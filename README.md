<p align="center"><img src="assets/icons/icon-256.png" width="112" height="112" alt="狐狸OS 图标"></p>

<h1 align="center">狐狸OS（FoxOS）</h1>

<p align="center">给智能体使用的桌面操作系统：真实的桌面与应用、统一的 <code>foxos</code> 命令与 MCP 工具、审计与人工接管、自研隔离环境。</p>

<p align="center">
  <a href="https://github.com/gatesenman/foxos/releases/tag/v0.2.0-windows-preview">下载 Windows 预览版</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="AGENTS.md">智能体接入</a> ·
  <a href="docs/test-report.md">测试报告</a> ·
  <a href="README.en.md">English</a>
</p>

![狐狸OS 桌面：快捷方式、标题栏与任务栏显示各程序自带的图标](docs/screenshots/desktop.png)

## 狐狸OS 是什么

狐狸OS 是运行在 Windows、Linux（以及计划中的 macOS）上的桌面程序。它给智能体（Claude Code、Codex、Gemini CLI 等 ACP / MCP 客户端）
和人一个共同的工作台：

- **真实的应用**：终端（真实 PTY）、文件管理器、Monaco 编辑器、浏览器、LibreOffice 原生窗口，以及 51 个 Everything 开源应用（表格、文档、白板、CRM、国际象棋……）。
- **同一套操作，三个入口**：图形界面、`foxos <应用> <资源> <动作> --json` 命令、MCP 工具（stdio 与 Streamable HTTP），调用的是同一个内核命令。
- **可追溯、可接管**：每次调用都写入审计日志；同一文件单写者锁；一键“人工接管”让所有智能体的写操作暂停。
- **自研隔离环境**：不依赖 Docker / 虚拟机软件；Linux 上用命名空间运行官方发行版根文件系统，Windows 上一键安装 WSL2 发行版、Windows Sandbox、Hyper-V 虚拟机。
- **内置智能体熟悉的东西**：标准 `.xlsx` / `.docx` / `.pptx`、Excel 公式、经典 CLI 约定（子命令、`--help`、`--json`、稳定退出码）、git、Python、Node。

## 截图

所有截图都来自运行中的真实桌面（xvfb，1600×1000），内容是工作空间里用 `foxos` 命令创建的真实文件。截图脚本：[`apps/desktop/scripts/screenshots.js`](apps/desktop/scripts/screenshots.js)。

| | |
| --- | --- |
| ![开始菜单](docs/screenshots/start-menu.png)<br>**开始菜单**：内置程序与按 9 个分组列出的已安装 Everything 应用，每个程序显示其开源项目自带的图标 | ![应用中心](docs/screenshots/app-center.png)<br>**应用中心**：51 个 Everything 应用显示各自上游的图标；另有内置应用、LibreOffice、开发工具与 ACP 智能体 |
| ![安装向导](docs/screenshots/setup-wizard.png)<br>**首次运行安装向导**：检测并在线安装 LibreOffice、Python 办公库、Node.js、git、环境与 Everything 分组 | ![终端](docs/screenshots/terminal.png)<br>**终端**：真实 PTY；`foxos` 命令直接读写工作空间里的表格、文档和环境 |
| ![文件管理器](docs/screenshots/files.png)<br>**文件管理器**：工作空间实时同步，CLI、MCP、智能体的修改立即出现 | ![编辑器](docs/screenshots/editor.png)<br>**Monaco 编辑器**：语法高亮，保存到工作空间 |
| ![浏览器](docs/screenshots/browser.png)<br>**浏览器**：内置网页浏览器 | ![设置 → 语言](docs/screenshots/settings-language.png)<br>**设置 → 语言**：简体中文（默认）/ English，立即切换并保存；安装向导第一步也可选 |
| ![English 界面：桌面](docs/screenshots/desktop-en.png)<br>**English 界面**：切换后外壳、窗口、会话面板全部为英文 | ![English 界面：应用中心](docs/screenshots/app-center-en.png)<br>**English 界面**：应用中心的分组名与应用说明随语言切换 |
| ![LibreOffice Writer](docs/screenshots/libreoffice-writer.png)<br>**LibreOffice Writer**：打开由 `foxos docs` 生成的周报 .docx | ![LibreOffice Calc](docs/screenshots/libreoffice-calc.png)<br>**LibreOffice Calc**：`foxos sheets` 写入的公式与原生图表 |
| ![Everything 表格](docs/screenshots/everything-spreadsheet.png)<br>**Everything · 表格**：打开工作空间里的 `2026年销售.xlsx`；上游自带中文界面，随狐狸OS 语言切换 | ![Everything 文档](docs/screenshots/everything-documents.png)<br>**Everything · 文档**：打开 `项目周报.docx` |
| ![Everything 白板](docs/screenshots/everything-whiteboard.png)<br>**Everything · 白板** | ![Everything CRM](docs/screenshots/everything-crm.png)<br>**Everything · CRM** |
| ![Everything 国际象棋](docs/screenshots/everything-chess.png)<br>**Everything · 国际象棋** | ![ACP 智能体一键安装](docs/screenshots/acp-agent-install.png)<br>**ACP 智能体一键安装**：从 ACP 官方注册表安装 Gemini CLI，卡片内显示安装日志，装好即可“启动会话” |
| ![安装系统](docs/screenshots/environments-catalog.png)<br>**环境 → 安装系统**：WSL2 发行版、LXC / 官方根文件系统、Windows Sandbox、Hyper-V；顶部是本机能力检查 | ![Alpine 环境](docs/screenshots/environments-alpine.png)<br>**环境**：从目录一键安装并运行中的 Alpine，实时资源、快照、自定义操作 |
| ![审计与人工接管](docs/screenshots/audit-takeover.png)<br>**活动与人工接管**：所有操作进审计日志；接管后智能体写操作被拒绝（`PAUSED`） | |

