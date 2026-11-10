# Whiteboard（whiteboard）操作清单

分组：office · 替代 Miro, Microsoft Whiteboard, FigJam · 许可证 AGPL-3.0-only · 页面标题「Your boards · Whiteboard」

共 26 个操作，全部有语义命令（`foxos whiteboard <资源> <动词>`，MCP 工具 `whiteboard.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `board-library.select` | `foxos whiteboard board-library select` | 主界面 > Board library > all # | `target`（必填） | 点击名称匹配的「all #」项（button） | 不适用（只读） |
| `board-library-2.select` | `foxos whiteboard board-library-2 select` | 主界面 > Board library > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `main.select` | `foxos whiteboard main select` | 主界面 > main > crazy # eight ideas in eight minutes, then share and vote. | `target`（必填） | 点击名称匹配的「crazy # eight ideas in eight minutes, then share and vote.」项（button） | 不适用（只读） |
| `whiteboard-home.show` | `foxos whiteboard whiteboard-home show` | 主界面 > Whiteboard home | — | 点击「Whiteboard home」（link），切换到该视图 | 不适用（只读） |
| `trash.delete` | `foxos whiteboard trash delete` | 主界面 > Board library > Trash | — | 点击「Trash」（button） | 否（应用没有撤销入口） |
| `organization.join` | `foxos whiteboard organization join` | 主界面 > Organization > Join an organization | — | 点击「Join an organization」（button） | 否（应用没有撤销入口） |
| `set-up-organization.activate` | `foxos whiteboard set-up-organization activate` | 主界面 > Organization > Set up an organization | — | 点击「Set up an organization」（button） | 否（应用没有撤销入口） |
| `feedback.send` | `foxos whiteboard feedback send` | 主界面 > aside > Send feedback | — | 点击「Send feedback」（button） | 否（应用没有撤销入口） |
| `language.set` | `foxos whiteboard language set` | 主界面 > Language | `value`（必填）, `submit` | 把「Language」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `appearance.set` | `foxos whiteboard appearance set` | 主界面 > Appearance | `value`（必填）, `submit` | 把「Appearance」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `powered-by-puter.show` | `foxos whiteboard powered-by-puter show` | 主界面 > aside > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `command-palette-ctrl-cmd-k.activate` | `foxos whiteboard command-palette-ctrl-cmd-k activate` | 主界面 > Command palette (Ctrl/Cmd K) | — | 点击「Command palette (Ctrl/Cmd K)」（button） | 否（应用没有撤销入口） |
| `shared-board.join` | `foxos whiteboard shared-board join` | 主界面 > Join shared board | — | 点击「Join shared board」（button） | 否（应用没有撤销入口） |
| `training.show` | `foxos whiteboard training show` | 主界面 > Help and training | — | 点击「Help and training」（button），切换到该视图 | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos whiteboard keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `account-menu-local.activate` | `foxos whiteboard account-menu-local activate` | 主界面 > Account menu · local | — | 点击「Account menu · local」（button） | 否（应用没有撤销入口） |
| `browse-templates.activate` | `foxos whiteboard browse-templates activate` | 主界面 > main > Browse all templates | — | 点击「Browse all templates」（button） | 否（应用没有撤销入口） |
| `blank-boarda-fresh-start.activate` | `foxos whiteboard blank-boarda-fresh-start activate` | 主界面 > main > Blank boardA fresh start | — | 点击「Blank boardA fresh start」（button） | 否（应用没有撤销入口） |
| `board.create` | `foxos whiteboard board create` | 主界面 > main > New board | — | 点击「New board」（button） | 否（应用没有撤销入口） |
| `search-boards.set` | `foxos whiteboard search-boards set` | 主界面 > Search boards | `value`（必填）, `submit` | 把「Search boards」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sort-boards.set` | `foxos whiteboard sort-boards set` | 主界面 > Sort boards | `value`（必填）, `submit` | 把「Sort boards」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `board-file.import` | `foxos whiteboard board-file import` | 主界面 > Import board file | — | 点击「Import board file」（button） | 否（应用没有撤销入口） |
| `migrate-from-miro.activate` | `foxos whiteboard migrate-from-miro activate` | 主界面 > Migrate from Miro | — | 点击「Migrate from Miro」（button） | 否（应用没有撤销入口） |
| `grid-view.activate` | `foxos whiteboard grid-view activate` | 主界面 > Grid view | — | 点击「Grid view」（button） | 否（应用没有撤销入口） |
| `list-view.activate` | `foxos whiteboard list-view activate` | 主界面 > List view | — | 点击「List view」（button） | 否（应用没有撤销入口） |
| `keyboard-shortcuts-2.activate` | `foxos whiteboard keyboard-shortcuts-2 activate` | 主界面 > footer > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
