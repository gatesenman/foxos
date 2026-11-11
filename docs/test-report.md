# 测试报告

由 `npm run test:all`（[scripts/test_all.py](../scripts/test_all.py)）生成，不使用模拟：pytest 调用真实 CLI / 内核，桌面端到端测试用 Playwright 驱动真实的 Electron 桌面，MCP 测试使用官方 MCP SDK 作为客户端。

- 时间：2026-11-11 14:39（UTC+8）　提交：`f40a775`
- 环境：Linux 6.12.113+（x86_64），Python 3.13.5，Node v24.22.1，Landlock ABI 6
- 未覆盖：Windows 与 macOS 实机（本报告在 Linux 上生成；Windows 代码路径另有 wine 下的测试，见 [sandbox.md](sandbox.md)、[windows-test-guide.md](windows-test-guide.md)）

## 总览

| | 通过 | 失败 | 跳过 | 已知上游缺陷 |
| --- | --- | --- | --- | --- |
| 测试用例（140） | 134 | 1 | 4 | 1 |
| 用户故事（32） | 29 | 1 | 1 | 1 |

- Everything 应用：**50/51** 在桌面里本地启动，**49/51** 通过“界面操作与 CLI 等价”检查，**51/51** 通过 MCP（官方 SDK）调用成功；1 个失败，1 个跳过，1 个为已知上游缺陷。
- 操作清单：51 个应用共 **3350** 项操作，其中 **3350** 项有 CLI / MCP 绑定；测试中实际执行并比对结果的有 **50** 项（每个应用一项等价检查）。
- MCP：stdio 列出 4320 个工具（62 个应用），逐应用调用 63/63 成功；Streamable HTTP（compact）69 个工具；SDK 1.32.2。

## 用户故事

| 故事 | 内容 | 结果 | 通过 | 失败 | 跳过 |
| --- | --- | --- | --- | --- | --- |
| US-01 | 所有命令只能操作工作空间内的路径（越界、符号链接逃逸、保留目录被拒绝） | 通过 | 8 | 0 | 0 |
| US-02 | 文件管理：列出、读写、重命名、删除进回收站并恢复 | 通过 | 2 | 0 | 0 |
| US-03 | 单写者文件锁：并发写不丢更新，锁等待，进程死亡后回收 | 通过 | 4 | 0 | 0 |
| US-04 | 人工接管：暂停后智能体的写操作返回 PAUSED，身份写入审计 | 通过 | 2 | 0 | 0 |
| US-05 | 表格（xlsx）：创建、写公式、计算值、导出、错误码稳定 | 通过 | 5 | 0 | 0 |
| US-06 | 文档（docx）与演示文稿（pptx）：创建、编辑、导出 PDF | 通过 | 3 | 0 | 0 |
| US-07 | 命令目录：help --json、示例可解析、工具导出、参考文档与注册表一致 | 通过 | 6 | 0 | 0 |
| US-08 | 桌面冒烟：空工作空间启动桌面并渲染 | 通过 | 1 | 0 | 0 |
| US-10 | MCP（stdio）：官方 SDK 列出工具并对每个应用调用一次，与 CLI 同一内核 | 通过 | 2 | 0 | 0 |
| US-11 | MCP（Streamable HTTP）：令牌认证、compact 工具集、everything_run | 通过 | 1 | 0 | 0 |
| US-30 | 环境：创建、启动、执行、停止 | 通过 | 1 | 0 | 0 |
| US-31 | 环境隔离规则（文件系统、进程、网络、主机名） | 通过 | 1 | 0 | 0 |
| US-32 | 环境快照与恢复 | 通过 | 1 | 0 | 0 |
| US-33 | 环境克隆、导出 .foxenv、导入 | 通过 | 1 | 0 | 0 |
| US-34 | 环境挂载、资源限制、自定义操作、日志 | 通过 | 1 | 0 | 0 |
| US-35 | WSL2 后端命令 | 通过 | 1 | 0 | 0 |
| US-36 | macOS Virtualization.framework 后端配置 | 通过 | 1 | 0 | 0 |
| US-37 | 环境应用：GUI 操作与 CLI 状态一致 | 通过 | 1 | 0 | 0 |
| US-38 | Windows 环境目录与提供者（WSL2 / Windows 沙盒 / Hyper-V）：解析、计划、外部提供者协议 | 通过 | 28 | 0 | 0 |
| US-39 | Windows 实机：WSL 安装 Ubuntu、doctor（需要 Windows 硬件） | 跳过 | 0 | 0 | 2 |
| US-40 | Everything 办公类应用：本地打开，界面操作与 CLI 等价 | 通过 | 7 | 0 | 0 |
| US-41 | Everything 协作类应用 | 通过 | 6 | 0 | 0 |
| US-42 | Everything 创作类应用 | 通过（含已知上游缺陷） | 6 | 0 | 0 |
| US-43 | Everything 工程类应用 | 通过 | 4 | 0 | 0 |
| US-44 | Everything 效率类应用 | 失败 | 4 | 1 | 0 |
| US-45 | Everything 财务类应用 | 通过 | 4 | 0 | 0 |
| US-46 | Everything 商务类应用 | 通过 | 12 | 0 | 1 |
| US-47 | Everything 开发类应用 | 通过 | 1 | 0 | 0 |
| US-48 | Everything 游戏类应用 | 通过 | 5 | 0 | 0 |
| US-50 | 安装系统：目录与一键安装（Linux 宿主上真实安装 Alpine） | 通过 | 1 | 0 | 0 |
| US-52 | 轻量隔离：Landlock + seccomp 真实限制；智能体在轻量沙箱中运行；Seatbelt / Windows 策略生成 | 通过 | 14 | 0 | 1 |
| US-53 | 程序图标：每个程序显示其开源项目自带的图标（Everything 上游 / LibreOffice / 系统终端 / Code - OSS / Electron / ACP 注册表），缺失时退回并报告 | 通过 | 1 | 0 | 0 |
| US-60 | 真实 XFCE 会话：列出/聚焦/移动/缩放窗口，键入与点击，人工接管（CLI 与 MCP） | 通过 | 4 | 0 | 0 |
| US-61 | linux-kvm 来宾与 foxos env run / desktop-attach（至少一个 Linux 来宾路径） | 通过 | 4 | 0 | 0 |

