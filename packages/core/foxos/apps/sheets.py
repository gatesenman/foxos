"""Spreadsheet（表格）应用：标准 .xlsx 文件，底层使用 openpyxl（MIT）。

公式求值与 PDF/ODS 导出通过 LibreOffice 无头模式完成（外部进程，不打包）。
不包含、不依赖任何 AGPL 代码（Everything 的 spreadsheet 为 AGPL-3.0-only，未复用）。
"""

from __future__ import annotations

from foxos.i18n import tr
import csv
import datetime as _dt
import shutil
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.utils.cell import (
    column_index_from_string,
    coordinate_from_string,
    get_column_letter,
    range_boundaries,
)
from openpyxl.utils.exceptions import CellCoordinatesException, InvalidFileException

from .. import office
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app

APP = "sheets"
XLSX_EXT = {".xlsx"}
CHART_TYPES = ["bar", "line", "pie"]
MAX_CELLS = 20000

register_app(
    APP,
    tr("sheets.spreadsheets_read_and_write_standard"),
    tr("sheets.reads_and_writes_excel_2007_xlsx"),
    limits=[
        tr("sheets.only_xlsx_is_read_and_written_xls"),
        tr("sheets.formulas_are_written_as_text"),
        tr("sheets.charts_support_only_bar_line_pie"),
        tr("sheets.a_single_read_returns_at_most_20000"),
    ],
)


# ----------------------------------------------------------------------
# helpers
def _check_ext(path: Path) -> None:
    if path.suffix.lower() not in XLSX_EXT:
        raise FoxError("USAGE", tr("sheets.only_xlsx_files_are_supported", path.name), hint=tr("sheets.file_names_end_in_xlsx"))


def _load(ctx: Context, path: Path, data_only: bool = False):
    _check_ext(path)
    if not path.exists():
        raise FoxError("NOT_FOUND", tr("common.file_not_found", ctx.rel(path)), hint=tr("sheets.create_it_first_with_foxos_sheets"))
    try:
        return openpyxl.load_workbook(path, data_only=data_only)
    except (InvalidFileException, KeyError, OSError, ValueError) as e:
        raise FoxError("USAGE", tr("sheets.cannot_open_as_xlsx", ctx.rel(path), e)) from e


def _sheet(wb, name: str | None, create: bool = False):
    if not name:
        return wb.active
    if name in wb.sheetnames:
        return wb[name]
    if create:
        return wb.create_sheet(name)
    raise FoxError("NOT_FOUND", tr("sheets.sheet_not_found", name), details={"sheets": wb.sheetnames})


def _bounds(ref: str):
    try:
        min_col, min_row, max_col, max_row = range_boundaries(ref.upper().replace("$", ""))
    except (ValueError, TypeError, CellCoordinatesException) as e:
        raise FoxError("USAGE", tr("sheets.invalid_cell_range", ref), hint=tr("sheets.use_a1_notation_such_as_a1_c10")) from e
    if None in (min_col, min_row, max_col, max_row):
        raise FoxError("USAGE", tr("sheets.the_range_needs_explicit_start_and", ref), hint=tr("sheets.e_g_a1_c10"))
    return min_col, min_row, max_col, max_row


def _check_cell(ref: str) -> str:
    ref = ref.strip().upper().replace("$", "")
    try:
        col, row = coordinate_from_string(ref)
        ok = row >= 1 and row <= 1048576 and 1 <= column_index_from_string(col) <= 16384
    except (ValueError, CellCoordinatesException):
        ok = False
    if not ok:
        raise FoxError("USAGE", tr("sheets.invalid_cell_address", ref), hint=tr("sheets.use_a1_notation_such_as_b2_columns_a"))
    return f"{col}{row}"


def _jsonable(v):
    if isinstance(v, (_dt.datetime, _dt.date, _dt.time)):
        return v.isoformat()
    if isinstance(v, _dt.timedelta):
        return v.total_seconds()
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


def _grid(ws, min_col, min_row, max_col, max_row):
    return [
        [_jsonable(c.value) for c in row]
        for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col)
    ]


def _title_text(chart) -> str | None:
    t = getattr(chart, "title", None)
    if t is None:
        return None
    if isinstance(t, str):
        return t
    try:
        return "".join(r.t for p in t.tx.rich.p for r in (p.r or [])) or None
    except AttributeError:
        return None


def _anchor_of(chart) -> str | None:
    a = chart.anchor
    if isinstance(a, str):
        return a
    try:
        return f"{get_column_letter(a._from.col + 1)}{a._from.row + 1}"
    except AttributeError:
        return None


