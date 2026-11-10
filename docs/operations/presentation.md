# Presentation（presentation）操作清单

分组：office · 替代 Microsoft PowerPoint, Google Slides, Apple Keynote · 许可证 AGPL-3.0-only · 页面标题「Untitled presentation | Presentation」

共 284 个操作，全部有语义命令（`foxos presentation <资源> <动词>`，MCP 工具 `presentation.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `search.search` | `foxos presentation search search` | 主界面 > search for * | `target`（必填） | 点击名称匹配的「search for *」项（textbox） | 不适用（只读） |
| `local.select` | `foxos presentation local select` | 主界面 > local: * | `target`（必填） | 点击名称匹配的「local: *」项（button） | 不适用（只读） |
| `font-size.select` | `foxos presentation font-size select` | 主界面 > # font size | `target`（必填） | 点击名称匹配的「# font size」项（button） | 不适用（只读） |
| `list-level.select` | `foxos presentation list-level select` | 主界面 > # list level | `target`（必填） | 点击名称匹配的「# list level」项（button） | 不适用（只读） |
| `slide-1.select` | `foxos presentation slide-1 select` | 主界面 > slide 1: * | `target`（必填） | 点击名称匹配的「slide 1: *」项（button） | 不适用（只读） |
| `options.select` | `foxos presentation options select` | 主界面 > options for * | `target`（必填） | 点击名称匹配的「options for *」项（button） | 不适用（只读） |
| `centered-title-select-edit.select` | `foxos presentation centered-title-select-edit select` | 主界面 > centered title # select to edit | `target`（必填） | 点击名称匹配的「centered title # select to edit」项（button） | 不适用（只读） |
| `subtitle-select-edit.select` | `foxos presentation subtitle-select-edit select` | 主界面 > subtitle # select to edit | `target`（必填） | 点击名称匹配的「subtitle # select to edit」项（button） | 不适用（只读） |
| `draft-6-slide-pitch-deck.select` | `foxos presentation draft-6-slide-pitch-deck select` | 主界面 > Suggestions > draft a 6-slide pitch deck for * | `target`（必填） | 点击名称匹配的「draft a 6-slide pitch deck for *」项（button） | 不适用（只读） |
| `outline-talk-topic-i-give-you.select` | `foxos presentation outline-talk-topic-i-give-you select` | 主界面 > Suggestions > outline a # talk on a topic i give you | `target`（必填） | 点击名称匹配的「outline a # talk on a topic i give you」项（button） | 不适用（只读） |
| `accessibility.select` | `foxos presentation accessibility select` | 主界面 > footer > accessibility: * | `target`（必填） | 点击名称匹配的「accessibility: *」项（button） | 不适用（只读） |
| `pen.select` | `foxos presentation pen select` | Draw > pen: * | `target`（必填） | 点击名称匹配的「pen: *」项（button） | 不适用（只读） |
| `pencil.select` | `foxos presentation pencil select` | Draw > pencil: * | `target`（必填） | 点击名称匹配的「pencil: *」项（button） | 不适用（只读） |
| `highlighter.select` | `foxos presentation highlighter select` | Draw > highlighter: * | `target`（必填） | 点击名称匹配的「highlighter: *」项（button） | 不适用（只读） |
| `duration.select` | `foxos presentation duration select` | Transitions > # duration | `target`（必填） | 点击名称匹配的「# duration」项（button） | 不适用（只读） |
| `advance-after.select` | `foxos presentation advance-after select` | Transitions > # advance after | `target`（必填） | 点击名称匹配的「# advance after」项（button） | 不适用（只读） |
| `delay.select` | `foxos presentation delay select` | Animations > # delay | `target`（必填） | 点击名称匹配的「# delay」项（button） | 不适用（只读） |
| `content.dismiss` | `foxos presentation content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `presentations.previous` | `foxos presentation presentations previous` | 主界面 > Back to presentations | — | 点击「Back to presentations」（button） | 不适用（只读） |
| `puter.save` | `foxos presentation puter save` | 主界面 > Save to Puter | — | 点击「Save to Puter」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos presentation undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos presentation redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `file.activate` | `foxos presentation file activate` | 主界面 > Presentation menus > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos presentation edit update` | 主界面 > Presentation menus > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `view.show` | `foxos presentation view show` | 主界面 > Presentation menus > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos presentation insert create` | 主界面 > Presentation menus > Insert | — | 点击「Insert」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `format.activate` | `foxos presentation format activate` | 主界面 > Presentation menus > Format | — | 点击「Format」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `arrange.activate` | `foxos presentation arrange activate` | 主界面 > Presentation menus > Arrange | — | 点击「Arrange」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `slide.activate` | `foxos presentation slide activate` | 主界面 > Presentation menus > Slide | — | 点击「Slide」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `tools.activate` | `foxos presentation tools activate` | 主界面 > Presentation menus > Tools | — | 点击「Tools」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `slide-show.activate` | `foxos presentation slide-show activate` | 主界面 > Presentation menus > Slide Show | — | 点击「Slide Show」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos presentation help show` | 主界面 > Presentation menus > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `untitled-presentation.rename` | `foxos presentation untitled-presentation rename` | 主界面 > header > Rename “Untitled presentation” | — | 点击「Rename “Untitled presentation”」（button） | 可能（应用提供撤销，未逐项验证） |
| `save.save` | `foxos presentation save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `ask-ai.activate` | `foxos presentation ask-ai activate` | 主界面 > Ask AI | — | 点击「Ask AI」（button） | 可能（应用提供撤销，未逐项验证） |
| `present.activate` | `foxos presentation present activate` | 主界面 > Present | — | 点击「Present」（button） | 可能（应用提供撤销，未逐项验证） |
| `home.show` | `foxos presentation home show` | 主界面 > Ribbon tabs > Home | — | 点击「Home」（tab），切换到该视图 | 不适用（只读） |
| `insert-2.create` | `foxos presentation insert-2 create` | 主界面 > Ribbon tabs > Insert | — | 点击「Insert」（tab） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos presentation draw draw` | 主界面 > Ribbon tabs > Draw | — | 点击「Draw」（tab） | 可能（应用提供撤销，未逐项验证） |
| `design.show` | `foxos presentation design show` | 主界面 > Ribbon tabs > Design | — | 点击「Design」（tab），切换到该视图 | 不适用（只读） |
| `transitions.show` | `foxos presentation transitions show` | 主界面 > Ribbon tabs > Transitions | — | 点击「Transitions」（tab），切换到该视图 | 不适用（只读） |
| `animations.show` | `foxos presentation animations show` | 主界面 > Ribbon tabs > Animations | — | 点击「Animations」（tab），切换到该视图 | 不适用（只读） |
| `slide-show.show` | `foxos presentation slide-show show` | 主界面 > Ribbon tabs > Slide Show | — | 点击「Slide Show」（tab），切换到该视图 | 不适用（只读） |
| `record.record` | `foxos presentation record record` | 主界面 > Ribbon tabs > Record | — | 点击「Record」（tab） | 可能（应用提供撤销，未逐项验证） |
| `review.show` | `foxos presentation review show` | 主界面 > Ribbon tabs > Review | — | 点击「Review」（tab），切换到该视图 | 不适用（只读） |
| `view-2.show` | `foxos presentation view-2 show` | 主界面 > Ribbon tabs > View | — | 点击「View」（tab），切换到该视图 | 不适用（只读） |
| `ribbon.collapse` | `foxos presentation ribbon collapse` | 主界面 > Collapse the ribbon | — | 点击「Collapse the ribbon」（button） | 不适用（只读） |
| `paste.paste` | `foxos presentation paste paste` | 主界面 > Paste | — | 点击「Paste」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.paste` | `foxos presentation options paste` | 主界面 > Paste options | — | 点击「Paste options」（button） | 可能（应用提供撤销，未逐项验证） |
| `cut.cut` | `foxos presentation cut cut` | 主界面 > Cut | — | 点击「Cut」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.copy` | `foxos presentation copy copy` | 主界面 > Copy | — | 点击「Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-painter.activate` | `foxos presentation format-painter activate` | 主界面 > Format Painter | — | 点击「Format Painter」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide.create` | `foxos presentation slide create` | 主界面 > New Slide | — | 点击「New Slide」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-layouts.create` | `foxos presentation slide-layouts create` | 主界面 > New Slide layouts | — | 点击「New Slide layouts」（button） | 可能（应用提供撤销，未逐项验证） |
| `layout.activate` | `foxos presentation layout activate` | 主界面 > Layout | — | 点击「Layout」（button） | 可能（应用提供撤销，未逐项验证） |
| `reset.reset` | `foxos presentation reset reset` | 主界面 > Reset | — | 点击「Reset」（button） | 可能（应用提供撤销，未逐项验证） |
| `section.activate` | `foxos presentation section activate` | 主界面 > Section | — | 点击「Section」（button） | 可能（应用提供撤销，未逐项验证） |
| `font.set` | `foxos presentation font set` | 主界面 > Font | `value`（必填）, `submit` | 把「Font」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `font-list.activate` | `foxos presentation font-list activate` | 主界面 > Font list | — | 点击「Font list」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-size.set` | `foxos presentation font-size set` | 主界面 > Font Size | `value`（必填）, `submit` | 把「Font Size」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `font-size-list.activate` | `foxos presentation font-size-list activate` | 主界面 > Font Size list | — | 点击「Font Size list」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-font-size.activate` | `foxos presentation increase-font-size activate` | 主界面 > Increase Font Size | — | 点击「Increase Font Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `formatting.clear` | `foxos presentation formatting clear` | 主界面 > Clear All Formatting | — | 点击「Clear All Formatting」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-settings.activate` | `foxos presentation font-settings activate` | 主界面 > Font Settings | — | 点击「Font Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `bold.format` | `foxos presentation bold format` | 主界面 > Bold | — | 点击「Bold」（button） | 可能（应用提供撤销，未逐项验证） |
| `italic.format` | `foxos presentation italic format` | 主界面 > Italic | — | 点击「Italic」（button） | 可能（应用提供撤销，未逐项验证） |
| `underline.format` | `foxos presentation underline format` | 主界面 > Underline | — | 点击「Underline」（button） | 可能（应用提供撤销，未逐项验证） |
| `strikethrough.format` | `foxos presentation strikethrough format` | 主界面 > Strikethrough | — | 点击「Strikethrough」（button） | 可能（应用提供撤销，未逐项验证） |
| `superscript.activate` | `foxos presentation superscript activate` | 主界面 > Superscript | — | 点击「Superscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `subscript.activate` | `foxos presentation subscript activate` | 主界面 > Subscript | — | 点击「Subscript」（button） | 可能（应用提供撤销，未逐项验证） |
| `character-spacing.activate` | `foxos presentation character-spacing activate` | 主界面 > Character Spacing | — | 点击「Character Spacing」（button） | 可能（应用提供撤销，未逐项验证） |
| `case.update` | `foxos presentation case update` | 主界面 > Change Case | — | 点击「Change Case」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-highlight-color.activate` | `foxos presentation text-highlight-color activate` | 主界面 > Text Highlight Color | — | 点击「Text Highlight Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `highlight-colors.activate` | `foxos presentation highlight-colors activate` | 主界面 > Highlight colors | — | 点击「Highlight colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-color.activate` | `foxos presentation font-color activate` | 主界面 > Font Color | — | 点击「Font Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `font-colors.activate` | `foxos presentation font-colors activate` | 主界面 > Font colors | — | 点击「Font colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `bullets.activate` | `foxos presentation bullets activate` | 主界面 > Bullets | — | 点击「Bullets」（button） | 可能（应用提供撤销，未逐项验证） |
| `bullet-styles.activate` | `foxos presentation bullet-styles activate` | 主界面 > Bullet styles | — | 点击「Bullet styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbering.activate` | `foxos presentation numbering activate` | 主界面 > Numbering | — | 点击「Numbering」（button） | 可能（应用提供撤销，未逐项验证） |
| `numbering-styles.activate` | `foxos presentation numbering-styles activate` | 主界面 > Numbering styles | — | 点击「Numbering styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `increase-list-level.activate` | `foxos presentation increase-list-level activate` | 主界面 > Increase List Level | — | 点击「Increase List Level」（button） | 可能（应用提供撤销，未逐项验证） |
| `line-spacing.activate` | `foxos presentation line-spacing activate` | 主界面 > Line Spacing | — | 点击「Line Spacing」（button） | 可能（应用提供撤销，未逐项验证） |
| `columns.activate` | `foxos presentation columns activate` | 主界面 > Columns | — | 点击「Columns」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph-settings.activate` | `foxos presentation paragraph-settings activate` | 主界面 > Paragraph Settings | — | 点击「Paragraph Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `left.align` | `foxos presentation left align` | 主界面 > Align Left | — | 点击「Align Left」（button） | 可能（应用提供撤销，未逐项验证） |
| `center.activate` | `foxos presentation center activate` | 主界面 > Center | — | 点击「Center」（button） | 可能（应用提供撤销，未逐项验证） |
| `right.align` | `foxos presentation right align` | 主界面 > Align Right | — | 点击「Align Right」（button） | 可能（应用提供撤销，未逐项验证） |
| `justify.activate` | `foxos presentation justify activate` | 主界面 > Justify | — | 点击「Justify」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-direction.activate` | `foxos presentation text-direction activate` | 主界面 > Text Direction | — | 点击「Text Direction」（button） | 可能（应用提供撤销，未逐项验证） |
| `text.align` | `foxos presentation text align` | 主界面 > Align Text | — | 点击「Align Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `convert-smartart.activate` | `foxos presentation convert-smartart activate` | 主界面 > Convert to SmartArt | — | 点击「Convert to SmartArt」（button） | 可能（应用提供撤销，未逐项验证） |
| `insert-3.create` | `foxos presentation insert-3 create` | 主界面 > Insert > Insert | — | 点击「Insert」（button） | 可能（应用提供撤销，未逐项验证） |
| `drawing.activate` | `foxos presentation drawing activate` | 主界面 > Drawing > Drawing | — | 点击「Drawing」（button） | 可能（应用提供撤销，未逐项验证） |
| `editing.activate` | `foxos presentation editing activate` | 主界面 > Editing > Editing | — | 点击「Editing」（button） | 可能（应用提供撤销，未逐项验证） |
| `designer.activate` | `foxos presentation designer activate` | 主界面 > Designer > Designer | — | 点击「Designer」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-thumbnails.resize` | `foxos presentation slide-thumbnails resize` | 主界面 > Resize slide thumbnails | — | 点击「Resize slide thumbnails」（separator） | 可能（应用提供撤销，未逐项验证） |
| `notes.resize` | `foxos presentation notes resize` | 主界面 > Resize notes | — | 点击「Resize notes」（separator） | 可能（应用提供撤销，未逐项验证） |
| `speaker-notes.set` | `foxos presentation speaker-notes set` | 主界面 > main > Speaker notes | `value`（必填）, `submit` | 把「Speaker notes」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `assistant.resize` | `foxos presentation assistant resize` | 主界面 > Resize the assistant | — | 点击「Resize the assistant」（separator） | 可能（应用提供撤销，未逐项验证） |
| `chat.create` | `foxos presentation chat create` | 主界面 > New chat | — | 点击「New chat」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant-settings.activate` | `foxos presentation assistant-settings activate` | 主界面 > Assistant settings | — | 点击「Assistant settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant.close` | `foxos presentation assistant close` | 主界面 > Close the assistant | — | 点击「Close the assistant」（button） | 不适用（只读） |
| `turn-notes-into-slides.activate` | `foxos presentation turn-notes-into-slides activate` | 主界面 > Suggestions > Turn my notes into slides | — | 点击「Turn my notes into slides」（button） | 可能（应用提供撤销，未逐项验证） |
| `message-assistant.set` | `foxos presentation message-assistant set` | 主界面 > Message the assistant | `value`（必填）, `submit` | 把「Message the assistant」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `send.send` | `foxos presentation send send` | 主界面 > Send | — | 点击「Send」（button） | 可能（应用提供撤销，未逐项验证） |
| `english-united-states.activate` | `foxos presentation english-united-states activate` | 主界面 > footer > English (United States) | — | 点击「English (United States)」（button） | 可能（应用提供撤销，未逐项验证） |
| `notes.activate` | `foxos presentation notes activate` | 主界面 > footer > Notes | — | 点击「Notes」（button） | 可能（应用提供撤销，未逐项验证） |
| `comments.activate` | `foxos presentation comments activate` | 主界面 > footer > Comments | — | 点击「Comments」（button） | 可能（应用提供撤销，未逐项验证） |
| `normal.activate` | `foxos presentation normal activate` | 主界面 > Normal | — | 点击「Normal」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-sorter.activate` | `foxos presentation slide-sorter activate` | 主界面 > Slide Sorter | — | 点击「Slide Sorter」（button） | 可能（应用提供撤销，未逐项验证） |
| `reading-view.activate` | `foxos presentation reading-view activate` | 主界面 > Reading View | — | 点击「Reading View」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-show-2.activate` | `foxos presentation slide-show-2 activate` | 主界面 > Slide Show | — | 点击「Slide Show」（button） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-out` | `foxos presentation view zoom-out` | 主界面 > Zoom out | — | 点击「Zoom out」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom.set` | `foxos presentation zoom set` | 主界面 > Zoom | `value`（必填）, `submit` | 把「Zoom」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-` | `foxos presentation view zoom-` | 主界面 > Zoom in | — | 点击「Zoom in」（button） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-level` | `foxos presentation view zoom-level` | 主界面 > Zoom level | — | 点击「Zoom level」（button） | 可能（应用提供撤销，未逐项验证） |
| `fit-slide-current-window.activate` | `foxos presentation fit-slide-current-window activate` | 主界面 > Fit slide to current window | — | 点击「Fit slide to current window」（button） | 可能（应用提供撤销，未逐项验证） |
| `close.close` | `foxos presentation close close` | Rename “Untitled presentation” > Close | — | 点击「Close」（button） | 不适用（只读） |
| `presentation-name.set` | `foxos presentation presentation-name set` | Rename “Untitled presentation” > Presentation name | `value`（必填）, `submit` | 把「Presentation name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `cancel.cancel` | `foxos presentation cancel cancel` | Rename “Untitled presentation” > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `appearance.activate` | `foxos presentation appearance activate` | local: account and settings > Account > Appearance | — | 点击「Appearance」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcuts.activate` | `foxos presentation keyboard-shortcuts activate` | local: account and settings > Account > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `table.activate` | `foxos presentation table activate` | Insert > Table | — | 点击「Table」（button） | 可能（应用提供撤销，未逐项验证） |
| `pictures.activate` | `foxos presentation pictures activate` | Insert > Pictures | — | 点击「Pictures」（button） | 可能（应用提供撤销，未逐项验证） |
| `picture-sources.activate` | `foxos presentation picture-sources activate` | Insert > Picture sources | — | 点击「Picture sources」（button） | 可能（应用提供撤销，未逐项验证） |
| `screenshot.activate` | `foxos presentation screenshot activate` | Insert > Screenshot | — | 点击「Screenshot」（button） | 可能（应用提供撤销，未逐项验证） |
| `screenshot-options.activate` | `foxos presentation screenshot-options activate` | Insert > Screenshot options | — | 点击「Screenshot options」（button） | 可能（应用提供撤销，未逐项验证） |
| `photo-album.activate` | `foxos presentation photo-album activate` | Insert > Photo Album | — | 点击「Photo Album」（button） | 可能（应用提供撤销，未逐项验证） |
| `shapes.activate` | `foxos presentation shapes activate` | Insert > Shapes | — | 点击「Shapes」（button） | 可能（应用提供撤销，未逐项验证） |
| `icons.activate` | `foxos presentation icons activate` | Insert > Icons | — | 点击「Icons」（button） | 可能（应用提供撤销，未逐项验证） |
| `smartart.activate` | `foxos presentation smartart activate` | Insert > SmartArt | — | 点击「SmartArt」（button） | 可能（应用提供撤销，未逐项验证） |
| `chart.activate` | `foxos presentation chart activate` | Insert > Chart | — | 点击「Chart」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom.zoom` | `foxos presentation zoom zoom` | Insert > Zoom | — | 点击「Zoom」（button） | 不适用（只读） |
| `link.activate` | `foxos presentation link activate` | Insert > Link | — | 点击「Link」（button） | 可能（应用提供撤销，未逐项验证） |
| `action.activate` | `foxos presentation action activate` | Insert > Action | — | 点击「Action」（button） | 可能（应用提供撤销，未逐项验证） |
| `action-options.activate` | `foxos presentation action-options activate` | Insert > Action options | — | 点击「Action options」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.activate` | `foxos presentation comment activate` | Insert > Comment | — | 点击「Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-box.activate` | `foxos presentation text-box activate` | Insert > Text Box | — | 点击「Text Box」（button） | 可能（应用提供撤销，未逐项验证） |
| `header-footer.activate` | `foxos presentation header-footer activate` | Insert > Header & Footer | — | 点击「Header & Footer」（button） | 可能（应用提供撤销，未逐项验证） |
| `wordart.activate` | `foxos presentation wordart activate` | Insert > WordArt | — | 点击「WordArt」（button） | 可能（应用提供撤销，未逐项验证） |
| `date-time.activate` | `foxos presentation date-time activate` | Insert > Date & Time | — | 点击「Date & Time」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-number.activate` | `foxos presentation slide-number activate` | Insert > Slide Number | — | 点击「Slide Number」（button） | 可能（应用提供撤销，未逐项验证） |
| `object.activate` | `foxos presentation object activate` | Insert > Object | — | 点击「Object」（button） | 可能（应用提供撤销，未逐项验证） |
| `symbols.activate` | `foxos presentation symbols activate` | Insert > Symbols > Symbols | — | 点击「Symbols」（button） | 可能（应用提供撤销，未逐项验证） |
| `media.activate` | `foxos presentation media activate` | Insert > Media > Media | — | 点击「Media」（button） | 可能（应用提供撤销，未逐项验证） |
| `select.select` | `foxos presentation select select` | Draw > Select | — | 点击「Select」（button） | 不适用（只读） |
| `eraser.activate` | `foxos presentation eraser activate` | Draw > Eraser | — | 点击「Eraser」（button） | 可能（应用提供撤销，未逐项验证） |
| `eraser-options.activate` | `foxos presentation eraser-options activate` | Draw > Eraser options | — | 点击「Eraser options」（button） | 可能（应用提供撤销，未逐项验证） |
| `lasso-select.activate` | `foxos presentation lasso-select activate` | Draw > Lasso Select | — | 点击「Lasso Select」（button） | 可能（应用提供撤销，未逐项验证） |
| `pen.create` | `foxos presentation pen create` | Draw > Add Pen | — | 点击「Add Pen」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-text.activate` | `foxos presentation ink-text activate` | Draw > Ink to Text | — | 点击「Ink to Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-shape.activate` | `foxos presentation ink-shape activate` | Draw > Ink to Shape | — | 点击「Ink to Shape」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-shape-options.activate` | `foxos presentation ink-shape-options activate` | Draw > Ink to Shape options | — | 点击「Ink to Shape options」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-math.activate` | `foxos presentation ink-math activate` | Draw > Ink to Math | — | 点击「Ink to Math」（button） | 可能（应用提供撤销，未逐项验证） |
| `ink-replay.activate` | `foxos presentation ink-replay activate` | Draw > Ink Replay | — | 点击「Ink Replay」（button） | 可能（应用提供撤销，未逐项验证） |
| `ruler.activate` | `foxos presentation ruler activate` | Draw > Ruler | — | 点击「Ruler」（button） | 可能（应用提供撤销，未逐项验证） |
| `touch.draw` | `foxos presentation touch draw` | Draw > Draw with Touch | — | 点击「Draw with Touch」（button） | 可能（应用提供撤销，未逐项验证） |
| `default-theme.activate` | `foxos presentation default-theme activate` | Design > Default Theme | — | 点击「Default Theme」（option） | 可能（应用提供撤销，未逐项验证） |
| `paper.activate` | `foxos presentation paper activate` | Design > Paper | — | 点击「Paper」（option） | 可能（应用提供撤销，未逐项验证） |
| `studio.activate` | `foxos presentation studio activate` | Design > Studio | — | 点击「Studio」（option） | 可能（应用提供撤销，未逐项验证） |
| `cobalt.activate` | `foxos presentation cobalt activate` | Design > Cobalt | — | 点击「Cobalt」（option） | 可能（应用提供撤销，未逐项验证） |
| `row-themes.previous` | `foxos presentation row-themes previous` | Design > Previous row of Themes | — | 点击「Previous row of Themes」（button） | 不适用（只读） |
| `row-themes.next` | `foxos presentation row-themes next` | Design > Next row of Themes | — | 点击「Next row of Themes」（button） | 不适用（只读） |
| `themes.show` | `foxos presentation themes show` | Design > More Themes | — | 点击「More Themes」（button），切换到该视图 | 不适用（只读） |
| `default.activate` | `foxos presentation default activate` | Design > Default | — | 点击「Default」（option） | 可能（应用提供撤销，未逐项验证） |
| `default-dark.activate` | `foxos presentation default-dark activate` | Design > Default (Dark) | — | 点击「Default (Dark)」（option） | 可能（应用提供撤销，未逐项验证） |
| `default-accents-turned.activate` | `foxos presentation default-accents-turned activate` | Design > Default (Accents turned) | — | 点击「Default (Accents turned)」（option） | 可能（应用提供撤销，未逐项验证） |
| `default-accents-turned-twice.activate` | `foxos presentation default-accents-turned-twice activate` | Design > Default (Accents turned twice) | — | 点击「Default (Accents turned twice)」（option） | 可能（应用提供撤销，未逐项验证） |
| `row-variants.previous` | `foxos presentation row-variants previous` | Design > Previous row of Variants | — | 点击「Previous row of Variants」（button） | 不适用（只读） |
| `row-variants.next` | `foxos presentation row-variants next` | Design > Next row of Variants | — | 点击「Next row of Variants」（button） | 不适用（只读） |
| `variants.show` | `foxos presentation variants show` | Design > More Variants | — | 点击「More Variants」（button），切换到该视图 | 不适用（只读） |
| `colors.activate` | `foxos presentation colors activate` | Design > Colors | — | 点击「Colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `fonts.activate` | `foxos presentation fonts activate` | Design > Fonts | — | 点击「Fonts」（button） | 可能（应用提供撤销，未逐项验证） |
| `effects.activate` | `foxos presentation effects activate` | Design > Effects | — | 点击「Effects」（button） | 可能（应用提供撤销，未逐项验证） |
| `background-styles.activate` | `foxos presentation background-styles activate` | Design > Background Styles | — | 点击「Background Styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-size.activate` | `foxos presentation slide-size activate` | Design > Slide Size | — | 点击「Slide Size」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-background.activate` | `foxos presentation format-background activate` | Design > Format Background | — | 点击「Format Background」（button） | 可能（应用提供撤销，未逐项验证） |
| `hide-background-graphics.toggle` | `foxos presentation hide-background-graphics toggle` | Design > Customize > Hide Background Graphics | — | 切换「Hide Background Graphics」 | 可能（应用提供撤销，未逐项验证） |
| `design-ideas.activate` | `foxos presentation design-ideas activate` | Design > Design Ideas | — | 点击「Design Ideas」（button） | 可能（应用提供撤销，未逐项验证） |
| `preview.activate` | `foxos presentation preview activate` | Transitions > Preview | — | 点击「Preview」（button） | 可能（应用提供撤销，未逐项验证） |
| `none.activate` | `foxos presentation none activate` | Transitions > None | — | 点击「None」（option） | 可能（应用提供撤销，未逐项验证） |
| `morph.activate` | `foxos presentation morph activate` | Transitions > Morph | — | 点击「Morph」（option） | 可能（应用提供撤销，未逐项验证） |
| `fade.activate` | `foxos presentation fade activate` | Transitions > Fade | — | 点击「Fade」（option） | 可能（应用提供撤销，未逐项验证） |
| `push.activate` | `foxos presentation push activate` | Transitions > Push | — | 点击「Push」（option） | 可能（应用提供撤销，未逐项验证） |
| `wipe.activate` | `foxos presentation wipe activate` | Transitions > Wipe | — | 点击「Wipe」（option） | 可能（应用提供撤销，未逐项验证） |
| `split.activate` | `foxos presentation split activate` | Transitions > Split | — | 点击「Split」（option） | 可能（应用提供撤销，未逐项验证） |
| `reveal.activate` | `foxos presentation reveal activate` | Transitions > Reveal | — | 点击「Reveal」（option） | 可能（应用提供撤销，未逐项验证） |
| `transitions-cut.cut` | `foxos presentation transitions-cut cut` | Transitions > Cut | — | 点击「Cut」（option） | 可能（应用提供撤销，未逐项验证） |
| `random-bars.activate` | `foxos presentation random-bars activate` | Transitions > Random Bars | — | 点击「Random Bars」（option） | 可能（应用提供撤销，未逐项验证） |
| `row-transitions.previous` | `foxos presentation row-transitions previous` | Transitions > Previous row of Transitions | — | 点击「Previous row of Transitions」（button） | 不适用（只读） |
| `row-transitions.next` | `foxos presentation row-transitions next` | Transitions > Next row of Transitions | — | 点击「Next row of Transitions」（button） | 不适用（只读） |
| `transitions-2.show` | `foxos presentation transitions-2 show` | Transitions > More Transitions | — | 点击「More Transitions」（button），切换到该视图 | 不适用（只读） |
| `effect-options.activate` | `foxos presentation effect-options activate` | Transitions > Effect Options | — | 点击「Effect Options」（button） | 可能（应用提供撤销，未逐项验证） |
| `sound.activate` | `foxos presentation sound activate` | Transitions > Sound | — | 点击「Sound」（button） | 可能（应用提供撤销，未逐项验证） |
| `duration.set` | `foxos presentation duration set` | Transitions > Duration | `value`（必填）, `submit` | 把「Duration」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `increase-duration.activate` | `foxos presentation increase-duration activate` | Transitions > Increase Duration | — | 点击「Increase Duration」（button） | 可能（应用提供撤销，未逐项验证） |
| `apply.confirm` | `foxos presentation apply confirm` | Transitions > Apply To All | — | 点击「Apply To All」（button） | 可能（应用提供撤销，未逐项验证） |
| `mouse-click.toggle` | `foxos presentation mouse-click toggle` | Transitions > Timing > On Mouse Click | — | 切换「On Mouse Click」 | 可能（应用提供撤销，未逐项验证） |
| `after.toggle` | `foxos presentation after toggle` | Transitions > Timing > After | — | 切换「After」 | 可能（应用提供撤销，未逐项验证） |
| `advance-after-seconds.set` | `foxos presentation advance-after-seconds set` | Transitions > Advance after (seconds) | `value`（必填）, `submit` | 把「Advance after (seconds)」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `increase-advance-after.activate` | `foxos presentation increase-advance-after activate` | Transitions > Increase Advance after | — | 点击「Increase Advance after」（button） | 可能（应用提供撤销，未逐项验证） |
| `preview-options.activate` | `foxos presentation preview-options activate` | Animations > Preview options | — | 点击「Preview options」（button） | 可能（应用提供撤销，未逐项验证） |
| `appear.activate` | `foxos presentation appear activate` | Animations > Appear | — | 点击「Appear」（option） | 可能（应用提供撤销，未逐项验证） |
| `fly.activate` | `foxos presentation fly activate` | Animations > Fly In | — | 点击「Fly In」（option） | 可能（应用提供撤销，未逐项验证） |
| `float.activate` | `foxos presentation float activate` | Animations > Float In | — | 点击「Float In」（option） | 可能（应用提供撤销，未逐项验证） |
| `shape.activate` | `foxos presentation shape activate` | Animations > Shape | — | 点击「Shape」（option） | 可能（应用提供撤销，未逐项验证） |
| `row-animations.previous` | `foxos presentation row-animations previous` | Animations > Previous row of Animations | — | 点击「Previous row of Animations」（button） | 不适用（只读） |
| `row-animations.next` | `foxos presentation row-animations next` | Animations > Next row of Animations | — | 点击「Next row of Animations」（button） | 不适用（只读） |
| `animations-2.show` | `foxos presentation animations-2 show` | Animations > More Animations | — | 点击「More Animations」（button），切换到该视图 | 不适用（只读） |
| `animation.create` | `foxos presentation animation create` | Animations > Add Animation | — | 点击「Add Animation」（button） | 可能（应用提供撤销，未逐项验证） |
| `animation-pane.activate` | `foxos presentation animation-pane activate` | Animations > Animation Pane | — | 点击「Animation Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `trigger.activate` | `foxos presentation trigger activate` | Animations > Trigger | — | 点击「Trigger」（button） | 可能（应用提供撤销，未逐项验证） |
| `animation-painter.activate` | `foxos presentation animation-painter activate` | Animations > Animation Painter | — | 点击「Animation Painter」（button） | 可能（应用提供撤销，未逐项验证） |
| `start.set` | `foxos presentation start set` | Animations > Start | `value`（必填）, `submit` | 把「Start」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `list.start` | `foxos presentation list start` | Animations > Start list | — | 点击「Start list」（button） | 可能（应用提供撤销，未逐项验证） |
| `delay.set` | `foxos presentation delay set` | Animations > Delay | `value`（必填）, `submit` | 把「Delay」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `increase-delay.activate` | `foxos presentation increase-delay activate` | Animations > Increase Delay | — | 点击「Increase Delay」（button） | 可能（应用提供撤销，未逐项验证） |
| `earlier.move` | `foxos presentation earlier move` | Animations > Move Earlier | — | 点击「Move Earlier」（button） | 可能（应用提供撤销，未逐项验证） |
| `later.move` | `foxos presentation later move` | Animations > Move Later | — | 点击「Move Later」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-start.play` | `foxos presentation from-start play` | Slide Show > Play from Start | — | 点击「Play from Start」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-current-slide.play` | `foxos presentation from-current-slide play` | Slide Show > Play from Current Slide | — | 点击「Play from Current Slide」（button） | 可能（应用提供撤销，未逐项验证） |
| `presenter-view.activate` | `foxos presentation presenter-view activate` | Slide Show > Presenter View | — | 点击「Presenter View」（button） | 可能（应用提供撤销，未逐项验证） |
| `custom-show.activate` | `foxos presentation custom-show activate` | Slide Show > Custom Show | — | 点击「Custom Show」（button） | 可能（应用提供撤销，未逐项验证） |
| `set-up-slide-show.activate` | `foxos presentation set-up-slide-show activate` | Slide Show > Set Up Slide Show | — | 点击「Set Up Slide Show」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide.hide` | `foxos presentation slide hide` | Slide Show > Hide Slide | — | 点击「Hide Slide」（button） | 不适用（只读） |
| `rehearse-timings.activate` | `foxos presentation rehearse-timings activate` | Slide Show > Rehearse Timings | — | 点击「Rehearse Timings」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-show-record.record` | `foxos presentation slide-show-record record` | Slide Show > Record | — | 点击「Record」（button） | 可能（应用提供撤销，未逐项验证） |
| `options.record` | `foxos presentation options record` | Slide Show > Record options | — | 点击「Record options」（button） | 可能（应用提供撤销，未逐项验证） |
| `play-narrations.toggle` | `foxos presentation play-narrations toggle` | Slide Show > Set Up > Play Narrations | — | 切换「Play Narrations」 | 可能（应用提供撤销，未逐项验证） |
| `use-timings.toggle` | `foxos presentation use-timings toggle` | Slide Show > Set Up > Use Timings | — | 切换「Use Timings」 | 可能（应用提供撤销，未逐项验证） |
| `show-media-controls.toggle` | `foxos presentation show-media-controls toggle` | Slide Show > Set Up > Show Media Controls | — | 切换「Show Media Controls」 | 可能（应用提供撤销，未逐项验证） |
| `always-use-subtitles.toggle` | `foxos presentation always-use-subtitles toggle` | Slide Show > Captions & Subtitles > Always Use Subtitles | — | 切换「Always Use Subtitles」 | 可能（应用提供撤销，未逐项验证） |
| `subtitle-settings.activate` | `foxos presentation subtitle-settings activate` | Slide Show > Subtitle Settings | — | 点击「Subtitle Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `live-camera.activate` | `foxos presentation live-camera activate` | Record > Live Camera | — | 点击「Live Camera」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-beginning.activate` | `foxos presentation from-beginning activate` | Record > From Beginning | — | 点击「From Beginning」（button） | 可能（应用提供撤销，未逐项验证） |
| `from-current-slide.activate` | `foxos presentation from-current-slide activate` | Record > From Current Slide | — | 点击「From Current Slide」（button） | 可能（应用提供撤销，未逐项验证） |
| `recording.clear` | `foxos presentation recording clear` | Record > Clear Recording | — | 点击「Clear Recording」（button） | 可能（应用提供撤销，未逐项验证） |
| `camera.reset` | `foxos presentation camera reset` | Record > Reset to Camera | — | 点击「Reset to Camera」（button） | 可能（应用提供撤销，未逐项验证） |
| `video.export` | `foxos presentation video export` | Record > Export to Video | — | 点击「Export to Video」（button） | 可能（应用提供撤销，未逐项验证） |
| `spelling.activate` | `foxos presentation spelling activate` | Review > Spelling | — | 点击「Spelling」（button） | 可能（应用提供撤销，未逐项验证） |
| `thesaurus.activate` | `foxos presentation thesaurus activate` | Review > Thesaurus | — | 点击「Thesaurus」（button） | 可能（应用提供撤销，未逐项验证） |
| `accessibility.run` | `foxos presentation accessibility run` | Review > Check Accessibility | — | 点击「Check Accessibility」（button） | 可能（应用提供撤销，未逐项验证） |
| `accessibility-options.activate` | `foxos presentation accessibility-options activate` | Review > Accessibility options | — | 点击「Accessibility options」（button） | 可能（应用提供撤销，未逐项验证） |
| `alt-text.activate` | `foxos presentation alt-text activate` | Review > Alt Text | — | 点击「Alt Text」（button） | 可能（应用提供撤销，未逐项验证） |
| `translate.activate` | `foxos presentation translate activate` | Review > Translate | — | 点击「Translate」（button） | 可能（应用提供撤销，未逐项验证） |
| `language.activate` | `foxos presentation language activate` | Review > Language | — | 点击「Language」（button） | 可能（应用提供撤销，未逐项验证） |
| `comment.create` | `foxos presentation comment create` | Review > New Comment | — | 点击「New Comment」（button） | 可能（应用提供撤销，未逐项验证） |
| `delete.delete` | `foxos presentation delete delete` | Review > Delete | — | 点击「Delete」（button） | 可能（应用提供撤销，未逐项验证） |
| `previous.previous` | `foxos presentation previous previous` | Review > Previous | — | 点击「Previous」（button） | 不适用（只读） |
| `next.next` | `foxos presentation next next` | Review > Next | — | 点击「Next」（button） | 不适用（只读） |
| `comments.show` | `foxos presentation comments show` | Review > Show Comments | — | 点击「Show Comments」（button），切换到该视图 | 不适用（只读） |
| `comments-options.show` | `foxos presentation comments-options show` | Review > Show Comments options | — | 点击「Show Comments options」（button），切换到该视图 | 不适用（只读） |
| `compare.activate` | `foxos presentation compare activate` | Review > Compare | — | 点击「Compare」（button） | 可能（应用提供撤销，未逐项验证） |
| `always-open-read-only.activate` | `foxos presentation always-open-read-only activate` | Review > Always Open Read-Only | — | 点击「Always Open Read-Only」（button） | 可能（应用提供撤销，未逐项验证） |
| `outline-view.activate` | `foxos presentation outline-view activate` | View > Outline View | — | 点击「Outline View」（button） | 可能（应用提供撤销，未逐项验证） |
| `notes-page.activate` | `foxos presentation notes-page activate` | View > Notes Page | — | 点击「Notes Page」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-master.activate` | `foxos presentation slide-master activate` | View > Slide Master | — | 点击「Slide Master」（button） | 可能（应用提供撤销，未逐项验证） |
| `handout-master.activate` | `foxos presentation handout-master activate` | View > Handout Master | — | 点击「Handout Master」（button） | 可能（应用提供撤销，未逐项验证） |
| `notes-master.activate` | `foxos presentation notes-master activate` | View > Notes Master | — | 点击「Notes Master」（button） | 可能（应用提供撤销，未逐项验证） |
| `ruler.toggle` | `foxos presentation ruler toggle` | View > Show > Ruler | — | 切换「Ruler」 | 可能（应用提供撤销，未逐项验证） |
| `gridlines.toggle` | `foxos presentation gridlines toggle` | View > Show > Gridlines | — | 切换「Gridlines」 | 可能（应用提供撤销，未逐项验证） |
| `guides.toggle` | `foxos presentation guides toggle` | View > Show > Guides | — | 切换「Guides」 | 可能（应用提供撤销，未逐项验证） |
| `view-notes.activate` | `foxos presentation view-notes activate` | View > Notes | — | 点击「Notes」（button） | 可能（应用提供撤销，未逐项验证） |
| `grid-settings.activate` | `foxos presentation grid-settings activate` | View > Grid Settings | — | 点击「Grid Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `fit-window.activate` | `foxos presentation fit-window activate` | View > Fit to Window | — | 点击「Fit to Window」（button） | 可能（应用提供撤销，未逐项验证） |
| `color.activate` | `foxos presentation color activate` | View > Color | — | 点击「Color」（button） | 可能（应用提供撤销，未逐项验证） |
| `grayscale.activate` | `foxos presentation grayscale activate` | View > Grayscale | — | 点击「Grayscale」（button） | 可能（应用提供撤销，未逐项验证） |
| `black-white.activate` | `foxos presentation black-white activate` | View > Black and White | — | 点击「Black and White」（button） | 可能（应用提供撤销，未逐项验证） |
| `slide-thumbnails.activate` | `foxos presentation slide-thumbnails activate` | View > Slide Thumbnails | — | 点击「Slide Thumbnails」（button） | 可能（应用提供撤销，未逐项验证） |
| `format-pane.activate` | `foxos presentation format-pane activate` | View > Format Pane | — | 点击「Format Pane」（button） | 可能（应用提供撤销，未逐项验证） |
| `ai-assistant.activate` | `foxos presentation ai-assistant activate` | View > AI Assistant | — | 点击「AI Assistant」（button） | 可能（应用提供撤销，未逐项验证） |
| `pastectrlv.activate` | `foxos presentation pastectrlv activate` | Paste options > Paste options > PasteCtrl+V | — | 点击「PasteCtrl+V」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `as-text-only.paste` | `foxos presentation as-text-only paste` | Paste options > Paste options > Paste as Text Only | — | 点击「Paste as Text Only」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `duplicatectrld.activate` | `foxos presentation duplicatectrld activate` | Paste options > Paste options > DuplicateCtrl+D | — | 点击「DuplicateCtrl+D」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `special.paste` | `foxos presentation special paste` | Paste options > Paste options > Paste Special… | — | 点击「Paste Special…」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `match-formatting.paste` | `foxos presentation match-formatting paste` | Paste options > Paste options > Paste and Match Formatting | — | 点击「Paste and Match Formatting」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `selection.select-all` | `foxos presentation selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.duplicate` | `foxos presentation selection duplicate` | 键盘 mod+d | — | 在当前焦点上按 mod+d（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `shortcut.key-j` | `foxos presentation shortcut key-j` | 键盘 mod+j | — | 在当前焦点上按 mod+j（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `command-palette.show` | `foxos presentation command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/main.js 中定义） | 不适用 |
| `document.open` | `foxos presentation document open` | 键盘 mod+o | — | 在当前焦点上按 mod+o（src/main.js 中定义） | 不适用 |
| `document.print` | `foxos presentation document print` | 键盘 mod+p | — | 在当前焦点上按 mod+p（src/main.js 中定义） | 不适用 |
| `document.save` | `foxos presentation document save` | 键盘 mod+s | — | 在当前焦点上按 mod+s（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `clipboard.paste` | `foxos presentation clipboard paste` | 键盘 mod+v | — | 在当前焦点上按 mod+v（src/main.js 中定义） | 可能（应用提供撤销，未逐项验证） |
