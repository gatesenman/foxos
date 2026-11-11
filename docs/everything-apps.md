# Everything 应用（51 个）

上游：[HeyPuter/everything](https://github.com/HeyPuter/everything) 提交 `0fbb88cd`。AGPL 许可的应用在安装时从上游源码在本机构建，狐狸OS 不修改、不内置其源码；其余为 MIT。

每个应用：本机运行（`foxapp://` + 本地 Puter 运行时）、打开 / 保存工作空间文件、`foxos <应用> …` 语义命令与同名 MCP 工具、用户故事 US-40…48（按分组）与端到端测试（启动 + 一次界面操作与等价 CLI 命令的结果对比）。

覆盖：本机可运行 **50/51**，有语义命令 **50/51**，启动测试通过 **50/51**，界面与命令等价 **49/51**。

| 分组 | 应用 | ID | 许可证 | 本机运行 | 语义命令 | 启动测试 | 界面 = 命令 | 等价测试用的命令 | 界面语言 | 操作清单 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 办公 | Spreadsheet | `spreadsheet` | AGPL-3.0-only | 可运行 | 371 | 通过 | 一致 | `foxos spreadsheet cell-reference set foxos parity` | 中文 / 英文，格式跟随 | [spreadsheet.md](operations/spreadsheet.md) |
| 办公 | Documents | `documents` | MIT (root LICENSE) | 可运行 | 311 | 通过 | 一致 | `foxos documents document-name set foxos parity` | 英文，格式跟随 | [documents.md](operations/documents.md) |
| 办公 | Presentation | `presentation` | AGPL-3.0-only | 可运行 | 284 | 通过 | 一致 | `foxos presentation speaker-notes set foxos parity` | 英文，格式跟随 | [presentation.md](operations/presentation.md) |
| 办公 | Whiteboard | `whiteboard` | AGPL-3.0-only | 可运行 | 26 | 通过 | 一致 | `foxos whiteboard search-boards set foxos parity` | 英文，格式跟随 | [whiteboard.md](operations/whiteboard.md) |
| 办公 | PDF | `pdf` | AGPL-3.0-only | 可运行 | 85 | 通过 | 一致 | `foxos pdf page-number set 2` | 英文，格式跟随 | [pdf.md](operations/pdf.md) |
| 办公 | Notes | `notes` | AGPL-3.0-only | 可运行 | 136 | 通过 | 一致 | `foxos notes insert create` | 英文，格式跟随 | [notes.md](operations/notes.md) |
| 办公 | Records | `records` | MIT | 可运行 | 16 | 通过 | 一致 | `foxos records search-bases set foxos parity` | 英文，格式跟随 | [records.md](operations/records.md) |
| 协作 | Meetings | `meetings` | MIT (root LICENSE) | 可运行 | 17 | 通过 | 一致 | `foxos meetings meeting-code-or-link set foxos parity` | 英文，格式跟随 | [meetings.md](operations/meetings.md) |
| 协作 | Teamchat | `teamchat` | MIT (root LICENSE) | 可运行 | 6 | 通过 | 一致 | `foxos teamchat close close` | 英文，格式跟随 | [teamchat.md](operations/teamchat.md) |
| 协作 | Email | `email` | AGPL-3.0-only | 可运行 | 2 | 通过 | 一致 | `foxos email grant-read-access activate` | 英文，格式跟随 | [email.md](operations/email.md) |
| 协作 | Contacts | `contacts` | MIT (root LICENSE) | 可运行 | 28 | 通过 | 一致 | `foxos contacts contact create` | 英文，格式跟随 | [contacts.md](operations/contacts.md) |
| 协作 | Calendar | `calendar` | MIT | 可运行 | 36 | 通过 | 一致 | `foxos calendar create create` | 英文，格式跟随 | [calendar.md](operations/calendar.md) |
| 协作 | Signatures | `signatures` | MIT (root LICENSE) | 可运行 | 29 | 通过 | 一致 | `foxos signatures set-up-account activate` | 英文，格式跟随 | [signatures.md](operations/signatures.md) |
| 创意 | Photo Studio | `photo-studio` | MIT (root LICENSE) | 可运行 | 104 | 通过 | 不一致 | `foxos photo-studio describe-edit set foxos parity` | 英文，格式跟随 | [photo-studio.md](operations/photo-studio.md) |
| 创意 | Video Studio | `video-studio` | AGPL-3.0-only | 可运行 | 34 | 通过 | 一致 | `foxos video-studio search-projects set foxos parity` | 英文，格式跟随 | [video-studio.md](operations/video-studio.md) |
| 创意 | Vector Studio | `vector-studio` | MIT (root LICENSE) | 可运行 | 90 | 通过 | 一致 | `foxos vector-studio single-or-double-column-tools toggle` | 英文，格式跟随 | [vector-studio.md](operations/vector-studio.md) |
| 创意 | Audio Studio | `audio-studio` | MIT (root LICENSE) | 可运行 | 148 | 通过 | 一致 | `foxos audio-studio search-commands set foxos parity` | 英文，格式跟随 | [audio-studio.md](operations/audio-studio.md) |
| 创意 | Music Studio | `music-studio` | MIT (root LICENSE) | 可运行 | 266 | 通过 | 一致 | `foxos music-studio add create` | 英文，格式跟随 | [music-studio.md](operations/music-studio.md) |
| 创意 | 3D Studio | `3d` | AGPL-3.0-only | 可运行 | 230 | 通过 | 一致 | `foxos 3d default activate` | 英文，格式跟随 | [3d.md](operations/3d.md) |
| 工程 | CAD | `cad` | AGPL-3.0-only | 可运行 | 180 | 通过 | 一致 | `foxos cad drawing create` | 英文，格式跟随 | [cad.md](operations/cad.md) |
| 工程 | Parametric | `parametric` | AGPL-3.0-only | 可运行 | 33 | 通过 | 一致 | `foxos parametric insert create` | 英文，格式跟随 | [parametric.md](operations/parametric.md) |
| 工程 | Circuits | `circuits` | AGPL-3.0-only | 可运行 | 39 | 通过 | 一致 | `foxos circuits project create` | 英文，格式跟随 | [circuits.md](operations/circuits.md) |
| 工程 | Building Design | `building-design` | AGPL-3.0-only | 可运行 | 1 | 通过 | 一致 | `foxos building-design it dismiss` | 英文，格式跟随 | [building-design.md](operations/building-design.md) |
| 效率 | Tasks | `tasks` | MIT (root LICENSE) | 可运行 | 58 | 通过 | 一致 | `foxos tasks first-task create` | 英文，格式跟随 | [tasks.md](operations/tasks.md) |
| 效率 | Projects | `projects` | MIT | 可运行 | 50 | 通过 | 一致 | `foxos projects first-project create` | 英文，格式跟随 | [projects.md](operations/projects.md) |
| 效率 | Wiki | `wiki` | MIT (root LICENSE) | 可运行 | 60 | 通过 | 一致 | `foxos wiki getting-started set foxos parity` | 英文，格式跟随 | [wiki.md](operations/wiki.md) |
| 效率 | Time Tracking | `time-tracking` | MIT (root LICENSE) | 可运行 | 71 | 通过 | 一致 | `foxos time-tracking set-up-tracking activate` | 英文，格式跟随 | [time-tracking.md](operations/time-tracking.md) |
| 效率 | Surveys | `survey` | MIT | 可运行 | 28 | 通过 | 一致 | `foxos survey search-surveys set foxos parity` | 英文，格式跟随 | [survey.md](operations/survey.md) |
| 财务 | Accounting | `accounting` | MIT | 可运行 | 45 | 通过 | 一致 | `foxos accounting books create` | 英文，格式跟随 | [accounting.md](operations/accounting.md) |
| 财务 | Invoicing | `invoicing` | MIT (root LICENSE) | 可运行 | 20 | 通过 | 一致 | `foxos invoicing set-up-business activate` | 英文，格式跟随 | [invoicing.md](operations/invoicing.md) |
| 财务 | Expenses | `expense` | MIT (root LICENSE) | 可运行 | 17 | 通过 | 一致 | `foxos expense set-up-expenses activate` | 英文，格式跟随 | [expense.md](operations/expense.md) |
| 财务 | Cap Table | `cap-table` | MIT (root LICENSE) | 可运行 | 27 | 通过 | 一致 | `foxos cap-table set-up-company activate` | 英文，格式固定英文 | [cap-table.md](operations/cap-table.md) |
| 业务 | CRM | `crm` | MIT (root LICENSE) | 可运行 | 16 | 通过 | 一致 | `foxos crm set-up-pipeline activate` | 英文，格式固定英文 | [crm.md](operations/crm.md) |
| 业务 | Help Desk | `help-desk` | MIT | 可运行 | 6 | 通过 | 一致 | `foxos help-desk help-desk-name set foxos parity` | 英文，格式跟随 | [help-desk.md](operations/help-desk.md) |
| 业务 | Contracts | `contracts` | MIT (root LICENSE) | 可运行 | 14 | 通过 | 一致 | `foxos contracts first-contract create` | 英文，格式跟随 | [contracts.md](operations/contracts.md) |
| 业务 | Point of Sale | `pos` | MIT (root LICENSE) | 可运行 | 17 | 通过 | 一致 | `foxos pos set-up-store activate` | 英文，格式跟随 | [pos.md](operations/pos.md) |
| 业务 | Inventory | `inventory` | MIT (root LICENSE) | 可运行 | 17 | 通过 | 一致 | `foxos inventory set-up-inventory activate` | 英文，格式跟随 | [inventory.md](operations/inventory.md) |
| 业务 | Assets | `assets` | MIT (root LICENSE) | 上游缺源码 | 0 | — | — | — | 英文 | [assets.md](operations/assets.md) |
| 业务 | Hiring | `hiring` | MIT (root LICENSE) | 可运行 | 22 | 通过 | 一致 | `foxos hiring set-up-hiring activate` | 英文，格式跟随 | [hiring.md](operations/hiring.md) |
| 业务 | Shifts | `shifts` | MIT (root LICENSE) | 可运行 | 17 | 通过 | 一致 | `foxos shifts set-up-team activate` | 英文，格式跟随 | [shifts.md](operations/shifts.md) |
| 业务 | Childcare | `childcare` | MIT (root LICENSE) | 可运行 | 39 | 通过 | 一致 | `foxos childcare school-name set foxos parity` | 英文，格式跟随 | [childcare.md](operations/childcare.md) |
| 业务 | Field Service | `field-service` | MIT (root LICENSE) | 可运行 | 40 | 通过 | 一致 | `foxos field-service business-name set foxos parity` | 英文，格式跟随 | [field-service.md](operations/field-service.md) |
| 业务 | Legal | `legal` | MIT (root LICENSE) | 可运行 | 43 | 通过 | 一致 | `foxos legal explore-sample-data activate` | 英文，格式跟随 | [legal.md](operations/legal.md) |
| 业务 | Fleet | `fleet` | MIT (root LICENSE) | 可运行 | 41 | 通过 | 一致 | `foxos fleet fleet-or-company-name set foxos parity` | 英文，格式跟随 | [fleet.md](operations/fleet.md) |
| 业务 | Property Management | `property-management` | MIT (root LICENSE) | 可运行 | 45 | 通过 | 一致 | `foxos property-management company-name set foxos parity` | 英文，格式跟随 | [property-management.md](operations/property-management.md) |
| 开发 | API Client | `api-client` | MIT (root LICENSE) | 可运行 | 59 | 通过 | 一致 | `foxos api-client filter set foxos parity` | 英文，格式跟随 | [api-client.md](operations/api-client.md) |
| 游戏 | Chess | `chess` | MIT (root LICENSE) | 可运行 | 30 | 通过 | 一致 | `foxos chess game create` | 英文 | [chess.md](operations/chess.md) |
| 游戏 | Backgammon | `backgammon` | MIT (root LICENSE) | 可运行 | 27 | 通过 | 一致 | `foxos backgammon game create` | 英文 | [backgammon.md](operations/backgammon.md) |
| 游戏 | Checkers | `checkers` | MIT (root LICENSE) | 可运行 | 21 | 通过 | 一致 | `foxos checkers game create` | 英文 | [checkers.md](operations/checkers.md) |
| 游戏 | Solitaire | `solitaire` | MIT (root LICENSE) | 可运行 | 9 | 通过 | 一致 | `foxos solitaire powered-by-puter show` | 英文 | [solitaire.md](operations/solitaire.md) |
| 游戏 | Sudoku | `sudoku` | MIT (root LICENSE) | 可运行 | 39 | 通过 | 一致 | `foxos sudoku puzzle create` | 英文，格式跟随 | [sudoku.md](operations/sudoku.md) |

说明：

- `assets` 的上游仓库缺少 `src/main.js`，无法构建（GitHub contents API 返回 404），如实标为“上游缺源码”，不计入可运行数。
- “语义命令”是从界面实际遍历 + 快捷键挖掘得到的操作数（`foxos <应用> <资源> <动作>`），清单见 `docs/operations/`。
- “界面语言”：上游应用自带的界面语言。狐狸OS 把自己的语言通过 Chromium 语言（`navigator.language`）传给每个应用；上游提供中文界面的（目前只有 spreadsheet）随狐狸OS 切换中 / 英文；其余是英文界面，标“格式跟随”的应用的日期与数字按狐狸OS 语言显示。数据来自扫描上游源码（`packages/core/foxos/data/everything-locale.json`），spreadsheet 由 US-55 端到端测试验证。
- 测试结果来自 `docs/test-results/everything.json`，由 `npm run test:all` 中的 everything.e2e.js 写入。
