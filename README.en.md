<p align="center"><img src="assets/icons/icon-256.png" width="112" height="112" alt="FoxOS icon"></p>

<h1 align="center">FoxOS (狐狸OS)</h1>

<p align="center">A desktop operating system for agents: real desktop apps, one <code>foxos</code> command line and MCP tool set for everything, audit log and human takeover, and a home-grown isolation layer.</p>

<p align="center"><a href="README.md">中文</a> · <a href="https://github.com/gatesenman/foxos/releases/tag/v0.3.4-os-preview">Bootable ISO</a> · <a href="https://github.com/gatesenman/foxos/releases/tag/v0.3.4-windows-preview">Windows companion preview</a> · <a href="docs/os-test-guide.md">ISO test guide</a> · <a href="AGENTS.md">AGENTS.md</a></p>

![FoxOS 0.3.4 real desktop: XFCE, start menu and bottom panel](docs/screenshots/os-0.3.4-desktop.png)

This screenshot is from the FoxOS 0.3.4 ISO booted in QEMU (live session, `zh_CN`, 1920×1080), with the first-login dialogs closed. It shows the real xfwm4 desktop: the Whisker "开始" menu (favorites: terminal, Thunar, Google Chrome, Mousepad, "安装 狐狸OS") and the bottom panel (Start, clock, Take over, System), not a painted Electron fake desktop.

## What it is

FoxOS is first a **bootable, installable Linux OS** (Ubuntu 24.04 base, Chinese default, XFCE desktop). Agents (ACP/MCP clients such as Claude Code, Codex, Gemini CLI) and humans share a real desktop: every window is a real OS process.

The Windows `.exe` is a **companion** ([v0.3.4-windows-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.4-windows-preview)), not the ISO itself. It is a client of the FoxOS virtual computer: it shows the guest desktop and the bot chat, every action runs inside the FoxOS computer, and host execution is off by default (see [docs/windows-client.md](docs/windows-client.md)). We will not ship a macOS system image for non-Apple hardware.

Environments do not use Docker, Podman, or QEMU as the product runtime: full Linux guests use in-kernel KVM plus cloud-hypervisor (Apache-2.0); light sandboxes use namespaces; the Windows companion uses WSL2 / Hyper-V / Windows Sandbox. Docker Hub is only an optional distribution channel; see [docs/docker.md](docs/docker.md).

The workbench includes:

- **Real apps**: terminal (real PTY), file manager, Monaco editor, browser, native LibreOffice windows, and the 51 open-source Everything apps.
- **One operation, three entry points**: GUI, `foxos <app> <resource> <verb> --json`, and MCP tools (stdio and Streamable HTTP) all call the same kernel command.
- **Traceable and interruptible**: every call goes to a JSONL audit log; single-writer file locks; one-click human takeover pauses all agent writes.
- **Programs keep their own icons**: Everything apps show their upstream `icon-128.png` (MIT icons bundled, AGPL icons read from the installed upstream component), LibreOffice icons come from the local LibreOffice install, the terminal uses the system terminal icon, the editor VS Code / Code - OSS, the browser Electron, ACP agents the registry `icon`. FoxOS's own apps keep the FoxOS style; font icons are only for controls. See [NOTICE](apps/desktop/src/third-party-icons/NOTICE.md).
- **Chinese and English**: Simplified Chinese is the default; switch to English in the setup wizard or Settings (applies immediately, saved). The `foxos` CLI, MCP tool descriptions and kernel messages follow `--lang` / `FOXOS_LANG` (JSON field names and error codes never change); the Windows installer and `install.ps1` are bilingual; Everything apps receive the FoxOS language through the Chromium locale (Spreadsheet ships a Chinese UI and follows it; the others are English-only upstream and are marked so in the App Center).
- **Own scrollbars**: no default OS scrollbars anywhere. The shell, every window and every Everything app webview use a thin FoxOS overlay scrollbar (transparent track, hidden until hover or scroll, wider on hover, accent while dragging, dark/light aware); Monaco and the terminal use matching settings.
- **Own isolation layer**: no Docker or VM software. Linux namespaces on Linux; one-click WSL2 distros, Windows Sandbox and Hyper-V on Windows.

