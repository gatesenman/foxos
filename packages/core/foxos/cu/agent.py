"""System 1 / System 2 电脑操控智能体（`foxos computer task` / `foxos browser task` 的默认做法）。

  观察（agent-desktop / CDP 无障碍快照）→ 观察编译器 → System 1 单步策略（Jev；没密钥自动回退 DeepSeek JSON）
  → 置信度分级：高 → 直接执行；中 → 执行后核对（状态是否变化 / 输入的文字是否到位）；低或连续失败 → 交给 System 2
  System 2 规划器（DeepSeek v4 pro，思考模式）：开始时把任务拆成带成功检查的子目标；升级时用完整观察亲自走一步
  （工具调用，可改计划）；卡住时重新规划；最后核对任务是否完成并给出答案。
删除、发送、支付、提交、安装等破坏性动作不论置信度都要人批准（智能体审批卡片）；人工接管时暂停。
每一步的延迟、置信度、是否升级、是否成功写进任务日志和审计日志（command = computer.step / browser.step）。
"""

from __future__ import annotations

import json
import re
import time

from .. import audit
from ..errors import FoxError
from ..i18n import get_lang, tr
from . import llm
from .loop import Loop, browser_tools, computer_tools
from .policy import ACTIONS, Observation, active_policy, observation

READ_TOOLS = ("read_text", "read", "observe_app")
DESTRUCTIVE_RE = re.compile(r"(delete|remove|erase|discard|send|submit|pay|purchase|buy|order|checkout|transfer|publish|post|install|"
                            r"uninstall|format|empty trash|sign ?out|log ?out|删除|移除|清空|发送|提交|支付|付款|购买|下单|结算|转账|发布|安装|卸载|退出登录)", re.I)

PLAN_SYS = ("You are the planner (System 2) of a computer-use agent on Linux (XFCE desktop or Chrome). Decompose the task into 1-8 short, "
            "concrete subgoals that a fast step policy can execute one UI action at a time. Reply with JSON only: "
            '{"subgoals": [{"goal": "...", "text": "exact text to type or option to select, or null", "check": "what is visible when done"}]}. '
            "Put any text that must be typed into `text` verbatim (the step policy cannot write text). Typing REPLACES the whole "
            "content of the target field, so to add to existing text put the complete desired final content in `text` "
            "(e.g. existing 'milk' plus a new line 'eggs' → text 'milk\\neggs'); do not plan caret movements. Do not include a final "
            "'report the answer' subgoal; answers are extracted at the end.")
VERIFY_SYS = ("You verify whether a computer-use task is complete, from the current UI observation. Reply with JSON only: "
              '{"complete": true|false, "answer": "final answer or extracted values, exact text with units, or a short summary", '
              '"missing": "what still needs to be done if not complete"}.')
STEP_SYS = ("You are the planner (System 2) of a computer-use agent. The fast step policy was not confident or failed. Look at the full "
            "observation and do the next step yourself with ONE tool call. Use set_plan to replace the remaining subgoals when the "
            "plan is wrong, subgoal_done as soon as the current subgoal is already satisfied (do not keep reading the page), and done "
            "(with the answer) only when the whole task is complete.")


