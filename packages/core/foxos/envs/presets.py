"""狐狸OS 预设系统：在线选择并安装「已经配置好」的 Linux / Windows / macOS 环境。

预设 = 桌面 + 默认中文 + 智能体运行时（Node / Bun / Python）+ ACP 智能体 + foxos 来宾桥。

| 种类 | 来源 | 狐狸OS 主机（Linux，KVM） | Windows 伴侣（Hyper-V / WSL2） | macOS 主机 |
| --- | --- | --- | --- | --- |
| foxos-image | 我们在 GitHub Releases 发布的 qcow2（分卷）与 WSL 根文件系统 | linux-kvm（UEFI 磁盘 + 种子光盘） | wsl2（wsl --import） | 不提供（x86_64 镜像） |
| foxos-iso | 狐狸OS 可引导 ISO（分卷） | linux-kvm（从 ISO 引导） | hyperv（第 2 代虚拟机） | 不提供 |
| windows-media | 安装时从微软官方下载评估版 ISO，再用 autounattend.xml + 首次登录脚本应用预设 | 不提供（cloud-hypervisor 不能从安装光盘装 Windows） | hyperv | 不提供 |
| macos-ipsw | 在 Apple 芯片 Mac 上由 Virtualization.framework 下载 Apple 官方 IPSW | 不提供（Apple 许可） | 不提供（Apple 许可） | macos-vz |

微软不允许再分发预装好的 Windows 镜像，Apple 只允许在 Apple 硬件上虚拟化 macOS，所以这两类只发布「配方」，介质都在安装时从官方下载。
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import socket
import subprocess
import time
from pathlib import Path
from xml.sax.saxutils import escape

from ..errors import FoxError
from ..i18n import tr
from . import download

DATA = Path(__file__).resolve().parents[1] / "data"
PRESETS_FILE = DATA / "env-presets.json"
TEMPLATES = DATA / "presets"
FORMAT = "foxos-env-presets/1"


def catalog() -> dict:
    # FOXOS_PRESETS_FILE：测试或镜像站用的替代目录（同一格式）
    d = json.loads(Path(os.environ.get("FOXOS_PRESETS_FILE") or PRESETS_FILE).read_text(encoding="utf-8"))
    if d.get("format") != FORMAT:
        raise FoxError("CONFLICT", tr("envs.presets.bad_format", d.get("format"), FORMAT))
    return d


def entries() -> list[dict]:
    c = catalog()
    base = (os.environ.get("FOXOS_PRESETS_BASE") or c.get("release_base", "")).rstrip("/")
    out = []
    for e in c["entries"]:
        e = json.loads(json.dumps(e))
        for art in (e.get("artifacts") or {}).values():
            rel = art.get("release") or e.get("release")
            for p in [art, *art.get("parts", [])]:
                if "name" in p and "url" not in p and rel:
                    p["url"] = f"{base}/{rel}/{p['name']}"
        e["preset"] = True
        out.append(e)
    return out


def get(pid: str) -> dict | None:
    return next((e for e in entries() if e["id"] == pid), None)


# ------------------------------------------------------------------ 主机与可用性

def _arch() -> str:
    import platform
    m = platform.machine().lower()
    return "aarch64" if m in ("arm64", "aarch64") else "x86_64"


def target(e: dict, host: str, arch: str | None = None) -> dict:
    """返回 {provider, artifact, available, reason}：这台主机用哪个提供者、下载哪个文件。"""
    arch = arch or _arch()
    hosts = e.get("hosts") or {}
    h = hosts.get(host)
    if not h:
        reason = (e.get("unavailable") or {}).get(host) or tr("envs.presets.not_on_this_host", host)
        return {"provider": None, "artifact": None, "available": False, "reason": reason}
    if h.get("arch") and arch not in h["arch"]:
        return {"provider": h["provider"], "artifact": h.get("artifact"), "available": False,
                "reason": tr("envs.presets.needs_arch", "/".join(h["arch"]), arch)}
    return {"provider": h["provider"], "artifact": h.get("artifact"), "available": True, "reason": None}


def sizes(e: dict, artifact: str | None) -> dict:
    """下载大小与需要的磁盘空间（字节）。"""
    art = (e.get("artifacts") or {}).get(artifact or "") or {}
    dl = int(art.get("size") or 0)
    if e["kind"] == "foxos-image" and artifact == "qcow2":
        # 分卷 + 拼好的 qcow2 同时存在一会儿，之后来宾磁盘按需增长到 disk_gb
        need = dl * 2 + int(e.get("disk_gb") or 8) * 1024 ** 3
    elif e["kind"] == "foxos-image":
        need = dl + int(e.get("disk_gb") or 8) * 1024 ** 3
    elif e["kind"] == "foxos-iso":
        need = dl * 2
    elif e["kind"] == "windows-media":
        dl = int((e.get("media") or {}).get("size") or 0)
        need = dl + int(e.get("disk_gb") or 64) * 1024 ** 3
    else:
        dl = int((e.get("media") or {}).get("size") or 0)
        need = dl + int(e.get("disk_gb") or 64) * 1024 ** 3
    return {"download_bytes": dl, "disk_bytes": need}


def describe(e: dict, host: str) -> dict:
    t = target(e, host)
    s = sizes(e, t["artifact"])
    return {**e, "host_providers": [t["provider"]] if t["provider"] else [], "installable": t["available"],
            **({"reason": t["reason"]} if not t["available"] else {}), "target": t, **s}


# ------------------------------------------------------------------ 种子（用户、SSH 公钥、语言），来宾里的 foxos 桥读它

def make_ssh_key(d: Path) -> dict:
    d.mkdir(parents=True, exist_ok=True)
    key = d / "id_ed25519"
    if not key.exists():
        kg = shutil.which("ssh-keygen")
        if not kg:
            return {"key": None, "pub": None}
        subprocess.run([kg, "-q", "-t", "ed25519", "-N", "", "-C", "foxos-env", "-f", str(key)], check=True)
    return {"key": str(key), "pub": (d / "id_ed25519.pub").read_text().strip()}


def seed_json(name: str, *, user: str = "foxos", ssh_pub: str | None, lang: str = "zh_CN.UTF-8", timezone: str = "Asia/Shanghai", extra: dict | None = None) -> dict:
    return {"format": "foxos-seed/1", "user": user, "hostname": f"foxos-{name}"[:63], "ssh_authorized_key": ssh_pub,
            "lang": lang, "timezone": timezone, **(extra or {})}


def iso_tool() -> list[str] | None:
    for t in ("xorriso", "genisoimage", "mkisofs"):
        p = shutil.which(t)
        if p:
            return [p, "-as", "mkisofs"] if t == "xorriso" else [p]
    return None


def make_seed_iso(src_dir: Path, out: Path) -> Path:
    tool = iso_tool()
    if not tool:
        raise FoxError("DEPENDENCY_MISSING", tr("envs.presets.no_iso_tool"), hint="sudo apt install xorriso")
    r = subprocess.run([*tool, "-quiet", "-V", "FOXOSSEED", "-J", "-r", "-o", str(out), str(src_dir)], capture_output=True, text=True)
    if r.returncode:
        raise FoxError("ERROR", tr("envs.presets.seed_iso_failed", (r.stderr or r.stdout)[-400:]))
    return out


# ------------------------------------------------------------------ Windows：应答文件与首次登录脚本

def windows_answer(e: dict, *, user: str, password: str, product_key: str | None, computer: str) -> str:
    tpl = (TEMPLATES / "autounattend.xml.tpl").read_text(encoding="utf-8")
    m = e.get("media") or {}
    pk = ""
    if product_key:
        pk = f"        <ProductKey><Key>{escape(product_key.strip())}</Key><WillShowUI>OnError</WillShowUI></ProductKey>"
    return tpl.format(ui_language=m.get("language", "zh-CN"), input_locale=m.get("input_locale", "0804:00000804"),
                      image_index=int(m.get("image_index") or 1), product_key_block=pk, computer_name=escape(computer[:15]),
                      timezone=m.get("timezone", "China Standard Time"), user=escape(user), password=escape(password))


def windows_seed(e: dict, d: Path, *, name: str, product_key: str | None, ssh_pub: str | None) -> dict:
    """写 autounattend.xml、foxos/postinstall.ps1、foxos/seed.json 到 d（之后做成 FOXOSSEED 光盘）。"""
    d.mkdir(parents=True, exist_ok=True)
    (d / "foxos").mkdir(exist_ok=True)
    password = secrets.token_urlsafe(12)
    computer = ("FOXOS-" + name.upper().replace("_", "-"))[:15]
    (d / "autounattend.xml").write_text(windows_answer(e, user="foxos", password=password, product_key=product_key, computer=computer), encoding="utf-8")
    shutil.copy(TEMPLATES / "postinstall.ps1", d / "foxos" / "postinstall.ps1")
    rt = e.get("runtime") or {}
    seed = seed_json(name, ssh_pub=ssh_pub, extra={"node_version": rt.get("node", "v24.22.2"), "python_version": rt.get("python", "3.13.9"),
                                                   "companion_install": rt.get("companion_install")})
    (d / "foxos" / "seed.json").write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"user": "foxos", "password": password, "computer": computer, "product_key": bool(product_key)}


def ps_seed_iso(src: str, out: str) -> str:
    """Windows 上没有 mkisofs：用系统自带的 IMAPI2FS COM 接口把种子目录做成 ISO（标签 FOXOSSEED）。"""
    q = lambda s: "'" + s.replace("'", "''") + "'"  # noqa: E731
    return ("$fs = New-Object -ComObject IMAPI2FS.MsftFileSystemImage; $fs.FileSystemsToCreate = 3; $fs.VolumeName = 'FOXOSSEED'; "
            f"$fs.Root.AddTree({q(src)}, $false); $r = $fs.CreateResultImage(); $st = $r.ImageStream; "
            "Add-Type -TypeDefinition 'using System; using System.IO; using System.Runtime.InteropServices.ComTypes; public class FoxIso { "
            "public static void Save(object s, string p) { IStream i = (IStream)s; using (var f = File.Create(p)) { byte[] b = new byte[1048576]; "
            "IntPtr n = System.Runtime.InteropServices.Marshal.AllocHGlobal(4); while (true) { i.Read(b, b.Length, n); int c = System.Runtime.InteropServices.Marshal.ReadInt32(n); "
            "if (c <= 0) break; f.Write(b, 0, c); } } } }'; "
            f"[FoxIso]::Save($st, {q(out)})")


# ------------------------------------------------------------------ 安装

def _free_port() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def check_space(where: Path, need: int) -> None:
    free = download.free_bytes(where)
    if need and free < need:
        raise FoxError("DEPENDENCY_MISSING", tr("envs.presets.not_enough_disk", _gb(need), _gb(free), where))


def _gb(n: int) -> str:
    return f"{n / 1024 ** 3:.1f} GB"


def fetch_artifact(e: dict, artifact: str, cache: Path, dest: Path, report) -> dict:
    """下载一个产物（可分卷、可续传、逐卷校验），拼成 dest 并校验整份 sha256。"""
    art = e["artifacts"][artifact]
    parts = art.get("parts") or []
    total = int(art.get("size") or 0)
    cache.mkdir(parents=True, exist_ok=True)
    done_before = 0
    results = []
    if parts:
        files = []
        for i, p in enumerate(parts):
            def prog(bytes=0, bytes_total=0, **k):  # noqa: A002
                report(phase="download", part=i + 1, parts=len(parts), bytes=done_before + bytes, bytes_total=total,
                       why=tr("envs.presets.downloading_part", i + 1, len(parts), p["name"]), resumed=k.get("resumed", 0))
            r = download.fetch(p["url"], cache / p["name"], size=p.get("size"), sha256=p.get("sha256"), progress=prog)
            results.append({"name": p["name"], **r})
            files.append(cache / p["name"])
            done_before += int(p.get("size") or r["bytes"])
        report(phase="verify", why=tr("envs.presets.assembling", dest.name), bytes=0, bytes_total=total)
        a = download.assemble(files, dest, sha256=art.get("sha256"), size=total or None,
                              progress=lambda bytes=0, bytes_total=0, **k: report(phase="verify", bytes=bytes, bytes_total=bytes_total, why=tr("envs.presets.assembling", dest.name)))
        for f in files:
            f.unlink(missing_ok=True)
        return {"parts": results, "assembled": a}
    r = download.fetch(art["url"], dest, size=art.get("size"), sha256=art.get("sha256"),
                       progress=lambda bytes=0, bytes_total=0, **k: report(phase="download", part=1, parts=1, bytes=bytes, bytes_total=bytes_total or total,
                                                                           why=tr("envs.presets.downloading_part", 1, 1, art["name"]), resumed=k.get("resumed", 0)))
    return {"parts": [{"name": art["name"], **r}], "assembled": {"bytes": r["bytes"], "sha256": r["sha256"], "verified": r["verified"]}}


def wait_ready(serial: Path, timeout: float, proc_alive=lambda: True) -> str | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            for line in serial.read_text(encoding="utf-8", errors="replace").splitlines():
                if "FOXOS-PRESET-READY" in line:
                    return line.strip()
        except OSError:
            pass
        if not proc_alive():
            return None
        time.sleep(2)
    return None
