"""系统命令：工作空间、文件列表、审计日志、任务队列。"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from .. import __version__, audit
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app
from ..workspace import RESERVED_DIR

register_app("workspace", "工作空间信息", "当前工作空间根目录与基本信息。")
register_app("files", "列出工作空间文件", "只读列出工作空间内的文件，忽略 .foxos 保留目录。")
register_app("audit", "审计日志", "查询 .foxos/audit.jsonl：谁在什么时候对什么文件执行了什么命令。")
register_app("tasks", "任务队列", "阶段 0 只记录任务，尚未接入模型自动执行。")


def workspace_info(ctx: Context) -> dict:
    files = sum(1 for _ in _walk(ctx.workspace.root))
    return {
        "root": str(ctx.workspace.root),
        "data_dir": str(ctx.workspace.data_dir),
        "audit_log": str(ctx.workspace.audit_path),
        "files": files,
        "version": __version__,
        "agent": ctx.agent,
    }


def _walk(base: Path):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d != RESERVED_DIR and not d.startswith("."))
        for fn in sorted(filenames):
            if ".foxos-tmp-" in fn:
                continue
            yield Path(dirpath) / fn


def files_list(ctx: Context, path: str | Path | None = None) -> dict:
    base = path if isinstance(path, Path) else ctx.workspace.root
    if not base.exists():
        raise FoxError("NOT_FOUND", f"目录不存在：{ctx.rel(base)}")
    if base.is_file():
        items = [base]
    else:
        items = list(_walk(base))
    out = []
    for p in items:
        st = p.stat()
        out.append({"path": ctx.rel(p), "bytes": st.st_size, "modified": st.st_mtime})
    return {"root": str(ctx.workspace.root), "count": len(out), "files": out}


def audit_tail(ctx: Context, limit: int = 20, agent: str | None = None, command: str | None = None) -> dict:
    if limit < 0:
        raise FoxError("USAGE", "limit 不能为负数")
    entries = audit.read(ctx.workspace, limit=limit, agent=agent, command=command)
    return {"count": len(entries), "entries": entries}


def _tasks_path(ctx: Context) -> Path:
    return ctx.workspace.data_dir / "tasks.jsonl"


def tasks_create(ctx: Context, goal: str) -> dict:
    if not goal.strip():
        raise FoxError("USAGE", "任务目标不能为空")
    task = {"id": "t-" + uuid.uuid4().hex[:8], "goal": goal.strip(), "status": "queued", "created_by": ctx.agent, "created_at": audit.now_iso()}
    with open(_tasks_path(ctx), "a", encoding="utf-8") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")
    return {"message": f"已加入任务队列：{task['id']}（阶段 0 尚未接入模型自动执行）", "task": task}


def tasks_list(ctx: Context, limit: int = 20) -> dict:
    p = _tasks_path(ctx)
    tasks = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    tasks = tasks[-limit:] if limit else []
    return {"count": len(tasks), "tasks": tasks}


register(Command("workspace", "info", "显示工作空间根目录、审计日志位置与文件数", workspace_info,
                 examples=["foxos workspace info --json"]))
register(Command("files", "list", "列出工作空间内的文件", files_list,
                 params=[Param("path", "string", "子目录（工作空间内），默认根目录", positional=True, path="read", metavar="PATH")],
                 examples=["foxos files list", "foxos files list reports --json"]))
register(Command("audit", "tail", "查看最近的审计记录", audit_tail,
                 params=[
                     Param("limit", "integer", "返回条数", default=20, cli_short="-n"),
                     Param("agent", "string", "只看某个智能体", cli_flag="--filter-agent"),
                     Param("command", "string", "按命令前缀过滤，如 sheets.write"),
                 ],
                 examples=["foxos audit tail -n 50", "foxos audit tail --filter-agent data-agent --json"],
                 limits=["查询本身不写入审计日志"], audited=False))
register(Command("tasks", "create", "把一个任务目标加入队列", tasks_create,
                 params=[Param("goal", "string", "任务目标（自然语言）", required=True, positional=True, metavar="GOAL")],
                 examples=["foxos tasks create '根据 sales.xlsx 制作分析报告'"],
                 limits=["阶段 0 只记录任务，不会自动调用模型执行"], permission="create"))
register(Command("tasks", "list", "列出任务队列", tasks_list,
                 params=[Param("limit", "integer", "返回条数", default=20, cli_short="-n")],
                 examples=["foxos tasks list --json"]))


# ----------------------------------------------------------------------
# 人工接管：暂停 / 恢复智能体写操作
register_app("control", "人工接管", "暂停后，非 human 身份的调用者不能执行任何写操作（读操作不受影响），返回 PAUSED（退出码 8）。")


def _pause_file(ctx: Context) -> Path:
    return ctx.workspace.data_dir / "paused"


def control_status(ctx: Context) -> dict:
    from ..kernel import control_state

    st = control_state(ctx.workspace)
    return {"paused": st is not None, **({"state": st} if st is not None else {})}


def control_pause(ctx: Context, reason: str | None = None) -> dict:
    from ..kernel import is_human

    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", "只有人（human 身份）可以发起人工接管")
    st = {"by": ctx.agent, "since": audit.now_iso(), "reason": reason}
    _pause_file(ctx).write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
    return {"message": "已人工接管：智能体写操作暂停", "paused": True, "state": st}


def control_resume(ctx: Context) -> dict:
    from ..kernel import is_human

    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", "只有人（human 身份）可以恢复智能体")
    p = _pause_file(ctx)
    was = p.exists()
    if was:
        p.unlink()
    return {"message": "已恢复：智能体可以继续写入" if was else "当前未暂停", "paused": False}


register(Command("control", "status", "查看是否处于人工接管（暂停）状态", control_status,
                 examples=["foxos control status --json"], limits=["查询本身不写入审计日志"], audited=False))
register(Command("control", "pause", "人工接管：暂停所有智能体的写操作", control_pause,
                 params=[Param("reason", "string", "暂停原因（写入状态与审计）")],
                 examples=["foxos control pause --reason '我来改第 3 页数据'"],
                 limits=["只有 human 身份可以执行", "身份由调用方声明（--agent），属于应用层约束"], permission="modify"))
register(Command("control", "resume", "结束人工接管，恢复智能体写操作", control_resume,
                 examples=["foxos control resume"],
                 limits=["只有 human 身份可以执行"], permission="modify"))
