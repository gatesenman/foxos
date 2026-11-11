"""连接器（OpenBot 的 Apps / MCP 连接器）：目录、自定义 MCP（stdio 与 HTTP）、令牌与 OAuth（PKCE、动态注册、刷新）、
每个智能体单独授权、写工具按审批规则询问、令牌不外泄。

OAuth 用一个真实的本机对端服务器（tests/peers/oauth_mcp.py）跑完整流程；托管的第三方 OAuth（Notion、Google Drive）
需要第三方账号，没有在这里真实授权。
"""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from conftest import _env
from test_bots import BotCLI

PEER = Path(__file__).resolve().parent / "peers" / "oauth_mcp.py"


@pytest.fixture
def bot(ws, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    return BotCLI(ws, home)


@pytest.fixture
def peer(tmp_path):
    rf = tmp_path / "peer.url"
    p = subprocess.Popen([sys.executable, str(PEER), str(rf)])
    for _ in range(100):
        if rf.exists() and rf.read_text():
            break
        time.sleep(0.05)
    yield rf.read_text()
    p.kill()


def test_US71_catalog_and_stdio_mcp_connector_with_per_bot_grant(bot, tmp_path):
    cat = bot.ok("connector", "catalog")["catalog"]
    keys = {c["key"] for c in cat}
    assert {"exa", "parallel", "firecrawl", "notion", "google-drive", "github"} <= keys
    assert {c["auth"]["kind"] for c in cat} == {"none", "bearer", "oauth"}
    # 另一个工作空间的 foxos MCP 服务器当作真实的 stdio 连接器
    other = tmp_path / "other"
    other.mkdir()
    (other / "remote.txt").write_text("hello from the other side")
    bot.ok("connector", "add", "--id", "otherws", "--title", "Other workspace",
           *[f"--arg={a}" for a in (sys.executable, "-m", "foxos", "--workspace", str(other), "mcp")])
    t = bot.ok("connector", "tools", "otherws", "--refresh")
    names = {x["name"]: x for x in t["tools"]}
    assert "files_list" in names and names["files_list"]["write"] is False and t["server"]["name"] == "foxos"
    r = bot.ok("connector", "tool", "call", "otherws", "--tool", "files_list", "--arguments", '{"path": "."}')
    assert "remote.txt" in r["text"]
    # 智能体没被授权时拒绝
    r = bot.ok("bot", "message", "send", "fox", 'use otherws files_list {"path": "."}')["reply"]
    assert r["cards"][0]["status"] == "failed" and "remote.txt" not in r["text"]
    bot.ok("bot", "config", "set", "fox", "--connectors", "otherws")
    r = bot.ok("bot", "message", "send", "fox", 'use otherws files_list {"path": "."}')["reply"]
    assert r["cards"][0]["status"] == "completed" and "remote.txt" in r["text"]
    # 未知连接器不能授权
    rc, d, _ = bot.run("bot", "config", "set", "fox", "--connectors", "nope")
    assert rc == 3
    bot.ok("connector", "remove", "otherws")
    assert bot.ok("connector", "list")["count"] == 0


def test_US72_oauth_pkce_dynamic_registration_refresh_and_write_approval(bot, peer):
    bot.ok("connector", "add", "--id", "notes", "--title", "Notes", "--url", peer + "/mcp", "--auth", "oauth")
    c = [x for x in bot.ok("connector", "list")["connectors"] if x["id"] == "notes"][0]
    assert c["auth"]["authorization_url"] == peer + "/authorize" and c["auth"]["registration_url"] == peer + "/register"
    p = subprocess.Popen([sys.executable, "-m", "foxos", "--workspace", str(bot.ws), "--agent", "human", "connector", "connect", "notes",
                          "--no-browser", "--json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         env=_env({"FOXOS_HOME": str(bot.home)}))
    line = p.stderr.readline()
    url = json.loads(line)["authorize_url"]
    assert "code_challenge_method=S256" in url and "state=" in url
    # 浏览器里点「允许」：授权页 302 到 127.0.0.1 的回调
    urllib.request.urlopen(url, timeout=20).read()
    out, err = p.communicate(timeout=60)
    r = json.loads(out)["result"]
    assert r["connected"] and {t["name"] for t in r["tools"]} == {"echo", "save_note"}
    tools = {t["name"]: t for t in r["tools"]}
    assert tools["save_note"]["write"] is True and tools["echo"]["write"] is False
    # 令牌只在本地密钥库
    blob = "".join(f.read_text(errors="ignore") for f in bot.home.rglob("*") if f.is_file() and f.name != "secrets.json")
    log = json.loads(urllib.request.urlopen(peer + "/log").read())
    assert log["log"][:3] == ["register", "authorize", "token"]
    assert "at-" not in blob and "rt-" not in blob
    # 第一枚令牌 1 秒过期：下一次调用前自动刷新
    time.sleep(1.5)
    r = bot.ok("connector", "tool", "call", "notes", "--tool", "echo", "--arguments", '{"text": "hi"}')
    assert r["text"] == "echo:hi"
    assert "refresh" in json.loads(urllib.request.urlopen(peer + "/log").read())["log"]
    # 写工具：按智能体的审批规则（拒绝 → 不写；允许 → 写）
    bot.ok("bot", "config", "set", "fox", "--connectors", "notes")
    r = bot.ok("bot", "message", "send", "fox", 'use notes save_note {"text": "denied"}', "--approve", "deny")["reply"]
    assert r["cards"][0]["status"] == "failed"
    r = bot.ok("bot", "message", "send", "fox", 'use notes save_note {"text": "kept"}', "--approve", "allow")["reply"]
    assert r["cards"][0]["status"] == "completed"
    assert json.loads(urllib.request.urlopen(peer + "/log").read())["notes"] == ["kept"]
    # 审计记下智能体身份与连接器工具
    calls = [e for e in bot.audit() if e.get("command") == "connector.tool.call"]
    assert any(e["agent"].startswith("bot:fox") for e in calls)
    bot.ok("connector", "disconnect", "notes")
    rc, d, _ = bot.run("connector", "tool", "call", "notes", "--tool", "echo", "--arguments", "{}")
    assert rc == 4


def test_US73_bearer_token_connector_secret_never_logged(bot, peer):
    # 同一个对端用 bearer 方式：令牌由 stdin 传入，存本地密钥库，输出与审计里看不到
    bot.ok("connector", "add", "--id", "notes-key", "--url", peer + "/mcp", "--auth", "bearer")
    rc, d, p = bot.run("connector", "connect", "notes-key", "--token-stdin", stdin="wrong-token-value")
    assert rc == 0 and d["result"].get("connected") is False  # 对端拒绝错误令牌
    assert "wrong-token-value" not in p.stdout + p.stderr
    blob = "".join(f.read_text(errors="ignore") for f in [*bot.home.rglob("*"), *bot.ws.rglob("*")] if f.is_file() and f.name != "secrets.json")
    assert "wrong-token-value" not in blob


def _online(url):
    try:
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=5)
        return True
    except Exception as e:  # noqa: BLE001
        return hasattr(e, "code")


@pytest.mark.skipif(not _online("https://mcp.exa.ai/mcp"), reason="mcp.exa.ai not reachable from this machine")
def test_US74_hosted_keyless_connector_live(bot):
    bot.ok("connector", "add", "--key", "exa")
    t = bot.ok("connector", "tools", "exa", "--refresh")
    names = [x["name"] for x in t["tools"]]
    assert names, t
    tool = next((n for n in names if "search" in n), names[0])
    r = bot.ok("connector", "tool", "call", "exa", "--tool", tool, "--arguments", json.dumps({"query": "Agent Client Protocol", "numResults": 1}),
               timeout=120)
    assert r["text"].strip() and not r["isError"]
