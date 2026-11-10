"""Presentation（演示）应用：标准 .pptx，底层 python-pptx（MIT）；PDF / ODP 导出走 LibreOffice。"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.exc import PackageNotFoundError
from pptx.util import Emu, Inches

from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app
from ._office_common import check_ext, lo_export, require_exists

APP = "slides"
EXT = {".pptx"}
LAYOUTS = {"title": 0, "title-content": 1, "section": 2, "two-content": 3, "title-only": 5, "blank": 6}
CHARTS = {"bar": XL_CHART_TYPE.COLUMN_CLUSTERED, "line": XL_CHART_TYPE.LINE_MARKERS, "pie": XL_CHART_TYPE.PIE}

register_app(
    APP,
    "演示：读写标准 .pptx（标题页、要点页、图片、原生图表、备注），替换文本与导出",
    "基于 python-pptx 读写 PowerPoint 2007+ (.pptx)，使用默认模板的标准版式。",
    limits=["只读写 .pptx；.ppt / .odp 输入暂不支持", "版式来自默认模板：title / title-content / section / two-content / title-only / blank",
            "图表仅 bar / line / pie，数据直接给出（不链接外部 xlsx）"],
)


def _open(ctx: Context, path: Path):
    check_ext(path, EXT, "演示")
    require_exists(ctx, path, "先用 foxos slides create 创建")
    try:
        return Presentation(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as e:
        raise FoxError("USAGE", f"无法作为 pptx 打开：{ctx.rel(path)}（{e}）") from e


def _slide(prs, index: int):
    n = len(prs.slides)
    if not 1 <= index <= n:
        raise FoxError("NOT_FOUND", f"没有第 {index} 页（共 {n} 页）", hint="页码从 1 开始")
    return prs.slides[index - 1]


def _slide_info(i: int, s) -> dict:
    title = s.shapes.title.text if s.shapes.title is not None else None
    texts, charts, pictures = [], [], 0
    for sh in s.shapes:
        if sh.has_text_frame and sh != s.shapes.title and sh.text_frame.text.strip():
            texts.append(sh.text_frame.text)
        if getattr(sh, "has_chart", False) and sh.has_chart:
            c = sh.chart
            charts.append({"type": str(c.chart_type).split(".")[-1].split(" ")[0],
                           "categories": [str(x) for x in c.plots[0].categories] if c.plots else [],
                           "series": [{"name": se.name, "values": list(se.values)} for se in c.plots[0].series] if c.plots else []})
        if sh.shape_type == 13:  # PICTURE
            pictures += 1
    notes = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    return {"index": i, "layout": s.slide_layout.name, "title": title, "texts": texts, "charts": charts,
            "pictures": pictures, "notes": notes}


def create(ctx: Context, file: Path, title: str | None = None, subtitle: str | None = None,
           aspect: str = "16:9", force: bool = False) -> dict:
    check_ext(file, EXT, "演示")
    if file.exists() and not force:
        raise FoxError("CONFLICT", f"文件已存在：{ctx.rel(file)}", hint="使用 --force 覆盖（会保留上一版本）")
    prs = Presentation()
    if aspect == "16:9":
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    if title:
        s = prs.slides.add_slide(prs.slide_layouts[0])
        s.shapes.title.text = title
        if subtitle and len(s.placeholders) > 1:
            s.placeholders[1].text = subtitle
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p)))
    return {"message": f"已创建 {ctx.rel(file)}", "file": ctx.rel(file), "slides": len(prs.slides), "aspect": aspect, **saved}


def read(ctx: Context, file: Path) -> dict:
    prs = _open(ctx, file)
    return {"file": ctx.rel(file), "slide_width": Emu(prs.slide_width).inches, "slide_height": Emu(prs.slide_height).inches,
            "count": len(prs.slides), "slides": [_slide_info(i, s) for i, s in enumerate(prs.slides, start=1)]}


def add(ctx: Context, file: Path, title: str | None = None, bullet: list | None = None, layout: str | None = None,
        image: Path | None = None, notes: str | None = None) -> dict:
    prs = _open(ctx, file)
    layout = layout or ("title-content" if bullet else ("title-only" if image else "title-content"))
    s = prs.slides.add_slide(prs.slide_layouts[LAYOUTS[layout]])
    if title is not None and s.shapes.title is not None:
        s.shapes.title.text = title
    if bullet:
        body = next((ph for ph in s.placeholders if ph.placeholder_format.idx == 1), None)
        if body is None:
            raise FoxError("USAGE", f"版式 {layout} 没有正文占位符，不能放要点", hint="使用 --layout title-content")
        tf = body.text_frame
        tf.text = str(bullet[0])
        for b in bullet[1:]:
            tf.add_paragraph().text = str(b)
    if image is not None:
        if not image.exists():
            raise FoxError("NOT_FOUND", f"图片不存在：{ctx.rel(image)}")
        w, h = prs.slide_width, prs.slide_height
        top = int(h * 0.22)
        s.shapes.add_picture(str(image), int(w * 0.1), top, height=int(h * 0.7))
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p)))
    return {"message": f"已在 {ctx.rel(file)} 添加第 {len(prs.slides)} 页", "file": ctx.rel(file),
            "slide": len(prs.slides), "layout": layout, **saved}


def chart_add(ctx: Context, file: Path, type: str, categories: list, values: list, slide: int | None = None,
              series_name: str = "Series 1", title: str | None = None) -> dict:
    if len(categories) != len(values):
        raise FoxError("USAGE", f"categories（{len(categories)} 个）与 values（{len(values)} 个）数量不一致")
    prs = _open(ctx, file)
    if slide is None:
        s = prs.slides.add_slide(prs.slide_layouts[LAYOUTS["title-only"]])
        if title:
            s.shapes.title.text = title
        slide = len(prs.slides)
    else:
        s = _slide(prs, slide)
    data = CategoryChartData()
    data.categories = [str(c) for c in categories]
    data.add_series(series_name, [float(v) for v in values])
    w, h = prs.slide_width, prs.slide_height
    gf = s.shapes.add_chart(CHARTS[type], int(w * 0.08), int(h * 0.2), int(w * 0.84), int(h * 0.72), data)
    ch = gf.chart
    ch.has_legend = type == "pie"
    if type == "pie":
        ch.legend.position = XL_LEGEND_POSITION.RIGHT
        ch.legend.include_in_layout = False
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p)))
    return {"message": f"已在 {ctx.rel(file)} 第 {slide} 页插入{type}图表", "file": ctx.rel(file), "slide": slide,
            "chart": {"type": type, "points": len(values)}, **saved}


def replace(ctx: Context, file: Path, find: str, replace: str) -> dict:
    if not find:
        raise FoxError("USAGE", "find 不能为空")
    prs = _open(ctx, file)
    n = 0
    for s in prs.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if find in r.text:
                        n += r.text.count(find)
                        r.text = r.text.replace(find, replace)
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p))) if n else {"previous_version": None}
    return {"message": f"在 {ctx.rel(file)} 中替换了 {n} 处", "file": ctx.rel(file), "replacements": n, **saved}


def export(ctx: Context, file: Path, output: Path, force: bool = False) -> dict:
    _open(ctx, file)
    fmt = output.suffix.lower().lstrip(".")
    if fmt not in ("pdf", "odp"):
        raise FoxError("USAGE", f"不支持导出为 .{fmt}", hint="支持 .pdf / .odp")
    if output.exists() and not force:
        raise FoxError("CONFLICT", f"输出文件已存在：{ctx.rel(output)}", hint="使用 --force 覆盖")
    saved = lo_export(ctx, file, output, fmt)
    return {"message": f"已导出 {ctx.rel(file)} → {ctx.rel(output)}", "file": ctx.rel(file), "output": ctx.rel(output),
            "format": fmt, "bytes": output.stat().st_size, **saved}


FILE = lambda access: Param("file", "string", "演示文稿路径（.pptx）", required=True, positional=True, path=access, metavar="FILE")  # noqa: E731

register(Command(APP, "create", "新建一个 .pptx 演示文稿（可带标题页）", create,
                 params=[FILE("write"), Param("title", "string", "标题页标题"), Param("subtitle", "string", "标题页副标题"),
                         Param("aspect", "string", "页面比例", default="16:9", enum=["16:9", "4:3"]),
                         Param("force", "boolean", "已存在时覆盖", default=False, cli_short="-f")],
                 examples=["foxos slides create deck.pptx --title '2026 年销售分析' --subtitle '数据组'"], permission="create"))
register(Command(APP, "read", "读取每页的版式、标题、文本、图表数据与备注", read,
                 params=[FILE("read")], examples=["foxos slides read deck.pptx --json"]))
register(Command(APP, "add", "追加一页（标题 + 要点 / 图片 / 备注）", add,
                 params=[FILE("write"), Param("title", "string", "页面标题", cli_short="-t"),
                         Param("bullet", "array", "要点，可重复：--bullet 一 --bullet 二", items={"type": "string"}, cli_repeat=True, cli_short="-b"),
                         Param("layout", "string", "版式", enum=list(LAYOUTS)),
                         Param("image", "string", "插入图片（工作空间内 png/jpg）", path="read"),
                         Param("notes", "string", "演讲者备注")],
                 examples=["foxos slides add deck.pptx -t 全年概况 -b '销售额 2013 万元' -b '同比增长 12%'",
                           "foxos slides add deck.pptx -t 趋势 --image charts/trend.png"],
                 permission="modify"))
register(Command(APP, "chart add", "插入原生 PowerPoint 图表（默认新建一页）", chart_add,
                 params=[FILE("write"), Param("type", "string", "图表类型", required=True, enum=list(CHARTS), cli_short="-T"),
                         Param("categories", "array", "分类，逗号分隔", required=True, items={"type": "string"}, cli_short="-c"),
                         Param("values", "array", "数值，逗号分隔，与分类一一对应", required=True, items={"type": "number"}, cli_short="-v"),
                         Param("slide", "integer", "插入到已有的第 N 页（从 1 开始）；不填则新建一页"),
                         Param("series_name", "string", "系列名称", default="Series 1"),
                         Param("title", "string", "新建页时的页面标题")],
                 examples=["foxos slides chart add deck.pptx --type bar -c Q1,Q2,Q3,Q4 -v 405,428,547,633 --title 季度销售额"],
                 permission="modify"))
register(Command(APP, "replace", "查找并替换所有页中的文本", replace,
                 params=[FILE("write"), Param("find", "string", "要查找的文本", required=True),
                         Param("replace", "string", "替换为", required=True)],
                 examples=["foxos slides replace deck.pptx --find 2025 --replace 2026"],
                 limits=["只在同一个文本 run 内匹配"], permission="modify"))
register(Command(APP, "export", "导出为 pdf / odp", export,
                 params=[FILE("read"), Param("output", "string", "输出路径", required=True, positional=True, path="write", metavar="OUTPUT"),
                         Param("force", "boolean", "输出已存在时覆盖", default=False, cli_short="-f")],
                 examples=["foxos slides export deck.pptx deck.pdf"], limits=["需要 LibreOffice"], permission="create"))
