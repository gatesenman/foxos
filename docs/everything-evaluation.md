# Everything 首批应用代码级评估（狐狸OS / FoxOS 阶段 0）

- 评估对象：https://github.com/HeyPuter/everything ，浅克隆提交 `0fbb88cdee2f54c94a9d2c975f43322888813c5d`（提交时间 2026-11-10 14:27，UTC+8）
- 评估日期：2026-11-10（UTC+8）
- 评估环境：Linux 盒子，Node v24.22.1，npm 11.21.1，Google Chrome 156（无头截图），LibreOffice（只用作独立校验工具）
- 原则：下文结论凡标「已验证」均为本次实际运行；标「未验证」的只依据代码或 README 阅读。命令前缀 `foxos` 为拟设计命令，Everything 中不存在。

## 1. 核心结论

1. 三个应用都能 `npm ci` + `npm run build` 一次成功，而且核心逻辑都能在 Node 中无头调用：表格（`src/core` + `aitools.js` 43 个工具）和演示（`lib/pptx` TypeScript 引擎）完成度最高，文档（`src/engine`）可读写 docx，但缺少面向智能体的工具层。
2. **最大风险是许可证**：仓库根目录是 MIT，但 Spreadsheet 和 Presentation 自己声明 **AGPL-3.0-only**（全仓共 12 个应用声明 AGPL）。只有 Documents 是 MIT。进入开发前必须先定好许可策略。
3. 三个应用都绑定 Puter 云：文件读写走 `puter.fs`，AI 走 `puter.ai`，SDK 从 `https://js.puter.com/v2/` 加载。断网时，Documents 和 Spreadsheet 的主页面直接停在「Could not reach Puter」；Presentation 和 Documents 的 playground 可以离线打开。要被狐狸OS承载，必须替换存储和 AI 适配层。
4. PDF/图片导出是共同短板：表格的无头 PDF 不画图表，中文会变成「?」；文档和演示的 PDF 依赖浏览器 Canvas 渲染，需要在外壳中用隐藏窗口渲染。
5. 三个首批应用可各自独立打包分发（tar.gz：文档 18 MB、表格 5.5 MB、演示 2.1 MB），适合做安装器的可选组件；第三方编码智能体可通过 ACP Registry（45 个已认证智能体）一键安装接入。
6. 建议阶段 0 的顺序是：先由法务定 AGPL 策略；同时先做表格 CLI（复用度最高），再做演示 CLI（优先评估直接使用 MIT 的上游 office-kit/pptx），然后做文档 CLI；最后接入外壳和本地存储。

## 2. 仓库整体概况

| 项目 | 情况 |
|---|---|
| 应用数 | `src/` 下 51 个应用目录（办公、协作、创意、工程、业务、开发工具、游戏等） |
| 结构 | 单仓多应用，**无根 package.json / workspace**；51 个目录各自有 `package.json` 和 `package-lock.json`，可独立安装、构建、部署 |
| 技术形态 | 均为 Vite 构建的纯前端 Web 应用（原生 JS，无框架），产物是静态 `dist/`；`amplify.yml` 把每个目录作为独立 AWS Amplify 应用部署 |
| 共享代码 | 仅 `dev/puter-localhost.mjs`（开发服务器插件）；应用之间不共享运行时代码 |
| 后端 | 统一用 Puter.js（云文件、KV、登录、AI、Worker）；协作服务以 Puter Worker 形式部署 |
| 运行要求 | Node ≥ 22.12（Presentation ≥ 22.18） |
| 体量 | 克隆约 1.9 GB、36,707 个文件 |
| 许可 | 根目录为 MIT；以下 12 个应用自带 AGPL 声明：3d、building-design、cad、circuits、email、notes、parametric（其 LICENSE 首行为自定义版权声明，需单独核实）、pdf、presentation、spreadsheet、video-studio、whiteboard |

### 候选应用与推荐

