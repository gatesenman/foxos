# 狐狸OS MCP 工具参考

> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos mcp` 的 tools/list 同源，请勿手改。

## 连接与调用

- stdio：`foxos --workspace <目录> mcp`；Streamable HTTP：`foxos --workspace <目录> mcp --http 127.0.0.1:8765 --token <令牌>`（POST /mcp）
- `--profile compact`（默认）：内置应用全部工具 + Everything 元工具；`--apps a,b`：额外暴露这些应用的全部工具；`--profile full`：全部工具
- `--tool-names dotted`：工具名用点分命令 ID（如 `tasks.add-task.set`），默认用下划线（`tasks_add-task_set`）

## 返回格式（所有工具相同）

成功：`isError=false`，`structuredContent` 为 `{"ok": true, "command": "<命令 ID>", "result": {...}}`，`content[0].text` 为同一 JSON 文本。

失败：`isError=true`，`structuredContent` 为 `{"ok": false, "command": ..., "error": {"code": "LOCKED", "exit_code": 5, "message": ..., "hint": ..., "details": {...}}}`。

错误码：USAGE(2) NOT_FOUND(3) PERMISSION_DENIED(4) LOCKED(5) DEPENDENCY_MISSING(6) CONFLICT(7) PAUSED(8) ERROR(1)。

共 4349 个工具。

## desktop（13 个工具）

### `desktop_status`

显示当前图形会话与人工接管状态。CLI：foxos desktop status。示例：foxos desktop status --json

只读：是 · 破坏性：否 · CLI：`foxos desktop status`

调用示例：

```json
{"name": "desktop_status", "arguments": {}}
```

### `desktop_windows`

列出合成器管理的真实窗口。CLI：foxos desktop windows。示例：foxos desktop windows --json

只读：是 · 破坏性：否 · CLI：`foxos desktop windows`

调用示例：

```json
{"name": "desktop_windows", "arguments": {}}
```

### `desktop_focus`

聚焦一个窗口。CLI：foxos desktop focus WINDOW。示例：foxos desktop focus 4278190080

只读：否 · 破坏性：否 · CLI：`foxos desktop focus`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |

调用示例：

```json
{"name": "desktop_focus", "arguments": {"window": "…"}}
```

### `desktop_move`

移动一个窗口。CLI：foxos desktop move WINDOW --x X --y Y。示例：foxos desktop move 4278190080 --x 100 --y 80

只读：否 · 破坏性：否 · CLI：`foxos desktop move`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |

调用示例：

```json
{"name": "desktop_move", "arguments": {"window": "…", "x": 1, "y": 1}}
```

### `desktop_resize`

调整一个窗口的大小。CLI：foxos desktop resize WINDOW --width WIDTH --height HEIGHT。示例：foxos desktop resize 4278190080 --width 800 --height 600

只读：否 · 破坏性：否 · CLI：`foxos desktop resize`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | integer | 是 | 宽度（像素） |
| `height` | integer | 是 | 高度（像素） |

调用示例：

```json
{"name": "desktop_resize", "arguments": {"window": "…", "width": 1, "height": 1}}
```

### `desktop_close`

关闭一个窗口。CLI：foxos desktop close WINDOW。示例：foxos desktop close 4278190080

只读：否 · 破坏性：否 · CLI：`foxos desktop close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |

调用示例：

```json
{"name": "desktop_close", "arguments": {"window": "…"}}
```

### `desktop_launch`

启动一个应用或命令。CLI：foxos desktop launch CMD...。示例：foxos desktop launch -- gnome-terminal

只读：否 · 破坏性：否 · CLI：`foxos desktop launch`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array | 是 | 要启动的命令和参数 |

调用示例：

```json
{"name": "desktop_launch", "arguments": {"command": []}}
```

### `desktop_type`

向当前聚焦的窗口键入文本。CLI：foxos desktop type TEXT。示例：foxos desktop type 'hello'

只读：否 · 破坏性：否 · CLI：`foxos desktop type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要键入的文本 |

调用示例：

```json
{"name": "desktop_type", "arguments": {"text": "…"}}
```

### `desktop_key`

发送按键或组合键。CLI：foxos desktop key KEYS。示例：foxos desktop key Return

只读：否 · 破坏性：否 · CLI：`foxos desktop key`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keys` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |

调用示例：

```json
{"name": "desktop_key", "arguments": {"keys": "…"}}
```

### `desktop_click`

在屏幕坐标处点击。CLI：foxos desktop click --x X --y Y [--button BUTTON]。示例：foxos desktop click --x 400 --y 300

只读：否 · 破坏性：否 · CLI：`foxos desktop click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键 |

调用示例：

```json
{"name": "desktop_click", "arguments": {"x": 1, "y": 1}}
```

### `desktop_screenshot`

截取当前会话画面。CLI：foxos desktop screenshot [--path PATH]。示例：foxos desktop screenshot --path shots/desk.png

只读：是 · 破坏性：否 · CLI：`foxos desktop screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/） |

调用示例：

```json
{"name": "desktop_screenshot", "arguments": {}}
```

### `desktop_takeover`

人工接管：暂停智能体的写操作。CLI：foxos desktop takeover [--reason REASON]。限制：只有 human 身份可以执行。示例：foxos desktop takeover --reason 我来改

只读：否 · 破坏性：否 · CLI：`foxos desktop takeover`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |

调用示例：

```json
{"name": "desktop_takeover", "arguments": {}}
```

### `desktop_resume`

结束人工接管，恢复智能体写操作。CLI：foxos desktop resume。限制：只有 human 身份可以执行。示例：foxos desktop resume

只读：否 · 破坏性：否 · CLI：`foxos desktop resume`

调用示例：

```json
{"name": "desktop_resume", "arguments": {}}
```

## session（13 个工具）

### `session_status`

显示当前图形会话与人工接管状态。CLI：foxos session status。示例：foxos session status --json

只读：是 · 破坏性：否 · CLI：`foxos session status`

调用示例：

```json
{"name": "session_status", "arguments": {}}
```

### `session_windows`

列出合成器管理的真实窗口。CLI：foxos session windows。示例：foxos session windows --json

只读：是 · 破坏性：否 · CLI：`foxos session windows`

调用示例：

```json
{"name": "session_windows", "arguments": {}}
```

### `session_focus`

聚焦一个窗口。CLI：foxos session focus WINDOW。示例：foxos session focus 4278190080

只读：否 · 破坏性：否 · CLI：`foxos session focus`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |

调用示例：

```json
{"name": "session_focus", "arguments": {"window": "…"}}
```

### `session_move`

移动一个窗口。CLI：foxos session move WINDOW --x X --y Y。示例：foxos session move 4278190080 --x 100 --y 80

只读：否 · 破坏性：否 · CLI：`foxos session move`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |

调用示例：

```json
{"name": "session_move", "arguments": {"window": "…", "x": 1, "y": 1}}
```

### `session_resize`

调整一个窗口的大小。CLI：foxos session resize WINDOW --width WIDTH --height HEIGHT。示例：foxos session resize 4278190080 --width 800 --height 600

只读：否 · 破坏性：否 · CLI：`foxos session resize`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |
| `width` | integer | 是 | 宽度（像素） |
| `height` | integer | 是 | 高度（像素） |

调用示例：

```json
{"name": "session_resize", "arguments": {"window": "…", "width": 1, "height": 1}}
```

### `session_close`

关闭一个窗口。CLI：foxos session close WINDOW。示例：foxos session close 4278190080

只读：否 · 破坏性：否 · CLI：`foxos session close`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `window` | string | 是 | 窗口编号（见 windows 命令） |

调用示例：

```json
{"name": "session_close", "arguments": {"window": "…"}}
```

### `session_launch`

启动一个应用或命令。CLI：foxos session launch CMD...。示例：foxos session launch -- gnome-terminal

只读：否 · 破坏性：否 · CLI：`foxos session launch`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array | 是 | 要启动的命令和参数 |

调用示例：

```json
{"name": "session_launch", "arguments": {"command": []}}
```

### `session_type`

向当前聚焦的窗口键入文本。CLI：foxos session type TEXT。示例：foxos session type 'hello'

只读：否 · 破坏性：否 · CLI：`foxos session type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要键入的文本 |

调用示例：

```json
{"name": "session_type", "arguments": {"text": "…"}}
```

### `session_key`

发送按键或组合键。CLI：foxos session key KEYS。示例：foxos session key Return

只读：否 · 破坏性：否 · CLI：`foxos session key`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keys` | string | 是 | 按键名，例如 Return，或组合键 ctrl+c |

调用示例：

```json
{"name": "session_key", "arguments": {"keys": "…"}}
```

### `session_click`

在屏幕坐标处点击。CLI：foxos session click --x X --y Y [--button BUTTON]。示例：foxos session click --x 400 --y 300

只读：否 · 破坏性：否 · CLI：`foxos session click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `x` | integer | 是 | X 坐标（像素） |
| `y` | integer | 是 | Y 坐标（像素） |
| `button` | integer |  | 鼠标按钮：1 左键、2 中键、3 右键 |

调用示例：

```json
{"name": "session_click", "arguments": {"x": 1, "y": 1}}
```

### `session_screenshot`

截取当前会话画面。CLI：foxos session screenshot [--path PATH]。示例：foxos session screenshot --path shots/desk.png

只读：是 · 破坏性：否 · CLI：`foxos session screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 工作空间内的 PNG 路径（缺省写到 .foxos/screenshots/） |

调用示例：

```json
{"name": "session_screenshot", "arguments": {}}
```

### `session_takeover`

人工接管：暂停智能体的写操作。CLI：foxos session takeover [--reason REASON]。限制：只有 human 身份可以执行。示例：foxos session takeover --reason 我来改

只读：否 · 破坏性：否 · CLI：`foxos session takeover`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |

调用示例：

```json
{"name": "session_takeover", "arguments": {}}
```

### `session_resume`

结束人工接管，恢复智能体写操作。CLI：foxos session resume。限制：只有 human 身份可以执行。示例：foxos session resume

只读：否 · 破坏性：否 · CLI：`foxos session resume`

调用示例：

```json
{"name": "session_resume", "arguments": {}}
```

## docs（5 个工具）

### `docs_create`

新建一个 .docx 文档。CLI：foxos docs create FILE [--title TITLE] [--force]。示例：foxos docs create report.docx --title '2026 年销售分析'

只读：否 · 破坏性：否 · CLI：`foxos docs create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `title` | string |  | 文档标题（写成 Title 样式的第一段，并写入文档属性） |
| `force` | boolean |  | 已存在时覆盖 |

调用示例：

```json
{"name": "docs_create", "arguments": {"file": "…"}}
```

### `docs_read`

读取文档段落（含样式名）、表格与字数统计。CLI：foxos docs read FILE。示例：foxos docs read report.docx --json

只读：是 · 破坏性：否 · CLI：`foxos docs read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |

调用示例：

```json
{"name": "docs_read", "arguments": {"file": "…"}}
```

### `docs_append`

在文档末尾追加段落、标题或表格。CLI：foxos docs append FILE [TEXT...] [--style STYLE] [--heading HEADING] [--table TABLE]。示例：foxos docs append report.docx '一、总体情况' --heading 1

只读：否 · 破坏性：否 · CLI：`foxos docs append`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `text` | array |  | 要追加的段落，每个参数一段 |
| `style` | string |  | 段落样式（Word 内置英文名），如 List Bullet、Quote |
| `heading` | integer |  | 作为标题追加：0=Title，1–9=Heading 1–9 |
| `table` | array |  | 追加表格：二维数组；CLI 中用 --table-json |

调用示例：

```json
{"name": "docs_append", "arguments": {"file": "…"}}
```

### `docs_replace`

查找并替换文本（正文与表格）。CLI：foxos docs replace FILE --find FIND --replace REPLACE。示例：foxos docs replace report.docx --find 2025 --replace 2026

只读：否 · 破坏性：否 · CLI：`foxos docs replace`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `find` | string | 是 | 要查找的文本 |
| `replace` | string | 是 | 替换为 |

调用示例：

```json
{"name": "docs_replace", "arguments": {"file": "…", "find": "…", "replace": "…"}}
```

### `docs_export`

导出为 pdf / odt / html / txt / md（由扩展名决定）。CLI：foxos docs export FILE OUTPUT [--force]。限制：pdf / odt / html 需要 LibreOffice。示例：foxos docs export report.docx report.pdf

只读：否 · 破坏性：否 · CLI：`foxos docs export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 文档路径（.docx） |
| `output` | string | 是 | 输出路径 |
| `force` | boolean |  | 输出已存在时覆盖 |

调用示例：

```json
{"name": "docs_export", "arguments": {"file": "…", "output": "…"}}
```

## env（30 个工具）

### `env_images`

列出可用镜像（官方发行版 rootfs）与本地镜像。CLI：foxos env images。示例：foxos env images --json

只读：是 · 破坏性：否 · CLI：`foxos env images`

调用示例：

```json
{"name": "env_images", "arguments": {}}
```

### `env_pull`

下载镜像并校验 sha256（目录 ID、https 地址或 .foxenv 文件）。CLI：foxos env pull IMAGE [--sha256 SHA256]。示例：foxos env pull alpine-3.20

只读：否 · 破坏性：否 · CLI：`foxos env pull`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `image` | string | 是 | 镜像 |
| `sha256` | string |  | 期望的 sha256（自定义地址时建议提供） |

调用示例：

```json
{"name": "env_pull", "arguments": {"image": "…"}}
```

### `env_run`

没有镜像就拉取，然后创建并启动（用法靠近 docker run）；可附上来宾桌面。CLI：foxos env run NAME [--image IMAGE] [--iso ISO] [--provider PROVIDER] [--network {user,host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--desktop-attach] [--no-start]。示例：foxos env run dev --image alpine-3.20

只读：否 · 破坏性：否 · CLI：`foxos env run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `image` | string |  | 镜像 ID |
| `iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `provider` | string |  | 指定提供者 |
| `network` | string |  | 网络：user 为用户态转发（来宾 5900 映射到宿主），none 断开，host 仅用于命名空间环境 可选：user / host / none |
| `workspace_mode` | string |  | 工作空间挂载方式 可选：rw / ro / none |
| `memory_mb` | integer |  | 内存上限（MB） |
| `cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | integer |  | 进程数上限 |
| `desktop_attach` | boolean |  | 启动后附上来宾桌面 |
| `no_start` | boolean |  | 只创建，不启动 |

调用示例：

```json
{"name": "env_run", "arguments": {"name": "…"}}
```

### `env_desktop-attach`

把完整虚拟机的来宾桌面作为显示通道打开（wayvnc）。CLI：foxos env desktop-attach NAME。示例：foxos env desktop-attach live --json

只读：否 · 破坏性：否 · CLI：`foxos env desktop-attach`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_desktop-attach", "arguments": {"name": "…"}}
```

### `env_create`

创建环境。CLI：foxos env create NAME [--image IMAGE] [--network {host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS]。示例：foxos env create dev

只读：否 · 破坏性：否 · CLI：`foxos env create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `image` | string |  | 镜像 ID |
| `network` | string |  | 网络：host（共享宿主网络）或 none（只有回环） 可选：host / none |
| `workspace_mode` | string |  | 工作空间挂载方式 可选：rw / ro / none |
| `memory_mb` | integer |  | 内存上限（MB） |
| `cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | integer |  | 进程数上限 |

调用示例：

```json
{"name": "env_create", "arguments": {"name": "…"}}
```

### `env_list`

列出环境及状态。CLI：foxos env list。示例：foxos env list --json

只读：是 · 破坏性：否 · CLI：`foxos env list`

调用示例：

```json
{"name": "env_list", "arguments": {}}
```

### `env_info`

环境详情（配置、快照、资源使用）。CLI：foxos env info NAME。示例：foxos env info dev --json

只读：是 · 破坏性：否 · CLI：`foxos env info`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_info", "arguments": {"name": "…"}}
```

### `env_start`

启动环境。CLI：foxos env start NAME。示例：foxos env start dev

只读：否 · 破坏性：否 · CLI：`foxos env start`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_start", "arguments": {"name": "…"}}
```

### `env_stop`

停止环境。CLI：foxos env stop NAME [--timeout TIMEOUT]。示例：foxos env stop dev

只读：否 · 破坏性：否 · CLI：`foxos env stop`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `timeout` | number |  | 等待秒数，超时强制结束 |

调用示例：

```json
{"name": "env_stop", "arguments": {"name": "…"}}
```

### `env_restart`

重启环境。CLI：foxos env restart NAME。示例：foxos env restart dev

只读：否 · 破坏性：否 · CLI：`foxos env restart`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_restart", "arguments": {"name": "…"}}
```

### `env_exec`

在环境中执行命令（默认工作目录 /workspace）。CLI：foxos env exec NAME [CMD...] [--cwd CWD] [--timeout TIMEOUT]。示例：foxos env exec dev -- uname -a

只读：否 · 破坏性：否 · CLI：`foxos env exec`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `cwd` | string |  | 环境内工作目录 |
| `timeout` | number |  | 超时秒数 |

调用示例：

```json
{"name": "env_exec", "arguments": {"name": "…"}}
```

### `env_shell`

进入环境的交互式 shell。CLI：foxos env shell NAME。示例：foxos env shell dev

只读：否 · 破坏性：否 · CLI：`foxos env shell`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_shell", "arguments": {"name": "…"}}
```

### `env_clone`

克隆环境（复制可写层与设置）。CLI：foxos env clone NAME NEW_NAME。示例：foxos env clone dev dev-copy

只读：否 · 破坏性：否 · CLI：`foxos env clone`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `new_name` | string | 是 | 新环境名 |

调用示例：

```json
{"name": "env_clone", "arguments": {"name": "…", "new_name": "…"}}
```

### `env_snapshot`

为停止的环境创建快照。CLI：foxos env snapshot NAME [--label LABEL]。示例：foxos env snapshot dev --label 装好依赖

只读：否 · 破坏性：否 · CLI：`foxos env snapshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `label` | string |  | 说明 |

调用示例：

```json
{"name": "env_snapshot", "arguments": {"name": "…"}}
```

### `env_restore`

恢复到快照。CLI：foxos env restore NAME SNAPSHOT。示例：foxos env restore dev 20261110T213000

只读：否 · 破坏性：否 · CLI：`foxos env restore`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `snapshot` | string | 是 | 快照 ID |

调用示例：

```json
{"name": "env_restore", "arguments": {"name": "…", "snapshot": "…"}}
```

### `env_export`

导出为 .foxenv 镜像（tar + zstd + manifest + sha256）。CLI：foxos env export NAME --out OUT。示例：foxos env export dev --out backups/dev.foxenv

只读：否 · 破坏性：否 · CLI：`foxos env export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `out` | string | 是 | 输出文件（工作空间内） |

调用示例：

```json
{"name": "env_export", "arguments": {"name": "…", "out": "…"}}
```

### `env_import`

从 .foxenv 镜像导入为新环境。CLI：foxos env import FILE --name NAME。示例：foxos env import backups/dev.foxenv --name dev2

只读：否 · 破坏性：否 · CLI：`foxos env import`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | .foxenv 文件（工作空间内） |
| `name` | string | 是 | 新环境名 |

调用示例：

```json
{"name": "env_import", "arguments": {"file": "…", "name": "…"}}
```

### `env_delete`

删除环境（不删除镜像与工作空间）。CLI：foxos env delete NAME。示例：foxos env delete dev-copy

只读：否 · 破坏性：是 · CLI：`foxos env delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_delete", "arguments": {"name": "…"}}
```

### `env_mount`

添加 / 移除宿主目录挂载。CLI：foxos env mount NAME --source SOURCE --target TARGET [--readonly] [--remove]。示例：foxos env mount dev --source ~/datasets --target /data --readonly

只读：否 · 破坏性：否 · CLI：`foxos env mount`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `source` | string | 是 | 宿主路径 |
| `target` | string | 是 | 环境内路径 |
| `readonly` | boolean |  | 只读 |
| `remove` | boolean |  | 移除该挂载 |

调用示例：

```json
{"name": "env_mount", "arguments": {"name": "…", "source": "…", "target": "…"}}
```

### `env_limits`

设置资源限制、网络与工作空间权限。CLI：foxos env limits NAME [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--network {host,none}] [--workspace-mode {rw,ro,none}]。示例：foxos env limits dev --memory-mb 2048 --pids 512

只读：否 · 破坏性：否 · CLI：`foxos env limits`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `memory_mb` | integer |  | 内存上限 MB（0 取消） |
| `cpus` | number |  | CPU 上限（0 取消） |
| `pids` | integer |  | 进程数上限（0 取消） |
| `network` | string |  | 网络 可选：host / none |
| `workspace_mode` | string |  | 工作空间挂载 可选：rw / ro / none |

调用示例：

```json
{"name": "env_limits", "arguments": {"name": "…"}}
```

### `env_stats`

资源使用（进程数、CPU 时间、内存、磁盘）。CLI：foxos env stats [NAME]。示例：foxos env stats --json

只读：是 · 破坏性：否 · CLI：`foxos env stats`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string |  | 环境名（缺省为全部） |

调用示例：

```json
{"name": "env_stats", "arguments": {}}
```

### `env_logs`

环境日志。CLI：foxos env logs NAME [--lines LINES]。示例：foxos env logs dev -n 50

只读：是 · 破坏性：否 · CLI：`foxos env logs`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `lines` | integer |  | 行数 |

调用示例：

```json
{"name": "env_logs", "arguments": {"name": "…"}}
```

### `env_action_add`

添加自定义操作（支持 ${env} ${image} ${workspace} ${host_workspace} ${hostname} 变量）。CLI：foxos env action add NAME ACTION --command COMMAND。示例：foxos env action add dev test --command 'cd ${workspace} && make test'

只读：否 · 破坏性：否 · CLI：`foxos env action add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `action` | string | 是 | 操作名 |
| `command` | string | 是 | 环境内执行的 shell 命令 |

调用示例：

```json
{"name": "env_action_add", "arguments": {"name": "…", "action": "…", "command": "…"}}
```

### `env_action_run`

运行自定义操作。CLI：foxos env action run NAME ACTION。示例：foxos env action run dev test --json

只读：否 · 破坏性：否 · CLI：`foxos env action run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |
| `action` | string | 是 | 操作名 |

调用示例：

```json
{"name": "env_action_run", "arguments": {"name": "…", "action": "…"}}
```

### `env_providers`

列出环境提供者（内置与第三方）及其能力、可用性。CLI：foxos env providers。示例：foxos env providers --json

只读：是 · 破坏性：否 · CLI：`foxos env providers`

调用示例：

```json
{"name": "env_providers", "arguments": {}}
```

### `env_doctor`

检查本机虚拟化能力（WSL、Windows Sandbox、Hyper-V、用户命名空间…）并给出修复操作。CLI：foxos env doctor [--provider PROVIDER]。示例：foxos env doctor --json

只读：是 · 破坏性：否 · CLI：`foxos env doctor`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `provider` | string |  | 只检查某个提供者 |

调用示例：

```json
{"name": "env_doctor", "arguments": {}}
```

### `env_fix`

执行 doctor 给出的修复操作（启用 WSL 等，需要管理员确认，可能需要重启）。CLI：foxos env fix --provider PROVIDER --action ACTION。示例：foxos env fix --provider wsl2 --action enable-wsl

只读：否 · 破坏性：否 · CLI：`foxos env fix`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `provider` | string | 是 | 提供者 |
| `action` | string | 是 | 修复操作 ID（见 doctor 输出） |

调用示例：

```json
{"name": "env_fix", "arguments": {"provider": "…", "action": "…"}}
```

### `env_catalog`

可一键安装的系统目录（WSL 发行版、LXC/官方根文件系统、Windows Sandbox、Hyper-V、macOS）。CLI：foxos env catalog [--guest {linux,windows,macos,any}] [--provider PROVIDER] [--available]。示例：foxos env catalog --json

只读：是 · 破坏性：否 · CLI：`foxos env catalog`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `guest` | string |  | 来宾系统 可选：linux / windows / macos / any |
| `provider` | string |  | 只看某个提供者 |
| `available` | boolean |  | 只显示本机可安装的 |

调用示例：

```json
{"name": "env_catalog", "arguments": {}}
```

### `env_install`

从目录一键安装一个系统为新环境（下载、校验 sha256、导入）。CLI：foxos env install ENTRY NAME [--provider PROVIDER] [--url URL] [--sha256 SHA256] [--iso ISO] [--location LOCATION] [--memory-mb MEMORY_MB] [--cpus CPUS] [--disk-gb DISK_GB] [--dry-run]。示例：foxos env install wsl-ubuntu-24.04 ubuntu

只读：否 · 破坏性：否 · CLI：`foxos env install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `entry` | string | 是 | 目录条目 ID（foxos env catalog） |
| `name` | string | 是 | 环境名 |
| `provider` | string |  | 指定提供者 |
| `url` | string |  | 自定义根文件系统地址（custom-rootfs） |
| `sha256` | string |  | 自定义来源的 sha256 |
| `iso` | string |  | 安装介质 ISO 路径（Hyper-V） |
| `location` | string |  | 安装位置（Windows 目录） |
| `memory_mb` | integer |  | 内存 MB（Hyper-V / Sandbox） |
| `cpus` | integer |  | CPU 数（Hyper-V） |
| `disk_gb` | integer |  | 磁盘 GB（Hyper-V） |
| `dry_run` | boolean |  | 只输出安装计划，不执行 |

调用示例：

```json
{"name": "env_install", "arguments": {"entry": "…", "name": "…"}}
```

### `env_progress`

查看安装进度。CLI：foxos env progress NAME。示例：foxos env progress ubuntu --json

只读：是 · 破坏性：否 · CLI：`foxos env progress`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 环境名 |

调用示例：

```json
{"name": "env_progress", "arguments": {"name": "…"}}
```

## everything（7 个工具）

### `everything_list`

列出 51 个 Everything 应用（分组、许可证、安装状态、操作数）。CLI：foxos everything list [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--installed]。示例：foxos everything list

只读：是 · 破坏性：否 · CLI：`foxos everything list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `group` | string |  | 只看某个分组 可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `installed_only` | boolean |  | 只列出已安装的 |

调用示例：

```json
{"name": "everything_list", "arguments": {}}
```

### `everything_info`

查看一个应用的详情、许可证与可用命令。CLI：foxos everything info APP。示例：foxos everything info tasks --json

只读：是 · 破坏性：否 · CLI：`foxos everything info`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |

调用示例：

```json
{"name": "everything_info", "arguments": {"app": "…"}}
```

### `everything_install`

从上游源码在本机构建并安装应用（固定提交，含许可证声明）。CLI：foxos everything install [APP...] [--all] [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--source SOURCE] [--force]。限制：需要 git、Node.js 22.12+ 与 npm；每个应用构建约 2–20 秒（不含下载）。示例：foxos everything install tasks chess

只读：否 · 破坏性：否 · CLI：`foxos everything install`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `apps` | array |  | 应用 ID |
| `all` | boolean |  | 安装全部 51 个 |
| `group` | string |  | 安装整个分组 可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `source` | string |  | 使用本地上游仓库目录（离线 / 镜像），默认从 GitHub 获取 |
| `force` | boolean |  | 已安装也重新构建 |

调用示例：

```json
{"name": "everything_install", "arguments": {}}
```

### `everything_commands`

列出一个应用的全部命令（语义操作 + 通用界面命令）及参数 Schema。CLI：foxos everything commands APP。示例：foxos everything commands tasks --json

只读：是 · 破坏性：否 · CLI：`foxos everything commands`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |

调用示例：

```json
{"name": "everything_commands", "arguments": {"app": "…"}}
```

### `everything_run`

执行一个应用的任意命令（与 foxos <app> <资源> <动词> 相同；权限、审计、写锁按被执行的命令计）。CLI：foxos everything run APP COMMAND [--args ARGS]。示例：foxos everything run tasks "add-task set" --args '{"value": "买牛奶", "submit": true}' --json

只读：是 · 破坏性：否 · CLI：`foxos everything run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |
| `command` | string | 是 | 命令，如 "task create" 或 "ui snapshot" |
| `args` | object |  | 命令参数（JSON 对象） |

调用示例：

```json
{"name": "everything_run", "arguments": {"app": "…", "command": "…"}}
```

### `everything_icons`

给已安装的应用补上上游自带的程序图标（不重新构建）。CLI：foxos everything icons [--source SOURCE]。示例：foxos everything icons --json

只读：否 · 破坏性：否 · CLI：`foxos everything icons`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `source` | string |  | 本地上游仓库路径（缺省从 GitHub 获取固定提交） |

调用示例：

```json
{"name": "everything_icons", "arguments": {}}
```

### `everything_uninstall`

卸载应用（保留工作空间中的数据）。CLI：foxos everything uninstall APP。示例：foxos everything uninstall chess

