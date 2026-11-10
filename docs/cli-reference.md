# foxos 命令参考

> 本文件由 `python scripts/gen_cli_docs.py` 从命令注册表生成，与 `foxos help --json` 同源，请勿手改。

## 通用约定

- **invocation**：foxos [全局选项] <app> <command> [参数]；全局选项可放在任意位置
- **global_options**
  - `--json`：以 JSON 输出：成功 {ok:true, command, result}，失败 {ok:false, command, error:{code, exit_code, message, hint}}
  - `--workspace PATH`：工作空间根目录（默认 $FOXOS_WORKSPACE 或 ~/FoxOS/workspace）
  - `--agent NAME`：调用者身份，写入审计日志（默认 $FOXOS_AGENT 或 human）
  - `--task ID`：关联的任务 ID（默认 $FOXOS_TASK）
  - `--lock-wait SECONDS`：目标文件被锁时最多等待的秒数（默认 0，立即返回 LOCKED）
- **exit_codes**
  - 0：OK：成功
  - 1：ERROR：未分类错误或内部错误
  - 2：USAGE：参数错误
  - 3：NOT_FOUND：文件、工作表或命令不存在
  - 4：PERMISSION_DENIED：路径越出工作空间或访问保留目录
  - 5：LOCKED：目标文件正被其他写入者锁定
  - 6：DEPENDENCY_MISSING：缺少外部依赖（如 LibreOffice）
  - 7：CONFLICT：目标已存在等冲突（可用 --force 覆盖时会提示）
  - 8：PAUSED：人工接管中，智能体的写操作被暂停
- **paths**：所有路径相对于工作空间根目录；越出工作空间或访问 .foxos/ 返回 PERMISSION_DENIED（4）
- **formulas**：单元格值以 = 开头即为 Excel 公式，如 =SUM(B2:B13)；以 ' 开头强制为文本
- **audit**：每次调用（含失败与拒绝）都追加到 <workspace>/.foxos/audit.jsonl；只读自省命令 audit tail、control status 成功时不记录
- **tool_names**：工具接口名 = 命令 ID 把 . 换成 _，如 sheets.chart.create → sheets_chart_create

## docs — 文档：读写标准 .docx（段落、标题、列表、表格），替换文本与导出

基于 python-docx 读写 Word 2007+ (.docx)。样式名使用 Word 内置英文样式名，如 Heading 1、List Bullet。

限制：

- 只读写 .docx；.doc / .odt 输入暂不支持
- 图片、页眉页脚、批注暂不可编辑
- 替换在段落内进行，跨段落的文本不会匹配

### `foxos docs create`

新建一个 .docx 文档

```text
foxos docs create FILE [--title TITLE] [--force]
```

工具接口名：`docs_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `title` | `--title` | string |  | 文档标题（写成 Title 样式的第一段，并写入文档属性） |
| `force` | `--force / -f` | boolean |  | 已存在时覆盖 |

示例：

```bash
foxos docs create report.docx --title '2026 年销售分析'
```

### `foxos docs read`

读取文档段落（含样式名）、表格与字数统计

```text
foxos docs read FILE
```

工具接口名：`docs_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（read） |

示例：

```bash
foxos docs read report.docx --json
```

### `foxos docs append`

在文档末尾追加段落、标题或表格

```text
foxos docs append FILE [TEXT...] [--style STYLE] [--heading HEADING] [--table TABLE]
```

工具接口名：`docs_append` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `text` | `TEXT` | array |  | 要追加的段落，每个参数一段 |
| `style` | `--style` | string |  | 段落样式（Word 内置英文名），如 List Bullet、Quote |
| `heading` | `--heading` | integer |  | 作为标题追加：0=Title，1–9=Heading 1–9 |
| `table` | `--table` | array |  | 追加表格：二维数组；CLI 中用 --table-json |

示例：

```bash
foxos docs append report.docx '一、总体情况' --heading 1
foxos docs append report.docx '全年销售额 2013 万元。' '同比增长 12%。'
foxos docs append report.docx '要点一' '要点二' --style 'List Bullet'
foxos docs append report.docx --table-json '[["月份","销售额"],["1月",120]]'
```

### `foxos docs replace`

查找并替换文本（正文与表格）

```text
foxos docs replace FILE --find FIND --replace REPLACE
```

工具接口名：`docs_replace` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（write） |
| `find` | `--find` | string | 是 | 要查找的文本 |
| `replace` | `--replace` | string | 是 | 替换为 |

示例：

```bash
foxos docs replace report.docx --find 2025 --replace 2026
```

### `foxos docs export`

导出为 pdf / odt / html / txt / md（由扩展名决定）

```text
foxos docs export FILE OUTPUT [--force]
```

工具接口名：`docs_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 文档路径（.docx）；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 输出已存在时覆盖 |

示例：

```bash
foxos docs export report.docx report.pdf
foxos docs export report.docx report.md
```

限制：

- pdf / odt / html 需要 LibreOffice

## env — 狐狸OS 环境

自研隔离环境：每个环境有自己的根文件系统、进程、主机名和资源限制；工作空间按规则挂载到 /workspace。

限制：

- Linux 后端无特权运行（用户命名空间）；cgroup 不可委派时用 rlimit 限制
- Windows 使用系统自带 WSL2；macOS 使用 Virtualization.framework

### `foxos env images`

列出可用镜像（官方发行版 rootfs）与本地镜像

```text
foxos env images
```

工具接口名：`env_images` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos env images --json
```

### `foxos env pull`

下载镜像并校验 sha256（目录 ID、https 地址或 .foxenv 文件）

```text
foxos env pull IMAGE [--sha256 SHA256]
```

工具接口名：`env_pull` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `image` | `IMAGE` | string | 是 | 镜像 |
| `sha256` | `--sha256` | string |  | 期望的 sha256（自定义地址时建议提供） |

示例：

```bash
foxos env pull alpine-3.20
foxos env pull ubuntu-24.04
```

### `foxos env create`

创建环境

```text
foxos env create NAME [--image IMAGE] [--network {host,none}] [--workspace-mode {rw,ro,none}] [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS]
```

工具接口名：`env_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `image` | `--image` | string |  | 镜像 ID；默认 alpine-3.20 |
| `network` | `--network` | string |  | 网络：host（共享宿主网络）或 none（只有回环）；可选：host / none；默认 host |
| `workspace_mode` | `--workspace-mode` | string |  | 工作空间挂载方式；可选：rw / ro / none；默认 rw |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限（MB） |
| `cpus` | `--cpus` | number |  | CPU 上限（核，需 cgroup） |
| `pids` | `--pids` | integer |  | 进程数上限 |

示例：

```bash
foxos env create dev
foxos env create sandbox --image ubuntu-24.04 --network none --workspace-mode ro --memory-mb 1024
```

### `foxos env list`

列出环境及状态

```text
foxos env list
```

工具接口名：`env_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos env list --json
```

### `foxos env info`

环境详情（配置、快照、资源使用）

```text
foxos env info NAME
```

工具接口名：`env_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env info dev --json
```

### `foxos env start`

启动环境

```text
foxos env start NAME
```

工具接口名：`env_start` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env start dev
```

### `foxos env stop`

停止环境

```text
foxos env stop NAME [--timeout TIMEOUT]
```

工具接口名：`env_stop` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `timeout` | `--timeout` | number |  | 等待秒数，超时强制结束；默认 5.0 |

示例：

```bash
foxos env stop dev
```

### `foxos env restart`

重启环境

```text
foxos env restart NAME
```

工具接口名：`env_restart` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env restart dev
```

### `foxos env exec`

在环境中执行命令（默认工作目录 /workspace）

```text
foxos env exec NAME [CMD...] [--cwd CWD] [--timeout TIMEOUT]
```

工具接口名：`env_exec` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `command` | `CMD` | array |  | 命令及参数（放在 -- 之后） |
| `cwd` | `--cwd` | string |  | 环境内工作目录；默认 /workspace |
| `timeout` | `--timeout` | number |  | 超时秒数；默认 600 |

示例：

```bash
foxos env exec dev -- uname -a
foxos env exec dev -- sh -c 'apk add python3 && python3 -V' --json
```

### `foxos env shell`

进入环境的交互式 shell

```text
foxos env shell NAME
```

工具接口名：`env_shell` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env shell dev
```

### `foxos env clone`

克隆环境（复制可写层与设置）

```text
foxos env clone NAME NEW_NAME
```

工具接口名：`env_clone` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `new_name` | `NEW_NAME` | string | 是 | 新环境名 |

示例：

```bash
foxos env clone dev dev-copy
```

### `foxos env snapshot`

为停止的环境创建快照

```text
foxos env snapshot NAME [--label LABEL]
```

工具接口名：`env_snapshot` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `label` | `--label` | string |  | 说明 |

示例：

```bash
foxos env snapshot dev --label 装好依赖
```

### `foxos env restore`

恢复到快照

```text
foxos env restore NAME SNAPSHOT
```

工具接口名：`env_restore` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `snapshot` | `SNAPSHOT` | string | 是 | 快照 ID |

示例：

```bash
foxos env restore dev 20261110T213000
```

### `foxos env export`

导出为 .foxenv 镜像（tar + zstd + manifest + sha256）

```text
foxos env export NAME --out OUT
```

工具接口名：`env_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `out` | `--out` | string | 是 | 输出文件（工作空间内）；工作空间路径（write） |

示例：

```bash
foxos env export dev --out backups/dev.foxenv
```

### `foxos env import`

从 .foxenv 镜像导入为新环境

```text
foxos env import FILE --name NAME
```

工具接口名：`env_import` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | .foxenv 文件（工作空间内）；工作空间路径（read） |
| `name` | `--name` | string | 是 | 新环境名 |

示例：

```bash
foxos env import backups/dev.foxenv --name dev2
```

### `foxos env delete`

删除环境（不删除镜像与工作空间）

```text
foxos env delete NAME
```

工具接口名：`env_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |

示例：

```bash
foxos env delete dev-copy
```

### `foxos env mount`

添加 / 移除宿主目录挂载

```text
foxos env mount NAME --source SOURCE --target TARGET [--readonly] [--remove]
```

工具接口名：`env_mount` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `source` | `--source` | string | 是 | 宿主路径 |
| `target` | `--target` | string | 是 | 环境内路径 |
| `readonly` | `--readonly` | boolean |  | 只读 |
| `remove` | `--remove` | boolean |  | 移除该挂载 |

示例：

```bash
foxos env mount dev --source ~/datasets --target /data --readonly
```

### `foxos env limits`

设置资源限制、网络与工作空间权限

```text
foxos env limits NAME [--memory-mb MEMORY_MB] [--cpus CPUS] [--pids PIDS] [--network {host,none}] [--workspace-mode {rw,ro,none}]
```

工具接口名：`env_limits` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `memory_mb` | `--memory-mb` | integer |  | 内存上限 MB（0 取消） |
| `cpus` | `--cpus` | number |  | CPU 上限（0 取消） |
| `pids` | `--pids` | integer |  | 进程数上限（0 取消） |
| `network` | `--network` | string |  | 网络；可选：host / none |
| `workspace_mode` | `--workspace-mode` | string |  | 工作空间挂载；可选：rw / ro / none |

示例：

```bash
foxos env limits dev --memory-mb 2048 --pids 512
foxos env limits dev --network none
```

### `foxos env stats`

资源使用（进程数、CPU 时间、内存、磁盘）

```text
foxos env stats [NAME]
```

工具接口名：`env_stats` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string |  | 环境名（缺省为全部） |

示例：

```bash
foxos env stats --json
```

### `foxos env logs`

环境日志

```text
foxos env logs NAME [--lines LINES]
```

工具接口名：`env_logs` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `lines` | `--lines / -n` | integer |  | 行数；默认 100 |

示例：

```bash
foxos env logs dev -n 50
```

### `foxos env action add`

添加自定义操作（支持 ${env} ${image} ${workspace} ${host_workspace} ${hostname} 变量）

```text
foxos env action add NAME ACTION --command COMMAND
```

工具接口名：`env_action_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `action` | `ACTION` | string | 是 | 操作名 |
| `command` | `--command` | string | 是 | 环境内执行的 shell 命令 |

示例：

```bash
foxos env action add dev test --command 'cd ${workspace} && make test'
```

### `foxos env action run`

运行自定义操作

```text
foxos env action run NAME ACTION
```

工具接口名：`env_action_run` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `name` | `NAME` | string | 是 | 环境名 |
| `action` | `ACTION` | string | 是 | 操作名 |

示例：

```bash
foxos env action run dev test --json
```

## everything — Everything 应用

上游 HeyPuter/everything 的 51 个应用：从上游源码在本机构建安装，在狐狸OS 中本地运行（不连接 puter.com）。

限制：

- AGPL-3.0 应用作为独立组件在安装时从上游获取，狐狸OS 不分发其源码或修改版

### `foxos everything list`

列出 51 个 Everything 应用（分组、许可证、安装状态、操作数）

```text
foxos everything list [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--installed]
```

工具接口名：`everything_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `group` | `--group` | string |  | 只看某个分组；可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `installed_only` | `--installed` | boolean |  | 只列出已安装的 |

示例：

```bash
foxos everything list
foxos everything list --group office --json
```

### `foxos everything info`

查看一个应用的详情、许可证与可用命令

```text
foxos everything info APP
```

工具接口名：`everything_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |

示例：

```bash
foxos everything info tasks --json
```

### `foxos everything install`

从上游源码在本机构建并安装应用（固定提交，含许可证声明）

```text
foxos everything install [APP...] [--all] [--group {office,collaboration,creative,engineering,productivity,finance,business,developer,games}] [--source SOURCE] [--force]
```

工具接口名：`everything_install` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `apps` | `APP` | array |  | 应用 ID |
| `all` | `--all` | boolean |  | 安装全部 51 个 |
| `group` | `--group` | string |  | 安装整个分组；可选：office / collaboration / creative / engineering / productivity / finance / business / developer / games |
| `source` | `--source` | string |  | 使用本地上游仓库目录（离线 / 镜像），默认从 GitHub 获取 |
| `force` | `--force / -f` | boolean |  | 已安装也重新构建 |

示例：

```bash
foxos everything install tasks chess
foxos everything install --group games
foxos everything install --all
```

限制：

- 需要 git、Node.js 22.12+ 与 npm；每个应用构建约 2–20 秒（不含下载）

### `foxos everything uninstall`

卸载应用（保留工作空间中的数据）

```text
foxos everything uninstall APP
```

工具接口名：`everything_uninstall` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `app` | `APP` | string | 是 | 应用 ID（foxos everything list 查看） |

示例：

```bash
foxos everything uninstall chess
```

## spreadsheet — Spreadsheet

办公 · 替代 Microsoft Excel, Google Sheets, Apple Numbers。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos spreadsheet app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos spreadsheet app open [--file FILE] [--headless]
```

工具接口名：`spreadsheet_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos spreadsheet app open
foxos spreadsheet app open --headless --json
```

### `foxos spreadsheet app close`

关闭应用实例

```text
foxos spreadsheet app close
```

工具接口名：`spreadsheet_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet app close --json
```

### `foxos spreadsheet app status`

应用是否已安装、是否在运行

```text
foxos spreadsheet app status
```

工具接口名：`spreadsheet_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet app status --json
```

### `foxos spreadsheet file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos spreadsheet file open PATH
```

工具接口名：`spreadsheet_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos spreadsheet file open X
```

### `foxos spreadsheet ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos spreadsheet ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`spreadsheet_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos spreadsheet ui snapshot --json
```

### `foxos spreadsheet ui text`

读取界面上的可见文本

```text
foxos spreadsheet ui text
```

工具接口名：`spreadsheet_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet ui text --json
```

### `foxos spreadsheet ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos spreadsheet ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`spreadsheet_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos spreadsheet ui click --ref e12
foxos spreadsheet ui click --name Settings
```

### `foxos spreadsheet ui type`

向控件输入文本（真实输入事件）

```text
foxos spreadsheet ui type TEXT [--ref REF] [--clear]
```

工具接口名：`spreadsheet_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos spreadsheet ui type 'hello' --ref e5
```

### `foxos spreadsheet ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos spreadsheet ui set --ref REF --value VALUE
```

工具接口名：`spreadsheet_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos spreadsheet ui set 
```

### `foxos spreadsheet ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos spreadsheet ui press KEY [--ref REF]
```

工具接口名：`spreadsheet_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos spreadsheet ui press mod+z
```

### `foxos spreadsheet ui screenshot`

应用窗口截图（PNG）

```text
foxos spreadsheet ui screenshot [--out OUT]
```

工具接口名：`spreadsheet_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos spreadsheet ui screenshot --json
```

### `foxos spreadsheet data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos spreadsheet data list [PATTERN]
```

工具接口名：`spreadsheet_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos spreadsheet data list --json
```

### `foxos spreadsheet data get`

读取应用保存的一项数据

```text
foxos spreadsheet data get KEY
```

工具接口名：`spreadsheet_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos spreadsheet data get X
```

### `foxos spreadsheet module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos spreadsheet module list
```

工具接口名：`spreadsheet_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet module list --json
```

### `foxos spreadsheet module read`

读取应用模块中的值（如 store 状态）

```text
foxos spreadsheet module read TARGET
```

工具接口名：`spreadsheet_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos spreadsheet module read X
```

### `foxos spreadsheet module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos spreadsheet module call TARGET [--args ARGS]
```

工具接口名：`spreadsheet_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos spreadsheet module call X
```

### `foxos spreadsheet op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos spreadsheet op list
```

工具接口名：`spreadsheet_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos spreadsheet op list --json
```

## documents — Documents

办公 · 替代 Microsoft Word, Google Docs, Apple Pages。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos documents app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos documents app open [--file FILE] [--headless]
```

工具接口名：`documents_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos documents app open
foxos documents app open --headless --json
```

### `foxos documents app close`

关闭应用实例

```text
foxos documents app close
```

工具接口名：`documents_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos documents app close --json
```

### `foxos documents app status`

应用是否已安装、是否在运行

```text
foxos documents app status
```

工具接口名：`documents_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos documents app status --json
```

### `foxos documents file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos documents file open PATH
```

工具接口名：`documents_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos documents file open X
```

### `foxos documents ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos documents ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`documents_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos documents ui snapshot --json
```

### `foxos documents ui text`

读取界面上的可见文本

```text
foxos documents ui text
```

工具接口名：`documents_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos documents ui text --json
```

### `foxos documents ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos documents ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`documents_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos documents ui click --ref e12
foxos documents ui click --name Settings
```

### `foxos documents ui type`

向控件输入文本（真实输入事件）

```text
foxos documents ui type TEXT [--ref REF] [--clear]
```

工具接口名：`documents_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos documents ui type 'hello' --ref e5
```

### `foxos documents ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos documents ui set --ref REF --value VALUE
```

工具接口名：`documents_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos documents ui set 
```

### `foxos documents ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos documents ui press KEY [--ref REF]
```

工具接口名：`documents_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos documents ui press mod+z
```

### `foxos documents ui screenshot`

应用窗口截图（PNG）

```text
foxos documents ui screenshot [--out OUT]
```

工具接口名：`documents_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos documents ui screenshot --json
```

### `foxos documents data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos documents data list [PATTERN]
```

工具接口名：`documents_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos documents data list --json
```

### `foxos documents data get`

读取应用保存的一项数据

```text
foxos documents data get KEY
```

工具接口名：`documents_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos documents data get X
```

### `foxos documents module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos documents module list
```

工具接口名：`documents_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos documents module list --json
```

### `foxos documents module read`

读取应用模块中的值（如 store 状态）

```text
foxos documents module read TARGET
```

工具接口名：`documents_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos documents module read X
```

### `foxos documents module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos documents module call TARGET [--args ARGS]
```

工具接口名：`documents_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos documents module call X
```

### `foxos documents op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos documents op list
```

工具接口名：`documents_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos documents op list --json
```

## presentation — Presentation

办公 · 替代 Microsoft PowerPoint, Google Slides, Apple Keynote。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos presentation app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos presentation app open [--file FILE] [--headless]
```

工具接口名：`presentation_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos presentation app open
foxos presentation app open --headless --json
```

### `foxos presentation app close`

关闭应用实例

