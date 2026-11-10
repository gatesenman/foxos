#!/usr/bin/env python3
"""从命令注册表生成 docs/cli-reference.md（与 foxos help --json 同源）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "core"))

from foxos.catalog import catalog  # noqa: E402

cat = catalog()
lines = ["# foxos 命令参考", "", "> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos help --json` 同源，请勿手改。", ""]
lines += ["## 通用约定", ""]
for k, v in cat["conventions"].items():
    if isinstance(v, dict):
        lines.append(f"- **{k}**")
        lines += [f"  - `{kk}`：{vv}" if kk.startswith("-") else f"  - {kk}：{vv}" for kk, vv in v.items()]
    else:
        lines.append(f"- **{k}**：{v}")
lines.append("")
for app in cat["apps"]:
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
out = ROOT / "docs" / "cli-reference.md"
text = "\n".join(lines)
if "--check" in sys.argv:
    if not out.exists() or out.read_text(encoding="utf-8") != text:
        sys.exit("docs/cli-reference.md 已过期，请运行 python scripts/gen_cli_docs.py")
    print("docs/cli-reference.md 与命令注册表一致")
else:
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}")