### 失败、跳过与已知缺陷的用例

| 故事 | 用例 | 结果 | 说明 |
| --- | --- | --- | --- |
| US-39 | `test_env_windows.py` test_hw_wsl_install_ubuntu | 跳过 | pending：需要 Windows 实机（见 docs/windows-test-guide.md） |
| US-39 | `test_env_windows.py` test_hw_doctor | 跳过 | pending：需要 Windows 实机（见 docs/windows-test-guide.md） |
| US-42 | `everything.e2e.js` US-42 photo-studio：本地打开，界面操作与 CLI 等价 | 通过（含已知上游缺陷） | 上游缺陷：src/app/pointer.ts 中 #viewport 的 pointerdown 处理只排除 button / input / .canvas-ui，开始页的“Describe an edit”文本框（textarea）被鼠标点击时焦点被抢到画布，用鼠标无法输入；CLI 的 set 不经过指针事件，所以结果不同 |
| US-44 | `everything.e2e.js` US-44 tasks：本地打开，界面操作与 CLI 等价 | 失败 | 只在 CLI 结果中出现：combobox/List/<id>/ |
| US-46 | `everything.e2e.js` US-46 assets：本地打开，界面操作与 CLI 等价 | 跳过 | 上游提交 0fbb88cd 的 src/assets 只有 index.html/package.json/vite.config.js，缺少 index.html 引用的 /src/main.js（GitHub contents API 对 src/assets/src 返回 404），因此无法构建。 |
| US-52 | `test_sandbox.py` test_windows_code_path_under_wine | 跳过 | 设置 FOXOS_TEST_WINE / FOXOS_TEST_WINE_PYTHON 后在 wine 中运行 Windows 代码路径 |

## 操作系统会话与环境（2026-11-11 21:55，Asia/Shanghai）

本次打磨 XFCE 桌面外观并重做 ISO（0.3.1）后，在同一 Linux 构建盒上重跑了 `npm run test:os`（US-60 / US-61），共 **8 通过、0 失败、0 跳过**（83.11 秒，最后一次在最终 ISO 构建之后运行）。**没有**重跑 Electron 桌面的 Everything 端到端；上表中 US-01–US-53 的 Everything 结果仍是 2026-11-11 14:39 那一次 `test:all`。

