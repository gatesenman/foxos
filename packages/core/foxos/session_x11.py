"""与正在运行的 XFCE / X11 会话对话：wmctrl 列窗口、聚焦、关闭、移动、缩放；
xdotool 键入与点击；scrot / maim 截图。

这是狐狸OS 图形会话的默认后端（Ubuntu 上的 XFCE 通常跑在 X11）。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .errors import FoxError
from .i18n import tr


def display_name() -> str | None:
    d = os.environ.get("DISPLAY")
    return d if d else None


def available_x11() -> bool:
    return bool(display_name())


def _run(argv: list[str], timeout: float = 8.0) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def _require(tool: str, missing_key: str, hint_key: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise FoxError("DEPENDENCY_MISSING", tr(missing_key), hint=tr(hint_key))
    return path


def _wid(win_id: str) -> str:
    s = str(win_id).strip()
    if not s:
        raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id))
    if s.lower().startswith("0x"):
        try:
            int(s, 16)
        except ValueError as e:
            raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id)) from e
        return hex(int(s, 16))
    try:
        return hex(int(s, 10))
    except ValueError as e:
        raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id)) from e


def _parse_wmctrl_list(text: str) -> list[dict[str, Any]]:
    """解析 `wmctrl -lG`：id desktop x y w h host title。"""
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split(None, 7)
        if len(parts) < 7:
            continue
        wid, desk, xs, ys, ws, hs, host = parts[:7]
        title = parts[7] if len(parts) > 7 else ""
        try:
            rec = {
                "id": hex(int(wid, 16)) if wid.lower().startswith("0x") else _wid(wid),
                "desktop": int(desk),
                "x": int(xs),
                "y": int(ys),
                "width": int(ws),
                "height": int(hs),
                "host": host,
                "title": title,
                "app_id": "",
                "states": [],
                "focused": False,
            }
        except ValueError:
            continue
        out.append(rec)
    return out


def _parse_wmctrl_classes(text: str) -> dict[str, str]:
    """解析 `wmctrl -lx`：id desktop class host title → id 到 WM_CLASS。"""
    classes: dict[str, str] = {}
    for line in text.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 3:
            continue
        wid, _desk, klass = parts[0], parts[1], parts[2]
        try:
            key = hex(int(wid, 16)) if wid.lower().startswith("0x") else _wid(wid)
        except (ValueError, FoxError):
            continue
        classes[key] = klass
    return classes


def _active_id(xprop: str | None) -> str | None:
    """从 xprop 或 xdotool 取当前活动窗口。"""
    if xprop and shutil.which("xprop"):
        r = _run(["xprop", "-root", "_NET_ACTIVE_WINDOW"])
        out = r.stdout or ""
        # 常见输出：window id # 0x400003, 0x0  —— 最后一个字段是 0x0，不能取 split()[-1]
        if r.returncode == 0 and "0x" in out:
            if "window id #" in out:
                token = out.split("window id #", 1)[1].split(",")[0].strip()
            else:
                token = out.replace(",", " ").split()
                token = next((x for x in token if x.lower().startswith("0x") and x.lower() != "0x0"), "0x0")
            try:
                val = int(token, 16)
                if val:
                    return hex(val)
            except ValueError:
                pass
    if shutil.which("xdotool"):
        r = _run(["xdotool", "getactivewindow"])
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return hex(int(r.stdout.strip()))
    return None


class X11Backend:
    """SessionBackend 的 X11 实现，由 session.get_backend 选用。"""

    def status(self) -> dict:
        wins = self.windows()
        return {
            "backend": "x11",
            "compositor": os.environ.get("XDG_CURRENT_DESKTOP") or "XFCE",
            "display": display_name(),
            "wayland_display": os.environ.get("WAYLAND_DISPLAY"),
            "windows": len(wins),
            "tools": {
                "wmctrl": bool(shutil.which("wmctrl")),
                "xdotool": bool(shutil.which("xdotool")),
                "scrot": bool(shutil.which("scrot")),
                "maim": bool(shutil.which("maim")),
            },
            "available": True,
        }

    def windows(self) -> list[dict]:
        wmctrl = _require("wmctrl", "desktop.wmctrl_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        r = _run([wmctrl, "-lG"])
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wmctrl_failed", (r.stderr or r.stdout or r.returncode)))
        wins = _parse_wmctrl_list(r.stdout or "")
        rx = _run([wmctrl, "-lx"])
        if rx.returncode == 0:
            classes = _parse_wmctrl_classes(rx.stdout or "")
            for w in wins:
                w["app_id"] = classes.get(w["id"], "")
        active = _active_id("xprop")
        if active:
            for w in wins:
                if w["id"] == active or int(w["id"], 16) == int(active, 16):
                    w["focused"] = True
                    if "activated" not in w["states"]:
                        w["states"] = list(w["states"]) + ["activated"]
        return wins

    def _find(self, win_id: str) -> dict:
        target = _wid(win_id)
        for w in self.windows():
            if w["id"] == target or int(w["id"], 16) == int(target, 16):
                return w
        raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id))

    def focus(self, win_id: str) -> dict:
        wmctrl = _require("wmctrl", "desktop.wmctrl_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        w = self._find(win_id)
        r = _run([wmctrl, "-ia", w["id"]])
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wmctrl_failed", (r.stderr or r.stdout or r.returncode)))
        return {"id": w["id"], "focused": True}

    def close(self, win_id: str) -> dict:
        wmctrl = _require("wmctrl", "desktop.wmctrl_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        w = self._find(win_id)
        r = _run([wmctrl, "-ic", w["id"]])
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wmctrl_failed", (r.stderr or r.stdout or r.returncode)))
        return {"id": w["id"], "closed": True}

    def _configure(self, win_id: str, x: int, y: int, width: int, height: int) -> None:
        wmctrl = _require("wmctrl", "desktop.wmctrl_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        r = _run([wmctrl, "-ir", win_id, "-e", f"0,{int(x)},{int(y)},{int(width)},{int(height)}"])
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wmctrl_failed", (r.stderr or r.stdout or r.returncode)))

    def _place(self, win_id: str, x: int | None, y: int | None, width: int | None, height: int | None) -> dict:
        """按 windows() 报出的客户区坐标放置。部分窗口管理器对 wmctrl -e 有固定偏移，请求一次后按实测误差再校正。"""
        import time
        w = self._find(win_id)
        tx = int(w["x"] if x is None else x)
        ty = int(w["y"] if y is None else y)
        tw = int(w["width"] if width is None else width)
        th = int(w["height"] if height is None else height)
        self._configure(w["id"], tx, ty, tw, th)
        time.sleep(0.05)
        now = self._find(w["id"])
        ox, oy = now["x"] - tx, now["y"] - ty
        ow, oh = now["width"] - tw, now["height"] - th
        if ox or oy or ow or oh:
            self._configure(w["id"], tx - ox, ty - oy, tw - ow, th - oh)
            time.sleep(0.05)
            now = self._find(w["id"])
        return {"id": w["id"], "x": now["x"], "y": now["y"], "width": now["width"], "height": now["height"], "via": "wmctrl"}

    def move(self, win_id: str, x: int, y: int) -> dict:
        r = self._place(win_id, int(x), int(y), None, None)
        return r

    def resize(self, win_id: str, width: int, height: int) -> dict:
        r = self._place(win_id, None, None, int(width), int(height))
        return r

    def launch(self, argv: list[str], env: dict[str, str] | None = None) -> dict:
        if not argv:
            raise FoxError("USAGE", tr("desktop.missing_the_command_to_launch"))
        e = {**os.environ, **(env or {})}
        p = subprocess.Popen(argv, env=e, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return {"command": argv, "pid": p.pid}

    def type_text(self, text: str) -> dict:
        xdotool = _require("xdotool", "desktop.xdotool_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        r = _run([xdotool, "type", "--clearmodifiers", "--", text], timeout=30)
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.xdotool_failed", (r.stderr or r.stdout or r.returncode)))
        return {"typed": text, "length": len(text)}

    def key(self, keys: str) -> dict:
        xdotool = _require("xdotool", "desktop.xdotool_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        args = [xdotool]
        tokens = keys.split()
        if not tokens:
            raise FoxError("USAGE", tr("desktop.key_names_for_example_return_or"))
        # xdotool key accepts ctrl+c directly
        args += ["key", "--clearmodifiers"]
        args.extend(tokens)
        r = _run(args)
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.xdotool_failed", (r.stderr or r.stdout or r.returncode)))
        return {"keys": keys}

    def click(self, x: int, y: int, button: int = 1) -> dict:
        xdotool = _require("xdotool", "desktop.xdotool_is_not_installed", "desktop.install_x11_tools_they_are_in_the_foxos_iso")
        r = _run([xdotool, "mousemove", "--sync", str(int(x)), str(int(y)), "click", str(int(button))])
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.xdotool_failed", (r.stderr or r.stdout or r.returncode)))
        return {"x": int(x), "y": int(y), "button": int(button)}

    def screenshot(self, dest: Path) -> dict:
        dest.parent.mkdir(parents=True, exist_ok=True)
        scrot = shutil.which("scrot")
        maim = shutil.which("maim")
        if scrot:
            r = _run([scrot, "-o", str(dest)], timeout=15)
            tool = "scrot"
        elif maim:
            r = _run([maim, str(dest)], timeout=15)
            tool = "maim"
        else:
            raise FoxError(
                "DEPENDENCY_MISSING",
                tr("desktop.screenshot_tool_is_not_installed"),
                hint=tr("desktop.install_x11_tools_they_are_in_the_foxos_iso"),
            )
        if r.returncode != 0 or not dest.exists():
            raise FoxError("ERROR", tr("desktop.screenshot_failed", (r.stderr or r.stdout or r.returncode)))
        return {"path": str(dest), "bytes": dest.stat().st_size, "via": tool}
