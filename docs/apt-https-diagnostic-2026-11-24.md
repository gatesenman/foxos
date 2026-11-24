# 2026-11-24 APT HTTPS 实际诊断

时间均为 Asia/Shanghai。本轮没有修改 OS 源码、软件源、证书或包签名规则，没有生成新 ISO，没有重跑 Chrome 安装。原配置 Chrome 的 FAIL 保留。

## 实际测试对象

- 候选源码 `86c7c2e3977e11060ea7816cc5a59130acd0716e`。
- 文件 `/opt/foxos-artifacts/candidate-86c7c2e/FoxOS-0.3.4-candidate-86c7c2e-amd64.iso`。
- 大小 2250704896 字节。启动前和诊断后均核对 SHA-256 `8f7658ba6019b40b2b39ecd9d2e096b323512abd491e92a18f3cce3724530bee`。
- 使用控制器 `09b6dde39a5c2dcda23c6a3d88c776826a6decc5`，TCG、4 CPU、4096 MiB。16:27:32 启动全新 Live 来宾，16:30:10 完成正常关机。
- 这是未发布候选，不是已发布的 0.3.4。未覆盖旧候选或原安装盘。

## 同一公共文件的结果

所有获取请求都指向 `https://archive.ubuntu.com/ubuntu/dists/noble/InRelease`。没有改成 HTTP，没有禁用 TLS 校验。

| 检查 | 结果 | 实际证据 |
|---|---|---|
| 来宾默认 curl GET | PASS | HTTP 200，证书验证结果 0，255850 字节。对端 172.66.152.176。 |
| 来宾强制 HTTP1.1 curl GET | PASS | HTTP 200，证书验证结果 0，同样字节数和 SHA。对端 104.20.28.246。 |
| 来宾 Ubuntu 签名验证 | PASS | gpgv 使用镜像内 ubuntu-archive-keyring，报告 Ubuntu Archive Automatic Signing Key (2018) 的 Good signature。 |
| 来宾默认 APT 获取 | FAIL | exit 100。TLS non-properly terminated，报告 IP 198.18.0.1。 |
| 来宾隔离配置 APT 获取 | FAIL | 清除代理环境变量，禁用现有 APT 配置目录和主文件后仍 exit 100，同一 IP、同一 TLS 错误。禁用目录用 `-`，产生不存在目录的警告，原日志保留。 |
| 原生构建机 APT 获取 | FAIL | 非 FoxOS 系统的 apt 3.0.4 同样 exit 100，TLS unexpected EOF，报告 IP 198.18.0.1。 |
| 原生构建机 curl GET | PASS | 默认调用和显式禁用 curlrc、代理的 HTTP1.1 调用均为 HTTP 200、证书验证结果 0。 |
| 来宾正常关机 | PASS | 实际确认 Casper 提示后退出，25.68 秒。没有强制停止，没有 squashfs 错误。 |

四份成功 GET 的 SHA-256 都是 `cdb2f31d809f589719a53c6ad15f255b27569c4059542ada282aaa21b8e164b0`。签名脚本保留的是 gpgv 状态，不是随后 cmp 的状态。这里依据独立记录的相同 SHA 判断文件一致，不把该脚本的零退出码当作 cmp 的独立断言。

来宾 apt 为 2.8.4，HTTPS 方法链接 GnuTLS。来宾 curl 为 8.5.0，链接 OpenSSL。原生构建机 curl 为 8.14.1。两处记录的代理环境变量均不存在，APT 配置没有显式 Proxy 指令。来宾有 120 个 CA PEM 文件，没有显式关闭 Verify-Peer 或 Verify-Host。两处 getent 都返回公共 Cloudflare IPv4，APT 错误中的 198.18.0.1 与这些地址不同。

## 能得出的结论

失败不只发生在 FoxOS，也不依赖 FoxOS 现有 APT 配置。当前环境对 APT 获取公共 HTTPS 文件存在可复现的传输阻塞。curl 的 HTTP1.1 同样成功，因此仅以 HTTP2 差异解释失败不足。

这些证据没有定位 198.18.0.1 的具体网络或代理机制，也没有证明某一 TLS 库本身有缺陷。不能据此修改生产源、关闭校验、替换下载器或添加未经验证的重试策略。本轮没有足够证据支持安全的产品补丁，停止这条诊断分支，保留环境阻塞。

GET 和 Ubuntu 签名通过不等于 APT 索引更新、依赖安装或 Chrome 原配置通过。先前 Live 手动 HTTP 干预后的条件通过没有升级为原配置通过。安装后的 Chrome、完整模型规划器和真实 Windows 仍未验证。没有启动性能提升结论。

## 证据与恢复位置

精简原始日志、确切来宾命令、执行脚本和摘要见 [APT HTTPS 证据](evidence/apt-https-2026-11-24)。`SHA256SUMS` 覆盖该目录的证据文件。没有复制 SSH 私钥或原始串口。

完整本机目录为 `/opt/foxos-artifacts/controller-validation-09b6dde/apt-diagnostic/`。本轮 Shell PID637505 和 QEMU PID637553 均已退出，没有遗留诊断来宾。

原全套免凭证回归 PID624566 已实际完成，为197通过、27跳过、零失败。原日志 `core-no-key.log` 保留，没有重复运行或替换旧批次计数。该计数包含16项控制器回归，不能重复相加。见[控制器复测报告](controller-validation-2026-11-24.md)。

没有 PAT 或 DeepSeek 认证重试，没有推送、发布、KVM、Docker 或用户电脑操作。
