# CRM（crm）操作清单

分组：business · 替代 Salesforce, HubSpot CRM, Pipedrive · 许可证 MIT (root LICENSE) · 页面标题「Sales CRM」

共 16 个操作，全部有语义命令（`foxos crm <资源> <动词>`，MCP 工具 `crm.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos crm skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `searchctrl-k.activate` | `foxos crm searchctrl-k activate` | 主界面 > Main navigation > SearchCtrl K | — | 点击「SearchCtrl K」（button） | 否（应用没有撤销入口） |
| `home.show` | `foxos crm home show` | 主界面 > Main navigation > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `pipeline.show` | `foxos crm pipeline show` | 主界面 > Main navigation > Pipeline | — | 点击「Pipeline」（link），切换到该视图 | 不适用（只读） |
| `leads.show` | `foxos crm leads show` | 主界面 > Main navigation > Leads | — | 点击「Leads」（link），切换到该视图 | 不适用（只读） |
| `follow-ups.show` | `foxos crm follow-ups show` | 主界面 > Main navigation > Follow-ups | — | 点击「Follow-ups」（link），切换到该视图 | 不适用（只读） |
| `companies.show` | `foxos crm companies show` | 主界面 > Main navigation > Companies | — | 点击「Companies」（link），切换到该视图 | 不适用（只读） |
| `activity.show` | `foxos crm activity show` | 主界面 > Main navigation > Activity | — | 点击「Activity」（link），切换到该视图 | 不适用（只读） |
| `forecast.show` | `foxos crm forecast show` | 主界面 > Main navigation > Forecast | — | 点击「Forecast」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos crm settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `lead.create` | `foxos crm lead create` | 主界面 > main > Add a lead | — | 点击「Add a lead」（button） | 否（应用没有撤销入口） |
| `me-around.show` | `foxos crm me-around show` | 主界面 > main > Show me around | — | 点击「Show me around」（button），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos crm close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-pipeline.activate` | `foxos crm set-up-pipeline activate` | 主界面 > Welcome > Set up my pipeline | — | 点击「Set up my pipeline」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos crm explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos crm command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/palette.js 中定义） | 不适用 |
