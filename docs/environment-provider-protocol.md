# 环境提供者协议（foxos-env-provider/1）

狐狸OS 的“环境”由**提供者（provider）**实现。不同平台的隔离 / 虚拟化机制（Linux 命名空间、WSL2、Windows Sandbox、Hyper-V、
Virtualization.framework …）都接到同一组 `foxos env` 命令、同一个 MCP 工具集和同一个“环境”应用上。

* 协议版本：`foxos-env-provider/1`（破坏性变更会升到 `/2`，狐狸OS 拒绝版本不匹配的提供者，返回 `CONFLICT`）
* JSON Schema：`packages/core/foxos/data/schemas/env-provider.schema.json`
* 目录格式：`foxos-env-catalog/1`，Schema 为 `packages/core/foxos/data/schemas/env-catalog.schema.json`
* 代码：`packages/core/foxos/envs/providers.py`

## 1. 内置提供者

| ID | 宿主 | 来宾 | 隔离级别 | 能力 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `linux-ns` | Linux | Linux | full（独立根文件系统 + 命名空间） | create start stop exec shell snapshot restore clone export import mount limits stats logs agent | 已实现，端到端测试 |
| `wsl2` | Windows | Linux | full（WSL2 轻量虚拟机中的发行版） | create start stop exec shell export import delete list-online agent | 已实现，单元测试；未在 Windows 硬件验证 |
| `windows-sandbox` | Windows 专业/企业/教育版 | Windows | full（一次性虚拟机） | create start delete | 已实现（.wsb 生成），单元测试；未在硬件验证 |
| `hyperv` | Windows 专业/企业/教育版 | Windows / 任意 ISO | full（虚拟机） | create start stop delete snapshot restore export import limits | 创建 / 启动已实现（PowerShell cmdlet），单元测试；未在硬件验证 |
| `macos-vz` | macOS | Linux | full（Virtualization.framework） | create start stop exec | 代码 + 单元测试；未在硬件验证 |
| `macos-guest` | — | macOS | — | 无 | 列出但禁用：Apple 许可只允许在 Apple 硬件上的 macOS 中虚拟化 macOS |

`foxos env providers --json` 列出全部提供者（含第三方）及 `doctor` 结果；`foxos env doctor` 只检查本机可用的提供者。

## 2. 方法

所有提供者（进程内或进程外）实现同一组方法：

| 方法 | 参数 | 结果 |
| --- | --- | --- |
| `initialize` | `{protocol, client}` | `{protocol, id}`（仅进程外；协议版本协商） |
| `describe` | — | `{id, name, protocol, platforms[], guest_os, isolation, capabilities[]}` |
| `doctor` | — | `{available, reason, checks[{id, ok, detail}], actions[step]}` |
| `plan_install` | `{entry, name, opts}` | `{steps: [step]}` |
| `plan`（保留） | `{op, name, opts}` | `{steps: [step]}`，`op` ∈ start / stop / delete / exec / export / snapshot / restore |

**计划与执行分离**：提供者只返回“步骤”，由狐狸OS 统一执行、记审计、报告进度。这样每条要执行的命令行都可以在任何平台上
做单元测试（“命令契约”），用户和智能体也可以先 `--dry-run` 审阅。

### 步骤（step）

恰好包含下列一种动作：

| 字段 | 含义 |
| --- | --- |
| `argv: [..]` | 运行一个程序（不经 shell） |
| `powershell: ".."` | 运行一段 PowerShell |
| `download: url, to, sha256, convert?` | 下载（或复制本地文件）并校验 sha256；`convert: "tar.gz"` 表示把 .tar.xz 转成 wsl --import 接受的 .tar.gz |
| `write: path, content` | 写文件（如 .wsb） |
| `foxos: [..], workspace?` | 运行一条 foxos 子命令 |

附加字段：`why`（给人看的说明）、`elevate`（需要管理员；Windows 上用 `Start-Process -Verb RunAs -Wait` 弹出 UAC）、
`confirm`（执行前需用户确认，如重启）、`manual`（只能由用户手动完成，如在 BIOS 中开启虚拟化）、`registers`（该步注册的发行版 / 虚拟机名）、
`ok_codes`（视为成功的非零退出码）。

执行器（`providers.execute`）的约定：下载步骤 sha256 不匹配立即失败（`CONFLICT`）；退出码 3010 或输出包含“需要重启”的消息时返回
`CONFLICT` + 重启提示；进度写入 `<FOXOS_HOME>/envs/instances/<名>/install.json`，`foxos env progress <名>` 读取。

## 3. 进程外提供者（JSON-RPC 2.0 over stdio）

第三方提供者放在 `<FOXOS_HOME>/providers/<id>/`，包含清单 `provider.json`：

```json
{
  "protocol": "foxos-env-provider/1",
  "id": "my-vm",
  "name": "My VM",
  "version": "0.1.0",
  "platforms": ["linux", "windows"],
  "guest_os": "linux",
  "isolation": "full",
  "capabilities": ["create", "start", "stop", "exec"],
  "command": ["./my-vm-provider", "--stdio"]
}
```

狐狸OS 启动 `command`，按行写入 JSON-RPC 请求，按行读取响应：

```
→ {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocol":"foxos-env-provider/1","client":"foxos"}}
← {"jsonrpc":"2.0","id":1,"result":{"protocol":"foxos-env-provider/1","id":"my-vm"}}
→ {"jsonrpc":"2.0","id":2,"method":"plan_install","params":{"entry":{…},"name":"dev","opts":{…}}}
← {"jsonrpc":"2.0","id":2,"result":{"steps":[{"argv":["my-vm","create","dev"],"why":"创建虚拟机"}]}}
```

