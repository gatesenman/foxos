"""最小 MCP（Model Context Protocol）stdio 服务器。

每行一条 JSON-RPC 2.0 消息。支持 initialize / ping / tools/list / tools/call。
tools/call 直接调用 kernel.invoke()，与 CLI 走同一内核、同一审计日志。
"""

from __future__ import annotations

import json
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
            "serverInfo": {"name": "foxos", "title": "狐狸OS", "version": __version__},
            "instructions": "狐狸OS 命令内核。路径相对于工作空间；先调用 tools/list 了解参数与限制。",
        })
    if method == "ping":
        return _resp(id_, {})
    if method == "tools/list":
        return _resp(id_, {"tools": catalog.mcp_tools()})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        agent = state.get("agent") or (f"mcp:{state['client']}" if state.get("client") else "mcp")
        ctx = Context(state["ws"], agent=agent, task=state.get("task"), interface="mcp")
        try:
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


def serve(ws: Workspace, agent_default: str | None = None, task: str | None = None, stdin=None, stdout=None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    state = {"ws": ws, "agent": agent_default, "task": task}
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
