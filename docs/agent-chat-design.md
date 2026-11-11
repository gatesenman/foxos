# 智能体聊天（主智能体 + 其他智能体）设计

[English](#english)

本文是狐狸OS「智能体」聊天的调研与设计记录：参考开源的 [CopilotKit/OpenBot](https://github.com/CopilotKit/OpenBot) 的界面与功能，做成「一个主智能体 + 任意多个其他智能体」，并让主智能体能灵活使用 [backnotprop/pstack](https://github.com/backnotprop/pstack) 的技能与原则。实现见文末「实现位置」。

## 1. 调研

### 1.1 许可证

| 项目 | 许可证 | 我们怎么用 |
|---|---|---|
| OpenBot（应用模板） | MIT（© 2026 CopilotKit） | **只借鉴界面与交互思路，不拷代码**。OpenBot 依赖的 CopilotKit Intelligence（会话、记忆、自动学习）是另行授权的服务，不是 MIT，我们完全不用。 |
| pstack | MIT（© 2026 Lauren Tan） | 允许再分发。技能和原则的 Markdown（`skills/*/SKILL.md` 及其 `references/`、`playbooks/`）随狐狸OS 一起分发，放在 `packages/core/foxos/data/pstack/`，附带原许可证全文 `NOTICE` 与来源提交号。不带 `statechart` 的 TypeScript 脚本和测试语料（体积大、需要 Bun）。 |
| ACP 注册表里的智能体 | 各自不同（Apache-2.0、MIT、proprietary…） | 每个智能体按注册表里的 `license` 字段决定：开源且允许再分发的可预装，proprietary 的只在用户点击安装时从官方来源下载。见 [agent-runtime.md](agent-runtime.md)。 |

### 1.2 OpenBot 是什么

OpenBot 是「AI 同事」工作区：React（Vite）前端 + Hono API 服务器 + PostgreSQL，智能体通过 AG-UI 协议接入，工具通过 MCP 接入，每个 Bot 有自己的浏览器「电脑」容器。和本项目相关的要点：

- **Bot（coworker）模型**：每个 Bot 有名字、头衔（title）、角色说明（role description）、头像种子（`avatarSeed`，用 boring-avatars 生成脸或「orb」）、可见性、是否隔离，以及后端（内置 Bot、远程 AG-UI 端点或 Mastra）。角色说明每次运行都作为「standing role」系统消息发给 Bot（`<identity>`、`<role>` 两段），再追加部署统一的工作规则（如何工作、何时询问、答案来源、何时用子智能体）。
- **主 Bot**：个人版只有一个起始 Bot「Personal Assistant」，作为默认对话对象；团队版有 `picked-harness` 默认智能体。其他 Bot 在 `/bots` 里创建，进入个人名册（置顶 / 隐藏）。
- **Bot 之间交接（handoff）**：一个 Bot 可以把任务交给另一个 Bot。交接内容是有类型的信封 `{task, constraints?, expecting?}`，而不是一段自由文本；有深度上限 `maxDepth` 和每次运行上限 `maxPerRun`；每次交接写审计，`initiator_kind = handoff`，「无人值守」过滤器能找出来。拒绝也是一句可以说给人听的话，而不是抛错。
- **子智能体**：`run_subagent` 让同一个 Bot 开一个新的运行做一部分工作，每个回答最多 5 个；子智能体遇到要人批准的动作会「交回」（handedBack）给主运行，由主运行在对话里请求批准。
- **聊天界面**：左侧 Bot / 频道名册（头像、正在输入的三点徽标）；对话区按「回合」排版；流式文字有节奏地显示（paced reveal）；工具调用是一行一行的卡片（tool-line / tool-activity），编码工具有专门卡片：命令 + 输出、文件编辑显示 diff、计划显示勾选清单；子任务步骤卡；输入框支持 `@` 提及 Bot、`/` 命令（技能）、附件条（图片与文本，上传后传链接不传字节）、听写、模型选择、排队发送。
- **审批卡片**：删除、发给别人、分享、发布、付款、改密码等动作先问人；选项有「允许一次 / 本对话允许 / 总是允许 / 拒绝」；改网站密码这类只能人做的，卡片写「这是你的事」。每次决定写审计。
- **接管**：Bot 的电脑画面可以实时看，人可以接手操作。
- **技能**：部署技能（管理员）和个人技能（作者），在 `/` 菜单里出现；超过 12 个工具时按技能匹配缩小每次提供的工具。
- **记忆**：每个 Bot 自己的记忆（来自对话和连接的应用，人确认后才生效），由 CopilotKit Intelligence 存储。
- **例程（routines）与目标（goals）**：定时让 Bot 做事，最短 15 分钟、最多 20 个启用；Bot 自己也能用工具创建 / 修改 / 删除例程。
- **审计**：每一行记录谁授权（actor）和是什么触发的（person / routine / handoff / …），可导出 CSV。

### 1.3 pstack 是什么、怎么调用

- **打包**：一个文件夹，`skills/<名字>/SKILL.md`，遵循 Agent Skills 格式：YAML 头 `name`、`description`（写明什么时候用、对应哪个斜杠命令），可选 `disable-model-invocation: true`（只在用户或另一个技能点名时才用，模型不自行触发）；正文是步骤。技能可带 `references/`（提示词模板、清单）、`playbooks/`（poteto-mode 的 23 个剧本）和 `scripts/`。
- **三类**：
  - 技能（`architect`、`tdd`、`swarm`、`arena`、`how`、`why`、`interrogate`、`unslop`、`reflect`…）——用 `/名字` 调用，或由另一个技能写「运行 **name** 技能」来调用。
  - 原则（24 个 `principle-*`，如「prove-it-works」「fix-root-causes」）——简短规则，被技能引用，在适用时自己加载。
  - 子智能体（`agents/poteto-agent.md`、`agents/comment-sicko.md`）——给 `/poteto-mode` 派出的委托用的身份说明；在 Claude Code 里是 `pstack:poteto-agent`。
- **总入口**：`/poteto-mode` 读请求、挑剧本、开待办，再按步骤调用其它技能与原则。
- **模型配置**：`/setup-pstack` 写一份「每个角色用哪个模型」的设置文件（Cursor：`~/.cursor/rules/pstack-models.mdc`；Claude Code：`~/.claude/rules/pstack-models.md`；其它：`~/.agents/pstack-models.md`）。`arena`、`architect`、`interrogate` 按列表里的模型各派一个子智能体。
- **跨 harness**：技能用 Cursor 的工具名写成（`Task`、`AskQuestion`），`docs/harness/claude-code.md` 给出到 Claude Code 的映射。镜像版去掉了 Cursor 专有部分，可以用 `npx skills add backnotprop/pstack` 装进 Claude Code、Codex、OpenCode 等。

## 2. 对照 OpenBot 的功能清单

状态：**已实现** = 有代码、有测试（括号里是用户故事编号，见 [user-stories.md](user-stories.md)）；**部分** = 有实现但没有在真实服务上跑通；**缺口** = 还没做；**不做** = 单机系统不需要。

| OpenBot 功能 | 狐狸OS 实现 | 状态 |
|---|---|---|
| Bot 资料：名字、头衔、角色、头像 | `foxos bot profile create/update/duplicate/reset/delete`；头像 = Tabler 图标 + 颜色，或工作空间里的图片 | 已实现（US-100） |
| 主 Bot | 每个工作空间固定一个主智能体「狐狸」（`main: true`，不能删除） | 已实现（US-100） |
| 其他 Bot 的名册：置顶、隐藏、搜索、正在运行的徽标 | 左栏名册；`--pinned/--hidden`；运行中显示动画徽标 | 已实现（US-100、US-108） |
| Bot 后端（内置 / AG-UI / Mastra） | 任一 ACP 智能体（本地智能体、Gemini CLI、Codex、Qwen Code、opencode、Claude Code、Cursor CLI…），或 OpenAI 兼容端点（只聊天，不带工具） | 已实现（US-102、US-116） |
| 流式回答、按回合排版 | ACP `agent_message_chunk` → SSE；重开窗口时从进行中回合的起点回放 | 已实现（US-107） |
| 工具卡片：命令 + 输出、diff、计划 | ACP `tool_call`/`tool_call_update`/`plan` → 卡片 | 已实现（US-102） |
| 审批卡片：允许一次 / 本对话 / 总是 / 拒绝 | ACP `session/request_permission`；每个智能体的审批模式与规则；审批页列出所有待批项 | 已实现（US-102、US-108） |
| `@` 提及、`/` 技能、附件 | 输入框 `@` 菜单、`/` 技能菜单、附件存到 `attachments/` 并作为 `resource_link` 发送 | 已实现（US-103、US-104） |
| 交接（handoff 信封 `{task, constraints, expecting}`）、深度与次数上限 | `foxos bot task delegate`、MCP `bot_task_delegate`；深度 3、每回合 5；审计 `delegated-by:<bot>` | 已实现（US-103） |
| 子智能体 | 其他 Bot 当子智能体（委托）；ACP 智能体自己的子任务原样显示为卡片 | 部分 |
| 技能（部署 / 个人） | pstack 随系统分发；工作空间 `.foxos/skills/` 与 `~/.agents/skills/` 覆盖同名；每个智能体可「全部 / 只选这些 / 关掉这些」 | 已实现（US-104） |
| 记忆 | `foxos bot memory add/list/forget`，每回合作为上下文；人确认才写入 | 已实现（US-105；不做自动学习） |
| 例程（定时） | `foxos bot routine create/update/delete/run`；systemd 用户定时器每 5 分钟检查；最短 15 分钟、最多 20 个启用 | 已实现（US-105） |
| 接管 | 狐狸OS 人工接管：全部暂停或只暂停一个智能体（`control pause --only bot:<id>`） | 已实现（US-106、US-115） |
| 审计（谁授权、什么触发） | `.foxos/audit.jsonl`：`bot:<id>/acp:<agent>`、远程是 `bot:<id>@<控制端>`；触发来源 person / routine / channel / handoff | 已实现 |
| 连接器：目录、OAuth、令牌、按 Bot 启用 | 见第 5 节 | 已实现（US-109–US-112；托管 OAuth 服务部分） |
| 频道（Slack 等） | Telegram 机器人、Webhook | 部分（只有这两种；Telegram 没有对真实机器人跑过） |
| Bot 的电脑 | 狐狸OS 本身就是智能体的电脑；多机见第 6 节 | 已实现（US-113–US-115） |
| 听写、语音 | — | 缺口 |
| 团队、可见性、SSO | `visibility` 字段保留，单机不生效 | 不做 |
| 自动学习、记忆来源导入 | 依赖 CopilotKit Intelligence（非 MIT） | 不做 |

## 3. 每个智能体的设置

设置页的分页：设置、技能、记忆、审批、例程、委托、机器、频道、管理。命令行是 `foxos bot config get/set`。

| OpenBot 设置 | 狐狸OS 字段（`foxos bot config set` 参数） | 状态 |
|---|---|---|
| Name | `name`（`--name`），同一工作空间唯一 | 已实现 |
| Title | `title`（`--title`） | 已实现 |
| Role description（standing role） | `role`（`--role`），每回合放进前言 | 已实现 |
| 额外指令 | `instructions`（`--instructions-stdin`） | 已实现 |
| Avatar（avatarSeed） | `avatar.icon/color/image`（`--icon --color --image`） | 已实现（用图标，不用生成的脸） |
| Backend / harness | `backend.kind=acp, agent`（`--agent`），或 `kind=model, base_url, model`（`--base-url --model`） | 已实现 |
| Model | `model`（`--model`），通过 ACP `session/set_model` 下发；没有就用该 ACP 智能体的默认（`foxos acp agent config --model`） | 已实现 |
| API key | `--api-key-stdin`，存在本机密钥库，任何输出里都是 `***` | 已实现（US-101） |
| Isolated / 工作文件夹 | `isolated`、`scope`（`bots/<id>`）；越界 PERMISSION_DENIED | 已实现 |
| Visibility | `visibility`（private/public） | 保留字段（单机） |
| Pinned / hidden / active | `pinned` `hidden` `active` | 已实现 |
| Notifications | `notifications` | 已实现 |
| Skills | `skills.mode/enabled/disabled`（`--skills-mode --skills --skills-off`） | 已实现 |
| Connectors | `connectors`（`--connectors`），只有列出的连接器的工具会给这个智能体 | 已实现（US-109） |
| Approvals | `approvals.mode`（ask / allow_reads / allow_all）、`rules`（`--rule 工具=allow|ask|deny`） | 已实现 |
| Handoff 范围 | `delegation.allowed/max_depth/max_per_turn`（`--delegate-to --max-depth --max-per-turn`） | 已实现 |
| Machines | `machines.allowed/default`（`--machines --default-machine`） | 已实现（US-114） |
| Channels | `channels`（`foxos bot channel set --kind telegram|webhook`） | 部分 |
| Routines | `foxos bot routine …`（按智能体） | 已实现 |

## 4. pstack 集成

1. **随系统分发**：`packages/core/foxos/data/pstack/`（MIT，带 `NOTICE` 与上游提交号 08547969）。`foxos bot skill list` 读每个 `SKILL.md` 的头部，分出 `skill` / `principle` / `subagent`。用户的同名技能优先。
2. **主智能体怎么用**：每回合的前言里有技能目录（名字、一句描述、SKILL.md 路径）；用户输入 `/architect …` 时把 SKILL.md 全文附在这一回合；智能体读 SKILL.md 或调用 MCP `bot_skill_show` 都记为「用过」，显示成回答上方的标签，写进 `skills_used`。
3. **多模型**：`foxos bot skill models` 写 `~/.agents/pstack-models.md`，把 pstack 的角色映射到其他智能体（例如 `arena runners: bot:claude, bot:codex`），主智能体用委托派发。
4. **给 ACP 背后的 CLI**：`foxos bot skill install --harness claude-code|codex|agents` 把 pstack 拷到它们自己的技能目录。

## 5. 连接器

| 能力 | 实现 |
|---|---|
| 目录 | `foxos connector catalog`：Parallel、Exa、Firecrawl（免密钥与 API key 两种）、Notion、Google Drive、GitHub、自定义 |
| 传输 | MCP Streamable HTTP 与 stdio（`connector add --command …`） |
| 认证 | 无；Bearer / 自定义头（`--token-stdin`，存密钥库）；OAuth 2.1：RFC 9728 → RFC 8414 发现、必须 S256 PKCE、动态客户端注册（RFC 7591）、刷新令牌、回调只听 127.0.0.1 |
| 按智能体启用 | 每个智能体的 `connectors` 列表；`connector tools` 列出工具 |
| 写操作 | 目录里的 `write_tools`、工具的 `destructiveHint` 或 `readOnlyHint:false` 都算写，按该智能体的审批模式处理 |
| 错误令牌 | 连接时被拒就不算连上，并断开（PERMISSION_DENIED） |

测试：本地的真实 OAuth 2.1 + MCP 测试服务（`tests/peers/oauth_mcp.py`）跑完整授权码流程；Exa 免密钥服务真实调用。Notion、Google Drive、GitHub 的托管 OAuth 流程已实现，但没有用真实账号跑过。

## 6. 多机：一个智能体控制多台狐狸OS、多个智能体共用一台

- **被控端**：`foxos machine serve`（系统里是 `foxos-machine.service`，0.0.0.0:7443）。第一次启动生成自签名证书。
- **配对**：被控端 `foxos machine host code` 给出一次性配对码（默认 10 分钟）和证书指纹；控制端 `foxos machine pair --name … --url … --code … --fingerprint …`。指纹不对就拒绝（防中间人）。配对时控制端把自己的证书交给被控端登记。
- **双向 TLS**：之后每次连接，控制端钉住被控端证书指纹，被控端校验控制端出示的证书正是配对时登记的那张，再校验令牌。只偷到令牌连不上（US-113）。
- **授权，默认拒绝**：`foxos machine host grant --client … --bot … --permissions read,create,modify [--apps …] [--scope …]`；`revoke`、`unpair` 立即生效。`machine`、`control`（配对授权与接管本身）永远不能远程调用。
- **一个智能体，多台机器**：智能体设置里的 `machines` 决定它能去哪些机器；对话里 MCP 工具带 `machine` 参数，命令行用 `--machine`（US-114）。
- **多个智能体，一台机器**：每个智能体分别授权；同一文件单写者锁（LOCKED）、`--expect-mtime` 乐观并发（CONFLICT）、桌面输入同一时间只归一个智能体（CONFLICT）；被控端的人可以只暂停一个智能体；`machine ping` 显示此刻谁在操作；远端自称 `human` 会被改写成 `remote-human:<控制端>`，不能绕过接管（US-115）。
- **审计**：被控端记 `bot:<id>@<控制端>`、`interface: remote`；控制端记 `interface: remote-client` 与目标机器。

## 7. 聊天窗口：独立或停靠

- `foxos-bots`（开始菜单「智能体」）打开独立窗口（Chromium 系 `--app`，没有时用 Firefox 专用配置），窗口类 `foxos-bots`；已经开着就切到前台。
- **停靠**：标题栏按钮或 `foxos-bots --dock [--side left|right]`，窗口贴到屏幕一侧、全高、置顶、所有工作区可见；`--undock` 恢复。选择按用户保存在 `~/.config/foxos/bots-ui.json`。截图：`docs/screenshots/bots-window-separate.png`、`bots-window-docked.png`。
- `foxos-bots --page approvals|connectors|agents|machines|skills|routines|runtime|settings/<bot>/<tab>` 直达页面。
- 限制：停靠用 wmctrl 移动窗口，不预留屏幕边（strut），最大化的其他窗口会被盖住一部分。
- Electron 伴侣里的「智能体」应用用 webview 打开同一个界面。

## 8. 实现位置

| 部分 | 位置 |
|---|---|
| 智能体资料 / 对话 / 记忆 / 委托 / 技能 / 例程 / 频道 | `packages/core/foxos/bots.py`、`apps/bot.py`、`channels.py`、`skills.py` |
| ACP 客户端、智能体安装 / 设置 / 更新 / 握手 | `acp_client.py`、`apps/acp.py`、`secrets.py` |
| 本地确定性 ACP 智能体 | `local_agent.py` |
| 连接器 | `connectors.py`、`apps/connector.py` |
| 多机 | `machines.py`、`apps/machine.py` |
| 运行环境 | `runtime.py`、`apps/runtime.py`、`data/runtime-manifest.json`，见 [agent-runtime.md](agent-runtime.md) |
| 聊天服务与界面 | `botchat/server.py`、`botchat/launch.py`、`botchat/static/` |
| 操作系统 | `scripts/os/hooks/30-foxos.sh`、`35-agent-runtime.sh`、`scripts/os/bots/`、`scripts/os/systemd/` |
| 伴侣程序 | `apps/desktop/src/main/bots.js`、`renderer/js/apps/bots.js` |
| 测试 | `packages/core/tests/test_bots.py`、`test_connectors.py`、`test_machines.py`、`test_acp_real.py`、`test_os_runtime.py` |

---

<a id="english"></a>

# Agent chat (main bot + other bots) design

This records the research and design for FoxOS's bot chat: modelled on the open-source [CopilotKit/OpenBot](https://github.com/CopilotKit/OpenBot) UI and features, with one main bot plus any number of other bots, and a main bot that uses the [backnotprop/pstack](https://github.com/backnotprop/pstack) skills and principles flexibly.

## 1. Research

### 1.1 Licenses

| Project | License | How we use it |
|---|---|---|
| OpenBot (application template) | MIT (© 2026 CopilotKit) | **Ideas and interaction patterns only, no code copied.** CopilotKit Intelligence (durable threads, memory, learning), which OpenBot depends on, is separately licensed and not MIT; FoxOS does not use it. |
| pstack | MIT (© 2026 Lauren Tan) | Redistribution allowed. The skill and principle Markdown (`skills/*/SKILL.md` with `references/` and `playbooks/`) ships in `packages/core/foxos/data/pstack/` with the full license text in `NOTICE` and the upstream commit. The `statechart` TypeScript scripts and test corpus are left out (large, need Bun). |
| ACP registry agents | Varies (Apache-2.0, MIT, proprietary…) | Decided per agent from the registry `license` field: open-source agents that allow redistribution may be preinstalled; proprietary ones are only downloaded from the official source when the user installs them. See [agent-runtime.md](agent-runtime.md). |

### 1.2 OpenBot

A workspace for "AI coworkers": a React/Vite app, a Hono API server and PostgreSQL. Agents connect over AG-UI, tools over MCP, and each Bot gets its own browser "computer" container. What matters here:

- **Bot (coworker) model**: name, title, role description, avatar seed (boring-avatars faces or an "orb"), visibility, isolation, and a backend (built-in, remote AG-UI endpoint, or Mastra). The role goes out with every run as a standing-role system message (`<identity>`, `<role>`), followed by deployment-wide working rules.
- **Main bot**: the personal edition starts with one Bot, the Personal Assistant, as the default conversation; the team edition has a `picked-harness` default agent. Other Bots are created from `/bots` and live in a personal roster (pinned / hidden).
- **Handoff between Bots**: a typed envelope `{task, constraints?, expecting?}` rather than free text, with `maxDepth` and `maxPerRun` caps. Each hop is audited with `initiator_kind = handoff`, and a refusal is a sentence the Bot can say, not an error.
- **Subagents**: `run_subagent` starts a fresh run of the same Bot for part of an answer (max 5 per answer). A subagent that needs approval hands the action back to the main run.
- **Chat UI**: a roster sidebar with avatars and a typing badge; turn-based transcript; paced streaming text; tool calls as line cards, with dedicated coding cards (command + output, file edits as diffs, plans as checklists); subtask step cards; a composer with `@` mentions, `/` commands (skills), an attachment strip, dictation, a model picker and a send queue.
- **Approval cards** before delete, send, share, post, pay or credential changes: Allow once / Allow for this conversation / Always allow / Deny, each decision audited.
- **Take over**: watch the Bot's computer live and take control.
- **Skills** (deployment and personal) in the `/` menu; **memory** per Bot (stored in Intelligence); **routines and goals** on schedules; **audit** with actor and initiator, CSV export.

### 1.3 pstack

- **Packaging**: plain Agent Skills, `skills/<name>/SKILL.md` with YAML front matter (`name`, `description` saying when to use it and which slash command, optional `disable-model-invocation: true`), plus optional `references/`, `playbooks/` and `scripts/`.
- **Three kinds**: skills (`architect`, `tdd`, `swarm`, `arena`, `how`, `why`, `interrogate`, `unslop`, `reflect`…) invoked as `/name` or by another skill naming them; 24 `principle-*` rules loaded when they apply; subagent identities in `agents/` (`poteto-agent`, `comment-sicko`).
- **Entry point**: `/poteto-mode` matches the task to one of 23 playbooks, opens a todo list and calls other skills and principles as steps fire.
- **Model config**: `/setup-pstack` writes a per-role model file (`~/.cursor/rules/pstack-models.mdc`, `~/.claude/rules/pstack-models.md`, or `~/.agents/pstack-models.md`); `arena`, `architect` and `interrogate` fan out one subagent per listed model.
- **Harnesses**: written with Cursor tool names, mapped for Claude Code in `docs/harness/claude-code.md`; the mirror installs into Claude Code, Codex, OpenCode and others with `npx skills add backnotprop/pstack`.

## 2. OpenBot parity

The Chinese section above has the full tables. In short:

- **Done** (with tests): bot profiles and the main bot (US-100); per-bot settings, all OpenBot fields plus model, API key, scope, skills, connectors, approvals, delegation and machines (US-101); real ACP turns with tool cards, diffs, terminals and approval cards (US-102); `@` mentions and typed handoff envelopes with depth and per-turn limits (US-103); pstack skills (US-104); memory and routines (US-105); pausing one bot or all bots (US-106); the chat service with SSE replay (US-107) and the browser UI in both languages (US-108); connectors with a catalog, stdio/HTTP MCP, bearer tokens, OAuth 2.1 with discovery, PKCE, dynamic registration and refresh, per-bot enablement and write approval (US-109 to US-112); multiple machines (US-113 to US-115); third-party ACP agents (US-116 to US-118).
- **Partial**: hosted OAuth for Notion, Google Drive and GitHub was never run against a real account; channels are only Telegram and webhook; sub-agents work through delegation only.
- **Gaps**: dictation and voice.
- **Not planned**: teams, SSO, auto-learning.

## 3. Multiple machines

`foxos machine serve` runs on the controlled machine. Pairing uses a one-time code plus the certificate fingerprint, and the controller registers its own certificate. Every later connection is mutual TLS (pinned server fingerprint plus the registered client certificate) and also needs the token. Grants are deny-by-default, per bot, with permission, app and scope limits. The audit log names `bot:<id>@<controller>`. Several bots on one machine are kept apart by file locks (LOCKED), optimistic concurrency (CONFLICT), a single desktop-input owner, and per-bot pause.

## 4. Chat window

`foxos-bots` opens a separate window (class `foxos-bots`). `--dock`/`--undock` docks it to a screen edge or detaches it, and the choice is saved per user. `--page` opens a given page.

## 5. Where it lives

See the table in section 8 of the Chinese part.
