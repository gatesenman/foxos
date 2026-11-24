"""不需要模型密钥的真实 Mousepad 回归；只在专门的测试显示器上运行。

FOXOS_CU_GUI=1 DISPLAY=:119 PYTHONPATH=packages/core pytest -q packages/core/tests/test_cu_gui.py
这不是 US121/US122 的规划器端到端，也不是 ISO 测试。
"""
import os
import shutil
import subprocess
import time
from types import SimpleNamespace
from pathlib import Path

import pytest

from foxos.cu import agent_desktop as ad

pytestmark = pytest.mark.skipif(
    os.environ.get("FOXOS_CU_GUI") != "1" or not os.environ.get("DISPLAY"),
    reason="requires an explicitly selected isolated GUI test display")


@pytest.mark.parametrize("case,initial,expected", [
    ("replace", "draft\n", "Shopping list: apples, milk"), ("append", "milk\n", "milk\neggs")])
def test_mousepad_semantic_edit_and_save(tmp_path, case, initial, expected):
    assert shutil.which("mousepad") and ad.available()
    path = tmp_path / "notes.txt"
    path.write_text(initial)
    data = tmp_path / "state"
    data.mkdir()
    ws = SimpleNamespace(data_dir=data)
    proc = subprocess.Popen(["mousepad", "--disable-server", str(path)],
                            env={**os.environ, "LC_ALL": "C.UTF-8"})
    try:
        deadline = time.monotonic() + 60
        while True:
            wins = [w for w in ad.windows("mousepad") if str(path) in (w.get("title") or "")
                    or "notes.txt" in (w.get("title") or "")]
            if len(wins) == 1:
                break
            assert time.monotonic() < deadline, wins
            time.sleep(0.5)
        wid = wins[0]["id"]
        snap = ad.snapshot(ws, window_id=wid)
        assert snap["complete"], snap
        fields = [n for n in snap["nodes"] if n.get("role") == "textfield" and n.get("value") == initial]
        assert len(fields) == 1, fields
        assert ad.act(ws, "get", fields[0]["ref"], property="text")["value"] == initial
        # 窗口标题解析也必须落到同一个真实窗口，不能把标题当进程名传下去。
        snap = ad.snapshot(ws, app=wins[0]["title"])
        fields = [n for n in snap["nodes"] if n.get("role") == "textfield" and n.get("value") == initial]
        assert len(fields) == 1
        ad.act(ws, "set-value", fields[0]["ref"], expected)
        snap = ad.snapshot(ws, window_id=wid)
        fields = [n for n in snap["nodes"] if n.get("role") == "textfield" and n.get("value") == expected]
        assert len(fields) == 1, fields
        # 用菜单的语义动作保存，不通过文件 API 改写结果。
        menus = [n for n in snap["nodes"] if n.get("role") == "menu" and n.get("name") == "File"]
        assert len(menus) == 1, menus
        ad.act(ws, "click", menus[0]["ref"])
        snap = ad.snapshot(ws, window_id=wid)
        save = [n for n in snap["nodes"] if n.get("role") == "menuitem" and n.get("name") == "Save"]
        assert len(save) == 1, save
        ad.act(ws, "click", save[0]["ref"])
        deadline = time.monotonic() + 10
        while path.read_text() != expected and time.monotonic() < deadline:
            time.sleep(0.2)
        assert path.read_text() == expected
        if evidence := os.environ.get("FOXOS_CU_EVIDENCE_DIR"):
            target = Path(evidence)
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target / f"{case}.txt")
        print(f"real-file-content: {path.read_text()!r}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
