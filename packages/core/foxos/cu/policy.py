"""System 1 / System 2 电脑操控的「快决策」部分：观察编译器 + 可插拔的单步策略。

观察编译器：把 agent-desktop 的无障碍快照（桌面）或 CDP 无障碍快照（网页）变成紧凑的编号元素表
（id、角色、名字/文字、状态、边框、可操作标志），加上目标、当前子目标、最近 N 个动作及结果、窗口/网页标题。
最多 255 个候选（Jev Choice 的上限）；超过时先按角色 / 可见性 / 与目标的词重叠预筛，Jev 用两段式打分。

单步策略返回有类型的决定：{action ∈ click/type/key/scroll/select/wait/done/escalate, target, key, confidence}
- JevPolicy      TypeSafe Jev（System One，托管 API）：一次请求并行问 action / target / key 三个 Choice，带校准过的置信度
- DeepSeekPolicy 没有 TypeSafe 密钥时的自动回退：deepseek-flash 关闭思考 + JSON 模式 + logprobs，
                 置信度 = 所选 action、target 取值那几个 token 的概率乘积（不是模型自己报的数）
System 1 不生成文字：要输入的文字由 System 2 规划器写在子目标里（text 字段）。
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass, field

from ..errors import FoxError
from . import llm

MAX_CANDIDATES = 255
ACTIONS = {
    "click": "Click / activate the target element (button, menu, menu item, link, tab, check box, list item).",
    "type": "Enter the subgoal's text into the target editable element (text field, search box), replacing its content.",
    "key": "Press the key combination given by the `key` answer (e.g. Enter to submit, ctrl+s to save, Escape to close).",
    "scroll": "Scroll the target (or the page) to reveal more content.",
    "select": "Choose the subgoal's text as the option of the target combo box / list.",
    "wait": "The UI is still loading or animating; wait briefly.",
    "done": "The current subgoal is already accomplished in the current state.",
    "escalate": "None of the above is clearly right, or required information is missing; hand over to the planner.",
}
NEEDS_TARGET = {"click", "type", "select"}
KEYS = {
    "computer": {"return": "Enter / confirm", "escape": "Close menu or dialog", "tab": "Next field", "ctrl+s": "Save",
                 "ctrl+a": "Select all", "ctrl+f": "Find", "page_down": "Page down", "down": "Arrow down", "up": "Arrow up"},
    "browser": {"Enter": "Enter / submit", "Escape": "Close popup", "Tab": "Next field", "PageDown": "Page down",
                "ArrowDown": "Arrow down", "ArrowUp": "Arrow up", "ctrl+a": "Select all"},
}
INTERACTIVE_ROLES = {"button", "menuitem", "menu", "checkbox", "radiobutton", "textfield", "textarea", "combobox", "listitem", "tab",
                     "link", "slider", "spinbutton", "treeitem", "switch", "searchfield", "searchbox", "textbox", "togglebutton",
                     "menuitemcheckbox", "menuitemradio", "option", "cell", "entry", "pushbutton", "push button", "menu item",
                     "check box", "radio button", "page tab", "combo box", "text", "list item", "listbox"}
ROLE_PRIORITY = {"textfield": 3, "textbox": 3, "searchbox": 3, "searchfield": 3, "combobox": 3, "button": 2, "menuitem": 2, "menu": 2,
                 "link": 1, "tab": 1, "checkbox": 2, "radiobutton": 2, "option": 1, "listitem": 0}


@dataclass
class Candidate:
    id: str
    role: str
    name: str = ""
    value: str | None = None
    states: list = field(default_factory=list)
    bbox: dict | None = None
    actions: list = field(default_factory=list)

    def label(self) -> str:
        s = f"{self.role}"
        if self.name:
            s += f' "{self.name[:100]}"'
        if self.value:
            s += f" = {json.dumps(self.value[:80], ensure_ascii=False)}"
        st = [x for x in self.states if x not in ("offscreen",)]
        if st:
            s += " [" + ", ".join(st[:4]) + "]"
        return s


@dataclass
class Observation:
    kind: str
    title: str | None
    url: str | None
    candidates: list[Candidate]
    text: str          # 给 System 1 的短上下文（可见文字摘录）
    full: str          # 原始快照文字（给 System 2）
    total: int = 0     # 预筛前的候选数
    surface: str = "a11y"            # a11y（agent-desktop）/ dom（浏览器 CDP）/ screen（只有截图）
    png: bytes | None = None         # screen 面：当前截图

    def fingerprint(self) -> str:
        import hashlib
        h = hashlib.sha1((str(self.title) + str(self.url) + "|".join(c.label() for c in self.candidates) + self.text).encode())
        if self.png:
            h.update(self.png)
        return h.hexdigest()[:12]

    def by_id(self, cid: str) -> Candidate | None:
        return next((c for c in self.candidates if c.id == cid), None)


# ------------------------------------------------------------------ 观察编译器

def _words(s: str) -> set:
    return {w for w in re.findall(r"[\w\u4e00-\u9fff]+", (s or "").lower()) if len(w) > 1}


def prefilter(cands: list[Candidate], goal: str, cap: int = MAX_CANDIDATES) -> list[Candidate]:
    if len(cands) <= cap:
        return cands
    gw = _words(goal)
    scored = []
    for i, c in enumerate(cands):
        sc = 3 * len(gw & _words(c.name + " " + (c.value or ""))) + ROLE_PRIORITY.get(c.role, 0)
        if "focused" in c.states:
            sc += 3
        scored.append((sc, i))
    keep = {i for _, i in sorted(scored, key=lambda t: (-t[0], t[1]))[:cap]}
    return [c for i, c in enumerate(cands) if i in keep]


def compile_computer(nodes: list[dict], title: str | None, full: str) -> list[Candidate]:
    out = []
    for n in nodes:
        st = n.get("states") or []
        if not n.get("ref") or "offscreen" in st or "disabled" in st:
            continue
        role = (n.get("role") or "").lower()
        if not (n.get("actions") or role in INTERACTIVE_ROLES):
            continue
        if role in ("menu",) and not n.get("name"):
            continue  # 菜单栏容器本身
        val = n.get("value") if n.get("value") is not None else n.get("text")
        out.append(Candidate(n["ref"], role, n.get("name") or (n.get("description") or ""), None if val in (None, "") else str(val),
                             st, n.get("bounds"), n.get("actions") or []))
    return out


LINE_RE = re.compile(r'^\s*- (?P<role>[\w ]+?)(?: "(?P<name>(?:[^"\\]|\\.)*)")?(?P<props>(?: \[[^\]]*\])*)(?:: (?P<val>.*))?$')
REF_RE = re.compile(r"(?:^|,\s*)ref=(e\d+)")


def compile_browser(snapshot: str) -> tuple[list[Candidate], str]:
    cands, texts = [], []
    for ln in (snapshot or "").splitlines():
        m = LINE_RE.match(ln)
        refm = None
        if m:
            raw = [p.strip() for grp in re.findall(r"\[([^\]]*)\]", m.group("props") or "") for p in grp.split(",") if p.strip()]
            refm = next((p[4:] for p in raw if p.startswith("ref=")), None)
        if m and refm:
            name = m.group("name") or ""
            try:
                name = json.loads(f'"{name}"')
            except ValueError:
                pass
            val = m.group("val")
            if val:
                try:
                    val = json.loads(val)
                except ValueError:
                    pass
            props = [p for p in raw if not p.startswith("ref=")]
            role = m.group("role").strip()
            if "disabled" in props:
                continue
            if role in ("heading", "img", "paragraph", "region", "navigation", "main", "banner", "contentinfo", "list", "group",
                        "table", "row", "columnheader", "rowheader", "article", "complementary", "form", "search", "LabelText"):
                texts.append(f"{role}: {name}")
                if role not in ("img",):
                    continue
                continue
            cands.append(Candidate(refm, role, name, None if val in (None, "") else str(val), props))
        else:
            t = ln.strip()
            if m and m.group("role").strip() in ("heading", "paragraph", "StaticText", "text") and m.group("name"):
                texts.append(m.group("name"))
            elif t.startswith("- text:"):
                texts.append(t[7:].strip().strip('"'))
    return cands, "\n".join(texts)


def observation(kind: str, title: str | None, url: str | None, full: str, nodes: list | None, goal: str) -> Observation:
    if kind == "browser":
        cands, text = compile_browser(full)
    else:
        cands = compile_computer(nodes or [], title, full)
        text = "\n".join(f"{c.role} {c.name}: {c.value}" for c in cands if c.value)[:1500]
    total = len(cands)
    return Observation(kind, title, url, cands if total <= MAX_CANDIDATES * 4 else prefilter(cands, goal, MAX_CANDIDATES * 4),
                       text[:2500], full, total)


# ------------------------------------------------------------------ 决定

@dataclass
class Decision:
    action: str
    target: str | None = None
    key: str | None = None
    confidence: float = 0.0
    probs: dict = field(default_factory=dict)
    provider: str = ""
    model: str | None = None
    seconds: float = 0.0
    usage: dict = field(default_factory=dict)
    note: str | None = None
    point: tuple | None = None       # screen 面：要点的屏幕坐标（来自定位）

    def public(self) -> dict:
        return {"action": self.action, "target": self.target, "key": self.key, "point": self.point, "confidence": round(self.confidence, 3),
                "provider": self.provider, "model": self.model, "ms": round(self.seconds * 1000), "note": self.note}


def state_for(obs: Observation, goal: str, subgoal: dict, history: list[dict]) -> dict:
    return {"goal": goal, "current_subgoal": subgoal.get("goal"), "subgoal_text_to_enter": subgoal.get("text"),
            "subgoal_target": subgoal.get("target"), "subgoal_success_check": subgoal.get("check"),
            "window_or_page_title": obs.title, "url": obs.url, "recent_actions": history[-5:], "visible_text": obs.text[:1500]}


SCREEN_ACTIONS = {k: v for k, v in ACTIONS.items() if k != "select"}
SCREEN_ACTIONS["click"] = "Click the subgoal's target on the screenshot (button, menu, link, field)."
SCREEN_ACTIONS["type"] = "Click the subgoal's target text field and type the subgoal's text into it (replacing its content)."
SCREEN_ACTIONS["scroll"] = "Scroll down to reveal more content."


def screen_target(subgoal: dict) -> str:
    return str(subgoal.get("target") or subgoal.get("goal") or "")


def ground_point(obs: Observation, description: str, cfg: dict | None = None) -> dict:
    """screen 面的定位：grounding.ground（默认 auto：有 TypeSafe 密钥用 Jev Box，否则本地 UI-TARS，否则视觉模型）。"""
    from . import grounding
    return grounding.ground(obs.png, description, cfg)


class Policy:
    name = "base"

    def decide(self, obs: Observation, goal: str, subgoal: dict, history: list[dict]) -> Decision:  # pragma: no cover
        raise NotImplementedError


class JevPolicy(Policy):
    """TypeSafe Jev：一次请求三个 Choice（action / target / key），候选超过 255 时两段式（先分块各选、再在胜者里选）。"""
    name = "typesafe"

    def __init__(self, client=None, model: str | None = None):
        from . import typesafe
        self.ts = typesafe
        self.client = client or typesafe.Client(model=model)

    def _target_q(self, cands: list[Candidate]) -> dict:
        return self.ts.choice("Which element should the next action act on to make progress on the current subgoal?",
                              {c.id: c.label() for c in cands})

    def decide(self, obs, goal, subgoal, history):
        if obs.surface == "screen":
            return jev_screen(self, obs, goal, subgoal, history)
        t0 = time.time()
        state = state_for(obs, goal, subgoal, history)
        cands = obs.candidates
        qs = {"action": self.ts.choice("What is the single best next UI action for the current subgoal?", ACTIONS),
              "key": self.ts.choice("If the next action is a key press, which key combination?", KEYS[obs.kind])}
        chunks = [cands[i:i + MAX_CANDIDATES] for i in range(0, len(cands), MAX_CANDIDATES)] or [[]]
        if len(chunks) == 1 and chunks[0]:
            qs["target"] = self._target_q(chunks[0])
        elif len(chunks) > 1:
            for i, ch in enumerate(chunks):
                qs[f"target_{i}"] = self._target_q(ch)
        r = self.client.ask(state, qs)
        a = r["answers"]
        usage = dict(r.get("usage") or {})
        target, tconf = None, 1.0
        if "target" in a:
            target, tconf = a["target"]["choice"], float(a["target"].get("confidence") or 0)
        elif len(chunks) > 1:  # 第二段：每块前两名进决赛
            finalists = []
            for i in range(len(chunks)):
                pr = a[f"target_{i}"].get("probabilities") or {}
                finalists += sorted(pr, key=pr.get, reverse=True)[:2]
            fin = [c for c in cands if c.id in finalists][:MAX_CANDIDATES]
            r2 = self.client.ask(state, {"target": self._target_q(fin)})
            target, tconf = r2["answers"]["target"]["choice"], float(r2["answers"]["target"].get("confidence") or 0)
            for k, v in (r2.get("usage") or {}).items():
                usage[k] = usage.get(k, 0) + v
        act = a["action"]["choice"]
        conf = float(a["action"].get("confidence") or 0)
        if act in NEEDS_TARGET:
            conf = min(conf, tconf)
        if act == "key":
            conf = min(conf, float(a["key"].get("confidence") or 0))
        return Decision(act, target if act in NEEDS_TARGET or act == "scroll" else None, a["key"]["choice"] if act == "key" else None,
                        conf, {"action": a["action"].get("probabilities")}, "typesafe", r.get("model"), time.time() - t0, usage)


def jev_screen(policy: "JevPolicy", obs: Observation, goal: str, subgoal: dict, history: list[dict]) -> Decision:
    """screen 面：截图作为图片资源，一次请求同时问 action / key（Choice）和目标位置（Box）。"""
    import uuid
    from . import grounding
    t0 = time.time()
    ph = "img-" + uuid.uuid4().hex
    state = {**state_for(obs, goal, subgoal, history), "screenshot": ph}
    qs = {"action": policy.ts.choice("What is the single best next UI action for the current subgoal, looking at the screenshot?",
                                     SCREEN_ACTIONS),
          "key": policy.ts.choice("If the next action is a key press, which key combination?", KEYS["computer"])}
    desc = screen_target(subgoal)
    if desc:
        qs["target"] = policy.ts.box("Locate this UI element in the screenshot: " + desc)
    r = policy.client.ask(state, qs, assets={ph: policy.ts.image_asset(obs.png)})
    a = r["answers"]
    act = a["action"]["choice"]
    conf = float(a["action"].get("confidence") or 0)
    point = None
    if act in ("click", "type"):
        if "target" not in a:
            return Decision("escalate", provider="typesafe", model=r.get("model"), seconds=time.time() - t0, note="no target description")
        b = a["target"]["box"]
        w, h = grounding.png_size(obs.png)
        point = (round((b["left"] + b["right"]) / 2 * w), round((b["top"] + b["bottom"]) / 2 * h))
        conf = min(conf, float(a["target"].get("confidence") or 0))
    key = a["key"]["choice"] if act == "key" else None
    if key:
        conf = min(conf, float(a["key"].get("confidence") or 0))
    return Decision(act, desc if point else None, key, conf, {"action": a["action"].get("probabilities")}, "typesafe", r.get("model"),
                    time.time() - t0, dict(r.get("usage") or {}), point=point)


SYS_DS = ("You are the fast step policy of a computer-use agent. Given the goal, the current subgoal, the recent actions and a numbered "
          "list of UI elements, choose the single next UI action. Reply with JSON only: "
          '{"action": one of ' + json.dumps(list(ACTIONS)) + ', "target": element id or null, "key": key name or null}. '
          "Action meanings: " + json.dumps(ACTIONS) + " Never invent element ids. Text to type always comes from subgoal_text_to_enter; "
          "if typing is needed but it is empty, answer escalate.")


def _value_span_prob(content: str, logprobs: list | None, field_name: str) -> float | None:
    """content 里 "field": "value" 的 value 由哪些 token 组成 → 这些 token 概率之积。"""
    if not logprobs:
        return None
    m = re.search(r'"%s"\s*:\s*"?([^",}]*)' % re.escape(field_name), content)
    if not m:
        return None
    s, e = m.span(1)
    pos, lp = 0, 0.0
    hit = False
    for t in logprobs:
        tok = t.get("token") or ""
        a, b = pos, pos + len(tok)
        if b > s and a < e:
            lp += float(t.get("logprob") or 0)
            hit = True
        pos = b
    return math.exp(lp) if hit else None


class DeepSeekPolicy(Policy):
    """自动回退：deepseek-flash，关闭思考，JSON 模式，置信度来自 logprobs。"""
    name = "deepseek"

    def __init__(self, cfg: dict | None = None, model: str | None = None):
        self.cfg = cfg or llm.load()
        self.model = model or self.cfg.get("fast_model") or ("deepseek-flash" if self.cfg["provider"] == "deepseek" else self.cfg["model"])

    def decide(self, obs, goal, subgoal, history):
        if obs.surface == "screen":
            return self.decide_screen(obs, goal, subgoal, history)
        state = state_for(obs, goal, subgoal, history)
        cands = prefilter(obs.candidates, f"{goal} {subgoal.get('goal')} {subgoal.get('text') or ''}")
        listing = "\n".join(f"{c.id}: {c.label()}" for c in cands)
        user = json.dumps(state, ensure_ascii=False) + "\n\nElements:\n" + (listing or "(none)") + \
            "\n\nKeys allowed: " + ", ".join(KEYS[obs.kind])
        extra = {"response_format": {"type": "json_object"}, "logprobs": True, "top_logprobs": 2}
        if self.cfg["provider"] == "deepseek":
            extra["thinking"] = {"type": "disabled"}
        r = llm.chat([{"role": "system", "content": SYS_DS}, {"role": "user", "content": user}], cfg=self.cfg, model=self.model,
                     timeout=60, temperature=0, extra=extra)
        content = r["message"].get("content") or "{}"
        try:
            d = json.loads(content)
        except ValueError:
            return Decision("escalate", provider="deepseek", model=r["model"], seconds=r["seconds"], usage=r.get("usage") or {},
                            note="unparsable")
        act = d.get("action") if d.get("action") in ACTIONS else "escalate"
        target = d.get("target") if isinstance(d.get("target"), str) else None
        lp = (r.get("logprobs") or {}).get("content")
        pa = _value_span_prob(content, lp, "action")
        conf = pa if pa is not None else 0.5
        if act in NEEDS_TARGET:
            if not target or not obs.by_id(target):
                return Decision("escalate", provider="deepseek", model=r["model"], seconds=r["seconds"], usage=r.get("usage") or {},
                                note=f"invalid target {target}")
            pt = _value_span_prob(content, lp, "target")
            conf = conf * (pt if pt is not None else 1.0)
        key = d.get("key") if act == "key" else None
        if act == "key" and key not in KEYS[obs.kind]:
            return Decision("escalate", provider="deepseek", model=r["model"], seconds=r["seconds"], usage=r.get("usage") or {},
                            note=f"invalid key {key}")
        if act == "key":
            pk = _value_span_prob(content, lp, "key")
            conf = conf * (pk if pk is not None else 1.0)
        return Decision(act, target if act in NEEDS_TARGET or act == "scroll" else None, key, conf, {}, "deepseek", r["model"],
                        r["seconds"], r.get("usage") or {})


def _ds_screen(self, obs, goal, subgoal, history):
    """DeepSeek 看不到图：只按标题 / 历史 / 子目标选动作，目标位置交给视觉定位（UI-TARS 或视觉模型）。"""
    state = state_for(obs, goal, subgoal, history)
    user = json.dumps(state, ensure_ascii=False) + "\n\nNo element list: the app has no accessibility info. For click/type answer " \
        "target=\"subgoal_target\"; the position is found by a vision model.\nKeys allowed: " + ", ".join(KEYS["computer"])
    extra = {"response_format": {"type": "json_object"}, "logprobs": True, "top_logprobs": 2}
    if self.cfg["provider"] == "deepseek":
        extra["thinking"] = {"type": "disabled"}
    r = llm.chat([{"role": "system", "content": SYS_DS}, {"role": "user", "content": user}], cfg=self.cfg, model=self.model,
                 timeout=60, temperature=0, extra=extra)
    content = r["message"].get("content") or "{}"
    try:
        d = json.loads(content)
    except ValueError:
        d = {}
    act = d.get("action") if d.get("action") in SCREEN_ACTIONS else "escalate"
    pa = _value_span_prob(content, (r.get("logprobs") or {}).get("content"), "action")
    conf = pa if pa is not None else 0.5
    secs = r["seconds"]
    point = None
    if act in ("click", "type"):
        desc = screen_target(subgoal)
        try:
            g = ground_point(obs, desc, self.cfg)
        except FoxError as e:
            return Decision("escalate", provider="deepseek", model=r["model"], seconds=secs, note=f"grounding: {e.message}"[:160])
        point = (int(g["x"]), int(g["y"]))
        secs += float(g.get("seconds") or 0)
        if g.get("confidence") is not None:
            conf = min(conf, float(g["confidence"]))
    key = d.get("key") if act == "key" else None
    if act == "key" and key not in KEYS["computer"]:
        return Decision("escalate", provider="deepseek", model=r["model"], seconds=secs, note=f"invalid key {key}")
    return Decision(act, screen_target(subgoal) if point else None, key, conf, {}, "deepseek", r["model"], secs, r.get("usage") or {},
                    point=point)


DeepSeekPolicy.decide_screen = _ds_screen


def active_policy(cfg: dict | None = None, prefer: str = "auto") -> Policy:
    """默认：有 TypeSafe 密钥就用 Jev，没有就自动回退 DeepSeek（配上密钥后不用改别的）。"""
    from . import typesafe
    cfg = cfg or llm.load()
    want = prefer if prefer != "auto" else (cfg.get("step_policy") or "auto")
    if want in ("auto", "typesafe") and typesafe.api_key():
        return JevPolicy(model=(cfg.get("typesafe") or {}).get("model"))
    if want == "typesafe":
        raise FoxError("DEPENDENCY_MISSING", "TypeSafe API key missing", hint="foxos model provider add typesafe --key-stdin")
    return DeepSeekPolicy(cfg)
