"""与正在运行的 wlroots / labwc 会话对话：wlr-foreign-toplevel 列窗口、聚焦、关闭；
虚拟指针点击；wtype 键入；grim 截图。

只用 Unix 套接字上的 Wayland 线路协议，不额外依赖 pywayland。合成器侧协议
（zwlr_foreign_toplevel_manager_v1、zwlr_virtual_pointer_manager_v1）是 labwc 已实现的标准。
"""

from __future__ import annotations

import array
import os
import socket
import struct
import time
from typing import Any, Callable

from .errors import FoxError
from .i18n import tr

# evdev BTN_LEFT / RIGHT / MIDDLE
_BTN = {1: 0x110, 2: 0x112, 3: 0x111}
_STATE_NAMES = {0: "maximized", 1: "minimized", 2: "activated", 3: "fullscreen"}


def _display_path() -> str:
    name = os.environ.get("WAYLAND_DISPLAY") or "wayland-0"
    if name.startswith("/"):
        return name
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime:
        raise FoxError("DEPENDENCY_MISSING", tr("desktop.wayland_display_is_not_available"), hint=tr("desktop.start_a_labwc_session_or_set_wayland"))
    return os.path.join(runtime, name)


class _Conn:
    def __init__(self, path: str | None = None):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect(path or _display_path())
        self.next_id = 2
        self.dispatch: dict[int, Callable[[int, bytes, list[int]], None]] = {}
        self.dead: set[int] = set()
        self._fds: list[int] = []
        self.last_error: str | None = None
        self.dispatch[1] = self._on_display

    def alloc(self) -> int:
        i = self.next_id
        self.next_id += 1
        return i

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def send(self, obj: int, opcode: int, payload: bytes = b"", fds: list[int] | None = None) -> None:
        size = 8 + len(payload)
        header = struct.pack("IHH", obj, opcode, size)
        if fds:
            self.sock.sendmsg([header + payload], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", fds))])
        else:
            self.sock.sendall(header + payload)

    def _recv_once(self) -> bool:
        try:
            data, anc, _flags, _ = self.sock.recvmsg(4096, 256)
        except socket.timeout:
            return False
        if not data:
            return False
        for level, typ, cmsg in anc:
            if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                self._fds.extend(array.array("i", cmsg).tolist())
        buf = data
        while len(buf) >= 8:
            obj, opcode, size = struct.unpack_from("IHH", buf)
            if size < 8 or len(buf) < size:
                # incomplete; shouldn't happen often with 4096
                more, anc2, _, _ = self.sock.recvmsg(4096, 256)
                for level, typ, cmsg in anc2:
                    if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                        self._fds.extend(array.array("i", cmsg).tolist())
                buf += more
                continue
            body = buf[8:size]
            buf = buf[size:]
            fn = self.dispatch.get(obj)
            if fn and obj not in self.dead:
                fn(opcode, body, self._fds)
        return True

    def roundtrip(self, timeout: float = 2.0) -> None:
        done = False
        cb = self.alloc()

        def on_cb(opcode: int, body: bytes, _fds: list[int]) -> None:
            nonlocal done
            if opcode == 0:
                done = True

        self.dispatch[cb] = on_cb
        self.send(1, 0, struct.pack("I", cb))  # wl_display.sync
        t0 = time.time()
        while not done and time.time() - t0 < timeout:
            if not self._recv_once():
                time.sleep(0.01)
        self.dispatch.pop(cb, None)
        if not done:
            raise FoxError("ERROR", tr("desktop.wayland_roundtrip_timed_out"))

    def _on_display(self, opcode: int, body: bytes, _fds: list[int]) -> None:
        if opcode == 1 and len(body) >= 4:  # delete_id
            oid = struct.unpack_from("I", body)[0]
            self.dead.add(oid)
            self.dispatch.pop(oid, None)
        elif opcode == 0 and len(body) >= 8:  # error
            obj, code = struct.unpack_from("II", body, 0)
            msg, _ = _parse_string(body, 8)
            self.last_error = f"object={obj} code={code} {msg}"


def _u32(n: int) -> bytes:
    return struct.pack("I", n)


def _string(s: str) -> bytes:
    b = s.encode("utf-8") + b"\x00"
    pad = (4 - (len(b) % 4)) % 4
    return struct.pack("I", len(b)) + b + (b"\x00" * pad)


def _parse_string(body: bytes, off: int) -> tuple[str, int]:
    (n,) = struct.unpack_from("I", body, off)
    off += 4
    raw = body[off:off + n]
    off += n
    off += (4 - (n % 4)) % 4
    return raw.split(b"\x00", 1)[0].decode("utf-8", "replace"), off


def _parse_array_u32(body: bytes, off: int) -> tuple[list[int], int]:
    (n,) = struct.unpack_from("I", body, off)
    off += 4
    vals = list(struct.unpack_from(f"{n // 4}I", body, off)) if n else []
    off += n
    off += (4 - (n % 4)) % 4
    return vals, off


class ForeignToplevels:
    """绑定 zwlr_foreign_toplevel_manager_v1，维护当前窗口表。"""

    def __init__(self, conn: _Conn):
        self.conn = conn
        self.globals: dict[str, tuple[int, int]] = {}  # interface -> (name, version)
        self.windows: dict[int, dict[str, Any]] = {}
        self.seat_id: int | None = None
        self.output_id: int | None = None
        self.manager_id: int | None = None
        self.vptr_mgr: int | None = None
        self._bind_registry()

    def _bind_registry(self) -> None:
        reg = self.conn.alloc()

        def on_reg(opcode: int, body: bytes, _fds: list[int]) -> None:
            if opcode == 0:  # global
                name = struct.unpack_from("I", body, 0)[0]
                iface, off = _parse_string(body, 4)
                version = struct.unpack_from("I", body, off)[0]
                self.globals[iface] = (name, version)

        self.conn.dispatch[reg] = on_reg
        self.conn.send(1, 1, _u32(reg))  # get_registry
        self.conn.roundtrip()

        def bind(iface: str, version: int | None = None) -> int | None:
            if iface not in self.globals:
                return None
            name, avail = self.globals[iface]
            ver = min(version or avail, avail)
            oid = self.conn.alloc()
            self.conn.send(reg, 0, _u32(name) + _string(iface) + _u32(ver) + _u32(oid))
            return oid

        self.manager_id = bind("zwlr_foreign_toplevel_manager_v1", 3)
        if self.manager_id:
            self.conn.dispatch[self.manager_id] = self._on_manager
        seat = bind("wl_seat", 7)
        if seat:
            self.seat_id = seat
            self.conn.dispatch[seat] = lambda *a: None
        out = bind("wl_output", 4)
        if out:
            self.output_id = out
            self.conn.dispatch[out] = lambda *a: None
        self.vptr_mgr = bind("zwlr_virtual_pointer_manager_v1", 2)
        self.conn.roundtrip()

    def _on_manager(self, opcode: int, body: bytes, _fds: list[int]) -> None:
        if opcode != 0 or len(body) < 4:  # toplevel
            return
        (oid,) = struct.unpack_from("I", body)
        win = {"id": str(oid), "object": oid, "title": "", "app_id": "", "states": [], "closed": False}
        self.windows[oid] = win

        def on_handle(op: int, b: bytes, _f: list[int], w=win) -> None:
            if op == 0:  # title
                w["title"], _ = _parse_string(b, 0)
            elif op == 1:  # app_id
                w["app_id"], _ = _parse_string(b, 0)
            elif op == 4:  # state
                vals, _ = _parse_array_u32(b, 0)
                w["states"] = [_STATE_NAMES.get(v, str(v)) for v in vals]
            elif op == 6:  # closed
                w["closed"] = True

        self.conn.dispatch[oid] = on_handle

    def refresh(self) -> list[dict[str, Any]]:
        self.conn.roundtrip()
        out = []
        for w in self.windows.values():
            if w["closed"]:
                continue
            out.append({
                "id": w["id"],
                "title": w["title"],
                "app_id": w["app_id"],
                "states": list(w["states"]),
                "focused": "activated" in w["states"],
            })
        return out

    def _win(self, win_id: str) -> dict[str, Any]:
        self.refresh()
        try:
            oid = int(win_id)
        except ValueError as e:
            raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id)) from e
        w = self.windows.get(oid)
        if not w or w["closed"]:
            raise FoxError("NOT_FOUND", tr("desktop.no_window", win_id))
        return w

    def focus(self, win_id: str) -> dict[str, Any]:
        w = self._win(win_id)
        if not self.seat_id:
            raise FoxError("DEPENDENCY_MISSING", tr("desktop.no_wayland_seat"))
        self.conn.send(w["object"], 4, _u32(self.seat_id))  # activate
        self.conn.roundtrip()
        return {"id": w["id"], "focused": True}

    def close(self, win_id: str) -> dict[str, Any]:
        w = self._win(win_id)
        self.conn.send(w["object"], 5)  # close
        self.conn.roundtrip()
        return {"id": w["id"], "closed": True}

