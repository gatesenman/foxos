# Inventory（inventory）操作清单

分组：business · 替代 Zoho Inventory, Sortly, inFlow Inventory · 许可证 MIT (root LICENSE) · 页面标题「Inventory」

共 17 个操作，全部有语义命令（`foxos inventory <资源> <动词>`，MCP 工具 `inventory.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos inventory skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `searchctrl-k.activate` | `foxos inventory searchctrl-k activate` | 主界面 > Main navigation > SearchCtrl K | — | 点击「SearchCtrl K」（button） | 否（应用没有撤销入口） |
| `overview.show` | `foxos inventory overview show` | 主界面 > Main navigation > Overview | — | 点击「Overview」（link），切换到该视图 | 不适用（只读） |
| `products.show` | `foxos inventory products show` | 主界面 > Main navigation > Products | — | 点击「Products」（link），切换到该视图 | 不适用（只读） |
| `take-out.show` | `foxos inventory take-out show` | 主界面 > Main navigation > Take out | — | 点击「Take out」（link），切换到该视图 | 不适用（只读） |
| `reorder.show` | `foxos inventory reorder show` | 主界面 > Main navigation > Reorder | — | 点击「Reorder」（link），切换到该视图 | 不适用（只读） |
| `stocktake.show` | `foxos inventory stocktake show` | 主界面 > Main navigation > Stocktake | — | 点击「Stocktake」（link），切换到该视图 | 不适用（只读） |
| `history.show` | `foxos inventory history show` | 主界面 > Main navigation > History | — | 点击「History」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos inventory reports show` | 主界面 > Main navigation > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `locations.show` | `foxos inventory locations show` | 主界面 > Main navigation > Locations | — | 点击「Locations」（link），切换到该视图 | 不适用（只读） |
| `suppliers.show` | `foxos inventory suppliers show` | 主界面 > Main navigation > Suppliers | — | 点击「Suppliers」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos inventory settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `product.create` | `foxos inventory product create` | 主界面 > Main navigation > New product | — | 点击「New product」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos inventory close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-inventory.activate` | `foxos inventory set-up-inventory activate` | 主界面 > Welcome > Set up my inventory | — | 点击「Set up my inventory」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos inventory explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos inventory command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/palette.js 中定义） | 不适用 |