只读：否 · 破坏性：是 · CLI：`foxos everything uninstall`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app` | string | 是 | 应用 ID（foxos everything list 查看） |

调用示例：

```json
{"name": "everything_uninstall", "arguments": {"app": "…"}}
```

## spreadsheet（386 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `spreadsheet_account-menu_select` | 是 | `target`*: string |
| `spreadsheet_font_select` | 是 | `target`*: string |
| `spreadsheet_font-size_select` | 是 | `target`*: string |
| `spreadsheet_font-size-2_select` | 是 | `target`*: string |
| `spreadsheet_indent_select` | 是 | `target`*: string |
| `spreadsheet_number-format_select` | 是 | `target`*: string |
| `spreadsheet_places_show` | 是 | `target`*: string |
| `spreadsheet_fewer-places_select` | 是 | `target`*: string |
| `spreadsheet_sheets_select` | 是 | `target`*: string |
| `spreadsheet_options_select` | 是 | `target`*: string |
| `spreadsheet_view_zoom-level` |  | `target`*: string |
| `spreadsheet_other-charts_select` | 是 | `target`*: string |
| `spreadsheet_pen_select` | 是 | `target`*: string |
| `spreadsheet_pencil_select` | 是 | `target`*: string |
| `spreadsheet_highlighter_select` | 是 | `target`*: string |
| `spreadsheet_item_select` | 是 | `target`*: string |
| `spreadsheet_spreadsheets_previous` | 是 | — |
| `spreadsheet_autosave_toggle` |  | — |
| `spreadsheet_save_save` |  | — |
| `spreadsheet_undo_undo` |  | — |
| `spreadsheet_history_undo` |  | — |
| `spreadsheet_redo_redo` |  | — |
| `spreadsheet_customize-quick-access-toolbar_activate` |  | — |
| `spreadsheet_edit_update` |  | — |
| `spreadsheet_view_show` | 是 | — |
| `spreadsheet_insert_create` |  | — |
| `spreadsheet_format_activate` |  | — |
| `spreadsheet_tools_activate` |  | — |
| `spreadsheet_help_show` | 是 | — |
| `spreadsheet_untitled-spreadsheet_rename` |  | — |
| `spreadsheet_saved_activate` |  | — |
| `spreadsheet_menus_search` | 是 | — |
| `spreadsheet_comments_activate` |  | — |
| `spreadsheet_home_show` | 是 | — |
| `spreadsheet_insert-2_create` |  | — |
| `spreadsheet_draw_draw` |  | — |
| `spreadsheet_page-layout_show` | 是 | — |
| `spreadsheet_formulas_show` | 是 | — |
| `spreadsheet_review_show` | 是 | — |
| `spreadsheet_view-2_show` | 是 | — |
| `spreadsheet_automate_show` | 是 | — |
| `spreadsheet_scroll-ribbon-left_activate` |  | — |
| `spreadsheet_scroll-ribbon-right_activate` |  | — |
| `spreadsheet_ribbon_collapse` | 是 | — |
| `spreadsheet_paste_paste` |  | — |
| `spreadsheet_options_paste` |  | — |
| `spreadsheet_cut_cut` |  | — |
| `spreadsheet_copy_copy` |  | — |
| `spreadsheet_format-painter_activate` |  | — |
| `spreadsheet_increase-font-size_activate` |  | — |
| `spreadsheet_bold_format` |  | — |
| `spreadsheet_italic_format` |  | — |
| `spreadsheet_underline_format` |  | — |
| `spreadsheet_borders_activate` |  | — |
| `spreadsheet_fill-color-yellow_confirm` |  | — |
| `spreadsheet_fill-color_activate` |  | — |
| `spreadsheet_font-color-red_confirm` |  | — |
| `spreadsheet_text-color_activate` |  | — |
| `spreadsheet_top-align_activate` |  | — |
| `spreadsheet_middle-align_activate` |  | — |
| `spreadsheet_bottom-align_activate` |  | — |
| `spreadsheet_orientation_activate` |  | — |
| `spreadsheet_left_align` |  | — |
| `spreadsheet_center_align` |  | — |
| `spreadsheet_right_align` |  | — |
| `spreadsheet_increase-indent_activate` |  | — |
| `spreadsheet_wrap-text_activate` |  | — |
| `spreadsheet_merge-center_activate` |  | — |
| `spreadsheet_merge-options_activate` |  | — |
| `spreadsheet_accounting-number-format_activate` |  | — |
| `spreadsheet_accounting-number-format-options_activate` |  | — |
| `spreadsheet_format-as-percent_activate` |  | — |
| `spreadsheet_comma-style_activate` |  | — |
| `spreadsheet_conditional-formatting_activate` |  | — |
| `spreadsheet_format-as-table_activate` |  | — |
| `spreadsheet_cell-styles_activate` |  | — |
| `spreadsheet_insert-3_create` |  | — |
| `spreadsheet_delete_delete` |  | — |
| `spreadsheet_format-2_activate` |  | — |
| `spreadsheet_autosum_activate` |  | — |
| `spreadsheet_autosum-options_activate` |  | — |
| `spreadsheet_fill_activate` |  | — |
| `spreadsheet_clear_clear` |  | — |
| `spreadsheet_filter_sort` | 是 | — |
| `spreadsheet_select_search` | 是 | — |
| `spreadsheet_cell-reference_set` |  | `value`*: string, `submit`: boolean |
| `spreadsheet_named-ranges_activate` |  | — |
| `spreadsheet_edit_cancel` | 是 | — |
| `spreadsheet_edit_confirm` |  | — |
| `spreadsheet_function_create` |  | — |
| `spreadsheet_formula-or-value_set` |  | `value`*: string, `submit`: boolean |
| `spreadsheet_formula-bar_expand` | 是 | — |
| `spreadsheet_select_select` | 是 | — |
| `spreadsheet_spreadsheet-grid_activate` |  | — |
| `spreadsheet_scroll-sheets-left_activate` |  | — |
| `spreadsheet_scroll-sheets-right_activate` |  | — |
| `spreadsheet_sheets_activate` |  | — |
| `spreadsheet_sheet_create` |  | — |
| `spreadsheet_accessibility_run` |  | — |
| `spreadsheet_normal_activate` |  | — |
| `spreadsheet_page-layout_activate` |  | — |
| `spreadsheet_page-break-preview_activate` |  | — |
| `spreadsheet_view_zoom-out` |  | — |
| `spreadsheet_worksheet-zoom_set` |  | `value`*: string, `submit`: boolean |
| `spreadsheet_view_zoom-` |  | — |
| `spreadsheet_assistant_resize` |  | — |
| `spreadsheet_chat_create` |  | — |
| `spreadsheet_assistant-settings_activate` |  | — |
| `spreadsheet_assistant_collapse` | 是 | — |
| `spreadsheet_loan-calculator-payment-schedule_create` |  | — |
| `spreadsheet_message-assistant_set` |  | `value`*: string, `submit`: boolean |
| `spreadsheet_attach-files_activate` |  | — |
| `spreadsheet_send_send` |  | — |
| `spreadsheet_spreadsheet_create` |  | — |
| `spreadsheet_open_open` | 是 | — |
| `spreadsheet_customize-quick-access-toolbar-save_save` |  | — |
| `spreadsheet_print_print` | 是 | — |
| `spreadsheet_spelling_activate` |  | — |
| `spreadsheet_customize-quick-access-toolbar-undo_undo` |  | — |
| `spreadsheet_customize-quick-access-toolbar-redo_redo` |  | — |
| `spreadsheet_ascending_sort` | 是 | — |
| `spreadsheet_descending_sort` | 是 | — |
| `spreadsheet_find_search` | 是 | — |
| `spreadsheet_chart_create` |  | — |
| `spreadsheet_filter_filter` | 是 | — |
| `spreadsheet_commands_show` | 是 | — |
| `spreadsheet_below-ribbon_show` | 是 | — |
| `spreadsheet_command-labels_show` | 是 | — |
| `spreadsheet_close_close` | 是 | — |
| `spreadsheet_name_set` |  | `value`*: string, `submit`: boolean |
| `spreadsheet_cancel_cancel` | 是 | — |
| `spreadsheet_rename_rename` |  | — |
| `spreadsheet_system-theme_toggle` |  | — |
| `spreadsheet_light-theme_toggle` |  | — |
| `spreadsheet_dark-theme_toggle` |  | — |
| `spreadsheet_regional-format-english-united-states_activate` |  | — |
| `spreadsheet_options_activate` |  | — |
| `spreadsheet_keyboard-shortcuts_activate` |  | — |
| `spreadsheet_about_show` | 是 | — |
| `spreadsheet_pivottable_activate` |  | — |
| `spreadsheet_recommended-pivottables_activate` |  | — |
| `spreadsheet_table_activate` |  | — |
| `spreadsheet_pictures_activate` |  | — |
| `spreadsheet_shapes_activate` |  | — |
| `spreadsheet_icons_activate` |  | — |
| `spreadsheet_smartart-graphic_create` |  | — |
| `spreadsheet_recommended-charts_activate` |  | — |
| `spreadsheet_column-chart_create` |  | — |
| `spreadsheet_line-chart_create` |  | — |
| `spreadsheet_pie-chart_create` |  | — |
| `spreadsheet_bar-chart_create` |  | — |
| `spreadsheet_area-chart_create` |  | — |
| `spreadsheet_scatter-chart_create` |  | — |
| `spreadsheet_hierarchy-chart_create` |  | — |
| `spreadsheet_statistic-chart_create` |  | — |
| `spreadsheet_combo-chart_create` |  | — |
| `spreadsheet_line-sparklines_create` |  | — |
| `spreadsheet_column-sparklines_create` |  | — |
| `spreadsheet_win-loss-sparklines_create` |  | — |
| `spreadsheet_slicer_activate` |  | — |
| `spreadsheet_timeline_activate` |  | — |
| `spreadsheet_link_create` |  | — |
| `spreadsheet_note_activate` |  | — |
| `spreadsheet_comment_activate` |  | — |
| `spreadsheet_text-box_activate` |  | — |
| `spreadsheet_header-footer_activate` |  | — |
| `spreadsheet_wordart_activate` |  | — |
| `spreadsheet_checkbox_activate` |  | — |
| `spreadsheet_dropdown_activate` |  | — |
| `spreadsheet_date-picker_activate` |  | — |
| `spreadsheet_equation_activate` |  | — |
| `spreadsheet_equation-options_activate` |  | — |
| `spreadsheet_symbol_activate` |  | — |
| `spreadsheet_insert-sheet_create` |  | — |
| `spreadsheet_draw-select_select` | 是 | — |
| `spreadsheet_lasso-select_activate` |  | — |
| `spreadsheet_eraser_activate` |  | — |
| `spreadsheet_pen_create` |  | — |
| `spreadsheet_touch_draw` |  | — |
| `spreadsheet_ink-shape_activate` |  | — |
| `spreadsheet_themes_activate` |  | — |
| `spreadsheet_theme-colors_activate` |  | — |
| `spreadsheet_theme-fonts_activate` |  | — |
| `spreadsheet_effects_activate` |  | — |
| `spreadsheet_margins_activate` |  | — |
| `spreadsheet_size_activate` |  | — |
| `spreadsheet_area_print` | 是 | — |
| `spreadsheet_breaks_activate` |  | — |
| `spreadsheet_sheet-background_activate` |  | — |
| `spreadsheet_titles_print` | 是 | — |
| `spreadsheet_page-setup_activate` |  | — |
| `spreadsheet_pdf_export` |  | — |
| `spreadsheet_width_activate` |  | — |
| `spreadsheet_height_activate` |  | — |
| `spreadsheet_scale_activate` |  | — |
| `spreadsheet_gridlines_activate` |  | — |
| `spreadsheet_gridlines_print` | 是 | — |
| `spreadsheet_headings_activate` |  | — |
| `spreadsheet_headings_print` | 是 | — |
| `spreadsheet_bring-forward_activate` |  | — |
| `spreadsheet_bring-forward-options_activate` |  | — |
| `spreadsheet_backward_send` |  | — |
| `spreadsheet_backward-options_send` |  | — |
| `spreadsheet_selection-pane_activate` |  | — |
| `spreadsheet_align_align` |  | — |
| `spreadsheet_group_group` |  | — |
| `spreadsheet_rotate_rotate` |  | — |
| `spreadsheet_recently-used_activate` |  | — |
| `spreadsheet_financial-functions_activate` |  | — |
| `spreadsheet_logical-functions_activate` |  | — |
| `spreadsheet_text-functions_activate` |  | — |
| `spreadsheet_date-time-functions_activate` |  | — |
| `spreadsheet_lookup-reference-functions_activate` |  | — |
| `spreadsheet_math-trig-functions_activate` |  | — |
| `spreadsheet_functions_show` | 是 | — |
| `spreadsheet_name-manager_activate` |  | — |
| `spreadsheet_define-name_activate` |  | — |
| `spreadsheet_use-formula_activate` |  | — |
| `spreadsheet_from-selection_create` |  | — |
| `spreadsheet_trace-precedents_activate` |  | — |
| `spreadsheet_trace-dependents_activate` |  | — |
| `spreadsheet_arrows_delete` |  | — |
| `spreadsheet_formulas-2_show` | 是 | — |
| `spreadsheet_error-checking_activate` |  | — |
| `spreadsheet_error-checking-options_activate` |  | — |
| `spreadsheet_evaluate-formula_activate` |  | — |
| `spreadsheet_watch-window_activate` |  | — |
| `spreadsheet_calculation-options_activate` |  | — |
| `spreadsheet_now_run` |  | — |
| `spreadsheet_sheet_run` |  | — |
| `spreadsheet_formulas-values_activate` |  | — |
| `spreadsheet_get-data_activate` |  | — |
| `spreadsheet_from-text-csv_activate` |  | — |
| `spreadsheet_from-web_activate` |  | — |
| `spreadsheet_from-table-range_activate` |  | — |
| `spreadsheet_refresh_activate` |  | — |
| `spreadsheet_refresh-options_activate` |  | — |
| `spreadsheet_queries-connections_activate` |  | — |
| `spreadsheet_links_update` |  | — |
| `spreadsheet_z_sort` | 是 | — |
| `spreadsheet_data-z_sort` | 是 | — |
| `spreadsheet_sort_sort` | 是 | — |
| `spreadsheet_data-filter_filter` | 是 | — |
| `spreadsheet_filter_clear` |  | — |
| `spreadsheet_reapply_activate` |  | — |
| `spreadsheet_advanced-filter_activate` |  | — |
| `spreadsheet_text-columns_activate` |  | — |
| `spreadsheet_flash-fill_activate` |  | — |
| `spreadsheet_duplicates_delete` |  | — |
| `spreadsheet_data-validation_activate` |  | — |
| `spreadsheet_data-validation-options_activate` |  | — |
| `spreadsheet_consolidate_activate` |  | — |
| `spreadsheet_form_activate` |  | — |
| `spreadsheet_data-cleanup_activate` |  | — |
| `spreadsheet_what-if-analysis_activate` |  | — |
| `spreadsheet_goal-seek_activate` |  | — |
| `spreadsheet_forecast-sheet_activate` |  | — |
| `spreadsheet_column-stats_activate` |  | — |
| `spreadsheet_data-analysis_activate` |  | — |
| `spreadsheet_solver_activate` |  | — |
| `spreadsheet_rows_ungroup` |  | — |
| `spreadsheet_subtotal_activate` |  | — |
| `spreadsheet_detail_show` | 是 | — |
| `spreadsheet_detail_hide` | 是 | — |
| `spreadsheet_auto-outline_activate` |  | — |
| `spreadsheet_outline_clear` |  | — |
| `spreadsheet_outline-settings_activate` |  | — |
| `spreadsheet_review-spelling_activate` |  | — |
| `spreadsheet_thesaurus_activate` |  | — |
| `spreadsheet_spelling-as-you-type_activate` |  | — |
| `spreadsheet_autocorrect-options_activate` |  | — |
| `spreadsheet_workbook-statistics_activate` |  | — |
| `spreadsheet_translate_activate` |  | — |
| `spreadsheet_comment_create` |  | — |
| `spreadsheet_comment_delete` |  | — |
| `spreadsheet_comment_previous` | 是 | — |
| `spreadsheet_comment_next` | 是 | — |
| `spreadsheet_comments_show` | 是 | — |
| `spreadsheet_note_delete` |  | — |
| `spreadsheet_notes-sheet_select` | 是 | — |
| `spreadsheet_changes_show` | 是 | — |
| `spreadsheet_protect-sheet_activate` |  | — |
| `spreadsheet_protect-workbook_activate` |  | — |
| `spreadsheet_protected-ranges_activate` |  | — |
| `spreadsheet_share_share` |  | — |
| `spreadsheet_copy_send` |  | — |
| `spreadsheet_version-history_activate` |  | — |
| `spreadsheet_normal-view_activate` |  | — |
| `spreadsheet_page-layout-view_activate` |  | — |
| `spreadsheet_custom-views_activate` |  | — |
| `spreadsheet_sheet-view_activate` |  | — |
| `spreadsheet_sheet-view_create` |  | — |
| `spreadsheet_keep-sheet-view_activate` |  | — |
| `spreadsheet_exit-sheet-view_activate` |  | — |
| `spreadsheet_options-sheet-view_activate` |  | — |
| `spreadsheet_formula-bar_activate` |  | — |
| `spreadsheet_zeros_show` | 是 | — |
| `spreadsheet_page-breaks_activate` |  | — |
| `spreadsheet_zoom_zoom` | 是 | — |
| `spreadsheet_view-2_zoom-` |  | — |
| `spreadsheet_freeze-panes_activate` |  | — |
| `spreadsheet_split_activate` |  | — |
| `spreadsheet_unhide_hide` | 是 | — |
| `spreadsheet_focus-mode_activate` |  | — |
| `spreadsheet_full-screen_activate` |  | — |
| `spreadsheet_ai-assistant_activate` |  | — |
| `spreadsheet_actions_record` |  | — |
| `spreadsheet_script_create` |  | — |
| `spreadsheet_scripts_activate` |  | — |
| `spreadsheet_code-editor_activate` |  | — |
| `spreadsheet_script_run` |  | — |
| `spreadsheet_button-that-runs-script_create` |  | — |
| `spreadsheet_highlight-duplicates-sample-script_run` |  | — |
| `spreadsheet_unhide-everything-sample-script_run` |  | — |
| `spreadsheet_sum-each-column-sample-script_run` |  | — |
| `spreadsheet_table-contents-sample-script_run` |  | — |
| `spreadsheet_style-header-row-sample-script_run` |  | — |
| `spreadsheet_remove-blank-rows-sample-script_run` |  | — |
| `spreadsheet_script-reference_activate` |  | — |
| `spreadsheet_paste-options-paste_paste` |  | — |
| `spreadsheet_formulas_activate` |  | — |
| `spreadsheet_formulas-number-formatting_activate` |  | — |
| `spreadsheet_keep-source-formatting_activate` |  | — |
| `spreadsheet_no-borders_activate` |  | — |
| `spreadsheet_keep-source-column-widths_activate` |  | — |
| `spreadsheet_transpose_activate` |  | — |
| `spreadsheet_values_activate` |  | — |
| `spreadsheet_values-number-formatting_activate` |  | — |
| `spreadsheet_values-source-formatting_activate` |  | — |
| `spreadsheet_formatting_activate` |  | — |
| `spreadsheet_link_paste` |  | — |
| `spreadsheet_picture_activate` |  | — |
| `spreadsheet_linked-picture_activate` |  | — |
| `spreadsheet_special_paste` |  | — |
| `spreadsheet_default_activate` |  | — |
| `spreadsheet_arial_activate` |  | — |
| `spreadsheet_arial-black_activate` |  | — |
| `spreadsheet_calibri_activate` |  | — |
| `spreadsheet_cambria_activate` |  | — |
| `spreadsheet_aharoni_activate` |  | — |
| `spreadsheet_avenir-next-lt-pro_activate` |  | — |
| `spreadsheet_century-gothic_activate` |  | — |
| `spreadsheet_constantia_activate` |  | — |
| `spreadsheet_corbel_activate` |  | — |
| `spreadsheet_helvetica_activate` |  | — |
| `spreadsheet_impact_activate` |  | — |
| `spreadsheet_lato_activate` |  | — |
| `spreadsheet_lato-light_activate` |  | — |
| `spreadsheet_lucida-sans_activate` |  | — |
| `spreadsheet_nyala_activate` |  | — |
| `spreadsheet_sans-semibold_open` | 是 | — |
| `spreadsheet_segoe-ui_activate` |  | — |
| `spreadsheet_source-sans-pro_activate` |  | — |
| `spreadsheet_tahoma_activate` |  | — |
| `spreadsheet_verdana_activate` |  | — |
| `spreadsheet_trebuchet-ms_activate` |  | — |
| `spreadsheet_georgia_activate` |  | — |
| `spreadsheet_rockwell_activate` |  | — |
| `spreadsheet_times-roman_activate` |  | — |
| `spreadsheet_garamond_activate` |  | — |
| `spreadsheet_courier_activate` |  | — |
| `spreadsheet_monospace_activate` |  | — |
| `spreadsheet_comic-sans-ms_activate` |  | — |
| `spreadsheet_document_search` | 是 | — |
| `spreadsheet_selection_group` |  | — |
| `spreadsheet_view_toggle-help` |  | — |
| `spreadsheet_shortcut_key-q` |  | — |
| `spreadsheet_document_save` |  | — |

## documents（328 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `documents_search_search` | 是 | `target`*: string |
| `documents_editing-mode_select` | 是 | `target`*: string |
| `documents_account-menu_select` | 是 | `target`*: string |
| `documents_font-size_select` | 是 | `target`*: string |
| `documents_indent_select` | 是 | `target`*: string |
| `documents_formatting_show` | 是 | `target`*: string |
| `documents_heading_select` | 是 | `target`*: string |
| `documents_left_select` | 是 | `target`*: string |
| `documents_right_select` | 是 | `target`*: string |
| `documents_top_select` | 是 | `target`*: string |
| `documents_bottom_select` | 是 | `target`*: string |
| `documents_spelling_select` | 是 | `target`*: string |
| `documents_accessibility_select` | 是 | `target`*: string |
| `documents_customize-quick-access-toolbar-formatting_show` | 是 | `target`*: string |
| `documents_pen_select` | 是 | `target`*: string |
| `documents_pencil_select` | 是 | `target`*: string |
| `documents_highlighter_select` | 是 | `target`*: string |
| `documents_check_run` |  | `target`*: string |
| `documents_autosave_toggle` |  | — |
| `documents_documents_activate` |  | — |
| `documents_save_save` |  | — |
| `documents_undo_undo` |  | — |
| `documents_history_undo` |  | — |
| `documents_redo_redo` |  | — |
| `documents_print_print` | 是 | — |
| `documents_customize-quick-access-toolbar_activate` |  | — |
| `documents_edit_update` |  | — |
| `documents_view_show` | 是 | — |
| `documents_insert_create` |  | — |
| `documents_format_activate` |  | — |
| `documents_tools_activate` |  | — |
| `documents_table_activate` |  | — |
| `documents_window_activate` |  | — |
| `documents_help_show` | 是 | — |
| `documents_document-name_set` |  | `value`*: string, `submit`: boolean |
| `documents_document-details_activate` |  | — |
| `documents_not-saved-yet_activate` |  | — |
| `documents_assistant_activate` |  | — |
| `documents_comments_activate` |  | — |
| `documents_share_share` |  | — |
| `documents_file-2_activate` |  | — |
| `documents_home_show` | 是 | — |
| `documents_insert-2_create` |  | — |
| `documents_draw_draw` |  | — |
| `documents_design_show` | 是 | — |
| `documents_layout_show` | 是 | — |
| `documents_references_show` | 是 | — |
| `documents_mailings_show` | 是 | — |
| `documents_review_show` | 是 | — |
| `documents_view-2_show` | 是 | — |
| `documents_ribbon-display-options_activate` |  | — |
| `documents_ribbon_collapse` | 是 | — |
| `documents_paste_paste` |  | — |
| `documents_options_paste` |  | — |
| `documents_cut_cut` |  | — |
| `documents_copy_copy` |  | — |
| `documents_format-painter_activate` |  | — |
| `documents_latin-font-family_activate` |  | — |
| `documents_font-size-pt_set` |  | `value`*: string, `submit`: boolean |
| `documents_font-sizes_activate` |  | — |
| `documents_increase-font-size_activate` |  | — |
| `documents_case_update` |  | — |
| `documents_formatting_clear` |  | — |
| `documents_bold_format` |  | — |
| `documents_italic_format` |  | — |
| `documents_underline_format` |  | — |
| `documents_options_format` |  | — |
| `documents_strikethrough_format` |  | — |
| `documents_subscript_activate` |  | — |
| `documents_superscript_activate` |  | — |
| `documents_text-effects_activate` |  | — |
| `documents_text-highlight_activate` |  | — |
| `documents_text-color_activate` |  | — |
| `documents_font-settings_activate` |  | — |
| `documents_bulleted-list_activate` |  | — |
| `documents_bullet-library_activate` |  | — |
| `documents_numbered-list_activate` |  | — |
| `documents_numbering-library_activate` |  | — |
| `documents_multilevel-list_activate` |  | — |
| `documents_increase-indent_activate` |  | — |
| `documents_sort_sort` | 是 | — |
| `documents_left_align` |  | — |
| `documents_center_align` |  | — |
| `documents_right_align` |  | — |
| `documents_justify_activate` |  | — |
| `documents_line-paragraph-spacing_activate` |  | — |
| `documents_paragraph-shading_activate` |  | — |
| `documents_borders_activate` |  | — |
| `documents_border-options_activate` |  | — |
| `documents_paragraph-settings_activate` |  | — |
| `documents_normal_activate` |  | — |
| `documents_title_activate` |  | — |
| `documents_subtitle_activate` |  | — |
| `documents_styles_show` | 是 | — |
| `documents_styles-pane_activate` |  | — |
| `documents_formatting-pane_activate` |  | — |
| `documents_dictate_activate` |  | — |
| `documents_find_search` | 是 | — |
| `documents_options_search` | 是 | — |
| `documents_replace_activate` |  | — |
| `documents_select_select` | 是 | — |
| `documents_left-indent_set` |  | `value`*: string, `submit`: boolean |
| `documents_hanging-indent_set` |  | `value`*: string, `submit`: boolean |
| `documents_first-line-indent_set` |  | `value`*: string, `submit`: boolean |
| `documents_right-indent_set` |  | `value`*: string, `submit`: boolean |
| `documents_document-text_set` |  | `value`*: string, `submit`: boolean |
| `documents_go-ctrlg_activate` |  | — |
| `documents_word-count_activate` |  | — |
| `documents_language_activate` |  | — |
| `documents_text-mode_toggle` |  | — |
| `documents_focus_activate` |  | — |
| `documents_read-mode_activate` |  | — |
| `documents_layout_print` | 是 | — |
| `documents_web-layout_activate` |  | — |
| `documents_outline_activate` |  | — |
| `documents_draft_activate` |  | — |
| `documents_view_zoom-out` |  | — |
| `documents_zoom-slider_set` |  | `value`*: string, `submit`: boolean |
| `documents_view_zoom-` |  | — |
| `documents_zoom_set` |  | `value`*: string, `submit`: boolean |
| `documents_customize-quick-access-toolbar-documents_activate` |  | — |
| `documents_customize-quick-access-toolbar-save_save` |  | — |
| `documents_customize-quick-access-toolbar-undo_undo` |  | — |
| `documents_customize-quick-access-toolbar-redo_redo` |  | — |
| `documents_customize-quick-access-toolbar-print_print` | 是 | — |
| `documents_document_create` |  | — |
| `documents_open_open` | 是 | — |
| `documents_customize-quick-access-toolbar-find_search` | 是 | — |
| `documents_spelling_activate` |  | — |
| `documents_as-pdf_save` |  | — |
| `documents_comment_create` |  | — |
| `documents_track-changes_activate` |  | — |
| `documents_customize-quick-access-toolbar-word-count_activate` |  | — |
| `documents_read-aloud_activate` |  | — |
| `documents_repeat_activate` |  | — |
| `documents_defaults_reset` |  | — |
| `documents_document_close` | 是 | — |
| `documents_file-name_set` |  | `value`*: string, `submit`: boolean |
| `documents_version-history_activate` |  | — |
| `documents_properties_activate` |  | — |
| `documents_rename_rename` |  | — |
| `documents_editingedit-document-directly_activate` |  | — |
| `documents_reviewingedits-become-tracked-changes_activate` |  | — |
| `documents_people_invite` |  | — |
| `documents_link_copy` |  | — |
| `documents_publish-web_activate` |  | — |
| `documents_copy-docx_send` |  | — |
| `documents_as-pdf_send` |  | — |
| `documents_system_toggle` |  | — |
| `documents_light_toggle` |  | — |
| `documents_dark_toggle` |  | — |
| `documents_dark-pagedark-paper-dark-theme_activate` |  | — |
| `documents_measurement-unitsinches_activate` |  | — |
| `documents_capitalize-first-letter-sentences_activate` |  | — |
| `documents_keyboard-shortcuts_activate` |  | — |
| `documents_documents_show` | 是 | — |
| `documents_document_previous` | 是 | — |
| `documents_file-open_open` | 是 | — |
| `documents_info_show` | 是 | — |
| `documents_file-save_save` |  | — |
| `documents_file-print_print` | 是 | — |
| `documents_file-share_share` |  | — |
| `documents_export_export` |  | — |
| `documents_close_close` | 是 | — |
| `documents_preferences_activate` |  | — |
| `documents_title_set` |  | `value`*: string, `submit`: boolean |
| `documents_subject_set` |  | `value`*: string, `submit`: boolean |
| `documents_author_set` |  | `value`*: string, `submit`: boolean |
| `documents_keywords_set` |  | `value`*: string, `submit`: boolean |
| `documents_category_set` |  | `value`*: string, `submit`: boolean |
| `documents_status_set` |  | `value`*: string, `submit`: boolean |
| `documents_comments_set` |  | `value`*: string, `submit`: boolean |
| `documents_properties_save` |  | — |
| `documents_only_show` | 是 | — |
| `documents_cover-page_activate` |  | — |
| `documents_blank-page_activate` |  | — |
| `documents_page-break_activate` |  | — |
| `documents_table_create` |  | — |
| `documents_pictures_activate` |  | — |
| `documents_shapes_activate` |  | — |
| `documents_icons_activate` |  | — |
| `documents_diagram_activate` |  | — |
| `documents_chart_activate` |  | — |
| `documents_or-edit-link_create` |  | — |
| `documents_bookmarks_activate` |  | — |
| `documents_insert-comment_create` |  | — |
| `documents_header_activate` |  | — |
| `documents_footer_activate` |  | — |
| `documents_page-number_activate` |  | — |
| `documents_text-box_activate` |  | — |
| `documents_quick-parts_activate` |  | — |
| `documents_wordart_activate` |  | — |
| `documents_drop-cap_activate` |  | — |
| `documents_signature-line_activate` |  | — |
| `documents_date-time_activate` |  | — |
| `documents_object_activate` |  | — |
| `documents_symbols_activate` |  | — |
| `documents_lasso-select_activate` |  | — |
| `documents_eraser_activate` |  | — |
| `documents_eraser-options_activate` |  | — |
| `documents_pen_create` |  | — |
| `documents_touch_draw` |  | — |
| `documents_ruler_activate` |  | — |
| `documents_ink-shape_activate` |  | — |
| `documents_ink-math_activate` |  | — |
| `documents_drawing-canvas_activate` |  | — |
| `documents_ink-replay_activate` |  | — |
| `documents_ink_hide` | 是 | — |
| `documents_themes_activate` |  | — |
| `documents_default-style-set_activate` |  | — |
| `documents_crisp-style-set_activate` |  | — |
| `documents_classic-style-set_activate` |  | — |
| `documents_banner-style-set_activate` |  | — |
| `documents_minimal-style-set_activate` |  | — |
| `documents_accent-bar-style-set_activate` |  | — |
| `documents_centered-style-set_activate` |  | — |
| `documents_contrast-style-set_format` |  | — |
| `documents_style-sets_show` | 是 | — |
| `documents_theme-colors_activate` |  | — |
| `documents_theme-fonts_activate` |  | — |
| `documents_paragraph-spacing_activate` |  | — |
| `documents_theme-effects_activate` |  | — |
| `documents_set-as-default_activate` |  | — |
| `documents_watermark_activate` |  | — |
| `documents_page-color_activate` |  | — |
| `documents_page-borders_activate` |  | — |
| `documents_margins_activate` |  | — |
| `documents_orientation_activate` |  | — |
| `documents_size_activate` |  | — |
| `documents_columns_activate` |  | — |
| `documents_breaks_activate` |  | — |
| `documents_line-numbers_activate` |  | — |
| `documents_hyphenation_activate` |  | — |
| `documents_page-setup_activate` |  | — |
| `documents_indent-left_set` |  | `value`*: string, `submit`: boolean |
| `documents_indent-right_set` |  | `value`*: string, `submit`: boolean |
| `documents_space-before-paragraph-pt_set` |  | `value`*: string, `submit`: boolean |
| `documents_space-after-paragraph-pt_set` |  | `value`*: string, `submit`: boolean |
| `documents_position_activate` |  | — |
| `documents_wrap-text_activate` |  | — |
| `documents_bring-forward_activate` |  | — |
| `documents_bring-forward-options_activate` |  | — |
| `documents_backward_send` |  | — |
| `documents_backward-options_send` |  | — |
| `documents_selection-pane_activate` |  | — |
| `documents_align_align` |  | — |
| `documents_group_group` |  | — |
| `documents_rotate_rotate` |  | — |
| `documents_table-contents_activate` |  | — |
| `documents_text_create` |  | — |
| `documents_table_update` |  | — |
| `documents_fields_update` |  | — |
| `documents_footnote_create` |  | — |
| `documents_endnote_create` |  | — |
| `documents_footnote_next` | 是 | — |
| `documents_notes_show` | 是 | — |
| `documents_footnote-endnote-settings_activate` |  | — |
| `documents_smart-lookup_activate` |  | — |
| `documents_citation_create` |  | — |
| `documents_manage-sources_activate` |  | — |
| `documents_citation-style_set` |  | `value`*: string, `submit`: boolean |
| `documents_bibliography_activate` |  | — |
| `documents_caption_create` |  | — |
| `documents_table-figures_create` |  | — |
| `documents_table-figures_update` |  | — |
| `documents_cross-reference_activate` |  | — |
| `documents_index_activate` |  | — |
| `documents_table-authorities_activate` |  | — |
| `documents_create_create` |  | — |
| `documents_mail-merge_start` |  | — |
| `documents_recipients_select` | 是 | — |
| `documents_recipient-list_update` |  | — |
| `documents_highlight-merge-fields_activate` |  | — |
| `documents_address-block_activate` |  | — |
| `documents_greeting-line_activate` |  | — |
| `documents_merge-field_create` |  | — |
| `documents_rules_activate` |  | — |
| `documents_match-fields_activate` |  | — |
| `documents_labels_update` |  | — |
| `documents_preview-results_activate` |  | — |
| `documents_first-record_activate` |  | — |
| `documents_record_previous` | 是 | — |
| `documents_go-record_set` |  | `value`*: string, `submit`: boolean |
| `documents_record_next` | 是 | — |
| `documents_last-record_activate` |  | — |
| `documents_recipient_search` | 是 | — |
| `documents_finish-merge_activate` |  | — |
| `documents_editor_activate` |  | — |
| `documents_spelling-options_activate` |  | — |
| `documents_thesaurus_activate` |  | — |
| `documents_review-word-count_activate` |  | — |
| `documents_review-read-aloud_activate` |  | — |
| `documents_accessibility_run` |  | — |
| `documents_review-language_activate` |  | — |
| `documents_comment_delete` |  | — |
| `documents_options_delete` |  | — |
| `documents_comment_previous` | 是 | — |
| `documents_comment_next` | 是 | — |
| `documents_resolve-comment_activate` |  | — |
| `documents_comments_show` | 是 | — |
| `documents_comments-options_show` | 是 | — |
| `documents_tracking_activate` |  | — |
| `documents_accept_activate` |  | — |
| `documents_accept-options_activate` |  | — |
| `documents_reject_activate` |  | — |
| `documents_reject-options_activate` |  | — |
| `documents_change_previous` | 是 | — |
| `documents_change_next` | 是 | — |
| `documents_compare_activate` |  | — |
| `documents_restrict-editing_activate` |  | — |

## presentation（301 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `presentation_search_search` | 是 | `target`*: string |
| `presentation_local_select` | 是 | `target`*: string |
| `presentation_font-size_select` | 是 | `target`*: string |
| `presentation_list-level_select` | 是 | `target`*: string |
| `presentation_slide-1_select` | 是 | `target`*: string |
| `presentation_options_select` | 是 | `target`*: string |
| `presentation_centered-title-select-edit_select` | 是 | `target`*: string |
| `presentation_subtitle-select-edit_select` | 是 | `target`*: string |
| `presentation_draft-6-slide-pitch-deck_select` | 是 | `target`*: string |
| `presentation_outline-talk-topic-i-give-you_select` | 是 | `target`*: string |
| `presentation_accessibility_select` | 是 | `target`*: string |
| `presentation_pen_select` | 是 | `target`*: string |
| `presentation_pencil_select` | 是 | `target`*: string |
| `presentation_highlighter_select` | 是 | `target`*: string |
| `presentation_duration_select` | 是 | `target`*: string |
| `presentation_advance-after_select` | 是 | `target`*: string |
| `presentation_delay_select` | 是 | `target`*: string |
| `presentation_content_dismiss` | 是 | — |
| `presentation_presentations_previous` | 是 | — |
| `presentation_puter_save` |  | — |
| `presentation_undo_undo` |  | — |
| `presentation_redo_redo` |  | — |
| `presentation_edit_update` |  | — |
| `presentation_view_show` | 是 | — |
| `presentation_insert_create` |  | — |
| `presentation_format_activate` |  | — |
| `presentation_arrange_activate` |  | — |
| `presentation_slide_activate` |  | — |
| `presentation_tools_activate` |  | — |
| `presentation_slide-show_activate` |  | — |
| `presentation_help_show` | 是 | — |
| `presentation_untitled-presentation_rename` |  | — |
| `presentation_save_save` |  | — |
| `presentation_ask-ai_activate` |  | — |
| `presentation_present_activate` |  | — |
| `presentation_home_show` | 是 | — |
| `presentation_insert-2_create` |  | — |
| `presentation_draw_draw` |  | — |
| `presentation_design_show` | 是 | — |
| `presentation_transitions_show` | 是 | — |
| `presentation_animations_show` | 是 | — |
| `presentation_slide-show_show` | 是 | — |
| `presentation_record_record` |  | — |
| `presentation_review_show` | 是 | — |
| `presentation_view-2_show` | 是 | — |
| `presentation_ribbon_collapse` | 是 | — |
| `presentation_paste_paste` |  | — |
| `presentation_options_paste` |  | — |
| `presentation_cut_cut` |  | — |
| `presentation_copy_copy` |  | — |
| `presentation_format-painter_activate` |  | — |
| `presentation_slide_create` |  | — |
| `presentation_slide-layouts_create` |  | — |
| `presentation_layout_activate` |  | — |
| `presentation_reset_reset` |  | — |
| `presentation_section_activate` |  | — |
| `presentation_font_set` |  | `value`*: string, `submit`: boolean |
| `presentation_font-list_activate` |  | — |
| `presentation_font-size_set` |  | `value`*: string, `submit`: boolean |
| `presentation_font-size-list_activate` |  | — |
| `presentation_increase-font-size_activate` |  | — |
| `presentation_formatting_clear` |  | — |
| `presentation_font-settings_activate` |  | — |
| `presentation_bold_format` |  | — |
| `presentation_italic_format` |  | — |
| `presentation_underline_format` |  | — |
| `presentation_strikethrough_format` |  | — |
| `presentation_superscript_activate` |  | — |
| `presentation_subscript_activate` |  | — |
| `presentation_character-spacing_activate` |  | — |
| `presentation_case_update` |  | — |
| `presentation_text-highlight-color_activate` |  | — |
| `presentation_highlight-colors_activate` |  | — |
| `presentation_font-color_activate` |  | — |
| `presentation_font-colors_activate` |  | — |
| `presentation_bullets_activate` |  | — |
| `presentation_bullet-styles_activate` |  | — |
| `presentation_numbering_activate` |  | — |
| `presentation_numbering-styles_activate` |  | — |
| `presentation_increase-list-level_activate` |  | — |
| `presentation_line-spacing_activate` |  | — |
| `presentation_columns_activate` |  | — |
| `presentation_paragraph-settings_activate` |  | — |
| `presentation_left_align` |  | — |
| `presentation_center_activate` |  | — |
| `presentation_right_align` |  | — |
| `presentation_justify_activate` |  | — |
| `presentation_text-direction_activate` |  | — |
| `presentation_text_align` |  | — |
| `presentation_convert-smartart_activate` |  | — |
| `presentation_insert-3_create` |  | — |
| `presentation_drawing_activate` |  | — |
| `presentation_editing_activate` |  | — |
| `presentation_designer_activate` |  | — |
| `presentation_slide-thumbnails_resize` |  | — |
| `presentation_notes_resize` |  | — |
| `presentation_speaker-notes_set` |  | `value`*: string, `submit`: boolean |
| `presentation_assistant_resize` |  | — |
| `presentation_chat_create` |  | — |
| `presentation_assistant-settings_activate` |  | — |
| `presentation_assistant_close` | 是 | — |
| `presentation_turn-notes-into-slides_activate` |  | — |
| `presentation_message-assistant_set` |  | `value`*: string, `submit`: boolean |
| `presentation_send_send` |  | — |
| `presentation_english-united-states_activate` |  | — |
| `presentation_notes_activate` |  | — |
| `presentation_comments_activate` |  | — |
| `presentation_normal_activate` |  | — |
| `presentation_slide-sorter_activate` |  | — |
| `presentation_reading-view_activate` |  | — |
| `presentation_slide-show-2_activate` |  | — |
| `presentation_view_zoom-out` |  | — |
| `presentation_zoom_set` |  | `value`*: string, `submit`: boolean |
| `presentation_view_zoom-` |  | — |
| `presentation_view_zoom-level` |  | — |
| `presentation_fit-slide-current-window_activate` |  | — |
| `presentation_close_close` | 是 | — |
| `presentation_presentation-name_set` |  | `value`*: string, `submit`: boolean |
| `presentation_cancel_cancel` | 是 | — |
| `presentation_appearance_activate` |  | — |
| `presentation_keyboard-shortcuts_activate` |  | — |
| `presentation_table_activate` |  | — |
| `presentation_pictures_activate` |  | — |
| `presentation_picture-sources_activate` |  | — |
| `presentation_screenshot_activate` |  | — |
| `presentation_screenshot-options_activate` |  | — |
| `presentation_photo-album_activate` |  | — |
| `presentation_shapes_activate` |  | — |
| `presentation_icons_activate` |  | — |
| `presentation_smartart_activate` |  | — |
| `presentation_chart_activate` |  | — |
| `presentation_zoom_zoom` | 是 | — |
| `presentation_link_activate` |  | — |
| `presentation_action_activate` |  | — |
| `presentation_action-options_activate` |  | — |
| `presentation_comment_activate` |  | — |
| `presentation_text-box_activate` |  | — |
| `presentation_header-footer_activate` |  | — |
| `presentation_wordart_activate` |  | — |
| `presentation_date-time_activate` |  | — |
| `presentation_slide-number_activate` |  | — |
| `presentation_object_activate` |  | — |
| `presentation_symbols_activate` |  | — |
| `presentation_media_activate` |  | — |
| `presentation_select_select` | 是 | — |
| `presentation_eraser_activate` |  | — |
| `presentation_eraser-options_activate` |  | — |
| `presentation_lasso-select_activate` |  | — |
| `presentation_pen_create` |  | — |
| `presentation_ink-text_activate` |  | — |
| `presentation_ink-shape_activate` |  | — |
| `presentation_ink-shape-options_activate` |  | — |
| `presentation_ink-math_activate` |  | — |
| `presentation_ink-replay_activate` |  | — |
| `presentation_ruler_activate` |  | — |
| `presentation_touch_draw` |  | — |
| `presentation_default-theme_activate` |  | — |
| `presentation_paper_activate` |  | — |
| `presentation_studio_activate` |  | — |
| `presentation_cobalt_activate` |  | — |
| `presentation_row-themes_previous` | 是 | — |
| `presentation_row-themes_next` | 是 | — |
| `presentation_themes_show` | 是 | — |
| `presentation_default_activate` |  | — |
| `presentation_default-dark_activate` |  | — |
| `presentation_default-accents-turned_activate` |  | — |
| `presentation_default-accents-turned-twice_activate` |  | — |
| `presentation_row-variants_previous` | 是 | — |
| `presentation_row-variants_next` | 是 | — |
| `presentation_variants_show` | 是 | — |
| `presentation_colors_activate` |  | — |
| `presentation_fonts_activate` |  | — |
| `presentation_effects_activate` |  | — |
| `presentation_background-styles_activate` |  | — |
| `presentation_slide-size_activate` |  | — |
| `presentation_format-background_activate` |  | — |
| `presentation_hide-background-graphics_toggle` |  | — |
| `presentation_design-ideas_activate` |  | — |
| `presentation_preview_activate` |  | — |
| `presentation_none_activate` |  | — |
| `presentation_morph_activate` |  | — |
| `presentation_fade_activate` |  | — |
| `presentation_push_activate` |  | — |
| `presentation_wipe_activate` |  | — |
| `presentation_split_activate` |  | — |
| `presentation_reveal_activate` |  | — |
| `presentation_transitions-cut_cut` |  | — |
| `presentation_random-bars_activate` |  | — |
| `presentation_row-transitions_previous` | 是 | — |
| `presentation_row-transitions_next` | 是 | — |
| `presentation_transitions-2_show` | 是 | — |
| `presentation_effect-options_activate` |  | — |
| `presentation_sound_activate` |  | — |
| `presentation_duration_set` |  | `value`*: string, `submit`: boolean |
| `presentation_increase-duration_activate` |  | — |
| `presentation_apply_confirm` |  | — |
| `presentation_mouse-click_toggle` |  | — |
| `presentation_after_toggle` |  | — |
| `presentation_advance-after-seconds_set` |  | `value`*: string, `submit`: boolean |
| `presentation_increase-advance-after_activate` |  | — |
| `presentation_preview-options_activate` |  | — |
| `presentation_appear_activate` |  | — |
| `presentation_fly_activate` |  | — |
| `presentation_float_activate` |  | — |
| `presentation_shape_activate` |  | — |
| `presentation_row-animations_previous` | 是 | — |
| `presentation_row-animations_next` | 是 | — |
| `presentation_animations-2_show` | 是 | — |
| `presentation_animation_create` |  | — |
| `presentation_animation-pane_activate` |  | — |
| `presentation_trigger_activate` |  | — |
| `presentation_animation-painter_activate` |  | — |
| `presentation_start_set` |  | `value`*: string, `submit`: boolean |
| `presentation_list_start` |  | — |
| `presentation_delay_set` |  | `value`*: string, `submit`: boolean |
| `presentation_increase-delay_activate` |  | — |
| `presentation_earlier_move` |  | — |
| `presentation_later_move` |  | — |
| `presentation_from-start_play` |  | — |
| `presentation_from-current-slide_play` |  | — |
| `presentation_presenter-view_activate` |  | — |
| `presentation_custom-show_activate` |  | — |
| `presentation_set-up-slide-show_activate` |  | — |
| `presentation_slide_hide` | 是 | — |
| `presentation_rehearse-timings_activate` |  | — |
| `presentation_slide-show-record_record` |  | — |
| `presentation_options_record` |  | — |
| `presentation_play-narrations_toggle` |  | — |
| `presentation_use-timings_toggle` |  | — |
| `presentation_show-media-controls_toggle` |  | — |
| `presentation_always-use-subtitles_toggle` |  | — |
| `presentation_subtitle-settings_activate` |  | — |
| `presentation_live-camera_activate` |  | — |
| `presentation_from-beginning_activate` |  | — |
| `presentation_from-current-slide_activate` |  | — |
| `presentation_recording_clear` |  | — |
| `presentation_camera_reset` |  | — |
| `presentation_video_export` |  | — |
| `presentation_spelling_activate` |  | — |
| `presentation_thesaurus_activate` |  | — |
| `presentation_accessibility_run` |  | — |
| `presentation_accessibility-options_activate` |  | — |
| `presentation_alt-text_activate` |  | — |
| `presentation_translate_activate` |  | — |
| `presentation_language_activate` |  | — |
| `presentation_comment_create` |  | — |
| `presentation_delete_delete` |  | — |
| `presentation_previous_previous` | 是 | — |
| `presentation_next_next` | 是 | — |
| `presentation_comments_show` | 是 | — |
| `presentation_comments-options_show` | 是 | — |
| `presentation_compare_activate` |  | — |
| `presentation_always-open-read-only_activate` |  | — |
| `presentation_outline-view_activate` |  | — |
| `presentation_notes-page_activate` |  | — |
| `presentation_slide-master_activate` |  | — |
| `presentation_handout-master_activate` |  | — |
| `presentation_notes-master_activate` |  | — |
| `presentation_ruler_toggle` |  | — |
| `presentation_gridlines_toggle` |  | — |
| `presentation_guides_toggle` |  | — |
| `presentation_view-notes_activate` |  | — |
| `presentation_grid-settings_activate` |  | — |
| `presentation_fit-window_activate` |  | — |
| `presentation_color_activate` |  | — |
| `presentation_grayscale_activate` |  | — |
| `presentation_black-white_activate` |  | — |
| `presentation_slide-thumbnails_activate` |  | — |
| `presentation_format-pane_activate` |  | — |
| `presentation_ai-assistant_activate` |  | — |
| `presentation_pastectrlv_activate` |  | — |
| `presentation_as-text-only_paste` |  | — |
| `presentation_duplicatectrld_activate` |  | — |
| `presentation_special_paste` |  | — |
| `presentation_match-formatting_paste` |  | — |
| `presentation_selection_select-all` |  | — |
| `presentation_selection_duplicate` |  | — |
| `presentation_shortcut_key-j` |  | — |
| `presentation_command-palette_show` | 是 | — |
| `presentation_document_open` | 是 | — |
| `presentation_document_print` | 是 | — |
| `presentation_document_save` |  | — |
| `presentation_clipboard_paste` |  | — |

## whiteboard（44 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `whiteboard_board-library_select` | 是 | `target`*: string |
| `whiteboard_board-library-2_select` | 是 | `target`*: string |
| `whiteboard_main_select` | 是 | `target`*: string |
| `whiteboard_whiteboard-home_show` | 是 | — |
| `whiteboard_trash_delete` |  | — |
| `whiteboard_organization_join` |  | — |
| `whiteboard_set-up-organization_activate` |  | — |
| `whiteboard_feedback_send` |  | — |
| `whiteboard_language_set` |  | `value`*: string, `submit`: boolean |
| `whiteboard_appearance_set` |  | `value`*: string, `submit`: boolean |
| `whiteboard_powered-by-puter_show` | 是 | — |
| `whiteboard_command-palette-ctrl-cmd-k_activate` |  | — |
| `whiteboard_shared-board_join` |  | — |
| `whiteboard_training_show` | 是 | — |
| `whiteboard_keyboard-shortcuts_activate` |  | — |
| `whiteboard_account-menu-local_activate` |  | — |
| `whiteboard_browse-templates_activate` |  | — |
| `whiteboard_blank-boarda-fresh-start_activate` |  | — |
| `whiteboard_board_create` |  | — |
| `whiteboard_search-boards_set` |  | `value`*: string, `submit`: boolean |
| `whiteboard_sort-boards_set` |  | `value`*: string, `submit`: boolean |
| `whiteboard_board-file_import` |  | — |
| `whiteboard_migrate-from-miro_activate` |  | — |
| `whiteboard_grid-view_activate` |  | — |
| `whiteboard_list-view_activate` |  | — |
| `whiteboard_keyboard-shortcuts-2_activate` |  | — |

## pdf（101 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `pdf_notes-highlight-text-up-pages_leave` |  | `target`*: string |
| `pdf_fillable-fields_create` |  | `target`*: string |
| `pdf_tools_select` | 是 | `target`*: string |
| `pdf_go-page_select` | 是 | `target`*: string |
| `pdf_page-actions_select` | 是 | `target`*: string |
| `pdf_pages_select` | 是 | `target`*: string |
| `pdf_current-page_select` | 是 | `target`*: string |
| `pdf_content_dismiss` | 是 | — |
| `pdf_pdfs_previous` | 是 | — |
| `pdf_edit_update` |  | — |
| `pdf_view_show` | 是 | — |
| `pdf_page_activate` |  | — |
| `pdf_insert_create` |  | — |
| `pdf_untitled-pdf_rename` |  | — |
| `pdf_settings_show` | 是 | — |
| `pdf_tools_activate` |  | — |
| `pdf_edit-2_update` |  | — |
| `pdf_comment_activate` |  | — |
| `pdf_export_export` |  | — |
| `pdf_fill-sign_activate` |  | — |
| `pdf_text-or-tools_search` | 是 | — |
| `pdf_undo_undo` |  | — |
| `pdf_redo_redo` |  | — |
| `pdf_download_export` |  | — |
| `pdf_puter_save` |  | — |
| `pdf_tools-panel_close` | 是 | — |
| `pdf_pdf-or-its-pages-another-format_save` |  | — |
| `pdf_pdf-or-turn-pictures-into-pdf-pages_start` |  | — |
| `pdf_combine-pdfs-pictures-into-one-pdf_activate` |  | — |
| `pdf_fill-forms-add-signature_activate` |  | — |
| `pdf_make-file-smaller-by-shrinking-its-pictu_activate` |  | — |
| `pdf_more_show` | 是 | — |
| `pdf_select_select` | 是 | — |
| `pdf_hand_activate` |  | — |
| `pdf_text_activate` |  | — |
| `pdf_highlight_activate` |  | — |
| `pdf_draw_draw` |  | — |
| `pdf_shape_activate` |  | — |
| `pdf_note_activate` |  | — |
| `pdf_image_activate` |  | — |
| `pdf_sign_sign` |  | — |
| `pdf_fill-forms_activate` |  | — |
| `pdf_pdf-page-view_activate` |  | — |
| `pdf_page_previous` | 是 | — |
| `pdf_page-number_set` |  | `value`*: string, `submit`: boolean |
| `pdf_page_next` | 是 | — |
| `pdf_view_zoom-out` |  | — |
| `pdf_zoom_set` |  | `value`*: string, `submit`: boolean |
| `pdf_view_zoom-` |  | — |
| `pdf_pages_show` | 是 | — |
| `pdf_comments_show` | 是 | — |
| `pdf_attachments_show` | 是 | — |
| `pdf_pages-panel_toggle` |  | — |
| `pdf_pages-panel_close` | 是 | — |
| `pdf_dialog_close` | 是 | — |
| `pdf_appearance_set` |  | `value`*: string, `submit`: boolean |
| `pdf_keyboard-shortcuts_activate` |  | — |
| `pdf_pdf-editor_show` | 是 | — |
| `pdf_tools_previous` | 是 | — |
| `pdf_text_create` |  | — |
| `pdf_image_create` |  | — |
| `pdf_link_create` |  | — |
| `pdf_text-images_update` |  | — |
| `pdf_pages_crop` |  | — |
| `pdf_header-footer_activate` |  | — |
| `pdf_watermark_activate` |  | — |
| `pdf_page-numbers_activate` |  | — |
| `pdf_bates-numbering_activate` |  | — |
| `pdf_headers-footers_delete` |  | — |
| `pdf_watermarks_delete` |  | — |
| `pdf_find-pdf_set` |  | `value`*: string, `submit`: boolean |
| `pdf_match_previous` | 是 | — |
| `pdf_match_next` | 是 | — |
| `pdf_search_close` | 是 | — |
| `pdf_pages_toggle` |  | — |
| `pdf_page-range_set` |  | `value`*: string, `submit`: boolean |
| `pdf_cancel_cancel` | 是 | — |
| `pdf_print_print` | 是 | — |
| `pdf_comments-panel_close` | 是 | — |
| `pdf_attachments-panel_close` | 是 | — |
| `pdf_attach-file_activate` |  | — |
| `pdf_selection_select-all` |  | — |
| `pdf_selection_group-shift` |  | — |

## notes（153 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `notes_font-size_select` | 是 | `target`*: string |
| `notes_indent-position_select` | 是 | `target`*: string |
| `notes_notebook_select` | 是 | `target`*: string |
| `notes_section_create` |  | `target`*: string |
| `notes_heading-alt_select` | 是 | `target`*: string |
| `notes_normalctrlalt_select` | 是 | `target`*: string |
| `notes_doctrl_select` | 是 | `target`*: string |
| `notes_importantctrl_select` | 是 | `target`*: string |
| `notes_questionctrl_select` | 是 | `target`*: string |
| `notes_remember_select` | 是 | `target`*: string |
| `notes_definitionctrl_select` | 是 | `target`*: string |
| `notes_highlightctrl_select` | 是 | `target`*: string |
| `notes_contactctrl_select` | 是 | `target`*: string |
| `notes_addressctrl_select` | 是 | `target`*: string |
| `notes_phone-numberctrl_select` | 是 | `target`*: string |
| `notes_source_select` | 是 | `target`*: string |
| `notes_do-priority_select` | 是 | `target`*: string |
| `notes_tagctrl_delete` |  | `target`*: string |
| `notes_undo_undo` |  | — |
| `notes_redo_redo` |  | — |
| `notes_commands_show` | 是 | — |
| `notes_changes-saved-sync-now_activate` |  | — |
| `notes_share_share` |  | — |
| `notes_home_show` | 是 | — |
| `notes_insert_create` |  | — |
| `notes_draw_draw` |  | — |
| `notes_view_show` | 是 | — |
| `notes_help_show` | 是 | — |
| `notes_tell-me-what-you-want-do_set` |  | `value`*: string, `submit`: boolean |
| `notes_ribbon_collapse` | 是 | — |
| `notes_paste_paste` |  | — |
| `notes_cut_cut` |  | — |
| `notes_copy_copy` |  | — |
| `notes_format-painter_activate` |  | — |
| `notes_font_set` |  | `value`*: string, `submit`: boolean |
| `notes_font-list_activate` |  | — |
| `notes_font-size_set` |  | `value`*: string, `submit`: boolean |
| `notes_font-size-list_activate` |  | — |
| `notes_increase-font-size_activate` |  | — |
| `notes_bold_format` |  | — |
| `notes_italic_format` |  | — |
| `notes_underline_format` |  | — |
| `notes_strikethrough_format` |  | — |
| `notes_subscript_activate` |  | — |
| `notes_superscript_activate` |  | — |
| `notes_text-highlight-color_activate` |  | — |
| `notes_text-highlight-color-options_activate` |  | — |
| `notes_font-color_activate` |  | — |
| `notes_font-color-options_activate` |  | — |
| `notes_formatting_clear` |  | — |
| `notes_bullets_activate` |  | — |
| `notes_bullets-options_activate` |  | — |
| `notes_numbering_activate` |  | — |
| `notes_numbering-options_activate` |  | — |
| `notes_increase-indent-position_activate` |  | — |
| `notes_paragraph-alignment_activate` |  | — |
| `notes_paragraph-up_move` |  | — |
| `notes_paragraph-down_move` |  | — |
| `notes_styles_activate` |  | — |
| `notes_do-tag_activate` |  | — |
| `notes_tags_activate` |  | — |
| `notes_tags_search` | 是 | — |
| `notes_dictate_activate` |  | — |
| `notes_assist_activate` |  | — |
| `notes_email-page_activate` |  | — |
| `notes_notebooks_activate` |  | — |
| `notes_search_search` | 是 | — |
| `notes_recent-notes_activate` |  | — |
| `notes_account_activate` |  | — |
| `notes_quick-notes_activate` |  | — |
| `notes_section-2_create` |  | — |
| `notes_sections-pane_resize` |  | — |
| `notes_pages_sort` | 是 | — |
| `notes_untitled-page_activate` |  | — |
| `notes_page_create` |  | — |
| `notes_pages-pane_resize` |  | — |
| `notes_page-date_activate` |  | — |
| `notes_page-time_activate` |  | — |
| `notes_pagectrlaltn_create` |  | — |
| `notes_sectionctrlaltt_create` |  | — |
| `notes_section-group_create` |  | — |
| `notes_notebook_create` |  | — |
| `notes_import_import` |  | — |
| `notes_export_export` |  | — |
| `notes_more-commands-share_share` |  | — |
| `notes_ctrlp_print` | 是 | — |
| `notes_sync-nowctrls_activate` |  | — |
| `notes_deleted-notes_activate` |  | — |
| `notes_protected-sectionsctrlaltl_lock` |  | — |
| `notes_theme_activate` |  | — |
| `notes_keyboard-shortcutsctrlshift_activate` |  | — |
| `notes_notes_show` | 是 | — |
| `notes_file-pagectrlaltn_create` |  | — |
| `notes_file-sectionctrlaltt_create` |  | — |
| `notes_file-section-group_create` |  | — |
| `notes_file-notebook_create` |  | — |
| `notes_file-import_import` |  | — |
| `notes_file-export_export` |  | — |
| `notes_file-share_share` |  | — |
| `notes_file-ctrlp_print` | 是 | — |
| `notes_file-sync-nowctrls_activate` |  | — |
| `notes_file-deleted-notes_activate` |  | — |
| `notes_file-protected-sectionsctrlaltl_lock` |  | — |
| `notes_file-theme_activate` |  | — |
| `notes_file-keyboard-shortcutsctrlshift_activate` |  | — |
| `notes_file-notes_show` | 是 | — |
| `notes_page-title_activate` |  | — |
| `notes_citation_activate` |  | — |
| `notes_quote_activate` |  | — |
| `notes_code_activate` |  | — |
| `notes_website-visit_activate` |  | — |
| `notes_idea_activate` |  | — |
| `notes_password_activate` |  | — |
| `notes_critical_activate` |  | — |
| `notes_project_activate` |  | — |
| `notes_project-b_activate` |  | — |
| `notes_movie-see_activate` |  | — |
| `notes_book-read_activate` |  | — |
| `notes_music-listen_activate` |  | — |
| `notes_discuss-manager_activate` |  | — |
| `notes_email_send` |  | — |
| `notes_meeting_schedule` |  | — |
| `notes_call-back_activate` |  | — |
| `notes_client-request_activate` |  | — |
| `notes_tags-2_search` | 是 | — |
| `notes_account-theme_activate` |  | — |
| `notes_keyboard-shortcuts_activate` |  | — |
| `notes_account-notes_show` | 是 | — |
| `notes_local-s-notebook_activate` |  | — |
| `notes_notebook-locals-notebook-switch-notebook-noteboo_create` |  | — |
| `notes_notebook-settings_activate` |  | — |
| `notes_none-order_activate` |  | — |
| `notes_date-created_activate` |  | — |
| `notes_date-modified_activate` |  | — |
| `notes_alphabetical_activate` |  | — |

## records（34 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `records_account_select` | 是 | `target`*: string |
| `records_content_dismiss` | 是 | — |
| `records_home_show` | 是 | — |
| `records_trash_delete` |  | — |
| `records_base_create` |  | — |
| `records_source-code-github-opens-tab_show` | 是 | — |
| `records_search-bases_set` |  | `value`*: string, `submit`: boolean |
| `records_from-scratcha-blank-base-one-table_start` |  | — |
| `records_base-2_create` |  | — |
| `records_notice_dismiss` | 是 | — |
| `records_it_dismiss` | 是 | — |
| `records_appearance_activate` |  | — |
| `records_keyboard-shortcuts_activate` |  | — |
| `records_preview_show` | 是 | — |
| `records_source-code-github_activate` |  | — |
| `records_command-palette_show` | 是 | — |

## meetings（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `meetings_item_select` | 是 | `target`*: string |
| `meetings_meeting_create` |  | `target`*: string |
| `meetings_settings_show` | 是 | — |
| `meetings_theme_toggle` |  | — |
| `meetings_out_sign` |  | — |
| `meetings_meeting-2_create` |  | — |
| `meetings_meeting-code-or-link_set` |  | `value`*: string, `submit`: boolean |
| `meetings_join_join` |  | — |
| `meetings_today_activate` |  | — |
| `meetings_week_previous` | 是 | — |
| `meetings_week_next` | 是 | — |
| `meetings_try-again_activate` |  | — |
| `meetings_refresh_activate` |  | — |
| `meetings_close_close` | 是 | — |
| `meetings_nickname_set` |  | `value`*: string, `submit`: boolean |
| `meetings_nickname_save` |  | — |
| `meetings_instant-meeting_start` |  | — |

## teamchat（24 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `teamchat_workspacestart-space_create` |  | `target`*: string |
| `teamchat_workspacestart-space-2_create` |  | `target`*: string |
| `teamchat_messages_dismiss` | 是 | — |
| `teamchat_invitepaste-code-or-link_join` |  | — |
| `teamchat_puter_show` | 是 | — |
| `teamchat_close_close` | 是 | — |

## email（20 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `email_grant-read-access_activate` |  | — |
| `email_command-palette_show` | 是 | — |

## contacts（46 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `contacts_account-menu_activate` |  | — |
| `contacts_smart-add_activate` |  | — |
| `contacts_contact_create` |  | — |
| `contacts_search-contacts_set` |  | `value`*: string, `submit`: boolean |
| `contacts_list-options_activate` |  | — |
| `contacts_favorites_activate` |  | — |
| `contacts_contact-2_create` |  | — |
| `contacts_import_import` |  | — |
| `contacts_contact-3_create` |  | — |
| `contacts_set-photo_activate` |  | — |
| `contacts_close_close` | 是 | — |
| `contacts_first-name_set` |  | `value`*: string, `submit`: boolean |
| `contacts_last-name_set` |  | `value`*: string, `submit`: boolean |
| `contacts_nickname_set` |  | `value`*: string, `submit`: boolean |
| `contacts_company_set` |  | `value`*: string, `submit`: boolean |
| `contacts_job-title_set` |  | `value`*: string, `submit`: boolean |
| `contacts_email_create` |  | — |
| `contacts_phone_create` |  | — |
| `contacts_link_create` |  | — |
| `contacts_address_create` |  | — |
| `contacts_birthday_set` |  | `value`*: string, `submit`: boolean |
| `contacts_hide-year_toggle` |  | — |
| `contacts_tags_set` |  | `value`*: string, `submit`: boolean |
| `contacts_notes_set` |  | `value`*: string, `submit`: boolean |
| `contacts_add-favorites_toggle` |  | — |
| `contacts_cancel_cancel` | 是 | — |
| `contacts_contact-4_create` |  | — |
| `contacts_selection_select-all` |  | — |

## calendar（54 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `calendar_day-view_select` | 是 | `target`*: string |
| `calendar_item_select` | 是 | `target`*: string |
| `calendar_selected_select` | 是 | `target`*: string |
| `calendar_open_open` | 是 | `target`*: string |
| `calendar_public-holiday_select` | 是 | `target`*: string |
| `calendar_year-view-open_open` | 是 | `target`*: string |
| `calendar_year-view-item_select` | 是 | `target`*: string |
| `calendar_go_select` | 是 | `target`*: string |
| `calendar_week_start` |  | `target`*: string |
| `calendar_time_select` | 是 | `target`*: string |
| `calendar_today_activate` |  | — |
| `calendar_previous_previous` | 是 | — |
| `calendar_next_next` | 是 | — |
| `calendar_events-tasks_search` | 是 | — |
| `calendar_year-view_activate` |  | — |
| `calendar_month-view_activate` |  | — |
| `calendar_week-view_activate` |  | — |
| `calendar_day-view_activate` |  | — |
| `calendar_list-view_activate` |  | — |
| `calendar_account-settings_activate` |  | — |
| `calendar_create_create` |  | — |
| `calendar_month_previous` | 是 | — |
| `calendar_month_next` | 是 | — |
| `calendar_booking-links_hide` | 是 | — |
| `calendar_link-that-lets-others-book-time-you_share` |  | — |
| `calendar_event_create` |  | — |
| `calendar_auto_activate` |  | — |
| `calendar_light_activate` |  | — |
| `calendar_dark_activate` |  | — |
| `calendar_secondary-time-zone_set` |  | `value`*: string, `submit`: boolean |
| `calendar_public-holidays_set` |  | `value`*: string, `submit`: boolean |
| `calendar_clock-changes-daylight-saving_toggle` |  | — |
| `calendar_export_import` |  | — |
| `calendar_out_sign` |  | — |
| `calendar_document_export` |  | — |
| `calendar_command-palette_show` | 是 | — |

## signatures（47 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `signatures_0out_select` | 是 | `target`*: string |
| `signatures_0waiting_select` | 是 | `target`*: string |
| `signatures_main_select` | 是 | `target`*: string |
| `signatures_out_select` | 是 | `target`*: string |
| `signatures_waiting_select` | 是 | `target`*: string |
| `signatures_skip_dismiss` | 是 | `target`*: string |
| `signatures_signer-declinessigning-closes_select` | 是 | `target`*: string |
| `signatures_signatures-githubsend-documents_select` | 是 | `target`*: string |
| `signatures_documents_show` | 是 | — |
| `signatures_settings_show` | 是 | — |
| `signatures_document_create` |  | — |
| `signatures_document-2_create` |  | — |
| `signatures_search-documents_set` |  | `value`*: string, `submit`: boolean |
| `signatures_drafts_activate` |  | — |
| `signatures_completed_activate` |  | — |
| `signatures_closed_activate` |  | — |
| `signatures_pdf_import` |  | — |
| `signatures_close_close` | 是 | — |
| `signatures_set-up-account_activate` |  | — |
| `signatures_explore-sample-documents_activate` |  | — |
| `signatures_name-shown-signers_set` |  | `value`*: string, `submit`: boolean |
| `signatures_system_activate` |  | — |
| `signatures_light_activate` |  | — |
| `signatures_dark_activate` |  | — |
| `signatures_documents-expire_set` |  | `value`*: string, `submit`: boolean |
| `signatures_remind-signers_set` |  | `value`*: string, `submit`: boolean |
| `signatures_any-signer-signsone-email-per-signature_toggle` |  | — |
| `signatures_signature_create` |  | — |
| `signatures_puteryour-documents-live-own-puter-cloud_show` | 是 | — |

## photo-studio（121 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `photo-studio_sheet_create` |  | `target`*: string |
| `photo-studio_photo-print_create` |  | `target`*: string |
| `photo-studio_copy_export` |  | `target`*: string |
| `photo-studio_edit_update` |  | — |
| `photo-studio_image_activate` |  | — |
| `photo-studio_layer_activate` |  | — |
| `photo-studio_type_activate` |  | — |
| `photo-studio_select_select` | 是 | — |
| `photo-studio_filter_filter` | 是 | — |
| `photo-studio_view_show` | 是 | — |
| `photo-studio_window_activate` |  | — |
| `photo-studio_help_show` | 是 | — |
| `photo-studio_commands_search` | 是 | — |
| `photo-studio_puter_save` |  | — |
| `photo-studio_export_export` |  | — |
| `photo-studio_puter-account_activate` |  | — |
| `photo-studio_tool-presets_activate` |  | — |
| `photo-studio_tool-presets-2_activate` |  | — |
| `photo-studio_color-theme_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_panels_toggle` |  | — |
| `photo-studio_default-colors_activate` |  | — |
| `photo-studio_switch-colors_activate` |  | — |
| `photo-studio_background-color_activate` |  | — |
| `photo-studio_foreground-color_activate` |  | — |
| `photo-studio_foreground-color-value_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_quick-mask-mode_activate` |  | — |
| `photo-studio_screen-mode_update` |  | — |
| `photo-studio_image-canvas_activate` |  | — |
| `photo-studio_image_open` | 是 | — |
| `photo-studio_document_create` |  | — |
| `photo-studio_describe-edit_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_image_select` | 是 | — |
| `photo-studio_start_start` |  | — |
| `photo-studio_large-web-page_create` |  | — |
| `photo-studio_square-social-post_create` |  | — |
| `photo-studio_standard-phone_create` |  | — |
| `photo-studio_presets-custom-sizes_activate` |  | — |
| `photo-studio_what-s-newrecent-features_activate` |  | — |
| `photo-studio_assistant_activate` |  | — |
| `photo-studio_generation-history_activate` |  | — |
| `photo-studio_history_activate` |  | — |
| `photo-studio_actions_activate` |  | — |
| `photo-studio_version-history_activate` |  | — |
| `photo-studio_navigator_activate` |  | — |
| `photo-studio_info_activate` |  | — |
| `photo-studio_histogram_activate` |  | — |
| `photo-studio_brushes_activate` |  | — |
| `photo-studio_brush-settings_activate` |  | — |
| `photo-studio_character_activate` |  | — |
| `photo-studio_paragraph_activate` |  | — |
| `photo-studio_styles_activate` |  | — |
| `photo-studio_layer-comps_activate` |  | — |
| `photo-studio_scripts_activate` |  | — |
| `photo-studio_color_show` | 是 | — |
| `photo-studio_swatches_show` | 是 | — |
| `photo-studio_gradients_show` | 是 | — |
| `photo-studio_patterns_show` | 是 | — |
| `photo-studio_color-panel-menu_activate` |  | — |
| `photo-studio_color-saturation-brightness_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_color-hue_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_hex-color_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_properties_show` | 是 | — |
| `photo-studio_adjustments_show` | 是 | — |
| `photo-studio_properties-panel-menu_activate` |  | — |
| `photo-studio_image-size_activate` |  | — |
| `photo-studio_layers_show` | 是 | — |
| `photo-studio_channels_show` | 是 | — |
| `photo-studio_paths_show` | 是 | — |
| `photo-studio_layers-panel-menu_activate` |  | — |
| `photo-studio_filter-layers-by-kind_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_filter-layers-by-name_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_layer-filtering_activate` |  | — |
| `photo-studio_blend-mode_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_opacity_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_transparency_lock` |  | — |
| `photo-studio_image-pixels_lock` |  | — |
| `photo-studio_position_lock` |  | — |
| `photo-studio_layer_lock` |  | — |
| `photo-studio_fill_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_image_create` |  | — |
| `photo-studio_link-layers_activate` |  | — |
| `photo-studio_layer-style_create` |  | — |
| `photo-studio_layer-mask_create` |  | — |
| `photo-studio_fill-or-adjustment-layer_create` |  | — |
| `photo-studio_group_create` |  | — |
| `photo-studio_layer_create` |  | — |
| `photo-studio_layer_delete` |  | — |
| `photo-studio_view_zoom-out` |  | — |
| `photo-studio_zoom-level_set` |  | `value`*: string, `submit`: boolean |
| `photo-studio_view_zoom-` |  | — |
| `photo-studio_document-sizes_activate` |  | — |
| `photo-studio_puter_show` | 是 | — |
| `photo-studio_icon_collapse` | 是 | — |
| `photo-studio_close_close` | 是 | — |
| `photo-studio_tab-group_close` | 是 | — |
| `photo-studio_shortcut_key-0` |  | — |
| `photo-studio_selection_select-all` |  | — |
| `photo-studio_selection_lock` |  | — |
| `photo-studio_document_save` |  | — |
| `photo-studio_edit_redo` |  | — |
| `photo-studio_clipboard_paste` |  | — |
| `photo-studio_shortcut_key-w` |  | — |
| `photo-studio_edit_undo` |  | — |

## video-studio（52 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `video-studio_account_select` | 是 | `target`*: string |
| `video-studio_browse-ready-made-projects-make-own_select` | 是 | `target`*: string |
| `video-studio_youtube-project_select` | 是 | `target`*: string |
| `video-studio_vertical-project_select` | 是 | `target`*: string |
| `video-studio_square-project_select` | 是 | `target`*: string |
| `video-studio_classic-project_select` | 是 | `target`*: string |
| `video-studio_portrait-project_select` | 是 | `target`*: string |
| `video-studio_feed-post-project_select` | 是 | `target`*: string |
| `video-studio_cinema-project_select` | 是 | `target`*: string |
| `video-studio_item_select` | 是 | `target`*: string |
| `video-studio_item-2_select` | 是 | `target`*: string |
| `video-studio_item-3_select` | 是 | `target`*: string |
| `video-studio_item-4_select` | 是 | `target`*: string |
| `video-studio_item-5_select` | 是 | `target`*: string |
| `video-studio_item-6_select` | 是 | `target`*: string |
| `video-studio_editor_dismiss` | 是 | — |
| `video-studio_home_show` | 是 | — |
| `video-studio_templates_show` | 是 | — |
| `video-studio_trash_delete` |  | — |
| `video-studio_editopen-media-project_import` |  | — |
| `video-studio_see_show` | 是 | — |
| `video-studio_search-projects_set` |  | `value`*: string, `submit`: boolean |
| `video-studio_sort_sort` | 是 | — |
| `video-studio_as-list_show` | 是 | — |
| `video-studio_project-actions_show` | 是 | — |
| `video-studio_powered-by-puter_show` | 是 | — |
| `video-studio_theme_activate` |  | — |
| `video-studio_last-modified_activate` |  | — |
| `video-studio_date-created_activate` |  | — |
| `video-studio_name_activate` |  | — |
| `video-studio_project-file_open` | 是 | — |
| `video-studio_media_import` |  | — |
| `video-studio_more-project-actions-trash_delete` |  | — |
| `video-studio_selection_select-all` |  | — |

## vector-studio（106 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `vector-studio_account_select` | 是 | `target`*: string |
| `vector-studio_drawing-modes_select` | 是 | `target`*: string |
| `vector-studio_letter-x_select` | 是 | `target`*: string |
| `vector-studio_x-mm_select` | 是 | `target`*: string |
| `vector-studio_postcard-x-pt_select` | 是 | `target`*: string |
| `vector-studio_web-x-px_select` | 是 | `target`*: string |
| `vector-studio_mobile-x-px_select` | 是 | `target`*: string |
| `vector-studio_square-x-px_select` | 是 | `target`*: string |
| `vector-studio_icon-x-px_select` | 是 | `target`*: string |
| `vector-studio_poster-x_select` | 是 | `target`*: string |
| `vector-studio_preview_select` | 是 | `target`*: string |
| `vector-studio_canvas_dismiss` | 是 | — |
| `vector-studio_home_activate` |  | — |
| `vector-studio_edit_update` |  | — |
| `vector-studio_object_activate` |  | — |
| `vector-studio_type_activate` |  | — |
| `vector-studio_select_select` | 是 | — |
| `vector-studio_effect_activate` |  | — |
| `vector-studio_view_show` | 是 | — |
| `vector-studio_window_activate` |  | — |
| `vector-studio_help_show` | 是 | — |
| `vector-studio_theme_activate` |  | — |
| `vector-studio_single-or-double-column-tools_toggle` |  | — |
| `vector-studio_selection-tool_activate` |  | — |
| `vector-studio_direct-selection-tool_activate` |  | — |
| `vector-studio_magic-wand-tool_activate` |  | — |
| `vector-studio_lasso-tool_activate` |  | — |
| `vector-studio_pen-tool_activate` |  | — |
| `vector-studio_curvature-tool_activate` |  | — |
| `vector-studio_sketch-shape-tool_activate` |  | — |
| `vector-studio_paintbrush-tool_activate` |  | — |
| `vector-studio_rectangle-tool_activate` |  | — |
| `vector-studio_line-segment-tool_activate` |  | — |
| `vector-studio_shape-builder-tool_activate` |  | — |
| `vector-studio_type-tool_activate` |  | — |
| `vector-studio_tool_rotate` |  | — |
| `vector-studio_scale-tool_activate` |  | — |
| `vector-studio_width-tool_activate` |  | — |
| `vector-studio_free-transform-tool_activate` |  | — |
| `vector-studio_eraser-tool_activate` |  | — |
| `vector-studio_perspective-grid-tool_activate` |  | — |
| `vector-studio_gradient-tool_activate` |  | — |
| `vector-studio_mesh-tool_activate` |  | — |
| `vector-studio_eyedropper-tool_activate` |  | — |
| `vector-studio_blend-tool_activate` |  | — |
| `vector-studio_symbol-sprayer-tool_activate` |  | — |
| `vector-studio_column-graph-tool_activate` |  | — |
| `vector-studio_artboard-tool_activate` |  | — |
| `vector-studio_hand-tool_activate` |  | — |
| `vector-studio_view_zoom-tool` |  | — |
| `vector-studio_fill_activate` |  | — |
| `vector-studio_stroke_activate` |  | — |
| `vector-studio_swap-fill-stroke_activate` |  | — |
| `vector-studio_default-fill-stroke_activate` |  | — |
| `vector-studio_color_activate` |  | — |
| `vector-studio_gradient_activate` |  | — |
| `vector-studio_none_activate` |  | — |
| `vector-studio_tools_activate` |  | — |
| `vector-studio_screen-mode_update` |  | — |
| `vector-studio_open_open` | 是 | — |
| `vector-studio_home-2_activate` |  | — |
| `vector-studio_recent_activate` |  | — |
| `vector-studio_files_activate` |  | — |
| `vector-studio_templates_activate` |  | — |
| `vector-studio_hide_hide` | 是 | — |
| `vector-studio_presets-sizes-settings_show` | 是 | — |
| `vector-studio_refresh-files_activate` |  | — |
| `vector-studio_powered-by-puter_show` | 是 | — |
| `vector-studio_panels_activate` |  | — |
| `vector-studio_color-paint-panels_activate` |  | — |
| `vector-studio_arrange-shape-panels_activate` |  | — |
| `vector-studio_type-panels_activate` |  | — |
| `vector-studio_symbols_activate` |  | — |
| `vector-studio_libraries_activate` |  | — |
| `vector-studio_asset-export_activate` |  | — |
| `vector-studio_generate_run` |  | — |
| `vector-studio_generation-history_activate` |  | — |
| `vector-studio_document-panels_activate` |  | — |
| `vector-studio_flattener-preview_activate` |  | — |
| `vector-studio_variables_activate` |  | — |
| `vector-studio_svg-interactivity_activate` |  | — |
| `vector-studio_actions_activate` |  | — |
| `vector-studio_mockup_activate` |  | — |
| `vector-studio_match-font_activate` |  | — |
| `vector-studio_properties_show` | 是 | — |
| `vector-studio_layers_show` | 是 | — |
| `vector-studio_signed-as-local_activate` |  | — |
| `vector-studio_shortcut_key-5` |  | — |

## audio-studio（165 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `audio-studio_account_select` | 是 | `target`*: string |
| `audio-studio_waveform_select` | 是 | `target`*: string |
| `audio-studio_multitrack_select` | 是 | `target`*: string |
| `audio-studio_selection-tool-e_select` | 是 | `target`*: string |
| `audio-studio_edit_update` |  | — |
| `audio-studio_multitrack_activate` |  | — |
| `audio-studio_clip_activate` |  | — |
| `audio-studio_effects_activate` |  | — |
| `audio-studio_favorites_activate` |  | — |
| `audio-studio_view_show` | 是 | — |
| `audio-studio_window_activate` |  | — |
| `audio-studio_help_show` | 是 | — |
| `audio-studio_spectral-frequency-display-shiftd_show` | 是 | — |
| `audio-studio_spectral-pitch-display_show` | 是 | — |
| `audio-studio_tool-v_move` |  | — |
| `audio-studio_razor-tool-r_activate` |  | — |
| `audio-studio_slip-tool-y_activate` |  | — |
| `audio-studio_time-selection-tool-t_activate` |  | — |
| `audio-studio_lasso-selection-tool-d_activate` |  | — |
| `audio-studio_paintbrush-selection-tool-p_activate` |  | — |
| `audio-studio_spot-healing-brush-tool-b_activate` |  | — |
| `audio-studio_workspaces_activate` |  | — |
| `audio-studio_search-commands_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_files_show` | 是 | — |
| `audio-studio_files-panel-menu_activate` |  | — |
| `audio-studio_favorites_show` | 是 | — |
| `audio-studio_open_open` | 是 | — |
| `audio-studio_import_import` |  | — |
| `audio-studio_audio-file_create` |  | — |
| `audio-studio_into-multitrack_create` |  | — |
| `audio-studio_close_close` | 是 | — |
| `audio-studio_search-files_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_name_activate` |  | — |
| `audio-studio_status_activate` |  | — |
| `audio-studio_duration_activate` |  | — |
| `audio-studio_sample-rate_activate` |  | — |
| `audio-studio_channels_activate` |  | — |
| `audio-studio_bit-depth_activate` |  | — |
| `audio-studio_format_activate` |  | — |
| `audio-studio_from-start_play` |  | — |
| `audio-studio_loop-playback_activate` |  | — |
| `audio-studio_auto-play_toggle` |  | — |
| `audio-studio_panels_resize` |  | — |
| `audio-studio_media-browser_show` | 是 | — |
| `audio-studio_media-browser-panel-menu_activate` |  | — |
| `audio-studio_effects-rack_show` | 是 | — |
| `audio-studio_markers_show` | 是 | — |
| `audio-studio_properties_show` | 是 | — |
| `audio-studio_panels-group_activate` |  | — |
| `audio-studio_up-one-level_activate` |  | — |
| `audio-studio_refresh_activate` |  | — |
| `audio-studio_folder-from-device_create` |  | — |
| `audio-studio_home_activate` |  | — |
| `audio-studio_search-folder_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_only-audio-files_show` | 是 | — |
| `audio-studio_homeappdata_activate` |  | — |
| `audio-studio_appdata_activate` |  | — |
| `audio-studio_folder_create` |  | — |
| `audio-studio_appdatafolder_activate` |  | — |
| `audio-studio_preview_play` |  | — |
| `audio-studio_preview_stop` |  | — |
| `audio-studio_loop-preview_activate` |  | — |
| `audio-studio_preview-position_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_auto-play-2_toggle` |  | — |
| `audio-studio_open-2_open` | 是 | — |
| `audio-studio_into-multitrack-2_create` |  | — |
| `audio-studio_history_show` | 是 | — |
| `audio-studio_history-panel-menu_activate` |  | — |
| `audio-studio_video_show` | 是 | — |
| `audio-studio_history_clear` |  | — |
| `audio-studio_editor_show` | 是 | — |
| `audio-studio_editor-panel-menu_activate` |  | — |
| `audio-studio_mixer_show` | 是 | — |
| `audio-studio_open-3_open` | 是 | — |
| `audio-studio_audio-file-2_create` |  | — |
| `audio-studio_multitrack-session_create` |  | — |
| `audio-studio_record_record` |  | — |
| `audio-studio_playhead-time_activate` |  | — |
| `audio-studio_stop_stop` |  | — |
| `audio-studio_space_play` |  | — |
| `audio-studio_pause_pause` |  | — |
| `audio-studio_playhead-previous_move` |  | — |
| `audio-studio_rewind_activate` |  | — |
| `audio-studio_fast-forward_activate` |  | — |
| `audio-studio_playhead-next_move` |  | — |
| `audio-studio_shiftspace_record` |  | — |
| `audio-studio_selection_dismiss` | 是 | — |
| `audio-studio_view_zoom-` |  | — |
| `audio-studio_view_zoom-out` |  | — |
| `audio-studio_view-2_zoom-` |  | — |
| `audio-studio_view-2_zoom-out` |  | — |
| `audio-studio_view-3_zoom-out` |  | — |
| `audio-studio_view-3_zoom-` |  | — |
| `audio-studio_view-4_zoom-` |  | — |
| `audio-studio_view-5_zoom-` |  | — |
| `audio-studio_view_zoom-reset` |  | — |
| `audio-studio_view-6_zoom-` |  | — |
| `audio-studio_sound-assistant_show` | 是 | — |
| `audio-studio_sound-assistant-panel-menu_activate` |  | — |
| `audio-studio_levels_show` | 是 | — |
| `audio-studio_levels-panel-menu_activate` |  | — |
| `audio-studio_left-channel-clip-indicator-click-reset_activate` |  | — |
| `audio-studio_right-channel-clip-indicator-click-reset_activate` |  | — |
| `audio-studio_selection-view_show` | 是 | — |
| `audio-studio_selection-view-panel-menu_activate` |  | — |
| `audio-studio_selection-start_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_selection-end_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_selection-duration_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_view-start_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_view-end_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_view-duration_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_signed-as-local_activate` |  | — |
| `audio-studio_saved-layout_reset` |  | — |
| `audio-studio_changes-workspace_save` |  | — |
| `audio-studio_as-workspace_save` |  | — |
| `audio-studio_workspaces_update` |  | — |
| `audio-studio_ctrlo_open` | 是 | — |
| `audio-studio_file-ctrli_import` |  | — |
| `audio-studio_audio-file-altshiftn_create` |  | — |
| `audio-studio_into-multitrack-session_create` |  | — |
| `audio-studio_closealtw_activate` |  | — |
| `audio-studio_allaltshiftw_close` | 是 | — |
| `audio-studio_columns_activate` |  | — |
| `audio-studio_by-open-order_sort` | 是 | — |
| `audio-studio_panel_close` | 是 | — |
| `audio-studio_other-panels-group_close` | 是 | — |
| `audio-studio_panel-group_close` | 是 | — |
| `audio-studio_maximize-frame_activate` |  | — |
| `audio-studio_file-name_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_sample-rate_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_channels_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_bit-depth_set` |  | `value`*: string, `submit`: boolean |
| `audio-studio_cancel_cancel` | 是 | — |
| `audio-studio_ok_confirm` |  | — |
| `audio-studio_media-browser-panel-menu-panel_close` | 是 | — |
| `audio-studio_media-browser-panel-menu-other-panels-group_close` | 是 | — |
| `audio-studio_media-browser-panel-menu-panel-group_close` | 是 | — |
| `audio-studio_media-browser-panel-menu-maximize-frame_activate` |  | — |
| `audio-studio_undoctrlz_activate` |  | — |
| `audio-studio_redoctrlshiftz_activate` |  | — |
| `audio-studio_later-states_delete` |  | — |
| `audio-studio_history-panel-menu-history_clear` |  | — |
| `audio-studio_history-panel-menu-panel_close` | 是 | — |
| `audio-studio_history-panel-menu-other-panels-group_close` | 是 | — |
| `audio-studio_history-panel-menu-panel-group_close` | 是 | — |
| `audio-studio_history-panel-menu-maximize-frame_activate` |  | — |
| `audio-studio_selection_select-all` |  | — |

## music-studio（283 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `music-studio_pattern-mode_select` | 是 | `target`*: string |
| `music-studio_song-mode_select` | 是 | `target`*: string |
| `music-studio_pattern_select` | 是 | `target`*: string |
| `music-studio_project_select` | 是 | `target`*: string |
| `music-studio_account_select` | 是 | `target`*: string |
| `music-studio_one-synthesized-drum-voice_select` | 是 | `target`*: string |
| `music-studio_browser_select` | 是 | `target`*: string |
| `music-studio_beat-clips_select` | 是 | `target`*: string |
| `music-studio_bassline-clips_select` | 是 | `target`*: string |
| `music-studio_chords-clips_select` | 是 | `target`*: string |
| `music-studio_lead-clip_select` | 是 | `target`*: string |
| `music-studio_track-1_select` | 是 | `target`*: string |
| `music-studio_track-2_select` | 是 | `target`*: string |
| `music-studio_track-3_select` | 是 | `target`*: string |
| `music-studio_track-4_select` | 是 | `target`*: string |
| `music-studio_track-5_select` | 是 | `target`*: string |
| `music-studio_mute-track_select` | 是 | `target`*: string |
| `music-studio_solo-track_select` | 是 | `target`*: string |
| `music-studio_track-6_select` | 是 | `target`*: string |
| `music-studio_track-7_select` | 是 | `target`*: string |
| `music-studio_track-8_select` | 是 | `target`*: string |
| `music-studio_track-9_select` | 是 | `target`*: string |
| `music-studio_track-10_select` | 是 | `target`*: string |
| `music-studio_track-11_select` | 是 | `target`*: string |
| `music-studio_track-12_select` | 是 | `target`*: string |
| `music-studio_track-13_select` | 是 | `target`*: string |
| `music-studio_track-14_select` | 是 | `target`*: string |
| `music-studio_track-15_select` | 是 | `target`*: string |
| `music-studio_track-16_select` | 是 | `target`*: string |
| `music-studio_kick_select` | 是 | `target`*: string |
| `music-studio_channel-rack-beat_select` | 是 | `target`*: string |
| `music-studio_kick-2_select` | 是 | `target`*: string |
| `music-studio_step-velocity_select` | 是 | `target`*: string |
| `music-studio_step-off_select` | 是 | `target`*: string |
| `music-studio_clap_select` | 是 | `target`*: string |
| `music-studio_clap-2_select` | 是 | `target`*: string |
| `music-studio_closed-hat_select` | 是 | `target`*: string |
| `music-studio_closed-hat-2_select` | 是 | `target`*: string |
| `music-studio_hat_open` | 是 | `target`*: string |
| `music-studio_hat-2_open` | 是 | `target`*: string |
| `music-studio_bass_select` | 是 | `target`*: string |
| `music-studio_bass-2_select` | 是 | `target`*: string |
| `music-studio_chords_select` | 是 | `target`*: string |
| `music-studio_chords-2_select` | 是 | `target`*: string |
| `music-studio_lead_select` | 是 | `target`*: string |
| `music-studio_lead-2_select` | 是 | `target`*: string |
| `music-studio_master-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-master_send` |  | `target`*: string |
| `music-studio_inputs_select` | 是 | `target`*: string |
| `music-studio_kick-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_clap-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-clap_send` |  | `target`*: string |
| `music-studio_hats-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-hats_send` |  | `target`*: string |
| `music-studio_bass-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-bass_send` |  | `target`*: string |
| `music-studio_chords-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-chords_send` |  | `target`*: string |
| `music-studio_lead-double-click-or-rename_select` | 是 | `target`*: string |
| `music-studio_kick-lead_send` |  | `target`*: string |
| `music-studio_double-click-or-rename_create` |  | `target`*: string |
| `music-studio_mute-insert_select` | 是 | `target`*: string |
| `music-studio_solo-insert_select` | 是 | `target`*: string |
| `music-studio_kick-insert_send` |  | `target`*: string |
| `music-studio_double-click-or-rename-2_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-3_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-4_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-5_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-6_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-7_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-8_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-9_create` |  | `target`*: string |
| `music-studio_double-click-or-rename-10_create` |  | `target`*: string |
| `music-studio_effect_select` | 是 | `target`*: string |
| `music-studio_beat_select` | 是 | `target`*: string |
| `music-studio_bassline_select` | 是 | `target`*: string |
| `music-studio_pattern-beat-select-pattern-chords_select` | 是 | `target`*: string |
| `music-studio_pattern-beat-select-pattern-lead_select` | 是 | `target`*: string |
| `music-studio_pattern_rename` |  | `target`*: string |
| `music-studio_clap-master_send` |  | `target`*: string |
| `music-studio_clap-kick_send` |  | `target`*: string |
| `music-studio_clap-hats_send` |  | `target`*: string |
| `music-studio_clap-bass_send` |  | `target`*: string |
| `music-studio_clap-chords_send` |  | `target`*: string |
| `music-studio_clap-lead_send` |  | `target`*: string |
| `music-studio_clap-insert_send` |  | `target`*: string |
| `music-studio_hats-master_send` |  | `target`*: string |
| `music-studio_hats-kick_send` |  | `target`*: string |
| `music-studio_hats-clap_send` |  | `target`*: string |
| `music-studio_hats-bass_send` |  | `target`*: string |
| `music-studio_hats-chords_send` |  | `target`*: string |
| `music-studio_hats-lead_send` |  | `target`*: string |
| `music-studio_hats-insert_send` |  | `target`*: string |
| `music-studio_bass-master_send` |  | `target`*: string |
| `music-studio_bass-kick_send` |  | `target`*: string |
| `music-studio_bass-clap_send` |  | `target`*: string |
| `music-studio_bass-hats_send` |  | `target`*: string |
| `music-studio_bass-chords_send` |  | `target`*: string |
| `music-studio_bass-lead_send` |  | `target`*: string |
| `music-studio_bass-insert_send` |  | `target`*: string |
| `music-studio_chords-master_send` |  | `target`*: string |
| `music-studio_chords-kick_send` |  | `target`*: string |
| `music-studio_chords-clap_send` |  | `target`*: string |
| `music-studio_chords-hats_send` |  | `target`*: string |
| `music-studio_chords-bass_send` |  | `target`*: string |
| `music-studio_chords-lead_send` |  | `target`*: string |
| `music-studio_chords-insert_send` |  | `target`*: string |
| `music-studio_reverb-slot-open-editor_select` | 是 | `target`*: string |
| `music-studio_lead-master_send` |  | `target`*: string |
| `music-studio_lead-kick_send` |  | `target`*: string |
| `music-studio_lead-clap_send` |  | `target`*: string |
| `music-studio_lead-hats_send` |  | `target`*: string |
| `music-studio_lead-bass_send` |  | `target`*: string |
| `music-studio_lead-chords_send` |  | `target`*: string |
| `music-studio_lead-insert_send` |  | `target`*: string |
| `music-studio_delay-slot-open-editor_select` | 是 | `target`*: string |
| `music-studio_lead-click-select-double-click-or-enter-reverb-s_select` | 是 | `target`*: string |
| `music-studio_add-mixer-insert-project_select` | 是 | `target`*: string |
| `music-studio_insert-master_send` |  | `target`*: string |
| `music-studio_insert-kick_send` |  | `target`*: string |
| `music-studio_insert-clap_send` |  | `target`*: string |
| `music-studio_insert-hats_send` |  | `target`*: string |
| `music-studio_insert-bass_send` |  | `target`*: string |
| `music-studio_insert-chords_send` |  | `target`*: string |
| `music-studio_insert-lead_send` |  | `target`*: string |
| `music-studio_insert-insert_send` |  | `target`*: string |
| `music-studio_add-mixer-insert-double-click-or-rename_create` |  | `target`*: string |
| `music-studio_volume_create` |  | `target`*: string |
| `music-studio_add-mixer-insert-mute-insert_select` | 是 | `target`*: string |
| `music-studio_add-mixer-insert-solo-insert_select` | 是 | `target`*: string |
| `music-studio_workspace_dismiss` | 是 | — |
| `music-studio_edit_update` |  | — |
| `music-studio_add_create` |  | — |
| `music-studio_patterns_activate` |  | — |
| `music-studio_view_show` | 是 | — |
| `music-studio_options_activate` |  | — |
| `music-studio_tools_activate` |  | — |
| `music-studio_help_show` | 是 | — |
| `music-studio_play_play` |  | — |
| `music-studio_stop_stop` |  | — |
| `music-studio_record_record` |  | — |
| `music-studio_tempo-beats-per-minute_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_metronome_activate` |  | — |
| `music-studio_count-in-before-recording_activate` |  | — |
| `music-studio_typing-keyboard-piano_activate` |  | — |
| `music-studio_pattern_previous` | 是 | — |
| `music-studio_pattern_next` | 是 | — |
| `music-studio_pattern_create` |  | — |
| `music-studio_playlist_activate` |  | — |
| `music-studio_channel-rack_activate` |  | — |
| `music-studio_piano-roll_activate` |  | — |
| `music-studio_mixer_activate` |  | — |
| `music-studio_browser_activate` |  | — |
| `music-studio_master-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_source-code-github-opens-tab_show` | 是 | — |
| `music-studio_audio_import` |  | — |
| `music-studio_collapse_collapse` | 是 | — |
| `music-studio_browser_close` | 是 | — |
| `music-studio_search-browser_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_instruments_activate` |  | — |
| `music-studio_synth-presets_activate` |  | — |
| `music-studio_drum-presets_activate` |  | — |
| `music-studio_effects_activate` |  | — |
| `music-studio_project_activate` |  | — |
| `music-studio_files_activate` |  | — |
| `music-studio_music-studio-files_activate` |  | — |
| `music-studio_browse-another-folder_activate` |  | — |
| `music-studio_audio-from-device_import` |  | — |
| `music-studio_device_activate` |  | — |
| `music-studio_browser_resize` |  | — |
| `music-studio_clip-sources_show` | 是 | — |
| `music-studio_tool_draw` |  | — |
| `music-studio_paint-tool_activate` |  | — |
| `music-studio_tool_delete` |  | — |
| `music-studio_mute-tool_activate` |  | — |
| `music-studio_slice-tool_activate` |  | — |
| `music-studio_tool_select` | 是 | — |
| `music-studio_view_zoom-tool` |  | — |
| `music-studio_playback-tool_activate` |  | — |
| `music-studio_snap_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_follow-playhead_activate` |  | — |
| `music-studio_follow-options_activate` |  | — |
| `music-studio_view_zoom-out` |  | — |
| `music-studio_view_zoom-` |  | — |
| `music-studio_view-2_zoom-` |  | — |
| `music-studio_maximize-playlist_activate` |  | — |
| `music-studio_playlist_close` | 是 | — |
| `music-studio_automation-clip_create` |  | — |
| `music-studio_clip-source-list_resize` |  | — |
| `music-studio_track_create` |  | — |
| `music-studio_song-position_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_mute-drums_activate` |  | — |
| `music-studio_solo-drums_activate` |  | — |
| `music-studio_mute-bass_activate` |  | — |
| `music-studio_solo-bass_activate` |  | — |
| `music-studio_mute-chords_activate` |  | — |
| `music-studio_solo-chords_activate` |  | — |
| `music-studio_mute-lead_activate` |  | — |
| `music-studio_solo-lead_activate` |  | — |
| `music-studio_playlist-arrangement_activate` |  | — |
| `music-studio_editors_resize` |  | — |
| `music-studio_bar_delete` |  | — |
| `music-studio_bar_create` |  | — |
| `music-studio_swing_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_velocity-lane_activate` |  | — |
| `music-studio_channel_create` |  | — |
| `music-studio_maximize-channel-rack_activate` |  | — |
| `music-studio_channel-rack_close` | 是 | — |
| `music-studio_kick-3_select` | 是 | — |
| `music-studio_clap-3_select` | 是 | — |
| `music-studio_closed-hat-3_select` | 是 | — |
| `music-studio_open-hat_select` | 是 | — |
| `music-studio_bass-3_select` | 是 | — |
| `music-studio_chords-3_select` | 是 | — |
| `music-studio_lead-3_select` | 是 | — |
| `music-studio_channel-2_create` |  | — |
| `music-studio_panels_resize` |  | — |
| `music-studio_mixer-insert_create` |  | — |
| `music-studio_effects-routing-panel_activate` |  | — |
| `music-studio_maximize-mixer_activate` |  | — |
| `music-studio_mixer_close` | 是 | — |
| `music-studio_mute-master_activate` |  | — |
| `music-studio_pan_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_width_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_kick-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_mute-kick_activate` |  | — |
| `music-studio_solo-kick_activate` |  | — |
| `music-studio_mute-clap_activate` |  | — |
| `music-studio_solo-clap_activate` |  | — |
| `music-studio_mute-hats_activate` |  | — |
| `music-studio_solo-hats_activate` |  | — |
| `music-studio_options_create` |  | — |
| `music-studio_insert_select` | 是 | — |
| `music-studio_send-level-master_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_send-master_delete` |  | — |
| `music-studio_send_create` |  | — |
| `music-studio_channel-rack_select` | 是 | — |
| `music-studio_music-studio-is-open-source_show` | 是 | — |
| `music-studio_take-tour_activate` |  | — |
| `music-studio_it_dismiss` | 是 | — |
| `music-studio_pattern-beat-select-pattern-pattern_create` |  | — |
| `music-studio_clone-pattern_activate` |  | — |
| `music-studio_signed-as-local_activate` |  | — |
| `music-studio_follow-options-follow-playhead_activate` |  | — |
| `music-studio_page-by-page_activate` |  | — |
| `music-studio_continuous_activate` |  | — |
| `music-studio_poly-synth_activate` |  | — |
| `music-studio_drum-synth_activate` |  | — |
| `music-studio_sampler_activate` |  | — |
| `music-studio_add-channel-synth-presets_activate` |  | — |
| `music-studio_add-channel-drum-presets_activate` |  | — |
| `music-studio_sampler-from-audio-file_activate` |  | — |
| `music-studio_clap-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_hats-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_bass-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_chords-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_drag-reorder-ctrlup-down_activate` |  | — |
| `music-studio_reverb_activate` |  | — |
| `music-studio_reverb-mix_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_reverb-options_activate` |  | — |
| `music-studio_lead-volume_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_delay_activate` |  | — |
| `music-studio_delay-mix_set` |  | `value`*: string, `submit`: boolean |
| `music-studio_delay-options_activate` |  | — |
| `music-studio_shortcut_key-t` |  | — |

## 3d（247 个工具）

### `3d_app_open`

打开应用（桌面窗口；--headless 用无界面实例）。CLI：foxos 3d app open [--file FILE] [--headless]。示例：foxos 3d app open

只读：否 · 破坏性：否 · CLI：`foxos 3d app open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string |  | 同时打开工作空间中的文件 |
| `headless` | boolean |  | 不显示窗口 |

