"""foxos bot serve：智能体聊天窗口的本机服务。

- 只监听 127.0.0.1（默认），访问需要令牌：启动器用 ?t=<令牌> 打开，服务换成 HttpOnly、SameSite=Strict 的 cookie；
  写操作还要求请求头 X-FoxOS: 1（防跨站请求）。
- 所有操作都走 kernel.invoke（与 CLI、MCP 同一内核、同一审计日志，身份 human，接口 ui）。
- /api/events 是 SSE：逐行跟踪每个智能体的 .foxos/bots/<id>/events.jsonl，所以 CLI、MCP 子进程（委托）、例程、频道发起的回合也实时显示。
- /hooks/<智能体>/<令牌>：Webhook 频道。
- 运行信息写到 FOXOS_HOME/botchat.json（0600），启动器复用已在运行的服务。
"""

from __future__ import annotations

import contextvars
import json
import mimetypes
import os
import re
import secrets as pysecrets
import shutil
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import activity, bots, i18n, machines, secrets
from ..errors import FoxError
from ..kernel import Context, invoke, paused_for

STATIC = Path(__file__).resolve().parent / "static"
UI_PREFS = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "foxos" / "bots-ui.json"
WINDOW_CLASS = "foxos-bots"


def _home() -> Path:
    from ..desktop_client import foxos_home
    return foxos_home()


def info_path() -> Path:
    return _home() / "botchat.json"


