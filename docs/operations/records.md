# Records（records）操作清单

分组：office · 替代 Airtable, Microsoft Access, Baserow · 许可证 MIT · 页面标题「Records」

共 16 个操作，全部有语义命令（`foxos records <资源> <动词>`，MCP 工具 `records.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account.select` | `foxos records account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `content.dismiss` | `foxos records content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `home.show` | `foxos records home show` | 主界面 > Main > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `trash.delete` | `foxos records trash delete` | 主界面 > Main > Trash | — | 点击「Trash」（link） | 否（应用没有撤销入口） |
| `base.create` | `foxos records base create` | 主界面 > Main > Create base | — | 点击「Create base」（button） | 否（应用没有撤销入口） |
| `source-code-github-opens-tab.show` | `foxos records source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `search-bases.set` | `foxos records search-bases set` | 主界面 > Search bases | `value`（必填）, `submit` | 把「Search bases」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `from-scratcha-blank-base-one-table.start` | `foxos records from-scratcha-blank-base-one-table start` | 主界面 > main > Start from scratchA blank base with one table. | — | 点击「Start from scratchA blank base with one table.」（button） | 否（应用没有撤销入口） |
| `base-2.create` | `foxos records base-2 create` | 主界面 > main > Create base | — | 点击「Create base」（button） | 否（应用没有撤销入口） |
| `notice.dismiss` | `foxos records notice dismiss` | 主界面 > Dismiss notice | — | 点击「Dismiss notice」（button） | 不适用（只读） |
| `it.dismiss` | `foxos records it dismiss` | 主界面 > Preview notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `appearance.activate` | `foxos records appearance activate` | Account: local > Account > Appearance | — | 点击「Appearance」（menuitem） | 否（应用没有撤销入口） |
| `keyboard-shortcuts.activate` | `foxos records keyboard-shortcuts activate` | Account: local > Account > Keyboard shortcuts? | — | 点击「Keyboard shortcuts?」（menuitem） | 否（应用没有撤销入口） |
| `preview.show` | `foxos records preview show` | Account: local > Account > About this preview | — | 点击「About this preview」（menuitem），切换到该视图 | 不适用（只读） |
| `source-code-github.activate` | `foxos records source-code-github activate` | Account: local > Account > Source code on GitHub↗ | — | 点击「Source code on GitHub↗」（menuitem） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos records command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/app.js 中定义） | 不适用 |
