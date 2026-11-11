#!/usr/bin/env python3
"""从发布的 SHA256SUMS 生成包管理器清单草稿（都还没有提交到各自的仓库）：

  winget/manifests/g/gatesenman/FoxOS/<版本>/   winget 1.6 多文件清单（NSIS 按用户 + MSI 按机器，x64 / arm64）
  homebrew/Casks/foxos.rb                        Homebrew cask（Apple 芯片 / Intel 分别校验）
  aur/foxos-bin/PKGBUILD 与 .SRCINFO             Arch AUR（x86_64 / aarch64 的 tar.gz）

用法：gen_manifests.py --version 0.3.2 --tag v0.3.2-os-preview --sums SHA256SUMS --out packaging
"""
from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import sys

REPO = "gatesenman/foxos"
HOMEPAGE = f"https://github.com/{REPO}"
DESC_EN = "FoxOS desktop companion and foxos CLI for agents (bundled Python 3.12 and kernel)"
DESC_ZH = "狐狸OS 桌面伴侣程序与 foxos 命令行（自带 Python 3.12 与内核）"


def read_sums(path: pathlib.Path) -> dict[str, str]:
    sums = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            sums[parts[-1].lstrip("*")] = parts[0].lower()
    return sums


def need(sums: dict[str, str], name: str) -> str:
    if name not in sums:
        sys.exit(f"SHA256SUMS 里没有 {name}")
    return sums[name]


def winget(v: str, tag: str, sums: dict[str, str], out: pathlib.Path) -> None:
    d = out / "winget" / "manifests" / "g" / "gatesenman" / "FoxOS" / v
    d.mkdir(parents=True, exist_ok=True)
    pid = "gatesenman.FoxOS"
    url = f"{HOMEPAGE}/releases/download/{tag}"
    head = "# yaml-language-server: $schema=https://aka.ms/winget-manifest.{kind}.1.6.0.schema.json\n"
    (d / f"{pid}.yaml").write_text(head.format(kind="version") + f"""
PackageIdentifier: {pid}
PackageVersion: {v}
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
""", encoding="utf-8")
    installers = []
    for arch in ("x64", "arm64"):
        exe = f"FoxOS-Setup-{v}-{arch}.exe"
        if exe in sums:
            installers.append(f"""- Architecture: {arch}
  InstallerType: nullsoft
  Scope: user
  InstallerUrl: {url}/{exe}
  InstallerSha256: {sums[exe].upper()}
  InstallerSwitches:
    Silent: /S
    SilentWithProgress: /S
""")
        msi = f"FoxOS-{v}-win-{arch}.msi"
        if msi in sums:
            installers.append(f"""- Architecture: {arch}
  InstallerType: wix
  Scope: machine
  InstallerUrl: {url}/{msi}
  InstallerSha256: {sums[msi].upper()}
""")
    if not installers:
        sys.exit("没有 Windows 安装包，无法生成 winget 清单")
    (d / f"{pid}.installer.yaml").write_text(head.format(kind="installer") + f"""
PackageIdentifier: {pid}
PackageVersion: {v}
MinimumOSVersion: 10.0.17763.0
UpgradeBehavior: install
ReleaseDate: {_dt.date.today().isoformat()}
Installers:
{''.join(installers)}ManifestType: installer
ManifestVersion: 1.6.0
""", encoding="utf-8")
    for loc, name, desc in (("en-US", "FoxOS", DESC_EN), ("zh-CN", "狐狸OS", DESC_ZH)):
        kind = "defaultLocale" if loc == "en-US" else "locale"
        (d / f"{pid}.locale.{loc}.yaml").write_text(head.format(kind=kind) + f"""
PackageIdentifier: {pid}
PackageVersion: {v}
PackageLocale: {loc}
Publisher: gaosichun
PublisherUrl: https://github.com/gatesenman
PackageName: {name}
PackageUrl: {HOMEPAGE}
License: Proprietary
ShortDescription: {desc}
Moniker: foxos
Tags:
- agent
- mcp
- desktop
ReleaseNotesUrl: {HOMEPAGE}/releases/tag/{tag}
ManifestType: {kind}
ManifestVersion: 1.6.0
""", encoding="utf-8")


def homebrew(v: str, tag: str, sums: dict[str, str], out: pathlib.Path) -> None:
    arm = need(sums, f"FoxOS-{v}-mac-arm64.zip")
    intel = need(sums, f"FoxOS-{v}-mac-x64.zip")
    d = out / "homebrew" / "Casks"
    d.mkdir(parents=True, exist_ok=True)
    (d / "foxos.rb").write_text(f'''cask "foxos" do
  arch arm: "arm64", intel: "x64"

  version "{v}"
  sha256 arm:   "{arm}",
         intel: "{intel}"

  url "{HOMEPAGE}/releases/download/{tag}/FoxOS-#{{version}}-mac-#{{arch}}.zip"
  name "FoxOS"
  name "狐狸OS"
  desc "{DESC_EN}"
  homepage "{HOMEPAGE}"

  livecheck do
    url :url
    strategy :github_releases
  end

  depends_on macos: ">= :big_sur"

  app "FoxOS.app"
  binary "#{{appdir}}/FoxOS.app/Contents/Resources/bin/foxos"

  zap trash: [
    "~/Library/Application Support/FoxOS",
    "~/Library/Logs/FoxOS",
    "~/Library/Preferences/io.github.gatesenman.foxos.plist",
  ]

  caveats <<~EOS
    FoxOS is not notarized by Apple yet. If macOS blocks the first launch, run:
      xattr -dr com.apple.quarantine "#{{appdir}}/FoxOS.app"
  EOS
end
''', encoding="utf-8")