- **US-60**（4 通过）：`packages/core/tests/test_os_session.py`。假后端覆盖列出、聚焦、移动、缩放、键入、点击、截图、关闭，以及 `desktop` / `session` 人工接管（智能体写操作返回 `PAUSED`）；新增用例确认不加 `--json` 时 `foxos desktop windows` / `session status` 也给人输出窗口列表与会话状态（之前是空输出）。MCP 工具目录含 `desktop_windows`、`desktop_move`、`session_takeover`。另在本机用 **Xvfb + xfwm4** 启动真实 XFCE 窗口管理器，打开两扇 xfce4-terminal 窗口，经 `wmctrl` 列出/聚焦/关闭/移动/缩放，用 `xdotool` 键入与点击，用 `scrot` 截图。程序化移动与缩放在 X11 上可用。
- **ISO 0.3.1 引导核对**（手动，非默认测试）：在本机以显式 `FOXOS_ALLOW_TEST_VMM=qemu-tcg`（TCG 软件模拟，KVM 在此宿主不可用）引导最终发布的 `FoxOS-0.3.1-amd64.iso`（1562474496 字节，SHA-256 `7acb74c92d159034966821900d43ddeec1815d0d7456d57232811371c31b4500`，Release v0.3.1-os-preview），Live 会话自动登录进 XFCE：终端里 `whoami` 为 `foxos`，`$XDG_CURRENT_DESKTOP $LANG` 为 `XFCE zh_CN.UTF-8`，`foxos desktop status` 报告 `backend: x11`、`wmctrl` / `xdotool` / `scrot` 齐全；Whisker 开始菜单为中文（收藏夹 / 最近使用 / 全部应用程序），图标为 Papirus。截图见 `docs/screenshots/os-live-boot.png`。
- **截图**：`docs/screenshots/os-desktop.png`、`os-desktop-session.png`、`os-terminal.png`、`os-editor.png` 由 `scripts/os/tools/shoot-desktop.sh` 生成：在 ISO 构建出的根文件系统上叠一层只读 overlay，以 Live 用户 `foxos`、`zh_CN.UTF-8`、主机名 `foxos` 用 `startxfce4` 启动真实会话（Xvfb 1920×1080），不是合成图。
- **US-61**（4 通过）：`packages/core/tests/test_os_kvm.py`。`linux-kvm` 已登记为内置提供者；Linux 目录条目（如 Alpine）含该提供者；`foxos env run --iso --no-start` 与 `foxos env desktop-attach` 命令/MCP 已接通。此构建盒的 `/dev/kvm` 存在，但内核曾出现 `kvm_arch_vcpu_create` BUG，`foxos env doctor --provider linux-kvm` 会如实报告不可用；**不会**在未设置 `FOXOS_ALLOW_TEST_VMM=qemu-tcg` 时改用 QEMU。产品路径仍是 cloud-hypervisor + KVM，来宾桌面走 wayvnc。默认测试套件不引导狐狸OS ISO（太慢）；在支持 KVM 的机器上可用该 ISO 或目录中的 Linux 系统做来宾桌面。复现：`npm run test:os`。

## 智能体、连接器、多机与运行环境（2026-11-12 01:00，Asia/Shanghai）

在合并主线（`bf5b1a6`）之后的分支上运行 `packages/core` 的全部 pytest：**111 通过、1 失败、3 跳过**（13 分 33 秒）。失败的是 US-61 `test_os_kvm.py`：这台构建盒上 `/dev/kvm` 存在但当前用户不可读写，是环境原因，以前就是这样。跳过的 3 个仍是 Windows 实机与 wine 用例。Electron 桌面端到端（Playwright）这次**没有**重跑；`apps/desktop` 的 `lint:i18n` 通过（511 个词条，0 错误）。

| 故事 | 测试 | 结果 |
|---|---|---|
| US-100–US-108 | `test_bots.py`（9 个）：智能体增删改、每个智能体的设置、真实 ACP 回合与审批卡片、委托、pstack、记忆与例程、暂停、聊天服务 SSE、真实无头 Chrome 里的界面（中英文） | 通过 |
| US-109–US-112 | `test_connectors.py`（4 个）：目录与 stdio MCP、OAuth 2.1（本地真实授权服务，PKCE、动态注册、刷新）、Bearer 令牌、Exa 真实调用 | 通过 |
| US-113–US-115 | `test_machines.py`（3 个）：两个真实 `machine serve` 被控端；配对码、指纹、双向 TLS；一个智能体控制两台；两个智能体共用一台（LOCKED、CONFLICT、PAUSED、撤销） | 通过 |
| US-116 | `test_acp_real.py`：从 GitHub 下载 opencode 2.2.7（sha256 校验），真实 ACP 握手与会话 | 通过 |
| US-117–US-118 | `test_os_runtime.py`：镜像 chroot 的 overlay 里（同一份 hook 30/35），以用户 foxos 检查版本、PEP 668、ACP 握手 | 通过 |

