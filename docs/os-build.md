# 狐狸OS ISO 怎么做

本文件与 `scripts/os/` 里的脚本对应，没有隐藏步骤。产品形态与技术选型见 [os.md](os.md)。

## 产出

- `build/os/FoxOS-0.3.1-amd64.iso`：Live（可试用）+ Calamares 安装器，UEFI 与传统 BIOS 都能引导
- `build/os/SHA256SUMS`：该 ISO 的 sha256。当前代码在构建机上产出 `FoxOS-0.3.1-amd64.iso`（1562474496 字节，SHA-256 `7acb74c92d159034966821900d43ddeec1815d0d7456d57232811371c31b4500`，即 Release v0.3.1-os-preview 上的镜像）。该文件已在 `.gitignore` 中，不会提交进 git。
- 单个 ISO 必须小于 2 GB（GitHub Release 的文件上限）。LibreOffice、Everything 应用、ACP 智能体等较大组件不打进 ISO，安装后在线获取。

`build/` 已在 `.gitignore` 里，不把 ISO 提交进 git。

## 依赖（构建机）

在 Debian / Ubuntu 构建机上安装：

```bash
sudo apt-get install debootstrap squashfs-tools xorriso grub-efi-amd64-bin grub-pc-bin \
  mtools dosfstools rsync wget ca-certificates
```

测试引导（**不是产品依赖**，不要装进 ISO）再加：

```bash
sudo apt-get install qemu-system-x86 ovmf qemu-utils
```

需要能访问 Ubuntu 24.04（noble）软件源，以及 GitHub（下载 cloud-hypervisor 官方静态二进制）和 Mozilla（下载 Firefox 官方 tarball）。

## 一条命令

在仓库根目录：

```bash
sudo scripts/os/build-iso.sh
```

常用环境变量：

| 变量 | 默认 | 含义 |
|---|---|---|
| `FOXOS_OS_WORK` | `/var/tmp/foxos-os` | 工作目录（chroot、缓存、临时 ISO 树） |
| `FOXOS_OS_OUT` | `<仓库>/build/os` | 写 ISO 与 SHA256SUMS 的目录 |
| `FOXOS_OS_MIRROR` | `http://archive.ubuntu.com/ubuntu` | Ubuntu 软件源，可换成国内镜像 |
| `FOXOS_OS_KEEP=1` | 关 | 结束后保留临时 ISO 树 |
| `FOXOS_OS_REPACK=1` | 关 | 复用已有 chroot，跳过 apt / Firefox / VMM 下载，只重跑 hook 并打包 |
| `FOXOS_CH_VERSION` | `v46.0` | 要下载的 cloud-hypervisor 版本标签 |

脚本会自行 `sudo`。已存在的 chroot 会复用（跳过 debootstrap）；要完全重做就删掉 `$FOXOS_OS_WORK/chroot`。

## 脚本实际做的事（按顺序）

1. **debootstrap** `--variant=minbase` 安装 Ubuntu 24.04（noble, amd64）。这是底本，随后用 APT 装包，不用 live-build / mkosi 等封装器。
2. 写入 `scripts/os/config/sources.list`（main / universe / restricted 与对应的 updates、security），在 chroot 里 `apt-get install` `config/packages.list` 中的包：内核、casper（Live 启动）、XFCE（xfce4-session、xfwm4、xfce4-panel、Whisker 菜单等）、Thunar、XFCE Terminal、Calamares、lightdm、Fcitx5、字体、NetworkManager、Hyper-V 来宾守护进程、GRUB 等。
3. 下载并安装 **Firefox 官方 Linux x64 tarball**（中文语言包）到 `/opt/firefox`。不用 Ubuntu 默认的 Snap。
4. 下载 **cloud-hypervisor** 官方静态二进制（Apache-2.0）到 `/usr/lib/foxos/vmm/`，并写入 `NOTICE`（版本、来源、许可）。这是完整环境的 VMM，不是 QEMU。
5. 把本仓库的狐狸OS Python 包拷到 `/usr/lib/foxos/python`，安装 `/usr/bin/foxos` 与用户级 systemd 服务 `foxos-mcp.service`。
6. 跑 `scripts/os/hooks/` 里的脚本（按文件名顺序）：locale / 时区、os-release 与壁纸等品牌、XFCE 会话与主题、安装器配置、initramfs 模块（virtio、Hyper-V、NVMe、USB）、清理构建机代理和 APT 缓存。**构建机上的代理配置不会留在 ISO 里。**
7. 从 chroot 取出内核与 initrd，用 **mksquashfs**（xz）做成 `/casper/filesystem.squashfs`。
8. 用宿主上的 **grub-mkrescue** 做成混合 ISO（UEFI + BIOS），卷标 `FOXOS_030`。启动参数见 `scripts/os/iso/grub.cfg`（`boot=casper`，默认 locale 为 zh_CN）。

Live 用户名为 `foxos`（见 `scripts/os/branding/casper.conf`）。在 Live 介质上 lightdm 会自动登录；安装到硬盘后不会自动登录，由 Calamares 创建的用户从登录器进入「狐狸OS」会话（XFCE / `startxfce4`）。

## 测试引导

