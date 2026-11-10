# Checkers（checkers）操作清单

分组：games · 替代 American checkers against the computer or a friend. · 许可证 MIT (root LICENSE) · 页面标题「Play Checkers Online — vs the Computer or a Friend」

共 21 个操作，全部有语义命令（`foxos checkers <资源> <动词>`，MCP 工具 `checkers.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `white-man.select` | `foxos checkers white-man select` | 主界面 > #, white man | `target`（必填） | 点击名称匹配的「#, white man」项（gridcell） | 不适用（只读） |
| `empty.select` | `foxos checkers empty select` | 主界面 > #, empty | `target`（必填） | 点击名称匹配的「#, empty」项（gridcell） | 不适用（只读） |
| `black-man.select` | `foxos checkers black-man select` | 主界面 > #, black man | `target`（必填） | 点击名称匹配的「#, black man」项（gridcell） | 不适用（只读） |
| `light-theme.activate` | `foxos checkers light-theme activate` | 主界面 > Light theme | — | 点击「Light theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `dark-theme.activate` | `foxos checkers dark-theme activate` | 主界面 > Dark theme | — | 点击「Dark theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `follow-system-theme.activate` | `foxos checkers follow-system-theme activate` | 主界面 > Follow system theme | — | 点击「Follow system theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `computer.activate` | `foxos checkers computer activate` | 主界面 > Game mode > Computer | — | 点击「Computer」（button） | 可能（应用提供撤销，未逐项验证） |
| `pass-play.activate` | `foxos checkers pass-play activate` | 主界面 > Game mode > Pass & Play | — | 点击「Pass & Play」（button） | 可能（应用提供撤销，未逐项验证） |
| `online.activate` | `foxos checkers online activate` | 主界面 > Game mode > Online | — | 点击「Online」（button） | 可能（应用提供撤销，未逐项验证） |
| `moves.activate` | `foxos checkers moves activate` | 主界面 > aside > Moves | — | 点击「Moves」（button） | 可能（应用提供撤销，未逐项验证） |
| `game-as-pdn.copy` | `foxos checkers game-as-pdn copy` | 主界面 > Copy the game as PDN | — | 点击「Copy the game as PDN」（button） | 可能（应用提供撤销，未逐项验证） |
| `game-as-pdn-file.export` | `foxos checkers game-as-pdn-file export` | 主界面 > Download the game as a PDN file | — | 点击「Download the game as a PDN file」（button） | 可能（应用提供撤销，未逐项验证） |
| `difficulty.set` | `foxos checkers difficulty set` | 主界面 > aside > Difficulty | `value`（必填）, `submit` | 把「Difficulty」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `clock.set` | `foxos checkers clock set` | 主界面 > aside > Clock | `value`（必填）, `submit` | 把「Clock」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `play-as.set` | `foxos checkers play-as set` | 主界面 > aside > Play as | `value`（必填）, `submit` | 把「Play as」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `game.create` | `foxos checkers game create` | 主界面 > aside > New game | — | 点击「New game」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos checkers undo undo` | 主界面 > aside > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-starting-position.activate` | `foxos checkers go-starting-position activate` | Moves > Go to the starting position | — | 点击「Go to the starting position」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-back-one-move.activate` | `foxos checkers go-back-one-move activate` | Moves > Go back one move | — | 点击「Go back one move」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-forward-one-move.activate` | `foxos checkers go-forward-one-move activate` | Moves > Go forward one move | — | 点击「Go forward one move」（button） | 可能（应用提供撤销，未逐项验证） |
| `return-current-position.activate` | `foxos checkers return-current-position activate` | Moves > Return to the current position | — | 点击「Return to the current position」（button） | 可能（应用提供撤销，未逐项验证） |
