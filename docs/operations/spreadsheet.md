# Spreadsheet（spreadsheet）操作清单

分组：office · 替代 Microsoft Excel, Google Sheets, Apple Numbers · 许可证 AGPL-3.0-only · 页面标题「Untitled spreadsheet · Spreadsheet」

共 371 个操作，全部有语义命令（`foxos spreadsheet <资源> <动词>`，MCP 工具 `spreadsheet.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account-menu.select` | `foxos spreadsheet account-menu select` | 主界面 > account menu for * | `target`（必填） | 点击名称匹配的「account menu for *」项（button） | 不适用（只读） |
| `font.select` | `foxos spreadsheet font select` | 主界面 > font: * | `target`（必填） | 点击名称匹配的「font: *」项（button） | 不适用（只读） |
| `font-size.select` | `foxos spreadsheet font-size select` | 主界面 > font size: * | `target`（必填） | 点击名称匹配的「font size: *」项（button） | 不适用（只读） |
| `font-size-2.select` | `foxos spreadsheet font-size-2 select` | 主界面 > # font size | `target`（必填） | 点击名称匹配的「# font size」项（button） | 不适用（只读） |
| `indent.select` | `foxos spreadsheet indent select` | 主界面 > # indent | `target`（必填） | 点击名称匹配的「# indent」项（button） | 不适用（只读） |
| `number-format.select` | `foxos spreadsheet number-format select` | 主界面 > number format: * | `target`（必填） | 点击名称匹配的「number format: *」项（button） | 不适用（只读） |
| `places.show` | `foxos spreadsheet places show` | 主界面 > more # places | `target`（必填） | 点击名称匹配的「more # places」项（button） | 不适用（只读） |
| `fewer-places.select` | `foxos spreadsheet fewer-places select` | 主界面 > fewer # places | `target`（必填） | 点击名称匹配的「fewer # places」项（button） | 不适用（只读） |
| `sheets.select` | `foxos spreadsheet sheets select` | 主界面 > Sheets > # | `target`（必填） | 点击名称匹配的「#」项（tab） | 不适用（只读） |
| `options.select` | `foxos spreadsheet options select` | 主界面 > # options | `target`（必填） | 点击名称匹配的「# options」项（button） | 不适用（只读） |
| `view.zoom-level` | `foxos spreadsheet view zoom-level` | 主界面 > zoom level: * | `target`（必填） | 点击名称匹配的「zoom level: *」项（button） | 可能（应用提供撤销，未逐项验证） |
| `other-charts.select` | `foxos spreadsheet other-charts select` | Insert > other charts: * | `target`（必填） | 点击名称匹配的「other charts: *」项（button） | 不适用（只读） |
| `pen.select` | `foxos spreadsheet pen select` | Draw > pen: * | `target`（必填） | 点击名称匹配的「pen: *」项（button） | 不适用（只读） |
| `pencil.select` | `foxos spreadsheet pencil select` | Draw > pencil: * | `target`（必填） | 点击名称匹配的「pencil: *」项（button） | 不适用（只读） |
| `highlighter.select` | `foxos spreadsheet highlighter select` | Draw > highlighter: * | `target`（必填） | 点击名称匹配的「highlighter: *」项（button） | 不适用（只读） |
| `item.select` | `foxos spreadsheet item select` | View > #% | `target`（必填） | 点击名称匹配的「#%」项（button） | 不适用（只读） |
| `spreadsheets.previous` | `foxos spreadsheet spreadsheets previous` | 主界面 > Back to all spreadsheets | — | 点击「Back to all spreadsheets」（button） | 不适用（只读） |
| `autosave.toggle` | `foxos spreadsheet autosave toggle` | 主界面 > AutoSave | — | 切换「AutoSave」 | 可能（应用提供撤销，未逐项验证） |
| `save.save` | `foxos spreadsheet save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos spreadsheet undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `history.undo` | `foxos spreadsheet history undo` | 主界面 > Undo history | — | 点击「Undo history」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos spreadsheet redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar.activate` | `foxos spreadsheet customize-quick-access-toolbar activate` | 主界面 > Customize Quick Access Toolbar | — | 点击「Customize Quick Access Toolbar」（button） | 可能（应用提供撤销，未逐项验证） |
| `file.activate` | `foxos spreadsheet file activate` | 主界面 > Menus > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos spreadsheet edit update` | 主界面 > Menus > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos spreadsheet view show` | 主界面 > Menus > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos spreadsheet insert create` | 主界面 > Menus > Insert | — | 点击「Insert」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `format.activate` | `foxos spreadsheet format activate` | 主界面 > Menus > Format | — | 点击「Format」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `data.activate` | `foxos spreadsheet data activate` | 主界面 > Menus > Data | — | 点击「Data」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `tools.activate` | `foxos spreadsheet tools activate` | 主界面 > Menus > Tools | — | 点击「Tools」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos spreadsheet help show` | 主界面 > Menus > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `untitled-spreadsheet.rename` | `foxos spreadsheet untitled-spreadsheet rename` | 主界面 > header > Rename "Untitled spreadsheet" | — | 点击「Rename "Untitled spreadsheet"」（button） | 可能（应用提供撤销，未逐项验证） |
| `saved.activate` | `foxos spreadsheet saved activate` | 主界面 > header > Saved | — | 点击「Saved」（button） | 可能（应用提供撤销，未逐项验证） |
| `menus.search` | `foxos spreadsheet menus search` | 主界面 > Search the menus | — | 点击「Search the menus」（button） | 不适用（只读） |
| `comments.activate` | `foxos spreadsheet comments activate` | 主界面 > Comments | — | 点击「Comments」（button） | 可能（应用提供撤销，未逐项验证） |
| `home.show` | `foxos spreadsheet home show` | 主界面 > Ribbon > Home | — | 点击「Home」（tab），切换到该视图 | 不适用（只读） |
| `insert-2.create` | `foxos spreadsheet insert-2 create` | 主界面 > Ribbon > Insert | — | 点击「Insert」（tab） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos spreadsheet draw draw` | 主界面 > Ribbon > Draw | — | 点击「Draw」（tab） | 可能（应用提供撤销，未逐项验证） |
| `page-layout.show` | `foxos spreadsheet page-layout show` | 主界面 > Ribbon > Page Layout | — | 点击「Page Layout」（tab），切换到该视图 | 不适用（只读） |
| `formulas.show` | `foxos spreadsheet formulas show` | 主界面 > Ribbon > Formulas | — | 点击「Formulas」（tab），切换到该视图 | 不适用（只读） |
| `data.show` | `foxos spreadsheet data show` | 主界面 > Ribbon > Data | — | 点击「Data」（tab），切换到该视图 | 不适用（只读） |
| `review.show` | `foxos spreadsheet review show` | 主界面 > Ribbon > Review | — | 点击「Review」（tab），切换到该视图 | 不适用（只读） |
| `view-2.show` | `foxos spreadsheet view-2 show` | 主界面 > Ribbon > View | — | 点击「View」（tab），切换到该视图 | 不适用（只读） |
| `automate.show` | `foxos spreadsheet automate show` | 主界面 > Ribbon > Automate | — | 点击「Automate」（tab），切换到该视图 | 不适用（只读） |
| `scroll-ribbon-left.activate` | `foxos spreadsheet scroll-ribbon-left activate` | 主界面 > Scroll ribbon left | — | 点击「Scroll ribbon left」（button） | 可能（应用提供撤销，未逐项验证） |
| `scroll-ribbon-right.activate` | `foxos spreadsheet scroll-ribbon-right activate` | 主界面 > Scroll ribbon right | — | 点击「Scroll ribbon right」（button） | 可能（应用提供撤销，未逐项验证） |
| `ribbon.collapse` | `foxos spreadsheet ribbon collapse` | 主界面 > Collapse ribbon | — | 点击「Collapse ribbon」（button） | 不适用（只读） |
| `paste.paste` | `foxos spreadsheet paste paste` | 主界面 > Paste | — | 点击「Paste」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.paste` | `foxos spreadsheet options paste` | 主界面 > Paste options | — | 点击「Paste options」（button） | 可能（应用提供撤销，未逐项验证） |
| `cut.cut` | `foxos spreadsheet cut cut` | 主界面 > Cut | — | 点击「Cut」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.copy` | `foxos spreadsheet copy copy` | 主界面 > Copy | — | 点击「Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-painter.activate` | `foxos spreadsheet format-painter activate` | 主界面 > Format Painter | — | 点击「Format Painter」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-font-size.activate` | `foxos spreadsheet increase-font-size activate` | 主界面 > Increase font size | — | 点击「Increase font size」（button） | 可能（应用提供撤销，未逐项验证） |
| `bold.format` | `foxos spreadsheet bold format` | 主界面 > Bold | — | 点击「Bold」（button） | 可能（应用提供撤销，未逐项验证） |
| `italic.format` | `foxos spreadsheet italic format` | 主界面 > Italic | — | 点击「Italic」（button） | 可能（应用提供撤销，未逐项验证） |
| `underline.format` | `foxos spreadsheet underline format` | 主界面 > Underline | — | 点击「Underline」（button） | 可能（应用提供撤销，未逐项验证） |
| `borders.activate` | `foxos spreadsheet borders activate` | 主界面 > Borders | — | 点击「Borders」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-color-yellow.confirm` | `foxos spreadsheet fill-color-yellow confirm` | 主界面 > Apply fill color yellow | — | 点击「Apply fill color yellow」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-color.activate` | `foxos spreadsheet fill-color activate` | 主界面 > Fill color | — | 点击「Fill color」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-color-red.confirm` | `foxos spreadsheet font-color-red confirm` | 主界面 > Apply font color red | — | 点击「Apply font color red」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-color.activate` | `foxos spreadsheet text-color activate` | 主界面 > Text color | — | 点击「Text color」（button） | 可能（应用提供撤销，未逐项验证） |
| `top-align.activate` | `foxos spreadsheet top-align activate` | 主界面 > Top align | — | 点击「Top align」（button） | 可能（应用提供撤销，未逐项验证） |
| `middle-align.activate` | `foxos spreadsheet middle-align activate` | 主界面 > Middle align | — | 点击「Middle align」（button） | 可能（应用提供撤销，未逐项验证） |
| `bottom-align.activate` | `foxos spreadsheet bottom-align activate` | 主界面 > Bottom align | — | 点击「Bottom align」（button） | 可能（应用提供撤销，未逐项验证） |
| `orientation.activate` | `foxos spreadsheet orientation activate` | 主界面 > Orientation | — | 点击「Orientation」（button） | 可能（应用提供撤销，未逐项验证） |
| `left.align` | `foxos spreadsheet left align` | 主界面 > Align left | — | 点击「Align left」（button） | 可能（应用提供撤销，未逐项验证） |
| `center.align` | `foxos spreadsheet center align` | 主界面 > Align center | — | 点击「Align center」（button） | 可能（应用提供撤销，未逐项验证） |
| `right.align` | `foxos spreadsheet right align` | 主界面 > Align right | — | 点击「Align right」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-indent.activate` | `foxos spreadsheet increase-indent activate` | 主界面 > Increase indent | — | 点击「Increase indent」（button） | 可能（应用提供撤销，未逐项验证） |
| `wrap-text.activate` | `foxos spreadsheet wrap-text activate` | 主界面 > Wrap text | — | 点击「Wrap text」（button） | 可能（应用提供撤销，未逐项验证） |
| `merge-center.activate` | `foxos spreadsheet merge-center activate` | 主界面 > Merge & Center | — | 点击「Merge & Center」（button） | 可能（应用提供撤销，未逐项验证） |
| `merge-options.activate` | `foxos spreadsheet merge-options activate` | 主界面 > Merge options | — | 点击「Merge options」（button） | 可能（应用提供撤销，未逐项验证） |
| `accounting-number-format.activate` | `foxos spreadsheet accounting-number-format activate` | 主界面 > Accounting Number Format | — | 点击「Accounting Number Format」（button） | 可能（应用提供撤销，未逐项验证） |
| `accounting-number-format-options.activate` | `foxos spreadsheet accounting-number-format-options activate` | 主界面 > Accounting Number Format options | — | 点击「Accounting Number Format options」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-as-percent.activate` | `foxos spreadsheet format-as-percent activate` | 主界面 > Format as percent | — | 点击「Format as percent」（button） | 可能（应用提供撤销，未逐项验证） |
| `comma-style.activate` | `foxos spreadsheet comma-style activate` | 主界面 > Comma Style | — | 点击「Comma Style」（button） | 可能（应用提供撤销，未逐项验证） |
| `conditional-formatting.activate` | `foxos spreadsheet conditional-formatting activate` | 主界面 > Conditional formatting | — | 点击「Conditional formatting」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-as-table.activate` | `foxos spreadsheet format-as-table activate` | 主界面 > Format as Table | — | 点击「Format as Table」（button） | 可能（应用提供撤销，未逐项验证） |
| `cell-styles.activate` | `foxos spreadsheet cell-styles activate` | 主界面 > Cell styles | — | 点击「Cell styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `insert-3.create` | `foxos spreadsheet insert-3 create` | 主界面 > Insert | — | 点击「Insert」（button） | 可能（应用提供撤销，未逐项验证） |
| `delete.delete` | `foxos spreadsheet delete delete` | 主界面 > Delete | — | 点击「Delete」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-2.activate` | `foxos spreadsheet format-2 activate` | 主界面 > Format | — | 点击「Format」（button） | 可能（应用提供撤销，未逐项验证） |
| `autosum.activate` | `foxos spreadsheet autosum activate` | 主界面 > AutoSum | — | 点击「AutoSum」（button） | 可能（应用提供撤销，未逐项验证） |
| `autosum-options.activate` | `foxos spreadsheet autosum-options activate` | 主界面 > AutoSum options | — | 点击「AutoSum options」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill.activate` | `foxos spreadsheet fill activate` | 主界面 > Fill | — | 点击「Fill」（button） | 可能（应用提供撤销，未逐项验证） |
| `clear.clear` | `foxos spreadsheet clear clear` | 主界面 > Clear | — | 点击「Clear」（button） | 可能（应用提供撤销，未逐项验证） |
| `filter.sort` | `foxos spreadsheet filter sort` | 主界面 > Sort & Filter | — | 点击「Sort & Filter」（button） | 不适用（只读） |
| `select.search` | `foxos spreadsheet select search` | 主界面 > Find & Select | — | 点击「Find & Select」（button） | 不适用（只读） |
| `cell-reference.set` | `foxos spreadsheet cell-reference set` | 主界面 > Cell reference | `value`（必填）, `submit` | 把「Cell reference」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `named-ranges.activate` | `foxos spreadsheet named-ranges activate` | 主界面 > Named ranges | — | 点击「Named ranges」（button） | 可能（应用提供撤销，未逐项验证） |
| `edit.cancel` | `foxos spreadsheet edit cancel` | 主界面 > Cancel edit | — | 点击「Cancel edit」（button） | 不适用（只读） |
| `edit.confirm` | `foxos spreadsheet edit confirm` | 主界面 > Apply edit | — | 点击「Apply edit」（button） | 可能（应用提供撤销，未逐项验证） |
| `function.create` | `foxos spreadsheet function create` | 主界面 > Insert function | — | 点击「Insert function」（button） | 可能（应用提供撤销，未逐项验证） |
| `formula-or-value.set` | `foxos spreadsheet formula-or-value set` | 主界面 > Formula or value | `value`（必填）, `submit` | 把「Formula or value」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `formula-bar.expand` | `foxos spreadsheet formula-bar expand` | 主界面 > Expand the formula bar | — | 点击「Expand the formula bar」（button） | 不适用（只读） |
| `select.select` | `foxos spreadsheet select select` | 主界面 > Select all | — | 点击「Select all」（button） | 不适用（只读） |
| `spreadsheet-grid.activate` | `foxos spreadsheet spreadsheet-grid activate` | 主界面 > Spreadsheet grid | — | 点击「Spreadsheet grid」（grid） | 可能（应用提供撤销，未逐项验证） |
| `scroll-sheets-left.activate` | `foxos spreadsheet scroll-sheets-left activate` | 主界面 > Scroll sheets left | — | 点击「Scroll sheets left」（button） | 可能（应用提供撤销，未逐项验证） |
| `scroll-sheets-right.activate` | `foxos spreadsheet scroll-sheets-right activate` | 主界面 > Scroll sheets right | — | 点击「Scroll sheets right」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheets.activate` | `foxos spreadsheet sheets activate` | 主界面 > All sheets | — | 点击「All sheets」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheet.create` | `foxos spreadsheet sheet create` | 主界面 > Add sheet | — | 点击「Add sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `accessibility.run` | `foxos spreadsheet accessibility run` | 主界面 > Check Accessibility | — | 点击「Check Accessibility」（button） | 可能（应用提供撤销，未逐项验证） |
| `normal.activate` | `foxos spreadsheet normal activate` | 主界面 > Normal | — | 点击「Normal」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-layout.activate` | `foxos spreadsheet page-layout activate` | 主界面 > Page Layout | — | 点击「Page Layout」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-break-preview.activate` | `foxos spreadsheet page-break-preview activate` | 主界面 > Page Break Preview | — | 点击「Page Break Preview」（button） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-out` | `foxos spreadsheet view zoom-out` | 主界面 > Zoom out | — | 点击「Zoom out」（button） | 可能（应用提供撤销，未逐项验证） |
| `worksheet-zoom.set` | `foxos spreadsheet worksheet-zoom set` | 主界面 > Worksheet zoom | `value`（必填）, `submit` | 把「Worksheet zoom」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-` | `foxos spreadsheet view zoom-` | 主界面 > Zoom in | — | 点击「Zoom in」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant.resize` | `foxos spreadsheet assistant resize` | 主界面 > Resize the assistant | — | 点击「Resize the assistant」（separator） | 可能（应用提供撤销，未逐项验证） |
| `chat.create` | `foxos spreadsheet chat create` | 主界面 > New chat | — | 点击「New chat」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant-settings.activate` | `foxos spreadsheet assistant-settings activate` | 主界面 > Assistant settings | — | 点击「Assistant settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant.collapse` | `foxos spreadsheet assistant collapse` | 主界面 > Collapse the assistant | — | 点击「Collapse the assistant」（button） | 不适用（只读） |
| `loan-calculator-payment-schedule.create` | `foxos spreadsheet loan-calculator-payment-schedule create` | 主界面 > Suggestions > Create a loan calculator with a payment schedule | — | 点击「Create a loan calculator with a payment schedule」（button） | 可能（应用提供撤销，未逐项验证） |
| `message-assistant.set` | `foxos spreadsheet message-assistant set` | 主界面 > Message the assistant | `value`（必填）, `submit` | 把「Message the assistant」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `attach-files.activate` | `foxos spreadsheet attach-files activate` | 主界面 > Attach files | — | 点击「Attach files」（button） | 可能（应用提供撤销，未逐项验证） |
| `send.send` | `foxos spreadsheet send send` | 主界面 > Send | — | 点击「Send」（button） | 可能（应用提供撤销，未逐项验证） |
| `spreadsheet.create` | `foxos spreadsheet spreadsheet create` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > New Spreadsheet | — | 点击「New Spreadsheet」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `open.open` | `foxos spreadsheet open open` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Open | — | 点击「Open」（menuitemcheckbox） | 不适用（只读） |
| `customize-quick-access-toolbar-save.save` | `foxos spreadsheet customize-quick-access-toolbar-save save` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Save | — | 点击「Save」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `print.print` | `foxos spreadsheet print print` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Print | — | 点击「Print」（menuitemcheckbox） | 不适用（只读） |
| `spelling.activate` | `foxos spreadsheet spelling activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Spelling | — | 点击「Spelling」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-undo.undo` | `foxos spreadsheet customize-quick-access-toolbar-undo undo` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Undo | — | 点击「Undo」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-redo.redo` | `foxos spreadsheet customize-quick-access-toolbar-redo redo` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Redo | — | 点击「Redo」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `ascending.sort` | `foxos spreadsheet ascending sort` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Sort Ascending | — | 点击「Sort Ascending」（menuitemcheckbox） | 不适用（只读） |
| `descending.sort` | `foxos spreadsheet descending sort` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Sort Descending | — | 点击「Sort Descending」（menuitemcheckbox） | 不适用（只读） |
| `find.search` | `foxos spreadsheet find search` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Find | — | 点击「Find」（menuitemcheckbox） | 不适用（只读） |
| `chart.create` | `foxos spreadsheet chart create` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Insert Chart | — | 点击「Insert Chart」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `filter.filter` | `foxos spreadsheet filter filter` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Filter | — | 点击「Filter」（menuitemcheckbox） | 不适用（只读） |
| `commands.show` | `foxos spreadsheet commands show` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > More Commands… | — | 点击「More Commands…」（menuitem），切换到该视图 | 不适用（只读） |
| `below-ribbon.show` | `foxos spreadsheet below-ribbon show` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Show Below the Ribbon | — | 点击「Show Below the Ribbon」（menuitem），切换到该视图 | 不适用（只读） |
| `command-labels.show` | `foxos spreadsheet command-labels show` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Show Command Labels | — | 点击「Show Command Labels」（menuitemcheckbox），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos spreadsheet close close` | Rename "Untitled spreadsheet" > Close | — | 点击「Close」（button） | 不适用（只读） |
| `name.set` | `foxos spreadsheet name set` | Rename "Untitled spreadsheet" > Name | `value`（必填）, `submit` | 把「Name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `cancel.cancel` | `foxos spreadsheet cancel cancel` | Rename "Untitled spreadsheet" > Rename spreadsheet > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `rename.rename` | `foxos spreadsheet rename rename` | Rename "Untitled spreadsheet" > Rename spreadsheet > Rename | — | 点击「Rename」（button） | 可能（应用提供撤销，未逐项验证） |
| `system-theme.toggle` | `foxos spreadsheet system-theme toggle` | Account menu for local > System theme | — | 切换「System theme」 | 可能（应用提供撤销，未逐项验证） |
| `light-theme.toggle` | `foxos spreadsheet light-theme toggle` | Account menu for local > Light theme | — | 切换「Light theme」 | 可能（应用提供撤销，未逐项验证） |
| `dark-theme.toggle` | `foxos spreadsheet dark-theme toggle` | Account menu for local > Dark theme | — | 切换「Dark theme」 | 可能（应用提供撤销，未逐项验证） |
| `regional-format-english-united-states.activate` | `foxos spreadsheet regional-format-english-united-states activate` | Account menu for local > Regional format, English (United States) | — | 点击「Regional format, English (United States)」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `options.activate` | `foxos spreadsheet options activate` | Account menu for local > Account > Options… | — | 点击「Options…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcuts.activate` | `foxos spreadsheet keyboard-shortcuts activate` | Account menu for local > Account > Keyboard shortcuts… | — | 点击「Keyboard shortcuts…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `about.show` | `foxos spreadsheet about show` | Account menu for local > Account > About… | — | 点击「About…」（menuitem），切换到该视图 | 不适用（只读） |
| `pivottable.activate` | `foxos spreadsheet pivottable activate` | Insert > PivotTable | — | 点击「PivotTable」（button） | 可能（应用提供撤销，未逐项验证） |
| `recommended-pivottables.activate` | `foxos spreadsheet recommended-pivottables activate` | Insert > Recommended PivotTables | — | 点击「Recommended PivotTables」（button） | 可能（应用提供撤销，未逐项验证） |
| `table.activate` | `foxos spreadsheet table activate` | Insert > Table | — | 点击「Table」（button） | 可能（应用提供撤销，未逐项验证） |
| `pictures.activate` | `foxos spreadsheet pictures activate` | Insert > Pictures | — | 点击「Pictures」（button） | 可能（应用提供撤销，未逐项验证） |
| `shapes.activate` | `foxos spreadsheet shapes activate` | Insert > Shapes | — | 点击「Shapes」（button） | 可能（应用提供撤销，未逐项验证） |
| `icons.activate` | `foxos spreadsheet icons activate` | Insert > Icons | — | 点击「Icons」（button） | 可能（应用提供撤销，未逐项验证） |
| `smartart-graphic.create` | `foxos spreadsheet smartart-graphic create` | Insert > Insert SmartArt graphic | — | 点击「Insert SmartArt graphic」（button） | 可能（应用提供撤销，未逐项验证） |
| `recommended-charts.activate` | `foxos spreadsheet recommended-charts activate` | Insert > Recommended Charts | — | 点击「Recommended Charts」（button） | 可能（应用提供撤销，未逐项验证） |
| `column-chart.create` | `foxos spreadsheet column-chart create` | Insert > Insert column chart | — | 点击「Insert column chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `line-chart.create` | `foxos spreadsheet line-chart create` | Insert > Insert line chart | — | 点击「Insert line chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `pie-chart.create` | `foxos spreadsheet pie-chart create` | Insert > Insert pie chart | — | 点击「Insert pie chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `bar-chart.create` | `foxos spreadsheet bar-chart create` | Insert > Insert bar chart | — | 点击「Insert bar chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `area-chart.create` | `foxos spreadsheet area-chart create` | Insert > Insert area chart | — | 点击「Insert area chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `scatter-chart.create` | `foxos spreadsheet scatter-chart create` | Insert > Insert scatter chart | — | 点击「Insert scatter chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `hierarchy-chart.create` | `foxos spreadsheet hierarchy-chart create` | Insert > Insert hierarchy chart | — | 点击「Insert hierarchy chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `statistic-chart.create` | `foxos spreadsheet statistic-chart create` | Insert > Insert statistic chart | — | 点击「Insert statistic chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `combo-chart.create` | `foxos spreadsheet combo-chart create` | Insert > Insert combo chart | — | 点击「Insert combo chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `line-sparklines.create` | `foxos spreadsheet line-sparklines create` | Insert > Insert line sparklines | — | 点击「Insert line sparklines」（button） | 可能（应用提供撤销，未逐项验证） |
| `column-sparklines.create` | `foxos spreadsheet column-sparklines create` | Insert > Insert column sparklines | — | 点击「Insert column sparklines」（button） | 可能（应用提供撤销，未逐项验证） |
| `win-loss-sparklines.create` | `foxos spreadsheet win-loss-sparklines create` | Insert > Insert win/loss sparklines | — | 点击「Insert win/loss sparklines」（button） | 可能（应用提供撤销，未逐项验证） |
| `slicer.activate` | `foxos spreadsheet slicer activate` | Insert > Slicer | — | 点击「Slicer」（button） | 可能（应用提供撤销，未逐项验证） |
| `timeline.activate` | `foxos spreadsheet timeline activate` | Insert > Timeline | — | 点击「Timeline」（button） | 可能（应用提供撤销，未逐项验证） |
| `link.create` | `foxos spreadsheet link create` | Insert > Insert link | — | 点击「Insert link」（button） | 可能（应用提供撤销，未逐项验证） |
| `note.activate` | `foxos spreadsheet note activate` | Insert > Note | — | 点击「Note」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.activate` | `foxos spreadsheet comment activate` | Insert > Comment | — | 点击「Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-box.activate` | `foxos spreadsheet text-box activate` | Insert > Text Box | — | 点击「Text Box」（button） | 可能（应用提供撤销，未逐项验证） |
| `header-footer.activate` | `foxos spreadsheet header-footer activate` | Insert > Header & Footer | — | 点击「Header & Footer」（button） | 可能（应用提供撤销，未逐项验证） |
| `wordart.activate` | `foxos spreadsheet wordart activate` | Insert > WordArt | — | 点击「WordArt」（button） | 可能（应用提供撤销，未逐项验证） |
| `checkbox.activate` | `foxos spreadsheet checkbox activate` | Insert > Checkbox | — | 点击「Checkbox」（button） | 可能（应用提供撤销，未逐项验证） |
| `dropdown.activate` | `foxos spreadsheet dropdown activate` | Insert > Dropdown | — | 点击「Dropdown」（button） | 可能（应用提供撤销，未逐项验证） |
| `date-picker.activate` | `foxos spreadsheet date-picker activate` | Insert > Date Picker | — | 点击「Date Picker」（button） | 可能（应用提供撤销，未逐项验证） |
| `equation.activate` | `foxos spreadsheet equation activate` | Insert > Equation | — | 点击「Equation」（button） | 可能（应用提供撤销，未逐项验证） |
| `equation-options.activate` | `foxos spreadsheet equation-options activate` | Insert > Equation options | — | 点击「Equation options」（button） | 可能（应用提供撤销，未逐项验证） |
| `symbol.activate` | `foxos spreadsheet symbol activate` | Insert > Symbol | — | 点击「Symbol」（button） | 可能（应用提供撤销，未逐项验证） |
| `insert-sheet.create` | `foxos spreadsheet insert-sheet create` | Insert > New Sheet | — | 点击「New Sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `draw-select.select` | `foxos spreadsheet draw-select select` | Draw > Select | — | 点击「Select」（button） | 不适用（只读） |
| `lasso-select.activate` | `foxos spreadsheet lasso-select activate` | Draw > Lasso Select | — | 点击「Lasso Select」（button） | 可能（应用提供撤销，未逐项验证） |
| `eraser.activate` | `foxos spreadsheet eraser activate` | Draw > Eraser | — | 点击「Eraser」（button） | 可能（应用提供撤销，未逐项验证） |
| `pen.create` | `foxos spreadsheet pen create` | Draw > Add Pen | — | 点击「Add Pen」（button） | 可能（应用提供撤销，未逐项验证） |
| `touch.draw` | `foxos spreadsheet touch draw` | Draw > Draw with Touch | — | 点击「Draw with Touch」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-shape.activate` | `foxos spreadsheet ink-shape activate` | Draw > Ink to Shape | — | 点击「Ink to Shape」（button） | 可能（应用提供撤销，未逐项验证） |
| `themes.activate` | `foxos spreadsheet themes activate` | Page Layout > Themes | — | 点击「Themes」（button） | 可能（应用提供撤销，未逐项验证） |
| `theme-colors.activate` | `foxos spreadsheet theme-colors activate` | Page Layout > Theme Colors | — | 点击「Theme Colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `theme-fonts.activate` | `foxos spreadsheet theme-fonts activate` | Page Layout > Theme Fonts | — | 点击「Theme Fonts」（button） | 可能（应用提供撤销，未逐项验证） |
| `effects.activate` | `foxos spreadsheet effects activate` | Page Layout > Effects | — | 点击「Effects」（button） | 可能（应用提供撤销，未逐项验证） |
| `margins.activate` | `foxos spreadsheet margins activate` | Page Layout > Margins | — | 点击「Margins」（button） | 可能（应用提供撤销，未逐项验证） |
| `size.activate` | `foxos spreadsheet size activate` | Page Layout > Size | — | 点击「Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `area.print` | `foxos spreadsheet area print` | Page Layout > Print Area | — | 点击「Print Area」（button） | 不适用（只读） |
| `breaks.activate` | `foxos spreadsheet breaks activate` | Page Layout > Breaks | — | 点击「Breaks」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheet-background.activate` | `foxos spreadsheet sheet-background activate` | Page Layout > Sheet Background | — | 点击「Sheet Background」（button） | 可能（应用提供撤销，未逐项验证） |
| `titles.print` | `foxos spreadsheet titles print` | Page Layout > Print Titles | — | 点击「Print Titles」（button） | 不适用（只读） |
| `page-setup.activate` | `foxos spreadsheet page-setup activate` | Page Layout > Page Setup | — | 点击「Page Setup」（button） | 可能（应用提供撤销，未逐项验证） |
| `pdf.export` | `foxos spreadsheet pdf export` | Page Layout > Export PDF | — | 点击「Export PDF」（button） | 可能（应用提供撤销，未逐项验证） |
| `width.activate` | `foxos spreadsheet width activate` | Page Layout > Width | — | 点击「Width」（button） | 可能（应用提供撤销，未逐项验证） |
| `height.activate` | `foxos spreadsheet height activate` | Page Layout > Height | — | 点击「Height」（button） | 可能（应用提供撤销，未逐项验证） |
| `scale.activate` | `foxos spreadsheet scale activate` | Page Layout > Scale | — | 点击「Scale」（button） | 可能（应用提供撤销，未逐项验证） |
| `gridlines.activate` | `foxos spreadsheet gridlines activate` | Page Layout > Gridlines | — | 点击「Gridlines」（button） | 可能（应用提供撤销，未逐项验证） |
| `gridlines.print` | `foxos spreadsheet gridlines print` | Page Layout > Print Gridlines | — | 点击「Print Gridlines」（button） | 不适用（只读） |
| `headings.activate` | `foxos spreadsheet headings activate` | Page Layout > Headings | — | 点击「Headings」（button） | 可能（应用提供撤销，未逐项验证） |
| `headings.print` | `foxos spreadsheet headings print` | Page Layout > Print Headings | — | 点击「Print Headings」（button） | 不适用（只读） |
| `bring-forward.activate` | `foxos spreadsheet bring-forward activate` | Page Layout > Bring Forward | — | 点击「Bring Forward」（button） | 可能（应用提供撤销，未逐项验证） |
| `bring-forward-options.activate` | `foxos spreadsheet bring-forward-options activate` | Page Layout > Bring Forward options | — | 点击「Bring Forward options」（button） | 可能（应用提供撤销，未逐项验证） |
| `backward.send` | `foxos spreadsheet backward send` | Page Layout > Send Backward | — | 点击「Send Backward」（button） | 可能（应用提供撤销，未逐项验证） |
| `backward-options.send` | `foxos spreadsheet backward-options send` | Page Layout > Send Backward options | — | 点击「Send Backward options」（button） | 可能（应用提供撤销，未逐项验证） |
| `selection-pane.activate` | `foxos spreadsheet selection-pane activate` | Page Layout > Selection Pane | — | 点击「Selection Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `align.align` | `foxos spreadsheet align align` | Page Layout > Align | — | 点击「Align」（button） | 可能（应用提供撤销，未逐项验证） |
| `group.group` | `foxos spreadsheet group group` | Page Layout > Group | — | 点击「Group」（button） | 可能（应用提供撤销，未逐项验证） |
| `rotate.rotate` | `foxos spreadsheet rotate rotate` | Page Layout > Rotate | — | 点击「Rotate」（button） | 可能（应用提供撤销，未逐项验证） |
| `recently-used.activate` | `foxos spreadsheet recently-used activate` | Formulas > Recently Used | — | 点击「Recently Used」（button） | 可能（应用提供撤销，未逐项验证） |
| `financial-functions.activate` | `foxos spreadsheet financial-functions activate` | Formulas > Financial functions | — | 点击「Financial functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `logical-functions.activate` | `foxos spreadsheet logical-functions activate` | Formulas > Logical functions | — | 点击「Logical functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-functions.activate` | `foxos spreadsheet text-functions activate` | Formulas > Text functions | — | 点击「Text functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `date-time-functions.activate` | `foxos spreadsheet date-time-functions activate` | Formulas > Date & Time functions | — | 点击「Date & Time functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `lookup-reference-functions.activate` | `foxos spreadsheet lookup-reference-functions activate` | Formulas > Lookup & Reference functions | — | 点击「Lookup & Reference functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `math-trig-functions.activate` | `foxos spreadsheet math-trig-functions activate` | Formulas > Math & Trig functions | — | 点击「Math & Trig functions」（button） | 可能（应用提供撤销，未逐项验证） |
| `functions.show` | `foxos spreadsheet functions show` | Formulas > More Functions | — | 点击「More Functions」（button），切换到该视图 | 不适用（只读） |
| `name-manager.activate` | `foxos spreadsheet name-manager activate` | Formulas > Name Manager | — | 点击「Name Manager」（button） | 可能（应用提供撤销，未逐项验证） |
| `define-name.activate` | `foxos spreadsheet define-name activate` | Formulas > Define Name | — | 点击「Define Name」（button） | 可能（应用提供撤销，未逐项验证） |
| `use-formula.activate` | `foxos spreadsheet use-formula activate` | Formulas > Use in Formula | — | 点击「Use in Formula」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-selection.create` | `foxos spreadsheet from-selection create` | Formulas > Create from Selection | — | 点击「Create from Selection」（button） | 可能（应用提供撤销，未逐项验证） |
| `trace-precedents.activate` | `foxos spreadsheet trace-precedents activate` | Formulas > Trace Precedents | — | 点击「Trace Precedents」（button） | 可能（应用提供撤销，未逐项验证） |
| `trace-dependents.activate` | `foxos spreadsheet trace-dependents activate` | Formulas > Trace Dependents | — | 点击「Trace Dependents」（button） | 可能（应用提供撤销，未逐项验证） |
| `arrows.delete` | `foxos spreadsheet arrows delete` | Formulas > Remove Arrows | — | 点击「Remove Arrows」（button） | 可能（应用提供撤销，未逐项验证） |
| `formulas-2.show` | `foxos spreadsheet formulas-2 show` | Formulas > Show Formulas | — | 点击「Show Formulas」（button），切换到该视图 | 不适用（只读） |
| `error-checking.activate` | `foxos spreadsheet error-checking activate` | Formulas > Error Checking | — | 点击「Error Checking」（button） | 可能（应用提供撤销，未逐项验证） |
| `error-checking-options.activate` | `foxos spreadsheet error-checking-options activate` | Formulas > Error Checking options | — | 点击「Error Checking options」（button） | 可能（应用提供撤销，未逐项验证） |
| `evaluate-formula.activate` | `foxos spreadsheet evaluate-formula activate` | Formulas > Evaluate Formula | — | 点击「Evaluate Formula」（button） | 可能（应用提供撤销，未逐项验证） |
| `watch-window.activate` | `foxos spreadsheet watch-window activate` | Formulas > Watch Window | — | 点击「Watch Window」（button） | 可能（应用提供撤销，未逐项验证） |
| `calculation-options.activate` | `foxos spreadsheet calculation-options activate` | Formulas > Calculation Options | — | 点击「Calculation Options」（button） | 可能（应用提供撤销，未逐项验证） |
| `now.run` | `foxos spreadsheet now run` | Formulas > Calculate Now | — | 点击「Calculate Now」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheet.run` | `foxos spreadsheet sheet run` | Formulas > Calculate Sheet | — | 点击「Calculate Sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `formulas-values.activate` | `foxos spreadsheet formulas-values activate` | Formulas > Formulas to Values | — | 点击「Formulas to Values」（button） | 可能（应用提供撤销，未逐项验证） |
| `get-data.activate` | `foxos spreadsheet get-data activate` | Data > Get Data | — | 点击「Get Data」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-text-csv.activate` | `foxos spreadsheet from-text-csv activate` | Data > From Text/CSV | — | 点击「From Text/CSV」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-web.activate` | `foxos spreadsheet from-web activate` | Data > From Web | — | 点击「From Web」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-table-range.activate` | `foxos spreadsheet from-table-range activate` | Data > From Table/Range | — | 点击「From Table/Range」（button） | 可能（应用提供撤销，未逐项验证） |
| `refresh.activate` | `foxos spreadsheet refresh activate` | Data > Refresh All | — | 点击「Refresh All」（button） | 可能（应用提供撤销，未逐项验证） |
| `refresh-options.activate` | `foxos spreadsheet refresh-options activate` | Data > Refresh All options | — | 点击「Refresh All options」（button） | 可能（应用提供撤销，未逐项验证） |
| `queries-connections.activate` | `foxos spreadsheet queries-connections activate` | Data > Queries & Connections | — | 点击「Queries & Connections」（button） | 可能（应用提供撤销，未逐项验证） |
| `links.update` | `foxos spreadsheet links update` | Data > Edit Links | — | 点击「Edit Links」（button） | 可能（应用提供撤销，未逐项验证） |
| `z.sort` | `foxos spreadsheet z sort` | Data > Sort A to Z | — | 点击「Sort A to Z」（button） | 不适用（只读） |
| `data-z.sort` | `foxos spreadsheet data-z sort` | Data > Sort Z to A | — | 点击「Sort Z to A」（button） | 不适用（只读） |
| `sort.sort` | `foxos spreadsheet sort sort` | Data > Sort | — | 点击「Sort」（button） | 不适用（只读） |
| `data-filter.filter` | `foxos spreadsheet data-filter filter` | Data > Filter | — | 点击「Filter」（button） | 不适用（只读） |
| `filter.clear` | `foxos spreadsheet filter clear` | Data > Clear filter | — | 点击「Clear filter」（button） | 可能（应用提供撤销，未逐项验证） |
| `reapply.activate` | `foxos spreadsheet reapply activate` | Data > Reapply | — | 点击「Reapply」（button） | 可能（应用提供撤销，未逐项验证） |
| `advanced-filter.activate` | `foxos spreadsheet advanced-filter activate` | Data > Advanced filter | — | 点击「Advanced filter」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-columns.activate` | `foxos spreadsheet text-columns activate` | Data > Text to Columns | — | 点击「Text to Columns」（button） | 可能（应用提供撤销，未逐项验证） |
| `flash-fill.activate` | `foxos spreadsheet flash-fill activate` | Data > Flash Fill | — | 点击「Flash Fill」（button） | 可能（应用提供撤销，未逐项验证） |
| `duplicates.delete` | `foxos spreadsheet duplicates delete` | Data > Remove Duplicates | — | 点击「Remove Duplicates」（button） | 可能（应用提供撤销，未逐项验证） |
| `data-validation.activate` | `foxos spreadsheet data-validation activate` | Data > Data Validation | — | 点击「Data Validation」（button） | 可能（应用提供撤销，未逐项验证） |
| `data-validation-options.activate` | `foxos spreadsheet data-validation-options activate` | Data > Data Validation options | — | 点击「Data Validation options」（button） | 可能（应用提供撤销，未逐项验证） |
| `consolidate.activate` | `foxos spreadsheet consolidate activate` | Data > Consolidate | — | 点击「Consolidate」（button） | 可能（应用提供撤销，未逐项验证） |
| `form.activate` | `foxos spreadsheet form activate` | Data > Form | — | 点击「Form」（button） | 可能（应用提供撤销，未逐项验证） |
| `data-cleanup.activate` | `foxos spreadsheet data-cleanup activate` | Data > Data Cleanup | — | 点击「Data Cleanup」（button） | 可能（应用提供撤销，未逐项验证） |
| `what-if-analysis.activate` | `foxos spreadsheet what-if-analysis activate` | Data > What-If Analysis | — | 点击「What-If Analysis」（button） | 可能（应用提供撤销，未逐项验证） |
| `goal-seek.activate` | `foxos spreadsheet goal-seek activate` | Data > Goal Seek | — | 点击「Goal Seek」（button） | 可能（应用提供撤销，未逐项验证） |
| `forecast-sheet.activate` | `foxos spreadsheet forecast-sheet activate` | Data > Forecast Sheet | — | 点击「Forecast Sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `column-stats.activate` | `foxos spreadsheet column-stats activate` | Data > Column Stats | — | 点击「Column Stats」（button） | 可能（应用提供撤销，未逐项验证） |
| `data-analysis.activate` | `foxos spreadsheet data-analysis activate` | Data > Data Analysis | — | 点击「Data Analysis」（button） | 可能（应用提供撤销，未逐项验证） |
| `solver.activate` | `foxos spreadsheet solver activate` | Data > Solver | — | 点击「Solver」（button） | 可能（应用提供撤销，未逐项验证） |
| `rows.ungroup` | `foxos spreadsheet rows ungroup` | Data > Ungroup Rows | — | 点击「Ungroup Rows」（button） | 可能（应用提供撤销，未逐项验证） |
| `subtotal.activate` | `foxos spreadsheet subtotal activate` | Data > Subtotal | — | 点击「Subtotal」（button） | 可能（应用提供撤销，未逐项验证） |
| `detail.show` | `foxos spreadsheet detail show` | Data > Show Detail | — | 点击「Show Detail」（button），切换到该视图 | 不适用（只读） |
| `detail.hide` | `foxos spreadsheet detail hide` | Data > Hide Detail | — | 点击「Hide Detail」（button） | 不适用（只读） |
| `auto-outline.activate` | `foxos spreadsheet auto-outline activate` | Data > Auto Outline | — | 点击「Auto Outline」（button） | 可能（应用提供撤销，未逐项验证） |
| `outline.clear` | `foxos spreadsheet outline clear` | Data > Clear Outline | — | 点击「Clear Outline」（button） | 可能（应用提供撤销，未逐项验证） |
| `outline-settings.activate` | `foxos spreadsheet outline-settings activate` | Data > Outline Settings | — | 点击「Outline Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `review-spelling.activate` | `foxos spreadsheet review-spelling activate` | Review > Spelling | — | 点击「Spelling」（button） | 可能（应用提供撤销，未逐项验证） |
| `thesaurus.activate` | `foxos spreadsheet thesaurus activate` | Review > Thesaurus | — | 点击「Thesaurus」（button） | 可能（应用提供撤销，未逐项验证） |
| `spelling-as-you-type.activate` | `foxos spreadsheet spelling-as-you-type activate` | Review > Spelling as You Type | — | 点击「Spelling as You Type」（button） | 可能（应用提供撤销，未逐项验证） |
| `autocorrect-options.activate` | `foxos spreadsheet autocorrect-options activate` | Review > AutoCorrect Options | — | 点击「AutoCorrect Options」（button） | 可能（应用提供撤销，未逐项验证） |
| `workbook-statistics.activate` | `foxos spreadsheet workbook-statistics activate` | Review > Workbook Statistics | — | 点击「Workbook Statistics」（button） | 可能（应用提供撤销，未逐项验证） |
| `translate.activate` | `foxos spreadsheet translate activate` | Review > Translate | — | 点击「Translate」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.create` | `foxos spreadsheet comment create` | Review > New Comment | — | 点击「New Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.delete` | `foxos spreadsheet comment delete` | Review > Delete Comment | — | 点击「Delete Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.previous` | `foxos spreadsheet comment previous` | Review > Previous Comment | — | 点击「Previous Comment」（button） | 不适用（只读） |
| `comment.next` | `foxos spreadsheet comment next` | Review > Next Comment | — | 点击「Next Comment」（button） | 不适用（只读） |
| `comments.show` | `foxos spreadsheet comments show` | Review > Show Comments | — | 点击「Show Comments」（button），切换到该视图 | 不适用（只读） |
| `note.delete` | `foxos spreadsheet note delete` | Review > Delete Note | — | 点击「Delete Note」（button） | 可能（应用提供撤销，未逐项验证） |
| `notes-sheet.select` | `foxos spreadsheet notes-sheet select` | Review > Select notes on this sheet | — | 点击「Select notes on this sheet」（button） | 不适用（只读） |
| `changes.show` | `foxos spreadsheet changes show` | Review > Show Changes | — | 点击「Show Changes」（button），切换到该视图 | 不适用（只读） |
| `protect-sheet.activate` | `foxos spreadsheet protect-sheet activate` | Review > Protect Sheet | — | 点击「Protect Sheet」（button） | 可能（应用提供撤销，未逐项验证） |
| `protect-workbook.activate` | `foxos spreadsheet protect-workbook activate` | Review > Protect Workbook | — | 点击「Protect Workbook」（button） | 可能（应用提供撤销，未逐项验证） |
| `protected-ranges.activate` | `foxos spreadsheet protected-ranges activate` | Review > Protected Ranges | — | 点击「Protected Ranges」（button） | 可能（应用提供撤销，未逐项验证） |
| `share.share` | `foxos spreadsheet share share` | Review > Share | — | 点击「Share」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.send` | `foxos spreadsheet copy send` | Review > Send a Copy | — | 点击「Send a Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `version-history.activate` | `foxos spreadsheet version-history activate` | Review > Version History | — | 点击「Version History」（button） | 可能（应用提供撤销，未逐项验证） |
| `normal-view.activate` | `foxos spreadsheet normal-view activate` | View > Normal view | — | 点击「Normal view」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-layout-view.activate` | `foxos spreadsheet page-layout-view activate` | View > Page Layout view | — | 点击「Page Layout view」（button） | 可能（应用提供撤销，未逐项验证） |
| `custom-views.activate` | `foxos spreadsheet custom-views activate` | View > Custom Views | — | 点击「Custom Views」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheet-view.activate` | `foxos spreadsheet sheet-view activate` | View > Sheet View | — | 点击「Sheet View」（button） | 可能（应用提供撤销，未逐项验证） |
| `sheet-view.create` | `foxos spreadsheet sheet-view create` | View > New sheet view | — | 点击「New sheet view」（button） | 可能（应用提供撤销，未逐项验证） |
| `keep-sheet-view.activate` | `foxos spreadsheet keep-sheet-view activate` | View > Keep sheet view | — | 点击「Keep sheet view」（button） | 可能（应用提供撤销，未逐项验证） |
| `exit-sheet-view.activate` | `foxos spreadsheet exit-sheet-view activate` | View > Exit sheet view | — | 点击「Exit sheet view」（button） | 可能（应用提供撤销，未逐项验证） |
| `options-sheet-view.activate` | `foxos spreadsheet options-sheet-view activate` | View > Options sheet view | — | 点击「Options sheet view」（button） | 可能（应用提供撤销，未逐项验证） |
| `formula-bar.activate` | `foxos spreadsheet formula-bar activate` | View > Formula Bar | — | 点击「Formula Bar」（button） | 可能（应用提供撤销，未逐项验证） |
| `zeros.show` | `foxos spreadsheet zeros show` | View > Show Zeros | — | 点击「Show Zeros」（button），切换到该视图 | 不适用（只读） |
| `page-breaks.activate` | `foxos spreadsheet page-breaks activate` | View > Page Breaks | — | 点击「Page Breaks」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom.zoom` | `foxos spreadsheet zoom zoom` | View > Zoom | — | 点击「Zoom」（button） | 不适用（只读） |
| `view-2.zoom-` | `foxos spreadsheet view-2 zoom-` | View > Zoom to Selection | — | 点击「Zoom to Selection」（button） | 可能（应用提供撤销，未逐项验证） |
| `freeze-panes.activate` | `foxos spreadsheet freeze-panes activate` | View > Freeze Panes | — | 点击「Freeze Panes」（button） | 可能（应用提供撤销，未逐项验证） |
| `split.activate` | `foxos spreadsheet split activate` | View > Split | — | 点击「Split」（button） | 可能（应用提供撤销，未逐项验证） |
| `unhide.hide` | `foxos spreadsheet unhide hide` | View > Hide & Unhide | — | 点击「Hide & Unhide」（button） | 不适用（只读） |
| `focus-mode.activate` | `foxos spreadsheet focus-mode activate` | View > Focus Mode | — | 点击「Focus Mode」（button） | 可能（应用提供撤销，未逐项验证） |
| `full-screen.activate` | `foxos spreadsheet full-screen activate` | View > Full Screen | — | 点击「Full Screen」（button） | 可能（应用提供撤销，未逐项验证） |
| `ai-assistant.activate` | `foxos spreadsheet ai-assistant activate` | View > AI Assistant | — | 点击「AI Assistant」（button） | 可能（应用提供撤销，未逐项验证） |
| `actions.record` | `foxos spreadsheet actions record` | Automate > Record Actions | — | 点击「Record Actions」（button） | 可能（应用提供撤销，未逐项验证） |
| `script.create` | `foxos spreadsheet script create` | Automate > New Script | — | 点击「New Script」（button） | 可能（应用提供撤销，未逐项验证） |
| `scripts.activate` | `foxos spreadsheet scripts activate` | Automate > All Scripts | — | 点击「All Scripts」（button） | 可能（应用提供撤销，未逐项验证） |
| `code-editor.activate` | `foxos spreadsheet code-editor activate` | Automate > Code Editor | — | 点击「Code Editor」（button） | 可能（应用提供撤销，未逐项验证） |
| `script.run` | `foxos spreadsheet script run` | Automate > Run a script | — | 点击「Run a script」（button） | 可能（应用提供撤销，未逐项验证） |
| `button-that-runs-script.create` | `foxos spreadsheet button-that-runs-script create` | Automate > Insert a button that runs a script | — | 点击「Insert a button that runs a script」（button） | 可能（应用提供撤销，未逐项验证） |
| `highlight-duplicates-sample-script.run` | `foxos spreadsheet highlight-duplicates-sample-script run` | Automate > Run the Highlight Duplicates sample script | — | 点击「Run the Highlight Duplicates sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `unhide-everything-sample-script.run` | `foxos spreadsheet unhide-everything-sample-script run` | Automate > Run the Unhide Everything sample script | — | 点击「Run the Unhide Everything sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `sum-each-column-sample-script.run` | `foxos spreadsheet sum-each-column-sample-script run` | Automate > Run the Sum Each Column sample script | — | 点击「Run the Sum Each Column sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `table-contents-sample-script.run` | `foxos spreadsheet table-contents-sample-script run` | Automate > Run the Table of Contents sample script | — | 点击「Run the Table of Contents sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `style-header-row-sample-script.run` | `foxos spreadsheet style-header-row-sample-script run` | Automate > Run the Style Header Row sample script | — | 点击「Run the Style Header Row sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `remove-blank-rows-sample-script.run` | `foxos spreadsheet remove-blank-rows-sample-script run` | Automate > Run the Remove Blank Rows sample script | — | 点击「Run the Remove Blank Rows sample script」（button） | 可能（应用提供撤销，未逐项验证） |
| `script-reference.activate` | `foxos spreadsheet script-reference activate` | Automate > Script Reference | — | 点击「Script Reference」（button） | 可能（应用提供撤销，未逐项验证） |
| `paste-options-paste.paste` | `foxos spreadsheet paste-options-paste paste` | Paste options > Paste options > Paste | — | 点击「Paste」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `formulas.activate` | `foxos spreadsheet formulas activate` | Paste options > Paste options > Formulas | — | 点击「Formulas」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `formulas-number-formatting.activate` | `foxos spreadsheet formulas-number-formatting activate` | Paste options > Paste options > Formulas & Number Formatting | — | 点击「Formulas & Number Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keep-source-formatting.activate` | `foxos spreadsheet keep-source-formatting activate` | Paste options > Paste options > Keep Source Formatting | — | 点击「Keep Source Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `no-borders.activate` | `foxos spreadsheet no-borders activate` | Paste options > Paste options > No Borders | — | 点击「No Borders」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keep-source-column-widths.activate` | `foxos spreadsheet keep-source-column-widths activate` | Paste options > Paste options > Keep Source Column Widths | — | 点击「Keep Source Column Widths」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `transpose.activate` | `foxos spreadsheet transpose activate` | Paste options > Paste options > Transpose | — | 点击「Transpose」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `values.activate` | `foxos spreadsheet values activate` | Paste options > Paste options > Values | — | 点击「Values」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `values-number-formatting.activate` | `foxos spreadsheet values-number-formatting activate` | Paste options > Paste options > Values & Number Formatting | — | 点击「Values & Number Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `values-source-formatting.activate` | `foxos spreadsheet values-source-formatting activate` | Paste options > Paste options > Values & Source Formatting | — | 点击「Values & Source Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `formatting.activate` | `foxos spreadsheet formatting activate` | Paste options > Paste options > Formatting | — | 点击「Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `link.paste` | `foxos spreadsheet link paste` | Paste options > Paste options > Paste Link | — | 点击「Paste Link」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `picture.activate` | `foxos spreadsheet picture activate` | Paste options > Paste options > Picture | — | 点击「Picture」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `linked-picture.activate` | `foxos spreadsheet linked-picture activate` | Paste options > Paste options > Linked Picture | — | 点击「Linked Picture」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `special.paste` | `foxos spreadsheet special paste` | Paste options > Paste options > Paste Special… | — | 点击「Paste Special…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `default.activate` | `foxos spreadsheet default activate` | Font: Calibri (Body) > Font > Default | — | 点击「Default」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `arial.activate` | `foxos spreadsheet arial activate` | Font: Calibri (Body) > Font > Arial | — | 点击「Arial」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `arial-black.activate` | `foxos spreadsheet arial-black activate` | Font: Calibri (Body) > Font > Arial Black | — | 点击「Arial Black」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `calibri.activate` | `foxos spreadsheet calibri activate` | Font: Calibri (Body) > Font > Calibri | — | 点击「Calibri」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `cambria.activate` | `foxos spreadsheet cambria activate` | Font: Calibri (Body) > Font > Cambria | — | 点击「Cambria」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `aharoni.activate` | `foxos spreadsheet aharoni activate` | Font: Calibri (Body) > Font > Aharoni | — | 点击「Aharoni」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `avenir-next-lt-pro.activate` | `foxos spreadsheet avenir-next-lt-pro activate` | Font: Calibri (Body) > Font > Avenir Next LT Pro | — | 点击「Avenir Next LT Pro」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `century-gothic.activate` | `foxos spreadsheet century-gothic activate` | Font: Calibri (Body) > Font > Century Gothic | — | 点击「Century Gothic」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `constantia.activate` | `foxos spreadsheet constantia activate` | Font: Calibri (Body) > Font > Constantia | — | 点击「Constantia」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `corbel.activate` | `foxos spreadsheet corbel activate` | Font: Calibri (Body) > Font > Corbel | — | 点击「Corbel」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `helvetica.activate` | `foxos spreadsheet helvetica activate` | Font: Calibri (Body) > Font > Helvetica | — | 点击「Helvetica」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `impact.activate` | `foxos spreadsheet impact activate` | Font: Calibri (Body) > Font > Impact | — | 点击「Impact」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `lato.activate` | `foxos spreadsheet lato activate` | Font: Calibri (Body) > Font > Lato | — | 点击「Lato」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `lato-light.activate` | `foxos spreadsheet lato-light activate` | Font: Calibri (Body) > Font > Lato Light | — | 点击「Lato Light」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `lucida-sans.activate` | `foxos spreadsheet lucida-sans activate` | Font: Calibri (Body) > Font > Lucida Sans | — | 点击「Lucida Sans」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `nyala.activate` | `foxos spreadsheet nyala activate` | Font: Calibri (Body) > Font > Nyala | — | 点击「Nyala」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `sans-semibold.open` | `foxos spreadsheet sans-semibold open` | Font: Calibri (Body) > Font > Open Sans Semibold | — | 点击「Open Sans Semibold」（menuitemradio） | 不适用（只读） |
| `segoe-ui.activate` | `foxos spreadsheet segoe-ui activate` | Font: Calibri (Body) > Font > Segoe UI | — | 点击「Segoe UI」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `source-sans-pro.activate` | `foxos spreadsheet source-sans-pro activate` | Font: Calibri (Body) > Font > Source Sans Pro | — | 点击「Source Sans Pro」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `tahoma.activate` | `foxos spreadsheet tahoma activate` | Font: Calibri (Body) > Font > Tahoma | — | 点击「Tahoma」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `verdana.activate` | `foxos spreadsheet verdana activate` | Font: Calibri (Body) > Font > Verdana | — | 点击「Verdana」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `trebuchet-ms.activate` | `foxos spreadsheet trebuchet-ms activate` | Font: Calibri (Body) > Font > Trebuchet MS | — | 点击「Trebuchet MS」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `georgia.activate` | `foxos spreadsheet georgia activate` | Font: Calibri (Body) > Font > Georgia | — | 点击「Georgia」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `rockwell.activate` | `foxos spreadsheet rockwell activate` | Font: Calibri (Body) > Font > Rockwell | — | 点击「Rockwell」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `times-roman.activate` | `foxos spreadsheet times-roman activate` | Font: Calibri (Body) > Font > Times New Roman | — | 点击「Times New Roman」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `garamond.activate` | `foxos spreadsheet garamond activate` | Font: Calibri (Body) > Font > Garamond | — | 点击「Garamond」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `courier.activate` | `foxos spreadsheet courier activate` | Font: Calibri (Body) > Font > Courier New | — | 点击「Courier New」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `monospace.activate` | `foxos spreadsheet monospace activate` | Font: Calibri (Body) > Font > Monospace | — | 点击「Monospace」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `comic-sans-ms.activate` | `foxos spreadsheet comic-sans-ms activate` | Font: Calibri (Body) > Font > Comic Sans MS | — | 点击「Comic Sans MS」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `document.search` | `foxos spreadsheet document search` | 键盘 mod+f | — | 在当前焦点上按 mod+f（src/ui/code-editor.js 中定义） | 不适用 |
| `selection.group` | `foxos spreadsheet selection group` | 键盘 mod+g | — | 在当前焦点上按 mod+g（src/ui/code-editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `view.toggle-help` | `foxos spreadsheet view toggle-help` | 键盘 mod+h | — | 在当前焦点上按 mod+h（src/ui/code-editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `shortcut.key-q` | `foxos spreadsheet shortcut key-q` | 键盘 mod+q | — | 在当前焦点上按 mod+q（src/ui/quick-analysis.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `document.save` | `foxos spreadsheet document save` | 键盘 mod+s | — | 在当前焦点上按 mod+s（src/ui/code-editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
