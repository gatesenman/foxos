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
register_app("files", "文件：列出、读写文本、新建、重命名、删除与恢复", "所有操作限定在工作空间内，删除进入回收站；.foxos 保留目录不可见。")
register_app("audit", "审计日志", "查询 .foxos/audit.jsonl：谁在什么时候对什么文件执行了什么命令。")
register_app("queue", "任务队列", "记录任务目标与状态；由桌面的 ACP 智能体会话执行。")


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


def _entry(ctx: Context, p: Path) -> dict:
    st = p.stat()
    return {
        "name": p.name,
        "path": ctx.rel(p),
        "type": "dir" if p.is_dir() else "file",
        "bytes": 0 if p.is_dir() else st.st_size,
        "modified": st.st_mtime,
    }


def files_list(ctx: Context, path: str | Path | None = None, recursive: bool = False, hidden: bool = False) -> dict:
    base = path if isinstance(path, Path) else ctx.workspace.root
    if not base.exists():
        raise FoxError("NOT_FOUND", f"目录不存在：{ctx.rel(base)}")
    if base.is_file():
        items = [base]
    elif recursive:
        items = list(_walk(base))
    else:
        items = sorted(
            (c for c in base.iterdir()
             if c.name != RESERVED_DIR and ".foxos-tmp-" not in c.name and (hidden or not c.name.startswith("."))),
            key=lambda c: (not c.is_dir(), c.name.lower()),
        )
    out = [_entry(ctx, p) for p in items]
    rel = ctx.rel(base) if base != ctx.workspace.root else ""
    return {"root": str(ctx.workspace.root), "path": "" if rel == "." else rel, "count": len(out), "entries": out,
            "files": [e for e in out if e["type"] == "file"]}


TEXT_LIMIT = 5 * 1024 * 1024


def files_read(ctx: Context, path: Path) -> dict:
    if not path.exists():
        raise FoxError("NOT_FOUND", f"文件不存在：{ctx.rel(path)}")
    if path.is_dir():
        raise FoxError("USAGE", f"是目录，不是文件：{ctx.rel(path)}", hint="用 foxos files list 查看目录")
    size = path.stat().st_size
    if size > TEXT_LIMIT:
        raise FoxError("USAGE", f"文件过大（{size} 字节），文本读取上限 {TEXT_LIMIT} 字节")
    data = path.read_bytes()
    if b"\x00" in data[:8192]:
        raise FoxError("USAGE", f"不是文本文件：{ctx.rel(path)}", hint="办公文件请用 foxos sheets/docs/slides read")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise FoxError("USAGE", f"不是 UTF-8 文本：{ctx.rel(path)}") from e
    return {"path": ctx.rel(path), "content": text, "bytes": size, "modified": path.stat().st_mtime, "encoding": "utf-8"}


def files_write(ctx: Context, path: Path, content: str, expect_mtime: float | None = None, force: bool = False) -> dict:
    if path.is_dir():
        raise FoxError("USAGE", f"是目录：{ctx.rel(path)}")
    existed = path.exists()
    if expect_mtime is not None and existed and abs(path.stat().st_mtime - expect_mtime) > 1e-6 and not force:
        raise FoxError(
            "CONFLICT",
            f"{ctx.rel(path)} 在你打开之后已被修改（可能是其他智能体或程序）",
            hint="重新读取后再保存，或使用 --force 覆盖",
            details={"expected_mtime": expect_mtime, "actual_mtime": path.stat().st_mtime},
        )
    data = content.encode("utf-8")
    saved = ctx.save_atomic(path, lambda p: p.write_bytes(data))
    return {"message": f"已保存 {ctx.rel(path)}（{len(data)} 字节）", "path": ctx.rel(path), "bytes": len(data),
            "created": not existed, "modified": path.stat().st_mtime, **saved}


def files_mkdir(ctx: Context, path: Path) -> dict:
    if path.exists():
        raise FoxError("CONFLICT", f"已存在：{ctx.rel(path)}")
    path.mkdir(parents=True)
    return {"message": f"已新建文件夹 {ctx.rel(path)}", "path": ctx.rel(path)}


def files_rename(ctx: Context, source: Path, target: Path, force: bool = False) -> dict:
    if not source.exists():
        raise FoxError("NOT_FOUND", f"不存在：{ctx.rel(source)}")
    if source == ctx.workspace.root:
        raise FoxError("PERMISSION_DENIED", "不能重命名工作空间根目录")
    if target.exists() and not force:
        raise FoxError("CONFLICT", f"目标已存在：{ctx.rel(target)}", hint="使用 --force 覆盖")
    target.parent.mkdir(parents=True, exist_ok=True)
    src_rel = _rel_str(ctx, source)
    os.replace(source, target)
    return {"message": f"已重命名 {src_rel} → {ctx.rel(target)}", "source": src_rel, "target": ctx.rel(target)}


def _rel_str(ctx: Context, p: Path) -> str:
    return Path(os.path.relpath(p, ctx.workspace.root)).as_posix()


def files_delete(ctx: Context, path: Path) -> dict:
    """删除 = 移入 .foxos/trash/<id>/，可用 foxos files restore 恢复。"""
    if not path.exists():
        raise FoxError("NOT_FOUND", f"不存在：{ctx.rel(path)}")
    if path == ctx.workspace.root:
        raise FoxError("PERMISSION_DENIED", "不能删除工作空间根目录")
    rel = ctx.rel(path)
    trash_id = audit.now_iso().replace(":", "").replace("-", "").replace(".", "")[:15] + "-" + uuid.uuid4().hex[:6]
    tdir = ctx.workspace.data_dir / "trash" / trash_id
    (tdir / rel).parent.mkdir(parents=True, exist_ok=True)
    os.replace(path, tdir / rel)
    (tdir / "meta.json").write_text(json.dumps({"path": rel, "deleted_by": ctx.agent, "deleted_at": audit.now_iso()},
                                               ensure_ascii=False), encoding="utf-8")
    return {"message": f"已移到回收站：{rel}", "path": rel, "trash_id": trash_id}


