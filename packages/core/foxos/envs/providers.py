"""环境提供者（provider）：把不同平台的隔离 / 虚拟化机制接到同一套 foxos env 命令上。

协议版本 foxos-env-provider/1，见 docs/environment-provider-protocol.md 与 data/schemas/env-provider.schema.json。
内置提供者在进程内实现同一组方法；第三方提供者是独立程序，通过 stdio 上的 JSON-RPC 2.0 通信（ExternalProvider）。

方法：
  describe()                        → {id, name, protocol, platforms, guest_os, isolation, capabilities[]}
  doctor()                          → {available, reason, checks[], actions[]}（检查并给出修复命令，如启用 WSL、需要重启）
  plan_install(entry, name, opts)   → [{argv | powershell | download, why}] 安装一个目录条目需要执行的步骤（可审阅、可记录的命令契约）
  plan(op, name, opts)              → 某个生命周期操作（start / stop / delete / exec / export / snapshot …）的步骤

内置提供者把“计划”与“执行”分开：计划是纯函数（在任何平台都能单元测试），执行只在对应平台上进行。
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from ..errors import FoxError

PROTOCOL = "foxos-env-provider/1"
CATALOG_FORMAT = "foxos-env-catalog/1"
DATA = Path(__file__).resolve().parents[1] / "data"


def host_os() -> str:
    return {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")


# ---------------------------------------------------------------- Windows 检测（输出解析为纯函数，便于用录下的真实输出测试）
HOME_EDITIONS = {"Core", "CoreN", "CoreSingleLanguage", "CoreCountrySpecific"}


def edition_supports_hyperv(edition_id: str) -> bool:
    """Windows Sandbox 与 Hyper-V 需要专业版 / 企业版 / 教育版（家庭版 EditionID 为 Core*）。"""
    return bool(edition_id) and edition_id not in HOME_EDITIONS


def decode_wsl(raw: bytes) -> str:
    """wsl.exe 的大多数输出是 UTF-16LE（无 BOM）；设置了 WSL_UTF8=1 时是 UTF-8。"""
    if raw.startswith(b"\xff\xfe") or b"\x00" in raw:
        return raw.decode("utf-16-le", "replace").replace("\ufeff", "")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-16-le", "replace") if len(raw) % 2 == 0 else raw.decode("utf-8", "replace")


# 以下正则依据 microsoft/WSL localization/strings/{en-US,zh-CN}/Resources.resw 中的原文消息
_REBOOT = r"system may need to be restarted|reboot|restart your computer|重新启动系统|需要重新启动|重启电脑"
_MISSING = (r"optional components needed to run wsl are not installed|requires the windows subsystem for linux optional component|"
            r"not installed|未安装运行 wsl 所需的可选组件|需要适用于 linux 的 windows 子系统可选组件|未安装")
_NO_VIRT = r"virtualization is not enabled|未启用虚拟化"


def parse_wsl_status(code: int, text: str) -> dict:
    """解析 `wsl.exe --status` 的结果：是否已安装、默认版本 / 发行版、是否缺组件、是否需要重启、BIOS 虚拟化是否关闭。"""
    t = text.lower()
    missing = bool(re.search(_MISSING, t))
    no_virt = bool(re.search(_NO_VIRT, t))
    m = re.search(r"(?:default version|默认版本)\s*[:：]\s*(\d)", text, re.I)
    dd = re.search(r"(?:default distribution|默认分发)\s*[:：]\s*(\S+)", text, re.I)
    return {"installed": code == 0 and not missing, "default_version": int(m.group(1)) if m else None, "default_distro": dd.group(1) if dd else None,
            "needs_reboot": bool(re.search(_REBOOT, t)), "missing_component": missing or (code != 0 and not no_virt), "virtualization_disabled": no_virt}


def parse_wsl_online(text: str) -> list[dict]:
    """解析 `wsl.exe --list --online` 的表格（NAME / FRIENDLY NAME）。"""
    out, started = [], False
    for line in text.replace("\x00", "").splitlines():
        if re.match(r"^\s*NAME\s+FRIENDLY NAME", line):
            started = True
            continue
        if started and line.strip():
            parts = re.split(r"\s{2,}", line.strip(), maxsplit=1)
            if len(parts) == 2:
                out.append({"name": parts[0].lstrip("* "), "friendly": parts[1]})
    return out


def is_reboot_required(code: int, text: str) -> bool:
    """3010 = ERROR_SUCCESS_REBOOT_REQUIRED；“请重启 WSL”之类不算重启电脑。"""
    return code == 3010 or bool(re.search(_REBOOT, text, re.I))


def wsl_name(name: str) -> str:
    return f"foxos-{name}"


def wsb_xml(workspace_host: str, *, networking: bool = True, memory_mb: int | None = None, readonly: bool = False,
            logon_command: str | None = None, vgpu: bool = False) -> str:
    """生成 Windows Sandbox 配置（.wsb）：把工作空间映射到沙箱桌面的 C:\\Users\\WDAGUtilityAccount\\Desktop\\workspace。"""
    from xml.sax.saxutils import escape
    lines = ["<Configuration>", f"  <VGpu>{'Enable' if vgpu else 'Disable'}</VGpu>", f"  <Networking>{'Enable' if networking else 'Disable'}</Networking>",
             "  <MappedFolders>", "    <MappedFolder>", f"      <HostFolder>{escape(workspace_host)}</HostFolder>",
             "      <SandboxFolder>C:\\Users\\WDAGUtilityAccount\\Desktop\\workspace</SandboxFolder>",
             f"      <ReadOnly>{'true' if readonly else 'false'}</ReadOnly>", "    </MappedFolder>", "  </MappedFolders>"]
    if memory_mb:
        lines.append(f"  <MemoryInMB>{int(memory_mb)}</MemoryInMB>")
    if logon_command:
        lines += ["  <LogonCommand>", f"    <Command>{escape(logon_command)}</Command>", "  </LogonCommand>"]
    lines.append("</Configuration>")
    return "\n".join(lines) + "\n"


def ps_quote(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


# ---------------------------------------------------------------- 提供者
class Provider:
    id = ""
    name = ""
    platforms: list[str] = []
    guest_os = "linux"
    isolation = "full"  # full：独立发行版 / 虚拟机；light：进程级沙箱
    capabilities: list[str] = []

    def describe(self) -> dict:
        return {"id": self.id, "name": self.name, "protocol": PROTOCOL, "platforms": self.platforms, "guest_os": self.guest_os,
                "isolation": self.isolation, "capabilities": self.capabilities, "builtin": True,
                "host_supported": host_os() in self.platforms}

    def doctor(self) -> dict:
        if host_os() not in self.platforms:
            return {"available": False, "reason": f"需要 {'/'.join(self.platforms)} 宿主", "checks": [], "actions": []}
        return {"available": True, "reason": None, "checks": [], "actions": []}

    def plan_install(self, entry: dict, name: str, opts: dict) -> list[dict]:
        raise FoxError("USAGE", f"{self.id} 不支持安装目录条目")


class LinuxNs(Provider):
    id = "linux-ns"
    name = "Linux 命名空间（狐狸OS 自研运行时）"
    platforms = ["linux"]
    capabilities = ["create", "start", "stop", "exec", "shell", "snapshot", "restore", "clone", "export", "import", "mount", "limits", "stats", "logs", "agent"]

    def doctor(self) -> dict:
        d = super().doctor()
        if not d["available"]:
            return d
        checks = []
        ok = subprocess.run(["unshare", "-U", "true"], capture_output=True).returncode == 0 if shutil.which("unshare") else None
        checks.append({"id": "userns", "ok": ok, "detail": "无特权用户命名空间" + ("可用" if ok else "不可用（内核或 sysctl kernel.unprivileged_userns_clone 禁止）")})
        try:
            import zstandard  # noqa: F401
            checks.append({"id": "zstd", "ok": True, "detail": "zstandard 可用"})
        except ImportError:
            checks.append({"id": "zstd", "ok": False, "detail": "缺少 Python 包 zstandard"})
        return {"available": bool(ok), "reason": None if ok else "用户命名空间不可用", "checks": checks, "actions": []}

    def plan_install(self, entry, name, opts):
        src = opts.get("_resolved") or entry["source"]
        if not src.get("url"):
            raise FoxError("USAGE", f"{entry['id']} 在 Linux 后端上需要可下载的根文件系统")
        image_id = re.sub(r"[^a-z0-9.-]+", "-", Path(src["url"].split("?")[0]).name.lower()).strip("-")[:60]
        pull = ["env", "pull", src["url"]] + (["--sha256", src["sha256"]] if src.get("sha256") else [])
        ws = opts.get("workspace")
        return [{"foxos": pull, "why": "下载并校验根文件系统", "workspace": ws},
                {"foxos": ["env", "create", name, "--image", image_id], "why": "创建环境", "registers": name, "workspace": ws}]


class Wsl2(Provider):
    id = "wsl2"
    name = "WSL2（适用于 Linux 的 Windows 子系统）"
    platforms = ["windows"]
    capabilities = ["create", "start", "stop", "exec", "shell", "export", "import", "delete", "list-online", "agent"]

    def doctor(self) -> dict:
        d = super().doctor()
        if not d["available"]:
            return d
        try:
            r = subprocess.run(["wsl.exe", "--status"], capture_output=True, timeout=60)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            r = None
        st = parse_wsl_status(r.returncode, decode_wsl(r.stdout + r.stderr)) if r else {"installed": False, "needs_reboot": False, "missing_component": True}
        actions = []
        if not st["installed"]:
            actions.append({"id": "enable-wsl", "label": "启用 WSL（需要管理员权限，完成后可能需要重启）", "argv": ["wsl.exe", "--install", "--no-distribution"], "elevate": True})
        if st.get("virtualization_disabled"):
            actions.append({"id": "bios", "label": "在电脑固件（BIOS/UEFI）设置里开启虚拟化（Intel VT-x / AMD-V），并运行 wsl --install --no-distribution", "manual": True})
        if st.get("needs_reboot"):
            actions.append({"id": "reboot", "label": "重启电脑以完成 WSL 安装", "argv": ["shutdown.exe", "/r", "/t", "0"], "confirm": True})
        return {"available": st["installed"] and not st.get("needs_reboot"), "reason": None if st["installed"] else "WSL 未安装或未启用",
                "checks": [{"id": "wsl", "ok": st["installed"], "detail": json.dumps(st, ensure_ascii=False)}], "actions": actions}

    def plan_install(self, entry, name, opts):
        src = opts.get("_resolved") or entry["source"]
        base = opts.get("location") or os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Public"), "FoxOS", "envs", name)
        if src["kind"] == "wsl-store":
            # 只在应用商店提供的旧式发行版：由 wsl.exe 安装，发行版名由 WSL 决定
            return [{"argv": ["wsl.exe", "--install", "-d", src["wsl_name"], "--no-launch"], "why": f"用 WSL 官方渠道安装 {entry['name']}", "registers": src["wsl_name"]}]
        if not src.get("url"):
            raise FoxError("USAGE", f"{entry['id']} 需要先解析下载地址")
        fname = os.path.basename(src["url"].split("?")[0]) or "rootfs.tar"
        file = os.path.join(base, fname)
        dl = {"download": src["url"], "to": file, "sha256": src.get("sha256"), "why": f"下载 {entry['name']} 根文件系统并校验 sha256"}
        if src.get("wsl_import_needs_convert"):
            dl["convert"] = "tar.gz"
            file = file.rsplit(".tar.xz", 1)[0] + ".tar.gz"
        return [
            dl,
            {"argv": ["wsl.exe", "--import", wsl_name(name), os.path.join(base, "disk"), file, "--version", "2"], "why": "导入为 WSL2 发行版", "registers": wsl_name(name)},
            {"argv": ["wsl.exe", "-d", wsl_name(name), "--exec", "/bin/sh", "-c", "true"], "why": "首次启动检查"},
        ]


class WindowsSandbox(Provider):
    id = "windows-sandbox"
    name = "Windows Sandbox（一次性 Windows 桌面）"
    platforms = ["windows"]
    guest_os = "windows"
    capabilities = ["create", "start", "delete"]

    def doctor(self) -> dict:
        d = super().doctor()
        if not d["available"]:
            return d
        ed = _edition()
        exe = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "WindowsSandbox.exe"
        checks = [{"id": "edition", "ok": edition_supports_hyperv(ed), "detail": f"Windows 版本 EditionID={ed or '未知'}（家庭版不支持）"},
                  {"id": "feature", "ok": exe.exists(), "detail": str(exe)}]
        actions = [] if exe.exists() or not edition_supports_hyperv(ed) else [
            {"id": "enable-sandbox", "label": "启用 Windows Sandbox（管理员，完成后需要重启）", "elevate": True,
             "powershell": "Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -All -NoRestart"}]
        ok = exe.exists() and edition_supports_hyperv(ed)
        return {"available": ok, "reason": None if ok else ("家庭版不支持 Windows Sandbox" if not edition_supports_hyperv(ed) else "Windows Sandbox 未启用"), "checks": checks, "actions": actions}

    def plan_install(self, entry, name, opts):
        wsb = os.path.join(opts.get("location") or os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Public"), "FoxOS", "envs"), f"{name}.wsb")
        xml = wsb_xml(opts.get("workspace") or "", networking=opts.get("network", "host") != "none", memory_mb=opts.get("memory_mb"), readonly=opts.get("workspace_mode") == "ro")
        return [{"write": wsb, "content": xml, "why": "生成 Windows Sandbox 配置"}, {"argv": ["cmd.exe", "/c", "start", "", wsb], "why": "启动沙箱（关闭窗口后内容全部丢弃）"}]


class HyperV(Provider):
    id = "hyperv"
    name = "Hyper-V 虚拟机"
    platforms = ["windows"]
    guest_os = "windows"
    capabilities = ["create", "start", "stop", "delete", "snapshot", "restore", "export", "import", "limits"]

    def doctor(self) -> dict:
        d = super().doctor()
        if not d["available"]:
            return d
        ed = _edition()
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "if (Get-Command New-VM -ErrorAction SilentlyContinue) { 'yes' } else { 'no' }"], capture_output=True, text=True)
        has = r.stdout.strip() == "yes"
        actions = [] if has or not edition_supports_hyperv(ed) else [
            {"id": "enable-hyperv", "label": "启用 Hyper-V（管理员，完成后需要重启）", "elevate": True,
             "powershell": "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -All -NoRestart"}]
        return {"available": has, "reason": None if has else ("家庭版不支持 Hyper-V" if not edition_supports_hyperv(ed) else "Hyper-V 未启用"),
                "checks": [{"id": "edition", "ok": edition_supports_hyperv(ed), "detail": f"EditionID={ed or '未知'}"}, {"id": "cmdlets", "ok": has, "detail": "Hyper-V PowerShell 模块"}], "actions": actions}

    def plan_install(self, entry, name, opts):
        iso = opts.get("iso") or entry["source"].get("iso")
        if not iso:
            raise FoxError("USAGE", "Hyper-V 虚拟机需要安装介质：--iso <Windows 或 Linux ISO 路径>",
                           hint=entry["source"].get("download_page") and f"官方下载页：{entry['source']['download_page']}")
        vm = wsl_name(name)
        base = opts.get("location") or os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Documents", "Hyper-V", "FoxOS", name)
        mem = int(opts.get("memory_mb") or 4096) * 1024 * 1024
        disk = int(opts.get("disk_gb") or 64) * 1024 ** 3
        cpus = int(opts.get("cpus") or 2)
        ps = "; ".join([
            f"New-VM -Name {ps_quote(vm)} -Generation 2 -MemoryStartupBytes {mem} -NewVHDPath {ps_quote(os.path.join(base, vm + '.vhdx'))} -NewVHDSizeBytes {disk} -Path {ps_quote(base)} -SwitchName 'Default Switch'",
            f"Set-VMProcessor -VMName {ps_quote(vm)} -Count {cpus}",
            f"Add-VMDvdDrive -VMName {ps_quote(vm)} -Path {ps_quote(iso)}",
            f"Set-VMFirmware -VMName {ps_quote(vm)} -FirstBootDevice (Get-VMDvdDrive -VMName {ps_quote(vm)})" + ("" if entry.get("secure_boot", True) else " -EnableSecureBoot Off"),
            f"Set-VMKeyProtector -VMName {ps_quote(vm)} -NewLocalKeyProtector; Enable-VMTPM -VMName {ps_quote(vm)}" if entry.get("tpm") else "$null",
            f"Start-VM -Name {ps_quote(vm)}",
        ])
        return [{"powershell": ps, "elevate": True, "why": "用 Hyper-V 创建并启动虚拟机（从 ISO 引导，按安装程序提示完成安装）"},
                {"argv": ["vmconnect.exe", "localhost", vm], "why": "打开虚拟机控制台"}]


class MacVZ(Provider):
    id = "macos-vz"
    name = "Virtualization.framework（macOS）"
    platforms = ["macos"]
    capabilities = ["create", "start", "stop", "exec"]

    def doctor(self) -> dict:
        d = super().doctor()
        if not d["available"]:
            return d
        helper = Path.home() / "Library" / "Application Support" / "FoxOS" / "bin" / "foxvz"
        return {"available": helper.exists(), "reason": None if helper.exists() else "FoxVZ 辅助程序未编译（安装向导 → 环境）",
                "checks": [{"id": "helper", "ok": helper.exists(), "detail": str(helper)}], "actions": []}


class MacGuestUnavailable(Provider):
    """macOS 来宾：Apple 许可只允许在 Apple 硬件上的 macOS 里虚拟化 macOS。"""
    id = "macos-guest"
    name = "macOS 来宾（仅 Apple 硬件）"
    platforms = ["macos"]
    guest_os = "macos"
    capabilities = []

    def doctor(self) -> dict:
        if host_os() != "macos":
            return {"available": False, "reason": "Apple 的软件许可只允许在 Apple 硬件上运行的 macOS 中虚拟化 macOS；Windows / Linux 宿主上不提供", "checks": [], "actions": []}
        return {"available": False, "reason": "计划中：在 Apple 芯片的 Mac 上通过 Virtualization.framework（VZMacOSInstaller）实现，当前版本尚未实现", "checks": [], "actions": []}


class ExternalProvider(Provider):
    """第三方提供者：独立程序，stdio 上的 JSON-RPC 2.0（每行一条消息）。清单文件 provider.json 见协议文档。"""

    def __init__(self, manifest: dict, path: Path):
        self.manifest = manifest
        self.dir = path
        self.id = manifest["id"]
        self.name = manifest.get("name", self.id)
        self.platforms = manifest.get("platforms", [])
        self.guest_os = manifest.get("guest_os", "linux")
        self.isolation = manifest.get("isolation", "full")
        self.capabilities = manifest.get("capabilities", [])

    def call(self, method: str, params: dict | None = None, timeout: float = 600) -> dict:
        cmd = [str(self.dir / c) if i == 0 and not os.path.isabs(c) and (self.dir / c).exists() else c for i, c in enumerate(self.manifest["command"])]
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocol": PROTOCOL, "client": "foxos"}},
                {"jsonrpc": "2.0", "id": 2, "method": method, "params": params or {}}]
        try:
            r = subprocess.run(cmd, input="".join(json.dumps(m) + "\n" for m in msgs), capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise FoxError("DEPENDENCY_MISSING", f"无法运行提供者 {self.id}：{e}") from e
        replies = {}
        for line in r.stdout.splitlines():
            try:
                m = json.loads(line)
                replies[m.get("id")] = m
            except ValueError:
                continue
        init = replies.get(1, {}).get("result") or {}
        if init.get("protocol") != PROTOCOL:
            raise FoxError("CONFLICT", f"提供者 {self.id} 的协议版本 {init.get('protocol')!r} 不受支持（需要 {PROTOCOL}）")
        rep = replies.get(2) or {}
        if "error" in rep:
            raise FoxError(rep["error"].get("data", {}).get("code", "ERROR"), rep["error"].get("message", "提供者返回错误"))
        return rep.get("result") or {}

    def describe(self) -> dict:
        return {**super().describe(), "builtin": False, "path": str(self.dir)}

    def doctor(self) -> dict:
        return self.call("doctor")

    def plan_install(self, entry, name, opts):
        return self.call("plan_install", {"entry": entry, "name": name, "opts": opts}).get("steps", [])


def _edition() -> str:
    if host_os() != "windows":
        return ""
    try:
        import winreg  # type: ignore
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as k:
            return winreg.QueryValueEx(k, "EditionID")[0]
    except OSError:
        return ""


BUILTIN = [LinuxNs(), Wsl2(), WindowsSandbox(), HyperV(), MacVZ(), MacGuestUnavailable()]


def external_dirs() -> list[Path]:
    from ..desktop_client import foxos_home
    base = foxos_home() / "providers"
    return sorted(p for p in base.iterdir() if (p / "provider.json").exists()) if base.is_dir() else []


def providers() -> dict[str, Provider]:
    out = {p.id: p for p in BUILTIN}
    for d in external_dirs():
        try:
            m = json.loads((d / "provider.json").read_text(encoding="utf-8"))
            if m.get("protocol") == PROTOCOL and m.get("id") and m["id"] not in out:
                out[m["id"]] = ExternalProvider(m, d)
        except (OSError, ValueError):
            continue
    return out


def get(pid: str) -> Provider:
    p = providers().get(pid)
    if not p:
        raise FoxError("NOT_FOUND", f"没有提供者 {pid}", hint="foxos env providers")
    return p


# ---------------------------------------------------------------- 目录
def catalog() -> dict:
    c = json.loads((DATA / "env-catalog.json").read_text(encoding="utf-8"))
    if c.get("format") != CATALOG_FORMAT:
        raise FoxError("CONFLICT", f"目录格式 {c.get('format')} 不受支持")
    return c


def entry(eid: str) -> dict:
    for e in catalog()["entries"]:
        if e["id"] == eid:
            return e
    raise FoxError("NOT_FOUND", f"目录里没有 {eid}", hint="foxos env catalog")


# ---------------------------------------------------------------- 动态来源解析（LXC 每日构建、Alpine 最新版、CHECKSUM 文件）
def parse_lxc_index(text: str, distro: str, release: str, arch: str = "amd64", variant: str = "default") -> str | None:
    """解析 LXC 镜像服务器的 meta/1.0/index-system，返回最新构建目录（如 /images/oracle/9/amd64/default/20261110_07:52/）。"""
    best = None
    for line in text.splitlines():
        p = line.strip().split(";")
        if len(p) == 6 and p[:4] == [distro, release, arch, variant]:
            if best is None or p[4] > best[0]:
                best = (p[4], p[5])
    return best[1] if best else None


def parse_alpine_releases(text: str, flavor: str = "alpine-minirootfs") -> dict | None:
    """解析 Alpine 的 latest-releases.yaml，取 minirootfs 的文件名与 sha256（避免依赖 YAML 库）。"""
    for block in re.split(r"^-\s*$", text, flags=re.M):
        kv = dict(re.findall(r"^\s+(\w+):\s*(.+?)\s*$", block, flags=re.M))
        if kv.get("flavor") == flavor and kv.get("file"):
            return {"file": kv["file"], "sha256": kv.get("sha256"), "version": kv.get("version"), "size": int(kv["size"]) if kv.get("size", "").isdigit() else None}
    return None


def parse_checksum(text: str, filename: str) -> str | None:
    """支持 `sha  file`、`SHA256 (file) = sha` 两种格式。"""
    for line in text.splitlines():
        m = re.match(r"^SHA256 \((.+)\) = ([0-9a-fA-F]{64})", line.strip())
        if m and m.group(1) == filename:
            return m.group(2).lower()
        parts = line.split()
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) and parts[-1].lstrip("*") == filename:
            return parts[0].lower()
    return None


def _get(url: str, timeout: float = 30) -> str:
    import urllib.request
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "foxos-env"}), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def resolve_source(entry: dict, opts: dict | None = None, fetch=_get) -> dict:
    """把目录条目的来源解析成具体的 {url, sha256, format}。fetch 可替换，便于用录下的服务器响应测试。"""
    opts = opts or {}
    src = dict(entry.get("source") or {})
    kind = src.get("kind")
    arm = os.environ.get("PROCESSOR_ARCHITECTURE", platform.machine()).lower() in ("arm64", "aarch64")
    if kind == "custom":
        if not opts.get("url"):
            raise FoxError("USAGE", "自定义系统需要 --url（https 地址或本地 .tar/.tar.gz/.tar.xz/.wsl 文件）")
        src.update(url=opts["url"], sha256=opts.get("sha256"))
    elif kind == "rootfs":
        if arm and src.get("arm64"):
            src.update(src["arm64"])
        if not src.get("sha256") and src.get("sha256_url"):
            fname = src["url"].rsplit("/", 1)[-1]
            src["sha256"] = parse_checksum(fetch(src["sha256_url"]), fname)
    elif kind == "alpine":
        a = "aarch64" if arm else "x86_64"
        base = f"https://dl-cdn.alpinelinux.org/alpine/{src.get('branch', 'latest-stable')}/releases/{a}/"
        rel = parse_alpine_releases(fetch(base + "latest-releases.yaml"))
        if not rel:
            raise FoxError("ERROR", "无法解析 Alpine 最新版本信息")
        src.update(url=base + rel["file"], sha256=rel["sha256"], version=rel.get("version"))
    elif kind == "lxc":
        server = src["server"].rstrip("/")
        path = parse_lxc_index(fetch(f"{server}/meta/1.0/index-system"), src["distro"], src["release"], "arm64" if arm else "amd64", src.get("variant", "default"))
        if not path:
            raise FoxError("NOT_FOUND", f"LXC 镜像服务器上没有 {src['distro']} {src['release']}")
        src.update(url=f"{server}{path}rootfs.tar.xz", sha256=parse_checksum(fetch(f"{server}{path}SHA256SUMS"), "rootfs.tar.xz"))
    if src.get("url"):
        u = src["url"].split("?")[0].lower()
        src["format"] = "tar.xz" if u.endswith((".tar.xz", ".txz")) else "tar.gz" if u.endswith((".tar.gz", ".tgz", ".wsl")) else "tar" if u.endswith(".tar") else "unknown"
        # wsl --import 接受 tar / tar.gz；xz 需先转换
        src["wsl_import_needs_convert"] = src["format"] == "tar.xz"
    return src


# ---------------------------------------------------------------- 计划执行
def ps_elevated(script: str) -> list[str]:
    """以管理员身份运行一段 PowerShell（触发 UAC 确认），等待结束并返回其退出码。"""
    inner = script.replace("'", "''")
    return ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"$p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command','{inner}'; exit $p.ExitCode"]


def step_argv(step: dict) -> list[str] | None:
    if "argv" in step:
        a = step["argv"]
        if step.get("elevate"):
            args = ",".join(ps_quote(x) for x in a[1:]) or "@()"
            return ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                    f"$p = Start-Process -FilePath {ps_quote(a[0])} -ArgumentList {args} -Verb RunAs -Wait -PassThru; exit $p.ExitCode"]
        return a
    if "powershell" in step:
        return ps_elevated(step["powershell"]) if step.get("elevate") else ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", step["powershell"]]
    return None


def convert_xz_to_gz(src: Path, dst: Path) -> None:
    import gzip
    import lzma
    with lzma.open(src, "rb") as i, gzip.open(dst, "wb", compresslevel=3) as o:
        shutil.copyfileobj(i, o, 1 << 20)


def execute(steps: list[dict], report=lambda **k: None) -> list[dict]:
    """逐步执行计划；download 步骤校验 sha256，失败立即停止。返回每步结果。"""
    from . import images
    results = []
    for i, s in enumerate(steps):
        report(step=i, total=len(steps), why=s.get("why"), state="running")
        if "download" in s:
            to = Path(s["to"])
            to.parent.mkdir(parents=True, exist_ok=True)
            src = s["download"]
            if Path(src).exists():
                shutil.copy2(src, to)
            else:
                images._fetch(src, to, lambda got, tot: report(step=i, total=len(steps), why=s.get("why"), state="running", bytes=got, bytes_total=tot))
            got = images._sha256(to)
            if s.get("sha256") and got != s["sha256"].lower():
                to.unlink(missing_ok=True)
                raise FoxError("CONFLICT", f"sha256 不匹配：期望 {s['sha256']}，实际 {got}")
            if s.get("convert") == "tar.gz":
                gz = to.with_name(to.name.rsplit(".tar.xz", 1)[0] + ".tar.gz")
                convert_xz_to_gz(to, gz)
                to.unlink()
            results.append({"step": i, "ok": True, "sha256": got, "verified": bool(s.get("sha256"))})
        elif "write" in s:
            Path(s["write"]).parent.mkdir(parents=True, exist_ok=True)
            Path(s["write"]).write_text(s["content"], encoding="utf-8")
            results.append({"step": i, "ok": True, "path": s["write"]})
        elif "foxos" in s:
            env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(Path(__file__).resolve().parents[2]), os.environ.get("PYTHONPATH")]))}
            if s.get("workspace"):
                env["FOXOS_WORKSPACE"] = s["workspace"]
            r = subprocess.run([sys.executable, "-m", "foxos", *s["foxos"], "--json"], capture_output=True, text=True, env=env)
            if r.returncode:
                raise FoxError("ERROR", f"步骤失败：foxos {' '.join(s['foxos'])}：{(r.stdout + r.stderr)[-800:]}")
            results.append({"step": i, "ok": True})
        else:
            argv = step_argv(s)
            r = subprocess.run(argv, capture_output=True)
            out = decode_wsl(r.stdout + r.stderr)
            if r.returncode and not (s.get("ok_codes") and r.returncode in s["ok_codes"]):
                if is_reboot_required(r.returncode, out):
                    raise FoxError("CONFLICT", "需要重启电脑才能继续", hint="重启后在“环境 → 安装系统”里重试")
                raise FoxError("ERROR", f"步骤失败（退出码 {r.returncode}）：{out.strip()[-800:]}")
            results.append({"step": i, "ok": True, "output": out.strip()[-2000:], "reboot_required": is_reboot_required(r.returncode, out)})
        report(step=i, total=len(steps), why=s.get("why"), state="done")
    return results
