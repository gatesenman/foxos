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
    return {"model": llm.public(llm.load()), "providers": sorted(llm.PROVIDERS), "grounding_kinds": list(llm.GROUNDING_KINDS)}


def model_set(ctx: Context, provider: str | None = None, model: str | None = None, vision_model: str | None = None,
              base_url: str | None = None, vision: str | None = None, grounding: str | None = None, grounding_url: str | None = None,
              grounding_model: str | None = None, max_steps: int | None = None) -> dict:
    from ..cu import llm
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("cu.model_human_only"))
    if provider and provider not in llm.PROVIDERS:
        raise FoxError("USAGE", tr("cu.bad_provider", ", ".join(sorted(llm.PROVIDERS))))
    patch = {"provider": provider, "model": model, "vision_model": vision_model, "base_url": base_url, "vision": vision,
             "max_steps": max_steps,
             "grounding": {"kind": grounding, "base_url": grounding_url, "model": grounding_model}}
    if provider:  # 换服务商：没给的模型 / 地址回到该服务商的默认值
        llm.reset_keys([k for k in ("model", "vision_model", "base_url") if patch[k] is None])
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
                  approve: str = "risky", vision: str = "auto") -> dict:
    from ..cu.loop import Loop, workspace_argv
    from ..kernel import invoke
    if launch:
        invoke("desktop.launch", {"command": workspace_argv(ctx, launch)}, ctx)
        import time
        time.sleep(2.0)
    return Loop(ctx, "computer", task, max_steps=int(max_steps), approve=approve, vision=vision, app=app).run()


register_app("computer", tr("cu.computer_title"), tr("cu.computer_summary"))
register(Command("computer", "model show", tr("cu.c_model_show"), model_show, examples=["foxos computer model show --json"],
                 permission="read", audited=False))
register(Command("computer", "model set", tr("cu.c_model_set"), model_set,
                 params=[Param("provider", "string", tr("cu.p_provider")), Param("model", "string", tr("cu.p_model")),
                         Param("vision_model", "string", tr("cu.p_vision_model")), Param("base_url", "string", tr("cu.p_base_url")),
                         Param("vision", "string", tr("cu.p_vision_mode"), enum=["auto", "off"]),
                         Param("grounding", "string", tr("cu.p_grounding"), enum=["vlm", "ui-tars", "omniparser", "none"]),
                         Param("grounding_url", "string", tr("cu.p_grounding_url")), Param("grounding_model", "string", tr("cu.p_grounding_model")),
                         Param("max_steps", "integer", tr("cu.p_max_steps"))],
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
                         Param("vision", "string", tr("cu.p_vision"), enum=["auto", "on", "off"], default="auto")],
                 examples=["foxos computer task '在 Mousepad 里写一行 hello 并保存' --launch mousepad --launch notes.txt --app mousepad --vision off"],
                 limits=[tr("cu.l_task_model"), tr("cu.l_task_approve"), tr("cu.l_takeover")], permission="run"))
