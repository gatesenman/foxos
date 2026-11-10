#!/usr/bin/env python3
"""生成版本化的系统目录 packages/core/foxos/data/env-catalog.json（格式 foxos-env-catalog/1）。

来源：
  * microsoft/WSL 的 distributions/DistributionInfo.json（MIT，快照在 data/wsl/，见 NOTICE.md）——wsl --install 使用的官方清单，含下载地址与 sha256；
  * Rocky Linux 官方 WSL 镜像（dl.rockylinux.org，含 CHECKSUM 文件）；
  * Alpine 官方 minirootfs；
  * LXC 镜像服务器 images.linuxcontainers.org（构建每天滚动，安装时现场解析最新构建与 SHA256SUMS）；
  * Windows 来宾：Windows Sandbox、Hyper-V（用户 ISO 或微软评估中心镜像）；
  * macOS 来宾：列出但禁用并说明原因。
用法：python scripts/gen_env_catalog.py [--refresh]（--refresh 先重新下载 DistributionInfo.json）
"""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "packages/core/foxos/data"
SNAP = DATA / "wsl/DistributionInfo.json"
SRC = "https://raw.githubusercontent.com/microsoft/WSL/master/distributions/DistributionInfo.json"

FAMILY = {"Ubuntu": "ubuntu", "openSUSE": "opensuse", "RLCPlus": "rocky", "SUSE": "sles", "kali": "kali", "Debian": "debian",
          "AlmaLinux": "almalinux", "archlinux": "arch", "Fedora": "fedora", "eLxr": "elxr", "AzureLinux": "azurelinux"}


def slug(s):
    return "".join(c if c.isalnum() or c in ".-" else "-" for c in s.lower()).strip("-")