```text
foxos presentation app close
```

工具接口名：`presentation_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos presentation app close --json
```

### `foxos presentation app status`

应用是否已安装、是否在运行

```text
foxos presentation app status
```

工具接口名：`presentation_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos presentation app status --json
```

### `foxos presentation file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos presentation file open PATH
```

工具接口名：`presentation_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos presentation file open X
```

### `foxos presentation ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos presentation ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`presentation_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos presentation ui snapshot --json
```

### `foxos presentation ui text`

读取界面上的可见文本

```text
foxos presentation ui text
```

工具接口名：`presentation_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos presentation ui text --json
```

### `foxos presentation ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos presentation ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`presentation_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos presentation ui click --ref e12
foxos presentation ui click --name Settings
```

### `foxos presentation ui type`

向控件输入文本（真实输入事件）

```text
foxos presentation ui type TEXT [--ref REF] [--clear]
```

工具接口名：`presentation_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos presentation ui type 'hello' --ref e5
```

### `foxos presentation ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos presentation ui set --ref REF --value VALUE
```

工具接口名：`presentation_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos presentation ui set 
```

### `foxos presentation ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos presentation ui press KEY [--ref REF]
```

工具接口名：`presentation_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos presentation ui press mod+z
```

### `foxos presentation ui screenshot`

应用窗口截图（PNG）

```text
foxos presentation ui screenshot [--out OUT]
```

工具接口名：`presentation_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos presentation ui screenshot --json
```

### `foxos presentation data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos presentation data list [PATTERN]
```

工具接口名：`presentation_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos presentation data list --json
```

### `foxos presentation data get`

读取应用保存的一项数据

```text
foxos presentation data get KEY
```

工具接口名：`presentation_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos presentation data get X
```

### `foxos presentation module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos presentation module list
```

工具接口名：`presentation_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos presentation module list --json
```

### `foxos presentation module read`

读取应用模块中的值（如 store 状态）

```text
foxos presentation module read TARGET
```

工具接口名：`presentation_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos presentation module read X
```

### `foxos presentation module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos presentation module call TARGET [--args ARGS]
```

工具接口名：`presentation_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos presentation module call X
```

### `foxos presentation op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos presentation op list
```

工具接口名：`presentation_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos presentation op list --json
```

## whiteboard — Whiteboard

办公 · 替代 Miro, Microsoft Whiteboard, FigJam。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos whiteboard app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos whiteboard app open [--file FILE] [--headless]
```

工具接口名：`whiteboard_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos whiteboard app open
foxos whiteboard app open --headless --json
```

### `foxos whiteboard app close`

关闭应用实例

```text
foxos whiteboard app close
```

工具接口名：`whiteboard_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos whiteboard app close --json
```

### `foxos whiteboard app status`

应用是否已安装、是否在运行

```text
foxos whiteboard app status
```

工具接口名：`whiteboard_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos whiteboard app status --json
```

### `foxos whiteboard file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos whiteboard file open PATH
```

工具接口名：`whiteboard_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos whiteboard file open X
```

### `foxos whiteboard ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos whiteboard ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`whiteboard_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos whiteboard ui snapshot --json
```

### `foxos whiteboard ui text`

读取界面上的可见文本

```text
foxos whiteboard ui text
```

工具接口名：`whiteboard_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos whiteboard ui text --json
```

### `foxos whiteboard ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos whiteboard ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`whiteboard_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos whiteboard ui click --ref e12
foxos whiteboard ui click --name Settings
```

### `foxos whiteboard ui type`

向控件输入文本（真实输入事件）

```text
foxos whiteboard ui type TEXT [--ref REF] [--clear]
```

工具接口名：`whiteboard_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos whiteboard ui type 'hello' --ref e5
```

### `foxos whiteboard ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos whiteboard ui set --ref REF --value VALUE
```

工具接口名：`whiteboard_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos whiteboard ui set 
```

### `foxos whiteboard ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos whiteboard ui press KEY [--ref REF]
```

工具接口名：`whiteboard_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos whiteboard ui press mod+z
```

### `foxos whiteboard ui screenshot`

应用窗口截图（PNG）

```text
foxos whiteboard ui screenshot [--out OUT]
```

工具接口名：`whiteboard_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos whiteboard ui screenshot --json
```

### `foxos whiteboard data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos whiteboard data list [PATTERN]
```

工具接口名：`whiteboard_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos whiteboard data list --json
```

### `foxos whiteboard data get`

读取应用保存的一项数据

```text
foxos whiteboard data get KEY
```

工具接口名：`whiteboard_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos whiteboard data get X
```

### `foxos whiteboard module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos whiteboard module list
```

工具接口名：`whiteboard_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos whiteboard module list --json
```

### `foxos whiteboard module read`

读取应用模块中的值（如 store 状态）

```text
foxos whiteboard module read TARGET
```

工具接口名：`whiteboard_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos whiteboard module read X
```

### `foxos whiteboard module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos whiteboard module call TARGET [--args ARGS]
```

工具接口名：`whiteboard_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos whiteboard module call X
```

### `foxos whiteboard op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos whiteboard op list
```

工具接口名：`whiteboard_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos whiteboard op list --json
```

## pdf — PDF

办公 · 替代 Adobe Acrobat, PDF Expert。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos pdf app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos pdf app open [--file FILE] [--headless]
```

工具接口名：`pdf_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos pdf app open
foxos pdf app open --headless --json
```

### `foxos pdf app close`

关闭应用实例

```text
foxos pdf app close
```

工具接口名：`pdf_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pdf app close --json
```

### `foxos pdf app status`

应用是否已安装、是否在运行

```text
foxos pdf app status
```

工具接口名：`pdf_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pdf app status --json
```

### `foxos pdf file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos pdf file open PATH
```

工具接口名：`pdf_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos pdf file open X
```

### `foxos pdf ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos pdf ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`pdf_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos pdf ui snapshot --json
```

### `foxos pdf ui text`

读取界面上的可见文本

```text
foxos pdf ui text
```

工具接口名：`pdf_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pdf ui text --json
```

### `foxos pdf ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos pdf ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`pdf_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos pdf ui click --ref e12
foxos pdf ui click --name Settings
```

### `foxos pdf ui type`

向控件输入文本（真实输入事件）

```text
foxos pdf ui type TEXT [--ref REF] [--clear]
```

工具接口名：`pdf_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos pdf ui type 'hello' --ref e5
```

### `foxos pdf ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos pdf ui set --ref REF --value VALUE
```

工具接口名：`pdf_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos pdf ui set 
```

### `foxos pdf ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos pdf ui press KEY [--ref REF]
```

工具接口名：`pdf_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos pdf ui press mod+z
```

### `foxos pdf ui screenshot`

应用窗口截图（PNG）

```text
foxos pdf ui screenshot [--out OUT]
```

工具接口名：`pdf_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos pdf ui screenshot --json
```

### `foxos pdf data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos pdf data list [PATTERN]
```

工具接口名：`pdf_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos pdf data list --json
```

### `foxos pdf data get`

读取应用保存的一项数据

```text
foxos pdf data get KEY
```

工具接口名：`pdf_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos pdf data get X
```

### `foxos pdf module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos pdf module list
```

工具接口名：`pdf_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pdf module list --json
```

### `foxos pdf module read`

读取应用模块中的值（如 store 状态）

```text
foxos pdf module read TARGET
```

工具接口名：`pdf_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos pdf module read X
```

### `foxos pdf module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos pdf module call TARGET [--args ARGS]
```

工具接口名：`pdf_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos pdf module call X
```

### `foxos pdf op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos pdf op list
```

工具接口名：`pdf_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pdf op list --json
```

## notes — Notes

办公 · 替代 Microsoft OneNote, Evernote, Apple Notes。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos notes app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos notes app open [--file FILE] [--headless]
```

工具接口名：`notes_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos notes app open
foxos notes app open --headless --json
```

### `foxos notes app close`

关闭应用实例

```text
foxos notes app close
```

工具接口名：`notes_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos notes app close --json
```

### `foxos notes app status`

应用是否已安装、是否在运行

```text
foxos notes app status
```

工具接口名：`notes_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos notes app status --json
```

### `foxos notes file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos notes file open PATH
```

工具接口名：`notes_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos notes file open X
```

### `foxos notes ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos notes ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`notes_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos notes ui snapshot --json
```

### `foxos notes ui text`

读取界面上的可见文本

```text
foxos notes ui text
```

工具接口名：`notes_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos notes ui text --json
```

### `foxos notes ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos notes ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`notes_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos notes ui click --ref e12
foxos notes ui click --name Settings
```

### `foxos notes ui type`

向控件输入文本（真实输入事件）

```text
foxos notes ui type TEXT [--ref REF] [--clear]
```

工具接口名：`notes_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos notes ui type 'hello' --ref e5
```

### `foxos notes ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos notes ui set --ref REF --value VALUE
```

工具接口名：`notes_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos notes ui set 
```

### `foxos notes ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos notes ui press KEY [--ref REF]
```

工具接口名：`notes_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos notes ui press mod+z
```

### `foxos notes ui screenshot`

应用窗口截图（PNG）

```text
foxos notes ui screenshot [--out OUT]
```

工具接口名：`notes_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos notes ui screenshot --json
```

### `foxos notes data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos notes data list [PATTERN]
```

工具接口名：`notes_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos notes data list --json
```

### `foxos notes data get`

读取应用保存的一项数据

```text
foxos notes data get KEY
```

工具接口名：`notes_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos notes data get X
```

### `foxos notes module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos notes module list
```

工具接口名：`notes_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos notes module list --json
```

### `foxos notes module read`

读取应用模块中的值（如 store 状态）

```text
foxos notes module read TARGET
```

工具接口名：`notes_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos notes module read X
```

### `foxos notes module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos notes module call TARGET [--args ARGS]
```

工具接口名：`notes_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos notes module call X
```

### `foxos notes op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos notes op list
```

工具接口名：`notes_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos notes op list --json
```

## records — Records

办公 · 替代 Airtable, Microsoft Access, Baserow。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos records app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos records app open [--file FILE] [--headless]
```

工具接口名：`records_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos records app open
foxos records app open --headless --json
```

### `foxos records app close`

关闭应用实例

```text
foxos records app close
```

工具接口名：`records_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos records app close --json
```

### `foxos records app status`

应用是否已安装、是否在运行

```text
foxos records app status
```

工具接口名：`records_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos records app status --json
```

### `foxos records file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos records file open PATH
```

工具接口名：`records_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos records file open X
```

### `foxos records ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos records ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`records_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos records ui snapshot --json
```

### `foxos records ui text`

读取界面上的可见文本

```text
foxos records ui text
```

工具接口名：`records_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos records ui text --json
```

### `foxos records ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos records ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`records_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos records ui click --ref e12
foxos records ui click --name Settings
```

### `foxos records ui type`

向控件输入文本（真实输入事件）

```text
foxos records ui type TEXT [--ref REF] [--clear]
```

工具接口名：`records_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos records ui type 'hello' --ref e5
```

### `foxos records ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos records ui set --ref REF --value VALUE
```

工具接口名：`records_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos records ui set 
```

### `foxos records ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos records ui press KEY [--ref REF]
```

工具接口名：`records_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos records ui press mod+z
```

### `foxos records ui screenshot`

应用窗口截图（PNG）

```text
foxos records ui screenshot [--out OUT]
```

工具接口名：`records_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos records ui screenshot --json
```

### `foxos records data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos records data list [PATTERN]
```

工具接口名：`records_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos records data list --json
```

### `foxos records data get`

读取应用保存的一项数据

```text
foxos records data get KEY
```

工具接口名：`records_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos records data get X
```

### `foxos records module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos records module list
```

工具接口名：`records_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos records module list --json
```

### `foxos records module read`

读取应用模块中的值（如 store 状态）

```text
foxos records module read TARGET
```

工具接口名：`records_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos records module read X
```

### `foxos records module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos records module call TARGET [--args ARGS]
```

工具接口名：`records_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos records module call X
```

### `foxos records op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos records op list
```

工具接口名：`records_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos records op list --json
```

## meetings — Meetings

协作 · 替代 Zoom, Google Meet, Microsoft Teams。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos meetings app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos meetings app open [--file FILE] [--headless]
```

工具接口名：`meetings_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos meetings app open
foxos meetings app open --headless --json
```

### `foxos meetings app close`

关闭应用实例

```text
foxos meetings app close
```

工具接口名：`meetings_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos meetings app close --json
```

### `foxos meetings app status`

应用是否已安装、是否在运行

```text
foxos meetings app status
```

工具接口名：`meetings_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos meetings app status --json
```

### `foxos meetings file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos meetings file open PATH
```

工具接口名：`meetings_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos meetings file open X
```

### `foxos meetings ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos meetings ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`meetings_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos meetings ui snapshot --json
```

### `foxos meetings ui text`

读取界面上的可见文本

```text
foxos meetings ui text
```

工具接口名：`meetings_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos meetings ui text --json
```

### `foxos meetings ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos meetings ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`meetings_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos meetings ui click --ref e12
foxos meetings ui click --name Settings
```

### `foxos meetings ui type`

向控件输入文本（真实输入事件）

```text
foxos meetings ui type TEXT [--ref REF] [--clear]
```

工具接口名：`meetings_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos meetings ui type 'hello' --ref e5
```

### `foxos meetings ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos meetings ui set --ref REF --value VALUE
```

工具接口名：`meetings_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos meetings ui set 
```

### `foxos meetings ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos meetings ui press KEY [--ref REF]
```

工具接口名：`meetings_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos meetings ui press mod+z
```

### `foxos meetings ui screenshot`

应用窗口截图（PNG）

```text
foxos meetings ui screenshot [--out OUT]
```

工具接口名：`meetings_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos meetings ui screenshot --json
```

### `foxos meetings data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos meetings data list [PATTERN]
```

工具接口名：`meetings_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos meetings data list --json
```

### `foxos meetings data get`

读取应用保存的一项数据

```text
foxos meetings data get KEY
```

工具接口名：`meetings_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos meetings data get X
```

### `foxos meetings module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos meetings module list
```

工具接口名：`meetings_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos meetings module list --json
```

### `foxos meetings module read`

读取应用模块中的值（如 store 状态）

```text
foxos meetings module read TARGET
```

工具接口名：`meetings_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos meetings module read X
```

### `foxos meetings module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos meetings module call TARGET [--args ARGS]
```

工具接口名：`meetings_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos meetings module call X
```

### `foxos meetings op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos meetings op list
```

工具接口名：`meetings_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos meetings op list --json
```

## teamchat — Teamchat

协作 · 替代 Slack, Microsoft Teams, Google Chat。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos teamchat app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos teamchat app open [--file FILE] [--headless]
```

工具接口名：`teamchat_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos teamchat app open
foxos teamchat app open --headless --json
```

### `foxos teamchat app close`

关闭应用实例

```text
foxos teamchat app close
```

工具接口名：`teamchat_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos teamchat app close --json
```

### `foxos teamchat app status`

应用是否已安装、是否在运行

```text
foxos teamchat app status
```

工具接口名：`teamchat_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos teamchat app status --json
```

### `foxos teamchat file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos teamchat file open PATH
```

工具接口名：`teamchat_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos teamchat file open X
```

### `foxos teamchat ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos teamchat ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`teamchat_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos teamchat ui snapshot --json
```

### `foxos teamchat ui text`

读取界面上的可见文本

```text
foxos teamchat ui text
```

工具接口名：`teamchat_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos teamchat ui text --json
```

### `foxos teamchat ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos teamchat ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`teamchat_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos teamchat ui click --ref e12
foxos teamchat ui click --name Settings
```

### `foxos teamchat ui type`

向控件输入文本（真实输入事件）

```text
foxos teamchat ui type TEXT [--ref REF] [--clear]
```

工具接口名：`teamchat_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos teamchat ui type 'hello' --ref e5
```

### `foxos teamchat ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos teamchat ui set --ref REF --value VALUE
```

工具接口名：`teamchat_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos teamchat ui set 
```

### `foxos teamchat ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos teamchat ui press KEY [--ref REF]
```

工具接口名：`teamchat_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos teamchat ui press mod+z
```

### `foxos teamchat ui screenshot`

应用窗口截图（PNG）

```text
foxos teamchat ui screenshot [--out OUT]
```

工具接口名：`teamchat_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos teamchat ui screenshot --json
```

### `foxos teamchat data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos teamchat data list [PATTERN]
```

工具接口名：`teamchat_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos teamchat data list --json
```

### `foxos teamchat data get`

读取应用保存的一项数据

```text
foxos teamchat data get KEY
```

工具接口名：`teamchat_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos teamchat data get X
```

### `foxos teamchat module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos teamchat module list
```

工具接口名：`teamchat_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos teamchat module list --json
```

### `foxos teamchat module read`

读取应用模块中的值（如 store 状态）

```text
foxos teamchat module read TARGET
```

工具接口名：`teamchat_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos teamchat module read X
```

### `foxos teamchat module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos teamchat module call TARGET [--args ARGS]
```

工具接口名：`teamchat_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos teamchat module call X
```

### `foxos teamchat op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos teamchat op list
```

工具接口名：`teamchat_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos teamchat op list --json
```

## email — Email

协作 · 替代 Gmail, Microsoft Outlook, Apple Mail。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos email app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos email app open [--file FILE] [--headless]
```

工具接口名：`email_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos email app open
foxos email app open --headless --json
```

### `foxos email app close`

关闭应用实例

```text
foxos email app close
```

工具接口名：`email_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos email app close --json
```

### `foxos email app status`

应用是否已安装、是否在运行

```text
foxos email app status
```

工具接口名：`email_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos email app status --json
```

### `foxos email file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos email file open PATH
```

工具接口名：`email_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos email file open X
```

### `foxos email ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos email ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`email_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos email ui snapshot --json
```

### `foxos email ui text`

读取界面上的可见文本

```text
foxos email ui text
```

工具接口名：`email_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos email ui text --json
```

### `foxos email ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos email ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`email_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos email ui click --ref e12
foxos email ui click --name Settings
```

### `foxos email ui type`

向控件输入文本（真实输入事件）

```text
foxos email ui type TEXT [--ref REF] [--clear]
```

工具接口名：`email_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos email ui type 'hello' --ref e5
```

### `foxos email ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos email ui set --ref REF --value VALUE
```

工具接口名：`email_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos email ui set 
```

### `foxos email ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos email ui press KEY [--ref REF]
```

工具接口名：`email_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos email ui press mod+z
```

### `foxos email ui screenshot`

应用窗口截图（PNG）

```text
foxos email ui screenshot [--out OUT]
```

工具接口名：`email_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos email ui screenshot --json
```

### `foxos email data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos email data list [PATTERN]
```

工具接口名：`email_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos email data list --json
```

### `foxos email data get`

读取应用保存的一项数据

```text
foxos email data get KEY
```

工具接口名：`email_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos email data get X
```

### `foxos email module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos email module list
```

工具接口名：`email_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos email module list --json
```

### `foxos email module read`

读取应用模块中的值（如 store 状态）

```text
foxos email module read TARGET
```

工具接口名：`email_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos email module read X
```

### `foxos email module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos email module call TARGET [--args ARGS]
```

工具接口名：`email_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos email module call X
```

### `foxos email op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos email op list
```

工具接口名：`email_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos email op list --json
```

## contacts — Contacts

协作 · 替代 Google Contacts, Apple Contacts。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos contacts app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos contacts app open [--file FILE] [--headless]
```

工具接口名：`contacts_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos contacts app open
foxos contacts app open --headless --json
```

### `foxos contacts app close`

关闭应用实例

```text
foxos contacts app close
```

工具接口名：`contacts_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contacts app close --json
```

### `foxos contacts app status`

应用是否已安装、是否在运行

```text
foxos contacts app status
```

工具接口名：`contacts_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contacts app status --json
```

### `foxos contacts file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos contacts file open PATH
```

工具接口名：`contacts_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos contacts file open X
```

### `foxos contacts ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos contacts ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`contacts_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos contacts ui snapshot --json
```

### `foxos contacts ui text`

读取界面上的可见文本

```text
foxos contacts ui text
```

工具接口名：`contacts_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contacts ui text --json
```

