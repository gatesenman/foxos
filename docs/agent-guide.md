# 狐狸OS 智能体使用指南

> 本文件由 `python scripts/gen_cli_docs.py` 从 `foxos/agent_guide.py` 生成，内容与 `foxos agent-guide` 输出一致。

狐狸OS 的每个应用（内置应用、51 个 Everything 应用、环境）都同时提供 **CLI** 与 **MCP** 两种入口，两者由同一份命令定义生成，
走同一个内核：同样的参数校验、工作空间约束、审计日志、写锁与人工接管规则。人在界面上做的操作和智能体通过命令做的操作效果相同。

## 1. 命令形式

- CLI：`foxos <应用> <资源> <动词> [参数] --json`，例如 `foxos tasks add-task set "买牛奶" --submit --json`、`foxos env exec dev -- uname -a`
- MCP 工具名：`<应用>_<资源>_<动词>`（如 `tasks_add-task_set`）；命令 ID 为点分形式 `tasks.add-task.set`，`foxos mcp --tool-names dotted` 可直接用点分名
  （默认用下划线，因为部分客户端只接受 `[A-Za-z0-9_-]`）
- 能力目录：`foxos help --json`（全部应用与命令、参数 Schema、示例），`foxos tools --format mcp|openai`
- Everything 应用的操作清单：`foxos <应用> op list --json`，文档见 `docs/operations/<应用>.md`
- 输出：加 `--json` 时 stdout 只有一个 JSON 对象 `{"ok": true, "command": ..., "result": ...}` 或 `{"ok": false, "error": {"code", "message", "hint"}}`

## 2. 连接 MCP

stdio（推荐，本机智能体）：

```bash
# Claude Code
claude mcp add foxos -- foxos --workspace /path/to/workspace mcp
```

Codex（`~/.codex/config.toml`）：

```toml
[mcp_servers.foxos]
command = "foxos"
args = ["--workspace", "/path/to/workspace", "mcp"]
env = { FOXOS_AGENT = "codex" }
```

Gemini CLI（`~/.gemini/settings.json`）与通用 `mcp.json`（Cursor 等编辑器）：

```json
{
  "mcpServers": {
    "foxos": {
      "command": "foxos",
      "args": [
        "--workspace",
        "/path/to/workspace",
        "mcp"
      ],
      "env": {
        "FOXOS_AGENT": "my-agent"
      }
    }
  }
}
```

Streamable HTTP（远程或多客户端）：

```bash
FOXOS_MCP_TOKEN=<随机令牌> foxos --workspace /path/to/workspace mcp --http 127.0.0.1:8765
```

```json
{
  "mcpServers": {
    "foxos": {
      "type": "http",
      "url": "http://127.0.0.1:8765/mcp",
      "headers": {
        "Authorization": "Bearer <FOXOS_MCP_TOKEN>"
      }
    }
  }
}
```

ACP：在狐狸OS 桌面右侧面板启动的 ACP 智能体（Claude Code ACP、Codex ACP、Gemini CLI、OpenCode、Qwen Code、Goose 等）
会在 `session/new` 中**自动注入**狐狸OS 的 MCP 服务器（stdio，`FOXOS_AGENT` 设为智能体 ID），无需手动配置。

工具数量：默认 `--profile compact` 暴露内置应用的全部工具，以及 Everything 的元工具
`everything_list` / `everything_commands` / `everything_run`（用后两者调用任意 Everything 应用的任意命令）。
`--apps tasks,chess` 额外直接暴露这些应用的全部工具；`--profile full` 暴露全部工具（数千个，部分客户端会截断）。

## 3. 工作空间规则

- 所有路径相对于工作空间根目录；`..`、绝对路径、符号链接逃逸都会被拒绝（PERMISSION_DENIED）
- `.foxos/` 是保留目录（审计、锁、控制状态），不能通过命令读写
- Everything 应用的私有数据在 `AppData/<应用>/`（`kv.json` 为键值存储），用户文件直接在工作空间里
- 环境（`foxos env`）把工作空间挂载到环境内的 `/workspace`，可设为只读或不挂载

