"""真实的第三方 ACP 智能体：用 `foxos runtime install` 从官方发布地址下载（校验 sha256），
注册成 ACP 智能体，再用 stdio 走真实的 initialize + session/new 握手。

没有模型账号，所以只验证到握手与会话建立（不发提示）。没有网络时跳过。
下载缓存在 /var/tmp/foxos-test-cache，重复运行不再下载。
"""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import _env

CACHE = Path(os.environ.get("FOXOS_TEST_CACHE", "/var/tmp/foxos-test-cache"))


def _online() -> bool:
    try:
        socket.create_connection(("github.com", 443), 5).close()
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not _online(), reason="no network to github.com")


@pytest.fixture
def rt(tmp_path):
    env = {"FOXOS_HOME": str(tmp_path / "home"), "FOXOS_RUNTIME_PREFIX": str(CACHE / "runtime"),
           "FOXOS_RUNTIME_BIN": str(tmp_path / "bin")}

    def run(*args, timeout=600):
        p = subprocess.run([sys.executable, "-m", "foxos", "--workspace", str(tmp_path), "--agent", "human", "--json", *args],
                           capture_output=True, text=True, env=_env(env), timeout=timeout)
        return p.returncode, (json.loads(p.stdout) if p.stdout.strip() else None), p
    return run


def test_US116_install_opencode_verified_and_real_acp_handshake(rt):
    rc, d, p = rt("runtime", "install", "opencode")
    assert rc == 0, p.stdout + p.stderr
    res = d["result"]["results"][0]
    assert res["ok"] and "2.2.7" in res["found"] and res["acp"]
    rc, d, p = rt("acp", "agent", "list")
    ids = {a["id"]: a for a in d["result"]["agents"]}
    assert "opencode" in ids and ids["opencode"]["method"] == "runtime:binary"
    rc, d, p = rt("acp", "agent", "probe", "opencode", timeout=180)
    assert rc == 0, p.stdout + p.stderr
    r = d["result"]
    assert r["protocolVersion"] == 1 and "opencode" in json.dumps(r.get("agentInfo") or r).lower()
    assert r["session"]["ok"] and r["session"]["sessionId"]
    # 每个智能体的设置：模型/模式/参数/环境变量（含密钥的变量名被拒绝，密钥走 secrets）
    rc, d, _ = rt("acp", "agent", "config", "opencode", "--model", "opencode/big-pickle", "--env", "OPENCODE_LOG=info")
    assert rc == 0 and d["result"]["config"]["model"] == "opencode/big-pickle"
    rc, d, _ = rt("acp", "agent", "config", "opencode", "--env", "OPENAI_API_KEY=sk-x")
    assert rc == 2 and "sk-x" not in json.dumps(d)
    # 更新检查走在线注册表（只检查，不装）
    rc, d, p = rt("acp", "agent", "update", "opencode", "--check", timeout=120)
    assert rc in (0, 6), p.stdout + p.stderr
