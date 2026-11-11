"""US-80…US-85：所有常见系统的安装包。

这些测试用真实产物和真实脚本：
- 构建过的 Linux 安装包放在 <仓库>/out/linux-<arch>/（scripts/packaging/collect-artifacts.sh 的输出），
  没有构建时相关用例跳过并说明原因；CI（.github/workflows/release.yml）每个平台都会构建并真装一遍。
- install.sh 通过本机 HTTP 服务下载、校验 SHA256SUMS、安装到临时 HOME，然后运行 foxos --version；
  再把 SHA256SUMS 改坏，确认脚本拒绝安装。
"""

from __future__ import annotations

import functools
import hashlib
import http.server
import json
import os
import platform
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
VERSION = json.loads((ROOT / "apps" / "desktop" / "package.json").read_text(encoding="utf-8"))["version"]
ARCH = {"x86_64": "x64", "amd64": "x64", "aarch64": "arm64", "arm64": "arm64"}.get(platform.machine().lower(), platform.machine())
OUT = ROOT / "out" / f"linux-{ARCH}"
TGZ = OUT / f"FoxOS-{VERSION}-linux-{ARCH}.tar.gz"
PKG = ROOT / "scripts" / "packaging"


@pytest.fixture
def release_server(tmp_path):
    """把本机构建的 tar.gz 与 SHA256SUMS 放在一个临时“发布目录”里，用 HTTP 提供下载。"""
    if not TGZ.exists():
        pytest.skip(f"没有 {TGZ.relative_to(ROOT)}：先运行 npm run dist:linux 与 collect-artifacts.sh")
    rel = tmp_path / "release"
    rel.mkdir()
    shutil.copy(TGZ, rel / TGZ.name)
    digest = hashlib.sha256(TGZ.read_bytes()).hexdigest()
    (rel / "SHA256SUMS").write_text(f"{digest}  {TGZ.name}\n", encoding="utf-8")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(rel))
    handler.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield rel, f"http://127.0.0.1:{srv.server_address[1]}", digest
    srv.shutdown()


def _install(base: str, home: Path, *extra: str) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "FOXOS_BASE_URL": base, "FOXOS_TAG": f"v{VERSION}-os-preview",
           "FOXOS_METHOD": "tar", "FOXOS_LANG": "en"}
    return subprocess.run(["sh", str(ROOT / "scripts" / "install.sh"), *extra], env=env, capture_output=True, text=True, timeout=600)