def aur(v: str, tag: str, sums: dict[str, str], out: pathlib.Path) -> None:
    x64 = need(sums, f"FoxOS-{v}-linux-x64.tar.gz")
    a64 = need(sums, f"FoxOS-{v}-linux-arm64.tar.gz")
    d = out / "aur" / "foxos-bin"
    d.mkdir(parents=True, exist_ok=True)
    url = f"{HOMEPAGE}/releases/download/{tag}"
    deps = ["gtk3", "nss", "alsa-lib", "libxss", "libxtst", "libnotify", "libsecret", "xdg-utils", "at-spi2-core", "ttf-font"]
    (d / "PKGBUILD").write_text(f"""# Maintainer: gaosichun <gatesenman@users.noreply.github.com>
pkgname=foxos-bin
pkgver={v}
pkgrel=1
pkgdesc="{DESC_EN}"
arch=('x86_64' 'aarch64')
url="{HOMEPAGE}"
license=('LicenseRef-FoxOS')
depends=({' '.join(f"'{x}'" for x in deps)})
optdepends=('noto-fonts-cjk: Chinese UI font')
provides=('foxos')
conflicts=('foxos')
options=('!strip' '!debug')
_tag={tag}
source_x86_64=("FoxOS-$pkgver-linux-x64.tar.gz::{url.replace(tag, '$_tag')}/FoxOS-$pkgver-linux-x64.tar.gz")
source_aarch64=("FoxOS-$pkgver-linux-arm64.tar.gz::{url.replace(tag, '$_tag')}/FoxOS-$pkgver-linux-arm64.tar.gz")
sha256sums_x86_64=('{x64}')
sha256sums_aarch64=('{a64}')

package() {{
  install -d "$pkgdir/opt/foxos" "$pkgdir/usr/bin"
  case $CARCH in x86_64) _a=x64 ;; aarch64) _a=arm64 ;; esac
  cp -a "$srcdir/FoxOS-$pkgver-linux-$_a/." "$pkgdir/opt/foxos/"
  ln -s /opt/foxos/foxos-desktop "$pkgdir/usr/bin/foxos-desktop"
  ln -s /opt/foxos/resources/bin/foxos "$pkgdir/usr/bin/foxos"
  install -Dm644 "$pkgdir/opt/foxos/resources/icon.png" "$pkgdir/usr/share/pixmaps/foxos.png"
  install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/foxos.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=FoxOS
Name[zh_CN]=狐狸OS
Exec=/usr/bin/foxos-desktop %U
Icon=foxos
Categories=Office;
EOF
}}
""", encoding="utf-8")
    dep_lines = "".join(f"\tdepends = {x}\n" for x in deps)
    (d / ".SRCINFO").write_text(f"""pkgbase = foxos-bin
\tpkgdesc = {DESC_EN}
\tpkgver = {v}
\tpkgrel = 1
\turl = {HOMEPAGE}
\tarch = x86_64
\tarch = aarch64
\tlicense = LicenseRef-FoxOS
{dep_lines}\toptdepends = noto-fonts-cjk: Chinese UI font
\tprovides = foxos
\tconflicts = foxos
\toptions = !strip
\toptions = !debug
\tsource_x86_64 = FoxOS-{v}-linux-x64.tar.gz::{url}/FoxOS-{v}-linux-x64.tar.gz
\tsha256sums_x86_64 = {x64}
\tsource_aarch64 = FoxOS-{v}-linux-arm64.tar.gz::{url}/FoxOS-{v}-linux-arm64.tar.gz
\tsha256sums_aarch64 = {a64}

pkgname = foxos-bin
""", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--sums", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--only", choices=["winget", "homebrew", "aur"], action="append")
    a = ap.parse_args()
    sums = read_sums(a.sums)
    done = []
    for name, fn in (("winget", winget), ("homebrew", homebrew), ("aur", aur)):
        if a.only and name not in a.only:
            continue
        try:
            fn(a.version, a.tag, sums, a.out)
            done.append(name)
        except SystemExit as e:  # 某个平台没有产物：跳过这一个清单，别的照常生成
            print(f"跳过 {name}：{e}", file=sys.stderr)
    print("已生成：" + ", ".join(done) if done else "什么都没生成")
    if not done:
        sys.exit(1)


if __name__ == "__main__":
    main()
