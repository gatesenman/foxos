# 测试报告

由 `npm run test:all`（[scripts/test_all.py](../scripts/test_all.py)）生成，不使用模拟：pytest 调用真实 CLI / 内核，桌面端到端测试用 Playwright 驱动真实的 Electron 桌面，MCP 测试使用官方 MCP SDK 作为客户端。

- 时间：2026-11-12 11:45（UTC+8）　提交：`0070d7f`　用时：28 分 38 秒
- 环境：Linux 6.12.113+（x86_64），Python 3.13.5，Node v24.22.1，Landlock ABI 6
- 未覆盖：Windows 与 macOS 实机（本报告在 Linux 上生成；Windows 代码路径另有 wine 下的测试，见 [sandbox.md](sandbox.md)、[windows-test-guide.md](windows-test-guide.md)）

## 总览

| | 通过 | 失败 | 跳过 | 已知上游缺陷 |
| --- | --- | --- | --- | --- |
| 测试用例（259） | 239 | 0 | 19 | 1 |
| 用户故事（95） | 80 | 0 | 13 | 1 |

- Everything 应用：**50/51** 在桌面里本地启动，**48/51** 通过“界面操作与 CLI 等价”检查，**51/51** 通过 MCP（官方 SDK）调用成功；0 个失败，1 个跳过，1 个为已知上游缺陷。
- 操作清单：51 个应用共 **3350** 项操作，其中 **3350** 项有 CLI / MCP 绑定；测试中实际执行并比对结果的有 **49** 项（每个应用一项等价检查）。
- MCP：stdio 列出 4507 个工具（74 个应用），逐应用调用 75/75 成功；Streamable HTTP（compact）256 个工具；SDK 1.32.2。

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
| US-44 | Everything 效率类应用 | 通过 | 5 | 0 | 0 |
| US-45 | Everything 财务类应用 | 通过 | 4 | 0 | 0 |
| US-46 | Everything 商务类应用 | 通过 | 12 | 0 | 1 |
| US-47 | Everything 开发类应用 | 通过 | 1 | 0 | 0 |
| US-48 | Everything 游戏类应用 | 通过 | 5 | 0 | 0 |
| US-50 | 安装系统：目录与一键安装（Linux 宿主上真实安装 Alpine） | 通过 | 1 | 0 | 0 |
| US-52 | 轻量隔离：Landlock + seccomp 真实限制；智能体在轻量沙箱中运行；Seatbelt / Windows 策略生成 | 通过 | 14 | 0 | 1 |
| US-53 | 程序图标：每个程序显示其开源项目自带的图标（Everything 上游 / LibreOffice / 系统终端 / Code - OSS / Electron / ACP 注册表），缺失时退回并报告 | 通过 | 1 | 0 | 0 |
| US-54 | 滚动条：外壳、应用 webview、Monaco、终端都用狐狸OS 细滚动条（轨道透明、平时隐藏、指向出现），截图逐像素检查 | 通过 | 1 | 0 | 0 |
| US-55 | 多语言：默认简体中文，安装向导与设置里可切换 English（实时生效并保存）；内核 / CLI / MCP 消息跟随 FOXOS_LANG / --lang，JSON 字段名不变 | 通过 | 5 | 0 | 0 |
| US-60 | 真实 XFCE 会话：列出/聚焦/移动/缩放窗口，键入与点击，人工接管（CLI 与 MCP） | 通过 | 4 | 0 | 0 |
| US-61 | linux-kvm 来宾与 foxos env run / desktop-attach（至少一个 Linux 来宾路径） | 通过 | 4 | 0 | 0 |
| US-62 | Google Chrome：默认浏览器、foxos desktop launch chrome、本机 CDP（127.0.0.1，人开启）打开网页、读标题、截图 | 通过 | 3 | 0 | 0 |
| US-80 | 一行安装 install.sh：识别系统与 CPU，从 Release 下载，校验 SHA256SUMS（被篡改就拒绝安装），安装后 foxos --version 与 sheets create 可用 | 跳过 | 0 | 0 | 3 |
| US-81 | Linux 安装包（AppImage / deb / rpm / tar.gz）：随包 Python 与内核，foxos --version、help --json、sheets create，无头启动桌面并截图 | 跳过 | 0 | 0 | 1 |
| US-82 | 包管理器清单草稿：winget（NSIS + MSI，x64 / arm64）、Homebrew cask（Apple 芯片 / Intel）、AUR foxos-bin，按发布的 SHA-256 生成 | 通过 | 1 | 0 | 0 |
| US-83 | 发布矩阵：Windows / macOS / Linux 各 x64 与 arm64、amd64 与 arm64 ISO，runner 直接上传 Release，一行安装在 Ubuntu / Debian / Fedora / openSUSE / Arch / macOS 上验证 | 跳过 | 0 | 0 | 1 |
| US-84 | arm64 系统镜像：Ubuntu ports + UEFI，Google 不提供 arm64 Chrome 时回退到 Firefox | 通过 | 2 | 0 | 0 |
| US-85 | Windows 在线安装 install.ps1：x64 / arm64 自动识别，NSIS / MSI / 便携版，纯 ASCII 兼容 PowerShell 5.1 | 通过 | 1 | 0 | 0 |
| US-100 | 智能体：主智能体与多个智能体的创建、复制、改名、删除 | 通过 | 1 | 0 | 0 |
| US-101 | 每个智能体的设置（对照 OpenBot 逐项）：名称、头像、说明、模型、ACP 智能体、范围、权限；密钥不外露 | 通过 | 1 | 0 | 0 |
| US-102 | 真实 ACP 回合：工具调用卡片、审批（允许/拒绝）、diff、终端输出，审计记下是哪个智能体 | 通过 | 1 | 0 | 0 |
| US-103 | @提及与委托：主智能体把任务交给别的智能体，结果在范围内汇报回来 | 通过 | 1 | 0 | 0 |
| US-104 | pstack 技能：发现、显示、在对话中运行 | 通过 | 1 | 0 | 0 |
| US-105 | 智能体记忆与例程（定时任务） | 通过 | 1 | 0 | 0 |
| US-106 | 只暂停一个智能体与人工接管 | 通过 | 1 | 0 | 0 |
| US-107 | 聊天服务：令牌鉴权、发送、SSE 流、重开时回放进行中的回合 | 通过 | 1 | 0 | 0 |
| US-108 | 聊天界面：真实浏览器里发送、审批、中英文切换 | 通过 | 1 | 0 | 0 |
| US-109 | 连接器目录与 stdio MCP 连接器，按智能体授权 | 通过 | 1 | 0 | 0 |
| US-110 | OAuth 2.1 连接器：发现（RFC 9728/8414）、PKCE、动态注册、刷新，写操作需审批 | 通过 | 1 | 0 | 0 |
| US-111 | Bearer 令牌连接器：错误令牌不算连上，密钥从不写进日志 | 通过 | 1 | 0 | 0 |
| US-112 | 免密钥的托管连接器真实调用 | 通过 | 1 | 0 | 0 |
| US-113 | 多机配对：一次性配对码、证书指纹、双向 TLS（令牌被偷也连不上） | 通过 | 1 | 0 | 0 |
| US-114 | 一个智能体控制两台狐狸OS：默认拒绝、按机器授权、两边审计写明控制端与智能体 | 通过 | 1 | 0 | 0 |
| US-115 | 多个智能体共用一台狐狸OS：范围与应用授权、LOCKED、CONFLICT、只暂停一个、撤销授权 | 通过 | 1 | 0 | 0 |
| US-116 | 从官方发布地址安装第三方 ACP 智能体（sha256 校验）并真实握手；智能体设置与更新检查 | 通过 | 1 | 0 | 0 |
| US-117 | 镜像阶段运行环境：以用户 foxos 检查预装版本、PEP 668、专有智能体不进镜像 | 跳过 | 0 | 0 | 1 |
| US-118 | 镜像里预装的 ACP 智能体已登记，以用户 foxos 真实握手 | 跳过 | 0 | 0 | 1 |
| US-63 | 在线选择并安装狐狸OS 预设系统（Linux / Windows / macOS）：目录显示下载大小与所需磁盘、主机可用性与原因；分卷断点续传、逐卷与整体 sha256 校验；Windows 应答文件与 Hyper-V 计划；Linux 预设真实下载 + 引导 + 就绪 + SSH 执行 | 通过 | 6 | 0 | 1 |
| US-64 | SSH 远程访问：公钥增删查与 GitHub 导入、智能体不能开门、密码强度检查、MCP ssh_* 对等、虚拟机 SSH 对外开放只限人 | 通过 | 4 | 0 | 0 |
| US-65 | 在真实启动的 ISO 上端到端：SSH 密钥登录 / 密码与 root 被拒 / 经 SSH 运行 foxos 与 MCP、Chrome 安装、在线预设下载并引导、bots 应用与真实 ACP（opencode）对话、runtime doctor、acp list、桌面会话控制、Calamares 装到虚拟磁盘并重启进入 | 未运行 | 0 | 0 | 0 |
| US-86 | Windows 伴侣程序不依赖 PATH 上的 foxos：终端 PATH 只保留一个键（Windows 的 Path），应用中心 / 环境终端用 foxos 的绝对路径；安装程序把 foxos.cmd 加到用户 PATH（保留 REG_EXPAND_SZ） | 通过 | 4 | 0 | 0 |
| US-87 | Windows / macOS / 普通 Linux 上的桌面程序是“狐狸OS 电脑”的客户端：应用中心安装、打开 Word、终端、文件、智能体、聊天都在狐狸OS 虚拟机或远程狐狸OS 里执行；本机执行默认关闭，打开后每次确认；虚拟机控制台 / 来宾桌面画面（noVNC） | 通过 | 9 | 0 | 0 |
| US-120 | 电脑操控体检：显示默认栈（agent-desktop + Jev/DeepSeek + 规划器）和两条兜底 | 跳过 | 0 | 0 | 1 |
| US-121 | 默认路径真实端到端：agent-desktop 读 Mousepad，Jev 选每一步，DeepSeek 规划，改写并保存文件 | 跳过 | 0 | 0 | 1 |
| US-122 | 没有 TypeSafe 密钥时单步策略自动退到 DeepSeek，同样完成真实编辑并保存 | 跳过 | 0 | 0 | 1 |
| US-123 | 没有无障碍信息的程序（xedit）自动退到截图操控：Jev Box 定位 + xdotool，真实写入并保存 | 跳过 | 0 | 0 | 1 |
| US-124 | 网页内容不在无障碍树里时自动退到浏览器操控（Chrome CDP / agent-browser），在本地网页下单并读出订单号 | 跳过 | 0 | 0 | 1 |
| US-125 | 按次（--surface）和按智能体（设置 computer_use）手动选择操控方式 | 跳过 | 0 | 0 | 1 |
| US-126 | TypeSafe Jev 服务商真实调用（provider test） | 跳过 | 0 | 0 | 1 |
| US-127 | 电脑操控离线单元测试：Jev 请求/回答校验、观察编译器、两段式打分、logprob 置信度、agent-desktop 信封、路由、按智能体设置 | 通过 | 17 | 0 | 0 |
| US-140 | 主智能体用 DeepSeek（服务商预设，密钥在密钥库）真实回答 | 通过 | 1 | 0 | 0 |
| US-141 | 主智能体用工具委托给 opencode 编码智能体（DeepSeek），改文件前人批准，卡片带 diff | 通过 | 1 | 0 | 0 |
| US-142 | 人拒绝真实代理的编辑：文件不变，卡片记为拒绝 | 通过 | 1 | 0 | 0 |
| US-143 | 真实模型回合里用 pstack 技能 | 通过 | 1 | 0 | 0 |
| US-144 | 真实模型的智能体读另一台狐狸OS 上的目录，对方审计写明控制端 | 通过 | 1 | 0 | 0 |
| US-145 | Qwen Code 经 OpenAI 兼容地址接 DeepSeek，写文件经狐狸OS 内核 | 通过 | 1 | 0 | 0 |
| US-146 | 智能体窗口：新建并配置智能体（含 DeepSeek 服务商预设） | 通过 | 1 | 0 | 0 |
| US-147 | 智能体窗口：真实 opencode 回合，编辑卡片带 diff，点允许后文件改了 | 通过 | 1 | 0 | 0 |
| US-148 | 智能体窗口：点拒绝，文件不变 | 通过 | 1 | 0 | 0 |
| US-149 | 智能体窗口：@ 委托给第二个智能体，在审批页批准 | 通过 | 1 | 0 | 0 |
| US-150 | 智能体窗口：/ 技能菜单与用过的技能 | 通过 | 1 | 0 | 0 |
| US-151 | 智能体窗口：添加真实的本地 MCP 连接器（HTTP + Bearer）并列出工具 | 通过 | 1 | 0 | 0 |
| US-152 | 停靠窗口占住屏幕边（_NET_WM_STRUT_PARTIAL），最大化窗口不被盖住 | 通过 | 1 | 0 | 0 |
| US-153 | 智能体窗口：配对第二台狐狸OS 并在聊天里切换机器 | 通过 | 1 | 0 | 0 |
| US-154 | 智能体窗口：人工接管让智能体的编辑停下，交还后恢复 | 通过 | 1 | 0 | 0 |
| US-155 | 宿主应用里的智能体只在狐狸OS 虚拟电脑里动手；宿主执行要人明确打开并逐个确认 | 通过 | 3 | 0 | 0 |
| US-156 | 桌面客户端的「允许在本机执行」和 foxos bot host-access 是同一个开关（默认关，两边互相看得到） | 通过 | 2 | 0 | 0 |
| US-157 | Qwen Code 在狐狸OS 里默认要审批：写文件前弹审批卡片，拒绝则不写 | 通过 | 1 | 0 | 0 |
| US-158 | 新会话带的对话历史不会让智能体把指令再做一遍（这一轮的消息不进历史，多行消息只占一行） | 通过 | 1 | 0 | 0 |
| US-159 | 智能体窗口界面：中英文文案齐全、只用随附的图标字体、深浅色主题跟随系统 | 通过 | 2 | 0 | 0 |

