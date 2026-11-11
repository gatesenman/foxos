"""ISO 阶段的智能体运行环境：在镜像 chroot 的 overlay 里（scripts/os/tools/agent-overlay.sh up，
跑的是和 ISO 构建同一份 hook 30/35），以普通用户 foxos 检查预装的版本、ACP 注册与 PEP 668。

overlay 没挂载或没有免密 sudo 时跳过。
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
OVL = Path(os.environ.get("FOXOS_OVL", "/var/tmp/foxos-agentchat-ovl"))
TOOL = ROOT / "scripts" / "os" / "tools" / "agent-overlay.sh"


def _ready() -> bool:
    if not (OVL / "root" / "usr" / "bin" / "foxos").exists() or not shutil.which("sudo"):
        return False
    return subprocess.run(["sudo", "-n", "true"], capture_output=True).returncode == 0


pytestmark = pytest.mark.skipif(not _ready(), reason="agent overlay not mounted (scripts/os/tools/agent-overlay.sh up)")


def as_foxos(cmd: str, timeout=300) -> str:
    p = subprocess.run(["sudo", "-n", "-E", "bash", str(TOOL), "as-foxos", cmd], capture_output=True, text=True, timeout=timeout)
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout


def test_US79_iso_runtime_versions_as_user_foxos():
    m = json.loads((ROOT / "packages/core/foxos/data/runtime-manifest.json").read_text())
    tools = {t["name"]: t for t in m["tools"]}
    out = as_foxos("foxos runtime doctor --json")
    d = json.loads(out)["result"]
    assert d["ok"], d
    assert d["python"]["pep668"] is True and d["python"]["foxos_venv"]
    iso = [t for t in d["tools"] if t["phase"] == "iso"]
    assert iso and all(tools[t["name"]]["redistributable"] for t in iso)
    bad = [(t["name"], t.get("found")) for t in iso if not t["ok"]]
    assert not bad, bad
    for t in iso:
        v = tools[t["name"]].get("version")
        if v and v[0].isdigit() and tools[t["name"]]["kind"] not in ("apt", "bundled"):
            assert v in (t.get("found") or ""), (t["name"], t.get("found"), v)
    # 专有智能体不在镜像里
    for name in ("claude", "claude-acp", "cursor-agent"):
        assert tools[name]["phase"] != "iso" and not tools[name]["redistributable"]
        assert not (OVL / "root" / "usr" / "lib" / "foxos" / "runtime" / name).exists()
    # 系统 python 不能被 pip 污染（PEP 668），foxos 自己的 venv 可用
    r = subprocess.run(["sudo", "-n", "-E", "bash", str(TOOL), "as-foxos", "python3 -m pip install --user requests"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "externally-managed" in (r.stdout + r.stderr)
    assert "ok" in as_foxos("/usr/lib/foxos/venv/bin/python -c 'import pptx, zstandard; print(\"ok\")'")


def test_US80_iso_acp_agents_registered_and_handshake_as_foxos():
    d = json.loads(as_foxos("foxos acp agent list --json"))["result"]["agents"]
    ids = {a["id"] for a in d}
    assert {"gemini", "codex-acp", "qwen-code", "opencode"} <= ids, ids
    p = json.loads(as_foxos("foxos acp agent probe opencode --json", timeout=180))["result"]
    assert p["protocolVersion"] == 1 and p["session"]["ok"]
    g = json.loads(as_foxos("foxos acp agent probe gemini --json", timeout=180))["result"]
    assert g["protocolVersion"] == 1 and g["session"].get("auth_required")
