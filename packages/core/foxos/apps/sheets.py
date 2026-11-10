"""Spreadsheet（表格）应用：标准 .xlsx 文件，底层使用 openpyxl（MIT）。

公式求值与 PDF/ODS 导出通过 LibreOffice 无头模式完成（外部进程，不打包）。
不包含、不依赖任何 AGPL 代码（Everything 的 spreadsheet 为 AGPL-3.0-only，未复用）。
"""

from __future__ import annotations

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
    "表格：读写标准 .xlsx 工作簿、公式、图表与导出",
    "基于 openpyxl 读写 Excel 2007+ (.xlsx) 文件；公式按 Excel 语法写入（以 = 开头），"
    "用 LibreOffice 无头模式求值与导出 PDF/ODS。",
    limits=[
        "只读写 .xlsx；.xls / .xlsm / .ods / .csv 输入暂不支持",
        "公式以文本写入，求值依赖 LibreOffice（read --computed、export）",
        "图表仅支持 bar / line / pie，数据按列组成系列",
        "单次 read 最多返回 20000 个单元格",
    ],
)


# ----------------------------------------------------------------------
# helpers
def _check_ext(path: Path) -> None:
    if path.suffix.lower() not in XLSX_EXT:
        raise FoxError("USAGE", f"只支持 .xlsx 文件：{path.name}", hint="文件名以 .xlsx 结尾")


def _load(ctx: Context, path: Path, data_only: bool = False):
    _check_ext(path)
    if not path.exists():
        raise FoxError("NOT_FOUND", f"文件不存在：{ctx.rel(path)}", hint="先用 foxos sheets create 创建")
    try:
        return openpyxl.load_workbook(path, data_only=data_only)
    except (InvalidFileException, KeyError, OSError, ValueError) as e:
        raise FoxError("USAGE", f"无法作为 xlsx 打开：{ctx.rel(path)}（{e}）") from e


def _sheet(wb, name: str | None, create: bool = False):
    if not name:
        return wb.active
    if name in wb.sheetnames:
        return wb[name]
    if create:
        return wb.create_sheet(name)
    raise FoxError("NOT_FOUND", f"工作表不存在：{name}", details={"sheets": wb.sheetnames})


def _bounds(ref: str):
    try:
        min_col, min_row, max_col, max_row = range_boundaries(ref.upper().replace("$", ""))
    except (ValueError, TypeError, CellCoordinatesException) as e:
        raise FoxError("USAGE", f"无效的单元格区域：{ref}", hint="使用 A1 记法，如 A1:C10") from e
    if None in (min_col, min_row, max_col, max_row):
        raise FoxError("USAGE", f"区域需要明确的起止单元格：{ref}", hint="如 A1:C10")
    return min_col, min_row, max_col, max_row


