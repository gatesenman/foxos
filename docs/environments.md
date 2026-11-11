# 环境：狐狸OS 自带的隔离运行环境

狐狸OS 自己实现了一层隔离环境，不依赖 Docker、Podman、LXC、VirtualBox、QEMU。
使用体验靠近 `docker pull` / `docker run`（`foxos env pull` / `run` / `start` / `stop` / `exec` / `desktop-attach`），实现完全是另一套。

在 **狐狸OS 操作系统（本仓库打出的 Linux ISO）** 上，环境是宿主机的一等功能，见 [os.md](os.md) 第 5 节。完整档的 Linux / Windows 来宾走内核自带的 KVM + 我们选用的 VMM（见下），来宾桌面显示为狐狸OS 的一个窗口。轻量档与已有的命名空间运行时仍然保留。

在 Windows / macOS 伴侣程序里，三个平台各用系统自带的机制：

| 平台 | 后端 ID | 实现 | 状态 |
|---|---|---|---|
| 狐狸OS / Linux 宿主 | `linux-kvm` | 内核 KVM + cloud-hypervisor（Apache-2.0，随系统提供二进制并保留 NOTICE，不把源码整树拷进仓库）：完整 Linux / Windows 虚拟机，virtio-blk / virtio-net / virtio-fs（工作空间）、来宾桌面进狐狸OS 窗口 | 已实现 `run` / `desktop-attach`：产品路径为 KVM + cloud-hypervisor + 来宾 wayvnc；KVM 不可用时需显式 `FOXOS_ALLOW_TEST_VMM=qemu-tcg` 才用 QEMU 做测试 |
| 狐狸OS / Linux 宿主 | `linux-ns` | 自研运行时 `foxos/envs/linux.py`：用户命名空间（无特权）+ mount / pid / uts / ipc / 可选 net 命名空间、overlayfs、pivot_root、seccomp、cgroup v2（可委派时）或 rlimit | 在本机（内核 6.12，普通用户 uid 1000）端到端测试通过；无 KVM 时仍可用 |
| Windows 伴侣 | `wsl2` | 驱动系统自带的 WSL2（`wsl.exe --import/--exec/--terminate/--export/--unregister`），进程限制用 Job Object | 有代码和单元测试（命令构造、路径换算、输出解析），**未在 Windows 实机上测试** |
| macOS 伴侣 | `macos-vz` | Swift 小程序 `FoxVZ.swift` 调用 Virtualization.framework（Linux 内核引导、virtio 磁盘 / 网络 NAT / virtio-fs 共享工作空间 / 控制台） | 有代码和单元测试（配置生成、命令构造），**未在 Mac 实机上测试** |

## 三个入口，同一套命令

- CLI：`foxos env <动词>`（见下表），加 `--json` 输出机器可读结果
- MCP：工具 `env_<动词>`（如 `env_create`、`env_exec`），与 CLI 由同一份命令定义生成
- 图形界面：桌面上的“环境”应用（开始菜单、应用中心、桌面图标）。界面上的每个按钮都调用同一个内核命令，审计记为 `human:desktop`；
  CLI / MCP / 智能体的操作会通过审计事件让界面实时刷新

