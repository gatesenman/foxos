"""电脑操控智能体：`foxos computer task "…"` 用模型看桌面（AT-SPI 无障碍树，可选截图）一步步操作程序。

`foxos computer model show|set|key` 配置模型：文字模型（DeepSeek v4 pro 等）配合无障碍树即可；配了视觉模型
（deepseek-flash、Qwen3-VL、GPT…）时附截图，并可用视觉定位（通用视觉模型 / UI-TARS / OmniParser）点没有无障碍信息的东西。
人工接管（foxos desktop takeover）时循环暂停，恢复后继续；高风险动作要人批准（foxos bot approval answer）。
"""

from __future__ import annotations

from .. import secrets
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app


def model_show(ctx: Context) -> dict:
    from ..cu import llm
    return {"model": llm.public(llm.load()), "providers": sorted(llm.all_providers()), "grounding_kinds": list(llm.GROUNDING_KINDS)}


def model_set(ctx: Context, provider: str | None = None, model: str | None = None, vision_model: str | None = None,
              base_url: str | None = None, vision: str | None = None, grounding: str | None = None, grounding_url: str | None = None,
              grounding_model: str | None = None, max_steps: int | None = None, step_policy: str | None = None,
              gate_high: float | None = None, gate_low: float | None = None) -> dict:
    from ..cu import llm
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("cu.model_human_only"))
    if provider and provider not in llm.all_providers():
        raise FoxError("USAGE", tr("cu.bad_provider", ", ".join(sorted(llm.all_providers()))))
    patch = {"provider": provider, "model": model, "vision_model": vision_model, "base_url": base_url, "vision": vision,
             "max_steps": max_steps, "step_policy": step_policy,
             "grounding": {"kind": grounding, "base_url": grounding_url, "model": grounding_model}}
    if provider:  # 换服务商：没给的模型 / 地址回到该服务商的默认值
        llm.reset_keys([k for k in ("model", "vision_model", "base_url") if patch[k] is None])
    if gate_high is not None or gate_low is not None:
        old = llm.load().get("gate") or {}
        hi = float(gate_high if gate_high is not None else old.get("high", 0.85))
        lo = float(gate_low if gate_low is not None else old.get("low", 0.55))
        if not 0 <= lo <= hi <= 1:
            raise FoxError("USAGE", tr("cu.bad_gate"))
        patch["gate"] = {"high": hi, "low": lo}
    cfg = llm.save(patch)
    return {"message": tr("cu.model_saved"), "model": llm.public(cfg)}


def model_key(ctx: Context, value: str, provider: str | None = None) -> dict:
    from ..cu import llm
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("cu.model_human_only"))
    p = provider or llm.load()["provider"]
    secrets.put(llm.key_name(p), value.strip())
    return {"message": tr("cu.key_saved", p), "provider": p, "api_key": f"…{value.strip()[-4:]}"}


def model_test(ctx: Context, vision: bool = False) -> dict:
    from ..cu import llm
    r = llm.chat([{"role": "user", "content": "Reply with the single word: pong"}], vision=vision)
    return {"ok": "pong" in (r["message"].get("content") or "").lower(), "model": r["model"], "seconds": r["seconds"],
            "reply": (r["message"].get("content") or "")[:80]}


def computer_task(ctx: Context, task: str, app: str | None = None, launch: list | None = None, max_steps: int = 25,
                  approve: str = "risky", vision: str = "auto", mode: str = "s1s2", policy: str = "auto", surface: str = "auto",
                  url: str | None = None) -> dict:
    import os
    from ..cu.agent import needs_browser_fallback
    from ..cu.loop import Loop, workspace_argv
    from ..kernel import invoke
    # 机器人设置里的默认（FOXOS_CU_*，由机器人轮次传进 MCP 环境），命令行参数优先
    if surface == "auto":
        surface = os.environ.get("FOXOS_CU_SURFACE") or "auto"
    if policy == "auto":
        policy = os.environ.get("FOXOS_CU_POLICY") or "auto"
    why = None
    if surface == "auto" and not launch:
        why = needs_browser_fallback(ctx, task, app, url)
    if surface == "browser" or why:
        # 兜底：agent-desktop 读不到网页内容（或手动指定）→ browser use（Chrome CDP / agent-browser，按编号元素操作）
        r = invoke("browser.task", {k: v for k, v in {"task": task, "url": url, "mode": mode, "policy": policy, "max_steps": max_steps,
                                                      "approve": approve, "vision": vision}.items() if v is not None}, ctx)
        return {**r, "routed_to": "browser", "route_reason": why or "surface=browser"}
    if launch:
        invoke("desktop.launch", {"command": workspace_argv(ctx, launch)}, ctx)
        import time
        time.sleep(2.0)
    if mode == "llm":
        return Loop(ctx, "computer", task, max_steps=int(max_steps), approve=approve, vision=vision, app=app).run()
    from ..cu.agent import Agent
    r = Agent(ctx, "computer", task, policy=policy, max_steps=int(max_steps), approve=approve, vision=vision, app=app,
              surface=surface).run()
    return {**r, "routed_to": "computer"}


