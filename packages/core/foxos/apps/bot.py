"""智能体（bot）命令：foxos bot <资源> <动作> = MCP bot_<资源>_<动作>。

一个主智能体 + 任意多个其它智能体；每个智能体有自己的资料、后端（ACP 智能体或模型端点）、对话、记忆、
工作范围、技能、连接器、机器、审批规则、委托规则、例程和频道。设置项与 OpenBot 的每个 Bot 设置逐项对应，
见 docs/agent-chat-design.md。
"""

from __future__ import annotations

import os
from pathlib import Path

from .. import bots, secrets, skills
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app

BOT = Param("bot", "string", tr("bot.p_bot"), required=True, positional=True, metavar="BOT")


def _human(ctx: Context):
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("bot.human_only"))


def _cfg_params(with_name: bool) -> list[Param]:
    ps = [Param("name", "string", tr("bot.p_name"), required=with_name, positional=with_name, metavar="NAME")] if with_name else \
         [Param("name", "string", tr("bot.p_name"))]
    ps += [
        Param("title", "string", tr("bot.p_title")),
        Param("role", "string", tr("bot.p_role")),
        Param("instructions", "string", tr("bot.p_instructions"), cli_stdin=True),
        Param("icon", "string", tr("bot.p_icon")),
        Param("color", "string", tr("bot.p_color")),
        Param("image", "string", tr("bot.p_image")),
        Param("agent", "string", tr("bot.p_agent"), cli_flag="--acp-agent"),
        Param("base_url", "string", tr("bot.p_base_url")),
        Param("model", "string", tr("bot.p_model")),
        Param("api_key", "string", tr("bot.p_api_key"), cli_stdin=True, secret=True),
        Param("scope", "string", tr("bot.p_scope")),
        Param("isolated", "boolean", tr("bot.p_isolated")),
        Param("visibility", "string", tr("bot.p_visibility"), enum=["private", "public"]),
        Param("pinned", "boolean", tr("bot.p_pinned")),
        Param("hidden", "boolean", tr("bot.p_hidden")),
        Param("active", "boolean", tr("bot.p_active")),
        Param("notifications", "boolean", tr("bot.p_notifications")),
        Param("skills_mode", "string", tr("bot.p_skills_mode"), enum=["all", "selected"]),
        Param("skills", "array", tr("bot.p_skills"), items={"type": "string"}),
        Param("skills_off", "array", tr("bot.p_skills_off"), items={"type": "string"}),
        Param("connectors", "array", tr("bot.p_connectors"), items={"type": "string"}),
        Param("machines", "array", tr("bot.p_machines"), items={"type": "string"}),
        Param("default_machine", "string", tr("bot.p_default_machine")),
        Param("approval_mode", "string", tr("bot.p_approval_mode"), enum=bots.APPROVAL_MODES),
        Param("rules", "object", tr("bot.p_rules"), cli_kv=True, cli_flag="--rule"),
        Param("delegate_to", "array", tr("bot.p_delegate_to"), items={"type": "string"}),
        Param("max_depth", "integer", tr("bot.p_max_depth")),
        Param("max_per_turn", "integer", tr("bot.p_max_per_turn")),
    ]
    return ps


