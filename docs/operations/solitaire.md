# Solitaire（solitaire）操作清单

分组：games · 替代 Klondike (draw one or three, optional Vegas scoring) and Spider solitaire, with optional cloud saves. · 许可证 MIT (root LICENSE) · 页面标题「Play Klondike Solitaire Online — Draw-One, Undo Any Move」

共 9 个操作，全部有语义命令（`foxos solitaire <资源> <动词>`，MCP 工具 `solitaire.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `klondike-draw.select` | `foxos solitaire klondike-draw select` | Choose a game > klondike, draw # | `target`（必填） | 点击名称匹配的「klondike, draw #」项（menuitemradio） | 不适用（只读） |
| `vegas-draw.select` | `foxos solitaire vegas-draw select` | Choose a game > vegas, draw # | `target`（必填） | 点击名称匹配的「vegas, draw #」项（menuitemradio） | 不适用（只读） |
| `spider-suit.select` | `foxos solitaire spider-suit select` | Choose a game > spider, # suit | `target`（必填） | 点击名称匹配的「spider, # suit」项（menuitemradio） | 不适用（只读） |
| `spider-suits.select` | `foxos solitaire spider-suits select` | Choose a game > spider, # suits | `target`（必填） | 点击名称匹配的「spider, # suits」项（menuitemradio） | 不适用（只读） |
| `game.select` | `foxos solitaire game select` | 主界面 > header > Choose a game | — | 点击「Choose a game」（button） | 不适用（只读） |
| `undo.undo` | `foxos solitaire undo undo` | 主界面 > header > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `powered-by-puter.show` | `foxos solitaire powered-by-puter show` | 主界面 > footer > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `document.create` | `foxos solitaire document create` | 键盘 mod+n | — | 在当前焦点上按 mod+n（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `edit.undo` | `foxos solitaire edit undo` | 键盘 mod+z | — | 在当前焦点上按 mod+z（src/main.js 中定义） | 不适用 |
