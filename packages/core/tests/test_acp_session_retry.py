"""ACP session/new：智能体还在启动（opencode 插件没激活完）时报 -32603，客户端稍等重试；别的错误不重试。

用真实子进程说 ACP（stdio 逐行 JSON-RPC），不替换客户端代码。0.3.3 ISO 端到端里 TCG 虚拟机上首个回合遇到过。
"""
import sys
import textwrap

import pytest

from foxos.acp_client import AcpConnection, AcpError

AGENT = textwrap.dedent('''
    import json, sys
    fails, msg = int(sys.argv[1]), sys.argv[2]
    n = 0
    for line in sys.stdin:
        m = json.loads(line)
        if "id" not in m or "method" not in m:
            continue
        if m["method"] == "initialize":
            r = {"result": {"protocolVersion": 1, "agentCapabilities": {}}}
        elif m["method"] == "session/new":
            n += 1
            r = {"error": {"code": -32603, "message": msg}} if n <= fails else {"result": {"sessionId": f"s-after-{n}"}}
        else:
            r = {"error": {"code": -32601, "message": "nope"}}
        print(json.dumps({"jsonrpc": "2.0", "id": m["id"], **r}), flush=True)
''')


def _conn(tmp_path, fails, msg):
    script = tmp_path / "agent.py"
    script.write_text(AGENT)
    c = AcpConnection(sys.executable, [str(script), str(fails), msg], identity="test", workspace=tmp_path)
    c.start()
    c.initialize(30)
    return c


def test_session_new_retries_while_agent_is_starting(tmp_path):
    c = _conn(tmp_path, 2, "Internal error: Internal service failure")
    try:
        assert c.new_session([], timeout=60)["sessionId"] == "s-after-3"
    finally:
        c.stop()


def test_session_new_does_not_retry_other_errors(tmp_path):
    c = _conn(tmp_path, 1, "Invalid model")
    try:
        with pytest.raises(AcpError, match="Invalid model"):
            c.new_session([], timeout=60)
    finally:
        c.stop()
