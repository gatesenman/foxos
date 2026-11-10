# Legal（legal）操作清单

分组：business · 替代 Clio, MyCase, PracticePanther · 许可证 MIT (root LICENSE) · 页面标题「Dashboard · Legal」

共 43 个操作，全部有语义命令（`foxos legal <资源> <动词>`，MCP 工具 `legal.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `timer.start` | `foxos legal timer start` | 主界面 > start timer, # | `target`（必填） | 点击名称匹配的「start timer, #」项（button） | 否（应用没有撤销入口） |
| `draft-bills-bills.select` | `foxos legal draft-bills-bills select` | 主界面 > Personal > draft bills$# bills | `target`（必填） | 点击名称匹配的「draft bills$# bills」项（link） | 不适用（只读） |
| `unpaid-bills.select` | `foxos legal unpaid-bills select` | 主界面 > Personal > unpaid$# bills | `target`（必填） | 点击名称匹配的「unpaid$# bills」项（link） | 不适用（只读） |
| `overdue-bills.select` | `foxos legal overdue-bills select` | 主界面 > Personal > overdue$# bills | `target`（必填） | 点击名称匹配的「overdue$# bills」项（link） | 不适用（只读） |
| `held-trust-trust-accounts.select` | `foxos legal held-trust-trust-accounts select` | 主界面 > Personal > held in trust$# trust accounts | `target`（必填） | 点击名称匹配的「held in trust$# trust accounts」项（link） | 不适用（只读） |
| `firm-name.select` | `foxos legal firm-name select` | 主界面 > dialog > firm name * | `target`（必填） | 点击名称匹配的「firm name *」项（textbox） | 不适用（只读） |
| `content.dismiss` | `foxos legal content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `legal-dashboard.show` | `foxos legal legal-dashboard show` | 主界面 > Legal dashboard | — | 点击「Legal dashboard」（link），切换到该视图 | 不适用（只读） |
| `dashboard.show` | `foxos legal dashboard show` | 主界面 > Main > Dashboard | — | 点击「Dashboard」（link），切换到该视图 | 不适用（只读） |
| `calendar.show` | `foxos legal calendar show` | 主界面 > Main > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `tasks.show` | `foxos legal tasks show` | 主界面 > Tasks | — | 点击「Tasks」（link），切换到该视图 | 不适用（只读） |
| `matters.show` | `foxos legal matters show` | 主界面 > Main > Matters | — | 点击「Matters」（link），切换到该视图 | 不适用（只读） |
| `contacts.show` | `foxos legal contacts show` | 主界面 > Main > Contacts | — | 点击「Contacts」（link），切换到该视图 | 不适用（只读） |
| `activities.show` | `foxos legal activities show` | 主界面 > Main > Activities | — | 点击「Activities」（link），切换到该视图 | 不适用（只读） |
| `billing.show` | `foxos legal billing show` | 主界面 > Billing | — | 点击「Billing」（link），切换到该视图 | 不适用（只读） |
| `accounts.show` | `foxos legal accounts show` | 主界面 > Main > Accounts | — | 点击「Accounts」（link），切换到该视图 | 不适用（只读） |
| `documents.show` | `foxos legal documents show` | 主界面 > Main > Documents | — | 点击「Documents」（link），切换到该视图 | 不适用（只读） |
| `communications.show` | `foxos legal communications show` | 主界面 > Main > Communications | — | 点击「Communications」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos legal reports show` | 主界面 > Main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos legal settings show` | 主界面 > aside > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos legal source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `navigation.collapse` | `foxos legal navigation collapse` | 主界面 > Collapse navigation | — | 点击「Collapse navigation」（button） | 不适用（只读） |
| `search.search` | `foxos legal search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `timer-details.activate` | `foxos legal timer-details activate` | 主界面 > Timer details | — | 点击「Timer details」（button） | 否（应用没有撤销入口） |
| `n.create` | `foxos legal n create` | 主界面 > header > Create new (N) | — | 点击「Create new (N)」（button） | 否（应用没有撤销入口） |
| `alerts.activate` | `foxos legal alerts activate` | 主界面 > Alerts | — | 点击「Alerts」（button） | 否（应用没有撤销入口） |
| `account-appearance.activate` | `foxos legal account-appearance activate` | 主界面 > Account and appearance | — | 点击「Account and appearance」（button） | 否（应用没有撤销入口） |
| `task.create` | `foxos legal task create` | 主界面 > header > New task | — | 点击「New task」（button） | 否（应用没有撤销入口） |
| `time.record` | `foxos legal time record` | 主界面 > header > Record time | — | 点击「Record time」（button） | 否（应用没有撤销入口） |
| `personal.show` | `foxos legal personal show` | 主界面 > Dashboard > Personal | — | 点击「Personal」（tab），切换到该视图 | 不适用（只读） |
| `firm.show` | `foxos legal firm show` | 主界面 > Dashboard > Firm | — | 点击「Firm」（tab），切换到该视图 | 不适用（只读） |
| `firm-users.open` | `foxos legal firm-users open` | 主界面 > Personal > Open firm users | — | 点击「Open firm users」（link） | 不适用（只读） |
| `calendar-2.show` | `foxos legal calendar-2 show` | 主界面 > Personal > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `matters-2.show` | `foxos legal matters-2 show` | 主界面 > Personal > Matters | — | 点击「Matters」（link），切换到该视图 | 不适用（只读） |
| `matter.create` | `foxos legal matter create` | 主界面 > Personal > New matter | — | 点击「New matter」（link） | 否（应用没有撤销入口） |
| `activities-2.show` | `foxos legal activities-2 show` | 主界面 > Personal > Activities | — | 点击「Activities」（link），切换到该视图 | 不适用（只读） |
| `billing-2.show` | `foxos legal billing-2 show` | 主界面 > Personal > Billing | — | 点击「Billing」（link），切换到该视图 | 不适用（只读） |
| `i-understand.activate` | `foxos legal i-understand activate` | 主界面 > Early alpha notice > I understand | — | 点击「I understand」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos legal close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `currency.set` | `foxos legal currency set` | 主界面 > dialog > Currency | `value`（必填）, `submit` | 把「Currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos legal explore-sample-data activate` | 主界面 > dialog > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `continue.activate` | `foxos legal continue activate` | 主界面 > dialog > Continue | — | 点击「Continue」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos legal command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shell.js 中定义） | 不适用 |
