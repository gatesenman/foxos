# 智能体运行环境（Node、Bun、Python、命令行工具、ACP 智能体）

[English](#english)

狐狸OS 给智能体准备好常用的运行环境和编码智能体命令行。清单只有一份：`packages/core/foxos/data/runtime-manifest.json`，固定版本、写明许可证与官方来源，下载按 sha256 校验（厂商不发布校验和的，记录下载到的 sha256 并显示出来）。

## 1. 三个阶段

| 阶段 | 什么时候装 | 装到哪里 | 规则 |
|---|---|---|---|
| `iso` | 构建镜像时（`scripts/os/hooks/35-agent-runtime.sh` 运行 `python3 -m foxos.runtime install --phase iso --system`） | `/usr/local`、`/usr/lib/foxos/runtime`，ACP 登记在 `/usr/lib/foxos/agents` | 只放**允许再分发**的工具 |
| `firstboot` | 用户第一次登录（`foxos-runtime-firstboot`，自动启动） | 当前用户：`~/.local/share/foxos/runtime`，链接到 `~/.local/bin`，ACP 登记在 `~/.local/share/foxos/agents` | 可再分发的直接装；**专有的先弹窗问用户**，同意才从官方来源下载（`--accept-license`） |
| `optional` | 用户需要时 | 同上 | `foxos runtime install go rust` |

## 2. 清单

| 工具 | 版本 | 阶段 | 许可证 | 来源 |
|---|---|---|---|---|
| Node.js LTS | 24.22.2 | iso | MIT | nodejs.org 官方二进制 |
| npm、Corepack | 随 Node | iso | Artistic-2.0、MIT | 随 Node |
| pnpm | 12.18.0 | iso | MIT | npm |
| Bun | 1.4.4 | iso | MIT | GitHub 发布 |
| Python 3、pip、pipx | Ubuntu 24.04 | iso | PSF-2.0、MIT | Ubuntu 软件源 |
| uv / uvx | 0.13.7 | iso | MIT OR Apache-2.0 | GitHub 发布 |
| GitHub CLI | 2.103.3 | iso | MIT | GitHub 发布 |
| git、curl、wget、jq、ripgrep、fd、build-essential、unzip、sqlite3 | Ubuntu 24.04 | iso | 各自的自由许可证 | Ubuntu 软件源 |
| Gemini CLI（带 ACP） | 0.68.0 | iso | Apache-2.0 | npm `@google/gemini-cli` |
| Codex CLI | 0.167.1 | iso | Apache-2.0 | npm `@openai/codex` |
| codex-acp | 2.6.0 | iso | Apache-2.0 | npm |
| Qwen Code（带 ACP） | 0.27.2 | iso | Apache-2.0 | npm |
| opencode（带 ACP） | 2.2.7 | iso | MIT | GitHub 发布 |
| agent-desktop（Vercel，电脑操作；与 Jev 一起是默认的 computer-use 栈） | 1.2.0 | iso | Apache-2.0 | npm `agent-desktop`（官方预编译 linux-x64 二进制；声明见 `/usr/share/doc/foxos/NOTICE.agent-desktop`） |
| Aider | 0.86.2 | firstboot | Apache-2.0 | PyPI（uv tool；体积大、依赖多，不进镜像） |
| Claude Code | 2.1.322 | firstboot | 专有（Anthropic 商业条款） | npm，用户同意后 |
| claude-agent-acp | 0.106.0 | firstboot | 专有（注册表元数据） | GitHub 发布，用户同意后 |
| Cursor CLI（cursor-agent） | 2026.11.05-86047df | firstboot | 专有 | 厂商下载地址，用户同意后；厂商不发布校验和 |
| Go | 1.27.4 | optional | BSD-3-Clause | go.dev |
| Rust | rustup 1.30.0 / stable | optional | MIT OR Apache-2.0 | rustup.rs |

**专有智能体永远不放进镜像。**

## 3. 命令

- `foxos runtime list [--phase …] [--group …]`：每个工具的版本、是否装好、许可证、来源。
- `foxos runtime doctor`：镜像阶段缺了什么、`~/.local/bin` 是否在 PATH、PEP 668、磁盘空间、首次登录还没装的。
- `foxos runtime install NAME… [--force] [--accept-license]`：装到当前用户。专有工具不带 `--accept-license` 时返回 PERMISSION_DENIED。
- `foxos acp agent list/show/install/uninstall/login/probe`：ACP 智能体；`probe` 真实走 initialize + session/new。
- `foxos acp agent config AGENT [--model] [--mode] [--arg=…] [--env K=V] [--clear]`：每个 ACP 智能体的默认设置。变量名像密钥（含 KEY/TOKEN/SECRET/PASSWORD）的会被拒绝，密钥请用 `foxos acp key set`。
- `foxos acp agent update [AGENT] [--all] [--check] [--accept-license]`：对比在线 ACP 注册表，新版本装到当前用户目录；离线返回 DEPENDENCY_MISSING。

## 4. Python 与 PEP 668

系统 Python 是「外部管理」的（`EXTERNALLY-MANAGED`），`pip install` 到系统会被拒绝，这是有意的。智能体装 Python 包请用：

- `uv venv && uv pip install …` 或 `python3 -m venv .venv`
- 命令行工具用 `pipx install …` 或 `uv tool install …`

狐狸OS 自己的依赖（python-pptx、zstandard）在 `/usr/lib/foxos/venv`（`--system-site-packages`），`/usr/bin/foxos` 用这个 venv 运行。

## 5. 验证

在镜像 chroot 的 overlay 里（`scripts/os/tools/agent-overlay.sh up`，跑的是同一份 hook 30/35，不改共享 chroot），以普通用户 `foxos` 检查（`tests/test_os_runtime.py`，US-117、US-118）：node v24.22.2、pnpm 12.18.0、bun 1.4.4、uv 0.13.7、gh 2.103.3、gemini 0.68.0、codex-cli 0.167.1、qwen 0.27.2、opencode 2.2.7；`runtime doctor` 正常；PEP 668 生效。首次登录阶段：aider 0.86.2 装进 `~/.local/bin`；同意条款后 Claude Code 2.1.322、claude-agent-acp 0.106.0、Cursor CLI 2026.11.05 安装成功。

ACP 握手（以 foxos 用户，没有任何账号）：

| 智能体 | 协议版本 | 结果 |
|---|---|---|
| Gemini CLI 0.68.0 | 1 | 需要登录（oauth-personal / gemini-api-key / vertex-ai） |
| codex-acp 2.6.0 | 1 | 需要登录（api-key / chat-gpt） |
| Qwen Code 0.27.2 | 1 | 需要登录（openai） |
| opencode 2.2.7 | 1 | 会话建立成功 |
| claude-agent-acp 0.106.0 | 1 | 会话建立成功（实际回答需要账号） |
| Cursor CLI | 1 | 需要登录（cursor_login） |

没有用任何真实模型账号跑过回答。

---

<a id="english"></a>

# Agent runtime

There is one manifest, `packages/core/foxos/data/runtime-manifest.json`. It pins each tool's version and records its license and official source. Downloads are checked against their sha256.

- **iso phase**: redistributable tools only, baked in by `scripts/os/hooks/35-agent-runtime.sh`. These are Node 24.22.2, pnpm, Bun, uv, gh, Python with pip and pipx, the common CLIs, and the Gemini CLI, Codex CLI with codex-acp, Qwen Code and opencode agents.
- **firstboot phase**: runs at first login (`foxos-runtime-firstboot`). Aider installs directly. The proprietary tools (Claude Code, claude-agent-acp, Cursor CLI) install only after the user agrees in a dialog, and always come from the vendor. They are never redistributed in the ISO.
- **optional phase**: Go and Rust, on request.

Commands:

- `foxos runtime list/doctor/install`
- `foxos acp agent config` sets the default model, mode, args and env. Secret-looking env names are rejected; use `foxos acp key set` for keys.
- `foxos acp agent update` checks for and installs updates.

The system Python is PEP 668 externally-managed. Use `uv`, `venv` or `pipx` instead. FoxOS's own dependencies live in `/usr/lib/foxos/venv`.

Verified as user `foxos` in an overlay of the image chroot (US-117, US-118). The real ACP handshake results are in the table above. No real model account was used.
