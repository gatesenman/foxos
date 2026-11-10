# Projects（projects）操作清单

分组：productivity · 替代 Trello, Asana, monday.com · 许可证 MIT · 页面标题「Project Management」

共 50 个操作，全部有语义命令（`foxos projects <资源> <动词>`，MCP 工具 `projects.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos projects skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `projects.show` | `foxos projects projects show` | 主界面 > Main navigation > Projects | — | 点击「Projects」（link），切换到该视图 | 不适用（只读） |
| `quick-addn.activate` | `foxos projects quick-addn activate` | 主界面 > Main navigation > Quick addn | — | 点击「Quick addn」（button） | 可能（应用提供撤销，未逐项验证） |
| `task.search` | `foxos projects task search` | 主界面 > Main navigation > Find a task/ | — | 点击「Find a task/」（button） | 不适用（只读） |
| `commandsctrlk.activate` | `foxos projects commandsctrlk activate` | 主界面 > Main navigation > CommandsCtrlK | — | 点击「CommandsCtrlK」（button） | 可能（应用提供撤销，未逐项验证） |
| `today.show` | `foxos projects today show` | 主界面 > Main navigation > Today | — | 点击「Today」（link），切换到该视图 | 不适用（只读） |
| `tasks.show` | `foxos projects tasks show` | 主界面 > Main navigation > All tasks | — | 点击「All tasks」（link），切换到该视图 | 不适用（只读） |
| `project.create` | `foxos projects project create` | 主界面 > New project | — | 点击「New project」（button） | 可能（应用提供撤销，未逐项验证） |
| `projects-2.show` | `foxos projects projects-2 show` | 主界面 > Main navigation > All projects | — | 点击「All projects」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos projects settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `project-2.create` | `foxos projects project-2 create` | 主界面 > header > New project | — | 点击「New project」（button） | 可能（应用提供撤销，未逐项验证） |
| `project-3.create` | `foxos projects project-3 create` | 主界面 > main > Create a project | — | 点击「Create a project」（button） | 可能（应用提供撤销，未逐项验证） |
| `close.close` | `foxos projects close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `first-project.create` | `foxos projects first-project create` | 主界面 > Welcome > Create my first project | — | 点击「Create my first project」（button） | 可能（应用提供撤销，未逐项验证） |
| `explore-sample-data.activate` | `foxos projects explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 可能（应用提供撤销，未逐项验证） |
| `today-projects.show` | `foxos projects today-projects show` | Today > All projects | — | 点击「All projects」（link），切换到该视图 | 不适用（只读） |
| `overdue.show` | `foxos projects overdue show` | All tasks > Saved views > Show Overdue | — | 点击「Show Overdue」（button），切换到该视图 | 不适用（只读） |
| `high-priority.show` | `foxos projects high-priority show` | All tasks > Saved views > Show High priority | — | 点击「Show High priority」（button），切换到该视图 | 不适用（只读） |
| `unscheduled.show` | `foxos projects unscheduled show` | All tasks > Saved views > Show Unscheduled | — | 点击「Show Unscheduled」（button），切换到该视图 | 不适用（只读） |
| `options.show` | `foxos projects options show` | All tasks > View options | — | 点击「View options」（button），切换到该视图 | 不适用（只读） |
| `filter-tasks-by-title.set` | `foxos projects filter-tasks-by-title set` | All tasks > Filter tasks by title | `value`（必填）, `submit` | 把「Filter tasks by title」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `label.activate` | `foxos projects label activate` | All tasks > Label | — | 点击「Label」（button） | 可能（应用提供撤销，未逐项验证） |
| `assignee.activate` | `foxos projects assignee activate` | All tasks > Assignee | — | 点击「Assignee」（button） | 可能（应用提供撤销，未逐项验证） |
| `priority.activate` | `foxos projects priority activate` | All tasks > Priority | — | 点击「Priority」（button） | 可能（应用提供撤销，未逐项验证） |
| `due.activate` | `foxos projects due activate` | All tasks > Due | — | 点击「Due」（button） | 可能（应用提供撤销，未逐项验证） |
| `project.activate` | `foxos projects project activate` | All tasks > main > Project | — | 点击「Project」（button） | 可能（应用提供撤销，未逐项验证） |
| `project-order.activate` | `foxos projects project-order activate` | All tasks > main > Project order | — | 点击「Project order」（button） | 可能（应用提供撤销，未逐项验证） |
| `light.toggle` | `foxos projects light toggle` | Settings > Theme > Light | — | 切换「Light」 | 可能（应用提供撤销，未逐项验证） |
| `dark.toggle` | `foxos projects dark toggle` | Settings > Theme > Dark | — | 切换「Dark」 | 可能（应用提供撤销，未逐项验证） |
| `system.toggle` | `foxos projects system toggle` | Settings > Theme > System | — | 切换「System」 | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos projects view show` | Settings > main > View | — | 点击「View」（button），切换到该视图 | 不适用（只读） |
| `export.export` | `foxos projects export export` | Settings > main > Export | — | 点击「Export」（button） | 可能（应用提供撤销，未逐项验证） |
| `import.import` | `foxos projects import import` | Settings > main > Import | — | 点击「Import」（button） | 可能（应用提供撤销，未逐项验证） |
| `calendar-file.export` | `foxos projects calendar-file export` | Settings > Export a calendar file | — | 点击「Export a calendar file」（button） | 可能（应用提供撤销，未逐项验证） |
| `restore-points.open` | `foxos projects restore-points open` | Settings > Open restore points | — | 点击「Open restore points」（button） | 不适用（只读） |
| `deleted-projects.open` | `foxos projects deleted-projects open` | Settings > Open deleted projects | — | 点击「Open deleted projects」（button） | 不适用（只读） |
| `learn-more.show` | `foxos projects learn-more show` | Settings > main > Learn more | — | 点击「Learn more」（link），切换到该视图 | 不适用（只读） |
| `name.set` | `foxos projects name set` | New project > New project > Name | `value`（必填）, `submit` | 把「Name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `purple.toggle` | `foxos projects purple toggle` | New project > Purple | — | 切换「Purple」 | 可能（应用提供撤销，未逐项验证） |
| `teal.toggle` | `foxos projects teal toggle` | New project > Teal | — | 切换「Teal」 | 可能（应用提供撤销，未逐项验证） |
| `amber.toggle` | `foxos projects amber toggle` | New project > Amber | — | 切换「Amber」 | 可能（应用提供撤销，未逐项验证） |
| `rose.toggle` | `foxos projects rose toggle` | New project > Rose | — | 切换「Rose」 | 可能（应用提供撤销，未逐项验证） |
| `indigo.toggle` | `foxos projects indigo toggle` | New project > Indigo | — | 切换「Indigo」 | 可能（应用提供撤销，未逐项验证） |
| `blue.toggle` | `foxos projects blue toggle` | New project > Blue | — | 切换「Blue」 | 可能（应用提供撤销，未逐项验证） |
| `olive.toggle` | `foxos projects olive toggle` | New project > Olive | — | 切换「Olive」 | 可能（应用提供撤销，未逐项验证） |
| `rust.toggle` | `foxos projects rust toggle` | New project > Rust | — | 切换「Rust」 | 可能（应用提供撤销，未逐项验证） |
| `cancel.cancel` | `foxos projects cancel cancel` | New project > New project > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `project-4.create` | `foxos projects project-4 create` | New project > New project > Create project | — | 点击「Create project」（button） | 可能（应用提供撤销，未逐项验证） |
| `command-palette.show` | `foxos projects command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shortcuts.js 中定义） | 不适用 |
| `edit.undo` | `foxos projects edit undo` | 键盘 mod+z | — | 在当前焦点上按 mod+z（src/ui/shortcuts.js 中定义） | 不适用 |
