"""智能体（bot）：一个主智能体 + 任意多个其它智能体。资料、对话、记忆、委托、审批、例程，以及每回合的执行引擎。

存储（都在工作空间的 .foxos/bots/ 下，由内核维护）：
  index.json                    所有智能体的设置
  <id>/messages.jsonl           对话（用户消息与智能体回答，回答里带工具卡片、用过的技能、机器）
  <id>/memory.jsonl             记忆
  <id>/events.jsonl             回合事件（流式文字、工具调用、审批……），聊天界面实时读取
  approvals/<请求>.json          等人回答的审批
  routines.json                 例程

每个回合都通过 ACP 跑一个真实的智能体进程（或 OpenAI 兼容的模型端点），文件读写、终端、委托都经过
foxos 内核：工作空间约束、该智能体的工作范围、写锁、审计、人工接管全部生效。
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from pathlib import Path

from . import audit, machines, secrets, skills
from .errors import FoxError
from .i18n import get_lang, tr

MAX_DEPTH = 3
MAX_PER_TURN = 5
APPROVAL_TIMEOUT = float(os.environ.get("FOXOS_APPROVAL_TIMEOUT", "600"))
ICON_RE = re.compile(r"^[a-z0-9-]{2,40}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ACP_KINDS = ["read", "edit", "delete", "move", "search", "execute", "think", "fetch", "switch_mode", "other"]
DECISIONS = ["allow", "ask", "deny"]
APPROVAL_MODES = ["ask", "allow_reads", "allow_all"]
_lock = threading.RLock()


# ---------------------------------------------------------------------- 存储
def root(ws) -> Path:
    d = ws.data_dir / "bots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _index_path(ws) -> Path:
    return root(ws) / "index.json"


def _load(ws) -> dict:
    try:
        return json.loads(_index_path(ws).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"bots": {}}


def _save(ws, d: dict) -> None:
    p = _index_path(ws)
    tmp = p.with_name(f".index.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


def _flock(ws):
    from .activity import _flock as fl
    return fl(root(ws) / ".index.lock")


def default_bot(main: bool = False) -> dict:
    return {
        "id": "", "name": "", "title": "", "role": "", "instructions": "",
        "avatar": {"icon": "robot", "color": "#E8743B"},
        "main": main, "visibility": "private", "isolated": False, "pinned": main, "hidden": False, "active": True,
        "notifications": True,
        "backend": {"kind": "acp", "agent": "foxos-local"},
        "model": None,
        "scope": ".",
        "skills": {"mode": "all", "disabled": [], "enabled": []},
        "connectors": [],
        "machines": {"default": machines.LOCAL, "allowed": [machines.LOCAL]},
        "approvals": {"mode": "ask", "rules": []},
        "delegation": {"allowed": ["*"], "max_depth": MAX_DEPTH, "max_per_turn": MAX_PER_TURN},
        "channels": {},
        "created": audit.now_iso(), "updated": audit.now_iso(),
    }


def ensure_main(ws) -> dict:
    with _lock, _flock(ws):
        d = _load(ws)
        mains = [b for b in d["bots"].values() if b.get("main")]
        if mains:
            return mains[0]
        b = default_bot(main=True)
        b.update(id="fox", name=tr("bots.main_name"), title=tr("bots.main_title"), role=tr("bots.main_role"),
                 avatar={"icon": "sparkles", "color": "#E8743B"})
        d["bots"][b["id"]] = b
        _save(ws, d)
        return b


def all_bots(ws) -> list[dict]:
    ensure_main(ws)
    bs = list(_load(ws)["bots"].values())
    bs.sort(key=lambda b: (not b.get("main"), not b.get("pinned"), b.get("created", "")))
    return bs


def get(ws, ref: str) -> dict:
    ensure_main(ws)
    bs = _load(ws)["bots"]
    if ref in bs:
        return bs[ref]
    r = str(ref or "").lstrip("@").lower()
    for b in bs.values():
        if b["name"].lower() == r or b["id"].lower() == r:
            return b
    if r in ("main", "主", "主智能体"):
        return next(b for b in bs.values() if b.get("main"))
    raise FoxError("NOT_FOUND", tr("bots.no_such_bot", ref), hint=tr("bots.list_hint"))


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30]
    return s or "bot-" + uuid.uuid4().hex[:6]


def validate_patch(ws, patch: dict, cur: dict | None = None) -> dict:
    out = {}
    for k, v in patch.items():
        if v is None:
            continue
        if k in ("name", "title", "role", "instructions", "model"):
            if not isinstance(v, str):
                raise FoxError("USAGE", tr("bots.bad_field", k))
            if k == "name" and not v.strip():
                raise FoxError("USAGE", tr("bots.name_required"))
            if k == "name" and ("@" in v or len(v) > 40):
                raise FoxError("USAGE", tr("bots.bad_name"))
            out[k] = v.strip() if k in ("name", "title") else v
        elif k == "avatar":
            icon, color, image = v.get("icon"), v.get("color"), v.get("image")
            if image:
                ws.resolve(image)  # 必须在工作空间里
                if not str(image).lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif")):
                    raise FoxError("USAGE", tr("bots.bad_image"))
            if icon and not ICON_RE.match(icon):
                raise FoxError("USAGE", tr("bots.bad_icon"))
            if color and not COLOR_RE.match(color):
                raise FoxError("USAGE", tr("bots.bad_color"))
            base = dict((cur or {}).get("avatar") or {})
            base.update({kk: vv for kk, vv in {"icon": icon, "color": color, "image": image}.items() if vv is not None})
            if image == "":
                base.pop("image", None)
            out["avatar"] = base
        elif k in ("visibility",):
            if v not in ("private", "public"):
                raise FoxError("USAGE", tr("bots.bad_visibility"))
            out[k] = v
        elif k in ("isolated", "pinned", "hidden", "active", "notifications"):
            if not isinstance(v, bool):
                raise FoxError("USAGE", tr("bots.bad_field", k))
            out[k] = v
        elif k == "backend":
            kind = v.get("kind")
            if kind == "acp":
                if not v.get("agent"):
                    raise FoxError("USAGE", tr("bots.backend_agent_required"))
                out[k] = {"kind": "acp", "agent": v["agent"]}
            elif kind == "local":
                out[k] = {"kind": "acp", "agent": "foxos-local"}
            elif kind == "model":
                if not v.get("base_url") or not v.get("model"):
                    raise FoxError("USAGE", tr("bots.backend_model_required"))
                out[k] = {"kind": "model", "base_url": v["base_url"].rstrip("/"), "model": v["model"],
                          "auth_header": v.get("auth_header") or "Authorization"}
            else:
                raise FoxError("USAGE", tr("bots.bad_backend"))
        elif k == "scope":
            p = ws.resolve(v or ".")
            out[k] = ws.rel(p) if p != ws.root else "."
        elif k == "skills":
            mode = v.get("mode", "all")
            if mode not in ("all", "selected"):
                raise FoxError("USAGE", tr("bots.bad_skills_mode"))
            known = {s["name"] for s in skills.catalog(ws)}
            for n in (v.get("enabled") or []) + (v.get("disabled") or []):
                if n not in known:
                    raise FoxError("NOT_FOUND", tr("skills.no_such_skill", n))
            out[k] = {"mode": mode, "enabled": sorted(set(v.get("enabled") or [])), "disabled": sorted(set(v.get("disabled") or []))}
        elif k == "connectors":
            from . import connectors
            known = {c["id"] for c in connectors.installed()}
            for c in v:
                if c not in known:
                    raise FoxError("NOT_FOUND", tr("connectors.no_such_connector", c))
            out[k] = sorted(set(v))
        elif k == "machines":
            reg = machines.registry()
            allowed = list(dict.fromkeys(v.get("allowed") or [machines.LOCAL]))
            for m in allowed:
                if m != machines.LOCAL and m not in reg:
                    raise FoxError("NOT_FOUND", tr("machines.no_such_machine", m))
            dflt = v.get("default") or allowed[0]
            if dflt not in allowed:
                allowed.append(dflt) if (dflt == machines.LOCAL or dflt in reg) else None
            if dflt != machines.LOCAL and dflt not in reg:
                raise FoxError("NOT_FOUND", tr("machines.no_such_machine", dflt))
            out[k] = {"default": dflt, "allowed": allowed}
        elif k == "approvals":
            mode = v.get("mode", "ask")
            if mode not in APPROVAL_MODES:
                raise FoxError("USAGE", tr("bots.bad_approval_mode", ", ".join(APPROVAL_MODES)))
            rules = []
            for r in v.get("rules") or []:
                if r.get("kind") not in ACP_KINDS or r.get("decision") not in DECISIONS:
                    raise FoxError("USAGE", tr("bots.bad_rule", ", ".join(ACP_KINDS)))
                rules.append({"kind": r["kind"], "decision": r["decision"]})
            out[k] = {"mode": mode, "rules": rules}
        elif k == "delegation":
            md = int(v.get("max_depth", MAX_DEPTH))
            mp = int(v.get("max_per_turn", MAX_PER_TURN))
            if not (0 <= md <= 5 and 0 <= mp <= 20):
                raise FoxError("USAGE", tr("bots.bad_delegation"))
            out[k] = {"allowed": list(v.get("allowed") or ["*"]), "max_depth": md, "max_per_turn": mp}
        elif k == "channels":
            out[k] = v
        else:
            raise FoxError("USAGE", tr("bots.unknown_field", k))
    return out


def create(ws, fields: dict, id_: str | None = None) -> dict:
    ensure_main(ws)
    with _lock, _flock(ws):
        d = _load(ws)
        b = default_bot()
        b.update(validate_patch(ws, fields))
        if not b["name"]:
            raise FoxError("USAGE", tr("bots.name_required"))
        if any(x["name"].lower() == b["name"].lower() for x in d["bots"].values()):
            raise FoxError("CONFLICT", tr("bots.name_taken", b["name"]))
        bid = id_ or _slug(b["name"])
        if not re.match(r"^[a-z0-9][a-z0-9-]{0,39}$", bid):
            raise FoxError("USAGE", tr("bots.bad_id"))
        while bid in d["bots"]:
            bid = f"{bid}-{uuid.uuid4().hex[:3]}"
        b["id"] = bid
        if b.get("isolated") and b.get("scope", ".") == ".":
            b["scope"] = f"bots/{bid}"
        (ws.root / b["scope"]).mkdir(parents=True, exist_ok=True)
        d["bots"][bid] = b
        _save(ws, d)
        return b


def update(ws, ref: str, patch: dict) -> dict:
    with _lock, _flock(ws):
        d = _load(ws)
        cur = get(ws, ref)
        p = validate_patch(ws, patch, cur)
        if "name" in p and any(x["name"].lower() == p["name"].lower() and x["id"] != cur["id"] for x in d["bots"].values()):
            raise FoxError("CONFLICT", tr("bots.name_taken", p["name"]))
        if cur.get("main") and p.get("active") is False:
            raise FoxError("USAGE", tr("bots.main_cannot_pause"))
        if p.get("isolated") and p.get("scope") is None and cur.get("scope", ".") == ".":
            p["scope"] = f"bots/{cur['id']}"
        b = {**d["bots"][cur["id"]], **p, "updated": audit.now_iso()}
        (ws.root / b["scope"]).mkdir(parents=True, exist_ok=True)
        d["bots"][cur["id"]] = b
        _save(ws, d)
        _pool_drop(cur["id"])
        return b


def delete(ws, ref: str) -> dict:
    with _lock, _flock(ws):
        d = _load(ws)
        cur = get(ws, ref)
        if cur.get("main"):
            raise FoxError("PERMISSION_DENIED", tr("bots.main_cannot_delete"))
        d["bots"].pop(cur["id"])
        _save(ws, d)
        bd = root(ws) / cur["id"]
        if bd.exists():
            stamp = time.strftime("%Y%m%dT%H%M%S")
            bd.rename(root(ws) / f".deleted-{cur['id']}-{stamp}")  # 软删除：对话和记忆保留可查
        _pool_drop(cur["id"])
        return cur


def duplicate(ws, ref: str, name: str) -> dict:
    cur = get(ws, ref)
    keep = {k: v for k, v in cur.items() if k not in ("id", "main", "created", "updated", "pinned")}
    keep["name"] = name
    if cur.get("isolated"):
        keep.pop("scope", None)
    return create(ws, keep)


def reset(ws, ref: str, memory: bool = True) -> dict:
    cur = get(ws, ref)
    bd = root(ws) / cur["id"]
    cleared = []
    for f in ("messages.jsonl", "events.jsonl") + (("memory.jsonl",) if memory else ()):
        if (bd / f).exists():
            (bd / f).unlink()
            cleared.append(f)
    _pool_drop(cur["id"])
    return {"bot": cur["id"], "cleared": cleared}


# ---------------------------------------------------------------------- 对话、记忆、事件
def _bot_dir(ws, bid: str) -> Path:
    d = root(ws) / bid
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append(path: Path, rec: dict) -> None:
    data = (json.dumps(rec, ensure_ascii=False, default=str) + "\n").encode("utf-8")
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def messages(ws, ref: str, limit: int = 100) -> list[dict]:
    b = get(ws, ref)
    m = _read_jsonl(_bot_dir(ws, b["id"]) / "messages.jsonl")
    return m[-limit:] if limit else m


def memory(ws, ref: str) -> list[dict]:
    b = get(ws, ref)
    return [m for m in _read_jsonl(_bot_dir(ws, b["id"]) / "memory.jsonl") if not m.get("forgotten")]


def memory_add(ws, ref: str, text: str, source: str) -> dict:
    b = get(ws, ref)
    if not text.strip():
        raise FoxError("USAGE", tr("bots.empty_memory"))
    rec = {"id": "mem-" + uuid.uuid4().hex[:8], "text": text.strip()[:2000], "source": source, "ts": audit.now_iso()}
    _append(_bot_dir(ws, b["id"]) / "memory.jsonl", rec)
    return rec


def memory_forget(ws, ref: str, mem_id: str) -> dict:
    b = get(ws, ref)
    p = _bot_dir(ws, b["id"]) / "memory.jsonl"
    items = _read_jsonl(p)
    if not any(m["id"] == mem_id for m in items):
        raise FoxError("NOT_FOUND", tr("bots.no_such_memory", mem_id))
    with _lock:
        tmp = p.with_name(".memory.tmp")
        tmp.write_text("".join(json.dumps({**m, **({"forgotten": True} if m["id"] == mem_id else {})}, ensure_ascii=False) + "\n" for m in items),
                       encoding="utf-8")
        os.replace(tmp, p)
    return {"forgotten": mem_id}


def events_since(ws, bid: str, offset: int) -> tuple[list[dict], int]:
    p = root(ws) / bid / "events.jsonl"
    if not p.exists():
        return [], 0
    size = p.stat().st_size
    if size < offset:
        offset = 0
    if size == offset:
        return [], offset
    with open(p, "rb") as f:
        f.seek(offset)
        data = f.read()
    cut = data.rfind(b"\n") + 1
    out = []
    for line in data[:cut].splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out, offset + cut


# ---------------------------------------------------------------------- 审批
def _approvals_dir(ws) -> Path:
    d = root(ws) / "approvals"
    d.mkdir(parents=True, exist_ok=True)
    return d


def approvals_pending(ws) -> list[dict]:
    out = []
    for f in sorted(_approvals_dir(ws).glob("*.json")):
        try:
            a = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if a.get("status") == "pending" and a.get("expires", 0) > time.time():
            out.append(a)
    return out


def approval_answer(ws, req_id: str, option_id: str | None, by: str) -> dict:
    f = _approvals_dir(ws) / f"{req_id}.json"
    if not re.match(r"^apr-[0-9a-f]+$", req_id) or not f.exists():
        raise FoxError("NOT_FOUND", tr("bots.no_such_approval", req_id))
    with _lock:
        a = json.loads(f.read_text(encoding="utf-8"))
        if a["status"] != "pending":
            raise FoxError("CONFLICT", tr("bots.approval_already", a["status"]))
        if option_id is not None and option_id not in [o["optionId"] for o in a["options"]]:
            raise FoxError("USAGE", tr("bots.bad_option", ", ".join(o["optionId"] for o in a["options"])))
        a.update(status="answered", optionId=option_id, by=by, answered=audit.now_iso())
        f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
    return a


def _auto_decision(bot: dict, kind: str) -> str:
    ap = bot.get("approvals") or {}
    for r in ap.get("rules") or []:
        if r["kind"] == kind:
            return r["decision"]
    mode = ap.get("mode", "ask")
    if mode == "allow_all":
        return "allow"
    if mode == "allow_reads" and kind in ("read", "search", "think", "fetch"):
        return "allow"
    return "ask"


def _pick(options: list[dict], allow: bool) -> str | None:
    want = ("allow_once", "allow_always") if allow else ("reject_once", "reject_always")
    for k in want:
        for o in options:
            if o.get("kind") == k:
                return o["optionId"]
    return None


def ask_file(ws, bot: dict, tool_call: dict, options: list[dict], turn: str | None = None) -> str | None:
    """不在聊天回合里的审批（例如连接器的写工具经 MCP 调用）：写审批请求，等人在界面或命令行回答。"""
    rid = "apr-" + uuid.uuid4().hex[:10]
    a = {"id": rid, "status": "pending", "bot": bot["id"], "bot_name": bot["name"], "turn": turn, "toolCall": tool_call,
         "options": options, "created": audit.now_iso(), "expires": time.time() + APPROVAL_TIMEOUT}
    f = _approvals_dir(ws) / f"{rid}.json"
    f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
    if turn:
        _append(_bot_dir(ws, bot["id"]) / "events.jsonl", {"turn": turn, "bot": bot["id"], "seq": 0, "t": time.time(), "type": "approval", "request": a})
    while time.time() < a["expires"]:
        try:
            cur = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cur = a
        if cur.get("status") == "answered":
            return cur.get("optionId")
        time.sleep(0.25)
    a["status"] = "expired"
    f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
    return None


# ---------------------------------------------------------------------- 执行引擎
class _Turn:
    def __init__(self, ws, bot: dict, turn: str, origin: str, delegated_by: str | None, depth: int):
        self.ws, self.bot, self.turn, self.origin, self.delegated_by, self.depth = ws, bot, turn, origin, delegated_by, depth
        self.text = ""
        self.cards: dict[str, dict] = {}
        self.order: list[str] = []
        self.plan: list[dict] = []
        self.skills_used: list[str] = []
        self.seq = 0
        self.ev_path = _bot_dir(ws, bot["id"]) / "events.jsonl"
        self.machine = (bot.get("machines") or {}).get("default", machines.LOCAL)
        self.skill_paths = skills.by_path(ws)
        self.lock = threading.Lock()

    def emit(self, ev: dict):
        with self.lock:
            self.seq += 1
            _append(self.ev_path, {"turn": self.turn, "bot": self.bot["id"], "seq": self.seq, "t": time.time(), **ev})

    def use_skill(self, name: str):
        if name and name not in self.skills_used:
            self.skills_used.append(name)
            self.emit({"type": "skill", "name": name})

    def card(self, cid: str) -> dict:
        if cid not in self.cards:
            self.cards[cid] = {"id": cid, "type": "tool", "machine": self.machine}
            self.order.append(cid)
        return self.cards[cid]

    def on_acp(self, e: dict):
        t = e.get("type")
        if t == "update":
            u = e["update"]
            k = u.get("sessionUpdate")
            if k == "agent_message_chunk":
                c = u.get("content") or {}
                if c.get("type") == "text":
                    self.text += c.get("text", "")
                    self.emit({"type": "text", "text": c.get("text", "")})
            elif k == "agent_thought_chunk":
                self.emit({"type": "thought", "text": (u.get("content") or {}).get("text", "")})
            elif k in ("tool_call", "tool_call_update"):
                cd = self.card(u.get("toolCallId") or uuid.uuid4().hex[:6])
                for f in ("title", "kind", "status", "locations", "rawInput", "rawOutput"):
                    if u.get(f) is not None:
                        cd[f] = u[f]
                if u.get("content") is not None:
                    cd["content"] = _clip_content(u["content"])
                raw = cd.get("rawInput") or {}
                if isinstance(raw, dict) and raw.get("machine"):
                    cd["machine"] = raw["machine"]
                self._skill_from_tool(cd)
                self._delegation_from_tool(cd)
                self.emit({"type": "card", "card": cd})
            elif k == "plan":
                self.plan = u.get("entries") or []
                self.emit({"type": "plan", "entries": self.plan})
            elif k == "available_commands_update":
                pass
        elif t == "fs":
            name = self.skill_paths.get(os.path.realpath(e.get("path", ""))) if e.get("readonly") else None
            if name:
                self.use_skill(name)
            self.emit({"type": "fs", "op": e["op"], "path": e.get("path"), "machine": self.machine,
                       **({"old": (e.get("old") or "")[:20000], "new": (e.get("new") or "")[:20000]} if e["op"] == "write" else {})})
        elif t == "terminal_start":
            self.emit({"type": "terminal", "terminalId": e["terminalId"], "command": e["command"], "cwd": e["cwd"], "machine": self.machine})
        elif t == "terminal":
            self.emit({"type": "terminal_output", "terminalId": e["terminalId"], "output": (e.get("output") or {}).get("output", "")[-20000:]})
        elif t == "stderr":
            pass

    def _delegation_from_tool(self, cd: dict):
        """智能体通过 foxos MCP 工具 bot_task_delegate 委托时，卡片显示成「委托」：交给谁、任务、回报。"""
        raw = cd.get("rawInput") or {}
        if not isinstance(raw, dict):
            return
        args = raw.get("arguments") if isinstance(raw.get("arguments"), dict) else raw
        if "bot_task_delegate" not in str(cd.get("title") or "") and raw.get("tool") not in ("bot_task_delegate", "bot.task.delegate"):
            return
        cd["type"] = "delegation"
        cd["via"] = "tool"
        if args.get("to"):
            cd["to"] = args["to"]
            try:
                cd["to_name"] = get(self.ws, args["to"])["name"]
            except FoxError:
                cd["to_name"] = args["to"]
        if args.get("task"):
            cd["task"] = args["task"]
        texts = [c.get("content", {}).get("text", "") for c in cd.get("content") or [] if isinstance(c, dict) and c.get("type") == "content"]
        for t in [json.dumps(cd.get("rawOutput")) if cd.get("rawOutput") else "", *texts]:
            try:
                j = json.loads(t) if t else None
            except ValueError:
                j = None
            res = (j or {}).get("result") if isinstance(j, dict) and "result" in j else j
            if isinstance(res, dict) and "answer" in res:
                cd["answer"] = res["answer"]
                cd["refused"] = res.get("refused", False)
                cd["skills_used"] = res.get("skills_used", [])
                break
            if t and not j:
                cd.setdefault("answer", t)

    def _skill_from_tool(self, cd: dict):
        raw = cd.get("rawInput") or {}
        title = str(cd.get("title") or "")
        if isinstance(raw, dict):
            for key in ("path", "file_path", "absolute_path"):
                n = self.skill_paths.get(os.path.realpath(str(raw.get(key) or "")))
                if n:
                    self.use_skill(n)
            if "skill_show" in title or raw.get("tool") in ("bot_skill_show", "bot.skill.show"):
                n = raw.get("name") or raw.get("skill")
                if n:
                    self.use_skill(n)


def _clip_content(content: list) -> list:
    out = []
    for c in content or []:
        c = dict(c)
        for k in ("oldText", "newText"):
            if isinstance(c.get(k), str) and len(c[k]) > 40000:
                c[k] = c[k][:40000]
        out.append(c)
    return out


_pool: dict[str, dict] = {}
_pool_lock = threading.Lock()


def _pool_drop(bid: str):
    with _pool_lock:
        p = _pool.pop(bid, None)
    if p:
        try:
            p["conn"].stop()
        except Exception:  # noqa: BLE001
            pass


def _preamble(ws, bot: dict, turn: _Turn, envelope: dict | None, attachments: list) -> str:
    others = [b for b in all_bots(ws) if b["id"] != bot["id"] and b.get("active", True)]
    allowed = (bot.get("delegation") or {}).get("allowed") or ["*"]
    deleg = [b for b in others if "*" in allowed or b["id"] in allowed]
    sk = skills.for_bot(ws, bot)
    mem = memory(ws, bot["id"])[-30:]
    from . import connectors
    conns = [c for c in connectors.installed() if c["id"] in (bot.get("connectors") or [])]
    ctx = {"bot": {"id": bot["id"], "name": bot["name"], "title": bot.get("title"), "main": bot.get("main", False)},
           "bots": [{"id": b["id"], "name": b["name"], "title": b.get("title"), "role": b.get("role")} for b in deleg],
           "skills": [{"name": s["name"], "kind": s["kind"], "path": s["path"]} for s in sk],
           "memory": [m["text"] for m in mem], "machine": turn.machine,
           "machines": (bot.get("machines") or {}).get("allowed", [machines.LOCAL]),
           "connectors": [c["id"] for c in conns], "scope": bot.get("scope", "."), "depth": turn.depth,
           "lang": get_lang()}
    lines = [f"<foxos-context>{json.dumps(ctx, ensure_ascii=False)}</foxos-context>",
             tr("bots.pre_identity", bot["name"], bot.get("title") or ""),
             ]
    if bot.get("role"):
        lines.append(tr("bots.pre_role", bot["role"]))
    if bot.get("instructions"):
        lines.append(tr("bots.pre_instructions", bot["instructions"]))
    lines.append(tr("bots.pre_rules", bot.get("scope", "."), turn.machine))
    if deleg and turn.depth < (bot.get("delegation") or {}).get("max_depth", MAX_DEPTH):
        lines.append(tr("bots.pre_delegate", "; ".join(f"{b['name']} ({b['id']}): {b.get('title') or ''} {b.get('role') or ''}".strip() for b in deleg)))
    if len(ctx["machines"]) > 1:
        lines.append(tr("bots.pre_machines", ", ".join(ctx["machines"]), turn.machine))
    if sk:
        lines.append(tr("bots.pre_skills") + "\n" + "\n".join(f"- {s['name']} [{s['kind']}]: {s['description'][:160]} ({s['path']})" for s in sk))
    if conns:
        lines.append(tr("bots.pre_connectors", ", ".join(f"{c['id']} ({c['title']})" for c in conns)))
    if mem:
        lines.append(tr("bots.pre_memory") + "\n" + "\n".join(f"- {m['text']}" for m in mem))
    if envelope:
        lines.append(tr("bots.pre_envelope", envelope.get("from", "?"), envelope.get("task", ""), envelope.get("constraints") or "-",
                        envelope.get("expecting") or "-"))
    return "\n\n".join(lines)


def _history(ws, bot: dict, n: int = 10) -> str:
    msgs = messages(ws, bot["id"], n)
    if not msgs:
        return ""
    return tr("bots.pre_history") + "\n" + "\n".join(f"[{m['role']}] {m.get('text', '')[:600]}" for m in msgs)


def parse_mentions(ws, text: str, self_id: str) -> tuple[list[dict], str]:
    """开头的 @名字 → 要直接交给的智能体；返回（智能体列表、剩下的任务文字）。"""
    found = []
    rest = text.strip()
    while True:
        m = re.match(r"^@([^\s:：,，]+)[\s:：,，]*", rest)
        if not m:
            break
        try:
            b = get(ws, m.group(1))
        except FoxError:
            break
        if b["id"] != self_id and b not in found:
            found.append(b)
        rest = rest[m.end():]
    return found, rest.strip()


def run_turn(ws, ref: str, text: str, *, attachments: list | None = None, actor: str = "human", origin: str = "person",
             delegated_by: str | None = None, depth: int = 0, envelope: dict | None = None, keep: bool = False,
             approval_mode: str | None = None, turn_id: str | None = None) -> dict:
    bot = get(ws, ref)
    if not bot.get("active", True):
        raise FoxError("PAUSED", tr("bots.bot_inactive", bot["name"]))
    if not text.strip() and not attachments:
        raise FoxError("USAGE", tr("bots.empty_message"))
    turn = _Turn(ws, bot, turn_id or "turn-" + uuid.uuid4().hex[:10], origin, delegated_by, depth)
    t0 = time.time()
    user_msg = {"id": "msg-" + uuid.uuid4().hex[:10], "turn": turn.turn, "role": "user", "from": actor, "text": text,
                "attachments": attachments or [], "origin": origin, "ts": audit.now_iso(),
                **({"delegated_by": delegated_by, "envelope": envelope} if delegated_by else {})}
    _append(_bot_dir(ws, bot["id"]) / "messages.jsonl", user_msg)
    turn.emit({"type": "turn_start", "message": user_msg})
    ident = f"bot:{bot['id']}"
    stop = "end_turn"
    error = None
    try:
        mentions, rest = parse_mentions(ws, text, bot["id"]) if origin in ("person", "channel", "routine") else ([], text)
        if mentions:
            for mb in mentions:
                cd = turn.card("deleg-" + mb["id"])
                cd.update(type="delegation", to=mb["id"], to_name=mb["name"], task=rest, status="in_progress", via="mention")
                turn.emit({"type": "card", "card": cd})
                try:
                    ans = run_turn(ws, mb["id"], rest or text, actor=actor, origin="mention", delegated_by=ident, depth=depth + 1,
                                   envelope={"from": bot["name"], "task": rest}, keep=keep, approval_mode=approval_mode)
                    cd.update(status="completed", answer=ans.get("text", ""), message=ans["id"], skills_used=ans.get("skills_used", []))
                except FoxError as e:
                    cd.update(status="failed", answer=e.message)
                turn.emit({"type": "card", "card": cd})
                turn.text += f"**{mb['name']}**: {cd.get('answer', '')}\n"
            stop = "end_turn"
        else:
            m = re.match(r"^/([a-z0-9][a-z0-9-]*)\b", text.strip())
            skill_block = ""
            if m:
                try:
                    s = skills.get(ws, m.group(1))
                    if s["name"] in {x["name"] for x in skills.for_bot(ws, bot)}:
                        turn.use_skill(s["name"])
                        skill_block = f"\n<foxos-skill name=\"{s['name']}\" path=\"{s['path']}\">\n{s['content']}\n</foxos-skill>\n"
                except FoxError:
                    pass
            backend = bot.get("backend") or {"kind": "acp", "agent": "foxos-local"}
            if backend["kind"] == "model":
                stop = _run_model(ws, bot, turn, text, skill_block, envelope, attachments or [])
            else:
                stop = _run_acp(ws, bot, turn, text, skill_block, envelope, attachments or [], ident, keep, approval_mode)
    except FoxError as e:
        error = e
        turn.text += ("\n" if turn.text else "") + tr("bots.turn_error", e.message)
        stop = "error"
    for rec in audit.read(ws, limit=400, agent=None):
        if rec.get("command") == "bot.skill.show" and str(rec.get("agent", "")).startswith(ident) and rec.get("ts", "") >= user_msg["ts"]:
            turn.use_skill((rec.get("args") or {}).get("name", ""))
    reply = {"id": "msg-" + uuid.uuid4().hex[:10], "turn": turn.turn, "role": "bot", "bot": bot["id"], "text": turn.text.strip(),
             "cards": [turn.cards[c] for c in turn.order], "plan": turn.plan, "skills_used": turn.skills_used,
             "machine": turn.machine, "stop_reason": stop, "origin": origin, "ts": audit.now_iso(),
             "duration_ms": round((time.time() - t0) * 1000), **({"delegated_by": delegated_by} if delegated_by else {}),
             **({"error": error.to_dict()} if error else {})}
    _append(_bot_dir(ws, bot["id"]) / "messages.jsonl", reply)
    turn.emit({"type": "turn_end", "message": reply})
    if bot.get("notifications") and origin != "person":
        _notify(bot, reply)
    if error and error.code in ("PAUSED",):
        raise error
    return reply


def _notify(bot: dict, reply: dict):
    import shutil
    import subprocess
    if shutil.which("notify-send") and os.environ.get("DISPLAY"):
        subprocess.Popen(["notify-send", "-a", "FoxOS", "-i", "dialog-information", bot["name"], reply["text"][:200]],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _prompt_blocks(ws, text: str, pre: str, skill_block: str, attachments: list) -> list[dict]:
    blocks = [{"type": "text", "text": pre + "\n\n" + skill_block + "\n" + text}]
    for a in attachments:
        p = ws.resolve(a)
        blocks.append({"type": "resource_link", "uri": p.as_uri(), "name": os.path.basename(a), "size": p.stat().st_size if p.exists() else None})
    return blocks


def _run_acp(ws, bot, turn: _Turn, text, skill_block, envelope, attachments, ident, keep, approval_mode) -> str:
    from .acp_client import AcpConnection, AcpError, foxos_mcp_server
    from .apps.acp import agent_env, installed_info
    from .kernel import paused_for
    agent_id = (bot.get("backend") or {}).get("agent", "foxos-local")
    info = installed_info(agent_id)
    if not info:
        raise FoxError("DEPENDENCY_MISSING", tr("acp.not_installed", agent_id), hint=f"foxos acp agent install {agent_id}")
    aid = f"{ident}/acp:{agent_id}"
    mach = bot.get("machines") or {}

    def call(cmd, params):
        return machines.invoke(ws, turn.machine, cmd, params, agent=aid, task=f"turn:{turn.turn}")

    def on_perm(params):
        tc = params.get("toolCall") or {}
        kind = tc.get("kind") or "other"
        opts = params.get("options") or []
        mode = approval_mode or "rules"
        dec = {"deny": "deny", "allow": "allow"}.get(mode) or _auto_decision(bot, kind)
        cd = turn.card(tc.get("toolCallId") or "perm-" + uuid.uuid4().hex[:6])
        for f in ("title", "kind"):
            if tc.get(f):
                cd.setdefault(f, tc[f])
        if dec != "ask":
            opt = _pick(opts, dec == "allow")
            cd["approval"] = {"decision": dec, "by": "rule", "optionId": opt}
            turn.emit({"type": "card", "card": cd})
            return opt
        rid = "apr-" + uuid.uuid4().hex[:10]
        a = {"id": rid, "status": "pending", "bot": bot["id"], "bot_name": bot["name"], "turn": turn.turn, "toolCall": tc,
             "options": opts, "created": audit.now_iso(), "expires": time.time() + APPROVAL_TIMEOUT, "machine": turn.machine}
        f = _approvals_dir(ws) / f"{rid}.json"
        f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
        cd["approval"] = {"request": rid, "options": opts, "decision": "pending"}
        turn.emit({"type": "card", "card": cd})
        turn.emit({"type": "approval", "request": a})
        while time.time() < a["expires"]:
            try:
                cur = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cur = a
            if cur.get("status") == "answered":
                opt = cur.get("optionId")
                kindsel = next((o.get("kind") for o in opts if o["optionId"] == opt), None)
                cd["approval"] = {"request": rid, "decision": "allow" if kindsel and kindsel.startswith("allow") else "deny",
                                  "by": cur.get("by"), "optionId": opt}
                audit.append_safe(ws, {"agent": cur.get("by", "human"), "interface": "bot", "command": "bot.approval.answer",
                                       "status": "ok", "args": {"request": rid, "bot": bot["id"], "option": opt, "tool": tc.get("title")}})
                turn.emit({"type": "card", "card": cd})
                return opt
            if paused_for(ws, aid):
                break
            time.sleep(0.25)
        a["status"] = "expired"
        f.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
        cd["approval"] = {"request": rid, "decision": "deny", "by": "timeout"}
        turn.emit({"type": "card", "card": cd})
        return _pick(opts, False)

    env = agent_env(agent_id, info)
    if bot.get("model"):
        env.setdefault("FOXOS_BOT_MODEL", bot["model"])
    mcp_env = {"FOXOS_BOT_DEPTH": str(turn.depth), "FOXOS_BOT_TURN": turn.turn, "FOXOS_BOT_MACHINE": turn.machine,
               "FOXOS_BOT_MACHINES": ",".join(mach.get("allowed") or [machines.LOCAL]), "FOXOS_TASK": f"turn:{turn.turn}",
               **({"FOXOS_BOT_APPROVE": approval_mode} if approval_mode in ("allow", "deny") else {})}
    keep = keep and not approval_mode  # 带一次性审批方式的轮次不复用连接（MCP 环境变量随连接固定）
    pooled = None
    with _pool_lock:
        if keep and bot["id"] in _pool and not _pool[bot["id"]]["conn"].closed and _pool[bot["id"]]["agent"] == agent_id:
            pooled = _pool[bot["id"]]
    new = pooled is None
    if new:
        conn = AcpConnection(info["command"], info.get("args"), env, identity=aid, workspace=ws.root, scope=bot.get("scope", "."),
                             call=call, paused=lambda: paused_for(ws, aid), readonly_roots=[r for _, r in skills.roots(ws)],
                             on_event=lambda e: None, on_permission=lambda p: None)
        conn.start()
        try:
            init = conn.initialize()
            sess = conn.new_session([foxos_mcp_server(ws.root, aid, mcp_env)])
        except AcpError as e:
            conn.stop()
            msg = str(e)
            if e.code == -32000 or "auth" in msg.lower():
                raise FoxError("PERMISSION_DENIED", tr("bots.agent_needs_login", agent_id, msg),
                               hint=f"foxos acp key set {agent_id} <ENV_NAME> --value-stdin") from e
            raise FoxError("ERROR", tr("acp.handshake_failed", agent_id, msg, conn.stderr[-400:])) from e
        pooled = {"conn": conn, "session": sess["sessionId"], "agent": agent_id, "init": init}
        if keep:
            with _pool_lock:
                _pool[bot["id"]] = pooled
    conn = pooled["conn"]
    conn.on_event = turn.on_acp
    conn.on_permission = on_perm
    conn.call = call
    pre = _preamble(ws, bot, turn, envelope, attachments)
    if new:
        h = _history(ws, bot)
        if h:
            pre += "\n\n" + h
    turn.emit({"type": "agent", "agent": agent_id, "agentInfo": (pooled.get("init") or {}).get("agentInfo")})
    try:
        r = conn.prompt(pooled["session"], _prompt_blocks(ws, text, pre, skill_block, attachments))
        return (r or {}).get("stopReason", "end_turn")
    except AcpError as e:
        raise FoxError("ERROR", tr("bots.agent_failed", agent_id, e)) from e
    finally:
        if not keep:
            conn.stop()


def _run_model(ws, bot, turn: _Turn, text, skill_block, envelope, attachments) -> str:
    """OpenAI 兼容的 /chat/completions（流式）。没有工具调用；文件、委托请用 ACP 智能体作为后端。"""
    import urllib.request
    be = bot["backend"]
    key = secrets.get(f"bot:{bot['id']}:api_key")
    pre = _preamble(ws, bot, turn, envelope, attachments)
    msgs = [{"role": "system", "content": pre}]
    for m in messages(ws, bot["id"], 12)[:-1]:
        msgs.append({"role": "user" if m["role"] == "user" else "assistant", "content": m.get("text", "")})
    msgs.append({"role": "user", "content": skill_block + text})
    body = json.dumps({"model": be["model"], "messages": msgs, "stream": True}).encode("utf-8")
    hdr = {"Content-Type": "application/json"}
    if key:
        h = be.get("auth_header") or "Authorization"
        hdr[h] = f"Bearer {key}" if h.lower() == "authorization" else key
    req = urllib.request.Request(be["base_url"] + "/chat/completions", data=body, headers=hdr, method="POST")
    turn.emit({"type": "agent", "agent": "model:" + be["model"]})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0].get("delta", {}).get("content")
                except (ValueError, KeyError, IndexError):
                    continue
                if delta:
                    turn.text += delta
                    turn.emit({"type": "text", "text": delta})
    except OSError as e:
        raise FoxError("DEPENDENCY_MISSING", tr("bots.model_failed", be["base_url"], e)) from e
    return "end_turn"


# ---------------------------------------------------------------------- 委托
def _turn_counter(ws, turn: str) -> int:
    d = root(ws) / "turns"
    d.mkdir(parents=True, exist_ok=True)
    from .activity import _flock as fl
    with fl(d / f"{turn}.lock"):
        p = d / f"{turn}.count"
        n = int(p.read_text() or 0) if p.exists() else 0
        p.write_text(str(n + 1))
        return n + 1


def delegate(ws, caller: str, to: str, task: str, constraints: str | None = None, expecting: str | None = None,
             keep: bool = False) -> dict:
    """主智能体（或任何智能体）把一件事交给另一个智能体。拒绝也作为可以说给人听的回答返回（refused: true）。"""
    if not task.strip():
        raise FoxError("USAGE", tr("bots.empty_task"))
    target = get(ws, to)
    from_id = machines._bot_of(caller) if caller.startswith("bot:") else None
    src = get(ws, from_id) if from_id else None
    depth = int(os.environ.get("FOXOS_BOT_DEPTH", "0"))
    turn = os.environ.get("FOXOS_BOT_TURN")
    cfg = (src or {}).get("delegation") or {"allowed": ["*"], "max_depth": MAX_DEPTH, "max_per_turn": MAX_PER_TURN}

    def refuse(msg):
        return {"refused": True, "to": target["id"], "answer": msg}

    if src and target["id"] == src["id"]:
        return refuse(tr("bots.refuse_self"))
    if not target.get("active", True):
        return refuse(tr("bots.bot_inactive", target["name"]))
    if src and "*" not in cfg.get("allowed", ["*"]) and target["id"] not in cfg.get("allowed", []):
        return refuse(tr("bots.refuse_not_allowed", src["name"], target["name"]))
    if depth >= cfg.get("max_depth", MAX_DEPTH):
        return refuse(tr("bots.refuse_depth", cfg.get("max_depth", MAX_DEPTH)))
    if turn and _turn_counter(ws, turn) > cfg.get("max_per_turn", MAX_PER_TURN):
        return refuse(tr("bots.refuse_per_turn", cfg.get("max_per_turn", MAX_PER_TURN)))
    env = {"from": (src or {}).get("name", caller), "task": task, "constraints": constraints, "expecting": expecting}
    body = task + (f"\n\n{tr('bots.constraints')}: {constraints}" if constraints else "") + (f"\n{tr('bots.expecting')}: {expecting}" if expecting else "")
    # 人为这一轮选了「全部允许/全部拒绝」时，委托出去的子任务沿用（环境变量只由狐狸OS 在启动智能体的 MCP 进程时设置）
    appr = os.environ.get("FOXOS_BOT_APPROVE") if caller.startswith("bot:") and os.environ.get("FOXOS_BOT_APPROVE") in ("allow", "deny") else None
    r = run_turn(ws, target["id"], body, actor=caller, origin="handoff", delegated_by=caller, depth=depth + 1, envelope=env, keep=keep,
                 approval_mode=appr)
    return {"refused": False, "to": target["id"], "to_name": target["name"], "answer": r.get("text", ""), "message": r["id"],
            "skills_used": r.get("skills_used", []), "cards": len(r.get("cards", [])), "stop_reason": r.get("stop_reason")}


# ---------------------------------------------------------------------- 例程
def _routines_path(ws) -> Path:
    return root(ws) / "routines.json"


def routines(ws) -> list[dict]:
    try:
        return json.loads(_routines_path(ws).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def _save_routines(ws, rs):
    _routines_path(ws).write_text(json.dumps(rs, ensure_ascii=False, indent=2), encoding="utf-8")


def routine_create(ws, ref: str, instruction: str, every_minutes: int, title: str | None = None) -> dict:
    b = get(ws, ref)
    if every_minutes < 15:
        raise FoxError("USAGE", tr("bots.routine_floor"))
    with _lock:
        rs = routines(ws)
        if sum(1 for r in rs if r["enabled"]) >= 20:
            raise FoxError("CONFLICT", tr("bots.routine_cap"))
        r = {"id": "rt-" + uuid.uuid4().hex[:8], "bot": b["id"], "title": title or instruction[:40], "instruction": instruction,
             "every_minutes": every_minutes, "enabled": True, "next_run": time.time() + every_minutes * 60, "last_run": None,
             "created": audit.now_iso()}
        rs.append(r)
        _save_routines(ws, rs)
    return r


def routine_update(ws, rid: str, enabled: bool | None = None, every_minutes: int | None = None) -> dict:
    with _lock:
        rs = routines(ws)
        r = next((x for x in rs if x["id"] == rid), None)
        if not r:
            raise FoxError("NOT_FOUND", tr("bots.no_such_routine", rid))
        if every_minutes is not None:
            if every_minutes < 15:
                raise FoxError("USAGE", tr("bots.routine_floor"))
            r["every_minutes"] = every_minutes
        if enabled is not None:
            if enabled and not r["enabled"] and sum(1 for x in rs if x["enabled"]) >= 20:
                raise FoxError("CONFLICT", tr("bots.routine_cap"))
            r["enabled"] = enabled
        _save_routines(ws, rs)
    return r


def routine_delete(ws, rid: str) -> dict:
    with _lock:
        rs = routines(ws)
        if not any(x["id"] == rid for x in rs):
            raise FoxError("NOT_FOUND", tr("bots.no_such_routine", rid))
        _save_routines(ws, [x for x in rs if x["id"] != rid])
    return {"deleted": rid}


def routine_tick(ws, now: float | None = None, run_id: str | None = None) -> list[dict]:
    now = now or time.time()
    due = [r for r in routines(ws) if r["enabled"] and (r["next_run"] <= now or r["id"] == run_id)]
    out = []
    for r in due:
        with _lock:
            rs = routines(ws)
            cur = next((x for x in rs if x["id"] == r["id"]), None)
            if not cur:
                continue
            cur["last_run"] = now
            cur["next_run"] = now + cur["every_minutes"] * 60
            _save_routines(ws, rs)
        try:
            rep = run_turn(ws, r["bot"], r["instruction"], actor=f"routine:{r['id']}", origin="routine")
            out.append({"routine": r["id"], "ok": True, "message": rep["id"], "text": rep["text"][:500]})
        except FoxError as e:
            out.append({"routine": r["id"], "ok": False, "error": e.to_dict()})
    return out
