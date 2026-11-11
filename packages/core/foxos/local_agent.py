"""狐狸OS 本地智能体：一个真正的 ACP 智能体进程（stdio JSON-RPC），不调用任何模型，行为是确定的。

用途：没有模型密钥时也能完整使用「智能体」聊天（委托、技能、读写文件、终端、审批、跨机器操作），
也是端到端测试里的真实 ACP 进程。它像其他 ACP 智能体一样只通过 ACP 客户端能力（fs/*、terminal/*、
session/request_permission）和 session/new 交给它的 foxos MCP 服务器做事，因此受同样的工作空间约束、
写锁、审计和人工接管约束。

一行一条指令（中英文都可）：
  /技能名 [任务]                        读 SKILL.md，按它的章节列出计划
  write <路径>: <内容> | 写入 <路径>：<内容>   先请求批准，再写文件（显示 diff）
  run <命令> | 运行 <命令>                 在工作范围内运行命令（显示终端输出）
  @<智能体> <任务> | delegate <智能体>: <任务> | 委托 <智能体>：<任务>
  remember <内容> | 记住 <内容>
  on <机器>: list [目录] | 在 <机器> 上列出 [目录]
  read <路径> | 读取 <路径>
  use <连接器> <工具> {JSON 参数} | 使用 <连接器> <工具> {…}   经 foxos MCP 调用连接器工具（按智能体授权与审批）
其它文字：复述收到的上下文（身份、可委托的智能体、技能数）。

用法：python3 -m foxos.local_agent
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import uuid

PROTOCOL_VERSION = 1
NAME = "foxos-local"
_zh = (os.environ.get("FOXOS_LANG") or "zh-CN").lower().startswith("zh")


def T(zh: str, en: str) -> str:
    return zh if _zh else en


class Rpc:
    def __init__(self):
        self.lock = threading.Lock()
        self.next = 1
        self.pending: dict[int, dict] = {}

    def send(self, msg: dict):
        with self.lock:
            sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
            sys.stdout.flush()

    def request(self, method: str, params: dict):
        with self.lock:
            rid = self.next
            self.next += 1
            slot = {"ev": threading.Event()}
            self.pending[rid] = slot
        self.send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        slot["ev"].wait()
        if "error" in slot:
            raise RuntimeError(slot["error"].get("message", "error"))
        return slot.get("result")

    def resolve(self, msg: dict):
        slot = self.pending.pop(msg.get("id"), None)
        if slot is None:
            return
        if msg.get("error"):
            slot["error"] = msg["error"]
        else:
            slot["result"] = msg.get("result")
        slot["ev"].set()


class Mcp:
    """连 session/new 给的 stdio MCP 服务器（foxos）。"""

    def __init__(self, spec: dict):
        env = {**os.environ, **{e["name"]: e["value"] for e in spec.get("env") or []}}
        self.p = subprocess.Popen([spec["command"], *spec.get("args", [])], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, env=env, text=True, encoding="utf-8")
        self.n = 0
        self._call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": NAME, "version": "1"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.p.stdin.flush()

    def _call(self, method, params):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}, ensure_ascii=False) + "\n")
        self.p.stdin.flush()
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("MCP server exited")
            m = json.loads(line)
            if m.get("id") == self.n:
                if m.get("error"):
                    raise RuntimeError(m["error"].get("message"))
                return m["result"]

    def tool(self, name: str, args: dict) -> dict:
        r = self._call("tools/call", {"name": name, "arguments": args})
        return r.get("structuredContent") or json.loads(r["content"][0]["text"])


class Agent:
    def __init__(self):
        self.rpc = Rpc()
        self.sessions: dict[str, dict] = {}

    def update(self, sid: str, upd: dict):
        self.rpc.send({"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": sid, "update": upd}})

    def say(self, sid: str, text: str):
        # 分段发送，界面上是流式的
        for piece in re.findall(r".{1,24}", text, flags=re.S) or [text]:
            self.update(sid, {"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": piece}})

    def tool(self, sid: str, kind: str, title: str, raw: dict | None = None) -> str:
        tid = "call_" + uuid.uuid4().hex[:8]
        self.update(sid, {"sessionUpdate": "tool_call", "toolCallId": tid, "title": title, "kind": kind, "status": "in_progress",
                          **({"rawInput": raw} if raw else {})})
        return tid

    def done(self, sid: str, tid: str, ok: bool, content: list | None = None, raw_out: dict | None = None):
        self.update(sid, {"sessionUpdate": "tool_call_update", "toolCallId": tid, "status": "completed" if ok else "failed",
                          **({"content": content} if content else {}), **({"rawOutput": raw_out} if raw_out else {})})

    # -------------------------------------------------------------- 协议
    def handle(self, msg: dict):
        m, p, rid = msg.get("method"), msg.get("params") or {}, msg.get("id")
        if m is None:
            self.rpc.resolve(msg)
            return
        try:
            if m == "initialize":
                res = {"protocolVersion": PROTOCOL_VERSION,
                       "agentCapabilities": {"loadSession": False, "promptCapabilities": {"image": False, "audio": False, "embeddedContext": True},
                                             "mcpCapabilities": {"http": False, "sse": False}},
                       "agentInfo": {"name": NAME, "title": T("狐狸OS 本地智能体", "FoxOS local agent"), "version": "1.0.0"},
                       "authMethods": []}
                self.caps = p.get("clientCapabilities") or {}
            elif m == "session/new":
                sid = "sess_" + uuid.uuid4().hex[:10]
                mcp = next((s for s in p.get("mcpServers") or [] if s.get("name") == "foxos" and s.get("command")), None)
                self.sessions[sid] = {"cwd": p.get("cwd"), "mcp_spec": mcp, "mcp": None}
                res = {"sessionId": sid}
                self.update(sid, {"sessionUpdate": "available_commands_update", "availableCommands": []})
            elif m == "session/prompt":
                res = self.prompt(p["sessionId"], p.get("prompt") or [])
            elif m == "session/cancel":
                return
            elif m == "authenticate":
                res = {}
            else:
                raise RuntimeError(f"method not found: {m}")
            if rid is not None:
                self.rpc.send({"jsonrpc": "2.0", "id": rid, "result": res})
        except Exception as e:  # noqa: BLE001
            if rid is not None:
                self.rpc.send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32603, "message": str(e)}})

    def mcp(self, sid: str) -> Mcp:
        s = self.sessions[sid]
        if s["mcp"] is None:
            if not s["mcp_spec"]:
                raise RuntimeError(T("没有 foxos MCP 服务器", "no foxos MCP server was provided"))
            s["mcp"] = Mcp(s["mcp_spec"])
        return s["mcp"]

    # -------------------------------------------------------------- 回合
    def prompt(self, sid: str, blocks: list) -> dict:
        text = "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        ctx = {}
        mctx = re.search(r"<foxos-context>(.*?)</foxos-context>", text, re.S)
        if mctx:
            try:
                ctx = json.loads(mctx.group(1))
            except ValueError:
                ctx = {}
        user = re.sub(r"<foxos-context>.*?</foxos-context>", "", text, flags=re.S)
        user = re.sub(r"<foxos-skill[^>]*>.*?</foxos-skill>", "", user, flags=re.S)
        links = [b for b in blocks if b.get("type") in ("resource_link", "resource")]
        lines = [ln.strip() for ln in user.strip().splitlines() if ln.strip()]
        did = False
        for ln in lines:
            did = self.step(sid, ln, ctx) or did
        for b in links:
            uri = b.get("uri") or (b.get("resource") or {}).get("uri", "")
            self.say(sid, T(f"收到附件：{b.get('name') or uri}\n", f"Got attachment: {b.get('name') or uri}\n"))
            did = True
        if not did:
            me = ctx.get("bot", {})
            others = ", ".join("@" + b["name"] for b in ctx.get("bots", []) if not b.get("self"))
            self.say(sid, T(f"我是 {me.get('name', '本地智能体')}（{me.get('title') or '狐狸OS 本地智能体'}）。收到：{user.strip()[:200]}\n"
                            f"可委托：{others or '无'}；技能 {len(ctx.get('skills', []))} 个；记忆 {len(ctx.get('memory', []))} 条；默认机器 {ctx.get('machine', 'local')}。\n",
                            f"I am {me.get('name', 'the local agent')} ({me.get('title') or 'FoxOS local agent'}). Received: {user.strip()[:200]}\n"
                            f"Can delegate to: {others or 'none'}; {len(ctx.get('skills', []))} skills; {len(ctx.get('memory', []))} memories; default machine {ctx.get('machine', 'local')}.\n"))
        return {"stopReason": "end_turn"}

    def step(self, sid: str, ln: str, ctx: dict) -> bool:
        cwd = self.sessions[sid]["cwd"]
        m = re.match(r"^/([a-z0-9][a-z0-9-]*)\s*(.*)$", ln)
        if m:
            name, task = m.group(1), m.group(2)
            sk = next((s for s in ctx.get("skills", []) if s["name"] == name), None)
            if not sk:
                self.say(sid, T(f"没有技能 /{name}\n", f"No skill /{name}\n"))
                return True
            tid = self.tool(sid, "read", T(f"读取技能 {name}", f"Read skill {name}"), {"path": sk["path"]})
            body = self.rpc.request("fs/read_text_file", {"sessionId": sid, "path": sk["path"]})["content"]
            self.done(sid, tid, True)
            heads = [h.strip("# ").strip() for h in body.splitlines() if h.startswith("## ")][:8]
            self.update(sid, {"sessionUpdate": "plan", "entries": [{"content": h, "priority": "medium", "status": "pending"} for h in heads]})
            self.say(sid, T(f"按 /{name} 技能处理「{task or '当前任务'}」，共 {len(heads)} 个阶段：{'、'.join(heads)}\n",
                            f"Following /{name} for \"{task or 'the task'}\": {len(heads)} phases: {', '.join(heads)}\n"))
            return True
        m = re.match(r"^(?:write|写入)\s+(\S+?)\s*[:：]\s*(.*)$", ln, re.S)
        if m:
            path, content = m.group(1), m.group(2).replace("\\n", "\n")
            abspath = path if os.path.isabs(path) else os.path.join(cwd, path)
            tid = "call_" + uuid.uuid4().hex[:8]
            old = None
            try:
                old = self.rpc.request("fs/read_text_file", {"sessionId": sid, "path": abspath})["content"]
            except RuntimeError:
                pass
            diff = [{"type": "diff", "path": abspath, "oldText": old, "newText": content}]
            self.update(sid, {"sessionUpdate": "tool_call", "toolCallId": tid, "title": T(f"写入 {path}", f"Write {path}"), "kind": "edit",
                              "status": "pending", "locations": [{"path": abspath}], "content": diff, "rawInput": {"path": path}})
            r = self.rpc.request("session/request_permission", {"sessionId": sid, "toolCall": {"toolCallId": tid, "title": T(f"写入 {path}", f"Write {path}"), "kind": "edit"},
                                 "options": [{"optionId": "allow", "name": T("允许", "Allow"), "kind": "allow_once"},
                                             {"optionId": "allow-always", "name": T("总是允许", "Always allow"), "kind": "allow_always"},
                                             {"optionId": "reject", "name": T("拒绝", "Reject"), "kind": "reject_once"}]})
            out = (r or {}).get("outcome") or {}
            if out.get("outcome") != "selected" or str(out.get("optionId", "")).startswith("reject"):
                self.done(sid, tid, False)
                self.say(sid, T(f"没有写入 {path}（未获批准）。\n", f"Did not write {path} (not approved).\n"))
                return True
            try:
                self.rpc.request("fs/write_text_file", {"sessionId": sid, "path": abspath, "content": content})
                self.done(sid, tid, True, diff)
                self.say(sid, T(f"已写入 {path}。\n", f"Wrote {path}.\n"))
            except RuntimeError as e:
                self.done(sid, tid, False, [{"type": "content", "content": {"type": "text", "text": str(e)}}])
                self.say(sid, T(f"写入 {path} 失败：{e}\n", f"Writing {path} failed: {e}\n"))
            return True
        m = re.match(r"^(?:read|读取)\s+(\S+)$", ln)
        if m:
            path = m.group(1)
            tid = self.tool(sid, "read", T(f"读取 {path}", f"Read {path}"), {"path": path})
            try:
                c = self.rpc.request("fs/read_text_file", {"sessionId": sid, "path": path if os.path.isabs(path) else os.path.join(cwd, path)})["content"]
                self.done(sid, tid, True, [{"type": "content", "content": {"type": "text", "text": c[:2000]}}])
                self.say(sid, T(f"{path} 有 {len(c.splitlines())} 行。\n", f"{path} has {len(c.splitlines())} lines.\n"))
            except RuntimeError as e:
                self.done(sid, tid, False)
                self.say(sid, T(f"读取失败：{e}\n", f"Read failed: {e}\n"))
            return True
        m = re.match(r"^(?:run|运行)\s+(.+)$", ln)
        if m:
            cmd = m.group(1)
            tid = self.tool(sid, "execute", cmd, {"command": cmd})
            try:
                t = self.rpc.request("terminal/create", {"sessionId": sid, "command": "/bin/sh", "args": ["-c", cmd], "cwd": cwd})["terminalId"]
                self.update(sid, {"sessionUpdate": "tool_call_update", "toolCallId": tid, "content": [{"type": "terminal", "terminalId": t}]})
                st = self.rpc.request("terminal/wait_for_exit", {"sessionId": sid, "terminalId": t})
                out = self.rpc.request("terminal/output", {"sessionId": sid, "terminalId": t})
                self.rpc.request("terminal/release", {"sessionId": sid, "terminalId": t})
                ok = (st or {}).get("exitCode") == 0
                self.done(sid, tid, ok, [{"type": "content", "content": {"type": "text", "text": out.get("output", "")}}],
                          {"exitCode": (st or {}).get("exitCode"), "output": out.get("output", "")})
                self.say(sid, T(f"命令结束，退出码 {(st or {}).get('exitCode')}。\n", f"Command finished with exit code {(st or {}).get('exitCode')}.\n"))
            except RuntimeError as e:
                self.done(sid, tid, False, [{"type": "content", "content": {"type": "text", "text": str(e)}}])
                self.say(sid, T(f"不能运行：{e}\n", f"Could not run: {e}\n"))
            return True
        m = (re.match(r"^@(\S+)\s+(.+)$", ln) or re.match(r"^(?:delegate|委托)\s+@?(\S+?)\s*[:：]\s*(.+)$", ln))
        if m:
            to, task = m.group(1), m.group(2)
            tid = self.tool(sid, "other", T(f"委托给 {to}", f"Delegate to {to}"), {"tool": "bot_task_delegate", "to": to, "task": task})
            try:
                r = self.mcp(sid).tool("bot_task_delegate", {"to": to, "task": task})
                if not r.get("ok"):
                    raise RuntimeError(r["error"]["message"])
                ans = r["result"].get("answer", "")
                self.done(sid, tid, True, [{"type": "content", "content": {"type": "text", "text": ans}}], r["result"])
                self.say(sid, T(f"{to} 回报：{ans.strip()}\n", f"{to} reports: {ans.strip()}\n"))
            except RuntimeError as e:
                self.done(sid, tid, False, [{"type": "content", "content": {"type": "text", "text": str(e)}}])
                self.say(sid, T(f"委托给 {to} 没有成功：{e}\n", f"Delegating to {to} failed: {e}\n"))
            return True
        m = re.match(r"^(?:use|使用)\s+([a-z0-9][a-z0-9_-]*)\s+([A-Za-z0-9_.-]+)\s*(\{.*\})?\s*$", ln, re.S)
        if m:
            cid, tool, raw = m.group(1), m.group(2), m.group(3)
            try:
                args = json.loads(raw) if raw else {}
            except ValueError:
                self.say(sid, T("参数不是 JSON 对象。\n", "Arguments are not a JSON object.\n"))
                return True
            tid = self.tool(sid, "fetch", T(f"连接器 {cid} · {tool}", f"Connector {cid} · {tool}"), {"tool": "connector_tool_call", "connector": cid, "name": tool})
            r = self.mcp(sid).tool("connector_tool_call", {"connector": cid, "tool": tool, "arguments": args})
            if r.get("ok"):
                res = r["result"]
                text = res.get("text") or "\n".join(c.get("text", "") for c in (res.get("content") or []) if c.get("type") == "text") \
                    or json.dumps(res, ensure_ascii=False)[:2000]
                self.done(sid, tid, not res.get("isError"), [{"type": "content", "content": {"type": "text", "text": text[:4000]}}], {"connector": cid})
                self.say(sid, T(f"{cid} · {tool} 返回：{text[:400]}\n", f"{cid} · {tool} returned: {text[:400]}\n"))
            else:
                self.done(sid, tid, False, [{"type": "content", "content": {"type": "text", "text": r["error"]["message"]}}])
                self.say(sid, T(f"{cid} · {tool}：{r['error']['message']}\n", f"{cid} · {tool}: {r['error']['message']}\n"))
            return True
        m = re.match(r"^(?:remember|记住)\s*[:：]?\s*(.+)$", ln)
        if m:
            tid = self.tool(sid, "other", T("写入记忆", "Save memory"), {"tool": "bot_memory_add"})
            r = self.mcp(sid).tool("bot_memory_add", {"bot": (ctx.get("bot") or {}).get("id", ""), "text": m.group(1)})
            self.done(sid, tid, bool(r.get("ok")))
            self.say(sid, T("记住了。\n", "Saved to memory.\n") if r.get("ok") else T(f"没能记住：{r['error']['message']}\n", f"Could not save: {r['error']['message']}\n"))
            return True
        m = re.match(r"^(?:on\s+(\S+?)\s*:\s*list|在\s*(\S+?)\s*上列出)\s*(\S*)$", ln)
        if m:
            machine, folder = m.group(1) or m.group(2), m.group(3) or "."
            tid = self.tool(sid, "search", T(f"在 {machine} 上列出 {folder}", f"List {folder} on {machine}"), {"tool": "files_list", "machine": machine, "path": folder})
            r = self.mcp(sid).tool("files_list", {"path": folder, "machine": machine})
            if r.get("ok"):
                names = [e.get("name") for e in r["result"].get("entries", [])]
                self.done(sid, tid, True, [{"type": "content", "content": {"type": "text", "text": "\n".join(names)}}], {"machine": machine})
                self.say(sid, T(f"{machine} 上 {folder} 有：{'、'.join(names) or '（空）'}\n", f"{folder} on {machine}: {', '.join(names) or '(empty)'}\n"))
            else:
                self.done(sid, tid, False, [{"type": "content", "content": {"type": "text", "text": r['error']['message']}}], {"machine": machine})
                self.say(sid, T(f"{machine}：{r['error']['message']}\n", f"{machine}: {r['error']['message']}\n"))
            return True
        return False


def main() -> int:
    a = Agent()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if msg.get("method") == "session/prompt":
            threading.Thread(target=a.handle, args=(msg,), daemon=True).start()
        else:
            a.handle(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