```bash
scripts/os/qemu-boot.sh                          # UEFI + KVM；KVM 不可用时直接报错，不会悄悄改用 TCG
scripts/os/qemu-boot.sh --tcg --gtk              # 明确要求软件模拟（也可设 FOXOS_ALLOW_TEST_VMM=qemu-tcg）
scripts/os/qemu-boot.sh build/os/FoxOS-0.3.1-amd64.iso --install-disk /tmp/foxos-disk.qcow2
```

默认把内核串口写到 `$FOXOS_OS_WORK/qemu/serial.log`（`console=ttyS0`）。若构建机上的 QEMU 没有 VNC 显示模块，脚本会改用 gtk。

QEMU 只用于在本开发机上自动测试，**不是狐狸OS 的一部分**，也不进入 ISO。在真实电脑或 Hyper-V 里测试请看 [os-test-guide.md](os-test-guide.md)（该文件随第一张可引导 ISO 一起补齐）。

## 真实桌面截图

```bash
sudo scripts/os/tools/shoot-desktop.sh /tmp/foxos-shots 1920x1080
```

在构建出的根文件系统（`$FOXOS_OS_WORK/chroot`）上叠一层临时 overlay，不改 chroot 本身；建 Live 用户 `foxos`（全名「狐狸OS」），用独立 UTS 命名空间把主机名设为 `foxos`，在 Xvfb 上以 `startxfce4` 启动和 ISO 完全相同的 XFCE 会话，然后打开终端、Whisker 开始菜单和 Mousepad 截图。`docs/screenshots/os-*.png` 就是这样生成的。

## 许可证方面的处理

- XFCE、Calamares、GRUB、casper 等 GPL / 以 GPL 为主的组件：**只通过 Ubuntu 软件包安装**，不把源码拷进本仓库。狐狸OS 窗口装饰与面板样式见 `scripts/os/branding/xfce/ATTRIBUTION.md`。
- cloud-hypervisor：Apache-2.0，官方二进制 + `NOTICE`。
- Firefox：Mozilla 官方构建，按 Mozilla 公共许可分发；ISO 里保留其自身的许可文件。
- 不内置 AGPL 的 Everything 应用源码；不内置 Windows ISO。

## 排错

- debootstrap 失败：检查网络与 `FOXOS_OS_MIRROR`，以及构建机的 debootstrap 是否认识 `noble`（`ls /usr/share/debootstrap/scripts/noble`）。
- chroot 里 `apt-get` 失败：有时构建机的 HTTP 代理对 APT 不友好；脚本会在检测到 `/etc/apt/apt.conf.d/99-box-proxy` 时临时拷进 chroot，并在 hook `90-cleanup.sh` 里删除。
- ISO 引导后掉进 initramfs 的 busybox，并提示 `/cow format specified as 'overlay' and no support found`：检查 `scripts/os/branding/casper.conf` 里的 `BUILD_SYSTEM` 必须是 `Ubuntu` 或 `Debian`（这是 casper 的内部字段，不是产品名）。写成其它值时，casper 会执行 `modprobe "" -b overlay` 而失败。`scripts/os/verify-initrd.sh` 会在打包时拦下这个问题。Ubuntu 24.04 的 `linux-image-generic` 已把 squashfs / loop / virtio_blk / sr_mod 编进内核，不必以模块形式存在于 initrd；overlay 仍是模块，必须在 initrd 里。
- 启动日志里出现 `plymouthd: not found`：initramfs 里有 plymouth 脚本但没有守护进程（没装主题时 hook 会跳过复制）。构建 hook 会在没有 plymouthd 时删掉这些脚本；grub 也不再传 `splash`。
- ISO 引导后没有图形：用菜单里的「安全模式」看启动日志，或读 QEMU 串口日志；确认 `casper` 找到了 squashfs。
- 此宿主 `/dev/kvm` 存在但创建 vCPU 触发内核 BUG：`qemu-boot.sh` 会报错退出，需明确加 `--tcg`（或 `FOXOS_ALLOW_TEST_VMM=qemu-tcg`）才用软件模拟。这只影响本机构建测试，不影响 ISO 在真实电脑或正常 Hyper-V 上使用 KVM。
- ISO ≥ 2 GB：从 `packages.list` 再减包，或提高 squashfs 压缩（脚本已用 xz）。

## arm64 镜像

`FOXOS_OS_ARCH=arm64 scripts/os/build-iso.sh` 在 arm64 机器上构建 `FoxOS-<版本>-arm64.iso`（GitHub Actions 用 `ubuntu-24.04-arm`，见 [`release.yml`](../.github/workflows/release.yml) 的 `iso` 任务）。和 amd64 的区别：

- 软件源换成 `http://ports.ubuntu.com/ubuntu-ports`；只做 UEFI 引导（`grub-efi-arm64-signed`，构建机需要 `grub-efi-arm64-bin`），没有 BIOS 和 Hyper-V 来宾工具。
- Firefox 用 Mozilla 的 `linux64-aarch64` 包，cloud-hypervisor 用 `cloud-hypervisor-static-aarch64`。
- Google 不发布 Linux arm64 版 Chrome：`foxos-chrome-setup --status` 返回 `unsupported-arch`，「Google Chrome」入口直接打开 Firefox。
- 串口控制台是 `ttyAMA0`（QEMU virt 与多数 ARM 服务器）。

每个 ISO 必须小于 2 GiB（GitHub Release 单文件上限）；CI 同时上传单文件和 800 MiB 分卷。
