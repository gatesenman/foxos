"""智能体循环：观察 → 模型 → 动作 → 再观察，直到模型调用 done。

- browser：观察 = 当前网页的无障碍快照（文字），纯文字模型（DeepSeek v4 pro）即可；配置了视觉模型时附截图
- computer：观察 = 窗口列表 + agent-desktop 的无障碍快照（AT-SPI）；配置了视觉模型时附截图，并可用视觉定位点击；
  没有无障碍信息的程序退回 xdotool 键盘输入（type_keys）与视觉定位点击（click_visual）
每个动作都经 foxos 内核执行（与 CLI / MCP 同一条路径）：写审计、受工作空间约束、人工接管时停下等待；
需要审批的动作（approve=ask 时所有改动，risky 时只有高风险动作）走智能体审批卡片（foxos bot approval answer）。
过程写在 .foxos/tasks/<任务id>.jsonl。

做法参考：browser-use 的 Agent（DOM/无障碍文字 + 可选截图）、Playwright MCP 的快照 + ref、Agent S3 / UI-TARS 的
观察-思考-动作循环、OSWorld 的「a11y tree」观察方式。
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

from ..errors import FoxError
from ..i18n import get_lang, tr
from ..kernel import Context, invoke, is_human, paused_for
from . import llm

RISKY_RE = re.compile(r"(delete|remove|erase|send|submit|pay|purchase|buy|order|checkout|confirm|transfer|publish|post|sign ?out|log ?out|"
                      r"删除|移除|发送|提交|支付|付款|购买|下单|结算|确认|转账|发布|退出登录)", re.I)


def _fn(name: str, desc: str, props: dict | None = None, required: list | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": desc,
                                             "parameters": {"type": "object", "properties": props or {}, "required": required or []}}}


DONE = _fn("done", "Finish the task. Put the final answer / extracted values in `answer` (exact text, units included).",
           {"answer": {"type": "string"}, "success": {"type": "boolean"}}, ["answer", "success"])


def browser_tools() -> list:
    s = {"type": "string"}
    return [
        _fn("navigate", "Open a URL in the current tab.", {"url": s}, ["url"]),
        _fn("click", "Click the element with this ref from the latest snapshot.", {"ref": s}, ["ref"]),
        _fn("type", "Focus a textbox/searchbox by ref, replace its text, optionally press Enter.",
            {"ref": s, "text": s, "submit": {"type": "boolean"}}, ["ref", "text"]),
        _fn("press", "Press a key in the page, e.g. Enter, Escape, ArrowDown, Tab, ctrl+a.", {"key": s}, ["key"]),
        _fn("select", "Choose an option of a <select> combobox by value or visible text.", {"ref": s, "value": s}, ["ref", "value"]),
        _fn("scroll", "Scroll the page.", {"direction": {"type": "string", "enum": ["down", "up"]}}, ["direction"]),
        _fn("back", "Go back in history."),
        _fn("read_text", "Read the visible text of the page (or of one element by ref) when the snapshot is not enough.", {"ref": s}),
        DONE,
    ]


def computer_tools(vision: bool) -> list:
    s = {"type": "string"}
    t = [
        _fn("launch", "Start a desktop program, e.g. ['mousepad', 'notes.txt'] or ['xfce4-terminal']. Paths are inside the workspace.",
            {"command": {"type": "array", "items": s}}, ["command"]),
        _fn("observe_app", "Show the accessibility snapshot of a specific application by name (default: all/focused app).", {"app": s}),
        _fn("click", "Click an element by ref from the latest snapshot (menus, buttons, menu items, tabs, check boxes).",
            {"ref": s}, ["ref"]),
        _fn("set_text", "Replace the text of an editable element (textfield, entry) by ref; append=true inserts at the caret instead.",
            {"ref": s, "text": s, "append": {"type": "boolean"}}, ["ref", "text"]),
        _fn("select", "Choose an option in a combo box / list by ref and visible text.", {"ref": s, "value": s}, ["ref", "value"]),
        _fn("scroll", "Scroll a scrollable element by ref.", {"ref": s, "direction": {"type": "string", "enum": ["up", "down"]}}, ["ref"]),
        _fn("read", "Read the full text of an element by ref.", {"ref": s}, ["ref"]),
        _fn("key", "Send a key combination to the focused app, e.g. ctrl+s, return, escape.", {"keys": s}, ["keys"]),
        _fn("type_keys", "Fallback for apps without accessibility: type literal text into the focused window via the keyboard.", {"text": s}, ["text"]),
        _fn("focus_window", "Focus a window by id from the window list.", {"window": s}, ["window"]),
        _fn("wait", "Wait a few seconds for the UI to update.", {"seconds": {"type": "number"}}, ["seconds"]),
        DONE,
    ]
    if vision:
        t.insert(-1, _fn("click_visual", "Click something without accessibility info, described in words (vision grounding).",
                         {"description": s}, ["description"]))
    return t


def system_prompt(kind: str, vision: bool) -> str:
    return tr("cu.sys_browser" if kind == "browser" else "cu.sys_computer") + (" " + tr("cu.sys_vision") if vision else "") + \
        " " + tr("cu.sys_lang", get_lang())


def workspace_argv(ctx: Context, argv: list) -> list[str]:
    """启动程序时，参数里的相对路径按工作空间解析（越界的路径照常被拒绝）。"""
    out = [str(a) for a in argv]
    for i, a in enumerate(out[1:], 1):
        if a.startswith("-") or "://" in a or a.startswith("/"):
            continue
        cand = ctx.workspace.root / a
        if cand.exists() or (cand.parent.exists() and "." in Path(a).name):
            out[i] = str(ctx.resolve(a))
    return out


class Loop:
    def __init__(self, ctx: Context, kind: str, task: str, *, max_steps: int = 25, approve: str = "risky", vision: str = "auto",
                 tab: str | None = None, app: str | None = None, on_event=None, takeover_wait: float = 900.0, cfg: dict | None = None):
        self.ctx, self.kind, self.task = ctx, kind, task
        self.cfg = cfg or llm.load()
        self.vision = llm.vision_enabled(self.cfg) if vision == "auto" else vision == "on"
        self.max_steps, self.approve, self.tab, self.app = int(max_steps), approve, tab, app
        self.on_event = on_event or (lambda e: None)
        self.takeover_wait = takeover_wait
        self.id = "task-" + uuid.uuid4().hex[:10]
        d = ctx.workspace.data_dir / "tasks"
        d.mkdir(parents=True, exist_ok=True)
        self.log = d / f"{self.id}.jsonl"
        self.steps: list[dict] = []
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0}

    # -------------------------------------------------------------- 记录
    def event(self, ev: dict) -> None:
        ev = {"t": round(time.time(), 3), "task": self.id, **ev}
        with open(self.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        try:
            self.on_event(ev)
        except Exception:  # noqa: BLE001
            pass

    def run_cmd(self, cid: str, params: dict) -> dict:
        return invoke(cid, params, self.ctx)

    # -------------------------------------------------------------- 观察
    def observe(self) -> tuple[str, bytes | None]:
        if self.kind == "browser":
            s = self.run_cmd("browser.snapshot", {"tab": self.tab, "max_chars": 24000} if self.tab else {"max_chars": 24000})
            self.tab = s.get("tab") or self.tab
            text = f"URL: {s.get('url')}\nTitle: {s.get('title')}\n" + (s.get("snapshot") or "(empty page)") + \
                ("\n…(snapshot truncated; use scroll or read_text)" if s.get("truncated") else "")
            png = None
            if self.vision:
                try:
                    from . import cdp
                    p, ws = cdp.connect(self.ctx, self.tab)
                    try:
                        import base64
                        png = base64.b64decode(ws.call("Page.captureScreenshot", {"format": "png"}).get("data") or b"")
                    finally:
                        ws.close()
                except FoxError:
                    png = None
            return text, png
        wins = self.run_cmd("desktop.windows", {})
        wl = "\n".join(f"- window {w.get('id')} \"{w.get('title')}\"" + (" [active]" if w.get("active") else "") for w in wins.get("windows", []))
        try:
            tr_ = self.run_cmd("desktop.tree", {"app": self.app, "full": True} if self.app else {"full": True})
        except FoxError as e:
            if e.code == "PAUSED":
                raise
            tr_ = {"snapshot": f"(accessibility snapshot failed: {e.message}; use type_keys / key / click_visual)", "nodes": []}
        self._last_nodes = tr_.get("nodes") or []
        self._title = next((w.get("title") for w in wins.get("windows", []) if w.get("active")), None)
        text = "Windows:\n" + (wl or "(none)") + "\n\nAccessibility snapshot (agent-desktop):\n" + (tr_.get("snapshot") or "(no accessible app)")
        png = None
        if self.vision:
            import tempfile
            from ..session import get_backend
            with tempfile.TemporaryDirectory() as td:
                f = Path(td) / "s.png"
                try:
                    get_backend(self.ctx.workspace).screenshot(f)
                    png = f.read_bytes()
                except FoxError:
                    png = None
        return text, png

    # -------------------------------------------------------------- 接管与审批
    def wait_if_paused(self) -> bool:
        st = paused_for(self.ctx.workspace, self.ctx.agent)
        if not st:
            return True
        self.event({"type": "paused", "by": st.get("by"), "reason": st.get("reason")})
        deadline = time.time() + self.takeover_wait
        while time.time() < deadline:
            time.sleep(1.0)
            if not paused_for(self.ctx.workspace, self.ctx.agent):
                self.event({"type": "resumed"})
                return True
        return False

    def is_risky(self, name: str, args: dict) -> bool:
        """高风险：启动程序；或者动作目标 / 输入文字里有删除、发送、支付、提交、购买等字样；或者往密码框里输入。"""
        if name == "launch":
            return True
        vals = " ".join(str(v) for k, v in args.items() if k in ("text", "keys", "description", "value", "url"))
        label = self._label(args.get("ref")) if args.get("ref") else ""
        if name in ("type", "set_text") and "password" in label.lower():
            return True
        if name in ("click", "click_visual", "press", "key", "select", "type", "set_text", "type_keys"):
            return bool(RISKY_RE.search(label + " " + vals))
        return False

    def _label(self, ref) -> str:
        try:
            for line in (self._last_obs or "").splitlines():
                if f"[ref={ref}]" in line:
                    return line.strip()
        except (FoxError, AttributeError):
            pass
        return ""

    def approved(self, name: str, args: dict) -> bool:
        mutating = name not in ("read_text", "read", "observe_app", "wait", "scroll", "done", "back")
        need = (self.approve == "ask" and mutating) or (self.approve == "risky" and self.is_risky(name, args))
        if not need or is_human(self.ctx.agent):
            return True
        if self.approve == "deny":
            return False
        from .. import bots
        agent = str(self.ctx.agent)
        bid = agent.split("/")[0][4:] if agent.startswith("bot:") else None
        try:
            bot = bots.get(self.ctx.workspace, bid) if bid else None
        except FoxError:
            bot = None
        bot = bot or {"id": bid or "computer", "name": bid or tr("cu.task_title")}
        title = f"{self.kind} · {name} " + json.dumps(args, ensure_ascii=False)[:160] + (f" — {self._label(args['ref'])}" if args.get("ref") else "")
        tc = {"toolCallId": f"{self.id}-{len(self.steps)}", "title": title, "kind": "execute" if name == "launch" else "edit",
              "rawInput": {"tool": name, "args": args, "task": self.task}}
        opts = [{"optionId": "allow", "name": tr("cu.allow"), "kind": "allow_once"}, {"optionId": "deny", "name": tr("cu.deny"), "kind": "reject_once"}]
        import os
        self.event({"type": "approval", "tool": name, "args": args})
        turn = os.environ.get("FOXOS_BOT_TURN") if bot.get("main") is not None else None
        opt = bots.ask_file(self.ctx.workspace, bot, tc, opts, turn=turn)
        self.event({"type": "approval_answer", "tool": name, "option": opt})
        return opt == "allow"

    # -------------------------------------------------------------- 动作
    def act(self, name: str, a: dict) -> dict:
        t = self.tab
        if self.kind == "browser":
            m = {"navigate": ("browser.navigate", {"url": a.get("url"), "tab": t}),
                 "click": ("browser.click", {"ref": a.get("ref"), "tab": t}),
                 "type": ("browser.type", {"ref": a.get("ref"), "text": a.get("text", ""), "submit": bool(a.get("submit")), "tab": t}),
                 "press": ("browser.press", {"key": a.get("key"), "tab": t}),
                 "select": ("browser.select", {"ref": a.get("ref"), "value": a.get("value"), "tab": t}),
                 "scroll": ("browser.scroll", {"direction": a.get("direction", "down"), "tab": t}),
                 "back": ("browser.back", {"tab": t}),
                 "read_text": ("browser.text", {"ref": a.get("ref"), "tab": t, "max_chars": 12000})}
        else:
            m = {"launch": ("desktop.launch", {"command": workspace_argv(self.ctx, a.get("command") or [])}),
                 "observe_app": ("desktop.tree", {"app": a.get("app")}),
                 "click": ("desktop.element.click", {"ref": a.get("ref")}),
                 "set_text": ("desktop.element.set-text", {"ref": a.get("ref"), "text": a.get("text", ""), "append": bool(a.get("append"))}),
                 "select": ("desktop.element.select", {"ref": a.get("ref"), "value": a.get("value", "")}),
                 "scroll": ("desktop.element.scroll", {"ref": a.get("ref"), "direction": a.get("direction", "down")}),
                 "read": ("desktop.element.read", {"ref": a.get("ref")}),
                 "type_keys": ("desktop.type", {"text": a.get("text", "")}),
                 "key": ("desktop.press", {"keys": a.get("keys", "")}),
                 "focus_window": ("desktop.focus", {"window": str(a.get("window", ""))}),
                 "click_visual": ("desktop.ground", {"description": a.get("description", ""), "click": True})}
            if name == "wait":
                time.sleep(min(float(a.get("seconds") or 1), 30))
                return {"waited": a.get("seconds")}
            if name == "observe_app" and a.get("app"):
                self.app = a["app"]
        if name not in m:
            raise FoxError("USAGE", f"unknown tool {name}")
        cid, params = m[name]
        params = {k: v for k, v in params.items() if v is not None}
        r = self.run_cmd(cid, params)
        if name == "launch":
            time.sleep(2.0)
        return r

    @staticmethod
    def _short(r: dict) -> str:
        r = {k: v for k, v in (r or {}).items() if k not in ("nodes",)}
        s = json.dumps(r, ensure_ascii=False)
        return s if len(s) < 6000 else s[:6000] + "…"

    # -------------------------------------------------------------- 主循环
    def run(self) -> dict:
        tools = browser_tools() if self.kind == "browser" else computer_tools(self.vision)
        msgs: list[dict] = [{"role": "system", "content": system_prompt(self.kind, self.vision)},
                            {"role": "user", "content": tr("cu.task_intro", self.task)}]
        self.event({"type": "start", "kind": self.kind, "task_text": self.task, "model": self.cfg["model"],
                    "vision_model": self.cfg.get("vision_model") if self.vision else None, "agent": self.ctx.agent})
        answer, success, status = None, False, "max_steps"
        obs_idx: list[int] = []
        nudged = False
        self._last_obs = ""
        t0 = time.time()
        for step in range(1, self.max_steps + 1):
            if not self.wait_if_paused():
                status = "paused"
                break
            try:
                text, png = self.observe()
            except FoxError as e:
                if e.code == "PAUSED":
                    if self.wait_if_paused():
                        continue
                    status = "paused"
                    break
                text, png = f"(observation failed: {e.message})", None
            self._last_obs = text
            for i in obs_idx:  # 旧的观察只留一行，省 token
                msgs[i] = {"role": "user", "content": "(earlier observation omitted)"}
            content = [{"type": "text", "text": f"Step {step} observation:\n{text}"}]
            if png and self.vision:
                content.append(llm.image_part(png))
            msgs.append({"role": "user", "content": content if len(content) > 1 else content[0]["text"]})
            obs_idx.append(len(msgs) - 1)
            r = llm.chat(msgs, tools, vision=bool(png and self.vision), cfg=self.cfg)
            for k in self.usage:
                self.usage[k] += int((r.get("usage") or {}).get(k) or 0)
            msg = r["message"]
            msgs.append(llm.assistant_for_history(msg))
            if msg.get("content"):
                self.event({"type": "thought", "text": msg["content"][:2000]})
            calls = msg.get("tool_calls") or []
            if not calls:
                if nudged:
                    answer, success, status = msg.get("content"), True, "done"
                    break
                nudged = True
                msgs.append({"role": "user", "content": tr("cu.nudge")})
                continue
            finished = False
            for c in calls:
                name = c["function"]["name"]
                try:
                    args = json.loads(c["function"].get("arguments") or "{}")
                except ValueError:
                    args = {}
                rec = {"step": step, "tool": name, "args": args}
                if name == "done":
                    answer, success, status = args.get("answer"), bool(args.get("success", True)), "done"
                    msgs.append({"role": "tool", "tool_call_id": c["id"], "content": "ok"})
                    self.steps.append(rec)
                    self.event({"type": "done", "answer": answer, "success": success})
                    finished = True
                    continue
                if finished:
                    msgs.append({"role": "tool", "tool_call_id": c["id"], "content": "skipped"})
                    continue
                if not self.approved(name, args):
                    out = {"ok": False, "error": tr("cu.denied")}
                else:
                    try:
                        out = {"ok": True, "result": self.act(name, args)}
                    except FoxError as e:
                        out = {"ok": False, "error": e.message, "code": e.code}
                        if e.code == "PAUSED":
                            self.wait_if_paused()
                rec["ok"] = out["ok"]
                rec["result"] = self._short(out.get("result") or {"error": out.get("error")})[:600]
                self.steps.append(rec)
                self.event({"type": "action", **rec})
                msgs.append({"role": "tool", "tool_call_id": c["id"], "content": self._short(out)})
            if finished:
                break
        res = {"task_id": self.id, "status": status, "success": success and status == "done", "answer": answer,
               "steps": len(self.steps), "actions": self.steps, "model": self.cfg["model"],
               "vision": self.vision, "seconds": round(time.time() - t0, 1), "usage": self.usage, "log": self.ctx.rel(self.log)}
        if self.kind == "browser":
            res["tab"] = self.tab
        self.event({"type": "end", "status": status, "success": res["success"]})
        return res
