# foxos 命令参考

> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos help --json` 同源，请勿手改。

## 通用约定

- **invocation**：foxos [全局选项] <app> <command> [参数]；全局选项可放在任意位置
- **global_options**
  - `--json`：以 JSON 输出：成功 {ok:true, command, result}，失败 {ok:false, command, error:{code, exit_code, message, hint}}
  - `--workspace PATH`：工作空间根目录（默认 $FOXOS_WORKSPACE 或 ~/FoxOS/workspace）
  - `--agent NAME`：调用者身份，写入审计日志（默认 $FOXOS_AGENT 或 human）
  - `--task ID`：关联的任务 ID（默认 $FOXOS_TASK）
  - `--lang LANG`：界面语言：zh-CN（默认）或 en-US；也可用环境变量 FOXOS_LANG。JSON 字段名与错误码不随语言变化
  - `--lock-wait SECONDS`：目标文件被锁时最多等待的秒数（默认 0，立即返回 LOCKED）
  - `--machine NAME`：在这台已配对的狐狸OS 上执行（默认本机 local）
- **exit_codes**
  - 0：OK：成功
  - 1：ERROR：未分类错误或内部错误
  - 2：USAGE：参数错误
  - 3：NOT_FOUND：文件、工作表或命令不存在
  - 4：PERMISSION_DENIED：路径越出工作空间或访问保留目录
  - 5：LOCKED：目标文件正被其他写入者锁定
  - 6：DEPENDENCY_MISSING：缺少外部依赖（如 LibreOffice）
  - 7：CONFLICT：目标已存在等冲突（可用 --force 覆盖时会提示）
  - 8：PAUSED：人工接管中，智能体的写操作被暂停
- **paths**：所有路径相对于工作空间根目录；越出工作空间或访问 .foxos/ 返回 PERMISSION_DENIED（4）
- **formulas**：单元格值以 = 开头即为 Excel 公式，如 =SUM(B2:B13)；以 ' 开头强制为文本
- **audit**：每次调用（含失败与拒绝）都追加到 <workspace>/.foxos/audit.jsonl；只读自省命令 audit tail、control status 成功时不记录
- **tool_names**：工具接口名 = 命令 ID 把 . 换成 _，如 sheets.chart.create → sheets_chart_create

## acp — ACP 代码智能体：安装、登录、密钥、握手检查

通过 Agent Client Protocol（ACP）接入代码智能体：Claude Code、Codex、Gemini CLI、Qwen Code、opencode 等。智能体的文件读写与终端命令都走狐狸OS 内核（范围限制、写锁、审计、人工接管）。官方注册表：https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json

### `foxos acp agent list`

列出已安装的 ACP 智能体（--available 列出注册表）

```text
foxos acp agent list [--available]
```

工具接口名：`acp_agent_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `available` | `--available` | boolean |  | 列出注册表中全部可安装的智能体 |

示例：

```bash
foxos acp agent list --json
foxos acp agent list --available --json
```

### `foxos acp agent install`

从 ACP 官方注册表安装智能体（npm / 校验 sha256 的二进制 / uvx）

```text
foxos acp agent install AGENT
```

工具接口名：`acp_agent_install` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |

示例：

```bash
foxos acp agent install codex-acp
foxos acp agent install gemini
```

限制：

- 下载只来自注册表里的官方地址；二进制按注册表的 sha256 校验

### `foxos acp agent uninstall`

卸载用户安装的智能体

```text
foxos acp agent uninstall AGENT
```

工具接口名：`acp_agent_uninstall` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |

示例：

```bash
foxos acp agent uninstall codex-acp
```

### `foxos acp agent show`

查看一个智能体：版本、许可证、来源、登录方式、密钥

```text
foxos acp agent show AGENT
```

工具接口名：`acp_agent_show` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |

示例：

```bash
foxos acp agent show gemini --json
```

### `foxos acp agent probe`

真实启动智能体并握手：initialize，可选 session/new

```text
foxos acp agent probe AGENT [--session]
```

工具接口名：`acp_agent_probe` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `session` | `--session` | boolean |  | 握手后再建一个会话（session/new）；默认 True |

示例：

```bash
foxos acp agent probe codex-acp --json
```

### `foxos acp agent login`

用智能体自己的登录方式登录（ACP authenticate）

```text
foxos acp agent login AGENT --method METHOD
```

工具接口名：`acp_agent_login` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `method` | `--method` | string | 是 | 登录方式 ID（见 acp agent show） |

示例：

```bash
foxos acp agent login gemini --method oauth-personal
```

限制：

- 只有人可以登录智能体账号

### `foxos acp agent config`

查看或修改某个 ACP 智能体的设置：默认模型、模式、额外启动参数、非机密环境变量（机密用 acp key set）

```text
foxos acp agent config AGENT [--model MODEL] [--mode MODE] [--arg ARG] [--env ENV] [--clear]
```

工具接口名：`acp_agent_config` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `model` | `--model` | string |  | 默认模型 ID（会话开始时用 session/set_model 切换；空字符串清除） |
| `mode` | `--mode` | string |  | 默认模式 ID（session/set_mode；空字符串清除） |
| `arg` | `--arg` | array |  | 额外启动参数（可重复；替换原有的额外参数） |
| `env` | `--env` | object |  | 非机密环境变量 KEY=VALUE（可重复；VALUE 为空表示删除） |
| `clear` | `--clear` | boolean |  | 先清空全部设置 |

示例：

```bash
foxos acp agent config gemini --json
foxos acp agent config gemini --model gemini-2.5-pro
foxos acp agent config opencode --env OPENCODE_LOG=info
```

### `foxos acp agent update`

和官方注册表比较版本并更新 ACP 智能体（装到用户目录，系统预装的也不需要 root）

```text
foxos acp agent update [AGENT] [--all] [--check] [--accept-license]
```

工具接口名：`acp_agent_update` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string |  | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `all` | `--all` | boolean |  | 检查全部已安装的智能体 |
| `check` | `--check` | boolean |  | 只检查，不安装 |
| `accept_license` | `--accept-license` | boolean |  | 确认不可再分发的许可证（例如专有智能体） |

示例：

```bash
foxos acp agent update --all --check --json
foxos acp agent update gemini
```

### `foxos acp key set`

保存智能体的 API 密钥到本地密钥库（从标准输入读取，不写日志）

```text
foxos acp key set AGENT ENV_NAME --value VALUE
```

工具接口名：`acp_key_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `name` | `ENV_NAME` | string | 是 | 环境变量名（如 OPENAI_API_KEY） |
| `value` | `--value` | string | 是 | 密钥值（建议用 --value-stdin） |

示例：

```bash
printf %s "$KEY" | foxos acp key set codex-acp OPENAI_API_KEY --value-stdin
```

限制：

- 只有人可以管理智能体密钥
- 密钥只存本地密钥库（0600），不写审计日志

### `foxos acp key list`

列出已保存的智能体密钥（只显示末 4 位）

```text
foxos acp key list [--acp-agent AGENT]
```

工具接口名：`acp_key_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `--acp-agent` | string |  | 智能体 ID（如 codex-acp、gemini、claude-acp） |

示例：

```bash
foxos acp key list --json
```

### `foxos acp key remove`

删除一个智能体密钥

```text
foxos acp key remove AGENT ENV_NAME
```

工具接口名：`acp_key_remove` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `agent` | `AGENT` | string | 是 | 智能体 ID（如 codex-acp、gemini、claude-acp） |
| `name` | `ENV_NAME` | string | 是 | 环境变量名（如 OPENAI_API_KEY） |

示例：

```bash
foxos acp key remove codex-acp OPENAI_API_KEY
```

## bot — 智能体：主智能体与其它智能体、对话、委托、技能、记忆、审批、例程

一个主智能体（狐狸）加任意多个智能体。每个智能体有名字、头像、职责与指令、后端（ACP 代码智能体或 OpenAI 兼容模型）、自己的对话与记忆、工作范围、技能（pstack）、连接器、可控制的机器、审批规则、委托规则、例程与频道。设置项与 OpenBot 逐项对应。主智能体可以把任务委托给其它智能体（bot_task_delegate），结果回到主对话。

### `foxos bot profile list`

列出智能体

```text
foxos bot profile list [--hidden]
```

工具接口名：`bot_profile_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `hidden` | `--hidden` | boolean |  | 包括隐藏的智能体 |

示例：

```bash
foxos bot profile list --json
```

### `foxos bot profile show`

查看一个智能体

```text
foxos bot profile show BOT
```

工具接口名：`bot_profile_show` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot profile show fox --json
```

### `foxos bot profile create`

新建智能体

```text
foxos bot profile create NAME [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN] [--id ID]
```

工具接口名：`bot_profile_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 名字 |
| `title` | `--title` | string |  | 头衔（一行） |
| `role` | `--role` | string |  | 职责说明（它是做什么的） |
| `instructions` | `--instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | `--icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | `--color` | string |  | 头像颜色 #RRGGBB |
| `image` | `--image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | `--acp-agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | `--base-url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | `--model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | `--api-key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | `--scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | `--isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | `--visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户；可选：private / public |
| `pinned` | `--pinned` | boolean |  | 置顶 |
| `hidden` | `--hidden` | boolean |  | 从列表中隐藏 |
| `active` | `--active` | boolean |  | 是否启用 |
| `notifications` | `--notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | `--skills-mode` | string |  | 技能模式：all 全部 / selected 只用选中的；可选：all / selected |
| `skills` | `--skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | `--skills-off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | `--connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | `--machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | `--default-machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | `--approval-mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许；可选：ask / allow_reads / allow_all |
| `rules` | `--rule` | object |  | 审批规则：工具类型=allow\|ask\|deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | `--delegate-to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | `--max-depth` | integer |  | 委托最大深度 |
| `max_per_turn` | `--max-per-turn` | integer |  | 每轮最多委托几次 |
| `id` | `--id` | string |  | 指定 ID（小写字母数字与 -） |

示例：

```bash
foxos bot profile create Coder --title Coding --acp-agent codex-acp --icon code --color '#3B82F6' --isolated
```

限制：

- 这个操作只有人可以做

### `foxos bot profile update`

修改智能体资料（同 bot config set）

```text
foxos bot profile update BOT [--name NAME] [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN]
```

工具接口名：`bot_profile_update` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | `--name` | string |  | 名字 |
| `title` | `--title` | string |  | 头衔（一行） |
| `role` | `--role` | string |  | 职责说明（它是做什么的） |
| `instructions` | `--instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | `--icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | `--color` | string |  | 头像颜色 #RRGGBB |
| `image` | `--image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | `--acp-agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | `--base-url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | `--model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | `--api-key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | `--scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | `--isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | `--visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户；可选：private / public |
| `pinned` | `--pinned` | boolean |  | 置顶 |
| `hidden` | `--hidden` | boolean |  | 从列表中隐藏 |
| `active` | `--active` | boolean |  | 是否启用 |
| `notifications` | `--notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | `--skills-mode` | string |  | 技能模式：all 全部 / selected 只用选中的；可选：all / selected |
| `skills` | `--skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | `--skills-off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | `--connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | `--machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | `--default-machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | `--approval-mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许；可选：ask / allow_reads / allow_all |
| `rules` | `--rule` | object |  | 审批规则：工具类型=allow\|ask\|deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | `--delegate-to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | `--max-depth` | integer |  | 委托最大深度 |
| `max_per_turn` | `--max-per-turn` | integer |  | 每轮最多委托几次 |

示例：

```bash
foxos bot profile update coder --title Backend
```

限制：

- 这个操作只有人可以做

### `foxos bot profile delete`

删除智能体（主智能体不能删）

```text
foxos bot profile delete BOT
```

工具接口名：`bot_profile_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot profile delete coder
```

限制：

- 这个操作只有人可以做
- 主智能体不能删除或停用

### `foxos bot profile duplicate`

复制一个智能体的设置

```text
foxos bot profile duplicate BOT --name NAME
```

工具接口名：`bot_profile_duplicate` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | `--name` | string | 是 | 名字 |

示例：

```bash
foxos bot profile duplicate coder --name Coder2
```

### `foxos bot profile reset`

清空对话（默认也清空记忆）

```text
foxos bot profile reset BOT [--keep-memory]
```

工具接口名：`bot_profile_reset` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `keep_memory` | `--keep-memory` | boolean |  | 保留记忆 |

示例：

```bash
foxos bot profile reset coder
```

### `foxos bot config get`

查看一个智能体的全部设置

```text
foxos bot config get BOT
```

工具接口名：`bot_config_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot config get fox --json
```

### `foxos bot config set`

修改智能体设置（与 OpenBot 的 Bot 设置逐项对应）

```text
foxos bot config set BOT [--name NAME] [--title TITLE] [--role ROLE] [--instructions INSTRUCTIONS] [--icon ICON] [--color COLOR] [--image IMAGE] [--acp-agent AGENT] [--base-url BASE_URL] [--model MODEL] [--api-key API_KEY] [--scope SCOPE] [--isolated] [--visibility {private,public}] [--pinned] [--hidden] [--active] [--notifications] [--skills-mode {all,selected}] [--skills SKILLS] [--skills-off SKILLS_OFF] [--connectors CONNECTORS] [--machines MACHINES] [--default-machine DEFAULT_MACHINE] [--approval-mode {ask,allow_reads,allow_all}] [--rule RULES] [--delegate-to DELEGATE_TO] [--max-depth MAX_DEPTH] [--max-per-turn MAX_PER_TURN]
```

工具接口名：`bot_config_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | `--name` | string |  | 名字 |
| `title` | `--title` | string |  | 头衔（一行） |
| `role` | `--role` | string |  | 职责说明（它是做什么的） |
| `instructions` | `--instructions` | string |  | 指令（长文本，可用 --instructions-stdin） |
| `icon` | `--icon` | string |  | 头像字体图标名（Tabler，如 robot、code、search） |
| `color` | `--color` | string |  | 头像颜色 #RRGGBB |
| `image` | `--image` | string |  | 头像图片（工作空间内的 png/jpg/svg/webp） |
| `agent` | `--acp-agent` | string |  | 后端 ACP 智能体 ID（如 codex-acp、gemini、claude-acp、foxos-local） |
| `base_url` | `--base-url` | string |  | OpenAI 兼容端点（https://…/v1）；设置后后端改为模型 |
| `model` | `--model` | string |  | 模型名（模型后端）或给 ACP 智能体的模型偏好 |
| `api_key` | `--api-key` | string |  | 模型端点的 API 密钥（存本地密钥库；用 --api-key-stdin） |
| `scope` | `--scope` | string |  | 工作范围（工作空间内的目录） |
| `isolated` | `--isolated` | boolean |  | 隔离：只能操作自己的目录 bots/<id> |
| `visibility` | `--visibility` | string |  | 可见性：private 仅自己 / public 本机所有用户；可选：private / public |
| `pinned` | `--pinned` | boolean |  | 置顶 |
| `hidden` | `--hidden` | boolean |  | 从列表中隐藏 |
| `active` | `--active` | boolean |  | 是否启用 |
| `notifications` | `--notifications` | boolean |  | 完成时发桌面通知 |
| `skills_mode` | `--skills-mode` | string |  | 技能模式：all 全部 / selected 只用选中的；可选：all / selected |
| `skills` | `--skills` | array |  | 只启用这些技能（逗号分隔） |
| `skills_off` | `--skills-off` | array |  | 关闭这些技能（逗号分隔） |
| `connectors` | `--connectors` | array |  | 可用的连接器 ID（逗号分隔） |
| `machines` | `--machines` | array |  | 可以控制的机器（逗号分隔，local 是本机） |
| `default_machine` | `--default-machine` | string |  | 默认在哪台机器上操作 |
| `approval_mode` | `--approval-mode` | string |  | 审批方式：ask 每次询问 / allow_reads 读操作自动允许 / allow_all 全部允许；可选：ask / allow_reads / allow_all |
| `rules` | `--rule` | object |  | 审批规则：工具类型=allow\|ask\|deny（read、edit、delete、move、search、execute、fetch…；default 删除规则） |
| `delegate_to` | `--delegate-to` | array |  | 可以委托给哪些智能体（* 表示全部） |
| `max_depth` | `--max-depth` | integer |  | 委托最大深度 |
| `max_per_turn` | `--max-per-turn` | integer |  | 每轮最多委托几次 |

示例：

```bash
foxos bot config set coder --acp-agent claude-acp --skills tdd,architect --approval-mode allow_reads --rule execute=ask
foxos bot config set fox --machines local,vm1 --default-machine local --connectors exa
```

限制：

- 这个操作只有人可以做

### `foxos bot message send`

给智能体发消息并等待回答（@名字 委托，/技能 调用技能）

```text
foxos bot message send BOT TEXT [--attach ATTACHMENTS] [--approve {rules,allow,deny}]
```

工具接口名：`bot_message_send` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `text` | `TEXT` | string | 是 | 文字 |
| `attachments` | `--attach` | array |  | 附件（工作空间内的文件路径，可重复） |
| `approve` | `--approve` | string |  | 这一轮的审批：rules 按规则 / allow 全部允许 / deny 全部拒绝；可选：rules / allow / deny；默认 rules |

示例：

```bash
foxos bot message send fox '@coder write hello.py'
foxos bot message send coder '/tdd add tests for parse()'
```

### `foxos bot message list`

查看对话记录

```text
foxos bot message list BOT [--limit LIMIT]
```

工具接口名：`bot_message_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `limit` | `--limit` | integer |  | 最多返回多少条；默认 50 |

示例：

```bash
foxos bot message list fox --json
```

### `foxos bot task delegate`

把任务交给另一个智能体（任务/约束/期望结果），等它回报

```text
foxos bot task delegate TASK --to TO [--constraints CONSTRAINTS] [--expecting EXPECTING]
```

工具接口名：`bot_task_delegate` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `to` | `--to` | string | 是 | 交给哪个智能体 |
| `task` | `TASK` | string | 是 | 任务 |
| `constraints` | `--constraints` | string |  | 约束（不能做什么、范围） |
| `expecting` | `--expecting` | string |  | 期望得到什么结果 |

示例：

```bash
foxos bot task delegate --to coder 'fix tests/test_x.py' --expecting 'which files changed'
```

限制：

- 受对方智能体的委托规则、最大深度和每轮上限约束；被拒绝时返回 refused

### `foxos bot skill list`

列出技能与原则（工作空间、~/.agents/skills、pstack）

```text
foxos bot skill list [--bot BOT] [--kind {skill,principle,subagent}]
```

工具接口名：`bot_skill_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `--bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | `--kind` | string |  | 类型：skill 技能 / principle 原则 / subagent 子智能体；可选：skill / principle / subagent |

示例：

```bash
foxos bot skill list --json
foxos bot skill list --kind principle
```

### `foxos bot skill show`

查看一个技能的内容

```text
foxos bot skill show SKILL
```

工具接口名：`bot_skill_show` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `SKILL` | string | 是 | 技能名 |

示例：

```bash
foxos bot skill show architect
```

### `foxos bot skill run`

让智能体按某个技能完成任务

```text
foxos bot skill run BOT [TASK] --skill NAME
```

工具接口名：`bot_skill_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `name` | `--skill` | string | 是 | 技能名 |
| `task` | `TASK` | string |  | 任务；默认  |

示例：

```bash
foxos bot skill run fox --skill architect 'design the plugin interface'
```

### `foxos bot skill install`

把技能（含 pstack）安装到某个代码智能体的技能目录

```text
foxos bot skill install --harness {claude-code,codex,agents,gemini}
```

工具接口名：`bot_skill_install` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `harness` | `--harness` | string | 是 | 目标代码智能体；可选：claude-code / codex / agents / gemini |

示例：

```bash
foxos bot skill install --harness claude-code
```

### `foxos bot skill models`

写 pstack 的角色配置（pstack-models.md），角色指向狐狸OS 智能体

```text
foxos bot skill models [ROLE=BOTS...]
```

工具接口名：`bot_skill_models` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `roles` | `ROLE=BOTS` | object |  | 角色=智能体列表，如 'arena runners=claude,codex' |

示例：

```bash
foxos bot skill models 'arena runners=claude,codex'
```

### `foxos bot memory list`

列出智能体的记忆

```text
foxos bot memory list BOT
```

工具接口名：`bot_memory_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot memory list fox
```

### `foxos bot memory add`

让智能体记住一件事

```text
foxos bot memory add BOT TEXT
```

工具接口名：`bot_memory_add` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `text` | `TEXT` | string | 是 | 文字 |

示例：

```bash
foxos bot memory add fox 'weekly report goes to #team'
```

### `foxos bot memory forget`

删除一条记忆

```text
foxos bot memory forget BOT MEMORY_ID
```

工具接口名：`bot_memory_forget` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `memory` | `MEMORY_ID` | string | 是 | 记忆 ID |

示例：

```bash
foxos bot memory forget fox mem-1a2b3c4d
```

### `foxos bot approval list`

列出待审批的请求

```text
foxos bot approval list
```

工具接口名：`bot_approval_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos bot approval list --json
```

### `foxos bot approval answer`

回答一个待审批请求（允许/拒绝）

```text
foxos bot approval answer REQUEST [--option OPTION] [--deny]
```

工具接口名：`bot_approval_answer` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `request` | `REQUEST` | string | 是 | 审批请求 ID |
| `option` | `--option` | string |  | 选项 ID（如 allow、allow_always、reject） |
| `deny` | `--deny` | boolean |  | 拒绝 |

示例：

```bash
foxos bot approval answer apr-0123456789 --option allow
```

限制：

- 这个操作只有人可以做

### `foxos bot routine list`

列出例程

```text
foxos bot routine list [--bot BOT]
```

工具接口名：`bot_routine_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `--bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot routine list --json
```

### `foxos bot routine create`

新建例程：每隔若干分钟让智能体做一件事

```text
foxos bot routine create BOT --instruction INSTRUCTION --every-minutes EVERY_MINUTES [--title TITLE]
```

工具接口名：`bot_routine_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `instruction` | `--instruction` | string | 是 | 例程每次要做的事 |
| `every_minutes` | `--every-minutes` | integer | 是 | 间隔分钟（至少 15） |
| `title` | `--title` | string |  | 头衔（一行） |

示例：

```bash
foxos bot routine create fox --instruction 'tidy the inbox' --every-minutes 60
```

限制：

- 最短间隔 15 分钟，最多 20 个启用的例程

### `foxos bot routine update`

启用、停用或修改例程间隔

```text
foxos bot routine update ROUTINE [--enabled] [--every-minutes EVERY_MINUTES]
```

工具接口名：`bot_routine_update` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `routine` | `ROUTINE` | string | 是 | 例程 ID |
| `enabled` | `--enabled` | boolean |  | 启用 |
| `every_minutes` | `--every-minutes` | integer |  | 间隔分钟（至少 15） |

示例：

```bash
foxos bot routine update rt-1a2b3c4d --no-enabled
```

### `foxos bot routine delete`

删除例程

```text
foxos bot routine delete ROUTINE
```

工具接口名：`bot_routine_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `routine` | `ROUTINE` | string | 是 | 例程 ID |

示例：

```bash
foxos bot routine delete rt-1a2b3c4d
```

### `foxos bot routine run`

运行到期的例程（或立即运行指定例程）

```text
foxos bot routine run [--routine ROUTINE]
```

工具接口名：`bot_routine_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `routine` | `--routine` | string |  | 例程 ID |

示例：

```bash
foxos bot routine run
foxos bot routine run --routine rt-1a2b3c4d
```

### `foxos bot channel set`

设置频道：Telegram 机器人或 Webhook

```text
foxos bot channel set BOT --kind {telegram,webhook} [--token TOKEN] [--chat CHAT]
```

工具接口名：`bot_channel_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | `--kind` | string | 是 | 频道类型；可选：telegram / webhook |
| `token` | `--token` | string |  | Telegram 机器人令牌（用 --token-stdin） |
| `chat` | `--chat` | string |  | 只回答这个 Telegram 会话 ID |

示例：

```bash
printf %s "$TG" | foxos bot channel set fox --kind telegram --token-stdin
foxos bot channel set fox --kind webhook
```

限制：

- 这个操作只有人可以做

### `foxos bot channel remove`

移除一个频道

```text
foxos bot channel remove BOT --kind {telegram,webhook}
```

工具接口名：`bot_channel_remove` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `BOT` | string | 是 | 智能体 ID 或名字（main 表示主智能体） |
| `kind` | `--kind` | string | 是 | 频道类型；可选：telegram / webhook |

示例：

```bash
foxos bot channel remove fox --kind telegram
```

### `foxos bot channel poll`

收取频道新消息并让智能体回答（Telegram）

```text
foxos bot channel poll [--bot BOT]
```

工具接口名：`bot_channel_poll` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `bot` | `--bot` | string |  | 智能体 ID 或名字（main 表示主智能体） |

示例：

```bash
foxos bot channel poll
```

## browser — 浏览器（Google Chrome）

启动 Chrome、打开网页；人开启本机 CDP 后可列标签页、跳转、执行脚本、截图

### `foxos browser status`

Chrome 是否安装、版本、CDP 开关与端口

```text
foxos browser status
```

工具接口名：`browser_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos browser status --json
```

### `foxos browser cdp`

开启 / 关闭 Chrome 远程调试（CDP，只听 127.0.0.1）

```text
foxos browser cdp on|off [--port PORT]
```

工具接口名：`browser_cdp` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `state` | `on|off` | string | 是 | on 或 off |
| `port` | `--port` | integer |  | 调试端口（默认 9222） |

示例：

```bash
foxos browser cdp on
foxos browser cdp off
```

限制：

- 只有人可以开启；智能体只能关闭
- 只绑定 127.0.0.1；开启后使用单独的智能体配置文件 ~/.config/foxos/chrome-agent

### `foxos browser open`

在 Chrome 打开网址（CDP 运行时新开标签页，否则启动 Chrome）

```text
foxos browser open URL [--wait WAIT]
```

工具接口名：`browser_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `url` | `URL` | string | 是 | 网址 |
| `wait` | `--wait` | number |  | 启动后等待 CDP 就绪的秒数；默认 15.0 |

示例：

```bash
foxos browser open https://github.com/gatesenman/foxos
```

### `foxos browser tabs`

列出标签页（需要 CDP）

```text
foxos browser tabs
```

工具接口名：`browser_tabs` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos browser tabs --json
```

### `foxos browser navigate`

让标签页跳转并等待加载完成（需要 CDP）

```text
foxos browser navigate URL [--tab TAB]
```

工具接口名：`browser_navigate` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `url` | `URL` | string | 是 | 网址 |
| `tab` | `--tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |

示例：

```bash
foxos browser navigate https://example.com --tab 3F2A
```

### `foxos browser eval`

在标签页里执行 JavaScript 并返回值（需要 CDP）

```text
foxos browser eval JS [--tab TAB]
```

工具接口名：`browser_eval` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `expression` | `JS` | string | 是 | JavaScript 表达式 |
| `tab` | `--tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |

示例：

```bash
foxos browser eval 'document.title'
```

### `foxos browser screenshot`

截取标签页内容为 PNG（需要 CDP）

```text
foxos browser screenshot [--path PATH] [--tab TAB]
```

工具接口名：`browser_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `--path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/）；工作空间路径（write） |
| `tab` | `--tab` | string |  | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |

示例：

```bash
foxos browser screenshot --path shots/page.png
```

### `foxos browser close`

关闭标签页（需要 CDP）

```text
foxos browser close TAB
```

工具接口名：`browser_close` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `tab` | `TAB` | string | 是 | 标签页 id（foxos browser tabs 里的 id，可写前缀；默认第一个） |

示例：

```bash
foxos browser close 3F2A
```

## connector — 连接器：MCP 服务器与 OAuth 应用

连接器：远程 MCP 服务器（HTTP / SSE）、本地 MCP 命令、OAuth 应用（PKCE、动态注册）。目录与 OpenBot 一致（Parallel、Exa、Firecrawl、Notion、Google Drive），另加 GitHub 和自定义地址。令牌存本地密钥库；每个智能体单独开启；写操作按智能体的审批规则询问。

### `foxos connector catalog`

连接器目录

```text
foxos connector catalog
```

工具接口名：`connector_catalog` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos connector catalog --json
```

### `foxos connector list`

已添加的连接器

```text
foxos connector list
```

工具接口名：`connector_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos connector list --json
```

### `foxos connector add`

添加连接器（目录里的 key，或自定义 URL / 命令）

```text
foxos connector add [--key KEY] [--id ID] [--title TITLE] [--url URL] [--arg COMMAND] [--auth {none,bearer,oauth}] [--header HEADER]
```

工具接口名：`connector_add` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `--key` | string |  | 目录里的 key（见 connector catalog） |
| `id` | `--id` | string |  | 连接器 ID |
| `title` | `--title` | string |  | 显示名 |
| `url` | `--url` | string |  | MCP 服务器地址（https） |
| `command` | `--arg` | array |  | 本地 MCP 命令及参数（可重复 --arg） |
| `auth` | `--auth` | string |  | 认证方式；可选：none / bearer / oauth |
| `header` | `--header` | string |  | 令牌放在哪个请求头（默认 Authorization: Bearer） |

示例：

```bash
foxos connector add --key exa
foxos connector add --id mine --url https://mcp.example.com/mcp --auth bearer
```

限制：

- 这个操作只有人可以做

### `foxos connector remove`

移除连接器

```text
foxos connector remove CONNECTOR
```

工具接口名：`connector_remove` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `connector` | `CONNECTOR` | string | 是 | 连接器 ID |

示例：

```bash
foxos connector remove exa
```

### `foxos connector connect`

连接：API 令牌或 OAuth 登录

```text
foxos connector connect CONNECTOR [--token TOKEN] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET] [--no-browser]
```

工具接口名：`connector_connect` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `connector` | `CONNECTOR` | string | 是 | 连接器 ID |
| `token` | `--token` | string |  | API 令牌（用 --token-stdin） |
| `client_id` | `--client-id` | string |  | OAuth 客户端 ID（不支持动态注册的服务需要） |
| `client_secret` | `--client-secret` | string |  | OAuth 客户端密钥 |
| `no_browser` | `--no-browser` | boolean |  | 不自动打开浏览器，只打印授权地址 |

示例：

```bash
printf %s "$KEY" | foxos connector connect exa-authenticated --token-stdin
foxos connector connect notion
```

限制：

- 这个操作只有人可以做
- 令牌只存本地密钥库，不写日志

### `foxos connector disconnect`

断开连接并删除令牌

```text
foxos connector disconnect CONNECTOR
```

工具接口名：`connector_disconnect` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `connector` | `CONNECTOR` | string | 是 | 连接器 ID |

示例：

```bash
foxos connector disconnect notion
```

### `foxos connector tools`

连接器提供的工具

```text
foxos connector tools CONNECTOR [--refresh]
```

工具接口名：`connector_tools` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `connector` | `CONNECTOR` | string | 是 | 连接器 ID |
| `refresh` | `--refresh` | boolean |  | 重新向服务器获取工具列表 |

示例：

```bash
foxos connector tools exa --refresh
```

### `foxos connector tool call`

调用连接器的一个工具

```text
foxos connector tool call CONNECTOR --tool TOOL [--arguments ARGUMENTS]
```

工具接口名：`connector_tool_call` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `connector` | `CONNECTOR` | string | 是 | 连接器 ID |
| `tool` | `--tool` | string | 是 | 工具名 |
| `arguments` | `--arguments` | object |  | 工具参数（JSON 对象） |

示例：

```bash
foxos connector tool call exa --tool web_search_exa --arguments '{"query":"ACP"}'
```

限制：

- 智能体调用时：连接器必须对该智能体开启；非只读工具按审批规则询问

## desktop — 真实桌面会话

在 XFCE 管理的真实窗口上列出、聚焦、移动，以及键入、点击和人工接管。不是 Electron 里画的假窗口。

### `foxos desktop status`

显示当前图形会话与人工接管状态

```text
foxos desktop status
```

工具接口名：`desktop_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos desktop status --json
```

### `foxos desktop windows`

列出合成器管理的真实窗口

```text
foxos desktop windows
```

工具接口名：`desktop_windows` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos desktop windows --json
```

### `foxos desktop focus`

聚焦一个窗口

```text
foxos desktop focus WINDOW
```

工具接口名：`desktop_focus` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |

示例：

```bash
foxos desktop focus 4278190080
```

### `foxos desktop move`

移动一个窗口

```text
foxos desktop move WINDOW --x X --y Y
```

工具接口名：`desktop_move` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | `--x` | integer | 是 | X 坐标（像素） |
| `y` | `--y` | integer | 是 | Y 坐标（像素） |

示例：

```bash
foxos desktop move 4278190080 --x 100 --y 80
```

### `foxos desktop resize`

调整一个窗口的大小

```text
foxos desktop resize WINDOW --width WIDTH --height HEIGHT
```

工具接口名：`desktop_resize` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | `--width` | integer | 是 | 宽度（像素） |
| `height` | `--height` | integer | 是 | 高度（像素） |

示例：

```bash
foxos desktop resize 4278190080 --width 800 --height 600
```

### `foxos desktop close`

关闭一个窗口

```text
foxos desktop close WINDOW
```

工具接口名：`desktop_close` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |

示例：

```bash
foxos desktop close 4278190080
```

### `foxos desktop launch`

启动一个应用或命令

```text
foxos desktop launch CMD...
```

工具接口名：`desktop_launch` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `command` | `CMD` | array | 是 | 要启动的命令和参数 |

示例：

```bash
foxos desktop launch chrome
foxos desktop launch -- xfce4-terminal
foxos desktop launch -- xfce4-terminal -T notes
```

### `foxos desktop type`

向当前聚焦的窗口键入文本

```text
foxos desktop type TEXT
```

工具接口名：`desktop_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要键入的文本 |

示例：

```bash
foxos desktop type 'hello'
```

### `foxos desktop key`

发送按键或组合键

```text
foxos desktop key KEYS
```

工具接口名：`desktop_key` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `keys` | `KEYS` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |

示例：

```bash
foxos desktop key Return
foxos desktop key ctrl+c
```

### `foxos desktop click`

在屏幕坐标处点击

```text
foxos desktop click --x X --y Y [--button BUTTON]
```

工具接口名：`desktop_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `x` | `--x` | integer | 是 | X 坐标（像素） |
| `y` | `--y` | integer | 是 | Y 坐标（像素） |
| `button` | `--button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键；默认 1 |

示例：

```bash
foxos desktop click --x 400 --y 300
```

### `foxos desktop screenshot`

截取当前会话画面

```text
foxos desktop screenshot [--path PATH]
```

工具接口名：`desktop_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `--path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/）；工作空间路径（write） |

示例：

```bash
foxos desktop screenshot --path shots/desk.png
```

### `foxos desktop activity`

现在是谁在操作：每个智能体最近的命令与桌面占用

```text
foxos desktop activity
```

工具接口名：`desktop_activity` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos desktop activity --json
```

### `foxos desktop release`

释放桌面输入占用（人用）

```text
foxos desktop release
```

工具接口名：`desktop_release` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos desktop release
```

### `foxos desktop takeover`

人工接管：暂停智能体的写操作

```text
foxos desktop takeover [--reason REASON] [--only IDENTITY]
```

工具接口名：`desktop_takeover` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `reason` | `--reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | `--only` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |

示例：

```bash
foxos desktop takeover --reason 我来改
```

限制：

- 只有 human 身份可以执行

### `foxos desktop resume`

结束人工接管，恢复智能体写操作

```text
foxos desktop resume [--only IDENTITY]
```

工具接口名：`desktop_resume` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `targets` | `--only` | array |  | 只恢复这些身份；不填则全部恢复 |

示例：

```bash
foxos desktop resume
```

限制：

- 只有 human 身份可以执行

## session — 真实桌面会话

在 XFCE 管理的真实窗口上列出、聚焦、移动，以及键入、点击和人工接管。不是 Electron 里画的假窗口。

### `foxos session status`

显示当前图形会话与人工接管状态

```text
foxos session status
```

工具接口名：`session_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos session status --json
```

### `foxos session windows`

列出合成器管理的真实窗口

```text
foxos session windows
```

工具接口名：`session_windows` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos session windows --json
```

### `foxos session focus`

聚焦一个窗口

```text
foxos session focus WINDOW
```

工具接口名：`session_focus` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |

示例：

```bash
foxos session focus 4278190080
```

### `foxos session move`

移动一个窗口

```text
foxos session move WINDOW --x X --y Y
```

工具接口名：`session_move` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | `--x` | integer | 是 | X 坐标（像素） |
| `y` | `--y` | integer | 是 | Y 坐标（像素） |

示例：

```bash
foxos session move 4278190080 --x 100 --y 80
```

### `foxos session resize`

调整一个窗口的大小

```text
foxos session resize WINDOW --width WIDTH --height HEIGHT
```

工具接口名：`session_resize` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | `--width` | integer | 是 | 宽度（像素） |
| `height` | `--height` | integer | 是 | 高度（像素） |

示例：

```bash
foxos session resize 4278190080 --width 800 --height 600
```

### `foxos session close`

关闭一个窗口

```text
foxos session close WINDOW
```

工具接口名：`session_close` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `window` | `WINDOW` | string | 是 | 窗口编号（见 windows 命令） |

示例：

```bash
foxos session close 4278190080
```

### `foxos session launch`

启动一个应用或命令

```text
foxos session launch CMD...
```

工具接口名：`session_launch` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `command` | `CMD` | array | 是 | 要启动的命令和参数 |

示例：

```bash
foxos session launch chrome
foxos session launch -- xfce4-terminal
foxos session launch -- xfce4-terminal -T notes
```

### `foxos session type`

向当前聚焦的窗口键入文本

```text
foxos session type TEXT
```

工具接口名：`session_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要键入的文本 |

示例：

```bash
foxos session type 'hello'
```

### `foxos session key`

发送按键或组合键

```text
foxos session key KEYS
```

工具接口名：`session_key` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `keys` | `KEYS` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |

示例：

```bash
foxos session key Return
foxos session key ctrl+c
```

### `foxos session click`

在屏幕坐标处点击

```text
foxos session click --x X --y Y [--button BUTTON]
```

工具接口名：`session_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `x` | `--x` | integer | 是 | X 坐标（像素） |
| `y` | `--y` | integer | 是 | Y 坐标（像素） |
| `button` | `--button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键；默认 1 |

示例：

```bash
foxos session click --x 400 --y 300
```

### `foxos session screenshot`

截取当前会话画面

```text
foxos session screenshot [--path PATH]
```

工具接口名：`session_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `--path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/）；工作空间路径（write） |

示例：

```bash
foxos session screenshot --path shots/desk.png
```

### `foxos session activity`

现在是谁在操作：每个智能体最近的命令与桌面占用

```text
foxos session activity
```

工具接口名：`session_activity` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos session activity --json
```

### `foxos session release`

释放桌面输入占用（人用）

```text
foxos session release
```

工具接口名：`session_release` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos session release
```

### `foxos session takeover`

人工接管：暂停智能体的写操作

```text
foxos session takeover [--reason REASON] [--only IDENTITY]
```

工具接口名：`session_takeover` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `reason` | `--reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | `--only` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |

示例：

```bash
foxos session takeover --reason 我来改
```

限制：

- 只有 human 身份可以执行

### `foxos session resume`

结束人工接管，恢复智能体写操作

```text
foxos session resume [--only IDENTITY]
```

工具接口名：`session_resume` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `targets` | `--only` | array |  | 只恢复这些身份；不填则全部恢复 |

示例：

```bash
foxos session resume
```

限制：

- 只有 human 身份可以执行

## docs — 文档：读写标准 .docx（段落、标题、列表、表格），替换文本与导出

基于 python-docx 读写 Word 2007+ (.docx)。样式名使用 Word 内置英文样式名，如 Heading 1、List Bullet。

限制：

- 只读写 .docx；.doc / .odt 输入暂不支持
- 图片、页眉页脚、批注暂不可编辑
- 替换在段落内进行，跨段落的文本不会匹配

### `foxos docs create`

新建一个 .docx 文档

```text
foxos docs create FILE [--title TITLE] [--force]
```

工具接口名：`docs_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `title` | `--title` | string |  | 文档标题（写成 Title 样式的第一段，并写入文档属性） |
| `force` | `--force / -f` | boolean |  | 已存在时覆盖 |

示例：

```bash
foxos docs create report.docx --title '2026 年销售分析'
```

### `foxos docs read`

读取文档段落（含样式名）、表格与字数统计

```text
foxos docs read FILE
```

工具接口名：`docs_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（read） |

示例：

```bash
foxos docs read report.docx --json
```

### `foxos docs append`

在文档末尾追加段落、标题或表格

```text
foxos docs append FILE [TEXT...] [--style STYLE] [--heading HEADING] [--table TABLE]
```

工具接口名：`docs_append` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `text` | `TEXT` | array |  | 要追加的段落，每个参数一段 |
| `style` | `--style` | string |  | 段落样式（Word 内置英文名），如 List Bullet、Quote |
| `heading` | `--heading` | integer |  | 作为标题追加：0=Title，1–9=Heading 1–9 |
| `table` | `--table` | array |  | 追加表格：二维数组；CLI 中用 --table-json |

示例：

```bash
foxos docs append report.docx '一、总体情况' --heading 1
foxos docs append report.docx '全年销售额 2013 万元。' '同比增长 12%。'
foxos docs append report.docx '要点一' '要点二' --style 'List Bullet'
foxos docs append report.docx --table-json '[["月份","销售额"],["1月",120]]'
```

### `foxos docs replace`

查找并替换文本（正文与表格）

```text
foxos docs replace FILE --find FIND --replace REPLACE
```

工具接口名：`docs_replace` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `find` | `--find` | string | 是 | 要查找的文本 |
| `replace` | `--replace` | string | 是 | 替换为 |

示例：

```bash
foxos docs replace report.docx --find 2025 --replace 2026
```

### `foxos docs export`

导出为 pdf / odt / html / txt / md（由扩展名决定）

```text
foxos docs export FILE OUTPUT [--force]
```

工具接口名：`docs_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 输出已存在时覆盖 |

示例：

```bash
foxos docs export report.docx report.pdf
foxos docs export report.docx report.md
```

限制：

- pdf / odt / html 需要 LibreOffice

## env — 狐狸OS 环境

自研隔离环境：每个环境有自己的根文件系统、进程、主机名和资源限制；工作空间按规则挂载到 /workspace。

限制：

- Linux 后端无特权运行（用户命名空间）；cgroup 不可委派时用 rlimit 限制
- Windows 使用系统自带 WSL2；macOS 使用 Virtualization.framework

### `foxos env images`

列出可用镜像（官方发行版 rootfs）与本地镜像

```text
foxos env images
```

工具接口名：`env_images` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos env images --json
```

### `foxos env pull`

下载镜像并校验 sha256（目录 ID、https 地址或 .foxenv 文件）

```text
foxos env pull IMAGE [--sha256 SHA256]
```

工具接口名：`env_pull` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `image` | `IMAGE` | string | 是 | 镜像 |
| `sha256` | `--sha256` | string |  | 期望的 sha256（自定义地址时建议提供） |

示例：

```bash
foxos env pull alpine-3.20
foxos env pull ubuntu-24.04
```

### `foxos env run`

没有镜像就拉取，然后创建并启动（用法靠近 docker run）；可附上来宾桌面

```text
foxos env run NAME [--image IMAGE] [--iso ISO] [--provider PROVIDER] [--network {user,host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--desktop-attach] [--no-start]
```

工具接口名：`env_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `image` | `--image` | string |  | 镜像 ID |
| `iso` | `--iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `provider` | `--provider` | string |  | 指定提供者 |
| `network` | `--network` | string |  | 网络：user 为用户态转发（来宾 5900 映射到宿主），none 断开，host 仅用于命名空间环境；可选：user / host / none；默认 user |
| `workspace_mode` | `--workspace-mode` | string |  | 工作空间挂载方式；可选：rw / ro / none；默认 rw |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限（MB） |
| `cpus` | `--cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | `--pids` | integer |  | 进程数上限 |
| `desktop_attach` | `--desktop-attach` | boolean |  | 启动后附上来宾桌面 |
| `no_start` | `--no-start` | boolean |  | 只创建，不启动 |

示例：

```bash
foxos env run dev --image alpine-3.20
foxos env run live --provider linux-kvm --iso FoxOS-0.3.0-amd64.iso --desktop-attach
```

### `foxos env desktop-attach`

把完整虚拟机的来宾桌面作为显示通道打开（wayvnc）

```text
foxos env desktop-attach NAME
```

工具接口名：`env_desktop-attach` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env desktop-attach live --json
```

### `foxos env create`

创建环境

```text
foxos env create NAME [--image IMAGE] [--network {host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS]
```

工具接口名：`env_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `image` | `--image` | string |  | 镜像 ID；默认 alpine-3.20 |
| `network` | `--network` | string |  | 网络：host（共享宿主网络）或 none（只有回环）；可选：host / none；默认 host |
| `workspace_mode` | `--workspace-mode` | string |  | 工作空间挂载方式；可选：rw / ro / none；默认 rw |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限（MB） |
| `cpus` | `--cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | `--pids` | integer |  | 进程数上限 |

示例：

```bash
foxos env create dev
foxos env create sandbox --image ubuntu-24.04 --network none --workspace-mode ro --memory-mb 1024
```

### `foxos env list`

列出环境及状态

```text
foxos env list
```

工具接口名：`env_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos env list --json
```

### `foxos env info`

环境详情（配置、快照、资源使用）

```text
foxos env info NAME
```

工具接口名：`env_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env info dev --json
```

### `foxos env start`

启动环境

```text
foxos env start NAME
```

工具接口名：`env_start` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env start dev
```

### `foxos env stop`

停止环境

```text
foxos env stop NAME [--timeout TIMEOUT]
```

工具接口名：`env_stop` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `timeout` | `--timeout` | number |  | 等待秒数，超时强制结束；默认 5.0 |

示例：

```bash
foxos env stop dev
```

### `foxos env restart`

重启环境

```text
foxos env restart NAME
```

工具接口名：`env_restart` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env restart dev
```

### `foxos env exec`

在环境中执行命令（默认工作目录 /workspace）

```text
foxos env exec NAME [CMD...] [--cwd CWD] [--timeout TIMEOUT]
```

工具接口名：`env_exec` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `command` | `CMD` | array |  | 命令及参数（放在 -- 之后） |
| `cwd` | `--cwd` | string |  | 环境内工作目录；默认 /workspace |
| `timeout` | `--timeout` | number |  | 超时秒数；默认 600 |

示例：

```bash
foxos env exec dev -- uname -a
foxos env exec dev -- sh -c 'apk add python3 && python3 -V' --json
```

### `foxos env shell`

进入环境的交互式 shell

```text
foxos env shell NAME
```

工具接口名：`env_shell` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env shell dev
```

### `foxos env clone`

克隆环境（复制可写层与设置）

```text
foxos env clone NAME NEW_NAME
```

工具接口名：`env_clone` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `new_name` | `NEW_NAME` | string | 是 | 新环境名 |

示例：

```bash
foxos env clone dev dev-copy
```

### `foxos env snapshot`

为停止的环境创建快照

```text
foxos env snapshot NAME [--label LABEL]
```

工具接口名：`env_snapshot` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `label` | `--label` | string |  | 说明 |

示例：

```bash
foxos env snapshot dev --label 装好依赖
```

### `foxos env restore`

恢复到快照

```text
foxos env restore NAME SNAPSHOT
```

工具接口名：`env_restore` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `snapshot` | `SNAPSHOT` | string | 是 | 快照 ID |

示例：

```bash
foxos env restore dev 20261110T213000
```

### `foxos env export`

导出为 .foxenv 镜像（tar + zstd + manifest + sha256）

```text
foxos env export NAME --out OUT
```

工具接口名：`env_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `out` | `--out` | string | 是 | 输出文件（工作空间内）；工作空间路径（write） |

示例：

```bash
foxos env export dev --out backups/dev.foxenv
```

### `foxos env import`

从 .foxenv 镜像导入为新环境

```text
foxos env import FILE --name NAME
```

工具接口名：`env_import` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | .foxenv 文件（工作空间内）；工作空间路径（read） |
| `name` | `--name` | string | 是 | 新环境名 |

示例：

```bash
foxos env import backups/dev.foxenv --name dev2
```

### `foxos env delete`

删除环境（不删除镜像与工作空间）

```text
foxos env delete NAME
```

工具接口名：`env_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env delete dev-copy
```

### `foxos env mount`

添加 / 移除宿主目录挂载

```text
foxos env mount NAME --source SOURCE --target TARGET [--readonly] [--remove]
```

工具接口名：`env_mount` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `source` | `--source` | string | 是 | 宿主路径 |
| `target` | `--target` | string | 是 | 环境内路径 |
| `readonly` | `--readonly` | boolean |  | 只读 |
| `remove` | `--remove` | boolean |  | 移除该挂载 |

示例：

```bash
foxos env mount dev --source ~/datasets --target /data --readonly
```

### `foxos env limits`

设置资源限制、网络与工作空间权限

```text
foxos env limits NAME [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--network {host,none}] [--workspace-mode {rw,ro,none}]
```

工具接口名：`env_limits` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限 MB（0 取消） |
| `cpus` | `--cpus` | number |  | CPU 上限（0 取消） |
| `pids` | `--pids` | integer |  | 进程数上限（0 取消） |
| `network` | `--network` | string |  | 网络；可选：host / none |
| `workspace_mode` | `--workspace-mode` | string |  | 工作空间挂载；可选：rw / ro / none |

示例：

```bash
foxos env limits dev --memory-mb 2048 --pids 512
foxos env limits dev --network none
```

### `foxos env stats`

资源使用（进程数、CPU 时间、内存、磁盘）

```text
foxos env stats [NAME]
```

工具接口名：`env_stats` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string |  | 环境名（缺省为全部） |

示例：

```bash
foxos env stats --json
```

### `foxos env logs`

环境日志

```text
foxos env logs NAME [--lines LINES]
```

工具接口名：`env_logs` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `lines` | `--lines / -n` | integer |  | 行数；默认 100 |

示例：

```bash
foxos env logs dev -n 50
```

### `foxos env action add`

添加自定义操作（支持 ${env} ${image} ${workspace} ${host_workspace} ${hostname} 变量）

```text
foxos env action add NAME ACTION --command COMMAND
```

工具接口名：`env_action_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `action` | `ACTION` | string | 是 | 操作名 |
| `command` | `--command` | string | 是 | 环境内执行的 shell 命令 |

示例：

```bash
foxos env action add dev test --command 'cd ${workspace} && make test'
```

### `foxos env action run`

运行自定义操作

```text
foxos env action run NAME ACTION
```

工具接口名：`env_action_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `action` | `ACTION` | string | 是 | 操作名 |

示例：

```bash
foxos env action run dev test --json
```

### `foxos env providers`

列出环境提供者（内置与第三方）及其能力、可用性

```text
foxos env providers
```

工具接口名：`env_providers` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos env providers --json
```

### `foxos env doctor`

检查本机虚拟化能力（WSL、Windows Sandbox、Hyper-V、用户命名空间…）并给出修复操作

```text
foxos env doctor [--provider PROVIDER]
```

工具接口名：`env_doctor` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `provider` | `--provider` | string |  | 只检查某个提供者 |

示例：

```bash
foxos env doctor --json
foxos env doctor --provider wsl2
```

### `foxos env fix`

执行 doctor 给出的修复操作（启用 WSL 等，需要管理员确认，可能需要重启）

```text
foxos env fix --provider PROVIDER --action ACTION
```

工具接口名：`env_fix` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `provider` | `--provider` | string | 是 | 提供者 |
| `action` | `--action` | string | 是 | 修复操作 ID（见 doctor 输出） |

示例：

```bash
foxos env fix --provider wsl2 --action enable-wsl
```

### `foxos env catalog`

可一键安装的系统目录（WSL 发行版、LXC/官方根文件系统、Windows Sandbox、Hyper-V、macOS）

```text
foxos env catalog [--guest {linux,windows,macos,any}] [--provider PROVIDER] [--available]
```

工具接口名：`env_catalog` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `guest` | `--guest` | string |  | 来宾系统；可选：linux / windows / macos / any |
| `provider` | `--provider` | string |  | 只看某个提供者 |
| `available` | `--available` | boolean |  | 只显示本机可安装的 |

示例：

```bash
foxos env catalog --json
foxos env catalog --guest windows
```

### `foxos env install`

从目录一键安装一个系统为新环境（下载、校验 sha256、导入）

```text
foxos env install ENTRY NAME [--provider PROVIDER] [--url URL] [--sha256 SHA256] [--iso ISO] [--location LOCATION] [--memory-mb MEMORY_MB] [--cpus CPUS] [--disk-gb DISK_GB] [--dry-run]
```

工具接口名：`env_install` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `entry` | `ENTRY` | string | 是 | 目录条目 ID（foxos env catalog） |
| `name` | `NAME` | string | 是 | 环境名 |
| `provider` | `--provider` | string |  | 指定提供者 |
| `url` | `--url` | string |  | 自定义根文件系统地址（custom-rootfs） |
| `sha256` | `--sha256` | string |  | 自定义来源的 sha256 |
| `iso` | `--iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `location` | `--location` | string |  | 安装位置（Windows 目录） |
| `memory_mb` | `--memory-mb` | integer |  | 内存 MB（Hyper-V / Sandbox） |
| `cpus` | `--cpus` | integer |  | CPU 数（Hyper-V） |
| `disk_gb` | `--disk-gb` | integer |  | 磁盘 GB（Hyper-V） |
| `dry_run` | `--dry-run` | boolean |  | 只输出安装计划，不执行 |

示例：

```bash
foxos env install wsl-ubuntu-24.04 ubuntu
foxos env install alpine tiny --dry-run --json
foxos env install hyperv-windows-11-eval win11 --iso D:\iso\win11.iso
```

### `foxos env progress`

查看安装进度

```text
foxos env progress NAME
```

工具接口名：`env_progress` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env progress ubuntu --json
```

## everything — Everything 应用

上游 HeyPuter/everything 的 51 个应用：从上游源码在本机构建安装，在狐狸OS 中本地运行（不连接 puter.com）。

限制：

- AGPL-3.0 应用作为独立组件在安装时从上游获取，狐狸OS 不分发其源码或修改版

### `foxos everything list`

列出 51 个 Everything 应用（分组、许可证、安装状态、操作数）

```text
foxos everything list [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--installed]
```

工具接口名：`everything_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `group` | `--group` | string |  | 只看某个分组；可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `installed_only` | `--installed` | boolean |  | 只列出已安装的 |

示例：

```bash
foxos everything list
foxos everything list --group office --json
```

### `foxos everything info`

查看一个应用的详情、许可证与可用命令

```text
foxos everything info APP
```

工具接口名：`everything_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |

示例：

```bash
foxos everything info tasks --json
```

### `foxos everything install`

从上游源码在本机构建并安装应用（固定提交，含许可证声明）

```text
foxos everything install [APP...] [--all] [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--source SOURCE] [--force]
```

工具接口名：`everything_install` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `apps` | `APP` | array |  | 应用 ID |
| `all` | `--all` | boolean |  | 安装全部 51 个 |
| `group` | `--group` | string |  | 安装整个分组；可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `source` | `--source` | string |  | 使用本地上游仓库目录（离线 / 镜像），默认从 GitHub 获取 |
| `force` | `--force / -f` | boolean |  | 已安装也重新构建 |

示例：

```bash
foxos everything install tasks chess
foxos everything install --group games
foxos everything install --all
```

限制：

- 需要 git、Node.js 22.12+ 与 npm；每个应用构建约 2–20 秒（不含下载）

### `foxos everything commands`

列出一个应用的全部命令（语义操作 + 通用界面命令）及参数 Schema

```text
foxos everything commands APP
```

工具接口名：`everything_commands` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |

示例：

```bash
foxos everything commands tasks --json
```

### `foxos everything run`

执行一个应用的任意命令（与 foxos <app> <资源> <动词> 相同；权限、审计、写锁按被执行的命令计）

```text
foxos everything run APP COMMAND [--args ARGS]
```

工具接口名：`everything_run` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |
| `command` | `COMMAND` | string | 是 | 命令，如 "task create" 或 "ui snapshot" |
| `args` | `--args` | object |  | 命令参数（JSON 对象） |

示例：

```bash
foxos everything run tasks "add-task set" --args '{"value": "买牛奶", "submit": true}' --json
```

### `foxos everything icons`

给已安装的应用补上上游自带的程序图标（不重新构建）

```text
foxos everything icons [--source SOURCE]
```

工具接口名：`everything_icons` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `source` | `--source` | string |  | 本地上游仓库路径（缺省从 GitHub 获取固定提交） |

示例：

```bash
foxos everything icons --json
```

### `foxos everything uninstall`

卸载应用（保留工作空间中的数据）

```text
foxos everything uninstall APP
```

工具接口名：`everything_uninstall` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |

示例：

```bash
foxos everything uninstall chess
```

## machine — 多台狐狸OS：配对、授权、远程执行

一个智能体可以控制多台狐狸OS，多个智能体也可以共用一台。被控端运行 foxos machine serve（HTTPS，自签证书，控制端固定证书指纹），用一次性配对码换取令牌；每个智能体在每台机器上的权限单独授予，默认全部拒绝；被控端的审计日志写明是哪台控制端的哪个智能体。

### `foxos machine list`

列出机器（本机与已配对的机器）

```text
foxos machine list [--check]
```

工具接口名：`machine_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `check` | `--check` | boolean |  | 逐台检查在线状态 |

示例：

```bash
foxos machine list --check --json
```

### `foxos machine pair`

与另一台狐狸OS 配对

```text
foxos machine pair --name NAME --url URL --code CODE [--fingerprint FINGERPRINT] [--client CLIENT]
```

工具接口名：`machine_pair` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `--name` | string | 是 | 机器名 |
| `url` | `--url` | string | 是 | 被控端地址 https://主机:7443 |
| `code` | `--code` | string | 是 | 被控端给出的配对码 |
| `fingerprint` | `--fingerprint` | string |  | 被控端证书的 sha256 指纹（强烈建议填写） |
| `client` | `--client` | string |  | 本机在对方那里显示的名字（默认主机名） |

示例：

```bash
foxos machine pair --name vm1 --url https://192.168.1.20:7443 --code AB12-CD34-EF56 --fingerprint 3f…
```

限制：

- 只有人可以配对机器或修改授权

### `foxos machine remove`

移除配对的机器

```text
foxos machine remove MACHINE
```

工具接口名：`machine_remove` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `MACHINE` | string | 是 | 机器名 |

示例：

```bash
foxos machine remove vm1
```

### `foxos machine ping`

检查机器是否在线，看授权与谁在操作

```text
foxos machine ping MACHINE
```

工具接口名：`machine_ping` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `MACHINE` | string | 是 | 机器名 |

示例：

```bash
foxos machine ping vm1 --json
```

### `foxos machine call`

在一台机器上执行一条 foxos 命令

```text
foxos machine call MACHINE --command COMMAND [--params PARAMS]
```

工具接口名：`machine_call` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `MACHINE` | string | 是 | 机器名 |
| `command` | `--command` | string | 是 | 命令 ID（如 files.list） |
| `params` | `--params` | object |  | 命令参数（JSON 对象） |

示例：

```bash
foxos machine call vm1 --command files.list --params '{"path":"."}'
```

### `foxos machine host code`

（被控端）生成一次性配对码

```text
foxos machine host code [--ttl TTL]
```

工具接口名：`machine_host_code` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ttl` | `--ttl` | integer |  | 配对码有效秒数；默认 600 |

示例：

```bash
foxos machine host code --json
```

限制：

- 只有人可以配对机器或修改授权

### `foxos machine host clients`

（被控端）已配对的控制端与授权

```text
foxos machine host clients
```

工具接口名：`machine_host_clients` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos machine host clients --json
```

### `foxos machine host grant`

（被控端）给某台控制端的某个智能体授权

```text
foxos machine host grant --client CLIENT --bot BOT --permissions PERMISSIONS [--apps APPS] [--scope SCOPE]
```

工具接口名：`machine_host_grant` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `client` | `--client` | string | 是 | 控制端名 |
| `bot` | `--bot` | string | 是 | 控制端上的智能体 ID（* 表示全部） |
| `permissions` | `--permissions` | array | 是 | 权限：read、create、modify、delete、run |
| `apps` | `--apps` | array |  | 允许的应用（逗号分隔，不填表示全部） |
| `scope` | `--scope` | string |  | 允许的目录范围（工作空间内）；默认 . |

示例：

```bash
foxos machine host grant --client laptop --bot coder --permissions read,create,modify --apps files --scope projects
```

限制：

- 只有人可以配对机器或修改授权
- 默认拒绝：没有授权的智能体什么都不能做；machine 与 control 命令永远不能远程执行

### `foxos machine host revoke`

（被控端）撤销授权

```text
foxos machine host revoke --client CLIENT [--bot BOT]
```

工具接口名：`machine_host_revoke` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `client` | `--client` | string | 是 | 控制端名 |
| `bot` | `--bot` | string |  | 控制端上的智能体 ID（* 表示全部） |

示例：

```bash
foxos machine host revoke --client laptop --bot coder
```

### `foxos machine host unpair`

（被控端）解除一台控制端的配对

```text
foxos machine host unpair --client CLIENT
```

工具接口名：`machine_host_unpair` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `client` | `--client` | string | 是 | 控制端名 |

示例：

```bash
foxos machine host unpair --client laptop
```

## runtime — 运行环境：Node、Bun、Python、常用工具与智能体命令行

智能体运行环境：Node.js LTS、npm、pnpm、corepack、Bun、Python（pip、venv、uv、pipx）、git、gh、curl、wget、jq、ripgrep、fd、gcc/make、unzip、sqlite3，可选 Go 与 Rust，以及智能体命令行（gemini、codex、claude、qwen、opencode、cursor-agent、aider 与 ACP 适配器）。清单固定版本、许可证、官方来源和 sha256；ISO 只预装可再分发的，其余首次登录时安装。

### `foxos runtime list`

列出清单里的工具与安装状态

```text
foxos runtime list [--phase {iso,firstboot,optional}] [--group {runtime,tools,agents,optional}]
```

工具接口名：`runtime_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `phase` | `--phase` | string |  | 安装阶段；可选：iso / firstboot / optional |
| `group` | `--group` | string |  | 分组；可选：runtime / tools / agents / optional |

示例：

```bash
foxos runtime list --json
foxos runtime list --group agents
```

### `foxos runtime doctor`

检查运行环境：缺什么、版本、PEP 668、PATH、磁盘

```text
foxos runtime doctor
```

工具接口名：`runtime_doctor` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos runtime doctor --json
```

### `foxos runtime install`

安装工具（固定版本，官方来源，校验 sha256）；firstboot 表示全部首次登录项

```text
foxos runtime install NAME... [--force] [--accept-license]
```

工具接口名：`runtime_install` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | array | 是 | 工具名（见 runtime list），或 firstboot |
| `force` | `--force` | boolean |  | 已安装也重新安装 |
| `accept_license` | `--accept-license` | boolean |  | 确认许可证（不可再分发的工具需要） |

示例：

```bash
foxos runtime install codex codex-acp
foxos runtime install claude claude-acp --accept-license
foxos runtime install go
```

限制：

- 只有人可以安装软件
- 只从清单里的官方地址下载；不可再分发的工具需要 --accept-license

## sandbox — 轻量隔离

进程级沙箱：直接运行宿主上的程序，只能读写工作空间，可选禁止联网（Linux Landlock + seccomp、macOS Seatbelt、Windows 受限令牌 / AppContainer + 作业对象）。

限制：

- Linux 需要内核启用 Landlock（5.13+）；TCP 网络限制需 ABI 4（6.7+），信号隔离需 ABI 6（6.12+）
- Windows restricted 模式只限制写入（读取不受限）；appcontainer 模式读写与网络都受限，但很多程序在 AppContainer 中无法运行
- macOS 与 Windows 实现尚未在实机上验证

### `foxos sandbox check`

本机可用的轻量隔离能力（机制、Landlock ABI、网络 / 信号隔离）

```text
foxos sandbox check
```

工具接口名：`sandbox_check` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sandbox check --json
```

### `foxos sandbox run`

在轻量沙箱中运行命令：只能读写工作空间，可选禁止联网

```text
foxos sandbox run [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}] [--max-processes MAX_PROCESSES] [--memory-mb MEMORY_MB] [--cwd CWD] [--timeout TIMEOUT]
```

工具接口名：`sandbox_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `command` | `CMD` | array |  | 命令及参数（放在 -- 之后） |
| `network` | `--network` | string |  | 是否允许联网；可选：on / off；默认 on |
| `read` | `--read` | array |  | 额外只读路径（可重复） |
| `write` | `--write` | array |  | 额外可写路径（可重复） |
| `home` | `--home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写；可选：private / read / write；默认 private |
| `windows_mode` | `--windows-mode` | string |  | Windows：restricted 受限令牌 / appcontainer；可选：restricted / appcontainer；默认 restricted |
| `max_processes` | `--max-processes` | integer |  | 最多进程数（Windows 作业对象） |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限 MB（Windows 作业对象） |
| `cwd` | `--cwd` | string |  | 工作目录（工作空间内） |
| `timeout` | `--timeout` | number |  | 超时秒数；默认 600 |

示例：

```bash
foxos sandbox run --json -- python3 build.py
foxos sandbox run --network off -- sh -c 'curl -sI https://example.com'
```

### `foxos sandbox policy`

显示将生效的沙箱规则（不执行）

```text
foxos sandbox policy [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}]
```

工具接口名：`sandbox_policy` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `command` | `CMD` | array |  | 命令及参数（放在 -- 之后） |
| `network` | `--network` | string |  | 是否允许联网；可选：on / off；默认 on |
| `read` | `--read` | array |  | 额外只读路径（可重复） |
| `write` | `--write` | array |  | 额外可写路径（可重复） |
| `home` | `--home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写；可选：private / read / write；默认 private |
| `windows_mode` | `--windows-mode` | string |  | Windows：restricted 受限令牌 / appcontainer；可选：restricted / appcontainer；默认 restricted |

示例：

```bash
foxos sandbox policy --network off --json -- node agent.js
```

## sheets — 表格：读写标准 .xlsx 工作簿、公式、图表与导出

基于 openpyxl 读写 Excel 2007+ (.xlsx) 文件；公式按 Excel 语法写入（以 = 开头），用 LibreOffice 无头模式求值与导出 PDF/ODS。

限制：

- 只读写 .xlsx；.xls / .xlsm / .ods / .csv 输入暂不支持
- 公式以文本写入，求值依赖 LibreOffice（read --computed、export）
- 图表仅支持 bar / line / pie，数据按列组成系列
- 单次 read 最多返回 20000 个单元格

### `foxos sheets create`

新建一个 .xlsx 工作簿

```text
foxos sheets create FILE [--sheet SHEET] [--headers HEADERS] [--force]
```

工具接口名：`sheets_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 要创建的工作簿路径（.xlsx）；工作空间路径（write） |
| `sheet` | `--sheet / -s` | string |  | 第一个工作表的名称；默认 Sheet1 |
| `headers` | `--headers` | array |  | 第一行表头，逗号分隔（CLI）或字符串数组（工具接口） |
| `force` | `--force / -f` | boolean |  | 文件已存在时覆盖（上一版本会保存到 .foxos/versions） |

示例：

```bash
foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales
foxos sheets create report/q1.xlsx --force --json
```

限制：

- 只创建 .xlsx；父目录不存在时自动创建

### `foxos sheets read`

读取工作表单元格（公式、图表；可选用 LibreOffice 求值）

```text
foxos sheets read FILE [--sheet SHEET] [--range RANGE] [--computed]
```

工具接口名：`sheets_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（read） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `range` | `--range / -r` | string |  | A1 记法区域，如 A1:C10；默认整个已用区域 |
| `computed` | `--computed` | boolean |  | 用 LibreOffice 重算公式，额外返回 values（不修改原文件） |

示例：

```bash
foxos sheets read sales.xlsx
foxos sheets read sales.xlsx --range A1:B13 --computed --json
```

限制：

- 单次最多 20000 个单元格
- --computed 需要 LibreOffice

### `foxos sheets write`

写入单元格值或公式（CELL=VALUE，以 = 开头为公式）

```text
foxos sheets write FILE CELL=VALUE... [--sheet SHEET] [--create-sheet]
```

工具接口名：`sheets_write` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（write） |
| `cells` | `CELL=VALUE` | object | 是 | 要写入的单元格：{"A1": "Month", "B2": 120, "B14": "=SUM(B2:B13)"}；CLI 中写成 A1=Month B2=120 B14==SUM(B2:B13)，数字自动识别，TRUE/FALSE 为布尔，空值清空单元格 |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `create_sheet` | `--create-sheet` | boolean |  | 工作表不存在时新建 |

示例：

```bash
foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135
foxos sheets write sales.xlsx 'B14==SUM(B2:B13)' --sheet Sales
foxos sheets write sales.xlsx --cells-json '{"C2": "=B2*1.1"}' --json
```

限制：

- 公式按 Excel 英文函数名写入，不在写入时校验或求值
- 不支持写入样式、合并单元格（阶段 0）

### `foxos sheets chart create`

基于单元格区域创建原生 Excel 图表

```text
foxos sheets chart create FILE --type {bar,line,pie} --data DATA [--categories CATEGORIES] [--title TITLE] [--sheet SHEET] [--anchor ANCHOR] [--x-title X_TITLE] [--y-title Y_TITLE] [--no-header]
```

工具接口名：`sheets_chart_create` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（write） |
| `type` | `--type / -t` | string | 是 | 图表类型；可选：bar / line / pie |
| `data` | `--data / -d` | string | 是 | 数据区域（按列为系列，首行默认为系列名），如 B1:B13 |
| `categories` | `--categories / -c` | string |  | 分类（X 轴）区域，如 A2:A13 |
| `title` | `--title` | string |  | 图表标题 |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `anchor` | `--anchor / -a` | string |  | 图表左上角所在单元格，默认放在数据右侧 |
| `x_title` | `--x-title` | string |  | X 轴标题（bar/line） |
| `y_title` | `--y-title` | string |  | Y 轴标题（bar/line） |
| `no_header` | `--no-header` | boolean |  | 数据区域首行不是系列名 |

示例：

```bash
foxos sheets chart create sales.xlsx --type bar --data B1:B13 --categories A2:A13 --title '月度销售额'
foxos sheets chart create sales.xlsx -t line -d B1:C13 -c A2:A13 --anchor E20 --json
```

限制：

- 仅 bar / line / pie
- 饼图只能一个系列
- 图表样式、颜色暂不可配置

### `foxos sheets chart list`

列出工作簿中的图表

```text
foxos sheets chart list FILE [--sheet SHEET]
```

工具接口名：`sheets_chart_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（read） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |

示例：

```bash
foxos sheets chart list sales.xlsx --json
```

### `foxos sheets export`

导出为 csv / pdf / ods / xlsx（格式由输出文件扩展名决定）

```text
foxos sheets export FILE OUTPUT [--sheet SHEET] [--force]
```

工具接口名：`sheets_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 源工作簿路径；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径：.csv / .pdf / .ods / .xlsx；工作空间路径（write） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `force` | `--force / -f` | boolean |  | 输出文件已存在时覆盖 |

示例：

```bash
foxos sheets export sales.xlsx sales.csv
foxos sheets export sales.xlsx out/sales.pdf --force --json
```

限制：

- csv 只导出一个工作表，公式导出为求值结果（需 LibreOffice，否则导出公式文本）
- pdf / ods 需要 LibreOffice

## slides — 演示：读写标准 .pptx（标题页、要点页、图片、原生图表、备注），替换文本与导出

基于 python-pptx 读写 PowerPoint 2007+ (.pptx)，使用默认模板的标准版式。

限制：

- 只读写 .pptx；.ppt / .odp 输入暂不支持
- 版式来自默认模板：title / title-content / section / two-content / title-only / blank
- 图表仅 bar / line / pie，数据直接给出（不链接外部 xlsx）

### `foxos slides create`

新建一个 .pptx 演示文稿（可带标题页）

```text
foxos slides create FILE [--title TITLE] [--subtitle SUBTITLE] [--aspect {16:9,4:3}] [--force]
```

工具接口名：`slides_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `title` | `--title` | string |  | 标题页标题 |
| `subtitle` | `--subtitle` | string |  | 标题页副标题 |
| `aspect` | `--aspect` | string |  | 页面比例；可选：16:9 / 4:3；默认 16:9 |
| `force` | `--force / -f` | boolean |  | 已存在时覆盖 |

示例：

```bash
foxos slides create deck.pptx --title '2026 年销售分析' --subtitle '数据组'
```

### `foxos slides read`

读取每页的版式、标题、文本、图表数据与备注

```text
foxos slides read FILE
```

工具接口名：`slides_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（read） |

示例：

```bash
foxos slides read deck.pptx --json
```

### `foxos slides add`

追加一页（标题 + 要点 / 图片 / 备注）

```text
foxos slides add FILE [--title TITLE] [--bullet BULLET] [--layout {title,title-content,section,two-content,title-only,blank}] [--image IMAGE] [--notes NOTES]
```

工具接口名：`slides_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `title` | `--title / -t` | string |  | 页面标题 |
| `bullet` | `--bullet / -b` | array |  | 要点，可重复：--bullet 一 --bullet 二 |
| `layout` | `--layout` | string |  | 版式；可选：title / title-content / section / two-content / title-only / blank |
| `image` | `--image` | string |  | 插入图片（工作空间内 png/jpg）；工作空间路径（read） |
| `notes` | `--notes` | string |  | 演讲者备注 |

示例：

```bash
foxos slides add deck.pptx -t 全年概况 -b '销售额 2013 万元' -b '同比增长 12%'
foxos slides add deck.pptx -t 趋势 --image charts/trend.png
```

### `foxos slides chart add`

插入原生 PowerPoint 图表（默认新建一页）

```text
foxos slides chart add FILE --type {bar,line,pie} --categories CATEGORIES --values VALUES [--slide SLIDE] [--series-name SERIES_NAME] [--title TITLE]
```

工具接口名：`slides_chart_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `type` | `--type / -T` | string | 是 | 图表类型；可选：bar / line / pie |
| `categories` | `--categories / -c` | array | 是 | 分类，逗号分隔 |
| `values` | `--values / -v` | array | 是 | 数值，逗号分隔，与分类一一对应 |
| `slide` | `--slide` | integer |  | 插入到已有的第 N 页（从 1 开始）；不填则新建一页 |
| `series_name` | `--series-name` | string |  | 系列名称；默认 Series 1 |
| `title` | `--title` | string |  | 新建页时的页面标题 |

示例：

```bash
foxos slides chart add deck.pptx --type bar -c Q1,Q2,Q3,Q4 -v 405,428,547,633 --title 季度销售额
```

### `foxos slides replace`

查找并替换所有页中的文本

```text
foxos slides replace FILE --find FIND --replace REPLACE
```

工具接口名：`slides_replace` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `find` | `--find` | string | 是 | 要查找的文本 |
| `replace` | `--replace` | string | 是 | 替换为 |

示例：

```bash
foxos slides replace deck.pptx --find 2025 --replace 2026
```

限制：

- 只在同一个文本 run 内匹配

### `foxos slides export`

导出为 pdf / odp

```text
foxos slides export FILE OUTPUT [--force]
```

工具接口名：`slides_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 输出已存在时覆盖 |

示例：

```bash
foxos slides export deck.pptx deck.pdf
```

限制：

- 需要 LibreOffice

## workspace — 工作空间信息

当前工作空间根目录与基本信息。

### `foxos workspace info`

显示工作空间根目录、审计日志位置与文件数

```text
foxos workspace info
```

工具接口名：`workspace_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos workspace info --json
```

## files — 文件：列出、读写文本、新建、重命名、删除与恢复

所有操作限定在工作空间内，删除进入回收站；.foxos 保留目录不可见。

### `foxos files list`

列出目录内容（默认工作空间根目录）

```text
foxos files list [PATH] [--recursive] [--hidden]
```

工具接口名：`files_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string |  | 目录（工作空间内），默认根目录；工作空间路径（read） |
| `recursive` | `--recursive / -r` | boolean |  | 递归列出所有文件 |
| `hidden` | `--hidden / -a` | boolean |  | 包含以 . 开头的文件 |

示例：

```bash
foxos files list
foxos files list reports --json
foxos files list -r
```

### `foxos files read`

读取 UTF-8 文本文件

```text
foxos files read PATH
```

工具接口名：`files_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos files read notes.md
foxos files read src/app.py --json
```

限制：

- 上限 5 MB；二进制与办公文件请用对应应用命令

### `foxos files write`

写入 UTF-8 文本文件（原子保存，覆盖前保留上一版）

```text
foxos files write PATH --content CONTENT [--expect-mtime EXPECT_MTIME] [--force]
```

工具接口名：`files_write` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（write） |
| `content` | `--content` | string | 是 | 文件内容；CLI 可用 --content-stdin 从标准输入读取 |
| `expect_mtime` | `--expect-mtime` | number |  | 乐观并发检查：文件当前修改时间必须等于该值，否则 CONFLICT |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files write notes.md --content '# 标题'
cat a.py | foxos files write src/a.py --content-stdin
```

### `foxos files mkdir`

新建文件夹（含父目录）

```text
foxos files mkdir PATH
```

工具接口名：`files_mkdir` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件夹路径；工作空间路径（write） |

示例：

```bash
foxos files mkdir reports/2026
```

### `foxos files rename`

重命名或移动文件 / 文件夹

```text
foxos files rename SOURCE TARGET [--force]
```

工具接口名：`files_rename` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `source` | `SOURCE` | string | 是 | 原路径；工作空间路径（write） |
| `target` | `TARGET` | string | 是 | 新路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files rename draft.md final.md
foxos files rename a.xlsx archive/a.xlsx
```

### `foxos files delete`

删除文件或文件夹（移入回收站，可恢复）

```text
foxos files delete PATH
```

工具接口名：`files_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 要删除的路径；工作空间路径（write） |

示例：

```bash
foxos files delete old.csv
```

限制：

- 移入 .foxos/trash/，用 foxos files restore 恢复

### `foxos files restore`

从回收站恢复

```text
foxos files restore TRASH_ID [--force]
```

工具接口名：`files_restore` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `trash_id` | `TRASH_ID` | string | 是 | 回收站条目 ID（files delete 返回，或 files trash 查看） |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files restore 20261110T2051-ab12cd
```

### `foxos files trash`

列出回收站

```text
foxos files trash
```

工具接口名：`files_trash` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos files trash --json
```

## audit — 审计日志

查询 .foxos/audit.jsonl：谁在什么时候对什么文件执行了什么命令。

### `foxos audit tail`

查看最近的审计记录

```text
foxos audit tail [--limit LIMIT] [--filter-agent AGENT] [--command COMMAND]
```

工具接口名：`audit_tail` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `limit` | `--limit / -n` | integer |  | 返回条数；默认 20 |
| `agent` | `--filter-agent` | string |  | 只看某个智能体 |
| `command` | `--command` | string |  | 按命令前缀过滤，如 sheets.write |

示例：

```bash
foxos audit tail -n 50
foxos audit tail --filter-agent data-agent --json
```

限制：

- 查询本身不写入审计日志

## queue — 任务队列

记录任务目标与状态；由桌面的 ACP 智能体会话执行。

### `foxos queue create`

把一个任务目标加入队列

```text
foxos queue create GOAL
```

工具接口名：`queue_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `goal` | `GOAL` | string | 是 | 任务目标（自然语言） |

示例：

```bash
foxos queue create '根据 sales.xlsx 制作分析报告'
```

限制：

- 只记录任务；执行由 ACP 智能体会话完成

### `foxos queue list`

列出任务队列

```text
foxos queue list [--limit LIMIT]
```

工具接口名：`queue_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `limit` | `--limit / -n` | integer |  | 返回条数；默认 20 |

示例：

```bash
foxos queue list --json
```

## control — 人工接管

暂停后，非 human 身份的调用者不能执行任何写操作（读操作不受影响），返回 PAUSED（退出码 8）。

### `foxos control status`

查看是否处于人工接管（暂停）状态

```text
foxos control status
```

工具接口名：`control_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos control status --json
```

限制：

- 查询本身不写入审计日志

### `foxos control pause`

人工接管：暂停所有智能体的写操作

```text
foxos control pause [--reason REASON] [--only IDENTITY]
```

工具接口名：`control_pause` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `reason` | `--reason` | string |  | 暂停原因（写入状态与审计） |
| `targets` | `--only` | array |  | 只暂停这些身份（如 bot:coder）；不填则全部暂停 |

示例：

```bash
foxos control pause --reason '我来改第 3 页数据'
foxos control pause --only bot:coder
```

限制：

- 只有 human 身份可以执行
- 身份由调用方声明（--agent），属于应用层约束

### `foxos control resume`

结束人工接管，恢复智能体写操作

```text
foxos control resume [--only IDENTITY]
```

工具接口名：`control_resume` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `targets` | `--only` | array |  | 只恢复这些身份；不填则全部恢复 |

示例：

```bash
foxos control resume
foxos control resume --only bot:coder
```

限制：

- 只有 human 身份可以执行

## Everything 应用的通用命令（每个应用都有）

以下以 `spreadsheet` 为例，把应用 ID 换成任意 Everything 应用即可。

## spreadsheet — Spreadsheet

办公 · 替代 Microsoft Excel, Google Sheets, Apple Numbers。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos spreadsheet app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos spreadsheet app open [--file FILE] [--headless]
```

工具接口名：`spreadsheet_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos spreadsheet app open
foxos spreadsheet app open --headless --json
```

### `foxos spreadsheet app close`

关闭应用实例

```text
foxos spreadsheet app close
```

工具接口名：`spreadsheet_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet app close --json
```

### `foxos spreadsheet app status`

应用是否已安装、是否在运行

```text
foxos spreadsheet app status
```

工具接口名：`spreadsheet_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet app status --json
```

### `foxos spreadsheet app reset`

重置应用：关闭实例并清空本工作空间下的应用数据（AppData/<应用> 与浏览器存储）

```text
foxos spreadsheet app reset
```

工具接口名：`spreadsheet_app_reset` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet app reset --json
```

### `foxos spreadsheet file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos spreadsheet file open PATH
```

工具接口名：`spreadsheet_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos spreadsheet file open X
```

### `foxos spreadsheet ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos spreadsheet ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`spreadsheet_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos spreadsheet ui snapshot --json
```

### `foxos spreadsheet ui text`

读取界面上的可见文本

```text
foxos spreadsheet ui text
```

工具接口名：`spreadsheet_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet ui text --json
```

### `foxos spreadsheet ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos spreadsheet ui click [--ref REF] [--name NAME] [--role ROLE] [--force]
```

工具接口名：`spreadsheet_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |
| `force` | `--force` | boolean |  | 控件被弹窗挡住时也强制点击 |

示例：

```bash
foxos spreadsheet ui click --ref e12
foxos spreadsheet ui click --name Settings
```

### `foxos spreadsheet ui type`

向控件输入文本（真实输入事件）

```text
foxos spreadsheet ui type TEXT [--ref REF] [--clear]
```

工具接口名：`spreadsheet_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos spreadsheet ui type 'hello' --ref e5
```

### `foxos spreadsheet ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos spreadsheet ui set --ref REF --value VALUE [--force]
```

工具接口名：`spreadsheet_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |
| `force` | `--force` | boolean |  | 控件被挡住时也强制设置 |

示例：

```bash
foxos spreadsheet ui set 
```

### `foxos spreadsheet ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos spreadsheet ui press KEY [--ref REF]
```

工具接口名：`spreadsheet_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos spreadsheet ui press mod+z
```

### `foxos spreadsheet ui screenshot`

应用窗口截图（PNG）

```text
foxos spreadsheet ui screenshot [--out OUT]
```

工具接口名：`spreadsheet_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos spreadsheet ui screenshot --json
```

### `foxos spreadsheet data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos spreadsheet data list [PATTERN]
```

工具接口名：`spreadsheet_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos spreadsheet data list --json
```

### `foxos spreadsheet data get`

读取应用保存的一项数据

```text
foxos spreadsheet data get KEY
```

工具接口名：`spreadsheet_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos spreadsheet data get X
```

### `foxos spreadsheet module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos spreadsheet module list
```

工具接口名：`spreadsheet_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet module list --json
```

### `foxos spreadsheet module read`

读取应用模块中的值（如 store 状态）

```text
foxos spreadsheet module read TARGET
```

工具接口名：`spreadsheet_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos spreadsheet module read X
```

### `foxos spreadsheet module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos spreadsheet module call TARGET [--args ARGS]
```

工具接口名：`spreadsheet_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos spreadsheet module call X
```

### `foxos spreadsheet op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos spreadsheet op list
```

工具接口名：`spreadsheet_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet op list --json
```

## Everything 应用的语义命令

每个应用的语义命令来自操作清单（`packages/core/foxos/data/ops/<应用>.json`，界面路径与效果见 `docs/operations/<应用>.md`）。

### spreadsheet（`spreadsheet`，368 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos spreadsheet account-menu select TARGET` | `spreadsheet_account-menu_select` | read | account menu for *（1 项，如 Account menu for local） |
| `foxos spreadsheet font select TARGET` | `spreadsheet_font_select` | read | font: *（1 项，如 Font: Calibri (Body)） |
| `foxos spreadsheet font-size select TARGET` | `spreadsheet_font-size_select` | read | font size: *（1 项，如 Font size: 11） |
| `foxos spreadsheet font-size-2 select TARGET` | `spreadsheet_font-size-2_select` | read | # font size（1 项，如 Decrease font size） |
| `foxos spreadsheet indent select TARGET` | `spreadsheet_indent_select` | read | # indent（1 项，如 Decrease indent） |
| `foxos spreadsheet number-format select TARGET` | `spreadsheet_number-format_select` | read | number format: *（1 项，如 Number format: General） |
| `foxos spreadsheet places show TARGET` | `spreadsheet_places_show` | read | more # places（1 项，如 More decimal places） |
| `foxos spreadsheet fewer-places select TARGET` | `spreadsheet_fewer-places_select` | read | fewer # places（1 项，如 Fewer decimal places） |
| `foxos spreadsheet sheets select TARGET` | `spreadsheet_sheets_select` | read | #（1 项，如 Sheet1） |
| `foxos spreadsheet options select TARGET` | `spreadsheet_options_select` | read | # options（1 项，如 Sheet1 options） |
| `foxos spreadsheet view zoom-level TARGET` | `spreadsheet_view_zoom-level` | modify | zoom level: *（1 项，如 Zoom level: 100%） |
| `foxos spreadsheet other-charts select TARGET` | `spreadsheet_other-charts_select` | read | other charts: *（1 项，如 Other Charts: waterfall, funnel, stock, surface or radar） |
| `foxos spreadsheet pen select TARGET` | `spreadsheet_pen_select` | read | pen: *（2 项，如 Pen: Black, 0.5 mm） |
| `foxos spreadsheet pencil select TARGET` | `spreadsheet_pencil_select` | read | pencil: *（1 项，如 Pencil: Gray, 1 mm） |
| `foxos spreadsheet highlighter select TARGET` | `spreadsheet_highlighter_select` | read | highlighter: *（1 项，如 Highlighter: Yellow, 6 mm） |
| `foxos spreadsheet item select TARGET` | `spreadsheet_item_select` | read | #%（1 项，如 100%） |
| `foxos spreadsheet spreadsheets previous` | `spreadsheet_spreadsheets_previous` | read | Back to all spreadsheets |
| `foxos spreadsheet autosave toggle` | `spreadsheet_autosave_toggle` | modify | AutoSave |
| `foxos spreadsheet save save` | `spreadsheet_save_save` | modify | Save |
| `foxos spreadsheet undo undo` | `spreadsheet_undo_undo` | modify | Undo |
| `foxos spreadsheet history undo` | `spreadsheet_history_undo` | modify | Undo history |
| `foxos spreadsheet redo redo` | `spreadsheet_redo_redo` | modify | Redo |
| `foxos spreadsheet customize-quick-access-toolbar activate` | `spreadsheet_customize-quick-access-toolbar_activate` | modify | Customize Quick Access Toolbar |
| `foxos spreadsheet edit update` | `spreadsheet_edit_update` | modify | Edit |
| `foxos spreadsheet view show` | `spreadsheet_view_show` | read | View |
| `foxos spreadsheet insert create` | `spreadsheet_insert_create` | modify | Insert |
| `foxos spreadsheet format activate` | `spreadsheet_format_activate` | modify | Format |
| `foxos spreadsheet tools activate` | `spreadsheet_tools_activate` | modify | Tools |
| `foxos spreadsheet help show` | `spreadsheet_help_show` | read | Help |
| `foxos spreadsheet untitled-spreadsheet rename` | `spreadsheet_untitled-spreadsheet_rename` | modify | Rename "Untitled spreadsheet" |
| `foxos spreadsheet saved activate` | `spreadsheet_saved_activate` | modify | Saved |
| `foxos spreadsheet menus search` | `spreadsheet_menus_search` | read | Search the menus |
| `foxos spreadsheet comments activate` | `spreadsheet_comments_activate` | modify | Comments |
| `foxos spreadsheet home show` | `spreadsheet_home_show` | read | Home |
| `foxos spreadsheet insert-2 create` | `spreadsheet_insert-2_create` | modify | Insert |
| `foxos spreadsheet draw draw` | `spreadsheet_draw_draw` | modify | Draw |
| `foxos spreadsheet page-layout show` | `spreadsheet_page-layout_show` | read | Page Layout |
| `foxos spreadsheet formulas show` | `spreadsheet_formulas_show` | read | Formulas |
| `foxos spreadsheet review show` | `spreadsheet_review_show` | read | Review |
| `foxos spreadsheet view-2 show` | `spreadsheet_view-2_show` | read | View |
| `foxos spreadsheet automate show` | `spreadsheet_automate_show` | read | Automate |
| `foxos spreadsheet scroll-ribbon-left activate` | `spreadsheet_scroll-ribbon-left_activate` | modify | Scroll ribbon left |
| `foxos spreadsheet scroll-ribbon-right activate` | `spreadsheet_scroll-ribbon-right_activate` | modify | Scroll ribbon right |
| `foxos spreadsheet ribbon collapse` | `spreadsheet_ribbon_collapse` | read | Collapse ribbon |
| `foxos spreadsheet paste paste` | `spreadsheet_paste_paste` | modify | Paste |
| `foxos spreadsheet options paste` | `spreadsheet_options_paste` | modify | Paste options |
| `foxos spreadsheet cut cut` | `spreadsheet_cut_cut` | modify | Cut |
| `foxos spreadsheet copy copy` | `spreadsheet_copy_copy` | modify | Copy |
| `foxos spreadsheet format-painter activate` | `spreadsheet_format-painter_activate` | modify | Format Painter |
| `foxos spreadsheet increase-font-size activate` | `spreadsheet_increase-font-size_activate` | modify | Increase font size |
| `foxos spreadsheet bold format` | `spreadsheet_bold_format` | modify | Bold |
| `foxos spreadsheet italic format` | `spreadsheet_italic_format` | modify | Italic |
| `foxos spreadsheet underline format` | `spreadsheet_underline_format` | modify | Underline |
| `foxos spreadsheet borders activate` | `spreadsheet_borders_activate` | modify | Borders |
| `foxos spreadsheet fill-color-yellow confirm` | `spreadsheet_fill-color-yellow_confirm` | modify | Apply fill color yellow |
| `foxos spreadsheet fill-color activate` | `spreadsheet_fill-color_activate` | modify | Fill color |
| `foxos spreadsheet font-color-red confirm` | `spreadsheet_font-color-red_confirm` | modify | Apply font color red |
| `foxos spreadsheet text-color activate` | `spreadsheet_text-color_activate` | modify | Text color |
| `foxos spreadsheet top-align activate` | `spreadsheet_top-align_activate` | modify | Top align |
| `foxos spreadsheet middle-align activate` | `spreadsheet_middle-align_activate` | modify | Middle align |
| `foxos spreadsheet bottom-align activate` | `spreadsheet_bottom-align_activate` | modify | Bottom align |
| `foxos spreadsheet orientation activate` | `spreadsheet_orientation_activate` | modify | Orientation |
| `foxos spreadsheet left align` | `spreadsheet_left_align` | modify | Align left |
| `foxos spreadsheet center align` | `spreadsheet_center_align` | modify | Align center |
| `foxos spreadsheet right align` | `spreadsheet_right_align` | modify | Align right |
| `foxos spreadsheet increase-indent activate` | `spreadsheet_increase-indent_activate` | modify | Increase indent |
| `foxos spreadsheet wrap-text activate` | `spreadsheet_wrap-text_activate` | modify | Wrap text |
| `foxos spreadsheet merge-center activate` | `spreadsheet_merge-center_activate` | modify | Merge & Center |
| `foxos spreadsheet merge-options activate` | `spreadsheet_merge-options_activate` | modify | Merge options |
| `foxos spreadsheet accounting-number-format activate` | `spreadsheet_accounting-number-format_activate` | modify | Accounting Number Format |
| `foxos spreadsheet accounting-number-format-options activate` | `spreadsheet_accounting-number-format-options_activate` | modify | Accounting Number Format options |
| `foxos spreadsheet format-as-percent activate` | `spreadsheet_format-as-percent_activate` | modify | Format as percent |
| `foxos spreadsheet comma-style activate` | `spreadsheet_comma-style_activate` | modify | Comma Style |
| `foxos spreadsheet conditional-formatting activate` | `spreadsheet_conditional-formatting_activate` | modify | Conditional formatting |
| `foxos spreadsheet format-as-table activate` | `spreadsheet_format-as-table_activate` | modify | Format as Table |
| `foxos spreadsheet cell-styles activate` | `spreadsheet_cell-styles_activate` | modify | Cell styles |
| `foxos spreadsheet insert-3 create` | `spreadsheet_insert-3_create` | modify | Insert |
| `foxos spreadsheet delete delete` | `spreadsheet_delete_delete` | delete | Delete |
| `foxos spreadsheet format-2 activate` | `spreadsheet_format-2_activate` | modify | Format |
| `foxos spreadsheet autosum activate` | `spreadsheet_autosum_activate` | modify | AutoSum |
| `foxos spreadsheet autosum-options activate` | `spreadsheet_autosum-options_activate` | modify | AutoSum options |
| `foxos spreadsheet fill activate` | `spreadsheet_fill_activate` | modify | Fill |
| `foxos spreadsheet clear clear` | `spreadsheet_clear_clear` | modify | Clear |
| `foxos spreadsheet filter sort` | `spreadsheet_filter_sort` | read | Sort & Filter |
| `foxos spreadsheet select search` | `spreadsheet_select_search` | read | Find & Select |
| `foxos spreadsheet cell-reference set VALUE [--submit]` | `spreadsheet_cell-reference_set` | modify | Cell reference |
| `foxos spreadsheet named-ranges activate` | `spreadsheet_named-ranges_activate` | modify | Named ranges |
| `foxos spreadsheet edit cancel` | `spreadsheet_edit_cancel` | read | Cancel edit |
| `foxos spreadsheet edit confirm` | `spreadsheet_edit_confirm` | modify | Apply edit |
| `foxos spreadsheet function create` | `spreadsheet_function_create` | modify | Insert function |
| `foxos spreadsheet formula-or-value set VALUE [--submit]` | `spreadsheet_formula-or-value_set` | modify | Formula or value |
| `foxos spreadsheet formula-bar expand` | `spreadsheet_formula-bar_expand` | read | Expand the formula bar |
| `foxos spreadsheet select select` | `spreadsheet_select_select` | read | Select all |
| `foxos spreadsheet spreadsheet-grid activate` | `spreadsheet_spreadsheet-grid_activate` | modify | Spreadsheet grid |
| `foxos spreadsheet scroll-sheets-left activate` | `spreadsheet_scroll-sheets-left_activate` | modify | Scroll sheets left |
| `foxos spreadsheet scroll-sheets-right activate` | `spreadsheet_scroll-sheets-right_activate` | modify | Scroll sheets right |
| `foxos spreadsheet sheets activate` | `spreadsheet_sheets_activate` | modify | All sheets |
| `foxos spreadsheet sheet create` | `spreadsheet_sheet_create` | modify | Add sheet |
| `foxos spreadsheet accessibility run` | `spreadsheet_accessibility_run` | modify | Check Accessibility |
| `foxos spreadsheet normal activate` | `spreadsheet_normal_activate` | modify | Normal |
| `foxos spreadsheet page-layout activate` | `spreadsheet_page-layout_activate` | modify | Page Layout |
| `foxos spreadsheet page-break-preview activate` | `spreadsheet_page-break-preview_activate` | modify | Page Break Preview |
| `foxos spreadsheet view zoom-out` | `spreadsheet_view_zoom-out` | modify | Zoom out |
| `foxos spreadsheet worksheet-zoom set VALUE [--submit]` | `spreadsheet_worksheet-zoom_set` | modify | Worksheet zoom |
| `foxos spreadsheet view zoom-` | `spreadsheet_view_zoom-` | modify | Zoom in |
| `foxos spreadsheet assistant resize` | `spreadsheet_assistant_resize` | modify | Resize the assistant |
| `foxos spreadsheet chat create` | `spreadsheet_chat_create` | modify | New chat |
| `foxos spreadsheet assistant-settings activate` | `spreadsheet_assistant-settings_activate` | modify | Assistant settings |
| `foxos spreadsheet assistant collapse` | `spreadsheet_assistant_collapse` | read | Collapse the assistant |
| `foxos spreadsheet loan-calculator-payment-schedule create` | `spreadsheet_loan-calculator-payment-schedule_create` | modify | Create a loan calculator with a payment schedule |
| `foxos spreadsheet message-assistant set VALUE [--submit]` | `spreadsheet_message-assistant_set` | modify | Message the assistant |
| `foxos spreadsheet attach-files activate` | `spreadsheet_attach-files_activate` | modify | Attach files |
| `foxos spreadsheet send send` | `spreadsheet_send_send` | modify | Send |
| `foxos spreadsheet spreadsheet create` | `spreadsheet_spreadsheet_create` | modify | New Spreadsheet |
| `foxos spreadsheet open open` | `spreadsheet_open_open` | read | Open |
| `foxos spreadsheet customize-quick-access-toolbar-save save` | `spreadsheet_customize-quick-access-toolbar-save_save` | modify | Save |
| `foxos spreadsheet print print` | `spreadsheet_print_print` | read | Print |
| `foxos spreadsheet spelling activate` | `spreadsheet_spelling_activate` | modify | Spelling |
| `foxos spreadsheet customize-quick-access-toolbar-undo undo` | `spreadsheet_customize-quick-access-toolbar-undo_undo` | modify | Undo |
| `foxos spreadsheet customize-quick-access-toolbar-redo redo` | `spreadsheet_customize-quick-access-toolbar-redo_redo` | modify | Redo |
| `foxos spreadsheet ascending sort` | `spreadsheet_ascending_sort` | read | Sort Ascending |
| `foxos spreadsheet descending sort` | `spreadsheet_descending_sort` | read | Sort Descending |
| `foxos spreadsheet find search` | `spreadsheet_find_search` | read | Find |
| `foxos spreadsheet chart create` | `spreadsheet_chart_create` | modify | Insert Chart |
| `foxos spreadsheet filter filter` | `spreadsheet_filter_filter` | read | Filter |
| `foxos spreadsheet commands show` | `spreadsheet_commands_show` | read | More Commands… |
| `foxos spreadsheet below-ribbon show` | `spreadsheet_below-ribbon_show` | read | Show Below the Ribbon |
| `foxos spreadsheet command-labels show` | `spreadsheet_command-labels_show` | read | Show Command Labels |
| `foxos spreadsheet close close` | `spreadsheet_close_close` | read | Close |
| `foxos spreadsheet name set VALUE [--submit]` | `spreadsheet_name_set` | modify | Name |
| `foxos spreadsheet cancel cancel` | `spreadsheet_cancel_cancel` | read | Cancel |
| `foxos spreadsheet rename rename` | `spreadsheet_rename_rename` | modify | Rename |
| `foxos spreadsheet system-theme toggle` | `spreadsheet_system-theme_toggle` | modify | System theme |
| `foxos spreadsheet light-theme toggle` | `spreadsheet_light-theme_toggle` | modify | Light theme |
| `foxos spreadsheet dark-theme toggle` | `spreadsheet_dark-theme_toggle` | modify | Dark theme |
| `foxos spreadsheet regional-format-english-united-states activate` | `spreadsheet_regional-format-english-united-states_activate` | modify | Regional format, English (United States) |
| `foxos spreadsheet options activate` | `spreadsheet_options_activate` | modify | Options… |
| `foxos spreadsheet keyboard-shortcuts activate` | `spreadsheet_keyboard-shortcuts_activate` | modify | Keyboard shortcuts… |
| `foxos spreadsheet about show` | `spreadsheet_about_show` | read | About… |
| `foxos spreadsheet pivottable activate` | `spreadsheet_pivottable_activate` | modify | PivotTable |
| `foxos spreadsheet recommended-pivottables activate` | `spreadsheet_recommended-pivottables_activate` | modify | Recommended PivotTables |
| `foxos spreadsheet table activate` | `spreadsheet_table_activate` | modify | Table |
| `foxos spreadsheet pictures activate` | `spreadsheet_pictures_activate` | modify | Pictures |
| `foxos spreadsheet shapes activate` | `spreadsheet_shapes_activate` | modify | Shapes |
| `foxos spreadsheet icons activate` | `spreadsheet_icons_activate` | modify | Icons |
| `foxos spreadsheet smartart-graphic create` | `spreadsheet_smartart-graphic_create` | modify | Insert SmartArt graphic |
| `foxos spreadsheet recommended-charts activate` | `spreadsheet_recommended-charts_activate` | modify | Recommended Charts |
| `foxos spreadsheet column-chart create` | `spreadsheet_column-chart_create` | modify | Insert column chart |
| `foxos spreadsheet line-chart create` | `spreadsheet_line-chart_create` | modify | Insert line chart |
| `foxos spreadsheet pie-chart create` | `spreadsheet_pie-chart_create` | modify | Insert pie chart |
| `foxos spreadsheet bar-chart create` | `spreadsheet_bar-chart_create` | modify | Insert bar chart |
| `foxos spreadsheet area-chart create` | `spreadsheet_area-chart_create` | modify | Insert area chart |
| `foxos spreadsheet scatter-chart create` | `spreadsheet_scatter-chart_create` | modify | Insert scatter chart |
| `foxos spreadsheet hierarchy-chart create` | `spreadsheet_hierarchy-chart_create` | modify | Insert hierarchy chart |
| `foxos spreadsheet statistic-chart create` | `spreadsheet_statistic-chart_create` | modify | Insert statistic chart |
| `foxos spreadsheet combo-chart create` | `spreadsheet_combo-chart_create` | modify | Insert combo chart |
| `foxos spreadsheet line-sparklines create` | `spreadsheet_line-sparklines_create` | modify | Insert line sparklines |
| `foxos spreadsheet column-sparklines create` | `spreadsheet_column-sparklines_create` | modify | Insert column sparklines |
| `foxos spreadsheet win-loss-sparklines create` | `spreadsheet_win-loss-sparklines_create` | modify | Insert win/loss sparklines |
| `foxos spreadsheet slicer activate` | `spreadsheet_slicer_activate` | modify | Slicer |
| `foxos spreadsheet timeline activate` | `spreadsheet_timeline_activate` | modify | Timeline |
| `foxos spreadsheet link create` | `spreadsheet_link_create` | modify | Insert link |
| `foxos spreadsheet note activate` | `spreadsheet_note_activate` | modify | Note |
| `foxos spreadsheet comment activate` | `spreadsheet_comment_activate` | modify | Comment |
| `foxos spreadsheet text-box activate` | `spreadsheet_text-box_activate` | modify | Text Box |
| `foxos spreadsheet header-footer activate` | `spreadsheet_header-footer_activate` | modify | Header & Footer |
| `foxos spreadsheet wordart activate` | `spreadsheet_wordart_activate` | modify | WordArt |
| `foxos spreadsheet checkbox activate` | `spreadsheet_checkbox_activate` | modify | Checkbox |
| `foxos spreadsheet dropdown activate` | `spreadsheet_dropdown_activate` | modify | Dropdown |
| `foxos spreadsheet date-picker activate` | `spreadsheet_date-picker_activate` | modify | Date Picker |
| `foxos spreadsheet equation activate` | `spreadsheet_equation_activate` | modify | Equation |
| `foxos spreadsheet equation-options activate` | `spreadsheet_equation-options_activate` | modify | Equation options |
| `foxos spreadsheet symbol activate` | `spreadsheet_symbol_activate` | modify | Symbol |
| `foxos spreadsheet insert-sheet create` | `spreadsheet_insert-sheet_create` | modify | New Sheet |
| `foxos spreadsheet draw-select select` | `spreadsheet_draw-select_select` | read | Select |
| `foxos spreadsheet lasso-select activate` | `spreadsheet_lasso-select_activate` | modify | Lasso Select |
| `foxos spreadsheet eraser activate` | `spreadsheet_eraser_activate` | modify | Eraser |
| `foxos spreadsheet pen create` | `spreadsheet_pen_create` | modify | Add Pen |
| `foxos spreadsheet touch draw` | `spreadsheet_touch_draw` | modify | Draw with Touch |
| `foxos spreadsheet ink-shape activate` | `spreadsheet_ink-shape_activate` | modify | Ink to Shape |
| `foxos spreadsheet themes activate` | `spreadsheet_themes_activate` | modify | Themes |
| `foxos spreadsheet theme-colors activate` | `spreadsheet_theme-colors_activate` | modify | Theme Colors |
| `foxos spreadsheet theme-fonts activate` | `spreadsheet_theme-fonts_activate` | modify | Theme Fonts |
| `foxos spreadsheet effects activate` | `spreadsheet_effects_activate` | modify | Effects |
| `foxos spreadsheet margins activate` | `spreadsheet_margins_activate` | modify | Margins |
| `foxos spreadsheet size activate` | `spreadsheet_size_activate` | modify | Size |
| `foxos spreadsheet area print` | `spreadsheet_area_print` | read | Print Area |
| `foxos spreadsheet breaks activate` | `spreadsheet_breaks_activate` | modify | Breaks |
| `foxos spreadsheet sheet-background activate` | `spreadsheet_sheet-background_activate` | modify | Sheet Background |
| `foxos spreadsheet titles print` | `spreadsheet_titles_print` | read | Print Titles |
| `foxos spreadsheet page-setup activate` | `spreadsheet_page-setup_activate` | modify | Page Setup |
| `foxos spreadsheet pdf export` | `spreadsheet_pdf_export` | modify | Export PDF |
| `foxos spreadsheet width activate` | `spreadsheet_width_activate` | modify | Width |
| `foxos spreadsheet height activate` | `spreadsheet_height_activate` | modify | Height |
| `foxos spreadsheet scale activate` | `spreadsheet_scale_activate` | modify | Scale |
| `foxos spreadsheet gridlines activate` | `spreadsheet_gridlines_activate` | modify | Gridlines |
| `foxos spreadsheet gridlines print` | `spreadsheet_gridlines_print` | read | Print Gridlines |
| `foxos spreadsheet headings activate` | `spreadsheet_headings_activate` | modify | Headings |
| `foxos spreadsheet headings print` | `spreadsheet_headings_print` | read | Print Headings |
| `foxos spreadsheet bring-forward activate` | `spreadsheet_bring-forward_activate` | modify | Bring Forward |
| `foxos spreadsheet bring-forward-options activate` | `spreadsheet_bring-forward-options_activate` | modify | Bring Forward options |
| `foxos spreadsheet backward send` | `spreadsheet_backward_send` | modify | Send Backward |
| `foxos spreadsheet backward-options send` | `spreadsheet_backward-options_send` | modify | Send Backward options |
| `foxos spreadsheet selection-pane activate` | `spreadsheet_selection-pane_activate` | modify | Selection Pane |
| `foxos spreadsheet align align` | `spreadsheet_align_align` | modify | Align |
| `foxos spreadsheet group group` | `spreadsheet_group_group` | modify | Group |
| `foxos spreadsheet rotate rotate` | `spreadsheet_rotate_rotate` | modify | Rotate |
| `foxos spreadsheet recently-used activate` | `spreadsheet_recently-used_activate` | modify | Recently Used |
| `foxos spreadsheet financial-functions activate` | `spreadsheet_financial-functions_activate` | modify | Financial functions |
| `foxos spreadsheet logical-functions activate` | `spreadsheet_logical-functions_activate` | modify | Logical functions |
| `foxos spreadsheet text-functions activate` | `spreadsheet_text-functions_activate` | modify | Text functions |
| `foxos spreadsheet date-time-functions activate` | `spreadsheet_date-time-functions_activate` | modify | Date & Time functions |
| `foxos spreadsheet lookup-reference-functions activate` | `spreadsheet_lookup-reference-functions_activate` | modify | Lookup & Reference functions |
| `foxos spreadsheet math-trig-functions activate` | `spreadsheet_math-trig-functions_activate` | modify | Math & Trig functions |
| `foxos spreadsheet functions show` | `spreadsheet_functions_show` | read | More Functions |
| `foxos spreadsheet name-manager activate` | `spreadsheet_name-manager_activate` | modify | Name Manager |
| `foxos spreadsheet define-name activate` | `spreadsheet_define-name_activate` | modify | Define Name |
| `foxos spreadsheet use-formula activate` | `spreadsheet_use-formula_activate` | modify | Use in Formula |
| `foxos spreadsheet from-selection create` | `spreadsheet_from-selection_create` | modify | Create from Selection |
| `foxos spreadsheet trace-precedents activate` | `spreadsheet_trace-precedents_activate` | modify | Trace Precedents |
| `foxos spreadsheet trace-dependents activate` | `spreadsheet_trace-dependents_activate` | modify | Trace Dependents |
| `foxos spreadsheet arrows delete` | `spreadsheet_arrows_delete` | delete | Remove Arrows |
| `foxos spreadsheet formulas-2 show` | `spreadsheet_formulas-2_show` | read | Show Formulas |
| `foxos spreadsheet error-checking activate` | `spreadsheet_error-checking_activate` | modify | Error Checking |
| `foxos spreadsheet error-checking-options activate` | `spreadsheet_error-checking-options_activate` | modify | Error Checking options |
| `foxos spreadsheet evaluate-formula activate` | `spreadsheet_evaluate-formula_activate` | modify | Evaluate Formula |
| `foxos spreadsheet watch-window activate` | `spreadsheet_watch-window_activate` | modify | Watch Window |
| `foxos spreadsheet calculation-options activate` | `spreadsheet_calculation-options_activate` | modify | Calculation Options |
| `foxos spreadsheet now run` | `spreadsheet_now_run` | modify | Calculate Now |
| `foxos spreadsheet sheet run` | `spreadsheet_sheet_run` | modify | Calculate Sheet |
| `foxos spreadsheet formulas-values activate` | `spreadsheet_formulas-values_activate` | modify | Formulas to Values |
| `foxos spreadsheet get-data activate` | `spreadsheet_get-data_activate` | modify | Get Data |
| `foxos spreadsheet from-text-csv activate` | `spreadsheet_from-text-csv_activate` | modify | From Text/CSV |
| `foxos spreadsheet from-web activate` | `spreadsheet_from-web_activate` | modify | From Web |
| `foxos spreadsheet from-table-range activate` | `spreadsheet_from-table-range_activate` | modify | From Table/Range |
| `foxos spreadsheet refresh activate` | `spreadsheet_refresh_activate` | modify | Refresh All |
| `foxos spreadsheet refresh-options activate` | `spreadsheet_refresh-options_activate` | modify | Refresh All options |
| `foxos spreadsheet queries-connections activate` | `spreadsheet_queries-connections_activate` | modify | Queries & Connections |
| `foxos spreadsheet links update` | `spreadsheet_links_update` | modify | Edit Links |
| `foxos spreadsheet z sort` | `spreadsheet_z_sort` | read | Sort A to Z |
| `foxos spreadsheet data-z sort` | `spreadsheet_data-z_sort` | read | Sort Z to A |
| `foxos spreadsheet sort sort` | `spreadsheet_sort_sort` | read | Sort |
| `foxos spreadsheet data-filter filter` | `spreadsheet_data-filter_filter` | read | Filter |
| `foxos spreadsheet filter clear` | `spreadsheet_filter_clear` | modify | Clear filter |
| `foxos spreadsheet reapply activate` | `spreadsheet_reapply_activate` | modify | Reapply |
| `foxos spreadsheet advanced-filter activate` | `spreadsheet_advanced-filter_activate` | modify | Advanced filter |
| `foxos spreadsheet text-columns activate` | `spreadsheet_text-columns_activate` | modify | Text to Columns |
| `foxos spreadsheet flash-fill activate` | `spreadsheet_flash-fill_activate` | modify | Flash Fill |
| `foxos spreadsheet duplicates delete` | `spreadsheet_duplicates_delete` | delete | Remove Duplicates |
| `foxos spreadsheet data-validation activate` | `spreadsheet_data-validation_activate` | modify | Data Validation |
| `foxos spreadsheet data-validation-options activate` | `spreadsheet_data-validation-options_activate` | modify | Data Validation options |
| `foxos spreadsheet consolidate activate` | `spreadsheet_consolidate_activate` | modify | Consolidate |
| `foxos spreadsheet form activate` | `spreadsheet_form_activate` | modify | Form |
| `foxos spreadsheet data-cleanup activate` | `spreadsheet_data-cleanup_activate` | modify | Data Cleanup |
| `foxos spreadsheet what-if-analysis activate` | `spreadsheet_what-if-analysis_activate` | modify | What-If Analysis |
| `foxos spreadsheet goal-seek activate` | `spreadsheet_goal-seek_activate` | modify | Goal Seek |
| `foxos spreadsheet forecast-sheet activate` | `spreadsheet_forecast-sheet_activate` | modify | Forecast Sheet |
| `foxos spreadsheet column-stats activate` | `spreadsheet_column-stats_activate` | modify | Column Stats |
| `foxos spreadsheet data-analysis activate` | `spreadsheet_data-analysis_activate` | modify | Data Analysis |
| `foxos spreadsheet solver activate` | `spreadsheet_solver_activate` | modify | Solver |
| `foxos spreadsheet rows ungroup` | `spreadsheet_rows_ungroup` | modify | Ungroup Rows |
| `foxos spreadsheet subtotal activate` | `spreadsheet_subtotal_activate` | modify | Subtotal |
| `foxos spreadsheet detail show` | `spreadsheet_detail_show` | read | Show Detail |
| `foxos spreadsheet detail hide` | `spreadsheet_detail_hide` | read | Hide Detail |
| `foxos spreadsheet auto-outline activate` | `spreadsheet_auto-outline_activate` | modify | Auto Outline |
| `foxos spreadsheet outline clear` | `spreadsheet_outline_clear` | modify | Clear Outline |
| `foxos spreadsheet outline-settings activate` | `spreadsheet_outline-settings_activate` | modify | Outline Settings |
| `foxos spreadsheet review-spelling activate` | `spreadsheet_review-spelling_activate` | modify | Spelling |
| `foxos spreadsheet thesaurus activate` | `spreadsheet_thesaurus_activate` | modify | Thesaurus |
| `foxos spreadsheet spelling-as-you-type activate` | `spreadsheet_spelling-as-you-type_activate` | modify | Spelling as You Type |
| `foxos spreadsheet autocorrect-options activate` | `spreadsheet_autocorrect-options_activate` | modify | AutoCorrect Options |
| `foxos spreadsheet workbook-statistics activate` | `spreadsheet_workbook-statistics_activate` | modify | Workbook Statistics |
| `foxos spreadsheet translate activate` | `spreadsheet_translate_activate` | modify | Translate |
| `foxos spreadsheet comment create` | `spreadsheet_comment_create` | modify | New Comment |
| `foxos spreadsheet comment delete` | `spreadsheet_comment_delete` | delete | Delete Comment |
| `foxos spreadsheet comment previous` | `spreadsheet_comment_previous` | read | Previous Comment |
| `foxos spreadsheet comment next` | `spreadsheet_comment_next` | read | Next Comment |
| `foxos spreadsheet comments show` | `spreadsheet_comments_show` | read | Show Comments |
| `foxos spreadsheet note delete` | `spreadsheet_note_delete` | delete | Delete Note |
| `foxos spreadsheet notes-sheet select` | `spreadsheet_notes-sheet_select` | read | Select notes on this sheet |
| `foxos spreadsheet changes show` | `spreadsheet_changes_show` | read | Show Changes |
| `foxos spreadsheet protect-sheet activate` | `spreadsheet_protect-sheet_activate` | modify | Protect Sheet |
| `foxos spreadsheet protect-workbook activate` | `spreadsheet_protect-workbook_activate` | modify | Protect Workbook |
| `foxos spreadsheet protected-ranges activate` | `spreadsheet_protected-ranges_activate` | modify | Protected Ranges |
| `foxos spreadsheet share share` | `spreadsheet_share_share` | modify | Share |
| `foxos spreadsheet copy send` | `spreadsheet_copy_send` | modify | Send a Copy |
| `foxos spreadsheet version-history activate` | `spreadsheet_version-history_activate` | modify | Version History |
| `foxos spreadsheet normal-view activate` | `spreadsheet_normal-view_activate` | modify | Normal view |
| `foxos spreadsheet page-layout-view activate` | `spreadsheet_page-layout-view_activate` | modify | Page Layout view |
| `foxos spreadsheet custom-views activate` | `spreadsheet_custom-views_activate` | modify | Custom Views |
| `foxos spreadsheet sheet-view activate` | `spreadsheet_sheet-view_activate` | modify | Sheet View |
| `foxos spreadsheet sheet-view create` | `spreadsheet_sheet-view_create` | modify | New sheet view |
| `foxos spreadsheet keep-sheet-view activate` | `spreadsheet_keep-sheet-view_activate` | modify | Keep sheet view |
| `foxos spreadsheet exit-sheet-view activate` | `spreadsheet_exit-sheet-view_activate` | modify | Exit sheet view |
| `foxos spreadsheet options-sheet-view activate` | `spreadsheet_options-sheet-view_activate` | modify | Options sheet view |
| `foxos spreadsheet formula-bar activate` | `spreadsheet_formula-bar_activate` | modify | Formula Bar |
| `foxos spreadsheet zeros show` | `spreadsheet_zeros_show` | read | Show Zeros |
| `foxos spreadsheet page-breaks activate` | `spreadsheet_page-breaks_activate` | modify | Page Breaks |
| `foxos spreadsheet zoom zoom` | `spreadsheet_zoom_zoom` | read | Zoom |
| `foxos spreadsheet view-2 zoom-` | `spreadsheet_view-2_zoom-` | modify | Zoom to Selection |
| `foxos spreadsheet freeze-panes activate` | `spreadsheet_freeze-panes_activate` | modify | Freeze Panes |
| `foxos spreadsheet split activate` | `spreadsheet_split_activate` | modify | Split |
| `foxos spreadsheet unhide hide` | `spreadsheet_unhide_hide` | read | Hide & Unhide |
| `foxos spreadsheet focus-mode activate` | `spreadsheet_focus-mode_activate` | modify | Focus Mode |
| `foxos spreadsheet full-screen activate` | `spreadsheet_full-screen_activate` | modify | Full Screen |
| `foxos spreadsheet ai-assistant activate` | `spreadsheet_ai-assistant_activate` | modify | AI Assistant |
| `foxos spreadsheet actions record` | `spreadsheet_actions_record` | modify | Record Actions |
| `foxos spreadsheet script create` | `spreadsheet_script_create` | modify | New Script |
| `foxos spreadsheet scripts activate` | `spreadsheet_scripts_activate` | modify | All Scripts |
| `foxos spreadsheet code-editor activate` | `spreadsheet_code-editor_activate` | modify | Code Editor |
| `foxos spreadsheet script run` | `spreadsheet_script_run` | modify | Run a script |
| `foxos spreadsheet button-that-runs-script create` | `spreadsheet_button-that-runs-script_create` | modify | Insert a button that runs a script |
| `foxos spreadsheet highlight-duplicates-sample-script run` | `spreadsheet_highlight-duplicates-sample-script_run` | modify | Run the Highlight Duplicates sample script |
| `foxos spreadsheet unhide-everything-sample-script run` | `spreadsheet_unhide-everything-sample-script_run` | modify | Run the Unhide Everything sample script |
| `foxos spreadsheet sum-each-column-sample-script run` | `spreadsheet_sum-each-column-sample-script_run` | modify | Run the Sum Each Column sample script |
| `foxos spreadsheet table-contents-sample-script run` | `spreadsheet_table-contents-sample-script_run` | modify | Run the Table of Contents sample script |
| `foxos spreadsheet style-header-row-sample-script run` | `spreadsheet_style-header-row-sample-script_run` | modify | Run the Style Header Row sample script |
| `foxos spreadsheet remove-blank-rows-sample-script run` | `spreadsheet_remove-blank-rows-sample-script_run` | modify | Run the Remove Blank Rows sample script |
| `foxos spreadsheet script-reference activate` | `spreadsheet_script-reference_activate` | modify | Script Reference |
| `foxos spreadsheet paste-options-paste paste` | `spreadsheet_paste-options-paste_paste` | modify | Paste |
| `foxos spreadsheet formulas activate` | `spreadsheet_formulas_activate` | modify | Formulas |
| `foxos spreadsheet formulas-number-formatting activate` | `spreadsheet_formulas-number-formatting_activate` | modify | Formulas & Number Formatting |
| `foxos spreadsheet keep-source-formatting activate` | `spreadsheet_keep-source-formatting_activate` | modify | Keep Source Formatting |
| `foxos spreadsheet no-borders activate` | `spreadsheet_no-borders_activate` | modify | No Borders |
| `foxos spreadsheet keep-source-column-widths activate` | `spreadsheet_keep-source-column-widths_activate` | modify | Keep Source Column Widths |
| `foxos spreadsheet transpose activate` | `spreadsheet_transpose_activate` | modify | Transpose |
| `foxos spreadsheet values activate` | `spreadsheet_values_activate` | modify | Values |
| `foxos spreadsheet values-number-formatting activate` | `spreadsheet_values-number-formatting_activate` | modify | Values & Number Formatting |
| `foxos spreadsheet values-source-formatting activate` | `spreadsheet_values-source-formatting_activate` | modify | Values & Source Formatting |
| `foxos spreadsheet formatting activate` | `spreadsheet_formatting_activate` | modify | Formatting |
| `foxos spreadsheet link paste` | `spreadsheet_link_paste` | modify | Paste Link |
| `foxos spreadsheet picture activate` | `spreadsheet_picture_activate` | modify | Picture |
| `foxos spreadsheet linked-picture activate` | `spreadsheet_linked-picture_activate` | modify | Linked Picture |
| `foxos spreadsheet special paste` | `spreadsheet_special_paste` | modify | Paste Special… |
| `foxos spreadsheet default activate` | `spreadsheet_default_activate` | modify | Default |
| `foxos spreadsheet arial activate` | `spreadsheet_arial_activate` | modify | Arial |
| `foxos spreadsheet arial-black activate` | `spreadsheet_arial-black_activate` | modify | Arial Black |
| `foxos spreadsheet calibri activate` | `spreadsheet_calibri_activate` | modify | Calibri |
| `foxos spreadsheet cambria activate` | `spreadsheet_cambria_activate` | modify | Cambria |
| `foxos spreadsheet aharoni activate` | `spreadsheet_aharoni_activate` | modify | Aharoni |
| `foxos spreadsheet avenir-next-lt-pro activate` | `spreadsheet_avenir-next-lt-pro_activate` | modify | Avenir Next LT Pro |
| `foxos spreadsheet century-gothic activate` | `spreadsheet_century-gothic_activate` | modify | Century Gothic |
| `foxos spreadsheet constantia activate` | `spreadsheet_constantia_activate` | modify | Constantia |
| `foxos spreadsheet corbel activate` | `spreadsheet_corbel_activate` | modify | Corbel |
| `foxos spreadsheet helvetica activate` | `spreadsheet_helvetica_activate` | modify | Helvetica |
| `foxos spreadsheet impact activate` | `spreadsheet_impact_activate` | modify | Impact |
| `foxos spreadsheet lato activate` | `spreadsheet_lato_activate` | modify | Lato |
| `foxos spreadsheet lato-light activate` | `spreadsheet_lato-light_activate` | modify | Lato Light |
| `foxos spreadsheet lucida-sans activate` | `spreadsheet_lucida-sans_activate` | modify | Lucida Sans |
| `foxos spreadsheet nyala activate` | `spreadsheet_nyala_activate` | modify | Nyala |
| `foxos spreadsheet sans-semibold open` | `spreadsheet_sans-semibold_open` | read | Open Sans Semibold |
| `foxos spreadsheet segoe-ui activate` | `spreadsheet_segoe-ui_activate` | modify | Segoe UI |
| `foxos spreadsheet source-sans-pro activate` | `spreadsheet_source-sans-pro_activate` | modify | Source Sans Pro |
| `foxos spreadsheet tahoma activate` | `spreadsheet_tahoma_activate` | modify | Tahoma |
| `foxos spreadsheet verdana activate` | `spreadsheet_verdana_activate` | modify | Verdana |
| `foxos spreadsheet trebuchet-ms activate` | `spreadsheet_trebuchet-ms_activate` | modify | Trebuchet MS |
| `foxos spreadsheet georgia activate` | `spreadsheet_georgia_activate` | modify | Georgia |
| `foxos spreadsheet rockwell activate` | `spreadsheet_rockwell_activate` | modify | Rockwell |
| `foxos spreadsheet times-roman activate` | `spreadsheet_times-roman_activate` | modify | Times New Roman |
| `foxos spreadsheet garamond activate` | `spreadsheet_garamond_activate` | modify | Garamond |
| `foxos spreadsheet courier activate` | `spreadsheet_courier_activate` | modify | Courier New |
| `foxos spreadsheet monospace activate` | `spreadsheet_monospace_activate` | modify | Monospace |
| `foxos spreadsheet comic-sans-ms activate` | `spreadsheet_comic-sans-ms_activate` | modify | Comic Sans MS |
| `foxos spreadsheet document search` | `spreadsheet_document_search` | read | 快捷键 mod+f |
| `foxos spreadsheet selection group` | `spreadsheet_selection_group` | modify | 快捷键 mod+g |
| `foxos spreadsheet view toggle-help` | `spreadsheet_view_toggle-help` | modify | 快捷键 mod+h |
| `foxos spreadsheet shortcut key-q` | `spreadsheet_shortcut_key-q` | modify | 快捷键 mod+q |
| `foxos spreadsheet document save` | `spreadsheet_document_save` | modify | 快捷键 mod+s |

### documents（`documents`，310 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos documents search search TARGET` | `documents_search_search` | read | search for *（1 项，如 Search for commands） |
| `foxos documents editing-mode select TARGET` | `documents_editing-mode_select` | read | editing mode: *（1 项，如 Editing mode: Editing） |
| `foxos documents account-menu select TARGET` | `documents_account-menu_select` | read | account menu for *（1 项，如 Account menu for local） |
| `foxos documents font-size select TARGET` | `documents_font-size_select` | read | # font size（1 项，如 Decrease Font Size） |
| `foxos documents indent select TARGET` | `documents_indent_select` | read | # indent（1 项，如 Decrease Indent） |
| `foxos documents formatting show TARGET` | `documents_formatting_show` | read | show formatting #（1 项，如 Show Formatting Marks） |
| `foxos documents heading select TARGET` | `documents_heading_select` | read | heading #（5 项，如 Heading 1） |
| `foxos documents left select TARGET` | `documents_left_select` | read | left #（1 项，如 Left margin） |
| `foxos documents right select TARGET` | `documents_right_select` | read | right #（1 项，如 Right margin） |
| `foxos documents top select TARGET` | `documents_top_select` | read | top #（1 项，如 Top margin） |
| `foxos documents bottom select TARGET` | `documents_bottom_select` | read | bottom #（1 项，如 Bottom margin） |
| `foxos documents spelling select TARGET` | `documents_spelling_select` | read | spelling: *（1 项，如 Spelling: no errors） |
| `foxos documents accessibility select TARGET` | `documents_accessibility_select` | read | accessibility: *（1 项，如 Accessibility: good to go. Open the Accessibility pane.） |
| `foxos documents customize-quick-access-toolbar-formatting show TARGET` | `documents_customize-quick-access-toolbar-formatting_show` | read | show formatting #（1 项，如 Show Formatting Marks） |
| `foxos documents pen select TARGET` | `documents_pen_select` | read | pen: *（3 项，如 Pen: Black, 0.5 mm） |
| `foxos documents pencil select TARGET` | `documents_pencil_select` | read | pencil: *（1 项，如 Pencil: #595959, 1 mm） |
| `foxos documents highlighter select TARGET` | `documents_highlighter_select` | read | highlighter: *（1 项，如 Highlighter: Yellow, 6 mm） |
| `foxos documents check run TARGET` | `documents_check_run` | modify | check for *（1 项，如 Check for Errors） |
| `foxos documents autosave toggle` | `documents_autosave_toggle` | modify | AutoSave |
| `foxos documents documents activate` | `documents_documents_activate` | modify | All Documents |
| `foxos documents save save` | `documents_save_save` | modify | Save |
| `foxos documents undo undo` | `documents_undo_undo` | modify | Undo |
| `foxos documents history undo` | `documents_history_undo` | modify | Undo history |
| `foxos documents redo redo` | `documents_redo_redo` | modify | Redo |
| `foxos documents print print` | `documents_print_print` | read | Print |
| `foxos documents customize-quick-access-toolbar activate` | `documents_customize-quick-access-toolbar_activate` | modify | Customize Quick Access Toolbar |
| `foxos documents edit update` | `documents_edit_update` | modify | Edit |
| `foxos documents view show` | `documents_view_show` | read | View |
| `foxos documents insert create` | `documents_insert_create` | modify | Insert |
| `foxos documents format activate` | `documents_format_activate` | modify | Format |
| `foxos documents tools activate` | `documents_tools_activate` | modify | Tools |
| `foxos documents table activate` | `documents_table_activate` | modify | Table |
| `foxos documents window activate` | `documents_window_activate` | modify | Window |
| `foxos documents help show` | `documents_help_show` | read | Help |
| `foxos documents document-name set VALUE [--submit]` | `documents_document-name_set` | modify | Document name |
| `foxos documents document-details activate` | `documents_document-details_activate` | modify | Document details |
| `foxos documents not-saved-yet activate` | `documents_not-saved-yet_activate` | modify | Not saved yet |
| `foxos documents assistant activate` | `documents_assistant_activate` | modify | Assistant |
| `foxos documents comments activate` | `documents_comments_activate` | modify | Comments |
| `foxos documents share share` | `documents_share_share` | modify | Share |
| `foxos documents file-2 activate` | `documents_file-2_activate` | modify | File |
| `foxos documents home show` | `documents_home_show` | read | Home |
| `foxos documents insert-2 create` | `documents_insert-2_create` | modify | Insert |
| `foxos documents draw draw` | `documents_draw_draw` | modify | Draw |
| `foxos documents design show` | `documents_design_show` | read | Design |
| `foxos documents layout show` | `documents_layout_show` | read | Layout |
| `foxos documents references show` | `documents_references_show` | read | References |
| `foxos documents mailings show` | `documents_mailings_show` | read | Mailings |
| `foxos documents review show` | `documents_review_show` | read | Review |
| `foxos documents view-2 show` | `documents_view-2_show` | read | View |
| `foxos documents ribbon-display-options activate` | `documents_ribbon-display-options_activate` | modify | Ribbon display options |
| `foxos documents ribbon collapse` | `documents_ribbon_collapse` | read | Collapse the ribbon |
| `foxos documents paste paste` | `documents_paste_paste` | modify | Paste |
| `foxos documents options paste` | `documents_options_paste` | modify | Paste options |
| `foxos documents cut cut` | `documents_cut_cut` | modify | Cut |
| `foxos documents copy copy` | `documents_copy_copy` | modify | Copy |
| `foxos documents format-painter activate` | `documents_format-painter_activate` | modify | Format Painter |
| `foxos documents latin-font-family activate` | `documents_latin-font-family_activate` | modify | Latin font family |
| `foxos documents font-size-pt set VALUE [--submit]` | `documents_font-size-pt_set` | modify | Font size (pt) |
| `foxos documents font-sizes activate` | `documents_font-sizes_activate` | modify | Font sizes |
| `foxos documents increase-font-size activate` | `documents_increase-font-size_activate` | modify | Increase Font Size |
| `foxos documents case update` | `documents_case_update` | modify | Change Case |
| `foxos documents formatting clear` | `documents_formatting_clear` | modify | Clear All Formatting |
| `foxos documents bold format` | `documents_bold_format` | modify | Bold |
| `foxos documents italic format` | `documents_italic_format` | modify | Italic |
| `foxos documents underline format` | `documents_underline_format` | modify | Underline |
| `foxos documents options format` | `documents_options_format` | modify | Underline options |
| `foxos documents strikethrough format` | `documents_strikethrough_format` | modify | Strikethrough |
| `foxos documents subscript activate` | `documents_subscript_activate` | modify | Subscript |
| `foxos documents superscript activate` | `documents_superscript_activate` | modify | Superscript |
| `foxos documents text-effects activate` | `documents_text-effects_activate` | modify | Text Effects |
| `foxos documents text-highlight activate` | `documents_text-highlight_activate` | modify | Text highlight |
| `foxos documents text-color activate` | `documents_text-color_activate` | modify | Text color |
| `foxos documents font-settings activate` | `documents_font-settings_activate` | modify | Font Settings |
| `foxos documents bulleted-list activate` | `documents_bulleted-list_activate` | modify | Bulleted list |
| `foxos documents bullet-library activate` | `documents_bullet-library_activate` | modify | Bullet Library |
| `foxos documents numbered-list activate` | `documents_numbered-list_activate` | modify | Numbered list |
| `foxos documents numbering-library activate` | `documents_numbering-library_activate` | modify | Numbering Library |
| `foxos documents multilevel-list activate` | `documents_multilevel-list_activate` | modify | Multilevel List |
| `foxos documents increase-indent activate` | `documents_increase-indent_activate` | modify | Increase Indent |
| `foxos documents sort sort` | `documents_sort_sort` | read | Sort |
| `foxos documents left align` | `documents_left_align` | modify | Align left |
| `foxos documents center align` | `documents_center_align` | modify | Align center |
| `foxos documents right align` | `documents_right_align` | modify | Align right |
| `foxos documents justify activate` | `documents_justify_activate` | modify | Justify |
| `foxos documents line-paragraph-spacing activate` | `documents_line-paragraph-spacing_activate` | modify | Line and Paragraph Spacing |
| `foxos documents paragraph-shading activate` | `documents_paragraph-shading_activate` | modify | Paragraph shading |
| `foxos documents borders activate` | `documents_borders_activate` | modify | Borders |
| `foxos documents border-options activate` | `documents_border-options_activate` | modify | Border options |
| `foxos documents paragraph-settings activate` | `documents_paragraph-settings_activate` | modify | Paragraph Settings |
| `foxos documents normal activate` | `documents_normal_activate` | modify | Normal |
| `foxos documents title activate` | `documents_title_activate` | modify | Title |
| `foxos documents subtitle activate` | `documents_subtitle_activate` | modify | Subtitle |
| `foxos documents styles show` | `documents_styles_show` | read | More Styles |
| `foxos documents styles-pane activate` | `documents_styles-pane_activate` | modify | Styles Pane |
| `foxos documents formatting-pane activate` | `documents_formatting-pane_activate` | modify | Formatting Pane |
| `foxos documents dictate activate` | `documents_dictate_activate` | modify | Dictate |
| `foxos documents find search` | `documents_find_search` | read | Find |
| `foxos documents options search` | `documents_options_search` | read | Find options |
| `foxos documents replace activate` | `documents_replace_activate` | modify | Replace |
| `foxos documents select select` | `documents_select_select` | read | Select |
| `foxos documents left-indent set VALUE [--submit]` | `documents_left-indent_set` | modify | Left indent |
| `foxos documents hanging-indent set VALUE [--submit]` | `documents_hanging-indent_set` | modify | Hanging indent |
| `foxos documents first-line-indent set VALUE [--submit]` | `documents_first-line-indent_set` | modify | First line indent |
| `foxos documents right-indent set VALUE [--submit]` | `documents_right-indent_set` | modify | Right indent |
| `foxos documents document-text set VALUE [--submit]` | `documents_document-text_set` | modify | Document text |
| `foxos documents go-ctrlg activate` | `documents_go-ctrlg_activate` | modify | Go To (Ctrl+G) |
| `foxos documents word-count activate` | `documents_word-count_activate` | modify | Word Count |
| `foxos documents language activate` | `documents_language_activate` | modify | Language |
| `foxos documents text-mode toggle` | `documents_text-mode_toggle` | modify | Text mode |
| `foxos documents focus activate` | `documents_focus_activate` | modify | Focus |
| `foxos documents read-mode activate` | `documents_read-mode_activate` | modify | Read Mode |
| `foxos documents layout print` | `documents_layout_print` | read | Print Layout |
| `foxos documents web-layout activate` | `documents_web-layout_activate` | modify | Web Layout |
| `foxos documents outline activate` | `documents_outline_activate` | modify | Outline |
| `foxos documents draft activate` | `documents_draft_activate` | modify | Draft |
| `foxos documents view zoom-out` | `documents_view_zoom-out` | modify | Zoom Out |
| `foxos documents zoom-slider set VALUE [--submit]` | `documents_zoom-slider_set` | modify | Zoom slider |
| `foxos documents view zoom-` | `documents_view_zoom-` | modify | Zoom In |
| `foxos documents zoom set VALUE [--submit]` | `documents_zoom_set` | modify | Zoom |
| `foxos documents customize-quick-access-toolbar-documents activate` | `documents_customize-quick-access-toolbar-documents_activate` | modify | All Documents |
| `foxos documents customize-quick-access-toolbar-save save` | `documents_customize-quick-access-toolbar-save_save` | modify | Save |
| `foxos documents customize-quick-access-toolbar-undo undo` | `documents_customize-quick-access-toolbar-undo_undo` | modify | Undo |
| `foxos documents customize-quick-access-toolbar-redo redo` | `documents_customize-quick-access-toolbar-redo_redo` | modify | Redo |
| `foxos documents customize-quick-access-toolbar-print print` | `documents_customize-quick-access-toolbar-print_print` | read | Print |
| `foxos documents document create` | `documents_document_create` | modify | New Document |
| `foxos documents open open` | `documents_open_open` | read | Open |
| `foxos documents customize-quick-access-toolbar-find search` | `documents_customize-quick-access-toolbar-find_search` | read | Find |
| `foxos documents spelling activate` | `documents_spelling_activate` | modify | Spelling |
| `foxos documents as-pdf save` | `documents_as-pdf_save` | modify | Save as PDF |
| `foxos documents comment create` | `documents_comment_create` | modify | New Comment |
| `foxos documents track-changes activate` | `documents_track-changes_activate` | modify | Track Changes |
| `foxos documents customize-quick-access-toolbar-word-count activate` | `documents_customize-quick-access-toolbar-word-count_activate` | modify | Word Count |
| `foxos documents read-aloud activate` | `documents_read-aloud_activate` | modify | Read Aloud |
| `foxos documents repeat activate` | `documents_repeat_activate` | modify | Repeat |
| `foxos documents defaults reset` | `documents_defaults_reset` | modify | Reset to Defaults |
| `foxos documents document close` | `documents_document_close` | read | Close document |
| `foxos documents file-name set VALUE [--submit]` | `documents_file-name_set` | modify | File name |
| `foxos documents version-history activate` | `documents_version-history_activate` | modify | Version History |
| `foxos documents properties activate` | `documents_properties_activate` | modify | Properties |
| `foxos documents rename rename` | `documents_rename_rename` | modify | Rename |
| `foxos documents editingedit-document-directly activate` | `documents_editingedit-document-directly_activate` | modify | EditingEdit the document directly. |
| `foxos documents reviewingedits-become-tracked-changes activate` | `documents_reviewingedits-become-tracked-changes_activate` | modify | ReviewingEdits become tracked changes. |
| `foxos documents people invite` | `documents_people_invite` | modify | Invite People… |
| `foxos documents link copy` | `documents_link_copy` | modify | Copy Link |
| `foxos documents publish-web activate` | `documents_publish-web_activate` | modify | Publish to the Web… |
| `foxos documents copy-docx send` | `documents_copy-docx_send` | modify | Send a Copy (.docx) |
| `foxos documents as-pdf send` | `documents_as-pdf_send` | modify | Send as PDF |
| `foxos documents system toggle` | `documents_system_toggle` | modify | System |
| `foxos documents light toggle` | `documents_light_toggle` | modify | Light |
| `foxos documents dark toggle` | `documents_dark_toggle` | modify | Dark |
| `foxos documents dark-pagedark-paper-dark-theme activate` | `documents_dark-pagedark-paper-dark-theme_activate` | modify | Dark pageDark paper with the dark theme |
| `foxos documents measurement-unitsinches activate` | `documents_measurement-unitsinches_activate` | modify | Measurement unitsInches |
| `foxos documents capitalize-first-letter-sentences activate` | `documents_capitalize-first-letter-sentences_activate` | modify | Capitalize the first letter of sentences |
| `foxos documents keyboard-shortcuts activate` | `documents_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos documents documents show` | `documents_documents_show` | read | About Documents |
| `foxos documents document previous` | `documents_document_previous` | read | Back to the document |
| `foxos documents file-open open` | `documents_file-open_open` | read | Open |
| `foxos documents info show` | `documents_info_show` | read | Info |
| `foxos documents file-save save` | `documents_file-save_save` | modify | Save |
| `foxos documents file-print print` | `documents_file-print_print` | read | Print |
| `foxos documents file-share share` | `documents_file-share_share` | modify | Share |
| `foxos documents export export` | `documents_export_export` | modify | Export |
| `foxos documents close close` | `documents_close_close` | read | Close |
| `foxos documents preferences activate` | `documents_preferences_activate` | modify | Preferences |
| `foxos documents title set VALUE [--submit]` | `documents_title_set` | modify | Title |
| `foxos documents subject set VALUE [--submit]` | `documents_subject_set` | modify | Subject |
| `foxos documents author set VALUE [--submit]` | `documents_author_set` | modify | Author |
| `foxos documents keywords set VALUE [--submit]` | `documents_keywords_set` | modify | Keywords |
| `foxos documents category set VALUE [--submit]` | `documents_category_set` | modify | Category |
| `foxos documents status set VALUE [--submit]` | `documents_status_set` | modify | Status |
| `foxos documents comments set VALUE [--submit]` | `documents_comments_set` | modify | Comments |
| `foxos documents properties save` | `documents_properties_save` | modify | Save Properties |
| `foxos documents only show` | `documents_only_show` | read | View Only |
| `foxos documents cover-page activate` | `documents_cover-page_activate` | modify | Cover Page |
| `foxos documents blank-page activate` | `documents_blank-page_activate` | modify | Blank Page |
| `foxos documents page-break activate` | `documents_page-break_activate` | modify | Page break |
| `foxos documents table create` | `documents_table_create` | modify | Insert table |
| `foxos documents pictures activate` | `documents_pictures_activate` | modify | Pictures |
| `foxos documents shapes activate` | `documents_shapes_activate` | modify | Shapes |
| `foxos documents icons activate` | `documents_icons_activate` | modify | Icons |
| `foxos documents diagram activate` | `documents_diagram_activate` | modify | Diagram |
| `foxos documents chart activate` | `documents_chart_activate` | modify | Chart |
| `foxos documents or-edit-link create` | `documents_or-edit-link_create` | modify | Insert or edit link |
| `foxos documents bookmarks activate` | `documents_bookmarks_activate` | modify | Bookmarks |
| `foxos documents insert-comment create` | `documents_insert-comment_create` | modify | New Comment |
| `foxos documents header activate` | `documents_header_activate` | modify | Header |
| `foxos documents footer activate` | `documents_footer_activate` | modify | Footer |
| `foxos documents page-number activate` | `documents_page-number_activate` | modify | Page Number |
| `foxos documents text-box activate` | `documents_text-box_activate` | modify | Text Box |
| `foxos documents quick-parts activate` | `documents_quick-parts_activate` | modify | Quick Parts |
| `foxos documents wordart activate` | `documents_wordart_activate` | modify | WordArt |
| `foxos documents drop-cap activate` | `documents_drop-cap_activate` | modify | Drop Cap |
| `foxos documents signature-line activate` | `documents_signature-line_activate` | modify | Signature Line |
| `foxos documents date-time activate` | `documents_date-time_activate` | modify | Date & Time |
| `foxos documents object activate` | `documents_object_activate` | modify | Object |
| `foxos documents symbols activate` | `documents_symbols_activate` | modify | Symbols |
| `foxos documents lasso-select activate` | `documents_lasso-select_activate` | modify | Lasso Select |
| `foxos documents eraser activate` | `documents_eraser_activate` | modify | Eraser |
| `foxos documents eraser-options activate` | `documents_eraser-options_activate` | modify | Eraser options |
| `foxos documents pen create` | `documents_pen_create` | modify | Add Pen |
| `foxos documents touch draw` | `documents_touch_draw` | modify | Draw with Touch |
| `foxos documents ruler activate` | `documents_ruler_activate` | modify | Ruler |
| `foxos documents ink-shape activate` | `documents_ink-shape_activate` | modify | Ink to Shape |
| `foxos documents ink-math activate` | `documents_ink-math_activate` | modify | Ink to Math |
| `foxos documents drawing-canvas activate` | `documents_drawing-canvas_activate` | modify | Drawing Canvas |
| `foxos documents ink-replay activate` | `documents_ink-replay_activate` | modify | Ink Replay |
| `foxos documents ink hide` | `documents_ink_hide` | read | Hide Ink |
| `foxos documents themes activate` | `documents_themes_activate` | modify | Themes |
| `foxos documents default-style-set activate` | `documents_default-style-set_activate` | modify | Default style set |
| `foxos documents crisp-style-set activate` | `documents_crisp-style-set_activate` | modify | Crisp style set |
| `foxos documents classic-style-set activate` | `documents_classic-style-set_activate` | modify | Classic style set |
| `foxos documents banner-style-set activate` | `documents_banner-style-set_activate` | modify | Banner style set |
| `foxos documents minimal-style-set activate` | `documents_minimal-style-set_activate` | modify | Minimal style set |
| `foxos documents accent-bar-style-set activate` | `documents_accent-bar-style-set_activate` | modify | Accent Bar style set |
| `foxos documents centered-style-set activate` | `documents_centered-style-set_activate` | modify | Centered style set |
| `foxos documents contrast-style-set format` | `documents_contrast-style-set_format` | modify | Bold Contrast style set |
| `foxos documents style-sets show` | `documents_style-sets_show` | read | More Style Sets |
| `foxos documents theme-colors activate` | `documents_theme-colors_activate` | modify | Theme Colors |
| `foxos documents theme-fonts activate` | `documents_theme-fonts_activate` | modify | Theme Fonts |
| `foxos documents paragraph-spacing activate` | `documents_paragraph-spacing_activate` | modify | Paragraph Spacing |
| `foxos documents theme-effects activate` | `documents_theme-effects_activate` | modify | Theme Effects |
| `foxos documents set-as-default activate` | `documents_set-as-default_activate` | modify | Set as Default |
| `foxos documents watermark activate` | `documents_watermark_activate` | modify | Watermark |
| `foxos documents page-color activate` | `documents_page-color_activate` | modify | Page Color |
| `foxos documents page-borders activate` | `documents_page-borders_activate` | modify | Page Borders |
| `foxos documents margins activate` | `documents_margins_activate` | modify | Margins |
| `foxos documents orientation activate` | `documents_orientation_activate` | modify | Orientation |
| `foxos documents size activate` | `documents_size_activate` | modify | Size |
| `foxos documents columns activate` | `documents_columns_activate` | modify | Columns |
| `foxos documents breaks activate` | `documents_breaks_activate` | modify | Breaks |
| `foxos documents line-numbers activate` | `documents_line-numbers_activate` | modify | Line Numbers |
| `foxos documents hyphenation activate` | `documents_hyphenation_activate` | modify | Hyphenation |
| `foxos documents page-setup activate` | `documents_page-setup_activate` | modify | Page setup |
| `foxos documents indent-left set VALUE [--submit]` | `documents_indent-left_set` | modify | Indent left (in) |
| `foxos documents indent-right set VALUE [--submit]` | `documents_indent-right_set` | modify | Indent right (in) |
| `foxos documents space-before-paragraph-pt set VALUE [--submit]` | `documents_space-before-paragraph-pt_set` | modify | Space before paragraph (pt) |
| `foxos documents space-after-paragraph-pt set VALUE [--submit]` | `documents_space-after-paragraph-pt_set` | modify | Space after paragraph (pt) |
| `foxos documents position activate` | `documents_position_activate` | modify | Position |
| `foxos documents wrap-text activate` | `documents_wrap-text_activate` | modify | Wrap Text |
| `foxos documents bring-forward activate` | `documents_bring-forward_activate` | modify | Bring Forward |
| `foxos documents bring-forward-options activate` | `documents_bring-forward-options_activate` | modify | Bring Forward options |
| `foxos documents backward send` | `documents_backward_send` | modify | Send Backward |
| `foxos documents backward-options send` | `documents_backward-options_send` | modify | Send Backward options |
| `foxos documents selection-pane activate` | `documents_selection-pane_activate` | modify | Selection Pane |
| `foxos documents align align` | `documents_align_align` | modify | Align |
| `foxos documents group group` | `documents_group_group` | modify | Group |
| `foxos documents rotate rotate` | `documents_rotate_rotate` | modify | Rotate |
| `foxos documents table-contents activate` | `documents_table-contents_activate` | modify | Table of Contents |
| `foxos documents text create` | `documents_text_create` | modify | Add Text |
| `foxos documents table update` | `documents_table_update` | modify | Update Table |
| `foxos documents fields update` | `documents_fields_update` | modify | Update Fields |
| `foxos documents footnote create` | `documents_footnote_create` | modify | Insert Footnote |
| `foxos documents endnote create` | `documents_endnote_create` | modify | Insert Endnote |
| `foxos documents footnote next` | `documents_footnote_next` | read | Next Footnote |
| `foxos documents notes show` | `documents_notes_show` | read | Show Notes |
| `foxos documents footnote-endnote-settings activate` | `documents_footnote-endnote-settings_activate` | modify | Footnote and Endnote Settings |
| `foxos documents smart-lookup activate` | `documents_smart-lookup_activate` | modify | Smart Lookup |
| `foxos documents citation create` | `documents_citation_create` | modify | Insert Citation |
| `foxos documents manage-sources activate` | `documents_manage-sources_activate` | modify | Manage Sources |
| `foxos documents citation-style set VALUE [--submit]` | `documents_citation-style_set` | modify | Citation style |
| `foxos documents bibliography activate` | `documents_bibliography_activate` | modify | Bibliography |
| `foxos documents caption create` | `documents_caption_create` | modify | Insert Caption |
| `foxos documents table-figures create` | `documents_table-figures_create` | modify | Insert Table of Figures |
| `foxos documents table-figures update` | `documents_table-figures_update` | modify | Update Table of Figures |
| `foxos documents cross-reference activate` | `documents_cross-reference_activate` | modify | Cross-reference |
| `foxos documents index activate` | `documents_index_activate` | modify | Index |
| `foxos documents table-authorities activate` | `documents_table-authorities_activate` | modify | Table of Authorities |
| `foxos documents create create` | `documents_create_create` | modify | Create |
| `foxos documents mail-merge start` | `documents_mail-merge_start` | modify | Start Mail Merge |
| `foxos documents recipients select` | `documents_recipients_select` | read | Select Recipients |
| `foxos documents recipient-list update` | `documents_recipient-list_update` | modify | Edit Recipient List |
| `foxos documents highlight-merge-fields activate` | `documents_highlight-merge-fields_activate` | modify | Highlight Merge Fields |
| `foxos documents address-block activate` | `documents_address-block_activate` | modify | Address Block |
| `foxos documents greeting-line activate` | `documents_greeting-line_activate` | modify | Greeting Line |
| `foxos documents merge-field create` | `documents_merge-field_create` | modify | Insert Merge Field |
| `foxos documents rules activate` | `documents_rules_activate` | modify | Rules |
| `foxos documents match-fields activate` | `documents_match-fields_activate` | modify | Match Fields |
| `foxos documents labels update` | `documents_labels_update` | modify | Update Labels |
| `foxos documents preview-results activate` | `documents_preview-results_activate` | modify | Preview Results |
| `foxos documents first-record activate` | `documents_first-record_activate` | modify | First Record |
| `foxos documents record previous` | `documents_record_previous` | read | Previous Record |
| `foxos documents go-record set VALUE [--submit]` | `documents_go-record_set` | modify | Go to record |
| `foxos documents record next` | `documents_record_next` | read | Next Record |
| `foxos documents last-record activate` | `documents_last-record_activate` | modify | Last Record |
| `foxos documents recipient search` | `documents_recipient_search` | read | Find Recipient |
| `foxos documents finish-merge activate` | `documents_finish-merge_activate` | modify | Finish & Merge |
| `foxos documents editor activate` | `documents_editor_activate` | modify | Editor |
| `foxos documents spelling-options activate` | `documents_spelling-options_activate` | modify | Spelling options |
| `foxos documents thesaurus activate` | `documents_thesaurus_activate` | modify | Thesaurus |
| `foxos documents review-word-count activate` | `documents_review-word-count_activate` | modify | Word Count |
| `foxos documents review-read-aloud activate` | `documents_review-read-aloud_activate` | modify | Read Aloud |
| `foxos documents accessibility run` | `documents_accessibility_run` | modify | Check Accessibility |
| `foxos documents review-language activate` | `documents_review-language_activate` | modify | Language |
| `foxos documents comment delete` | `documents_comment_delete` | delete | Delete Comment |
| `foxos documents options delete` | `documents_options_delete` | delete | Delete options |
| `foxos documents comment previous` | `documents_comment_previous` | read | Previous Comment |
| `foxos documents comment next` | `documents_comment_next` | read | Next Comment |
| `foxos documents resolve-comment activate` | `documents_resolve-comment_activate` | modify | Resolve Comment |
| `foxos documents comments show` | `documents_comments_show` | read | Show Comments |
| `foxos documents comments-options show` | `documents_comments-options_show` | read | Show Comments options |
| `foxos documents tracking activate` | `documents_tracking_activate` | modify | Tracking |
| `foxos documents accept activate` | `documents_accept_activate` | modify | Accept |
| `foxos documents accept-options activate` | `documents_accept-options_activate` | modify | Accept options |
| `foxos documents reject activate` | `documents_reject_activate` | modify | Reject |
| `foxos documents reject-options activate` | `documents_reject-options_activate` | modify | Reject options |
| `foxos documents change previous` | `documents_change_previous` | read | Previous Change |
| `foxos documents change next` | `documents_change_next` | read | Next Change |
| `foxos documents compare activate` | `documents_compare_activate` | modify | Compare |
| `foxos documents restrict-editing activate` | `documents_restrict-editing_activate` | modify | Restrict Editing |

### presentation（`presentation`，283 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos presentation search search TARGET` | `presentation_search_search` | read | search for *（1 项，如 Search for commands） |
| `foxos presentation local select TARGET` | `presentation_local_select` | read | local: *（1 项，如 local: account and settings） |
| `foxos presentation font-size select TARGET` | `presentation_font-size_select` | read | # font size（1 项，如 Decrease Font Size） |
| `foxos presentation list-level select TARGET` | `presentation_list-level_select` | read | # list level（1 项，如 Decrease List Level） |
| `foxos presentation slide-1 select TARGET` | `presentation_slide-1_select` | read | slide 1: *（1 项，如 Slide 1: Blank） |
| `foxos presentation options select TARGET` | `presentation_options_select` | read | options for *（1 项，如 Options for slide 1） |
| `foxos presentation centered-title-select-edit select TARGET` | `presentation_centered-title-select-edit_select` | read | centered title # select to edit（1 项，如 Centered Title 1. Select to edit） |
| `foxos presentation subtitle-select-edit select TARGET` | `presentation_subtitle-select-edit_select` | read | subtitle # select to edit（1 项，如 Subtitle 2. Select to edit） |
| `foxos presentation draft-6-slide-pitch-deck select TARGET` | `presentation_draft-6-slide-pitch-deck_select` | read | draft a 6-slide pitch deck for *（1 项，如 Draft a 6-slide pitch deck for a new product） |
| `foxos presentation outline-talk-topic-i-give-you select TARGET` | `presentation_outline-talk-topic-i-give-you_select` | read | outline a # talk on a topic i give you（1 项，如 Outline a 10-minute talk on a topic I give you） |
| `foxos presentation accessibility select TARGET` | `presentation_accessibility_select` | read | accessibility: *（1 项，如 Accessibility: Good to go） |
| `foxos presentation pen select TARGET` | `presentation_pen_select` | read | pen: *（2 项，如 Pen: Black, 1 mm） |
| `foxos presentation pencil select TARGET` | `presentation_pencil_select` | read | pencil: *（1 项，如 Pencil: Graphite, 1 mm） |
| `foxos presentation highlighter select TARGET` | `presentation_highlighter_select` | read | highlighter: *（1 项，如 Highlighter: Yellow, 6 mm） |
| `foxos presentation duration select TARGET` | `presentation_duration_select` | read | # duration（1 项，如 Decrease Duration） |
| `foxos presentation advance-after select TARGET` | `presentation_advance-after_select` | read | # advance after（1 项，如 Decrease Advance after） |
| `foxos presentation delay select TARGET` | `presentation_delay_select` | read | # delay（1 项，如 Decrease Delay） |
| `foxos presentation content dismiss` | `presentation_content_dismiss` | read | Skip to content |
| `foxos presentation presentations previous` | `presentation_presentations_previous` | read | Back to presentations |
| `foxos presentation puter save` | `presentation_puter_save` | modify | Save to Puter |
| `foxos presentation undo undo` | `presentation_undo_undo` | modify | Undo |
| `foxos presentation redo redo` | `presentation_redo_redo` | modify | Redo |
| `foxos presentation edit update` | `presentation_edit_update` | modify | Edit |
| `foxos presentation view show` | `presentation_view_show` | read | View |
| `foxos presentation insert create` | `presentation_insert_create` | modify | Insert |
| `foxos presentation format activate` | `presentation_format_activate` | modify | Format |
| `foxos presentation arrange activate` | `presentation_arrange_activate` | modify | Arrange |
| `foxos presentation slide activate` | `presentation_slide_activate` | modify | Slide |
| `foxos presentation tools activate` | `presentation_tools_activate` | modify | Tools |
| `foxos presentation slide-show activate` | `presentation_slide-show_activate` | modify | Slide Show |
| `foxos presentation help show` | `presentation_help_show` | read | Help |
| `foxos presentation untitled-presentation rename` | `presentation_untitled-presentation_rename` | modify | Rename “Untitled presentation” |
| `foxos presentation save save` | `presentation_save_save` | modify | Save |
| `foxos presentation ask-ai activate` | `presentation_ask-ai_activate` | modify | Ask AI |
| `foxos presentation present activate` | `presentation_present_activate` | modify | Present |
| `foxos presentation home show` | `presentation_home_show` | read | Home |
| `foxos presentation insert-2 create` | `presentation_insert-2_create` | modify | Insert |
| `foxos presentation draw draw` | `presentation_draw_draw` | modify | Draw |
| `foxos presentation design show` | `presentation_design_show` | read | Design |
| `foxos presentation transitions show` | `presentation_transitions_show` | read | Transitions |
| `foxos presentation animations show` | `presentation_animations_show` | read | Animations |
| `foxos presentation slide-show show` | `presentation_slide-show_show` | read | Slide Show |
| `foxos presentation record record` | `presentation_record_record` | modify | Record |
| `foxos presentation review show` | `presentation_review_show` | read | Review |
| `foxos presentation view-2 show` | `presentation_view-2_show` | read | View |
| `foxos presentation ribbon collapse` | `presentation_ribbon_collapse` | read | Collapse the ribbon |
| `foxos presentation paste paste` | `presentation_paste_paste` | modify | Paste |
| `foxos presentation options paste` | `presentation_options_paste` | modify | Paste options |
| `foxos presentation cut cut` | `presentation_cut_cut` | modify | Cut |
| `foxos presentation copy copy` | `presentation_copy_copy` | modify | Copy |
| `foxos presentation format-painter activate` | `presentation_format-painter_activate` | modify | Format Painter |
| `foxos presentation slide create` | `presentation_slide_create` | modify | New Slide |
| `foxos presentation slide-layouts create` | `presentation_slide-layouts_create` | modify | New Slide layouts |
| `foxos presentation layout activate` | `presentation_layout_activate` | modify | Layout |
| `foxos presentation reset reset` | `presentation_reset_reset` | modify | Reset |
| `foxos presentation section activate` | `presentation_section_activate` | modify | Section |
| `foxos presentation font set VALUE [--submit]` | `presentation_font_set` | modify | Font |
| `foxos presentation font-list activate` | `presentation_font-list_activate` | modify | Font list |
| `foxos presentation font-size set VALUE [--submit]` | `presentation_font-size_set` | modify | Font Size |
| `foxos presentation font-size-list activate` | `presentation_font-size-list_activate` | modify | Font Size list |
| `foxos presentation increase-font-size activate` | `presentation_increase-font-size_activate` | modify | Increase Font Size |
| `foxos presentation formatting clear` | `presentation_formatting_clear` | modify | Clear All Formatting |
| `foxos presentation font-settings activate` | `presentation_font-settings_activate` | modify | Font Settings |
| `foxos presentation bold format` | `presentation_bold_format` | modify | Bold |
| `foxos presentation italic format` | `presentation_italic_format` | modify | Italic |
| `foxos presentation underline format` | `presentation_underline_format` | modify | Underline |
| `foxos presentation strikethrough format` | `presentation_strikethrough_format` | modify | Strikethrough |
| `foxos presentation superscript activate` | `presentation_superscript_activate` | modify | Superscript |
| `foxos presentation subscript activate` | `presentation_subscript_activate` | modify | Subscript |
| `foxos presentation character-spacing activate` | `presentation_character-spacing_activate` | modify | Character Spacing |
| `foxos presentation case update` | `presentation_case_update` | modify | Change Case |
| `foxos presentation text-highlight-color activate` | `presentation_text-highlight-color_activate` | modify | Text Highlight Color |
| `foxos presentation highlight-colors activate` | `presentation_highlight-colors_activate` | modify | Highlight colors |
| `foxos presentation font-color activate` | `presentation_font-color_activate` | modify | Font Color |
| `foxos presentation font-colors activate` | `presentation_font-colors_activate` | modify | Font colors |
| `foxos presentation bullets activate` | `presentation_bullets_activate` | modify | Bullets |
| `foxos presentation bullet-styles activate` | `presentation_bullet-styles_activate` | modify | Bullet styles |
| `foxos presentation numbering activate` | `presentation_numbering_activate` | modify | Numbering |
| `foxos presentation numbering-styles activate` | `presentation_numbering-styles_activate` | modify | Numbering styles |
| `foxos presentation increase-list-level activate` | `presentation_increase-list-level_activate` | modify | Increase List Level |
| `foxos presentation line-spacing activate` | `presentation_line-spacing_activate` | modify | Line Spacing |
| `foxos presentation columns activate` | `presentation_columns_activate` | modify | Columns |
| `foxos presentation paragraph-settings activate` | `presentation_paragraph-settings_activate` | modify | Paragraph Settings |
| `foxos presentation left align` | `presentation_left_align` | modify | Align Left |
| `foxos presentation center activate` | `presentation_center_activate` | modify | Center |
| `foxos presentation right align` | `presentation_right_align` | modify | Align Right |
| `foxos presentation justify activate` | `presentation_justify_activate` | modify | Justify |
| `foxos presentation text-direction activate` | `presentation_text-direction_activate` | modify | Text Direction |
| `foxos presentation text align` | `presentation_text_align` | modify | Align Text |
| `foxos presentation convert-smartart activate` | `presentation_convert-smartart_activate` | modify | Convert to SmartArt |
| `foxos presentation insert-3 create` | `presentation_insert-3_create` | modify | Insert |
| `foxos presentation drawing activate` | `presentation_drawing_activate` | modify | Drawing |
| `foxos presentation editing activate` | `presentation_editing_activate` | modify | Editing |
| `foxos presentation designer activate` | `presentation_designer_activate` | modify | Designer |
| `foxos presentation slide-thumbnails resize` | `presentation_slide-thumbnails_resize` | modify | Resize slide thumbnails |
| `foxos presentation notes resize` | `presentation_notes_resize` | modify | Resize notes |
| `foxos presentation speaker-notes set VALUE [--submit]` | `presentation_speaker-notes_set` | modify | Speaker notes |
| `foxos presentation assistant resize` | `presentation_assistant_resize` | modify | Resize the assistant |
| `foxos presentation chat create` | `presentation_chat_create` | modify | New chat |
| `foxos presentation assistant-settings activate` | `presentation_assistant-settings_activate` | modify | Assistant settings |
| `foxos presentation assistant close` | `presentation_assistant_close` | read | Close the assistant |
| `foxos presentation turn-notes-into-slides activate` | `presentation_turn-notes-into-slides_activate` | modify | Turn my notes into slides |
| `foxos presentation message-assistant set VALUE [--submit]` | `presentation_message-assistant_set` | modify | Message the assistant |
| `foxos presentation send send` | `presentation_send_send` | modify | Send |
| `foxos presentation english-united-states activate` | `presentation_english-united-states_activate` | modify | English (United States) |
| `foxos presentation notes activate` | `presentation_notes_activate` | modify | Notes |
| `foxos presentation comments activate` | `presentation_comments_activate` | modify | Comments |
| `foxos presentation normal activate` | `presentation_normal_activate` | modify | Normal |
| `foxos presentation slide-sorter activate` | `presentation_slide-sorter_activate` | modify | Slide Sorter |
| `foxos presentation reading-view activate` | `presentation_reading-view_activate` | modify | Reading View |
| `foxos presentation slide-show-2 activate` | `presentation_slide-show-2_activate` | modify | Slide Show |
| `foxos presentation view zoom-out` | `presentation_view_zoom-out` | modify | Zoom out |
| `foxos presentation zoom set VALUE [--submit]` | `presentation_zoom_set` | modify | Zoom |
| `foxos presentation view zoom-` | `presentation_view_zoom-` | modify | Zoom in |
| `foxos presentation view zoom-level` | `presentation_view_zoom-level` | modify | Zoom level |
| `foxos presentation fit-slide-current-window activate` | `presentation_fit-slide-current-window_activate` | modify | Fit slide to current window |
| `foxos presentation close close` | `presentation_close_close` | read | Close |
| `foxos presentation presentation-name set VALUE [--submit]` | `presentation_presentation-name_set` | modify | Presentation name |
| `foxos presentation cancel cancel` | `presentation_cancel_cancel` | read | Cancel |
| `foxos presentation appearance activate` | `presentation_appearance_activate` | modify | Appearance |
| `foxos presentation keyboard-shortcuts activate` | `presentation_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos presentation table activate` | `presentation_table_activate` | modify | Table |
| `foxos presentation pictures activate` | `presentation_pictures_activate` | modify | Pictures |
| `foxos presentation picture-sources activate` | `presentation_picture-sources_activate` | modify | Picture sources |
| `foxos presentation screenshot activate` | `presentation_screenshot_activate` | modify | Screenshot |
| `foxos presentation screenshot-options activate` | `presentation_screenshot-options_activate` | modify | Screenshot options |
| `foxos presentation photo-album activate` | `presentation_photo-album_activate` | modify | Photo Album |
| `foxos presentation shapes activate` | `presentation_shapes_activate` | modify | Shapes |
| `foxos presentation icons activate` | `presentation_icons_activate` | modify | Icons |
| `foxos presentation smartart activate` | `presentation_smartart_activate` | modify | SmartArt |
| `foxos presentation chart activate` | `presentation_chart_activate` | modify | Chart |
| `foxos presentation zoom zoom` | `presentation_zoom_zoom` | read | Zoom |
| `foxos presentation link activate` | `presentation_link_activate` | modify | Link |
| `foxos presentation action activate` | `presentation_action_activate` | modify | Action |
| `foxos presentation action-options activate` | `presentation_action-options_activate` | modify | Action options |
| `foxos presentation comment activate` | `presentation_comment_activate` | modify | Comment |
| `foxos presentation text-box activate` | `presentation_text-box_activate` | modify | Text Box |
| `foxos presentation header-footer activate` | `presentation_header-footer_activate` | modify | Header & Footer |
| `foxos presentation wordart activate` | `presentation_wordart_activate` | modify | WordArt |
| `foxos presentation date-time activate` | `presentation_date-time_activate` | modify | Date & Time |
| `foxos presentation slide-number activate` | `presentation_slide-number_activate` | modify | Slide Number |
| `foxos presentation object activate` | `presentation_object_activate` | modify | Object |
| `foxos presentation symbols activate` | `presentation_symbols_activate` | modify | Symbols |
| `foxos presentation media activate` | `presentation_media_activate` | modify | Media |
| `foxos presentation select select` | `presentation_select_select` | read | Select |
| `foxos presentation eraser activate` | `presentation_eraser_activate` | modify | Eraser |
| `foxos presentation eraser-options activate` | `presentation_eraser-options_activate` | modify | Eraser options |
| `foxos presentation lasso-select activate` | `presentation_lasso-select_activate` | modify | Lasso Select |
| `foxos presentation pen create` | `presentation_pen_create` | modify | Add Pen |
| `foxos presentation ink-text activate` | `presentation_ink-text_activate` | modify | Ink to Text |
| `foxos presentation ink-shape activate` | `presentation_ink-shape_activate` | modify | Ink to Shape |
| `foxos presentation ink-shape-options activate` | `presentation_ink-shape-options_activate` | modify | Ink to Shape options |
| `foxos presentation ink-math activate` | `presentation_ink-math_activate` | modify | Ink to Math |
| `foxos presentation ink-replay activate` | `presentation_ink-replay_activate` | modify | Ink Replay |
| `foxos presentation ruler activate` | `presentation_ruler_activate` | modify | Ruler |
| `foxos presentation touch draw` | `presentation_touch_draw` | modify | Draw with Touch |
| `foxos presentation default-theme activate` | `presentation_default-theme_activate` | modify | Default Theme |
| `foxos presentation paper activate` | `presentation_paper_activate` | modify | Paper |
| `foxos presentation studio activate` | `presentation_studio_activate` | modify | Studio |
| `foxos presentation cobalt activate` | `presentation_cobalt_activate` | modify | Cobalt |
| `foxos presentation row-themes previous` | `presentation_row-themes_previous` | read | Previous row of Themes |
| `foxos presentation row-themes next` | `presentation_row-themes_next` | read | Next row of Themes |
| `foxos presentation themes show` | `presentation_themes_show` | read | More Themes |
| `foxos presentation default activate` | `presentation_default_activate` | modify | Default |
| `foxos presentation default-dark activate` | `presentation_default-dark_activate` | modify | Default (Dark) |
| `foxos presentation default-accents-turned activate` | `presentation_default-accents-turned_activate` | modify | Default (Accents turned) |
| `foxos presentation default-accents-turned-twice activate` | `presentation_default-accents-turned-twice_activate` | modify | Default (Accents turned twice) |
| `foxos presentation row-variants previous` | `presentation_row-variants_previous` | read | Previous row of Variants |
| `foxos presentation row-variants next` | `presentation_row-variants_next` | read | Next row of Variants |
| `foxos presentation variants show` | `presentation_variants_show` | read | More Variants |
| `foxos presentation colors activate` | `presentation_colors_activate` | modify | Colors |
| `foxos presentation fonts activate` | `presentation_fonts_activate` | modify | Fonts |
| `foxos presentation effects activate` | `presentation_effects_activate` | modify | Effects |
| `foxos presentation background-styles activate` | `presentation_background-styles_activate` | modify | Background Styles |
| `foxos presentation slide-size activate` | `presentation_slide-size_activate` | modify | Slide Size |
| `foxos presentation format-background activate` | `presentation_format-background_activate` | modify | Format Background |
| `foxos presentation hide-background-graphics toggle` | `presentation_hide-background-graphics_toggle` | modify | Hide Background Graphics |
| `foxos presentation design-ideas activate` | `presentation_design-ideas_activate` | modify | Design Ideas |
| `foxos presentation preview activate` | `presentation_preview_activate` | modify | Preview |
| `foxos presentation none activate` | `presentation_none_activate` | modify | None |
| `foxos presentation morph activate` | `presentation_morph_activate` | modify | Morph |
| `foxos presentation fade activate` | `presentation_fade_activate` | modify | Fade |
| `foxos presentation push activate` | `presentation_push_activate` | modify | Push |
| `foxos presentation wipe activate` | `presentation_wipe_activate` | modify | Wipe |
| `foxos presentation split activate` | `presentation_split_activate` | modify | Split |
| `foxos presentation reveal activate` | `presentation_reveal_activate` | modify | Reveal |
| `foxos presentation transitions-cut cut` | `presentation_transitions-cut_cut` | modify | Cut |
| `foxos presentation random-bars activate` | `presentation_random-bars_activate` | modify | Random Bars |
| `foxos presentation row-transitions previous` | `presentation_row-transitions_previous` | read | Previous row of Transitions |
| `foxos presentation row-transitions next` | `presentation_row-transitions_next` | read | Next row of Transitions |
| `foxos presentation transitions-2 show` | `presentation_transitions-2_show` | read | More Transitions |
| `foxos presentation effect-options activate` | `presentation_effect-options_activate` | modify | Effect Options |
| `foxos presentation sound activate` | `presentation_sound_activate` | modify | Sound |
| `foxos presentation duration set VALUE [--submit]` | `presentation_duration_set` | modify | Duration |
| `foxos presentation increase-duration activate` | `presentation_increase-duration_activate` | modify | Increase Duration |
| `foxos presentation apply confirm` | `presentation_apply_confirm` | modify | Apply To All |
| `foxos presentation mouse-click toggle` | `presentation_mouse-click_toggle` | modify | On Mouse Click |
| `foxos presentation after toggle` | `presentation_after_toggle` | modify | After |
| `foxos presentation advance-after-seconds set VALUE [--submit]` | `presentation_advance-after-seconds_set` | modify | Advance after (seconds) |
| `foxos presentation increase-advance-after activate` | `presentation_increase-advance-after_activate` | modify | Increase Advance after |
| `foxos presentation preview-options activate` | `presentation_preview-options_activate` | modify | Preview options |
| `foxos presentation appear activate` | `presentation_appear_activate` | modify | Appear |
| `foxos presentation fly activate` | `presentation_fly_activate` | modify | Fly In |
| `foxos presentation float activate` | `presentation_float_activate` | modify | Float In |
| `foxos presentation shape activate` | `presentation_shape_activate` | modify | Shape |
| `foxos presentation row-animations previous` | `presentation_row-animations_previous` | read | Previous row of Animations |
| `foxos presentation row-animations next` | `presentation_row-animations_next` | read | Next row of Animations |
| `foxos presentation animations-2 show` | `presentation_animations-2_show` | read | More Animations |
| `foxos presentation animation create` | `presentation_animation_create` | modify | Add Animation |
| `foxos presentation animation-pane activate` | `presentation_animation-pane_activate` | modify | Animation Pane |
| `foxos presentation trigger activate` | `presentation_trigger_activate` | modify | Trigger |
| `foxos presentation animation-painter activate` | `presentation_animation-painter_activate` | modify | Animation Painter |
| `foxos presentation start set VALUE [--submit]` | `presentation_start_set` | modify | Start |
| `foxos presentation list start` | `presentation_list_start` | modify | Start list |
| `foxos presentation delay set VALUE [--submit]` | `presentation_delay_set` | modify | Delay |
| `foxos presentation increase-delay activate` | `presentation_increase-delay_activate` | modify | Increase Delay |
| `foxos presentation earlier move` | `presentation_earlier_move` | modify | Move Earlier |
| `foxos presentation later move` | `presentation_later_move` | modify | Move Later |
| `foxos presentation from-start play` | `presentation_from-start_play` | modify | Play from Start |
| `foxos presentation from-current-slide play` | `presentation_from-current-slide_play` | modify | Play from Current Slide |
| `foxos presentation presenter-view activate` | `presentation_presenter-view_activate` | modify | Presenter View |
| `foxos presentation custom-show activate` | `presentation_custom-show_activate` | modify | Custom Show |
| `foxos presentation set-up-slide-show activate` | `presentation_set-up-slide-show_activate` | modify | Set Up Slide Show |
| `foxos presentation slide hide` | `presentation_slide_hide` | read | Hide Slide |
| `foxos presentation rehearse-timings activate` | `presentation_rehearse-timings_activate` | modify | Rehearse Timings |
| `foxos presentation slide-show-record record` | `presentation_slide-show-record_record` | modify | Record |
| `foxos presentation options record` | `presentation_options_record` | modify | Record options |
| `foxos presentation play-narrations toggle` | `presentation_play-narrations_toggle` | modify | Play Narrations |
| `foxos presentation use-timings toggle` | `presentation_use-timings_toggle` | modify | Use Timings |
| `foxos presentation show-media-controls toggle` | `presentation_show-media-controls_toggle` | modify | Show Media Controls |
| `foxos presentation always-use-subtitles toggle` | `presentation_always-use-subtitles_toggle` | modify | Always Use Subtitles |
| `foxos presentation subtitle-settings activate` | `presentation_subtitle-settings_activate` | modify | Subtitle Settings |
| `foxos presentation live-camera activate` | `presentation_live-camera_activate` | modify | Live Camera |
| `foxos presentation from-beginning activate` | `presentation_from-beginning_activate` | modify | From Beginning |
| `foxos presentation from-current-slide activate` | `presentation_from-current-slide_activate` | modify | From Current Slide |
| `foxos presentation recording clear` | `presentation_recording_clear` | modify | Clear Recording |
| `foxos presentation camera reset` | `presentation_camera_reset` | modify | Reset to Camera |
| `foxos presentation video export` | `presentation_video_export` | modify | Export to Video |
| `foxos presentation spelling activate` | `presentation_spelling_activate` | modify | Spelling |
| `foxos presentation thesaurus activate` | `presentation_thesaurus_activate` | modify | Thesaurus |
| `foxos presentation accessibility run` | `presentation_accessibility_run` | modify | Check Accessibility |
| `foxos presentation accessibility-options activate` | `presentation_accessibility-options_activate` | modify | Accessibility options |
| `foxos presentation alt-text activate` | `presentation_alt-text_activate` | modify | Alt Text |
| `foxos presentation translate activate` | `presentation_translate_activate` | modify | Translate |
| `foxos presentation language activate` | `presentation_language_activate` | modify | Language |
| `foxos presentation comment create` | `presentation_comment_create` | modify | New Comment |
| `foxos presentation delete delete` | `presentation_delete_delete` | delete | Delete |
| `foxos presentation previous previous` | `presentation_previous_previous` | read | Previous |
| `foxos presentation next next` | `presentation_next_next` | read | Next |
| `foxos presentation comments show` | `presentation_comments_show` | read | Show Comments |
| `foxos presentation comments-options show` | `presentation_comments-options_show` | read | Show Comments options |
| `foxos presentation compare activate` | `presentation_compare_activate` | modify | Compare |
| `foxos presentation always-open-read-only activate` | `presentation_always-open-read-only_activate` | modify | Always Open Read-Only |
| `foxos presentation outline-view activate` | `presentation_outline-view_activate` | modify | Outline View |
| `foxos presentation notes-page activate` | `presentation_notes-page_activate` | modify | Notes Page |
| `foxos presentation slide-master activate` | `presentation_slide-master_activate` | modify | Slide Master |
| `foxos presentation handout-master activate` | `presentation_handout-master_activate` | modify | Handout Master |
| `foxos presentation notes-master activate` | `presentation_notes-master_activate` | modify | Notes Master |
| `foxos presentation ruler toggle` | `presentation_ruler_toggle` | modify | Ruler |
| `foxos presentation gridlines toggle` | `presentation_gridlines_toggle` | modify | Gridlines |
| `foxos presentation guides toggle` | `presentation_guides_toggle` | modify | Guides |
| `foxos presentation view-notes activate` | `presentation_view-notes_activate` | modify | Notes |
| `foxos presentation grid-settings activate` | `presentation_grid-settings_activate` | modify | Grid Settings |
| `foxos presentation fit-window activate` | `presentation_fit-window_activate` | modify | Fit to Window |
| `foxos presentation color activate` | `presentation_color_activate` | modify | Color |
| `foxos presentation grayscale activate` | `presentation_grayscale_activate` | modify | Grayscale |
| `foxos presentation black-white activate` | `presentation_black-white_activate` | modify | Black and White |
| `foxos presentation slide-thumbnails activate` | `presentation_slide-thumbnails_activate` | modify | Slide Thumbnails |
| `foxos presentation format-pane activate` | `presentation_format-pane_activate` | modify | Format Pane |
| `foxos presentation ai-assistant activate` | `presentation_ai-assistant_activate` | modify | AI Assistant |
| `foxos presentation pastectrlv activate` | `presentation_pastectrlv_activate` | modify | PasteCtrl+V |
| `foxos presentation as-text-only paste` | `presentation_as-text-only_paste` | modify | Paste as Text Only |
| `foxos presentation duplicatectrld activate` | `presentation_duplicatectrld_activate` | modify | DuplicateCtrl+D |
| `foxos presentation special paste` | `presentation_special_paste` | modify | Paste Special… |
| `foxos presentation match-formatting paste` | `presentation_match-formatting_paste` | modify | Paste and Match Formatting |
| `foxos presentation selection select-all` | `presentation_selection_select-all` | modify | 快捷键 mod+a |
| `foxos presentation selection duplicate` | `presentation_selection_duplicate` | modify | 快捷键 mod+d |
| `foxos presentation shortcut key-j` | `presentation_shortcut_key-j` | modify | 快捷键 mod+j |
| `foxos presentation command-palette show` | `presentation_command-palette_show` | read | 快捷键 mod+k |
| `foxos presentation document open` | `presentation_document_open` | read | 快捷键 mod+o |
| `foxos presentation document print` | `presentation_document_print` | read | 快捷键 mod+p |
| `foxos presentation document save` | `presentation_document_save` | modify | 快捷键 mod+s |
| `foxos presentation clipboard paste` | `presentation_clipboard_paste` | modify | 快捷键 mod+v |

### whiteboard（`whiteboard`，26 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos whiteboard board-library select TARGET` | `whiteboard_board-library_select` | read | all #（1 项，如 All boards0） |
| `foxos whiteboard board-library-2 select TARGET` | `whiteboard_board-library-2_select` | read | #（1 项，如 Favorites0） |
| `foxos whiteboard main select TARGET` | `whiteboard_main_select` | read | crazy # eight ideas in eight minutes, then share and vote.（1 项，如 Crazy 8sSketch eight ideas in eight minutes, then share and vote.） |
| `foxos whiteboard whiteboard-home show` | `whiteboard_whiteboard-home_show` | read | Whiteboard home |
| `foxos whiteboard trash delete` | `whiteboard_trash_delete` | delete | Trash |
| `foxos whiteboard organization join` | `whiteboard_organization_join` | modify | Join an organization |
| `foxos whiteboard set-up-organization activate` | `whiteboard_set-up-organization_activate` | modify | Set up an organization |
| `foxos whiteboard feedback send` | `whiteboard_feedback_send` | modify | Send feedback |
| `foxos whiteboard language set VALUE [--submit]` | `whiteboard_language_set` | modify | Language |
| `foxos whiteboard appearance set VALUE [--submit]` | `whiteboard_appearance_set` | modify | Appearance |
| `foxos whiteboard powered-by-puter show` | `whiteboard_powered-by-puter_show` | read | Powered by Puter |
| `foxos whiteboard command-palette-ctrl-cmd-k activate` | `whiteboard_command-palette-ctrl-cmd-k_activate` | modify | Command palette (Ctrl/Cmd K) |
| `foxos whiteboard shared-board join` | `whiteboard_shared-board_join` | modify | Join shared board |
| `foxos whiteboard training show` | `whiteboard_training_show` | read | Help and training |
| `foxos whiteboard keyboard-shortcuts activate` | `whiteboard_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos whiteboard account-menu-local activate` | `whiteboard_account-menu-local_activate` | modify | Account menu · local |
| `foxos whiteboard browse-templates activate` | `whiteboard_browse-templates_activate` | modify | Browse all templates |
| `foxos whiteboard blank-boarda-fresh-start activate` | `whiteboard_blank-boarda-fresh-start_activate` | modify | Blank boardA fresh start |
| `foxos whiteboard board create` | `whiteboard_board_create` | modify | New board |
| `foxos whiteboard search-boards set VALUE [--submit]` | `whiteboard_search-boards_set` | modify | Search boards |
| `foxos whiteboard sort-boards set VALUE [--submit]` | `whiteboard_sort-boards_set` | modify | Sort boards |
| `foxos whiteboard board-file import` | `whiteboard_board-file_import` | modify | Import board file |
| `foxos whiteboard migrate-from-miro activate` | `whiteboard_migrate-from-miro_activate` | modify | Migrate from Miro |
| `foxos whiteboard grid-view activate` | `whiteboard_grid-view_activate` | modify | Grid view |
| `foxos whiteboard list-view activate` | `whiteboard_list-view_activate` | modify | List view |
| `foxos whiteboard keyboard-shortcuts-2 activate` | `whiteboard_keyboard-shortcuts-2_activate` | modify | Keyboard shortcuts |

### pdf（`pdf`，83 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos pdf notes-highlight-text-up-pages leave TARGET` | `pdf_notes-highlight-text-up-pages_leave` | modify | leave notes, highlight text, and # up pages.（1 项，如 Leave notes, highlight text, and mark up pages.） |
| `foxos pdf fillable-fields create TARGET` | `pdf_fillable-fields_create` | modify | add fillable fields: *（1 项，如 Add fillable fields: choose a field type, then drag a box on the page or click to place one. Double-click a field for it） |
| `foxos pdf tools select TARGET` | `pdf_tools_select` | read | # text, pictures, or areas, then apply to remove them from the file for good.（1 项，如 Mark text, pictures, or areas, then apply to remove them from the file for good.） |
| `foxos pdf go-page select TARGET` | `pdf_go-page_select` | read | go to page #（1 项，如 Go to page 1） |
| `foxos pdf page-actions select TARGET` | `pdf_page-actions_select` | read | page # actions（1 项，如 Page 1 actions） |
| `foxos pdf pages select TARGET` | `pdf_pages_select` | read | all pages (#)（1 项，如 All pages (1)） |
| `foxos pdf current-page select TARGET` | `pdf_current-page_select` | read | current page (#)（1 项，如 Current page (1)） |
| `foxos pdf content dismiss` | `pdf_content_dismiss` | read | Skip to content |
| `foxos pdf pdfs previous` | `pdf_pdfs_previous` | read | Back to your PDFs |
| `foxos pdf edit update` | `pdf_edit_update` | modify | Edit |
| `foxos pdf view show` | `pdf_view_show` | read | View |
| `foxos pdf page activate` | `pdf_page_activate` | modify | Page |
| `foxos pdf insert create` | `pdf_insert_create` | modify | Insert |
| `foxos pdf untitled-pdf rename` | `pdf_untitled-pdf_rename` | modify | Rename Untitled.pdf |
| `foxos pdf settings show` | `pdf_settings_show` | read | Settings |
| `foxos pdf tools activate` | `pdf_tools_activate` | modify | Tools |
| `foxos pdf edit-2 update` | `pdf_edit-2_update` | modify | Edit |
| `foxos pdf comment activate` | `pdf_comment_activate` | modify | Comment |
| `foxos pdf export export` | `pdf_export_export` | modify | Export |
| `foxos pdf fill-sign activate` | `pdf_fill-sign_activate` | modify | Fill & Sign |
| `foxos pdf text-or-tools search` | `pdf_text-or-tools_search` | read | Find text or tools |
| `foxos pdf undo undo` | `pdf_undo_undo` | modify | Undo |
| `foxos pdf redo redo` | `pdf_redo_redo` | modify | Redo |
| `foxos pdf download export` | `pdf_download_export` | modify | Download |
| `foxos pdf puter save` | `pdf_puter_save` | modify | Save to Puter |
| `foxos pdf tools-panel close` | `pdf_tools-panel_close` | read | Close tools panel |
| `foxos pdf pdf-or-its-pages-another-format save` | `pdf_pdf-or-its-pages-another-format_save` | modify | Save the PDF, or its pages, in another format. |
| `foxos pdf pdf-or-turn-pictures-into-pdf-pages start` | `pdf_pdf-or-turn-pictures-into-pdf-pages_start` | modify | Start a new PDF, or turn pictures into PDF pages. |
| `foxos pdf combine-pdfs-pictures-into-one-pdf activate` | `pdf_combine-pdfs-pictures-into-one-pdf_activate` | modify | Combine PDFs and pictures into one new PDF. |
| `foxos pdf fill-forms-add-signature activate` | `pdf_fill-forms-add-signature_activate` | modify | Fill in forms and add your signature. |
| `foxos pdf make-file-smaller-by-shrinking-its-pictu activate` | `pdf_make-file-smaller-by-shrinking-its-pictu_activate` | modify | Make the file smaller by shrinking its pictures. |
| `foxos pdf more show` | `pdf_more_show` | read | View more |
| `foxos pdf select select` | `pdf_select_select` | read | Select |
| `foxos pdf hand activate` | `pdf_hand_activate` | modify | Hand |
| `foxos pdf text activate` | `pdf_text_activate` | modify | Text |
| `foxos pdf highlight activate` | `pdf_highlight_activate` | modify | Highlight |
| `foxos pdf draw draw` | `pdf_draw_draw` | modify | Draw |
| `foxos pdf shape activate` | `pdf_shape_activate` | modify | Shape |
| `foxos pdf note activate` | `pdf_note_activate` | modify | Note |
| `foxos pdf image activate` | `pdf_image_activate` | modify | Image |
| `foxos pdf sign sign` | `pdf_sign_sign` | modify | Sign |
| `foxos pdf fill-forms activate` | `pdf_fill-forms_activate` | modify | Fill forms |
| `foxos pdf pdf-page-view activate` | `pdf_pdf-page-view_activate` | modify | PDF page view |
| `foxos pdf page previous` | `pdf_page_previous` | read | Previous page |
| `foxos pdf page-number set VALUE [--submit]` | `pdf_page-number_set` | modify | Page number |
| `foxos pdf page next` | `pdf_page_next` | read | Next page |
| `foxos pdf view zoom-out` | `pdf_view_zoom-out` | modify | Zoom out |
| `foxos pdf zoom set VALUE [--submit]` | `pdf_zoom_set` | modify | Zoom |
| `foxos pdf view zoom-` | `pdf_view_zoom-` | modify | Zoom in |
| `foxos pdf pages show` | `pdf_pages_show` | read | Pages |
| `foxos pdf comments show` | `pdf_comments_show` | read | Comments |
| `foxos pdf attachments show` | `pdf_attachments_show` | read | Attachments |
| `foxos pdf pages-panel toggle` | `pdf_pages-panel_toggle` | modify | Toggle pages panel |
| `foxos pdf pages-panel close` | `pdf_pages-panel_close` | read | Close pages panel |
| `foxos pdf dialog close` | `pdf_dialog_close` | read | Close dialog |
| `foxos pdf appearance set VALUE [--submit]` | `pdf_appearance_set` | modify | Appearance |
| `foxos pdf keyboard-shortcuts activate` | `pdf_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos pdf pdf-editor show` | `pdf_pdf-editor_show` | read | About PDF Editor |
| `foxos pdf tools previous` | `pdf_tools_previous` | read | Back to all tools |
| `foxos pdf text create` | `pdf_text_create` | modify | Add text |
| `foxos pdf image create` | `pdf_image_create` | modify | Add image |
| `foxos pdf link create` | `pdf_link_create` | modify | Add link |
| `foxos pdf text-images update` | `pdf_text-images_update` | modify | Edit text and images |
| `foxos pdf pages crop` | `pdf_pages_crop` | modify | Crop pages |
| `foxos pdf header-footer activate` | `pdf_header-footer_activate` | modify | Header and footer… |
| `foxos pdf watermark activate` | `pdf_watermark_activate` | modify | Watermark… |
| `foxos pdf page-numbers activate` | `pdf_page-numbers_activate` | modify | Page numbers… |
| `foxos pdf bates-numbering activate` | `pdf_bates-numbering_activate` | modify | Bates numbering… |
| `foxos pdf headers-footers delete` | `pdf_headers-footers_delete` | delete | Remove headers and footers |
| `foxos pdf watermarks delete` | `pdf_watermarks_delete` | delete | Remove watermarks |
| `foxos pdf find-pdf set VALUE [--submit]` | `pdf_find-pdf_set` | modify | Find in PDF |
| `foxos pdf match previous` | `pdf_match_previous` | read | Previous match |
| `foxos pdf match next` | `pdf_match_next` | read | Next match |
| `foxos pdf search close` | `pdf_search_close` | read | Close search |
| `foxos pdf pages toggle` | `pdf_pages_toggle` | modify | Pages |
| `foxos pdf page-range set VALUE [--submit]` | `pdf_page-range_set` | modify | Page range |
| `foxos pdf cancel cancel` | `pdf_cancel_cancel` | read | Cancel |
| `foxos pdf print print` | `pdf_print_print` | read | Print |
| `foxos pdf comments-panel close` | `pdf_comments-panel_close` | read | Close comments panel |
| `foxos pdf attachments-panel close` | `pdf_attachments-panel_close` | read | Close attachments panel |
| `foxos pdf attach-file activate` | `pdf_attach-file_activate` | modify | Attach a file… |
| `foxos pdf selection select-all` | `pdf_selection_select-all` | modify | 快捷键 mod+a |
| `foxos pdf selection group-shift` | `pdf_selection_group-shift` | modify | 快捷键 mod+shift+g |

### notes（`notes`，135 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos notes font-size select TARGET` | `notes_font-size_select` | read | # font size（1 项，如 Decrease Font Size） |
| `foxos notes indent-position select TARGET` | `notes_indent-position_select` | read | # indent position（1 项，如 Decrease Indent Position） |
| `foxos notes notebook select TARGET` | `notes_notebook_select` | read | notebook: *（1 项，如 Notebook: local's Notebook. Switch notebooks） |
| `foxos notes section create TARGET` | `notes_section_create` | modify | new section #（1 项，如 New Section 1） |
| `foxos notes heading-alt select TARGET` | `notes_heading-alt_select` | read | heading #+alt+#（6 项，如 Heading 1Ctrl+Alt+1） |
| `foxos notes normalctrlalt select TARGET` | `notes_normalctrlalt_select` | read | normalctrl+alt+#（1 项，如 NormalCtrl+Alt+0） |
| `foxos notes doctrl select TARGET` | `notes_doctrl_select` | read | to doctrl+#（1 项，如 To DoCtrl+1） |
| `foxos notes importantctrl select TARGET` | `notes_importantctrl_select` | read | importantctrl+#（1 项，如 ImportantCtrl+2） |
| `foxos notes questionctrl select TARGET` | `notes_questionctrl_select` | read | questionctrl+#（1 项，如 QuestionCtrl+3） |
| `foxos notes remember select TARGET` | `notes_remember_select` | read | remember for *（1 项，如 Remember for laterCtrl+4） |
| `foxos notes definitionctrl select TARGET` | `notes_definitionctrl_select` | read | definitionctrl+#（1 项，如 DefinitionCtrl+5） |
| `foxos notes highlightctrl select TARGET` | `notes_highlightctrl_select` | read | highlightctrl+#（1 项，如 HighlightCtrl+6） |
| `foxos notes contactctrl select TARGET` | `notes_contactctrl_select` | read | contactctrl+#（1 项，如 ContactCtrl+7） |
| `foxos notes addressctrl select TARGET` | `notes_addressctrl_select` | read | addressctrl+#（1 项，如 AddressCtrl+8） |
| `foxos notes phone-numberctrl select TARGET` | `notes_phone-numberctrl_select` | read | phone numberctrl+#（1 项，如 Phone numberCtrl+9） |
| `foxos notes source select TARGET` | `notes_source_select` | read | source for *（1 项，如 Source for article） |
| `foxos notes do-priority select TARGET` | `notes_do-priority_select` | read | to do priority #（2 项，如 To Do priority 1） |
| `foxos notes tagctrl delete TARGET` | `notes_tagctrl_delete` | modify | remove tagctrl+#（1 项，如 Remove TagCtrl+0） |
| `foxos notes undo undo` | `notes_undo_undo` | modify | Undo |
| `foxos notes redo redo` | `notes_redo_redo` | modify | Redo |
| `foxos notes commands show` | `notes_commands_show` | read | More commands |
| `foxos notes changes-saved-sync-now activate` | `notes_changes-saved-sync-now_activate` | modify | All changes saved. Sync now |
| `foxos notes share share` | `notes_share_share` | modify | Share |
| `foxos notes home show` | `notes_home_show` | read | Home |
| `foxos notes insert create` | `notes_insert_create` | modify | Insert |
| `foxos notes draw draw` | `notes_draw_draw` | modify | Draw |
| `foxos notes view show` | `notes_view_show` | read | View |
| `foxos notes help show` | `notes_help_show` | read | Help |
| `foxos notes tell-me-what-you-want-do set VALUE [--submit]` | `notes_tell-me-what-you-want-do_set` | modify | Tell me what you want to do |
| `foxos notes ribbon collapse` | `notes_ribbon_collapse` | read | Collapse the Ribbon |
| `foxos notes paste paste` | `notes_paste_paste` | modify | Paste |
| `foxos notes cut cut` | `notes_cut_cut` | modify | Cut |
| `foxos notes copy copy` | `notes_copy_copy` | modify | Copy |
| `foxos notes format-painter activate` | `notes_format-painter_activate` | modify | Format Painter |
| `foxos notes font set VALUE [--submit]` | `notes_font_set` | modify | Font |
| `foxos notes font-list activate` | `notes_font-list_activate` | modify | Font list |
| `foxos notes font-size set VALUE [--submit]` | `notes_font-size_set` | modify | Font Size |
| `foxos notes font-size-list activate` | `notes_font-size-list_activate` | modify | Font size list |
| `foxos notes increase-font-size activate` | `notes_increase-font-size_activate` | modify | Increase Font Size |
| `foxos notes bold format` | `notes_bold_format` | modify | Bold |
| `foxos notes italic format` | `notes_italic_format` | modify | Italic |
| `foxos notes underline format` | `notes_underline_format` | modify | Underline |
| `foxos notes strikethrough format` | `notes_strikethrough_format` | modify | Strikethrough |
| `foxos notes subscript activate` | `notes_subscript_activate` | modify | Subscript |
| `foxos notes superscript activate` | `notes_superscript_activate` | modify | Superscript |
| `foxos notes text-highlight-color activate` | `notes_text-highlight-color_activate` | modify | Text Highlight Color |
| `foxos notes text-highlight-color-options activate` | `notes_text-highlight-color-options_activate` | modify | Text Highlight Color options |
| `foxos notes font-color activate` | `notes_font-color_activate` | modify | Font Color |
| `foxos notes font-color-options activate` | `notes_font-color-options_activate` | modify | Font Color options |
| `foxos notes formatting clear` | `notes_formatting_clear` | modify | Clear All Formatting |
| `foxos notes bullets activate` | `notes_bullets_activate` | modify | Bullets |
| `foxos notes bullets-options activate` | `notes_bullets-options_activate` | modify | Bullets options |
| `foxos notes numbering activate` | `notes_numbering_activate` | modify | Numbering |
| `foxos notes numbering-options activate` | `notes_numbering-options_activate` | modify | Numbering options |
| `foxos notes increase-indent-position activate` | `notes_increase-indent-position_activate` | modify | Increase Indent Position |
| `foxos notes paragraph-alignment activate` | `notes_paragraph-alignment_activate` | modify | Paragraph Alignment |
| `foxos notes paragraph-up move` | `notes_paragraph-up_move` | modify | Move Paragraph Up |
| `foxos notes paragraph-down move` | `notes_paragraph-down_move` | modify | Move Paragraph Down |
| `foxos notes styles activate` | `notes_styles_activate` | modify | Styles |
| `foxos notes do-tag activate` | `notes_do-tag_activate` | modify | To Do Tag |
| `foxos notes tags activate` | `notes_tags_activate` | modify | Tags |
| `foxos notes tags search` | `notes_tags_search` | read | Find Tags |
| `foxos notes dictate activate` | `notes_dictate_activate` | modify | Dictate |
| `foxos notes assist activate` | `notes_assist_activate` | modify | Assist |
| `foxos notes email-page activate` | `notes_email-page_activate` | modify | Email Page |
| `foxos notes notebooks activate` | `notes_notebooks_activate` | modify | Notebooks |
| `foxos notes search search` | `notes_search_search` | read | Search |
| `foxos notes recent-notes activate` | `notes_recent-notes_activate` | modify | Recent Notes |
| `foxos notes account activate` | `notes_account_activate` | modify | Account |
| `foxos notes quick-notes activate` | `notes_quick-notes_activate` | modify | Quick Notes |
| `foxos notes section-2 create` | `notes_section-2_create` | modify | Add section |
| `foxos notes sections-pane resize` | `notes_sections-pane_resize` | modify | Resize sections pane |
| `foxos notes pages sort` | `notes_pages_sort` | read | Sort pages |
| `foxos notes untitled-page activate` | `notes_untitled-page_activate` | modify | Untitled Page |
| `foxos notes page create` | `notes_page_create` | modify | Add page |
| `foxos notes pages-pane resize` | `notes_pages-pane_resize` | modify | Resize pages pane |
| `foxos notes page-date activate` | `notes_page-date_activate` | modify | Page date |
| `foxos notes page-time activate` | `notes_page-time_activate` | modify | Page time |
| `foxos notes pagectrlaltn create` | `notes_pagectrlaltn_create` | modify | New PageCtrl+Alt+N |
| `foxos notes sectionctrlaltt create` | `notes_sectionctrlaltt_create` | modify | New SectionCtrl+Alt+T |
| `foxos notes section-group create` | `notes_section-group_create` | modify | New Section Group |
| `foxos notes notebook create` | `notes_notebook_create` | modify | New Notebook... |
| `foxos notes import import` | `notes_import_import` | modify | Import... |
| `foxos notes export export` | `notes_export_export` | modify | Export |
| `foxos notes more-commands-share share` | `notes_more-commands-share_share` | modify | Share... |
| `foxos notes ctrlp print` | `notes_ctrlp_print` | read | Print...Ctrl+P |
| `foxos notes sync-nowctrls activate` | `notes_sync-nowctrls_activate` | modify | Sync NowCtrl+S |
| `foxos notes deleted-notes activate` | `notes_deleted-notes_activate` | modify | Deleted Notes |
| `foxos notes protected-sectionsctrlaltl lock` | `notes_protected-sectionsctrlaltl_lock` | modify | Lock All Protected SectionsCtrl+Alt+L |
| `foxos notes theme activate` | `notes_theme_activate` | modify | Theme |
| `foxos notes keyboard-shortcutsctrlshift activate` | `notes_keyboard-shortcutsctrlshift_activate` | modify | Keyboard ShortcutsCtrl+Shift+/ |
| `foxos notes notes show` | `notes_notes_show` | read | About Notes |
| `foxos notes file-pagectrlaltn create` | `notes_file-pagectrlaltn_create` | modify | New PageCtrl+Alt+N |
| `foxos notes file-sectionctrlaltt create` | `notes_file-sectionctrlaltt_create` | modify | New SectionCtrl+Alt+T |
| `foxos notes file-section-group create` | `notes_file-section-group_create` | modify | New Section Group |
| `foxos notes file-notebook create` | `notes_file-notebook_create` | modify | New Notebook... |
| `foxos notes file-import import` | `notes_file-import_import` | modify | Import... |
| `foxos notes file-export export` | `notes_file-export_export` | modify | Export |
| `foxos notes file-share share` | `notes_file-share_share` | modify | Share... |
| `foxos notes file-ctrlp print` | `notes_file-ctrlp_print` | read | Print...Ctrl+P |
| `foxos notes file-sync-nowctrls activate` | `notes_file-sync-nowctrls_activate` | modify | Sync NowCtrl+S |
| `foxos notes file-deleted-notes activate` | `notes_file-deleted-notes_activate` | modify | Deleted Notes |
| `foxos notes file-protected-sectionsctrlaltl lock` | `notes_file-protected-sectionsctrlaltl_lock` | modify | Lock All Protected SectionsCtrl+Alt+L |
| `foxos notes file-theme activate` | `notes_file-theme_activate` | modify | Theme |
| `foxos notes file-keyboard-shortcutsctrlshift activate` | `notes_file-keyboard-shortcutsctrlshift_activate` | modify | Keyboard ShortcutsCtrl+Shift+/ |
| `foxos notes file-notes show` | `notes_file-notes_show` | read | About Notes |
| `foxos notes page-title activate` | `notes_page-title_activate` | modify | Page Title |
| `foxos notes citation activate` | `notes_citation_activate` | modify | Citation |
| `foxos notes quote activate` | `notes_quote_activate` | modify | Quote |
| `foxos notes code activate` | `notes_code_activate` | modify | Code |
| `foxos notes website-visit activate` | `notes_website-visit_activate` | modify | Website to visit |
| `foxos notes idea activate` | `notes_idea_activate` | modify | Idea |
| `foxos notes password activate` | `notes_password_activate` | modify | Password |
| `foxos notes critical activate` | `notes_critical_activate` | modify | Critical |
| `foxos notes project activate` | `notes_project_activate` | modify | Project A |
| `foxos notes project-b activate` | `notes_project-b_activate` | modify | Project B |
| `foxos notes movie-see activate` | `notes_movie-see_activate` | modify | Movie to see |
| `foxos notes book-read activate` | `notes_book-read_activate` | modify | Book to read |
| `foxos notes music-listen activate` | `notes_music-listen_activate` | modify | Music to listen to |
| `foxos notes discuss-manager activate` | `notes_discuss-manager_activate` | modify | Discuss with manager |
| `foxos notes email send` | `notes_email_send` | modify | Send in email |
| `foxos notes meeting schedule` | `notes_meeting_schedule` | modify | Schedule meeting |
| `foxos notes call-back activate` | `notes_call-back_activate` | modify | Call back |
| `foxos notes client-request activate` | `notes_client-request_activate` | modify | Client request |
| `foxos notes tags-2 search` | `notes_tags-2_search` | read | Find Tags |
| `foxos notes account-theme activate` | `notes_account-theme_activate` | modify | Theme |
| `foxos notes keyboard-shortcuts activate` | `notes_keyboard-shortcuts_activate` | modify | Keyboard Shortcuts |
| `foxos notes account-notes show` | `notes_account-notes_show` | read | About Notes |
| `foxos notes local-s-notebook activate` | `notes_local-s-notebook_activate` | modify | local's Notebook |
| `foxos notes notebook-locals-notebook-switch-notebook-noteboo create` | `notes_notebook-locals-notebook-switch-notebook-noteboo_create` | modify | Add Notebook |
| `foxos notes notebook-settings activate` | `notes_notebook-settings_activate` | modify | Notebook Settings |
| `foxos notes none-order activate` | `notes_none-order_activate` | modify | None (your order) |
| `foxos notes date-created activate` | `notes_date-created_activate` | modify | Date created |
| `foxos notes date-modified activate` | `notes_date-modified_activate` | modify | Date modified |
| `foxos notes alphabetical activate` | `notes_alphabetical_activate` | modify | Alphabetical |

### records（`records`，16 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos records account select TARGET` | `records_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos records content dismiss` | `records_content_dismiss` | read | Skip to content |
| `foxos records home show` | `records_home_show` | read | Home |
| `foxos records trash delete` | `records_trash_delete` | delete | Trash |
| `foxos records base create` | `records_base_create` | modify | Create base |
| `foxos records source-code-github-opens-tab show` | `records_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos records search-bases set VALUE [--submit]` | `records_search-bases_set` | modify | Search bases |
| `foxos records from-scratcha-blank-base-one-table start` | `records_from-scratcha-blank-base-one-table_start` | modify | Start from scratchA blank base with one table. |
| `foxos records base-2 create` | `records_base-2_create` | modify | Create base |
| `foxos records notice dismiss` | `records_notice_dismiss` | read | Dismiss notice |
| `foxos records it dismiss` | `records_it_dismiss` | read | Got it |
| `foxos records appearance activate` | `records_appearance_activate` | modify | Appearance |
| `foxos records keyboard-shortcuts activate` | `records_keyboard-shortcuts_activate` | modify | Keyboard shortcuts? |
| `foxos records preview show` | `records_preview_show` | read | About this preview |
| `foxos records source-code-github activate` | `records_source-code-github_activate` | modify | Source code on GitHub↗ |
| `foxos records command-palette show` | `records_command-palette_show` | read | 快捷键 mod+k |

### meetings（`meetings`，17 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos meetings item select TARGET` | `meetings_item_select` | read | #（7 项，如 Sunday, November 8） |
| `foxos meetings meeting create TARGET` | `meetings_meeting_create` | modify | create a meeting for *（1 项，如 Create a meeting for later） |
| `foxos meetings settings show` | `meetings_settings_show` | read | Settings |
| `foxos meetings theme toggle` | `meetings_theme_toggle` | modify | Toggle theme |
| `foxos meetings out sign` | `meetings_out_sign` | modify | Sign out |
| `foxos meetings meeting-2 create` | `meetings_meeting-2_create` | modify | New meeting |
| `foxos meetings meeting-code-or-link set VALUE [--submit]` | `meetings_meeting-code-or-link_set` | modify | Meeting code or link |
| `foxos meetings join join` | `meetings_join_join` | modify | Join |
| `foxos meetings today activate` | `meetings_today_activate` | modify | Today |
| `foxos meetings week previous` | `meetings_week_previous` | read | Previous week |
| `foxos meetings week next` | `meetings_week_next` | read | Next week |
| `foxos meetings try-again activate` | `meetings_try-again_activate` | modify | Try again |
| `foxos meetings refresh activate` | `meetings_refresh_activate` | modify | Refresh |
| `foxos meetings close close` | `meetings_close_close` | read | Close |
| `foxos meetings nickname set VALUE [--submit]` | `meetings_nickname_set` | modify | Nickname |
| `foxos meetings nickname save` | `meetings_nickname_save` | modify | Save nickname |
| `foxos meetings instant-meeting start` | `meetings_instant-meeting_start` | modify | Start an instant meeting |

### teamchat（`teamchat`，6 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos teamchat workspacestart-space create TARGET` | `teamchat_workspacestart-space_create` | modify | create a workspacestart a space for *（1 项，如 Create a workspaceStart a space for your team） |
| `foxos teamchat workspacestart-space-2 create TARGET` | `teamchat_workspacestart-space-2_create` | modify | create a workspacestart a space for *（1 项，如 Create a workspaceStart a space for your team and invite people） |
| `foxos teamchat messages dismiss` | `teamchat_messages_dismiss` | read | Skip to messages |
| `foxos teamchat invitepaste-code-or-link join` | `teamchat_invitepaste-code-or-link_join` | modify | Join with an invitePaste a code or link |
| `foxos teamchat puter show` | `teamchat_puter_show` | read | Puter |
| `foxos teamchat close close` | `teamchat_close_close` | read | Close |

### email（`email`，2 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos email grant-read-access activate` | `email_grant-read-access_activate` | modify | Grant read access |
| `foxos email command-palette show` | `email_command-palette_show` | read | 快捷键 mod+k |

### contacts（`contacts`，28 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos contacts account-menu activate` | `contacts_account-menu_activate` | modify | Account menu |
| `foxos contacts smart-add activate` | `contacts_smart-add_activate` | modify | Smart add |
| `foxos contacts contact create` | `contacts_contact_create` | modify | New contact |
| `foxos contacts search-contacts set VALUE [--submit]` | `contacts_search-contacts_set` | modify | Search contacts |
| `foxos contacts list-options activate` | `contacts_list-options_activate` | modify | List options |
| `foxos contacts favorites activate` | `contacts_favorites_activate` | modify | Favorites |
| `foxos contacts contact-2 create` | `contacts_contact-2_create` | modify | New contact |
| `foxos contacts import import` | `contacts_import_import` | modify | Import |
| `foxos contacts contact-3 create` | `contacts_contact-3_create` | modify | New contact |
| `foxos contacts set-photo activate` | `contacts_set-photo_activate` | modify | Set photo |
| `foxos contacts close close` | `contacts_close_close` | read | Close |
| `foxos contacts first-name set VALUE [--submit]` | `contacts_first-name_set` | modify | First name |
| `foxos contacts last-name set VALUE [--submit]` | `contacts_last-name_set` | modify | Last name |
| `foxos contacts nickname set VALUE [--submit]` | `contacts_nickname_set` | modify | Nickname |
| `foxos contacts company set VALUE [--submit]` | `contacts_company_set` | modify | Company |
| `foxos contacts job-title set VALUE [--submit]` | `contacts_job-title_set` | modify | Job title |
| `foxos contacts email create` | `contacts_email_create` | modify | Add email |
| `foxos contacts phone create` | `contacts_phone_create` | modify | Add phone |
| `foxos contacts link create` | `contacts_link_create` | modify | Add link |
| `foxos contacts address create` | `contacts_address_create` | modify | Add address |
| `foxos contacts birthday set VALUE [--submit]` | `contacts_birthday_set` | modify | Birthday |
| `foxos contacts hide-year toggle` | `contacts_hide-year_toggle` | modify | Hide year |
| `foxos contacts tags set VALUE [--submit]` | `contacts_tags_set` | modify | Tags |
| `foxos contacts notes set VALUE [--submit]` | `contacts_notes_set` | modify | Notes |
| `foxos contacts add-favorites toggle` | `contacts_add-favorites_toggle` | modify | Add to favorites |
| `foxos contacts cancel cancel` | `contacts_cancel_cancel` | read | Cancel |
| `foxos contacts contact-4 create` | `contacts_contact-4_create` | modify | Add contact |
| `foxos contacts selection select-all` | `contacts_selection_select-all` | modify | 快捷键 mod+a |

### calendar（`calendar`，36 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos calendar day-view select TARGET` | `calendar_day-view_select` | read | # day view（1 项，如 4 Day view） |
| `foxos calendar item select TARGET` | `calendar_item_select` | read | #（34 项，如 Sun Nov 01 2026） |
| `foxos calendar selected select TARGET` | `calendar_selected_select` | read | #, selected（1 项，如 Tue Nov 10 2026, selected） |
| `foxos calendar open open TARGET` | `calendar_open_open` | read | open #（35 项，如 Open Sun, November 1, 2026） |
| `foxos calendar public-holiday select TARGET` | `calendar_public-holiday_select` | read | public holiday: *（2 项，如 Public holiday: Veterans Day） |
| `foxos calendar year-view-open open TARGET` | `calendar_year-view-open_open` | read | open #（12 项，如 Open January） |
| `foxos calendar year-view-item select TARGET` | `calendar_year-view-item_select` | read | #（330 项，如 Thu Jan 01 2026） |
| `foxos calendar go select TARGET` | `calendar_go_select` | read | go to #（7 项，如 Go to Sun, November 8, 2026） |
| `foxos calendar week start TARGET` | `calendar_week_start` | modify | start week on #（1 项，如 Start week on Monday） |
| `foxos calendar time select TARGET` | `calendar_time_select` | read | # time（1 项，如 24-hour time） |
| `foxos calendar today activate` | `calendar_today_activate` | modify | Today |
| `foxos calendar previous previous` | `calendar_previous_previous` | read | Previous |
| `foxos calendar next next` | `calendar_next_next` | read | Next |
| `foxos calendar events-tasks search` | `calendar_events-tasks_search` | read | Search events and tasks |
| `foxos calendar year-view activate` | `calendar_year-view_activate` | modify | Year view |
| `foxos calendar month-view activate` | `calendar_month-view_activate` | modify | Month view |
| `foxos calendar week-view activate` | `calendar_week-view_activate` | modify | Week view |
| `foxos calendar day-view activate` | `calendar_day-view_activate` | modify | Day view |
| `foxos calendar list-view activate` | `calendar_list-view_activate` | modify | List view |
| `foxos calendar account-settings activate` | `calendar_account-settings_activate` | modify | Account and settings |
| `foxos calendar create create` | `calendar_create_create` | modify | Create |
| `foxos calendar month previous` | `calendar_month_previous` | read | Previous month |
| `foxos calendar month next` | `calendar_month_next` | read | Next month |
| `foxos calendar booking-links hide` | `calendar_booking-links_hide` | read | Hide booking links |
| `foxos calendar link-that-lets-others-book-time-you share` | `calendar_link-that-lets-others-book-time-you_share` | modify | Share a link that lets others book time with you |
| `foxos calendar event create` | `calendar_event_create` | modify | New event |
| `foxos calendar auto activate` | `calendar_auto_activate` | modify | Auto |
| `foxos calendar light activate` | `calendar_light_activate` | modify | Light |
| `foxos calendar dark activate` | `calendar_dark_activate` | modify | Dark |
| `foxos calendar secondary-time-zone set VALUE [--submit]` | `calendar_secondary-time-zone_set` | modify | Secondary time zone |
| `foxos calendar public-holidays set VALUE [--submit]` | `calendar_public-holidays_set` | modify | Public holidays |
| `foxos calendar clock-changes-daylight-saving toggle` | `calendar_clock-changes-daylight-saving_toggle` | modify | Clock changes (daylight saving) |
| `foxos calendar export import` | `calendar_export_import` | modify | Import & export |
| `foxos calendar out sign` | `calendar_out_sign` | modify | Sign out |
| `foxos calendar document export` | `calendar_document_export` | modify | 快捷键 mod+e |
| `foxos calendar command-palette show` | `calendar_command-palette_show` | read | 快捷键 mod+k |

### signatures（`signatures`，29 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos signatures 0out select TARGET` | `signatures_0out_select` | read | 0out for *（1 项，如 0Out for signature） |
| `foxos signatures 0waiting select TARGET` | `signatures_0waiting_select` | read | 0waiting for *（1 项，如 0Waiting for you） |
| `foxos signatures main select TARGET` | `signatures_main_select` | read | #（1 项，如 0Completed） |
| `foxos signatures out select TARGET` | `signatures_out_select` | read | out for *（1 项，如 Out for signature） |
| `foxos signatures waiting select TARGET` | `signatures_waiting_select` | read | waiting for *（1 项，如 Waiting for you） |
| `foxos signatures skip dismiss TARGET` | `signatures_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos signatures signer-declinessigning-closes select TARGET` | `signatures_signer-declinessigning-closes_select` | read | a signer declinessigning closes for *（1 项，如 A signer declinesSigning closes for everyone, so this one usually needs you） |
| `foxos signatures signatures-githubsend-documents select TARGET` | `signatures_signatures-githubsend-documents_select` | read | signatures on githubsend documents for *（1 项，如 Signatures on GitHubSend documents for signature, powered by Puter） |
| `foxos signatures documents show` | `signatures_documents_show` | read | Documents |
| `foxos signatures settings show` | `signatures_settings_show` | read | Settings |
| `foxos signatures document create` | `signatures_document_create` | modify | New document |
| `foxos signatures document-2 create` | `signatures_document-2_create` | modify | New document |
| `foxos signatures search-documents set VALUE [--submit]` | `signatures_search-documents_set` | modify | Search documents |
| `foxos signatures drafts activate` | `signatures_drafts_activate` | modify | Drafts |
| `foxos signatures completed activate` | `signatures_completed_activate` | modify | Completed |
| `foxos signatures closed activate` | `signatures_closed_activate` | modify | Closed |
| `foxos signatures pdf import` | `signatures_pdf_import` | modify | Upload a PDF |
| `foxos signatures close close` | `signatures_close_close` | read | Close |
| `foxos signatures set-up-account activate` | `signatures_set-up-account_activate` | modify | Set up my account |
| `foxos signatures explore-sample-documents activate` | `signatures_explore-sample-documents_activate` | modify | Explore with sample documents |
| `foxos signatures name-shown-signers set VALUE [--submit]` | `signatures_name-shown-signers_set` | modify | Name shown to signers |
| `foxos signatures system activate` | `signatures_system_activate` | modify | System |
| `foxos signatures light activate` | `signatures_light_activate` | modify | Light |
| `foxos signatures dark activate` | `signatures_dark_activate` | modify | Dark |
| `foxos signatures documents-expire set VALUE [--submit]` | `signatures_documents-expire_set` | modify | Documents expire |
| `foxos signatures remind-signers set VALUE [--submit]` | `signatures_remind-signers_set` | modify | Remind signers |
| `foxos signatures any-signer-signsone-email-per-signature toggle` | `signatures_any-signer-signsone-email-per-signature_toggle` | modify | Any signer signsOne email per signature |
| `foxos signatures signature create` | `signatures_signature_create` | modify | Create signature |
| `foxos signatures puteryour-documents-live-own-puter-cloud show` | `signatures_puteryour-documents-live-own-puter-cloud_show` | read | PuterYour documents live in your own Puter cloud |

### photo-studio（`photo-studio`，103 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos photo-studio sheet create TARGET` | `photo-studio_sheet_create` | modify | create # sheet（1 项，如 Create A4 sheet） |
| `foxos photo-studio photo-print create TARGET` | `photo-studio_photo-print_create` | modify | create photo print #（1 项，如 Create Photo print 6 × 4） |
| `foxos photo-studio copy export TARGET` | `photo-studio_copy_export` | modify | export a copy for *（1 项，如 Export a copy for the web, repeat it in one click and keep an editable project.） |
| `foxos photo-studio edit update` | `photo-studio_edit_update` | modify | Edit |
| `foxos photo-studio image activate` | `photo-studio_image_activate` | modify | Image |
| `foxos photo-studio layer activate` | `photo-studio_layer_activate` | modify | Layer |
| `foxos photo-studio type activate` | `photo-studio_type_activate` | modify | Type |
| `foxos photo-studio select select` | `photo-studio_select_select` | read | Select |
| `foxos photo-studio filter filter` | `photo-studio_filter_filter` | read | Filter |
| `foxos photo-studio view show` | `photo-studio_view_show` | read | View |
| `foxos photo-studio window activate` | `photo-studio_window_activate` | modify | Window |
| `foxos photo-studio help show` | `photo-studio_help_show` | read | Help |
| `foxos photo-studio commands search` | `photo-studio_commands_search` | read | Search commands |
| `foxos photo-studio puter save` | `photo-studio_puter_save` | modify | Save to Puter |
| `foxos photo-studio export export` | `photo-studio_export_export` | modify | Export |
| `foxos photo-studio puter-account activate` | `photo-studio_puter-account_activate` | modify | Puter account |
| `foxos photo-studio tool-presets activate` | `photo-studio_tool-presets_activate` | modify | Tool presets |
| `foxos photo-studio tool-presets-2 activate` | `photo-studio_tool-presets-2_activate` | modify | Tool Presets |
| `foxos photo-studio color-theme set VALUE [--submit]` | `photo-studio_color-theme_set` | modify | Color theme |
| `foxos photo-studio panels toggle` | `photo-studio_panels_toggle` | modify | Toggle panels |
| `foxos photo-studio default-colors activate` | `photo-studio_default-colors_activate` | modify | Default colors |
| `foxos photo-studio switch-colors activate` | `photo-studio_switch-colors_activate` | modify | Switch colors |
| `foxos photo-studio background-color activate` | `photo-studio_background-color_activate` | modify | Background color |
| `foxos photo-studio foreground-color activate` | `photo-studio_foreground-color_activate` | modify | Foreground color |
| `foxos photo-studio foreground-color-value set VALUE [--submit]` | `photo-studio_foreground-color-value_set` | modify | Foreground color value |
| `foxos photo-studio quick-mask-mode activate` | `photo-studio_quick-mask-mode_activate` | modify | Quick Mask mode |
| `foxos photo-studio screen-mode update` | `photo-studio_screen-mode_update` | modify | Change screen mode |
| `foxos photo-studio image-canvas activate` | `photo-studio_image-canvas_activate` | modify | Image canvas |
| `foxos photo-studio image open` | `photo-studio_image_open` | read | Open an image |
| `foxos photo-studio document create` | `photo-studio_document_create` | modify | New document |
| `foxos photo-studio describe-edit set VALUE [--submit]` | `photo-studio_describe-edit_set` | modify | Describe an edit |
| `foxos photo-studio image select` | `photo-studio_image_select` | read | Choose image… |
| `foxos photo-studio start start` | `photo-studio_start_start` | modify | Start |
| `foxos photo-studio large-web-page create` | `photo-studio_large-web-page_create` | modify | Create Large web page |
| `foxos photo-studio square-social-post create` | `photo-studio_square-social-post_create` | modify | Create Square social post |
| `foxos photo-studio standard-phone create` | `photo-studio_standard-phone_create` | modify | Create Standard phone |
| `foxos photo-studio presets-custom-sizes activate` | `photo-studio_presets-custom-sizes_activate` | modify | All presets and custom sizes |
| `foxos photo-studio what-s-newrecent-features activate` | `photo-studio_what-s-newrecent-features_activate` | modify | What’s NewRecent features |
| `foxos photo-studio assistant activate` | `photo-studio_assistant_activate` | modify | Assistant |
| `foxos photo-studio generation-history activate` | `photo-studio_generation-history_activate` | modify | Generation History |
| `foxos photo-studio history activate` | `photo-studio_history_activate` | modify | History |
| `foxos photo-studio actions activate` | `photo-studio_actions_activate` | modify | Actions |
| `foxos photo-studio version-history activate` | `photo-studio_version-history_activate` | modify | Version History |
| `foxos photo-studio navigator activate` | `photo-studio_navigator_activate` | modify | Navigator |
| `foxos photo-studio info activate` | `photo-studio_info_activate` | modify | Info |
| `foxos photo-studio histogram activate` | `photo-studio_histogram_activate` | modify | Histogram |
| `foxos photo-studio brushes activate` | `photo-studio_brushes_activate` | modify | Brushes |
| `foxos photo-studio brush-settings activate` | `photo-studio_brush-settings_activate` | modify | Brush Settings |
| `foxos photo-studio character activate` | `photo-studio_character_activate` | modify | Character |
| `foxos photo-studio paragraph activate` | `photo-studio_paragraph_activate` | modify | Paragraph |
| `foxos photo-studio styles activate` | `photo-studio_styles_activate` | modify | Styles |
| `foxos photo-studio layer-comps activate` | `photo-studio_layer-comps_activate` | modify | Layer Comps |
| `foxos photo-studio scripts activate` | `photo-studio_scripts_activate` | modify | Scripts |
| `foxos photo-studio color show` | `photo-studio_color_show` | read | Color |
| `foxos photo-studio swatches show` | `photo-studio_swatches_show` | read | Swatches |
| `foxos photo-studio gradients show` | `photo-studio_gradients_show` | read | Gradients |
| `foxos photo-studio patterns show` | `photo-studio_patterns_show` | read | Patterns |
| `foxos photo-studio color-panel-menu activate` | `photo-studio_color-panel-menu_activate` | modify | Color panel menu |
| `foxos photo-studio color-saturation-brightness set VALUE [--submit]` | `photo-studio_color-saturation-brightness_set` | modify | Color saturation and brightness |
| `foxos photo-studio color-hue set VALUE [--submit]` | `photo-studio_color-hue_set` | modify | Color hue |
| `foxos photo-studio hex-color set VALUE [--submit]` | `photo-studio_hex-color_set` | modify | Hex color |
| `foxos photo-studio properties show` | `photo-studio_properties_show` | read | Properties |
| `foxos photo-studio adjustments show` | `photo-studio_adjustments_show` | read | Adjustments |
| `foxos photo-studio properties-panel-menu activate` | `photo-studio_properties-panel-menu_activate` | modify | Properties panel menu |
| `foxos photo-studio image-size activate` | `photo-studio_image-size_activate` | modify | Image size |
| `foxos photo-studio layers show` | `photo-studio_layers_show` | read | Layers |
| `foxos photo-studio channels show` | `photo-studio_channels_show` | read | Channels |
| `foxos photo-studio paths show` | `photo-studio_paths_show` | read | Paths |
| `foxos photo-studio layers-panel-menu activate` | `photo-studio_layers-panel-menu_activate` | modify | Layers panel menu |
| `foxos photo-studio filter-layers-by-kind set VALUE [--submit]` | `photo-studio_filter-layers-by-kind_set` | modify | Filter layers by kind |
| `foxos photo-studio filter-layers-by-name set VALUE [--submit]` | `photo-studio_filter-layers-by-name_set` | modify | Filter layers by name |
| `foxos photo-studio layer-filtering activate` | `photo-studio_layer-filtering_activate` | modify | Layer filtering |
| `foxos photo-studio blend-mode set VALUE [--submit]` | `photo-studio_blend-mode_set` | modify | Blend mode |
| `foxos photo-studio opacity set VALUE [--submit]` | `photo-studio_opacity_set` | modify | Opacity % |
| `foxos photo-studio transparency lock` | `photo-studio_transparency_lock` | modify | Lock transparency |
| `foxos photo-studio image-pixels lock` | `photo-studio_image-pixels_lock` | modify | Lock image pixels |
| `foxos photo-studio position lock` | `photo-studio_position_lock` | modify | Lock position |
| `foxos photo-studio layer lock` | `photo-studio_layer_lock` | modify | Lock layer |
| `foxos photo-studio fill set VALUE [--submit]` | `photo-studio_fill_set` | modify | Fill % |
| `foxos photo-studio image create` | `photo-studio_image_create` | modify | Add an image |
| `foxos photo-studio link-layers activate` | `photo-studio_link-layers_activate` | modify | Link layers |
| `foxos photo-studio layer-style create` | `photo-studio_layer-style_create` | modify | Add a layer style |
| `foxos photo-studio layer-mask create` | `photo-studio_layer-mask_create` | modify | Add layer mask |
| `foxos photo-studio fill-or-adjustment-layer create` | `photo-studio_fill-or-adjustment-layer_create` | modify | New fill or adjustment layer |
| `foxos photo-studio group create` | `photo-studio_group_create` | modify | New group |
| `foxos photo-studio layer create` | `photo-studio_layer_create` | modify | New layer |
| `foxos photo-studio layer delete` | `photo-studio_layer_delete` | delete | Delete layer |
| `foxos photo-studio view zoom-out` | `photo-studio_view_zoom-out` | modify | Zoom out |
| `foxos photo-studio zoom-level set VALUE [--submit]` | `photo-studio_zoom-level_set` | modify | Zoom level |
| `foxos photo-studio view zoom-` | `photo-studio_view_zoom-` | modify | Zoom in |
| `foxos photo-studio document-sizes activate` | `photo-studio_document-sizes_activate` | modify | Document Sizes: |
| `foxos photo-studio puter show` | `photo-studio_puter_show` | read | Puter |
| `foxos photo-studio icon collapse` | `photo-studio_icon_collapse` | read | Collapse to Icon |
| `foxos photo-studio close close` | `photo-studio_close_close` | read | Close |
| `foxos photo-studio tab-group close` | `photo-studio_tab-group_close` | read | Close Tab Group |
| `foxos photo-studio shortcut key-0` | `photo-studio_shortcut_key-0` | modify | 快捷键 mod+0 |
| `foxos photo-studio selection select-all` | `photo-studio_selection_select-all` | modify | 快捷键 mod+a |
| `foxos photo-studio selection lock` | `photo-studio_selection_lock` | modify | 快捷键 mod+l |
| `foxos photo-studio document save` | `photo-studio_document_save` | modify | 快捷键 mod+s |
| `foxos photo-studio edit redo` | `photo-studio_edit_redo` | modify | 快捷键 mod+shift+z |
| `foxos photo-studio clipboard paste` | `photo-studio_clipboard_paste` | modify | 快捷键 mod+v |
| `foxos photo-studio shortcut key-w` | `photo-studio_shortcut_key-w` | modify | 快捷键 mod+w |
| `foxos photo-studio edit undo` | `photo-studio_edit_undo` | modify | 快捷键 mod+z |

### video-studio（`video-studio`，34 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos video-studio account select TARGET` | `video-studio_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos video-studio browse-ready-made-projects-make-own select TARGET` | `video-studio_browse-ready-made-projects-make-own_select` | read | browse # ready-made projects to make your own（1 项，如 Browse templates10 ready-made projects to make your own） |
| `foxos video-studio youtube-project select TARGET` | `video-studio_youtube-project_select` | read | # youtube, new project（1 项，如 16:9 YouTube, new project） |
| `foxos video-studio vertical-project select TARGET` | `video-studio_vertical-project_select` | read | # vertical, new project（1 项，如 9:16 Vertical, new project） |
| `foxos video-studio square-project select TARGET` | `video-studio_square-project_select` | read | # square, new project（1 项，如 1:1 Square, new project） |
| `foxos video-studio classic-project select TARGET` | `video-studio_classic-project_select` | read | # classic, new project（1 项，如 4:3 Classic, new project） |
| `foxos video-studio portrait-project select TARGET` | `video-studio_portrait-project_select` | read | # portrait, new project（1 项，如 3:4 Portrait, new project） |
| `foxos video-studio feed-post-project select TARGET` | `video-studio_feed-post-project_select` | read | # feed post, new project（1 项，如 4:5 Feed post, new project） |
| `foxos video-studio cinema-project select TARGET` | `video-studio_cinema-project_select` | read | # cinema, new project（1 项，如 21:9 Cinema, new project） |
| `foxos video-studio item select TARGET` | `video-studio_item_select` | read | # title intro, intros and outros, # a bold title over a glowing backdrop with a slow push in.（1 项，如 16:9 Title intro, Intros and outros, 00:06. A bold title over a glowing backdrop with a slow push in.） |
| `foxos video-studio item-2 select TARGET` | `video-studio_item-2_select` | read | # photo slideshow, slideshows, # slots. four photo slots with gentle motion, soft transitions and captions.（1 项，如 16:9 Photo slideshow, Slideshows, 00:14, 4 slots. Four photo slots with gentle motion, soft transitions and captions.） |
| `foxos video-studio item-3 select TARGET` | `video-studio_item-3_select` | read | # quote card, social, # a typed-out quote with an author line on a warm paper backdrop.（1 项，如 1:1 Quote card, Social, 00:08. A typed-out quote with an author line on a warm paper backdrop.） |
| `foxos video-studio item-4 select TARGET` | `video-studio_item-4_select` | read | # countdown, intros and outros, # five, four, three, two, one with a pulsing ring and a flash at go.（1 项，如 16:9 Countdown, Intros and outros, 00:07. Five, four, three, two, one with a pulsing ring and a flash at go.） |
| `foxos video-studio item-5 select TARGET` | `video-studio_item-5_select` | read | # product promo, business, # slot. show off a product with a price burst and a call to action.（1 项，如 4:5 Product promo, Business, 00:09, 1 slot. Show off a product with a price burst and a call to action.） |
| `foxos video-studio item-6 select TARGET` | `video-studio_item-6_select` | read | # vertical story, social, # slots. three tall photo slots that push up, with neon and script titles.（1 项，如 9:16 Vertical story, Social, 00:09, 3 slots. Three tall photo slots that push up, with neon and script titles.） |
| `foxos video-studio editor dismiss` | `video-studio_editor_dismiss` | read | Skip to editor |
| `foxos video-studio home show` | `video-studio_home_show` | read | Home |
| `foxos video-studio templates show` | `video-studio_templates_show` | read | Templates |
| `foxos video-studio trash delete` | `video-studio_trash_delete` | delete | Trash |
| `foxos video-studio editopen-media-project import` | `video-studio_editopen-media-project_import` | modify | Import and editOpen media in a new project |
| `foxos video-studio see show` | `video-studio_see_show` | read | See all |
| `foxos video-studio search-projects set VALUE [--submit]` | `video-studio_search-projects_set` | modify | Search projects |
| `foxos video-studio sort sort` | `video-studio_sort_sort` | read | Sort |
| `foxos video-studio as-list show` | `video-studio_as-list_show` | read | Show as list |
| `foxos video-studio project-actions show` | `video-studio_project-actions_show` | read | More project actions |
| `foxos video-studio powered-by-puter show` | `video-studio_powered-by-puter_show` | read | Powered by Puter |
| `foxos video-studio theme activate` | `video-studio_theme_activate` | modify | Theme |
| `foxos video-studio last-modified activate` | `video-studio_last-modified_activate` | modify | Last modified |
| `foxos video-studio date-created activate` | `video-studio_date-created_activate` | modify | Date created |
| `foxos video-studio name activate` | `video-studio_name_activate` | modify | Name |
| `foxos video-studio project-file open` | `video-studio_project-file_open` | read | Open project file... |
| `foxos video-studio media import` | `video-studio_media_import` | modify | Import media... |
| `foxos video-studio more-project-actions-trash delete` | `video-studio_more-project-actions-trash_delete` | delete | Trash |
| `foxos video-studio selection select-all` | `video-studio_selection_select-all` | modify | 快捷键 mod+a |

### vector-studio（`vector-studio`，88 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos vector-studio account select TARGET` | `vector-studio_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos vector-studio drawing-modes select TARGET` | `vector-studio_drawing-modes_select` | read | drawing modes: *（1 项，如 Drawing Modes: Draw Normal） |
| `foxos vector-studio letter-x select TARGET` | `vector-studio_letter-x_select` | read | letter # x # in（1 项，如 Letter 8.5 x 11 in） |
| `foxos vector-studio x-mm select TARGET` | `vector-studio_x-mm_select` | read | # x # mm（1 项，如 A4 210 x 297 mm） |
| `foxos vector-studio postcard-x-pt select TARGET` | `vector-studio_postcard-x-pt_select` | read | postcard # x # pt（1 项，如 Postcard 288 x 560 pt） |
| `foxos vector-studio web-x-px select TARGET` | `vector-studio_web-x-px_select` | read | web # x # px（1 项，如 Web 1920 x 1080 px） |
| `foxos vector-studio mobile-x-px select TARGET` | `vector-studio_mobile-x-px_select` | read | mobile # x # px（1 项，如 Mobile 390 x 844 px） |
| `foxos vector-studio square-x-px select TARGET` | `vector-studio_square-x-px_select` | read | square # x # px（1 项，如 Square 1080 x 1080 px） |
| `foxos vector-studio icon-x-px select TARGET` | `vector-studio_icon-x-px_select` | read | icon # x # px（1 项，如 Icon 512 x 512 px） |
| `foxos vector-studio poster-x select TARGET` | `vector-studio_poster-x_select` | read | poster # x # in（1 项，如 Poster 18 x 24 in） |
| `foxos vector-studio preview select TARGET` | `vector-studio_preview_select` | read | # preview（1 项，如 Separations Preview） |
| `foxos vector-studio canvas dismiss` | `vector-studio_canvas_dismiss` | read | Skip to canvas |
| `foxos vector-studio home activate` | `vector-studio_home_activate` | modify | Home |
| `foxos vector-studio edit update` | `vector-studio_edit_update` | modify | Edit |
| `foxos vector-studio object activate` | `vector-studio_object_activate` | modify | Object |
| `foxos vector-studio type activate` | `vector-studio_type_activate` | modify | Type |
| `foxos vector-studio select select` | `vector-studio_select_select` | read | Select |
| `foxos vector-studio effect activate` | `vector-studio_effect_activate` | modify | Effect |
| `foxos vector-studio view show` | `vector-studio_view_show` | read | View |
| `foxos vector-studio window activate` | `vector-studio_window_activate` | modify | Window |
| `foxos vector-studio help show` | `vector-studio_help_show` | read | Help |
| `foxos vector-studio theme activate` | `vector-studio_theme_activate` | modify | Theme |
| `foxos vector-studio single-or-double-column-tools toggle` | `vector-studio_single-or-double-column-tools_toggle` | modify | Toggle single or double column tools |
| `foxos vector-studio selection-tool activate` | `vector-studio_selection-tool_activate` | modify | Selection Tool |
| `foxos vector-studio direct-selection-tool activate` | `vector-studio_direct-selection-tool_activate` | modify | Direct Selection Tool |
| `foxos vector-studio magic-wand-tool activate` | `vector-studio_magic-wand-tool_activate` | modify | Magic Wand Tool |
| `foxos vector-studio lasso-tool activate` | `vector-studio_lasso-tool_activate` | modify | Lasso Tool |
| `foxos vector-studio pen-tool activate` | `vector-studio_pen-tool_activate` | modify | Pen Tool |
| `foxos vector-studio curvature-tool activate` | `vector-studio_curvature-tool_activate` | modify | Curvature Tool |
| `foxos vector-studio sketch-shape-tool activate` | `vector-studio_sketch-shape-tool_activate` | modify | Sketch Shape Tool |
| `foxos vector-studio paintbrush-tool activate` | `vector-studio_paintbrush-tool_activate` | modify | Paintbrush Tool |
| `foxos vector-studio rectangle-tool activate` | `vector-studio_rectangle-tool_activate` | modify | Rectangle Tool |
| `foxos vector-studio line-segment-tool activate` | `vector-studio_line-segment-tool_activate` | modify | Line Segment Tool |
| `foxos vector-studio shape-builder-tool activate` | `vector-studio_shape-builder-tool_activate` | modify | Shape Builder Tool |
| `foxos vector-studio type-tool activate` | `vector-studio_type-tool_activate` | modify | Type Tool |
| `foxos vector-studio tool rotate` | `vector-studio_tool_rotate` | modify | Rotate Tool |
| `foxos vector-studio scale-tool activate` | `vector-studio_scale-tool_activate` | modify | Scale Tool |
| `foxos vector-studio width-tool activate` | `vector-studio_width-tool_activate` | modify | Width Tool |
| `foxos vector-studio free-transform-tool activate` | `vector-studio_free-transform-tool_activate` | modify | Free Transform Tool |
| `foxos vector-studio eraser-tool activate` | `vector-studio_eraser-tool_activate` | modify | Eraser Tool |
| `foxos vector-studio perspective-grid-tool activate` | `vector-studio_perspective-grid-tool_activate` | modify | Perspective Grid Tool |
| `foxos vector-studio gradient-tool activate` | `vector-studio_gradient-tool_activate` | modify | Gradient Tool |
| `foxos vector-studio mesh-tool activate` | `vector-studio_mesh-tool_activate` | modify | Mesh Tool |
| `foxos vector-studio eyedropper-tool activate` | `vector-studio_eyedropper-tool_activate` | modify | Eyedropper Tool |
| `foxos vector-studio blend-tool activate` | `vector-studio_blend-tool_activate` | modify | Blend Tool |
| `foxos vector-studio symbol-sprayer-tool activate` | `vector-studio_symbol-sprayer-tool_activate` | modify | Symbol Sprayer Tool |
| `foxos vector-studio column-graph-tool activate` | `vector-studio_column-graph-tool_activate` | modify | Column Graph Tool |
| `foxos vector-studio artboard-tool activate` | `vector-studio_artboard-tool_activate` | modify | Artboard Tool |
| `foxos vector-studio hand-tool activate` | `vector-studio_hand-tool_activate` | modify | Hand Tool |
| `foxos vector-studio view zoom-tool` | `vector-studio_view_zoom-tool` | modify | Zoom Tool |
| `foxos vector-studio fill activate` | `vector-studio_fill_activate` | modify | Fill |
| `foxos vector-studio stroke activate` | `vector-studio_stroke_activate` | modify | Stroke |
| `foxos vector-studio swap-fill-stroke activate` | `vector-studio_swap-fill-stroke_activate` | modify | Swap Fill and Stroke |
| `foxos vector-studio default-fill-stroke activate` | `vector-studio_default-fill-stroke_activate` | modify | Default Fill and Stroke |
| `foxos vector-studio color activate` | `vector-studio_color_activate` | modify | Color |
| `foxos vector-studio gradient activate` | `vector-studio_gradient_activate` | modify | Gradient |
| `foxos vector-studio none activate` | `vector-studio_none_activate` | modify | None |
| `foxos vector-studio tools activate` | `vector-studio_tools_activate` | modify | All tools |
| `foxos vector-studio screen-mode update` | `vector-studio_screen-mode_update` | modify | Change Screen Mode |
| `foxos vector-studio open open` | `vector-studio_open_open` | read | Open |
| `foxos vector-studio home-2 activate` | `vector-studio_home-2_activate` | modify | Home |
| `foxos vector-studio recent activate` | `vector-studio_recent_activate` | modify | Recent |
| `foxos vector-studio files activate` | `vector-studio_files_activate` | modify | Your files |
| `foxos vector-studio templates activate` | `vector-studio_templates_activate` | modify | Templates |
| `foxos vector-studio hide hide` | `vector-studio_hide_hide` | read | Hide |
| `foxos vector-studio presets-sizes-settings show` | `vector-studio_presets-sizes-settings_show` | read | More Presets All sizes and settings |
| `foxos vector-studio refresh-files activate` | `vector-studio_refresh-files_activate` | modify | Refresh Your files |
| `foxos vector-studio powered-by-puter show` | `vector-studio_powered-by-puter_show` | read | Powered by Puter |
| `foxos vector-studio panels activate` | `vector-studio_panels_activate` | modify | Panels |
| `foxos vector-studio color-paint-panels activate` | `vector-studio_color-paint-panels_activate` | modify | Color and Paint panels |
| `foxos vector-studio arrange-shape-panels activate` | `vector-studio_arrange-shape-panels_activate` | modify | Arrange and Shape panels |
| `foxos vector-studio type-panels activate` | `vector-studio_type-panels_activate` | modify | Type panels |
| `foxos vector-studio symbols activate` | `vector-studio_symbols_activate` | modify | Symbols |
| `foxos vector-studio libraries activate` | `vector-studio_libraries_activate` | modify | Libraries |
| `foxos vector-studio asset-export activate` | `vector-studio_asset-export_activate` | modify | Asset Export |
| `foxos vector-studio generate run` | `vector-studio_generate_run` | modify | Generate |
| `foxos vector-studio generation-history activate` | `vector-studio_generation-history_activate` | modify | Generation History |
| `foxos vector-studio document-panels activate` | `vector-studio_document-panels_activate` | modify | Document panels |
| `foxos vector-studio flattener-preview activate` | `vector-studio_flattener-preview_activate` | modify | Flattener Preview |
| `foxos vector-studio variables activate` | `vector-studio_variables_activate` | modify | Variables |
| `foxos vector-studio svg-interactivity activate` | `vector-studio_svg-interactivity_activate` | modify | SVG Interactivity |
| `foxos vector-studio actions activate` | `vector-studio_actions_activate` | modify | Actions |
| `foxos vector-studio mockup activate` | `vector-studio_mockup_activate` | modify | Mockup |
| `foxos vector-studio match-font activate` | `vector-studio_match-font_activate` | modify | Match Font |
| `foxos vector-studio properties show` | `vector-studio_properties_show` | read | Properties |
| `foxos vector-studio layers show` | `vector-studio_layers_show` | read | Layers |
| `foxos vector-studio signed-as-local activate` | `vector-studio_signed-as-local_activate` | modify | Signed in as local |
| `foxos vector-studio shortcut key-5` | `vector-studio_shortcut_key-5` | modify | 快捷键 mod+5 |

### audio-studio（`audio-studio`，147 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos audio-studio account select TARGET` | `audio-studio_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos audio-studio waveform select TARGET` | `audio-studio_waveform_select` | read | waveform (#)（1 项，如 Waveform (9)） |
| `foxos audio-studio multitrack select TARGET` | `audio-studio_multitrack_select` | read | multitrack (#)（1 项，如 Multitrack (0)） |
| `foxos audio-studio selection-tool-e select TARGET` | `audio-studio_selection-tool-e_select` | read | # selection tool (e)（1 项，如 Marquee Selection Tool (E)） |
| `foxos audio-studio edit update` | `audio-studio_edit_update` | modify | Edit |
| `foxos audio-studio multitrack activate` | `audio-studio_multitrack_activate` | modify | Multitrack |
| `foxos audio-studio clip activate` | `audio-studio_clip_activate` | modify | Clip |
| `foxos audio-studio effects activate` | `audio-studio_effects_activate` | modify | Effects |
| `foxos audio-studio favorites activate` | `audio-studio_favorites_activate` | modify | Favorites |
| `foxos audio-studio view show` | `audio-studio_view_show` | read | View |
| `foxos audio-studio window activate` | `audio-studio_window_activate` | modify | Window |
| `foxos audio-studio help show` | `audio-studio_help_show` | read | Help |
| `foxos audio-studio spectral-frequency-display-shiftd show` | `audio-studio_spectral-frequency-display-shiftd_show` | read | Show Spectral Frequency Display (Shift+D) |
| `foxos audio-studio spectral-pitch-display show` | `audio-studio_spectral-pitch-display_show` | read | Show Spectral Pitch Display |
| `foxos audio-studio tool-v move` | `audio-studio_tool-v_move` | modify | Move Tool (V) |
| `foxos audio-studio razor-tool-r activate` | `audio-studio_razor-tool-r_activate` | modify | Razor Tool (R) |
| `foxos audio-studio slip-tool-y activate` | `audio-studio_slip-tool-y_activate` | modify | Slip Tool (Y) |
| `foxos audio-studio time-selection-tool-t activate` | `audio-studio_time-selection-tool-t_activate` | modify | Time Selection Tool (T) |
| `foxos audio-studio lasso-selection-tool-d activate` | `audio-studio_lasso-selection-tool-d_activate` | modify | Lasso Selection Tool (D) |
| `foxos audio-studio paintbrush-selection-tool-p activate` | `audio-studio_paintbrush-selection-tool-p_activate` | modify | Paintbrush Selection Tool (P) |
| `foxos audio-studio spot-healing-brush-tool-b activate` | `audio-studio_spot-healing-brush-tool-b_activate` | modify | Spot Healing Brush Tool (B) |
| `foxos audio-studio workspaces activate` | `audio-studio_workspaces_activate` | modify | All workspaces |
| `foxos audio-studio search-commands set VALUE [--submit]` | `audio-studio_search-commands_set` | modify | Search commands |
| `foxos audio-studio files show` | `audio-studio_files_show` | read | Files |
| `foxos audio-studio files-panel-menu activate` | `audio-studio_files-panel-menu_activate` | modify | Files panel menu |
| `foxos audio-studio favorites show` | `audio-studio_favorites_show` | read | Favorites |
| `foxos audio-studio open open` | `audio-studio_open_open` | read | Open |
| `foxos audio-studio import import` | `audio-studio_import_import` | modify | Import |
| `foxos audio-studio audio-file create` | `audio-studio_audio-file_create` | modify | New Audio File |
| `foxos audio-studio into-multitrack create` | `audio-studio_into-multitrack_create` | modify | Insert into Multitrack |
| `foxos audio-studio close close` | `audio-studio_close_close` | read | Close |
| `foxos audio-studio search-files set VALUE [--submit]` | `audio-studio_search-files_set` | modify | Search files |
| `foxos audio-studio name activate` | `audio-studio_name_activate` | modify | Name |
| `foxos audio-studio status activate` | `audio-studio_status_activate` | modify | Status |
| `foxos audio-studio duration activate` | `audio-studio_duration_activate` | modify | Duration |
| `foxos audio-studio sample-rate activate` | `audio-studio_sample-rate_activate` | modify | Sample Rate |
| `foxos audio-studio channels activate` | `audio-studio_channels_activate` | modify | Channels |
| `foxos audio-studio bit-depth activate` | `audio-studio_bit-depth_activate` | modify | Bit Depth |
| `foxos audio-studio format activate` | `audio-studio_format_activate` | modify | Format |
| `foxos audio-studio from-start play` | `audio-studio_from-start_play` | modify | Play from Start |
| `foxos audio-studio loop-playback activate` | `audio-studio_loop-playback_activate` | modify | Loop Playback |
| `foxos audio-studio auto-play toggle` | `audio-studio_auto-play_toggle` | modify | Auto-play |
| `foxos audio-studio panels resize` | `audio-studio_panels_resize` | modify | Resize panels |
| `foxos audio-studio media-browser show` | `audio-studio_media-browser_show` | read | Media Browser |
| `foxos audio-studio media-browser-panel-menu activate` | `audio-studio_media-browser-panel-menu_activate` | modify | Media Browser panel menu |
| `foxos audio-studio effects-rack show` | `audio-studio_effects-rack_show` | read | Effects Rack |
| `foxos audio-studio markers show` | `audio-studio_markers_show` | read | Markers |
| `foxos audio-studio properties show` | `audio-studio_properties_show` | read | Properties |
| `foxos audio-studio panels-group activate` | `audio-studio_panels-group_activate` | modify | All panels in this group |
| `foxos audio-studio up-one-level activate` | `audio-studio_up-one-level_activate` | modify | Up One Level |
| `foxos audio-studio refresh activate` | `audio-studio_refresh_activate` | modify | Refresh |
| `foxos audio-studio folder-from-device create` | `audio-studio_folder-from-device_create` | modify | Add a Folder from This Device |
| `foxos audio-studio home activate` | `audio-studio_home_activate` | modify | Home |
| `foxos audio-studio search-folder set VALUE [--submit]` | `audio-studio_search-folder_set` | modify | Search this folder |
| `foxos audio-studio only-audio-files show` | `audio-studio_only-audio-files_show` | read | Show only audio files |
| `foxos audio-studio homeappdata activate` | `audio-studio_homeappdata_activate` | modify | HomeAppData |
| `foxos audio-studio appdata activate` | `audio-studio_appdata_activate` | modify | AppData |
| `foxos audio-studio folder create` | `audio-studio_folder_create` | modify | Add Folder... |
| `foxos audio-studio appdatafolder activate` | `audio-studio_appdatafolder_activate` | modify | AppDataFolder |
| `foxos audio-studio preview play` | `audio-studio_preview_play` | modify | Play Preview |
| `foxos audio-studio preview stop` | `audio-studio_preview_stop` | modify | Stop Preview |
| `foxos audio-studio loop-preview activate` | `audio-studio_loop-preview_activate` | modify | Loop Preview |
| `foxos audio-studio preview-position set VALUE [--submit]` | `audio-studio_preview-position_set` | modify | Preview position |
| `foxos audio-studio auto-play-2 toggle` | `audio-studio_auto-play-2_toggle` | modify | Auto-play |
| `foxos audio-studio open-2 open` | `audio-studio_open-2_open` | read | Open |
| `foxos audio-studio into-multitrack-2 create` | `audio-studio_into-multitrack-2_create` | modify | Insert into Multitrack |
| `foxos audio-studio history show` | `audio-studio_history_show` | read | History |
| `foxos audio-studio history-panel-menu activate` | `audio-studio_history-panel-menu_activate` | modify | History panel menu |
| `foxos audio-studio video show` | `audio-studio_video_show` | read | Video |
| `foxos audio-studio history clear` | `audio-studio_history_clear` | modify | Clear history |
| `foxos audio-studio editor show` | `audio-studio_editor_show` | read | Editor |
| `foxos audio-studio editor-panel-menu activate` | `audio-studio_editor-panel-menu_activate` | modify | Editor panel menu |
| `foxos audio-studio mixer show` | `audio-studio_mixer_show` | read | Mixer |
| `foxos audio-studio open-3 open` | `audio-studio_open-3_open` | read | Open |
| `foxos audio-studio audio-file-2 create` | `audio-studio_audio-file-2_create` | modify | New Audio File |
| `foxos audio-studio multitrack-session create` | `audio-studio_multitrack-session_create` | modify | New Multitrack Session |
| `foxos audio-studio record record` | `audio-studio_record_record` | modify | Record |
| `foxos audio-studio playhead-time activate` | `audio-studio_playhead-time_activate` | modify | Playhead time |
| `foxos audio-studio stop stop` | `audio-studio_stop_stop` | modify | Stop |
| `foxos audio-studio space play` | `audio-studio_space_play` | modify | Play (Space) |
| `foxos audio-studio pause pause` | `audio-studio_pause_pause` | modify | Pause |
| `foxos audio-studio playhead-previous move` | `audio-studio_playhead-previous_move` | modify | Move Playhead to Previous |
| `foxos audio-studio rewind activate` | `audio-studio_rewind_activate` | modify | Rewind |
| `foxos audio-studio fast-forward activate` | `audio-studio_fast-forward_activate` | modify | Fast Forward |
| `foxos audio-studio playhead-next move` | `audio-studio_playhead-next_move` | modify | Move Playhead to Next |
| `foxos audio-studio shiftspace record` | `audio-studio_shiftspace_record` | modify | Record (Shift+Space) |
| `foxos audio-studio selection dismiss` | `audio-studio_selection_dismiss` | read | Skip Selection |
| `foxos audio-studio view zoom-` | `audio-studio_view_zoom-` | modify | Zoom In (Amplitude) |
| `foxos audio-studio view zoom-out` | `audio-studio_view_zoom-out` | modify | Zoom Out (Amplitude) |
| `foxos audio-studio view-2 zoom-` | `audio-studio_view-2_zoom-` | modify | Zoom In (Time) |
| `foxos audio-studio view-2 zoom-out` | `audio-studio_view-2_zoom-out` | modify | Zoom Out (Time) |
| `foxos audio-studio view-3 zoom-out` | `audio-studio_view-3_zoom-out` | modify | Zoom Out Full (All Axes) |
| `foxos audio-studio view-3 zoom-` | `audio-studio_view-3_zoom-` | modify | Zoom In at In Point |
| `foxos audio-studio view-4 zoom-` | `audio-studio_view-4_zoom-` | modify | Zoom In at Out Point |
| `foxos audio-studio view-5 zoom-` | `audio-studio_view-5_zoom-` | modify | Zoom to Selection |
| `foxos audio-studio view zoom-reset` | `audio-studio_view_zoom-reset` | modify | Zoom Reset (Time) |
| `foxos audio-studio view-6 zoom-` | `audio-studio_view-6_zoom-` | modify | Zoom In Full (Selected Track) |
| `foxos audio-studio sound-assistant show` | `audio-studio_sound-assistant_show` | read | Sound Assistant |
| `foxos audio-studio sound-assistant-panel-menu activate` | `audio-studio_sound-assistant-panel-menu_activate` | modify | Sound Assistant panel menu |
| `foxos audio-studio levels show` | `audio-studio_levels_show` | read | Levels |
| `foxos audio-studio levels-panel-menu activate` | `audio-studio_levels-panel-menu_activate` | modify | Levels panel menu |
| `foxos audio-studio left-channel-clip-indicator-click-reset activate` | `audio-studio_left-channel-clip-indicator-click-reset_activate` | modify | Left channel clip indicator. Click to reset. |
| `foxos audio-studio right-channel-clip-indicator-click-reset activate` | `audio-studio_right-channel-clip-indicator-click-reset_activate` | modify | Right channel clip indicator. Click to reset. |
| `foxos audio-studio selection-view show` | `audio-studio_selection-view_show` | read | Selection/View |
| `foxos audio-studio selection-view-panel-menu activate` | `audio-studio_selection-view-panel-menu_activate` | modify | Selection/View panel menu |
| `foxos audio-studio selection-start set VALUE [--submit]` | `audio-studio_selection-start_set` | modify | Selection start |
| `foxos audio-studio selection-end set VALUE [--submit]` | `audio-studio_selection-end_set` | modify | Selection end |
| `foxos audio-studio selection-duration set VALUE [--submit]` | `audio-studio_selection-duration_set` | modify | Selection duration |
| `foxos audio-studio view-start set VALUE [--submit]` | `audio-studio_view-start_set` | modify | View start |
| `foxos audio-studio view-end set VALUE [--submit]` | `audio-studio_view-end_set` | modify | View end |
| `foxos audio-studio view-duration set VALUE [--submit]` | `audio-studio_view-duration_set` | modify | View duration |
| `foxos audio-studio signed-as-local activate` | `audio-studio_signed-as-local_activate` | modify | Signed in as local |
| `foxos audio-studio saved-layout reset` | `audio-studio_saved-layout_reset` | modify | Reset to Saved Layout |
| `foxos audio-studio changes-workspace save` | `audio-studio_changes-workspace_save` | modify | Save Changes to this Workspace |
| `foxos audio-studio as-workspace save` | `audio-studio_as-workspace_save` | modify | Save as New Workspace... |
| `foxos audio-studio workspaces update` | `audio-studio_workspaces_update` | modify | Edit Workspaces... |
| `foxos audio-studio ctrlo open` | `audio-studio_ctrlo_open` | read | Open...Ctrl+O |
| `foxos audio-studio file-ctrli import` | `audio-studio_file-ctrli_import` | modify | Import File...Ctrl+I |
| `foxos audio-studio audio-file-altshiftn create` | `audio-studio_audio-file-altshiftn_create` | modify | New Audio File...Alt+Shift+N |
| `foxos audio-studio into-multitrack-session create` | `audio-studio_into-multitrack-session_create` | modify | Insert into Multitrack Session |
| `foxos audio-studio closealtw activate` | `audio-studio_closealtw_activate` | modify | CloseAlt+W |
| `foxos audio-studio allaltshiftw close` | `audio-studio_allaltshiftw_close` | read | Close AllAlt+Shift+W |
| `foxos audio-studio columns activate` | `audio-studio_columns_activate` | modify | Columns |
| `foxos audio-studio by-open-order sort` | `audio-studio_by-open-order_sort` | read | Sort by Open Order |
| `foxos audio-studio panel close` | `audio-studio_panel_close` | read | Close Panel |
| `foxos audio-studio other-panels-group close` | `audio-studio_other-panels-group_close` | read | Close Other Panels in Group |
| `foxos audio-studio panel-group close` | `audio-studio_panel-group_close` | read | Close Panel Group |
| `foxos audio-studio maximize-frame activate` | `audio-studio_maximize-frame_activate` | modify | Maximize Frame` |
| `foxos audio-studio file-name set VALUE [--submit]` | `audio-studio_file-name_set` | modify | File name |
| `foxos audio-studio sample-rate set VALUE [--submit]` | `audio-studio_sample-rate_set` | modify | Sample rate |
| `foxos audio-studio channels set VALUE [--submit]` | `audio-studio_channels_set` | modify | Channels |
| `foxos audio-studio bit-depth set VALUE [--submit]` | `audio-studio_bit-depth_set` | modify | Bit depth |
| `foxos audio-studio cancel cancel` | `audio-studio_cancel_cancel` | read | Cancel |
| `foxos audio-studio ok confirm` | `audio-studio_ok_confirm` | modify | OK |
| `foxos audio-studio media-browser-panel-menu-panel close` | `audio-studio_media-browser-panel-menu-panel_close` | read | Close Panel |
| `foxos audio-studio media-browser-panel-menu-other-panels-group close` | `audio-studio_media-browser-panel-menu-other-panels-group_close` | read | Close Other Panels in Group |
| `foxos audio-studio media-browser-panel-menu-panel-group close` | `audio-studio_media-browser-panel-menu-panel-group_close` | read | Close Panel Group |
| `foxos audio-studio media-browser-panel-menu-maximize-frame activate` | `audio-studio_media-browser-panel-menu-maximize-frame_activate` | modify | Maximize Frame` |
| `foxos audio-studio undoctrlz activate` | `audio-studio_undoctrlz_activate` | modify | UndoCtrl+Z |
| `foxos audio-studio redoctrlshiftz activate` | `audio-studio_redoctrlshiftz_activate` | modify | RedoCtrl+Shift+Z |
| `foxos audio-studio later-states delete` | `audio-studio_later-states_delete` | delete | Delete Later States |
| `foxos audio-studio history-panel-menu-history clear` | `audio-studio_history-panel-menu-history_clear` | modify | Clear History... |
| `foxos audio-studio history-panel-menu-panel close` | `audio-studio_history-panel-menu-panel_close` | read | Close Panel |
| `foxos audio-studio history-panel-menu-other-panels-group close` | `audio-studio_history-panel-menu-other-panels-group_close` | read | Close Other Panels in Group |
| `foxos audio-studio history-panel-menu-panel-group close` | `audio-studio_history-panel-menu-panel-group_close` | read | Close Panel Group |
| `foxos audio-studio history-panel-menu-maximize-frame activate` | `audio-studio_history-panel-menu-maximize-frame_activate` | modify | Maximize Frame` |
| `foxos audio-studio selection select-all` | `audio-studio_selection_select-all` | modify | 快捷键 mod+a |

### music-studio（`music-studio`，265 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos music-studio pattern-mode select TARGET` | `music-studio_pattern-mode_select` | read | pattern mode: *（1 项，如 Pattern mode: play the selected pattern (L toggles)） |
| `foxos music-studio song-mode select TARGET` | `music-studio_song-mode_select` | read | song mode: *（1 项，如 Song mode: play the playlist arrangement (L toggles)） |
| `foxos music-studio pattern select TARGET` | `music-studio_pattern_select` | read | pattern: *（1 项，如 Pattern: Beat. Select pattern） |
| `foxos music-studio project select TARGET` | `music-studio_project_select` | read | project: *（1 项，如 Project: Demo Song. . Open project settings） |
| `foxos music-studio account select TARGET` | `music-studio_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos music-studio one-synthesized-drum-voice select TARGET` | `music-studio_one-synthesized-drum-voice_select` | read | one synthesized drum voice: *（1 项，如 One synthesized drum voice: kick, snare, clap, hats, toms and more, shaped from oscillators and noise.） |
| `foxos music-studio browser select TARGET` | `music-studio_browser_select` | read | #（4 项，如 Patterns4） |
| `foxos music-studio beat-clips select TARGET` | `music-studio_beat-clips_select` | read | beat, # clips（1 项，如 Beat, 8 clips） |
| `foxos music-studio bassline-clips select TARGET` | `music-studio_bassline-clips_select` | read | bassline, # clips（1 项，如 Bassline, 2 clips） |
| `foxos music-studio chords-clips select TARGET` | `music-studio_chords-clips_select` | read | chords, # clips（1 项，如 Chords, 2 clips） |
| `foxos music-studio lead-clip select TARGET` | `music-studio_lead-clip_select` | read | lead, # clip（1 项，如 Lead, 1 clip） |
| `foxos music-studio track-1 select TARGET` | `music-studio_track-1_select` | read | track 1: *（1 项，如 Track 1: Drums） |
| `foxos music-studio track-2 select TARGET` | `music-studio_track-2_select` | read | track 2: *（1 项，如 Track 2: Bass） |
| `foxos music-studio track-3 select TARGET` | `music-studio_track-3_select` | read | track 3: *（1 项，如 Track 3: Chords） |
| `foxos music-studio track-4 select TARGET` | `music-studio_track-4_select` | read | track 4: *（1 项，如 Track 4: Lead） |
| `foxos music-studio track-5 select TARGET` | `music-studio_track-5_select` | read | track 5: *（1 项，如 Track 5: Track 5） |
| `foxos music-studio mute-track select TARGET` | `music-studio_mute-track_select` | read | mute track #（12 项，如 Mute Track 5） |
| `foxos music-studio solo-track select TARGET` | `music-studio_solo-track_select` | read | solo track #（12 项，如 Solo Track 5） |
| `foxos music-studio track-6 select TARGET` | `music-studio_track-6_select` | read | track 6: *（1 项，如 Track 6: Track 6） |
| `foxos music-studio track-7 select TARGET` | `music-studio_track-7_select` | read | track 7: *（1 项，如 Track 7: Track 7） |
| `foxos music-studio track-8 select TARGET` | `music-studio_track-8_select` | read | track 8: *（1 项，如 Track 8: Track 8） |
| `foxos music-studio track-9 select TARGET` | `music-studio_track-9_select` | read | track 9: *（1 项，如 Track 9: Track 9） |
| `foxos music-studio track-10 select TARGET` | `music-studio_track-10_select` | read | track 10: *（1 项，如 Track 10: Track 10） |
| `foxos music-studio track-11 select TARGET` | `music-studio_track-11_select` | read | track 11: *（1 项，如 Track 11: Track 11） |
| `foxos music-studio track-12 select TARGET` | `music-studio_track-12_select` | read | track 12: *（1 项，如 Track 12: Track 12） |
| `foxos music-studio track-13 select TARGET` | `music-studio_track-13_select` | read | track 13: *（1 项，如 Track 13: Track 13） |
| `foxos music-studio track-14 select TARGET` | `music-studio_track-14_select` | read | track 14: *（1 项，如 Track 14: Track 14） |
| `foxos music-studio track-15 select TARGET` | `music-studio_track-15_select` | read | track 15: *（1 项，如 Track 15: Track 15） |
| `foxos music-studio track-16 select TARGET` | `music-studio_track-16_select` | read | track 16: *（1 项，如 Track 16: Track 16） |
| `foxos music-studio kick select TARGET` | `music-studio_kick_select` | read | kick: *（1 项，如 Kick: on） |
| `foxos music-studio channel-rack-beat select TARGET` | `music-studio_channel-rack-beat_select` | read | #（6 项，如 1） |
| `foxos music-studio kick-2 select TARGET` | `music-studio_kick-2_select` | read | kick: *（1 项，如 Kick: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio step-velocity select TARGET` | `music-studio_step-velocity_select` | read | step #, on, velocity #%（17 项，如 Step 1, on, velocity 80%） |
| `foxos music-studio step-off select TARGET` | `music-studio_step-off_select` | read | step #, off（16 项，如 Step 2, off） |
| `foxos music-studio clap select TARGET` | `music-studio_clap_select` | read | clap: *（1 项，如 Clap: on） |
| `foxos music-studio clap-2 select TARGET` | `music-studio_clap-2_select` | read | clap: *（1 项，如 Clap: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio closed-hat select TARGET` | `music-studio_closed-hat_select` | read | closed hat: *（1 项，如 Closed Hat: on） |
| `foxos music-studio closed-hat-2 select TARGET` | `music-studio_closed-hat-2_select` | read | closed hat: *（1 项，如 Closed Hat: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio hat open TARGET` | `music-studio_hat_open` | read | open hat: *（1 项，如 Open Hat: on） |
| `foxos music-studio hat-2 open TARGET` | `music-studio_hat-2_open` | read | open hat: *（1 项，如 Open Hat: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio bass select TARGET` | `music-studio_bass_select` | read | bass: *（1 项，如 Bass: on） |
| `foxos music-studio bass-2 select TARGET` | `music-studio_bass-2_select` | read | bass: *（1 项，如 Bass: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio chords select TARGET` | `music-studio_chords_select` | read | chords: *（1 项，如 Chords: on） |
| `foxos music-studio chords-2 select TARGET` | `music-studio_chords-2_select` | read | chords: *（1 项，如 Chords: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio lead select TARGET` | `music-studio_lead_select` | read | lead: *（1 项，如 Lead: on） |
| `foxos music-studio lead-2 select TARGET` | `music-studio_lead-2_select` | read | lead: *（1 项，如 Lead: click to select, double-click or Enter for the editor, right-click for options） |
| `foxos music-studio master-double-click-or-rename select TARGET` | `music-studio_master-double-click-or-rename_select` | read | master. double-click or # to rename.（1 项，如 Master. Double-click or F2 to rename.） |
| `foxos music-studio kick-master send TARGET` | `music-studio_kick-master_send` | modify | send # kick to master（1 项，如 Send 1 Kick to Master） |
| `foxos music-studio inputs select TARGET` | `music-studio_inputs_select` | read | inputs: *（6 项，如 Inputs: Kick） |
| `foxos music-studio kick-double-click-or-rename select TARGET` | `music-studio_kick-double-click-or-rename_select` | read | kick. double-click or # to rename.（1 项，如 Kick. Double-click or F2 to rename.） |
| `foxos music-studio clap-double-click-or-rename select TARGET` | `music-studio_clap-double-click-or-rename_select` | read | clap. double-click or # to rename.（1 项，如 Clap. Double-click or F2 to rename.） |
| `foxos music-studio kick-clap send TARGET` | `music-studio_kick-clap_send` | modify | send # kick to # clap（1 项，如 Send 1 Kick to 2 Clap） |
| `foxos music-studio hats-double-click-or-rename select TARGET` | `music-studio_hats-double-click-or-rename_select` | read | hats. double-click or # to rename.（1 项，如 Hats. Double-click or F2 to rename.） |
| `foxos music-studio kick-hats send TARGET` | `music-studio_kick-hats_send` | modify | send # kick to # hats（1 项，如 Send 1 Kick to 3 Hats） |
| `foxos music-studio bass-double-click-or-rename select TARGET` | `music-studio_bass-double-click-or-rename_select` | read | bass. double-click or # to rename.（1 项，如 Bass. Double-click or F2 to rename.） |
| `foxos music-studio kick-bass send TARGET` | `music-studio_kick-bass_send` | modify | send # kick to # bass（1 项，如 Send 1 Kick to 4 Bass） |
| `foxos music-studio chords-double-click-or-rename select TARGET` | `music-studio_chords-double-click-or-rename_select` | read | chords. double-click or # to rename.（1 项，如 Chords. Double-click or F2 to rename.） |
| `foxos music-studio kick-chords send TARGET` | `music-studio_kick-chords_send` | modify | send # kick to # chords（1 项，如 Send 1 Kick to 5 Chords） |
| `foxos music-studio lead-double-click-or-rename select TARGET` | `music-studio_lead-double-click-or-rename_select` | read | lead. double-click or # to rename.（1 项，如 Lead. Double-click or F2 to rename.） |
| `foxos music-studio kick-lead send TARGET` | `music-studio_kick-lead_send` | modify | send # kick to # lead（1 项，如 Send 1 Kick to 6 Lead） |
| `foxos music-studio double-click-or-rename create TARGET` | `music-studio_double-click-or-rename_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 7. Double-click or F2 to rename.） |
| `foxos music-studio mute-insert select TARGET` | `music-studio_mute-insert_select` | read | mute insert #（10 项，如 Mute Insert 7） |
| `foxos music-studio solo-insert select TARGET` | `music-studio_solo-insert_select` | read | solo insert #（10 项，如 Solo Insert 7） |
| `foxos music-studio kick-insert send TARGET` | `music-studio_kick-insert_send` | modify | send # kick to insert #（10 项，如 Send 1 Kick to Insert 7） |
| `foxos music-studio double-click-or-rename-2 create TARGET` | `music-studio_double-click-or-rename-2_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 8. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-3 create TARGET` | `music-studio_double-click-or-rename-3_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 9. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-4 create TARGET` | `music-studio_double-click-or-rename-4_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 10. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-5 create TARGET` | `music-studio_double-click-or-rename-5_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 11. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-6 create TARGET` | `music-studio_double-click-or-rename-6_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 12. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-7 create TARGET` | `music-studio_double-click-or-rename-7_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 13. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-8 create TARGET` | `music-studio_double-click-or-rename-8_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 14. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-9 create TARGET` | `music-studio_double-click-or-rename-9_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 15. Double-click or F2 to rename.） |
| `foxos music-studio double-click-or-rename-10 create TARGET` | `music-studio_double-click-or-rename-10_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 16. Double-click or F2 to rename.） |
| `foxos music-studio effect select TARGET` | `music-studio_effect_select` | read | # effect（10 项，如 1Add effect） |
| `foxos music-studio beat select TARGET` | `music-studio_beat_select` | read | # beat（1 项，如 1. Beat） |
| `foxos music-studio bassline select TARGET` | `music-studio_bassline_select` | read | # bassline（1 项，如 2. Bassline） |
| `foxos music-studio pattern-beat-select-pattern-chords select TARGET` | `music-studio_pattern-beat-select-pattern-chords_select` | read | # chords（1 项，如 3. Chords） |
| `foxos music-studio pattern-beat-select-pattern-lead select TARGET` | `music-studio_pattern-beat-select-pattern-lead_select` | read | # lead（1 项，如 4. Lead） |
| `foxos music-studio pattern rename TARGET` | `music-studio_pattern_rename` | modify | rename pattern...#（1 项，如 Rename pattern...F2） |
| `foxos music-studio clap-master send TARGET` | `music-studio_clap-master_send` | modify | send # clap to master（1 项，如 Send 2 Clap to Master） |
| `foxos music-studio clap-kick send TARGET` | `music-studio_clap-kick_send` | modify | send # clap to # kick（1 项，如 Send 2 Clap to 1 Kick） |
| `foxos music-studio clap-hats send TARGET` | `music-studio_clap-hats_send` | modify | send # clap to # hats（1 项，如 Send 2 Clap to 3 Hats） |
| `foxos music-studio clap-bass send TARGET` | `music-studio_clap-bass_send` | modify | send # clap to # bass（1 项，如 Send 2 Clap to 4 Bass） |
| `foxos music-studio clap-chords send TARGET` | `music-studio_clap-chords_send` | modify | send # clap to # chords（1 项，如 Send 2 Clap to 5 Chords） |
| `foxos music-studio clap-lead send TARGET` | `music-studio_clap-lead_send` | modify | send # clap to # lead（1 项，如 Send 2 Clap to 6 Lead） |
| `foxos music-studio clap-insert send TARGET` | `music-studio_clap-insert_send` | modify | send # clap to insert #（10 项，如 Send 2 Clap to Insert 7） |
| `foxos music-studio hats-master send TARGET` | `music-studio_hats-master_send` | modify | send # hats to master（1 项，如 Send 3 Hats to Master） |
| `foxos music-studio hats-kick send TARGET` | `music-studio_hats-kick_send` | modify | send # hats to # kick（1 项，如 Send 3 Hats to 1 Kick） |
| `foxos music-studio hats-clap send TARGET` | `music-studio_hats-clap_send` | modify | send # hats to # clap（1 项，如 Send 3 Hats to 2 Clap） |
| `foxos music-studio hats-bass send TARGET` | `music-studio_hats-bass_send` | modify | send # hats to # bass（1 项，如 Send 3 Hats to 4 Bass） |
| `foxos music-studio hats-chords send TARGET` | `music-studio_hats-chords_send` | modify | send # hats to # chords（1 项，如 Send 3 Hats to 5 Chords） |
| `foxos music-studio hats-lead send TARGET` | `music-studio_hats-lead_send` | modify | send # hats to # lead（1 项，如 Send 3 Hats to 6 Lead） |
| `foxos music-studio hats-insert send TARGET` | `music-studio_hats-insert_send` | modify | send # hats to insert #（10 项，如 Send 3 Hats to Insert 7） |
| `foxos music-studio bass-master send TARGET` | `music-studio_bass-master_send` | modify | send # bass to master（1 项，如 Send 4 Bass to Master） |
| `foxos music-studio bass-kick send TARGET` | `music-studio_bass-kick_send` | modify | send # bass to # kick（1 项，如 Send 4 Bass to 1 Kick） |
| `foxos music-studio bass-clap send TARGET` | `music-studio_bass-clap_send` | modify | send # bass to # clap（1 项，如 Send 4 Bass to 2 Clap） |
| `foxos music-studio bass-hats send TARGET` | `music-studio_bass-hats_send` | modify | send # bass to # hats（1 项，如 Send 4 Bass to 3 Hats） |
| `foxos music-studio bass-chords send TARGET` | `music-studio_bass-chords_send` | modify | send # bass to # chords（1 项，如 Send 4 Bass to 5 Chords） |
| `foxos music-studio bass-lead send TARGET` | `music-studio_bass-lead_send` | modify | send # bass to # lead（1 项，如 Send 4 Bass to 6 Lead） |
| `foxos music-studio bass-insert send TARGET` | `music-studio_bass-insert_send` | modify | send # bass to insert #（10 项，如 Send 4 Bass to Insert 7） |
| `foxos music-studio chords-master send TARGET` | `music-studio_chords-master_send` | modify | send # chords to master（1 项，如 Send 5 Chords to Master） |
| `foxos music-studio chords-kick send TARGET` | `music-studio_chords-kick_send` | modify | send # chords to # kick（1 项，如 Send 5 Chords to 1 Kick） |
| `foxos music-studio chords-clap send TARGET` | `music-studio_chords-clap_send` | modify | send # chords to # clap（1 项，如 Send 5 Chords to 2 Clap） |
| `foxos music-studio chords-hats send TARGET` | `music-studio_chords-hats_send` | modify | send # chords to # hats（1 项，如 Send 5 Chords to 3 Hats） |
| `foxos music-studio chords-bass send TARGET` | `music-studio_chords-bass_send` | modify | send # chords to # bass（1 项，如 Send 5 Chords to 4 Bass） |
| `foxos music-studio chords-lead send TARGET` | `music-studio_chords-lead_send` | modify | send # chords to # lead（1 项，如 Send 5 Chords to 6 Lead） |
| `foxos music-studio chords-insert send TARGET` | `music-studio_chords-insert_send` | modify | send # chords to insert #（10 项，如 Send 5 Chords to Insert 7） |
| `foxos music-studio reverb-slot-open-editor select TARGET` | `music-studio_reverb-slot-open-editor_select` | read | reverb, slot # open editor（1 项，如 Reverb, slot 1. Open editor） |
| `foxos music-studio lead-master send TARGET` | `music-studio_lead-master_send` | modify | send # lead to master（1 项，如 Send 6 Lead to Master） |
| `foxos music-studio lead-kick send TARGET` | `music-studio_lead-kick_send` | modify | send # lead to # kick（1 项，如 Send 6 Lead to 1 Kick） |
| `foxos music-studio lead-clap send TARGET` | `music-studio_lead-clap_send` | modify | send # lead to # clap（1 项，如 Send 6 Lead to 2 Clap） |
| `foxos music-studio lead-hats send TARGET` | `music-studio_lead-hats_send` | modify | send # lead to # hats（1 项，如 Send 6 Lead to 3 Hats） |
| `foxos music-studio lead-bass send TARGET` | `music-studio_lead-bass_send` | modify | send # lead to # bass（1 项，如 Send 6 Lead to 4 Bass） |
| `foxos music-studio lead-chords send TARGET` | `music-studio_lead-chords_send` | modify | send # lead to # chords（1 项，如 Send 6 Lead to 5 Chords） |
| `foxos music-studio lead-insert send TARGET` | `music-studio_lead-insert_send` | modify | send # lead to insert #（10 项，如 Send 6 Lead to Insert 7） |
| `foxos music-studio delay-slot-open-editor select TARGET` | `music-studio_delay-slot-open-editor_select` | read | delay, slot # open editor（1 项，如 Delay, slot 1. Open editor） |
| `foxos music-studio lead-click-select-double-click-or-enter-reverb-s select TARGET` | `music-studio_lead-click-select-double-click-or-enter-reverb-s_select` | read | reverb, slot # open editor（1 项，如 Reverb, slot 2. Open editor） |
| `foxos music-studio add-mixer-insert-project select TARGET` | `music-studio_add-mixer-insert-project_select` | read | project: *（1 项，如 Project: Demo Song. Edited. Open project settings） |
| `foxos music-studio insert-master send TARGET` | `music-studio_insert-master_send` | modify | send insert # to master（1 项，如 Send Insert 17 to Master） |
| `foxos music-studio insert-kick send TARGET` | `music-studio_insert-kick_send` | modify | send insert # to # kick（1 项，如 Send Insert 17 to 1 Kick） |
| `foxos music-studio insert-clap send TARGET` | `music-studio_insert-clap_send` | modify | send insert # to # clap（1 项，如 Send Insert 17 to 2 Clap） |
| `foxos music-studio insert-hats send TARGET` | `music-studio_insert-hats_send` | modify | send insert # to # hats（1 项，如 Send Insert 17 to 3 Hats） |
| `foxos music-studio insert-bass send TARGET` | `music-studio_insert-bass_send` | modify | send insert # to # bass（1 项，如 Send Insert 17 to 4 Bass） |
| `foxos music-studio insert-chords send TARGET` | `music-studio_insert-chords_send` | modify | send insert # to # chords（1 项，如 Send Insert 17 to 5 Chords） |
| `foxos music-studio insert-lead send TARGET` | `music-studio_insert-lead_send` | modify | send insert # to # lead（1 项，如 Send Insert 17 to 6 Lead） |
| `foxos music-studio insert-insert send TARGET` | `music-studio_insert-insert_send` | modify | send insert # to insert #（10 项，如 Send Insert 17 to Insert 7） |
| `foxos music-studio add-mixer-insert-double-click-or-rename create TARGET` | `music-studio_add-mixer-insert-double-click-or-rename_create` | modify | insert # double-click or # to rename.（1 项，如 Insert 17. Double-click or F2 to rename.） |
| `foxos music-studio volume create TARGET` | `music-studio_volume_create` | modify | insert # volume（1 项，如 Insert 17 volume） |
| `foxos music-studio add-mixer-insert-mute-insert select TARGET` | `music-studio_add-mixer-insert-mute-insert_select` | read | mute insert #（1 项，如 Mute Insert 17） |
| `foxos music-studio add-mixer-insert-solo-insert select TARGET` | `music-studio_add-mixer-insert-solo-insert_select` | read | solo insert #（1 项，如 Solo Insert 17） |
| `foxos music-studio workspace dismiss` | `music-studio_workspace_dismiss` | read | Skip to workspace |
| `foxos music-studio edit update` | `music-studio_edit_update` | modify | Edit |
| `foxos music-studio add create` | `music-studio_add_create` | modify | Add |
| `foxos music-studio patterns activate` | `music-studio_patterns_activate` | modify | Patterns |
| `foxos music-studio view show` | `music-studio_view_show` | read | View |
| `foxos music-studio options activate` | `music-studio_options_activate` | modify | Options |
| `foxos music-studio tools activate` | `music-studio_tools_activate` | modify | Tools |
| `foxos music-studio help show` | `music-studio_help_show` | read | Help |
| `foxos music-studio play play` | `music-studio_play_play` | modify | Play |
| `foxos music-studio stop stop` | `music-studio_stop_stop` | modify | Stop |
| `foxos music-studio record record` | `music-studio_record_record` | modify | Record |
| `foxos music-studio tempo-beats-per-minute set VALUE [--submit]` | `music-studio_tempo-beats-per-minute_set` | modify | Tempo in beats per minute |
| `foxos music-studio metronome activate` | `music-studio_metronome_activate` | modify | Metronome |
| `foxos music-studio count-in-before-recording activate` | `music-studio_count-in-before-recording_activate` | modify | Count-in before recording |
| `foxos music-studio typing-keyboard-piano activate` | `music-studio_typing-keyboard-piano_activate` | modify | Typing keyboard to piano |
| `foxos music-studio pattern previous` | `music-studio_pattern_previous` | read | Previous pattern |
| `foxos music-studio pattern next` | `music-studio_pattern_next` | read | Next pattern |
| `foxos music-studio pattern create` | `music-studio_pattern_create` | modify | New pattern |
| `foxos music-studio playlist activate` | `music-studio_playlist_activate` | modify | Playlist |
| `foxos music-studio channel-rack activate` | `music-studio_channel-rack_activate` | modify | Channel rack |
| `foxos music-studio piano-roll activate` | `music-studio_piano-roll_activate` | modify | Piano roll |
| `foxos music-studio mixer activate` | `music-studio_mixer_activate` | modify | Mixer |
| `foxos music-studio browser activate` | `music-studio_browser_activate` | modify | Browser |
| `foxos music-studio master-volume set VALUE [--submit]` | `music-studio_master-volume_set` | modify | Master volume |
| `foxos music-studio source-code-github-opens-tab show` | `music-studio_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos music-studio audio import` | `music-studio_audio_import` | modify | Import audio |
| `foxos music-studio collapse collapse` | `music-studio_collapse_collapse` | read | Collapse all |
| `foxos music-studio browser close` | `music-studio_browser_close` | read | Close Browser |
| `foxos music-studio search-browser set VALUE [--submit]` | `music-studio_search-browser_set` | modify | Search the browser |
| `foxos music-studio instruments activate` | `music-studio_instruments_activate` | modify | Instruments |
| `foxos music-studio synth-presets activate` | `music-studio_synth-presets_activate` | modify | Synth presets |
| `foxos music-studio drum-presets activate` | `music-studio_drum-presets_activate` | modify | Drum presets |
| `foxos music-studio effects activate` | `music-studio_effects_activate` | modify | Effects |
| `foxos music-studio project activate` | `music-studio_project_activate` | modify | Project |
| `foxos music-studio files activate` | `music-studio_files_activate` | modify | My files |
| `foxos music-studio music-studio-files activate` | `music-studio_music-studio-files_activate` | modify | Music Studio files |
| `foxos music-studio browse-another-folder activate` | `music-studio_browse-another-folder_activate` | modify | Browse another folder... |
| `foxos music-studio audio-from-device import` | `music-studio_audio-from-device_import` | modify | Import audio from this device... |
| `foxos music-studio device activate` | `music-studio_device_activate` | modify | This device |
| `foxos music-studio browser resize` | `music-studio_browser_resize` | modify | Resize browser |
| `foxos music-studio clip-sources show` | `music-studio_clip-sources_show` | read | Show clip sources |
| `foxos music-studio tool draw` | `music-studio_tool_draw` | modify | Draw tool |
| `foxos music-studio paint-tool activate` | `music-studio_paint-tool_activate` | modify | Paint tool |
| `foxos music-studio tool delete` | `music-studio_tool_delete` | delete | Delete tool |
| `foxos music-studio mute-tool activate` | `music-studio_mute-tool_activate` | modify | Mute tool |
| `foxos music-studio slice-tool activate` | `music-studio_slice-tool_activate` | modify | Slice tool |
| `foxos music-studio tool select` | `music-studio_tool_select` | read | Select tool |
| `foxos music-studio view zoom-tool` | `music-studio_view_zoom-tool` | modify | Zoom tool |
| `foxos music-studio playback-tool activate` | `music-studio_playback-tool_activate` | modify | Playback tool |
| `foxos music-studio snap set VALUE [--submit]` | `music-studio_snap_set` | modify | Snap |
| `foxos music-studio follow-playhead activate` | `music-studio_follow-playhead_activate` | modify | Follow playhead |
| `foxos music-studio follow-options activate` | `music-studio_follow-options_activate` | modify | Follow options |
| `foxos music-studio view zoom-out` | `music-studio_view_zoom-out` | modify | Zoom out |
| `foxos music-studio view zoom-` | `music-studio_view_zoom-` | modify | Zoom in |
| `foxos music-studio view-2 zoom-` | `music-studio_view-2_zoom-` | modify | Zoom to fit song |
| `foxos music-studio maximize-playlist activate` | `music-studio_maximize-playlist_activate` | modify | Maximize Playlist |
| `foxos music-studio playlist close` | `music-studio_playlist_close` | read | Close Playlist |
| `foxos music-studio automation-clip create` | `music-studio_automation-clip_create` | modify | Add automation clip |
| `foxos music-studio clip-source-list resize` | `music-studio_clip-source-list_resize` | modify | Resize clip source list |
| `foxos music-studio track create` | `music-studio_track_create` | modify | Add track |
| `foxos music-studio song-position set VALUE [--submit]` | `music-studio_song-position_set` | modify | Song position |
| `foxos music-studio mute-drums activate` | `music-studio_mute-drums_activate` | modify | Mute Drums |
| `foxos music-studio solo-drums activate` | `music-studio_solo-drums_activate` | modify | Solo Drums |
| `foxos music-studio mute-bass activate` | `music-studio_mute-bass_activate` | modify | Mute Bass |
| `foxos music-studio solo-bass activate` | `music-studio_solo-bass_activate` | modify | Solo Bass |
| `foxos music-studio mute-chords activate` | `music-studio_mute-chords_activate` | modify | Mute Chords |
| `foxos music-studio solo-chords activate` | `music-studio_solo-chords_activate` | modify | Solo Chords |
| `foxos music-studio mute-lead activate` | `music-studio_mute-lead_activate` | modify | Mute Lead |
| `foxos music-studio solo-lead activate` | `music-studio_solo-lead_activate` | modify | Solo Lead |
| `foxos music-studio playlist-arrangement activate` | `music-studio_playlist-arrangement_activate` | modify | Playlist arrangement |
| `foxos music-studio editors resize` | `music-studio_editors_resize` | modify | Resize editors |
| `foxos music-studio bar delete` | `music-studio_bar_delete` | delete | Remove a bar |
| `foxos music-studio bar create` | `music-studio_bar_create` | modify | Add a bar |
| `foxos music-studio swing set VALUE [--submit]` | `music-studio_swing_set` | modify | Swing |
| `foxos music-studio velocity-lane activate` | `music-studio_velocity-lane_activate` | modify | Velocity lane |
| `foxos music-studio channel create` | `music-studio_channel_create` | modify | Add a channel |
| `foxos music-studio maximize-channel-rack activate` | `music-studio_maximize-channel-rack_activate` | modify | Maximize Channel rack |
| `foxos music-studio channel-rack close` | `music-studio_channel-rack_close` | read | Close Channel rack |
| `foxos music-studio kick-3 select` | `music-studio_kick-3_select` | read | Select Kick |
| `foxos music-studio clap-3 select` | `music-studio_clap-3_select` | read | Select Clap |
| `foxos music-studio closed-hat-3 select` | `music-studio_closed-hat-3_select` | read | Select Closed Hat |
| `foxos music-studio open-hat select` | `music-studio_open-hat_select` | read | Select Open Hat |
| `foxos music-studio bass-3 select` | `music-studio_bass-3_select` | read | Select Bass |
| `foxos music-studio chords-3 select` | `music-studio_chords-3_select` | read | Select Chords |
| `foxos music-studio lead-3 select` | `music-studio_lead-3_select` | read | Select Lead |
| `foxos music-studio channel-2 create` | `music-studio_channel-2_create` | modify | Add a channel |
| `foxos music-studio panels resize` | `music-studio_panels_resize` | modify | Resize panels |
| `foxos music-studio mixer-insert create` | `music-studio_mixer-insert_create` | modify | Add mixer insert |
| `foxos music-studio effects-routing-panel activate` | `music-studio_effects-routing-panel_activate` | modify | Effects and routing panel |
| `foxos music-studio maximize-mixer activate` | `music-studio_maximize-mixer_activate` | modify | Maximize Mixer |
| `foxos music-studio mixer close` | `music-studio_mixer_close` | read | Close Mixer |
| `foxos music-studio mute-master activate` | `music-studio_mute-master_activate` | modify | Mute Master |
| `foxos music-studio pan set VALUE [--submit]` | `music-studio_pan_set` | modify | Pan |
| `foxos music-studio width set VALUE [--submit]` | `music-studio_width_set` | modify | Width |
| `foxos music-studio kick-volume set VALUE [--submit]` | `music-studio_kick-volume_set` | modify | Kick volume |
| `foxos music-studio mute-kick activate` | `music-studio_mute-kick_activate` | modify | Mute Kick |
| `foxos music-studio solo-kick activate` | `music-studio_solo-kick_activate` | modify | Solo Kick |
| `foxos music-studio mute-clap activate` | `music-studio_mute-clap_activate` | modify | Mute Clap |
| `foxos music-studio solo-clap activate` | `music-studio_solo-clap_activate` | modify | Solo Clap |
| `foxos music-studio mute-hats activate` | `music-studio_mute-hats_activate` | modify | Mute Hats |
| `foxos music-studio solo-hats activate` | `music-studio_solo-hats_activate` | modify | Solo Hats |
| `foxos music-studio options create` | `music-studio_options_create` | modify | Insert options |
| `foxos music-studio insert select` | `music-studio_insert_select` | read | Select this insert |
| `foxos music-studio send-level-master set VALUE [--submit]` | `music-studio_send-level-master_set` | modify | Send level to Master |
| `foxos music-studio send-master delete` | `music-studio_send-master_delete` | delete | Remove send to Master |
| `foxos music-studio send create` | `music-studio_send_create` | modify | Add send |
| `foxos music-studio channel-rack select` | `music-studio_channel-rack_select` | read | Select in the channel rack |
| `foxos music-studio music-studio-is-open-source show` | `music-studio_music-studio-is-open-source_show` | read | Music Studio is open source |
| `foxos music-studio take-tour activate` | `music-studio_take-tour_activate` | modify | Take the tour |
| `foxos music-studio it dismiss` | `music-studio_it_dismiss` | read | Got it |
| `foxos music-studio pattern-beat-select-pattern-pattern create` | `music-studio_pattern-beat-select-pattern-pattern_create` | modify | New pattern |
| `foxos music-studio clone-pattern activate` | `music-studio_clone-pattern_activate` | modify | Clone pattern |
| `foxos music-studio signed-as-local activate` | `music-studio_signed-as-local_activate` | modify | Signed in as local |
| `foxos music-studio follow-options-follow-playhead activate` | `music-studio_follow-options-follow-playhead_activate` | modify | Follow playhead |
| `foxos music-studio page-by-page activate` | `music-studio_page-by-page_activate` | modify | Page by page |
| `foxos music-studio continuous activate` | `music-studio_continuous_activate` | modify | Continuous |
| `foxos music-studio poly-synth activate` | `music-studio_poly-synth_activate` | modify | Poly Synth |
| `foxos music-studio drum-synth activate` | `music-studio_drum-synth_activate` | modify | Drum Synth |
| `foxos music-studio sampler activate` | `music-studio_sampler_activate` | modify | Sampler |
| `foxos music-studio add-channel-synth-presets activate` | `music-studio_add-channel-synth-presets_activate` | modify | Synth presets |
| `foxos music-studio add-channel-drum-presets activate` | `music-studio_add-channel-drum-presets_activate` | modify | Drum presets |
| `foxos music-studio sampler-from-audio-file activate` | `music-studio_sampler-from-audio-file_activate` | modify | Sampler from audio file... |
| `foxos music-studio clap-volume set VALUE [--submit]` | `music-studio_clap-volume_set` | modify | Clap volume |
| `foxos music-studio hats-volume set VALUE [--submit]` | `music-studio_hats-volume_set` | modify | Hats volume |
| `foxos music-studio bass-volume set VALUE [--submit]` | `music-studio_bass-volume_set` | modify | Bass volume |
| `foxos music-studio chords-volume set VALUE [--submit]` | `music-studio_chords-volume_set` | modify | Chords volume |
| `foxos music-studio drag-reorder-ctrlup-down activate` | `music-studio_drag-reorder-ctrlup-down_activate` | modify | Drag to reorder (Ctrl+Up/Down) |
| `foxos music-studio reverb activate` | `music-studio_reverb_activate` | modify | Reverb on |
| `foxos music-studio reverb-mix set VALUE [--submit]` | `music-studio_reverb-mix_set` | modify | Reverb mix |
| `foxos music-studio reverb-options activate` | `music-studio_reverb-options_activate` | modify | Reverb options |
| `foxos music-studio lead-volume set VALUE [--submit]` | `music-studio_lead-volume_set` | modify | Lead volume |
| `foxos music-studio delay activate` | `music-studio_delay_activate` | modify | Delay on |
| `foxos music-studio delay-mix set VALUE [--submit]` | `music-studio_delay-mix_set` | modify | Delay mix |
| `foxos music-studio delay-options activate` | `music-studio_delay-options_activate` | modify | Delay options |
| `foxos music-studio shortcut key-t` | `music-studio_shortcut_key-t` | modify | 快捷键 mod+t |

### 3d（`3d`，229 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos 3d cozy-room select TARGET` | `3d_cozy-room_select` | read | a cozy room: *（1 项，如 A cozy room: floor, two walls, a sofa and a lamp） |
| `foxos 3d adjust-last-operation select TARGET` | `3d_adjust-last-operation_select` | read | adjust last operation…#（1 项，如 Adjust Last Operation…F9） |
| `foxos 3d search show TARGET` | `3d_search_show` | read | menu search…#（1 项，如 Menu Search…F3） |
| `foxos 3d active-item rename TARGET` | `3d_active-item_rename` | modify | rename active item…#（1 项，如 Rename Active Item…F2） |
| `foxos 3d batch-rename-ctrl select TARGET` | `3d_batch-rename-ctrl_select` | read | batch rename…ctrl #（1 项，如 Batch Rename…Ctrl F2） |
| `foxos 3d render select TARGET` | `3d_render_select` | read | render #（1 项，如 Render ImageF12） |
| `foxos 3d render-animationctrl select TARGET` | `3d_render-animationctrl_select` | read | render animationctrl #（1 项，如 Render AnimationCtrl F12） |
| `foxos 3d view show TARGET` | `3d_view_show` | read | view #（1 项，如 View RenderF11） |
| `foxos 3d animationctrl show TARGET` | `3d_animationctrl_show` | read | view animationctrl #（1 项，如 View AnimationCtrl F11） |
| `foxos 3d e-g-png filter TARGET` | `3d_e-g-png_filter` | read | filter (e.g. *.png)（1 项，如 Filter (e.g. *.png)） |
| `foxos 3d slot-empty select TARGET` | `3d_slot-empty_select` | read | slot # (empty)（1 项，如 Slot 1 (empty)） |
| `foxos 3d fps select TARGET` | `3d_fps_select` | read | # fps（1 项，如 24 fps） |
| `foxos 3d edit update` | `3d_edit_update` | modify | Edit |
| `foxos 3d render activate` | `3d_render_activate` | modify | Render |
| `foxos 3d window activate` | `3d_window_activate` | modify | Window |
| `foxos 3d help show` | `3d_help_show` | read | Help |
| `foxos 3d layout show` | `3d_layout_show` | read | Layout |
| `foxos 3d modeling show` | `3d_modeling_show` | read | Modeling |
| `foxos 3d sculpting show` | `3d_sculpting_show` | read | Sculpting |
| `foxos 3d uv-editing show` | `3d_uv-editing_show` | read | UV Editing |
| `foxos 3d texture-paint show` | `3d_texture-paint_show` | read | Texture Paint |
| `foxos 3d shading show` | `3d_shading_show` | read | Shading |
| `foxos 3d animation show` | `3d_animation_show` | read | Animation |
| `foxos 3d rendering show` | `3d_rendering_show` | read | Rendering |
| `foxos 3d compositing show` | `3d_compositing_show` | read | Compositing |
| `foxos 3d geometry-nodes show` | `3d_geometry-nodes_show` | read | Geometry Nodes |
| `foxos 3d scripting show` | `3d_scripting_show` | read | Scripting |
| `foxos 3d workspace create` | `3d_workspace_create` | modify | Add Workspace |
| `foxos 3d assistant activate` | `3d_assistant_activate` | modify | Assistant |
| `foxos 3d pin-scene-workspace activate` | `3d_pin-scene-workspace_activate` | modify | Pin Scene to Workspace |
| `foxos 3d scene activate` | `3d_scene_activate` | modify | Scene |
| `foxos 3d scene set VALUE [--submit]` | `3d_scene_set` | modify | Scene |
| `foxos 3d scene create` | `3d_scene_create` | modify | New Scene |
| `foxos 3d scene delete` | `3d_scene_delete` | delete | Delete Scene |
| `foxos 3d layer show` | `3d_layer_show` | read | View Layer |
| `foxos 3d viewlayer set VALUE [--submit]` | `3d_viewlayer_set` | modify | ViewLayer |
| `foxos 3d view-layer create` | `3d_view-layer_create` | modify | Add View Layer |
| `foxos 3d view-layer delete` | `3d_view-layer_delete` | delete | Remove View Layer |
| `foxos 3d object-mode activate` | `3d_object-mode_activate` | modify | Object Mode |
| `foxos 3d view-2 show` | `3d_view-2_show` | read | View |
| `foxos 3d select select` | `3d_select_select` | read | Select |
| `foxos 3d add create` | `3d_add_create` | modify | Add |
| `foxos 3d object activate` | `3d_object_activate` | modify | Object |
| `foxos 3d global activate` | `3d_global_activate` | modify | Global |
| `foxos 3d options activate` | `3d_options_activate` | modify | Options |
| `foxos 3d marker activate` | `3d_marker_activate` | modify | Marker |
| `foxos 3d playback activate` | `3d_playback_activate` | modify | Playback |
| `foxos 3d search set VALUE [--submit]` | `3d_search_set` | modify | Search |
| `foxos 3d collapse collapse` | `3d_collapse_collapse` | read | Collapse |
| `foxos 3d expand expand` | `3d_expand_expand` | read | Expand |
| `foxos 3d menus activate` | `3d_menus_activate` | modify | Menus |
| `foxos 3d search-ctrl-f set VALUE [--submit]` | `3d_search-ctrl-f_set` | modify | Search (Ctrl F) |
| `foxos 3d cube set VALUE [--submit]` | `3d_cube_set` | modify | Cube |
| `foxos 3d location-x lock` | `3d_location-x_lock` | modify | Lock Location X |
| `foxos 3d location-y lock` | `3d_location-y_lock` | modify | Lock Location Y |
| `foxos 3d location-z lock` | `3d_location-z_lock` | modify | Lock Location Z |
| `foxos 3d rotation-x lock` | `3d_rotation-x_lock` | modify | Lock Rotation X |
| `foxos 3d rotation-y lock` | `3d_rotation-y_lock` | modify | Lock Rotation Y |
| `foxos 3d rotation-z lock` | `3d_rotation-z_lock` | modify | Lock Rotation Z |
| `foxos 3d xyz-euler activate` | `3d_xyz-euler_activate` | modify | XYZ Euler |
| `foxos 3d scale-x lock` | `3d_scale-x_lock` | modify | Lock Scale X |
| `foxos 3d scale-y lock` | `3d_scale-y_lock` | modify | Lock Scale Y |
| `foxos 3d scale-z lock` | `3d_scale-z_lock` | modify | Lock Scale Z |
| `foxos 3d ai-model set VALUE [--submit]` | `3d_ai-model_set` | modify | AI model |
| `foxos 3d chat create` | `3d_chat_create` | modify | New chat |
| `foxos 3d assistant close` | `3d_assistant_close` | read | Close the assistant |
| `foxos 3d wooden-dining-table-four-chairs activate` | `3d_wooden-dining-table-four-chairs_activate` | modify | A wooden dining table with four chairs |
| `foxos 3d snowman-carrot-nose-scarf activate` | `3d_snowman-carrot-nose-scarf_activate` | modify | A snowman with a carrot nose and a scarf |
| `foxos 3d attach-files activate` | `3d_attach-files_activate` | modify | Attach files |
| `foxos 3d message-assistant set VALUE [--submit]` | `3d_message-assistant_set` | modify | Message the assistant |
| `foxos 3d send send` | `3d_send_send` | modify | Send |
| `foxos 3d default activate` | `3d_default_activate` | modify | Default |
| `foxos 3d graphite activate` | `3d_graphite_activate` | modify | Graphite |
| `foxos 3d midnight activate` | `3d_midnight_activate` | modify | Midnight |
| `foxos 3d light activate` | `3d_light_activate` | modify | Light |
| `foxos 3d high-contrast activate` | `3d_high-contrast_activate` | modify | High Contrast |
| `foxos 3d compact activate` | `3d_compact_activate` | modify | Compact |
| `foxos 3d normal activate` | `3d_normal_activate` | modify | Normal |
| `foxos 3d large activate` | `3d_large_activate` | modify | Large |
| `foxos 3d larger activate` | `3d_larger_activate` | modify | Larger |
| `foxos 3d play play` | `3d_play_play` | modify | Play |
| `foxos 3d tools activate` | `3d_tools_activate` | modify | Tools |
| `foxos 3d search search` | `3d_search_search` | read | Search |
| `foxos 3d continue activate` | `3d_continue_activate` | modify | Continue |
| `foxos 3d newctrl-n activate` | `3d_newctrl-n_activate` | modify | NewCtrl N |
| `foxos 3d ctrl-o open` | `3d_ctrl-o_open` | read | Open…Ctrl O |
| `foxos 3d recentshift-ctrl-o open` | `3d_recentshift-ctrl-o_open` | read | Open RecentShift Ctrl O |
| `foxos 3d revert activate` | `3d_revert_activate` | modify | Revert |
| `foxos 3d recover activate` | `3d_recover_activate` | modify | Recover |
| `foxos 3d savectrl-s activate` | `3d_savectrl-s_activate` | modify | SaveCtrl S |
| `foxos 3d as-shift-ctrl-s save` | `3d_as-shift-ctrl-s_save` | modify | Save As…Shift Ctrl S |
| `foxos 3d copy save` | `3d_copy_save` | modify | Save Copy… |
| `foxos 3d incrementalctrl-alt-s save` | `3d_incrementalctrl-alt-s_save` | modify | Save IncrementalCtrl Alt S |
| `foxos 3d link activate` | `3d_link_activate` | modify | Link… |
| `foxos 3d append activate` | `3d_append_activate` | modify | Append… |
| `foxos 3d data-previews activate` | `3d_data-previews_activate` | modify | Data Previews |
| `foxos 3d import import` | `3d_import_import` | modify | Import |
| `foxos 3d export export` | `3d_export_export` | modify | Export |
| `foxos 3d collections export` | `3d_collections_export` | modify | Export All Collections |
| `foxos 3d external-data activate` | `3d_external-data_activate` | modify | External Data |
| `foxos 3d clean-up activate` | `3d_clean-up_activate` | modify | Clean Up |
| `foxos 3d defaults activate` | `3d_defaults_activate` | modify | Defaults |
| `foxos 3d quitctrl-q activate` | `3d_quitctrl-q_activate` | modify | QuitCtrl Q |
| `foxos 3d undoctrl-z activate` | `3d_undoctrl-z_activate` | modify | UndoCtrl Z |
| `foxos 3d redoshift-ctrl-z activate` | `3d_redoshift-ctrl-z_activate` | modify | RedoShift Ctrl Z |
| `foxos 3d historyctrl-alt-z undo` | `3d_historyctrl-alt-z_undo` | modify | Undo HistoryCtrl Alt Z |
| `foxos 3d repeat-lastshift-r activate` | `3d_repeat-lastshift-r_activate` | modify | Repeat LastShift R |
| `foxos 3d repeat-history activate` | `3d_repeat-history_activate` | modify | Repeat History… |
| `foxos 3d preferences-ctrl activate` | `3d_preferences-ctrl_activate` | modify | Preferences…Ctrl , |
| `foxos 3d render-audio activate` | `3d_render-audio_activate` | modify | Render Audio… |
| `foxos 3d interface lock` | `3d_interface_lock` | modify | Lock Interface |
| `foxos 3d window create` | `3d_window_create` | modify | New Window |
| `foxos 3d main-window create` | `3d_main-window_create` | modify | New Main Window |
| `foxos 3d window-fullscreen toggle` | `3d_window-fullscreen_toggle` | modify | Toggle Window Fullscreen |
| `foxos 3d workspacectrl-page-down next` | `3d_workspacectrl-page-down_next` | read | Next WorkspaceCtrl Page Down |
| `foxos 3d workspacectrl-page-up previous` | `3d_workspacectrl-page-up_previous` | read | Previous WorkspaceCtrl Page Up |
| `foxos 3d status-bar show` | `3d_status-bar_show` | read | Show Status Bar |
| `foxos 3d status-bar-scene-statistics activate` | `3d_status-bar-scene-statistics_activate` | modify | Status Bar Scene Statistics |
| `foxos 3d ai-assistant activate` | `3d_ai-assistant_activate` | modify | AI Assistant |
| `foxos 3d screenshot save` | `3d_screenshot_save` | modify | Save Screenshot |
| `foxos 3d screenshot-editor save` | `3d_screenshot-editor_save` | modify | Save Screenshot (Editor) |
| `foxos 3d keyboard-shortcuts activate` | `3d_keyboard-shortcuts_activate` | modify | Keyboard Shortcuts |
| `foxos 3d report-bug activate` | `3d_report-bug_activate` | modify | Report a Bug |
| `foxos 3d system-info save` | `3d_system-info_save` | modify | Save System Info |
| `foxos 3d about show` | `3d_about_show` | read | About |
| `foxos 3d mode update` | `3d_mode_update` | modify | Edit Mode |
| `foxos 3d x activate` | `3d_x_activate` | modify | X |
| `foxos 3d y activate` | `3d_y_activate` | modify | Y |
| `foxos 3d z activate` | `3d_z_activate` | modify | Z |
| `foxos 3d modifier create` | `3d_modifier_create` | modify | Add Modifier |
| `foxos 3d sculpt-mode activate` | `3d_sculpt-mode_activate` | modify | Sculpt Mode |
| `foxos 3d sculpt activate` | `3d_sculpt_activate` | modify | Sculpt |
| `foxos 3d mask activate` | `3d_mask_activate` | modify | Mask |
| `foxos 3d face-sets activate` | `3d_face-sets_activate` | modify | Face Sets |
| `foxos 3d brush activate` | `3d_brush_activate` | modify | Brush |
| `foxos 3d texture activate` | `3d_texture_activate` | modify | Texture |
| `foxos 3d stroke activate` | `3d_stroke_activate` | modify | Stroke |
| `foxos 3d falloff activate` | `3d_falloff_activate` | modify | Falloff |
| `foxos 3d cursor activate` | `3d_cursor_activate` | modify | Cursor |
| `foxos 3d remesh activate` | `3d_remesh_activate` | modify | Remesh |
| `foxos 3d subtract create` | `3d_subtract_create` | modify | Add/Subtract |
| `foxos 3d contrast-smooth activate` | `3d_contrast-smooth_activate` | modify | Contrast & Smooth |
| `foxos 3d transform activate` | `3d_transform_activate` | modify | Transform |
| `foxos 3d simplify activate` | `3d_simplify_activate` | modify | Simplify |
| `foxos 3d utilities activate` | `3d_utilities_activate` | modify | Utilities |
| `foxos 3d paint activate` | `3d_paint_activate` | modify | Paint |
| `foxos 3d assets activate` | `3d_assets_activate` | modify | Assets |
| `foxos 3d draw draw` | `3d_draw_draw` | modify | Draw |
| `foxos 3d sharp draw` | `3d_sharp_draw` | modify | Draw Sharp |
| `foxos 3d clay activate` | `3d_clay_activate` | modify | Clay |
| `foxos 3d clay-strips activate` | `3d_clay-strips_activate` | modify | Clay Strips |
| `foxos 3d clay-thumb activate` | `3d_clay-thumb_activate` | modify | Clay Thumb |
| `foxos 3d layer activate` | `3d_layer_activate` | modify | Layer |
| `foxos 3d inflate-deflate activate` | `3d_inflate-deflate_activate` | modify | Inflate/Deflate |
| `foxos 3d blob activate` | `3d_blob_activate` | modify | Blob |
| `foxos 3d crease activate` | `3d_crease_activate` | modify | Crease |
| `foxos 3d smooth activate` | `3d_smooth_activate` | modify | Smooth |
| `foxos 3d flatten-contrast activate` | `3d_flatten-contrast_activate` | modify | Flatten/Contrast |
| `foxos 3d fill-deepen activate` | `3d_fill-deepen_activate` | modify | Fill/Deepen |
| `foxos 3d scrape-peaks activate` | `3d_scrape-peaks_activate` | modify | Scrape/Peaks |
| `foxos 3d multiplane-scrape activate` | `3d_multiplane-scrape_activate` | modify | Multiplane Scrape |
| `foxos 3d pinch-magnify activate` | `3d_pinch-magnify_activate` | modify | Pinch/Magnify |
| `foxos 3d grab activate` | `3d_grab_activate` | modify | Grab |
| `foxos 3d elastic-deform activate` | `3d_elastic-deform_activate` | modify | Elastic Deform |
| `foxos 3d snake-hook activate` | `3d_snake-hook_activate` | modify | Snake Hook |
| `foxos 3d thumb activate` | `3d_thumb_activate` | modify | Thumb |
| `foxos 3d pose activate` | `3d_pose_activate` | modify | Pose |
| `foxos 3d nudge activate` | `3d_nudge_activate` | modify | Nudge |
| `foxos 3d rotate rotate` | `3d_rotate_rotate` | modify | Rotate |
| `foxos 3d boundary activate` | `3d_boundary_activate` | modify | Boundary |
| `foxos 3d cloth activate` | `3d_cloth_activate` | modify | Cloth |
| `foxos 3d slide-relax activate` | `3d_slide-relax_activate` | modify | Slide Relax |
| `foxos 3d face-sets draw` | `3d_face-sets_draw` | modify | Draw Face Sets |
| `foxos 3d smear activate` | `3d_smear_activate` | modify | Smear |
| `foxos 3d crisp-crease activate` | `3d_crisp-crease_activate` | modify | Crisp Crease |
| `foxos 3d noise-detail activate` | `3d_noise-detail_activate` | modify | Noise Detail |
| `foxos 3d soft-clay activate` | `3d_soft-clay_activate` | modify | Soft Clay |
| `foxos 3d steady-line activate` | `3d_steady-line_activate` | modify | Steady Line |
| `foxos 3d sculpting-scene activate` | `3d_sculpting-scene_activate` | modify | Scene |
| `foxos 3d voxel-remesh activate` | `3d_voxel-remesh_activate` | modify | Voxel Remesh |
| `foxos 3d x-x activate` | `3d_x-x_activate` | modify | -X to +X |
| `foxos 3d symmetrize activate` | `3d_symmetrize_activate` | modify | Symmetrize |
| `foxos 3d shared-location activate` | `3d_shared-location_activate` | modify | Shared Location |
| `foxos 3d no-image activate` | `3d_no-image_activate` | modify | No Image |
| `foxos 3d material-base-color set VALUE [--submit]` | `3d_material-base-color_set` | modify | Material Base Color |
| `foxos 3d mix activate` | `3d_mix_activate` | modify | Mix |
| `foxos 3d texture-paint activate` | `3d_texture-paint_activate` | modify | Texture Paint |
| `foxos 3d soften activate` | `3d_soften_activate` | modify | Soften |
| `foxos 3d clone activate` | `3d_clone_activate` | modify | Clone |
| `foxos 3d fill activate` | `3d_fill_activate` | modify | Fill |
| `foxos 3d airbrush activate` | `3d_airbrush_activate` | modify | Airbrush |
| `foxos 3d paint-soft-pressure activate` | `3d_paint-soft-pressure_activate` | modify | Paint Soft Pressure |
| `foxos 3d pencil activate` | `3d_pencil_activate` | modify | Pencil |
| `foxos 3d red-airbrush activate` | `3d_red-airbrush_activate` | modify | Red Airbrush |
| `foxos 3d speckle activate` | `3d_speckle_activate` | modify | Speckle |
| `foxos 3d color activate` | `3d_color_activate` | modify | Color |
| `foxos 3d gradient activate` | `3d_gradient_activate` | modify | Gradient |
| `foxos 3d base-color-texture create` | `3d_base-color-texture_create` | modify | New Base Color Texture |
| `foxos 3d back previous` | `3d_back_previous` | read | Back |
| `foxos 3d forward next` | `3d_forward_next` | read | Forward |
| `foxos 3d parent-directory activate` | `3d_parent-directory_activate` | modify | Parent Directory |
| `foxos 3d refresh activate` | `3d_refresh_activate` | modify | Refresh |
| `foxos 3d directory create` | `3d_directory_create` | modify | Create New Directory |
| `foxos 3d no-folder-opened activate` | `3d_no-folder-opened_activate` | modify | No folder opened |
| `foxos 3d settings filter` | `3d_settings_filter` | read | Filter settings |
| `foxos 3d folder open` | `3d_folder_open` | read | Open Folder… |
| `foxos 3d browser-storage activate` | `3d_browser-storage_activate` | modify | Browser Storage |
| `foxos 3d files create` | `3d_files_create` | modify | Add Files… |
| `foxos 3d open open` | `3d_open_open` | read | Open |
| `foxos 3d material set VALUE [--submit]` | `3d_material_set` | modify | Material |
| `foxos 3d world set VALUE [--submit]` | `3d_world_set` | modify | World |
| `foxos 3d background activate` | `3d_background_activate` | modify | Background |
| `foxos 3d dope-sheet activate` | `3d_dope-sheet_activate` | modify | Dope Sheet |
| `foxos 3d channel activate` | `3d_channel_activate` | modify | Channel |
| `foxos 3d key activate` | `3d_key_activate` | modify | Key |
| `foxos 3d keying activate` | `3d_keying_activate` | modify | Keying |
| `foxos 3d image activate` | `3d_image_activate` | modify | Image |
| `foxos 3d tool activate` | `3d_tool_activate` | modify | Tool |
| `foxos 3d scopes activate` | `3d_scopes_activate` | modify | Scopes |
| `foxos 3d realtime-raster activate` | `3d_realtime-raster_activate` | modify | Realtime (Raster) |
| `foxos 3d backdrop activate` | `3d_backdrop_activate` | modify | Backdrop |
| `foxos 3d node activate` | `3d_node_activate` | modify | Node |
| `foxos 3d render set VALUE [--submit]` | `3d_render_set` | modify | //render/ |
| `foxos 3d png activate` | `3d_png_activate` | modify | PNG |
| `foxos 3d rgba activate` | `3d_rgba_activate` | modify | RGBA |
| `foxos 3d selection copy` | `3d_selection_copy` | modify | 快捷键 mod+c |
| `foxos 3d selection lock` | `3d_selection_lock` | modify | 快捷键 mod+l |
| `foxos 3d selection cut` | `3d_selection_cut` | modify | 快捷键 mod+x |
| `foxos 3d edit undo` | `3d_edit_undo` | modify | 快捷键 mod+z |

### cad（`cad`，180 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos cad arc select TARGET` | `cad_arc_select` | read | arc, #（1 项，如 Arc, 3-Point） |
| `foxos cad application-menu select TARGET` | `cad_application-menu_select` | read | #（1 项，如 HelpF1） |
| `foxos cad circle-options select TARGET` | `cad_circle-options_select` | read | #（2 项，如 2-Point） |
| `foxos cad arc-options select TARGET` | `cad_arc-options_select` | read | #（1 项，如 3-Point） |
| `foxos cad application-menu activate` | `cad_application-menu_activate` | modify | Application menu |
| `foxos cad drawing create` | `cad_drawing_create` | modify | New drawing |
| `foxos cad open open` | `cad_open_open` | read | Open |
| `foxos cad save save` | `cad_save_save` | modify | Save |
| `foxos cad undo undo` | `cad_undo_undo` | modify | Undo |
| `foxos cad redo redo` | `cad_redo_redo` | modify | Redo |
| `foxos cad plot activate` | `cad_plot_activate` | modify | Plot |
| `foxos cad commands search` | `cad_commands_search` | read | Search commands |
| `foxos cad theme activate` | `cad_theme_activate` | modify | Theme |
| `foxos cad help show` | `cad_help_show` | read | Help |
| `foxos cad source-code-github-opens-tab show` | `cad_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos cad home show` | `cad_home_show` | read | Home |
| `foxos cad insert create` | `cad_insert_create` | modify | Insert |
| `foxos cad annotate show` | `cad_annotate_show` | read | Annotate |
| `foxos cad view show` | `cad_view_show` | read | View |
| `foxos cad manage show` | `cad_manage_show` | read | Manage |
| `foxos cad output show` | `cad_output_show` | read | Output |
| `foxos cad minimize-ribbon activate` | `cad_minimize-ribbon_activate` | modify | Minimize the ribbon |
| `foxos cad line activate` | `cad_line_activate` | modify | Line |
| `foxos cad polyline activate` | `cad_polyline_activate` | modify | Polyline |
| `foxos cad circle-center-radius activate` | `cad_circle-center-radius_activate` | modify | Circle, Center, Radius |
| `foxos cad circle-options activate` | `cad_circle-options_activate` | modify | Circle options |
| `foxos cad arc-options activate` | `cad_arc-options_activate` | modify | Arc options |
| `foxos cad rectangle activate` | `cad_rectangle_activate` | modify | Rectangle |
| `foxos cad rectangle-options activate` | `cad_rectangle-options_activate` | modify | Rectangle options |
| `foxos cad ellipse activate` | `cad_ellipse_activate` | modify | Ellipse |
| `foxos cad ellipse-options activate` | `cad_ellipse-options_activate` | modify | Ellipse options |
| `foxos cad hatch activate` | `cad_hatch_activate` | modify | Hatch |
| `foxos cad spline activate` | `cad_spline_activate` | modify | Spline |
| `foxos cad construction-line activate` | `cad_construction-line_activate` | modify | Construction line |
| `foxos cad point activate` | `cad_point_activate` | modify | Point |
| `foxos cad draw draw` | `cad_draw_draw` | modify | Draw |
| `foxos cad move move` | `cad_move_move` | modify | Move |
| `foxos cad copy copy` | `cad_copy_copy` | modify | Copy |
| `foxos cad stretch activate` | `cad_stretch_activate` | modify | Stretch |
| `foxos cad rotate rotate` | `cad_rotate_rotate` | modify | Rotate |
| `foxos cad mirror activate` | `cad_mirror_activate` | modify | Mirror |
| `foxos cad scale activate` | `cad_scale_activate` | modify | Scale |
| `foxos cad trim activate` | `cad_trim_activate` | modify | Trim |
| `foxos cad trim-options activate` | `cad_trim-options_activate` | modify | Trim options |
| `foxos cad fillet activate` | `cad_fillet_activate` | modify | Fillet |
| `foxos cad fillet-options activate` | `cad_fillet-options_activate` | modify | Fillet options |
| `foxos cad array activate` | `cad_array_activate` | modify | Array |
| `foxos cad array-options activate` | `cad_array-options_activate` | modify | Array options |
| `foxos cad erase activate` | `cad_erase_activate` | modify | Erase |
| `foxos cad explode activate` | `cad_explode_activate` | modify | Explode |
| `foxos cad offset activate` | `cad_offset_activate` | modify | Offset |
| `foxos cad modify update` | `cad_modify_update` | modify | Modify |
| `foxos cad text-multiline-text activate` | `cad_text-multiline-text_activate` | modify | Text, Multiline text |
| `foxos cad text-options activate` | `cad_text-options_activate` | modify | Text options |
| `foxos cad dimension-linear activate` | `cad_dimension-linear_activate` | modify | Dimension, Linear |
| `foxos cad dimension-options activate` | `cad_dimension-options_activate` | modify | Dimension options |
| `foxos cad leader activate` | `cad_leader_activate` | modify | Leader |
| `foxos cad continue activate` | `cad_continue_activate` | modify | Continue |
| `foxos cad baseline activate` | `cad_baseline_activate` | modify | Baseline |
| `foxos cad layer-properties activate` | `cad_layer-properties_activate` | modify | Layer Properties |
| `foxos cad turn-layer-off activate` | `cad_turn-layer-off_activate` | modify | Turn layer off |
| `foxos cad isolate-layers activate` | `cad_isolate-layers_activate` | modify | Isolate layers |
| `foxos cad freeze-layer activate` | `cad_freeze-layer_activate` | modify | Freeze layer |
| `foxos cad layer lock` | `cad_layer_lock` | modify | Lock layer |
| `foxos cad make-current activate` | `cad_make-current_activate` | modify | Make Current |
| `foxos cad turn-layers activate` | `cad_turn-layers_activate` | modify | Turn all layers on |
| `foxos cad unisolate-layers activate` | `cad_unisolate-layers_activate` | modify | Unisolate layers |
| `foxos cad thaw-layers activate` | `cad_thaw-layers_activate` | modify | Thaw all layers |
| `foxos cad layer unlock` | `cad_layer_unlock` | modify | Unlock layer |
| `foxos cad match-layer activate` | `cad_match-layer_activate` | modify | Match Layer |
| `foxos cad insert-2 create` | `cad_insert-2_create` | modify | Insert |
| `foxos cad create create` | `cad_create_create` | modify | Create |
| `foxos cad library activate` | `cad_library_activate` | modify | Library |
| `foxos cad match-properties activate` | `cad_match-properties_activate` | modify | Match Properties |
| `foxos cad measure-distance activate` | `cad_measure-distance_activate` | modify | Measure, Distance |
| `foxos cad measure-options activate` | `cad_measure-options_activate` | modify | Measure options |
| `foxos cad quick-select activate` | `cad_quick-select_activate` | modify | Quick select |
| `foxos cad select select` | `cad_select_select` | read | Select all |
| `foxos cad similar select` | `cad_similar_select` | read | Select similar |
| `foxos cad paste paste` | `cad_paste_paste` | modify | Paste |
| `foxos cad cut cut` | `cad_cut_cut` | modify | Cut |
| `foxos cad clipboard copy` | `cad_clipboard_copy` | modify | Copy to clipboard |
| `foxos cad base-point copy` | `cad_base-point_copy` | modify | Copy with base point |
| `foxos cad it dismiss` | `cad_it_dismiss` | read | Got it |
| `foxos cad cursor-coordinates-click-change-display activate` | `cad_cursor-coordinates-click-change-display_activate` | modify | Cursor coordinates. Click to change the display. |
| `foxos cad grid activate` | `cad_grid_activate` | modify | Grid |
| `foxos cad snap-grid activate` | `cad_snap-grid_activate` | modify | Snap to grid |
| `foxos cad snap-grid-settings activate` | `cad_snap-grid-settings_activate` | modify | Snap to grid settings |
| `foxos cad ortho-mode activate` | `cad_ortho-mode_activate` | modify | Ortho mode |
| `foxos cad polar-tracking activate` | `cad_polar-tracking_activate` | modify | Polar tracking |
| `foxos cad polar-tracking-settings activate` | `cad_polar-tracking-settings_activate` | modify | Polar tracking settings |
| `foxos cad object-snap activate` | `cad_object-snap_activate` | modify | Object snap |
| `foxos cad object-snap-settings activate` | `cad_object-snap-settings_activate` | modify | Object snap settings |
| `foxos cad object-snap-tracking activate` | `cad_object-snap-tracking_activate` | modify | Object snap tracking |
| `foxos cad dynamic-input activate` | `cad_dynamic-input_activate` | modify | Dynamic input |
| `foxos cad lineweights show` | `cad_lineweights_show` | read | Show lineweights |
| `foxos cad selection-preview activate` | `cad_selection-preview_activate` | modify | Selection preview |
| `foxos cad drawing-units activate` | `cad_drawing-units_activate` | modify | Drawing units |
| `foxos cad drafting-settings activate` | `cad_drafting-settings_activate` | modify | Drafting settings |
| `foxos cad clean-screen activate` | `cad_clean-screen_activate` | modify | Clean screen |
| `foxos cad newctrln activate` | `cad_newctrln_activate` | modify | NewCtrl+N |
| `foxos cad ctrlo open` | `cad_ctrlo_open` | read | Open...Ctrl+O |
| `foxos cad sample-drawing open` | `cad_sample-drawing_open` | read | Open sample drawing |
| `foxos cad savectrls activate` | `cad_savectrls_activate` | modify | SaveCtrl+S |
| `foxos cad as-ctrlshifts save` | `cad_as-ctrlshifts_save` | modify | Save as...Ctrl+Shift+S |
| `foxos cad dxf-or-dwg import` | `cad_dxf-or-dwg_import` | modify | Import DXF or DWG... |
| `foxos cad export export` | `cad_export_export` | modify | Export... |
| `foxos cad plot-ctrlp activate` | `cad_plot-ctrlp_activate` | modify | Plot...Ctrl+P |
| `foxos cad application-menu-drawing-units activate` | `cad_application-menu-drawing-units_activate` | modify | Drawing units... |
| `foxos cad purge-unused activate` | `cad_purge-unused_activate` | modify | Purge unused... |
| `foxos cad settings show` | `cad_settings_show` | read | Settings... |
| `foxos cad keyboard-shortcuts activate` | `cad_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos cad source-code-github activate` | `cad_source-code-github_activate` | modify | Source code on GitHub |
| `foxos cad drawing close` | `cad_drawing_close` | read | Close drawing |
| `foxos cad close close` | `cad_close_close` | read | Close |
| `foxos cad search-commands set VALUE [--submit]` | `cad_search-commands_set` | modify | Search commands |
| `foxos cad alignalign activate` | `cad_alignalign_activate` | modify | AlignALIGN |
| `foxos cad aligned-dimensiondimaligned activate` | `cad_aligned-dimensiondimaligned_activate` | modify | Aligned dimensionDIMALIGNED |
| `foxos cad angular-dimensiondimangular activate` | `cad_angular-dimensiondimangular_activate` | modify | Angular dimensionDIMANGULAR |
| `foxos cad arcarc activate` | `cad_arcarc_activate` | modify | ArcARC |
| `foxos cad baseline-dimensiondimbaseline activate` | `cad_baseline-dimensiondimbaseline_activate` | modify | Baseline dimensionDIMBASELINE |
| `foxos cad blocks-paletteblocks activate` | `cad_blocks-paletteblocks_activate` | modify | Blocks paletteBLOCKS |
| `foxos cad breakbreak activate` | `cad_breakbreak_activate` | modify | BreakBREAK |
| `foxos cad break-at-pointbreakatpoint activate` | `cad_break-at-pointbreakatpoint_activate` | modify | Break at pointBREAKATPOINT |
| `foxos cad chamferchamfer activate` | `cad_chamferchamfer_activate` | modify | ChamferCHAMFER |
| `foxos cad circlecircle activate` | `cad_circlecircle_activate` | modify | CircleCIRCLE |
| `foxos cad clean-screencleanscreen activate` | `cad_clean-screencleanscreen_activate` | modify | Clean screenCLEANSCREEN |
| `foxos cad drawingclose close` | `cad_drawingclose_close` | read | Close drawingCLOSE |
| `foxos cad construction-linexline activate` | `cad_construction-linexline_activate` | modify | Construction lineXLINE |
| `foxos cad continue-dimensiondimcontinue activate` | `cad_continue-dimensiondimcontinue_activate` | modify | Continue dimensionDIMCONTINUE |
| `foxos cad copycopy activate` | `cad_copycopy_activate` | modify | CopyCOPY |
| `foxos cad clipboardcopyclip copy` | `cad_clipboardcopyclip_copy` | modify | Copy to clipboardCOPYCLIP |
| `foxos cad base-pointcopybase copy` | `cad_base-pointcopybase_copy` | modify | Copy with base pointCOPYBASE |
| `foxos cad blockblock create` | `cad_blockblock_create` | modify | Create blockBLOCK |
| `foxos cad cutcutclip activate` | `cad_cutcutclip_activate` | modify | CutCUTCLIP |
| `foxos cad diameter-dimensiondimdiameter activate` | `cad_diameter-dimensiondimdiameter_activate` | modify | Diameter dimensionDIMDIAMETER |
| `foxos cad dimensiondim activate` | `cad_dimensiondim_activate` | modify | DimensionDIM |
| `foxos cad dimension-stylesdimstyle activate` | `cad_dimension-stylesdimstyle_activate` | modify | Dimension stylesDIMSTYLE |
| `foxos cad donutdonut activate` | `cad_donutdonut_activate` | modify | DonutDONUT |
| `foxos cad drafting-settingsdsettings activate` | `cad_drafting-settingsdsettings_activate` | modify | Drafting settingsDSETTINGS |
| `foxos cad orderdraworder draw` | `cad_orderdraworder_draw` | modify | Draw orderDRAWORDER |
| `foxos cad drawing-unitsunits activate` | `cad_drawing-unitsunits_activate` | modify | Drawing unitsUNITS |
| `foxos cad ellipseellipse activate` | `cad_ellipseellipse_activate` | modify | EllipseELLIPSE |
| `foxos cad eraseerase activate` | `cad_eraseerase_activate` | modify | EraseERASE |
| `foxos cad explodeexplode activate` | `cad_explodeexplode_activate` | modify | ExplodeEXPLODE |
| `foxos cad exportexport activate` | `cad_exportexport_activate` | modify | ExportEXPORT |
| `foxos cad dwgdwgout export` | `cad_dwgdwgout_export` | modify | Export DWGDWGOUT |
| `foxos cad dxfdxfout export` | `cad_dxfdxfout_export` | modify | Export DXFDXFOUT |
| `foxos cad extendextend activate` | `cad_extendextend_activate` | modify | ExtendEXTEND |
| `foxos cad filletfillet activate` | `cad_filletfillet_activate` | modify | FilletFILLET |
| `foxos cad freeze-layerlayfrz activate` | `cad_freeze-layerlayfrz_activate` | modify | Freeze layerLAYFRZ |
| `foxos cad grid-displaygrid activate` | `cad_grid-displaygrid_activate` | modify | Grid displayGRID |
| `foxos cad hatchhatch activate` | `cad_hatchhatch_activate` | modify | HatchHATCH |
| `foxos cad helphelp activate` | `cad_helphelp_activate` | modify | HelpHELP |
| `foxos cad dxf-or-dwgimport import` | `cad_dxf-or-dwgimport_import` | modify | Import DXF or DWGIMPORT |
| `foxos cad blockinsert create` | `cad_blockinsert_create` | modify | Insert blockINSERT |
| `foxos cad isolate-layerslayiso activate` | `cad_isolate-layerslayiso_activate` | modify | Isolate layersLAYISO |
| `foxos cad joinjoin activate` | `cad_joinjoin_activate` | modify | JoinJOIN |
| `foxos cad keyboard-shortcutsshortcuts activate` | `cad_keyboard-shortcutsshortcuts_activate` | modify | Keyboard shortcutsSHORTCUTS |
| `foxos cad layer-propertieslayer activate` | `cad_layer-propertieslayer_activate` | modify | Layer propertiesLAYER |
| `foxos cad leaderleader activate` | `cad_leaderleader_activate` | modify | LeaderLEADER |
| `foxos cad lengthenlengthen activate` | `cad_lengthenlengthen_activate` | modify | LengthenLENGTHEN |
| `foxos cad lineline activate` | `cad_lineline_activate` | modify | LineLINE |
| `foxos cad linear-dimensiondimlinear activate` | `cad_linear-dimensiondimlinear_activate` | modify | Linear dimensionDIMLINEAR |
| `foxos cad linetype-scaleltscale activate` | `cad_linetype-scaleltscale_activate` | modify | Linetype scaleLTSCALE |
| `foxos cad linetypeslinetype activate` | `cad_linetypeslinetype_activate` | modify | LinetypesLINETYPE |
| `foxos cad system activate` | `cad_system_activate` | modify | System |
| `foxos cad light activate` | `cad_light_activate` | modify | Light |
| `foxos cad dark activate` | `cad_dark_activate` | modify | Dark |
| `foxos cad center-radius activate` | `cad_center-radius_activate` | modify | Center, Radius |
| `foxos cad center-diameter activate` | `cad_center-diameter_activate` | modify | Center, Diameter |
| `foxos cad tan-tan-radius activate` | `cad_tan-tan-radius_activate` | modify | Tan, Tan, Radius |
| `foxos cad center-end start` | `cad_center-end_start` | modify | Start, Center, End |
| `foxos cad center-start-end activate` | `cad_center-start-end_activate` | modify | Center, Start, End |
| `foxos cad end-radius start` | `cad_end-radius_start` | modify | Start, End, Radius |
| `foxos cad rectangle-options-rectangle activate` | `cad_rectangle-options-rectangle_activate` | modify | Rectangle |
| `foxos cad polygon activate` | `cad_polygon_activate` | modify | Polygon |
| `foxos cad center activate` | `cad_center_activate` | modify | Center |
| `foxos cad axis-end activate` | `cad_axis-end_activate` | modify | Axis, End |
| `foxos cad elliptical-arc activate` | `cad_elliptical-arc_activate` | modify | Elliptical arc |

### parametric（`parametric`，32 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos parametric item select TARGET` | `parametric_item_select` | read | # view. use arrow keys to rotate, ctrl and arrow keys to pan, f to fit, plus and minus to zoom.（1 项，如 3D view. Use arrow keys to rotate, Ctrl and arrow keys to pan, F to fit, plus and minus to zoom.） |
| `foxos parametric default-units select TARGET` | `parametric_default-units_select` | read | default units for *（1 项，如 Default units for new parts） |
| `foxos parametric graphics-area dismiss` | `parametric_graphics-area_dismiss` | read | Skip to the graphics area |
| `foxos parametric edit update` | `parametric_edit_update` | modify | Edit |
| `foxos parametric view show` | `parametric_view_show` | read | View |
| `foxos parametric insert create` | `parametric_insert_create` | modify | Insert |
| `foxos parametric tools activate` | `parametric_tools_activate` | modify | Tools |
| `foxos parametric help show` | `parametric_help_show` | read | Help |
| `foxos parametric open open` | `parametric_open_open` | read | Open... |
| `foxos parametric save save` | `parametric_save_save` | modify | Save |
| `foxos parametric undo undo` | `parametric_undo_undo` | modify | Undo |
| `foxos parametric redo redo` | `parametric_redo_redo` | modify | Redo |
| `foxos parametric rebuild activate` | `parametric_rebuild_activate` | modify | Rebuild |
| `foxos parametric options activate` | `parametric_options_activate` | modify | Options... |
| `foxos parametric part rename` | `parametric_part_rename` | modify | Rename part |
| `foxos parametric search-commands set VALUE [--submit]` | `parametric_search-commands_set` | modify | Search commands |
| `foxos parametric assistant activate` | `parametric_assistant_activate` | modify | Assistant |
| `foxos parametric share share` | `parametric_share_share` | modify | Share... |
| `foxos parametric source-code-github show` | `parametric_source-code-github_show` | read | Source code on GitHub |
| `foxos parametric apps activate` | `parametric_apps_activate` | modify | Apps |
| `foxos parametric account activate` | `parametric_account_activate` | modify | Account |
| `foxos parametric panel resize` | `parametric_panel_resize` | modify | Resize panel |
| `foxos parametric unit-system activate` | `parametric_unit-system_activate` | modify | Unit system |
| `foxos parametric close close` | `parametric_close_close` | read | Close |
| `foxos parametric system activate` | `parametric_system_activate` | modify | System |
| `foxos parametric light activate` | `parametric_light_activate` | modify | Light |
| `foxos parametric dark activate` | `parametric_dark_activate` | modify | Dark |
| `foxos parametric image-quality set VALUE [--submit]` | `parametric_image-quality_set` | modify | Image quality |
| `foxos parametric reverse-mouse-wheel-zoom-direction toggle` | `parametric_reverse-mouse-wheel-zoom-direction_toggle` | modify | Reverse mouse wheel zoom direction |
| `foxos parametric done confirm` | `parametric_done_confirm` | modify | Done |
| `foxos parametric apps-tab open` | `parametric_apps-tab_open` | read | Open Apps in a new tab |
| `foxos parametric document save` | `parametric_document_save` | modify | 快捷键 mod+s |

### circuits（`circuits`，38 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos circuits theme select TARGET` | `circuits_theme_select` | read | theme: *（1 项，如 Theme: match system） |
| `foxos circuits account select TARGET` | `circuits_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos circuits examplea-led-blinker-its-board open TARGET` | `circuits_examplea-led-blinker-its-board_open` | read | open the examplea # led blinker with its board（1 项，如 Open the exampleA 555 LED blinker with its board） |
| `foxos circuits design-canvas dismiss` | `circuits_design-canvas_dismiss` | read | Skip to the design canvas |
| `foxos circuits project create` | `circuits_project_create` | modify | New project |
| `foxos circuits project open` | `circuits_project_open` | read | Open project |
| `foxos circuits save save` | `circuits_save_save` | modify | Save |
| `foxos circuits undo undo` | `circuits_undo_undo` | modify | Undo |
| `foxos circuits redo redo` | `circuits_redo_redo` | modify | Redo |
| `foxos circuits commandsctrlk search` | `circuits_commandsctrlk_search` | read | Search commandsCtrl+K |
| `foxos circuits source-code-github-opens-tab show` | `circuits_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos circuits edit update` | `circuits_edit_update` | modify | Edit |
| `foxos circuits view show` | `circuits_view_show` | read | View |
| `foxos circuits project activate` | `circuits_project_activate` | modify | Project |
| `foxos circuits reports activate` | `circuits_reports_activate` | modify | Reports |
| `foxos circuits window activate` | `circuits_window_activate` | modify | Window |
| `foxos circuits help show` | `circuits_help_show` | read | Help |
| `foxos circuits schematic-sheet create` | `circuits_schematic-sheet_create` | modify | Add schematic sheet |
| `foxos circuits board create` | `circuits_board_create` | modify | Add board |
| `foxos circuits project-options activate` | `circuits_project-options_activate` | modify | Project options |
| `foxos circuits projects show` | `circuits_projects_show` | read | Projects |
| `foxos circuits navigator show` | `circuits_navigator_show` | read | Navigator |
| `foxos circuits properties show` | `circuits_properties_show` | read | Properties |
| `foxos circuits components show` | `circuits_components_show` | read | Components |
| `foxos circuits puter show` | `circuits_puter_show` | read | Puter |
| `foxos circuits panels activate` | `circuits_panels_activate` | modify | Panels |
| `foxos circuits it dismiss` | `circuits_it_dismiss` | read | Got it |
| `foxos circuits notification dismiss` | `circuits_notification_dismiss` | read | Dismiss notification |
| `foxos circuits preferences activate` | `circuits_preferences_activate` | modify | Preferences |
| `foxos circuits schematic-sheet activate` | `circuits_schematic-sheet_activate` | modify | Schematic sheet |
| `foxos circuits board activate` | `circuits_board_activate` | modify | Board |
| `foxos circuits project rename` | `circuits_project_rename` | modify | Rename project... |
| `foxos circuits savectrls activate` | `circuits_savectrls_activate` | modify | SaveCtrl+S |
| `foxos circuits project-file export` | `circuits_project-file_export` | modify | Download project file |
| `foxos circuits compile-electrical-rules-check activate` | `circuits_compile-electrical-rules-check_activate` | modify | Compile (electrical rules check) |
| `foxos circuits annotate-schematics activate` | `circuits_annotate-schematics_activate` | modify | Annotate schematics... |
| `foxos circuits board-from-schematic update` | `circuits_board-from-schematic_update` | modify | Update board from schematic... |
| `foxos circuits project close` | `circuits_project_close` | read | Close project |

### building-design（`building-design`，1 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos building-design it dismiss` | `building-design_it_dismiss` | read | Got it |

### tasks（`tasks`，58 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos tasks add create TARGET` | `tasks_add_create` | modify | add for *（1 项，如 Add for today） |
| `foxos tasks skip dismiss TARGET` | `tasks_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos tasks list open TARGET` | `tasks_list_open` | read | open list: *（2 项，如 Open list: Personal） |
| `foxos tasks actions select TARGET` | `tasks_actions_select` | read | actions for *（2 项，如 Actions for Personal） |
| `foxos tasks tasks open TARGET` | `tasks_tasks_open` | read | # open tasks（42 项，如 Mon, Oct 26, 0 open tasks） |
| `foxos tasks week-starts select TARGET` | `tasks_week-starts_select` | read | week starts on #（1 项，如 Week starts on Monday） |
| `foxos tasks content dismiss` | `tasks_content_dismiss` | read | Skip to content |
| `foxos tasks task create` | `tasks_task_create` | modify | New task |
| `foxos tasks today show` | `tasks_today_show` | read | Today |
| `foxos tasks upcoming show` | `tasks_upcoming_show` | read | Upcoming |
| `foxos tasks lists show` | `tasks_lists_show` | read | Lists |
| `foxos tasks calendar show` | `tasks_calendar_show` | read | Calendar |
| `foxos tasks logbook show` | `tasks_logbook_show` | read | Logbook |
| `foxos tasks settings show` | `tasks_settings_show` | read | Settings |
| `foxos tasks list create` | `tasks_list_create` | modify | New list |
| `foxos tasks personal show` | `tasks_personal_show` | read | Personal |
| `foxos tasks work show` | `tasks_work_show` | read | Work |
| `foxos tasks search search` | `tasks_search_search` | read | Search/ |
| `foxos tasks add-task set VALUE [--submit]` | `tasks_add-task_set` | modify | Add a task |
| `foxos tasks options show` | `tasks_options_show` | read | More options |
| `foxos tasks close close` | `tasks_close_close` | read | Close |
| `foxos tasks first-task create` | `tasks_first-task_create` | modify | Add my first task |
| `foxos tasks explore-sample-data activate` | `tasks_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos tasks task-title set VALUE [--submit]` | `tasks_task-title_set` | modify | Task title |
| `foxos tasks notes set VALUE [--submit]` | `tasks_notes_set` | modify | Notes |
| `foxos tasks list set VALUE [--submit]` | `tasks_list_set` | modify | List |
| `foxos tasks due-date set VALUE [--submit]` | `tasks_due-date_set` | modify | Due date |
| `foxos tasks due-time set VALUE [--submit]` | `tasks_due-time_set` | modify | Due time |
| `foxos tasks today activate` | `tasks_today_activate` | modify | Today |
| `foxos tasks tomorrow activate` | `tasks_tomorrow_activate` | modify | Tomorrow |
| `foxos tasks week next` | `tasks_week_next` | read | Next week |
| `foxos tasks no-date activate` | `tasks_no-date_activate` | modify | No date |
| `foxos tasks remind-me set VALUE [--submit]` | `tasks_remind-me_set` | modify | Remind me |
| `foxos tasks none activate` | `tasks_none_activate` | modify | None |
| `foxos tasks low activate` | `tasks_low_activate` | modify | Low |
| `foxos tasks medium activate` | `tasks_medium_activate` | modify | Medium |
| `foxos tasks high activate` | `tasks_high_activate` | modify | High |
| `foxos tasks add-tag set VALUE [--submit]` | `tasks_add-tag_set` | modify | Add a tag |
| `foxos tasks repeat set VALUE [--submit]` | `tasks_repeat_set` | modify | Repeat |
| `foxos tasks subtask create` | `tasks_subtask_create` | modify | Add subtask |
| `foxos tasks cancel cancel` | `tasks_cancel_cancel` | read | Cancel |
| `foxos tasks task-2 create` | `tasks_task-2_create` | modify | Add task |
| `foxos tasks upcoming-task create` | `tasks_upcoming-task_create` | modify | New task |
| `foxos tasks lists-list create` | `tasks_lists-list_create` | modify | New list |
| `foxos tasks ics-calendar-file export` | `tasks_ics-calendar-file_export` | modify | Download .ics calendar file |
| `foxos tasks month previous` | `tasks_month_previous` | read | Previous month |
| `foxos tasks calendar-today activate` | `tasks_calendar-today_activate` | modify | Today |
| `foxos tasks month next` | `tasks_month_next` | read | Next month |
| `foxos tasks system activate` | `tasks_system_activate` | modify | System |
| `foxos tasks light activate` | `tasks_light_activate` | modify | Light |
| `foxos tasks dark activate` | `tasks_dark_activate` | modify | Dark |
| `foxos tasks due-date-reminders toggle` | `tasks_due-date-reminders_toggle` | modify | Due-date reminders |
| `foxos tasks exportdownload-everything-as-json-file activate` | `tasks_exportdownload-everything-as-json-file_activate` | modify | ExportDownload everything as a JSON file |
| `foxos tasks lists previous` | `tasks_lists_previous` | read | Back to lists |
| `foxos tasks list share` | `tasks_list_share` | modify | Share list |
| `foxos tasks list update` | `tasks_list_update` | modify | Edit list |
| `foxos tasks personal-add create` | `tasks_personal-add_create` | modify | Add |
| `foxos tasks search-tasks set VALUE [--submit]` | `tasks_search-tasks_set` | modify | Search tasks |

### projects（`projects`，50 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos projects skip dismiss TARGET` | `projects_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos projects projects show` | `projects_projects_show` | read | Projects |
| `foxos projects quick-addn activate` | `projects_quick-addn_activate` | modify | Quick addn |
| `foxos projects task search` | `projects_task_search` | read | Find a task/ |
| `foxos projects commandsctrlk activate` | `projects_commandsctrlk_activate` | modify | CommandsCtrlK |
| `foxos projects today show` | `projects_today_show` | read | Today |
| `foxos projects tasks show` | `projects_tasks_show` | read | All tasks |
| `foxos projects project create` | `projects_project_create` | modify | New project |
| `foxos projects projects-2 show` | `projects_projects-2_show` | read | All projects |
| `foxos projects settings show` | `projects_settings_show` | read | Settings |
| `foxos projects project-2 create` | `projects_project-2_create` | modify | New project |
| `foxos projects project-3 create` | `projects_project-3_create` | modify | Create a project |
| `foxos projects close close` | `projects_close_close` | read | Close |
| `foxos projects first-project create` | `projects_first-project_create` | modify | Create my first project |
| `foxos projects explore-sample-data activate` | `projects_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos projects today-projects show` | `projects_today-projects_show` | read | All projects |
| `foxos projects overdue show` | `projects_overdue_show` | read | Show Overdue |
| `foxos projects high-priority show` | `projects_high-priority_show` | read | Show High priority |
| `foxos projects unscheduled show` | `projects_unscheduled_show` | read | Show Unscheduled |
| `foxos projects options show` | `projects_options_show` | read | View options |
| `foxos projects filter-tasks-by-title set VALUE [--submit]` | `projects_filter-tasks-by-title_set` | modify | Filter tasks by title |
| `foxos projects label activate` | `projects_label_activate` | modify | Label |
| `foxos projects assignee activate` | `projects_assignee_activate` | modify | Assignee |
| `foxos projects priority activate` | `projects_priority_activate` | modify | Priority |
| `foxos projects due activate` | `projects_due_activate` | modify | Due |
| `foxos projects project activate` | `projects_project_activate` | modify | Project |
| `foxos projects project-order activate` | `projects_project-order_activate` | modify | Project order |
| `foxos projects light toggle` | `projects_light_toggle` | modify | Light |
| `foxos projects dark toggle` | `projects_dark_toggle` | modify | Dark |
| `foxos projects system toggle` | `projects_system_toggle` | modify | System |
| `foxos projects view show` | `projects_view_show` | read | View |
| `foxos projects export export` | `projects_export_export` | modify | Export |
| `foxos projects import import` | `projects_import_import` | modify | Import |
| `foxos projects calendar-file export` | `projects_calendar-file_export` | modify | Export a calendar file |
| `foxos projects restore-points open` | `projects_restore-points_open` | read | Open restore points |
| `foxos projects deleted-projects open` | `projects_deleted-projects_open` | read | Open deleted projects |
| `foxos projects learn-more show` | `projects_learn-more_show` | read | Learn more |
| `foxos projects name set VALUE [--submit]` | `projects_name_set` | modify | Name |
| `foxos projects purple toggle` | `projects_purple_toggle` | modify | Purple |
| `foxos projects teal toggle` | `projects_teal_toggle` | modify | Teal |
| `foxos projects amber toggle` | `projects_amber_toggle` | modify | Amber |
| `foxos projects rose toggle` | `projects_rose_toggle` | modify | Rose |
| `foxos projects indigo toggle` | `projects_indigo_toggle` | modify | Indigo |
| `foxos projects blue toggle` | `projects_blue_toggle` | modify | Blue |
| `foxos projects olive toggle` | `projects_olive_toggle` | modify | Olive |
| `foxos projects rust toggle` | `projects_rust_toggle` | modify | Rust |
| `foxos projects cancel cancel` | `projects_cancel_cancel` | read | Cancel |
| `foxos projects project-4 create` | `projects_project-4_create` | modify | Create project |
| `foxos projects command-palette show` | `projects_command-palette_show` | read | 快捷键 mod+k |
| `foxos projects edit undo` | `projects_edit_undo` | modify | 快捷键 mod+z |

### wiki（`wiki`，60 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos wiki heading select TARGET` | `wiki_heading_select` | read | heading #（1 项，如 Heading 2） |
| `foxos wiki files import TARGET` | `wiki_files_import` | modify | import # files（1 项，如 Import Markdown files） |
| `foxos wiki here import TARGET` | `wiki_here_import` | modify | import # here（1 项，如 Import Markdown here） |
| `foxos wiki page dismiss` | `wiki_page_dismiss` | read | Skip to page |
| `foxos wiki lolocal-s-wiki activate` | `wiki_lolocal-s-wiki_activate` | modify | LOlocal’s wiki |
| `foxos wiki sidebar close` | `wiki_sidebar_close` | read | Close sidebar |
| `foxos wiki searchctrlk activate` | `wiki_searchctrlk_activate` | modify | SearchCtrl+K |
| `foxos wiki home activate` | `wiki_home_activate` | modify | Home |
| `foxos wiki pagectrlaltn create` | `wiki_pagectrlaltn_create` | modify | New pageCtrl+Alt+N |
| `foxos wiki private activate` | `wiki_private_activate` | modify | Private |
| `foxos wiki private-page create` | `wiki_private-page_create` | modify | Add a private page |
| `foxos wiki getting-started activate` | `wiki_getting-started_activate` | modify | Getting started |
| `foxos wiki tasks activate` | `wiki_tasks_activate` | modify | Tasks |
| `foxos wiki notes activate` | `wiki_notes_activate` | modify | Notes |
| `foxos wiki templates activate` | `wiki_templates_activate` | modify | Templates |
| `foxos wiki import import` | `wiki_import_import` | modify | Import |
| `foxos wiki trash delete` | `wiki_trash_delete` | delete | Trash |
| `foxos wiki settings show` | `wiki_settings_show` | read | Settings |
| `foxos wiki powered-by-puter show` | `wiki_powered-by-puter_show` | read | Powered by Puter |
| `foxos wiki sidebar resize` | `wiki_sidebar_resize` | modify | Resize sidebar |
| `foxos wiki getting-started-2 activate` | `wiki_getting-started-2_activate` | modify | Getting started |
| `foxos wiki share share` | `wiki_share_share` | modify | Share |
| `foxos wiki comments activate` | `wiki_comments_activate` | modify | Comments |
| `foxos wiki favorites create` | `wiki_favorites_create` | modify | Add to favorites |
| `foxos wiki page-options activate` | `wiki_page-options_activate` | modify | Page options |
| `foxos wiki page-icon update` | `wiki_page-icon_update` | modify | Change page icon |
| `foxos wiki cover create` | `wiki_cover_create` | modify | Add cover |
| `foxos wiki getting-started set VALUE [--submit]` | `wiki_getting-started_set` | modify | Getting started |
| `foxos wiki callout-icon update` | `wiki_callout-icon_update` | modify | Change callout icon |
| `foxos wiki callout set VALUE [--submit]` | `wiki_callout_set` | modify | Callout |
| `foxos wiki text set VALUE [--submit]` | `wiki_text_set` | modify | Text |
| `foxos wiki bulleted-list set VALUE [--submit]` | `wiki_bulleted-list_set` | modify | Bulleted list |
| `foxos wiki done toggle` | `wiki_done_toggle` | modify | Done |
| `foxos wiki to-do-list set VALUE [--submit]` | `wiki_to-do-list_set` | modify | To-do list |
| `foxos wiki content hide` | `wiki_content_hide` | read | Hide content |
| `foxos wiki toggle-list set VALUE [--submit]` | `wiki_toggle-list_set` | modify | Toggle list |
| `foxos wiki quote set VALUE [--submit]` | `wiki_quote_set` | modify | Quote |
| `foxos wiki theme activate` | `wiki_theme_activate` | modify | Theme |
| `foxos wiki lolocals-wiki-settings show` | `wiki_lolocals-wiki-settings_show` | read | Settings |
| `foxos wiki keyboard-shortcutsctrl activate` | `wiki_keyboard-shortcutsctrl_activate` | modify | Keyboard shortcutsCtrl+/ |
| `foxos wiki close close` | `wiki_close_close` | read | Close |
| `foxos wiki system toggle` | `wiki_system_toggle` | modify | System |
| `foxos wiki light toggle` | `wiki_light_toggle` | modify | Light |
| `foxos wiki dark toggle` | `wiki_dark_toggle` | modify | Dark |
| `foxos wiki settings-powered-by-puter show` | `wiki_settings-powered-by-puter_show` | read | Powered by Puter |
| `foxos wiki page share` | `wiki_page_share` | modify | Share this page |
| `foxos wiki page-options-favorites create` | `wiki_page-options-favorites_create` | modify | Add to favorites |
| `foxos wiki link copy` | `wiki_link_copy` | modify | Copy link |
| `foxos wiki duplicate duplicate` | `wiki_duplicate_duplicate` | modify | Duplicate |
| `foxos wiki move move` | `wiki_move_move` | modify | Move to |
| `foxos wiki page lock` | `wiki_page_lock` | modify | Lock page |
| `foxos wiki export export` | `wiki_export_export` | modify | Export |
| `foxos wiki page-history activate` | `wiki_page-history_activate` | modify | Page history |
| `foxos wiki trash move` | `wiki_trash_move` | modify | Move to trash |
| `foxos wiki selection select-all` | `wiki_selection_select-all` | modify | 快捷键 mod+a |
| `foxos wiki selection copy` | `wiki_selection_copy` | modify | 快捷键 mod+c |
| `foxos wiki selection duplicate` | `wiki_selection_duplicate` | modify | 快捷键 mod+d |
| `foxos wiki command-palette show` | `wiki_command-palette_show` | read | 快捷键 mod+k |
| `foxos wiki selection lock-shift` | `wiki_selection_lock-shift` | modify | 快捷键 mod+shift+l |
| `foxos wiki edit undo` | `wiki_edit_undo` | modify | 快捷键 mod+z |

### time-tracking（`time-tracking`，71 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos time-tracking skip dismiss TARGET` | `time-tracking_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos time-tracking nov-9-nov-15-0m-across-0-days select TARGET` | `time-tracking_nov-9-nov-15-0m-across-0-days_select` | read | #（7 项，如 Mon） |
| `foxos time-tracking log-time select TARGET` | `time-tracking_log-time_select` | read | log time on #（5 项，如 Log time on Wednesday, Nov 11） |
| `foxos time-tracking printable-timesheet select TARGET` | `time-tracking_printable-timesheet_select` | read | a printable timesheet for *（1 项，如 A printable timesheet for this range） |
| `foxos time-tracking backup-from export TARGET` | `time-tracking_backup-from_export` | modify | download the backup from #（1 项，如 Download the backup from Nov 10, 2026） |
| `foxos time-tracking restore-backup-from select TARGET` | `time-tracking_restore-backup-from_select` | read | restore the backup from #（1 项，如 Restore the backup from Nov 10, 2026） |
| `foxos time-tracking csvevery-entry-ready export TARGET` | `time-tracking_csvevery-entry-ready_export` | modify | export csvevery entry, ready for *（1 项，如 Export CSVEvery entry, ready for invoicing or a spreadsheet） |
| `foxos time-tracking content dismiss` | `time-tracking_content_dismiss` | read | Skip to content |
| `foxos time-tracking timer show` | `time-tracking_timer_show` | read | Timer |
| `foxos time-tracking timesheet show` | `time-tracking_timesheet_show` | read | Timesheet |
| `foxos time-tracking reports show` | `time-tracking_reports_show` | read | Reports |
| `foxos time-tracking projects show` | `time-tracking_projects_show` | read | Projects |
| `foxos time-tracking settings show` | `time-tracking_settings_show` | read | Settings |
| `foxos time-tracking log-time activate` | `time-tracking_log-time_activate` | modify | Log time |
| `foxos time-tracking client create` | `time-tracking_client_create` | modify | Add a client |
| `foxos time-tracking close close` | `time-tracking_close_close` | read | Close |
| `foxos time-tracking set-up-tracking activate` | `time-tracking_set-up-tracking_activate` | modify | Set up tracking |
| `foxos time-tracking explore-sample-data activate` | `time-tracking_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos time-tracking jump-date activate` | `time-tracking_jump-date_activate` | modify | Jump to a date |
| `foxos time-tracking entries search` | `time-tracking_entries_search` | read | Search entries |
| `foxos time-tracking week activate` | `time-tracking_week_activate` | modify | Week |
| `foxos time-tracking grid activate` | `time-tracking_grid_activate` | modify | Grid |
| `foxos time-tracking month activate` | `time-tracking_month_activate` | modify | Month |
| `foxos time-tracking week previous` | `time-tracking_week_previous` | read | Previous week |
| `foxos time-tracking today activate` | `time-tracking_today_activate` | modify | Today |
| `foxos time-tracking week next` | `time-tracking_week_next` | read | Next week |
| `foxos time-tracking log-time-yesterday activate` | `time-tracking_log-time-yesterday_activate` | modify | Log time on Yesterday |
| `foxos time-tracking log-time-today activate` | `time-tracking_log-time-today_activate` | modify | Log time on Today |
| `foxos time-tracking invoice-ready-summary-report print` | `time-tracking_invoice-ready-summary-report_print` | read | Print an invoice-ready summary of this report |
| `foxos time-tracking csv export` | `time-tracking_csv_export` | modify | Export CSV |
| `foxos time-tracking report activate` | `time-tracking_report_activate` | modify | Report |
| `foxos time-tracking insights activate` | `time-tracking_insights_activate` | modify | Insights |
| `foxos time-tracking invoices activate` | `time-tracking_invoices_activate` | modify | Invoices |
| `foxos time-tracking reports-week activate` | `time-tracking_reports-week_activate` | modify | This week |
| `foxos time-tracking last-week activate` | `time-tracking_last-week_activate` | modify | Last week |
| `foxos time-tracking reports-month activate` | `time-tracking_reports-month_activate` | modify | This month |
| `foxos time-tracking last-month activate` | `time-tracking_last-month_activate` | modify | Last month |
| `foxos time-tracking custom activate` | `time-tracking_custom_activate` | modify | Custom |
| `foxos time-tracking client activate` | `time-tracking_client_activate` | modify | Client |
| `foxos time-tracking project activate` | `time-tracking_project_activate` | modify | Project |
| `foxos time-tracking task activate` | `time-tracking_task_activate` | modify | Task |
| `foxos time-tracking unbilled activate` | `time-tracking_unbilled_activate` | modify | Unbilled |
| `foxos time-tracking invoiced activate` | `time-tracking_invoiced_activate` | modify | Invoiced |
| `foxos time-tracking projects-client create` | `time-tracking_projects-client_create` | modify | New client |
| `foxos time-tracking first-client create` | `time-tracking_first-client_create` | modify | Add your first client |
| `foxos time-tracking light activate` | `time-tracking_light_activate` | modify | Light |
| `foxos time-tracking dark activate` | `time-tracking_dark_activate` | modify | Dark |
| `foxos time-tracking system activate` | `time-tracking_system_activate` | modify | System |
| `foxos time-tracking currency set VALUE [--submit]` | `time-tracking_currency_set` | modify | Currency |
| `foxos time-tracking default-hourly-rate set VALUE [--submit]` | `time-tracking_default-hourly-rate_set` | modify | Default hourly rate |
| `foxos time-tracking default-rate-applies-from set VALUE [--submit]` | `time-tracking_default-rate-applies-from_set` | modify | Default rate applies from |
| `foxos time-tracking round-billable-time set VALUE [--submit]` | `time-tracking_round-billable-time_set` | modify | Round billable time |
| `foxos time-tracking week-starts set VALUE [--submit]` | `time-tracking_week-starts_set` | modify | Week starts on |
| `foxos time-tracking weekly-target-hours set VALUE [--submit]` | `time-tracking_weekly-target-hours_set` | modify | Weekly target (hours) |
| `foxos time-tracking target-counts set VALUE [--submit]` | `time-tracking_target-counts_set` | modify | Target counts |
| `foxos time-tracking business-name set VALUE [--submit]` | `time-tracking_business-name_set` | modify | Business name |
| `foxos time-tracking address set VALUE [--submit]` | `time-tracking_address_set` | modify | Address |
| `foxos time-tracking tax-vat-id set VALUE [--submit]` | `time-tracking_tax-vat-id_set` | modify | Tax / VAT ID |
| `foxos time-tracking default-tax-rate set VALUE [--submit]` | `time-tracking_default-tax-rate_set` | modify | Default tax rate (%) |
| `foxos time-tracking payment-terms set VALUE [--submit]` | `time-tracking_payment-terms_set` | modify | Payment terms |
| `foxos time-tracking terms-line set VALUE [--submit]` | `time-tracking_terms-line_set` | modify | Terms line |
| `foxos time-tracking how-pay set VALUE [--submit]` | `time-tracking_how-pay_set` | modify | How to pay |
| `foxos time-tracking logo import` | `time-tracking_logo_import` | modify | Upload logo |
| `foxos time-tracking long-timer-warning set VALUE [--submit]` | `time-tracking_long-timer-warning_set` | modify | Long timer warning |
| `foxos time-tracking away-sleep-gaps set VALUE [--submit]` | `time-tracking_away-sleep-gaps_set` | modify | Away and sleep gaps |
| `foxos time-tracking daily-tracking-nudge set VALUE [--submit]` | `time-tracking_daily-tracking-nudge_set` | modify | Daily tracking nudge |
| `foxos time-tracking unbilled-time-reminder set VALUE [--submit]` | `time-tracking_unbilled-time-reminder_set` | modify | Unbilled time reminder |
| `foxos time-tracking counts-as-aging set VALUE [--submit]` | `time-tracking_counts-as-aging_set` | modify | Counts as aging |
| `foxos time-tracking system-notifications toggle` | `time-tracking_system-notifications_toggle` | modify | System notifications |
| `foxos time-tracking automatic-backups set VALUE [--submit]` | `time-tracking_automatic-backups_set` | modify | Automatic backups |
| `foxos time-tracking puter show` | `time-tracking_puter_show` | read | Puter |

### survey（`survey`，28 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos survey folders select TARGET` | `survey_folders_select` | read | all #（1 项，如 All surveys0） |
| `foxos survey describe-survey select TARGET` | `survey_describe-survey_select` | read | describe your survey for *（1 项，如 Describe your survey for AI） |
| `foxos survey content dismiss` | `survey_content_dismiss` | read | Skip to content |
| `foxos survey surveys-home show` | `survey_surveys-home_show` | read | Surveys home |
| `foxos survey source-code-github-opens-tab show` | `survey_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos survey account-settings activate` | `survey_account-settings_activate` | modify | Account and settings |
| `foxos survey folder create` | `survey_folder_create` | modify | New folder |
| `foxos survey source-github open` | `survey_source-github_open` | read | Open source on GitHub |
| `foxos survey powered-by-puter show` | `survey_powered-by-puter_show` | read | Powered by Puter |
| `foxos survey survey create` | `survey_survey_create` | modify | Create survey |
| `foxos survey from-scratcha-blank-survey start` | `survey_from-scratcha-blank-survey_start` | modify | Start from scratchA blank survey |
| `foxos survey use-templateready-made-fully-editable activate` | `survey_use-templateready-made-fully-editable_activate` | modify | Use a templateReady-made, fully editable |
| `foxos survey questionspaste-list-or-open-file import` | `survey_questionspaste-list-or-open-file_import` | modify | Import questionsPaste a list or open a file |
| `foxos survey generate run` | `survey_generate_run` | modify | Generate |
| `foxos survey search-surveys set VALUE [--submit]` | `survey_search-surveys_set` | modify | Search surveys |
| `foxos survey filter-by-status set VALUE [--submit]` | `survey_filter-by-status_set` | modify | Filter by status |
| `foxos survey sort-by set VALUE [--submit]` | `survey_sort-by_set` | modify | Sort by |
| `foxos survey survey-2 create` | `survey_survey-2_create` | modify | Create a survey |
| `foxos survey it dismiss` | `survey_it_dismiss` | read | Got it |
| `foxos survey system activate` | `survey_system_activate` | modify | System |
| `foxos survey light activate` | `survey_light_activate` | modify | Light |
| `foxos survey dark activate` | `survey_dark_activate` | modify | Dark |
| `foxos survey keyboard-shortcuts activate` | `survey_keyboard-shortcuts_activate` | modify | Keyboard shortcuts? |
| `foxos survey surveys show` | `survey_surveys_show` | read | About Surveys |
| `foxos survey from-scratch start` | `survey_from-scratch_start` | modify | Start from scratch |
| `foxos survey use-template activate` | `survey_use-template_activate` | modify | Use a template |
| `foxos survey ai run` | `survey_ai_run` | modify | Generate with AI |
| `foxos survey questions import` | `survey_questions_import` | modify | Import questions |

### accounting（`accounting`，45 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos accounting account-menu select TARGET` | `accounting_account-menu_select` | read | account menu for *（1 项，如 Account menu for local） |
| `foxos accounting company-name select TARGET` | `accounting_company-name_select` | read | company name *（1 项，如 Company name *） |
| `foxos accounting content dismiss` | `accounting_content_dismiss` | read | Skip to content |
| `foxos accounting home show` | `accounting_home_show` | read | Home |
| `foxos accounting create create` | `accounting_create_create` | modify | Create |
| `foxos accounting home-2 show` | `accounting_home-2_show` | read | Home |
| `foxos accounting banking show` | `accounting_banking_show` | read | Banking |
| `foxos accounting sales show` | `accounting_sales_show` | read | Sales |
| `foxos accounting purchases show` | `accounting_purchases_show` | read | Purchases |
| `foxos accounting reports show` | `accounting_reports_show` | read | Reports |
| `foxos accounting menu show` | `accounting_menu_show` | read | Menu |
| `foxos accounting settings show` | `accounting_settings_show` | read | Settings |
| `foxos accounting navigation open` | `accounting_navigation_open` | read | Open navigation |
| `foxos accounting search set VALUE [--submit]` | `accounting_search_set` | modify | Search |
| `foxos accounting keyboard-shortcuts activate` | `accounting_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos accounting settings-2 show` | `accounting_settings-2_show` | read | Settings |
| `foxos accounting panel collapse` | `accounting_panel_collapse` | read | Collapse panel |
| `foxos accounting accounting activate` | `accounting_accounting_activate` | modify | Accounting |
| `foxos accounting purchases activate` | `accounting_purchases_activate` | modify | Purchases |
| `foxos accounting sales activate` | `accounting_sales_activate` | modify | Sales |
| `foxos accounting sales-tax activate` | `accounting_sales-tax_activate` | modify | Sales Tax |
| `foxos accounting reports activate` | `accounting_reports_activate` | modify | Reports |
| `foxos accounting puter show` | `accounting_puter_show` | read | Puter |
| `foxos accounting privacy activate` | `accounting_privacy_activate` | modify | Privacy |
| `foxos accounting invoice create` | `accounting_invoice_create` | modify | Create invoice |
| `foxos accounting payment record` | `accounting_payment_record` | modify | Record payment |
| `foxos accounting expense record` | `accounting_expense_record` | modify | Record expense |
| `foxos accounting enter-bill activate` | `accounting_enter-bill_activate` | modify | Enter bill |
| `foxos accounting pay-bills activate` | `accounting_pay-bills_activate` | modify | Pay bills |
| `foxos accounting deposit record` | `accounting_deposit_record` | modify | Record deposit |
| `foxos accounting write-check activate` | `accounting_write-check_activate` | modify | Write check |
| `foxos accounting bank-statement import` | `accounting_bank-statement_import` | modify | Upload bank statement |
| `foxos accounting period set VALUE [--submit]` | `accounting_period_set` | modify | Period |
| `foxos accounting report show` | `accounting_report_show` | read | View report |
| `foxos accounting overdue show` | `accounting_overdue_show` | read | Overdue |
| `foxos accounting not-due-yet show` | `accounting_not-due-yet_show` | read | Not due yet |
| `foxos accounting paid show` | `accounting_paid_show` | read | Paid |
| `foxos accounting go-banking show` | `accounting_go-banking_show` | read | Go to banking |
| `foxos accounting as-table show` | `accounting_as-table_show` | read | View as table |
| `foxos accounting close close` | `accounting_close_close` | read | Close |
| `foxos accounting home-currency set VALUE [--submit]` | `accounting_home-currency_set` | modify | Home currency |
| `foxos accounting fiscal-year-starts set VALUE [--submit]` | `accounting_fiscal-year-starts_set` | modify | Fiscal year starts in |
| `foxos accounting date-format set VALUE [--submit]` | `accounting_date-format_set` | modify | Date format |
| `foxos accounting start-sample-company-explore toggle` | `accounting_start-sample-company-explore_toggle` | modify | Start with a sample company to explore |
| `foxos accounting books create` | `accounting_books_create` | modify | Create my books |

### invoicing（`invoicing`，20 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos invoicing skip dismiss TARGET` | `invoicing_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos invoicing content dismiss` | `invoicing_content_dismiss` | read | Skip to content |
| `foxos invoicing switch-dark-theme activate` | `invoicing_switch-dark-theme_activate` | modify | Switch to dark theme |
| `foxos invoicing home show` | `invoicing_home_show` | read | Home |
| `foxos invoicing invoices show` | `invoicing_invoices_show` | read | Invoices |
| `foxos invoicing estimates show` | `invoicing_estimates_show` | read | Estimates |
| `foxos invoicing recurring show` | `invoicing_recurring_show` | read | Recurring |
| `foxos invoicing clients show` | `invoicing_clients_show` | read | Clients |
| `foxos invoicing receipts show` | `invoicing_receipts_show` | read | Receipts |
| `foxos invoicing saved-items show` | `invoicing_saved-items_show` | read | Saved items |
| `foxos invoicing reports show` | `invoicing_reports_show` | read | Reports |
| `foxos invoicing trash delete` | `invoicing_trash_delete` | delete | Trash |
| `foxos invoicing invoice create` | `invoicing_invoice_create` | modify | New invoice |
| `foxos invoicing estimate create` | `invoicing_estimate_create` | modify | New estimate |
| `foxos invoicing settings show` | `invoicing_settings_show` | read | Settings |
| `foxos invoicing invoice-2 create` | `invoicing_invoice-2_create` | modify | New invoice |
| `foxos invoicing estimate-2 create` | `invoicing_estimate-2_create` | modify | New estimate |
| `foxos invoicing close close` | `invoicing_close_close` | read | Close |
| `foxos invoicing set-up-business activate` | `invoicing_set-up-business_activate` | modify | Set up my business |
| `foxos invoicing explore-sample-data activate` | `invoicing_explore-sample-data_activate` | modify | Explore with sample data |

### expense（`expense`，17 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos expense month-nothing-last-month select TARGET` | `expense_month-nothing-last-month_select` | read | this month$# nothing last month（1 项，如 This month$0.00vs. nothing last month） |
| `foxos expense not-report-expenses select TARGET` | `expense_not-report-expenses_select` | read | not in a report$# expenses（1 项，如 Not in a report$0.000 expenses） |
| `foxos expense awaiting-reimbursement-expenses-flight select TARGET` | `expense_awaiting-reimbursement-expenses-flight_select` | read | awaiting reimbursement$# expenses in flight（1 项，如 Awaiting reimbursement$0.000 expenses in flight） |
| `foxos expense lines-open select TARGET` | `expense_lines-open_select` | read | to # lines open（1 项，如 To reconcile0statement lines open） |
| `foxos expense skip dismiss TARGET` | `expense_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos expense content dismiss` | `expense_content_dismiss` | read | Skip to content |
| `foxos expense home show` | `expense_home_show` | read | Home |
| `foxos expense expenses show` | `expense_expenses_show` | read | Expenses |
| `foxos expense reports show` | `expense_reports_show` | read | Reports |
| `foxos expense reconcile show` | `expense_reconcile_show` | read | Reconcile |
| `foxos expense settings show` | `expense_settings_show` | read | Settings |
| `foxos expense capture-receipt activate` | `expense_capture-receipt_activate` | modify | Capture receipt |
| `foxos expense manual-entry activate` | `expense_manual-entry_activate` | modify | Manual entry |
| `foxos expense capture-receipt-2 activate` | `expense_capture-receipt-2_activate` | modify | Capture receipt |
| `foxos expense close close` | `expense_close_close` | read | Close |
| `foxos expense set-up-expenses activate` | `expense_set-up-expenses_activate` | modify | Set up my expenses |
| `foxos expense explore-sample-data activate` | `expense_explore-sample-data_activate` | modify | Explore with sample data |

### cap-table（`cap-table`，27 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos cap-table skip dismiss TARGET` | `cap-table_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos cap-table main-content dismiss` | `cap-table_main-content_dismiss` | read | Skip to main content |
| `foxos cap-table searchctrl-k activate` | `cap-table_searchctrl-k_activate` | modify | SearchCtrl K |
| `foxos cap-table home activate` | `cap-table_home_activate` | modify | Home |
| `foxos cap-table cap-table activate` | `cap-table_cap-table_activate` | modify | Cap table |
| `foxos cap-table securities activate` | `cap-table_securities_activate` | modify | Securities |
| `foxos cap-table stakeholders activate` | `cap-table_stakeholders_activate` | modify | Stakeholders |
| `foxos cap-table classes share` | `cap-table_classes_share` | modify | Share classes |
| `foxos cap-table round-modeling activate` | `cap-table_round-modeling_activate` | modify | Round modeling |
| `foxos cap-table exit-scenarios activate` | `cap-table_exit-scenarios_activate` | modify | Exit scenarios |
| `foxos cap-table needs-attention activate` | `cap-table_needs-attention_activate` | modify | Needs attention |
| `foxos cap-table reports activate` | `cap-table_reports_activate` | modify | Reports |
| `foxos cap-table history activate` | `cap-table_history_activate` | modify | History |
| `foxos cap-table settings show` | `cap-table_settings_show` | read | Settings |
| `foxos cap-table issue-security activate` | `cap-table_issue-security_activate` | modify | Issue security |
| `foxos cap-table issue-security-2 activate` | `cap-table_issue-security-2_activate` | modify | Issue security |
| `foxos cap-table by-class activate` | `cap-table_by-class_activate` | modify | By class |
| `foxos cap-table by-holder activate` | `cap-table_by-holder_activate` | modify | By holder |
| `foxos cap-table cap-table open` | `cap-table_cap-table_open` | read | Open cap table |
| `foxos cap-table set-up-company-profile-do activate` | `cap-table_set-up-company-profile-do_activate` | modify | Set up your company profile, to do |
| `foxos cap-table share-class-do create` | `cap-table_share-class-do_create` | modify | Create a share class, to do |
| `foxos cap-table issue-founder-shares-do activate` | `cap-table_issue-founder-shares-do_activate` | modify | Issue founder shares, to do |
| `foxos cap-table adopt-equity-plan-reserve-shares-do activate` | `cap-table_adopt-equity-plan-reserve-shares-do_activate` | modify | Adopt an equity plan and reserve shares, to do |
| `foxos cap-table grant-options-or-add-safe-do activate` | `cap-table_grant-options-or-add-safe-do_activate` | modify | Grant options or add a SAFE, to do |
| `foxos cap-table close close` | `cap-table_close_close` | read | Close |
| `foxos cap-table set-up-company activate` | `cap-table_set-up-company_activate` | modify | Set up my company |
| `foxos cap-table explore-sample-data activate` | `cap-table_explore-sample-data_activate` | modify | Explore with sample data |

### crm（`crm`，16 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos crm skip dismiss TARGET` | `crm_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos crm searchctrl-k activate` | `crm_searchctrl-k_activate` | modify | SearchCtrl K |
| `foxos crm home show` | `crm_home_show` | read | Home |
| `foxos crm pipeline show` | `crm_pipeline_show` | read | Pipeline |
| `foxos crm leads show` | `crm_leads_show` | read | Leads |
| `foxos crm follow-ups show` | `crm_follow-ups_show` | read | Follow-ups |
| `foxos crm companies show` | `crm_companies_show` | read | Companies |
| `foxos crm activity show` | `crm_activity_show` | read | Activity |
| `foxos crm forecast show` | `crm_forecast_show` | read | Forecast |
| `foxos crm settings show` | `crm_settings_show` | read | Settings |
| `foxos crm lead create` | `crm_lead_create` | modify | Add a lead |
| `foxos crm me-around show` | `crm_me-around_show` | read | Show me around |
| `foxos crm close close` | `crm_close_close` | read | Close |
| `foxos crm set-up-pipeline activate` | `crm_set-up-pipeline_activate` | modify | Set up my pipeline |
| `foxos crm explore-sample-data activate` | `crm_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos crm command-palette show` | `crm_command-palette_show` | read | 快捷键 mod+k |

### help-desk（`help-desk`，6 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos help-desk help-desk-name set VALUE [--submit]` | `help-desk_help-desk-name_set` | modify | Help desk name |
| `foxos help-desk name set VALUE [--submit]` | `help-desk_name_set` | modify | Your name |
| `foxos help-desk help-desk create` | `help-desk_help-desk_create` | modify | Create help desk |
| `foxos help-desk source-code show` | `help-desk_source-code_show` | read | Source code |
| `foxos help-desk puter show` | `help-desk_puter_show` | read | Puter |
| `foxos help-desk dismiss dismiss` | `help-desk_dismiss_dismiss` | read | Dismiss |

### contracts（`contracts`，14 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos contracts skip dismiss TARGET` | `contracts_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos contracts content dismiss` | `contracts_content_dismiss` | read | Skip to content |
| `foxos contracts home show` | `contracts_home_show` | read | Home |
| `foxos contracts contracts show` | `contracts_contracts_show` | read | Contracts |
| `foxos contracts renewals show` | `contracts_renewals_show` | read | Renewals |
| `foxos contracts obligations show` | `contracts_obligations_show` | read | Obligations |
| `foxos contracts contacts show` | `contracts_contacts_show` | read | Contacts |
| `foxos contracts settings show` | `contracts_settings_show` | read | Settings |
| `foxos contracts contract create` | `contracts_contract_create` | modify | New contract |
| `foxos contracts contract-2 create` | `contracts_contract-2_create` | modify | New contract |
| `foxos contracts contract-3 create` | `contracts_contract-3_create` | modify | Add a contract |
| `foxos contracts close close` | `contracts_close_close` | read | Close |
| `foxos contracts first-contract create` | `contracts_first-contract_create` | modify | Add my first contract |
| `foxos contracts explore-sample-data activate` | `contracts_explore-sample-data_activate` | modify | Explore with sample data |

### pos（`pos`，17 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos pos skip dismiss TARGET` | `pos_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos pos register show` | `pos_register_show` | read | Register |
| `foxos pos products show` | `pos_products_show` | read | Products |
| `foxos pos receipts show` | `pos_receipts_show` | read | Receipts |
| `foxos pos customers show` | `pos_customers_show` | read | Customers |
| `foxos pos reports show` | `pos_reports_show` | read | Reports |
| `foxos pos settings show` | `pos_settings_show` | read | Settings |
| `foxos pos search-products-or-scan-barcode set VALUE [--submit]` | `pos_search-products-or-scan-barcode_set` | modify | Search products or scan a barcode |
| `foxos pos cash-drawer activate` | `pos_cash-drawer_activate` | modify | Cash drawer |
| `foxos pos products create` | `pos_products_create` | modify | Add products |
| `foxos pos custom-item create` | `pos_custom-item_create` | modify | Add a custom item |
| `foxos pos park-sale-serve-next-customer activate` | `pos_park-sale-serve-next-customer_activate` | modify | Park this sale and serve the next customer |
| `foxos pos clear clear` | `pos_clear_clear` | modify | Clear |
| `foxos pos charge activate` | `pos_charge_activate` | modify | Charge |
| `foxos pos close close` | `pos_close_close` | read | Close |
| `foxos pos set-up-store activate` | `pos_set-up-store_activate` | modify | Set up my store |
| `foxos pos explore-sample-data activate` | `pos_explore-sample-data_activate` | modify | Explore with sample data |

### inventory（`inventory`，17 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos inventory skip dismiss TARGET` | `inventory_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos inventory searchctrl-k activate` | `inventory_searchctrl-k_activate` | modify | SearchCtrl K |
| `foxos inventory overview show` | `inventory_overview_show` | read | Overview |
| `foxos inventory products show` | `inventory_products_show` | read | Products |
| `foxos inventory take-out show` | `inventory_take-out_show` | read | Take out |
| `foxos inventory reorder show` | `inventory_reorder_show` | read | Reorder |
| `foxos inventory stocktake show` | `inventory_stocktake_show` | read | Stocktake |
| `foxos inventory history show` | `inventory_history_show` | read | History |
| `foxos inventory reports show` | `inventory_reports_show` | read | Reports |
| `foxos inventory locations show` | `inventory_locations_show` | read | Locations |
| `foxos inventory suppliers show` | `inventory_suppliers_show` | read | Suppliers |
| `foxos inventory settings show` | `inventory_settings_show` | read | Settings |
| `foxos inventory product create` | `inventory_product_create` | modify | New product |
| `foxos inventory close close` | `inventory_close_close` | read | Close |
| `foxos inventory set-up-inventory activate` | `inventory_set-up-inventory_activate` | modify | Set up my inventory |
| `foxos inventory explore-sample-data activate` | `inventory_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos inventory command-palette show` | `inventory_command-palette_show` | read | 快捷键 mod+k |

### assets（`assets`，0 个语义命令）

（尚无语义命令：应用未安装或清单未生成，可用上面的通用命令操作。）

### hiring（`hiring`，22 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos hiring yet open TARGET` | `hiring_yet_open` | read | open # yet（1 项，如 Open jobs0None yet） |
| `foxos hiring candidates-not-yet-hired select TARGET` | `hiring_candidates-not-yet-hired_select` | read | candidates in #, not yet hired（1 项，如 Candidates in play0Active, not yet hired） |
| `foxos hiring interviews-today select TARGET` | `hiring_interviews-today_select` | read | interviews · # today（1 项，如 Interviews · 7 days0Nothing today） |
| `foxos hiring offers-signature select TARGET` | `hiring_offers-signature_select` | read | offers # signature（1 项，如 Offers out0Awaiting signature） |
| `foxos hiring main select TARGET` | `hiring_main_select` | read | #（5 项，如 Applied0） |
| `foxos hiring skip dismiss TARGET` | `hiring_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos hiring searchctrl-k activate` | `hiring_searchctrl-k_activate` | modify | SearchCtrl K |
| `foxos hiring overview activate` | `hiring_overview_activate` | modify | Overview |
| `foxos hiring jobs activate` | `hiring_jobs_activate` | modify | Jobs |
| `foxos hiring pipeline activate` | `hiring_pipeline_activate` | modify | Pipeline |
| `foxos hiring interviews activate` | `hiring_interviews_activate` | modify | Interviews |
| `foxos hiring offers activate` | `hiring_offers_activate` | modify | Offers |
| `foxos hiring onboarding activate` | `hiring_onboarding_activate` | modify | Onboarding |
| `foxos hiring reports activate` | `hiring_reports_activate` | modify | Reports |
| `foxos hiring settings show` | `hiring_settings_show` | read | Settings |
| `foxos hiring theme activate` | `hiring_theme_activate` | modify | Theme |
| `foxos hiring puter show` | `hiring_puter_show` | read | Puter |
| `foxos hiring reports-2 activate` | `hiring_reports-2_activate` | modify | Reports |
| `foxos hiring close close` | `hiring_close_close` | read | Close |
| `foxos hiring set-up-hiring activate` | `hiring_set-up-hiring_activate` | modify | Set up my hiring |
| `foxos hiring explore-sample-data activate` | `hiring_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos hiring command-palette show` | `hiring_command-palette_show` | read | 快捷键 mod+k |

### shifts（`shifts`，17 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos shifts theme select TARGET` | `shifts_theme_select` | read | theme: *（1 项，如 Theme: System） |
| `foxos shifts skip dismiss TARGET` | `shifts_skip_dismiss` | read | skip for *（1 项，如 Skip for now） |
| `foxos shifts home activate` | `shifts_home_activate` | modify | Home |
| `foxos shifts schedule schedule` | `shifts_schedule_schedule` | modify | Schedule |
| `foxos shifts team activate` | `shifts_team_activate` | modify | Team |
| `foxos shifts availability activate` | `shifts_availability_activate` | modify | Availability |
| `foxos shifts swaps activate` | `shifts_swaps_activate` | modify | Swaps |
| `foxos shifts attendance activate` | `shifts_attendance_activate` | modify | Attendance |
| `foxos shifts reports activate` | `shifts_reports_activate` | modify | Reports |
| `foxos shifts backup-restore activate` | `shifts_backup-restore_activate` | modify | Backup & restore |
| `foxos shifts out sign` | `shifts_out_sign` | modify | Sign out |
| `foxos shifts puter show` | `shifts_puter_show` | read | Puter |
| `foxos shifts employee create` | `shifts_employee_create` | modify | Add employee |
| `foxos shifts sample-data import` | `shifts_sample-data_import` | modify | Load sample data |
| `foxos shifts close close` | `shifts_close_close` | read | Close |
| `foxos shifts set-up-team activate` | `shifts_set-up-team_activate` | modify | Set up my team |
| `foxos shifts explore-sample-data activate` | `shifts_explore-sample-data_activate` | modify | Explore with sample data |

### childcare（`childcare`，39 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos childcare children-enrolled select TARGET` | `childcare_children-enrolled_select` | read | children # enrolled（1 项，如 Children here0of 0 enrolled） |
| `foxos childcare absent-reported select TARGET` | `childcare_absent-reported_select` | read | absent # reported（1 项，如 Absent today0Nobody reported） |
| `foxos childcare staff-staff-members select TARGET` | `childcare_staff-staff-members_select` | read | staff on # staff members（1 项，如 Staff on site00 staff members） |
| `foxos childcare ratio-rooms-ratio select TARGET` | `childcare_ratio-rooms-ratio_select` | read | ratio # rooms in ratio（1 项，如 Ratio alerts0All rooms in ratio） |
| `foxos childcare content dismiss` | `childcare_content_dismiss` | read | Skip to content |
| `foxos childcare log-or-add-n activate` | `childcare_log-or-add-n_activate` | modify | Log or add (N) |
| `foxos childcare home show` | `childcare_home_show` | read | Home |
| `foxos childcare check-in show` | `childcare_check-in_show` | read | Check-in |
| `foxos childcare activities show` | `childcare_activities_show` | read | Activities |
| `foxos childcare messages show` | `childcare_messages_show` | read | Messages |
| `foxos childcare children show` | `childcare_children_show` | read | Children |
| `foxos childcare families show` | `childcare_families_show` | read | Families |
| `foxos childcare rooms show` | `childcare_rooms_show` | read | Rooms |
| `foxos childcare staff show` | `childcare_staff_show` | read | Staff |
| `foxos childcare calendar show` | `childcare_calendar_show` | read | Calendar |
| `foxos childcare menus show` | `childcare_menus_show` | read | Menus |
| `foxos childcare billing show` | `childcare_billing_show` | read | Billing |
| `foxos childcare reports show` | `childcare_reports_show` | read | Reports |
| `foxos childcare source-code-github-opens-tab show` | `childcare_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos childcare puter show` | `childcare_puter_show` | read | Puter |
| `foxos childcare navigation collapse` | `childcare_navigation_collapse` | read | Collapse navigation |
| `foxos childcare search search` | `childcare_search_search` | read | Search |
| `foxos childcare keyboard-shortcuts activate` | `childcare_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos childcare settings show` | `childcare_settings_show` | read | Settings |
| `foxos childcare account-appearance activate` | `childcare_account-appearance_activate` | modify | Account and appearance |
| `foxos childcare kiosk show` | `childcare_kiosk_show` | read | Kiosk |
| `foxos childcare check run` | `childcare_check_run` | modify | Check in |
| `foxos childcare log-activity activate` | `childcare_log-activity_activate` | modify | Log activity |
| `foxos childcare room create` | `childcare_room_create` | modify | Add a room |
| `foxos childcare log open` | `childcare_log_open` | read | Open log |
| `foxos childcare log-activity-2 activate` | `childcare_log-activity-2_activate` | modify | Log an activity |
| `foxos childcare calendar-2 show` | `childcare_calendar-2_show` | read | Calendar |
| `foxos childcare it dismiss` | `childcare_it_dismiss` | read | Got it |
| `foxos childcare close close` | `childcare_close_close` | read | Close |
| `foxos childcare school-name set VALUE [--submit]` | `childcare_school-name_set` | modify | School name |
| `foxos childcare rooms set VALUE [--submit]` | `childcare_rooms_set` | modify | Rooms |
| `foxos childcare use-sample-data activate` | `childcare_use-sample-data_activate` | modify | Use sample data |
| `foxos childcare get-started activate` | `childcare_get-started_activate` | modify | Get started |
| `foxos childcare command-palette show` | `childcare_command-palette_show` | read | 快捷键 mod+k |

### field-service（`field-service`，40 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos field-service workflow select TARGET` | `field-service_workflow_select` | read | #（3 项，如 Requests0NewAssessments today0） |
| `foxos field-service paymentowed-you select TARGET` | `field-service_paymentowed-you_select` | read | # paymentowed to you$#（1 项，如 Invoices0Awaiting paymentOwed to you$0.00Drafts0） |
| `foxos field-service content dismiss` | `field-service_content_dismiss` | read | Skip to content |
| `foxos field-service n create` | `field-service_n_create` | modify | Create (N) |
| `foxos field-service home show` | `field-service_home_show` | read | Home |
| `foxos field-service schedule schedule` | `field-service_schedule_schedule` | modify | Schedule |
| `foxos field-service clients show` | `field-service_clients_show` | read | Clients |
| `foxos field-service requests show` | `field-service_requests_show` | read | Requests |
| `foxos field-service quotes show` | `field-service_quotes_show` | read | Quotes |
| `foxos field-service jobs show` | `field-service_jobs_show` | read | Jobs |
| `foxos field-service invoices show` | `field-service_invoices_show` | read | Invoices |
| `foxos field-service payments show` | `field-service_payments_show` | read | Payments |
| `foxos field-service timesheets show` | `field-service_timesheets_show` | read | Timesheets |
| `foxos field-service expenses show` | `field-service_expenses_show` | read | Expenses |
| `foxos field-service reports show` | `field-service_reports_show` | read | Reports |
| `foxos field-service source-code-github-opens-tab show` | `field-service_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos field-service puter show` | `field-service_puter_show` | read | Puter |
| `foxos field-service navigation collapse` | `field-service_navigation_collapse` | read | Collapse navigation |
| `foxos field-service search search` | `field-service_search_search` | read | Search |
| `foxos field-service keyboard-shortcuts activate` | `field-service_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos field-service settings show` | `field-service_settings_show` | read | Settings |
| `foxos field-service account-appearance activate` | `field-service_account-appearance_activate` | modify | Account and appearance |
| `foxos field-service dismiss dismiss` | `field-service_dismiss_dismiss` | read | Dismiss |
| `foxos field-service business-details create` | `field-service_business-details_create` | modify | Add your business details |
| `foxos field-service services-you-offer create` | `field-service_services-you-offer_create` | modify | Add the services you offer |
| `foxos field-service team create` | `field-service_team_create` | modify | Add your team |
| `foxos field-service first-client create` | `field-service_first-client_create` | modify | Add your first client |
| `foxos field-service first-quote send` | `field-service_first-quote_send` | modify | Send your first quote |
| `foxos field-service schedule-2 schedule` | `field-service_schedule-2_schedule` | modify | Schedule |
| `foxos field-service job create` | `field-service_job_create` | modify | New job |
| `foxos field-service reports-2 show` | `field-service_reports-2_show` | read | Reports |
| `foxos field-service close close` | `field-service_close_close` | read | Close |
| `foxos field-service business-name set VALUE [--submit]` | `field-service_business-name_set` | modify | Business name |
| `foxos field-service name set VALUE [--submit]` | `field-service_name_set` | modify | Your name |
| `foxos field-service industry set VALUE [--submit]` | `field-service_industry_set` | modify | Industry |
| `foxos field-service currency set VALUE [--submit]` | `field-service_currency_set` | modify | Currency |
| `foxos field-service sample-data import` | `field-service_sample-data_import` | modify | Load sample data |
| `foxos field-service get-started activate` | `field-service_get-started_activate` | modify | Get started |
| `foxos field-service it dismiss` | `field-service_it_dismiss` | read | Got it |
| `foxos field-service command-palette show` | `field-service_command-palette_show` | read | 快捷键 mod+k |

### legal（`legal`，43 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos legal timer start TARGET` | `legal_timer_start` | modify | start timer, #（1 项，如 Start timer, 00:00:00） |
| `foxos legal draft-bills-bills select TARGET` | `legal_draft-bills-bills_select` | read | draft bills$# bills（1 项，如 Draft bills$00 bills） |
| `foxos legal unpaid-bills select TARGET` | `legal_unpaid-bills_select` | read | unpaid$# bills（1 项，如 Unpaid$00 bills） |
| `foxos legal overdue-bills select TARGET` | `legal_overdue-bills_select` | read | overdue$# bills（1 项，如 Overdue$00 bills） |
| `foxos legal held-trust-trust-accounts select TARGET` | `legal_held-trust-trust-accounts_select` | read | held in trust$# trust accounts（1 项，如 Held in trust$0All trust accounts） |
| `foxos legal firm-name select TARGET` | `legal_firm-name_select` | read | firm name *（1 项，如 Firm name *） |
| `foxos legal content dismiss` | `legal_content_dismiss` | read | Skip to content |
| `foxos legal legal-dashboard show` | `legal_legal-dashboard_show` | read | Legal dashboard |
| `foxos legal dashboard show` | `legal_dashboard_show` | read | Dashboard |
| `foxos legal calendar show` | `legal_calendar_show` | read | Calendar |
| `foxos legal tasks show` | `legal_tasks_show` | read | Tasks |
| `foxos legal matters show` | `legal_matters_show` | read | Matters |
| `foxos legal contacts show` | `legal_contacts_show` | read | Contacts |
| `foxos legal activities show` | `legal_activities_show` | read | Activities |
| `foxos legal billing show` | `legal_billing_show` | read | Billing |
| `foxos legal accounts show` | `legal_accounts_show` | read | Accounts |
| `foxos legal documents show` | `legal_documents_show` | read | Documents |
| `foxos legal communications show` | `legal_communications_show` | read | Communications |
| `foxos legal reports show` | `legal_reports_show` | read | Reports |
| `foxos legal settings show` | `legal_settings_show` | read | Settings |
| `foxos legal source-code-github-opens-tab show` | `legal_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos legal navigation collapse` | `legal_navigation_collapse` | read | Collapse navigation |
| `foxos legal search search` | `legal_search_search` | read | Search |
| `foxos legal timer-details activate` | `legal_timer-details_activate` | modify | Timer details |
| `foxos legal n create` | `legal_n_create` | modify | Create new (N) |
| `foxos legal alerts activate` | `legal_alerts_activate` | modify | Alerts |
| `foxos legal account-appearance activate` | `legal_account-appearance_activate` | modify | Account and appearance |
| `foxos legal task create` | `legal_task_create` | modify | New task |
| `foxos legal time record` | `legal_time_record` | modify | Record time |
| `foxos legal personal show` | `legal_personal_show` | read | Personal |
| `foxos legal firm show` | `legal_firm_show` | read | Firm |
| `foxos legal firm-users open` | `legal_firm-users_open` | read | Open firm users |
| `foxos legal calendar-2 show` | `legal_calendar-2_show` | read | Calendar |
| `foxos legal matters-2 show` | `legal_matters-2_show` | read | Matters |
| `foxos legal matter create` | `legal_matter_create` | modify | New matter |
| `foxos legal activities-2 show` | `legal_activities-2_show` | read | Activities |
| `foxos legal billing-2 show` | `legal_billing-2_show` | read | Billing |
| `foxos legal i-understand activate` | `legal_i-understand_activate` | modify | I understand |
| `foxos legal close close` | `legal_close_close` | read | Close |
| `foxos legal currency set VALUE [--submit]` | `legal_currency_set` | modify | Currency |
| `foxos legal explore-sample-data activate` | `legal_explore-sample-data_activate` | modify | Explore with sample data |
| `foxos legal continue activate` | `legal_continue_activate` | modify | Continue |
| `foxos legal command-palette show` | `legal_command-palette_show` | read | 快捷键 mod+k |

### fleet（`fleet`，41 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos fleet content dismiss` | `fleet_content_dismiss` | read | Skip to content |
| `foxos fleet dashboard show` | `fleet_dashboard_show` | read | Dashboard |
| `foxos fleet dashboard-2 show` | `fleet_dashboard-2_show` | read | Dashboard |
| `foxos fleet vehicles activate` | `fleet_vehicles_activate` | modify | Vehicles |
| `foxos fleet inspections activate` | `fleet_inspections_activate` | modify | Inspections |
| `foxos fleet issues show` | `fleet_issues_show` | read | Issues |
| `foxos fleet reminders activate` | `fleet_reminders_activate` | modify | Reminders |
| `foxos fleet service activate` | `fleet_service_activate` | modify | Service |
| `foxos fleet contacts show` | `fleet_contacts_show` | read | Contacts |
| `foxos fleet vendors show` | `fleet_vendors_show` | read | Vendors |
| `foxos fleet parts-inventory activate` | `fleet_parts-inventory_activate` | modify | Parts and inventory |
| `foxos fleet fuel-energy show` | `fleet_fuel-energy_show` | read | Fuel and energy |
| `foxos fleet documents show` | `fleet_documents_show` | read | Documents |
| `foxos fleet reports show` | `fleet_reports_show` | read | Reports |
| `foxos fleet settings show` | `fleet_settings_show` | read | Settings |
| `foxos fleet source-code-github-opens-tab show` | `fleet_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos fleet puter show` | `fleet_puter_show` | read | Puter |
| `foxos fleet sidebar collapse` | `fleet_sidebar_collapse` | read | Collapse sidebar |
| `foxos fleet search search` | `fleet_search_search` | read | Search |
| `foxos fleet keyboard-shortcuts activate` | `fleet_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos fleet needs-attention activate` | `fleet_needs-attention_activate` | modify | Needs attention |
| `foxos fleet add create` | `fleet_add_create` | modify | Add new |
| `foxos fleet account-appearance activate` | `fleet_account-appearance_activate` | modify | Account and appearance |
| `foxos fleet inspection start` | `fleet_inspection_start` | modify | Start inspection |
| `foxos fleet report-issue show` | `fleet_report-issue_show` | read | Report issue |
| `foxos fleet fuel create` | `fleet_fuel_create` | modify | Add fuel |
| `foxos fleet vehicle create` | `fleet_vehicle_create` | modify | Add vehicle |
| `foxos fleet contact create` | `fleet_contact_create` | modify | Add contact |
| `foxos fleet inspection-forms show` | `fleet_inspection-forms_show` | read | Inspection forms |
| `foxos fleet service-programs show` | `fleet_service-programs_show` | read | Service programs |
| `foxos fleet team-access show` | `fleet_team-access_show` | read | Team access |
| `foxos fleet it dismiss` | `fleet_it_dismiss` | read | Got it |
| `foxos fleet close close` | `fleet_close_close` | read | Close |
| `foxos fleet fleet-or-company-name set VALUE [--submit]` | `fleet_fleet-or-company-name_set` | modify | Fleet or company name |
| `foxos fleet distance set VALUE [--submit]` | `fleet_distance_set` | modify | Distance |
| `foxos fleet fuel-volume set VALUE [--submit]` | `fleet_fuel-volume_set` | modify | Fuel volume |
| `foxos fleet currency set VALUE [--submit]` | `fleet_currency_set` | modify | Currency |
| `foxos fleet sample-data start` | `fleet_sample-data_start` | modify | Start with sample data |
| `foxos fleet continue activate` | `fleet_continue_activate` | modify | Continue |
| `foxos fleet command-palette show` | `fleet_command-palette_show` | read | 快捷键 mod+k |
| `foxos fleet document save` | `fleet_document_save` | modify | 快捷键 mod+s |

### property-management（`property-management`，45 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos property-management collected-charges-posted-yet select TARGET` | `property-management_collected-charges-posted-yet_select` | read | collected in # charges posted yet（1 项，如 Collected in November$0.00No charges posted yet） |
| `foxos property-management outstanding-balances-is-paid-up select TARGET` | `property-management_outstanding-balances-is-paid-up_select` | read | outstanding balances$# is paid up（1 项，如 Outstanding balances$0.00Everyone is paid up） |
| `foxos property-management units-occupied select TARGET` | `property-management_units-occupied_select` | read | # of # units occupied（1 项，如 Occupancy0%0 of 0 units occupied） |
| `foxos property-management work-urgent open TARGET` | `property-management_work-urgent_open` | read | open work # urgent（1 项，如 Open work orders0None urgent） |
| `foxos property-management view show TARGET` | `property-management_view_show` | read | view all: *（5 项，如 View all: Outstanding balances） |
| `foxos property-management financials select TARGET` | `property-management_financials_select` | read | financials: *（1 项，如 Financials: Income and expenses） |
| `foxos property-management renewals select TARGET` | `property-management_renewals_select` | read | renewals: *（1 项，如 Renewals: Expiring leases） |
| `foxos property-management calendar select TARGET` | `property-management_calendar_select` | read | calendar: *（1 项，如 Calendar: This week） |
| `foxos property-management listings select TARGET` | `property-management_listings_select` | read | listings: *（1 项，如 Listings: Vacant units） |
| `foxos property-management content dismiss` | `property-management_content_dismiss` | read | Skip to content |
| `foxos property-management dashboard show` | `property-management_dashboard_show` | read | Dashboard |
| `foxos property-management n create` | `property-management_n_create` | modify | Create (N) |
| `foxos property-management dashboard-2 show` | `property-management_dashboard-2_show` | read | Dashboard |
| `foxos property-management rentals activate` | `property-management_rentals_activate` | modify | Rentals |
| `foxos property-management properties show` | `property-management_properties_show` | read | Properties |
| `foxos property-management rent-roll show` | `property-management_rent-roll_show` | read | Rent roll |
| `foxos property-management tenants show` | `property-management_tenants_show` | read | Tenants |
| `foxos property-management rental-owners show` | `property-management_rental-owners_show` | read | Rental owners |
| `foxos property-management outstanding-balances show` | `property-management_outstanding-balances_show` | read | Outstanding balances |
| `foxos property-management leasing activate` | `property-management_leasing_activate` | modify | Leasing |
| `foxos property-management accounting activate` | `property-management_accounting_activate` | modify | Accounting |
| `foxos property-management maintenance activate` | `property-management_maintenance_activate` | modify | Maintenance |
| `foxos property-management tasks show` | `property-management_tasks_show` | read | Tasks |
| `foxos property-management communication show` | `property-management_communication_show` | read | Communication |
| `foxos property-management calendar show` | `property-management_calendar_show` | read | Calendar |
| `foxos property-management reports show` | `property-management_reports_show` | read | Reports |
| `foxos property-management settings show` | `property-management_settings_show` | read | Settings |
| `foxos property-management source-code-github-opens-tab show` | `property-management_source-code-github-opens-tab_show` | read | Source code on GitHub (opens in a new tab) |
| `foxos property-management puter show` | `property-management_puter_show` | read | Puter |
| `foxos property-management navigation collapse` | `property-management_navigation_collapse` | read | Collapse navigation |
| `foxos property-management search search` | `property-management_search_search` | read | Search |
| `foxos property-management keyboard-shortcuts activate` | `property-management_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos property-management account-appearance activate` | `property-management_account-appearance_activate` | modify | Account and appearance |
| `foxos property-management receive-payment activate` | `property-management_receive-payment_activate` | modify | Receive payment |
| `foxos property-management work-orderwork-order create` | `property-management_work-orderwork-order_create` | modify | New work orderWork order |
| `foxos property-management lease create` | `property-management_lease_create` | modify | New lease |
| `foxos property-management close close` | `property-management_close_close` | read | Close |
| `foxos property-management company-name set VALUE [--submit]` | `property-management_company-name_set` | modify | Company name |
| `foxos property-management name set VALUE [--submit]` | `property-management_name_set` | modify | Your name |
| `foxos property-management what-you-manage set VALUE [--submit]` | `property-management_what-you-manage_set` | modify | What you manage |
| `foxos property-management currency set VALUE [--submit]` | `property-management_currency_set` | modify | Currency |
| `foxos property-management sample-portfolio import` | `property-management_sample-portfolio_import` | modify | Load sample portfolio |
| `foxos property-management get-started activate` | `property-management_get-started_activate` | modify | Get started |
| `foxos property-management it dismiss` | `property-management_it_dismiss` | read | Got it |
| `foxos property-management command-palette show` | `property-management_command-palette_show` | read | 快捷键 mod+k |

### api-client（`api-client`，58 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos api-client account select TARGET` | `api-client_account_select` | read | account: *（1 项，如 Account: local） |
| `foxos api-client environment select TARGET` | `api-client_environment_select` | read | environment: *（1 项，如 Environment: none） |
| `foxos api-client requests-through send TARGET` | `api-client_requests-through_send` | modify | send requests through: *（1 项，如 Send requests through: Auto） |
| `foxos api-client editor dismiss` | `api-client_editor_dismiss` | read | Skip to editor |
| `foxos api-client collections-requests-environments search` | `api-client_collections-requests-environments_search` | read | Search collections, requests and environments |
| `foxos api-client import import` | `api-client_import_import` | modify | Import |
| `foxos api-client theme activate` | `api-client_theme_activate` | modify | Theme |
| `foxos api-client settings show` | `api-client_settings_show` | read | Settings |
| `foxos api-client collections activate` | `api-client_collections_activate` | modify | Collections |
| `foxos api-client environments activate` | `api-client_environments_activate` | modify | Environments |
| `foxos api-client history activate` | `api-client_history_activate` | modify | History |
| `foxos api-client collection create` | `api-client_collection_create` | modify | New collection |
| `foxos api-client filter set VALUE [--submit]` | `api-client_filter_set` | modify | Filter |
| `foxos api-client collection-2 create` | `api-client_collection-2_create` | modify | New collection |
| `foxos api-client import-2 import` | `api-client_import-2_import` | modify | Import |
| `foxos api-client sidebar resize` | `api-client_sidebar_resize` | modify | Resize sidebar |
| `foxos api-client request create` | `api-client_request_create` | modify | New request |
| `foxos api-client open-tabs activate` | `api-client_open-tabs_activate` | modify | All open tabs |
| `foxos api-client quick-look-at-variables activate` | `api-client_quick-look-at-variables_activate` | modify | Quick look at variables |
| `foxos api-client requestctrlaltn create` | `api-client_requestctrlaltn_create` | modify | New requestCtrl+Alt+N |
| `foxos api-client collection-3 create` | `api-client_collection-3_create` | modify | New collection |
| `foxos api-client import-3 import` | `api-client_import-3_import` | modify | Import |
| `foxos api-client environment create` | `api-client_environment_create` | modify | New environment |
| `foxos api-client websocket create` | `api-client_websocket_create` | modify | New WebSocket |
| `foxos api-client collection run` | `api-client_collection_run` | modify | Run a collection |
| `foxos api-client sidebar toggle` | `api-client_sidebar_toggle` | modify | Toggle sidebar |
| `foxos api-client console activate` | `api-client_console_activate` | modify | Console |
| `foxos api-client cookies activate` | `api-client_cookies_activate` | modify | Cookies |
| `foxos api-client response-layout activate` | `api-client_response-layout_activate` | modify | Response layout |
| `foxos api-client keyboard-shortcuts activate` | `api-client_keyboard-shortcuts_activate` | modify | Keyboard shortcuts |
| `foxos api-client source-code-github show` | `api-client_source-code-github_show` | read | Source code on GitHub |
| `foxos api-client notification dismiss` | `api-client_notification_dismiss` | read | Dismiss notification |
| `foxos api-client system activate` | `api-client_system_activate` | modify | System |
| `foxos api-client light activate` | `api-client_light_activate` | modify | Light |
| `foxos api-client dark activate` | `api-client_dark_activate` | modify | Dark |
| `foxos api-client close close` | `api-client_close_close` | read | Close |
| `foxos api-client general show` | `api-client_general_show` | read | General |
| `foxos api-client requests show` | `api-client_requests_show` | read | Requests |
| `foxos api-client about show` | `api-client_about_show` | read | About |
| `foxos api-client system toggle` | `api-client_system_toggle` | modify | System |
| `foxos api-client light toggle` | `api-client_light_toggle` | modify | Light |
| `foxos api-client dark toggle` | `api-client_dark_toggle` | modify | Dark |
| `foxos api-client below toggle` | `api-client_below_toggle` | modify | Below |
| `foxos api-client beside toggle` | `api-client_beside_toggle` | modify | Beside |
| `foxos api-client sync-now activate` | `api-client_sync-now_activate` | modify | Sync now |
| `foxos api-client everything export` | `api-client_everything_export` | modify | Export everything |
| `foxos api-client websocket-request create` | `api-client_websocket-request_create` | modify | New WebSocket request |
| `foxos api-client tabs close` | `api-client_tabs_close` | read | Close all tabs |
| `foxos api-client no-environment activate` | `api-client_no-environment_activate` | modify | No environment |
| `foxos api-client environment-none-environment create` | `api-client_environment-none-environment_create` | modify | New environment |
| `foxos api-client manage-environments activate` | `api-client_manage-environments_activate` | modify | Manage environments |
| `foxos api-client edit update` | `api-client_edit_update` | modify | Edit |
| `foxos api-client automatic activate` | `api-client_automatic_activate` | modify | Automatic |
| `foxos api-client browser-only activate` | `api-client_browser-only_activate` | modify | Browser only |
| `foxos api-client puter-relay activate` | `api-client_puter-relay_activate` | modify | Puter relay |
| `foxos api-client what-is-difference activate` | `api-client_what-is-difference_activate` | modify | What is the difference? |
| `foxos api-client below-request activate` | `api-client_below-request_activate` | modify | Below the request |
| `foxos api-client beside-request activate` | `api-client_beside-request_activate` | modify | Beside the request |

### chess（`chess`，30 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos chess black-rook select TARGET` | `chess_black-rook_select` | read | #, black rook（2 项，如 a8, Black rook） |
| `foxos chess black-knight select TARGET` | `chess_black-knight_select` | read | #, black knight（2 项，如 b8, Black knight） |
| `foxos chess black-bishop select TARGET` | `chess_black-bishop_select` | read | #, black bishop（2 项，如 c8, Black bishop） |
| `foxos chess black-queen select TARGET` | `chess_black-queen_select` | read | #, black queen（1 项，如 d8, Black queen） |
| `foxos chess black-king select TARGET` | `chess_black-king_select` | read | #, black king（1 项，如 e8, Black king） |
| `foxos chess black-pawn select TARGET` | `chess_black-pawn_select` | read | #, black pawn（8 项，如 a7, Black pawn） |
| `foxos chess empty select TARGET` | `chess_empty_select` | read | #, empty（32 项，如 a6, empty） |
| `foxos chess white-pawn select TARGET` | `chess_white-pawn_select` | read | #, white pawn（8 项，如 a2, White pawn） |
| `foxos chess white-rook select TARGET` | `chess_white-rook_select` | read | #, white rook（2 项，如 a1, White rook） |
| `foxos chess white-knight select TARGET` | `chess_white-knight_select` | read | #, white knight（2 项，如 b1, White knight） |
| `foxos chess white-bishop select TARGET` | `chess_white-bishop_select` | read | #, white bishop（2 项，如 c1, White bishop） |
| `foxos chess white-queen select TARGET` | `chess_white-queen_select` | read | #, white queen（1 项，如 d1, White queen） |
| `foxos chess white-king select TARGET` | `chess_white-king_select` | read | #, white king（1 项，如 e1, White king） |
| `foxos chess light-theme activate` | `chess_light-theme_activate` | modify | Light theme |
| `foxos chess dark-theme activate` | `chess_dark-theme_activate` | modify | Dark theme |
| `foxos chess follow-system-theme activate` | `chess_follow-system-theme_activate` | modify | Follow system theme |
| `foxos chess computer activate` | `chess_computer_activate` | modify | Computer |
| `foxos chess pass-play activate` | `chess_pass-play_activate` | modify | Pass & Play |
| `foxos chess online activate` | `chess_online_activate` | modify | Online |
| `foxos chess game-as-pgn copy` | `chess_game-as-pgn_copy` | modify | Copy the game as PGN |
| `foxos chess game-as-pgn-file export` | `chess_game-as-pgn-file_export` | modify | Download the game as a PGN file |
| `foxos chess go-starting-position activate` | `chess_go-starting-position_activate` | modify | Go to the starting position |
| `foxos chess go-back-one-move activate` | `chess_go-back-one-move_activate` | modify | Go back one move |
| `foxos chess go-forward-one-move activate` | `chess_go-forward-one-move_activate` | modify | Go forward one move |
| `foxos chess return-current-position activate` | `chess_return-current-position_activate` | modify | Return to the current position |
| `foxos chess difficulty set VALUE [--submit]` | `chess_difficulty_set` | modify | Difficulty |
| `foxos chess clock set VALUE [--submit]` | `chess_clock_set` | modify | Clock |
| `foxos chess play-as set VALUE [--submit]` | `chess_play-as_set` | modify | Play as |
| `foxos chess game create` | `chess_game_create` | modify | New game |
| `foxos chess undo undo` | `chess_undo_undo` | modify | Undo |

### backgammon（`backgammon`，27 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos backgammon point-white-checkers select TARGET` | `backgammon_point-white-checkers_select` | read | point # white checkers（4 项，如 Point 13, 5 White checkers） |
| `foxos backgammon point-empty select TARGET` | `backgammon_point-empty_select` | read | point #, empty（16 项，如 Point 14, empty） |
| `foxos backgammon point-black-checkers select TARGET` | `backgammon_point-black-checkers_select` | read | point # black checkers（4 项，如 Point 17, 3 Black checkers） |
| `foxos backgammon light-theme activate` | `backgammon_light-theme_activate` | modify | Light theme |
| `foxos backgammon dark-theme activate` | `backgammon_dark-theme_activate` | modify | Dark theme |
| `foxos backgammon follow-system-theme activate` | `backgammon_follow-system-theme_activate` | modify | Follow system theme |
| `foxos backgammon black-bar-empty activate` | `backgammon_black-bar-empty_activate` | modify | Black bar, empty |
| `foxos backgammon black-tray-empty activate` | `backgammon_black-tray-empty_activate` | modify | Black tray, empty |
| `foxos backgammon white-bar-empty activate` | `backgammon_white-bar-empty_activate` | modify | White bar, empty |
| `foxos backgammon white-tray-empty activate` | `backgammon_white-tray-empty_activate` | modify | White tray, empty |
| `foxos backgammon computer activate` | `backgammon_computer_activate` | modify | Computer |
| `foxos backgammon pass-play activate` | `backgammon_pass-play_activate` | modify | Pass & Play |
| `foxos backgammon online activate` | `backgammon_online_activate` | modify | Online |
| `foxos backgammon moves activate` | `backgammon_moves_activate` | modify | Moves |
| `foxos backgammon game-as-mat-transcript copy` | `backgammon_game-as-mat-transcript_copy` | modify | Copy the game as a .mat transcript |
| `foxos backgammon game-as-mat-file export` | `backgammon_game-as-mat-file_export` | modify | Download the game as a .mat file |
| `foxos backgammon roll-start activate` | `backgammon_roll-start_activate` | modify | Roll to start |
| `foxos backgammon difficulty set VALUE [--submit]` | `backgammon_difficulty_set` | modify | Difficulty |
| `foxos backgammon clock set VALUE [--submit]` | `backgammon_clock_set` | modify | Clock |
| `foxos backgammon doubling-cube set VALUE [--submit]` | `backgammon_doubling-cube_set` | modify | Doubling cube |
| `foxos backgammon play-as set VALUE [--submit]` | `backgammon_play-as_set` | modify | Play as |
| `foxos backgammon game create` | `backgammon_game_create` | modify | New game |
| `foxos backgammon turn undo` | `backgammon_turn_undo` | modify | Undo turn |
| `foxos backgammon go-starting-position activate` | `backgammon_go-starting-position_activate` | modify | Go to the starting position |
| `foxos backgammon go-back-one-turn activate` | `backgammon_go-back-one-turn_activate` | modify | Go back one turn |
| `foxos backgammon go-forward-one-turn activate` | `backgammon_go-forward-one-turn_activate` | modify | Go forward one turn |
| `foxos backgammon return-current-position activate` | `backgammon_return-current-position_activate` | modify | Return to the current position |

### checkers（`checkers`，21 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos checkers white-man select TARGET` | `checkers_white-man_select` | read | #, white man（12 项，如 32, White man） |
| `foxos checkers empty select TARGET` | `checkers_empty_select` | read | #, empty（8 项，如 20, empty） |
| `foxos checkers black-man select TARGET` | `checkers_black-man_select` | read | #, black man（12 项，如 12, Black man） |
| `foxos checkers light-theme activate` | `checkers_light-theme_activate` | modify | Light theme |
| `foxos checkers dark-theme activate` | `checkers_dark-theme_activate` | modify | Dark theme |
| `foxos checkers follow-system-theme activate` | `checkers_follow-system-theme_activate` | modify | Follow system theme |
| `foxos checkers computer activate` | `checkers_computer_activate` | modify | Computer |
| `foxos checkers pass-play activate` | `checkers_pass-play_activate` | modify | Pass & Play |
| `foxos checkers online activate` | `checkers_online_activate` | modify | Online |
| `foxos checkers moves activate` | `checkers_moves_activate` | modify | Moves |
| `foxos checkers game-as-pdn copy` | `checkers_game-as-pdn_copy` | modify | Copy the game as PDN |
| `foxos checkers game-as-pdn-file export` | `checkers_game-as-pdn-file_export` | modify | Download the game as a PDN file |
| `foxos checkers difficulty set VALUE [--submit]` | `checkers_difficulty_set` | modify | Difficulty |
| `foxos checkers clock set VALUE [--submit]` | `checkers_clock_set` | modify | Clock |
| `foxos checkers play-as set VALUE [--submit]` | `checkers_play-as_set` | modify | Play as |
| `foxos checkers game create` | `checkers_game_create` | modify | New game |
| `foxos checkers undo undo` | `checkers_undo_undo` | modify | Undo |
| `foxos checkers go-starting-position activate` | `checkers_go-starting-position_activate` | modify | Go to the starting position |
| `foxos checkers go-back-one-move activate` | `checkers_go-back-one-move_activate` | modify | Go back one move |
| `foxos checkers go-forward-one-move activate` | `checkers_go-forward-one-move_activate` | modify | Go forward one move |
| `foxos checkers return-current-position activate` | `checkers_return-current-position_activate` | modify | Return to the current position |

### solitaire（`solitaire`，9 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos solitaire klondike-draw select TARGET` | `solitaire_klondike-draw_select` | read | klondike, draw #（2 项，如 Klondike, Draw 1） |
| `foxos solitaire vegas-draw select TARGET` | `solitaire_vegas-draw_select` | read | vegas, draw #（2 项，如 Vegas, Draw 1） |
| `foxos solitaire spider-suit select TARGET` | `solitaire_spider-suit_select` | read | spider, # suit（1 项，如 Spider, 1 suit） |
| `foxos solitaire spider-suits select TARGET` | `solitaire_spider-suits_select` | read | spider, # suits（2 项，如 Spider, 2 suits） |
| `foxos solitaire game select` | `solitaire_game_select` | read | Choose a game |
| `foxos solitaire undo undo` | `solitaire_undo_undo` | modify | Undo |
| `foxos solitaire powered-by-puter show` | `solitaire_powered-by-puter_show` | read | Powered by Puter |
| `foxos solitaire document create` | `solitaire_document_create` | modify | 快捷键 mod+n |
| `foxos solitaire edit undo` | `solitaire_edit_undo` | modify | 快捷键 mod+z |

### sudoku（`sudoku`，39 个语义命令）

| CLI | 工具接口名 | 权限 | 说明 |
|---|---|---|---|
| `foxos sudoku row-column-clue select TARGET` | `sudoku_row-column-clue_select` | read | row #, column #, clue（30 项，如 row 1, column 1, 6, clue） |
| `foxos sudoku row-column-empty select TARGET` | `sudoku_row-column-empty_select` | read | row #, column #, empty（51 项，如 row 1, column 2, empty） |
| `foxos sudoku pencil-n select TARGET` | `sudoku_pencil-n_select` | read | pencil # (n)（1 项，如 Pencil marks (N)） |
| `foxos sudoku remaining select TARGET` | `sudoku_remaining_select` | read | # remaining（9 项，如 1, 3 remaining） |
| `foxos sudoku settings-row-column-empty select TARGET` | `sudoku_settings-row-column-empty_select` | read | row #, column #, empty（20 项，如 row 1, column 1, empty） |
| `foxos sudoku settings-row-column-clue select TARGET` | `sudoku_settings-row-column-clue_select` | read | row #, column #, clue（30 项，如 row 1, column 3, 1, clue） |
| `foxos sudoku settings-remaining select TARGET` | `sudoku_settings-remaining_select` | read | # remaining（7 项，如 1, 6 remaining） |
| `foxos sudoku tidy-pencil select TARGET` | `sudoku_tidy-pencil_select` | read | tidy pencil #（1 项，如 Tidy pencil marks） |
| `foxos sudoku puzzle-row-column-clue select TARGET` | `sudoku_puzzle-row-column-clue_select` | read | row #, column #, clue（27 项，如 row 1, column 2, 8, clue） |
| `foxos sudoku puzzle-row-column-empty select TARGET` | `sudoku_puzzle-row-column-empty_select` | read | row #, column #, empty（7 项，如 row 1, column 8, empty） |
| `foxos sudoku puzzle-remaining select TARGET` | `sudoku_puzzle-remaining_select` | read | # remaining（4 项，如 2, 3 remaining） |
| `foxos sudoku daily-row-column-clue select TARGET` | `sudoku_daily-row-column-clue_select` | read | row #, column #, clue（25 项，如 row 1, column 5, 5, clue） |
| `foxos sudoku daily-row-column-empty select TARGET` | `sudoku_daily-row-column-empty_select` | read | row #, column #, empty（2 项，如 row 3, column 9, empty） |
| `foxos sudoku daily-remaining select TARGET` | `sudoku_daily-remaining_select` | read | # remaining（5 项，如 1, 5 remaining） |
| `foxos sudoku powered-by-puter-row-column-clue select TARGET` | `sudoku_powered-by-puter-row-column-clue_select` | read | row #, column #, clue（25 项，如 row 1, column 1, 4, clue） |
| `foxos sudoku powered-by-puter-remaining select TARGET` | `sudoku_powered-by-puter-remaining_select` | read | # remaining（5 项，如 3, 3 remaining） |
| `foxos sudoku light-theme activate` | `sudoku_light-theme_activate` | modify | Light theme |
| `foxos sudoku dark-theme activate` | `sudoku_dark-theme_activate` | modify | Dark theme |
| `foxos sudoku match-system-theme activate` | `sudoku_match-system-theme_activate` | modify | Match system theme |
| `foxos sudoku records activate` | `sudoku_records_activate` | modify | Records |
| `foxos sudoku settings show` | `sudoku_settings_show` | read | Settings |
| `foxos sudoku signed-as-local activate` | `sudoku_signed-as-local_activate` | modify | Signed in as local |
| `foxos sudoku pause pause` | `sudoku_pause_pause` | modify | Pause |
| `foxos sudoku ctrlz undo` | `sudoku_ctrlz_undo` | modify | Undo (Ctrl+Z) |
| `foxos sudoku ctrlshiftz redo` | `sudoku_ctrlshiftz_redo` | modify | Redo (Ctrl+Shift+Z) |
| `foxos sudoku erase-backspace activate` | `sudoku_erase-backspace_activate` | modify | Erase (Backspace) |
| `foxos sudoku hint-h activate` | `sudoku_hint-h_activate` | modify | Hint (H) |
| `foxos sudoku next-puzzle set VALUE [--submit]` | `sudoku_next-puzzle_set` | modify | Next puzzle |
| `foxos sudoku puzzle create` | `sudoku_puzzle_create` | modify | New puzzle |
| `foxos sudoku daily activate` | `sudoku_daily_activate` | modify | Daily |
| `foxos sudoku powered-by-puter show` | `sudoku_powered-by-puter_show` | read | Powered by Puter |
| `foxos sudoku check-as-i-go toggle` | `sudoku_check-as-i-go_toggle` | modify | Check as I go |
| `foxos sudoku highlight-row-column-box toggle` | `sudoku_highlight-row-column-box_toggle` | modify | Highlight row, column and box |
| `foxos sudoku highlight-matching-digits toggle` | `sudoku_highlight-matching-digits_toggle` | modify | Highlight matching digits |
| `foxos sudoku show-digits-remaining toggle` | `sudoku_show-digits-remaining_toggle` | modify | Show digits remaining |
| `foxos sudoku show-clock toggle` | `sudoku_show-clock_toggle` | modify | Show the clock |
| `foxos sudoku done confirm` | `sudoku_done_confirm` | modify | Done |
| `foxos sudoku edit redo-shift` | `sudoku_edit_redo-shift` | modify | 快捷键 mod+shift+y |
| `foxos sudoku edit undo` | `sudoku_edit_undo` | modify | 快捷键 mod+z |
