"""Documents（文档）应用：标准 .docx，底层 python-docx（MIT）；PDF / ODT / HTML 导出走 LibreOffice。"""

from __future__ import annotations

from pathlib import Path

import docx
from docx.opc.exceptions import PackageNotFoundError

from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app
from ._office_common import check_ext, lo_export, require_exists

APP = "docs"
EXT = {".docx"}

register_app(
    APP,
    "文档：读写标准 .docx（段落、标题、列表、表格），替换文本与导出",
    "基于 python-docx 读写 Word 2007+ (.docx)。样式名使用 Word 内置英文样式名，如 Heading 1、List Bullet。",
    limits=["只读写 .docx；.doc / .odt 输入暂不支持", "图片、页眉页脚、批注暂不可编辑", "替换在段落内进行，跨段落的文本不会匹配"],
)


def _open(ctx: Context, path: Path):
    check_ext(path, EXT, "文档")
    require_exists(ctx, path, "先用 foxos docs create 创建")
    try:
        return docx.Document(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as e:
        raise FoxError("USAGE", f"无法作为 docx 打开：{ctx.rel(path)}（{e}）") from e


def _style_ok(d, style: str) -> str:
    try:
        d.styles[style]
    except KeyError as e:
        names = sorted(s.name for s in d.styles if s.type == 1)[:40]
        raise FoxError("USAGE", f"文档中没有样式：{style}", details={"styles": names}) from e
    return style


def create(ctx: Context, file: Path, title: str | None = None, force: bool = False) -> dict:
    check_ext(file, EXT, "文档")
    if file.exists() and not force:
        raise FoxError("CONFLICT", f"文件已存在：{ctx.rel(file)}", hint="使用 --force 覆盖（会保留上一版本）")
    d = docx.Document()
    if title:
        d.add_heading(title, level=0)
        d.core_properties.title = title
    saved = ctx.save_atomic(file, lambda p: d.save(str(p)))
    return {"message": f"已创建 {ctx.rel(file)}", "file": ctx.rel(file), "title": title, **saved}


def read(ctx: Context, file: Path) -> dict:
    d = _open(ctx, file)
    paragraphs = [
        {"index": i, "style": p.style.name if p.style is not None else None, "text": p.text}
        for i, p in enumerate(d.paragraphs)
    ]
    tables = [{"index": i, "rows": [[c.text for c in r.cells] for r in t.rows]} for i, t in enumerate(d.tables)]
    words = sum(len(p["text"].split()) for p in paragraphs)
    return {"file": ctx.rel(file), "title": d.core_properties.title or None, "paragraphs": paragraphs,
            "tables": tables, "stats": {"paragraphs": len(paragraphs), "tables": len(tables), "words": words,
                                        "characters": sum(len(p["text"]) for p in paragraphs)}}


def append(ctx: Context, file: Path, text: list, style: str | None = None, heading: int | None = None,
           table: list | None = None) -> dict:
    d = _open(ctx, file)
    if not text and not table:
        raise FoxError("USAGE", "没有要追加的内容", hint="foxos docs append report.docx '第一段' '第二段' 或 --table-json")
    if heading is not None and not 0 <= heading <= 9:
        raise FoxError("USAGE", "heading 取值 0–9")
    added = 0
    for t in text or []:
        if heading is not None:
            d.add_heading(str(t), level=heading)
        else:
            d.add_paragraph(str(t), style=_style_ok(d, style) if style else None)
        added += 1
    if table:
        if not all(isinstance(r, list) for r in table) or not table:
            raise FoxError("USAGE", "table 必须是二维数组，如 [[\"月份\",\"销售额\"],[\"1月\",120]]")
        cols = max(len(r) for r in table)
        tb = d.add_table(rows=len(table), cols=cols)
        tb.style = "Table Grid"
        for ri, r in enumerate(table):
            for ci in range(cols):
                tb.cell(ri, ci).text = "" if ci >= len(r) or r[ci] is None else str(r[ci])
    saved = ctx.save_atomic(file, lambda p: d.save(str(p)))
    return {"message": f"已向 {ctx.rel(file)} 追加 {added} 段" + ("和 1 个表格" if table else ""),
            "file": ctx.rel(file), "paragraphs_added": added, "table_added": bool(table),
            "paragraphs_total": len(d.paragraphs), **saved}


def _replace_in_paragraph(p, find: str, repl: str) -> int:
    if find not in p.text:
        return 0
    n = 0
    for r in p.runs:  # 先在单个 run 内替换，保留格式
        if find in r.text:
            n += r.text.count(find)
            r.text = r.text.replace(find, repl)
    if find in p.text:  # 文本跨 run：合并到第一个 run
        n += p.text.count(find)
        full = p.text.replace(find, repl)
        for i, r in enumerate(p.runs):
            r.text = full if i == 0 else ""
    return n


def replace(ctx: Context, file: Path, find: str, replace: str) -> dict:
    if not find:
        raise FoxError("USAGE", "find 不能为空")
    d = _open(ctx, file)
    n = 0
    for p in d.paragraphs:
        n += _replace_in_paragraph(p, find, replace)
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    n += _replace_in_paragraph(p, find, replace)
    saved = ctx.save_atomic(file, lambda p: d.save(str(p))) if n else {"previous_version": None}
    return {"message": f"在 {ctx.rel(file)} 中替换了 {n} 处", "file": ctx.rel(file), "replacements": n, **saved}


def export(ctx: Context, file: Path, output: Path, force: bool = False) -> dict:
    _open(ctx, file)
    fmt = output.suffix.lower().lstrip(".")
    if fmt not in ("pdf", "odt", "html", "txt", "md"):
        raise FoxError("USAGE", f"不支持导出为 .{fmt}", hint="支持 .pdf / .odt / .html / .txt / .md")
    if output.exists() and not force:
        raise FoxError("CONFLICT", f"输出文件已存在：{ctx.rel(output)}", hint="使用 --force 覆盖")
    if fmt in ("txt", "md"):
        d = docx.Document(str(file))
        blocks: list[tuple[str, str]] = []  # (kind, text)
        for p in d.paragraphs:
            name = p.style.name if p.style is not None else ""
            if fmt == "md" and name == "Title":
                blocks.append(("p", f"# {p.text}"))
            elif fmt == "md" and name.startswith("Heading "):
                lvl = name.split()[-1]
                blocks.append(("p", "#" * (int(lvl) + 1 if lvl.isdigit() else 2) + " " + p.text))
            elif fmt == "md" and name.startswith("List Bullet"):
                blocks.append(("li", f"- {p.text}"))
            elif fmt == "md" and name.startswith("List Number"):
                blocks.append(("li", f"1. {p.text}"))
            else:
                blocks.append(("p", p.text))
        for t in d.tables:
            rows = [[c.text for c in r.cells] for r in t.rows]
            if not rows:
                continue
            if fmt == "md":
                md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])] + ["| " + " | ".join(r) + " |" for r in rows[1:]]
                blocks.append(("p", "\n".join(md)))
            else:
                blocks.append(("p", "\n".join("\t".join(r) for r in rows)))
        out_parts = []
        for i, (kind, text) in enumerate(blocks):
            if i:
                out_parts.append("\n" if (fmt == "txt" or (kind == "li" and blocks[i - 1][0] == "li")) else "\n\n")
            out_parts.append(text)
        body = "".join(out_parts) + "\n"
        saved = ctx.save_atomic(output, lambda p: p.write_text(body, encoding="utf-8"))
    else:
        saved = lo_export(ctx, file, output, "html:XHTML Writer File:UTF8" if fmt == "html" else fmt)
    return {"message": f"已导出 {ctx.rel(file)} → {ctx.rel(output)}", "file": ctx.rel(file),
            "output": ctx.rel(output), "format": fmt, "bytes": output.stat().st_size, **saved}


