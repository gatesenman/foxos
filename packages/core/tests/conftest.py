import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1]
# 测试默认模拟“运行在狐狸OS 虚拟电脑里”；宿主保护（智能体不在宿主上动手）由 test_hostguard.py 用 FOXOS_PLACE=host 单独测
os.environ.setdefault("FOXOS_PLACE", "foxos")


def _env(extra=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CORE) + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("FOXOS_AGENT", None)
    env.pop("FOXOS_WORKSPACE", None)
    env.pop("FOXOS_LANG", None)  # 默认语言（中文），个别用例显式传入
    env.update(extra or {})
    return env


class FoxCLI:
    def __init__(self, ws: Path):
        self.ws = ws

    def run(self, *args, agent="test-agent", json_out=True, check=None, extra_env=None, timeout=180):
        cmd = [sys.executable, "-m", "foxos", "--workspace", str(self.ws), "--agent", agent, *args]
        if json_out:
            cmd.append("--json")
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=_env(extra_env), timeout=timeout)
        data = None
        if json_out and p.stdout.strip():
            data = json.loads(p.stdout)
        if check is not None:
            assert p.returncode == check, f"exit {p.returncode} != {check}\nstdout={p.stdout}\nstderr={p.stderr}"
        return p.returncode, data, p

    def popen(self, *args, agent="test-agent"):
        cmd = [sys.executable, "-m", "foxos", "--workspace", str(self.ws), "--agent", agent, *args, "--json"]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=_env())

    def audit(self):
        p = self.ws / ".foxos" / "audit.jsonl"
        if not p.exists():
            return []
        return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture
def ws(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    return root


@pytest.fixture
def fox(ws):
    return FoxCLI(ws)


@pytest.fixture
def core_env():
    return _env()
