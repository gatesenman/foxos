# Windows 实机测试清单（v0.2.0-windows-preview）

这份清单给在真实 Windows 电脑上验收狐狸OS 的人使用。安装包在 Linux 上交叉编译（electron-builder + wine），
内核在 wine 里做过冒烟测试，但**没有在真实 Windows 硬件上运行过**。每一项请记录：通过 / 失败 / 现象截图，
失败时附上 `%APPDATA%\FoxOS\logs`（若存在）与工作空间里 `.foxos\audit.jsonl` 的最后几行。

测试环境建议：Windows 10 22H2 或 Windows 11 23H2+，x64，专业版（家庭版可测除 Windows Sandbox / Hyper-V 以外的全部项目）。

## 0. 准备

- [ ] 记录：Windows 版本（`winver`）、版本类型（家庭版 / 专业版…）、是否已装 WSL（`wsl --status`）、CPU 虚拟化是否开启（任务管理器 → 性能 → CPU → 虚拟化）
- [ ] 安装包未签名：SmartScreen 会提示“Windows 已保护你的电脑”，点“更多信息 → 仍要运行”。这是预期行为，记录即可

## 1. 安装

任选一种方式（建议两种都测）：

**A. 在线安装脚本**（管理员不是必须）

```powershell
$env:GITHUB_TOKEN = '<能读取 gatesenman/foxos 的令牌>'   # 仓库私有；公开后可省略
powershell -ExecutionPolicy Bypass -File install.ps1          # 安装程序
powershell -ExecutionPolicy Bypass -File install.ps1 -Portable  # 便携版
```

- [ ] 脚本打印“SHA-256 校验通过”
- [ ] 安装程序可选择安装目录，完成后开始菜单出现“狐狸OS”
- [ ] 便携版解压到 `%LOCALAPPDATA%\FoxOS-Portable`，开始菜单出现“狐狸OS（便携版）”

**B. 手动下载**：从 Release 页下载 `FoxOS-Setup-0.2.0-x64.exe` 或 `FoxOS-0.2.0-win-x64.zip`，
用 `Get-FileHash -Algorithm SHA256 <文件>` 与 `SHA256SUMS` 对照。

- [ ] 卸载：设置 → 应用 → 狐狸OS → 卸载，能干净卸载（工作空间 `文档\FoxOS` 之类的用户数据保留）

## 2. 首次运行

- [ ] 双击启动，出现桌面（不是白屏 / 黑屏）；任务栏图标是狐狸图标
- [ ] 首次运行弹出安装向导，能选择工作空间目录（默认在用户目录下）
- [ ] 向导“组件”页：Python 显示“已就绪”（安装包自带 Python 3.12 与办公库，**不需要**另装 Python）
- [ ] 界面中文显示正常，没有方块字；图标都是线性图标（没有 emoji）

## 3. 终端

- [ ] 打开“终端”，默认是 PowerShell，可以输入、Tab 补全、中文显示正常、窗口缩放后排版正确
- [ ] 在终端运行 `foxos --version`，输出 `0.2.0`
- [ ] `foxos files list --json`、`foxos sheets create 测试.xlsx`、`foxos docs create 测试.docx` 成功，文件管理器里实时出现这两个文件
- [ ] `foxos agent-guide` 输出接入说明

## 4. LibreOffice（在线组件）

- [ ] 向导里 LibreOffice 点“安装”：有 winget 时走 winget；没有时脚本从 download.documentfoundation.org 下载最新 MSI，打印“SHA-256 校验通过”，弹出 UAC 后安装
- [ ] 安装完成后向导显示“已安装”与版本号
- [ ] 在文件管理器里双击 `测试.docx`，用 LibreOffice Writer 打开；任务栏出现对应窗口

## 5. Everything 应用（任选 3 个）

建议：表格（spreadsheet）、任务（tasks）、国际象棋（chess）。

- [ ] 应用中心 → Everything → 对应分组“安装”：在内置终端里从上游源码构建（需要 Node.js 与 git，向导可一键安装）
- [ ] 打开应用，界面正常，能新建 / 保存到工作空间
- [ ] 终端里 `foxos everything commands spreadsheet --json` 列出语义命令；执行其中一条后 GUI 里能看到变化

## 6. ACP 智能体

- [ ] 应用中心 → 智能体：安装一个 npm 型 ACP 智能体（如 Claude Code ACP 或 Gemini CLI），安装过程在内置终端可见
- [ ] 右侧面板选择该智能体 → 启动 → 发送“列出工作空间里的文件”，智能体通过 foxos 命令 / MCP 完成，“活动”页出现审计记录
- [ ] 点“人工接管”后智能体的写操作被拒绝（PAUSED），点“交还”后恢复

## 7. 环境 → 安装系统（WSL2 一键安装 Ubuntu）

1. [ ] 打开“环境”→ 左下角“安装系统”。顶部显示本机检查结果：`wsl2`、`windows-sandbox`、`hyperv` 各一行
2. [ ] 如果 WSL 未启用：`wsl2` 一行显示“启用 WSL”按钮 → 点击 → UAC 确认 → 完成后提示重启 → 重启电脑 → 回到这里，`wsl2` 显示“可用”
   - BIOS 未开启虚拟化时应显示“在电脑固件设置里开启虚拟化”的说明
3. [ ] 在 Linux 分区点 **Ubuntu 24.04 LTS → 安装**，环境名保持默认 `ubuntu-24.04`，开始安装
4. [ ] 进度条显示下载字节数；完成后左侧列表出现该环境
5. [ ] 选中环境 → “终端”，进入 Ubuntu 的 shell；运行 `cat /etc/os-release` 显示 Ubuntu 24.04；`ls /mnt/c` 能看到 C 盘
6. [ ] PowerShell 里 `wsl -l -v` 显示 `foxos-ubuntu-24-04`（或你取的名字）为 Version 2
7. [ ] 狐狸OS 终端：`foxos env exec ubuntu-24-04 --json -- uname -a` 返回 Linux 内核信息（工作目录映射为工作空间的 `/mnt/<盘符>/…`）
8. [ ] “删除”该环境后，`wsl -l -v` 里对应发行版消失

可选：
- [ ] 安装 Oracle Linux 9.5（应用商店包，走 `wsl --install -d OracleLinux_9_5`）
- [ ] 安装 “Oracle Linux 9（LXC 构建）”（.tar.xz 自动转换后导入）
- [ ] 专业版：Windows Sandbox → 安装 → 打开一次性 Windows 桌面，桌面上 `workspace` 文件夹就是狐狸OS 工作空间
- [ ] 专业版：Hyper-V → “从 ISO 安装”，选一个 ISO，创建虚拟机并打开控制台；Hyper-V 管理器里能看到 `foxos-<名>`
- [ ] macOS 一栏显示为禁用，并说明原因

命令行等价操作（同样需要测）：

```powershell
foxos env doctor --json
foxos env catalog --available
foxos env install wsl-ubuntu-24.04 ubuntu --dry-run --json   # 查看将执行的每条命令
foxos env install wsl-ubuntu-24.04 ubuntu
foxos env progress ubuntu
```

## 8. 结果回报

把每节的勾选情况、失败项的现象与截图、`foxos env doctor --json` 的输出发回即可。
实机结果会写回 `packages/core/tests/fixtures/windows/`（真实命令输出）与 `docs/test-report.md`。
