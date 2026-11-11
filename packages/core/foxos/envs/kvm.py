"""linux-kvm 提供者的执行层：KVM + cloud-hypervisor（产品路径）；本机 KVM 不可用时，
仅当显式设置 FOXOS_ALLOW_TEST_VMM=qemu-tcg 才用 QEMU TCG 做开发测试（QEMU 不是产品依赖）。
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr

# 此宿主曾出现的内核问题，探测到就不要再去创建 vCPU。
_KVM_BUG = "kvm_arch_vcpu_create"

CH_CANDIDATES = (
    os.environ.get("FOXOS_CLOUD_HYPERVISOR"),
    "/usr/lib/foxos/vmm/cloud-hypervisor",
    "/usr/bin/cloud-hypervisor",
    "/var/tmp/foxos-os/chroot/usr/lib/foxos/vmm/cloud-hypervisor",
    "/var/tmp/foxos-os/staging/vmm/cloud-hypervisor",
)


def cloud_hypervisor() -> str | None:
    for p in CH_CANDIDATES:
        if p and os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return shutil.which("cloud-hypervisor")


def _dmesg_has_kvm_bug() -> bool:
    if os.environ.get("FOXOS_KVM") == "0":
        return True
    try:
        r = subprocess.run(["dmesg"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and _KVM_BUG in r.stdout:
            return True
    except (OSError, subprocess.TimeoutExpired):
        pass
    for log in ("/var/log/kern.log", "/var/log/dmesg"):
        try:
            with open(log, errors="replace") as f:
                if _KVM_BUG in f.read():
                    return True
        except OSError:
            continue
    return False


def kvm_probe() -> dict:
    """检查 /dev/kvm 是否存在、可访问，以及此内核是否已知会在创建 vCPU 时崩溃。"""
    dev = Path("/dev/kvm")
    exists = dev.exists()
    access = bool(exists and os.access(dev, os.R_OK | os.W_OK))
    bug = _dmesg_has_kvm_bug()
    reason = None
    ok = False
    if os.environ.get("FOXOS_KVM") == "0":
        reason = tr("env.kvm_disabled_by_foxos_kvm")
    elif not exists:
        reason = tr("env.kvm_device_is_missing")
    elif not access:
        reason = tr("env.kvm_device_not_writable")
    elif bug:
        reason = tr("env.kvm_host_kernel_bug_vcpu_create")
    else:
        ok = True
    return {"available": ok, "exists": exists, "writable": access, "known_broken": bug, "reason": reason, "device": "/dev/kvm"}


def test_vmm_allowed() -> bool:
    return os.environ.get("FOXOS_ALLOW_TEST_VMM", "").strip().lower() in {"1", "true", "qemu-tcg", "qemu", "tcg"}


def qemu_bin() -> str | None:
    return shutil.which("qemu-system-x86_64")


def select_vmm() -> dict:
    """选择实际启动来宾的 VMM。产品路径是 cloud-hypervisor + KVM。"""
    kvm = kvm_probe()
    ch = cloud_hypervisor()
    if kvm["available"] and ch:
        return {"id": "cloud-hypervisor", "path": ch, "accel": "kvm", "product": True, "kvm": kvm}
    qemu = qemu_bin()
    if test_vmm_allowed() and qemu:
        reason = kvm["reason"] or tr("env.kvm_or_cloud_hypervisor_unavailable")
        return {
            "id": "qemu-tcg",
            "path": qemu,
            "accel": "tcg",
            "product": False,
            "kvm": kvm,
            "warning": tr("env.using_qemu_tcg_test_only", reason),
        }
    if not kvm["available"]:
        hint = tr("env.to_test_on_this_machine_set_foxos_allow")
        raise FoxError("DEPENDENCY_MISSING", kvm["reason"] or tr("env.kvm_is_not_available"), hint=hint)
    raise FoxError("DEPENDENCY_MISSING", tr("env.cloud_hypervisor_binary_not_found"), hint=tr("env.it_is_shipped_on_the_foxos_iso"))


def _pid_file(d: Path) -> Path:
    return d / "run" / "vmm.pid"


def _display_file(d: Path) -> Path:
    return d / "run" / "display.json"


def state(d: Path, cfg: dict | None = None) -> str:
    pf = _pid_file(d)
    try:
        pid = int(pf.read_text().strip())
    except (OSError, ValueError):
        return "stopped"
    try:
        os.kill(pid, 0)
    except OSError:
        return "stopped"
    return "running"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ovmf() -> tuple[str, str]:
    code = os.environ.get("OVMF_CODE", "/usr/share/OVMF/OVMF_CODE_4M.fd")
    vars_tpl = os.environ.get("OVMF_VARS", "/usr/share/OVMF/OVMF_VARS_4M.fd")
    if not os.path.isfile(code):
        raise FoxError("DEPENDENCY_MISSING", tr("env.ovmf_firmware_not_found", code))
    return code, vars_tpl


def start(cfg: dict, d: Path) -> dict:
    if state(d) == "running":
        return {"message": tr("env.is_already_running", cfg["name"]), "env": cfg["name"], "state": "running", "display": _read_display(d)}
    vmm = select_vmm()
    iso = cfg.get("iso")
    if iso and not os.path.isfile(iso):
        raise FoxError("NOT_FOUND", tr("env.iso_not_found", iso))
    if not iso and not cfg.get("disk") and not cfg.get("kernel"):
        raise FoxError("USAGE", tr("env.linux_kvm_needs_an_iso_a_disk_or"), hint=tr("env.foxos_env_run_name_iso_path_to"))
    (d / "run").mkdir(parents=True, exist_ok=True)
    (d / "logs").mkdir(parents=True, exist_ok=True)
    mem = int(cfg.get("limits", {}).get("memory_mb") or cfg.get("memory_mb") or 2048)
    cpus = int(cfg.get("limits", {}).get("cpus") or cfg.get("cpus") or 2)
    vnc_port = _free_port()
    way_port = _free_port()
    log = open(d / "logs" / "vmm.log", "ab")
    serial = d / "logs" / "serial.log"
    serial.write_text("", encoding="utf-8")
    if vmm["id"] == "cloud-hypervisor":
        argv = _argv_cloud_hypervisor(vmm["path"], cfg, d, mem, cpus, way_port)
        display = {"protocol": "wayvnc", "host": "127.0.0.1", "port": way_port, "kind": "guest-wayvnc", "product": True}
    else:
        argv = _argv_qemu_tcg(vmm["path"], cfg, d, mem, cpus, vnc_port, way_port, serial)
        display = {
            "protocol": "wayvnc",
            "host": "127.0.0.1",
            "port": way_port,
            "kind": "guest-wayvnc",
            "product": False,
            "vmm": "qemu-tcg",
            "warning": vmm.get("warning"),
            "note": tr("env.guest_wayvnc_listens_after_the_guest"),
        }
    proc = subprocess.Popen(argv, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
    _pid_file(d).write_text(str(proc.pid), encoding="utf-8")
    (d / "run" / "vmm.argv.json").write_text(json.dumps(argv, ensure_ascii=False, indent=1), encoding="utf-8")
    _write_json(_display_file(d), display)
    time.sleep(0.3)
    if proc.poll() is not None:
        raise FoxError("ERROR", tr("env.vmm_exited_immediately", proc.returncode), hint=tr("common.see", d / "logs" / "vmm.log"))
    return {"message": tr("env.started_linux_kvm", cfg["name"], vmm["id"]), "env": cfg["name"], "state": "running",
            "vmm": {k: vmm[k] for k in ("id", "accel", "product") if k in vmm}, "display": display, "pid": proc.pid}


def _argv_cloud_hypervisor(ch: str, cfg: dict, d: Path, mem: int, cpus: int, way_port: int) -> list[str]:
    # 产品路径：cloud-hypervisor 需要内核或支持 UEFI 的固件。ISO 走 firmware。
    argv = [ch, "--cpus", f"boot={cpus}", "--memory", f"size={mem}M", "--console", "off"]
    kernel = cfg.get("kernel")
    initrd = cfg.get("initrd")
    disk = cfg.get("disk")
    iso = cfg.get("iso")
    cmdline = cfg.get("cmdline") or "console=ttyS0 foxos.vnc"
    if kernel:
        argv += ["--kernel", kernel]
        if initrd:
            argv += ["--initramfs", initrd]
        argv += ["--cmdline", cmdline]
    if disk:
        argv += ["--disk", f"path={disk}"]
    if iso:
        argv += ["--disk", f"path={iso},readonly=on"]
        code, _vars = _ovmf()
        vars_copy = d / "run" / "OVMF_VARS.fd"
        if not vars_copy.exists():
            shutil.copy(_vars, vars_copy)
        argv += ["--firmware", code]
    # 网络：用户态 TAP 需要权限。来宾 wayvnc 经 vsock 或 virtio-net 端口；此处记录端口约定。
    argv += ["--serial", "tty"]
    net = cfg.get("network") or "user"
    if net != "none":
        # 尽量用 macvtap / tap 不作为默认（要 root）。无网络时仍可走 vsock；第一版记录端口供 desktop-attach。
        pass
    return argv


def _argv_qemu_tcg(qemu: str, cfg: dict, d: Path, mem: int, cpus: int, vnc_port: int, way_port: int, serial: Path) -> list[str]:
    argv = [qemu, "-accel", "tcg", "-m", str(mem), "-smp", str(cpus), "-machine", "q35",
            "-display", "none", "-vga", "virtio",
            "-serial", f"file:{serial}",
            "-daemonize" if False else "-nodefaults"]
    # -nodefaults can drop cdrom; don't use it. Rebuild without nodefaults.
    argv = [qemu, "-accel", "tcg", "-m", str(mem), "-smp", str(cpus), "-machine", "q35",
            "-display", "none", "-vga", "virtio",
            "-chardev", f"file,id=serial0,path={serial}", "-serial", "chardev:serial0"]
    iso = cfg.get("iso")
    disk = cfg.get("disk")
    kernel = cfg.get("kernel")
    if kernel:
        argv += ["-kernel", kernel]
        if cfg.get("initrd"):
            argv += ["-initrd", cfg["initrd"]]
        argv += ["-append", cfg.get("cmdline") or "console=ttyS0 foxos.vnc"]
    if iso:
        code, vars_tpl = _ovmf()
        vars_copy = d / "run" / "OVMF_VARS.fd"
        if not vars_copy.exists():
            shutil.copy(vars_tpl, vars_copy)
        argv += ["-drive", f"if=pflash,format=raw,readonly=on,file={code}",
                 "-drive", f"if=pflash,format=raw,file={vars_copy}",
                 "-cdrom", iso, "-boot", "d"]
    if disk:
        argv += ["-drive", f"file={disk},if=virtio,format=qcow2"]
    net = cfg.get("network") or "user"
    if net != "none":
        argv += ["-netdev", f"user,id=n0,hostfwd=tcp:127.0.0.1:{way_port}-:5900",
                 "-device", "virtio-net-pci,netdev=n0"]
    else:
        argv += ["-nic", "none"]
    return argv


def stop(cfg: dict, d: Path, timeout: float = 8.0) -> dict:
    pf = _pid_file(d)
    try:
        pid = int(pf.read_text().strip())
    except (OSError, ValueError):
        return {"message": tr("env.is_not_running", cfg["name"])}
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        try:
            pf.unlink()
        except OSError:
            pass
        return {"message": tr("env.is_not_running", cfg["name"])}
    t0 = time.time()
    while time.time() - t0 < timeout and state(d) == "running":
        time.sleep(0.1)
    if state(d) == "running":
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        time.sleep(0.1)
    try:
        pf.unlink()
    except OSError:
        pass
    return {"message": tr("common.stopped", cfg["name"])}


def _read_display(d: Path) -> dict | None:
    f = _display_file(d)
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def desktop_attach(cfg: dict, d: Path) -> dict:
    if state(d) != "running":
        raise FoxError("DEPENDENCY_MISSING", tr("env.environment_is_not_running", cfg["name"]), hint=f"foxos env start {cfg['name']}")
    display = _read_display(d) or {}
    return {
        "env": cfg["name"],
        "display": display,
        "message": tr("env.desktop_attach_ready", cfg["name"], display.get("protocol") or "none", display.get("host") or "", display.get("port") or ""),
        "viewer": "none",
    }


def exec_in(cfg: dict, d: Path, argv: list[str], cwd: str = "/", timeout: float | None = None) -> subprocess.CompletedProcess:
    """第一版：若配置了 ssh，则走 ssh；否则说明尚需来宾内的通道。"""
    ssh = cfg.get("ssh") or {}
    if ssh.get("host"):
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
        if ssh.get("port"):
            cmd += ["-p", str(ssh["port"])]
        if ssh.get("key"):
            cmd += ["-i", ssh["key"]]
        user = ssh.get("user") or "foxos"
        cmd += [f"{user}@{ssh['host']}", "sh", "-c", f"cd {cwd} && " + " ".join(argv)]
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    raise FoxError("DEPENDENCY_MISSING", tr("env.linux_kvm_exec_needs_ssh_or_vsock"), hint=tr("env.configure_ssh_on_the_guest_or_use"))