| 类别 | 候选目录 | 许可 | 结论 |
|---|---|---|---|
| 文档 | `src/documents`（Word 替代，docx） | MIT | **推荐** |
| 文档 | `src/notes`（笔记本） | AGPL | 不是 docx 文档，不推荐 |
| 文档 | `src/wiki`（页面/数据库） | 未单独声明（按根目录 MIT） | 不是 docx 文档，可作后续知识库 |
| 表格 | `src/spreadsheet`（Excel 替代，xlsx） | AGPL | **推荐**（功能最强，但需处理许可） |
| 表格 | `src/records`（Airtable 替代） | MIT | 数据库型，不读写 xlsx，可作备选 |
| 演示 | `src/presentation`（PowerPoint 替代，pptx） | AGPL（内含 MIT 的 lib/pptx） | **推荐**（唯一候选） |

## 3. 实测记录

| 步骤 | Documents | Spreadsheet | Presentation |
|---|---|---|---|
| `npm ci` | 成功（182 包，约 2 秒） | 成功（95 包） | 成功（115 包，postinstall 打 fflate 补丁成功） |
| `npm run build` | 成功；prebuild 许可检查通过（205 个锁定包，无 AGPL） | 成功 | 成功（有 chunk 体积警告） |
| `dist` 体积 | 34 MB（字体 17 MB） | 13 MB | 5.0 MB |
| 联网时 UI（Chrome 无头截图） | 正常显示编辑器 | 正常显示表格与 Assistant 面板 | 正常显示编辑器与 Assistant 面板 |
| 断网时 UI（屏蔽外网） | 主页面停在「Could not reach Puter」；`playground.html` 正常 | 停在「Could not reach Puter」 | 正常显示编辑器 |
| Node 无头 PoC | 创建 docx → 设 Heading1 → 加粗 → 插入段落 → 导出 → 重新打开，文本和样式都保留；LibreOffice 读出正确文本 | 新建工作簿 → write_cells → SUM 公式 → calculate → create_chart → 加粗 → 导出 xlsx → 重新打开（公式和图表都在）；LibreOffice 读出正确值；无头 PDF 可生成 | 新建 pptx → 标题页 → 文本框 → 柱状图 → 表格 → 保存 → 重新打开（2 页）；LibreOffice 转出 2 页 PDF，图表正常 |
| 单元测试（抽样） | `canvas-styles.test.js` 15/15 通过 | `aitools*` + `io*` 共 439 个测试文件、3,972 个用例全部通过 | `slide-deck.test.ts` + `tables.test.ts` 8/8 通过（全量测试因超时中断，未完成） |

## 4. 逐应用评估

### 4.1 Documents（`src/documents`）

**1）技术栈、依赖、许可、启动**
- 原生 JS + Vite 8，自研 Canvas 排版引擎（`src/engine/`，402 个文件）；源码 714 个 JS 文件、约 11.2 万行，1,163 个测试文件。
- 运行时依赖：fflate、@zip.js/zip.js、yjs（协作）、mdast/micromark（Markdown）、opentype.js、rtf.js、utif、nspell、bidi-js、lucide。
- 许可：应用为 MIT；`AGENTS.md` 明确禁止引入 AGPL；`tools/check-licenses.mjs` 在构建前自动检查（本次通过）。字体为 Noto Sans 等 OFL-1.1。依赖许可以元数据声明为准，**未做源码级审计**。
- 启动：`npm ci && npm run dev`（端口 5173），或构建后 `vite preview`。

**2）文件格式与存储**
- 原生格式 docx（`src/engine/docx.js` 的 `DocxPackage`），会保留未改动的包部件。可导入 txt / Markdown / HTML；可导出 docx、PDF（浏览器渲染）。
- 存储：`src/lib/puter.js` 调 `puter.fs.read/write`（Puter 云）；本地草稿用 localStorage / IndexedDB；协作用 Yjs + Puter Worker。
- 限制（README 原文）：这是受限的编辑器原型；字段、批注、修订、多节、嵌套表格、浮动图片等结构可能被拒绝编辑或只读打开。README 的功能列表同时又写了支持批注和修订，前后不一致，**需用真实文件实测**。

