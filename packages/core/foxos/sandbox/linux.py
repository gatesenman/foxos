"""Linux 轻量隔离：Landlock + seccomp。

在启动器进程里（python -m foxos.sandbox exec）依次：
1. prctl(PR_SET_NO_NEW_PRIVS)：之后 setuid 程序不能提权
2. Landlock 规则集：文件系统只允许策略中的路径；不联网时禁止所有 TCP bind / connect（ABI ≥ 4）；
   禁止向沙箱外的进程发信号、禁止连接沙箱外的抽象 unix 套接字（ABI ≥ 6）
3. seccomp 过滤器：拒绝加载内核模块、kexec、ptrace、mount、命名空间、io_uring 等；不联网时拒绝创建 AF_INET / AF_INET6 / AF_PACKET 套接字
4. execve 目标程序（限制随进程树继承，无法解除）
"""

from __future__ import annotations

import ctypes
import ctypes.util
import errno
import json
import os
import platform
import struct
import subprocess
import sys
from pathlib import Path

ARCH = platform.machine()
libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
libc.syscall.restype = ctypes.c_long

SYS_LANDLOCK_CREATE_RULESET, SYS_LANDLOCK_ADD_RULE, SYS_LANDLOCK_RESTRICT_SELF = 444, 445, 446  # x86_64 与 aarch64 相同
LANDLOCK_CREATE_RULESET_VERSION = 1
LANDLOCK_RULE_PATH_BENEATH, LANDLOCK_RULE_NET_PORT = 1, 2
PR_SET_NO_NEW_PRIVS, PR_GET_SECCOMP, PR_SET_SECCOMP, SECCOMP_MODE_FILTER = 38, 21, 22, 2

# 文件系统访问权（include/uapi/linux/landlock.h）
FS = {"EXECUTE": 1 << 0, "WRITE_FILE": 1 << 1, "READ_FILE": 1 << 2, "READ_DIR": 1 << 3, "REMOVE_DIR": 1 << 4, "REMOVE_FILE": 1 << 5,
      "MAKE_CHAR": 1 << 6, "MAKE_DIR": 1 << 7, "MAKE_REG": 1 << 8, "MAKE_SOCK": 1 << 9, "MAKE_FIFO": 1 << 10, "MAKE_BLOCK": 1 << 11,
      "MAKE_SYM": 1 << 12, "REFER": 1 << 13, "TRUNCATE": 1 << 14, "IOCTL_DEV": 1 << 15}
NET_BIND_TCP, NET_CONNECT_TCP = 1, 2
SCOPE_ABSTRACT_UNIX_SOCKET, SCOPE_SIGNAL = 1, 2
FILE_ONLY = FS["EXECUTE"] | FS["WRITE_FILE"] | FS["READ_FILE"] | FS["TRUNCATE"] | FS["IOCTL_DEV"]  # 规则作用于普通文件时只能用这些权


def abi_version() -> int:
    v = libc.syscall(SYS_LANDLOCK_CREATE_RULESET, None, ctypes.c_size_t(0), ctypes.c_uint32(LANDLOCK_CREATE_RULESET_VERSION))
    return int(v) if v > 0 else 0


def fs_handled(abi: int) -> int:
    m = (1 << 13) - 1
    if abi >= 2:
        m |= FS["REFER"]
    if abi >= 3:
        m |= FS["TRUNCATE"]
    if abi >= 5:
        m |= FS["IOCTL_DEV"]
    return m


def access_sets(abi: int) -> dict:
    h = fs_handled(abi)
    ro = FS["EXECUTE"] | FS["READ_FILE"] | FS["READ_DIR"]
    dev = (ro | FS["WRITE_FILE"] | FS["TRUNCATE"] | FS["IOCTL_DEV"]) & h  # /dev/null、/dev/tty、/dev/pts/*
    return {"ro": ro, "rw": h, "dev": dev}