调用示例：

```json
{"name": "3d_app_open", "arguments": {}}
```

### `3d_app_close`

关闭应用实例。CLI：foxos 3d app close。示例：foxos 3d app close --json

只读：否 · 破坏性：否 · CLI：`foxos 3d app close`

调用示例：

```json
{"name": "3d_app_close", "arguments": {}}
```

### `3d_app_status`

应用是否已安装、是否在运行。CLI：foxos 3d app status。示例：foxos 3d app status --json

只读：是 · 破坏性：否 · CLI：`foxos 3d app status`

调用示例：

```json
{"name": "3d_app_status", "arguments": {}}
```

### `3d_app_reset`

重置应用：关闭实例并清空本工作空间下的应用数据（AppData/<应用> 与浏览器存储）。CLI：foxos 3d app reset。示例：foxos 3d app reset --json

只读：否 · 破坏性：是 · CLI：`foxos 3d app reset`

调用示例：

```json
{"name": "3d_app_reset", "arguments": {}}
```

### `3d_file_open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）。CLI：foxos 3d file open PATH。示例：foxos 3d file open X

只读：否 · 破坏性：否 · CLI：`foxos 3d file open`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |

调用示例：

```json
{"name": "3d_file_open", "arguments": {"path": "…"}}
```

### `3d_ui_snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值。CLI：foxos 3d ui snapshot [--all] [--limit LIMIT]。示例：foxos 3d ui snapshot --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui snapshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `all` | boolean |  | 包括不可见元素 |
| `limit` | integer |  | 最多返回元素数 |