def files_restore(ctx: Context, trash_id: str, force: bool = False) -> dict:
    tdir = ctx.workspace.data_dir / "trash" / trash_id
    if "/" in trash_id or "\\" in trash_id or ".." in trash_id or not (tdir / "meta.json").exists():
        raise FoxError("NOT_FOUND", f"回收站中没有：{trash_id}", hint="用 foxos files trash 查看")
    meta = json.loads((tdir / "meta.json").read_text(encoding="utf-8"))
    target = ctx.resolve(meta["path"])
    if target.exists() and not force:
        raise FoxError("CONFLICT", f"原位置已存在：{meta['path']}", hint="使用 --force 覆盖")
    from .. import locks

    with locks.write_lock(ctx.workspace, meta["path"], ctx.agent, ctx.lock_wait):
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tdir / meta["path"], target)
    import shutil

    shutil.rmtree(tdir, ignore_errors=True)
    return {"message": f"已恢复 {meta['path']}", "path": meta["path"]}


def files_trash(ctx: Context) -> dict:
    base = ctx.workspace.data_dir / "trash"
    items = []
    if base.exists():
        for d in sorted(base.iterdir()):
            m = d / "meta.json"
            if m.exists():
                items.append({"trash_id": d.name, **json.loads(m.read_text(encoding="utf-8"))})
    return {"count": len(items), "items": items}


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
    return {"message": f"已加入任务队列：{task['id']}", "task": task}


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
PATHP = lambda desc, access, req=True: Param("path", "string", desc, required=req, positional=True, path=access, metavar="PATH")  # noqa: E731
FORCE = Param("force", "boolean", "目标已存在时覆盖", default=False, cli_short="-f")

register(Command("files", "list", "列出目录内容（默认工作空间根目录）", files_list,
                 params=[PATHP("目录（工作空间内），默认根目录", "read", req=False),
                         Param("recursive", "boolean", "递归列出所有文件", default=False, cli_short="-r"),
                         Param("hidden", "boolean", "包含以 . 开头的文件", default=False, cli_short="-a")],
                 examples=["foxos files list", "foxos files list reports --json", "foxos files list -r"]))
register(Command("files", "read", "读取 UTF-8 文本文件", files_read,
                 params=[PATHP("文件路径", "read")],
                 examples=["foxos files read notes.md", "foxos files read src/app.py --json"],
                 limits=["上限 5 MB；二进制与办公文件请用对应应用命令"]))
register(Command("files", "write", "写入 UTF-8 文本文件（原子保存，覆盖前保留上一版）", files_write,
                 params=[PATHP("文件路径", "write"),
                         Param("content", "string", "文件内容；CLI 可用 --content-stdin 从标准输入读取", required=True, cli_stdin=True),
                         Param("expect_mtime", "number", "乐观并发检查：文件当前修改时间必须等于该值，否则 CONFLICT"),
                         FORCE],
                 examples=["foxos files write notes.md --content '# 标题'", "cat a.py | foxos files write src/a.py --content-stdin"],
                 permission="modify"))
register(Command("files", "mkdir", "新建文件夹（含父目录）", files_mkdir,
                 params=[PATHP("文件夹路径", "write")], examples=["foxos files mkdir reports/2026"], permission="create"))
register(Command("files", "rename", "重命名或移动文件 / 文件夹", files_rename,
                 params=[Param("source", "string", "原路径", required=True, positional=True, path="write", metavar="SOURCE"),
                         Param("target", "string", "新路径", required=True, positional=True, path="write", metavar="TARGET"),
                         FORCE],
                 examples=["foxos files rename draft.md final.md", "foxos files rename a.xlsx archive/a.xlsx"], permission="modify"))
register(Command("files", "delete", "删除文件或文件夹（移入回收站，可恢复）", files_delete,
                 params=[PATHP("要删除的路径", "write")], examples=["foxos files delete old.csv"],
                 limits=["移入 .foxos/trash/，用 foxos files restore 恢复"], permission="delete"))
register(Command("files", "restore", "从回收站恢复", files_restore,
                 params=[Param("trash_id", "string", "回收站条目 ID（files delete 返回，或 files trash 查看）", required=True, positional=True, metavar="TRASH_ID"),
                         FORCE],
                 examples=["foxos files restore 20261110T2051-ab12cd"], permission="create"))
register(Command("files", "trash", "列出回收站", files_trash, examples=["foxos files trash --json"]))
register(Command("audit", "tail", "查看最近的审计记录", audit_tail,
                 params=[
                     Param("limit", "integer", "返回条数", default=20, cli_short="-n"),
                     Param("agent", "string", "只看某个智能体", cli_flag="--filter-agent"),
                     Param("command", "string", "按命令前缀过滤，如 sheets.write"),
                 ],
                 examples=["foxos audit tail -n 50", "foxos audit tail --filter-agent data-agent --json"],
                 limits=["查询本身不写入审计日志"], audited=False))
register(Command("queue", "create", "把一个任务目标加入队列", tasks_create,
                 params=[Param("goal", "string", "任务目标（自然语言）", required=True, positional=True, metavar="GOAL")],
                 examples=["foxos queue create '根据 sales.xlsx 制作分析报告'"],
                 limits=["只记录任务；执行由 ACP 智能体会话完成"], permission="create"))
register(Command("queue", "list", "列出任务队列", tasks_list,
                 params=[Param("limit", "integer", "返回条数", default=20, cli_short="-n")],
                 examples=["foxos queue list --json"]))


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