# ---- seccomp ----
NR = {
    "x86_64": {"kexec_load": 246, "kexec_file_load": 320, "init_module": 175, "finit_module": 313, "delete_module": 176, "reboot": 169, "swapon": 167,
               "swapoff": 168, "acct": 163, "settimeofday": 164, "clock_settime": 227, "adjtimex": 159, "bpf": 321, "perf_event_open": 298,
               "userfaultfd": 323, "keyctl": 250, "add_key": 248, "request_key": 249, "iopl": 172, "ioperm": 173, "open_by_handle_at": 304,
               "quotactl": 179, "syslog": 103, "personality": 135, "ptrace": 101, "process_vm_readv": 310, "process_vm_writev": 311,
               "mount": 165, "umount2": 166, "pivot_root": 155, "chroot": 161, "unshare": 272, "setns": 308, "fsopen": 430, "fsmount": 432,
               "move_mount": 429, "open_tree": 428, "io_uring_setup": 425, "io_uring_enter": 426, "io_uring_register": 427,
               "clone": 56, "clone3": 435, "socket": 41},
    "aarch64": {"kexec_load": 104, "kexec_file_load": 294, "init_module": 105, "finit_module": 273, "delete_module": 106, "reboot": 142, "swapon": 224,
                "swapoff": 225, "acct": 89, "settimeofday": 170, "clock_settime": 112, "adjtimex": 171, "bpf": 280, "perf_event_open": 241,
                "userfaultfd": 282, "keyctl": 219, "add_key": 217, "request_key": 218, "open_by_handle_at": 265, "quotactl": 60, "syslog": 116,
                "personality": 92, "ptrace": 117, "process_vm_readv": 270, "process_vm_writev": 271, "mount": 40, "umount2": 39,
                "pivot_root": 41, "chroot": 51, "unshare": 97, "setns": 268, "fsopen": 430, "fsmount": 432, "move_mount": 429, "open_tree": 428,
                "io_uring_setup": 425, "io_uring_enter": 426, "io_uring_register": 427, "clone": 220, "clone3": 435, "socket": 198},
}
AUDIT_ARCH = {"x86_64": 0xC000003E, "aarch64": 0xC00000B7}
DENY = ["kexec_load", "kexec_file_load", "init_module", "finit_module", "delete_module", "reboot", "swapon", "swapoff", "acct", "settimeofday",
        "clock_settime", "adjtimex", "bpf", "perf_event_open", "userfaultfd", "keyctl", "add_key", "request_key", "iopl", "ioperm",
        "open_by_handle_at", "quotactl", "syslog", "ptrace", "process_vm_readv", "process_vm_writev", "mount", "umount2", "pivot_root",
        "chroot", "unshare", "setns", "fsopen", "fsmount", "move_mount", "open_tree", "io_uring_setup", "io_uring_enter", "io_uring_register"]
CLONE_NS = 0x00020000 | 0x02000000 | 0x04000000 | 0x08000000 | 0x10000000 | 0x20000000 | 0x40000000 | 0x00000080  # NEWNS/CGROUP/UTS/IPC/USER/PID/NET/TIME
DENY_FAMILIES = [2, 10, 17]  # AF_INET, AF_INET6, AF_PACKET
RET_ALLOW, RET_ERRNO = 0x7FFF0000, 0x00050000
LD_W_ABS, JEQ_K, JGE_K, JSET_K, RET_K, ALU_AND_K = 0x20, 0x15, 0x35, 0x45, 0x06, 0x54
AF_INET, AF_INET6, AF_PACKET, SOCK_STREAM = 2, 10, 17, 1


class _Asm:
    """极小的 BPF 汇编器：支持标签跳转（跳转距离 ≤ 255 条指令）。"""

    def __init__(self):
        self.ins: list = []
        self.labels: dict = {}

    def stmt(self, code, k):
        self.ins.append((code, k, None, None))

    def jump(self, code, k, jt=None, jf=None):
        self.ins.append((code, k, jt, jf))

    def label(self, name):
        self.labels[name] = len(self.ins)

    def build(self) -> bytes:
        out = []
        for i, (code, k, jt, jf) in enumerate(self.ins):
            def off(t):
                if t is None:
                    return 0
                d = self.labels[t] - i - 1
                assert 0 <= d <= 255, (t, d)
                return d
            out.append(struct.pack("HBBI", code, off(jt), off(jf), k))
        return b"".join(out)


