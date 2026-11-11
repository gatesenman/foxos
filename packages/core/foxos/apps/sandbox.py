"""foxos sandbox：轻量隔离级别（进程级沙箱）。

与 foxos env（完全隔离：独立发行版 / 虚拟机）互补：直接用宿主上的程序与工具链，零启动开销，
但只能读写工作空间（与声明的路径），可选禁止联网。实现见 foxos/sandbox/。
"""

from __future__ import annotations

from foxos.i18n import tr
import shlex
import subprocess
import time

from .. import sandbox as sb
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app


def _policy(ctx: Context, network: str, read: list | None, write: list | None, home: str, windows_mode: str,
            max_processes: int | None, memory_mb: int | None) -> sb.Policy:
    ws = str(ctx.workspace.root)
    return sb.Policy(workspace=ws, read=[str(ctx.workspace.root / p) if not _abs(p) else p for p in (read or [])],
                     write=[str(ctx.workspace.root / p) if not _abs(p) else p for p in (write or [])],
                     network=network != "off", home=home, windows_mode=windows_mode, max_processes=max_processes, memory_mb=memory_mb)


def _profile(ctx: Context) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", ctx.agent or "default")[:40] or "default"


def _abs(p: str) -> bool:
    import os
    return os.path.isabs(p)


def sandbox_check(ctx: Context) -> dict:
    return sb.capabilities()


def _require():
    caps = sb.capabilities()
    if not caps.get("available"):
        raise FoxError("DEPENDENCY_MISSING", tr("sandbox.the_light_sandbox_cannot_be_used_on", caps.get('reason')), hint=tr("sandbox.foxos_sandbox_check_or_use_full"), details=caps)
    return caps


def sandbox_run(ctx: Context, command: list, network: str = "on", read: list | None = None, write: list | None = None, home: str = "private",
                windows_mode: str = "restricted", max_processes: int | None = None, memory_mb: int | None = None,
                cwd: str | None = None, timeout: float = 600) -> dict:
    if not command:
        raise FoxError("USAGE", tr("common.missing_the_command_to_run"))
    argv = [str(c) for c in command]
    if len(argv) == 1 and " " in argv[0]:
        argv = ["cmd.exe", "/c", argv[0]] if sb.PLATFORM == "windows" else ["/bin/sh", "-c", argv[0]]
    _require()
    pol = _policy(ctx, network, read, write, home, windows_mode, max_processes, memory_mb)
    wd = str(ctx.resolve(cwd)) if cwd else pol.workspace
    t0 = time.time()
    try:
        r = sb.run(pol, argv, cwd=wd, timeout=timeout, profile=_profile(ctx))
    except subprocess.TimeoutExpired as e:
        raise FoxError("ERROR", tr("sandbox.timed_out_s", timeout, shlex.join(argv))) from e
    except OSError as e:
        raise FoxError("ERROR", tr("sandbox.sandbox_failed_to_start", e)) from e
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    return {"command": argv, "exit_code": r.returncode, "stdout": out[-200000:], "stderr": err[-50000:], "duration_s": round(time.time() - t0, 3),
            "sandbox": {"platform": sb.PLATFORM, "network": pol.network, "home": home}}


def sandbox_policy(ctx: Context, command: list | None = None, network: str = "on", read: list | None = None, write: list | None = None,
                   home: str = "private", windows_mode: str = "restricted") -> dict:
    """只计算不执行：展示将生效的规则（Linux：Landlock 规则；macOS：Seatbelt 配置；Windows：icacls 操作）。"""
    pol = sb.prepare(_policy(ctx, network, read, write, home, windows_mode, None, None), [str(c) for c in (command or [])], _profile(ctx))
    out = {"platform": sb.PLATFORM, "policy": pol.to_dict()}
    if sb.PLATFORM == "linux":
        from ..sandbox import linux
        out["landlock_rules"] = [{"path": p, "access": k} for p, k in linux.rules(pol.to_dict())]
        out["seccomp_denied"] = linux.DENY + ([] if pol.network else ["socket(AF_INET/AF_INET6/AF_PACKET)"]) + [tr("sandbox.clone_namespace_flags"), "clone3 → ENOSYS"]
    from ..sandbox import macos, windows
    out["seatbelt_profile"] = macos.profile(pol)
    out["windows_acl"] = windows.icacls_plan(pol, windows_mode, "<AppContainer SID>")
    return out


register_app("sandbox", tr("sandbox.light_sandbox"), tr("sandbox.process_level_sandbox_runs_programs"),
             limits=[tr("sandbox.linux_needs_landlock_enabled_in_the"),
                     tr("sandbox.windows_restricted_mode_only_limits"),
                     tr("sandbox.the_macos_and_windows")])
POLICY = [Param("network", "string", tr("sandbox.allow_network_access"), default="on", enum=["on", "off"]),
          Param("read", "array", tr("sandbox.extra_read_only_path_repeatable"), items={"type": "string"}, cli_repeat=True),
          Param("write", "array", tr("sandbox.extra_writable_path_repeatable"), items={"type": "string"}, cli_repeat=True),
          Param("home", "string", tr("sandbox.home_private_private_folder_read"), default="private", enum=["private", "read", "write"]),
          Param("windows_mode", "string", tr("sandbox.windows_restricted_restricted_token"), default="restricted", enum=["restricted", "appcontainer"])]
CMD = Param("command", "array", tr("common.command_and_arguments_after"), positional=True, items={"type": "string"}, metavar="CMD")
register(Command("sandbox", "check", tr("sandbox.light_sandbox_capabilities_on_this"), sandbox_check, examples=["foxos sandbox check --json"]))
register(Command("sandbox", "run", tr("sandbox.run_a_command_in_the_light_sandbox"), sandbox_run,
                 params=[CMD, *POLICY, Param("max_processes", "integer", tr("sandbox.maximum_processes_windows_job_object")), Param("memory_mb", "integer", tr("sandbox.memory_limit_mb_windows_job_object")),
                         Param("cwd", "string", tr("sandbox.working_directory_in_the_workspace")), Param("timeout", "number", tr("common.timeout_in_seconds"), default=600)],
                 examples=["foxos sandbox run --json -- python3 build.py", "foxos sandbox run --network off -- sh -c 'curl -sI https://example.com'"], permission="run"))
register(Command("sandbox", "policy", tr("sandbox.show_the_sandbox_rules_that_would"), sandbox_policy, params=[CMD, *POLICY], examples=["foxos sandbox policy --network off --json -- node agent.js"]))