没有用真实模型账号跑过回答。Gemini CLI、codex-acp、Qwen Code、Cursor CLI 的握手结果是「需要登录」；opencode 和 claude-agent-acp 能建立会话。详见 [agent-runtime.md](agent-runtime.md)。截图在 `docs/screenshots/bots-*.png`，是 overlay 里真实 XFCE 会话中的「智能体」窗口（Firefox 后备浏览器）。

## Everything 应用覆盖（51 个）

等价检查：同一个操作分别用真实鼠标 / 键盘事件（GUI）和 `foxos` CLI 执行，两次结束后的界面状态与应用数据必须一致。操作数来自 [操作清单](operations/)。

| 应用 | 分组 | 启动 | 等价检查 | 检查的操作 | 清单操作 | 有 CLI / MCP 绑定 | 测试中执行 | MCP 调用 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Spreadsheet (`spreadsheet`) | 办公 | 通过 | 一致 | `foxos spreadsheet cell-reference set foxos parity` | 371 | 371 | 1 | 通过 |  |
| Documents (`documents`) | 办公 | 通过 | 一致 | `foxos documents document-name set foxos parity` | 311 | 311 | 1 | 通过 |  |
| Presentation (`presentation`) | 办公 | 通过 | 一致 | `foxos presentation speaker-notes set foxos parity` | 284 | 284 | 1 | 通过 |  |
| Whiteboard (`whiteboard`) | 办公 | 通过 | 一致 | `foxos whiteboard search-boards set foxos parity` | 26 | 26 | 1 | 通过 |  |
| PDF (`pdf`) | 办公 | 通过 | 一致 | `foxos pdf page-number set 2` | 85 | 85 | 1 | 通过 |  |
| Notes (`notes`) | 办公 | 通过 | 一致 | `foxos notes insert create` | 136 | 136 | 1 | 通过 |  |
| Records (`records`) | 办公 | 通过 | 一致 | `foxos records search-bases set foxos parity` | 16 | 16 | 1 | 通过 |  |
| Meetings (`meetings`) | 协作 | 通过 | 一致 | `foxos meetings meeting-code-or-link set foxos parity` | 17 | 17 | 1 | 通过 |  |
| Teamchat (`teamchat`) | 协作 | 通过 | 一致 | `foxos teamchat close close` | 6 | 6 | 1 | 通过 |  |
| Email (`email`) | 协作 | 通过 | 一致 | `foxos email grant-read-access activate` | 2 | 2 | 1 | 通过 |  |
| Contacts (`contacts`) | 协作 | 通过 | 一致 | `foxos contacts contact create` | 28 | 28 | 1 | 通过 |  |
| Calendar (`calendar`) | 协作 | 通过 | 一致 | `foxos calendar create create` | 36 | 36 | 1 | 通过 |  |
| Signatures (`signatures`) | 协作 | 通过 | 一致 | `foxos signatures set-up-account activate` | 29 | 29 | 1 | 通过 |  |
| Photo Studio (`photo-studio`) | 创意 | 通过 | 不一致 | `foxos photo-studio describe-edit set foxos parity` | 104 | 104 | 1 | 通过 | 上游缺陷：src/app/pointer.ts 中 #viewport 的 pointerdown 处理只排除 button / input / .canvas-ui，开始页的“Describe an edit”文本框（textarea）被鼠标点击时焦点被抢到画布，用鼠标无法输入；CLI 的 set 不经过指针事件，所 |
| Video Studio (`video-studio`) | 创意 | 通过 | 一致 | `foxos video-studio search-projects set foxos parity` | 34 | 34 | 1 | 通过 |  |
| Vector Studio (`vector-studio`) | 创意 | 通过 | 一致 | `foxos vector-studio single-or-double-column-tools toggle` | 90 | 90 | 1 | 通过 |  |
| Audio Studio (`audio-studio`) | 创意 | 通过 | 一致 | `foxos audio-studio search-commands set foxos parity` | 148 | 148 | 1 | 通过 |  |
| Music Studio (`music-studio`) | 创意 | 通过 | 一致 | `foxos music-studio add create` | 266 | 266 | 1 | 通过 |  |
| 3D Studio (`3d`) | 创意 | 通过 | 一致 | `foxos 3d default activate` | 230 | 230 | 1 | 通过 |  |
| CAD (`cad`) | 工程 | 通过 | 一致 | `foxos cad drawing create` | 180 | 180 | 1 | 通过 |  |
| Parametric (`parametric`) | 工程 | 通过 | 一致 | `foxos parametric insert create` | 33 | 33 | 1 | 通过 |  |
| Circuits (`circuits`) | 工程 | 通过 | 一致 | `foxos circuits project create` | 39 | 39 | 1 | 通过 |  |
| Building Design (`building-design`) | 工程 | 通过 | 一致 | `foxos building-design it dismiss` | 1 | 1 | 1 | 通过 |  |
| Tasks (`tasks`) | 效率 | 通过 | 一致 | `foxos tasks first-task create` | 58 | 58 | 1 | 通过 |  |
| Projects (`projects`) | 效率 | 通过 | 一致 | `foxos projects first-project create` | 50 | 50 | 1 | 通过 |  |
| Wiki (`wiki`) | 效率 | 通过 | 一致 | `foxos wiki getting-started set foxos parity` | 60 | 60 | 1 | 通过 |  |
| Time Tracking (`time-tracking`) | 效率 | 通过 | 一致 | `foxos time-tracking set-up-tracking activate` | 71 | 71 | 1 | 通过 |  |
| Surveys (`survey`) | 效率 | 通过 | 一致 | `foxos survey search-surveys set foxos parity` | 28 | 28 | 1 | 通过 |  |
| Accounting (`accounting`) | 财务 | 通过 | 一致 | `foxos accounting books create` | 45 | 45 | 1 | 通过 |  |
| Invoicing (`invoicing`) | 财务 | 通过 | 一致 | `foxos invoicing set-up-business activate` | 20 | 20 | 1 | 通过 |  |
| Expenses (`expense`) | 财务 | 通过 | 一致 | `foxos expense set-up-expenses activate` | 17 | 17 | 1 | 通过 |  |
| Cap Table (`cap-table`) | 财务 | 通过 | 一致 | `foxos cap-table set-up-company activate` | 27 | 27 | 1 | 通过 |  |
| CRM (`crm`) | 业务 | 通过 | 一致 | `foxos crm set-up-pipeline activate` | 16 | 16 | 1 | 通过 |  |
| Help Desk (`help-desk`) | 业务 | 通过 | 一致 | `foxos help-desk help-desk-name set foxos parity` | 6 | 6 | 1 | 通过 |  |
| Contracts (`contracts`) | 业务 | 通过 | 一致 | `foxos contracts first-contract create` | 14 | 14 | 1 | 通过 |  |
| Point of Sale (`pos`) | 业务 | 通过 | 一致 | `foxos pos set-up-store activate` | 17 | 17 | 1 | 通过 |  |
| Inventory (`inventory`) | 业务 | 通过 | 一致 | `foxos inventory set-up-inventory activate` | 17 | 17 | 1 | 通过 |  |
| Assets (`assets`) | 业务 | — | — | — | 0 | 0 | 0 | 通过 | 上游提交 0fbb88cd 的 src/assets 只有 index.html/package.json/vite.config.js，缺少 index.html 引用的 /src/main.js（GitHub contents API 对 src/assets/src 返回 404），因此无法构建。 |
| Hiring (`hiring`) | 业务 | 通过 | 一致 | `foxos hiring set-up-hiring activate` | 22 | 22 | 1 | 通过 |  |
| Shifts (`shifts`) | 业务 | 通过 | 一致 | `foxos shifts set-up-team activate` | 17 | 17 | 1 | 通过 |  |
| Childcare (`childcare`) | 业务 | 通过 | 一致 | `foxos childcare school-name set foxos parity` | 39 | 39 | 1 | 通过 |  |
| Field Service (`field-service`) | 业务 | 通过 | 一致 | `foxos field-service business-name set foxos parity` | 40 | 40 | 1 | 通过 |  |
| Legal (`legal`) | 业务 | 通过 | 一致 | `foxos legal explore-sample-data activate` | 43 | 43 | 1 | 通过 |  |
| Fleet (`fleet`) | 业务 | 通过 | 一致 | `foxos fleet fleet-or-company-name set foxos parity` | 41 | 41 | 1 | 通过 |  |
| Property Management (`property-management`) | 业务 | 通过 | 一致 | `foxos property-management company-name set foxos parity` | 45 | 45 | 1 | 通过 |  |
| API Client (`api-client`) | 开发 | 通过 | 一致 | `foxos api-client filter set foxos parity` | 59 | 59 | 1 | 通过 |  |
| Chess (`chess`) | 游戏 | 通过 | 一致 | `foxos chess game create` | 30 | 30 | 1 | 通过 |  |
| Backgammon (`backgammon`) | 游戏 | 通过 | 一致 | `foxos backgammon game create` | 27 | 27 | 1 | 通过 |  |
| Checkers (`checkers`) | 游戏 | 通过 | 一致 | `foxos checkers game create` | 21 | 21 | 1 | 通过 |  |
| Solitaire (`solitaire`) | 游戏 | 通过 | 一致 | `foxos solitaire powered-by-puter show` | 9 | 9 | 1 | 通过 |  |
| Sudoku (`sudoku`) | 游戏 | 通过 | 一致 | `foxos sudoku puzzle create` | 39 | 39 | 1 | 通过 |  |

