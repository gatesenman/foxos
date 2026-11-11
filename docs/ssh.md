# SSH 远程访问 / SSH remote access

狐狸OS 默认开着 OpenSSH（端口 22），让人和智能体从别的电脑连进来。默认设置偏安全：

| 项 | 安装后的系统 | 现场（Live）会话 |
| --- | --- | --- |
| sshd | 开机自启 | 开机自启 |
| 密钥登录 | 开（安装程序或首次登录时粘贴 / 导入公钥） | 开（从标签为 `FOXOSSEED` 的光盘 / U 盘导入 `authorized_keys`） |
| 密码登录 | **关**；只有在安装程序 / 首次登录向导里勾选并设一个强密码才开 | 开，但只接受开机时随机生成的一次性 16 位密码 |
| root 登录 | 禁止（`PermitRootLogin no`） | 禁止 |
| 防火墙 ufw | 开，放行 22/tcp | 开，放行 22/tcp |
| 主机密钥 | 每台机器首次开机时生成（镜像里不带） | 每次开机生成 |

配置写在 `/etc/ssh/sshd_config.d/10-foxos.conf`（`PubkeyAuthentication yes`、`PasswordAuthentication no|yes`、`KbdInteractiveAuthentication no`、`PermitRootLogin no`、`MaxAuthTries 4`）。

## 现场会话

开机后桌面弹出一个警告窗口，桌面上还有 `SSH-登录信息.txt`，控制台（tty1 和串口）与登录提示里也会打印：

```
ssh foxos@192.168.1.23        一次性密码：Xq7…（16 位）
警告：现场会话里任何知道这个密码的人都能登录；用完请关机，或运行 foxos ssh password off
```

不想在现场会话开 SSH：开机菜单里按 `e`，在内核参数末尾加 `foxos.live_ssh=off`。

预先放公钥：做一张卷标为 `FOXOSSEED` 的光盘或 U 盘，根目录放 `authorized_keys`，开机时会导入给 `foxos` 用户。

## 安装时与首次登录

- 点「安装狐狸OS」时先弹出 SSH 设置：粘贴公钥、选一个公钥文件，或填 `github:用户名` 从 GitHub 导入；可选「允许密码登录」，密码至少 12 位、包含 3 类字符、不含用户名、不是常见密码。
- 安装程序最后一步（`shellprocess@ssh`）把公钥写进新用户的 `~/.ssh/authorized_keys`，重新生成主机密钥，默认关掉密码登录。
- 没在安装时设置的，首次登录时会再问一次（之后可随时用下面的命令改）。

面板「系统」菜单第一项显示 `ssh 用户@地址`，点开能看到详细状态与 MCP-over-SSH 的用法。

## 命令（CLI 与 MCP 对等）

| CLI | MCP 工具 | 谁能用 |
| --- | --- | --- |
| `foxos ssh status` | `ssh_status` | 所有人 |
| `foxos ssh enable` | `ssh_enable` | 只有人（human） |
| `foxos ssh disable` | `ssh_disable` | 所有人（只会收紧） |
| `foxos ssh keys add --key/--file/--github` | `ssh_keys_add` | 只有人 |
| `foxos ssh keys list` | `ssh_keys_list` | 所有人 |
| `foxos ssh keys remove N/指纹` | `ssh_keys_remove` | 所有人 |
| `foxos ssh password on [--new-password]` / `off` | `ssh_password` | `on` 只有人，并且要 sudo / pkexec 认证；`off` 所有人 |

改系统设置的部分经 `/usr/lib/foxos/foxos-ssh-admin`；sudoers 只对「收紧」类操作（status、enable、disable、password-off）免密，打开密码登录、设密码都要认证。

## 智能体经 SSH 连进来

```bash
ssh foxos@<地址> foxos runtime doctor --json          # 直接跑命令
ssh foxos@<地址> foxos --workspace ~/FoxOS/workspace mcp   # MCP over SSH（stdio）
```

MCP 客户端配置示例（Claude Code / Codex / Gemini CLI 通用的 stdio 形式）：

```json
{"mcpServers": {"foxos": {"command": "ssh", "args": ["-T", "foxos@192.168.1.23", "foxos", "--workspace", "~/FoxOS/workspace", "mcp"]}}}
```

## 虚拟环境（预设系统）的 SSH

`linux-kvm` 环境启动时把客户机的 22 端口转发到主机的一个端口（默认只在 `127.0.0.1`），`foxos env exec` 就走这条 SSH。`foxos env list` 显示连接命令：

```
running  dev  …
      ssh: ssh -p 40211 -i ~/.local/share/foxos/envs/dev/ssh/id_ed25519 foxos@127.0.0.1
```

要从别的电脑直接连虚拟机：`foxos env expose dev --ssh on --port 2222`（只有人能开；下次启动生效；绑定到 `0.0.0.0`，主机防火墙要放行 2222）。`--ssh off` 收回到本机。

## 测过什么

- `tests/test_ssh.py`（US-64）：公钥增删查、GitHub 导入、智能体不能开门、密码强度、MCP 对等、智能体不能对外开放虚拟机 SSH。
- `tests/test_os_iso_e2e.py`（US-65）：启动真实 ISO，经 qemu `hostfwd` 用密钥登录、错误密码和 root 被拒、经 SSH 运行 foxos 和 MCP；装到虚拟磁盘重启后，密钥可登录、密码被拒。结果见 [test-report.md](test-report.md)。

## English summary

OpenSSH is on by default on port 22. Key login works out of the box (keys come from the installer / first-run wizard, a `github:USER` import, or a `FOXOSSEED` seed disc in the live session). Password login is off on installed systems unless you turn it on with a strong password; root login is always off; ufw allows 22/tcp. The live session prints its address and a one-time random password on the desktop and console (disable with `foxos.live_ssh=off`). Manage it with `foxos ssh status|enable|disable|keys add|list|remove|password on|off` (MCP `ssh_*`; enabling and adding keys need the human identity). Agents connect with `ssh foxos@HOST foxos …` or run MCP over SSH stdio: `ssh -T foxos@HOST foxos mcp`. VMs forward guest port 22 to a host port shown by `foxos env list`; `foxos env expose NAME --ssh on` exposes it on all addresses.
