# Vector Studio（vector-studio）操作清单

分组：creative · 替代 Adobe Illustrator, CorelDRAW, Affinity Designer · 许可证 MIT (root LICENSE) · 页面标题「Vector Studio」

共 90 个操作，全部有语义命令（`foxos vector-studio <资源> <动词>`，MCP 工具 `vector-studio.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account.select` | `foxos vector-studio account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `drawing-modes.select` | `foxos vector-studio drawing-modes select` | 主界面 > drawing modes: * | `target`（必填） | 点击名称匹配的「drawing modes: *」项（button） | 不适用（只读） |
| `letter-x.select` | `foxos vector-studio letter-x select` | 主界面 > main > letter # x # in | `target`（必填） | 点击名称匹配的「letter # x # in」项（button） | 不适用（只读） |
| `x-mm.select` | `foxos vector-studio x-mm select` | 主界面 > main > # x # mm | `target`（必填） | 点击名称匹配的「# x # mm」项（button） | 不适用（只读） |
| `postcard-x-pt.select` | `foxos vector-studio postcard-x-pt select` | 主界面 > main > postcard # x # pt | `target`（必填） | 点击名称匹配的「postcard # x # pt」项（button） | 不适用（只读） |
| `web-x-px.select` | `foxos vector-studio web-x-px select` | 主界面 > main > web # x # px | `target`（必填） | 点击名称匹配的「web # x # px」项（button） | 不适用（只读） |
| `mobile-x-px.select` | `foxos vector-studio mobile-x-px select` | 主界面 > main > mobile # x # px | `target`（必填） | 点击名称匹配的「mobile # x # px」项（button） | 不适用（只读） |
| `square-x-px.select` | `foxos vector-studio square-x-px select` | 主界面 > main > square # x # px | `target`（必填） | 点击名称匹配的「square # x # px」项（button） | 不适用（只读） |
| `icon-x-px.select` | `foxos vector-studio icon-x-px select` | 主界面 > main > icon # x # px | `target`（必填） | 点击名称匹配的「icon # x # px」项（button） | 不适用（只读） |
| `poster-x.select` | `foxos vector-studio poster-x select` | 主界面 > main > poster # x # in | `target`（必填） | 点击名称匹配的「poster # x # in」项（button） | 不适用（只读） |
| `preview.select` | `foxos vector-studio preview select` | 主界面 > # preview | `target`（必填） | 点击名称匹配的「# preview」项（button） | 不适用（只读） |
| `canvas.dismiss` | `foxos vector-studio canvas dismiss` | 主界面 > Skip to canvas | — | 点击「Skip to canvas」（link） | 不适用（只读） |
| `home.activate` | `foxos vector-studio home activate` | 主界面 > Home | — | 点击「Home」（button） | 否（应用没有撤销入口） |
| `file.activate` | `foxos vector-studio file activate` | 主界面 > Application menu > File | — | 点击「File」（menuitem） | 否（应用没有撤销入口） |
| `edit.update` | `foxos vector-studio edit update` | 主界面 > Application menu > Edit | — | 点击「Edit」（menuitem） | 否（应用没有撤销入口） |
| `object.activate` | `foxos vector-studio object activate` | 主界面 > Application menu > Object | — | 点击「Object」（menuitem） | 否（应用没有撤销入口） |
| `type.activate` | `foxos vector-studio type activate` | 主界面 > Application menu > Type | — | 点击「Type」（menuitem） | 否（应用没有撤销入口） |
| `select.select` | `foxos vector-studio select select` | 主界面 > Application menu > Select | — | 点击「Select」（menuitem） | 不适用（只读） |
| `effect.activate` | `foxos vector-studio effect activate` | 主界面 > Application menu > Effect | — | 点击「Effect」（menuitem） | 否（应用没有撤销入口） |
| `view.show` | `foxos vector-studio view show` | 主界面 > Application menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `window.activate` | `foxos vector-studio window activate` | 主界面 > Application menu > Window | — | 点击「Window」（menuitem） | 否（应用没有撤销入口） |
| `help.show` | `foxos vector-studio help show` | 主界面 > Application menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `theme.activate` | `foxos vector-studio theme activate` | 主界面 > Theme | — | 点击「Theme」（button） | 否（应用没有撤销入口） |
| `single-or-double-column-tools.toggle` | `foxos vector-studio single-or-double-column-tools toggle` | 主界面 > Toggle single or double column tools | — | 切换「Toggle single or double column tools」 | 否（应用没有撤销入口） |
| `selection-tool.activate` | `foxos vector-studio selection-tool activate` | 主界面 > Selection Tool | — | 点击「Selection Tool」（button） | 否（应用没有撤销入口） |
| `direct-selection-tool.activate` | `foxos vector-studio direct-selection-tool activate` | 主界面 > Direct Selection Tool | — | 点击「Direct Selection Tool」（button） | 否（应用没有撤销入口） |
| `magic-wand-tool.activate` | `foxos vector-studio magic-wand-tool activate` | 主界面 > Magic Wand Tool | — | 点击「Magic Wand Tool」（button） | 否（应用没有撤销入口） |
| `lasso-tool.activate` | `foxos vector-studio lasso-tool activate` | 主界面 > Lasso Tool | — | 点击「Lasso Tool」（button） | 否（应用没有撤销入口） |
| `pen-tool.activate` | `foxos vector-studio pen-tool activate` | 主界面 > Pen Tool | — | 点击「Pen Tool」（button） | 否（应用没有撤销入口） |
| `curvature-tool.activate` | `foxos vector-studio curvature-tool activate` | 主界面 > Curvature Tool | — | 点击「Curvature Tool」（button） | 否（应用没有撤销入口） |
| `sketch-shape-tool.activate` | `foxos vector-studio sketch-shape-tool activate` | 主界面 > Sketch Shape Tool | — | 点击「Sketch Shape Tool」（button） | 否（应用没有撤销入口） |
| `paintbrush-tool.activate` | `foxos vector-studio paintbrush-tool activate` | 主界面 > Paintbrush Tool | — | 点击「Paintbrush Tool」（button） | 否（应用没有撤销入口） |
| `rectangle-tool.activate` | `foxos vector-studio rectangle-tool activate` | 主界面 > Rectangle Tool | — | 点击「Rectangle Tool」（button） | 否（应用没有撤销入口） |
| `line-segment-tool.activate` | `foxos vector-studio line-segment-tool activate` | 主界面 > Line Segment Tool | — | 点击「Line Segment Tool」（button） | 否（应用没有撤销入口） |
| `shape-builder-tool.activate` | `foxos vector-studio shape-builder-tool activate` | 主界面 > Shape Builder Tool | — | 点击「Shape Builder Tool」（button） | 否（应用没有撤销入口） |
| `type-tool.activate` | `foxos vector-studio type-tool activate` | 主界面 > Type Tool | — | 点击「Type Tool」（button） | 否（应用没有撤销入口） |
| `tool.rotate` | `foxos vector-studio tool rotate` | 主界面 > Rotate Tool | — | 点击「Rotate Tool」（button） | 否（应用没有撤销入口） |
| `scale-tool.activate` | `foxos vector-studio scale-tool activate` | 主界面 > Scale Tool | — | 点击「Scale Tool」（button） | 否（应用没有撤销入口） |
| `width-tool.activate` | `foxos vector-studio width-tool activate` | 主界面 > Width Tool | — | 点击「Width Tool」（button） | 否（应用没有撤销入口） |
| `free-transform-tool.activate` | `foxos vector-studio free-transform-tool activate` | 主界面 > Free Transform Tool | — | 点击「Free Transform Tool」（button） | 否（应用没有撤销入口） |
| `eraser-tool.activate` | `foxos vector-studio eraser-tool activate` | 主界面 > Eraser Tool | — | 点击「Eraser Tool」（button） | 否（应用没有撤销入口） |
| `perspective-grid-tool.activate` | `foxos vector-studio perspective-grid-tool activate` | 主界面 > Perspective Grid Tool | — | 点击「Perspective Grid Tool」（button） | 否（应用没有撤销入口） |
| `gradient-tool.activate` | `foxos vector-studio gradient-tool activate` | 主界面 > Gradient Tool | — | 点击「Gradient Tool」（button） | 否（应用没有撤销入口） |
| `mesh-tool.activate` | `foxos vector-studio mesh-tool activate` | 主界面 > Mesh Tool | — | 点击「Mesh Tool」（button） | 否（应用没有撤销入口） |
| `eyedropper-tool.activate` | `foxos vector-studio eyedropper-tool activate` | 主界面 > Eyedropper Tool | — | 点击「Eyedropper Tool」（button） | 否（应用没有撤销入口） |
| `blend-tool.activate` | `foxos vector-studio blend-tool activate` | 主界面 > Blend Tool | — | 点击「Blend Tool」（button） | 否（应用没有撤销入口） |
| `symbol-sprayer-tool.activate` | `foxos vector-studio symbol-sprayer-tool activate` | 主界面 > Symbol Sprayer Tool | — | 点击「Symbol Sprayer Tool」（button） | 否（应用没有撤销入口） |
| `column-graph-tool.activate` | `foxos vector-studio column-graph-tool activate` | 主界面 > Column Graph Tool | — | 点击「Column Graph Tool」（button） | 否（应用没有撤销入口） |
| `artboard-tool.activate` | `foxos vector-studio artboard-tool activate` | 主界面 > Artboard Tool | — | 点击「Artboard Tool」（button） | 否（应用没有撤销入口） |
| `hand-tool.activate` | `foxos vector-studio hand-tool activate` | 主界面 > Hand Tool | — | 点击「Hand Tool」（button） | 否（应用没有撤销入口） |
| `view.zoom-tool` | `foxos vector-studio view zoom-tool` | 主界面 > Zoom Tool | — | 点击「Zoom Tool」（button） | 否（应用没有撤销入口） |
| `fill.activate` | `foxos vector-studio fill activate` | 主界面 > Fill | — | 点击「Fill」（button） | 否（应用没有撤销入口） |
| `stroke.activate` | `foxos vector-studio stroke activate` | 主界面 > Stroke | — | 点击「Stroke」（button） | 否（应用没有撤销入口） |
| `swap-fill-stroke.activate` | `foxos vector-studio swap-fill-stroke activate` | 主界面 > Swap Fill and Stroke | — | 点击「Swap Fill and Stroke」（button） | 否（应用没有撤销入口） |
| `default-fill-stroke.activate` | `foxos vector-studio default-fill-stroke activate` | 主界面 > Default Fill and Stroke | — | 点击「Default Fill and Stroke」（button） | 否（应用没有撤销入口） |
| `color.activate` | `foxos vector-studio color activate` | 主界面 > Color | — | 点击「Color」（button） | 否（应用没有撤销入口） |
| `gradient.activate` | `foxos vector-studio gradient activate` | 主界面 > Gradient | — | 点击「Gradient」（button） | 否（应用没有撤销入口） |
| `none.activate` | `foxos vector-studio none activate` | 主界面 > None | — | 点击「None」（button） | 否（应用没有撤销入口） |
| `tools.activate` | `foxos vector-studio tools activate` | 主界面 > All tools | — | 点击「All tools」（button） | 否（应用没有撤销入口） |
| `screen-mode.update` | `foxos vector-studio screen-mode update` | 主界面 > Change Screen Mode | — | 点击「Change Screen Mode」（button） | 否（应用没有撤销入口） |
| `file.create` | `foxos vector-studio file create` | 主界面 > Home > New file | — | 点击「New file」（button） | 否（应用没有撤销入口） |
| `open.open` | `foxos vector-studio open open` | 主界面 > Home > Open | — | 点击「Open」（button） | 不适用（只读） |
| `home-2.activate` | `foxos vector-studio home-2 activate` | 主界面 > Home > Home | — | 点击「Home」（button） | 否（应用没有撤销入口） |
| `recent.activate` | `foxos vector-studio recent activate` | 主界面 > Home > Recent | — | 点击「Recent」（button） | 否（应用没有撤销入口） |
| `files.activate` | `foxos vector-studio files activate` | 主界面 > Home > Your files | — | 点击「Your files」（button） | 否（应用没有撤销入口） |
| `templates.activate` | `foxos vector-studio templates activate` | 主界面 > Home > Templates | — | 点击「Templates」（button） | 否（应用没有撤销入口） |
| `hide.hide` | `foxos vector-studio hide hide` | 主界面 > main > Hide | — | 点击「Hide」（button） | 不适用（只读） |
| `presets-sizes-settings.show` | `foxos vector-studio presets-sizes-settings show` | 主界面 > main > More Presets All sizes and settings | — | 点击「More Presets All sizes and settings」（button），切换到该视图 | 不适用（只读） |
| `refresh-files.activate` | `foxos vector-studio refresh-files activate` | 主界面 > Refresh Your files | — | 点击「Refresh Your files」（button） | 否（应用没有撤销入口） |
| `powered-by-puter.show` | `foxos vector-studio powered-by-puter show` | 主界面 > footer > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `panels.activate` | `foxos vector-studio panels activate` | 主界面 > Panels | — | 点击「Panels」（button） | 否（应用没有撤销入口） |
| `color-paint-panels.activate` | `foxos vector-studio color-paint-panels activate` | 主界面 > Color and Paint panels | — | 点击「Color and Paint panels」（button） | 否（应用没有撤销入口） |
| `arrange-shape-panels.activate` | `foxos vector-studio arrange-shape-panels activate` | 主界面 > Arrange and Shape panels | — | 点击「Arrange and Shape panels」（button） | 否（应用没有撤销入口） |
| `type-panels.activate` | `foxos vector-studio type-panels activate` | 主界面 > Type panels | — | 点击「Type panels」（button） | 否（应用没有撤销入口） |
| `symbols.activate` | `foxos vector-studio symbols activate` | 主界面 > Symbols | — | 点击「Symbols」（button） | 否（应用没有撤销入口） |
| `libraries.activate` | `foxos vector-studio libraries activate` | 主界面 > Libraries | — | 点击「Libraries」（button） | 否（应用没有撤销入口） |
| `asset-export.activate` | `foxos vector-studio asset-export activate` | 主界面 > Asset Export | — | 点击「Asset Export」（button） | 否（应用没有撤销入口） |
| `generate.run` | `foxos vector-studio generate run` | 主界面 > Generate | — | 点击「Generate」（button） | 否（应用没有撤销入口） |
| `generation-history.activate` | `foxos vector-studio generation-history activate` | 主界面 > Generation History | — | 点击「Generation History」（button） | 否（应用没有撤销入口） |
| `document-panels.activate` | `foxos vector-studio document-panels activate` | 主界面 > Document panels | — | 点击「Document panels」（button） | 否（应用没有撤销入口） |
| `flattener-preview.activate` | `foxos vector-studio flattener-preview activate` | 主界面 > Flattener Preview | — | 点击「Flattener Preview」（button） | 否（应用没有撤销入口） |
| `variables.activate` | `foxos vector-studio variables activate` | 主界面 > Variables | — | 点击「Variables」（button） | 否（应用没有撤销入口） |
| `svg-interactivity.activate` | `foxos vector-studio svg-interactivity activate` | 主界面 > SVG Interactivity | — | 点击「SVG Interactivity」（button） | 否（应用没有撤销入口） |
| `actions.activate` | `foxos vector-studio actions activate` | 主界面 > Actions | — | 点击「Actions」（button） | 否（应用没有撤销入口） |
| `mockup.activate` | `foxos vector-studio mockup activate` | 主界面 > Mockup | — | 点击「Mockup」（button） | 否（应用没有撤销入口） |
| `match-font.activate` | `foxos vector-studio match-font activate` | 主界面 > Match Font | — | 点击「Match Font」（button） | 否（应用没有撤销入口） |
| `properties.show` | `foxos vector-studio properties show` | 主界面 > Panels > Properties | — | 点击「Properties」（tab），切换到该视图 | 不适用（只读） |
| `layers.show` | `foxos vector-studio layers show` | 主界面 > Panels > Layers | — | 点击「Layers」（tab），切换到该视图 | 不适用（只读） |
| `signed-as-local.activate` | `foxos vector-studio signed-as-local activate` | Account: local > Account > Signed in as local | — | 点击「Signed in as local」（menuitem） | 否（应用没有撤销入口） |
| `shortcut.key-5` | `foxos vector-studio shortcut key-5` | 键盘 mod+5 | — | 在当前焦点上按 mod+5（src/features/perspective/tools.js 中定义） | 否（应用没有撤销入口） |
