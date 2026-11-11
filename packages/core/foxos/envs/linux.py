"""狐狸OS 自研 Linux 环境运行时（不依赖 Docker / Podman / LXC 等）。

只用内核原生机制：用户命名空间（无特权运行）+ mount / pid / uts / ipc / 可选 net 命名空间、
overlayfs（镜像只读层 + 环境可写层）、pivot_root、seccomp 系统调用过滤、cgroup v2（可写时）或 rlimit 限制。

用法（由 foxos env 命令调用）：
  python -m foxos.envs.linux supervise ENV_DIR      # 启动环境的 init（后台）
  python -m foxos.envs.linux exec ENV_DIR -- CMD…   # 在运行中的环境里执行命令
"""

from __future__ import annotations

from foxos.i18n import tr
import ctypes
import fcntl  # noqa: F401  pivot_root 之后无法再导入扩展模块，提前导入
import ctypes.util
import errno
import json
import os
import platform
import resource
import signal
import socket
import struct
import sys
import time
from pathlib import Path

libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
libc.mount.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]
libc.umount2.argtypes = [ctypes.c_char_p, ctypes.c_int]

MS_RDONLY, MS_NOSUID, MS_NODEV, MS_NOEXEC, MS_REMOUNT, MS_BIND, MS_REC, MS_PRIVATE = 1, 2, 4, 8, 32, 4096, 16384, 1 << 18
MNT_DETACH = 2
ARCH = platform.machine()
SYS_PIVOT_ROOT = {"x86_64": 155, "aarch64": 217}.get(ARCH)
PR_SET_NO_NEW_PRIVS, PR_SET_SECCOMP, SECCOMP_MODE_FILTER = 38, 22, 2

# seccomp：拒绝对容器无意义且危险的系统调用（返回 EPERM）
SECCOMP_DENY = {
    "x86_64": {"kexec_load": 246, "kexec_file_load": 320, "init_module": 175, "finit_module": 313, "delete_module": 176, "reboot": 169,
               "swapon": 167, "swapoff": 168, "acct": 163, "settimeofday": 164, "clock_settime": 227, "adjtimex": 159, "bpf": 321,
               "perf_event_open": 298, "userfaultfd": 323, "keyctl": 250, "add_key": 248, "request_key": 249, "iopl": 172, "ioperm": 173,
               "open_by_handle_at": 304, "lookup_dcookie": 212, "quotactl": 179, "syslog": 103, "personality": 135},
    "aarch64": {"kexec_load": 104, "kexec_file_load": 294, "init_module": 105, "finit_module": 273, "delete_module": 106, "reboot": 142,
                "swapon": 224, "swapoff": 225, "acct": 89, "settimeofday": 170, "clock_settime": 112, "adjtimex": 171, "bpf": 280,
                "perf_event_open": 241, "userfaultfd": 282, "keyctl": 219, "add_key": 217, "request_key": 218,
                "open_by_handle_at": 265, "lookup_dcookie": 18, "quotactl": 60, "syslog": 116, "personality": 92},
}
AUDIT_ARCH = {"x86_64": 0xC000003E, "aarch64": 0xC00000B7}


def _check(rc: int, what: str) -> None:
    if rc != 0:
        e = ctypes.get_errno()
        raise OSError(e, f"{what}: {os.strerror(e)}")


def mount(src: str | None, target: str, fstype: str | None = None, flags: int = 0, data: str | None = None) -> None:
    _check(libc.mount(src.encode() if src else None, target.encode(), fstype.encode() if fstype else None, flags, data.encode() if data else None),
           f"mount {fstype or ''} {src} → {target}")


def seccomp_filter() -> bytes:
    deny = SECCOMP_DENY.get(ARCH, {})
    BPF_LD_W_ABS, BPF_JEQ_K, BPF_RET_K = 0x20, 0x15, 0x06
    ins = []
    def stmt(code, k): ins.append(struct.pack("HBBI", code, 0, 0, k))
    def jump(code, k, jt, jf): ins.append(struct.pack("HBBI", code, jt, jf, k))
    stmt(BPF_LD_W_ABS, 4)  # seccomp_data.arch
    jump(BPF_JEQ_K, AUDIT_ARCH[ARCH], 1, 0)
    stmt(BPF_RET_K, 0x7FFF0000)  # 其他架构：放行（不在这里拦截）
    stmt(BPF_LD_W_ABS, 0)  # seccomp_data.nr
    nrs = sorted(deny.values())
    for i, nr in enumerate(nrs):
        jump(BPF_JEQ_K, nr, len(nrs) - i, 0)
    stmt(BPF_RET_K, 0x7FFF0000)  # SECCOMP_RET_ALLOW
    stmt(BPF_RET_K, 0x00050000 | errno.EPERM)  # SECCOMP_RET_ERRNO
    return b"".join(ins)


