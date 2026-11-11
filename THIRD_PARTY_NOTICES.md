# Third-party notices / 第三方声明

狐狸OS 随附或参考的第三方作品。完整许可证文本随文件分发。

## 随狐狸OS 分发

| 作品 | 版本 | 许可证 | 位置 | 许可证全文 |
|---|---|---|---|---|
| pstack（Lauren Tan） | 上游提交 08547969 | MIT © 2026 Lauren Tan | `packages/core/foxos/data/pstack/`（只有 Markdown：`skills/*/SKILL.md`、`references/`、`playbooks/`、`agents/*.md`） | `packages/core/foxos/data/pstack/NOTICE`；系统里 `/usr/share/doc/foxos/NOTICE.pstack` |
| Tabler Icons（webfont） | 3.51.0 | MIT © 2020-2026 Paweł Kuna | `packages/core/foxos/botchat/static/vendor/tabler/` | 同目录 `LICENSE`；系统里 `/usr/share/doc/foxos/LICENSE.tabler-icons` |

pstack 的技能原文没有改动，里面提到的工具名与编辑器（例如 Cursor 的 `Task`、`AskQuestion`）是上游原文。

## 参考了界面与交互、没有拷贝代码

| 作品 | 许可证 | 说明 |
|---|---|---|
| OpenBot（CopilotKit） | MIT © 2026 CopilotKit | 智能体名册、对话、工具卡片、审批卡片、交接信封、每个智能体的设置、连接器的设计参考了 OpenBot。狐狸OS 的实现是独立编写的，没有拷贝 OpenBot 的源代码或素材。OpenBot 依赖的 CopilotKit Intelligence 不是 MIT 授权，狐狸OS 不使用。如果以后拷贝 OpenBot 代码，需要保留它的 MIT 版权与许可声明。 |

## 镜像里的智能体运行环境

镜像只预装允许再分发的工具（Node.js、Bun、uv、GitHub CLI、Gemini CLI、Codex CLI、codex-acp、Qwen Code、opencode 等），每个工具的许可证与来源见 [docs/agent-runtime.md](docs/agent-runtime.md) 和 `packages/core/foxos/data/runtime-manifest.json`。专有工具（Claude Code、claude-agent-acp、Cursor CLI）不在镜像里，只在用户同意后从厂商官方来源安装。

## 电脑操控 / Computer use

作为依赖在安装时获取（npm 固定版本），镜像预装到 `/usr/lib/foxos/tools/<名字>/`，许可证文件随 npm 包（`node_modules/<名字>/LICENSE`）。狐狸OS 只通过命令行 / JSON 调用它们，没有拷贝源代码。
Installed as pinned npm dependencies (preinstalled in the ISO under `/usr/lib/foxos/tools/<name>/`, license files ship inside each package). FoxOS only calls them as separate processes; no source code is copied.

| 作品 / Work | 版本 / Version | 许可证 / License | 用途 / Use |
|---|---|---|---|
| agent-desktop（Vercel Labs） | 1.2.0 | Apache-2.0 | 默认：桌面无障碍树观察与操作 / default desktop observe & act |
| agent-browser（Vercel Labs） | 0.42.0 | Apache-2.0 | 兜底：网页操作（经 CDP 连自带 Chrome）/ browser-use fallback |
| @playwright/mcp（Microsoft） | 0.0.85 | Apache-2.0 | 给 ACP 智能体的浏览器 MCP / browser MCP for ACP agents (not preinstalled) |
| llama.cpp（ggml-org） | b12284 | MIT | 可选本地模型运行时，按 sha256 下载，不进镜像 / optional local runtime, downloaded with sha256 checks, not in the ISO |
| UI-TARS-1.5-7B（ByteDance Seed）GGUF（Mungert/UI-TARS-1.5-7B-GGUF） | Q4_K_M + q8_0 mmproj | Apache-2.0 | 可选本地视觉定位；权重不进镜像，用户一键下载 / optional; weights never shipped |
| xdotool、scrot | 发行版软件包 / distro packages | BSD-3-Clause / MIT-feh | 截图兜底的键鼠与截图（独立进程）/ screenshot fallback (separate processes) |

托管服务（不分发任何代码）/ Hosted services (nothing redistributed)：TypeSafe Jev（System One API）、DeepSeek API。密钥只在本机密钥库，不进镜像。
