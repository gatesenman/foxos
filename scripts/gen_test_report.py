#!/usr/bin/env python3
"""由测试结果生成 docs/test-report.md 与 docs/test-results/summary.json。

输入：build/test-results/*.xml（JUnit，test_all.py 写入）、docs/test-results/{everything,mcp,apps}.json、
packages/core/foxos/data/ops/*.json（操作清单）、scripts/stories.json（用户故事与测试的对应）。
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "build" / "test-results"
DOC = ROOT / "docs" / "test-report.md"
TR = ROOT / "docs" / "test-results"
LABEL = {"pass": "通过", "fail": "失败", "skip": "跳过", "known": "通过（含已知上游缺陷）", "none": "未运行"}


def cases() -> list[dict]:
    out = []
    for f in sorted(RES.glob("*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for tc in root.iter("testcase"):
            if f.stem == "pytest":
                suite, file = "pytest", tc.get("classname", "").split(".")[-1] + ".py"
            elif f.stem == "smoke":
                suite, file = "smoke", "smoke.sh"
            else:
                suite, file = "e2e", Path(tc.get("file") or f.stem).name
            sk = tc.find("skipped")
            failed = tc.find("failure") is not None or tc.find("error") is not None
            if sk is not None and sk.get("type") == "todo":
                status = "known" if failed else "pass"
            elif failed:
                status = "fail"
            elif sk is not None:
                status = "skip"
            else:
                status = "pass"
            msg = (sk.get("message") if sk is not None else None) or (tc.find("failure").get("message") if tc.find("failure") is not None else "")
            out.append({"suite": suite, "file": file, "name": tc.get("name", ""), "status": status, "time": float(tc.get("time") or 0), "message": (msg or "")[:300]})
    return out


def story_status(cs: list[dict]) -> str:
    if not cs:
        return "none"
    st = {c["status"] for c in cs}
    if "fail" in st:
        return "fail"
    if "known" in st:
        return "known"
    if "pass" in st:
        return "pass"
    return "skip"


def load(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=int, default=None)
    a = ap.parse_args()
    cs = cases()
    stories = load(ROOT / "scripts" / "stories.json", {"stories": []})["stories"]
    used = set()
    rows = []
    for s in stories:
        mine = []
        for suite, file, rx in s["match"]:
            for i, c in enumerate(cs):
                if c["suite"] == suite and c["file"] == file and re.search(rx, c["name"]):
                    mine.append(c)
                    used.add(i)
        cnt = {k: sum(1 for c in mine if c["status"] == k) for k in ("pass", "fail", "skip", "known")}
        rows.append({**{k: s[k] for k in ("id", "title")}, "status": story_status(mine), **cnt, "cases": mine})
    unassigned = [c for i, c in enumerate(cs) if i not in used]

    catalog = load(ROOT / "packages" / "core" / "foxos" / "data" / "everything.json", {"apps": []})["apps"]
    ev = load(TR / "everything.json", {})
    appsdoc = {x["id"]: x for x in load(TR / "apps.json", {"apps": []})["apps"]}
    mcp = load(TR / "mcp.json", {})
    apps = []
    for c in catalog:
        e = ev.get(c["id"], {})
        inv = load(ROOT / "packages" / "core" / "foxos" / "data" / "ops" / f"{c['id']}.json", {"ops": []})["ops"]
        bound = sum(1 for o in inv if o.get("binding"))
        case = next((x for x in cs if x["file"] == "everything.e2e.js" and re.search(rf" {re.escape(c['id'])}：", x["name"])), None)
        mcp_called = any(x.get("app") == c["id"] and x.get("ok") for x in (mcp.get("stdio") or {}).get("calls", []))
        apps.append({"id": c["id"], "name": c.get("name", c["id"]), "group": appsdoc.get(c["id"], {}).get("group", c.get("group")),
                     "installed": appsdoc.get(c["id"], {}).get("boot") is not None or e.get("boot") == "ok" or bool(inv),
                     "boot": e.get("boot"), "parity": e.get("parity"), "op": e.get("op"), "cli": e.get("cli"), "note": e.get("known") or e.get("note"),
                     "test": case["status"] if case else "none", "ops": len(inv), "bound": bound, "executed": 1 if e.get("op") else 0, "mcp": mcp_called})
    n = len(apps)
    cov = {"catalog": n, "boot_ok": sum(a["boot"] == "ok" for a in apps), "parity_equal": sum(a["parity"] == "equal" for a in apps),
           "test_pass": sum(a["test"] in ("pass", "known") for a in apps), "test_fail": sum(a["test"] == "fail" for a in apps),
           "test_skip": sum(a["test"] == "skip" for a in apps), "known": sum(a["test"] == "known" for a in apps),
           "ops": sum(a["ops"] for a in apps), "ops_bound": sum(a["bound"] for a in apps), "ops_executed": sum(a["executed"] for a in apps),
           "mcp_called": sum(a["mcp"] for a in apps)}
    tot = {k: sum(1 for c in cs if c["status"] == k) for k in ("pass", "fail", "skip", "known")}
    st = {k: sum(1 for r in rows if r["status"] == k) for k in LABEL}

    now = datetime.now(timezone(timedelta(hours=8)))
    commit = sh(["git", "rev-parse", "--short", "HEAD"])
    caps = {}
    try:
        sys.path.insert(0, str(ROOT / "packages" / "core"))
        from foxos import sandbox
        caps = sandbox.capabilities()
    except Exception:  # noqa: BLE001
        pass
    L = []
    L.append("# 测试报告\n")
    L.append(f"由 `npm run test:all`（[scripts/test_all.py](../scripts/test_all.py)）生成，不使用模拟：pytest 调用真实 CLI / 内核，桌面端到端测试用 Playwright 驱动真实的 Electron 桌面，MCP 测试使用官方 MCP SDK 作为客户端。\n")
    L.append(f"- 时间：{now:%Y-%m-%d %H:%M}（UTC+8）　提交：`{commit}`" + (f"　用时：{a.duration // 60} 分 {a.duration % 60} 秒" if a.duration else ""))
    L.append(f"- 环境：{platform.system()} {platform.release()}（{platform.machine()}），Python {platform.python_version()}，Node {sh(['node', '--version'])}"
             + (f"，Landlock ABI {caps.get('landlock_abi')}" if caps.get("landlock_abi") else ""))
    L.append("- 未覆盖：Windows 与 macOS 实机（本报告在 Linux 上生成；Windows 代码路径另有 wine 下的测试，见 [sandbox.md](sandbox.md)、[windows-test-guide.md](windows-test-guide.md)）\n")
    L.append("## 总览\n")
    L.append("| | 通过 | 失败 | 跳过 | 已知上游缺陷 |\n| --- | --- | --- | --- | --- |")
    L.append(f"| 测试用例（{len(cs)}） | {tot['pass']} | {tot['fail']} | {tot['skip']} | {tot['known']} |")
    L.append(f"| 用户故事（{len(rows)}） | {st['pass']} | {st['fail']} | {st['skip']} | {st['known']} |\n")
    L.append(f"- Everything 应用：**{cov['boot_ok']}/{n}** 在桌面里本地启动，**{cov['parity_equal']}/{n}** 通过“界面操作与 CLI 等价”检查，"
             f"**{cov['mcp_called']}/{n}** 通过 MCP（官方 SDK）调用成功；{cov['test_fail']} 个失败，{cov['test_skip']} 个跳过，{cov['known']} 个为已知上游缺陷。")
    L.append(f"- 操作清单：{n} 个应用共 **{cov['ops']}** 项操作，其中 **{cov['ops_bound']}** 项有 CLI / MCP 绑定；测试中实际执行并比对结果的有 **{cov['ops_executed']}** 项（每个应用一项等价检查）。")
    if mcp.get("stdio"):
        m = mcp["stdio"]
        L.append(f"- MCP：stdio 列出 {m.get('tools')} 个工具（{m.get('apps')} 个应用），逐应用调用 {sum(1 for c in m.get('calls', []) if c.get('ok'))}/{len(m.get('calls', []))} 成功；"
                 f"Streamable HTTP（compact）{(mcp.get('http') or {}).get('tools')} 个工具；SDK {m.get('sdk')}。")
    L.append("")
    L.append("## 用户故事\n")
    L.append("| 故事 | 内容 | 结果 | 通过 | 失败 | 跳过 |\n| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        L.append(f"| {r['id']} | {r['title']} | {LABEL[r['status']]} | {r['pass'] + r['known']} | {r['fail']} | {r['skip']} |")
    L.append("")
    bad = [(r["id"], c) for r in rows for c in r["cases"] if c["status"] in ("fail", "skip", "known")]
    if bad:
        L.append("### 失败、跳过与已知缺陷的用例\n")
        L.append("| 故事 | 用例 | 结果 | 说明 |\n| --- | --- | --- | --- |")
        for sid, c in bad:
            L.append(f"| {sid} | `{c['file']}` {c['name']} | {LABEL[c['status']]} | {c['message'].replace('|', '/').replace(chr(10), ' ')[:220]} |")
        L.append("")
    if unassigned:
        L.append(f"未归入故事的用例：{len(unassigned)} 个（{', '.join(sorted({c['file'] for c in unassigned}))}）\n")
    L.append(f"## Everything 应用覆盖（{n} 个）\n")
    L.append("等价检查：同一个操作分别用真实鼠标 / 键盘事件（GUI）和 `foxos` CLI 执行，两次结束后的界面状态与应用数据必须一致。操作数来自 [操作清单](operations/)。\n")
    L.append("| 应用 | 分组 | 启动 | 等价检查 | 检查的操作 | 清单操作 | 有 CLI / MCP 绑定 | 测试中执行 | MCP 调用 | 说明 |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    P = {"equal": "一致", "different": "不一致", "no-op": "无可检查操作", None: "—"}
    for x in apps:
        L.append(f"| {x['name']} (`{x['id']}`) | {x['group']} | {'通过' if x['boot'] == 'ok' else '—'} | {P.get(x['parity'], x['parity'])} | "
                 f"{('`' + x['cli'] + '`') if x['cli'] else '—'} | {x['ops']} | {x['bound']} | {x['executed']} | {'通过' if x['mcp'] else '—'} | "
                 f"{(x['note'] or '').replace('|', '/')[:160]} |")
    L.append("")
    L.append("## 复现\n")
    L.append("```bash\npython3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'\n(cd apps/desktop && npm ci)\n"
             "FOXOS_HOME=~/.local/share/FoxOS npm run test:all          # 全部\npython3 scripts/test_all.py --only e2e --e2e mcp,sandbox  # 只跑部分\n```\n")
    DOC.write_text("\n".join(L) + "\n", encoding="utf-8")
    TR.mkdir(parents=True, exist_ok=True)
    (TR / "summary.json").write_text(json.dumps({"generated": now.isoformat(timespec="seconds"), "commit": commit, "cases": tot, "stories": st,
                                                 "story_results": [{k: v for k, v in r.items() if k != "cases"} for r in rows],
                                                 "everything": cov}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {DOC.relative_to(ROOT)}：用例 {tot}，故事 {st}，Everything {cov}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