调用示例：

```json
{"name": "3d_ui_snapshot", "arguments": {}}
```

### `3d_ui_text`

读取界面上的可见文本。CLI：foxos 3d ui text。示例：foxos 3d ui text --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui text`

调用示例：

```json
{"name": "3d_ui_text", "arguments": {}}
```

### `3d_ui_click`

点击控件（按 ref 或名称），与人点击相同。CLI：foxos 3d ui click [--ref REF] [--name NAME] [--role ROLE] [--force]。示例：foxos 3d ui click --ref e12

只读：否 · 破坏性：否 · CLI：`foxos 3d ui click`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `ref` | string |  | snapshot 返回的元素引用 |
| `name` | string |  | 按可访问名称查找 |
| `role` | string |  | 限定角色，如 button |
| `force` | boolean |  | 控件被弹窗挡住时也强制点击 |

调用示例：

```json
{"name": "3d_ui_click", "arguments": {}}
```

### `3d_ui_type`

向控件输入文本（真实输入事件）。CLI：foxos 3d ui type TEXT [--ref REF] [--clear]。示例：foxos 3d ui type 'hello' --ref e5

只读：否 · 破坏性：否 · CLI：`foxos 3d ui type`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | string | 是 | 要输入的文本 |
| `ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | boolean |  | 先清空 |

调用示例：

```json
{"name": "3d_ui_type", "arguments": {"text": "…"}}
```

### `3d_ui_set`

设置输入框 / 下拉框 / 复选框的值。CLI：foxos 3d ui set --ref REF --value VALUE [--force]。示例：foxos 3d ui set 

只读：否 · 破坏性：否 · CLI：`foxos 3d ui set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `ref` | string | 是 | 元素引用 |
| `value` | string | 是 | 值 |
| `force` | boolean |  | 控件被挡住时也强制设置 |

调用示例：

```json
{"name": "3d_ui_set", "arguments": {"ref": "…", "value": "…"}}
```

### `3d_ui_press`

按键或快捷键（如 Enter、ctrl+z、mod+s）。CLI：foxos 3d ui press KEY [--ref REF]。示例：foxos 3d ui press mod+z

只读：否 · 破坏性：否 · CLI：`foxos 3d ui press`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 按键 |
| `ref` | string |  | 先聚焦的元素引用 |

调用示例：

```json
{"name": "3d_ui_press", "arguments": {"key": "…"}}
```

### `3d_ui_screenshot`

应用窗口截图（PNG）。CLI：foxos 3d ui screenshot [--out OUT]。示例：foxos 3d ui screenshot --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ui screenshot`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `out` | string |  | 保存到工作空间路径 |

调用示例：

```json
{"name": "3d_ui_screenshot", "arguments": {}}
```

### `3d_data_list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）。CLI：foxos 3d data list [PATTERN]。示例：foxos 3d data list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d data list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pattern` | string |  | 通配符 |

调用示例：

```json
{"name": "3d_data_list", "arguments": {}}
```

### `3d_data_get`

读取应用保存的一项数据。CLI：foxos 3d data get KEY。示例：foxos 3d data get X

只读：是 · 破坏性：否 · CLI：`foxos 3d data get`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 数据键 |

调用示例：

```json
{"name": "3d_data_get", "arguments": {"key": "…"}}
```

### `3d_module_list`

列出应用自己的 ES 模块及导出（供 module call 使用）。CLI：foxos 3d module list。示例：foxos 3d module list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d module list`

调用示例：

```json
{"name": "3d_module_list", "arguments": {}}
```

### `3d_module_read`

读取应用模块中的值（如 store 状态）。CLI：foxos 3d module read TARGET。示例：foxos 3d module read X

只读：是 · 破坏性：否 · CLI：`foxos 3d module read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

调用示例：

```json
{"name": "3d_module_read", "arguments": {"target": "…"}}
```

### `3d_module_call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）。CLI：foxos 3d module call TARGET [--args ARGS]。示例：foxos 3d module call X

只读：否 · 破坏性：否 · CLI：`foxos 3d module call`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 模块路径#导出.方法 |
| `args` | array |  | 参数（JSON 数组） |

调用示例：

```json
{"name": "3d_module_call", "arguments": {"target": "…"}}
```

### `3d_op_list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）。CLI：foxos 3d op list。示例：foxos 3d op list --json

只读：是 · 破坏性：否 · CLI：`foxos 3d op list`

调用示例：

```json
{"name": "3d_op_list", "arguments": {}}
```

### `3d_cozy-room_select`

a cozy room: *（1 项，如 A cozy room: floor, two walls, a sofa and a lamp）。CLI：foxos 3d cozy-room select TARGET。界面：主界面 > Conversation > a cozy room: *。效果：点击名称匹配的「a cozy room: *」项（button）。示例：foxos 3d cozy-room select 'A cozy room: floor, two walls, a sofa and a lamp' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d cozy-room select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'A cozy room: floor, two walls, a sofa and a lamp' |

调用示例：

```json
{"name": "3d_cozy-room_select", "arguments": {"target": "…"}}
```

### `3d_adjust-last-operation_select`

adjust last operation…#（1 项，如 Adjust Last Operation…F9）。CLI：foxos 3d adjust-last-operation select TARGET。界面：Edit > menu > adjust last operation…#。效果：点击名称匹配的「adjust last operation…#」项（menuitem）。示例：foxos 3d adjust-last-operation select 'Adjust Last Operation…F9' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d adjust-last-operation select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Adjust Last Operation…F9' |

调用示例：

```json
{"name": "3d_adjust-last-operation_select", "arguments": {"target": "…"}}
```

### `3d_search_show`

menu search…#（1 项，如 Menu Search…F3）。CLI：foxos 3d search show TARGET。界面：Edit > menu > menu search…#。效果：点击名称匹配的「menu search…#」项（menuitem）。示例：foxos 3d search show 'Menu Search…F3' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d search show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Menu Search…F3' |

调用示例：

```json
{"name": "3d_search_show", "arguments": {"target": "…"}}
```

### `3d_active-item_rename`

rename active item…#（1 项，如 Rename Active Item…F2）。CLI：foxos 3d active-item rename TARGET。界面：Edit > menu > rename active item…#。效果：点击名称匹配的「rename active item…#」项（menuitem）。示例：foxos 3d active-item rename 'Rename Active Item…F2' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d active-item rename`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Rename Active Item…F2' |

调用示例：

```json
{"name": "3d_active-item_rename", "arguments": {"target": "…"}}
```

### `3d_batch-rename-ctrl_select`

batch rename…ctrl #（1 项，如 Batch Rename…Ctrl F2）。CLI：foxos 3d batch-rename-ctrl select TARGET。界面：Edit > menu > batch rename…ctrl #。效果：点击名称匹配的「batch rename…ctrl #」项（menuitem）。示例：foxos 3d batch-rename-ctrl select 'Batch Rename…Ctrl F2' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d batch-rename-ctrl select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Batch Rename…Ctrl F2' |

调用示例：

```json
{"name": "3d_batch-rename-ctrl_select", "arguments": {"target": "…"}}
```

### `3d_render_select`

render #（1 项，如 Render ImageF12）。CLI：foxos 3d render select TARGET。界面：Render > menu > render #。效果：点击名称匹配的「render #」项（menuitem）。示例：foxos 3d render select 'Render ImageF12' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d render select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Render ImageF12' |

调用示例：

```json
{"name": "3d_render_select", "arguments": {"target": "…"}}
```

### `3d_render-animationctrl_select`

render animationctrl #（1 项，如 Render AnimationCtrl F12）。CLI：foxos 3d render-animationctrl select TARGET。界面：Render > menu > render animationctrl #。效果：点击名称匹配的「render animationctrl #」项（menuitem）。示例：foxos 3d render-animationctrl select 'Render AnimationCtrl F12' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d render-animationctrl select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Render AnimationCtrl F12' |

调用示例：

```json
{"name": "3d_render-animationctrl_select", "arguments": {"target": "…"}}
```

### `3d_view_show`

view #（1 项，如 View RenderF11）。CLI：foxos 3d view show TARGET。界面：Render > menu > view #。效果：点击名称匹配的「view #」项（menuitem）。示例：foxos 3d view show 'View RenderF11' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d view show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'View RenderF11' |

调用示例：

```json
{"name": "3d_view_show", "arguments": {"target": "…"}}
```

### `3d_animationctrl_show`

view animationctrl #（1 项，如 View AnimationCtrl F11）。CLI：foxos 3d animationctrl show TARGET。界面：Render > menu > view animationctrl #。效果：点击名称匹配的「view animationctrl #」项（menuitem）。示例：foxos 3d animationctrl show 'View AnimationCtrl F11' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d animationctrl show`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'View AnimationCtrl F11' |

调用示例：

```json
{"name": "3d_animationctrl_show", "arguments": {"target": "…"}}
```

### `3d_e-g-png_filter`

filter (e.g. *.png)（1 项，如 Filter (e.g. *.png)）。CLI：foxos 3d e-g-png filter TARGET。界面：Shading > main > filter (e.g. *.png)。效果：点击名称匹配的「filter (e.g. *.png)」项（textbox）。示例：foxos 3d e-g-png filter 'Filter (e.g. *.png)' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d e-g-png filter`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Filter (e.g. *.png)' |

调用示例：

```json
{"name": "3d_e-g-png_filter", "arguments": {"target": "…"}}
```

### `3d_slot-empty_select`

slot # (empty)（1 项，如 Slot 1 (empty)）。CLI：foxos 3d slot-empty select TARGET。界面：Rendering > main > slot # (empty)。效果：点击名称匹配的「slot # (empty)」项（button）。示例：foxos 3d slot-empty select 'Slot 1 (empty)' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d slot-empty select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 'Slot 1 (empty)' |

调用示例：

```json
{"name": "3d_slot-empty_select", "arguments": {"target": "…"}}
```

### `3d_fps_select`

# fps（1 项，如 24 fps）。CLI：foxos 3d fps select TARGET。界面：Compositing > main > # fps。效果：点击名称匹配的「# fps」项（button）。示例：foxos 3d fps select '24 fps' --json

只读：是 · 破坏性：否 · CLI：`foxos 3d fps select`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `target` | string | 是 | 要操作的项的名称（或其一部分），如 '24 fps' |

调用示例：

```json
{"name": "3d_fps_select", "arguments": {"target": "…"}}
```

### `3d_edit_update`

Edit。CLI：foxos 3d edit update。界面：主界面 > header > Edit。效果：点击「Edit」（button）。示例：foxos 3d edit update --json

只读：否 · 破坏性：否 · CLI：`foxos 3d edit update`

调用示例：

```json
{"name": "3d_edit_update", "arguments": {}}
```

### `3d_render_activate`

Render。CLI：foxos 3d render activate。界面：主界面 > header > Render。效果：点击「Render」（button）。示例：foxos 3d render activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render activate`

