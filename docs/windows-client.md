# 狐狸OS 电脑客户端（Windows / macOS / 普通 Linux）/ The FoxOS computer client

[中文](#中文) · [English](#english)

## 中文

从 0.3.3 起，装在 Windows（以及 macOS、普通 Linux）上的 FoxOS 只是「狐狸OS 电脑」的**客户端**：它显示那台电脑的画面和智能体聊天，所有动作都交给那台电脑执行。**不会在你自己的电脑上装软件、开 Word、跑终端或改文件。**

「狐狸OS 电脑」可以是：

| 方式 | 说明 |
|---|---|
| 本机上的狐狸OS 虚拟机 | 在「狐狸OS 电脑」窗口里点「新建虚拟机」：选一个狐狸OS 预设（`foxos-debian-12`、`foxos-ubuntu-24.04` 镜像，或狐狸OS ISO）和本机可用的虚拟化（Hyper-V、WSL2、QEMU、VirtualBox，按 `foxos env providers` 的检测结果列出），等于运行 `foxos env install <预设> <名字> --provider <虚拟化> --start`。之后可以在窗口里启动 / 停止。 |
| 远程狐狸OS（SSH） | 局域网或云上的狐狸OS：填主机、端口、用户和 SSH 私钥。只用密钥（BatchMode），不保存密码；第一次连接记下主机指纹，之后指纹变了会拒绝连接。 |
| 配对的狐狸OS | 在那台狐狸OS 上运行 `foxos machine host code` 得到配对码，在这里点「配对新的狐狸OS」。命令走配对的 HTTPS 通道（证书指纹固定、按客户端 × 智能体授权）；画面和终端还需要填 SSH 地址。 |

### 什么在哪里执行

| 动作 | 执行位置 |
|---|---|
| 应用中心安装 Everything 应用 | 狐狸OS 电脑的终端里运行 `foxos everything install …` |
| 应用中心安装 LibreOffice / git / Node.js / Python | 狐狸OS 电脑的终端里 `sudo apt-get install …`（sudo 密码在终端里输入） |
| 打开 Word / 表格 / 演示 | 狐狸OS 电脑桌面上的 LibreOffice Writer / Calc / Impress（`foxos desktop launch -- libreoffice --writer`），在「狐狸OS 电脑」窗口里看到 |
| 终端 | 狐狸OS 电脑的 shell（SSH） |
| 文件、表格、文档、演示等所有 foxos 命令 | 狐狸OS 电脑里的 foxos（工作空间在那台电脑上） |
| ACP 智能体（安装、登录、会话） | 狐狸OS 电脑里：`foxos acp agent install`，会话用 `foxos acp stdio <智能体>` 经 SSH 连接，MCP 是那台电脑里的 `foxos mcp` |
| 智能体聊天 | 狐狸OS 电脑里的 `foxos bot serve`，经 SSH 端口转发到本机 127.0.0.1 |
| Everything 应用窗口 | 在狐狸OS 电脑的桌面上打开（`foxos <应用> open`） |
| 新建 / 启动 / 停止虚拟机、配对 | 本机（这是在管理狐狸OS 电脑本身） |

### 本机执行

默认**关闭**。设置 → 「在哪台电脑上执行」里可以打开「允许在本机执行（每次确认）」；打开后，少数明确要在本机运行的动作（本机终端、在本机文件管理器里显示）每一次都会弹出原生确认框，默认按钮是「取消」。智能体、应用中心、打开 Word 即使打开这个开关也仍然只在狐狸OS 电脑里执行。

本机就是狐狸OS（`/etc/os-release` 里 `ID=foxos`，即 ISO / 虚拟机里的桌面）时，桌面程序照常在本机执行。开发时 `npm start` 也沿用本机执行；`FOXOS_CLIENT_MODE=1` 强制客户端模式，`FOXOS_HOST_EXECUTION=1` 强制本机模式。

### 画面

- 本机 QEMU 虚拟机：直接显示虚拟机控制台（QEMU `-vnc 127.0.0.1:N`，只听本机回环），开机过程也能看到。
- 远程狐狸OS 和其他虚拟化：经 SSH 在那台电脑里按需启动 `x11vnc -localhost`（只听那台电脑自己的 127.0.0.1，`-shared`），再用 `ssh -W` 转发。没有经过网络明文传输。
- 渲染用 [noVNC](https://github.com/novnc/noVNC) 1.7.0（MPL-2.0，打包在 `apps/desktop/src/renderer/vendor/novnc/`，许可证文件一起分发；重新生成：`node apps/desktop/scripts/vendor-novnc.mjs <装了 @novnc/novnc 与 esbuild 的目录>`）。

### 「foxos 不是内部或外部命令」（0.2.0）

0.2.0 在应用中心点「安装」时，在本机 PowerShell 里运行 `foxos everything install …`；根因是终端环境里同时有 `Path` 和 `PATH` 两个键，PowerShell 读到的是没改过的 `Path`，于是找不到 foxos（0.3.3 已修，见 US-86）。更根本的是这个安装本来就不该在本机执行：0.3.3 起它在狐狸OS 电脑里运行（US-87），本机 PowerShell 不参与。

### 测过什么、没测过什么

已在构建机上测过（US-87）：

- 单元 / 结构测试：执行模式判定、命令路由（`env` / `machine` 在本机，其余在来宾）、SSH 参数与引号、主进程把 Office / 终端 / 智能体 / Everything / 聊天都转给来宾、本机执行闸门（默认关、每次原生对话框）、QEMU 控制台参数、`foxos acp stdio`。
- 端到端（`apps/desktop/e2e/client.e2e.js`，Playwright 驱动真实 Electron，客户端模式）：来宾是真实的狐狸OS 根文件系统（ISO 里的 chroot：sshd + Xvfb :0 上的 XFCE + foxos，`scripts/e2e/foxos-guest-chroot.sh`）。2026-11-12 通过：本机执行默认关闭、终端在来宾里跑、Everything 应用在来宾里装/开、文件写在来宾里、电脑画面（noVNC）显示来宾桌面、应用中心在来宾里 `apt-get install libreoffice-writer` 后「打开 Word」在来宾桌面打开 LibreOffice Writer（`FOXOS_E2E_GUEST_APT=1`）。

**没有在真正的 Windows 上测过**：

- Windows 自带的 `ssh.exe`（OpenSSH 客户端）与私钥文件权限（OpenSSH 要求私钥只有当前用户可读）。
- 在 Windows 上用 Hyper-V / WSL2 / VirtualBox 新建与启动狐狸OS 虚拟机（`foxos env install` 的这些后端在本仓库的 Linux 构建机上无法运行）；Hyper-V 虚拟机没有 QEMU 那样的本机 VNC 控制台，画面依赖来宾里的 x11vnc + SSH。
- noVNC 画面在 Windows 版 Electron 里的显示与键盘映射（输入法、Win 键）。
- NSIS 安装程序写用户 PATH 的宏、MSI（仍未构建）。
- arm64 Windows 上的全部流程。

## English

Since 0.3.3 the FoxOS app on Windows (and on macOS and plain Linux) is a **client** of a "FoxOS computer". It shows that computer's screen and the agent chat, and every action runs on that computer. **It never installs software, opens Word, runs a terminal or touches files on your own PC.**

The FoxOS computer can be:

| Option | What it does |
|---|---|
| A FoxOS VM on this PC | In the "FoxOS computer" window, click "Create VM". Pick a FoxOS preset (the `foxos-debian-12` or `foxos-ubuntu-24.04` image, or the FoxOS ISO) and a virtualization backend detected by `foxos env providers` (Hyper-V, WSL2, QEMU, VirtualBox). This runs `foxos env install <preset> <name> --provider <p> --start`. You can start and stop the VM from the window. |
| A remote FoxOS over SSH | Enter host, port, user and SSH private key. Key-only (BatchMode), no passwords stored. The host key is recorded on first connect and enforced afterwards. |
| A paired FoxOS | Run `foxos machine host code` on that FoxOS, then click "Pair a new FoxOS" here. Commands use the paired HTTPS channel (pinned certificate, per client × agent grants). The screen and terminal also need its SSH address. |

### What runs where

| Action | Runs on |
|---|---|
| App center: install Everything apps | `foxos everything install …` in a FoxOS-computer terminal |
| App center: install LibreOffice / git / Node.js / Python | `sudo apt-get install …` in a FoxOS-computer terminal (type the sudo password there) |
| Open Word / Calc / Impress | LibreOffice on the FoxOS computer's desktop (`foxos desktop launch -- libreoffice --writer`), visible in the FoxOS computer window |
| Terminal | A shell on the FoxOS computer (SSH) |
| Files, sheets, docs, slides — every foxos command | foxos on the FoxOS computer (the workspace lives there) |
| ACP agents (install, login, sessions) | On the FoxOS computer: `foxos acp agent install`; sessions use `foxos acp stdio <agent>` over SSH with that computer's `foxos mcp` |
| Agent chat | `foxos bot serve` on the FoxOS computer, forwarded over SSH to 127.0.0.1 here |
| Everything app windows | Opened on the FoxOS computer's desktop (`foxos <app> open`) |
| Create / start / stop the VM, pairing | This PC (it manages the FoxOS computer itself) |

### Running on this PC

This is **off** by default. You can turn on "Allow running on this PC (confirm every time)" under Settings → "Where actions run". Even then, the few actions that explicitly target this PC (a local terminal, "show in this PC's file manager") each show a native confirmation dialog whose default button is Cancel. Agents, the app center and Open Word always run on the FoxOS computer, whatever this setting says.

The app keeps running actions locally when it is itself running on FoxOS (`ID=foxos` in `/etc/os-release`, i.e. the desktop inside the ISO or a VM), and in development (`npm start`). Set `FOXOS_CLIENT_MODE=1` to force client mode, or `FOXOS_HOST_EXECUTION=1` to force local mode.

### Screen

- **Local QEMU VMs:** the window shows the VM console directly (QEMU `-vnc 127.0.0.1:N`, loopback only), so you can watch the VM boot.
- **Remote FoxOS and other backends:** the app starts `x11vnc -localhost` on demand over SSH. It listens only on that computer's own 127.0.0.1 and is `-shared`, and the stream is forwarded with `ssh -W`, so nothing crosses the network unencrypted.
- **Rendering:** [noVNC](https://github.com/novnc/noVNC) 1.7.0 (MPL-2.0) is vendored in `apps/desktop/src/renderer/vendor/novnc/` together with its license files. To regenerate it, run `node apps/desktop/scripts/vendor-novnc.mjs <dir with @novnc/novnc and esbuild installed>`.

### "foxos is not recognized" (0.2.0)

In 0.2.0, clicking Install in the app center ran `foxos everything install …` in a local PowerShell.

- **Immediate cause:** the terminal environment had both a `Path` and a `PATH` key, and PowerShell read the unmodified `Path`. This is fixed in 0.3.3 (US-86).
- **Underlying problem:** that install should never have run on the PC at all. Since 0.3.3 it runs on the FoxOS computer (US-87), and the local PowerShell is not involved.

### Tested vs. untested

**Tested on the build machine (US-87):**

- **Unit and structure tests:**
  - execution-mode detection;
  - command routing (`env` / `machine` run locally, everything else on the guest);
  - SSH arguments and quoting;
  - the main process forwarding Office, terminals, agents, Everything and chat to the guest;
  - the host-execution gate (off by default, one native dialog per action);
  - the QEMU console flags;
  - `foxos acp stdio`.
- **End to end** (`apps/desktop/e2e/client.e2e.js`, Playwright driving the real Electron app in client mode):
  - The guest is a real FoxOS root filesystem: the ISO chroot with sshd, XFCE on Xvfb :0, and foxos (`scripts/e2e/foxos-guest-chroot.sh`).
  - Passed on 2026-11-12. Covered: host execution off by default, terminals running in the guest, Everything apps installed and opened in the guest, files written in the guest, and the computer view (noVNC) showing the guest desktop. With `FOXOS_E2E_GUEST_APT=1`, the app center ran `apt-get install libreoffice-writer` in the guest, and "Open Word" then opened LibreOffice Writer on the guest desktop.

**Not tested on real Windows:**

- Windows' built-in `ssh.exe` (OpenSSH client) and its private-key permission rules (OpenSSH requires the key file to be readable only by the current user).
- Creating and starting FoxOS VMs with Hyper-V, WSL2 or VirtualBox on Windows. These `foxos env install` backends cannot run on this Linux build machine. Hyper-V VMs also have no local VNC console like QEMU's, so the screen relies on x11vnc in the guest plus SSH.
- The noVNC view in Windows Electron: rendering and keyboard mapping (IME, the Windows key).
- The NSIS macro that writes the user PATH. The MSI is still not built.
- Anything on Windows arm64.