## Screenshots (the real FoxOS 0.3.4 system)

Every image below comes from FoxOS 0.3.4 itself: the live session, the installer and the installed login screen were captured from the 0.3.4 ISO booted in QEMU. The first-login dialogs ("安装 Google Chrome", "安装智能体命令行", "SSH 远程登录") were closed first, so no one-time password appears in any shot. Nothing is composited or mocked. The UI is in Simplified Chinese, the default.

| | |
| --- | --- |
| ![Desktop and start menu](docs/screenshots/os-0.3.4-desktop.png)<br>**Desktop and start menu**: XFCE desktop, Whisker "开始" menu (Chinese, Papirus icons), panel with clock / takeover / system | ![foxos commands in a terminal](docs/screenshots/os-0.3.4-terminal.png)<br>**foxos commands in a terminal**: a real `foxos@foxos` session in XFCE Terminal: `foxos sheets` writes a formula and reads it back, `foxos docs` builds a report, `foxos files` lists the workspace |
| ![Google Chrome](docs/screenshots/os-0.3.4-chrome.png)<br>**Google Chrome**: Chrome 157 installed from Google's official repository at first login (the default browser), Chinese UI | ![Thunar file manager](docs/screenshots/os-0.3.4-files.png)<br>**Thunar file manager**: the workspace with the `.xlsx` / `.docx` the terminal just created |
| ![Bots window](docs/screenshots/os-0.3.4-bots.png)<br>**Bots window**: the main bot "狐狸" opened from the start menu, with the new chat UI; approvals, connectors, code agents, machines, skills, routines and runtimes at the bottom left | ![Install FoxOS](docs/screenshots/os-0.3.4-installing.png)<br>**Install FoxOS**: Calamares started from the 0.3.4 ISO; the summary shows the EFI and root partitions |
| ![Installed system login](docs/screenshots/os-0.3.4-installed-login.png)<br>**Installed system**: the login screen after installing 0.3.4 to a virtual disk and booting from it | |