def _patch(cur: dict | None, a: dict) -> dict:
    cur = cur or bots.default_bot()
    p: dict = {k: a.get(k) for k in ("name", "title", "role", "instructions", "model", "visibility", "isolated", "pinned", "hidden",
                                    "active", "notifications", "scope")}
    if any(a.get(k) is not None for k in ("icon", "color", "image")):
        p["avatar"] = {"icon": a.get("icon"), "color": a.get("color"), "image": a.get("image")}
    be = cur.get("backend") or {}
    if a.get("agent") and not a.get("base_url"):
        p["backend"] = {"kind": "acp", "agent": a["agent"]}
    elif a.get("base_url") or (a.get("model") and be.get("kind") == "model"):
        p["backend"] = {"kind": "model", "base_url": a.get("base_url") or be.get("base_url"), "model": a.get("model") or be.get("model")}
    if any(a.get(k) is not None for k in ("skills_mode", "skills", "skills_off")):
        s = dict(cur.get("skills") or {})
        if a.get("skills_mode"):
            s["mode"] = a["skills_mode"]
        if a.get("skills") is not None:
            s["enabled"] = a["skills"]
            s.setdefault("mode", "selected") if a.get("skills_mode") is None else None
            if a.get("skills_mode") is None:
                s["mode"] = "selected"
        if a.get("skills_off") is not None:
            s["disabled"] = a["skills_off"]
        p["skills"] = s
    if a.get("connectors") is not None:
        p["connectors"] = a["connectors"]
    if a.get("machines") is not None or a.get("default_machine"):
        m = dict(cur.get("machines") or {})
        if a.get("machines") is not None:
            m["allowed"] = a["machines"]
        if a.get("default_machine"):
            m["default"] = a["default_machine"]
            if a["default_machine"] not in m.get("allowed", []):
                m["allowed"] = [*m.get("allowed", []), a["default_machine"]]
        p["machines"] = m
    if a.get("approval_mode") or a.get("rules") is not None:
        ap = dict(cur.get("approvals") or {})
        if a.get("approval_mode"):
            ap["mode"] = a["approval_mode"]
        if a.get("rules") is not None:
            rules = {r["kind"]: r["decision"] for r in ap.get("rules") or []}
            for k, v in (a["rules"] or {}).items():
                if v in (None, "", "default"):
                    rules.pop(k, None)
                else:
                    rules[k] = str(v)
            ap["rules"] = [{"kind": k, "decision": v} for k, v in rules.items()]
        p["approvals"] = ap
    if any(a.get(k) is not None for k in ("delegate_to", "max_depth", "max_per_turn")):
        dl = dict(cur.get("delegation") or {})
        if a.get("delegate_to") is not None:
            dl["allowed"] = a["delegate_to"]
        if a.get("max_depth") is not None:
            dl["max_depth"] = a["max_depth"]
        if a.get("max_per_turn") is not None:
            dl["max_per_turn"] = a["max_per_turn"]
        p["delegation"] = dl
    return {k: v for k, v in p.items() if v is not None}


def _public(ws, b: dict) -> dict:
    out = dict(b)
    out["has_api_key"] = bool(secrets.get(f"bot:{b['id']}:api_key"))
    out["identity"] = f"bot:{b['id']}"
    return out


def profile_list(ctx: Context, hidden: bool = False) -> dict:
    bs = [b for b in bots.all_bots(ctx.workspace) if hidden or not b.get("hidden")]
    return {"count": len(bs), "bots": [_public(ctx.workspace, b) for b in bs]}


def profile_show(ctx: Context, bot: str) -> dict:
    return {"bot": _public(ctx.workspace, bots.get(ctx.workspace, bot))}


def profile_create(ctx: Context, name: str, id: str | None = None, **a) -> dict:
    _human(ctx)
    key = a.pop("api_key", None)
    b = bots.create(ctx.workspace, _patch(None, {"name": name, **a}), id_=id)
    if key:
        secrets.put(f"bot:{b['id']}:api_key", key)
    return {"message": tr("bot.created", b["name"]), "bot": _public(ctx.workspace, b)}


def config_set(ctx: Context, bot: str, **a) -> dict:
    _human(ctx)
    cur = bots.get(ctx.workspace, bot)
    key = a.pop("api_key", None)
    b = bots.update(ctx.workspace, cur["id"], _patch(cur, a))
    if key:
        secrets.put(f"bot:{b['id']}:api_key", key)
    return {"message": tr("bot.updated", b["name"]), "bot": _public(ctx.workspace, b)}


def config_get(ctx: Context, bot: str) -> dict:
    b = bots.get(ctx.workspace, bot)
    return {"bot": b["id"], "config": _public(ctx.workspace, b), "skills_effective": [s["name"] for s in skills.for_bot(ctx.workspace, b)]}


