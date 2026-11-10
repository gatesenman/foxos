# Accounting（accounting）操作清单

分组：finance · 替代 QuickBooks Online, Xero, Wave Accounting · 许可证 MIT · 页面标题「Accounting」

共 45 个操作，全部有语义命令（`foxos accounting <资源> <动词>`，MCP 工具 `accounting.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account-menu.select` | `foxos accounting account-menu select` | 主界面 > account menu for * | `target`（必填） | 点击名称匹配的「account menu for *」项（button） | 不适用（只读） |
| `company-name.select` | `foxos accounting company-name select` | 主界面 > dialog > company name * | `target`（必填） | 点击名称匹配的「company name *」项（textbox） | 不适用（只读） |
| `content.dismiss` | `foxos accounting content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `home.show` | `foxos accounting home show` | 主界面 > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `create.create` | `foxos accounting create create` | 主界面 > Primary > Create | — | 点击「Create」（button） | 否（应用没有撤销入口） |
| `home-2.show` | `foxos accounting home-2 show` | 主界面 > Primary > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `banking.show` | `foxos accounting banking show` | 主界面 > Primary > Banking | — | 点击「Banking」（link），切换到该视图 | 不适用（只读） |
| `sales.show` | `foxos accounting sales show` | 主界面 > Primary > Sales | — | 点击「Sales」（link），切换到该视图 | 不适用（只读） |
| `purchases.show` | `foxos accounting purchases show` | 主界面 > Primary > Purchases | — | 点击「Purchases」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos accounting reports show` | 主界面 > Primary > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `menu.show` | `foxos accounting menu show` | 主界面 > Primary > Menu | — | 点击「Menu」（button），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos accounting settings show` | 主界面 > Primary > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `navigation.open` | `foxos accounting navigation open` | 主界面 > Open navigation | — | 点击「Open navigation」（button） | 不适用（只读） |
| `search.set` | `foxos accounting search set` | 主界面 > Search | `value`（必填）, `submit` | 把「Search」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `keyboard-shortcuts.activate` | `foxos accounting keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `settings-2.show` | `foxos accounting settings-2 show` | 主界面 > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `panel.collapse` | `foxos accounting panel collapse` | 主界面 > Collapse panel | — | 点击「Collapse panel」（button） | 不适用（只读） |
| `accounting.activate` | `foxos accounting accounting activate` | 主界面 > Sections > Accounting | — | 点击「Accounting」（button） | 否（应用没有撤销入口） |
| `purchases.activate` | `foxos accounting purchases activate` | 主界面 > Sections > Purchases | — | 点击「Purchases」（button） | 否（应用没有撤销入口） |
| `sales.activate` | `foxos accounting sales activate` | 主界面 > Sections > Sales | — | 点击「Sales」（button） | 否（应用没有撤销入口） |
| `sales-tax.activate` | `foxos accounting sales-tax activate` | 主界面 > Sections > Sales Tax | — | 点击「Sales Tax」（button） | 否（应用没有撤销入口） |
| `reports.activate` | `foxos accounting reports activate` | 主界面 > Sections > Reports | — | 点击「Reports」（button） | 否（应用没有撤销入口） |
| `puter.show` | `foxos accounting puter show` | 主界面 > Sections > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `privacy.activate` | `foxos accounting privacy activate` | 主界面 > main > Privacy | — | 点击「Privacy」（button） | 否（应用没有撤销入口） |
| `invoice.create` | `foxos accounting invoice create` | 主界面 > main > Create invoice | — | 点击「Create invoice」（button） | 否（应用没有撤销入口） |
| `payment.record` | `foxos accounting payment record` | 主界面 > main > Record payment | — | 点击「Record payment」（button） | 否（应用没有撤销入口） |
| `expense.record` | `foxos accounting expense record` | 主界面 > main > Record expense | — | 点击「Record expense」（button） | 否（应用没有撤销入口） |
| `enter-bill.activate` | `foxos accounting enter-bill activate` | 主界面 > main > Enter bill | — | 点击「Enter bill」（button） | 否（应用没有撤销入口） |
| `pay-bills.activate` | `foxos accounting pay-bills activate` | 主界面 > main > Pay bills | — | 点击「Pay bills」（button） | 否（应用没有撤销入口） |
| `deposit.record` | `foxos accounting deposit record` | 主界面 > main > Record deposit | — | 点击「Record deposit」（button） | 否（应用没有撤销入口） |
| `write-check.activate` | `foxos accounting write-check activate` | 主界面 > main > Write check | — | 点击「Write check」（button） | 否（应用没有撤销入口） |
| `bank-statement.import` | `foxos accounting bank-statement import` | 主界面 > main > Upload bank statement | — | 点击「Upload bank statement」（button） | 否（应用没有撤销入口） |
| `period.set` | `foxos accounting period set` | 主界面 > Period | `value`（必填）, `submit` | 把「Period」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `report.show` | `foxos accounting report show` | 主界面 > Profit and loss > View report | — | 点击「View report」（link），切换到该视图 | 不适用（只读） |
| `overdue.show` | `foxos accounting overdue show` | 主界面 > Invoices > Overdue | — | 点击「Overdue」（link），切换到该视图 | 不适用（只读） |
| `not-due-yet.show` | `foxos accounting not-due-yet show` | 主界面 > Invoices > Not due yet | — | 点击「Not due yet」（link），切换到该视图 | 不适用（只读） |
| `paid.show` | `foxos accounting paid show` | 主界面 > Invoices > Paid | — | 点击「Paid」（link），切换到该视图 | 不适用（只读） |
| `go-banking.show` | `foxos accounting go-banking show` | 主界面 > Bank accounts > Go to banking | — | 点击「Go to banking」（link），切换到该视图 | 不适用（只读） |
| `as-table.show` | `foxos accounting as-table show` | 主界面 > Income and expenses > View as table | — | 点击「View as table」（button），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos accounting close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `home-currency.set` | `foxos accounting home-currency set` | 主界面 > dialog > Home currency | `value`（必填）, `submit` | 把「Home currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `fiscal-year-starts.set` | `foxos accounting fiscal-year-starts set` | 主界面 > dialog > Fiscal year starts in | `value`（必填）, `submit` | 把「Fiscal year starts in」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `date-format.set` | `foxos accounting date-format set` | 主界面 > dialog > Date format | `value`（必填）, `submit` | 把「Date format」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `start-sample-company-explore.toggle` | `foxos accounting start-sample-company-explore toggle` | 主界面 > dialog > Start with a sample company to explore | — | 切换「Start with a sample company to explore」 | 否（应用没有撤销入口） |
| `books.create` | `foxos accounting books create` | 主界面 > dialog > Create my books | — | 点击「Create my books」（button） | 否（应用没有撤销入口） |
