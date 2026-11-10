"""端到端：创建 xlsx → 写入单元格与公式 → 生成图表 → 重新打开验证，全程 CLI，每步进审计日志。"""

import csv
import shutil

import openpyxl
import pytest

HAS_SOFFICE = bool(shutil.which("soffice") or shutil.which("libreoffice"))

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
SALES = [120, 135, 150, 98, 170, 160]


def test_full_workflow_via_cli(fox, ws):
    # 1. 创建
    code, out, _ = fox.run("sheets", "create", "reports/sales.xlsx", "--sheet", "Sales", "--headers", "Month,Sales,Target", check=0)
    assert out["ok"] and out["result"]["sheets"] == ["Sales"]
    assert (ws / "reports" / "sales.xlsx").exists()

    # 2. 写单元格与公式
    cells = []
    for i, (m, s) in enumerate(zip(MONTHS, SALES), start=2):
        cells += [f"A{i}={m}", f"B{i}={s}", f"C{i}==B{i}*1.1"]
    cells += ["A8=Total", "B8==SUM(B2:B7)", "C8==AVERAGE(B2:B7)"]
    code, out, _ = fox.run("sheets", "write", "reports/sales.xlsx", *cells, "--sheet", "Sales", agent="data-agent", check=0)
    assert out["result"]["formulas"] == 8
    assert out["result"]["previous_version"].startswith(".foxos/versions/reports/sales.xlsx/")

    # 用工具接口风格（JSON 对象）再改一个单元格
    code, out, _ = fox.run("sheets", "write", "reports/sales.xlsx", "--cells-json", '{"D1": "Note", "D2": "peak"}', check=0)
    assert out["result"]["cells"] == ["D1", "D2"]

    # 3. 生成图表
    code, out, _ = fox.run(
        "sheets", "chart", "create", "reports/sales.xlsx", "--type", "bar", "--data", "B1:B7",
        "--categories", "A2:A7", "--title", "月度销售额", "--anchor", "F2", "--sheet", "Sales",
        agent="data-agent", check=0,
    )
    assert out["result"]["chart"]["anchor"] == "F2"
    fox.run("sheets", "chart", "create", "reports/sales.xlsx", "-t", "line", "-d", "B1:C7", "-c", "A2:A7",
            "--title", "实际 vs 目标", "-a", "F20", check=0)

    # 4. 用 openpyxl 独立重新打开验证（不经过 foxos）
    wb = openpyxl.load_workbook(ws / "reports" / "sales.xlsx")
    sh = wb["Sales"]
    assert [c.value for c in sh[1]][:3] == ["Month", "Sales", "Target"]
    assert sh["A2"].value == "Jan" and sh["B2"].value == 120
    assert sh["C3"].value == "=B3*1.1"
    assert sh["B8"].value == "=SUM(B2:B7)"
    assert sh["D2"].value == "peak"
    assert len(sh._charts) == 2
    assert type(sh._charts[0]).__name__ == "BarChart"
    assert type(sh._charts[1]).__name__ == "LineChart"
    assert sh._charts[0].series[0].val.numRef.f == "'Sales'!$B$2:$B$7"

    # 再经 CLI 读回：公式与图表
    code, out, _ = fox.run("sheets", "read", "reports/sales.xlsx", "--range", "A1:C8", check=0)
    r = out["result"]
    assert r["rows"][7] == ["Total", "=SUM(B2:B7)", "=AVERAGE(B2:B7)"]
    assert [c["type"] for c in r["charts"]] == ["bar", "line"]
    assert r["charts"][0]["title"] == "月度销售额"
    code, out, _ = fox.run("sheets", "chart", "list", "reports/sales.xlsx", check=0)
    assert out["result"]["count"] == 2

    # 5. 审计日志：每一步都有记录，且记录了调用者和目标文件
    entries = fox.audit()
    cmds = [e["command"] for e in entries]
    assert cmds == ["sheets.create", "sheets.write", "sheets.write", "sheets.chart.create",
                    "sheets.chart.create", "sheets.read", "sheets.chart.list"]
    assert all(e["status"] == "ok" for e in entries)
    assert entries[1]["agent"] == "data-agent"
    assert all(e["targets"][0]["path"] == "reports/sales.xlsx" for e in entries)
    assert entries[0]["targets"][0]["access"] == "write"
    assert entries[5]["targets"][0]["access"] == "read"
    # 版本记录：每次覆盖前都保留了上一版
    versions = list((ws / ".foxos" / "versions" / "reports" / "sales.xlsx").iterdir())
    assert len(versions) == 4


