# 阶段 0 原型：架构与技术选择

本文记录阶段 0 原型的实现方式、技术选择的理由、依赖许可和安全边界。产品目标见 [产品规划](product-plan.md)，Everything 应用评估见 [评估报告](everything-evaluation.md)。

## 1. 核心原则：只用智能体本来就熟悉的东西

狐狸OS 是智能体专用的系统。阶段 0 的每个选择都优先考虑“模型不用学就会用”：

| 方面 | 选择 | 为什么智能体熟悉 |
|---|---|---|
| 文件格式 | 标准 `.xlsx`（Office Open XML）、`.csv`、`.pdf`、`.jsonl` | 训练语料中大量出现；任何工具都能打开验证 |
| 单元格与公式 | A1 记法、Excel 英文函数名（`=SUM(B2:B13)`） | 与 Excel / LibreOffice / openpyxl 完全一致 |
| 命令行 | `foxos <app> <command> [参数]`、`--help`、`--json`、稳定退出码、错误写 stderr | 与 git、kubectl、gh 等经典 CLI 习惯一致 |
| 表格库 | openpyxl（Python） | 智能体处理 Excel 最常用的库之一 |
| 公式求值与导出 | LibreOffice 无头模式（`soffice --headless --convert-to`） | 经典的无头办公方案 |
| 审计日志 | JSON Lines | 可以直接 `tail -f`、`jq`、`grep` |
| 工具接口 | MCP（stdio JSON-RPC）+ JSON Schema，另可导出 OpenAI function 格式 | 主流智能体客户端都支持 |
| 运行环境 | 宿主系统的终端、git、Python、Node | 不引入新运行时，不依赖 Docker / 虚拟机 |

不发明新概念：路径就是工作空间里的相对路径，单元格就是 `B2`，图表类型就是 `bar` / `line` / `pie`。

## 2. 仓库结构

```text
packages/core/            统一命令内核与 foxos CLI（Python 包 foxos）
  foxos/kernel.py         命令注册、参数校验、路径约束、写锁、审计（唯一执行入口 invoke）
  foxos/workspace.py      工作空间目录约束
  foxos/locks.py          同一文件单写者锁
  foxos/audit.py          JSONL 审计日志
  foxos/cli.py            CLI（参数由命令定义生成）
  foxos/mcp_server.py     MCP stdio 服务器
  foxos/catalog.py        能力目录（help --json）与工具 Schema 导出
  foxos/office.py         LibreOffice 调用
  foxos/apps/sheets.py    表格应用
  foxos/apps/system.py    工作空间、文件、审计、任务、人工接管
  tests/                  pytest 测试（全部通过真实子进程调用 CLI / MCP）
apps/desktop/             Electron 桌面外壳
scripts/seed_demo.py      生成多智能体演示工作空间
scripts/gen_cli_docs.py   生成 docs/cli-reference.md
```

## 3. 统一命令内核

```text
   foxos CLI ──┐
 MCP 服务器 ───┼──► kernel.invoke(command_id, params, ctx)
   桌面外壳 ───┘        │
                        ├─ 参数校验（类型、必填、枚举；与 JSON Schema 同源）
                        ├─ 人工接管检查（暂停时拒绝智能体写操作）
                        ├─ 路径解析与工作空间约束（拒绝越界）
                        ├─ 写目标加单写者锁（按路径排序获取）
                        ├─ 执行应用 handler（原子保存 + 版本记录）
                        └─ 追加审计记录（成功 / 失败 / 拒绝）
```

- 每个命令只定义一次（`Command` + `Param`）。CLI 参数、`--help` 文本、`foxos help --json` 能力目录、MCP `tools/list`、OpenAI function 定义、`docs/cli-reference.md` 都从这份定义生成，不会出现“CLI 能做、工具接口不能做”。
- 桌面外壳不直接读写文件，也通过子进程调用 `python -m foxos ... --json`，与智能体走同一条路径，因此桌面上的操作同样进入审计日志。
- 输出约定：`--json` 时成功为 `{"ok": true, "command", "result"}`，失败为 `{"ok": false, "command", "error": {"code", "exit_code", "message", "hint", "details"}}`；人类可读模式下错误写到 stderr。

### 退出码

| 退出码 | code | 含义 |
|---|---|---|
| 0 | OK | 成功 |
| 1 | ERROR | 未分类错误 / 内部错误 |
| 2 | USAGE | 参数错误 |
| 3 | NOT_FOUND | 文件、工作表、命令不存在 |
| 4 | PERMISSION_DENIED | 路径越出工作空间、访问保留目录、非人类发起接管 |
| 5 | LOCKED | 目标文件正被其他写入者锁定 |
| 6 | DEPENDENCY_MISSING | 缺少 LibreOffice 等外部依赖 |
| 7 | CONFLICT | 目标已存在（可用 `--force`） |
| 8 | PAUSED | 人工接管中，智能体写操作被暂停 |

