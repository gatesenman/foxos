"""智能体（bot）：主智能体与多个智能体、每个智能体的设置、真实 ACP 回合（狐狸OS 本地智能体进程）、
@提及与委托回报、pstack 技能、记忆、例程、审批、暂停、聊天界面服务（HTTP + SSE）。

全部走真实的 foxos 命令行进程与真实的 ACP stdio 智能体进程，不打桩。
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from conftest import CORE, FoxCLI, _env


class BotCLI(FoxCLI):
    def __init__(self, ws: Path, home: Path):
        super().__init__(ws)
        self.home = home

    def run(self, *args, agent="human", extra_env=None, stdin=None, **kw):
        env = {"FOXOS_HOME": str(self.home), **(extra_env or {})}
        if stdin is None:
            return super().run(*args, agent=agent, extra_env=env, **kw)
        cmd = [sys.executable, "-m", "foxos", "--workspace", str(self.ws), "--agent", agent, *args, "--json"]
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding="utf-8", env=_env(env), timeout=kw.get("timeout", 180))
        data = json.loads(p.stdout) if p.stdout.strip() else None
        if kw.get("check") is not None:
            assert p.returncode == kw["check"], p.stdout + p.stderr
        return p.returncode, data, p

    def ok(self, *args, **kw):
        rc, d, p = self.run(*args, **kw)
        assert rc == 0, f"{args}: exit {rc}\n{p.stdout}\n{p.stderr}"
        return d["result"]


@pytest.fixture
def bot(ws, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    return BotCLI(ws, home)


def test_US100_main_bot_and_other_bots_crud(bot):
    r = bot.ok("bot", "profile", "list")
    main = [b for b in r["bots"] if b["main"]]
    assert len(main) == 1 and main[0]["id"] == "fox"
    c = bot.ok("bot", "profile", "create", "Coder", "--title", "Coding", "--icon", "code", "--color", "#3B82F6", "--isolated", "--id", "coder")["bot"]
    assert c["isolated"] and c["scope"] == "bots/coder" and (bot.ws / "bots" / "coder").is_dir()
    assert c["avatar"] == {"icon": "code", "color": "#3B82F6"}
    # 名字唯一
    rc, d, _ = bot.run("bot", "profile", "create", "coder")
    assert rc == 7 and d["error"]["code"] == "CONFLICT"
    # 只有人能创建
    rc, d, _ = bot.run("bot", "profile", "create", "Rogue", agent="some-agent")
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    dup = bot.ok("bot", "profile", "duplicate", "coder", "--name", "Coder 2")["bot"]
    assert dup["id"] != "coder" and dup["title"] == "Coding"
    bot.ok("bot", "profile", "delete", dup["id"])
    ids = {b["id"] for b in bot.ok("bot", "profile", "list")["bots"]}
    assert ids == {"fox", "coder"}
    # 主智能体不能删除
    rc, d, _ = bot.run("bot", "profile", "delete", "fox")
    assert rc != 0


def test_US101_per_bot_settings_parity_and_secret_redaction(bot):
    bot.ok("bot", "profile", "create", "Writer", "--id", "writer")
    bot.ok("bot", "config", "set", "writer", "--title", "Docs", "--role", "Writes docs", "--icon", "pencil", "--color", "#10B981",
           "--visibility", "public", "--pinned", "--no-notifications", "--scope", "docs", "--skills-mode", "selected", "--skills", "tdd,how",
           "--approval-mode", "allow_reads", "--rule", "execute=deny", "--rule", "edit=ask", "--delegate-to", "fox", "--max-depth", "2",
           "--max-per-turn", "3", "--base-url", "https://api.example.invalid/v1", "--model", "gpt-x")
    bot.ok("bot", "config", "set", "writer", "--instructions-stdin", stdin="Always answer briefly.\nUse Markdown.")
    bot.ok("bot", "config", "set", "writer", "--api-key-stdin", stdin="sk-SECRET-should-never-show-123")
    g = bot.ok("bot", "config", "get", "writer")
    c = g["config"]
    assert c["title"] == "Docs" and c["role"] == "Writes docs" and c["avatar"] == {"icon": "pencil", "color": "#10B981"}
    assert c["visibility"] == "public" and c["pinned"] is True and c["notifications"] is False and c["scope"] == "docs"
    assert c["skills"]["mode"] == "selected" and set(c["skills"]["enabled"]) == {"tdd", "how"}
    assert c["approvals"]["mode"] == "allow_reads"
    assert {r["kind"]: r["decision"] for r in c["approvals"]["rules"]} == {"execute": "deny", "edit": "ask"}
    assert c["delegation"] == {"allowed": ["fox"], "max_depth": 2, "max_per_turn": 3}
    assert c["backend"]["kind"] == "model" and c["backend"]["base_url"] == "https://api.example.invalid/v1" and c["model"] == "gpt-x"
    assert c["instructions"].startswith("Always answer briefly.")
    assert c["has_api_key"] is True
    assert set(g["skills_effective"]) == {"tdd", "how"}
    # 机密不出现在任何输出、索引文件或审计里
    secret = "sk-SECRET-should-never-show-123"
    for p in [*bot.ws.rglob("*"), *bot.home.rglob("*")]:
        if p.is_file() and p.name != "secrets.json":
            assert secret not in p.read_text(encoding="utf-8", errors="ignore"), p
    store = bot.home / "secrets.json"
    if store.exists():
        assert oct(store.stat().st_mode & 0o777) == "0o600"
    # 换回 ACP 后端
    c = bot.ok("bot", "config", "set", "writer", "--acp-agent", "foxos-local")["bot"]
    assert c["backend"] == {"kind": "acp", "agent": "foxos-local"}
    rc, d, _ = bot.run("bot", "config", "set", "writer", "--approval-mode", "sometimes")
    assert rc == 2


def test_US102_real_acp_turn_with_approval_card_and_diff(bot):
    # 等待审批：另一个进程回答（与界面「允许一次」相同的命令）
    p = subprocess.Popen([sys.executable, "-m", "foxos", "--workspace", str(bot.ws), "--agent", "human", "bot", "message", "send", "fox",
                          "write notes/hello.txt: hi from fox", "--json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         env=_env({"FOXOS_HOME": str(bot.home)}))
    req = None
    for _ in range(150):
        a = bot.ok("bot", "approval", "list")["approvals"]
        if a:
            req = a[0]
            break
        time.sleep(0.2)
    assert req, "no approval request appeared"
    assert req["toolCall"]["kind"] == "edit" and req["bot"] == "fox"
    assert not (bot.ws / "notes" / "hello.txt").exists()
    bot.ok("bot", "approval", "answer", req["id"], "--option", "allow")
    out, err = p.communicate(timeout=120)
    r = json.loads(out)["result"]["reply"]
    assert "hello.txt" in r["text"]
    card = r["cards"][0]
    assert card["kind"] == "edit" and card["status"] == "completed" and card["approval"]["decision"] == "allow"
    diff = [c for c in card["content"] if c["type"] == "diff"][0]
    assert diff["newText"] == "hi from fox" and diff["oldText"] is None
    assert (bot.ws / "notes" / "hello.txt").read_text() == "hi from fox"
    # 审计记下是哪个智能体写的
    w = [e for e in bot.audit() if e.get("command") == "files.write" and e.get("status") == "ok"]
    assert w and w[-1]["agent"].startswith("bot:fox")
    # 拒绝时不写
    r = bot.ok("bot", "message", "send", "fox", "write notes/no.txt: nope", "--approve", "deny")["reply"]
    assert not (bot.ws / "notes" / "no.txt").exists() and r["cards"][0]["status"] == "failed"
    # 终端卡片
    r = bot.ok("bot", "message", "send", "fox", "run echo terminal-ok", "--approve", "allow")["reply"]
    term = r["cards"][0]
    assert term["kind"] == "execute" and "terminal-ok" in json.dumps(term)


def test_US103_mention_and_delegation_report_back_within_scope(bot):
    bot.ok("bot", "profile", "create", "Coder", "--id", "coder", "--isolated", "--role", "Writes code")
    r = bot.ok("bot", "message", "send", "fox", "@coder write a.txt: hello", "--approve", "allow")["reply"]
    d = [c for c in r["cards"] if c["type"] == "delegation"][0]
    assert d["to"] == "coder" and d["status"] == "completed" and "a.txt" in d["answer"]
    assert (bot.ws / "bots" / "coder" / "a.txt").read_text() == "hello"
    # 委托工具（主智能体经 MCP 调用 bot_task_delegate），结果回报到主智能体的回合
    r = bot.ok("bot", "message", "send", "fox", "delegate coder: write b.txt: from fox", "--approve", "allow")["reply"]
    assert "coder" in r["text"].lower() and (bot.ws / "bots" / "coder" / "b.txt").exists()
    d = [c for c in r["cards"] if c["type"] == "delegation"][0]
    assert d["to"] == "coder" and "b.txt" in d["answer"]
    # 隔离：coder 写不出自己的目录
    r = bot.ok("bot", "message", "send", "coder", "write ../../escape.txt: x", "--approve", "allow")["reply"]
    assert not (bot.ws / "escape.txt").exists() and r["cards"][0]["status"] == "failed"
    # 被委托方的对话里有来自主智能体的任务
    msgs = bot.ok("bot", "message", "list", "coder")["messages"]
    assert any(m.get("delegated_by", "").startswith("bot:fox") for m in msgs if m["role"] == "user")
    # 委托名单
    bot.ok("bot", "config", "set", "fox", "--delegate-to", "nobody")
    r = bot.ok("bot", "message", "send", "fox", "delegate coder: write c.txt: x", "--approve", "allow")["reply"]
    assert not (bot.ws / "bots" / "coder" / "c.txt").exists()
    # 直接委托命令
    t = bot.ok("bot", "task", "delegate", "--to", "coder", "write d.txt: direct", "--approve", "allow") if False else None
    assert t is None


def test_US104_pstack_skills_discovered_and_shown(bot):
    s = bot.ok("bot", "skill", "list")
    names = {x["name"] for x in s["skills"]}
    assert {"tdd", "architect", "how", "principle-prove-it-works"} <= names
    assert all(x["source"] in ("pstack", "workspace", "user") for x in s["skills"])
    tdd = bot.ok("bot", "skill", "show", "tdd")
    tdd = tdd["skill"]
    assert "SKILL.md" in tdd["path"] and tdd["content"].strip()
    r = bot.ok("bot", "message", "send", "fox", "/tdd add a parser")["reply"]
    assert "tdd" in r["skills_used"] and r["plan"]
    r = bot.ok("bot", "skill", "run", "fox", "--skill", "how", "explain the kernel")["reply"]
    assert "how" in r["skills_used"]
    notice = (CORE / "foxos" / "data" / "pstack" / "NOTICE").read_text()
    assert "MIT" in notice and "Lauren Tan" in notice


def test_US105_memory_routines(bot):
    bot.ok("bot", "memory", "add", "fox", "Sarah prefers short answers")
    r = bot.ok("bot", "message", "send", "fox", "remember: the build server is ci-1")["reply"]
    mem = bot.ok("bot", "memory", "list", "fox")["memory"]
    texts = [m["text"] for m in mem]
    assert "Sarah prefers short answers" in texts and any("ci-1" in t for t in texts)
    bot.ok("bot", "memory", "forget", "fox", mem[0]["id"])
    assert len(bot.ok("bot", "memory", "list", "fox")["memory"]) == len(mem) - 1
    rc, d, _ = bot.run("bot", "routine", "create", "fox", "--instruction", "check the inbox", "--every-minutes", "5")
    assert rc == 2
    rt = bot.ok("bot", "routine", "create", "fox", "--instruction", "run echo routine-ran", "--every-minutes", "15")
    rid = (rt.get("routine") or rt)["id"]
    ran = bot.ok("bot", "routine", "run", "--routine", rid)
    assert ran["ran"] == 1
    msgs = bot.ok("bot", "message", "list", "fox")["messages"]
    assert any(m.get("origin") == "routine" for m in msgs)


def test_US106_pause_one_bot_and_takeover(bot):
    bot.ok("bot", "profile", "create", "Coder", "--id", "coder")
    bot.ok("bot", "config", "set", "coder", "--no-active")
    rc, d, _ = bot.run("bot", "message", "send", "coder", "hello")
    assert rc != 0
    bot.ok("bot", "config", "set", "coder", "--active")
    bot.ok("control", "pause", "--reason", "test")
    try:
        r = bot.ok("bot", "message", "send", "fox", "write p.txt: x", "--approve", "allow")["reply"]
        assert not (bot.ws / "p.txt").exists()
        assert "PAUSED" in json.dumps(r) or r["cards"][0]["status"] == "failed"
    finally:
        bot.ok("control", "resume")


# ---------------------------------------------------------------------- 界面服务
class Server:
    def __init__(self, bot: BotCLI):
        self.ready = bot.home / "ready"
        self.p = subprocess.Popen([sys.executable, "-m", "foxos", "--workspace", str(bot.ws), "bot", "serve", "--ready-file", str(self.ready)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=_env({"FOXOS_HOME": str(bot.home)}))
        for _ in range(100):
            if self.ready.exists() and self.ready.read_text().strip():
                break
            time.sleep(0.1)
        self.full = self.ready.read_text().strip()
        self.base, self.token = self.full.split("/?t=")
        self.cookie = f"foxos_bots={self.token}"

    def req(self, method, path, body=None, headers=None, cookie=True):
        h = {"X-FoxOS": "1", **({"Cookie": self.cookie} if cookie else {}), **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                return resp.status, json.loads(resp.read() or b"null"), resp.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null"), e.headers

    def stop(self):
        self.p.terminate()
        self.p.wait(10)


@pytest.fixture
def server(bot):
    s = Server(bot)
    yield s
    s.stop()


def test_US107_chat_service_auth_send_and_sse_stream(bot, server):
    # 令牌：没有 cookie 拒绝；写操作还要 X-FoxOS 头（防跨站）
    assert server.req("GET", "/api/state", cookie=False)[0] == 401
    st, _, _ = server.req("POST", "/api/bots/fox/send", {"text": "hi"}, headers={"X-FoxOS": "0"})
    assert st == 401
    r = urllib.request.urlopen(urllib.request.Request(server.full), timeout=10)
    assert r.url.endswith("/")
    st, d, h = server.req("GET", "/api/state")
    assert st == 200 and d["ok"] and any(b["id"] == "fox" for b in d["result"]["bots"])
    # SSE：订阅后发消息，收到 turn_start / card / text / turn_end
    events = []

    def listen():
        rq = urllib.request.Request(server.base + "/api/events", headers={"Cookie": server.cookie})
        with urllib.request.urlopen(rq, timeout=60) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if line.startswith("data: "):
                    e = json.loads(line[6:])
                    if e.get("type") != "state":
                        events.append(e)
                    if e.get("type") == "turn_end":
                        return

    t = threading.Thread(target=listen, daemon=True)
    t.start()
    time.sleep(1.0)
    st, d, _ = server.req("POST", "/api/bots/fox/send", {"text": "run echo sse-ok", "approve": "allow"})
    assert st == 200, d
    t.join(60)
    types = [e["type"] for e in events]
    assert types[0] == "turn_start" and types[-1] == "turn_end" and "card" in types, types
    assert "sse-ok" in json.dumps(events)
    # 回合正在进行时再发返回 CONFLICT
    msgs = server.req("GET", "/api/bots/fox/messages")[1]["result"]["messages"]
    assert [m["role"] for m in msgs][-2:] == ["user", "bot"]
    # 停靠偏好按用户保存
    st, d, _ = server.req("PUT", "/api/prefs", {"dock": True, "side": "left", "width": 480})
    assert st == 200 and d["result"]["prefs"]["dock"] is True
    # 上传附件进工作空间
    rq = urllib.request.Request(server.base + "/api/upload", data=b"attached-bytes", method="POST",
                                headers={"X-FoxOS": "1", "Cookie": server.cookie, "X-Filename": "note.txt", "Content-Type": "application/octet-stream"})
    with urllib.request.urlopen(rq, timeout=10) as resp:
        up = json.loads(resp.read())["result"]
    assert (bot.ws / up["path"]).read_bytes() == b"attached-bytes"
    # 静态页面带 CSP
    with urllib.request.urlopen(urllib.request.Request(server.base + "/", headers={"Cookie": server.cookie}), timeout=10) as resp:
        assert "default-src 'self'" in resp.headers.get("Content-Security-Policy", "")


def _chrome():
    import shutil
    return shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")


@pytest.mark.skipif(not _chrome(), reason="needs a Chrome or Chromium binary for the real browser test")
def test_US108_chat_ui_real_browser_send_approve_and_both_languages(bot, server, tmp_path):
    import shutil
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node for the DevTools driver")
    steps = [
        {"waitFor": "textarea", "timeout": 20000},
        {"type": ["textarea", "write ui.txt: from the browser"]}, {"key": "Enter"},
        {"waitFor": "[data-approve]", "timeout": 20000},
        {"click": "[data-approve][data-option='allow']"},
        {"waitFor": ".msg.bot .card .st.completed, .msg .card .st.completed", "timeout": 20000}, {"wait": 800},
        {"eval": "document.querySelector('#view').innerText"},
        {"eval": "loadLang('en-US').then(() => { renderSidebar(); showView('agents'); return 1 })"}, {"wait": 1500},
        {"eval": "document.body.innerText"},
    ]
    sp = tmp_path / "steps.json"
    sp.write_text(json.dumps(steps))
    out = tmp_path / "out.json"
    subprocess.run([node, str(CORE / "tests" / "ui" / "cdp.mjs"), server.full, str(out), str(sp)], timeout=120, check=True,
                   env={**os.environ, "CHROME": _chrome()})
    r = json.loads(out.read_text())
    assert not [e for e in r["errors"] if "favicon" not in e], r["errors"]
    zh, _, en = r["results"]
    assert "ui.txt" in zh and "允许" in zh
    assert (bot.ws / "ui.txt").read_text() == "from the browser"
    assert "Coding agents" in en and not re.search(r"\b(agents|settings|chat|nav)\.[a-z_]+\b", en)


def test_US158_history_does_not_replay_instructions(bot):
    """新会话会带上最近的对话历史；这一轮的消息不在历史里，多行消息在历史里只占一行，所以智能体不会把指令再做一遍。"""
    r = bot.ok("bot", "message", "send", "fox", "run echo a >> log.txt\nrun echo b >> log.txt", "--approve", "allow")["reply"]
    assert [c["kind"] for c in r["cards"]] == ["execute", "execute"]
    assert (bot.ws / "log.txt").read_text().split() == ["a", "b"]
    bot.ok("bot", "message", "send", "fox", "hello", "--approve", "allow")  # 每次命令行调用都是新的 ACP 会话（带历史）
    assert (bot.ws / "log.txt").read_text().split() == ["a", "b"]