调用示例：

```json
{"name": "3d_render_activate", "arguments": {}}
```

### `3d_window_activate`

Window。CLI：foxos 3d window activate。界面：主界面 > header > Window。效果：点击「Window」（button）。示例：foxos 3d window activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window activate`

调用示例：

```json
{"name": "3d_window_activate", "arguments": {}}
```

### `3d_help_show`

Help。CLI：foxos 3d help show。界面：主界面 > header > Help。效果：点击「Help」（button），切换到该视图。示例：foxos 3d help show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d help show`

调用示例：

```json
{"name": "3d_help_show", "arguments": {}}
```

### `3d_layout_show`

Layout。CLI：foxos 3d layout show。界面：主界面 > tablist > Layout。效果：点击「Layout」（tab），切换到该视图。示例：foxos 3d layout show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d layout show`

调用示例：

```json
{"name": "3d_layout_show", "arguments": {}}
```

### `3d_modeling_show`

Modeling。CLI：foxos 3d modeling show。界面：主界面 > tablist > Modeling。效果：点击「Modeling」（tab），切换到该视图。示例：foxos 3d modeling show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d modeling show`

调用示例：

```json
{"name": "3d_modeling_show", "arguments": {}}
```

### `3d_sculpting_show`

Sculpting。CLI：foxos 3d sculpting show。界面：主界面 > tablist > Sculpting。效果：点击「Sculpting」（tab），切换到该视图。示例：foxos 3d sculpting show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d sculpting show`

调用示例：

```json
{"name": "3d_sculpting_show", "arguments": {}}
```

### `3d_uv-editing_show`

UV Editing。CLI：foxos 3d uv-editing show。界面：主界面 > tablist > UV Editing。效果：点击「UV Editing」（tab），切换到该视图。示例：foxos 3d uv-editing show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d uv-editing show`

调用示例：

```json
{"name": "3d_uv-editing_show", "arguments": {}}
```

### `3d_texture-paint_show`

Texture Paint。CLI：foxos 3d texture-paint show。界面：主界面 > tablist > Texture Paint。效果：点击「Texture Paint」（tab），切换到该视图。示例：foxos 3d texture-paint show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d texture-paint show`

调用示例：

```json
{"name": "3d_texture-paint_show", "arguments": {}}
```

### `3d_shading_show`

Shading。CLI：foxos 3d shading show。界面：主界面 > tablist > Shading。效果：点击「Shading」（tab），切换到该视图。示例：foxos 3d shading show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d shading show`

调用示例：

```json
{"name": "3d_shading_show", "arguments": {}}
```

### `3d_animation_show`

Animation。CLI：foxos 3d animation show。界面：主界面 > tablist > Animation。效果：点击「Animation」（tab），切换到该视图。示例：foxos 3d animation show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d animation show`

调用示例：

```json
{"name": "3d_animation_show", "arguments": {}}
```

### `3d_rendering_show`

Rendering。CLI：foxos 3d rendering show。界面：主界面 > tablist > Rendering。效果：点击「Rendering」（tab），切换到该视图。示例：foxos 3d rendering show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d rendering show`

调用示例：

```json
{"name": "3d_rendering_show", "arguments": {}}
```

### `3d_compositing_show`

Compositing。CLI：foxos 3d compositing show。界面：主界面 > tablist > Compositing。效果：点击「Compositing」（tab），切换到该视图。示例：foxos 3d compositing show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d compositing show`

调用示例：

```json
{"name": "3d_compositing_show", "arguments": {}}
```

### `3d_geometry-nodes_show`

Geometry Nodes。CLI：foxos 3d geometry-nodes show。界面：主界面 > tablist > Geometry Nodes。效果：点击「Geometry Nodes」（tab），切换到该视图。示例：foxos 3d geometry-nodes show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d geometry-nodes show`

调用示例：

```json
{"name": "3d_geometry-nodes_show", "arguments": {}}
```

### `3d_scripting_show`

Scripting。CLI：foxos 3d scripting show。界面：主界面 > tablist > Scripting。效果：点击「Scripting」（tab），切换到该视图。示例：foxos 3d scripting show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d scripting show`

调用示例：

```json
{"name": "3d_scripting_show", "arguments": {}}
```

### `3d_workspace_create`

Add Workspace。CLI：foxos 3d workspace create。界面：主界面 > Add Workspace。效果：点击「Add Workspace」（button）。示例：foxos 3d workspace create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d workspace create`

调用示例：

```json
{"name": "3d_workspace_create", "arguments": {}}
```

### `3d_assistant_activate`

Assistant。CLI：foxos 3d assistant activate。界面：主界面 > header > Assistant。效果：点击「Assistant」（button）。示例：foxos 3d assistant activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d assistant activate`

调用示例：

```json
{"name": "3d_assistant_activate", "arguments": {}}
```

### `3d_pin-scene-workspace_activate`

Pin Scene to Workspace。CLI：foxos 3d pin-scene-workspace activate。界面：主界面 > Pin Scene to Workspace。效果：点击「Pin Scene to Workspace」（button）。示例：foxos 3d pin-scene-workspace activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pin-scene-workspace activate`

调用示例：

```json
{"name": "3d_pin-scene-workspace_activate", "arguments": {}}
```

### `3d_scene_activate`

Scene。CLI：foxos 3d scene activate。界面：主界面 > Scene。效果：点击「Scene」（button）。示例：foxos 3d scene activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene activate`

调用示例：

```json
{"name": "3d_scene_activate", "arguments": {}}
```

### `3d_scene_set`

Scene。CLI：foxos 3d scene set VALUE [--submit]。界面：主界面 > header > Scene。效果：把「Scene」设为给定值（触发 input / change 事件）。示例：foxos 3d scene set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Scene」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_scene_set", "arguments": {"value": "…"}}
```

### `3d_scene_create`

New Scene。CLI：foxos 3d scene create。界面：主界面 > New Scene。效果：点击「New Scene」（button）。示例：foxos 3d scene create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scene create`

调用示例：

```json
{"name": "3d_scene_create", "arguments": {}}
```

### `3d_scene_delete`

Delete Scene。CLI：foxos 3d scene delete。界面：主界面 > Delete Scene。效果：点击「Delete Scene」（button）。示例：foxos 3d scene delete --json

只读：否 · 破坏性：是 · CLI：`foxos 3d scene delete`

调用示例：

```json
{"name": "3d_scene_delete", "arguments": {}}
```

### `3d_layer_show`

View Layer。CLI：foxos 3d layer show。界面：主界面 > View Layer。效果：点击「View Layer」（button），切换到该视图。示例：foxos 3d layer show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d layer show`

调用示例：

```json
{"name": "3d_layer_show", "arguments": {}}
```

### `3d_viewlayer_set`

ViewLayer。CLI：foxos 3d viewlayer set VALUE [--submit]。界面：主界面 > header > ViewLayer。效果：把「ViewLayer」设为给定值（触发 input / change 事件）。示例：foxos 3d viewlayer set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d viewlayer set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「ViewLayer」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_viewlayer_set", "arguments": {"value": "…"}}
```

### `3d_view-layer_create`

Add View Layer。CLI：foxos 3d view-layer create。界面：主界面 > Add View Layer。效果：点击「Add View Layer」（button）。示例：foxos 3d view-layer create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d view-layer create`

调用示例：

```json
{"name": "3d_view-layer_create", "arguments": {}}
```

### `3d_view-layer_delete`

Remove View Layer。CLI：foxos 3d view-layer delete。界面：主界面 > Remove View Layer。效果：点击「Remove View Layer」（button）。示例：foxos 3d view-layer delete --json

只读：否 · 破坏性：是 · CLI：`foxos 3d view-layer delete`

调用示例：

```json
{"name": "3d_view-layer_delete", "arguments": {}}
```

### `3d_object-mode_activate`

Object Mode。CLI：foxos 3d object-mode activate。界面：主界面 > main > Object Mode。效果：点击「Object Mode」（button）。示例：foxos 3d object-mode activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d object-mode activate`

调用示例：

```json
{"name": "3d_object-mode_activate", "arguments": {}}
```

### `3d_view-2_show`

View。CLI：foxos 3d view-2 show。界面：主界面 > main > View。效果：点击「View」（button），切换到该视图。示例：foxos 3d view-2 show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d view-2 show`

调用示例：

```json
{"name": "3d_view-2_show", "arguments": {}}
```

### `3d_select_select`

Select。CLI：foxos 3d select select。界面：主界面 > main > Select。效果：点击「Select」（button）。示例：foxos 3d select select --json

只读：是 · 破坏性：否 · CLI：`foxos 3d select select`

调用示例：

```json
{"name": "3d_select_select", "arguments": {}}
```

### `3d_add_create`

Add。CLI：foxos 3d add create。界面：主界面 > main > Add。效果：点击「Add」（button）。示例：foxos 3d add create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d add create`

调用示例：

```json
{"name": "3d_add_create", "arguments": {}}
```

### `3d_object_activate`

Object。CLI：foxos 3d object activate。界面：主界面 > main > Object。效果：点击「Object」（button）。示例：foxos 3d object activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d object activate`

调用示例：

```json
{"name": "3d_object_activate", "arguments": {}}
```

### `3d_global_activate`

Global。CLI：foxos 3d global activate。界面：主界面 > main > Global。效果：点击「Global」（button）。示例：foxos 3d global activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d global activate`

调用示例：

```json
{"name": "3d_global_activate", "arguments": {}}
```

### `3d_options_activate`

Options。CLI：foxos 3d options activate。界面：主界面 > main > Options。效果：点击「Options」（button）。示例：foxos 3d options activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d options activate`

调用示例：

```json
{"name": "3d_options_activate", "arguments": {}}
```

### `3d_marker_activate`

Marker。CLI：foxos 3d marker activate。界面：主界面 > main > Marker。效果：点击「Marker」（button）。示例：foxos 3d marker activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d marker activate`

调用示例：

```json
{"name": "3d_marker_activate", "arguments": {}}
```

### `3d_playback_activate`

Playback。CLI：foxos 3d playback activate。界面：主界面 > main > Playback。效果：点击「Playback」（button）。示例：foxos 3d playback activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d playback activate`

调用示例：

```json
{"name": "3d_playback_activate", "arguments": {}}
```

### `3d_search_set`

Search。CLI：foxos 3d search set VALUE [--submit]。界面：主界面 > main > Search。效果：把「Search」设为给定值（触发 input / change 事件）。示例：foxos 3d search set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d search set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Search」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_search_set", "arguments": {"value": "…"}}
```

### `3d_collapse_collapse`

Collapse。CLI：foxos 3d collapse collapse。界面：主界面 > Collapse。效果：点击「Collapse」（button）。示例：foxos 3d collapse collapse --json

只读：是 · 破坏性：否 · CLI：`foxos 3d collapse collapse`

调用示例：

```json
{"name": "3d_collapse_collapse", "arguments": {}}
```

### `3d_expand_expand`

Expand。CLI：foxos 3d expand expand。界面：主界面 > Expand。效果：点击「Expand」（button）。示例：foxos 3d expand expand --json

只读：是 · 破坏性：否 · CLI：`foxos 3d expand expand`

调用示例：

```json
{"name": "3d_expand_expand", "arguments": {}}
```

### `3d_menus_activate`

Menus。CLI：foxos 3d menus activate。界面：主界面 > Menus。效果：点击「Menus」（button）。示例：foxos 3d menus activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d menus activate`

调用示例：

```json
{"name": "3d_menus_activate", "arguments": {}}
```

### `3d_search-ctrl-f_set`

Search (Ctrl F)。CLI：foxos 3d search-ctrl-f set VALUE [--submit]。界面：主界面 > main > Search (Ctrl F)。效果：把「Search (Ctrl F)」设为给定值（触发 input / change 事件）。示例：foxos 3d search-ctrl-f set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d search-ctrl-f set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Search (Ctrl F)」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_search-ctrl-f_set", "arguments": {"value": "…"}}
```

### `3d_cube_set`

Cube。CLI：foxos 3d cube set VALUE [--submit]。界面：主界面 > main > Cube。效果：把「Cube」设为给定值（触发 input / change 事件）。示例：foxos 3d cube set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cube set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Cube」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_cube_set", "arguments": {"value": "…"}}
```

### `3d_location-x_lock`

Lock Location X。CLI：foxos 3d location-x lock。界面：主界面 > Lock Location X。效果：点击「Lock Location X」（button）。示例：foxos 3d location-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-x lock`

调用示例：

```json
{"name": "3d_location-x_lock", "arguments": {}}
```

### `3d_location-y_lock`

Lock Location Y。CLI：foxos 3d location-y lock。界面：主界面 > Lock Location Y。效果：点击「Lock Location Y」（button）。示例：foxos 3d location-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-y lock`

调用示例：

```json
{"name": "3d_location-y_lock", "arguments": {}}
```

### `3d_location-z_lock`

Lock Location Z。CLI：foxos 3d location-z lock。界面：主界面 > Lock Location Z。效果：点击「Lock Location Z」（button）。示例：foxos 3d location-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d location-z lock`

调用示例：

```json
{"name": "3d_location-z_lock", "arguments": {}}
```

### `3d_rotation-x_lock`

Lock Rotation X。CLI：foxos 3d rotation-x lock。界面：主界面 > Lock Rotation X。效果：点击「Lock Rotation X」（button）。示例：foxos 3d rotation-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-x lock`

调用示例：

```json
{"name": "3d_rotation-x_lock", "arguments": {}}
```

### `3d_rotation-y_lock`

Lock Rotation Y。CLI：foxos 3d rotation-y lock。界面：主界面 > Lock Rotation Y。效果：点击「Lock Rotation Y」（button）。示例：foxos 3d rotation-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-y lock`

调用示例：

```json
{"name": "3d_rotation-y_lock", "arguments": {}}
```

### `3d_rotation-z_lock`

Lock Rotation Z。CLI：foxos 3d rotation-z lock。界面：主界面 > Lock Rotation Z。效果：点击「Lock Rotation Z」（button）。示例：foxos 3d rotation-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotation-z lock`

调用示例：

```json
{"name": "3d_rotation-z_lock", "arguments": {}}
```

### `3d_xyz-euler_activate`

XYZ Euler。CLI：foxos 3d xyz-euler activate。界面：主界面 > main > XYZ Euler。效果：点击「XYZ Euler」（button）。示例：foxos 3d xyz-euler activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d xyz-euler activate`

调用示例：

```json
{"name": "3d_xyz-euler_activate", "arguments": {}}
```

### `3d_scale-x_lock`

Lock Scale X。CLI：foxos 3d scale-x lock。界面：主界面 > Lock Scale X。效果：点击「Lock Scale X」（button）。示例：foxos 3d scale-x lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-x lock`

调用示例：

```json
{"name": "3d_scale-x_lock", "arguments": {}}
```

### `3d_scale-y_lock`

Lock Scale Y。CLI：foxos 3d scale-y lock。界面：主界面 > Lock Scale Y。效果：点击「Lock Scale Y」（button）。示例：foxos 3d scale-y lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-y lock`

调用示例：

```json
{"name": "3d_scale-y_lock", "arguments": {}}
```

### `3d_scale-z_lock`

Lock Scale Z。CLI：foxos 3d scale-z lock。界面：主界面 > Lock Scale Z。效果：点击「Lock Scale Z」（button）。示例：foxos 3d scale-z lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scale-z lock`

调用示例：

```json
{"name": "3d_scale-z_lock", "arguments": {}}
```

### `3d_ai-model_set`

AI model。CLI：foxos 3d ai-model set VALUE [--submit]。界面：主界面 > AI model。效果：把「AI model」设为给定值（触发 input / change 事件）。示例：foxos 3d ai-model set claude-fable-5-1 --json

只读：否 · 破坏性：否 · CLI：`foxos 3d ai-model set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「AI model」的新值 可选：claude-fable-5-1 / claude-opus-5-5 / claude-sonnet-5-5 / claude-haiku-5-5 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_ai-model_set", "arguments": {"value": "claude-fable-5-1"}}
```

### `3d_chat_create`

New chat。CLI：foxos 3d chat create。界面：主界面 > New chat。效果：点击「New chat」（button）。示例：foxos 3d chat create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d chat create`

调用示例：

```json
{"name": "3d_chat_create", "arguments": {}}
```

### `3d_assistant_close`

Close the assistant。CLI：foxos 3d assistant close。界面：主界面 > Close the assistant。效果：点击「Close the assistant」（button）。示例：foxos 3d assistant close --json

只读：是 · 破坏性：否 · CLI：`foxos 3d assistant close`

调用示例：

```json
{"name": "3d_assistant_close", "arguments": {}}
```

### `3d_wooden-dining-table-four-chairs_activate`

A wooden dining table with four chairs。CLI：foxos 3d wooden-dining-table-four-chairs activate。界面：主界面 > Conversation > A wooden dining table with four chairs。效果：点击「A wooden dining table with four chairs」（button）。示例：foxos 3d wooden-dining-table-four-chairs activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d wooden-dining-table-four-chairs activate`

调用示例：

```json
{"name": "3d_wooden-dining-table-four-chairs_activate", "arguments": {}}
```

### `3d_snowman-carrot-nose-scarf_activate`

A snowman with a carrot nose and a scarf。CLI：foxos 3d snowman-carrot-nose-scarf activate。界面：主界面 > Conversation > A snowman with a carrot nose and a scarf。效果：点击「A snowman with a carrot nose and a scarf」（button）。示例：foxos 3d snowman-carrot-nose-scarf activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d snowman-carrot-nose-scarf activate`

调用示例：

```json
{"name": "3d_snowman-carrot-nose-scarf_activate", "arguments": {}}
```

### `3d_attach-files_activate`

Attach files。CLI：foxos 3d attach-files activate。界面：主界面 > Attach files。效果：点击「Attach files」（button）。示例：foxos 3d attach-files activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d attach-files activate`

调用示例：

```json
{"name": "3d_attach-files_activate", "arguments": {}}
```

### `3d_message-assistant_set`

Message the assistant。CLI：foxos 3d message-assistant set VALUE [--submit]。界面：主界面 > Message the assistant。效果：把「Message the assistant」设为给定值（触发 input / change 事件）。示例：foxos 3d message-assistant set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d message-assistant set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Message the assistant」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_message-assistant_set", "arguments": {"value": "…"}}
```

### `3d_send_send`

Send。CLI：foxos 3d send send。界面：主界面 > Send。效果：点击「Send」（button）。示例：foxos 3d send send --json

只读：否 · 破坏性：否 · CLI：`foxos 3d send send`

调用示例：

```json
{"name": "3d_send_send", "arguments": {}}
```

### `3d_default_activate`

Default。CLI：foxos 3d default activate。界面：主界面 > Welcome > Default。效果：点击「Default」（button）。示例：foxos 3d default activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d default activate`

调用示例：

```json
{"name": "3d_default_activate", "arguments": {}}
```

### `3d_graphite_activate`

Graphite。CLI：foxos 3d graphite activate。界面：主界面 > Welcome > Graphite。效果：点击「Graphite」（button）。示例：foxos 3d graphite activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d graphite activate`

调用示例：

```json
{"name": "3d_graphite_activate", "arguments": {}}
```

### `3d_midnight_activate`

Midnight。CLI：foxos 3d midnight activate。界面：主界面 > Welcome > Midnight。效果：点击「Midnight」（button）。示例：foxos 3d midnight activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d midnight activate`

调用示例：

```json
{"name": "3d_midnight_activate", "arguments": {}}
```

### `3d_light_activate`

Light。CLI：foxos 3d light activate。界面：主界面 > Welcome > Light。效果：点击「Light」（button）。示例：foxos 3d light activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d light activate`

调用示例：

```json
{"name": "3d_light_activate", "arguments": {}}
```

### `3d_high-contrast_activate`

High Contrast。CLI：foxos 3d high-contrast activate。界面：主界面 > Welcome > High Contrast。效果：点击「High Contrast」（button）。示例：foxos 3d high-contrast activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d high-contrast activate`

调用示例：

```json
{"name": "3d_high-contrast_activate", "arguments": {}}
```

### `3d_compact_activate`

Compact。CLI：foxos 3d compact activate。界面：主界面 > Welcome > Compact。效果：点击「Compact」（button）。示例：foxos 3d compact activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d compact activate`

调用示例：

```json
{"name": "3d_compact_activate", "arguments": {}}
```

### `3d_normal_activate`

Normal。CLI：foxos 3d normal activate。界面：主界面 > Welcome > Normal。效果：点击「Normal」（button）。示例：foxos 3d normal activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d normal activate`

调用示例：

```json
{"name": "3d_normal_activate", "arguments": {}}
```

### `3d_large_activate`

Large。CLI：foxos 3d large activate。界面：主界面 > Welcome > Large。效果：点击「Large」（button）。示例：foxos 3d large activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d large activate`

调用示例：

```json
{"name": "3d_large_activate", "arguments": {}}
```

### `3d_larger_activate`

Larger。CLI：foxos 3d larger activate。界面：主界面 > Welcome > Larger。效果：点击「Larger」（button）。示例：foxos 3d larger activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d larger activate`

调用示例：

```json
{"name": "3d_larger_activate", "arguments": {}}
```

### `3d_play_play`

Play。CLI：foxos 3d play play。界面：主界面 > Welcome > Play。效果：点击「Play」（button）。示例：foxos 3d play play --json

只读：否 · 破坏性：否 · CLI：`foxos 3d play play`

调用示例：

```json
{"name": "3d_play_play", "arguments": {}}
```

### `3d_tools_activate`

Tools。CLI：foxos 3d tools activate。界面：主界面 > Welcome > Tools。效果：点击「Tools」（button）。示例：foxos 3d tools activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d tools activate`

调用示例：

```json
{"name": "3d_tools_activate", "arguments": {}}
```

### `3d_search_search`

Search。CLI：foxos 3d search search。界面：主界面 > Welcome > Search。效果：点击「Search」（button）。示例：foxos 3d search search --json

只读：是 · 破坏性：否 · CLI：`foxos 3d search search`

调用示例：

```json
{"name": "3d_search_search", "arguments": {}}
```

### `3d_continue_activate`

Continue。CLI：foxos 3d continue activate。界面：主界面 > Welcome > Continue。效果：点击「Continue」（button）。示例：foxos 3d continue activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d continue activate`

调用示例：

```json
{"name": "3d_continue_activate", "arguments": {}}
```

### `3d_newctrl-n_activate`

NewCtrl N。CLI：foxos 3d newctrl-n activate。界面：File > menu > NewCtrl N。效果：点击「NewCtrl N」（menuitem）。示例：foxos 3d newctrl-n activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d newctrl-n activate`

调用示例：

```json
{"name": "3d_newctrl-n_activate", "arguments": {}}
```

### `3d_ctrl-o_open`

Open…Ctrl O。CLI：foxos 3d ctrl-o open。界面：File > menu > Open…Ctrl O。效果：点击「Open…Ctrl O」（menuitem）。示例：foxos 3d ctrl-o open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d ctrl-o open`

调用示例：

```json
{"name": "3d_ctrl-o_open", "arguments": {}}
```

### `3d_recentshift-ctrl-o_open`

Open RecentShift Ctrl O。CLI：foxos 3d recentshift-ctrl-o open。界面：File > menu > Open RecentShift Ctrl O。效果：点击「Open RecentShift Ctrl O」（menuitem）。示例：foxos 3d recentshift-ctrl-o open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d recentshift-ctrl-o open`

调用示例：

```json
{"name": "3d_recentshift-ctrl-o_open", "arguments": {}}
```

### `3d_revert_activate`

Revert。CLI：foxos 3d revert activate。界面：File > menu > Revert。效果：点击「Revert」（menuitem）。示例：foxos 3d revert activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d revert activate`

调用示例：

```json
{"name": "3d_revert_activate", "arguments": {}}
```

### `3d_recover_activate`

Recover。CLI：foxos 3d recover activate。界面：File > menu > Recover。效果：点击「Recover」（menuitem）。示例：foxos 3d recover activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d recover activate`

调用示例：

```json
{"name": "3d_recover_activate", "arguments": {}}
```

### `3d_savectrl-s_activate`

SaveCtrl S。CLI：foxos 3d savectrl-s activate。界面：File > menu > SaveCtrl S。效果：点击「SaveCtrl S」（menuitem）。示例：foxos 3d savectrl-s activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d savectrl-s activate`

调用示例：

```json
{"name": "3d_savectrl-s_activate", "arguments": {}}
```

### `3d_as-shift-ctrl-s_save`

Save As…Shift Ctrl S。CLI：foxos 3d as-shift-ctrl-s save。界面：File > menu > Save As…Shift Ctrl S。效果：点击「Save As…Shift Ctrl S」（menuitem）。示例：foxos 3d as-shift-ctrl-s save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d as-shift-ctrl-s save`

调用示例：

```json
{"name": "3d_as-shift-ctrl-s_save", "arguments": {}}
```

### `3d_copy_save`

Save Copy…。CLI：foxos 3d copy save。界面：File > menu > Save Copy…。效果：点击「Save Copy…」（menuitem）。示例：foxos 3d copy save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d copy save`

调用示例：

```json
{"name": "3d_copy_save", "arguments": {}}
```

### `3d_incrementalctrl-alt-s_save`

Save IncrementalCtrl Alt S。CLI：foxos 3d incrementalctrl-alt-s save。界面：File > menu > Save IncrementalCtrl Alt S。效果：点击「Save IncrementalCtrl Alt S」（menuitem）。示例：foxos 3d incrementalctrl-alt-s save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d incrementalctrl-alt-s save`

调用示例：

```json
{"name": "3d_incrementalctrl-alt-s_save", "arguments": {}}
```

### `3d_link_activate`

Link…。CLI：foxos 3d link activate。界面：File > menu > Link…。效果：点击「Link…」（menuitem）。示例：foxos 3d link activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d link activate`

调用示例：

```json
{"name": "3d_link_activate", "arguments": {}}
```

### `3d_append_activate`

Append…。CLI：foxos 3d append activate。界面：File > menu > Append…。效果：点击「Append…」（menuitem）。示例：foxos 3d append activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d append activate`

调用示例：

```json
{"name": "3d_append_activate", "arguments": {}}
```

### `3d_data-previews_activate`

Data Previews。CLI：foxos 3d data-previews activate。界面：File > menu > Data Previews。效果：点击「Data Previews」（menuitem）。示例：foxos 3d data-previews activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d data-previews activate`

调用示例：

```json
{"name": "3d_data-previews_activate", "arguments": {}}
```

### `3d_import_import`

Import。CLI：foxos 3d import import。界面：File > menu > Import。效果：点击「Import」（menuitem）。示例：foxos 3d import import --json

只读：否 · 破坏性：否 · CLI：`foxos 3d import import`

调用示例：

```json
{"name": "3d_import_import", "arguments": {}}
```

### `3d_export_export`

Export。CLI：foxos 3d export export。界面：File > menu > Export。效果：点击「Export」（menuitem）。示例：foxos 3d export export --json

只读：否 · 破坏性：否 · CLI：`foxos 3d export export`

调用示例：

```json
{"name": "3d_export_export", "arguments": {}}
```

### `3d_collections_export`

Export All Collections。CLI：foxos 3d collections export。界面：File > menu > Export All Collections。效果：点击「Export All Collections」（menuitem）。示例：foxos 3d collections export --json

只读：否 · 破坏性：否 · CLI：`foxos 3d collections export`

调用示例：

```json
{"name": "3d_collections_export", "arguments": {}}
```

### `3d_external-data_activate`

External Data。CLI：foxos 3d external-data activate。界面：File > menu > External Data。效果：点击「External Data」（menuitem）。示例：foxos 3d external-data activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d external-data activate`

调用示例：

```json
{"name": "3d_external-data_activate", "arguments": {}}
```

### `3d_clean-up_activate`

Clean Up。CLI：foxos 3d clean-up activate。界面：File > menu > Clean Up。效果：点击「Clean Up」（menuitem）。示例：foxos 3d clean-up activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clean-up activate`

调用示例：

```json
{"name": "3d_clean-up_activate", "arguments": {}}
```

### `3d_defaults_activate`

Defaults。CLI：foxos 3d defaults activate。界面：File > menu > Defaults。效果：点击「Defaults」（menuitem）。示例：foxos 3d defaults activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d defaults activate`

调用示例：

```json
{"name": "3d_defaults_activate", "arguments": {}}
```

### `3d_quitctrl-q_activate`

QuitCtrl Q。CLI：foxos 3d quitctrl-q activate。界面：File > menu > QuitCtrl Q。效果：点击「QuitCtrl Q」（menuitem）。示例：foxos 3d quitctrl-q activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d quitctrl-q activate`

调用示例：

```json
{"name": "3d_quitctrl-q_activate", "arguments": {}}
```

### `3d_undoctrl-z_activate`

UndoCtrl Z。CLI：foxos 3d undoctrl-z activate。界面：Edit > menu > UndoCtrl Z。效果：点击「UndoCtrl Z」（menuitem）。示例：foxos 3d undoctrl-z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d undoctrl-z activate`

调用示例：

```json
{"name": "3d_undoctrl-z_activate", "arguments": {}}
```

### `3d_redoshift-ctrl-z_activate`

RedoShift Ctrl Z。CLI：foxos 3d redoshift-ctrl-z activate。界面：Edit > menu > RedoShift Ctrl Z。效果：点击「RedoShift Ctrl Z」（menuitem）。示例：foxos 3d redoshift-ctrl-z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d redoshift-ctrl-z activate`

调用示例：

```json
{"name": "3d_redoshift-ctrl-z_activate", "arguments": {}}
```

### `3d_historyctrl-alt-z_undo`

Undo HistoryCtrl Alt Z。CLI：foxos 3d historyctrl-alt-z undo。界面：Edit > menu > Undo HistoryCtrl Alt Z。效果：点击「Undo HistoryCtrl Alt Z」（menuitem）。示例：foxos 3d historyctrl-alt-z undo --json

只读：否 · 破坏性：否 · CLI：`foxos 3d historyctrl-alt-z undo`

调用示例：

```json
{"name": "3d_historyctrl-alt-z_undo", "arguments": {}}
```

### `3d_repeat-lastshift-r_activate`

Repeat LastShift R。CLI：foxos 3d repeat-lastshift-r activate。界面：Edit > menu > Repeat LastShift R。效果：点击「Repeat LastShift R」（menuitem）。示例：foxos 3d repeat-lastshift-r activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d repeat-lastshift-r activate`

调用示例：

```json
{"name": "3d_repeat-lastshift-r_activate", "arguments": {}}
```

### `3d_repeat-history_activate`

Repeat History…。CLI：foxos 3d repeat-history activate。界面：Edit > menu > Repeat History…。效果：点击「Repeat History…」（menuitem）。示例：foxos 3d repeat-history activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d repeat-history activate`

调用示例：

```json
{"name": "3d_repeat-history_activate", "arguments": {}}
```

### `3d_preferences-ctrl_activate`

Preferences…Ctrl ,。CLI：foxos 3d preferences-ctrl activate。界面：Edit > menu > Preferences…Ctrl ,。效果：点击「Preferences…Ctrl ,」（menuitem）。示例：foxos 3d preferences-ctrl activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d preferences-ctrl activate`

调用示例：

```json
{"name": "3d_preferences-ctrl_activate", "arguments": {}}
```

### `3d_render-audio_activate`

Render Audio…。CLI：foxos 3d render-audio activate。界面：Render > menu > Render Audio…。效果：点击「Render Audio…」（menuitem）。示例：foxos 3d render-audio activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render-audio activate`

调用示例：

```json
{"name": "3d_render-audio_activate", "arguments": {}}
```

### `3d_interface_lock`

Lock Interface。CLI：foxos 3d interface lock。界面：Render > menu > Lock Interface。效果：点击「Lock Interface」（menuitem）。示例：foxos 3d interface lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d interface lock`

调用示例：

```json
{"name": "3d_interface_lock", "arguments": {}}
```

### `3d_window_create`

New Window。CLI：foxos 3d window create。界面：Window > menu > New Window。效果：点击「New Window」（menuitem）。示例：foxos 3d window create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window create`

调用示例：

```json
{"name": "3d_window_create", "arguments": {}}
```

### `3d_main-window_create`

New Main Window。CLI：foxos 3d main-window create。界面：Window > menu > New Main Window。效果：点击「New Main Window」（menuitem）。示例：foxos 3d main-window create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d main-window create`

调用示例：

```json
{"name": "3d_main-window_create", "arguments": {}}
```

### `3d_window-fullscreen_toggle`

Toggle Window Fullscreen。CLI：foxos 3d window-fullscreen toggle。界面：Window > menu > Toggle Window Fullscreen。效果：切换「Toggle Window Fullscreen」。示例：foxos 3d window-fullscreen toggle --json

只读：否 · 破坏性：否 · CLI：`foxos 3d window-fullscreen toggle`

调用示例：

```json
{"name": "3d_window-fullscreen_toggle", "arguments": {}}
```

### `3d_workspacectrl-page-down_next`

Next WorkspaceCtrl Page Down。CLI：foxos 3d workspacectrl-page-down next。界面：Window > menu > Next WorkspaceCtrl Page Down。效果：点击「Next WorkspaceCtrl Page Down」（menuitem）。示例：foxos 3d workspacectrl-page-down next --json

只读：是 · 破坏性：否 · CLI：`foxos 3d workspacectrl-page-down next`

调用示例：

```json
{"name": "3d_workspacectrl-page-down_next", "arguments": {}}
```

### `3d_workspacectrl-page-up_previous`

Previous WorkspaceCtrl Page Up。CLI：foxos 3d workspacectrl-page-up previous。界面：Window > menu > Previous WorkspaceCtrl Page Up。效果：点击「Previous WorkspaceCtrl Page Up」（menuitem）。示例：foxos 3d workspacectrl-page-up previous --json

只读：是 · 破坏性：否 · CLI：`foxos 3d workspacectrl-page-up previous`

调用示例：

```json
{"name": "3d_workspacectrl-page-up_previous", "arguments": {}}
```

### `3d_status-bar_show`

Show Status Bar。CLI：foxos 3d status-bar show。界面：Window > menu > Show Status Bar。效果：点击「Show Status Bar」（menuitem），切换到该视图。示例：foxos 3d status-bar show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d status-bar show`

调用示例：

```json
{"name": "3d_status-bar_show", "arguments": {}}
```

### `3d_status-bar-scene-statistics_activate`

Status Bar Scene Statistics。CLI：foxos 3d status-bar-scene-statistics activate。界面：Window > menu > Status Bar Scene Statistics。效果：点击「Status Bar Scene Statistics」（menuitem）。示例：foxos 3d status-bar-scene-statistics activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d status-bar-scene-statistics activate`

调用示例：

```json
{"name": "3d_status-bar-scene-statistics_activate", "arguments": {}}
```

### `3d_ai-assistant_activate`

AI Assistant。CLI：foxos 3d ai-assistant activate。界面：Window > menu > AI Assistant。效果：点击「AI Assistant」（menuitem）。示例：foxos 3d ai-assistant activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d ai-assistant activate`

调用示例：

```json
{"name": "3d_ai-assistant_activate", "arguments": {}}
```

### `3d_screenshot_save`

Save Screenshot。CLI：foxos 3d screenshot save。界面：Window > menu > Save Screenshot。效果：点击「Save Screenshot」（menuitem）。示例：foxos 3d screenshot save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d screenshot save`

调用示例：

```json
{"name": "3d_screenshot_save", "arguments": {}}
```

### `3d_screenshot-editor_save`

Save Screenshot (Editor)。CLI：foxos 3d screenshot-editor save。界面：Window > menu > Save Screenshot (Editor)。效果：点击「Save Screenshot (Editor)」（menuitem）。示例：foxos 3d screenshot-editor save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d screenshot-editor save`

调用示例：

```json
{"name": "3d_screenshot-editor_save", "arguments": {}}
```

### `3d_keyboard-shortcuts_activate`

Keyboard Shortcuts。CLI：foxos 3d keyboard-shortcuts activate。界面：Help > menu > Keyboard Shortcuts。效果：点击「Keyboard Shortcuts」（menuitem）。示例：foxos 3d keyboard-shortcuts activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d keyboard-shortcuts activate`

调用示例：

```json
{"name": "3d_keyboard-shortcuts_activate", "arguments": {}}
```

### `3d_report-bug_activate`

Report a Bug。CLI：foxos 3d report-bug activate。界面：Help > menu > Report a Bug。效果：点击「Report a Bug」（menuitem）。示例：foxos 3d report-bug activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d report-bug activate`

