# Cap Table（cap-table）操作清单

分组：finance · 替代 Carta, Pulley · 许可证 MIT (root LICENSE) · 页面标题「Cap Table」

共 27 个操作，全部有语义命令（`foxos cap-table <资源> <动词>`，MCP 工具 `cap-table.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `skip.dismiss` | `foxos cap-table skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `main-content.dismiss` | `foxos cap-table main-content dismiss` | 主界面 > Skip to main content | — | 点击「Skip to main content」（button） | 不适用（只读） |
| `searchctrl-k.activate` | `foxos cap-table searchctrl-k activate` | 主界面 > Main navigation > SearchCtrl K | — | 点击「SearchCtrl K」（button） | 否（应用没有撤销入口） |
| `home.activate` | `foxos cap-table home activate` | 主界面 > Main navigation > Home | — | 点击「Home」（button） | 否（应用没有撤销入口） |
| `cap-table.activate` | `foxos cap-table cap-table activate` | 主界面 > Main navigation > Cap table | — | 点击「Cap table」（button） | 否（应用没有撤销入口） |
| `securities.activate` | `foxos cap-table securities activate` | 主界面 > Main navigation > Securities | — | 点击「Securities」（button） | 否（应用没有撤销入口） |
| `stakeholders.activate` | `foxos cap-table stakeholders activate` | 主界面 > Main navigation > Stakeholders | — | 点击「Stakeholders」（button） | 否（应用没有撤销入口） |
| `classes.share` | `foxos cap-table classes share` | 主界面 > Main navigation > Share classes | — | 点击「Share classes」（button） | 否（应用没有撤销入口） |
| `round-modeling.activate` | `foxos cap-table round-modeling activate` | 主界面 > Main navigation > Round modeling | — | 点击「Round modeling」（button） | 否（应用没有撤销入口） |
| `exit-scenarios.activate` | `foxos cap-table exit-scenarios activate` | 主界面 > Main navigation > Exit scenarios | — | 点击「Exit scenarios」（button） | 否（应用没有撤销入口） |
| `needs-attention.activate` | `foxos cap-table needs-attention activate` | 主界面 > Main navigation > Needs attention | — | 点击「Needs attention」（button） | 否（应用没有撤销入口） |
| `reports.activate` | `foxos cap-table reports activate` | 主界面 > Main navigation > Reports | — | 点击「Reports」（button） | 否（应用没有撤销入口） |
| `history.activate` | `foxos cap-table history activate` | 主界面 > Main navigation > History | — | 点击「History」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos cap-table settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `issue-security.activate` | `foxos cap-table issue-security activate` | 主界面 > Main navigation > Issue security | — | 点击「Issue security」（button） | 否（应用没有撤销入口） |
| `issue-security-2.activate` | `foxos cap-table issue-security-2 activate` | 主界面 > main > Issue security | — | 点击「Issue security」（button） | 否（应用没有撤销入口） |
| `by-class.activate` | `foxos cap-table by-class activate` | 主界面 > Ownership grouping > By class | — | 点击「By class」（button） | 否（应用没有撤销入口） |
| `by-holder.activate` | `foxos cap-table by-holder activate` | 主界面 > Ownership grouping > By holder | — | 点击「By holder」（button） | 否（应用没有撤销入口） |
| `cap-table.open` | `foxos cap-table cap-table open` | 主界面 > main > Open cap table | — | 点击「Open cap table」（button） | 不适用（只读） |
| `set-up-company-profile-do.activate` | `foxos cap-table set-up-company-profile-do activate` | 主界面 > main > Set up your company profile, to do | — | 点击「Set up your company profile, to do」（button） | 否（应用没有撤销入口） |
| `share-class-do.create` | `foxos cap-table share-class-do create` | 主界面 > main > Create a share class, to do | — | 点击「Create a share class, to do」（button） | 否（应用没有撤销入口） |
| `issue-founder-shares-do.activate` | `foxos cap-table issue-founder-shares-do activate` | 主界面 > main > Issue founder shares, to do | — | 点击「Issue founder shares, to do」（button） | 否（应用没有撤销入口） |
| `adopt-equity-plan-reserve-shares-do.activate` | `foxos cap-table adopt-equity-plan-reserve-shares-do activate` | 主界面 > main > Adopt an equity plan and reserve shares, to do | — | 点击「Adopt an equity plan and reserve shares, to do」（button） | 否（应用没有撤销入口） |
| `grant-options-or-add-safe-do.activate` | `foxos cap-table grant-options-or-add-safe-do activate` | 主界面 > main > Grant options or add a SAFE, to do | — | 点击「Grant options or add a SAFE, to do」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos cap-table close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-company.activate` | `foxos cap-table set-up-company activate` | 主界面 > Welcome > Set up my company | — | 点击「Set up my company」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos cap-table explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