## 功能

| 领域 | 内容 |
| --- | --- |
| 桌面 | 窗口管理（拖动、缩放、最大化、任务栏）、开始菜单、全局搜索（应用 + 工作空间文件）、会话恢复；无 emoji |
| 程序图标 | 每个程序显示它自己的开源项目自带的图标：Everything 应用用上游 `icon-128.png`（MIT 应用随附，AGPL 应用安装后从上游组件读取）、LibreOffice 用本机安装的图标、终端用系统终端图标、编辑器用 VS Code / Code - OSS 图标、浏览器用 Electron 图标、ACP 智能体用注册表 `icon` 字段；狐狸OS 自己的程序（文件、设置、环境、应用中心）保留狐狸OS 风格；线性字体图标只用于按钮等控件。来源与许可见 [third-party-icons/NOTICE.md](apps/desktop/src/third-party-icons/NOTICE.md) |
| 内置应用 | 终端（node-pty / ConPTY）、文件管理器、Monaco 编辑器、浏览器、应用中心、设置、安装向导、环境 |
| 办公 | `foxos sheets` / `docs` / `slides` 读写标准 .xlsx / .docx / .pptx（公式、原生图表、表格、备注），LibreOffice 原生窗口打开、求值与导出 |
| Everything 应用 | 51 个开源应用（9 个分组），本机构建运行；每个应用有从界面实际遍历出的语义命令（`foxos <应用> <资源> <动作>`），见 [docs/everything-apps.md](docs/everything-apps.md) 与 [docs/operations/](docs/operations/) |
| 智能体 | ACP 客户端（会话面板、运行位置：宿主或某个环境）、ACP 官方注册表一键安装、MCP 服务（stdio / Streamable HTTP、令牌、compact / full 工具集） |
| 安全与协作 | 工作空间约束（拒绝 `../`、符号链接逃逸、保留目录）、JSONL 审计日志、文件锁、原子保存与版本、人工接管（`PAUSED`，退出码 8） |
| 环境 | Linux 命名空间运行时（overlayfs、pivot_root、seccomp、cgroup v2 / rlimit）、`.foxenv` 镜像、快照、克隆、导出；Windows：WSL2、Windows Sandbox、Hyper-V；提供者协议 |
| 多语言 | 简体中文（默认）与 English：安装向导第一步与设置里切换，立即生效并保存；`foxos` 命令行、MCP 工具说明与内核错误消息跟随 `--lang` / `FOXOS_LANG`（JSON 字段名与错误码不变）；Windows 安装程序与 `install.ps1` 中英双语；Everything 应用通过 Chromium 语言接收狐狸OS 语言，上游提供中文界面的（spreadsheet）随之切换，其余在应用中心标“英文界面”（逐个记录见 [docs/everything-apps.md](docs/everything-apps.md)）。词条在 `apps/desktop/src/locales/` 与 `packages/core/foxos/data/locales/` |
| 滚动条 | 不用系统默认滚动条：外壳、所有窗口与 Everything 应用（注入到每个 webview）统一用狐狸OS 细滚动条——轨道透明、平时隐藏、指向或滚动时出现、指向时加宽、拖动时为强调色，随深浅色主题变化；Monaco 与终端（xterm）使用相同尺寸与颜色 |
| 安装 | 首次运行向导按平台在线安装组件；Windows 安装包自带 Python 与办公库 |