### 失败、跳过与已知缺陷的用例

| 故事 | 用例 | 结果 | 说明 |
| --- | --- | --- | --- |
| US-39 | `test_env_windows.py` test_hw_wsl_install_ubuntu | 跳过 | pending：需要 Windows 实机（见 docs/windows-test-guide.md） |
| US-39 | `test_env_windows.py` test_hw_doctor | 跳过 | pending：需要 Windows 实机（见 docs/windows-test-guide.md） |
| US-42 | `everything.e2e.js` US-42 photo-studio：本地打开，界面操作与 CLI 等价 | 通过（含已知上游缺陷） | 上游缺陷：src/app/pointer.ts 中 #viewport 的 pointerdown 处理只排除 button / input / .canvas-ui，开始页的“Describe an edit”文本框（textarea）被鼠标点击时焦点被抢到画布，用鼠标无法输入；CLI 的 set 不经过指针事件，所以结果不同 |
| US-46 | `everything.e2e.js` US-46 assets：本地打开，界面操作与 CLI 等价 | 跳过 | 上游提交 0fbb88cd 的 src/assets 只有 index.html/package.json/vite.config.js，缺少 index.html 引用的 /src/main.js（GitHub contents API 对 src/assets/src 返回 404），因此无法构建。 |
| US-52 | `test_sandbox.py` test_windows_code_path_under_wine | 跳过 | 设置 FOXOS_TEST_WINE / FOXOS_TEST_WINE_PYTHON 后在 wine 中运行 Windows 代码路径 |
| US-80 | `test_packaging.py` test_US80_install_sh_downloads_verifies_and_installs_the_cli | 跳过 | 没有 out/linux-x64/FoxOS-0.3.3-linux-x64.tar.gz：先运行 npm run dist:linux 与 collect-artifacts.sh |
| US-80 | `test_packaging.py` test_US80_install_sh_refuses_a_tampered_download | 跳过 | 没有 out/linux-x64/FoxOS-0.3.3-linux-x64.tar.gz：先运行 npm run dist:linux 与 collect-artifacts.sh |
| US-80 | `test_packaging.py` test_US80_install_sh_download_only_keeps_file | 跳过 | 没有 out/linux-x64/FoxOS-0.3.3-linux-x64.tar.gz：先运行 npm run dist:linux 与 collect-artifacts.sh |
| US-81 | `test_packaging.py` test_US81_linux_packages_smoke | 跳过 | 没有构建 Linux 安装包 |
| US-83 | `test_packaging.py` test_US83_release_matrix_covers_every_common_platform | 跳过 | could not import 'yaml': No module named 'yaml' |
| US-117 | `test_os_runtime.py` test_US117_iso_runtime_versions_as_user_foxos | 跳过 | agent overlay not mounted (scripts/os/tools/agent-overlay.sh up) |
| US-118 | `test_os_runtime.py` test_US118_iso_acp_agents_registered_and_handshake_as_foxos | 跳过 | agent overlay not mounted (scripts/os/tools/agent-overlay.sh up) |
| US-63 | `test_env_presets.py` test_US63_real_linux_preset_download_verify_boot | 跳过 | 真实下载与引导：设置 FOXOS_PRESET_E2E=1 |
| US-120 | `test_cu_real.py` test_US120_doctor_reports_default_stack_and_fallbacks | 跳过 | real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session |
| US-121 | `test_cu_real.py` test_US121_default_path_agent_desktop_with_jev_edits_and_saves | 跳过 | needs a TypeSafe key |
| US-122 | `test_cu_real.py` test_US122_step_policy_falls_back_to_deepseek_without_typesafe_key | 跳过 | real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session |
| US-123 | `test_cu_real.py` test_US123_no_a11y_app_falls_back_to_screenshot_computer_use | 跳过 | real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session |
| US-124 | `test_cu_real.py` test_US124_web_target_not_in_a11y_tree_falls_back_to_browser_use | 跳过 | real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session |
| US-125 | `test_cu_real.py` test_US125_surface_can_be_forced_per_call_and_per_bot | 跳过 | real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session |
| US-126 | `test_cu_real.py` test_US126_typesafe_provider_live_call | 跳过 | needs a TypeSafe key |

