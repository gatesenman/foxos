# Windows 实机测试清单（v0.3.3-windows-preview）

给 Sarah 在真实 Windows 电脑上验收用。0.3.3 起，Windows 上的狐狸OS 是**狐狸OS 电脑的客户端**：
智能体、应用中心、「打开 Word」、终端、文件都在狐狸OS 虚拟机（来宾）里执行，**不在 Windows 本机执行**；
本机执行默认关闭。安装包在 Linux 上用 electron-builder + wine 交叉编译，客户端在 Linux 上对真实狐狸OS 来宾做过端到端测试，
但**没有在真实 Windows 上运行过**。

每一项记录：通过 / 失败 / 截图。失败时附上 `%APPDATA%\FoxOS\logs`（若存在）和窗口里的错误原文。

建议环境：Windows 11 23H2+（或 Windows 10 22H2），x64，专业版（需要 Hyper-V；家庭版用 VirtualBox）。有 arm64 Windows 设备的话，第 1 节换成 arm64 安装包再测一遍。

## 0. 准备

- [ ] 记录 Windows 版本（`winver`）、版本类型、CPU 架构、CPU 虚拟化是否开启（任务管理器 → 性能 → CPU → 虚拟化）
- [ ] PowerShell 运行 `ssh -V`，确认系统自带 OpenSSH 客户端（没有：设置 → 系统 → 可选功能 → 添加「OpenSSH 客户端」）
- [ ] 生成密钥（客户端用它登录狐狸OS 电脑）：`ssh-keygen -t ed25519`，一路回车。公钥是 `%USERPROFILE%\.ssh\id_ed25519.pub`
- [ ] 安装包没有签名：SmartScreen 提示「Windows 已保护你的电脑」时点「更多信息 → 仍要运行」，这是预期行为

## 1. 安装

任选一种（建议两种都试）：

```powershell
# 一行安装（安装程序）
irm https://github.com/gatesenman/foxos/releases/download/v0.3.3-windows-preview/install.ps1 | iex
# 便携版
$env:FOXOS_PORTABLE = '1'; irm https://github.com/gatesenman/foxos/releases/download/v0.3.3-windows-preview/install.ps1 | iex
```

