# Email（email）操作清单

分组：collaboration · 替代 Gmail, Microsoft Outlook, Apple Mail · 许可证 AGPL-3.0-only · 页面标题「Puter Mail」

共 2 个操作，全部有语义命令（`foxos email <资源> <动词>`，MCP 工具 `email.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `grant-read-access.activate` | `foxos email grant-read-access activate` | 主界面 > Grant read access | — | 点击「Grant read access」（button） | 否（应用没有撤销入口） |
| `command-palette.show` | `foxos email command-palette show` | 键盘 mod+k | — | 在当前焦点上按 mod+k（src/ui/editor.js 中定义） | 不适用 |