| 动词 | 作用 | 界面位置 |
|---|---|---|
| `images` | 官方镜像目录与本地镜像 | 左下“镜像” |
| `pull IMAGE [--sha256]` | 下载镜像（目录 ID、https 地址或 .foxenv 文件）并校验 sha256 | 镜像页“下载” / “从地址安装” |
| `run NAME --image [-- desktop-attach]` | 没有镜像就 `pull`，然后创建并启动（用法靠近 `docker run`）；可直接附上来宾桌面窗口 | “运行” |
| `create NAME --image --network host\|none --workspace-mode rw\|ro\|none [--memory-mb --cpus --pids]` | 创建环境 | “新建” |
| `list` / `info NAME` | 列表 / 详情（配置、快照、操作、cgroup 状态） | 左侧列表 / 详情页 |
| `start` / `stop` / `restart` | 启停 | 快捷操作 |
| `exec NAME -- CMD…` | 在环境里执行命令（默认工作目录 /workspace），返回退出码、stdout、stderr | 自定义操作的“运行” |
| `desktop-attach NAME` | 把完整虚拟机的来宾桌面作为狐狸OS 的一个窗口打开，之后智能体可对来宾做与宿主相同的窗口操作 | “打开桌面” |
| `shell NAME` | 交互式 shell | “终端”（在内置终端窗口里打开） |
| `clone NAME NEW` | 复制可写层与设置 | “克隆” |
| `snapshot NAME [--label]` / `restore NAME SNAPSHOT` | 快照 / 恢复（需先停止） | “快照”页 |
| `export NAME --out FILE` / `import FILE --name` | 导出 / 导入 `.foxenv` | “导出” / 左下“导入” |
| `delete NAME` | 删除环境（不删镜像、不动工作空间） | “删除” |
| `mount NAME --source --target [--readonly] [--remove]` | 宿主目录挂载 | “设置”页 → 挂载 |
| `limits NAME [--memory-mb --cpus --pids --network --workspace-mode]` | 资源限制、网络、工作空间权限 | “设置”页 |
| `stats [NAME]` | 进程数、CPU 时间、内存、可写层磁盘 | “概览”页（每 2 秒刷新） |
| `logs NAME [-n]` | 环境日志与 init 日志 | “日志”页 |
| `action add NAME ACTION --command` / `action run NAME ACTION` | 自定义操作，支持 `${env}` `${image}` `${workspace}` `${host_workspace}` `${hostname}` 变量 | “自定义操作”页 |

## 镜像格式 `.foxenv`

一个 tar 文件，内含：

- `manifest.json`：`{"format": "foxenv/1", "id", "name", "arch", "source", "created", "shell", "rootfs": "rootfs.tar.zst", "sha256"}`
- `rootfs.tar.zst`：根文件系统（zstd 压缩的 tar），`sha256` 为它的摘要，导入时校验

镜像来源：官方发行版 rootfs（Alpine minirootfs、Ubuntu base，下载时用发行方公布的 SHA256 校验），
任意 https 地址（`.tar.gz` / `.tar.zst` / `.foxenv`，可用 `--sha256` 指定期望值），以及 GitHub Releases 上发布的 `.foxenv`。

存储位置：`FOXOS_HOME/envs/images/<id>/`（只读层），`FOXOS_HOME/envs/instances/<名字>/{env.json, upper, work, merged, logs, snapshots, run}`。

## Linux 运行时细节

启动（`foxos env start`）时：

1. 监督进程读取 uid/gid 后 `unshare(CLONE_NEWUSER)`，写 `uid_map`（`0 <uid> 1`）、`setgroups=deny`、`gid_map`，在环境里是 root、在宿主上仍是普通用户
2. `unshare(NEWPID | NEWUTS | NEWIPC [| NEWNET])`，fork 出环境的 1 号进程；1 号进程自己 `unshare(NEWNS)`（不影响监督进程的根）
3. 挂载：根设为 rprivate；overlayfs（`lowerdir=镜像, upperdir, workdir, userxattr`，用户命名空间内的无特权 overlay）；`/proc`；`/sys`（无网络时挂新的 sysfs，否则只读绑定）；
   tmpfs `/dev` 并绑定 null / zero / full / random / urandom / tty，devpts（newinstance）、shm、fd 链接；tmpfs `/tmp` `/run`；`resolv.conf`；
   工作空间绑定到 `/workspace`（只读模式下再 remount 只读）；用户挂载；狐狸OS 安装的 ACP 智能体只读挂到 `/opt/foxos/agents`
4. `pivot_root` 到新根并卸载旧根
5. 无网络模式下只拉起回环网卡 `lo`
6. 资源限制，然后安装 seccomp 过滤器（拒绝 kexec、内核模块、reboot、swap、时钟设置、bpf、perf_event_open、userfaultfd、keyctl、iopl、open_by_handle_at 等，返回 EPERM）
7. 1 号进程回收僵尸进程；`stop` 向它发 SIGTERM，超时后 SIGKILL

`exec` 用 `setns` 依次加入环境的 user、mnt、pid、uts、ipc（和 net）命名空间，fork 后 chdir、加限制与 seccomp，再 `execvpe`。

### 本机内核不允许、或做不到的部分（如实说明）