def profile_delete(ctx: Context, bot: str) -> dict:
    _human(ctx)
    b = bots.delete(ctx.workspace, bot)
    secrets.delete(f"bot:{b['id']}:api_key")
    return {"message": tr("bot.deleted", b["name"]), "bot": b["id"]}


def profile_duplicate(ctx: Context, bot: str, name: str) -> dict:
    _human(ctx)
    b = bots.duplicate(ctx.workspace, bot, name)
    return {"message": tr("bot.created", b["name"]), "bot": _public(ctx.workspace, b)}


def profile_reset(ctx: Context, bot: str, keep_memory: bool = False) -> dict:
    _human(ctx)
    return bots.reset(ctx.workspace, bot, memory=not keep_memory)


def message_send(ctx: Context, bot: str, text: str, attachments: list | None = None, approve: str = "rules") -> dict:
    for a in attachments or []:
        if not ctx.resolve(a).is_file():
            raise FoxError("NOT_FOUND", tr("bot.no_attachment", a))
    if approve == "allow" and not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("bot.allow_human_only"))
    r = bots.run_turn(ctx.workspace, bot, text, attachments=attachments, actor=ctx.agent,
                      origin="person" if is_human(ctx.agent) else "handoff",
                      delegated_by=None if is_human(ctx.agent) else ctx.agent, approval_mode=None if approve == "rules" else approve,
                      keep=ctx.interface == "ui")  # 聊天窗口里复用智能体连接（同一个 ACP 会话，可以中途停止）
    return {"reply": r}


def message_list(ctx: Context, bot: str, limit: int = 50) -> dict:
    ms = bots.messages(ctx.workspace, bot, limit)
    return {"bot": bots.get(ctx.workspace, bot)["id"], "count": len(ms), "messages": ms}


def task_delegate(ctx: Context, to: str, task: str, constraints: str | None = None, expecting: str | None = None) -> dict:
    return bots.delegate(ctx.workspace, ctx.agent, to, task, constraints, expecting)


def skill_list(ctx: Context, bot: str | None = None, kind: str | None = None) -> dict:
    items = skills.for_bot(ctx.workspace, bots.get(ctx.workspace, bot)) if bot else skills.catalog(ctx.workspace)
    if kind:
        items = [s for s in items if s["kind"] == kind]
    return {"count": len(items), "skills": items, "notice": str(skills.PSTACK / "NOTICE")}


def skill_show(ctx: Context, name: str) -> dict:
    return {"skill": skills.get(ctx.workspace, name)}


def skill_run(ctx: Context, bot: str, name: str, task: str = "") -> dict:
    skills.get(ctx.workspace, name)
    return message_send(ctx, bot, f"/{name} {task}".strip())


def skill_install(ctx: Context, harness: str) -> dict:
    _human(ctx)
    return skills.install(harness, ws=ctx.workspace)


def skill_models(ctx: Context, roles: dict) -> dict:
    """写 ~/.agents/pstack-models.md：pstack 的角色 → 狐狸OS 智能体（例如 arena runners: bot:claude, bot:codex）。"""
    _human(ctx)
    known = {b["id"] for b in bots.all_bots(ctx.workspace)}
    lines = ["# pstack model configuration (written by FoxOS). Values are FoxOS bots: delegate to them with bot_task_delegate."]
    for role, val in (roles or {}).items():
        ids = [v.strip().removeprefix("bot:") for v in str(val).split(",") if v.strip()]
        for i in ids:
            if i not in known and i not in ("inherit-parent", "auto"):
                raise FoxError("NOT_FOUND", tr("bots.no_such_bot", i))
        lines.append(f"{role}: " + ", ".join(i if i in ("inherit-parent", "auto") else f"bot:{i}" for i in ids))
    p = Path.home() / ".agents" / "pstack-models.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": str(p), "roles": len(roles or {})}


def memory_list(ctx: Context, bot: str) -> dict:
    m = bots.memory(ctx.workspace, bot)
    return {"count": len(m), "memory": m}


