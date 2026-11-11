"""系统命令：工作空间、文件列表、审计日志、任务队列。"""

from __future__ import annotations

from foxos.i18n import tr
import json
import os
import uuid
from pathlib import Path

from .. import __version__, audit
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app
from ..workspace import RESERVED_DIR

register_app("workspace", tr("system.workspace_info"), tr("system.the_current_workspace_root_and_basic"))
register_app("files", tr("system.files_list_read_and_write_text"), tr("system.every_operation_stays_inside_the"))
register_app("audit", tr("system.audit_log"), tr("system.query_foxos_audit_jsonl_who_ran"))
register_app("queue", tr("system.task_queue"), tr("system.records_task_goals_and_status_tasks"))


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
        raise FoxError("NOT_FOUND", tr("system.folder_not_found", ctx.rel(base)))
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
        raise FoxError("NOT_FOUND", tr("common.file_not_found", ctx.rel(path)))
    if path.is_dir():
        raise FoxError("USAGE", tr("system.is_a_folder_not_a_file", ctx.rel(path)), hint=tr("system.use_foxos_files_list_to_see_folders"))
    size = path.stat().st_size
    if size > TEXT_LIMIT:
        raise FoxError("USAGE", tr("system.file_too_large_bytes_the_text_read", size, TEXT_LIMIT))
    data = path.read_bytes()
    if b"\x00" in data[:8192]:
        raise FoxError("USAGE", tr("system.not_a_text_file", ctx.rel(path)), hint=tr("system.for_office_files_use_foxos_sheets"))
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise FoxError("USAGE", tr("system.not_utf_8_text", ctx.rel(path))) from e
    return {"path": ctx.rel(path), "content": text, "bytes": size, "modified": path.stat().st_mtime, "encoding": "utf-8"}


def files_write(ctx: Context, path: Path, content: str, expect_mtime: float | None = None, force: bool = False) -> dict:
    if path.is_dir():
        raise FoxError("USAGE", tr("system.is_a_folder", ctx.rel(path)))
    existed = path.exists()
    if expect_mtime is not None and existed and abs(path.stat().st_mtime - expect_mtime) > 1e-6 and not force:
        raise FoxError(
            "CONFLICT",
            tr("system.was_changed_after_you_opened_it", ctx.rel(path)),
            hint=tr("system.read_it_again_before_saving_or_use"),
            details={"expected_mtime": expect_mtime, "actual_mtime": path.stat().st_mtime},
        )
    data = content.encode("utf-8")
    saved = ctx.save_atomic(path, lambda p: p.write_bytes(data))
    return {"message": tr("system.saved_bytes", ctx.rel(path), len(data)), "path": ctx.rel(path), "bytes": len(data),
            "created": not existed, "modified": path.stat().st_mtime, **saved}


def files_mkdir(ctx: Context, path: Path) -> dict:
    if path.exists():
        raise FoxError("CONFLICT", tr("system.already_exists", ctx.rel(path)))
    path.mkdir(parents=True)
    return {"message": tr("system.created_folder", ctx.rel(path)), "path": ctx.rel(path)}


def files_rename(ctx: Context, source: Path, target: Path, force: bool = False) -> dict:
    if not source.exists():
        raise FoxError("NOT_FOUND", tr("system.does_not_exist", ctx.rel(source)))
    if source == ctx.workspace.root:
        raise FoxError("PERMISSION_DENIED", tr("system.the_workspace_root_cannot_be_renamed"))
    if target.exists() and not force:
        raise FoxError("CONFLICT", tr("system.target_already_exists", ctx.rel(target)), hint=tr("common.use_force_to_overwrite"))
    target.parent.mkdir(parents=True, exist_ok=True)
    src_rel = _rel_str(ctx, source)
    os.replace(source, target)
    return {"message": tr("system.renamed", src_rel, ctx.rel(target)), "source": src_rel, "target": ctx.rel(target)}


def _rel_str(ctx: Context, p: Path) -> str:
    return Path(os.path.relpath(p, ctx.workspace.root)).as_posix()


def files_delete(ctx: Context, path: Path) -> dict:
    """删除 = 移入 .foxos/trash/<id>/，可用 foxos files restore 恢复。"""
    if not path.exists():
        raise FoxError("NOT_FOUND", tr("system.does_not_exist", ctx.rel(path)))
    if path == ctx.workspace.root:
        raise FoxError("PERMISSION_DENIED", tr("system.the_workspace_root_cannot_be_deleted"))
    rel = ctx.rel(path)
    trash_id = audit.now_iso().replace(":", "").replace("-", "").replace(".", "")[:15] + "-" + uuid.uuid4().hex[:6]
    tdir = ctx.workspace.data_dir / "trash" / trash_id
    (tdir / rel).parent.mkdir(parents=True, exist_ok=True)
    os.replace(path, tdir / rel)
    (tdir / "meta.json").write_text(json.dumps({"path": rel, "deleted_by": ctx.agent, "deleted_at": audit.now_iso()},
                                               ensure_ascii=False), encoding="utf-8")
    return {"message": tr("system.moved_to_trash", rel), "path": rel, "trash_id": trash_id}


