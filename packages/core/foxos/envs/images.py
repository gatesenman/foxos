"""环境镜像：官方发行版 rootfs 目录与狐狸OS 镜像格式（.foxenv）。

.foxenv = 普通 tar 归档，内含：
  manifest.json      {"format": "foxenv/1", "name", "version", "arch", "created", "source", "rootfs": "rootfs.tar.zst", "sha256", "size"}
  rootfs.tar.zst     根文件系统（tar，zstd 压缩）
导入时校验 sha256；在线目录中的镜像同样逐个校验官方发布的 sha256。
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from ..errors import FoxError

ARCH = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}.get(platform.machine().lower(), platform.machine())
DEB_ARCH = {"x86_64": "amd64", "aarch64": "arm64"}.get(ARCH, ARCH)

CATALOG = [
    {"id": "alpine-3.20", "name": "Alpine Linux 3.20", "size_mb": 3.5,
     "url": f"https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/{ARCH}/alpine-minirootfs-3.20.3-{ARCH}.tar.gz",
     "sha256_url": f"https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/{ARCH}/alpine-minirootfs-3.20.3-{ARCH}.tar.gz.sha256",
     "shell": "/bin/sh", "packages": "apk add"},
    {"id": "ubuntu-24.04", "name": "Ubuntu 24.04 LTS（ubuntu-base）", "size_mb": 29,
     "url": f"https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/ubuntu-base-24.04.5-base-{DEB_ARCH}.tar.gz",
     "sha256_url": "https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/SHA256SUMS",
     "shell": "/bin/bash", "packages": "apt-get install"},
    {"id": "ubuntu-22.04", "name": "Ubuntu 22.04 LTS（ubuntu-base）", "size_mb": 28,
     "url": f"https://cdimage.ubuntu.com/ubuntu-base/releases/22.04/release/ubuntu-base-22.04.5-base-{DEB_ARCH}.tar.gz",
     "sha256_url": "https://cdimage.ubuntu.com/ubuntu-base/releases/22.04/release/SHA256SUMS",
     "shell": "/bin/bash", "packages": "apt-get install"},
]


def _fetch(url: str, dest: Path, progress=None) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "foxos-env"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        got = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            got += len(b)
            if progress:
                progress(got, total)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _expected_sha(entry: dict, filename: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(entry["sha256_url"], headers={"User-Agent": "foxos-env"}), timeout=30) as r:
        text = r.read().decode("utf-8", "replace")
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == filename:
            return parts[0].lower()
    if re.fullmatch(r"[0-9a-f]{64}", text.strip().split()[0] if text.strip() else ""):
        return text.strip().split()[0]
    raise FoxError("ERROR", f"在官方校验文件中找不到 {filename}")


def extract_rootfs(archive: Path, dest: Path) -> None:
    """用系统 tar 解包（保留绝对符号链接；跳过无特权无法创建的设备节点）。"""
    dest.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zst" or archive.name.endswith(".tar.zst"):
        import zstandard
        with open(archive, "rb") as f:
            dctx = zstandard.ZstdDecompressor()
            p = subprocess.Popen(["tar", "-x", "--no-same-owner", "--no-same-permissions", "--exclude=./dev/*", "-C", str(dest)], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            dctx.copy_stream(f, p.stdin)
            p.stdin.close()
            err = p.stderr.read().decode()
            if p.wait() not in (0, 2):
                raise FoxError("ERROR", f"解包失败：{err[-500:]}")
        return
    r = subprocess.run(["tar", "-x", "--no-same-owner", "--exclude=./dev/*", "-f", str(archive), "-C", str(dest)], capture_output=True, text=True)
    if r.returncode not in (0, 2):
        raise FoxError("ERROR", f"解包失败：{r.stderr[-500:]}")


def pull(entry_or_url: str, images_dir: Path, sha256: str | None = None, progress=None) -> dict:
    entry = next((c for c in CATALOG if c["id"] == entry_or_url), None)
    url = entry["url"] if entry else entry_or_url
    if not re.match(r"^https://", url) and not Path(url).exists():
        raise FoxError("USAGE", "镜像必须是目录中的 ID、https:// 地址或本地文件")
    image_id = entry["id"] if entry else re.sub(r"[^a-z0-9.-]+", "-", Path(url.split("?")[0]).name.lower()).strip("-")[:60]
    out = images_dir / image_id
    if (out / "manifest.json").exists():
        return json.loads((out / "manifest.json").read_text())
    tmp = Path(tempfile.mkdtemp(prefix="foxos-img-", dir=images_dir))
    try:
        fname = Path(url.split("?")[0]).name
        arc = tmp / fname
        if Path(url).exists():
            shutil.copy2(url, arc)
        else:
            _fetch(url, arc, progress)
        got = _sha256(arc)
        want = sha256 or (_expected_sha(entry, fname) if entry else None)
        if want and got != want.lower():
            raise FoxError("CONFLICT", f"sha256 不匹配：期望 {want}，实际 {got}")
        if fname.endswith(".foxenv"):
            return import_foxenv(arc, images_dir)
        extract_rootfs(arc, tmp / "rootfs")
        m = {"format": "foxenv/1", "id": image_id, "name": entry["name"] if entry else image_id, "arch": ARCH, "source": url, "sha256": got,
             "verified": bool(want), "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "shell": entry["shell"] if entry else "/bin/sh"}
        (tmp / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1))
        arc.unlink()
        tmp.rename(out)
        return m
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


def write_foxenv(rootfs_dirs: list[Path], dest: Path, meta: dict) -> dict:
    """把一组目录（下层在前，上层覆盖）打包成 .foxenv。"""
    import zstandard
    tmp = Path(tempfile.mkdtemp(prefix="foxos-export-"))
    try:
        rfs = tmp / "rootfs.tar.zst"
        cctx = zstandard.ZstdCompressor(level=6, threads=-1)
        with open(rfs, "wb") as raw, cctx.stream_writer(raw) as zw:
            tar = subprocess.Popen(["tar", "-c", "--numeric-owner", "--owner=0", "--group=0", "-f", "-", *sum((["-C", str(d), "."] for d in rootfs_dirs), [])],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            shutil.copyfileobj(tar.stdout, zw)
            err = tar.stderr.read().decode()
            if tar.wait() not in (0, 1):
                raise FoxError("ERROR", f"打包失败：{err[-500:]}")
        m = {"format": "foxenv/1", **meta, "arch": ARCH, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "rootfs": "rootfs.tar.zst", "sha256": _sha256(rfs), "size": rfs.stat().st_size}
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(dest, "w") as t:
            data = json.dumps(m, ensure_ascii=False, indent=1).encode()
            ti = tarfile.TarInfo("manifest.json"); ti.size = len(data); ti.mtime = int(time.time())
            t.addfile(ti, io.BytesIO(data))
            t.add(rfs, "rootfs.tar.zst")
        return m
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def read_foxenv(arc: Path, work: Path) -> tuple[dict, Path]:
    with tarfile.open(arc, "r") as t:
        m = json.loads(t.extractfile("manifest.json").read())
        if m.get("format") != "foxenv/1":
            raise FoxError("USAGE", "不是狐狸OS 环境镜像（foxenv/1）")
        t.extract("rootfs.tar.zst", work, filter="data")
    rfs = work / "rootfs.tar.zst"
    if _sha256(rfs) != m["sha256"]:
        raise FoxError("CONFLICT", "镜像校验失败（sha256 不匹配），文件可能损坏或被篡改")
    return m, rfs


def import_foxenv(arc: Path, images_dir: Path, image_id: str | None = None) -> dict:
    work = Path(tempfile.mkdtemp(prefix="foxos-import-", dir=images_dir))
    try:
        m, rfs = read_foxenv(arc, work)
        iid = image_id or m.get("id") or f"import-{m['sha256'][:12]}"
        out = images_dir / iid
        if (out / "manifest.json").exists():
            return json.loads((out / "manifest.json").read_text())
        extract_rootfs(rfs, work / "rootfs")
        rfs.unlink()
        m = {**m, "id": iid, "source": str(arc), "verified": True}
        (work / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1))
        work.rename(out)
        return m
    finally:
        if work.exists():
            shutil.rmtree(work, ignore_errors=True)
