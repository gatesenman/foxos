"""狐狸OS 的电脑操控、浏览器操控与命令行操控（computer use / browser use / command use）。

- shell.py      tmux 持久会话：退出码、超时、录制（asciicast v2）、工作空间约束、审计
- a11y.py       AT-SPI 无障碍树（Linux 桌面）：tree / find / 按元素点击、输入
- a11y_helper.py 在带 gi（PyGObject）的系统 Python 里运行的 AT-SPI 助手进程
- llm.py        OpenAI 兼容的模型调用（DeepSeek 默认），工具调用、视觉输入
- grounding.py  视觉定位：通用视觉模型 / UI-TARS / OmniParser 服务
- loop.py       智能体循环（browser task、computer task）：观察 → 模型 → 动作，接管与审批
- cdp.py        Chrome DevTools Protocol：无障碍快照、按 ref 点击 / 输入、下载
- recorder.py   终端输出录制为 asciicast v2（asciinema 可播放）
"""