def seccomp_program(network: bool, arch: str = ARCH, tcp_ports: bool = False) -> bytes:
    """tcp_ports：不联网但允许连接个别 TCP 端口时，放行 AF_INET / AF_INET6 的 SOCK_STREAM 套接字（端口由 Landlock 限制），
    UDP / 原始套接字仍然拒绝。"""
    nr = NR[arch]
    a = _Asm()
    a.stmt(LD_W_ABS, 4)
    a.jump(JEQ_K, AUDIT_ARCH[arch], jf="deny")  # 其他 ABI（如 x86_64 上的 i386 / x32 入口）一律拒绝
    a.stmt(LD_W_ABS, 0)
    a.jump(JGE_K, 0x40000000, jt="deny")  # x32 系统调用号
    for name in DENY:
        if name in nr:  # iopl / ioperm 只有 x86
            a.jump(JEQ_K, nr[name], jt="deny")
    a.jump(JEQ_K, nr["clone3"], jt="enosys")  # clone3 的参数在结构体里无法检查：返回 ENOSYS，libc 会退回 clone
    a.jump(JEQ_K, nr["clone"], jt="clone")
    if not network:
        a.jump(JEQ_K, nr["socket"], jt="socket")
    a.stmt(RET_K, RET_ALLOW)
    a.label("clone")
    a.stmt(LD_W_ABS, 16)  # args[0] 低 32 位：flags
    a.jump(JSET_K, CLONE_NS, jt="deny")
    a.stmt(RET_K, RET_ALLOW)
    if not network:
        a.label("socket")
        a.stmt(LD_W_ABS, 16)  # args[0]：domain
        if tcp_ports:
            a.jump(JEQ_K, AF_PACKET, jt="deny")
            a.jump(JEQ_K, AF_INET, jt="inet")
            a.jump(JEQ_K, AF_INET6, jt="inet")
            a.stmt(RET_K, RET_ALLOW)
            a.label("inet")
            a.stmt(LD_W_ABS, 24)  # args[1]：type（低 4 位，去掉 SOCK_NONBLOCK / SOCK_CLOEXEC）
            a.stmt(ALU_AND_K, 0xF)
            a.jump(JEQ_K, SOCK_STREAM, jf="deny")
            a.stmt(RET_K, RET_ALLOW)
        else:
            for fam in DENY_FAMILIES:
                a.jump(JEQ_K, fam, jt="deny")
            a.stmt(RET_K, RET_ALLOW)
    a.label("deny")
    a.stmt(RET_K, RET_ERRNO | errno.EPERM)
    a.label("enosys")
    a.stmt(RET_K, RET_ERRNO | errno.ENOSYS)
    return a.build()


def seccomp_available() -> bool:
    return ARCH in NR and libc.prctl(PR_GET_SECCOMP, 0, 0, 0, 0) == 0


def capabilities() -> dict:
    abi = abi_version()
    sec = seccomp_available()
    return {
        "platform": "linux", "mechanism": "landlock+seccomp", "available": abi >= 1 and sec,
        "landlock_abi": abi, "seccomp": sec, "arch": ARCH,
        "filesystem": abi >= 1, "network": "tcp+socket" if abi >= 4 else ("socket" if sec else False),
        "signal_scope": abi >= 6, "abstract_unix_scope": abi >= 6, "truncate": abi >= 3, "ioctl_dev": abi >= 5,
        "reason": None if abi >= 1 and sec else ("内核没有启用 Landlock（需要 5.13+ 且 lsm= 包含 landlock）" if abi < 1 else "seccomp 不可用"),
    }


def _check(rc: int, what: str) -> int:
    if rc < 0:
        e = ctypes.get_errno()
        raise OSError(e, f"{what}: {os.strerror(e)}")
    return rc


def _add_path(rs: int, path: str, access: int) -> bool:
    try:
        fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
    except OSError:
        return False  # 不存在的路径跳过
    try:
        if not os.path.isdir(path):
            access &= FILE_ONLY
        if not access:
            return False
        attr = ctypes.create_string_buffer(struct.pack("=Qi", access, fd))
        _check(libc.syscall(SYS_LANDLOCK_ADD_RULE, ctypes.c_int(rs), ctypes.c_int(LANDLOCK_RULE_PATH_BENEATH), attr, ctypes.c_uint32(0)), f"landlock_add_rule {path}")
        return True
    finally:
        os.close(fd)


