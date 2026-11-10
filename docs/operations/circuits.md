# Circuits（circuits）操作清单

分组：engineering · 替代 Altium Designer, Autodesk Eagle, OrCAD · 许可证 AGPL-3.0-only · 页面标题「Circuits」

共 39 个操作，全部有语义命令（`foxos circuits <资源> <动词>`，MCP 工具 `circuits.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `theme.select` | `foxos circuits theme select` | 主界面 > theme: * | `target`（必填） | 点击名称匹配的「theme: *」项（button） | 不适用（只读） |
| `account.select` | `foxos circuits account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `examplea-led-blinker-its-board.open` | `foxos circuits examplea-led-blinker-its-board open` | 主界面 > Start > open the examplea # led blinker with its board | `target`（必填） | 点击名称匹配的「open the examplea # led blinker with its board」项（button） | 不适用（只读） |
| `design-canvas.dismiss` | `foxos circuits design-canvas dismiss` | 主界面 > Skip to the design canvas | — | 点击「Skip to the design canvas」（link） | 不适用（只读） |
| `project.create` | `foxos circuits project create` | 主界面 > New project | — | 点击「New project」（button） | 可能（应用提供撤销，未逐项验证） |
| `project.open` | `foxos circuits project open` | 主界面 > Open project | — | 点击「Open project」（button） | 不适用（只读） |
| `save.save` | `foxos circuits save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos circuits undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos circuits redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `commandsctrlk.search` | `foxos circuits commandsctrlk search` | 主界面 > banner > Search commandsCtrl+K | — | 点击「Search commandsCtrl+K」（button） | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos circuits source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `file.activate` | `foxos circuits file activate` | 主界面 > Main menu > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos circuits edit update` | 主界面 > Main menu > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos circuits view show` | 主界面 > Main menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `project.activate` | `foxos circuits project activate` | 主界面 > Main menu > Project | — | 点击「Project」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `reports.activate` | `foxos circuits reports activate` | 主界面 > Main menu > Reports | — | 点击「Reports」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `window.activate` | `foxos circuits window activate` | 主界面 > Main menu > Window | — | 点击「Window」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos circuits help show` | 主界面 > Main menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `schematic-sheet.create` | `foxos circuits schematic-sheet create` | 主界面 > Add schematic sheet | — | 点击「Add schematic sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `board.create` | `foxos circuits board create` | 主界面 > Add board | — | 点击「Add board」（button） | 可能（应用提供撤销，未逐项验证） |
| `project-options.activate` | `foxos circuits project-options activate` | 主界面 > Project options | — | 点击「Project options」（button） | 可能（应用提供撤销，未逐项验证） |
| `projects.show` | `foxos circuits projects show` | 主界面 > Project panels > Projects | — | 点击「Projects」（tab），切换到该视图 | 不适用（只读） |
| `navigator.show` | `foxos circuits navigator show` | 主界面 > Project panels > Navigator | — | 点击「Navigator」（tab），切换到该视图 | 不适用（只读） |
| `properties.show` | `foxos circuits properties show` | 主界面 > Design panels > Properties | — | 点击「Properties」（tab），切换到该视图 | 不适用（只读） |
| `components.show` | `foxos circuits components show` | 主界面 > Design panels > Components | — | 点击「Components」（tab），切换到该视图 | 不适用（只读） |
| `puter.show` | `foxos circuits puter show` | 主界面 > Status > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `panels.activate` | `foxos circuits panels activate` | 主界面 > Status > Panels | — | 点击「Panels」（button） | 可能（应用提供撤销，未逐项验证） |
| `it.dismiss` | `foxos circuits it dismiss` | 主界面 > Notifications > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `notification.dismiss` | `foxos circuits notification dismiss` | 主界面 > Dismiss notification | — | 点击「Dismiss notification」（button） | 不适用（只读） |
| `preferences.activate` | `foxos circuits preferences activate` | Account: local > Account > Preferences | — | 点击「Preferences」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `schematic-sheet.activate` | `foxos circuits schematic-sheet activate` | Project options > Context menu > Schematic sheet | — | 点击「Schematic sheet」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `board.activate` | `foxos circuits board activate` | Project options > Context menu > Board | — | 点击「Board」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `project.rename` | `foxos circuits project rename` | Project options > Context menu > Rename project... | — | 点击「Rename project...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `savectrls.activate` | `foxos circuits savectrls activate` | Project options > Context menu > SaveCtrl+S | — | 点击「SaveCtrl+S」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `project-file.export` | `foxos circuits project-file export` | Project options > Context menu > Download project file | — | 点击「Download project file」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `compile-electrical-rules-check.activate` | `foxos circuits compile-electrical-rules-check activate` | Project options > Context menu > Compile (electrical rules check) | — | 点击「Compile (electrical rules check)」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `annotate-schematics.activate` | `foxos circuits annotate-schematics activate` | Project options > Context menu > Annotate schematics... | — | 点击「Annotate schematics...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `board-from-schematic.update` | `foxos circuits board-from-schematic update` | Project options > Context menu > Update board from schematic... | — | 点击「Update board from schematic...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `project.close` | `foxos circuits project close` | Project options > Context menu > Close project | — | 点击「Close project」（menuitem） | 不适用（只读） |
