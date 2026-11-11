"""Documents（文档）应用：标准 .docx，底层 python-docx（MIT）；PDF / ODT / HTML 导出走 LibreOffice。"""

from __future__ import annotations

from foxos.i18n import tr
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
    tr("docs.documents_read_and_write_standard"),
    tr("docs.reads_and_writes_word_2007_docx_with"),
    limits=[tr("docs.only_docx_is_read_and_written_doc"), tr("docs.images_headers_footers_and_comments"), tr("docs.replacement_happens_within_a")],
)


def _open(ctx: Context, path: Path):
    check_ext(path, EXT, tr("docs.documents"))
    require_exists(ctx, path, tr("docs.create_it_first_with_foxos_docs"))
    try:
        return docx.Document(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as e:
        raise FoxError("USAGE", tr("docs.cannot_open_as_docx", ctx.rel(path), e)) from e


def _style_ok(d, style: str) -> str:
    try:
        d.styles[style]
    except KeyError as e:
        names = sorted(s.name for s in d.styles if s.type == 1)[:40]
        raise FoxError("USAGE", tr("docs.the_document_has_no_style", style), details={"styles": names}) from e
    return style


def create(ctx: Context, file: Path, title: str | None = None, force: bool = False) -> dict:
    check_ext(file, EXT, tr("docs.documents"))
    if file.exists() and not force:
        raise FoxError("CONFLICT", tr("common.file_already_exists", ctx.rel(file)), hint=tr("common.use_force_to_overwrite_the_previous"))
    d = docx.Document()
    if title:
        d.add_heading(title, level=0)
        d.core_properties.title = title
    saved = ctx.save_atomic(file, lambda p: d.save(str(p)))
    return {"message": tr("common.created", ctx.rel(file)), "file": ctx.rel(file), "title": title, **saved}


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
        raise FoxError("USAGE", tr("docs.nothing_to_append"), hint=tr("docs.foxos_docs_append_report_docx_first"))
    if heading is not None and not 0 <= heading <= 9:
        raise FoxError("USAGE", tr("docs.heading_must_be_0_9"))
    added = 0
    for t in text or []:
        if heading is not None:
            d.add_heading(str(t), level=heading)
        else:
            d.add_paragraph(str(t), style=_style_ok(d, style) if style else None)
        added += 1
    if table:
        if not all(isinstance(r, list) for r in table) or not table:
            raise FoxError("USAGE", tr("docs.table_must_be_a_2_d_array_such_as"))
        cols = max(len(r) for r in table)
        tb = d.add_table(rows=len(table), cols=cols)
        tb.style = "Table Grid"
        for ri, r in enumerate(table):
            for ci in range(cols):
                tb.cell(ri, ci).text = "" if ci >= len(r) or r[ci] is None else str(r[ci])
    saved = ctx.save_atomic(file, lambda p: d.save(str(p)))
    return {"message": tr("docs.appended_paragraph_s_to", ctx.rel(file), added) + (tr("docs.and_1_table") if table else ""),
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
        raise FoxError("USAGE", tr("common.find_cannot_be_empty"))
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
    return {"message": tr("common.replaced_occurrence_s_in", ctx.rel(file), n), "file": ctx.rel(file), "replacements": n, **saved}


def export(ctx: Context, file: Path, output: Path, force: bool = False) -> dict:
    _open(ctx, file)
    fmt = output.suffix.lower().lstrip(".")
    if fmt not in ("pdf", "odt", "html", "txt", "md"):
        raise FoxError("USAGE", tr("common.cannot_export_to", fmt), hint=tr("docs.supported_pdf_odt_html_txt_md"))
    if output.exists() and not force:
        raise FoxError("CONFLICT", tr("common.output_file_already_exists", ctx.rel(output)), hint=tr("common.use_force_to_overwrite"))
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
    return {"message": tr("common.exported", ctx.rel(file), ctx.rel(output)), "file": ctx.rel(file),
            "output": ctx.rel(output), "format": fmt, "bytes": output.stat().st_size, **saved}


FILE = lambda access: Param("file", "string", tr("docs.document_path_docx"), required=True, positional=True, path=access, metavar="FILE")  # noqa: E731

register(Command(APP, "create", tr("docs.create_a_new_docx_document"), create,
                 params=[FILE("write"), Param("title", "string", tr("docs.document_title_written_as_the_first")),
                         Param("force", "boolean", tr("common.overwrite_if_it_exists"), default=False, cli_short="-f")],
                 examples=[tr("docs.foxos_docs_create_report_docx_title")], permission="create"))
register(Command(APP, "read", tr("docs.read_paragraphs_with_style_names"), read,
                 params=[FILE("read")], examples=["foxos docs read report.docx --json"]))
register(Command(APP, "append", tr("docs.append_paragraphs_a_heading_or_a"), append,
                 params=[FILE("write"),
                         Param("text", "array", tr("docs.paragraphs_to_append_one_per"), positional=True, items={"type": "string"}, metavar="TEXT"),
                         Param("style", "string", tr("docs.paragraph_style_word_built_in")),
                         Param("heading", "integer", tr("docs.append_as_a_heading_0_title_1_9")),
                         Param("table", "array", tr("docs.append_a_table_a_2_d_array_use_table"), items={"type": "array"})],
                 examples=[tr("docs.foxos_docs_append_report_docx_1"),
                           tr("docs.foxos_docs_append_report_docx_annual"),
                           tr("docs.foxos_docs_append_report_docx_point"),
                           tr("docs.foxos_docs_append_report_docx_table")],
                 permission="modify"))
register(Command(APP, "replace", tr("docs.find_and_replace_text_body_and"), replace,
                 params=[FILE("write"), Param("find", "string", tr("common.text_to_find"), required=True),
                         Param("replace", "string", tr("common.replace_with"), required=True)],
                 examples=["foxos docs replace report.docx --find 2025 --replace 2026"], permission="modify"))
register(Command(APP, "export", tr("docs.export_to_pdf_odt_html_txt_md_chosen"), export,
                 params=[FILE("read"), Param("output", "string", tr("common.output_path"), required=True, positional=True, path="write", metavar="OUTPUT"),
                         Param("force", "boolean", tr("common.overwrite_the_output_if_it_exists"), default=False, cli_short="-f")],
                 examples=["foxos docs export report.docx report.pdf", "foxos docs export report.docx report.md"],
                 limits=[tr("docs.pdf_odt_html_need_libreoffice")], permission="create"))
