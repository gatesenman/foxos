"""MCP（Model Context Protocol）服务器：stdio（每行一条 JSON-RPC 2.0 消息）与 Streamable HTTP（POST /mcp）。

支持 initialize / ping / tools/list / tools/call。tools/call 直接调用 kernel.invoke()，与 CLI 走同一内核、同一审计日志、
同一锁与人工接管规则。工具由命令注册表生成，与 CLI、docs/mcp-reference.md 同源。
"""

from __future__ import annotations

from foxos.i18n import tr
import json
import os
import sys

from . import __version__, catalog
from .errors import FoxError
from .kernel import Context, invoke
from .workspace import Workspace

SUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]


def _resp(id_, result=None, error=None) -> dict:
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg


def handle(msg: dict, state: dict) -> dict | None:
    method = msg.get("method")
    id_ = msg.get("id")
    params = msg.get("params") or {}
    if id_ is None:  # notification
        return None
    if method == "initialize":
        pv = params.get("protocolVersion")
        state["client"] = (params.get("clientInfo") or {}).get("name")
        return _resp(id_, {
            "protocolVersion": pv if pv in SUPPORTED else SUPPORTED[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "foxos", "title": tr("mcp_server.foxos"), "version": __version__},
            "instructions": (tr("mcp_server.foxos_command_kernel_paths_are") + catalog.ERROR_CODES),
        })
    if method == "ping":
        return _resp(id_, {})
    if method == "tools/list":
        return _resp(id_, {"tools": catalog.mcp_tools(state.get("profile", "compact"), state.get("apps"), state.get("names", "underscore"))})
    if method == "tools/call":
        name = params.get("name")
        args = dict(params.get("arguments") or {})
        agent = state.get("agent") or (f"mcp:{state['client']}" if state.get("client") else "mcp")
        ctx = Context(state["ws"], agent=agent, task=state.get("task"), interface="mcp")
        try:
            machine = args.pop("machine", None) or os.environ.get("FOXOS_BOT_MACHINE") or None
            if machine and machine != "local":
                allowed = [m for m in os.environ.get("FOXOS_BOT_MACHINES", "").split(",") if m]
                if os.environ.get("FOXOS_BOT_MACHINES") is not None and machine not in allowed:
                    raise FoxError("PERMISSION_DENIED", tr("machines.bot_not_allowed", machine), hint=tr("machines.bot_allowed_hint"))
                from . import machines
                result = machines.invoke(state["ws"], machine, name, args, agent, state.get("task"), interface="mcp")
            else:
                result = invoke(name, args, ctx)
            payload = {"ok": True, "command": name, "result": result}
            is_error = False
        except FoxError as e:
            payload = {"ok": False, "command": name, "error": e.to_dict()}
            is_error = True
        text = json.dumps(payload, ensure_ascii=False, default=str)
        return _resp(id_, {
            "content": [{"type": "text", "text": text}],
            "structuredContent": json.loads(text),
            "isError": is_error,
        })
    return _resp(id_, error={"code": -32601, "message": f"Method not found: {method}"})


def serve(ws: Workspace, agent_default: str | None = None, task: str | None = None, stdin=None, stdout=None,
          profile: str = "compact", apps: list[str] | None = None, names: str = "underscore") -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    state = {"ws": ws, "agent": agent_default, "task": task, "profile": profile, "apps": apps, "names": names}
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            out = _resp(None, error={"code": -32700, "message": "Parse error"})
        else:
            out = handle(msg, state)
        if out is not None:
            stdout.write(json.dumps(out, ensure_ascii=False, default=str) + "\n")
            stdout.flush()
    return 0


def serve_http(ws: Workspace, host: str = "127.0.0.1", port: int = 8765, token: str | None = None, agent_default: str | None = None,
               task: str | None = None, profile: str = "compact", apps: list[str] | None = None, names: str = "underscore", ready=None) -> int:
    """Streamable HTTP 传输（MCP 2025-03-26 起）：客户端 POST JSON-RPC 到 /mcp，服务器以 application/json 返回。

    不提供服务器主动推送（GET 返回 405，规范允许）。会话以 Mcp-Session-Id 头区分；可用 --token 要求 Bearer 认证。
    默认只监听 127.0.0.1。
    """
    import secrets
    import uuid
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    sessions: dict[str, dict] = {}

    MAX_BODY = 64 * 1024 * 1024

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):  # 不把请求写到 stderr
            pass

        def _send(self, code, body=None, headers=None):
            data = b"" if body is None else json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            if body is not None:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _auth(self) -> bool:
            if not token:
                return True
            got = self.headers.get("Authorization", "")
            return secrets.compare_digest(got, f"Bearer {token}")

        def do_GET(self):  # noqa: N802
            self._send(405, {"error": tr("mcp_server.this_server_does_not_provide_an_sse")}, {"Allow": "POST, DELETE"})

        def do_DELETE(self):  # noqa: N802
            sessions.pop(self.headers.get("Mcp-Session-Id", ""), None)
            self._send(200, {})

        def do_POST(self):  # noqa: N802
            # 先读完请求体：连接是 keep-alive，提前返回（404 / 401）时未读的请求体会被当成下一个请求
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                self.close_connection = True
                return self._send(413, {"error": "request too large"})
            body = self.rfile.read(n)
            if self.path.split("?")[0] not in ("/mcp", "/"):
                return self._send(404, {"error": "not found"})
            if not self._auth():
                return self._send(401, {"error": "unauthorized"}, {"WWW-Authenticate": "Bearer"})
            try:
                msg = json.loads(body.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return self._send(400, _resp(None, error={"code": -32700, "message": "Parse error"}))
            sid = self.headers.get("Mcp-Session-Id")
            msgs = msg if isinstance(msg, list) else [msg]
            is_init = any(isinstance(m, dict) and m.get("method") == "initialize" for m in msgs)
            if is_init:
                sid = uuid.uuid4().hex
                sessions[sid] = {"ws": ws, "agent": agent_default, "task": task, "profile": profile, "apps": apps, "names": names}
            elif not sid or sid not in sessions:
                return self._send(404 if sid else 400, _resp(None, error={"code": -32000, "message": tr("mcp_server.missing_or_invalid_mcp_session_id")}))
            outs = [o for o in (handle(m, sessions[sid]) for m in msgs if isinstance(m, dict)) if o is not None]
            hdr = {"Mcp-Session-Id": sid}
            if not outs:
                return self._send(202, None, hdr)
            self._send(200, outs if isinstance(msg, list) else outs[0], hdr)

    srv = ThreadingHTTPServer((host, port), H)
    url = f"http://{srv.server_address[0]}:{srv.server_address[1]}/mcp"
    if ready:
        ready(url)
    else:
        print(json.dumps({"url": url, "auth": "bearer" if token else None}, ensure_ascii=False), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
