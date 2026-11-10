# CAD（cad）操作清单

分组：engineering · 替代 AutoCAD, DraftSight, BricsCAD · 许可证 AGPL-3.0-only · 页面标题「CAD」

共 180 个操作，全部有语义命令（`foxos cad <资源> <动词>`，MCP 工具 `cad.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `arc.select` | `foxos cad arc select` | 主界面 > arc, # | `target`（必填） | 点击名称匹配的「arc, #」项（button） | 不适用（只读） |
| `application-menu.select` | `foxos cad application-menu select` | Application menu > Application menu > # | `target`（必填） | 点击名称匹配的「#」项（menuitem） | 不适用（只读） |
| `circle-options.select` | `foxos cad circle-options select` | Circle options > Circle options > # | `target`（必填） | 点击名称匹配的「#」项（menuitem） | 不适用（只读） |
| `arc-options.select` | `foxos cad arc-options select` | Arc options > Arc options > # | `target`（必填） | 点击名称匹配的「#」项（menuitem） | 不适用（只读） |
| `application-menu.activate` | `foxos cad application-menu activate` | 主界面 > Application menu | — | 点击「Application menu」（button） | 可能（应用提供撤销，未逐项验证） |
| `drawing.create` | `foxos cad drawing create` | 主界面 > New drawing | — | 点击「New drawing」（button） | 可能（应用提供撤销，未逐项验证） |
| `open.open` | `foxos cad open open` | 主界面 > Open | — | 点击「Open」（button） | 不适用（只读） |
| `save.save` | `foxos cad save save` | 主界面 > Save | — | 点击「Save」（button） | 可能（应用提供撤销，未逐项验证） |
| `undo.undo` | `foxos cad undo undo` | 主界面 > Undo | — | 点击「Undo」（button） | 可能（应用提供撤销，未逐项验证） |
| `redo.redo` | `foxos cad redo redo` | 主界面 > Redo | — | 点击「Redo」（button） | 可能（应用提供撤销，未逐项验证） |
| `plot.activate` | `foxos cad plot activate` | 主界面 > Plot | — | 点击「Plot」（button） | 可能（应用提供撤销，未逐项验证） |
| `commands.search` | `foxos cad commands search` | 主界面 > Search commands | — | 点击「Search commands」（button） | 不适用（只读） |
| `theme.activate` | `foxos cad theme activate` | 主界面 > Theme | — | 点击「Theme」（button） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos cad help show` | 主界面 > Help | — | 点击「Help」（button），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos cad source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `home.show` | `foxos cad home show` | 主界面 > Ribbon > Home | — | 点击「Home」（tab），切换到该视图 | 不适用（只读） |
| `insert.create` | `foxos cad insert create` | 主界面 > Ribbon > Insert | — | 点击「Insert」（tab） | 可能（应用提供撤销，未逐项验证） |
| `annotate.show` | `foxos cad annotate show` | 主界面 > Ribbon > Annotate | — | 点击「Annotate」（tab），切换到该视图 | 不适用（只读） |
| `view.show` | `foxos cad view show` | 主界面 > Ribbon > View | — | 点击「View」（tab），切换到该视图 | 不适用（只读） |
| `manage.show` | `foxos cad manage show` | 主界面 > Ribbon > Manage | — | 点击「Manage」（tab），切换到该视图 | 不适用（只读） |
| `output.show` | `foxos cad output show` | 主界面 > Ribbon > Output | — | 点击「Output」（tab），切换到该视图 | 不适用（只读） |
| `minimize-ribbon.activate` | `foxos cad minimize-ribbon activate` | 主界面 > Minimize the ribbon | — | 点击「Minimize the ribbon」（button） | 可能（应用提供撤销，未逐项验证） |
| `line.activate` | `foxos cad line activate` | 主界面 > Line | — | 点击「Line」（button） | 可能（应用提供撤销，未逐项验证） |
| `polyline.activate` | `foxos cad polyline activate` | 主界面 > Polyline | — | 点击「Polyline」（button） | 可能（应用提供撤销，未逐项验证） |
| `circle-center-radius.activate` | `foxos cad circle-center-radius activate` | 主界面 > Circle, Center, Radius | — | 点击「Circle, Center, Radius」（button） | 可能（应用提供撤销，未逐项验证） |
| `circle-options.activate` | `foxos cad circle-options activate` | 主界面 > Circle options | — | 点击「Circle options」（button） | 可能（应用提供撤销，未逐项验证） |
| `arc-options.activate` | `foxos cad arc-options activate` | 主界面 > Arc options | — | 点击「Arc options」（button） | 可能（应用提供撤销，未逐项验证） |
| `rectangle.activate` | `foxos cad rectangle activate` | 主界面 > Rectangle | — | 点击「Rectangle」（button） | 可能（应用提供撤销，未逐项验证） |
| `rectangle-options.activate` | `foxos cad rectangle-options activate` | 主界面 > Rectangle options | — | 点击「Rectangle options」（button） | 可能（应用提供撤销，未逐项验证） |
| `ellipse.activate` | `foxos cad ellipse activate` | 主界面 > Ellipse | — | 点击「Ellipse」（button） | 可能（应用提供撤销，未逐项验证） |
| `ellipse-options.activate` | `foxos cad ellipse-options activate` | 主界面 > Ellipse options | — | 点击「Ellipse options」（button） | 可能（应用提供撤销，未逐项验证） |
| `hatch.activate` | `foxos cad hatch activate` | 主界面 > Hatch | — | 点击「Hatch」（button） | 可能（应用提供撤销，未逐项验证） |
| `spline.activate` | `foxos cad spline activate` | 主界面 > Spline | — | 点击「Spline」（button） | 可能（应用提供撤销，未逐项验证） |
| `construction-line.activate` | `foxos cad construction-line activate` | 主界面 > Construction line | — | 点击「Construction line」（button） | 可能（应用提供撤销，未逐项验证） |
| `point.activate` | `foxos cad point activate` | 主界面 > Point | — | 点击「Point」（button） | 可能（应用提供撤销，未逐项验证） |
| `draw.draw` | `foxos cad draw draw` | 主界面 > Draw > Draw | — | 点击「Draw」（button） | 可能（应用提供撤销，未逐项验证） |
| `move.move` | `foxos cad move move` | 主界面 > Move | — | 点击「Move」（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.copy` | `foxos cad copy copy` | 主界面 > Copy | — | 点击「Copy」（button） | 可能（应用提供撤销，未逐项验证） |
| `stretch.activate` | `foxos cad stretch activate` | 主界面 > Stretch | — | 点击「Stretch」（button） | 可能（应用提供撤销，未逐项验证） |
| `rotate.rotate` | `foxos cad rotate rotate` | 主界面 > Rotate | — | 点击「Rotate」（button） | 可能（应用提供撤销，未逐项验证） |
| `mirror.activate` | `foxos cad mirror activate` | 主界面 > Mirror | — | 点击「Mirror」（button） | 可能（应用提供撤销，未逐项验证） |
| `scale.activate` | `foxos cad scale activate` | 主界面 > Scale | — | 点击「Scale」（button） | 可能（应用提供撤销，未逐项验证） |
| `trim.activate` | `foxos cad trim activate` | 主界面 > Trim | — | 点击「Trim」（button） | 可能（应用提供撤销，未逐项验证） |
| `trim-options.activate` | `foxos cad trim-options activate` | 主界面 > Trim options | — | 点击「Trim options」（button） | 可能（应用提供撤销，未逐项验证） |
| `fillet.activate` | `foxos cad fillet activate` | 主界面 > Fillet | — | 点击「Fillet」（button） | 可能（应用提供撤销，未逐项验证） |
| `fillet-options.activate` | `foxos cad fillet-options activate` | 主界面 > Fillet options | — | 点击「Fillet options」（button） | 可能（应用提供撤销，未逐项验证） |
| `array.activate` | `foxos cad array activate` | 主界面 > Array | — | 点击「Array」（button） | 可能（应用提供撤销，未逐项验证） |
| `array-options.activate` | `foxos cad array-options activate` | 主界面 > Array options | — | 点击「Array options」（button） | 可能（应用提供撤销，未逐项验证） |
| `erase.activate` | `foxos cad erase activate` | 主界面 > Erase | — | 点击「Erase」（button） | 可能（应用提供撤销，未逐项验证） |
| `explode.activate` | `foxos cad explode activate` | 主界面 > Explode | — | 点击「Explode」（button） | 可能（应用提供撤销，未逐项验证） |
| `offset.activate` | `foxos cad offset activate` | 主界面 > Offset | — | 点击「Offset」（button） | 可能（应用提供撤销，未逐项验证） |
| `modify.update` | `foxos cad modify update` | 主界面 > Modify > Modify | — | 点击「Modify」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-multiline-text.activate` | `foxos cad text-multiline-text activate` | 主界面 > Text, Multiline text | — | 点击「Text, Multiline text」（button） | 可能（应用提供撤销，未逐项验证） |
| `text-options.activate` | `foxos cad text-options activate` | 主界面 > Text options | — | 点击「Text options」（button） | 可能（应用提供撤销，未逐项验证） |
| `dimension-linear.activate` | `foxos cad dimension-linear activate` | 主界面 > Dimension, Linear | — | 点击「Dimension, Linear」（button） | 可能（应用提供撤销，未逐项验证） |
| `dimension-options.activate` | `foxos cad dimension-options activate` | 主界面 > Dimension options | — | 点击「Dimension options」（button） | 可能（应用提供撤销，未逐项验证） |
| `leader.activate` | `foxos cad leader activate` | 主界面 > Leader | — | 点击「Leader」（button） | 可能（应用提供撤销，未逐项验证） |
| `continue.activate` | `foxos cad continue activate` | 主界面 > Continue | — | 点击「Continue」（button） | 可能（应用提供撤销，未逐项验证） |
| `baseline.activate` | `foxos cad baseline activate` | 主界面 > Baseline | — | 点击「Baseline」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer-properties.activate` | `foxos cad layer-properties activate` | 主界面 > Layer Properties | — | 点击「Layer Properties」（button） | 可能（应用提供撤销，未逐项验证） |
| `turn-layer-off.activate` | `foxos cad turn-layer-off activate` | 主界面 > Turn layer off | — | 点击「Turn layer off」（button） | 可能（应用提供撤销，未逐项验证） |
| `isolate-layers.activate` | `foxos cad isolate-layers activate` | 主界面 > Isolate layers | — | 点击「Isolate layers」（button） | 可能（应用提供撤销，未逐项验证） |
| `freeze-layer.activate` | `foxos cad freeze-layer activate` | 主界面 > Freeze layer | — | 点击「Freeze layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer.lock` | `foxos cad layer lock` | 主界面 > Lock layer | — | 点击「Lock layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `make-current.activate` | `foxos cad make-current activate` | 主界面 > Make Current | — | 点击「Make Current」（button） | 可能（应用提供撤销，未逐项验证） |
| `turn-layers.activate` | `foxos cad turn-layers activate` | 主界面 > Turn all layers on | — | 点击「Turn all layers on」（button） | 可能（应用提供撤销，未逐项验证） |
| `unisolate-layers.activate` | `foxos cad unisolate-layers activate` | 主界面 > Unisolate layers | — | 点击「Unisolate layers」（button） | 可能（应用提供撤销，未逐项验证） |
| `thaw-layers.activate` | `foxos cad thaw-layers activate` | 主界面 > Thaw all layers | — | 点击「Thaw all layers」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer.unlock` | `foxos cad layer unlock` | 主界面 > Unlock layer | — | 点击「Unlock layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `match-layer.activate` | `foxos cad match-layer activate` | 主界面 > Match Layer | — | 点击「Match Layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `insert-2.create` | `foxos cad insert-2 create` | 主界面 > Insert | — | 点击「Insert」（button） | 可能（应用提供撤销，未逐项验证） |
| `create.create` | `foxos cad create create` | 主界面 > Create | — | 点击「Create」（button） | 可能（应用提供撤销，未逐项验证） |
| `library.activate` | `foxos cad library activate` | 主界面 > Library | — | 点击「Library」（button） | 可能（应用提供撤销，未逐项验证） |
| `match-properties.activate` | `foxos cad match-properties activate` | 主界面 > Match Properties | — | 点击「Match Properties」（button） | 可能（应用提供撤销，未逐项验证） |
| `measure-distance.activate` | `foxos cad measure-distance activate` | 主界面 > Measure, Distance | — | 点击「Measure, Distance」（button） | 可能（应用提供撤销，未逐项验证） |
| `measure-options.activate` | `foxos cad measure-options activate` | 主界面 > Measure options | — | 点击「Measure options」（button） | 可能（应用提供撤销，未逐项验证） |
| `quick-select.activate` | `foxos cad quick-select activate` | 主界面 > Quick select | — | 点击「Quick select」（button） | 可能（应用提供撤销，未逐项验证） |
| `select.select` | `foxos cad select select` | 主界面 > Select all | — | 点击「Select all」（button） | 不适用（只读） |
| `similar.select` | `foxos cad similar select` | 主界面 > Select similar | — | 点击「Select similar」（button） | 不适用（只读） |
| `paste.paste` | `foxos cad paste paste` | 主界面 > Paste | — | 点击「Paste」（button） | 可能（应用提供撤销，未逐项验证） |
| `cut.cut` | `foxos cad cut cut` | 主界面 > Cut | — | 点击「Cut」（button） | 可能（应用提供撤销，未逐项验证） |
| `clipboard.copy` | `foxos cad clipboard copy` | 主界面 > Copy to clipboard | — | 点击「Copy to clipboard」（button） | 可能（应用提供撤销，未逐项验证） |
| `base-point.copy` | `foxos cad base-point copy` | 主界面 > Copy with base point | — | 点击「Copy with base point」（button） | 可能（应用提供撤销，未逐项验证） |
| `it.dismiss` | `foxos cad it dismiss` | 主界面 > Early alpha notice > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `cursor-coordinates-click-change-display.activate` | `foxos cad cursor-coordinates-click-change-display activate` | 主界面 > Cursor coordinates. Click to change the display. | — | 点击「Cursor coordinates. Click to change the display.」（button） | 可能（应用提供撤销，未逐项验证） |
| `grid.activate` | `foxos cad grid activate` | 主界面 > Grid | — | 点击「Grid」（button） | 可能（应用提供撤销，未逐项验证） |
| `snap-grid.activate` | `foxos cad snap-grid activate` | 主界面 > Snap to grid | — | 点击「Snap to grid」（button） | 可能（应用提供撤销，未逐项验证） |
| `snap-grid-settings.activate` | `foxos cad snap-grid-settings activate` | 主界面 > Snap to grid settings | — | 点击「Snap to grid settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `ortho-mode.activate` | `foxos cad ortho-mode activate` | 主界面 > Ortho mode | — | 点击「Ortho mode」（button） | 可能（应用提供撤销，未逐项验证） |
| `polar-tracking.activate` | `foxos cad polar-tracking activate` | 主界面 > Polar tracking | — | 点击「Polar tracking」（button） | 可能（应用提供撤销，未逐项验证） |
| `polar-tracking-settings.activate` | `foxos cad polar-tracking-settings activate` | 主界面 > Polar tracking settings | — | 点击「Polar tracking settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `object-snap.activate` | `foxos cad object-snap activate` | 主界面 > Object snap | — | 点击「Object snap」（button） | 可能（应用提供撤销，未逐项验证） |
| `object-snap-settings.activate` | `foxos cad object-snap-settings activate` | 主界面 > Object snap settings | — | 点击「Object snap settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `object-snap-tracking.activate` | `foxos cad object-snap-tracking activate` | 主界面 > Object snap tracking | — | 点击「Object snap tracking」（button） | 可能（应用提供撤销，未逐项验证） |
| `dynamic-input.activate` | `foxos cad dynamic-input activate` | 主界面 > Dynamic input | — | 点击「Dynamic input」（button） | 可能（应用提供撤销，未逐项验证） |
| `lineweights.show` | `foxos cad lineweights show` | 主界面 > Show lineweights | — | 点击「Show lineweights」（button），切换到该视图 | 不适用（只读） |
| `selection-preview.activate` | `foxos cad selection-preview activate` | 主界面 > Selection preview | — | 点击「Selection preview」（button） | 可能（应用提供撤销，未逐项验证） |
| `drawing-units.activate` | `foxos cad drawing-units activate` | 主界面 > Drawing units | — | 点击「Drawing units」（button） | 可能（应用提供撤销，未逐项验证） |
| `drafting-settings.activate` | `foxos cad drafting-settings activate` | 主界面 > Drafting settings | — | 点击「Drafting settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `clean-screen.activate` | `foxos cad clean-screen activate` | 主界面 > Clean screen | — | 点击「Clean screen」（button） | 可能（应用提供撤销，未逐项验证） |
| `newctrln.activate` | `foxos cad newctrln activate` | Application menu > Application menu > NewCtrl+N | — | 点击「NewCtrl+N」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `ctrlo.open` | `foxos cad ctrlo open` | Application menu > Application menu > Open...Ctrl+O | — | 点击「Open...Ctrl+O」（menuitem） | 不适用（只读） |
| `sample-drawing.open` | `foxos cad sample-drawing open` | Application menu > Application menu > Open sample drawing | — | 点击「Open sample drawing」（menuitem） | 不适用（只读） |
| `savectrls.activate` | `foxos cad savectrls activate` | Application menu > Application menu > SaveCtrl+S | — | 点击「SaveCtrl+S」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `as-ctrlshifts.save` | `foxos cad as-ctrlshifts save` | Application menu > Application menu > Save as...Ctrl+Shift+S | — | 点击「Save as...Ctrl+Shift+S」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `dxf-or-dwg.import` | `foxos cad dxf-or-dwg import` | Application menu > Application menu > Import DXF or DWG... | — | 点击「Import DXF or DWG...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos cad export export` | Application menu > Application menu > Export... | — | 点击「Export...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `plot-ctrlp.activate` | `foxos cad plot-ctrlp activate` | Application menu > Application menu > Plot...Ctrl+P | — | 点击「Plot...Ctrl+P」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `application-menu-drawing-units.activate` | `foxos cad application-menu-drawing-units activate` | Application menu > Application menu > Drawing units... | — | 点击「Drawing units...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `purge-unused.activate` | `foxos cad purge-unused activate` | Application menu > Application menu > Purge unused... | — | 点击「Purge unused...」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `settings.show` | `foxos cad settings show` | Application menu > Application menu > Settings... | — | 点击「Settings...」（menuitem），切换到该视图 | 不适用（只读） |
| `keyboard-shortcuts.activate` | `foxos cad keyboard-shortcuts activate` | Application menu > Application menu > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `source-code-github.activate` | `foxos cad source-code-github activate` | Application menu > Application menu > Source code on GitHub | — | 点击「Source code on GitHub」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `drawing.close` | `foxos cad drawing close` | Application menu > Application menu > Close drawing | — | 点击「Close drawing」（menuitem） | 不适用（只读） |
| `close.close` | `foxos cad close close` | Search commands > Close | — | 点击「Close」（button） | 不适用（只读） |
| `search-commands.set` | `foxos cad search-commands set` | Search commands > Search commands | `value`（必填）, `submit` | 把「Search commands」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `alignalign.activate` | `foxos cad alignalign activate` | Search commands > Commands > AlignALIGN | — | 点击「AlignALIGN」（option） | 可能（应用提供撤销，未逐项验证） |
| `aligned-dimensiondimaligned.activate` | `foxos cad aligned-dimensiondimaligned activate` | Search commands > Commands > Aligned dimensionDIMALIGNED | — | 点击「Aligned dimensionDIMALIGNED」（option） | 可能（应用提供撤销，未逐项验证） |
| `angular-dimensiondimangular.activate` | `foxos cad angular-dimensiondimangular activate` | Search commands > Commands > Angular dimensionDIMANGULAR | — | 点击「Angular dimensionDIMANGULAR」（option） | 可能（应用提供撤销，未逐项验证） |
| `arcarc.activate` | `foxos cad arcarc activate` | Search commands > Commands > ArcARC | — | 点击「ArcARC」（option） | 可能（应用提供撤销，未逐项验证） |
| `baseline-dimensiondimbaseline.activate` | `foxos cad baseline-dimensiondimbaseline activate` | Search commands > Commands > Baseline dimensionDIMBASELINE | — | 点击「Baseline dimensionDIMBASELINE」（option） | 可能（应用提供撤销，未逐项验证） |
| `blocks-paletteblocks.activate` | `foxos cad blocks-paletteblocks activate` | Search commands > Commands > Blocks paletteBLOCKS | — | 点击「Blocks paletteBLOCKS」（option） | 可能（应用提供撤销，未逐项验证） |
| `breakbreak.activate` | `foxos cad breakbreak activate` | Search commands > Commands > BreakBREAK | — | 点击「BreakBREAK」（option） | 可能（应用提供撤销，未逐项验证） |
| `break-at-pointbreakatpoint.activate` | `foxos cad break-at-pointbreakatpoint activate` | Search commands > Commands > Break at pointBREAKATPOINT | — | 点击「Break at pointBREAKATPOINT」（option） | 可能（应用提供撤销，未逐项验证） |
| `chamferchamfer.activate` | `foxos cad chamferchamfer activate` | Search commands > Commands > ChamferCHAMFER | — | 点击「ChamferCHAMFER」（option） | 可能（应用提供撤销，未逐项验证） |
| `circlecircle.activate` | `foxos cad circlecircle activate` | Search commands > Commands > CircleCIRCLE | — | 点击「CircleCIRCLE」（option） | 可能（应用提供撤销，未逐项验证） |
| `clean-screencleanscreen.activate` | `foxos cad clean-screencleanscreen activate` | Search commands > Commands > Clean screenCLEANSCREEN | — | 点击「Clean screenCLEANSCREEN」（option） | 可能（应用提供撤销，未逐项验证） |
| `drawingclose.close` | `foxos cad drawingclose close` | Search commands > Commands > Close drawingCLOSE | — | 点击「Close drawingCLOSE」（option） | 不适用（只读） |
| `construction-linexline.activate` | `foxos cad construction-linexline activate` | Search commands > Commands > Construction lineXLINE | — | 点击「Construction lineXLINE」（option） | 可能（应用提供撤销，未逐项验证） |
| `continue-dimensiondimcontinue.activate` | `foxos cad continue-dimensiondimcontinue activate` | Search commands > Commands > Continue dimensionDIMCONTINUE | — | 点击「Continue dimensionDIMCONTINUE」（option） | 可能（应用提供撤销，未逐项验证） |
| `copycopy.activate` | `foxos cad copycopy activate` | Search commands > Commands > CopyCOPY | — | 点击「CopyCOPY」（option） | 可能（应用提供撤销，未逐项验证） |
| `clipboardcopyclip.copy` | `foxos cad clipboardcopyclip copy` | Search commands > Commands > Copy to clipboardCOPYCLIP | — | 点击「Copy to clipboardCOPYCLIP」（option） | 可能（应用提供撤销，未逐项验证） |
| `base-pointcopybase.copy` | `foxos cad base-pointcopybase copy` | Search commands > Commands > Copy with base pointCOPYBASE | — | 点击「Copy with base pointCOPYBASE」（option） | 可能（应用提供撤销，未逐项验证） |
| `blockblock.create` | `foxos cad blockblock create` | Search commands > Commands > Create blockBLOCK | — | 点击「Create blockBLOCK」（option） | 可能（应用提供撤销，未逐项验证） |
| `cutcutclip.activate` | `foxos cad cutcutclip activate` | Search commands > Commands > CutCUTCLIP | — | 点击「CutCUTCLIP」（option） | 可能（应用提供撤销，未逐项验证） |
| `diameter-dimensiondimdiameter.activate` | `foxos cad diameter-dimensiondimdiameter activate` | Search commands > Commands > Diameter dimensionDIMDIAMETER | — | 点击「Diameter dimensionDIMDIAMETER」（option） | 可能（应用提供撤销，未逐项验证） |
| `dimensiondim.activate` | `foxos cad dimensiondim activate` | Search commands > Commands > DimensionDIM | — | 点击「DimensionDIM」（option） | 可能（应用提供撤销，未逐项验证） |
| `dimension-stylesdimstyle.activate` | `foxos cad dimension-stylesdimstyle activate` | Search commands > Commands > Dimension stylesDIMSTYLE | — | 点击「Dimension stylesDIMSTYLE」（option） | 可能（应用提供撤销，未逐项验证） |
| `donutdonut.activate` | `foxos cad donutdonut activate` | Search commands > Commands > DonutDONUT | — | 点击「DonutDONUT」（option） | 可能（应用提供撤销，未逐项验证） |
| `drafting-settingsdsettings.activate` | `foxos cad drafting-settingsdsettings activate` | Search commands > Commands > Drafting settingsDSETTINGS | — | 点击「Drafting settingsDSETTINGS」（option） | 可能（应用提供撤销，未逐项验证） |
| `orderdraworder.draw` | `foxos cad orderdraworder draw` | Search commands > Commands > Draw orderDRAWORDER | — | 点击「Draw orderDRAWORDER」（option） | 可能（应用提供撤销，未逐项验证） |
| `drawing-unitsunits.activate` | `foxos cad drawing-unitsunits activate` | Search commands > Commands > Drawing unitsUNITS | — | 点击「Drawing unitsUNITS」（option） | 可能（应用提供撤销，未逐项验证） |
| `ellipseellipse.activate` | `foxos cad ellipseellipse activate` | Search commands > Commands > EllipseELLIPSE | — | 点击「EllipseELLIPSE」（option） | 可能（应用提供撤销，未逐项验证） |
| `eraseerase.activate` | `foxos cad eraseerase activate` | Search commands > Commands > EraseERASE | — | 点击「EraseERASE」（option） | 可能（应用提供撤销，未逐项验证） |
| `explodeexplode.activate` | `foxos cad explodeexplode activate` | Search commands > Commands > ExplodeEXPLODE | — | 点击「ExplodeEXPLODE」（option） | 可能（应用提供撤销，未逐项验证） |
| `exportexport.activate` | `foxos cad exportexport activate` | Search commands > Commands > ExportEXPORT | — | 点击「ExportEXPORT」（option） | 可能（应用提供撤销，未逐项验证） |
| `dwgdwgout.export` | `foxos cad dwgdwgout export` | Search commands > Commands > Export DWGDWGOUT | — | 点击「Export DWGDWGOUT」（option） | 可能（应用提供撤销，未逐项验证） |
| `dxfdxfout.export` | `foxos cad dxfdxfout export` | Search commands > Commands > Export DXFDXFOUT | — | 点击「Export DXFDXFOUT」（option） | 可能（应用提供撤销，未逐项验证） |
| `extendextend.activate` | `foxos cad extendextend activate` | Search commands > Commands > ExtendEXTEND | — | 点击「ExtendEXTEND」（option） | 可能（应用提供撤销，未逐项验证） |
| `filletfillet.activate` | `foxos cad filletfillet activate` | Search commands > Commands > FilletFILLET | — | 点击「FilletFILLET」（option） | 可能（应用提供撤销，未逐项验证） |
| `freeze-layerlayfrz.activate` | `foxos cad freeze-layerlayfrz activate` | Search commands > Commands > Freeze layerLAYFRZ | — | 点击「Freeze layerLAYFRZ」（option） | 可能（应用提供撤销，未逐项验证） |
| `grid-displaygrid.activate` | `foxos cad grid-displaygrid activate` | Search commands > Commands > Grid displayGRID | — | 点击「Grid displayGRID」（option） | 可能（应用提供撤销，未逐项验证） |
| `hatchhatch.activate` | `foxos cad hatchhatch activate` | Search commands > Commands > HatchHATCH | — | 点击「HatchHATCH」（option） | 可能（应用提供撤销，未逐项验证） |
| `helphelp.activate` | `foxos cad helphelp activate` | Search commands > Commands > HelpHELP | — | 点击「HelpHELP」（option） | 可能（应用提供撤销，未逐项验证） |
| `dxf-or-dwgimport.import` | `foxos cad dxf-or-dwgimport import` | Search commands > Commands > Import DXF or DWGIMPORT | — | 点击「Import DXF or DWGIMPORT」（option） | 可能（应用提供撤销，未逐项验证） |
| `blockinsert.create` | `foxos cad blockinsert create` | Search commands > Commands > Insert blockINSERT | — | 点击「Insert blockINSERT」（option） | 可能（应用提供撤销，未逐项验证） |
| `isolate-layerslayiso.activate` | `foxos cad isolate-layerslayiso activate` | Search commands > Commands > Isolate layersLAYISO | — | 点击「Isolate layersLAYISO」（option） | 可能（应用提供撤销，未逐项验证） |
| `joinjoin.activate` | `foxos cad joinjoin activate` | Search commands > Commands > JoinJOIN | — | 点击「JoinJOIN」（option） | 可能（应用提供撤销，未逐项验证） |
| `keyboard-shortcutsshortcuts.activate` | `foxos cad keyboard-shortcutsshortcuts activate` | Search commands > Commands > Keyboard shortcutsSHORTCUTS | — | 点击「Keyboard shortcutsSHORTCUTS」（option） | 可能（应用提供撤销，未逐项验证） |
| `layer-propertieslayer.activate` | `foxos cad layer-propertieslayer activate` | Search commands > Commands > Layer propertiesLAYER | — | 点击「Layer propertiesLAYER」（option） | 可能（应用提供撤销，未逐项验证） |
| `leaderleader.activate` | `foxos cad leaderleader activate` | Search commands > Commands > LeaderLEADER | — | 点击「LeaderLEADER」（option） | 可能（应用提供撤销，未逐项验证） |
| `lengthenlengthen.activate` | `foxos cad lengthenlengthen activate` | Search commands > Commands > LengthenLENGTHEN | — | 点击「LengthenLENGTHEN」（option） | 可能（应用提供撤销，未逐项验证） |
| `lineline.activate` | `foxos cad lineline activate` | Search commands > Commands > LineLINE | — | 点击「LineLINE」（option） | 可能（应用提供撤销，未逐项验证） |
| `linear-dimensiondimlinear.activate` | `foxos cad linear-dimensiondimlinear activate` | Search commands > Commands > Linear dimensionDIMLINEAR | — | 点击「Linear dimensionDIMLINEAR」（option） | 可能（应用提供撤销，未逐项验证） |
| `linetype-scaleltscale.activate` | `foxos cad linetype-scaleltscale activate` | Search commands > Commands > Linetype scaleLTSCALE | — | 点击「Linetype scaleLTSCALE」（option） | 可能（应用提供撤销，未逐项验证） |
| `linetypeslinetype.activate` | `foxos cad linetypeslinetype activate` | Search commands > Commands > LinetypesLINETYPE | — | 点击「LinetypesLINETYPE」（option） | 可能（应用提供撤销，未逐项验证） |
| `system.activate` | `foxos cad system activate` | Theme > Theme > System | — | 点击「System」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `light.activate` | `foxos cad light activate` | Theme > Theme > Light | — | 点击「Light」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `dark.activate` | `foxos cad dark activate` | Theme > Theme > Dark | — | 点击「Dark」（menuitemradio） | 可能（应用提供撤销，未逐项验证） |
| `center-radius.activate` | `foxos cad center-radius activate` | Circle options > Circle options > Center, Radius | — | 点击「Center, Radius」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `center-diameter.activate` | `foxos cad center-diameter activate` | Circle options > Circle options > Center, Diameter | — | 点击「Center, Diameter」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `tan-tan-radius.activate` | `foxos cad tan-tan-radius activate` | Circle options > Circle options > Tan, Tan, Radius | — | 点击「Tan, Tan, Radius」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `center-end.start` | `foxos cad center-end start` | Arc options > Arc options > Start, Center, End | — | 点击「Start, Center, End」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `center-start-end.activate` | `foxos cad center-start-end activate` | Arc options > Arc options > Center, Start, End | — | 点击「Center, Start, End」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `end-radius.start` | `foxos cad end-radius start` | Arc options > Arc options > Start, End, Radius | — | 点击「Start, End, Radius」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `rectangle-options-rectangle.activate` | `foxos cad rectangle-options-rectangle activate` | Rectangle options > Rectangle options > Rectangle | — | 点击「Rectangle」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `polygon.activate` | `foxos cad polygon activate` | Rectangle options > Rectangle options > Polygon | — | 点击「Polygon」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `center.activate` | `foxos cad center activate` | Ellipse options > Ellipse options > Center | — | 点击「Center」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `axis-end.activate` | `foxos cad axis-end activate` | Ellipse options > Ellipse options > Axis, End | — | 点击「Axis, End」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `elliptical-arc.activate` | `foxos cad elliptical-arc activate` | Ellipse options > Ellipse options > Elliptical arc | — | 点击「Elliptical arc」（menuitem） | 可能（应用提供撤销，未逐项验证） |
