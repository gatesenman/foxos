# Sudoku（sudoku）操作清单

分组：games · 替代 Four difficulty levels, daily puzzles, and hints that explain the logic. · 许可证 MIT (root LICENSE) · 页面标题「Sudoku: Play Free in Your Browser」

共 39 个操作，全部有语义命令（`foxos sudoku <资源> <动词>`，MCP 工具 `sudoku.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `row-column-clue.select` | `foxos sudoku row-column-clue select` | 主界面 > row #, column #, clue | `target`（必填） | 点击名称匹配的「row #, column #, clue」项（gridcell） | 不适用（只读） |
| `row-column-empty.select` | `foxos sudoku row-column-empty select` | 主界面 > row #, column #, empty | `target`（必填） | 点击名称匹配的「row #, column #, empty」项（gridcell） | 不适用（只读） |
| `pencil-n.select` | `foxos sudoku pencil-n select` | 主界面 > Tools > pencil # (n) | `target`（必填） | 点击名称匹配的「pencil # (n)」项（button） | 不适用（只读） |
| `remaining.select` | `foxos sudoku remaining select` | 主界面 > # remaining | `target`（必填） | 点击名称匹配的「# remaining」项（button） | 不适用（只读） |
| `settings-row-column-empty.select` | `foxos sudoku settings-row-column-empty select` | Settings > row #, column #, empty | `target`（必填） | 点击名称匹配的「row #, column #, empty」项（gridcell） | 不适用（只读） |
| `settings-row-column-clue.select` | `foxos sudoku settings-row-column-clue select` | Settings > row #, column #, clue | `target`（必填） | 点击名称匹配的「row #, column #, clue」项（gridcell） | 不适用（只读） |
| `settings-remaining.select` | `foxos sudoku settings-remaining select` | Settings > # remaining | `target`（必填） | 点击名称匹配的「# remaining」项（button） | 不适用（只读） |
| `tidy-pencil.select` | `foxos sudoku tidy-pencil select` | Settings > tidy pencil # | `target`（必填） | 点击名称匹配的「tidy pencil #」项（checkbox） | 不适用（只读） |
| `puzzle-row-column-clue.select` | `foxos sudoku puzzle-row-column-clue select` | New puzzle > row #, column #, clue | `target`（必填） | 点击名称匹配的「row #, column #, clue」项（gridcell） | 不适用（只读） |
| `puzzle-row-column-empty.select` | `foxos sudoku puzzle-row-column-empty select` | New puzzle > row #, column #, empty | `target`（必填） | 点击名称匹配的「row #, column #, empty」项（gridcell） | 不适用（只读） |
| `puzzle-remaining.select` | `foxos sudoku puzzle-remaining select` | New puzzle > # remaining | `target`（必填） | 点击名称匹配的「# remaining」项（button） | 不适用（只读） |
| `daily-row-column-clue.select` | `foxos sudoku daily-row-column-clue select` | Daily > row #, column #, clue | `target`（必填） | 点击名称匹配的「row #, column #, clue」项（gridcell） | 不适用（只读） |
| `daily-row-column-empty.select` | `foxos sudoku daily-row-column-empty select` | Daily > row #, column #, empty | `target`（必填） | 点击名称匹配的「row #, column #, empty」项（gridcell） | 不适用（只读） |
| `daily-remaining.select` | `foxos sudoku daily-remaining select` | Daily > # remaining | `target`（必填） | 点击名称匹配的「# remaining」项（button） | 不适用（只读） |
| `powered-by-puter-row-column-clue.select` | `foxos sudoku powered-by-puter-row-column-clue select` | Powered by Puter > row #, column #, clue | `target`（必填） | 点击名称匹配的「row #, column #, clue」项（gridcell） | 不适用（只读） |
| `powered-by-puter-remaining.select` | `foxos sudoku powered-by-puter-remaining select` | Powered by Puter > # remaining | `target`（必填） | 点击名称匹配的「# remaining」项（button） | 不适用（只读） |
| `light-theme.activate` | `foxos sudoku light-theme activate` | 主界面 > Colour theme > Light theme | — | 点击「Light theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `dark-theme.activate` | `foxos sudoku dark-theme activate` | 主界面 > Colour theme > Dark theme | — | 点击「Dark theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `match-system-theme.activate` | `foxos sudoku match-system-theme activate` | 主界面 > Colour theme > Match system theme | — | 点击「Match system theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `records.activate` | `foxos sudoku records activate` | 主界面 > Records | — | 点击「Records」（button） | 可能（应用提供撤销，未逐项验证） |
| `settings.show` | `foxos sudoku settings show` | 主界面 > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `signed-as-local.activate` | `foxos sudoku signed-as-local activate` | 主界面 > Signed in as local | — | 点击「Signed in as local」（button） | 可能（应用提供撤销，未逐项验证） |
| `pause.pause` | `foxos sudoku pause pause` | 主界面 > Pause | — | 点击「Pause」（button） | 可能（应用提供撤销，未逐项验证） |
| `ctrlz.undo` | `foxos sudoku ctrlz undo` | 主界面 > Tools > Undo (Ctrl+Z) | — | 点击「Undo (Ctrl+Z)」（button） | 可能（应用提供撤销，未逐项验证） |
| `ctrlshiftz.redo` | `foxos sudoku ctrlshiftz redo` | 主界面 > Tools > Redo (Ctrl+Shift+Z) | — | 点击「Redo (Ctrl+Shift+Z)」（button） | 可能（应用提供撤销，未逐项验证） |
| `erase-backspace.activate` | `foxos sudoku erase-backspace activate` | 主界面 > Tools > Erase (Backspace) | — | 点击「Erase (Backspace)」（button） | 可能（应用提供撤销，未逐项验证） |
| `hint-h.activate` | `foxos sudoku hint-h activate` | 主界面 > Tools > Hint (H) | — | 点击「Hint (H)」（button） | 可能（应用提供撤销，未逐项验证） |
| `next-puzzle.set` | `foxos sudoku next-puzzle set` | 主界面 > aside > Next puzzle | `value`（必填）, `submit` | 把「Next puzzle」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `puzzle.create` | `foxos sudoku puzzle create` | 主界面 > aside > New puzzle | — | 点击「New puzzle」（button） | 可能（应用提供撤销，未逐项验证） |
| `daily.activate` | `foxos sudoku daily activate` | 主界面 > aside > Daily | — | 点击「Daily」（button） | 可能（应用提供撤销，未逐项验证） |
| `powered-by-puter.show` | `foxos sudoku powered-by-puter show` | 主界面 > footer > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `check-as-i-go.toggle` | `foxos sudoku check-as-i-go toggle` | Settings > Check as I go | — | 切换「Check as I go」 | 可能（应用提供撤销，未逐项验证） |
| `highlight-row-column-box.toggle` | `foxos sudoku highlight-row-column-box toggle` | Settings > Highlight row, column and box | — | 切换「Highlight row, column and box」 | 可能（应用提供撤销，未逐项验证） |
| `highlight-matching-digits.toggle` | `foxos sudoku highlight-matching-digits toggle` | Settings > Highlight matching digits | — | 切换「Highlight matching digits」 | 可能（应用提供撤销，未逐项验证） |
| `show-digits-remaining.toggle` | `foxos sudoku show-digits-remaining toggle` | Settings > Show digits remaining | — | 切换「Show digits remaining」 | 可能（应用提供撤销，未逐项验证） |
| `show-clock.toggle` | `foxos sudoku show-clock toggle` | Settings > Show the clock | — | 切换「Show the clock」 | 可能（应用提供撤销，未逐项验证） |
| `done.confirm` | `foxos sudoku done confirm` | Settings > dialog > Done | — | 点击「Done」（button） | 可能（应用提供撤销，未逐项验证） |
| `edit.redo-shift` | `foxos sudoku edit redo-shift` | 键盘 mod+shift+y | — | 在当前焦点上按 mod+shift+y（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `edit.undo` | `foxos sudoku edit undo` | 键盘 mod+z | — | 在当前焦点上按 mod+z（src/main.js 中定义） | 不适用 |