- **cgroup v2 资源限制**：只有当前用户的 cgroup 已委派（目录可写）时才用 cgroup（`memory.max`、`pids.max`、`cpu.max`，按整个环境计算）。
  本机 `/sys/fs/cgroup/agent` 属于 root、不可写，所以回退到 rlimit：内存用 `RLIMIT_AS`（每个进程的地址空间），进程数用 `RLIMIT_NPROC`（按用户计算），
  **CPU 上限在这种情况下不生效**。`foxos env info` 的 `cgroup` 与 `limits_note` 字段会写明当前用的是哪一种
- **网络**：`host` 共享宿主网络命名空间；`none` 是独立的网络命名空间，只有 `lo`。没有实现 NAT / 端口转发（无特权情况下需要 slirp 之类的用户态网络栈）
- **设备**：不能 mknod，`/dev` 里的设备节点是从宿主绑定的
- **uid 映射**：无特权下只能映射一个 uid（环境里的 root ↔ 宿主的当前用户）；环境内创建其他用户的文件，在宿主上都属于当前用户。
  因此需要多个 uid 的软件（例如以 `nobody` 身份运行的服务）在环境里会以 root 身份运行
- **镜像里的设备文件**：解包时跳过 `./dev/*`，不保留属主（`--no-same-owner`）
- **在环境里执行 `reboot`**：seccomp 拒绝 reboot 系统调用；busybox 的 `reboot` 会改为向 1 号进程发 SIGTERM，效果是环境停止

## 隔离级别与平台选择（决策记录）

研究过程与许可证核对见 [virtualization-references.md](virtualization-references.md)。决定：

| 档位 | 含义 | Linux | Windows | macOS |
| --- | --- | --- | --- | --- |
| **轻量**（进程级沙箱，[`foxos sandbox`](sandbox.md)） | 启动快、与宿主共享系统与已装工具；限制文件读写范围、网络与危险系统调用 | Landlock（文件、TCP、信号作用域）+ seccomp | 受限令牌（低完整性）或 AppContainer + 作业对象 | Seatbelt（sandbox-exec，按会话生成策略） |
| **完整**（独立系统 / 虚拟机） | 独立根文件系统或带桌面的虚拟机，可随意装软件、快照、导出；完整虚拟机的桌面显示为狐狸OS 窗口 | 有 KVM 时：`linux-kvm`（KVM + cloud-hypervisor）；否则：`linux-ns`（本文后面各节，命名空间，不是带桌面的独立电脑） | `wsl2`（Linux 发行版）、`windows-sandbox`、`hyperv` | `macos-vz`（Virtualization.framework Linux 虚拟机） |

- 每个智能体会话在面板“运行位置”里选：宿主、轻量沙箱、轻量沙箱（不联网），或某个运行中的完整环境。
- 不依赖 Docker / Podman / LXC / VirtualBox / QEMU。完整虚拟机用的是内核 KVM（Linux 已有的功能）和 Apache-2.0 的 cloud-hypervisor（随系统提供，保留 NOTICE）。GPL / LGPL / AGPL 项目只借鉴思路，不复制代码。
- **状态**：`linux-ns` 已实现并端到端测试；`linux-kvm` 已接入 `foxos env run` / `desktop-attach`（产品路径为内核 KVM + cloud-hypervisor，来宾桌面走 wayvnc）。在 KVM 不可用（例如本构建盒创建 vCPU 会触发内核 BUG）的机器上，只有显式设置 `FOXOS_ALLOW_TEST_VMM=qemu-tcg` 才用 QEMU TCG 做开发测试，QEMU 不是产品依赖。Windows 三个伴侣提供者有代码与单元测试，未在 Windows 硬件上验证；
  轻量档的 Linux 实现已完成并端到端测试（US-52）；macOS（Seatbelt）与 Windows（受限令牌 / AppContainer + 作业对象）有代码与单元测试，未在实机上验证。详见 [sandbox.md](sandbox.md)。


## 狐狸OS 宿主上的完整虚拟机（KVM）

这一节只适用于狐狸OS 操作系统（或一般 Linux 宿主）。Windows / macOS 伴侣仍用上一节的 WSL2 / Hyper-V / Virtualization.framework。

### 为什么是 KVM + cloud-hypervisor

