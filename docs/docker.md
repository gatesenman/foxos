# 狐狸OS 与 Docker Hub / FoxOS on Docker Hub

中文在前，English follows.

> **这是分发通道，不是运行时。** 狐狸OS 本身不在系统里依赖 Docker / Podman / LXC / VirtualBox / QEMU。完整来宾环境用内核 KVM + cloud-hypervisor（或轻量命名空间沙箱；Windows 上的伴侣程序用 WSL2 / Hyper-V）。Docker 镜像只为了让人 `docker pull` / `docker run` 试用，或把 ISO 拉下来做在线安装。

> **This is a distribution channel, not the OS runtime.** FoxOS does not depend on Docker, Podman, LXC, VirtualBox, or QEMU as a product component. Full guests use in-kernel KVM plus cloud-hypervisor (or a light namespace sandbox; the Windows companion uses WSL2 / Hyper-V). The Docker image exists so people can `docker pull` / `docker run` a trial, or fetch the ISO for an online install.

预定公开仓库名是 [`gatesenman/foxos`](https://hub.docker.com/r/gatesenman/foxos)。**现在还没有推送。** 需要 Sarah 的 Docker Hub 账号登录之后才会 `docker push`。没有账号之前请不要发明一个，也不要把密码写进仓库。

The intended public repository is [`gatesenman/foxos`](https://hub.docker.com/r/gatesenman/foxos). **Nothing has been pushed yet.** We will `docker push` only after Sarah signs in with her Docker Hub account. Do not invent an account, and do not put a password in the repo.

## 镜像标签 / Tags

标签与 GitHub Release 版本对齐，例如 `v0.3.0-os-preview` 对应：

| 标签 | 作用 |
|---|---|
| `gatesenman/foxos:0.3.0-os-preview` | 试用：在有 KVM 的 Linux 宿主上，用 **cloud-hypervisor** 引导 **真正的** FoxOS ISO，把来宾桌面以 VNC / 网页暴露出来 |
| `gatesenman/foxos:0.3.0-os-preview-installer` | 在线安装助手：只下载 GitHub Release 里的 ISO 并校验 sha256，不启动虚拟机 |
| `gatesenman/foxos:os-preview` | 指向当前预览试用标签（推送成功后才会有） |

Tags follow the GitHub Release version. `v0.3.0-os-preview` maps to `gatesenman/foxos:0.3.0-os-preview` (trial) and `gatesenman/foxos:0.3.0-os-preview-installer` (ISO download + checksum only).

## 试用（真 ISO，不是假桌面）/ Trial (real ISO, not a fake desktop)

容器里不画一个 Electron 或网页假装桌面。它用和狐狸OS 相同的 VMM（cloud-hypervisor，Apache-2.0 官方静态二进制）在宿主的 `/dev/kvm` 上引导 Release 里的 ISO。来宾 labwc 会话在内核参数带 `foxos.vnc` 时启动 **wayvnc**；容器把 5900（VNC）和 6080（noVNC 网页）转到那台虚拟机。

The container does not paint a fake desktop. It boots the real release ISO with the same VMM FoxOS ships (cloud-hypervisor) on the host’s `/dev/kvm`. When the guest is started with `foxos.vnc`, labwc launches **wayvnc**; the container forwards port 5900 (VNC) and 6080 (noVNC web).

```bash
# 需要 Linux 宿主，并且 CPU 支持虚拟化（VMX/SVM），把 KVM 传进容器
docker pull gatesenman/foxos:0.3.0-os-preview

docker run --rm -it \
  --device /dev/kvm \
  --device /dev/net/tun \
  --cap-add NET_ADMIN \
  -p 5900:5900 -p 6080:6080 \
  -e FOXOS_ISO_SHA256='<把 Release 里 SHA256SUMS 的值贴这里>' \
  gatesenman/foxos:0.3.0-os-preview
```

浏览器打开 `http://127.0.0.1:6080/vnc.html`，或用 VNC 客户端连 `127.0.0.1:5900`。来宾要到图形会话起来之后桌面才会出现，请多等一会儿。

Then open `http://127.0.0.1:6080/vnc.html` or a VNC client at `127.0.0.1:5900`. Wait until the guest graphical session is up.

### 没有 KVM 时 / When there is no KVM

如果看不到 `/dev/kvm`，入口脚本会说明原因并退出，**不会**在容器里塞一个假桌面。请改用 GitHub Release 的 ISO 在真实电脑、已启用虚拟化的 Hyper-V、或本仓库的 `scripts/os/qemu-boot.sh`（QEMU **只用于开发测试**，不是产品依赖）启动。

If `/dev/kvm` is missing, the entrypoint exits with an explanation. It will **not** fake a desktop. Use the GitHub Release ISO on a real PC, on Hyper-V with virtualization enabled, or `scripts/os/qemu-boot.sh` on a dev machine (QEMU is a **test-only** tool, not a product dependency).

可选环境变量：`FOXOS_ISO_URL`、`FOXOS_ISO_SHA256`、`FOXOS_ISO_PATH`、`FOXOS_MEM`（默认 `4G`）、`FOXOS_CPUS`（默认 `2`）、`FOXOS_NOVNC=0` 可关掉网页端。

## 在线安装（只拉 ISO）/ Online install (ISO only)

```bash
docker pull gatesenman/foxos:0.3.0-os-preview-installer

docker run --rm \
  -v "$PWD:/out" \
  gatesenman/foxos:0.3.0-os-preview-installer
```

当前目录会得到 `FoxOS-0.3.0-amd64.iso` 和 `SHA256SUMS`，脚本会按校验和验证。然后把 ISO 写到 U 盘，或在 Hyper-V / 本机虚拟机里启动。安装步骤见 [os-test-guide.md](os-test-guide.md)。

The current directory receives the ISO and `SHA256SUMS`, verified by checksum. Write it to USB or boot it in Hyper-V / a local VM. See [os-test-guide.md](os-test-guide.md).

## 本地构建（尚未登录 Docker Hub 时）/ Build locally (before Docker Hub login)

在仓库根目录：

```bash
docker build -f docker/os/Dockerfile -t gatesenman/foxos:0.3.0-os-preview .
docker build -f docker/os/Dockerfile.installer -t gatesenman/foxos:0.3.0-os-preview-installer .
```

不要在未得到 Sarah 同意、未登录其账号之前执行 `docker login` 或 `docker push`。CI 工作流是 `.github/workflows/docker.yml`，默认只构建；把 `push` 设为 true 且 Secrets 配好之后才会推送。

Do not run `docker login` or `docker push` until Sarah has agreed and signed in. The workflow `.github/workflows/docker.yml` builds only, unless `push` is enabled and the secrets are set.

## Docker Official Images / Marketplace

把镜像推到 **Docker Hub 公开仓库** 之后，任何人都可以立刻 `docker pull`。这 **不是** Docker Official Images、Verified Publisher，也不是 Docker Marketplace / Partner 上架。那些是单独的申请流程，没有 Sarah 的明确指示，我们不会提交。

Publishing to a **public Docker Hub repository** makes `docker pull` work immediately. That is **not** the same as Docker Official Images, Verified Publisher, or a Docker Marketplace / partner listing. Those are separate applications. We will not file them without Sarah’s explicit word.

## 许可证

- 镜像里的 cloud-hypervisor：Apache-2.0，官方静态二进制 + `NOTICE`。
- ISO 本身的许可与 GitHub Release 相同（见 ISO 内文档）。镜像默认在运行时下载 ISO，不把 Windows 评估版或其它专有安装盘打进镜像。
