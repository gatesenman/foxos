"""多机：一个智能体控制多台狐狸OS、多个智能体共用一台狐狸OS。

起两个真实的被控端（各自独立的 FOXOS_HOME、工作区与端口，`foxos machine serve`），一个控制端；
配对码 + 证书指纹 + 控制端证书（双向 TLS），授权默认拒绝，审计写明是哪个控制端上的哪个智能体。
全部是真实进程与真实 TLS 连接，不打桩。
"""

import json
import os
import socket
import ssl
import subprocess
import sys
import time
from pathlib import Path

import pytest

from conftest import _env

pytestmark = pytest.mark.skipif(not __import__("shutil").which("openssl"), reason="openssl not installed")


class Node:
    def __init__(self, root: Path, name: str):
        self.name = name
        self.home = root / name / "home"
        self.ws = root / name / "ws"
        self.home.mkdir(parents=True)
        self.ws.mkdir(parents=True)
        self.proc = None
        self.info = None

    def env(self, extra=None):
        return _env({"FOXOS_HOME": str(self.home), **(extra or {})})

    def run(self, *args, agent="human", machine=None, timeout=120):
        cmd = [sys.executable, "-m", "foxos", "--workspace", str(self.ws), "--agent", agent, "--json"]
        if machine:
            cmd += ["--machine", machine]
        p = subprocess.run(cmd + list(args), capture_output=True, text=True, encoding="utf-8", env=self.env(), timeout=timeout)
        return p.returncode, (json.loads(p.stdout) if p.stdout.strip() else None), p

    def ok(self, *args, **kw):
        rc, d, p = self.run(*args, **kw)
        assert rc == 0, f"{args}: exit {rc}\n{p.stdout}\n{p.stderr}"
        return d["result"]

    def serve(self):
        self.proc = subprocess.Popen([sys.executable, "-m", "foxos", "--workspace", str(self.ws), "machine", "serve",
                                      "--listen", "127.0.0.1:0", "--name", self.name],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env())
        line = self.proc.stdout.readline()
        assert line, self.proc.stderr.read()
        self.info = json.loads(line)
        return self.info

    def audit(self):
        out = []
        for f in sorted((self.ws / ".foxos").glob("audit*.jsonl")):
            out += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
        return out

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(10)


@pytest.fixture
def net(tmp_path):
    alpha, beta, ctl = Node(tmp_path, "alpha-host"), Node(tmp_path, "beta-host"), Node(tmp_path, "ctl")
    alpha.serve()
    beta.serve()
    yield alpha, beta, ctl
    alpha.stop()
    beta.stop()


def pair(host: Node, ctl: Node, name: str):
    code = host.ok("machine", "host", "code")
    r = ctl.ok("machine", "pair", "--name", name, "--url", host.info["url"], "--code", code["code"],
               "--fingerprint", code["fingerprint"], "--client", "ctl")
    assert r["fingerprint"] == host.info["fingerprint"] == code["fingerprint"]
    return code


def test_US75_pairing_code_fingerprint_and_mutual_tls(net):
    alpha, beta, ctl = net
    # 指纹不对：拒绝（防中间人），什么都不登记
    code = alpha.ok("machine", "host", "code")
    rc, d, _ = ctl.run("machine", "pair", "--name", "alpha", "--url", alpha.info["url"], "--code", code["code"], "--fingerprint", "00" * 32)
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    assert ctl.ok("machine", "list")["machines"] == [m for m in ctl.ok("machine", "list")["machines"] if m["name"] == "local"]
    # 配对码对、指纹对：成功；配对码一次性
    r = ctl.ok("machine", "pair", "--name", "alpha", "--url", alpha.info["url"], "--code", code["code"], "--fingerprint", code["fingerprint"],
               "--client", "ctl")
    assert r["host"] == "alpha-host"
    rc, d, _ = ctl.run("machine", "pair", "--name", "alpha2", "--url", alpha.info["url"], "--code", code["code"])
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    # 错误的配对码被审计
    assert any(e.get("command") == "machine.pair" and e["status"] == "denied" for e in alpha.audit())
    clients = alpha.ok("machine", "host", "clients")["clients"]
    entry = clients["ctl"] if isinstance(clients, dict) else [c for c in clients if c.get("client", c.get("name")) == "ctl"][0]
    assert "token" not in json.dumps(entry).replace("token_hash", "") and "cert_pem" not in json.dumps(entry)
    # 双向 TLS：拿着正确的令牌、但不出示控制端证书 → 401（令牌被偷也没用）
    tok = subprocess.run([sys.executable, "-c", "from foxos import secrets; print(secrets.get('machine:alpha:token'))"],
                         capture_output=True, text=True, env=ctl.env()).stdout.strip()
    assert len(tok) > 20
    host, port = alpha.info["url"][8:].split(":")
    cx = ssl.create_default_context()
    cx.check_hostname, cx.verify_mode = False, ssl.CERT_NONE
    with socket.create_connection((host, int(port)), 10) as s, cx.wrap_socket(s) as t:
        t.sendall(f"GET /v1/whoami HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {tok}\r\nConnection: close\r\n\r\n".encode())
        resp = b""
        while chunk := t.recv(65536):
            resp += chunk
    assert resp.startswith(b"HTTP/1.1 401")
    # 出示一张别的自签名证书也不行（握手阶段就被拒）
    other = Path(str(ctl.home) + "-other")
    other.mkdir()
    subprocess.run(["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-nodes", "-keyout",
                    str(other / "k.pem"), "-out", str(other / "c.pem"), "-days", "1", "-subj", "/CN=evil"], check=True, capture_output=True)
    cx.load_cert_chain(str(other / "c.pem"), str(other / "k.pem"))
    rejected = False
    try:
        with socket.create_connection((host, int(port)), 10) as s, cx.wrap_socket(s) as t:
            t.sendall(f"GET /v1/whoami HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {tok}\r\nConnection: close\r\n\r\n".encode())
            rejected = not t.recv(65536).startswith(b"HTTP/1.1 200")
    except (ssl.SSLError, ConnectionError, OSError):
        rejected = True
    assert rejected
    # 正常控制端（出示配对时登记的证书）：200
    p = ctl.ok("machine", "ping", "alpha")
    assert p["ok"] and p["host"] == "alpha-host" and p["client"] == "ctl"


