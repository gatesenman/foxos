"""foxos 命令行：参数由命令注册表生成，执行统一走 kernel.invoke()。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from . import i18n

i18n.init_from_argv(sys.argv[1:])  # 命令说明在导入注册表时取词，必须先确定语言（--lang / FOXOS_LANG）
from . import __version__, catalog  # noqa: E402
from .errors import EXIT_CODE_DOCS, FoxError  # noqa: E402
from .kernel import APPS, REGISTRY, Context, find, invoke, load_apps  # noqa: E402
from .workspace import Workspace  # noqa: E402
from .i18n import tr  # noqa: E402

DEST = "p_"  # 命令参数在 argparse 命名空间里的前缀，避免与全局选项（--agent 等）冲突
_INT = re.compile(r"^[+-]?\d+$")
_FLOAT = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # 统一成 USAGE 错误，--json 时也能输出结构化结果
        raise FoxError("USAGE", message, hint=tr("cli.run_help_for_usage", self.prog))


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
        raise FoxError("USAGE", tr("cli.not_valid_json", e)) from e


def parse_kv(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        if "=" not in it:
            raise FoxError("USAGE", tr("cli.expected_cell_value", it), hint=tr("cli.e_g_a1_month_or_b5_sum_b2_b4"))
        k, v = it.split("=", 1)
        if not k:
            raise FoxError("USAGE", tr("cli.missing_the_cell_address", it))
        out[k] = coerce_cell_value(v)
    return out


def _globals(suppress: bool) -> argparse.ArgumentParser:
    g = argparse.ArgumentParser(add_help=False)
    d = (lambda v: argparse.SUPPRESS) if suppress else (lambda v: v)
    g.add_argument("--json", action="store_true", default=d(False), help=tr("cli.json_output"))
    g.add_argument("--workspace", "-w", default=d(None), metavar="PATH", help=tr("cli.workspace_root"))
    g.add_argument("--agent", default=d(None), metavar="NAME", help=tr("cli.caller_identity_written_to_the_audit"))
    g.add_argument("--task", default=d(None), metavar="ID", help=tr("cli.related_task_id"))
    g.add_argument("--lang", default=d(None), metavar="LANG", help=tr("cli.lang_option"))
    g.add_argument("--machine", "-m", default=d(None), metavar="NAME", help=tr("catalog.machine_option"))
    g.add_argument("--lock-wait", type=float, default=d(0.0), metavar="SECONDS", help=tr("cli.seconds_to_wait_for_a_file_lock"))
    return g


def _epilog(cmd) -> str:
    parts = []
    if cmd.examples:
        parts.append(tr("cli.examples") + "\n".join("  " + e for e in cmd.examples))
    if cmd.limits:
        parts.append(tr("cli.limits") + "\n".join("  - " + l for l in cmd.limits))
    parts.append(tr("cli.exit_codes") + "  ".join(f"{k}={v.split(tr("cli.text"))[0]}" for k, v in EXIT_CODE_DOCS.items()))
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
                               help=tr("cli.pass_as_a_json_object", prm.name))
                continue
            if prm.type == "array":
                kw["nargs"] = "*" if not prm.required else "+"
            elif not prm.required or prm.cli_stdin:
                kw["nargs"] = "?"
            if prm.cli_stdin:  # 位置参数也可以从标准输入读（大文本、密钥）：--<name>-stdin
                p.add_argument(f"--{prm.name.replace('_', '-')}-stdin", dest=f"{DEST}{prm.name}__stdin",
                               action="store_true", help=tr("cli.read_from_standard_input", prm.name))
            p.add_argument(DEST + prm.name, metavar=prm.metavar or prm.name.upper(), **kw)
            continue
        flags = [prm.flag] + ([prm.cli_short] if prm.cli_short else [])
        kw["dest"] = DEST + prm.name
        if prm.cli_kv:  # --rule KEY=VALUE 可重复
            p.add_argument(*flags, action="append", metavar="KEY=VALUE", **kw)
            p.add_argument(f"--{prm.name.replace('_', '-')}-json", dest=f"{DEST}{prm.name}__json", metavar="JSON",
                           help=tr("cli.pass_as_a_json_object", prm.name))
            continue
        if prm.type == "boolean":
            # 没有默认值的布尔参数是「三态」：--x 设为真，--no-x 设为假，不写则不改（如 bot config set --no-pinned）
            p.add_argument(*flags, action=argparse.BooleanOptionalAction if prm.default is None else "store_true", default=None, **kw)
        elif prm.type == "array" and (prm.items or {}).get("type") in ("array", "object"):
            p.add_argument(f"--{prm.name.replace('_', '-')}-json", dest=DEST + prm.name, metavar="JSON",
                           type=_json_arg, help=prm.description)
        elif prm.type == "array" and prm.cli_repeat:
            kw["metavar"] = prm.metavar or prm.name.upper()
            p.add_argument(*flags, action="append", **kw)
        else:
            if prm.cli_stdin:
                p.add_argument(f"--{prm.name.replace('_', '-')}-stdin", dest=f"{DEST}{prm.name}__stdin",
                               action="store_true", help=tr("cli.read_from_standard_input", prm.name))
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
        description=tr("cli.foxos_command_line_one_set_of"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[_globals(False)],
    )
    top.add_argument("--version", action="version", version=f"foxos {__version__}")
    apps = top.add_subparsers(dest="_app", metavar="<app>", parser_class=_Parser)

    h = apps.add_parser("help", help=tr("cli.capability_catalog_json_prints_a"), parents=parents)
    h.add_argument("app", nargs="?", help=tr("cli.only_one_app"))
    h.set_defaults(_special="help")
    t = apps.add_parser("tools", help=tr("cli.export_tool_definitions_json_schema"), parents=parents)
    t.add_argument("--format", choices=["mcp", "openai"], default="mcp")
    t.set_defaults(_special="tools")
    m = apps.add_parser("mcp", help=tr("cli.run_as_an_mcp_server_stdio_by"), parents=parents)
    m.add_argument("--http", metavar="HOST:PORT", help=tr("cli.use_streamable_http_and_listen_on"))
    m.add_argument("--token", help=tr("cli.bearer_token_required_in_http_mode"))
    m.add_argument("--profile", choices=["compact", "full"], default=os.environ.get("FOXOS_MCP_PROFILE", "compact"),
                   help=tr("cli.compact_all_built_in_app_tools"))
    m.add_argument("--apps", help=tr("cli.also_expose_all_tools_of_these"))
    m.add_argument("--tool-names", choices=["underscore", "dotted"], default="underscore",
                   help=tr("cli.tool_name_format_underscore_tasks"))
    m.set_defaults(_special="mcp")
    t2 = apps.add_parser("agent-guide", help=tr("cli.print_the_agent_guide_docs_agent"), parents=parents)
    t2.set_defaults(_special="agent-guide")

    app_subs = {}
    for app, meta in APPS.items():
        cmds = [c for c in REGISTRY.values() if c.app == app]
        desc = meta["summary"] + ("\n\n" + meta["description"] if meta["description"] else "")
        desc += tr("cli.commands") + "\n".join(f"  {c.usage()}\n      {c.summary}" for c in cmds)
        if meta["limits"]:
            desc += tr("cli.limits_2") + "\n".join("  - " + l for l in meta["limits"])
        ap = apps.add_parser(app, help=meta["summary"], description=desc,
                             formatter_class=argparse.RawDescriptionHelpFormatter, parents=parents)
        asub = ap.add_subparsers(dest="_sub", metavar="<command>", parser_class=_Parser)
        app_subs[app] = asub
        groups: dict = {}
        for c in cmds:
            words = c.name.split()
            target = asub
            if len(words) == 2:
                if words[0] not in groups:
                    gp = asub.add_parser(words[0], help=tr("cli.subcommands", words[0]), parents=parents)
                    groups[words[0]] = gp.add_subparsers(dest="_sub2", metavar="<command>", parser_class=_Parser)
                target = groups[words[0]]
            _add_command(target, c, parents)
    if "bot" in app_subs:
        bs = app_subs["bot"].add_parser("serve", help=tr("cli.bot_serve"), parents=parents)
        bs.add_argument("--listen", default="127.0.0.1:0", metavar="HOST:PORT")
        bs.add_argument("--token", default=None, help=tr("cli.bot_serve_token"))
        bs.add_argument("--open", action="store_true", help=tr("cli.bot_serve_open"))
        bs.add_argument("--ready-file", default=None, metavar="PATH", help=tr("cli.bot_serve_ready"))
        bs.set_defaults(_special="bot-serve")
    if "machine" in app_subs:
        ms = app_subs["machine"].add_parser("serve", help=tr("cli.machine_serve"), parents=parents)
        ms.add_argument("--listen", default="0.0.0.0:7443", metavar="HOST:PORT")
        ms.add_argument("--name", default=None)
        ms.set_defaults(_special="machine-serve")
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
                print(tr("cli.formulas") + "  ".join(formulas), file=out)
        if result.get("note"):
            print("# " + result["note"], file=out)
    if "charts" in result:
        for c in result["charts"]:
            print(tr("cli.chart", c['index'], c.get('sheet', ''), c['type'], c['anchor'], c.get('title') or '')
                  + ", ".join(s["values"] or "" for s in c["series"]), file=out)
    if cmd_id in ("env.exec", "env.action.run"):
        sys.stdout.write(result["stdout"])
        sys.stderr.write(result["stderr"])
        if result["exit_code"]:
            print(tr("cli.exit_code", result['exit_code']), file=sys.stderr)
    if cmd_id == "env.list":
        for e in result["envs"]:
            print(tr("cli.network_workspace", e['state'], e['name'], e['image'], e['network'], e['workspace']['mode']), file=out)
    if cmd_id == "everything.list":
        for a in result["apps"]:
            print(tr("cli.ops", tr("cli.installed") if a['installed'] else tr("cli.not_installed"), a['group_name'], a['id'], a['name'], a['license'], a['ops']), file=out)
        print(tr("cli.in_total_installed_upstream", result['count'], result['installed'], result['commit'][:8]), file=out)
    if cmd_id.endswith(".ui.snapshot"):
        print(f"# {result['title']}  {result['url']}", file=out)
        for e in result["elements"]:
            print(f"[{e['ref']}] {e['role']:<10} {e['name']}" + (f" = {e['value']!r}" if e.get("value") not in (None, "") else "") + (tr("cli.disabled") if e.get("disabled") else ""), file=out)
    if cmd_id in ("desktop.windows", "session.windows"):
        wins = result.get("windows") or []
        if not wins:
            print(tr("cli.no_windows"), file=out)
        for w in wins:
            mark = "*" if w.get("focused") else " "
            geo = f"{w.get('width', 0)}x{w.get('height', 0)}+{w.get('x', 0)}+{w.get('y', 0)}"
            app = w.get("app_id") or w.get("host") or ""
            print(f"{mark} {w['id']:<12} {geo:<20} {app:<20} {w.get('title', '')}", file=out)
    if cmd_id in ("desktop.status", "session.status"):
        for k in ("backend", "compositor", "display", "wayland_display", "windows", "paused", "takeover"):
            if result.get(k) not in (None, ""):
                v = result[k]
                print(f"  {k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}", file=out)
        tools = result.get("tools") or {}
        if tools:
            print("  tools: " + ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in tools.items()), file=out)
    if cmd_id == "browser.status":
        cdp = result.get("cdp") or {}
        print(f"  chrome: {result.get('version') or (result.get('binary') or tr('browser.chrome_not_installed'))}", file=out)
        print(f"  cdp: {'on' if cdp.get('enabled') else 'off'}  {cdp.get('address')}:{cdp.get('port')}  running={'yes' if cdp.get('running') else 'no'}", file=out)
    if cmd_id == "browser.tabs":
        for tb in result.get("tabs") or []:
            print(f"  {tb['id']}  {tb.get('title') or ''}  {tb.get('url') or ''}", file=out)
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
    if cmd_id in ("bot.message.send", "bot.skill.run"):
        r = result["reply"]
        for c in r.get("cards") or []:
            ap = (c.get("approval") or {}).get("decision")
            print(f"  [{c.get('type')}:{c.get('kind') or c.get('to') or ''}] {c.get('title') or c.get('to_name') or ''} {c.get('status') or ''}"
                  + (f" ({ap})" if ap else "") + (f" @{c['machine']}" if c.get("machine") and c["machine"] != "local" else ""), file=out)
        if r.get("skills_used"):
            print("  skills: " + ", ".join(r["skills_used"]), file=out)
        print(r.get("text", ""), file=out)
        return
    if cmd_id.split(".")[0] in ("bot", "connector", "machine", "runtime", "acp") and not result.get("message"):
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str), file=out)
        return
    skip = {"message", "rows", "values", "charts", "files", "entries", "tasks", "note", "content", "stdout", "stderr", "apps", "envs", "elements"}
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
        print(tr("cli.foxos_error", e.code, e.message), file=sys.stderr)
        if e.hint:
            print(tr("cli.hint", e.hint), file=sys.stderr)
    return e.exit_code


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    i18n.init_from_argv(argv)
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
                print(tr("cli.run_foxos_app_help_for_details_foxos"))
            return 0
        if special == "agent-guide":
            from .agent_guide import guide
            g = guide()
            if as_json:
                print(json.dumps(g, ensure_ascii=False, indent=2))
            else:
                print(g["markdown"])
            return 0
        if special == "tools":
            tools = catalog.mcp_tools() if ns.format == "mcp" else catalog.openai_tools()
            print(json.dumps(tools, ensure_ascii=False, indent=2))
            return 0
        ws = Workspace(ns.workspace)
        agent = ns.agent or os.environ.get("FOXOS_AGENT") or "human"
        task = ns.task or os.environ.get("FOXOS_TASK")
        if special == "bot-serve":
            from .botchat.server import serve as bot_serve
            host, _, port = ns.listen.rpartition(":")
            return bot_serve(ws, host or "127.0.0.1", int(port or 0), token=ns.token or os.environ.get("FOXOS_BOTS_TOKEN"),
                             open_ui=ns.open, ready_file=ns.ready_file)
        if special == "machine-serve":
            from .machines import serve as machine_serve
            host, _, port = ns.listen.rpartition(":")
            return machine_serve(ws, host or "0.0.0.0", int(port or 7443), name=ns.name)
        if special == "mcp":
            from .mcp_server import serve, serve_http
            kw = dict(agent_default=ns.agent or os.environ.get("FOXOS_AGENT"), task=task, profile=ns.profile,
                      apps=[a.strip() for a in (ns.apps or "").split(",") if a.strip()] or None, names=ns.tool_names)
            if ns.http:
                host, _, port = ns.http.rpartition(":")
                return serve_http(ws, host or "127.0.0.1", int(port or 0), token=ns.token or os.environ.get("FOXOS_MCP_TOKEN"), **kw)
            return serve(ws, **kw)
        cmd_id = getattr(ns, "_cmd", None)
        if not cmd_id:
            sub = [a for a in argv if not a.startswith("-")][:2]
            parser.parse_args(sub + ["--help"])
            return 2
        cmd = find(cmd_id)
        params = {}
        for p in cmd.params:
            if p.cli_kv:
                raw_kv = getattr(ns, DEST + p.name, None) or []
                merged = {k: (v if not isinstance(v, (int, float, bool)) or p.name != "roles" else str(v)) for k, v in parse_kv(raw_kv).items()}
                raw_json = getattr(ns, f"{DEST}{p.name}__json", None)
                if raw_json:
                    try:
                        extra = json.loads(raw_json)
                    except json.JSONDecodeError as e:
                        raise FoxError("USAGE", tr("cli.json_is_not_valid_json", p.name, e)) from e
                    if not isinstance(extra, dict):
                        raise FoxError("USAGE", tr("cli.json_must_be_a_json_object", p.name))
                    merged.update(extra)
                if merged:
                    params[p.name] = merged
                continue
            v = getattr(ns, DEST + p.name, None)
            if p.cli_stdin and getattr(ns, f"{DEST}{p.name}__stdin", False):
                v = sys.stdin.buffer.read().decode("utf-8")
            if v is None or (p.positional and p.type == "array" and v == []):
                continue
            if isinstance(v, str) and (p.type == "object" or (p.type == "array" and v.lstrip().startswith("["))):
                try:
                    v = json.loads(v)
                except ValueError as e:
                    raise FoxError("USAGE", tr("cli.parameter_needs_json", p.name, e)) from e
            if p.type == "array" and isinstance(v, str):
                v = [s.strip() for s in v.split(",") if s.strip()]
            if p.type == "array" and p.items and p.items.get("type") in ("number", "integer"):
                try:
                    v = [float(x) if p.items["type"] == "number" else int(x) for x in v]
                except ValueError as e:
                    raise FoxError("USAGE", tr("cli.elements_of_parameter_must_be", p.name, e)) from e
            params[p.name] = v
        ctx = Context(ws, agent=agent, task=task, lock_wait=ns.lock_wait, interface="cli")
        machine = getattr(ns, "machine", None) or os.environ.get("FOXOS_MACHINE")
        if machine and machine != "local" and cmd.app not in catalog.NO_MACHINE_PARAM:
            from . import machines
            result = machines.invoke(ws, machine, cmd.id, params, agent, task, interface="cli")
        else:
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
        return _emit_error(FoxError("ERROR", tr("cli.internal_error", type(e).__name__, e)), as_json, cmd_id)


if __name__ == "__main__":
    sys.exit(main())
