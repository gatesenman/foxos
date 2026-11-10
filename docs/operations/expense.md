# Expenses（expense）操作清单

分组：finance · 替代 Expensify, SAP Concur, Zoho Expense · 许可证 MIT (root LICENSE) · 页面标题「Expenses」

共 17 个操作，全部有语义命令（`foxos expense <资源> <动词>`，MCP 工具 `expense.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `month-nothing-last-month.select` | `foxos expense month-nothing-last-month select` | 主界面 > main > this month$# nothing last month | `target`（必填） | 点击名称匹配的「this month$# nothing last month」项（button） | 不适用（只读） |
| `not-report-expenses.select` | `foxos expense not-report-expenses select` | 主界面 > main > not in a report$# expenses | `target`（必填） | 点击名称匹配的「not in a report$# expenses」项（button） | 不适用（只读） |
| `awaiting-reimbursement-expenses-flight.select` | `foxos expense awaiting-reimbursement-expenses-flight select` | 主界面 > main > awaiting reimbursement$# expenses in flight | `target`（必填） | 点击名称匹配的「awaiting reimbursement$# expenses in flight」项（button） | 不适用（只读） |
| `lines-open.select` | `foxos expense lines-open select` | 主界面 > main > to # lines open | `target`（必填） | 点击名称匹配的「to # lines open」项（button） | 不适用（只读） |
| `skip.dismiss` | `foxos expense skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `content.dismiss` | `foxos expense content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `home.show` | `foxos expense home show` | 主界面 > Main navigation > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `expenses.show` | `foxos expense expenses show` | 主界面 > Main navigation > Expenses | — | 点击「Expenses」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos expense reports show` | 主界面 > Main navigation > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `reconcile.show` | `foxos expense reconcile show` | 主界面 > Main navigation > Reconcile | — | 点击「Reconcile」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos expense settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `capture-receipt.activate` | `foxos expense capture-receipt activate` | 主界面 > Main navigation > Capture receipt | — | 点击「Capture receipt」（button） | 否（应用没有撤销入口） |
| `manual-entry.activate` | `foxos expense manual-entry activate` | 主界面 > main > Manual entry | — | 点击「Manual entry」（button） | 否（应用没有撤销入口） |
| `capture-receipt-2.activate` | `foxos expense capture-receipt-2 activate` | 主界面 > main > Capture receipt | — | 点击「Capture receipt」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos expense close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-expenses.activate` | `foxos expense set-up-expenses activate` | 主界面 > Welcome > Set up my expenses | — | 点击「Set up my expenses」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos expense explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
