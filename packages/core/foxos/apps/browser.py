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
    return {"cdp": bool(d.get("cdp", False)), "port": port}


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
