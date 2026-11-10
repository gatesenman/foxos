# Notes（notes）操作清单

分组：office · 替代 Microsoft OneNote, Evernote, Apple Notes · 许可证 AGPL-3.0-only · 页面标题「Untitled Page - Notes」

共 136 个操作，全部有语义命令（`foxos notes <资源> <动词>`，MCP 工具 `notes.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `font-size.select` | `foxos notes font-size select` | 主界面 > # font size | `target`（必填） | 点击名称匹配的「# font size」项（button） | 不适用（只读） |
| `indent-position.select` | `foxos notes indent-position select` | 主界面 > # indent position | `target`（必填） | 点击名称匹配的「# indent position」项（button） | 不适用（只读） |
| `notebook.select` | `foxos notes notebook select` | 主界面 > notebook: * | `target`（必填） | 点击名称匹配的「notebook: *」项（button） | 不适用（只读） |
| `section.create` | `foxos notes section create` | 主界面 > Sections > new section # | `target`（必填） | 点击名称匹配的「new section #」项（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `heading-alt.select` | `foxos notes heading-alt select` | Styles > Styles > heading #+alt+# | `target`（必填） | 点击名称匹配的「heading #+alt+#」项（menuitemradio） | 不适用（只读） |
| `normalctrlalt.select` | `foxos notes normalctrlalt select` | Styles > Styles > normalctrl+alt+# | `target`（必填） | 点击名称匹配的「normalctrl+alt+#」项（menuitemradio） | 不适用（只读） |
| `doctrl.select` | `foxos notes doctrl select` | Tags > Tags > to doctrl+# | `target`（必填） | 点击名称匹配的「to doctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `importantctrl.select` | `foxos notes importantctrl select` | Tags > Tags > importantctrl+# | `target`（必填） | 点击名称匹配的「importantctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `questionctrl.select` | `foxos notes questionctrl select` | Tags > Tags > questionctrl+# | `target`（必填） | 点击名称匹配的「questionctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `remember.select` | `foxos notes remember select` | Tags > Tags > remember for * | `target`（必填） | 点击名称匹配的「remember for *」项（menuitemcheckbox） | 不适用（只读） |
| `definitionctrl.select` | `foxos notes definitionctrl select` | Tags > Tags > definitionctrl+# | `target`（必填） | 点击名称匹配的「definitionctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `highlightctrl.select` | `foxos notes highlightctrl select` | Tags > Tags > highlightctrl+# | `target`（必填） | 点击名称匹配的「highlightctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `contactctrl.select` | `foxos notes contactctrl select` | Tags > Tags > contactctrl+# | `target`（必填） | 点击名称匹配的「contactctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `addressctrl.select` | `foxos notes addressctrl select` | Tags > Tags > addressctrl+# | `target`（必填） | 点击名称匹配的「addressctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `phone-numberctrl.select` | `foxos notes phone-numberctrl select` | Tags > Tags > phone numberctrl+# | `target`（必填） | 点击名称匹配的「phone numberctrl+#」项（menuitemcheckbox） | 不适用（只读） |
| `source.select` | `foxos notes source select` | Tags > Tags > source for * | `target`（必填） | 点击名称匹配的「source for *」项（menuitemcheckbox） | 不适用（只读） |
| `do-priority.select` | `foxos notes do-priority select` | Tags > Tags > to do priority # | `target`（必填） | 点击名称匹配的「to do priority #」项（menuitemcheckbox） | 不适用（只读） |
| `tagctrl.delete` | `foxos notes tagctrl delete` | Tags > Tags > remove tagctrl+# | `target`（必填） | 点击名称匹配的「remove tagctrl+#」项（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos notes undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos notes redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `commands.show` | `foxos notes commands show` | 主界面 > More commands | — | 点击「More commands」（button），切换到该视图 | 不适用（只读） |
| `changes-saved-sync-now.activate` | `foxos notes changes-saved-sync-now activate` | 主界面 > All changes saved. Sync now | — | 点击「All changes saved. Sync now」（button） | 可能（应用提供撤销，未逐项验证） |
| `share.share` | `foxos notes share share` | 主界面 > Share | — | 点击「Share」（button） | 可能（应用提供撤销，未逐项验证） |
| `file.activate` | `foxos notes file activate` | 主界面 > Ribbon > File | — | 点击「File」（button） | 可能（应用提供撤销，未逐项验证） |
| `home.show` | `foxos notes home show` | 主界面 > Ribbon tabs > Home | — | 点击「Home」（tab），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos notes insert create` | 主界面 > Ribbon tabs > Insert | — | 点击「Insert」（tab） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos notes draw draw` | 主界面 > Ribbon tabs > Draw | — | 点击「Draw」（tab） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos notes view show` | 主界面 > Ribbon tabs > View | — | 点击「View」（tab），切换到该视图 | 不适用（只读） |
| `help.show` | `foxos notes help show` | 主界面 > Ribbon tabs > Help | — | 点击「Help」（tab），切换到该视图 | 不适用（只读） |
| `tell-me-what-you-want-do.set` | `foxos notes tell-me-what-you-want-do set` | 主界面 > Tell me what you want to do | `value`（必填）, `submit` | 把「Tell me what you want to do」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `ribbon.collapse` | `foxos notes ribbon collapse` | 主界面 > Collapse the Ribbon | — | 点击「Collapse the Ribbon」（button） | 不适用（只读） |
| `paste.paste` | `foxos notes paste paste` | 主界面 > Paste | — | 点击「Paste」（button） | 可能（应用提供撤销，未逐项验证） |
| `cut.cut` | `foxos notes cut cut` | 主界面 > Cut | — | 点击「Cut」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.copy` | `foxos notes copy copy` | 主界面 > Copy | — | 点击「Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-painter.activate` | `foxos notes format-painter activate` | 主界面 > Format Painter | — | 点击「Format Painter」（button） | 可能（应用提供撤销，未逐项验证） |
| `font.set` | `foxos notes font set` | 主界面 > Font | `value`（必填）, `submit` | 把「Font」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `font-list.activate` | `foxos notes font-list activate` | 主界面 > Font list | — | 点击「Font list」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-size.set` | `foxos notes font-size set` | 主界面 > Font Size | `value`（必填）, `submit` | 把「Font Size」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `font-size-list.activate` | `foxos notes font-size-list activate` | 主界面 > Font size list | — | 点击「Font size list」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-font-size.activate` | `foxos notes increase-font-size activate` | 主界面 > Increase Font Size | — | 点击「Increase Font Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `bold.format` | `foxos notes bold format` | 主界面 > Bold | — | 点击「Bold」（button） | 可能（应用提供撤销，未逐项验证） |
| `italic.format` | `foxos notes italic format` | 主界面 > Italic | — | 点击「Italic」（button） | 可能（应用提供撤销，未逐项验证） |
| `underline.format` | `foxos notes underline format` | 主界面 > Underline | — | 点击「Underline」（button） | 可能（应用提供撤销，未逐项验证） |
| `strikethrough.format` | `foxos notes strikethrough format` | 主界面 > Strikethrough | — | 点击「Strikethrough」（button） | 可能（应用提供撤销，未逐项验证） |
| `subscript.activate` | `foxos notes subscript activate` | 主界面 > Subscript | — | 点击「Subscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `superscript.activate` | `foxos notes superscript activate` | 主界面 > Superscript | — | 点击「Superscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-highlight-color.activate` | `foxos notes text-highlight-color activate` | 主界面 > Text Highlight Color | — | 点击「Text Highlight Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-highlight-color-options.activate` | `foxos notes text-highlight-color-options activate` | 主界面 > Text Highlight Color options | — | 点击「Text Highlight Color options」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-color.activate` | `foxos notes font-color activate` | 主界面 > Font Color | — | 点击「Font Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-color-options.activate` | `foxos notes font-color-options activate` | 主界面 > Font Color options | — | 点击「Font Color options」（button） | 可能（应用提供撤销，未逐项验证） |
| `formatting.clear` | `foxos notes formatting clear` | 主界面 > Clear All Formatting | — | 点击「Clear All Formatting」（button） | 可能（应用提供撤销，未逐项验证） |
| `bullets.activate` | `foxos notes bullets activate` | 主界面 > Bullets | — | 点击「Bullets」（button） | 可能（应用提供撤销，未逐项验证） |
| `bullets-options.activate` | `foxos notes bullets-options activate` | 主界面 > Bullets options | — | 点击「Bullets options」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbering.activate` | `foxos notes numbering activate` | 主界面 > Numbering | — | 点击「Numbering」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbering-options.activate` | `foxos notes numbering-options activate` | 主界面 > Numbering options | — | 点击「Numbering options」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-indent-position.activate` | `foxos notes increase-indent-position activate` | 主界面 > Increase Indent Position | — | 点击「Increase Indent Position」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-alignment.activate` | `foxos notes paragraph-alignment activate` | 主界面 > Paragraph Alignment | — | 点击「Paragraph Alignment」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-up.move` | `foxos notes paragraph-up move` | 主界面 > Move Paragraph Up | — | 点击「Move Paragraph Up」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-down.move` | `foxos notes paragraph-down move` | 主界面 > Move Paragraph Down | — | 点击「Move Paragraph Down」（button） | 可能（应用提供撤销，未逐项验证） |
| `styles.activate` | `foxos notes styles activate` | 主界面 > Styles | — | 点击「Styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `do-tag.activate` | `foxos notes do-tag activate` | 主界面 > To Do Tag | — | 点击「To Do Tag」（button） | 可能（应用提供撤销，未逐项验证） |
| `tags.activate` | `foxos notes tags activate` | 主界面 > Tags | — | 点击「Tags」（button） | 可能（应用提供撤销，未逐项验证） |
| `tags.search` | `foxos notes tags search` | 主界面 > Find Tags | — | 点击「Find Tags」（button） | 不适用（只读） |
| `dictate.activate` | `foxos notes dictate activate` | 主界面 > Dictate | — | 点击「Dictate」（button） | 可能（应用提供撤销，未逐项验证） |
| `assist.activate` | `foxos notes assist activate` | 主界面 > Assist | — | 点击「Assist」（button） | 可能（应用提供撤销，未逐项验证） |
| `email-page.activate` | `foxos notes email-page activate` | 主界面 > Email Page | — | 点击「Email Page」（button） | 可能（应用提供撤销，未逐项验证） |
| `notebooks.activate` | `foxos notes notebooks activate` | 主界面 > Notebooks | — | 点击「Notebooks」（button） | 可能（应用提供撤销，未逐项验证） |
| `search.search` | `foxos notes search search` | 主界面 > Search | — | 点击「Search」（button） | 不适用（只读） |
| `recent-notes.activate` | `foxos notes recent-notes activate` | 主界面 > Recent Notes | — | 点击「Recent Notes」（button） | 可能（应用提供撤销，未逐项验证） |
| `account.activate` | `foxos notes account activate` | 主界面 > Account | — | 点击「Account」（button） | 可能（应用提供撤销，未逐项验证） |
| `quick-notes.activate` | `foxos notes quick-notes activate` | 主界面 > Sections > Quick Notes | — | 点击「Quick Notes」（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `section-2.create` | `foxos notes section-2 create` | 主界面 > Sections > Add section | — | 点击「Add section」（button） | 可能（应用提供撤销，未逐项验证） |
| `sections-pane.resize` | `foxos notes sections-pane resize` | 主界面 > Resize sections pane | — | 点击「Resize sections pane」（separator） | 可能（应用提供撤销，未逐项验证） |
| `pages.sort` | `foxos notes pages sort` | 主界面 > Sort pages | — | 点击「Sort pages」（button） | 不适用（只读） |
| `untitled-page.activate` | `foxos notes untitled-page activate` | 主界面 > Pages > Untitled Page | — | 点击「Untitled Page」（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `page.create` | `foxos notes page create` | 主界面 > Pages > Add page | — | 点击「Add page」（button） | 可能（应用提供撤销，未逐项验证） |
| `pages-pane.resize` | `foxos notes pages-pane resize` | 主界面 > Resize pages pane | — | 点击「Resize pages pane」（separator） | 可能（应用提供撤销，未逐项验证） |
| `page-date.activate` | `foxos notes page-date activate` | 主界面 > Page date | — | 点击「Page date」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-time.activate` | `foxos notes page-time activate` | 主界面 > Page time | — | 点击「Page time」（button） | 可能（应用提供撤销，未逐项验证） |
| `pagectrlaltn.create` | `foxos notes pagectrlaltn create` | More commands > More commands > New PageCtrl+Alt+N | — | 点击「New PageCtrl+Alt+N」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `sectionctrlaltt.create` | `foxos notes sectionctrlaltt create` | More commands > More commands > New SectionCtrl+Alt+T | — | 点击「New SectionCtrl+Alt+T」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `section-group.create` | `foxos notes section-group create` | More commands > More commands > New Section Group | — | 点击「New Section Group」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `notebook.create` | `foxos notes notebook create` | More commands > More commands > New Notebook... | — | 点击「New Notebook...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `import.import` | `foxos notes import import` | More commands > More commands > Import... | — | 点击「Import...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos notes export export` | More commands > More commands > Export | — | 点击「Export」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `more-commands-share.share` | `foxos notes more-commands-share share` | More commands > More commands > Share... | — | 点击「Share...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `ctrlp.print` | `foxos notes ctrlp print` | More commands > More commands > Print...Ctrl+P | — | 点击「Print...Ctrl+P」（menuitem） | 不适用（只读） |
| `sync-nowctrls.activate` | `foxos notes sync-nowctrls activate` | More commands > More commands > Sync NowCtrl+S | — | 点击「Sync NowCtrl+S」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `deleted-notes.activate` | `foxos notes deleted-notes activate` | More commands > More commands > Deleted Notes | — | 点击「Deleted Notes」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `protected-sectionsctrlaltl.lock` | `foxos notes protected-sectionsctrlaltl lock` | More commands > More commands > Lock All Protected SectionsCtrl+Alt+L | — | 点击「Lock All Protected SectionsCtrl+Alt+L」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `theme.activate` | `foxos notes theme activate` | More commands > More commands > Theme | — | 点击「Theme」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcutsctrlshift.activate` | `foxos notes keyboard-shortcutsctrlshift activate` | More commands > More commands > Keyboard ShortcutsCtrl+Shift+/ | — | 点击「Keyboard ShortcutsCtrl+Shift+/」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `notes.show` | `foxos notes notes show` | More commands > More commands > About Notes | — | 点击「About Notes」（menuitem），切换到该视图 | 不适用（只读） |
| `file-pagectrlaltn.create` | `foxos notes file-pagectrlaltn create` | File > File > New PageCtrl+Alt+N | — | 点击「New PageCtrl+Alt+N」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-sectionctrlaltt.create` | `foxos notes file-sectionctrlaltt create` | File > File > New SectionCtrl+Alt+T | — | 点击「New SectionCtrl+Alt+T」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-section-group.create` | `foxos notes file-section-group create` | File > File > New Section Group | — | 点击「New Section Group」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-notebook.create` | `foxos notes file-notebook create` | File > File > New Notebook... | — | 点击「New Notebook...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-import.import` | `foxos notes file-import import` | File > File > Import... | — | 点击「Import...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-export.export` | `foxos notes file-export export` | File > File > Export | — | 点击「Export」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-share.share` | `foxos notes file-share share` | File > File > Share... | — | 点击「Share...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-ctrlp.print` | `foxos notes file-ctrlp print` | File > File > Print...Ctrl+P | — | 点击「Print...Ctrl+P」（menuitem） | 不适用（只读） |
| `file-sync-nowctrls.activate` | `foxos notes file-sync-nowctrls activate` | File > File > Sync NowCtrl+S | — | 点击「Sync NowCtrl+S」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-deleted-notes.activate` | `foxos notes file-deleted-notes activate` | File > File > Deleted Notes | — | 点击「Deleted Notes」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-protected-sectionsctrlaltl.lock` | `foxos notes file-protected-sectionsctrlaltl lock` | File > File > Lock All Protected SectionsCtrl+Alt+L | — | 点击「Lock All Protected SectionsCtrl+Alt+L」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-theme.activate` | `foxos notes file-theme activate` | File > File > Theme | — | 点击「Theme」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-keyboard-shortcutsctrlshift.activate` | `foxos notes file-keyboard-shortcutsctrlshift activate` | File > File > Keyboard ShortcutsCtrl+Shift+/ | — | 点击「Keyboard ShortcutsCtrl+Shift+/」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `file-notes.show` | `foxos notes file-notes show` | File > File > About Notes | — | 点击「About Notes」（menuitem），切换到该视图 | 不适用（只读） |
| `page-title.activate` | `foxos notes page-title activate` | Styles > Styles > Page Title | — | 点击「Page Title」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `citation.activate` | `foxos notes citation activate` | Styles > Styles > Citation | — | 点击「Citation」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `quote.activate` | `foxos notes quote activate` | Styles > Styles > Quote | — | 点击「Quote」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `code.activate` | `foxos notes code activate` | Styles > Styles > Code | — | 点击「Code」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `website-visit.activate` | `foxos notes website-visit activate` | Tags > Tags > Website to visit | — | 点击「Website to visit」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `idea.activate` | `foxos notes idea activate` | Tags > Tags > Idea | — | 点击「Idea」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `password.activate` | `foxos notes password activate` | Tags > Tags > Password | — | 点击「Password」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `critical.activate` | `foxos notes critical activate` | Tags > Tags > Critical | — | 点击「Critical」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `project.activate` | `foxos notes project activate` | Tags > Tags > Project A | — | 点击「Project A」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `project-b.activate` | `foxos notes project-b activate` | Tags > Tags > Project B | — | 点击「Project B」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `movie-see.activate` | `foxos notes movie-see activate` | Tags > Tags > Movie to see | — | 点击「Movie to see」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `book-read.activate` | `foxos notes book-read activate` | Tags > Tags > Book to read | — | 点击「Book to read」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `music-listen.activate` | `foxos notes music-listen activate` | Tags > Tags > Music to listen to | — | 点击「Music to listen to」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `discuss-manager.activate` | `foxos notes discuss-manager activate` | Tags > Tags > Discuss with manager | — | 点击「Discuss with manager」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `email.send` | `foxos notes email send` | Tags > Tags > Send in email | — | 点击「Send in email」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `meeting.schedule` | `foxos notes meeting schedule` | Tags > Tags > Schedule meeting | — | 点击「Schedule meeting」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `call-back.activate` | `foxos notes call-back activate` | Tags > Tags > Call back | — | 点击「Call back」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `client-request.activate` | `foxos notes client-request activate` | Tags > Tags > Client request | — | 点击「Client request」（menuitemcheckbox） | 可能（应用提供撤销，未逐项验证） |
| `tags-2.search` | `foxos notes tags-2 search` | Tags > Tags > Find Tags | — | 点击「Find Tags」（menuitem） | 不适用（只读） |
| `account-theme.activate` | `foxos notes account-theme activate` | Account > Account > Theme | — | 点击「Theme」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcuts.activate` | `foxos notes keyboard-shortcuts activate` | Account > Account > Keyboard Shortcuts | — | 点击「Keyboard Shortcuts」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `account-notes.show` | `foxos notes account-notes show` | Account > Account > About Notes | — | 点击「About Notes」（menuitem），切换到该视图 | 不适用（只读） |
| `local-s-notebook.activate` | `foxos notes local-s-notebook activate` | Notebook: local's Notebook. Switch notebooks > Notebooks > local's Notebook | — | 点击「local's Notebook」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `notebook-locals-notebook-switch-notebook-noteboo.create` | `foxos notes notebook-locals-notebook-switch-notebook-noteboo create` | Notebook: local's Notebook. Switch notebooks > Notebooks > Add Notebook | — | 点击「Add Notebook」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `notebook-settings.activate` | `foxos notes notebook-settings activate` | Notebook: local's Notebook. Switch notebooks > Notebooks > Notebook Settings | — | 点击「Notebook Settings」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `none-order.activate` | `foxos notes none-order activate` | Sort pages > Sort pages > None (your order) | — | 点击「None (your order)」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `date-created.activate` | `foxos notes date-created activate` | Sort pages > Sort pages > Date created | — | 点击「Date created」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `date-modified.activate` | `foxos notes date-modified activate` | Sort pages > Sort pages > Date modified | — | 点击「Date modified」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `alphabetical.activate` | `foxos notes alphabetical activate` | Sort pages > Sort pages > Alphabetical | — | 点击「Alphabetical」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