**3）业务逻辑与 UI 分离**
- 分离良好，AGENTS.md 要求「模型变更、DOCX 序列化、排版、绘制」分开。
- 可无头调用（已验证）：`src/engine/model.js`（`TextDocument`：段落样式、格式、表格、列表、批注、书签等）、`src/engine/docx.js`（`createDocx`、`DocxPackage.open/export`）。Node 中只需用 jsdom 注入 `DOMParser` / `XMLSerializer`。
- 可能可无头调用（未验证）：`src/lib/document-export.js`（`documentMarkdown` / `documentHtml` / `documentPlainText`）、`src/lib/import-markdown-blocks.js`、`src/engine/layout.js`（需要提供测量函数）。
- 依赖浏览器：`src/lib/pdf-export.js`（逐页 Canvas → JPEG + 隐藏文本层）、`src/engine/canvas-editor.js`。
- 图表：`src/engine/chart-builder.js` 能生成 DrawingML 图表 XML（14 种类型），但插入流程写在 UI 的 `src/views/insert-chart.js` 中。

**4）已有 CLI/API/插件接口**：无 CLI；没有 function-calling 工具集（`src/lib/assistant.js` 只是基于提示词的改写/总结）；`playground.html` 是不需要账号的本地评估页面。

**6）外壳承载**：`base: './'` 的静态构建，可被 Electron 或 Tauri 加载；需要替换 `src/lib/puter.js` 存储、去掉 `index.html` 中的 Puter SDK 和 plausible 统计脚本，并替换 `puter.ai`。

### 4.2 Spreadsheet（`src/spreadsheet`）

**1）技术栈、依赖、许可、启动**
- 原生 JS + Vite 8；源码 545 个 JS 文件、约 25.5 万行，3,507 个测试文件。
- 运行时依赖：@noble/hashes、@xmldom/xmldom、intl-messageformat、lucide；内置 SheetJS Community Edition 0.20.3（Apache-2.0，`src/vendor/xlsx.mjs`）和 SCOWL 词表。
- 许可：**AGPL-3.0-only**（`LICENSE` 和 `package.json` 都这样声明）。
- 启动：`npm ci && npm run dev`。

**2）文件格式与存储**
- 读：xlsx / xls / csv / tsv / ods；写：xlsx / ods / csv / tsv / PDF（README 和 `src/core/io.js`）。
- 隐藏工作表 `_puter_meta` 保存应用自己的扩展元数据，其他软件会忽略。
- 存储：Puter FS `Spreadsheets/<name>.xlsx`，版本快照在 `Spreadsheets/.versions/`，设置放在 Puter KV，草稿放在浏览器存储。

**3）业务逻辑与 UI 分离（最好）**
- README 写明 `src/core/` 为「pure logic, no DOM」。已验证可在 Node 直接调用的模块：
  - `src/core/workbook.js`（`Workbook` 文档模型，含惰性求值和撤销）
  - `src/core/formula/`（分词器、解析器、求值器，README 称有 510+ 个函数）
  - `src/core/io.js`（`workbookFromFile`、`workbookToXlsx`、`workbookToOds`、`sheetToCsv`）
  - `src/core/charts.js`（图表模型）
  - `src/core/sheet-pdf.js`（`sheetsToPdf`，纯 JS 写 PDF）
  - `src/core/aitools.js`（`TOOLS` 共 43 个 function-calling 工具定义，加上 `runTool(wb, name, args, env)`）
- 43 个工具：get_workbook_info、get_sheet_details、read_range、calculate、find、write_cells、fill_formula、clear_range、copy_range、move_range、find_replace、format_cells、insert/delete rows/columns、sort_range、filter_range、create_pivot_table、create/update/delete_chart（18 种图表）、create_table、条件格式、数据验证、manage_sheet、freeze_panes、remove_duplicates、split_text_to_columns、add_sparklines、set_link、行高列宽、set_hidden、merge_cells、manage_name、add_note、goal_seek、solve、select_range。
- `env` 只需要提供 sheetId / select / autofit 等回调，本次用约 10 行桩代码就跑通了。
- 依赖浏览器：`src/ui/chartsvg.js`（图表渲染；无头导出 PNG/SVG **未验证**）。

