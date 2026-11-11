# 预设系统：在线选择并安装 Linux / Windows / macOS

“环境”应用 → **安装系统** 顶部的「狐狸OS 预设系统（已配置好）」，或命令行 / MCP：

```bash
foxos env catalog --presets                                   # 列出预设：下载大小、所需磁盘、本机能否安装及原因
foxos env install foxos-debian-12 dev --dry-run               # 只看计划：要下载的分卷、URL、sha256
foxos env install foxos-debian-12 dev --start --wait-ready 1800
foxos env progress dev                                        # 进度：第几个分卷、字节数、续传次数、校验阶段
foxos env exec dev -- foxos --version                         # 经 SSH 来宾桥在来宾里执行
foxos env install windows-11-enterprise-eval win11 --product-key XXXXX-XXXXX-XXXXX-XXXXX-XXXXX   # 密钥可选
```

MCP 工具同名：`env.catalog`（参数 `presets`）、`env.install`（参数 `product_key`、`start`、`wait_ready`）、`env.progress`。

## 预设里有什么

每个预设都已经配好：桌面（Linux 为 XFCE + lightdm 自动登录）、默认简体中文（`zh_CN.UTF-8`、Noto CJK 字体、Asia/Shanghai）、Node.js、Bun、Python、Git、ACP 智能体（预装 Gemini CLI，Apache-2.0；Claude Code 等专有许可的智能体在首次使用时在线安装）、`foxos` CLI 与 foxos MCP 用户服务，以及来宾桥（OpenSSH，主机生成的密钥；Linux 另有 x11vnc 只监听来宾回环）。

来宾首次启动时 `foxos-preset-firstboot` 从标签为 `FOXOSSEED` 的种子光盘读 `seed.json`（用户、SSH 公钥、主机名、语言、时区），`foxos-preset-ready` 在串口与 `/run/foxos-ready` 上报一行 `FOXOS-PRESET-READY ... node=... bun=... python=... foxos=...`，主机的 `--wait-ready` 等的就是这一行。

## 目录与发布

目录在 `packages/core/foxos/data/env-presets.json`（格式 `foxos-env-presets/1`），由 `scripts/presets/make-catalog.py` 从构建产物生成。Linux 镜像由 `scripts/presets/build-preset.sh <debian-12|ubuntu-24.04>` 构建（debootstrap → 8 GB GPT 磁盘 → 压缩 qcow2 按 900 MB 分卷 + WSL 根文件系统 tar.gz + SHA256SUMS），发布在 GitHub Release `presets-2026.11`。

| 预设 | 来源 | 狐狸OS 主机（Linux） | Windows 伴侣 | Mac |
| --- | --- | --- | --- | --- |
| `foxos-debian-12`、`foxos-ubuntu-24.04` | 狐狸OS Release 的 qcow2 分卷 / WSL tar.gz | `linux-kvm`：UEFI 磁盘 + 种子光盘 | `wsl2`：`wsl --import` | 不提供（x86_64 镜像，arm64 预设尚未发布） |
| `foxos-os-0.3.2` | 狐狸OS ISO 分卷（`v0.3.2-os-preview`） | `linux-kvm` 从 ISO 引导 | `hyperv` 第 2 代虚拟机 | 不提供 |
| `windows-11-enterprise-eval`、`windows-server-2025-eval` | 安装时从微软官方下载中文评估版 ISO | 不提供（见下） | `hyperv` | 不提供 |
| `macos-latest` | 安装时由 Virtualization.framework 取 Apple 官方 IPSW | 不提供（Apple 许可） | 不提供（Apple 许可） | `macos-vz`，仅 Apple 芯片 |

本机不能装的条目在目录里照样列出，但禁用并写明原因。

### 下载、续传、校验

`foxos/envs/download.py`：每个分卷写到 `.partial`，断线后用 HTTP `Range` 从已下载的字节继续；每个分卷核对大小和 sha256，拼接后再核对整体 sha256；不一致就删除并报 `CONFLICT`，不会留下坏文件。已经下载且校验通过的文件直接复用，所以中断后再执行一次同样的 `env install`（或在界面上再点一次「安装」）就是续传。安装前检查磁盘剩余空间（下载 + 解压后的磁盘）。

## Windows：只发布配方