class Agent(Loop):
    def __init__(self, ctx, kind: str, task: str, *, policy: str = "auto", high: float | None = None, low: float | None = None,
                 surface: str = "auto", **kw):
        super().__init__(ctx, kind, task, **kw)
        self.surface_pref = surface if kind == "computer" else "dom"
        self.surface = "dom" if kind == "browser" else ("screen" if surface == "screen" else "a11y")
        self.routes: list[dict] = []
        gate = self.cfg.get("gate") or {}
        self.high = float(high if high is not None else gate.get("high", 0.85))
        self.low = float(low if low is not None else gate.get("low", 0.55))
        self.policy = active_policy(self.cfg, policy)
        self.subgoals: list[dict] = []
        self.sg = 0
        self.history: list[dict] = []
        self.telemetry: list[dict] = []
        self.s2_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        self.s1_usage: dict = {}
        self._last_nodes: list = []
        self._s2_read: str | None = None
        self._title = None
        self._url = None

    # ------------------------------------------------------------ 观察
    def compile(self) -> Observation:
        if self.kind == "computer" and self.surface_pref == "screen":
            return self.compile_screen()
        text, png = self.observe()
        self._last_obs = text
        self._png = png
        if self.kind == "browser":
            m = re.search(r"^URL: (.*)$", text, re.M)
            t = re.search(r"^Title: (.*)$", text, re.M)
            self._url, self._title = (m.group(1) if m else None), (t.group(1) if t else None)
        obs = observation(self.kind, self._title, self._url, text, self._last_nodes, self.task)
        if self.kind == "browser":
            obs.surface = "dom"
        elif not obs.candidates and self.surface_pref == "auto":
            # 路由：没有无障碍信息（快照失败 / 0 个可操作元素）→ 截图视觉
            return self.compile_screen(text, reason="no accessible elements")
        self._set_surface("a11y" if self.kind == "computer" else "dom", None)
        return obs

    def _set_surface(self, surface: str, reason: str | None) -> None:
        if surface != self.surface or not self.routes:
            self.routes.append({"surface": surface, "reason": reason})
            self.event({"type": "route", "surface": surface, "reason": reason})
        self.surface = surface

    def screenshot(self) -> bytes:
        import tempfile
        from pathlib import Path
        from ..session import get_backend
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "s.png"
            try:
                get_backend(self.ctx.workspace).screenshot(f)
            except (subprocess.TimeoutExpired, OSError) as e:  # 负载高时 scrot 会超时：转成可重试的观察错误
                raise FoxError("ERROR", f"screenshot: {e}") from e
            return f.read_bytes()

    def _observe(self) -> Observation:
        """观察一次；失败（截图 / agent-desktop 超时）时记事件并重试一次。"""
        try:
            return self.compile()
        except FoxError as e:
            if e.code == "PAUSED":
                raise
            self.event({"type": "observe_error", "error": e.message[:300]})
            time.sleep(1.0)
            return self.compile()

    def compile_screen(self, a11y_text: str | None = None, reason: str | None = "surface=screen") -> Observation:
        """screen 面：只有截图（给 Jev / 视觉定位）；给规划器的文字只有窗口列表和标题。"""
        self._set_surface("screen", reason)
        wins = self.run_cmd("desktop.windows", {})
        wl = [w for w in wins.get("windows", [])]
        self._title = next((w.get("title") for w in wl if w.get("active")), None)
        text = "Windows:\n" + ("\n".join(f"- window {w.get('id')} \"{w.get('title')}\"" + (" [active]" if w.get("active") else "")
                                        for w in wl) or "(none)")
        text += "\n\n(screen mode: no accessibility info — act by visual description: click_visual, type_keys, key)"
        self._last_obs = text
        self._png = png = self.screenshot()
        return Observation("computer", self._title, None, [], (self._title or "")[:200], text, 0, surface="screen", png=png)

    # ------------------------------------------------------------ System 2
    def _s2(self, messages, tools=None, json_mode=False, timeout=240):
        extra = {"response_format": {"type": "json_object"}} if json_mode else None
        r = llm.chat(messages, tools, cfg=self.cfg, timeout=timeout, extra=extra)
        for k in self.s2_usage:
            self.s2_usage[k] += int((r.get("usage") or {}).get(k) or 0)
        return r

    @staticmethod
    def _json(text: str) -> dict:
        m = re.search(r"\{.*\}", text or "", re.S)
        try:
            return json.loads(m.group(0)) if m else {}
        except ValueError:
            return {}

    def plan(self, obs: Observation, note: str | None = None) -> None:
        t0 = time.time()
        user = f"Task: {self.task}\n\nCurrent observation:\n{obs.full[:12000]}"
        if note:
            user += f"\n\nReplanning because: {note}\nDone so far: {json.dumps(self.history[-8:], ensure_ascii=False)}"
        r = self._s2([{"role": "system", "content": PLAN_SYS + " " + tr("cu.sys_lang", get_lang())}, {"role": "user", "content": user}],
                     json_mode=True)
        sgs = [s for s in (self._json(r["message"].get("content")).get("subgoals") or []) if isinstance(s, dict) and s.get("goal")]
        self.subgoals = sgs[:8] or [{"goal": self.task, "text": None, "check": None}]
        self.sg = 0
        self.event({"type": "plan", "subgoals": self.subgoals, "seconds": round(time.time() - t0, 2), "replan": bool(note)})

    def page_text(self) -> str:
        """浏览器：快照只有元素，核对答案时再带上网页正文（信息框、段落里的文字）。"""
        if self.kind != "browser":
            return ""
        try:
            t = self.run_cmd("browser.text", {"tab": self.tab, "max_chars": 12000} if self.tab else {"max_chars": 12000})
            return "\n\nPage text:\n" + str(t.get("text") or "")[:12000]
        except FoxError:
            return ""

    def verify(self, obs: Observation) -> dict:
        if obs.surface == "screen" and self.policy.name == "typesafe":
            return self.verify_screen(obs)
        r = self._s2([{"role": "system", "content": VERIFY_SYS + " " + tr("cu.sys_lang", get_lang())},
                      {"role": "user", "content": f"Task: {self.task}\nActions so far: {json.dumps(self.history[-10:], ensure_ascii=False)}\n\n"
                                                  f"Current observation:\n{obs.full[:12000]}{self.page_text()}"}], json_mode=True)
        d = self._json(r["message"].get("content"))
        self.event({"type": "verify", **{k: d.get(k) for k in ("complete", "answer", "missing")}})
        return d

    def verify_screen(self, obs: Observation) -> dict:
        """规划器（DeepSeek）看不到截图：screen 面的完成检查交给 Jev（Noul，截图 + 任务 + 已做的动作）。"""
        import uuid
        ts = self.policy.ts
        ph = "img-" + uuid.uuid4().hex
        st = {"task": self.task, "actions_so_far": self.history[-10:], "subgoal_checks": [s.get("check") for s in self.subgoals],
              "screenshot": ph}
        r = self.policy.client.ask(st, {"complete": ts.noul("Looking at the screenshot, is the task fully complete?")},
                                   assets={ph: ts.image_asset(obs.png)})
        p = float(r["answers"]["complete"]["noul"])
        d = {"complete": p >= 0.7, "answer": None, "missing": None if p >= 0.7 else f"screen check says not complete (p={p:.2f})",
             "p": round(p, 3), "by": "typesafe"}
        self.event({"type": "verify", **d})
        return d

    def s2_step(self, obs: Observation, reason: str) -> dict:
        """升级：规划器看完整观察，亲自做一步（或改计划 / 标记子目标完成 / 结束）。"""
        tools = (browser_tools() if self.kind == "browser" else computer_tools(self.vision or obs.surface == "screen")) + [
            {"type": "function", "function": {"name": "set_plan", "description": "Replace the remaining subgoals.",
                                              "parameters": {"type": "object", "properties": {"subgoals": {"type": "array", "items": {
                                                  "type": "object", "properties": {"goal": {"type": "string"}, "text": {"type": "string"},
                                                                                   "target": {"type": "string"},
                                                                                   "check": {"type": "string"}}, "required": ["goal"]}}},
                                                             "required": ["subgoals"]}}},
            {"type": "function", "function": {"name": "subgoal_done", "description": "The current subgoal is already satisfied.",
                                              "parameters": {"type": "object", "properties": {}}}}]
        sg = self.subgoals[self.sg] if self.sg < len(self.subgoals) else {}
        user = (f"Task: {self.task}\nPlan: {json.dumps(self.subgoals, ensure_ascii=False)}\nCurrent subgoal #{self.sg + 1}: "
                f"{json.dumps(sg, ensure_ascii=False)}\nWhy you are called: {reason}\nRecent actions: "
                f"{json.dumps(self.history[-6:], ensure_ascii=False)}\n\nObservation:\n{obs.full[:16000]}")
        if self._s2_read:  # 规划器每次调用是无状态的：把上一次读到的内容带回去，避免反复读
            user += f"\n\nYour previous read returned:\n{self._s2_read[:6000]}\nUse it: call done with the answer if it answers the task, " \
                    "or subgoal_done / set_plan if the plan is out of date. Do not read the same thing again."
        content = [{"type": "text", "text": user}]
        if self._png is not None and self.vision and obs.surface != "screen":
            content.append(llm.image_part(self._png))
        r = self._s2([{"role": "system", "content": STEP_SYS + " " + tr("cu.sys_lang", get_lang())},
                      {"role": "user", "content": content if len(content) > 1 else user}], tools)
        calls = r["message"].get("tool_calls") or []
        if not calls:
            return {"tool": None, "ok": False, "note": (r["message"].get("content") or "")[:200]}
        c = calls[0]
        name = c["function"]["name"]
        try:
            args = json.loads(c["function"].get("arguments") or "{}")
        except ValueError:
            args = {}
        if name == "set_plan":
            self.subgoals = self.subgoals[:self.sg] + [s for s in args.get("subgoals") or [] if isinstance(s, dict) and s.get("goal")]
            self.event({"type": "plan", "subgoals": self.subgoals, "replan": True, "by": "s2"})
            return {"tool": name, "ok": True}
        if name == "subgoal_done":
            self.sg += 1
            return {"tool": name, "ok": True}
        if name == "done":
            return {"tool": "done", "ok": True, "answer": args.get("answer"), "success": bool(args.get("success", True))}
        out = self.execute(name, args)
        self._s2_read = out.pop("full", None) if name in READ_TOOLS and out.get("ok") else None
        return {"tool": name, "args": args, **out}

    # ------------------------------------------------------------ 执行
    def is_risky(self, name: str, args: dict) -> bool:
        if name == "launch":
            return True
        vals = " ".join(str(v) for k, v in args.items() if k in ("text", "keys", "key", "description", "value", "url"))
        label = self._label(args.get("ref")) if args.get("ref") else ""
        if name in ("type", "set_text") and "password" in label.lower():
            return True
        ctx = (self._title or "") if name in ("click", "key", "press") else ""
        return bool(DESTRUCTIVE_RE.search(label + " " + vals)) or (name in ("key", "press") and bool(DESTRUCTIVE_RE.search(ctx)) and
                                                                     str(args.get("keys") or args.get("key")).lower() in ("return", "enter"))

    def execute(self, name: str, args: dict) -> dict:
        t0 = time.time()
        if not self.approved(name, args):
            return {"ok": False, "error": tr("cu.denied"), "denied": True, "ms": 0}
        try:
            res = self.act(name, args)
            out = {"ok": True, "result": self._short(res)[:400], "ms": round((time.time() - t0) * 1000)}
            if name in READ_TOOLS:
                out["full"] = self._short(res)
            return out
        except FoxError as e:
            if e.code == "PAUSED":
                self.wait_if_paused()
            return {"ok": False, "error": e.message, "code": e.code, "ms": round((time.time() - t0) * 1000)}

    def to_tool(self, d, sg: dict, obs: Observation) -> tuple[str, dict] | None:
        if obs.surface == "screen":
            if d.action in ("click", "type") and not d.point:
                return None
            if d.action == "click":
                return "click_point", {"x": d.point[0], "y": d.point[1], "description": d.target}
            if d.action == "type":
                return ("type_at", {"x": d.point[0], "y": d.point[1], "text": sg["text"], "description": d.target}) if sg.get("text") else None
            if d.action == "key":
                return "key_x", {"keys": d.key}
            if d.action == "scroll":
                return "key_x", {"keys": "page_down"}
            if d.action == "wait":
                return "wait", {"seconds": 1.5}
            return None
        b = self.kind == "browser"
        if d.action == "click":
            return "click", {"ref": d.target}
        if d.action == "type":
            if not sg.get("text"):
                return None
            return ("type", {"ref": d.target, "text": sg["text"]}) if b else ("set_text", {"ref": d.target, "text": sg["text"]})
        if d.action == "select":
            return ("select", {"ref": d.target, "value": sg.get("text") or ""}) if sg.get("text") else None
        if d.action == "key":
            return ("press", {"key": d.key}) if b else ("key", {"keys": d.key})
        if d.action == "scroll":
            if b:
                return "scroll", {"direction": "down"}
            tgt = d.target or next((c.id for c in obs.candidates if c.role in ("scrollarea", "scrollpane", "scroll pane")), None)
            return ("scroll", {"ref": tgt, "direction": "down"}) if tgt else ("key", {"keys": "page_down"})
        if d.action == "wait":
            return "wait", {"seconds": 1.5}
        return None

    def act(self, name: str, a: dict) -> dict:
        """screen 面的三个动作：坐标点击、点击后键盘输入（先全选，替换内容）、xdotool 按键。"""
        if name == "click_point":
            return self.run_cmd("desktop.click", {"x": int(a["x"]), "y": int(a["y"])})
        if name == "type_at":
            self.run_cmd("desktop.click", {"x": int(a["x"]), "y": int(a["y"])})
            time.sleep(0.2)
            self.run_cmd("desktop.key", {"keys": "ctrl+a"})
            return self.run_cmd("desktop.type", {"text": a.get("text", "")})
        if name == "key_x":
            return self.run_cmd("desktop.key", {"keys": a.get("keys", "")})
        if name == "key" and self.surface == "screen":
            return self.run_cmd("desktop.key", {"keys": a.get("keys", "")})
        return super().act(name, a)

    def verified(self, before: Observation, tool: str, args: dict) -> bool:
        time.sleep(0.4)
        try:
            after = self.compile()
        except FoxError as e:
            if e.code == "PAUSED":
                raise
            self.event({"type": "observe_error", "error": e.message[:300]})
            self._pending = None
            return False
        self._pending = after
        if tool in ("set_text", "type"):
            c = after.by_id(args.get("ref")) if self.kind == "computer" else None
            if c is not None and c.value is not None:
                return args.get("text", "")[:40] in c.value
        return after.fingerprint() != before.fingerprint()

    def telemetry_rec(self, rec: dict) -> None:
        self.telemetry.append(rec)
        self.event({"type": "step", **rec})
        audit.append_safe(self.ctx.workspace, {"agent": self.ctx.agent, "interface": getattr(self.ctx, "interface", "cli"),
                                               "command": f"{self.kind}.step", "status": "ok" if rec.get("ok") else "error",
                                               "params": {"task": self.id, **{k: rec.get(k) for k in (
                                                   "step", "tier", "action", "target", "confidence", "gate", "policy_ms", "exec_ms",
                                                   "escalated", "verified", "provider")}}})

    # ------------------------------------------------------------ 主循环
    def run(self) -> dict:
        t0 = time.time()
        self.event({"type": "start", "kind": self.kind, "task_text": self.task, "mode": "s1s2", "policy": self.policy.name,
                    "surface": self.surface_pref,
                    "planner": self.cfg["model"], "agent": self.ctx.agent, "gate": [self.low, self.high]})
        answer, success, status = None, False, "max_steps"
        fails = 0
        stall = 0
        self._pending = None
        obs = self._observe()
        self.plan(obs)
        for step in range(1, self.max_steps + 1):
            if not self.wait_if_paused():
                status = "paused"
                break
            try:
                obs = self._pending or self.compile()
            except FoxError as e:
                if e.code == "PAUSED":
                    continue
                self.event({"type": "observe_error", "error": e.message[:300]})
                time.sleep(1.0)
                try:
                    obs = self._observe()
                except FoxError as e2:
                    answer, status = f"observation failed: {e2.message}", "error"
                    break
            self._pending = None
            if self.sg >= len(self.subgoals):
                v = self.verify(obs)
                if v.get("complete"):
                    answer, success, status = v.get("answer"), True, "done"
                    break
                self.plan(obs, note=v.get("missing") or "verification failed")
                continue
            sg = self.subgoals[self.sg]
            rec = {"step": step, "subgoal": self.sg + 1, "candidates": len(obs.candidates), "candidates_total": obs.total}
            try:
                d = self.policy.decide(obs, self.task, sg, self.history)
            except FoxError as e:
                d = None
                rec["policy_error"] = e.message[:200]
            if d is not None:
                for k, v in (d.usage or {}).items():
                    if isinstance(v, (int, float)):
                        self.s1_usage[k] = self.s1_usage.get(k, 0) + v
                rec.update(provider=d.provider, action=d.action, target=d.target, key=d.key, confidence=round(d.confidence, 3),
                           policy_ms=round(d.seconds * 1000))
            mapped = self.to_tool(d, sg, obs) if d is not None and d.action not in ("done", "escalate") else None
            reason = None
            if d is None:
                reason = "step policy error"
            elif d.action == "escalate":
                reason = "step policy escalated" + (f" ({d.note})" if d.note else "")
            elif d.action == "done":
                if d.confidence >= self.low:
                    rec.update(tier="s1", gate="high" if d.confidence >= self.high else "medium", ok=True)
                    self.history.append({"subgoal": sg.get("goal"), "action": "done"})
                    self.sg += 1
                    self.telemetry_rec(rec)
                    continue
                reason = f"low confidence done ({d.confidence:.2f})"
            elif d.confidence < self.low:
                reason = f"low confidence {d.confidence:.2f}"
            elif fails >= 2:
                reason = f"{fails} consecutive failures"
            elif mapped is None:
                reason = f"cannot map {d.action} (missing text or target)"
            if reason is None:
                gate = "high" if d.confidence >= self.high else "medium"
                tool, args = mapped
                out = self.execute(tool, args)
                ok = out["ok"]
                ver = None
                if ok and gate == "medium" and tool not in ("wait",):
                    ver = self.verified(obs, tool, args)
                    ok = ver
                fails = 0 if ok else fails + 1
                self.history.append({"subgoal": sg.get("goal"), "action": tool, "args": {k: v for k, v in args.items() if k != "text"},
                                     "ok": ok, "error": out.get("error")})
                rec.update(tier="s1", gate=gate, tool=tool, ok=ok, verified=ver, exec_ms=out.get("ms"), escalated=False,
                           error=out.get("error"))
                self.steps.append({"step": step, "tool": tool, "args": args, "ok": ok, "tier": "s1"})
                self.telemetry_rec(rec)
                continue
            # ---- 升级到 System 2
            t1 = time.time()
            out = self.s2_step(obs, reason)
            rec.update(tier="s2", escalated=True, reason=reason, s2_tool=out.get("tool"), ok=bool(out.get("ok")),
                       s2_ms=round((time.time() - t1) * 1000), error=out.get("error"))
            self.telemetry_rec(rec)
            if out.get("tool") == "done":
                v = self.verify(self.compile())
                answer = v.get("answer") or out.get("answer")
                success, status = bool(v.get("complete", out.get("success"))), "done"
                break
            if out.get("tool") not in (None, "set_plan", "subgoal_done"):
                self.steps.append({"step": step, "tool": out["tool"], "args": out.get("args"), "ok": out.get("ok"), "tier": "s2"})
                self.history.append({"subgoal": sg.get("goal"), "action": out["tool"], "by": "planner", "ok": out.get("ok"),
                                     "error": out.get("error")})
            fails = 0 if out.get("ok") else fails + 1
            stall = stall + 1 if not out.get("ok") else 0
            if stall >= 3:
                self.plan(self.compile(), note="stalled: planner steps keep failing")
                stall = 0
        tel = self.telemetry
        res = {"task_id": self.id, "status": status, "success": bool(success and status == "done"), "answer": answer, "mode": "s1s2",
               "surface": self.surface, "routes": self.routes,
               "policy": self.policy.name, "planner": self.cfg["model"], "steps": len(tel), "actions": self.steps,
               "subgoals": self.subgoals, "seconds": round(time.time() - t0, 1),
               "s1_steps": sum(1 for t in tel if t.get("tier") == "s1"), "escalations": sum(1 for t in tel if t.get("escalated")),
               "mean_confidence": round(sum(t.get("confidence") or 0 for t in tel) / max(1, len(tel)), 3),
               "mean_policy_ms": round(sum(t.get("policy_ms") or 0 for t in tel) / max(1, len(tel))),
               "usage": {"planner": self.s2_usage, "step_policy": self.s1_usage}, "log": self.ctx.rel(self.log)}
        if self.kind == "browser":
            res["tab"] = self.tab
        self.event({"type": "end", "status": status, "success": res["success"]})
        return res