def test_US80_install_sh_downloads_verifies_and_installs_the_cli(release_server, tmp_path):
    _, base, digest = release_server
    home = tmp_path / "home"
    home.mkdir()
    r = _install(base, home)
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"SHA-256 OK: {digest}" in r.stdout
    assert f"foxos {VERSION}" in r.stdout
    cli = home / ".local" / "bin" / "foxos"
    assert cli.is_symlink()
    out = subprocess.run([str(cli), "--version"], capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == f"foxos {VERSION}"
    # 随包 Python 带好了内核依赖：用安装好的 foxos 真的建一个 xlsx
    ws = tmp_path / "ws"
    out = subprocess.run([str(cli), "--workspace", str(ws), "sheets", "create", "a.xlsx", "--json"], capture_output=True, text=True, timeout=120)
    assert json.loads(out.stdout)["ok"] is True and (ws / "a.xlsx").stat().st_size > 0
    desk = (home / ".local" / "share" / "applications" / "foxos.desktop").read_text(encoding="utf-8")
    assert "Name[zh_CN]=狐狸OS" in desk


def test_US80_install_sh_refuses_a_tampered_download(release_server, tmp_path):
    rel, base, _ = release_server
    (rel / "SHA256SUMS").write_text(f"{'0' * 64}  {TGZ.name}\n", encoding="utf-8")
    home = tmp_path / "home"
    home.mkdir()
    r = _install(base, home)
    assert r.returncode != 0
    assert "SHA-256 mismatch" in r.stderr
    assert not (home / ".local" / "share" / "foxos").exists()
    assert not (home / ".local" / "bin" / "foxos").exists()


def test_US80_install_sh_download_only_keeps_file(release_server, tmp_path):
    _, base, digest = release_server
    home = tmp_path / "home"
    home.mkdir()
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "FOXOS_BASE_URL": base, "FOXOS_TAG": f"v{VERSION}-os-preview", "FOXOS_LANG": "en"}
    r = subprocess.run(["sh", str(ROOT / "scripts" / "install.sh"), "--method", "tar", "--download-only"], env=env, cwd=tmp_path,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr
    assert hashlib.sha256((tmp_path / TGZ.name).read_bytes()).hexdigest() == digest


@pytest.mark.skipif(not (OUT / f"FoxOS-{VERSION}-linux-{ARCH}.deb").exists(), reason="没有构建 Linux 安装包")
def test_US81_linux_packages_smoke():
    """tar.gz 与 AppImage：foxos --version、help --json、sheets create、无头启动桌面截图；deb / rpm：架构、安装脚本、随包 Python。"""
    r = subprocess.run(["bash", str(PKG / "smoke-linux.sh"), str(OUT), ARCH], capture_output=True, text=True, timeout=900)
    print(r.stdout)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "失败 0" in r.stdout


def test_US82_package_manager_manifests(tmp_path):
    names = [f"FoxOS-Setup-{VERSION}-x64.exe", f"FoxOS-Setup-{VERSION}-arm64.exe", f"FoxOS-{VERSION}-win-x64.msi",
             f"FoxOS-{VERSION}-win-arm64.msi", f"FoxOS-{VERSION}-mac-arm64.zip", f"FoxOS-{VERSION}-mac-x64.zip",
             f"FoxOS-{VERSION}-linux-x64.tar.gz", f"FoxOS-{VERSION}-linux-arm64.tar.gz"]
    sums = {n: hashlib.sha256(n.encode()).hexdigest() for n in names}
    (tmp_path / "SHA256SUMS").write_text("".join(f"{h}  {n}\n" for n, h in sums.items()), encoding="utf-8")
    out = tmp_path / "m"
    subprocess.run(["python3", str(PKG / "gen_manifests.py"), "--version", VERSION, "--tag", f"v{VERSION}-os-preview",
                    "--sums", str(tmp_path / "SHA256SUMS"), "--out", str(out)], check=True, capture_output=True, text=True)
    inst = (out / "winget/manifests/g/gatesenman/FoxOS" / VERSION / "gatesenman.FoxOS.installer.yaml").read_text(encoding="utf-8")
    for n in names[:4]:
        assert n in inst and sums[n].upper() in inst
    assert inst.count("Architecture: arm64") == 2 and "InstallerType: wix" in inst and "Silent: /S" in inst
    cask = (out / "homebrew/Casks/foxos.rb").read_text(encoding="utf-8")
    assert sums[names[4]] in cask and sums[names[5]] in cask and 'binary "#{appdir}/FoxOS.app/Contents/Resources/bin/foxos"' in cask
    pkgbuild = out / "aur/foxos-bin/PKGBUILD"
    text = pkgbuild.read_text(encoding="utf-8")
    assert sums[names[6]] in text and sums[names[7]] in text
    subprocess.run(["bash", "-n", str(pkgbuild)], check=True)
    srcinfo = (out / "aur/foxos-bin/.SRCINFO").read_text(encoding="utf-8")
    assert f"pkgver = {VERSION}" in srcinfo and "arch = aarch64" in srcinfo


def test_US83_release_matrix_covers_every_common_platform():
    """发布矩阵：Windows / macOS / Linux 各 x64 + arm64，amd64 + arm64 两张 ISO，以及一行安装在主流发行版上的验证。"""
    yaml = pytest.importorskip("yaml")
    wf = yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"))
    on = wf.get("on", wf.get(True))
    assert "workflow_dispatch" in on and on["push"]["tags"] == ["v*"]
    desk = {(m["os"], m["arch"]) for m in wf["jobs"]["desktop"]["strategy"]["matrix"]["include"]}
    assert desk == {(o, a) for o in ("linux", "mac", "win") for a in ("x64", "arm64")}
    iso = {m["arch"]: m["runner"] for m in wf["jobs"]["iso"]["strategy"]["matrix"]["include"]}
    assert iso == {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}
    distros = {m["name"].split("-")[0] for m in wf["jobs"]["install-e2e"]["strategy"]["matrix"]["include"]}
    assert {"ubuntu", "debian", "fedora", "opensuse", "archlinux", "macos"} <= distros
    assert wf["permissions"] == {"contents": "write"}
    text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "secrets.GH_" not in text and "gh_foxos_token" not in text   # 只用内置 GITHUB_TOKEN


def test_US84_arm64_os_has_no_chrome_and_falls_back_to_firefox(tmp_path):
    """Google 不发布 Linux arm64 版 Chrome：arm64 系统上 foxos-chrome-setup 报告 unsupported-arch，入口改用 Firefox。"""
    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "dpkg").write_text("#!/bin/sh\n[ \"$1\" = --print-architecture ] && echo arm64\n", encoding="utf-8")
    (shim / "dpkg").chmod(0o755)
    env = {**os.environ, "PATH": f"{shim}:{os.environ['PATH']}", "HOME": str(tmp_path)}
    setup = ROOT / "scripts/os/chrome/foxos-chrome-setup"
    st = subprocess.run(["bash", str(setup), "--status"], env=env, capture_output=True, text=True)
    assert st.returncode == 0 and st.stdout.strip() == "unsupported-arch"
    assert subprocess.run(["bash", str(setup), "--firstrun"], env=env).returncode == 0
    assert subprocess.run(["bash", str(setup), "--gui"], env=env).returncode == 1          # foxos-chrome 因此改用 Firefox
    inst = subprocess.run(["bash", str(setup), "--install"], env=env, capture_output=True, text=True)
    assert inst.returncode == 6 and "arm64" in inst.stderr


def test_US84_iso_build_script_is_arch_aware():
    s = (ROOT / "scripts/os/build-iso.sh").read_text(encoding="utf-8")
    assert 'ARCH=${FOXOS_OS_ARCH:-amd64}' in s and 'ISO_NAME="FoxOS-${VERSION}-${ARCH}.iso"' in s
    assert "ports.ubuntu.com/ubuntu-ports" in s and "grub-efi-arm64-signed" in s and "linux64-aarch64" in s
    assert "cloud-hypervisor-static-aarch64" in s
    subprocess.run(["bash", "-n", str(ROOT / "scripts/os/build-iso.sh")], check=True)


def test_US85_install_ps1_is_ascii_and_supports_arm64_and_msi():
    s = (ROOT / "scripts/install.ps1").read_bytes()
    s.decode("ascii")                                       # irm | iex 在 Windows PowerShell 5.1 下要求纯 ASCII
    t = s.decode()
    assert "FoxOS-Setup-*-$Arch.exe" in t and "FoxOS-*-win-$Arch.msi" in t and "FoxOS-*-win-$Arch.zip" in t
    assert "'ARM64'" in t and "msiexec.exe" in t and "v0.3.2-os-preview" in t