FILE = lambda access: Param("file", "string", "文档路径（.docx）", required=True, positional=True, path=access, metavar="FILE")  # noqa: E731

register(Command(APP, "create", "新建一个 .docx 文档", create,
                 params=[FILE("write"), Param("title", "string", "文档标题（写成 Title 样式的第一段，并写入文档属性）"),
                         Param("force", "boolean", "已存在时覆盖", default=False, cli_short="-f")],
                 examples=["foxos docs create report.docx --title '2026 年销售分析'"], permission="create"))
register(Command(APP, "read", "读取文档段落（含样式名）、表格与字数统计", read,
                 params=[FILE("read")], examples=["foxos docs read report.docx --json"]))
register(Command(APP, "append", "在文档末尾追加段落、标题或表格", append,
                 params=[FILE("write"),
                         Param("text", "array", "要追加的段落，每个参数一段", positional=True, items={"type": "string"}, metavar="TEXT"),
                         Param("style", "string", "段落样式（Word 内置英文名），如 List Bullet、Quote"),
                         Param("heading", "integer", "作为标题追加：0=Title，1–9=Heading 1–9"),
                         Param("table", "array", "追加表格：二维数组；CLI 中用 --table-json", items={"type": "array"})],
                 examples=["foxos docs append report.docx '一、总体情况' --heading 1",
                           "foxos docs append report.docx '全年销售额 2013 万元。' '同比增长 12%。'",
                           "foxos docs append report.docx '要点一' '要点二' --style 'List Bullet'",
                           "foxos docs append report.docx --table-json '[[\"月份\",\"销售额\"],[\"1月\",120]]'"],
                 permission="modify"))
register(Command(APP, "replace", "查找并替换文本（正文与表格）", replace,
                 params=[FILE("write"), Param("find", "string", "要查找的文本", required=True),
                         Param("replace", "string", "替换为", required=True)],
                 examples=["foxos docs replace report.docx --find 2025 --replace 2026"], permission="modify"))
register(Command(APP, "export", "导出为 pdf / odt / html / txt / md（由扩展名决定）", export,
                 params=[FILE("read"), Param("output", "string", "输出路径", required=True, positional=True, path="write", metavar="OUTPUT"),
                         Param("force", "boolean", "输出已存在时覆盖", default=False, cli_short="-f")],
                 examples=["foxos docs export report.docx report.pdf", "foxos docs export report.docx report.md"],
                 limits=["pdf / odt / html 需要 LibreOffice"], permission="create"))