### `foxos contacts ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos contacts ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`contacts_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos contacts ui click --ref e12
foxos contacts ui click --name Settings
```

### `foxos contacts ui type`

向控件输入文本（真实输入事件）

```text
foxos contacts ui type TEXT [--ref REF] [--clear]
```

工具接口名：`contacts_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos contacts ui type 'hello' --ref e5
```

### `foxos contacts ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos contacts ui set --ref REF --value VALUE
```

工具接口名：`contacts_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos contacts ui set 
```

### `foxos contacts ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos contacts ui press KEY [--ref REF]
```

工具接口名：`contacts_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos contacts ui press mod+z
```

### `foxos contacts ui screenshot`

应用窗口截图（PNG）

```text
foxos contacts ui screenshot [--out OUT]
```

工具接口名：`contacts_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos contacts ui screenshot --json
```

### `foxos contacts data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos contacts data list [PATTERN]
```

工具接口名：`contacts_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos contacts data list --json
```

### `foxos contacts data get`

读取应用保存的一项数据

```text
foxos contacts data get KEY
```

工具接口名：`contacts_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos contacts data get X
```

### `foxos contacts module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos contacts module list
```

工具接口名：`contacts_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contacts module list --json
```

### `foxos contacts module read`

读取应用模块中的值（如 store 状态）

```text
foxos contacts module read TARGET
```

工具接口名：`contacts_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos contacts module read X
```

### `foxos contacts module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos contacts module call TARGET [--args ARGS]
```

工具接口名：`contacts_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos contacts module call X
```

### `foxos contacts op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos contacts op list
```

工具接口名：`contacts_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contacts op list --json
```

## calendar — Calendar

协作 · 替代 Google Calendar, Apple Calendar, Outlook Calendar。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos calendar app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos calendar app open [--file FILE] [--headless]
```

工具接口名：`calendar_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos calendar app open
foxos calendar app open --headless --json
```

### `foxos calendar app close`

关闭应用实例

```text
foxos calendar app close
```

工具接口名：`calendar_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos calendar app close --json
```

### `foxos calendar app status`

应用是否已安装、是否在运行

```text
foxos calendar app status
```

工具接口名：`calendar_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos calendar app status --json
```

### `foxos calendar file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos calendar file open PATH
```

工具接口名：`calendar_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos calendar file open X
```

### `foxos calendar ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos calendar ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`calendar_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos calendar ui snapshot --json
```

### `foxos calendar ui text`

读取界面上的可见文本

```text
foxos calendar ui text
```

工具接口名：`calendar_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos calendar ui text --json
```

### `foxos calendar ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos calendar ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`calendar_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos calendar ui click --ref e12
foxos calendar ui click --name Settings
```

### `foxos calendar ui type`

向控件输入文本（真实输入事件）

```text
foxos calendar ui type TEXT [--ref REF] [--clear]
```

工具接口名：`calendar_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos calendar ui type 'hello' --ref e5
```

### `foxos calendar ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos calendar ui set --ref REF --value VALUE
```

工具接口名：`calendar_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos calendar ui set 
```

### `foxos calendar ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos calendar ui press KEY [--ref REF]
```

工具接口名：`calendar_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos calendar ui press mod+z
```

### `foxos calendar ui screenshot`

应用窗口截图（PNG）

```text
foxos calendar ui screenshot [--out OUT]
```

工具接口名：`calendar_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos calendar ui screenshot --json
```

### `foxos calendar data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos calendar data list [PATTERN]
```

工具接口名：`calendar_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos calendar data list --json
```

### `foxos calendar data get`

读取应用保存的一项数据

```text
foxos calendar data get KEY
```

工具接口名：`calendar_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos calendar data get X
```

### `foxos calendar module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos calendar module list
```

工具接口名：`calendar_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos calendar module list --json
```

### `foxos calendar module read`

读取应用模块中的值（如 store 状态）

```text
foxos calendar module read TARGET
```

工具接口名：`calendar_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos calendar module read X
```

### `foxos calendar module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos calendar module call TARGET [--args ARGS]
```

工具接口名：`calendar_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos calendar module call X
```

### `foxos calendar op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos calendar op list
```

工具接口名：`calendar_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos calendar op list --json
```

## signatures — Signatures

协作 · 替代 DocuSign, Adobe Acrobat Sign, Dropbox Sign。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos signatures app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos signatures app open [--file FILE] [--headless]
```

工具接口名：`signatures_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos signatures app open
foxos signatures app open --headless --json
```

### `foxos signatures app close`

关闭应用实例

```text
foxos signatures app close
```

工具接口名：`signatures_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos signatures app close --json
```

### `foxos signatures app status`

应用是否已安装、是否在运行

```text
foxos signatures app status
```

工具接口名：`signatures_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos signatures app status --json
```

### `foxos signatures file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos signatures file open PATH
```

工具接口名：`signatures_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos signatures file open X
```

### `foxos signatures ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos signatures ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`signatures_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos signatures ui snapshot --json
```

### `foxos signatures ui text`

读取界面上的可见文本

```text
foxos signatures ui text
```

工具接口名：`signatures_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos signatures ui text --json
```

### `foxos signatures ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos signatures ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`signatures_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos signatures ui click --ref e12
foxos signatures ui click --name Settings
```

### `foxos signatures ui type`

向控件输入文本（真实输入事件）

```text
foxos signatures ui type TEXT [--ref REF] [--clear]
```

工具接口名：`signatures_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos signatures ui type 'hello' --ref e5
```

### `foxos signatures ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos signatures ui set --ref REF --value VALUE
```

工具接口名：`signatures_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos signatures ui set 
```

### `foxos signatures ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos signatures ui press KEY [--ref REF]
```

工具接口名：`signatures_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos signatures ui press mod+z
```

### `foxos signatures ui screenshot`

应用窗口截图（PNG）

```text
foxos signatures ui screenshot [--out OUT]
```

工具接口名：`signatures_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos signatures ui screenshot --json
```

### `foxos signatures data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos signatures data list [PATTERN]
```

工具接口名：`signatures_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos signatures data list --json
```

### `foxos signatures data get`

读取应用保存的一项数据

```text
foxos signatures data get KEY
```

工具接口名：`signatures_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos signatures data get X
```

### `foxos signatures module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos signatures module list
```

工具接口名：`signatures_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos signatures module list --json
```

### `foxos signatures module read`

读取应用模块中的值（如 store 状态）

```text
foxos signatures module read TARGET
```

工具接口名：`signatures_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos signatures module read X
```

### `foxos signatures module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos signatures module call TARGET [--args ARGS]
```

工具接口名：`signatures_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos signatures module call X
```

### `foxos signatures op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos signatures op list
```

工具接口名：`signatures_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos signatures op list --json
```

## photo-studio — Photo Studio

创意 · 替代 Adobe Photoshop, Pixelmator。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos photo-studio app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos photo-studio app open [--file FILE] [--headless]
```

工具接口名：`photo-studio_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos photo-studio app open
foxos photo-studio app open --headless --json
```

### `foxos photo-studio app close`

关闭应用实例

```text
foxos photo-studio app close
```

工具接口名：`photo-studio_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos photo-studio app close --json
```

### `foxos photo-studio app status`

应用是否已安装、是否在运行

```text
foxos photo-studio app status
```

工具接口名：`photo-studio_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos photo-studio app status --json
```

### `foxos photo-studio file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos photo-studio file open PATH
```

工具接口名：`photo-studio_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos photo-studio file open X
```

### `foxos photo-studio ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos photo-studio ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`photo-studio_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos photo-studio ui snapshot --json
```

### `foxos photo-studio ui text`

读取界面上的可见文本

```text
foxos photo-studio ui text
```

工具接口名：`photo-studio_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos photo-studio ui text --json
```

### `foxos photo-studio ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos photo-studio ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`photo-studio_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos photo-studio ui click --ref e12
foxos photo-studio ui click --name Settings
```

### `foxos photo-studio ui type`

向控件输入文本（真实输入事件）

```text
foxos photo-studio ui type TEXT [--ref REF] [--clear]
```

工具接口名：`photo-studio_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos photo-studio ui type 'hello' --ref e5
```

### `foxos photo-studio ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos photo-studio ui set --ref REF --value VALUE
```

工具接口名：`photo-studio_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos photo-studio ui set 
```

### `foxos photo-studio ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos photo-studio ui press KEY [--ref REF]
```

工具接口名：`photo-studio_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos photo-studio ui press mod+z
```

### `foxos photo-studio ui screenshot`

应用窗口截图（PNG）

```text
foxos photo-studio ui screenshot [--out OUT]
```

工具接口名：`photo-studio_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos photo-studio ui screenshot --json
```

### `foxos photo-studio data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos photo-studio data list [PATTERN]
```

工具接口名：`photo-studio_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos photo-studio data list --json
```

### `foxos photo-studio data get`

读取应用保存的一项数据

```text
foxos photo-studio data get KEY
```

工具接口名：`photo-studio_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos photo-studio data get X
```

### `foxos photo-studio module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos photo-studio module list
```

工具接口名：`photo-studio_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos photo-studio module list --json
```

### `foxos photo-studio module read`

读取应用模块中的值（如 store 状态）

```text
foxos photo-studio module read TARGET
```

工具接口名：`photo-studio_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos photo-studio module read X
```

### `foxos photo-studio module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos photo-studio module call TARGET [--args ARGS]
```

工具接口名：`photo-studio_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos photo-studio module call X
```

### `foxos photo-studio op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos photo-studio op list
```

工具接口名：`photo-studio_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos photo-studio op list --json
```

## video-studio — Video Studio

创意 · 替代 CapCut, Adobe Premiere Pro, Final Cut Pro, DaVinci Resolve。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos video-studio app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos video-studio app open [--file FILE] [--headless]
```

工具接口名：`video-studio_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos video-studio app open
foxos video-studio app open --headless --json
```

### `foxos video-studio app close`

关闭应用实例

```text
foxos video-studio app close
```

工具接口名：`video-studio_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos video-studio app close --json
```

### `foxos video-studio app status`

应用是否已安装、是否在运行

```text
foxos video-studio app status
```

工具接口名：`video-studio_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos video-studio app status --json
```

### `foxos video-studio file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos video-studio file open PATH
```

工具接口名：`video-studio_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos video-studio file open X
```

### `foxos video-studio ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos video-studio ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`video-studio_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos video-studio ui snapshot --json
```

### `foxos video-studio ui text`

读取界面上的可见文本

```text
foxos video-studio ui text
```

工具接口名：`video-studio_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos video-studio ui text --json
```

### `foxos video-studio ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos video-studio ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`video-studio_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos video-studio ui click --ref e12
foxos video-studio ui click --name Settings
```

### `foxos video-studio ui type`

向控件输入文本（真实输入事件）

```text
foxos video-studio ui type TEXT [--ref REF] [--clear]
```

工具接口名：`video-studio_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos video-studio ui type 'hello' --ref e5
```

### `foxos video-studio ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos video-studio ui set --ref REF --value VALUE
```

工具接口名：`video-studio_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos video-studio ui set 
```

### `foxos video-studio ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos video-studio ui press KEY [--ref REF]
```

工具接口名：`video-studio_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos video-studio ui press mod+z
```

### `foxos video-studio ui screenshot`

应用窗口截图（PNG）

```text
foxos video-studio ui screenshot [--out OUT]
```

工具接口名：`video-studio_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos video-studio ui screenshot --json
```

### `foxos video-studio data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos video-studio data list [PATTERN]
```

工具接口名：`video-studio_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos video-studio data list --json
```

### `foxos video-studio data get`

读取应用保存的一项数据

```text
foxos video-studio data get KEY
```

工具接口名：`video-studio_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos video-studio data get X
```

### `foxos video-studio module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos video-studio module list
```

工具接口名：`video-studio_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos video-studio module list --json
```

### `foxos video-studio module read`

读取应用模块中的值（如 store 状态）

```text
foxos video-studio module read TARGET
```

工具接口名：`video-studio_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos video-studio module read X
```

### `foxos video-studio module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos video-studio module call TARGET [--args ARGS]
```

工具接口名：`video-studio_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos video-studio module call X
```

### `foxos video-studio op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos video-studio op list
```

工具接口名：`video-studio_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos video-studio op list --json
```

## vector-studio — Vector Studio

创意 · 替代 Adobe Illustrator, CorelDRAW, Affinity Designer。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos vector-studio app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos vector-studio app open [--file FILE] [--headless]
```

工具接口名：`vector-studio_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos vector-studio app open
foxos vector-studio app open --headless --json
```

### `foxos vector-studio app close`

关闭应用实例

```text
foxos vector-studio app close
```

工具接口名：`vector-studio_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos vector-studio app close --json
```

### `foxos vector-studio app status`

应用是否已安装、是否在运行

```text
foxos vector-studio app status
```

工具接口名：`vector-studio_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos vector-studio app status --json
```

### `foxos vector-studio file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos vector-studio file open PATH
```

工具接口名：`vector-studio_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos vector-studio file open X
```

### `foxos vector-studio ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos vector-studio ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`vector-studio_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos vector-studio ui snapshot --json
```

### `foxos vector-studio ui text`

读取界面上的可见文本

```text
foxos vector-studio ui text
```

工具接口名：`vector-studio_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos vector-studio ui text --json
```

### `foxos vector-studio ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos vector-studio ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`vector-studio_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos vector-studio ui click --ref e12
foxos vector-studio ui click --name Settings
```

### `foxos vector-studio ui type`

向控件输入文本（真实输入事件）

```text
foxos vector-studio ui type TEXT [--ref REF] [--clear]
```

工具接口名：`vector-studio_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos vector-studio ui type 'hello' --ref e5
```

### `foxos vector-studio ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos vector-studio ui set --ref REF --value VALUE
```

工具接口名：`vector-studio_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos vector-studio ui set 
```

### `foxos vector-studio ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos vector-studio ui press KEY [--ref REF]
```

工具接口名：`vector-studio_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos vector-studio ui press mod+z
```

### `foxos vector-studio ui screenshot`

应用窗口截图（PNG）

```text
foxos vector-studio ui screenshot [--out OUT]
```

工具接口名：`vector-studio_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos vector-studio ui screenshot --json
```

### `foxos vector-studio data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos vector-studio data list [PATTERN]
```

工具接口名：`vector-studio_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos vector-studio data list --json
```

### `foxos vector-studio data get`

读取应用保存的一项数据

```text
foxos vector-studio data get KEY
```

工具接口名：`vector-studio_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos vector-studio data get X
```

### `foxos vector-studio module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos vector-studio module list
```

工具接口名：`vector-studio_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos vector-studio module list --json
```

### `foxos vector-studio module read`

读取应用模块中的值（如 store 状态）

```text
foxos vector-studio module read TARGET
```

工具接口名：`vector-studio_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos vector-studio module read X
```

### `foxos vector-studio module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos vector-studio module call TARGET [--args ARGS]
```

工具接口名：`vector-studio_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos vector-studio module call X
```

### `foxos vector-studio op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos vector-studio op list
```

工具接口名：`vector-studio_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos vector-studio op list --json
```

## audio-studio — Audio Studio

创意 · 替代 Adobe Audition, Sound Forge。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos audio-studio app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos audio-studio app open [--file FILE] [--headless]
```

工具接口名：`audio-studio_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos audio-studio app open
foxos audio-studio app open --headless --json
```

### `foxos audio-studio app close`

关闭应用实例

```text
foxos audio-studio app close
```

工具接口名：`audio-studio_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos audio-studio app close --json
```

### `foxos audio-studio app status`

应用是否已安装、是否在运行

```text
foxos audio-studio app status
```

工具接口名：`audio-studio_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos audio-studio app status --json
```

### `foxos audio-studio file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos audio-studio file open PATH
```

工具接口名：`audio-studio_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos audio-studio file open X
```

### `foxos audio-studio ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos audio-studio ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`audio-studio_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos audio-studio ui snapshot --json
```

### `foxos audio-studio ui text`

读取界面上的可见文本

```text
foxos audio-studio ui text
```

工具接口名：`audio-studio_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos audio-studio ui text --json
```

### `foxos audio-studio ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos audio-studio ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`audio-studio_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos audio-studio ui click --ref e12
foxos audio-studio ui click --name Settings
```

### `foxos audio-studio ui type`

向控件输入文本（真实输入事件）

```text
foxos audio-studio ui type TEXT [--ref REF] [--clear]
```

工具接口名：`audio-studio_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos audio-studio ui type 'hello' --ref e5
```

### `foxos audio-studio ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos audio-studio ui set --ref REF --value VALUE
```

工具接口名：`audio-studio_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos audio-studio ui set 
```

### `foxos audio-studio ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos audio-studio ui press KEY [--ref REF]
```

工具接口名：`audio-studio_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos audio-studio ui press mod+z
```

### `foxos audio-studio ui screenshot`

应用窗口截图（PNG）

```text
foxos audio-studio ui screenshot [--out OUT]
```

工具接口名：`audio-studio_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos audio-studio ui screenshot --json
```

### `foxos audio-studio data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos audio-studio data list [PATTERN]
```

工具接口名：`audio-studio_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos audio-studio data list --json
```

### `foxos audio-studio data get`

读取应用保存的一项数据

```text
foxos audio-studio data get KEY
```

工具接口名：`audio-studio_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos audio-studio data get X
```

### `foxos audio-studio module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos audio-studio module list
```

工具接口名：`audio-studio_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos audio-studio module list --json
```

### `foxos audio-studio module read`

读取应用模块中的值（如 store 状态）

```text
foxos audio-studio module read TARGET
```

工具接口名：`audio-studio_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos audio-studio module read X
```

### `foxos audio-studio module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos audio-studio module call TARGET [--args ARGS]
```

工具接口名：`audio-studio_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos audio-studio module call X
```

### `foxos audio-studio op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos audio-studio op list
```

工具接口名：`audio-studio_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos audio-studio op list --json
```

## music-studio — Music Studio

创意 · 替代 FL Studio, Ableton Live, Logic Pro。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos music-studio app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos music-studio app open [--file FILE] [--headless]
```

工具接口名：`music-studio_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos music-studio app open
foxos music-studio app open --headless --json
```

### `foxos music-studio app close`

关闭应用实例

```text
foxos music-studio app close
```

工具接口名：`music-studio_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos music-studio app close --json
```

### `foxos music-studio app status`

应用是否已安装、是否在运行

```text
foxos music-studio app status
```

工具接口名：`music-studio_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos music-studio app status --json
```

### `foxos music-studio file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos music-studio file open PATH
```

工具接口名：`music-studio_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos music-studio file open X
```

### `foxos music-studio ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos music-studio ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`music-studio_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos music-studio ui snapshot --json
```

### `foxos music-studio ui text`

读取界面上的可见文本

```text
foxos music-studio ui text
```

工具接口名：`music-studio_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos music-studio ui text --json
```

### `foxos music-studio ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos music-studio ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`music-studio_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos music-studio ui click --ref e12
foxos music-studio ui click --name Settings
```

### `foxos music-studio ui type`

向控件输入文本（真实输入事件）

```text
foxos music-studio ui type TEXT [--ref REF] [--clear]
```

工具接口名：`music-studio_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos music-studio ui type 'hello' --ref e5
```

### `foxos music-studio ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos music-studio ui set --ref REF --value VALUE
```

工具接口名：`music-studio_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos music-studio ui set 
```

### `foxos music-studio ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos music-studio ui press KEY [--ref REF]
```

工具接口名：`music-studio_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos music-studio ui press mod+z
```

### `foxos music-studio ui screenshot`

应用窗口截图（PNG）

```text
foxos music-studio ui screenshot [--out OUT]
```

工具接口名：`music-studio_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos music-studio ui screenshot --json
```

### `foxos music-studio data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos music-studio data list [PATTERN]
```

工具接口名：`music-studio_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos music-studio data list --json
```

### `foxos music-studio data get`

读取应用保存的一项数据

```text
foxos music-studio data get KEY
```

工具接口名：`music-studio_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos music-studio data get X
```

### `foxos music-studio module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos music-studio module list
```

工具接口名：`music-studio_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos music-studio module list --json
```

### `foxos music-studio module read`

读取应用模块中的值（如 store 状态）

```text
foxos music-studio module read TARGET
```

工具接口名：`music-studio_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos music-studio module read X
```

### `foxos music-studio module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos music-studio module call TARGET [--args ARGS]
```

工具接口名：`music-studio_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos music-studio module call X
```

### `foxos music-studio op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos music-studio op list
```

工具接口名：`music-studio_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos music-studio op list --json
```

## 3d — 3D Studio

创意 · 替代 Autodesk Maya, SketchUp。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos 3d app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos 3d app open [--file FILE] [--headless]
```

