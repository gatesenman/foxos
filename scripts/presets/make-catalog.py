#!/usr/bin/env python3
"""生成 packages/core/foxos/data/env-presets.json（foxos-env-presets/1）。

Linux 预设的大小与 sha256 来自 build/presets/<id>/foxos-<id>.json（build-preset.sh 的产物），
狐狸OS ISO 来自 build/os/release-<ver>/SHA256SUMS；Windows / macOS 只是「配方」，介质在安装时从官方下载。
用法：python3 scripts/presets/make-catalog.py [--release presets-2026.11] [--os-version 0.3.3]
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "packages/core/foxos/data/env-presets.json"
ap = argparse.ArgumentParser()
ap.add_argument("--release", default="presets-2026.11")
ap.add_argument("--os-version", default="0.3.3")
a = ap.parse_args()

FEATURES = ["desktop-xfce", "zh-CN", "node", "bun", "python", "acp-gemini-cli", "foxos-cli", "foxos-mcp", "foxos-bridge-ssh"]
RUNTIME = {"node": "v24.22.2", "bun": "1.3.2", "python": "3.13.9",
           "companion_install": "https://github.com/gatesenman/foxos/releases/download/v0.3.3-windows-preview/install.ps1"}
LINUX = [("debian-12", "Debian 12 bookworm", "debian", "12"), ("ubuntu-24.04", "Ubuntu 24.04 LTS", "ubuntu", "24.04")]

entries = []
for pid, title, fam, ver in LINUX:
    f = ROOT / "build/presets" / pid / f"foxos-{pid}.json"
    if not f.exists():
        old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"entries": []}
        prev = next((e for e in old["entries"] if e["id"] == f"foxos-{pid}"), None)
        if prev:
            entries.append(prev)
        continue
    b = json.loads(f.read_text(encoding="utf-8"))
    entries.append({
        "id": f"foxos-{pid}", "name": f"{title} · 狐狸OS 预设", "guest_os": "linux", "family": fam, "version": ver, "kind": "foxos-image",
        "summary": "XFCE 桌面、默认中文、Node.js / Bun / Python、Gemini CLI（ACP）、foxos 命令与 MCP、SSH 来宾桥",
        "release": a.release, "preset_version": b["version"], "features": FEATURES, "runtime": RUNTIME,
        "disk_gb": b["disk_gb"], "memory_mb": 2048, "cpus": 2,
        "artifacts": {"qcow2": {k: b["qcow2"][k] for k in ("name", "size", "sha256", "parts")},
                      "wsl": {k: b["wsl"][k] for k in ("name", "size", "sha256")}},
        "hosts": {"linux": {"provider": "linux-kvm", "artifact": "qcow2", "arch": ["x86_64"]},
                  "windows": {"provider": "wsl2", "artifact": "wsl", "arch": ["x86_64"]}},
        "unavailable": {"macos": "预设镜像是 x86_64；Apple 芯片 Mac 上的 arm64 预设尚未发布"},
        "license": "各发行版软件包按各自许可；Node.js、Bun 为 MIT；Gemini CLI 为 Apache-2.0。不含不允许再分发的软件。",
    })

# 狐狸OS ISO 本身作为来宾
rel = ROOT / f"build/os/release-{a.os_version}"
sums = {}
if (rel / "SHA256SUMS").exists():
    for line in (rel / "SHA256SUMS").read_text().splitlines():
        h, n = line.split()
        sums[n.lstrip("*")] = h
iso = f"FoxOS-{a.os_version}-amd64.iso"
if sums:
    parts = sorted(n for n in sums if n.startswith(iso + ".part"))
    entries.append({
        "id": f"foxos-os-{a.os_version}", "name": f"狐狸OS {a.os_version}（可引导 ISO，Live + 安装器）", "guest_os": "linux", "family": "foxos",
        "version": a.os_version, "kind": "foxos-iso", "summary": "狐狸OS 自己作为来宾：XFCE、中文、foxos、人工接管、Calamares 安装器",
        "features": ["desktop-xfce", "zh-CN", "foxos-cli", "foxos-mcp", "calamares"], "memory_mb": 4096, "cpus": 2, "disk_gb": 32,
        "artifacts": {"iso": {"name": iso, "release": f"v{a.os_version}-os-preview", "size": sum(os.path.getsize(rel / p) for p in parts),
                              "sha256": sums[iso], "parts": [{"name": p, "size": os.path.getsize(rel / p), "sha256": sums[p]} for p in parts]}},
        "hosts": {"linux": {"provider": "linux-kvm", "artifact": "iso", "arch": ["x86_64"]},
                  "windows": {"provider": "hyperv", "artifact": "iso", "arch": ["x86_64"]}},
        "unavailable": {"macos": "狐狸OS ISO 是 x86_64"},
    })

WIN = [
    ("windows-11-enterprise-eval", "Windows 11 企业版评估版 · 狐狸OS 预设", "11", "Windows 11 企业版（评估版，90 天）",
     "https://go.microsoft.com/fwlink/?LinkId=2382601&clcid=0x804&culture=zh-cn&country=cn", "https://www.microsoft.com/zh-cn/evalcenter/download-windows-11-enterprise", 8548628480, 4096, 64, True),
    ("windows-server-2025-eval", "Windows Server 2025 评估版 · 狐狸OS 预设", "2025", "Windows Server 2025（评估版，180 天）",
     "https://go.microsoft.com/fwlink/?linkid=2345732&clcid=0x804&culture=zh-cn&country=cn", "https://www.microsoft.com/zh-cn/evalcenter/download-windows-server-2025", 8423151616, 4096, 64, False),
]
for wid, name, ver, edition, url, page, size, mem, disk, tpm in WIN:
    entries.append({
        "id": wid, "name": name, "guest_os": "windows", "family": "windows", "version": ver, "kind": "windows-media",
        "summary": "安装时从微软官方下载中文评估版 ISO，用 autounattend.xml 无人值守安装，首次登录脚本装好 Node.js / Bun / Python / Git、Gemini CLI、狐狸OS Windows 伴侣与 SSH 来宾桥",
        "features": ["desktop", "zh-CN", "node", "bun", "python", "git", "acp-gemini-cli", "foxos-companion", "foxos-bridge-ssh"], "runtime": RUNTIME,
        "media": {"source": "microsoft-evalcenter", "url": url, "page": page, "size": size, "sha256": None, "edition": edition, "language": "zh-CN",
                  "input_locale": "0804:00000804", "timezone": "China Standard Time", "image_index": 1 if ver == "11" else 2,
                  "filename": f"{wid}-zh-cn.iso", "verify": "微软在评估中心页面公布 ISO 的 SHA-256；可用 --sha256 传入核对，否则记录实际 sha256"},
        "license": "微软评估许可；不允许再分发预装镜像，所以狐狸OS 只发布应答文件与脚本。有正式许可的用户可用 --product-key 传入密钥，或用 --iso 指定自己的零售版 ISO。",
        "memory_mb": mem, "cpus": 2, "disk_gb": disk, "tpm": tpm,
        "hosts": {"windows": {"provider": "hyperv", "arch": ["x86_64"]}},
        "unavailable": {"linux": "狐狸OS 主机的产品 VMM 是 cloud-hypervisor，不能从安装光盘安装 Windows（没有安装期的 CD/AHCI 与驱动注入路径）；请在 Windows 伴侣程序里用 Hyper-V 安装",
                        "macos": "macOS 上不提供 Windows 来宾"},
    })
entries.append({
    "id": "macos-latest", "name": "macOS（最新支持版本）· 狐狸OS 预设", "guest_os": "macos", "family": "macos", "version": "latest", "kind": "macos-ipsw",
    "summary": "仅在 Apple 芯片 Mac 上：由 Virtualization.framework 下载 Apple 官方 IPSW 安装 macOS 虚拟机；设置助理完成后运行共享文件夹里的脚本装好 Node.js / Bun / Gemini CLI / foxos",
    "features": ["desktop", "node", "bun", "acp-gemini-cli", "foxos-cli", "foxos-bridge-ssh"], "runtime": RUNTIME,
    "media": {"source": "apple-ipsw", "via": "VZMacOSRestoreImage.fetchLatestSupported", "size": 17179869184},
    "license": "Apple 软件许可只允许在 Apple 硬件上运行的 macOS 中虚拟化 macOS（每台 Mac 最多 2 个额外实例）。不提供任何非 Apple 硬件上的 macOS 镜像。",
    "memory_mb": 8192, "cpus": 4, "disk_gb": 64,
    "hosts": {"macos": {"provider": "macos-vz", "arch": ["aarch64"]}},
    "unavailable": {"linux": "Apple 的软件许可只允许在 Apple 硬件上的 macOS 中虚拟化 macOS；PC 上不提供",
                    "windows": "Apple 的软件许可只允许在 Apple 硬件上的 macOS 中虚拟化 macOS；PC 上不提供"},
})
doc = {"format": "foxos-env-presets/1", "version": a.release, "release_base": "https://github.com/gatesenman/foxos/releases/download",
       "note": "狐狸OS 预设系统。Linux 与狐狸OS 镜像发布在 GitHub Releases（分卷、sha256）；Windows / macOS 只发布配方，介质安装时从官方下载。", "entries": entries}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(entries)} entries)")
