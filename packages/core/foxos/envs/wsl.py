"""Windows 后端：直接驱动 Windows 自带的 WSL2 平台（wsl.exe）。

每个狐狸OS 环境对应一个以 foxos- 为前缀的 WSL 发行版：
  create  → wsl.exe --import foxos-<name> <目录> <rootfs.tar> --version 2
  start   → wsl.exe -d foxos-<name> --exec /bin/true（WSL 按需启动）
  stop    → wsl.exe --terminate foxos-<name>
  exec    → wsl.exe -d foxos-<name> --cd <目录> --exec <命令…>
  export  → wsl.exe --export foxos-<name> <文件>
  delete  → wsl.exe --unregister foxos-<name>
工作空间通过 WSL 自动挂载的 /mnt/<盘符>/… 访问。
状态说明：本模块已实现并有单元测试（命令构造与输出解析）；尚未在 Windows 硬件上做端到端验证。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PureWindowsPath

from ..errors import FoxError

PREFIX = "foxos-"


def distro(name: str) -> str:
    return PREFIX + name


def win_to_wsl_path(p: str) -> str:
    w = PureWindowsPath(p)
    if not w.drive or not w.drive.endswith(":"):
        raise FoxError("USAGE", f"不是 Windows 绝对路径：{p}")
    rest = "/".join(w.parts[1:])
    return f"/mnt/{w.drive[0].lower()}/{rest}".rstrip("/")


def cmd_import(name: str, install_dir: str, tar: str) -> list[str]:
    return ["wsl.exe", "--import", distro(name), install_dir, tar, "--version", "2"]


def cmd_exec(name: str, argv: list[str], cwd: str | None = None) -> list[str]:
    c = ["wsl.exe", "-d", distro(name)]
    if cwd:
        c += ["--cd", cwd]
    return [*c, "--exec", *argv]


def cmd_terminate(name: str) -> list[str]:
    return ["wsl.exe", "--terminate", distro(name)]


def cmd_export(name: str, out: str) -> list[str]:
    return ["wsl.exe", "--export", distro(name), out]


def cmd_unregister(name: str) -> list[str]:
    return ["wsl.exe", "--unregister", distro(name)]


def parse_list_verbose(text: str) -> dict[str, dict]:
    """解析 `wsl.exe --list --verbose`（输出为 UTF-16LE，调用方需先解码）。"""
    out = {}
    for line in text.replace("\x00", "").splitlines()[1:]:
        m = re.match(r"^\s*(\*)?\s*(\S+)\s+(Running|Stopped|Installing|Converting|Uninstalling)\s+(\d)\s*$", line)
        if m:
            out[m.group(2)] = {"default": bool(m.group(1)), "state": m.group(3).lower(), "version": int(m.group(4))}
    return out


def _run(cmd: list[str], **kw):
    try:
        return subprocess.run(cmd, capture_output=True, **kw)
    except FileNotFoundError as e:
        raise FoxError("DEPENDENCY_MISSING", "没有找到 wsl.exe：请启用“适用于 Linux 的 Windows 子系统”", hint="管理员 PowerShell 运行 wsl --install") from e


def state(name: str) -> str:
    r = _run(["wsl.exe", "--list", "--verbose"])
    info = parse_list_verbose(r.stdout.decode("utf-16-le", "replace"))
    return info.get(distro(name), {}).get("state", "missing")


def create(name, image, workspace, home):
    from . import images
    m = images.pull(image, home / "images")
    tar = Path(home / "images" / m["id"] / "rootfs.tar")
    if not tar.exists():
        subprocess.run(["tar", "-c", "-f", str(tar), "-C", str(home / "images" / m["id"] / "rootfs"), "."], check=True)
    inst = home / "instances" / name
    inst.mkdir(parents=True, exist_ok=True)
    r = _run(cmd_import(name, str(inst / "disk"), str(tar)))
    if r.returncode:
        raise FoxError("ERROR", r.stderr.decode("utf-16-le", "replace") or "wsl --import 失败")
    return {"message": f"已创建 WSL2 环境 {distro(name)}", "workspace_in_env": win_to_wsl_path(str(workspace))}


def start(name):
    r = _run(cmd_exec(name, ["/bin/true"]))
    if r.returncode:
        raise FoxError("ERROR", "WSL 启动失败")
    return {"message": f"已启动 {distro(name)}"}


def stop(name):
    _run(cmd_terminate(name))
    return {"message": f"已停止 {distro(name)}"}


def exec_(name, argv, cwd):
    return _run(cmd_exec(name, argv, cwd))
