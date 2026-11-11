"""统一命令内核：命令注册、参数校验、路径约束、写锁、审计。

CLI、MCP 工具服务器、桌面外壳都只调用 invoke()。每个命令只定义一次（Command），
CLI 参数、JSON Schema、能力目录（foxos help --json）都从这份定义生成。
"""

from __future__ import annotations

from foxos.i18n import tr
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from . import audit, locks
from .errors import FoxError
from .workspace import Workspace

JSON_TYPES = {"string", "integer", "number", "boolean", "object", "array"}


@dataclass
class Param:
    name: str
    type: str
    description: str
    required: bool = False
    default: Any = None
    enum: list | None = None
    items: dict | None = None  # array 元素 schema
    positional: bool = False
    # path 参数：自动做工作空间约束；access="write" 时自动加单写者锁
    path: str | None = None  # None | "read" | "write"
    # CLI 专用：object 类型以多个 KEY=VALUE 位置参数传入（如 A1=100 B2==SUM(A1:A3)）
    cli_kv: bool = False
    cli_flag: str | None = None  # 默认 --name（下划线转连字符）
    cli_short: str | None = None
    cli_repeat: bool = False  # array 参数在 CLI 中以重复选项传入（--bullet a --bullet b），否则逗号分隔
    cli_stdin: bool = False  # string 参数可用 --<name>-stdin 从标准输入读取（大文本，如编辑器保存）
    metavar: str | None = None

    def __post_init__(self):
        assert self.type in JSON_TYPES, self.type

    @property
    def flag(self) -> str:
        return self.cli_flag or "--" + self.name.replace("_", "-")

    def schema(self) -> dict:
        s: dict = {"type": self.type, "description": self.description}
        if self.enum:
            s["enum"] = list(self.enum)
        if self.default is not None:
            s["default"] = self.default
        if self.items:
            s["items"] = self.items
        if self.type == "object" and self.cli_kv:
            s["additionalProperties"] = {"type": ["string", "number", "boolean", "null"]}
        return s


@dataclass
class Command:
    app: str
    name: str  # 例如 "create"、"chart create"
    summary: str
    handler: Callable[..., dict]
    params: list[Param] = field(default_factory=list)
    description: str = ""
    examples: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    permission: str = "read"  # read | create | modify | delete | run
    audited: bool = True  # 只读的系统自省命令（audit tail、control status）不写审计，避免界面轮询淹没真实操作

    @property
    def id(self) -> str:
        return ".".join([self.app, *self.name.split()])

    @property
    def tool_name(self) -> str:
        return self.id.replace(".", "_")

    @property
    def cli(self) -> str:
        return f"foxos {self.app} {self.name}"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {p.name: p.schema() for p in self.params},
            "required": [p.name for p in self.params if p.required],
            "additionalProperties": False,
        }

    def usage(self) -> str:
        parts = [self.cli]
        for p in self.params:
            if p.positional:
                tok = (p.metavar or p.name.upper()) + ("..." if p.cli_kv or p.type == "array" else "")
                parts.append(tok if p.required else f"[{tok}]")
        for p in self.params:
            if not p.positional:
                if p.type == "boolean":
                    parts.append(f"[{p.flag}]")
                else:
                    val = "{" + ",".join(map(str, p.enum)) + "}" if p.enum else (p.metavar or p.name.upper())
                    parts.append(f"{p.flag} {val}" if p.required else f"[{p.flag} {val}]")
        return " ".join(parts)


@dataclass
class Context:
    workspace: Workspace
    agent: str = "human"
    task: str | None = None
    lock_wait: float = 0.0
    interface: str = "cli"  # cli | mcp | desktop

    def rel(self, path: Path) -> str:
        return self.workspace.rel(path)

    def resolve(self, p: str) -> Path:
        return self.workspace.resolve(p)

    # 原子保存 + 版本记录：先写临时文件再 os.replace；覆盖已有文件前保留上一版本
    def save_atomic(self, target: Path, writer: Callable[[Path], None]) -> dict:
        target.parent.mkdir(parents=True, exist_ok=True)
        version = None
        if target.exists():
            stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
            vdir = self.workspace.versions_dir / self.rel(target)
            vdir.mkdir(parents=True, exist_ok=True)
            safe_agent = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.agent)
            vpath = vdir / f"{stamp}-{safe_agent}{target.suffix}"
            shutil.copy2(target, vpath)
            version = Path(os.path.relpath(vpath, self.workspace.root)).as_posix()
        tmp = target.with_name(f".{target.name}.foxos-tmp-{os.getpid()}{target.suffix}")
        try:
            writer(tmp)
            os.replace(tmp, target)
        finally:
            if tmp.exists():
                tmp.unlink()
        return {"previous_version": version}


def is_human(agent: str) -> bool:
    return agent == "human" or agent.startswith("human:")


def control_state(ws: Workspace) -> dict | None:
    """人工接管状态：.foxos/paused 存在即暂停所有智能体（非 human）的写操作。"""
    p = ws.data_dir / "paused"
    if not p.exists():
        return None
    try:
        import json

        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


