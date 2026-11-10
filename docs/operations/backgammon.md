# Backgammon（backgammon）操作清单

分组：games · 替代 Play against the computer or a friend, locally or online. · 许可证 MIT (root LICENSE) · 页面标题「Play Backgammon Online — vs the Computer or a Friend」

共 27 个操作，全部有语义命令（`foxos backgammon <资源> <动词>`，MCP 工具 `backgammon.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `point-white-checkers.select` | `foxos backgammon point-white-checkers select` | 主界面 > point # white checkers | `target`（必填） | 点击名称匹配的「point # white checkers」项（gridcell） | 不适用（只读） |
| `point-empty.select` | `foxos backgammon point-empty select` | 主界面 > point #, empty | `target`（必填） | 点击名称匹配的「point #, empty」项（gridcell） | 不适用（只读） |
| `point-black-checkers.select` | `foxos backgammon point-black-checkers select` | 主界面 > point # black checkers | `target`（必填） | 点击名称匹配的「point # black checkers」项（gridcell） | 不适用（只读） |
| `light-theme.activate` | `foxos backgammon light-theme activate` | 主界面 > Light theme | — | 点击「Light theme」（button） | 否（应用没有撤销入口） |
| `dark-theme.activate` | `foxos backgammon dark-theme activate` | 主界面 > Dark theme | — | 点击「Dark theme」（button） | 否（应用没有撤销入口） |
| `follow-system-theme.activate` | `foxos backgammon follow-system-theme activate` | 主界面 > Follow system theme | — | 点击「Follow system theme」（button） | 否（应用没有撤销入口） |
| `black-bar-empty.activate` | `foxos backgammon black-bar-empty activate` | 主界面 > Black bar, empty | — | 点击「Black bar, empty」（gridcell） | 否（应用没有撤销入口） |
| `black-tray-empty.activate` | `foxos backgammon black-tray-empty activate` | 主界面 > Black tray, empty | — | 点击「Black tray, empty」（gridcell） | 否（应用没有撤销入口） |
| `white-bar-empty.activate` | `foxos backgammon white-bar-empty activate` | 主界面 > White bar, empty | — | 点击「White bar, empty」（gridcell） | 否（应用没有撤销入口） |
| `white-tray-empty.activate` | `foxos backgammon white-tray-empty activate` | 主界面 > White tray, empty | — | 点击「White tray, empty」（gridcell） | 否（应用没有撤销入口） |
| `computer.activate` | `foxos backgammon computer activate` | 主界面 > Game mode > Computer | — | 点击「Computer」（button） | 否（应用没有撤销入口） |
| `pass-play.activate` | `foxos backgammon pass-play activate` | 主界面 > Game mode > Pass & Play | — | 点击「Pass & Play」（button） | 否（应用没有撤销入口） |
| `online.activate` | `foxos backgammon online activate` | 主界面 > Game mode > Online | — | 点击「Online」（button） | 否（应用没有撤销入口） |
| `moves.activate` | `foxos backgammon moves activate` | 主界面 > aside > Moves | — | 点击「Moves」（button） | 否（应用没有撤销入口） |
| `game-as-mat-transcript.copy` | `foxos backgammon game-as-mat-transcript copy` | 主界面 > Copy the game as a .mat transcript | — | 点击「Copy the game as a .mat transcript」（button） | 否（应用没有撤销入口） |
| `game-as-mat-file.export` | `foxos backgammon game-as-mat-file export` | 主界面 > Download the game as a .mat file | — | 点击「Download the game as a .mat file」（button） | 否（应用没有撤销入口） |
| `roll-start.activate` | `foxos backgammon roll-start activate` | 主界面 > aside > Roll to start | — | 点击「Roll to start」（button） | 否（应用没有撤销入口） |
| `difficulty.set` | `foxos backgammon difficulty set` | 主界面 > aside > Difficulty | `value`（必填）, `submit` | 把「Difficulty」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `clock.set` | `foxos backgammon clock set` | 主界面 > aside > Clock | `value`（必填）, `submit` | 把「Clock」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `doubling-cube.set` | `foxos backgammon doubling-cube set` | 主界面 > aside > Doubling cube | `value`（必填）, `submit` | 把「Doubling cube」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `play-as.set` | `foxos backgammon play-as set` | 主界面 > aside > Play as | `value`（必填）, `submit` | 把「Play as」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `game.create` | `foxos backgammon game create` | 主界面 > aside > New game | — | 点击「New game」（button） | 否（应用没有撤销入口） |
| `turn.undo` | `foxos backgammon turn undo` | 主界面 > aside > Undo turn | — | 点击「Undo turn」（button） | 否（应用没有撤销入口） |
| `go-starting-position.activate` | `foxos backgammon go-starting-position activate` | Moves > Go to the starting position | — | 点击「Go to the starting position」（button） | 否（应用没有撤销入口） |
| `go-back-one-turn.activate` | `foxos backgammon go-back-one-turn activate` | Moves > Go back one turn | — | 点击「Go back one turn」（button） | 否（应用没有撤销入口） |
| `go-forward-one-turn.activate` | `foxos backgammon go-forward-one-turn activate` | Moves > Go forward one turn | — | 点击「Go forward one turn」（button） | 否（应用没有撤销入口） |
| `return-current-position.activate` | `foxos backgammon return-current-position activate` | Moves > Return to the current position | — | 点击「Return to the current position」（button） | 否（应用没有撤销入口） |
