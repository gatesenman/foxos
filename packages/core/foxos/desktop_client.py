"""连接正在运行的狐狸OS 桌面（本机控制通道）。没有运行时可按需以无界面模式自动启动。"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

from .errors import FoxError
from .workspace import Workspace


def foxos_home() -> Path:
    if os.environ.get("FOXOS_HOME"):
        return Path(os.environ["FOXOS_HOME"]).resolve()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "FoxOS"
    if os.uname().sysname == "Darwin":
        return Path.home() / "Library" / "Application Support" / "FoxOS"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "foxos"


def _info(ws: Workspace) -> dict | None:
    f = ws.data_dir / "desktop.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    try:
        if os.name == "posix":
            os.kill(int(d["pid"]), 0)
    except (ProcessLookupError, KeyError, ValueError):
        return None
    except PermissionError:
        pass
    return d


def _launch_cmd() -> list[str] | None:
    if os.environ.get("FOXOS_DESKTOP_CMD"):
        return json.loads(os.environ["FOXOS_DESKTOP_CMD"])
    f = foxos_home() / "desktop-launch.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        return [d["exec"], *d.get("args", [])]
    except (OSError, ValueError, KeyError):
        return None


def ensure_desktop(ws: Workspace, autostart: bool = True) -> dict:
    d = _info(ws)
    if d:
        return d
    if not autostart or os.environ.get("FOXOS_NO_AUTOSTART") == "1":
        raise FoxError("DEPENDENCY_MISSING", "狐狸OS 桌面没有运行", hint="先启动桌面，或运行 foxos desktop start --headless")
    cmd = _launch_cmd()
    if not cmd:
        raise FoxError("DEPENDENCY_MISSING", "狐狸OS 桌面没有运行，且找不到启动命令", hint="先手动启动一次桌面（会记录启动方式），或设置 FOXOS_DESKTOP_CMD")
    args = [a for a in cmd if not a.startswith("--workspace=") and a != "--headless"]
    args += [f"--workspace={ws.root}", "--headless"]
    log = open(ws.data_dir / "desktop-headless.log", "ab")
    kw = {"start_new_session": True} if os.name == "posix" else {"creationflags": 0x00000008 | 0x00000200}
    subprocess.Popen(args, stdout=log, stderr=log, stdin=subprocess.DEVNULL, **kw)
    for _ in range(300):
        time.sleep(0.1)
        d = _info(ws)
        if d:
            return d
    raise FoxError("ERROR", "无界面桌面启动超时", hint=f"查看 {ws.data_dir / 'desktop-headless.log'}")


def call(ws: Workspace, op: str, app: str | None = None, params: dict | None = None, agent: str = "agent", timeout: float = 120) -> dict:
    d = ensure_desktop(ws)
    body = json.dumps({"op": op, "app": app, "params": params or {}, "agent": agent}).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{d['port']}/", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {d['token']}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            res = json.loads(r.read().decode("utf-8"))
    except OSError as e:
        raise FoxError("ERROR", f"无法连接桌面控制通道：{e}") from e
    if not res.get("ok"):
        err = res.get("error") or {}
        raise FoxError(err.get("code", "ERROR"), err.get("message", "桌面返回错误"))
    return res["result"]