def _chart_info(idx: int, chart) -> dict:
    series = []
    for s in chart.series:
        val = s.val.numRef.f if s.val and s.val.numRef else None
        cat = None
        if s.cat is not None:
            ref = s.cat.numRef or s.cat.strRef
            cat = ref.f if ref is not None else None
        name = None
        if s.tx is not None and s.tx.strRef is not None:
            name = s.tx.strRef.f
        series.append({"values": val, "categories": cat, "name_ref": name})
    kind = {"BarChart": "bar", "LineChart": "line", "PieChart": "pie"}.get(type(chart).__name__, type(chart).__name__)
    return {"index": idx, "type": kind, "title": _title_text(chart), "anchor": _anchor_of(chart), "series": series}


def _has_formulas(wb) -> bool:
    return any(c.data_type == "f" for ws in wb.worksheets for row in ws.iter_rows() for c in row)


# ----------------------------------------------------------------------
# commands
def create(ctx: Context, file: Path, sheet: str = "Sheet1", headers: list | None = None, force: bool = False) -> dict:
    _check_ext(file)
    if file.exists() and not force:
        raise FoxError("CONFLICT", tr("common.file_already_exists", ctx.rel(file)), hint=tr("common.use_force_to_overwrite_the_previous"))
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    if headers:
        ws.append([str(h) for h in headers])
    saved = ctx.save_atomic(file, lambda p: wb.save(p))
    return {
        "message": tr("common.created", ctx.rel(file)),
        "file": ctx.rel(file),
        "sheets": wb.sheetnames,
        "headers": headers or [],
        **saved,
    }


def read(ctx: Context, file: Path, sheet: str | None = None, range: str | None = None, computed: bool = False) -> dict:
    wb = _load(ctx, file)
    ws = _sheet(wb, sheet)
    if range:
        b = _bounds(range)
    else:
        b = (1, 1, max(ws.max_column, 1), max(ws.max_row, 1))
    min_col, min_row, max_col, max_row = b
    n = (max_col - min_col + 1) * (max_row - min_row + 1)
    if n > MAX_CELLS:
        raise FoxError("USAGE", tr("sheets.the_range_has_cells_more_than_the", n, MAX_CELLS), hint=tr("sheets.read_in_batches_with_range"))
    ref = f"{get_column_letter(min_col)}{min_row}:{get_column_letter(max_col)}{max_row}"
    rows = _grid(ws, *b)
    out = {
        "file": ctx.rel(file),
        "sheet": ws.title,
        "sheets": wb.sheetnames,
        "dimensions": ws.dimensions,
        "range": ref,
        "rows": rows,
        "charts": [_chart_info(i, c) for i, c in enumerate(ws._charts)],
    }
    has_f = any(isinstance(v, str) and v.startswith("=") for r in rows for v in r)
    if computed:
        with tempfile.TemporaryDirectory(prefix="foxos-") as td:
            calc = office.recalculated_copy(file, Path(td))
            wbv = openpyxl.load_workbook(calc, data_only=True)
            out["values"] = _grid(wbv[ws.title], *b)
        out["computed_by"] = "libreoffice"
    elif has_f:
        out["note"] = tr("sheets.values_in_rows_that_start_with_are")
    return out


def write(ctx: Context, file: Path, cells: dict, sheet: str | None = None, create_sheet: bool = False) -> dict:
    if not cells:
        raise FoxError("USAGE", tr("sheets.no_cells_to_write"), hint=tr("sheets.for_example_foxos_sheets_write_data"))
    wb = _load(ctx, file)
    ws = _sheet(wb, sheet, create=create_sheet)
    written, formulas = [], 0
    normalized = {}
    for ref, value in cells.items():
        r = _check_cell(str(ref))
        if value is not None and not isinstance(value, (str, int, float, bool)):
            raise FoxError("USAGE", tr("sheets.unsupported_value_type_for", r, type(value).__name__))
        normalized[r] = value
    for r, value in normalized.items():
        ws[r] = value
        written.append(r)
        if isinstance(value, str) and value.startswith("="):
            formulas += 1
    saved = ctx.save_atomic(file, lambda p: wb.save(p))
    return {
        "message": tr("sheets.wrote_cell_s_to", len(written), ctx.rel(file), ws.title),
        "file": ctx.rel(file),
        "sheet": ws.title,
        "cells": written,
        "formulas": formulas,
        **saved,
    }


