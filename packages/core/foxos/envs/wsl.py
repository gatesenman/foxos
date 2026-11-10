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
        raise FoxError("DEPENDENCY_MISSING", "没有找到 wsl.exe：请启用“适用于 Linux 的 Windows 子系统”", hint="环境 → 安装系统 → 启用 WSL，或管理员 PowerShell 运行 wsl --install --no-distribution") from e


def _text(raw: bytes) -> str:
    from .providers import decode_wsl
    return decode_wsl(raw or b"")


def dname(cfg: dict) -> str:
    """环境对应的 WSL 发行版名：通过 --import 安装的为 foxos-<名>；应用商店发行版用其自身名字。"""
    return cfg.get("wsl_distro") or distro(cfg["name"])


def list_verbose() -> dict[str, dict]:
    r = _run(["wsl.exe", "--list", "--verbose"])
    return parse_list_verbose(_text(r.stdout))


def state(cfg_or_name) -> str:
    d = dname(cfg_or_name) if isinstance(cfg_or_name, dict) else distro(cfg_or_name)
    return list_verbose().get(d, {}).get("state", "missing")


def cmd_exec_d(d: str, argv: list[str], cwd: str | None = None) -> list[str]:
    c = ["wsl.exe", "-d", d]
    if cwd:
        c += ["--cd", cwd]
    return [*c, "--exec", *argv]


def map_cwd(cwd: str, cfg: dict) -> str:
    """/workspace 映射到工作空间在 WSL 里的 /mnt/<盘符>/… 路径。"""
    ws = (cfg.get("workspace") or {}).get("path")
    if ws and (cwd == "/workspace" or cwd.startswith("/workspace/")):
        try:
            return win_to_wsl_path(ws) + cwd[len("/workspace"):]
        except FoxError:
            return cwd
    return cwd


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
        raise FoxError("ERROR", _text(r.stdout + r.stderr).strip() or "wsl --import 失败")
    return {"message": f"已创建 WSL2 环境 {distro(name)}", "workspace_in_env": win_to_wsl_path(str(workspace)), "image": m["id"]}


def start(cfg):
    r = _run(cmd_exec_d(dname(cfg), ["/bin/sh", "-c", "true"]))
    if r.returncode:
        raise FoxError("ERROR", "WSL 启动失败：" + _text(r.stdout + r.stderr).strip()[-500:])
    return {"message": f"已启动 {dname(cfg)}"}


def stop(cfg):
    _run(["wsl.exe", "--terminate", dname(cfg)])
    return {"message": f"已停止 {dname(cfg)}"}


def exec_(cfg, argv, cwd, capture=True, timeout=None):
    cmd = cmd_exec_d(dname(cfg), argv, map_cwd(cwd, cfg))
    if not capture:
        return subprocess.call(cmd)
    return _run(cmd, timeout=timeout)


def export(cfg, out: str):
    r = _run(["wsl.exe", "--export", dname(cfg), out])
    if r.returncode:
        raise FoxError("ERROR", _text(r.stdout + r.stderr).strip()[-500:] or "wsl --export 失败")


def unregister(cfg):
    r = _run(["wsl.exe", "--unregister", dname(cfg)])
    if r.returncode and "not found" not in _text(r.stdout + r.stderr).lower():
        raise FoxError("ERROR", _text(r.stdout + r.stderr).strip()[-500:] or "wsl --unregister 失败")
