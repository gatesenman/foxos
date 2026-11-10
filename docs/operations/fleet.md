# Fleet（fleet）操作清单

分组：business · 替代 Fleetio, Samsara Fleet Maintenance, Whip Around · 许可证 MIT (root LICENSE) · 页面标题「Dashboard · Fleet」

共 41 个操作，全部有语义命令（`foxos fleet <资源> <动词>`，MCP 工具 `fleet.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `content.dismiss` | `foxos fleet content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `dashboard.show` | `foxos fleet dashboard show` | 主界面 > Dashboard | — | 点击「Dashboard」（link），切换到该视图 | 不适用（只读） |
| `dashboard-2.show` | `foxos fleet dashboard-2 show` | 主界面 > Main > Dashboard | — | 点击「Dashboard」（link），切换到该视图 | 不适用（只读） |
| `vehicles.activate` | `foxos fleet vehicles activate` | 主界面 > Main > Vehicles | — | 点击「Vehicles」（button） | 否（应用没有撤销入口） |
| `inspections.activate` | `foxos fleet inspections activate` | 主界面 > Main > Inspections | — | 点击「Inspections」（button） | 否（应用没有撤销入口） |
| `issues.show` | `foxos fleet issues show` | 主界面 > Issues | — | 点击「Issues」（link），切换到该视图 | 不适用（只读） |
| `reminders.activate` | `foxos fleet reminders activate` | 主界面 > Reminders | — | 点击「Reminders」（button） | 否（应用没有撤销入口） |
| `service.activate` | `foxos fleet service activate` | 主界面 > Main > Service | — | 点击「Service」（button） | 否（应用没有撤销入口） |
| `contacts.show` | `foxos fleet contacts show` | 主界面 > Main > Contacts | — | 点击「Contacts」（link），切换到该视图 | 不适用（只读） |
| `vendors.show` | `foxos fleet vendors show` | 主界面 > Main > Vendors | — | 点击「Vendors」（link），切换到该视图 | 不适用（只读） |
| `parts-inventory.activate` | `foxos fleet parts-inventory activate` | 主界面 > Main > Parts and inventory | — | 点击「Parts and inventory」（button） | 否（应用没有撤销入口） |
| `fuel-energy.show` | `foxos fleet fuel-energy show` | 主界面 > Main > Fuel and energy | — | 点击「Fuel and energy」（link），切换到该视图 | 不适用（只读） |
| `documents.show` | `foxos fleet documents show` | 主界面 > Main > Documents | — | 点击「Documents」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos fleet reports show` | 主界面 > Main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos fleet settings show` | 主界面 > Sidebar > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos fleet source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos fleet puter show` | 主界面 > Sidebar > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `sidebar.collapse` | `foxos fleet sidebar collapse` | 主界面 > Collapse sidebar | — | 点击「Collapse sidebar」（button） | 不适用（只读） |
| `search.search` | `foxos fleet search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos fleet keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `needs-attention.activate` | `foxos fleet needs-attention activate` | 主界面 > Needs attention | — | 点击「Needs attention」（button） | 否（应用没有撤销入口） |
| `add.create` | `foxos fleet add create` | 主界面 > Add new | — | 点击「Add new」（button） | 否（应用没有撤销入口） |
| `account-appearance.activate` | `foxos fleet account-appearance activate` | 主界面 > Account and appearance | — | 点击「Account and appearance」（button） | 否（应用没有撤销入口） |
| `inspection.start` | `foxos fleet inspection start` | 主界面 > header > Start inspection | — | 点击「Start inspection」（link） | 否（应用没有撤销入口） |
| `report-issue.show` | `foxos fleet report-issue show` | 主界面 > header > Report issue | — | 点击「Report issue」（link），切换到该视图 | 不适用（只读） |
| `fuel.create` | `foxos fleet fuel create` | 主界面 > header > Add fuel | — | 点击「Add fuel」（link） | 否（应用没有撤销入口） |
| `vehicle.create` | `foxos fleet vehicle create` | 主界面 > main > Add vehicle | — | 点击「Add vehicle」（link） | 否（应用没有撤销入口） |
| `contact.create` | `foxos fleet contact create` | 主界面 > main > Add contact | — | 点击「Add contact」（link） | 否（应用没有撤销入口） |
| `inspection-forms.show` | `foxos fleet inspection-forms show` | 主界面 > main > Inspection forms | — | 点击「Inspection forms」（link），切换到该视图 | 不适用（只读） |
| `service-programs.show` | `foxos fleet service-programs show` | 主界面 > main > Service programs | — | 点击「Service programs」（link），切换到该视图 | 不适用（只读） |
| `team-access.show` | `foxos fleet team-access show` | 主界面 > main > Team access | — | 点击「Team access」（link），切换到该视图 | 不适用（只读） |
| `it.dismiss` | `foxos fleet it dismiss` | 主界面 > Early alpha notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `close.close` | `foxos fleet close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `fleet-or-company-name.set` | `foxos fleet fleet-or-company-name set` | 主界面 > dialog > Fleet or company name | `value`（必填）, `submit` | 把「Fleet or company name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `distance.set` | `foxos fleet distance set` | 主界面 > dialog > Distance | `value`（必填）, `submit` | 把「Distance」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `fuel-volume.set` | `foxos fleet fuel-volume set` | 主界面 > dialog > Fuel volume | `value`（必填）, `submit` | 把「Fuel volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `currency.set` | `foxos fleet currency set` | 主界面 > dialog > Currency | `value`（必填）, `submit` | 把「Currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sample-data.start` | `foxos fleet sample-data start` | 主界面 > dialog > Start with sample data | — | 点击「Start with sample data」（button） | 否（应用没有撤销入口） |
| `continue.activate` | `foxos fleet continue activate` | 主界面 > dialog > Continue | — | 点击「Continue」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos fleet command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shell.js 中定义） | 不适用 |
| `document.save` | `foxos fleet document save` | 键盘 mod+s | — | 在当前焦点上按 mod+s（src/ui/form.js 中定义） | 否（应用没有撤销入口） |