def chart_create(
    ctx: Context,
    file: Path,
    type: str,
    data: str,
    categories: str | None = None,
    title: str | None = None,
    sheet: str | None = None,
    anchor: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
    no_header: bool = False,
) -> dict:
    wb = _load(ctx, file)
    ws = _sheet(wb, sheet)
    dmin_col, dmin_row, dmax_col, dmax_row = _bounds(data)
    if dmax_row - dmin_row < (0 if no_header else 1):
        raise FoxError("USAGE", tr("sheets.data_range_is_too_small", data), hint=tr("sheets.with_series_names_in_the_first_row"))
    cls = {"bar": BarChart, "line": LineChart, "pie": PieChart}[type]
    chart = cls()
    if title:
        chart.title = title
    if type != "pie":
        if x_title:
            chart.x_axis.title = x_title
        if y_title:
            chart.y_axis.title = y_title
    elif dmax_col > dmin_col:
        raise FoxError("USAGE", tr("sheets.a_pie_chart_can_have_only_one_data"))
    ref = Reference(ws, min_col=dmin_col, min_row=dmin_row, max_col=dmax_col, max_row=dmax_row)
    chart.add_data(ref, titles_from_data=not no_header)
    if categories:
        cmin_col, cmin_row, cmax_col, cmax_row = _bounds(categories)
        chart.set_categories(Reference(ws, min_col=cmin_col, min_row=cmin_row, max_col=cmax_col, max_row=cmax_row))
    if anchor:
        anchor = _check_cell(anchor)
    else:
        anchor = f"{get_column_letter(ws.max_column + 2)}2"
    ws.add_chart(chart, anchor)
    index = len(ws._charts) - 1
    saved = ctx.save_atomic(file, lambda p: wb.save(p))
    return {
        "message": tr("sheets.created_a_chart_at_on", ctx.rel(file), ws.title, anchor, type),
        "file": ctx.rel(file),
        "sheet": ws.title,
        "chart": {"index": index, "type": type, "title": title, "anchor": anchor, "data": data, "categories": categories},
        **saved,
    }


def chart_list(ctx: Context, file: Path, sheet: str | None = None) -> dict:
    wb = _load(ctx, file)
    sheets = [_sheet(wb, sheet)] if sheet else wb.worksheets
    charts = []
    for ws in sheets:
        for i, c in enumerate(ws._charts):
            charts.append({"sheet": ws.title, **_chart_info(i, c)})
    return {"file": ctx.rel(file), "count": len(charts), "charts": charts}