工具接口名：`3d_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos 3d app open
foxos 3d app open --headless --json
```

### `foxos 3d app close`

关闭应用实例

```text
foxos 3d app close
```

工具接口名：`3d_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos 3d app close --json
```

### `foxos 3d app status`

应用是否已安装、是否在运行

```text
foxos 3d app status
```

工具接口名：`3d_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos 3d app status --json
```

### `foxos 3d file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos 3d file open PATH
```

工具接口名：`3d_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos 3d file open X
```

### `foxos 3d ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos 3d ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`3d_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos 3d ui snapshot --json
```

### `foxos 3d ui text`

读取界面上的可见文本

```text
foxos 3d ui text
```

工具接口名：`3d_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos 3d ui text --json
```

### `foxos 3d ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos 3d ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`3d_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos 3d ui click --ref e12
foxos 3d ui click --name Settings
```

### `foxos 3d ui type`

向控件输入文本（真实输入事件）

```text
foxos 3d ui type TEXT [--ref REF] [--clear]
```

工具接口名：`3d_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos 3d ui type 'hello' --ref e5
```

### `foxos 3d ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos 3d ui set --ref REF --value VALUE
```

工具接口名：`3d_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos 3d ui set 
```

### `foxos 3d ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos 3d ui press KEY [--ref REF]
```

工具接口名：`3d_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos 3d ui press mod+z
```

### `foxos 3d ui screenshot`

应用窗口截图（PNG）

```text
foxos 3d ui screenshot [--out OUT]
```

工具接口名：`3d_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos 3d ui screenshot --json
```

### `foxos 3d data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos 3d data list [PATTERN]
```

工具接口名：`3d_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos 3d data list --json
```

### `foxos 3d data get`

读取应用保存的一项数据

```text
foxos 3d data get KEY
```

工具接口名：`3d_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos 3d data get X
```

### `foxos 3d module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos 3d module list
```

工具接口名：`3d_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos 3d module list --json
```

### `foxos 3d module read`

读取应用模块中的值（如 store 状态）

```text
foxos 3d module read TARGET
```

工具接口名：`3d_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos 3d module read X
```

### `foxos 3d module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos 3d module call TARGET [--args ARGS]
```

工具接口名：`3d_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos 3d module call X
```

### `foxos 3d op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos 3d op list
```

工具接口名：`3d_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos 3d op list --json
```

## cad — CAD

工程 · 替代 AutoCAD, DraftSight, BricsCAD。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos cad app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos cad app open [--file FILE] [--headless]
```

工具接口名：`cad_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos cad app open
foxos cad app open --headless --json
```

### `foxos cad app close`

关闭应用实例

```text
foxos cad app close
```

工具接口名：`cad_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cad app close --json
```

### `foxos cad app status`

应用是否已安装、是否在运行

```text
foxos cad app status
```

工具接口名：`cad_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cad app status --json
```

### `foxos cad file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos cad file open PATH
```

工具接口名：`cad_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos cad file open X
```

### `foxos cad ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos cad ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`cad_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos cad ui snapshot --json
```

### `foxos cad ui text`

读取界面上的可见文本

```text
foxos cad ui text
```

工具接口名：`cad_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cad ui text --json
```

### `foxos cad ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos cad ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`cad_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos cad ui click --ref e12
foxos cad ui click --name Settings
```

### `foxos cad ui type`

向控件输入文本（真实输入事件）

```text
foxos cad ui type TEXT [--ref REF] [--clear]
```

工具接口名：`cad_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos cad ui type 'hello' --ref e5
```

### `foxos cad ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos cad ui set --ref REF --value VALUE
```

工具接口名：`cad_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos cad ui set 
```

### `foxos cad ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos cad ui press KEY [--ref REF]
```

工具接口名：`cad_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos cad ui press mod+z
```

### `foxos cad ui screenshot`

应用窗口截图（PNG）

```text
foxos cad ui screenshot [--out OUT]
```

工具接口名：`cad_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos cad ui screenshot --json
```

### `foxos cad data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos cad data list [PATTERN]
```

工具接口名：`cad_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos cad data list --json
```

### `foxos cad data get`

读取应用保存的一项数据

```text
foxos cad data get KEY
```

工具接口名：`cad_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos cad data get X
```

### `foxos cad module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos cad module list
```

工具接口名：`cad_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cad module list --json
```

### `foxos cad module read`

读取应用模块中的值（如 store 状态）

```text
foxos cad module read TARGET
```

工具接口名：`cad_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos cad module read X
```

### `foxos cad module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos cad module call TARGET [--args ARGS]
```

工具接口名：`cad_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos cad module call X
```

### `foxos cad op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos cad op list
```

工具接口名：`cad_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cad op list --json
```

## parametric — Parametric

工程 · 替代 SolidWorks, Autodesk Fusion, Autodesk Inventor。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos parametric app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos parametric app open [--file FILE] [--headless]
```

工具接口名：`parametric_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos parametric app open
foxos parametric app open --headless --json
```

### `foxos parametric app close`

关闭应用实例

```text
foxos parametric app close
```

工具接口名：`parametric_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos parametric app close --json
```

### `foxos parametric app status`

应用是否已安装、是否在运行

```text
foxos parametric app status
```

工具接口名：`parametric_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos parametric app status --json
```

### `foxos parametric file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos parametric file open PATH
```

工具接口名：`parametric_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos parametric file open X
```

### `foxos parametric ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos parametric ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`parametric_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos parametric ui snapshot --json
```

### `foxos parametric ui text`

读取界面上的可见文本

```text
foxos parametric ui text
```

工具接口名：`parametric_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos parametric ui text --json
```

### `foxos parametric ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos parametric ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`parametric_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos parametric ui click --ref e12
foxos parametric ui click --name Settings
```

### `foxos parametric ui type`

向控件输入文本（真实输入事件）

```text
foxos parametric ui type TEXT [--ref REF] [--clear]
```

工具接口名：`parametric_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos parametric ui type 'hello' --ref e5
```

### `foxos parametric ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos parametric ui set --ref REF --value VALUE
```

工具接口名：`parametric_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos parametric ui set 
```

### `foxos parametric ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos parametric ui press KEY [--ref REF]
```

工具接口名：`parametric_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos parametric ui press mod+z
```

### `foxos parametric ui screenshot`

应用窗口截图（PNG）

```text
foxos parametric ui screenshot [--out OUT]
```

工具接口名：`parametric_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos parametric ui screenshot --json
```

### `foxos parametric data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos parametric data list [PATTERN]
```

工具接口名：`parametric_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos parametric data list --json
```

### `foxos parametric data get`

读取应用保存的一项数据

```text
foxos parametric data get KEY
```

工具接口名：`parametric_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos parametric data get X
```

### `foxos parametric module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos parametric module list
```

工具接口名：`parametric_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos parametric module list --json
```

### `foxos parametric module read`

读取应用模块中的值（如 store 状态）

```text
foxos parametric module read TARGET
```

工具接口名：`parametric_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos parametric module read X
```

### `foxos parametric module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos parametric module call TARGET [--args ARGS]
```

工具接口名：`parametric_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos parametric module call X
```

### `foxos parametric op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos parametric op list
```

工具接口名：`parametric_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos parametric op list --json
```

## circuits — Circuits

工程 · 替代 Altium Designer, Autodesk Eagle, OrCAD。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos circuits app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos circuits app open [--file FILE] [--headless]
```

工具接口名：`circuits_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos circuits app open
foxos circuits app open --headless --json
```

### `foxos circuits app close`

关闭应用实例

```text
foxos circuits app close
```

工具接口名：`circuits_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos circuits app close --json
```

### `foxos circuits app status`

应用是否已安装、是否在运行

```text
foxos circuits app status
```

工具接口名：`circuits_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos circuits app status --json
```

### `foxos circuits file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos circuits file open PATH
```

工具接口名：`circuits_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos circuits file open X
```

### `foxos circuits ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos circuits ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`circuits_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos circuits ui snapshot --json
```

### `foxos circuits ui text`

读取界面上的可见文本

```text
foxos circuits ui text
```

工具接口名：`circuits_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos circuits ui text --json
```

### `foxos circuits ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos circuits ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`circuits_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos circuits ui click --ref e12
foxos circuits ui click --name Settings
```

### `foxos circuits ui type`

向控件输入文本（真实输入事件）

```text
foxos circuits ui type TEXT [--ref REF] [--clear]
```

工具接口名：`circuits_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos circuits ui type 'hello' --ref e5
```

### `foxos circuits ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos circuits ui set --ref REF --value VALUE
```

工具接口名：`circuits_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos circuits ui set 
```

### `foxos circuits ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos circuits ui press KEY [--ref REF]
```

工具接口名：`circuits_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos circuits ui press mod+z
```

### `foxos circuits ui screenshot`

应用窗口截图（PNG）

```text
foxos circuits ui screenshot [--out OUT]
```

工具接口名：`circuits_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos circuits ui screenshot --json
```

### `foxos circuits data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos circuits data list [PATTERN]
```

工具接口名：`circuits_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos circuits data list --json
```

### `foxos circuits data get`

读取应用保存的一项数据

```text
foxos circuits data get KEY
```

工具接口名：`circuits_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos circuits data get X
```

### `foxos circuits module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos circuits module list
```

工具接口名：`circuits_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos circuits module list --json
```

### `foxos circuits module read`

读取应用模块中的值（如 store 状态）

```text
foxos circuits module read TARGET
```

工具接口名：`circuits_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos circuits module read X
```

### `foxos circuits module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos circuits module call TARGET [--args ARGS]
```

工具接口名：`circuits_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos circuits module call X
```

### `foxos circuits op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos circuits op list
```

工具接口名：`circuits_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos circuits op list --json
```

## building-design — Building Design

工程 · 替代 Autodesk Revit, ArchiCAD, Vectorworks。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：AGPL-3.0-only

### `foxos building-design app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos building-design app open [--file FILE] [--headless]
```

工具接口名：`building-design_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos building-design app open
foxos building-design app open --headless --json
```

### `foxos building-design app close`

关闭应用实例

```text
foxos building-design app close
```

工具接口名：`building-design_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos building-design app close --json
```

### `foxos building-design app status`

应用是否已安装、是否在运行

```text
foxos building-design app status
```

工具接口名：`building-design_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos building-design app status --json
```

### `foxos building-design file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos building-design file open PATH
```

工具接口名：`building-design_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos building-design file open X
```

### `foxos building-design ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos building-design ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`building-design_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos building-design ui snapshot --json
```

### `foxos building-design ui text`

读取界面上的可见文本

```text
foxos building-design ui text
```

工具接口名：`building-design_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos building-design ui text --json
```

### `foxos building-design ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos building-design ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`building-design_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos building-design ui click --ref e12
foxos building-design ui click --name Settings
```

### `foxos building-design ui type`

向控件输入文本（真实输入事件）

```text
foxos building-design ui type TEXT [--ref REF] [--clear]
```

工具接口名：`building-design_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos building-design ui type 'hello' --ref e5
```

### `foxos building-design ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos building-design ui set --ref REF --value VALUE
```

工具接口名：`building-design_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos building-design ui set 
```

### `foxos building-design ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos building-design ui press KEY [--ref REF]
```

工具接口名：`building-design_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos building-design ui press mod+z
```

### `foxos building-design ui screenshot`

应用窗口截图（PNG）

```text
foxos building-design ui screenshot [--out OUT]
```

工具接口名：`building-design_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos building-design ui screenshot --json
```

### `foxos building-design data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos building-design data list [PATTERN]
```

工具接口名：`building-design_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos building-design data list --json
```

### `foxos building-design data get`

读取应用保存的一项数据

```text
foxos building-design data get KEY
```

工具接口名：`building-design_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos building-design data get X
```

### `foxos building-design module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos building-design module list
```

工具接口名：`building-design_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos building-design module list --json
```

### `foxos building-design module read`

读取应用模块中的值（如 store 状态）

```text
foxos building-design module read TARGET
```

工具接口名：`building-design_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos building-design module read X
```

### `foxos building-design module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos building-design module call TARGET [--args ARGS]
```

工具接口名：`building-design_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos building-design module call X
```

### `foxos building-design op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos building-design op list
```

工具接口名：`building-design_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos building-design op list --json
```

## tasks — Tasks

效率 · 替代 Todoist, Microsoft To Do, TickTick。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos tasks app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos tasks app open [--file FILE] [--headless]
```

工具接口名：`tasks_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos tasks app open
foxos tasks app open --headless --json
```

### `foxos tasks app close`

关闭应用实例

```text
foxos tasks app close
```

工具接口名：`tasks_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos tasks app close --json
```

### `foxos tasks app status`

应用是否已安装、是否在运行

```text
foxos tasks app status
```

工具接口名：`tasks_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos tasks app status --json
```

### `foxos tasks file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos tasks file open PATH
```

工具接口名：`tasks_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos tasks file open X
```

### `foxos tasks ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos tasks ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`tasks_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos tasks ui snapshot --json
```

### `foxos tasks ui text`

读取界面上的可见文本

```text
foxos tasks ui text
```

工具接口名：`tasks_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos tasks ui text --json
```

### `foxos tasks ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos tasks ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`tasks_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos tasks ui click --ref e12
foxos tasks ui click --name Settings
```

### `foxos tasks ui type`

向控件输入文本（真实输入事件）

```text
foxos tasks ui type TEXT [--ref REF] [--clear]
```

工具接口名：`tasks_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos tasks ui type 'hello' --ref e5
```

### `foxos tasks ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos tasks ui set --ref REF --value VALUE
```

工具接口名：`tasks_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos tasks ui set 
```

### `foxos tasks ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos tasks ui press KEY [--ref REF]
```

工具接口名：`tasks_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos tasks ui press mod+z
```

### `foxos tasks ui screenshot`

应用窗口截图（PNG）

```text
foxos tasks ui screenshot [--out OUT]
```

工具接口名：`tasks_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos tasks ui screenshot --json
```

### `foxos tasks data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos tasks data list [PATTERN]
```

工具接口名：`tasks_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos tasks data list --json
```

### `foxos tasks data get`

读取应用保存的一项数据

```text
foxos tasks data get KEY
```

工具接口名：`tasks_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos tasks data get X
```

### `foxos tasks module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos tasks module list
```

工具接口名：`tasks_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos tasks module list --json
```

### `foxos tasks module read`

读取应用模块中的值（如 store 状态）

```text
foxos tasks module read TARGET
```

工具接口名：`tasks_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos tasks module read X
```

### `foxos tasks module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos tasks module call TARGET [--args ARGS]
```

工具接口名：`tasks_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos tasks module call X
```

### `foxos tasks op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos tasks op list
```

工具接口名：`tasks_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos tasks op list --json
```

## projects — Projects

效率 · 替代 Trello, Asana, monday.com。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos projects app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos projects app open [--file FILE] [--headless]
```

工具接口名：`projects_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos projects app open
foxos projects app open --headless --json
```

### `foxos projects app close`

关闭应用实例

```text
foxos projects app close
```

工具接口名：`projects_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos projects app close --json
```

### `foxos projects app status`

应用是否已安装、是否在运行

```text
foxos projects app status
```

工具接口名：`projects_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos projects app status --json
```

### `foxos projects file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos projects file open PATH
```

工具接口名：`projects_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos projects file open X
```

### `foxos projects ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos projects ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`projects_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos projects ui snapshot --json
```

### `foxos projects ui text`

读取界面上的可见文本

```text
foxos projects ui text
```

工具接口名：`projects_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos projects ui text --json
```

### `foxos projects ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos projects ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`projects_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos projects ui click --ref e12
foxos projects ui click --name Settings
```

### `foxos projects ui type`

向控件输入文本（真实输入事件）

```text
foxos projects ui type TEXT [--ref REF] [--clear]
```

工具接口名：`projects_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos projects ui type 'hello' --ref e5
```

### `foxos projects ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos projects ui set --ref REF --value VALUE
```

工具接口名：`projects_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos projects ui set 
```

### `foxos projects ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos projects ui press KEY [--ref REF]
```

工具接口名：`projects_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos projects ui press mod+z
```

### `foxos projects ui screenshot`

应用窗口截图（PNG）

```text
foxos projects ui screenshot [--out OUT]
```

工具接口名：`projects_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos projects ui screenshot --json
```

### `foxos projects data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos projects data list [PATTERN]
```

工具接口名：`projects_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos projects data list --json
```

### `foxos projects data get`

读取应用保存的一项数据

```text
foxos projects data get KEY
```

工具接口名：`projects_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos projects data get X
```

### `foxos projects module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos projects module list
```

工具接口名：`projects_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos projects module list --json
```

### `foxos projects module read`

读取应用模块中的值（如 store 状态）

```text
foxos projects module read TARGET
```

工具接口名：`projects_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos projects module read X
```

### `foxos projects module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos projects module call TARGET [--args ARGS]
```

工具接口名：`projects_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos projects module call X
```

### `foxos projects op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos projects op list
```

工具接口名：`projects_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos projects op list --json
```

## wiki — Wiki

效率 · 替代 Notion, Confluence, Coda。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos wiki app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos wiki app open [--file FILE] [--headless]
```

工具接口名：`wiki_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos wiki app open
foxos wiki app open --headless --json
```

### `foxos wiki app close`

关闭应用实例

```text
foxos wiki app close
```

工具接口名：`wiki_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos wiki app close --json
```

### `foxos wiki app status`

应用是否已安装、是否在运行

```text
foxos wiki app status
```

工具接口名：`wiki_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos wiki app status --json
```

### `foxos wiki file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos wiki file open PATH
```

工具接口名：`wiki_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos wiki file open X
```

### `foxos wiki ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos wiki ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`wiki_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos wiki ui snapshot --json
```

### `foxos wiki ui text`

读取界面上的可见文本

```text
foxos wiki ui text
```

工具接口名：`wiki_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos wiki ui text --json
```

### `foxos wiki ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos wiki ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`wiki_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos wiki ui click --ref e12
foxos wiki ui click --name Settings
```

### `foxos wiki ui type`

向控件输入文本（真实输入事件）

```text
foxos wiki ui type TEXT [--ref REF] [--clear]
```

工具接口名：`wiki_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos wiki ui type 'hello' --ref e5
```

### `foxos wiki ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos wiki ui set --ref REF --value VALUE
```

工具接口名：`wiki_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos wiki ui set 
```

### `foxos wiki ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos wiki ui press KEY [--ref REF]
```

工具接口名：`wiki_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos wiki ui press mod+z
```

### `foxos wiki ui screenshot`

应用窗口截图（PNG）

```text
foxos wiki ui screenshot [--out OUT]
```

工具接口名：`wiki_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos wiki ui screenshot --json
```

### `foxos wiki data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos wiki data list [PATTERN]
```

工具接口名：`wiki_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos wiki data list --json
```

### `foxos wiki data get`

读取应用保存的一项数据

```text
foxos wiki data get KEY
```

工具接口名：`wiki_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos wiki data get X
```

### `foxos wiki module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos wiki module list
```

工具接口名：`wiki_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos wiki module list --json
```

### `foxos wiki module read`

读取应用模块中的值（如 store 状态）

```text
foxos wiki module read TARGET
```

工具接口名：`wiki_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos wiki module read X
```

### `foxos wiki module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos wiki module call TARGET [--args ARGS]
```

工具接口名：`wiki_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos wiki module call X
```

### `foxos wiki op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos wiki op list
```

工具接口名：`wiki_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos wiki op list --json
```

## time-tracking — Time Tracking

效率 · 替代 Toggl Track, Harvest, Clockify。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos time-tracking app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos time-tracking app open [--file FILE] [--headless]
```

工具接口名：`time-tracking_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos time-tracking app open
foxos time-tracking app open --headless --json
```

### `foxos time-tracking app close`