REGISTRY: dict[str, Command] = {}
APPS: dict[str, dict] = {}


def register_app(name: str, summary: str, description: str = "", limits: list[str] | None = None) -> None:
    APPS[name] = {"name": name, "summary": summary, "description": description, "limits": limits or []}


def register(cmd: Command) -> Command:
    if cmd.id in REGISTRY:
        raise ValueError(f"duplicate command {cmd.id}")
    REGISTRY[cmd.id] = cmd
    return cmd


def load_apps() -> None:
    # 导入即注册
    from .apps import desktop, docs, env, everything, sandbox, sheets, slides, system  # noqa: F401


def find(command_id: str) -> Command:
    load_apps()
    cid = command_id.replace("_", ".") if command_id not in REGISTRY else command_id
    if cid in REGISTRY:
        return REGISTRY[cid]
    for c in REGISTRY.values():
        if c.tool_name == command_id or c.id == command_id:
            return c
    raise FoxError("NOT_FOUND", tr("kernel.unknown_command", command_id), hint=tr("kernel.run_foxos_help_json_to_see_all"))


# ----------------------------------------------------------------------
def _check_type(p: Param, v: Any) -> Any:
    t = p.type
    ok = {
        "string": lambda x: isinstance(x, str),
        "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        "boolean": lambda x: isinstance(x, bool),
        "object": lambda x: isinstance(x, dict),
        "array": lambda x: isinstance(x, list),
    }[t]
    if not ok(v):
        raise FoxError("USAGE", tr("kernel.parameter_should_be_got", p.name, t, type(v).__name__), details={"param": p.name})
    if p.enum and v not in p.enum:
        raise FoxError("USAGE", tr("kernel.parameter_must_be_one_of_got", p.name, ', '.join(map(str, p.enum)), v), details={"param": p.name})
    return v


def validate(cmd: Command, params: dict) -> dict:
    params = dict(params or {})
    known = {p.name for p in cmd.params}
    unknown = sorted(set(params) - known)
    if unknown:
        raise FoxError("USAGE", tr("kernel.does_not_accept_parameter", cmd.cli, ', '.join(unknown)), hint=tr("kernel.usage", cmd.usage()))
    out = {}
    for p in cmd.params:
        if p.name not in params or params[p.name] is None:
            if p.required:
                raise FoxError("USAGE", tr("kernel.missing_required_parameter", p.name), hint=tr("kernel.usage", cmd.usage()), details={"param": p.name})
            out[p.name] = p.default
            continue
        out[p.name] = _check_type(p, params[p.name])
    return out


def invoke(command_id: str, params: dict | None, ctx: Context) -> dict:
    """执行命令并写审计日志。成功返回 result dict，失败抛出 FoxError（同样已记审计）。"""
    t0 = time.monotonic()
    record: dict = {
        "agent": ctx.agent,
        "task": ctx.task,
        "interface": ctx.interface,
        "command": command_id,
        "args": params or {},
    }
    held: list[Path] = []
    try:
        cmd = find(command_id)
        record["command"] = cmd.id
        record["permission"] = cmd.permission
        values = validate(cmd, params or {})
        if cmd.permission != "read" and cmd.app != "control" and not is_human(ctx.agent) and control_state(ctx.workspace):
            st = control_state(ctx.workspace)
            raise FoxError(
                "PAUSED",
                tr("kernel.human_takeover_is_active_agent", st.get('by', tr("common.unknown"))),
                hint=tr("kernel.wait_for_a_person_to_run_foxos"),
                details=st,
            )
        targets = []
        for p in cmd.params:
            if p.path and values.get(p.name):
                resolved = ctx.resolve(values[p.name])
                rel = ctx.rel(resolved)
                targets.append({"path": rel, "access": p.path})
                values[p.name] = resolved
        record["targets"] = targets
        # 写锁：按路径排序获取，避免多个目标时死锁
        for t in sorted((t for t in targets if t["access"] == "write"), key=lambda t: t["path"]):
            held.append(locks.acquire(ctx.workspace, t["path"], ctx.agent, ctx.lock_wait))
        result = cmd.handler(ctx, **values)
        record["status"] = "ok"
        if isinstance(result, dict) and result.get("message"):
            record["message"] = result["message"]
        return result
    except FoxError as e:
        record["status"] = "denied" if e.code in ("PERMISSION_DENIED", "LOCKED", "PAUSED") else "error"
        record["error"] = {"code": e.code, "message": e.message}
        raise
    except Exception as e:  # 内部错误也要进审计
        record["status"] = "error"
        record["error"] = {"code": "ERROR", "message": f"{type(e).__name__}: {e}"}
        raise FoxError("ERROR", f"{type(e).__name__}: {e}") from e
    finally:
        for lk in held:
            locks.release(lk)
        record["duration_ms"] = round((time.monotonic() - t0) * 1000, 1)
        cmd_obj = REGISTRY.get(record["command"])
        if cmd_obj is None or cmd_obj.audited or record.get("status") != "ok":
            try:
                audit.append(ctx.workspace, record)
            except OSError:
                pass