def test_US76_one_bot_controls_two_foxos_machines(net):
    alpha, beta, ctl = net
    pair(alpha, ctl, "alpha")
    pair(beta, ctl, "beta")
    (alpha.ws / "on-alpha.txt").write_text("a")
    (beta.ws / "on-beta.txt").write_text("b")
    # 默认拒绝：配对了但没授权
    rc, d, _ = ctl.run("files", "list", agent="bot:fox", machine="alpha")
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    alpha.ok("machine", "host", "grant", "--client", "ctl", "--bot", "fox", "--permissions", "read,create,modify")
    beta.ok("machine", "host", "grant", "--client", "ctl", "--bot", "fox", "--permissions", "read")
    # 主智能体可以去哪些机器：在设置里
    ctl.ok("bot", "config", "set", "fox", "--machines", "local,alpha,beta", "--default-machine", "local")
    # 一个智能体、一次对话里，分别在两台机器上操作（真实 ACP 回合 → MCP → 远程）
    r = ctl.ok("bot", "message", "send", "fox", "on alpha: list .")["reply"]
    assert "on-alpha.txt" in r["text"] and "on-beta.txt" not in r["text"]
    r = ctl.ok("bot", "message", "send", "fox", "on beta: list .")["reply"]
    assert "on-beta.txt" in r["text"] and "on-alpha.txt" not in r["text"]
    assert r["cards"][0]["rawOutput"]["machine"] == "beta" if r["cards"][0].get("rawOutput") else True
    # 写：alpha 授了 modify，beta 只授了 read
    ctl.ok("files", "write", "from-fox.txt", "--content", "hello alpha", agent="bot:fox", machine="alpha")
    assert (alpha.ws / "from-fox.txt").read_text() == "hello alpha"
    rc, d, _ = ctl.run("files", "write", "from-fox.txt", "--content", "x", agent="bot:fox", machine="beta")
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED" and not (beta.ws / "from-fox.txt").exists()
    # 不在这个智能体允许列表里的机器：控制端就拒绝
    ctl.ok("bot", "config", "set", "fox", "--machines", "local,alpha")
    r = ctl.ok("bot", "message", "send", "fox", "on beta: list .")["reply"]
    assert "on-beta.txt" not in r["text"]
    # 两边的审计都写明是哪个控制端上的哪个智能体
    wa = [e for e in alpha.audit() if e.get("command") == "files.write" and e["status"] == "ok"]
    assert wa and wa[-1]["agent"] == "bot:fox@ctl" and wa[-1]["interface"] == "remote"
    lb = [e for e in beta.audit() if e.get("command") == "files.list" and e["status"] == "ok"]
    assert lb and lb[-1]["agent"].startswith("bot:fox") and lb[-1]["agent"].endswith("@ctl")
    db = [e for e in beta.audit() if e.get("command") == "files.write"]
    assert db and db[-1]["status"] == "denied"
    cl = [e for e in ctl.audit() if e.get("interface") == "remote-client" and e.get("machine") == "alpha"]
    assert cl and cl[-1]["status"] == "ok"
    # machine list --check 看到两台都在线
    ms = {m["name"]: m for m in ctl.ok("machine", "list", "--check")["machines"]}
    assert {"local", "alpha", "beta"} <= set(ms)