def files_restore(ctx: Context, trash_id: str, force: bool = False) -> dict:
    tdir = ctx.workspace.data_dir / "trash" / trash_id
    if "/" in trash_id or "\\" in trash_id or ".." in trash_id or not (tdir / "meta.json").exists():
        raise FoxError("NOT_FOUND", tr("system.not_in_the_trash", trash_id), hint=tr("system.see_foxos_files_trash"))
    meta = json.loads((tdir / "meta.json").read_text(encoding="utf-8"))
    target = ctx.resolve(meta["path"])
    if target.exists() and not force:
        raise FoxError("CONFLICT", tr("system.the_original_location_already_exists", meta['path']), hint=tr("common.use_force_to_overwrite"))
    from .. import locks

    with locks.write_lock(ctx.workspace, meta["path"], ctx.agent, ctx.lock_wait):
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tdir / meta["path"], target)
    import shutil

    shutil.rmtree(tdir, ignore_errors=True)
    return {"message": tr("system.restored", meta['path']), "path": meta["path"]}


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
        raise FoxError("USAGE", tr("system.limit_cannot_be_negative"))
    entries = audit.read(ctx.workspace, limit=limit, agent=agent, command=command)
    return {"count": len(entries), "entries": entries}


def _tasks_path(ctx: Context) -> Path:
    return ctx.workspace.data_dir / "tasks.jsonl"


def tasks_create(ctx: Context, goal: str) -> dict:
    if not goal.strip():
        raise FoxError("USAGE", tr("system.the_task_goal_cannot_be_empty"))
    task = {"id": "t-" + uuid.uuid4().hex[:8], "goal": goal.strip(), "status": "queued", "created_by": ctx.agent, "created_at": audit.now_iso()}
    with open(_tasks_path(ctx), "a", encoding="utf-8") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")
    return {"message": tr("system.added_to_the_task_queue", task['id']), "task": task}


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


register(Command("workspace", "info", tr("system.show_the_workspace_root_the_audit"), workspace_info,
                 examples=["foxos workspace info --json"]))
PATHP = lambda desc, access, req=True: Param("path", "string", desc, required=req, positional=True, path=access, metavar="PATH")  # noqa: E731
FORCE = Param("force", "boolean", tr("system.overwrite_if_the_target_exists"), default=False, cli_short="-f")

register(Command("files", "list", tr("system.list_a_folder_the_workspace_root_by"), files_list,
                 params=[PATHP(tr("system.folder_in_the_workspace_the_root_by"), "read", req=False),
                         Param("recursive", "boolean", tr("system.list_all_files_recursively"), default=False, cli_short="-r"),
                         Param("hidden", "boolean", tr("system.include_files_starting_with"), default=False, cli_short="-a")],
                 examples=["foxos files list", "foxos files list reports --json", "foxos files list -r"]))
register(Command("files", "read", tr("system.read_a_utf_8_text_file"), files_read,
                 params=[PATHP(tr("common.file_path"), "read")],
                 examples=["foxos files read notes.md", "foxos files read src/app.py --json"],
                 limits=[tr("system.limit_5_mb_use_the_matching_app")]))
register(Command("files", "write", tr("system.write_a_utf_8_text_file_atomic_save"), files_write,
                 params=[PATHP(tr("common.file_path"), "write"),
                         Param("content", "string", tr("system.file_content_on_the_cli_content"), required=True, cli_stdin=True),
                         Param("expect_mtime", "number", tr("system.optimistic_concurrency_check_the")),
                         FORCE],
                 examples=[tr("system.foxos_files_write_notes_md_content"), "cat a.py | foxos files write src/a.py --content-stdin"],
                 permission="modify"))
register(Command("files", "mkdir", tr("system.create_a_folder_with_parents"), files_mkdir,
                 params=[PATHP(tr("system.folder_path"), "write")], examples=["foxos files mkdir reports/2026"], permission="create"))
register(Command("files", "rename", tr("system.rename_or_move_a_file_folder"), files_rename,
                 params=[Param("source", "string", tr("system.original_path"), required=True, positional=True, path="write", metavar="SOURCE"),
                         Param("target", "string", tr("system.new_path"), required=True, positional=True, path="write", metavar="TARGET"),
                         FORCE],
                 examples=["foxos files rename draft.md final.md", "foxos files rename a.xlsx archive/a.xlsx"], permission="modify"))
register(Command("files", "delete", tr("system.delete_a_file_or_folder_moved_to_the"), files_delete,
                 params=[PATHP(tr("system.path_to_delete"), "write")], examples=["foxos files delete old.csv"],
                 limits=[tr("system.moved_to_foxos_trash_restore_with")], permission="delete"))
