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

## 2. 映射到狐狸OS

| OpenBot 功能 | 狐狸OS 实现 | 状态 |
|---|---|---|
| Bot 资料：名字、头衔、角色、头像 | `foxos bot profile create/update`：名字、头衔、角色说明、头像（Tabler 字体图标名 + 颜色，或工作空间里的图片；不用 emoji） | 已实现 |
| 主 Bot（Personal Assistant） | 每个工作空间固定一个主智能体（`main: true`，不能删除，只能改设置）；第一次使用自动创建「狐狸」 | 已实现 |
| Bot 后端（内置 / AG-UI 端点） | 后端 = 任一已安装的 ACP 智能体（Claude Code、Codex、Gemini CLI、注册表里其它）或「本地智能体」（仓库自带、确定性的 ACP 进程，不需要模型密钥）或 OpenAI 兼容模型端点 | 已实现（模型端点见缺口） |
| 每个 Bot 自己的对话 | `.foxos/bots/<id>/messages.jsonl`；`foxos bot message list/send` | 已实现 |
| 每个 Bot 自己的记忆 | `.foxos/bots/<id>/memory.jsonl`；`foxos bot memory add/list/forget`；每回合作为上下文交给 Bot | 已实现（不做自动学习） |
| 工作范围（OpenBot 的每 Bot 文件夹 / 隔离） | 每个 Bot 有 `scope`（工作空间里的子目录）；ACP 的 `fs/*` 和终端都限制在范围内，越界返回 PERMISSION_DENIED；仍受工作空间约束、写锁、审计、人工接管 | 已实现 |
| 流式消息 | ACP `session/update` 的 `agent_message_chunk` → 服务端 SSE → 界面逐段追加 | 已实现 |
| 工具调用卡片（命令 + 输出、diff、计划） | ACP `tool_call` / `tool_call_update`（`content` 里的 `diff`、`terminal`）、`plan` → 卡片：文件编辑显示增删行，终端显示命令与输出，计划显示勾选清单 | 已实现 |
| 审批卡片 | ACP `session/request_permission` → 卡片，选项来自智能体（允许一次 / 总是允许 / 拒绝）；人工接管时一律拒绝 | 已实现（没有「本对话允许」的持久规则） |
| 附件 | 输入框选文件 → 存到工作空间 `attachments/`（经内核写入，有审计），作为 ACP `resource_link` 发给智能体 | 已实现 |
| `@` 提及其它 Bot | 输入 `@名字`：消息直接交给那个 Bot；主智能体回答里的 `@名字` 也会转交 | 已实现 |
| Bot 之间交接（handoff 信封） | `foxos bot task delegate --to <bot> --task … [--constraints …] [--expecting …]`；主智能体通过 MCP 工具 `bot_task_delegate` 调用；深度上限 3、每回合上限 5；审计里 `task` 字段记录 `delegated-by:<bot>` | 已实现 |
| 主 Bot 汇总回报 | 被委托的 Bot 的回答作为工具结果返回给主智能体；聊天里显示「已委托给 X」卡片，X 的回答折叠在卡片里 | 已实现 |
| 技能（`/` 菜单） | pstack 技能与原则：`foxos bot skill list/show/run`；输入框 `/` 弹出技能；主智能体每回合拿到技能目录，可通过 `fs/read_text_file` 读 SKILL.md 或 MCP `bot_skill_show` 调用；用过的技能显示成消息上方的标签 | 已实现 |
| 子智能体 | pstack 的子智能体说明（poteto-agent）在委托时可附加；ACP 智能体自身的子智能体（如 Claude Code 的 Task）原样显示为工具卡片 | 部分 |
| 接管 | 沿用狐狸OS 人工接管：暂停期间 ACP 写文件、终端和委托全部返回 PAUSED，审批卡片自动拒绝 | 已实现 |
| 审计 | 沿用 `.foxos/audit.jsonl`；身份 `bot:<id>`（经 ACP 智能体时 `bot:<id>/acp:<agent>`）；密钥参数在审计里写成 `***` | 已实现 |
| Bot 头像 | Tabler 图标字体 + 主题色圆形；ACP 智能体显示注册表官方图标 | 已实现 |
| 例程 / 目标 | 没做。可以用系统的 systemd 用户定时器调用 `foxos bot message send` | 缺口 |
| 团队共享、可见性、SSO | 单机系统，不需要 | 不做 |
| 自动学习、记忆来源导入 | 依赖 CopilotKit Intelligence（非 MIT） | 不做 |
| 听写、语音 | — | 缺口 |

已有部件和缺口：

- **已有**：Electron 伴侣里的「智能体会话」面板（单个 ACP 会话、权限卡片、审计时间线）、`apps/desktop/src/main/acp.js`（Node 版 ACP 客户端）、ACP 注册表安装（Electron 里）、`foxos` CLI / MCP、审计、人工接管、工作空间约束、写锁、轻量沙箱。
- **缺的（本次补上）**：Python 版 ACP 客户端（CLI / MCP / 操作系统里都能用，不依赖 Electron）、在系统里安装 ACP 智能体（`foxos acp agent install`）、本地密钥库、多个 Bot 的资料 / 对话 / 记忆、委托、pstack、操作系统里的聊天窗口。

## 3. pstack 集成设计