调用示例：

```json
{"name": "3d_report-bug_activate", "arguments": {}}
```

### `3d_system-info_save`

Save System Info。CLI：foxos 3d system-info save。界面：Help > menu > Save System Info。效果：点击「Save System Info」（menuitem）。示例：foxos 3d system-info save --json

只读：否 · 破坏性：否 · CLI：`foxos 3d system-info save`

调用示例：

```json
{"name": "3d_system-info_save", "arguments": {}}
```

### `3d_about_show`

About。CLI：foxos 3d about show。界面：Help > menu > About。效果：点击「About」（menuitem），切换到该视图。示例：foxos 3d about show --json

只读：是 · 破坏性：否 · CLI：`foxos 3d about show`

调用示例：

```json
{"name": "3d_about_show", "arguments": {}}
```

### `3d_mode_update`

Edit Mode。CLI：foxos 3d mode update。界面：Modeling > main > Edit Mode。效果：点击「Edit Mode」（button）。示例：foxos 3d mode update --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mode update`

调用示例：

```json
{"name": "3d_mode_update", "arguments": {}}
```

### `3d_x_activate`

X。CLI：foxos 3d x activate。界面：Modeling > main > X。效果：点击「X」（button）。示例：foxos 3d x activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d x activate`

调用示例：

```json
{"name": "3d_x_activate", "arguments": {}}
```

### `3d_y_activate`

Y。CLI：foxos 3d y activate。界面：Modeling > main > Y。效果：点击「Y」（button）。示例：foxos 3d y activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d y activate`

调用示例：

```json
{"name": "3d_y_activate", "arguments": {}}
```

### `3d_z_activate`

Z。CLI：foxos 3d z activate。界面：Modeling > main > Z。效果：点击「Z」（button）。示例：foxos 3d z activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d z activate`

调用示例：

```json
{"name": "3d_z_activate", "arguments": {}}
```

### `3d_modifier_create`

Add Modifier。CLI：foxos 3d modifier create。界面：Modeling > main > Add Modifier。效果：点击「Add Modifier」（button）。示例：foxos 3d modifier create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d modifier create`

调用示例：

```json
{"name": "3d_modifier_create", "arguments": {}}
```

### `3d_sculpt-mode_activate`

Sculpt Mode。CLI：foxos 3d sculpt-mode activate。界面：Sculpting > main > Sculpt Mode。效果：点击「Sculpt Mode」（button）。示例：foxos 3d sculpt-mode activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpt-mode activate`

调用示例：

```json
{"name": "3d_sculpt-mode_activate", "arguments": {}}
```

### `3d_sculpt_activate`

Sculpt。CLI：foxos 3d sculpt activate。界面：Sculpting > main > Sculpt。效果：点击「Sculpt」（button）。示例：foxos 3d sculpt activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpt activate`

调用示例：

```json
{"name": "3d_sculpt_activate", "arguments": {}}
```

### `3d_mask_activate`

Mask。CLI：foxos 3d mask activate。界面：Sculpting > main > Mask。效果：点击「Mask」（button）。示例：foxos 3d mask activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mask activate`

调用示例：

```json
{"name": "3d_mask_activate", "arguments": {}}
```

### `3d_face-sets_activate`

Face Sets。CLI：foxos 3d face-sets activate。界面：Sculpting > main > Face Sets。效果：点击「Face Sets」（button）。示例：foxos 3d face-sets activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d face-sets activate`

调用示例：

```json
{"name": "3d_face-sets_activate", "arguments": {}}
```

### `3d_brush_activate`

Brush。CLI：foxos 3d brush activate。界面：Sculpting > main > Brush。效果：点击「Brush」（button）。示例：foxos 3d brush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d brush activate`

调用示例：

```json
{"name": "3d_brush_activate", "arguments": {}}
```

### `3d_texture_activate`

Texture。CLI：foxos 3d texture activate。界面：Sculpting > main > Texture。效果：点击「Texture」（button）。示例：foxos 3d texture activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d texture activate`

调用示例：

```json
{"name": "3d_texture_activate", "arguments": {}}
```

### `3d_stroke_activate`

Stroke。CLI：foxos 3d stroke activate。界面：Sculpting > main > Stroke。效果：点击「Stroke」（button）。示例：foxos 3d stroke activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d stroke activate`

调用示例：

```json
{"name": "3d_stroke_activate", "arguments": {}}
```

### `3d_falloff_activate`

Falloff。CLI：foxos 3d falloff activate。界面：Sculpting > main > Falloff。效果：点击「Falloff」（button）。示例：foxos 3d falloff activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d falloff activate`

调用示例：

```json
{"name": "3d_falloff_activate", "arguments": {}}
```

### `3d_cursor_activate`

Cursor。CLI：foxos 3d cursor activate。界面：Sculpting > main > Cursor。效果：点击「Cursor」（button）。示例：foxos 3d cursor activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cursor activate`

调用示例：

```json
{"name": "3d_cursor_activate", "arguments": {}}
```

### `3d_remesh_activate`

Remesh。CLI：foxos 3d remesh activate。界面：Sculpting > main > Remesh。效果：点击「Remesh」（button）。示例：foxos 3d remesh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d remesh activate`

调用示例：

```json
{"name": "3d_remesh_activate", "arguments": {}}
```

### `3d_subtract_create`

Add/Subtract。CLI：foxos 3d subtract create。界面：Sculpting > main > Add/Subtract。效果：点击「Add/Subtract」（button）。示例：foxos 3d subtract create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d subtract create`

调用示例：

```json
{"name": "3d_subtract_create", "arguments": {}}
```

### `3d_contrast-smooth_activate`

Contrast & Smooth。CLI：foxos 3d contrast-smooth activate。界面：Sculpting > main > Contrast & Smooth。效果：点击「Contrast & Smooth」（button）。示例：foxos 3d contrast-smooth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d contrast-smooth activate`

调用示例：

```json
{"name": "3d_contrast-smooth_activate", "arguments": {}}
```

### `3d_transform_activate`

Transform。CLI：foxos 3d transform activate。界面：Sculpting > main > Transform。效果：点击「Transform」（button）。示例：foxos 3d transform activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d transform activate`

调用示例：

```json
{"name": "3d_transform_activate", "arguments": {}}
```

### `3d_simplify_activate`

Simplify。CLI：foxos 3d simplify activate。界面：Sculpting > main > Simplify。效果：点击「Simplify」（button）。示例：foxos 3d simplify activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d simplify activate`

调用示例：

```json
{"name": "3d_simplify_activate", "arguments": {}}
```

### `3d_utilities_activate`

Utilities。CLI：foxos 3d utilities activate。界面：Sculpting > main > Utilities。效果：点击「Utilities」（button）。示例：foxos 3d utilities activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d utilities activate`

调用示例：

```json
{"name": "3d_utilities_activate", "arguments": {}}
```

### `3d_paint_activate`

Paint。CLI：foxos 3d paint activate。界面：Sculpting > main > Paint。效果：点击「Paint」（button）。示例：foxos 3d paint activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d paint activate`

调用示例：

```json
{"name": "3d_paint_activate", "arguments": {}}
```

### `3d_assets_activate`

Assets。CLI：foxos 3d assets activate。界面：Sculpting > main > Assets。效果：点击「Assets」（button）。示例：foxos 3d assets activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d assets activate`

调用示例：

```json
{"name": "3d_assets_activate", "arguments": {}}
```

### `3d_draw_draw`

Draw。CLI：foxos 3d draw draw。界面：Sculpting > main > Draw。效果：点击「Draw」（button）。示例：foxos 3d draw draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d draw draw`

调用示例：

```json
{"name": "3d_draw_draw", "arguments": {}}
```

### `3d_sharp_draw`

Draw Sharp。CLI：foxos 3d sharp draw。界面：Sculpting > main > Draw Sharp。效果：点击「Draw Sharp」（button）。示例：foxos 3d sharp draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sharp draw`

调用示例：

```json
{"name": "3d_sharp_draw", "arguments": {}}
```

### `3d_clay_activate`

Clay。CLI：foxos 3d clay activate。界面：Sculpting > main > Clay。效果：点击「Clay」（button）。示例：foxos 3d clay activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay activate`

调用示例：

```json
{"name": "3d_clay_activate", "arguments": {}}
```

### `3d_clay-strips_activate`

Clay Strips。CLI：foxos 3d clay-strips activate。界面：Sculpting > main > Clay Strips。效果：点击「Clay Strips」（button）。示例：foxos 3d clay-strips activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay-strips activate`

调用示例：

```json
{"name": "3d_clay-strips_activate", "arguments": {}}
```

### `3d_clay-thumb_activate`

Clay Thumb。CLI：foxos 3d clay-thumb activate。界面：Sculpting > main > Clay Thumb。效果：点击「Clay Thumb」（button）。示例：foxos 3d clay-thumb activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clay-thumb activate`

调用示例：

```json
{"name": "3d_clay-thumb_activate", "arguments": {}}
```

### `3d_layer_activate`

Layer。CLI：foxos 3d layer activate。界面：Sculpting > main > Layer。效果：点击「Layer」（button）。示例：foxos 3d layer activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d layer activate`

调用示例：

```json
{"name": "3d_layer_activate", "arguments": {}}
```

### `3d_inflate-deflate_activate`

Inflate/Deflate。CLI：foxos 3d inflate-deflate activate。界面：Sculpting > main > Inflate/Deflate。效果：点击「Inflate/Deflate」（button）。示例：foxos 3d inflate-deflate activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d inflate-deflate activate`

调用示例：

```json
{"name": "3d_inflate-deflate_activate", "arguments": {}}
```

### `3d_blob_activate`

Blob。CLI：foxos 3d blob activate。界面：Sculpting > main > Blob。效果：点击「Blob」（button）。示例：foxos 3d blob activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d blob activate`

调用示例：

```json
{"name": "3d_blob_activate", "arguments": {}}
```

### `3d_crease_activate`

Crease。CLI：foxos 3d crease activate。界面：Sculpting > main > Crease。效果：点击「Crease」（button）。示例：foxos 3d crease activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d crease activate`

调用示例：

```json
{"name": "3d_crease_activate", "arguments": {}}
```

### `3d_smooth_activate`

Smooth。CLI：foxos 3d smooth activate。界面：Sculpting > main > Smooth。效果：点击「Smooth」（button）。示例：foxos 3d smooth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d smooth activate`

调用示例：

```json
{"name": "3d_smooth_activate", "arguments": {}}
```

### `3d_flatten-contrast_activate`

Flatten/Contrast。CLI：foxos 3d flatten-contrast activate。界面：Sculpting > main > Flatten/Contrast。效果：点击「Flatten/Contrast」（button）。示例：foxos 3d flatten-contrast activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d flatten-contrast activate`

调用示例：

```json
{"name": "3d_flatten-contrast_activate", "arguments": {}}
```

### `3d_fill-deepen_activate`

Fill/Deepen。CLI：foxos 3d fill-deepen activate。界面：Sculpting > main > Fill/Deepen。效果：点击「Fill/Deepen」（button）。示例：foxos 3d fill-deepen activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d fill-deepen activate`

调用示例：

```json
{"name": "3d_fill-deepen_activate", "arguments": {}}
```

### `3d_scrape-peaks_activate`

Scrape/Peaks。CLI：foxos 3d scrape-peaks activate。界面：Sculpting > main > Scrape/Peaks。效果：点击「Scrape/Peaks」（button）。示例：foxos 3d scrape-peaks activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scrape-peaks activate`

调用示例：

```json
{"name": "3d_scrape-peaks_activate", "arguments": {}}
```

### `3d_multiplane-scrape_activate`

Multiplane Scrape。CLI：foxos 3d multiplane-scrape activate。界面：Sculpting > main > Multiplane Scrape。效果：点击「Multiplane Scrape」（button）。示例：foxos 3d multiplane-scrape activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d multiplane-scrape activate`

调用示例：

```json
{"name": "3d_multiplane-scrape_activate", "arguments": {}}
```

### `3d_pinch-magnify_activate`

Pinch/Magnify。CLI：foxos 3d pinch-magnify activate。界面：Sculpting > main > Pinch/Magnify。效果：点击「Pinch/Magnify」（button）。示例：foxos 3d pinch-magnify activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pinch-magnify activate`

调用示例：

```json
{"name": "3d_pinch-magnify_activate", "arguments": {}}
```

### `3d_grab_activate`

Grab。CLI：foxos 3d grab activate。界面：Sculpting > main > Grab。效果：点击「Grab」（button）。示例：foxos 3d grab activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d grab activate`

调用示例：

```json
{"name": "3d_grab_activate", "arguments": {}}
```

### `3d_elastic-deform_activate`

Elastic Deform。CLI：foxos 3d elastic-deform activate。界面：Sculpting > main > Elastic Deform。效果：点击「Elastic Deform」（button）。示例：foxos 3d elastic-deform activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d elastic-deform activate`

调用示例：

```json
{"name": "3d_elastic-deform_activate", "arguments": {}}
```

### `3d_snake-hook_activate`

Snake Hook。CLI：foxos 3d snake-hook activate。界面：Sculpting > main > Snake Hook。效果：点击「Snake Hook」（button）。示例：foxos 3d snake-hook activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d snake-hook activate`

调用示例：

```json
{"name": "3d_snake-hook_activate", "arguments": {}}
```

### `3d_thumb_activate`

Thumb。CLI：foxos 3d thumb activate。界面：Sculpting > main > Thumb。效果：点击「Thumb」（button）。示例：foxos 3d thumb activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d thumb activate`

调用示例：

```json
{"name": "3d_thumb_activate", "arguments": {}}
```

### `3d_pose_activate`

Pose。CLI：foxos 3d pose activate。界面：Sculpting > main > Pose。效果：点击「Pose」（button）。示例：foxos 3d pose activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pose activate`

调用示例：

```json
{"name": "3d_pose_activate", "arguments": {}}
```

### `3d_nudge_activate`

Nudge。CLI：foxos 3d nudge activate。界面：Sculpting > main > Nudge。效果：点击「Nudge」（button）。示例：foxos 3d nudge activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d nudge activate`

调用示例：

```json
{"name": "3d_nudge_activate", "arguments": {}}
```

### `3d_rotate_rotate`

Rotate。CLI：foxos 3d rotate rotate。界面：Sculpting > main > Rotate。效果：点击「Rotate」（button）。示例：foxos 3d rotate rotate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rotate rotate`

调用示例：

```json
{"name": "3d_rotate_rotate", "arguments": {}}
```

### `3d_boundary_activate`

Boundary。CLI：foxos 3d boundary activate。界面：Sculpting > main > Boundary。效果：点击「Boundary」（button）。示例：foxos 3d boundary activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d boundary activate`

调用示例：

```json
{"name": "3d_boundary_activate", "arguments": {}}
```

### `3d_cloth_activate`

Cloth。CLI：foxos 3d cloth activate。界面：Sculpting > main > Cloth。效果：点击「Cloth」（button）。示例：foxos 3d cloth activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d cloth activate`

调用示例：

```json
{"name": "3d_cloth_activate", "arguments": {}}
```

### `3d_slide-relax_activate`

Slide Relax。CLI：foxos 3d slide-relax activate。界面：Sculpting > main > Slide Relax。效果：点击「Slide Relax」（button）。示例：foxos 3d slide-relax activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d slide-relax activate`

调用示例：

```json
{"name": "3d_slide-relax_activate", "arguments": {}}
```

### `3d_face-sets_draw`

Draw Face Sets。CLI：foxos 3d face-sets draw。界面：Sculpting > main > Draw Face Sets。效果：点击「Draw Face Sets」（button）。示例：foxos 3d face-sets draw --json

只读：否 · 破坏性：否 · CLI：`foxos 3d face-sets draw`

调用示例：

```json
{"name": "3d_face-sets_draw", "arguments": {}}
```

### `3d_smear_activate`

Smear。CLI：foxos 3d smear activate。界面：Sculpting > main > Smear。效果：点击「Smear」（button）。示例：foxos 3d smear activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d smear activate`

调用示例：

```json
{"name": "3d_smear_activate", "arguments": {}}
```

### `3d_crisp-crease_activate`

Crisp Crease。CLI：foxos 3d crisp-crease activate。界面：Sculpting > main > Crisp Crease。效果：点击「Crisp Crease」（button）。示例：foxos 3d crisp-crease activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d crisp-crease activate`

调用示例：

```json
{"name": "3d_crisp-crease_activate", "arguments": {}}
```

### `3d_noise-detail_activate`

Noise Detail。CLI：foxos 3d noise-detail activate。界面：Sculpting > main > Noise Detail。效果：点击「Noise Detail」（button）。示例：foxos 3d noise-detail activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d noise-detail activate`

调用示例：

```json
{"name": "3d_noise-detail_activate", "arguments": {}}
```

### `3d_soft-clay_activate`

Soft Clay。CLI：foxos 3d soft-clay activate。界面：Sculpting > main > Soft Clay。效果：点击「Soft Clay」（button）。示例：foxos 3d soft-clay activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d soft-clay activate`

调用示例：

```json
{"name": "3d_soft-clay_activate", "arguments": {}}
```

### `3d_steady-line_activate`

Steady Line。CLI：foxos 3d steady-line activate。界面：Sculpting > main > Steady Line。效果：点击「Steady Line」（button）。示例：foxos 3d steady-line activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d steady-line activate`

调用示例：

```json
{"name": "3d_steady-line_activate", "arguments": {}}
```

### `3d_sculpting-scene_activate`

Scene。CLI：foxos 3d sculpting-scene activate。界面：Sculpting > main > Scene。效果：点击「Scene」（button）。示例：foxos 3d sculpting-scene activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d sculpting-scene activate`

调用示例：

```json
{"name": "3d_sculpting-scene_activate", "arguments": {}}
```

### `3d_voxel-remesh_activate`

Voxel Remesh。CLI：foxos 3d voxel-remesh activate。界面：Sculpting > main > Voxel Remesh。效果：点击「Voxel Remesh」（button）。示例：foxos 3d voxel-remesh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d voxel-remesh activate`

调用示例：

```json
{"name": "3d_voxel-remesh_activate", "arguments": {}}
```

### `3d_x-x_activate`

-X to +X。CLI：foxos 3d x-x activate。界面：Sculpting > main > -X to +X。效果：点击「-X to +X」（button）。示例：foxos 3d x-x activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d x-x activate`

调用示例：

```json
{"name": "3d_x-x_activate", "arguments": {}}
```

### `3d_symmetrize_activate`

Symmetrize。CLI：foxos 3d symmetrize activate。界面：Sculpting > main > Symmetrize。效果：点击「Symmetrize」（button）。示例：foxos 3d symmetrize activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d symmetrize activate`

调用示例：

```json
{"name": "3d_symmetrize_activate", "arguments": {}}
```

### `3d_shared-location_activate`

Shared Location。CLI：foxos 3d shared-location activate。界面：UV Editing > main > Shared Location。效果：点击「Shared Location」（button）。示例：foxos 3d shared-location activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d shared-location activate`

调用示例：

```json
{"name": "3d_shared-location_activate", "arguments": {}}
```

### `3d_no-image_activate`

No Image。CLI：foxos 3d no-image activate。界面：UV Editing > main > No Image。效果：点击「No Image」（button）。示例：foxos 3d no-image activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d no-image activate`

调用示例：

```json
{"name": "3d_no-image_activate", "arguments": {}}
```

### `3d_material-base-color_set`

Material Base Color。CLI：foxos 3d material-base-color set VALUE [--submit]。界面：Texture Paint > main > Material Base Color。效果：把「Material Base Color」设为给定值（触发 input / change 事件）。示例：foxos 3d material-base-color set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d material-base-color set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Material Base Color」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_material-base-color_set", "arguments": {"value": "…"}}
```

### `3d_mix_activate`

Mix。CLI：foxos 3d mix activate。界面：Texture Paint > main > Mix。效果：点击「Mix」（button）。示例：foxos 3d mix activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d mix activate`

调用示例：

```json
{"name": "3d_mix_activate", "arguments": {}}
```

### `3d_texture-paint_activate`

Texture Paint。CLI：foxos 3d texture-paint activate。界面：Texture Paint > main > Texture Paint。效果：点击「Texture Paint」（button）。示例：foxos 3d texture-paint activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d texture-paint activate`

调用示例：

```json
{"name": "3d_texture-paint_activate", "arguments": {}}
```

### `3d_soften_activate`

Soften。CLI：foxos 3d soften activate。界面：Texture Paint > main > Soften。效果：点击「Soften」（button）。示例：foxos 3d soften activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d soften activate`

调用示例：

```json
{"name": "3d_soften_activate", "arguments": {}}
```

### `3d_clone_activate`

Clone。CLI：foxos 3d clone activate。界面：Texture Paint > main > Clone。效果：点击「Clone」（button）。示例：foxos 3d clone activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d clone activate`

调用示例：

```json
{"name": "3d_clone_activate", "arguments": {}}
```

### `3d_fill_activate`

Fill。CLI：foxos 3d fill activate。界面：Texture Paint > main > Fill。效果：点击「Fill」（button）。示例：foxos 3d fill activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d fill activate`

调用示例：

```json
{"name": "3d_fill_activate", "arguments": {}}
```

### `3d_airbrush_activate`

Airbrush。CLI：foxos 3d airbrush activate。界面：Texture Paint > main > Airbrush。效果：点击「Airbrush」（button）。示例：foxos 3d airbrush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d airbrush activate`

调用示例：

```json
{"name": "3d_airbrush_activate", "arguments": {}}
```

### `3d_paint-soft-pressure_activate`

Paint Soft Pressure。CLI：foxos 3d paint-soft-pressure activate。界面：Texture Paint > main > Paint Soft Pressure。效果：点击「Paint Soft Pressure」（button）。示例：foxos 3d paint-soft-pressure activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d paint-soft-pressure activate`

调用示例：

```json
{"name": "3d_paint-soft-pressure_activate", "arguments": {}}
```

### `3d_pencil_activate`

Pencil。CLI：foxos 3d pencil activate。界面：Texture Paint > main > Pencil。效果：点击「Pencil」（button）。示例：foxos 3d pencil activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d pencil activate`

调用示例：

```json
{"name": "3d_pencil_activate", "arguments": {}}
```

### `3d_red-airbrush_activate`

Red Airbrush。CLI：foxos 3d red-airbrush activate。界面：Texture Paint > main > Red Airbrush。效果：点击「Red Airbrush」（button）。示例：foxos 3d red-airbrush activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d red-airbrush activate`

调用示例：

```json
{"name": "3d_red-airbrush_activate", "arguments": {}}
```

### `3d_speckle_activate`

Speckle。CLI：foxos 3d speckle activate。界面：Texture Paint > main > Speckle。效果：点击「Speckle」（button）。示例：foxos 3d speckle activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d speckle activate`

调用示例：

```json
{"name": "3d_speckle_activate", "arguments": {}}
```

### `3d_color_activate`

Color。CLI：foxos 3d color activate。界面：Texture Paint > main > Color。效果：点击「Color」（button）。示例：foxos 3d color activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d color activate`

调用示例：

```json
{"name": "3d_color_activate", "arguments": {}}
```

### `3d_gradient_activate`

Gradient。CLI：foxos 3d gradient activate。界面：Texture Paint > main > Gradient。效果：点击「Gradient」（button）。示例：foxos 3d gradient activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d gradient activate`

调用示例：

```json
{"name": "3d_gradient_activate", "arguments": {}}
```

### `3d_base-color-texture_create`

New Base Color Texture。CLI：foxos 3d base-color-texture create。界面：Texture Paint > main > New Base Color Texture。效果：点击「New Base Color Texture」（button）。示例：foxos 3d base-color-texture create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d base-color-texture create`

调用示例：

```json
{"name": "3d_base-color-texture_create", "arguments": {}}
```

### `3d_back_previous`

Back。CLI：foxos 3d back previous。界面：Shading > Back。效果：点击「Back」（button）。示例：foxos 3d back previous --json

只读：是 · 破坏性：否 · CLI：`foxos 3d back previous`

调用示例：

```json
{"name": "3d_back_previous", "arguments": {}}
```

### `3d_forward_next`

Forward。CLI：foxos 3d forward next。界面：Shading > Forward。效果：点击「Forward」（button）。示例：foxos 3d forward next --json

只读：是 · 破坏性：否 · CLI：`foxos 3d forward next`

调用示例：

```json
{"name": "3d_forward_next", "arguments": {}}
```

### `3d_parent-directory_activate`

Parent Directory。CLI：foxos 3d parent-directory activate。界面：Shading > Parent Directory。效果：点击「Parent Directory」（button）。示例：foxos 3d parent-directory activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d parent-directory activate`

调用示例：

```json
{"name": "3d_parent-directory_activate", "arguments": {}}
```

### `3d_refresh_activate`

Refresh。CLI：foxos 3d refresh activate。界面：Shading > Refresh。效果：点击「Refresh」（button）。示例：foxos 3d refresh activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d refresh activate`

调用示例：

```json
{"name": "3d_refresh_activate", "arguments": {}}
```

### `3d_directory_create`

Create New Directory。CLI：foxos 3d directory create。界面：Shading > Create New Directory。效果：点击「Create New Directory」（button）。示例：foxos 3d directory create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d directory create`

调用示例：

```json
{"name": "3d_directory_create", "arguments": {}}
```

### `3d_no-folder-opened_activate`

No folder opened。CLI：foxos 3d no-folder-opened activate。界面：Shading > main > No folder opened。效果：点击「No folder opened」（button）。示例：foxos 3d no-folder-opened activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d no-folder-opened activate`

调用示例：

```json
{"name": "3d_no-folder-opened_activate", "arguments": {}}
```

### `3d_settings_filter`

Filter settings。CLI：foxos 3d settings filter。界面：Shading > Filter settings。效果：点击「Filter settings」（button）。示例：foxos 3d settings filter --json

只读：是 · 破坏性：否 · CLI：`foxos 3d settings filter`

调用示例：

```json
{"name": "3d_settings_filter", "arguments": {}}
```

### `3d_folder_open`

Open Folder…。CLI：foxos 3d folder open。界面：Shading > main > Open Folder…。效果：点击「Open Folder…」（button）。示例：foxos 3d folder open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d folder open`

调用示例：

```json
{"name": "3d_folder_open", "arguments": {}}
```

### `3d_browser-storage_activate`

Browser Storage。CLI：foxos 3d browser-storage activate。界面：Shading > main > Browser Storage。效果：点击「Browser Storage」（button）。示例：foxos 3d browser-storage activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d browser-storage activate`

调用示例：

```json
{"name": "3d_browser-storage_activate", "arguments": {}}
```

### `3d_files_create`

Add Files…。CLI：foxos 3d files create。界面：Shading > main > Add Files…。效果：点击「Add Files…」（button）。示例：foxos 3d files create --json

只读：否 · 破坏性：否 · CLI：`foxos 3d files create`

调用示例：

```json
{"name": "3d_files_create", "arguments": {}}
```

### `3d_open_open`

Open。CLI：foxos 3d open open。界面：Shading > main > Open。效果：点击「Open」（button）。示例：foxos 3d open open --json

只读：是 · 破坏性：否 · CLI：`foxos 3d open open`

调用示例：

```json
{"name": "3d_open_open", "arguments": {}}
```

### `3d_material_set`

Material。CLI：foxos 3d material set VALUE [--submit]。界面：Shading > main > Material。效果：把「Material」设为给定值（触发 input / change 事件）。示例：foxos 3d material set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d material set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「Material」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_material_set", "arguments": {"value": "…"}}
```

### `3d_world_set`

World。CLI：foxos 3d world set VALUE [--submit]。界面：Shading > main > World。效果：把「World」设为给定值（触发 input / change 事件）。示例：foxos 3d world set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d world set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「World」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_world_set", "arguments": {"value": "…"}}
```

### `3d_background_activate`

Background。CLI：foxos 3d background activate。界面：Shading > main > Background。效果：点击「Background」（button）。示例：foxos 3d background activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d background activate`

调用示例：

```json
{"name": "3d_background_activate", "arguments": {}}
```

### `3d_dope-sheet_activate`

Dope Sheet。CLI：foxos 3d dope-sheet activate。界面：Animation > main > Dope Sheet。效果：点击「Dope Sheet」（button）。示例：foxos 3d dope-sheet activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d dope-sheet activate`

调用示例：

```json
{"name": "3d_dope-sheet_activate", "arguments": {}}
```

### `3d_channel_activate`

Channel。CLI：foxos 3d channel activate。界面：Animation > main > Channel。效果：点击「Channel」（button）。示例：foxos 3d channel activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d channel activate`

调用示例：

```json
{"name": "3d_channel_activate", "arguments": {}}
```

### `3d_key_activate`

Key。CLI：foxos 3d key activate。界面：Animation > main > Key。效果：点击「Key」（button）。示例：foxos 3d key activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d key activate`

调用示例：

```json
{"name": "3d_key_activate", "arguments": {}}
```

### `3d_keying_activate`

Keying。CLI：foxos 3d keying activate。界面：Animation > main > Keying。效果：点击「Keying」（button）。示例：foxos 3d keying activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d keying activate`

调用示例：

```json
{"name": "3d_keying_activate", "arguments": {}}
```

### `3d_image_activate`

Image。CLI：foxos 3d image activate。界面：Rendering > main > Image。效果：点击「Image」（button）。示例：foxos 3d image activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d image activate`

调用示例：

```json
{"name": "3d_image_activate", "arguments": {}}
```

### `3d_tool_activate`

Tool。CLI：foxos 3d tool activate。界面：Rendering > main > Tool。效果：点击「Tool」（button）。示例：foxos 3d tool activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d tool activate`

调用示例：

```json
{"name": "3d_tool_activate", "arguments": {}}
```

### `3d_scopes_activate`

Scopes。CLI：foxos 3d scopes activate。界面：Rendering > main > Scopes。效果：点击「Scopes」（button）。示例：foxos 3d scopes activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d scopes activate`

调用示例：

```json
{"name": "3d_scopes_activate", "arguments": {}}
```

### `3d_realtime-raster_activate`

Realtime (Raster)。CLI：foxos 3d realtime-raster activate。界面：Rendering > main > Realtime (Raster)。效果：点击「Realtime (Raster)」（button）。示例：foxos 3d realtime-raster activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d realtime-raster activate`

调用示例：

```json
{"name": "3d_realtime-raster_activate", "arguments": {}}
```

### `3d_backdrop_activate`

Backdrop。CLI：foxos 3d backdrop activate。界面：Compositing > main > Backdrop。效果：点击「Backdrop」（button）。示例：foxos 3d backdrop activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d backdrop activate`

调用示例：

```json
{"name": "3d_backdrop_activate", "arguments": {}}
```

### `3d_node_activate`

Node。CLI：foxos 3d node activate。界面：Compositing > main > Node。效果：点击「Node」（button）。示例：foxos 3d node activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d node activate`

调用示例：

```json
{"name": "3d_node_activate", "arguments": {}}
```

### `3d_render_set`

//render/。CLI：foxos 3d render set VALUE [--submit]。界面：Compositing > main > //render/。效果：把「//render/」设为给定值（触发 input / change 事件）。示例：foxos 3d render set '示例' --json

只读：否 · 破坏性：否 · CLI：`foxos 3d render set`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `value` | string | 是 | 「//render/」的新值 |
| `submit` | boolean |  | 设置后按 Enter 提交 |

调用示例：

```json
{"name": "3d_render_set", "arguments": {"value": "…"}}
```

### `3d_png_activate`

PNG。CLI：foxos 3d png activate。界面：Compositing > main > PNG。效果：点击「PNG」（button）。示例：foxos 3d png activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d png activate`

调用示例：

```json
{"name": "3d_png_activate", "arguments": {}}
```

### `3d_rgba_activate`

RGBA。CLI：foxos 3d rgba activate。界面：Compositing > main > RGBA。效果：点击「RGBA」（button）。示例：foxos 3d rgba activate --json

只读：否 · 破坏性：否 · CLI：`foxos 3d rgba activate`

调用示例：

```json
{"name": "3d_rgba_activate", "arguments": {}}
```

### `3d_selection_copy`

快捷键 mod+c。CLI：foxos 3d selection copy。界面：键盘 mod+c；快捷键 mod+c。效果：在当前焦点上按 mod+c（src/sequencer/transform.ts 中定义）。示例：foxos 3d selection copy --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection copy`

调用示例：

```json
{"name": "3d_selection_copy", "arguments": {}}
```

### `3d_selection_lock`

快捷键 mod+l。CLI：foxos 3d selection lock。界面：键盘 mod+l；快捷键 mod+l。效果：在当前焦点上按 mod+l（src/scripting/console.ts 中定义）。示例：foxos 3d selection lock --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection lock`

调用示例：

```json
{"name": "3d_selection_lock", "arguments": {}}
```

### `3d_selection_cut`

快捷键 mod+x。CLI：foxos 3d selection cut。界面：键盘 mod+x；快捷键 mod+x。效果：在当前焦点上按 mod+x（src/sequencer/pvtransform.ts 中定义）。示例：foxos 3d selection cut --json

只读：否 · 破坏性：否 · CLI：`foxos 3d selection cut`

调用示例：

```json
{"name": "3d_selection_cut", "arguments": {}}
```

### `3d_edit_undo`

快捷键 mod+z。CLI：foxos 3d edit undo。界面：键盘 mod+z；快捷键 mod+z。效果：在当前焦点上按 mod+z（src/modes/editmesh/knife.ts 中定义）。示例：foxos 3d edit undo --json

只读：否 · 破坏性：否 · CLI：`foxos 3d edit undo`

调用示例：

```json
{"name": "3d_edit_undo", "arguments": {}}
```

