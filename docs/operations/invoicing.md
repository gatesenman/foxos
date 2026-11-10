# Invoicing（invoicing）操作清单

分组：finance · 替代 FreshBooks, Zoho Invoice, Wave Invoicing · 许可证 MIT (root LICENSE) · 页面标题「Invoicing & Estimates」

共 20 个操作，全部有语义命令（`foxos invoicing <资源> <动词>`，MCP 工具 `invoicing.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos invoicing skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `content.dismiss` | `foxos invoicing content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `switch-dark-theme.activate` | `foxos invoicing switch-dark-theme activate` | 主界面 > Switch to dark theme | — | 点击「Switch to dark theme」（button） | 否（应用没有撤销入口） |
| `home.show` | `foxos invoicing home show` | 主界面 > Main navigation > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `invoices.show` | `foxos invoicing invoices show` | 主界面 > Main navigation > Invoices | — | 点击「Invoices」（link），切换到该视图 | 不适用（只读） |
| `estimates.show` | `foxos invoicing estimates show` | 主界面 > Main navigation > Estimates | — | 点击「Estimates」（link），切换到该视图 | 不适用（只读） |
| `recurring.show` | `foxos invoicing recurring show` | 主界面 > Main navigation > Recurring | — | 点击「Recurring」（link），切换到该视图 | 不适用（只读） |
| `clients.show` | `foxos invoicing clients show` | 主界面 > Main navigation > Clients | — | 点击「Clients」（link），切换到该视图 | 不适用（只读） |
| `receipts.show` | `foxos invoicing receipts show` | 主界面 > Main navigation > Receipts | — | 点击「Receipts」（link），切换到该视图 | 不适用（只读） |
| `saved-items.show` | `foxos invoicing saved-items show` | 主界面 > Main navigation > Saved items | — | 点击「Saved items」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos invoicing reports show` | 主界面 > Main navigation > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `trash.delete` | `foxos invoicing trash delete` | 主界面 > Main navigation > Trash | — | 点击「Trash」（link） | 否（应用没有撤销入口） |
| `invoice.create` | `foxos invoicing invoice create` | 主界面 > Main navigation > New invoice | — | 点击「New invoice」（button） | 否（应用没有撤销入口） |
| `estimate.create` | `foxos invoicing estimate create` | 主界面 > Main navigation > New estimate | — | 点击「New estimate」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos invoicing settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `invoice-2.create` | `foxos invoicing invoice-2 create` | 主界面 > main > New invoice | — | 点击「New invoice」（button） | 否（应用没有撤销入口） |
| `estimate-2.create` | `foxos invoicing estimate-2 create` | 主界面 > main > New estimate | — | 点击「New estimate」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos invoicing close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-business.activate` | `foxos invoicing set-up-business activate` | 主界面 > Welcome > Set up my business | — | 点击「Set up my business」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos invoicing explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
