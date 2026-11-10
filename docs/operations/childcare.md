# Childcare（childcare）操作清单

分组：business · 替代 brightwheel, Procare, HiMama · 许可证 MIT (root LICENSE) · 页面标题「Good evening · Childcare」

共 39 个操作，全部有语义命令（`foxos childcare <资源> <动词>`，MCP 工具 `childcare.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `children-enrolled.select` | `foxos childcare children-enrolled select` | 主界面 > main > children # enrolled | `target`（必填） | 点击名称匹配的「children # enrolled」项（link） | 不适用（只读） |
| `absent-reported.select` | `foxos childcare absent-reported select` | 主界面 > main > absent # reported | `target`（必填） | 点击名称匹配的「absent # reported」项（link） | 不适用（只读） |
| `staff-staff-members.select` | `foxos childcare staff-staff-members select` | 主界面 > main > staff on # staff members | `target`（必填） | 点击名称匹配的「staff on # staff members」项（link） | 不适用（只读） |
| `ratio-rooms-ratio.select` | `foxos childcare ratio-rooms-ratio select` | 主界面 > main > ratio # rooms in ratio | `target`（必填） | 点击名称匹配的「ratio # rooms in ratio」项（link） | 不适用（只读） |
| `content.dismiss` | `foxos childcare content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `log-or-add-n.activate` | `foxos childcare log-or-add-n activate` | 主界面 > aside > Log or add (N) | — | 点击「Log or add (N)」（button） | 否（应用没有撤销入口） |
| `home.show` | `foxos childcare home show` | 主界面 > Main > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `check-in.show` | `foxos childcare check-in show` | 主界面 > Main > Check-in | — | 点击「Check-in」（link），切换到该视图 | 不适用（只读） |
| `activities.show` | `foxos childcare activities show` | 主界面 > Main > Activities | — | 点击「Activities」（link），切换到该视图 | 不适用（只读） |
| `messages.show` | `foxos childcare messages show` | 主界面 > Messages | — | 点击「Messages」（link），切换到该视图 | 不适用（只读） |
| `children.show` | `foxos childcare children show` | 主界面 > Main > Children | — | 点击「Children」（link），切换到该视图 | 不适用（只读） |
| `families.show` | `foxos childcare families show` | 主界面 > Main > Families | — | 点击「Families」（link），切换到该视图 | 不适用（只读） |
| `rooms.show` | `foxos childcare rooms show` | 主界面 > Main > Rooms | — | 点击「Rooms」（link），切换到该视图 | 不适用（只读） |
| `staff.show` | `foxos childcare staff show` | 主界面 > Main > Staff | — | 点击「Staff」（link），切换到该视图 | 不适用（只读） |
| `calendar.show` | `foxos childcare calendar show` | 主界面 > Main > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `menus.show` | `foxos childcare menus show` | 主界面 > Main > Menus | — | 点击「Menus」（link），切换到该视图 | 不适用（只读） |
| `billing.show` | `foxos childcare billing show` | 主界面 > Billing | — | 点击「Billing」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos childcare reports show` | 主界面 > Main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos childcare source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos childcare puter show` | 主界面 > aside > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `navigation.collapse` | `foxos childcare navigation collapse` | 主界面 > Collapse navigation | — | 点击「Collapse navigation」（button） | 不适用（只读） |
| `search.search` | `foxos childcare search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos childcare keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos childcare settings show` | 主界面 > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `account-appearance.activate` | `foxos childcare account-appearance activate` | 主界面 > Account and appearance | — | 点击「Account and appearance」（button） | 否（应用没有撤销入口） |
| `kiosk.show` | `foxos childcare kiosk show` | 主界面 > header > Kiosk | — | 点击「Kiosk」（link），切换到该视图 | 不适用（只读） |
| `check.run` | `foxos childcare check run` | 主界面 > header > Check in | — | 点击「Check in」（link） | 否（应用没有撤销入口） |
| `log-activity.activate` | `foxos childcare log-activity activate` | 主界面 > header > Log activity | — | 点击「Log activity」（button） | 否（应用没有撤销入口） |
| `room.create` | `foxos childcare room create` | 主界面 > main > Add a room | — | 点击「Add a room」（link） | 否（应用没有撤销入口） |
| `log.open` | `foxos childcare log open` | 主界面 > main > Open log | — | 点击「Open log」（link） | 不适用（只读） |
| `log-activity-2.activate` | `foxos childcare log-activity-2 activate` | 主界面 > main > Log an activity | — | 点击「Log an activity」（button） | 否（应用没有撤销入口） |
| `calendar-2.show` | `foxos childcare calendar-2 show` | 主界面 > main > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `it.dismiss` | `foxos childcare it dismiss` | 主界面 > Early alpha notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `close.close` | `foxos childcare close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `school-name.set` | `foxos childcare school-name set` | 主界面 > dialog > School name | `value`（必填）, `submit` | 把「School name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `rooms.set` | `foxos childcare rooms set` | 主界面 > dialog > Rooms | `value`（必填）, `submit` | 把「Rooms」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `use-sample-data.activate` | `foxos childcare use-sample-data activate` | 主界面 > dialog > Use sample data | — | 点击「Use sample data」（button） | 否（应用没有撤销入口） |
| `get-started.activate` | `foxos childcare get-started activate` | 主界面 > dialog > Get started | — | 点击「Get started」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos childcare command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shell.js 中定义） | 不适用 |