微软不允许再分发装好的 Windows 镜像，所以狐狸OS 不发布任何 Windows 镜像。安装时：

1. 从微软官方链接下载中文评估版 ISO（也可以 `--iso` 用自己的 ISO）；
2. 生成种子盘（`IMAPI2FS`，标签 `FOXOSSEED`）：`autounattend.xml`（zh-CN、清空并分区第一块磁盘、本地用户 `foxos` 随机密码并自动登录；填了产品密钥才写 `<ProductKey>`，评估版不需要）+ `foxos/postinstall.ps1` + `seed.json`；
3. Hyper-V 第 2 代虚拟机挂两张光盘（安装 ISO + 种子盘），开 vTPM（Windows 11 需要），开机时按 Enter 通过「Press any key to boot from CD」；
4. 首次登录时 `postinstall.ps1` 安装 Node.js、Python、Git、Bun、Gemini CLI、狐狸OS 伴侣程序（`install.ps1 -Silent`）和 OpenSSH 服务器（放入主机的公钥），最后写就绪文件。

评估版有使用期限（微软评估中心页面写明），到期后需要正式许可；界面和目录里都显示许可说明，可以在安装对话框里填自己的产品密钥。

狐狸OS 主机上 Windows 预设禁用：产品 VMM 是 cloud-hypervisor，没有安装期需要的 CD-ROM / AHCI 和驱动注入路径。请在 Windows 伴侣程序里用 Hyper-V 安装。

## macOS：只在 Mac 上

Apple 只允许在 Apple 硬件上的 macOS 里虚拟化 macOS，狐狸OS 不提供任何 macOS 镜像，也不支持非 Apple 硬件。在 Apple 芯片 Mac 上：`foxvz install-macos` 用 `VZMacOSRestoreImage.fetchLatestSupported` 取 Apple 官方 IPSW 并用 `VZMacOSInstaller` 安装；`foxvz run-macos` 启动，种子目录以 virtio-fs 标签 `foxos-seed` 只读共享。macOS 的「设置助理」需要人完成，之后在来宾终端运行共享目录里的 `macos-postinstall.sh`（Homebrew、Node、Bun、Python、Gemini CLI、foxos、SSH 公钥）。辅助程序编译后要用 `foxvz.entitlements`（`com.apple.security.virtualization`）签名，安装向导会做这一步。

## 验证到什么程度（如实说明）

已在本机（Linux 容器，KVM 不可用，用 `FOXOS_ALLOW_TEST_VMM=qemu-tcg` 明确允许 QEMU TCG 代替）实际跑过：

- 构建 `debian-12`、`ubuntu-24.04` 两个预设镜像，打包分卷与 SHA256SUMS；
- `foxos env install foxos-debian-12 ... --start --wait-ready`：分卷下载、逐卷与整体 sha256 校验、种子光盘、UEFI 引导、来宾上报 `FOXOS-PRESET-READY`，再用 `foxos env exec` 经 SSH 在来宾里执行命令（中文 locale、Node、Bun、foxos）；
- 断线续传（本地 HTTP 服务器在传输中途断开，第二次请求带 `Range` 从断点继续）、sha256 不一致时删除并报错、分卷拼接；
- Windows 应答文件生成并按 XML 解析、Hyper-V 安装计划（两张光盘、vTPM、按键）、种子盘 PowerShell 脚本生成；
- 目录在 Linux 主机上对 Windows / macOS 条目给出的不可用原因。

没有实际跑过：

- Windows 预设的完整安装（需要 Windows 主机与 Hyper-V；无人值守安装、`postinstall.ps1`、按 Enter 引导都未在真实 Hyper-V 上验证）；
- Windows 上用 WSL2 导入 Linux 预设；
- macOS 预设（需要 Apple 芯片 Mac；`FoxVZ.swift` 的 `install-macos` / `run-macos` 没有在 Mac 上编译过）；
- 真实 KVM + cloud-hypervisor 引导预设 qcow2（cloud-hypervisor 需要 CLOUDHV 固件，当前代码给的是 OVMF；网络也只在 QEMU 用户网络下验证过）；
- 狐狸OS ISO 预设（`foxos-os-0.3.2`）作为来宾的安装流程只在 `--dry-run` 下核对过计划。
