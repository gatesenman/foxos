"""谁正在操作这台狐狸OS：每个非人身份最近一次命令（.foxos/activity.json），以及桌面输入的占用（desktop-owner.json）。

多个智能体共用一台机器时，界面（聊天窗口、底栏「正在操作」）读这里显示是哪个智能体在动；
桌面输入（键入、点击、聚焦、启动……）同一时间只归一个智能体，另一个在占用期内会得到 CONFLICT。
"""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from .errors import FoxError
from .i18n import tr

ACTIVE_SECONDS = 60
CLAIM_SECONDS = float(os.environ.get("FOXOS_DESKTOP_CLAIM_SECONDS", "20"))


@contextmanager
def _flock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        except ImportError:  # Windows：只有一个桌面进程写，不加锁
            pass
        yield
    finally:
        os.close(fd)


def _read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write(path: Path, data: dict) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def record(ws, agent: str, command: str, status: str, machine: str | None = None) -> None:
    from .kernel import is_human
    if is_human(agent):
        return
    p = ws.data_dir / "activity.json"
    with _flock(ws.data_dir / "activity.lock"):
        d = _read(p)
        now = time.time()
        d = {k: v for k, v in d.items() if now - v.get("t", 0) < 3600}
        d[agent] = {"command": command, "status": status, "t": now, **({"machine": machine} if machine else {})}
        _write(p, d)


def current(ws, within: float = ACTIVE_SECONDS) -> list[dict]:
    d = _read(ws.data_dir / "activity.json")
    now = time.time()
    out = [{"agent": k, **v, "seconds_ago": round(now - v.get("t", 0), 1)} for k, v in d.items() if now - v.get("t", 0) <= within]
    out.sort(key=lambda x: x["seconds_ago"])
    owner = desktop_owner(ws)
    return [{**x, "desktop": bool(owner and owner["agent"] == x["agent"])} for x in out]


def desktop_owner(ws) -> dict | None:
    d = _read(ws.data_dir / "desktop-owner.json")
    if d and d.get("until", 0) > time.time():
        return d
    return None


def claim_desktop(ws, agent: str, seconds: float | None = None) -> None:
    """桌面输入的占用：同一时间只归一个智能体（人随时可以操作，不受限制）。"""
    from .kernel import agent_matches, is_human
    if is_human(agent):
        return
    p = ws.data_dir / "desktop-owner.json"
    with _flock(ws.data_dir / "desktop-owner.lock"):
        cur = _read(p)
        now = time.time()
        if cur and cur.get("until", 0) > now and cur.get("agent") != agent and not agent_matches(agent, [cur.get("agent")]):
            raise FoxError("CONFLICT", tr("activity.desktop_in_use", cur.get("agent"), int(cur["until"] - now) + 1),
                           hint=tr("activity.desktop_in_use_hint"), details={"holder": cur.get("agent"), "until": cur.get("until")})
        _write(p, {"agent": agent, "since": cur.get("since", now) if cur.get("agent") == agent else now,
                   "until": now + (CLAIM_SECONDS if seconds is None else seconds)})


def release_desktop(ws, agent: str) -> bool:
    p = ws.data_dir / "desktop-owner.json"
    with _flock(ws.data_dir / "desktop-owner.lock"):
        cur = _read(p)
        if cur.get("agent") == agent:
            p.unlink(missing_ok=True)
            return True
    return False
