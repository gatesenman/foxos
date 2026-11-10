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

## files — 列出工作空间文件

只读列出工作空间内的文件，忽略 .foxos 保留目录。

### `foxos files list`

列出工作空间内的文件

```text
foxos files list [PATH]
```

工具接口名：`files_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `path` | `PATH` | string |  | 子目录（工作空间内），默认根目录；工作空间路径（read） |

示例：

```bash
foxos files list
foxos files list reports --json
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

## tasks — 任务队列

阶段 0 只记录任务，尚未接入模型自动执行。

### `foxos tasks create`

把一个任务目标加入队列

```text
foxos tasks create GOAL
```

工具接口名：`tasks_create` · 权限：`create`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `goal` | `GOAL` | string | 是 | 任务目标（自然语言） |

示例：

```bash
foxos tasks create '根据 sales.xlsx 制作分析报告'
```

限制：

- 阶段 0 只记录任务，不会自动调用模型执行

### `foxos tasks list`

列出任务队列

```text
foxos tasks list [--limit LIMIT]
```

工具接口名：`tasks_list` · 权限：`read`

| 参数 | CLI | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `limit` | `--limit / -n` | integer |  | 返回条数；默认 20 |

示例：

```bash
foxos tasks list --json
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
