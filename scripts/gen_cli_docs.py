#!/usr/bin/env python3
"""从命令注册表生成参考文档（与 foxos help --json、MCP tools/list 同源）。

生成：docs/cli-reference.md、docs/mcp-reference.md、docs/agent-guide.md。
--check：只比较，不写入；任何一个文件与代码不一致时退出码非 0（测试与 CI 用它防止文档漂移）。
"""

import json
import os
import sys
from pathlib import Path

os.environ["FOXOS_LANG"] = "zh-CN"  # 参考文档固定用默认语言（中文）生成

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "core"))

from foxos.catalog import catalog  # noqa: E402

cat = catalog()
from foxos.catalog import everything_ids, mcp_tools  # noqa: E402
from foxos.agent_guide import guide  # noqa: E402

EV = everything_ids()
EV_GENERIC = {"app open", "app close", "app status", "app reset", "file open", "ui snapshot", "ui text", "ui click", "ui type", "ui set", "ui press",
              "ui screenshot", "data list", "data get", "module list", "module read", "module call", "op list"}
lines = ["# foxos 命令参考", "", "> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos help --json` 同源，请勿手改。", ""]
lines += ["## 通用约定", ""]
for k, v in cat["conventions"].items():
    if isinstance(v, dict):
        lines.append(f"- **{k}**")
        lines += [f"  - `{kk}`：{vv}" if kk.startswith("-") else f"  - {kk}：{vv}" for kk, vv in v.items()]
    else:
        lines.append(f"- **{k}**：{v}")
lines.append("")
ev_apps = [a for a in cat["apps"] if a["commands"] and a["commands"][0]["id"].split(".")[0] in EV]
for app in [a for a in cat["apps"] if a not in ev_apps] + ev_apps[:1]:
    if app in ev_apps:
        lines += ["## Everything 应用的通用命令（每个应用都有）", "", f"以下以 `{app['commands'][0]['id'].split('.')[0]}` 为例，把应用 ID 换成任意 Everything 应用即可。", ""]
        app = {**app, "commands": [c for c in app["commands"] if " ".join(c["id"].split(".")[1:]).replace(".", " ") in EV_GENERIC]}
    lines += [f"## {app['name']} — {app['summary']}", ""]
    if app["description"]:
        lines += [app["description"], ""]
    if app["limits"]:
        lines += ["限制：", ""] + [f"- {l}" for l in app["limits"]] + [""]
    for c in app["commands"]:
        lines += [f"### `{c['cli']}`", "", c["summary"], "", f"```text\n{c['usage']}\n```", "",
                  f"工具接口名：`{c['tool']}` · 权限：`{c['permission']}`", "",
                  "| 参数 | CLI | 类型 | 必填 | 说明 |", "|---|---|---|---|---|"]
        for p in c["params"]:
            extra = []
            if p.get("enum"):
                extra.append("可选：" + " / ".join(map(str, p["enum"])))
            if p.get("default") not in (None, False):
                extra.append(f"默认 {p['default']}")
            if p.get("path_access"):
                extra.append(f"工作空间路径（{p['path_access']}）")
            desc = p["description"].replace("|", "\\|") + ("；" + "；".join(extra) if extra else "")
            cli = p["cli"] + (f" / {p['short']}" if p.get("short") else "")
            lines.append(f"| `{p['name']}` | `{cli}` | {p['type']} | {'是' if p['required'] else ''} | {desc} |")
        if not c["params"]:
            lines.append("| — | | | | 无参数 |")
        lines.append("")
        if c["examples"]:
            lines += ["示例：", "", "```bash"] + c["examples"] + ["```", ""]
        if c["limits"]:
            lines += ["限制：", ""] + [f"- {l}" for l in c["limits"]] + [""]
lines += ["## Everything 应用的语义命令", "",
          "每个应用的语义命令来自操作清单（`packages/core/foxos/data/ops/<应用>.json`，界面路径与效果见 `docs/operations/<应用>.md`）。", ""]
for app in ev_apps:
    aid = app["commands"][0]["id"].split(".")[0]
    sem = [c for c in app["commands"] if " ".join(c["id"].split(".")[1:]) not in EV_GENERIC]
    lines += [f"### {app['name']}（`{aid}`，{len(sem)} 个语义命令）", ""]
    if sem:
        lines += ["| CLI | 工具接口名 | 权限 | 说明 |", "|---|---|---|---|"]
        for c in sem:
            lines.append(f"| `{c['usage']}` | `{c['tool']}` | {c['permission']} | {c['summary'].replace('|', '/')} |")
    else:
        lines.append("（尚无语义命令：应用未安装或清单未生成，可用上面的通用命令操作。）")
    lines.append("")

