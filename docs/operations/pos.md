# Point of Sale（pos）操作清单

分组：business · 替代 Square POS, Shopify POS, Lightspeed · 许可证 MIT (root LICENSE) · 页面标题「Register · Point of Sale」

共 17 个操作，全部有语义命令（`foxos pos <资源> <动词>`，MCP 工具 `pos.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos pos skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `register.show` | `foxos pos register show` | 主界面 > Main navigation > Register | — | 点击「Register」（link），切换到该视图 | 不适用（只读） |
| `products.show` | `foxos pos products show` | 主界面 > Main navigation > Products | — | 点击「Products」（link），切换到该视图 | 不适用（只读） |
| `receipts.show` | `foxos pos receipts show` | 主界面 > Main navigation > Receipts | — | 点击「Receipts」（link），切换到该视图 | 不适用（只读） |
| `customers.show` | `foxos pos customers show` | 主界面 > Main navigation > Customers | — | 点击「Customers」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos pos reports show` | 主界面 > Main navigation > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos pos settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `search-products-or-scan-barcode.set` | `foxos pos search-products-or-scan-barcode set` | 主界面 > Search products or scan a barcode | `value`（必填）, `submit` | 把「Search products or scan a barcode」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `cash-drawer.activate` | `foxos pos cash-drawer activate` | 主界面 > Cash drawer | — | 点击「Cash drawer」（button） | 否（应用没有撤销入口） |
| `products.create` | `foxos pos products create` | 主界面 > Product catalog > Add products | — | 点击「Add products」（link） | 否（应用没有撤销入口） |
| `custom-item.create` | `foxos pos custom-item create` | 主界面 > Add a custom item | — | 点击「Add a custom item」（button） | 否（应用没有撤销入口） |
| `park-sale-serve-next-customer.activate` | `foxos pos park-sale-serve-next-customer activate` | 主界面 > Current sale > Park this sale and serve the next customer | — | 点击「Park this sale and serve the next customer」（button） | 否（应用没有撤销入口） |
| `clear.clear` | `foxos pos clear clear` | 主界面 > Current sale > Clear | — | 点击「Clear」（button） | 否（应用没有撤销入口） |
| `charge.activate` | `foxos pos charge activate` | 主界面 > Current sale > Charge | — | 点击「Charge」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos pos close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-store.activate` | `foxos pos set-up-store activate` | 主界面 > Welcome > Set up my store | — | 点击「Set up my store」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos pos explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
