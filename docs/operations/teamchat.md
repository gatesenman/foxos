# Teamchat（teamchat）操作清单

分组：collaboration · 替代 Slack, Microsoft Teams, Google Chat · 许可证 MIT (root LICENSE) · 页面标题「Teamchat」

共 6 个操作，全部有语义命令（`foxos teamchat <资源> <动词>`，MCP 工具 `teamchat.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `workspacestart-space.create` | `foxos teamchat workspacestart-space create` | 主界面 > create a workspacestart a space for * | `target`（必填） | 点击名称匹配的「create a workspacestart a space for *」项（button） | 否（应用没有撤销入口） |
| `workspacestart-space-2.create` | `foxos teamchat workspacestart-space-2 create` | 主界面 > Welcome to Teamchat > create a workspacestart a space for * | `target`（必填） | 点击名称匹配的「create a workspacestart a space for *」项（button） | 否（应用没有撤销入口） |
| `messages.dismiss` | `foxos teamchat messages dismiss` | 主界面 > Skip to messages | — | 点击「Skip to messages」（link） | 不适用（只读） |
| `invitepaste-code-or-link.join` | `foxos teamchat invitepaste-code-or-link join` | 主界面 > Join with an invitePaste a code or link | — | 点击「Join with an invitePaste a code or link」（button） | 否（应用没有撤销入口） |
| `puter.show` | `foxos teamchat puter show` | 主界面 > Puter | — | 点击「Puter」（link），切换到该视图 | 不适用（只读） |
| `close.close` | `foxos teamchat close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
