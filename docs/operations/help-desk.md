# Help Desk（help-desk）操作清单

分组：business · 替代 Zendesk, Freshdesk, Intercom, Help Scout · 许可证 MIT · 页面标题「Help Desk」

共 6 个操作，全部有语义命令（`foxos help-desk <资源> <动词>`，MCP 工具 `help-desk.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `help-desk-name.set` | `foxos help-desk help-desk-name set` | 主界面 > main > Help desk name | `value`（必填）, `submit` | 把「Help desk name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `name.set` | `foxos help-desk name set` | 主界面 > main > Your name | `value`（必填）, `submit` | 把「Your name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `help-desk.create` | `foxos help-desk help-desk create` | 主界面 > main > Create help desk | — | 点击「Create help desk」（button） | 否（应用没有撤销入口） |
| `source-code.show` | `foxos help-desk source-code show` | 主界面 > main > Source code | — | 点击「Source code」（link），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos help-desk puter show` | 主界面 > main > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `dismiss.dismiss` | `foxos help-desk dismiss dismiss` | 主界面 > Dismiss | — | 点击「Dismiss」（button） | 不适用（只读） |
