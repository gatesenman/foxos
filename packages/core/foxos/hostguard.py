"""宿主保护：在宿主应用里（Windows / macOS / 普通 Linux 上的狐狸OS 伴侣程序），智能体只在狐狸OS 虚拟电脑里动手。

- 运行在狐狸OS 系统里（/etc/os-release 的 ID=foxos）时，本机就是狐狸OS 虚拟电脑，不受限制。
- 运行在宿主上时，智能体（身份 bot:…）对本机（local）的调用一律拒绝，提示改用配对的狐狸OS 虚拟电脑；
  只有人明确打开「允许智能体在宿主上执行」（foxos bot host-access enable，只有人能做）以后才放行，
  并且每一个不是只读的操作都要人当场确认一次（审批卡片），规则和“全部允许”都不能代替。
- FOXOS_PLACE=host|foxos 可以覆盖检测（测试与特殊部署用）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from . import audit, secrets
from .errors import FoxError
from .i18n import tr

OS_RELEASE = Path(os.environ.get("FOXOS_OS_RELEASE", "/etc/os-release"))


def place() -> str:
    """'foxos'：运行在狐狸OS 系统里；'host'：运行在宿主（伴侣程序、开发机）上。"""
    p = os.environ.get("FOXOS_PLACE", "").strip().lower()
    if p in ("host", "foxos"):
        return p
    try:
        for ln in OS_RELEASE.read_text(encoding="utf-8").splitlines():
            if ln.strip() == "ID=foxos" or ln.strip() == 'ID="foxos"':
                return "foxos"
    except OSError:
        pass
    return "host"


def on_host() -> bool:
    return place() == "host"


def _path() -> Path:
    return secrets.home() / "host-access.json"


def policy() -> dict:
    try:
        d = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    return {"enabled": bool(d.get("enabled")), "by": d.get("by"), "at": d.get("at")}


def set_policy(enabled: bool, by: str) -> dict:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    d = {"enabled": bool(enabled), "by": by, "at": audit.now_iso()}
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(d, indent=2), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, p)  # 原子替换：桌面客户端直接读这个文件，不能读到写了一半的内容
    return d


def state_path() -> str:
    """唯一的开关状态文件。桌面客户端的「允许在本机执行」也读写它（通过 foxos bot host-access）。"""
    return str(_path())


def is_bot(agent: str | None) -> bool:
    return str(agent or "").startswith("bot:")


def guard(agent: str, command: str, permission: str, confirm: Callable[[str, str], bool] | None = None) -> None:
    """智能体要在本机执行 command 之前调用。不在宿主上、或调用者不是智能体时直接放行。"""
    if not is_bot(agent) or not on_host():
        return
    if not policy()["enabled"]:
        raise FoxError("PERMISSION_DENIED", tr("host.bots_stay_in_vm", command), hint=tr("host.bots_stay_in_vm_hint"),
                       details={"command": command, "place": "host"})
    if permission == "read":
        return
    if confirm is None or not confirm(command, permission):
        raise FoxError("PERMISSION_DENIED", tr("host.not_confirmed", command), details={"command": command, "place": "host"})
