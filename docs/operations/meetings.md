# Meetings（meetings）操作清单

分组：collaboration · 替代 Zoom, Google Meet, Microsoft Teams · 许可证 MIT (root LICENSE) · 页面标题「Puter Meetings」

共 17 个操作，全部有语义命令（`foxos meetings <资源> <动词>`，MCP 工具 `meetings.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `item.select` | `foxos meetings item select` | 主界面 > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `meeting.create` | `foxos meetings meeting create` | New meeting > menu > create a meeting for * | `target`（必填） | 点击名称匹配的「create a meeting for *」项（menuitem） | 否（应用没有撤销入口） |
| `settings.show` | `foxos meetings settings show` | 主界面 > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `theme.toggle` | `foxos meetings theme toggle` | 主界面 > Toggle theme | — | 切换「Toggle theme」 | 否（应用没有撤销入口） |
| `out.sign` | `foxos meetings out sign` | 主界面 > Sign out | — | 点击「Sign out」（button） | 否（应用没有撤销入口） |
| `meeting-2.create` | `foxos meetings meeting-2 create` | 主界面 > main > New meeting | — | 点击「New meeting」（button） | 否（应用没有撤销入口） |
| `meeting-code-or-link.set` | `foxos meetings meeting-code-or-link set` | 主界面 > Meeting code or link | `value`（必填）, `submit` | 把「Meeting code or link」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `join.join` | `foxos meetings join join` | 主界面 > main > Join | — | 点击「Join」（button） | 否（应用没有撤销入口） |
| `today.activate` | `foxos meetings today activate` | 主界面 > aside > Today | — | 点击「Today」（button） | 否（应用没有撤销入口） |
| `week.previous` | `foxos meetings week previous` | 主界面 > Previous week | — | 点击「Previous week」（button） | 不适用（只读） |
| `week.next` | `foxos meetings week next` | 主界面 > Next week | — | 点击「Next week」（button） | 不适用（只读） |
| `try-again.activate` | `foxos meetings try-again activate` | 主界面 > aside > Try again | — | 点击「Try again」（button） | 否（应用没有撤销入口） |
| `refresh.activate` | `foxos meetings refresh activate` | 主界面 > Refresh | — | 点击「Refresh」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos meetings close close` | Settings > Close | — | 点击「Close」（button） | 不适用（只读） |
| `nickname.set` | `foxos meetings nickname set` | Settings > Nickname | `value`（必填）, `submit` | 把「Nickname」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `nickname.save` | `foxos meetings nickname save` | Settings > Settings > Save nickname | — | 点击「Save nickname」（button） | 否（应用没有撤销入口） |
| `instant-meeting.start` | `foxos meetings instant-meeting start` | New meeting > menu > Start an instant meeting | — | 点击「Start an instant meeting」（menuitem） | 否（应用没有撤销入口） |
