# Wiki（wiki）操作清单

分组：productivity · 替代 Notion, Confluence, Coda · 许可证 MIT (root LICENSE) · 页面标题「Getting started - Wiki」

共 60 个操作，全部有语义命令（`foxos wiki <资源> <动词>`，MCP 工具 `wiki.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `heading.select` | `foxos wiki heading select` | 主界面 > heading # | `target`（必填） | 点击名称匹配的「heading #」项（textbox） | 不适用（只读） |
| `files.import` | `foxos wiki files import` | Settings > dialog > import # files | `target`（必填） | 点击名称匹配的「import # files」项（button） | 可能（应用提供撤销，未逐项验证） |
| `here.import` | `foxos wiki here import` | Page options > Getting started options > import # here | `target`（必填） | 点击名称匹配的「import # here」项（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `page.dismiss` | `foxos wiki page dismiss` | 主界面 > Skip to page | — | 点击「Skip to page」（link） | 不适用（只读） |
| `lolocal-s-wiki.activate` | `foxos wiki lolocal-s-wiki activate` | 主界面 > Sidebar > LOlocal’s wiki | — | 点击「LOlocal’s wiki」（button） | 可能（应用提供撤销，未逐项验证） |
| `sidebar.close` | `foxos wiki sidebar close` | 主界面 > Close sidebar | — | 点击「Close sidebar」（button） | 不适用（只读） |
| `searchctrlk.activate` | `foxos wiki searchctrlk activate` | 主界面 > Workspace > SearchCtrl+K | — | 点击「SearchCtrl+K」（button） | 可能（应用提供撤销，未逐项验证） |
| `home.activate` | `foxos wiki home activate` | 主界面 > Workspace > Home | — | 点击「Home」（button） | 可能（应用提供撤销，未逐项验证） |
| `pagectrlaltn.create` | `foxos wiki pagectrlaltn create` | 主界面 > Workspace > New pageCtrl+Alt+N | — | 点击「New pageCtrl+Alt+N」（button） | 可能（应用提供撤销，未逐项验证） |
| `private.activate` | `foxos wiki private activate` | 主界面 > Private > Private | — | 点击「Private」（button） | 可能（应用提供撤销，未逐项验证） |
| `private-page.create` | `foxos wiki private-page create` | 主界面 > Add a private page | — | 点击「Add a private page」（button） | 可能（应用提供撤销，未逐项验证） |
| `getting-started.activate` | `foxos wiki getting-started activate` | 主界面 > Getting started | — | 点击「Getting started」（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `tasks.activate` | `foxos wiki tasks activate` | 主界面 > Tasks | — | 点击「Tasks」（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `notes.activate` | `foxos wiki notes activate` | 主界面 > Notes | — | 点击「Notes」（treeitem） | 可能（应用提供撤销，未逐项验证） |
| `templates.activate` | `foxos wiki templates activate` | 主界面 > Sidebar > Templates | — | 点击「Templates」（button） | 可能（应用提供撤销，未逐项验证） |
| `import.import` | `foxos wiki import import` | 主界面 > Sidebar > Import | — | 点击「Import」（button） | 可能（应用提供撤销，未逐项验证） |
| `trash.delete` | `foxos wiki trash delete` | 主界面 > Sidebar > Trash | — | 点击「Trash」（button） | 可能（应用提供撤销，未逐项验证） |
| `settings.show` | `foxos wiki settings show` | 主界面 > Sidebar > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `powered-by-puter.show` | `foxos wiki powered-by-puter show` | 主界面 > Sidebar > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `sidebar.resize` | `foxos wiki sidebar resize` | 主界面 > Resize sidebar | — | 点击「Resize sidebar」（separator） | 可能（应用提供撤销，未逐项验证） |
| `getting-started-2.activate` | `foxos wiki getting-started-2 activate` | 主界面 > Breadcrumb > Getting started | — | 点击「Getting started」（button） | 可能（应用提供撤销，未逐项验证） |
| `share.share` | `foxos wiki share share` | 主界面 > header > Share | — | 点击「Share」（button） | 可能（应用提供撤销，未逐项验证） |
| `comments.activate` | `foxos wiki comments activate` | 主界面 > Comments | — | 点击「Comments」（button） | 可能（应用提供撤销，未逐项验证） |
| `favorites.create` | `foxos wiki favorites create` | 主界面 > Add to favorites | — | 点击「Add to favorites」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-options.activate` | `foxos wiki page-options activate` | 主界面 > Page options | — | 点击「Page options」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-icon.update` | `foxos wiki page-icon update` | 主界面 > Change page icon | — | 点击「Change page icon」（button） | 可能（应用提供撤销，未逐项验证） |
| `cover.create` | `foxos wiki cover create` | 主界面 > header > Add cover | — | 点击「Add cover」（button） | 可能（应用提供撤销，未逐项验证） |
| `getting-started.set` | `foxos wiki getting-started set` | 主界面 > header > Getting started | `value`（必填）, `submit` | 把「Getting started」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `callout-icon.update` | `foxos wiki callout-icon update` | 主界面 > Change callout icon | — | 点击「Change callout icon」（button） | 可能（应用提供撤销，未逐项验证） |
| `callout.set` | `foxos wiki callout set` | 主界面 > Callout | `value`（必填）, `submit` | 把「Callout」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `text.set` | `foxos wiki text set` | 主界面 > Text | `value`（必填）, `submit` | 把「Text」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `bulleted-list.set` | `foxos wiki bulleted-list set` | 主界面 > Bulleted list | `value`（必填）, `submit` | 把「Bulleted list」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `done.toggle` | `foxos wiki done toggle` | 主界面 > Done | — | 切换「Done」 | 可能（应用提供撤销，未逐项验证） |
| `to-do-list.set` | `foxos wiki to-do-list set` | 主界面 > To-do list | `value`（必填）, `submit` | 把「To-do list」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `content.hide` | `foxos wiki content hide` | 主界面 > Hide content | — | 点击「Hide content」（button） | 不适用（只读） |
| `toggle-list.set` | `foxos wiki toggle-list set` | 主界面 > Toggle list | `value`（必填）, `submit` | 把「Toggle list」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `quote.set` | `foxos wiki quote set` | 主界面 > Quote | `value`（必填）, `submit` | 把「Quote」设为给定值（触发 input / change 事件） | 可能（应用提供撤销，未逐项验证） |
| `theme.activate` | `foxos wiki theme activate` | LOlocal’s wiki > Account > Theme | — | 点击「Theme」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `lolocals-wiki-settings.show` | `foxos wiki lolocals-wiki-settings show` | LOlocal’s wiki > Account > Settings | — | 点击「Settings」（menuitem），切换到该视图 | 不适用（只读） |
| `keyboard-shortcutsctrl.activate` | `foxos wiki keyboard-shortcutsctrl activate` | LOlocal’s wiki > Account > Keyboard shortcutsCtrl+/ | — | 点击「Keyboard shortcutsCtrl+/」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `close.close` | `foxos wiki close close` | Settings > Close | — | 点击「Close」（button） | 不适用（只读） |
| `system.toggle` | `foxos wiki system toggle` | Settings > Theme > System | — | 切换「System」 | 可能（应用提供撤销，未逐项验证） |
| `light.toggle` | `foxos wiki light toggle` | Settings > Theme > Light | — | 切换「Light」 | 可能（应用提供撤销，未逐项验证） |
| `dark.toggle` | `foxos wiki dark toggle` | Settings > Theme > Dark | — | 切换「Dark」 | 可能（应用提供撤销，未逐项验证） |
| `settings-powered-by-puter.show` | `foxos wiki settings-powered-by-puter show` | Settings > dialog > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `page.share` | `foxos wiki page share` | Share > dialog > Share this page | — | 点击「Share this page」（button） | 可能（应用提供撤销，未逐项验证） |
| `page-options-favorites.create` | `foxos wiki page-options-favorites create` | Page options > Getting started options > Add to favorites | — | 点击「Add to favorites」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `link.copy` | `foxos wiki link copy` | Page options > Getting started options > Copy link | — | 点击「Copy link」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `duplicate.duplicate` | `foxos wiki duplicate duplicate` | Page options > Getting started options > Duplicate | — | 点击「Duplicate」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `move.move` | `foxos wiki move move` | Page options > Getting started options > Move to | — | 点击「Move to」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `page.lock` | `foxos wiki page lock` | Page options > Getting started options > Lock page | — | 点击「Lock page」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `export.export` | `foxos wiki export export` | Page options > Getting started options > Export | — | 点击「Export」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `page-history.activate` | `foxos wiki page-history activate` | Page options > Getting started options > Page history | — | 点击「Page history」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `trash.move` | `foxos wiki trash move` | Page options > Getting started options > Move to trash | — | 点击「Move to trash」（menuitem） | 可能（应用提供撤销，未逐项验证） |
| `selection.select-all` | `foxos wiki selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/editor/editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.copy` | `foxos wiki selection copy` | 键盘 mod+c | — | 在当前焦点上按 mod+c（src/editor/editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `selection.duplicate` | `foxos wiki selection duplicate` | 键盘 mod+d | — | 在当前焦点上按 mod+d（src/editor/editor.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `command-palette.show` | `foxos wiki command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/app.js 中定义） | 不适用 |
| `selection.lock-shift` | `foxos wiki selection lock-shift` | 键盘 mod+shift+l | — | 在当前焦点上按 mod+shift+l（src/ui/app.js 中定义） | 可能（应用提供撤销，未逐项验证） |
| `edit.undo` | `foxos wiki edit undo` | 键盘 mod+z | — | 在当前焦点上按 mod+z（src/editor/editor.js 中定义） | 不适用 |
