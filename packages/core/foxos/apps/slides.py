"""Presentation（演示）应用：标准 .pptx，底层 python-pptx（MIT）；PDF / ODP 导出走 LibreOffice。"""

from __future__ import annotations

from foxos.i18n import tr
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
    tr("slides.presentations_read_and_write"),
    tr("slides.reads_and_writes_powerpoint_2007"),
    limits=[tr("slides.only_pptx_is_read_and_written_ppt"), tr("slides.layouts_come_from_the_default"),
            tr("slides.charts_support_only_bar_line_pie")],
)


def _open(ctx: Context, path: Path):
    check_ext(path, EXT, tr("slides.presentations"))
    require_exists(ctx, path, tr("slides.create_it_first_with_foxos_slides"))
    try:
        return Presentation(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as e:
        raise FoxError("USAGE", tr("slides.cannot_open_as_pptx", ctx.rel(path), e)) from e


def _slide(prs, index: int):
    n = len(prs.slides)
    if not 1 <= index <= n:
        raise FoxError("NOT_FOUND", tr("slides.there_is_no_slide_slides_in_total", index, n), hint=tr("slides.slide_numbers_start_at_1"))
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
    check_ext(file, EXT, tr("slides.presentations"))
    if file.exists() and not force:
        raise FoxError("CONFLICT", tr("common.file_already_exists", ctx.rel(file)), hint=tr("common.use_force_to_overwrite_the_previous"))
    prs = Presentation()
    if aspect == "16:9":
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    if title:
        s = prs.slides.add_slide(prs.slide_layouts[0])
        s.shapes.title.text = title
        if subtitle and len(s.placeholders) > 1:
            s.placeholders[1].text = subtitle
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p)))
    return {"message": tr("common.created", ctx.rel(file)), "file": ctx.rel(file), "slides": len(prs.slides), "aspect": aspect, **saved}


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
            raise FoxError("USAGE", tr("slides.layout_has_no_body_placeholder_and", layout), hint=tr("slides.use_layout_title_content"))
        tf = body.text_frame
        tf.text = str(bullet[0])
        for b in bullet[1:]:
            tf.add_paragraph().text = str(b)
    if image is not None:
        if not image.exists():
            raise FoxError("NOT_FOUND", tr("slides.image_not_found", ctx.rel(image)))
        w, h = prs.slide_width, prs.slide_height
        top = int(h * 0.22)
        s.shapes.add_picture(str(image), int(w * 0.1), top, height=int(h * 0.7))
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    saved = ctx.save_atomic(file, lambda p: prs.save(str(p)))
    return {"message": tr("slides.added_slide_to", ctx.rel(file), len(prs.slides)), "file": ctx.rel(file),
            "slide": len(prs.slides), "layout": layout, **saved}


def chart_add(ctx: Context, file: Path, type: str, categories: list, values: list, slide: int | None = None,
              series_name: str = "Series 1", title: str | None = None) -> dict:
    if len(categories) != len(values):
        raise FoxError("USAGE", tr("slides.categories_and_values_have_different", len(categories), len(values)))
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
    return {"message": tr("slides.inserted_a_chart_on_slide_of", ctx.rel(file), slide, type), "file": ctx.rel(file), "slide": slide,
            "chart": {"type": type, "points": len(values)}, **saved}


def replace(ctx: Context, file: Path, find: str, replace: str) -> dict:
    if not find:
        raise FoxError("USAGE", tr("common.find_cannot_be_empty"))
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
    return {"message": tr("common.replaced_occurrence_s_in", ctx.rel(file), n), "file": ctx.rel(file), "replacements": n, **saved}


