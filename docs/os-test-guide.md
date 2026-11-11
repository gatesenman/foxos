# 狐狸OS 0.3.1 预览版测试指南

这是可引导、可安装的 狐狸OS ISO（Ubuntu 24.04 基础，XFCE 桌面，默认简体中文）。下面说明怎么在 U 盘、真实电脑、Hyper-V 和本机构建测试里启动它。Windows 上的 `.exe` 是伴侣程序，不是这张 ISO。

预发布：[v0.3.1-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.1-os-preview)

| 文件 | 说明 |
| --- | --- |
| `FoxOS-0.3.1-amd64.iso.part1` | 分卷 1（838860800 字节） |
| `FoxOS-0.3.1-amd64.iso.part2` | 分卷 2（723613696 字节） |
| `FoxOS-0.3.1-amd64.iso` | 拼接后的 Live + 安装镜像（UEFI，可选 BIOS），1562474496 字节，小于 2 GB |
| `SHA256SUMS` | 校验和（含完整 ISO 与两个分卷） |

完整 ISO 的 SHA-256 为 `7acb74c92d159034966821900d43ddeec1815d0d7456d57232811371c31b4500`。Release 上只有两个分卷：本构建环境单个上传约 1.46 GiB 的完整 ISO 时连接在中途断开，所以请把分卷拼起来再校验。

Linux / macOS：

```bash
base=https://github.com/gatesenman/foxos/releases/download/v0.3.1-os-preview
curl -L -O "$base/FoxOS-0.3.1-amd64.iso.part1"
curl -L -O "$base/FoxOS-0.3.1-amd64.iso.part2"
curl -L -O "$base/SHA256SUMS"
cat FoxOS-0.3.1-amd64.iso.part1 FoxOS-0.3.1-amd64.iso.part2 > FoxOS-0.3.1-amd64.iso
sha256sum -c SHA256SUMS --ignore-missing
```

Windows（PowerShell）：

```powershell
cmd /c copy /b FoxOS-0.3.1-amd64.iso.part1+FoxOS-0.3.1-amd64.iso.part2 FoxOS-0.3.1-amd64.iso
Get-FileHash -Algorithm SHA256 .\FoxOS-0.3.1-amd64.iso
```

上一版 [v0.3.0-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.0-os-preview)（labwc 桌面，ISO SHA-256 `4c0986f71e8650123adc996e2a0b512d00a874dab8f1f3468464976d308e9ea6`）保持不变，不再推荐。

进入桌面后可以这样确认：底栏左下角是「开始」，右侧是时钟、「人工接管」和「系统」；打开终端（Super+回车）运行 `whoami`（应为 `foxos`）、`echo $XDG_CURRENT_DESKTOP`（应为 `XFCE`）和 `foxos desktop windows`（列出真实窗口）。默认是英文键盘，Ctrl+空格 切换拼音。

## 在 U 盘上写盘（推荐在真实电脑上试）

在 Linux 上（把 `sdX` 换成你的 U 盘，先确认不会覆盖系统盘）：

```bash
sudo dd if=FoxOS-0.3.1-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

在 Windows 上可用 Rufus 或 `balenaEtcher`，把 ISO 写到 U 盘（DD / 镜像模式）。然后从 U 盘启动（UEFI 优先；部分机器也可走传统 BIOS）。

默认菜单「狐狸OS（试用或安装）」会自动登录用户 `foxos`（空密码），进入 XFCE 桌面：底部面板（开始、时钟、系统、人工接管）、壁纸，以及真实的窗口（终端、文件管理器、编辑器、Firefox）。中文界面与 Fcitx5 拼音默认开启；物理键盘布局是 US。

要安装到硬盘：打开开始菜单里的「安装 狐狸OS」（Calamares）。安装过程会分区并写入引导，请先备份。安装完成后去掉 U 盘再启动。

LibreOffice 与部分大型组件不在第一张 ISO 里，安装后按提示再下载。

## Hyper-V（Windows 伴侣环境）

在已启用虚拟化的 Windows 上：

1. 新建第二代虚拟机（UEFI），挂上 `FoxOS-0.3.1-amd64.iso`，分配至少 4 GB 内存、2 个虚拟处理器和一块虚拟硬盘（若要安装）。
2. 启动后应进入与 U 盘相同的 Live 桌面。第一代（BIOS）也可以试，但优先用第二代。
3. 若只看到文本控制台、没有桌面，请把日志或照片发回 issue，并说明是否开启了虚拟化（任务管理器 → 性能 → 虚拟化）。

Windows 伴侣程序里的「环境」以后会用 Hyper-V / WSL2 启动同一张 ISO；本预览请先按上面步骤在 Hyper-V 管理器里直接挂载 ISO 验证。

## 本机构建测试（QEMU 仅用于开发，不是产品依赖）

QEMU / Docker 都不是狐狸OS 的运行时。完整来宾环境用内核 KVM + cloud-hypervisor，或轻量命名空间；Windows 伴侣用 WSL2 / Hyper-V。

```bash
# 在仓库里制作 ISO，见 docs/os-build.md
sudo FOXOS_OS_KEEP=1 scripts/os/build-iso.sh

# 测试引导（有可用 KVM 时用 KVM，否则 TCG）
scripts/os/qemu-boot.sh build/os/FoxOS-0.3.1-amd64.iso
```

本构建机若 `/dev/kvm` 存在但创建 vCPU 触发内核 BUG，请加 `--tcg`。这只影响开发机，不影响真实电脑或正常 Hyper-V。

## Docker Hub（分发通道，尚未推送）

试用镜像计划用 cloud-hypervisor + 宿主 `/dev/kvm` 引导**真正的** ISO，并把桌面通过 VNC / noVNC 暴露出来，不在容器里画假桌面。镜像名预定 `gatesenman/foxos`，标签与本 Release 版本对齐。在 Sarah 登录 Docker Hub 并同意推送之前，仓库里只有 Dockerfile 与说明，见 [docker.md](docker.md)。Docker Official Images / Marketplace 是单独的申请，不会在未同意时提交。

## 还请留意

- macOS 来宾环境在 PC / 这张 Linux ISO 上是禁用的（需要 Apple 硬件上的 Virtualization.framework），不是漏做。
- 不要把 Windows 评估版 ISO 再分发进 GitHub Release。
- 预览版的智能体窗口控制、全部发行版环境目录还在迭代；第一张 ISO 的目标是：能开机、能看到真桌面、能安装。
