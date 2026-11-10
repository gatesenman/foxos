# Contracts（contracts）操作清单

分组：business · 替代 ContractSafe, Juro · 许可证 MIT (root LICENSE) · 页面标题「Contract Manager」

共 14 个操作，全部有语义命令（`foxos contracts <资源> <动词>`，MCP 工具 `contracts.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos contracts skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `content.dismiss` | `foxos contracts content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（button） | 不适用（只读） |
| `home.show` | `foxos contracts home show` | 主界面 > Main navigation > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `contracts.show` | `foxos contracts contracts show` | 主界面 > Main navigation > Contracts | — | 点击「Contracts」（link），切换到该视图 | 不适用（只读） |
| `renewals.show` | `foxos contracts renewals show` | 主界面 > Main navigation > Renewals | — | 点击「Renewals」（link），切换到该视图 | 不适用（只读） |
| `obligations.show` | `foxos contracts obligations show` | 主界面 > Main navigation > Obligations | — | 点击「Obligations」（link），切换到该视图 | 不适用（只读） |
| `contacts.show` | `foxos contracts contacts show` | 主界面 > Main navigation > Contacts | — | 点击「Contacts」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos contracts settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `contract.create` | `foxos contracts contract create` | 主界面 > Main navigation > New contract | — | 点击「New contract」（button） | 否（应用没有撤销入口） |
| `contract-2.create` | `foxos contracts contract-2 create` | 主界面 > main > New contract | — | 点击「New contract」（button） | 否（应用没有撤销入口） |
| `contract-3.create` | `foxos contracts contract-3 create` | 主界面 > main > Add a contract | — | 点击「Add a contract」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos contracts close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `first-contract.create` | `foxos contracts first-contract create` | 主界面 > Welcome > Add my first contract | — | 点击「Add my first contract」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos contracts explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
