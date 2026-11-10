"""foxos sandbox：轻量隔离级别（进程级沙箱）。

与 foxos env（完全隔离：独立发行版 / 虚拟机）互补：直接用宿主上的程序与工具链，零启动开销，
但只能读写工作空间（与声明的路径），可选禁止联网。实现见 foxos/sandbox/。
"""

from __future__ import annotations

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
        raise FoxError("DEPENDENCY_MISSING", f"本机不能使用轻量隔离：{caps.get('reason')}", hint="foxos sandbox check；或改用完全隔离 foxos env", details=caps)
    return caps


def sandbox_run(ctx: Context, command: list, network: str = "on", read: list | None = None, write: list | None = None, home: str = "private",
                windows_mode: str = "restricted", max_processes: int | None = None, memory_mb: int | None = None,
                cwd: str | None = None, timeout: float = 600) -> dict:
    if not command:
        raise FoxError("USAGE", "缺少要执行的命令")
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
        raise FoxError("ERROR", f"超时（{timeout} 秒）：{shlex.join(argv)}") from e
    except OSError as e:
        raise FoxError("ERROR", f"沙箱启动失败：{e}") from e
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
        out["seccomp_denied"] = linux.DENY + ([] if pol.network else ["socket(AF_INET/AF_INET6/AF_PACKET)"]) + ["clone(命名空间标志)", "clone3 → ENOSYS"]
    from ..sandbox import macos, windows
    out["seatbelt_profile"] = macos.profile(pol)
    out["windows_acl"] = windows.icacls_plan(pol, windows_mode, "<AppContainer SID>")
    return out


register_app("sandbox", "轻量隔离", "进程级沙箱：直接运行宿主上的程序，只能读写工作空间，可选禁止联网（Linux Landlock + seccomp、macOS Seatbelt、Windows 受限令牌 / AppContainer + 作业对象）。",
             limits=["Linux 需要内核启用 Landlock（5.13+）；TCP 网络限制需 ABI 4（6.7+），信号隔离需 ABI 6（6.12+）",
                     "Windows restricted 模式只限制写入（读取不受限）；appcontainer 模式读写与网络都受限，但很多程序在 AppContainer 中无法运行",
                     "macOS 与 Windows 实现尚未在实机上验证"])
POLICY = [Param("network", "string", "是否允许联网", default="on", enum=["on", "off"]),
          Param("read", "array", "额外只读路径（可重复）", items={"type": "string"}, cli_repeat=True),
          Param("write", "array", "额外可写路径（可重复）", items={"type": "string"}, cli_repeat=True),
          Param("home", "string", "HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写", default="private", enum=["private", "read", "write"]),
          Param("windows_mode", "string", "Windows：restricted 受限令牌 / appcontainer", default="restricted", enum=["restricted", "appcontainer"])]
CMD = Param("command", "array", "命令及参数（放在 -- 之后）", positional=True, items={"type": "string"}, metavar="CMD")
register(Command("sandbox", "check", "本机可用的轻量隔离能力（机制、Landlock ABI、网络 / 信号隔离）", sandbox_check, examples=["foxos sandbox check --json"]))
register(Command("sandbox", "run", "在轻量沙箱中运行命令：只能读写工作空间，可选禁止联网", sandbox_run,
                 params=[CMD, *POLICY, Param("max_processes", "integer", "最多进程数（Windows 作业对象）"), Param("memory_mb", "integer", "内存上限 MB（Windows 作业对象）"),
                         Param("cwd", "string", "工作目录（工作空间内）"), Param("timeout", "number", "超时秒数", default=600)],
                 examples=["foxos sandbox run --json -- python3 build.py", "foxos sandbox run --network off -- sh -c 'curl -sI https://example.com'"], permission="run"))
register(Command("sandbox", "policy", "显示将生效的沙箱规则（不执行）", sandbox_policy, params=[CMD, *POLICY], examples=["foxos sandbox policy --network off --json -- node agent.js"]))