**4）已有接口**：无 CLI；有上述 AI 工具层；有用户脚本运行时（`script-runtime.src.js`、`script-api-docs.js`）。

**6）外壳承载**：静态构建（`base: './'`）。断网时主页面被 Puter SDK 门禁挡住，需要改 `src/lib/puter.js` 与 `src/lib/doc.js`；IMPORTDATA、IMPORTHTML 等公式会联网，应纳入狐狸OS的网络权限控制。

### 4.3 Presentation（`src/presentation`）

**1）技术栈、依赖、许可、启动**
- 原生 JS + Vite 8 + TypeScript 引擎；源码 477 个 JS/TS 文件、约 19.9 万行，459 个测试文件。
- 运行时依赖：fflate（打补丁）、lucide、nspell、unicode-segmenter。引擎 `lib/pptx`、`lib/pptx-preview` 源自 office-kit（MIT，Yuichiro Yamashita，原版本 0.12.0 / 0.9.1，见 `lib/README.md`），在本仓库中独立维护，不再与上游同步。
- 许可：应用为 **AGPL-3.0-only**；`lib/pptx` 目录保留 MIT LICENSE。但 README 又写「本应用全部内容为 AGPL」，**本仓库对 lib 的修改适用哪种许可存在歧义**。
- 启动：`npm ci`（含 patch-package）→ `npm run dev`。

**2）文件格式与存储**
- 原生 pptx（不支持 .ppt 和加密文件；导入上限 200 MB / 300 页）。导出：pptx、PNG（zip）、PDF（浏览器预览渲染后自写 PDF）、GIF、视频。
- 存储：`src/cloud.js` 调 `puter.fs`（`Presentations/`），本地恢复草稿放在 IndexedDB；不使用 KV。

**3）业务逻辑与 UI 分离**
- `lib/pptx/src/node.ts` 是官方的 Node 入口（`loadPresentationFile` / `savePresentationToFile`），Node 22.18+ 可以直接导入 TS。已验证：`createPresentation`、`addTitleSlide`、`addBlankSlide`、`addSlideTextBox`、`addSlideChart`（带内嵌 xlsx 的原生图表）、`addSlideTable`、`getSlides`。另有约 140 个 API 文件（母版、布局、动画、批注、SmartArt、媒体等）**未逐一验证**。
- `lib/pptx-preview/src/render-slide.ts` 的 `renderSlideToSvg` 在 Node 中可以输出 SVG。已验证图表和表格形状会画出来，但**文字缺失**，因为需要宿主提供文字测量回调。
- `src/assistant-tools.js` 在 Node 中可以导入，共 23 个工具：get_presentation、read_slide、find_text、add_slide、duplicate/move/delete、set_notes、add_text/shape/line/table、set_text、set_table_cells、format_text、style_objects、set_bounds、reorder、delete_objects、replace_text、apply_theme 等。**没有插入图表的工具**，而且 `env` 依赖编辑器提供的 `edit()`、`setText()` 等。

**4）已有接口**：无 CLI；有 TS 库 API 和 23 个 AI 工具。

**6）外壳承载**：静态构建；断网时也能打开编辑器（已验证）；需要替换 `src/cloud.js` 和 `puter.ai`。

## 5. 能力清单（已验证 / 部分支持 / 暂不支持 / 未验证）

