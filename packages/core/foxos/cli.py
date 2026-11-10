"""foxos 命令行：参数由命令注册表生成，执行统一走 kernel.invoke()。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from . import __version__, catalog
from .errors import EXIT_CODE_DOCS, FoxError
from .kernel import APPS, REGISTRY, Context, find, invoke, load_apps
from .workspace import Workspace

DEST = "p_"  # 命令参数在 argparse 命名空间里的前缀，避免与全局选项（--agent 等）冲突
_INT = re.compile(r"^[+-]?\d+$")
_FLOAT = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # 统一成 USAGE 错误，--json 时也能输出结构化结果
        raise FoxError("USAGE", message, hint=f"运行 {self.prog} --help 查看用法")


def coerce_cell_value(raw: str):
    """CLI 中 CELL=VALUE 的值：数字自动识别，TRUE/FALSE 为布尔，空为清空，'前缀强制文本。"""
    if raw == "":
        return None
    if raw.startswith("'"):
        return raw[1:]
    if raw.upper() in ("TRUE", "FALSE"):
        return raw.upper() == "TRUE"
    if _INT.match(raw):
        return int(raw)
    if _FLOAT.match(raw):
        return float(raw)
    return raw


def _json_arg(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise FoxError("USAGE", f"不是合法 JSON：{e}") from e


def parse_kv(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        if "=" not in it:
            raise FoxError("USAGE", f"应为 CELL=VALUE 形式：{it}", hint="例如 A1=Month 或 B5==SUM(B2:B4)")
        k, v = it.split("=", 1)
        if not k:
            raise FoxError("USAGE", f"缺少单元格地址：{it}")
        out[k] = coerce_cell_value(v)
    return out


def _globals(suppress: bool) -> argparse.ArgumentParser:
    g = argparse.ArgumentParser(add_help=False)
    d = (lambda v: argparse.SUPPRESS) if suppress else (lambda v: v)
    g.add_argument("--json", action="store_true", default=d(False), help="JSON 输出")
    g.add_argument("--workspace", "-w", default=d(None), metavar="PATH", help="工作空间根目录")
    g.add_argument("--agent", default=d(None), metavar="NAME", help="调用者身份（写入审计日志）")
    g.add_argument("--task", default=d(None), metavar="ID", help="关联任务 ID")
    g.add_argument("--lock-wait", type=float, default=d(0.0), metavar="SECONDS", help="等待文件锁的秒数")
    return g


def _epilog(cmd) -> str:
    parts = []
    if cmd.examples:
        parts.append("示例：\n" + "\n".join("  " + e for e in cmd.examples))
    if cmd.limits:
        parts.append("限制：\n" + "\n".join("  - " + l for l in cmd.limits))
    parts.append("退出码：" + "  ".join(f"{k}={v.split('：')[0]}" for k, v in EXIT_CODE_DOCS.items()))
    return "\n\n".join(parts)


def _add_command(sub, cmd, parents):
    leaf_name = cmd.name.split()[-1]
    p = sub.add_parser(
        leaf_name, help=cmd.summary, description=cmd.summary + ("\n\n" + cmd.description if cmd.description else ""),
        epilog=_epilog(cmd), formatter_class=argparse.RawDescriptionHelpFormatter, parents=parents,
    )
    p.set_defaults(_cmd=cmd.id)
    for prm in cmd.params:
        kw: dict = {"help": prm.description}
        if prm.positional:
            if prm.cli_kv:
                p.add_argument(DEST + prm.name, nargs="*", metavar=prm.metavar, **kw)
                p.add_argument(f"--{prm.name.replace('_', '-')}-json", dest=f"{DEST}{prm.name}__json", metavar="JSON",
                               help=f"以 JSON 对象传入 {prm.name}")
                continue
            if prm.type == "array":
                kw["nargs"] = "*" if not prm.required else "+"
            elif not prm.required:
                kw["nargs"] = "?"
            p.add_argument(DEST + prm.name, metavar=prm.metavar or prm.name.upper(), **kw)
            continue
        flags = [prm.flag] + ([prm.cli_short] if prm.cli_short else [])
        kw["dest"] = DEST + prm.name
        if prm.type == "boolean":
            p.add_argument(*flags, action="store_true", default=None, **kw)
        elif prm.type == "array" and (prm.items or {}).get("type") in ("array", "object"):
            p.add_argument(f"--{prm.name.replace('_', '-')}-json", dest=DEST + prm.name, metavar="JSON",
                           type=_json_arg, help=prm.description)
        elif prm.type == "array" and prm.cli_repeat:
            kw["metavar"] = prm.metavar or prm.name.upper()
            p.add_argument(*flags, action="append", **kw)
        else:
            if prm.cli_stdin:
                p.add_argument(f"--{prm.name.replace('_', '-')}-stdin", dest=f"{DEST}{prm.name}__stdin",
                               action="store_true", help=f"从标准输入读取 {prm.name}")
            if prm.type == "integer":
                kw["type"] = int
            elif prm.type == "number":
                kw["type"] = float
            if prm.enum:
                kw["choices"] = prm.enum
            kw["metavar"] = prm.metavar or prm.name.upper()
            p.add_argument(*flags, **kw)
    return p


def build_parser() -> argparse.ArgumentParser:
    load_apps()
    parents = [_globals(True)]
    top = _Parser(
        prog="foxos",
        description="狐狸OS（FoxOS）命令行：智能体与人共用的统一命令。运行 foxos help --json 获取完整能力目录。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_globals(False)],
    )
    top.add_argument("--version", action="version", version=f"foxos {__version__}")
    apps = top.add_subparsers(dest="_app", metavar="<app>", parser_class=_Parser)

    h = apps.add_parser("help", help="能力目录（--json 输出机器可读目录）", parents=parents)
    h.add_argument("app", nargs="?", help="只看某个应用")
    h.set_defaults(_special="help")
    t = apps.add_parser("tools", help="导出工具定义（MCP / OpenAI function 格式的 JSON Schema）", parents=parents)
    t.add_argument("--format", choices=["mcp", "openai"], default="mcp")
    t.set_defaults(_special="tools")
    m = apps.add_parser("mcp", help="以 stdio MCP 服务器方式运行，向智能体暴露全部命令", parents=parents)
    m.set_defaults(_special="mcp")

    for app, meta in APPS.items():
        cmds = [c for c in REGISTRY.values() if c.app == app]
        desc = meta["summary"] + ("\n\n" + meta["description"] if meta["description"] else "")
        desc += "\n\n命令：\n" + "\n".join(f"  {c.usage()}\n      {c.summary}" for c in cmds)
        if meta["limits"]:
            desc += "\n\n限制：\n" + "\n".join("  - " + l for l in meta["limits"])
        ap = apps.add_parser(app, help=meta["summary"], description=desc,
                             formatter_class=argparse.RawDescriptionHelpFormatter, parents=parents)
        asub = ap.add_subparsers(dest="_sub", metavar="<command>", parser_class=_Parser)
        groups: dict = {}
        for c in cmds:
            words = c.name.split()
            target = asub
            if len(words) == 2:
                if words[0] not in groups:
                    gp = asub.add_parser(words[0], help=f"{words[0]} 子命令", parents=parents)
                    groups[words[0]] = gp.add_subparsers(dest="_sub2", metavar="<command>", parser_class=_Parser)
                target = groups[words[0]]
            _add_command(target, c, parents)
    return top


# ----------------------------------------------------------------------
def _fmt_cell(v) -> str:
    return "" if v is None else str(v)


def print_human(cmd_id: str, result: dict) -> None:
    out = sys.stdout
    if result.get("message"):
        print(result["message"], file=out)
    if "rows" in result:
        print(f"# {result['file']}!{result['sheet']} {result['range']}", file=out)
        grid = result.get("values", result["rows"])
        for r in grid:
            print("\t".join(_fmt_cell(v) for v in r), file=out)
        if result.get("values"):
            from openpyxl.utils.cell import get_column_letter, range_boundaries

            c0, r0, _, _ = range_boundaries(result["range"])
            formulas = [
                f"{get_column_letter(c0 + ci)}{r0 + ri}{v}"
                for ri, r in enumerate(result["rows"])
                for ci, v in enumerate(r)
                if isinstance(v, str) and v.startswith("=")
            ]
            if formulas:
                print("# 公式：" + "  ".join(formulas), file=out)
        if result.get("note"):
            print("# " + result["note"], file=out)
    if "charts" in result:
        for c in result["charts"]:
            print(f"chart[{c['index']}] {c.get('sheet', '')} {c['type']} @ {c['anchor']} 「{c.get('title') or ''}」 "
                  + ", ".join(s["values"] or "" for s in c["series"]), file=out)
    if cmd_id == "everything.list":
        for a in result["apps"]:
            print(f"{'已安装' if a['installed'] else '未安装'}  {a['group_name']:<4} {a['id']:<20} {a['name']:<22} {a['license']:<20} 操作 {a['ops']}", file=out)
        print(f"共 {result['count']} 个，已安装 {result['installed']} 个（上游 {result['commit'][:8]}）", file=out)
    if cmd_id.endswith(".ui.snapshot"):
        print(f"# {result['title']}  {result['url']}", file=out)
        for e in result["elements"]:
            print(f"[{e['ref']}] {e['role']:<10} {e['name']}" + (f" = {e['value']!r}" if e.get("value") not in (None, "") else "") + (" (禁用)" if e.get("disabled") else ""), file=out)
    if cmd_id == "files.list":
        for f in result["entries"]:
            print(f"{'<DIR>' if f['type'] == 'dir' else f['bytes']:>10}  {f['path']}{'/' if f['type'] == 'dir' else ''}", file=out)
    if cmd_id == "files.read":
        sys.stdout.write(result["content"])
    if cmd_id == "files.trash":
        for t in result["items"]:
            print(f"{t['trash_id']}  {t['path']}  ({t['deleted_by']})", file=out)
    if cmd_id in ("docs.read", "slides.read"):
        print(json.dumps({k: v for k, v in result.items() if k != "file"}, ensure_ascii=False, indent=2), file=out)
    if cmd_id == "audit.tail":
        for e in result["entries"]:
            tgt = ",".join(t["path"] for t in e.get("targets") or [])
            err = f" {e['error']['code']}" if e.get("error") else ""
            print(f"{e['ts']}  {e['agent']:<14} {e['status']:<6} {e['command']:<22} {tgt}{err}", file=out)
    if "tasks" in result and isinstance(result["tasks"], list):
        for t in result["tasks"]:
            print(f"{t['id']}  {t['status']:<8} {t['goal']}", file=out)
    skip = {"message", "rows", "values", "charts", "files", "entries", "tasks", "note", "content"}
    if cmd_id.startswith(("workspace", "sheets.create", "sheets.write", "sheets.chart.create", "sheets.export",
                          "docs.create", "docs.append", "docs.replace", "docs.export", "slides.create", "slides.add",
                          "slides.replace", "slides.export", "slides.chart", "files.write", "files.delete", "files.rename")):
        for k, v in result.items():
            if k in skip or v in (None, [], {}):
                continue
            print(f"  {k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}", file=out)


def _emit_error(e: FoxError, as_json: bool, cmd_id: str | None) -> int:
    if as_json:
        print(json.dumps({"ok": False, "command": cmd_id, "error": e.to_dict()}, ensure_ascii=False, indent=2))
    else:
        print(f"foxos: 错误 [{e.code}]：{e.message}", file=sys.stderr)
        if e.hint:
            print(f"提示：{e.hint}", file=sys.stderr)
    return e.exit_code


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    as_json = "--json" in argv
    cmd_id = None
    try:
        parser = build_parser()
        if not argv:
            parser.print_help()
            return 0
        ns = parser.parse_args(argv)
        as_json = bool(getattr(ns, "json", False))
        special = getattr(ns, "_special", None)
        if special == "help":
            cat = catalog.catalog(ns.app)
            if as_json:
                print(json.dumps(cat, ensure_ascii=False, indent=2))
            else:
                for a in cat["apps"]:
                    print(f"{a['name']}: {a['summary']}")
                    for c in a["commands"]:
                        print(f"  {c['usage']}\n      {c['summary']}")
                print("\n运行 foxos <app> --help 查看详情；foxos help --json 输出机器可读能力目录。")
            return 0
        if special == "tools":
            tools = catalog.mcp_tools() if ns.format == "mcp" else catalog.openai_tools()
            print(json.dumps(tools, ensure_ascii=False, indent=2))
            return 0
        ws = Workspace(ns.workspace)
        agent = ns.agent or os.environ.get("FOXOS_AGENT") or "human"
        task = ns.task or os.environ.get("FOXOS_TASK")
        if special == "mcp":
            from .mcp_server import serve
            return serve(ws, agent_default=ns.agent or os.environ.get("FOXOS_AGENT"), task=task)
        cmd_id = getattr(ns, "_cmd", None)
        if not cmd_id:
            sub = [a for a in argv if not a.startswith("-")][:2]
            parser.parse_args(sub + ["--help"])
            return 2
        cmd = find(cmd_id)
        params = {}
        for p in cmd.params:
            if p.cli_kv:
                merged = parse_kv(getattr(ns, DEST + p.name, None) or [])
                raw_json = getattr(ns, f"{DEST}{p.name}__json", None)
                if raw_json:
                    try:
                        extra = json.loads(raw_json)
                    except json.JSONDecodeError as e:
                        raise FoxError("USAGE", f"--{p.name}-json 不是合法 JSON：{e}") from e
                    if not isinstance(extra, dict):
                        raise FoxError("USAGE", f"--{p.name}-json 必须是 JSON 对象")
                    merged.update(extra)
                if merged:
                    params[p.name] = merged
                continue
            v = getattr(ns, DEST + p.name, None)
            if p.cli_stdin and getattr(ns, f"{DEST}{p.name}__stdin", False):
                v = sys.stdin.buffer.read().decode("utf-8")
            if v is None or (p.positional and p.type == "array" and v == []):
                continue
            if p.type == "array" and isinstance(v, str):
                v = [s.strip() for s in v.split(",") if s.strip()]
            if p.type == "array" and p.items and p.items.get("type") in ("number", "integer"):
                try:
                    v = [float(x) if p.items["type"] == "number" else int(x) for x in v]
                except ValueError as e:
                    raise FoxError("USAGE", f"参数 {p.name} 的元素必须是数字：{e}") from e
            params[p.name] = v
        ctx = Context(ws, agent=agent, task=task, lock_wait=ns.lock_wait, interface="cli")
        result = invoke(cmd.id, params, ctx)
        if as_json:
            print(json.dumps({"ok": True, "command": cmd.id, "result": result}, ensure_ascii=False, indent=2, default=str))
        else:
            print_human(cmd.id, result)
        return 0
    except FoxError as e:
        return _emit_error(e, as_json, cmd_id)
    except KeyboardInterrupt:
        return 130
    except Exception as e:  # 未预期的内部错误：同样遵守输出约定
        return _emit_error(FoxError("ERROR", f"内部错误：{type(e).__name__}: {e}"), as_json, cmd_id)


if __name__ == "__main__":
    sys.exit(main())
