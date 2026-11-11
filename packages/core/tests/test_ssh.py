"""US-64：SSH 远程访问的命令面（foxos ssh ... 与 MCP ssh_*），在宿主上不改系统 sshd 的部分。

真实的 sshd（密钥可登录、密码被拒、root 被拒、经 SSH 运行 foxos）在启动后的 ISO 上测：tests/test_os_iso_e2e.py。
"""

from __future__ import annotations

import http.server
import subprocess
import threading

import pytest

from foxos.apps.ssh import password_strength


@pytest.fixture()
def keypair(tmp_path):
    k = tmp_path / "id"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "me@laptop", "-f", str(k)], check=True)
    return k, (tmp_path / "id.pub").read_text().strip()


def test_US64_keys_add_list_remove_and_agents_cannot_add(fox, tmp_path, keypair):
    ak = tmp_path / "home" / ".ssh" / "authorized_keys"
    env = {"FOXOS_SSH_AUTHORIZED_KEYS": str(ak)}
    _, pub = keypair
    # 智能体不能给自己开门
    code, out, _ = fox.run("ssh", "keys", "add", "--key", pub, agent="some-bot", extra_env=env)
    assert code == 4 and out["error"]["code"] == "PERMISSION_DENIED" and not ak.exists()
    r = fox.run("ssh", "keys", "add", "--key", pub + "\nnot-a-key", agent="human", extra_env=env, check=0)[1]["result"]
    assert len(r["added"]) == 1 and len(r["invalid"]) == 1
    assert oct(ak.stat().st_mode & 0o777) == "0o600" and oct(ak.parent.stat().st_mode & 0o777) == "0o700"
    # 重复添加被跳过
    assert fox.run("ssh", "keys", "add", "--key", pub, agent="human", extra_env=env, check=0)[1]["result"]["skipped"]
    ls = fox.run("ssh", "keys", "list", extra_env=env, check=0)[1]["result"]
    assert ls["count"] == 1 and ls["keys"][0]["type"] == "ssh-ed25519" and ls["keys"][0]["fingerprint"].startswith("SHA256:")
    assert ls["keys"][0]["comment"] == "me@laptop"
    # 智能体可以删除（只会收紧）
    fox.run("ssh", "keys", "remove", "1", agent="some-bot", extra_env=env, check=0)
    assert fox.run("ssh", "keys", "list", extra_env=env, check=0)[1]["result"]["count"] == 0


def test_US64_import_keys_from_github_user(fox, tmp_path, keypair):
    _, pub = keypair

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):  # noqa: N802
            body = (pub.rsplit(" ", 1)[0] + "\n").encode() if self.path == "/octo.keys" else b""
            self.send_response(200 if body else 404); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        ak = tmp_path / "ak"
        env = {"FOXOS_SSH_AUTHORIZED_KEYS": str(ak), "FOXOS_GITHUB_KEYS_BASE": f"http://127.0.0.1:{srv.server_address[1]}"}
        r = fox.run("ssh", "keys", "add", "--github", "octo", agent="human", extra_env=env, check=0)[1]["result"]
        assert len(r["added"]) == 1 and "github:octo" in ak.read_text()
        code, out, _ = fox.run("ssh", "keys", "add", "--github", "bad/name", agent="human", extra_env=env)
        assert code == 2
    finally:
        srv.shutdown()


def test_US64_password_strength_and_human_only(fox):
    assert password_strength("Fox-Os-2026-strong!", "foxos") == []
    assert password_strength("short1A", "x")
    assert password_strength("alllowercaseletters", "x")          # 只有一类字符
    assert password_strength("foxosFOXOS1234", "foxos")           # 包含用户名
    code, out, _ = fox.run("ssh", "password", "on", "--new-password", "Fox-Os-2026-strong!", agent="some-bot")
    assert code == 4 and out["error"]["code"] == "PERMISSION_DENIED"
    code, out, _ = fox.run("ssh", "enable", agent="some-bot")
    assert code == 4


def test_US64_status_and_mcp_parity(fox):
    r = fox.run("ssh", "status", check=0)[1]["result"]
    for k in ("active", "port", "addresses", "password_login", "root_login", "firewall", "authorized_keys", "connect", "mcp_over_ssh"):
        assert k in r
    assert r["mcp_over_ssh"].endswith("foxos mcp")
    from foxos import catalog as cmdcat
    names = {t["name"] for t in cmdcat.mcp_tools("full", None)}
    assert {"ssh_status", "ssh_enable", "ssh_disable", "ssh_keys_add", "ssh_keys_list", "ssh_keys_remove", "ssh_password"} <= names
    # 智能体不能把虚拟机 SSH 对外开放
    code, out, _ = fox.run("env", "expose", "nope", "--ssh", "on", agent="some-bot")
    assert code in (3, 4)