关闭应用实例

```text
foxos time-tracking app close
```

工具接口名：`time-tracking_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos time-tracking app close --json
```

### `foxos time-tracking app status`

应用是否已安装、是否在运行

```text
foxos time-tracking app status
```

工具接口名：`time-tracking_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos time-tracking app status --json
```

### `foxos time-tracking file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos time-tracking file open PATH
```

工具接口名：`time-tracking_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos time-tracking file open X
```

### `foxos time-tracking ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos time-tracking ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`time-tracking_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos time-tracking ui snapshot --json
```

### `foxos time-tracking ui text`

读取界面上的可见文本

```text
foxos time-tracking ui text
```

工具接口名：`time-tracking_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos time-tracking ui text --json
```

### `foxos time-tracking ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos time-tracking ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`time-tracking_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos time-tracking ui click --ref e12
foxos time-tracking ui click --name Settings
```

### `foxos time-tracking ui type`

向控件输入文本（真实输入事件）

```text
foxos time-tracking ui type TEXT [--ref REF] [--clear]
```

工具接口名：`time-tracking_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos time-tracking ui type 'hello' --ref e5
```

### `foxos time-tracking ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos time-tracking ui set --ref REF --value VALUE
```

工具接口名：`time-tracking_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos time-tracking ui set 
```

### `foxos time-tracking ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos time-tracking ui press KEY [--ref REF]
```

工具接口名：`time-tracking_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos time-tracking ui press mod+z
```

### `foxos time-tracking ui screenshot`

应用窗口截图（PNG）

```text
foxos time-tracking ui screenshot [--out OUT]
```

工具接口名：`time-tracking_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos time-tracking ui screenshot --json
```

### `foxos time-tracking data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos time-tracking data list [PATTERN]
```

工具接口名：`time-tracking_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos time-tracking data list --json
```

### `foxos time-tracking data get`

读取应用保存的一项数据

```text
foxos time-tracking data get KEY
```

工具接口名：`time-tracking_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos time-tracking data get X
```

### `foxos time-tracking module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos time-tracking module list
```

工具接口名：`time-tracking_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos time-tracking module list --json
```

### `foxos time-tracking module read`

读取应用模块中的值（如 store 状态）

```text
foxos time-tracking module read TARGET
```

工具接口名：`time-tracking_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos time-tracking module read X
```

### `foxos time-tracking module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos time-tracking module call TARGET [--args ARGS]
```

工具接口名：`time-tracking_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos time-tracking module call X
```

### `foxos time-tracking op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos time-tracking op list
```

工具接口名：`time-tracking_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos time-tracking op list --json
```

## survey — Surveys

效率 · 替代 SurveyMonkey, Google Forms, Typeform。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos survey app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos survey app open [--file FILE] [--headless]
```

工具接口名：`survey_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos survey app open
foxos survey app open --headless --json
```

### `foxos survey app close`

关闭应用实例

```text
foxos survey app close
```

工具接口名：`survey_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos survey app close --json
```

### `foxos survey app status`

应用是否已安装、是否在运行

```text
foxos survey app status
```

工具接口名：`survey_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos survey app status --json
```

### `foxos survey file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos survey file open PATH
```

工具接口名：`survey_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos survey file open X
```

### `foxos survey ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos survey ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`survey_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos survey ui snapshot --json
```

### `foxos survey ui text`

读取界面上的可见文本

```text
foxos survey ui text
```

工具接口名：`survey_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos survey ui text --json
```

### `foxos survey ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos survey ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`survey_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos survey ui click --ref e12
foxos survey ui click --name Settings
```

### `foxos survey ui type`

向控件输入文本（真实输入事件）

```text
foxos survey ui type TEXT [--ref REF] [--clear]
```

工具接口名：`survey_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos survey ui type 'hello' --ref e5
```

### `foxos survey ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos survey ui set --ref REF --value VALUE
```

工具接口名：`survey_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos survey ui set 
```

### `foxos survey ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos survey ui press KEY [--ref REF]
```

工具接口名：`survey_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos survey ui press mod+z
```

### `foxos survey ui screenshot`

应用窗口截图（PNG）

```text
foxos survey ui screenshot [--out OUT]
```

工具接口名：`survey_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos survey ui screenshot --json
```

### `foxos survey data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos survey data list [PATTERN]
```

工具接口名：`survey_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos survey data list --json
```

### `foxos survey data get`

读取应用保存的一项数据

```text
foxos survey data get KEY
```

工具接口名：`survey_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos survey data get X
```

### `foxos survey module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos survey module list
```

工具接口名：`survey_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos survey module list --json
```

### `foxos survey module read`

读取应用模块中的值（如 store 状态）

```text
foxos survey module read TARGET
```

工具接口名：`survey_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos survey module read X
```

### `foxos survey module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos survey module call TARGET [--args ARGS]
```

工具接口名：`survey_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos survey module call X
```

### `foxos survey op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos survey op list
```

工具接口名：`survey_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos survey op list --json
```

## accounting — Accounting

财务 · 替代 QuickBooks Online, Xero, Wave Accounting。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos accounting app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos accounting app open [--file FILE] [--headless]
```

工具接口名：`accounting_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos accounting app open
foxos accounting app open --headless --json
```

### `foxos accounting app close`

关闭应用实例

```text
foxos accounting app close
```

工具接口名：`accounting_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos accounting app close --json
```

### `foxos accounting app status`

应用是否已安装、是否在运行

```text
foxos accounting app status
```

工具接口名：`accounting_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos accounting app status --json
```

### `foxos accounting file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos accounting file open PATH
```

工具接口名：`accounting_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos accounting file open X
```

### `foxos accounting ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos accounting ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`accounting_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos accounting ui snapshot --json
```

### `foxos accounting ui text`

读取界面上的可见文本

```text
foxos accounting ui text
```

工具接口名：`accounting_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos accounting ui text --json
```

### `foxos accounting ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos accounting ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`accounting_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos accounting ui click --ref e12
foxos accounting ui click --name Settings
```

### `foxos accounting ui type`

向控件输入文本（真实输入事件）

```text
foxos accounting ui type TEXT [--ref REF] [--clear]
```

工具接口名：`accounting_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos accounting ui type 'hello' --ref e5
```

### `foxos accounting ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos accounting ui set --ref REF --value VALUE
```

工具接口名：`accounting_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos accounting ui set 
```

### `foxos accounting ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos accounting ui press KEY [--ref REF]
```

工具接口名：`accounting_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos accounting ui press mod+z
```

### `foxos accounting ui screenshot`

应用窗口截图（PNG）

```text
foxos accounting ui screenshot [--out OUT]
```

工具接口名：`accounting_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos accounting ui screenshot --json
```

### `foxos accounting data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos accounting data list [PATTERN]
```

工具接口名：`accounting_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos accounting data list --json
```

### `foxos accounting data get`

读取应用保存的一项数据

```text
foxos accounting data get KEY
```

工具接口名：`accounting_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos accounting data get X
```

### `foxos accounting module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos accounting module list
```

工具接口名：`accounting_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos accounting module list --json
```

### `foxos accounting module read`

读取应用模块中的值（如 store 状态）

```text
foxos accounting module read TARGET
```

工具接口名：`accounting_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos accounting module read X
```

### `foxos accounting module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos accounting module call TARGET [--args ARGS]
```

工具接口名：`accounting_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos accounting module call X
```

### `foxos accounting op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos accounting op list
```

工具接口名：`accounting_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos accounting op list --json
```

## invoicing — Invoicing

财务 · 替代 FreshBooks, Zoho Invoice, Wave Invoicing。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos invoicing app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos invoicing app open [--file FILE] [--headless]
```

工具接口名：`invoicing_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos invoicing app open
foxos invoicing app open --headless --json
```

### `foxos invoicing app close`

关闭应用实例

```text
foxos invoicing app close
```

工具接口名：`invoicing_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos invoicing app close --json
```

### `foxos invoicing app status`

应用是否已安装、是否在运行

```text
foxos invoicing app status
```

工具接口名：`invoicing_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos invoicing app status --json
```

### `foxos invoicing file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos invoicing file open PATH
```

工具接口名：`invoicing_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos invoicing file open X
```

### `foxos invoicing ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos invoicing ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`invoicing_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos invoicing ui snapshot --json
```

### `foxos invoicing ui text`

读取界面上的可见文本

```text
foxos invoicing ui text
```

工具接口名：`invoicing_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos invoicing ui text --json
```

### `foxos invoicing ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos invoicing ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`invoicing_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos invoicing ui click --ref e12
foxos invoicing ui click --name Settings
```

### `foxos invoicing ui type`

向控件输入文本（真实输入事件）

```text
foxos invoicing ui type TEXT [--ref REF] [--clear]
```

工具接口名：`invoicing_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos invoicing ui type 'hello' --ref e5
```

### `foxos invoicing ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos invoicing ui set --ref REF --value VALUE
```

工具接口名：`invoicing_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos invoicing ui set 
```

### `foxos invoicing ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos invoicing ui press KEY [--ref REF]
```

工具接口名：`invoicing_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos invoicing ui press mod+z
```

### `foxos invoicing ui screenshot`

应用窗口截图（PNG）

```text
foxos invoicing ui screenshot [--out OUT]
```

工具接口名：`invoicing_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos invoicing ui screenshot --json
```

### `foxos invoicing data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos invoicing data list [PATTERN]
```

工具接口名：`invoicing_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos invoicing data list --json
```

### `foxos invoicing data get`

读取应用保存的一项数据

```text
foxos invoicing data get KEY
```

工具接口名：`invoicing_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos invoicing data get X
```

### `foxos invoicing module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos invoicing module list
```

工具接口名：`invoicing_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos invoicing module list --json
```

### `foxos invoicing module read`

读取应用模块中的值（如 store 状态）

```text
foxos invoicing module read TARGET
```

工具接口名：`invoicing_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos invoicing module read X
```

### `foxos invoicing module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos invoicing module call TARGET [--args ARGS]
```

工具接口名：`invoicing_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos invoicing module call X
```

### `foxos invoicing op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos invoicing op list
```

工具接口名：`invoicing_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos invoicing op list --json
```

## expense — Expenses

财务 · 替代 Expensify, SAP Concur, Zoho Expense。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos expense app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos expense app open [--file FILE] [--headless]
```

工具接口名：`expense_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos expense app open
foxos expense app open --headless --json
```

### `foxos expense app close`

关闭应用实例

```text
foxos expense app close
```

工具接口名：`expense_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos expense app close --json
```

### `foxos expense app status`

应用是否已安装、是否在运行

```text
foxos expense app status
```

工具接口名：`expense_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos expense app status --json
```

### `foxos expense file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos expense file open PATH
```

工具接口名：`expense_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos expense file open X
```

### `foxos expense ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos expense ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`expense_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos expense ui snapshot --json
```

### `foxos expense ui text`

读取界面上的可见文本

```text
foxos expense ui text
```

工具接口名：`expense_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos expense ui text --json
```

### `foxos expense ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos expense ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`expense_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos expense ui click --ref e12
foxos expense ui click --name Settings
```

### `foxos expense ui type`

向控件输入文本（真实输入事件）

```text
foxos expense ui type TEXT [--ref REF] [--clear]
```

工具接口名：`expense_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos expense ui type 'hello' --ref e5
```

### `foxos expense ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos expense ui set --ref REF --value VALUE
```

工具接口名：`expense_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos expense ui set 
```

### `foxos expense ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos expense ui press KEY [--ref REF]
```

工具接口名：`expense_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos expense ui press mod+z
```

### `foxos expense ui screenshot`

应用窗口截图（PNG）

```text
foxos expense ui screenshot [--out OUT]
```

工具接口名：`expense_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos expense ui screenshot --json
```

### `foxos expense data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos expense data list [PATTERN]
```

工具接口名：`expense_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos expense data list --json
```

### `foxos expense data get`

读取应用保存的一项数据

```text
foxos expense data get KEY
```

工具接口名：`expense_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos expense data get X
```

### `foxos expense module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos expense module list
```

工具接口名：`expense_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos expense module list --json
```

### `foxos expense module read`

读取应用模块中的值（如 store 状态）

```text
foxos expense module read TARGET
```

工具接口名：`expense_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos expense module read X
```

### `foxos expense module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos expense module call TARGET [--args ARGS]
```

工具接口名：`expense_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos expense module call X
```

### `foxos expense op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos expense op list
```

工具接口名：`expense_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos expense op list --json
```

## cap-table — Cap Table

财务 · 替代 Carta, Pulley。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos cap-table app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos cap-table app open [--file FILE] [--headless]
```

工具接口名：`cap-table_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos cap-table app open
foxos cap-table app open --headless --json
```

### `foxos cap-table app close`

关闭应用实例

```text
foxos cap-table app close
```

工具接口名：`cap-table_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cap-table app close --json
```

### `foxos cap-table app status`

应用是否已安装、是否在运行

```text
foxos cap-table app status
```

工具接口名：`cap-table_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cap-table app status --json
```

### `foxos cap-table file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos cap-table file open PATH
```

工具接口名：`cap-table_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos cap-table file open X
```

### `foxos cap-table ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos cap-table ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`cap-table_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos cap-table ui snapshot --json
```

### `foxos cap-table ui text`

读取界面上的可见文本

```text
foxos cap-table ui text
```

工具接口名：`cap-table_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cap-table ui text --json
```

### `foxos cap-table ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos cap-table ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`cap-table_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos cap-table ui click --ref e12
foxos cap-table ui click --name Settings
```

### `foxos cap-table ui type`

向控件输入文本（真实输入事件）

```text
foxos cap-table ui type TEXT [--ref REF] [--clear]
```

工具接口名：`cap-table_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos cap-table ui type 'hello' --ref e5
```

### `foxos cap-table ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos cap-table ui set --ref REF --value VALUE
```

工具接口名：`cap-table_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos cap-table ui set 
```

### `foxos cap-table ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos cap-table ui press KEY [--ref REF]
```

工具接口名：`cap-table_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos cap-table ui press mod+z
```

### `foxos cap-table ui screenshot`

应用窗口截图（PNG）

```text
foxos cap-table ui screenshot [--out OUT]
```

工具接口名：`cap-table_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos cap-table ui screenshot --json
```

### `foxos cap-table data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos cap-table data list [PATTERN]
```

工具接口名：`cap-table_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos cap-table data list --json
```

### `foxos cap-table data get`

读取应用保存的一项数据

```text
foxos cap-table data get KEY
```

工具接口名：`cap-table_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos cap-table data get X
```

### `foxos cap-table module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos cap-table module list
```

工具接口名：`cap-table_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cap-table module list --json
```

### `foxos cap-table module read`

读取应用模块中的值（如 store 状态）

```text
foxos cap-table module read TARGET
```

工具接口名：`cap-table_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos cap-table module read X
```

### `foxos cap-table module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos cap-table module call TARGET [--args ARGS]
```

工具接口名：`cap-table_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos cap-table module call X
```

### `foxos cap-table op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos cap-table op list
```

工具接口名：`cap-table_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos cap-table op list --json
```

## crm — CRM

业务 · 替代 Salesforce, HubSpot CRM, Pipedrive。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos crm app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos crm app open [--file FILE] [--headless]
```

工具接口名：`crm_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos crm app open
foxos crm app open --headless --json
```

### `foxos crm app close`

关闭应用实例

```text
foxos crm app close
```

工具接口名：`crm_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos crm app close --json
```

### `foxos crm app status`

应用是否已安装、是否在运行

```text
foxos crm app status
```

工具接口名：`crm_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos crm app status --json
```

### `foxos crm file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos crm file open PATH
```

工具接口名：`crm_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos crm file open X
```

### `foxos crm ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos crm ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`crm_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos crm ui snapshot --json
```

### `foxos crm ui text`

读取界面上的可见文本

```text
foxos crm ui text
```

工具接口名：`crm_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos crm ui text --json
```

### `foxos crm ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos crm ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`crm_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos crm ui click --ref e12
foxos crm ui click --name Settings
```

### `foxos crm ui type`

向控件输入文本（真实输入事件）

```text
foxos crm ui type TEXT [--ref REF] [--clear]
```

工具接口名：`crm_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos crm ui type 'hello' --ref e5
```

### `foxos crm ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos crm ui set --ref REF --value VALUE
```

工具接口名：`crm_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos crm ui set 
```

### `foxos crm ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos crm ui press KEY [--ref REF]
```

工具接口名：`crm_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos crm ui press mod+z
```

### `foxos crm ui screenshot`

应用窗口截图（PNG）

```text
foxos crm ui screenshot [--out OUT]
```

工具接口名：`crm_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos crm ui screenshot --json
```

### `foxos crm data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos crm data list [PATTERN]
```

工具接口名：`crm_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos crm data list --json
```

### `foxos crm data get`

读取应用保存的一项数据

```text
foxos crm data get KEY
```

工具接口名：`crm_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos crm data get X
```

### `foxos crm module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos crm module list
```

工具接口名：`crm_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos crm module list --json
```

### `foxos crm module read`

读取应用模块中的值（如 store 状态）

```text
foxos crm module read TARGET
```

工具接口名：`crm_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos crm module read X
```

### `foxos crm module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos crm module call TARGET [--args ARGS]
```

工具接口名：`crm_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos crm module call X
```

### `foxos crm op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos crm op list
```

工具接口名：`crm_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos crm op list --json
```

## help-desk — Help Desk

业务 · 替代 Zendesk, Freshdesk, Intercom, Help Scout。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT

### `foxos help-desk app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos help-desk app open [--file FILE] [--headless]
```

工具接口名：`help-desk_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos help-desk app open
foxos help-desk app open --headless --json
```

### `foxos help-desk app close`

关闭应用实例

```text
foxos help-desk app close
```

工具接口名：`help-desk_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos help-desk app close --json
```

### `foxos help-desk app status`

应用是否已安装、是否在运行

```text
foxos help-desk app status
```

工具接口名：`help-desk_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos help-desk app status --json
```

### `foxos help-desk file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos help-desk file open PATH
```

工具接口名：`help-desk_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos help-desk file open X
```

### `foxos help-desk ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos help-desk ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`help-desk_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos help-desk ui snapshot --json
```

### `foxos help-desk ui text`

读取界面上的可见文本

```text
foxos help-desk ui text
```

工具接口名：`help-desk_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos help-desk ui text --json
```

### `foxos help-desk ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos help-desk ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`help-desk_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos help-desk ui click --ref e12
foxos help-desk ui click --name Settings
```

### `foxos help-desk ui type`

向控件输入文本（真实输入事件）

```text
foxos help-desk ui type TEXT [--ref REF] [--clear]
```

工具接口名：`help-desk_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos help-desk ui type 'hello' --ref e5
```

### `foxos help-desk ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos help-desk ui set --ref REF --value VALUE
```

工具接口名：`help-desk_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos help-desk ui set 
```

### `foxos help-desk ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos help-desk ui press KEY [--ref REF]
```

工具接口名：`help-desk_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos help-desk ui press mod+z
```

### `foxos help-desk ui screenshot`

应用窗口截图（PNG）

```text
foxos help-desk ui screenshot [--out OUT]
```

工具接口名：`help-desk_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos help-desk ui screenshot --json
```

### `foxos help-desk data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos help-desk data list [PATTERN]
```

工具接口名：`help-desk_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos help-desk data list --json
```

### `foxos help-desk data get`

读取应用保存的一项数据

```text
foxos help-desk data get KEY
```

工具接口名：`help-desk_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos help-desk data get X
```

### `foxos help-desk module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos help-desk module list
```

工具接口名：`help-desk_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos help-desk module list --json
```

### `foxos help-desk module read`

读取应用模块中的值（如 store 状态）

```text
foxos help-desk module read TARGET
```

工具接口名：`help-desk_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos help-desk module read X
```

### `foxos help-desk module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos help-desk module call TARGET [--args ARGS]
```

工具接口名：`help-desk_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos help-desk module call X
```

### `foxos help-desk op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos help-desk op list
```

工具接口名：`help-desk_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos help-desk op list --json
```

## contracts — Contracts

业务 · 替代 ContractSafe, Juro。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos contracts app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos contracts app open [--file FILE] [--headless]
```