def main():
    if "--refresh" in sys.argv:
        SNAP.write_bytes(urllib.request.urlopen(SRC, timeout=60).read())
    info = json.loads(SNAP.read_text(encoding="utf-8"))
    entries = []
    modern_names = set()
    alias = next((d for d in info["ModernDistributions"].get("Ubuntu", []) if d["Name"] == "Ubuntu"), None)
    alias_url = ((alias or {}).get("Amd64Url") or {}).get("Url")
    for fam, lst in info["ModernDistributions"].items():
        for d in lst:
            if d["Name"] == "Ubuntu" and fam == "Ubuntu":
                continue  # 别名，指向最新 LTS
            modern_names.add(d["Name"])
            a = d.get("Amd64Url") or {}
            e = {"id": "wsl-" + slug(d["Name"]), "name": d["FriendlyName"], "family": FAMILY.get(fam, slug(fam)), "guest_os": "linux",
                 "arch": ["x86_64"] + (["aarch64"] if d.get("Arm64Url") else []), "providers": ["wsl2", "linux-ns"],
                 "source": {"kind": "rootfs", "url": a.get("Url"), "sha256": (a.get("Sha256") or "").removeprefix("0x").lower() or None,
                            "wsl_name": d["Name"], "origin": "microsoft/WSL DistributionInfo.json"},
                 "default": bool(alias_url) and a.get("Url") == alias_url}
            if d.get("Arm64Url"):
                e["source"]["arm64"] = {"url": d["Arm64Url"]["Url"], "sha256": d["Arm64Url"]["Sha256"].removeprefix("0x").lower()}
            entries.append(e)
    for d in info.get("Distributions", []):
        if d["Name"] in modern_names or d["Name"] in ("Ubuntu", "Debian", "kali-linux", "openSUSE-Tumbleweed"):
            continue
        fam = "oracle" if d["Name"].startswith("Oracle") else "sles" if d["Name"].startswith("SUSE") else slug(d["Name"])
        entries.append({"id": "wsl-" + slug(d["Name"]), "name": d.get("FriendlyName", d["Name"]), "family": fam, "guest_os": "linux", "arch": ["x86_64"],
                        "providers": ["wsl2"], "source": {"kind": "wsl-store", "wsl_name": d["Name"], "origin": "microsoft/WSL DistributionInfo.json（应用商店包）"}})
    for v, f in (("9", "Rocky-9-WSL-Base.latest.x86_64.wsl"), ("10", "Rocky-10-WSL-Base.latest.x86_64.wsl")):
        base = f"https://dl.rockylinux.org/pub/rocky/{v}/images/x86_64/"
        entries.append({"id": f"rocky-{v}", "name": f"Rocky Linux {v}", "family": "rocky", "guest_os": "linux", "arch": ["x86_64"], "providers": ["wsl2", "linux-ns"],
                        "source": {"kind": "rootfs", "url": base + f, "sha256_url": base + f + ".CHECKSUM", "origin": "Rocky Linux 官方 WSL 镜像"}})
    entries.append({"id": "alpine", "name": "Alpine Linux（最新稳定版）", "family": "alpine", "guest_os": "linux", "arch": ["x86_64", "aarch64"], "providers": ["wsl2", "linux-ns"],
                    "source": {"kind": "alpine", "branch": "latest-stable", "origin": "Alpine 官方 minirootfs（latest-releases.yaml 提供 sha256）"}})
    for distro, rel, name, fam in (("oracle", "9", "Oracle Linux 9", "oracle"), ("oracle", "10", "Oracle Linux 10", "oracle"), ("rockylinux", "9", "Rocky Linux 9（LXC 构建）", "rocky"),
                                   ("debian", "trixie", "Debian 13 trixie（LXC 构建）", "debian"), ("ubuntu", "noble", "Ubuntu 24.04（LXC 构建）", "ubuntu"),
                                   ("alpine", "3.24", "Alpine 3.24（LXC 构建）", "alpine"), ("archlinux", "current", "Arch Linux（LXC 构建）", "arch"),
                                   ("opensuse", "tumbleweed", "openSUSE Tumbleweed（LXC 构建）", "opensuse"), ("fedora", "45", "Fedora 45（LXC 构建）", "fedora")):
        entries.append({"id": f"lxc-{distro}-{rel}", "name": name, "family": fam, "guest_os": "linux", "arch": ["x86_64", "aarch64"], "providers": ["wsl2", "linux-ns"],
                        "source": {"kind": "lxc", "server": "https://images.linuxcontainers.org", "distro": distro, "release": rel, "variant": "default",
                                   "origin": "LXC 镜像服务器（每日构建，安装时解析最新构建并按 SHA256SUMS 校验）"}})
    entries.append({"id": "custom-rootfs", "name": "自定义根文件系统（URL 或本地 .tar / .tar.gz / .tar.xz / .wsl）", "family": "custom", "guest_os": "linux", "arch": ["x86_64", "aarch64"],
                    "providers": ["wsl2", "linux-ns"], "source": {"kind": "custom", "needs": ["url"], "origin": "用户提供，可附带 --sha256"}})
    entries += [
        {"id": "windows-sandbox", "name": "Windows Sandbox（一次性 Windows 桌面）", "family": "windows", "guest_os": "windows", "arch": ["x86_64"], "providers": ["windows-sandbox"],
         "source": {"kind": "host", "origin": "Windows 10/11 专业版、企业版、教育版自带"}, "requires": {"editions": "Pro/Enterprise/Education", "feature": "Containers-DisposableClientVM"}},
        {"id": "hyperv-windows-11-eval", "name": "Windows 11 企业版评估版（Hyper-V 虚拟机，90 天）", "family": "windows", "guest_os": "windows", "arch": ["x86_64"], "providers": ["hyperv"], "tpm": True,
         "source": {"kind": "iso", "needs": ["iso"], "download_page": "https://www.microsoft.com/en-us/evalcenter/download-windows-11-enterprise", "origin": "微软评估中心（需在网页上登记后下载 ISO）"},
         "requires": {"editions": "Pro/Enterprise/Education", "feature": "Microsoft-Hyper-V-All", "memory_mb": 4096}},
        {"id": "hyperv-windows-server-2025-eval", "name": "Windows Server 2025 评估版（Hyper-V 虚拟机，180 天）", "family": "windows", "guest_os": "windows", "arch": ["x86_64"], "providers": ["hyperv"],
         "source": {"kind": "iso", "needs": ["iso"], "download_page": "https://www.microsoft.com/en-us/evalcenter/download-windows-server-2025", "origin": "微软评估中心"},
         "requires": {"editions": "Pro/Enterprise/Education", "feature": "Microsoft-Hyper-V-All", "memory_mb": 2048}},
        {"id": "hyperv-custom-iso", "name": "从 ISO 安装（Windows 或 Linux，Hyper-V 虚拟机）", "family": "custom", "guest_os": "any", "arch": ["x86_64"], "providers": ["hyperv"], "secure_boot": False,
         "source": {"kind": "iso", "needs": ["iso"], "origin": "用户提供的 ISO"}, "requires": {"editions": "Pro/Enterprise/Education", "feature": "Microsoft-Hyper-V-All"}},
        {"id": "macos-guest", "name": "macOS 虚拟机", "family": "macos", "guest_os": "macos", "arch": ["aarch64"], "providers": ["macos-guest"], "disabled": True,
         "reason": "Apple 的软件许可只允许在 Apple 硬件上运行的 macOS 中虚拟化 macOS；Windows 与 Linux 上不提供。在 Apple 芯片 Mac 上的支持尚未实现。",
         "source": {"kind": "none"}},
    ]
    out = {"format": "foxos-env-catalog/1", "version": date.today().strftime("%Y.%m.%d"), "generated_from": [SRC, "https://dl.rockylinux.org", "https://dl-cdn.alpinelinux.org", "https://images.linuxcontainers.org"],
           "entries": entries}
    (DATA / "env-catalog.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(entries)} entries")


if __name__ == "__main__":
    main()
