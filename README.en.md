<p align="center"><img src="assets/icons/icon-256.png" width="112" height="112" alt="FoxOS icon"></p>

<h1 align="center">FoxOS (狐狸OS)</h1>

<p align="center">A desktop operating system for agents: real desktop apps, one <code>foxos</code> command line and MCP tool set for everything, audit log and human takeover, and a home-grown isolation layer.</p>

<p align="center"><a href="README.md">中文</a> · <a href="https://github.com/gatesenman/foxos/releases/tag/v0.2.0-windows-preview">Windows preview download</a> · <a href="AGENTS.md">AGENTS.md</a> · <a href="docs/test-report.md">Test report</a></p>

![FoxOS desktop](docs/screenshots/desktop.png)

## What it is

FoxOS is a desktop program for Windows and Linux (macOS planned) that gives agents (ACP/MCP clients such as Claude Code, Codex, Gemini CLI) and humans one shared workbench:

- **Real apps**: terminal (real PTY), file manager, Monaco editor, browser, native LibreOffice windows, and the 51 open-source Everything apps.
- **One operation, three entry points**: GUI, `foxos <app> <resource> <verb> --json`, and MCP tools (stdio and Streamable HTTP) all call the same kernel command.
- **Traceable and interruptible**: every call goes to a JSONL audit log; single-writer file locks; one-click human takeover pauses all agent writes.
- **Own isolation layer**: no Docker or VM software. Linux namespaces on Linux; one-click WSL2 distros, Windows Sandbox and Hyper-V on Windows.

## Screenshots

Captured from the running desktop (xvfb, 1600×1000) with real files created in the workspace by `foxos` commands ([script](apps/desktop/scripts/screenshots.js)).

| | |
| --- | --- |
| ![App center](docs/screenshots/app-center.png)<br>App center: built-ins, LibreOffice, tools, ACP agents, 51 Everything apps in 9 groups | ![Setup wizard](docs/screenshots/setup-wizard.png)<br>First-run wizard with component picker |
| ![Terminal](docs/screenshots/terminal.png)<br>Terminal running `foxos` commands | ![Files](docs/screenshots/files.png)<br>File manager, live-synced workspace |
| ![Editor](docs/screenshots/editor.png)<br>Monaco editor | ![Browser](docs/screenshots/browser.png)<br>Browser |
| ![Writer](docs/screenshots/libreoffice-writer.png)<br>LibreOffice Writer with a generated .docx | ![Calc](docs/screenshots/libreoffice-calc.png)<br>LibreOffice Calc: formulas and a native chart |
| ![Spreadsheet](docs/screenshots/everything-spreadsheet.png)<br>Everything Spreadsheet opening a workspace .xlsx | ![Documents](docs/screenshots/everything-documents.png)<br>Everything Documents opening a workspace .docx |
| ![Whiteboard](docs/screenshots/everything-whiteboard.png)<br>Everything Whiteboard | ![CRM](docs/screenshots/everything-crm.png)<br>Everything CRM |
| ![Chess](docs/screenshots/everything-chess.png)<br>Everything Chess | ![ACP install](docs/screenshots/acp-agent-install.png)<br>One-click ACP agent install from the official registry |
| ![Install a system](docs/screenshots/environments-catalog.png)<br>Environments → Install a system (WSL2 distros, rootfs, Windows Sandbox, Hyper-V) | ![Alpine](docs/screenshots/environments-alpine.png)<br>A running Alpine environment with live stats |
| ![Audit and takeover](docs/screenshots/audit-takeover.png)<br>Activity log and human takeover (`PAUSED`) | |

## Download

Windows x64 preview: [v0.2.0-windows-preview](https://github.com/gatesenman/foxos/releases/tag/v0.2.0-windows-preview) (pre-release, not yet verified on real Windows hardware — see the [test checklist](docs/windows-test-guide.md)).

```powershell
irm https://github.com/gatesenman/foxos/releases/download/v0.2.0-windows-preview/install.ps1 | iex      # anonymous download, verifies SHA256SUMS
$env:FOXOS_PORTABLE = '1'; irm https://github.com/gatesenman/foxos/releases/download/v0.2.0-windows-preview/install.ps1 | iex   # portable
```

`$env:GITHUB_TOKEN` is optional and only helps with GitHub's anonymous API rate limit. The installer is unsigned (SmartScreen warns on first run). Linux: run from source for now; macOS: not released.

## Quick start (from source)

```bash
git clone https://github.com/gatesenman/foxos.git && cd foxos
python3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'
cd apps/desktop && npm ci && npm start
```

## For agents: CLI and MCP

See [AGENTS.md](AGENTS.md), `foxos agent-guide`, [agent guide](docs/agent-guide.md), [CLI reference](docs/cli-reference.md), [MCP reference](docs/mcp-reference.md).
Grammar `foxos <app> <resource> <verb> --json`; MCP tool names `<app>_<resource>_<verb>`; exit codes 0 OK, 1 ERROR, 2 USAGE, 3 NOT_FOUND, 4 PERMISSION_DENIED, 5 LOCKED, 6 DEPENDENCY_MISSING, 7 CONFLICT, 8 PAUSED.

## Everything apps (51)

From [HeyPuter/everything](https://github.com/HeyPuter/everything) at `0fbb88cd`. AGPL apps are built from upstream source at install time and are not modified or vendored.

<!-- apps:start -->
Runs locally: **50/51** · semantic CLI/MCP commands: **50/51** · boot e2e passed: **4/51** · GUI = CLI parity: **2/51** (details: [docs/everything-apps.md](docs/everything-apps.md))

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

Linux: unprivileged user namespaces + overlayfs + pivot_root + seccomp, cgroup v2 when delegated (rlimit otherwise), snapshots, clones, `.foxenv` export, agents can run inside. Windows: WSL2 distro catalog with automatic WSL enablement, Windows Sandbox, Hyper-V. macOS: Virtualization.framework backend (untested on hardware). See [docs/environments.md](docs/environments.md) and the [provider protocol](docs/environment-provider-protocol.md).

## Architecture

Desktop (Electron: window manager, built-in apps, Everything runtime, ACP client, app bridge) → kernel (Python `foxos`: command registry generating argparse / JSON Schema / MCP tools / docs; workspace confinement, locks, audit, takeover; apps; environment providers). See the diagram in [README.md](README.md#架构) and [docs/architecture.md](docs/architecture.md).

## Testing

`npm run test:all` at the repo root runs pytest, the Playwright + Electron end-to-end tests under xvfb and the official-MCP-SDK tests, and writes [docs/test-report.md](docs/test-report.md) (pass/fail/skip per user story, per-app coverage). No mocks.

## Roadmap

Done: kernel, audit, locks, takeover, MCP; desktop and real apps; 51 Everything apps (50 run); Linux environment runtime; Windows environment catalog; Windows x64 preview.
Next: Windows hardware verification; light sandbox level (Landlock + seccomp, Seatbelt, restricted token + job objects); Linux packages; macOS build; code signing.

## License

No license has been chosen yet (no LICENSE file). AGPL Everything apps are not distributed with this repository.
