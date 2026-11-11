# 环境层参考的开源项目

调研时间：2026-11-10。许可证都是从各仓库自己的 LICENSE / COPYING 文件核对的（GitHub API `repos/<仓库>/license` 返回的文件内容，不只看徽章）。

使用规则：
- MIT / Apache-2.0 / BSD：可以参考设计，必要时可复制代码，但要保留原版权与许可声明（目前**没有复制任何代码**）
- GPL / LGPL / AGPL / 自定义或 fair-source 许可：**只借鉴思路**，不复制代码、素材、文字
- 操作系统自带机制（Landlock、Seatbelt、AppContainer、Windows Sandbox、Hyper-V）：按官方文档调用系统接口

## Linux

| 项目 | 许可证（核对文件） | 机制 | 狐狸OS 借鉴什么 |
|---|---|---|---|
| bubblewrap（containers/bubblewrap） | LGPL-2.1（`LICENSE`，GitHub 识别为 NOASSERTION） | 无特权用户命名空间 + 绑定挂载 + pivot_root，一次性沙箱 | 只借鉴思路：“轻量沙箱 = 只读绑定宿主根 + 可写工作目录 + tmpfs”的模型；不调用、不复制 |
| nsjail（google/nsjail） | Apache-2.0（`LICENSE`） | 命名空间 + cgroup + rlimit + seccomp-bpf（kafel 规则） | 资源限制的分层：cgroup 可用时用 cgroup，否则 rlimit；把 seccomp 规则当成可配置策略 |
| youki（youki-dev/youki） | Apache-2.0（`LICENSE`） | Rust 实现的 OCI 运行时 | 容器启动步骤的拆分（建命名空间 → 挂载 → pivot_root → 降权 → exec）和 rootless cgroup 委派检测 |
| crun（containers/crun） | GPL-2.0（`COPYING`） | C 实现的 OCI 运行时 | 只借鉴思路：用户命名空间下的 overlay / idmap 处理方式 |
| gVisor（google/gvisor） | Apache-2.0（`LICENSE`） | 用户态内核（Sentry）拦截系统调用 | 作为“比命名空间更强、比虚拟机更轻”的第三档的参考，暂不实现 |
| Landlock（Linux 内核 LSM） | 内核的一部分（GPL-2.0）；只调用其系统调用接口 | 无特权进程自己限制文件系统 / 网络访问 | 轻量沙箱的文件规则：除工作空间和临时目录外只读。本机内核 ABI 版本 6 可用 |
| firejail（netblue30/firejail） | GPL-2.0（`COPYING`） | setuid 沙箱 + 应用配置文件 | 只借鉴思路：按应用的配置文件（profile） |
| libkrun / krunvm（libkrun/*） | Apache-2.0（`LICENSE`） | 库形式的 KVM 微虚拟机（Linux KVM / macOS HVF） | “完整隔离档”在有 KVM 的机器上的候选；镜像即根文件系统目录的思路 |
| Firecracker（firecracker-microvm/firecracker） | Apache-2.0（`LICENSE`） | KVM 微虚拟机，REST API 控制 | 用版本化的 API 控制后端的做法（见 environment-provider-protocol）；因没有显示设备，不作为带桌面的完整环境 VMM |
| cloud-hypervisor（cloud-hypervisor/cloud-hypervisor） | Apache-2.0（`LICENSE`） | Rust VMM，KVM，virtio-blk / net / fs / console，virtio-gpu 路径，可跑 Linux 与 Windows 来宾 | **狐狸OS 操作系统上完整虚拟机的 VMM**：随 ISO 提供官方或构建脚本编出的二进制，保留 NOTICE；来宾桌面进狐狸OS 窗口。不把上游源码整树拷进仓库 |
| wayvnc（any1/wayvnc） | ISC（`LICENSE`） | 把 Wayland 会话以 VNC/RFB 提供出去 | 完整虚拟机来宾桌面的过渡显示通道（经 vsock）；宿主窗口是狐狸OS 自己的，随后用 virtio-gpu 替换 |

## macOS

| 项目 | 许可证 | 机制 | 借鉴 |
|---|---|---|---|
| Lima（lima-vm/lima） | Apache-2.0 | Virtualization.framework / QEMU 跑 Linux 虚拟机，YAML 模板 | 镜像模板目录（发行版 → 多架构镜像地址 + 摘要）、virtiofs 共享主目录 |
| UTM（utmapp/UTM） | Apache-2.0 | QEMU 与 Virtualization.framework 的图形前端 | 虚拟机配置界面的组织方式 |
| Code-Hex/vz | MIT | Virtualization.framework 的 Go 绑定 | 对照它确认 VZ 配置项（引导器、virtio 设备、NAT、virtio-fs）的用法；FoxVZ.swift 直接用 Swift 调用，没有复制 |
| vfkit（crc-org/vfkit） | Apache-2.0 | 命令行方式启动 VZ 虚拟机 | “用一个小的辅助程序 + 命令行参数驱动 VZ”的结构，正是 FoxVZ 的做法 |
| Apple containerization / container | Apache-2.0 | 每个容器一个轻量 VZ 虚拟机 | macOS 上“完整隔离档”的方向：每个环境一个最小 Linux 虚拟机 |
| Seatbelt（sandbox-exec，系统自带） | Apple 系统组件 | SBPL 策略文件 | 轻量沙箱：默认拒绝、只允许写工作空间与临时目录、网络按需开放 |

## Windows

| 项目 | 许可证 | 机制 | 借鉴 |
|---|---|---|---|
| microsoft/WSL | MIT | WSL2 本身已开源 | 对照 `wsl.exe` 的参数与 `--list --online` 输出格式，确定命令契约 |
| microsoft/hcsshim | MIT | Host Compute Service（HCS）的 Go 封装 | Hyper-V 隔离容器 / 虚拟机的计算系统 JSON 文档结构；后续 HCS 提供者的参考 |
| Windows Sandbox（系统自带） | Windows 组件 | `.wsb` XML 配置（映射文件夹、网络、登录命令） | 一键生成 `.wsb` 启动一次性 Windows 来宾 |
| AppContainer / 受限令牌 / Job Object（系统自带） | Windows API | 进程级隔离与资源限制 | 轻量沙箱档：受限令牌 + 低完整性 + Job Object 限制进程数与内存 |
| Sandboxie-Plus | Classic 版 GPL-3.0（`LICENSE.Classic`）；Plus 版为自定义商业许可（`LICENSE.Plus`，非商业免费，商业需证书） | 内核驱动做文件 / 注册表重定向 | 只借鉴思路：写时重定向到沙箱目录的体验 |

## 面向智能体的沙箱

| 项目 | 许可证 | 机制 | 借鉴 |
|---|---|---|---|
| anthropics/sandbox-runtime（原 anthropic-experimental） | Apache-2.0 | macOS 用 sandbox-exec + 动态生成的 Seatbelt 策略；Linux 用 bubblewrap + 网络命名空间；Windows 用专用本地账户 + WFP 出站过滤 + 写受限令牌；网络经宿主上的 HTTP / SOCKS 代理按域名放行 | “轻量档”的整体设计：文件写入白名单 + 默认无网络 + 经代理放行域名 |
| openai/codex 沙箱（codex-rs/linux-sandbox、sandboxing、windows-sandbox-rs） | Apache-2.0 | Linux：Landlock 文件规则 + seccomp（禁 ptrace、io_uring，按需只允许 AF_UNIX 套接字）；macOS：默认拒绝的 SBPL 基础策略；Windows：受限令牌、ACL、WFP | 轻量档的 seccomp 补充规则（ptrace、process_vm_*、io_uring）与“只读 / 工作空间可写 / 完全放开”三档策略 |
| E2B（e2b-dev/E2B） | Apache-2.0 | 云端 Firecracker 沙箱 + SDK | 远程提供者的接口形态（创建、执行、文件、关闭） |
| microsandbox（superradcompany/microsandbox） | Apache-2.0 | 基于 libkrun 的本地微虚拟机 | 本地微虚拟机作为可插拔提供者 |

## 结论（已写入 docs/environments.md 的“隔离级别与平台选择”）

- 每个智能体会话可选两档隔离：**轻量**（进程级沙箱，启动快，与宿主共享系统）和**完整**（独立发行版 / 虚拟机）
- Linux：轻量 = 用户命名空间 + 只读宿主根 + Landlock + seccomp；完整 = 有 KVM 时用 cloud-hypervisor 跑带桌面的虚拟机（见 [os.md](os.md)、[environments.md](environments.md)），否则用已有的命名空间 + overlayfs + pivot_root + cgroup / rlimit + seccomp 环境
- Windows：轻量 = 受限令牌 + Job Object（后续 AppContainer）；完整 = WSL2 发行版、Windows Sandbox、Hyper-V 虚拟机
- macOS：轻量 = Seatbelt（sandbox-exec 生成策略）；完整 = Virtualization.framework Linux 虚拟机