def virtual_click(ft: ForeignToplevels, x: int, y: int, button: int = 1, width: int = 1280, height: int = 800) -> dict[str, Any]:
    if not ft.vptr_mgr:
        raise FoxError("DEPENDENCY_MISSING", tr("desktop.virtual_pointer_protocol_unavailable"), hint=tr("desktop.labwc_or_another_wlroots_compositor"))
    conn = ft.conn
    ptr = conn.alloc()
    conn.dispatch[ptr] = lambda *a: None
    # create_virtual_pointer(seat, id) — seat may be null
    conn.send(ft.vptr_mgr, 0, _u32(ft.seat_id or 0) + _u32(ptr))
    now = int(time.time() * 1000) & 0xFFFFFFFF
    code = _BTN.get(int(button), _BTN[1])
    # 0 motion, 1 motion_absolute, 2 button, 3 axis, 4 frame, 8 destroy
    conn.send(ptr, 1, struct.pack("IIIII", now, int(x), int(y), int(width), int(height)))
    conn.send(ptr, 4)
    conn.send(ptr, 2, struct.pack("III", now + 1, code, 1))
    conn.send(ptr, 4)
    conn.send(ptr, 2, struct.pack("III", now + 2, code, 0))
    conn.send(ptr, 4)
    try:
        conn.roundtrip()
    except FoxError:
        err = conn.last_error or "roundtrip"
        raise FoxError("ERROR", tr("desktop.pointer_click_failed", err)) from None
    if conn.last_error:
        raise FoxError("ERROR", tr("desktop.pointer_click_failed", conn.last_error))
    conn.send(ptr, 8)
    return {"x": int(x), "y": int(y), "button": int(button)}
