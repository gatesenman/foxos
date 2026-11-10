# API Client（api-client）操作清单

分组：developer · 替代 Postman, Insomnia, Hoppscotch · 许可证 MIT (root LICENSE) · 页面标题「API Client」

共 59 个操作，全部有语义命令（`foxos api-client <资源> <动词>`，MCP 工具 `api-client.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account.select` | `foxos api-client account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `environment.select` | `foxos api-client environment select` | 主界面 > environment: * | `target`（必填） | 点击名称匹配的「environment: *」项（button） | 不适用（只读） |
| `requests-through.send` | `foxos api-client requests-through send` | 主界面 > send requests through: * | `target`（必填） | 点击名称匹配的「send requests through: *」项（button） | 否（应用没有撤销入口） |
| `editor.dismiss` | `foxos api-client editor dismiss` | 主界面 > Skip to editor | — | 点击「Skip to editor」（link） | 不适用（只读） |
| `collections-requests-environments.search` | `foxos api-client collections-requests-environments search` | 主界面 > Search collections, requests and environments | — | 点击「Search collections, requests and environments」（button） | 不适用（只读） |
| `import.import` | `foxos api-client import import` | 主界面 > Import | — | 点击「Import」（button） | 否（应用没有撤销入口） |
| `theme.activate` | `foxos api-client theme activate` | 主界面 > Theme | — | 点击「Theme」（button） | 否（应用没有撤销入口） |
| `settings.show` | `foxos api-client settings show` | 主界面 > Settings | — | 点击「Settings」（button），切换到该视图 | 不适用（只读） |
| `collections.activate` | `foxos api-client collections activate` | 主界面 > Sidebar sections > Collections | — | 点击「Collections」（button） | 否（应用没有撤销入口） |
| `environments.activate` | `foxos api-client environments activate` | 主界面 > Sidebar sections > Environments | — | 点击「Environments」（button） | 否（应用没有撤销入口） |
| `history.activate` | `foxos api-client history activate` | 主界面 > Sidebar sections > History | — | 点击「History」（button） | 否（应用没有撤销入口） |
| `collection.create` | `foxos api-client collection create` | 主界面 > New collection | — | 点击「New collection」（button） | 否（应用没有撤销入口） |
| `filter.set` | `foxos api-client filter set` | 主界面 > Filter | `value`（必填）, `submit` | 把「Filter」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `collection-2.create` | `foxos api-client collection-2 create` | 主界面 > Sidebar > New collection | — | 点击「New collection」（button） | 否（应用没有撤销入口） |
| `import-2.import` | `foxos api-client import-2 import` | 主界面 > Sidebar > Import | — | 点击「Import」（button） | 否（应用没有撤销入口） |
| `sidebar.resize` | `foxos api-client sidebar resize` | 主界面 > Resize sidebar | — | 点击「Resize sidebar」（separator） | 否（应用没有撤销入口） |
| `request.create` | `foxos api-client request create` | 主界面 > New request | — | 点击「New request」（button） | 否（应用没有撤销入口） |
| `open-tabs.activate` | `foxos api-client open-tabs activate` | 主界面 > All open tabs | — | 点击「All open tabs」（button） | 否（应用没有撤销入口） |
| `quick-look-at-variables.activate` | `foxos api-client quick-look-at-variables activate` | 主界面 > Quick look at variables | — | 点击「Quick look at variables」（button） | 否（应用没有撤销入口） |
| `requestctrlaltn.create` | `foxos api-client requestctrlaltn create` | 主界面 > main > New requestCtrl+Alt+N | — | 点击「New requestCtrl+Alt+N」（button） | 否（应用没有撤销入口） |
| `collection-3.create` | `foxos api-client collection-3 create` | 主界面 > main > New collection | — | 点击「New collection」（button） | 否（应用没有撤销入口） |
| `import-3.import` | `foxos api-client import-3 import` | 主界面 > main > Import | — | 点击「Import」（button） | 否（应用没有撤销入口） |
| `environment.create` | `foxos api-client environment create` | 主界面 > main > New environment | — | 点击「New environment」（button） | 否（应用没有撤销入口） |
| `websocket.create` | `foxos api-client websocket create` | 主界面 > main > New WebSocket | — | 点击「New WebSocket」（button） | 否（应用没有撤销入口） |
| `collection.run` | `foxos api-client collection run` | 主界面 > main > Run a collection | — | 点击「Run a collection」（button） | 否（应用没有撤销入口） |
| `sidebar.toggle` | `foxos api-client sidebar toggle` | 主界面 > Toggle sidebar | — | 切换「Toggle sidebar」 | 否（应用没有撤销入口） |
| `console.activate` | `foxos api-client console activate` | 主界面 > Console | — | 点击「Console」（button） | 否（应用没有撤销入口） |
| `cookies.activate` | `foxos api-client cookies activate` | 主界面 > Cookies | — | 点击「Cookies」（button） | 否（应用没有撤销入口） |
| `response-layout.activate` | `foxos api-client response-layout activate` | 主界面 > Response layout | — | 点击「Response layout」（button） | 否（应用没有撤销入口） |
| `keyboard-shortcuts.activate` | `foxos api-client keyboard-shortcuts activate` | 主界面 > Keyboard shortcuts | — | 点击「Keyboard shortcuts」（button） | 否（应用没有撤销入口） |
| `source-code-github.show` | `foxos api-client source-code-github show` | 主界面 > Source code on GitHub | — | 点击「Source code on GitHub」（link），切换到该视图 | 不适用（只读） |
| `notification.dismiss` | `foxos api-client notification dismiss` | 主界面 > Dismiss notification | — | 点击「Dismiss notification」（button） | 不适用（只读） |
| `system.activate` | `foxos api-client system activate` | Theme > Theme > System | — | 点击「System」（menuitemradio） | 否（应用没有撤销入口） |
| `light.activate` | `foxos api-client light activate` | Theme > Theme > Light | — | 点击「Light」（menuitemradio） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos api-client dark activate` | Theme > Theme > Dark | — | 点击「Dark」（menuitemradio） | 否（应用没有撤销入口） |
| `close.close` | `foxos api-client close close` | Settings > Close | — | 点击「Close」（button） | 不适用（只读） |
| `general.show` | `foxos api-client general show` | Settings > Settings sections > General | — | 点击「General」（tab），切换到该视图 | 不适用（只读） |
| `requests.show` | `foxos api-client requests show` | Settings > Settings sections > Requests | — | 点击「Requests」（tab），切换到该视图 | 不适用（只读） |
| `data.show` | `foxos api-client data show` | Settings > Settings sections > Data | — | 点击「Data」（tab），切换到该视图 | 不适用（只读） |
| `about.show` | `foxos api-client about show` | Settings > Settings sections > About | — | 点击「About」（tab），切换到该视图 | 不适用（只读） |
| `system.toggle` | `foxos api-client system toggle` | Settings > dialog > System | — | 切换「System」 | 否（应用没有撤销入口） |
| `light.toggle` | `foxos api-client light toggle` | Settings > dialog > Light | — | 切换「Light」 | 否（应用没有撤销入口） |
| `dark.toggle` | `foxos api-client dark toggle` | Settings > dialog > Dark | — | 切换「Dark」 | 否（应用没有撤销入口） |
| `below.toggle` | `foxos api-client below toggle` | Settings > dialog > Below | — | 切换「Below」 | 否（应用没有撤销入口） |
| `beside.toggle` | `foxos api-client beside toggle` | Settings > dialog > Beside | — | 切换「Beside」 | 否（应用没有撤销入口） |
| `sync-now.activate` | `foxos api-client sync-now activate` | Account: local > Account > Sync now | — | 点击「Sync now」（menuitem） | 否（应用没有撤销入口） |
| `everything.export` | `foxos api-client everything export` | Account: local > Account > Export everything | — | 点击「Export everything」（menuitem） | 否（应用没有撤销入口） |
| `websocket-request.create` | `foxos api-client websocket-request create` | All open tabs > Open tabs > New WebSocket request | — | 点击「New WebSocket request」（menuitem） | 否（应用没有撤销入口） |
| `tabs.close` | `foxos api-client tabs close` | All open tabs > Open tabs > Close all tabs | — | 点击「Close all tabs」（menuitem） | 不适用（只读） |
| `no-environment.activate` | `foxos api-client no-environment activate` | Environment: none > Environment > No environment | — | 点击「No environment」（menuitemradio） | 否（应用没有撤销入口） |
| `environment-none-environment.create` | `foxos api-client environment-none-environment create` | Environment: none > Environment > New environment | — | 点击「New environment」（menuitem） | 否（应用没有撤销入口） |
| `manage-environments.activate` | `foxos api-client manage-environments activate` | Environment: none > Environment > Manage environments | — | 点击「Manage environments」（menuitem） | 否（应用没有撤销入口） |
| `edit.update` | `foxos api-client edit update` | Quick look at variables > Variables in scope > Edit | — | 点击「Edit」（button） | 否（应用没有撤销入口） |
| `automatic.activate` | `foxos api-client automatic activate` | Send requests through: Auto > Send requests through > Automatic | — | 点击「Automatic」（menuitemradio） | 否（应用没有撤销入口） |
| `browser-only.activate` | `foxos api-client browser-only activate` | Send requests through: Auto > Send requests through > Browser only | — | 点击「Browser only」（menuitemradio） | 否（应用没有撤销入口） |
| `puter-relay.activate` | `foxos api-client puter-relay activate` | Send requests through: Auto > Send requests through > Puter relay | — | 点击「Puter relay」（menuitemradio） | 否（应用没有撤销入口） |
| `what-is-difference.activate` | `foxos api-client what-is-difference activate` | Send requests through: Auto > Send requests through > What is the difference? | — | 点击「What is the difference?」（menuitem） | 否（应用没有撤销入口） |
| `below-request.activate` | `foxos api-client below-request activate` | Response layout > Response layout > Below the request | — | 点击「Below the request」（menuitemradio） | 否（应用没有撤销入口） |
| `beside-request.activate` | `foxos api-client beside-request activate` | Response layout > Response layout > Beside the request | — | 点击「Beside the request」（menuitemradio） | 否（应用没有撤销入口） |
