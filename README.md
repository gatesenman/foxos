<p align="center"><img src="assets/icons/icon-256.png" width="128" height="128" alt="狐狸OS 图标"></p>

<h1 align="center">狐狸OS（FoxOS）</h1>

<p align="center">给 AI 智能体使用的桌面操作系统平台：虚拟桌面、应用、文件空间、命令系统和多智能体协作。</p>

## 简介

狐狸OS 是运行在 Windows、macOS 和 Linux 之上的桌面程序。它自带虚拟桌面、应用管理和任务运行时，不依赖 Docker 或虚拟机。多个智能体通过统一的 `foxos` 命令、结构化工具接口（MCP）和图形界面协作完成办公、设计、研发和业务任务；人可以随时查看、审核和接管。

**核心原则：内置的都是智能体本来就非常熟悉的软件和格式**：标准 `.xlsx` / `.csv` / `.pdf`、Excel 公式、经典 CLI 约定（子命令、`--help`、`--json`、稳定退出码）、终端、git、Python、Node。命令设计贴近模型熟知的习惯，不发明新概念。

![狐狸OS 桌面（阶段 0 原型）](docs/screenshots/desktop.png)

*截图：演示工作空间中，数据、文档、审核等智能体通过 `foxos` 命令协作处理 `reports/sales.xlsx`；右侧是从审计日志实时读取的智能体状态和操作记录（包括被写锁拒绝、越界访问被拒绝的记录）。*

## 当前状态：阶段 0 原型