## cad（198 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `cad_arc_select` | 是 | `target`*: string |
| `cad_application-menu_select` | 是 | `target`*: string |
| `cad_circle-options_select` | 是 | `target`*: string |
| `cad_arc-options_select` | 是 | `target`*: string |
| `cad_application-menu_activate` |  | — |
| `cad_drawing_create` |  | — |
| `cad_open_open` | 是 | — |
| `cad_save_save` |  | — |
| `cad_undo_undo` |  | — |
| `cad_redo_redo` |  | — |
| `cad_plot_activate` |  | — |
| `cad_commands_search` | 是 | — |
| `cad_theme_activate` |  | — |
| `cad_help_show` | 是 | — |
| `cad_source-code-github-opens-tab_show` | 是 | — |
| `cad_home_show` | 是 | — |
| `cad_insert_create` |  | — |
| `cad_annotate_show` | 是 | — |
| `cad_view_show` | 是 | — |
| `cad_manage_show` | 是 | — |
| `cad_output_show` | 是 | — |
| `cad_minimize-ribbon_activate` |  | — |
| `cad_line_activate` |  | — |
| `cad_polyline_activate` |  | — |
| `cad_circle-center-radius_activate` |  | — |
| `cad_circle-options_activate` |  | — |
| `cad_arc-options_activate` |  | — |
| `cad_rectangle_activate` |  | — |
| `cad_rectangle-options_activate` |  | — |
| `cad_ellipse_activate` |  | — |
| `cad_ellipse-options_activate` |  | — |
| `cad_hatch_activate` |  | — |
| `cad_spline_activate` |  | — |
| `cad_construction-line_activate` |  | — |
| `cad_point_activate` |  | — |
| `cad_draw_draw` |  | — |
| `cad_move_move` |  | — |
| `cad_copy_copy` |  | — |
| `cad_stretch_activate` |  | — |
| `cad_rotate_rotate` |  | — |
| `cad_mirror_activate` |  | — |
| `cad_scale_activate` |  | — |
| `cad_trim_activate` |  | — |
| `cad_trim-options_activate` |  | — |
| `cad_fillet_activate` |  | — |
| `cad_fillet-options_activate` |  | — |
| `cad_array_activate` |  | — |
| `cad_array-options_activate` |  | — |
| `cad_erase_activate` |  | — |
| `cad_explode_activate` |  | — |
| `cad_offset_activate` |  | — |
| `cad_modify_update` |  | — |
| `cad_text-multiline-text_activate` |  | — |
| `cad_text-options_activate` |  | — |
| `cad_dimension-linear_activate` |  | — |
| `cad_dimension-options_activate` |  | — |
| `cad_leader_activate` |  | — |
| `cad_continue_activate` |  | — |
| `cad_baseline_activate` |  | — |
| `cad_layer-properties_activate` |  | — |
| `cad_turn-layer-off_activate` |  | — |
| `cad_isolate-layers_activate` |  | — |
| `cad_freeze-layer_activate` |  | — |
| `cad_layer_lock` |  | — |
| `cad_make-current_activate` |  | — |
| `cad_turn-layers_activate` |  | — |
| `cad_unisolate-layers_activate` |  | — |
| `cad_thaw-layers_activate` |  | — |
| `cad_layer_unlock` |  | — |
| `cad_match-layer_activate` |  | — |
| `cad_insert-2_create` |  | — |
| `cad_create_create` |  | — |
| `cad_library_activate` |  | — |
| `cad_match-properties_activate` |  | — |
| `cad_measure-distance_activate` |  | — |
| `cad_measure-options_activate` |  | — |
| `cad_quick-select_activate` |  | — |
| `cad_select_select` | 是 | — |
| `cad_similar_select` | 是 | — |
| `cad_paste_paste` |  | — |
| `cad_cut_cut` |  | — |
| `cad_clipboard_copy` |  | — |
| `cad_base-point_copy` |  | — |
| `cad_it_dismiss` | 是 | — |
| `cad_cursor-coordinates-click-change-display_activate` |  | — |
| `cad_grid_activate` |  | — |
| `cad_snap-grid_activate` |  | — |
| `cad_snap-grid-settings_activate` |  | — |
| `cad_ortho-mode_activate` |  | — |
| `cad_polar-tracking_activate` |  | — |
| `cad_polar-tracking-settings_activate` |  | — |
| `cad_object-snap_activate` |  | — |
| `cad_object-snap-settings_activate` |  | — |
| `cad_object-snap-tracking_activate` |  | — |
| `cad_dynamic-input_activate` |  | — |
| `cad_lineweights_show` | 是 | — |
| `cad_selection-preview_activate` |  | — |
| `cad_drawing-units_activate` |  | — |
| `cad_drafting-settings_activate` |  | — |
| `cad_clean-screen_activate` |  | — |
| `cad_newctrln_activate` |  | — |
| `cad_ctrlo_open` | 是 | — |
| `cad_sample-drawing_open` | 是 | — |
| `cad_savectrls_activate` |  | — |
| `cad_as-ctrlshifts_save` |  | — |
| `cad_dxf-or-dwg_import` |  | — |
| `cad_export_export` |  | — |
| `cad_plot-ctrlp_activate` |  | — |
| `cad_application-menu-drawing-units_activate` |  | — |
| `cad_purge-unused_activate` |  | — |
| `cad_settings_show` | 是 | — |
| `cad_keyboard-shortcuts_activate` |  | — |
| `cad_source-code-github_activate` |  | — |
| `cad_drawing_close` | 是 | — |
| `cad_close_close` | 是 | — |
| `cad_search-commands_set` |  | `value`*: string, `submit`: boolean |
| `cad_alignalign_activate` |  | — |
| `cad_aligned-dimensiondimaligned_activate` |  | — |
| `cad_angular-dimensiondimangular_activate` |  | — |
| `cad_arcarc_activate` |  | — |
| `cad_baseline-dimensiondimbaseline_activate` |  | — |
| `cad_blocks-paletteblocks_activate` |  | — |
| `cad_breakbreak_activate` |  | — |
| `cad_break-at-pointbreakatpoint_activate` |  | — |
| `cad_chamferchamfer_activate` |  | — |
| `cad_circlecircle_activate` |  | — |
| `cad_clean-screencleanscreen_activate` |  | — |
| `cad_drawingclose_close` | 是 | — |
| `cad_construction-linexline_activate` |  | — |
| `cad_continue-dimensiondimcontinue_activate` |  | — |
| `cad_copycopy_activate` |  | — |
| `cad_clipboardcopyclip_copy` |  | — |
| `cad_base-pointcopybase_copy` |  | — |
| `cad_blockblock_create` |  | — |
| `cad_cutcutclip_activate` |  | — |
| `cad_diameter-dimensiondimdiameter_activate` |  | — |
| `cad_dimensiondim_activate` |  | — |
| `cad_dimension-stylesdimstyle_activate` |  | — |
| `cad_donutdonut_activate` |  | — |
| `cad_drafting-settingsdsettings_activate` |  | — |
| `cad_orderdraworder_draw` |  | — |
| `cad_drawing-unitsunits_activate` |  | — |
| `cad_ellipseellipse_activate` |  | — |
| `cad_eraseerase_activate` |  | — |
| `cad_explodeexplode_activate` |  | — |
| `cad_exportexport_activate` |  | — |
| `cad_dwgdwgout_export` |  | — |
| `cad_dxfdxfout_export` |  | — |
| `cad_extendextend_activate` |  | — |
| `cad_filletfillet_activate` |  | — |
| `cad_freeze-layerlayfrz_activate` |  | — |
| `cad_grid-displaygrid_activate` |  | — |
| `cad_hatchhatch_activate` |  | — |
| `cad_helphelp_activate` |  | — |
| `cad_dxf-or-dwgimport_import` |  | — |
| `cad_blockinsert_create` |  | — |
| `cad_isolate-layerslayiso_activate` |  | — |
| `cad_joinjoin_activate` |  | — |
| `cad_keyboard-shortcutsshortcuts_activate` |  | — |
| `cad_layer-propertieslayer_activate` |  | — |
| `cad_leaderleader_activate` |  | — |
| `cad_lengthenlengthen_activate` |  | — |
| `cad_lineline_activate` |  | — |
| `cad_linear-dimensiondimlinear_activate` |  | — |
| `cad_linetype-scaleltscale_activate` |  | — |
| `cad_linetypeslinetype_activate` |  | — |
| `cad_system_activate` |  | — |
| `cad_light_activate` |  | — |
| `cad_dark_activate` |  | — |
| `cad_center-radius_activate` |  | — |
| `cad_center-diameter_activate` |  | — |
| `cad_tan-tan-radius_activate` |  | — |
| `cad_center-end_start` |  | — |
| `cad_center-start-end_activate` |  | — |
| `cad_end-radius_start` |  | — |
| `cad_rectangle-options-rectangle_activate` |  | — |
| `cad_polygon_activate` |  | — |
| `cad_center_activate` |  | — |
| `cad_axis-end_activate` |  | — |
| `cad_elliptical-arc_activate` |  | — |

## parametric（50 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `parametric_item_select` | 是 | `target`*: string |
| `parametric_default-units_select` | 是 | `target`*: string |
| `parametric_graphics-area_dismiss` | 是 | — |
| `parametric_edit_update` |  | — |
| `parametric_view_show` | 是 | — |
| `parametric_insert_create` |  | — |
| `parametric_tools_activate` |  | — |
| `parametric_help_show` | 是 | — |
| `parametric_open_open` | 是 | — |
| `parametric_save_save` |  | — |
| `parametric_undo_undo` |  | — |
| `parametric_redo_redo` |  | — |
| `parametric_rebuild_activate` |  | — |
| `parametric_options_activate` |  | — |
| `parametric_part_rename` |  | — |
| `parametric_search-commands_set` |  | `value`*: string, `submit`: boolean |
| `parametric_assistant_activate` |  | — |
| `parametric_share_share` |  | — |
| `parametric_source-code-github_show` | 是 | — |
| `parametric_apps_activate` |  | — |
| `parametric_account_activate` |  | — |
| `parametric_panel_resize` |  | — |
| `parametric_unit-system_activate` |  | — |
| `parametric_close_close` | 是 | — |
| `parametric_system_activate` |  | — |
| `parametric_light_activate` |  | — |
| `parametric_dark_activate` |  | — |
| `parametric_image-quality_set` |  | `value`*: string, `submit`: boolean |
| `parametric_reverse-mouse-wheel-zoom-direction_toggle` |  | — |
| `parametric_done_confirm` |  | — |
| `parametric_apps-tab_open` | 是 | — |
| `parametric_document_save` |  | — |

## circuits（56 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `circuits_theme_select` | 是 | `target`*: string |
| `circuits_account_select` | 是 | `target`*: string |
| `circuits_examplea-led-blinker-its-board_open` | 是 | `target`*: string |
| `circuits_design-canvas_dismiss` | 是 | — |
| `circuits_project_create` |  | — |
| `circuits_project_open` | 是 | — |
| `circuits_save_save` |  | — |
| `circuits_undo_undo` |  | — |
| `circuits_redo_redo` |  | — |
| `circuits_commandsctrlk_search` | 是 | — |
| `circuits_source-code-github-opens-tab_show` | 是 | — |
| `circuits_edit_update` |  | — |
| `circuits_view_show` | 是 | — |
| `circuits_project_activate` |  | — |
| `circuits_reports_activate` |  | — |
| `circuits_window_activate` |  | — |
| `circuits_help_show` | 是 | — |
| `circuits_schematic-sheet_create` |  | — |
| `circuits_board_create` |  | — |
| `circuits_project-options_activate` |  | — |
| `circuits_projects_show` | 是 | — |
| `circuits_navigator_show` | 是 | — |
| `circuits_properties_show` | 是 | — |
| `circuits_components_show` | 是 | — |
| `circuits_puter_show` | 是 | — |
| `circuits_panels_activate` |  | — |
| `circuits_it_dismiss` | 是 | — |
| `circuits_notification_dismiss` | 是 | — |
| `circuits_preferences_activate` |  | — |
| `circuits_schematic-sheet_activate` |  | — |
| `circuits_board_activate` |  | — |
| `circuits_project_rename` |  | — |
| `circuits_savectrls_activate` |  | — |
| `circuits_project-file_export` |  | — |
| `circuits_compile-electrical-rules-check_activate` |  | — |
| `circuits_annotate-schematics_activate` |  | — |
| `circuits_board-from-schematic_update` |  | — |
| `circuits_project_close` | 是 | — |

## building-design（19 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `building-design_it_dismiss` | 是 | — |

## tasks（76 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `tasks_add_create` |  | `target`*: string |
| `tasks_skip_dismiss` | 是 | `target`*: string |
| `tasks_list_open` | 是 | `target`*: string |
| `tasks_actions_select` | 是 | `target`*: string |
| `tasks_tasks_open` | 是 | `target`*: string |
| `tasks_week-starts_select` | 是 | `target`*: string |
| `tasks_content_dismiss` | 是 | — |
| `tasks_task_create` |  | — |
| `tasks_today_show` | 是 | — |
| `tasks_upcoming_show` | 是 | — |
| `tasks_lists_show` | 是 | — |
| `tasks_calendar_show` | 是 | — |
| `tasks_logbook_show` | 是 | — |
| `tasks_settings_show` | 是 | — |
| `tasks_list_create` |  | — |
| `tasks_personal_show` | 是 | — |
| `tasks_work_show` | 是 | — |
| `tasks_search_search` | 是 | — |
| `tasks_add-task_set` |  | `value`*: string, `submit`: boolean |
| `tasks_options_show` | 是 | — |
| `tasks_close_close` | 是 | — |
| `tasks_first-task_create` |  | — |
| `tasks_explore-sample-data_activate` |  | — |
| `tasks_task-title_set` |  | `value`*: string, `submit`: boolean |
| `tasks_notes_set` |  | `value`*: string, `submit`: boolean |
| `tasks_list_set` |  | `value`*: string, `submit`: boolean |
| `tasks_due-date_set` |  | `value`*: string, `submit`: boolean |
| `tasks_due-time_set` |  | `value`*: string, `submit`: boolean |
| `tasks_today_activate` |  | — |
| `tasks_tomorrow_activate` |  | — |
| `tasks_week_next` | 是 | — |
| `tasks_no-date_activate` |  | — |
| `tasks_remind-me_set` |  | `value`*: string, `submit`: boolean |
| `tasks_none_activate` |  | — |
| `tasks_low_activate` |  | — |
| `tasks_medium_activate` |  | — |
| `tasks_high_activate` |  | — |
| `tasks_add-tag_set` |  | `value`*: string, `submit`: boolean |
| `tasks_repeat_set` |  | `value`*: string, `submit`: boolean |
| `tasks_subtask_create` |  | — |
| `tasks_cancel_cancel` | 是 | — |
| `tasks_task-2_create` |  | — |
| `tasks_upcoming-task_create` |  | — |
| `tasks_lists-list_create` |  | — |
| `tasks_ics-calendar-file_export` |  | — |
| `tasks_month_previous` | 是 | — |
| `tasks_calendar-today_activate` |  | — |
| `tasks_month_next` | 是 | — |
| `tasks_system_activate` |  | — |
| `tasks_light_activate` |  | — |
| `tasks_dark_activate` |  | — |
| `tasks_due-date-reminders_toggle` |  | — |
| `tasks_exportdownload-everything-as-json-file_activate` |  | — |
| `tasks_lists_previous` | 是 | — |
| `tasks_list_share` |  | — |
| `tasks_list_update` |  | — |
| `tasks_personal-add_create` |  | — |
| `tasks_search-tasks_set` |  | `value`*: string, `submit`: boolean |

## projects（68 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `projects_skip_dismiss` | 是 | `target`*: string |
| `projects_projects_show` | 是 | — |
| `projects_quick-addn_activate` |  | — |
| `projects_task_search` | 是 | — |
| `projects_commandsctrlk_activate` |  | — |
| `projects_today_show` | 是 | — |
| `projects_tasks_show` | 是 | — |
| `projects_project_create` |  | — |
| `projects_projects-2_show` | 是 | — |
| `projects_settings_show` | 是 | — |
| `projects_project-2_create` |  | — |
| `projects_project-3_create` |  | — |
| `projects_close_close` | 是 | — |
| `projects_first-project_create` |  | — |
| `projects_explore-sample-data_activate` |  | — |
| `projects_today-projects_show` | 是 | — |
| `projects_overdue_show` | 是 | — |
| `projects_high-priority_show` | 是 | — |
| `projects_unscheduled_show` | 是 | — |
| `projects_options_show` | 是 | — |
| `projects_filter-tasks-by-title_set` |  | `value`*: string, `submit`: boolean |
| `projects_label_activate` |  | — |
| `projects_assignee_activate` |  | — |
| `projects_priority_activate` |  | — |
| `projects_due_activate` |  | — |
| `projects_project_activate` |  | — |
| `projects_project-order_activate` |  | — |
| `projects_light_toggle` |  | — |
| `projects_dark_toggle` |  | — |
| `projects_system_toggle` |  | — |
| `projects_view_show` | 是 | — |
| `projects_export_export` |  | — |
| `projects_import_import` |  | — |
| `projects_calendar-file_export` |  | — |
| `projects_restore-points_open` | 是 | — |
| `projects_deleted-projects_open` | 是 | — |
| `projects_learn-more_show` | 是 | — |
| `projects_name_set` |  | `value`*: string, `submit`: boolean |
| `projects_purple_toggle` |  | — |
| `projects_teal_toggle` |  | — |
| `projects_amber_toggle` |  | — |
| `projects_rose_toggle` |  | — |
| `projects_indigo_toggle` |  | — |
| `projects_blue_toggle` |  | — |
| `projects_olive_toggle` |  | — |
| `projects_rust_toggle` |  | — |
| `projects_cancel_cancel` | 是 | — |
| `projects_project-4_create` |  | — |
| `projects_command-palette_show` | 是 | — |
| `projects_edit_undo` |  | — |

## wiki（78 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `wiki_heading_select` | 是 | `target`*: string |
| `wiki_files_import` |  | `target`*: string |
| `wiki_here_import` |  | `target`*: string |
| `wiki_page_dismiss` | 是 | — |
| `wiki_lolocal-s-wiki_activate` |  | — |
| `wiki_sidebar_close` | 是 | — |
| `wiki_searchctrlk_activate` |  | — |
| `wiki_home_activate` |  | — |
| `wiki_pagectrlaltn_create` |  | — |
| `wiki_private_activate` |  | — |
| `wiki_private-page_create` |  | — |
| `wiki_getting-started_activate` |  | — |
| `wiki_tasks_activate` |  | — |
| `wiki_notes_activate` |  | — |
| `wiki_templates_activate` |  | — |
| `wiki_import_import` |  | — |
| `wiki_trash_delete` |  | — |
| `wiki_settings_show` | 是 | — |
| `wiki_powered-by-puter_show` | 是 | — |
| `wiki_sidebar_resize` |  | — |
| `wiki_getting-started-2_activate` |  | — |
| `wiki_share_share` |  | — |
| `wiki_comments_activate` |  | — |
| `wiki_favorites_create` |  | — |
| `wiki_page-options_activate` |  | — |
| `wiki_page-icon_update` |  | — |
| `wiki_cover_create` |  | — |
| `wiki_getting-started_set` |  | `value`*: string, `submit`: boolean |
| `wiki_callout-icon_update` |  | — |
| `wiki_callout_set` |  | `value`*: string, `submit`: boolean |
| `wiki_text_set` |  | `value`*: string, `submit`: boolean |
| `wiki_bulleted-list_set` |  | `value`*: string, `submit`: boolean |
| `wiki_done_toggle` |  | — |
| `wiki_to-do-list_set` |  | `value`*: string, `submit`: boolean |
| `wiki_content_hide` | 是 | — |
| `wiki_toggle-list_set` |  | `value`*: string, `submit`: boolean |
| `wiki_quote_set` |  | `value`*: string, `submit`: boolean |
| `wiki_theme_activate` |  | — |
| `wiki_lolocals-wiki-settings_show` | 是 | — |
| `wiki_keyboard-shortcutsctrl_activate` |  | — |
| `wiki_close_close` | 是 | — |
| `wiki_system_toggle` |  | — |
| `wiki_light_toggle` |  | — |
| `wiki_dark_toggle` |  | — |
| `wiki_settings-powered-by-puter_show` | 是 | — |
| `wiki_page_share` |  | — |
| `wiki_page-options-favorites_create` |  | — |
| `wiki_link_copy` |  | — |
| `wiki_duplicate_duplicate` |  | — |
| `wiki_move_move` |  | — |
| `wiki_page_lock` |  | — |
| `wiki_export_export` |  | — |
| `wiki_page-history_activate` |  | — |
| `wiki_trash_move` |  | — |
| `wiki_selection_select-all` |  | — |
| `wiki_selection_copy` |  | — |
| `wiki_selection_duplicate` |  | — |
| `wiki_command-palette_show` | 是 | — |
| `wiki_selection_lock-shift` |  | — |
| `wiki_edit_undo` |  | — |

## time-tracking（89 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `time-tracking_skip_dismiss` | 是 | `target`*: string |
| `time-tracking_nov-9-nov-15-0m-across-0-days_select` | 是 | `target`*: string |
| `time-tracking_log-time_select` | 是 | `target`*: string |
| `time-tracking_printable-timesheet_select` | 是 | `target`*: string |
| `time-tracking_backup-from_export` |  | `target`*: string |
| `time-tracking_restore-backup-from_select` | 是 | `target`*: string |
| `time-tracking_csvevery-entry-ready_export` |  | `target`*: string |
| `time-tracking_content_dismiss` | 是 | — |
| `time-tracking_timer_show` | 是 | — |
| `time-tracking_timesheet_show` | 是 | — |
| `time-tracking_reports_show` | 是 | — |
| `time-tracking_projects_show` | 是 | — |
| `time-tracking_settings_show` | 是 | — |
| `time-tracking_log-time_activate` |  | — |
| `time-tracking_client_create` |  | — |
| `time-tracking_close_close` | 是 | — |
| `time-tracking_set-up-tracking_activate` |  | — |
| `time-tracking_explore-sample-data_activate` |  | — |
| `time-tracking_jump-date_activate` |  | — |
| `time-tracking_entries_search` | 是 | — |
| `time-tracking_week_activate` |  | — |
| `time-tracking_grid_activate` |  | — |
| `time-tracking_month_activate` |  | — |
| `time-tracking_week_previous` | 是 | — |
| `time-tracking_today_activate` |  | — |
| `time-tracking_week_next` | 是 | — |
| `time-tracking_log-time-yesterday_activate` |  | — |
| `time-tracking_log-time-today_activate` |  | — |
| `time-tracking_invoice-ready-summary-report_print` | 是 | — |
| `time-tracking_csv_export` |  | — |
| `time-tracking_report_activate` |  | — |
| `time-tracking_insights_activate` |  | — |
| `time-tracking_invoices_activate` |  | — |
| `time-tracking_reports-week_activate` |  | — |
| `time-tracking_last-week_activate` |  | — |
| `time-tracking_reports-month_activate` |  | — |
| `time-tracking_last-month_activate` |  | — |
| `time-tracking_custom_activate` |  | — |
| `time-tracking_client_activate` |  | — |
| `time-tracking_project_activate` |  | — |
| `time-tracking_task_activate` |  | — |
| `time-tracking_unbilled_activate` |  | — |
| `time-tracking_invoiced_activate` |  | — |
| `time-tracking_projects-client_create` |  | — |
| `time-tracking_first-client_create` |  | — |
| `time-tracking_light_activate` |  | — |
| `time-tracking_dark_activate` |  | — |
| `time-tracking_system_activate` |  | — |
| `time-tracking_currency_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_default-hourly-rate_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_default-rate-applies-from_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_round-billable-time_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_week-starts_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_weekly-target-hours_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_target-counts_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_business-name_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_address_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_tax-vat-id_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_default-tax-rate_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_payment-terms_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_terms-line_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_how-pay_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_logo_import` |  | — |
| `time-tracking_long-timer-warning_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_away-sleep-gaps_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_daily-tracking-nudge_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_unbilled-time-reminder_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_counts-as-aging_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_system-notifications_toggle` |  | — |
| `time-tracking_automatic-backups_set` |  | `value`*: string, `submit`: boolean |
| `time-tracking_puter_show` | 是 | — |

## survey（46 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `survey_folders_select` | 是 | `target`*: string |
| `survey_describe-survey_select` | 是 | `target`*: string |
| `survey_content_dismiss` | 是 | — |
| `survey_surveys-home_show` | 是 | — |
| `survey_source-code-github-opens-tab_show` | 是 | — |
| `survey_account-settings_activate` |  | — |
| `survey_folder_create` |  | — |
| `survey_source-github_open` | 是 | — |
| `survey_powered-by-puter_show` | 是 | — |
| `survey_survey_create` |  | — |
| `survey_from-scratcha-blank-survey_start` |  | — |
| `survey_use-templateready-made-fully-editable_activate` |  | — |
| `survey_questionspaste-list-or-open-file_import` |  | — |
| `survey_generate_run` |  | — |
| `survey_search-surveys_set` |  | `value`*: string, `submit`: boolean |
| `survey_filter-by-status_set` |  | `value`*: string, `submit`: boolean |
| `survey_sort-by_set` |  | `value`*: string, `submit`: boolean |
| `survey_survey-2_create` |  | — |
| `survey_it_dismiss` | 是 | — |
| `survey_system_activate` |  | — |
| `survey_light_activate` |  | — |
| `survey_dark_activate` |  | — |
| `survey_keyboard-shortcuts_activate` |  | — |
| `survey_surveys_show` | 是 | — |
| `survey_from-scratch_start` |  | — |
| `survey_use-template_activate` |  | — |
| `survey_ai_run` |  | — |
| `survey_questions_import` |  | — |

## accounting（63 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `accounting_account-menu_select` | 是 | `target`*: string |
| `accounting_company-name_select` | 是 | `target`*: string |
| `accounting_content_dismiss` | 是 | — |
| `accounting_home_show` | 是 | — |
| `accounting_create_create` |  | — |
| `accounting_home-2_show` | 是 | — |
| `accounting_banking_show` | 是 | — |
| `accounting_sales_show` | 是 | — |
| `accounting_purchases_show` | 是 | — |
| `accounting_reports_show` | 是 | — |
| `accounting_menu_show` | 是 | — |
| `accounting_settings_show` | 是 | — |
| `accounting_navigation_open` | 是 | — |
| `accounting_search_set` |  | `value`*: string, `submit`: boolean |
| `accounting_keyboard-shortcuts_activate` |  | — |
| `accounting_settings-2_show` | 是 | — |
| `accounting_panel_collapse` | 是 | — |
| `accounting_accounting_activate` |  | — |
| `accounting_purchases_activate` |  | — |
| `accounting_sales_activate` |  | — |
| `accounting_sales-tax_activate` |  | — |
| `accounting_reports_activate` |  | — |
| `accounting_puter_show` | 是 | — |
| `accounting_privacy_activate` |  | — |
| `accounting_invoice_create` |  | — |
| `accounting_payment_record` |  | — |
| `accounting_expense_record` |  | — |
| `accounting_enter-bill_activate` |  | — |
| `accounting_pay-bills_activate` |  | — |
| `accounting_deposit_record` |  | — |
| `accounting_write-check_activate` |  | — |
| `accounting_bank-statement_import` |  | — |
| `accounting_period_set` |  | `value`*: string, `submit`: boolean |
| `accounting_report_show` | 是 | — |
| `accounting_overdue_show` | 是 | — |
| `accounting_not-due-yet_show` | 是 | — |
| `accounting_paid_show` | 是 | — |
| `accounting_go-banking_show` | 是 | — |
| `accounting_as-table_show` | 是 | — |
| `accounting_close_close` | 是 | — |
| `accounting_home-currency_set` |  | `value`*: string, `submit`: boolean |
| `accounting_fiscal-year-starts_set` |  | `value`*: string, `submit`: boolean |
| `accounting_date-format_set` |  | `value`*: string, `submit`: boolean |
| `accounting_start-sample-company-explore_toggle` |  | — |
| `accounting_books_create` |  | — |

## invoicing（38 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `invoicing_skip_dismiss` | 是 | `target`*: string |
| `invoicing_content_dismiss` | 是 | — |
| `invoicing_switch-dark-theme_activate` |  | — |
| `invoicing_home_show` | 是 | — |
| `invoicing_invoices_show` | 是 | — |
| `invoicing_estimates_show` | 是 | — |
| `invoicing_recurring_show` | 是 | — |
| `invoicing_clients_show` | 是 | — |
| `invoicing_receipts_show` | 是 | — |
| `invoicing_saved-items_show` | 是 | — |
| `invoicing_reports_show` | 是 | — |
| `invoicing_trash_delete` |  | — |
| `invoicing_invoice_create` |  | — |
| `invoicing_estimate_create` |  | — |
| `invoicing_settings_show` | 是 | — |
| `invoicing_invoice-2_create` |  | — |
| `invoicing_estimate-2_create` |  | — |
| `invoicing_close_close` | 是 | — |
| `invoicing_set-up-business_activate` |  | — |
| `invoicing_explore-sample-data_activate` |  | — |

## expense（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `expense_month-nothing-last-month_select` | 是 | `target`*: string |
| `expense_not-report-expenses_select` | 是 | `target`*: string |
| `expense_awaiting-reimbursement-expenses-flight_select` | 是 | `target`*: string |
| `expense_lines-open_select` | 是 | `target`*: string |
| `expense_skip_dismiss` | 是 | `target`*: string |
| `expense_content_dismiss` | 是 | — |
| `expense_home_show` | 是 | — |
| `expense_expenses_show` | 是 | — |
| `expense_reports_show` | 是 | — |
| `expense_reconcile_show` | 是 | — |
| `expense_settings_show` | 是 | — |
| `expense_capture-receipt_activate` |  | — |
| `expense_manual-entry_activate` |  | — |
| `expense_capture-receipt-2_activate` |  | — |
| `expense_close_close` | 是 | — |
| `expense_set-up-expenses_activate` |  | — |
| `expense_explore-sample-data_activate` |  | — |

## cap-table（45 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `cap-table_skip_dismiss` | 是 | `target`*: string |
| `cap-table_main-content_dismiss` | 是 | — |
| `cap-table_searchctrl-k_activate` |  | — |
| `cap-table_home_activate` |  | — |
| `cap-table_cap-table_activate` |  | — |
| `cap-table_securities_activate` |  | — |
| `cap-table_stakeholders_activate` |  | — |
| `cap-table_classes_share` |  | — |
| `cap-table_round-modeling_activate` |  | — |
| `cap-table_exit-scenarios_activate` |  | — |
| `cap-table_needs-attention_activate` |  | — |
| `cap-table_reports_activate` |  | — |
| `cap-table_history_activate` |  | — |
| `cap-table_settings_show` | 是 | — |
| `cap-table_issue-security_activate` |  | — |
| `cap-table_issue-security-2_activate` |  | — |
| `cap-table_by-class_activate` |  | — |
| `cap-table_by-holder_activate` |  | — |
| `cap-table_cap-table_open` | 是 | — |
| `cap-table_set-up-company-profile-do_activate` |  | — |
| `cap-table_share-class-do_create` |  | — |
| `cap-table_issue-founder-shares-do_activate` |  | — |
| `cap-table_adopt-equity-plan-reserve-shares-do_activate` |  | — |
| `cap-table_grant-options-or-add-safe-do_activate` |  | — |
| `cap-table_close_close` | 是 | — |
| `cap-table_set-up-company_activate` |  | — |
| `cap-table_explore-sample-data_activate` |  | — |

## crm（34 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `crm_skip_dismiss` | 是 | `target`*: string |
| `crm_searchctrl-k_activate` |  | — |
| `crm_home_show` | 是 | — |
| `crm_pipeline_show` | 是 | — |
| `crm_leads_show` | 是 | — |
| `crm_follow-ups_show` | 是 | — |
| `crm_companies_show` | 是 | — |
| `crm_activity_show` | 是 | — |
| `crm_forecast_show` | 是 | — |
| `crm_settings_show` | 是 | — |
| `crm_lead_create` |  | — |
| `crm_me-around_show` | 是 | — |
| `crm_close_close` | 是 | — |
| `crm_set-up-pipeline_activate` |  | — |
| `crm_explore-sample-data_activate` |  | — |
| `crm_command-palette_show` | 是 | — |

## help-desk（24 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `help-desk_help-desk-name_set` |  | `value`*: string, `submit`: boolean |
| `help-desk_name_set` |  | `value`*: string, `submit`: boolean |
| `help-desk_help-desk_create` |  | — |
| `help-desk_source-code_show` | 是 | — |
| `help-desk_puter_show` | 是 | — |
| `help-desk_dismiss_dismiss` | 是 | — |

## contracts（32 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `contracts_skip_dismiss` | 是 | `target`*: string |
| `contracts_content_dismiss` | 是 | — |
| `contracts_home_show` | 是 | — |
| `contracts_contracts_show` | 是 | — |
| `contracts_renewals_show` | 是 | — |
| `contracts_obligations_show` | 是 | — |
| `contracts_contacts_show` | 是 | — |
| `contracts_settings_show` | 是 | — |
| `contracts_contract_create` |  | — |
| `contracts_contract-2_create` |  | — |
| `contracts_contract-3_create` |  | — |
| `contracts_close_close` | 是 | — |
| `contracts_first-contract_create` |  | — |
| `contracts_explore-sample-data_activate` |  | — |

## pos（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `pos_skip_dismiss` | 是 | `target`*: string |
| `pos_register_show` | 是 | — |
| `pos_products_show` | 是 | — |
| `pos_receipts_show` | 是 | — |
| `pos_customers_show` | 是 | — |
| `pos_reports_show` | 是 | — |
| `pos_settings_show` | 是 | — |
| `pos_search-products-or-scan-barcode_set` |  | `value`*: string, `submit`: boolean |
| `pos_cash-drawer_activate` |  | — |
| `pos_products_create` |  | — |
| `pos_custom-item_create` |  | — |
| `pos_park-sale-serve-next-customer_activate` |  | — |
| `pos_clear_clear` |  | — |
| `pos_charge_activate` |  | — |
| `pos_close_close` | 是 | — |
| `pos_set-up-store_activate` |  | — |
| `pos_explore-sample-data_activate` |  | — |

## inventory（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `inventory_skip_dismiss` | 是 | `target`*: string |
| `inventory_searchctrl-k_activate` |  | — |
| `inventory_overview_show` | 是 | — |
| `inventory_products_show` | 是 | — |
| `inventory_take-out_show` | 是 | — |
| `inventory_reorder_show` | 是 | — |
| `inventory_stocktake_show` | 是 | — |
| `inventory_history_show` | 是 | — |
| `inventory_reports_show` | 是 | — |
| `inventory_locations_show` | 是 | — |
| `inventory_suppliers_show` | 是 | — |
| `inventory_settings_show` | 是 | — |
| `inventory_product_create` |  | — |
| `inventory_close_close` | 是 | — |
| `inventory_set-up-inventory_activate` |  | — |
| `inventory_explore-sample-data_activate` |  | — |
| `inventory_command-palette_show` | 是 | — |

## assets（18 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|

## hiring（40 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `hiring_yet_open` | 是 | `target`*: string |
| `hiring_candidates-not-yet-hired_select` | 是 | `target`*: string |
| `hiring_interviews-today_select` | 是 | `target`*: string |
| `hiring_offers-signature_select` | 是 | `target`*: string |
| `hiring_main_select` | 是 | `target`*: string |
| `hiring_skip_dismiss` | 是 | `target`*: string |
| `hiring_searchctrl-k_activate` |  | — |
| `hiring_overview_activate` |  | — |
| `hiring_jobs_activate` |  | — |
| `hiring_pipeline_activate` |  | — |
| `hiring_interviews_activate` |  | — |
| `hiring_offers_activate` |  | — |
| `hiring_onboarding_activate` |  | — |
| `hiring_reports_activate` |  | — |
| `hiring_settings_show` | 是 | — |
| `hiring_theme_activate` |  | — |
| `hiring_puter_show` | 是 | — |
| `hiring_reports-2_activate` |  | — |
| `hiring_close_close` | 是 | — |
| `hiring_set-up-hiring_activate` |  | — |
| `hiring_explore-sample-data_activate` |  | — |
| `hiring_command-palette_show` | 是 | — |

## shifts（35 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `shifts_theme_select` | 是 | `target`*: string |
| `shifts_skip_dismiss` | 是 | `target`*: string |
| `shifts_home_activate` |  | — |
| `shifts_schedule_schedule` |  | — |
| `shifts_team_activate` |  | — |
| `shifts_availability_activate` |  | — |
| `shifts_swaps_activate` |  | — |
| `shifts_attendance_activate` |  | — |
| `shifts_reports_activate` |  | — |
| `shifts_backup-restore_activate` |  | — |
| `shifts_out_sign` |  | — |
| `shifts_puter_show` | 是 | — |
| `shifts_employee_create` |  | — |
| `shifts_sample-data_import` |  | — |
| `shifts_close_close` | 是 | — |
| `shifts_set-up-team_activate` |  | — |
| `shifts_explore-sample-data_activate` |  | — |

## childcare（57 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `childcare_children-enrolled_select` | 是 | `target`*: string |
| `childcare_absent-reported_select` | 是 | `target`*: string |
| `childcare_staff-staff-members_select` | 是 | `target`*: string |
| `childcare_ratio-rooms-ratio_select` | 是 | `target`*: string |
| `childcare_content_dismiss` | 是 | — |
| `childcare_log-or-add-n_activate` |  | — |
| `childcare_home_show` | 是 | — |
| `childcare_check-in_show` | 是 | — |
| `childcare_activities_show` | 是 | — |
| `childcare_messages_show` | 是 | — |
| `childcare_children_show` | 是 | — |
| `childcare_families_show` | 是 | — |
| `childcare_rooms_show` | 是 | — |
| `childcare_staff_show` | 是 | — |
| `childcare_calendar_show` | 是 | — |
| `childcare_menus_show` | 是 | — |
| `childcare_billing_show` | 是 | — |
| `childcare_reports_show` | 是 | — |
| `childcare_source-code-github-opens-tab_show` | 是 | — |
| `childcare_puter_show` | 是 | — |
| `childcare_navigation_collapse` | 是 | — |
| `childcare_search_search` | 是 | — |
| `childcare_keyboard-shortcuts_activate` |  | — |
| `childcare_settings_show` | 是 | — |
| `childcare_account-appearance_activate` |  | — |
| `childcare_kiosk_show` | 是 | — |
| `childcare_check_run` |  | — |
| `childcare_log-activity_activate` |  | — |
| `childcare_room_create` |  | — |
| `childcare_log_open` | 是 | — |
| `childcare_log-activity-2_activate` |  | — |
| `childcare_calendar-2_show` | 是 | — |
| `childcare_it_dismiss` | 是 | — |
| `childcare_close_close` | 是 | — |
| `childcare_school-name_set` |  | `value`*: string, `submit`: boolean |
| `childcare_rooms_set` |  | `value`*: string, `submit`: boolean |
| `childcare_use-sample-data_activate` |  | — |
| `childcare_get-started_activate` |  | — |
| `childcare_command-palette_show` | 是 | — |