def memory_add(ctx: Context, bot: str, text: str) -> dict:
    b = bots.get(ctx.workspace, bot)
    if not is_human(ctx.agent) and not ctx.agent.startswith(f"bot:{b['id']}"):
        raise FoxError("PERMISSION_DENIED", tr("bot.memory_own_only"))
    return {"memory": bots.memory_add(ctx.workspace, b["id"], text, ctx.agent)}


def memory_forget(ctx: Context, bot: str, memory: str) -> dict:
    _human(ctx)
    return bots.memory_forget(ctx.workspace, bot, memory)


def approval_list(ctx: Context) -> dict:
    a = bots.approvals_pending(ctx.workspace)
    return {"count": len(a), "approvals": a}


def approval_answer(ctx: Context, request: str, option: str | None = None, deny: bool = False) -> dict:
    _human(ctx)
    return {"approval": bots.approval_answer(ctx.workspace, request, None if deny else option, ctx.agent)}


def routine_list(ctx: Context, bot: str | None = None) -> dict:
    rs = bots.routines(ctx.workspace)
    if bot:
        bid = bots.get(ctx.workspace, bot)["id"]
        rs = [r for r in rs if r["bot"] == bid]
    return {"count": len(rs), "routines": rs}


def routine_create(ctx: Context, bot: str, instruction: str, every_minutes: int, title: str | None = None) -> dict:
    return {"routine": bots.routine_create(ctx.workspace, bot, instruction, every_minutes, title)}


def routine_update(ctx: Context, routine: str, enabled: bool | None = None, every_minutes: int | None = None) -> dict:
    return {"routine": bots.routine_update(ctx.workspace, routine, enabled, every_minutes)}


def routine_delete(ctx: Context, routine: str) -> dict:
    return bots.routine_delete(ctx.workspace, routine)


def routine_run(ctx: Context, routine: str | None = None) -> dict:
    r = bots.routine_tick(ctx.workspace, run_id=routine)
    return {"ran": len(r), "results": r}


def channel_set(ctx: Context, bot: str, kind: str, token: str | None = None, chat: str | None = None) -> dict:
    _human(ctx)
    from .. import channels
    return channels.configure(ctx.workspace, bot, kind, token, chat)


def channel_remove(ctx: Context, bot: str, kind: str) -> dict:
    _human(ctx)
    from .. import channels
    return channels.remove(ctx.workspace, bot, kind)


def channel_poll(ctx: Context, bot: str | None = None) -> dict:
    from .. import channels
    return channels.poll(ctx.workspace, bot)


register_app("bot", tr("bot.app_summary"), tr("bot.app_description"))
register(Command("bot", "profile list", tr("bot.c_list"), profile_list,
                 params=[Param("hidden", "boolean", tr("bot.p_show_hidden"), default=False)], examples=["foxos bot profile list --json"], audited=False))
register(Command("bot", "profile show", tr("bot.c_show"), profile_show, params=[BOT], examples=["foxos bot profile show fox --json"]))
register(Command("bot", "profile create", tr("bot.c_create"), profile_create,
                 params=[*_cfg_params(True), Param("id", "string", tr("bot.p_id"))],
                 examples=["foxos bot profile create Coder --title Coding --acp-agent codex-acp --icon code --color '#3B82F6' --isolated"],
                 permission="create", limits=[tr("bot.human_only")]))
register(Command("bot", "profile update", tr("bot.c_update"), config_set, params=[BOT, *_cfg_params(False)],
                 examples=["foxos bot profile update coder --title Backend"], permission="modify", limits=[tr("bot.human_only")]))
register(Command("bot", "profile delete", tr("bot.c_delete"), profile_delete, params=[BOT], examples=["foxos bot profile delete coder"],
                 permission="delete", limits=[tr("bot.human_only"), tr("bot.l_main")]))
register(Command("bot", "profile duplicate", tr("bot.c_duplicate"), profile_duplicate,
                 params=[BOT, Param("name", "string", tr("bot.p_name"), required=True)], examples=["foxos bot profile duplicate coder --name Coder2"],
                 permission="create"))
