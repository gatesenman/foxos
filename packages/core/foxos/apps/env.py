"""狐狸OS 环境（foxos env）：自研的隔离环境层。

Linux：自研运行时（用户 / mount / pid / uts / ipc / 可选 net 命名空间、overlayfs、pivot_root、seccomp、cgroup v2 或 rlimit），见 foxos/envs/linux.py。
Windows：直接驱动系统自带的 WSL2（wsl.exe --import / --export / --terminate），见 foxos/envs/wsl.py。
macOS：Apple Virtualization.framework（Swift 小助手 foxos-vz），见 foxos/envs/macos.py。
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import desktop_client
from ..envs import images
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app

IS_LINUX = sys.platform.startswith("linux")
BACKEND = "linux-ns" if IS_LINUX else ("wsl2" if os.name == "nt" else "macos-vz")


def home() -> Path:
    return desktop_client.foxos_home() / "envs"


def images_dir() -> Path:
    d = home() / "images"
    d.mkdir(parents=True, exist_ok=True)
    return d


def env_dir(name: str) -> Path:
    return home() / "instances" / name


def _valid(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", name or ""):
        raise FoxError("USAGE", "环境名只能包含小写字母、数字和连字符（最长 41 个字符）")
    return name


def _cfg(name: str) -> dict:
    f = env_dir(_valid(name)) / "env.json"
    if not f.exists():
        raise FoxError("NOT_FOUND", f"没有名为 {name} 的环境", hint="foxos env list")
    return json.loads(f.read_text(encoding="utf-8"))


def _save(cfg: dict) -> None:
    d = env_dir(cfg["name"])
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / "env.json.tmp"
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, d / "env.json")


def _log(name: str, text: str) -> None:
    d = env_dir(name) / "logs"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "env.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {text}\n")


def _need_linux():
    if not IS_LINUX:
        raise FoxError("DEPENDENCY_MISSING", f"本机后端为 {BACKEND}；该命令目前由 Linux 后端实现", hint="Windows 使用 foxos env 的 WSL2 后端（见 docs/environments.md）")


def _linux():
    from ..envs import linux
    return linux


def _pid(name: str) -> int | None:
    return _linux().init_pid(env_dir(name)) if IS_LINUX else None


def _state(name: str) -> str:
    if not IS_LINUX:
        from ..envs import wsl
        return wsl.state(name) if os.name == "nt" else "unknown"
    return "running" if _pid(name) else "stopped"


def _ns_pids(pid1: int) -> list[int]:
    try:
        target = os.readlink(f"/proc/{pid1}/ns/pid")
    except OSError:
        return []
    out = []
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                if os.readlink(f"/proc/{d}/ns/pid") == target or (int(d) == pid1):
                    out.append(int(d))
            except OSError:
                pass
    # 1 号进程本身在父 pid 命名空间里，pid ns 链接指向自己的命名空间之外；也算进去
    try:
        for d in os.listdir("/proc"):
            if d.isdigit():
                with open(f"/proc/{d}/status") as f:
                    if f"PPid:\t{pid1}\n" in f.read():
                        pass
    except OSError:
        pass
    return sorted(set(out))


def _du(p: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(p):
        for f in files:
            try:
                total += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return total


def _stats(name: str) -> dict:
    pid = _pid(name)
    disk = _du(env_dir(name) / "upper") if (env_dir(name) / "upper").exists() else 0
    if not pid:
        return {"state": "stopped", "processes": 0, "cpu_seconds": 0.0, "memory_mb": 0.0, "disk_mb": round(disk / 1048576, 2)}
    tick = os.sysconf("SC_CLK_TCK")
    cpu = 0.0
    rss = 0
    pids = _ns_pids(pid)
    for p in pids:
        try:
            st = open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()
            cpu += (int(st[11]) + int(st[12])) / tick
            rss += int(open(f"/proc/{p}/statm").read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
        except (OSError, IndexError, ValueError):
            pass
    return {"state": "running", "init_pid": pid, "processes": len(pids), "cpu_seconds": round(cpu, 2), "memory_mb": round(rss / 1048576, 1), "disk_mb": round(disk / 1048576, 2)}


def _summary(cfg: dict) -> dict:
    return {"name": cfg["name"], "image": cfg["image"], "backend": cfg.get("backend", BACKEND), "state": _state(cfg["name"]), "network": cfg.get("network"),
            "workspace": cfg.get("workspace"), "limits": cfg.get("limits"), "mounts": cfg.get("mounts", []), "created": cfg.get("created"),
            "snapshots": len(cfg.get("snapshots", [])), "actions": list((cfg.get("actions") or {}).keys())}


# ---------------------------------------------------------------- 命令实现
def env_images(ctx: Context) -> dict:
    local = []
    for d in sorted(images_dir().iterdir()) if images_dir().exists() else []:
        if (d / "manifest.json").exists():
            local.append(json.loads((d / "manifest.json").read_text()))
    return {"backend": BACKEND, "catalog": images.CATALOG, "local": local}


def env_pull(ctx: Context, image: str, sha256: str | None = None) -> dict:
    m = images.pull(image, images_dir(), sha256)
    return {"message": f"镜像就绪：{m['id']}（sha256 {m['sha256'][:12]}…{'，已校验' if m.get('verified') else '，未提供校验值'}）", "image": m}


def env_create(ctx: Context, name: str, image: str = "alpine-3.20", network: str = "host", workspace_mode: str = "rw",
               memory_mb: int | None = None, cpus: float | None = None, pids: int | None = None) -> dict:
    _valid(name)
    if (env_dir(name) / "env.json").exists():
        raise FoxError("CONFLICT", f"环境 {name} 已存在")
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.create(name, image, ctx.workspace.root, home())
    m = images.pull(image, images_dir()) if not (images_dir() / image / "manifest.json").exists() else json.loads((images_dir() / image / "manifest.json").read_text())
    cfg = {"name": name, "image": m["id"], "backend": BACKEND, "lower": str(images_dir() / m["id"] / "rootfs"), "hostname": name, "network": network,
           "workspace": {"path": str(ctx.workspace.root), "mode": workspace_mode}, "limits": {k: v for k, v in {"memory_mb": memory_mb, "cpus": cpus, "pids": pids}.items() if v},
           "mounts": [], "snapshots": [], "actions": {}, "shell": m.get("shell", "/bin/sh"), "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent}
    for sub in ("upper", "work", "logs", "snapshots"):
        (env_dir(name) / sub).mkdir(parents=True, exist_ok=True)
    _save(cfg)
    _log(name, f"created by {ctx.agent} from {m['id']}")
    return {"message": f"已创建环境 {name}（{m['id']}，工作空间以 {workspace_mode} 挂载到 /workspace）", "env": _summary(cfg)}


def env_list(ctx: Context) -> dict:
    d = home() / "instances"
    envs = [_summary(json.loads((p / "env.json").read_text())) for p in sorted(d.iterdir()) if (p / "env.json").exists()] if d.exists() else []
    return {"backend": BACKEND, "count": len(envs), "envs": envs}


def env_info(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    cg = env_dir(name) / "run" / "cgroup"
    cgs = cg.read_text() if cg.exists() else "未启动过"
    note = ("cgroup v2 已启用，限制按整个环境计算" if cgs.startswith("on")
            else f"cgroup v2 不可用（{cgs}）；内存（RLIMIT_AS，每进程）与进程数（RLIMIT_NPROC，按用户）以 rlimit 生效，CPU 上限不生效")
    return {**_summary(cfg), "stats": _stats(name) if IS_LINUX else None, "path": str(env_dir(name)),
            "snapshots_detail": cfg.get("snapshots", []), "actions_detail": [{"name": k, "command": v} for k, v in (cfg.get("actions") or {}).items()],
            "cgroup": cgs, "limits_note": note}


def env_start(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.start(name)
    _need_linux()
    if _pid(name):
        return {"message": f"{name} 已在运行", "env": _summary(cfg)}
    d = env_dir(name)
    (d / "run").mkdir(exist_ok=True)
    for f in ("status", "init.pid"):
        try:
            (d / "run" / f).unlink()
        except FileNotFoundError:
            pass
    # 系统挂载：狐狸OS 安装的 ACP 智能体只读挂到 /opt/foxos/agents，供“在环境中运行智能体”使用
    from ..desktop_client import foxos_home
    agents = foxos_home() / "agents"
    cfg["system_mounts"] = [{"source": str(agents), "target": "/opt/foxos/agents", "readonly": True}] if agents.is_dir() else []
    _save(cfg)
    log = open(d / "logs" / "init.log", "ab")
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2])}
    subprocess.Popen([sys.executable, "-m", "foxos.envs.linux", "supervise", str(d)], stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True, env=env)
    for _ in range(100):
        st = (d / "run" / "status").read_text() if (d / "run" / "status").exists() else ""
        if st.startswith("running"):
            _log(name, f"started by {ctx.agent}: {st}")
            return {"message": f"已启动 {name}（{st}）", "env": _summary(cfg), "status": st}
        if st.startswith("error") or st.startswith("stopped"):
            raise FoxError("ERROR", f"启动失败：{st}", hint=f"查看 {d / 'logs' / 'init.log'}")
        time.sleep(0.05)
    raise FoxError("ERROR", "启动超时", hint=f"查看 {d / 'logs' / 'init.log'}")


def env_stop(ctx: Context, name: str, timeout: float = 5.0) -> dict:
    _cfg(name)
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.stop(name)
    pid = _pid(name)
    if not pid:
        return {"message": f"{name} 没有运行"}
    os.kill(pid, signal.SIGTERM)
    t0 = time.time()
    while time.time() - t0 < timeout and _pid(name):
        time.sleep(0.05)
    if _pid(name):
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.1)
    _log(name, f"stopped by {ctx.agent}")
    return {"message": f"已停止 {name}"}


def env_restart(ctx: Context, name: str) -> dict:
    env_stop(ctx, name)
    return env_start(ctx, name)


def _exec(name: str, argv: list[str], cwd: str = "/workspace", capture: bool = True, envs: dict | None = None, timeout: float | None = None):
    cfg = _cfg(name)
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.exec_(name, argv, cwd)
    if not _pid(name):
        raise FoxError("LOCKED" if False else "DEPENDENCY_MISSING", f"环境 {name} 没有运行", hint=f"foxos env start {name}")
    cmd = [sys.executable, "-m", "foxos.envs.linux", "exec", str(env_dir(name)), "--cwd", cwd]
    for k, v in (envs or {}).items():
        cmd += ["--env", f"{k}={v}"]
    cmd += ["--", *argv]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2])}
    if not capture:
        return subprocess.call(cmd, env=env)
    return subprocess.run(cmd, capture_output=True, env=env, timeout=timeout)


def env_exec(ctx: Context, name: str, command: list, cwd: str = "/workspace", timeout: float = 600) -> dict:
    if not command:
        raise FoxError("USAGE", "缺少要执行的命令")
    argv = [str(c) for c in command]
    if len(argv) == 1 and " " in argv[0]:
        argv = ["/bin/sh", "-c", argv[0]]
    t0 = time.time()
    r = _exec(name, argv, cwd=cwd, timeout=timeout)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    _log(name, f"exec by {ctx.agent}: {shlex.join(argv)} → {r.returncode}")
    return {"env": name, "command": argv, "exit_code": r.returncode, "stdout": out[-200000:], "stderr": err[-50000:], "duration_s": round(time.time() - t0, 3)}


def env_shell(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    if not sys.stdin.isatty():
        raise FoxError("USAGE", "shell 需要交互式终端；非交互请用 foxos env exec")
    code = _exec(name, [cfg.get("shell") or "/bin/sh", "-l"], capture=False)
    return {"message": f"已退出 {name} 的 shell（退出码 {code}）", "exit_code": code}


def _rmtree(p: Path) -> None:
    # overlayfs 的 work/work 目录权限为 000，先补上权限再删除
    def onexc(func, path, _exc):
        os.chmod(path, 0o700)
        parent = os.path.dirname(path)
        os.chmod(parent, 0o700)
        func(path)
    if p.exists():
        for root, dirs, _files in os.walk(p):
            for d in dirs:
                try:
                    os.chmod(os.path.join(root, d), 0o700)
                except OSError:
                    pass
        shutil.rmtree(p, onexc=onexc)


def _copy_tree(src: Path, dst: Path) -> None:
    subprocess.run(["cp", "-a", f"{src}/.", str(dst)], check=True) if IS_LINUX else shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)


def env_clone(ctx: Context, name: str, new_name: str) -> dict:
    cfg = _cfg(name)
    _valid(new_name)
    if (env_dir(new_name) / "env.json").exists():
        raise FoxError("CONFLICT", f"环境 {new_name} 已存在")
    if _pid(name):
        raise FoxError("LOCKED", f"{name} 正在运行，先停止再克隆（保证文件一致）", hint=f"foxos env stop {name}")
    for sub in ("upper", "work", "logs", "snapshots"):
        (env_dir(new_name) / sub).mkdir(parents=True, exist_ok=True)
    _copy_tree(env_dir(name) / "upper", env_dir(new_name) / "upper")
    new = {**cfg, "name": new_name, "hostname": new_name, "snapshots": [], "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cloned_from": name}
    _save(new)
    return {"message": f"已从 {name} 克隆出 {new_name}", "env": _summary(new)}


def _tar_upper(name: str, dest: Path) -> int:
    import zstandard
    cctx = zstandard.ZstdCompressor(level=6, threads=-1)
    with open(dest, "wb") as raw, cctx.stream_writer(raw) as zw:
        p = subprocess.Popen(["tar", "-c", "--numeric-owner", "-C", str(env_dir(name) / "upper"), "."], stdout=subprocess.PIPE)
        shutil.copyfileobj(p.stdout, zw)
        p.wait()
    return dest.stat().st_size


def env_snapshot(ctx: Context, name: str, label: str | None = None) -> dict:
    cfg = _cfg(name)
    if _pid(name):
        raise FoxError("LOCKED", f"{name} 正在运行，先停止再做快照（保证一致性）", hint=f"foxos env stop {name}")
    sid = datetime.now().strftime("%Y%m%dT%H%M%S")
    size = _tar_upper(name, env_dir(name) / "snapshots" / f"{sid}.tar.zst")
    snap = {"id": sid, "label": label, "size": size, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "by": ctx.agent}
    cfg.setdefault("snapshots", []).append(snap)
    _save(cfg)
    return {"message": f"已为 {name} 创建快照 {sid}", "snapshot": snap}


def env_restore(ctx: Context, name: str, snapshot: str) -> dict:
    cfg = _cfg(name)
    if _pid(name):
        raise FoxError("LOCKED", f"{name} 正在运行，先停止再恢复", hint=f"foxos env stop {name}")
    snap = next((s for s in cfg.get("snapshots", []) if s["id"] == snapshot), None)
    if not snap:
        raise FoxError("NOT_FOUND", f"{name} 没有快照 {snapshot}")
    up = env_dir(name) / "upper"
    _rmtree(up)
    _rmtree(env_dir(name) / "work")
    up.mkdir()
    (env_dir(name) / "work").mkdir()
    images.extract_rootfs(env_dir(name) / "snapshots" / f"{snapshot}.tar.zst", up)
    return {"message": f"已把 {name} 恢复到快照 {snapshot}"}


def env_export(ctx: Context, name: str, out: Path) -> dict:
    cfg = _cfg(name)
    if _pid(name):
        raise FoxError("LOCKED", f"{name} 正在运行，先停止再导出", hint=f"foxos env stop {name}")
    # 下层（镜像）在前、可写层在后：tar 解包时后者覆盖前者；overlay 的删除标记（字符设备 0/0）在无特权导出时会被跳过
    m = images.write_foxenv([Path(cfg["lower"]), env_dir(name) / "upper"], out, {"id": f"{name}-export", "name": f"{name}（从 {cfg['image']} 导出）", "source": f"env:{name}"})
    return {"message": f"已导出 {name} → {ctx.rel(out)}（{m['size'] / 1048576:.1f} MB，sha256 {m['sha256'][:12]}…）", "path": ctx.rel(out), "manifest": m}


def env_import(ctx: Context, file: Path, name: str) -> dict:
    m = images.import_foxenv(file, images_dir(), image_id=f"img-{_valid(name)}")
    return env_create(ctx, name, image=m["id"])


def env_delete(ctx: Context, name: str) -> dict:
    _cfg(name)
    if _pid(name):
        env_stop(ctx, name)
    _rmtree(env_dir(name))
    return {"message": f"已删除环境 {name}（镜像保留）"}


def env_mount(ctx: Context, name: str, source: str, target: str, readonly: bool = False, remove: bool = False) -> dict:
    cfg = _cfg(name)
    src = str(Path(source).expanduser().resolve())
    if not remove and not Path(src).exists():
        raise FoxError("NOT_FOUND", f"宿主路径不存在：{src}")
    if not target.startswith("/") or ".." in target.split("/"):
        raise FoxError("USAGE", "目标必须是环境内的绝对路径")
    cfg["mounts"] = [m for m in cfg.get("mounts", []) if m["target"] != target]
    if not remove:
        cfg["mounts"].append({"source": src, "target": target, "readonly": readonly})
    _save(cfg)
    return {"message": f"{'已移除' if remove else '已添加'}挂载 {target}（下次启动生效）", "mounts": cfg["mounts"], "restart_required": bool(_pid(name))}


def env_limits(ctx: Context, name: str, memory_mb: int | None = None, cpus: float | None = None, pids: int | None = None, network: str | None = None, workspace_mode: str | None = None) -> dict:
    cfg = _cfg(name)
    lim = cfg.get("limits") or {}
    for k, v in (("memory_mb", memory_mb), ("cpus", cpus), ("pids", pids)):
        if v is not None:
            if v == 0:
                lim.pop(k, None)
            else:
                lim[k] = v
    cfg["limits"] = lim
    if network:
        cfg["network"] = network
    if workspace_mode:
        cfg["workspace"]["mode"] = workspace_mode
    _save(cfg)
    note = "内存（RLIMIT_AS，每进程）与进程数（RLIMIT_NPROC）以 rlimit 生效；cgroup v2 可写时按整个环境计。cpus 仅在 cgroup v2 可委派时生效。"
    return {"message": f"已更新 {name} 的设置（下次启动生效）", "limits": lim, "network": cfg["network"], "workspace": cfg["workspace"], "note": note}


def env_stats(ctx: Context, name: str | None = None) -> dict:
    names = [name] if name else [e["name"] for e in env_list(ctx)["envs"]]
    return {"stats": {n: _stats(n) for n in names}}


def env_logs(ctx: Context, name: str, lines: int = 100) -> dict:
    _cfg(name)
    out = {}
    for f in ("env.log", "init.log"):
        p = env_dir(name) / "logs" / f
        out[f] = p.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:] if p.exists() else []
    return {"env": name, "logs": out}


def _subst(cmd: str, cfg: dict, ctx: Context) -> str:
    vars_ = {"env": cfg["name"], "image": cfg["image"], "workspace": "/workspace", "host_workspace": str(ctx.workspace.root), "hostname": cfg.get("hostname", cfg["name"])}
    return re.sub(r"\$\{(\w+)\}", lambda m: vars_.get(m.group(1), m.group(0)), cmd)


def env_action_add(ctx: Context, name: str, action: str, command: str) -> dict:
    cfg = _cfg(name)
    cfg.setdefault("actions", {})[action] = command
    _save(cfg)
    return {"message": f"已为 {name} 添加自定义操作 {action}", "actions": cfg["actions"]}


def env_action_run(ctx: Context, name: str, action: str) -> dict:
    cfg = _cfg(name)
    cmd = (cfg.get("actions") or {}).get(action)
    if not cmd:
        raise FoxError("NOT_FOUND", f"{name} 没有自定义操作 {action}")
    return env_exec(ctx, name, ["/bin/sh", "-c", _subst(cmd, cfg, ctx)])


register_app("env", "狐狸OS 环境", "自研隔离环境：每个环境有自己的根文件系统、进程、主机名和资源限制；工作空间按规则挂载到 /workspace。",
             limits=["Linux 后端无特权运行（用户命名空间）；cgroup 不可委派时用 rlimit 限制", "Windows 使用系统自带 WSL2；macOS 使用 Virtualization.framework"])
NAME = Param("name", "string", "环境名", required=True, positional=True, metavar="NAME")
register(Command("env", "images", "列出可用镜像（官方发行版 rootfs）与本地镜像", env_images, examples=["foxos env images --json"]))
register(Command("env", "pull", "下载镜像并校验 sha256（目录 ID、https 地址或 .foxenv 文件）", env_pull,
                 params=[Param("image", "string", "镜像", required=True, positional=True, metavar="IMAGE"), Param("sha256", "string", "期望的 sha256（自定义地址时建议提供）")],
                 examples=["foxos env pull alpine-3.20", "foxos env pull ubuntu-24.04"], permission="run"))
register(Command("env", "create", "创建环境", env_create,
                 params=[NAME, Param("image", "string", "镜像 ID", default="alpine-3.20"), Param("network", "string", "网络：host（共享宿主网络）或 none（只有回环）", enum=["host", "none"], default="host"),
                         Param("workspace_mode", "string", "工作空间挂载方式", enum=["rw", "ro", "none"], default="rw", cli_flag="--workspace-mode"),
                         Param("memory_mb", "integer", "内存上限（MB）"), Param("cpus", "number", "CPU 上限（核，需 cgroup）"), Param("pids", "integer", "进程数上限")],
                 examples=["foxos env create dev", "foxos env create sandbox --image ubuntu-24.04 --network none --workspace-mode ro --memory-mb 1024"], permission="create"))
register(Command("env", "list", "列出环境及状态", env_list, examples=["foxos env list --json"]))
register(Command("env", "info", "环境详情（配置、快照、资源使用）", env_info, params=[NAME], examples=["foxos env info dev --json"]))
register(Command("env", "start", "启动环境", env_start, params=[NAME], examples=["foxos env start dev"], permission="run"))
register(Command("env", "stop", "停止环境", env_stop, params=[NAME, Param("timeout", "number", "等待秒数，超时强制结束", default=5.0)], examples=["foxos env stop dev"], permission="run"))
register(Command("env", "restart", "重启环境", env_restart, params=[NAME], examples=["foxos env restart dev"], permission="run"))
register(Command("env", "exec", "在环境中执行命令（默认工作目录 /workspace）", env_exec,
                 params=[NAME, Param("command", "array", "命令及参数（放在 -- 之后）", positional=True, items={"type": "string"}, metavar="CMD"),
                         Param("cwd", "string", "环境内工作目录", default="/workspace"), Param("timeout", "number", "超时秒数", default=600)],
                 examples=["foxos env exec dev -- uname -a", "foxos env exec dev -- sh -c 'apk add python3 && python3 -V' --json"], permission="run"))
register(Command("env", "shell", "进入环境的交互式 shell", env_shell, params=[NAME], examples=["foxos env shell dev"], permission="run"))
register(Command("env", "clone", "克隆环境（复制可写层与设置）", env_clone, params=[NAME, Param("new_name", "string", "新环境名", required=True, positional=True, metavar="NEW_NAME")],
                 examples=["foxos env clone dev dev-copy"], permission="create"))
register(Command("env", "snapshot", "为停止的环境创建快照", env_snapshot, params=[NAME, Param("label", "string", "说明")], examples=["foxos env snapshot dev --label 装好依赖"], permission="create"))
register(Command("env", "restore", "恢复到快照", env_restore, params=[NAME, Param("snapshot", "string", "快照 ID", required=True, positional=True, metavar="SNAPSHOT")],
                 examples=["foxos env restore dev 20261110T213000"], permission="modify"))
register(Command("env", "export", "导出为 .foxenv 镜像（tar + zstd + manifest + sha256）", env_export,
                 params=[NAME, Param("out", "string", "输出文件（工作空间内）", required=True, path="write")], examples=["foxos env export dev --out backups/dev.foxenv"], permission="create"))
register(Command("env", "import", "从 .foxenv 镜像导入为新环境", env_import,
                 params=[Param("file", "string", ".foxenv 文件（工作空间内）", required=True, positional=True, path="read", metavar="FILE"), Param("name", "string", "新环境名", required=True)],
                 examples=["foxos env import backups/dev.foxenv --name dev2"], permission="create"))
register(Command("env", "delete", "删除环境（不删除镜像与工作空间）", env_delete, params=[NAME], examples=["foxos env delete dev-copy"], permission="delete"))
register(Command("env", "mount", "添加 / 移除宿主目录挂载", env_mount,
                 params=[NAME, Param("source", "string", "宿主路径", required=True), Param("target", "string", "环境内路径", required=True),
                         Param("readonly", "boolean", "只读"), Param("remove", "boolean", "移除该挂载")],
                 examples=["foxos env mount dev --source ~/datasets --target /data --readonly"], permission="modify"))
register(Command("env", "limits", "设置资源限制、网络与工作空间权限", env_limits,
                 params=[NAME, Param("memory_mb", "integer", "内存上限 MB（0 取消）"), Param("cpus", "number", "CPU 上限（0 取消）"), Param("pids", "integer", "进程数上限（0 取消）"),
                         Param("network", "string", "网络", enum=["host", "none"]), Param("workspace_mode", "string", "工作空间挂载", enum=["rw", "ro", "none"], cli_flag="--workspace-mode")],
                 examples=["foxos env limits dev --memory-mb 2048 --pids 512", "foxos env limits dev --network none"], permission="modify"))
register(Command("env", "stats", "资源使用（进程数、CPU 时间、内存、磁盘）", env_stats, params=[Param("name", "string", "环境名（缺省为全部）", positional=True, metavar="NAME")],
                 examples=["foxos env stats --json"], audited=False))
register(Command("env", "logs", "环境日志", env_logs, params=[NAME, Param("lines", "integer", "行数", default=100, cli_short="-n")], examples=["foxos env logs dev -n 50"]))
register(Command("env", "action add", "添加自定义操作（支持 ${env} ${image} ${workspace} ${host_workspace} ${hostname} 变量）", env_action_add,
                 params=[NAME, Param("action", "string", "操作名", required=True, positional=True, metavar="ACTION"), Param("command", "string", "环境内执行的 shell 命令", required=True)],
                 examples=["foxos env action add dev test --command 'cd ${workspace} && make test'"], permission="modify"))
register(Command("env", "action run", "运行自定义操作", env_action_run, params=[NAME, Param("action", "string", "操作名", required=True, positional=True, metavar="ACTION")],
                 examples=["foxos env action run dev test --json"], permission="run"))