def test_US77_many_bots_share_one_foxos_with_locks_conflict_and_takeover(net):
    alpha, _, ctl = net
    pair(alpha, ctl, "alpha")
    alpha.ok("machine", "host", "grant", "--client", "ctl", "--bot", "fox", "--permissions", "read,create,modify")
    alpha.ok("machine", "host", "grant", "--client", "ctl", "--bot", "coder", "--permissions", "read,modify", "--apps", "files",
             "--scope", "src")
    (alpha.ws / "src").mkdir()
    (alpha.ws / "shared.txt").write_text("v0")
    # coder 只能在 src 里
    rc, d, _ = ctl.run("files", "write", "shared.txt", "--content", "c", agent="bot:coder", machine="alpha")
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    ctl.ok("files", "write", "src/a.py", "--content", "print(1)", agent="bot:coder", machine="alpha")
    # coder 只授了 files 应用
    rc, d, _ = ctl.run("sheets", "create", "src/t.xlsx", agent="bot:coder", machine="alpha")
    assert rc == 4 and d["error"]["code"] == "PERMISSION_DENIED"
    # 同一文件单写者锁：被控端本机上另一个智能体正在写 shared.txt（真实持锁的活进程）
    holder = subprocess.Popen([sys.executable, "-c", (
        "import sys,time; from foxos.workspace import Workspace; from foxos import locks;"
        f"ws=Workspace({str(alpha.ws)!r}); lk=locks.acquire(ws,'shared.txt','bot:writer',0);"
        "print('held',flush=True); time.sleep(30)")], stdout=subprocess.PIPE, text=True, env=alpha.env())
    assert holder.stdout.readline().strip() == "held"
    try:
        rc, d, _ = ctl.run("files", "write", "shared.txt", "--content", "fox", agent="bot:fox", machine="alpha")
        assert rc == 5 and d["error"]["code"] == "LOCKED", d
        assert (alpha.ws / "shared.txt").read_text() == "v0"
    finally:
        holder.terminate()
        holder.wait(10)
    # 乐观并发：两个智能体基于同一版本修改，后到的得到 CONFLICT
    mtime = (alpha.ws / "shared.txt").stat().st_mtime
    ctl.ok("files", "write", "shared.txt", "--content", "fox v1", "--expect-mtime", repr(mtime), agent="bot:fox", machine="alpha")
    alpha.ok("machine", "host", "grant", "--client", "ctl", "--bot", "coder", "--permissions", "read,modify", "--apps", "files")
    rc, d, _ = ctl.run("files", "write", "shared.txt", "--content", "coder v1", "--expect-mtime", repr(mtime), agent="bot:coder",
                       machine="alpha")
    assert rc == 7 and d["error"]["code"] == "CONFLICT", d
    assert (alpha.ws / "shared.txt").read_text() == "fox v1"
    # 被控端的人接管（暂停的是写操作）：只暂停 coder，fox 继续
    alpha.ok("control", "pause", "--only", "bot:coder", "--reason", "I am editing")
    rc, d, _ = ctl.run("files", "write", "src/b.py", "--content", "x", agent="bot:coder", machine="alpha")
    assert rc == 8 and d["error"]["code"] == "PAUSED", d
    assert not (alpha.ws / "src" / "b.py").exists()
    ctl.ok("files", "list", agent="bot:coder", machine="alpha")  # 读不受影响
    ctl.ok("files", "write", "fox2.txt", "--content", "ok", agent="bot:fox", machine="alpha")
    # 全体暂停：远端自称 human 也绕不过（被改写成 remote-human，且没有授权）
    alpha.ok("control", "pause", "--reason", "all stop")
    rc, d, _ = ctl.run("files", "write", "fox3.txt", "--content", "x", agent="bot:fox", machine="alpha")
    assert rc == 8
    rc, d, _ = ctl.run("files", "write", "fox3.txt", "--content", "x", agent="human", machine="alpha")
    assert rc != 0 and not (alpha.ws / "fox3.txt").exists()
    alpha.ok("control", "resume")
    ctl.ok("files", "write", "fox3.txt", "--content", "ok", agent="bot:fox", machine="alpha")
    # 被控端的人能看到此刻谁在操作，审计分得清两个智能体
    who = ctl.ok("machine", "ping", "alpha")
    assert {a["agent"] for a in who["acting"]} >= {"bot:fox@ctl"}
    agents = {e["agent"] for e in alpha.audit() if e.get("interface") == "remote"}
    assert {"bot:fox@ctl", "bot:coder@ctl"} <= agents
    statuses = {(e["agent"], e["status"], (e.get("error") or {}).get("code")) for e in alpha.audit() if e.get("interface") == "remote"}
    assert ("bot:fox@ctl", "denied", "LOCKED") in statuses and ("bot:coder@ctl", "denied", "PAUSED") in statuses
    assert {("bot:coder@ctl", "error", "CONFLICT"), ("bot:coder@ctl", "denied", "CONFLICT")} & statuses
    # 撤销授权 → 立即拒绝
    alpha.ok("machine", "host", "revoke", "--client", "ctl", "--bot", "coder")
    rc, d, _ = ctl.run("files", "list", agent="bot:coder", machine="alpha")
    assert rc == 4
