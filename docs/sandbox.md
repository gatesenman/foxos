# 轻量隔离（foxos sandbox）

轻量隔离是进程级沙箱：程序直接运行在宿主上，用宿主上已经装好的工具链，没有启动开销；但它只能读写工作空间（和你声明的路径），可以选择不联网。
它和 [完整隔离（foxos env）](environments.md) 互补：完整隔离提供独立的根文件系统 / 虚拟机，能随意装软件、快照、导出；轻量隔离适合“用宿主工具跑一个不完全信任的智能体或脚本”。

## 用法

```bash
foxos sandbox check --json                                   # 本机能用哪些机制（Landlock ABI、网络 / 信号隔离）
foxos sandbox run --json -- python3 build.py                 # 只能读写工作空间
foxos sandbox run --network off --json -- npm test           # 再加上不联网
foxos sandbox run --read ~/datasets --write ~/.cache/pip --json -- python3 train.py
foxos sandbox policy --network off --json -- node agent.js   # 只显示将生效的规则，不执行
```

注意 `--json` 等选项要放在 `--` 之前；`--` 之后的内容原样作为命令。

桌面端：会话面板的“运行位置”选择 **轻量沙箱** 或 **轻量沙箱（不联网）** 后启动智能体。
foxos MCP 服务器运行在沙箱外（宿主上的 Streamable HTTP，随机端口 + 随机令牌），所以 Everything 应用和桌面控制仍然可用；不联网时沙箱只放行到这个端口的 TCP 连接。
不支持 HTTP MCP 的智能体退回 stdio MCP，此时 MCP 服务器和智能体一起运行在沙箱里。

## 策略

| 项 | 默认 | 说明 |
| --- | --- | --- |
| 工作空间 | 读写 | 当前工作空间 |
| 系统目录 | 只读 | Linux：/usr /bin /lib /etc /opt /proc /sys 等；macOS：/System /usr /Library 等；Windows：系统目录与 Program Files |
| 程序目录 | 只读 | 要运行的程序的安装目录（可执行文件真实路径的上一级；虚拟环境、`#!` 解释器也会加入） |
| HOME | 私有 | `--home private`：`FOXOS_HOME/sandbox/<配置>/home`；`read`：真实 HOME 只读；`write`：真实 HOME 可写 |
| 临时目录 | 私有 | `FOXOS_HOME/sandbox/<配置>/tmp`，设为 TMPDIR |
| 额外路径 | 无 | `--read PATH`、`--write PATH`（可重复） |
| 网络 | 允许 | `--network off` 禁止 |

## 各平台实现

### Linux：Landlock + seccomp（已实现，端到端测试）

启动器（`python -m foxos.sandbox exec|wrap`）在 execve 目标程序之前对自身施加限制，之后整棵进程树都继承且无法解除：

1. `prctl(PR_SET_NO_NEW_PRIVS)`：setuid 程序不能再提权。
2. Landlock 规则集（按内核 ABI 自动选择能力）：
   - 文件系统：只有上表的路径有访问权（只读 = 执行 / 读文件 / 读目录；读写 = 当前 ABI 的全部权限）；`/dev` 允许读写设备与 ioctl（终端），`/dev/shm` 读写；
   - 不联网（ABI ≥ 4，内核 6.7+）：禁止所有 TCP bind / connect，只放行声明的端口；
   - 作用域（ABI ≥ 6，内核 6.12+）：不能向沙箱外的进程发信号，不能连接沙箱外的抽象 unix 套接字。
3. seccomp 过滤器：拒绝（EPERM）加载内核模块、kexec、bpf、perf、ptrace、process_vm_*、mount / pivot_root / chroot、unshare / setns、带命名空间标志的 clone、io_uring、keyctl 等；
   clone3 返回 ENOSYS（参数在结构体里无法检查，libc 会退回 clone）；非本机 ABI（x86_64 上的 i386 / x32 入口）一律拒绝；
   不联网时拒绝 AF_INET / AF_INET6 / AF_PACKET 套接字（放行端口时只允许 TCP 流套接字，UDP 和原始套接字仍拒绝）。

内核没有启用 Landlock 时 `foxos sandbox run` 返回 DEPENDENCY_MISSING，不会在没有隔离的情况下运行。
已知限制：Landlock 的端口规则不区分目标地址（放行的端口在任意主机上都可连接）；`/proc` 只读可见（能看到其他进程的命令行，但不能向它们发信号或 ptrace）。

### macOS：Seatbelt（代码与单元测试，未在 Mac 实机验证）

按策略生成 SBPL 配置文件并用 `/usr/bin/sandbox-exec -p` 运行：默认拒绝；系统目录、程序目录与只读路径可读；只有工作空间、私有 tmp / HOME 与可写路径可写；
不联网时只允许 unix 套接字；只能向同一沙箱内的进程发信号。`foxos sandbox policy --json` 可以看到生成的配置。

### Windows：受限令牌或 AppContainer + 作业对象（代码与单元测试，未在 Windows 实机验证）

- `--windows-mode restricted`（默认）：`CreateRestrictedToken`（去掉特权、管理员组仅拒绝）并把令牌设为低完整性级别。
  强制完整性控制禁止低完整性进程写入中 / 高完整性的文件、注册表和进程，所以只有被 `icacls /setintegritylevel (OI)(CI)low` 标记的目录（工作空间、私有 tmp / HOME、可写路径）可写。
  这一模式**不限制读取和网络**。
- `--windows-mode appcontainer`：在 AppContainer 中运行（`CreateAppContainerProfile` + `SECURITY_CAPABILITIES`），默认不能访问用户文件、不能联网；
  按策略给 AppContainer SID 授予工作空间（完全控制）与只读路径（读取和执行）的 ACL，联网时授予 internetClient / privateNetworkClientServer 能力。很多桌面程序在 AppContainer 中不能正常运行。
- 两种模式都放进作业对象：启动器结束时整组进程一起结束、可选进程数 / 内存上限、界面限制（不能切换桌面、改显示设置、注销关机、读剪贴板、操作作业外的窗口句柄）。

## 测试

- `packages/core/tests/test_sandbox.py`（US-52）：真实运行——工作空间可写、外部不可读写、子进程继承、声明路径、私有 HOME、网络开 / 关 / 放行单端口、UDP、ptrace / unshare、NoNewPrivs 与 Seccomp 状态、信号作用域；以及 seccomp 程序（x86_64 / aarch64）、Seatbelt 配置与 Windows ACL 计划的生成。
- `apps/desktop/e2e/sandbox.e2e.js`（US-52）：在桌面会话面板选择“轻量沙箱（不联网）”启动真实的 Gemini CLI（ACP），检查智能体进程的 NoNewPrivs、Seccomp、私有 HOME。
- `test_windows_code_path_under_wine`：设置 `FOXOS_TEST_WINE`、`FOXOS_TEST_WINE_PYTHON` 后，用打包进 Windows 版的嵌入式 Python 在 wine 中走一遍 Windows 代码路径（受限令牌、作业对象、管道、退出码）。
  wine 不实现强制完整性控制，也不实现 AppContainer（`CreateAppContainerProfile` 返回 E_NOTIMPL），所以这只证明代码路径能走通，不证明隔离有效。