def rules(policy: dict) -> list[tuple[str, str]]:
    """策略 → (路径, ro|rw|dev) 列表（便于测试与展示）。"""
    from . import system_read_paths
    out = [(p, "ro") for p in system_read_paths()]
    out += [(p, "ro") for p in policy.get("read") or []]
    out += [("/dev", "dev"), ("/dev/shm", "rw")]
    out += [(p, "rw") for p in [policy["workspace"], policy.get("tmp"), policy.get("private_home"), *(policy.get("write") or [])] if p]
    return out


def apply(policy: dict) -> dict:
    """在当前进程上施加限制（不可撤销）。"""
    abi = abi_version()
    if abi < 1:
        raise OSError(errno.EOPNOTSUPP, "内核没有启用 Landlock")
    acc = access_sets(abi)
    network = bool(policy.get("network", True))
    handled_net = (NET_BIND_TCP | NET_CONNECT_TCP) if (abi >= 4 and not network) else 0
    scoped = (SCOPE_SIGNAL | SCOPE_ABSTRACT_UNIX_SOCKET) if abi >= 6 else 0
    size = 24 if abi >= 6 else (16 if abi >= 4 else 8)
    attr = ctypes.create_string_buffer(struct.pack("=QQQ", fs_handled(abi), handled_net, scoped)[:size], size)
    rs = _check(libc.syscall(SYS_LANDLOCK_CREATE_RULESET, attr, ctypes.c_size_t(size), ctypes.c_uint32(0)), "landlock_create_ruleset")
    added = []
    try:
        for path, kind in rules(policy):
            if _add_path(rs, path, acc[kind]):
                added.append([path, kind])
        ports = [int(x) for x in policy.get("connect_ports") or []] if handled_net else []
        for port in ports:
            na = ctypes.create_string_buffer(struct.pack("=QQ", NET_CONNECT_TCP, port))
            _check(libc.syscall(SYS_LANDLOCK_ADD_RULE, ctypes.c_int(rs), ctypes.c_int(LANDLOCK_RULE_NET_PORT), na, ctypes.c_uint32(0)), f"landlock_add_rule port {port}")
            added.append([f"tcp:{port}", "connect"])
        _check(libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "prctl(NO_NEW_PRIVS)")
        _check(libc.syscall(SYS_LANDLOCK_RESTRICT_SELF, ctypes.c_int(rs), ctypes.c_uint32(0)), "landlock_restrict_self")
    finally:
        os.close(rs)
    prog = seccomp_program(network, tcp_ports=bool(ports))
    buf = ctypes.create_string_buffer(prog)

    class SockFprog(ctypes.Structure):
        _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.c_void_p)]
    fp = SockFprog(len(prog) // 8, ctypes.addressof(buf))
    _check(libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(fp), 0, 0), "prctl(SECCOMP)")
    return {"landlock_abi": abi, "rules": added, "network": network, "scoped": bool(scoped), "seccomp_instructions": len(prog) // 8}


def exec_(policy: dict, argv: list[str], cwd: str | None = None) -> None:
    """启动器：施加限制后 execvpe（不返回）。"""
    if cwd:
        os.chdir(cwd)
    env = {k: v for k, v in os.environ.items() if k != "FOXOS_SANDBOX_LAUNCHER"}
    env.update(policy.get("env") or {})
    env["FOXOS_SANDBOX"] = "light"
    info = apply(policy)
    if os.environ.get("FOXOS_SANDBOX_VERBOSE"):
        sys.stderr.write(json.dumps({"sandbox": info}, ensure_ascii=False) + "\n")
    try:
        os.execvpe(argv[0], argv, env)
    except OSError as e:
        sys.stderr.write(f"foxos sandbox: 无法执行 {argv[0]}：{e.strerror}\n")
        os._exit(127)


def launcher(policy, argv: list[str], cwd: str | None = None) -> list[str]:
    core = str(Path(__file__).resolve().parents[2])
    code = f"import sys; sys.path.insert(0, {core!r}); from foxos.sandbox.__main__ import main; main()"
    pd = policy.to_dict() if hasattr(policy, "to_dict") else policy
    out = [sys.executable, "-c", code, "exec", "--policy", json.dumps(pd, ensure_ascii=False)]
    if cwd:
        out += ["--cwd", cwd]
    return out + ["--", *argv]


def run(policy, argv: list[str], cwd: str | None = None, timeout: float | None = None, capture: bool = True):
    cmd = launcher(policy, argv, cwd)
    return subprocess.run(cmd, capture_output=capture, timeout=timeout)
