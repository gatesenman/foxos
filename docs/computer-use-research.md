# 电脑、浏览器、命令行操控：开源技术调研与狐狸OS 的选型

> 中文在前，English below。调研时间 2026-11。所有数字都注明来源；我们自己测的数字来自本仓库的真实端到端测试
> （`docs/test-report.md`，`docs/test-results/cu-bench.json`）。

## 结论（先看这个）

**默认栈：agent-desktop（观察 / 操作）+ TypeSafe Jev（System 1 单步策略）+ DeepSeek（System 2 规划器）。**
两条兜底只在 agent-desktop 读不到目标时自动启用，也可以按机器人设置或命令行手动指定：

| 路径 | 什么时候用 | 观察 | 动作 | 谁选下一步 |
|---|---|---|---|---|
| **默认：agent-desktop** | 桌面程序（GTK / Qt / Electron，有无障碍树） | agent-desktop 无障碍快照 → 编号元素表（≤255） | agent-desktop 按引用点击 / 填写 / 选择 / 滚动 / 按键 | Jev（Choice，带置信度）；没 TypeSafe 密钥自动退到 DeepSeek flash JSON |
| 兜底：computer use（截图） | 程序没有无障碍信息（0 个可操作元素 / 快照失败），或 `--surface screen` | 屏幕截图 | xdotool 坐标点击 / 键盘输入 / 按键 | Jev（Choice + Box 定位，一次请求）；无密钥时 DeepSeek 选动作 + 视觉定位（deepseek-flash 视觉 / 可选本地 UI-TARS-1.5-7B） |
| 兜底：browser use | 目标是网页而 agent-desktop 读不到网页内容（Chrome 不在无障碍树里），或 `--surface browser` / `foxos browser task` | Chrome CDP 无障碍快照（编号元素） | agent-browser 0.42.0（装了就用，经 `--cdp` 连狐狸OS 自带 Chrome）或内置 CDP | 同上 |

置信度分级（三条路径共用）：≥0.85 直接执行；0.55–0.85 执行后核对（界面是否变化 / 文字是否到位）；<0.55 或连续失败 → 交给规划器亲自走一步。
删除、发送、支付、提交、安装等破坏性动作不论置信度都要人批准；每一步的延迟、置信度、是否升级写进任务日志和审计日志。

本地视觉模型只保留 **UI-TARS-1.5-7B**（可选，一键安装，默认不装）；模型服务商只保留 **DeepSeek** 和 **TypeSafe**。

## 1. 调研范围与候选

### 1.1 桌面观察 / 操作层

| 项目 | 许可 | 做法 | 结论 |
|---|---|---|---|
| **vercel-labs/agent-desktop**（npm `agent-desktop` 1.2.0） | Apache-2.0 | 原生命令行，读系统无障碍树（Linux AT-SPI），稳定引用 `@sid:eN`，JSON 信封，按引用操作；多窗口时报 AMBIGUOUS_TARGET | **选用（默认）**。在本机 Debian 13 + XFCE 上：status 0.14 s，snapshot ≈0.3 s。适配层 `foxos/cu/agent_desktop.py` 处理多窗口（对话框优先、引用加 `w2` 前缀） |
| 自写 AT-SPI（pyatspi） | LGPL 依赖 | 之前的 a11y.py | 删掉，agent-desktop 更完整、更快 |
| xdotool + scrot | BSD 类 / GPL（独立进程） | 坐标点击、键盘、截图 | 保留为兜底（computer use） |
| Anthropic computer use / OpenAI CUA | 专有 API | 截图 → 托管模型 → 坐标 | 不集成（专有、贵、不能本地） |
| Open Interpreter OS mode、Agent S2/S3 | AGPL / Apache | 完整智能体框架 | 不集成：我们只要观察 / 操作层，规划用自己的 S1/S2 |

### 1.2 浏览器

| 项目 | 许可 | 结论 |
|---|---|---|
| 内置 CDP（`foxos/cu/cdp.py`） | 本仓库 | 默认浏览器实现：无障碍快照编号元素、点击、填写、按键、下载 |
| **vercel-labs/agent-browser** 0.42.0 | Apache-2.0 | **选用（browser use 后端，装了就用）**：Rust 原生命令行 + 守护进程，`--cdp` 连现有 Chrome，引用 `@eN`，遮挡 / 隐藏 / 禁用时报错而不是点错，自带 `mcp` 服务器。注意：切标签会清掉引用（适配层只在需要时切）；不点视口外元素（适配层先 scrollintoview） |
| Microsoft Playwright MCP 0.0.85 | Apache-2.0 | 保留为给 ACP 智能体用的外部 MCP 引擎 |
| browser-use | MIT | 评估后不集成：真实测试 238 s 仍「extraction timed out」，Python 依赖重 |
| Chrome DevTools MCP | Apache-2.0 | 不集成（与内置 CDP 重复） |

### 1.3 单步决策（System 1）

| 候选 | 做法 | 结论 |
|---|---|---|
| **TypeSafe Jev**（`jev-1.14.0`，托管 System One API） | `POST /v1/systemone`：Choice（≤255 选项，返回选项 + 校准置信度 + 概率）、Score、Noul、**Box（图片定位，1.14 起）**；输入可含 PNG/JPEG。价格 $0.042 / 百万输入 token，输出免费（typesafe.ai/pricing） | **默认 S1**。实测：GET /v1/models 200（114 ms），Choice 200（78–128 ms）；一步决策（action + key + target 三问并行）≈100–150 ms |
| DeepSeek flash（关闭思考 + JSON + logprobs） | 置信度 = 所选 action / target / key 那几个 token 的概率乘积 | 没 TypeSafe 密钥时的自动回退；≈1 s 一步 |
| 本地约束解码（llama.cpp grammar） | 需要本地大模型 | 不做：机器内存不够，收益不明 |