register(Command("bot", "profile reset", tr("bot.c_reset"), profile_reset,
                 params=[BOT, Param("keep_memory", "boolean", tr("bot.p_keep_memory"), default=False)], examples=["foxos bot profile reset coder"],
                 permission="delete"))
register(Command("bot", "config get", tr("bot.c_config_get"), config_get, params=[BOT], examples=["foxos bot config get fox --json"]))
register(Command("bot", "config set", tr("bot.c_config_set"), config_set, params=[BOT, *_cfg_params(False)],
                 examples=["foxos bot config set coder --acp-agent claude-acp --skills tdd,architect --approval-mode allow_reads --rule execute=ask",
                           "foxos bot config set fox --machines local,vm1 --default-machine local --connectors exa"],
                 permission="modify", limits=[tr("bot.human_only")]))
register(Command("bot", "message send", tr("bot.c_send"), message_send,
                 params=[BOT, Param("text", "string", tr("bot.p_text"), required=True, positional=True, metavar="TEXT", cli_stdin=True),
                         Param("attachments", "array", tr("bot.p_attachments"), items={"type": "string"}, cli_flag="--attach", cli_repeat=True),
                         Param("approve", "string", tr("bot.p_approve"), enum=["rules", "allow", "deny"], default="rules")],
                 examples=["foxos bot message send fox '@coder write hello.py'", "foxos bot message send coder '/tdd add tests for parse()'"],
                 permission="run"))
register(Command("bot", "message list", tr("bot.c_messages"), message_list,
                 params=[BOT, Param("limit", "integer", tr("bot.p_limit"), default=50)], examples=["foxos bot message list fox --json"], audited=False))
register(Command("bot", "task delegate", tr("bot.c_delegate"), task_delegate,
                 params=[Param("to", "string", tr("bot.p_to"), required=True),
                         Param("task", "string", tr("bot.p_task"), required=True, positional=True, metavar="TASK", cli_stdin=True),
                         Param("constraints", "string", tr("bot.p_constraints")), Param("expecting", "string", tr("bot.p_expecting"))],
                 examples=["foxos bot task delegate --to coder 'fix tests/test_x.py' --expecting 'which files changed'"],
                 permission="run", limits=[tr("bot.l_delegate")]))
register(Command("bot", "skill list", tr("bot.c_skills"), skill_list,
                 params=[Param("bot", "string", tr("bot.p_bot")), Param("kind", "string", tr("bot.p_kind"), enum=["skill", "principle", "subagent"])],
                 examples=["foxos bot skill list --json", "foxos bot skill list --kind principle"], audited=False))
register(Command("bot", "skill show", tr("bot.c_skill_show"), skill_show,
                 params=[Param("name", "string", tr("bot.p_skill"), required=True, positional=True, metavar="SKILL")], examples=["foxos bot skill show architect"]))
register(Command("bot", "skill run", tr("bot.c_skill_run"), skill_run,
                 params=[BOT, Param("name", "string", tr("bot.p_skill"), required=True, cli_flag="--skill"),
                         Param("task", "string", tr("bot.p_task"), default="", positional=True, metavar="TASK")],
                 examples=["foxos bot skill run fox --skill architect 'design the plugin interface'"], permission="run"))
register(Command("bot", "skill install", tr("bot.c_skill_install"), skill_install,
                 params=[Param("harness", "string", tr("bot.p_harness"), required=True, enum=list(skills.HARNESS_DIRS))],
                 examples=["foxos bot skill install --harness claude-code"], permission="create"))
register(Command("bot", "skill models", tr("bot.c_skill_models"), skill_models,
                 params=[Param("roles", "object", tr("bot.p_roles"), cli_kv=True, positional=True, metavar="ROLE=BOTS")],
                 examples=["foxos bot skill models 'arena runners=claude,codex'"], permission="modify"))