More screenshots of the bot chat UI are in their own section below: [Bot chat UI](#智能体聊天界面034--bot-chat-ui).

## Download

Everything is on [v0.3.2-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.2-os-preview) (pre-release); `SHA256SUMS` in the same release covers every file. Two different things:

- **The FoxOS operating system**: the bootable ISO (Ubuntu 24.04 + XFCE). The screenshots above are this system. From 0.3.2 the default browser is Google Chrome, installed from Google's official repository at first login (see [docs/os.md](docs/os.md)).
- **The desktop companion + `foxos` CLI**: an app for your existing Windows / macOS / Linux. It bundles Python 3.12 and the kernel, so `foxos` works in a terminal right after install.

| OS | x64 | arm64 |
| --- | --- | --- |
| Windows 10 1809+ / 11 | `FoxOS-Setup-0.3.2-x64.exe` (installer) · `FoxOS-0.3.2-win-x64.zip` (portable) | `FoxOS-Setup-0.3.2-arm64.exe` · `FoxOS-0.3.2-win-arm64.zip` |
| macOS 11+ | Intel: `FoxOS-0.3.2-mac-x64.zip` | Apple silicon: `FoxOS-0.3.2-mac-arm64.zip` |
| Ubuntu / Debian / Mint | `FoxOS-0.3.2-linux-x64.deb` | `FoxOS-0.3.2-linux-arm64.deb` |
| Fedora / RHEL / Rocky / Alma / openSUSE | `FoxOS-0.3.2-linux-x64.rpm` | `FoxOS-0.3.2-linux-arm64.rpm` |
| Arch / Manjaro / other distros | `FoxOS-0.3.2-linux-x64.tar.gz` · `.AppImage` | `FoxOS-0.3.2-linux-arm64.tar.gz` · `.AppImage` |
| **FoxOS OS ISO** | `FoxOS-0.3.4-amd64.iso.part-00` + `.part-01` + `.part-02` (on [v0.3.4-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.4-os-preview); join into the ISO; UEFI + BIOS) | build script ready (`FOXOS_OS_ARCH=arm64`); built on an arm64 runner once GitHub Actions is available |
| Package managers (drafts, not submitted) | winget `gatesenman.FoxOS` · Homebrew cask `foxos` · AUR `foxos-bin`, see `FoxOS-0.3.2-package-manifests.zip` and [`packaging/`](packaging/) | same |

End-to-end tests (install → desktop launch → `foxos --version` → `foxos sheets create` → uninstall): the Linux x64 deb / rpm / tar.gz / AppImage pass on Ubuntu 24.04, Debian 12, Fedora 43, openSUSE Tumbleweed and Arch. Linux arm64 install, CLI and uninstall pass under qemu; the desktop launch still needs a real arm64 machine. **The Windows and macOS builds have not been tested on real machines yet, so treat them as previews.** The MSI, dmg, arm64 ISO and single-file ISO are built by GitHub Actions ([`release.yml`](.github/workflows/release.yml)), which also runs the end-to-end tests on every platform. Actions cannot start on this repository right now because of a GitHub account billing lock; re-run the workflow once that is fixed. See [docs/install.md](docs/install.md) and the [test report](docs/test-report.md).

One-line install (detects OS and CPU, downloads, verifies SHA-256, installs, then runs `foxos --version`):

```bash
# Linux / macOS: deb on Ubuntu / Debian, rpm on Fedora / RHEL / openSUSE, ~/.local elsewhere or without sudo
curl -fsSL https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.sh | sh
```

```powershell
# Windows (x64 / arm64); set $env:FOXOS_PORTABLE = '1' for portable or $env:FOXOS_MSI = '1' for the MSI first
irm https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.ps1 | iex
```

The packages are not code-signed yet: on Windows, SmartScreen → "More info" → "Run anyway"; on macOS, Control-click FoxOS in Applications → Open (macOS 15+: System Settings → Privacy & Security → "Open Anyway"). Per-OS details, AppImage and ISO usage: **[docs/install.md](docs/install.md#english)**.

The ISO ([v0.3.4-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.4-os-preview)) is published as three parts, each under 1 GiB; join and verify them (`SHA256SUMS` is in the same release):

```bash
cat FoxOS-0.3.4-amd64.iso.part-00 FoxOS-0.3.4-amd64.iso.part-01 FoxOS-0.3.4-amd64.iso.part-02 > FoxOS-0.3.4-amd64.iso
sha256sum -c SHA256SUMS --ignore-missing
```

```powershell
cmd /c copy /b FoxOS-0.3.4-amd64.iso.part-00+FoxOS-0.3.4-amd64.iso.part-01+FoxOS-0.3.4-amd64.iso.part-02 FoxOS-0.3.4-amd64.iso
Get-FileHash -Algorithm SHA256 .\FoxOS-0.3.4-amd64.iso
```

USB and Hyper-V steps: [ISO test guide](docs/os-test-guide.md). Older releases (`v0.3.3-os-preview`, `v0.3.2-os-preview`, `v0.3.1-os-preview`, `v0.3.0-os-preview`, the Windows companion `v0.2.0-windows-preview`) remain on the [Releases](https://github.com/gatesenman/foxos/releases) page.

## 智能体聊天界面（0.3.4） / Bot chat UI

The "智能体" (bots) window in FoxOS 0.3.4. The Windows companion `v0.3.4-windows-preview` shows the same UI. The bots in these shots are working in a local test workspace.

| | |
| --- | --- |
| ![Chat and tool calls](docs/screenshots/bots-ui-chat-after.png)<br>**Chat**: the main bot "狐狸" answers while calling tools; each file read or command is an expandable card, and the "正在操作" bar at the top lists what every bot is doing | ![Approval](docs/screenshots/bots-ui-approval-after.png)<br>**Approval**: before "编码助手" writes a file it shows the diff and waits for allow once / always allow / deny |
| ![Docked to the screen edge](docs/screenshots/bots-ui-docked-desktop-after.png)<br>**Docked**: the chat docks to the right edge of the desktop while other windows keep working | ![Bot settings](docs/screenshots/bots-ui-settings-after.png)<br>**Bot settings**: name, title, instructions, avatar, plus skills and permissions, memory, approval rules, routines, delegation, machines and computer use |
| ![New chat](docs/screenshots/bots-ui-empty-after.png)<br>**New chat**: the main bot's start page with suggested prompts | ![Dark mode](docs/screenshots/bots-ui-chat-dark-after.png)<br>**Dark mode**: the same chat following the system dark theme |

## Quick start (from source)

```bash
git clone https://github.com/gatesenman/foxos.git && cd foxos
python3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'
cd apps/desktop && npm ci && npm start
```

## For agents: CLI and MCP

See [AGENTS.md](AGENTS.md), `foxos agent-guide`, [agent guide](docs/agent-guide.md), [CLI reference](docs/cli-reference.md), [MCP reference](docs/mcp-reference.md).
Messages and command descriptions are Chinese by default; use `--lang en-US` or `FOXOS_LANG=en-US` for English (JSON field names, error codes and command names do not change).
SSH is on by default (keys only; password login off, root login off, ufw allows 22). Agents connect with `ssh foxos@HOST foxos …` or MCP over SSH stdio `ssh -T foxos@HOST foxos mcp`; the live session shows its address and a one-time password. See [docs/ssh.md](docs/ssh.md).
Grammar `foxos <app> <resource> <verb> --json`; MCP tool names `<app>_<resource>_<verb>`; exit codes 0 OK, 1 ERROR, 2 USAGE, 3 NOT_FOUND, 4 PERMISSION_DENIED, 5 LOCKED, 6 DEPENDENCY_MISSING, 7 CONFLICT, 8 PAUSED.

## Everything apps (51)

From [HeyPuter/everything](https://github.com/HeyPuter/everything) at `0fbb88cd`. AGPL apps are built from upstream source at install time and are not modified or vendored.

<!-- apps:start -->
Runs locally: **50/51** · semantic CLI/MCP commands: **50/51** · boot e2e passed: **50/51** · GUI = CLI parity: **49/51** (details: [docs/everything-apps.md](docs/everything-apps.md))

| Group | Apps (ops = semantic commands) |
| --- | --- |
| Office | Spreadsheet `spreadsheet` (371 · AGPL)<br>Documents `documents` (311)<br>Presentation `presentation` (284 · AGPL)<br>Whiteboard `whiteboard` (26 · AGPL)<br>PDF `pdf` (85 · AGPL)<br>Notes `notes` (136 · AGPL)<br>Records `records` (16) |
| Collaboration | Meetings `meetings` (17)<br>Teamchat `teamchat` (6)<br>Email `email` (2 · AGPL)<br>Contacts `contacts` (28)<br>Calendar `calendar` (36)<br>Signatures `signatures` (29) |
| Creative Tools | Photo Studio `photo-studio` (104)<br>Video Studio `video-studio` (34 · AGPL)<br>Vector Studio `vector-studio` (90)<br>Audio Studio `audio-studio` (148)<br>Music Studio `music-studio` (266)<br>3D Studio `3d` (230 · AGPL) |
| Engineering | CAD `cad` (180 · AGPL)<br>Parametric `parametric` (33 · AGPL)<br>Circuits `circuits` (39 · AGPL)<br>Building Design `building-design` (1 · AGPL) |
| Productivity | Tasks `tasks` (58)<br>Projects `projects` (50)<br>Wiki `wiki` (60)<br>Time Tracking `time-tracking` (71)<br>Surveys `survey` (28) |
| Finance | Accounting `accounting` (45)<br>Invoicing `invoicing` (20)<br>Expenses `expense` (17)<br>Cap Table `cap-table` (27) |
| Business | CRM `crm` (16)<br>Help Desk `help-desk` (6)<br>Contracts `contracts` (14)<br>Point of Sale `pos` (17)<br>Inventory `inventory` (17)<br>Assets `assets` (0) — upstream source missing<br>Hiring `hiring` (22)<br>Shifts `shifts` (17)<br>Childcare `childcare` (39)<br>Field Service `field-service` (40)<br>Legal `legal` (43)<br>Fleet `fleet` (41)<br>Property Management `property-management` (45) |
| Developer Tools | API Client `api-client` (59) |
| Games | Chess `chess` (30)<br>Backgammon `backgammon` (27)<br>Checkers `checkers` (21)<br>Solitaire `solitaire` (9)<br>Sudoku `sudoku` (39) |
<!-- apps:end -->

## Environments

Linux: unprivileged user namespaces + overlayfs + pivot_root + seccomp, cgroup v2 when delegated (rlimit otherwise), snapshots, clones, `.foxenv` export, agents can run inside. Windows: WSL2 distro catalog with automatic WSL enablement, Windows Sandbox, Hyper-V. macOS: Virtualization.framework backend (untested on hardware). See [docs/environments.md](docs/environments.md) and the [provider protocol](docs/environment-provider-protocol.md). **Online preset systems**: preconfigured Debian 12 / Ubuntu 24.04 / FoxOS guests (desktop, Chinese, Node / Bun / Python, ACP agents, the foxos bridge) plus Windows evaluation and macOS recipes that download the official Microsoft / Apple media at install time; split downloads resume and are checked against sha256. See [docs/presets.md](docs/presets.md).

Light isolation (`foxos sandbox`): run host tools directly, but only the workspace is readable/writable and network can be turned off (Linux Landlock + seccomp, macOS Seatbelt, Windows restricted token / AppContainer + job objects). Pick "轻量沙箱" as the run location in the session panel. See [docs/sandbox.md](docs/sandbox.md).

## Architecture

Desktop (Electron: window manager, built-in apps, Everything runtime, ACP client, app bridge) → kernel (Python `foxos`: command registry generating argparse / JSON Schema / MCP tools / docs; workspace confinement, locks, audit, takeover; apps; environment providers). See the diagram in [README.md](README.md#架构) and [docs/architecture.md](docs/architecture.md).

## Testing

`npm run test:all` at the repo root runs pytest, the Playwright + Electron end-to-end tests under xvfb and the official-MCP-SDK tests, and writes [docs/test-report.md](docs/test-report.md) (pass/fail/skip per user story, per-app coverage). No mocks.

Latest report (Linux): 140 cases — 134 passed, 1 failed, 4 skipped, 1 known upstream defect; 29/32 user stories passed; Everything apps 50/51 boot locally, 49/51 GUI/CLI parity, 51/51 MCP calls succeed; program icons: Everything 51/51, built-ins 6/6, ACP agents 45/45. See the [test report](docs/test-report.md).

## Roadmap

Done: kernel, audit, locks, takeover, MCP; desktop and real apps; 51 Everything apps (50 run); Linux environment runtime; Windows environment catalog; Windows x64 preview.
Light sandbox level: Linux Landlock + seccomp (tested); macOS Seatbelt and Windows restricted token / AppContainer + job objects (code and unit tests, not yet verified on hardware).
Chinese / English UI (Chinese default) and FoxOS scrollbars: done.
Next: Windows hardware verification; Linux packages; macOS build; code signing.

## License

No license has been chosen yet (no LICENSE file). AGPL Everything apps are not distributed with this repository.
