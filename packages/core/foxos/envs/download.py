"""可续传下载与分卷拼接（预设镜像、狐狸OS ISO、Windows 安装介质共用）。

- 写到 `<目标>.partial`，断线后用 HTTP Range 从已下载的字节继续（服务器返回 200 时从头重下）。
- 下载完核对大小与 sha256；不匹配就删掉 .partial 并报 CONFLICT，不留下坏文件。
- 目标已存在且 sha256 一致时直接复用（再次安装同一预设不重复下载）。
- 分卷按顺序拼接，边拼边算 sha256，与目录里整盘的 sha256 对比。
"""

from __future__ import annotations

import hashlib
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from ..errors import FoxError
from ..i18n import tr

CHUNK = 1 << 20
Progress = Callable[..., None]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def _is_local(src: str) -> Path | None:
    if src.startswith("file://"):
        return Path(urllib.request.url2pathname(src[7:]))
    p = Path(src)
    return p if (not src.startswith(("http://", "https://")) and p.exists()) else None


def fetch(url: str, dest: Path, *, size: int | None = None, sha256: str | None = None, progress: Progress | None = None,
          retries: int = 8, timeout: float = 60.0) -> dict:
    """下载 url 到 dest，可续传。返回 {bytes, sha256, verified, resumed, cached}。"""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    want = (sha256 or "").lower() or None
    if dest.exists() and (not size or dest.stat().st_size == size):
        if want is None or sha256_file(dest) == want:
            n = dest.stat().st_size
            if progress:
                progress(bytes=n, bytes_total=n, cached=True)
            return {"bytes": n, "sha256": want or sha256_file(dest), "verified": bool(want), "resumed": 0, "cached": True}
    part = dest.with_name(dest.name + ".partial")
    local = _is_local(url)
    if local is not None:
        shutil.copyfile(local, part)
        resumed = 0
    else:
        resumed = _http_resumable(url, part, size=size, progress=progress, retries=retries, timeout=timeout)
    got_size = part.stat().st_size
    if size and got_size != size:
        raise FoxError("CONFLICT", tr("envs.download.size_mismatch", dest.name, size, got_size), hint=tr("envs.download.retry_hint"))
    got = sha256_file(part)
    if want and got != want:
        part.unlink(missing_ok=True)
        raise FoxError("CONFLICT", tr("common.sha256_mismatch_expected_got", want, got), hint=tr("envs.download.retry_hint"))
    os.replace(part, dest)
    return {"bytes": got_size, "sha256": got, "verified": bool(want), "resumed": resumed, "cached": False}


def _http_resumable(url: str, part: Path, *, size: int | None, progress: Progress | None, retries: int, timeout: float) -> int:
    resumed = 0
    attempt = 0
    while True:
        have = part.stat().st_size if part.exists() else 0
        if size and have > size:
            part.unlink(); have = 0
        if size and have == size:
            return resumed
        headers = {"User-Agent": "foxos-env"}
        if have:
            headers["Range"] = f"bytes={have}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — 目录里的 https 链接或用户给的地址
                code = getattr(r, "status", 200)
                if have and code == 206:
                    mode = "ab"; resumed += 1
                    total = size or (have + int(r.headers.get("Content-Length") or 0))
                else:
                    mode = "wb"; have = 0
                    total = size or int(r.headers.get("Content-Length") or 0)
                got = have
                with open(part, mode) as f:
                    while True:
                        b = r.read(CHUNK)
                        if not b:
                            break
                        f.write(b)
                        got += len(b)
                        if progress:
                            progress(bytes=got, bytes_total=total, resumed=resumed)
                if total and got < total:
                    raise urllib.error.URLError(f"short read {got}/{total}")
                return resumed
        except urllib.error.HTTPError as e:
            if e.code == 416 and have:       # 已经下完（Range 超出）
                return resumed
            if e.code in (403, 404, 410):
                raise FoxError("NOT_FOUND", tr("envs.download.http_error", e.code, url)) from e
            err = e
        except (urllib.error.URLError, OSError, ConnectionError, TimeoutError) as e:
            err = e
        attempt += 1
        if attempt > retries:
            raise FoxError("ERROR", tr("envs.download.failed_after_retries", url, retries, err),
                           hint=tr("envs.download.resume_hint"))
        time.sleep(min(30.0, 0.5 * 2 ** attempt))


def assemble(parts: list[Path], dest: Path, *, sha256: str | None = None, size: int | None = None, progress: Progress | None = None) -> dict:
    """按顺序拼接分卷到 dest，边写边算 sha256；不匹配则删除并报 CONFLICT。"""
    dest = Path(dest)
    tmp = dest.with_name(dest.name + ".assembling")
    h = hashlib.sha256()
    total = sum(p.stat().st_size for p in parts)
    done = 0
    with open(tmp, "wb") as out:
        for p in parts:
            with open(p, "rb") as f:
                for b in iter(lambda: f.read(CHUNK), b""):
                    out.write(b); h.update(b); done += len(b)
                    if progress:
                        progress(bytes=done, bytes_total=total)
    got = h.hexdigest()
    if size and done != size:
        tmp.unlink(missing_ok=True)
        raise FoxError("CONFLICT", tr("envs.download.size_mismatch", dest.name, size, done))
    if sha256 and got != sha256.lower():
        tmp.unlink(missing_ok=True)
        raise FoxError("CONFLICT", tr("common.sha256_mismatch_expected_got", sha256, got))
    os.replace(tmp, dest)
    return {"bytes": done, "sha256": got, "verified": bool(sha256)}


def free_bytes(path: Path) -> int:
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free