@pytest.mark.skipif(not HAS_SOFFICE, reason="需要 LibreOffice")
def test_computed_values_and_export(fox, ws):
    fox.run("sheets", "create", "s.xlsx", "--headers", "Month,Sales", check=0)
    cells = [f"A{i}={m}" for i, m in enumerate(MONTHS, 2)] + [f"B{i}={s}" for i, s in enumerate(SALES, 2)]
    fox.run("sheets", "write", "s.xlsx", *cells, "B8==SUM(B2:B7)", "B9==MAX(B2:B7)", "B10==B8/6", check=0)
    fox.run("sheets", "chart", "create", "s.xlsx", "-t", "pie", "-d", "B1:B7", "-c", "A2:A7", check=0)

    code, out, _ = fox.run("sheets", "read", "s.xlsx", "--range", "B8:B10", "--computed", check=0)
    vals = [row[0] for row in out["result"]["values"]]
    assert vals[0] == sum(SALES)
    assert vals[1] == max(SALES)
    assert vals[2] == pytest.approx(sum(SALES) / 6)
    # 原文件未被重算副本改动：仍是公式
    assert openpyxl.load_workbook(ws / "s.xlsx").active["B8"].value == "=SUM(B2:B7)"

    fox.run("sheets", "export", "s.xlsx", "out/s.csv", check=0)
    rows = list(csv.reader(open(ws / "out" / "s.csv", encoding="utf-8")))
    assert rows[0] == ["Month", "Sales"]
    assert rows[7][1] == str(sum(SALES))

    code, out, _ = fox.run("sheets", "export", "s.xlsx", "out/s.pdf", check=0)
    assert (ws / "out" / "s.pdf").read_bytes()[:5] == b"%PDF-"
    # 已存在 → CONFLICT；--force 覆盖
    fox.run("sheets", "export", "s.xlsx", "out/s.pdf", check=7)
    fox.run("sheets", "export", "s.xlsx", "out/s.pdf", "--force", check=0)

    exports = [e for e in fox.audit() if e["command"] == "sheets.export"]
    assert [e["status"] for e in exports] == ["ok", "ok", "error", "ok"]
    assert exports[2]["error"]["code"] == "CONFLICT"


def test_missing_libreoffice_reports_dependency(fox, ws):
    fox.run("sheets", "create", "s.xlsx", check=0)
    code, out, _ = fox.run("sheets", "export", "s.xlsx", "s.pdf", extra_env={"FOXOS_SOFFICE": "/nonexistent/soffice"})
    assert code == 6 and out["error"]["code"] == "DEPENDENCY_MISSING"


def test_errors_have_stable_codes(fox, ws):
    code, out, _ = fox.run("sheets", "read", "nope.xlsx")
    assert code == 3 and out["error"]["code"] == "NOT_FOUND"
    fox.run("sheets", "create", "a.xlsx", check=0)
    code, out, _ = fox.run("sheets", "create", "a.xlsx")
    assert code == 7 and "--force" in out["error"]["hint"]
    code, out, _ = fox.run("sheets", "write", "a.xlsx", "ZZZ0=1")
    assert code == 2 and out["error"]["code"] == "USAGE"
    code, out, _ = fox.run("sheets", "chart", "create", "a.xlsx", "--data", "B1:B3")
    assert code == 2 and "type" in out["error"]["message"]
    code, out, _ = fox.run("sheets", "chart", "create", "a.xlsx", "--type", "radar", "--data", "B1:B3")
    assert code == 2
    code, out, _ = fox.run("sheets", "read", "a.xlsx", "--sheet", "Missing")
    assert code == 3 and out["error"]["details"]["sheets"] == ["Sheet1"]
    code, out, _ = fox.run("sheets", "create", "notes.txt")
    assert code == 2
    # 人类可读模式：错误写到 stderr
    code, _, p = fox.run("sheets", "read", "nope.xlsx", json_out=False)
    assert code == 3 and "NOT_FOUND" in p.stderr and p.stdout == ""


def test_cli_value_coercion(fox, ws):
    fox.run("sheets", "create", "t.xlsx", check=0)
    fox.run("sheets", "write", "t.xlsx", "A1=42", "A2=3.5", "A3=TRUE", "A4='007", "A5=hello world", "A6=", check=0)
    sh = openpyxl.load_workbook(ws / "t.xlsx").active
    assert sh["A1"].value == 42 and sh["A2"].value == 3.5 and sh["A3"].value is True
    assert sh["A4"].value == "007" and sh["A5"].value == "hello world" and sh["A6"].value is None