或从 [发布页](https://github.com/gatesenman/foxos/releases/tag/v0.3.3-windows-preview) 手动下载 `FoxOS-Setup-0.3.3-x64.exe` / `FoxOS-0.3.3-win-x64.zip`（arm64 同名换成 `arm64`），
用 `Get-FileHash -Algorithm SHA256 <文件>` 和 `SHA256SUMS` 对照。

- [ ] 脚本打印 `SHA-256 OK`；开始菜单出现「狐狸OS」
- [ ] **新开**一个 PowerShell，运行 `foxos --version`，输出 `foxos 0.3.3`（0.2.0 的「foxos 不是内部或外部命令」不再出现）
- [ ] 截图①：`foxos --version` 的输出

## 2. 准备一台狐狸OS 电脑（来宾）

客户端需要**狐狸OS 0.3.3 或更新**的来宾（0.3.2 及更早的 ISO 没有 SSH，连不上）。先看 [系统预览发布页](https://github.com/gatesenman/foxos/releases?q=os-preview&expanded=true) 有没有 0.3.3 或更新的 ISO：

**A. 有 0.3.3+ ISO**：在 Hyper-V（专业版）或 VirtualBox 里新建虚拟机，内存 4 GB、磁盘 32 GB，挂 ISO 安装（[安装指南](os-test-guide.md)）。装好后在狐狸OS 终端：

```sh
foxos --version                     # 0.3.3 或更新
foxos ssh enable
foxos ssh keys add --key "<粘贴 id_ed25519.pub 的整行内容>"
ip -4 addr                          # 记下虚拟机的 IP
```

**B. 还没有 0.3.3 ISO**：用 Xubuntu 24.04 虚拟机代替（画面靠 x11vnc，需要 X11 会话；用 Ubuntu 的话登录时选「Ubuntu on Xorg」）。装好后在虚拟机终端：

```sh
sudo apt install -y openssh-server x11vnc pipx libreoffice-writer
pipx install "git+https://github.com/gatesenman/foxos#subdirectory=packages/core"
pipx ensurepath   # 然后关掉终端重开
foxos --version   # 0.3.3 或更新
mkdir -p ~/.ssh && echo "<粘贴 id_ed25519.pub 的整行内容>" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
ip -4 addr
```

- [ ] 记录用的是 A 还是 B、虚拟化（Hyper-V / VirtualBox）、来宾 `foxos --version`
- [ ] PowerShell 里 `ssh <用户>@<虚拟机 IP> foxos --version` 不要密码就能输出版本（先确认 SSH 本身通）

## 3. 首次运行与连接

- [ ] 双击启动，出现桌面（不是白屏 / 黑屏）；中文正常；「狐狸OS 电脑」窗口自动打开，显示「未连接」和连接页
- [ ] 连接页最上面有「需要一台狐狸OS 电脑」说明（需要的版本、下载 ISO、开 SSH、新建或远程）。**这一块是发布后加的，0.3.3 预览安装包里可能还没有，没有就记「无」**
- [ ] 截图②：首次运行的连接页
- [ ] 「远程狐狸OS（SSH）」填：地址 = 虚拟机 IP，端口 22，用户 = 来宾用户名（狐狸OS 是 `foxos`），私钥 = 点「选择」选 `%USERPROFILE%\.ssh\id_ed25519` → 「连接」
- [ ] 状态变成绿色「在线 · foxos 0.3.x」，几秒内窗口里出现**来宾的桌面画面**，能用鼠标点、键盘打字（试一下中文输入法、Windows 键）
- [ ] 截图③：「狐狸OS 电脑」窗口里显示来宾桌面

可选（专业版）：
- [ ] 「本机上的狐狸OS 虚拟机」→ 选预设和虚拟化 → 「新建虚拟机」：终端里能看到下载 / 创建过程，结束后自动连上。记录用的预设、虚拟化和结果（这一项在构建机上测不了）

## 4. 所有动作都在来宾里执行

- [ ] 工具栏右侧显示「本机执行：关」
- [ ] 打开「终端」：标题是「狐狸OS 电脑终端」；运行 `hostname`、`uname -a`、`cat /etc/os-release`，输出的是**来宾**（Linux）的信息，不是 Windows
- [ ] 截图④：终端里 `uname -a` 的输出

### 「打开 Word」在来宾里打开 Writer

- [ ] 应用中心找到 LibreOffice / Office，点「安装」：打开的是来宾终端，执行 `sudo apt-get install -y libreoffice-writer libreoffice-calc libreoffice-impress`（狐狸OS 免密；B 方案的 Ubuntu 可能要输一次密码）。完成后**Windows 本机没有装任何东西**（开始菜单 / 「应用」列表里没有 LibreOffice）
- [ ] 点「打开 Word」（开始菜单 / 桌面上的文档或 Writer 图标）：**来宾桌面画面里**出现「无标题 1 — LibreOffice Writer」窗口（第一次启动可能要 30–60 秒）；Windows 本机没有弹出任何 Word / Writer 窗口
- [ ] 在 Writer 里打几个字，保存到来宾的「文档」里；来宾终端 `ls ~/Documents`（或 `~/文档`）能看到文件
- [ ] 截图⑤：「狐狸OS 电脑」窗口里的 Writer

### 其他

- [ ] 应用中心 → Everything 装一个应用（如 chess）：安装在来宾终端里进行；打开后出现在来宾桌面
- [ ] 右侧聊天选一个已在来宾里安装的智能体 →「启动」→ 发「列出工作空间里的文件」：能回复，「活动」页有记录（来宾需要 0.3.3+；B 方案先在来宾里 `foxos acp agent install <智能体>`）
- [ ] 「人工接管」后智能体写操作被拒绝，「交还」后恢复

## 5. 本机执行默认关闭

- [ ] 设置 →「在哪台电脑上执行」：显示客户端模式，「允许在本机执行（每次确认）」是关的
- [ ] 不打开开关时，任何需要在本机执行的动作（例如「在本机文件管理器里显示文件」）提示「本机执行已关闭」，**不会**在 Windows 上执行
- [ ] 打开开关：先弹确认框；之后每一次本机动作都再弹一次原生确认框，点「取消」就不执行
- [ ] 测完把开关关回去
- [ ] 截图⑥：本机执行开关打开时弹出的确认框

## 6. 卸载

- [ ] 设置 → 应用 → 狐狸OS → 卸载，干净卸载；`foxos` 命令从 PATH 消失（新开 PowerShell 验证）

## 7. 回报

发回：

1. 每节的勾选结果，失败项的现象和错误原文；
2. 截图：①`foxos --version`、②首次运行连接页、③来宾桌面画面、④终端 `uname -a`、⑤来宾里的 Writer、⑥本机执行确认框；
3. 第 0 节和第 2 节的记录（Windows 版本 / 架构、虚拟化、来宾方案与版本）；
4. 失败时 `%APPDATA%\FoxOS\logs` 里的日志（若存在）。

结果会写回 `docs/test-report.md` 和 `docs/windows-client.md` 的「测过什么、没测过什么」。