未归入故事的用例：2 个（env-install.e2e.js, test_desktop_client.py）

## Everything 应用覆盖（51 个）

等价检查：同一个操作分别用真实鼠标 / 键盘事件（GUI）和 `foxos` CLI 执行，两次结束后的界面状态与应用数据必须一致。操作数来自 [操作清单](operations/)。

| 应用 | 分组 | 启动 | 等价检查 | 检查的操作 | 清单操作 | 有 CLI / MCP 绑定 | 测试中执行 | MCP 调用 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Spreadsheet (`spreadsheet`) | 办公 | 通过 | 无可检查操作 | — | 371 | 371 | 0 | 通过 | 主界面没有适合做等价检查的操作 |
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
- 狐狸OS 自己的程序保留狐狸OS 风格图标：files, environments, appcenter, settings, bots, computer。

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

## 说明

- **真实模型（US-140–US-145、US-157）：** 这些用例用 DeepSeek 的 OpenAI 兼容接口真实回答。密钥从 `~/.secrets/deepseek_api_key`（或 `FOXOS_TEST_DEEPSEEK_KEY_FILE`）读取，只经标准输入存进测试自己的密钥库，不出现在日志、截图和本报告里。这次运行有密钥文件，7 个都通过。没有密钥文件时它们**跳过**（不算失败），没有密钥的 CI 仍然是绿的。
- **智能体窗口（US-146–US-154）：** 在自己的 Xvfb + xfwm4 桌面里打开真实的智能体窗口（Chrome 应用模式），用 Playwright 经 CDP 点界面。代码智能体是 opencode，这次用 `deepseek/deepseek-flash`。没有密钥时用 opencode 的默认免费模型，不需要密钥，但 opencode 对免费用量有上限，用完会报 “Free usage limit reached”。停靠用例检查 `_NET_WM_STRUT_PARTIAL`：窗口停靠时占住屏幕右边，最大化的窗口不盖住它，取消停靠后释放。截图在 `docs/screenshots/bots-e2e-*.png`。
- **宿主保护（US-155）：** 在宿主应用里，智能体只在狐狸OS 虚拟电脑里动手。其余测试用 `FOXOS_PLACE=foxos` 模拟虚拟电脑里面。
- **一个本机执行开关（US-156）：** 桌面客户端设置里的「允许在本机执行」和 `foxos bot host-access` 读写同一个状态文件。用例在客户端模式下打开真实的 Electron 设置窗口：在设置里打开后命令行看到已打开，在命令行里关掉后设置里也是关的，旧 `settings.json` 里的值不算数，智能体改不了这个开关。
- **Qwen Code 默认要审批（US-157）：** 狐狸OS 用 `--approval-mode default` 启动 Qwen Code。去掉这个参数重跑同一个用例时，Qwen Code 不问就写了文件，用例失败；加上以后，拒绝时文件没有出现，批准后才写入。
- **US-44 tasks 偶发失败的根因：** 等价检查先按“含数字”过滤控件，再把生成的 ID 归一化。tasks 的 ID 是 `Date.now().toString(36) + '-' + 6 位随机 base36`，有时含数字，有时不含。同一个下拉框因此在一次结果里被丢掉，在另一次里留成 `<id>`。模拟 10 万次，不一致率约 16%。现在先归一化再过滤，不一致率为 0。这次 tasks 通过。
- **这次运行：** 11:17–11:45（UTC+8）在智能体窗口界面改版（US-159）之后完整跑了一遍 `npm run test:all`，没有失败。photo-studio 仍是已知的上游缺陷。
- **之前修过的问题：** 构建盒和其他构建共用机器，负载一度到 80–100。那时 US-41 calendar / signatures（桌面控制通道超时）、US-50 和智能体窗口（opencode 首次运行的版本检查超过 60 秒）都失败过。版本检查的超时已放宽到 240 秒。US-50 另有一个真问题：有 KVM 的宿主上，安装 Alpine 这类根文件系统条目时会优先选 linux-kvm，但这类条目没有可引导的磁盘。已改为不优先 linux-kvm。

