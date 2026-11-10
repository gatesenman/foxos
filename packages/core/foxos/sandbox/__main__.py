"""启动器：python -m foxos.sandbox exec --policy JSON [--cwd DIR] -- 命令 参数...

施加本平台的轻量隔离后执行命令（Linux：Landlock + seccomp 后 execve；macOS：sandbox-exec；Windows：受限令牌 / AppContainer + 作业对象）。
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m foxos.sandbox")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exec")
    e.add_argument("--policy", required=True)
    e.add_argument("--cwd")
    e.add_argument("command", nargs=argparse.REMAINDER)
    w = sub.add_parser("wrap", help="补全策略（私有 HOME / tmp、程序目录）后执行，供桌面端启动智能体")
    w.add_argument("--workspace", required=True)
    w.add_argument("--read", action="append", default=[])
    w.add_argument("--write", action="append", default=[])
    w.add_argument("--network", choices=["on", "off"], default="on")
    w.add_argument("--connect-port", type=int, action="append", default=[])
    w.add_argument("--home", choices=["private", "read", "write"], default="private")
    w.add_argument("--windows-mode", choices=["restricted", "appcontainer"], default="restricted")
    w.add_argument("--profile", default="default")
    w.add_argument("--env", action="append", default=[], help="KEY=VALUE")
    w.add_argument("--cwd")
    w.add_argument("command", nargs=argparse.REMAINDER)
    sub.add_parser("check")
    a = ap.parse_args(argv)
    from . import PLATFORM, Policy, capabilities
    if a.cmd == "check":
        print(json.dumps(capabilities(), ensure_ascii=False, indent=1))
        return
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd:
        ap.error("缺少要执行的命令")
    if a.cmd == "wrap":
        import os
        import re
        from . import prepare
        core = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base = Policy(workspace=os.path.abspath(a.workspace), read=[*a.read, core, *_python_dirs()], write=a.write, network=a.network == "on",
                      connect_ports=a.connect_port, home=a.home, windows_mode=a.windows_mode,
                      env=dict(kv.split("=", 1) for kv in a.env if "=" in kv))
        policy = prepare(base, cmd, re.sub(r"[^A-Za-z0-9_.-]+", "-", a.profile)[:40] or "default").to_dict()
    else:
        policy = json.loads(a.policy)
    if PLATFORM == "linux":
        from . import linux
        linux.exec_(policy, cmd, a.cwd)
    p = Policy.from_dict(policy)
    if PLATFORM == "macos":
        from . import macos
        sys.exit(macos.run(p, cmd, cwd=a.cwd, capture=False).returncode)
    if PLATFORM == "windows":
        from . import windows
        sys.exit(windows.run(p, cmd, cwd=a.cwd, capture=False).returncode)
    sys.stderr.write(f"不支持的平台 {PLATFORM}\n")
    sys.exit(6)


def _python_dirs() -> list[str]:
    """当前 Python 的安装目录（沙箱里的智能体可以再启动 foxos 命令 / stdio MCP）。"""
    import sys as _s
    return list(dict.fromkeys(d for d in (_s.prefix, _s.base_prefix, _s.exec_prefix) if d))


if __name__ == "__main__":
    main()
