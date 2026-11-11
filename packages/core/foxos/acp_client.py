"""ACP（Agent Client Protocol）客户端，Python 版：CLI、MCP、聊天服务和操作系统里的「智能体」窗口共用。

以子进程启动智能体（Claude Code、Codex、Gemini CLI 或注册表里的任何 ACP 智能体），stdio 上逐行 JSON-RPC 2.0。
狐狸OS 是客户端，向智能体提供：
- fs/read_text_file、fs/write_text_file：经 foxos 内核（files read / files write），受工作空间约束、
  该智能体的工作范围（scope）、写锁、人工接管与审计约束；
- terminal/*：在工作范围内运行命令，人工接管时拒绝，每条命令写审计；
- session/request_permission：交给界面的审批卡片（或按智能体的审批规则自动回答）。
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from . import __version__, audit
from .errors import FoxError
from .i18n import tr

PROTOCOL_VERSION = 1


class AcpError(Exception):
    def __init__(self, message: str, code: int | None = None, data: Any = None):
        super().__init__(message)
        self.code = code
        self.data = data


class _Terminal:
    def __init__(self, proc: subprocess.Popen, limit: int):
        self.proc = proc
        self.limit = limit
        self.out = b""
        self.truncated = False
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._pump, daemon=True)
        self.t.start()

    def _pump(self):
        for chunk in iter(lambda: self.proc.stdout.read1(65536) if hasattr(self.proc.stdout, "read1") else self.proc.stdout.read(4096), b""):
            with self.lock:
                self.out += chunk
                if self.limit and len(self.out) > self.limit:
                    self.out = self.out[-self.limit:]
                    self.truncated = True

    def output(self) -> dict:
        with self.lock:
            text = self.out.decode("utf-8", "replace")
        st = None
        if self.proc.poll() is not None:
            self.t.join(timeout=2)
            with self.lock:
                text = self.out.decode("utf-8", "replace")
            st = {"exitCode": self.proc.returncode if self.proc.returncode >= 0 else None,
                  "signal": None if self.proc.returncode >= 0 else str(-self.proc.returncode)}
        return {"output": text, "truncated": self.truncated, **({"exitStatus": st} if st else {})}


class AcpConnection:
    """一个 ACP 智能体进程。回调：
    on_event(dict)：session/update、stderr、fs、terminal 事件（给聊天界面画卡片）
    on_permission(params) -> optionId | None：审批（阻塞直到人或规则回答）
    call(command_id, params) -> dict：执行 foxos 命令（本机内核或远程机器），fs 读写走它
    """

    def __init__(self, command: str, args: list[str] | None = None, env: dict | None = None, *, identity: str,
                 workspace: Path, scope: str = ".", on_event: Callable[[dict], None] | None = None,
                 on_permission: Callable[[dict], str | None] | None = None,
                 call: Callable[[str, dict], dict] | None = None, paused: Callable[[], dict | None] | None = None,
                 readonly_roots: list | None = None):
        self.command = command
        self.args = list(args or [])
        self.env = dict(env or {})
        self.identity = identity
        self.workspace = Path(workspace).resolve()
        self.scope = (scope or ".").strip("/") or "."
        self.scope_root = (self.workspace / self.scope).resolve()
        self.on_event = on_event or (lambda e: None)
        self.on_permission = on_permission or (lambda p: None)
        self.call = call
        self.paused = paused or (lambda: None)
        # 工作空间以外允许只读的目录（技能目录：pstack 与用户技能），读到时发 skill 事件
        self.readonly_roots = [Path(os.path.realpath(r)) for r in (readonly_roots or [])]
        self.next_id = 1
        self.pending: dict[int, dict] = {}
        self.lock = threading.Lock()
        self.stderr = ""
        self.closed = None
        self.init: dict | None = None
        self.terminals: dict[str, _Terminal] = {}
        self.proc: subprocess.Popen | None = None

    # ------------------------------------------------------------------ 进程
    def start(self) -> None:
        self.scope_root.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, **self.env, "FOXOS_WORKSPACE": str(self.workspace), "FOXOS_AGENT": self.identity}
        try:
            self.proc = subprocess.Popen([self.command, *self.args], cwd=str(self.scope_root), env=env,
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as e:
            raise FoxError("DEPENDENCY_MISSING", tr("acp.cannot_start_agent", self.command, e)) from e
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stderr(self):
        for line in iter(self.proc.stderr.readline, b""):
            s = line.decode("utf-8", "replace")
            self.stderr = (self.stderr + s)[-20000:]
            self.on_event({"type": "stderr", "text": s})

    def _read_stdout(self):
        for line in iter(self.proc.stdout.readline, b""):
            s = line.decode("utf-8", "replace").strip()
            if not s:
                continue
            try:
                msg = json.loads(s)
            except ValueError:
                self.on_event({"type": "stdout", "text": s})
                continue
            self._dispatch(msg)
        code = self.proc.wait()
        self._close(tr("acp.agent_exited", code))

    def _close(self, reason: str):
        with self.lock:
            if self.closed:
                return
            self.closed = reason
            pend = list(self.pending.values())
            self.pending.clear()
        for p in pend:
            p["error"] = AcpError(reason)
            p["event"].set()
        self.on_event({"type": "closed", "reason": reason})

    def stop(self):
        for t in list(self.terminals.values()):
            if t.proc.poll() is None:
                t.proc.kill()
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.close()
            except OSError:
                pass
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()

    # ------------------------------------------------------------------ JSON-RPC
    def _send(self, msg: dict):
        if self.closed:
            raise AcpError(tr("acp.connection_closed", self.closed))
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        with self.lock:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def request(self, method: str, params: dict, timeout: float = 120.0) -> Any:
        with self.lock:
            rid = self.next_id
            self.next_id += 1
            slot = {"event": threading.Event()}
            self.pending[rid] = slot
        self._send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        if not slot["event"].wait(timeout):
            with self.lock:
                self.pending.pop(rid, None)
            raise AcpError(tr("acp.timed_out", method))
        if "error" in slot:
            raise slot["error"]
        return slot.get("result")

    def notify(self, method: str, params: dict):
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _dispatch(self, msg: dict):
        if "method" not in msg and msg.get("id") is not None:
            with self.lock:
                slot = self.pending.pop(msg["id"], None)
            if slot is None:
                return
            if msg.get("error"):
                e = msg["error"]
                slot["error"] = AcpError(e.get("message") or "ACP error", e.get("code"), e.get("data"))
            else:
                slot["result"] = msg.get("result")
            slot["event"].set()
            return
        method = msg.get("method")
        if method == "session/update":
            p = msg.get("params") or {}
            self.on_event({"type": "update", "sessionId": p.get("sessionId"), "update": p.get("update") or {}})
            return
        if msg.get("id") is not None:
            threading.Thread(target=self._answer, args=(msg,), daemon=True).start()

    def _answer(self, msg: dict):
        try:
            result = self._handle(msg["method"], msg.get("params") or {})
            self._send({"jsonrpc": "2.0", "id": msg["id"], "result": result})
        except FoxError as e:
            self._send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32000, "message": e.message, "data": e.to_dict()}})
        except AcpError as e:
            self._send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": e.code or -32603, "message": str(e)}})
        except Exception as e:  # noqa: BLE001 — 回给智能体，不让它卡住
            self._send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32603, "message": f"{type(e).__name__}: {e}"}})

    # ------------------------------------------------------------------ 客户端能力
    def rel(self, p: str) -> str:
        """智能体给的绝对路径 → 工作空间相对路径；超出该智能体的工作范围直接拒绝。"""
        s = str(p or "")
        path = Path(s) if os.path.isabs(s) else self.scope_root / s
        real = Path(os.path.realpath(path))
        try:
            real.relative_to(self.scope_root)
        except ValueError:
            raise FoxError("PERMISSION_DENIED", tr("acp.outside_scope", s, self.scope),
                           details={"path": s, "scope": self.scope}) from None
        return Path(os.path.relpath(real, self.workspace)).as_posix()

    def _handle(self, method: str, params: dict) -> Any:
        if method == "session/request_permission":
            self.on_event({"type": "permission", "params": params})
            if self.paused():
                opt = next((o["optionId"] for o in params.get("options", []) if str(o.get("kind", "")).startswith("reject")), None)
            else:
                opt = self.on_permission(params)
            self.on_event({"type": "permission_answer", "toolCallId": (params.get("toolCall") or {}).get("toolCallId"), "optionId": opt})
            return {"outcome": {"outcome": "selected", "optionId": opt}} if opt else {"outcome": {"outcome": "cancelled"}}
        if method == "fs/read_text_file":
            real = Path(os.path.realpath(str(params.get("path") or "")))
            for root in self.readonly_roots:
                try:
                    real.relative_to(root)
                except ValueError:
                    continue
                if not real.is_file():
                    raise FoxError("NOT_FOUND", tr("acp.no_such_file", str(real)))
                self.on_event({"type": "fs", "op": "read", "path": str(real), "readonly": True})
                return {"content": real.read_text(encoding="utf-8")}
            rel = self.rel(params.get("path"))
            r = self.call("files.read", {"path": rel})
            content = r.get("content", "")
            if params.get("line") or params.get("limit"):
                lines = content.split("\n")
                start = max(0, int(params.get("line") or 1) - 1)
                end = start + int(params["limit"]) if params.get("limit") else None
                content = "\n".join(lines[start:end])
            self.on_event({"type": "fs", "op": "read", "path": rel, "abs": str(self.workspace / rel)})
            return {"content": content}
        if method == "fs/write_text_file":
            rel = self.rel(params.get("path"))
            old = None
            try:
                old = self.call("files.read", {"path": rel}).get("content")
            except FoxError:
                pass
            self.call("files.write", {"path": rel, "content": params.get("content") or ""})
            self.on_event({"type": "fs", "op": "write", "path": rel, "old": old, "new": params.get("content") or ""})
            return None
        if method == "terminal/create":
            return self._terminal_create(params)
        if method == "terminal/output":
            return self._term(params).output()
        if method == "terminal/wait_for_exit":
            t = self._term(params)
            t.proc.wait()
            t.t.join(timeout=2)
            o = t.output()
            self.on_event({"type": "terminal", "terminalId": params.get("terminalId"), "output": o})
            return o.get("exitStatus") or {"exitCode": t.proc.returncode, "signal": None}
        if method == "terminal/kill":
            t = self._term(params)
            if t.proc.poll() is None:
                t.proc.kill()
            return None
        if method == "terminal/release":
            t = self.terminals.pop(params.get("terminalId"), None)
            if t and t.proc.poll() is None:
                t.proc.kill()
            return None
        raise AcpError(tr("acp.method_not_supported", method), -32601)

    def _term(self, params) -> _Terminal:
        t = self.terminals.get(params.get("terminalId"))
        if not t:
            raise AcpError(tr("acp.no_such_terminal", params.get("terminalId")), -32602)
        return t

    def _terminal_create(self, params: dict) -> dict:
        st = self.paused()
        cmd = [str(params.get("command") or "")] + [str(a) for a in (params.get("args") or [])]
        cwd = params.get("cwd") or str(self.scope_root)
        rec = {"agent": self.identity, "interface": "acp", "command": "acp.terminal", "permission": "run",
               "args": {"argv": cmd, "cwd": cwd}}
        try:
            if st:
                raise FoxError("PAUSED", tr("kernel.human_takeover_is_active_agent", st.get("by", "?")))
            rel_cwd = self.rel(cwd)
            env = {**os.environ, **{e["name"]: e["value"] for e in params.get("env") or [] if "name" in e}}
            shell = len(cmd) == 1 and any(c in cmd[0] for c in " |&;<>$")
            proc = subprocess.Popen(cmd[0] if shell else cmd, shell=shell, cwd=str(self.workspace / rel_cwd), env=env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FoxError as e:
            rec.update(status="denied" if e.code in ("PAUSED", "PERMISSION_DENIED") else "error", error={"code": e.code, "message": e.message})
            audit.append_safe(self.workspace, rec)
            raise
        tid = "term-" + uuid.uuid4().hex[:10]
        self.terminals[tid] = _Terminal(proc, int(params.get("outputByteLimit") or 1_000_000))
        rec.update(status="ok", targets=[{"path": rel_cwd, "access": "run"}])
        audit.append_safe(self.workspace, rec)
        self.on_event({"type": "terminal_start", "terminalId": tid, "command": " ".join(cmd), "cwd": rel_cwd})
        return {"terminalId": tid}

    # ------------------------------------------------------------------ ACP 方法
    def initialize(self, timeout: float = 60.0) -> dict:
        self.init = self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "clientCapabilities": {"fs": {"readTextFile": True, "writeTextFile": True}, "terminal": True},
            "clientInfo": {"name": "foxos", "title": tr("common.foxos"), "version": __version__},
        }, timeout)
        return self.init

    def authenticate(self, method_id: str, timeout: float = 300.0):
        return self.request("authenticate", {"methodId": method_id}, timeout)

    def new_session(self, mcp_servers: list | None = None, timeout: float = 120.0) -> dict:
        return self.request("session/new", {"cwd": str(self.scope_root), "mcpServers": mcp_servers or []}, timeout)

    def configure_session(self, session: dict, model: str | None = None, mode: str | None = None, timeout: float = 30.0) -> dict:
        """按设置切换会话的模型与模式（ACP session/set_model、session/set_mode）。
        只在智能体在 session/new 里报告了可选项时才发；智能体不支持或拒绝时记下原因，不中断回合。"""
        out: dict = {}
        sid = session.get("sessionId")
        models = (session.get("models") or {}).get("availableModels") or []
        modes = (session.get("modes") or {}).get("availableModes") or []
        # 新版 ACP：会话配置项（configOptions，category=model/mode），用 session/set_config_option 设置（opencode 等）
        opts = {o.get("category") or o.get("id"): o for o in (session.get("configOptions") or []) if isinstance(o, dict)}
        for cat, want in (("model", model), ("mode", mode)):
            o = opts.get(cat)
            if not want or not o:
                continue
            values = [v.get("value") for v in o.get("options") or []]
            if values and want not in values:
                out[cat] = {"ok": False, "error": f"unknown {cat}", "available": values}
            else:
                try:
                    self.request("session/set_config_option", {"sessionId": sid, "configId": o["id"], "value": want}, timeout)
                    out[cat] = {"ok": True, "id": want}
                except AcpError as e:
                    out[cat] = {"ok": False, "error": str(e)}
            if cat == "model":
                model = None
            else:
                mode = None
        if model:
            if models and not any(m.get("modelId") == model for m in models):
                out["model"] = {"ok": False, "error": "unknown model", "available": [m.get("modelId") for m in models]}
            else:
                try:
                    self.request("session/set_model", {"sessionId": sid, "modelId": model}, timeout)
                    out["model"] = {"ok": True, "id": model}
                except AcpError as e:
                    out["model"] = {"ok": False, "error": str(e)}
        if mode:
            if modes and not any(m.get("id") == mode for m in modes):
                out["mode"] = {"ok": False, "error": "unknown mode", "available": [m.get("id") for m in modes]}
            else:
                try:
                    self.request("session/set_mode", {"sessionId": sid, "modeId": mode}, timeout)
                    out["mode"] = {"ok": True, "id": mode}
                except AcpError as e:
                    out["mode"] = {"ok": False, "error": str(e)}
        return out

    def prompt(self, session_id: str, blocks: list[dict], timeout: float = 3600.0) -> dict:
        return self.request("session/prompt", {"sessionId": session_id, "prompt": blocks}, timeout)

    def cancel(self, session_id: str):
        try:
            self.notify("session/cancel", {"sessionId": session_id})
        except AcpError:
            pass


def foxos_mcp_server(workspace: Path, identity: str, extra_env: dict | None = None) -> dict:
    """session/new 里交给智能体的 foxos MCP 服务器（stdio）。"""
    import sys
    core = str(Path(__file__).resolve().parents[1])
    env = {"PYTHONPATH": core, "FOXOS_AGENT": identity, "PYTHONIOENCODING": "utf-8", **(extra_env or {})}
    if os.environ.get("FOXOS_HOME"):
        env["FOXOS_HOME"] = os.environ["FOXOS_HOME"]
    from .i18n import get_lang
    env["FOXOS_LANG"] = get_lang()
    return {"name": "foxos", "command": sys.executable, "args": ["-m", "foxos", "--workspace", str(workspace), "mcp"],
            "env": [{"name": k, "value": v} for k, v in env.items()]}