BROWSER_HINT = re.compile(r"(https?://|www\.|\.(com|org|net|io|cn)\b|website|web page|webpage|browser|chrome|google|search the web|"
                          r"网页|网站|浏览器|搜索一下|上网)", re.I)


BROWSER_APPS = ("chrome", "google-chrome", "chromium", "chromium-browser", "browser", "firefox")


def needs_browser_fallback(ctx, task: str, app: str | None = None, url: str | None = None) -> str | None:
    """默认走 agent-desktop + Jev。只有目标是网页、而 agent-desktop 读不到网页内容时，才退到 browser use。
    返回退路的原因；None = 留在默认路径。"""
    web = bool(url) or (app or "").lower() in BROWSER_APPS or (not app and bool(BROWSER_HINT.search(task or "")))
    if not web:
        return None
    from . import agent_desktop
    try:
        apps = [str(a.get("name") or "").lower() for a in agent_desktop.apps()]
    except Exception as e:  # noqa: BLE001  agent-desktop 不可用 → 网页只能走浏览器
        return f"agent-desktop unavailable ({str(e)[:80]})"
    names = [a for a in apps if any(b in a for b in BROWSER_APPS)]
    if not names:
        return "no browser exposed to the accessibility tree"
    try:
        snap = agent_desktop.snapshot(ctx.workspace, app=names[0], interactive=True)
    except Exception as e:  # noqa: BLE001
        return f"browser snapshot failed ({str(e)[:80]})"
    roles = {str(n.get("role") or "").lower() for n in snap.get("nodes") or []}
    if not roles & {"link", "document", "document web", "heading", "entry", "textfield"}:
        return "web content not exposed to the accessibility tree"
    return None


def known_actions() -> list[str]:
    return list(ACTIONS)