def _check_cell(ref: str) -> str:
    ref = ref.strip().upper().replace("$", "")
    try:
        col, row = coordinate_from_string(ref)
        ok = row >= 1 and row <= 1048576 and 1 <= column_index_from_string(col) <= 16384
    except (ValueError, CellCoordinatesException):
        ok = False
    if not ok:
        raise FoxError("USAGE", f"无效的单元格地址：{ref}", hint="使用 A1 记法，如 B2（列 A–XFD，行 1–1048576）")
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
        raise FoxError("CONFLICT", f"文件已存在：{ctx.rel(file)}", hint="使用 --force 覆盖（会保留上一版本）")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    if headers:
        ws.append([str(h) for h in headers])
    saved = ctx.save_atomic(file, lambda p: wb.save(p))
    return {
        "message": f"已创建 {ctx.rel(file)}",
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
        raise FoxError("USAGE", f"区域包含 {n} 个单元格，超过单次上限 {MAX_CELLS}", hint="用 --range 分批读取")
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
        out["note"] = "rows 中以 = 开头的是公式；加 --computed 用 LibreOffice 求值"
    return out


def write(ctx: Context, file: Path, cells: dict, sheet: str | None = None, create_sheet: bool = False) -> dict:
    if not cells:
        raise FoxError("USAGE", "没有要写入的单元格", hint="例如：foxos sheets write data.xlsx A1=Month B1=Sales B5==SUM(B2:B4)")
    wb = _load(ctx, file)
    ws = _sheet(wb, sheet, create=create_sheet)
    written, formulas = [], 0
    normalized = {}
    for ref, value in cells.items():
        r = _check_cell(str(ref))
        if value is not None and not isinstance(value, (str, int, float, bool)):
            raise FoxError("USAGE", f"{r} 的值类型不支持：{type(value).__name__}")
        normalized[r] = value
    for r, value in normalized.items():
        ws[r] = value
        written.append(r)
        if isinstance(value, str) and value.startswith("="):
            formulas += 1
    saved = ctx.save_atomic(file, lambda p: wb.save(p))
    return {
        "message": f"已写入 {len(written)} 个单元格到 {ctx.rel(file)}!{ws.title}",
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
        raise FoxError("USAGE", f"数据区域 {data} 太小", hint="首行为系列名称时至少需要两行；否则加 --no-header")
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
        raise FoxError("USAGE", "饼图只能有一个数据系列（一列）")
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
        "message": f"已在 {ctx.rel(file)}!{ws.title} 的 {anchor} 创建{type}图表",
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
        raise FoxError("USAGE", f"不支持导出为 .{fmt}", hint="支持 .csv / .pdf / .ods / .xlsx")
    if output.exists() and not force:
        raise FoxError("CONFLICT", f"输出文件已存在：{ctx.rel(output)}", hint="使用 --force 覆盖")
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
                    warnings.append("未找到 LibreOffice，公式以文本形式导出")

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
                warnings.append("PDF/ODS 导出包含所有工作表，--sheet 被忽略")
            staged = tdp / "in" / (output.stem + file.suffix)
            staged.parent.mkdir()
            shutil.copy2(file, staged)
            converted = office.convert(staged, fmt, tdp / "out")
            saved = ctx.save_atomic(output, lambda p: shutil.copy2(converted, p))
    return {
        "message": f"已导出 {ctx.rel(file)} → {ctx.rel(output)}",
        "file": ctx.rel(file),
        "output": ctx.rel(output),
        "format": fmt,
        "bytes": output.stat().st_size,
        "warnings": warnings,
        **saved,
    }


# ----------------------------------------------------------------------
FILE = Param("file", "string", "工作簿路径（工作空间内，.xlsx）", required=True, positional=True, metavar="FILE")
SHEET = Param("sheet", "string", "工作表名称，默认当前活动工作表", cli_short="-s")

register(Command(
    APP, "create", "新建一个 .xlsx 工作簿",
    create,
    params=[
        Param("file", "string", "要创建的工作簿路径（.xlsx）", required=True, positional=True, path="write", metavar="FILE"),
        Param("sheet", "string", "第一个工作表的名称", default="Sheet1", cli_short="-s"),
        Param("headers", "array", "第一行表头，逗号分隔（CLI）或字符串数组（工具接口）", items={"type": "string"}),
        Param("force", "boolean", "文件已存在时覆盖（上一版本会保存到 .foxos/versions）", default=False, cli_short="-f"),
    ],
    examples=[
        "foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales",
        "foxos sheets create report/q1.xlsx --force --json",
    ],
    limits=["只创建 .xlsx；父目录不存在时自动创建"],
    permission="create",
))

register(Command(
    APP, "read", "读取工作表单元格（公式、图表；可选用 LibreOffice 求值）",
    read,
    params=[
        Param("file", "string", "工作簿路径", required=True, positional=True, path="read", metavar="FILE"),
        SHEET,
        Param("range", "string", "A1 记法区域，如 A1:C10；默认整个已用区域", cli_short="-r"),
        Param("computed", "boolean", "用 LibreOffice 重算公式，额外返回 values（不修改原文件）", default=False),
    ],
    examples=[
        "foxos sheets read sales.xlsx",
        "foxos sheets read sales.xlsx --range A1:B13 --computed --json",
    ],
    limits=[f"单次最多 {MAX_CELLS} 个单元格", "--computed 需要 LibreOffice"],
    permission="read",
))

register(Command(
    APP, "write", "写入单元格值或公式（CELL=VALUE，以 = 开头为公式）",
    write,
    params=[
        Param("file", "string", "工作簿路径", required=True, positional=True, path="write", metavar="FILE"),
        Param(
            "cells", "object",
            "要写入的单元格：{\"A1\": \"Month\", \"B2\": 120, \"B14\": \"=SUM(B2:B13)\"}；"
            "CLI 中写成 A1=Month B2=120 B14==SUM(B2:B13)，数字自动识别，TRUE/FALSE 为布尔，空值清空单元格",
            required=True, positional=True, cli_kv=True, metavar="CELL=VALUE",
        ),
        SHEET,
        Param("create_sheet", "boolean", "工作表不存在时新建", default=False),
    ],
    examples=[
        "foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135",
        "foxos sheets write sales.xlsx 'B14==SUM(B2:B13)' --sheet Sales",
        "foxos sheets write sales.xlsx --cells-json '{\"C2\": \"=B2*1.1\"}' --json",
    ],
    limits=["公式按 Excel 英文函数名写入，不在写入时校验或求值", "不支持写入样式、合并单元格（阶段 0）"],
    permission="modify",
))

register(Command(
    APP, "chart create", "基于单元格区域创建原生 Excel 图表",
    chart_create,
    params=[
        Param("file", "string", "工作簿路径", required=True, positional=True, path="write", metavar="FILE"),
        Param("type", "string", "图表类型", required=True, enum=CHART_TYPES, cli_short="-t"),
        Param("data", "string", "数据区域（按列为系列，首行默认为系列名），如 B1:B13", required=True, cli_short="-d"),
        Param("categories", "string", "分类（X 轴）区域，如 A2:A13", cli_short="-c"),
        Param("title", "string", "图表标题"),
        SHEET,
        Param("anchor", "string", "图表左上角所在单元格，默认放在数据右侧", cli_short="-a"),
        Param("x_title", "string", "X 轴标题（bar/line）"),
        Param("y_title", "string", "Y 轴标题（bar/line）"),
        Param("no_header", "boolean", "数据区域首行不是系列名", default=False),
    ],
    examples=[
        "foxos sheets chart create sales.xlsx --type bar --data B1:B13 --categories A2:A13 --title '月度销售额'",
        "foxos sheets chart create sales.xlsx -t line -d B1:C13 -c A2:A13 --anchor E20 --json",
    ],
    limits=["仅 bar / line / pie", "饼图只能一个系列", "图表样式、颜色暂不可配置"],
    permission="modify",
))

register(Command(
    APP, "chart list", "列出工作簿中的图表",
    chart_list,
    params=[
        Param("file", "string", "工作簿路径", required=True, positional=True, path="read", metavar="FILE"),
        SHEET,
    ],
    examples=["foxos sheets chart list sales.xlsx --json"],
    permission="read",
))

register(Command(
    APP, "export", "导出为 csv / pdf / ods / xlsx（格式由输出文件扩展名决定）",
    export,
    params=[
        Param("file", "string", "源工作簿路径", required=True, positional=True, path="read", metavar="FILE"),
        Param("output", "string", "输出路径：.csv / .pdf / .ods / .xlsx", required=True, positional=True, path="write", metavar="OUTPUT"),
        SHEET,
        Param("force", "boolean", "输出文件已存在时覆盖", default=False, cli_short="-f"),
    ],
    examples=[
        "foxos sheets export sales.xlsx sales.csv",
        "foxos sheets export sales.xlsx out/sales.pdf --force --json",
    ],
    limits=["csv 只导出一个工作表，公式导出为求值结果（需 LibreOffice，否则导出公式文本）", "pdf / ods 需要 LibreOffice"],
    permission="create",
))
