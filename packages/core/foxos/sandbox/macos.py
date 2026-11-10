"""macOS 轻量隔离：Seatbelt（sandbox-exec 与系统沙箱同一机制）。

profile() 根据策略生成 SBPL 配置文件：
- 默认拒绝（deny default）
- 允许读取系统目录、程序目录、工作空间与声明的只读路径；任意路径的元数据（stat / 路径解析需要）
- 只允许写工作空间、私有临时目录 / HOME 与声明的可写路径，以及 /dev/null、/dev/tty 等设备
- 不联网时只允许本机 unix 套接字
- 进程只能向同一沙箱内的进程发信号
注：Apple 已将 sandbox-exec 标记为不推荐使用，但它仍随系统提供并被广泛使用（同一内核机制）；尚未在 Mac 实机上验证。
"""

from __future__ import annotations

import os
import shutil
import subprocess

SANDBOX_EXEC = "/usr/bin/sandbox-exec"


def _q(path: str) -> str:
    """SBPL 字符串字面量（转义反斜杠与双引号）。路径取真实路径：/tmp → /private/tmp。"""
    p = os.path.realpath(path)
    return '"' + p.replace("\\", "\\\\").replace('"', '\\"') + '"'


def profile(policy) -> str:
    from . import system_read_paths
    pd = policy.to_dict() if hasattr(policy, "to_dict") else policy
    reads = [*system_read_paths(), *(pd.get("read") or [])]
    writes = [p for p in [pd["workspace"], pd.get("tmp"), pd.get("private_home"), *(pd.get("write") or [])] if p]
    lines = [
        "(version 1)",
        "(deny default)",
        "(allow process-fork)",
        "(allow process-exec)",
        "(allow signal (target same-sandbox))",
        "(allow sysctl-read)",
        "(allow mach-lookup)",
        "(allow ipc-posix-shm)",
        "(allow ipc-posix-sem)",
        "(allow iokit-open)",
        "(allow user-preference-read)",
        "(allow file-read-metadata)",
        '(allow file-read* (literal "/"))',
        "(allow file-read* file-write-data (literal \"/dev/null\") (literal \"/dev/zero\") (literal \"/dev/tty\") (regex #\"^/dev/ttys[0-9]+$\") (literal \"/dev/ptmx\"))",
        '(allow file-read* (literal "/dev/random") (literal "/dev/urandom") (literal "/dev/dtracehelper"))',
        "(allow file-ioctl (regex #\"^/dev/(tty|ttys[0-9]+|ptmx)$\"))",
        "(allow pseudo-tty)",
    ]
    if reads:
        lines.append("(allow file-read* " + " ".join(f"(subpath {_q(p)})" for p in reads) + ")")
    lines.append("(allow file-read* file-write* " + " ".join(f"(subpath {_q(p)})" for p in writes) + ")")
    if pd.get("network", True):
        lines.append("(allow network*)")
        lines.append("(allow system-socket)")
    else:
        lines.append('(allow network* (local unix-socket) (remote unix-socket))')
        lines.append("(allow system-socket (socket-domain AF_UNIX))")
    return "\n".join(lines) + "\n"


def capabilities() -> dict:
    ok = os.path.exists(SANDBOX_EXEC)
    return {"platform": "macos", "mechanism": "seatbelt", "available": ok, "filesystem": ok, "network": ok, "signal_scope": ok,
            "verified_on_hardware": False, "reason": None if ok else "找不到 /usr/bin/sandbox-exec"}


def command(policy, argv: list[str]) -> list[str]:
    return [SANDBOX_EXEC, "-p", profile(policy), *argv]


def run(policy, argv: list[str], cwd: str | None = None, timeout: float | None = None, capture: bool = True):
    if not os.path.exists(SANDBOX_EXEC):
        raise OSError(2, "找不到 /usr/bin/sandbox-exec")
    pd = policy.to_dict() if hasattr(policy, "to_dict") else policy
    env = {**os.environ, **(pd.get("env") or {}), "FOXOS_SANDBOX": "light"}
    exe = shutil.which(argv[0], path=env.get("PATH")) or argv[0]
    return subprocess.run(command(policy, [exe, *argv[1:]]), cwd=cwd or pd["workspace"], env=env, capture_output=capture, timeout=timeout)
