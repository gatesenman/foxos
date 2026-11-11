# 浏览器（Google Chrome）操作清单

狐狸OS 的默认浏览器是 Google Chrome（首次使用时从 Google 官方源安装，原因见 [os.md](../os.md#浏览器为什么-chrome-不在-iso-里怎么装)）。命令由同一份注册表生成 CLI 与 MCP 工具（`browser_status`、`browser_open` …）。

## 安全边界

- CDP（Chrome DevTools Protocol）**默认关闭**。只有人（human 身份）能执行 `foxos browser cdp on`；智能体执行会得到 `PERMISSION_DENIED`（退出码 4），但可以 `cdp off`。
- 打开后只绑定 `127.0.0.1`（默认端口 9222，可 `--port` 改），不对局域网开放；客户端也只连本机地址。
- 狐狸OS 启动的受控 Chrome 使用单独的配置文件 `~/.config/foxos/chrome-agent`，与你自己的 Chrome 配置分开。
- 开关在重新启动 Chrome 后生效（已在运行的 Chrome 不会突然多出调试端口）。
- 人工接管中，`open / navigate / eval / close / cdp` 返回 `PAUSED`；`status / tabs / screenshot` 仍可执行。

## 命令

| 命令 | 作用 | 需要 CDP |
| --- | --- | --- |
| `foxos browser status` | 是否安装、版本、CDP 开关 / 端口 / 是否在运行 | 否 |
| `foxos browser cdp on\|off [--port N]` | 开 / 关本机远程调试（开：仅人） | 否 |
| `foxos desktop launch chrome [URL]` | 用狐狸OS 参数启动 Chrome（与 `browser open` 同一套参数） | 否 |
| `foxos browser open URL` | CDP 在运行时新开标签页，否则启动 Chrome 打开 | 否 |
| `foxos browser tabs` | 列出标签页（id、标题、网址） | 是 |
| `foxos browser navigate URL [--tab ID]` | 跳转并等待 `document.readyState == complete` | 是 |
| `foxos browser eval JS [--tab ID]` | 执行 JavaScript，返回值（JSON 可序列化） | 是 |
| `foxos browser screenshot [--path P] [--tab ID]` | 把标签页内容存为 PNG（工作空间内） | 是 |
| `foxos browser close ID` | 关闭标签页 | 是 |

窗口级操作（聚焦、移动、缩放、键入、整屏截图）仍用 `foxos desktop …`，Chrome 是普通的 X11 窗口（`Google-chrome`）。

## 测试

US-62：`packages/core/tests/test_os_chrome.py`。在有 Chrome 与 Xvfb 的机器上真的启动 Chrome，打开工作空间里的中文页面，经 CDP 读标题、执行脚本、截图，并检查调试端口只在 127.0.0.1 上监听。