## 4. 工作空间、锁、版本与审计

- **工作空间**：`--workspace` / `$FOXOS_WORKSPACE` / 默认 `~/FoxOS/workspace`。相对路径相对于根目录解析；先 `realpath`（解析 `..` 和符号链接）再判断是否位于根目录内，因此 `../x`、绝对路径越界、符号链接逃逸都会被拒绝。`.foxos/` 是保留目录（审计、锁、版本、任务），命令不能直接访问。
- **单写者锁**：写入目标在 `.foxos/locks/` 下用 `O_CREAT|O_EXCL` 原子创建锁文件，记录持有者。被占用时立即返回 `LOCKED`，或用 `--lock-wait` 等待。读不加锁，可以并行。持有进程已退出（POSIX 上检测 pid）或锁超过 10 分钟会被回收。
- **原子保存与版本**：先写同目录临时文件再 `os.replace`；覆盖已有文件前把上一版复制到 `.foxos/versions/<相对路径>/<时间戳>-<智能体>.xlsx`，结果里返回 `previous_version`。
- **审计**：每次调用追加一行 JSON 到 `.foxos/audit.jsonl`，包含时间、智能体、任务、接口（cli / mcp）、命令、参数、目标文件及读写方式、状态（ok / error / denied）、错误码、耗时。只读自省命令 `audit tail`、`control status` 成功时不记录，避免界面轮询淹没真实操作。
- **人工接管**：`foxos control pause` 写入 `.foxos/paused`，之后非 `human` 身份的写操作返回 `PAUSED`；读不受影响；只有 `human` 身份能暂停 / 恢复。

## 5. 为什么桌面外壳选 Electron

评估报告第 7 节的结论是“Electron 风险最低；Tauri 在 macOS/Linux 的 WebKit 兼容性未验证”。阶段 0 选 Electron：

1. 三个平台使用同一个 Chromium，Everything 应用后续接入时的渲染行为与评估时一致。
2. 首发平台 Windows 的打包链（electron-builder + NSIS）成熟，图标直接用 `assets/icon.ico`。
3. 桌面只是外壳，业务都在 Python 内核里；以后如需换 Tauri 以减小体积，内核和 CLI 不受影响。

安全设置：`contextIsolation: true`、`nodeIntegration: false`、`sandbox: true`、严格 CSP；渲染进程只能通过 preload 暴露的 `foxos.run(args)`（参数数组，不经过 shell）调用内核。

## 6. 依赖与许可

| 依赖 | 用途 | 许可 | 方式 |
|---|---|---|---|
| Python 3.10+ | 内核运行时 | PSF | 宿主系统安装 |
| openpyxl 3.1 | 读写 xlsx、原生图表 | MIT | pip 依赖 |
| et-xmlfile | openpyxl 依赖 | MIT | pip 依赖 |
| LibreOffice | 公式求值、PDF / ODS 导出 | MPL-2.0 | 可选外部程序，以子进程调用，不随狐狸OS 分发 |
| Electron 45 | 桌面外壳 | MIT | npm 开发依赖，打包进安装包 |
| electron-builder 26 | 打包（Linux dir / AppImage、Windows NSIS） | MIT | npm 开发依赖 |
| pytest | 测试 | MIT | 开发依赖 |

**没有复制、vendor 或依赖任何 AGPL 代码。** Everything 的 Spreadsheet 和 Presentation 为 AGPL-3.0-only，本原型未使用；表格能力完全基于 openpyxl 重新实现。本仓库暂未选定许可证。

## 7. 安全边界（必须如实理解）

- 工作空间约束、写锁、人工接管都是**应用层约束**：只约束通过 foxos 内核（CLI / MCP / 桌面）发出的操作。智能体如果直接在宿主终端里运行任意程序，不受这些约束。这不是操作系统级沙箱，也不是恶意代码防护。
- 调用者身份（`--agent` / `FOXOS_AGENT` / MCP 客户端名）由调用方声明，阶段 0 未做认证；“只有 human 能接管”同样依赖这个声明。
- 锁是协作式的：遵守 foxos 内核的进程之间互斥；绕过内核直接写文件不会被阻止。
- 并发写入的正确性已在 Linux 上用 8 个并发进程测试；Windows / macOS 上的锁和路径行为（大小写、盘符、符号链接）尚未实测。
