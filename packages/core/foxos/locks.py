"""同一文件单写者锁。

每个被写入的文件在 .foxos/locks/ 下对应一个锁文件，用 O_CREAT|O_EXCL 原子创建，
内容记录持有者（智能体、进程、时间）。读操作不加锁，可以并行。

- 获取失败时立即返回 LOCKED（退出码 5），或在 --lock-wait 秒内重试。
- 持有进程已退出（POSIX 上检测 pid）或锁超过 stale_after 秒，视为陈旧锁并回收。
"""

from __future__ import annotations

from foxos.i18n import tr
import hashlib
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from .errors import FoxError
from .workspace import Workspace

STALE_AFTER_SECONDS = 600


def _lock_file(ws: Workspace, rel_path: str) -> Path:
    key = os.path.normcase(rel_path)
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return ws.locks_dir / f"{digest}.lock"


def _pid_alive(pid: int) -> bool:
    if os.name != "posix":
        return True  # Windows 上只依赖超时回收（os.kill(pid, 0) 在 Windows 上会终止进程）
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_holder(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _is_stale(path: Path, holder: dict | None) -> bool:
    try:
        age = time.time() - path.stat().st_mtime
    except FileNotFoundError:
        return True
    if age > STALE_AFTER_SECONDS:
        return True
    if holder and isinstance(holder.get("pid"), int) and holder.get("host") == _host():
        return not _pid_alive(holder["pid"])
    return False


def _host() -> str:
    try:
        return os.uname().nodename
    except AttributeError:
        return os.environ.get("COMPUTERNAME", "")


def acquire(ws: Workspace, rel_path: str, owner: str, wait: float = 0.0) -> Path:
    lock = _lock_file(ws, rel_path)
    deadline = time.monotonic() + max(wait, 0.0)
    payload = json.dumps(
        {"path": rel_path, "owner": owner, "pid": os.getpid(), "host": _host(), "acquired_at": time.time()},
        ensure_ascii=False,
    ).encode("utf-8")
    while True:
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            holder = read_holder(lock)
            if _is_stale(lock, holder):
                try:
                    lock.unlink()
                except FileNotFoundError:
                    pass
                continue
            if time.monotonic() >= deadline:
                who = (holder or {}).get("owner", tr("common.unknown"))
                raise FoxError(
                    "LOCKED",
                    tr("locks.is_being_written_by_only_one_writer", rel_path, who),
                    hint=tr("locks.retry_later_or_use_lock_wait_seconds"),
                    details={"path": rel_path, "holder": holder},
                )
            time.sleep(0.05)
            continue
        try:
            os.write(fd, payload)
        finally:
            os.close(fd)
        return lock


def release(lock: Path) -> None:
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


@contextmanager
def write_lock(ws: Workspace, rel_path: str, owner: str, wait: float = 0.0):
    lock = acquire(ws, rel_path, owner, wait)
    try:
        yield lock
    finally:
        release(lock)