工具接口名：`contracts_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos contracts app open
foxos contracts app open --headless --json
```

### `foxos contracts app close`

关闭应用实例

```text
foxos contracts app close
```

工具接口名：`contracts_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contracts app close --json
```

### `foxos contracts app status`

应用是否已安装、是否在运行

```text
foxos contracts app status
```

工具接口名：`contracts_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contracts app status --json
```

### `foxos contracts file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos contracts file open PATH
```

工具接口名：`contracts_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos contracts file open X
```

### `foxos contracts ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos contracts ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`contracts_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos contracts ui snapshot --json
```

### `foxos contracts ui text`

读取界面上的可见文本

```text
foxos contracts ui text
```

工具接口名：`contracts_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contracts ui text --json
```

### `foxos contracts ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos contracts ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`contracts_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos contracts ui click --ref e12
foxos contracts ui click --name Settings
```

### `foxos contracts ui type`

向控件输入文本（真实输入事件）

```text
foxos contracts ui type TEXT [--ref REF] [--clear]
```

工具接口名：`contracts_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos contracts ui type 'hello' --ref e5
```

### `foxos contracts ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos contracts ui set --ref REF --value VALUE
```

工具接口名：`contracts_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos contracts ui set 
```

### `foxos contracts ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos contracts ui press KEY [--ref REF]
```

工具接口名：`contracts_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos contracts ui press mod+z
```

### `foxos contracts ui screenshot`

应用窗口截图（PNG）

```text
foxos contracts ui screenshot [--out OUT]
```

工具接口名：`contracts_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos contracts ui screenshot --json
```

### `foxos contracts data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos contracts data list [PATTERN]
```

工具接口名：`contracts_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos contracts data list --json
```

### `foxos contracts data get`

读取应用保存的一项数据

```text
foxos contracts data get KEY
```

工具接口名：`contracts_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos contracts data get X
```

### `foxos contracts module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos contracts module list
```

工具接口名：`contracts_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contracts module list --json
```

### `foxos contracts module read`

读取应用模块中的值（如 store 状态）

```text
foxos contracts module read TARGET
```

工具接口名：`contracts_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos contracts module read X
```

### `foxos contracts module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos contracts module call TARGET [--args ARGS]
```

工具接口名：`contracts_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos contracts module call X
```

### `foxos contracts op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos contracts op list
```

工具接口名：`contracts_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos contracts op list --json
```

## pos — Point of Sale

业务 · 替代 Square POS, Shopify POS, Lightspeed。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos pos app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos pos app open [--file FILE] [--headless]
```

工具接口名：`pos_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos pos app open
foxos pos app open --headless --json
```

### `foxos pos app close`

关闭应用实例

```text
foxos pos app close
```

工具接口名：`pos_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pos app close --json
```

### `foxos pos app status`

应用是否已安装、是否在运行

```text
foxos pos app status
```

工具接口名：`pos_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pos app status --json
```

### `foxos pos file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos pos file open PATH
```

工具接口名：`pos_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos pos file open X
```

### `foxos pos ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos pos ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`pos_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos pos ui snapshot --json
```

### `foxos pos ui text`

读取界面上的可见文本

```text
foxos pos ui text
```

工具接口名：`pos_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pos ui text --json
```

### `foxos pos ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos pos ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`pos_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos pos ui click --ref e12
foxos pos ui click --name Settings
```

### `foxos pos ui type`

向控件输入文本（真实输入事件）

```text
foxos pos ui type TEXT [--ref REF] [--clear]
```

工具接口名：`pos_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos pos ui type 'hello' --ref e5
```

### `foxos pos ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos pos ui set --ref REF --value VALUE
```

工具接口名：`pos_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos pos ui set 
```

### `foxos pos ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos pos ui press KEY [--ref REF]
```

工具接口名：`pos_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos pos ui press mod+z
```

### `foxos pos ui screenshot`

应用窗口截图（PNG）

```text
foxos pos ui screenshot [--out OUT]
```

工具接口名：`pos_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos pos ui screenshot --json
```

### `foxos pos data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos pos data list [PATTERN]
```

工具接口名：`pos_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos pos data list --json
```

### `foxos pos data get`

读取应用保存的一项数据

```text
foxos pos data get KEY
```

工具接口名：`pos_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos pos data get X
```

### `foxos pos module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos pos module list
```

工具接口名：`pos_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pos module list --json
```

### `foxos pos module read`

读取应用模块中的值（如 store 状态）

```text
foxos pos module read TARGET
```

工具接口名：`pos_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos pos module read X
```

### `foxos pos module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos pos module call TARGET [--args ARGS]
```

工具接口名：`pos_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos pos module call X
```

### `foxos pos op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos pos op list
```

工具接口名：`pos_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos pos op list --json
```

## inventory — Inventory

业务 · 替代 Zoho Inventory, Sortly, inFlow Inventory。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos inventory app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos inventory app open [--file FILE] [--headless]
```

工具接口名：`inventory_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos inventory app open
foxos inventory app open --headless --json
```

### `foxos inventory app close`

关闭应用实例

```text
foxos inventory app close
```

工具接口名：`inventory_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos inventory app close --json
```

### `foxos inventory app status`

应用是否已安装、是否在运行

```text
foxos inventory app status
```

工具接口名：`inventory_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos inventory app status --json
```

### `foxos inventory file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos inventory file open PATH
```

工具接口名：`inventory_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos inventory file open X
```

### `foxos inventory ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos inventory ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`inventory_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos inventory ui snapshot --json
```

### `foxos inventory ui text`

读取界面上的可见文本

```text
foxos inventory ui text
```

工具接口名：`inventory_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos inventory ui text --json
```

### `foxos inventory ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos inventory ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`inventory_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos inventory ui click --ref e12
foxos inventory ui click --name Settings
```

### `foxos inventory ui type`

向控件输入文本（真实输入事件）

```text
foxos inventory ui type TEXT [--ref REF] [--clear]
```

工具接口名：`inventory_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos inventory ui type 'hello' --ref e5
```

### `foxos inventory ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos inventory ui set --ref REF --value VALUE
```

工具接口名：`inventory_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos inventory ui set 
```

### `foxos inventory ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos inventory ui press KEY [--ref REF]
```

工具接口名：`inventory_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos inventory ui press mod+z
```

### `foxos inventory ui screenshot`

应用窗口截图（PNG）

```text
foxos inventory ui screenshot [--out OUT]
```

工具接口名：`inventory_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos inventory ui screenshot --json
```

### `foxos inventory data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos inventory data list [PATTERN]
```

工具接口名：`inventory_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos inventory data list --json
```

### `foxos inventory data get`

读取应用保存的一项数据

```text
foxos inventory data get KEY
```

工具接口名：`inventory_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos inventory data get X
```

### `foxos inventory module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos inventory module list
```

工具接口名：`inventory_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos inventory module list --json
```

### `foxos inventory module read`

读取应用模块中的值（如 store 状态）

```text
foxos inventory module read TARGET
```

工具接口名：`inventory_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos inventory module read X
```

### `foxos inventory module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos inventory module call TARGET [--args ARGS]
```

工具接口名：`inventory_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos inventory module call X
```

### `foxos inventory op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos inventory op list
```

工具接口名：`inventory_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos inventory op list --json
```

## assets — Assets

业务 · 替代 Asset Panda, EZOfficeInventory。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos assets app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos assets app open [--file FILE] [--headless]
```

工具接口名：`assets_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos assets app open
foxos assets app open --headless --json
```

### `foxos assets app close`

关闭应用实例

```text
foxos assets app close
```

工具接口名：`assets_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos assets app close --json
```

### `foxos assets app status`

应用是否已安装、是否在运行

```text
foxos assets app status
```

工具接口名：`assets_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos assets app status --json
```

### `foxos assets file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos assets file open PATH
```

工具接口名：`assets_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos assets file open X
```

### `foxos assets ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos assets ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`assets_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos assets ui snapshot --json
```

### `foxos assets ui text`

读取界面上的可见文本

```text
foxos assets ui text
```

工具接口名：`assets_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos assets ui text --json
```

### `foxos assets ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos assets ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`assets_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos assets ui click --ref e12
foxos assets ui click --name Settings
```

### `foxos assets ui type`

向控件输入文本（真实输入事件）

```text
foxos assets ui type TEXT [--ref REF] [--clear]
```

工具接口名：`assets_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos assets ui type 'hello' --ref e5
```

### `foxos assets ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos assets ui set --ref REF --value VALUE
```

工具接口名：`assets_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos assets ui set 
```

### `foxos assets ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos assets ui press KEY [--ref REF]
```

工具接口名：`assets_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos assets ui press mod+z
```

### `foxos assets ui screenshot`

应用窗口截图（PNG）

```text
foxos assets ui screenshot [--out OUT]
```

工具接口名：`assets_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos assets ui screenshot --json
```

### `foxos assets data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos assets data list [PATTERN]
```

工具接口名：`assets_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos assets data list --json
```

### `foxos assets data get`

读取应用保存的一项数据

```text
foxos assets data get KEY
```

工具接口名：`assets_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos assets data get X
```

### `foxos assets module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos assets module list
```

工具接口名：`assets_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos assets module list --json
```

### `foxos assets module read`

读取应用模块中的值（如 store 状态）

```text
foxos assets module read TARGET
```

工具接口名：`assets_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos assets module read X
```

### `foxos assets module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos assets module call TARGET [--args ARGS]
```

工具接口名：`assets_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos assets module call X
```

### `foxos assets op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos assets op list
```

工具接口名：`assets_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos assets op list --json
```

## hiring — Hiring

业务 · 替代 Greenhouse, Lever, Workable。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos hiring app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos hiring app open [--file FILE] [--headless]
```

工具接口名：`hiring_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos hiring app open
foxos hiring app open --headless --json
```

### `foxos hiring app close`

关闭应用实例

```text
foxos hiring app close
```

工具接口名：`hiring_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos hiring app close --json
```

### `foxos hiring app status`

应用是否已安装、是否在运行

```text
foxos hiring app status
```

工具接口名：`hiring_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos hiring app status --json
```

### `foxos hiring file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos hiring file open PATH
```

工具接口名：`hiring_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos hiring file open X
```

### `foxos hiring ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos hiring ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`hiring_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos hiring ui snapshot --json
```

### `foxos hiring ui text`

读取界面上的可见文本

```text
foxos hiring ui text
```

工具接口名：`hiring_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos hiring ui text --json
```

### `foxos hiring ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos hiring ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`hiring_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos hiring ui click --ref e12
foxos hiring ui click --name Settings
```

### `foxos hiring ui type`

向控件输入文本（真实输入事件）

```text
foxos hiring ui type TEXT [--ref REF] [--clear]
```

工具接口名：`hiring_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos hiring ui type 'hello' --ref e5
```

### `foxos hiring ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos hiring ui set --ref REF --value VALUE
```

工具接口名：`hiring_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos hiring ui set 
```

### `foxos hiring ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos hiring ui press KEY [--ref REF]
```

工具接口名：`hiring_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos hiring ui press mod+z
```

### `foxos hiring ui screenshot`

应用窗口截图（PNG）

```text
foxos hiring ui screenshot [--out OUT]
```

工具接口名：`hiring_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos hiring ui screenshot --json
```

### `foxos hiring data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos hiring data list [PATTERN]
```

工具接口名：`hiring_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos hiring data list --json
```

### `foxos hiring data get`

读取应用保存的一项数据

```text
foxos hiring data get KEY
```

工具接口名：`hiring_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos hiring data get X
```

### `foxos hiring module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos hiring module list
```

工具接口名：`hiring_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos hiring module list --json
```

### `foxos hiring module read`

读取应用模块中的值（如 store 状态）

```text
foxos hiring module read TARGET
```

工具接口名：`hiring_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos hiring module read X
```

### `foxos hiring module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos hiring module call TARGET [--args ARGS]
```

工具接口名：`hiring_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos hiring module call X
```

### `foxos hiring op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos hiring op list
```

工具接口名：`hiring_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos hiring op list --json
```

## shifts — Shifts

业务 · 替代 Deputy, When I Work, Homebase。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos shifts app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos shifts app open [--file FILE] [--headless]
```

工具接口名：`shifts_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos shifts app open
foxos shifts app open --headless --json
```

### `foxos shifts app close`

关闭应用实例

```text
foxos shifts app close
```

工具接口名：`shifts_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos shifts app close --json
```

### `foxos shifts app status`

应用是否已安装、是否在运行

```text
foxos shifts app status
```

工具接口名：`shifts_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos shifts app status --json
```

### `foxos shifts file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos shifts file open PATH
```

工具接口名：`shifts_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos shifts file open X
```

### `foxos shifts ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos shifts ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`shifts_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos shifts ui snapshot --json
```

### `foxos shifts ui text`

读取界面上的可见文本

```text
foxos shifts ui text
```

工具接口名：`shifts_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos shifts ui text --json
```

### `foxos shifts ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos shifts ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`shifts_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos shifts ui click --ref e12
foxos shifts ui click --name Settings
```

### `foxos shifts ui type`

向控件输入文本（真实输入事件）

```text
foxos shifts ui type TEXT [--ref REF] [--clear]
```

工具接口名：`shifts_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos shifts ui type 'hello' --ref e5
```

### `foxos shifts ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos shifts ui set --ref REF --value VALUE
```

工具接口名：`shifts_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos shifts ui set 
```

### `foxos shifts ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos shifts ui press KEY [--ref REF]
```

工具接口名：`shifts_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos shifts ui press mod+z
```

### `foxos shifts ui screenshot`

应用窗口截图（PNG）

```text
foxos shifts ui screenshot [--out OUT]
```

工具接口名：`shifts_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos shifts ui screenshot --json
```

### `foxos shifts data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos shifts data list [PATTERN]
```

工具接口名：`shifts_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos shifts data list --json
```

### `foxos shifts data get`

读取应用保存的一项数据

```text
foxos shifts data get KEY
```

工具接口名：`shifts_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos shifts data get X
```

### `foxos shifts module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos shifts module list
```

工具接口名：`shifts_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos shifts module list --json
```

### `foxos shifts module read`

读取应用模块中的值（如 store 状态）

```text
foxos shifts module read TARGET
```

工具接口名：`shifts_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos shifts module read X
```

### `foxos shifts module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos shifts module call TARGET [--args ARGS]
```

工具接口名：`shifts_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos shifts module call X
```

### `foxos shifts op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos shifts op list
```

工具接口名：`shifts_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos shifts op list --json
```

## childcare — Childcare

业务 · 替代 brightwheel, Procare, HiMama。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos childcare app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos childcare app open [--file FILE] [--headless]
```

工具接口名：`childcare_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos childcare app open
foxos childcare app open --headless --json
```

### `foxos childcare app close`

关闭应用实例

```text
foxos childcare app close
```

工具接口名：`childcare_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos childcare app close --json
```

### `foxos childcare app status`

应用是否已安装、是否在运行

```text
foxos childcare app status
```

工具接口名：`childcare_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos childcare app status --json
```

### `foxos childcare file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos childcare file open PATH
```

工具接口名：`childcare_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos childcare file open X
```

### `foxos childcare ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos childcare ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`childcare_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos childcare ui snapshot --json
```

### `foxos childcare ui text`

读取界面上的可见文本

```text
foxos childcare ui text
```

工具接口名：`childcare_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos childcare ui text --json
```

### `foxos childcare ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos childcare ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`childcare_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos childcare ui click --ref e12
foxos childcare ui click --name Settings
```

### `foxos childcare ui type`

向控件输入文本（真实输入事件）

```text
foxos childcare ui type TEXT [--ref REF] [--clear]
```

工具接口名：`childcare_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos childcare ui type 'hello' --ref e5
```

### `foxos childcare ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos childcare ui set --ref REF --value VALUE
```

工具接口名：`childcare_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos childcare ui set 
```

### `foxos childcare ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos childcare ui press KEY [--ref REF]
```

工具接口名：`childcare_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos childcare ui press mod+z
```

### `foxos childcare ui screenshot`

应用窗口截图（PNG）

```text
foxos childcare ui screenshot [--out OUT]
```

工具接口名：`childcare_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos childcare ui screenshot --json
```

### `foxos childcare data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos childcare data list [PATTERN]
```

工具接口名：`childcare_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos childcare data list --json
```

### `foxos childcare data get`

读取应用保存的一项数据

```text
foxos childcare data get KEY
```

工具接口名：`childcare_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos childcare data get X
```

### `foxos childcare module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos childcare module list
```

工具接口名：`childcare_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos childcare module list --json
```

### `foxos childcare module read`

读取应用模块中的值（如 store 状态）

```text
foxos childcare module read TARGET
```

工具接口名：`childcare_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos childcare module read X
```

### `foxos childcare module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos childcare module call TARGET [--args ARGS]
```

工具接口名：`childcare_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos childcare module call X
```

### `foxos childcare op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos childcare op list
```

工具接口名：`childcare_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos childcare op list --json
```

## field-service — Field Service

业务 · 替代 Jobber, Housecall Pro, ServiceTitan。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos field-service app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos field-service app open [--file FILE] [--headless]
```

工具接口名：`field-service_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos field-service app open
foxos field-service app open --headless --json
```

### `foxos field-service app close`

关闭应用实例

```text
foxos field-service app close
```

工具接口名：`field-service_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos field-service app close --json
```

### `foxos field-service app status`

应用是否已安装、是否在运行

```text
foxos field-service app status
```

工具接口名：`field-service_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos field-service app status --json
```

### `foxos field-service file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos field-service file open PATH
```

工具接口名：`field-service_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos field-service file open X
```

### `foxos field-service ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos field-service ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`field-service_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos field-service ui snapshot --json
```

### `foxos field-service ui text`

读取界面上的可见文本

```text
foxos field-service ui text
```

工具接口名：`field-service_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos field-service ui text --json
```

### `foxos field-service ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos field-service ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`field-service_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos field-service ui click --ref e12
foxos field-service ui click --name Settings
```

### `foxos field-service ui type`

向控件输入文本（真实输入事件）

```text
foxos field-service ui type TEXT [--ref REF] [--clear]
```

工具接口名：`field-service_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos field-service ui type 'hello' --ref e5
```

### `foxos field-service ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos field-service ui set --ref REF --value VALUE
```

工具接口名：`field-service_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos field-service ui set 
```

### `foxos field-service ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos field-service ui press KEY [--ref REF]
```

工具接口名：`field-service_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos field-service ui press mod+z
```

### `foxos field-service ui screenshot`

应用窗口截图（PNG）

```text
foxos field-service ui screenshot [--out OUT]
```

工具接口名：`field-service_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos field-service ui screenshot --json
```

### `foxos field-service data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos field-service data list [PATTERN]
```

工具接口名：`field-service_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos field-service data list --json
```

### `foxos field-service data get`

读取应用保存的一项数据

```text
foxos field-service data get KEY
```

工具接口名：`field-service_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos field-service data get X
```

### `foxos field-service module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos field-service module list
```

工具接口名：`field-service_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos field-service module list --json
```

### `foxos field-service module read`

读取应用模块中的值（如 store 状态）

```text
foxos field-service module read TARGET
```

工具接口名：`field-service_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos field-service module read X
```

### `foxos field-service module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos field-service module call TARGET [--args ARGS]
```

工具接口名：`field-service_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos field-service module call X
```

### `foxos field-service op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos field-service op list
```

工具接口名：`field-service_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos field-service op list --json
```

## legal — Legal

业务 · 替代 Clio, MyCase, PracticePanther。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos legal app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos legal app open [--file FILE] [--headless]
```

工具接口名：`legal_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos legal app open
foxos legal app open --headless --json
```

### `foxos legal app close`

关闭应用实例

```text
foxos legal app close
```

工具接口名：`legal_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos legal app close --json
```

### `foxos legal app status`

应用是否已安装、是否在运行

```text
foxos legal app status
```

工具接口名：`legal_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos legal app status --json
```

### `foxos legal file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos legal file open PATH
```

工具接口名：`legal_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos legal file open X
```

### `foxos legal ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos legal ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`legal_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos legal ui snapshot --json
```

### `foxos legal ui text`

读取界面上的可见文本

```text
foxos legal ui text
```

工具接口名：`legal_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos legal ui text --json
```

