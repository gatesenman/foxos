# 环境：狐狸OS 自带的隔离运行环境

狐狸OS 自己实现了一层隔离环境，不依赖 Docker、Podman、LXC、VirtualBox、QEMU。
三个平台各用系统自带的机制：

| 平台 | 后端 ID | 实现 | 状态 |
|---|---|---|---|
| Linux | `linux-ns` | 自研运行时 `foxos/envs/linux.py`：用户命名空间（无特权）+ mount / pid / uts / ipc / 可选 net 命名空间、overlayfs、pivot_root、seccomp、cgroup v2（可委派时）或 rlimit | 在本机（内核 6.12，普通用户 uid 1000）端到端测试通过 |
| Windows | `wsl2` | 驱动系统自带的 WSL2（`wsl.exe --import/--exec/--terminate/--export/--unregister`），进程限制用 Job Object | 有代码和单元测试（命令构造、路径换算、输出解析），**未在 Windows 实机上测试** |
| macOS | `macos-vz` | Swift 小程序 `FoxVZ.swift` 调用 Virtualization.framework（Linux 内核引导、virtio 磁盘 / 网络 NAT / virtio-fs 共享工作空间 / 控制台） | 有代码和单元测试（配置生成、命令构造），**未在 Mac 实机上测试** |

## 三个入口，同一套命令

- CLI：`foxos env <动词>`（见下表），加 `--json` 输出机器可读结果
- MCP：工具 `env_<动词>`（如 `env_create`、`env_exec`），与 CLI 由同一份命令定义生成
- 图形界面：桌面上的“环境”应用（开始菜单、应用中心、桌面图标）。界面上的每个按钮都调用同一个内核命令，审计记为 `human:desktop`；
  CLI / MCP / 智能体的操作会通过审计事件让界面实时刷新

| 动词 | 作用 | 界面位置 |
|---|---|---|
| `images` | 官方镜像目录与本地镜像 | 左下“镜像” |
| `pull IMAGE [--sha256]` | 下载镜像（目录 ID、https 地址或 .foxenv 文件）并校验 sha256 | 镜像页“下载” / “从地址安装” |
| `create NAME --image --network host\|none --workspace-mode rw\|ro\|none [--memory-mb --cpus --pids]` | 创建环境 | “新建” |
| `list` / `info NAME` | 列表 / 详情（配置、快照、操作、cgroup 状态） | 左侧列表 / 详情页 |
| `start` / `stop` / `restart` | 启停 | 快捷操作 |
| `exec NAME -- CMD…` | 在环境里执行命令（默认工作目录 /workspace），返回退出码、stdout、stderr | 自定义操作的“运行” |
| `shell NAME` | 交互式 shell | “终端”（在内置终端窗口里打开） |
| `clone NAME NEW` | 复制可写层与设置 | “克隆” |
| `snapshot NAME [--label]` / `restore NAME SNAPSHOT` | 快照 / 恢复（需先停止） | “快照”页 |
| `export NAME --out FILE` / `import FILE --name` | 导出 / 导入 `.foxenv` | “导出” / 左下“导入” |
| `delete NAME` | 删除环境（不删镜像、不动工作空间） | “删除” |
| `mount NAME --source --target [--readonly] [--remove]` | 宿主目录挂载 | “设置”页 → 挂载 |
| `limits NAME [--memory-mb --cpus --pids --network --workspace-mode]` | 资源限制、网络、工作空间权限 | “设置”页 |
| `stats [NAME]` | 进程数、CPU 时间、内存、可写层磁盘 | “概览”页（每 2 秒刷新） |
| `logs NAME [-n]` | 环境日志与 init 日志 | “日志”页 |
| `action add NAME ACTION --command` / `action run NAME ACTION` | 自定义操作，支持 `${env}` `${image}` `${workspace}` `${host_workspace}` `${hostname}` 变量 | “自定义操作”页 |

## 镜像格式 `.foxenv`

一个 tar 文件，内含：

- `manifest.json`：`{"format": "foxenv/1", "id", "name", "arch", "source", "created", "shell", "rootfs": "rootfs.tar.zst", "sha256"}`
- `rootfs.tar.zst`：根文件系统（zstd 压缩的 tar），`sha256` 为它的摘要，导入时校验

镜像来源：官方发行版 rootfs（Alpine minirootfs、Ubuntu base，下载时用发行方公布的 SHA256 校验），
任意 https 地址（`.tar.gz` / `.tar.zst` / `.foxenv`，可用 `--sha256` 指定期望值），以及 GitHub Releases 上发布的 `.foxenv`。

存储位置：`FOXOS_HOME/envs/images/<id>/`（只读层），`FOXOS_HOME/envs/instances/<名字>/{env.json, upper, work, merged, logs, snapshots, run}`。

## Linux 运行时细节

启动（`foxos env start`）时：