| 应用 | 能力 | 状态 | 说明 |
|---|---|---|---|
| 文档 | 安装、构建 | 已验证 | 含许可检查 |
| 文档 | 新建、编辑、保存、重开 docx（无头） | 已验证 | 标题样式、加粗、段落 |
| 文档 | 读取纯文本 | 已验证 | `documentText` |
| 文档 | 导出 Markdown / HTML | 未验证 | 函数在 `src/lib/document-export.js` |
| 文档 | 导入 Markdown / HTML | 部分支持 | UI 支持，无头未验证 |
| 文档 | 表格、列表 | 部分支持 | 模型 API 存在，无头未测 |
| 文档 | 插入图表 | 部分支持 | XML 生成器有，插入流程在 UI 中 |
| 文档 | 导出 PDF | 部分支持 | 仅浏览器 Canvas |
| 文档 | 复杂 docx（多节、字段、浮动图） | 暂不支持或只读 | 以 README 为准，需实测 |
| 文档 | CLI 或智能体工具 | 暂不支持 | 需自建 |
| 表格 | 安装、构建、3,972 个用例 | 已验证 | 抽样测试 |
| 表格 | 写单元格、公式、计算、读区域 | 已验证 | 通过 `runTool` |
| 表格 | 创建图表并随 xlsx 往返 | 已验证 | 柱状图 |
| 表格 | 导出 xlsx 并在 LibreOffice 读取 | 已验证 | |
| 表格 | 导出 PDF（无头） | 部分支持 | 不画图表，非 Win-1252 字符（含中文）变「?」 |
| 表格 | 导入 csv / ods、透视表、43 个工具全量 | 未验证 | 代码存在 |
| 表格 | 图表导出为 PNG / SVG（无头） | 未验证 | 渲染在 `src/ui` |
| 表格 | 本地文件存储 | 暂不支持 | 仅 Puter 云 |
| 演示 | 安装、构建、离线打开 UI | 已验证 | |
| 演示 | 新建 pptx、标题页、文本、表格、图表、保存、重开 | 已验证 | LibreOffice 渲染正常 |
| 演示 | 无头 SVG 渲染 | 部分支持 | 文字需要测量回调 |
| 演示 | 导出 PDF / PNG | 部分支持 | 浏览器栅格化 |
| 演示 | 23 个 AI 工具 | 部分支持 | 需编辑器 env；无图表工具 |
| 演示 | .ppt、加密文件、协作编辑 | 暂不支持 | README |
| 演示 | 复杂导入文件的保真度 | 未验证 | README 称为近似 |

## 6. 规划命令复用分类与工作量（粗估，人天，单人熟练开发）

| 规划命令 | 底层能力 | 分类 | 人天 |
|---|---|---|---|
| `foxos sheets open <xlsx/csv/ods>` | `io.workbookFromFile` | 可直接复用 | 0.5 |
| `foxos sheets read / write / formula` | `aitools.runTool`（read_range、write_cells、fill_formula、calculate） | 可直接复用 | 1 |
| `foxos sheets analyze --sheet` | get_sheet_details、calculate、create_pivot_table 组合 | 需适配层 | 2 |
| `foxos sheets chart create --type --range` | create_chart（18 种） | 可直接复用 | 0.5 |
| `foxos sheets chart export png` | `src/ui/chartsvg.js` | 需适配层（未验证） | 2-3 |
| `foxos sheets export xlsx/csv/ods` | `io.workbookToXlsx` 等 | 可直接复用 | 0.5 |
| `foxos sheets export pdf` | `sheetsToPdf`（无图表、无中文） | 需自建或改造（嵌入 CJK 字体、画图表），或改用隐藏窗口打印 | 5-8 |
| 表格 env 桩、CLI 框架、能力目录（导出 TOOLS 的 schema） | | 需适配层 | 2-3 |
| `foxos docs create / open / save` | `createDocx`、`DocxPackage` | 可直接复用 | 1 |
| `foxos docs read --format text/md/html` | `documentText`、`document-export.js` | 需适配层 | 1-2 |
| `foxos docs edit`（按段落或位置插入、替换、样式、加粗、列表、表格） | `TextDocument` 选区式 API | 需适配层（改为按地址定位的命令） | 4-6 |
| `foxos docs import md` | `import-markdown-blocks.js` | 需适配层（未验证） | 2-3 |
| `foxos docs chart insert` | `chart-builder.js` + UI 插入逻辑 | 需适配层 | 3-5 |
| `foxos docs export pdf` | `pdf-export.js`（浏览器） | 需适配层（外壳隐藏窗口渲染） | 3-5 |
| 文档智能体工具 schema | 无 | 需自建 | 3-4 |
| `foxos slides create / open / save` | `lib/pptx` | 可直接复用 | 0.5 |
| `foxos slides add-page / fill`（标题、文本、占位符、表格） | addTitleSlide、addSlideTextBox、setSlideTitle、addSlideTable | 可直接复用，占位符填充需适配 | 1-2 |
| `foxos slides chart insert` | `addSlideChart` | 可直接复用 | 1 |
| 演示智能体工具（复用 23 个，补图表工具） | `assistant-tools.js` | 需适配层（env 桩）+ 自建 1 个 | 4-5 |
| `foxos slides export pdf/png` | renderSlideToSvg + 浏览器栅格化 + `pdf-writer.js` | 需适配层 | 4-6 |
| 三应用的存储适配（Puter FS 换成狐狸OS工作区） | `src/lib/puter.js`、`src/cloud.js` | 需适配层 | 6-10（合计） |
| 三应用的 AI 适配（`puter.ai` 换成狐狸OS模型网关），去掉统计脚本 | | 需适配层 | 3-5（合计） |

