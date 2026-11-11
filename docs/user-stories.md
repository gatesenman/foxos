# 用户故事：智能体（US-100 起）

[English](#english)

每个故事都有自动测试（`scripts/stories.json` 里登记了它对应的测试）。这一段从 US-100 开始编号，是为了不和主线、其他分支已经用掉的 US-62、US-63 冲突。

| 故事 | 内容 | 测试 |
|---|---|---|
| US-100 | 智能体：主智能体与多个智能体的创建、复制、改名、删除 | `packages/core/tests/test_bots.py`：`test_US100_…` |
| US-101 | 每个智能体的设置（对照 OpenBot 逐项）：名称、头像、说明、模型、ACP 智能体、范围、权限；密钥不外露 | `packages/core/tests/test_bots.py`：`test_US101_…` |
| US-102 | 真实 ACP 回合：工具调用卡片、审批（允许/拒绝）、diff、终端输出，审计记下是哪个智能体 | `packages/core/tests/test_bots.py`：`test_US102_…` |
| US-103 | @提及与委托：主智能体把任务交给别的智能体，结果在范围内汇报回来 | `packages/core/tests/test_bots.py`：`test_US103_…` |
| US-104 | pstack 技能：发现、显示、在对话中运行 | `packages/core/tests/test_bots.py`：`test_US104_…` |
| US-105 | 智能体记忆与例程（定时任务） | `packages/core/tests/test_bots.py`：`test_US105_…` |
| US-106 | 只暂停一个智能体与人工接管 | `packages/core/tests/test_bots.py`：`test_US106_…` |
| US-107 | 聊天服务：令牌鉴权、发送、SSE 流、重开时回放进行中的回合 | `packages/core/tests/test_bots.py`：`test_US107_…` |
| US-108 | 聊天界面：真实浏览器里发送、审批、中英文切换 | `packages/core/tests/test_bots.py`：`test_US108_…` |
| US-109 | 连接器目录与 stdio MCP 连接器，按智能体授权 | `packages/core/tests/test_connectors.py`：`test_US109_…` |
| US-110 | OAuth 2.1 连接器：发现（RFC 9728/8414）、PKCE、动态注册、刷新，写操作需审批 | `packages/core/tests/test_connectors.py`：`test_US110_…` |
| US-111 | Bearer 令牌连接器：错误令牌不算连上，密钥从不写进日志 | `packages/core/tests/test_connectors.py`：`test_US111_…` |
| US-112 | 免密钥的托管连接器真实调用 | `packages/core/tests/test_connectors.py`：`test_US112_…` |
| US-113 | 多机配对：一次性配对码、证书指纹、双向 TLS（令牌被偷也连不上） | `packages/core/tests/test_machines.py`：`test_US113_…` |
| US-114 | 一个智能体控制两台狐狸OS：默认拒绝、按机器授权、两边审计写明控制端与智能体 | `packages/core/tests/test_machines.py`：`test_US114_…` |
| US-115 | 多个智能体共用一台狐狸OS：范围与应用授权、LOCKED、CONFLICT、只暂停一个、撤销授权 | `packages/core/tests/test_machines.py`：`test_US115_…` |
| US-116 | 从官方发布地址安装第三方 ACP 智能体（sha256 校验）并真实握手；智能体设置与更新检查 | `packages/core/tests/test_acp_real.py`：`test_US116_…` |
| US-117 | 镜像阶段运行环境：以用户 foxos 检查预装版本、PEP 668、专有智能体不进镜像 | `packages/core/tests/test_os_runtime.py`：`test_US117_…` |
| US-118 | 镜像里预装的 ACP 智能体已登记，以用户 foxos 真实握手 | `packages/core/tests/test_os_runtime.py`：`test_US118_…` |
| US-119 | 主智能体用 DeepSeek（服务商预设，密钥在密钥库）真实回答 | `packages/core/tests/test_bots_deepseek.py`：`test_US119_…` |
| US-120 | 主智能体用工具委托给 opencode 编码智能体（DeepSeek），改文件前人批准，卡片带 diff | `packages/core/tests/test_bots_deepseek.py`：`test_US120_…` |
| US-121 | 人拒绝真实代理的编辑：文件不变，卡片记为拒绝 | `packages/core/tests/test_bots_deepseek.py`：`test_US121_…` |
| US-122 | 真实模型回合里用 pstack 技能 | `packages/core/tests/test_bots_deepseek.py`：`test_US122_…` |
| US-123 | 真实模型的智能体读另一台狐狸OS 上的目录，对方审计写明控制端 | `packages/core/tests/test_bots_deepseek.py`：`test_US123_…` |
| US-124 | Qwen Code 经 OpenAI 兼容地址接 DeepSeek，写文件经狐狸OS 内核 | `packages/core/tests/test_bots_deepseek.py`：`test_US124_…` |
| US-125 | 智能体窗口：新建并配置智能体（含 DeepSeek 服务商预设） | `apps/desktop/e2e/bots.e2e.mjs`：`US-125` |
| US-126 | 智能体窗口：真实 opencode 回合，编辑卡片带 diff，点允许后文件改了 | `apps/desktop/e2e/bots.e2e.mjs`：`US-126` |
| US-127 | 智能体窗口：点拒绝，文件不变 | `apps/desktop/e2e/bots.e2e.mjs`：`US-127` |
| US-128 | 智能体窗口：@ 委托给第二个智能体，在审批页批准 | `apps/desktop/e2e/bots.e2e.mjs`：`US-128` |
| US-129 | 智能体窗口：/ 技能菜单与用过的技能 | `apps/desktop/e2e/bots.e2e.mjs`：`US-129` |
| US-130 | 智能体窗口：添加真实的本地 MCP 连接器（HTTP + Bearer）并列出工具 | `apps/desktop/e2e/bots.e2e.mjs`：`US-130` |
| US-131 | 停靠窗口占住屏幕边（`_NET_WM_STRUT_PARTIAL`），最大化窗口不被盖住，取消停靠后释放 | `apps/desktop/e2e/bots.e2e.mjs`：`US-131` |
| US-132 | 智能体窗口：配对第二台狐狸OS 并在聊天里切换机器 | `apps/desktop/e2e/bots.e2e.mjs`：`US-132` |
| US-133 | 智能体窗口：人工接管让智能体的编辑停下（卡片记为接管），交还后恢复 | `apps/desktop/e2e/bots.e2e.mjs`：`US-133` |
| US-134 | 宿主应用里的智能体只在狐狸OS 虚拟电脑里动手；宿主执行要人明确打开（`foxos bot host-access enable`）并逐个确认 | `packages/core/tests/test_hostguard.py`：`test_US134_…` |

说明：

- US-102–US-108 用仓库自带的本地 ACP 智能体（`python3 -m foxos.local_agent`，一个真实的 ACP stdio 进程，按规则回答，不需要模型账号）。这样每一步（工具卡片、审批、diff、委托、技能）都能在测试里确定地重现。
- US-112 会真实调用 Exa 的免密钥 MCP 服务；US-116 会从 GitHub 下载 opencode。没有网络时这两个跳过。
- US-117、US-118 要先运行 `sudo scripts/os/tools/agent-overlay.sh up`，在镜像 chroot 的 overlay 里检查；没挂载时跳过。
- US-119–US-124 用真实模型（DeepSeek 的 OpenAI 兼容接口）跑回答。密钥从 `~/.secrets/deepseek_api_key`（或 `FOXOS_TEST_DEEPSEEK_KEY_FILE`）读取，只经标准输入存进测试自己的密钥库；没有密钥文件时这些用例**跳过**（不算失败），所以没有密钥的 CI 仍然是绿的。
- US-125–US-133 在自己的 Xvfb + xfwm4 桌面里打开真实的智能体窗口（Chrome 应用模式），用 Playwright 经 CDP 点界面。代码智能体是 opencode：有 DeepSeek 密钥时用 `deepseek/deepseek-flash`，没有时用 opencode 的默认免费模型（不需要密钥，但 opencode 对免费用量有上限，用完会报 “Free usage limit reached”）。
- 真实的 Gemini、Codex、Claude、Cursor 测到的是 ACP 握手和会话建立，见 [agent-runtime.md](agent-runtime.md)。

---

<a id="english"></a>

# User stories: bots (US-100 onward)

Every story has an automated test, and `scripts/stories.json` maps each story to its test. The block starts at US-100 because main and other branches already use US-62 and US-63.

- US-100–US-108: bots, settings, ACP turns, delegation, pstack, memory, routines, pause, the chat service and the UI. They use the repo's local ACP agent, a real stdio process that needs no model account.
- US-109–US-112: connectors. US-112 is a live call to Exa.
- US-113–US-115: multiple machines with two real `machine serve` hosts.
- US-116: opencode is downloaded, checked against its sha256, and completes a real ACP handshake.
- US-117–US-118: the ISO runtime, checked as user `foxos` in an overlay of the image chroot.
- US-119–US-124: real model turns through DeepSeek's OpenAI-compatible API: the main bot answers, delegates to an opencode code bot that edits a file after a person approves (the card carries the diff), a denied edit leaves the file alone, a pstack skill, a read on a second FoxOS machine, and Qwen Code pointed at DeepSeek. The key is read from `~/.secrets/deepseek_api_key` (or `FOXOS_TEST_DEEPSEEK_KEY_FILE`) and only goes into the test's own secret store over stdin. Without the key file these tests are skipped, not failed.
- US-134: on a host app (the Windows companion and other non-FoxOS systems), bots act only inside the FoxOS virtual computer. Host execution needs a person to turn it on, and then a confirmation for every action that isn't read-only.
- US-125–US-133: the real bots window (Chrome app mode) on its own Xvfb + xfwm4 desktop, driven with Playwright over CDP: create and configure bots, approve and deny real opencode edits, @ delegation, `/` skills, a real local MCP connector, docking with a reserved screen edge, pairing a second machine, and takeover. The code bots use `deepseek/deepseek-flash` when the key file exists and opencode's default free model otherwise (no key, but opencode caps free usage).
