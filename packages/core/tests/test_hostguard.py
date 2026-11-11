"""US-134：宿主应用里的智能体只在狐狸OS 虚拟电脑里动手。

FOXOS_PLACE=host 模拟宿主（Windows 伴侣程序等）；被控的“虚拟电脑”是另一个 machine serve，FOXOS_PLACE=foxos。
- 默认：智能体对本机的任何调用（读也算）被拒绝，提示改用虚拟电脑；人照常可用。
- 智能体经 --machine 路由到配对的虚拟电脑：照常执行，对方审计写明控制端。
- 打开宿主执行只有人能做；打开后只读放行，每个非只读操作都要人逐个确认（审批卡片），没有确认就拒绝。
- 代码智能体（ACP 进程会在本机自己动手）在宿主上默认不能运行。
"""

import json
import subprocess
import sys
import time

from conftest import _env
from test_machines import Node, pair

HOST = {"FOXOS_PLACE": "host"}


class Host(Node):
    def env(self, extra=None):
        return _env({"FOXOS_HOME": str(self.home), **HOST, **(extra or {})})


def test_US134_place_detection(tmp_path, monkeypatch):
    from foxos import hostguard
    rel = tmp_path / "os-release"
    rel.write_text('NAME="狐狸OS"\nID=foxos\nID_LIKE="ubuntu debian"\n')
    monkeypatch.delenv("FOXOS_PLACE", raising=False)
    monkeypatch.setattr(hostguard, "OS_RELEASE", rel)
    assert hostguard.place() == "foxos"
    rel.write_text("NAME=Ubuntu\nID=ubuntu\n")
    assert hostguard.place() == "host"
    monkeypatch.setattr(hostguard, "OS_RELEASE", tmp_path / "missing")
    assert hostguard.on_host()
    monkeypatch.setenv("FOXOS_PLACE", "foxos")
    assert not hostguard.on_host()


def test_US134_bots_act_in_the_vm_never_on_the_host(tmp_path):
    host = Host(tmp_path, "host")
    vm = Node(tmp_path, "foxos-vm")  # FOXOS_PLACE=foxos（conftest 默认）
    vm.serve()
    try:
        (host.ws / "h.txt").write_text("host file\n")
        st = host.ok("bot", "host-access")
        assert st["on_host"] and not st["enabled"]
        # 默认：智能体在宿主本机读写都被拒绝，审计里有记录；人照常
        for args in (["files", "read", "h.txt"], ["files", "write", "x.txt", "--content", "no"]):
            rc, d, _ = host.run(*args, agent="bot:fox")
            assert rc != 0 and d["error"]["code"] == "PERMISSION_DENIED" and "虚拟电脑" in d["error"]["message"]
        assert not (host.ws / "x.txt").exists()
        assert host.ok("files", "read", "h.txt")["content"] == "host file\n"
        denied = [e for e in host.audit() if e.get("agent") == "bot:fox" and e.get("status") == "denied"]
        assert len(denied) == 2
        # 路由到虚拟电脑：照常执行，对方审计写明控制端
        pair(vm, host, "vm")
        vm.ok("machine", "host", "grant", "--client", "ctl", "--bot", "fox", "--permissions", "read,create,modify", "--apps", "files")
        host.ok("files", "write", "in-vm.txt", "--content", "written in the vm", agent="bot:fox", machine="vm")
        assert (vm.ws / "in-vm.txt").read_text() == "written in the vm"
        assert not (host.ws / "in-vm.txt").exists()
        assert any(e.get("command") == "files.write" and e["agent"] == "bot:fox@ctl" for e in vm.audit())
        # 代码智能体（ACP）在宿主上默认不能运行
        rc, d, _ = host.run("bot", "message", "send", "fox", "read h.txt")
        assert rc == 0 and d["result"]["reply"]["error"]["code"] == "PERMISSION_DENIED"
        # 只有人能打开宿主执行
        rc, d, _ = host.run("bot", "host-access", "enable", agent="bot:fox")
        assert rc != 0 and d["error"]["code"] == "PERMISSION_DENIED"
        assert host.ok("bot", "host-access", "enable")["enabled"]
        # 打开以后：读放行；非只读的操作没有人逐个确认就拒绝（CLI 调用没有确认渠道）
        assert host.ok("files", "read", "h.txt", agent="bot:fox")["content"] == "host file\n"
        rc, d, _ = host.run("files", "write", "x.txt", "--content", "no", agent="bot:fox")
        assert rc != 0 and d["error"]["code"] == "PERMISSION_DENIED" and not (host.ws / "x.txt").exists()
    finally:
        vm.stop()


def _send_answering(host: Host, bot: str, text: str, allow: bool):
    cmd = [sys.executable, "-m", "foxos", "--workspace", str(host.ws), "--agent", "human", "--json", "bot", "message", "send", bot, text]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=host.env())
    seen = []
    t0 = time.time()
    while proc.poll() is None and time.time() - t0 < 120:
        for a in host.ok("bot", "approval", "list")["approvals"]:
            if a["id"] not in {x["id"] for x in seen}:
                seen.append(a)
                opt = next(o["optionId"] for o in a["options"] if o["kind"].startswith("allow" if allow else "reject"))
                host.ok("bot", "approval", "answer", a["id"], "--option", opt)
        time.sleep(0.2)
    out, _ = proc.communicate(timeout=30)
    return json.loads(out)["result"]["reply"], seen


def test_US134_opt_in_host_execution_asks_per_action(tmp_path):
    host = Host(tmp_path, "host")
    host.ok("bot", "host-access", "enable")
    # 已有“全部允许”规则也不能代替人逐个确认
    host.ok("bot", "config", "set", "fox", "--approval-mode", "allow_all")
    reply, seen = _send_answering(host, "fox", "write notes/ok.txt: confirmed on host", allow=True)
    assert (host.ws / "notes" / "ok.txt").read_text() == "confirmed on host"
    titles = [a["toolCall"].get("title", "") for a in seen]
    assert any("files.write" in t for t in titles), titles
    host_cards = [c for c in reply["cards"] if c.get("host")]
    assert host_cards and host_cards[0]["approval"]["decision"] == "allow" and host_cards[0]["approval"]["by"] == "human"
    reply, seen = _send_answering(host, "fox", "write notes/no.txt: refused", allow=False)
    assert seen and not (host.ws / "notes" / "no.txt").exists()
    # 关掉以后回到默认
    assert not host.ok("bot", "host-access", "disable")["enabled"]
    rc, d, _ = host.run("files", "read", "notes/ok.txt", agent="bot:fox")
    assert rc != 0 and d["error"]["code"] == "PERMISSION_DENIED"