def load_prefs() -> dict:
    try:
        p = json.loads(UI_PREFS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        p = {}
    return {"dock": bool(p.get("dock", False)), "side": p.get("side", "right") if p.get("side") in ("left", "right") else "right",
            "width": int(p.get("width", 440)) if str(p.get("width", 440)).isdigit() else 440, "theme": p.get("theme", "auto")}


def save_prefs(p: dict) -> dict:
    cur = load_prefs()
    for k in ("dock", "side", "width", "theme"):
        if k in p:
            cur[k] = p[k]
    cur = {"dock": bool(cur["dock"]), "side": cur["side"] if cur["side"] in ("left", "right") else "right",
           "width": max(320, min(900, int(cur["width"]))), "theme": cur["theme"] if cur["theme"] in ("auto", "light", "dark") else "auto"}
    UI_PREFS.parent.mkdir(parents=True, exist_ok=True)
    UI_PREFS.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    return cur


def _geometry(win: str) -> tuple[int, int, int, int] | None:
    r = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        f = ln.split()
        if f and f[0] == win:
            return int(f[2]), int(f[3]), int(f[4]), int(f[5])
    return None


def apply_window_mode(prefs: dict) -> dict:
    """在 XFCE / X11 上把聊天窗口停靠到屏幕一侧（全高、置顶、所有工作区可见），或恢复成普通窗口。"""
    if not os.environ.get("DISPLAY") or not shutil.which("wmctrl"):
        return {"applied": False, "reason": "no DISPLAY or wmctrl"}
    r = subprocess.run(["wmctrl", "-lx"], capture_output=True, text=True)
    wins = [ln.split()[0] for ln in r.stdout.splitlines() if WINDOW_CLASS in ln.split()[2].lower()] if r.returncode == 0 else []
    if not wins:
        return {"applied": False, "reason": "window not found"}
    try:
        out = subprocess.run(["xdpyinfo"], capture_output=True, text=True).stdout
        m = re.search(r"dimensions:\s+(\d+)x(\d+)", out)
        sw, sh = (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)
    except OSError:
        sw, sh = 1920, 1080
    panel = 44  # 底栏高度（scripts/os/branding/xfce/panel）
    for w in wins:
        if prefs["dock"]:
            x = sw - prefs["width"] if prefs["side"] == "right" else 0
            subprocess.run(["wmctrl", "-i", "-r", w, "-b", "remove,maximized_vert,maximized_horz"])
            subprocess.run(["wmctrl", "-i", "-r", w, "-e", f"0,{x},0,{prefs['width']},{sh - panel}"])
            subprocess.run(["wmctrl", "-i", "-r", w, "-b", "add,above,sticky,skip_taskbar"])
            if prefs["side"] == "right":
                # 浏览器有最小宽度、窗框有边：按实际几何把右边缘贴回屏幕边
                time.sleep(0.3)
                g = _geometry(w)
                if g and (g[0] + g[2] != sw or g[1] + g[3] > sh - panel):
                    h = g[3] - max(0, g[1] + g[3] - (sh - panel))
                    subprocess.run(["wmctrl", "-i", "-r", w, "-e", f"0,{max(0, x - (g[0] + g[2] - sw))},0,-1,{h}"])
        else:
            subprocess.run(["wmctrl", "-i", "-r", w, "-b", "remove,above,sticky,skip_taskbar"])
            ww, wh = min(1200, sw - 120), min(820, sh - panel - 80)
            subprocess.run(["wmctrl", "-i", "-r", w, "-e", f"0,{(sw - ww) // 2},{(sh - panel - wh) // 2},{ww},{wh}"])
    return {"applied": True, "windows": len(wins)}


class State:
    def __init__(self, ws, token: str):
        self.ws = ws
        self.token = token
        self.running: dict[str, dict] = {}  # bot -> {turn thread, started}
        self.jobs: dict[str, dict] = {}  # 安装、OAuth 等后台任务
        self.lock = threading.Lock()

    def ctx(self) -> Context:
        return Context(self.ws, agent="human", interface="ui")

    def call(self, cmd: str, params: dict | None = None):
        return invoke(cmd, params or {}, self.ctx())

    def job(self, kind: str, fn, **meta) -> str:
        jid = "job-" + pysecrets.token_hex(5)
        rec = {"id": jid, "kind": kind, "status": "running", "log": [], "started": time.time(), **meta}
        with self.lock:
            self.jobs[jid] = rec

        def run():
            try:
                rec["result"] = fn(rec)
                rec["status"] = "done"
            except FoxError as e:
                rec["status"] = "failed"
                rec["error"] = e.to_dict()
            except Exception as e:  # noqa: BLE001
                rec["status"] = "failed"
                rec["error"] = {"code": "ERROR", "message": f"{type(e).__name__}: {e}"}
            rec["ended"] = time.time()
        threading.Thread(target=contextvars.copy_context().run, args=(run,), daemon=True).start()
        return jid


def _public_job(j: dict) -> dict:
    return {k: v for k, v in j.items() if k not in ("secret",)}


def make_handler(st: State):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        # ---------------------------------------------------------- 基础
        def _send(self, code: int, body=None, ctype="application/json; charset=utf-8", headers=None):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _authed(self) -> bool:
            c = self.headers.get("Cookie") or ""
            m = re.search(r"(?:^|;\s*)foxos_bots=([A-Za-z0-9_\-]+)", c)
            tok = (m.group(1) if m else None) or self.headers.get("X-FoxOS-Token")
            return bool(tok) and pysecrets.compare_digest(tok, st.token)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 50 * 2**20:
                raise FoxError("USAGE", "body too large")
            raw = self.rfile.read(n) if n else b""
            if not raw:
                return {}
            try:
                return json.loads(raw.decode("utf-8"))
            except ValueError as e:
                raise FoxError("USAGE", f"bad JSON: {e}") from None

        def _ok(self, result):
            self._send(200, {"ok": True, "result": result})

        def _err(self, e: FoxError, code: int | None = None):
            m = {"USAGE": 400, "NOT_FOUND": 404, "PERMISSION_DENIED": 403, "LOCKED": 423, "CONFLICT": 409, "PAUSED": 423}
            self._send(code or m.get(e.code, 500), {"ok": False, "error": e.to_dict()})

        # ---------------------------------------------------------- GET
        def do_GET(self):  # noqa: N802
            with i18n.using(self.headers.get("X-FoxOS-Lang")):
                return self._do_get()

        def _do_get(self):
            u = urllib.parse.urlparse(self.path)
            q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
            if u.path == "/" and q.get("t"):
                if not pysecrets.compare_digest(q["t"], st.token):
                    return self._send(403, b"forbidden", "text/plain")
                return self._send(302, b"", "text/plain", {"Location": "/", "Set-Cookie": f"foxos_bots={st.token}; HttpOnly; SameSite=Strict; Path=/"})
            if not u.path.startswith("/api/"):
                return self._static(u.path)
            if not self._authed():
                return self._send(401, {"ok": False, "error": {"code": "PERMISSION_DENIED", "message": "token required"}})
            try:
                return self._get(u.path, q)
            except FoxError as e:
                return self._err(e)

        def _static(self, path: str):
            if path in ("/", ""):
                path = "/index.html"
            p = (STATIC / path.lstrip("/")).resolve()
            if not p.is_relative_to(STATIC.resolve()) or not p.is_file():
                return self._send(404, b"not found", "text/plain")
            ct = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            if p.suffix == ".woff2":
                ct = "font/woff2"
            if ct.startswith("text/") or ct in ("application/javascript", "application/json"):
                ct += "; charset=utf-8"
            hdr = {"Content-Security-Policy": "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; connect-src 'self'"} \
                if p.suffix == ".html" else {}
            return self._send(200, p.read_bytes(), ct, hdr)

        def _get(self, path: str, q: dict):
            parts = path.split("/")[2:]
            if parts == ["state"]:
                return self._ok(self._state(full=q.get("full") == "1"))
            if parts == ["events"]:
                return self._events()
            if len(parts) == 3 and parts[0] == "bots" and parts[2] == "messages":
                return self._ok(st.call("bot.message.list", {"bot": parts[1], "limit": int(q.get("limit", 200))}))
            if len(parts) == 3 and parts[0] == "bots" and parts[2] == "memory":
                return self._ok(st.call("bot.memory.list", {"bot": parts[1]}))
            if len(parts) == 3 and parts[0] == "bots" and parts[2] == "config":
                return self._ok(st.call("bot.config.get", {"bot": parts[1]}))
            if parts == ["skills"]:
                return self._ok(st.call("bot.skill.list", {k: v for k, v in q.items() if k in ("bot", "kind")}))
            if len(parts) == 2 and parts[0] == "skills":
                return self._ok(st.call("bot.skill.show", {"name": parts[1]}))
            if parts == ["routines"]:
                return self._ok(st.call("bot.routine.list", {}))
            if parts == ["approvals"]:
                return self._ok(st.call("bot.approval.list", {}))
            if parts == ["connectors"]:
                return self._ok({"catalog": st.call("connector.catalog")["catalog"], "installed": st.call("connector.list")["connectors"]})
            if len(parts) == 3 and parts[0] == "connectors" and parts[2] == "tools":
                return self._ok(st.call("connector.tools", {"connector": parts[1], "refresh": q.get("refresh") == "1"}))
            if parts == ["agents"]:
                try:
                    reg = st.call("acp.agent.list", {"available": True})
                except FoxError as e:
                    reg = {"agents": [], "error": e.to_dict()}
                return self._ok({"installed": st.call("acp.agent.list", {})["agents"], "registry": reg.get("agents", []),
                                 "keys": st.call("acp.key.list", {})["keys"], "source": reg.get("source")})
            if len(parts) == 3 and parts[0] == "agents" and parts[2] == "icon":
                return self._icon(parts[1])
            if parts == ["machines"]:
                return self._ok({"machines": st.call("machine.list", {"check": q.get("check") == "1"})["machines"],
                                 "host": self._host_info()})
            if parts == ["runtime"]:
                return self._ok(st.call("runtime.list", {}))
            if parts == ["jobs"]:
                return self._ok([_public_job(j) for j in st.jobs.values()])
            if len(parts) == 2 and parts[0] == "jobs":
                j = st.jobs.get(parts[1])
                if not j:
                    raise FoxError("NOT_FOUND", parts[1])
                return self._ok(_public_job(j))
            if parts == ["file"]:
                return self._file(q.get("path", ""))
            if parts == ["prefs"]:
                return self._ok(load_prefs())
            if parts == ["audit"]:
                return self._ok(st.call("audit.tail", {"limit": int(q.get("limit", 50)), **({"agent": q["agent"]} if q.get("agent") else {})}))
            raise FoxError("NOT_FOUND", path)

        def _host_info(self) -> dict:
            try:
                cert = machines.host_dir() / "cert.pem"
                fp = None
                if cert.exists():
                    import ssl
                    fp = machines.fingerprint_der(ssl.PEM_cert_to_DER_cert(cert.read_text()))
                clients = st.call("machine.host.clients")["clients"]
            except FoxError:
                fp, clients = None, []
            return {"fingerprint": fp, "clients": clients}

        def _icon(self, agent_id: str):
            from ..apps import acp as acpapp
            if not re.match(r"^[a-z0-9][a-z0-9._-]{0,60}$", agent_id):
                return self._send(404, b"", "text/plain")
            p = acpapp.icon_path(agent_id)
            if not p:
                try:
                    reg = acpapp.fetch_registry(offline=True)
                    e = next((a for a in reg["data"]["agents"] if a["id"] == agent_id), None)
                    p = acpapp.fetch_icon(e) if e else None
                except Exception:  # noqa: BLE001
                    p = None
            if not p or not Path(p).is_file():
                return self._send(404, b"", "text/plain")
            return self._send(200, Path(p).read_bytes(), "image/svg+xml", {"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'"})

        def _file(self, rel: str):
            p = st.ws.resolve(rel)
            if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg") or not p.is_file():
                raise FoxError("NOT_FOUND", rel)
            ct = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            return self._send(200, p.read_bytes(), ct, {"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'"})

        def _state(self, full: bool = False) -> dict:
            bl = st.call("bot.profile.list", {"hidden": True})["bots"]
            acts = activity.current(st.ws)
            owner = activity.desktop_owner(st.ws)
            paused = {b["id"]: bool(paused_for(st.ws, f"bot:{b['id']}/x")) for b in bl}
            try:
                ctl = st.call("control.status")
            except FoxError:
                ctl = {}
            out = {"lang": i18n.get_lang(), "bots": bl, "running": {k: {"turn": v.get("turn"), "since": v.get("since")} for k, v in st.running.items()},
                   "activity": acts, "desktop_owner": owner, "paused": paused, "control": ctl,
                   "approvals": st.call("bot.approval.list")["approvals"], "prefs": load_prefs(), "workspace": str(st.ws.root),
                   "machines": [m["name"] for m in st.call("machine.list")["machines"]]}
            return out

        # ---------------------------------------------------------- SSE
        def _events(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            offsets: dict[str, int] = {}
            for b in bots.all_bots(st.ws):
                offsets[b["id"]] = bots.open_turn_offset(st.ws, b["id"])
            last_state = 0.0
            try:
                self.wfile.write(b": hello\n\n")
                self.wfile.flush()
                while True:
                    sent = False
                    for b in bots.all_bots(st.ws):
                        evs, off = bots.events_since(st.ws, b["id"], offsets.get(b["id"], 0))
                        offsets[b["id"]] = off
                        for e in evs:
                            self.wfile.write(b"data: " + json.dumps(e, ensure_ascii=False, default=str).encode("utf-8") + b"\n\n")
                            sent = True
                    if time.time() - last_state > 1.5:
                        last_state = time.time()
                        s = {"type": "state", "running": {k: v.get("turn") for k, v in st.running.items()},
                             "activity": activity.current(st.ws), "desktop_owner": activity.desktop_owner(st.ws),
                             "approvals": len(bots.approvals_pending(st.ws)),
                             "jobs": [_public_job(j) for j in st.jobs.values() if j["status"] == "running" or time.time() - j.get("ended", 0) < 10]}
                        try:
                            s["control"] = st.call("control.status")
                        except FoxError:
                            pass
                        self.wfile.write(b"data: " + json.dumps(s, ensure_ascii=False, default=str).encode("utf-8") + b"\n\n")
                        sent = True
                    if sent:
                        self.wfile.flush()
                    time.sleep(0.15)
            except (BrokenPipeError, ConnectionResetError, OSError):
                return

        # ---------------------------------------------------------- 写操作
        def do_POST(self):  # noqa: N802
            return self._write("POST")

        def do_PUT(self):  # noqa: N802
            return self._write("PUT")

        def do_PATCH(self):  # noqa: N802
            return self._write("PATCH")

        def do_DELETE(self):  # noqa: N802
            return self._write("DELETE")

        def _write(self, method: str):
            with i18n.using(self.headers.get("X-FoxOS-Lang")):
                return self._do_write(method)

        def _do_write(self, method: str):
            u = urllib.parse.urlparse(self.path)
            if u.path.startswith("/hooks/") and method == "POST":
                return self._hook(u.path)
            if not self._authed() or self.headers.get("X-FoxOS") != "1":
                return self._send(401, {"ok": False, "error": {"code": "PERMISSION_DENIED", "message": "token required"}})
            try:
                if u.path == "/api/upload":
                    return self._upload()
                body = self._body()
                return self._ok(self._route(method, u.path.split("/")[2:], body))
            except FoxError as e:
                return self._err(e)

        def _upload(self):
            name = urllib.parse.unquote(self.headers.get("X-Filename") or "file")
            name = re.sub(r"[^\w.\- ()\u4e00-\u9fff]+", "_", os.path.basename(name))[:120] or "file"
            n = int(self.headers.get("Content-Length") or 0)
            if n > 50 * 2**20:
                raise FoxError("USAGE", "file too large (50 MB)")
            data = self.rfile.read(n)
            rel = f"attachments/{time.strftime('%Y-%m-%d')}/{name}"
            base, ext = os.path.splitext(rel)
            i = 1
            while (st.ws.root / rel).exists():
                rel = f"{base}-{i}{ext}"
                i += 1
            _write_bytes(st, rel, data)
            return self._ok({"path": rel, "bytes": len(data)})

        def _hook(self, path: str):
            parts = path.split("/")
            if len(parts) != 4:
                return self._send(404, {"ok": False})
            bid, tok = parts[2], parts[3]
            want = secrets.get(f"bot:{bid}:webhook")
            if not want or not pysecrets.compare_digest(tok, want):
                return self._send(403, {"ok": False, "error": {"code": "PERMISSION_DENIED", "message": "bad hook token"}})
            try:
                body = self._body()
                text = str(body.get("text") or "").strip()
                r = bots.run_turn(st.ws, bid, text, actor=f"webhook:{body.get('from') or 'anonymous'}"[:80], origin="channel")
                return self._send(200, {"ok": True, "reply": r["text"], "message": r["id"]})
            except FoxError as e:
                return self._err(e)

        def _route(self, method: str, parts: list[str], b: dict):
            # 智能体
            if parts == ["bots"] and method == "POST":
                return st.call("bot.profile.create", b)
            if len(parts) == 2 and parts[0] == "bots":
                if method in ("PATCH", "PUT"):
                    return st.call("bot.config.set", {"bot": parts[1], **b})
                if method == "DELETE":
                    return st.call("bot.profile.delete", {"bot": parts[1]})
            if len(parts) == 3 and parts[0] == "bots":
                bid, act = parts[1], parts[2]
                if act == "send":
                    return self._send_turn(bid, b)
                if act == "cancel":
                    return {"cancelled": bots.cancel(bots.get(st.ws, bid)["id"])}
                if act == "duplicate":
                    return st.call("bot.profile.duplicate", {"bot": bid, "name": b.get("name")})
                if act == "reset":
                    return st.call("bot.profile.reset", {"bot": bid, "keep_memory": bool(b.get("keep_memory"))})
                if act == "memory" and method == "POST":
                    return st.call("bot.memory.add", {"bot": bid, "text": b.get("text", "")})
                if act == "pause":
                    return st.call("control.pause", {"reason": b.get("reason") or "ui", "targets": [f"bot:{bots.get(st.ws, bid)['id']}"]})
                if act == "resume":
                    return st.call("control.resume", {"targets": [f"bot:{bots.get(st.ws, bid)['id']}"]})
                if act == "channel":
                    return st.call("bot.channel.set", {"bot": bid, **b}) if method == "POST" else st.call("bot.channel.remove", {"bot": bid, **b})
            if len(parts) == 4 and parts[0] == "bots" and parts[2] == "memory" and method == "DELETE":
                return st.call("bot.memory.forget", {"bot": parts[1], "memory": parts[3]})
            if len(parts) == 2 and parts[0] == "approvals":
                return st.call("bot.approval.answer", {"request": parts[1], **({"option": b["option"]} if b.get("option") else {"deny": True})})
            if parts == ["routines"] and method == "POST":
                return st.call("bot.routine.create", b)
            if len(parts) == 2 and parts[0] == "routines":
                if method == "DELETE":
                    return st.call("bot.routine.delete", {"routine": parts[1]})
                if parts[1] == "run":
                    return st.call("bot.routine.run", b)
                return st.call("bot.routine.update", {"routine": parts[1], **b})
            # 人工接管
            if parts == ["control", "pause"]:
                return st.call("control.pause", {"reason": b.get("reason") or "ui", **({"targets": b["targets"]} if b.get("targets") else {})})
            if parts == ["control", "resume"]:
                return st.call("control.resume", {**({"targets": b["targets"]} if b.get("targets") else {})})
            # 连接器
            if parts == ["connectors"] and method == "POST":
                return st.call("connector.add", b)
            if len(parts) == 2 and parts[0] == "connectors" and method == "DELETE":
                return st.call("connector.remove", {"connector": parts[1]})
            if len(parts) == 3 and parts[0] == "connectors":
                cid, act = parts[1], parts[2]
                if act == "connect":
                    if b.get("token"):
                        return st.call("connector.connect", {"connector": cid, "token": b["token"]})
                    return self._oauth(cid, b)
                if act == "disconnect":
                    return st.call("connector.disconnect", {"connector": cid})
                if act == "call":
                    return st.call("connector.tool.call", {"connector": cid, "tool": b.get("tool"), "arguments": b.get("arguments") or {}})
            # 代码智能体
            if len(parts) == 3 and parts[0] == "agents":
                aid, act = parts[1], parts[2]
                if act == "install":
                    return {"job": st.job("install", lambda rec: st.call("acp.agent.install", {"agent": aid}), agent=aid)}
                if act == "uninstall":
                    return st.call("acp.agent.uninstall", {"agent": aid})
                if act == "probe":
                    return {"job": st.job("probe", lambda rec: st.call("acp.agent.probe", {"agent": aid}), agent=aid)}
                if act == "key":
                    if method == "DELETE":
                        return st.call("acp.key.remove", {"agent": aid, "name": b.get("name")})
                    return st.call("acp.key.set", {"agent": aid, "name": b.get("name"), "value": b.get("value")})
                if act == "login":
                    return {"job": st.job("login", lambda rec: st.call("acp.agent.login", {"agent": aid, "method": b.get("method")}), agent=aid)}
            # 机器
            if parts == ["machines", "pair"]:
                return st.call("machine.pair", b)
            if len(parts) == 2 and parts[0] == "machines" and method == "DELETE":
                return st.call("machine.remove", {"name": parts[1]})
            if parts == ["machines", "host", "code"]:
                return st.call("machine.host.code", b)
            if parts == ["machines", "host", "grant"]:
                return st.call("machine.host.grant", b)
            if parts == ["machines", "host", "revoke"]:
                return st.call("machine.host.revoke", b)
            if parts == ["machines", "host", "unpair"]:
                return st.call("machine.host.unpair", b)
            # 运行环境
            if len(parts) == 3 and parts[0] == "runtime" and parts[2] == "install":
                return {"job": st.job("runtime", lambda rec: st.call("runtime.install", {"name": [parts[1]], "accept_license": bool(b.get("accept_license"))}),
                                      tool=parts[1])}
            # 窗口
            if parts == ["prefs"]:
                p = save_prefs(b)
                return {"prefs": p, "window": apply_window_mode(p)}
            raise FoxError("NOT_FOUND", "/".join(parts))

        def _send_turn(self, bid: str, b: dict):
            bot = bots.get(st.ws, bid)
            with st.lock:
                if bot["id"] in st.running:
                    raise FoxError("CONFLICT", i18n.tr("botchat.busy", bot["name"]))
                st.running[bot["id"]] = {"since": time.time()}

            def run():
                try:
                    st.call("bot.message.send", {"bot": bot["id"], "text": b.get("text", ""), "attachments": b.get("attachments") or [],
                                                 "approve": b.get("approve") or "rules"})
                except FoxError as e:
                    bots._append(bots._bot_dir(st.ws, bot["id"]) / "events.jsonl",
                                 {"bot": bot["id"], "type": "error", "t": time.time(), "error": e.to_dict()})
                finally:
                    with st.lock:
                        st.running.pop(bot["id"], None)
            threading.Thread(target=contextvars.copy_context().run, args=(run,), daemon=True).start()
            return {"started": True, "bot": bot["id"]}

        def _oauth(self, cid: str, b: dict):
            from .. import connectors
            urls: list[str] = []

            def fn(rec):
                connectors.oauth_connect(cid, b.get("client_id"), b.get("client_secret"), open_browser=True,
                                         on_url=lambda u: (urls.append(u), rec.__setitem__("authorize_url", u)))
                return connectors.refresh_tools(cid)
            jid = st.job("oauth", fn, connector=cid)
            for _ in range(40):
                if urls or st.jobs[jid]["status"] != "running":
                    break
                time.sleep(0.1)
            return {"job": jid, "authorize_url": urls[0] if urls else None, "status": st.jobs[jid]["status"], "error": st.jobs[jid].get("error")}
    return H


def _write_bytes(st: State, rel: str, data: bytes):
    """files.write 只收文本时，二进制附件直接写入工作空间（仍记审计）。"""
    from .. import audit
    p = st.ws.resolve(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    audit.append_safe(st.ws, {"agent": "human", "interface": "ui", "command": "bot.attachment.upload", "status": "ok",
                              "targets": [{"path": rel, "access": "create"}], "args": {"path": rel, "bytes": len(data)}})


def serve(ws, host: str = "127.0.0.1", port: int = 0, token: str | None = None, open_ui: bool = False, ready_file: str | None = None) -> int:
    token = token or pysecrets.token_urlsafe(24)
    st = State(ws, token)
    bots.ensure_main(ws)
    srv = ThreadingHTTPServer((host, port), make_handler(st))
    srv.daemon_threads = True
    real_port = srv.server_address[1]
    url = f"http://{'127.0.0.1' if host in ('0.0.0.0', '') else host}:{real_port}/"
    info = {"url": url, "pid": os.getpid(), "workspace": str(ws.root), "started": time.time()}
    ip = info_path()
    ip.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(ip, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({**info, "token": token}, f)
    if ready_file:
        fd = os.open(ready_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(f"{url}?t={token}\n")
    print(json.dumps({"url": url, "pid": os.getpid(), "workspace": str(ws.root)}), flush=True)
    if open_ui:
        subprocess.Popen(["foxos-bots", "--url", f"{url}?t={token}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) \
            if shutil.which("foxos-bots") else None
    try:
        srv.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if json.loads(ip.read_text()).get("pid") == os.getpid():
                ip.unlink()
        except (OSError, ValueError):
            pass
    return 0