register(Command("files", "restore", tr("system.restore_from_the_trash"), files_restore,
                 params=[Param("trash_id", "string", tr("system.trash_entry_id_returned_by_files"), required=True, positional=True, metavar="TRASH_ID"),
                         FORCE],
                 examples=["foxos files restore 20261110T2051-ab12cd"], permission="create"))
register(Command("files", "trash", tr("system.list_the_trash"), files_trash, examples=["foxos files trash --json"]))
register(Command("audit", "tail", tr("system.show_recent_audit_records"), audit_tail,
                 params=[
                     Param("limit", "integer", tr("system.number_of_records"), default=20, cli_short="-n"),
                     Param("agent", "string", tr("system.only_one_agent"), cli_flag="--filter-agent"),
                     Param("command", "string", tr("system.filter_by_command_prefix_such_as")),
                 ],
                 examples=["foxos audit tail -n 50", "foxos audit tail --filter-agent data-agent --json"],
                 limits=[tr("system.the_query_itself_is_not_written_to")], audited=False))
register(Command("queue", "create", tr("system.add_a_task_goal_to_the_queue"), tasks_create,
                 params=[Param("goal", "string", tr("system.task_goal_natural_language"), required=True, positional=True, metavar="GOAL")],
                 examples=[tr("system.foxos_queue_create_make_an_analysis")],
                 limits=[tr("system.only_records_the_task_acp_agent")], permission="create"))
register(Command("queue", "list", tr("system.list_the_task_queue"), tasks_list,
                 params=[Param("limit", "integer", tr("system.number_of_records"), default=20, cli_short="-n")],
                 examples=["foxos queue list --json"]))


# ----------------------------------------------------------------------
# 人工接管：暂停 / 恢复智能体写操作
register_app("control", tr("system.human_takeover"), tr("system.while_paused_callers_that_are_not"))


def _pause_file(ctx: Context) -> Path:
    return ctx.workspace.data_dir / "paused"


def control_status(ctx: Context) -> dict:
    from ..kernel import control_state

    st = control_state(ctx.workspace)
    return {"paused": st is not None, **({"state": st} if st is not None else {})}


def control_pause(ctx: Context, reason: str | None = None, targets: list | None = None) -> dict:
    from ..kernel import control_state, is_human

    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("system.only_a_person_the_human_identity_can"))
    targets = [str(t) for t in (targets or []) if str(t).strip()]
    prev = control_state(ctx.workspace)
    if targets and prev is not None and prev.get("targets"):
        # 已经按身份暂停了一部分：合并
        targets = sorted(set(prev["targets"]) | set(targets))
    elif targets and prev is not None and not prev.get("targets"):
        targets = []  # 已经全体暂停，保持全体
    st = {"by": ctx.agent, "since": audit.now_iso(), "reason": reason}
    if targets:
        st["targets"] = targets
    _pause_file(ctx).write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
    msg = tr("system.paused_only", ", ".join(targets)) if targets else tr("system.taken_over_agent_writes_are_paused")
    return {"message": msg, "paused": True, "state": st}


def control_resume(ctx: Context, targets: list | None = None) -> dict:
    from ..kernel import control_state, is_human

    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("system.only_a_person_the_human_identity_can_2"))
    p = _pause_file(ctx)
    was = p.exists()
    st = control_state(ctx.workspace)
    if was and targets and st and st.get("targets"):
        left = [t for t in st["targets"] if t not in set(targets)]
        if left:
            st["targets"] = left
            p.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
            return {"message": tr("system.paused_only", ", ".join(left)), "paused": True, "state": st}
    if was:
        p.unlink()
    return {"message": tr("system.resumed_agents_can_write_again") if was else tr("system.not_paused"), "paused": False}


register(Command("control", "status", tr("system.show_whether_human_takeover_pause_is"), control_status,
                 examples=["foxos control status --json"], limits=[tr("system.the_query_itself_is_not_written_to")], audited=False))
register(Command("control", "pause", tr("system.human_takeover_pause_all_agent"), control_pause,
                 params=[Param("reason", "string", tr("system.reason_for_pausing_written_to_the")),
                         Param("targets", "array", tr("system.pause_targets"), items={"type": "string"}, cli_flag="--only", cli_repeat=True, metavar="IDENTITY")],
                 examples=[tr("system.foxos_control_pause_reason_i_am"), "foxos control pause --only bot:coder"],
                 limits=[tr("system.only_the_human_identity_can_run_this"), tr("system.the_identity_is_declared_by_the")], permission="modify"))
register(Command("control", "resume", tr("system.end_human_takeover_and_resume_agent"), control_resume,
                 params=[Param("targets", "array", tr("system.resume_targets"), items={"type": "string"}, cli_flag="--only", cli_repeat=True, metavar="IDENTITY")],
                 examples=["foxos control resume", "foxos control resume --only bot:coder"],
                 limits=[tr("system.only_the_human_identity_can_run_this")], permission="modify"))
