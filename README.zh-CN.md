# FoxOS

完整说明见 [README.md](./README.md)。

## 首次运行体检

在本机确认安装是否可用（不必构建 Live ISO）：

```bash
python -m foxos status --json
python -m foxos status
```

报告包含版本、审计日志路径、人工接管命令（`foxos control status|pause|resume`）以及 MCP 入口（stdio / HTTP）。