## field-service（58 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `field-service_workflow_select` | 是 | `target`*: string |
| `field-service_paymentowed-you_select` | 是 | `target`*: string |
| `field-service_content_dismiss` | 是 | — |
| `field-service_n_create` |  | — |
| `field-service_home_show` | 是 | — |
| `field-service_schedule_schedule` |  | — |
| `field-service_clients_show` | 是 | — |
| `field-service_requests_show` | 是 | — |
| `field-service_quotes_show` | 是 | — |
| `field-service_jobs_show` | 是 | — |
| `field-service_invoices_show` | 是 | — |
| `field-service_payments_show` | 是 | — |
| `field-service_timesheets_show` | 是 | — |
| `field-service_expenses_show` | 是 | — |
| `field-service_reports_show` | 是 | — |
| `field-service_source-code-github-opens-tab_show` | 是 | — |
| `field-service_puter_show` | 是 | — |
| `field-service_navigation_collapse` | 是 | — |
| `field-service_search_search` | 是 | — |
| `field-service_keyboard-shortcuts_activate` |  | — |
| `field-service_settings_show` | 是 | — |
| `field-service_account-appearance_activate` |  | — |
| `field-service_dismiss_dismiss` | 是 | — |
| `field-service_business-details_create` |  | — |
| `field-service_services-you-offer_create` |  | — |
| `field-service_team_create` |  | — |
| `field-service_first-client_create` |  | — |
| `field-service_first-quote_send` |  | — |
| `field-service_schedule-2_schedule` |  | — |
| `field-service_job_create` |  | — |
| `field-service_reports-2_show` | 是 | — |
| `field-service_close_close` | 是 | — |
| `field-service_business-name_set` |  | `value`*: string, `submit`: boolean |
| `field-service_name_set` |  | `value`*: string, `submit`: boolean |
| `field-service_industry_set` |  | `value`*: string, `submit`: boolean |
| `field-service_currency_set` |  | `value`*: string, `submit`: boolean |
| `field-service_sample-data_import` |  | — |
| `field-service_get-started_activate` |  | — |
| `field-service_it_dismiss` | 是 | — |
| `field-service_command-palette_show` | 是 | — |

## legal（61 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `legal_timer_start` |  | `target`*: string |
| `legal_draft-bills-bills_select` | 是 | `target`*: string |
| `legal_unpaid-bills_select` | 是 | `target`*: string |
| `legal_overdue-bills_select` | 是 | `target`*: string |
| `legal_held-trust-trust-accounts_select` | 是 | `target`*: string |
| `legal_firm-name_select` | 是 | `target`*: string |
| `legal_content_dismiss` | 是 | — |
| `legal_legal-dashboard_show` | 是 | — |
| `legal_dashboard_show` | 是 | — |
| `legal_calendar_show` | 是 | — |
| `legal_tasks_show` | 是 | — |
| `legal_matters_show` | 是 | — |
| `legal_contacts_show` | 是 | — |
| `legal_activities_show` | 是 | — |
| `legal_billing_show` | 是 | — |
| `legal_accounts_show` | 是 | — |
| `legal_documents_show` | 是 | — |
| `legal_communications_show` | 是 | — |
| `legal_reports_show` | 是 | — |
| `legal_settings_show` | 是 | — |
| `legal_source-code-github-opens-tab_show` | 是 | — |
| `legal_navigation_collapse` | 是 | — |
| `legal_search_search` | 是 | — |
| `legal_timer-details_activate` |  | — |
| `legal_n_create` |  | — |
| `legal_alerts_activate` |  | — |
| `legal_account-appearance_activate` |  | — |
| `legal_task_create` |  | — |
| `legal_time_record` |  | — |
| `legal_personal_show` | 是 | — |
| `legal_firm_show` | 是 | — |
| `legal_firm-users_open` | 是 | — |
| `legal_calendar-2_show` | 是 | — |
| `legal_matters-2_show` | 是 | — |
| `legal_matter_create` |  | — |
| `legal_activities-2_show` | 是 | — |
| `legal_billing-2_show` | 是 | — |
| `legal_i-understand_activate` |  | — |
| `legal_close_close` | 是 | — |
| `legal_currency_set` |  | `value`*: string, `submit`: boolean |
| `legal_explore-sample-data_activate` |  | — |
| `legal_continue_activate` |  | — |
| `legal_command-palette_show` | 是 | — |

## fleet（59 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `fleet_content_dismiss` | 是 | — |
| `fleet_dashboard_show` | 是 | — |
| `fleet_dashboard-2_show` | 是 | — |
| `fleet_vehicles_activate` |  | — |
| `fleet_inspections_activate` |  | — |
| `fleet_issues_show` | 是 | — |
| `fleet_reminders_activate` |  | — |
| `fleet_service_activate` |  | — |
| `fleet_contacts_show` | 是 | — |
| `fleet_vendors_show` | 是 | — |
| `fleet_parts-inventory_activate` |  | — |
| `fleet_fuel-energy_show` | 是 | — |
| `fleet_documents_show` | 是 | — |
| `fleet_reports_show` | 是 | — |
| `fleet_settings_show` | 是 | — |
| `fleet_source-code-github-opens-tab_show` | 是 | — |
| `fleet_puter_show` | 是 | — |
| `fleet_sidebar_collapse` | 是 | — |
| `fleet_search_search` | 是 | — |
| `fleet_keyboard-shortcuts_activate` |  | — |
| `fleet_needs-attention_activate` |  | — |
| `fleet_add_create` |  | — |
| `fleet_account-appearance_activate` |  | — |
| `fleet_inspection_start` |  | — |
| `fleet_report-issue_show` | 是 | — |
| `fleet_fuel_create` |  | — |
| `fleet_vehicle_create` |  | — |
| `fleet_contact_create` |  | — |
| `fleet_inspection-forms_show` | 是 | — |
| `fleet_service-programs_show` | 是 | — |
| `fleet_team-access_show` | 是 | — |
| `fleet_it_dismiss` | 是 | — |
| `fleet_close_close` | 是 | — |
| `fleet_fleet-or-company-name_set` |  | `value`*: string, `submit`: boolean |
| `fleet_distance_set` |  | `value`*: string, `submit`: boolean |
| `fleet_fuel-volume_set` |  | `value`*: string, `submit`: boolean |
| `fleet_currency_set` |  | `value`*: string, `submit`: boolean |
| `fleet_sample-data_start` |  | — |
| `fleet_continue_activate` |  | — |
| `fleet_command-palette_show` | 是 | — |
| `fleet_document_save` |  | — |

## property-management（63 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `property-management_collected-charges-posted-yet_select` | 是 | `target`*: string |
| `property-management_outstanding-balances-is-paid-up_select` | 是 | `target`*: string |
| `property-management_units-occupied_select` | 是 | `target`*: string |
| `property-management_work-urgent_open` | 是 | `target`*: string |
| `property-management_view_show` | 是 | `target`*: string |
| `property-management_financials_select` | 是 | `target`*: string |
| `property-management_renewals_select` | 是 | `target`*: string |
| `property-management_calendar_select` | 是 | `target`*: string |
| `property-management_listings_select` | 是 | `target`*: string |
| `property-management_content_dismiss` | 是 | — |
| `property-management_dashboard_show` | 是 | — |
| `property-management_n_create` |  | — |
| `property-management_dashboard-2_show` | 是 | — |
| `property-management_rentals_activate` |  | — |
| `property-management_properties_show` | 是 | — |
| `property-management_rent-roll_show` | 是 | — |
| `property-management_tenants_show` | 是 | — |
| `property-management_rental-owners_show` | 是 | — |
| `property-management_outstanding-balances_show` | 是 | — |
| `property-management_leasing_activate` |  | — |
| `property-management_accounting_activate` |  | — |
| `property-management_maintenance_activate` |  | — |
| `property-management_tasks_show` | 是 | — |
| `property-management_communication_show` | 是 | — |
| `property-management_calendar_show` | 是 | — |
| `property-management_reports_show` | 是 | — |
| `property-management_settings_show` | 是 | — |
| `property-management_source-code-github-opens-tab_show` | 是 | — |
| `property-management_puter_show` | 是 | — |
| `property-management_navigation_collapse` | 是 | — |
| `property-management_search_search` | 是 | — |
| `property-management_keyboard-shortcuts_activate` |  | — |
| `property-management_account-appearance_activate` |  | — |
| `property-management_receive-payment_activate` |  | — |
| `property-management_work-orderwork-order_create` |  | — |
| `property-management_lease_create` |  | — |
| `property-management_close_close` | 是 | — |
| `property-management_company-name_set` |  | `value`*: string, `submit`: boolean |
| `property-management_name_set` |  | `value`*: string, `submit`: boolean |
| `property-management_what-you-manage_set` |  | `value`*: string, `submit`: boolean |
| `property-management_currency_set` |  | `value`*: string, `submit`: boolean |
| `property-management_sample-portfolio_import` |  | — |
| `property-management_get-started_activate` |  | — |
| `property-management_it_dismiss` | 是 | — |
| `property-management_command-palette_show` | 是 | — |

## api-client（76 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `api-client_account_select` | 是 | `target`*: string |
| `api-client_environment_select` | 是 | `target`*: string |
| `api-client_requests-through_send` |  | `target`*: string |
| `api-client_editor_dismiss` | 是 | — |
| `api-client_collections-requests-environments_search` | 是 | — |
| `api-client_import_import` |  | — |
| `api-client_theme_activate` |  | — |
| `api-client_settings_show` | 是 | — |
| `api-client_collections_activate` |  | — |
| `api-client_environments_activate` |  | — |
| `api-client_history_activate` |  | — |
| `api-client_collection_create` |  | — |
| `api-client_filter_set` |  | `value`*: string, `submit`: boolean |
| `api-client_collection-2_create` |  | — |
| `api-client_import-2_import` |  | — |
| `api-client_sidebar_resize` |  | — |
| `api-client_request_create` |  | — |
| `api-client_open-tabs_activate` |  | — |
| `api-client_quick-look-at-variables_activate` |  | — |
| `api-client_requestctrlaltn_create` |  | — |
| `api-client_collection-3_create` |  | — |
| `api-client_import-3_import` |  | — |
| `api-client_environment_create` |  | — |
| `api-client_websocket_create` |  | — |
| `api-client_collection_run` |  | — |
| `api-client_sidebar_toggle` |  | — |
| `api-client_console_activate` |  | — |
| `api-client_cookies_activate` |  | — |
| `api-client_response-layout_activate` |  | — |
| `api-client_keyboard-shortcuts_activate` |  | — |
| `api-client_source-code-github_show` | 是 | — |
| `api-client_notification_dismiss` | 是 | — |
| `api-client_system_activate` |  | — |
| `api-client_light_activate` |  | — |
| `api-client_dark_activate` |  | — |
| `api-client_close_close` | 是 | — |
| `api-client_general_show` | 是 | — |
| `api-client_requests_show` | 是 | — |
| `api-client_about_show` | 是 | — |
| `api-client_system_toggle` |  | — |
| `api-client_light_toggle` |  | — |
| `api-client_dark_toggle` |  | — |
| `api-client_below_toggle` |  | — |
| `api-client_beside_toggle` |  | — |
| `api-client_sync-now_activate` |  | — |
| `api-client_everything_export` |  | — |
| `api-client_websocket-request_create` |  | — |
| `api-client_tabs_close` | 是 | — |
| `api-client_no-environment_activate` |  | — |
| `api-client_environment-none-environment_create` |  | — |
| `api-client_manage-environments_activate` |  | — |
| `api-client_edit_update` |  | — |
| `api-client_automatic_activate` |  | — |
| `api-client_browser-only_activate` |  | — |
| `api-client_puter-relay_activate` |  | — |
| `api-client_what-is-difference_activate` |  | — |
| `api-client_below-request_activate` |  | — |
| `api-client_beside-request_activate` |  | — |

## chess（48 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `chess_black-rook_select` | 是 | `target`*: string |
| `chess_black-knight_select` | 是 | `target`*: string |
| `chess_black-bishop_select` | 是 | `target`*: string |
| `chess_black-queen_select` | 是 | `target`*: string |
| `chess_black-king_select` | 是 | `target`*: string |
| `chess_black-pawn_select` | 是 | `target`*: string |
| `chess_empty_select` | 是 | `target`*: string |
| `chess_white-pawn_select` | 是 | `target`*: string |
| `chess_white-rook_select` | 是 | `target`*: string |
| `chess_white-knight_select` | 是 | `target`*: string |
| `chess_white-bishop_select` | 是 | `target`*: string |
| `chess_white-queen_select` | 是 | `target`*: string |
| `chess_white-king_select` | 是 | `target`*: string |
| `chess_light-theme_activate` |  | — |
| `chess_dark-theme_activate` |  | — |
| `chess_follow-system-theme_activate` |  | — |
| `chess_computer_activate` |  | — |
| `chess_pass-play_activate` |  | — |
| `chess_online_activate` |  | — |
| `chess_game-as-pgn_copy` |  | — |
| `chess_game-as-pgn-file_export` |  | — |
| `chess_go-starting-position_activate` |  | — |
| `chess_go-back-one-move_activate` |  | — |
| `chess_go-forward-one-move_activate` |  | — |
| `chess_return-current-position_activate` |  | — |
| `chess_difficulty_set` |  | `value`*: string, `submit`: boolean |
| `chess_clock_set` |  | `value`*: string, `submit`: boolean |
| `chess_play-as_set` |  | `value`*: string, `submit`: boolean |
| `chess_game_create` |  | — |
| `chess_undo_undo` |  | — |

## backgammon（45 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `backgammon_point-white-checkers_select` | 是 | `target`*: string |
| `backgammon_point-empty_select` | 是 | `target`*: string |
| `backgammon_point-black-checkers_select` | 是 | `target`*: string |
| `backgammon_light-theme_activate` |  | — |
| `backgammon_dark-theme_activate` |  | — |
| `backgammon_follow-system-theme_activate` |  | — |
| `backgammon_black-bar-empty_activate` |  | — |
| `backgammon_black-tray-empty_activate` |  | — |
| `backgammon_white-bar-empty_activate` |  | — |
| `backgammon_white-tray-empty_activate` |  | — |
| `backgammon_computer_activate` |  | — |
| `backgammon_pass-play_activate` |  | — |
| `backgammon_online_activate` |  | — |
| `backgammon_moves_activate` |  | — |
| `backgammon_game-as-mat-transcript_copy` |  | — |
| `backgammon_game-as-mat-file_export` |  | — |
| `backgammon_roll-start_activate` |  | — |
| `backgammon_difficulty_set` |  | `value`*: string, `submit`: boolean |
| `backgammon_clock_set` |  | `value`*: string, `submit`: boolean |
| `backgammon_doubling-cube_set` |  | `value`*: string, `submit`: boolean |
| `backgammon_play-as_set` |  | `value`*: string, `submit`: boolean |
| `backgammon_game_create` |  | — |
| `backgammon_turn_undo` |  | — |
| `backgammon_go-starting-position_activate` |  | — |
| `backgammon_go-back-one-turn_activate` |  | — |
| `backgammon_go-forward-one-turn_activate` |  | — |
| `backgammon_return-current-position_activate` |  | — |

## checkers（39 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `checkers_white-man_select` | 是 | `target`*: string |
| `checkers_empty_select` | 是 | `target`*: string |
| `checkers_black-man_select` | 是 | `target`*: string |
| `checkers_light-theme_activate` |  | — |
| `checkers_dark-theme_activate` |  | — |
| `checkers_follow-system-theme_activate` |  | — |
| `checkers_computer_activate` |  | — |
| `checkers_pass-play_activate` |  | — |
| `checkers_online_activate` |  | — |
| `checkers_moves_activate` |  | — |
| `checkers_game-as-pdn_copy` |  | — |
| `checkers_game-as-pdn-file_export` |  | — |
| `checkers_difficulty_set` |  | `value`*: string, `submit`: boolean |
| `checkers_clock_set` |  | `value`*: string, `submit`: boolean |
| `checkers_play-as_set` |  | `value`*: string, `submit`: boolean |
| `checkers_game_create` |  | — |
| `checkers_undo_undo` |  | — |
| `checkers_go-starting-position_activate` |  | — |
| `checkers_go-back-one-move_activate` |  | — |
| `checkers_go-forward-one-move_activate` |  | — |
| `checkers_return-current-position_activate` |  | — |

## solitaire（27 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `solitaire_klondike-draw_select` | 是 | `target`*: string |
| `solitaire_vegas-draw_select` | 是 | `target`*: string |
| `solitaire_spider-suit_select` | 是 | `target`*: string |
| `solitaire_spider-suits_select` | 是 | `target`*: string |
| `solitaire_game_select` | 是 | — |
| `solitaire_undo_undo` |  | — |
| `solitaire_powered-by-puter_show` | 是 | — |
| `solitaire_document_create` |  | — |
| `solitaire_edit_undo` |  | — |

## sudoku（57 个工具）

通用工具同上例；语义工具：

| 工具 | 只读 | 参数 |
|---|---|---|
| `sudoku_row-column-clue_select` | 是 | `target`*: string |
| `sudoku_row-column-empty_select` | 是 | `target`*: string |
| `sudoku_pencil-n_select` | 是 | `target`*: string |
| `sudoku_remaining_select` | 是 | `target`*: string |
| `sudoku_settings-row-column-empty_select` | 是 | `target`*: string |
| `sudoku_settings-row-column-clue_select` | 是 | `target`*: string |
| `sudoku_settings-remaining_select` | 是 | `target`*: string |
| `sudoku_tidy-pencil_select` | 是 | `target`*: string |
| `sudoku_puzzle-row-column-clue_select` | 是 | `target`*: string |
| `sudoku_puzzle-row-column-empty_select` | 是 | `target`*: string |
| `sudoku_puzzle-remaining_select` | 是 | `target`*: string |
| `sudoku_daily-row-column-clue_select` | 是 | `target`*: string |
| `sudoku_daily-row-column-empty_select` | 是 | `target`*: string |
| `sudoku_daily-remaining_select` | 是 | `target`*: string |
| `sudoku_powered-by-puter-row-column-clue_select` | 是 | `target`*: string |
| `sudoku_powered-by-puter-remaining_select` | 是 | `target`*: string |
| `sudoku_light-theme_activate` |  | — |
| `sudoku_dark-theme_activate` |  | — |
| `sudoku_match-system-theme_activate` |  | — |
| `sudoku_records_activate` |  | — |
| `sudoku_settings_show` | 是 | — |
| `sudoku_signed-as-local_activate` |  | — |
| `sudoku_pause_pause` |  | — |
| `sudoku_ctrlz_undo` |  | — |
| `sudoku_ctrlshiftz_redo` |  | — |
| `sudoku_erase-backspace_activate` |  | — |
| `sudoku_hint-h_activate` |  | — |
| `sudoku_next-puzzle_set` |  | `value`*: string, `submit`: boolean |
| `sudoku_puzzle_create` |  | — |
| `sudoku_daily_activate` |  | — |
| `sudoku_powered-by-puter_show` | 是 | — |
| `sudoku_check-as-i-go_toggle` |  | — |
| `sudoku_highlight-row-column-box_toggle` |  | — |
| `sudoku_highlight-matching-digits_toggle` |  | — |
| `sudoku_show-digits-remaining_toggle` |  | — |
| `sudoku_show-clock_toggle` |  | — |
| `sudoku_done_confirm` |  | — |
| `sudoku_edit_redo-shift` |  | — |
| `sudoku_edit_undo` |  | — |

## sandbox（3 个工具）

### `sandbox_check`

本机可用的轻量隔离能力（机制、Landlock ABI、网络 / 信号隔离）。CLI：foxos sandbox check。示例：foxos sandbox check --json

只读：是 · 破坏性：否 · CLI：`foxos sandbox check`

调用示例：

```json
{"name": "sandbox_check", "arguments": {}}
```

### `sandbox_run`

在轻量沙箱中运行命令：只能读写工作空间，可选禁止联网。CLI：foxos sandbox run [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}] [--max-processes MAX_PROCESSES] [--memory-mb MEMORY_MB] [--cwd CWD] [--timeout TIMEOUT]。示例：foxos sandbox run --json -- python3 build.py

只读：否 · 破坏性：否 · CLI：`foxos sandbox run`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `network` | string |  | 是否允许联网 可选：on / off |
| `read` | array |  | 额外只读路径（可重复） |
| `write` | array |  | 额外可写路径（可重复） |
| `home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写 可选：private / read / write |
| `windows_mode` | string |  | Windows：restricted 受限令牌 / appcontainer 可选：restricted / appcontainer |
| `max_processes` | integer |  | 最多进程数（Windows 作业对象） |
| `memory_mb` | integer |  | 内存上限 MB（Windows 作业对象） |
| `cwd` | string |  | 工作目录（工作空间内） |
| `timeout` | number |  | 超时秒数 |

调用示例：

```json
{"name": "sandbox_run", "arguments": {}}
```

### `sandbox_policy`

显示将生效的沙箱规则（不执行）。CLI：foxos sandbox policy [CMD...] [--network {on,off}] [--read READ] [--write WRITE] [--home {private,read,write}] [--windows-mode {restricted,appcontainer}]。示例：foxos sandbox policy --network off --json -- node agent.js

只读：是 · 破坏性：否 · CLI：`foxos sandbox policy`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `command` | array |  | 命令及参数（放在 -- 之后） |
| `network` | string |  | 是否允许联网 可选：on / off |
| `read` | array |  | 额外只读路径（可重复） |
| `write` | array |  | 额外可写路径（可重复） |
| `home` | string |  | HOME：private 私有目录 / read 真实 HOME 只读 / write 真实 HOME 可写 可选：private / read / write |
| `windows_mode` | string |  | Windows：restricted 受限令牌 / appcontainer 可选：restricted / appcontainer |

调用示例：

```json
{"name": "sandbox_policy", "arguments": {}}
```

## sheets（6 个工具）

### `sheets_create`

新建一个 .xlsx 工作簿。CLI：foxos sheets create FILE [--sheet SHEET] [--headers HEADERS] [--force]。限制：只创建 .xlsx；父目录不存在时自动创建。示例：foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales

只读：否 · 破坏性：否 · CLI：`foxos sheets create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 要创建的工作簿路径（.xlsx） |
| `sheet` | string |  | 第一个工作表的名称 |
| `headers` | array |  | 第一行表头，逗号分隔（CLI）或字符串数组（工具接口） |
| `force` | boolean |  | 文件已存在时覆盖（上一版本会保存到 .foxos/versions） |

调用示例：

```json
{"name": "sheets_create", "arguments": {"file": "…"}}
```

### `sheets_read`

读取工作表单元格（公式、图表；可选用 LibreOffice 求值）。CLI：foxos sheets read FILE [--sheet SHEET] [--range RANGE] [--computed]。限制：单次最多 20000 个单元格；--computed 需要 LibreOffice。示例：foxos sheets read sales.xlsx

只读：是 · 破坏性：否 · CLI：`foxos sheets read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `range` | string |  | A1 记法区域，如 A1:C10；默认整个已用区域 |
| `computed` | boolean |  | 用 LibreOffice 重算公式，额外返回 values（不修改原文件） |

调用示例：

```json
{"name": "sheets_read", "arguments": {"file": "…"}}
```

### `sheets_write`

写入单元格值或公式（CELL=VALUE，以 = 开头为公式）。CLI：foxos sheets write FILE CELL=VALUE... [--sheet SHEET] [--create-sheet]。限制：公式按 Excel 英文函数名写入，不在写入时校验或求值；不支持写入样式、合并单元格（阶段 0）。示例：foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135

只读：否 · 破坏性：否 · CLI：`foxos sheets write`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `cells` | object | 是 | 要写入的单元格：{"A1": "Month", "B2": 120, "B14": "=SUM(B2:B13)"}；CLI 中写成 A1=Month B2=120 B14==SUM(B2:B13)，数字自动识别，TRUE/FALSE 为布尔，空值清空单元格 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `create_sheet` | boolean |  | 工作表不存在时新建 |

调用示例：

```json
{"name": "sheets_write", "arguments": {"file": "…", "cells": {}}}
```

### `sheets_chart_create`

基于单元格区域创建原生 Excel 图表。CLI：foxos sheets chart create FILE --type {bar,line,pie} --data DATA [--categories CATEGORIES] [--title TITLE] [--sheet SHEET] [--anchor ANCHOR] [--x-title X_TITLE] [--y-title Y_TITLE] [--no-header]。限制：仅 bar / line / pie；饼图只能一个系列；图表样式、颜色暂不可配置。示例：foxos sheets chart create sales.xlsx --type bar --data B1:B13 --categories A2:A13 --title '月度销售额'

只读：否 · 破坏性：否 · CLI：`foxos sheets chart create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `type` | string | 是 | 图表类型 可选：bar / line / pie |
| `data` | string | 是 | 数据区域（按列为系列，首行默认为系列名），如 B1:B13 |
| `categories` | string |  | 分类（X 轴）区域，如 A2:A13 |
| `title` | string |  | 图表标题 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `anchor` | string |  | 图表左上角所在单元格，默认放在数据右侧 |
| `x_title` | string |  | X 轴标题（bar/line） |
| `y_title` | string |  | Y 轴标题（bar/line） |
| `no_header` | boolean |  | 数据区域首行不是系列名 |

调用示例：

```json
{"name": "sheets_chart_create", "arguments": {"file": "…", "type": "bar", "data": "…"}}
```

### `sheets_chart_list`

列出工作簿中的图表。CLI：foxos sheets chart list FILE [--sheet SHEET]。示例：foxos sheets chart list sales.xlsx --json

只读：是 · 破坏性：否 · CLI：`foxos sheets chart list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 工作簿路径 |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |

调用示例：

```json
{"name": "sheets_chart_list", "arguments": {"file": "…"}}
```

### `sheets_export`

导出为 csv / pdf / ods / xlsx（格式由输出文件扩展名决定）。CLI：foxos sheets export FILE OUTPUT [--sheet SHEET] [--force]。限制：csv 只导出一个工作表，公式导出为求值结果（需 LibreOffice，否则导出公式文本）；pdf / ods 需要 LibreOffice。示例：foxos sheets export sales.xlsx sales.csv

只读：否 · 破坏性：否 · CLI：`foxos sheets export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 源工作簿路径 |
| `output` | string | 是 | 输出路径：.csv / .pdf / .ods / .xlsx |
| `sheet` | string |  | 工作表名称，默认当前活动工作表 |
| `force` | boolean |  | 输出文件已存在时覆盖 |

调用示例：

```json
{"name": "sheets_export", "arguments": {"file": "…", "output": "…"}}
```

## slides（6 个工具）

### `slides_create`

新建一个 .pptx 演示文稿（可带标题页）。CLI：foxos slides create FILE [--title TITLE] [--subtitle SUBTITLE] [--aspect {16:9,4:3}] [--force]。示例：foxos slides create deck.pptx --title '2026 年销售分析' --subtitle '数据组'

只读：否 · 破坏性：否 · CLI：`foxos slides create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `title` | string |  | 标题页标题 |
| `subtitle` | string |  | 标题页副标题 |
| `aspect` | string |  | 页面比例 可选：16:9 / 4:3 |
| `force` | boolean |  | 已存在时覆盖 |

调用示例：

```json
{"name": "slides_create", "arguments": {"file": "…"}}
```

### `slides_read`

读取每页的版式、标题、文本、图表数据与备注。CLI：foxos slides read FILE。示例：foxos slides read deck.pptx --json

只读：是 · 破坏性：否 · CLI：`foxos slides read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |

调用示例：

```json
{"name": "slides_read", "arguments": {"file": "…"}}
```

### `slides_add`

追加一页（标题 + 要点 / 图片 / 备注）。CLI：foxos slides add FILE [--title TITLE] [--bullet BULLET] [--layout {title,title-content,section,two-content,title-only,blank}] [--image IMAGE] [--notes NOTES]。示例：foxos slides add deck.pptx -t 全年概况 -b '销售额 2013 万元' -b '同比增长 12%'

只读：否 · 破坏性：否 · CLI：`foxos slides add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `title` | string |  | 页面标题 |
| `bullet` | array |  | 要点，可重复：--bullet 一 --bullet 二 |
| `layout` | string |  | 版式 可选：title / title-content / section / two-content / title-only / blank |
| `image` | string |  | 插入图片（工作空间内 png/jpg） |
| `notes` | string |  | 演讲者备注 |

调用示例：

```json
{"name": "slides_add", "arguments": {"file": "…"}}
```

### `slides_chart_add`

插入原生 PowerPoint 图表（默认新建一页）。CLI：foxos slides chart add FILE --type {bar,line,pie} --categories CATEGORIES --values VALUES [--slide SLIDE] [--series-name SERIES_NAME] [--title TITLE]。示例：foxos slides chart add deck.pptx --type bar -c Q1,Q2,Q3,Q4 -v 405,428,547,633 --title 季度销售额

只读：否 · 破坏性：否 · CLI：`foxos slides chart add`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `type` | string | 是 | 图表类型 可选：bar / line / pie |
| `categories` | array | 是 | 分类，逗号分隔 |
| `values` | array | 是 | 数值，逗号分隔，与分类一一对应 |
| `slide` | integer |  | 插入到已有的第 N 页（从 1 开始）；不填则新建一页 |
| `series_name` | string |  | 系列名称 |
| `title` | string |  | 新建页时的页面标题 |

调用示例：

```json
{"name": "slides_chart_add", "arguments": {"file": "…", "type": "bar", "categories": [], "values": []}}
```

### `slides_replace`

查找并替换所有页中的文本。CLI：foxos slides replace FILE --find FIND --replace REPLACE。限制：只在同一个文本 run 内匹配。示例：foxos slides replace deck.pptx --find 2025 --replace 2026

只读：否 · 破坏性：否 · CLI：`foxos slides replace`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `find` | string | 是 | 要查找的文本 |
| `replace` | string | 是 | 替换为 |

调用示例：

```json
{"name": "slides_replace", "arguments": {"file": "…", "find": "…", "replace": "…"}}
```

### `slides_export`

导出为 pdf / odp。CLI：foxos slides export FILE OUTPUT [--force]。限制：需要 LibreOffice。示例：foxos slides export deck.pptx deck.pdf

只读：否 · 破坏性：否 · CLI：`foxos slides export`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | 是 | 演示文稿路径（.pptx） |
| `output` | string | 是 | 输出路径 |
| `force` | boolean |  | 输出已存在时覆盖 |

调用示例：

```json
{"name": "slides_export", "arguments": {"file": "…", "output": "…"}}
```

## workspace（1 个工具）

### `workspace_info`

显示工作空间根目录、审计日志位置与文件数。CLI：foxos workspace info。示例：foxos workspace info --json

只读：是 · 破坏性：否 · CLI：`foxos workspace info`

调用示例：

```json
{"name": "workspace_info", "arguments": {}}
```

## files（8 个工具）

### `files_list`

列出目录内容（默认工作空间根目录）。CLI：foxos files list [PATH] [--recursive] [--hidden]。示例：foxos files list

只读：是 · 破坏性：否 · CLI：`foxos files list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string |  | 目录（工作空间内），默认根目录 |
| `recursive` | boolean |  | 递归列出所有文件 |
| `hidden` | boolean |  | 包含以 . 开头的文件 |

调用示例：

```json
{"name": "files_list", "arguments": {}}
```

### `files_read`

读取 UTF-8 文本文件。CLI：foxos files read PATH。限制：上限 5 MB；二进制与办公文件请用对应应用命令。示例：foxos files read notes.md

只读：是 · 破坏性：否 · CLI：`foxos files read`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |

调用示例：

```json
{"name": "files_read", "arguments": {"path": "…"}}
```

### `files_write`

写入 UTF-8 文本文件（原子保存，覆盖前保留上一版）。CLI：foxos files write PATH --content CONTENT [--expect-mtime EXPECT_MTIME] [--force]。示例：foxos files write notes.md --content '# 标题'

只读：否 · 破坏性：否 · CLI：`foxos files write`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件路径 |
| `content` | string | 是 | 文件内容；CLI 可用 --content-stdin 从标准输入读取 |
| `expect_mtime` | number |  | 乐观并发检查：文件当前修改时间必须等于该值，否则 CONFLICT |
| `force` | boolean |  | 目标已存在时覆盖 |

调用示例：

```json
{"name": "files_write", "arguments": {"path": "…", "content": "…"}}
```

### `files_mkdir`

新建文件夹（含父目录）。CLI：foxos files mkdir PATH。示例：foxos files mkdir reports/2026

只读：否 · 破坏性：否 · CLI：`foxos files mkdir`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 文件夹路径 |

调用示例：

```json
{"name": "files_mkdir", "arguments": {"path": "…"}}
```

### `files_rename`

重命名或移动文件 / 文件夹。CLI：foxos files rename SOURCE TARGET [--force]。示例：foxos files rename draft.md final.md

只读：否 · 破坏性：否 · CLI：`foxos files rename`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `source` | string | 是 | 原路径 |
| `target` | string | 是 | 新路径 |
| `force` | boolean |  | 目标已存在时覆盖 |

调用示例：

```json
{"name": "files_rename", "arguments": {"source": "…", "target": "…"}}
```

### `files_delete`

删除文件或文件夹（移入回收站，可恢复）。CLI：foxos files delete PATH。限制：移入 .foxos/trash/，用 foxos files restore 恢复。示例：foxos files delete old.csv

只读：否 · 破坏性：是 · CLI：`foxos files delete`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `path` | string | 是 | 要删除的路径 |

调用示例：

```json
{"name": "files_delete", "arguments": {"path": "…"}}
```

### `files_restore`

从回收站恢复。CLI：foxos files restore TRASH_ID [--force]。示例：foxos files restore 20261110T2051-ab12cd

只读：否 · 破坏性：否 · CLI：`foxos files restore`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `trash_id` | string | 是 | 回收站条目 ID（files delete 返回，或 files trash 查看） |
| `force` | boolean |  | 目标已存在时覆盖 |

调用示例：

```json
{"name": "files_restore", "arguments": {"trash_id": "…"}}
```

### `files_trash`

列出回收站。CLI：foxos files trash。示例：foxos files trash --json

只读：是 · 破坏性：否 · CLI：`foxos files trash`

调用示例：

```json
{"name": "files_trash", "arguments": {}}
```

## audit（1 个工具）

### `audit_tail`

查看最近的审计记录。CLI：foxos audit tail [--limit LIMIT] [--filter-agent AGENT] [--command COMMAND]。限制：查询本身不写入审计日志。示例：foxos audit tail -n 50

只读：是 · 破坏性：否 · CLI：`foxos audit tail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer |  | 返回条数 |
| `agent` | string |  | 只看某个智能体 |
| `command` | string |  | 按命令前缀过滤，如 sheets.write |

调用示例：

```json
{"name": "audit_tail", "arguments": {}}
```

## queue（2 个工具）

### `queue_create`

把一个任务目标加入队列。CLI：foxos queue create GOAL。限制：只记录任务；执行由 ACP 智能体会话完成。示例：foxos queue create '根据 sales.xlsx 制作分析报告'

只读：否 · 破坏性：否 · CLI：`foxos queue create`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `goal` | string | 是 | 任务目标（自然语言） |

调用示例：

```json
{"name": "queue_create", "arguments": {"goal": "…"}}
```

### `queue_list`

列出任务队列。CLI：foxos queue list [--limit LIMIT]。示例：foxos queue list --json

只读：是 · 破坏性：否 · CLI：`foxos queue list`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer |  | 返回条数 |

调用示例：

```json
{"name": "queue_list", "arguments": {}}
```

## control（3 个工具）

### `control_status`

查看是否处于人工接管（暂停）状态。CLI：foxos control status。限制：查询本身不写入审计日志。示例：foxos control status --json

只读：是 · 破坏性：否 · CLI：`foxos control status`

调用示例：

```json
{"name": "control_status", "arguments": {}}
```

### `control_pause`

人工接管：暂停所有智能体的写操作。CLI：foxos control pause [--reason REASON]。限制：只有 human 身份可以执行；身份由调用方声明（--agent），属于应用层约束。示例：foxos control pause --reason '我来改第 3 页数据'

只读：否 · 破坏性：否 · CLI：`foxos control pause`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reason` | string |  | 暂停原因（写入状态与审计） |

调用示例：

```json
{"name": "control_pause", "arguments": {}}
```

### `control_resume`

结束人工接管，恢复智能体写操作。CLI：foxos control resume。限制：只有 human 身份可以执行。示例：foxos control resume

只读：否 · 破坏性：否 · CLI：`foxos control resume`

调用示例：

```json
{"name": "control_resume", "arguments": {}}
```

