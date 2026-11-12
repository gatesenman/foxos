# 狐狸OS 容器镜像（Docker Hub / GHCR） / FoxOS container images

中文在前，English follows.

> **这是分发通道，不是运行时。** 狐狸OS 本身不在系统里依赖 Docker / Podman / LXC / VirtualBox / QEMU。完整来宾环境用内核 KVM + cloud-hypervisor（或轻量命名空间沙箱；Windows 上的伴侣程序用 WSL2 / Hyper-V）。容器镜像只为了让人 `docker pull` / `docker run` 试用，或把 ISO 拉下来做在线安装。

> **This is a distribution channel, not the OS runtime.** FoxOS does not depend on Docker, Podman, LXC, VirtualBox, or QEMU as a product component. Full guests use in-kernel KVM plus cloud-hypervisor (or a light namespace sandbox; the Windows companion uses WSL2 / Hyper-V). The images exist so people can `docker pull` / `docker run` a trial, or fetch the ISO for an online install.

预定的公开镜像名有两个，内容相同：

- Docker Hub：[`gatesenman/foxos`](https://hub.docker.com/r/gatesenman/foxos)（即 `docker.io/gatesenman/foxos`）
- GitHub 容器仓库（GHCR）：`ghcr.io/gatesenman/foxos`

**现在两个都还没有推送。** 推送需要 Sarah 明确同意；Docker Hub 还需要她的账号。没有账号之前请不要发明一个，也不要把密码或令牌写进仓库。

There are two intended public image names with the same content: Docker Hub [`gatesenman/foxos`](https://hub.docker.com/r/gatesenman/foxos) and GHCR `ghcr.io/gatesenman/foxos`. **Neither has been pushed yet.** Pushing needs Sarah's explicit go-ahead, and Docker Hub also needs her account. Do not invent an account, and do not put a password or token in the repo.

## 版本 / Version

镜像只有一个版本号 `FOXOS_VERSION`（构建参数，同时写进镜像的环境变量），当前是 `0.3.4`。它决定：

- 默认从哪个 Release 下载：`https://github.com/gatesenman/foxos/releases/download/v<版本>-os-preview/`
- ISO 文件名：`FoxOS-<版本>-amd64.iso`
- 镜像标签：`<版本>-os-preview`（试用）和 `<版本>-os-preview-installer`（在线安装）

There is one version value, `FOXOS_VERSION` (a build arg, also baked in as an env var), currently `0.3.4`. It picks the release (`v<version>-os-preview`), the ISO name (`FoxOS-<version>-amd64.iso`) and the tags. You can override it at run time with `-e FOXOS_VERSION=…`.

## 下载与校验 / Download and verification

两个镜像都用同一个脚本 [`docker/os/fetch-iso.sh`](../docker/os/fetch-iso.sh)（镜像里是 `/usr/local/bin/foxos-fetch-iso`）：

1. 下载 Release 的 `SHA256SUMS`。
2. 已有 ISO 且与 `SHA256SUMS` 一致就直接用，不重下。
3. 从 `SHA256SUMS` 里读出所有 `FoxOS-<版本>-amd64.iso.part-NN` 分卷（0.3.4 是 `part-00`、`part-01`、`part-02`），按顺序逐个下载、逐个校验，追加进 ISO 后立即删掉，磁盘峰值约为「ISO + 一个分卷」。分卷数量变了不用改脚本。单个分卷校验失败会重下一次，仍失败就退出。
4. 拼好的整张 ISO 再按 `SHA256SUMS` 校验一次。Release 里没有分卷时就下载整张 ISO 并校验。

可选环境变量：`FOXOS_VERSION`、`FOXOS_RELEASE_URL`、`FOXOS_ISO_NAME`、`FOXOS_SUMS_URL`、`FOXOS_ISO_SHA256`（要与 `SHA256SUMS` 一致，否则退出）、`FOXOS_ISO_URL`（直接指定 ISO，跳过 Release，用 `FOXOS_ISO_SHA256` 校验）、`FOXOS_PREFER_FULL=1`（有整张 ISO 时优先下整张）。

Both images use [`docker/os/fetch-iso.sh`](../docker/os/fetch-iso.sh). It downloads the release `SHA256SUMS` and reuses an existing ISO if it matches. Otherwise it reads the list of `FoxOS-<version>-amd64.iso.part-NN` parts from `SHA256SUMS` (0.3.4 has `part-00` to `part-02`), so a different part count needs no change. Each part is downloaded and checked, appended to the ISO, then deleted, so peak disk use is about the ISO plus one part. A part that fails its checksum is retried once. The assembled ISO is checked against `SHA256SUMS` again. If the release has no parts, the single ISO is downloaded and checked.

## 镜像标签 / Tags

| 标签 / Tag | 作用 / Purpose | 大小 / Size（本地构建，2026-11-12） |
|---|---|---|
| `gatesenman/foxos:0.3.4-os-preview`<br>`ghcr.io/gatesenman/foxos:0.3.4-os-preview` | 试用：在有 KVM 的 Linux 宿主上，用 **cloud-hypervisor** 引导 **真正的** FoxOS ISO，把来宾桌面以 VNC / 网页暴露出来。镜像里不带 ISO，首次运行时下载。<br>Trial: boots the real ISO with cloud-hypervisor on the host's KVM and exposes the guest desktop over VNC / noVNC. The ISO is downloaded on first run. | 388 MB 解压 / unpacked，约 123 MiB gzip |
| `gatesenman/foxos:0.3.4-os-preview-installer`<br>`ghcr.io/gatesenman/foxos:0.3.4-os-preview-installer` | 在线安装助手：只下载 ISO 并校验，不启动虚拟机。<br>Online installer helper: downloads and verifies the ISO only. | 84.7 MB 解压 / unpacked，约 31 MiB gzip |
| `…:os-preview` | 指向当前预览试用标签（推送成功后才会有） / Points at the current trial tag (only after a push) | |

## 试用（真 ISO，不是假桌面）/ Trial (real ISO, not a fake desktop)

容器里不画一个 Electron 或网页假装桌面。它用和狐狸OS 相同的 VMM（cloud-hypervisor，Apache-2.0 官方静态二进制）在宿主的 `/dev/kvm` 上引导 Release 里的 ISO。来宾 XFCE 会话在内核参数带 `foxos.vnc` 时启动 **x11vnc**；容器把 5900（VNC）和 6080（noVNC 网页）转到那台虚拟机。

The container does not paint a fake desktop. It boots the real release ISO with the same VMM FoxOS ships (cloud-hypervisor) on the host’s `/dev/kvm`. When the guest is started with `foxos.vnc`, the XFCE session launches **x11vnc**; the container forwards port 5900 (VNC) and 6080 (noVNC web).

```bash
# 需要 Linux 宿主，并且 CPU 支持虚拟化（VMX/SVM），把 KVM 传进容器
docker pull gatesenman/foxos:0.3.4-os-preview      # 或 ghcr.io/gatesenman/foxos:0.3.4-os-preview

docker run --rm -it \
  --device /dev/kvm \
  --device /dev/net/tun \
  --cap-add NET_ADMIN \
  -p 5900:5900 -p 6080:6080 \
  -v foxos-iso:/var/lib/foxos \
  gatesenman/foxos:0.3.4-os-preview
```

ISO 按上面的方式自动下载并校验，放在卷 `foxos-iso` 里，下次启动不重下。浏览器打开 `http://127.0.0.1:6080/vnc.html`，或用 VNC 客户端连 `127.0.0.1:5900`。来宾要到图形会话起来之后桌面才会出现，请多等一会儿。已经有 ISO 时可以挂进去并用 `-e FOXOS_ISO_PATH=/var/lib/foxos/FoxOS-0.3.4-amd64.iso` 指定（加 `FOXOS_ISO_SHA256` 会校验）。

The ISO is downloaded and verified into the `foxos-iso` volume and reused next time. Then open `http://127.0.0.1:6080/vnc.html` or a VNC client at `127.0.0.1:5900`, and wait until the guest graphical session is up. To use an ISO you already have, mount it and set `FOXOS_ISO_PATH` (plus `FOXOS_ISO_SHA256` to verify it).

容器内的 `/proc/sys` 默认只读，入口脚本打不开 IPv4 转发时会打印一条警告；端口转发不通时请加 `--sysctl net.ipv4.ip_forward=1`。

`/proc/sys` is read-only in a default container, so the entrypoint prints a warning when it cannot enable IPv4 forwarding. If the ports do not reach the guest, add `--sysctl net.ipv4.ip_forward=1`.

### 没有 KVM 时 / When there is no KVM

如果看不到 `/dev/kvm`，入口脚本会说明原因并退出，**不会**在容器里塞一个假桌面。请改用 GitHub Release 的 ISO 在真实电脑、已启用虚拟化的 Hyper-V、或本仓库的 `scripts/os/qemu-boot.sh`（QEMU **只用于开发测试**，不是产品依赖）启动。

If `/dev/kvm` is missing, the entrypoint exits with an explanation. It will **not** fake a desktop. Use the GitHub Release ISO on a real PC, on Hyper-V with virtualization enabled, or `scripts/os/qemu-boot.sh` on a dev machine (QEMU is a **test-only** tool, not a product dependency).

其它可选环境变量：`FOXOS_MEM`（默认 `4G`）、`FOXOS_CPUS`（默认 `2`）、`FOXOS_NOVNC=0` 可关掉网页端。

Other options: `FOXOS_MEM` (default `4G`), `FOXOS_CPUS` (default `2`), `FOXOS_NOVNC=0` to turn off the web client.

## 在线安装（只拉 ISO）/ Online install (ISO only)

```bash
docker pull gatesenman/foxos:0.3.4-os-preview-installer   # 或 ghcr.io/gatesenman/foxos:0.3.4-os-preview-installer

docker run --rm \
  -v "$PWD:/out" \
  gatesenman/foxos:0.3.4-os-preview-installer
```

当前目录会得到 `FoxOS-0.3.4-amd64.iso` 和 `SHA256SUMS`：脚本按 `SHA256SUMS` 下载三个分卷、逐个校验、拼接，再校验整张 ISO。然后把 ISO 写到 U 盘，或在 Hyper-V / 本机虚拟机里启动。安装步骤见 [os-test-guide.md](os-test-guide.md)。

The current directory receives `FoxOS-0.3.4-amd64.iso` and `SHA256SUMS`: the script downloads the three parts listed in `SHA256SUMS`, checks each, joins them and checks the whole ISO. Write it to USB or boot it in Hyper-V / a local VM. See [os-test-guide.md](os-test-guide.md).

## 本地构建 / Build locally

在仓库根目录（构建上下文只包含 `docker/os/`，见 `.dockerignore`）：

From the repo root (the build context only contains `docker/os/`; see `.dockerignore`):

```bash
V=0.3.4
docker build -f docker/os/Dockerfile --build-arg FOXOS_VERSION=$V \
  -t gatesenman/foxos:$V-os-preview -t ghcr.io/gatesenman/foxos:$V-os-preview .
docker build -f docker/os/Dockerfile.installer --build-arg FOXOS_VERSION=$V \
  -t gatesenman/foxos:$V-os-preview-installer -t ghcr.io/gatesenman/foxos:$V-os-preview-installer .
```

不要在未得到 Sarah 同意之前执行 `docker login` 或 `docker push`。

Do not run `docker login` or `docker push` until Sarah has agreed.

## CI 推送（默认关闭）/ CI push (off by default)

工作流是 [`.github/workflows/docker.yml`](../.github/workflows/docker.yml)，只能手动运行（`workflow_dispatch`）。输入：

| 输入 / Input | 默认 / Default | 说明 / Meaning |
|---|---|---|
| `version` | `0.3.4` | 传给 `FOXOS_VERSION`；会先检查 `v<版本>-os-preview` 的 `SHA256SUMS` 存在 / Passed as `FOXOS_VERSION`; the release `SHA256SUMS` must exist |
| `push_dockerhub` | `false` | 推送到 `docker.io/gatesenman/foxos`；需要仓库 Secrets `DOCKERHUB_USERNAME`、`DOCKERHUB_TOKEN`，缺了就失败，不会推送 / Needs the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets, fails without them |
| `push_ghcr` | `false` | 推送到 `ghcr.io/gatesenman/foxos`；默认用本次运行的 `GITHUB_TOKEN`（工作流已声明 `packages: write`），也可以配 `GHCR_USERNAME` / `GHCR_TOKEN`（经典 PAT，带 `write:packages`）/ Uses the run's `GITHUB_TOKEN` (`packages: write`), or the `GHCR_USERNAME` / `GHCR_TOKEN` secrets (a classic PAT with `write:packages`) |

两个开关都不勾时，工作流只构建并打印镜像大小，没有任何登录或推送步骤会运行。注意：细粒度个人令牌（`github_pat_…`）不能推 GHCR，GitHub 要求经典 PAT 的 `write:packages` 或 Actions 的 `GITHUB_TOKEN`。第一次推到 GHCR 后，包默认是私有的，需要在包设置里改成公开，`docker pull` 才不用登录。

With both switches off, the workflow only builds and prints the image sizes; no login or push step runs. Fine-grained personal tokens (`github_pat_…`) cannot push to GHCR; GitHub requires a classic PAT with `write:packages`, or the Actions `GITHUB_TOKEN`. After the first GHCR push the package is private by default; make it public in the package settings so `docker pull` works without logging in.

## Docker Official Images / Marketplace

把镜像推到 **Docker Hub 公开仓库** 之后，任何人都可以立刻 `docker pull`。这 **不是** Docker Official Images、Verified Publisher，也不是 Docker Marketplace / Partner 上架。那些是单独的申请流程，没有 Sarah 的明确指示，我们不会提交。

Publishing to a **public Docker Hub repository** makes `docker pull` work immediately. That is **not** the same as Docker Official Images, Verified Publisher, or a Docker Marketplace / partner listing. Those are separate applications. We will not file them without Sarah’s explicit word.

## 许可证

- 镜像里的 cloud-hypervisor：Apache-2.0，官方静态二进制 + `NOTICE`。
- ISO 本身的许可与 GitHub Release 相同（见 ISO 内文档）。镜像默认在运行时下载 ISO，不把 Windows 评估版或其它专有安装盘打进镜像。