## 程序图标覆盖（US-53）

- Everything 应用：**51/51** 显示上游自带图标（来源：已安装的上游组件 50，随附（MIT） 1）；缺失：无（AGPL 应用未安装时没有图标，安装后从上游组件读取）。
- 内置程序：**6/6** —— writer：本机 LibreOffice，calc：本机 LibreOffice，impress：本机 LibreOffice，terminal：系统终端，editor：Code - OSS（随附，MIT），browser：Electron（随附）。
- ACP 智能体：**45/45** 显示注册表 `icon`（45 个在注册表里有 icon）。
- 狐狸OS 自己的程序保留狐狸OS 风格图标：files, environments, appcenter, settings。

## Windows 客户端（US-86 / US-87，2026-11-12 05:15，Asia/Shanghai）

- US-86（`foxos` 找不到，Path/PATH 重复）：pytest 通过。
- US-87 单元与结构测试 8/8 通过（`packages/core/tests/test_desktop_client.py`）。
- US-87 端到端 1/1 通过（`apps/desktop/e2e/client.e2e.js`）：真实 Electron（客户端模式）+ 真实狐狸OS 根文件系统来宾（sshd、Xvfb :0 上的 XFCE）。覆盖：本机执行默认关闭；终端、Everything 应用、文件写入都在来宾里；电脑画面经 SSH 转发的 x11vnc 显示来宾桌面；`FOXOS_E2E_GUEST_APT=1` 时应用中心在来宾里 apt 安装 LibreOffice Writer，「打开 Word」在来宾桌面打开 Writer。
- 修复中发现的缺陷：`--json` 被放在命令末尾，`desktop launch -- libreoffice --writer --json` 把它传给了 LibreOffice，Writer 打不开；现在 `--json` 放在命令前面（`bc8d9cc`）。
- 安装包：[v0.3.3-windows-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.3-windows-preview)（x64 / arm64 的 exe 与 zip，wine 下构建；x64 包内 Python 在 wine 里跑过 `foxos --version`、`env list`、`machine list`、`everything list`、`env catalog`，Windows Electron 在 wine 里默认进入客户端模式；arm64 只核对了 PE 架构）。
- 未覆盖：Windows 实机（见 [windows-client.md](windows-client.md)）。

