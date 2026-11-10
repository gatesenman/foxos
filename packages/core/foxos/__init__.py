"""狐狸OS（FoxOS）统一命令内核。

CLI（foxos.cli）、MCP 工具服务器（foxos.mcp_server）和桌面外壳都调用同一个
kernel.invoke()，保证「CLI 能做的，智能体工具接口也能做」，结果格式一致。
"""

__version__ = "0.0.1"
