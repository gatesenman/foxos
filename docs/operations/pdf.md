# PDF（pdf）操作清单

分组：office · 替代 Adobe Acrobat, PDF Expert · 许可证 AGPL-3.0-only · 页面标题「Untitled.pdf · PDF Editor」

共 85 个操作，全部有语义命令（`foxos pdf <资源> <动词>`，MCP 工具 `pdf.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `notes-highlight-text-up-pages.leave` | `foxos pdf notes-highlight-text-up-pages leave` | 主界面 > Tools > leave notes, highlight text, and # up pages. | `target`（必填） | 点击名称匹配的「leave notes, highlight text, and # up pages.」项（button） | 可能（应用提供撤销，未逐项验证） |
| `fillable-fields.create` | `foxos pdf fillable-fields create` | 主界面 > Tools > add fillable fields: * | `target`（必填） | 点击名称匹配的「add fillable fields: *」项（button） | 可能（应用提供撤销，未逐项验证） |
| `tools.select` | `foxos pdf tools select` | 主界面 > Tools > # text, pictures, or areas, then apply to remove them from the file for good. | `target`（必填） | 点击名称匹配的「# text, pictures, or areas, then apply to remove them from the file for good.」项（button） | 不适用（只读） |
| `go-page.select` | `foxos pdf go-page select` | 主界面 > go to page # | `target`（必填） | 点击名称匹配的「go to page #」项（button） | 不适用（只读） |
| `page-actions.select` | `foxos pdf page-actions select` | 主界面 > page # actions | `target`（必填） | 点击名称匹配的「page # actions」项（button） | 不适用（只读） |
| `pages.select` | `foxos pdf pages select` | Print file > Pages to include > all pages (#) | `target`（必填） | 点击名称匹配的「all pages (#)」项（radio） | 不适用（只读） |
| `current-page.select` | `foxos pdf current-page select` | Print file > Pages to include > current page (#) | `target`（必填） | 点击名称匹配的「current page (#)」项（radio） | 不适用（只读） |
| `content.dismiss` | `foxos pdf content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `pdfs.previous` | `foxos pdf pdfs previous` | 主界面 > Back to your PDFs | — | 点击「Back to your PDFs」（button） | 不适用（只读） |
| `file.activate` | `foxos pdf file activate` | 主界面 > PDF menus > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos pdf edit update` | 主界面 > PDF menus > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos pdf view show` | 主界面 > PDF menus > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `page.activate` | `foxos pdf page activate` | 主界面 > PDF menus > Page | — | 点击「Page」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `insert.create` | `foxos pdf insert create` | 主界面 > PDF menus > Insert | — | 点击「Insert」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `untitled-pdf.rename` | `foxos pdf untitled-pdf rename` | 主界面 > Rename Untitled.pdf | — | 点击「Rename Untitled.pdf」（button） | 可能（应用提供撤销，未逐项验证） |
| `settings.show` | `foxos pdf settings show` | 主界面 > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `tools.activate` | `foxos pdf tools activate` | 主界面 > Tool sets > Tools | — | 点击「Tools」（button） | 可能（应用提供撤销，未逐项验证） |
| `edit-2.update` | `foxos pdf edit-2 update` | 主界面 > Tool sets > Edit | — | 点击「Edit」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.activate` | `foxos pdf comment activate` | 主界面 > Tool sets > Comment | — | 点击「Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos pdf export export` | 主界面 > Tool sets > Export | — | 点击「Export」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-sign.activate` | `foxos pdf fill-sign activate` | 主界面 > Tool sets > Fill & Sign | — | 点击「Fill & Sign」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-or-tools.search` | `foxos pdf text-or-tools search` | 主界面 > Find text or tools | — | 点击「Find text or tools」（button） | 不适用（只读） |
| `undo.undo` | `foxos pdf undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos pdf redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `download.export` | `foxos pdf download export` | 主界面 > Download | — | 点击「Download」（button） | 可能（应用提供撤销，未逐项验证） |
| `file.print` | `foxos pdf file print` | 主界面 > Print file | — | 点击「Print file」（button） | 不适用（只读） |
| `puter.save` | `foxos pdf puter save` | 主界面 > Save to Puter | — | 点击「Save to Puter」（button） | 可能（应用提供撤销，未逐项验证） |
| `tools-panel.close` | `foxos pdf tools-panel close` | 主界面 > Close tools panel | — | 点击「Close tools panel」（button） | 不适用（只读） |
| `pdf-or-its-pages-another-format.save` | `foxos pdf pdf-or-its-pages-another-format save` | 主界面 > Tools > Save the PDF, or its pages, in another format. | — | 点击「Save the PDF, or its pages, in another format.」（button） | 可能（应用提供撤销，未逐项验证） |
| `pdf-or-turn-pictures-into-pdf-pages.start` | `foxos pdf pdf-or-turn-pictures-into-pdf-pages start` | 主界面 > Tools > Start a new PDF, or turn pictures into PDF pages. | — | 点击「Start a new PDF, or turn pictures into PDF pages.」（button） | 可能（应用提供撤销，未逐项验证） |
| `combine-pdfs-pictures-into-one-pdf.activate` | `foxos pdf combine-pdfs-pictures-into-one-pdf activate` | 主界面 > Tools > Combine PDFs and pictures into one new PDF. | — | 点击「Combine PDFs and pictures into one new PDF.」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-forms-add-signature.activate` | `foxos pdf fill-forms-add-signature activate` | 主界面 > Tools > Fill in forms and add your signature. | — | 点击「Fill in forms and add your signature.」（button） | 可能（应用提供撤销，未逐项验证） |
| `make-file-smaller-by-shrinking-its-pictu.activate` | `foxos pdf make-file-smaller-by-shrinking-its-pictu activate` | 主界面 > Tools > Make the file smaller by shrinking its pictures. | — | 点击「Make the file smaller by shrinking its pictures.」（button） | 可能（应用提供撤销，未逐项验证） |
| `more.show` | `foxos pdf more show` | 主界面 > Tools > View more | — | 点击「View more」（button），切换到该视图 | 不适用（只读） |
| `select.select` | `foxos pdf select select` | 主界面 > Select | — | 点击「Select」（button） | 不适用（只读） |
| `hand.activate` | `foxos pdf hand activate` | 主界面 > Hand | — | 点击「Hand」（button） | 可能（应用提供撤销，未逐项验证） |
| `text.activate` | `foxos pdf text activate` | 主界面 > Text | — | 点击「Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `highlight.activate` | `foxos pdf highlight activate` | 主界面 > Highlight | — | 点击「Highlight」（button） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos pdf draw draw` | 主界面 > Draw | — | 点击「Draw」（button） | 可能（应用提供撤销，未逐项验证） |
| `shape.activate` | `foxos pdf shape activate` | 主界面 > Shape | — | 点击「Shape」（button） | 可能（应用提供撤销，未逐项验证） |
| `note.activate` | `foxos pdf note activate` | 主界面 > Note | — | 点击「Note」（button） | 可能（应用提供撤销，未逐项验证） |
| `image.activate` | `foxos pdf image activate` | 主界面 > Image | — | 点击「Image」（button） | 可能（应用提供撤销，未逐项验证） |
| `sign.sign` | `foxos pdf sign sign` | 主界面 > Sign | — | 点击「Sign」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-forms.activate` | `foxos pdf fill-forms activate` | 主界面 > Fill forms | — | 点击「Fill forms」（button） | 可能（应用提供撤销，未逐项验证） |
| `pdf-page-view.activate` | `foxos pdf pdf-page-view activate` | 主界面 > PDF page view | — | 点击「PDF page view」（region） | 可能（应用提供撤销，未逐项验证） |
| `page.previous` | `foxos pdf page previous` | 主界面 > Previous page | — | 点击「Previous page」（button） | 不适用（只读） |
| `page-number.set` | `foxos pdf page-number set` | 主界面 > Page number | `value`（必填）, `submit` | 把「Page number」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `page.next` | `foxos pdf page next` | 主界面 > Next page | — | 点击「Next page」（button） | 不适用（只读） |
| `view.zoom-out` | `foxos pdf view zoom-out` | 主界面 > Zoom out | — | 点击「Zoom out」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom.set` | `foxos pdf zoom set` | 主界面 > Zoom | `value`（必填）, `submit` | 把「Zoom」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-` | `foxos pdf view zoom-` | 主界面 > Zoom in | — | 点击「Zoom in」（button） | 可能（应用提供撤销，未逐项验证） |
| `pages.show` | `foxos pdf pages show` | 主界面 > Pages | — | 点击「Pages」（tab），切换到该视图 | 不适用（只读） |
| `comments.show` | `foxos pdf comments show` | 主界面 > Comments | — | 点击「Comments」（tab），切换到该视图 | 不适用（只读） |
| `attachments.show` | `foxos pdf attachments show` | 主界面 > Attachments | — | 点击「Attachments」（tab），切换到该视图 | 不适用（只读） |
| `pages-panel.toggle` | `foxos pdf pages-panel toggle` | 主界面 > Toggle pages panel | — | 切换「Toggle pages panel」 | 可能（应用提供撤销，未逐项验证） |
| `pages-panel.close` | `foxos pdf pages-panel close` | 主界面 > Close pages panel | — | 点击「Close pages panel」（button） | 不适用（只读） |
| `dialog.close` | `foxos pdf dialog close` | Settings > Close dialog | — | 点击「Close dialog」（button） | 不适用（只读） |
| `appearance.set` | `foxos pdf appearance set` | Settings > dialog > Appearance | `value`（必填）, `submit` | 把「Appearance」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcuts.activate` | `foxos pdf keyboard-shortcuts activate` | Settings > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 可能（应用提供撤销，未逐项验证） |
| `pdf-editor.show` | `foxos pdf pdf-editor show` | Settings > About PDF Editor | — | 点击「About PDF Editor」（button），切换到该视图 | 不适用（只读） |
| `tools.previous` | `foxos pdf tools previous` | Edit > Back to all tools | — | 点击「Back to all tools」（button） | 不适用（只读） |
| `text.create` | `foxos pdf text create` | Edit > Add text | — | 点击「Add text」（button） | 可能（应用提供撤销，未逐项验证） |
| `image.create` | `foxos pdf image create` | Edit > Add image | — | 点击「Add image」（button） | 可能（应用提供撤销，未逐项验证） |
| `link.create` | `foxos pdf link create` | Edit > Add link | — | 点击「Add link」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-images.update` | `foxos pdf text-images update` | Edit > Edit text and images | — | 点击「Edit text and images」（button） | 可能（应用提供撤销，未逐项验证） |
| `pages.crop` | `foxos pdf pages crop` | Edit > Crop pages | — | 点击「Crop pages」（button） | 可能（应用提供撤销，未逐项验证） |
| `header-footer.activate` | `foxos pdf header-footer activate` | Edit > Header and footer… | — | 点击「Header and footer…」（button） | 可能（应用提供撤销，未逐项验证） |
| `watermark.activate` | `foxos pdf watermark activate` | Edit > Watermark… | — | 点击「Watermark…」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-numbers.activate` | `foxos pdf page-numbers activate` | Edit > Page numbers… | — | 点击「Page numbers…」（button） | 可能（应用提供撤销，未逐项验证） |
| `bates-numbering.activate` | `foxos pdf bates-numbering activate` | Edit > Bates numbering… | — | 点击「Bates numbering…」（button） | 可能（应用提供撤销，未逐项验证） |
| `headers-footers.delete` | `foxos pdf headers-footers delete` | Edit > Remove headers and footers | — | 点击「Remove headers and footers」（button） | 可能（应用提供撤销，未逐项验证） |
| `watermarks.delete` | `foxos pdf watermarks delete` | Edit > Remove watermarks | — | 点击「Remove watermarks」（button） | 可能（应用提供撤销，未逐项验证） |
| `find-pdf.set` | `foxos pdf find-pdf set` | Find text or tools > Find in PDF | `value`（必填）, `submit` | 把「Find in PDF」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `match.previous` | `foxos pdf match previous` | Find text or tools > Previous match | — | 点击「Previous match」（button） | 不适用（只读） |
| `match.next` | `foxos pdf match next` | Find text or tools > Next match | — | 点击「Next match」（button） | 不适用（只读） |
| `search.close` | `foxos pdf search close` | Find text or tools > Close search | — | 点击「Close search」（button） | 不适用（只读） |
| `pages.toggle` | `foxos pdf pages toggle` | Print file > Pages to include > Pages | — | 切换「Pages」 | 可能（应用提供撤销，未逐项验证） |
| `page-range.set` | `foxos pdf page-range set` | Print file > Page range | `value`（必填）, `submit` | 把「Page range」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `cancel.cancel` | `foxos pdf cancel cancel` | Print file > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `print.print` | `foxos pdf print print` | Print file > Print | — | 点击「Print」（button） | 不适用（只读） |
| `comments-panel.close` | `foxos pdf comments-panel close` | Comments > Close comments panel | — | 点击「Close comments panel」（button） | 不适用（只读） |
| `attachments-panel.close` | `foxos pdf attachments-panel close` | Attachments > Close attachments panel | — | 点击「Close attachments panel」（button） | 不适用（只读） |
| `attach-file.activate` | `foxos pdf attach-file activate` | Attachments > Attach a file… | — | 点击「Attach a file…」（button） | 可能（应用提供撤销，未逐项验证） |
| `selection.select-all` | `foxos pdf selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/organize-view.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.group-shift` | `foxos pdf selection group-shift` | 键盘 mod+shift+g | — | 在当前焦点上按 mod+shift+g（src/compare-view.js 中定义） | 可能（应用提供撤销，未逐项验证） |
