# 狐狸OS MCP 工具参考

> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos mcp` 的 tools/list 同源，请勿手改。

## 连接与调用

- stdio：`foxos --workspace <目录> mcp`；Streamable HTTP：`foxos --workspace <目录> mcp --http 127.0.0.1:8765 --token <令牌>`（POST /mcp）
- `--profile compact`（默认）：内置应用全部工具 + Everything 元工具；`--apps a,b`：额外暴露这些应用的全部工具；`--profile full`：全部工具
- `--tool-names dotted`：工具名用点分命令 ID（如 `tasks.add-task.set`），默认用下划线（`tasks_add-task_set`）

## 返回格式（所有工具相同）

成功：`isError=false`，`structuredContent` 为 `{"ok": true, "command": "<命令 ID>", "result": {...}}`，`content[0].text` 为同一 JSON 文本。

失败：`isError=true`，`structuredContent` 为 `{"ok": false, "command": ..., "error": {"code": "LOCKED", "exit_code": 5, "message": ..., "hint": ..., "details": {...}}}`。

错误码：USAGE(2) NOT_FOUND(3) PERMISSION_DENIED(4) LOCKED(5) DEPENDENCY_MISSING(6) CONFLICT(7) PAUSED(8) ERROR(1)。

共 4432 个工具。

## acp（12 个工具）

### `acp_agent_list`

列出已安装的 ACP 智能体（--available 列出注册表）。CLI：foxos acp agent list [--available]。示例：foxos acp agent list --json

只读：是 · 破坏性：否 · CLI：`foxos acp agent list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `available` | boolean |  | 列出注册表中全部可安装的智能体 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_list", "arguments": {}}
```

### `acp_list`

列出已安装的 ACP 智能体（--available 列出注册表）。CLI：foxos acp list [--available]。示例：foxos acp list

只读：是 · 破坏性：否 · CLI：`foxos acp list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `available` | boolean |  | 列出注册表中全部可安装的智能体 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_list", "arguments": {}}
```

### `acp_agent_install`

从 ACP 官方注册表安装智能体（npm / 校验 sha256 的二进制 / uvx）。CLI：foxos acp agent install AGENT。限制：下载只来自注册表里的官方地址；二进制按注册表的 sha256 校验。示例：foxos acp agent install codex-acp

只读：否 · 破坏性：否 · CLI：`foxos acp agent install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_install", "arguments": {"agent": "…"}}
```

### `acp_agent_uninstall`

卸载用户安装的智能体。CLI：foxos acp agent uninstall AGENT。示例：foxos acp agent uninstall codex-acp

只读：否 · 破坏性：是 · CLI：`foxos acp agent uninstall`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_uninstall", "arguments": {"agent": "…"}}
```

### `acp_agent_show`

查看一个智能体：版本、许可证、来源、登录方式、密钥。CLI：foxos acp agent show AGENT。示例：foxos acp agent show gemini --json

只读：是 · 破坏性：否 · CLI：`foxos acp agent show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_show", "arguments": {"agent": "…"}}
```

### `acp_agent_probe`

真实启动智能体并握手：initialize，可选 session/new。CLI：foxos acp agent probe AGENT [--session]。示例：foxos acp agent probe codex-acp --json

只读：否 · 破坏性：否 · CLI：`foxos acp agent probe`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `session` | boolean |  | 握手后再建一个会话（session/new） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_probe", "arguments": {"agent": "…"}}
```

### `acp_agent_login`

用智能体自己的登录方式登录（ACP authenticate）。CLI：foxos acp agent login AGENT --method METHOD。限制：只有人可以登录智能体账号。示例：foxos acp agent login gemini --method oauth-personal

只读：否 · 破坏性：否 · CLI：`foxos acp agent login`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `method` | string | 是 | 登录方式 ID（见 acp agent show） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_login", "arguments": {"agent": "…", "method": "…"}}
```

### `acp_agent_config`

查看或修改某个 ACP 智能体的设置：默认模型、模式、额外启动参数、非机密环境变量（机密用 acp key set）。CLI：foxos acp agent config AGENT [--model MODEL] [--mode MODE] [--arg ARG] [--env ENV] [--clear]。示例：foxos acp agent config gemini --json

只读：否 · 破坏性：否 · CLI：`foxos acp agent config`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `model` | string |  | 默认模型 ID（会话开始时用 session/set_model 切换；空字符串清除） |
| `mode` | string |  | 默认模式 ID（session/set_mode；空字符串清除） |
| `arg` | array |  | 额外启动参数（可重复；替换原有的额外参数） |
| `env` | object |  | 非机密环境变量 KEY=VALUE（可重复；VALUE 为空表示删除） |
| `clear` | boolean |  | 先清空全部设置 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_config", "arguments": {"agent": "…"}}
```

### `acp_agent_update`

和官方注册表比较版本并更新 ACP 智能体（装到用户目录，系统预装的也不需要 root）。CLI：foxos acp agent update [AGENT] [--all] [--check] [--accept-license]。示例：foxos acp agent update --all --check --json

只读：否 · 破坏性：否 · CLI：`foxos acp agent update`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string |  | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `all` | boolean |  | 检查全部已安装的智能体 |
| `check` | boolean |  | 只检查，不安装 |
| `accept_license` | boolean |  | 确认不可再分发的许可证（例如专有智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_agent_update", "arguments": {}}
```

### `acp_key_set`

保存智能体的 API 密钥到本地密钥库（从标准输入读取，不写日志）。CLI：foxos acp key set AGENT ENV_NAME --value VALUE。限制：只有人可以管理智能体密钥；密钥只存本地密钥库（0600），不写审计日志。示例：printf %s "$KEY" | foxos acp key set codex-acp OPENAI_API_KEY --value-stdin

只读：否 · 破坏性：否 · CLI：`foxos acp key set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `name` | string | 是 | 环境变量名（如 OPENAI_API_KEY） |
| `value` | string | 是 | 密钥值（建议用 --value-stdin） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_key_set", "arguments": {"agent": "…", "name": "…", "value": "…"}}
```

### `acp_key_list`

列出已保存的智能体密钥（只显示末 4 位）。CLI：foxos acp key list [--acp-agent AGENT]。示例：foxos acp key list --json

只读：是 · 破坏性：否 · CLI：`foxos acp key list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string |  | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_key_list", "arguments": {}}
```

### `acp_key_remove`

删除一个智能体密钥。CLI：foxos acp key remove AGENT ENV_NAME。示例：foxos acp key remove codex-acp OPENAI_API_KEY

只读：否 · 破坏性：是 · CLI：`foxos acp key remove`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `agent` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `name` | string | 是 | 环境变量名（如 OPENAI_API_KEY） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "acp_key_remove", "arguments": {"agent": "…", "name": "…"}}
```

## bot（30 个工具）

### `bot_profile_list`

列出智能体。CLI：foxos bot profile list [--hidden]。示例：foxos bot profile list --json

只读：是 · 破坏性：否 · CLI：`foxos bot profile list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `hidden` | boolean |  | 包括隐藏的智能体 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_list", "arguments": {}}
```

### `bot_profile_show`

查看一个智能体。CLI：foxos bot profile show BOT。示例：foxos bot profile show fox --json

只读：是 · 破坏性：否 · CLI：`foxos bot profile show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_show", "arguments": {"bot": "…"}}
```

### `bot_profile_create`

新建智能体。CLI：foxos bot profile create NAME [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN] [--id ID]。限制：这个操作只有人可以做。示例：foxos bot profile create Coder --title Coding --acp-agent codex-acp --icon code --color '#3B82F6' --isolated

只读：否 · 破坏性：否 · CLI：`foxos bot profile create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 名字 |
| `title` | string |  | 头衔（一行） |
| `role` | string |  | 职责说明（它是做什么的） |
| `instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | string |  | 头像颜色 #RRGGBB |
| `image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户 可选：private / public |
| `pinned` | boolean |  | 置顶 |
| `hidden` | boolean |  | 从列表中隐藏 |
| `active` | boolean |  | 是否启用 |
| `notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | string |  | 技能模式：all 全部 / selected 只用选中的 可选：all / selected |
| `skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许 可选：ask / allow_reads / allow_all |
| `rules` | object |  | 审批规则：工具类型=allow/ask/deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | integer |  | 委托最大深度 |
| `max_per_turn` | integer |  | 每轮最多委托几次 |
| `id` | string |  | 指定 ID（小写字母数字与 -） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_create", "arguments": {"name": "…"}}
```

### `bot_profile_update`

修改智能体资料（同 bot config set）。CLI：foxos bot profile update BOT [--name NAME] [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN]。限制：这个操作只有人可以做。示例：foxos bot profile update coder --title Backend

只读：否 · 破坏性：否 · CLI：`foxos bot profile update`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | string |  | 名字 |
| `title` | string |  | 头衔（一行） |
| `role` | string |  | 职责说明（它是做什么的） |
| `instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | string |  | 头像颜色 #RRGGBB |
| `image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户 可选：private / public |
| `pinned` | boolean |  | 置顶 |
| `hidden` | boolean |  | 从列表中隐藏 |
| `active` | boolean |  | 是否启用 |
| `notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | string |  | 技能模式：all 全部 / selected 只用选中的 可选：all / selected |
| `skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许 可选：ask / allow_reads / allow_all |
| `rules` | object |  | 审批规则：工具类型=allow/ask/deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | integer |  | 委托最大深度 |
| `max_per_turn` | integer |  | 每轮最多委托几次 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_update", "arguments": {"bot": "…"}}
```

### `bot_profile_delete`

删除智能体（主智能体不能删）。CLI：foxos bot profile delete BOT。限制：这个操作只有人可以做；主智能体不能删除或停用。示例：foxos bot profile delete coder

只读：否 · 破坏性：是 · CLI：`foxos bot profile delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_delete", "arguments": {"bot": "…"}}
```

### `bot_profile_duplicate`

复制一个智能体的设置。CLI：foxos bot profile duplicate BOT --name NAME。示例：foxos bot profile duplicate coder --name Coder2

只读：否 · 破坏性：否 · CLI：`foxos bot profile duplicate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | string | 是 | 名字 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_duplicate", "arguments": {"bot": "…", "name": "…"}}
```

### `bot_profile_reset`

清空对话（默认也清空记忆）。CLI：foxos bot profile reset BOT [--keep-memory]。示例：foxos bot profile reset coder

只读：否 · 破坏性：是 · CLI：`foxos bot profile reset`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `keep_memory` | boolean |  | 保留记忆 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_profile_reset", "arguments": {"bot": "…"}}
```

### `bot_config_get`

查看一个智能体的全部设置。CLI：foxos bot config get BOT。示例：foxos bot config get fox --json

只读：是 · 破坏性：否 · CLI：`foxos bot config get`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_config_get", "arguments": {"bot": "…"}}
```

### `bot_config_set`

修改智能体设置（与 OpenBot 的 Bot 设置逐项对应）。CLI：foxos bot config set BOT [--name NAME] [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN]。限制：这个操作只有人可以做。示例：foxos bot config set coder --acp-agent claude-acp --skills tdd,architect --approval-mode allow_reads --rule execute=ask

只读：否 · 破坏性：否 · CLI：`foxos bot config set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | string |  | 名字 |
| `title` | string |  | 头衔（一行） |
| `role` | string |  | 职责说明（它是做什么的） |
| `instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | string |  | 头像颜色 #RRGGBB |
| `image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户 可选：private / public |
| `pinned` | boolean |  | 置顶 |
| `hidden` | boolean |  | 从列表中隐藏 |
| `active` | boolean |  | 是否启用 |
| `notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | string |  | 技能模式：all 全部 / selected 只用选中的 可选：all / selected |
| `skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许 可选：ask / allow_reads / allow_all |
| `rules` | object |  | 审批规则：工具类型=allow/ask/deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | integer |  | 委托最大深度 |
| `max_per_turn` | integer |  | 每轮最多委托几次 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_config_set", "arguments": {"bot": "…"}}
```

### `bot_message_send`

给智能体发消息并等待回答（@名字 委托，/技能 调用技能）。CLI：foxos bot message send BOT TEXT [--attach ATTACHMENTS] [--approve {rules,allow,deny}]。示例：foxos bot message send fox '@coder write hello.py'

只读：否 · 破坏性：否 · CLI：`foxos bot message send`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `text` | string | 是 | 文字 |
| `attachments` | array |  | 附件（工作空间内的文件路径，可重复） |
| `approve` | string |  | 这一轮的审批：rules 按规则 / allow 全部允许 / deny 全部拒绝 可选：rules / allow / deny |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_message_send", "arguments": {"bot": "…", "text": "…"}}
```

### `bot_message_list`

查看对话记录。CLI：foxos bot message list BOT [--limit LIMIT]。示例：foxos bot message list fox --json

只读：是 · 破坏性：否 · CLI：`foxos bot message list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `limit` | integer |  | 最多返回多少条 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_message_list", "arguments": {"bot": "…"}}
```

### `bot_task_delegate`

把任务交给另一个智能体（任务/约束/期望结果），等它回报。CLI：foxos bot task delegate TASK --to TO [--constraints CONSTRAINTS] [--expecting EXPECTING]。限制：受对方智能体的委托规则、最大深度和每轮上限约束；被拒绝时返回 refused。示例：foxos bot task delegate --to coder 'fix tests/test_x.py' --expecting 'which files changed'

只读：否 · 破坏性：否 · CLI：`foxos bot task delegate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `to` | string | 是 | 交给哪个智能体 |
| `task` | string | 是 | 任务 |
| `constraints` | string |  | 约束（不能做什么、范围） |
| `expecting` | string |  | 期望得到什么结果 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_task_delegate", "arguments": {"to": "…", "task": "…"}}
```

### `bot_skill_list`

列出技能与原则（工作空间、~/.agents/skills、pstack）。CLI：foxos bot skill list [--bot BOT] [--kind {skill,principle,subagent}]。示例：foxos bot skill list --json

只读：是 · 破坏性：否 · CLI：`foxos bot skill list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | string |  | 类型：skill 技能 / principle 原则 / subagent 子智能体 可选：skill / principle / subagent |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_skill_list", "arguments": {}}
```

### `bot_skill_show`

查看一个技能的内容。CLI：foxos bot skill show SKILL。示例：foxos bot skill show architect

只读：是 · 破坏性：否 · CLI：`foxos bot skill show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 技能名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_skill_show", "arguments": {"name": "…"}}
```

### `bot_skill_run`

让智能体按某个技能完成任务。CLI：foxos bot skill run BOT [TASK] --skill NAME。示例：foxos bot skill run fox --skill architect 'design the plugin interface'

只读：否 · 破坏性：否 · CLI：`foxos bot skill run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | string | 是 | 技能名 |
| `task` | string |  | 任务 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_skill_run", "arguments": {"bot": "…", "name": "…"}}
```

### `bot_skill_install`

把技能（含 pstack）安装到某个代码智能体的技能目录。CLI：foxos bot skill install --harness {claude-code,codex,agents,gemini}。示例：foxos bot skill install --harness claude-code

只读：否 · 破坏性：否 · CLI：`foxos bot skill install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `harness` | string | 是 | 目标代码智能体 可选：claude-code / codex / agents / gemini |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_skill_install", "arguments": {"harness": "claude-code"}}
```

### `bot_skill_models`

写 pstack 的角色配置（pstack-models.md），角色指向狐狸OS 智能体。CLI：foxos bot skill models [ROLE=BOTS...]。示例：foxos bot skill models 'arena runners=claude,codex'

只读：否 · 破坏性：否 · CLI：`foxos bot skill models`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `roles` | object |  | 角色=智能体列表，如 'arena runners=claude,codex' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_skill_models", "arguments": {}}
```

### `bot_memory_list`

列出智能体的记忆。CLI：foxos bot memory list BOT。示例：foxos bot memory list fox

只读：是 · 破坏性：否 · CLI：`foxos bot memory list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_memory_list", "arguments": {"bot": "…"}}
```

### `bot_memory_add`

让智能体记住一件事。CLI：foxos bot memory add BOT TEXT。示例：foxos bot memory add fox 'weekly report goes to #team'

只读：否 · 破坏性：否 · CLI：`foxos bot memory add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `text` | string | 是 | 文字 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_memory_add", "arguments": {"bot": "…", "text": "…"}}
```

### `bot_memory_forget`

删除一条记忆。CLI：foxos bot memory forget BOT MEMORY_ID。示例：foxos bot memory forget fox mem-1a2b3c4d

只读：否 · 破坏性：是 · CLI：`foxos bot memory forget`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `memory` | string | 是 | 记忆 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_memory_forget", "arguments": {"bot": "…", "memory": "…"}}
```

### `bot_approval_list`

列出待审批的请求。CLI：foxos bot approval list。示例：foxos bot approval list --json

只读：是 · 破坏性：否 · CLI：`foxos bot approval list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_approval_list", "arguments": {}}
```

### `bot_approval_answer`

回答一个待审批请求（允许/拒绝）。CLI：foxos bot approval answer REQUEST [--option OPTION] [--deny]。限制：这个操作只有人可以做。示例：foxos bot approval answer apr-0123456789 --option allow

只读：否 · 破坏性：否 · CLI：`foxos bot approval answer`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `request` | string | 是 | 审批请求 ID |
| `option` | string |  | 选项 ID（如 allow、allow_always、reject） |
| `deny` | boolean |  | 拒绝 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_approval_answer", "arguments": {"request": "…"}}
```

### `bot_routine_list`

列出例程。CLI：foxos bot routine list [--bot BOT]。示例：foxos bot routine list --json

只读：是 · 破坏性：否 · CLI：`foxos bot routine list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_routine_list", "arguments": {}}
```

### `bot_routine_create`

新建例程：每隔若干分钟让智能体做一件事。CLI：foxos bot routine create BOT --instruction INSTRUCTION --every-minutes EVERY_MINUTES [--title TITLE]。限制：最短间隔 15 分钟，最多 20 个启用的例程。示例：foxos bot routine create fox --instruction 'tidy the inbox' --every-minutes 60

只读：否 · 破坏性：否 · CLI：`foxos bot routine create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `instruction` | string | 是 | 例程每次要做的事 |
| `every_minutes` | integer | 是 | 间隔分钟（至少 15） |
| `title` | string |  | 头衔（一行） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_routine_create", "arguments": {"bot": "…", "instruction": "…", "every_minutes": 1}}
```

### `bot_routine_update`

启用、停用或修改例程间隔。CLI：foxos bot routine update ROUTINE [--enabled] [--every-minutes EVERY_MINUTES]。示例：foxos bot routine update rt-1a2b3c4d --no-enabled

只读：否 · 破坏性：否 · CLI：`foxos bot routine update`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `routine` | string | 是 | 例程 ID |
| `enabled` | boolean |  | 启用 |
| `every_minutes` | integer |  | 间隔分钟（至少 15） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_routine_update", "arguments": {"routine": "…"}}
```

### `bot_routine_delete`

删除例程。CLI：foxos bot routine delete ROUTINE。示例：foxos bot routine delete rt-1a2b3c4d

只读：否 · 破坏性：是 · CLI：`foxos bot routine delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `routine` | string | 是 | 例程 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_routine_delete", "arguments": {"routine": "…"}}
```

### `bot_routine_run`

运行到期的例程（或立即运行指定例程）。CLI：foxos bot routine run [--routine ROUTINE]。示例：foxos bot routine run

只读：否 · 破坏性：否 · CLI：`foxos bot routine run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `routine` | string |  | 例程 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_routine_run", "arguments": {}}
```

### `bot_channel_set`

设置频道：Telegram 机器人或 Webhook。CLI：foxos bot channel set BOT --kind {telegram,webhook} [--token TOKEN] [--chat CHAT]。限制：这个操作只有人可以做。示例：printf %s "$TG" | foxos bot channel set fox --kind telegram --token-stdin

只读：否 · 破坏性：否 · CLI：`foxos bot channel set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | string | 是 | 频道类型 可选：telegram / webhook |
| `token` | string |  | Telegram 机器人令牌（用 --token-stdin） |
| `chat` | string |  | 只回答这个 Telegram 会话 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_channel_set", "arguments": {"bot": "…", "kind": "telegram"}}
```

### `bot_channel_remove`

移除一个频道。CLI：foxos bot channel remove BOT --kind {telegram,webhook}。示例：foxos bot channel remove fox --kind telegram

只读：否 · 破坏性：是 · CLI：`foxos bot channel remove`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | string | 是 | 频道类型 可选：telegram / webhook |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_channel_remove", "arguments": {"bot": "…", "kind": "telegram"}}
```

### `bot_channel_poll`

收取频道新消息并让智能体回答（Telegram）。CLI：foxos bot channel poll [--bot BOT]。示例：foxos bot channel poll

只读：否 · 破坏性：否 · CLI：`foxos bot channel poll`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "bot_channel_poll", "arguments": {}}
```

## browser（8 个工具）

### `browser_status`

Chrome 是否安装、版本、CDP 开关与端口。CLI：foxos browser status。示例：foxos browser status --json

只读：是 · 破坏性：否 · CLI：`foxos browser status`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_status", "arguments": {}}
```

### `browser_cdp`

开启 / 关闭 Chrome 远程调试（CDP，只听 127.0.0.1）。CLI：foxos browser cdp on|off [--port PORT]。限制：只有人可以开启；智能体只能关闭；只绑定 127.0.0.1；开启后使用单独的智能体配置文件 ~/.config/foxos/chrome-agent。示例：foxos browser cdp on

只读：否 · 破坏性：否 · CLI：`foxos browser cdp`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `state` | string | 是 | on 或 off |
| `port` | integer |  | 调试端口（默认 9222） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_cdp", "arguments": {"state": "…"}}
```

### `browser_open`

在 Chrome 打开网址（CDP 运行时新开标签页，否则启动 Chrome）。CLI：foxos browser open URL [--wait WAIT]。示例：foxos browser open https://github.com/gatesenman/foxos

只读：否 · 破坏性：否 · CLI：`foxos browser open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `url` | string | 是 | 网址 |
| `wait` | number |  | 启动后等待 CDP 就绪的秒数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_open", "arguments": {"url": "…"}}
```

### `browser_tabs`

列出标签页（需要 CDP）。CLI：foxos browser tabs。示例：foxos browser tabs --json

只读：是 · 破坏性：否 · CLI：`foxos browser tabs`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_tabs", "arguments": {}}
```

### `browser_navigate`

让标签页跳转并等待加载完成（需要 CDP）。CLI：foxos browser navigate URL [--tab TAB]。示例：foxos browser navigate https://example.com --tab 3F2A

只读：否 · 破坏性：否 · CLI：`foxos browser navigate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `url` | string | 是 | 网址 |
| `tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_navigate", "arguments": {"url": "…"}}
```

### `browser_eval`

在标签页里执行 JavaScript 并返回值（需要 CDP）。CLI：foxos browser eval JS [--tab TAB]。示例：foxos browser eval 'document.title'

只读：否 · 破坏性：否 · CLI：`foxos browser eval`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `expression` | string | 是 | JavaScript 表达式 |
| `tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_eval", "arguments": {"expression": "…"}}
```

### `browser_screenshot`

截取标签页内容为 PNG（需要 CDP）。CLI：foxos browser screenshot [--path PATH] [--tab TAB]。示例：foxos browser screenshot --path shots/page.png

只读：是 · 破坏性：否 · CLI：`foxos browser screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/） |
| `tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_screenshot", "arguments": {}}
```

### `browser_close`

关闭标签页（需要 CDP）。CLI：foxos browser close TAB。示例：foxos browser close 3F2A

只读：否 · 破坏性：否 · CLI：`foxos browser close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `tab` | string | 是 | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "browser_close", "arguments": {"tab": "…"}}
```

## connector（8 个工具）

### `connector_catalog`

连接器目录。CLI：foxos connector catalog。示例：foxos connector catalog --json

只读：是 · 破坏性：否 · CLI：`foxos connector catalog`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_catalog", "arguments": {}}
```

### `connector_list`

已添加的连接器。CLI：foxos connector list。示例：foxos connector list --json

只读：是 · 破坏性：否 · CLI：`foxos connector list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_list", "arguments": {}}
```

### `connector_add`

添加连接器（目录里的 key，或自定义 URL / 命令）。CLI：foxos connector add [--key KEY] [--id ID] [--title TITLE] [--url URL] [--arg COMMAND] [--auth {none,bearer,oauth}] [--header HEADER]。限制：这个操作只有人可以做。示例：foxos connector add --key exa

只读：否 · 破坏性：否 · CLI：`foxos connector add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string |  | 目录里的 key（见 connector catalog） |
| `id` | string |  | 连接器 ID |
| `title` | string |  | 显示名 |
| `url` | string |  | MCP 服务器地址（https） |
| `command` | array |  | 本地 MCP 命令及参数（可重复 --arg） |
| `auth` | string |  | 认证方式 可选：none / bearer / oauth |
| `header` | string |  | 令牌放在哪个请求头（默认 Authorization: Bearer） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_add", "arguments": {}}
```

### `connector_remove`

移除连接器。CLI：foxos connector remove CONNECTOR。示例：foxos connector remove exa

只读：否 · 破坏性：是 · CLI：`foxos connector remove`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connector` | string | 是 | 连接器 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_remove", "arguments": {"connector": "…"}}
```

### `connector_connect`

连接：API 令牌或 OAuth 登录。CLI：foxos connector connect CONNECTOR [--token TOKEN] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET] [--no-browser]。限制：这个操作只有人可以做；令牌只存本地密钥库，不写日志。示例：printf %s "$KEY" | foxos connector connect exa-authenticated --token-stdin

只读：否 · 破坏性：否 · CLI：`foxos connector connect`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connector` | string | 是 | 连接器 ID |
| `token` | string |  | API 令牌（用 --token-stdin） |
| `client_id` | string |  | OAuth 客户端 ID（不支持动态注册的服务需要） |
| `client_secret` | string |  | OAuth 客户端密钥 |
| `no_browser` | boolean |  | 不自动打开浏览器，只打印授权地址 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_connect", "arguments": {"connector": "…"}}
```

### `connector_disconnect`

断开连接并删除令牌。CLI：foxos connector disconnect CONNECTOR。示例：foxos connector disconnect notion

只读：否 · 破坏性：否 · CLI：`foxos connector disconnect`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connector` | string | 是 | 连接器 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_disconnect", "arguments": {"connector": "…"}}
```

### `connector_tools`

连接器提供的工具。CLI：foxos connector tools CONNECTOR [--refresh]。示例：foxos connector tools exa --refresh

只读：是 · 破坏性：否 · CLI：`foxos connector tools`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connector` | string | 是 | 连接器 ID |
| `refresh` | boolean |  | 重新向服务器获取工具列表 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_tools", "arguments": {"connector": "…"}}
```

### `connector_tool_call`

调用连接器的一个工具。CLI：foxos connector tool call CONNECTOR --tool TOOL [--arguments ARGUMENTS]。限制：智能体调用时：连接器必须对该智能体开启；非只读工具按审批规则询问。示例：foxos connector tool call exa --tool web_search_exa --arguments '{"query":"ACP"}'

只读：否 · 破坏性：否 · CLI：`foxos connector tool call`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connector` | string | 是 | 连接器 ID |
| `tool` | string | 是 | 工具名 |
| `arguments` | object |  | 工具参数（JSON 对象） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "connector_tool_call", "arguments": {"connector": "…", "tool": "…"}}
```

## desktop（15 个工具）

### `desktop_status`

显示当前图形会话与人工接管状态。CLI：foxos desktop status。示例：foxos desktop status --json

只读：是 · 破坏性：否 · CLI：`foxos desktop status`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_status", "arguments": {}}
```

### `desktop_windows`

列出合成器管理的真实窗口。CLI：foxos desktop windows。示例：foxos desktop windows --json

只读：是 · 破坏性：否 · CLI：`foxos desktop windows`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_windows", "arguments": {}}
```

### `desktop_focus`

聚焦一个窗口。CLI：foxos desktop focus WINDOW。示例：foxos desktop focus 4278190080

只读：否 · 破坏性：否 · CLI：`foxos desktop focus`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_focus", "arguments": {"window": "…"}}
```

### `desktop_move`

移动一个窗口。CLI：foxos desktop move WINDOW --x X --y Y。示例：foxos desktop move 4278190080 --x 100 --y 80

只读：否 · 破坏性：否 · CLI：`foxos desktop move`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_move", "arguments": {"window": "…", "x": 1, "y": 1}}
```

### `desktop_resize`

调整一个窗口的大小。CLI：foxos desktop resize WINDOW --width WIDTH --height HEIGHT。示例：foxos desktop resize 4278190080 --width 800 --height 600

只读：否 · 破坏性：否 · CLI：`foxos desktop resize`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | integer | 是 | 宽度（像素） |
| `height` | integer | 是 | 高度（像素） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_resize", "arguments": {"window": "…", "width": 1, "height": 1}}
```

### `desktop_close`

关闭一个窗口。CLI：foxos desktop close WINDOW。示例：foxos desktop close 4278190080

只读：否 · 破坏性：否 · CLI：`foxos desktop close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_close", "arguments": {"window": "…"}}
```

### `desktop_launch`

启动一个应用或命令。CLI：foxos desktop launch CMD...。示例：foxos desktop launch chrome

只读：否 · 破坏性：否 · CLI：`foxos desktop launch`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array | 是 | 要启动的命令和参数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_launch", "arguments": {"command": []}}
```

### `desktop_type`

向当前聚焦的窗口键入文本。CLI：foxos desktop type TEXT。示例：foxos desktop type 'hello'

只读：否 · 破坏性：否 · CLI：`foxos desktop type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要键入的文本 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_type", "arguments": {"text": "…"}}
```

### `desktop_key`

发送按键或组合键。CLI：foxos desktop key KEYS。示例：foxos desktop key Return

只读：否 · 破坏性：否 · CLI：`foxos desktop key`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keys` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_key", "arguments": {"keys": "…"}}
```

### `desktop_click`

在屏幕坐标处点击。CLI：foxos desktop click --x X --y Y [--button BUTTON]。示例：foxos desktop click --x 400 --y 300

只读：否 · 破坏性：否 · CLI：`foxos desktop click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_click", "arguments": {"x": 1, "y": 1}}
```

### `desktop_screenshot`

截取当前会话画面。CLI：foxos desktop screenshot [--path PATH]。示例：foxos desktop screenshot --path shots/desk.png

只读：是 · 破坏性：否 · CLI：`foxos desktop screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_screenshot", "arguments": {}}
```

### `desktop_activity`

现在是谁在操作：每个智能体最近的命令与桌面占用。CLI：foxos desktop activity。示例：foxos desktop activity --json

只读：是 · 破坏性：否 · CLI：`foxos desktop activity`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_activity", "arguments": {}}
```

### `desktop_release`

释放桌面输入占用（人用）。CLI：foxos desktop release。示例：foxos desktop release

只读：否 · 破坏性：否 · CLI：`foxos desktop release`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_release", "arguments": {}}
```

### `desktop_takeover`

人工接管：暂停智能体的写操作。CLI：foxos desktop takeover [--reason REASON] [--only IDENTITY]。限制：只有 human 身份可以执行。示例：foxos desktop takeover --reason 我来改

只读：否 · 破坏性：否 · CLI：`foxos desktop takeover`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_takeover", "arguments": {}}
```

### `desktop_resume`

结束人工接管，恢复智能体写操作。CLI：foxos desktop resume [--only IDENTITY]。限制：只有 human 身份可以执行。示例：foxos desktop resume

只读：否 · 破坏性：否 · CLI：`foxos desktop resume`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `targets` | array |  | 只恢复这些身份；不填则全部恢复 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "desktop_resume", "arguments": {}}
```

## session（15 个工具）

### `session_status`

显示当前图形会话与人工接管状态。CLI：foxos session status。示例：foxos session status --json

只读：是 · 破坏性：否 · CLI：`foxos session status`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_status", "arguments": {}}
```

### `session_windows`

列出合成器管理的真实窗口。CLI：foxos session windows。示例：foxos session windows --json

只读：是 · 破坏性：否 · CLI：`foxos session windows`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_windows", "arguments": {}}
```

### `session_focus`

聚焦一个窗口。CLI：foxos session focus WINDOW。示例：foxos session focus 4278190080

只读：否 · 破坏性：否 · CLI：`foxos session focus`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_focus", "arguments": {"window": "…"}}
```

### `session_move`

移动一个窗口。CLI：foxos session move WINDOW --x X --y Y。示例：foxos session move 4278190080 --x 100 --y 80

只读：否 · 破坏性：否 · CLI：`foxos session move`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_move", "arguments": {"window": "…", "x": 1, "y": 1}}
```

### `session_resize`

调整一个窗口的大小。CLI：foxos session resize WINDOW --width WIDTH --height HEIGHT。示例：foxos session resize 4278190080 --width 800 --height 600

只读：否 · 破坏性：否 · CLI：`foxos session resize`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | integer | 是 | 宽度（像素） |
| `height` | integer | 是 | 高度（像素） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_resize", "arguments": {"window": "…", "width": 1, "height": 1}}
```

### `session_close`

关闭一个窗口。CLI：foxos session close WINDOW。示例：foxos session close 4278190080

只读：否 · 破坏性：否 · CLI：`foxos session close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_close", "arguments": {"window": "…"}}
```

### `session_launch`

启动一个应用或命令。CLI：foxos session launch CMD...。示例：foxos session launch chrome

只读：否 · 破坏性：否 · CLI：`foxos session launch`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array | 是 | 要启动的命令和参数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_launch", "arguments": {"command": []}}
```

### `session_type`

向当前聚焦的窗口键入文本。CLI：foxos session type TEXT。示例：foxos session type 'hello'

只读：否 · 破坏性：否 · CLI：`foxos session type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要键入的文本 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_type", "arguments": {"text": "…"}}
```

### `session_key`

发送按键或组合键。CLI：foxos session key KEYS。示例：foxos session key Return

只读：否 · 破坏性：否 · CLI：`foxos session key`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keys` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_key", "arguments": {"keys": "…"}}
```

### `session_click`

在屏幕坐标处点击。CLI：foxos session click --x X --y Y [--button BUTTON]。示例：foxos session click --x 400 --y 300

只读：否 · 破坏性：否 · CLI：`foxos session click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_click", "arguments": {"x": 1, "y": 1}}
```

### `session_screenshot`

截取当前会话画面。CLI：foxos session screenshot [--path PATH]。示例：foxos session screenshot --path shots/desk.png

只读：是 · 破坏性：否 · CLI：`foxos session screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_screenshot", "arguments": {}}
```

### `session_activity`

现在是谁在操作：每个智能体最近的命令与桌面占用。CLI：foxos session activity。示例：foxos session activity --json

只读：是 · 破坏性：否 · CLI：`foxos session activity`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_activity", "arguments": {}}
```

### `session_release`

释放桌面输入占用（人用）。CLI：foxos session release。示例：foxos session release

只读：否 · 破坏性：否 · CLI：`foxos session release`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_release", "arguments": {}}
```

### `session_takeover`

人工接管：暂停智能体的写操作。CLI：foxos session takeover [--reason REASON] [--only IDENTITY]。限制：只有 human 身份可以执行。示例：foxos session takeover --reason 我来改

只读：否 · 破坏性：否 · CLI：`foxos session takeover`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_takeover", "arguments": {}}
```

### `session_resume`

结束人工接管，恢复智能体写操作。CLI：foxos session resume [--only IDENTITY]。限制：只有 human 身份可以执行。示例：foxos session resume

只读：否 · 破坏性：否 · CLI：`foxos session resume`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `targets` | array |  | 只恢复这些身份；不填则全部恢复 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "session_resume", "arguments": {}}
```

## docs（5 个工具）

### `docs_create`

新建一个 .docx 文档。CLI：foxos docs create FILE [--title TITLE] [--force]。示例：foxos docs create report.docx --title '2026 年销售分析'

只读：否 · 破坏性：否 · CLI：`foxos docs create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `title` | string |  | 文档标题（写成 Title 样式的第一段，并写入文档属性） |
| `force` | boolean |  | 已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "docs_create", "arguments": {"file": "…"}}
```

### `docs_read`

读取文档段落（含样式名）、表格与字数统计。CLI：foxos docs read FILE。示例：foxos docs read report.docx --json

只读：是 · 破坏性：否 · CLI：`foxos docs read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "docs_read", "arguments": {"file": "…"}}
```

### `docs_append`

在文档末尾追加段落、标题或表格。CLI：foxos docs append FILE [TEXT...] [--style STYLE] [--heading HEADING] [--table TABLE]。示例：foxos docs append report.docx '一、总体情况' --heading 1

只读：否 · 破坏性：否 · CLI：`foxos docs append`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `text` | array |  | 要追加的段落，每个参数一段 |
| `style` | string |  | 段落样式（Word 内置英文名），如 List Bullet、Quote |
| `heading` | integer |  | 作为标题追加：0=Title，1–9=Heading 1–9 |
| `table` | array |  | 追加表格：二维数组；CLI 中用 --table-json |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "docs_append", "arguments": {"file": "…"}}
```

### `docs_replace`

查找并替换文本（正文与表格）。CLI：foxos docs replace FILE --find FIND --replace REPLACE。示例：foxos docs replace report.docx --find 2025 --replace 2026

只读：否 · 破坏性：否 · CLI：`foxos docs replace`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `find` | string | 是 | 要查找的文本 |
| `replace` | string | 是 | 替换为 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "docs_replace", "arguments": {"file": "…", "find": "…", "replace": "…"}}
```

### `docs_export`

导出为 pdf / odt / html / txt / md（由扩展名决定）。CLI：foxos docs export FILE OUTPUT [--force]。限制：pdf / odt / html 需要 LibreOffice。示例：foxos docs export report.docx report.pdf

只读：否 · 破坏性：否 · CLI：`foxos docs export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `output` | string | 是 | 输出路径 |
| `force` | boolean |  | 输出已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "docs_export", "arguments": {"file": "…", "output": "…"}}
```

## env（31 个工具）

### `env_images`

列出可用镜像（官方发行版 rootfs）与本地镜像。CLI：foxos env images。示例：foxos env images --json

只读：是 · 破坏性：否 · CLI：`foxos env images`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_images", "arguments": {}}
```

### `env_pull`

下载镜像并校验 sha256（目录 ID、https 地址或 .foxenv 文件）。CLI：foxos env pull IMAGE [--sha256 SHA256]。示例：foxos env pull alpine-3.20

只读：否 · 破坏性：否 · CLI：`foxos env pull`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `image` | string | 是 | 镜像 |
| `sha256` | string |  | 期望的 sha256（自定义地址时建议提供） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_pull", "arguments": {"image": "…"}}
```

### `env_run`

没有镜像就拉取，然后创建并启动（用法靠近 docker run）；可附上来宾桌面。CLI：foxos env run NAME [--image IMAGE] [--iso ISO] [--provider PROVIDER] [--network {user,host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--desktop-attach] [--no-start]。示例：foxos env run dev --image alpine-3.20

只读：否 · 破坏性：否 · CLI：`foxos env run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `image` | string |  | 镜像 ID |
| `iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `provider` | string |  | 指定提供者 |
| `network` | string |  | 网络：user 为用户态转发（来宾 5900 映射到宿主），none 断开，host 仅用于命名空间环境 可选：user / host / none |
| `workspace_mode` | string |  | 工作空间挂载方式 可选：rw / ro / none |
| `memory_mb` | integer |  | 内存上限（MB） |
| `cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | integer |  | 进程数上限 |
| `desktop_attach` | boolean |  | 启动后附上来宾桌面 |
| `no_start` | boolean |  | 只创建，不启动 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_run", "arguments": {"name": "…"}}
```

### `env_desktop-attach`

把完整虚拟机的来宾桌面作为显示通道打开（wayvnc）。CLI：foxos env desktop-attach NAME。示例：foxos env desktop-attach live --json

只读：否 · 破坏性：否 · CLI：`foxos env desktop-attach`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_desktop-attach", "arguments": {"name": "…"}}
```

### `env_create`

创建环境。CLI：foxos env create NAME [--image IMAGE] [--network {host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS]。示例：foxos env create dev

只读：否 · 破坏性：否 · CLI：`foxos env create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `image` | string |  | 镜像 ID |
| `network` | string |  | 网络：host（共享宿主网络）或 none（只有回环） 可选：host / none |
| `workspace_mode` | string |  | 工作空间挂载方式 可选：rw / ro / none |
| `memory_mb` | integer |  | 内存上限（MB） |
| `cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | integer |  | 进程数上限 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_create", "arguments": {"name": "…"}}
```

### `env_list`

列出环境及状态。CLI：foxos env list。示例：foxos env list --json

只读：是 · 破坏性：否 · CLI：`foxos env list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_list", "arguments": {}}
```

### `env_info`

环境详情（配置、快照、资源使用）。CLI：foxos env info NAME。示例：foxos env info dev --json

只读：是 · 破坏性：否 · CLI：`foxos env info`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_info", "arguments": {"name": "…"}}
```

### `env_start`

启动环境。CLI：foxos env start NAME。示例：foxos env start dev

只读：否 · 破坏性：否 · CLI：`foxos env start`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_start", "arguments": {"name": "…"}}
```

### `env_stop`

停止环境。CLI：foxos env stop NAME [--timeout TIMEOUT]。示例：foxos env stop dev

只读：否 · 破坏性：否 · CLI：`foxos env stop`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `timeout` | number |  | 等待秒数，超时强制结束 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_stop", "arguments": {"name": "…"}}
```

### `env_restart`

重启环境。CLI：foxos env restart NAME。示例：foxos env restart dev

只读：否 · 破坏性：否 · CLI：`foxos env restart`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_restart", "arguments": {"name": "…"}}
```

### `env_exec`

在环境中执行命令（默认工作目录 /workspace）。CLI：foxos env exec NAME [CMD...] [--cwd CWD] [--timeout TIMEOUT]。示例：foxos env exec dev -- uname -a

只读：否 · 破坏性：否 · CLI：`foxos env exec`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `cwd` | string |  | 环境内工作目录 |
| `timeout` | number |  | 超时秒数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_exec", "arguments": {"name": "…"}}
```

### `env_shell`

进入环境的交互式 shell。CLI：foxos env shell NAME。示例：foxos env shell dev

只读：否 · 破坏性：否 · CLI：`foxos env shell`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_shell", "arguments": {"name": "…"}}
```

### `env_clone`

克隆环境（复制可写层与设置）。CLI：foxos env clone NAME NEW_NAME。示例：foxos env clone dev dev-copy

只读：否 · 破坏性：否 · CLI：`foxos env clone`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `new_name` | string | 是 | 新环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_clone", "arguments": {"name": "…", "new_name": "…"}}
```

### `env_snapshot`

为停止的环境创建快照。CLI：foxos env snapshot NAME [--label LABEL]。示例：foxos env snapshot dev --label 装好依赖

只读：否 · 破坏性：否 · CLI：`foxos env snapshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `label` | string |  | 说明 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_snapshot", "arguments": {"name": "…"}}
```

### `env_restore`

恢复到快照。CLI：foxos env restore NAME SNAPSHOT。示例：foxos env restore dev 20261110T213000

只读：否 · 破坏性：否 · CLI：`foxos env restore`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `snapshot` | string | 是 | 快照 ID |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_restore", "arguments": {"name": "…", "snapshot": "…"}}
```

### `env_export`

导出为 .foxenv 镜像（tar + zstd + manifest + sha256）。CLI：foxos env export NAME --out OUT。示例：foxos env export dev --out backups/dev.foxenv

只读：否 · 破坏性：否 · CLI：`foxos env export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `out` | string | 是 | 输出文件（工作空间内） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_export", "arguments": {"name": "…", "out": "…"}}
```

### `env_import`

从 .foxenv 镜像导入为新环境。CLI：foxos env import FILE --name NAME。示例：foxos env import backups/dev.foxenv --name dev2

只读：否 · 破坏性：否 · CLI：`foxos env import`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | .foxenv 文件（工作空间内） |
| `name` | string | 是 | 新环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_import", "arguments": {"file": "…", "name": "…"}}
```

### `env_delete`

删除环境（不删除镜像与工作空间）。CLI：foxos env delete NAME。示例：foxos env delete dev-copy

只读：否 · 破坏性：是 · CLI：`foxos env delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_delete", "arguments": {"name": "…"}}
```

### `env_mount`

添加 / 移除宿主目录挂载。CLI：foxos env mount NAME --source SOURCE --target TARGET [--readonly] [--remove]。示例：foxos env mount dev --source ~/datasets --target /data --readonly

只读：否 · 破坏性：否 · CLI：`foxos env mount`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `source` | string | 是 | 宿主路径 |
| `target` | string | 是 | 环境内路径 |
| `readonly` | boolean |  | 只读 |
| `remove` | boolean |  | 移除该挂载 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_mount", "arguments": {"name": "…", "source": "…", "target": "…"}}
```

### `env_limits`

设置资源限制、网络与工作空间权限。CLI：foxos env limits NAME [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--network {host,none}] [--workspace-mode {rw,ro,none}]。示例：foxos env limits dev --memory-mb 2048 --pids 512

只读：否 · 破坏性：否 · CLI：`foxos env limits`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `memory_mb` | integer |  | 内存上限 MB（0 取消） |
| `cpus` | number |  | CPU 上限（0 取消） |
| `pids` | integer |  | 进程数上限（0 取消） |
| `network` | string |  | 网络 可选：host / none |
| `workspace_mode` | string |  | 工作空间挂载 可选：rw / ro / none |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_limits", "arguments": {"name": "…"}}
```

### `env_stats`

资源使用（进程数、CPU 时间、内存、磁盘）。CLI：foxos env stats [NAME]。示例：foxos env stats --json

只读：是 · 破坏性：否 · CLI：`foxos env stats`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string |  | 环境名（缺省为全部） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_stats", "arguments": {}}
```

### `env_logs`

环境日志。CLI：foxos env logs NAME [--lines LINES]。示例：foxos env logs dev -n 50

只读：是 · 破坏性：否 · CLI：`foxos env logs`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `lines` | integer |  | 行数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_logs", "arguments": {"name": "…"}}
```

### `env_expose`

把虚拟机的 SSH 端口转发开放到主机的所有地址，或收回到本机。CLI：foxos env expose NAME --ssh on|off [--port PORT]。限制：开放只有人能执行；下次启动生效；主机防火墙需放行该端口。示例：foxos env expose dev --ssh on --port 2222

只读：否 · 破坏性：否 · CLI：`foxos env expose`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `ssh` | string | 是 | on（对外开放）或 off（只在本机） |
| `port` | integer |  | 主机上的固定端口（默认自动挑一个） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_expose", "arguments": {"name": "…", "ssh": "…"}}
```

### `env_action_add`

添加自定义操作（支持 ${env} ${image} ${workspace} ${host_workspace} ${hostname} 变量）。CLI：foxos env action add NAME ACTION --command COMMAND。示例：foxos env action add dev test --command 'cd ${workspace} && make test'

只读：否 · 破坏性：否 · CLI：`foxos env action add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `action` | string | 是 | 操作名 |
| `command` | string | 是 | 环境内执行的 shell 命令 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_action_add", "arguments": {"name": "…", "action": "…", "command": "…"}}
```

### `env_action_run`

运行自定义操作。CLI：foxos env action run NAME ACTION。示例：foxos env action run dev test --json

只读：否 · 破坏性：否 · CLI：`foxos env action run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `action` | string | 是 | 操作名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_action_run", "arguments": {"name": "…", "action": "…"}}
```

### `env_providers`

列出环境提供者（内置与第三方）及其能力、可用性。CLI：foxos env providers。示例：foxos env providers --json

只读：是 · 破坏性：否 · CLI：`foxos env providers`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_providers", "arguments": {}}
```

### `env_doctor`

检查本机虚拟化能力（WSL、Windows Sandbox、Hyper-V、用户命名空间…）并给出修复操作。CLI：foxos env doctor [--provider PROVIDER]。示例：foxos env doctor --json

只读：是 · 破坏性：否 · CLI：`foxos env doctor`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `provider` | string |  | 只检查某个提供者 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_doctor", "arguments": {}}
```

### `env_fix`

执行 doctor 给出的修复操作（启用 WSL 等，需要管理员确认，可能需要重启）。CLI：foxos env fix --provider PROVIDER --action ACTION。示例：foxos env fix --provider wsl2 --action enable-wsl

只读：否 · 破坏性：否 · CLI：`foxos env fix`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `provider` | string | 是 | 提供者 |
| `action` | string | 是 | 修复操作 ID（见 doctor 输出） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_fix", "arguments": {"provider": "…", "action": "…"}}
```

### `env_catalog`

可一键安装的系统目录（WSL 发行版、LXC/官方根文件系统、Windows Sandbox、Hyper-V、macOS）。CLI：foxos env catalog [--guest {linux,windows,macos,any}] [--provider PROVIDER] [--available] [--presets]。示例：foxos env catalog --json

只读：是 · 破坏性：否 · CLI：`foxos env catalog`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `guest` | string |  | 来宾系统 可选：linux / windows / macos / any |
| `provider` | string |  | 只看某个提供者 |
| `available` | boolean |  | 只显示本机可安装的 |
| `presets` | boolean |  | 只显示狐狸OS 预设系统 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_catalog", "arguments": {}}
```

### `env_install`

从目录一键安装一个系统为新环境（下载、校验 sha256、导入）。CLI：foxos env install ENTRY NAME [--provider PROVIDER] [--url URL] [--sha256 SHA256] [--iso ISO] [--location LOCATION] [--memory-mb MEMORY_MB] [--cpus CPUS] [--disk-gb DISK_GB] [--dry-run] [--product-key PRODUCT_KEY] [--start] [--wait-ready WAIT_READY]。示例：foxos env install foxos-debian-12 dev --start --wait-ready 900

只读：否 · 破坏性：否 · CLI：`foxos env install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `entry` | string | 是 | 目录条目 ID（foxos env catalog） |
| `name` | string | 是 | 环境名 |
| `provider` | string |  | 指定提供者 |
| `url` | string |  | 自定义根文件系统地址（custom-rootfs） |
| `sha256` | string |  | 自定义来源的 sha256 |
| `iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `location` | string |  | 安装位置（Windows 目录） |
| `memory_mb` | integer |  | 内存 MB（Hyper-V / Sandbox） |
| `cpus` | integer |  | CPU 数（Hyper-V） |
| `disk_gb` | integer |  | 磁盘 GB（Hyper-V） |
| `dry_run` | boolean |  | 只输出安装计划，不执行 |
| `product_key` | string |  | Windows 产品密钥（可选；评估版不需要） |
| `start` | boolean |  | 装好后启动（Linux KVM） |
| `wait_ready` | number |  | 启动后等待来宾报告就绪的秒数（0 = 不等） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_install", "arguments": {"entry": "…", "name": "…"}}
```

### `env_progress`

查看安装进度。CLI：foxos env progress NAME。示例：foxos env progress ubuntu --json

只读：是 · 破坏性：否 · CLI：`foxos env progress`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "env_progress", "arguments": {"name": "…"}}
```

## everything（7 个工具）

### `everything_list`

列出 51 个 Everything 应用（分组、许可证、安装状态、操作数）。CLI：foxos everything list [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--installed]。示例：foxos everything list

只读：是 · 破坏性：否 · CLI：`foxos everything list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `group` | string |  | 只看某个分组 可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `installed_only` | boolean |  | 只列出已安装的 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_list", "arguments": {}}
```

### `everything_info`

查看一个应用的详情、许可证与可用命令。CLI：foxos everything info APP。示例：foxos everything info tasks --json

只读：是 · 破坏性：否 · CLI：`foxos everything info`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_info", "arguments": {"app": "…"}}
```

### `everything_install`

从上游源码在本机构建并安装应用（固定提交，含许可证声明）。CLI：foxos everything install [APP...] [--all] [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--source SOURCE] [--force]。限制：需要 git、Node.js 22.12+ 与 npm；每个应用构建约 2–20 秒（不含下载）。示例：foxos everything install tasks chess

只读：否 · 破坏性：否 · CLI：`foxos everything install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `apps` | array |  | 应用 ID |
| `all` | boolean |  | 安装全部 51 个 |
| `group` | string |  | 安装整个分组 可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `source` | string |  | 使用本地上游仓库目录（离线 / 镜像），默认从 GitHub 获取 |
| `force` | boolean |  | 已安装也重新构建 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_install", "arguments": {}}
```

### `everything_commands`

列出一个应用的全部命令（语义操作 + 通用界面命令）及参数 Schema。CLI：foxos everything commands APP。示例：foxos everything commands tasks --json

只读：是 · 破坏性：否 · CLI：`foxos everything commands`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_commands", "arguments": {"app": "…"}}
```

### `everything_run`

执行一个应用的任意命令（与 foxos <app> <资源> <动词> 相同；权限、审计、写锁按被执行的命令计）。CLI：foxos everything run APP COMMAND [--args ARGS]。示例：foxos everything run tasks "add-task set" --args '{"value": "买牛奶", "submit": true}' --json

只读：是 · 破坏性：否 · CLI：`foxos everything run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |
| `command` | string | 是 | 命令，如 "task create" 或 "ui snapshot" |
| `args` | object |  | 命令参数（JSON 对象） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_run", "arguments": {"app": "…", "command": "…"}}
```

### `everything_icons`

给已安装的应用补上上游自带的程序图标（不重新构建）。CLI：foxos everything icons [--source SOURCE]。示例：foxos everything icons --json

只读：否 · 破坏性：否 · CLI：`foxos everything icons`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `source` | string |  | 本地上游仓库路径（缺省从 GitHub 获取固定提交） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_icons", "arguments": {}}
```

### `everything_uninstall`

卸载应用（保留工作空间中的数据）。CLI：foxos everything uninstall APP。示例：foxos everything uninstall chess

只读：否 · 破坏性：是 · CLI：`foxos everything uninstall`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "everything_uninstall", "arguments": {"app": "…"}}
```

## spreadsheet（386 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `spreadsheet_account-menu_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_font_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_font-size_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_font-size-2_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_indent_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_number-format_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_places_show` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_fewer-places_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_sheets_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_options_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_view_zoom-level` |  | `target`*: string, `machine`: string |
| `spreadsheet_other-charts_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_pen_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_pencil_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_highlighter_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_item_select` | 是 | `target`*: string, `machine`: string |
| `spreadsheet_spreadsheets_previous` | 是 | `machine`: string |
| `spreadsheet_autosave_toggle` |  | `machine`: string |
| `spreadsheet_save_save` |  | `machine`: string |
| `spreadsheet_undo_undo` |  | `machine`: string |
| `spreadsheet_history_undo` |  | `machine`: string |
| `spreadsheet_redo_redo` |  | `machine`: string |
| `spreadsheet_customize-quick-access-toolbar_activate` |  | `machine`: string |
| `spreadsheet_edit_update` |  | `machine`: string |
| `spreadsheet_view_show` | 是 | `machine`: string |
| `spreadsheet_insert_create` |  | `machine`: string |
| `spreadsheet_format_activate` |  | `machine`: string |
| `spreadsheet_tools_activate` |  | `machine`: string |
| `spreadsheet_help_show` | 是 | `machine`: string |
| `spreadsheet_untitled-spreadsheet_rename` |  | `machine`: string |
| `spreadsheet_saved_activate` |  | `machine`: string |
| `spreadsheet_menus_search` | 是 | `machine`: string |
| `spreadsheet_comments_activate` |  | `machine`: string |
| `spreadsheet_home_show` | 是 | `machine`: string |
| `spreadsheet_insert-2_create` |  | `machine`: string |
| `spreadsheet_draw_draw` |  | `machine`: string |
| `spreadsheet_page-layout_show` | 是 | `machine`: string |
| `spreadsheet_formulas_show` | 是 | `machine`: string |
| `spreadsheet_review_show` | 是 | `machine`: string |
| `spreadsheet_view-2_show` | 是 | `machine`: string |
| `spreadsheet_automate_show` | 是 | `machine`: string |
| `spreadsheet_scroll-ribbon-left_activate` |  | `machine`: string |
| `spreadsheet_scroll-ribbon-right_activate` |  | `machine`: string |
| `spreadsheet_ribbon_collapse` | 是 | `machine`: string |
| `spreadsheet_paste_paste` |  | `machine`: string |
| `spreadsheet_options_paste` |  | `machine`: string |
| `spreadsheet_cut_cut` |  | `machine`: string |
| `spreadsheet_copy_copy` |  | `machine`: string |
| `spreadsheet_format-painter_activate` |  | `machine`: string |
| `spreadsheet_increase-font-size_activate` |  | `machine`: string |
| `spreadsheet_bold_format` |  | `machine`: string |
| `spreadsheet_italic_format` |  | `machine`: string |
| `spreadsheet_underline_format` |  | `machine`: string |
| `spreadsheet_borders_activate` |  | `machine`: string |
| `spreadsheet_fill-color-yellow_confirm` |  | `machine`: string |
| `spreadsheet_fill-color_activate` |  | `machine`: string |
| `spreadsheet_font-color-red_confirm` |  | `machine`: string |
| `spreadsheet_text-color_activate` |  | `machine`: string |
| `spreadsheet_top-align_activate` |  | `machine`: string |
| `spreadsheet_middle-align_activate` |  | `machine`: string |
| `spreadsheet_bottom-align_activate` |  | `machine`: string |
| `spreadsheet_orientation_activate` |  | `machine`: string |
| `spreadsheet_left_align` |  | `machine`: string |
| `spreadsheet_center_align` |  | `machine`: string |
| `spreadsheet_right_align` |  | `machine`: string |
| `spreadsheet_increase-indent_activate` |  | `machine`: string |
| `spreadsheet_wrap-text_activate` |  | `machine`: string |
| `spreadsheet_merge-center_activate` |  | `machine`: string |
| `spreadsheet_merge-options_activate` |  | `machine`: string |
| `spreadsheet_accounting-number-format_activate` |  | `machine`: string |
| `spreadsheet_accounting-number-format-options_activate` |  | `machine`: string |
| `spreadsheet_format-as-percent_activate` |  | `machine`: string |
| `spreadsheet_comma-style_activate` |  | `machine`: string |
| `spreadsheet_conditional-formatting_activate` |  | `machine`: string |
| `spreadsheet_format-as-table_activate` |  | `machine`: string |
| `spreadsheet_cell-styles_activate` |  | `machine`: string |
| `spreadsheet_insert-3_create` |  | `machine`: string |
| `spreadsheet_delete_delete` |  | `machine`: string |
| `spreadsheet_format-2_activate` |  | `machine`: string |
| `spreadsheet_autosum_activate` |  | `machine`: string |
| `spreadsheet_autosum-options_activate` |  | `machine`: string |
| `spreadsheet_fill_activate` |  | `machine`: string |
| `spreadsheet_clear_clear` |  | `machine`: string |
| `spreadsheet_filter_sort` | 是 | `machine`: string |
| `spreadsheet_select_search` | 是 | `machine`: string |
| `spreadsheet_cell-reference_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `spreadsheet_named-ranges_activate` |  | `machine`: string |
| `spreadsheet_edit_cancel` | 是 | `machine`: string |
| `spreadsheet_edit_confirm` |  | `machine`: string |
| `spreadsheet_function_create` |  | `machine`: string |
| `spreadsheet_formula-or-value_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `spreadsheet_formula-bar_expand` | 是 | `machine`: string |
| `spreadsheet_select_select` | 是 | `machine`: string |
| `spreadsheet_spreadsheet-grid_activate` |  | `machine`: string |
| `spreadsheet_scroll-sheets-left_activate` |  | `machine`: string |
| `spreadsheet_scroll-sheets-right_activate` |  | `machine`: string |
| `spreadsheet_sheets_activate` |  | `machine`: string |
| `spreadsheet_sheet_create` |  | `machine`: string |
| `spreadsheet_accessibility_run` |  | `machine`: string |
| `spreadsheet_normal_activate` |  | `machine`: string |
| `spreadsheet_page-layout_activate` |  | `machine`: string |
| `spreadsheet_page-break-preview_activate` |  | `machine`: string |
| `spreadsheet_view_zoom-out` |  | `machine`: string |
| `spreadsheet_worksheet-zoom_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `spreadsheet_view_zoom-` |  | `machine`: string |
| `spreadsheet_assistant_resize` |  | `machine`: string |
| `spreadsheet_chat_create` |  | `machine`: string |
| `spreadsheet_assistant-settings_activate` |  | `machine`: string |
| `spreadsheet_assistant_collapse` | 是 | `machine`: string |
| `spreadsheet_loan-calculator-payment-schedule_create` |  | `machine`: string |
| `spreadsheet_message-assistant_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `spreadsheet_attach-files_activate` |  | `machine`: string |
| `spreadsheet_send_send` |  | `machine`: string |
| `spreadsheet_spreadsheet_create` |  | `machine`: string |
| `spreadsheet_open_open` | 是 | `machine`: string |
| `spreadsheet_customize-quick-access-toolbar-save_save` |  | `machine`: string |
| `spreadsheet_print_print` | 是 | `machine`: string |
| `spreadsheet_spelling_activate` |  | `machine`: string |
| `spreadsheet_customize-quick-access-toolbar-undo_undo` |  | `machine`: string |
| `spreadsheet_customize-quick-access-toolbar-redo_redo` |  | `machine`: string |
| `spreadsheet_ascending_sort` | 是 | `machine`: string |
| `spreadsheet_descending_sort` | 是 | `machine`: string |
| `spreadsheet_find_search` | 是 | `machine`: string |
| `spreadsheet_chart_create` |  | `machine`: string |
| `spreadsheet_filter_filter` | 是 | `machine`: string |
| `spreadsheet_commands_show` | 是 | `machine`: string |
| `spreadsheet_below-ribbon_show` | 是 | `machine`: string |
| `spreadsheet_command-labels_show` | 是 | `machine`: string |
| `spreadsheet_close_close` | 是 | `machine`: string |
| `spreadsheet_name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `spreadsheet_cancel_cancel` | 是 | `machine`: string |
| `spreadsheet_rename_rename` |  | `machine`: string |
| `spreadsheet_system-theme_toggle` |  | `machine`: string |
| `spreadsheet_light-theme_toggle` |  | `machine`: string |
| `spreadsheet_dark-theme_toggle` |  | `machine`: string |
| `spreadsheet_regional-format-english-united-states_activate` |  | `machine`: string |
| `spreadsheet_options_activate` |  | `machine`: string |
| `spreadsheet_keyboard-shortcuts_activate` |  | `machine`: string |
| `spreadsheet_about_show` | 是 | `machine`: string |
| `spreadsheet_pivottable_activate` |  | `machine`: string |
| `spreadsheet_recommended-pivottables_activate` |  | `machine`: string |
| `spreadsheet_table_activate` |  | `machine`: string |
| `spreadsheet_pictures_activate` |  | `machine`: string |
| `spreadsheet_shapes_activate` |  | `machine`: string |
| `spreadsheet_icons_activate` |  | `machine`: string |
| `spreadsheet_smartart-graphic_create` |  | `machine`: string |
| `spreadsheet_recommended-charts_activate` |  | `machine`: string |
| `spreadsheet_column-chart_create` |  | `machine`: string |
| `spreadsheet_line-chart_create` |  | `machine`: string |
| `spreadsheet_pie-chart_create` |  | `machine`: string |
| `spreadsheet_bar-chart_create` |  | `machine`: string |
| `spreadsheet_area-chart_create` |  | `machine`: string |
| `spreadsheet_scatter-chart_create` |  | `machine`: string |
| `spreadsheet_hierarchy-chart_create` |  | `machine`: string |
| `spreadsheet_statistic-chart_create` |  | `machine`: string |
| `spreadsheet_combo-chart_create` |  | `machine`: string |
| `spreadsheet_line-sparklines_create` |  | `machine`: string |
| `spreadsheet_column-sparklines_create` |  | `machine`: string |
| `spreadsheet_win-loss-sparklines_create` |  | `machine`: string |
| `spreadsheet_slicer_activate` |  | `machine`: string |
| `spreadsheet_timeline_activate` |  | `machine`: string |
| `spreadsheet_link_create` |  | `machine`: string |
| `spreadsheet_note_activate` |  | `machine`: string |
| `spreadsheet_comment_activate` |  | `machine`: string |
| `spreadsheet_text-box_activate` |  | `machine`: string |
| `spreadsheet_header-footer_activate` |  | `machine`: string |
| `spreadsheet_wordart_activate` |  | `machine`: string |
| `spreadsheet_checkbox_activate` |  | `machine`: string |
| `spreadsheet_dropdown_activate` |  | `machine`: string |
| `spreadsheet_date-picker_activate` |  | `machine`: string |
| `spreadsheet_equation_activate` |  | `machine`: string |
| `spreadsheet_equation-options_activate` |  | `machine`: string |
| `spreadsheet_symbol_activate` |  | `machine`: string |
| `spreadsheet_insert-sheet_create` |  | `machine`: string |
| `spreadsheet_draw-select_select` | 是 | `machine`: string |
| `spreadsheet_lasso-select_activate` |  | `machine`: string |
| `spreadsheet_eraser_activate` |  | `machine`: string |
| `spreadsheet_pen_create` |  | `machine`: string |
| `spreadsheet_touch_draw` |  | `machine`: string |
| `spreadsheet_ink-shape_activate` |  | `machine`: string |
| `spreadsheet_themes_activate` |  | `machine`: string |
| `spreadsheet_theme-colors_activate` |  | `machine`: string |
| `spreadsheet_theme-fonts_activate` |  | `machine`: string |
| `spreadsheet_effects_activate` |  | `machine`: string |
| `spreadsheet_margins_activate` |  | `machine`: string |
| `spreadsheet_size_activate` |  | `machine`: string |
| `spreadsheet_area_print` | 是 | `machine`: string |
| `spreadsheet_breaks_activate` |  | `machine`: string |
| `spreadsheet_sheet-background_activate` |  | `machine`: string |
| `spreadsheet_titles_print` | 是 | `machine`: string |
| `spreadsheet_page-setup_activate` |  | `machine`: string |
| `spreadsheet_pdf_export` |  | `machine`: string |
| `spreadsheet_width_activate` |  | `machine`: string |
| `spreadsheet_height_activate` |  | `machine`: string |
| `spreadsheet_scale_activate` |  | `machine`: string |
| `spreadsheet_gridlines_activate` |  | `machine`: string |
| `spreadsheet_gridlines_print` | 是 | `machine`: string |
| `spreadsheet_headings_activate` |  | `machine`: string |
| `spreadsheet_headings_print` | 是 | `machine`: string |
| `spreadsheet_bring-forward_activate` |  | `machine`: string |
| `spreadsheet_bring-forward-options_activate` |  | `machine`: string |
| `spreadsheet_backward_send` |  | `machine`: string |
| `spreadsheet_backward-options_send` |  | `machine`: string |
| `spreadsheet_selection-pane_activate` |  | `machine`: string |
| `spreadsheet_align_align` |  | `machine`: string |
| `spreadsheet_group_group` |  | `machine`: string |
| `spreadsheet_rotate_rotate` |  | `machine`: string |
| `spreadsheet_recently-used_activate` |  | `machine`: string |
| `spreadsheet_financial-functions_activate` |  | `machine`: string |
| `spreadsheet_logical-functions_activate` |  | `machine`: string |
| `spreadsheet_text-functions_activate` |  | `machine`: string |
| `spreadsheet_date-time-functions_activate` |  | `machine`: string |
| `spreadsheet_lookup-reference-functions_activate` |  | `machine`: string |
| `spreadsheet_math-trig-functions_activate` |  | `machine`: string |
| `spreadsheet_functions_show` | 是 | `machine`: string |
| `spreadsheet_name-manager_activate` |  | `machine`: string |
| `spreadsheet_define-name_activate` |  | `machine`: string |
| `spreadsheet_use-formula_activate` |  | `machine`: string |
| `spreadsheet_from-selection_create` |  | `machine`: string |
| `spreadsheet_trace-precedents_activate` |  | `machine`: string |
| `spreadsheet_trace-dependents_activate` |  | `machine`: string |
| `spreadsheet_arrows_delete` |  | `machine`: string |
| `spreadsheet_formulas-2_show` | 是 | `machine`: string |
| `spreadsheet_error-checking_activate` |  | `machine`: string |
| `spreadsheet_error-checking-options_activate` |  | `machine`: string |
| `spreadsheet_evaluate-formula_activate` |  | `machine`: string |
| `spreadsheet_watch-window_activate` |  | `machine`: string |
| `spreadsheet_calculation-options_activate` |  | `machine`: string |
| `spreadsheet_now_run` |  | `machine`: string |
| `spreadsheet_sheet_run` |  | `machine`: string |
| `spreadsheet_formulas-values_activate` |  | `machine`: string |
| `spreadsheet_get-data_activate` |  | `machine`: string |
| `spreadsheet_from-text-csv_activate` |  | `machine`: string |
| `spreadsheet_from-web_activate` |  | `machine`: string |
| `spreadsheet_from-table-range_activate` |  | `machine`: string |
| `spreadsheet_refresh_activate` |  | `machine`: string |
| `spreadsheet_refresh-options_activate` |  | `machine`: string |
| `spreadsheet_queries-connections_activate` |  | `machine`: string |
| `spreadsheet_links_update` |  | `machine`: string |
| `spreadsheet_z_sort` | 是 | `machine`: string |
| `spreadsheet_data-z_sort` | 是 | `machine`: string |
| `spreadsheet_sort_sort` | 是 | `machine`: string |
| `spreadsheet_data-filter_filter` | 是 | `machine`: string |
| `spreadsheet_filter_clear` |  | `machine`: string |
| `spreadsheet_reapply_activate` |  | `machine`: string |
| `spreadsheet_advanced-filter_activate` |  | `machine`: string |
| `spreadsheet_text-columns_activate` |  | `machine`: string |
| `spreadsheet_flash-fill_activate` |  | `machine`: string |
| `spreadsheet_duplicates_delete` |  | `machine`: string |
| `spreadsheet_data-validation_activate` |  | `machine`: string |
| `spreadsheet_data-validation-options_activate` |  | `machine`: string |
| `spreadsheet_consolidate_activate` |  | `machine`: string |
| `spreadsheet_form_activate` |  | `machine`: string |
| `spreadsheet_data-cleanup_activate` |  | `machine`: string |
| `spreadsheet_what-if-analysis_activate` |  | `machine`: string |
| `spreadsheet_goal-seek_activate` |  | `machine`: string |
| `spreadsheet_forecast-sheet_activate` |  | `machine`: string |
| `spreadsheet_column-stats_activate` |  | `machine`: string |
| `spreadsheet_data-analysis_activate` |  | `machine`: string |
| `spreadsheet_solver_activate` |  | `machine`: string |
| `spreadsheet_rows_ungroup` |  | `machine`: string |
| `spreadsheet_subtotal_activate` |  | `machine`: string |
| `spreadsheet_detail_show` | 是 | `machine`: string |
| `spreadsheet_detail_hide` | 是 | `machine`: string |
| `spreadsheet_auto-outline_activate` |  | `machine`: string |
| `spreadsheet_outline_clear` |  | `machine`: string |
| `spreadsheet_outline-settings_activate` |  | `machine`: string |
| `spreadsheet_review-spelling_activate` |  | `machine`: string |
| `spreadsheet_thesaurus_activate` |  | `machine`: string |
| `spreadsheet_spelling-as-you-type_activate` |  | `machine`: string |
| `spreadsheet_autocorrect-options_activate` |  | `machine`: string |
| `spreadsheet_workbook-statistics_activate` |  | `machine`: string |
| `spreadsheet_translate_activate` |  | `machine`: string |
| `spreadsheet_comment_create` |  | `machine`: string |
| `spreadsheet_comment_delete` |  | `machine`: string |
| `spreadsheet_comment_previous` | 是 | `machine`: string |
| `spreadsheet_comment_next` | 是 | `machine`: string |
| `spreadsheet_comments_show` | 是 | `machine`: string |
| `spreadsheet_note_delete` |  | `machine`: string |
| `spreadsheet_notes-sheet_select` | 是 | `machine`: string |
| `spreadsheet_changes_show` | 是 | `machine`: string |
| `spreadsheet_protect-sheet_activate` |  | `machine`: string |
| `spreadsheet_protect-workbook_activate` |  | `machine`: string |
| `spreadsheet_protected-ranges_activate` |  | `machine`: string |
| `spreadsheet_share_share` |  | `machine`: string |
| `spreadsheet_copy_send` |  | `machine`: string |
| `spreadsheet_version-history_activate` |  | `machine`: string |
| `spreadsheet_normal-view_activate` |  | `machine`: string |
| `spreadsheet_page-layout-view_activate` |  | `machine`: string |
| `spreadsheet_custom-views_activate` |  | `machine`: string |
| `spreadsheet_sheet-view_activate` |  | `machine`: string |
| `spreadsheet_sheet-view_create` |  | `machine`: string |
| `spreadsheet_keep-sheet-view_activate` |  | `machine`: string |
| `spreadsheet_exit-sheet-view_activate` |  | `machine`: string |
| `spreadsheet_options-sheet-view_activate` |  | `machine`: string |
| `spreadsheet_formula-bar_activate` |  | `machine`: string |
| `spreadsheet_zeros_show` | 是 | `machine`: string |
| `spreadsheet_page-breaks_activate` |  | `machine`: string |
| `spreadsheet_zoom_zoom` | 是 | `machine`: string |
| `spreadsheet_view-2_zoom-` |  | `machine`: string |
| `spreadsheet_freeze-panes_activate` |  | `machine`: string |
| `spreadsheet_split_activate` |  | `machine`: string |
| `spreadsheet_unhide_hide` | 是 | `machine`: string |
| `spreadsheet_focus-mode_activate` |  | `machine`: string |
| `spreadsheet_full-screen_activate` |  | `machine`: string |
| `spreadsheet_ai-assistant_activate` |  | `machine`: string |
| `spreadsheet_actions_record` |  | `machine`: string |
| `spreadsheet_script_create` |  | `machine`: string |
| `spreadsheet_scripts_activate` |  | `machine`: string |
| `spreadsheet_code-editor_activate` |  | `machine`: string |
| `spreadsheet_script_run` |  | `machine`: string |
| `spreadsheet_button-that-runs-script_create` |  | `machine`: string |
| `spreadsheet_highlight-duplicates-sample-script_run` |  | `machine`: string |
| `spreadsheet_unhide-everything-sample-script_run` |  | `machine`: string |
| `spreadsheet_sum-each-column-sample-script_run` |  | `machine`: string |
| `spreadsheet_table-contents-sample-script_run` |  | `machine`: string |
| `spreadsheet_style-header-row-sample-script_run` |  | `machine`: string |
| `spreadsheet_remove-blank-rows-sample-script_run` |  | `machine`: string |
| `spreadsheet_script-reference_activate` |  | `machine`: string |
| `spreadsheet_paste-options-paste_paste` |  | `machine`: string |
| `spreadsheet_formulas_activate` |  | `machine`: string |
| `spreadsheet_formulas-number-formatting_activate` |  | `machine`: string |
| `spreadsheet_keep-source-formatting_activate` |  | `machine`: string |
| `spreadsheet_no-borders_activate` |  | `machine`: string |
| `spreadsheet_keep-source-column-widths_activate` |  | `machine`: string |
| `spreadsheet_transpose_activate` |  | `machine`: string |
| `spreadsheet_values_activate` |  | `machine`: string |
| `spreadsheet_values-number-formatting_activate` |  | `machine`: string |
| `spreadsheet_values-source-formatting_activate` |  | `machine`: string |
| `spreadsheet_formatting_activate` |  | `machine`: string |
| `spreadsheet_link_paste` |  | `machine`: string |
| `spreadsheet_picture_activate` |  | `machine`: string |
| `spreadsheet_linked-picture_activate` |  | `machine`: string |
| `spreadsheet_special_paste` |  | `machine`: string |
| `spreadsheet_default_activate` |  | `machine`: string |
| `spreadsheet_arial_activate` |  | `machine`: string |
| `spreadsheet_arial-black_activate` |  | `machine`: string |
| `spreadsheet_calibri_activate` |  | `machine`: string |
| `spreadsheet_cambria_activate` |  | `machine`: string |
| `spreadsheet_aharoni_activate` |  | `machine`: string |
| `spreadsheet_avenir-next-lt-pro_activate` |  | `machine`: string |
| `spreadsheet_century-gothic_activate` |  | `machine`: string |
| `spreadsheet_constantia_activate` |  | `machine`: string |
| `spreadsheet_corbel_activate` |  | `machine`: string |
| `spreadsheet_helvetica_activate` |  | `machine`: string |
| `spreadsheet_impact_activate` |  | `machine`: string |
| `spreadsheet_lato_activate` |  | `machine`: string |
| `spreadsheet_lato-light_activate` |  | `machine`: string |
| `spreadsheet_lucida-sans_activate` |  | `machine`: string |
| `spreadsheet_nyala_activate` |  | `machine`: string |
| `spreadsheet_sans-semibold_open` | 是 | `machine`: string |
| `spreadsheet_segoe-ui_activate` |  | `machine`: string |
| `spreadsheet_source-sans-pro_activate` |  | `machine`: string |
| `spreadsheet_tahoma_activate` |  | `machine`: string |
| `spreadsheet_verdana_activate` |  | `machine`: string |
| `spreadsheet_trebuchet-ms_activate` |  | `machine`: string |
| `spreadsheet_georgia_activate` |  | `machine`: string |
| `spreadsheet_rockwell_activate` |  | `machine`: string |
| `spreadsheet_times-roman_activate` |  | `machine`: string |
| `spreadsheet_garamond_activate` |  | `machine`: string |
| `spreadsheet_courier_activate` |  | `machine`: string |
| `spreadsheet_monospace_activate` |  | `machine`: string |
| `spreadsheet_comic-sans-ms_activate` |  | `machine`: string |
| `spreadsheet_document_search` | 是 | `machine`: string |
| `spreadsheet_selection_group` |  | `machine`: string |
| `spreadsheet_view_toggle-help` |  | `machine`: string |
| `spreadsheet_shortcut_key-q` |  | `machine`: string |
| `spreadsheet_document_save` |  | `machine`: string |

## documents（328 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `documents_search_search` | 是 | `target`*: string, `machine`: string |
| `documents_editing-mode_select` | 是 | `target`*: string, `machine`: string |
| `documents_account-menu_select` | 是 | `target`*: string, `machine`: string |
| `documents_font-size_select` | 是 | `target`*: string, `machine`: string |
| `documents_indent_select` | 是 | `target`*: string, `machine`: string |
| `documents_formatting_show` | 是 | `target`*: string, `machine`: string |
| `documents_heading_select` | 是 | `target`*: string, `machine`: string |
| `documents_left_select` | 是 | `target`*: string, `machine`: string |
| `documents_right_select` | 是 | `target`*: string, `machine`: string |
| `documents_top_select` | 是 | `target`*: string, `machine`: string |
| `documents_bottom_select` | 是 | `target`*: string, `machine`: string |
| `documents_spelling_select` | 是 | `target`*: string, `machine`: string |
| `documents_accessibility_select` | 是 | `target`*: string, `machine`: string |
| `documents_customize-quick-access-toolbar-formatting_show` | 是 | `target`*: string, `machine`: string |
| `documents_pen_select` | 是 | `target`*: string, `machine`: string |
| `documents_pencil_select` | 是 | `target`*: string, `machine`: string |
| `documents_highlighter_select` | 是 | `target`*: string, `machine`: string |
| `documents_check_run` |  | `target`*: string, `machine`: string |
| `documents_autosave_toggle` |  | `machine`: string |
| `documents_documents_activate` |  | `machine`: string |
| `documents_save_save` |  | `machine`: string |
| `documents_undo_undo` |  | `machine`: string |
| `documents_history_undo` |  | `machine`: string |
| `documents_redo_redo` |  | `machine`: string |
| `documents_print_print` | 是 | `machine`: string |
| `documents_customize-quick-access-toolbar_activate` |  | `machine`: string |
| `documents_edit_update` |  | `machine`: string |
| `documents_view_show` | 是 | `machine`: string |
| `documents_insert_create` |  | `machine`: string |
| `documents_format_activate` |  | `machine`: string |
| `documents_tools_activate` |  | `machine`: string |
| `documents_table_activate` |  | `machine`: string |
| `documents_window_activate` |  | `machine`: string |
| `documents_help_show` | 是 | `machine`: string |
| `documents_document-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_document-details_activate` |  | `machine`: string |
| `documents_not-saved-yet_activate` |  | `machine`: string |
| `documents_assistant_activate` |  | `machine`: string |
| `documents_comments_activate` |  | `machine`: string |
| `documents_share_share` |  | `machine`: string |
| `documents_file-2_activate` |  | `machine`: string |
| `documents_home_show` | 是 | `machine`: string |
| `documents_insert-2_create` |  | `machine`: string |
| `documents_draw_draw` |  | `machine`: string |
| `documents_design_show` | 是 | `machine`: string |
| `documents_layout_show` | 是 | `machine`: string |
| `documents_references_show` | 是 | `machine`: string |
| `documents_mailings_show` | 是 | `machine`: string |
| `documents_review_show` | 是 | `machine`: string |
| `documents_view-2_show` | 是 | `machine`: string |
| `documents_ribbon-display-options_activate` |  | `machine`: string |
| `documents_ribbon_collapse` | 是 | `machine`: string |
| `documents_paste_paste` |  | `machine`: string |
| `documents_options_paste` |  | `machine`: string |
| `documents_cut_cut` |  | `machine`: string |
| `documents_copy_copy` |  | `machine`: string |
| `documents_format-painter_activate` |  | `machine`: string |
| `documents_latin-font-family_activate` |  | `machine`: string |
| `documents_font-size-pt_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_font-sizes_activate` |  | `machine`: string |
| `documents_increase-font-size_activate` |  | `machine`: string |
| `documents_case_update` |  | `machine`: string |
| `documents_formatting_clear` |  | `machine`: string |
| `documents_bold_format` |  | `machine`: string |
| `documents_italic_format` |  | `machine`: string |
| `documents_underline_format` |  | `machine`: string |
| `documents_options_format` |  | `machine`: string |
| `documents_strikethrough_format` |  | `machine`: string |
| `documents_subscript_activate` |  | `machine`: string |
| `documents_superscript_activate` |  | `machine`: string |
| `documents_text-effects_activate` |  | `machine`: string |
| `documents_text-highlight_activate` |  | `machine`: string |
| `documents_text-color_activate` |  | `machine`: string |
| `documents_font-settings_activate` |  | `machine`: string |
| `documents_bulleted-list_activate` |  | `machine`: string |
| `documents_bullet-library_activate` |  | `machine`: string |
| `documents_numbered-list_activate` |  | `machine`: string |
| `documents_numbering-library_activate` |  | `machine`: string |
| `documents_multilevel-list_activate` |  | `machine`: string |
| `documents_increase-indent_activate` |  | `machine`: string |
| `documents_sort_sort` | 是 | `machine`: string |
| `documents_left_align` |  | `machine`: string |
| `documents_center_align` |  | `machine`: string |
| `documents_right_align` |  | `machine`: string |
| `documents_justify_activate` |  | `machine`: string |
| `documents_line-paragraph-spacing_activate` |  | `machine`: string |
| `documents_paragraph-shading_activate` |  | `machine`: string |
| `documents_borders_activate` |  | `machine`: string |
| `documents_border-options_activate` |  | `machine`: string |
| `documents_paragraph-settings_activate` |  | `machine`: string |
| `documents_normal_activate` |  | `machine`: string |
| `documents_title_activate` |  | `machine`: string |
| `documents_subtitle_activate` |  | `machine`: string |
| `documents_styles_show` | 是 | `machine`: string |
| `documents_styles-pane_activate` |  | `machine`: string |
| `documents_formatting-pane_activate` |  | `machine`: string |
| `documents_dictate_activate` |  | `machine`: string |
| `documents_find_search` | 是 | `machine`: string |
| `documents_options_search` | 是 | `machine`: string |
| `documents_replace_activate` |  | `machine`: string |
| `documents_select_select` | 是 | `machine`: string |
| `documents_left-indent_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_hanging-indent_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_first-line-indent_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_right-indent_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_document-text_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_go-ctrlg_activate` |  | `machine`: string |
| `documents_word-count_activate` |  | `machine`: string |
| `documents_language_activate` |  | `machine`: string |
| `documents_text-mode_toggle` |  | `machine`: string |
| `documents_focus_activate` |  | `machine`: string |
| `documents_read-mode_activate` |  | `machine`: string |
| `documents_layout_print` | 是 | `machine`: string |
| `documents_web-layout_activate` |  | `machine`: string |
| `documents_outline_activate` |  | `machine`: string |
| `documents_draft_activate` |  | `machine`: string |
| `documents_view_zoom-out` |  | `machine`: string |
| `documents_zoom-slider_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_view_zoom-` |  | `machine`: string |
| `documents_zoom_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_customize-quick-access-toolbar-documents_activate` |  | `machine`: string |
| `documents_customize-quick-access-toolbar-save_save` |  | `machine`: string |
| `documents_customize-quick-access-toolbar-undo_undo` |  | `machine`: string |
| `documents_customize-quick-access-toolbar-redo_redo` |  | `machine`: string |
| `documents_customize-quick-access-toolbar-print_print` | 是 | `machine`: string |
| `documents_document_create` |  | `machine`: string |
| `documents_open_open` | 是 | `machine`: string |
| `documents_customize-quick-access-toolbar-find_search` | 是 | `machine`: string |
| `documents_spelling_activate` |  | `machine`: string |
| `documents_as-pdf_save` |  | `machine`: string |
| `documents_comment_create` |  | `machine`: string |
| `documents_track-changes_activate` |  | `machine`: string |
| `documents_customize-quick-access-toolbar-word-count_activate` |  | `machine`: string |
| `documents_read-aloud_activate` |  | `machine`: string |
| `documents_repeat_activate` |  | `machine`: string |
| `documents_defaults_reset` |  | `machine`: string |
| `documents_document_close` | 是 | `machine`: string |
| `documents_file-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_version-history_activate` |  | `machine`: string |
| `documents_properties_activate` |  | `machine`: string |
| `documents_rename_rename` |  | `machine`: string |
| `documents_editingedit-document-directly_activate` |  | `machine`: string |
| `documents_reviewingedits-become-tracked-changes_activate` |  | `machine`: string |
| `documents_people_invite` |  | `machine`: string |
| `documents_link_copy` |  | `machine`: string |
| `documents_publish-web_activate` |  | `machine`: string |
| `documents_copy-docx_send` |  | `machine`: string |
| `documents_as-pdf_send` |  | `machine`: string |
| `documents_system_toggle` |  | `machine`: string |
| `documents_light_toggle` |  | `machine`: string |
| `documents_dark_toggle` |  | `machine`: string |
| `documents_dark-pagedark-paper-dark-theme_activate` |  | `machine`: string |
| `documents_measurement-unitsinches_activate` |  | `machine`: string |
| `documents_capitalize-first-letter-sentences_activate` |  | `machine`: string |
| `documents_keyboard-shortcuts_activate` |  | `machine`: string |
| `documents_documents_show` | 是 | `machine`: string |
| `documents_document_previous` | 是 | `machine`: string |
| `documents_file-open_open` | 是 | `machine`: string |
| `documents_info_show` | 是 | `machine`: string |
| `documents_file-save_save` |  | `machine`: string |
| `documents_file-print_print` | 是 | `machine`: string |
| `documents_file-share_share` |  | `machine`: string |
| `documents_export_export` |  | `machine`: string |
| `documents_close_close` | 是 | `machine`: string |
| `documents_preferences_activate` |  | `machine`: string |
| `documents_title_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_subject_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_author_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_keywords_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_category_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_status_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_comments_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_properties_save` |  | `machine`: string |
| `documents_only_show` | 是 | `machine`: string |
| `documents_cover-page_activate` |  | `machine`: string |
| `documents_blank-page_activate` |  | `machine`: string |
| `documents_page-break_activate` |  | `machine`: string |
| `documents_table_create` |  | `machine`: string |
| `documents_pictures_activate` |  | `machine`: string |
| `documents_shapes_activate` |  | `machine`: string |
| `documents_icons_activate` |  | `machine`: string |
| `documents_diagram_activate` |  | `machine`: string |
| `documents_chart_activate` |  | `machine`: string |
| `documents_or-edit-link_create` |  | `machine`: string |
| `documents_bookmarks_activate` |  | `machine`: string |
| `documents_insert-comment_create` |  | `machine`: string |
| `documents_header_activate` |  | `machine`: string |
| `documents_footer_activate` |  | `machine`: string |
| `documents_page-number_activate` |  | `machine`: string |
| `documents_text-box_activate` |  | `machine`: string |
| `documents_quick-parts_activate` |  | `machine`: string |
| `documents_wordart_activate` |  | `machine`: string |
| `documents_drop-cap_activate` |  | `machine`: string |
| `documents_signature-line_activate` |  | `machine`: string |
| `documents_date-time_activate` |  | `machine`: string |
| `documents_object_activate` |  | `machine`: string |
| `documents_symbols_activate` |  | `machine`: string |
| `documents_lasso-select_activate` |  | `machine`: string |
| `documents_eraser_activate` |  | `machine`: string |
| `documents_eraser-options_activate` |  | `machine`: string |
| `documents_pen_create` |  | `machine`: string |
| `documents_touch_draw` |  | `machine`: string |
| `documents_ruler_activate` |  | `machine`: string |
| `documents_ink-shape_activate` |  | `machine`: string |
| `documents_ink-math_activate` |  | `machine`: string |
| `documents_drawing-canvas_activate` |  | `machine`: string |
| `documents_ink-replay_activate` |  | `machine`: string |
| `documents_ink_hide` | 是 | `machine`: string |
| `documents_themes_activate` |  | `machine`: string |
| `documents_default-style-set_activate` |  | `machine`: string |
| `documents_crisp-style-set_activate` |  | `machine`: string |
| `documents_classic-style-set_activate` |  | `machine`: string |
| `documents_banner-style-set_activate` |  | `machine`: string |
| `documents_minimal-style-set_activate` |  | `machine`: string |
| `documents_accent-bar-style-set_activate` |  | `machine`: string |
| `documents_centered-style-set_activate` |  | `machine`: string |
| `documents_contrast-style-set_format` |  | `machine`: string |
| `documents_style-sets_show` | 是 | `machine`: string |
| `documents_theme-colors_activate` |  | `machine`: string |
| `documents_theme-fonts_activate` |  | `machine`: string |
| `documents_paragraph-spacing_activate` |  | `machine`: string |
| `documents_theme-effects_activate` |  | `machine`: string |
| `documents_set-as-default_activate` |  | `machine`: string |
| `documents_watermark_activate` |  | `machine`: string |
| `documents_page-color_activate` |  | `machine`: string |
| `documents_page-borders_activate` |  | `machine`: string |
| `documents_margins_activate` |  | `machine`: string |
| `documents_orientation_activate` |  | `machine`: string |
| `documents_size_activate` |  | `machine`: string |
| `documents_columns_activate` |  | `machine`: string |
| `documents_breaks_activate` |  | `machine`: string |
| `documents_line-numbers_activate` |  | `machine`: string |
| `documents_hyphenation_activate` |  | `machine`: string |
| `documents_page-setup_activate` |  | `machine`: string |
| `documents_indent-left_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_indent-right_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_space-before-paragraph-pt_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_space-after-paragraph-pt_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_position_activate` |  | `machine`: string |
| `documents_wrap-text_activate` |  | `machine`: string |
| `documents_bring-forward_activate` |  | `machine`: string |
| `documents_bring-forward-options_activate` |  | `machine`: string |
| `documents_backward_send` |  | `machine`: string |
| `documents_backward-options_send` |  | `machine`: string |
| `documents_selection-pane_activate` |  | `machine`: string |
| `documents_align_align` |  | `machine`: string |
| `documents_group_group` |  | `machine`: string |
| `documents_rotate_rotate` |  | `machine`: string |
| `documents_table-contents_activate` |  | `machine`: string |
| `documents_text_create` |  | `machine`: string |
| `documents_table_update` |  | `machine`: string |
| `documents_fields_update` |  | `machine`: string |
| `documents_footnote_create` |  | `machine`: string |
| `documents_endnote_create` |  | `machine`: string |
| `documents_footnote_next` | 是 | `machine`: string |
| `documents_notes_show` | 是 | `machine`: string |
| `documents_footnote-endnote-settings_activate` |  | `machine`: string |
| `documents_smart-lookup_activate` |  | `machine`: string |
| `documents_citation_create` |  | `machine`: string |
| `documents_manage-sources_activate` |  | `machine`: string |
| `documents_citation-style_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_bibliography_activate` |  | `machine`: string |
| `documents_caption_create` |  | `machine`: string |
| `documents_table-figures_create` |  | `machine`: string |
| `documents_table-figures_update` |  | `machine`: string |
| `documents_cross-reference_activate` |  | `machine`: string |
| `documents_index_activate` |  | `machine`: string |
| `documents_table-authorities_activate` |  | `machine`: string |
| `documents_create_create` |  | `machine`: string |
| `documents_mail-merge_start` |  | `machine`: string |
| `documents_recipients_select` | 是 | `machine`: string |
| `documents_recipient-list_update` |  | `machine`: string |
| `documents_highlight-merge-fields_activate` |  | `machine`: string |
| `documents_address-block_activate` |  | `machine`: string |
| `documents_greeting-line_activate` |  | `machine`: string |
| `documents_merge-field_create` |  | `machine`: string |
| `documents_rules_activate` |  | `machine`: string |
| `documents_match-fields_activate` |  | `machine`: string |
| `documents_labels_update` |  | `machine`: string |
| `documents_preview-results_activate` |  | `machine`: string |
| `documents_first-record_activate` |  | `machine`: string |
| `documents_record_previous` | 是 | `machine`: string |
| `documents_go-record_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `documents_record_next` | 是 | `machine`: string |
| `documents_last-record_activate` |  | `machine`: string |
| `documents_recipient_search` | 是 | `machine`: string |
| `documents_finish-merge_activate` |  | `machine`: string |
| `documents_editor_activate` |  | `machine`: string |
| `documents_spelling-options_activate` |  | `machine`: string |
| `documents_thesaurus_activate` |  | `machine`: string |
| `documents_review-word-count_activate` |  | `machine`: string |
| `documents_review-read-aloud_activate` |  | `machine`: string |
| `documents_accessibility_run` |  | `machine`: string |
| `documents_review-language_activate` |  | `machine`: string |
| `documents_comment_delete` |  | `machine`: string |
| `documents_options_delete` |  | `machine`: string |
| `documents_comment_previous` | 是 | `machine`: string |
| `documents_comment_next` | 是 | `machine`: string |
| `documents_resolve-comment_activate` |  | `machine`: string |
| `documents_comments_show` | 是 | `machine`: string |
| `documents_comments-options_show` | 是 | `machine`: string |
| `documents_tracking_activate` |  | `machine`: string |
| `documents_accept_activate` |  | `machine`: string |
| `documents_accept-options_activate` |  | `machine`: string |
| `documents_reject_activate` |  | `machine`: string |
| `documents_reject-options_activate` |  | `machine`: string |
| `documents_change_previous` | 是 | `machine`: string |
| `documents_change_next` | 是 | `machine`: string |
| `documents_compare_activate` |  | `machine`: string |
| `documents_restrict-editing_activate` |  | `machine`: string |

## presentation（301 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `presentation_search_search` | 是 | `target`*: string, `machine`: string |
| `presentation_local_select` | 是 | `target`*: string, `machine`: string |
| `presentation_font-size_select` | 是 | `target`*: string, `machine`: string |
| `presentation_list-level_select` | 是 | `target`*: string, `machine`: string |
| `presentation_slide-1_select` | 是 | `target`*: string, `machine`: string |
| `presentation_options_select` | 是 | `target`*: string, `machine`: string |
| `presentation_centered-title-select-edit_select` | 是 | `target`*: string, `machine`: string |
| `presentation_subtitle-select-edit_select` | 是 | `target`*: string, `machine`: string |
| `presentation_draft-6-slide-pitch-deck_select` | 是 | `target`*: string, `machine`: string |
| `presentation_outline-talk-topic-i-give-you_select` | 是 | `target`*: string, `machine`: string |
| `presentation_accessibility_select` | 是 | `target`*: string, `machine`: string |
| `presentation_pen_select` | 是 | `target`*: string, `machine`: string |
| `presentation_pencil_select` | 是 | `target`*: string, `machine`: string |
| `presentation_highlighter_select` | 是 | `target`*: string, `machine`: string |
| `presentation_duration_select` | 是 | `target`*: string, `machine`: string |
| `presentation_advance-after_select` | 是 | `target`*: string, `machine`: string |
| `presentation_delay_select` | 是 | `target`*: string, `machine`: string |
| `presentation_content_dismiss` | 是 | `machine`: string |
| `presentation_presentations_previous` | 是 | `machine`: string |
| `presentation_puter_save` |  | `machine`: string |
| `presentation_undo_undo` |  | `machine`: string |
| `presentation_redo_redo` |  | `machine`: string |
| `presentation_edit_update` |  | `machine`: string |
| `presentation_view_show` | 是 | `machine`: string |
| `presentation_insert_create` |  | `machine`: string |
| `presentation_format_activate` |  | `machine`: string |
| `presentation_arrange_activate` |  | `machine`: string |
| `presentation_slide_activate` |  | `machine`: string |
| `presentation_tools_activate` |  | `machine`: string |
| `presentation_slide-show_activate` |  | `machine`: string |
| `presentation_help_show` | 是 | `machine`: string |
| `presentation_untitled-presentation_rename` |  | `machine`: string |
| `presentation_save_save` |  | `machine`: string |
| `presentation_ask-ai_activate` |  | `machine`: string |
| `presentation_present_activate` |  | `machine`: string |
| `presentation_home_show` | 是 | `machine`: string |
| `presentation_insert-2_create` |  | `machine`: string |
| `presentation_draw_draw` |  | `machine`: string |
| `presentation_design_show` | 是 | `machine`: string |
| `presentation_transitions_show` | 是 | `machine`: string |
| `presentation_animations_show` | 是 | `machine`: string |
| `presentation_slide-show_show` | 是 | `machine`: string |
| `presentation_record_record` |  | `machine`: string |
| `presentation_review_show` | 是 | `machine`: string |
| `presentation_view-2_show` | 是 | `machine`: string |
| `presentation_ribbon_collapse` | 是 | `machine`: string |
| `presentation_paste_paste` |  | `machine`: string |
| `presentation_options_paste` |  | `machine`: string |
| `presentation_cut_cut` |  | `machine`: string |
| `presentation_copy_copy` |  | `machine`: string |
| `presentation_format-painter_activate` |  | `machine`: string |
| `presentation_slide_create` |  | `machine`: string |
| `presentation_slide-layouts_create` |  | `machine`: string |
| `presentation_layout_activate` |  | `machine`: string |
| `presentation_reset_reset` |  | `machine`: string |
| `presentation_section_activate` |  | `machine`: string |
| `presentation_font_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_font-list_activate` |  | `machine`: string |
| `presentation_font-size_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_font-size-list_activate` |  | `machine`: string |
| `presentation_increase-font-size_activate` |  | `machine`: string |
| `presentation_formatting_clear` |  | `machine`: string |
| `presentation_font-settings_activate` |  | `machine`: string |
| `presentation_bold_format` |  | `machine`: string |
| `presentation_italic_format` |  | `machine`: string |
| `presentation_underline_format` |  | `machine`: string |
| `presentation_strikethrough_format` |  | `machine`: string |
| `presentation_superscript_activate` |  | `machine`: string |
| `presentation_subscript_activate` |  | `machine`: string |
| `presentation_character-spacing_activate` |  | `machine`: string |
| `presentation_case_update` |  | `machine`: string |
| `presentation_text-highlight-color_activate` |  | `machine`: string |
| `presentation_highlight-colors_activate` |  | `machine`: string |
| `presentation_font-color_activate` |  | `machine`: string |
| `presentation_font-colors_activate` |  | `machine`: string |
| `presentation_bullets_activate` |  | `machine`: string |
| `presentation_bullet-styles_activate` |  | `machine`: string |
| `presentation_numbering_activate` |  | `machine`: string |
| `presentation_numbering-styles_activate` |  | `machine`: string |
| `presentation_increase-list-level_activate` |  | `machine`: string |
| `presentation_line-spacing_activate` |  | `machine`: string |
| `presentation_columns_activate` |  | `machine`: string |
| `presentation_paragraph-settings_activate` |  | `machine`: string |
| `presentation_left_align` |  | `machine`: string |
| `presentation_center_activate` |  | `machine`: string |
| `presentation_right_align` |  | `machine`: string |
| `presentation_justify_activate` |  | `machine`: string |
| `presentation_text-direction_activate` |  | `machine`: string |
| `presentation_text_align` |  | `machine`: string |
| `presentation_convert-smartart_activate` |  | `machine`: string |
| `presentation_insert-3_create` |  | `machine`: string |
| `presentation_drawing_activate` |  | `machine`: string |
| `presentation_editing_activate` |  | `machine`: string |
| `presentation_designer_activate` |  | `machine`: string |
| `presentation_slide-thumbnails_resize` |  | `machine`: string |
| `presentation_notes_resize` |  | `machine`: string |
| `presentation_speaker-notes_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_assistant_resize` |  | `machine`: string |
| `presentation_chat_create` |  | `machine`: string |
| `presentation_assistant-settings_activate` |  | `machine`: string |
| `presentation_assistant_close` | 是 | `machine`: string |
| `presentation_turn-notes-into-slides_activate` |  | `machine`: string |
| `presentation_message-assistant_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_send_send` |  | `machine`: string |
| `presentation_english-united-states_activate` |  | `machine`: string |
| `presentation_notes_activate` |  | `machine`: string |
| `presentation_comments_activate` |  | `machine`: string |
| `presentation_normal_activate` |  | `machine`: string |
| `presentation_slide-sorter_activate` |  | `machine`: string |
| `presentation_reading-view_activate` |  | `machine`: string |
| `presentation_slide-show-2_activate` |  | `machine`: string |
| `presentation_view_zoom-out` |  | `machine`: string |
| `presentation_zoom_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_view_zoom-` |  | `machine`: string |
| `presentation_view_zoom-level` |  | `machine`: string |
| `presentation_fit-slide-current-window_activate` |  | `machine`: string |
| `presentation_close_close` | 是 | `machine`: string |
| `presentation_presentation-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_cancel_cancel` | 是 | `machine`: string |
| `presentation_appearance_activate` |  | `machine`: string |
| `presentation_keyboard-shortcuts_activate` |  | `machine`: string |
| `presentation_table_activate` |  | `machine`: string |
| `presentation_pictures_activate` |  | `machine`: string |
| `presentation_picture-sources_activate` |  | `machine`: string |
| `presentation_screenshot_activate` |  | `machine`: string |
| `presentation_screenshot-options_activate` |  | `machine`: string |
| `presentation_photo-album_activate` |  | `machine`: string |
| `presentation_shapes_activate` |  | `machine`: string |
| `presentation_icons_activate` |  | `machine`: string |
| `presentation_smartart_activate` |  | `machine`: string |
| `presentation_chart_activate` |  | `machine`: string |
| `presentation_zoom_zoom` | 是 | `machine`: string |
| `presentation_link_activate` |  | `machine`: string |
| `presentation_action_activate` |  | `machine`: string |
| `presentation_action-options_activate` |  | `machine`: string |
| `presentation_comment_activate` |  | `machine`: string |
| `presentation_text-box_activate` |  | `machine`: string |
| `presentation_header-footer_activate` |  | `machine`: string |
| `presentation_wordart_activate` |  | `machine`: string |
| `presentation_date-time_activate` |  | `machine`: string |
| `presentation_slide-number_activate` |  | `machine`: string |
| `presentation_object_activate` |  | `machine`: string |
| `presentation_symbols_activate` |  | `machine`: string |
| `presentation_media_activate` |  | `machine`: string |
| `presentation_select_select` | 是 | `machine`: string |
| `presentation_eraser_activate` |  | `machine`: string |
| `presentation_eraser-options_activate` |  | `machine`: string |
| `presentation_lasso-select_activate` |  | `machine`: string |
| `presentation_pen_create` |  | `machine`: string |
| `presentation_ink-text_activate` |  | `machine`: string |
| `presentation_ink-shape_activate` |  | `machine`: string |
| `presentation_ink-shape-options_activate` |  | `machine`: string |
| `presentation_ink-math_activate` |  | `machine`: string |
| `presentation_ink-replay_activate` |  | `machine`: string |
| `presentation_ruler_activate` |  | `machine`: string |
| `presentation_touch_draw` |  | `machine`: string |
| `presentation_default-theme_activate` |  | `machine`: string |
| `presentation_paper_activate` |  | `machine`: string |
| `presentation_studio_activate` |  | `machine`: string |
| `presentation_cobalt_activate` |  | `machine`: string |
| `presentation_row-themes_previous` | 是 | `machine`: string |
| `presentation_row-themes_next` | 是 | `machine`: string |
| `presentation_themes_show` | 是 | `machine`: string |
| `presentation_default_activate` |  | `machine`: string |
| `presentation_default-dark_activate` |  | `machine`: string |
| `presentation_default-accents-turned_activate` |  | `machine`: string |
| `presentation_default-accents-turned-twice_activate` |  | `machine`: string |
| `presentation_row-variants_previous` | 是 | `machine`: string |
| `presentation_row-variants_next` | 是 | `machine`: string |
| `presentation_variants_show` | 是 | `machine`: string |
| `presentation_colors_activate` |  | `machine`: string |
| `presentation_fonts_activate` |  | `machine`: string |
| `presentation_effects_activate` |  | `machine`: string |
| `presentation_background-styles_activate` |  | `machine`: string |
| `presentation_slide-size_activate` |  | `machine`: string |
| `presentation_format-background_activate` |  | `machine`: string |
| `presentation_hide-background-graphics_toggle` |  | `machine`: string |
| `presentation_design-ideas_activate` |  | `machine`: string |
| `presentation_preview_activate` |  | `machine`: string |
| `presentation_none_activate` |  | `machine`: string |
| `presentation_morph_activate` |  | `machine`: string |
| `presentation_fade_activate` |  | `machine`: string |
| `presentation_push_activate` |  | `machine`: string |
| `presentation_wipe_activate` |  | `machine`: string |
| `presentation_split_activate` |  | `machine`: string |
| `presentation_reveal_activate` |  | `machine`: string |
| `presentation_transitions-cut_cut` |  | `machine`: string |
| `presentation_random-bars_activate` |  | `machine`: string |
| `presentation_row-transitions_previous` | 是 | `machine`: string |
| `presentation_row-transitions_next` | 是 | `machine`: string |
| `presentation_transitions-2_show` | 是 | `machine`: string |
| `presentation_effect-options_activate` |  | `machine`: string |
| `presentation_sound_activate` |  | `machine`: string |
| `presentation_duration_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_increase-duration_activate` |  | `machine`: string |
| `presentation_apply_confirm` |  | `machine`: string |
| `presentation_mouse-click_toggle` |  | `machine`: string |
| `presentation_after_toggle` |  | `machine`: string |
| `presentation_advance-after-seconds_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_increase-advance-after_activate` |  | `machine`: string |
| `presentation_preview-options_activate` |  | `machine`: string |
| `presentation_appear_activate` |  | `machine`: string |
| `presentation_fly_activate` |  | `machine`: string |
| `presentation_float_activate` |  | `machine`: string |
| `presentation_shape_activate` |  | `machine`: string |
| `presentation_row-animations_previous` | 是 | `machine`: string |
| `presentation_row-animations_next` | 是 | `machine`: string |
| `presentation_animations-2_show` | 是 | `machine`: string |
| `presentation_animation_create` |  | `machine`: string |
| `presentation_animation-pane_activate` |  | `machine`: string |
| `presentation_trigger_activate` |  | `machine`: string |
| `presentation_animation-painter_activate` |  | `machine`: string |
| `presentation_start_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_list_start` |  | `machine`: string |
| `presentation_delay_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `presentation_increase-delay_activate` |  | `machine`: string |
| `presentation_earlier_move` |  | `machine`: string |
| `presentation_later_move` |  | `machine`: string |
| `presentation_from-start_play` |  | `machine`: string |
| `presentation_from-current-slide_play` |  | `machine`: string |
| `presentation_presenter-view_activate` |  | `machine`: string |
| `presentation_custom-show_activate` |  | `machine`: string |
| `presentation_set-up-slide-show_activate` |  | `machine`: string |
| `presentation_slide_hide` | 是 | `machine`: string |
| `presentation_rehearse-timings_activate` |  | `machine`: string |
| `presentation_slide-show-record_record` |  | `machine`: string |
| `presentation_options_record` |  | `machine`: string |
| `presentation_play-narrations_toggle` |  | `machine`: string |
| `presentation_use-timings_toggle` |  | `machine`: string |
| `presentation_show-media-controls_toggle` |  | `machine`: string |
| `presentation_always-use-subtitles_toggle` |  | `machine`: string |
| `presentation_subtitle-settings_activate` |  | `machine`: string |
| `presentation_live-camera_activate` |  | `machine`: string |
| `presentation_from-beginning_activate` |  | `machine`: string |
| `presentation_from-current-slide_activate` |  | `machine`: string |
| `presentation_recording_clear` |  | `machine`: string |
| `presentation_camera_reset` |  | `machine`: string |
| `presentation_video_export` |  | `machine`: string |
| `presentation_spelling_activate` |  | `machine`: string |
| `presentation_thesaurus_activate` |  | `machine`: string |
| `presentation_accessibility_run` |  | `machine`: string |
| `presentation_accessibility-options_activate` |  | `machine`: string |
| `presentation_alt-text_activate` |  | `machine`: string |
| `presentation_translate_activate` |  | `machine`: string |
| `presentation_language_activate` |  | `machine`: string |
| `presentation_comment_create` |  | `machine`: string |
| `presentation_delete_delete` |  | `machine`: string |
| `presentation_previous_previous` | 是 | `machine`: string |
| `presentation_next_next` | 是 | `machine`: string |
| `presentation_comments_show` | 是 | `machine`: string |
| `presentation_comments-options_show` | 是 | `machine`: string |
| `presentation_compare_activate` |  | `machine`: string |
| `presentation_always-open-read-only_activate` |  | `machine`: string |
| `presentation_outline-view_activate` |  | `machine`: string |
| `presentation_notes-page_activate` |  | `machine`: string |
| `presentation_slide-master_activate` |  | `machine`: string |
| `presentation_handout-master_activate` |  | `machine`: string |
| `presentation_notes-master_activate` |  | `machine`: string |
| `presentation_ruler_toggle` |  | `machine`: string |
| `presentation_gridlines_toggle` |  | `machine`: string |
| `presentation_guides_toggle` |  | `machine`: string |
| `presentation_view-notes_activate` |  | `machine`: string |
| `presentation_grid-settings_activate` |  | `machine`: string |
| `presentation_fit-window_activate` |  | `machine`: string |
| `presentation_color_activate` |  | `machine`: string |
| `presentation_grayscale_activate` |  | `machine`: string |
| `presentation_black-white_activate` |  | `machine`: string |
| `presentation_slide-thumbnails_activate` |  | `machine`: string |
| `presentation_format-pane_activate` |  | `machine`: string |
| `presentation_ai-assistant_activate` |  | `machine`: string |
| `presentation_pastectrlv_activate` |  | `machine`: string |
| `presentation_as-text-only_paste` |  | `machine`: string |
| `presentation_duplicatectrld_activate` |  | `machine`: string |
| `presentation_special_paste` |  | `machine`: string |
| `presentation_match-formatting_paste` |  | `machine`: string |
| `presentation_selection_select-all` |  | `machine`: string |
| `presentation_selection_duplicate` |  | `machine`: string |
| `presentation_shortcut_key-j` |  | `machine`: string |
| `presentation_command-palette_show` | 是 | `machine`: string |
| `presentation_document_open` | 是 | `machine`: string |
| `presentation_document_print` | 是 | `machine`: string |
| `presentation_document_save` |  | `machine`: string |
| `presentation_clipboard_paste` |  | `machine`: string |

## whiteboard（44 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `whiteboard_board-library_select` | 是 | `target`*: string, `machine`: string |
| `whiteboard_board-library-2_select` | 是 | `target`*: string, `machine`: string |
| `whiteboard_main_select` | 是 | `target`*: string, `machine`: string |
| `whiteboard_whiteboard-home_show` | 是 | `machine`: string |
| `whiteboard_trash_delete` |  | `machine`: string |
| `whiteboard_organization_join` |  | `machine`: string |
| `whiteboard_set-up-organization_activate` |  | `machine`: string |
| `whiteboard_feedback_send` |  | `machine`: string |
| `whiteboard_language_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `whiteboard_appearance_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `whiteboard_powered-by-puter_show` | 是 | `machine`: string |
| `whiteboard_command-palette-ctrl-cmd-k_activate` |  | `machine`: string |
| `whiteboard_shared-board_join` |  | `machine`: string |
| `whiteboard_training_show` | 是 | `machine`: string |
| `whiteboard_keyboard-shortcuts_activate` |  | `machine`: string |
| `whiteboard_account-menu-local_activate` |  | `machine`: string |
| `whiteboard_browse-templates_activate` |  | `machine`: string |
| `whiteboard_blank-boarda-fresh-start_activate` |  | `machine`: string |
| `whiteboard_board_create` |  | `machine`: string |
| `whiteboard_search-boards_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `whiteboard_sort-boards_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `whiteboard_board-file_import` |  | `machine`: string |
| `whiteboard_migrate-from-miro_activate` |  | `machine`: string |
| `whiteboard_grid-view_activate` |  | `machine`: string |
| `whiteboard_list-view_activate` |  | `machine`: string |
| `whiteboard_keyboard-shortcuts-2_activate` |  | `machine`: string |

## pdf（101 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `pdf_notes-highlight-text-up-pages_leave` |  | `target`*: string, `machine`: string |
| `pdf_fillable-fields_create` |  | `target`*: string, `machine`: string |
| `pdf_tools_select` | 是 | `target`*: string, `machine`: string |
| `pdf_go-page_select` | 是 | `target`*: string, `machine`: string |
| `pdf_page-actions_select` | 是 | `target`*: string, `machine`: string |
| `pdf_pages_select` | 是 | `target`*: string, `machine`: string |
| `pdf_current-page_select` | 是 | `target`*: string, `machine`: string |
| `pdf_content_dismiss` | 是 | `machine`: string |
| `pdf_pdfs_previous` | 是 | `machine`: string |
| `pdf_edit_update` |  | `machine`: string |
| `pdf_view_show` | 是 | `machine`: string |
| `pdf_page_activate` |  | `machine`: string |
| `pdf_insert_create` |  | `machine`: string |
| `pdf_untitled-pdf_rename` |  | `machine`: string |
| `pdf_settings_show` | 是 | `machine`: string |
| `pdf_tools_activate` |  | `machine`: string |
| `pdf_edit-2_update` |  | `machine`: string |
| `pdf_comment_activate` |  | `machine`: string |
| `pdf_export_export` |  | `machine`: string |
| `pdf_fill-sign_activate` |  | `machine`: string |
| `pdf_text-or-tools_search` | 是 | `machine`: string |
| `pdf_undo_undo` |  | `machine`: string |
| `pdf_redo_redo` |  | `machine`: string |
| `pdf_download_export` |  | `machine`: string |
| `pdf_puter_save` |  | `machine`: string |
| `pdf_tools-panel_close` | 是 | `machine`: string |
| `pdf_pdf-or-its-pages-another-format_save` |  | `machine`: string |
| `pdf_pdf-or-turn-pictures-into-pdf-pages_start` |  | `machine`: string |
| `pdf_combine-pdfs-pictures-into-one-pdf_activate` |  | `machine`: string |
| `pdf_fill-forms-add-signature_activate` |  | `machine`: string |
| `pdf_make-file-smaller-by-shrinking-its-pictu_activate` |  | `machine`: string |
| `pdf_more_show` | 是 | `machine`: string |
| `pdf_select_select` | 是 | `machine`: string |
| `pdf_hand_activate` |  | `machine`: string |
| `pdf_text_activate` |  | `machine`: string |
| `pdf_highlight_activate` |  | `machine`: string |
| `pdf_draw_draw` |  | `machine`: string |
| `pdf_shape_activate` |  | `machine`: string |
| `pdf_note_activate` |  | `machine`: string |
| `pdf_image_activate` |  | `machine`: string |
| `pdf_sign_sign` |  | `machine`: string |
| `pdf_fill-forms_activate` |  | `machine`: string |
| `pdf_pdf-page-view_activate` |  | `machine`: string |
| `pdf_page_previous` | 是 | `machine`: string |
| `pdf_page-number_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pdf_page_next` | 是 | `machine`: string |
| `pdf_view_zoom-out` |  | `machine`: string |
| `pdf_zoom_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pdf_view_zoom-` |  | `machine`: string |
| `pdf_pages_show` | 是 | `machine`: string |
| `pdf_comments_show` | 是 | `machine`: string |
| `pdf_attachments_show` | 是 | `machine`: string |
| `pdf_pages-panel_toggle` |  | `machine`: string |
| `pdf_pages-panel_close` | 是 | `machine`: string |
| `pdf_dialog_close` | 是 | `machine`: string |
| `pdf_appearance_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pdf_keyboard-shortcuts_activate` |  | `machine`: string |
| `pdf_pdf-editor_show` | 是 | `machine`: string |
| `pdf_tools_previous` | 是 | `machine`: string |
| `pdf_text_create` |  | `machine`: string |
| `pdf_image_create` |  | `machine`: string |
| `pdf_link_create` |  | `machine`: string |
| `pdf_text-images_update` |  | `machine`: string |
| `pdf_pages_crop` |  | `machine`: string |
| `pdf_header-footer_activate` |  | `machine`: string |
| `pdf_watermark_activate` |  | `machine`: string |
| `pdf_page-numbers_activate` |  | `machine`: string |
| `pdf_bates-numbering_activate` |  | `machine`: string |
| `pdf_headers-footers_delete` |  | `machine`: string |
| `pdf_watermarks_delete` |  | `machine`: string |
| `pdf_find-pdf_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pdf_match_previous` | 是 | `machine`: string |
| `pdf_match_next` | 是 | `machine`: string |
| `pdf_search_close` | 是 | `machine`: string |
| `pdf_pages_toggle` |  | `machine`: string |
| `pdf_page-range_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pdf_cancel_cancel` | 是 | `machine`: string |
| `pdf_print_print` | 是 | `machine`: string |
| `pdf_comments-panel_close` | 是 | `machine`: string |
| `pdf_attachments-panel_close` | 是 | `machine`: string |
| `pdf_attach-file_activate` |  | `machine`: string |
| `pdf_selection_select-all` |  | `machine`: string |
| `pdf_selection_group-shift` |  | `machine`: string |

## notes（153 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `notes_font-size_select` | 是 | `target`*: string, `machine`: string |
| `notes_indent-position_select` | 是 | `target`*: string, `machine`: string |
| `notes_notebook_select` | 是 | `target`*: string, `machine`: string |
| `notes_section_create` |  | `target`*: string, `machine`: string |
| `notes_heading-alt_select` | 是 | `target`*: string, `machine`: string |
| `notes_normalctrlalt_select` | 是 | `target`*: string, `machine`: string |
| `notes_doctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_importantctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_questionctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_remember_select` | 是 | `target`*: string, `machine`: string |
| `notes_definitionctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_highlightctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_contactctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_addressctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_phone-numberctrl_select` | 是 | `target`*: string, `machine`: string |
| `notes_source_select` | 是 | `target`*: string, `machine`: string |
| `notes_do-priority_select` | 是 | `target`*: string, `machine`: string |
| `notes_tagctrl_delete` |  | `target`*: string, `machine`: string |
| `notes_undo_undo` |  | `machine`: string |
| `notes_redo_redo` |  | `machine`: string |
| `notes_commands_show` | 是 | `machine`: string |
| `notes_changes-saved-sync-now_activate` |  | `machine`: string |
| `notes_share_share` |  | `machine`: string |
| `notes_home_show` | 是 | `machine`: string |
| `notes_insert_create` |  | `machine`: string |
| `notes_draw_draw` |  | `machine`: string |
| `notes_view_show` | 是 | `machine`: string |
| `notes_help_show` | 是 | `machine`: string |
| `notes_tell-me-what-you-want-do_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `notes_ribbon_collapse` | 是 | `machine`: string |
| `notes_paste_paste` |  | `machine`: string |
| `notes_cut_cut` |  | `machine`: string |
| `notes_copy_copy` |  | `machine`: string |
| `notes_format-painter_activate` |  | `machine`: string |
| `notes_font_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `notes_font-list_activate` |  | `machine`: string |
| `notes_font-size_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `notes_font-size-list_activate` |  | `machine`: string |
| `notes_increase-font-size_activate` |  | `machine`: string |
| `notes_bold_format` |  | `machine`: string |
| `notes_italic_format` |  | `machine`: string |
| `notes_underline_format` |  | `machine`: string |
| `notes_strikethrough_format` |  | `machine`: string |
| `notes_subscript_activate` |  | `machine`: string |
| `notes_superscript_activate` |  | `machine`: string |
| `notes_text-highlight-color_activate` |  | `machine`: string |
| `notes_text-highlight-color-options_activate` |  | `machine`: string |
| `notes_font-color_activate` |  | `machine`: string |
| `notes_font-color-options_activate` |  | `machine`: string |
| `notes_formatting_clear` |  | `machine`: string |
| `notes_bullets_activate` |  | `machine`: string |
| `notes_bullets-options_activate` |  | `machine`: string |
| `notes_numbering_activate` |  | `machine`: string |
| `notes_numbering-options_activate` |  | `machine`: string |
| `notes_increase-indent-position_activate` |  | `machine`: string |
| `notes_paragraph-alignment_activate` |  | `machine`: string |
| `notes_paragraph-up_move` |  | `machine`: string |
| `notes_paragraph-down_move` |  | `machine`: string |
| `notes_styles_activate` |  | `machine`: string |
| `notes_do-tag_activate` |  | `machine`: string |
| `notes_tags_activate` |  | `machine`: string |
| `notes_tags_search` | 是 | `machine`: string |
| `notes_dictate_activate` |  | `machine`: string |
| `notes_assist_activate` |  | `machine`: string |
| `notes_email-page_activate` |  | `machine`: string |
| `notes_notebooks_activate` |  | `machine`: string |
| `notes_search_search` | 是 | `machine`: string |
| `notes_recent-notes_activate` |  | `machine`: string |
| `notes_account_activate` |  | `machine`: string |
| `notes_quick-notes_activate` |  | `machine`: string |
| `notes_section-2_create` |  | `machine`: string |
| `notes_sections-pane_resize` |  | `machine`: string |
| `notes_pages_sort` | 是 | `machine`: string |
| `notes_untitled-page_activate` |  | `machine`: string |
| `notes_page_create` |  | `machine`: string |
| `notes_pages-pane_resize` |  | `machine`: string |
| `notes_page-date_activate` |  | `machine`: string |
| `notes_page-time_activate` |  | `machine`: string |
| `notes_pagectrlaltn_create` |  | `machine`: string |
| `notes_sectionctrlaltt_create` |  | `machine`: string |
| `notes_section-group_create` |  | `machine`: string |
| `notes_notebook_create` |  | `machine`: string |
| `notes_import_import` |  | `machine`: string |
| `notes_export_export` |  | `machine`: string |
| `notes_more-commands-share_share` |  | `machine`: string |
| `notes_ctrlp_print` | 是 | `machine`: string |
| `notes_sync-nowctrls_activate` |  | `machine`: string |
| `notes_deleted-notes_activate` |  | `machine`: string |
| `notes_protected-sectionsctrlaltl_lock` |  | `machine`: string |
| `notes_theme_activate` |  | `machine`: string |
| `notes_keyboard-shortcutsctrlshift_activate` |  | `machine`: string |
| `notes_notes_show` | 是 | `machine`: string |
| `notes_file-pagectrlaltn_create` |  | `machine`: string |
| `notes_file-sectionctrlaltt_create` |  | `machine`: string |
| `notes_file-section-group_create` |  | `machine`: string |
| `notes_file-notebook_create` |  | `machine`: string |
| `notes_file-import_import` |  | `machine`: string |
| `notes_file-export_export` |  | `machine`: string |
| `notes_file-share_share` |  | `machine`: string |
| `notes_file-ctrlp_print` | 是 | `machine`: string |
| `notes_file-sync-nowctrls_activate` |  | `machine`: string |
| `notes_file-deleted-notes_activate` |  | `machine`: string |
| `notes_file-protected-sectionsctrlaltl_lock` |  | `machine`: string |
| `notes_file-theme_activate` |  | `machine`: string |
| `notes_file-keyboard-shortcutsctrlshift_activate` |  | `machine`: string |
| `notes_file-notes_show` | 是 | `machine`: string |
| `notes_page-title_activate` |  | `machine`: string |
| `notes_citation_activate` |  | `machine`: string |
| `notes_quote_activate` |  | `machine`: string |
| `notes_code_activate` |  | `machine`: string |
| `notes_website-visit_activate` |  | `machine`: string |
| `notes_idea_activate` |  | `machine`: string |
| `notes_password_activate` |  | `machine`: string |
| `notes_critical_activate` |  | `machine`: string |
| `notes_project_activate` |  | `machine`: string |
| `notes_project-b_activate` |  | `machine`: string |
| `notes_movie-see_activate` |  | `machine`: string |
| `notes_book-read_activate` |  | `machine`: string |
| `notes_music-listen_activate` |  | `machine`: string |
| `notes_discuss-manager_activate` |  | `machine`: string |
| `notes_email_send` |  | `machine`: string |
| `notes_meeting_schedule` |  | `machine`: string |
| `notes_call-back_activate` |  | `machine`: string |
| `notes_client-request_activate` |  | `machine`: string |
| `notes_tags-2_search` | 是 | `machine`: string |
| `notes_account-theme_activate` |  | `machine`: string |
| `notes_keyboard-shortcuts_activate` |  | `machine`: string |
| `notes_account-notes_show` | 是 | `machine`: string |
| `notes_local-s-notebook_activate` |  | `machine`: string |
| `notes_notebook-locals-notebook-switch-notebook-noteboo_create` |  | `machine`: string |
| `notes_notebook-settings_activate` |  | `machine`: string |
| `notes_none-order_activate` |  | `machine`: string |
| `notes_date-created_activate` |  | `machine`: string |
| `notes_date-modified_activate` |  | `machine`: string |
| `notes_alphabetical_activate` |  | `machine`: string |

## records（34 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `records_account_select` | 是 | `target`*: string, `machine`: string |
| `records_content_dismiss` | 是 | `machine`: string |
| `records_home_show` | 是 | `machine`: string |
| `records_trash_delete` |  | `machine`: string |
| `records_base_create` |  | `machine`: string |
| `records_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `records_search-bases_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `records_from-scratcha-blank-base-one-table_start` |  | `machine`: string |
| `records_base-2_create` |  | `machine`: string |
| `records_notice_dismiss` | 是 | `machine`: string |
| `records_it_dismiss` | 是 | `machine`: string |
| `records_appearance_activate` |  | `machine`: string |
| `records_keyboard-shortcuts_activate` |  | `machine`: string |
| `records_preview_show` | 是 | `machine`: string |
| `records_source-code-github_activate` |  | `machine`: string |
| `records_command-palette_show` | 是 | `machine`: string |

## meetings（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `meetings_item_select` | 是 | `target`*: string, `machine`: string |
| `meetings_meeting_create` |  | `target`*: string, `machine`: string |
| `meetings_settings_show` | 是 | `machine`: string |
| `meetings_theme_toggle` |  | `machine`: string |
| `meetings_out_sign` |  | `machine`: string |
| `meetings_meeting-2_create` |  | `machine`: string |
| `meetings_meeting-code-or-link_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `meetings_join_join` |  | `machine`: string |
| `meetings_today_activate` |  | `machine`: string |
| `meetings_week_previous` | 是 | `machine`: string |
| `meetings_week_next` | 是 | `machine`: string |
| `meetings_try-again_activate` |  | `machine`: string |
| `meetings_refresh_activate` |  | `machine`: string |
| `meetings_close_close` | 是 | `machine`: string |
| `meetings_nickname_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `meetings_nickname_save` |  | `machine`: string |
| `meetings_instant-meeting_start` |  | `machine`: string |

## teamchat（24 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `teamchat_workspacestart-space_create` |  | `target`*: string, `machine`: string |
| `teamchat_workspacestart-space-2_create` |  | `target`*: string, `machine`: string |
| `teamchat_messages_dismiss` | 是 | `machine`: string |
| `teamchat_invitepaste-code-or-link_join` |  | `machine`: string |
| `teamchat_puter_show` | 是 | `machine`: string |
| `teamchat_close_close` | 是 | `machine`: string |

## email（20 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `email_grant-read-access_activate` |  | `machine`: string |
| `email_command-palette_show` | 是 | `machine`: string |

## contacts（46 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `contacts_account-menu_activate` |  | `machine`: string |
| `contacts_smart-add_activate` |  | `machine`: string |
| `contacts_contact_create` |  | `machine`: string |
| `contacts_search-contacts_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_list-options_activate` |  | `machine`: string |
| `contacts_favorites_activate` |  | `machine`: string |
| `contacts_contact-2_create` |  | `machine`: string |
| `contacts_import_import` |  | `machine`: string |
| `contacts_contact-3_create` |  | `machine`: string |
| `contacts_set-photo_activate` |  | `machine`: string |
| `contacts_close_close` | 是 | `machine`: string |
| `contacts_first-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_last-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_nickname_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_company_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_job-title_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_email_create` |  | `machine`: string |
| `contacts_phone_create` |  | `machine`: string |
| `contacts_link_create` |  | `machine`: string |
| `contacts_address_create` |  | `machine`: string |
| `contacts_birthday_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_hide-year_toggle` |  | `machine`: string |
| `contacts_tags_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_notes_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `contacts_add-favorites_toggle` |  | `machine`: string |
| `contacts_cancel_cancel` | 是 | `machine`: string |
| `contacts_contact-4_create` |  | `machine`: string |
| `contacts_selection_select-all` |  | `machine`: string |

## calendar（54 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `calendar_day-view_select` | 是 | `target`*: string, `machine`: string |
| `calendar_item_select` | 是 | `target`*: string, `machine`: string |
| `calendar_selected_select` | 是 | `target`*: string, `machine`: string |
| `calendar_open_open` | 是 | `target`*: string, `machine`: string |
| `calendar_public-holiday_select` | 是 | `target`*: string, `machine`: string |
| `calendar_year-view-open_open` | 是 | `target`*: string, `machine`: string |
| `calendar_year-view-item_select` | 是 | `target`*: string, `machine`: string |
| `calendar_go_select` | 是 | `target`*: string, `machine`: string |
| `calendar_week_start` |  | `target`*: string, `machine`: string |
| `calendar_time_select` | 是 | `target`*: string, `machine`: string |
| `calendar_today_activate` |  | `machine`: string |
| `calendar_previous_previous` | 是 | `machine`: string |
| `calendar_next_next` | 是 | `machine`: string |
| `calendar_events-tasks_search` | 是 | `machine`: string |
| `calendar_year-view_activate` |  | `machine`: string |
| `calendar_month-view_activate` |  | `machine`: string |
| `calendar_week-view_activate` |  | `machine`: string |
| `calendar_day-view_activate` |  | `machine`: string |
| `calendar_list-view_activate` |  | `machine`: string |
| `calendar_account-settings_activate` |  | `machine`: string |
| `calendar_create_create` |  | `machine`: string |
| `calendar_month_previous` | 是 | `machine`: string |
| `calendar_month_next` | 是 | `machine`: string |
| `calendar_booking-links_hide` | 是 | `machine`: string |
| `calendar_link-that-lets-others-book-time-you_share` |  | `machine`: string |
| `calendar_event_create` |  | `machine`: string |
| `calendar_auto_activate` |  | `machine`: string |
| `calendar_light_activate` |  | `machine`: string |
| `calendar_dark_activate` |  | `machine`: string |
| `calendar_secondary-time-zone_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `calendar_public-holidays_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `calendar_clock-changes-daylight-saving_toggle` |  | `machine`: string |
| `calendar_export_import` |  | `machine`: string |
| `calendar_out_sign` |  | `machine`: string |
| `calendar_document_export` |  | `machine`: string |
| `calendar_command-palette_show` | 是 | `machine`: string |

## signatures（47 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `signatures_0out_select` | 是 | `target`*: string, `machine`: string |
| `signatures_0waiting_select` | 是 | `target`*: string, `machine`: string |
| `signatures_main_select` | 是 | `target`*: string, `machine`: string |
| `signatures_out_select` | 是 | `target`*: string, `machine`: string |
| `signatures_waiting_select` | 是 | `target`*: string, `machine`: string |
| `signatures_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `signatures_signer-declinessigning-closes_select` | 是 | `target`*: string, `machine`: string |
| `signatures_signatures-githubsend-documents_select` | 是 | `target`*: string, `machine`: string |
| `signatures_documents_show` | 是 | `machine`: string |
| `signatures_settings_show` | 是 | `machine`: string |
| `signatures_document_create` |  | `machine`: string |
| `signatures_document-2_create` |  | `machine`: string |
| `signatures_search-documents_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `signatures_drafts_activate` |  | `machine`: string |
| `signatures_completed_activate` |  | `machine`: string |
| `signatures_closed_activate` |  | `machine`: string |
| `signatures_pdf_import` |  | `machine`: string |
| `signatures_close_close` | 是 | `machine`: string |
| `signatures_set-up-account_activate` |  | `machine`: string |
| `signatures_explore-sample-documents_activate` |  | `machine`: string |
| `signatures_name-shown-signers_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `signatures_system_activate` |  | `machine`: string |
| `signatures_light_activate` |  | `machine`: string |
| `signatures_dark_activate` |  | `machine`: string |
| `signatures_documents-expire_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `signatures_remind-signers_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `signatures_any-signer-signsone-email-per-signature_toggle` |  | `machine`: string |
| `signatures_signature_create` |  | `machine`: string |
| `signatures_puteryour-documents-live-own-puter-cloud_show` | 是 | `machine`: string |

## photo-studio（121 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `photo-studio_sheet_create` |  | `target`*: string, `machine`: string |
| `photo-studio_photo-print_create` |  | `target`*: string, `machine`: string |
| `photo-studio_copy_export` |  | `target`*: string, `machine`: string |
| `photo-studio_edit_update` |  | `machine`: string |
| `photo-studio_image_activate` |  | `machine`: string |
| `photo-studio_layer_activate` |  | `machine`: string |
| `photo-studio_type_activate` |  | `machine`: string |
| `photo-studio_select_select` | 是 | `machine`: string |
| `photo-studio_filter_filter` | 是 | `machine`: string |
| `photo-studio_view_show` | 是 | `machine`: string |
| `photo-studio_window_activate` |  | `machine`: string |
| `photo-studio_help_show` | 是 | `machine`: string |
| `photo-studio_commands_search` | 是 | `machine`: string |
| `photo-studio_puter_save` |  | `machine`: string |
| `photo-studio_export_export` |  | `machine`: string |
| `photo-studio_puter-account_activate` |  | `machine`: string |
| `photo-studio_tool-presets_activate` |  | `machine`: string |
| `photo-studio_tool-presets-2_activate` |  | `machine`: string |
| `photo-studio_color-theme_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_panels_toggle` |  | `machine`: string |
| `photo-studio_default-colors_activate` |  | `machine`: string |
| `photo-studio_switch-colors_activate` |  | `machine`: string |
| `photo-studio_background-color_activate` |  | `machine`: string |
| `photo-studio_foreground-color_activate` |  | `machine`: string |
| `photo-studio_foreground-color-value_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_quick-mask-mode_activate` |  | `machine`: string |
| `photo-studio_screen-mode_update` |  | `machine`: string |
| `photo-studio_image-canvas_activate` |  | `machine`: string |
| `photo-studio_image_open` | 是 | `machine`: string |
| `photo-studio_document_create` |  | `machine`: string |
| `photo-studio_describe-edit_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_image_select` | 是 | `machine`: string |
| `photo-studio_start_start` |  | `machine`: string |
| `photo-studio_large-web-page_create` |  | `machine`: string |
| `photo-studio_square-social-post_create` |  | `machine`: string |
| `photo-studio_standard-phone_create` |  | `machine`: string |
| `photo-studio_presets-custom-sizes_activate` |  | `machine`: string |
| `photo-studio_what-s-newrecent-features_activate` |  | `machine`: string |
| `photo-studio_assistant_activate` |  | `machine`: string |
| `photo-studio_generation-history_activate` |  | `machine`: string |
| `photo-studio_history_activate` |  | `machine`: string |
| `photo-studio_actions_activate` |  | `machine`: string |
| `photo-studio_version-history_activate` |  | `machine`: string |
| `photo-studio_navigator_activate` |  | `machine`: string |
| `photo-studio_info_activate` |  | `machine`: string |
| `photo-studio_histogram_activate` |  | `machine`: string |
| `photo-studio_brushes_activate` |  | `machine`: string |
| `photo-studio_brush-settings_activate` |  | `machine`: string |
| `photo-studio_character_activate` |  | `machine`: string |
| `photo-studio_paragraph_activate` |  | `machine`: string |
| `photo-studio_styles_activate` |  | `machine`: string |
| `photo-studio_layer-comps_activate` |  | `machine`: string |
| `photo-studio_scripts_activate` |  | `machine`: string |
| `photo-studio_color_show` | 是 | `machine`: string |
| `photo-studio_swatches_show` | 是 | `machine`: string |
| `photo-studio_gradients_show` | 是 | `machine`: string |
| `photo-studio_patterns_show` | 是 | `machine`: string |
| `photo-studio_color-panel-menu_activate` |  | `machine`: string |
| `photo-studio_color-saturation-brightness_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_color-hue_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_hex-color_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_properties_show` | 是 | `machine`: string |
| `photo-studio_adjustments_show` | 是 | `machine`: string |
| `photo-studio_properties-panel-menu_activate` |  | `machine`: string |
| `photo-studio_image-size_activate` |  | `machine`: string |
| `photo-studio_layers_show` | 是 | `machine`: string |
| `photo-studio_channels_show` | 是 | `machine`: string |
| `photo-studio_paths_show` | 是 | `machine`: string |
| `photo-studio_layers-panel-menu_activate` |  | `machine`: string |
| `photo-studio_filter-layers-by-kind_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_filter-layers-by-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_layer-filtering_activate` |  | `machine`: string |
| `photo-studio_blend-mode_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_opacity_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_transparency_lock` |  | `machine`: string |
| `photo-studio_image-pixels_lock` |  | `machine`: string |
| `photo-studio_position_lock` |  | `machine`: string |
| `photo-studio_layer_lock` |  | `machine`: string |
| `photo-studio_fill_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_image_create` |  | `machine`: string |
| `photo-studio_link-layers_activate` |  | `machine`: string |
| `photo-studio_layer-style_create` |  | `machine`: string |
| `photo-studio_layer-mask_create` |  | `machine`: string |
| `photo-studio_fill-or-adjustment-layer_create` |  | `machine`: string |
| `photo-studio_group_create` |  | `machine`: string |
| `photo-studio_layer_create` |  | `machine`: string |
| `photo-studio_layer_delete` |  | `machine`: string |
| `photo-studio_view_zoom-out` |  | `machine`: string |
| `photo-studio_zoom-level_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `photo-studio_view_zoom-` |  | `machine`: string |
| `photo-studio_document-sizes_activate` |  | `machine`: string |
| `photo-studio_puter_show` | 是 | `machine`: string |
| `photo-studio_icon_collapse` | 是 | `machine`: string |
| `photo-studio_close_close` | 是 | `machine`: string |
| `photo-studio_tab-group_close` | 是 | `machine`: string |
| `photo-studio_shortcut_key-0` |  | `machine`: string |
| `photo-studio_selection_select-all` |  | `machine`: string |
| `photo-studio_selection_lock` |  | `machine`: string |
| `photo-studio_document_save` |  | `machine`: string |
| `photo-studio_edit_redo` |  | `machine`: string |
| `photo-studio_clipboard_paste` |  | `machine`: string |
| `photo-studio_shortcut_key-w` |  | `machine`: string |
| `photo-studio_edit_undo` |  | `machine`: string |

## video-studio（52 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `video-studio_account_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_browse-ready-made-projects-make-own_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_youtube-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_vertical-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_square-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_classic-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_portrait-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_feed-post-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_cinema-project_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item-2_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item-3_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item-4_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item-5_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_item-6_select` | 是 | `target`*: string, `machine`: string |
| `video-studio_editor_dismiss` | 是 | `machine`: string |
| `video-studio_home_show` | 是 | `machine`: string |
| `video-studio_templates_show` | 是 | `machine`: string |
| `video-studio_trash_delete` |  | `machine`: string |
| `video-studio_editopen-media-project_import` |  | `machine`: string |
| `video-studio_see_show` | 是 | `machine`: string |
| `video-studio_search-projects_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `video-studio_sort_sort` | 是 | `machine`: string |
| `video-studio_as-list_show` | 是 | `machine`: string |
| `video-studio_project-actions_show` | 是 | `machine`: string |
| `video-studio_powered-by-puter_show` | 是 | `machine`: string |
| `video-studio_theme_activate` |  | `machine`: string |
| `video-studio_last-modified_activate` |  | `machine`: string |
| `video-studio_date-created_activate` |  | `machine`: string |
| `video-studio_name_activate` |  | `machine`: string |
| `video-studio_project-file_open` | 是 | `machine`: string |
| `video-studio_media_import` |  | `machine`: string |
| `video-studio_more-project-actions-trash_delete` |  | `machine`: string |
| `video-studio_selection_select-all` |  | `machine`: string |

## vector-studio（106 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `vector-studio_account_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_drawing-modes_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_letter-x_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_x-mm_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_postcard-x-pt_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_web-x-px_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_mobile-x-px_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_square-x-px_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_icon-x-px_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_poster-x_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_preview_select` | 是 | `target`*: string, `machine`: string |
| `vector-studio_canvas_dismiss` | 是 | `machine`: string |
| `vector-studio_home_activate` |  | `machine`: string |
| `vector-studio_edit_update` |  | `machine`: string |
| `vector-studio_object_activate` |  | `machine`: string |
| `vector-studio_type_activate` |  | `machine`: string |
| `vector-studio_select_select` | 是 | `machine`: string |
| `vector-studio_effect_activate` |  | `machine`: string |
| `vector-studio_view_show` | 是 | `machine`: string |
| `vector-studio_window_activate` |  | `machine`: string |
| `vector-studio_help_show` | 是 | `machine`: string |
| `vector-studio_theme_activate` |  | `machine`: string |
| `vector-studio_single-or-double-column-tools_toggle` |  | `machine`: string |
| `vector-studio_selection-tool_activate` |  | `machine`: string |
| `vector-studio_direct-selection-tool_activate` |  | `machine`: string |
| `vector-studio_magic-wand-tool_activate` |  | `machine`: string |
| `vector-studio_lasso-tool_activate` |  | `machine`: string |
| `vector-studio_pen-tool_activate` |  | `machine`: string |
| `vector-studio_curvature-tool_activate` |  | `machine`: string |
| `vector-studio_sketch-shape-tool_activate` |  | `machine`: string |
| `vector-studio_paintbrush-tool_activate` |  | `machine`: string |
| `vector-studio_rectangle-tool_activate` |  | `machine`: string |
| `vector-studio_line-segment-tool_activate` |  | `machine`: string |
| `vector-studio_shape-builder-tool_activate` |  | `machine`: string |
| `vector-studio_type-tool_activate` |  | `machine`: string |
| `vector-studio_tool_rotate` |  | `machine`: string |
| `vector-studio_scale-tool_activate` |  | `machine`: string |
| `vector-studio_width-tool_activate` |  | `machine`: string |
| `vector-studio_free-transform-tool_activate` |  | `machine`: string |
| `vector-studio_eraser-tool_activate` |  | `machine`: string |
| `vector-studio_perspective-grid-tool_activate` |  | `machine`: string |
| `vector-studio_gradient-tool_activate` |  | `machine`: string |
| `vector-studio_mesh-tool_activate` |  | `machine`: string |
| `vector-studio_eyedropper-tool_activate` |  | `machine`: string |
| `vector-studio_blend-tool_activate` |  | `machine`: string |
| `vector-studio_symbol-sprayer-tool_activate` |  | `machine`: string |
| `vector-studio_column-graph-tool_activate` |  | `machine`: string |
| `vector-studio_artboard-tool_activate` |  | `machine`: string |
| `vector-studio_hand-tool_activate` |  | `machine`: string |
| `vector-studio_view_zoom-tool` |  | `machine`: string |
| `vector-studio_fill_activate` |  | `machine`: string |
| `vector-studio_stroke_activate` |  | `machine`: string |
| `vector-studio_swap-fill-stroke_activate` |  | `machine`: string |
| `vector-studio_default-fill-stroke_activate` |  | `machine`: string |
| `vector-studio_color_activate` |  | `machine`: string |
| `vector-studio_gradient_activate` |  | `machine`: string |
| `vector-studio_none_activate` |  | `machine`: string |
| `vector-studio_tools_activate` |  | `machine`: string |
| `vector-studio_screen-mode_update` |  | `machine`: string |
| `vector-studio_open_open` | 是 | `machine`: string |
| `vector-studio_home-2_activate` |  | `machine`: string |
| `vector-studio_recent_activate` |  | `machine`: string |
| `vector-studio_files_activate` |  | `machine`: string |
| `vector-studio_templates_activate` |  | `machine`: string |
| `vector-studio_hide_hide` | 是 | `machine`: string |
| `vector-studio_presets-sizes-settings_show` | 是 | `machine`: string |
| `vector-studio_refresh-files_activate` |  | `machine`: string |
| `vector-studio_powered-by-puter_show` | 是 | `machine`: string |
| `vector-studio_panels_activate` |  | `machine`: string |
| `vector-studio_color-paint-panels_activate` |  | `machine`: string |
| `vector-studio_arrange-shape-panels_activate` |  | `machine`: string |
| `vector-studio_type-panels_activate` |  | `machine`: string |
| `vector-studio_symbols_activate` |  | `machine`: string |
| `vector-studio_libraries_activate` |  | `machine`: string |
| `vector-studio_asset-export_activate` |  | `machine`: string |
| `vector-studio_generate_run` |  | `machine`: string |
| `vector-studio_generation-history_activate` |  | `machine`: string |
| `vector-studio_document-panels_activate` |  | `machine`: string |
| `vector-studio_flattener-preview_activate` |  | `machine`: string |
| `vector-studio_variables_activate` |  | `machine`: string |
| `vector-studio_svg-interactivity_activate` |  | `machine`: string |
| `vector-studio_actions_activate` |  | `machine`: string |
| `vector-studio_mockup_activate` |  | `machine`: string |
| `vector-studio_match-font_activate` |  | `machine`: string |
| `vector-studio_properties_show` | 是 | `machine`: string |
| `vector-studio_layers_show` | 是 | `machine`: string |
| `vector-studio_signed-as-local_activate` |  | `machine`: string |
| `vector-studio_shortcut_key-5` |  | `machine`: string |

## audio-studio（165 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `audio-studio_account_select` | 是 | `target`*: string, `machine`: string |
| `audio-studio_waveform_select` | 是 | `target`*: string, `machine`: string |
| `audio-studio_multitrack_select` | 是 | `target`*: string, `machine`: string |
| `audio-studio_selection-tool-e_select` | 是 | `target`*: string, `machine`: string |
| `audio-studio_edit_update` |  | `machine`: string |
| `audio-studio_multitrack_activate` |  | `machine`: string |
| `audio-studio_clip_activate` |  | `machine`: string |
| `audio-studio_effects_activate` |  | `machine`: string |
| `audio-studio_favorites_activate` |  | `machine`: string |
| `audio-studio_view_show` | 是 | `machine`: string |
| `audio-studio_window_activate` |  | `machine`: string |
| `audio-studio_help_show` | 是 | `machine`: string |
| `audio-studio_spectral-frequency-display-shiftd_show` | 是 | `machine`: string |
| `audio-studio_spectral-pitch-display_show` | 是 | `machine`: string |
| `audio-studio_tool-v_move` |  | `machine`: string |
| `audio-studio_razor-tool-r_activate` |  | `machine`: string |
| `audio-studio_slip-tool-y_activate` |  | `machine`: string |
| `audio-studio_time-selection-tool-t_activate` |  | `machine`: string |
| `audio-studio_lasso-selection-tool-d_activate` |  | `machine`: string |
| `audio-studio_paintbrush-selection-tool-p_activate` |  | `machine`: string |
| `audio-studio_spot-healing-brush-tool-b_activate` |  | `machine`: string |
| `audio-studio_workspaces_activate` |  | `machine`: string |
| `audio-studio_search-commands_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_files_show` | 是 | `machine`: string |
| `audio-studio_files-panel-menu_activate` |  | `machine`: string |
| `audio-studio_favorites_show` | 是 | `machine`: string |
| `audio-studio_open_open` | 是 | `machine`: string |
| `audio-studio_import_import` |  | `machine`: string |
| `audio-studio_audio-file_create` |  | `machine`: string |
| `audio-studio_into-multitrack_create` |  | `machine`: string |
| `audio-studio_close_close` | 是 | `machine`: string |
| `audio-studio_search-files_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_name_activate` |  | `machine`: string |
| `audio-studio_status_activate` |  | `machine`: string |
| `audio-studio_duration_activate` |  | `machine`: string |
| `audio-studio_sample-rate_activate` |  | `machine`: string |
| `audio-studio_channels_activate` |  | `machine`: string |
| `audio-studio_bit-depth_activate` |  | `machine`: string |
| `audio-studio_format_activate` |  | `machine`: string |
| `audio-studio_from-start_play` |  | `machine`: string |
| `audio-studio_loop-playback_activate` |  | `machine`: string |
| `audio-studio_auto-play_toggle` |  | `machine`: string |
| `audio-studio_panels_resize` |  | `machine`: string |
| `audio-studio_media-browser_show` | 是 | `machine`: string |
| `audio-studio_media-browser-panel-menu_activate` |  | `machine`: string |
| `audio-studio_effects-rack_show` | 是 | `machine`: string |
| `audio-studio_markers_show` | 是 | `machine`: string |
| `audio-studio_properties_show` | 是 | `machine`: string |
| `audio-studio_panels-group_activate` |  | `machine`: string |
| `audio-studio_up-one-level_activate` |  | `machine`: string |
| `audio-studio_refresh_activate` |  | `machine`: string |
| `audio-studio_folder-from-device_create` |  | `machine`: string |
| `audio-studio_home_activate` |  | `machine`: string |
| `audio-studio_search-folder_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_only-audio-files_show` | 是 | `machine`: string |
| `audio-studio_homeappdata_activate` |  | `machine`: string |
| `audio-studio_appdata_activate` |  | `machine`: string |
| `audio-studio_folder_create` |  | `machine`: string |
| `audio-studio_appdatafolder_activate` |  | `machine`: string |
| `audio-studio_preview_play` |  | `machine`: string |
| `audio-studio_preview_stop` |  | `machine`: string |
| `audio-studio_loop-preview_activate` |  | `machine`: string |
| `audio-studio_preview-position_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_auto-play-2_toggle` |  | `machine`: string |
| `audio-studio_open-2_open` | 是 | `machine`: string |
| `audio-studio_into-multitrack-2_create` |  | `machine`: string |
| `audio-studio_history_show` | 是 | `machine`: string |
| `audio-studio_history-panel-menu_activate` |  | `machine`: string |
| `audio-studio_video_show` | 是 | `machine`: string |
| `audio-studio_history_clear` |  | `machine`: string |
| `audio-studio_editor_show` | 是 | `machine`: string |
| `audio-studio_editor-panel-menu_activate` |  | `machine`: string |
| `audio-studio_mixer_show` | 是 | `machine`: string |
| `audio-studio_open-3_open` | 是 | `machine`: string |
| `audio-studio_audio-file-2_create` |  | `machine`: string |
| `audio-studio_multitrack-session_create` |  | `machine`: string |
| `audio-studio_record_record` |  | `machine`: string |
| `audio-studio_playhead-time_activate` |  | `machine`: string |
| `audio-studio_stop_stop` |  | `machine`: string |
| `audio-studio_space_play` |  | `machine`: string |
| `audio-studio_pause_pause` |  | `machine`: string |
| `audio-studio_playhead-previous_move` |  | `machine`: string |
| `audio-studio_rewind_activate` |  | `machine`: string |
| `audio-studio_fast-forward_activate` |  | `machine`: string |
| `audio-studio_playhead-next_move` |  | `machine`: string |
| `audio-studio_shiftspace_record` |  | `machine`: string |
| `audio-studio_selection_dismiss` | 是 | `machine`: string |
| `audio-studio_view_zoom-` |  | `machine`: string |
| `audio-studio_view_zoom-out` |  | `machine`: string |
| `audio-studio_view-2_zoom-` |  | `machine`: string |
| `audio-studio_view-2_zoom-out` |  | `machine`: string |
| `audio-studio_view-3_zoom-out` |  | `machine`: string |
| `audio-studio_view-3_zoom-` |  | `machine`: string |
| `audio-studio_view-4_zoom-` |  | `machine`: string |
| `audio-studio_view-5_zoom-` |  | `machine`: string |
| `audio-studio_view_zoom-reset` |  | `machine`: string |
| `audio-studio_view-6_zoom-` |  | `machine`: string |
| `audio-studio_sound-assistant_show` | 是 | `machine`: string |
| `audio-studio_sound-assistant-panel-menu_activate` |  | `machine`: string |
| `audio-studio_levels_show` | 是 | `machine`: string |
| `audio-studio_levels-panel-menu_activate` |  | `machine`: string |
| `audio-studio_left-channel-clip-indicator-click-reset_activate` |  | `machine`: string |
| `audio-studio_right-channel-clip-indicator-click-reset_activate` |  | `machine`: string |
| `audio-studio_selection-view_show` | 是 | `machine`: string |
| `audio-studio_selection-view-panel-menu_activate` |  | `machine`: string |
| `audio-studio_selection-start_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_selection-end_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_selection-duration_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_view-start_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_view-end_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_view-duration_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_signed-as-local_activate` |  | `machine`: string |
| `audio-studio_saved-layout_reset` |  | `machine`: string |
| `audio-studio_changes-workspace_save` |  | `machine`: string |
| `audio-studio_as-workspace_save` |  | `machine`: string |
| `audio-studio_workspaces_update` |  | `machine`: string |
| `audio-studio_ctrlo_open` | 是 | `machine`: string |
| `audio-studio_file-ctrli_import` |  | `machine`: string |
| `audio-studio_audio-file-altshiftn_create` |  | `machine`: string |
| `audio-studio_into-multitrack-session_create` |  | `machine`: string |
| `audio-studio_closealtw_activate` |  | `machine`: string |
| `audio-studio_allaltshiftw_close` | 是 | `machine`: string |
| `audio-studio_columns_activate` |  | `machine`: string |
| `audio-studio_by-open-order_sort` | 是 | `machine`: string |
| `audio-studio_panel_close` | 是 | `machine`: string |
| `audio-studio_other-panels-group_close` | 是 | `machine`: string |
| `audio-studio_panel-group_close` | 是 | `machine`: string |
| `audio-studio_maximize-frame_activate` |  | `machine`: string |
| `audio-studio_file-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_sample-rate_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_channels_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_bit-depth_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `audio-studio_cancel_cancel` | 是 | `machine`: string |
| `audio-studio_ok_confirm` |  | `machine`: string |
| `audio-studio_media-browser-panel-menu-panel_close` | 是 | `machine`: string |
| `audio-studio_media-browser-panel-menu-other-panels-group_close` | 是 | `machine`: string |
| `audio-studio_media-browser-panel-menu-panel-group_close` | 是 | `machine`: string |
| `audio-studio_media-browser-panel-menu-maximize-frame_activate` |  | `machine`: string |
| `audio-studio_undoctrlz_activate` |  | `machine`: string |
| `audio-studio_redoctrlshiftz_activate` |  | `machine`: string |
| `audio-studio_later-states_delete` |  | `machine`: string |
| `audio-studio_history-panel-menu-history_clear` |  | `machine`: string |
| `audio-studio_history-panel-menu-panel_close` | 是 | `machine`: string |
| `audio-studio_history-panel-menu-other-panels-group_close` | 是 | `machine`: string |
| `audio-studio_history-panel-menu-panel-group_close` | 是 | `machine`: string |
| `audio-studio_history-panel-menu-maximize-frame_activate` |  | `machine`: string |
| `audio-studio_selection_select-all` |  | `machine`: string |

## music-studio（283 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `music-studio_pattern-mode_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_song-mode_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_pattern_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_project_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_account_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_one-synthesized-drum-voice_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_browser_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_beat-clips_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_bassline-clips_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_chords-clips_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_lead-clip_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-1_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-3_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-4_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-5_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_mute-track_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_solo-track_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-6_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-7_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-8_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-9_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-10_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-11_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-12_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-13_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-14_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-15_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_track-16_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_channel-rack-beat_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_step-velocity_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_step-off_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_clap_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_clap-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_closed-hat_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_closed-hat-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_hat_open` | 是 | `target`*: string, `machine`: string |
| `music-studio_hat-2_open` | 是 | `target`*: string, `machine`: string |
| `music-studio_bass_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_bass-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_chords_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_chords-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_lead_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_lead-2_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_master-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_inputs_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_clap-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-double-click-or-rename_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename_create` |  | `target`*: string, `machine`: string |
| `music-studio_mute-insert_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_solo-insert_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_kick-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-2_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-3_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-4_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-5_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-6_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-7_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-8_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-9_create` |  | `target`*: string, `machine`: string |
| `music-studio_double-click-or-rename-10_create` |  | `target`*: string, `machine`: string |
| `music-studio_effect_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_beat_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_bassline_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_pattern-beat-select-pattern-chords_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_pattern-beat-select-pattern-lead_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_pattern_rename` |  | `target`*: string, `machine`: string |
| `music-studio_clap-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_clap-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_hats-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_bass-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_chords-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_reverb-slot-open-editor_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_lead-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_lead-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_delay-slot-open-editor_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_lead-click-select-double-click-or-enter-reverb-s_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_add-mixer-insert-project_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_insert-master_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-kick_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-clap_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-hats_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-bass_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-chords_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-lead_send` |  | `target`*: string, `machine`: string |
| `music-studio_insert-insert_send` |  | `target`*: string, `machine`: string |
| `music-studio_add-mixer-insert-double-click-or-rename_create` |  | `target`*: string, `machine`: string |
| `music-studio_volume_create` |  | `target`*: string, `machine`: string |
| `music-studio_add-mixer-insert-mute-insert_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_add-mixer-insert-solo-insert_select` | 是 | `target`*: string, `machine`: string |
| `music-studio_workspace_dismiss` | 是 | `machine`: string |
| `music-studio_edit_update` |  | `machine`: string |
| `music-studio_add_create` |  | `machine`: string |
| `music-studio_patterns_activate` |  | `machine`: string |
| `music-studio_view_show` | 是 | `machine`: string |
| `music-studio_options_activate` |  | `machine`: string |
| `music-studio_tools_activate` |  | `machine`: string |
| `music-studio_help_show` | 是 | `machine`: string |
| `music-studio_play_play` |  | `machine`: string |
| `music-studio_stop_stop` |  | `machine`: string |
| `music-studio_record_record` |  | `machine`: string |
| `music-studio_tempo-beats-per-minute_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_metronome_activate` |  | `machine`: string |
| `music-studio_count-in-before-recording_activate` |  | `machine`: string |
| `music-studio_typing-keyboard-piano_activate` |  | `machine`: string |
| `music-studio_pattern_previous` | 是 | `machine`: string |
| `music-studio_pattern_next` | 是 | `machine`: string |
| `music-studio_pattern_create` |  | `machine`: string |
| `music-studio_playlist_activate` |  | `machine`: string |
| `music-studio_channel-rack_activate` |  | `machine`: string |
| `music-studio_piano-roll_activate` |  | `machine`: string |
| `music-studio_mixer_activate` |  | `machine`: string |
| `music-studio_browser_activate` |  | `machine`: string |
| `music-studio_master-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `music-studio_audio_import` |  | `machine`: string |
| `music-studio_collapse_collapse` | 是 | `machine`: string |
| `music-studio_browser_close` | 是 | `machine`: string |
| `music-studio_search-browser_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_instruments_activate` |  | `machine`: string |
| `music-studio_synth-presets_activate` |  | `machine`: string |
| `music-studio_drum-presets_activate` |  | `machine`: string |
| `music-studio_effects_activate` |  | `machine`: string |
| `music-studio_project_activate` |  | `machine`: string |
| `music-studio_files_activate` |  | `machine`: string |
| `music-studio_music-studio-files_activate` |  | `machine`: string |
| `music-studio_browse-another-folder_activate` |  | `machine`: string |
| `music-studio_audio-from-device_import` |  | `machine`: string |
| `music-studio_device_activate` |  | `machine`: string |
| `music-studio_browser_resize` |  | `machine`: string |
| `music-studio_clip-sources_show` | 是 | `machine`: string |
| `music-studio_tool_draw` |  | `machine`: string |
| `music-studio_paint-tool_activate` |  | `machine`: string |
| `music-studio_tool_delete` |  | `machine`: string |
| `music-studio_mute-tool_activate` |  | `machine`: string |
| `music-studio_slice-tool_activate` |  | `machine`: string |
| `music-studio_tool_select` | 是 | `machine`: string |
| `music-studio_view_zoom-tool` |  | `machine`: string |
| `music-studio_playback-tool_activate` |  | `machine`: string |
| `music-studio_snap_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_follow-playhead_activate` |  | `machine`: string |
| `music-studio_follow-options_activate` |  | `machine`: string |
| `music-studio_view_zoom-out` |  | `machine`: string |
| `music-studio_view_zoom-` |  | `machine`: string |
| `music-studio_view-2_zoom-` |  | `machine`: string |
| `music-studio_maximize-playlist_activate` |  | `machine`: string |
| `music-studio_playlist_close` | 是 | `machine`: string |
| `music-studio_automation-clip_create` |  | `machine`: string |
| `music-studio_clip-source-list_resize` |  | `machine`: string |
| `music-studio_track_create` |  | `machine`: string |
| `music-studio_song-position_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_mute-drums_activate` |  | `machine`: string |
| `music-studio_solo-drums_activate` |  | `machine`: string |
| `music-studio_mute-bass_activate` |  | `machine`: string |
| `music-studio_solo-bass_activate` |  | `machine`: string |
| `music-studio_mute-chords_activate` |  | `machine`: string |
| `music-studio_solo-chords_activate` |  | `machine`: string |
| `music-studio_mute-lead_activate` |  | `machine`: string |
| `music-studio_solo-lead_activate` |  | `machine`: string |
| `music-studio_playlist-arrangement_activate` |  | `machine`: string |
| `music-studio_editors_resize` |  | `machine`: string |
| `music-studio_bar_delete` |  | `machine`: string |
| `music-studio_bar_create` |  | `machine`: string |
| `music-studio_swing_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_velocity-lane_activate` |  | `machine`: string |
| `music-studio_channel_create` |  | `machine`: string |
| `music-studio_maximize-channel-rack_activate` |  | `machine`: string |
| `music-studio_channel-rack_close` | 是 | `machine`: string |
| `music-studio_kick-3_select` | 是 | `machine`: string |
| `music-studio_clap-3_select` | 是 | `machine`: string |
| `music-studio_closed-hat-3_select` | 是 | `machine`: string |
| `music-studio_open-hat_select` | 是 | `machine`: string |
| `music-studio_bass-3_select` | 是 | `machine`: string |
| `music-studio_chords-3_select` | 是 | `machine`: string |
| `music-studio_lead-3_select` | 是 | `machine`: string |
| `music-studio_channel-2_create` |  | `machine`: string |
| `music-studio_panels_resize` |  | `machine`: string |
| `music-studio_mixer-insert_create` |  | `machine`: string |
| `music-studio_effects-routing-panel_activate` |  | `machine`: string |
| `music-studio_maximize-mixer_activate` |  | `machine`: string |
| `music-studio_mixer_close` | 是 | `machine`: string |
| `music-studio_mute-master_activate` |  | `machine`: string |
| `music-studio_pan_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_width_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_kick-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_mute-kick_activate` |  | `machine`: string |
| `music-studio_solo-kick_activate` |  | `machine`: string |
| `music-studio_mute-clap_activate` |  | `machine`: string |
| `music-studio_solo-clap_activate` |  | `machine`: string |
| `music-studio_mute-hats_activate` |  | `machine`: string |
| `music-studio_solo-hats_activate` |  | `machine`: string |
| `music-studio_options_create` |  | `machine`: string |
| `music-studio_insert_select` | 是 | `machine`: string |
| `music-studio_send-level-master_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_send-master_delete` |  | `machine`: string |
| `music-studio_send_create` |  | `machine`: string |
| `music-studio_channel-rack_select` | 是 | `machine`: string |
| `music-studio_music-studio-is-open-source_show` | 是 | `machine`: string |
| `music-studio_take-tour_activate` |  | `machine`: string |
| `music-studio_it_dismiss` | 是 | `machine`: string |
| `music-studio_pattern-beat-select-pattern-pattern_create` |  | `machine`: string |
| `music-studio_clone-pattern_activate` |  | `machine`: string |
| `music-studio_signed-as-local_activate` |  | `machine`: string |
| `music-studio_follow-options-follow-playhead_activate` |  | `machine`: string |
| `music-studio_page-by-page_activate` |  | `machine`: string |
| `music-studio_continuous_activate` |  | `machine`: string |
| `music-studio_poly-synth_activate` |  | `machine`: string |
| `music-studio_drum-synth_activate` |  | `machine`: string |
| `music-studio_sampler_activate` |  | `machine`: string |
| `music-studio_add-channel-synth-presets_activate` |  | `machine`: string |
| `music-studio_add-channel-drum-presets_activate` |  | `machine`: string |
| `music-studio_sampler-from-audio-file_activate` |  | `machine`: string |
| `music-studio_clap-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_hats-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_bass-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_chords-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_drag-reorder-ctrlup-down_activate` |  | `machine`: string |
| `music-studio_reverb_activate` |  | `machine`: string |
| `music-studio_reverb-mix_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_reverb-options_activate` |  | `machine`: string |
| `music-studio_lead-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_delay_activate` |  | `machine`: string |
| `music-studio_delay-mix_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `music-studio_delay-options_activate` |  | `machine`: string |
| `music-studio_shortcut_key-t` |  | `machine`: string |

## 3d（247 个工具）

### `3d_app_open`

打开应用（桌面窗口；--headless 用无界面实例）。CLI：foxos 3d app open [--file FILE] [--headless]。示例：foxos 3d app open

只读：否 · 破坏性：否 · CLI：`foxos 3d app open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string |  | 同时打开工作空间中的文件 |
| `headless` | boolean |  | 不显示窗口 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_app_open", "arguments": {}}
```

### `3d_app_close`

关闭应用实例。CLI：foxos 3d app close。示例：foxos 3d app close --json

只读：否 · 破坏性：否 · CLI：`foxos 3d app close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_app_close", "arguments": {}}
```

### `3d_app_status`

应用是否已安装、是否在运行。CLI：foxos 3d app status。示例：foxos 3d app status --json

只读：是 · 破坏性：否 · CLI：`foxos 3d app status`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_app_status", "arguments": {}}
```

### `3d_app_reset`

重置应用：关闭实例并清空本工作空间下的应用数据（AppData/<应用> 与浏览器存储）。CLI：foxos 3d app reset。示例：foxos 3d app reset --json

只读：否 · 破坏性：是 · CLI：`foxos 3d app reset`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_app_reset", "arguments": {}}
```

### `3d_file_open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）。CLI：foxos 3d file open PATH。示例：foxos 3d file open X

只读：否 · 破坏性：否 · CLI：`foxos 3d file open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_file_open", "arguments": {"path": "…"}}
```

### `3d_ui_snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值。CLI：foxos 3d ui snapshot [--all] [--limit LIMIT]。示例：foxos 3d ui snapshot --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui snapshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `all` | boolean |  | 包括不可见元素 |
| `limit` | integer |  | 最多返回元素数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_snapshot", "arguments": {}}
```

### `3d_ui_text`

读取界面上的可见文本。CLI：foxos 3d ui text。示例：foxos 3d ui text --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui text`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_text", "arguments": {}}
```

### `3d_ui_click`

点击控件（按 ref 或名称），与人点击相同。CLI：foxos 3d ui click [--ref REF] [--name NAME] [--role ROLE] [--force]。示例：foxos 3d ui click --ref e12

只读：否 · 破坏性：否 · CLI：`foxos 3d ui click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `ref` | string |  | snapshot 返回的元素引用 |
| `name` | string |  | 按可访问名称查找 |
| `role` | string |  | 限定角色，如 button |
| `force` | boolean |  | 控件被弹窗挡住时也强制点击 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_click", "arguments": {}}
```

### `3d_ui_type`

向控件输入文本（真实输入事件）。CLI：foxos 3d ui type TEXT [--ref REF] [--clear]。示例：foxos 3d ui type 'hello' --ref e5

只读：否 · 破坏性：否 · CLI：`foxos 3d ui type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要输入的文本 |
| `ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | boolean |  | 先清空 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_type", "arguments": {"text": "…"}}
```

### `3d_ui_set`

设置输入框 / 下拉框 / 复选框的值。CLI：foxos 3d ui set --ref REF --value VALUE [--force]。示例：foxos 3d ui set 

只读：否 · 破坏性：否 · CLI：`foxos 3d ui set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `ref` | string | 是 | 元素引用 |
| `value` | string | 是 | 值 |
| `force` | boolean |  | 控件被挡住时也强制设置 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_set", "arguments": {"ref": "…", "value": "…"}}
```

### `3d_ui_press`

按键或快捷键（如 Enter、ctrl+z、mod+s）。CLI：foxos 3d ui press KEY [--ref REF]。示例：foxos 3d ui press mod+z

只读：否 · 破坏性：否 · CLI：`foxos 3d ui press`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 按键 |
| `ref` | string |  | 先聚焦的元素引用 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_press", "arguments": {"key": "…"}}
```

### `3d_ui_screenshot`

应用窗口截图（PNG）。CLI：foxos 3d ui screenshot [--out OUT]。示例：foxos 3d ui screenshot --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `out` | string |  | 保存到工作空间路径 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ui_screenshot", "arguments": {}}
```

### `3d_data_list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）。CLI：foxos 3d data list [PATTERN]。示例：foxos 3d data list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d data list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pattern` | string |  | 通配符 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_data_list", "arguments": {}}
```

### `3d_data_get`

读取应用保存的一项数据。CLI：foxos 3d data get KEY。示例：foxos 3d data get X

只读：是 · 破坏性：否 · CLI：`foxos 3d data get`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 数据键 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_data_get", "arguments": {"key": "…"}}
```

### `3d_module_list`

列出应用自己的 ES 模块及导出（供 module call 使用）。CLI：foxos 3d module list。示例：foxos 3d module list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d module list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_module_list", "arguments": {}}
```

### `3d_module_read`

读取应用模块中的值（如 store 状态）。CLI：foxos 3d module read TARGET。示例：foxos 3d module read X

只读：是 · 破坏性：否 · CLI：`foxos 3d module read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_module_read", "arguments": {"target": "…"}}
```

### `3d_module_call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）。CLI：foxos 3d module call TARGET [--args ARGS]。示例：foxos 3d module call X

只读：否 · 破坏性：否 · CLI：`foxos 3d module call`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 模块路径#导出.方法 |
| `args` | array |  | 参数（JSON 数组） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_module_call", "arguments": {"target": "…"}}
```

### `3d_op_list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）。CLI：foxos 3d op list。示例：foxos 3d op list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d op list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_op_list", "arguments": {}}
```

### `3d_cozy-room_select`

a cozy room: *（1 项，如 A cozy room: floor, two walls, a sofa and a lamp）。CLI：foxos 3d cozy-room select TARGET。界面：主界面 > Conversation > a cozy room: *。效果：点击名称匹配的「a cozy room: *」项（button）。示例：foxos 3d cozy-room select 'A cozy room: floor, two walls, a sofa and a lamp' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d cozy-room select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'A cozy room: floor, two walls, a sofa and a lamp' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_cozy-room_select", "arguments": {"target": "…"}}
```

### `3d_adjust-last-operation_select`

adjust last operation…#（1 项，如 Adjust Last Operation…F9）。CLI：foxos 3d adjust-last-operation select TARGET。界面：Edit > menu > adjust last operation…#。效果：点击名称匹配的「adjust last operation…#」项（menuitem）。示例：foxos 3d adjust-last-operation select 'Adjust Last Operation…F9' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d adjust-last-operation select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Adjust Last Operation…F9' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_adjust-last-operation_select", "arguments": {"target": "…"}}
```

### `3d_search_show`

menu search…#（1 项，如 Menu Search…F3）。CLI：foxos 3d search show TARGET。界面：Edit > menu > menu search…#。效果：点击名称匹配的「menu search…#」项（menuitem）。示例：foxos 3d search show 'Menu Search…F3' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d search show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Menu Search…F3' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_search_show", "arguments": {"target": "…"}}
```

### `3d_active-item_rename`

rename active item…#（1 项，如 Rename Active Item…F2）。CLI：foxos 3d active-item rename TARGET。界面：Edit > menu > rename active item…#。效果：点击名称匹配的「rename active item…#」项（menuitem）。示例：foxos 3d active-item rename 'Rename Active Item…F2' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d active-item rename`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Rename Active Item…F2' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_active-item_rename", "arguments": {"target": "…"}}
```

### `3d_batch-rename-ctrl_select`

batch rename…ctrl #（1 项，如 Batch Rename…Ctrl F2）。CLI：foxos 3d batch-rename-ctrl select TARGET。界面：Edit > menu > batch rename…ctrl #。效果：点击名称匹配的「batch rename…ctrl #」项（menuitem）。示例：foxos 3d batch-rename-ctrl select 'Batch Rename…Ctrl F2' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d batch-rename-ctrl select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Batch Rename…Ctrl F2' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_batch-rename-ctrl_select", "arguments": {"target": "…"}}
```

### `3d_render_select`

render #（1 项，如 Render ImageF12）。CLI：foxos 3d render select TARGET。界面：Render > menu > render #。效果：点击名称匹配的「render #」项（menuitem）。示例：foxos 3d render select 'Render ImageF12' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d render select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Render ImageF12' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_render_select", "arguments": {"target": "…"}}
```

### `3d_render-animationctrl_select`

render animationctrl #（1 项，如 Render AnimationCtrl F12）。CLI：foxos 3d render-animationctrl select TARGET。界面：Render > menu > render animationctrl #。效果：点击名称匹配的「render animationctrl #」项（menuitem）。示例：foxos 3d render-animationctrl select 'Render AnimationCtrl F12' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d render-animationctrl select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Render AnimationCtrl F12' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_render-animationctrl_select", "arguments": {"target": "…"}}
```

### `3d_view_show`

view #（1 项，如 View RenderF11）。CLI：foxos 3d view show TARGET。界面：Render > menu > view #。效果：点击名称匹配的「view #」项（menuitem）。示例：foxos 3d view show 'View RenderF11' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d view show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'View RenderF11' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_view_show", "arguments": {"target": "…"}}
```

### `3d_animationctrl_show`

view animationctrl #（1 项，如 View AnimationCtrl F11）。CLI：foxos 3d animationctrl show TARGET。界面：Render > menu > view animationctrl #。效果：点击名称匹配的「view animationctrl #」项（menuitem）。示例：foxos 3d animationctrl show 'View AnimationCtrl F11' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d animationctrl show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'View AnimationCtrl F11' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_animationctrl_show", "arguments": {"target": "…"}}
```

### `3d_e-g-png_filter`

filter (e.g. *.png)（1 项，如 Filter (e.g. *.png)）。CLI：foxos 3d e-g-png filter TARGET。界面：Shading > main > filter (e.g. *.png)。效果：点击名称匹配的「filter (e.g. *.png)」项（textbox）。示例：foxos 3d e-g-png filter 'Filter (e.g. *.png)' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d e-g-png filter`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Filter (e.g. *.png)' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_e-g-png_filter", "arguments": {"target": "…"}}
```

### `3d_slot-empty_select`

slot # (empty)（1 项，如 Slot 1 (empty)）。CLI：foxos 3d slot-empty select TARGET。界面：Rendering > main > slot # (empty)。效果：点击名称匹配的「slot # (empty)」项（button）。示例：foxos 3d slot-empty select 'Slot 1 (empty)' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d slot-empty select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Slot 1 (empty)' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_slot-empty_select", "arguments": {"target": "…"}}
```

### `3d_fps_select`

# fps（1 项，如 24 fps）。CLI：foxos 3d fps select TARGET。界面：Compositing > main > # fps。效果：点击名称匹配的「# fps」项（button）。示例：foxos 3d fps select '24 fps' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d fps select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 '24 fps' |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_fps_select", "arguments": {"target": "…"}}
```

### `3d_edit_update`

Edit。CLI：foxos 3d edit update。界面：主界面 > header > Edit。效果：点击「Edit」（button）。示例：foxos 3d edit update --json

只读：否 · 破坏性：否 · CLI：`foxos 3d edit update`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_edit_update", "arguments": {}}
```

### `3d_render_activate`

Render。CLI：foxos 3d render activate。界面：主界面 > header > Render。效果：点击「Render」（button）。示例：foxos 3d render activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_render_activate", "arguments": {}}
```

### `3d_window_activate`

Window。CLI：foxos 3d window activate。界面：主界面 > header > Window。效果：点击「Window」（button）。示例：foxos 3d window activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_window_activate", "arguments": {}}
```

### `3d_help_show`

Help。CLI：foxos 3d help show。界面：主界面 > header > Help。效果：点击「Help」（button），切换到该视图。示例：foxos 3d help show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d help show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_help_show", "arguments": {}}
```

### `3d_layout_show`

Layout。CLI：foxos 3d layout show。界面：主界面 > tablist > Layout。效果：点击「Layout」（tab），切换到该视图。示例：foxos 3d layout show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d layout show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_layout_show", "arguments": {}}
```

### `3d_modeling_show`

Modeling。CLI：foxos 3d modeling show。界面：主界面 > tablist > Modeling。效果：点击「Modeling」（tab），切换到该视图。示例：foxos 3d modeling show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d modeling show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_modeling_show", "arguments": {}}
```

### `3d_sculpting_show`

Sculpting。CLI：foxos 3d sculpting show。界面：主界面 > tablist > Sculpting。效果：点击「Sculpting」（tab），切换到该视图。示例：foxos 3d sculpting show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d sculpting show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_sculpting_show", "arguments": {}}
```

### `3d_uv-editing_show`

UV Editing。CLI：foxos 3d uv-editing show。界面：主界面 > tablist > UV Editing。效果：点击「UV Editing」（tab），切换到该视图。示例：foxos 3d uv-editing show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d uv-editing show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_uv-editing_show", "arguments": {}}
```

### `3d_texture-paint_show`

Texture Paint。CLI：foxos 3d texture-paint show。界面：主界面 > tablist > Texture Paint。效果：点击「Texture Paint」（tab），切换到该视图。示例：foxos 3d texture-paint show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d texture-paint show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_texture-paint_show", "arguments": {}}
```

### `3d_shading_show`

Shading。CLI：foxos 3d shading show。界面：主界面 > tablist > Shading。效果：点击「Shading」（tab），切换到该视图。示例：foxos 3d shading show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d shading show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_shading_show", "arguments": {}}
```

### `3d_animation_show`

Animation。CLI：foxos 3d animation show。界面：主界面 > tablist > Animation。效果：点击「Animation」（tab），切换到该视图。示例：foxos 3d animation show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d animation show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_animation_show", "arguments": {}}
```

### `3d_rendering_show`

Rendering。CLI：foxos 3d rendering show。界面：主界面 > tablist > Rendering。效果：点击「Rendering」（tab），切换到该视图。示例：foxos 3d rendering show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d rendering show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rendering_show", "arguments": {}}
```

### `3d_compositing_show`

Compositing。CLI：foxos 3d compositing show。界面：主界面 > tablist > Compositing。效果：点击「Compositing」（tab），切换到该视图。示例：foxos 3d compositing show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d compositing show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_compositing_show", "arguments": {}}
```

### `3d_geometry-nodes_show`

Geometry Nodes。CLI：foxos 3d geometry-nodes show。界面：主界面 > tablist > Geometry Nodes。效果：点击「Geometry Nodes」（tab），切换到该视图。示例：foxos 3d geometry-nodes show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d geometry-nodes show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_geometry-nodes_show", "arguments": {}}
```

### `3d_scripting_show`

Scripting。CLI：foxos 3d scripting show。界面：主界面 > tablist > Scripting。效果：点击「Scripting」（tab），切换到该视图。示例：foxos 3d scripting show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d scripting show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scripting_show", "arguments": {}}
```

### `3d_workspace_create`

Add Workspace。CLI：foxos 3d workspace create。界面：主界面 > Add Workspace。效果：点击「Add Workspace」（button）。示例：foxos 3d workspace create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d workspace create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_workspace_create", "arguments": {}}
```

### `3d_assistant_activate`

Assistant。CLI：foxos 3d assistant activate。界面：主界面 > header > Assistant。效果：点击「Assistant」（button）。示例：foxos 3d assistant activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d assistant activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_assistant_activate", "arguments": {}}
```

### `3d_pin-scene-workspace_activate`

Pin Scene to Workspace。CLI：foxos 3d pin-scene-workspace activate。界面：主界面 > Pin Scene to Workspace。效果：点击「Pin Scene to Workspace」（button）。示例：foxos 3d pin-scene-workspace activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pin-scene-workspace activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_pin-scene-workspace_activate", "arguments": {}}
```

### `3d_scene_activate`

Scene。CLI：foxos 3d scene activate。界面：主界面 > Scene。效果：点击「Scene」（button）。示例：foxos 3d scene activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scene_activate", "arguments": {}}
```

### `3d_scene_set`

Scene。CLI：foxos 3d scene set VALUE [--submit]。界面：主界面 > header > Scene。效果：把「Scene」设为给定值（触发 input / change 事件）。示例：foxos 3d scene set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Scene」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scene_set", "arguments": {"value": "…"}}
```

### `3d_scene_create`

New Scene。CLI：foxos 3d scene create。界面：主界面 > New Scene。效果：点击「New Scene」（button）。示例：foxos 3d scene create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scene_create", "arguments": {}}
```

### `3d_scene_delete`

Delete Scene。CLI：foxos 3d scene delete。界面：主界面 > Delete Scene。效果：点击「Delete Scene」（button）。示例：foxos 3d scene delete --json

只读：否 · 破坏性：是 · CLI：`foxos 3d scene delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scene_delete", "arguments": {}}
```

### `3d_layer_show`

View Layer。CLI：foxos 3d layer show。界面：主界面 > View Layer。效果：点击「View Layer」（button），切换到该视图。示例：foxos 3d layer show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d layer show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_layer_show", "arguments": {}}
```

### `3d_viewlayer_set`

ViewLayer。CLI：foxos 3d viewlayer set VALUE [--submit]。界面：主界面 > header > ViewLayer。效果：把「ViewLayer」设为给定值（触发 input / change 事件）。示例：foxos 3d viewlayer set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d viewlayer set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「ViewLayer」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_viewlayer_set", "arguments": {"value": "…"}}
```

### `3d_view-layer_create`

Add View Layer。CLI：foxos 3d view-layer create。界面：主界面 > Add View Layer。效果：点击「Add View Layer」（button）。示例：foxos 3d view-layer create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d view-layer create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_view-layer_create", "arguments": {}}
```

### `3d_view-layer_delete`

Remove View Layer。CLI：foxos 3d view-layer delete。界面：主界面 > Remove View Layer。效果：点击「Remove View Layer」（button）。示例：foxos 3d view-layer delete --json

只读：否 · 破坏性：是 · CLI：`foxos 3d view-layer delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_view-layer_delete", "arguments": {}}
```

### `3d_object-mode_activate`

Object Mode。CLI：foxos 3d object-mode activate。界面：主界面 > main > Object Mode。效果：点击「Object Mode」（button）。示例：foxos 3d object-mode activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d object-mode activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_object-mode_activate", "arguments": {}}
```

### `3d_view-2_show`

View。CLI：foxos 3d view-2 show。界面：主界面 > main > View。效果：点击「View」（button），切换到该视图。示例：foxos 3d view-2 show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d view-2 show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_view-2_show", "arguments": {}}
```

### `3d_select_select`

Select。CLI：foxos 3d select select。界面：主界面 > main > Select。效果：点击「Select」（button）。示例：foxos 3d select select --json

只读：是 · 破坏性：否 · CLI：`foxos 3d select select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_select_select", "arguments": {}}
```

### `3d_add_create`

Add。CLI：foxos 3d add create。界面：主界面 > main > Add。效果：点击「Add」（button）。示例：foxos 3d add create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d add create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_add_create", "arguments": {}}
```

### `3d_object_activate`

Object。CLI：foxos 3d object activate。界面：主界面 > main > Object。效果：点击「Object」（button）。示例：foxos 3d object activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d object activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_object_activate", "arguments": {}}
```

### `3d_global_activate`

Global。CLI：foxos 3d global activate。界面：主界面 > main > Global。效果：点击「Global」（button）。示例：foxos 3d global activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d global activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_global_activate", "arguments": {}}
```

### `3d_options_activate`

Options。CLI：foxos 3d options activate。界面：主界面 > main > Options。效果：点击「Options」（button）。示例：foxos 3d options activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d options activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_options_activate", "arguments": {}}
```

### `3d_marker_activate`

Marker。CLI：foxos 3d marker activate。界面：主界面 > main > Marker。效果：点击「Marker」（button）。示例：foxos 3d marker activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d marker activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_marker_activate", "arguments": {}}
```

### `3d_playback_activate`

Playback。CLI：foxos 3d playback activate。界面：主界面 > main > Playback。效果：点击「Playback」（button）。示例：foxos 3d playback activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d playback activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_playback_activate", "arguments": {}}
```

### `3d_search_set`

Search。CLI：foxos 3d search set VALUE [--submit]。界面：主界面 > main > Search。效果：把「Search」设为给定值（触发 input / change 事件）。示例：foxos 3d search set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d search set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Search」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_search_set", "arguments": {"value": "…"}}
```

### `3d_collapse_collapse`

Collapse。CLI：foxos 3d collapse collapse。界面：主界面 > Collapse。效果：点击「Collapse」（button）。示例：foxos 3d collapse collapse --json

只读：是 · 破坏性：否 · CLI：`foxos 3d collapse collapse`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_collapse_collapse", "arguments": {}}
```

### `3d_expand_expand`

Expand。CLI：foxos 3d expand expand。界面：主界面 > Expand。效果：点击「Expand」（button）。示例：foxos 3d expand expand --json

只读：是 · 破坏性：否 · CLI：`foxos 3d expand expand`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_expand_expand", "arguments": {}}
```

### `3d_menus_activate`

Menus。CLI：foxos 3d menus activate。界面：主界面 > Menus。效果：点击「Menus」（button）。示例：foxos 3d menus activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d menus activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_menus_activate", "arguments": {}}
```

### `3d_search-ctrl-f_set`

Search (Ctrl F)。CLI：foxos 3d search-ctrl-f set VALUE [--submit]。界面：主界面 > main > Search (Ctrl F)。效果：把「Search (Ctrl F)」设为给定值（触发 input / change 事件）。示例：foxos 3d search-ctrl-f set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d search-ctrl-f set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Search (Ctrl F)」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_search-ctrl-f_set", "arguments": {"value": "…"}}
```

### `3d_cube_set`

Cube。CLI：foxos 3d cube set VALUE [--submit]。界面：主界面 > main > Cube。效果：把「Cube」设为给定值（触发 input / change 事件）。示例：foxos 3d cube set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cube set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Cube」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_cube_set", "arguments": {"value": "…"}}
```

### `3d_location-x_lock`

Lock Location X。CLI：foxos 3d location-x lock。界面：主界面 > Lock Location X。效果：点击「Lock Location X」（button）。示例：foxos 3d location-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-x lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_location-x_lock", "arguments": {}}
```

### `3d_location-y_lock`

Lock Location Y。CLI：foxos 3d location-y lock。界面：主界面 > Lock Location Y。效果：点击「Lock Location Y」（button）。示例：foxos 3d location-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-y lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_location-y_lock", "arguments": {}}
```

### `3d_location-z_lock`

Lock Location Z。CLI：foxos 3d location-z lock。界面：主界面 > Lock Location Z。效果：点击「Lock Location Z」（button）。示例：foxos 3d location-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-z lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_location-z_lock", "arguments": {}}
```

### `3d_rotation-x_lock`

Lock Rotation X。CLI：foxos 3d rotation-x lock。界面：主界面 > Lock Rotation X。效果：点击「Lock Rotation X」（button）。示例：foxos 3d rotation-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-x lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rotation-x_lock", "arguments": {}}
```

### `3d_rotation-y_lock`

Lock Rotation Y。CLI：foxos 3d rotation-y lock。界面：主界面 > Lock Rotation Y。效果：点击「Lock Rotation Y」（button）。示例：foxos 3d rotation-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-y lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rotation-y_lock", "arguments": {}}
```

### `3d_rotation-z_lock`

Lock Rotation Z。CLI：foxos 3d rotation-z lock。界面：主界面 > Lock Rotation Z。效果：点击「Lock Rotation Z」（button）。示例：foxos 3d rotation-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-z lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rotation-z_lock", "arguments": {}}
```

### `3d_xyz-euler_activate`

XYZ Euler。CLI：foxos 3d xyz-euler activate。界面：主界面 > main > XYZ Euler。效果：点击「XYZ Euler」（button）。示例：foxos 3d xyz-euler activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d xyz-euler activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_xyz-euler_activate", "arguments": {}}
```

### `3d_scale-x_lock`

Lock Scale X。CLI：foxos 3d scale-x lock。界面：主界面 > Lock Scale X。效果：点击「Lock Scale X」（button）。示例：foxos 3d scale-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-x lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scale-x_lock", "arguments": {}}
```

### `3d_scale-y_lock`

Lock Scale Y。CLI：foxos 3d scale-y lock。界面：主界面 > Lock Scale Y。效果：点击「Lock Scale Y」（button）。示例：foxos 3d scale-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-y lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scale-y_lock", "arguments": {}}
```

### `3d_scale-z_lock`

Lock Scale Z。CLI：foxos 3d scale-z lock。界面：主界面 > Lock Scale Z。效果：点击「Lock Scale Z」（button）。示例：foxos 3d scale-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-z lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scale-z_lock", "arguments": {}}
```

### `3d_ai-model_set`

AI model。CLI：foxos 3d ai-model set VALUE [--submit]。界面：主界面 > AI model。效果：把「AI model」设为给定值（触发 input / change 事件）。示例：foxos 3d ai-model set claude-fable-5-1 --json

只读：否 · 破坏性：否 · CLI：`foxos 3d ai-model set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「AI model」的新值 可选：claude-fable-5-1 / claude-opus-5-5 / claude-sonnet-5-5 / claude-haiku-5-5 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ai-model_set", "arguments": {"value": "claude-fable-5-1"}}
```

### `3d_chat_create`

New chat。CLI：foxos 3d chat create。界面：主界面 > New chat。效果：点击「New chat」（button）。示例：foxos 3d chat create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d chat create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_chat_create", "arguments": {}}
```

### `3d_assistant_close`

Close the assistant。CLI：foxos 3d assistant close。界面：主界面 > Close the assistant。效果：点击「Close the assistant」（button）。示例：foxos 3d assistant close --json

只读：是 · 破坏性：否 · CLI：`foxos 3d assistant close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_assistant_close", "arguments": {}}
```

### `3d_wooden-dining-table-four-chairs_activate`

A wooden dining table with four chairs。CLI：foxos 3d wooden-dining-table-four-chairs activate。界面：主界面 > Conversation > A wooden dining table with four chairs。效果：点击「A wooden dining table with four chairs」（button）。示例：foxos 3d wooden-dining-table-four-chairs activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d wooden-dining-table-four-chairs activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_wooden-dining-table-four-chairs_activate", "arguments": {}}
```

### `3d_snowman-carrot-nose-scarf_activate`

A snowman with a carrot nose and a scarf。CLI：foxos 3d snowman-carrot-nose-scarf activate。界面：主界面 > Conversation > A snowman with a carrot nose and a scarf。效果：点击「A snowman with a carrot nose and a scarf」（button）。示例：foxos 3d snowman-carrot-nose-scarf activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d snowman-carrot-nose-scarf activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_snowman-carrot-nose-scarf_activate", "arguments": {}}
```

### `3d_attach-files_activate`

Attach files。CLI：foxos 3d attach-files activate。界面：主界面 > Attach files。效果：点击「Attach files」（button）。示例：foxos 3d attach-files activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d attach-files activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_attach-files_activate", "arguments": {}}
```

### `3d_message-assistant_set`

Message the assistant。CLI：foxos 3d message-assistant set VALUE [--submit]。界面：主界面 > Message the assistant。效果：把「Message the assistant」设为给定值（触发 input / change 事件）。示例：foxos 3d message-assistant set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d message-assistant set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Message the assistant」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_message-assistant_set", "arguments": {"value": "…"}}
```

### `3d_send_send`

Send。CLI：foxos 3d send send。界面：主界面 > Send。效果：点击「Send」（button）。示例：foxos 3d send send --json

只读：否 · 破坏性：否 · CLI：`foxos 3d send send`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_send_send", "arguments": {}}
```

### `3d_default_activate`

Default。CLI：foxos 3d default activate。界面：主界面 > Welcome > Default。效果：点击「Default」（button）。示例：foxos 3d default activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d default activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_default_activate", "arguments": {}}
```

### `3d_graphite_activate`

Graphite。CLI：foxos 3d graphite activate。界面：主界面 > Welcome > Graphite。效果：点击「Graphite」（button）。示例：foxos 3d graphite activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d graphite activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_graphite_activate", "arguments": {}}
```

### `3d_midnight_activate`

Midnight。CLI：foxos 3d midnight activate。界面：主界面 > Welcome > Midnight。效果：点击「Midnight」（button）。示例：foxos 3d midnight activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d midnight activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_midnight_activate", "arguments": {}}
```

### `3d_light_activate`

Light。CLI：foxos 3d light activate。界面：主界面 > Welcome > Light。效果：点击「Light」（button）。示例：foxos 3d light activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d light activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_light_activate", "arguments": {}}
```

### `3d_high-contrast_activate`

High Contrast。CLI：foxos 3d high-contrast activate。界面：主界面 > Welcome > High Contrast。效果：点击「High Contrast」（button）。示例：foxos 3d high-contrast activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d high-contrast activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_high-contrast_activate", "arguments": {}}
```

### `3d_compact_activate`

Compact。CLI：foxos 3d compact activate。界面：主界面 > Welcome > Compact。效果：点击「Compact」（button）。示例：foxos 3d compact activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d compact activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_compact_activate", "arguments": {}}
```

### `3d_normal_activate`

Normal。CLI：foxos 3d normal activate。界面：主界面 > Welcome > Normal。效果：点击「Normal」（button）。示例：foxos 3d normal activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d normal activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_normal_activate", "arguments": {}}
```

### `3d_large_activate`

Large。CLI：foxos 3d large activate。界面：主界面 > Welcome > Large。效果：点击「Large」（button）。示例：foxos 3d large activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d large activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_large_activate", "arguments": {}}
```

### `3d_larger_activate`

Larger。CLI：foxos 3d larger activate。界面：主界面 > Welcome > Larger。效果：点击「Larger」（button）。示例：foxos 3d larger activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d larger activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_larger_activate", "arguments": {}}
```

### `3d_play_play`

Play。CLI：foxos 3d play play。界面：主界面 > Welcome > Play。效果：点击「Play」（button）。示例：foxos 3d play play --json

只读：否 · 破坏性：否 · CLI：`foxos 3d play play`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_play_play", "arguments": {}}
```

### `3d_tools_activate`

Tools。CLI：foxos 3d tools activate。界面：主界面 > Welcome > Tools。效果：点击「Tools」（button）。示例：foxos 3d tools activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d tools activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_tools_activate", "arguments": {}}
```

### `3d_search_search`

Search。CLI：foxos 3d search search。界面：主界面 > Welcome > Search。效果：点击「Search」（button）。示例：foxos 3d search search --json

只读：是 · 破坏性：否 · CLI：`foxos 3d search search`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_search_search", "arguments": {}}
```

### `3d_continue_activate`

Continue。CLI：foxos 3d continue activate。界面：主界面 > Welcome > Continue。效果：点击「Continue」（button）。示例：foxos 3d continue activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d continue activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_continue_activate", "arguments": {}}
```

### `3d_newctrl-n_activate`

NewCtrl N。CLI：foxos 3d newctrl-n activate。界面：File > menu > NewCtrl N。效果：点击「NewCtrl N」（menuitem）。示例：foxos 3d newctrl-n activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d newctrl-n activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_newctrl-n_activate", "arguments": {}}
```

### `3d_ctrl-o_open`

Open…Ctrl O。CLI：foxos 3d ctrl-o open。界面：File > menu > Open…Ctrl O。效果：点击「Open…Ctrl O」（menuitem）。示例：foxos 3d ctrl-o open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ctrl-o open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ctrl-o_open", "arguments": {}}
```

### `3d_recentshift-ctrl-o_open`

Open RecentShift Ctrl O。CLI：foxos 3d recentshift-ctrl-o open。界面：File > menu > Open RecentShift Ctrl O。效果：点击「Open RecentShift Ctrl O」（menuitem）。示例：foxos 3d recentshift-ctrl-o open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d recentshift-ctrl-o open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_recentshift-ctrl-o_open", "arguments": {}}
```

### `3d_revert_activate`

Revert。CLI：foxos 3d revert activate。界面：File > menu > Revert。效果：点击「Revert」（menuitem）。示例：foxos 3d revert activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d revert activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_revert_activate", "arguments": {}}
```

### `3d_recover_activate`

Recover。CLI：foxos 3d recover activate。界面：File > menu > Recover。效果：点击「Recover」（menuitem）。示例：foxos 3d recover activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d recover activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_recover_activate", "arguments": {}}
```

### `3d_savectrl-s_activate`

SaveCtrl S。CLI：foxos 3d savectrl-s activate。界面：File > menu > SaveCtrl S。效果：点击「SaveCtrl S」（menuitem）。示例：foxos 3d savectrl-s activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d savectrl-s activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_savectrl-s_activate", "arguments": {}}
```

### `3d_as-shift-ctrl-s_save`

Save As…Shift Ctrl S。CLI：foxos 3d as-shift-ctrl-s save。界面：File > menu > Save As…Shift Ctrl S。效果：点击「Save As…Shift Ctrl S」（menuitem）。示例：foxos 3d as-shift-ctrl-s save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d as-shift-ctrl-s save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_as-shift-ctrl-s_save", "arguments": {}}
```

### `3d_copy_save`

Save Copy…。CLI：foxos 3d copy save。界面：File > menu > Save Copy…。效果：点击「Save Copy…」（menuitem）。示例：foxos 3d copy save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d copy save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_copy_save", "arguments": {}}
```

### `3d_incrementalctrl-alt-s_save`

Save IncrementalCtrl Alt S。CLI：foxos 3d incrementalctrl-alt-s save。界面：File > menu > Save IncrementalCtrl Alt S。效果：点击「Save IncrementalCtrl Alt S」（menuitem）。示例：foxos 3d incrementalctrl-alt-s save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d incrementalctrl-alt-s save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_incrementalctrl-alt-s_save", "arguments": {}}
```

### `3d_link_activate`

Link…。CLI：foxos 3d link activate。界面：File > menu > Link…。效果：点击「Link…」（menuitem）。示例：foxos 3d link activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d link activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_link_activate", "arguments": {}}
```

### `3d_append_activate`

Append…。CLI：foxos 3d append activate。界面：File > menu > Append…。效果：点击「Append…」（menuitem）。示例：foxos 3d append activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d append activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_append_activate", "arguments": {}}
```

### `3d_data-previews_activate`

Data Previews。CLI：foxos 3d data-previews activate。界面：File > menu > Data Previews。效果：点击「Data Previews」（menuitem）。示例：foxos 3d data-previews activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d data-previews activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_data-previews_activate", "arguments": {}}
```

### `3d_import_import`

Import。CLI：foxos 3d import import。界面：File > menu > Import。效果：点击「Import」（menuitem）。示例：foxos 3d import import --json

只读：否 · 破坏性：否 · CLI：`foxos 3d import import`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_import_import", "arguments": {}}
```

### `3d_export_export`

Export。CLI：foxos 3d export export。界面：File > menu > Export。效果：点击「Export」（menuitem）。示例：foxos 3d export export --json

只读：否 · 破坏性：否 · CLI：`foxos 3d export export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_export_export", "arguments": {}}
```

### `3d_collections_export`

Export All Collections。CLI：foxos 3d collections export。界面：File > menu > Export All Collections。效果：点击「Export All Collections」（menuitem）。示例：foxos 3d collections export --json

只读：否 · 破坏性：否 · CLI：`foxos 3d collections export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_collections_export", "arguments": {}}
```

### `3d_external-data_activate`

External Data。CLI：foxos 3d external-data activate。界面：File > menu > External Data。效果：点击「External Data」（menuitem）。示例：foxos 3d external-data activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d external-data activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_external-data_activate", "arguments": {}}
```

### `3d_clean-up_activate`

Clean Up。CLI：foxos 3d clean-up activate。界面：File > menu > Clean Up。效果：点击「Clean Up」（menuitem）。示例：foxos 3d clean-up activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clean-up activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_clean-up_activate", "arguments": {}}
```

### `3d_defaults_activate`

Defaults。CLI：foxos 3d defaults activate。界面：File > menu > Defaults。效果：点击「Defaults」（menuitem）。示例：foxos 3d defaults activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d defaults activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_defaults_activate", "arguments": {}}
```

### `3d_quitctrl-q_activate`

QuitCtrl Q。CLI：foxos 3d quitctrl-q activate。界面：File > menu > QuitCtrl Q。效果：点击「QuitCtrl Q」（menuitem）。示例：foxos 3d quitctrl-q activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d quitctrl-q activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_quitctrl-q_activate", "arguments": {}}
```

### `3d_undoctrl-z_activate`

UndoCtrl Z。CLI：foxos 3d undoctrl-z activate。界面：Edit > menu > UndoCtrl Z。效果：点击「UndoCtrl Z」（menuitem）。示例：foxos 3d undoctrl-z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d undoctrl-z activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_undoctrl-z_activate", "arguments": {}}
```

### `3d_redoshift-ctrl-z_activate`

RedoShift Ctrl Z。CLI：foxos 3d redoshift-ctrl-z activate。界面：Edit > menu > RedoShift Ctrl Z。效果：点击「RedoShift Ctrl Z」（menuitem）。示例：foxos 3d redoshift-ctrl-z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d redoshift-ctrl-z activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_redoshift-ctrl-z_activate", "arguments": {}}
```

### `3d_historyctrl-alt-z_undo`

Undo HistoryCtrl Alt Z。CLI：foxos 3d historyctrl-alt-z undo。界面：Edit > menu > Undo HistoryCtrl Alt Z。效果：点击「Undo HistoryCtrl Alt Z」（menuitem）。示例：foxos 3d historyctrl-alt-z undo --json

只读：否 · 破坏性：否 · CLI：`foxos 3d historyctrl-alt-z undo`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_historyctrl-alt-z_undo", "arguments": {}}
```

### `3d_repeat-lastshift-r_activate`

Repeat LastShift R。CLI：foxos 3d repeat-lastshift-r activate。界面：Edit > menu > Repeat LastShift R。效果：点击「Repeat LastShift R」（menuitem）。示例：foxos 3d repeat-lastshift-r activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d repeat-lastshift-r activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_repeat-lastshift-r_activate", "arguments": {}}
```

### `3d_repeat-history_activate`

Repeat History…。CLI：foxos 3d repeat-history activate。界面：Edit > menu > Repeat History…。效果：点击「Repeat History…」（menuitem）。示例：foxos 3d repeat-history activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d repeat-history activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_repeat-history_activate", "arguments": {}}
```

### `3d_preferences-ctrl_activate`

Preferences…Ctrl ,。CLI：foxos 3d preferences-ctrl activate。界面：Edit > menu > Preferences…Ctrl ,。效果：点击「Preferences…Ctrl ,」（menuitem）。示例：foxos 3d preferences-ctrl activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d preferences-ctrl activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_preferences-ctrl_activate", "arguments": {}}
```

### `3d_render-audio_activate`

Render Audio…。CLI：foxos 3d render-audio activate。界面：Render > menu > Render Audio…。效果：点击「Render Audio…」（menuitem）。示例：foxos 3d render-audio activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render-audio activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_render-audio_activate", "arguments": {}}
```

### `3d_interface_lock`

Lock Interface。CLI：foxos 3d interface lock。界面：Render > menu > Lock Interface。效果：点击「Lock Interface」（menuitem）。示例：foxos 3d interface lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d interface lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_interface_lock", "arguments": {}}
```

### `3d_window_create`

New Window。CLI：foxos 3d window create。界面：Window > menu > New Window。效果：点击「New Window」（menuitem）。示例：foxos 3d window create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_window_create", "arguments": {}}
```

### `3d_main-window_create`

New Main Window。CLI：foxos 3d main-window create。界面：Window > menu > New Main Window。效果：点击「New Main Window」（menuitem）。示例：foxos 3d main-window create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d main-window create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_main-window_create", "arguments": {}}
```

### `3d_window-fullscreen_toggle`

Toggle Window Fullscreen。CLI：foxos 3d window-fullscreen toggle。界面：Window > menu > Toggle Window Fullscreen。效果：切换「Toggle Window Fullscreen」。示例：foxos 3d window-fullscreen toggle --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window-fullscreen toggle`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_window-fullscreen_toggle", "arguments": {}}
```

### `3d_workspacectrl-page-down_next`

Next WorkspaceCtrl Page Down。CLI：foxos 3d workspacectrl-page-down next。界面：Window > menu > Next WorkspaceCtrl Page Down。效果：点击「Next WorkspaceCtrl Page Down」（menuitem）。示例：foxos 3d workspacectrl-page-down next --json

只读：是 · 破坏性：否 · CLI：`foxos 3d workspacectrl-page-down next`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_workspacectrl-page-down_next", "arguments": {}}
```

### `3d_workspacectrl-page-up_previous`

Previous WorkspaceCtrl Page Up。CLI：foxos 3d workspacectrl-page-up previous。界面：Window > menu > Previous WorkspaceCtrl Page Up。效果：点击「Previous WorkspaceCtrl Page Up」（menuitem）。示例：foxos 3d workspacectrl-page-up previous --json

只读：是 · 破坏性：否 · CLI：`foxos 3d workspacectrl-page-up previous`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_workspacectrl-page-up_previous", "arguments": {}}
```

### `3d_status-bar_show`

Show Status Bar。CLI：foxos 3d status-bar show。界面：Window > menu > Show Status Bar。效果：点击「Show Status Bar」（menuitem），切换到该视图。示例：foxos 3d status-bar show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d status-bar show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_status-bar_show", "arguments": {}}
```

### `3d_status-bar-scene-statistics_activate`

Status Bar Scene Statistics。CLI：foxos 3d status-bar-scene-statistics activate。界面：Window > menu > Status Bar Scene Statistics。效果：点击「Status Bar Scene Statistics」（menuitem）。示例：foxos 3d status-bar-scene-statistics activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d status-bar-scene-statistics activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_status-bar-scene-statistics_activate", "arguments": {}}
```

### `3d_ai-assistant_activate`

AI Assistant。CLI：foxos 3d ai-assistant activate。界面：Window > menu > AI Assistant。效果：点击「AI Assistant」（menuitem）。示例：foxos 3d ai-assistant activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d ai-assistant activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_ai-assistant_activate", "arguments": {}}
```

### `3d_screenshot_save`

Save Screenshot。CLI：foxos 3d screenshot save。界面：Window > menu > Save Screenshot。效果：点击「Save Screenshot」（menuitem）。示例：foxos 3d screenshot save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d screenshot save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_screenshot_save", "arguments": {}}
```

### `3d_screenshot-editor_save`

Save Screenshot (Editor)。CLI：foxos 3d screenshot-editor save。界面：Window > menu > Save Screenshot (Editor)。效果：点击「Save Screenshot (Editor)」（menuitem）。示例：foxos 3d screenshot-editor save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d screenshot-editor save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_screenshot-editor_save", "arguments": {}}
```

### `3d_keyboard-shortcuts_activate`

Keyboard Shortcuts。CLI：foxos 3d keyboard-shortcuts activate。界面：Help > menu > Keyboard Shortcuts。效果：点击「Keyboard Shortcuts」（menuitem）。示例：foxos 3d keyboard-shortcuts activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d keyboard-shortcuts activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_keyboard-shortcuts_activate", "arguments": {}}
```

### `3d_report-bug_activate`

Report a Bug。CLI：foxos 3d report-bug activate。界面：Help > menu > Report a Bug。效果：点击「Report a Bug」（menuitem）。示例：foxos 3d report-bug activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d report-bug activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_report-bug_activate", "arguments": {}}
```

### `3d_system-info_save`

Save System Info。CLI：foxos 3d system-info save。界面：Help > menu > Save System Info。效果：点击「Save System Info」（menuitem）。示例：foxos 3d system-info save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d system-info save`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_system-info_save", "arguments": {}}
```

### `3d_about_show`

About。CLI：foxos 3d about show。界面：Help > menu > About。效果：点击「About」（menuitem），切换到该视图。示例：foxos 3d about show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d about show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_about_show", "arguments": {}}
```

### `3d_mode_update`

Edit Mode。CLI：foxos 3d mode update。界面：Modeling > main > Edit Mode。效果：点击「Edit Mode」（button）。示例：foxos 3d mode update --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mode update`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_mode_update", "arguments": {}}
```

### `3d_x_activate`

X。CLI：foxos 3d x activate。界面：Modeling > main > X。效果：点击「X」（button）。示例：foxos 3d x activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d x activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_x_activate", "arguments": {}}
```

### `3d_y_activate`

Y。CLI：foxos 3d y activate。界面：Modeling > main > Y。效果：点击「Y」（button）。示例：foxos 3d y activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d y activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_y_activate", "arguments": {}}
```

### `3d_z_activate`

Z。CLI：foxos 3d z activate。界面：Modeling > main > Z。效果：点击「Z」（button）。示例：foxos 3d z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d z activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_z_activate", "arguments": {}}
```

### `3d_modifier_create`

Add Modifier。CLI：foxos 3d modifier create。界面：Modeling > main > Add Modifier。效果：点击「Add Modifier」（button）。示例：foxos 3d modifier create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d modifier create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_modifier_create", "arguments": {}}
```

### `3d_sculpt-mode_activate`

Sculpt Mode。CLI：foxos 3d sculpt-mode activate。界面：Sculpting > main > Sculpt Mode。效果：点击「Sculpt Mode」（button）。示例：foxos 3d sculpt-mode activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpt-mode activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_sculpt-mode_activate", "arguments": {}}
```

### `3d_sculpt_activate`

Sculpt。CLI：foxos 3d sculpt activate。界面：Sculpting > main > Sculpt。效果：点击「Sculpt」（button）。示例：foxos 3d sculpt activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpt activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_sculpt_activate", "arguments": {}}
```

### `3d_mask_activate`

Mask。CLI：foxos 3d mask activate。界面：Sculpting > main > Mask。效果：点击「Mask」（button）。示例：foxos 3d mask activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mask activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_mask_activate", "arguments": {}}
```

### `3d_face-sets_activate`

Face Sets。CLI：foxos 3d face-sets activate。界面：Sculpting > main > Face Sets。效果：点击「Face Sets」（button）。示例：foxos 3d face-sets activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d face-sets activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_face-sets_activate", "arguments": {}}
```

### `3d_brush_activate`

Brush。CLI：foxos 3d brush activate。界面：Sculpting > main > Brush。效果：点击「Brush」（button）。示例：foxos 3d brush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d brush activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_brush_activate", "arguments": {}}
```

### `3d_texture_activate`

Texture。CLI：foxos 3d texture activate。界面：Sculpting > main > Texture。效果：点击「Texture」（button）。示例：foxos 3d texture activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d texture activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_texture_activate", "arguments": {}}
```

### `3d_stroke_activate`

Stroke。CLI：foxos 3d stroke activate。界面：Sculpting > main > Stroke。效果：点击「Stroke」（button）。示例：foxos 3d stroke activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d stroke activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_stroke_activate", "arguments": {}}
```

### `3d_falloff_activate`

Falloff。CLI：foxos 3d falloff activate。界面：Sculpting > main > Falloff。效果：点击「Falloff」（button）。示例：foxos 3d falloff activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d falloff activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_falloff_activate", "arguments": {}}
```

### `3d_cursor_activate`

Cursor。CLI：foxos 3d cursor activate。界面：Sculpting > main > Cursor。效果：点击「Cursor」（button）。示例：foxos 3d cursor activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cursor activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_cursor_activate", "arguments": {}}
```

### `3d_remesh_activate`

Remesh。CLI：foxos 3d remesh activate。界面：Sculpting > main > Remesh。效果：点击「Remesh」（button）。示例：foxos 3d remesh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d remesh activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_remesh_activate", "arguments": {}}
```

### `3d_subtract_create`

Add/Subtract。CLI：foxos 3d subtract create。界面：Sculpting > main > Add/Subtract。效果：点击「Add/Subtract」（button）。示例：foxos 3d subtract create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d subtract create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_subtract_create", "arguments": {}}
```

### `3d_contrast-smooth_activate`

Contrast & Smooth。CLI：foxos 3d contrast-smooth activate。界面：Sculpting > main > Contrast & Smooth。效果：点击「Contrast & Smooth」（button）。示例：foxos 3d contrast-smooth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d contrast-smooth activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_contrast-smooth_activate", "arguments": {}}
```

### `3d_transform_activate`

Transform。CLI：foxos 3d transform activate。界面：Sculpting > main > Transform。效果：点击「Transform」（button）。示例：foxos 3d transform activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d transform activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_transform_activate", "arguments": {}}
```

### `3d_simplify_activate`

Simplify。CLI：foxos 3d simplify activate。界面：Sculpting > main > Simplify。效果：点击「Simplify」（button）。示例：foxos 3d simplify activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d simplify activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_simplify_activate", "arguments": {}}
```

### `3d_utilities_activate`

Utilities。CLI：foxos 3d utilities activate。界面：Sculpting > main > Utilities。效果：点击「Utilities」（button）。示例：foxos 3d utilities activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d utilities activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_utilities_activate", "arguments": {}}
```

### `3d_paint_activate`

Paint。CLI：foxos 3d paint activate。界面：Sculpting > main > Paint。效果：点击「Paint」（button）。示例：foxos 3d paint activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d paint activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_paint_activate", "arguments": {}}
```

### `3d_assets_activate`

Assets。CLI：foxos 3d assets activate。界面：Sculpting > main > Assets。效果：点击「Assets」（button）。示例：foxos 3d assets activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d assets activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_assets_activate", "arguments": {}}
```

### `3d_draw_draw`

Draw。CLI：foxos 3d draw draw。界面：Sculpting > main > Draw。效果：点击「Draw」（button）。示例：foxos 3d draw draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d draw draw`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_draw_draw", "arguments": {}}
```

### `3d_sharp_draw`

Draw Sharp。CLI：foxos 3d sharp draw。界面：Sculpting > main > Draw Sharp。效果：点击「Draw Sharp」（button）。示例：foxos 3d sharp draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sharp draw`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_sharp_draw", "arguments": {}}
```

### `3d_clay_activate`

Clay。CLI：foxos 3d clay activate。界面：Sculpting > main > Clay。效果：点击「Clay」（button）。示例：foxos 3d clay activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_clay_activate", "arguments": {}}
```

### `3d_clay-strips_activate`

Clay Strips。CLI：foxos 3d clay-strips activate。界面：Sculpting > main > Clay Strips。效果：点击「Clay Strips」（button）。示例：foxos 3d clay-strips activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay-strips activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_clay-strips_activate", "arguments": {}}
```

### `3d_clay-thumb_activate`

Clay Thumb。CLI：foxos 3d clay-thumb activate。界面：Sculpting > main > Clay Thumb。效果：点击「Clay Thumb」（button）。示例：foxos 3d clay-thumb activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay-thumb activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_clay-thumb_activate", "arguments": {}}
```

### `3d_layer_activate`

Layer。CLI：foxos 3d layer activate。界面：Sculpting > main > Layer。效果：点击「Layer」（button）。示例：foxos 3d layer activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d layer activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_layer_activate", "arguments": {}}
```

### `3d_inflate-deflate_activate`

Inflate/Deflate。CLI：foxos 3d inflate-deflate activate。界面：Sculpting > main > Inflate/Deflate。效果：点击「Inflate/Deflate」（button）。示例：foxos 3d inflate-deflate activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d inflate-deflate activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_inflate-deflate_activate", "arguments": {}}
```

### `3d_blob_activate`

Blob。CLI：foxos 3d blob activate。界面：Sculpting > main > Blob。效果：点击「Blob」（button）。示例：foxos 3d blob activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d blob activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_blob_activate", "arguments": {}}
```

### `3d_crease_activate`

Crease。CLI：foxos 3d crease activate。界面：Sculpting > main > Crease。效果：点击「Crease」（button）。示例：foxos 3d crease activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d crease activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_crease_activate", "arguments": {}}
```

### `3d_smooth_activate`

Smooth。CLI：foxos 3d smooth activate。界面：Sculpting > main > Smooth。效果：点击「Smooth」（button）。示例：foxos 3d smooth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d smooth activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_smooth_activate", "arguments": {}}
```

### `3d_flatten-contrast_activate`

Flatten/Contrast。CLI：foxos 3d flatten-contrast activate。界面：Sculpting > main > Flatten/Contrast。效果：点击「Flatten/Contrast」（button）。示例：foxos 3d flatten-contrast activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d flatten-contrast activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_flatten-contrast_activate", "arguments": {}}
```

### `3d_fill-deepen_activate`

Fill/Deepen。CLI：foxos 3d fill-deepen activate。界面：Sculpting > main > Fill/Deepen。效果：点击「Fill/Deepen」（button）。示例：foxos 3d fill-deepen activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d fill-deepen activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_fill-deepen_activate", "arguments": {}}
```

### `3d_scrape-peaks_activate`

Scrape/Peaks。CLI：foxos 3d scrape-peaks activate。界面：Sculpting > main > Scrape/Peaks。效果：点击「Scrape/Peaks」（button）。示例：foxos 3d scrape-peaks activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scrape-peaks activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scrape-peaks_activate", "arguments": {}}
```

### `3d_multiplane-scrape_activate`

Multiplane Scrape。CLI：foxos 3d multiplane-scrape activate。界面：Sculpting > main > Multiplane Scrape。效果：点击「Multiplane Scrape」（button）。示例：foxos 3d multiplane-scrape activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d multiplane-scrape activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_multiplane-scrape_activate", "arguments": {}}
```

### `3d_pinch-magnify_activate`

Pinch/Magnify。CLI：foxos 3d pinch-magnify activate。界面：Sculpting > main > Pinch/Magnify。效果：点击「Pinch/Magnify」（button）。示例：foxos 3d pinch-magnify activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pinch-magnify activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_pinch-magnify_activate", "arguments": {}}
```

### `3d_grab_activate`

Grab。CLI：foxos 3d grab activate。界面：Sculpting > main > Grab。效果：点击「Grab」（button）。示例：foxos 3d grab activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d grab activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_grab_activate", "arguments": {}}
```

### `3d_elastic-deform_activate`

Elastic Deform。CLI：foxos 3d elastic-deform activate。界面：Sculpting > main > Elastic Deform。效果：点击「Elastic Deform」（button）。示例：foxos 3d elastic-deform activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d elastic-deform activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_elastic-deform_activate", "arguments": {}}
```

### `3d_snake-hook_activate`

Snake Hook。CLI：foxos 3d snake-hook activate。界面：Sculpting > main > Snake Hook。效果：点击「Snake Hook」（button）。示例：foxos 3d snake-hook activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d snake-hook activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_snake-hook_activate", "arguments": {}}
```

### `3d_thumb_activate`

Thumb。CLI：foxos 3d thumb activate。界面：Sculpting > main > Thumb。效果：点击「Thumb」（button）。示例：foxos 3d thumb activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d thumb activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_thumb_activate", "arguments": {}}
```

### `3d_pose_activate`

Pose。CLI：foxos 3d pose activate。界面：Sculpting > main > Pose。效果：点击「Pose」（button）。示例：foxos 3d pose activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pose activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_pose_activate", "arguments": {}}
```

### `3d_nudge_activate`

Nudge。CLI：foxos 3d nudge activate。界面：Sculpting > main > Nudge。效果：点击「Nudge」（button）。示例：foxos 3d nudge activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d nudge activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_nudge_activate", "arguments": {}}
```

### `3d_rotate_rotate`

Rotate。CLI：foxos 3d rotate rotate。界面：Sculpting > main > Rotate。效果：点击「Rotate」（button）。示例：foxos 3d rotate rotate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotate rotate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rotate_rotate", "arguments": {}}
```

### `3d_boundary_activate`

Boundary。CLI：foxos 3d boundary activate。界面：Sculpting > main > Boundary。效果：点击「Boundary」（button）。示例：foxos 3d boundary activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d boundary activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_boundary_activate", "arguments": {}}
```

### `3d_cloth_activate`

Cloth。CLI：foxos 3d cloth activate。界面：Sculpting > main > Cloth。效果：点击「Cloth」（button）。示例：foxos 3d cloth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cloth activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_cloth_activate", "arguments": {}}
```

### `3d_slide-relax_activate`

Slide Relax。CLI：foxos 3d slide-relax activate。界面：Sculpting > main > Slide Relax。效果：点击「Slide Relax」（button）。示例：foxos 3d slide-relax activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d slide-relax activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_slide-relax_activate", "arguments": {}}
```

### `3d_face-sets_draw`

Draw Face Sets。CLI：foxos 3d face-sets draw。界面：Sculpting > main > Draw Face Sets。效果：点击「Draw Face Sets」（button）。示例：foxos 3d face-sets draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d face-sets draw`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_face-sets_draw", "arguments": {}}
```

### `3d_smear_activate`

Smear。CLI：foxos 3d smear activate。界面：Sculpting > main > Smear。效果：点击「Smear」（button）。示例：foxos 3d smear activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d smear activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_smear_activate", "arguments": {}}
```

### `3d_crisp-crease_activate`

Crisp Crease。CLI：foxos 3d crisp-crease activate。界面：Sculpting > main > Crisp Crease。效果：点击「Crisp Crease」（button）。示例：foxos 3d crisp-crease activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d crisp-crease activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_crisp-crease_activate", "arguments": {}}
```

### `3d_noise-detail_activate`

Noise Detail。CLI：foxos 3d noise-detail activate。界面：Sculpting > main > Noise Detail。效果：点击「Noise Detail」（button）。示例：foxos 3d noise-detail activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d noise-detail activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_noise-detail_activate", "arguments": {}}
```

### `3d_soft-clay_activate`

Soft Clay。CLI：foxos 3d soft-clay activate。界面：Sculpting > main > Soft Clay。效果：点击「Soft Clay」（button）。示例：foxos 3d soft-clay activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d soft-clay activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_soft-clay_activate", "arguments": {}}
```

### `3d_steady-line_activate`

Steady Line。CLI：foxos 3d steady-line activate。界面：Sculpting > main > Steady Line。效果：点击「Steady Line」（button）。示例：foxos 3d steady-line activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d steady-line activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_steady-line_activate", "arguments": {}}
```

### `3d_sculpting-scene_activate`

Scene。CLI：foxos 3d sculpting-scene activate。界面：Sculpting > main > Scene。效果：点击「Scene」（button）。示例：foxos 3d sculpting-scene activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpting-scene activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_sculpting-scene_activate", "arguments": {}}
```

### `3d_voxel-remesh_activate`

Voxel Remesh。CLI：foxos 3d voxel-remesh activate。界面：Sculpting > main > Voxel Remesh。效果：点击「Voxel Remesh」（button）。示例：foxos 3d voxel-remesh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d voxel-remesh activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_voxel-remesh_activate", "arguments": {}}
```

### `3d_x-x_activate`

-X to +X。CLI：foxos 3d x-x activate。界面：Sculpting > main > -X to +X。效果：点击「-X to +X」（button）。示例：foxos 3d x-x activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d x-x activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_x-x_activate", "arguments": {}}
```

### `3d_symmetrize_activate`

Symmetrize。CLI：foxos 3d symmetrize activate。界面：Sculpting > main > Symmetrize。效果：点击「Symmetrize」（button）。示例：foxos 3d symmetrize activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d symmetrize activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_symmetrize_activate", "arguments": {}}
```

### `3d_shared-location_activate`

Shared Location。CLI：foxos 3d shared-location activate。界面：UV Editing > main > Shared Location。效果：点击「Shared Location」（button）。示例：foxos 3d shared-location activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d shared-location activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_shared-location_activate", "arguments": {}}
```

### `3d_no-image_activate`

No Image。CLI：foxos 3d no-image activate。界面：UV Editing > main > No Image。效果：点击「No Image」（button）。示例：foxos 3d no-image activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d no-image activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_no-image_activate", "arguments": {}}
```

### `3d_material-base-color_set`

Material Base Color。CLI：foxos 3d material-base-color set VALUE [--submit]。界面：Texture Paint > main > Material Base Color。效果：把「Material Base Color」设为给定值（触发 input / change 事件）。示例：foxos 3d material-base-color set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d material-base-color set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Material Base Color」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_material-base-color_set", "arguments": {"value": "…"}}
```

### `3d_mix_activate`

Mix。CLI：foxos 3d mix activate。界面：Texture Paint > main > Mix。效果：点击「Mix」（button）。示例：foxos 3d mix activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mix activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_mix_activate", "arguments": {}}
```

### `3d_texture-paint_activate`

Texture Paint。CLI：foxos 3d texture-paint activate。界面：Texture Paint > main > Texture Paint。效果：点击「Texture Paint」（button）。示例：foxos 3d texture-paint activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d texture-paint activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_texture-paint_activate", "arguments": {}}
```

### `3d_soften_activate`

Soften。CLI：foxos 3d soften activate。界面：Texture Paint > main > Soften。效果：点击「Soften」（button）。示例：foxos 3d soften activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d soften activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_soften_activate", "arguments": {}}
```

### `3d_clone_activate`

Clone。CLI：foxos 3d clone activate。界面：Texture Paint > main > Clone。效果：点击「Clone」（button）。示例：foxos 3d clone activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clone activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_clone_activate", "arguments": {}}
```

### `3d_fill_activate`

Fill。CLI：foxos 3d fill activate。界面：Texture Paint > main > Fill。效果：点击「Fill」（button）。示例：foxos 3d fill activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d fill activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_fill_activate", "arguments": {}}
```

### `3d_airbrush_activate`

Airbrush。CLI：foxos 3d airbrush activate。界面：Texture Paint > main > Airbrush。效果：点击「Airbrush」（button）。示例：foxos 3d airbrush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d airbrush activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_airbrush_activate", "arguments": {}}
```

### `3d_paint-soft-pressure_activate`

Paint Soft Pressure。CLI：foxos 3d paint-soft-pressure activate。界面：Texture Paint > main > Paint Soft Pressure。效果：点击「Paint Soft Pressure」（button）。示例：foxos 3d paint-soft-pressure activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d paint-soft-pressure activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_paint-soft-pressure_activate", "arguments": {}}
```

### `3d_pencil_activate`

Pencil。CLI：foxos 3d pencil activate。界面：Texture Paint > main > Pencil。效果：点击「Pencil」（button）。示例：foxos 3d pencil activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pencil activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_pencil_activate", "arguments": {}}
```

### `3d_red-airbrush_activate`

Red Airbrush。CLI：foxos 3d red-airbrush activate。界面：Texture Paint > main > Red Airbrush。效果：点击「Red Airbrush」（button）。示例：foxos 3d red-airbrush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d red-airbrush activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_red-airbrush_activate", "arguments": {}}
```

### `3d_speckle_activate`

Speckle。CLI：foxos 3d speckle activate。界面：Texture Paint > main > Speckle。效果：点击「Speckle」（button）。示例：foxos 3d speckle activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d speckle activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_speckle_activate", "arguments": {}}
```

### `3d_color_activate`

Color。CLI：foxos 3d color activate。界面：Texture Paint > main > Color。效果：点击「Color」（button）。示例：foxos 3d color activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d color activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_color_activate", "arguments": {}}
```

### `3d_gradient_activate`

Gradient。CLI：foxos 3d gradient activate。界面：Texture Paint > main > Gradient。效果：点击「Gradient」（button）。示例：foxos 3d gradient activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d gradient activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_gradient_activate", "arguments": {}}
```

### `3d_base-color-texture_create`

New Base Color Texture。CLI：foxos 3d base-color-texture create。界面：Texture Paint > main > New Base Color Texture。效果：点击「New Base Color Texture」（button）。示例：foxos 3d base-color-texture create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d base-color-texture create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_base-color-texture_create", "arguments": {}}
```

### `3d_back_previous`

Back。CLI：foxos 3d back previous。界面：Shading > Back。效果：点击「Back」（button）。示例：foxos 3d back previous --json

只读：是 · 破坏性：否 · CLI：`foxos 3d back previous`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_back_previous", "arguments": {}}
```

### `3d_forward_next`

Forward。CLI：foxos 3d forward next。界面：Shading > Forward。效果：点击「Forward」（button）。示例：foxos 3d forward next --json

只读：是 · 破坏性：否 · CLI：`foxos 3d forward next`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_forward_next", "arguments": {}}
```

### `3d_parent-directory_activate`

Parent Directory。CLI：foxos 3d parent-directory activate。界面：Shading > Parent Directory。效果：点击「Parent Directory」（button）。示例：foxos 3d parent-directory activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d parent-directory activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_parent-directory_activate", "arguments": {}}
```

### `3d_refresh_activate`

Refresh。CLI：foxos 3d refresh activate。界面：Shading > Refresh。效果：点击「Refresh」（button）。示例：foxos 3d refresh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d refresh activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_refresh_activate", "arguments": {}}
```

### `3d_directory_create`

Create New Directory。CLI：foxos 3d directory create。界面：Shading > Create New Directory。效果：点击「Create New Directory」（button）。示例：foxos 3d directory create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d directory create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_directory_create", "arguments": {}}
```

### `3d_no-folder-opened_activate`

No folder opened。CLI：foxos 3d no-folder-opened activate。界面：Shading > main > No folder opened。效果：点击「No folder opened」（button）。示例：foxos 3d no-folder-opened activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d no-folder-opened activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_no-folder-opened_activate", "arguments": {}}
```

### `3d_settings_filter`

Filter settings。CLI：foxos 3d settings filter。界面：Shading > Filter settings。效果：点击「Filter settings」（button）。示例：foxos 3d settings filter --json

只读：是 · 破坏性：否 · CLI：`foxos 3d settings filter`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_settings_filter", "arguments": {}}
```

### `3d_folder_open`

Open Folder…。CLI：foxos 3d folder open。界面：Shading > main > Open Folder…。效果：点击「Open Folder…」（button）。示例：foxos 3d folder open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d folder open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_folder_open", "arguments": {}}
```

### `3d_browser-storage_activate`

Browser Storage。CLI：foxos 3d browser-storage activate。界面：Shading > main > Browser Storage。效果：点击「Browser Storage」（button）。示例：foxos 3d browser-storage activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d browser-storage activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_browser-storage_activate", "arguments": {}}
```

### `3d_files_create`

Add Files…。CLI：foxos 3d files create。界面：Shading > main > Add Files…。效果：点击「Add Files…」（button）。示例：foxos 3d files create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d files create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_files_create", "arguments": {}}
```

### `3d_open_open`

Open。CLI：foxos 3d open open。界面：Shading > main > Open。效果：点击「Open」（button）。示例：foxos 3d open open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d open open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_open_open", "arguments": {}}
```

### `3d_material_set`

Material。CLI：foxos 3d material set VALUE [--submit]。界面：Shading > main > Material。效果：把「Material」设为给定值（触发 input / change 事件）。示例：foxos 3d material set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d material set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Material」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_material_set", "arguments": {"value": "…"}}
```

### `3d_world_set`

World。CLI：foxos 3d world set VALUE [--submit]。界面：Shading > main > World。效果：把「World」设为给定值（触发 input / change 事件）。示例：foxos 3d world set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d world set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「World」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_world_set", "arguments": {"value": "…"}}
```

### `3d_background_activate`

Background。CLI：foxos 3d background activate。界面：Shading > main > Background。效果：点击「Background」（button）。示例：foxos 3d background activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d background activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_background_activate", "arguments": {}}
```

### `3d_dope-sheet_activate`

Dope Sheet。CLI：foxos 3d dope-sheet activate。界面：Animation > main > Dope Sheet。效果：点击「Dope Sheet」（button）。示例：foxos 3d dope-sheet activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d dope-sheet activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_dope-sheet_activate", "arguments": {}}
```

### `3d_channel_activate`

Channel。CLI：foxos 3d channel activate。界面：Animation > main > Channel。效果：点击「Channel」（button）。示例：foxos 3d channel activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d channel activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_channel_activate", "arguments": {}}
```

### `3d_key_activate`

Key。CLI：foxos 3d key activate。界面：Animation > main > Key。效果：点击「Key」（button）。示例：foxos 3d key activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d key activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_key_activate", "arguments": {}}
```

### `3d_keying_activate`

Keying。CLI：foxos 3d keying activate。界面：Animation > main > Keying。效果：点击「Keying」（button）。示例：foxos 3d keying activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d keying activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_keying_activate", "arguments": {}}
```

### `3d_image_activate`

Image。CLI：foxos 3d image activate。界面：Rendering > main > Image。效果：点击「Image」（button）。示例：foxos 3d image activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d image activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_image_activate", "arguments": {}}
```

### `3d_tool_activate`

Tool。CLI：foxos 3d tool activate。界面：Rendering > main > Tool。效果：点击「Tool」（button）。示例：foxos 3d tool activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d tool activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_tool_activate", "arguments": {}}
```

### `3d_scopes_activate`

Scopes。CLI：foxos 3d scopes activate。界面：Rendering > main > Scopes。效果：点击「Scopes」（button）。示例：foxos 3d scopes activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scopes activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_scopes_activate", "arguments": {}}
```

### `3d_realtime-raster_activate`

Realtime (Raster)。CLI：foxos 3d realtime-raster activate。界面：Rendering > main > Realtime (Raster)。效果：点击「Realtime (Raster)」（button）。示例：foxos 3d realtime-raster activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d realtime-raster activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_realtime-raster_activate", "arguments": {}}
```

### `3d_backdrop_activate`

Backdrop。CLI：foxos 3d backdrop activate。界面：Compositing > main > Backdrop。效果：点击「Backdrop」（button）。示例：foxos 3d backdrop activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d backdrop activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_backdrop_activate", "arguments": {}}
```

### `3d_node_activate`

Node。CLI：foxos 3d node activate。界面：Compositing > main > Node。效果：点击「Node」（button）。示例：foxos 3d node activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d node activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_node_activate", "arguments": {}}
```

### `3d_render_set`

//render/。CLI：foxos 3d render set VALUE [--submit]。界面：Compositing > main > //render/。效果：把「//render/」设为给定值（触发 input / change 事件）。示例：foxos 3d render set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「//render/」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_render_set", "arguments": {"value": "…"}}
```

### `3d_png_activate`

PNG。CLI：foxos 3d png activate。界面：Compositing > main > PNG。效果：点击「PNG」（button）。示例：foxos 3d png activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d png activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_png_activate", "arguments": {}}
```

### `3d_rgba_activate`

RGBA。CLI：foxos 3d rgba activate。界面：Compositing > main > RGBA。效果：点击「RGBA」（button）。示例：foxos 3d rgba activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rgba activate`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_rgba_activate", "arguments": {}}
```

### `3d_selection_copy`

快捷键 mod+c。CLI：foxos 3d selection copy。界面：键盘 mod+c；快捷键 mod+c。效果：在当前焦点上按 mod+c（src/sequencer/transform.ts 中定义）。示例：foxos 3d selection copy --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection copy`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_selection_copy", "arguments": {}}
```

### `3d_selection_lock`

快捷键 mod+l。CLI：foxos 3d selection lock。界面：键盘 mod+l；快捷键 mod+l。效果：在当前焦点上按 mod+l（src/scripting/console.ts 中定义）。示例：foxos 3d selection lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection lock`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_selection_lock", "arguments": {}}
```

### `3d_selection_cut`

快捷键 mod+x。CLI：foxos 3d selection cut。界面：键盘 mod+x；快捷键 mod+x。效果：在当前焦点上按 mod+x（src/sequencer/pvtransform.ts 中定义）。示例：foxos 3d selection cut --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection cut`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_selection_cut", "arguments": {}}
```

### `3d_edit_undo`

快捷键 mod+z。CLI：foxos 3d edit undo。界面：键盘 mod+z；快捷键 mod+z。效果：在当前焦点上按 mod+z（src/modes/editmesh/knife.ts 中定义）。示例：foxos 3d edit undo --json

只读：否 · 破坏性：否 · CLI：`foxos 3d edit undo`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "3d_edit_undo", "arguments": {}}
```

## cad（198 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `cad_arc_select` | 是 | `target`*: string, `machine`: string |
| `cad_application-menu_select` | 是 | `target`*: string, `machine`: string |
| `cad_circle-options_select` | 是 | `target`*: string, `machine`: string |
| `cad_arc-options_select` | 是 | `target`*: string, `machine`: string |
| `cad_application-menu_activate` |  | `machine`: string |
| `cad_drawing_create` |  | `machine`: string |
| `cad_open_open` | 是 | `machine`: string |
| `cad_save_save` |  | `machine`: string |
| `cad_undo_undo` |  | `machine`: string |
| `cad_redo_redo` |  | `machine`: string |
| `cad_plot_activate` |  | `machine`: string |
| `cad_commands_search` | 是 | `machine`: string |
| `cad_theme_activate` |  | `machine`: string |
| `cad_help_show` | 是 | `machine`: string |
| `cad_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `cad_home_show` | 是 | `machine`: string |
| `cad_insert_create` |  | `machine`: string |
| `cad_annotate_show` | 是 | `machine`: string |
| `cad_view_show` | 是 | `machine`: string |
| `cad_manage_show` | 是 | `machine`: string |
| `cad_output_show` | 是 | `machine`: string |
| `cad_minimize-ribbon_activate` |  | `machine`: string |
| `cad_line_activate` |  | `machine`: string |
| `cad_polyline_activate` |  | `machine`: string |
| `cad_circle-center-radius_activate` |  | `machine`: string |
| `cad_circle-options_activate` |  | `machine`: string |
| `cad_arc-options_activate` |  | `machine`: string |
| `cad_rectangle_activate` |  | `machine`: string |
| `cad_rectangle-options_activate` |  | `machine`: string |
| `cad_ellipse_activate` |  | `machine`: string |
| `cad_ellipse-options_activate` |  | `machine`: string |
| `cad_hatch_activate` |  | `machine`: string |
| `cad_spline_activate` |  | `machine`: string |
| `cad_construction-line_activate` |  | `machine`: string |
| `cad_point_activate` |  | `machine`: string |
| `cad_draw_draw` |  | `machine`: string |
| `cad_move_move` |  | `machine`: string |
| `cad_copy_copy` |  | `machine`: string |
| `cad_stretch_activate` |  | `machine`: string |
| `cad_rotate_rotate` |  | `machine`: string |
| `cad_mirror_activate` |  | `machine`: string |
| `cad_scale_activate` |  | `machine`: string |
| `cad_trim_activate` |  | `machine`: string |
| `cad_trim-options_activate` |  | `machine`: string |
| `cad_fillet_activate` |  | `machine`: string |
| `cad_fillet-options_activate` |  | `machine`: string |
| `cad_array_activate` |  | `machine`: string |
| `cad_array-options_activate` |  | `machine`: string |
| `cad_erase_activate` |  | `machine`: string |
| `cad_explode_activate` |  | `machine`: string |
| `cad_offset_activate` |  | `machine`: string |
| `cad_modify_update` |  | `machine`: string |
| `cad_text-multiline-text_activate` |  | `machine`: string |
| `cad_text-options_activate` |  | `machine`: string |
| `cad_dimension-linear_activate` |  | `machine`: string |
| `cad_dimension-options_activate` |  | `machine`: string |
| `cad_leader_activate` |  | `machine`: string |
| `cad_continue_activate` |  | `machine`: string |
| `cad_baseline_activate` |  | `machine`: string |
| `cad_layer-properties_activate` |  | `machine`: string |
| `cad_turn-layer-off_activate` |  | `machine`: string |
| `cad_isolate-layers_activate` |  | `machine`: string |
| `cad_freeze-layer_activate` |  | `machine`: string |
| `cad_layer_lock` |  | `machine`: string |
| `cad_make-current_activate` |  | `machine`: string |
| `cad_turn-layers_activate` |  | `machine`: string |
| `cad_unisolate-layers_activate` |  | `machine`: string |
| `cad_thaw-layers_activate` |  | `machine`: string |
| `cad_layer_unlock` |  | `machine`: string |
| `cad_match-layer_activate` |  | `machine`: string |
| `cad_insert-2_create` |  | `machine`: string |
| `cad_create_create` |  | `machine`: string |
| `cad_library_activate` |  | `machine`: string |
| `cad_match-properties_activate` |  | `machine`: string |
| `cad_measure-distance_activate` |  | `machine`: string |
| `cad_measure-options_activate` |  | `machine`: string |
| `cad_quick-select_activate` |  | `machine`: string |
| `cad_select_select` | 是 | `machine`: string |
| `cad_similar_select` | 是 | `machine`: string |
| `cad_paste_paste` |  | `machine`: string |
| `cad_cut_cut` |  | `machine`: string |
| `cad_clipboard_copy` |  | `machine`: string |
| `cad_base-point_copy` |  | `machine`: string |
| `cad_it_dismiss` | 是 | `machine`: string |
| `cad_cursor-coordinates-click-change-display_activate` |  | `machine`: string |
| `cad_grid_activate` |  | `machine`: string |
| `cad_snap-grid_activate` |  | `machine`: string |
| `cad_snap-grid-settings_activate` |  | `machine`: string |
| `cad_ortho-mode_activate` |  | `machine`: string |
| `cad_polar-tracking_activate` |  | `machine`: string |
| `cad_polar-tracking-settings_activate` |  | `machine`: string |
| `cad_object-snap_activate` |  | `machine`: string |
| `cad_object-snap-settings_activate` |  | `machine`: string |
| `cad_object-snap-tracking_activate` |  | `machine`: string |
| `cad_dynamic-input_activate` |  | `machine`: string |
| `cad_lineweights_show` | 是 | `machine`: string |
| `cad_selection-preview_activate` |  | `machine`: string |
| `cad_drawing-units_activate` |  | `machine`: string |
| `cad_drafting-settings_activate` |  | `machine`: string |
| `cad_clean-screen_activate` |  | `machine`: string |
| `cad_newctrln_activate` |  | `machine`: string |
| `cad_ctrlo_open` | 是 | `machine`: string |
| `cad_sample-drawing_open` | 是 | `machine`: string |
| `cad_savectrls_activate` |  | `machine`: string |
| `cad_as-ctrlshifts_save` |  | `machine`: string |
| `cad_dxf-or-dwg_import` |  | `machine`: string |
| `cad_export_export` |  | `machine`: string |
| `cad_plot-ctrlp_activate` |  | `machine`: string |
| `cad_application-menu-drawing-units_activate` |  | `machine`: string |
| `cad_purge-unused_activate` |  | `machine`: string |
| `cad_settings_show` | 是 | `machine`: string |
| `cad_keyboard-shortcuts_activate` |  | `machine`: string |
| `cad_source-code-github_activate` |  | `machine`: string |
| `cad_drawing_close` | 是 | `machine`: string |
| `cad_close_close` | 是 | `machine`: string |
| `cad_search-commands_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `cad_alignalign_activate` |  | `machine`: string |
| `cad_aligned-dimensiondimaligned_activate` |  | `machine`: string |
| `cad_angular-dimensiondimangular_activate` |  | `machine`: string |
| `cad_arcarc_activate` |  | `machine`: string |
| `cad_baseline-dimensiondimbaseline_activate` |  | `machine`: string |
| `cad_blocks-paletteblocks_activate` |  | `machine`: string |
| `cad_breakbreak_activate` |  | `machine`: string |
| `cad_break-at-pointbreakatpoint_activate` |  | `machine`: string |
| `cad_chamferchamfer_activate` |  | `machine`: string |
| `cad_circlecircle_activate` |  | `machine`: string |
| `cad_clean-screencleanscreen_activate` |  | `machine`: string |
| `cad_drawingclose_close` | 是 | `machine`: string |
| `cad_construction-linexline_activate` |  | `machine`: string |
| `cad_continue-dimensiondimcontinue_activate` |  | `machine`: string |
| `cad_copycopy_activate` |  | `machine`: string |
| `cad_clipboardcopyclip_copy` |  | `machine`: string |
| `cad_base-pointcopybase_copy` |  | `machine`: string |
| `cad_blockblock_create` |  | `machine`: string |
| `cad_cutcutclip_activate` |  | `machine`: string |
| `cad_diameter-dimensiondimdiameter_activate` |  | `machine`: string |
| `cad_dimensiondim_activate` |  | `machine`: string |
| `cad_dimension-stylesdimstyle_activate` |  | `machine`: string |
| `cad_donutdonut_activate` |  | `machine`: string |
| `cad_drafting-settingsdsettings_activate` |  | `machine`: string |
| `cad_orderdraworder_draw` |  | `machine`: string |
| `cad_drawing-unitsunits_activate` |  | `machine`: string |
| `cad_ellipseellipse_activate` |  | `machine`: string |
| `cad_eraseerase_activate` |  | `machine`: string |
| `cad_explodeexplode_activate` |  | `machine`: string |
| `cad_exportexport_activate` |  | `machine`: string |
| `cad_dwgdwgout_export` |  | `machine`: string |
| `cad_dxfdxfout_export` |  | `machine`: string |
| `cad_extendextend_activate` |  | `machine`: string |
| `cad_filletfillet_activate` |  | `machine`: string |
| `cad_freeze-layerlayfrz_activate` |  | `machine`: string |
| `cad_grid-displaygrid_activate` |  | `machine`: string |
| `cad_hatchhatch_activate` |  | `machine`: string |
| `cad_helphelp_activate` |  | `machine`: string |
| `cad_dxf-or-dwgimport_import` |  | `machine`: string |
| `cad_blockinsert_create` |  | `machine`: string |
| `cad_isolate-layerslayiso_activate` |  | `machine`: string |
| `cad_joinjoin_activate` |  | `machine`: string |
| `cad_keyboard-shortcutsshortcuts_activate` |  | `machine`: string |
| `cad_layer-propertieslayer_activate` |  | `machine`: string |
| `cad_leaderleader_activate` |  | `machine`: string |
| `cad_lengthenlengthen_activate` |  | `machine`: string |
| `cad_lineline_activate` |  | `machine`: string |
| `cad_linear-dimensiondimlinear_activate` |  | `machine`: string |
| `cad_linetype-scaleltscale_activate` |  | `machine`: string |
| `cad_linetypeslinetype_activate` |  | `machine`: string |
| `cad_system_activate` |  | `machine`: string |
| `cad_light_activate` |  | `machine`: string |
| `cad_dark_activate` |  | `machine`: string |
| `cad_center-radius_activate` |  | `machine`: string |
| `cad_center-diameter_activate` |  | `machine`: string |
| `cad_tan-tan-radius_activate` |  | `machine`: string |
| `cad_center-end_start` |  | `machine`: string |
| `cad_center-start-end_activate` |  | `machine`: string |
| `cad_end-radius_start` |  | `machine`: string |
| `cad_rectangle-options-rectangle_activate` |  | `machine`: string |
| `cad_polygon_activate` |  | `machine`: string |
| `cad_center_activate` |  | `machine`: string |
| `cad_axis-end_activate` |  | `machine`: string |
| `cad_elliptical-arc_activate` |  | `machine`: string |

## parametric（50 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `parametric_item_select` | 是 | `target`*: string, `machine`: string |
| `parametric_default-units_select` | 是 | `target`*: string, `machine`: string |
| `parametric_graphics-area_dismiss` | 是 | `machine`: string |
| `parametric_edit_update` |  | `machine`: string |
| `parametric_view_show` | 是 | `machine`: string |
| `parametric_insert_create` |  | `machine`: string |
| `parametric_tools_activate` |  | `machine`: string |
| `parametric_help_show` | 是 | `machine`: string |
| `parametric_open_open` | 是 | `machine`: string |
| `parametric_save_save` |  | `machine`: string |
| `parametric_undo_undo` |  | `machine`: string |
| `parametric_redo_redo` |  | `machine`: string |
| `parametric_rebuild_activate` |  | `machine`: string |
| `parametric_options_activate` |  | `machine`: string |
| `parametric_part_rename` |  | `machine`: string |
| `parametric_search-commands_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `parametric_assistant_activate` |  | `machine`: string |
| `parametric_share_share` |  | `machine`: string |
| `parametric_source-code-github_show` | 是 | `machine`: string |
| `parametric_apps_activate` |  | `machine`: string |
| `parametric_account_activate` |  | `machine`: string |
| `parametric_panel_resize` |  | `machine`: string |
| `parametric_unit-system_activate` |  | `machine`: string |
| `parametric_close_close` | 是 | `machine`: string |
| `parametric_system_activate` |  | `machine`: string |
| `parametric_light_activate` |  | `machine`: string |
| `parametric_dark_activate` |  | `machine`: string |
| `parametric_image-quality_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `parametric_reverse-mouse-wheel-zoom-direction_toggle` |  | `machine`: string |
| `parametric_done_confirm` |  | `machine`: string |
| `parametric_apps-tab_open` | 是 | `machine`: string |
| `parametric_document_save` |  | `machine`: string |

## circuits（56 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `circuits_theme_select` | 是 | `target`*: string, `machine`: string |
| `circuits_account_select` | 是 | `target`*: string, `machine`: string |
| `circuits_examplea-led-blinker-its-board_open` | 是 | `target`*: string, `machine`: string |
| `circuits_design-canvas_dismiss` | 是 | `machine`: string |
| `circuits_project_create` |  | `machine`: string |
| `circuits_project_open` | 是 | `machine`: string |
| `circuits_save_save` |  | `machine`: string |
| `circuits_undo_undo` |  | `machine`: string |
| `circuits_redo_redo` |  | `machine`: string |
| `circuits_commandsctrlk_search` | 是 | `machine`: string |
| `circuits_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `circuits_edit_update` |  | `machine`: string |
| `circuits_view_show` | 是 | `machine`: string |
| `circuits_project_activate` |  | `machine`: string |
| `circuits_reports_activate` |  | `machine`: string |
| `circuits_window_activate` |  | `machine`: string |
| `circuits_help_show` | 是 | `machine`: string |
| `circuits_schematic-sheet_create` |  | `machine`: string |
| `circuits_board_create` |  | `machine`: string |
| `circuits_project-options_activate` |  | `machine`: string |
| `circuits_projects_show` | 是 | `machine`: string |
| `circuits_navigator_show` | 是 | `machine`: string |
| `circuits_properties_show` | 是 | `machine`: string |
| `circuits_components_show` | 是 | `machine`: string |
| `circuits_puter_show` | 是 | `machine`: string |
| `circuits_panels_activate` |  | `machine`: string |
| `circuits_it_dismiss` | 是 | `machine`: string |
| `circuits_notification_dismiss` | 是 | `machine`: string |
| `circuits_preferences_activate` |  | `machine`: string |
| `circuits_schematic-sheet_activate` |  | `machine`: string |
| `circuits_board_activate` |  | `machine`: string |
| `circuits_project_rename` |  | `machine`: string |
| `circuits_savectrls_activate` |  | `machine`: string |
| `circuits_project-file_export` |  | `machine`: string |
| `circuits_compile-electrical-rules-check_activate` |  | `machine`: string |
| `circuits_annotate-schematics_activate` |  | `machine`: string |
| `circuits_board-from-schematic_update` |  | `machine`: string |
| `circuits_project_close` | 是 | `machine`: string |

## building-design（19 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `building-design_it_dismiss` | 是 | `machine`: string |

## tasks（76 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `tasks_add_create` |  | `target`*: string, `machine`: string |
| `tasks_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `tasks_list_open` | 是 | `target`*: string, `machine`: string |
| `tasks_actions_select` | 是 | `target`*: string, `machine`: string |
| `tasks_tasks_open` | 是 | `target`*: string, `machine`: string |
| `tasks_week-starts_select` | 是 | `target`*: string, `machine`: string |
| `tasks_content_dismiss` | 是 | `machine`: string |
| `tasks_task_create` |  | `machine`: string |
| `tasks_today_show` | 是 | `machine`: string |
| `tasks_upcoming_show` | 是 | `machine`: string |
| `tasks_lists_show` | 是 | `machine`: string |
| `tasks_calendar_show` | 是 | `machine`: string |
| `tasks_logbook_show` | 是 | `machine`: string |
| `tasks_settings_show` | 是 | `machine`: string |
| `tasks_list_create` |  | `machine`: string |
| `tasks_personal_show` | 是 | `machine`: string |
| `tasks_work_show` | 是 | `machine`: string |
| `tasks_search_search` | 是 | `machine`: string |
| `tasks_add-task_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_options_show` | 是 | `machine`: string |
| `tasks_close_close` | 是 | `machine`: string |
| `tasks_first-task_create` |  | `machine`: string |
| `tasks_explore-sample-data_activate` |  | `machine`: string |
| `tasks_task-title_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_notes_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_list_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_due-date_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_due-time_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_today_activate` |  | `machine`: string |
| `tasks_tomorrow_activate` |  | `machine`: string |
| `tasks_week_next` | 是 | `machine`: string |
| `tasks_no-date_activate` |  | `machine`: string |
| `tasks_remind-me_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_none_activate` |  | `machine`: string |
| `tasks_low_activate` |  | `machine`: string |
| `tasks_medium_activate` |  | `machine`: string |
| `tasks_high_activate` |  | `machine`: string |
| `tasks_add-tag_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_repeat_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `tasks_subtask_create` |  | `machine`: string |
| `tasks_cancel_cancel` | 是 | `machine`: string |
| `tasks_task-2_create` |  | `machine`: string |
| `tasks_upcoming-task_create` |  | `machine`: string |
| `tasks_lists-list_create` |  | `machine`: string |
| `tasks_ics-calendar-file_export` |  | `machine`: string |
| `tasks_month_previous` | 是 | `machine`: string |
| `tasks_calendar-today_activate` |  | `machine`: string |
| `tasks_month_next` | 是 | `machine`: string |
| `tasks_system_activate` |  | `machine`: string |
| `tasks_light_activate` |  | `machine`: string |
| `tasks_dark_activate` |  | `machine`: string |
| `tasks_due-date-reminders_toggle` |  | `machine`: string |
| `tasks_exportdownload-everything-as-json-file_activate` |  | `machine`: string |
| `tasks_lists_previous` | 是 | `machine`: string |
| `tasks_list_share` |  | `machine`: string |
| `tasks_list_update` |  | `machine`: string |
| `tasks_personal-add_create` |  | `machine`: string |
| `tasks_search-tasks_set` |  | `value`*: string, `submit`: boolean, `machine`: string |

## projects（68 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `projects_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `projects_projects_show` | 是 | `machine`: string |
| `projects_quick-addn_activate` |  | `machine`: string |
| `projects_task_search` | 是 | `machine`: string |
| `projects_commandsctrlk_activate` |  | `machine`: string |
| `projects_today_show` | 是 | `machine`: string |
| `projects_tasks_show` | 是 | `machine`: string |
| `projects_project_create` |  | `machine`: string |
| `projects_projects-2_show` | 是 | `machine`: string |
| `projects_settings_show` | 是 | `machine`: string |
| `projects_project-2_create` |  | `machine`: string |
| `projects_project-3_create` |  | `machine`: string |
| `projects_close_close` | 是 | `machine`: string |
| `projects_first-project_create` |  | `machine`: string |
| `projects_explore-sample-data_activate` |  | `machine`: string |
| `projects_today-projects_show` | 是 | `machine`: string |
| `projects_overdue_show` | 是 | `machine`: string |
| `projects_high-priority_show` | 是 | `machine`: string |
| `projects_unscheduled_show` | 是 | `machine`: string |
| `projects_options_show` | 是 | `machine`: string |
| `projects_filter-tasks-by-title_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `projects_label_activate` |  | `machine`: string |
| `projects_assignee_activate` |  | `machine`: string |
| `projects_priority_activate` |  | `machine`: string |
| `projects_due_activate` |  | `machine`: string |
| `projects_project_activate` |  | `machine`: string |
| `projects_project-order_activate` |  | `machine`: string |
| `projects_light_toggle` |  | `machine`: string |
| `projects_dark_toggle` |  | `machine`: string |
| `projects_system_toggle` |  | `machine`: string |
| `projects_view_show` | 是 | `machine`: string |
| `projects_export_export` |  | `machine`: string |
| `projects_import_import` |  | `machine`: string |
| `projects_calendar-file_export` |  | `machine`: string |
| `projects_restore-points_open` | 是 | `machine`: string |
| `projects_deleted-projects_open` | 是 | `machine`: string |
| `projects_learn-more_show` | 是 | `machine`: string |
| `projects_name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `projects_purple_toggle` |  | `machine`: string |
| `projects_teal_toggle` |  | `machine`: string |
| `projects_amber_toggle` |  | `machine`: string |
| `projects_rose_toggle` |  | `machine`: string |
| `projects_indigo_toggle` |  | `machine`: string |
| `projects_blue_toggle` |  | `machine`: string |
| `projects_olive_toggle` |  | `machine`: string |
| `projects_rust_toggle` |  | `machine`: string |
| `projects_cancel_cancel` | 是 | `machine`: string |
| `projects_project-4_create` |  | `machine`: string |
| `projects_command-palette_show` | 是 | `machine`: string |
| `projects_edit_undo` |  | `machine`: string |

## wiki（78 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `wiki_heading_select` | 是 | `target`*: string, `machine`: string |
| `wiki_files_import` |  | `target`*: string, `machine`: string |
| `wiki_here_import` |  | `target`*: string, `machine`: string |
| `wiki_page_dismiss` | 是 | `machine`: string |
| `wiki_lolocal-s-wiki_activate` |  | `machine`: string |
| `wiki_sidebar_close` | 是 | `machine`: string |
| `wiki_searchctrlk_activate` |  | `machine`: string |
| `wiki_home_activate` |  | `machine`: string |
| `wiki_pagectrlaltn_create` |  | `machine`: string |
| `wiki_private_activate` |  | `machine`: string |
| `wiki_private-page_create` |  | `machine`: string |
| `wiki_getting-started_activate` |  | `machine`: string |
| `wiki_tasks_activate` |  | `machine`: string |
| `wiki_notes_activate` |  | `machine`: string |
| `wiki_templates_activate` |  | `machine`: string |
| `wiki_import_import` |  | `machine`: string |
| `wiki_trash_delete` |  | `machine`: string |
| `wiki_settings_show` | 是 | `machine`: string |
| `wiki_powered-by-puter_show` | 是 | `machine`: string |
| `wiki_sidebar_resize` |  | `machine`: string |
| `wiki_getting-started-2_activate` |  | `machine`: string |
| `wiki_share_share` |  | `machine`: string |
| `wiki_comments_activate` |  | `machine`: string |
| `wiki_favorites_create` |  | `machine`: string |
| `wiki_page-options_activate` |  | `machine`: string |
| `wiki_page-icon_update` |  | `machine`: string |
| `wiki_cover_create` |  | `machine`: string |
| `wiki_getting-started_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_callout-icon_update` |  | `machine`: string |
| `wiki_callout_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_text_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_bulleted-list_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_done_toggle` |  | `machine`: string |
| `wiki_to-do-list_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_content_hide` | 是 | `machine`: string |
| `wiki_toggle-list_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_quote_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `wiki_theme_activate` |  | `machine`: string |
| `wiki_lolocals-wiki-settings_show` | 是 | `machine`: string |
| `wiki_keyboard-shortcutsctrl_activate` |  | `machine`: string |
| `wiki_close_close` | 是 | `machine`: string |
| `wiki_system_toggle` |  | `machine`: string |
| `wiki_light_toggle` |  | `machine`: string |
| `wiki_dark_toggle` |  | `machine`: string |
| `wiki_settings-powered-by-puter_show` | 是 | `machine`: string |
| `wiki_page_share` |  | `machine`: string |
| `wiki_page-options-favorites_create` |  | `machine`: string |
| `wiki_link_copy` |  | `machine`: string |
| `wiki_duplicate_duplicate` |  | `machine`: string |
| `wiki_move_move` |  | `machine`: string |
| `wiki_page_lock` |  | `machine`: string |
| `wiki_export_export` |  | `machine`: string |
| `wiki_page-history_activate` |  | `machine`: string |
| `wiki_trash_move` |  | `machine`: string |
| `wiki_selection_select-all` |  | `machine`: string |
| `wiki_selection_copy` |  | `machine`: string |
| `wiki_selection_duplicate` |  | `machine`: string |
| `wiki_command-palette_show` | 是 | `machine`: string |
| `wiki_selection_lock-shift` |  | `machine`: string |
| `wiki_edit_undo` |  | `machine`: string |

## time-tracking（89 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `time-tracking_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `time-tracking_nov-9-nov-15-0m-across-0-days_select` | 是 | `target`*: string, `machine`: string |
| `time-tracking_log-time_select` | 是 | `target`*: string, `machine`: string |
| `time-tracking_printable-timesheet_select` | 是 | `target`*: string, `machine`: string |
| `time-tracking_backup-from_export` |  | `target`*: string, `machine`: string |
| `time-tracking_restore-backup-from_select` | 是 | `target`*: string, `machine`: string |
| `time-tracking_csvevery-entry-ready_export` |  | `target`*: string, `machine`: string |
| `time-tracking_content_dismiss` | 是 | `machine`: string |
| `time-tracking_timer_show` | 是 | `machine`: string |
| `time-tracking_timesheet_show` | 是 | `machine`: string |
| `time-tracking_reports_show` | 是 | `machine`: string |
| `time-tracking_projects_show` | 是 | `machine`: string |
| `time-tracking_settings_show` | 是 | `machine`: string |
| `time-tracking_log-time_activate` |  | `machine`: string |
| `time-tracking_client_create` |  | `machine`: string |
| `time-tracking_close_close` | 是 | `machine`: string |
| `time-tracking_set-up-tracking_activate` |  | `machine`: string |
| `time-tracking_explore-sample-data_activate` |  | `machine`: string |
| `time-tracking_jump-date_activate` |  | `machine`: string |
| `time-tracking_entries_search` | 是 | `machine`: string |
| `time-tracking_week_activate` |  | `machine`: string |
| `time-tracking_grid_activate` |  | `machine`: string |
| `time-tracking_month_activate` |  | `machine`: string |
| `time-tracking_week_previous` | 是 | `machine`: string |
| `time-tracking_today_activate` |  | `machine`: string |
| `time-tracking_week_next` | 是 | `machine`: string |
| `time-tracking_log-time-yesterday_activate` |  | `machine`: string |
| `time-tracking_log-time-today_activate` |  | `machine`: string |
| `time-tracking_invoice-ready-summary-report_print` | 是 | `machine`: string |
| `time-tracking_csv_export` |  | `machine`: string |
| `time-tracking_report_activate` |  | `machine`: string |
| `time-tracking_insights_activate` |  | `machine`: string |
| `time-tracking_invoices_activate` |  | `machine`: string |
| `time-tracking_reports-week_activate` |  | `machine`: string |
| `time-tracking_last-week_activate` |  | `machine`: string |
| `time-tracking_reports-month_activate` |  | `machine`: string |
| `time-tracking_last-month_activate` |  | `machine`: string |
| `time-tracking_custom_activate` |  | `machine`: string |
| `time-tracking_client_activate` |  | `machine`: string |
| `time-tracking_project_activate` |  | `machine`: string |
| `time-tracking_task_activate` |  | `machine`: string |
| `time-tracking_unbilled_activate` |  | `machine`: string |
| `time-tracking_invoiced_activate` |  | `machine`: string |
| `time-tracking_projects-client_create` |  | `machine`: string |
| `time-tracking_first-client_create` |  | `machine`: string |
| `time-tracking_light_activate` |  | `machine`: string |
| `time-tracking_dark_activate` |  | `machine`: string |
| `time-tracking_system_activate` |  | `machine`: string |
| `time-tracking_currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_default-hourly-rate_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_default-rate-applies-from_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_round-billable-time_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_week-starts_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_weekly-target-hours_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_target-counts_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_business-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_address_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_tax-vat-id_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_default-tax-rate_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_payment-terms_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_terms-line_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_how-pay_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_logo_import` |  | `machine`: string |
| `time-tracking_long-timer-warning_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_away-sleep-gaps_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_daily-tracking-nudge_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_unbilled-time-reminder_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_counts-as-aging_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_system-notifications_toggle` |  | `machine`: string |
| `time-tracking_automatic-backups_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `time-tracking_puter_show` | 是 | `machine`: string |

## survey（46 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `survey_folders_select` | 是 | `target`*: string, `machine`: string |
| `survey_describe-survey_select` | 是 | `target`*: string, `machine`: string |
| `survey_content_dismiss` | 是 | `machine`: string |
| `survey_surveys-home_show` | 是 | `machine`: string |
| `survey_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `survey_account-settings_activate` |  | `machine`: string |
| `survey_folder_create` |  | `machine`: string |
| `survey_source-github_open` | 是 | `machine`: string |
| `survey_powered-by-puter_show` | 是 | `machine`: string |
| `survey_survey_create` |  | `machine`: string |
| `survey_from-scratcha-blank-survey_start` |  | `machine`: string |
| `survey_use-templateready-made-fully-editable_activate` |  | `machine`: string |
| `survey_questionspaste-list-or-open-file_import` |  | `machine`: string |
| `survey_generate_run` |  | `machine`: string |
| `survey_search-surveys_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `survey_filter-by-status_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `survey_sort-by_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `survey_survey-2_create` |  | `machine`: string |
| `survey_it_dismiss` | 是 | `machine`: string |
| `survey_system_activate` |  | `machine`: string |
| `survey_light_activate` |  | `machine`: string |
| `survey_dark_activate` |  | `machine`: string |
| `survey_keyboard-shortcuts_activate` |  | `machine`: string |
| `survey_surveys_show` | 是 | `machine`: string |
| `survey_from-scratch_start` |  | `machine`: string |
| `survey_use-template_activate` |  | `machine`: string |
| `survey_ai_run` |  | `machine`: string |
| `survey_questions_import` |  | `machine`: string |

## accounting（63 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `accounting_account-menu_select` | 是 | `target`*: string, `machine`: string |
| `accounting_company-name_select` | 是 | `target`*: string, `machine`: string |
| `accounting_content_dismiss` | 是 | `machine`: string |
| `accounting_home_show` | 是 | `machine`: string |
| `accounting_create_create` |  | `machine`: string |
| `accounting_home-2_show` | 是 | `machine`: string |
| `accounting_banking_show` | 是 | `machine`: string |
| `accounting_sales_show` | 是 | `machine`: string |
| `accounting_purchases_show` | 是 | `machine`: string |
| `accounting_reports_show` | 是 | `machine`: string |
| `accounting_menu_show` | 是 | `machine`: string |
| `accounting_settings_show` | 是 | `machine`: string |
| `accounting_navigation_open` | 是 | `machine`: string |
| `accounting_search_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `accounting_keyboard-shortcuts_activate` |  | `machine`: string |
| `accounting_settings-2_show` | 是 | `machine`: string |
| `accounting_panel_collapse` | 是 | `machine`: string |
| `accounting_accounting_activate` |  | `machine`: string |
| `accounting_purchases_activate` |  | `machine`: string |
| `accounting_sales_activate` |  | `machine`: string |
| `accounting_sales-tax_activate` |  | `machine`: string |
| `accounting_reports_activate` |  | `machine`: string |
| `accounting_puter_show` | 是 | `machine`: string |
| `accounting_privacy_activate` |  | `machine`: string |
| `accounting_invoice_create` |  | `machine`: string |
| `accounting_payment_record` |  | `machine`: string |
| `accounting_expense_record` |  | `machine`: string |
| `accounting_enter-bill_activate` |  | `machine`: string |
| `accounting_pay-bills_activate` |  | `machine`: string |
| `accounting_deposit_record` |  | `machine`: string |
| `accounting_write-check_activate` |  | `machine`: string |
| `accounting_bank-statement_import` |  | `machine`: string |
| `accounting_period_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `accounting_report_show` | 是 | `machine`: string |
| `accounting_overdue_show` | 是 | `machine`: string |
| `accounting_not-due-yet_show` | 是 | `machine`: string |
| `accounting_paid_show` | 是 | `machine`: string |
| `accounting_go-banking_show` | 是 | `machine`: string |
| `accounting_as-table_show` | 是 | `machine`: string |
| `accounting_close_close` | 是 | `machine`: string |
| `accounting_home-currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `accounting_fiscal-year-starts_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `accounting_date-format_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `accounting_start-sample-company-explore_toggle` |  | `machine`: string |
| `accounting_books_create` |  | `machine`: string |

## invoicing（38 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `invoicing_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `invoicing_content_dismiss` | 是 | `machine`: string |
| `invoicing_switch-dark-theme_activate` |  | `machine`: string |
| `invoicing_home_show` | 是 | `machine`: string |
| `invoicing_invoices_show` | 是 | `machine`: string |
| `invoicing_estimates_show` | 是 | `machine`: string |
| `invoicing_recurring_show` | 是 | `machine`: string |
| `invoicing_clients_show` | 是 | `machine`: string |
| `invoicing_receipts_show` | 是 | `machine`: string |
| `invoicing_saved-items_show` | 是 | `machine`: string |
| `invoicing_reports_show` | 是 | `machine`: string |
| `invoicing_trash_delete` |  | `machine`: string |
| `invoicing_invoice_create` |  | `machine`: string |
| `invoicing_estimate_create` |  | `machine`: string |
| `invoicing_settings_show` | 是 | `machine`: string |
| `invoicing_invoice-2_create` |  | `machine`: string |
| `invoicing_estimate-2_create` |  | `machine`: string |
| `invoicing_close_close` | 是 | `machine`: string |
| `invoicing_set-up-business_activate` |  | `machine`: string |
| `invoicing_explore-sample-data_activate` |  | `machine`: string |

## expense（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `expense_month-nothing-last-month_select` | 是 | `target`*: string, `machine`: string |
| `expense_not-report-expenses_select` | 是 | `target`*: string, `machine`: string |
| `expense_awaiting-reimbursement-expenses-flight_select` | 是 | `target`*: string, `machine`: string |
| `expense_lines-open_select` | 是 | `target`*: string, `machine`: string |
| `expense_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `expense_content_dismiss` | 是 | `machine`: string |
| `expense_home_show` | 是 | `machine`: string |
| `expense_expenses_show` | 是 | `machine`: string |
| `expense_reports_show` | 是 | `machine`: string |
| `expense_reconcile_show` | 是 | `machine`: string |
| `expense_settings_show` | 是 | `machine`: string |
| `expense_capture-receipt_activate` |  | `machine`: string |
| `expense_manual-entry_activate` |  | `machine`: string |
| `expense_capture-receipt-2_activate` |  | `machine`: string |
| `expense_close_close` | 是 | `machine`: string |
| `expense_set-up-expenses_activate` |  | `machine`: string |
| `expense_explore-sample-data_activate` |  | `machine`: string |

## cap-table（45 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `cap-table_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `cap-table_main-content_dismiss` | 是 | `machine`: string |
| `cap-table_searchctrl-k_activate` |  | `machine`: string |
| `cap-table_home_activate` |  | `machine`: string |
| `cap-table_cap-table_activate` |  | `machine`: string |
| `cap-table_securities_activate` |  | `machine`: string |
| `cap-table_stakeholders_activate` |  | `machine`: string |
| `cap-table_classes_share` |  | `machine`: string |
| `cap-table_round-modeling_activate` |  | `machine`: string |
| `cap-table_exit-scenarios_activate` |  | `machine`: string |
| `cap-table_needs-attention_activate` |  | `machine`: string |
| `cap-table_reports_activate` |  | `machine`: string |
| `cap-table_history_activate` |  | `machine`: string |
| `cap-table_settings_show` | 是 | `machine`: string |
| `cap-table_issue-security_activate` |  | `machine`: string |
| `cap-table_issue-security-2_activate` |  | `machine`: string |
| `cap-table_by-class_activate` |  | `machine`: string |
| `cap-table_by-holder_activate` |  | `machine`: string |
| `cap-table_cap-table_open` | 是 | `machine`: string |
| `cap-table_set-up-company-profile-do_activate` |  | `machine`: string |
| `cap-table_share-class-do_create` |  | `machine`: string |
| `cap-table_issue-founder-shares-do_activate` |  | `machine`: string |
| `cap-table_adopt-equity-plan-reserve-shares-do_activate` |  | `machine`: string |
| `cap-table_grant-options-or-add-safe-do_activate` |  | `machine`: string |
| `cap-table_close_close` | 是 | `machine`: string |
| `cap-table_set-up-company_activate` |  | `machine`: string |
| `cap-table_explore-sample-data_activate` |  | `machine`: string |

## crm（34 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `crm_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `crm_searchctrl-k_activate` |  | `machine`: string |
| `crm_home_show` | 是 | `machine`: string |
| `crm_pipeline_show` | 是 | `machine`: string |
| `crm_leads_show` | 是 | `machine`: string |
| `crm_follow-ups_show` | 是 | `machine`: string |
| `crm_companies_show` | 是 | `machine`: string |
| `crm_activity_show` | 是 | `machine`: string |
| `crm_forecast_show` | 是 | `machine`: string |
| `crm_settings_show` | 是 | `machine`: string |
| `crm_lead_create` |  | `machine`: string |
| `crm_me-around_show` | 是 | `machine`: string |
| `crm_close_close` | 是 | `machine`: string |
| `crm_set-up-pipeline_activate` |  | `machine`: string |
| `crm_explore-sample-data_activate` |  | `machine`: string |
| `crm_command-palette_show` | 是 | `machine`: string |

## help-desk（24 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `help-desk_help-desk-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `help-desk_name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `help-desk_help-desk_create` |  | `machine`: string |
| `help-desk_source-code_show` | 是 | `machine`: string |
| `help-desk_puter_show` | 是 | `machine`: string |
| `help-desk_dismiss_dismiss` | 是 | `machine`: string |

## contracts（32 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `contracts_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `contracts_content_dismiss` | 是 | `machine`: string |
| `contracts_home_show` | 是 | `machine`: string |
| `contracts_contracts_show` | 是 | `machine`: string |
| `contracts_renewals_show` | 是 | `machine`: string |
| `contracts_obligations_show` | 是 | `machine`: string |
| `contracts_contacts_show` | 是 | `machine`: string |
| `contracts_settings_show` | 是 | `machine`: string |
| `contracts_contract_create` |  | `machine`: string |
| `contracts_contract-2_create` |  | `machine`: string |
| `contracts_contract-3_create` |  | `machine`: string |
| `contracts_close_close` | 是 | `machine`: string |
| `contracts_first-contract_create` |  | `machine`: string |
| `contracts_explore-sample-data_activate` |  | `machine`: string |

## pos（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `pos_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `pos_register_show` | 是 | `machine`: string |
| `pos_products_show` | 是 | `machine`: string |
| `pos_receipts_show` | 是 | `machine`: string |
| `pos_customers_show` | 是 | `machine`: string |
| `pos_reports_show` | 是 | `machine`: string |
| `pos_settings_show` | 是 | `machine`: string |
| `pos_search-products-or-scan-barcode_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `pos_cash-drawer_activate` |  | `machine`: string |
| `pos_products_create` |  | `machine`: string |
| `pos_custom-item_create` |  | `machine`: string |
| `pos_park-sale-serve-next-customer_activate` |  | `machine`: string |
| `pos_clear_clear` |  | `machine`: string |
| `pos_charge_activate` |  | `machine`: string |
| `pos_close_close` | 是 | `machine`: string |
| `pos_set-up-store_activate` |  | `machine`: string |
| `pos_explore-sample-data_activate` |  | `machine`: string |

## inventory（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `inventory_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `inventory_searchctrl-k_activate` |  | `machine`: string |
| `inventory_overview_show` | 是 | `machine`: string |
| `inventory_products_show` | 是 | `machine`: string |
| `inventory_take-out_show` | 是 | `machine`: string |
| `inventory_reorder_show` | 是 | `machine`: string |
| `inventory_stocktake_show` | 是 | `machine`: string |
| `inventory_history_show` | 是 | `machine`: string |
| `inventory_reports_show` | 是 | `machine`: string |
| `inventory_locations_show` | 是 | `machine`: string |
| `inventory_suppliers_show` | 是 | `machine`: string |
| `inventory_settings_show` | 是 | `machine`: string |
| `inventory_product_create` |  | `machine`: string |
| `inventory_close_close` | 是 | `machine`: string |
| `inventory_set-up-inventory_activate` |  | `machine`: string |
| `inventory_explore-sample-data_activate` |  | `machine`: string |
| `inventory_command-palette_show` | 是 | `machine`: string |

## assets（18 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|

## hiring（40 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `hiring_yet_open` | 是 | `target`*: string, `machine`: string |
| `hiring_candidates-not-yet-hired_select` | 是 | `target`*: string, `machine`: string |
| `hiring_interviews-today_select` | 是 | `target`*: string, `machine`: string |
| `hiring_offers-signature_select` | 是 | `target`*: string, `machine`: string |
| `hiring_main_select` | 是 | `target`*: string, `machine`: string |
| `hiring_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `hiring_searchctrl-k_activate` |  | `machine`: string |
| `hiring_overview_activate` |  | `machine`: string |
| `hiring_jobs_activate` |  | `machine`: string |
| `hiring_pipeline_activate` |  | `machine`: string |
| `hiring_interviews_activate` |  | `machine`: string |
| `hiring_offers_activate` |  | `machine`: string |
| `hiring_onboarding_activate` |  | `machine`: string |
| `hiring_reports_activate` |  | `machine`: string |
| `hiring_settings_show` | 是 | `machine`: string |
| `hiring_theme_activate` |  | `machine`: string |
| `hiring_puter_show` | 是 | `machine`: string |
| `hiring_reports-2_activate` |  | `machine`: string |
| `hiring_close_close` | 是 | `machine`: string |
| `hiring_set-up-hiring_activate` |  | `machine`: string |
| `hiring_explore-sample-data_activate` |  | `machine`: string |
| `hiring_command-palette_show` | 是 | `machine`: string |

## shifts（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `shifts_theme_select` | 是 | `target`*: string, `machine`: string |
| `shifts_skip_dismiss` | 是 | `target`*: string, `machine`: string |
| `shifts_home_activate` |  | `machine`: string |
| `shifts_schedule_schedule` |  | `machine`: string |
| `shifts_team_activate` |  | `machine`: string |
| `shifts_availability_activate` |  | `machine`: string |
| `shifts_swaps_activate` |  | `machine`: string |
| `shifts_attendance_activate` |  | `machine`: string |
| `shifts_reports_activate` |  | `machine`: string |
| `shifts_backup-restore_activate` |  | `machine`: string |
| `shifts_out_sign` |  | `machine`: string |
| `shifts_puter_show` | 是 | `machine`: string |
| `shifts_employee_create` |  | `machine`: string |
| `shifts_sample-data_import` |  | `machine`: string |
| `shifts_close_close` | 是 | `machine`: string |
| `shifts_set-up-team_activate` |  | `machine`: string |
| `shifts_explore-sample-data_activate` |  | `machine`: string |

## childcare（57 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `childcare_children-enrolled_select` | 是 | `target`*: string, `machine`: string |
| `childcare_absent-reported_select` | 是 | `target`*: string, `machine`: string |
| `childcare_staff-staff-members_select` | 是 | `target`*: string, `machine`: string |
| `childcare_ratio-rooms-ratio_select` | 是 | `target`*: string, `machine`: string |
| `childcare_content_dismiss` | 是 | `machine`: string |
| `childcare_log-or-add-n_activate` |  | `machine`: string |
| `childcare_home_show` | 是 | `machine`: string |
| `childcare_check-in_show` | 是 | `machine`: string |
| `childcare_activities_show` | 是 | `machine`: string |
| `childcare_messages_show` | 是 | `machine`: string |
| `childcare_children_show` | 是 | `machine`: string |
| `childcare_families_show` | 是 | `machine`: string |
| `childcare_rooms_show` | 是 | `machine`: string |
| `childcare_staff_show` | 是 | `machine`: string |
| `childcare_calendar_show` | 是 | `machine`: string |
| `childcare_menus_show` | 是 | `machine`: string |
| `childcare_billing_show` | 是 | `machine`: string |
| `childcare_reports_show` | 是 | `machine`: string |
| `childcare_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `childcare_puter_show` | 是 | `machine`: string |
| `childcare_navigation_collapse` | 是 | `machine`: string |
| `childcare_search_search` | 是 | `machine`: string |
| `childcare_keyboard-shortcuts_activate` |  | `machine`: string |
| `childcare_settings_show` | 是 | `machine`: string |
| `childcare_account-appearance_activate` |  | `machine`: string |
| `childcare_kiosk_show` | 是 | `machine`: string |
| `childcare_check_run` |  | `machine`: string |
| `childcare_log-activity_activate` |  | `machine`: string |
| `childcare_room_create` |  | `machine`: string |
| `childcare_log_open` | 是 | `machine`: string |
| `childcare_log-activity-2_activate` |  | `machine`: string |
| `childcare_calendar-2_show` | 是 | `machine`: string |
| `childcare_it_dismiss` | 是 | `machine`: string |
| `childcare_close_close` | 是 | `machine`: string |
| `childcare_school-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `childcare_rooms_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `childcare_use-sample-data_activate` |  | `machine`: string |
| `childcare_get-started_activate` |  | `machine`: string |
| `childcare_command-palette_show` | 是 | `machine`: string |

## field-service（58 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `field-service_workflow_select` | 是 | `target`*: string, `machine`: string |
| `field-service_paymentowed-you_select` | 是 | `target`*: string, `machine`: string |
| `field-service_content_dismiss` | 是 | `machine`: string |
| `field-service_n_create` |  | `machine`: string |
| `field-service_home_show` | 是 | `machine`: string |
| `field-service_schedule_schedule` |  | `machine`: string |
| `field-service_clients_show` | 是 | `machine`: string |
| `field-service_requests_show` | 是 | `machine`: string |
| `field-service_quotes_show` | 是 | `machine`: string |
| `field-service_jobs_show` | 是 | `machine`: string |
| `field-service_invoices_show` | 是 | `machine`: string |
| `field-service_payments_show` | 是 | `machine`: string |
| `field-service_timesheets_show` | 是 | `machine`: string |
| `field-service_expenses_show` | 是 | `machine`: string |
| `field-service_reports_show` | 是 | `machine`: string |
| `field-service_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `field-service_puter_show` | 是 | `machine`: string |
| `field-service_navigation_collapse` | 是 | `machine`: string |
| `field-service_search_search` | 是 | `machine`: string |
| `field-service_keyboard-shortcuts_activate` |  | `machine`: string |
| `field-service_settings_show` | 是 | `machine`: string |
| `field-service_account-appearance_activate` |  | `machine`: string |
| `field-service_dismiss_dismiss` | 是 | `machine`: string |
| `field-service_business-details_create` |  | `machine`: string |
| `field-service_services-you-offer_create` |  | `machine`: string |
| `field-service_team_create` |  | `machine`: string |
| `field-service_first-client_create` |  | `machine`: string |
| `field-service_first-quote_send` |  | `machine`: string |
| `field-service_schedule-2_schedule` |  | `machine`: string |
| `field-service_job_create` |  | `machine`: string |
| `field-service_reports-2_show` | 是 | `machine`: string |
| `field-service_close_close` | 是 | `machine`: string |
| `field-service_business-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `field-service_name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `field-service_industry_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `field-service_currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `field-service_sample-data_import` |  | `machine`: string |
| `field-service_get-started_activate` |  | `machine`: string |
| `field-service_it_dismiss` | 是 | `machine`: string |
| `field-service_command-palette_show` | 是 | `machine`: string |

## legal（61 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `legal_timer_start` |  | `target`*: string, `machine`: string |
| `legal_draft-bills-bills_select` | 是 | `target`*: string, `machine`: string |
| `legal_unpaid-bills_select` | 是 | `target`*: string, `machine`: string |
| `legal_overdue-bills_select` | 是 | `target`*: string, `machine`: string |
| `legal_held-trust-trust-accounts_select` | 是 | `target`*: string, `machine`: string |
| `legal_firm-name_select` | 是 | `target`*: string, `machine`: string |
| `legal_content_dismiss` | 是 | `machine`: string |
| `legal_legal-dashboard_show` | 是 | `machine`: string |
| `legal_dashboard_show` | 是 | `machine`: string |
| `legal_calendar_show` | 是 | `machine`: string |
| `legal_tasks_show` | 是 | `machine`: string |
| `legal_matters_show` | 是 | `machine`: string |
| `legal_contacts_show` | 是 | `machine`: string |
| `legal_activities_show` | 是 | `machine`: string |
| `legal_billing_show` | 是 | `machine`: string |
| `legal_accounts_show` | 是 | `machine`: string |
| `legal_documents_show` | 是 | `machine`: string |
| `legal_communications_show` | 是 | `machine`: string |
| `legal_reports_show` | 是 | `machine`: string |
| `legal_settings_show` | 是 | `machine`: string |
| `legal_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `legal_navigation_collapse` | 是 | `machine`: string |
| `legal_search_search` | 是 | `machine`: string |
| `legal_timer-details_activate` |  | `machine`: string |
| `legal_n_create` |  | `machine`: string |
| `legal_alerts_activate` |  | `machine`: string |
| `legal_account-appearance_activate` |  | `machine`: string |
| `legal_task_create` |  | `machine`: string |
| `legal_time_record` |  | `machine`: string |
| `legal_personal_show` | 是 | `machine`: string |
| `legal_firm_show` | 是 | `machine`: string |
| `legal_firm-users_open` | 是 | `machine`: string |
| `legal_calendar-2_show` | 是 | `machine`: string |
| `legal_matters-2_show` | 是 | `machine`: string |
| `legal_matter_create` |  | `machine`: string |
| `legal_activities-2_show` | 是 | `machine`: string |
| `legal_billing-2_show` | 是 | `machine`: string |
| `legal_i-understand_activate` |  | `machine`: string |
| `legal_close_close` | 是 | `machine`: string |
| `legal_currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `legal_explore-sample-data_activate` |  | `machine`: string |
| `legal_continue_activate` |  | `machine`: string |
| `legal_command-palette_show` | 是 | `machine`: string |

## fleet（59 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `fleet_content_dismiss` | 是 | `machine`: string |
| `fleet_dashboard_show` | 是 | `machine`: string |
| `fleet_dashboard-2_show` | 是 | `machine`: string |
| `fleet_vehicles_activate` |  | `machine`: string |
| `fleet_inspections_activate` |  | `machine`: string |
| `fleet_issues_show` | 是 | `machine`: string |
| `fleet_reminders_activate` |  | `machine`: string |
| `fleet_service_activate` |  | `machine`: string |
| `fleet_contacts_show` | 是 | `machine`: string |
| `fleet_vendors_show` | 是 | `machine`: string |
| `fleet_parts-inventory_activate` |  | `machine`: string |
| `fleet_fuel-energy_show` | 是 | `machine`: string |
| `fleet_documents_show` | 是 | `machine`: string |
| `fleet_reports_show` | 是 | `machine`: string |
| `fleet_settings_show` | 是 | `machine`: string |
| `fleet_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `fleet_puter_show` | 是 | `machine`: string |
| `fleet_sidebar_collapse` | 是 | `machine`: string |
| `fleet_search_search` | 是 | `machine`: string |
| `fleet_keyboard-shortcuts_activate` |  | `machine`: string |
| `fleet_needs-attention_activate` |  | `machine`: string |
| `fleet_add_create` |  | `machine`: string |
| `fleet_account-appearance_activate` |  | `machine`: string |
| `fleet_inspection_start` |  | `machine`: string |
| `fleet_report-issue_show` | 是 | `machine`: string |
| `fleet_fuel_create` |  | `machine`: string |
| `fleet_vehicle_create` |  | `machine`: string |
| `fleet_contact_create` |  | `machine`: string |
| `fleet_inspection-forms_show` | 是 | `machine`: string |
| `fleet_service-programs_show` | 是 | `machine`: string |
| `fleet_team-access_show` | 是 | `machine`: string |
| `fleet_it_dismiss` | 是 | `machine`: string |
| `fleet_close_close` | 是 | `machine`: string |
| `fleet_fleet-or-company-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `fleet_distance_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `fleet_fuel-volume_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `fleet_currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `fleet_sample-data_start` |  | `machine`: string |
| `fleet_continue_activate` |  | `machine`: string |
| `fleet_command-palette_show` | 是 | `machine`: string |
| `fleet_document_save` |  | `machine`: string |

## property-management（63 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `property-management_collected-charges-posted-yet_select` | 是 | `target`*: string, `machine`: string |
| `property-management_outstanding-balances-is-paid-up_select` | 是 | `target`*: string, `machine`: string |
| `property-management_units-occupied_select` | 是 | `target`*: string, `machine`: string |
| `property-management_work-urgent_open` | 是 | `target`*: string, `machine`: string |
| `property-management_view_show` | 是 | `target`*: string, `machine`: string |
| `property-management_financials_select` | 是 | `target`*: string, `machine`: string |
| `property-management_renewals_select` | 是 | `target`*: string, `machine`: string |
| `property-management_calendar_select` | 是 | `target`*: string, `machine`: string |
| `property-management_listings_select` | 是 | `target`*: string, `machine`: string |
| `property-management_content_dismiss` | 是 | `machine`: string |
| `property-management_dashboard_show` | 是 | `machine`: string |
| `property-management_n_create` |  | `machine`: string |
| `property-management_dashboard-2_show` | 是 | `machine`: string |
| `property-management_rentals_activate` |  | `machine`: string |
| `property-management_properties_show` | 是 | `machine`: string |
| `property-management_rent-roll_show` | 是 | `machine`: string |
| `property-management_tenants_show` | 是 | `machine`: string |
| `property-management_rental-owners_show` | 是 | `machine`: string |
| `property-management_outstanding-balances_show` | 是 | `machine`: string |
| `property-management_leasing_activate` |  | `machine`: string |
| `property-management_accounting_activate` |  | `machine`: string |
| `property-management_maintenance_activate` |  | `machine`: string |
| `property-management_tasks_show` | 是 | `machine`: string |
| `property-management_communication_show` | 是 | `machine`: string |
| `property-management_calendar_show` | 是 | `machine`: string |
| `property-management_reports_show` | 是 | `machine`: string |
| `property-management_settings_show` | 是 | `machine`: string |
| `property-management_source-code-github-opens-tab_show` | 是 | `machine`: string |
| `property-management_puter_show` | 是 | `machine`: string |
| `property-management_navigation_collapse` | 是 | `machine`: string |
| `property-management_search_search` | 是 | `machine`: string |
| `property-management_keyboard-shortcuts_activate` |  | `machine`: string |
| `property-management_account-appearance_activate` |  | `machine`: string |
| `property-management_receive-payment_activate` |  | `machine`: string |
| `property-management_work-orderwork-order_create` |  | `machine`: string |
| `property-management_lease_create` |  | `machine`: string |
| `property-management_close_close` | 是 | `machine`: string |
| `property-management_company-name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `property-management_name_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `property-management_what-you-manage_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `property-management_currency_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `property-management_sample-portfolio_import` |  | `machine`: string |
| `property-management_get-started_activate` |  | `machine`: string |
| `property-management_it_dismiss` | 是 | `machine`: string |
| `property-management_command-palette_show` | 是 | `machine`: string |

## api-client（76 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `api-client_account_select` | 是 | `target`*: string, `machine`: string |
| `api-client_environment_select` | 是 | `target`*: string, `machine`: string |
| `api-client_requests-through_send` |  | `target`*: string, `machine`: string |
| `api-client_editor_dismiss` | 是 | `machine`: string |
| `api-client_collections-requests-environments_search` | 是 | `machine`: string |
| `api-client_import_import` |  | `machine`: string |
| `api-client_theme_activate` |  | `machine`: string |
| `api-client_settings_show` | 是 | `machine`: string |
| `api-client_collections_activate` |  | `machine`: string |
| `api-client_environments_activate` |  | `machine`: string |
| `api-client_history_activate` |  | `machine`: string |
| `api-client_collection_create` |  | `machine`: string |
| `api-client_filter_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `api-client_collection-2_create` |  | `machine`: string |
| `api-client_import-2_import` |  | `machine`: string |
| `api-client_sidebar_resize` |  | `machine`: string |
| `api-client_request_create` |  | `machine`: string |
| `api-client_open-tabs_activate` |  | `machine`: string |
| `api-client_quick-look-at-variables_activate` |  | `machine`: string |
| `api-client_requestctrlaltn_create` |  | `machine`: string |
| `api-client_collection-3_create` |  | `machine`: string |
| `api-client_import-3_import` |  | `machine`: string |
| `api-client_environment_create` |  | `machine`: string |
| `api-client_websocket_create` |  | `machine`: string |
| `api-client_collection_run` |  | `machine`: string |
| `api-client_sidebar_toggle` |  | `machine`: string |
| `api-client_console_activate` |  | `machine`: string |
| `api-client_cookies_activate` |  | `machine`: string |
| `api-client_response-layout_activate` |  | `machine`: string |
| `api-client_keyboard-shortcuts_activate` |  | `machine`: string |
| `api-client_source-code-github_show` | 是 | `machine`: string |
| `api-client_notification_dismiss` | 是 | `machine`: string |
| `api-client_system_activate` |  | `machine`: string |
| `api-client_light_activate` |  | `machine`: string |
| `api-client_dark_activate` |  | `machine`: string |
| `api-client_close_close` | 是 | `machine`: string |
| `api-client_general_show` | 是 | `machine`: string |
| `api-client_requests_show` | 是 | `machine`: string |
| `api-client_about_show` | 是 | `machine`: string |
| `api-client_system_toggle` |  | `machine`: string |
| `api-client_light_toggle` |  | `machine`: string |
| `api-client_dark_toggle` |  | `machine`: string |
| `api-client_below_toggle` |  | `machine`: string |
| `api-client_beside_toggle` |  | `machine`: string |
| `api-client_sync-now_activate` |  | `machine`: string |
| `api-client_everything_export` |  | `machine`: string |
| `api-client_websocket-request_create` |  | `machine`: string |
| `api-client_tabs_close` | 是 | `machine`: string |
| `api-client_no-environment_activate` |  | `machine`: string |
| `api-client_environment-none-environment_create` |  | `machine`: string |
| `api-client_manage-environments_activate` |  | `machine`: string |
| `api-client_edit_update` |  | `machine`: string |
| `api-client_automatic_activate` |  | `machine`: string |
| `api-client_browser-only_activate` |  | `machine`: string |
| `api-client_puter-relay_activate` |  | `machine`: string |
| `api-client_what-is-difference_activate` |  | `machine`: string |
| `api-client_below-request_activate` |  | `machine`: string |
| `api-client_beside-request_activate` |  | `machine`: string |

## chess（48 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `chess_black-rook_select` | 是 | `target`*: string, `machine`: string |
| `chess_black-knight_select` | 是 | `target`*: string, `machine`: string |
| `chess_black-bishop_select` | 是 | `target`*: string, `machine`: string |
| `chess_black-queen_select` | 是 | `target`*: string, `machine`: string |
| `chess_black-king_select` | 是 | `target`*: string, `machine`: string |
| `chess_black-pawn_select` | 是 | `target`*: string, `machine`: string |
| `chess_empty_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-pawn_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-rook_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-knight_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-bishop_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-queen_select` | 是 | `target`*: string, `machine`: string |
| `chess_white-king_select` | 是 | `target`*: string, `machine`: string |
| `chess_light-theme_activate` |  | `machine`: string |
| `chess_dark-theme_activate` |  | `machine`: string |
| `chess_follow-system-theme_activate` |  | `machine`: string |
| `chess_computer_activate` |  | `machine`: string |
| `chess_pass-play_activate` |  | `machine`: string |
| `chess_online_activate` |  | `machine`: string |
| `chess_game-as-pgn_copy` |  | `machine`: string |
| `chess_game-as-pgn-file_export` |  | `machine`: string |
| `chess_go-starting-position_activate` |  | `machine`: string |
| `chess_go-back-one-move_activate` |  | `machine`: string |
| `chess_go-forward-one-move_activate` |  | `machine`: string |
| `chess_return-current-position_activate` |  | `machine`: string |
| `chess_difficulty_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `chess_clock_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `chess_play-as_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `chess_game_create` |  | `machine`: string |
| `chess_undo_undo` |  | `machine`: string |

## backgammon（45 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `backgammon_point-white-checkers_select` | 是 | `target`*: string, `machine`: string |
| `backgammon_point-empty_select` | 是 | `target`*: string, `machine`: string |
| `backgammon_point-black-checkers_select` | 是 | `target`*: string, `machine`: string |
| `backgammon_light-theme_activate` |  | `machine`: string |
| `backgammon_dark-theme_activate` |  | `machine`: string |
| `backgammon_follow-system-theme_activate` |  | `machine`: string |
| `backgammon_black-bar-empty_activate` |  | `machine`: string |
| `backgammon_black-tray-empty_activate` |  | `machine`: string |
| `backgammon_white-bar-empty_activate` |  | `machine`: string |
| `backgammon_white-tray-empty_activate` |  | `machine`: string |
| `backgammon_computer_activate` |  | `machine`: string |
| `backgammon_pass-play_activate` |  | `machine`: string |
| `backgammon_online_activate` |  | `machine`: string |
| `backgammon_moves_activate` |  | `machine`: string |
| `backgammon_game-as-mat-transcript_copy` |  | `machine`: string |
| `backgammon_game-as-mat-file_export` |  | `machine`: string |
| `backgammon_roll-start_activate` |  | `machine`: string |
| `backgammon_difficulty_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `backgammon_clock_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `backgammon_doubling-cube_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `backgammon_play-as_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `backgammon_game_create` |  | `machine`: string |
| `backgammon_turn_undo` |  | `machine`: string |
| `backgammon_go-starting-position_activate` |  | `machine`: string |
| `backgammon_go-back-one-turn_activate` |  | `machine`: string |
| `backgammon_go-forward-one-turn_activate` |  | `machine`: string |
| `backgammon_return-current-position_activate` |  | `machine`: string |

## checkers（39 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `checkers_white-man_select` | 是 | `target`*: string, `machine`: string |
| `checkers_empty_select` | 是 | `target`*: string, `machine`: string |
| `checkers_black-man_select` | 是 | `target`*: string, `machine`: string |
| `checkers_light-theme_activate` |  | `machine`: string |
| `checkers_dark-theme_activate` |  | `machine`: string |
| `checkers_follow-system-theme_activate` |  | `machine`: string |
| `checkers_computer_activate` |  | `machine`: string |
| `checkers_pass-play_activate` |  | `machine`: string |
| `checkers_online_activate` |  | `machine`: string |
| `checkers_moves_activate` |  | `machine`: string |
| `checkers_game-as-pdn_copy` |  | `machine`: string |
| `checkers_game-as-pdn-file_export` |  | `machine`: string |
| `checkers_difficulty_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `checkers_clock_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `checkers_play-as_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `checkers_game_create` |  | `machine`: string |
| `checkers_undo_undo` |  | `machine`: string |
| `checkers_go-starting-position_activate` |  | `machine`: string |
| `checkers_go-back-one-move_activate` |  | `machine`: string |
| `checkers_go-forward-one-move_activate` |  | `machine`: string |
| `checkers_return-current-position_activate` |  | `machine`: string |

## solitaire（27 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `solitaire_klondike-draw_select` | 是 | `target`*: string, `machine`: string |
| `solitaire_vegas-draw_select` | 是 | `target`*: string, `machine`: string |
| `solitaire_spider-suit_select` | 是 | `target`*: string, `machine`: string |
| `solitaire_spider-suits_select` | 是 | `target`*: string, `machine`: string |
| `solitaire_game_select` | 是 | `machine`: string |
| `solitaire_undo_undo` |  | `machine`: string |
| `solitaire_powered-by-puter_show` | 是 | `machine`: string |
| `solitaire_document_create` |  | `machine`: string |
| `solitaire_edit_undo` |  | `machine`: string |

## sudoku（57 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `sudoku_row-column-clue_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_row-column-empty_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_pencil-n_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_remaining_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_settings-row-column-empty_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_settings-row-column-clue_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_settings-remaining_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_tidy-pencil_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_puzzle-row-column-clue_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_puzzle-row-column-empty_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_puzzle-remaining_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_daily-row-column-clue_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_daily-row-column-empty_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_daily-remaining_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_powered-by-puter-row-column-clue_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_powered-by-puter-remaining_select` | 是 | `target`*: string, `machine`: string |
| `sudoku_light-theme_activate` |  | `machine`: string |
| `sudoku_dark-theme_activate` |  | `machine`: string |
| `sudoku_match-system-theme_activate` |  | `machine`: string |
| `sudoku_records_activate` |  | `machine`: string |
| `sudoku_settings_show` | 是 | `machine`: string |
| `sudoku_signed-as-local_activate` |  | `machine`: string |
| `sudoku_pause_pause` |  | `machine`: string |
| `sudoku_ctrlz_undo` |  | `machine`: string |
| `sudoku_ctrlshiftz_redo` |  | `machine`: string |
| `sudoku_erase-backspace_activate` |  | `machine`: string |
| `sudoku_hint-h_activate` |  | `machine`: string |
| `sudoku_next-puzzle_set` |  | `value`*: string, `submit`: boolean, `machine`: string |
| `sudoku_puzzle_create` |  | `machine`: string |
| `sudoku_daily_activate` |  | `machine`: string |
| `sudoku_powered-by-puter_show` | 是 | `machine`: string |
| `sudoku_check-as-i-go_toggle` |  | `machine`: string |
| `sudoku_highlight-row-column-box_toggle` |  | `machine`: string |
| `sudoku_highlight-matching-digits_toggle` |  | `machine`: string |
| `sudoku_show-digits-remaining_toggle` |  | `machine`: string |
| `sudoku_show-clock_toggle` |  | `machine`: string |
| `sudoku_done_confirm` |  | `machine`: string |
| `sudoku_edit_redo-shift` |  | `machine`: string |
| `sudoku_edit_undo` |  | `machine`: string |

## machine（10 个工具）

### `machine_list`

列出机器（本机与已配对的机器）。CLI：foxos machine list [--check]。示例：foxos machine list --check --json

只读：是 · 破坏性：否 · CLI：`foxos machine list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `check` | boolean |  | 逐台检查在线状态 |

调用示例：

```json
{"name": "machine_list", "arguments": {}}
```

### `machine_pair`

与另一台狐狸OS 配对。CLI：foxos machine pair --name NAME --url URL --code CODE [--fingerprint FINGERPRINT] [--client CLIENT]。限制：只有人可以配对机器或修改授权。示例：foxos machine pair --name vm1 --url https://192.168.1.20:7443 --code AB12-CD34-EF56 --fingerprint 3f…

只读：否 · 破坏性：否 · CLI：`foxos machine pair`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 机器名 |
| `url` | string | 是 | 被控端地址 https://主机:7443 |
| `code` | string | 是 | 被控端给出的配对码 |
| `fingerprint` | string |  | 被控端证书的 sha256 指纹（强烈建议填写） |
| `client` | string |  | 本机在对方那里显示的名字（默认主机名） |

调用示例：

```json
{"name": "machine_pair", "arguments": {"name": "…", "url": "…", "code": "…"}}
```

### `machine_remove`

移除配对的机器。CLI：foxos machine remove MACHINE。示例：foxos machine remove vm1

只读：否 · 破坏性：是 · CLI：`foxos machine remove`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 机器名 |

调用示例：

```json
{"name": "machine_remove", "arguments": {"name": "…"}}
```

### `machine_ping`

检查机器是否在线，看授权与谁在操作。CLI：foxos machine ping MACHINE。示例：foxos machine ping vm1 --json

只读：是 · 破坏性：否 · CLI：`foxos machine ping`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 机器名 |

调用示例：

```json
{"name": "machine_ping", "arguments": {"name": "…"}}
```

### `machine_call`

在一台机器上执行一条 foxos 命令。CLI：foxos machine call MACHINE --command COMMAND [--params PARAMS]。示例：foxos machine call vm1 --command files.list --params '{"path":"."}'

只读：否 · 破坏性：否 · CLI：`foxos machine call`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 机器名 |
| `command` | string | 是 | 命令 ID（如 files.list） |
| `params` | object |  | 命令参数（JSON 对象） |

调用示例：

```json
{"name": "machine_call", "arguments": {"name": "…", "command": "…"}}
```

### `machine_host_code`

（被控端）生成一次性配对码。CLI：foxos machine host code [--ttl TTL]。限制：只有人可以配对机器或修改授权。示例：foxos machine host code --json

只读：否 · 破坏性：否 · CLI：`foxos machine host code`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `ttl` | integer |  | 配对码有效秒数 |

调用示例：

```json
{"name": "machine_host_code", "arguments": {}}
```

### `machine_host_clients`

（被控端）已配对的控制端与授权。CLI：foxos machine host clients。示例：foxos machine host clients --json

只读：是 · 破坏性：否 · CLI：`foxos machine host clients`

调用示例：

```json
{"name": "machine_host_clients", "arguments": {}}
```

### `machine_host_grant`

（被控端）给某台控制端的某个智能体授权。CLI：foxos machine host grant --client CLIENT --bot BOT --permissions PERMISSIONS [--apps APPS] [--scope SCOPE]。限制：只有人可以配对机器或修改授权；默认拒绝：没有授权的智能体什么都不能做；machine 与 control 命令永远不能远程执行。示例：foxos machine host grant --client laptop --bot coder --permissions read,create,modify --apps files --scope projects

只读：否 · 破坏性：否 · CLI：`foxos machine host grant`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `client` | string | 是 | 控制端名 |
| `bot` | string | 是 | 控制端上的智能体 ID（* 表示全部） |
| `permissions` | array | 是 | 权限：read、create、modify、delete、run |
| `apps` | array |  | 允许的应用（逗号分隔，不填表示全部） |
| `scope` | string |  | 允许的目录范围（工作空间内） |

调用示例：

```json
{"name": "machine_host_grant", "arguments": {"client": "…", "bot": "…", "permissions": []}}
```

### `machine_host_revoke`

（被控端）撤销授权。CLI：foxos machine host revoke --client CLIENT [--bot BOT]。示例：foxos machine host revoke --client laptop --bot coder

只读：否 · 破坏性：否 · CLI：`foxos machine host revoke`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `client` | string | 是 | 控制端名 |
| `bot` | string |  | 控制端上的智能体 ID（* 表示全部） |

调用示例：

```json
{"name": "machine_host_revoke", "arguments": {"client": "…"}}
```

### `machine_host_unpair`

（被控端）解除一台控制端的配对。CLI：foxos machine host unpair --client CLIENT。示例：foxos machine host unpair --client laptop

只读：否 · 破坏性：是 · CLI：`foxos machine host unpair`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `client` | string | 是 | 控制端名 |

调用示例：

```json
{"name": "machine_host_unpair", "arguments": {"client": "…"}}
```

## runtime（3 个工具）

### `runtime_list`

列出清单里的工具与安装状态。CLI：foxos runtime list [--phase {iso,firstboot,optional}] [--group {runtime,tools,agents,optional}]。示例：foxos runtime list --json

只读：是 · 破坏性：否 · CLI：`foxos runtime list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `phase` | string |  | 安装阶段 可选：iso / firstboot / optional |
| `group` | string |  | 分组 可选：runtime / tools / agents / optional |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "runtime_list", "arguments": {}}
```

### `runtime_doctor`

检查运行环境：缺什么、版本、PEP 668、PATH、磁盘。CLI：foxos runtime doctor。示例：foxos runtime doctor --json

只读：是 · 破坏性：否 · CLI：`foxos runtime doctor`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "runtime_doctor", "arguments": {}}
```

### `runtime_install`

安装工具（固定版本，官方来源，校验 sha256）；firstboot 表示全部首次登录项。CLI：foxos runtime install NAME... [--force] [--accept-license]。限制：只有人可以安装软件；只从清单里的官方地址下载；不可再分发的工具需要 --accept-license。示例：foxos runtime install codex codex-acp

只读：否 · 破坏性：否 · CLI：`foxos runtime install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | array | 是 | 工具名（见 runtime list），或 firstboot |
| `force` | boolean |  | 已安装也重新安装 |
| `accept_license` | boolean |  | 确认许可证（不可再分发的工具需要） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "runtime_install", "arguments": {"name": []}}
```

## sandbox（3 个工具）

### `sandbox_check`

本机可用的轻量隔离能力（机制、Landlock ABI、网络 / 信号隔离）。CLI：foxos sandbox check。示例：foxos sandbox check --json

只读：是 · 破坏性：否 · CLI：`foxos sandbox check`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sandbox_check", "arguments": {}}
```

### `sandbox_run`

在轻量沙箱中运行命令：只能读写工作空间，可选禁止联网。CLI：foxos sandbox run [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}] [--max-processes MAX_PROCESSES] [--memory-mb MEMORY_MB] [--cwd CWD] [--timeout TIMEOUT]。示例：foxos sandbox run --json -- python3 build.py

只读：否 · 破坏性：否 · CLI：`foxos sandbox run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `network` | string |  | 是否允许联网 可选：on / off |
| `read` | array |  | 额外只读路径（可重复） |
| `write` | array |  | 额外可写路径（可重复） |
| `home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写 可选：private / read / write |
| `windows_mode` | string |  | Windows：restricted 受限令牌 / appcontainer 可选：restricted / appcontainer |
| `max_processes` | integer |  | 最多进程数（Windows 作业对象） |
| `memory_mb` | integer |  | 内存上限 MB（Windows 作业对象） |
| `cwd` | string |  | 工作目录（工作空间内） |
| `timeout` | number |  | 超时秒数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sandbox_run", "arguments": {}}
```

### `sandbox_policy`

显示将生效的沙箱规则（不执行）。CLI：foxos sandbox policy [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}]。示例：foxos sandbox policy --network off --json -- node agent.js

只读：是 · 破坏性：否 · CLI：`foxos sandbox policy`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `network` | string |  | 是否允许联网 可选：on / off |
| `read` | array |  | 额外只读路径（可重复） |
| `write` | array |  | 额外可写路径（可重复） |
| `home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写 可选：private / read / write |
| `windows_mode` | string |  | Windows：restricted 受限令牌 / appcontainer 可选：restricted / appcontainer |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sandbox_policy", "arguments": {}}
```

## sheets（6 个工具）

### `sheets_create`

新建一个 .xlsx 工作簿。CLI：foxos sheets create FILE [--sheet SHEET] [--headers HEADERS] [--force]。限制：只创建 .xlsx；父目录不存在时自动创建。示例：foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales

只读：否 · 破坏性：否 · CLI：`foxos sheets create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 要创建的工作簿路径（.xlsx） |
| `sheet` | string |  | 第一个工作表的名称 |
| `headers` | array |  | 第一行表头，逗号分隔（CLI）或字符串数组（工具接口） |
| `force` | boolean |  | 文件已存在时覆盖（上一版本会保存到 .foxos/versions） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_create", "arguments": {"file": "…"}}
```

### `sheets_read`

读取工作表单元格（公式、图表；可选用 LibreOffice 求值）。CLI：foxos sheets read FILE [--sheet SHEET] [--range RANGE] [--computed]。限制：单次最多 20000 个单元格；--computed 需要 LibreOffice。示例：foxos sheets read sales.xlsx

只读：是 · 破坏性：否 · CLI：`foxos sheets read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `range` | string |  | A1 记法区域，如 A1:C10；默认整个已用区域 |
| `computed` | boolean |  | 用 LibreOffice 重算公式，额外返回 values（不修改原文件） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_read", "arguments": {"file": "…"}}
```

### `sheets_write`

写入单元格值或公式（CELL=VALUE，以 = 开头为公式）。CLI：foxos sheets write FILE CELL=VALUE... [--sheet SHEET] [--create-sheet]。限制：公式按 Excel 英文函数名写入，不在写入时校验或求值；不支持写入样式、合并单元格（阶段 0）。示例：foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135

只读：否 · 破坏性：否 · CLI：`foxos sheets write`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `cells` | object | 是 | 要写入的单元格：{"A1": "Month", "B2": 120, "B14": "=SUM(B2:B13)"}；CLI 中写成 A1=Month B2=120 B14==SUM(B2:B13)，数字自动识别，TRUE/FALSE 为布尔，空值清空单元格 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `create_sheet` | boolean |  | 工作表不存在时新建 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_write", "arguments": {"file": "…", "cells": {}}}
```

### `sheets_chart_create`

基于单元格区域创建原生 Excel 图表。CLI：foxos sheets chart create FILE --type {bar,line,pie} --data DATA [--categories CATEGORIES] [--title TITLE] [--sheet SHEET] [--anchor ANCHOR] [--x-title X_TITLE] [--y-title Y_TITLE] [--no-header]。限制：仅 bar / line / pie；饼图只能一个系列；图表样式、颜色暂不可配置。示例：foxos sheets chart create sales.xlsx --type bar --data B1:B13 --categories A2:A13 --title '月度销售额'

只读：否 · 破坏性：否 · CLI：`foxos sheets chart create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `type` | string | 是 | 图表类型 可选：bar / line / pie |
| `data` | string | 是 | 数据区域（按列为系列，首行默认为系列名），如 B1:B13 |
| `categories` | string |  | 分类（X 轴）区域，如 A2:A13 |
| `title` | string |  | 图表标题 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `anchor` | string |  | 图表左上角所在单元格，默认放在数据右侧 |
| `x_title` | string |  | X 轴标题（bar/line） |
| `y_title` | string |  | Y 轴标题（bar/line） |
| `no_header` | boolean |  | 数据区域首行不是系列名 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_chart_create", "arguments": {"file": "…", "type": "bar", "data": "…"}}
```

### `sheets_chart_list`

列出工作簿中的图表。CLI：foxos sheets chart list FILE [--sheet SHEET]。示例：foxos sheets chart list sales.xlsx --json

只读：是 · 破坏性：否 · CLI：`foxos sheets chart list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_chart_list", "arguments": {"file": "…"}}
```

### `sheets_export`

导出为 csv / pdf / ods / xlsx（格式由输出文件扩展名决定）。CLI：foxos sheets export FILE OUTPUT [--sheet SHEET] [--force]。限制：csv 只导出一个工作表，公式导出为求值结果（需 LibreOffice，否则导出公式文本）；pdf / ods 需要 LibreOffice。示例：foxos sheets export sales.xlsx sales.csv

只读：否 · 破坏性：否 · CLI：`foxos sheets export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 源工作簿路径 |
| `output` | string | 是 | 输出路径：.csv / .pdf / .ods / .xlsx |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `force` | boolean |  | 输出文件已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "sheets_export", "arguments": {"file": "…", "output": "…"}}
```

## slides（6 个工具）

### `slides_create`

新建一个 .pptx 演示文稿（可带标题页）。CLI：foxos slides create FILE [--title TITLE] [--subtitle SUBTITLE] [--aspect {16:9,4:3}] [--force]。示例：foxos slides create deck.pptx --title '2026 年销售分析' --subtitle '数据组'

只读：否 · 破坏性：否 · CLI：`foxos slides create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `title` | string |  | 标题页标题 |
| `subtitle` | string |  | 标题页副标题 |
| `aspect` | string |  | 页面比例 可选：16:9 / 4:3 |
| `force` | boolean |  | 已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_create", "arguments": {"file": "…"}}
```

### `slides_read`

读取每页的版式、标题、文本、图表数据与备注。CLI：foxos slides read FILE。示例：foxos slides read deck.pptx --json

只读：是 · 破坏性：否 · CLI：`foxos slides read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_read", "arguments": {"file": "…"}}
```

### `slides_add`

追加一页（标题 + 要点 / 图片 / 备注）。CLI：foxos slides add FILE [--title TITLE] [--bullet BULLET] [--layout {title,title-content,section,two-content,title-only,blank}] [--image IMAGE] [--notes NOTES]。示例：foxos slides add deck.pptx -t 全年概况 -b '销售额 2013 万元' -b '同比增长 12%'

只读：否 · 破坏性：否 · CLI：`foxos slides add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `title` | string |  | 页面标题 |
| `bullet` | array |  | 要点，可重复：--bullet 一 --bullet 二 |
| `layout` | string |  | 版式 可选：title / title-content / section / two-content / title-only / blank |
| `image` | string |  | 插入图片（工作空间内 png/jpg） |
| `notes` | string |  | 演讲者备注 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_add", "arguments": {"file": "…"}}
```

### `slides_chart_add`

插入原生 PowerPoint 图表（默认新建一页）。CLI：foxos slides chart add FILE --type {bar,line,pie} --categories CATEGORIES --values VALUES [--slide SLIDE] [--series-name SERIES_NAME] [--title TITLE]。示例：foxos slides chart add deck.pptx --type bar -c Q1,Q2,Q3,Q4 -v 405,428,547,633 --title 季度销售额

只读：否 · 破坏性：否 · CLI：`foxos slides chart add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `type` | string | 是 | 图表类型 可选：bar / line / pie |
| `categories` | array | 是 | 分类，逗号分隔 |
| `values` | array | 是 | 数值，逗号分隔，与分类一一对应 |
| `slide` | integer |  | 插入到已有的第 N 页（从 1 开始）；不填则新建一页 |
| `series_name` | string |  | 系列名称 |
| `title` | string |  | 新建页时的页面标题 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_chart_add", "arguments": {"file": "…", "type": "bar", "categories": [], "values": []}}
```

### `slides_replace`

查找并替换所有页中的文本。CLI：foxos slides replace FILE --find FIND --replace REPLACE。限制：只在同一个文本 run 内匹配。示例：foxos slides replace deck.pptx --find 2025 --replace 2026

只读：否 · 破坏性：否 · CLI：`foxos slides replace`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `find` | string | 是 | 要查找的文本 |
| `replace` | string | 是 | 替换为 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_replace", "arguments": {"file": "…", "find": "…", "replace": "…"}}
```

### `slides_export`

导出为 pdf / odp。CLI：foxos slides export FILE OUTPUT [--force]。限制：需要 LibreOffice。示例：foxos slides export deck.pptx deck.pdf

只读：否 · 破坏性：否 · CLI：`foxos slides export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `output` | string | 是 | 输出路径 |
| `force` | boolean |  | 输出已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "slides_export", "arguments": {"file": "…", "output": "…"}}
```

## ssh（7 个工具）

### `ssh_status`

SSH 是否开启、地址、端口、密码登录、root 登录、防火墙、公钥数量与连接命令。CLI：foxos ssh status [--user USER]。示例：foxos ssh status

只读：是 · 破坏性：否 · CLI：`foxos ssh status`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user` | string |  | 用户（默认当前用户） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_status", "arguments": {}}
```

### `ssh_enable`

开启 SSH（只允许密钥登录，防火墙放行 22）。CLI：foxos ssh enable。限制：只有人（human 身份）能执行。示例：foxos ssh enable

只读：否 · 破坏性：否 · CLI：`foxos ssh enable`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_enable", "arguments": {}}
```

### `ssh_disable`

关闭 SSH 服务。CLI：foxos ssh disable。示例：foxos ssh disable

只读：否 · 破坏性：否 · CLI：`foxos ssh disable`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_disable", "arguments": {}}
```

### `ssh_keys_add`

添加 SSH 公钥到 authorized_keys：粘贴、文件或 GitHub 用户名。CLI：foxos ssh keys add [--key KEY] [--file FILE] [--github GITHUB] [--user USER]。限制：只有人（human 身份）能执行。示例：foxos ssh keys add --github octocat

只读：否 · 破坏性：否 · CLI：`foxos ssh keys add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string |  | 公钥文本（一行或多行） |
| `file` | string |  | 公钥文件路径 |
| `github` | string |  | 从 https://github.com/<用户名>.keys 导入 |
| `user` | string |  | 用户（默认当前用户） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_keys_add", "arguments": {}}
```

### `ssh_keys_list`

列出 authorized_keys 里的公钥（类型、注释、指纹）。CLI：foxos ssh keys list [--user USER]。示例：foxos ssh keys list

只读：是 · 破坏性：否 · CLI：`foxos ssh keys list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user` | string |  | 用户（默认当前用户） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_keys_list", "arguments": {}}
```

### `ssh_keys_remove`

按序号或指纹删除一个公钥。CLI：foxos ssh keys remove INDEX|SHA256:... [--user USER]。示例：foxos ssh keys remove 2

只读：否 · 破坏性：否 · CLI：`foxos ssh keys remove`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 序号、指纹（SHA256:…）或注释 |
| `user` | string |  | 用户（默认当前用户） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_keys_remove", "arguments": {"key": "…"}}
```

### `ssh_password`

打开或关闭 SSH 密码登录（打开时可同时设置一个足够强的新密码）。CLI：foxos ssh password on|off [--new-password NEW_PASSWORD]。限制：打开密码登录只有人能执行，并需要 sudo 密码；关闭任何人都可以。示例：foxos ssh password off

只读：否 · 破坏性：否 · CLI：`foxos ssh password`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `state` | string | 是 | on 或 off |
| `new_password` | string |  | 新密码（至少 12 位，三类字符） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "ssh_password", "arguments": {"state": "…"}}
```

## workspace（1 个工具）

### `workspace_info`

显示工作空间根目录、审计日志位置与文件数。CLI：foxos workspace info。示例：foxos workspace info --json

只读：是 · 破坏性：否 · CLI：`foxos workspace info`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "workspace_info", "arguments": {}}
```

## files（8 个工具）

### `files_list`

列出目录内容（默认工作空间根目录）。CLI：foxos files list [PATH] [--recursive] [--hidden]。示例：foxos files list

只读：是 · 破坏性：否 · CLI：`foxos files list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 目录（工作空间内），默认根目录 |
| `recursive` | boolean |  | 递归列出所有文件 |
| `hidden` | boolean |  | 包含以 . 开头的文件 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_list", "arguments": {}}
```

### `files_read`

读取 UTF-8 文本文件。CLI：foxos files read PATH。限制：上限 5 MB；二进制与办公文件请用对应应用命令。示例：foxos files read notes.md

只读：是 · 破坏性：否 · CLI：`foxos files read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_read", "arguments": {"path": "…"}}
```

### `files_write`

写入 UTF-8 文本文件（原子保存，覆盖前保留上一版）。CLI：foxos files write PATH --content CONTENT [--expect-mtime EXPECT_MTIME] [--force]。示例：foxos files write notes.md --content '# 标题'

只读：否 · 破坏性：否 · CLI：`foxos files write`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |
| `content` | string | 是 | 文件内容；CLI 可用 --content-stdin 从标准输入读取 |
| `expect_mtime` | number |  | 乐观并发检查：文件当前修改时间必须等于该值，否则 CONFLICT |
| `force` | boolean |  | 目标已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_write", "arguments": {"path": "…", "content": "…"}}
```

### `files_mkdir`

新建文件夹（含父目录）。CLI：foxos files mkdir PATH。示例：foxos files mkdir reports/2026

只读：否 · 破坏性：否 · CLI：`foxos files mkdir`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件夹路径 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_mkdir", "arguments": {"path": "…"}}
```

### `files_rename`

重命名或移动文件 / 文件夹。CLI：foxos files rename SOURCE TARGET [--force]。示例：foxos files rename draft.md final.md

只读：否 · 破坏性：否 · CLI：`foxos files rename`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `source` | string | 是 | 原路径 |
| `target` | string | 是 | 新路径 |
| `force` | boolean |  | 目标已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_rename", "arguments": {"source": "…", "target": "…"}}
```

### `files_delete`

删除文件或文件夹（移入回收站，可恢复）。CLI：foxos files delete PATH。限制：移入 .foxos/trash/，用 foxos files restore 恢复。示例：foxos files delete old.csv

只读：否 · 破坏性：是 · CLI：`foxos files delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 要删除的路径 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_delete", "arguments": {"path": "…"}}
```

### `files_restore`

从回收站恢复。CLI：foxos files restore TRASH_ID [--force]。示例：foxos files restore 20261110T2051-ab12cd

只读：否 · 破坏性：否 · CLI：`foxos files restore`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `trash_id` | string | 是 | 回收站条目 ID（files delete 返回，或 files trash 查看） |
| `force` | boolean |  | 目标已存在时覆盖 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_restore", "arguments": {"trash_id": "…"}}
```

### `files_trash`

列出回收站。CLI：foxos files trash。示例：foxos files trash --json

只读：是 · 破坏性：否 · CLI：`foxos files trash`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "files_trash", "arguments": {}}
```

## audit（1 个工具）

### `audit_tail`

查看最近的审计记录。CLI：foxos audit tail [--limit LIMIT] [--filter-agent AGENT] [--command COMMAND]。限制：查询本身不写入审计日志。示例：foxos audit tail -n 50

只读：是 · 破坏性：否 · CLI：`foxos audit tail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer |  | 返回条数 |
| `agent` | string |  | 只看某个智能体 |
| `command` | string |  | 按命令前缀过滤，如 sheets.write |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "audit_tail", "arguments": {}}
```

## queue（2 个工具）

### `queue_create`

把一个任务目标加入队列。CLI：foxos queue create GOAL。限制：只记录任务；执行由 ACP 智能体会话完成。示例：foxos queue create '根据 sales.xlsx 制作分析报告'

只读：否 · 破坏性：否 · CLI：`foxos queue create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `goal` | string | 是 | 任务目标（自然语言） |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "queue_create", "arguments": {"goal": "…"}}
```

### `queue_list`

列出任务队列。CLI：foxos queue list [--limit LIMIT]。示例：foxos queue list --json

只读：是 · 破坏性：否 · CLI：`foxos queue list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer |  | 返回条数 |
| `machine` | string |  | 在哪台狐狸OS 上执行：local 或已配对机器名（foxos machine list） |

调用示例：

```json
{"name": "queue_list", "arguments": {}}
```

## control（3 个工具）

### `control_status`

查看是否处于人工接管（暂停）状态。CLI：foxos control status。限制：查询本身不写入审计日志。示例：foxos control status --json

只读：是 · 破坏性：否 · CLI：`foxos control status`

调用示例：

```json
{"name": "control_status", "arguments": {}}
```

### `control_pause`

人工接管：暂停所有智能体的写操作。CLI：foxos control pause [--reason REASON] [--only IDENTITY]。限制：只有 human 身份可以执行；身份由调用方声明（--agent），属于应用层约束。示例：foxos control pause --reason '我来改第 3 页数据'

只读：否 · 破坏性：否 · CLI：`foxos control pause`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |

调用示例：

```json
{"name": "control_pause", "arguments": {}}
```

### `control_resume`

结束人工接管，恢复智能体写操作。CLI：foxos control resume [--only IDENTITY]。限制：只有 human 身份可以执行。示例：foxos control resume

只读：否 · 破坏性：否 · CLI：`foxos control resume`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `targets` | array |  | 只恢复这些身份；不填则全部恢复 |

调用示例：

```json
{"name": "control_resume", "arguments": {}}
```

