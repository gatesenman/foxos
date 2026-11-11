"""狐狸OS 环境（foxos env）：自研的隔离环境层。

Linux：自研运行时（用户 / mount / pid / uts / ipc / 可选 net 命名空间、overlayfs、pivot_root、seccomp、cgroup v2 或 rlimit），见 foxos/envs/linux.py。
Windows：直接驱动系统自带的 WSL2（wsl.exe --import / --export / --terminate），见 foxos/envs/wsl.py。
macOS：Apple Virtualization.framework（Swift 小助手 foxos-vz），见 foxos/envs/macos.py。
"""

from __future__ import annotations

from foxos.i18n import tr
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
from ..envs import download, images
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app

IS_LINUX = sys.platform.startswith("linux")
BACKEND = "linux-ns" if IS_LINUX else ("wsl2" if os.name == "nt" else "macos-vz")


def _provider_id(cfg: dict) -> str:
    return cfg.get("provider") or cfg.get("backend") or BACKEND


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
        raise FoxError("USAGE", tr("env.environment_names_may_only_contain"))
    return name


def _cfg(name: str) -> dict:
    f = env_dir(_valid(name)) / "env.json"
    if not f.exists():
        raise FoxError("NOT_FOUND", tr("env.no_environment_named", name), hint="foxos env list")
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
        raise FoxError("DEPENDENCY_MISSING", tr("env.this_machine_s_backend_is_this", BACKEND), hint=tr("env.on_windows_use_the_wsl2_backend_of"))


def _linux():
    from ..envs import linux
    return linux


def _pid(name: str) -> int | None:
    return _linux().init_pid(env_dir(name)) if IS_LINUX else None


def _state(name: str) -> str:
    cfg = _cfg(name)
    pid = _provider_id(cfg)
    if pid == "linux-kvm":
        from ..envs import kvm
        return kvm.state(env_dir(name), cfg)
    if not IS_LINUX:
        from ..envs import wsl
        if os.name != "nt":
            return "unknown"
        try:
            return wsl.state(cfg)
        except FoxError:
            return "unknown"
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
            "snapshots": len(cfg.get("snapshots", [])), "actions": list((cfg.get("actions") or {}).keys()),
            "catalog_id": cfg.get("catalog_id"), "guest_os": cfg.get("guest_os", "linux"), "provider": cfg.get("provider", cfg.get("backend", BACKEND)),
            "ssh": _ssh_summary(cfg)}


def _ssh_summary(cfg: dict) -> dict | None:
    """虚拟机的 SSH 入口（端口转发）：本机命令，以及 env expose --ssh on 之后的对外地址。"""
    f = env_dir(cfg["name"]) / "run" / "ssh.json"
    try:
        s = json.loads(f.read_text(encoding="utf-8")) if _state(cfg["name"]) == "running" else None
    except (OSError, ValueError):
        s = None
    if not s and not cfg.get("ssh_expose"):
        return None
    port = (s or {}).get("port") or cfg.get("ssh_port")
    key = (cfg.get("ssh") or {}).get("key")
    user = (cfg.get("ssh") or {}).get("user") or "foxos"
    return {"port": port, "user": user, "exposed": bool(cfg.get("ssh_expose")), "bind": (s or {}).get("bind") or "127.0.0.1",
            "command": f"ssh -p {port} {('-i ' + key + ' ') if key else ''}{user}@127.0.0.1" if port else None}


