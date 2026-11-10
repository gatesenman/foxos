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


def tool_description(cmd) -> str:
    d = f"{cmd.summary}。CLI：{cmd.usage()}"
    if cmd.limits:
        d += "。限制：" + "；".join(cmd.limits)
    return d


def mcp_tools() -> list[dict]:
    load_apps()
    return [
        {"name": c.tool_name, "title": c.cli, "description": tool_description(c), "inputSchema": c.input_schema()}
        for c in REGISTRY.values()
    ]


def openai_tools() -> list[dict]:
    return [
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["inputSchema"]}}
        for t in mcp_tools()
    ]