- **KVM** 是 Linux 内核的一部分（`/dev/kvm`），不是我们附带的虚拟机软件。这与 WSL2 之于 Windows 相同：用操作系统已经提供的虚拟化接口。
- **VMM** 必须能给来宾挂显示器，来宾桌面才能成为狐狸OS 的窗口。Apache-2.0 的 [cloud-hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor) 支持 virtio-blk、virtio-net、virtio-fs、virtio-console，并有 virtio-gpu 路径，也支持 Windows 来宾。同许可的 Firecracker 面向无界面微服务，不作为完整桌面环境的 VMM。QEMU / VirtualBox 不进入产品。
- 二进制由 `scripts/os/` 在构建 ISO 时获取或编译，放进系统的 `/usr/lib/foxos/vmm/`，NOTICE 写明版本、来源与 Apache-2.0。不把上游源码整树拷进本仓库。
- 没有 VMX/SVM，或宿主自己已是虚拟机且未打开嵌套虚拟化时：`foxos env doctor` 与 `run` 给出明确错误（如何在 BIOS / Hyper-V 里打开虚拟化，或改用 `linux-ns`），不静默失败。

### 来宾桌面怎么变成狐狸OS 的窗口

目标：人在狐狸OS 桌面上看到一个普通窗口，里面是来宾的完整桌面；`foxos env desktop-attach` 打开这个窗口后，智能体对来宾里的应用使用与宿主相同的操作语法。

