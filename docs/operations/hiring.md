# Hiring（hiring）操作清单

分组：business · 替代 Greenhouse, Lever, Workable · 许可证 MIT (root LICENSE) · 页面标题「Overview · Hiring」

共 22 个操作，全部有语义命令（`foxos hiring <资源> <动词>`，MCP 工具 `hiring.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `yet.open` | `foxos hiring yet open` | 主界面 > main > open # yet | `target`（必填） | 点击名称匹配的「open # yet」项（button） | 不适用（只读） |
| `candidates-not-yet-hired.select` | `foxos hiring candidates-not-yet-hired select` | 主界面 > main > candidates in #, not yet hired | `target`（必填） | 点击名称匹配的「candidates in #, not yet hired」项（button） | 不适用（只读） |
| `interviews-today.select` | `foxos hiring interviews-today select` | 主界面 > main > interviews · # today | `target`（必填） | 点击名称匹配的「interviews · # today」项（button） | 不适用（只读） |
| `offers-signature.select` | `foxos hiring offers-signature select` | 主界面 > main > offers # signature | `target`（必填） | 点击名称匹配的「offers # signature」项（button） | 不适用（只读） |
| `main.select` | `foxos hiring main select` | 主界面 > main > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `skip.dismiss` | `foxos hiring skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `searchctrl-k.activate` | `foxos hiring searchctrl-k activate` | 主界面 > aside > SearchCtrl K | — | 点击「SearchCtrl K」（button） | 否（应用没有撤销入口） |
| `overview.activate` | `foxos hiring overview activate` | 主界面 > Main > Overview | — | 点击「Overview」（button） | 否（应用没有撤销入口） |
| `jobs.activate` | `foxos hiring jobs activate` | 主界面 > Main > Jobs | — | 点击「Jobs」（button） | 否（应用没有撤销入口） |
| `pipeline.activate` | `foxos hiring pipeline activate` | 主界面 > Main > Pipeline | — | 点击「Pipeline」（button） | 否（应用没有撤销入口） |
| `interviews.activate` | `foxos hiring interviews activate` | 主界面 > Main > Interviews | — | 点击「Interviews」（button） | 否（应用没有撤销入口） |
| `offers.activate` | `foxos hiring offers activate` | 主界面 > Main > Offers | — | 点击「Offers」（button） | 否（应用没有撤销入口） |
| `onboarding.activate` | `foxos hiring onboarding activate` | 主界面 > Main > Onboarding | — | 点击「Onboarding」（button） | 否（应用没有撤销入口） |
| `reports.activate` | `foxos hiring reports activate` | 主界面 > Main > Reports | — | 点击「Reports」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos hiring settings show` | 主界面 > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `theme.activate` | `foxos hiring theme activate` | 主界面 > Theme | — | 点击「Theme」（button） | 否（应用没有撤销入口） |
| `puter.show` | `foxos hiring puter show` | 主界面 > aside > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `reports-2.activate` | `foxos hiring reports-2 activate` | 主界面 > main > Reports | — | 点击「Reports」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos hiring close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-hiring.activate` | `foxos hiring set-up-hiring activate` | 主界面 > Welcome > Set up my hiring | — | 点击「Set up my hiring」（button） | 否（应用没有撤销入口） |
| `explore-sample-data.activate` | `foxos hiring explore-sample-data activate` | 主界面 > Welcome > Explore with sample data | — | 点击「Explore with sample data」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos hiring command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/app.js 中定义） | 不适用 |