### `foxos legal ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos legal ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`legal_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos legal ui click --ref e12
foxos legal ui click --name Settings
```

### `foxos legal ui type`

向控件输入文本（真实输入事件）

```text
foxos legal ui type TEXT [--ref REF] [--clear]
```

工具接口名：`legal_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos legal ui type 'hello' --ref e5
```

### `foxos legal ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos legal ui set --ref REF --value VALUE
```

工具接口名：`legal_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos legal ui set 
```

### `foxos legal ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos legal ui press KEY [--ref REF]
```

工具接口名：`legal_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos legal ui press mod+z
```

### `foxos legal ui screenshot`

应用窗口截图（PNG）

```text
foxos legal ui screenshot [--out OUT]
```

工具接口名：`legal_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos legal ui screenshot --json
```

### `foxos legal data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos legal data list [PATTERN]
```

工具接口名：`legal_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos legal data list --json
```

### `foxos legal data get`

读取应用保存的一项数据

```text
foxos legal data get KEY
```

工具接口名：`legal_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos legal data get X
```

### `foxos legal module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos legal module list
```

工具接口名：`legal_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos legal module list --json
```

### `foxos legal module read`

读取应用模块中的值（如 store 状态）

```text
foxos legal module read TARGET
```

工具接口名：`legal_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos legal module read X
```

### `foxos legal module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos legal module call TARGET [--args ARGS]
```

工具接口名：`legal_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos legal module call X
```

### `foxos legal op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos legal op list
```

工具接口名：`legal_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos legal op list --json
```

## fleet — Fleet

业务 · 替代 Fleetio, Samsara Fleet Maintenance, Whip Around。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos fleet app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos fleet app open [--file FILE] [--headless]
```

工具接口名：`fleet_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos fleet app open
foxos fleet app open --headless --json
```

### `foxos fleet app close`

关闭应用实例

```text
foxos fleet app close
```

工具接口名：`fleet_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos fleet app close --json
```

### `foxos fleet app status`

应用是否已安装、是否在运行

```text
foxos fleet app status
```

工具接口名：`fleet_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos fleet app status --json
```

### `foxos fleet file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos fleet file open PATH
```

工具接口名：`fleet_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos fleet file open X
```

### `foxos fleet ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos fleet ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`fleet_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos fleet ui snapshot --json
```

### `foxos fleet ui text`

读取界面上的可见文本

```text
foxos fleet ui text
```

工具接口名：`fleet_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos fleet ui text --json
```

### `foxos fleet ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos fleet ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`fleet_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos fleet ui click --ref e12
foxos fleet ui click --name Settings
```

### `foxos fleet ui type`

向控件输入文本（真实输入事件）

```text
foxos fleet ui type TEXT [--ref REF] [--clear]
```

工具接口名：`fleet_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos fleet ui type 'hello' --ref e5
```

### `foxos fleet ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos fleet ui set --ref REF --value VALUE
```

工具接口名：`fleet_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos fleet ui set 
```

### `foxos fleet ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos fleet ui press KEY [--ref REF]
```

工具接口名：`fleet_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos fleet ui press mod+z
```

### `foxos fleet ui screenshot`

应用窗口截图（PNG）

```text
foxos fleet ui screenshot [--out OUT]
```

工具接口名：`fleet_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos fleet ui screenshot --json
```

### `foxos fleet data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos fleet data list [PATTERN]
```

工具接口名：`fleet_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos fleet data list --json
```

### `foxos fleet data get`

读取应用保存的一项数据

```text
foxos fleet data get KEY
```

工具接口名：`fleet_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos fleet data get X
```

### `foxos fleet module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos fleet module list
```

工具接口名：`fleet_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos fleet module list --json
```

### `foxos fleet module read`

读取应用模块中的值（如 store 状态）

```text
foxos fleet module read TARGET
```

工具接口名：`fleet_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos fleet module read X
```

### `foxos fleet module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos fleet module call TARGET [--args ARGS]
```

工具接口名：`fleet_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos fleet module call X
```

### `foxos fleet op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos fleet op list
```

工具接口名：`fleet_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos fleet op list --json
```

## property-management — Property Management

业务 · 替代 Buildium, AppFolio, Rent Manager。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos property-management app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos property-management app open [--file FILE] [--headless]
```

工具接口名：`property-management_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos property-management app open
foxos property-management app open --headless --json
```

### `foxos property-management app close`

关闭应用实例

```text
foxos property-management app close
```

工具接口名：`property-management_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos property-management app close --json
```

### `foxos property-management app status`

应用是否已安装、是否在运行

```text
foxos property-management app status
```

工具接口名：`property-management_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos property-management app status --json
```

### `foxos property-management file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos property-management file open PATH
```

工具接口名：`property-management_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos property-management file open X
```

### `foxos property-management ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos property-management ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`property-management_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos property-management ui snapshot --json
```

### `foxos property-management ui text`

读取界面上的可见文本

```text
foxos property-management ui text
```

工具接口名：`property-management_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos property-management ui text --json
```

### `foxos property-management ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos property-management ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`property-management_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos property-management ui click --ref e12
foxos property-management ui click --name Settings
```

### `foxos property-management ui type`

向控件输入文本（真实输入事件）

```text
foxos property-management ui type TEXT [--ref REF] [--clear]
```

工具接口名：`property-management_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos property-management ui type 'hello' --ref e5
```

### `foxos property-management ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos property-management ui set --ref REF --value VALUE
```

工具接口名：`property-management_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos property-management ui set 
```

### `foxos property-management ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos property-management ui press KEY [--ref REF]
```

工具接口名：`property-management_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos property-management ui press mod+z
```

### `foxos property-management ui screenshot`

应用窗口截图（PNG）

```text
foxos property-management ui screenshot [--out OUT]
```

工具接口名：`property-management_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos property-management ui screenshot --json
```

### `foxos property-management data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos property-management data list [PATTERN]
```

工具接口名：`property-management_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos property-management data list --json
```

### `foxos property-management data get`

读取应用保存的一项数据

```text
foxos property-management data get KEY
```

工具接口名：`property-management_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos property-management data get X
```

### `foxos property-management module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos property-management module list
```

工具接口名：`property-management_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos property-management module list --json
```

### `foxos property-management module read`

读取应用模块中的值（如 store 状态）

```text
foxos property-management module read TARGET
```

工具接口名：`property-management_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos property-management module read X
```

### `foxos property-management module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos property-management module call TARGET [--args ARGS]
```

工具接口名：`property-management_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos property-management module call X
```

### `foxos property-management op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos property-management op list
```

工具接口名：`property-management_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos property-management op list --json
```

## api-client — API Client

开发 · 替代 Postman, Insomnia, Hoppscotch。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos api-client app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos api-client app open [--file FILE] [--headless]
```

工具接口名：`api-client_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos api-client app open
foxos api-client app open --headless --json
```

### `foxos api-client app close`

关闭应用实例

```text
foxos api-client app close
```

工具接口名：`api-client_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos api-client app close --json
```

### `foxos api-client app status`

应用是否已安装、是否在运行

```text
foxos api-client app status
```

工具接口名：`api-client_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos api-client app status --json
```

### `foxos api-client file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos api-client file open PATH
```

工具接口名：`api-client_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos api-client file open X
```

### `foxos api-client ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos api-client ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`api-client_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos api-client ui snapshot --json
```

### `foxos api-client ui text`

读取界面上的可见文本

```text
foxos api-client ui text
```

工具接口名：`api-client_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos api-client ui text --json
```

### `foxos api-client ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos api-client ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`api-client_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos api-client ui click --ref e12
foxos api-client ui click --name Settings
```

### `foxos api-client ui type`

向控件输入文本（真实输入事件）

```text
foxos api-client ui type TEXT [--ref REF] [--clear]
```

工具接口名：`api-client_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos api-client ui type 'hello' --ref e5
```

### `foxos api-client ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos api-client ui set --ref REF --value VALUE
```

工具接口名：`api-client_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos api-client ui set 
```

### `foxos api-client ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos api-client ui press KEY [--ref REF]
```

工具接口名：`api-client_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos api-client ui press mod+z
```

### `foxos api-client ui screenshot`

应用窗口截图（PNG）

```text
foxos api-client ui screenshot [--out OUT]
```

工具接口名：`api-client_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos api-client ui screenshot --json
```

### `foxos api-client data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos api-client data list [PATTERN]
```

工具接口名：`api-client_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos api-client data list --json
```

### `foxos api-client data get`

读取应用保存的一项数据

```text
foxos api-client data get KEY
```

工具接口名：`api-client_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos api-client data get X
```

### `foxos api-client module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos api-client module list
```

工具接口名：`api-client_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos api-client module list --json
```

### `foxos api-client module read`

读取应用模块中的值（如 store 状态）

```text
foxos api-client module read TARGET
```

工具接口名：`api-client_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos api-client module read X
```

### `foxos api-client module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos api-client module call TARGET [--args ARGS]
```

工具接口名：`api-client_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos api-client module call X
```

### `foxos api-client op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos api-client op list
```

工具接口名：`api-client_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos api-client op list --json
```

## chess — Chess

游戏 · 替代 Play against the computer or a friend, with clocks and online play.。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos chess app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos chess app open [--file FILE] [--headless]
```

工具接口名：`chess_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos chess app open
foxos chess app open --headless --json
```

### `foxos chess app close`

关闭应用实例

```text
foxos chess app close
```

工具接口名：`chess_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos chess app close --json
```

### `foxos chess app status`

应用是否已安装、是否在运行

```text
foxos chess app status
```

工具接口名：`chess_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos chess app status --json
```

### `foxos chess file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos chess file open PATH
```

工具接口名：`chess_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos chess file open X
```

### `foxos chess ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos chess ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`chess_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos chess ui snapshot --json
```

### `foxos chess ui text`

读取界面上的可见文本

```text
foxos chess ui text
```

工具接口名：`chess_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos chess ui text --json
```

### `foxos chess ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos chess ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`chess_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos chess ui click --ref e12
foxos chess ui click --name Settings
```

### `foxos chess ui type`

向控件输入文本（真实输入事件）

```text
foxos chess ui type TEXT [--ref REF] [--clear]
```

工具接口名：`chess_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos chess ui type 'hello' --ref e5
```

### `foxos chess ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos chess ui set --ref REF --value VALUE
```

工具接口名：`chess_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos chess ui set 
```

### `foxos chess ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos chess ui press KEY [--ref REF]
```

工具接口名：`chess_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos chess ui press mod+z
```

### `foxos chess ui screenshot`

应用窗口截图（PNG）

```text
foxos chess ui screenshot [--out OUT]
```

工具接口名：`chess_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos chess ui screenshot --json
```

### `foxos chess data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos chess data list [PATTERN]
```

工具接口名：`chess_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos chess data list --json
```

### `foxos chess data get`

读取应用保存的一项数据

```text
foxos chess data get KEY
```

工具接口名：`chess_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos chess data get X
```

### `foxos chess module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos chess module list
```

工具接口名：`chess_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos chess module list --json
```

### `foxos chess module read`

读取应用模块中的值（如 store 状态）

```text
foxos chess module read TARGET
```

工具接口名：`chess_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos chess module read X
```

### `foxos chess module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos chess module call TARGET [--args ARGS]
```

工具接口名：`chess_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos chess module call X
```

### `foxos chess op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos chess op list
```

工具接口名：`chess_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos chess op list --json
```

## backgammon — Backgammon

游戏 · 替代 Play against the computer or a friend, locally or online.。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos backgammon app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos backgammon app open [--file FILE] [--headless]
```

工具接口名：`backgammon_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos backgammon app open
foxos backgammon app open --headless --json
```

### `foxos backgammon app close`

关闭应用实例

```text
foxos backgammon app close
```

工具接口名：`backgammon_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos backgammon app close --json
```

### `foxos backgammon app status`

应用是否已安装、是否在运行

```text
foxos backgammon app status
```

工具接口名：`backgammon_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos backgammon app status --json
```

### `foxos backgammon file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos backgammon file open PATH
```

工具接口名：`backgammon_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos backgammon file open X
```

### `foxos backgammon ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos backgammon ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`backgammon_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos backgammon ui snapshot --json
```

### `foxos backgammon ui text`

读取界面上的可见文本

```text
foxos backgammon ui text
```

工具接口名：`backgammon_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos backgammon ui text --json
```

### `foxos backgammon ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos backgammon ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`backgammon_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos backgammon ui click --ref e12
foxos backgammon ui click --name Settings
```

### `foxos backgammon ui type`

向控件输入文本（真实输入事件）

```text
foxos backgammon ui type TEXT [--ref REF] [--clear]
```

工具接口名：`backgammon_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos backgammon ui type 'hello' --ref e5
```

### `foxos backgammon ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos backgammon ui set --ref REF --value VALUE
```

工具接口名：`backgammon_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos backgammon ui set 
```

### `foxos backgammon ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos backgammon ui press KEY [--ref REF]
```

工具接口名：`backgammon_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos backgammon ui press mod+z
```

### `foxos backgammon ui screenshot`

应用窗口截图（PNG）

```text
foxos backgammon ui screenshot [--out OUT]
```

工具接口名：`backgammon_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos backgammon ui screenshot --json
```

### `foxos backgammon data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos backgammon data list [PATTERN]
```

工具接口名：`backgammon_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos backgammon data list --json
```

### `foxos backgammon data get`

读取应用保存的一项数据

```text
foxos backgammon data get KEY
```

工具接口名：`backgammon_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos backgammon data get X
```

### `foxos backgammon module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos backgammon module list
```

工具接口名：`backgammon_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos backgammon module list --json
```

### `foxos backgammon module read`

读取应用模块中的值（如 store 状态）

```text
foxos backgammon module read TARGET
```

工具接口名：`backgammon_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos backgammon module read X
```

### `foxos backgammon module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos backgammon module call TARGET [--args ARGS]
```

工具接口名：`backgammon_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos backgammon module call X
```

### `foxos backgammon op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos backgammon op list
```

工具接口名：`backgammon_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos backgammon op list --json
```

## checkers — Checkers

游戏 · 替代 American checkers against the computer or a friend.。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos checkers app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos checkers app open [--file FILE] [--headless]
```

工具接口名：`checkers_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos checkers app open
foxos checkers app open --headless --json
```

### `foxos checkers app close`

关闭应用实例

```text
foxos checkers app close
```

工具接口名：`checkers_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos checkers app close --json
```

### `foxos checkers app status`

应用是否已安装、是否在运行

```text
foxos checkers app status
```

工具接口名：`checkers_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos checkers app status --json
```

### `foxos checkers file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos checkers file open PATH
```

工具接口名：`checkers_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos checkers file open X
```

### `foxos checkers ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos checkers ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`checkers_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos checkers ui snapshot --json
```

### `foxos checkers ui text`

读取界面上的可见文本

```text
foxos checkers ui text
```

工具接口名：`checkers_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos checkers ui text --json
```

### `foxos checkers ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos checkers ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`checkers_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos checkers ui click --ref e12
foxos checkers ui click --name Settings
```

### `foxos checkers ui type`

向控件输入文本（真实输入事件）

```text
foxos checkers ui type TEXT [--ref REF] [--clear]
```

工具接口名：`checkers_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos checkers ui type 'hello' --ref e5
```

### `foxos checkers ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos checkers ui set --ref REF --value VALUE
```

工具接口名：`checkers_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos checkers ui set 
```

### `foxos checkers ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos checkers ui press KEY [--ref REF]
```

工具接口名：`checkers_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos checkers ui press mod+z
```

### `foxos checkers ui screenshot`

应用窗口截图（PNG）

```text
foxos checkers ui screenshot [--out OUT]
```

工具接口名：`checkers_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos checkers ui screenshot --json
```

### `foxos checkers data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos checkers data list [PATTERN]
```

工具接口名：`checkers_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos checkers data list --json
```

### `foxos checkers data get`

读取应用保存的一项数据

```text
foxos checkers data get KEY
```

工具接口名：`checkers_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos checkers data get X
```

### `foxos checkers module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos checkers module list
```

工具接口名：`checkers_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos checkers module list --json
```

### `foxos checkers module read`

读取应用模块中的值（如 store 状态）

```text
foxos checkers module read TARGET
```

工具接口名：`checkers_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos checkers module read X
```

### `foxos checkers module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos checkers module call TARGET [--args ARGS]
```

工具接口名：`checkers_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos checkers module call X
```

### `foxos checkers op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos checkers op list
```

工具接口名：`checkers_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos checkers op list --json
```

## solitaire — Solitaire

游戏 · 替代 Klondike (draw one or three, optional Vegas scoring) and Spider solitaire, with optional cloud saves.。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos solitaire app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos solitaire app open [--file FILE] [--headless]
```

工具接口名：`solitaire_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos solitaire app open
foxos solitaire app open --headless --json
```

### `foxos solitaire app close`

关闭应用实例

```text
foxos solitaire app close
```

工具接口名：`solitaire_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos solitaire app close --json
```

### `foxos solitaire app status`

应用是否已安装、是否在运行

```text
foxos solitaire app status
```

工具接口名：`solitaire_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos solitaire app status --json
```

### `foxos solitaire file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos solitaire file open PATH
```

工具接口名：`solitaire_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos solitaire file open X
```

### `foxos solitaire ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos solitaire ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`solitaire_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos solitaire ui snapshot --json
```

### `foxos solitaire ui text`

读取界面上的可见文本

```text
foxos solitaire ui text
```

工具接口名：`solitaire_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos solitaire ui text --json
```

### `foxos solitaire ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos solitaire ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`solitaire_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos solitaire ui click --ref e12
foxos solitaire ui click --name Settings
```

### `foxos solitaire ui type`

向控件输入文本（真实输入事件）

```text
foxos solitaire ui type TEXT [--ref REF] [--clear]
```

工具接口名：`solitaire_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos solitaire ui type 'hello' --ref e5
```

### `foxos solitaire ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos solitaire ui set --ref REF --value VALUE
```

工具接口名：`solitaire_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos solitaire ui set 
```

### `foxos solitaire ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos solitaire ui press KEY [--ref REF]
```

工具接口名：`solitaire_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos solitaire ui press mod+z
```

### `foxos solitaire ui screenshot`

应用窗口截图（PNG）

```text
foxos solitaire ui screenshot [--out OUT]
```

工具接口名：`solitaire_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos solitaire ui screenshot --json
```

### `foxos solitaire data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos solitaire data list [PATTERN]
```

工具接口名：`solitaire_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos solitaire data list --json
```

### `foxos solitaire data get`

读取应用保存的一项数据

```text
foxos solitaire data get KEY
```

工具接口名：`solitaire_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos solitaire data get X
```

### `foxos solitaire module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos solitaire module list
```

工具接口名：`solitaire_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos solitaire module list --json
```

### `foxos solitaire module read`

读取应用模块中的值（如 store 状态）

```text
foxos solitaire module read TARGET
```

工具接口名：`solitaire_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos solitaire module read X
```

### `foxos solitaire module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos solitaire module call TARGET [--args ARGS]
```

工具接口名：`solitaire_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos solitaire module call X
```

### `foxos solitaire op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos solitaire op list
```

工具接口名：`solitaire_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos solitaire op list --json
```

## sudoku — Sudoku

游戏 · 替代 Four difficulty levels, daily puzzles, and hints that explain the logic.。上游 Everything 应用，在狐狸OS 中本地运行。

限制：

- 许可证：MIT (root LICENSE)

### `foxos sudoku app open`

打开应用（桌面窗口；--headless 用无界面实例）

```text
foxos sudoku app open [--file FILE] [--headless]
```

工具接口名：`sudoku_app_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `--file` | string |  | 同时打开工作空间中的文件；工作空间路径（read） |
| `headless` | `--headless` | boolean |  | 不显示窗口 |

示例：

```bash
foxos sudoku app open
foxos sudoku app open --headless --json
```

### `foxos sudoku app close`

关闭应用实例

```text
foxos sudoku app close
```

工具接口名：`sudoku_app_close` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sudoku app close --json
```

### `foxos sudoku app status`

应用是否已安装、是否在运行

```text
foxos sudoku app status
```

工具接口名：`sudoku_app_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sudoku app status --json
```

### `foxos sudoku file open`

在应用中打开工作空间里的文件（与在文件管理器里双击相同）

```text
foxos sudoku file open PATH
```

工具接口名：`sudoku_file_open` · 权限：`run`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos sudoku file open X
```

