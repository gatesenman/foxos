"""真实模型的端到端回合（DeepSeek，OpenAI 兼容 API）。

- 主智能体「狐狸」用服务商预设 deepseek（模型后端，带函数调用）直接回答；
- 用 bot_task_delegate 委托给「编码助手」（opencode 经 ACP，模型 deepseek/deepseek-flash），
  编码助手改文件时弹出审批，由人（另一个进程里的 `bot approval answer`）批准或拒绝，卡片里有 diff；
- 用 pstack 技能；在另一台狐狸OS 上读目录；Qwen Code 经 OpenAI 兼容地址接 DeepSeek。

密钥从 ~/.secrets/deepseek_api_key（或 FOXOS_TEST_DEEPSEEK_KEY_FILE）读取，只经标准输入存进测试自己的密钥库，
不出现在命令行、日志和断言信息里。没有密钥文件时整个文件跳过（不算失败）。
模型回答不固定，所以断言落在可以核实的结果上：文件内容、审批记录、卡片、审计。
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from conftest import _env
from test_acp_real import CACHE, _online
from test_machines import Node, pair

KEY_FILE = Path(os.environ.get("FOXOS_TEST_DEEPSEEK_KEY_FILE", "~/.secrets/deepseek_api_key")).expanduser()
pytestmark = [
    pytest.mark.skipif(not KEY_FILE.is_file() or not KEY_FILE.read_text().strip(), reason="no DeepSeek key file (real-model e2e)"),
    pytest.mark.skipif(not _online(), reason="no network"),
]
MODEL = "deepseek/deepseek-flash"


class Box:
    def __init__(self, tmp: Path):
        self.ws = tmp / "ws"
        self.ws.mkdir()
        self.env = {"FOXOS_HOME": str(tmp / "home"), "FOXOS_RUNTIME_PREFIX": str(CACHE / "runtime"), "FOXOS_RUNTIME_BIN": str(tmp / "bin")}

    def cmd(self, *args):
        return [sys.executable, "-m", "foxos", "--workspace", str(self.ws), "--agent", "human", "--json", *args]

    def run(self, *args, stdin=None, timeout=600):
        p = subprocess.run(self.cmd(*args), input=stdin, capture_output=True, text=True, env=_env(self.env), timeout=timeout)
        return p.returncode, (json.loads(p.stdout) if p.stdout.strip() else None), p

    def ok(self, *args, **kw):
        rc, d, p = self.run(*args, **kw)
        assert rc == 0, f"{args[:3]}: exit {rc}\n{p.stdout[-2000:]}"
        return d["result"]

    def key(self, *args):
        with open(KEY_FILE, encoding="utf-8") as f:
            p = subprocess.run(self.cmd(*args), stdin=f, capture_output=True, text=True, env=_env(self.env), timeout=60)
        assert p.returncode == 0, "storing the key failed"

    def send_answering(self, bot: str, text: str, decide, timeout=600):
        """发消息；智能体每请求一次审批，就由 decide(approval) 决定 allow / reject（像人在界面上点）。"""
        proc = subprocess.Popen(self.cmd("bot", "message", "send", bot, text), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=_env(self.env))
        seen, t0 = [], time.time()
        while proc.poll() is None and time.time() - t0 < timeout:
            for a in self.ok("bot", "approval", "list")["approvals"]:
                if a["id"] in {s["id"] for s in seen}:
                    continue
                seen.append(a)
                opts = {o.get("kind", ""): o["optionId"] for o in a.get("options", [])}
                want = decide(a)
                oid = next((v for k, v in opts.items() if k.startswith(want)), None) or want
                self.ok("bot", "approval", "answer", a["id"], "--option", oid)
            time.sleep(0.3)
        out, err = proc.communicate(timeout=60)
        assert proc.returncode == 0, out[-2000:]
        return json.loads(out)["result"]["reply"], seen

    def messages(self, bot):
        return self.ok("bot", "message", "list", bot)["messages"]


@pytest.fixture(scope="module")
def box(tmp_path_factory):
    b = Box(tmp_path_factory.mktemp("deepseek"))
    assert b.ok("runtime", "install", "opencode")["results"][0]["ok"]
    b.key("acp", "key", "set", "opencode", "DEEPSEEK_API_KEY", "--value-stdin")
    b.ok("bot", "profile", "create", "编码助手", "--id", "coder", "--title", "写代码", "--acp-agent", "opencode", "--model", MODEL)
    b.key("bot", "config", "set", "fox", "--provider", "deepseek", "--api-key-stdin")
    return b


def test_US140_main_bot_real_deepseek_answer_and_provider_preset(box):
    cfg = box.ok("bot", "config", "get", "fox")["config"]
    assert cfg["backend"] == {**cfg["backend"], "kind": "model", "provider": "deepseek", "base_url": "https://api.deepseek.com"}
    assert cfg["has_api_key"] and "deepseek" in cfg["providers"]
    assert KEY_FILE.read_text().strip() not in json.dumps(cfg)
    r = box.ok("bot", "message", "send", "fox", "What is 17 multiplied by 23? Answer with the number only.")["reply"]
    assert "391" in r["text"] and r["stop_reason"] == "end_turn"
    ev = (box.ws / ".foxos" / "bots" / "fox" / "events.jsonl").read_text()
    assert '"model:deepseek-flash"' in ev


def test_US141_delegate_to_acp_code_bot_edit_with_diff_and_human_approval(box):
    (box.ws / "notes").mkdir(exist_ok=True)
    (box.ws / "notes" / "todo.txt").write_text("status: alpha\n")
    reply, seen = box.send_answering(
        "fox", "Use your bot_task_delegate tool to ask the bot with id coder to edit notes/todo.txt with its edit tool, "
               "replacing the word alpha with beta and changing nothing else. Then summarise what coder reported.",
        decide=lambda a: "allow")
    assert (box.ws / "notes" / "todo.txt").read_text().strip() == "status: beta"
    deleg = [c for c in reply["cards"] if c.get("type") == "delegation"]
    assert deleg and deleg[0]["to"] == "coder" and deleg[0]["status"] == "completed" and deleg[0].get("answer")
    assert seen and all(a["bot"] == "coder" for a in seen)
    coder = [m for m in box.messages("coder") if m["role"] == "bot"][-1]
    assert coder.get("delegated_by") == "bot:fox"
    edits = [c for c in coder["cards"] if c.get("kind") == "edit" and c.get("status") == "completed"]
    assert edits and (edits[-1].get("approval") or {}).get("decision", "").startswith("allow")
    diff = [x for c in edits for x in c.get("content") or [] if x.get("type") == "diff"]
    assert diff and "alpha" in (diff[-1].get("oldText") or "") and "beta" in diff[-1]["newText"]


def test_US142_human_denies_edit_file_untouched(box):
    (box.ws / "notes" / "keep.txt").write_text("keep me\n")
    reply, seen = box.send_answering("coder", "Use your edit tool to replace the word keep with drop in notes/keep.txt.",
                                     decide=lambda a: "reject")
    assert seen, "opencode should have asked before editing"
    assert (box.ws / "notes" / "keep.txt").read_text() == "keep me\n"
    assert any((c.get("approval") or {}).get("decision") == "deny" for c in reply["cards"])


def test_US143_pstack_skill_with_real_model(box):
    r = box.ok("bot", "message", "send", "fox", "/unslop Rewrite: 'In today's fast-paced world, it is important to note that "
                                                "our robust solution leverages synergy.' Give only the rewritten sentence.")["reply"]
    assert "unslop" in r["skills_used"]
    assert r["text"].strip() and "fast-paced" not in r["text"].lower()


def test_US144_real_model_bot_reads_another_foxos_machine(box, tmp_path):
    host = Node(tmp_path, "alpha-host")
    host.serve()
    try:
        ctl = Node.__new__(Node)
        ctl.name, ctl.home, ctl.ws, ctl.proc = "ctl", Path(box.env["FOXOS_HOME"]), box.ws, None
        pair(host, ctl, "alpha")
        host.ok("machine", "host", "grant", "--client", "ctl", "--bot", "fox", "--permissions", "read", "--apps", "files")
        (host.ws / "only-on-alpha-7c1f.txt").write_text("x")
        box.ok("bot", "config", "set", "fox", "--machines", "local,alpha")
        r = box.ok("bot", "message", "send", "fox", "Call files_list with machine set to alpha and path '.', then list the file names you got.")["reply"]
        assert "only-on-alpha-7c1f.txt" in r["text"]
        remote = [c for c in r["cards"] if c.get("title") == "files_list" and c.get("machine") == "alpha"]
        assert remote and remote[0]["status"] == "completed"
        hits = [e for e in host.audit() if e.get("command") == "files.list" and e.get("status") == "ok"]
        assert hits and hits[-1]["agent"].startswith("bot:fox/model:") and hits[-1]["agent"].endswith("@ctl")
    finally:
        host.stop()


def test_US145_qwen_code_via_openai_compatible_deepseek(box):
    assert box.ok("runtime", "install", "qwen")["results"][0]["ok"]
    box.key("acp", "key", "set", "qwen-code", "OPENAI_API_KEY", "--value-stdin")
    box.ok("acp", "agent", "config", "qwen-code", "--env", "OPENAI_BASE_URL=https://api.deepseek.com", "--env", "OPENAI_MODEL=deepseek-flash")
    box.ok("bot", "profile", "create", "Qwen", "--id", "qwen", "--acp-agent", "qwen-code")
    r, _ = box.send_answering("qwen", "Create the file notes/qwen.txt containing exactly: qwen via deepseek", decide=lambda a: "allow")
    assert (box.ws / "notes" / "qwen.txt").read_text().strip() == "qwen via deepseek"
    w = [json.loads(x) for x in (box.ws / ".foxos" / "audit.jsonl").read_text().splitlines() if '"files.write"' in x]
    assert any(e["agent"] == "bot:qwen/acp:qwen-code" and e["status"] == "ok" for e in w)


def test_US157_qwen_code_asks_before_writing_by_default(box):
    """在狐狸OS 里 Qwen Code 默认用 --approval-mode default：写文件前弹审批卡片；拒绝 → 文件不出现，批准 → 写入。"""
    if not (box.ws / ".foxos" / "bots" / "qwen").exists() and "qwen" not in json.dumps(box.ok("bot", "profile", "list")):
        test_US145_qwen_code_via_openai_compatible_deepseek(box)
    from foxos.apps import acp as acp_app
    assert acp_app.default_args("qwen-code", ["--acp"]) == ["--acp", "--approval-mode", "default"]
    assert acp_app.default_args("qwen-code", ["--acp", "--approval-mode=yolo"]) == ["--acp", "--approval-mode=yolo"]  # 人明确改过的以人为准
    (box.ws / "notes").mkdir(exist_ok=True)
    target = box.ws / "notes" / "qwen-ask.txt"
    _, seen = box.send_answering("qwen", "Use your write_file tool to create notes/qwen-ask.txt containing exactly: denied", decide=lambda a: "reject")
    assert seen and all(a["bot"] == "qwen" for a in seen), "Qwen Code should ask before writing"
    assert not target.exists()
    _, seen = box.send_answering("qwen", "Use your write_file tool to create notes/qwen-ask.txt containing exactly: approved", decide=lambda a: "allow")
    assert seen, "Qwen Code should ask before writing"
    assert target.read_text().strip() == "approved"
