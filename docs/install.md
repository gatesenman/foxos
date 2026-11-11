# 安装狐狸OS / Installing FoxOS

[中文](#中文) · [English](#english)

## 中文

狐狸OS 有两种东西，别弄混：

- **狐狸OS 操作系统**：可引导的 ISO（Ubuntu 24.04 + XFCE，中文界面），写进 U 盘装到电脑上，或在 Hyper-V / QEMU / UTM 里启动。
- **狐狸OS 桌面伴侣程序 + `foxos` 命令行**：装在你现有的 Windows、macOS 或 Linux 上的应用程序。安装包自带 Python 3.12 和狐狸OS 内核，装好就能在终端里用 `foxos`，不需要另外装 Python。

所有文件都在 GitHub Release [v0.3.2-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.2-os-preview)。

> **现状（2026-11-12）**：表里标「待 CI」的文件（MSI、dmg、arm64 ISO、单文件 ISO）要在 GitHub Actions 的 Windows / macOS / arm64 机器上构建。本仓库的 Actions 目前因 GitHub 账户的账单问题无法启动（任务未开始即失败）；账单恢复后手动运行一次 `release` 工作流就会补上。其余文件已在 Linux 构建机上构建并做过安装测试；macOS 的 zip 已 ad-hoc 签名，但还没在真 Mac 上运行过。
每个文件的 SHA-256 都在同一发布的 `SHA256SUMS` 里；安装脚本会自动校验，校验不通过就停止。

### 选哪个文件

| 系统 | CPU | 文件 | 说明 |
| --- | --- | --- | --- |
| Windows 10 1809+ / 11 | x64 | `FoxOS-Setup-0.3.2-x64.exe` | 安装程序（按用户安装，可选目录，中文 / English） |
| | x64 | `FoxOS-0.3.2-win-x64.msi`（待 CI） | MSI（按机器安装，适合批量部署；需要管理员） |
| | x64 | `FoxOS-0.3.2-win-x64.zip` | 便携版，解压即用 |
| | arm64 | `FoxOS-Setup-0.3.2-arm64.exe` · `FoxOS-0.3.2-win-arm64.zip` · `FoxOS-0.3.2-win-arm64.msi`（待 CI） | 同上，原生 arm64（Surface Pro X / 骁龙 X 等） |
| macOS 11+ | Apple 芯片（M1–M4） | `FoxOS-0.3.2-mac-arm64.zip`（`.dmg` 待 CI） | 解压后拖到「应用程序」 |
| | Intel | `FoxOS-0.3.2-mac-x64.zip`（`.dmg` 待 CI） | 同上 |
| Ubuntu / Debian / Linux Mint / deepin / 统信 UOS | x64 · arm64 | `FoxOS-0.3.2-linux-x64.deb` · `FoxOS-0.3.2-linux-arm64.deb` | `sudo apt install ./文件名.deb` |
| Fedora / RHEL / Rocky / Alma / openEuler / openSUSE | x64 · arm64 | `FoxOS-0.3.2-linux-x64.rpm` · `FoxOS-0.3.2-linux-arm64.rpm` | `sudo dnf install ./文件名.rpm`；openSUSE 用 `sudo zypper install --allow-unsigned-rpm ./文件名.rpm` |
| Arch / Manjaro / 其他发行版 | x64 · arm64 | `FoxOS-0.3.2-linux-x64.tar.gz` · `FoxOS-0.3.2-linux-arm64.tar.gz` | 解压即用；Arch 也可以用 AUR 草稿 `foxos-bin` |
| 任何 Linux 桌面 | x64 · arm64 | `FoxOS-0.3.2-linux-x64.AppImage` · `FoxOS-0.3.2-linux-arm64.AppImage` | 单文件，`chmod +x` 后双击；需要 FUSE 2（Ubuntu 24.04：`sudo apt install libfuse2t64`）。只含桌面，命令行请用 deb / rpm / tar.gz |
| 狐狸OS 系统（PC、Hyper-V、VMware、QEMU） | amd64 | 分卷 `FoxOS-0.3.2-amd64.iso.part1` + `.part2`（单文件 `.iso` 待 CI） | UEFI + 传统 BIOS |
| 狐狸OS 系统（ARM 电脑、UTM / Parallels on Apple 芯片、ARM 服务器） | arm64 | `FoxOS-0.3.2-arm64.iso`（待 CI） | 仅 UEFI；Google 没有 Linux arm64 版 Chrome，arm64 系统默认用 Firefox |

### 一行安装

Linux 和 macOS（自动识别系统和 CPU，下载、校验、安装，最后运行 `foxos --version`）：

```bash
curl -fsSL https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.sh | sh
```

- Ubuntu / Debian 用 `.deb`，Fedora / RHEL / openSUSE 用 `.rpm`（需要 sudo）；Arch 等其他发行版、或没有 sudo 时，装到 `~/.local/share/foxos`，命令链接到 `~/.local/bin/foxos`。
- 指定方式：`curl -fsSL …/install.sh | sh -s -- --method tar`（可选 `deb` / `rpm` / `tar` / `appimage`）；只下载校验：`--download-only`；英文提示：`--lang en`。
- macOS 装到 `/Applications/FoxOS.app`（没有写权限就装到 `~/Applications`），命令链接到 `/usr/local/bin/foxos` 或 `~/.local/bin/foxos`。

Windows（PowerShell，x64 和 arm64 自动识别）：

```powershell
irm https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.ps1 | iex
# 便携版 / MSI：先设环境变量再运行同一行
$env:FOXOS_PORTABLE = '1'   # 或 $env:FOXOS_MSI = '1'
```

下载脚本后也可以带参数：`-Portable`、`-Msi`、`-Arch arm64`、`-Silent`、`-Dir <目录>`、`-DownloadOnly`、`-Lang en-US`。

### 各系统的注意事项

**Windows**：安装包还没有代码签名，首次运行时 SmartScreen 会提示「Windows 已保护你的电脑」，点「更多信息 → 仍要运行」。

**macOS**：安装包还没有经过 Apple 公证（需要 Apple 开发者账号）。第一次打开时：

1. 在「访达 → 应用程序」里**按住 Control 点按**（或右键）FoxOS，选「打开」，在弹窗里再点「打开」。
2. macOS 15 Sequoia 及以后，右键「打开」不再出现放行按钮：先双击一次，再到「系统设置 → 隐私与安全性」底部点「仍要打开」，输入密码确认。
3. 或者在终端里执行一次：`xattr -dr com.apple.quarantine /Applications/FoxOS.app`（用 `install.sh` 安装时已经自动做了）。

**Linux**：

- deb / rpm 会把程序装到 `/opt/FoxOS`，并建立 `/usr/bin/foxos`（命令行）和 `/usr/bin/foxos-desktop`（桌面）。卸载：`sudo apt remove foxos-desktop` 或 `sudo dnf remove foxos-desktop`。
- 中文界面需要中文字体：Ubuntu / Debian 会自动推荐安装 `fonts-noto-cjk`；Fedora 装 `google-noto-sans-cjk-fonts`，Arch 装 `noto-fonts-cjk`。
- 在没有用户命名空间的系统上（部分加固内核），deb / rpm 会自动给 `chrome-sandbox` 设 SUID；tar.gz / AppImage 可加 `--no-sandbox` 启动。

### 包管理器（草稿）

每次发布都会附带 `FoxOS-<版本>-package-manifests.zip`，里面是按本次 SHA-256 填好的清单，仓库里 [`packaging/`](../packaging/) 也有一份：

- **winget**：`packaging/winget/manifests/g/gatesenman/FoxOS/<版本>/`（NSIS 按用户 + MSI 按机器，x64 / arm64）。提交到 [winget-pkgs](https://github.com/microsoft/winget-pkgs) 后可以 `winget install gatesenman.FoxOS`；现在可以本地试：`winget install --manifest <目录>`（需要先 `winget settings --enable LocalManifestFiles`）。
- **Homebrew**：`packaging/homebrew/Casks/foxos.rb`。现在可以本地试：`brew install --cask ./foxos.rb`。
- **AUR**：`packaging/aur/foxos-bin/PKGBUILD`。现在可以本地试：`makepkg -si`。

这三个都还没有提交到官方仓库（需要以 Sarah 的账号提交并维护）。

### 系统镜像（ISO）

单个文件小于 2 GiB，可以直接下载 `FoxOS-0.3.2-<amd64|arm64>.iso`；同时保留 800 MiB 的分卷，网络不稳时下载分卷再合并：

```bash
cat FoxOS-0.3.2-amd64.iso.part1 FoxOS-0.3.2-amd64.iso.part2 > FoxOS-0.3.2-amd64.iso
sha256sum -c SHA256SUMS --ignore-missing
```

```powershell
cmd /c copy /b FoxOS-0.3.2-amd64.iso.part1+FoxOS-0.3.2-amd64.iso.part2 FoxOS-0.3.2-amd64.iso
Get-FileHash -Algorithm SHA256 .\FoxOS-0.3.2-amd64.iso
```

写 U 盘、Hyper-V 和 QEMU 的步骤见 [os-test-guide.md](os-test-guide.md)。arm64 镜像在 Apple 芯片 Mac 上可以用 UTM（选「虚拟化 → Linux」，引导 ISO 即可）。

### 这些安装包是怎么做出来的

全部由 GitHub Actions 的 [`release.yml`](../.github/workflows/release.yml) 在对应系统的机器上构建，并由构建机直接上传到 Release：

- Windows x64 / arm64：`windows-2022` / `windows-11-arm`；Linux x64 / arm64：`ubuntu-24.04` / `ubuntu-24.04-arm`；macOS Apple 芯片 / Intel：`macos-14` / `macos-15-intel`；arm64 ISO：`ubuntu-24.04-arm`。
- 每台构建机在上传前都会真装一遍并运行 `foxos --version`（Windows：NSIS 静默安装、MSI、便携版；macOS：挂载 dmg、验签；Linux：apt 真装 deb、解开 AppImage 和 tar.gz、检查 rpm）。
- 上传后再在 Ubuntu、Debian、Fedora、openSUSE、Arch、macOS、Windows 上用 `install.sh` / `install.ps1` 从 Release 真实下载安装一次。
- 签名可以随时打开：在仓库 Secrets 里配置 `MAC_CSC_LINK`、`MAC_CSC_KEY_PASSWORD`、`APPLE_ID`、`APPLE_APP_SPECIFIC_PASSWORD`、`APPLE_TEAM_ID`（macOS 签名 + 公证）或 `WIN_CSC_LINK`、`WIN_CSC_KEY_PASSWORD`（Windows），不用改代码。
- 本地构建：`cd apps/desktop && npm ci && npm run dist:linux`（其他平台见 `package.json` 里的 `dist:*`；Windows 在 Linux 上交叉构建见 [windows-build.md](windows-build.md)）。

## English

FoxOS ships two different things:

- **The FoxOS operating system**: a bootable ISO (Ubuntu 24.04 + XFCE, Chinese UI by default). Flash it to a USB stick or boot it in Hyper-V / QEMU / UTM.
- **The FoxOS desktop companion + `foxos` CLI**: an app for your existing Windows, macOS or Linux. Every package bundles Python 3.12 and the FoxOS kernel, so `foxos` works in a terminal right after install.

Everything is on the GitHub release [v0.3.2-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.2-os-preview).

> **Status (2026-11-12)**: files marked "pending CI" (MSI, dmg, arm64 ISO, single-file ISO) need GitHub Actions Windows / macOS / arm64 runners. Actions cannot start on this repository right now because of a GitHub account billing lock; once that is resolved, run the `release` workflow once to add them. Everything else was built and install-tested on a Linux build machine; the macOS zips are ad-hoc signed but not yet run on a real Mac.
 `SHA256SUMS` in the same release covers every file; the install scripts verify it and stop on a mismatch.

### Which file

| OS | CPU | File | Notes |
| --- | --- | --- | --- |
| Windows 10 1809+ / 11 | x64 | `FoxOS-Setup-0.3.2-x64.exe` | Installer (per user, choose folder, Chinese / English) |
| | x64 | `FoxOS-0.3.2-win-x64.msi` (pending CI) | MSI (per machine, for managed deployment; needs admin) |
| | x64 | `FoxOS-0.3.2-win-x64.zip` | Portable |
| | arm64 | `FoxOS-Setup-0.3.2-arm64.exe` · `FoxOS-0.3.2-win-arm64.zip` · `.msi` (pending CI) | Same, native arm64 |
| macOS 11+ | Apple silicon | `FoxOS-0.3.2-mac-arm64.zip` (`.dmg` pending CI) | Unzip, drag to Applications |
| | Intel | `FoxOS-0.3.2-mac-x64.zip` (`.dmg` pending CI) | Same |
| Ubuntu / Debian / Mint | x64 · arm64 | `FoxOS-0.3.2-linux-<arch>.deb` | `sudo apt install ./file.deb` |
| Fedora / RHEL / Rocky / Alma / openSUSE | x64 · arm64 | `FoxOS-0.3.2-linux-<arch>.rpm` | `sudo dnf install ./file.rpm`; openSUSE: `sudo zypper install --allow-unsigned-rpm ./file.rpm` |
| Arch / other distros | x64 · arm64 | `FoxOS-0.3.2-linux-<arch>.tar.gz` | Extract and run; AUR draft `foxos-bin` |
| Any Linux desktop | x64 · arm64 | `FoxOS-0.3.2-linux-<arch>.AppImage` | Single file; needs FUSE 2. Desktop only; use deb / rpm / tar.gz for the CLI |
| FoxOS OS (PC, Hyper-V, VMware, QEMU) | amd64 | `.part1` + `.part2` (single `.iso` pending CI) | UEFI + legacy BIOS |
| FoxOS OS (ARM PCs, UTM / Parallels on Apple silicon, ARM servers) | arm64 | `FoxOS-0.3.2-arm64.iso` (pending CI) | UEFI only; Google ships no Linux arm64 Chrome, so Firefox is the default browser |

### One-line install

```bash
# Linux and macOS
curl -fsSL https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.sh | sh
# options: sh -s -- --method deb|rpm|tar|appimage  --download-only  --lang en
```

```powershell
# Windows (x64 / arm64 detected automatically)
irm https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.ps1 | iex
# $env:FOXOS_PORTABLE = '1' or $env:FOXOS_MSI = '1' before the same line; or -Portable / -Msi / -Arch / -Silent / -Dir / -DownloadOnly
```

### Platform notes

- **Windows**: not code-signed yet; on first run SmartScreen says "Windows protected your PC" → "More info" → "Run anyway".
- **macOS**: not notarized yet (needs an Apple Developer account). Control-click (right-click) FoxOS in Applications → Open → Open. On macOS 15 Sequoia and later, open it once, then go to System Settings → Privacy & Security → "Open Anyway". Or run `xattr -dr com.apple.quarantine /Applications/FoxOS.app` (install.sh already does this).
- **Linux**: deb / rpm install to `/opt/FoxOS` with `/usr/bin/foxos` and `/usr/bin/foxos-desktop`. Install a CJK font for the Chinese UI (`fonts-noto-cjk`, `google-noto-sans-cjk-fonts`, `noto-fonts-cjk`).

### Package managers (drafts)

Each release attaches `FoxOS-<version>-package-manifests.zip` with winget, Homebrew cask and AUR `PKGBUILD` filled in with that release's SHA-256 values; a copy lives in [`packaging/`](../packaging/). None is submitted to the official repositories yet. Try them locally with `winget install --manifest <dir>`, `brew install --cask ./foxos.rb`, or `makepkg -si`.

### OS images

Each ISO is below 2 GiB and is attached as a single file plus 800 MiB parts. Join the parts with `cat` (or `copy /b` on Windows) and check `SHA256SUMS`. See [os-test-guide.md](os-test-guide.md) for USB, Hyper-V and QEMU.

### How these are built

[`release.yml`](../.github/workflows/release.yml) builds every package on a matching GitHub Actions runner and uploads it straight to the release. Each runner installs and runs what it built before uploading, and after upload `install.sh` / `install.ps1` install from the release on Ubuntu, Debian, Fedora, openSUSE, Arch, macOS and Windows. Signing turns on by adding the `MAC_*` / `APPLE_*` or `WIN_CSC_*` repository secrets.
