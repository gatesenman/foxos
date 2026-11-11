# AGENTS.md — 在狐狸OS 里工作的智能体须知

狐狸OS 的所有能力都可以通过 `foxos` 命令或 MCP 工具使用；图形界面上能做的事，命令也能做，并且写入同一份审计日志。

## 发现能力

```bash
foxos help --json                # 所有应用、命令、参数、示例、退出码
foxos <应用> --help              # 某个应用的命令
foxos agent-guide                # 接入说明（Claude Code / Codex / Gemini CLI 的 MCP 配置片段）
foxos everything commands <应用> --json   # Everything 应用的语义命令（从界面实际遍历得到）
```

参考：[docs/agent-guide.md](docs/agent-guide.md) · [docs/cli-reference.md](docs/cli-reference.md) · [docs/mcp-reference.md](docs/mcp-reference.md)

## 约定

- 语法：`foxos <应用> <资源> <动作> [参数] --json`；MCP 工具名把空格换成下划线：`<应用>_<资源>_<动作>`
- 加 `--json` 得到 `{"ok", "command", "result" | "error": {"code", "message", "hint"}}`
- 退出码：0 OK · 1 ERROR · 2 USAGE · 3 NOT_FOUND · 4 PERMISSION_DENIED · 5 LOCKED · 6 DEPENDENCY_MISSING · 7 CONFLICT · 8 PAUSED
- 用 `--agent <名字>`（或环境变量 `FOXOS_AGENT`）声明身份，审计日志按身份记录

## 规则

1. **只在工作空间内操作**。路径相对于工作空间；`../`、越界绝对路径、符号链接逃逸和 `.foxos/` 会被拒绝（PERMISSION_DENIED）。
2. **遇到 PAUSED（退出码 8）就停下**：人已接管，等待恢复，不要重试绕过。
3. **遇到 LOCKED（退出码 5）**：别人正在写同一文件；用 `--lock-wait <秒>` 排队或稍后再试。
4. **改文件前先读**：`sheets read`、`docs read`、`slides read`、`files read` 都返回结构化内容。
5. **在环境里跑不受信任的东西**：`foxos env install alpine sandbox && foxos env start sandbox && foxos env exec sandbox -- <命令>`；工作空间挂载在 `/workspace`。
6. 不要直接编辑 `.foxos/` 下的文件（审计、锁、版本由内核维护）。

## MCP

```bash
foxos --workspace <目录> mcp                         # stdio（默认 full 工具集）
foxos --workspace <目录> mcp --profile compact       # 精简：通用工具 + everything_commands / everything_run
FOXOS_MCP_TOKEN=<令牌> foxos --workspace <目录> mcp --http 127.0.0.1:8765   # Streamable HTTP，POST /mcp，Bearer 令牌
```

工具的 `_meta` 里有 `foxos/id`、对应的 CLI、权限与示例；错误以 `isError: true` 加结构化内容返回。

## 智能体（bot）、多机与运行环境

- 智能体：`foxos bot profile|config|message|task|skill|memory|routine|approval|channel …`；你的身份是 `bot:<id>`（经 ACP 时 `bot:<id>/acp:<智能体>`）。只能在自己的 `scope` 里读写；委托用 `bot_task_delegate`（`{task, constraints, expecting}`，深度 ≤ 3，每回合 ≤ 5）。
- 技能：`foxos bot skill list/show`；需要时先读 SKILL.md 再按步骤做（pstack 随系统分发）。
- 连接器：`foxos connector tools <连接器>`、`connector tool call`；只有智能体设置里启用的连接器能用，写操作要人批准。
- 另一台狐狸OS：`--machine <名字>`（MCP 工具参数 `machine`）。被控端默认拒绝，返回 PERMISSION_DENIED 时不要换身份重试，请人去被控端授权（`foxos machine host grant`）。
- 运行环境：`foxos runtime doctor`；系统 Python 遵循 PEP 668，装包用 `uv`/`venv`/`pipx`。说明见 [docs/agent-chat-design.md](docs/agent-chat-design.md)、[docs/agent-runtime.md](docs/agent-runtime.md)。

## 给本仓库的贡献者

- 代码：内核 `packages/core`（Python），桌面 `apps/desktop`（Electron）；命令只在注册表里定义一次，文档由 `scripts/gen_cli_docs.py` 生成（`--check` 检查漂移）
- 测试：`npm run test:all`（见 [docs/test-report.md](docs/test-report.md)）；不使用模拟
- 提交前运行 `python scripts/gen_cli_docs.py --check`
