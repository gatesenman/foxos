# 桌面会话操作清单

这是狐狸OS **真实图形会话**（XFCE / X11，窗口管理器为 xfwm4）上的操作，不是 Electron 外壳里画的假窗口。命令由同一份注册表生成 CLI 与 MCP 工具。

`foxos desktop …` 与 `foxos session …` 是同一组动词。人工接管也可以继续用 `foxos control pause|resume|status`。

## 环境

- 需要正在运行的 X11 会话（`DISPLAY` 指向狐狸OS 的 XFCE 桌面）。狐狸OS ISO 默认自动登录到这个会话。
- 窗口列表 / 聚焦 / 关闭 / 移动 / 缩放走 `wmctrl`；键入与点击用 `xdotool`；截图用 `scrot`（若无 scrot 则用 `maim`）。这些工具在 ISO 里已预装。
- 程序化移动 / 缩放在 XFCE / X11 上可用。若当前没有图形显示，命令返回 `DEPENDENCY_MISSING`。测试可用 `FOXOS_SESSION_BACKEND=fake`。
- 若只有 Wayland 显示（`WAYLAND_DISPLAY`）而没有 X11，会改用原来的 wlroots 后端（`wtype` / `grim`），不是本系统的默认会话。
- 人工接管中，非人身份的写操作（type / click / move / close / launch / key / takeover）返回 `PAUSED`。列出窗口、状态、截图仍可执行。

## 命令

| 命令 | 作用 |
| --- | --- |
| `foxos desktop status` | 会话与接管状态 |
| `foxos desktop windows` | 列出真实窗口（id、标题、app_id、是否聚焦） |
| `foxos desktop focus WINDOW` | 聚焦 |
| `foxos desktop move WINDOW --x --y` | 移动 |
| `foxos desktop resize WINDOW --width --height` | 缩放 |
| `foxos desktop close WINDOW` | 关闭 |
| `foxos desktop launch -- CMD…` | 启动应用 |
| `foxos desktop type TEXT` | 向聚焦窗口键入 |
| `foxos desktop key KEYS` | 按键，例如 `Return`、`ctrl+c` |
| `foxos desktop click --x --y [--button 1]` | 点击 |
| `foxos desktop screenshot [--path shots/desk.png]` | 截图（工作空间内） |
| `foxos desktop takeover [--reason …]` | 人工接管（仅人的身份） |
| `foxos desktop resume` | 结束接管 |

MCP 工具名为 `desktop_windows`、`desktop_focus`、`session_takeover` 等，与 CLI 走同一内核。用户故事：US-60。
