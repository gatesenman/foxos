# Video Studio（video-studio）操作清单

分组：creative · 替代 CapCut, Adobe Premiere Pro, Final Cut Pro, DaVinci Resolve · 许可证 AGPL-3.0-only · 页面标题「Video Studio」

共 34 个操作，全部有语义命令（`foxos video-studio <资源> <动词>`，MCP 工具 `video-studio.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account.select` | `foxos video-studio account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `browse-ready-made-projects-make-own.select` | `foxos video-studio browse-ready-made-projects-make-own select` | 主界面 > Quick start > browse # ready-made projects to make your own | `target`（必填） | 点击名称匹配的「browse # ready-made projects to make your own」项（button） | 不适用（只读） |
| `youtube-project.select` | `foxos video-studio youtube-project select` | 主界面 > # youtube, new project | `target`（必填） | 点击名称匹配的「# youtube, new project」项（button） | 不适用（只读） |
| `vertical-project.select` | `foxos video-studio vertical-project select` | 主界面 > # vertical, new project | `target`（必填） | 点击名称匹配的「# vertical, new project」项（button） | 不适用（只读） |
| `square-project.select` | `foxos video-studio square-project select` | 主界面 > # square, new project | `target`（必填） | 点击名称匹配的「# square, new project」项（button） | 不适用（只读） |
| `classic-project.select` | `foxos video-studio classic-project select` | 主界面 > # classic, new project | `target`（必填） | 点击名称匹配的「# classic, new project」项（button） | 不适用（只读） |
| `portrait-project.select` | `foxos video-studio portrait-project select` | 主界面 > # portrait, new project | `target`（必填） | 点击名称匹配的「# portrait, new project」项（button） | 不适用（只读） |
| `feed-post-project.select` | `foxos video-studio feed-post-project select` | 主界面 > # feed post, new project | `target`（必填） | 点击名称匹配的「# feed post, new project」项（button） | 不适用（只读） |
| `cinema-project.select` | `foxos video-studio cinema-project select` | 主界面 > # cinema, new project | `target`（必填） | 点击名称匹配的「# cinema, new project」项（button） | 不适用（只读） |
| `item.select` | `foxos video-studio item select` | 主界面 > # title intro, intros and outros, # a bold title over a glowing backdrop with a slow push in. | `target`（必填） | 点击名称匹配的「# title intro, intros and outros, # a bold title over a glowing backdrop with a slow push in.」项（button） | 不适用（只读） |
| `item-2.select` | `foxos video-studio item-2 select` | 主界面 > # photo slideshow, slideshows, # slots. four photo slots with gentle motion, soft transitions and captions. | `target`（必填） | 点击名称匹配的「# photo slideshow, slideshows, # slots. four photo slots with gentle motion, soft transitions and captions.」项（button） | 不适用（只读） |
| `item-3.select` | `foxos video-studio item-3 select` | 主界面 > # quote card, social, # a typed-out quote with an author line on a warm paper backdrop. | `target`（必填） | 点击名称匹配的「# quote card, social, # a typed-out quote with an author line on a warm paper backdrop.」项（button） | 不适用（只读） |
| `item-4.select` | `foxos video-studio item-4 select` | 主界面 > # countdown, intros and outros, # five, four, three, two, one with a pulsing ring and a flash at go. | `target`（必填） | 点击名称匹配的「# countdown, intros and outros, # five, four, three, two, one with a pulsing ring and a flash at go.」项（button） | 不适用（只读） |
| `item-5.select` | `foxos video-studio item-5 select` | 主界面 > # product promo, business, # slot. show off a product with a price burst and a call to action. | `target`（必填） | 点击名称匹配的「# product promo, business, # slot. show off a product with a price burst and a call to action.」项（button） | 不适用（只读） |
| `item-6.select` | `foxos video-studio item-6 select` | 主界面 > # vertical story, social, # slots. three tall photo slots that push up, with neon and script titles. | `target`（必填） | 点击名称匹配的「# vertical story, social, # slots. three tall photo slots that push up, with neon and script titles.」项（button） | 不适用（只读） |
| `editor.dismiss` | `foxos video-studio editor dismiss` | 主界面 > Skip to editor | — | 点击「Skip to editor」（link） | 不适用（只读） |
| `home.show` | `foxos video-studio home show` | 主界面 > Home sections > Home | — | 点击「Home」（link），切换到该视图 | 不适用（只读） |
| `templates.show` | `foxos video-studio templates show` | 主界面 > Home sections > Templates | — | 点击「Templates」（link），切换到该视图 | 不适用（只读） |
| `trash.delete` | `foxos video-studio trash delete` | 主界面 > Home sections > Trash | — | 点击「Trash」（link） | 否（应用没有撤销入口） |
| `editopen-media-project.import` | `foxos video-studio editopen-media-project import` | 主界面 > Quick start > Import and editOpen media in a new project | — | 点击「Import and editOpen media in a new project」（button） | 否（应用没有撤销入口） |
| `see.show` | `foxos video-studio see show` | 主界面 > main > See all | — | 点击「See all」（link），切换到该视图 | 不适用（只读） |
| `search-projects.set` | `foxos video-studio search-projects set` | 主界面 > Search projects | `value`（必填）, `submit` | 把「Search projects」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sort.sort` | `foxos video-studio sort sort` | 主界面 > main > Sort | — | 点击「Sort」（button） | 不适用（只读） |
| `as-list.show` | `foxos video-studio as-list show` | 主界面 > Show as list | — | 点击「Show as list」（button），切换到该视图 | 不适用（只读） |
| `project-actions.show` | `foxos video-studio project-actions show` | 主界面 > More project actions | — | 点击「More project actions」（button），切换到该视图 | 不适用（只读） |
| `powered-by-puter.show` | `foxos video-studio powered-by-puter show` | 主界面 > footer > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `theme.activate` | `foxos video-studio theme activate` | Account: local > Account > Theme | — | 点击「Theme」（menuitem） | 否（应用没有撤销入口） |
| `last-modified.activate` | `foxos video-studio last-modified activate` | Sort > Sort projects > Last modified | — | 点击「Last modified」（menuitemradio） | 否（应用没有撤销入口） |
| `date-created.activate` | `foxos video-studio date-created activate` | Sort > Sort projects > Date created | — | 点击「Date created」（menuitemradio） | 否（应用没有撤销入口） |
| `name.activate` | `foxos video-studio name activate` | Sort > Sort projects > Name | — | 点击「Name」（menuitemradio） | 否（应用没有撤销入口） |
| `project-file.open` | `foxos video-studio project-file open` | More project actions > More project actions > Open project file... | — | 点击「Open project file...」（menuitem） | 不适用（只读） |
| `media.import` | `foxos video-studio media import` | More project actions > More project actions > Import media... | — | 点击「Import media...」（menuitem） | 否（应用没有撤销入口） |
| `more-project-actions-trash.delete` | `foxos video-studio more-project-actions-trash delete` | More project actions > More project actions > Trash | — | 点击「Trash」（menuitem） | 否（应用没有撤销入口） |
| `selection.select-all` | `foxos video-studio selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/ui/panels/media.js 中定义） | 否（应用没有撤销入口） |
