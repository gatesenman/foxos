"""能力目录：从命令注册表生成 `foxos help --json`、JSON Schema 工具定义、MCP tools/list。"""

from __future__ import annotations

from foxos.i18n import tr
from . import __version__
from .errors import EXIT_CODE_DOCS, FoxError
from .kernel import APPS, REGISTRY, load_apps

CONVENTIONS = {
    "invocation": tr("catalog.foxos_global_options_app_command"),
    "global_options": {
        "--json": tr("catalog.json_output_success_failure"),
        "--workspace PATH": tr("catalog.workspace_root_default_foxos"),
        "--agent NAME": tr("catalog.caller_identity_written_to_the_audit"),
        "--task ID": tr("catalog.related_task_id_default_foxos_task"),
        "--lang LANG": tr("cli.lang_option"),
        "--lock-wait SECONDS": tr("catalog.maximum_seconds_to_wait_when_the"),
        "--machine NAME": tr("catalog.machine_option"),
    },
    "exit_codes": {str(k): v for k, v in EXIT_CODE_DOCS.items()},
    "paths": tr("catalog.all_paths_are_relative_to_the"),
    "formulas": tr("catalog.a_cell_value_starting_with_is_an"),
    "audit": tr("catalog.every_call_including_failures_and"),
    "tool_names": tr("catalog.tool_name_command_id_with_replaced"),
}


def command_entry(cmd) -> dict:
    return {
        "id": cmd.id,
        "tool": cmd.tool_name,
        "cli": cmd.cli,
        "usage": cmd.usage(),
        "summary": cmd.summary,
        "permission": cmd.permission,
        "params": [
            {
                "name": p.name,
                "type": p.type,
                "required": p.required,
                "description": p.description,
                "cli": (p.metavar or p.name.upper()) if p.positional else p.flag,
                **({"short": p.cli_short} if p.cli_short else {}),
                **({"enum": p.enum} if p.enum else {}),
                **({"default": p.default} if p.default is not None else {}),
                **({"path_access": p.path} if p.path else {}),
            }
            for p in cmd.params
        ],
        "examples": cmd.examples,
        "limits": cmd.limits,
        "input_schema": cmd.input_schema(),
    }


def catalog(app: str | None = None) -> dict:
    load_apps()
    if app and app not in APPS:
        raise FoxError("NOT_FOUND", tr("catalog.unknown_app", app), details={"apps": sorted(APPS)})
    apps = []
    for name, meta in APPS.items():
        if app and name != app:
            continue
        cmds = [command_entry(c) for c in REGISTRY.values() if c.app == name]
        apps.append({**meta, "commands": cmds})
    return {"name": "foxos", "version": __version__, "conventions": CONVENTIONS, "apps": apps}


ERROR_CODES = tr("catalog.error_codes_usage_2_not_found_3")


def tool_description(cmd) -> str:
    d = tr("catalog.cli", cmd.summary, cmd.usage())
    if cmd.description:
        d += tr("catalog.text", cmd.description)
    if cmd.limits:
        d += tr("catalog.limits") + tr("common.text").join(cmd.limits)
    if cmd.examples:
        d += tr("catalog.examples") + cmd.examples[0]
    return d


def everything_ids() -> set[str]:
    try:
        from .apps.everything import APPS as EV
        return set(EV)
    except Exception:  # noqa: BLE001
        return set()


def select_commands(profile: str = "compact", apps: list[str] | None = None) -> list:
    """MCP 暴露哪些命令。

    compact（默认）：内置应用的全部命令 + Everything 的元工具（everything run / commands 等），
                    51 个 Everything 应用的数千个操作通过 everything_run 调用，避免客户端工具列表过长；
    full：全部命令；apps：额外暴露这些应用的全部命令（如 --apps tasks,chess）。
    """
    load_apps()
    ev = everything_ids()
    want = set(apps or [])
    out = []
    for c in REGISTRY.values():
        if profile == "full" or c.app not in ev or c.app in want:
            out.append(c)
    return out


NO_MACHINE_PARAM = {"machine", "control"}  # 机器管理与接管只在本机执行


def mcp_tools(profile: str = "full", apps: list[str] | None = None, names: str = "underscore") -> list[dict]:
    out = []
    for c in select_commands(profile, apps):
        schema = c.input_schema()
        if c.app not in NO_MACHINE_PARAM:
            schema = {**schema, "properties": {**schema.get("properties", {}),
                                               "machine": {"type": "string", "description": tr("catalog.machine_param")}}}
        t = {"name": c.id if names == "dotted" else c.tool_name, "title": c.cli, "description": tool_description(c),
             "inputSchema": schema,
             "annotations": {"title": c.cli, "readOnlyHint": c.permission == "read", "destructiveHint": c.permission == "delete",
                             "idempotentHint": c.permission == "read", "openWorldHint": False},
             "_meta": {"foxos/id": c.id, "foxos/cli": c.cli, "foxos/permission": c.permission, "foxos/examples": c.examples}}
        out.append(t)
    return out


def openai_tools() -> list[dict]:
    return [
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["inputSchema"]}}
        for t in mcp_tools()
    ]