### `foxos sudoku ui snapshot`

界面可访问性快照：可交互元素及其引用（ref）、角色、名称、值

```text
foxos sudoku ui snapshot [--all] [--limit LIMIT]
```

工具接口名：`sudoku_ui_snapshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `all` | `--all` | boolean |  | 包括不可见元素 |
| `limit` | `--limit` | integer |  | 最多返回元素数；默认 400 |

示例：

```bash
foxos sudoku ui snapshot --json
```

### `foxos sudoku ui text`

读取界面上的可见文本

```text
foxos sudoku ui text
```

工具接口名：`sudoku_ui_text` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sudoku ui text --json
```

### `foxos sudoku ui click`

点击控件（按 ref 或名称），与人点击相同

```text
foxos sudoku ui click [--ref REF] [--name NAME] [--role ROLE]
```

工具接口名：`sudoku_ui_click` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string |  | snapshot 返回的元素引用 |
| `name` | `--name` | string |  | 按可访问名称查找 |
| `role` | `--role` | string |  | 限定角色，如 button |

示例：

```bash
foxos sudoku ui click --ref e12
foxos sudoku ui click --name Settings
```

### `foxos sudoku ui type`

向控件输入文本（真实输入事件）

```text
foxos sudoku ui type TEXT [--ref REF] [--clear]
```

工具接口名：`sudoku_ui_type` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `text` | `TEXT` | string | 是 | 要输入的文本 |
| `ref` | `--ref` | string |  | 元素引用，缺省为当前焦点 |
| `clear` | `--clear` | boolean |  | 先清空 |

示例：

```bash
foxos sudoku ui type 'hello' --ref e5
```

### `foxos sudoku ui set`

设置输入框 / 下拉框 / 复选框的值

```text
foxos sudoku ui set --ref REF --value VALUE
```

工具接口名：`sudoku_ui_set` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ref` | `--ref` | string | 是 | 元素引用 |
| `value` | `--value` | string | 是 | 值 |

示例：

```bash
foxos sudoku ui set 
```

### `foxos sudoku ui press`

按键或快捷键（如 Enter、ctrl+z、mod+s）

```text
foxos sudoku ui press KEY [--ref REF]
```

工具接口名：`sudoku_ui_press` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 按键 |
| `ref` | `--ref` | string |  | 先聚焦的元素引用 |

示例：

```bash
foxos sudoku ui press mod+z
```

### `foxos sudoku ui screenshot`

应用窗口截图（PNG）

```text
foxos sudoku ui screenshot [--out OUT]
```

工具接口名：`sudoku_ui_screenshot` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `out` | `--out` | string |  | 保存到工作空间路径；工作空间路径（write） |

示例：

```bash
foxos sudoku ui screenshot --json
```

### `foxos sudoku data list`

列出应用保存的数据键（工作空间 AppData/<应用>/kv.json）

```text
foxos sudoku data list [PATTERN]
```

工具接口名：`sudoku_data_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `pattern` | `PATTERN` | string |  | 通配符；默认 * |

示例：

```bash
foxos sudoku data list --json
```

### `foxos sudoku data get`

读取应用保存的一项数据

```text
foxos sudoku data get KEY
```

工具接口名：`sudoku_data_get` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `key` | `KEY` | string | 是 | 数据键 |

示例：

```bash
foxos sudoku data get X
```

### `foxos sudoku module list`

列出应用自己的 ES 模块及导出（供 module call 使用）

```text
foxos sudoku module list
```

工具接口名：`sudoku_module_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sudoku module list --json
```

### `foxos sudoku module read`

读取应用模块中的值（如 store 状态）

```text
foxos sudoku module read TARGET
```

工具接口名：`sudoku_module_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.属性，如 src/lib/store.js#store.tasks |

示例：

```bash
foxos sudoku module read X
```

### `foxos sudoku module call`

调用应用自己的函数 / 方法（应用内部逻辑，与界面调用同一代码）

```text
foxos sudoku module call TARGET [--args ARGS]
```

工具接口名：`sudoku_module_call` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `target` | `TARGET` | string | 是 | 模块路径#导出.方法 |
| `args` | `--args` | array |  | 参数（JSON 数组） |

示例：

```bash
foxos sudoku module call X
```

### `foxos sudoku op list`

列出该应用的操作清单（界面路径、快捷键、参数、是否已有语义命令）

```text
foxos sudoku op list
```

工具接口名：`sudoku_op_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos sudoku op list --json
```

## sheets — 表格：读写标准 .xlsx 工作簿、公式、图表与导出

基于 openpyxl 读写 Excel 2007+ (.xlsx) 文件；公式按 Excel 语法写入（以 = 开头），用 LibreOffice 无头模式求值与导出 PDF/ODS。

限制：

- 只读写 .xlsx；.xls / .xlsm / .ods / .csv 输入暂不支持
- 公式以文本写入，求值依赖 LibreOffice（read --computed、export）
- 图表仅支持 bar / line / pie，数据按列组成系列
- 单次 read 最多返回 20000 个单元格

### `foxos sheets create`

新建一个 .xlsx 工作簿

```text
foxos sheets create FILE [--sheet SHEET] [--headers HEADERS] [--force]
```

工具接口名：`sheets_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 要创建的工作簿路径（.xlsx）；工作空间路径（write） |
| `sheet` | `--sheet / -s` | string |  | 第一个工作表的名称；默认 Sheet1 |
| `headers` | `--headers` | array |  | 第一行表头，逗号分隔（CLI）或字符串数组（工具接口） |
| `force` | `--force / -f` | boolean |  | 文件已存在时覆盖（上一版本会保存到 .foxos/versions） |

示例：

```bash
foxos sheets create sales.xlsx --sheet Sales --headers Month,Sales
foxos sheets create report/q1.xlsx --force --json
```

限制：

- 只创建 .xlsx；父目录不存在时自动创建

### `foxos sheets read`

读取工作表单元格（公式、图表；可选用 LibreOffice 求值）

```text
foxos sheets read FILE [--sheet SHEET] [--range RANGE] [--computed]
```

工具接口名：`sheets_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（read） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `range` | `--range / -r` | string |  | A1 记法区域，如 A1:C10；默认整个已用区域 |
| `computed` | `--computed` | boolean |  | 用 LibreOffice 重算公式，额外返回 values（不修改原文件） |

示例：

```bash
foxos sheets read sales.xlsx
foxos sheets read sales.xlsx --range A1:B13 --computed --json
```

限制：

- 单次最多 20000 个单元格
- --computed 需要 LibreOffice

### `foxos sheets write`

写入单元格值或公式（CELL=VALUE，以 = 开头为公式）

```text
foxos sheets write FILE CELL=VALUE... [--sheet SHEET] [--create-sheet]
```

工具接口名：`sheets_write` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（write） |
| `cells` | `CELL=VALUE` | object | 是 | 要写入的单元格：{"A1": "Month", "B2": 120, "B14": "=SUM(B2:B13)"}；CLI 中写成 A1=Month B2=120 B14==SUM(B2:B13)，数字自动识别，TRUE/FALSE 为布尔，空值清空单元格 |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `create_sheet` | `--create-sheet` | boolean |  | 工作表不存在时新建 |

示例：

```bash
foxos sheets write sales.xlsx A2=Jan B2=120 A3=Feb B3=135
foxos sheets write sales.xlsx 'B14==SUM(B2:B13)' --sheet Sales
foxos sheets write sales.xlsx --cells-json '{"C2": "=B2*1.1"}' --json
```

限制：

- 公式按 Excel 英文函数名写入，不在写入时校验或求值
- 不支持写入样式、合并单元格（阶段 0）

### `foxos sheets chart create`

基于单元格区域创建原生 Excel 图表

```text
foxos sheets chart create FILE --type {bar,line,pie} --data DATA [--categories CATEGORIES] [--title TITLE] [--sheet SHEET] [--anchor ANCHOR] [--x-title X_TITLE] [--y-title Y_TITLE] [--no-header]
```

工具接口名：`sheets_chart_create` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（write） |
| `type` | `--type / -t` | string | 是 | 图表类型；可选：bar / line / pie |
| `data` | `--data / -d` | string | 是 | 数据区域（按列为系列，首行默认为系列名），如 B1:B13 |
| `categories` | `--categories / -c` | string |  | 分类（X 轴）区域，如 A2:A13 |
| `title` | `--title` | string |  | 图表标题 |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `anchor` | `--anchor / -a` | string |  | 图表左上角所在单元格，默认放在数据右侧 |
| `x_title` | `--x-title` | string |  | X 轴标题（bar/line） |
| `y_title` | `--y-title` | string |  | Y 轴标题（bar/line） |
| `no_header` | `--no-header` | boolean |  | 数据区域首行不是系列名 |

示例：

```bash
foxos sheets chart create sales.xlsx --type bar --data B1:B13 --categories A2:A13 --title '月度销售额'
foxos sheets chart create sales.xlsx -t line -d B1:C13 -c A2:A13 --anchor E20 --json
```

限制：

- 仅 bar / line / pie
- 饼图只能一个系列
- 图表样式、颜色暂不可配置

### `foxos sheets chart list`

列出工作簿中的图表

```text
foxos sheets chart list FILE [--sheet SHEET]
```

工具接口名：`sheets_chart_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 工作簿路径；工作空间路径（read） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |

示例：

```bash
foxos sheets chart list sales.xlsx --json
```

### `foxos sheets export`

导出为 csv / pdf / ods / xlsx（格式由输出文件扩展名决定）

```text
foxos sheets export FILE OUTPUT [--sheet SHEET] [--force]
```

工具接口名：`sheets_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 源工作簿路径；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径：.csv / .pdf / .ods / .xlsx；工作空间路径（write） |
| `sheet` | `--sheet / -s` | string |  | 工作表名称，默认当前活动工作表 |
| `force` | `--force / -f` | boolean |  | 输出文件已存在时覆盖 |

示例：

```bash
foxos sheets export sales.xlsx sales.csv
foxos sheets export sales.xlsx out/sales.pdf --force --json
```

限制：

- csv 只导出一个工作表，公式导出为求值结果（需 LibreOffice，否则导出公式文本）
- pdf / ods 需要 LibreOffice

## slides — 演示：读写标准 .pptx（标题页、要点页、图片、原生图表、备注），替换文本与导出

基于 python-pptx 读写 PowerPoint 2007+ (.pptx)，使用默认模板的标准版式。

限制：

- 只读写 .pptx；.ppt / .odp 输入暂不支持
- 版式来自默认模板：title / title-content / section / two-content / title-only / blank
- 图表仅 bar / line / pie，数据直接给出（不链接外部 xlsx）

### `foxos slides create`

新建一个 .pptx 演示文稿（可带标题页）

```text
foxos slides create FILE [--title TITLE] [--subtitle SUBTITLE] [--aspect {16:9,4:3}] [--force]
```

工具接口名：`slides_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `title` | `--title` | string |  | 标题页标题 |
| `subtitle` | `--subtitle` | string |  | 标题页副标题 |
| `aspect` | `--aspect` | string |  | 页面比例；可选：16:9 / 4:3；默认 16:9 |
| `force` | `--force / -f` | boolean |  | 已存在时覆盖 |

示例：

```bash
foxos slides create deck.pptx --title '2026 年销售分析' --subtitle '数据组'
```

### `foxos slides read`

读取每页的版式、标题、文本、图表数据与备注

```text
foxos slides read FILE
```

工具接口名：`slides_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（read） |

示例：

```bash
foxos slides read deck.pptx --json
```

### `foxos slides add`

追加一页（标题 + 要点 / 图片 / 备注）

```text
foxos slides add FILE [--title TITLE] [--bullet BULLET] [--layout {title,title-content,section,two-content,title-only,blank}] [--image IMAGE] [--notes NOTES]
```

工具接口名：`slides_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `title` | `--title / -t` | string |  | 页面标题 |
| `bullet` | `--bullet / -b` | array |  | 要点，可重复：--bullet 一 --bullet 二 |
| `layout` | `--layout` | string |  | 版式；可选：title / title-content / section / two-content / title-only / blank |
| `image` | `--image` | string |  | 插入图片（工作空间内 png/jpg）；工作空间路径（read） |
| `notes` | `--notes` | string |  | 演讲者备注 |

示例：

```bash
foxos slides add deck.pptx -t 全年概况 -b '销售额 2013 万元' -b '同比增长 12%'
foxos slides add deck.pptx -t 趋势 --image charts/trend.png
```

### `foxos slides chart add`

插入原生 PowerPoint 图表（默认新建一页）

```text
foxos slides chart add FILE --type {bar,line,pie} --categories CATEGORIES --values VALUES [--slide SLIDE] [--series-name SERIES_NAME] [--title TITLE]
```

工具接口名：`slides_chart_add` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `type` | `--type / -T` | string | 是 | 图表类型；可选：bar / line / pie |
| `categories` | `--categories / -c` | array | 是 | 分类，逗号分隔 |
| `values` | `--values / -v` | array | 是 | 数值，逗号分隔，与分类一一对应 |
| `slide` | `--slide` | integer |  | 插入到已有的第 N 页（从 1 开始）；不填则新建一页 |
| `series_name` | `--series-name` | string |  | 系列名称；默认 Series 1 |
| `title` | `--title` | string |  | 新建页时的页面标题 |

示例：

```bash
foxos slides chart add deck.pptx --type bar -c Q1,Q2,Q3,Q4 -v 405,428,547,633 --title 季度销售额
```

### `foxos slides replace`

查找并替换所有页中的文本

```text
foxos slides replace FILE --find FIND --replace REPLACE
```

工具接口名：`slides_replace` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（write） |
| `find` | `--find` | string | 是 | 要查找的文本 |
| `replace` | `--replace` | string | 是 | 替换为 |

示例：

```bash
foxos slides replace deck.pptx --find 2025 --replace 2026
```

限制：

- 只在同一个文本 run 内匹配

### `foxos slides export`

导出为 pdf / odp

```text
foxos slides export FILE OUTPUT [--force]
```

工具接口名：`slides_export` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `file` | `FILE` | string | 是 | 演示文稿路径（.pptx）；工作空间路径（read） |
| `output` | `OUTPUT` | string | 是 | 输出路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 输出已存在时覆盖 |

示例：

```bash
foxos slides export deck.pptx deck.pdf
```

限制：

- 需要 LibreOffice

## workspace — 工作空间信息

当前工作空间根目录与基本信息。

### `foxos workspace info`

显示工作空间根目录、审计日志位置与文件数

```text
foxos workspace info
```

工具接口名：`workspace_info` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos workspace info --json
```

## files — 文件：列出、读写文本、新建、重命名、删除与恢复

所有操作限定在工作空间内，删除进入回收站；.foxos 保留目录不可见。

### `foxos files list`

列出目录内容（默认工作空间根目录）

```text
foxos files list [PATH] [--recursive] [--hidden]
```

工具接口名：`files_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string |  | 目录（工作空间内），默认根目录；工作空间路径（read） |
| `recursive` | `--recursive / -r` | boolean |  | 递归列出所有文件 |
| `hidden` | `--hidden / -a` | boolean |  | 包含以 . 开头的文件 |

示例：

```bash
foxos files list
foxos files list reports --json
foxos files list -r
```

### `foxos files read`

读取 UTF-8 文本文件

```text
foxos files read PATH
```

工具接口名：`files_read` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（read） |

示例：

```bash
foxos files read notes.md
foxos files read src/app.py --json
```

限制：

- 上限 5 MB；二进制与办公文件请用对应应用命令

### `foxos files write`

写入 UTF-8 文本文件（原子保存，覆盖前保留上一版）

```text
foxos files write PATH --content CONTENT [--expect-mtime EXPECT_MTIME] [--force]
```

工具接口名：`files_write` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件路径；工作空间路径（write） |
| `content` | `--content` | string | 是 | 文件内容；CLI 可用 --content-stdin 从标准输入读取 |
| `expect_mtime` | `--expect-mtime` | number |  | 乐观并发检查：文件当前修改时间必须等于该值，否则 CONFLICT |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files write notes.md --content '# 标题'
cat a.py | foxos files write src/a.py --content-stdin
```

### `foxos files mkdir`

新建文件夹（含父目录）

```text
foxos files mkdir PATH
```

工具接口名：`files_mkdir` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 文件夹路径；工作空间路径（write） |

示例：

```bash
foxos files mkdir reports/2026
```

### `foxos files rename`

重命名或移动文件 / 文件夹

```text
foxos files rename SOURCE TARGET [--force]
```

工具接口名：`files_rename` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `source` | `SOURCE` | string | 是 | 原路径；工作空间路径（write） |
| `target` | `TARGET` | string | 是 | 新路径；工作空间路径（write） |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files rename draft.md final.md
foxos files rename a.xlsx archive/a.xlsx
```

### `foxos files delete`

删除文件或文件夹（移入回收站，可恢复）

```text
foxos files delete PATH
```

工具接口名：`files_delete` · 权限：`delete`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string | 是 | 要删除的路径；工作空间路径（write） |

示例：

```bash
foxos files delete old.csv
```

限制：

- 移入 .foxos/trash/，用 foxos files restore 恢复

### `foxos files restore`

从回收站恢复

```text
foxos files restore TRASH_ID [--force]
```

工具接口名：`files_restore` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `trash_id` | `TRASH_ID` | string | 是 | 回收站条目 ID（files delete 返回，或 files trash 查看） |
| `force` | `--force / -f` | boolean |  | 目标已存在时覆盖 |

示例：

```bash
foxos files restore 20261110T2051-ab12cd
```

### `foxos files trash`

列出回收站

```text
foxos files trash
```

工具接口名：`files_trash` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos files trash --json
```

## audit — 审计日志

查询 .foxos/audit.jsonl：谁在什么时候对什么文件执行了什么命令。

### `foxos audit tail`

查看最近的审计记录

```text
foxos audit tail [--limit LIMIT] [--filter-agent AGENT] [--command COMMAND]
```

工具接口名：`audit_tail` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `limit` | `--limit / -n` | integer |  | 返回条数；默认 20 |
| `agent` | `--filter-agent` | string |  | 只看某个智能体 |
| `command` | `--command` | string |  | 按命令前缀过滤，如 sheets.write |

示例：

```bash
foxos audit tail -n 50
foxos audit tail --filter-agent data-agent --json
```

限制：

- 查询本身不写入审计日志

## queue — 任务队列

记录任务目标与状态；由桌面的 ACP 智能体会话执行。

### `foxos queue create`

把一个任务目标加入队列

```text
foxos queue create GOAL
```

工具接口名：`queue_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `goal` | `GOAL` | string | 是 | 任务目标（自然语言） |

示例：

```bash
foxos queue create '根据 sales.xlsx 制作分析报告'
```

限制：

- 只记录任务；执行由 ACP 智能体会话完成

### `foxos queue list`

列出任务队列

```text
foxos queue list [--limit LIMIT]
```

工具接口名：`queue_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `limit` | `--limit / -n` | integer |  | 返回条数；默认 20 |

示例：

```bash
foxos queue list --json
```

## control — 人工接管

暂停后，非 human 身份的调用者不能执行任何写操作（读操作不受影响），返回 PAUSED（退出码 8）。

### `foxos control status`

查看是否处于人工接管（暂停）状态

```text
foxos control status
```

工具接口名：`control_status` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos control status --json
```

限制：

- 查询本身不写入审计日志

### `foxos control pause`

人工接管：暂停所有智能体的写操作

```text
foxos control pause [--reason REASON]
```

工具接口名：`control_pause` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `reason` | `--reason` | string |  | 暂停原因（写入状态与审计） |

示例：

```bash
foxos control pause --reason '我来改第 3 页数据'
```

限制：

- 只有 human 身份可以执行
- 身份由调用方声明（--agent），属于应用层约束

### `foxos control resume`

结束人工接管，恢复智能体写操作

```text
foxos control resume
```

工具接口名：`control_resume` · 权限：`modify`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| — | | | | 无参数 |

示例：

```bash
foxos control resume
```

限制：

- 只有 human 身份可以执行