**估算合计**：表格约 14-20 人天，文档约 17-26 人天，演示约 11-15 人天，共享存储/AI/外壳适配约 9-15 人天。总计约 51-76 人天。不含许可处理和全面兼容性测试。

## 7. 外壳承载（Tauri / Electron）与联网依赖

| 项目 | Documents | Spreadsheet | Presentation |
|---|---|---|---|
| 产物 | 静态 dist，`base: './'` | 同左 | 同左 |
| 必须联网的部分 | Puter SDK（主页面门禁）、puter.fs/kv/auth/ai、plausible 统计、协作 Worker | Puter SDK（门禁）、puter.fs/kv/auth/ai、plausible、IMPORT* 公式、邮件 Worker | puter.fs、puter.ai；编辑器本身可离线 |
| 断网可用（已验证） | 仅 playground | 否（需改造） | 是 |
| 外壳建议 | Electron 风险最低（测试基于 Chromium）；Windows 首发用 Tauri 也可以，因为 WebView2 是 Chromium；macOS/Linux 的 Tauri（WebKit）兼容性**未验证** | 同左 | 同左 |

注意：Electron 用 `file://` 加载 ES module 可能遇到限制，建议使用自定义协议或本地静态服务（未验证）。

## 8. 风险

1. **AGPL**（高）：Spreadsheet 和 Presentation 为 AGPL-3.0-only。狐狸OS分发修改版，或通过网络提供服务，都可能触发开源义务；与狐狸OS打包后是否构成衍生作品需要法务判断。可选方案：①狐狸OS相关组件本身按 AGPL 开源；②以独立进程和明确边界隔离（是否足够需法务确认）；③联系 Puter 获取商业授权；④演示改用上游 office-kit/pptx（MIT），表格只复用 SheetJS CE（Apache-2.0），公式引擎等另行自研或选型。
2. **Puter 绑定**（中）：存储、登录、AI、协作都走 Puter，需要逐个替换；上游更新频繁，长期合并成本高，建议 fork 后固定版本。
3. **中文与导出**（中）：表格 PDF 不支持中文；文档默认字体 Noto Sans 的中文排版**未验证**；演示 PDF 文字层用 Helvetica，中文表现**未验证**。
4. **格式兼容**（中）：文档引擎对复杂 docx 有限制，演示预览为近似保真。需要用真实业务文件建立回归语料。
5. **体量与上游演进**（低到中）：三应用合计约 57 万行代码，且大量由自动化提交。建议只依赖 core/engine 层，并锁定提交版本。

