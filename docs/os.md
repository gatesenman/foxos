# 狐狸OS 操作系统

狐狸OS（FoxOS）是一个可安装、可引导的 Linux 桌面操作系统：给智能体和人同一套真实的桌面、应用与命令。智能体可以像人一样操作系统里的窗口、应用和文件，效果相同。

本文件描述操作系统本身的架构与实现边界。命令内核、审计、接管与应用适配仍见 [architecture.md](architecture.md)；隔离环境见 [environments.md](environments.md)；ISO 的制作步骤见 [os-build.md](os-build.md)。

## 1. 产品形态

- **主产品**：`FoxOS-<版本>-amd64.iso`（Live 可体验 + Calamares 安装器）。发布到 [GitHub Releases](https://github.com/gatesenman/foxos/releases)，单个 ISO 不超过 2 GB。
- **引导**：真实硬件（UEFI，兼做传统 BIOS）、Windows 上的 Hyper-V / 狐狸OS「环境」应用、以及本仓库开发机上的 QEMU/KVM。**QEMU 只用于测试，不是产品依赖，也不打进 ISO。** 产品不附带 Docker、Podman、LXC、VirtualBox、QEMU。
- **安装后**：真实登录、真实 XFCE（X11）会话、由 xfwm4 管理的真实窗口。LibreOffice、终端、文件管理器、浏览器、编辑器、Everything 应用都是操作系统里的普通进程，各有自己的窗口，而不是画在同一个 Electron 窗口里的矩形。
- **Windows / macOS 伴侣**：此前的 Windows 安装包（`.exe`）和今后在已有桌面上运行的伴侣程序，用来在那些平台上继续跑智能体，直到各自有自己的系统镜像。macOS 系统镜像只能在 Apple 硬件上制作和运行（Apple 许可），PC / 本 ISO 做不到，目录里会写明原因。

## 2. 基础系统

- **底本**：Ubuntu 24.04 LTS（noble）。智能体已经熟悉 `apt`、`systemd`、FHS 路径；LTS 有五年更新。
- **品牌**：对外名称是「狐狸OS / FoxOS」，不再出现 Ubuntu 的默认宣传、欢迎页或主题包。
  - `/etc/os-release`：`NAME="狐狸OS"`，`ID=foxos`，`ID_LIKE=ubuntu debian`，`PRETTY_NAME` 带版本，主页指向本仓库
  - 默认主机名 `foxos`
  - Plymouth 启动画面、登录界面（greeter）、壁纸、光标与面板均为狐狸OS 外观
  - `lsb_release`、APT 来源说明等处不展示 Ubuntu 营销文案；软件源本身仍指向 Ubuntu 归档（或镜像），保证安全更新
- **默认语言**：简体中文（zh-CN），可在安装器和设置里切到 English；`foxos` / MCP 消息跟随 `--lang` / `FOXOS_LANG`（见桌面的多语言实现）。
- **输入与字体**：Noto CJK 字体；Fcitx5 + 拼音，安装后也可选其他输入法。

## 3. 桌面（XFCE）

### 为什么选 XFCE

会话是 **XFCE**，跑在 **X11** 上（窗口管理器为 xfwm4）。这是给智能体用的 Ubuntu / Debian VPS 上最常见的轻量桌面：窗口、面板、开始菜单都是系统里的真控件，远程桌面和自动化工具（wmctrl、xdotool）也最成熟。软件包以发行版形式安装，**不把源码拷进本仓库**。

选它而不是 GNOME Shell 或 KDE Plasma，是因为：

1. **窗口由窗口管理器管理**，Alt+Tab、多工作区、边缘吸附与普通 Linux 桌面一致，不是自绘的假窗口。
2. 体积比 GNOME / KDE 小，便于把 ISO 压在 2 GB 以内，也便于去掉上游桌面的品牌残留。
3. 智能体控制窗口走成熟的 X11 工具：`wmctrl` 列出 / 聚焦 / 关闭 / 移动 / 缩放，`xdotool` 键入与点击，`scrot` 截图。
4. 配置是普通的 xfconf XML 与面板插件，行为可审计、可测试。

外观用狐狸OS 自己的窗口装饰与面板样式（暖色、克制，不以默认 Greybird 灰皮肤示人），GTK 控件建立在 Adwaita 之上；图标主题优先 Yaru（否则 Adwaita）。来源与许可见 `scripts/os/branding/xfce/ATTRIBUTION.md`。

### 面板、登录、安装器

- **面板**：标准的 xfce4-panel。左侧是 Whisker 开始菜单（按钮标题为「开始」），中间是任务栏，右侧是托盘、时钟、**人工接管** 和 **系统**（注销 / 关机）。不用 Electron 画整张桌面。若仍保留 Electron，它只作为「智能体会话 / 设置」的一个普通窗口跑在这套桌面上。
- **登录**：LightDM + lightdm-gtk-greeter（Live 可自动登录到 `foxos` 用户，安装后按安装器里创建的用户登录「狐狸OS」会话）。
- **安装器**：Calamares（发行版软件包，不把源码拷进仓库）。默认中文，含分区、用户、可选磁盘加密、网络，以及组件选择：桌面已预装；Everything 应用、ACP 智能体、额外环境镜像在安装后按需在线下载（避免 ISO 超 2 GB，也不在镜像里内置 AGPL 源码）。

### 预装应用（都是普通软件包 / 普通进程）

| 用途 | 第一版选用 | 说明 |
|---|---|---|
| 终端 | XFCE Terminal | 真实 PTY；可直接运行 `foxos` |
| 文件管理器 | Thunar | 比 Nautilus 依赖少，支持工作空间书签 |
| 浏览器 | Firefox（Mozilla 官方 .deb，不用 Snap） |  |
| 编辑器 | Mousepad；Code - OSS 作可选组件 | 原 Electron 里的 Monaco 编辑器若保留，改为独立窗口 |
| 办公 | LibreOffice | **体积大，不默认打进 ISO**；安装器 / `foxos` 在线安装组件可装，装完是普通窗口 |
| Everything 应用 | 安装后在线构建/安装 | 各应用是独立进程、独立窗口（Web 应用跑在隔离的浏览进程里，仍是操作系统窗口，不是外壳内嵌矩形） |

狐狸OS 自己的界面（面板、设置、开始菜单、环境窗口）使用自定义细滚动条；不修改 LibreOffice、Firefox 等工具包内部的默认滚动条。

## 4. 智能体控制整台机器

这是这套操作系统存在的理由。人能做的，智能体用同一套命令也能做，效果相同。

- **命令与 MCP**：`foxos` CLI 与 MCP 服务器以 systemd（用户与系统服务）开机自启，契约写在 [AGENTS.md](../AGENTS.md) 与 [agent-guide.md](agent-guide.md)。语法仍是 `foxos <应用> <资源> <动词>`，另增面向操作系统本身的 `foxos desktop …` / `foxos session …` / 扩展后的 `foxos env …`。
- **窗口与输入**（真实 API，不是进程内假界面）：列出 / 聚焦 / 移动 / 缩放 / 关闭窗口，启动应用，点击、键入、快捷键，截图，能拿到的辅助功能树。实现走 `wmctrl`、`xdotool`、`scrot`（XFCE / X11）。
- **仍然生效**：工作空间路径约束、写锁、JSONL 审计、人工接管（真实快捷键 + 面板按钮，暂停智能体写操作）、轻量沙箱与完整环境。
- **ACP 智能体**作为系统组件安装，启动时注入 MCP。
- 操作系统级操作清单记入 [operations/desktop.md](operations/desktop.md) 与命令目录，并配用户故事与端到端测试（US-6x）。

第一张可引导 ISO 就会带上 CLI / MCP 服务和面板上的接管按钮；窗口级控制与完整操作清单在随后的迭代补齐，不假装第一张盘已经做完。

## 5. 环境：做在操作系统里的「像 docker 一样好用」的虚拟机

环境是宿主机的一等功能，不是事后插件。使用体验靠近 `docker pull` / `docker run`，但 **不使用、不附带 Docker、Podman、LXC、VirtualBox、QEMU**。完整说明、命令表与限制见 [environments.md](environments.md)。这里只固定技术选型。

两档，面向 Linux 来宾（在狐狸OS 这台 Linux 宿主机上）：

| 档 | 机制 | 用途 |
|---|---|---|
| **轻量** | 已有实现：用户命名空间 + overlayfs + Landlock / seccomp / cgroup（`linux-ns`，以及 `foxos sandbox`） | 启动快，与宿主共享工具链；不是一台带桌面的独立电脑 |
| **完整虚拟机** | Linux 内核自带的 **KVM**（和 WSL2 之于 Windows 一样，是内核功能，不是我们附带的虚拟机软件）+ 我们选用的 VMM | 独立的 Linux / Windows 系统，带桌面；来宾桌面显示为狐狸OS 的一个窗口 |

**VMM 选型：cloud-hypervisor（Apache-2.0）。** 以官方二进制或本仓库构建脚本编译的二进制随 ISO 提供，NOTICE 保留版权与许可；不把无关源码整树拷进仓库。选它而不是 Firecracker，是因为完整环境必须能挂显示（virtio-gpu / 来宾桌面窗口）；Firecracker 面向无界面的微服务虚拟机，没有这条路。也不用 QEMU（产品依赖禁令）。libkrun（同样 Apache-2.0）可作为「只跑一个带 GPU 的应用」的后续选项。

来宾桌面进入狐狸OS 窗口的第一版路径：来宾内的图形会话 + 许可允许的显示通道（优先 virtio-gpu 扫描到宿主 GTK 窗口；过渡方案可以是 vsock 上的 wayvnc，ISC 许可，宿主用我们自己的小窗口显示）。输入走同一通道或 virtio-input。目标是人在狐狸OS 里看到并操作来宾桌面，智能体也可以 `foxos env desktop-attach` 后对来宾做与宿主相同的窗口操作。

- **Windows 来宾**：同一套 KVM + cloud-hypervisor，镜像来自用户提供的 ISO 或微软评估版 / 开发版 ISO（下载时校验校验和，记录许可条款，**不把 Windows ISO 放进 GitHub Release**）。安装 virtio 来宾工具以便桌面显示到窗口。若本机没有 VMX/SVM，或已处于无法嵌套的虚拟机中，命令明确报错并提示原因。
- **macOS 来宾**：仅 Apple 允许在 Apple 硬件上虚拟化 macOS。本 ISO（PC / Linux）目录里看得到该条目，但禁用，并写明原因。伴侣程序在 macOS 上运行时，再接已有的 Virtualization.framework 提供者。
- **在 Windows 伴侣里**：继续用已实现的 WSL2、Hyper-V、Windows Sandbox 提供者。
- **目录**（一键、可校验）：Ubuntu 20.04 / 22.04 / 24.04 / 26.04、Debian、Fedora、openSUSE Leap / Tumbleweed、Alma、Rocky、Oracle、Arch、Alpine、Kali，以及 Windows 10 / 11 评估版、Windows Server 评估版；支持自定义 ISO / URL。Linux 来宾预装或首次启动时安装桌面、Everything 应用与 `foxos` CLI/MCP，使来宾里的智能体能用同一套操作。Windows 来宾在虚拟机首次启动后，自动跑已有的 Windows 伴侣安装程序。
- **命令**：在已有 `pull` / `start` / `stop` / `exec` 之上，补齐 `foxos env run`（没有镜像就 pull，然后创建并启动，用法靠近 `docker run`）和 `foxos env desktop-attach`。

第一张 ISO 就必须带上「环境」功能和 **至少一条能用的 Linux 来宾桌面路径**（KVM 可用时走完整虚拟机；KVM 不可用时明确报错，并仍可使用已测试过的 `linux-ns` 轻量/完整命名空间环境）。不必在第一张盘上备齐所有目录条目。

## 6. 构建与测试

- 构建脚本在 `scripts/os/`，步骤写在 [os-build.md](os-build.md)。方法是 **debootstrap（Ubuntu 24.04）→ 在 chroot 里装包与换品牌 → squashfs → GRUB 混合 ISO（UEFI + BIOS）**。每一步都在脚本里，不使用说不清的封装器。
- 可复现：固定发行版代号与软件源，记录包列表；可选组件不打进 ISO。
- 端到端：用 QEMU/KVM **测试**引导 ISO（UEFI）、登录、给真实桌面和真实窗口截图、跑 `foxos` 与一次 MCP 会话、安装到虚拟磁盘并再引导。另测环境：在支持 KVM 的机器上启动一个 Linux 来宾。测试结果写入 `docs/test-report.md` 与用户故事 US-6x。`npm run test:all` 增加 `test:os` 目标。
- 预发布（如 `v0.3.0-os-preview`）附 ISO、`SHA256SUMS` 和中文测试说明 [os-test-guide.md](os-test-guide.md)（Ventoy / Rufus / dd 写 U 盘，以及在 Hyper-V / 狐狸OS 环境里引导）。

## 7. 第一张 ISO 包含什么、稍后补什么

**第一张可引导 ISO 必须已经做到：**

- 作为 Live 盘能引导到真实的狐狸OS 桌面（XFCE + 终端 / 文件管理器 / 浏览器）
- 品牌是狐狸OS（os-release、主机名、壁纸、登录器），默认中文
- Calamares 安装器（中文默认）
- `foxos` 命令与 MCP 的 systemd 服务
- 「环境」功能在系统里：目录可见，`linux-ns` 可用；KVM 可用时至少能拉起一条 Linux 来宾路径
- 人工接管的面板按钮与快捷键（命令侧已有 PAUSED）

**随后迭代（不假装已经做完）：**

- 智能体对辅助功能树的更完整覆盖（窗口的列出、聚焦、移动、缩放、键入、点击已由 `foxos desktop` 提供）
- linux-kvm 来宾内 exec（SSH / vsock）与 virtio-gpu 目标显示路径
- 完整目录里的每一个来宾（含 Windows 评估版的自动安装与来宾工具）
- virtio-gpu 直出（替换过渡显示通道）
- LibreOffice、Everything、ACP 的在线组件安装器在安装后的打磨
- 代码签名与安全启动的狐狸OS 自己的密钥（第一张盘可借助 Ubuntu 的 shim 以便在关闭或兼容安全启动时能引导；自定义签名稍后）

## 8. 许可与边界（不变）

- 不在仓库根目录擅自加 LICENSE 文件。
- 不把 AGPL 的 Everything 应用源码放进 ISO；安装器在线获取。
- 不复制 GPL 代码（Calamares、XFCE、GRUB 等以发行版软件包形式安装）。
- 随 ISO 提供的 Apache-2.0 / MIT / BSD 二进制（如 cloud-hypervisor）保留 NOTICE。
- 不重新分发 Windows ISO。
