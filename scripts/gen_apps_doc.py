#!/usr/bin/env python3
"""生成 docs/everything-apps.md（51 个 Everything 应用：分组、许可证、本机运行、语义命令数、端到端测试结果）。

数据来源：foxos everything list（目录与已安装状态，读取 FOXOS_HOME）、data/ops/<app>.json（操作清单）、
docs/test-results/everything.json（everything.e2e.js 写入的启动 / 界面与命令等价测试结果）。
用法：FOXOS_HOME=<含已安装应用的目录> python scripts/gen_apps_doc.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "packages" / "core"


def everything_list():
    env = {**os.environ, "PYTHONPATH": str(CORE), "FOXOS_LANG": "zh-CN"}
    out = subprocess.run([sys.executable, "-m", "foxos", "everything", "list", "--json"], capture_output=True, text=True, env=env, check=True).stdout
    return json.loads(out)["result"]


def ops_info(app):
    f = CORE / "foxos" / "data" / "ops" / f"{app}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text(encoding="utf-8"))
    ops = d.get("ops") or []
    return {"total": len(ops), "semantic": sum(1 for o in ops if o.get("kind", "semantic") != "ui"), "inventory": d}


def results():
    f = ROOT / "docs" / "test-results" / "everything.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


LABEL = {"ok": "通过", "fail": "失败", "error": "失败", "same": "一致", "equal": "一致", "different": "不一致", "skip": "跳过", None: "—"}


def build():
    d = everything_list()
    res = results()
    rows, cov = [], {"total": len(d["apps"]), "local": 0, "cli": 0, "boot": 0, "parity": 0}
    for g in d["groups"]:
        for a in [x for x in d["apps"] if x["group"] == g["id"]]:
            upstream_issue = a["id"] == "assets" or a.get("upstreamIssue")
            r = res.get(a["id"], {})
            if not upstream_issue:
                cov["local"] += 1
            if a.get("ops"):
                cov["cli"] += 1
            if r.get("boot") == "ok":
                cov["boot"] += 1
            if r.get("parity") in ("same", "equal"):
                cov["parity"] += 1
            rows.append({**a, "group": g["zh"], "group_id": g["id"], "upstream_issue": bool(upstream_issue), "boot": r.get("boot"), "parity": r.get("parity"), "op": r.get("cli")})
    return d, rows, cov


def uilang(r):
    ui = "中文 / 英文" if "zh-CN" in (r.get("ui_languages") or []) else "英文"
    return ui + {"follows": "，格式跟随", "en-US": "，格式固定英文"}.get(r.get("locale_formats"), "")


def main():
    d, rows, cov = build()
    lines = ["# Everything 应用（51 个）", "",
             f"上游：[HeyPuter/everything]({d['upstream']}) 提交 `{d['commit'][:8]}`。"
             "AGPL 许可的应用在安装时从上游源码在本机构建，狐狸OS 不修改、不内置其源码；其余为 MIT。",
             "", "每个应用：本机运行（`foxapp://` + 本地 Puter 运行时）、打开 / 保存工作空间文件、`foxos <应用> …` 语义命令与同名 MCP 工具、"
             "用户故事 US-40…48（按分组）与端到端测试（启动 + 一次界面操作与等价 CLI 命令的结果对比）。", "",
             f"覆盖：本机可运行 **{cov['local']}/{cov['total']}**，有语义命令 **{cov['cli']}/{cov['total']}**，"
             f"启动测试通过 **{cov['boot']}/{cov['total']}**，界面与命令等价 **{cov['parity']}/{cov['total']}**。", "",
             "| 分组 | 应用 | ID | 许可证 | 本机运行 | 语义命令 | 启动测试 | 界面 = 命令 | 等价测试用的命令 | 界面语言 | 操作清单 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['group']} | {r['name']} | `{r['id']}` | {r['license']} | {'上游缺源码' if r['upstream_issue'] else '可运行'} | {r.get('ops') or 0} | "
                     f"{LABEL.get(r['boot'], r['boot'])} | {LABEL.get(r['parity'], r['parity'])} | {('`' + r['op'] + '`') if r['op'] else '—'} | {uilang(r)} | "
                     f"[{r['id']}.md](operations/{r['id']}.md) |")
    lines += ["", "说明：", "",
              "- `assets` 的上游仓库缺少 `src/main.js`，无法构建（GitHub contents API 返回 404），如实标为“上游缺源码”，不计入可运行数。",
              "- “语义命令”是从界面实际遍历 + 快捷键挖掘得到的操作数（`foxos <应用> <资源> <动作>`），清单见 `docs/operations/`。",
              "- “界面语言”：上游应用自带的界面语言。狐狸OS 把自己的语言通过 Chromium 语言（`navigator.language`）传给每个应用；"
              "上游提供中文界面的（目前只有 spreadsheet）随狐狸OS 切换中 / 英文；其余是英文界面，标“格式跟随”的应用的日期与数字按狐狸OS 语言显示。"
              "数据来自扫描上游源码（`packages/core/foxos/data/everything-locale.json`），spreadsheet 由 US-55 端到端测试验证。",
              "- 测试结果来自 `docs/test-results/everything.json`，由 `npm run test:all` 中的 everything.e2e.js 写入。", ""]
    (ROOT / "docs" / "everything-apps.md").write_text("\n".join(lines), encoding="utf-8")
    json.dump({"coverage": cov, "apps": [{k: r[k] for k in ("id", "name", "group", "group_id", "license", "upstream_issue", "ops", "boot", "parity")} for r in rows]},
              open(ROOT / "docs" / "test-results" / "apps.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    readme_tables(d, rows, cov)
    print(json.dumps(cov, ensure_ascii=False))


def readme_tables(d, rows, cov):
    """更新 README.md / README.en.md 中 <!-- apps:start --> … <!-- apps:end --> 之间的应用表。"""
    import re
    for fn, en in (("README.md", False), ("README.en.md", True)):
        f = ROOT / fn
        if not f.exists():
            continue
        out = [("| Group | Apps (ops = semantic commands) |" if en else "| 分组 | 应用（括号内为语义命令数） |"), "| --- | --- |"]
        for g in d["groups"]:
            items = []
            for r in [x for x in rows if x["group_id"] == g["id"]]:
                mark = (" — upstream source missing" if en else " — 上游缺源码") if r["upstream_issue"] else ""
                lic = " · AGPL" if r.get("agpl") else ""
                items.append(f"{r['name']} `{r['id']}` ({r.get('ops') or 0}{lic}){mark}")
            out.append(f"| {g['en'] if en else g['zh'] + ' ' + g['en']} | " + "<br>".join(items) + " |")
        summary = (f"Runs locally: **{cov['local']}/{cov['total']}** · semantic CLI/MCP commands: **{cov['cli']}/{cov['total']}** · "
                   f"boot e2e passed: **{cov['boot']}/{cov['total']}** · GUI = CLI parity: **{cov['parity']}/{cov['total']}** (details: [docs/everything-apps.md](docs/everything-apps.md))"
                   if en else
                   f"本机可运行 **{cov['local']}/{cov['total']}** · 有语义命令（CLI / MCP）**{cov['cli']}/{cov['total']}** · "
                   f"启动测试通过 **{cov['boot']}/{cov['total']}** · 界面与命令等价 **{cov['parity']}/{cov['total']}**（明细：[docs/everything-apps.md](docs/everything-apps.md)）")
        block = "<!-- apps:start -->\n" + summary + "\n\n" + "\n".join(out) + "\n<!-- apps:end -->"
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"<!-- apps:start -->.*?<!-- apps:end -->", lambda m: block, text, flags=re.S)
        f.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
