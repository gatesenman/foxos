"""调用 LibreOffice（soffice --headless）做公式重算和格式转换。

LibreOffice 是智能体非常熟悉的无头办公工具（MPL-2.0），这里只作为外部进程调用，
不随狐狸OS 打包。找不到时返回 DEPENDENCY_MISSING（退出码 6）。
"""

from __future__ import annotations

from foxos.i18n import tr
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from .errors import FoxError

_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice() -> str | None:
    env = os.environ.get("FOXOS_SOFFICE")
    if env:
        return env if Path(env).exists() else None
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    for c in _CANDIDATES:
        if Path(c).exists():
            return c
    return None


def require_soffice() -> str:
    p = find_soffice()
    if not p:
        raise FoxError(
            "DEPENDENCY_MISSING",
            tr("office.libreoffice_soffice_is_needed_to"),
            hint=tr("office.install_libreoffice_or_set_the_foxos"),
        )
    return p


def convert(src: Path, fmt: str, outdir: Path, timeout: int = 120) -> Path:
    """soffice --headless --convert-to <fmt>，每次使用独立的用户配置目录以支持并发。"""
    soffice = require_soffice()
    outdir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.gettempdir()) / f"foxos-lo-{uuid.uuid4().hex}"
    cmd = [
        soffice,
        f"-env:UserInstallation={profile.as_uri()}",
        "--headless",
        "--norestore",
        "--convert-to",
        fmt,
        "--outdir",
        str(outdir),
        str(src),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise FoxError("ERROR", tr("office.libreoffice_conversion_timed_out_s", timeout)) from e
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    ext = fmt.split(":")[0]
    out = outdir / (src.stem + "." + ext)
    if proc.returncode != 0 or not out.exists():
        raise FoxError("ERROR", tr("office.libreoffice_conversion_failed", (proc.stderr or proc.stdout).strip()[:500]))
    return out


def recalculated_copy(src: Path, tmpdir: Path) -> Path:
    """返回一个由 LibreOffice 重新计算过公式的 xlsx 副本（不修改原文件）。"""
    staged = tmpdir / "in" / src.name
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, staged)
    return convert(staged, "xlsx", tmpdir / "out")