阶段 0 的目标是验证最关键的技术假设：**智能体能通过统一命令创建文件、完成修改、重新打开并验证结果，且每一步都可追溯。** 这一点已经通过自动化测试证明（见[测试](#测试)）。

### 已实现

- **统一命令内核**（`packages/core`，Python）：CLI、MCP 工具服务器、桌面外壳调用同一个 `kernel.invoke()`；命令只定义一次，参数、帮助、能力目录、JSON Schema 都从定义生成。
- **工作空间约束**：所有路径限定在工作空间内，拒绝 `../`、越界绝对路径、符号链接逃逸和保留目录 `.foxos/`。
- **审计日志**：每次调用（成功、失败、被拒绝）写入 `.foxos/audit.jsonl`，记录智能体、接口、命令、目标文件、状态和耗时。
- **同一文件单写者锁**：并发写同一文件时返回 `LOCKED`（退出码 5），或用 `--lock-wait` 排队；读可并行；崩溃遗留的锁自动回收。
- **原子保存与版本记录**：覆盖前自动保留上一版到 `.foxos/versions/`。
- **人工接管**：`foxos control pause/resume`，暂停期间智能体写操作返回 `PAUSED`（退出码 8），桌面左侧“人工接管”按钮可一键切换。
- **表格应用 `foxos sheets`**（基于 openpyxl，MIT）：`create`、`read`（可用 LibreOffice 求值公式）、`write`（值与公式）、`chart create`（原生 Excel 柱状 / 折线 / 饼图）、`chart list`、`export`（csv / pdf / ods / xlsx）。
- **能力目录**：`foxos help --json`（命令、参数、示例、限制、退出码约定）、`foxos <app> --help`、[命令参考](docs/cli-reference.md)。
- **工具接口**：`foxos mcp`（stdio MCP 服务器）、`foxos tools --format mcp|openai` 导出 JSON Schema。
- **系统命令**：`workspace info`、`files list`、`audit tail`、`tasks create/list`。
- **桌面外壳**（`apps/desktop`，Electron）：顶栏、左侧导航、中间虚拟桌面（可拖动窗口：文件中心、表格预览与图表、命令终端、任务中心、应用中心、智能体中心、活动记录）、右侧智能体团队与操作记录（实时读取审计日志）、底部任务输入栏（输入 `foxos ...` 直接执行命令，其他文字加入任务队列）。
- **打包配置**：Linux（dir / AppImage）、Windows（NSIS 安装包，使用 `assets/icon.ico`）、macOS（dmg）。

### 未实现（后续阶段）

- 接入大模型：任务目前只入队记录，**不会自动拆解和执行**；主管 / 数据 / 文档 / 演示 / 审核等角色目前只是通过 `--agent` 声明的身份。
- 文档（docx）和演示（pptx）应用；Everything 应用的界面集成。
- 智能体中心的角色配置、模型与预算设置；任务依赖与失败恢复。
- 身份认证（`--agent` 由调用方自行声明）、网络权限、凭据管理、资源限制。
- 操作系统级隔离：工作空间约束和写锁是应用层约束，详见[架构说明 · 安全边界](docs/architecture.md#7-安全边界必须如实理解)。
- 系统在线安装器、ACP 智能体一键安装（见产品规划第十、十一节）。
- 把 Python 运行时打包进安装包（目前要求宿主已安装 Python 3.10+ 和 openpyxl）。
- Windows / macOS 实机验证：Windows 打包配置已写好但**未在 Windows 上构建和运行**；macOS 未测试。

## 安装

前置条件：Python 3.10+、Node.js 20+（仅桌面需要）；可选 LibreOffice（公式求值、PDF / ODS 导出）。

```bash
git clone https://github.com/gatesenman/foxos.git
cd foxos

# 命令内核与 CLI
python3 -m venv .venv
source .venv/bin/activate            # Windows：.venv\Scripts\activate
pip install -e "packages/core[test]"
foxos --version
```

## 使用 CLI

```bash
export FOXOS_WORKSPACE=~/FoxOS/workspace   # 也可每次用 --workspace 指定
export FOXOS_AGENT=data-agent              # 调用者身份，写入审计日志

foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales
foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135 A4=Mar B4=150 'B5==SUM(B2:B4)'
foxos sheets chart create sales.xlsx --type bar --data B1:B4 --categories A2:A4 --title 月度销售额
foxos sheets read sales.xlsx --computed        # 用 LibreOffice 求值公式
foxos sheets export sales.xlsx sales.pdf
foxos audit tail                               # 谁在什么时候做了什么
```

- 单元格写法：`A1=Month`（文本）、`B2=120`（数字）、`B5==SUM(B2:B4)`（公式，以 `=` 开头）、`A4='007`（强制文本）、`A6=`（清空）；也可用 `--cells-json '{"B2": 120}'`。
- 每个命令都支持 `--json`；失败时返回稳定的错误码和退出码，例如越界路径返回 `PERMISSION_DENIED`（4），文件被锁返回 `LOCKED`（5）。
- 能力目录：`foxos help`、`foxos help --json`、`foxos sheets --help`、`foxos sheets chart create --help`。完整参考见 [docs/cli-reference.md](docs/cli-reference.md)。

### 作为 MCP 工具接入智能体

```json
{
  "mcpServers": {
    "foxos": {
      "command": "/path/to/foxos/.venv/bin/foxos",
      "args": ["mcp", "--workspace", "/path/to/workspace"],
      "env": { "FOXOS_AGENT": "data-agent" }
    }
  }
}
```

工具名为命令 ID 把 `.` 换成 `_`（如 `sheets_chart_create`）。`foxos tools --format openai` 可导出 OpenAI function 格式的定义。MCP 调用与 CLI 调用写入同一个审计日志（`interface` 字段区分）。

## 运行桌面

```bash
cd apps/desktop
npm install
npm start                                      # 使用 $FOXOS_WORKSPACE 或 ~/FoxOS/workspace

# 用演示数据启动：先生成多智能体演示工作空间
python ../../scripts/seed_demo.py ../../demo-workspace
npm run start:demo
```

桌面会自动使用仓库下的 `.venv/bin/python`；也可以用 `FOXOS_PYTHON` 指定 Python 路径。Linux 无图形环境时可以用 `xvfb-run -a npm start -- --no-sandbox`。

打包：

```bash
npm run dist:linux          # Linux 目录版：dist/linux-unpacked/foxos-desktop（已验证）
npm run dist:linux:appimage # AppImage
npm run dist:win            # Windows NSIS 安装包（配置已写，未在 Windows 上验证）
```

## 测试

```bash
# 内核与 CLI：25 项测试，全部通过真实子进程调用 CLI / MCP
cd packages/core && pytest -q

# 桌面冒烟测试（Linux，需要 xvfb-run）：截图 + 界面交互自检（提交任务、运行命令、人工接管与恢复）
cd apps/desktop && npm run test:smoke
```

测试覆盖：

- **端到端**：CLI 创建 xlsx → 写入单元格与公式 → 生成柱状图和折线图 → 用 openpyxl 独立重新打开验证公式与图表 → CLI 读回 → 审计日志逐步核对（命令顺序、智能体、目标文件、读写方式）→ 版本记录核对。
- **公式求值与导出**：LibreOffice 求值 `SUM` / `MAX` / 除法结果正确，原文件不被改动；导出 csv（求值后的值）、pdf，重复导出返回 `CONFLICT`。
- **越界路径**：`../`、多级 `../`、越界绝对路径、符号链接逃逸、`.foxos/` 保留目录、导出到工作空间外，全部拒绝并记入审计。
- **并发写锁**：锁被占用时写入返回 `LOCKED` 且文件不变、读和写其他文件不受影响；`--lock-wait` 排队成功；8 个进程并发写同一文件不丢更新；崩溃进程遗留的锁被回收。
- **人工接管、能力目录、工具 Schema、MCP 服务器**（initialize / tools/list / tools/call、越界与参数错误、与 CLI 共用审计日志）。

## 文档

- [产品规划](docs/product-plan.md)
- [Everything 首批应用代码级评估](docs/everything-evaluation.md)
- [阶段 0 架构与技术选择](docs/architecture.md)（含依赖许可与安全边界）
- [foxos 命令参考](docs/cli-reference.md)

## 资源

- `assets/icon.png`（1024×1024）、`assets/icon.ico`（16–256 多尺寸）
- `assets/icons/icon-{16,24,32,48,64,128,256,512,1024}.png`
- `assets/icon.jpg`（原始图标）

## 许可

本仓库暂未选定许可证。阶段 0 的依赖均为 MIT / PSF / MPL-2.0（LibreOffice 仅作为外部程序调用），未使用任何 AGPL 代码；Everything 应用的许可情况见评估报告。