## 9. 建议的阶段 0 落地顺序

1. 第 1 周并行：法务确认 AGPL 策略；锁定上述提交并 fork。
2. 表格无头内核：Node 中封装 `Workbook` + `runTool`，实现 `foxos sheets open/read/write/chart create/export xlsx`，把 43 个工具的 schema 导出为能力目录（约 4-5 人天）。
3. 演示无头内核：基于 `lib/pptx`（优先评估上游 MIT 版本），实现 `foxos slides create/add-page/chart insert/table/save`（约 3 人天）。
4. 文档无头内核：基于 `TextDocument`/`DocxPackage`，实现 `foxos docs create/read/append/style/save`（约 4-5 人天）。
5. 智能体闭环：查询能力目录 → 结构化调用 → 重新打开文件校验（测试中可用 LibreOffice 做独立校验）。达到阶段 0 通过标准「创建、修改、重开、验证」。
6. 外壳：先用 Electron 或 Tauri 承载 Presentation（可离线）与 Documents playground，替换存储为本地工作区，再处理 Spreadsheet 的 Puter 门禁。
7. 导出：在外壳隐藏窗口中实现 PDF/PNG 渲染，补上中文字体。

## 10. 后续建议：在线安装器与组件化分发

**组件化可行性（已验证构建产物体积）**：三个首批应用在仓库中本来就是独立的 Vite 项目（各有自己的 package.json 和 lock 文件），`npm run build` 后各生成一个自包含的静态 `dist/`，`base: './'`，不依赖其他应用目录，天然适合作为狐狸OS安装器里的可选组件单独打包下载。实测体积如下（tar.gz 用 gzip 默认级别压缩）：

| 组件 | dist 原始 | tar.gz | 说明 |
|---|---|---|---|
| Documents | 34 MB | 18 MB | 字体 17 MB、示例 fixtures 8.6 MB、同义词库 2.8 MB；去掉 fixtures 后 12 MB |
| Spreadsheet | 13 MB | 5.5 MB | 内含 Carlito/Caladea 等字体 3.8 MB |
| Presentation | 5.0 MB | 2.1 MB | 最小 |

建议的组件包结构是：`dist/`（UI）+ 无头内核（core/engine 加上 foxos 适配层，Node 侧）+ `manifest.json`（版本、许可证、能力目录、所需权限、联网需求、校验和与签名）。安装器从狐狸OS组件源拉取索引，用户勾选后逐个下载、校验、解压到应用目录，并注册命令与能力目录。AGPL 组件（表格、演示）建议在安装时单独展示许可、提供对应源码下载入口，并与 MIT 组件分开打包，这也便于后续许可策略调整。字体、示例文件、词典可拆为「可选资源包」，进一步减小首装体积。注意：上述 dist 仍包含 Puter SDK 引用和 plausible 统计脚本，组件化前需先完成第 7 节的本地化改造；无头内核在 Node 中运行时需要随包附带 jsdom（仅文档需要）或换成更轻量的 XML 实现（未验证）。

## 11. ACP 智能体接入

**ACP 现状（2026-11-10 核实）**
- ACP（Agent Client Protocol）标准化「客户端（编辑器或宿主）」与「编码智能体」之间的通信：客户端以子进程方式启动智能体，通过 stdio 上的 JSON-RPC 交互，协议中包含会话、提示、工具调用、文件读写和终端请求、权限请求等。协议仓库为 https://github.com/agentclientprotocol/agent-client-protocol （Apache-2.0，最新 schema 发布为 `schema-v1.30.0`，发布于 2026-11-09 17:41（UTC+8）），官方文档在 https://agentclientprotocol.com 。TypeScript SDK 为 npm 包 `@agentclientprotocol/sdk` 2.5.0（Apache-2.0）。
- 官方 Agents 页面（https://agentclientprotocol.com/get-started/agents ）列出 50 余个实现。另有精选的 **ACP Registry**（https://github.com/agentclientprotocol/registry ），只收录支持认证的智能体，并由 CI 校验握手返回有效的 `authMethods`。其机器可读索引为 https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json （本次拉取：version 1.0.0，共 45 个智能体）。每个条目给出分发方式：`npx` 包名加启动参数，或按平台给出 `binary` 压缩包 URL、`cmd` 和 sha256。JetBrains 已基于该注册表在 IDE 内提供一键安装（https://blog.jetbrains.com/ai/2026/01/acp-agent-registry/ ）。

