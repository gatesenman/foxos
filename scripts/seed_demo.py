#!/usr/bin/env python3
"""生成一个演示工作空间：多个智能体身份通过 foxos CLI 完成「销售数据 → 图表 → 审核」。

用法：python scripts/seed_demo.py [工作空间目录]（默认 ./demo-workspace，会先清空）
所有操作都通过真实的 foxos 命令执行，并写入该工作空间的审计日志。
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "core"))

from foxos import locks  # noqa: E402
from foxos.workspace import Workspace  # noqa: E402

ws_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "demo-workspace").resolve()
if ws_dir.exists():
    shutil.rmtree(ws_dir)
ws_dir.mkdir(parents=True)
env = {**os.environ, "PYTHONPATH": str(ROOT / "packages" / "core")}


def fox(agent, *args, ok=True):
    cmd = [sys.executable, "-m", "foxos", "--workspace", str(ws_dir), "--agent", agent, *args]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8")
    print(f"[{agent}] foxos {' '.join(args)} → {p.returncode}")
    if ok and p.returncode != 0:
        sys.exit(p.stderr)
    return p


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SALES = [120, 135, 150, 98, 170, 160, 182, 175, 190, 205, 198, 230]
TARGET = [130, 130, 140, 140, 150, 150, 165, 165, 180, 180, 195, 210]

fox("human", "tasks", "create", "根据 2026 年销售数据制作分析表和图表，完成后交给我审核")
fox("supervisor", "tasks", "create", "数据智能体：整理 reports/sales.xlsx 并生成柱状图与折线图")
fox("data-agent", "sheets", "create", "reports/sales.xlsx", "--sheet", "Sales", "--headers", "Month,Sales,Target,Gap")
cells = []
for i, (m, s, t) in enumerate(zip(MONTHS, SALES, TARGET), start=2):
    cells += [f"A{i}={m}", f"B{i}={s}", f"C{i}={t}", f"D{i}==B{i}-C{i}"]
cells += ["A14=Total", "B14==SUM(B2:B13)", "C14==SUM(C2:C13)", "D14==B14-C14"]
fox("data-agent", "sheets", "write", "reports/sales.xlsx", *cells, "--sheet", "Sales")
fox("data-agent", "sheets", "chart", "create", "reports/sales.xlsx", "--type", "bar", "--data", "B1:B13",
    "--categories", "A2:A13", "--title", "月度销售额", "--anchor", "F2")
fox("data-agent", "sheets", "chart", "create", "reports/sales.xlsx", "--type", "line", "--data", "B1:C13",
    "--categories", "A2:A13", "--title", "实际 vs 目标", "--anchor", "F20")

# 文档智能体尝试在数据智能体写入期间修改同一文件 → 被单写者锁拒绝
lk = locks.acquire(Workspace(ws_dir), "reports/sales.xlsx", owner="data-agent")
fox("doc-agent", "sheets", "write", "reports/sales.xlsx", "E1=Note", ok=False)
locks.release(lk)

fox("review-agent", "sheets", "read", "reports/sales.xlsx", "--range", "A14:D14", "--computed")
fox("review-agent", "sheets", "chart", "list", "reports/sales.xlsx")
fox("review-agent", "sheets", "read", "../secrets.xlsx", ok=False)  # 越界访问 → 拒绝
fox("data-agent", "sheets", "export", "reports/sales.xlsx", "reports/sales.pdf")
fox("data-agent", "sheets", "export", "reports/sales.xlsx", "reports/sales.csv")
print(f"演示工作空间：{ws_dir}")
