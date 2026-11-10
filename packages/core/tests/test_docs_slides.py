"""文档（python-docx）与演示（python-pptx）：CLI 创建 → 编辑 → 用库独立重新打开验证 → 导出。"""

import shutil

import docx
import pytest
from pptx import Presentation

HAS_SOFFICE = bool(shutil.which("soffice") or shutil.which("libreoffice"))


def test_docs_workflow(fox, ws):
    fox.run("docs", "create", "report.docx", "--title", "2025 年销售分析", check=0)
    fox.run("docs", "append", "report.docx", "一、总体情况", "--heading", "1", agent="doc-agent", check=0)
    fox.run("docs", "append", "report.docx", "全年销售额 2013 万元。", "2025 年同比增长 12%。", check=0)
    fox.run("docs", "append", "report.docx", "华东最高", "华南次之", "--style", "List Bullet", check=0)
    fox.run("docs", "append", "report.docx", "--table-json", '[["季度","销售额"],["Q1",405],["Q2",428]]', check=0)
    code, out, _ = fox.run("docs", "replace", "report.docx", "--find", "2025", "--replace", "2026", check=0)
    assert out["result"]["replacements"] == 2

    d = docx.Document(str(ws / "report.docx"))  # 独立重新打开
    texts = [(p.style.name, p.text) for p in d.paragraphs]
    assert texts[0] == ("Title", "2026 年销售分析")
    assert ("Heading 1", "一、总体情况") in texts
    assert ("List Bullet", "华东最高") in texts
    assert "2026 年同比增长 12%。" in [t for _, t in texts]
    assert d.tables[0].cell(2, 1).text == "428"

    code, out, _ = fox.run("docs", "read", "report.docx", check=0)
    r = out["result"]
    assert r["stats"]["tables"] == 1 and r["tables"][0]["rows"][0] == ["季度", "销售额"]

    fox.run("docs", "export", "report.docx", "report.md", check=0)
    md = (ws / "report.md").read_text(encoding="utf-8")
    assert md.startswith("# 2026 年销售分析") and "## 一、总体情况" in md and "- 华东最高\n- 华南次之" in md
    assert "| Q2 | 428 |" in md

    code, out, _ = fox.run("docs", "append", "report.docx", "x", "--style", "NoSuchStyle")
    assert code == 2 and "NoSuchStyle" in out["error"]["message"]
    code, out, _ = fox.run("docs", "read", "missing.docx")
    assert code == 3
    cmds = [e["command"] for e in fox.audit()]
    assert cmds.count("docs.append") == 5 and "docs.replace" in cmds


@pytest.mark.skipif(not HAS_SOFFICE, reason="需要 LibreOffice")
def test_docs_and_slides_pdf_export(fox, ws):
    fox.run("docs", "create", "a.docx", "--title", "测试", check=0)
    fox.run("docs", "export", "a.docx", "a.pdf", check=0)
    assert (ws / "a.pdf").read_bytes()[:5] == b"%PDF-"
    fox.run("slides", "create", "a.pptx", "--title", "测试", check=0)
    fox.run("slides", "export", "a.pptx", "out/a.pdf", check=0)
    assert (ws / "out" / "a.pdf").read_bytes()[:5] == b"%PDF-"


def test_slides_workflow(fox, ws):
    fox.run("slides", "create", "deck.pptx", "--title", "2025 年销售分析", "--subtitle", "数据组", check=0)
    fox.run("slides", "add", "deck.pptx", "-t", "全年概况", "-b", "销售额 2013 万元", "-b", "2025 年增长 12%",
            "--notes", "先讲结论", agent="slides-agent", check=0)
    fox.run("slides", "chart", "add", "deck.pptx", "--type", "bar", "-c", "Q1,Q2,Q3,Q4", "-v", "405,428,547,633",
            "--title", "季度销售额", "--series-name", "销售额", check=0)
    code, out, _ = fox.run("slides", "replace", "deck.pptx", "--find", "2025", "--replace", "2026", check=0)
    assert out["result"]["replacements"] == 2

    prs = Presentation(str(ws / "deck.pptx"))  # 独立重新打开
    assert len(prs.slides) == 3
    assert prs.slides[0].shapes.title.text == "2026 年销售分析"
    body = [sh for sh in prs.slides[1].shapes if sh.has_text_frame and sh != prs.slides[1].shapes.title][0]
    assert [p.text for p in body.text_frame.paragraphs] == ["销售额 2013 万元", "2026 年增长 12%"]
    assert prs.slides[1].notes_slide.notes_text_frame.text == "先讲结论"
    chart = [sh for sh in prs.slides[2].shapes if sh.has_chart][0].chart
    assert list(chart.plots[0].categories) == ["Q1", "Q2", "Q3", "Q4"]
    assert list(chart.plots[0].series[0].values) == [405.0, 428.0, 547.0, 633.0]

    code, out, _ = fox.run("slides", "read", "deck.pptx", check=0)
    r = out["result"]
    assert r["count"] == 3 and r["slides"][2]["charts"][0]["series"][0]["name"] == "销售额"
    code, out, _ = fox.run("slides", "chart", "add", "deck.pptx", "--type", "pie", "-c", "a,b", "-v", "1")
    assert code == 2
    code, out, _ = fox.run("slides", "chart", "add", "deck.pptx", "--type", "pie", "-c", "a,b", "-v", "1,x")
    assert code == 2
    code, out, _ = fox.run("slides", "chart", "add", "deck.pptx", "--type", "line", "-c", "a", "-v", "1", "--slide", "9")
    assert code == 3