# ---------------------------------------------------------------- 命令实现
def env_run(ctx: Context, name: str, image: str | None = None, iso: str | None = None, provider: str | None = None,
            network: str = "user", workspace_mode: str = "rw", memory_mb: int | None = None, cpus: float | None = None,
            pids: int | None = None, desktop_attach: bool = False, no_start: bool = False) -> dict:
    """没有就创建并启动（靠近 docker run）。--iso 默认走 linux-kvm。"""
    _valid(name)
    prov = provider or ("linux-kvm" if iso else BACKEND)
    exists = (env_dir(name) / "env.json").exists()
    if not exists:
        if prov == "linux-kvm":
            if iso:
                iso_path = str(Path(iso).expanduser())
                if not Path(iso_path).is_file():
                    # 也允许工作空间相对路径
                    cand = ctx.workspace.root / iso
                    iso_path = str(cand) if cand.is_file() else iso_path
                if not Path(iso_path).is_file():
                    raise FoxError("NOT_FOUND", tr("env.iso_not_found", iso))
            cfg = {"name": name, "image": image or (Path(iso).name if iso else "linux-kvm"),
                   "backend": "linux-kvm", "provider": "linux-kvm", "guest_os": "linux",
                   "iso": str(Path(iso_path).resolve()) if iso else None,
                   "network": network if network != "host" else "user",
                   "workspace": {"path": str(ctx.workspace.root), "mode": workspace_mode},
                   "limits": {k: v for k, v in {"memory_mb": memory_mb, "cpus": cpus, "pids": pids}.items() if v},
                   "mounts": [], "snapshots": [], "actions": {}, "shell": "/bin/sh",
                   "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent}
            for sub in ("logs", "run"):
                (env_dir(name) / sub).mkdir(parents=True, exist_ok=True)
            _save(cfg)
            _log(name, f"created by {ctx.agent} provider=linux-kvm iso={cfg.get('iso')}")
        else:
            env_create(ctx, name, image=image or "alpine-3.20", network="host" if network == "user" else network,
                       workspace_mode=workspace_mode, memory_mb=memory_mb, cpus=cpus, pids=pids)
    if no_start:
        return {"message": tr("env.created_environment_not_started", name), "env": _summary(_cfg(name))}
    started = env_start(ctx, name)
    if desktop_attach:
        att = env_desktop_attach(ctx, name)
        started["attach"] = att
    return started


def env_desktop_attach(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    if _provider_id(cfg) != "linux-kvm":
        raise FoxError("USAGE", tr("env.desktop_attach_is_for_linux_kvm"), hint=tr("env.use_provider_linux_kvm_or_pass_iso"))
    from ..envs import kvm
    return kvm.desktop_attach(cfg, env_dir(name))


def env_images(ctx: Context) -> dict:
    local = []
    for d in sorted(images_dir().iterdir()) if images_dir().exists() else []:
        if (d / "manifest.json").exists():
            local.append(json.loads((d / "manifest.json").read_text()))
    return {"backend": BACKEND, "catalog": images.CATALOG, "local": local}


def env_pull(ctx: Context, image: str, sha256: str | None = None) -> dict:
    m = images.pull(image, images_dir(), sha256)
    return {"message": tr("env.image_ready_sha256", m['id'], m['sha256'][:12], tr("env.verified") if m.get('verified') else tr("env.no_checksum_given")), "image": m}


def env_create(ctx: Context, name: str, image: str = "alpine-3.20", network: str = "host", workspace_mode: str = "rw",
               memory_mb: int | None = None, cpus: float | None = None, pids: int | None = None) -> dict:
    _valid(name)
    if (env_dir(name) / "env.json").exists():
        raise FoxError("CONFLICT", tr("env.environment_already_exists", name))
    if BACKEND == "wsl2":
        from ..envs import wsl
        r = wsl.create(name, image, ctx.workspace.root, home())
        _save({"name": name, "image": r.get("image", image), "backend": "wsl2", "wsl_distro": wsl.distro(name), "network": "host",
               "workspace": {"path": str(ctx.workspace.root), "mode": "rw"}, "limits": {}, "mounts": [], "snapshots": [], "actions": {}, "shell": "/bin/sh",
               "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent})
        return r
    m = images.pull(image, images_dir()) if not (images_dir() / image / "manifest.json").exists() else json.loads((images_dir() / image / "manifest.json").read_text())
    cfg = {"name": name, "image": m["id"], "backend": BACKEND, "lower": str(images_dir() / m["id"] / "rootfs"), "hostname": name, "network": network,
           "workspace": {"path": str(ctx.workspace.root), "mode": workspace_mode}, "limits": {k: v for k, v in {"memory_mb": memory_mb, "cpus": cpus, "pids": pids}.items() if v},
           "mounts": [], "snapshots": [], "actions": {}, "shell": m.get("shell", "/bin/sh"), "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent}
    for sub in ("upper", "work", "logs", "snapshots"):
        (env_dir(name) / sub).mkdir(parents=True, exist_ok=True)
    _save(cfg)
    _log(name, f"created by {ctx.agent} from {m['id']}")
    return {"message": tr("env.created_environment_workspace", name, m['id'], workspace_mode), "env": _summary(cfg)}


def env_list(ctx: Context) -> dict:
    d = home() / "instances"
    envs = [_summary(json.loads((p / "env.json").read_text())) for p in sorted(d.iterdir()) if (p / "env.json").exists()] if d.exists() else []
    return {"backend": BACKEND, "count": len(envs), "envs": envs}


def env_info(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    cg = env_dir(name) / "run" / "cgroup"
    cgs = cg.read_text() if cg.exists() else tr("env.never_started")
    note = (tr("env.cgroup_v2_is_enabled_limits_apply_to") if cgs.startswith("on")
            else tr("env.cgroup_v2_is_unavailable_memory", cgs))
    return {**_summary(cfg), "stats": _stats(name) if IS_LINUX else None, "path": str(env_dir(name)),
            "snapshots_detail": cfg.get("snapshots", []), "actions_detail": [{"name": k, "command": v} for k, v in (cfg.get("actions") or {}).items()],
            "cgroup": cgs, "limits_note": note}


def env_start(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    if _provider_id(cfg) == "linux-kvm":
        from ..envs import kvm
        r = kvm.start(cfg, env_dir(name))
        _log(name, f"started by {ctx.agent}: {r.get('vmm')}")
        return {**r, "env": _summary(_cfg(name))}
    if cfg.get("start_steps"):
        from ..envs import providers
        providers.execute(cfg["start_steps"])
        _log(name, f"started by {ctx.agent}")
        return {"message": tr("env.started", name, cfg.get('provider')), "env": _summary(cfg)}
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.start(cfg)
    _need_linux()
    if _pid(name):
        return {"message": tr("env.is_already_running", name), "env": _summary(cfg)}
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
            return {"message": tr("env.started", name, st), "env": _summary(cfg), "status": st}
        if st.startswith("error") or st.startswith("stopped"):
            raise FoxError("ERROR", tr("env.failed_to_start", st), hint=tr("common.see", d / 'logs' / 'init.log'))
        time.sleep(0.05)
    raise FoxError("ERROR", tr("env.start_timed_out"), hint=tr("common.see", d / 'logs' / 'init.log'))


def env_stop(ctx: Context, name: str, timeout: float = 5.0) -> dict:
    cfg = _cfg(name)
    if _provider_id(cfg) == "linux-kvm":
        from ..envs import kvm
        r = kvm.stop(cfg, env_dir(name), timeout=timeout)
        _log(name, f"stopped by {ctx.agent}")
        return r
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.stop(cfg)
    pid = _pid(name)
    if not pid:
        return {"message": tr("env.is_not_running", name)}
    os.kill(pid, signal.SIGTERM)
    t0 = time.time()
    while time.time() - t0 < timeout and _pid(name):
        time.sleep(0.05)
    if _pid(name):
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.1)
    _log(name, f"stopped by {ctx.agent}")
    return {"message": tr("common.stopped", name)}


def env_restart(ctx: Context, name: str) -> dict:
    env_stop(ctx, name)
    return env_start(ctx, name)


def _exec(name: str, argv: list[str], cwd: str = "/workspace", capture: bool = True, envs: dict | None = None, timeout: float | None = None):
    cfg = _cfg(name)
    if _provider_id(cfg) == "linux-kvm":
        from ..envs import kvm
        return kvm.exec_in(cfg, env_dir(name), argv, cwd=cwd, timeout=timeout)
    if BACKEND == "wsl2":
        from ..envs import wsl
        return wsl.exec_(cfg, argv, cwd, capture=capture, timeout=timeout)
    if not _pid(name):
        raise FoxError("LOCKED" if False else "DEPENDENCY_MISSING", tr("env.environment_is_not_running", name), hint=f"foxos env start {name}")
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
        raise FoxError("USAGE", tr("common.missing_the_command_to_run"))
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
        raise FoxError("USAGE", tr("env.shell_needs_an_interactive_terminal"))
    code = _exec(name, [cfg.get("shell") or "/bin/sh", "-l"], capture=False)
    return {"message": tr("env.exited_the_shell_of_exit_code", name, code), "exit_code": code}


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
        raise FoxError("CONFLICT", tr("env.environment_already_exists", new_name))
    if _pid(name):
        raise FoxError("LOCKED", tr("env.is_running_stop_it_before_cloning_to", name), hint=f"foxos env stop {name}")
    for sub in ("upper", "work", "logs", "snapshots"):
        (env_dir(new_name) / sub).mkdir(parents=True, exist_ok=True)
    _copy_tree(env_dir(name) / "upper", env_dir(new_name) / "upper")
    new = {**cfg, "name": new_name, "hostname": new_name, "snapshots": [], "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cloned_from": name}
    _save(new)
    return {"message": tr("env.cloned_from", name, new_name), "env": _summary(new)}


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
        raise FoxError("LOCKED", tr("env.is_running_stop_it_before_taking_a", name), hint=f"foxos env stop {name}")
    sid = datetime.now().strftime("%Y%m%dT%H%M%S")
    size = _tar_upper(name, env_dir(name) / "snapshots" / f"{sid}.tar.zst")
    snap = {"id": sid, "label": label, "size": size, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "by": ctx.agent}
    cfg.setdefault("snapshots", []).append(snap)
    _save(cfg)
    return {"message": tr("env.created_snapshot_of", name, sid), "snapshot": snap}


def env_restore(ctx: Context, name: str, snapshot: str) -> dict:
    cfg = _cfg(name)
    if _pid(name):
        raise FoxError("LOCKED", tr("env.is_running_stop_it_before_restoring", name), hint=f"foxos env stop {name}")
    snap = next((s for s in cfg.get("snapshots", []) if s["id"] == snapshot), None)
    if not snap:
        raise FoxError("NOT_FOUND", tr("env.has_no_snapshot", name, snapshot))
    up = env_dir(name) / "upper"
    _rmtree(up)
    _rmtree(env_dir(name) / "work")
    up.mkdir()
    (env_dir(name) / "work").mkdir()
    images.extract_rootfs(env_dir(name) / "snapshots" / f"{snapshot}.tar.zst", up)
    return {"message": tr("env.restored_to_snapshot", name, snapshot)}


def env_export(ctx: Context, name: str, out: Path) -> dict:
    cfg = _cfg(name)
    if cfg.get("backend") == "wsl2":
        from ..envs import wsl
        wsl.export(cfg, str(out))
        return {"message": tr("env.exported_wsl_tar_format_import_it", name, ctx.rel(out)), "path": ctx.rel(out)}
    if _pid(name):
        raise FoxError("LOCKED", tr("env.is_running_stop_it_before_exporting", name), hint=f"foxos env stop {name}")
    # 下层（镜像）在前、可写层在后：tar 解包时后者覆盖前者；overlay 的删除标记（字符设备 0/0）在无特权导出时会被跳过
    m = images.write_foxenv([Path(cfg["lower"]), env_dir(name) / "upper"], out, {"id": f"{name}-export", "name": tr("env.exported_from", name, cfg['image']), "source": f"env:{name}"})
    return {"message": tr("env.exported_mb_sha256", name, ctx.rel(out), m['size'] / 1048576, m['sha256'][:12]), "path": ctx.rel(out), "manifest": m}


def env_import(ctx: Context, file: Path, name: str) -> dict:
    m = images.import_foxenv(file, images_dir(), image_id=f"img-{_valid(name)}")
    return env_create(ctx, name, image=m["id"])


def env_delete(ctx: Context, name: str) -> dict:
    cfg = _cfg(name)
    if cfg.get("backend") == "wsl2":
        from ..envs import wsl
        wsl.unregister(cfg)
        _rmtree(env_dir(name))
        return {"message": tr("env.deleted_environment_unregistered_wsl", name, wsl.dname(cfg))}
    if cfg.get("backend") in ("windows-sandbox", "hyperv"):
        _rmtree(env_dir(name))
        return {"message": tr("env.removed_from_the_list", name) + (tr("env.delete_the_hyper_v_virtual_machine") if cfg.get("backend") == "hyperv" else "")}
    if _provider_id(cfg) == "linux-kvm":
        if _state(name) == "running":
            env_stop(ctx, name)
        _rmtree(env_dir(name))
        return {"message": tr("env.deleted_environment_image_kept", name)}
    if _pid(name):
        env_stop(ctx, name)
    _rmtree(env_dir(name))
    return {"message": tr("env.deleted_environment_image_kept", name)}


def env_mount(ctx: Context, name: str, source: str, target: str, readonly: bool = False, remove: bool = False) -> dict:
    cfg = _cfg(name)
    src = str(Path(source).expanduser().resolve())
    if not remove and not Path(src).exists():
        raise FoxError("NOT_FOUND", tr("env.host_path_does_not_exist", src))
    if not target.startswith("/") or ".." in target.split("/"):
        raise FoxError("USAGE", tr("env.the_target_must_be_an_absolute_path"))
    cfg["mounts"] = [m for m in cfg.get("mounts", []) if m["target"] != target]
    if not remove:
        cfg["mounts"].append({"source": src, "target": target, "readonly": readonly})
    _save(cfg)
    return {"message": tr("env.mount_applies_on_next_start", tr("env.removed") if remove else tr("env.added"), target), "mounts": cfg["mounts"], "restart_required": bool(_pid(name))}


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
    note = tr("env.memory_rlimit_as_per_process_and")
    return {"message": tr("env.updated_the_settings_of_applies_on", name), "limits": lim, "network": cfg["network"], "workspace": cfg["workspace"], "note": note}


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
    return {"message": tr("env.added_custom_action_to", name, action), "actions": cfg["actions"]}


def env_action_run(ctx: Context, name: str, action: str) -> dict:
    cfg = _cfg(name)
    cmd = (cfg.get("actions") or {}).get(action)
    if not cmd:
        raise FoxError("NOT_FOUND", tr("env.has_no_custom_action", name, action))
    return env_exec(ctx, name, ["/bin/sh", "-c", _subst(cmd, cfg, ctx)])



# ---------------------------------------------------------------- 系统目录与提供者（一键安装系统）
def env_providers(ctx: Context) -> dict:
    from ..envs import providers
    out = []
    for p in providers.providers().values():
        d = p.describe()
        try:
            d["doctor"] = p.doctor()
        except FoxError as e:
            d["doctor"] = {"available": False, "reason": e.message, "checks": [], "actions": []}
        out.append(d)
    return {"host": providers.host_os(), "protocol": providers.PROTOCOL, "providers": out}


def env_doctor(ctx: Context, provider: str | None = None) -> dict:
    from ..envs import providers
    ids = [provider] if provider else [p.id for p in providers.providers().values() if providers.host_os() in p.platforms]
    res = {i: providers.get(i).doctor() for i in ids}
    return {"host": providers.host_os(), "results": res, "ok": all(r.get("available") for r in res.values()) if res else False}


def env_fix(ctx: Context, provider: str, action: str) -> dict:
    """执行 doctor 给出的修复操作（如启用 WSL / Windows Sandbox / Hyper-V，会弹出管理员确认）。"""
    from ..envs import providers
    d = providers.get(provider).doctor()
    act = next((a for a in d.get("actions", []) if a["id"] == action), None)
    if not act:
        raise FoxError("NOT_FOUND", tr("env.currently_has_no_fix", provider, action), hint=f"foxos env doctor --provider {provider}")
    if act.get("manual"):
        return {"message": act["label"], "manual": True, "reboot_required": False, "results": []}
    res = providers.execute([act])
    reboot = any(r.get("reboot_required") for r in res) or action.startswith("enable-")
    return {"message": tr("env.done", act['label']) + (tr("env.restart_the_computer_for_it_to_take") if reboot else ""), "reboot_required": reboot, "results": res}


def env_catalog(ctx: Context, guest: str | None = None, provider: str | None = None, available: bool = False, presets: bool = False) -> dict:
    from ..envs import presets as P
    from ..envs import providers
    c = providers.catalog()
    host = providers.host_os()
    provs = providers.providers()
    items = []
    for e in P.entries():
        it = P.describe(e, host)
        if guest and e.get("guest_os") != guest:
            continue
        if provider and provider not in [h.get("provider") for h in (e.get("hosts") or {}).values()]:
            continue
        if available and not it["installable"]:
            continue
        items.append(it)
    for e in ([] if presets else c["entries"]):
        if guest and e.get("guest_os") != guest:
            continue
        if provider and provider not in e["providers"]:
            continue
        usable = [p for p in e["providers"] if p in provs and host in provs[p].platforms]
        it = {**e, "host_providers": usable, "installable": bool(usable) and not e.get("disabled")}
        if not it["installable"] and not e.get("disabled"):
            it["reason"] = tr("env.no_provider_is_available_on_this", host, '/'.join(e['providers']))
        if available and not it["installable"]:
            continue
        items.append(it)
    return {"format": c["format"], "version": c["version"], "presets_format": P.FORMAT, "host": host, "count": len(items),
            "presets": sum(1 for i in items if i.get("preset")), "entries": items}


def _install_status(name: str, **kw) -> None:
    d = env_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "install.json"
    cur = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    cur.update(kw, updated=time.time())
    f.write_text(json.dumps(cur, ensure_ascii=False), encoding="utf-8")


def env_install(ctx: Context, entry: str, name: str, provider: str | None = None, url: str | None = None, sha256: str | None = None, iso: str | None = None,
                location: str | None = None, memory_mb: int | None = None, cpus: int | None = None, disk_gb: int | None = None, dry_run: bool = False,
                product_key: str | None = None, start: bool = False, wait_ready: float = 0) -> dict:
    from ..envs import presets as P
    from ..envs import providers
    _valid(name)
    pe = P.get(entry)
    if pe is not None:
        return _install_preset(ctx, pe, name, provider=provider, iso=iso, sha256=sha256, memory_mb=memory_mb, cpus=cpus, disk_gb=disk_gb,
                               product_key=product_key, start=start, wait_ready=wait_ready, location=location, dry_run=dry_run)
    e = providers.entry(entry)
    if e.get("disabled"):
        raise FoxError("DEPENDENCY_MISSING", tr("env.is_unavailable", e['name'], e.get('reason')))
    host = providers.host_os()
    provs = providers.providers()
    cands = [provider] if provider else [p for p in e["providers"] if p in provs and host in provs[p].platforms] or e["providers"][:1]
    if not provider and host == "linux" and "linux-kvm" in cands:
        kvm_doc = providers.get("linux-kvm").doctor()
        # 根文件系统类的条目（alpine / rootfs / lxc）没有可引导的磁盘：没给 --iso 时用 KVM 装不了，不要优先它
        rootfs_only = e["source"]["kind"] in ("rootfs", "alpine", "lxc") and not iso
        if kvm_doc.get("available") and kvm_doc.get("kvm", {}).get("available") and not rootfs_only:
            cands = ["linux-kvm"] + [c for c in cands if c != "linux-kvm"]
        else:
            cands = [c for c in cands if c != "linux-kvm"] + (["linux-kvm"] if "linux-kvm" in cands else [])
    p = providers.get(cands[0])
    opts = {"url": url, "sha256": sha256, "iso": iso, "location": location, "memory_mb": memory_mb, "cpus": cpus, "disk_gb": disk_gb, "workspace": str(ctx.workspace.root)}
    if not dry_run and (env_dir(name) / "env.json").exists():
        raise FoxError("CONFLICT", tr("env.environment_already_exists", name))
    src = providers.resolve_source(e, opts) if e["source"]["kind"] in ("rootfs", "alpine", "lxc", "custom") else dict(e["source"])
    opts["_resolved"] = src
    steps = p.plan_install(e, name, opts)
    plan = {"entry": e["id"], "name": name, "provider": p.id, "source": src, "steps": steps}
    if dry_run:
        return {"message": tr("env.install_plan_steps", e['name'], name, p.id, len(steps)), "plan": plan, "dry_run": True}
    if host not in p.platforms:
        raise FoxError("DEPENDENCY_MISSING", tr("env.needs_a_host_current", p.name, '/'.join(p.platforms), host), hint=tr("env.add_dry_run_to_see_the_install_plan"))
    doc = p.doctor()
    if not doc.get("available"):
        acts = tr("common.text").join(tr("env.foxos_env_fix_provider_action", p.id, a['id'], a['label']) for a in doc.get("actions", []))
        raise FoxError("DEPENDENCY_MISSING", tr("env.is_unavailable", p.name, doc.get('reason')), hint=acts or None)
    _install_status(name, state="running", entry=e["id"], provider=p.id, steps=len(steps), step=0)
    try:
        res = providers.execute(steps, report=lambda **k: _install_status(name, **k))
    except FoxError as ex:
        _install_status(name, state="error", error=ex.message)
        raise
    if p.id != "linux-ns":  # linux-ns 由 env create 自己写配置
        reg = next((s.get("registers") for s in steps if s.get("registers")), None)
        cfg = {"name": name, "image": e["id"], "catalog_id": e["id"], "backend": p.id, "provider": p.id, "guest_os": e.get("guest_os", "linux"),
               "network": "host", "workspace": {"path": str(ctx.workspace.root), "mode": "rw"}, "limits": {k: v for k, v in {"memory_mb": memory_mb, "cpus": cpus}.items() if v},
               "mounts": [], "snapshots": [], "actions": {}, "shell": "/bin/bash" if e.get("family") not in ("alpine",) else "/bin/sh",
               "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent, "source": src}
        if p.id == "wsl2":
            cfg["wsl_distro"] = reg
        else:
            cfg["start_steps"] = [s for s in steps if "argv" in s or "powershell" in s][-1:]
            if p.id == "hyperv":
                cfg["start_steps"] = [{"powershell": f"Start-VM -Name {providers.ps_quote(providers.wsl_name(name))}", "elevate": True}, {"argv": ["vmconnect.exe", "localhost", providers.wsl_name(name)]}]
        _save(cfg)
    _install_status(name, state="done")
    _log(name, f"installed {e['id']} via {p.id} by {ctx.agent}")
    return {"message": tr("env.installed_as_environment", e['name'], name, p.id), "plan": plan, "results": res}


def _install_preset(ctx: Context, e: dict, name: str, *, provider: str | None, iso: str | None, sha256: str | None, memory_mb: int | None,
                    cpus: int | None, disk_gb: int | None, product_key: str | None, start: bool, wait_ready: float, location: str | None, dry_run: bool) -> dict:
    """安装一个狐狸OS 预设：下载（可续传、逐卷校验）→ 拼接校验 → 生成种子 → 注册环境 →（可选）启动并等来宾报告就绪。"""
    from ..envs import presets as P
    from ..envs import providers
    host = providers.host_os()
    tgt = P.target(e, host)
    s = P.sizes(e, tgt["artifact"])
    plan = {"entry": e["id"], "name": name, "kind": e["kind"], "host": host, "provider": provider or tgt["provider"], "artifact": tgt["artifact"],
            "download_bytes": s["download_bytes"], "disk_bytes": s["disk_bytes"], "features": e.get("features", []),
            "files": [{k: p.get(k) for k in ("name", "url", "size", "sha256")} for p in ((e.get("artifacts") or {}).get(tgt["artifact"] or "", {}).get("parts") or
                      ([e["artifacts"][tgt["artifact"]]] if tgt["artifact"] in (e.get("artifacts") or {}) else []))]}
    if e["kind"] == "windows-media":
        plan["media"] = {k: (e.get("media") or {}).get(k) for k in ("url", "page", "size", "sha256", "edition", "language")}
        plan["license"] = e.get("license")
    if e["kind"] == "macos-ipsw":
        plan["media"] = e.get("media")
    if dry_run:
        return {"message": tr("env.preset_plan", e["name"], name, plan["provider"] or "-", _hsize(s["download_bytes"]), _hsize(s["disk_bytes"])),
                "plan": plan, "dry_run": True, "available": tgt["available"], **({"reason": tgt["reason"]} if not tgt["available"] else {})}
    if not tgt["available"]:
        raise FoxError("DEPENDENCY_MISSING", tr("env.is_unavailable", e["name"], tgt["reason"]))
    if (env_dir(name) / "env.json").exists():
        raise FoxError("CONFLICT", tr("env.environment_already_exists", name))
    pid = provider or tgt["provider"]
    prov = providers.get(pid)
    doc = prov.doctor()
    if not doc.get("available"):
        acts = tr("common.text").join(tr("env.foxos_env_fix_provider_action", prov.id, a['id'], a['label']) for a in doc.get("actions", []))
        raise FoxError("DEPENDENCY_MISSING", tr("env.is_unavailable", prov.name, doc.get('reason')), hint=acts or None)
    d = env_dir(name)
    cache = home() / "cache" / "presets" / e["id"]
    P.check_space(d.parent if d.parent.exists() else home(), s["disk_bytes"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "logs").mkdir(exist_ok=True); (d / "run").mkdir(exist_ok=True)
    t0 = time.time()
    rep = lambda **k: _install_status(name, state="running", entry=e["id"], provider=pid, total=4, step={"download": 0, "verify": 1, "seed": 2, "boot": 3}.get(k.get("phase"), 0),  # noqa: E731
                                      download_bytes=s["download_bytes"], disk_bytes=s["disk_bytes"], elapsed=round(time.time() - t0, 1), **k)
    rep(phase="download", why=tr("env.preset_starting", e["name"]), bytes=0, bytes_total=s["download_bytes"])
    cfg_base = {"name": name, "image": e["id"], "catalog_id": e["id"], "preset": e["id"], "guest_os": e.get("guest_os"),
                "workspace": {"path": str(ctx.workspace.root), "mode": "rw"}, "mounts": [], "snapshots": [], "actions": {},
                "limits": {k: v for k, v in {"memory_mb": memory_mb or e.get("memory_mb"), "cpus": cpus or e.get("cpus")}.items() if v},
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "created_by": ctx.agent, "features": e.get("features", [])}
    result: dict = {"plan": plan}
    try:
        if e["kind"] in ("foxos-image", "foxos-iso") and pid == "linux-kvm":
            is_iso = e["kind"] == "foxos-iso"
            target = d / ("install.iso" if is_iso else "disk.qcow2")
            if iso and is_iso:
                shutil.copy2(iso, target)
                fetched = {"parts": [], "assembled": {"sha256": images._sha256(target), "verified": False}}
            else:
                fetched = P.fetch_artifact(e, tgt["artifact"], cache, target, rep)
            result["download"] = fetched
            rep(phase="seed", why=tr("env.preset_seed"))
            key = P.make_ssh_key(d / "ssh")
            seed_dir = d / "seed"; seed_dir.mkdir(exist_ok=True)
            (seed_dir / "seed.json").write_text(json.dumps(P.seed_json(name, ssh_pub=key["pub"]), ensure_ascii=False, indent=1), encoding="utf-8")
            seed_iso = P.make_seed_iso(seed_dir, d / "seed.iso") if not is_iso else None
            cfg = {**cfg_base, "backend": "linux-kvm", "provider": "linux-kvm", "network": "user", "shell": "/bin/bash",
                   **({"iso": str(target)} if is_iso else {"disk": str(target), "disk_format": "qcow2", "boot": "uefi", "seed": str(seed_iso)}),
                   "ssh": {"host": "127.0.0.1", "user": "foxos", "key": key["key"]} if key["key"] and not is_iso else {}}
            _save(cfg)
        elif e["kind"] == "foxos-image" and pid == "wsl2":
            target = cache / e["artifacts"]["wsl"]["name"]
            result["download"] = P.fetch_artifact(e, "wsl", cache, target, rep)
            loc = location or str(d / "wsl")
            steps = [{"argv": ["wsl.exe", "--import", providers.wsl_name(name), loc, str(target), "--version", "2"], "registers": providers.wsl_name(name),
                      "why": tr("env.preset_wsl_import")}]
            rep(phase="seed", why=tr("env.preset_wsl_import"))
            result["results"] = providers.execute(steps)
            cfg = {**cfg_base, "backend": "wsl2", "provider": "wsl2", "wsl_distro": providers.wsl_name(name), "network": "host", "shell": "/bin/bash"}
            _save(cfg)
        elif pid == "hyperv":
            if e["kind"] == "foxos-iso":
                media = d / "install.iso"
                result["download"] = P.fetch_artifact(e, tgt["artifact"], cache, media, rep) if not iso else {"local": iso}
                media_path = iso or str(media)
                seed_ps = None
            else:  # windows-media：从微软官方下载安装介质（或用户给的 ISO），再生成应答文件
                m = e["media"]
                media_path = iso
                if not iso:
                    dest = cache / m.get("filename", f"{e['id']}.iso")
                    def prog(bytes=0, bytes_total=0, **k):  # noqa: A002
                        rep(phase="download", part=1, parts=1, bytes=bytes, bytes_total=bytes_total or m.get("size") or 0, why=tr("env.preset_ms_download", m.get("edition", "")), resumed=k.get("resumed", 0))
                    r = download.fetch(m["url"], dest, size=m.get("size"), sha256=sha256 or m.get("sha256"), progress=prog)
                    result["download"] = {"parts": [{"name": dest.name, **r}], "assembled": r}
                    media_path = str(dest)
                rep(phase="seed", why=tr("env.preset_seed"))
                key = P.make_ssh_key(d / "ssh")
                seed_dir = d / "seed"
                result["windows"] = P.windows_seed(e, seed_dir, name=name, product_key=product_key, ssh_pub=key["pub"])
                (d / "credentials.json").write_text(json.dumps({k: result["windows"][k] for k in ("user", "password")}), encoding="utf-8")
                seed_ps = P.ps_seed_iso(str(seed_dir), str(d / "seed.iso"))
            steps = ([{"powershell": seed_ps, "why": tr("env.preset_seed")}] if seed_ps else []) + prov.plan_install(
                {**e, "tpm": e.get("tpm", e["kind"] == "windows-media")}, name,
                {"iso": media_path, "location": location, "memory_mb": memory_mb or e.get("memory_mb"), "cpus": cpus or e.get("cpus"),
                 "disk_gb": disk_gb or e.get("disk_gb"), "seed_iso": str(d / "seed.iso") if seed_ps else None})
            rep(phase="boot", why=tr("envs.providers.create_and_start_a_hyper_v_virtual"))
            result["results"] = providers.execute(steps)
            vm = providers.wsl_name(name)
            cfg = {**cfg_base, "backend": "hyperv", "provider": "hyperv", "network": "host", "shell": "powershell",
                   "start_steps": [{"powershell": f"Start-VM -Name {providers.ps_quote(vm)}", "elevate": True}, {"argv": ["vmconnect.exe", "localhost", vm]}]}
            _save(cfg)
        elif e["kind"] == "macos-ipsw" and pid == "macos-vz":
            from ..envs import macos
            rep(phase="download", why=tr("env.preset_ipsw"))
            seed_dir = d / "seed"; seed_dir.mkdir(exist_ok=True)
            key = P.make_ssh_key(d / "ssh")
            (seed_dir / "seed.json").write_text(json.dumps(P.seed_json(name, ssh_pub=key["pub"], extra={"node_version": (e.get("runtime") or {}).get("node", "v24.22.2")})), encoding="utf-8")
            shutil.copy(P.TEMPLATES / "macos-postinstall.sh", seed_dir / "macos-postinstall.sh")
            helper = Path.home() / "Library" / "Application Support" / "FoxOS" / "bin" / "foxvz"
            r = subprocess.run([str(helper), "install-macos", "--dir", str(d), "--disk-gb", str(disk_gb or e.get("disk_gb") or 64),
                                "--share", str(seed_dir)], capture_output=True, text=True)
            if r.returncode:
                raise FoxError("ERROR", tr("env.preset_ipsw_failed", (r.stderr or r.stdout)[-600:]))
            cfg = {**cfg_base, "backend": "macos-vz", "provider": "macos-vz", "network": "nat", "shell": "/bin/zsh", "macos_guest": True,
                   "postinstall": str(seed_dir / "macos-postinstall.sh")}
            _save(cfg)
        else:
            raise FoxError("USAGE", tr("env.preset_provider_mismatch", e["id"], pid))
    except FoxError as ex:
        _install_status(name, state="error", error=ex.message, hint=ex.hint, entry=e["id"], provider=pid)
        if not (d / "env.json").exists():
            for f in ("seed", "ssh"):
                shutil.rmtree(d / f, ignore_errors=True)
        raise
    _log(name, f"installed preset {e['id']} via {pid} by {ctx.agent}")
    ready = None
    if start and pid == "linux-kvm":
        rep(phase="boot", why=tr("env.preset_booting"))
        result["start"] = env_start(ctx, name)
        if wait_ready:
            from ..envs import kvm
            ready = P.wait_ready(d / "logs" / "serial.log", float(wait_ready), proc_alive=lambda: kvm.state(d) == "running")
            result["ready"] = ready
            if not ready:
                _install_status(name, state="error", error=tr("env.preset_not_ready", wait_ready), entry=e["id"], provider=pid)
                raise FoxError("ERROR", tr("env.preset_not_ready", wait_ready), hint=tr("common.see", d / "logs" / "serial.log"))
    _install_status(name, state="done", phase="done", ready=ready, elapsed=round(time.time() - t0, 1))
    return {"message": tr("env.preset_installed", e["name"], name, pid), "env": _summary(_cfg(name)), **result}


def _hsize(n: int) -> str:
    return f"{n / 1024 ** 3:.1f} GB" if n >= 1024 ** 3 else f"{n / 1024 ** 2:.0f} MB"


def env_install_status(ctx: Context, name: str) -> dict:
    f = env_dir(_valid(name)) / "install.json"
    if not f.exists():
        raise FoxError("NOT_FOUND", tr("env.has_no_install_record", name))
    return json.loads(f.read_text(encoding="utf-8"))


register_app("env", tr("env.foxos_environments"), tr("env.foxos_s_own_isolated_environments"),
             limits=[tr("env.the_linux_backend_runs_unprivileged"), tr("env.windows_uses_the_built_in_wsl2_macos")])
NAME = Param("name", "string", tr("env.environment_name"), required=True, positional=True, metavar="NAME")
register(Command("env", "images", tr("env.list_available_images_official"), env_images, examples=["foxos env images --json"]))
register(Command("env", "pull", tr("env.download_an_image_and_verify_its"), env_pull,
                 params=[Param("image", "string", tr("env.image"), required=True, positional=True, metavar="IMAGE"), Param("sha256", "string", tr("env.expected_sha256_recommended_for"))],
                 examples=["foxos env pull alpine-3.20", "foxos env pull ubuntu-24.04"], permission="run"))
register(Command("env", "run", tr("env.pull_if_needed_create_and_start"), env_run,
                 params=[NAME, Param("image", "string", tr("env.image_id")), Param("iso", "string", tr("env.installation_media_iso_path_hyper_v")),
                         Param("provider", "string", tr("env.use_a_specific_provider")),
                         Param("network", "string", tr("env.network_user_or_none_for_kvm"), enum=["user", "host", "none"], default="user"),
                         Param("workspace_mode", "string", tr("env.how_the_workspace_is_mounted"), enum=["rw", "ro", "none"], default="rw", cli_flag="--workspace-mode"),
                         Param("memory_mb", "integer", tr("env.memory_limit_mb")), Param("cpus", "number", tr("env.cpu_limit_cores_needs_cgroup")), Param("pids", "integer", tr("env.process_limit")),
                         Param("desktop_attach", "boolean", tr("env.attach_the_guest_desktop_after_start"), cli_flag="--desktop-attach"),
                         Param("no_start", "boolean", tr("env.only_create_do_not_start"), default=False, cli_flag="--no-start")],
                 examples=["foxos env run dev --image alpine-3.20", "foxos env run live --provider linux-kvm --iso FoxOS-0.3.0-amd64.iso --desktop-attach"],
                 permission="run"))
register(Command("env", "desktop-attach", tr("env.open_the_guest_desktop_as_a_display"), env_desktop_attach,
                 params=[NAME], examples=["foxos env desktop-attach live --json"], permission="run"))
register(Command("env", "create", tr("common.create_an_environment"), env_create,
                 params=[NAME, Param("image", "string", tr("env.image_id"), default="alpine-3.20"), Param("network", "string", tr("env.network_host_shares_the_host_network"), enum=["host", "none"], default="host"),
                         Param("workspace_mode", "string", tr("env.how_the_workspace_is_mounted"), enum=["rw", "ro", "none"], default="rw", cli_flag="--workspace-mode"),
                         Param("memory_mb", "integer", tr("env.memory_limit_mb")), Param("cpus", "number", tr("env.cpu_limit_cores_needs_cgroup")), Param("pids", "integer", tr("env.process_limit"))],
                 examples=["foxos env create dev", "foxos env create sandbox --image ubuntu-24.04 --network none --workspace-mode ro --memory-mb 1024"], permission="create"))
register(Command("env", "list", tr("env.list_environments_and_their_state"), env_list, examples=["foxos env list --json"]))
register(Command("env", "info", tr("env.environment_details_configuration"), env_info, params=[NAME], examples=["foxos env info dev --json"]))
register(Command("env", "start", tr("env.start_an_environment"), env_start, params=[NAME], examples=["foxos env start dev"], permission="run"))
register(Command("env", "stop", tr("env.stop_an_environment"), env_stop, params=[NAME, Param("timeout", "number", tr("env.seconds_to_wait_before_forcing_it_to"), default=5.0)], examples=["foxos env stop dev"], permission="run"))
register(Command("env", "restart", tr("env.restart_an_environment"), env_restart, params=[NAME], examples=["foxos env restart dev"], permission="run"))
register(Command("env", "exec", tr("env.run_a_command_in_an_environment"), env_exec,
                 params=[NAME, Param("command", "array", tr("common.command_and_arguments_after"), positional=True, items={"type": "string"}, metavar="CMD"),
                         Param("cwd", "string", tr("env.working_directory_inside_the"), default="/workspace"), Param("timeout", "number", tr("common.timeout_in_seconds"), default=600)],
                 examples=["foxos env exec dev -- uname -a", "foxos env exec dev -- sh -c 'apk add python3 && python3 -V' --json"], permission="run"))
register(Command("env", "shell", tr("env.open_an_interactive_shell_in_an"), env_shell, params=[NAME], examples=["foxos env shell dev"], permission="run"))
register(Command("env", "clone", tr("env.clone_an_environment_copies_the"), env_clone, params=[NAME, Param("new_name", "string", tr("env.new_environment_name"), required=True, positional=True, metavar="NEW_NAME")],
                 examples=["foxos env clone dev dev-copy"], permission="create"))
register(Command("env", "snapshot", tr("env.take_a_snapshot_of_a_stopped"), env_snapshot, params=[NAME, Param("label", "string", tr("env.note"))], examples=[tr("env.foxos_env_snapshot_dev_label_deps")], permission="create"))
register(Command("env", "restore", tr("env.restore_a_snapshot"), env_restore, params=[NAME, Param("snapshot", "string", tr("env.snapshot_id"), required=True, positional=True, metavar="SNAPSHOT")],
                 examples=["foxos env restore dev 20261110T213000"], permission="modify"))
register(Command("env", "export", tr("env.export_as_a_foxenv_image_tar_zstd"), env_export,
                 params=[NAME, Param("out", "string", tr("env.output_file_in_the_workspace"), required=True, path="write")], examples=["foxos env export dev --out backups/dev.foxenv"], permission="create"))
register(Command("env", "import", tr("env.import_a_foxenv_image_as_a_new"), env_import,
                 params=[Param("file", "string", tr("env.foxenv_file_in_the_workspace"), required=True, positional=True, path="read", metavar="FILE"), Param("name", "string", tr("env.new_environment_name"), required=True)],
                 examples=["foxos env import backups/dev.foxenv --name dev2"], permission="create"))
register(Command("env", "delete", tr("env.delete_an_environment_images_and_the"), env_delete, params=[NAME], examples=["foxos env delete dev-copy"], permission="delete"))
register(Command("env", "mount", tr("env.add_remove_a_host_directory_mount"), env_mount,
                 params=[NAME, Param("source", "string", tr("env.host_path"), required=True), Param("target", "string", tr("env.path_inside_the_environment"), required=True),
                         Param("readonly", "boolean", tr("env.read_only")), Param("remove", "boolean", tr("env.remove_this_mount"))],
                 examples=["foxos env mount dev --source ~/datasets --target /data --readonly"], permission="modify"))
register(Command("env", "limits", tr("env.set_resource_limits_network_and"), env_limits,
                 params=[NAME, Param("memory_mb", "integer", tr("env.memory_limit_mb_0_to_clear")), Param("cpus", "number", tr("env.cpu_limit_0_to_clear")), Param("pids", "integer", tr("env.process_limit_0_to_clear")),
                         Param("network", "string", tr("env.network"), enum=["host", "none"]), Param("workspace_mode", "string", tr("env.workspace_mount"), enum=["rw", "ro", "none"], cli_flag="--workspace-mode")],
                 examples=["foxos env limits dev --memory-mb 2048 --pids 512", "foxos env limits dev --network none"], permission="modify"))
register(Command("env", "stats", tr("env.resource_usage_processes_cpu_time"), env_stats, params=[Param("name", "string", tr("env.environment_name_all_by_default"), positional=True, metavar="NAME")],
                 examples=["foxos env stats --json"], audited=False))
register(Command("env", "logs", tr("env.environment_logs"), env_logs, params=[NAME, Param("lines", "integer", tr("env.lines"), default=100, cli_short="-n")], examples=["foxos env logs dev -n 50"]))
def env_expose(ctx: Context, name: str, ssh: str, port: int | None = None) -> dict:
    """把虚拟机的 SSH 端口转发开放到主机的所有地址（默认只在 127.0.0.1）。下次启动生效。"""
    from ..kernel import is_human
    cfg = _cfg(name)
    on = str(ssh).strip().lower() in ("on", "true", "1", "yes")
    if on and not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("env.expose_human_only"))
    cfg["ssh_expose"] = on
    if on:
        cfg["ssh_port"] = int(port or cfg.get("ssh_port") or 0) or _free_tcp_port()
    elif port is None:
        cfg.pop("ssh_port", None)
    _save(cfg)
    return {"message": tr("env.expose_ssh_on", name, cfg["ssh_port"]) if on else tr("env.expose_ssh_off", name),
            "ssh_expose": on, "ssh_port": cfg.get("ssh_port"), "restart_needed": _state(name) == "running"}


def _free_tcp_port() -> int:
    import socket as _s
    with _s.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


register(Command("env", "expose", tr("env.expose_summary"), env_expose,
                 params=[NAME, Param("ssh", "string", tr("env.expose_ssh_param"), required=True, metavar="on|off"),
                         Param("port", "integer", tr("env.expose_port_param"))],
                 examples=["foxos env expose dev --ssh on --port 2222", "foxos env expose dev --ssh off"],
                 limits=[tr("env.expose_limit")], permission="modify"))
register(Command("env", "action add", tr("env.add_a_custom_action_supports_the"), env_action_add,
                 params=[NAME, Param("action", "string", tr("env.action_name"), required=True, positional=True, metavar="ACTION"), Param("command", "string", tr("env.shell_command_run_inside_the"), required=True)],
                 examples=["foxos env action add dev test --command 'cd ${workspace} && make test'"], permission="modify"))
register(Command("env", "action run", tr("env.run_a_custom_action"), env_action_run, params=[NAME, Param("action", "string", tr("env.action_name"), required=True, positional=True, metavar="ACTION")],
                 examples=["foxos env action run dev test --json"], permission="run"))
register(Command("env", "providers", tr("env.list_environment_providers_built_in"), env_providers, examples=["foxos env providers --json"], audited=False))
register(Command("env", "doctor", tr("env.check_this_machine_s_virtualization"), env_doctor,
                 params=[Param("provider", "string", tr("env.check_only_one_provider"))], examples=["foxos env doctor --json", "foxos env doctor --provider wsl2"], audited=False))
register(Command("env", "fix", tr("env.apply_a_fix_suggested_by_doctor"), env_fix,
                 params=[Param("provider", "string", tr("env.provider"), required=True), Param("action", "string", tr("env.fix_id_see_the_doctor_output"), required=True)],
                 examples=["foxos env fix --provider wsl2 --action enable-wsl"], permission="run"))
register(Command("env", "catalog", tr("env.catalog_of_systems_you_can_install"), env_catalog,
                 params=[Param("guest", "string", tr("env.guest_system"), enum=["linux", "windows", "macos", "any"]), Param("provider", "string", tr("env.show_only_one_provider")),
                         Param("available", "boolean", tr("env.show_only_what_this_machine_can")),
                         Param("presets", "boolean", tr("env.show_only_presets"))],
                 examples=["foxos env catalog --json", "foxos env catalog --presets", "foxos env catalog --guest windows"], audited=False))
register(Command("env", "install", tr("env.install_a_system_from_the_catalog_as"), env_install,
                 params=[Param("entry", "string", tr("env.catalog_entry_id_foxos_env_catalog"), required=True, positional=True, metavar="ENTRY"), NAME,
                         Param("provider", "string", tr("env.use_a_specific_provider")), Param("url", "string", tr("env.custom_root_file_system_url_custom")), Param("sha256", "string", tr("env.sha256_of_the_custom_source")),
                         Param("iso", "string", tr("env.installation_media_iso_path_hyper_v")), Param("location", "string", tr("env.install_location_windows_folder")),
                         Param("memory_mb", "integer", tr("env.memory_mb_hyper_v_sandbox")), Param("cpus", "integer", tr("env.cpu_count_hyper_v")), Param("disk_gb", "integer", tr("env.disk_gb_hyper_v")),
                         Param("dry_run", "boolean", tr("env.only_print_the_install_plan_do_not")),
                         Param("product_key", "string", tr("env.windows_product_key")),
                         Param("start", "boolean", tr("env.start_after_install")),
                         Param("wait_ready", "number", tr("env.wait_ready_seconds"), default=0)],
                 examples=["foxos env install foxos-debian-12 dev --start --wait-ready 900", "foxos env install windows-11-enterprise-eval win11 --dry-run",
                           "foxos env install wsl-ubuntu-24.04 ubuntu", "foxos env install alpine tiny --dry-run --json", "foxos env install hyperv-windows-11-eval win11 --iso D:\\iso\\win11.iso"],
                 permission="create"))
register(Command("env", "progress", tr("env.show_install_progress"), env_install_status, params=[NAME], examples=["foxos env progress ubuntu --json"], audited=False))