**狐狸OS 作为 ACP 客户端的接入方案**
1. 狐狸OS运行时内置 ACP 客户端（Rust 侧可用官方 Rust 实现，TS 侧可用 `@agentclientprotocol/sdk`；具体 crate 名与版本未核实）。每个智能体以子进程运行在独立工作目录，由运行时负责超时、取消和资源限制。
2. 「智能体中心」直接读取 ACP Registry 的 `registry.json`，实现一键安装。`binary` 类型下载对应平台压缩包，校验 sha256 后解压到狐狸OS私有目录；`npx` 类型使用狐狸OS自带的 Node 运行时，安装时锁定注册表给出的版本，并写入注册表提供的环境变量（如关闭自动更新）。认证流程按握手返回的 `authMethods` 引导用户完成，密钥交由狐狸OS凭据管理保存。
3. 把 ACP 的 fs/terminal 请求映射到狐狸OS的工作区权限与命令总线：智能体读写文件、执行 `foxos sheets ...` 等命令都经过权限检查和审计记录；ACP 的权限请求直接弹到「人工接管」面板。
4. 狐狸OS的应用能力目录（例如表格 43 个工具的 schema）通过 MCP 或命令说明提供给 ACP 智能体。ACP 会话可以携带 MCP 服务器配置，该能力的具体字段需按 schema 核对后实现，**未验证**。这样同一套 foxos 命令可同时服务内置智能体和第三方 ACP 智能体。

**首批建议一键安装的智能体**（均在本次拉取的 registry.json 中核实，版本为拉取时的值）

| 智能体 | 注册表 id | 分发方式与启动 | 许可（注册表声明） |
|---|---|---|---|
| Gemini CLI | `gemini` | npx `@google/gemini-cli@0.67.0 --acp` | Apache-2.0 |
| Codex（ACP 适配器） | `codex-acp` | npx `@agentclientprotocol/codex-acp@2.6.0` | Apache-2.0 |
| Claude Agent（ACP 适配器） | `claude-acp` | 全平台二进制（含 Windows x64/arm64），或 npx `@agentclientprotocol/claude-agent-acp@0.103.0` | proprietary |
| Qwen Code | `qwen-code` | npx `@qwen-code/qwen-code@0.27.1 --acp --experimental-skills` | Apache-2.0 |
| Kimi Code | `kimi-code` | npx `@moonshot-ai/kimi-code@2.5.2 acp` | MIT |
| goose | `goose` | 二进制 `goose acp`（含 windows-x86_64） | Apache-2.0 |
| OpenCode | `opencode` | 二进制 `opencode acp`（含 Windows x64/arm64） | MIT |
| GitHub Copilot CLI | `github-copilot-cli` | npx `@github/copilot@1.0.108 --acp` | proprietary |
| Codebuddy Code（腾讯云） | `codebuddy-code` | npx `@tencent-ai/codebuddy-code@2.182.0 --acp` | Proprietary |
| GLM Agent（社区，智谱 GLM） | `glm-acp-agent` | npx `glm-acp-agent@1.17.1` | Apache-2.0 |

另外，Cursor、Mistral Vibe、Junie、Kiro、Qoder、MiniMax Code 等也在注册表中，可作为第二批。注意：Kiro 的注册表条目没有 Windows 二进制；Mistral Vibe 只有 windows-x86_64。首发 Windows 时应以注册表的平台字段过滤。以上智能体均为编码智能体；它们能否稳定调用 foxos 办公命令，需要在阶段 0 的评测集中实测（**未验证**）。