# ---------------------------------------------------------------- MCP 参考
tools = mcp_tools("full")
m = ["# 狐狸OS MCP 工具参考", "", "> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos mcp` 的 tools/list 同源，请勿手改。", "",
     "## 连接与调用", "",
     "- stdio：`foxos --workspace <目录> mcp`；Streamable HTTP：`foxos --workspace <目录> mcp --http 127.0.0.1:8765 --token <令牌>`（POST /mcp）",
     "- `--profile compact`（默认）：内置应用全部工具 + Everything 元工具；`--apps a,b`：额外暴露这些应用的全部工具；`--profile full`：全部工具",
     "- `--tool-names dotted`：工具名用点分命令 ID（如 `tasks.add-task.set`），默认用下划线（`tasks_add-task_set`）",
     "",
     "## 返回格式（所有工具相同）", "",
     "成功：`isError=false`，`structuredContent` 为 `{\"ok\": true, \"command\": \"<命令 ID>\", \"result\": {...}}`，`content[0].text` 为同一 JSON 文本。",
     "",
     "失败：`isError=true`，`structuredContent` 为 `{\"ok\": false, \"command\": ..., \"error\": {\"code\": \"LOCKED\", \"exit_code\": 5, \"message\": ..., \"hint\": ..., \"details\": {...}}}`。",
     "",
     "错误码：USAGE(2) NOT_FOUND(3) PERMISSION_DENIED(4) LOCKED(5) DEPENDENCY_MISSING(6) CONFLICT(7) PAUSED(8) ERROR(1)。", "",
     f"共 {len(tools)} 个工具。", ""]
by_app: dict = {}
for t in tools:
    by_app.setdefault(t["_meta"]["foxos/id"].split(".")[0], []).append(t)
for aid, ts in by_app.items():
    if aid in EV and aid != sorted(EV & set(by_app))[0]:
        m += [f"## {aid}（{len(ts)} 个工具）", "", "通用工具同上例；语义工具：", "", "| 工具 | 只读 | 参数 |", "|---|---|---|"]
        for t in ts:
            if " ".join(t["_meta"]["foxos/id"].split(".")[1:]) in EV_GENERIC:
                continue
            props = t["inputSchema"]["properties"]
            req = set(t["inputSchema"].get("required", []))
            m.append(f"| `{t['name']}` | {'是' if t['annotations']['readOnlyHint'] else ''} | " + (", ".join(f"`{k}`{'*' if k in req else ''}: {v.get('type', 'any')}" for k, v in props.items()) or "—") + " |")
        m.append("")
        continue
    m += [f"## {aid}（{len(ts)} 个工具）", ""]
    for t in ts:
        props = t["inputSchema"]["properties"]
        req = set(t["inputSchema"].get("required", []))
        ex_args = {k: (v.get("enum") or [v.get("default")])[0] if (v.get("enum") or v.get("default") is not None) else {"string": "…", "integer": 1, "number": 1, "boolean": True, "array": [], "object": {}}.get(v.get("type"), "…")
                   for k, v in props.items() if k in req}
        m += [f"### `{t['name']}`", "", t["description"].replace("\n", " "), "",
              f"只读：{'是' if t['annotations']['readOnlyHint'] else '否'} · 破坏性：{'是' if t['annotations']['destructiveHint'] else '否'} · CLI：`{t['title']}`", ""]
        if props:
            m += ["| 参数 | 类型 | 必填 | 说明 |", "|---|---|---|---|"]
            for k, v in props.items():
                typ = v.get("type", "any")
                typ = "/".join(typ) if isinstance(typ, list) else typ
                extra = (" 可选：" + " / ".join(map(str, v["enum"]))) if v.get("enum") else ""
                m.append(f"| `{k}` | {typ} | {'是' if k in req else ''} | {(v.get('description') or '').replace('|', '/')}{extra} |")
            m.append("")
        m += ["调用示例：", "", "```json", json.dumps({"name": t["name"], "arguments": ex_args}, ensure_ascii=False), "```", ""]

outputs = {
    ROOT / "docs" / "cli-reference.md": "\n".join(lines),
    ROOT / "docs" / "mcp-reference.md": "\n".join(m) + "\n",
    ROOT / "docs" / "agent-guide.md": guide(portable=True)["markdown"],
}
stale = []
for out, text in outputs.items():
    rel = out.relative_to(ROOT)
    if "--check" in sys.argv:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            stale.append(str(rel))
    else:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {rel}")
if "--check" in sys.argv:
    if stale:
        sys.exit("以下文档与代码不一致，请运行 python scripts/gen_cli_docs.py：" + "、".join(stale))
    print("参考文档与命令注册表一致：" + "、".join(str(o.relative_to(ROOT)) for o in outputs))
