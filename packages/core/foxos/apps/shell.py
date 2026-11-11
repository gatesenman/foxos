"""持久终端会话（tmux）：智能体像人一样在同一个 shell 里连续工作——cd、环境变量、虚拟环境都保留。

`foxos shell session new|list|exec|wait|read|send-keys|kill|history` = MCP `shell_session_*`。

- 每条 exec 返回输出、退出码、用时、结束后的当前目录；超时不杀进程，返回 timed_out，之后用 wait / read / send-keys C-c
- 输出原样记录在 .foxos/shell/<会话>/out.log，同时录成 asciicast v2（`asciinema play <文件>` 可回放）
- 工作空间约束：会话起始目录必须在工作空间内；智能体的会话默认在轻量沙箱（Landlock + seccomp）里运行，
  只能写工作空间（和私有 HOME / 临时目录）；只有人（human 身份）能开不加隔离的会话
- 审计：每条命令经内核写审计日志；会话自己的 history.jsonl 记录命令、退出码、用时；人工接管时 exec 返回 PAUSED

参考：SWE-agent / mini-swe-agent 的 ACI（命令 + 退出码 + 截断输出）、OpenHands 的 tmux 持久 bash、
Terminal-Bench 的 Terminus（tmux send-keys + 屏幕快照）、Warp 的「命令块」（每条命令一个块：命令、输出、退出码、目录）。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app

NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,40}$")
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()][A-Za-z0-9]|\x1b[=>78DEHMc]")
WIDTH, HEIGHT = 200, 50
MAX_OUT = 30000


# ------------------------------------------------------------------ 基础

def _tmux_bin() -> str:
    b = shutil.which("tmux")
    if not b:
        raise FoxError("DEPENDENCY_MISSING", tr("shell.no_tmux"), hint="sudo apt install tmux")
    return b


def _socket(ctx: Context) -> str:
    h = hashlib.sha1(str(ctx.workspace.root).encode()).hexdigest()[:10]
    return f"foxos-{h}"


def _tmux(ctx: Context, *args: str, check: bool = True, timeout: float = 10) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "TMUX"}
    p = subprocess.run([_tmux_bin(), "-L", _socket(ctx), *args], capture_output=True, text=True, timeout=timeout, env=env)
    if check and p.returncode != 0:
        raise FoxError("ERROR", tr("shell.tmux_failed", " ".join(args[:2]), (p.stderr or p.stdout).strip()))
    return p


def _root(ctx: Context) -> Path:
    d = ctx.workspace.data_dir / "shell"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _dir(ctx: Context, name: str) -> Path:
    return _root(ctx) / name


def _meta(ctx: Context, name: str) -> dict:
    if not NAME_RE.match(name or ""):
        raise FoxError("USAGE", tr("shell.bad_name"))
    f = _dir(ctx, name) / "meta.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise FoxError("NOT_FOUND", tr("shell.no_session", name), hint="foxos shell session list") from None


def _save_meta(ctx: Context, m: dict) -> None:
    f = _dir(ctx, m["name"]) / "meta.json"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, f)


def _alive(ctx: Context, name: str) -> bool:
    return _tmux(ctx, "has-session", "-t", f"={name}", check=False).returncode == 0


def _check_owner(ctx: Context, m: dict) -> None:
    """会话属于开它的身份；人可以操作任何会话，智能体只能操作自己的（或 shared 会话）。"""
    if is_human(ctx.agent) or m.get("shared") or m.get("owner") == ctx.agent:
        return
    owner = str(m.get("owner") or "")
    # bot:fox 与 bot:fox/acp:xxx 视为同一智能体
    if owner.split("/")[0] == str(ctx.agent).split("/")[0]:
        return
    raise FoxError("PERMISSION_DENIED", tr("shell.not_owner", m["name"], owner))


def clean(text: str) -> str:
    text = ANSI_RE.sub("", text)
    out = []
    for line in text.replace("\r\n", "\n").split("\n"):
        if "\r" in line:  # 进度条：只留最后一次覆盖的内容
            line = line.rstrip("\r").split("\r")[-1]
        out.append(line)
    return "\n".join(out)


def _clip(s: str, limit: int) -> tuple[str, bool]:
    if limit and len(s) > limit:
        head = limit // 3
        return s[:head] + f"\n…[{len(s) - limit} chars omitted]…\n" + s[-(limit - head):], True
    return s, False


def _isolation_default() -> str:
    try:
        from ..sandbox import linux
        return "light" if sys.platform.startswith("linux") and linux.abi_version() > 0 else "none"
    except Exception:  # noqa: BLE001
        return "none"


# ------------------------------------------------------------------ 命令

def session_new(ctx: Context, name: str | None = None, cwd: str | None = None, isolation: str | None = None,
                network: bool | None = None, record: bool | None = None, shared: bool = False, env: dict | None = None) -> dict:
    network, record = network is not False, record is not False
    name = name or f"s{uuid.uuid4().hex[:6]}"
    if not NAME_RE.match(name):
        raise FoxError("USAGE", tr("shell.bad_name"))
    if _alive(ctx, name):
        raise FoxError("CONFLICT", tr("shell.exists", name))
    start = ctx.resolve(cwd or ".")
    if not start.is_dir():
        raise FoxError("NOT_FOUND", tr("shell.no_dir", ctx.rel(start)))
    iso = isolation or ("none" if is_human(ctx.agent) else _isolation_default())
    if iso not in ("light", "none"):
        raise FoxError("USAGE", tr("shell.bad_isolation"))
    if iso == "none" and not is_human(ctx.agent):
        if _isolation_default() == "light":
            raise FoxError("PERMISSION_DENIED", tr("shell.none_human_only"))
    d = _dir(ctx, name)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "out.log").write_bytes(b"")
    cast = d / "session.cast"
    argv = ["bash", "--noprofile", "--norc", "-i"]
    if iso == "light":
        from .. import sandbox
        pol = sandbox.Policy(workspace=str(ctx.workspace.root), network=bool(network), home="private")
        pol = sandbox.prepare(pol, ["/bin/bash"], profile=f"shell-{_socket(ctx)}")
        argv = sandbox.launcher_argv(pol, ["/bin/bash", "--noprofile", "--norc", "-i"], profile=f"shell-{_socket(ctx)}")
    envs = {"FOXOS_AGENT": ctx.agent, "FOXOS_SHELL_SESSION": name, "TERM": "xterm-256color", "HISTFILE": "/dev/null",
            "PAGER": "cat", "GIT_PAGER": "cat", "LANG": os.environ.get("LANG") or "C.UTF-8", "FOXOS_WORKSPACE": str(ctx.workspace.root)}
    for k, v in (env or {}).items():
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(k)):
            raise FoxError("USAGE", tr("shell.bad_env", k))
        envs[str(k)] = str(v)
    eargs = []
    for k, v in envs.items():
        eargs += ["-e", f"{k}={v}"]
    _tmux(ctx, "new-session", "-d", "-s", name, "-x", str(WIDTH), "-y", str(HEIGHT), "-c", str(start), *eargs,
          " ".join(shlex.quote(a) for a in argv))
    try:
        return _finish_new(ctx, name, d, cast, start, iso, network, record, shared)
    except BaseException:
        _tmux(ctx, "kill-session", "-t", f"={name}", check=False)
        raise


def _finish_new(ctx, name, d, cast, start, iso, network, record, shared) -> dict:
    _tmux(ctx, "set-option", "-t", f"={name}", "history-limit", "50000", check=False)
    rec = [sys.executable, "-m", "foxos.cu.recorder", str(d / "out.log"), str(cast) if record else "-", str(WIDTH), str(HEIGHT)]
    core = str(Path(__file__).resolve().parents[2])
    pipe = f"PYTHONPATH={shlex.quote(core)} " + " ".join(shlex.quote(a) for a in rec)
    _tmux(ctx, "pipe-pane", "-o", "-t", f"={name}:", pipe)
    m = {"name": name, "owner": ctx.agent, "shared": bool(shared), "cwd": ctx.rel(start) if start != ctx.workspace.root else ".",
         "isolation": iso, "network": bool(network), "record": bool(record), "created": time.time(), "running": None, "seq": 0}
    _save_meta(ctx, m)
    # 关回显、清提示符，之后的输出就只有命令自己的输出
    _send_line(ctx, name, "stty -echo 2>/dev/null; PS1=''; PS2=''; PROMPT_COMMAND=''; unset HISTFILE; set +o history 2>/dev/null; cd " + shlex.quote(str(start)))
    r = _exec(ctx, m, "clear", timeout=15, record_history=False)
    _tmux(ctx, "clear-history", "-t", f"={name}:", check=False)
    if r.get("timed_out"):
        raise FoxError("ERROR", tr("shell.start_failed", name, clean((d / "out.log").read_text("utf-8", "replace"))[-400:]))
    return {"message": tr("shell.created", name, iso), "session": name, "isolation": iso, "cwd": m["cwd"],
            "recording": ctx.rel(cast) if record else None, "socket": _socket(ctx)}


def _send_line(ctx: Context, name: str, line: str) -> None:
    _tmux(ctx, "send-keys", "-t", f"={name}:", "-l", "--", line)
    _tmux(ctx, "send-keys", "-t", f"={name}:", "Enter")


def _log_size(ctx: Context, name: str) -> int:
    try:
        return (_dir(ctx, name) / "out.log").stat().st_size
    except OSError:
        return 0


def _read_from(ctx: Context, name: str, offset: int) -> str:
    with open(_dir(ctx, name) / "out.log", "rb") as f:
        f.seek(offset)
        return f.read().decode("utf-8", "replace")


def _marker_re(rid: str) -> re.Pattern:
    return re.compile("\x1eFX" + re.escape(rid) + r":(-?\d+):([^\x1e]*)\x1e")


def _exec(ctx: Context, m: dict, command: str, timeout: float = 120, max_output: int = MAX_OUT, record_history: bool = True) -> dict:
    name = m["name"]
    d = _dir(ctx, name)
    rid = uuid.uuid4().hex[:10]
    script = d / f"cmd-{rid}.sh"
    script.write_text(command.rstrip("\n") + "\n", encoding="utf-8")
    offset = _log_size(ctx, name)
    m["seq"] = int(m.get("seq") or 0) + 1
    m["running"] = {"id": rid, "command": command, "offset": offset, "started": time.time(), "seq": m["seq"]}
    _save_meta(ctx, m)
    a, b = rid[:5], rid[5:]
    _send_line(ctx, name, f"source {shlex.quote(str(script))}; printf '\\036FX%s%s:%d:%s\\036\\n' {a} {b} \"$?\" \"$PWD\"; rm -f {shlex.quote(str(script))}")
    return _wait(ctx, m, rid, timeout, max_output, record_history)


def _wait(ctx: Context, m: dict, rid: str, timeout: float, max_output: int, record_history: bool = True) -> dict:
    name = m["name"]
    run = m.get("running") or {}
    offset = int(run.get("offset") or 0)
    pat = _marker_re(rid)
    deadline = time.time() + max(0.0, float(timeout))
    while True:
        raw = _read_from(ctx, name, offset)
        mt = pat.search(raw)
        if mt or time.time() >= deadline or not _alive(ctx, name):
            break
        time.sleep(0.05)
    body = raw[:mt.start()] if mt else raw
    out, truncated = _clip(clean(body).strip("\n"), max_output)
    dur = round(time.time() - float(run.get("started") or time.time()), 3)
    res = {"session": name, "id": rid, "seq": run.get("seq"), "command": run.get("command"), "output": out, "truncated": truncated,
           "duration_s": dur}
    if mt:
        pwd = mt.group(2)
        res.update(exit_code=int(mt.group(1)), timed_out=False, running=False, cwd=_rel_or_abs(ctx, pwd))
        if not _inside(ctx, pwd):
            res["warning"] = tr("shell.outside_workspace", pwd)
        m["running"] = None
        m["cwd_now"] = res["cwd"]
        _save_meta(ctx, m)
        if record_history:
            with open(_dir(ctx, name) / "history.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"seq": run.get("seq"), "id": rid, "agent": ctx.agent, "command": run.get("command"),
                                    "exit_code": res["exit_code"], "duration_s": dur, "cwd": res["cwd"],
                                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, ensure_ascii=False) + "\n")
    elif not _alive(ctx, name):
        res.update(exit_code=None, timed_out=False, running=False, ended=True)
        m["running"] = None
        _save_meta(ctx, m)
    else:
        res.update(exit_code=None, timed_out=True, running=True,
                   hint=tr("shell.timed_out_hint", name, rid))
    return res


def _inside(ctx: Context, p: str) -> bool:
    try:
        Path(p).resolve().relative_to(ctx.workspace.root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _rel_or_abs(ctx: Context, p: str) -> str:
    if _inside(ctx, p):
        r = os.path.relpath(Path(p).resolve(), ctx.workspace.root.resolve())
        return "." if r == "." else r
    return p


def _live_meta(ctx: Context, name: str) -> dict:
    m = _meta(ctx, name)
    _check_owner(ctx, m)
    if not _alive(ctx, name):
        raise FoxError("NOT_FOUND", tr("shell.session_ended", name), hint="foxos shell session new")
    return m


def session_exec(ctx: Context, session: str, command: str, timeout: float = 120.0, max_output: int = MAX_OUT) -> dict:
    m = _live_meta(ctx, session)
    if m.get("running"):
        prev = m["running"]
        if not _marker_re(prev["id"]).search(_read_from(ctx, session, int(prev.get("offset") or 0))):
            raise FoxError("CONFLICT", tr("shell.busy", session, prev.get("command", "")[:80]),
                           hint=tr("shell.busy_hint", session, prev["id"]))
        _wait(ctx, m, prev["id"], 0, max_output)  # 上一条已经结束：补记历史
    if not command.strip():
        raise FoxError("USAGE", tr("shell.empty_command"))
    return _exec(ctx, m, command, timeout=float(timeout), max_output=int(max_output))


def session_wait(ctx: Context, session: str, id: str | None = None, timeout: float = 60.0, max_output: int = MAX_OUT) -> dict:
    m = _live_meta(ctx, session)
    run = m.get("running")
    if not run:
        raise FoxError("NOT_FOUND", tr("shell.nothing_running", session))
    if id and run["id"] != id:
        raise FoxError("NOT_FOUND", tr("shell.no_such_run", id))
    return _wait(ctx, m, run["id"], float(timeout), int(max_output))


def session_read(ctx: Context, session: str, mode: str = "screen", lines: int = 50, since: int | None = None) -> dict:
    m = _meta(ctx, session)
    _check_owner(ctx, m)
    if mode == "screen":
        if not _alive(ctx, session):
            raise FoxError("NOT_FOUND", tr("shell.session_ended", session))
        p = _tmux(ctx, "capture-pane", "-p", "-J", "-t", f"={session}:", "-S", f"-{max(0, int(lines) - HEIGHT)}" if int(lines) > HEIGHT else "0")
        text = p.stdout.rstrip("\n")
        cur = _tmux(ctx, "display-message", "-p", "-t", f"={session}:", "#{pane_current_command}|#{cursor_x},#{cursor_y}").stdout.strip()
        cmd, _, cursor = cur.partition("|")
        return {"session": session, "mode": "screen", "screen": text, "foreground": cmd, "cursor": cursor,
                "running": m.get("running")}
    if mode == "log":
        size = _log_size(ctx, session)
        start = int(since) if since is not None else max(0, size - 200_000)
        text = clean(_read_from(ctx, session, start))
        tail = "\n".join(text.split("\n")[-int(lines):]) if since is None else text
        out, truncated = _clip(tail, MAX_OUT)
        return {"session": session, "mode": "log", "output": out, "truncated": truncated, "offset": size, "running": m.get("running")}
    raise FoxError("USAGE", tr("shell.bad_read_mode"))


_KEY_RE = re.compile(r"^(?:[CMS]-)*(?:[A-Za-z0-9]|Enter|Escape|Tab|BSpace|Space|Up|Down|Left|Right|Home|End|PageUp|PageDown|PPage|NPage|DC|IC|F\d{1,2}|BTab)$")


def session_send_keys(ctx: Context, session: str, keys: list | None = None, text: str | None = None, enter: bool = False) -> dict:
    _live_meta(ctx, session)
    if not keys and text is None:
        raise FoxError("USAGE", tr("shell.keys_or_text"))
    if text is not None:
        _tmux(ctx, "send-keys", "-t", f"={session}:", "-l", "--", text)
    for k in keys or []:
        if not _KEY_RE.match(str(k)):
            raise FoxError("USAGE", tr("shell.bad_key", k))
        _tmux(ctx, "send-keys", "-t", f"={session}:", str(k))
    if enter:
        _tmux(ctx, "send-keys", "-t", f"={session}:", "Enter")
    time.sleep(0.15)
    return {"message": tr("shell.sent", session), "session": session, "keys": keys or [], "text_length": len(text or "")}


def session_kill(ctx: Context, session: str) -> dict:
    m = _meta(ctx, session)
    _check_owner(ctx, m)
    alive = _alive(ctx, session)
    if alive:
        _tmux(ctx, "kill-session", "-t", f"={session}", check=False)
    m["running"] = None
    m["ended"] = time.time()
    _save_meta(ctx, m)
    return {"message": tr("shell.killed", session), "session": session, "was_running": alive,
            "recording": ctx.rel(_dir(ctx, session) / "session.cast") if m.get("record") else None}


def session_list(ctx: Context) -> dict:
    out = []
    for d in sorted(_root(ctx).iterdir()) if _root(ctx).exists() else []:
        f = d / "meta.json"
        if not f.is_file():
            continue
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out.append({"session": m["name"], "owner": m.get("owner"), "alive": _alive(ctx, m["name"]), "isolation": m.get("isolation"),
                    "cwd": m.get("cwd_now") or m.get("cwd"), "commands": m.get("seq", 0) - 1 if m.get("seq") else 0,
                    "running": (m.get("running") or {}).get("command"),
                    "recording": ctx.rel(d / "session.cast") if m.get("record") else None})
    return {"count": len(out), "sessions": out}


def session_history(ctx: Context, session: str, limit: int = 50) -> dict:
    m = _meta(ctx, session)
    _check_owner(ctx, m)
    f = _dir(ctx, session) / "history.jsonl"
    rows = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()] if f.exists() else []
    return {"session": session, "count": len(rows), "history": rows[-int(limit):],
            "recording": ctx.rel(_dir(ctx, session) / "session.cast") if m.get("record") else None}


# ------------------------------------------------------------------ 注册

register_app("shell", tr("shell.app_title"), tr("shell.app_summary"))
S = Param("session", "string", tr("shell.p_session"), required=True, positional=True, metavar="SESSION")
register(Command("shell", "session new", tr("shell.c_new"), session_new,
                 params=[Param("name", "string", tr("shell.p_name"), positional=True, metavar="NAME"),
                         Param("cwd", "string", tr("shell.p_cwd"), path="read"),
                         Param("isolation", "string", tr("shell.p_isolation"), enum=["light", "none"]),
                         Param("network", "boolean", tr("shell.p_network")),
                         Param("record", "boolean", tr("shell.p_record")),
                         Param("shared", "boolean", tr("shell.p_shared"), default=False),
                         Param("env", "object", tr("shell.p_env"), cli_kv=True)],
                 examples=["foxos shell session new dev --cwd .", "foxos shell session new build --isolation light --no-network"],
                 limits=[tr("shell.l_isolation"), tr("shell.l_bounds")], permission="run"))
register(Command("shell", "session exec", tr("shell.c_exec"), session_exec,
                 params=[S, Param("command", "string", tr("shell.p_command"), required=True, positional=True, metavar="COMMAND", cli_stdin=True),
                         Param("timeout", "number", tr("shell.p_timeout"), default=120.0),
                         Param("max_output", "integer", tr("shell.p_max_output"), default=MAX_OUT)],
                 examples=["foxos shell session exec dev 'python3 -m venv .venv && . .venv/bin/activate'", "foxos shell session exec dev 'pytest -q' --timeout 600"],
                 limits=[tr("shell.l_timeout")], permission="run"))
register(Command("shell", "session wait", tr("shell.c_wait"), session_wait,
                 params=[S, Param("id", "string", tr("shell.p_id")), Param("timeout", "number", tr("shell.p_timeout"), default=60.0),
                         Param("max_output", "integer", tr("shell.p_max_output"), default=MAX_OUT)],
                 examples=["foxos shell session wait dev --timeout 300"], permission="read"))
register(Command("shell", "session read", tr("shell.c_read"), session_read,
                 params=[S, Param("mode", "string", tr("shell.p_mode"), enum=["screen", "log"], default="screen"),
                         Param("lines", "integer", tr("shell.p_lines"), default=50), Param("since", "integer", tr("shell.p_since"))],
                 examples=["foxos shell session read dev", "foxos shell session read dev --mode log --lines 200"], permission="read"))
register(Command("shell", "session send-keys", tr("shell.c_keys"), session_send_keys,
                 params=[S, Param("keys", "array", tr("shell.p_keys"), positional=True, items={"type": "string"}, metavar="KEY"),
                         Param("text", "string", tr("shell.p_text")), Param("enter", "boolean", tr("shell.p_enter"), default=False)],
                 examples=["foxos shell session send-keys dev C-c", "foxos shell session send-keys dev --text 'print(1+1)' --enter"],
                 permission="run"))
register(Command("shell", "session kill", tr("shell.c_kill"), session_kill, params=[S],
                 examples=["foxos shell session kill dev"], permission="run"))
register(Command("shell", "session list", tr("shell.c_list"), session_list, examples=["foxos shell session list --json"], permission="read"))
register(Command("shell", "session history", tr("shell.c_history"), session_history,
                 params=[S, Param("limit", "integer", tr("shell.p_limit"), default=50)],
                 examples=["foxos shell session history dev"], permission="read"))
