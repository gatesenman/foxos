# Shifts（shifts）操作清单

分组：business · 替代 Deputy, When I Work, Homebase · 许可证 MIT (root LICENSE) · 页面标题「Home · Shifts」

共 17 个操作，全部有语义命令（`foxos shifts <资源> <动词>`，MCP 工具 `shifts.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `theme.select` | `foxos shifts theme select` | 主界面 > theme: * | `target`（必填） | 点击名称匹配的「theme: *」项（button） | 不适用（只读） |
| `skip.dismiss` | `foxos shifts skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `home.activate` | `foxos shifts home activate` | 主界面 > Main > Home | — | 点击「Home」（button） | 否（应用没有撤销入口） |
| `schedule.schedule` | `foxos shifts schedule schedule` | 主界面 > Main > Schedule | — | 点击「Schedule」（button） | 否（应用没有撤销入口） |
| `team.activate` | `foxos shifts team activate` | 主界面 > Main > Team | — | 点击「Team」（button） | 否（应用没有撤销入口） |
| `availability.activate` | `foxos shifts availability activate` | 主界面 > Main > Availability | — | 点击「Availability」（button） | 否（应用没有撤销入口） |
| `swaps.activate` | `foxos shifts swaps activate` | 主界面 > Main > Swaps | — | 点击「Swaps」（button） | 否（应用没有撤销入口） |
| `attendance.activate` | `foxos shifts attendance activate` | 主界面 > Main > Attendance | — | 点击「Attendance」（button） | 否（应用没有撤销入口） |
| `reports.activate` | `foxos shifts reports activate` | 主界面 > Main > Reports | — | 点击「Reports」（button） | 否（应用没有撤销入口） |
| `backup-restore.activate` | `foxos shifts backup-restore activate` | 主界面 > aside > Backup & restore | — | 点击「Backup & restore」（button） | 否（应用没有撤销入口） |
| `out.sign` | `foxos shifts out sign` | 主界面 > Sign out | — | 点击「Sign out」（button） | 否（应用没有撤销入口） |
| `puter.show` | `foxos shifts puter show` | 主界面 > aside > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `employee.create` | `foxos shifts employee create` | 主界面 > main > Add employee | — | 点击「Add employee」（button） | 否（应用没有撤销入口） |
| `sample-data.import` | `foxos shifts sample-data import` | 主界面 > main > Load sample data | — | 点击「Load sample data」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos shifts close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-team.activate` | `foxos shifts set-up-team activate` | 主界面 > Welcome > Set up my team | — | 点击「Set up my team」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos shifts explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