def doctor(ctx: Context) -> dict:
    """默认电脑操控栈的体检：agent-desktop（观察 / 操作）+ Jev（单步策略，没密钥回退 DeepSeek）+ 截图 / xdotool 兜底。"""
    import os
    import shutil
    from ..cu import agent_desktop, llm, models, policy, typesafe
    cfg = llm.load()
    checks = []

    def add(name, ok, detail, hint=None, required=True):
        checks.append({"check": name, "ok": bool(ok), "detail": detail, "hint": hint, "required": required})

    ad = agent_desktop.status()
    add("agent-desktop", ad.get("installed") and not ad.get("error"),
        f"{ad.get('version') or ad.get('pin')} accessibility={ad.get('accessibility')}" if ad.get("installed") else tr("ad.missing"),
        None if ad.get("installed") else "foxos computer backend install")
    disp = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    add("display", bool(disp), disp or "-", tr("desktop.start_an_xfce_session_or_set_display"))
    fb = {t: bool(shutil.which(t)) for t in ("xdotool", "scrot", "import")}
    add("fallback: computer use (screenshot + xdotool)", fb["xdotool"] and (fb["scrot"] or fb["import"]), ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in fb.items()),
        "sudo apt install xdotool scrot", required=False)
    has_planner = llm.has_key(cfg)
    add("planner (System 2)", has_planner, f"{cfg['provider']} / {cfg['model']}", "foxos model provider add deepseek --key-stdin")
    ts = bool(typesafe.api_key())
    try:
        active = policy.active_policy(cfg).name
    except FoxError as e:
        active = f"error: {e.message}"
    add("step policy (System 1)", active in ("typesafe", "deepseek"),
        f"active={active}; typesafe key={'yes' if ts else 'no'}" + ("" if ts else " → using DeepSeek JSON fallback; switches to Jev when a TypeSafe key is added"),
        None if ts else "foxos model provider add typesafe --key-stdin", required=False)
    g = cfg.get("grounding") or {}
    inst = {m["id"]: m for m in models.installed()}
    gres = g.get("kind") or "auto"
    if gres == "auto":
        gres = "auto→typesafe (Jev Box)" if ts else ("auto→ui-tars" if "ui-tars-1.5-7b" in inst else "auto→vlm")
    add("vision grounding (optional)", True, f"kind={gres} model={g.get('model') or ('vision model ' + str(cfg.get('vision_model')))}"
        + f"; ui-tars-1.5-7b installed={'yes' if 'ui-tars-1.5-7b' in inst else 'no'}", None if inst else "foxos model install ui-tars-1.5-7b",
        required=False)
    from ..cu import agent_browser
    ab = agent_browser.status()
    add("fallback: browser use (Chrome CDP" + (" + agent-browser)" if ab["installed"] else ")"), True,
        f"agent-browser={'yes ' + ab['pin'] if ab['installed'] else 'no (built-in CDP)'}", None if ab["installed"] else
        "foxos browser engine install agent-browser", required=False)
    gate = cfg.get("gate") or {}
    gk = g.get("kind") or "auto"
    return {"ok": all(c["ok"] for c in checks if c["required"]), "checks": checks,
            "stack": {"default": f"{agent_desktop.PIN} + {'Jev' if active == 'typesafe' else active} step policy + {cfg['model']} planner",
                      "observe_act": agent_desktop.PIN, "step_policy": active, "planner": cfg["model"],
                      "fallbacks": {"computer_use": f"screenshot + xdotool, grounding={gk} (only when agent-desktop sees no accessible elements)",
                                    "browser_use": ("agent-browser " if ab["installed"] else "built-in ") + "Chrome CDP (only when agent-desktop "
                                                   "cannot read the web page)"},
                      "surface_default": os.environ.get("FOXOS_CU_SURFACE") or "auto",
                      "gate": {"high": gate.get("high", 0.85), "low": gate.get("low", 0.55)}}}


