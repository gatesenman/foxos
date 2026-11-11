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