### 1.4 视觉定位（只在 computer use 兜底里用）

| 模型 | 许可 | 公开分数 | 结论 |
|---|---|---|---|
| **UI-TARS-1.5-7B**（ByteDance Seed） | Apache-2.0 | ScreenSpot-Pro 49.6，OSWorld 27.4（官方模型卡；Holo2 模型卡复测 ScreenSpot-Pro 39.0） | **唯一的可选本地模型**：`foxos model install ui-tars-1.5-7b`（GGUF Q4_K_M 4.78 GB + mmproj 0.85 GB，断点续传 + sha256，国内优先魔搭），`foxos model run`（llama.cpp b12284 / vLLM）。默认不装 |
| Jev Box | 托管 | 我们在 1440×900 截图上实测：4 个目标中 3 个落在目标内（「Save」与「Save As」相邻时选错） | 有密钥时 computer use 的默认定位 |
| deepseek-flash 视觉 | 托管 | 官方价格页标注支持 Vision | 无 Jev 密钥时的托管定位 |
| GUI-Owl、OS-Atlas、ShowUI、OmniParser 等 | 多为 Apache / MIT / AGPL | — | 不再集成（少而精）。OmniParser 代码保留为可选定位后端但不推荐 |

### 1.5 命令行

`foxos shell`：工作空间内的持久 shell 会话（运行、读输出、发送输入、中断），走同样的审计、接管和越界检查；MCP 工具 `shell_*`。

## 2. 实测（本机 Debian 13 + Xvfb XFCE，真实 Jev / DeepSeek）

见 `docs/test-report.md` 的 US-120 起，以及下面的基准表（`python3 scripts/cu_bench.py` 生成）。

<!-- BENCH -->

## 3. 许可

agent-desktop、agent-browser、Playwright MCP 在安装时作为依赖（npm 固定版本）获取，ISO 预装到 `/usr/lib/foxos/tools`，
许可证随包；llama.cpp（MIT）运行时按 sha256 下载；UI-TARS 权重（Apache-2.0）不进 ISO，用户自己一键下载。
xdotool / scrot 是独立进程，不复制代码。见 `THIRD_PARTY_NOTICES.md`。

---

# Computer, browser and shell control: open-source survey and FoxOS choices (English)

## Bottom line

**Default stack: agent-desktop (observe/act) + TypeSafe Jev (System 1 step policy) + DeepSeek (System 2 planner).**
Two fallbacks are used automatically only when agent-desktop cannot read the target, and can be chosen per bot (bot settings → computer use) or per call (`--surface`):

| Path | When | Observation | Actions | Step choice |
|---|---|---|---|---|
| **Default: agent-desktop** | Desktop apps with an accessibility tree | agent-desktop snapshot → numbered elements (≤255) | agent-desktop ref click / fill / select / scroll / keys | Jev Choice with calibrated confidence; DeepSeek-flash JSON when no TypeSafe key |
| Fallback: computer use (screenshot) | No accessible elements / snapshot fails, or `--surface screen` | Screenshot | xdotool click at point / type / keys | Jev Choice + Box in one request; without a key DeepSeek picks the action and a vision model grounds it (deepseek-flash vision or optional local UI-TARS-1.5-7B) |
| Fallback: browser use | Web target that agent-desktop cannot read (Chrome not in the a11y tree), or `--surface browser` / `foxos browser task` | Chrome CDP accessibility snapshot | agent-browser 0.42.0 (when installed, attached via `--cdp`) or built-in CDP | same |

Gating for all three: ≥0.85 execute; 0.55–0.85 execute then verify; <0.55 or repeated failures escalate to the planner. Destructive actions always need human approval. Every step's latency, confidence and escalation goes to the task log and the audit log.

Only one optional local vision model is kept (**UI-TARS-1.5-7B**, one-click, not installed by default) and two providers (**DeepSeek**, **TypeSafe**).

## Candidates

- **Desktop layer:** agent-desktop 1.2.0 (Apache-2.0) chosen; our own AT-SPI helper removed; xdotool/scrot kept as the screenshot fallback; Anthropic/OpenAI computer-use APIs, Open Interpreter and Agent S not integrated.
- **Browser:** built-in CDP plus **agent-browser 0.42.0** (Apache-2.0) as the browser-use backend; Playwright MCP kept for ACP agents; browser-use dropped (real run: 238 s, extraction timed out); Chrome DevTools MCP not integrated.
- **System 1:** **TypeSafe Jev 1.14** (hosted; Choice ≤255 options with confidence, Score, Noul, Box image grounding; $0.042 per million input tokens, output free). Measured: models 200 in 114 ms, Choice 200 in 78–128 ms; one step decision ≈100–150 ms. DeepSeek-flash (thinking disabled, JSON, logprob confidence) is the automatic fallback.
- **Vision grounding (fallback only):** UI-TARS-1.5-7B (Apache-2.0; ScreenSpot-Pro 49.6, OSWorld 27.4 per the model card) as the optional local model; Jev Box when a key exists (we measured 3 of 4 targets hit on a 1440×900 screenshot; it confused adjacent "Save"/"Save As"); deepseek-flash vision otherwise.
- **Shell:** `foxos shell` persistent sessions with audit, takeover and workspace bounds.

## Measurements

See `docs/test-report.md` (US-120+) and the benchmark table above (`scripts/cu_bench.py`).

## Licenses

agent-desktop, agent-browser and Playwright MCP are installed as pinned npm dependencies (preinstalled in the ISO under `/usr/lib/foxos/tools`); llama.cpp (MIT) is downloaded with sha256 checks; UI-TARS weights are never shipped. xdotool/scrot run as separate processes. See `THIRD_PARTY_NOTICES.md`.
