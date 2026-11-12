<p align="center"><img src="assets/icons/icon-256.png" width="112" height="112" alt="FoxOS icon"></p>

<h1 align="center">FoxOS (狐狸OS)</h1>

<p align="center">A desktop operating system for agents: real desktop apps, one <code>foxos</code> command line and MCP tool set for everything, audit log and human takeover, and a home-grown isolation layer.</p>

<p align="center"><a href="README.md">中文</a> · <a href="https://github.com/gatesenman/foxos/releases/tag/v0.3.3-os-preview">Bootable ISO</a> · <a href="https://github.com/gatesenman/foxos/releases/tag/v0.3.4-windows-preview">Windows companion preview</a> · <a href="docs/os-test-guide.md">ISO test guide</a> · <a href="AGENTS.md">AGENTS.md</a></p>

![FoxOS real desktop: XFCE, start menu, bottom panel, and terminal](docs/screenshots/os-031-desktop.png)

This screenshot is from a real FoxOS XFCE graphical session (QEMU / Xvfb used for testing only). It shows real xfwm4 windows: the XFCE terminal (`foxos@foxos`), the bottom panel (Start, clock, System, Take over), and the Whisker applications menu — not a painted Electron fake desktop.

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

## Screenshots (the real FoxOS 0.3.2 / 0.3.1 system)

Every image below comes from FoxOS itself (the four Chrome shots are 0.3.2, the rest 0.3.1): the ISO's root filesystem running a real XFCE session as user `foxos` in `zh_CN` (Xvfb, 1920×1080), with real xfwm4 windows and real application processes. The installer and boot shots come from the ISO booted in QEMU. Nothing is composited or mocked. Script: [`scripts/os/tools/shoot-desktop.sh`](scripts/os/tools/shoot-desktop.sh).

| | |
| --- | --- |
| ![Desktop and start menu](docs/screenshots/os-031-desktop.png)<br>**Desktop and start menu**: XFCE desktop, Whisker "开始" menu (Chinese, Papirus icons, "安装 狐狸OS" in favorites), panel with clock / takeover / system | ![foxos commands in a terminal](docs/screenshots/os-031-terminal.png)<br>**foxos commands in a terminal**: XFCE Terminal, a real `foxos@foxos` session: `foxos sheets` writes formulas, `foxos docs` builds a report, `foxos files` lists the workspace |
| ![Google Chrome](docs/screenshots/os-032-chrome.png)<br>**Google Chrome (default browser in 0.3.2)**: Real Chrome 157 opened by `foxos desktop launch chrome`, Chinese UI; the start-menu favorite and the xdg default browser point to it | ![An agent driving Chrome over CDP](docs/screenshots/os-032-chrome-cdp.png)<br>**Agent control over CDP**: After a human runs `foxos browser cdp on` (127.0.0.1 only, off by default), an agent reads tabs, evaluates script and takes a screenshot with `foxos browser tabs / eval / screenshot` |
| ![First login: install Google Chrome](docs/screenshots/os-032-live-boot.png)<br>**First login: install Google Chrome**: The dialog that appears after the 0.3.2 ISO boots in QEMU. Google's terms keep Chrome out of the ISO; "同意并安装" installs it from Google's official repository | ![Chrome setup dialog](docs/screenshots/os-032-chrome-setup.png)<br>**Setup dialog (full resolution)**: The same dialog in a 1920×1080 session; declining is fine, Firefox stays as the offline fallback |
| ![Thunar file manager](docs/screenshots/os-031-files.png)<br>**Thunar file manager**: The workspace with the `.xlsx` / `.docx` the commands just created | ![Firefox](docs/screenshots/os-031-firefox.png)<br>**Firefox**: The default browser in 0.3.1 (from 0.3.2 the default is Google Chrome; Firefox stays as the offline fallback) showing the project page |
| ![Mousepad text editor](docs/screenshots/os-031-editor.png)<br>**Mousepad text editor**: Chinese menus, editing Markdown in the workspace | ![Settings Manager](docs/screenshots/os-031-settings.png)<br>**Settings Manager**: XFCE settings (appearance, display, keyboard, input method), Chinese UI |
| ![System menu](docs/screenshots/os-031-system.png)<br>**System menu**: Log out / restart / shut down dialog from the panel "系统" button | ![Human takeover](docs/screenshots/os-031-takeover.png)<br>**Human takeover**: After `foxos control pause`, agent writes are refused (`PAUSED`, exit code 8); real terminal output. The panel indicator had not refreshed to "接管中" yet in this shot; fixed in 0.3.2 |
| ![Install FoxOS](docs/screenshots/os-031-installer.png)<br>**Install FoxOS**: Calamares started from the 0.3.1 ISO booted in QEMU (VM resolution, blank disk attached) | ![Booted from the ISO](docs/screenshots/os-live-boot.png)<br>**Booted from the ISO**: The 0.3.1 live session in a VM, auto-logged in as `foxos` on XFCE |

