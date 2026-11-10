# Contacts（contacts）操作清单

分组：collaboration · 替代 Google Contacts, Apple Contacts · 许可证 MIT (root LICENSE) · 页面标题「Contacts — Your address book, in the cloud」

共 28 个操作，全部有语义命令（`foxos contacts <资源> <动词>`，MCP 工具 `contacts.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account-menu.activate` | `foxos contacts account-menu activate` | 主界面 > Account menu | — | 点击「Account menu」（button） | 否（应用没有撤销入口） |
| `smart-add.activate` | `foxos contacts smart-add activate` | 主界面 > Smart add | — | 点击「Smart add」（button） | 否（应用没有撤销入口） |
| `contact.create` | `foxos contacts contact create` | 主界面 > New contact | — | 点击「New contact」（button） | 否（应用没有撤销入口） |
| `search-contacts.set` | `foxos contacts search-contacts set` | 主界面 > Search contacts | `value`（必填）, `submit` | 把「Search contacts」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `list-options.activate` | `foxos contacts list-options activate` | 主界面 > List options | — | 点击「List options」（button） | 否（应用没有撤销入口） |
| `favorites.activate` | `foxos contacts favorites activate` | 主界面 > aside > Favorites | — | 点击「Favorites」（button） | 否（应用没有撤销入口） |
| `contact-2.create` | `foxos contacts contact-2 create` | 主界面 > aside > New contact | — | 点击「New contact」（button） | 否（应用没有撤销入口） |
| `import.import` | `foxos contacts import import` | 主界面 > aside > Import | — | 点击「Import」（button） | 否（应用没有撤销入口） |
| `contact-3.create` | `foxos contacts contact-3 create` | 主界面 > main > New contact | — | 点击「New contact」（button） | 否（应用没有撤销入口） |
| `set-photo.activate` | `foxos contacts set-photo activate` | New contact > Set photo | — | 点击「Set photo」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos contacts close close` | New contact > Close | — | 点击「Close」（button） | 不适用（只读） |
| `first-name.set` | `foxos contacts first-name set` | New contact > dialog > First name | `value`（必填）, `submit` | 把「First name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `last-name.set` | `foxos contacts last-name set` | New contact > dialog > Last name | `value`（必填）, `submit` | 把「Last name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `nickname.set` | `foxos contacts nickname set` | New contact > dialog > Nickname | `value`（必填）, `submit` | 把「Nickname」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `company.set` | `foxos contacts company set` | New contact > dialog > Company | `value`（必填）, `submit` | 把「Company」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `job-title.set` | `foxos contacts job-title set` | New contact > dialog > Job title | `value`（必填）, `submit` | 把「Job title」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `email.create` | `foxos contacts email create` | New contact > dialog > Add email | — | 点击「Add email」（button） | 否（应用没有撤销入口） |
| `phone.create` | `foxos contacts phone create` | New contact > dialog > Add phone | — | 点击「Add phone」（button） | 否（应用没有撤销入口） |
| `link.create` | `foxos contacts link create` | New contact > dialog > Add link | — | 点击「Add link」（button） | 否（应用没有撤销入口） |
| `address.create` | `foxos contacts address create` | New contact > dialog > Add address | — | 点击「Add address」（button） | 否（应用没有撤销入口） |
| `birthday.set` | `foxos contacts birthday set` | New contact > dialog > Birthday | `value`（必填）, `submit` | 把「Birthday」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `hide-year.toggle` | `foxos contacts hide-year toggle` | New contact > dialog > Hide year | — | 切换「Hide year」 | 否（应用没有撤销入口） |
| `tags.set` | `foxos contacts tags set` | New contact > dialog > Tags | `value`（必填）, `submit` | 把「Tags」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `notes.set` | `foxos contacts notes set` | New contact > dialog > Notes | `value`（必填）, `submit` | 把「Notes」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `add-favorites.toggle` | `foxos contacts add-favorites toggle` | New contact > dialog > Add to favorites | — | 切换「Add to favorites」 | 否（应用没有撤销入口） |
| `cancel.cancel` | `foxos contacts cancel cancel` | New contact > footer > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `contact-4.create` | `foxos contacts contact-4 create` | New contact > footer > Add contact | — | 点击「Add contact」（button） | 否（应用没有撤销入口） |
| `selection.select-all` | `foxos contacts selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/ui/app.js 中定义） | 否（应用没有撤销入口） |
