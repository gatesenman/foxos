# 狐狸OS 0.3.0 预览版测试指南

这是第一张**可引导、可安装**的 狐狸OS ISO（Ubuntu 24.04 基础，XFCE 桌面）。下面说明怎么在 U 盘、真实电脑、Hyper-V 和本机构建测试里启动它。Windows 上的 `.exe` 是伴侣程序，不是这张 ISO。

本仓库当前代码已经把默认图形会话改成 XFCE。在构建机上新做出来的 ISO 是：

- `build/os/FoxOS-0.3.0-amd64.iso`：1534500864 字节（约 1.43 GiB，小于 2 GB）
- SHA-256：`8d70c6514df41dd85ddaff0b53ce4308e0b27ed13afd441687f23d536b1ef3bb`

下面表格与校验和仍对应 GitHub Release [v0.3.0-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.0-os-preview) 上已发布的分卷（更换 XFCE 之前的预览镜像）。新构建还没有拆分上传到该 Release。若要用 XFCE 这版，请在仓库里按 [os-build.md](os-build.md) 自行制作，或等待下一次发布。

预发布：[v0.3.0-os-preview](https://github.com/gatesenman/foxos/releases/tag/v0.3.0-os-preview)

| 文件 | 说明 |
| --- | --- |
| `FoxOS-0.3.0-amd64.iso.part1` | 分卷 1（838860800 字节） |
| `FoxOS-0.3.0-amd64.iso.part2` | 分卷 2（668198912 字节） |
| `FoxOS-0.3.0-amd64.iso` | 拼接后的 Live + 安装镜像（UEFI，可选 BIOS），1507059712 字节，小于 2 GB |
| `SHA256SUMS` | 校验和（含完整 ISO 与两个分卷） |

完整 ISO 的 SHA-256 为 `4c0986f71e8650123adc996e2a0b512d00a874dab8f1f3468464976d308e9ea6`。Release 上是两个分卷（本构建环境上传单个 1.4 GiB 附件会在中途断开）。

```bash
base=https://github.com/gatesenman/foxos/releases/download/v0.3.0-os-preview
curl -L -O "$base/FoxOS-0.3.0-amd64.iso.part1"
curl -L -O "$base/FoxOS-0.3.0-amd64.iso.part2"
curl -L -O "$base/SHA256SUMS"
cat FoxOS-0.3.0-amd64.iso.part1 FoxOS-0.3.0-amd64.iso.part2 > FoxOS-0.3.0-amd64.iso
sha256sum -c SHA256SUMS
```

## 在 U 盘上写盘（推荐在真实电脑上试）

在 Linux 上（把 `sdX` 换成你的 U 盘，先确认不会覆盖系统盘）：

```bash
sudo dd if=FoxOS-0.3.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

在 Windows 上可用 Rufus 或 `balenaEtcher`，把 ISO 写到 U 盘（DD / 镜像模式）。然后从 U 盘启动（UEFI 优先；部分机器也可走传统 BIOS）。

默认菜单「狐狸OS（试用或安装）」会自动登录用户 `foxos`（空密码），进入 XFCE 桌面：底部面板（开始、时钟、系统、人工接管）、壁纸，以及真实的窗口（终端、文件管理器、编辑器、Firefox）。中文界面与 Fcitx5 拼音默认开启；物理键盘布局是 US。

要安装到硬盘：打开开始菜单里的「安装 狐狸OS」（Calamares）。安装过程会分区并写入引导，请先备份。安装完成后去掉 U 盘再启动。

LibreOffice 与部分大型组件不在第一张 ISO 里，安装后按提示再下载。

## Hyper-V（Windows 伴侣环境）

在已启用虚拟化的 Windows 上：

1. 新建第二代虚拟机（UEFI），挂上 `FoxOS-0.3.0-amd64.iso`，分配至少 4 GB 内存、2 个虚拟处理器和一块虚拟硬盘（若要安装）。
2. 启动后应进入与 U 盘相同的 Live 桌面。第一代（BIOS）也可以试，但优先用第二代。
3. 若只看到文本控制台、没有桌面，请把日志或照片发回 issue，并说明是否开启了虚拟化（任务管理器 → 性能 → 虚拟化）。

Windows 伴侣程序里的「环境」以后会用 Hyper-V / WSL2 启动同一张 ISO；本预览请先按上面步骤在 Hyper-V 管理器里直接挂载 ISO 验证。

## 本机构建测试（QEMU 仅用于开发，不是产品依赖）

QEMU / Docker 都不是狐狸OS 的运行时。完整来宾环境用内核 KVM + cloud-hypervisor，或轻量命名空间；Windows 伴侣用 WSL2 / Hyper-V。

```bash
# 在仓库里制作 ISO，见 docs/os-build.md
sudo FOXOS_OS_KEEP=1 scripts/os/build-iso.sh

# 测试引导（有可用 KVM 时用 KVM，否则 TCG）
scripts/os/qemu-boot.sh build/os/FoxOS-0.3.0-amd64.iso
```

本构建机若 `/dev/kvm` 存在但创建 vCPU 触发内核 BUG，请加 `--tcg`。这只影响开发机，不影响真实电脑或正常 Hyper-V。

## Docker Hub（分发通道，尚未推送）

试用镜像计划用 cloud-hypervisor + 宿主 `/dev/kvm` 引导**真正的** ISO，并把桌面通过 VNC / noVNC 暴露出来，不在容器里画假桌面。镜像名预定 `gatesenman/foxos`，标签与本 Release 版本对齐。在 Sarah 登录 Docker Hub 并同意推送之前，仓库里只有 Dockerfile 与说明，见 [docker.md](docker.md)。Docker Official Images / Marketplace 是单独的申请，不会在未同意时提交。

## 还请留意

- macOS 来宾环境在 PC / 这张 Linux ISO 上是禁用的（需要 Apple 硬件上的 Virtualization.framework），不是漏做。
- 不要把 Windows 评估版 ISO 再分发进 GitHub Release。
- 预览版的智能体窗口控制、全部发行版环境目录还在迭代；第一张 ISO 的目标是：能开机、能看到真桌面、能安装。
