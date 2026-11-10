# Parametric（parametric）操作清单

分组：engineering · 替代 SolidWorks, Autodesk Fusion, Autodesk Inventor · 许可证 AGPL-3.0-only · 页面标题「Parametric」

共 33 个操作，全部有语义命令（`foxos parametric <资源> <动词>`，MCP 工具 `parametric.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `item.select` | `foxos parametric item select` | 主界面 > # view. use arrow keys to rotate, ctrl and arrow keys to pan, f to fit, plus and minus to zoom. | `target`（必填） | 点击名称匹配的「# view. use arrow keys to rotate, ctrl and arrow keys to pan, f to fit, plus and minus to zoom.」项（application） | 不适用（只读） |
| `default-units.select` | `foxos parametric default-units select` | Options... > dialog > default units for * | `target`（必填） | 点击名称匹配的「default units for *」项（combobox） | 不适用（只读） |
| `graphics-area.dismiss` | `foxos parametric graphics-area dismiss` | 主界面 > Skip to the graphics area | — | 点击「Skip to the graphics area」（link） | 不适用（只读） |
| `file.activate` | `foxos parametric file activate` | 主界面 > Main menu > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos parametric edit update` | 主界面 > Main menu > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos parametric view show` | 主界面 > Main menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos parametric insert create` | 主界面 > Main menu > Insert | — | 点击「Insert」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `tools.activate` | `foxos parametric tools activate` | 主界面 > Main menu > Tools | — | 点击「Tools」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos parametric help show` | 主界面 > Main menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `open.open` | `foxos parametric open open` | 主界面 > Open... | — | 点击「Open...」（button） | 不适用（只读） |
| `save.save` | `foxos parametric save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos parametric undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos parametric redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `rebuild.activate` | `foxos parametric rebuild activate` | 主界面 > Rebuild | — | 点击「Rebuild」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.activate` | `foxos parametric options activate` | 主界面 > Options... | — | 点击「Options...」（button） | 可能（应用提供撤销，未逐项验证） |
| `part.rename` | `foxos parametric part rename` | 主界面 > header > Rename part | — | 点击「Rename part」（button） | 可能（应用提供撤销，未逐项验证） |
| `search-commands.set` | `foxos parametric search-commands set` | 主界面 > Search commands | `value`（必填）, `submit` | 把「Search commands」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `assistant.activate` | `foxos parametric assistant activate` | 主界面 > Assistant | — | 点击「Assistant」（button） | 可能（应用提供撤销，未逐项验证） |
| `share.share` | `foxos parametric share share` | 主界面 > Share... | — | 点击「Share...」（button） | 可能（应用提供撤销，未逐项验证） |
| `source-code-github.show` | `foxos parametric source-code-github show` | 主界面 > Source code on GitHub | — | 点击「Source code on GitHub」（link），切换到该视图 | 不适用（只读） |
| `apps.activate` | `foxos parametric apps activate` | 主界面 > Apps | — | 点击「Apps」（button） | 可能（应用提供撤销，未逐项验证） |
| `account.activate` | `foxos parametric account activate` | 主界面 > Account | — | 点击「Account」（button） | 可能（应用提供撤销，未逐项验证） |
| `panel.resize` | `foxos parametric panel resize` | 主界面 > Resize panel | — | 点击「Resize panel」（separator） | 可能（应用提供撤销，未逐项验证） |
| `unit-system.activate` | `foxos parametric unit-system activate` | 主界面 > footer > Unit system | — | 点击「Unit system」（button） | 可能（应用提供撤销，未逐项验证） |
| `close.close` | `foxos parametric close close` | Options... > Close | — | 点击「Close」（button） | 不适用（只读） |
| `system.activate` | `foxos parametric system activate` | Options... > Theme > System | — | 点击「System」（button） | 可能（应用提供撤销，未逐项验证） |
| `light.activate` | `foxos parametric light activate` | Options... > Theme > Light | — | 点击「Light」（button） | 可能（应用提供撤销，未逐项验证） |
| `dark.activate` | `foxos parametric dark activate` | Options... > Theme > Dark | — | 点击「Dark」（button） | 可能（应用提供撤销，未逐项验证） |
| `image-quality.set` | `foxos parametric image-quality set` | Options... > dialog > Image quality | `value`（必填）, `submit` | 把「Image quality」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `reverse-mouse-wheel-zoom-direction.toggle` | `foxos parametric reverse-mouse-wheel-zoom-direction toggle` | Options... > dialog > Reverse mouse wheel zoom direction | — | 切换「Reverse mouse wheel zoom direction」 | 可能（应用提供撤销，未逐项验证） |
| `done.confirm` | `foxos parametric done confirm` | Options... > dialog > Done | — | 点击「Done」（button） | 可能（应用提供撤销，未逐项验证） |
| `apps-tab.open` | `foxos parametric apps-tab open` | Apps > Open Apps in a new tab | — | 点击「Open Apps in a new tab」（link） | 不适用（只读） |
| `document.save` | `foxos parametric document save` | 键盘 mod+s | — | 在当前焦点上按 mod+s（src/app/app.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
