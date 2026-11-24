# 2026-11-24 验证记录

时间使用 Asia/Shanghai。代码基于远端主线 `c975bbd`，本地分支为 `gaosichun/real-system`。

## 已修复

源码提交 `35912fc`：

- 正文的 `value` 和 `text` 不再调用 `strip()`。首尾空格与换行属于文件内容。
- 按照实际 `agent-desktop@1.2.0` 的命令帮助修正参数。`get`、`is`、`wait`、`press` 不接受 `--timeout-ms`。
- 删除跨快照猜测元素引用和自动重放操作的代码。重复编号或相同名称不能证明是同一个控件。
- 按键失败不再自动切换到 `--headed` 物理输入，也不自动抢焦点重试。
- 标题匹配到多个窗口时拒绝选第一个。常规快照不再为解析标题额外运行一次窗口列表命令。
- 快照状态文件不再额外保存正文副本。

测试器提交 `42e2dfb`：

- ISO 测试默认使用 TCG，不再通过 `/dev/kvm` 是否可读自动选择硬件加速。
- 增加 `cu_semantic`。该用例只调用来宾 `/usr/lib/foxos/python` 中的代码，不读取模型密钥。
- `cu_semantic` 与完整规划器用例分开记录，不能相互替代。

## 实际结果

本轮的桌面环境是构建机 Debian 13 上隔离的 Xvfb、xfwm4、Mousepad 和 AT-SPI，不是新 FoxOS ISO。编辑器测试进程使用 C.UTF-8 菜单文案，不验证系统默认语言。

| 项目 | 状态 | 证据和边界 |
|---|---|---|
| 桌面、安全路由、ACP 重试、ISO 测试器回归 | PASS | 53 项通过。包含默认拒绝宿主读写、只在来宾进程写入文件、打开宿主执行后仍需逐项批准。 |
| 隔离模型凭证的广泛回归 | FAIL，复测已修复环境问题 | 179 项通过、27 项跳过、2 项失败。US-32、US-33 均因构建机缺少已声明的 `zstandard` 依赖失败。安装 `python3-zstandard` 后，这两项真实快照恢复与克隆导出导入复测通过。没有重新跑整套，不能记作整套零失败。 |
| 实际 Mousepad 替换正文并保存 | PASS | 使用无障碍语义动作修改并点击菜单保存，磁盘内容为 `Shopping list: apples, milk`。不是通过文件 API 写入结果。 |
| 实际 Mousepad 新增清单行并保存 | PASS | 磁盘内容精确为 `milk\neggs`。同时验证实际文本读取与按窗口标题定位。 |
| opencode 官方下载、哈希校验与 ACP 握手 | PASS | 独立的真实进程测试通过，包含会话建立。不发送模型提示。不能与旧 TCG 的 358 秒首轮对话作速度比较。 |
| DeepSeek 凭证检查 | BLOCKED | 官方接口返回 HTTP 401。当前进程没有 `DEEPSEEK_API_KEY` 环境变量。 |
| Jev 凭证检查 | PASS | 模型列表接口返回 HTTP 200。没有据此声称完整编辑任务通过。 |
| 完整模型用例初次尝试 | FAIL | 广泛测试自动读到了原有无效凭证，US-140、US-141、US-142 失败。该轮在 15 项通过、3 项失败后中断。随后单独运行无凭证测试，不覆盖这次失败。 |
| US-121、US-122 完整规划器 | BLOCKED | DeepSeek 认证失败。没有用预设步骤冒充规划器通过。 |
| 358 秒首轮对话优化 | NOT TESTED | 尚无新最终镜像上的首轮对话测量，不能声称已加速。 |
| 新最终 ISO 开机、SSH、MCP、运行时、远程通道、Chrome、安装与重启 | NOT TESTED | 本轮没有构建新 ISO。新 `cu_semantic` 也尚未在最终 ISO 上运行。 |
| 真实 Windows、Mac、WSL2 | NOT TESTED | 未操作任何用户电脑。 |
| 推送本次分支 | BLOCKED | 保存的项目令牌被 GitHub 拒绝，返回 `Invalid username or token`。没有切换账号或连接方式重试。 |
| 新预发布、容器发布 | NOT TESTED | 没有发布新文件，没有删除或替换旧版本。容器发布仍暂停。 |

## 证据

构建机持久目录为 `/workspace/foxos-evidence/2026-11-24/`：

- `final-targeted.log`：53 项针对性回归。
- `gui.log`：两个实际桌面编辑用例及磁盘内容。
- `files/replace.txt`、`files/append.txt`：通过菜单保存的实际文件。
- `acp-real.log`：真实第三方 ACP 安装及握手。
- `core-all.log`：因无效模型凭证而中断的初次广泛测试，保留失败记录。
- `core-no-key.log`：显式隔离模型凭证后的广泛回归记录。
- `iso-tools.log`：恢复本地镜像构建和 TCG 测试工具的安装记录。
- `archive-retest.log`：两项实际环境归档用例在恢复依赖后通过。
- `file-sha256.json`：实际保存文件的 SHA-256。

运行针对性回归的命令为 `PYTHONPATH=packages/core python3 -m pytest -q packages/core/tests/test_computer_use.py packages/core/tests/test_hostguard.py packages/core/tests/test_desktop_client.py packages/core/tests/test_acp_session_retry.py packages/core/tests/test_iso_harness.py`。

实际编辑用例为 `packages/core/tests/test_cu_gui.py`。必须在专用测试显示器上显式设置 `FOXOS_CU_GUI=1`，不会在普通测试时自动打开编辑器。

## 本地构建条件

剩余磁盘约 120 GiB，没有删除旧资料。镜像构建及 TCG 测试工具已安装，并在 root 的 PATH 中确认可用。安装工具不等于已经构建或验收镜像。本轮没有启动 KVM。

## 发布前仍需完成

1. 保留本地提交，取得可用的项目推送凭证后正常推送。主线只允许快进。
2. 从干净、已验证的提交构建下一版 ISO，保留源码提交号与镜像 SHA-256。
3. 仅引导该最终 ISO。先运行所有不依赖模型凭证的开机、安全、运行时、安装与重启用例，以及 `python3 scripts/os/e2e/iso_e2e.py run cu_semantic`。
4. 有可用模型凭证后运行完整规划器编辑、首轮对话和相关回归。记录失败，不以免密钥用例替代。
5. 使用最终系统重新拍摄干净截图，更新 README、用户故事和测试报告。
6. 核对分卷与哈希后发布新的 GitHub 预发布，逐项列出失败与未测试项目。旧版本保留。
