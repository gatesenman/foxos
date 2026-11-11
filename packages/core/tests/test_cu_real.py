"""电脑操控的真实端到端（US-120 起）：真的 XFCE 桌面、真的 agent-desktop / agent-browser / Chrome、真的 Jev 与 DeepSeek。

需要：DISPLAY（XFCE 会话）、agent-desktop、mousepad、xedit（x11-apps）、Chrome CDP（工作空间的 browser.json）、
DeepSeek 密钥（狐狸OS 密钥库），Jev 用例还需要 TYPESAFE_API_KEY。设置 FOXOS_CU_E2E=1 才跑；
FOXOS_CU_E2E_WS 指向一个已开启 CDP 的工作空间（默认 /tmp/wscu）。密钥不会出现在输出里。
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "packages" / "core"
pytestmark = pytest.mark.skipif(os.environ.get("FOXOS_CU_E2E") != "1" or not os.environ.get("DISPLAY"),
                                reason="real computer-use e2e: set FOXOS_CU_E2E=1 on a desktop session")
spec = importlib.util.spec_from_file_location("cu_bench", ROOT / "scripts" / "cu_bench.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
WS = Path(os.environ.get("FOXOS_CU_E2E_WS", "/tmp/wscu"))
PORT = 8766


def fox(*args, env=None, timeout=900):
    p = subprocess.run([sys.executable, "-m", "foxos", "--workspace", str(WS), "--agent", "bot:e2e", *args, "--json"], cwd=CORE,
                       capture_output=True, text=True, timeout=timeout, env=env or os.environ.copy())
    d = json.loads(p.stdout)
    assert d.get("ok"), d
    return d["result"]


@pytest.fixture(scope="module", autouse=True)
def site():
    WS.mkdir(parents=True, exist_ok=True)
    bench.serve_site(PORT)
    yield
    bench.sh("pkill -x mousepad; pkill -x xedit")


def _task(task, *extra, env=None):
    return fox("computer", "task", task, "--vision", "off", "--approve", "auto", "--max-steps", "14", *extra, env=env)


def test_US120_doctor_reports_default_stack_and_fallbacks():
    r = fox("computer", "doctor")
    st = r["stack"]
    assert st["observe_act"].startswith("agent-desktop@") and "computer_use" in st["fallbacks"] and "browser_use" in st["fallbacks"]
    assert st["step_policy"] == ("typesafe" if os.environ.get("TYPESAFE_API_KEY") else "deepseek")


@pytest.mark.skipif(not os.environ.get("TYPESAFE_API_KEY"), reason="needs a TypeSafe key")
def test_US121_default_path_agent_desktop_with_jev_edits_and_saves():
    bench.mousepad(WS, "us121.txt", "draft\n")
    r = _task('In the open Mousepad window (us121.txt), replace the whole document text with exactly "Shopping list: apples, milk" '
              "and then save the file.", "--app", "mousepad")
    assert r["routed_to"] == "computer" and r["surface"] == "a11y" and r["policy"] == "typesafe"
    assert (WS / "us121.txt").read_text().strip() == "Shopping list: apples, milk"
    assert r["s1_steps"] >= 1 and r["mean_policy_ms"] < 2000


def test_US122_step_policy_falls_back_to_deepseek_without_typesafe_key():
    env = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
    bench.mousepad(WS, "us122.txt", "milk\n")
    r = _task("In the open Mousepad window (us122.txt), make the document contain two lines: 'milk' then 'eggs', then save the file.",
              "--app", "mousepad", env=env)
    assert r["policy"] == "deepseek" and r["surface"] == "a11y"
    assert [x.strip() for x in (WS / "us122.txt").read_text().strip().splitlines()] == ["milk", "eggs"]


@pytest.mark.skipif(not shutil.which("xedit"), reason="needs xedit (x11-apps), an app without accessibility")
def test_US123_no_a11y_app_falls_back_to_screenshot_computer_use():
    bench.xedit(WS, "us123.txt")
    r = _task('In the xedit window (us123.txt), click into the large text area, type exactly "hello from screen mode" and then click '
              "the Save button at the top.", "--app", "xedit")
    assert r["surface"] == "screen" and r["routes"][0]["reason"] == "no accessible elements"
    assert (WS / "us123.txt").read_text().strip() == "hello from screen mode"


def test_US124_web_target_not_in_a11y_tree_falls_back_to_browser_use():
    bench.sh("pkill -x mousepad; pkill -x xedit")
    r = _task("On the Fox Shop page, enter the name Ada, choose the colour Green, place the order and report the order code shown.",
              "--url", f"http://127.0.0.1:{PORT}/")
    assert r["routed_to"] == "browser" and r["route_reason"]
    assert "FOX-Ada-green" in str(r["answer"])


def test_US125_surface_can_be_forced_per_call_and_per_bot():
    from foxos import bots
    assert bots.validate_patch(None, {"computer_use": {"surface": "browser", "step_policy": "deepseek"}})["computer_use"]["surface"] == "browser"
    env = {**os.environ, "FOXOS_CU_SURFACE": "browser"}
    r = _task("On the Fox Shop page, enter the name Bo, keep the default colour, place the order and report the order code shown.",
              "--url", f"http://127.0.0.1:{PORT}/", env=env)
    assert r["routed_to"] == "browser" and r["route_reason"] == "surface=browser" and "FOX-Bo-red" in str(r["answer"])


@pytest.mark.skipif(not os.environ.get("TYPESAFE_API_KEY"), reason="needs a TypeSafe key")
def test_US126_typesafe_provider_live_call():
    r = fox("model", "provider", "test", "typesafe")
    assert r["ok"] and r["choice"] == "save" and r["model"].startswith("jev-") and r["seconds"] < 10
