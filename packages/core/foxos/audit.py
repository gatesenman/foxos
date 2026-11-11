"""审计日志：每次命令调用（成功、失败、被拒绝）都追加一行 JSON 到 .foxos/audit.jsonl。

JSONL 是智能体和人都熟悉的格式：可以直接 `tail -f`、`jq`，桌面外壳也直接读它。
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from .workspace import Workspace


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def append(ws: Workspace, record: dict) -> dict:
    entry = {"id": uuid.uuid4().hex[:12], "ts": now_iso(), **record}
    line = json.dumps(entry, ensure_ascii=False, default=str) + "\n"
    data = line.encode("utf-8")
    # O_APPEND + 单次 write：多进程并发追加时每行保持完整。
    fd = os.open(ws.audit_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    return entry


def read(ws: Workspace, limit: int | None = None, agent: str | None = None, command: str | None = None) -> list[dict]:
    if not ws.audit_path.exists():
        return []
    out = []
    with open(ws.audit_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if agent and rec.get("agent") != agent:
                continue
            if command and not str(rec.get("command", "")).startswith(command):
                continue
            out.append(rec)
    if limit is not None and limit >= 0:
        out = out[-limit:] if limit else []
    return out


def append_safe(ws, record: dict) -> None:
    """不经内核的动作（ACP 终端、远程机器调用）也写审计；ws 可以是 Workspace 或工作空间根目录。"""
    from .workspace import Workspace
    try:
        append(ws if isinstance(ws, Workspace) else Workspace(ws), record)
    except OSError:
        pass