1. **随系统分发**：`packages/core/foxos/data/pstack/skills/`（MIT，带 `NOTICE` 与上游提交号）。`foxos bot skill list` 读每个 `SKILL.md` 的头部，分出 `skill` / `principle` / `subagent`，给出路径与是否 `disable-model-invocation`。用户还能把自己的技能放进工作空间 `.foxos/skills/<名字>/SKILL.md` 或 `~/.agents/skills/`，同名时用户的优先。
2. **主智能体怎么用**：
   - 每个回合，主智能体收到一段狐狸OS 前言：身份与角色、记忆、可委托的其它 Bot 名单、技能目录（名字 + 一句描述 + SKILL.md 绝对路径），以及规则「需要时先读 SKILL.md 再按步骤做；原则在适用时读」。
   - 用户输入 `/architect …`、`/tdd …`：把对应 SKILL.md 全文附在这一回合（就像 Cursor / Claude Code 把技能附到消息上）。
   - 智能体自己读 SKILL.md（`fs/read_text_file` 命中技能路径）或调用 MCP `bot_skill_show`，都算「用了这个技能」。
   - 聊天里每条主智能体回答上方显示用过的技能标签（例如「architect」「principle-prove-it-works」），也写进消息记录 `skills_used`。
3. **子智能体与多模型**：pstack 的 `arena` / `swarm` / `architect` 要求按模型列表派多个子智能体。狐狸OS 把「其它 Bot」当作可派的子智能体：主智能体用 `bot_task_delegate` 把一部分交给 Claude Code Bot、另一部分交给 Codex Bot，结果回到主智能体合并。`foxos bot skill models` 写 `~/.agents/pstack-models.md`，把角色映射到 Bot（例如 `arena runners: bot:claude, bot:codex`）。
4. **Claude Code / Codex 自带技能机制**：`foxos bot skill install --harness claude-code|codex|agents` 把 pstack 拷到 `~/.claude/skills/`、`~/.codex/skills/` 或 `~/.agents/skills/`，这样 ACP 背后的 CLI 自己也能发现（它们支持 Agent Skills 时）。

## 4. 实现位置

| 部分 | 位置 |
|---|---|
| Bot 资料 / 对话 / 记忆 / 委托 / 技能命令 | `packages/core/foxos/apps/bot.py`、`packages/core/foxos/bots.py` |
| ACP 客户端（Python，stdio JSON-RPC） | `packages/core/foxos/acp_client.py` |
| ACP 智能体安装、密钥、握手 | `packages/core/foxos/apps/acp.py`、`packages/core/foxos/secrets.py` |
| 本地确定性 ACP 智能体 | `packages/core/foxos/local_agent.py`（`python3 -m foxos.local_agent`） |
| 聊天服务与界面 | `packages/core/foxos/botchat/`（`foxos bot serve`，只监听 127.0.0.1，随机令牌） |
| 操作系统里的窗口 | `scripts/os/bots/foxos-bots`、`foxos-bots.desktop`（开始菜单「智能体」） |
| 伴侣程序 | Electron 的「智能体」应用打开同一个界面 |
| pstack | `packages/core/foxos/data/pstack/` |
| 运行时（Node、Bun、Python、uv、智能体 CLI） | `scripts/os/runtime/manifest.json`、`scripts/os/hooks/35-agent-runtime.sh`、`foxos runtime …`，说明见 [agent-runtime.md](agent-runtime.md) |

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

## 2. Mapping onto FoxOS

See the table in the Chinese section above; every row has the same meaning. In short:

- **Implemented**: bot profiles (name, title, role, font-icon or image avatar, no emoji), one fixed main bot per workspace, backends (any installed ACP agent, the bundled deterministic local agent, or an OpenAI-compatible endpoint), per-bot conversation and memory, per-bot workspace scope enforced on ACP `fs/*` and terminals on top of workspace bounds, locks, audit and takeover; streaming; tool-call cards with diffs, terminal output and plans; approval cards from ACP `session/request_permission`; attachments saved into the workspace and sent as `resource_link`; `@` mentions; typed delegation envelopes with depth 3 and 5-per-turn caps; pstack skills in the `/` menu with "skills used" chips; registry icons for ACP agents.
- **Partial**: subagents (pstack's poteto-agent brief can be attached to a delegation; an ACP agent's own subagents show as tool cards).
- **Gaps**: routines and goals, dictation, "allow for this conversation" persisted rules, automatic learning (depends on non-MIT Intelligence), team sharing (not needed on a single-user OS).

Existing pieces: the Electron agent session panel (one ACP session, permission cards, audit timeline), `acp.js` (Node ACP client), registry install in Electron, the `foxos` CLI/MCP, audit, takeover, workspace bounds, file locks and the light sandbox. Missing before this change: a Python ACP client usable from CLI/MCP and the OS, ACP install from the OS, a secret store, multiple bots with conversations and memory, delegation, pstack, and an OS chat window.

## 3. pstack integration

1. **Shipped** in `packages/core/foxos/data/pstack/skills/` (MIT, `NOTICE`, upstream commit). `foxos bot skill list` reads each front matter and classifies `skill` / `principle` / `subagent`. User skills in `.foxos/skills/<name>/SKILL.md` or `~/.agents/skills/` override by name.
2. **How the main bot uses them**: each turn carries a FoxOS preamble (identity and role, memory, the bots it can delegate to, the skill catalog with absolute SKILL.md paths, and the rule "read SKILL.md first when one applies"). `/architect …` or `/tdd …` attaches that SKILL.md in full. A `fs/read_text_file` on a skill path or an MCP `bot_skill_show` call counts as using it. The chat shows "skills used" chips above the answer and stores them as `skills_used`.
3. **Subagents and multiple models**: other bots act as pstack's subagents. The main bot calls `bot_task_delegate` to hand parts to a Claude Code bot and a Codex bot and merges the results. `foxos bot skill models` writes `~/.agents/pstack-models.md` mapping roles to bots.
4. **Native skill discovery**: `foxos bot skill install --harness claude-code|codex|agents` copies pstack into `~/.claude/skills/`, `~/.codex/skills/` or `~/.agents/skills/` so the CLI behind an ACP agent finds them itself.

## 4. Where it lives

See the table in section 4 above.
