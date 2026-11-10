"""能力目录：从命令注册表生成 `foxos help --json`、JSON Schema 工具定义、MCP tools/list。"""

from __future__ import annotations

from . import __version__
from .errors import EXIT_CODE_DOCS, FoxError
from .kernel import APPS, REGISTRY, load_apps

CONVENTIONS = {
    "invocation": "foxos [全局选项] <app> <command> [参数]；全局选项可放在任意位置",
    "global_options": {
        "--json": "以 JSON 输出：成功 {ok:true, command, result}，失败 {ok:false, command, error:{code, exit_code, message, hint}}",
        "--workspace PATH": "工作空间根目录（默认 $FOXOS_WORKSPACE 或 ~/FoxOS/workspace）",
        "--agent NAME": "调用者身份，写入审计日志（默认 $FOXOS_AGENT 或 human）",
        "--task ID": "关联的任务 ID（默认 $FOXOS_TASK）",
        "--lock-wait SECONDS": "目标文件被锁时最多等待的秒数（默认 0，立即返回 LOCKED）",
    },
    "exit_codes": {str(k): v for k, v in EXIT_CODE_DOCS.items()},
    "paths": "所有路径相对于工作空间根目录；越出工作空间或访问 .foxos/ 返回 PERMISSION_DENIED（4）",
    "formulas": "单元格值以 = 开头即为 Excel 公式，如 =SUM(B2:B13)；以 ' 开头强制为文本",
    "audit": "每次调用（含失败与拒绝）都追加到 <workspace>/.foxos/audit.jsonl；只读自省命令 audit tail、control status 成功时不记录",
    "tool_names": "工具接口名 = 命令 ID 把 . 换成 _，如 sheets.chart.create → sheets_chart_create",
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
        raise FoxError("NOT_FOUND", f"未知应用：{app}", details={"apps": sorted(APPS)})
    apps = []
    for name, meta in APPS.items():
        if app and name != app:
            continue
        cmds = [command_entry(c) for c in REGISTRY.values() if c.app == name]
        apps.append({**meta, "commands": cmds})
    return {"name": "foxos", "version": __version__, "conventions": CONVENTIONS, "apps": apps}


ERROR_CODES = "错误码：USAGE(2) NOT_FOUND(3) PERMISSION_DENIED(4) LOCKED(5) DEPENDENCY_MISSING(6) CONFLICT(7) PAUSED(8)，失败时 isError=true，structuredContent.error.code 给出错误码"


def tool_description(cmd) -> str:
    d = f"{cmd.summary}。CLI：{cmd.usage()}"
    if cmd.description:
        d += f"。{cmd.description}"
    if cmd.limits:
        d += "。限制：" + "；".join(cmd.limits)
    if cmd.examples:
        d += "。示例：" + cmd.examples[0]
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


def mcp_tools(profile: str = "full", apps: list[str] | None = None, names: str = "underscore") -> list[dict]:
    out = []
    for c in select_commands(profile, apps):
        t = {"name": c.id if names == "dotted" else c.tool_name, "title": c.cli, "description": tool_description(c),
             "inputSchema": c.input_schema(),
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
