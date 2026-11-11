"""docs / slides / sheets 共用的导出逻辑：交给 LibreOffice 无头转换。"""

from __future__ import annotations

from foxos.i18n import tr
import shutil
import tempfile
from pathlib import Path

from .. import office
from ..errors import FoxError
from ..kernel import Context


def check_ext(path: Path, exts: set[str], kind: str) -> None:
    if path.suffix.lower() not in exts:
        raise FoxError("USAGE", tr("office_common.only_files_are_supported", ' / '.join(sorted(exts)), path.name), hint=tr("office_common.file_names_end_in", kind, sorted(exts)[0]))


def require_exists(ctx: Context, path: Path, create_hint: str) -> None:
    if not path.exists():
        raise FoxError("NOT_FOUND", tr("common.file_not_found", ctx.rel(path)), hint=create_hint)


def lo_export(ctx: Context, src: Path, output: Path, fmt: str) -> dict:
    """用 LibreOffice 把 src 转成 fmt，原子保存到 output。"""
    with tempfile.TemporaryDirectory(prefix="foxos-") as td:
        tdp = Path(td)
        staged = tdp / "in" / (output.stem + src.suffix)
        staged.parent.mkdir()
        shutil.copy2(src, staged)
        converted = office.convert(staged, fmt, tdp / "out")
        return ctx.save_atomic(output, lambda p: shutil.copy2(converted, p))