def apply_seccomp() -> bool:
    if ARCH not in SECCOMP_DENY:
        return False
    prog = seccomp_filter()
    buf = ctypes.create_string_buffer(prog)
    class SockFprog(ctypes.Structure):
        _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.c_void_p)]
    fp = SockFprog(len(prog) // 8, ctypes.addressof(buf))
    _check(libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "prctl(NO_NEW_PRIVS)")
    _check(libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(fp), 0, 0), "prctl(SECCOMP)")
    return True


def apply_rlimits(limits: dict) -> None:
    if limits.get("memory_mb"):
        b = int(limits["memory_mb"]) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (b, b))
    if limits.get("pids"):
        n = int(limits["pids"])
        resource.setrlimit(resource.RLIMIT_NPROC, (n, n))
    if limits.get("nofile"):
        n = int(limits["nofile"])
        resource.setrlimit(resource.RLIMIT_NOFILE, (n, n))


def write_maps(uid: int, gid: int, pid: str = "self") -> None:
    for name, text in (("uid_map", f"0 {uid} 1"), ("setgroups", "deny"), ("gid_map", f"0 {gid} 1")):
        # 必须一次 write 写入，且不能截断（不能用普通的文本写入）
        fd = os.open(f"/proc/{pid}/{name}", os.O_WRONLY)
        try:
            os.write(fd, text.encode())
        finally:
            os.close(fd)


def load(env_dir: Path) -> dict:
    return json.loads((env_dir / "env.json").read_text(encoding="utf-8"))


def _bind_dev(root: Path) -> None:
    dev = root / "dev"
    dev.mkdir(exist_ok=True)
    mount("tmpfs", str(dev), "tmpfs", MS_NOSUID, "mode=755,size=64k")
    for n in ("null", "zero", "full", "random", "urandom", "tty"):
        t = dev / n
        t.touch()
        mount(f"/dev/{n}", str(t), None, MS_BIND)
    (dev / "pts").mkdir()
    try:
        mount("devpts", str(dev / "pts"), "devpts", MS_NOSUID | MS_NOEXEC, "newinstance,ptmxmode=0666,mode=620")
        os.symlink("pts/ptmx", dev / "ptmx")
    except OSError:
        pass
    (dev / "shm").mkdir()
    mount("tmpfs", str(dev / "shm"), "tmpfs", MS_NOSUID | MS_NODEV, "mode=1777,size=64m")
    for a, b in (("/proc/self/fd", "fd"), ("/proc/self/fd/0", "stdin"), ("/proc/self/fd/1", "stdout"), ("/proc/self/fd/2", "stderr")):
        os.symlink(a, dev / b)