def export(ctx: Context, file: Path, output: Path, sheet: str | None = None, force: bool = False) -> dict:
    wb = _load(ctx, file)
    fmt = output.suffix.lower().lstrip(".")
    if fmt not in ("csv", "pdf", "ods", "xlsx"):
        raise FoxError("USAGE", tr("common.cannot_export_to", fmt), hint=tr("sheets.supported_csv_pdf_ods_xlsx"))
    if output.exists() and not force:
        raise FoxError("CONFLICT", tr("common.output_file_already_exists", ctx.rel(output)), hint=tr("common.use_force_to_overwrite"))
    warnings = []
    with tempfile.TemporaryDirectory(prefix="foxos-") as td:
        tdp = Path(td)
        if fmt == "csv":
            ws = _sheet(wb, sheet)
            source_ws = ws
            if _has_formulas(wb):
                if office.find_soffice():
                    calc = office.recalculated_copy(file, tdp)
                    source_ws = openpyxl.load_workbook(calc, data_only=True)[ws.title]
                else:
                    warnings.append(tr("sheets.libreoffice_not_found_formulas"))

            def writer(p: Path):
                with open(p, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for row in source_ws.iter_rows(values_only=True):
                        w.writerow(["" if v is None else _jsonable(v) for v in row])

            saved = ctx.save_atomic(output, writer)
        elif fmt == "xlsx":
            saved = ctx.save_atomic(output, lambda p: shutil.copy2(file, p))
        else:
            if sheet:
                warnings.append(tr("sheets.pdf_ods_export_includes_all_sheets"))
            staged = tdp / "in" / (output.stem + file.suffix)
            staged.parent.mkdir()
            shutil.copy2(file, staged)
            converted = office.convert(staged, fmt, tdp / "out")
            saved = ctx.save_atomic(output, lambda p: shutil.copy2(converted, p))
    return {
        "message": tr("common.exported", ctx.rel(file), ctx.rel(output)),
        "file": ctx.rel(file),
        "output": ctx.rel(output),
        "format": fmt,
        "bytes": output.stat().st_size,
        "warnings": warnings,
        **saved,
    }


# ----------------------------------------------------------------------
FILE = Param("file", "string", tr("sheets.workbook_path_in_the_workspace_xlsx"), required=True, positional=True, metavar="FILE")
SHEET = Param("sheet", "string", tr("sheets.sheet_name_the_active_sheet_by"), cli_short="-s")

register(Command(
    APP, "create", tr("sheets.create_a_new_xlsx_workbook"),
    create,
    params=[
        Param("file", "string", tr("sheets.path_of_the_workbook_to_create_xlsx"), required=True, positional=True, path="write", metavar="FILE"),
        Param("sheet", "string", tr("sheets.name_of_the_first_sheet"), default="Sheet1", cli_short="-s"),
        Param("headers", "array", tr("sheets.header_row_comma_separated_cli_or_an"), items={"type": "string"}),
        Param("force", "boolean", tr("sheets.overwrite_if_the_file_exists_the"), default=False, cli_short="-f"),
    ],
    examples=[
        "foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales",
        "foxos sheets create report/q1.xlsx --force --json",
    ],
    limits=[tr("sheets.only_creates_xlsx_missing_parent")],
    permission="create",
))

register(Command(
    APP, "read", tr("sheets.read_sheet_cells_formulas_charts"),
    read,
    params=[
        Param("file", "string", tr("sheets.workbook_path"), required=True, positional=True, path="read", metavar="FILE"),
        SHEET,
        Param("range", "string", tr("sheets.range_in_a1_notation_such_as_a1_c10"), cli_short="-r"),
        Param("computed", "boolean", tr("sheets.recalculate_formulas_with"), default=False),
    ],
    examples=[
        "foxos sheets read sales.xlsx",
        "foxos sheets read sales.xlsx --range A1:B13 --computed --json",
    ],
    limits=[tr("sheets.at_most_cells_per_call", MAX_CELLS), tr("sheets.computed_needs_libreoffice")],
    permission="read",
))

register(Command(
    APP, "write", tr("sheets.write_cell_values_or_formulas_cell"),
    write,
    params=[
        Param("file", "string", tr("sheets.workbook_path"), required=True, positional=True, path="write", metavar="FILE"),
        Param(
            "cells", "object",
            tr("sheets.cells_to_write_on_the_cli_write_a1"),
            required=True, positional=True, cli_kv=True, metavar="CELL=VALUE",
        ),
        SHEET,
        Param("create_sheet", "boolean", tr("sheets.create_the_sheet_if_it_does_not"), default=False),
    ],
    examples=[
        "foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135",
        "foxos sheets write sales.xlsx 'B14==SUM(B2:B13)' --sheet Sales",
        "foxos sheets write sales.xlsx --cells-json '{\"C2\": \"=B2*1.1\"}' --json",
    ],
    limits=[tr("sheets.formulas_are_written_with_english"), tr("sheets.writing_styles_and_merged_cells_is")],
    permission="modify",
))

register(Command(
    APP, "chart create", tr("sheets.create_a_native_excel_chart_from_a"),
    chart_create,
    params=[
        Param("file", "string", tr("sheets.workbook_path"), required=True, positional=True, path="write", metavar="FILE"),
        Param("type", "string", tr("common.chart_type"), required=True, enum=CHART_TYPES, cli_short="-t"),
        Param("data", "string", tr("sheets.data_range_each_column_is_a_series"), required=True, cli_short="-d"),
        Param("categories", "string", tr("sheets.category_x_axis_range_such_as_a2_a13"), cli_short="-c"),
        Param("title", "string", tr("sheets.chart_title")),
        SHEET,
        Param("anchor", "string", tr("sheets.cell_for_the_chart_s_top_left_corner"), cli_short="-a"),
        Param("x_title", "string", tr("sheets.x_axis_title_bar_line")),
        Param("y_title", "string", tr("sheets.y_axis_title_bar_line")),
        Param("no_header", "boolean", tr("sheets.the_first_row_of_the_data_range_is"), default=False),
    ],
    examples=[
        tr("sheets.foxos_sheets_chart_create_sales_xlsx"),
        "foxos sheets chart create sales.xlsx -t line -d B1:C13 -c A2:A13 --anchor E20 --json",
    ],
    limits=[tr("sheets.bar_line_pie_only"), tr("sheets.a_pie_chart_has_only_one_series"), tr("sheets.chart_styles_and_colors_are_not")],
    permission="modify",
))

register(Command(
    APP, "chart list", tr("sheets.list_the_charts_in_a_workbook"),
    chart_list,
    params=[
        Param("file", "string", tr("sheets.workbook_path"), required=True, positional=True, path="read", metavar="FILE"),
        SHEET,
    ],
    examples=["foxos sheets chart list sales.xlsx --json"],
    permission="read",
))

register(Command(
    APP, "export", tr("sheets.export_to_csv_pdf_ods_xlsx_format"),
    export,
    params=[
        Param("file", "string", tr("sheets.source_workbook_path"), required=True, positional=True, path="read", metavar="FILE"),
        Param("output", "string", tr("sheets.output_path_csv_pdf_ods_xlsx"), required=True, positional=True, path="write", metavar="OUTPUT"),
        SHEET,
        Param("force", "boolean", tr("sheets.overwrite_the_output_file_if_it"), default=False, cli_short="-f"),
    ],
    examples=[
        "foxos sheets export sales.xlsx sales.csv",
        "foxos sheets export sales.xlsx out/sales.pdf --force --json",
    ],
    limits=[tr("sheets.csv_exports_only_one_sheet_formulas"), tr("sheets.pdf_ods_need_libreoffice")],
    permission="create",
))
