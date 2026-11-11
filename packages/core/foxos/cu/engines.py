"""外部开源浏览器引擎：安装时作为依赖下载（不打进仓库），各自独立进程运行。

- agent-browser        Vercel Labs agent-browser（Apache-2.0），npm 包 agent-browser，经 --cdp 连狐狸OS 的 Chrome；
                       也是 foxos browser 的可选观察 / 操作后端（foxos browser backend set agent-browser）
- playwright-mcp       Microsoft Playwright MCP（Apache-2.0），npm 包 @playwright/mcp，经 --cdp-endpoint 连狐狸OS 的 Chrome
它们的 MCP 服务器也会交给 ACP 智能体（按智能体设置）。少而精：browser-use、Chrome DevTools MCP 已评估但不集成，
见 docs/computer-use-research.md。
系统镜像把它们预装在 /usr/lib/foxos/tools/<引擎>；用户安装的在 FOXOS_HOME/tools/<引擎>。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

PINS = {"agent-browser": "agent-browser@0.42.0", "playwright-mcp": "@playwright/mcp@0.0.85"}
LICENSES = {"agent-browser": "Apache-2.0", "playwright-mcp": "Apache-2.0"}
SYSTEM_TOOLS = Path(os.environ.get("FOXOS_SYSTEM_TOOLS", "/usr/lib/foxos/tools"))


def user_dir(engine: str) -> Path:
    return secrets.home() / "tools" / engine


def _entry(engine: str, base: Path) -> list[str] | None:
    if engine == "agent-browser":
        f = base / "node_modules" / ".bin" / "agent-browser"
        return [str(f)] if f.exists() else None
    if engine == "playwright-mcp":
        f = base / "node_modules" / "@playwright" / "mcp" / "cli.js"
        return [shutil.which("node") or "node", str(f)] if f.exists() else None
    return None


def entry(engine: str) -> list[str] | None:
    for base in (user_dir(engine), SYSTEM_TOOLS / engine):
        e = _entry(engine, base)
        if e:
            return e
    return None


def status() -> dict:
    out = []
    for e in PINS:
        ent = entry(e)
        out.append({"engine": e, "installed": bool(ent), "package": PINS[e], "license": LICENSES[e],
                    "path": ent[-1] if ent else None})
    return {"engines": out, "node": shutil.which("node")}


def install(engine: str) -> dict:
    d = user_dir(engine)
    d.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if engine in ("agent-browser", "playwright-mcp"):
        npm = shutil.which("npm")
        if not npm:
            raise FoxError("DEPENDENCY_MISSING", tr("cu.need_node"))
        p = subprocess.run([npm, "install", "--no-audit", "--no-fund", "--prefix", str(d), PINS[engine]], capture_output=True, text=True, timeout=900)
    else:
        raise FoxError("USAGE", tr("cu.bad_engine", engine))
    if p.returncode != 0:
        raise FoxError("ERROR", tr("cu.engine_install_failed", engine, (p.stderr or p.stdout)[-600:]))
    return {"message": tr("cu.engine_installed", engine), "engine": engine, "package": PINS[engine], "license": LICENSES[engine],
            "path": str(d), "seconds": round(time.time() - t0, 1)}


def cdp_endpoint(ctx) -> str:
    from ..apps.browser import LOCALHOST, load_cfg
    return f"http://{LOCALHOST}:{load_cfg(ctx)['port']}"


def mcp_spec(engine: str, cdp_url: str) -> dict | None:
    """ACP session/new 用的 stdio MCP 服务器描述。"""
    ent = entry(engine)
    if not ent:
        return None
    if engine == "agent-browser":
        args = [*ent[1:], "--cdp", cdp_url.rsplit(":", 1)[-1], "mcp"]
        name = "agent-browser"
    elif engine == "playwright-mcp":
        args = [*ent[1:], "--cdp-endpoint", cdp_url]
        name = "playwright"
    else:
        return None
    return {"name": name, "command": ent[0], "args": args, "env": []}


class StdioMcp:
    def __init__(self, spec: dict, timeout: float = 60, cwd: str | None = None):
        env = {**os.environ, **{e["name"]: e["value"] for e in spec.get("env") or []}}
        self.p = subprocess.Popen([spec["command"], *spec.get("args", [])], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=env, text=True, encoding="utf-8", cwd=cwd)
        self.n = 0
        self.timeout = timeout
        self.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "foxos", "version": "1"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.p.stdin.flush()

    def call(self, method: str, params: dict) -> dict:
        import select
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}, ensure_ascii=False) + "\n")
        self.p.stdin.flush()
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            r, _, _ = select.select([self.p.stdout], [], [], 1.0)
            if not r:
                if self.p.poll() is not None:
                    break
                continue
            line = self.p.stdout.readline()
            if not line:
                break
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if m.get("id") == self.n:
                if m.get("error"):
                    raise FoxError("ERROR", tr("cu.mcp_error", method, m["error"].get("message")))
                return m.get("result") or {}
        err = ""
        if self.p.poll() is not None and self.p.stderr:
            err = self.p.stderr.read()[-500:]
        raise FoxError("ERROR", tr("cu.mcp_no_reply", method, err))

    def close(self):
        try:
            self.p.stdin.close()
            self.p.terminate()
            self.p.wait(timeout=5)
        except Exception:  # noqa: BLE001
            self.p.kill()


def _client(ctx, engine: str) -> StdioMcp:
    spec = mcp_spec(engine, cdp_endpoint(ctx))
    if not spec:
        raise FoxError("DEPENDENCY_MISSING", tr("cu.engine_missing", engine), hint=f"foxos browser engine install {engine}")
    d = ctx.workspace.data_dir / engine  # 引擎自己的输出（快照文件、截图）放在 .foxos/<引擎>/
    d.mkdir(parents=True, exist_ok=True)
    return StdioMcp(spec, timeout=90, cwd=str(d))


def tools(ctx, engine: str) -> dict:
    c = _client(ctx, engine)
    try:
        ts = c.call("tools/list", {}).get("tools") or []
    finally:
        c.close()
    return {"engine": engine, "count": len(ts), "tools": [{"name": t["name"], "description": (t.get("description") or "")[:200]} for t in ts]}


def call(ctx, engine: str, tool: str, args: dict) -> dict:
    c = _client(ctx, engine)
    try:
        r = c.call("tools/call", {"name": tool, "arguments": args})
    finally:
        c.close()
    texts = [x.get("text") for x in r.get("content") or [] if x.get("type") == "text"]
    return {"engine": engine, "tool": tool, "isError": bool(r.get("isError")), "text": "\n".join(t for t in texts if t)[:60000],
            "images": sum(1 for x in r.get("content") or [] if x.get("type") == "image")}