Screenshots of the Windows companion app are in their own section below: [Windows companion app](#windows-伴侣程序在现有-windows-桌面上运行v020--windows-companion-app).

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
| **FoxOS OS ISO** | `FoxOS-0.3.3-amd64.iso.part-00` + `.part-01` + `.part-02` (on [v0.3.3-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.3-os-preview); join into the ISO; UEFI + BIOS) | build script ready (`FOXOS_OS_ARCH=arm64`); built on an arm64 runner once GitHub Actions is available |
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

The ISO ([v0.3.3-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.3-os-preview)) is published as three parts, each under 1 GiB; join and verify them (`SHA256SUMS` is in the same release):

```bash
cat FoxOS-0.3.3-amd64.iso.part-00 FoxOS-0.3.3-amd64.iso.part-01 FoxOS-0.3.3-amd64.iso.part-02 > FoxOS-0.3.3-amd64.iso
sha256sum -c SHA256SUMS --ignore-missing
```

```powershell
cmd /c copy /b FoxOS-0.3.3-amd64.iso.part-00+FoxOS-0.3.3-amd64.iso.part-01+FoxOS-0.3.3-amd64.iso.part-02 FoxOS-0.3.3-amd64.iso
Get-FileHash -Algorithm SHA256 .\FoxOS-0.3.3-amd64.iso
```

USB and Hyper-V steps: [ISO test guide](docs/os-test-guide.md). Older releases (`v0.3.2-os-preview`, `v0.3.1-os-preview`, `v0.3.0-os-preview`, the Windows companion `v0.2.0-windows-preview`) remain on the [Releases](https://github.com/gatesenman/foxos/releases) page.

## Windows 伴侣程序（在现有 Windows 桌面上运行，v0.2.0） / Windows companion app

These are screenshots of the **Windows companion app** (`v0.2.0-windows-preview`, Electron). It runs on your existing Windows (or Linux) desktop and provides a terminal, editor, Everything apps, environments and agent sessions. **It is not the FoxOS operating system desktop**; see the [screenshots](#screenshots-the-real-foxos-031-system) above for that. Captured with xvfb at 1600×1000 by [`apps/desktop/scripts/screenshots.js`](apps/desktop/scripts/screenshots.js).

| | |
| --- | --- |
| ![Start menu](docs/screenshots/start-menu.png)<br>Start menu: built-ins and installed Everything apps in 9 groups, each with its project's own icon | ![App center](docs/screenshots/app-center.png)<br>App center: 51 Everything apps with their upstream icons, plus built-ins, LibreOffice, tools, ACP agents |
| ![Setup wizard](docs/screenshots/setup-wizard.png)<br>First-run wizard with component picker | ![Terminal](docs/screenshots/terminal.png)<br>Terminal running `foxos` commands |
| ![Files](docs/screenshots/files.png)<br>File manager, live-synced workspace | ![Editor](docs/screenshots/editor.png)<br>Monaco editor |
| ![Browser](docs/screenshots/browser.png)<br>Browser | ![Settings → Language](docs/screenshots/settings-language-en.png)<br>Settings → Language: 简体中文 (default) / English, applies immediately |
| ![App center (English)](docs/screenshots/app-center-en.png)<br>App center in English: group names and app descriptions follow the language | ![Writer](docs/screenshots/libreoffice-writer.png)<br>LibreOffice Writer with a generated .docx |
| ![Calc](docs/screenshots/libreoffice-calc.png)<br>LibreOffice Calc: formulas and a native chart | ![Spreadsheet](docs/screenshots/everything-spreadsheet.png)<br>Everything Spreadsheet opening a workspace .xlsx (Chinese UI, shipped upstream, follows the FoxOS language) |
| ![Documents](docs/screenshots/everything-documents.png)<br>Everything Documents opening a workspace .docx | ![Whiteboard](docs/screenshots/everything-whiteboard.png)<br>Everything Whiteboard |
| ![CRM](docs/screenshots/everything-crm.png)<br>Everything CRM | ![Chess](docs/screenshots/everything-chess.png)<br>Everything Chess |
| ![ACP install](docs/screenshots/acp-agent-install.png)<br>One-click ACP agent install from the official registry | ![Install a system](docs/screenshots/environments-catalog.png)<br>Environments → Install a system (WSL2 distros, rootfs, Windows Sandbox, Hyper-V) |
| ![Alpine](docs/screenshots/environments-alpine.png)<br>A running Alpine environment with live stats | ![Audit and takeover](docs/screenshots/audit-takeover.png)<br>Activity log and human takeover (`PAUSED`) |

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

Linux: unprivileged user namespaces + overlayfs + pivot_root + seccomp, cgroup v2 when delegated (rlimit otherwise), snapshots, clones, `.foxenv` export, agents can run inside. Windows: WSL2 distro catalog with automatic WSL enablement, Windows Sandbox, Hyper-V. macOS: Virtualization.framework backend (untested on hardware). See [docs/environments.md](docs/environments.md) and the [provider protocol](docs/environment-provider-protocol.md). **Online preset systems**: preconfigured Debian 12 / Ubuntu 24.04 / FoxOS guests (desktop, Chinese, Node / Bun / Python, ACP agents, the foxos bridge) plus Windows evaluation and macOS recipes that download the official Microsoft / Apple media at install time; split downloads resume and are checked against sha256. See [docs/presets.md](docs/presets.md) and the [screenshot](docs/screenshots/env-presets-032.png).

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
