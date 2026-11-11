"""真实桌面会话后端：默认是 XFCE / X11（wmctrl、xdotool、scrot）；
也保留 Wayland / wlroots 实现。测试可用假后端。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .errors import FoxError
from .i18n import tr
from .workspace import Workspace


def _env_backend() -> str | None:
    return os.environ.get("FOXOS_SESSION_BACKEND") or None


class SessionBackend:
    def status(self) -> dict:  # pragma: no cover - interface
        raise NotImplementedError

    def windows(self) -> list[dict]:
        raise NotImplementedError

    def focus(self, win_id: str) -> dict:
        raise NotImplementedError

    def close(self, win_id: str) -> dict:
        raise NotImplementedError

    def move(self, win_id: str, x: int, y: int) -> dict:
        raise NotImplementedError

    def resize(self, win_id: str, width: int, height: int) -> dict:
        raise NotImplementedError

    def launch(self, argv: list[str], env: dict[str, str] | None = None) -> dict:
        raise NotImplementedError

    def type_text(self, text: str) -> dict:
        raise NotImplementedError

    def key(self, keys: str) -> dict:
        raise NotImplementedError

    def click(self, x: int, y: int, button: int = 1) -> dict:
        raise NotImplementedError

    def screenshot(self, dest: Path) -> dict:
        raise NotImplementedError


class FakeBackend(SessionBackend):
    """进程内假会话，由 FOXOS_SESSION_FAKE 指向的 JSON 文件保存窗口，供单元测试。"""

    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            self._write({"windows": [], "serial": 0, "typed": "", "clicks": [], "keys": []})

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, self.path)

    def status(self) -> dict:
        d = self._read()
        return {"backend": "fake", "compositor": "fake", "wayland_display": None, "windows": len(d["windows"]), "available": True}

    def windows(self) -> list[dict]:
        return list(self._read()["windows"])

    def _get(self, win_id: str) -> tuple[dict, dict]:
        d = self._read()
        for w in d["windows"]:
            if w["id"] == str(win_id):
                return d, w
        raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id))

    def focus(self, win_id: str) -> dict:
        d, w = self._get(win_id)
        for o in d["windows"]:
            o["focused"] = o["id"] == w["id"]
            st = [s for s in o.get("states", []) if s != "activated"]
            if o["focused"]:
                st.append("activated")
            o["states"] = st
        self._write(d)
        return {"id": w["id"], "focused": True}

    def close(self, win_id: str) -> dict:
        d, w = self._get(win_id)
        d["windows"] = [o for o in d["windows"] if o["id"] != w["id"]]
        self._write(d)
        return {"id": w["id"], "closed": True}

    def move(self, win_id: str, x: int, y: int) -> dict:
        d, w = self._get(win_id)
        w["x"], w["y"] = int(x), int(y)
        self._write(d)
        return {"id": w["id"], "x": int(x), "y": int(y)}

    def resize(self, win_id: str, width: int, height: int) -> dict:
        d, w = self._get(win_id)
        w["width"], w["height"] = int(width), int(height)
        self._write(d)
        return {"id": w["id"], "width": int(width), "height": int(height)}

    def launch(self, argv: list[str], env: dict[str, str] | None = None) -> dict:
        d = self._read()
        d["serial"] = int(d.get("serial") or 0) + 1
        wid = str(d["serial"])
        title = argv[0] if argv else "app"
        win = {"id": wid, "title": title, "app_id": title, "states": ["activated"], "focused": True, "x": 0, "y": 0, "width": 800, "height": 600}
        for o in d["windows"]:
            o["focused"] = False
            o["states"] = [s for s in o.get("states", []) if s != "activated"]
        d["windows"].append(win)
        self._write(d)
        return {"id": wid, "command": argv, "pid": None}

    def type_text(self, text: str) -> dict:
        d = self._read()
        d["typed"] = d.get("typed", "") + text
        self._write(d)
        return {"typed": text, "length": len(text)}

    def key(self, keys: str) -> dict:
        d = self._read()
        d.setdefault("keys", []).append(keys)
        self._write(d)
        return {"keys": keys}

    def click(self, x: int, y: int, button: int = 1) -> dict:
        d = self._read()
        ev = {"x": int(x), "y": int(y), "button": int(button)}
        d.setdefault("clicks", []).append(ev)
        self._write(d)
        return ev

    def screenshot(self, dest: Path) -> dict:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
        return {"path": str(dest), "bytes": dest.stat().st_size}


class WaylandBackend(SessionBackend):
    def __init__(self):
        from .session_wayland import ForeignToplevels, _Conn, _display_path

        self._display = _display_path()
        self._Conn = _Conn
        self._Foreign = ForeignToplevels

    def _ft(self):
        conn = self._Conn()
        return conn, self._Foreign(conn)

    def status(self) -> dict:
        conn, ft = self._ft()
        try:
            wins = ft.refresh()
            return {
                "backend": "wayland",
                "compositor": os.environ.get("XDG_CURRENT_DESKTOP") or _guess_compositor(),
                "wayland_display": os.environ.get("WAYLAND_DISPLAY"),
                "display_path": self._display,
                "windows": len(wins),
                "protocols": {
                    "foreign_toplevel": ft.manager_id is not None,
                    "virtual_pointer": ft.vptr_mgr is not None,
                },
                "tools": {"wtype": bool(shutil.which("wtype")), "grim": bool(shutil.which("grim"))},
                "available": ft.manager_id is not None,
            }
        finally:
            conn.close()

    def windows(self) -> list[dict]:
        conn, ft = self._ft()
        try:
            return ft.refresh()
        finally:
            conn.close()

    def focus(self, win_id: str) -> dict:
        conn, ft = self._ft()
        try:
            return ft.focus(win_id)
        finally:
            conn.close()

    def close(self, win_id: str) -> dict:
        conn, ft = self._ft()
        try:
            return ft.close(win_id)
        finally:
            conn.close()

    def move(self, win_id: str, x: int, y: int) -> dict:
        # Wayland 后端：foreign-toplevel 没有设位置请求；若有 wlrctl 则用之，否则说明限制。
        if shutil.which("wlrctl"):
            r = subprocess.run(["wlrctl", "toplevel", "move", win_id, str(x), str(y)], capture_output=True, text=True)
            if r.returncode == 0:
                return {"id": win_id, "x": int(x), "y": int(y), "via": "wlrctl"}
        raise FoxError(
            "DEPENDENCY_MISSING",
            tr("desktop.move_not_supported_by_this_compositor"),
            hint=tr("desktop.foreign_toplevel_has_no_position_request"),
        )

    def resize(self, win_id: str, width: int, height: int) -> dict:
        if shutil.which("wlrctl"):
            r = subprocess.run(["wlrctl", "toplevel", "resize", win_id, str(width), str(height)], capture_output=True, text=True)
            if r.returncode == 0:
                return {"id": win_id, "width": int(width), "height": int(height), "via": "wlrctl"}
        raise FoxError(
            "DEPENDENCY_MISSING",
            tr("desktop.resize_not_supported_by_this_compositor"),
            hint=tr("desktop.foreign_toplevel_has_no_position_request"),
        )

    def launch(self, argv: list[str], env: dict[str, str] | None = None) -> dict:
        if not argv:
            raise FoxError("USAGE", tr("desktop.missing_the_command_to_launch"))
        e = {**os.environ, **(env or {})}
        p = subprocess.Popen(argv, env=e, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return {"command": argv, "pid": p.pid}

    def type_text(self, text: str) -> dict:
        wtype = shutil.which("wtype")
        if not wtype:
            raise FoxError("DEPENDENCY_MISSING", tr("desktop.wtype_is_not_installed"), hint=tr("desktop.install_wtype_it_is_in_the_foxos_iso"))
        r = subprocess.run([wtype, "--", text], capture_output=True, text=True)
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wtype_failed", r.stderr.strip() or r.returncode))
        return {"typed": text, "length": len(text)}

    def key(self, keys: str) -> dict:
        wtype = shutil.which("wtype")
        if not wtype:
            raise FoxError("DEPENDENCY_MISSING", tr("desktop.wtype_is_not_installed"), hint=tr("desktop.install_wtype_it_is_in_the_foxos_iso"))
        # wtype -k for key names, allow "ctrl+c" style via -M
        args = [wtype]
        for tok in keys.split():
            if "+" in tok:
                mods, _, key = tok.rpartition("+")
                for m in mods.split("+"):
                    args += ["-M", m]
                args += ["-k", key]
                for m in reversed(mods.split("+")):
                    args += ["-m", m]
            else:
                args += ["-k", tok]
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode != 0:
            raise FoxError("ERROR", tr("desktop.wtype_failed", r.stderr.strip() or r.returncode))
        return {"keys": keys}

    def click(self, x: int, y: int, button: int = 1) -> dict:
        from .session_wayland import virtual_click

        conn, ft = self._ft()
        try:
            ft.refresh()
            return virtual_click(ft, int(x), int(y), int(button))
        finally:
            conn.close()

    def screenshot(self, dest: Path) -> dict:
        grim = shutil.which("grim")
        if not grim:
            raise FoxError("DEPENDENCY_MISSING", tr("desktop.grim_is_not_installed"), hint=tr("desktop.install_grim_it_is_in_the_foxos_iso"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([grim, str(dest)], capture_output=True, text=True)
        if r.returncode != 0 or not dest.exists():
            raise FoxError("ERROR", tr("desktop.grim_failed", r.stderr.strip() or r.returncode))
        return {"path": str(dest), "bytes": dest.stat().st_size}


def _guess_compositor() -> str | None:
    return os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("XDG_SESSION_DESKTOP")


def available_wayland() -> bool:
    if not os.environ.get("WAYLAND_DISPLAY"):
        return False
    try:
        from .session_wayland import _display_path
        return os.path.exists(_display_path())
    except FoxError:
        return False


def available_x11() -> bool:
    from .session_x11 import available_x11 as _ok
    return _ok()


def get_backend(ws: Workspace | None = None) -> SessionBackend:
    kind = (_env_backend() or "").strip().lower()
    fake = os.environ.get("FOXOS_SESSION_FAKE")
    if kind == "fake" or fake:
        path = Path(fake) if fake else (ws.data_dir / "session-fake.json" if ws else Path("/tmp/foxos-session-fake.json"))
        return FakeBackend(path)
    if kind in ("x11", "xfce", "xfwm", "xfwm4"):
        if available_x11():
            from .session_x11 import X11Backend
            return X11Backend()  # type: ignore[return-value]
        raise FoxError("DEPENDENCY_MISSING", tr("desktop.x11_display_is_not_available"), hint=tr("desktop.start_an_xfce_session_or_set_display"))
    if kind in ("wayland", "labwc"):
        if available_wayland():
            return WaylandBackend()
        raise FoxError("DEPENDENCY_MISSING", tr("desktop.wayland_display_is_not_available"), hint=tr("desktop.start_an_xfce_session_or_set_display"))
    # 默认：狐狸OS 图形会话是 XFCE / X11；若只有 Wayland 再走 wlroots。
    # 不要悄悄落到 Electron 假桌面。
    if available_x11():
        from .session_x11 import X11Backend
        return X11Backend()  # type: ignore[return-value]
    if available_wayland():
        return WaylandBackend()
    raise FoxError("DEPENDENCY_MISSING", tr("desktop.x11_display_is_not_available"), hint=tr("desktop.start_an_xfce_session_or_set_display"))