def export(ctx: Context, file: Path, output: Path, force: bool = False) -> dict:
    _open(ctx, file)
    fmt = output.suffix.lower().lstrip(".")
    if fmt not in ("pdf", "odp"):
        raise FoxError("USAGE", tr("common.cannot_export_to", fmt), hint=tr("slides.supported_pdf_odp"))
    if output.exists() and not force:
        raise FoxError("CONFLICT", tr("common.output_file_already_exists", ctx.rel(output)), hint=tr("common.use_force_to_overwrite"))
    saved = lo_export(ctx, file, output, fmt)
    return {"message": tr("common.exported", ctx.rel(file), ctx.rel(output)), "file": ctx.rel(file), "output": ctx.rel(output),
            "format": fmt, "bytes": output.stat().st_size, **saved}


FILE = lambda access: Param("file", "string", tr("slides.presentation_path_pptx"), required=True, positional=True, path=access, metavar="FILE")  # noqa: E731

register(Command(APP, "create", tr("slides.create_a_new_pptx_presentation"), create,
                 params=[FILE("write"), Param("title", "string", tr("slides.title_slide_title")), Param("subtitle", "string", tr("slides.title_slide_subtitle")),
                         Param("aspect", "string", tr("slides.slide_aspect_ratio"), default="16:9", enum=["16:9", "4:3"]),
                         Param("force", "boolean", tr("common.overwrite_if_it_exists"), default=False, cli_short="-f")],
                 examples=[tr("slides.foxos_slides_create_deck_pptx_title")], permission="create"))
register(Command(APP, "read", tr("slides.read_each_slide_s_layout_title_text"), read,
                 params=[FILE("read")], examples=["foxos slides read deck.pptx --json"]))
register(Command(APP, "add", tr("slides.append_a_slide_title_bullets_image"), add,
                 params=[FILE("write"), Param("title", "string", tr("slides.slide_title"), cli_short="-t"),
                         Param("bullet", "array", tr("slides.bullet_repeatable_bullet_one_bullet"), items={"type": "string"}, cli_repeat=True, cli_short="-b"),
                         Param("layout", "string", tr("slides.layout"), enum=list(LAYOUTS)),
                         Param("image", "string", tr("slides.insert_an_image_png_jpg_in_the"), path="read"),
                         Param("notes", "string", tr("slides.speaker_notes"))],
                 examples=[tr("slides.foxos_slides_add_deck_pptx_t_year_in"),
                           tr("slides.foxos_slides_add_deck_pptx_t_trend")],
                 permission="modify"))
register(Command(APP, "chart add", tr("slides.insert_a_native_powerpoint_chart_on"), chart_add,
                 params=[FILE("write"), Param("type", "string", tr("common.chart_type"), required=True, enum=list(CHARTS), cli_short="-T"),
                         Param("categories", "array", tr("slides.categories_comma_separated"), required=True, items={"type": "string"}, cli_short="-c"),
                         Param("values", "array", tr("slides.values_comma_separated_one_per"), required=True, items={"type": "number"}, cli_short="-v"),
                         Param("slide", "integer", tr("slides.insert_on_existing_slide_n_from_1_a")),
                         Param("series_name", "string", tr("slides.series_name"), default="Series 1"),
                         Param("title", "string", tr("slides.slide_title_for_a_new_slide"))],
                 examples=[tr("slides.foxos_slides_chart_add_deck_pptx")],
                 permission="modify"))
register(Command(APP, "replace", tr("slides.find_and_replace_text_on_all_slides"), replace,
                 params=[FILE("write"), Param("find", "string", tr("common.text_to_find"), required=True),
                         Param("replace", "string", tr("common.replace_with"), required=True)],
                 examples=["foxos slides replace deck.pptx --find 2025 --replace 2026"],
                 limits=[tr("slides.matches_only_within_a_single_text")], permission="modify"))
register(Command(APP, "export", tr("slides.export_to_pdf_odp"), export,
                 params=[FILE("read"), Param("output", "string", tr("common.output_path"), required=True, positional=True, path="write", metavar="OUTPUT"),
                         Param("force", "boolean", tr("common.overwrite_the_output_if_it_exists"), default=False, cli_short="-f")],
                 examples=["foxos slides export deck.pptx deck.pdf"], limits=[tr("slides.needs_libreoffice")], permission="create"))
