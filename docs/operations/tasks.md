# Tasks（tasks）操作清单

分组：productivity · 替代 Todoist, Microsoft To Do, TickTick · 许可证 MIT (root LICENSE) · 页面标题「Tasks」

共 58 个操作，全部有语义命令（`foxos tasks <资源> <动词>`，MCP 工具 `tasks.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `add.create` | `foxos tasks add create` | 主界面 > header > add for * | `target`（必填） | 点击名称匹配的「add for *」项（button） | 否（应用没有撤销入口） |
| `skip.dismiss` | `foxos tasks skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `list.open` | `foxos tasks list open` | Lists > open list: * | `target`（必填） | 点击名称匹配的「open list: *」项（button） | 不适用（只读） |
| `actions.select` | `foxos tasks actions select` | Lists > actions for * | `target`（必填） | 点击名称匹配的「actions for *」项（button） | 不适用（只读） |
| `tasks.open` | `foxos tasks tasks open` | Calendar > # open tasks | `target`（必填） | 点击名称匹配的「# open tasks」项（button） | 不适用（只读） |
| `week-starts.select` | `foxos tasks week-starts select` | Settings > week starts on # | `target`（必填） | 点击名称匹配的「week starts on #」项（switch） | 不适用（只读） |
| `content.dismiss` | `foxos tasks content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `task.create` | `foxos tasks task create` | 主界面 > aside > New task | — | 点击「New task」（button） | 否（应用没有撤销入口） |
| `today.show` | `foxos tasks today show` | 主界面 > Main > Today | — | 点击「Today」（link），切换到该视图 | 不适用（只读） |
| `upcoming.show` | `foxos tasks upcoming show` | 主界面 > Main > Upcoming | — | 点击「Upcoming」（link），切换到该视图 | 不适用（只读） |
| `lists.show` | `foxos tasks lists show` | 主界面 > Main > Lists | — | 点击「Lists」（link），切换到该视图 | 不适用（只读） |
| `calendar.show` | `foxos tasks calendar show` | 主界面 > Main > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `logbook.show` | `foxos tasks logbook show` | 主界面 > Main > Logbook | — | 点击「Logbook」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos tasks settings show` | 主界面 > Main > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `list.create` | `foxos tasks list create` | 主界面 > New list | — | 点击「New list」（button） | 否（应用没有撤销入口） |
| `personal.show` | `foxos tasks personal show` | 主界面 > Main > Personal | — | 点击「Personal」（link），切换到该视图 | 不适用（只读） |
| `work.show` | `foxos tasks work show` | 主界面 > Main > Work | — | 点击「Work」（link），切换到该视图 | 不适用（只读） |
| `search.search` | `foxos tasks search search` | 主界面 > aside > Search/ | — | 点击「Search/」（button） | 不适用（只读） |
| `add-task.set` | `foxos tasks add-task set` | 主界面 > Add a task | `value`（必填）, `submit` | 把「Add a task」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `options.show` | `foxos tasks options show` | 主界面 > More options | — | 点击「More options」（button），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos tasks close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `first-task.create` | `foxos tasks first-task create` | 主界面 > Welcome > Add my first task | — | 点击「Add my first task」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos tasks explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `task-title.set` | `foxos tasks task-title set` | New task > Task title | `value`（必填）, `submit` | 把「Task title」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `notes.set` | `foxos tasks notes set` | New task > New task > Notes | `value`（必填）, `submit` | 把「Notes」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `list.set` | `foxos tasks list set` | New task > New task > List | `value`（必填）, `submit` | 把「List」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `due-date.set` | `foxos tasks due-date set` | New task > Due date | `value`（必填）, `submit` | 把「Due date」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `due-time.set` | `foxos tasks due-time set` | New task > Due time | `value`（必填）, `submit` | 把「Due time」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `today.activate` | `foxos tasks today activate` | New task > New task > Today | — | 点击「Today」（button） | 否（应用没有撤销入口） |
| `tomorrow.activate` | `foxos tasks tomorrow activate` | New task > New task > Tomorrow | — | 点击「Tomorrow」（button） | 否（应用没有撤销入口） |
| `week.next` | `foxos tasks week next` | New task > New task > Next week | — | 点击「Next week」（button） | 不适用（只读） |
| `no-date.activate` | `foxos tasks no-date activate` | New task > New task > No date | — | 点击「No date」（button） | 否（应用没有撤销入口） |
| `remind-me.set` | `foxos tasks remind-me set` | New task > New task > Remind me | `value`（必填）, `submit` | 把「Remind me」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `none.activate` | `foxos tasks none activate` | New task > Priority > None | — | 点击「None」（button） | 否（应用没有撤销入口） |
| `low.activate` | `foxos tasks low activate` | New task > Priority > Low | — | 点击「Low」（button） | 否（应用没有撤销入口） |
| `medium.activate` | `foxos tasks medium activate` | New task > Priority > Medium | — | 点击「Medium」（button） | 否（应用没有撤销入口） |
| `high.activate` | `foxos tasks high activate` | New task > Priority > High | — | 点击「High」（button） | 否（应用没有撤销入口） |
| `add-tag.set` | `foxos tasks add-tag set` | New task > Add a tag | `value`（必填）, `submit` | 把「Add a tag」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `repeat.set` | `foxos tasks repeat set` | New task > New task > Repeat | `value`（必填）, `submit` | 把「Repeat」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `subtask.create` | `foxos tasks subtask create` | New task > New task > Add subtask | — | 点击「Add subtask」（button） | 否（应用没有撤销入口） |
| `cancel.cancel` | `foxos tasks cancel cancel` | New task > New task > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `task-2.create` | `foxos tasks task-2 create` | New task > New task > Add task | — | 点击「Add task」（button） | 否（应用没有撤销入口） |
| `upcoming-task.create` | `foxos tasks upcoming-task create` | Upcoming > header > New task | — | 点击「New task」（button） | 否（应用没有撤销入口） |
| `lists-list.create` | `foxos tasks lists-list create` | Lists > header > New list | — | 点击「New list」（button） | 否（应用没有撤销入口） |
| `ics-calendar-file.export` | `foxos tasks ics-calendar-file export` | Calendar > Download .ics calendar file | — | 点击「Download .ics calendar file」（button） | 否（应用没有撤销入口） |
| `month.previous` | `foxos tasks month previous` | Calendar > Previous month | — | 点击「Previous month」（button） | 不适用（只读） |
| `calendar-today.activate` | `foxos tasks calendar-today activate` | Calendar > header > Today | — | 点击「Today」（button） | 否（应用没有撤销入口） |
| `month.next` | `foxos tasks month next` | Calendar > Next month | — | 点击「Next month」（button） | 不适用（只读） |
| `system.activate` | `foxos tasks system activate` | Settings > Theme > System | — | 点击「System」（button） | 否（应用没有撤销入口） |
| `light.activate` | `foxos tasks light activate` | Settings > Theme > Light | — | 点击「Light」（button） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos tasks dark activate` | Settings > Theme > Dark | — | 点击「Dark」（button） | 否（应用没有撤销入口） |
| `due-date-reminders.toggle` | `foxos tasks due-date-reminders toggle` | Settings > Due-date reminders | — | 切换「Due-date reminders」 | 否（应用没有撤销入口） |
| `exportdownload-everything-as-json-file.activate` | `foxos tasks exportdownload-everything-as-json-file activate` | Settings > main > ExportDownload everything as a JSON file | — | 点击「ExportDownload everything as a JSON file」（button） | 否（应用没有撤销入口） |
| `lists.previous` | `foxos tasks lists previous` | Personal > Back to lists | — | 点击「Back to lists」（button） | 不适用（只读） |
| `list.share` | `foxos tasks list share` | Personal > Share list | — | 点击「Share list」（button） | 否（应用没有撤销入口） |
| `list.update` | `foxos tasks list update` | Personal > Edit list | — | 点击「Edit list」（button） | 否（应用没有撤销入口） |
| `personal-add.create` | `foxos tasks personal-add create` | Personal > header > Add | — | 点击「Add」（button） | 否（应用没有撤销入口） |
| `search-tasks.set` | `foxos tasks search-tasks set` | Search/ > Search tasks | `value`（必填）, `submit` | 把「Search tasks」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