1. **目标路径**：virtio-gpu（以及 virtio-input）把来宾帧缓冲呈现在一个 GTK 窗口里，工作空间通过 virtio-fs 挂到来宾的 `/workspace`。
2. **第一版可用的过渡路径**：来宾里的图形会话通过 vsock 上的 [wayvnc](https://github.com/any1/wayvnc)（ISC）提供显示；宿主用狐狸OS 自己的小窗口显示，不引入 QEMU。随后用 virtio-gpu 替换，命令不变。

### Windows 与 macOS 来宾

- **Windows**：同一套 `linux-kvm`。镜像只能是用户给定的 ISO，或从微软评估中心 / 开发者渠道按目录条目下载的评估版、开发版（下载后校验 sha256，把许可条款记在目录与界面里）。**狐狸OS 的 GitHub Release 不包含任何 Windows ISO。** 来宾里安装 virtio 驱动与工具后，桌面同样进狐狸OS 窗口。首次启动可自动跑狐狸OS Windows 伴侣安装程序，以便来宾内也有 `foxos` 与 Everything。
- **macOS**：Apple 只允许在 Apple 硬件上的 macOS 中虚拟化 macOS。狐狸OS ISO（PC）的目录里该条目可见但禁用，说明即此句。伴侣程序在 Mac 上运行时，走已有的 `macos-vz`；在 Mac 上虚拟化 macOS 本身属于后续工作，不在本 ISO 的范围里。

### 来宾里的桌面与 Everything

每个受支持的 Linux 来宾镜像应预装或在首次启动时安装：一个桌面会话、Everything 应用（在线获取，不把 AGPL 源码打进来宾镜像仓库）、以及 `foxos` CLI / MCP。这样在来宾里运行的智能体与在宿主上使用同一套操作。Windows 来宾通过首次启动自动安装伴侣程序达到同一效果。

第一张 ISO 不要求目录里每一个发行版都已预构建，但目录要可见、可一键安装（官方根文件系统或 ISO + 校验和），并且至少一条 Linux 来宾桌面路径在 KVM 可用时能跑通。

## 一键安装系统（Windows 重点）

“环境”应用左下角 **安装系统**，或 `foxos env catalog` / `foxos env install`。详见 [environment-provider-protocol.md](environment-provider-protocol.md)。

**狐狸OS 预设系统**（已配置好桌面、中文、Node / Bun / Python、ACP 智能体与 foxos 桥的 Linux / Windows / macOS）在同一个目录的顶部：分卷断点续传、逐卷 sha256 校验，Windows 与 macOS 的介质在安装时从微软 / Apple 官方下载。详见 [presets.md](presets.md)。

- **Linux 发行版（WSL2）**：Ubuntu 20.04 / 22.04 / 24.04 / 26.04、Debian、Kali、openSUSE Leap / Tumbleweed、SUSE Linux Enterprise、Fedora、AlmaLinux、
  Rocky Linux（官方 WSL 镜像与 CIQ 版）、Oracle Linux（应用商店包，或 LXC 构建）、Arch、Alpine、eLxr、Azure Linux，以及 LXC 镜像服务器的每日构建和自定义 URL / 本地 tar。
  默认安装方式：下载官方根文件系统 → 校验 sha256 → `wsl.exe --import foxos-<名> <目录> <文件> --version 2`；只有应用商店包的发行版用 `wsl.exe --install -d <名> --no-launch`。
  LXC 构建是 .tar.xz，导入前自动转成 .tar.gz。
- **WSL 未启用时**：`doctor` 检测（解析 `wsl.exe --status`，兼容 UTF-16 输出与中英文消息），一键“启用 WSL”执行
  `wsl.exe --install --no-distribution`（UAC 确认），需要重启时明确提示；BIOS 未开启虚拟化时给出手动步骤。
- **Windows 来宾**：Windows Sandbox（生成 .wsb，把工作空间映射到沙箱桌面，可设网络 / 内存 / 只读）；Hyper-V 虚拟机（用户 ISO，或从微软评估中心下载的
  Windows 11 企业版 / Windows Server 2025 评估版 ISO；`New-VM` 第 2 代、vTPM、DVD 引导、`vmconnect`）。两者都检测 Windows 版本（家庭版不支持）与可选功能，可一键启用。
- **macOS 来宾**：列出但禁用，说明原因（Apple 许可只允许在 Apple 硬件上的 macOS 中虚拟化 macOS）。
- 在狐狸OS / Linux 宿主上，同一目录中的 Linux 条目优先由 `linux-kvm` 安装为带桌面的完整虚拟机（KVM 可用时）；否则由 `linux-ns` 安装为命名空间环境（端到端测试 US-50 真实安装 Alpine）。Windows 来宾只在 `linux-kvm` 下提供。macOS 来宾条目在此宿主上禁用（见上节）。

## 在环境里运行智能体

桌面右侧面板的“运行位置”可以选一个运行中的环境（Linux 后端）。启动后：

- 智能体进程在环境里运行，工作目录 `/workspace`，ACP 的 `session/new` 的 `cwd` 为 `/workspace`；
  智能体请求读写文件时，`/workspace/...` 会换算回宿主的工作空间路径，仍然经过狐狸OS 内核（工作空间约束、写锁、人工接管、审计）
- 智能体程序来自宿主上狐狸OS 安装的智能体目录（只读挂在 `/opt/foxos/agents`）。npm 类智能体需要环境里有 Node.js（例如 `foxos env exec dev -- apk add nodejs`）；
  二进制类智能体需要与环境的 C 库兼容（Alpine 是 musl，Ubuntu 是 glibc）
- foxos MCP：宿主启动一个只监听 127.0.0.1 的 Streamable HTTP MCP 服务器（随机端口 + 随机令牌），以 `type: http` 注入给智能体。
  需要环境共享宿主网络（`--network host`）且智能体声明支持 HTTP MCP；否则不注入，并在会话里提示
- 智能体身份仍是 `acp:<智能体 ID>`，审计里能看到

## 安装器

安装器（`install.sh` / `install.ps1`）和桌面的安装向导都把“环境”作为一个组件：Linux 上检查用户命名空间是否可用（`unshare -U true`）并预下载 Alpine 镜像；
Windows 上检查 / 启用 WSL2；macOS 上编译 `FoxVZ` 辅助程序（需要 Xcode 命令行工具）。

## 测试

- `packages/core/tests/test_envs.py`：US-30 ～ US-36，真实地在本机创建、启动、执行、隔离检查（只读工作空间、无网络、主机名、pid 命名空间、seccomp）、快照恢复、克隆、导出导入、挂载、限制、自定义操作、日志、审计与人工接管；
  Windows / macOS 后端的单元测试
- `apps/desktop/e2e/environments.e2e.js`：US-37，用 Playwright 驱动真实桌面：在界面上新建、启动、运行自定义操作、快照，并用 CLI 核对状态一致；CLI 停止后界面实时刷新

参考：界面布局参考了 wsl-ui 的思路（仪表盘、快捷操作、自定义操作）。wsl-ui 是 GPL-3.0 项目，狐狸OS 没有使用它的任何代码、素材或文字。
