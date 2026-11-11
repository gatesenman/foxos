#!/usr/bin/env python3
"""检查 Live initrd：casper.conf 的 BUILD_SYSTEM、overlay 模块、不完整的 plymouth。"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path


def iter_newc(data: bytes, start: int = 0):
    off = start
    while off + 110 <= len(data):
        if data[off : off + 6] not in (b"070701", b"070702"):
            return
        namesize = int(data[off + 94 : off + 102], 16)
        filesize = int(data[off + 54 : off + 62], 16)
        name = data[off + 110 : off + 110 + namesize - 1].decode("latin1", "replace")
        data_off = (off + 110 + namesize + 3) & ~3
        end = (data_off + filesize + 3) & ~3
        if name == "TRAILER!!!":
            return
        yield name, data[data_off : data_off + filesize]
        off = end


def split_streams(blob: bytes) -> list[bytes]:
    streams: list[bytes] = []
    off = 0
    zstd_magic = b"\x28\xb5\x2f\xfd"
    while off + 6 < len(blob):
        if blob[off : off + 6] in (b"070701", b"070702"):
            files = list(iter_newc(blob, off))
            # recompute end
            end = off
            for _name, _ in iter_newc(blob, off):
                pass

            def end_of(data: bytes, start: int) -> int:
                o = start
                while o + 110 <= len(data):
                    if data[o : o + 6] not in (b"070701", b"070702"):
                        return o
                    namesize = int(data[o + 94 : o + 102], 16)
                    filesize = int(data[o + 54 : o + 62], 16)
                    name = data[o + 110 : o + 110 + namesize - 1].decode("latin1", "replace")
                    data_off = (o + 110 + namesize + 3) & ~3
                    e = (data_off + filesize + 3) & ~3
                    if name == "TRAILER!!!":
                        while e < len(data) and data[e] == 0:
                            e += 1
                        return e
                    o = e
                return o

            end = end_of(blob, off)
            streams.append(blob[off:end])
            off = end
        elif blob[off : off + 4] == zstd_magic:
            import tempfile
            tdir = tempfile.mkdtemp(prefix="foxos-verify-initrd-")
            tmp_in = Path(tdir) / "tail.zst"
            tmp_out = Path(tdir) / "tail.cpio"
            tmp_in.write_bytes(blob[off:])
            r = subprocess.run(["zstd", "-d", "-f", "-q", "-o", str(tmp_out), str(tmp_in)])
            if r.returncode != 0:
                sys.stderr.write("无法解压 initrd 末尾的 zstd 段\n")
                sys.exit(2)
            streams.append(tmp_out.read_bytes())
            break
        elif blob[off : off + 2] == b"\x1f\x8b":
            r = subprocess.run(["gzip", "-dc"], input=blob[off:], capture_output=True)
            if r.returncode != 0:
                sys.stderr.write("无法解压 initrd 末尾的 gzip 段\n")
                sys.exit(2)
            streams.append(r.stdout)
            break
        else:
            # skip padding zeros
            if blob[off] == 0:
                off += 1
                continue
            sys.stderr.write(f"未知的 initrd 段 @ {off}: {blob[off:off+8]!r}\n")
            break
    return streams


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("用法：scripts/os/verify-initrd.sh <initrd>\n")
        return 2
    path = Path(sys.argv[1])
    blob = path.read_bytes()
    files: dict[str, bytes] = {}
    for stream in split_streams(blob):
        for name, content in iter_newc(stream):
            files[name] = content

    errors: list[str] = []
    if "scripts/casper" not in files:
        errors.append("缺少 scripts/casper")
    conf = files.get("etc/casper.conf", b"").decode("utf-8", "replace")
    if 'BUILD_SYSTEM="Ubuntu"' not in conf and "BUILD_SYSTEM=\"Debian\"" not in conf:
        errors.append(
            "etc/casper.conf 的 BUILD_SYSTEM 必须是 Ubuntu 或 Debian"
            f"（否则 casper 会执行 modprobe \"\" -b overlay 而失败）。实际内容：\n{conf}"
        )
    has_overlay = any(
        n.endswith("/overlay.ko") or n.endswith("/overlay.ko.zst") or n.endswith("/overlay.ko.xz")
        for n in files
    )
    builtin = files.get(
        next((n for n in files if n.endswith("modules.builtin")), ""),
        b"",
    ).decode("latin1", "replace")
    if not has_overlay and "overlay.ko" not in builtin:
        errors.append("initrd 里没有 overlay 模块，且 kernel modules.builtin 也未列出")
    plymouth_scripts = [n for n in files if n.endswith("/plymouth") and n.startswith("scripts/")]
    has_plymouthd = any(n.endswith("plymouthd") and files[n] for n in files)
    if plymouth_scripts and not has_plymouthd:
        errors.append(
            "initramfs 含 plymouth 脚本但没有 plymouthd：" + ", ".join(plymouth_scripts)
        )
    if errors:
        sys.stderr.write("initrd 检查失败（%s）：\n" % path)
        for e in errors:
            sys.stderr.write("  - %s\n" % e)
        return 1
    print("initrd 检查通过：casper BUILD_SYSTEM 正确，overlay 已包含，plymouth 完整或已移除")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
