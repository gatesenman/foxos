# Time Tracking（time-tracking）操作清单

分组：productivity · 替代 Toggl Track, Harvest, Clockify · 许可证 MIT (root LICENSE) · 页面标题「Hourly · Time Tracking」

共 71 个操作，全部有语义命令（`foxos time-tracking <资源> <动词>`，MCP 工具 `time-tracking.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos time-tracking skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `nov-9-nov-15-0m-across-0-days.select` | `foxos time-tracking nov-9-nov-15-0m-across-0-days select` | Timesheet > Nov 9 - Nov 15: 0m across 0 days > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `log-time.select` | `foxos time-tracking log-time select` | Timesheet > log time on # | `target`（必填） | 点击名称匹配的「log time on #」项（button） | 不适用（只读） |
| `printable-timesheet.select` | `foxos time-tracking printable-timesheet select` | Reports > main > a printable timesheet for * | `target`（必填） | 点击名称匹配的「a printable timesheet for *」项（button） | 不适用（只读） |
| `backup-from.export` | `foxos time-tracking backup-from export` | Settings > download the backup from # | `target`（必填） | 点击名称匹配的「download the backup from #」项（button） | 否（应用没有撤销入口） |
| `restore-backup-from.select` | `foxos time-tracking restore-backup-from select` | Settings > restore the backup from # | `target`（必填） | 点击名称匹配的「restore the backup from #」项（button） | 不适用（只读） |
| `csvevery-entry-ready.export` | `foxos time-tracking csvevery-entry-ready export` | Settings > main > export csvevery entry, ready for * | `target`（必填） | 点击名称匹配的「export csvevery entry, ready for *」项（button） | 否（应用没有撤销入口） |
| `content.dismiss` | `foxos time-tracking content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（button） | 不适用（只读） |
| `timer.show` | `foxos time-tracking timer show` | 主界面 > Main navigation > Timer | — | 点击「Timer」（link），切换到该视图 | 不适用（只读） |
| `timesheet.show` | `foxos time-tracking timesheet show` | 主界面 > Main navigation > Timesheet | — | 点击「Timesheet」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos time-tracking reports show` | 主界面 > Main navigation > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `projects.show` | `foxos time-tracking projects show` | 主界面 > Main navigation > Projects | — | 点击「Projects」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos time-tracking settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `log-time.activate` | `foxos time-tracking log-time activate` | 主界面 > Main navigation > Log time | — | 点击「Log time」（button） | 否（应用没有撤销入口） |
| `client.create` | `foxos time-tracking client create` | 主界面 > Timer > Add a client | — | 点击「Add a client」（link） | 否（应用没有撤销入口） |
| `close.close` | `foxos time-tracking close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-tracking.activate` | `foxos time-tracking set-up-tracking activate` | 主界面 > Welcome > Set up tracking | — | 点击「Set up tracking」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos time-tracking explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `jump-date.activate` | `foxos time-tracking jump-date activate` | Timesheet > main > Jump to a date | — | 点击「Jump to a date」（button） | 否（应用没有撤销入口） |
| `entries.search` | `foxos time-tracking entries search` | Timesheet > Search entries | — | 点击「Search entries」（button） | 不适用（只读） |
| `week.activate` | `foxos time-tracking week activate` | Timesheet > Timesheet unit > Week | — | 点击「Week」（button） | 否（应用没有撤销入口） |
| `grid.activate` | `foxos time-tracking grid activate` | Timesheet > Timesheet unit > Grid | — | 点击「Grid」（button） | 否（应用没有撤销入口） |
| `month.activate` | `foxos time-tracking month activate` | Timesheet > Timesheet unit > Month | — | 点击「Month」（button） | 否（应用没有撤销入口） |
| `week.previous` | `foxos time-tracking week previous` | Timesheet > Previous week | — | 点击「Previous week」（button） | 不适用（只读） |
| `today.activate` | `foxos time-tracking today activate` | Timesheet > Timesheet navigation > Today | — | 点击「Today」（button） | 否（应用没有撤销入口） |
| `week.next` | `foxos time-tracking week next` | Timesheet > Next week | — | 点击「Next week」（button） | 不适用（只读） |
| `log-time-yesterday.activate` | `foxos time-tracking log-time-yesterday activate` | Timesheet > Log time on Yesterday | — | 点击「Log time on Yesterday」（button） | 否（应用没有撤销入口） |
| `log-time-today.activate` | `foxos time-tracking log-time-today activate` | Timesheet > Log time on Today | — | 点击「Log time on Today」（button） | 否（应用没有撤销入口） |
| `invoice-ready-summary-report.print` | `foxos time-tracking invoice-ready-summary-report print` | Reports > main > Print an invoice-ready summary of this report | — | 点击「Print an invoice-ready summary of this report」（button） | 不适用（只读） |
| `csv.export` | `foxos time-tracking csv export` | Reports > main > Export CSV | — | 点击「Export CSV」（button） | 否（应用没有撤销入口） |
| `report.activate` | `foxos time-tracking report activate` | Reports > Reports view > Report | — | 点击「Report」（button） | 否（应用没有撤销入口） |
| `insights.activate` | `foxos time-tracking insights activate` | Reports > Reports view > Insights | — | 点击「Insights」（button） | 否（应用没有撤销入口） |
| `invoices.activate` | `foxos time-tracking invoices activate` | Reports > Reports view > Invoices | — | 点击「Invoices」（button） | 否（应用没有撤销入口） |
| `reports-week.activate` | `foxos time-tracking reports-week activate` | Reports > Date range > This week | — | 点击「This week」（button） | 否（应用没有撤销入口） |
| `last-week.activate` | `foxos time-tracking last-week activate` | Reports > Date range > Last week | — | 点击「Last week」（button） | 否（应用没有撤销入口） |
| `reports-month.activate` | `foxos time-tracking reports-month activate` | Reports > Date range > This month | — | 点击「This month」（button） | 否（应用没有撤销入口） |
| `last-month.activate` | `foxos time-tracking last-month activate` | Reports > Date range > Last month | — | 点击「Last month」（button） | 否（应用没有撤销入口） |
| `custom.activate` | `foxos time-tracking custom activate` | Reports > Date range > Custom | — | 点击「Custom」（button） | 否（应用没有撤销入口） |
| `client.activate` | `foxos time-tracking client activate` | Reports > Group by > Client | — | 点击「Client」（button） | 否（应用没有撤销入口） |
| `project.activate` | `foxos time-tracking project activate` | Reports > Group by > Project | — | 点击「Project」（button） | 否（应用没有撤销入口） |
| `task.activate` | `foxos time-tracking task activate` | Reports > Group by > Task | — | 点击「Task」（button） | 否（应用没有撤销入口） |
| `unbilled.activate` | `foxos time-tracking unbilled activate` | Reports > Billing state > Unbilled | — | 点击「Unbilled」（button） | 否（应用没有撤销入口） |
| `invoiced.activate` | `foxos time-tracking invoiced activate` | Reports > Billing state > Invoiced | — | 点击「Invoiced」（button） | 否（应用没有撤销入口） |
| `projects-client.create` | `foxos time-tracking projects-client create` | Projects > main > New client | — | 点击「New client」（button） | 否（应用没有撤销入口） |
| `first-client.create` | `foxos time-tracking first-client create` | Projects > main > Add your first client | — | 点击「Add your first client」（button） | 否（应用没有撤销入口） |
| `light.activate` | `foxos time-tracking light activate` | Settings > Theme > Light | — | 点击「Light」（button） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos time-tracking dark activate` | Settings > Theme > Dark | — | 点击「Dark」（button） | 否（应用没有撤销入口） |
| `system.activate` | `foxos time-tracking system activate` | Settings > Theme > System | — | 点击「System」（button） | 否（应用没有撤销入口） |
| `currency.set` | `foxos time-tracking currency set` | Settings > main > Currency | `value`（必填）, `submit` | 把「Currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `default-hourly-rate.set` | `foxos time-tracking default-hourly-rate set` | Settings > main > Default hourly rate | `value`（必填）, `submit` | 把「Default hourly rate」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `default-rate-applies-from.set` | `foxos time-tracking default-rate-applies-from set` | Settings > Default rate applies from | `value`（必填）, `submit` | 把「Default rate applies from」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `round-billable-time.set` | `foxos time-tracking round-billable-time set` | Settings > main > Round billable time | `value`（必填）, `submit` | 把「Round billable time」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `week-starts.set` | `foxos time-tracking week-starts set` | Settings > main > Week starts on | `value`（必填）, `submit` | 把「Week starts on」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `weekly-target-hours.set` | `foxos time-tracking weekly-target-hours set` | Settings > main > Weekly target (hours) | `value`（必填）, `submit` | 把「Weekly target (hours)」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `target-counts.set` | `foxos time-tracking target-counts set` | Settings > main > Target counts | `value`（必填）, `submit` | 把「Target counts」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `business-name.set` | `foxos time-tracking business-name set` | Settings > main > Business name | `value`（必填）, `submit` | 把「Business name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `address.set` | `foxos time-tracking address set` | Settings > main > Address | `value`（必填）, `submit` | 把「Address」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `tax-vat-id.set` | `foxos time-tracking tax-vat-id set` | Settings > main > Tax / VAT ID | `value`（必填）, `submit` | 把「Tax / VAT ID」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `default-tax-rate.set` | `foxos time-tracking default-tax-rate set` | Settings > main > Default tax rate (%) | `value`（必填）, `submit` | 把「Default tax rate (%)」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `payment-terms.set` | `foxos time-tracking payment-terms set` | Settings > main > Payment terms | `value`（必填）, `submit` | 把「Payment terms」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `terms-line.set` | `foxos time-tracking terms-line set` | Settings > main > Terms line | `value`（必填）, `submit` | 把「Terms line」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `how-pay.set` | `foxos time-tracking how-pay set` | Settings > main > How to pay | `value`（必填）, `submit` | 把「How to pay」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `logo.import` | `foxos time-tracking logo import` | Settings > main > Upload logo | — | 点击「Upload logo」（button） | 否（应用没有撤销入口） |
| `long-timer-warning.set` | `foxos time-tracking long-timer-warning set` | Settings > main > Long timer warning | `value`（必填）, `submit` | 把「Long timer warning」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `away-sleep-gaps.set` | `foxos time-tracking away-sleep-gaps set` | Settings > main > Away and sleep gaps | `value`（必填）, `submit` | 把「Away and sleep gaps」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `daily-tracking-nudge.set` | `foxos time-tracking daily-tracking-nudge set` | Settings > main > Daily tracking nudge | `value`（必填）, `submit` | 把「Daily tracking nudge」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `unbilled-time-reminder.set` | `foxos time-tracking unbilled-time-reminder set` | Settings > main > Unbilled time reminder | `value`（必填）, `submit` | 把「Unbilled time reminder」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `counts-as-aging.set` | `foxos time-tracking counts-as-aging set` | Settings > main > Counts as aging | `value`（必填）, `submit` | 把「Counts as aging」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `system-notifications.toggle` | `foxos time-tracking system-notifications toggle` | Settings > main > System notifications | — | 切换「System notifications」 | 否（应用没有撤销入口） |
| `automatic-backups.set` | `foxos time-tracking automatic-backups set` | Settings > main > Automatic backups | `value`（必填）, `submit` | 把「Automatic backups」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `puter.show` | `foxos time-tracking puter show` | Settings > main > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
