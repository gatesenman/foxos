# Photo Studio（photo-studio）操作清单

分组：creative · 替代 Adobe Photoshop, Pixelmator · 许可证 MIT (root LICENSE) · 页面标题「Photo Studio」

共 104 个操作，全部有语义命令（`foxos photo-studio <资源> <动词>`，MCP 工具 `photo-studio.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `sheet.create` | `foxos photo-studio sheet create` | 主界面 > New from a preset > create # sheet | `target`（必填） | 点击名称匹配的「create # sheet」项（button） | 可能（应用提供撤销，未逐项验证） |
| `photo-print.create` | `foxos photo-studio photo-print create` | 主界面 > New from a preset > create photo print # | `target`（必填） | 点击名称匹配的「create photo print #」项（button） | 可能（应用提供撤销，未逐项验证） |
| `copy.export` | `foxos photo-studio copy export` | 主界面 > Learn > export a copy for * | `target`（必填） | 点击名称匹配的「export a copy for *」项（button） | 可能（应用提供撤销，未逐项验证） |
| `file.activate` | `foxos photo-studio file activate` | 主界面 > Application menu > File | — | 点击「File」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `edit.update` | `foxos photo-studio edit update` | 主界面 > Application menu > Edit | — | 点击「Edit」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `image.activate` | `foxos photo-studio image activate` | 主界面 > Application menu > Image | — | 点击「Image」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `layer.activate` | `foxos photo-studio layer activate` | 主界面 > Application menu > Layer | — | 点击「Layer」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `type.activate` | `foxos photo-studio type activate` | 主界面 > Application menu > Type | — | 点击「Type」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `select.select` | `foxos photo-studio select select` | 主界面 > Application menu > Select | — | 点击「Select」（menuitem） | 不适用（只读） |
| `filter.filter` | `foxos photo-studio filter filter` | 主界面 > Application menu > Filter | — | 点击「Filter」（menuitem） | 不适用（只读） |
| `view.show` | `foxos photo-studio view show` | 主界面 > Application menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `window.activate` | `foxos photo-studio window activate` | 主界面 > Application menu > Window | — | 点击「Window」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `help.show` | `foxos photo-studio help show` | 主界面 > Application menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `commands.search` | `foxos photo-studio commands search` | 主界面 > Search commands | — | 点击「Search commands」（button） | 不适用（只读） |
| `puter.save` | `foxos photo-studio puter save` | 主界面 > header > Save to Puter | — | 点击「Save to Puter」（button） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos photo-studio export export` | 主界面 > header > Export | — | 点击「Export」（button） | 可能（应用提供撤销，未逐项验证） |
| `puter-account.activate` | `foxos photo-studio puter-account activate` | 主界面 > Puter account | — | 点击「Puter account」（button） | 可能（应用提供撤销，未逐项验证） |
| `tool-presets.activate` | `foxos photo-studio tool-presets activate` | 主界面 > Tool presets | — | 点击「Tool presets」（button） | 可能（应用提供撤销，未逐项验证） |
| `tool-presets-2.activate` | `foxos photo-studio tool-presets-2 activate` | 主界面 > Tool Presets | — | 点击「Tool Presets」（button） | 可能（应用提供撤销，未逐项验证） |
| `color-theme.set` | `foxos photo-studio color-theme set` | 主界面 > Color theme | `value`（必填）, `submit` | 把「Color theme」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `panels.toggle` | `foxos photo-studio panels toggle` | 主界面 > Toggle panels | — | 切换「Toggle panels」 | 可能（应用提供撤销，未逐项验证） |
| `default-colors.activate` | `foxos photo-studio default-colors activate` | 主界面 > Default colors | — | 点击「Default colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `switch-colors.activate` | `foxos photo-studio switch-colors activate` | 主界面 > Switch colors | — | 点击「Switch colors」（button） | 可能（应用提供撤销，未逐项验证） |
| `background-color.activate` | `foxos photo-studio background-color activate` | 主界面 > Background color | — | 点击「Background color」（button） | 可能（应用提供撤销，未逐项验证） |
| `foreground-color.activate` | `foxos photo-studio foreground-color activate` | 主界面 > Foreground color | — | 点击「Foreground color」（button） | 可能（应用提供撤销，未逐项验证） |
| `foreground-color-value.set` | `foxos photo-studio foreground-color-value set` | 主界面 > Foreground color value | `value`（必填）, `submit` | 把「Foreground color value」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `quick-mask-mode.activate` | `foxos photo-studio quick-mask-mode activate` | 主界面 > Quick Mask mode | — | 点击「Quick Mask mode」（button） | 可能（应用提供撤销，未逐项验证） |
| `screen-mode.update` | `foxos photo-studio screen-mode update` | 主界面 > Change screen mode | — | 点击「Change screen mode」（button） | 可能（应用提供撤销，未逐项验证） |
| `image-canvas.activate` | `foxos photo-studio image-canvas activate` | 主界面 > Image canvas | — | 点击「Image canvas」（generic） | 可能（应用提供撤销，未逐项验证） |
| `image.open` | `foxos photo-studio image open` | 主界面 > Image canvas > Open an image | — | 点击「Open an image」（button） | 不适用（只读） |
| `document.create` | `foxos photo-studio document create` | 主界面 > Image canvas > New document | — | 点击「New document」（button） | 可能（应用提供撤销，未逐项验证） |
| `describe-edit.set` | `foxos photo-studio describe-edit set` | 主界面 > Describe an edit | `value`（必填）, `submit` | 把「Describe an edit」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `image.select` | `foxos photo-studio image select` | 主界面 > Describe an edit > Choose image… | — | 点击「Choose image…」（button） | 不适用（只读） |
| `start.start` | `foxos photo-studio start start` | 主界面 > Describe an edit > Start | — | 点击「Start」（button） | 可能（应用提供撤销，未逐项验证） |
| `large-web-page.create` | `foxos photo-studio large-web-page create` | 主界面 > New from a preset > Create Large web page | — | 点击「Create Large web page」（button） | 可能（应用提供撤销，未逐项验证） |
| `square-social-post.create` | `foxos photo-studio square-social-post create` | 主界面 > New from a preset > Create Square social post | — | 点击「Create Square social post」（button） | 可能（应用提供撤销，未逐项验证） |
| `standard-phone.create` | `foxos photo-studio standard-phone create` | 主界面 > New from a preset > Create Standard phone | — | 点击「Create Standard phone」（button） | 可能（应用提供撤销，未逐项验证） |
| `presets-custom-sizes.activate` | `foxos photo-studio presets-custom-sizes activate` | 主界面 > New from a preset > All presets and custom sizes | — | 点击「All presets and custom sizes」（button） | 可能（应用提供撤销，未逐项验证） |
| `what-s-newrecent-features.activate` | `foxos photo-studio what-s-newrecent-features activate` | 主界面 > Learn > What’s NewRecent features | — | 点击「What’s NewRecent features」（button） | 可能（应用提供撤销，未逐项验证） |
| `assistant.activate` | `foxos photo-studio assistant activate` | 主界面 > Assistant | — | 点击「Assistant」（button） | 可能（应用提供撤销，未逐项验证） |
| `generation-history.activate` | `foxos photo-studio generation-history activate` | 主界面 > Generation History | — | 点击「Generation History」（button） | 可能（应用提供撤销，未逐项验证） |
| `history.activate` | `foxos photo-studio history activate` | 主界面 > History | — | 点击「History」（button） | 可能（应用提供撤销，未逐项验证） |
| `actions.activate` | `foxos photo-studio actions activate` | 主界面 > Actions | — | 点击「Actions」（button） | 可能（应用提供撤销，未逐项验证） |
| `version-history.activate` | `foxos photo-studio version-history activate` | 主界面 > Version History | — | 点击「Version History」（button） | 可能（应用提供撤销，未逐项验证） |
| `navigator.activate` | `foxos photo-studio navigator activate` | 主界面 > Navigator | — | 点击「Navigator」（button） | 可能（应用提供撤销，未逐项验证） |
| `info.activate` | `foxos photo-studio info activate` | 主界面 > Info | — | 点击「Info」（button） | 可能（应用提供撤销，未逐项验证） |
| `histogram.activate` | `foxos photo-studio histogram activate` | 主界面 > Histogram | — | 点击「Histogram」（button） | 可能（应用提供撤销，未逐项验证） |
| `brushes.activate` | `foxos photo-studio brushes activate` | 主界面 > Brushes | — | 点击「Brushes」（button） | 可能（应用提供撤销，未逐项验证） |
| `brush-settings.activate` | `foxos photo-studio brush-settings activate` | 主界面 > Brush Settings | — | 点击「Brush Settings」（button） | 可能（应用提供撤销，未逐项验证） |
| `character.activate` | `foxos photo-studio character activate` | 主界面 > Character | — | 点击「Character」（button） | 可能（应用提供撤销，未逐项验证） |
| `paragraph.activate` | `foxos photo-studio paragraph activate` | 主界面 > Paragraph | — | 点击「Paragraph」（button） | 可能（应用提供撤销，未逐项验证） |
| `styles.activate` | `foxos photo-studio styles activate` | 主界面 > Styles | — | 点击「Styles」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer-comps.activate` | `foxos photo-studio layer-comps activate` | 主界面 > Layer Comps | — | 点击「Layer Comps」（button） | 可能（应用提供撤销，未逐项验证） |
| `scripts.activate` | `foxos photo-studio scripts activate` | 主界面 > Scripts | — | 点击「Scripts」（button） | 可能（应用提供撤销，未逐项验证） |
| `color.show` | `foxos photo-studio color show` | 主界面 > Panels > Color | — | 点击「Color」（tab），切换到该视图 | 不适用（只读） |
| `swatches.show` | `foxos photo-studio swatches show` | 主界面 > Panels > Swatches | — | 点击「Swatches」（tab），切换到该视图 | 不适用（只读） |
| `gradients.show` | `foxos photo-studio gradients show` | 主界面 > Panels > Gradients | — | 点击「Gradients」（tab），切换到该视图 | 不适用（只读） |
| `patterns.show` | `foxos photo-studio patterns show` | 主界面 > Panels > Patterns | — | 点击「Patterns」（tab），切换到该视图 | 不适用（只读） |
| `color-panel-menu.activate` | `foxos photo-studio color-panel-menu activate` | 主界面 > Color panel menu | — | 点击「Color panel menu」（button） | 可能（应用提供撤销，未逐项验证） |
| `color-saturation-brightness.set` | `foxos photo-studio color-saturation-brightness set` | 主界面 > Color saturation and brightness | `value`（必填）, `submit` | 把「Color saturation and brightness」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `color-hue.set` | `foxos photo-studio color-hue set` | 主界面 > Color hue | `value`（必填）, `submit` | 把「Color hue」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `hex-color.set` | `foxos photo-studio hex-color set` | 主界面 > Hex color | `value`（必填）, `submit` | 把「Hex color」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `properties.show` | `foxos photo-studio properties show` | 主界面 > Panels > Properties | — | 点击「Properties」（tab），切换到该视图 | 不适用（只读） |
| `adjustments.show` | `foxos photo-studio adjustments show` | 主界面 > Panels > Adjustments | — | 点击「Adjustments」（tab），切换到该视图 | 不适用（只读） |
| `properties-panel-menu.activate` | `foxos photo-studio properties-panel-menu activate` | 主界面 > Properties panel menu | — | 点击「Properties panel menu」（button） | 可能（应用提供撤销，未逐项验证） |
| `image-size.activate` | `foxos photo-studio image-size activate` | 主界面 > Properties > Image size | — | 点击「Image size」（button） | 可能（应用提供撤销，未逐项验证） |
| `layers.show` | `foxos photo-studio layers show` | 主界面 > Panels > Layers | — | 点击「Layers」（tab），切换到该视图 | 不适用（只读） |
| `channels.show` | `foxos photo-studio channels show` | 主界面 > Panels > Channels | — | 点击「Channels」（tab），切换到该视图 | 不适用（只读） |
| `paths.show` | `foxos photo-studio paths show` | 主界面 > Panels > Paths | — | 点击「Paths」（tab），切换到该视图 | 不适用（只读） |
| `layers-panel-menu.activate` | `foxos photo-studio layers-panel-menu activate` | 主界面 > Layers panel menu | — | 点击「Layers panel menu」（button） | 可能（应用提供撤销，未逐项验证） |
| `filter-layers-by-kind.set` | `foxos photo-studio filter-layers-by-kind set` | 主界面 > Filter layers by kind | `value`（必填）, `submit` | 把「Filter layers by kind」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `filter-layers-by-name.set` | `foxos photo-studio filter-layers-by-name set` | 主界面 > Filter layers by name | `value`（必填）, `submit` | 把「Filter layers by name」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `layer-filtering.activate` | `foxos photo-studio layer-filtering activate` | 主界面 > Layer filtering | — | 点击「Layer filtering」（button） | 可能（应用提供撤销，未逐项验证） |
| `blend-mode.set` | `foxos photo-studio blend-mode set` | 主界面 > Blend mode | `value`（必填）, `submit` | 把「Blend mode」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `opacity.set` | `foxos photo-studio opacity set` | 主界面 > Layers > Opacity % | `value`（必填）, `submit` | 把「Opacity %」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `transparency.lock` | `foxos photo-studio transparency lock` | 主界面 > Lock transparency | — | 点击「Lock transparency」（button） | 可能（应用提供撤销，未逐项验证） |
| `image-pixels.lock` | `foxos photo-studio image-pixels lock` | 主界面 > Lock image pixels | — | 点击「Lock image pixels」（button） | 可能（应用提供撤销，未逐项验证） |
| `position.lock` | `foxos photo-studio position lock` | 主界面 > Lock position | — | 点击「Lock position」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer.lock` | `foxos photo-studio layer lock` | 主界面 > Lock layer | — | 点击「Lock layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill.set` | `foxos photo-studio fill set` | 主界面 > Layers > Fill % | `value`（必填）, `submit` | 把「Fill %」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `image.create` | `foxos photo-studio image create` | 主界面 > Document layers > Add an image | — | 点击「Add an image」（button） | 可能（应用提供撤销，未逐项验证） |
| `link-layers.activate` | `foxos photo-studio link-layers activate` | 主界面 > Link layers | — | 点击「Link layers」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer-style.create` | `foxos photo-studio layer-style create` | 主界面 > Add a layer style | — | 点击「Add a layer style」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer-mask.create` | `foxos photo-studio layer-mask create` | 主界面 > Add layer mask | — | 点击「Add layer mask」（button） | 可能（应用提供撤销，未逐项验证） |
| `fill-or-adjustment-layer.create` | `foxos photo-studio fill-or-adjustment-layer create` | 主界面 > New fill or adjustment layer | — | 点击「New fill or adjustment layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `group.create` | `foxos photo-studio group create` | 主界面 > New group | — | 点击「New group」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer.create` | `foxos photo-studio layer create` | 主界面 > New layer | — | 点击「New layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `layer.delete` | `foxos photo-studio layer delete` | 主界面 > Delete layer | — | 点击「Delete layer」（button） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-out` | `foxos photo-studio view zoom-out` | 主界面 > Zoom out | — | 点击「Zoom out」（button） | 可能（应用提供撤销，未逐项验证） |
| `zoom-level.set` | `foxos photo-studio zoom-level set` | 主界面 > Zoom level | `value`（必填）, `submit` | 把「Zoom level」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `view.zoom-` | `foxos photo-studio view zoom-` | 主界面 > Zoom in | — | 点击「Zoom in」（button） | 可能（应用提供撤销，未逐项验证） |
| `document-sizes.activate` | `foxos photo-studio document-sizes activate` | 主界面 > Document Sizes: | — | 点击「Document Sizes:」（button） | 可能（应用提供撤销，未逐项验证） |
| `puter.show` | `foxos photo-studio puter show` | 主界面 > footer > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `icon.collapse` | `foxos photo-studio icon collapse` | Color panel menu > menu > Collapse to Icon | — | 点击「Collapse to Icon」（menuitem） | 不适用（只读） |
| `close.close` | `foxos photo-studio close close` | Color panel menu > menu > Close | — | 点击「Close」（menuitem） | 不适用（只读） |
| `tab-group.close` | `foxos photo-studio tab-group close` | Color panel menu > menu > Close Tab Group | — | 点击「Close Tab Group」（menuitem） | 不适用（只读） |
| `shortcut.key-0` | `foxos photo-studio shortcut key-0` | 键盘 mod+0 | — | 在当前焦点上按 mod+0（src/features/filters/liquify.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.select-all` | `foxos photo-studio selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/features/animation/panel.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.lock` | `foxos photo-studio selection lock` | 键盘 mod+l | — | 在当前焦点上按 mod+l（src/features/warp/perspective-warp.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `document.save` | `foxos photo-studio document save` | 键盘 mod+s | — | 在当前焦点上按 mod+s（src/features/scripting/code-editor.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `edit.redo` | `foxos photo-studio edit redo` | 键盘 mod+shift+z | — | 在当前焦点上按 mod+shift+z（src/features/warp/session.ts 中定义） | 不适用 |
| `clipboard.paste` | `foxos photo-studio clipboard paste` | 键盘 mod+v | — | 在当前焦点上按 mod+v（src/features/filters/perspective-planes.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `shortcut.key-w` | `foxos photo-studio shortcut key-w` | 键盘 mod+w | — | 在当前焦点上按 mod+w（src/features/warp/perspective-warp.ts 中定义） | 可能（应用提供撤销，未逐项验证） |
| `edit.undo` | `foxos photo-studio edit undo` | 键盘 mod+z | — | 在当前焦点上按 mod+z（src/features/filters/liquify.ts 中定义） | 不适用 |
