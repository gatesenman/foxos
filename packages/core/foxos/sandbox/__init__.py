"""轻量隔离级别（进程级沙箱）：不建独立的根文件系统，直接在宿主上运行程序，但只允许它

- 读写工作空间（以及额外声明的可写目录、私有临时目录、私有 HOME）
- 读取系统目录与程序自身所在目录（只读）
- 按策略决定是否联网
- 不能向沙箱外的进程发信号（Linux：Landlock scope；Windows：作业对象 + 受限令牌）

各平台的实现：
  Linux   Landlock（文件系统、TCP、信号 / 抽象 unix 套接字作用域）+ seccomp（拒绝危险系统调用与非本地套接字）
  macOS   Seatbelt（sandbox-exec 配置文件，由 macos.profile() 生成）
  Windows 受限令牌（去掉管理员组与特权、低完整性级别）或 AppContainer，加作业对象（随父进程结束、进程数 / 内存上限、界面限制）

与“完全隔离”（foxos env：独立发行版 / 虚拟机）相比，轻量级别启动零开销、直接使用宿主上的工具链，
代价是隔离边界由宿主内核的安全机制提供，且不同平台能限制的范围不同（见 capabilities()）。
"""

from __future__ import annotations

from foxos.i18n import tr
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

PLATFORM = "linux" if sys.platform.startswith("linux") else ("windows" if os.name == "nt" else ("macos" if sys.platform == "darwin" else sys.platform))


@dataclass
class Policy:
    workspace: str
    read: list[str] = field(default_factory=list)  # 额外只读目录 / 文件
    write: list[str] = field(default_factory=list)  # 额外可写目录 / 文件
    network: bool = True
    connect_ports: list[int] = field(default_factory=list)  # 不联网时仍允许连接的 TCP 端口（如宿主上的 foxos MCP HTTP 服务器）
    home: str = "private"  # private：私有 HOME（沙箱目录下）；read：真实 HOME 只读；write：真实 HOME 可写
    tmp: str | None = None  # 私有临时目录（可写），缺省由 prepare() 创建
    private_home: str | None = None
    max_processes: int | None = None
    memory_mb: int | None = None
    windows_mode: str = "restricted"  # restricted | appcontainer
    env: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Policy":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def system_read_paths() -> list[str]:
    """程序正常运行所需的只读系统路径（按平台）。"""
    if PLATFORM == "linux":
        cands = ["/usr", "/bin", "/sbin", "/lib", "/lib32", "/lib64", "/libx32", "/etc", "/opt", "/proc", "/sys", "/run/systemd/resolve",
                 "/var/lib/ca-certificates", "/nix/store", "/snap"]
    elif PLATFORM == "macos":
        cands = ["/usr", "/bin", "/sbin", "/System", "/Library", "/Applications", "/opt/homebrew", "/usr/local", "/private/etc", "/etc",
                 "/private/var/db/timezone", "/var/db/timezone", "/dev"]
    else:
        root = os.environ.get("SystemRoot", r"C:\Windows")
        cands = [root, os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
    return [p for p in cands if p and os.path.exists(p)]


def program_paths(argv0: str) -> list[str]:
    """要运行的程序所在的安装目录（只读）：可执行文件真实路径的上一级目录。
    例：~/.local/share/fnm/node-v22/bin/node → ~/.local/share/fnm/node-v22；脚本解释器（#!）也一并加入。"""
    out = []
    exe = shutil.which(argv0) or argv0
    if not os.path.exists(exe):
        return out
    real = os.path.realpath(exe)

    def install_dir(f: str) -> str:
        d = os.path.dirname(f)
        return os.path.dirname(d) if os.path.basename(d) in ("bin", "Scripts", ".bin") else d
    out.append(install_dir(real))
    if os.path.abspath(exe) != real:
        out.append(install_dir(os.path.abspath(exe)))  # 例如虚拟环境：.venv/bin/python → /usr/bin/python3.12，pyvenv.cfg 在 .venv
    try:
        with open(real, "rb") as f:
            head = f.read(256)
        if head.startswith(b"#!"):
            line = head[2:].split(b"\n")[0].decode("utf-8", "replace").split()
            interp = line[1] if line and line[0].endswith("/env") and len(line) > 1 else (line[0] if line else None)
            if interp and interp != argv0:
                out += program_paths(interp)
    except OSError:
        pass
    return list(dict.fromkeys(out))


def sandbox_home() -> Path:
    from .. import desktop_client
    return desktop_client.foxos_home() / "sandbox"


def prepare(policy: Policy, argv: list[str], profile: str = "default") -> Policy:
    """补全策略：私有 tmp / HOME、程序目录、环境变量。返回新的 Policy（不修改入参）。"""
    p = Policy.from_dict(policy.to_dict())
    base = sandbox_home() / profile
    if not p.tmp:
        p.tmp = str(base / "tmp")
    Path(p.tmp).mkdir(parents=True, exist_ok=True)
    env = dict(p.env)
    env.setdefault("TMPDIR", p.tmp)
    if PLATFORM == "windows":
        env.setdefault("TEMP", p.tmp)
        env.setdefault("TMP", p.tmp)
    real_home = str(Path.home())
    if p.home == "private":
        p.private_home = p.private_home or str(base / "home")
        Path(p.private_home).mkdir(parents=True, exist_ok=True)
        env.setdefault("HOME", p.private_home)
        if PLATFORM == "windows":
            env.setdefault("USERPROFILE", p.private_home)
    elif p.home == "read":
        p.read.append(real_home)
    elif p.home == "write":
        p.write.append(real_home)
    if argv:
        p.read += program_paths(argv[0])
    p.read = list(dict.fromkeys(os.path.abspath(x) for x in p.read if x))
    p.write = list(dict.fromkeys(os.path.abspath(x) for x in p.write if x))
    p.env = env
    return p


def capabilities() -> dict:
    """本机能提供的轻量隔离能力（不同平台、内核版本不同）。"""
    if PLATFORM == "linux":
        from . import linux
        return linux.capabilities()
    if PLATFORM == "macos":
        from . import macos
        return macos.capabilities()
    if PLATFORM == "windows":
        from . import windows
        return windows.capabilities()
    return {"platform": PLATFORM, "available": False, "reason": tr("sandbox.unsupported_platform")}


def run(policy: Policy, argv: list[str], cwd: str | None = None, timeout: float | None = None, capture: bool = True, profile: str = "default"):
    """在沙箱中运行 argv，返回 subprocess.CompletedProcess（capture=False 时 stdout/stderr 为 None）。"""
    p = prepare(policy, argv, profile)
    cwd = cwd or p.workspace
    if PLATFORM == "linux":
        from . import linux
        return linux.run(p, argv, cwd=cwd, timeout=timeout, capture=capture)
    if PLATFORM == "macos":
        from . import macos
        return macos.run(p, argv, cwd=cwd, timeout=timeout, capture=capture)
    if PLATFORM == "windows":
        from . import windows
        return windows.run(p, argv, cwd=cwd, timeout=timeout, capture=capture)
    raise OSError(tr("sandbox.the_light_sandbox_does_not_support", PLATFORM))


def launcher_argv(policy: Policy, argv: list[str], profile: str = "default", python: str | None = None) -> list[str]:
    """给其他程序（如桌面端启动智能体）用的命令行：python -m foxos.sandbox exec --policy JSON -- argv。"""
    import json
    p = prepare(policy, argv, profile)
    return [python or sys.executable, "-m", "foxos.sandbox", "exec", "--policy", json.dumps(p.to_dict(), ensure_ascii=False), "--", *argv]