## 4. 写锁

- 写文件、驱动应用界面时内核自动加锁：`.foxos/locks/<sha1(路径)[:16]>.lock`，内容为 `{path, owner, pid, host, acquired_at}`
- 被占用时等待 `--lock-wait` 秒（默认 10），仍被占用返回 LOCKED（退出码 5），`error.details` 给出持有者
- 同一应用的界面同一时刻只允许一个调用者驱动（锁 `AppData/<应用>/.ui`）

## 5. 审计

- 每次调用（只读的自省命令除外）都写一行 JSON 到 `.foxos/audit.jsonl`：时间、智能体、接口（cli / mcp / desktop）、命令、参数、目标路径、结果、耗时
- 智能体身份：`--agent <名字>` 或环境变量 `FOXOS_AGENT`；MCP 默认记为 `mcp:<客户端名>`；人在桌面上的操作记为 `human:desktop` 或 `human:<应用>`
- 查看：`foxos audit tail -n 50 --json`；桌面右侧“活动”面板实时显示

## 6. 人工接管

- 人在桌面点“人工接管”或运行 `foxos control pause`：之后智能体的所有写操作返回 PAUSED（退出码 8），只读命令照常
- 恢复：`foxos control resume`；查看：`foxos control status --json`
- 收到 PAUSED 时应停止写操作、等待，不要换别的方式绕过

## 7. 退出码

| 退出码 | 错误码 | 含义 |
|---|---|---|
| 0 | OK | 成功 |
| 1 | ERROR | 其他错误 |
| 2 | USAGE | 参数错误 |
| 3 | NOT_FOUND | 文件、应用、环境、界面元素不存在 |
| 4 | PERMISSION_DENIED | 越出工作空间或无权限 |
| 5 | LOCKED | 目标被其他调用者锁定 |
| 6 | DEPENDENCY_MISSING | 缺少依赖（应用未安装、LibreOffice 未安装等） |
| 7 | CONFLICT | 文件已被修改（`--expect-mtime` 不符）、状态冲突 |
| 8 | PAUSED | 人工接管中 |

## 8. Everything 应用

- 安装：`foxos everything install tasks chess`（从上游源码在本机构建，固定提交，附许可证）；`foxos everything list --json`
- 语义操作：`foxos <应用> <资源> <动词>`，每个操作在应用的真实界面上执行（点击、输入、按键），界面实时更新；没有桌面窗口时自动启动无界面实例
- 通用界面工具：`ui snapshot`（可交互元素及 ref）、`ui click --ref e12`、`ui type`、`ui set`、`ui press mod+z`、`ui screenshot`、`ui text`
- 应用内部逻辑：`module list` / `module read` / `module call`（调用应用自己的 ES 模块导出，与界面使用同一代码）
- 重置：`foxos <应用> app reset`（清空本工作空间下该应用的数据）

## 9. 环境

`foxos env images|pull|create|run|list|info|start|stop|restart|exec|shell|clone|snapshot|restore|export|import|delete|mount|limits|stats|logs|action add|action run|desktop-attach|providers|doctor|catalog|install`，
MCP 工具 `env_*`。完整虚拟机用 `linux-kvm`（内核 KVM + cloud-hypervisor）。详见 docs/environments.md。

## 10. 真实桌面会话

在狐狸OS 的 XFCE 会话里，智能体对**真实窗口**使用 `foxos desktop …` 或 `foxos session …`（同一组动词，MCP 为 `desktop_*` / `session_*`）：
列出 / 聚焦 / 移动 / 关闭窗口，启动应用，键入、点击、截图，以及人工接管（`takeover` / `resume`，与 `foxos control pause` 同一状态）。
这些不是 Electron 里画的矩形。操作清单见 docs/operations/desktop.md。人能做的，智能体用同一套命令也能做，效果相同。
