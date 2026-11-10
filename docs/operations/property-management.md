# Property Management（property-management）操作清单

分组：business · 替代 Buildium, AppFolio, Rent Manager · 许可证 MIT (root LICENSE) · 页面标题「Dashboard · Property Management」

共 45 个操作，全部有语义命令（`foxos property-management <资源> <动词>`，MCP 工具 `property-management.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `collected-charges-posted-yet.select` | `foxos property-management collected-charges-posted-yet select` | 主界面 > Key figures > collected in # charges posted yet | `target`（必填） | 点击名称匹配的「collected in # charges posted yet」项（link） | 不适用（只读） |
| `outstanding-balances-is-paid-up.select` | `foxos property-management outstanding-balances-is-paid-up select` | 主界面 > Key figures > outstanding balances$# is paid up | `target`（必填） | 点击名称匹配的「outstanding balances$# is paid up」项（link） | 不适用（只读） |
| `units-occupied.select` | `foxos property-management units-occupied select` | 主界面 > Key figures > # of # units occupied | `target`（必填） | 点击名称匹配的「# of # units occupied」项（link） | 不适用（只读） |
| `work-urgent.open` | `foxos property-management work-urgent open` | 主界面 > Key figures > open work # urgent | `target`（必填） | 点击名称匹配的「open work # urgent」项（link） | 不适用（只读） |
| `view.show` | `foxos property-management view show` | 主界面 > view all: * | `target`（必填） | 点击名称匹配的「view all: *」项（link） | 不适用（只读） |
| `financials.select` | `foxos property-management financials select` | 主界面 > financials: * | `target`（必填） | 点击名称匹配的「financials: *」项（link） | 不适用（只读） |
| `renewals.select` | `foxos property-management renewals select` | 主界面 > renewals: * | `target`（必填） | 点击名称匹配的「renewals: *」项（link） | 不适用（只读） |
| `calendar.select` | `foxos property-management calendar select` | 主界面 > calendar: * | `target`（必填） | 点击名称匹配的「calendar: *」项（link） | 不适用（只读） |
| `listings.select` | `foxos property-management listings select` | 主界面 > listings: * | `target`（必填） | 点击名称匹配的「listings: *」项（link） | 不适用（只读） |
| `content.dismiss` | `foxos property-management content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `dashboard.show` | `foxos property-management dashboard show` | 主界面 > Dashboard | — | 点击「Dashboard」（link），切换到该视图 | 不适用（只读） |
| `n.create` | `foxos property-management n create` | 主界面 > aside > Create (N) | — | 点击「Create (N)」（button） | 否（应用没有撤销入口） |
| `dashboard-2.show` | `foxos property-management dashboard-2 show` | 主界面 > Main > Dashboard | — | 点击「Dashboard」（link），切换到该视图 | 不适用（只读） |
| `rentals.activate` | `foxos property-management rentals activate` | 主界面 > Main > Rentals | — | 点击「Rentals」（button） | 否（应用没有撤销入口） |
| `properties.show` | `foxos property-management properties show` | 主界面 > Rentals > Properties | — | 点击「Properties」（link），切换到该视图 | 不适用（只读） |
| `rent-roll.show` | `foxos property-management rent-roll show` | 主界面 > Rentals > Rent roll | — | 点击「Rent roll」（link），切换到该视图 | 不适用（只读） |
| `tenants.show` | `foxos property-management tenants show` | 主界面 > Rentals > Tenants | — | 点击「Tenants」（link），切换到该视图 | 不适用（只读） |
| `rental-owners.show` | `foxos property-management rental-owners show` | 主界面 > Rentals > Rental owners | — | 点击「Rental owners」（link），切换到该视图 | 不适用（只读） |
| `outstanding-balances.show` | `foxos property-management outstanding-balances show` | 主界面 > Outstanding balances | — | 点击「Outstanding balances」（link），切换到该视图 | 不适用（只读） |
| `leasing.activate` | `foxos property-management leasing activate` | 主界面 > Main > Leasing | — | 点击「Leasing」（button） | 否（应用没有撤销入口） |
| `accounting.activate` | `foxos property-management accounting activate` | 主界面 > Main > Accounting | — | 点击「Accounting」（button） | 否（应用没有撤销入口） |
| `maintenance.activate` | `foxos property-management maintenance activate` | 主界面 > Main > Maintenance | — | 点击「Maintenance」（button） | 否（应用没有撤销入口） |
| `tasks.show` | `foxos property-management tasks show` | 主界面 > Tasks | — | 点击「Tasks」（link），切换到该视图 | 不适用（只读） |
| `communication.show` | `foxos property-management communication show` | 主界面 > Main > Communication | — | 点击「Communication」（link），切换到该视图 | 不适用（只读） |
| `calendar.show` | `foxos property-management calendar show` | 主界面 > Main > Calendar | — | 点击「Calendar」（link），切换到该视图 | 不适用（只读） |
| `reports.show` | `foxos property-management reports show` | 主界面 > Main > Reports | — | 点击「Reports」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos property-management settings show` | 主界面 > aside > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos property-management source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos property-management puter show` | 主界面 > aside > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `navigation.collapse` | `foxos property-management navigation collapse` | 主界面 > Collapse navigation | — | 点击「Collapse navigation」（button） | 不适用（只读） |
| `search.search` | `foxos property-management search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos property-management keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `account-appearance.activate` | `foxos property-management account-appearance activate` | 主界面 > Account and appearance | — | 点击「Account and appearance」（button） | 否（应用没有撤销入口） |
| `receive-payment.activate` | `foxos property-management receive-payment activate` | 主界面 > header > Receive payment | — | 点击「Receive payment」（button） | 否（应用没有撤销入口） |
| `work-orderwork-order.create` | `foxos property-management work-orderwork-order create` | 主界面 > header > New work orderWork order | — | 点击「New work orderWork order」（link） | 否（应用没有撤销入口） |
| `lease.create` | `foxos property-management lease create` | 主界面 > header > New lease | — | 点击「New lease」（link） | 否（应用没有撤销入口） |
| `close.close` | `foxos property-management close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `company-name.set` | `foxos property-management company-name set` | 主界面 > dialog > Company name | `value`（必填）, `submit` | 把「Company name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `name.set` | `foxos property-management name set` | 主界面 > dialog > Your name | `value`（必填）, `submit` | 把「Your name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `what-you-manage.set` | `foxos property-management what-you-manage set` | 主界面 > dialog > What you manage | `value`（必填）, `submit` | 把「What you manage」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `currency.set` | `foxos property-management currency set` | 主界面 > dialog > Currency | `value`（必填）, `submit` | 把「Currency」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sample-portfolio.import` | `foxos property-management sample-portfolio import` | 主界面 > dialog > Load sample portfolio | — | 点击「Load sample portfolio」（button） | 否（应用没有撤销入口） |
| `get-started.activate` | `foxos property-management get-started activate` | 主界面 > dialog > Get started | — | 点击「Get started」（button） | 否（应用没有撤销入口） |
| `it.dismiss` | `foxos property-management it dismiss` | 主界面 > Early alpha notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `command-palette.show` | `foxos property-management command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/shell.js 中定义） | 不适用 |
