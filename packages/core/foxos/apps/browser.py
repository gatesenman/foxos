"""Google Chrome：启动、打开网页、标签页、截图，以及本机 CDP（Chrome DevTools Protocol）。

CDP 默认关闭。打开需要人（human 身份）执行 `foxos browser cdp on`：之后 狐狸OS 启动的
Chrome 只监听 127.0.0.1（不对局域网开放），并使用单独的「智能体配置文件」
（~/.config/foxos/chrome-agent），不会把你日常 Chrome 配置里的登录态交给智能体。
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, register, register_app

DEFAULT_PORT = 9222
LOCALHOST = "127.0.0.1"
_CANDIDATES = ("google-chrome-stable", "google-chrome", "chrome")
ALIASES = {"chrome", "google-chrome", "google-chrome-stable", "browser"}


# ------------------------------------------------------------------ 配置与可执行文件

def _cfg_path(ctx: Context) -> Path:
    return ctx.workspace.data_dir / "browser.json"


def load_cfg(ctx: Context) -> dict:
    try:
        d = json.loads(_cfg_path(ctx).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    port = int(os.environ.get("FOXOS_CHROME_CDP_PORT") or d.get("port") or DEFAULT_PORT)
    return {"cdp": bool(d.get("cdp", False)), "port": port, "backend": d.get("backend") or "auto"}


def save_cfg(ctx: Context, cfg: dict) -> None:
    try:
        d = json.loads(_cfg_path(ctx).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    d.update({k: v for k, v in cfg.items() if k in ("backend",)})
    _cfg_path(ctx).write_text(json.dumps(d, indent=1), encoding="utf-8")


def chrome_binary() -> str | None:
    env = os.environ.get("FOXOS_CHROME")
    if env:
        return env if (os.path.isabs(env) and os.access(env, os.X_OK)) else shutil.which(env)
    for c in _CANDIDATES:
        p = shutil.which(c)
        if p:
            return p
    return None


def _require_chrome() -> str:
    b = chrome_binary()
    if not b:
        raise FoxError("DEPENDENCY_MISSING", tr("browser.chrome_not_installed"), hint=tr("browser.install_hint"))
    return b


def agent_profile_dir() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "foxos" / "chrome-agent"


def chrome_argv(ctx: Context, extra: list[str]) -> list[str]:
    """`foxos desktop launch chrome …` 与 `foxos browser open` 共用的启动参数。"""
    cfg = load_cfg(ctx)
    argv = [_require_chrome(), "--no-first-run", "--no-default-browser-check", "--lang=zh-CN" if _lang_zh() else "--lang=en-US"]
    if cfg["cdp"]:
        prof = agent_profile_dir()
        prof.mkdir(parents=True, exist_ok=True)
        argv += [f"--user-data-dir={prof}", f"--remote-debugging-address={LOCALHOST}", f"--remote-debugging-port={cfg['port']}"]
    argv += [a for a in (os.environ.get("FOXOS_CHROME_FLAGS") or "").split() if a]
    return argv + list(extra)


def _lang_zh() -> bool:
    from .. import i18n
    return str(getattr(i18n, "_lang", "zh-CN")).lower().startswith("zh")


# ------------------------------------------------------------------ CDP：HTTP 端点

def _http(ctx: Context, path: str, method: str = "GET", timeout: float = 3.0):
    port = load_cfg(ctx)["port"]
    req = urllib.request.Request(f"http://{LOCALHOST}:{port}{path}", method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — 只连 127.0.0.1
        body = r.read().decode("utf-8", "replace")
    try:
        return json.loads(body)
    except ValueError:
        return body


def _cdp_version(ctx: Context) -> dict | None:
    try:
        v = _http(ctx, "/json/version", timeout=1.5)
        return v if isinstance(v, dict) else None
    except (OSError, urllib.error.URLError):
        return None


def _require_cdp(ctx: Context) -> None:
    cfg = load_cfg(ctx)
    if not cfg["cdp"]:
        raise FoxError("PERMISSION_DENIED", tr("browser.cdp_disabled"), hint=tr("browser.cdp_enable_hint"))
    if _cdp_version(ctx) is None:
        raise FoxError("NOT_FOUND", tr("browser.cdp_not_running", cfg["port"]), hint=tr("browser.cdp_start_hint"))


def _pages(ctx: Context) -> list[dict]:
    lst = _http(ctx, "/json/list")
    return [{"id": t.get("id"), "title": t.get("title"), "url": t.get("url"), "ws": t.get("webSocketDebuggerUrl")}
            for t in (lst or []) if t.get("type") == "page"]


def _page(ctx: Context, tab: str | None) -> dict:
    pages = _pages(ctx)
    if not pages:
        raise FoxError("NOT_FOUND", tr("browser.no_tabs"))
    if not tab:
        return pages[0]
    for p in pages:
        if p["id"] == tab or str(p["id"]).startswith(tab):
            return p
    raise FoxError("NOT_FOUND", tr("browser.no_tab", tab))


# ------------------------------------------------------------------ CDP：最小 WebSocket 客户端（标准库）

class _WS:
    def __init__(self, url: str, timeout: float = 15.0):
        u = urllib.parse.urlparse(url)
        if u.hostname not in ("127.0.0.1", "localhost"):
            raise FoxError("PERMISSION_DENIED", tr("browser.cdp_localhost_only"))
        self.s = socket.create_connection((u.hostname, u.port or 80), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self.s.recv(4096)
            if not chunk:
                break
            head += chunk
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise FoxError("ERROR", tr("browser.cdp_handshake_failed", head.split(b"\r\n", 1)[0].decode("latin-1")))
        self.buf = head.split(b"\r\n\r\n", 1)[1]
        self.n = 0

    def _recvn(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.s.recv(max(65536, n - len(self.buf)))
            if not chunk:
                raise FoxError("ERROR", tr("browser.cdp_closed"))
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, obj: dict) -> None:
        data = json.dumps(obj).encode()
        hdr = bytearray([0x81])
        n = len(data)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
        mask = os.urandom(4)
        self.s.sendall(bytes(hdr) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self) -> dict:
        payload = b""
        while True:
            b1, b2 = self._recvn(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recvn(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recvn(8))[0]
            data = self._recvn(n)
            op = b1 & 0x0F
            if op == 0x8:
                raise FoxError("ERROR", tr("browser.cdp_closed"))
            if op in (0x9, 0xA):
                continue
            payload += data
            if b1 & 0x80:
                return json.loads(payload.decode("utf-8"))

    def call(self, method: str, params: dict | None = None) -> dict:
        self.n += 1
        mid = self.n
        self.send({"id": mid, "method": method, "params": params or {}})
        while True:
            m = self.recv()
            if m.get("id") == mid:
                if "error" in m:
                    raise FoxError("ERROR", tr("browser.cdp_error", method, m["error"].get("message")))
                return m.get("result") or {}

    def close(self) -> None:
        try:
            self.s.close()
        except OSError:
            pass


# ------------------------------------------------------------------ 命令

def browser_status(ctx: Context) -> dict:
    b = chrome_binary()
    version = None
    if b:
        try:
            version = subprocess.run([b, "--version"], capture_output=True, text=True, timeout=10).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            version = None
    cfg = load_cfg(ctx)
    v = _cdp_version(ctx) if cfg["cdp"] else None
    return {"installed": bool(b), "binary": b, "version": version,
            "cdp": {"enabled": cfg["cdp"], "address": LOCALHOST, "port": cfg["port"], "running": v is not None,
                    **({"browser": v.get("Browser")} if v else {}),
                    "profile": str(agent_profile_dir()) if cfg["cdp"] else None}}


def browser_cdp(ctx: Context, state: str, port: int | None = None) -> dict:
    from ..kernel import is_human
    s = str(state).strip().lower()
    if s not in ("on", "off", "enable", "disable", "true", "false", "1", "0"):
        raise FoxError("USAGE", tr("browser.cdp_state_usage"))
    on = s in ("on", "enable", "true", "1")
    if on and not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("browser.cdp_human_only"))
    cfg = load_cfg(ctx)
    cfg["cdp"] = on
    if port:
        p = int(port)
        if not 1024 <= p <= 65535:
            raise FoxError("USAGE", tr("browser.bad_port"))
        cfg["port"] = p
    _cfg_path(ctx).write_text(json.dumps(cfg), encoding="utf-8")
    return {"message": tr("browser.cdp_now_on", cfg["port"]) if on else tr("browser.cdp_now_off"),
            "cdp": {"enabled": on, "address": LOCALHOST, "port": cfg["port"]}, "restart_needed": True}


def browser_open(ctx: Context, url: str, wait: float = 15.0) -> dict:
    cfg = load_cfg(ctx)
    if cfg["cdp"] and _cdp_version(ctx) is not None:
        t = _http(ctx, "/json/new?" + urllib.parse.quote(url, safe=":/?&=#%"), method="PUT")
        return {"message": tr("browser.opened", url), "url": url, "tab": t.get("id") if isinstance(t, dict) else None, "via": "cdp"}
    from ..session import get_backend
    r = get_backend(ctx.workspace).launch(chrome_argv(ctx, ["--new-window", url]))
    out = {"message": tr("browser.opened", url), "url": url, "pid": r.get("pid"), "via": "launch"}
    if cfg["cdp"]:
        deadline = time.time() + float(wait or 0)
        while time.time() < deadline and _cdp_version(ctx) is None:
            time.sleep(0.3)
        if _cdp_version(ctx) is not None:
            out["tab"] = next((p["id"] for p in _pages(ctx) if p["url"].rstrip("/") == url.rstrip("/")), None)
            out["cdp"] = True
    return out


def browser_tabs(ctx: Context) -> dict:
    _require_cdp(ctx)
    pages = [{k: v for k, v in p.items() if k != "ws"} for p in _pages(ctx)]
    return {"count": len(pages), "tabs": pages}


def browser_navigate(ctx: Context, url: str, tab: str | None = None) -> dict:
    _require_cdp(ctx)
    p = _page(ctx, tab)
    ws = _WS(p["ws"])
    try:
        ws.call("Page.enable")
        r = ws.call("Page.navigate", {"url": url})
        for _ in range(100):
            st = ws.call("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
            if (st.get("result") or {}).get("value") == "complete":
                break
            time.sleep(0.2)
        title = ws.call("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
    finally:
        ws.close()
    return {"message": tr("browser.navigated", url), "tab": p["id"], "url": url, "frame": r.get("frameId"),
            "title": (title.get("result") or {}).get("value")}


def browser_eval(ctx: Context, expression: str, tab: str | None = None) -> dict:
    _require_cdp(ctx)
    p = _page(ctx, tab)
    ws = _WS(p["ws"])
    try:
        r = ws.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
    finally:
        ws.close()
    if r.get("exceptionDetails"):
        raise FoxError("ERROR", tr("browser.eval_exception", (r["exceptionDetails"].get("exception") or {}).get("description") or r["exceptionDetails"].get("text")))
    return {"tab": p["id"], "value": (r.get("result") or {}).get("value")}


def browser_screenshot(ctx: Context, path: str | None = None, tab: str | None = None) -> dict:
    _require_cdp(ctx)
    p = _page(ctx, tab)
    from .desktop import _ts
    dest = ctx.workspace.root / (path or f".foxos/screenshots/chrome-{_ts()}.png")
    ws = _WS(p["ws"])
    try:
        r = ws.call("Page.captureScreenshot", {"format": "png"})
    finally:
        ws.close()
    data = base64.b64decode(r.get("data") or b"")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    rel = ctx.workspace.rel(dest) if str(dest).startswith(str(ctx.workspace.root)) else str(dest)
    return {"message": tr("desktop.saved_screenshot", rel), "path": rel, "bytes": len(data), "tab": p["id"], "url": p["url"]}


def browser_close(ctx: Context, tab: str) -> dict:
    _require_cdp(ctx)
    p = _page(ctx, tab)
    _http(ctx, f"/json/close/{p['id']}")
    return {"message": tr("browser.closed_tab", p["id"]), "tab": p["id"]}


register_app("browser", tr("browser.app_title"), tr("browser.app_summary"))
_TAB = Param("tab", "string", tr("browser.tab_id_param"))
register(Command("browser", "status", tr("browser.status_summary"), browser_status,
                 examples=["foxos browser status --json"], audited=False))
register(Command("browser", "cdp", tr("browser.cdp_summary"), browser_cdp,
                 params=[Param("state", "string", tr("browser.cdp_state_param"), required=True, positional=True, metavar="on|off"),
                         Param("port", "integer", tr("browser.port_param"))],
                 examples=["foxos browser cdp on", "foxos browser cdp off"],
                 limits=[tr("browser.cdp_limit_human"), tr("browser.cdp_limit_localhost")], permission="modify"))
register(Command("browser", "open", tr("browser.open_summary"), browser_open,
                 params=[Param("url", "string", tr("browser.url_param"), required=True, positional=True, metavar="URL"),
                         Param("wait", "number", tr("browser.wait_param"), default=15.0)],
                 examples=["foxos browser open https://github.com/gatesenman/foxos"], permission="run"))
register(Command("browser", "tabs", tr("browser.tabs_summary"), browser_tabs,
                 examples=["foxos browser tabs --json"], permission="read"))
register(Command("browser", "navigate", tr("browser.navigate_summary"), browser_navigate,
                 params=[Param("url", "string", tr("browser.url_param"), required=True, positional=True, metavar="URL"), _TAB],
                 examples=["foxos browser navigate https://example.com --tab 3F2A"], permission="modify"))
register(Command("browser", "eval", tr("browser.eval_summary"), browser_eval,
                 params=[Param("expression", "string", tr("browser.expression_param"), required=True, positional=True, metavar="JS"), _TAB],
                 examples=["foxos browser eval 'document.title'"], permission="modify"))
register(Command("browser", "screenshot", tr("browser.screenshot_summary"), browser_screenshot,
                 params=[Param("path", "string", tr("desktop.workspace_relative_png_path"), path="write"), _TAB],
                 examples=["foxos browser screenshot --path shots/page.png"], permission="read"))
register(Command("browser", "close", tr("browser.close_summary"), browser_close,
                 params=[Param("tab", "string", tr("browser.tab_id_param"), required=True, positional=True, metavar="TAB")],
                 examples=["foxos browser close 3F2A"], permission="modify"))


# ------------------------------------------------------------------ 浏览器操控：无障碍快照 + ref（Playwright MCP 同款做法）

def _ab(ctx: Context):
    """agent-browser 后端（装了且没有设成 builtin 时）；否则 None，用内置 CDP 实现。"""
    want = load_cfg(ctx).get("backend") or "auto"
    if want == "builtin":
        return None
    from ..cu import agent_browser
    if agent_browser.binary():
        return agent_browser
    if want == "agent-browser":
        raise FoxError("DEPENDENCY_MISSING", tr("ab.missing"), hint="foxos browser engine install agent-browser")
    return None


def browser_snapshot(ctx: Context, tab: str | None = None, max_chars: int = 40000, interactive: bool = False) -> dict:
    ab = _ab(ctx)
    if ab:
        r = ab.snapshot(ctx, tab or _page(ctx, None)["id"], bool(interactive))
        if len(r["snapshot"]) > max_chars:
            r["snapshot"], r["truncated"] = r["snapshot"][:max_chars], True
        return r
    from ..cu import cdp
    return cdp.snapshot(ctx, tab, int(max_chars), bool(interactive))


def browser_click(ctx: Context, ref: str, tab: str | None = None, double: bool = False, button: str = "left") -> dict:
    ab = _ab(ctx)
    if ab and not double and button == "left":
        return ab.click(ctx, ref, tab)
    from ..cu import cdp
    return cdp.click(ctx, ref, tab, button, bool(double))


def browser_type(ctx: Context, ref: str, text: str, tab: str | None = None, submit: bool = False, append: bool = False) -> dict:
    ab = _ab(ctx)
    if ab and not append:
        return ab.fill(ctx, ref, text, tab, bool(submit))
    from ..cu import cdp
    return cdp.type_text(ctx, ref, text, tab, bool(submit), clear=not append)


def browser_press(ctx: Context, key: str, tab: str | None = None) -> dict:
    ab = _ab(ctx)
    if ab:
        return ab.press(ctx, key, tab)
    from ..cu import cdp
    return cdp.press(ctx, key, tab)


def browser_select(ctx: Context, ref: str, value: str, tab: str | None = None) -> dict:
    ab = _ab(ctx)
    if ab:
        return ab.select(ctx, ref, value, tab)
    from ..cu import cdp
    return cdp.select_option(ctx, ref, value, tab)


def browser_scroll(ctx: Context, direction: str = "down", amount: int = 600, tab: str | None = None) -> dict:
    ab = _ab(ctx)
    if ab and direction in ("up", "down"):
        return ab.scroll(ctx, direction, int(amount), tab)
    from ..cu import cdp
    return cdp.scroll(ctx, direction, int(amount), tab)


def browser_back(ctx: Context, tab: str | None = None) -> dict:
    ab = _ab(ctx)
    if ab:
        return ab.back(ctx, tab)
    from ..cu import cdp
    return cdp.history(ctx, -1, tab)


def browser_backend_set(ctx: Context, backend: str) -> dict:
    cfg = load_cfg(ctx)
    cfg["backend"] = backend
    save_cfg(ctx, cfg)
    from ..cu import agent_browser
    return {"backend": backend, "agent_browser": agent_browser.status(),
            "active": "agent-browser" if _ab(ctx) else "builtin"}


def browser_backend_status(ctx: Context) -> dict:
    from ..cu import agent_browser
    try:
        active = "agent-browser" if _ab(ctx) else "builtin"
    except FoxError as e:
        active = f"error: {e.message}"
    return {"backend": load_cfg(ctx).get("backend") or "auto", "active": active, "agent_browser": agent_browser.status()}


def browser_forward(ctx: Context, tab: str | None = None) -> dict:
    from ..cu import cdp
    return cdp.history(ctx, 1, tab)


def browser_text(ctx: Context, tab: str | None = None, ref: str | None = None, max_chars: int = 30000) -> dict:
    from ..cu import cdp
    return cdp.page_text(ctx, tab, ref, int(max_chars))


def browser_wait(ctx: Context, text: str | None = None, seconds: float = 0, tab: str | None = None, timeout: float = 20) -> dict:
    from ..cu import cdp
    return cdp.wait_for(ctx, text, float(seconds or 0), tab, float(timeout))


def browser_download(ctx: Context, url: str | None = None, ref: str | None = None, tab: str | None = None, timeout: float = 120) -> dict:
    from ..cu import cdp
    return cdp.download(ctx, url, ref, tab, float(timeout))


def browser_downloads(ctx: Context) -> dict:
    from ..cu import cdp
    return cdp.list_downloads(ctx)


def browser_tab_select(ctx: Context, tab: str) -> dict:
    _require_cdp(ctx)
    p = _page(ctx, tab)
    _http(ctx, f"/json/activate/{p['id']}")
    return {"message": tr("cu.tab_selected", p["id"]), "tab": p["id"], "url": p["url"], "title": p["title"]}


def browser_tab_new(ctx: Context, url: str = "about:blank") -> dict:
    _require_cdp(ctx)
    t = _http(ctx, "/json/new?" + urllib.parse.quote(url, safe=":/?&=#%"), method="PUT")
    return {"message": tr("browser.opened", url), "tab": t.get("id") if isinstance(t, dict) else None, "url": url}


def ensure_running(ctx: Context, wait: float = 20.0) -> None:
    """browser task 用：CDP 已由人开启但 Chrome 没在跑时，按狐狸OS 参数启动它。"""
    cfg = load_cfg(ctx)
    if not cfg["cdp"]:
        raise FoxError("PERMISSION_DENIED", tr("browser.cdp_disabled"), hint=tr("browser.cdp_enable_hint"))
    if _cdp_version(ctx) is None:
        browser_open(ctx, "about:blank", wait=wait)
    if _cdp_version(ctx) is None:
        raise FoxError("NOT_FOUND", tr("browser.cdp_not_running", cfg["port"]), hint=tr("browser.cdp_start_hint"))


def browser_task(ctx: Context, task: str, url: str | None = None, mode: str = "s1s2", policy: str = "auto", max_steps: int = 25,
                 approve: str = "risky", vision: str = "auto", tab: str | None = None) -> dict:
    """智能体循环：给一句话任务，模型看无障碍快照、按 ref 操作，直到完成并给出答案。"""
    ensure_running(ctx)
    if not tab:
        t = browser_tab_new(ctx, url or "about:blank")
        tab = t["tab"]
        if url:
            time.sleep(1.0)
    elif url:
        browser_navigate(ctx, url, tab)
    if mode == "llm":
        from ..cu.loop import Loop
        return Loop(ctx, "browser", task, max_steps=int(max_steps), approve=approve, vision=vision, tab=tab).run()
    from ..cu.agent import Agent
    return Agent(ctx, "browser", task, policy=policy, max_steps=int(max_steps), approve=approve, vision=vision, tab=tab).run()


def browser_engine_status(ctx: Context) -> dict:
    from ..cu import engines
    return engines.status()


def browser_engine_install(ctx: Context, engine: str) -> dict:
    from ..cu import engines
    return engines.install(engine)


def browser_engine_call(ctx: Context, engine: str, tool: str, args: dict | None = None) -> dict:
    from ..cu import engines
    ensure_running(ctx)
    return engines.call(ctx, engine, tool, args or {})


def browser_engine_tools(ctx: Context, engine: str) -> dict:
    from ..cu import engines
    ensure_running(ctx)
    return engines.tools(ctx, engine)


_REF = Param("ref", "string", tr("cu.p_ref"), required=True, positional=True, metavar="REF")
register(Command("browser", "snapshot", tr("cu.c_snapshot"), browser_snapshot,
                 params=[_TAB, Param("max_chars", "integer", tr("cu.p_max_chars"), default=40000),
                         Param("interactive", "boolean", tr("cu.p_interactive"), default=False)],
                 examples=["foxos browser snapshot", "foxos browser snapshot --interactive --json"],
                 limits=[tr("cu.l_snapshot")], permission="read", audited=False))
register(Command("browser", "click", tr("cu.c_click"), browser_click,
                 params=[_REF, _TAB, Param("double", "boolean", tr("cu.p_double"), default=False),
                         Param("button", "string", tr("cu.p_button"), enum=["left", "right", "middle"], default="left")],
                 examples=["foxos browser click e12"], permission="modify"))
register(Command("browser", "type", tr("cu.c_type"), browser_type,
                 params=[_REF, Param("text", "string", tr("cu.p_text"), required=True, positional=True, metavar="TEXT"), _TAB,
                         Param("submit", "boolean", tr("cu.p_submit"), default=False), Param("append", "boolean", tr("cu.p_append"), default=False)],
                 examples=["foxos browser type e5 'FoxOS' --submit"], permission="modify"))
register(Command("browser", "press", tr("cu.c_press"), browser_press,
                 params=[Param("key", "string", tr("cu.p_key"), required=True, positional=True, metavar="KEY"), _TAB],
                 examples=["foxos browser press Enter", "foxos browser press ctrl+a"], permission="modify"))
register(Command("browser", "select", tr("cu.c_select"), browser_select,
                 params=[_REF, Param("value", "string", tr("cu.p_value"), required=True, positional=True, metavar="VALUE"), _TAB],
                 examples=["foxos browser select e9 '中文'"], permission="modify"))
register(Command("browser", "scroll", tr("cu.c_scroll"), browser_scroll,
                 params=[Param("direction", "string", tr("cu.p_direction"), enum=["down", "up", "left", "right"], default="down", positional=True, metavar="DIR"),
                         Param("amount", "integer", tr("cu.p_amount"), default=600), _TAB],
                 examples=["foxos browser scroll down"], permission="read"))
register(Command("browser", "back", tr("cu.c_back"), browser_back, params=[_TAB], examples=["foxos browser back"], permission="modify"))
register(Command("browser", "forward", tr("cu.c_forward"), browser_forward, params=[_TAB], examples=["foxos browser forward"], permission="modify"))
register(Command("browser", "text", tr("cu.c_text"), browser_text,
                 params=[_TAB, Param("ref", "string", tr("cu.p_ref_opt")), Param("max_chars", "integer", tr("cu.p_max_chars"), default=30000)],
                 examples=["foxos browser text", "foxos browser text --ref e40"], permission="read", audited=False))
register(Command("browser", "wait", tr("cu.c_wait"), browser_wait,
                 params=[Param("text", "string", tr("cu.p_wait_text")), Param("seconds", "number", tr("cu.p_seconds")), _TAB,
                         Param("timeout", "number", tr("cu.p_timeout"), default=20)],
                 examples=["foxos browser wait --text '结果'", "foxos browser wait --seconds 2"], permission="read", audited=False))
register(Command("browser", "download", tr("cu.c_download"), browser_download,
                 params=[Param("url", "string", tr("browser.url_param")), Param("ref", "string", tr("cu.p_ref_opt")), _TAB,
                         Param("timeout", "number", tr("cu.p_timeout"), default=120)],
                 examples=["foxos browser download --url https://example.com/file.pdf", "foxos browser download --ref e33"],
                 limits=[tr("cu.l_download")], permission="create"))
register(Command("browser", "downloads", tr("cu.c_downloads"), browser_downloads, examples=["foxos browser downloads --json"], permission="read"))
register(Command("browser", "tab select", tr("cu.c_tab_select"), browser_tab_select,
                 params=[Param("tab", "string", tr("browser.tab_id_param"), required=True, positional=True, metavar="TAB")],
                 examples=["foxos browser tab select 3F2A"], permission="modify"))
register(Command("browser", "tab new", tr("cu.c_tab_new"), browser_tab_new,
                 params=[Param("url", "string", tr("browser.url_param"), default="about:blank", positional=True, metavar="URL")],
                 examples=["foxos browser tab new https://example.com"], permission="run"))
register(Command("browser", "task", tr("cu.c_task"), browser_task,
                 params=[Param("task", "string", tr("cu.p_task"), required=True, positional=True, metavar="TASK"),
                         Param("url", "string", tr("cu.p_start_url")),
                         Param("mode", "string", tr("cu.p_mode"), enum=["s1s2", "llm"], default="s1s2"),
                         Param("policy", "string", tr("cu.p_policy"), enum=["auto", "typesafe", "deepseek"], default="auto"),
                         Param("max_steps", "integer", tr("cu.p_max_steps"), default=25),
                         Param("approve", "string", tr("cu.p_approve"), enum=["risky", "ask", "auto", "deny"], default="risky"),
                         Param("vision", "string", tr("cu.p_vision"), enum=["auto", "on", "off"], default="auto"), _TAB],
                 examples=["foxos browser task '在维基百科查珠穆朗玛峰的海拔' --url https://zh.wikipedia.org --vision off",
                           "foxos browser task 'find the latest FoxOS release name' --url https://github.com/gatesenman/foxos --mode llm"],
                 limits=[tr("cu.l_task_model"), tr("cu.l_task_approve")], permission="run"))
register(Command("browser", "backend set", tr("ab.c_backend_set"), browser_backend_set,
                 params=[Param("backend", "string", tr("ab.p_backend"), required=True, positional=True, metavar="BACKEND",
                               enum=["auto", "agent-browser", "builtin"])],
                 examples=["foxos browser backend set agent-browser", "foxos browser backend set builtin"], permission="modify"))
register(Command("browser", "backend status", tr("ab.c_backend_status"), browser_backend_status,
                 examples=["foxos browser backend status --json"], permission="read", audited=False))
register(Command("browser", "engine status", tr("cu.c_engine_status"), browser_engine_status,
                 examples=["foxos browser engine status --json"], permission="read", audited=False))
register(Command("browser", "engine install", tr("cu.c_engine_install"), browser_engine_install,
                 params=[Param("engine", "string", tr("cu.p_engine_name"), required=True, positional=True, metavar="ENGINE",
                               enum=["agent-browser", "playwright-mcp"])],
                 examples=["foxos browser engine install agent-browser", "foxos browser engine install playwright-mcp"], permission="run"))
register(Command("browser", "engine tools", tr("cu.c_engine_tools"), browser_engine_tools,
                 params=[Param("engine", "string", tr("cu.p_engine_name"), required=True, positional=True, metavar="ENGINE",
                               enum=["agent-browser", "playwright-mcp"])],
                 examples=["foxos browser engine tools playwright-mcp"], permission="read"))
register(Command("browser", "engine call", tr("cu.c_engine_call"), browser_engine_call,
                 params=[Param("engine", "string", tr("cu.p_engine_name"), required=True, positional=True, metavar="ENGINE",
                               enum=["agent-browser", "playwright-mcp"]),
                         Param("tool", "string", tr("cu.p_tool"), required=True, positional=True, metavar="TOOL"),
                         Param("args", "object", tr("cu.p_args"))],
                 examples=["foxos browser engine call playwright-mcp browser_snapshot",
                           "foxos browser engine call playwright-mcp browser_navigate --args '{\"url\": \"https://example.com\"}'"], permission="modify"))