def setup_root(env_dir: Path, cfg: dict) -> Path:
    """在新的 mount 命名空间里组装根文件系统并 pivot_root。返回 None（已切换根）。"""
    mount(None, "/", None, MS_REC | MS_PRIVATE)
    lower = Path(cfg["lower"])
    upper, work, merged = env_dir / "upper", env_dir / "work", env_dir / "merged"
    for d in (upper, work, merged):
        d.mkdir(exist_ok=True)
    mount("overlay", str(merged), "overlay", 0, f"lowerdir={lower},upperdir={upper},workdir={work},userxattr")
    root = merged
    for d in ("proc", "sys", "tmp", "run", "workspace", "etc", ".oldroot"):
        (root / d).mkdir(exist_ok=True)
    mount("proc", str(root / "proc"), "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC)
    try:
        if cfg.get("network") == "none":
            mount("sysfs", str(root / "sys"), "sysfs", MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC)
        else:
            mount("/sys", str(root / "sys"), None, MS_BIND | MS_REC)
    except OSError:
        pass
    _bind_dev(root)
    mount("tmpfs", str(root / "tmp"), "tmpfs", MS_NOSUID | MS_NODEV, "mode=1777")
    mount("tmpfs", str(root / "run"), "tmpfs", MS_NOSUID | MS_NODEV, "mode=755")
    if cfg.get("network", "host") == "host" and Path("/etc/resolv.conf").exists():
        rc = root / "etc" / "resolv.conf"
        if rc.is_symlink():
            rc.unlink()
        rc.touch()
        mount(os.path.realpath("/etc/resolv.conf"), str(rc), None, MS_BIND)
    ws = cfg.get("workspace") or {}
    if ws.get("mode", "rw") != "none" and ws.get("path"):
        mount(ws["path"], str(root / "workspace"), None, MS_BIND | MS_REC)
        if ws.get("mode") == "ro":
            mount(None, str(root / "workspace"), None, MS_REMOUNT | MS_BIND | MS_RDONLY | MS_REC)
    for m in [*cfg.get("mounts", []), *cfg.get("system_mounts", [])]:
        if not Path(m["source"]).exists():
            continue
        t = root / m["target"].lstrip("/")
        if Path(m["source"]).is_dir():
            t.mkdir(parents=True, exist_ok=True)
        else:
            t.parent.mkdir(parents=True, exist_ok=True)
            t.touch()
        mount(m["source"], str(t), None, MS_BIND | MS_REC)
        if m.get("readonly"):
            mount(None, str(t), None, MS_REMOUNT | MS_BIND | MS_RDONLY | MS_REC)
    old = root / ".oldroot"
    _check(libc.syscall(SYS_PIVOT_ROOT, str(root).encode(), str(old).encode()), "pivot_root")
    os.chdir("/")
    _check(libc.umount2(b"/.oldroot", MNT_DETACH), "umount oldroot")
    os.rmdir("/.oldroot")
    return Path("/")


CONTAINER_ENV = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/root", "TERM": "xterm-256color", "LANG": "C.UTF-8", "FOXOS_ENV": "1"}


def cgroup_setup(name: str, limits: dict) -> str:
    """尝试为环境建立 cgroup v2 子组（需要当前 cgroup 已委派给本用户）。返回状态说明。

    成功时把监督进程移入子组，之后环境内所有进程都在其中，限制按整个环境计算。
    失败（例如 cgroup 目录属于 root）时返回原因，调用方回退到 rlimit。
    """
    try:
        line = next(l for l in Path("/proc/self/cgroup").read_text().splitlines() if l.startswith("0::"))
    except (OSError, StopIteration):
        return tr("envs.linux.unavailable_not_cgroup_v2")
    base = Path("/sys/fs/cgroup") / line[3:].lstrip("/")
    if not os.access(base, os.W_OK):
        return tr("envs.linux.unavailable_is_not_writable_cgroup", base)
    want = [c for c, k in (("memory", "memory_mb"), ("pids", "pids"), ("cpu", "cpus")) if limits.get(k)]
    try:
        avail = (base / "cgroup.controllers").read_text().split()
        sub = (base / "cgroup.subtree_control").read_text().split()
        for c in want:
            if c in avail and c not in sub:
                (base / "cgroup.subtree_control").write_text(f"+{c}")
        cg = base / f"foxos-{name}"
        cg.mkdir(exist_ok=True)
        if limits.get("memory_mb") and (cg / "memory.max").exists():
            (cg / "memory.max").write_text(str(int(limits["memory_mb"]) * 1024 * 1024))
        if limits.get("pids") and (cg / "pids.max").exists():
            (cg / "pids.max").write_text(str(int(limits["pids"])))
        if limits.get("cpus") and (cg / "cpu.max").exists():
            (cg / "cpu.max").write_text(f"{int(float(limits['cpus']) * 100000)} 100000")
        (cg / "cgroup.procs").write_text(str(os.getpid()))
        return f"on: {cg}"
    except OSError as e:
        return f"unavailable: {e}"


def supervise(env_dir: Path) -> int:
    cfg = load(env_dir)
    run = env_dir / "run"
    run.mkdir(exist_ok=True)
    (run / "cgroup").write_text(cgroup_setup(cfg["name"], cfg.get("limits") or {}))
    uid, gid = os.getuid(), os.getgid()  # 必须在 unshare 之前读取
    os.unshare(os.CLONE_NEWUSER)
    write_maps(uid, gid)
    ns = os.CLONE_NEWPID | os.CLONE_NEWUTS | os.CLONE_NEWIPC  # mount 命名空间由 1 号进程自己创建，监督进程保持原来的根
    if cfg.get("network") == "none":
        ns |= os.CLONE_NEWNET
    os.unshare(ns)
    r, w = os.pipe()
    pid = os.fork()
    if pid:
        os.close(w)
        (run / "init.pid").write_text(str(pid))
        status = os.read(r, 4096).decode() or tr("envs.linux.init_failed_to_start")
        (run / "status").write_text(status)
        _, st = os.waitpid(pid, 0)
        for f in ("init.pid",):
            try:
                (run / f).unlink()
            except FileNotFoundError:
                pass
        (run / "status").write_text(f"stopped {os.waitstatus_to_exitcode(st)}")
        return 0
    # ---- 环境内的 1 号进程
    os.close(r)
    try:
        os.unshare(os.CLONE_NEWNS)
        socket.sethostname(cfg.get("hostname") or cfg["name"])
        setup_root(env_dir, cfg)
        if cfg.get("network") == "none":
            _lo_up()
        apply_rlimits(cfg.get("limits") or {})
        sec = apply_seccomp()
        os.write(w, f"running seccomp={'on' if sec else 'off'}".encode())
    except Exception as e:  # noqa: BLE001
        os.write(w, f"error {type(e).__name__}: {e}".encode())
        os._exit(1)
    os.close(w)
    stop = {"flag": False}
    def term(*_):
        stop["flag"] = True
        for p in _children():
            try:
                os.kill(p, signal.SIGTERM)
            except ProcessLookupError:
                pass
    signal.signal(signal.SIGTERM, term)
    signal.signal(signal.SIGINT, term)
    boot = cfg.get("boot_command")
    if boot:
        if os.fork() == 0:
            os.execvpe(boot[0], boot, CONTAINER_ENV)
    while True:
        try:
            os.wait()
        except ChildProcessError:
            if stop["flag"]:
                os._exit(0)
            signal.pause() if not stop["flag"] else os._exit(0)
        except InterruptedError:
            pass
        if stop["flag"] and not _children():
            os._exit(0)


def _children() -> list[int]:
    out = []
    for d in os.listdir("/proc"):
        if d.isdigit() and d != "1":
            out.append(int(d))
    return out


def _lo_up() -> None:

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifr = struct.pack("16sH14s", b"lo", 0, b"")
    flags = struct.unpack("16sH14s", fcntl.ioctl(s, 0x8913, ifr))[1]
    fcntl.ioctl(s, 0x8914, struct.pack("16sH14s", b"lo", flags | 1, b""))
    s.close()


def init_pid(env_dir: Path) -> int | None:
    try:
        pid = int((env_dir / "run" / "init.pid").read_text())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


def exec_in(env_dir: Path, argv: list[str], cwd: str = "/", env: dict | None = None, user_env: bool = True) -> int:
    pid = init_pid(env_dir)
    if not pid:
        print(tr("envs.linux.the_environment_is_not_running"), file=sys.stderr)
        return 6
    cfg = load(env_dir)
    fds = {}
    for n in ("user", "mnt", "pid", "uts", "ipc", "net"):
        if n == "net" and cfg.get("network") != "none":
            continue
        fds[n] = os.open(f"/proc/{pid}/ns/{n}", os.O_RDONLY)
    os.setns(fds.pop("user"), os.CLONE_NEWUSER)
    for n, fd in fds.items():
        os.setns(fd, 0)
        os.close(fd)
    child = os.fork()
    if child == 0:
        try:
            os.chdir(cwd if os.path.isdir(cwd) else "/")
            apply_rlimits(cfg.get("limits") or {})
            apply_seccomp()
            os.execvpe(argv[0], argv, {**CONTAINER_ENV, **(env or {})})
        except OSError as e:
            print(tr("envs.linux.cannot_run", argv[0], e.strerror), file=sys.stderr)
            os._exit(127)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    _, st = os.waitpid(child, 0)
    return os.waitstatus_to_exitcode(st)


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "supervise":
        return supervise(Path(argv[1]))
    if len(argv) >= 2 and argv[0] == "exec":
        rest = argv[2:]
        cwd = "/"
        envs = {}
        while rest and rest[0] != "--":
            if rest[0] == "--cwd":
                cwd = rest[1]; rest = rest[2:]
            elif rest[0] == "--env":
                k, _, v = rest[1].partition("="); envs[k] = v; rest = rest[2:]
            else:
                break
        if rest and rest[0] == "--":
            rest = rest[1:]
        return exec_in(Path(argv[1]), rest or ["/bin/sh"], cwd=cwd, env=envs)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