def backend_install(ctx: Context) -> dict:
    from ..cu import agent_desktop
    return agent_desktop.install()


def backend_status(ctx: Context) -> dict:
    from ..cu import agent_desktop
    return agent_desktop.status()


register_app("computer", tr("cu.computer_title"), tr("cu.computer_summary"))
register(Command("computer", "doctor", tr("cu.c_doctor"), doctor, examples=["foxos computer doctor", "foxos computer doctor --json"],
                 permission="read", audited=False))
register(Command("computer", "backend install", tr("cu.c_backend_install"), backend_install, examples=["foxos computer backend install"],
                 permission="run"))
register(Command("computer", "backend status", tr("cu.c_backend_status"), backend_status, examples=["foxos computer backend status --json"],
                 permission="read", audited=False))
register(Command("computer", "model show", tr("cu.c_model_show"), model_show, examples=["foxos computer model show --json"],
                 permission="read", audited=False))
register(Command("computer", "model set", tr("cu.c_model_set"), model_set,
                 params=[Param("provider", "string", tr("cu.p_provider")), Param("model", "string", tr("cu.p_model")),
                         Param("vision_model", "string", tr("cu.p_vision_model")), Param("base_url", "string", tr("cu.p_base_url")),
                         Param("vision", "string", tr("cu.p_vision_mode"), enum=["auto", "off"]),
                         Param("grounding", "string", tr("cu.p_grounding"), enum=["auto", "vlm", "ui-tars", "omniparser", "typesafe", "none"]),
                         Param("grounding_url", "string", tr("cu.p_grounding_url")), Param("grounding_model", "string", tr("cu.p_grounding_model")),
                         Param("max_steps", "integer", tr("cu.p_max_steps")),
                         Param("step_policy", "string", tr("cu.p_step_policy"), enum=["auto", "typesafe", "deepseek"]),
                         Param("gate_high", "number", tr("cu.p_gate_high")), Param("gate_low", "number", tr("cu.p_gate_low"))],
                 examples=["foxos computer model set --provider deepseek", "foxos computer model set --vision off",
                           "foxos computer model set --grounding ui-tars --grounding-url http://127.0.0.1:8000/v1 --grounding-model ByteDance-Seed/UI-TARS-1.5-7B"],
                 limits=[tr("cu.l_human_only")], permission="modify"))
register(Command("computer", "model key", tr("cu.c_model_key"), model_key,
                 params=[Param("value", "string", tr("cu.p_key_value"), required=True, positional=True, metavar="KEY", secret=True, cli_stdin=True),
                         Param("provider", "string", tr("cu.p_provider"))],
                 examples=["foxos computer model key --value-stdin < deepseek.key"], limits=[tr("cu.l_human_only")], permission="modify"))
register(Command("computer", "model test", tr("cu.c_model_test"), model_test,
                 params=[Param("vision", "boolean", tr("cu.p_test_vision"), default=False)],
                 examples=["foxos computer model test"], permission="read"))
register(Command("computer", "task", tr("cu.c_computer_task"), computer_task,
                 params=[Param("task", "string", tr("cu.p_task"), required=True, positional=True, metavar="TASK"),
                         Param("app", "string", tr("cu.p_task_app")),
                         Param("launch", "array", tr("cu.p_launch"), items={"type": "string"}, cli_repeat=True, metavar="ARG"),
                         Param("max_steps", "integer", tr("cu.p_max_steps"), default=25),
                         Param("approve", "string", tr("cu.p_approve"), enum=["risky", "ask", "auto", "deny"], default="risky"),
                         Param("vision", "string", tr("cu.p_vision"), enum=["auto", "on", "off"], default="auto"),
                         Param("mode", "string", tr("cu.p_mode"), enum=["s1s2", "llm"], default="s1s2"),
                         Param("policy", "string", tr("cu.p_policy"), enum=["auto", "typesafe", "deepseek"], default="auto"),
                         Param("surface", "string", tr("cu.p_surface"), enum=["auto", "a11y", "screen", "browser"], default="auto"),
                         Param("url", "string", tr("cu.p_url"))],
                 examples=["foxos computer task '在 Mousepad 里写一行 hello 并保存' --launch mousepad --launch notes.txt --app mousepad --vision off",
                           "foxos computer task '在 xpaint 里点“确定”' --app xpaint --surface screen",
                           "foxos computer task '查一下 example.com 的标题' --url https://example.com"],
                 limits=[tr("cu.l_task_model"), tr("cu.l_task_approve"), tr("cu.l_takeover")], permission="run"))