## 下载

**Windows x64 预览版**：[v0.2.0-windows-preview](https://github.com/gatesenman/foxos/releases/tag/v0.2.0-windows-preview)（预发布，尚未在 Windows 实机上验收，见 [Windows 测试清单](docs/windows-test-guide.md)）

| 文件 | 说明 |
| --- | --- |
| `FoxOS-Setup-0.2.0-x64.exe` | 安装程序（可选安装目录，按用户安装；简体中文 / English，按系统语言选择，默认中文） |
| `FoxOS-0.2.0-win-x64.zip` | 便携版 |
| `install.ps1` | 在线安装：匿名下载、校验 `SHA256SUMS`、安装 |
| `SHA256SUMS` | 校验值 |

```powershell
# 一行安装（匿名下载，不需要令牌）
irm https://github.com/gatesenman/foxos/releases/download/v0.2.0-windows-preview/install.ps1 | iex
# 便携版
$env:FOXOS_PORTABLE = '1'; irm https://github.com/gatesenman/foxos/releases/download/v0.2.0-windows-preview/install.ps1 | iex
# 下载脚本后带参数：-Portable / -Silent / -Dir <目录> / -DownloadOnly / -Lang en-US（提示语言，默认中文；也可设 $env:FOXOS_LANG）
powershell -ExecutionPolicy Bypass -File install.ps1 -Portable
```

`$env:GITHUB_TOKEN` 可选，只在遇到 GitHub 匿名 API 频率限制（每小时 60 次）时设置。安装包未签名，首次运行时 SmartScreen 会提示，选“更多信息 → 仍要运行”。

Linux：目前从源码运行（见下），安装包尚未发布。macOS：未发布、未测试。

## 快速开始

从源码运行（Linux，Windows 同理）：

```bash
git clone https://github.com/gatesenman/foxos.git && cd foxos
python3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'
cd apps/desktop && npm ci && npm start          # 桌面；首次运行会打开安装向导
```

只用命令行：

```bash
export PYTHONPATH=$PWD/packages/core
python3 -m foxos --workspace ~/FoxOS/workspace sheets create 销售.xlsx
python3 -m foxos --workspace ~/FoxOS/workspace sheets write 销售.xlsx A1=月份 B1=金额 A2=1月 B2=120 'B3==SUM(B2:B2)'
python3 -m foxos --workspace ~/FoxOS/workspace env install alpine dev && python3 -m foxos env start dev
python3 -m foxos help --json      # 完整能力目录
```

## 给智能体：CLI 与 MCP

- 入门：[AGENTS.md](AGENTS.md)，或在终端运行 `foxos agent-guide`（含 Claude Code、Codex、Gemini CLI 的接入配置）
- 文档：[智能体指南](docs/agent-guide.md) · [命令参考](docs/cli-reference.md) · [MCP 工具参考](docs/mcp-reference.md)
- 语言：命令说明与消息默认中文，`--lang en-US` 或 `FOXOS_LANG=en-US` 切换为英文；JSON 字段名、错误码、命令名不随语言变化
- 约定：`foxos <应用> <资源> <动作> [--json]`；MCP 工具名 `<应用>_<资源>_<动作>`；退出码 0 成功、1 错误、2 用法、3 不存在、4 拒绝、5 被锁、6 缺依赖、7 冲突、8 已暂停

```bash
foxos --workspace ~/FoxOS/workspace mcp                                    # stdio
FOXOS_MCP_TOKEN=<令牌> foxos --workspace ~/FoxOS/workspace mcp --http 127.0.0.1:8765   # Streamable HTTP（POST /mcp）
foxos mcp --profile compact                                                # 精简工具集（通用 + everything_run）
```

## Everything 应用（51 个）

来自 [HeyPuter/everything](https://github.com/HeyPuter/everything)（提交 `0fbb88cd`）。AGPL 应用在安装时从上游源码在本机构建，狐狸OS 不修改、不内置其源码。

<!-- apps:start -->
本机可运行 **50/51** · 有语义命令（CLI / MCP）**50/51** · 启动测试通过 **50/51** · 界面与命令等价 **49/51**（明细：[docs/everything-apps.md](docs/everything-apps.md)）

| 分组 | 应用（括号内为语义命令数） |
| --- | --- |
| 办公 Office | Spreadsheet `spreadsheet` (371 · AGPL)<br>Documents `documents` (311)<br>Presentation `presentation` (284 · AGPL)<br>Whiteboard `whiteboard` (26 · AGPL)<br>PDF `pdf` (85 · AGPL)<br>Notes `notes` (136 · AGPL)<br>Records `records` (16) |
| 协作 Collaboration | Meetings `meetings` (17)<br>Teamchat `teamchat` (6)<br>Email `email` (2 · AGPL)<br>Contacts `contacts` (28)<br>Calendar `calendar` (36)<br>Signatures `signatures` (29) |
| 创意 Creative Tools | Photo Studio `photo-studio` (104)<br>Video Studio `video-studio` (34 · AGPL)<br>Vector Studio `vector-studio` (90)<br>Audio Studio `audio-studio` (148)<br>Music Studio `music-studio` (266)<br>3D Studio `3d` (230 · AGPL) |
| 工程 Engineering | CAD `cad` (180 · AGPL)<br>Parametric `parametric` (33 · AGPL)<br>Circuits `circuits` (39 · AGPL)<br>Building Design `building-design` (1 · AGPL) |
| 效率 Productivity | Tasks `tasks` (58)<br>Projects `projects` (50)<br>Wiki `wiki` (60)<br>Time Tracking `time-tracking` (71)<br>Surveys `survey` (28) |
| 财务 Finance | Accounting `accounting` (45)<br>Invoicing `invoicing` (20)<br>Expenses `expense` (17)<br>Cap Table `cap-table` (27) |
| 业务 Business | CRM `crm` (16)<br>Help Desk `help-desk` (6)<br>Contracts `contracts` (14)<br>Point of Sale `pos` (17)<br>Inventory `inventory` (17)<br>Assets `assets` (0) — 上游缺源码<br>Hiring `hiring` (22)<br>Shifts `shifts` (17)<br>Childcare `childcare` (39)<br>Field Service `field-service` (40)<br>Legal `legal` (43)<br>Fleet `fleet` (41)<br>Property Management `property-management` (45) |
| 开发 Developer Tools | API Client `api-client` (59) |
| 游戏 Games | Chess `chess` (30)<br>Backgammon `backgammon` (27)<br>Checkers `checkers` (21)<br>Solitaire `solitaire` (9)<br>Sudoku `sudoku` (39) |
<!-- apps:end -->

## 环境

“环境”应用和 `foxos env` 命令管理隔离环境，详见 [docs/environments.md](docs/environments.md)：

- **Linux**：自研运行时，无特权用户命名空间 + overlayfs + pivot_root + seccomp，cgroup v2 可委派时限制资源，否则用 rlimit；工作空间挂载到 `/workspace`；快照、克隆、导出为 `.foxenv`；智能体可以在环境里运行
- **Windows**：一键安装 WSL2 发行版（Ubuntu、Debian、Kali、openSUSE、Fedora、AlmaLinux、Rocky、Oracle Linux、Arch、Alpine…），自动检测并启用 WSL；Windows Sandbox；Hyper-V 虚拟机
- **macOS**：Virtualization.framework 后端（代码与单元测试，未在硬件验证）；macOS 来宾按 Apple 许可禁用
- 提供者协议与系统目录：[docs/environment-provider-protocol.md](docs/environment-provider-protocol.md)；参考项目与许可证核对：[docs/virtualization-references.md](docs/virtualization-references.md)

轻量隔离（`foxos sandbox`）：不建独立系统，直接用宿主上的工具运行，但只能读写工作空间、可选不联网（Linux Landlock + seccomp，macOS Seatbelt，Windows 受限令牌 / AppContainer + 作业对象）。会话面板“运行位置”可选“轻量沙箱”。见 [docs/sandbox.md](docs/sandbox.md)。

## 架构

```mermaid
flowchart LR
  subgraph Clients[调用方]
    H[人：桌面界面]
    A[ACP 智能体<br>Claude Code / Codex / Gemini CLI]
    M[MCP 客户端]
    T[终端 / 脚本]
  end
  subgraph Desktop[桌面 Electron]
    WM[窗口管理 / 内置应用]
    EV[Everything 应用<br>foxapp:// + Puter 运行时]
    ACP[ACP 客户端]
    BR[应用桥<br>界面操作与读取]
  end
  subgraph Core[内核 Python：foxos]
    REG[命令注册表<br>argparse / JSON Schema / MCP 工具 / 文档]
    WS[工作空间约束 · 锁 · 原子保存]
    AU[审计日志 · 人工接管]
    APPS[sheets / docs / slides / files / everything / env …]
    ENV[环境提供者<br>linux-ns / wsl2 / windows-sandbox / hyperv / macos-vz]
  end
  H --> WM
  A <--> ACP
  ACP -->|foxos 命令 / HTTP MCP| REG
  M -->|stdio / Streamable HTTP| REG
  T -->|foxos CLI| REG
  WM -->|IPC| REG
  REG --> WS --> APPS
  REG --> AU
  APPS -->|控制通道| BR --> EV
  APPS --> ENV
  APPS --> LO[LibreOffice]
```

更多：[docs/architecture.md](docs/architecture.md)。

## 测试

```bash
npm run test:all      # 仓库根目录：pytest + 桌面端到端测试（Playwright + Electron，xvfb）+ MCP 官方 SDK 测试，生成 docs/test-report.md
```

- 测试不使用模拟：真实文件、真实 LibreOffice、真实 Electron、真实环境运行时、官方 MCP SDK 客户端
- 最近一次报告（Linux）：140 个用例 134 通过、1 失败、4 跳过、1 个已知上游缺陷；32 个用户故事 29 通过；Everything 应用 50/51 本地启动、49/51 界面与 CLI 等价、51/51 MCP 调用成功；程序图标 Everything 51/51、内置程序 6/6、ACP 智能体 45/45。详见 [测试报告](docs/test-report.md)
- 用户故事与测试一一对应（US-编号），报告列出每个故事的通过 / 失败 / 跳过、51 个应用的覆盖与每个应用的操作覆盖：[docs/test-report.md](docs/test-report.md)
- Windows 专用测试：命令行契约单元测试在 Linux 上运行；实机测试见 [docs/windows-test-guide.md](docs/windows-test-guide.md)

## 路线图

- [x] 命令内核、审计、锁、人工接管、MCP（stdio / HTTP）
- [x] 桌面、真实终端、文件、编辑器、浏览器、LibreOffice
- [x] 51 个 Everything 应用（50 个可运行）与语义命令
- [x] Linux 环境运行时；Windows 环境目录与提供者协议
- [x] Windows x64 预览版安装包
- [ ] Windows 实机验收（进行中）
- [x] 轻量沙箱档：Linux Landlock + seccomp（已测试）；macOS Seatbelt、Windows 受限令牌 / AppContainer + 作业对象（代码与单元测试，待实机验证）
- [ ] Linux 安装包与发布、macOS 构建
- [x] 中英文界面（默认中文）与狐狸OS 细滚动条
- [ ] 代码签名、自动更新

## 许可

仓库目前没有选定许可证（未包含 LICENSE 文件）。Everything 中的 AGPL 应用不随仓库分发，安装时从上游获取并保持原许可证；
WSL 发行版清单快照来自 microsoft/WSL（MIT，声明见 `packages/core/foxos/data/wsl/NOTICE.md`）。
