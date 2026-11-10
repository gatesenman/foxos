# Calendar（calendar）操作清单

分组：collaboration · 替代 Google Calendar, Apple Calendar, Outlook Calendar · 许可证 MIT · 页面标题「Calendar — a fast, private calendar for the web」

共 36 个操作，全部有语义命令（`foxos calendar <资源> <动词>`，MCP 工具 `calendar.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `day-view.select` | `foxos calendar day-view select` | 主界面 > Calendar view > # day view | `target`（必填） | 点击名称匹配的「# day view」项（button） | 不适用（只读） |
| `item.select` | `foxos calendar item select` | 主界面 > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `selected.select` | `foxos calendar selected select` | 主界面 > #, selected | `target`（必填） | 点击名称匹配的「#, selected」项（button） | 不适用（只读） |
| `open.open` | `foxos calendar open open` | 主界面 > open # | `target`（必填） | 点击名称匹配的「open #」项（button） | 不适用（只读） |
| `public-holiday.select` | `foxos calendar public-holiday select` | 主界面 > public holiday: * | `target`（必填） | 点击名称匹配的「public holiday: *」项（button） | 不适用（只读） |
| `year-view-open.open` | `foxos calendar year-view-open open` | Year view > main > open # | `target`（必填） | 点击名称匹配的「open #」项（button） | 不适用（只读） |
| `year-view-item.select` | `foxos calendar year-view-item select` | Year view > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `go.select` | `foxos calendar go select` | Week view > go to # | `target`（必填） | 点击名称匹配的「go to #」项（button） | 不适用（只读） |
| `week.start` | `foxos calendar week start` | Account and settings > Account and settings > start week on # | `target`（必填） | 点击名称匹配的「start week on #」项（switch） | 否（应用没有撤销入口） |
| `time.select` | `foxos calendar time select` | Account and settings > Account and settings > # time | `target`（必填） | 点击名称匹配的「# time」项（switch） | 不适用（只读） |
| `today.activate` | `foxos calendar today activate` | 主界面 > header > Today | — | 点击「Today」（button） | 否（应用没有撤销入口） |
| `previous.previous` | `foxos calendar previous previous` | 主界面 > Previous | — | 点击「Previous」（button） | 不适用（只读） |
| `next.next` | `foxos calendar next next` | 主界面 > Next | — | 点击「Next」（button） | 不适用（只读） |
| `events-tasks.search` | `foxos calendar events-tasks search` | 主界面 > Search events and tasks | — | 点击「Search events and tasks」（button） | 不适用（只读） |
| `year-view.activate` | `foxos calendar year-view activate` | 主界面 > Calendar view > Year view | — | 点击「Year view」（button） | 否（应用没有撤销入口） |
| `month-view.activate` | `foxos calendar month-view activate` | 主界面 > Calendar view > Month view | — | 点击「Month view」（button） | 否（应用没有撤销入口） |
| `week-view.activate` | `foxos calendar week-view activate` | 主界面 > Calendar view > Week view | — | 点击「Week view」（button） | 否（应用没有撤销入口） |
| `day-view.activate` | `foxos calendar day-view activate` | 主界面 > Calendar view > Day view | — | 点击「Day view」（button） | 否（应用没有撤销入口） |
| `list-view.activate` | `foxos calendar list-view activate` | 主界面 > Calendar view > List view | — | 点击「List view」（button） | 否（应用没有撤销入口） |
| `account-settings.activate` | `foxos calendar account-settings activate` | 主界面 > Account and settings | — | 点击「Account and settings」（button） | 否（应用没有撤销入口） |
| `create.create` | `foxos calendar create create` | 主界面 > Calendar navigation > Create | — | 点击「Create」（button） | 否（应用没有撤销入口） |
| `month.previous` | `foxos calendar month previous` | 主界面 > Previous month | — | 点击「Previous month」（button） | 不适用（只读） |
| `month.next` | `foxos calendar month next` | 主界面 > Next month | — | 点击「Next month」（button） | 不适用（只读） |
| `booking-links.hide` | `foxos calendar booking-links hide` | 主界面 > Calendar navigation > Hide booking links | — | 点击「Hide booking links」（button） | 不适用（只读） |
| `link-that-lets-others-book-time-you.share` | `foxos calendar link-that-lets-others-book-time-you share` | 主界面 > Calendar navigation > Share a link that lets others book time with you | — | 点击「Share a link that lets others book time with you」（button） | 否（应用没有撤销入口） |
| `event.create` | `foxos calendar event create` | List view > main > New event | — | 点击「New event」（button） | 否（应用没有撤销入口） |
| `auto.activate` | `foxos calendar auto activate` | Account and settings > Theme > Auto | — | 点击「Auto」（button） | 否（应用没有撤销入口） |
| `light.activate` | `foxos calendar light activate` | Account and settings > Theme > Light | — | 点击「Light」（button） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos calendar dark activate` | Account and settings > Theme > Dark | — | 点击「Dark」（button） | 否（应用没有撤销入口） |
| `secondary-time-zone.set` | `foxos calendar secondary-time-zone set` | Account and settings > Secondary time zone | `value`（必填）, `submit` | 把「Secondary time zone」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `public-holidays.set` | `foxos calendar public-holidays set` | Account and settings > Public holidays | `value`（必填）, `submit` | 把「Public holidays」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `clock-changes-daylight-saving.toggle` | `foxos calendar clock-changes-daylight-saving toggle` | Account and settings > Account and settings > Clock changes (daylight saving) | — | 切换「Clock changes (daylight saving)」 | 否（应用没有撤销入口） |
| `export.import` | `foxos calendar export import` | Account and settings > Account and settings > Import & export | — | 点击「Import & export」（button） | 否（应用没有撤销入口） |
| `out.sign` | `foxos calendar out sign` | Account and settings > Account and settings > Sign out | — | 点击「Sign out」（button） | 否（应用没有撤销入口） |
| `document.export` | `foxos calendar document export` | 键盘 mod+e | — | 在当前焦点上按 mod+e（src/js/modal.js 中定义） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos calendar command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/js/app.js 中定义） | 不适用 |