错误用标准 JSON-RPC `error`，可在 `error.data.code` 放狐狸OS 错误码（`NOT_FOUND`、`DEPENDENCY_MISSING` …）。
提供者 ID 不能与内置提供者重名；协议版本不符的清单会被忽略。示例与测试见 `packages/core/tests/test_env_windows.py::test_external_provider_jsonrpc`。

## 4. 系统目录（foxos-env-catalog/1）

`packages/core/foxos/data/env-catalog.json`，由 `scripts/gen_env_catalog.py` 生成：

```json
{"format": "foxos-env-catalog/1", "version": "2026.11.10", "entries": [
  {"id": "wsl-ubuntu-24.04", "name": "Ubuntu 24.04 LTS", "family": "ubuntu", "guest_os": "linux", "arch": ["x86_64", "aarch64"],
   "providers": ["wsl2", "linux-ns"],
   "source": {"kind": "rootfs", "url": "https://releases.ubuntu.com/…-wsl-amd64.wsl", "sha256": "…", "wsl_name": "Ubuntu-24.04"}}
]}
```

`source.kind`：

| kind | 含义 | 解析 |
| --- | --- | --- |
| `rootfs` | 固定地址的根文件系统（.wsl / .tar.gz / .tar.xz），附 `sha256` 或 `sha256_url` | 直接使用；arm64 主机用 `source.arm64` |
| `wsl-store` | 只在应用商店提供的发行版（如 Oracle Linux） | `wsl.exe --install -d <wsl_name> --no-launch` |
| `alpine` | Alpine 官方 minirootfs 最新版 | 读取 `latest-releases.yaml` 得到文件名与 sha256 |
| `lxc` | LXC 镜像服务器每日构建 | 读取 `meta/1.0/index-system` 找最新构建，再读该构建的 `SHA256SUMS` |
| `custom` | 用户提供的 URL / 本地文件 | 需要 `--url`，可选 `--sha256` |
| `host` | 宿主自带（Windows Sandbox） | — |
| `iso` | 从安装介质创建虚拟机（Hyper-V） | 需要 `--iso`；`download_page` 指向官方下载页 |
| `none` | 不可安装（`disabled: true` + `reason`） | — |

来源与许可：WSL 条目来自 microsoft/WSL 的 `distributions/DistributionInfo.json`（MIT，快照与许可声明见 `packages/core/foxos/data/wsl/`）；
其余来自各发行版官方镜像站与 images.linuxcontainers.org。目录只记录地址与校验值，不包含任何发行版文件。

## 5. 命令

```
foxos env providers                         # 提供者与可用性
foxos env doctor [--provider wsl2]          # 检查本机能力，列出修复操作
foxos env fix --provider wsl2 --action enable-wsl   # 执行修复（UAC 确认，可能需要重启）
foxos env catalog [--guest linux|windows|macos|any] [--available]
foxos env install <条目> <名> [--provider P] [--url U --sha256 S] [--iso PATH] [--memory-mb N --cpus N --disk-gb N] [--location DIR] [--dry-run]
foxos env progress <名>                      # 安装进度
```

同名 MCP 工具：`env_providers`、`env_doctor`、`env_fix`、`env_catalog`、`env_install`、`env_progress`。

## 预设目录 `foxos-env-presets/1`

狐狸OS 预设（[presets.md](presets.md)）和普通目录条目合并显示在 `foxos env catalog` 里，条目带 `"preset": true`。文件 `packages/core/foxos/data/env-presets.json`：

```json
{"format": "foxos-env-presets/1", "version": "2026.11",
 "release_base": "https://github.com/gatesenman/foxos/releases/download",
 "entries": [{
   "id": "foxos-debian-12", "kind": "foxos-image", "guest_os": "linux", "release": "presets-2026.11", "disk_gb": 8,
   "features": ["desktop-xfce", "zh-CN", "node", "bun", "python", "acp-gemini-cli", "foxos-cli", "foxos-mcp", "foxos-bridge-ssh"],
   "artifacts": {"qcow2": {"name": "foxos-debian-12.qcow2", "size": 0, "sha256": "…",
                           "parts": [{"name": "foxos-debian-12.qcow2.part1", "size": 0, "sha256": "…"}]},
                 "wsl":   {"name": "foxos-debian-12-wsl.tar.gz", "size": 0, "sha256": "…"}},
   "hosts": {"linux": {"provider": "linux-kvm", "artifact": "qcow2", "arch": ["x86_64"]},
             "windows": {"provider": "wsl2", "artifact": "wsl", "arch": ["x86_64"]}},
   "unavailable": {"macos": "原因（显示在界面上）"}}]}
```

- `kind`：`foxos-image`（qcow2 / WSL 根文件系统）、`foxos-iso`、`windows-media`（`media.url` 指向微软官方，带 `size`、`license`、`tpm`）、`macos-ipsw`。
- 下载地址 = `release_base/release/name`；每个分卷与整体都有 `size` 与 `sha256`。`FOXOS_PRESETS_BASE` 可指向镜像站（同样的目录结构，`file://` 也可以），`FOXOS_PRESETS_FILE` 可替换整个目录文件。
- `env catalog` 给每个条目算出 `installable`、`reason`、`host_providers`、`download_bytes`、`disk_bytes`（下载 + 解压后的磁盘 + 余量）。
