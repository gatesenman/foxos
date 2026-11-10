"""macOS 后端：Apple Virtualization.framework（系统原生），通过随狐狸OS 提供的 Swift 小助手 foxos-vz 驱动。

每个环境是一台轻量 Linux 虚拟机：内核 + initrd + 根文件系统磁盘镜像（由狐狸OS 镜像生成），
工作空间通过 virtio-fs 共享为 /workspace，控制台走 virtio 串口。
状态说明：Swift 源码在 data/macos/FoxVZ.swift；本模块的配置生成有单元测试；尚未在 Mac 硬件上验证。
"""

from __future__ import annotations

import json
from pathlib import Path


def vm_config(name: str, env_dir: Path, workspace: Path, cpus: int = 2, memory_mb: int = 2048, network: str = "nat") -> dict:
    return {
        "name": name,
        "cpus": max(1, int(cpus)),
        "memoryBytes": int(memory_mb) * 1024 * 1024,
        "kernel": str(env_dir / "vmlinuz"),
        "initrd": str(env_dir / "initrd.img"),
        "commandLine": "console=hvc0 root=/dev/vda rw quiet",
        "disk": str(env_dir / "rootfs.img"),
        "shares": [{"tag": "workspace", "path": str(workspace), "readOnly": False}],
        "network": network,
        "serialLog": str(env_dir / "logs" / "console.log"),
    }


def write_config(cfg: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=1))
    return path


def helper_cmd(helper: str, config: Path, action: str = "run") -> list[str]:
    return [helper, action, "--config", str(config)]