## 安装包（发布矩阵，v0.3.2-os-preview）

2026-11-12 01:00–02:30（Asia/Shanghai）。Linux 用 `scripts/packaging/e2e-rootfs.sh` 在各发行版官方根文件系统里（chroot，不用容器）真实走一遍：Release 同款 `install.sh` 一行安装（从 file:// 发布目录下载并校验 SHA256SUMS）→ 以普通用户无头启动桌面并截图 → `foxos --version` → `foxos sheets create` → 卸载并确认 `/usr/bin/foxos`、`/opt/FoxOS`、`~/.local/opt/foxos` 都已删除。arm64 在 x86_64 上用 qemu-user 运行。Windows / macOS 的端到端要在 GitHub Actions 的真机上跑（`release.yml` 的 e2e-windows / e2e-mac 任务），仓库 Actions 因账户账单被锁，任务未开始即失败，所以这两个平台**未验证**。

| 系统 | CPU | 安装包 | 构建 | 端到端（安装 → 启动桌面 → foxos --version → sheets create → 卸载） | 说明 |
| --- | --- | --- | --- | --- | --- |
| Ubuntu 24.04 | x64 | deb · tar.gz · AppImage | ✅ 本地 | ✅ 通过 ×3 | 截图 e2e-ubuntu-24.04-{deb,tar,appimage}-x64.png |
| Debian 12 | x64 | deb · tar.gz · AppImage | ✅ 本地 | ✅ 通过 ×3 |  |
| Fedora 43 | x64 | rpm | ✅ 本地 | ✅ 通过 | 测试机连不上 Cisco openh264 源，测试时关掉（与 FoxOS 无关） |
| openSUSE Tumbleweed | x64 | rpm | ✅ 本地 | ✅ 通过 | 第一次失败：最小系统没有字体，Chromium 启动崩溃；rpm 加了字体依赖后重建并通过 |
| Arch Linux | x64 | tar.gz · AppImage | ✅ 本地 | ✅ 通过 ×2 | AUR PKGBUILD 加了 ttf-font 依赖 |
| Debian 12 | arm64 | deb · tar.gz | ✅ 本地 | ⚠️ 部分：安装、CLI、卸载通过；桌面启动未验证 | qemu-user 下 Chromium 崩溃（GPU 进程起不来、SIGTRAP），需真 arm64 机器 |
| Fedora 43 | arm64 | rpm | ✅ 本地 | ⚠️ 部分：安装、CLI、卸载通过；桌面启动未验证 | 同上 |
| Linux | arm64 | AppImage | ✅ 本地 | ⚠️ 只验证内容（unsquashfs 后 foxos --version、sheets create） | AppImage 头里的魔数让 qemu 的 binfmt 不匹配，无法在 qemu 下执行 |
| Windows 10/11 | x64 | NSIS exe · 便携 zip | ✅ 本地（wine 交叉构建） | ❌ 未验证 | wine 下解包 payload，python -m foxos --version 正常；真机静默安装 / 启动 / 卸载要等 CI |
| Windows 11 | arm64 | NSIS exe · 便携 zip | ✅ 本地（wine 交叉构建） | ❌ 未验证 | 只检查了 PE 架构为 ARM64 |
| Windows | x64 · arm64 | MSI | ❌ 未构建 | ❌ | WiX 在 wine 下崩溃，只能在 CI 的 Windows 机器上构建 |
| macOS 11+ | arm64 · x64 | zip | ✅ 本地（ad-hoc 签名） | ❌ 未验证 | 没有 Mac；CI 的 macos-14 / macos-15-intel 任务被账单锁挡住 |
| macOS 11+ | arm64 · x64 | dmg | ❌ 未构建 | ❌ | dmg 需要 macOS 工具链（CI） |
| 狐狸OS 系统 | arm64 | ISO | ❌ 未构建 | ❌ | 构建机出口连不上 ports.ubuntu.com（所有 ubuntu-ports 镜像返回 500）；CI 的 ubuntu-24.04-arm 任务被账单锁挡住 |
| 狐狸OS 系统 | amd64 | 单文件 ISO | ❌ 未上传 | — | 分卷 part1 + part2 已在发布里；单文件由 CI 合并上传 |

GitHub Actions 运行：[43057548522](https://github.com/gatesenman/foxos/actions/runs/43057548522)（失败：账户账单锁定，任务未启动）；[43059095200](https://github.com/gatesenman/foxos/actions/runs/43059095200)（失败：账户账单锁定，任务未启动）；[43070332484](https://github.com/gatesenman/foxos/actions/runs/43070332484)（失败：账户账单锁定，任务未启动）

## 复现

```bash
python3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'
(cd apps/desktop && npm ci)
FOXOS_HOME=~/.local/share/FoxOS npm run test:all          # 全部
python3 scripts/test_all.py --only e2e --e2e mcp,sandbox  # 只跑部分
```

