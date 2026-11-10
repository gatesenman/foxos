# Documents（documents）操作清单

分组：office · 替代 Microsoft Word, Google Docs, Apple Pages · 许可证 MIT (root LICENSE) · 页面标题「Untitled document — Documents」

共 311 个操作，全部有语义命令（`foxos documents <资源> <动词>`，MCP 工具 `documents.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `search.search` | `foxos documents search search` | 主界面 > search for * | `target`（必填） | 点击名称匹配的「search for *」项（combobox） | 不适用（只读） |
| `editing-mode.select` | `foxos documents editing-mode select` | 主界面 > editing mode: * | `target`（必填） | 点击名称匹配的「editing mode: *」项（button） | 不适用（只读） |
| `account-menu.select` | `foxos documents account-menu select` | 主界面 > account menu for * | `target`（必填） | 点击名称匹配的「account menu for *」项（button） | 不适用（只读） |
| `font-size.select` | `foxos documents font-size select` | 主界面 > # font size | `target`（必填） | 点击名称匹配的「# font size」项（button） | 不适用（只读） |
| `indent.select` | `foxos documents indent select` | 主界面 > # indent | `target`（必填） | 点击名称匹配的「# indent」项（button） | 不适用（只读） |
| `formatting.show` | `foxos documents formatting show` | 主界面 > show formatting # | `target`（必填） | 点击名称匹配的「show formatting #」项（button） | 不适用（只读） |
| `heading.select` | `foxos documents heading select` | 主界面 > Styles > heading # | `target`（必填） | 点击名称匹配的「heading #」项（option） | 不适用（只读） |
| `left.select` | `foxos documents left select` | 主界面 > left # | `target`（必填） | 点击名称匹配的「left #」项（slider） | 不适用（只读） |
| `right.select` | `foxos documents right select` | 主界面 > right # | `target`（必填） | 点击名称匹配的「right #」项（slider） | 不适用（只读） |
| `top.select` | `foxos documents top select` | 主界面 > top # | `target`（必填） | 点击名称匹配的「top #」项（slider） | 不适用（只读） |
| `bottom.select` | `foxos documents bottom select` | 主界面 > bottom # | `target`（必填） | 点击名称匹配的「bottom #」项（slider） | 不适用（只读） |
| `spelling.select` | `foxos documents spelling select` | 主界面 > spelling: * | `target`（必填） | 点击名称匹配的「spelling: *」项（button） | 不适用（只读） |
| `accessibility.select` | `foxos documents accessibility select` | 主界面 > Status bar > accessibility: * | `target`（必填） | 点击名称匹配的「accessibility: *」项（button） | 不适用（只读） |
| `customize-quick-access-toolbar-formatting.show` | `foxos documents customize-quick-access-toolbar-formatting show` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > show formatting # | `target`（必填） | 点击名称匹配的「show formatting #」项（menuitemcheckbox） | 不适用（只读） |
| `pen.select` | `foxos documents pen select` | Draw > pen: * | `target`（必填） | 点击名称匹配的「pen: *」项（button） | 不适用（只读） |
| `pencil.select` | `foxos documents pencil select` | Draw > pencil: * | `target`（必填） | 点击名称匹配的「pencil: *」项（button） | 不适用（只读） |
| `highlighter.select` | `foxos documents highlighter select` | Draw > highlighter: * | `target`（必填） | 点击名称匹配的「highlighter: *」项（button） | 不适用（只读） |
| `check.run` | `foxos documents check run` | Mailings > check for * | `target`（必填） | 点击名称匹配的「check for *」项（button） | 可能（应用提供撤销，未逐项验证） |
| `autosave.toggle` | `foxos documents autosave toggle` | 主界面 > AutoSave | — | 切换「AutoSave」 | 可能（应用提供撤销，未逐项验证） |
| `documents.activate` | `foxos documents documents activate` | 主界面 > All Documents | — | 点击「All Documents」（button） | 可能（应用提供撤销，未逐项验证） |
| `save.save` | `foxos documents save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos documents undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `history.undo` | `foxos documents history undo` | 主界面 > Undo history | — | 点击「Undo history」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos documents redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `print.print` | `foxos documents print print` | 主界面 > Print | — | 点击「Print」（button） | 不适用（只读） |
| `customize-quick-access-toolbar.activate` | `foxos documents customize-quick-access-toolbar activate` | 主界面 > Customize Quick Access Toolbar | — | 点击「Customize Quick Access Toolbar」（button） | 可能（应用提供撤销，未逐项验证） |
| `file.activate` | `foxos documents file activate` | 主界面 > Menu bar > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos documents edit update` | 主界面 > Menu bar > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos documents view show` | 主界面 > Menu bar > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos documents insert create` | 主界面 > Menu bar > Insert | — | 点击「Insert」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `format.activate` | `foxos documents format activate` | 主界面 > Menu bar > Format | — | 点击「Format」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `tools.activate` | `foxos documents tools activate` | 主界面 > Menu bar > Tools | — | 点击「Tools」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `table.activate` | `foxos documents table activate` | 主界面 > Menu bar > Table | — | 点击「Table」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `window.activate` | `foxos documents window activate` | 主界面 > Menu bar > Window | — | 点击「Window」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos documents help show` | 主界面 > Menu bar > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `document-name.set` | `foxos documents document-name set` | 主界面 > Document name | `value`（必填）, `submit` | 把「Document name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `document-details.activate` | `foxos documents document-details activate` | 主界面 > Document details | — | 点击「Document details」（button） | 可能（应用提供撤销，未逐项验证） |
| `not-saved-yet.activate` | `foxos documents not-saved-yet activate` | 主界面 > Not saved yet | — | 点击「Not saved yet」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant.activate` | `foxos documents assistant activate` | 主界面 > Assistant | — | 点击「Assistant」（button） | 可能（应用提供撤销，未逐项验证） |
| `comments.activate` | `foxos documents comments activate` | 主界面 > Comments | — | 点击「Comments」（button） | 可能（应用提供撤销，未逐项验证） |
| `share.share` | `foxos documents share share` | 主界面 > Share | — | 点击「Share」（button） | 可能（应用提供撤销，未逐项验证） |
| `file-2.activate` | `foxos documents file-2 activate` | 主界面 > header > File | — | 点击「File」（button） | 可能（应用提供撤销，未逐项验证） |
| `home.show` | `foxos documents home show` | 主界面 > Ribbon tabs > Home | — | 点击「Home」（tab），切换到该视图 | 不适用（只读） |
| `insert-2.create` | `foxos documents insert-2 create` | 主界面 > Ribbon tabs > Insert | — | 点击「Insert」（tab） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos documents draw draw` | 主界面 > Ribbon tabs > Draw | — | 点击「Draw」（tab） | 可能（应用提供撤销，未逐项验证） |
| `design.show` | `foxos documents design show` | 主界面 > Ribbon tabs > Design | — | 点击「Design」（tab），切换到该视图 | 不适用（只读） |
| `layout.show` | `foxos documents layout show` | 主界面 > Ribbon tabs > Layout | — | 点击「Layout」（tab），切换到该视图 | 不适用（只读） |
| `references.show` | `foxos documents references show` | 主界面 > Ribbon tabs > References | — | 点击「References」（tab），切换到该视图 | 不适用（只读） |
| `mailings.show` | `foxos documents mailings show` | 主界面 > Ribbon tabs > Mailings | — | 点击「Mailings」（tab），切换到该视图 | 不适用（只读） |
| `review.show` | `foxos documents review show` | 主界面 > Ribbon tabs > Review | — | 点击「Review」（tab），切换到该视图 | 不适用（只读） |
| `view-2.show` | `foxos documents view-2 show` | 主界面 > Ribbon tabs > View | — | 点击「View」（tab），切换到该视图 | 不适用（只读） |
| `ribbon-display-options.activate` | `foxos documents ribbon-display-options activate` | 主界面 > Ribbon display options | — | 点击「Ribbon display options」（button） | 可能（应用提供撤销，未逐项验证） |
| `ribbon.collapse` | `foxos documents ribbon collapse` | 主界面 > Collapse the ribbon | — | 点击「Collapse the ribbon」（button） | 不适用（只读） |
| `paste.paste` | `foxos documents paste paste` | 主界面 > Paste | — | 点击「Paste」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.paste` | `foxos documents options paste` | 主界面 > Paste options | — | 点击「Paste options」（button） | 可能（应用提供撤销，未逐项验证） |
| `cut.cut` | `foxos documents cut cut` | 主界面 > Cut | — | 点击「Cut」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.copy` | `foxos documents copy copy` | 主界面 > Copy | — | 点击「Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-painter.activate` | `foxos documents format-painter activate` | 主界面 > Format Painter | — | 点击「Format Painter」（button） | 可能（应用提供撤销，未逐项验证） |
| `latin-font-family.activate` | `foxos documents latin-font-family activate` | 主界面 > Latin font family | — | 点击「Latin font family」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-size-pt.set` | `foxos documents font-size-pt set` | 主界面 > Font size (pt) | `value`（必填）, `submit` | 把「Font size (pt)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `font-sizes.activate` | `foxos documents font-sizes activate` | 主界面 > Font sizes | — | 点击「Font sizes」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-font-size.activate` | `foxos documents increase-font-size activate` | 主界面 > Increase Font Size | — | 点击「Increase Font Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `case.update` | `foxos documents case update` | 主界面 > Change Case | — | 点击「Change Case」（button） | 可能（应用提供撤销，未逐项验证） |
| `formatting.clear` | `foxos documents formatting clear` | 主界面 > Clear All Formatting | — | 点击「Clear All Formatting」（button） | 可能（应用提供撤销，未逐项验证） |
| `bold.format` | `foxos documents bold format` | 主界面 > Bold | — | 点击「Bold」（button） | 可能（应用提供撤销，未逐项验证） |
| `italic.format` | `foxos documents italic format` | 主界面 > Italic | — | 点击「Italic」（button） | 可能（应用提供撤销，未逐项验证） |
| `underline.format` | `foxos documents underline format` | 主界面 > Underline | — | 点击「Underline」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.format` | `foxos documents options format` | 主界面 > Underline options | — | 点击「Underline options」（button） | 可能（应用提供撤销，未逐项验证） |
| `strikethrough.format` | `foxos documents strikethrough format` | 主界面 > Strikethrough | — | 点击「Strikethrough」（button） | 可能（应用提供撤销，未逐项验证） |
| `subscript.activate` | `foxos documents subscript activate` | 主界面 > Subscript | — | 点击「Subscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `superscript.activate` | `foxos documents superscript activate` | 主界面 > Superscript | — | 点击「Superscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-effects.activate` | `foxos documents text-effects activate` | 主界面 > Text Effects | — | 点击「Text Effects」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-highlight.activate` | `foxos documents text-highlight activate` | 主界面 > Text highlight | — | 点击「Text highlight」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-color.activate` | `foxos documents text-color activate` | 主界面 > Text color | — | 点击「Text color」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-settings.activate` | `foxos documents font-settings activate` | 主界面 > Font Settings | — | 点击「Font Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `bulleted-list.activate` | `foxos documents bulleted-list activate` | 主界面 > Bulleted list | — | 点击「Bulleted list」（button） | 可能（应用提供撤销，未逐项验证） |
| `bullet-library.activate` | `foxos documents bullet-library activate` | 主界面 > Bullet Library | — | 点击「Bullet Library」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbered-list.activate` | `foxos documents numbered-list activate` | 主界面 > Numbered list | — | 点击「Numbered list」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbering-library.activate` | `foxos documents numbering-library activate` | 主界面 > Numbering Library | — | 点击「Numbering Library」（button） | 可能（应用提供撤销，未逐项验证） |
| `multilevel-list.activate` | `foxos documents multilevel-list activate` | 主界面 > Multilevel List | — | 点击「Multilevel List」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-indent.activate` | `foxos documents increase-indent activate` | 主界面 > Increase Indent | — | 点击「Increase Indent」（button） | 可能（应用提供撤销，未逐项验证） |
| `sort.sort` | `foxos documents sort sort` | 主界面 > Sort | — | 点击「Sort」（button） | 不适用（只读） |
| `left.align` | `foxos documents left align` | 主界面 > Align left | — | 点击「Align left」（button） | 可能（应用提供撤销，未逐项验证） |
| `center.align` | `foxos documents center align` | 主界面 > Align center | — | 点击「Align center」（button） | 可能（应用提供撤销，未逐项验证） |
| `right.align` | `foxos documents right align` | 主界面 > Align right | — | 点击「Align right」（button） | 可能（应用提供撤销，未逐项验证） |
| `justify.activate` | `foxos documents justify activate` | 主界面 > Justify | — | 点击「Justify」（button） | 可能（应用提供撤销，未逐项验证） |
| `line-paragraph-spacing.activate` | `foxos documents line-paragraph-spacing activate` | 主界面 > Line and Paragraph Spacing | — | 点击「Line and Paragraph Spacing」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-shading.activate` | `foxos documents paragraph-shading activate` | 主界面 > Paragraph shading | — | 点击「Paragraph shading」（button） | 可能（应用提供撤销，未逐项验证） |
| `borders.activate` | `foxos documents borders activate` | 主界面 > Borders | — | 点击「Borders」（button） | 可能（应用提供撤销，未逐项验证） |
| `border-options.activate` | `foxos documents border-options activate` | 主界面 > Border options | — | 点击「Border options」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-settings.activate` | `foxos documents paragraph-settings activate` | 主界面 > Paragraph Settings | — | 点击「Paragraph Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `normal.activate` | `foxos documents normal activate` | 主界面 > Styles > Normal | — | 点击「Normal」（option） | 可能（应用提供撤销，未逐项验证） |
| `title.activate` | `foxos documents title activate` | 主界面 > Styles > Title | — | 点击「Title」（option） | 可能（应用提供撤销，未逐项验证） |
| `subtitle.activate` | `foxos documents subtitle activate` | 主界面 > Styles > Subtitle | — | 点击「Subtitle」（option） | 可能（应用提供撤销，未逐项验证） |
| `styles.show` | `foxos documents styles show` | 主界面 > More Styles | — | 点击「More Styles」（button），切换到该视图 | 不适用（只读） |
| `styles-pane.activate` | `foxos documents styles-pane activate` | 主界面 > Styles Pane | — | 点击「Styles Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `formatting-pane.activate` | `foxos documents formatting-pane activate` | 主界面 > Formatting Pane | — | 点击「Formatting Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `dictate.activate` | `foxos documents dictate activate` | 主界面 > Dictate | — | 点击「Dictate」（button） | 可能（应用提供撤销，未逐项验证） |
| `find.search` | `foxos documents find search` | 主界面 > Find | — | 点击「Find」（button） | 不适用（只读） |
| `options.search` | `foxos documents options search` | 主界面 > Find options | — | 点击「Find options」（button） | 不适用（只读） |
| `replace.activate` | `foxos documents replace activate` | 主界面 > Replace | — | 点击「Replace」（button） | 可能（应用提供撤销，未逐项验证） |
| `select.select` | `foxos documents select select` | 主界面 > Select | — | 点击「Select」（button） | 不适用（只读） |
| `left-indent.set` | `foxos documents left-indent set` | 主界面 > Left indent | `value`（必填）, `submit` | 把「Left indent」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `hanging-indent.set` | `foxos documents hanging-indent set` | 主界面 > Hanging indent | `value`（必填）, `submit` | 把「Hanging indent」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `first-line-indent.set` | `foxos documents first-line-indent set` | 主界面 > First line indent | `value`（必填）, `submit` | 把「First line indent」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `right-indent.set` | `foxos documents right-indent set` | 主界面 > Right indent | `value`（必填）, `submit` | 把「Right indent」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `document-text.set` | `foxos documents document-text set` | 主界面 > Document text | `value`（必填）, `submit` | 把「Document text」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `go-ctrlg.activate` | `foxos documents go-ctrlg activate` | 主界面 > Status bar > Go To (Ctrl+G) | — | 点击「Go To (Ctrl+G)」（button） | 可能（应用提供撤销，未逐项验证） |
| `word-count.activate` | `foxos documents word-count activate` | 主界面 > Status bar > Word Count | — | 点击「Word Count」（button） | 可能（应用提供撤销，未逐项验证） |
| `language.activate` | `foxos documents language activate` | 主界面 > Status bar > Language | — | 点击「Language」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-mode.toggle` | `foxos documents text-mode toggle` | 主界面 > Status bar > Text mode | — | 切换「Text mode」 | 可能（应用提供撤销，未逐项验证） |
| `focus.activate` | `foxos documents focus activate` | 主界面 > Focus | — | 点击「Focus」（button） | 可能（应用提供撤销，未逐项验证） |
| `read-mode.activate` | `foxos documents read-mode activate` | 主界面 > Read Mode | — | 点击「Read Mode」（button） | 可能（应用提供撤销，未逐项验证） |
| `layout.print` | `foxos documents layout print` | 主界面 > Print Layout | — | 点击「Print Layout」（button） | 不适用（只读） |
| `web-layout.activate` | `foxos documents web-layout activate` | 主界面 > Web Layout | — | 点击「Web Layout」（button） | 可能（应用提供撤销，未逐项验证） |
| `outline.activate` | `foxos documents outline activate` | 主界面 > Outline | — | 点击「Outline」（button） | 可能（应用提供撤销，未逐项验证） |
| `draft.activate` | `foxos documents draft activate` | 主界面 > Draft | — | 点击「Draft」（button） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-out` | `foxos documents view zoom-out` | 主界面 > Zoom Out | — | 点击「Zoom Out」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom-slider.set` | `foxos documents zoom-slider set` | 主界面 > Zoom slider | `value`（必填）, `submit` | 把「Zoom slider」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-` | `foxos documents view zoom-` | 主界面 > Zoom In | — | 点击「Zoom In」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom.set` | `foxos documents zoom set` | 主界面 > Zoom | `value`（必填）, `submit` | 把「Zoom」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-documents.activate` | `foxos documents customize-quick-access-toolbar-documents activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > All Documents | — | 点击「All Documents」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-save.save` | `foxos documents customize-quick-access-toolbar-save save` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Save | — | 点击「Save」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-undo.undo` | `foxos documents customize-quick-access-toolbar-undo undo` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Undo | — | 点击「Undo」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-redo.redo` | `foxos documents customize-quick-access-toolbar-redo redo` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Redo | — | 点击「Redo」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-print.print` | `foxos documents customize-quick-access-toolbar-print print` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Print | — | 点击「Print」（menuitemcheckbox） | 不适用（只读） |
| `document.create` | `foxos documents document create` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > New Document | — | 点击「New Document」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `open.open` | `foxos documents open open` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Open | — | 点击「Open」（menuitemcheckbox） | 不适用（只读） |
| `customize-quick-access-toolbar-find.search` | `foxos documents customize-quick-access-toolbar-find search` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Find | — | 点击「Find」（menuitemcheckbox） | 不适用（只读） |
| `spelling.activate` | `foxos documents spelling activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Spelling | — | 点击「Spelling」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `as-pdf.save` | `foxos documents as-pdf save` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Save as PDF | — | 点击「Save as PDF」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `comment.create` | `foxos documents comment create` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > New Comment | — | 点击「New Comment」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `track-changes.activate` | `foxos documents track-changes activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Track Changes | — | 点击「Track Changes」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `customize-quick-access-toolbar-word-count.activate` | `foxos documents customize-quick-access-toolbar-word-count activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Word Count | — | 点击「Word Count」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `read-aloud.activate` | `foxos documents read-aloud activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Read Aloud | — | 点击「Read Aloud」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `repeat.activate` | `foxos documents repeat activate` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Repeat | — | 点击「Repeat」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `defaults.reset` | `foxos documents defaults reset` | Customize Quick Access Toolbar > Customize Quick Access Toolbar > Reset to Defaults | — | 点击「Reset to Defaults」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `document.close` | `foxos documents document close` | Document details > Close document | — | 点击「Close document」（button） | 不适用（只读） |
| `file-name.set` | `foxos documents file-name set` | Document details > File name | `value`（必填）, `submit` | 把「File name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `version-history.activate` | `foxos documents version-history activate` | Document details > Document > Version History | — | 点击「Version History」（button） | 可能（应用提供撤销，未逐项验证） |
| `properties.activate` | `foxos documents properties activate` | Document details > Document > Properties | — | 点击「Properties」（button） | 可能（应用提供撤销，未逐项验证） |
| `rename.rename` | `foxos documents rename rename` | Document details > Document > Rename | — | 点击「Rename」（button） | 可能（应用提供撤销，未逐项验证） |
| `editingedit-document-directly.activate` | `foxos documents editingedit-document-directly activate` | Editing mode: Editing > Editing mode > EditingEdit the document directly. | — | 点击「EditingEdit the document directly.」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `reviewingedits-become-tracked-changes.activate` | `foxos documents reviewingedits-become-tracked-changes activate` | Editing mode: Editing > Editing mode > ReviewingEdits become tracked changes. | — | 点击「ReviewingEdits become tracked changes.」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `people.invite` | `foxos documents people invite` | Share > Share > Invite People… | — | 点击「Invite People…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `link.copy` | `foxos documents link copy` | Share > Share > Copy Link | — | 点击「Copy Link」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `publish-web.activate` | `foxos documents publish-web activate` | Share > Share > Publish to the Web… | — | 点击「Publish to the Web…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `copy-docx.send` | `foxos documents copy-docx send` | Share > Share > Send a Copy (.docx) | — | 点击「Send a Copy (.docx)」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `as-pdf.send` | `foxos documents as-pdf send` | Share > Share > Send as PDF | — | 点击「Send as PDF」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `system.toggle` | `foxos documents system toggle` | Account menu for local > Appearance > System | — | 切换「System」 | 可能（应用提供撤销，未逐项验证） |
| `light.toggle` | `foxos documents light toggle` | Account menu for local > Appearance > Light | — | 切换「Light」 | 可能（应用提供撤销，未逐项验证） |
| `dark.toggle` | `foxos documents dark toggle` | Account menu for local > Appearance > Dark | — | 切换「Dark」 | 可能（应用提供撤销，未逐项验证） |
| `dark-pagedark-paper-dark-theme.activate` | `foxos documents dark-pagedark-paper-dark-theme activate` | Account menu for local > Account > Dark pageDark paper with the dark theme | — | 点击「Dark pageDark paper with the dark theme」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `measurement-unitsinches.activate` | `foxos documents measurement-unitsinches activate` | Account menu for local > Account > Measurement unitsInches | — | 点击「Measurement unitsInches」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `capitalize-first-letter-sentences.activate` | `foxos documents capitalize-first-letter-sentences activate` | Account menu for local > Account > Capitalize the first letter of sentences | — | 点击「Capitalize the first letter of sentences」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcuts.activate` | `foxos documents keyboard-shortcuts activate` | Account menu for local > Account > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `documents.show` | `foxos documents documents show` | Account menu for local > Account > About Documents | — | 点击「About Documents」（menuitem），切换到该视图 | 不适用（只读） |
| `document.previous` | `foxos documents document previous` | File > Back to the document | — | 点击「Back to the document」（button） | 不适用（只读） |
| `file-open.open` | `foxos documents file-open open` | File > File > Open | — | 点击「Open」（tab） | 不适用（只读） |
| `info.show` | `foxos documents info show` | File > File > Info | — | 点击「Info」（tab），切换到该视图 | 不适用（只读） |
| `file-save.save` | `foxos documents file-save save` | File > File > Save | — | 点击「Save」（tab） | 可能（应用提供撤销，未逐项验证） |
| `file-print.print` | `foxos documents file-print print` | File > File > Print | — | 点击「Print」（tab） | 不适用（只读） |
| `file-share.share` | `foxos documents file-share share` | File > File > Share | — | 点击「Share」（tab） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos documents export export` | File > File > Export | — | 点击「Export」（tab） | 可能（应用提供撤销，未逐项验证） |
| `close.close` | `foxos documents close close` | File > aside > Close | — | 点击「Close」（button） | 不适用（只读） |
| `preferences.activate` | `foxos documents preferences activate` | File > aside > Preferences | — | 点击「Preferences」（button） | 可能（应用提供撤销，未逐项验证） |
| `title.set` | `foxos documents title set` | File > Title | `value`（必填）, `submit` | 把「Title」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `subject.set` | `foxos documents subject set` | File > Subject | `value`（必填）, `submit` | 把「Subject」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `author.set` | `foxos documents author set` | File > Author | `value`（必填）, `submit` | 把「Author」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `keywords.set` | `foxos documents keywords set` | File > Keywords | `value`（必填）, `submit` | 把「Keywords」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `category.set` | `foxos documents category set` | File > Category | `value`（必填）, `submit` | 把「Category」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `status.set` | `foxos documents status set` | File > Status | `value`（必填）, `submit` | 把「Status」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `comments.set` | `foxos documents comments set` | File > Comments | `value`（必填）, `submit` | 把「Comments」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `properties.save` | `foxos documents properties save` | File > main > Save Properties | — | 点击「Save Properties」（button） | 可能（应用提供撤销，未逐项验证） |
| `only.show` | `foxos documents only show` | File > main > View Only | — | 点击「View Only」（button），切换到该视图 | 不适用（只读） |
| `cover-page.activate` | `foxos documents cover-page activate` | Insert > Cover Page | — | 点击「Cover Page」（button） | 可能（应用提供撤销，未逐项验证） |
| `blank-page.activate` | `foxos documents blank-page activate` | Insert > Blank Page | — | 点击「Blank Page」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-break.activate` | `foxos documents page-break activate` | Insert > Page break | — | 点击「Page break」（button） | 可能（应用提供撤销，未逐项验证） |
| `table.create` | `foxos documents table create` | Insert > Insert table | — | 点击「Insert table」（button） | 可能（应用提供撤销，未逐项验证） |
| `pictures.activate` | `foxos documents pictures activate` | Insert > Pictures | — | 点击「Pictures」（button） | 可能（应用提供撤销，未逐项验证） |
| `shapes.activate` | `foxos documents shapes activate` | Insert > Shapes | — | 点击「Shapes」（button） | 可能（应用提供撤销，未逐项验证） |
| `icons.activate` | `foxos documents icons activate` | Insert > Icons | — | 点击「Icons」（button） | 可能（应用提供撤销，未逐项验证） |
| `diagram.activate` | `foxos documents diagram activate` | Insert > Diagram | — | 点击「Diagram」（button） | 可能（应用提供撤销，未逐项验证） |
| `chart.activate` | `foxos documents chart activate` | Insert > Chart | — | 点击「Chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `or-edit-link.create` | `foxos documents or-edit-link create` | Insert > Insert or edit link | — | 点击「Insert or edit link」（button） | 可能（应用提供撤销，未逐项验证） |
| `bookmarks.activate` | `foxos documents bookmarks activate` | Insert > Bookmarks | — | 点击「Bookmarks」（button） | 可能（应用提供撤销，未逐项验证） |
| `insert-comment.create` | `foxos documents insert-comment create` | Insert > New Comment | — | 点击「New Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `header.activate` | `foxos documents header activate` | Insert > Header | — | 点击「Header」（button） | 可能（应用提供撤销，未逐项验证） |
| `footer.activate` | `foxos documents footer activate` | Insert > Footer | — | 点击「Footer」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-number.activate` | `foxos documents page-number activate` | Insert > Page Number | — | 点击「Page Number」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-box.activate` | `foxos documents text-box activate` | Insert > Text Box | — | 点击「Text Box」（button） | 可能（应用提供撤销，未逐项验证） |
| `quick-parts.activate` | `foxos documents quick-parts activate` | Insert > Quick Parts | — | 点击「Quick Parts」（button） | 可能（应用提供撤销，未逐项验证） |
| `wordart.activate` | `foxos documents wordart activate` | Insert > WordArt | — | 点击「WordArt」（button） | 可能（应用提供撤销，未逐项验证） |
| `drop-cap.activate` | `foxos documents drop-cap activate` | Insert > Drop Cap | — | 点击「Drop Cap」（button） | 可能（应用提供撤销，未逐项验证） |
| `signature-line.activate` | `foxos documents signature-line activate` | Insert > Signature Line | — | 点击「Signature Line」（button） | 可能（应用提供撤销，未逐项验证） |
| `date-time.activate` | `foxos documents date-time activate` | Insert > Date & Time | — | 点击「Date & Time」（button） | 可能（应用提供撤销，未逐项验证） |
| `object.activate` | `foxos documents object activate` | Insert > Object | — | 点击「Object」（button） | 可能（应用提供撤销，未逐项验证） |
| `symbols.activate` | `foxos documents symbols activate` | Insert > Symbols | — | 点击「Symbols」（button） | 可能（应用提供撤销，未逐项验证） |
| `lasso-select.activate` | `foxos documents lasso-select activate` | Draw > Lasso Select | — | 点击「Lasso Select」（button） | 可能（应用提供撤销，未逐项验证） |
| `eraser.activate` | `foxos documents eraser activate` | Draw > Eraser | — | 点击「Eraser」（button） | 可能（应用提供撤销，未逐项验证） |
| `eraser-options.activate` | `foxos documents eraser-options activate` | Draw > Eraser options | — | 点击「Eraser options」（button） | 可能（应用提供撤销，未逐项验证） |
| `pen.create` | `foxos documents pen create` | Draw > Add Pen | — | 点击「Add Pen」（button） | 可能（应用提供撤销，未逐项验证） |
| `touch.draw` | `foxos documents touch draw` | Draw > Draw with Touch | — | 点击「Draw with Touch」（button） | 可能（应用提供撤销，未逐项验证） |
| `ruler.activate` | `foxos documents ruler activate` | Draw > Ruler | — | 点击「Ruler」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-shape.activate` | `foxos documents ink-shape activate` | Draw > Ink to Shape | — | 点击「Ink to Shape」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-math.activate` | `foxos documents ink-math activate` | Draw > Ink to Math | — | 点击「Ink to Math」（button） | 可能（应用提供撤销，未逐项验证） |
| `drawing-canvas.activate` | `foxos documents drawing-canvas activate` | Draw > Drawing Canvas | — | 点击「Drawing Canvas」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-replay.activate` | `foxos documents ink-replay activate` | Draw > Ink Replay | — | 点击「Ink Replay」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink.hide` | `foxos documents ink hide` | Draw > Hide Ink | — | 点击「Hide Ink」（button） | 不适用（只读） |
| `themes.activate` | `foxos documents themes activate` | Design > Themes | — | 点击「Themes」（button） | 可能（应用提供撤销，未逐项验证） |
| `default-style-set.activate` | `foxos documents default-style-set activate` | Design > Default style set | — | 点击「Default style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `crisp-style-set.activate` | `foxos documents crisp-style-set activate` | Design > Crisp style set | — | 点击「Crisp style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `classic-style-set.activate` | `foxos documents classic-style-set activate` | Design > Classic style set | — | 点击「Classic style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `banner-style-set.activate` | `foxos documents banner-style-set activate` | Design > Banner style set | — | 点击「Banner style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `minimal-style-set.activate` | `foxos documents minimal-style-set activate` | Design > Minimal style set | — | 点击「Minimal style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `accent-bar-style-set.activate` | `foxos documents accent-bar-style-set activate` | Design > Accent Bar style set | — | 点击「Accent Bar style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `centered-style-set.activate` | `foxos documents centered-style-set activate` | Design > Centered style set | — | 点击「Centered style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `contrast-style-set.format` | `foxos documents contrast-style-set format` | Design > Bold Contrast style set | — | 点击「Bold Contrast style set」（option） | 可能（应用提供撤销，未逐项验证） |
| `style-sets.show` | `foxos documents style-sets show` | Design > More Style Sets | — | 点击「More Style Sets」（button），切换到该视图 | 不适用（只读） |
| `theme-colors.activate` | `foxos documents theme-colors activate` | Design > Theme Colors | — | 点击「Theme Colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `theme-fonts.activate` | `foxos documents theme-fonts activate` | Design > Theme Fonts | — | 点击「Theme Fonts」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-spacing.activate` | `foxos documents paragraph-spacing activate` | Design > Paragraph Spacing | — | 点击「Paragraph Spacing」（button） | 可能（应用提供撤销，未逐项验证） |
| `theme-effects.activate` | `foxos documents theme-effects activate` | Design > Theme Effects | — | 点击「Theme Effects」（button） | 可能（应用提供撤销，未逐项验证） |
| `set-as-default.activate` | `foxos documents set-as-default activate` | Design > Set as Default | — | 点击「Set as Default」（button） | 可能（应用提供撤销，未逐项验证） |
| `watermark.activate` | `foxos documents watermark activate` | Design > Watermark | — | 点击「Watermark」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-color.activate` | `foxos documents page-color activate` | Design > Page Color | — | 点击「Page Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-borders.activate` | `foxos documents page-borders activate` | Design > Page Borders | — | 点击「Page Borders」（button） | 可能（应用提供撤销，未逐项验证） |
| `margins.activate` | `foxos documents margins activate` | Layout > Margins | — | 点击「Margins」（button） | 可能（应用提供撤销，未逐项验证） |
| `orientation.activate` | `foxos documents orientation activate` | Layout > Orientation | — | 点击「Orientation」（button） | 可能（应用提供撤销，未逐项验证） |
| `size.activate` | `foxos documents size activate` | Layout > Size | — | 点击「Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `columns.activate` | `foxos documents columns activate` | Layout > Columns | — | 点击「Columns」（button） | 可能（应用提供撤销，未逐项验证） |
| `breaks.activate` | `foxos documents breaks activate` | Layout > Breaks | — | 点击「Breaks」（button） | 可能（应用提供撤销，未逐项验证） |
| `line-numbers.activate` | `foxos documents line-numbers activate` | Layout > Line Numbers | — | 点击「Line Numbers」（button） | 可能（应用提供撤销，未逐项验证） |
| `hyphenation.activate` | `foxos documents hyphenation activate` | Layout > Hyphenation | — | 点击「Hyphenation」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-setup.activate` | `foxos documents page-setup activate` | Layout > Page setup | — | 点击「Page setup」（button） | 可能（应用提供撤销，未逐项验证） |
| `indent-left.set` | `foxos documents indent-left set` | Layout > Indent left (in) | `value`（必填）, `submit` | 把「Indent left (in)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `indent-right.set` | `foxos documents indent-right set` | Layout > Indent right (in) | `value`（必填）, `submit` | 把「Indent right (in)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `space-before-paragraph-pt.set` | `foxos documents space-before-paragraph-pt set` | Layout > Space before paragraph (pt) | `value`（必填）, `submit` | 把「Space before paragraph (pt)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `space-after-paragraph-pt.set` | `foxos documents space-after-paragraph-pt set` | Layout > Space after paragraph (pt) | `value`（必填）, `submit` | 把「Space after paragraph (pt)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `position.activate` | `foxos documents position activate` | Layout > Position | — | 点击「Position」（button） | 可能（应用提供撤销，未逐项验证） |
| `wrap-text.activate` | `foxos documents wrap-text activate` | Layout > Wrap Text | — | 点击「Wrap Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `bring-forward.activate` | `foxos documents bring-forward activate` | Layout > Bring Forward | — | 点击「Bring Forward」（button） | 可能（应用提供撤销，未逐项验证） |
| `bring-forward-options.activate` | `foxos documents bring-forward-options activate` | Layout > Bring Forward options | — | 点击「Bring Forward options」（button） | 可能（应用提供撤销，未逐项验证） |
| `backward.send` | `foxos documents backward send` | Layout > Send Backward | — | 点击「Send Backward」（button） | 可能（应用提供撤销，未逐项验证） |
| `backward-options.send` | `foxos documents backward-options send` | Layout > Send Backward options | — | 点击「Send Backward options」（button） | 可能（应用提供撤销，未逐项验证） |
| `selection-pane.activate` | `foxos documents selection-pane activate` | Layout > Selection Pane | — | 点击「Selection Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `align.align` | `foxos documents align align` | Layout > Align | — | 点击「Align」（button） | 可能（应用提供撤销，未逐项验证） |
| `group.group` | `foxos documents group group` | Layout > Group | — | 点击「Group」（button） | 可能（应用提供撤销，未逐项验证） |
| `rotate.rotate` | `foxos documents rotate rotate` | Layout > Rotate | — | 点击「Rotate」（button） | 可能（应用提供撤销，未逐项验证） |
| `table-contents.activate` | `foxos documents table-contents activate` | References > Table of Contents | — | 点击「Table of Contents」（button） | 可能（应用提供撤销，未逐项验证） |
| `text.create` | `foxos documents text create` | References > Add Text | — | 点击「Add Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `table.update` | `foxos documents table update` | References > Update Table | — | 点击「Update Table」（button） | 可能（应用提供撤销，未逐项验证） |
| `fields.update` | `foxos documents fields update` | References > Update Fields | — | 点击「Update Fields」（button） | 可能（应用提供撤销，未逐项验证） |
| `footnote.create` | `foxos documents footnote create` | References > Insert Footnote | — | 点击「Insert Footnote」（button） | 可能（应用提供撤销，未逐项验证） |
| `endnote.create` | `foxos documents endnote create` | References > Insert Endnote | — | 点击「Insert Endnote」（button） | 可能（应用提供撤销，未逐项验证） |
| `footnote.next` | `foxos documents footnote next` | References > Next Footnote | — | 点击「Next Footnote」（button） | 不适用（只读） |
| `notes.show` | `foxos documents notes show` | References > Show Notes | — | 点击「Show Notes」（button），切换到该视图 | 不适用（只读） |
| `footnote-endnote-settings.activate` | `foxos documents footnote-endnote-settings activate` | References > Footnote and Endnote Settings | — | 点击「Footnote and Endnote Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `smart-lookup.activate` | `foxos documents smart-lookup activate` | References > Smart Lookup | — | 点击「Smart Lookup」（button） | 可能（应用提供撤销，未逐项验证） |
| `citation.create` | `foxos documents citation create` | References > Insert Citation | — | 点击「Insert Citation」（button） | 可能（应用提供撤销，未逐项验证） |
| `manage-sources.activate` | `foxos documents manage-sources activate` | References > Manage Sources | — | 点击「Manage Sources」（button） | 可能（应用提供撤销，未逐项验证） |
| `citation-style.set` | `foxos documents citation-style set` | References > Citation style | `value`（必填）, `submit` | 把「Citation style」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `bibliography.activate` | `foxos documents bibliography activate` | References > Bibliography | — | 点击「Bibliography」（button） | 可能（应用提供撤销，未逐项验证） |
| `caption.create` | `foxos documents caption create` | References > Insert Caption | — | 点击「Insert Caption」（button） | 可能（应用提供撤销，未逐项验证） |
| `table-figures.create` | `foxos documents table-figures create` | References > Insert Table of Figures | — | 点击「Insert Table of Figures」（button） | 可能（应用提供撤销，未逐项验证） |
| `table-figures.update` | `foxos documents table-figures update` | References > Update Table of Figures | — | 点击「Update Table of Figures」（button） | 可能（应用提供撤销，未逐项验证） |
| `cross-reference.activate` | `foxos documents cross-reference activate` | References > Cross-reference | — | 点击「Cross-reference」（button） | 可能（应用提供撤销，未逐项验证） |
| `index.activate` | `foxos documents index activate` | References > Index | — | 点击「Index」（button） | 可能（应用提供撤销，未逐项验证） |
| `table-authorities.activate` | `foxos documents table-authorities activate` | References > Table of Authorities | — | 点击「Table of Authorities」（button） | 可能（应用提供撤销，未逐项验证） |
| `create.create` | `foxos documents create create` | Mailings > Create | — | 点击「Create」（button） | 可能（应用提供撤销，未逐项验证） |
| `mail-merge.start` | `foxos documents mail-merge start` | Mailings > Start Mail Merge | — | 点击「Start Mail Merge」（button） | 可能（应用提供撤销，未逐项验证） |
| `recipients.select` | `foxos documents recipients select` | Mailings > Select Recipients | — | 点击「Select Recipients」（button） | 不适用（只读） |
| `recipient-list.update` | `foxos documents recipient-list update` | Mailings > Edit Recipient List | — | 点击「Edit Recipient List」（button） | 可能（应用提供撤销，未逐项验证） |
| `highlight-merge-fields.activate` | `foxos documents highlight-merge-fields activate` | Mailings > Highlight Merge Fields | — | 点击「Highlight Merge Fields」（button） | 可能（应用提供撤销，未逐项验证） |
| `address-block.activate` | `foxos documents address-block activate` | Mailings > Address Block | — | 点击「Address Block」（button） | 可能（应用提供撤销，未逐项验证） |
| `greeting-line.activate` | `foxos documents greeting-line activate` | Mailings > Greeting Line | — | 点击「Greeting Line」（button） | 可能（应用提供撤销，未逐项验证） |
| `merge-field.create` | `foxos documents merge-field create` | Mailings > Insert Merge Field | — | 点击「Insert Merge Field」（button） | 可能（应用提供撤销，未逐项验证） |
| `rules.activate` | `foxos documents rules activate` | Mailings > Rules | — | 点击「Rules」（button） | 可能（应用提供撤销，未逐项验证） |
| `match-fields.activate` | `foxos documents match-fields activate` | Mailings > Match Fields | — | 点击「Match Fields」（button） | 可能（应用提供撤销，未逐项验证） |
| `labels.update` | `foxos documents labels update` | Mailings > Update Labels | — | 点击「Update Labels」（button） | 可能（应用提供撤销，未逐项验证） |
| `preview-results.activate` | `foxos documents preview-results activate` | Mailings > Preview Results | — | 点击「Preview Results」（button） | 可能（应用提供撤销，未逐项验证） |
| `first-record.activate` | `foxos documents first-record activate` | Mailings > First Record | — | 点击「First Record」（button） | 可能（应用提供撤销，未逐项验证） |
| `record.previous` | `foxos documents record previous` | Mailings > Previous Record | — | 点击「Previous Record」（button） | 不适用（只读） |
| `go-record.set` | `foxos documents go-record set` | Mailings > Go to record | `value`（必填）, `submit` | 把「Go to record」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `record.next` | `foxos documents record next` | Mailings > Next Record | — | 点击「Next Record」（button） | 不适用（只读） |
| `last-record.activate` | `foxos documents last-record activate` | Mailings > Last Record | — | 点击「Last Record」（button） | 可能（应用提供撤销，未逐项验证） |
| `recipient.search` | `foxos documents recipient search` | Mailings > Find Recipient | — | 点击「Find Recipient」（button） | 不适用（只读） |
| `finish-merge.activate` | `foxos documents finish-merge activate` | Mailings > Finish & Merge | — | 点击「Finish & Merge」（button） | 可能（应用提供撤销，未逐项验证） |
| `editor.activate` | `foxos documents editor activate` | Review > Editor | — | 点击「Editor」（button） | 可能（应用提供撤销，未逐项验证） |
| `spelling-options.activate` | `foxos documents spelling-options activate` | Review > Spelling options | — | 点击「Spelling options」（button） | 可能（应用提供撤销，未逐项验证） |
| `thesaurus.activate` | `foxos documents thesaurus activate` | Review > Thesaurus | — | 点击「Thesaurus」（button） | 可能（应用提供撤销，未逐项验证） |
| `review-word-count.activate` | `foxos documents review-word-count activate` | Review > Word Count | — | 点击「Word Count」（button） | 可能（应用提供撤销，未逐项验证） |
| `review-read-aloud.activate` | `foxos documents review-read-aloud activate` | Review > Read Aloud | — | 点击「Read Aloud」（button） | 可能（应用提供撤销，未逐项验证） |
| `accessibility.run` | `foxos documents accessibility run` | Review > Check Accessibility | — | 点击「Check Accessibility」（button） | 可能（应用提供撤销，未逐项验证） |
| `review-language.activate` | `foxos documents review-language activate` | Review > Language | — | 点击「Language」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.delete` | `foxos documents comment delete` | Review > Delete Comment | — | 点击「Delete Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.delete` | `foxos documents options delete` | Review > Delete options | — | 点击「Delete options」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.previous` | `foxos documents comment previous` | Review > Previous Comment | — | 点击「Previous Comment」（button） | 不适用（只读） |
| `comment.next` | `foxos documents comment next` | Review > Next Comment | — | 点击「Next Comment」（button） | 不适用（只读） |
| `resolve-comment.activate` | `foxos documents resolve-comment activate` | Review > Resolve Comment | — | 点击「Resolve Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `comments.show` | `foxos documents comments show` | Review > Show Comments | — | 点击「Show Comments」（button），切换到该视图 | 不适用（只读） |
| `comments-options.show` | `foxos documents comments-options show` | Review > Show Comments options | — | 点击「Show Comments options」（button），切换到该视图 | 不适用（只读） |
| `tracking.activate` | `foxos documents tracking activate` | Review > Tracking | — | 点击「Tracking」（button） | 可能（应用提供撤销，未逐项验证） |
| `accept.activate` | `foxos documents accept activate` | Review > Accept | — | 点击「Accept」（button） | 可能（应用提供撤销，未逐项验证） |
| `accept-options.activate` | `foxos documents accept-options activate` | Review > Accept options | — | 点击「Accept options」（button） | 可能（应用提供撤销，未逐项验证） |
| `reject.activate` | `foxos documents reject activate` | Review > Reject | — | 点击「Reject」（button） | 可能（应用提供撤销，未逐项验证） |
| `reject-options.activate` | `foxos documents reject-options activate` | Review > Reject options | — | 点击「Reject options」（button） | 可能（应用提供撤销，未逐项验证） |
| `change.previous` | `foxos documents change previous` | Review > Previous Change | — | 点击「Previous Change」（button） | 不适用（只读） |
| `change.next` | `foxos documents change next` | Review > Next Change | — | 点击「Next Change」（button） | 不适用（只读） |
| `compare.activate` | `foxos documents compare activate` | Review > Compare | — | 点击「Compare」（button） | 可能（应用提供撤销，未逐项验证） |
| `restrict-editing.activate` | `foxos documents restrict-editing activate` | Review > Restrict Editing | — | 点击「Restrict Editing」（button） | 可能（应用提供撤销，未逐项验证） |