register(Command("bot", "memory list", tr("bot.c_memory_list"), memory_list, params=[BOT], examples=["foxos bot memory list fox"], audited=False))
register(Command("bot", "memory add", tr("bot.c_memory_add"), memory_add,
                 params=[BOT, Param("text", "string", tr("bot.p_text"), required=True, positional=True, metavar="TEXT")],
                 examples=["foxos bot memory add fox 'weekly report goes to #team'"], permission="create"))
register(Command("bot", "memory forget", tr("bot.c_memory_forget"), memory_forget,
                 params=[BOT, Param("memory", "string", tr("bot.p_memory"), required=True, positional=True, metavar="MEMORY_ID")],
                 examples=["foxos bot memory forget fox mem-1a2b3c4d"], permission="delete"))
register(Command("bot", "approval list", tr("bot.c_approvals"), approval_list, examples=["foxos bot approval list --json"], audited=False))
register(Command("bot", "approval answer", tr("bot.c_approval_answer"), approval_answer,
                 params=[Param("request", "string", tr("bot.p_request"), required=True, positional=True, metavar="REQUEST"),
                         Param("option", "string", tr("bot.p_option")), Param("deny", "boolean", tr("bot.p_deny"), default=False)],
                 examples=["foxos bot approval answer apr-0123456789 --option allow"], permission="modify", limits=[tr("bot.human_only")]))
register(Command("bot", "routine list", tr("bot.c_routines"), routine_list, params=[Param("bot", "string", tr("bot.p_bot"))],
                 examples=["foxos bot routine list --json"], audited=False))
register(Command("bot", "routine create", tr("bot.c_routine_create"), routine_create,
                 params=[BOT, Param("instruction", "string", tr("bot.p_instruction"), required=True),
                         Param("every_minutes", "integer", tr("bot.p_every"), required=True), Param("title", "string", tr("bot.p_title"))],
                 examples=["foxos bot routine create fox --instruction 'tidy the inbox' --every-minutes 60"], permission="create", limits=[tr("bot.l_routine")]))
register(Command("bot", "routine update", tr("bot.c_routine_update"), routine_update,
                 params=[Param("routine", "string", tr("bot.p_routine"), required=True, positional=True, metavar="ROUTINE"),
                         Param("enabled", "boolean", tr("bot.p_enabled")), Param("every_minutes", "integer", tr("bot.p_every"))],
                 examples=["foxos bot routine update rt-1a2b3c4d --no-enabled"], permission="modify"))
register(Command("bot", "routine delete", tr("bot.c_routine_delete"), routine_delete,
                 params=[Param("routine", "string", tr("bot.p_routine"), required=True, positional=True, metavar="ROUTINE")],
                 examples=["foxos bot routine delete rt-1a2b3c4d"], permission="delete"))
register(Command("bot", "routine run", tr("bot.c_routine_run"), routine_run,
                 params=[Param("routine", "string", tr("bot.p_routine"))], examples=["foxos bot routine run", "foxos bot routine run --routine rt-1a2b3c4d"],
                 permission="run"))
register(Command("bot", "channel set", tr("bot.c_channel_set"), channel_set,
                 params=[BOT, Param("kind", "string", tr("bot.p_channel_kind"), required=True, enum=["telegram", "webhook"]),
                         Param("token", "string", tr("bot.p_channel_token"), cli_stdin=True, secret=True), Param("chat", "string", tr("bot.p_chat"))],
                 examples=["printf %s \"$TG\" | foxos bot channel set fox --kind telegram --token-stdin", "foxos bot channel set fox --kind webhook"],
                 permission="modify", limits=[tr("bot.human_only")]))
register(Command("bot", "channel remove", tr("bot.c_channel_remove"), channel_remove,
                 params=[BOT, Param("kind", "string", tr("bot.p_channel_kind"), required=True, enum=["telegram", "webhook"])],
                 examples=["foxos bot channel remove fox --kind telegram"], permission="delete"))
register(Command("bot", "channel poll", tr("bot.c_channel_poll"), channel_poll, params=[Param("bot", "string", tr("bot.p_bot"))],
                 examples=["foxos bot channel poll"], permission="run"))