## 复现

```bash
python3 -m venv .venv && .venv/bin/pip install -e 'packages/core[test]'
(cd apps/desktop && npm ci)
FOXOS_HOME=~/.local/share/FoxOS npm run test:all          # 全部
python3 scripts/test_all.py --only e2e --e2e mcp,sandbox  # 只跑部分
```

## 0.3.3 ISO 端到端（US-65，发布版 e51ff278，main 923b57a）

ISO：`/var/tmp/foxos-e2e/final2/FoxOS-0.3.3-amd64.iso`；虚拟化：tcg（宿主没有 KVM，按要求显式用 TCG）；时间为北京时间（UTC+8）。

| 用例 | 结果 | 开始 | 结束 | 说明 |
|---|---|---|---|---|
| SSH：密钥可登录、默认 / 错误密码与 root 被拒、ufw 放行 22 | **PASS** | 2026-11-12 10:17:40 | 2026-11-12 10:18:03 | 开机后 163s 密钥登录成功；sshd -T：permitrootlogin no pubkeyauthentication yes passwordauthentication yes kbdinteractiveauthentication no；默认 / 错误密码被拒；root 被拒；ufw active 放行 22/tcp；现场会话：一次性 16 位随机密码可登录（不记录），同一密码登录 root 被拒，live-ssh.txt 含警告 |
| 经 SSH 运行 foxos 与 MCP over SSH（stdio） | **PASS** | 2026-11-12 10:18:03 | 2026-11-12 10:40:48 | foxos 0.3.3；foxos ssh status：active、root_login=no、password_login=True；MCP over SSH：256 个工具，tools/call ssh_status 成功 |
| foxos runtime doctor | **PASS** | 2026-11-12 10:40:48 | 2026-11-12 10:43:31 | runtime doctor 退出码 0，ok=True，32 项：node, npm, corepack, pnpm, bun, python, pip, pipx, uv, gh, git, curl, wget, jq；agent-desktop 1.2.0 已预装（含 NOTICE） |
| foxos acp list 与 opencode 握手 | **PASS** | 2026-11-12 10:43:31 | 2026-11-12 10:46:22 | acp list：codex-acp, foxos-local, gemini, opencode, qwen-code；opencode 握手：{"agent": "opencode", "command": "/usr/lib/foxos/runtime/opencode/opencode", "protocolVersion": 1, "agentInfo": {"name": "OpenCode", "version": "2.2.7"}, "authMethods": [{"description": "Run `opencode |
| 「智能体」窗口启动 + opencode（ACP，DeepSeek）真实对话 | **FAIL** | 2026-11-12 11:45:31 | 2026-11-12 11:52:35 | AssertionError: {   "ok": true,   "command": "bot.message.send",   "result": {     "reply": {       "id": "msg-0dd168669b",       "turn": "turn-a3fda178be",       "role": "bot",       "bot": "e2e-opencode",       "text": "出错了：智能体 opencode 握手失败：等待 initialize 超时。stderr：",       "cards": [],       "plan": [],       "skills_used": [],       "machine": "local",       "stop_reason": "error",       "origin": "person",       "ts": "2026-11-12T11:33:34.355+08:00",       "duration_ms": 63236,       "error": {         "code": "ERROR",         "exit_code": 1,         "message": "智能体 opencode 握手失败：等待 initialize 超时。stderr："       }     }   } }  |
| Calamares 安装到虚拟磁盘 | **PASS** | 2026-11-12 10:56:10 | 2026-11-12 11:32:36 | 2177s 完成；Starting job "networkcfg" ( 24 / 31 ) Starting job "hwclock" ( 25 / 31 ) Starting job "services-systemd" ( 26 / 31 ) Starting job "安装 Google Chrome（如已同意条款）" ( 27 / 31 ) Starting job "设置 SSH 远程登录" ( 28 / 31 ) Starting job "bootloader" ( 29 / 31 ) Starting job "正在创建 initramfs…" ( 30 / 31 ) Starting job "Unmounting file systems…" ( 31 / 31 )；目标盘：NAME SIZE FSTYPE SERIAL vda 32G foxostarget ├─vda1 300M vfat └─vda2 31.7G ext4 |
| 重启进入装好的系统：密钥可登录、密码被拒、foxos 可用 | **PASS** | 2026-11-12 11:56:35 | 2026-11-12 11:59:11 | 从虚拟磁盘启动（不挂 ISO）57s 后密钥登录成功；installed；即便用安装时设置的真实密码，密码登录也被拒；root 被拒；foxos ssh status：password_login=false；1 把公钥（Calamares 写入）；need-sudo |
| Windows 0.3.3 客户端前提：sshd、foxos acp stdio、x11vnc | **PASS** | 2026-11-12 10:46:22 | 2026-11-12 10:48:00 | sshd active/enabled；foxos acp stdio opencode 经 SSH 55s 内 initialize 返回 protocolVersion=1（agentInfo={"name": "OpenCode", "version": "2.2.7"}）；x11vnc（x11vnc: 0.9.16 lastmod: 2019-01-05）-localhost 经 ssh -W 转发读到 RFB 003.008 握手 |

合计 8 项，通过 7，失败 1。

### 说明（发布版 e51ff278）

- **ISO**：`FoxOS-0.3.3-amd64.iso`，2252578816 字节，SHA-256 `e51ff278cfbecfa77a7ef81c624aadf45cf14d66e17484de7f8d3f95d8c150e2`，从 main `923b57a` 构建（含 a781172 及其后的修复：「智能体」窗口等 bot serve 180 秒、安装器 partition.conf / mount.conf）。宿主没有 KVM，全部在 qemu TCG（软件模拟，4 CPU、4 GB）里跑，比真机慢一个数量级。
- **安装（Calamares）**：在上一个候选版上发现两处真缺陷并已修复、在这个 ISO 上验证通过：① 没有 `partition.conf` 时 Calamares 3.3.5「抹掉磁盘」只建 EFI 分区、不建根分区（系统被拷进现场会话内存）；② 没有 `mount.conf` 的 extraMounts，目标系统里没有 /dev，`grub-install` 失败。这次 31 个任务全部完成（日志「completion: succeeded」），装好的磁盘不挂 ISO 启动到狐狸OS 登录界面（截图 [os-0.3.3-installed-login.png](screenshots/os-0.3.3-installed-login.png)）。测试工具按旧条件（根分区已卸载）判完成，而 Calamares 3.3 只卸子挂载，所以在 Calamares 报成功后手动卸了根分区让判定结束；判定已改为看「completion: succeeded」（aadf7bb）。
- **「智能体」窗口 + DeepSeek 对话：FAIL（冷启动超时）**。窗口两次都正常打开（[截图](screenshots/os-0.3.3-bots-window.png)），但测试里的首个回合两次失败：10:56 那次 opencode 报 `ServiceUnavailableError: Location plugins did not finish activating`（插件还没激活完就收到 session/new，ACP 返回 -32603「Internal service failure」）；11:52 那次 `initialize` 60 秒超时（窗口的 bot serve 同时在冷启动 opencode）。同一 ISO、同一密钥在约 11:35（来宾时钟慢约 20 分钟，显示 11:15）手动再发一次：162 秒后回答 `FOXOS-E2E-PONG`（stop_reason=end_turn）。上一个候选版上这项 PASS（181 秒）。修复已在 main（**不在这个 ISO 里**）：session/new 遇到「还在启动」类错误稍等重试（aadf7bb，带测试），initialize 默认等 180 秒（ccc2cc6）。
- **电脑操控（FOXOS_CU_E2E=1）**、**桌面控制**、**Chrome** 只在上一个候选版 6eb0dccf 上跑过（下表）；两版之间这些部分没有改动。电脑操控 7 项里 US121（mousepad 文件仍是 draft）与 US122（没有「eggs」行）失败，其余 5 项通过；怀疑是 TCG 下 mousepad 打开慢于测试里的 2.5 秒等待，未确认。
- **agent-browser 0.42.0、agent-desktop 1.2.0** 在 ISO 的 /usr/local/bin，声明在 /usr/share/doc/foxos/NOTICE.agent-browser、NOTICE.agent-desktop（`runtime doctor` 的 32 项清单不含这两个，另行检查）。
- **没有跑**：预设系统的真实下载 + 嵌套启动（在 TCG 里再套 qemu-tcg，之前几次因宿主过载超时；这版没再试）；Windows / macOS 真机；WSL2；cloud-hypervisor；FoxVZ。预设镜像本身在宿主上验证过（presets-2026.11）。
- 密钥（DeepSeek、TypeSafe）只在测试时经 SSH 标准输入写进来宾，没有进 ISO、提交、日志或截图。

## 0.3.3 ISO 端到端：上一个候选版 6eb0dccf（main deb70a7，未发布）

ISO：`/var/tmp/foxos-e2e/final/FoxOS-0.3.3-amd64.iso`；虚拟化：tcg（宿主没有 KVM，按要求显式用 TCG）；时间为北京时间（UTC+8）。

| 用例 | 结果 | 开始 | 结束 | 说明 |
|---|---|---|---|---|
| SSH：密钥可登录、默认 / 错误密码与 root 被拒、ufw 放行 22 | **PASS** | 2026-11-12 07:26:27 | 2026-11-12 07:26:49 | 开机后 147s 密钥登录成功；sshd -T：permitrootlogin no pubkeyauthentication yes passwordauthentication yes kbdinteractiveauthentication no；默认 / 错误密码被拒；root 被拒；ufw active 放行 22/tcp；现场会话：一次性 16 位随机密码可登录（不记录），同一密码登录 root 被拒，live-ssh.txt 含警告 |
| 经 SSH 运行 foxos 与 MCP over SSH（stdio） | **PASS** | 2026-11-12 07:26:49 | 2026-11-12 07:30:10 | foxos 0.3.3；foxos ssh status：active、root_login=no、password_login=True；MCP over SSH：256 个工具，tools/call ssh_status 成功 |
| foxos runtime doctor | **PASS** | 2026-11-12 07:30:10 | 2026-11-12 07:33:01 | runtime doctor 退出码 0，ok=True，32 项：node, npm, corepack, pnpm, bun, python, pip, pipx, uv, gh, git, curl, wget, jq；agent-desktop 1.2.0 已预装（含 NOTICE） |
| foxos acp list 与 opencode 握手 | **PASS** | 2026-11-12 07:33:01 | 2026-11-12 07:35:53 | acp list：codex-acp, foxos-local, gemini, opencode, qwen-code；opencode 握手：{"agent": "opencode", "command": "/usr/lib/foxos/runtime/opencode/opencode", "protocolVersion": 1, "agentInfo": {"name": "OpenCode", "version": "2.2.7"}, "authMethods": [{"description": "Run `opencode |
| 桌面会话控制（foxos desktop …） | **PASS** | 2026-11-12 07:40:48 | 2026-11-12 07:54:05 | desktop status：{"backend": "x11", "compositor": "XFCE", "display": ":0", "wayland_display": null, "windows": 5, "tools": {"wmctrl": true, "xdotool": true, "scrot": true, "maim；launch → windows 里出现 → focus → type → key → screenshot → close 全部成功 |
| Google Chrome 安装、默认浏览器、CDP | **PASS** | 2026-11-12 07:54:05 | 2026-11-12 08:06:19 | Google Chrome 157.0.8103.78；从 dl.google.com 装好；CDP 开启后 browser tabs 看到「Example Domain」；默认浏览器：foxos-chrome.desktop Value: /usr/bin/google-chrome-stable |
| 「智能体」窗口启动 + opencode（ACP，DeepSeek）真实对话 | **PASS** | 2026-11-12 08:06:19 | 2026-11-12 08:28:37 | 智能体窗口「智能体 · 狐狸OS」出现；opencode（ACP，deepseek/deepseek-chat）真实回合 181s，回答含 FOXOS-E2E-PONG；密钥经 SSH 标准输入写入来宾密钥库 |
| Calamares 安装到虚拟磁盘 | **FAIL** | 2026-11-12 09:11:16 | 2026-11-12 09:57:05 | AssertionError: Calamares 没有完成：    Starting job "networkcfg" ( 24 / 31 )      Starting job "hwclock" ( 25 / 31 )  [PYTHON JOB]: "  .. RTC method failed, trying ISA bus method."      Starting job "services-systemd" ( 26 / 31 )      Starting job "安装 Google Chrome（如已同意条款）" ( 27 / 31 )      Starting job "设置 SSH 远程登录" ( 28 / 31 )      Starting job "bootloader" ( 29 / 31 )      ERROR: Installation failed: "启动加载器安装出错"   |
| Windows 0.3.3 客户端前提：sshd、foxos acp stdio、x11vnc | **PASS** | 2026-11-12 08:55:51 | 2026-11-12 08:57:48 | sshd active/enabled；foxos acp stdio opencode 经 SSH 73s 内 initialize 返回 protocolVersion=1（agentInfo={"name": "OpenCode", "version": "2.2.7"}）；x11vnc（x11vnc: 0.9.16 lastmod: 2019-01-05）-localhost 经 ssh -W 转发读到 RFB 003.008 握手 |
| 电脑操控真实端到端（FOXOS_CU_E2E=1） | **FAIL** | 2026-11-12 08:28:37 | 2026-11-12 08:51:06 | AssertionError: 2 failed, 5 passed in 785.53s (0:13:05)；失败：tests/test_cu_real.py::test_US121_default_path_agent_desktop_with_jev_edits_and_saves, tests/test_cu_real.py::test_US122_step_policy_falls_back_to_deepseek_without_typesafe_key |

合计 10 项，通过 8，失败 2。

