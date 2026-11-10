# Field Service（field-service）操作清单

分组：business · 替代 Jobber, Housecall Pro, ServiceTitan · 许可证 MIT (root LICENSE) · 页面标题「Home · Field Service」

共 40 个操作，全部有语义命令（`foxos field-service <资源> <动词>`，MCP 工具 `field-service.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `workflow.select` | `foxos field-service workflow select` | 主界面 > Workflow > # | `target`（必填） | 点击名称匹配的「#」项（link） | 不适用（只读） |
| `paymentowed-you.select` | `foxos field-service paymentowed-you select` | 主界面 > Workflow > # paymentowed to you$# | `target`（必填） | 点击名称匹配的「# paymentowed to you$#」项（link） | 不适用（只读） |
| `content.dismiss` | `foxos field-service content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `n.create` | `foxos field-service n create` | 主界面 > aside > Create (N) | — | 点击「Create (N)」（button） | 否（应用没有撤销入口） |
| `home.show` | `foxos field-service home show` | 主界面 > Main > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `schedule.schedule` | `foxos field-service schedule schedule` | 主界面 > Main > Schedule | — | 点击「Schedule」（link） | 否（应用没有撤销入口） |
| `clients.show` | `foxos field-service clients show` | 主界面 > Main > Clients | — | 点击「Clients」（link），切换到该视图 | 不适用（只读） |
| `requests.show` | `foxos field-service requests show` | 主界面 > Requests | — | 点击「Requests」（link），切换到该视图 | 不适用（只读） |
| `quotes.show` | `foxos field-service quotes show` | 主界面 > Main > Quotes | — | 点击「Quotes」（link），切换到该视图 | 不适用（只读） |
| `jobs.show` | `foxos field-service jobs show` | 主界面 > Jobs | — | 点击「Jobs」（link），切换到该视图 | 不适用（只读） |
| `invoices.show` | `foxos field-service invoices show` | 主界面 > Invoices | — | 点击「Invoices」（link），切换到该视图 | 不适用（只读） |
| `payments.show` | `foxos field-service payments show` | 主界面 > Main > Payments | — | 点击「Payments」（link），切换到该视图 | 不适用（只读） |
| `timesheets.show` | `foxos field-service timesheets show` | 主界面 > Main > Timesheets | — | 点击「Timesheets」（link），切换到该视图 | 不适用（只读） |
| `expenses.show` | `foxos field-service expenses show` | 主界面 > Main > Expenses | — | 点击「Expenses」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos field-service reports show` | 主界面 > Main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos field-service source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos field-service puter show` | 主界面 > aside > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `navigation.collapse` | `foxos field-service navigation collapse` | 主界面 > Collapse navigation | — | 点击「Collapse navigation」（button） | 不适用（只读） |
| `search.search` | `foxos field-service search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos field-service keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos field-service settings show` | 主界面 > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `account-appearance.activate` | `foxos field-service account-appearance activate` | 主界面 > Account and appearance | — | 点击「Account and appearance」（button） | 否（应用没有撤销入口） |
| `dismiss.dismiss` | `foxos field-service dismiss dismiss` | 主界面 > main > Dismiss | — | 点击「Dismiss」（button） | 不适用（只读） |
| `business-details.create` | `foxos field-service business-details create` | 主界面 > main > Add your business details | — | 点击「Add your business details」（link） | 否（应用没有撤销入口） |
| `services-you-offer.create` | `foxos field-service services-you-offer create` | 主界面 > main > Add the services you offer | — | 点击「Add the services you offer」（link） | 否（应用没有撤销入口） |
| `team.create` | `foxos field-service team create` | 主界面 > main > Add your team | — | 点击「Add your team」（link） | 否（应用没有撤销入口） |
| `first-client.create` | `foxos field-service first-client create` | 主界面 > main > Add your first client | — | 点击「Add your first client」（link） | 否（应用没有撤销入口） |
| `first-quote.send` | `foxos field-service first-quote send` | 主界面 > main > Send your first quote | — | 点击「Send your first quote」（link） | 否（应用没有撤销入口） |
| `schedule-2.schedule` | `foxos field-service schedule-2 schedule` | 主界面 > main > Schedule | — | 点击「Schedule」（link） | 否（应用没有撤销入口） |
| `job.create` | `foxos field-service job create` | 主界面 > main > New job | — | 点击「New job」（link） | 否（应用没有撤销入口） |
| `reports-2.show` | `foxos field-service reports-2 show` | 主界面 > main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos field-service close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `business-name.set` | `foxos field-service business-name set` | 主界面 > dialog > Business name | `value`（必填）, `submit` | 把「Business name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `name.set` | `foxos field-service name set` | 主界面 > dialog > Your name | `value`（必填）, `submit` | 把「Your name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `industry.set` | `foxos field-service industry set` | 主界面 > dialog > Industry | `value`（必填）, `submit` | 把「Industry」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `currency.set` | `foxos field-service currency set` | 主界面 > dialog > Currency | `value`（必填）, `submit` | 把「Currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sample-data.import` | `foxos field-service sample-data import` | 主界面 > dialog > Load sample data | — | 点击「Load sample data」（button） | 否（应用没有撤销入口） |
| `get-started.activate` | `foxos field-service get-started activate` | 主界面 > dialog > Get started | — | 点击「Get started」（button） | 否（应用没有撤销入口） |
| `it.dismiss` | `foxos field-service it dismiss` | 主界面 > Early alpha notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `command-palette.show` | `foxos field-service command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shell.js 中定义） | 不适用 |