1. 监督进程读取 uid/gid 后 `unshare(CLONE_NEWUSER)`，写 `uid_map`（`0 <uid> 1`）、`setgroups=deny`、`gid_map`，在环境里是 root、在宿主上仍是普通用户
2. `unshare(NEWPID | NEWUTS | NEWIPC [| NEWNET])`，fork 出环境的 1 号进程；1 号进程自己 `unshare(NEWNS)`（不影响监督进程的根）
3. 挂载：根设为 rprivate；overlayfs（`lowerdir=镜像, upperdir, workdir, userxattr`，用户命名空间内的无特权 overlay）；`/proc`；`/sys`（无网络时挂新的 sysfs，否则只读绑定）；
   tmpfs `/dev` 并绑定 null / zero / full / random / urandom / tty，devpts（newinstance）、shm、fd 链接；tmpfs `/tmp` `/run`；`resolv.conf`；
   工作空间绑定到 `/workspace`（只读模式下再 remount 只读）；用户挂载；狐狸OS 安装的 ACP 智能体只读挂到 `/opt/foxos/agents`
4. `pivot_root` 到新根并卸载旧根
5. 无网络模式下只拉起回环网卡 `lo`
6. 资源限制，然后安装 seccomp 过滤器（拒绝 kexec、内核模块、reboot、swap、时钟设置、bpf、perf_event_open、userfaultfd、keyctl、iopl、open_by_handle_at 等，返回 EPERM）
7. 1 号进程回收僵尸进程；`stop` 向它发 SIGTERM，超时后 SIGKILL

`exec` 用 `setns` 依次加入环境的 user、mnt、pid、uts、ipc（和 net）命名空间，fork 后 chdir、加限制与 seccomp，再 `execvpe`。

### 本机内核不允许、或做不到的部分（如实说明）

- **cgroup v2 资源限制**：只有当前用户的 cgroup 已委派（目录可写）时才用 cgroup（`memory.max`、`pids.max`、`cpu.max`，按整个环境计算）。
  本机 `/sys/fs/cgroup/agent` 属于 root、不可写，所以回退到 rlimit：内存用 `RLIMIT_AS`（每个进程的地址空间），进程数用 `RLIMIT_NPROC`（按用户计算），
  **CPU 上限在这种情况下不生效**。`foxos env info` 的 `cgroup` 与 `limits_note` 字段会写明当前用的是哪一种
- **网络**：`host` 共享宿主网络命名空间；`none` 是独立的网络命名空间，只有 `lo`。没有实现 NAT / 端口转发（无特权情况下需要 slirp 之类的用户态网络栈）
- **设备**：不能 mknod，`/dev` 里的设备节点是从宿主绑定的
- **uid 映射**：无特权下只能映射一个 uid（环境里的 root ↔ 宿主的当前用户）；环境内创建其他用户的文件，在宿主上都属于当前用户。
  因此需要多个 uid 的软件（例如以 `nobody` 身份运行的服务）在环境里会以 root 身份运行
- **镜像里的设备文件**：解包时跳过 `./dev/*`，不保留属主（`--no-same-owner`）
- **在环境里执行 `reboot`**：seccomp 拒绝 reboot 系统调用；busybox 的 `reboot` 会改为向 1 号进程发 SIGTERM，效果是环境停止

## 在环境里运行智能体

桌面右侧面板的“运行位置”可以选一个运行中的环境（Linux 后端）。启动后：

- 智能体进程在环境里运行，工作目录 `/workspace`，ACP 的 `session/new` 的 `cwd` 为 `/workspace`；
  智能体请求读写文件时，`/workspace/...` 会换算回宿主的工作空间路径，仍然经过狐狸OS 内核（工作空间约束、写锁、人工接管、审计）
- 智能体程序来自宿主上狐狸OS 安装的智能体目录（只读挂在 `/opt/foxos/agents`）。npm 类智能体需要环境里有 Node.js（例如 `foxos env exec dev -- apk add nodejs`）；
  二进制类智能体需要与环境的 C 库兼容（Alpine 是 musl，Ubuntu 是 glibc）
- foxos MCP：宿主启动一个只监听 127.0.0.1 的 Streamable HTTP MCP 服务器（随机端口 + 随机令牌），以 `type: http` 注入给智能体。
  需要环境共享宿主网络（`--network host`）且智能体声明支持 HTTP MCP；否则不注入，并在会话里提示
- 智能体身份仍是 `acp:<智能体 ID>`，审计里能看到

## 安装器

安装器（`install.sh` / `install.ps1`）和桌面的安装向导都把“环境”作为一个组件：Linux 上检查用户命名空间是否可用（`unshare -U true`）并预下载 Alpine 镜像；
Windows 上检查 / 启用 WSL2；macOS 上编译 `FoxVZ` 辅助程序（需要 Xcode 命令行工具）。

## 测试

- `packages/core/tests/test_envs.py`：US-30 ～ US-36，真实地在本机创建、启动、执行、隔离检查（只读工作空间、无网络、主机名、pid 命名空间、seccomp）、快照恢复、克隆、导出导入、挂载、限制、自定义操作、日志、审计与人工接管；
  Windows / macOS 后端的单元测试
- `apps/desktop/e2e/environments.e2e.js`：US-37，用 Playwright 驱动真实桌面：在界面上新建、启动、运行自定义操作、快照，并用 CLI 核对状态一致；CLI 停止后界面实时刷新

参考：界面布局参考了 wsl-ui 的思路（仪表盘、快捷操作、自定义操作）。wsl-ui 是 GPL-3.0 项目，狐狸OS 没有使用它的任何代码、素材或文字。
