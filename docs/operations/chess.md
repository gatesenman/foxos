# Chess（chess）操作清单

分组：games · 替代 Play against the computer or a friend, with clocks and online play. · 许可证 MIT (root LICENSE) · 页面标题「Play Chess Online — vs the Computer or a Friend」

共 30 个操作，全部有语义命令（`foxos chess <资源> <动词>`，MCP 工具 `chess.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `black-rook.select` | `foxos chess black-rook select` | 主界面 > #, black rook | `target`（必填） | 点击名称匹配的「#, black rook」项（gridcell） | 不适用（只读） |
| `black-knight.select` | `foxos chess black-knight select` | 主界面 > #, black knight | `target`（必填） | 点击名称匹配的「#, black knight」项（gridcell） | 不适用（只读） |
| `black-bishop.select` | `foxos chess black-bishop select` | 主界面 > #, black bishop | `target`（必填） | 点击名称匹配的「#, black bishop」项（gridcell） | 不适用（只读） |
| `black-queen.select` | `foxos chess black-queen select` | 主界面 > #, black queen | `target`（必填） | 点击名称匹配的「#, black queen」项（gridcell） | 不适用（只读） |
| `black-king.select` | `foxos chess black-king select` | 主界面 > #, black king | `target`（必填） | 点击名称匹配的「#, black king」项（gridcell） | 不适用（只读） |
| `black-pawn.select` | `foxos chess black-pawn select` | 主界面 > #, black pawn | `target`（必填） | 点击名称匹配的「#, black pawn」项（gridcell） | 不适用（只读） |
| `empty.select` | `foxos chess empty select` | 主界面 > #, empty | `target`（必填） | 点击名称匹配的「#, empty」项（gridcell） | 不适用（只读） |
| `white-pawn.select` | `foxos chess white-pawn select` | 主界面 > #, white pawn | `target`（必填） | 点击名称匹配的「#, white pawn」项（gridcell） | 不适用（只读） |
| `white-rook.select` | `foxos chess white-rook select` | 主界面 > #, white rook | `target`（必填） | 点击名称匹配的「#, white rook」项（gridcell） | 不适用（只读） |
| `white-knight.select` | `foxos chess white-knight select` | 主界面 > #, white knight | `target`（必填） | 点击名称匹配的「#, white knight」项（gridcell） | 不适用（只读） |
| `white-bishop.select` | `foxos chess white-bishop select` | 主界面 > #, white bishop | `target`（必填） | 点击名称匹配的「#, white bishop」项（gridcell） | 不适用（只读） |
| `white-queen.select` | `foxos chess white-queen select` | 主界面 > #, white queen | `target`（必填） | 点击名称匹配的「#, white queen」项（gridcell） | 不适用（只读） |
| `white-king.select` | `foxos chess white-king select` | 主界面 > #, white king | `target`（必填） | 点击名称匹配的「#, white king」项（gridcell） | 不适用（只读） |
| `light-theme.activate` | `foxos chess light-theme activate` | 主界面 > Light theme | — | 点击「Light theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `dark-theme.activate` | `foxos chess dark-theme activate` | 主界面 > Dark theme | — | 点击「Dark theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `follow-system-theme.activate` | `foxos chess follow-system-theme activate` | 主界面 > Follow system theme | — | 点击「Follow system theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `computer.activate` | `foxos chess computer activate` | 主界面 > Game mode > Computer | — | 点击「Computer」（button） | 可能（应用提供撤销，未逐项验证） |
| `pass-play.activate` | `foxos chess pass-play activate` | 主界面 > Game mode > Pass & Play | — | 点击「Pass & Play」（button） | 可能（应用提供撤销，未逐项验证） |
| `online.activate` | `foxos chess online activate` | 主界面 > Game mode > Online | — | 点击「Online」（button） | 可能（应用提供撤销，未逐项验证） |
| `game-as-pgn.copy` | `foxos chess game-as-pgn copy` | 主界面 > Copy the game as PGN | — | 点击「Copy the game as PGN」（button） | 可能（应用提供撤销，未逐项验证） |
| `game-as-pgn-file.export` | `foxos chess game-as-pgn-file export` | 主界面 > Download the game as a PGN file | — | 点击「Download the game as a PGN file」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-starting-position.activate` | `foxos chess go-starting-position activate` | 主界面 > Go to the starting position | — | 点击「Go to the starting position」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-back-one-move.activate` | `foxos chess go-back-one-move activate` | 主界面 > Go back one move | — | 点击「Go back one move」（button） | 可能（应用提供撤销，未逐项验证） |
| `go-forward-one-move.activate` | `foxos chess go-forward-one-move activate` | 主界面 > Go forward one move | — | 点击「Go forward one move」（button） | 可能（应用提供撤销，未逐项验证） |
| `return-current-position.activate` | `foxos chess return-current-position activate` | 主界面 > Return to the current position | — | 点击「Return to the current position」（button） | 可能（应用提供撤销，未逐项验证） |
| `difficulty.set` | `foxos chess difficulty set` | 主界面 > aside > Difficulty | `value`（必填）, `submit` | 把「Difficulty」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `clock.set` | `foxos chess clock set` | 主界面 > aside > Clock | `value`（必填）, `submit` | 把「Clock」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `play-as.set` | `foxos chess play-as set` | 主界面 > aside > Play as | `value`（必填）, `submit` | 把「Play as」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `game.create` | `foxos chess game create` | 主界面 > aside > New game | — | 点击「New game」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos chess undo undo` | 主界面 > aside > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
