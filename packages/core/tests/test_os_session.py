"""US-60：真实桌面会话命令（CLI + 接管）。假后端始终可跑；有 labwc 时再跑一次真实合成器。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

HAS_LABWC = bool(shutil.which("labwc") and shutil.which("foot") and shutil.which("wtype") and shutil.which("grim"))


def _fake_env(path: Path) -> dict:
    return {"FOXOS_SESSION_BACKEND": "fake", "FOXOS_SESSION_FAKE": str(path)}


def test_US60_desktop_and_session_commands_fake_backend(fox, tmp_path):
    fake = tmp_path / "session.json"
    env = _fake_env(fake)
    r = fox.run("desktop", "launch", "terminal", extra_env=env, check=0)[1]["result"]
    assert r["id"] == "1"
    wins = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
    assert wins["count"] == 1 and wins["windows"][0]["title"] == "terminal" and wins["windows"][0]["focused"]
    fox.run("desktop", "launch", "editor", extra_env=env, check=0)
    wins = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
    assert wins["count"] == 2
    term = next(w for w in wins["windows"] if w["title"] == "terminal")
    fox.run("desktop", "focus", term["id"], extra_env=env, check=0)
    wins = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
    focused = [w for w in wins["windows"] if w["focused"]]
    assert len(focused) == 1 and focused[0]["id"] == term["id"]
    fox.run("desktop", "move", term["id"], "--x", "40", "--y", "80", extra_env=env, check=0)
    fox.run("desktop", "resize", term["id"], "--width", "640", "--height", "480", extra_env=env, check=0)
    moved = next(w for w in fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]["windows"] if w["id"] == term["id"])
    assert moved["x"] == 40 and moved["y"] == 80 and moved["width"] == 640 and moved["height"] == 480
    fox.run("desktop", "type", "hello", extra_env=env, check=0)
    fox.run("desktop", "click", "--x", "10", "--y", "20", extra_env=env, check=0)
    fox.run("desktop", "screenshot", "--path", "shots/desk.png", extra_env=env, check=0)
    assert (fox.ws / "shots" / "desk.png").exists()
    fox.run("desktop", "close", term["id"], extra_env=env, check=0)
    left = fox.run("session", "windows", extra_env=env, check=0)[1]["result"]  # session 是同一套命令
    assert left["count"] == 1 and left["windows"][0]["title"] == "editor"

    # 智能体不能发起接管；人可以，之后智能体写操作（type）被拒绝
    code, out, _ = fox.run("desktop", "takeover", "--reason", "我来改", extra_env=env)
    assert code == 4
    fox.run("session", "takeover", "--reason", "我来改", agent="human", extra_env=env, check=0)
    st = fox.run("desktop", "status", extra_env=env, check=0)[1]["result"]
    assert st["paused"] is True and st["takeover"]["reason"] == "我来改"
    code, out, _ = fox.run("desktop", "type", "agent", extra_env=env)
    assert code == 8 and out["error"]["code"] == "PAUSED"
    fox.run("desktop", "type", "ok", agent="human:desktop", extra_env=env, check=0)
    fox.run("session", "resume", agent="human", extra_env=env, check=0)
    fox.run("desktop", "type", "again", extra_env=env, check=0)
    data = json.loads(fake.read_text())
    assert "hello" in data["typed"] and "again" in data["typed"] and data["clicks"][0]["x"] == 10


def test_US60_mcp_exposes_desktop_tools(fox):
    cat = fox.run("help", check=0)[1]
    apps = {a["name"]: a for a in cat["apps"]}
    assert "desktop" in apps and "session" in apps
    ids = {c["id"] for c in apps["desktop"]["commands"]}
    for cid in ("desktop.windows", "desktop.focus", "desktop.move", "desktop.type", "desktop.click", "desktop.takeover"):
        assert cid in ids
    _, _, p = fox.run("tools", "--format", "mcp", json_out=False, check=0)
    names = {t["name"] for t in json.loads(p.stdout)}
    assert "desktop_windows" in names and "session_takeover" in names and "desktop_move" in names


@pytest.fixture
def labwc_session(tmp_path):
    if not HAS_LABWC:
        pytest.skip("需要 labwc、foot、wtype、grim")
    runtime = tmp_path / "xdg"
    runtime.mkdir()
    cfg = runtime / "labwc-cfg"
    cfg.mkdir()
    env = {
        **os.environ,
        "XDG_RUNTIME_DIR": str(runtime),
        "XDG_CURRENT_DESKTOP": "labwc",
        "WLR_BACKENDS": "headless",
        "WLR_LIBINPUT_NO_DEVICES": "1",
        "WAYLAND_DISPLAY": "wayland-0",
        "LABWC_CONFIG_DIR": str(cfg),
    }
    log = open(runtime / "labwc.log", "wb")
    proc = subprocess.Popen(["labwc"], env=env, stdout=log, stderr=log, start_new_session=True)
    sock = runtime / "wayland-0"
    for _ in range(50):
        if sock.exists():
            break
        time.sleep(0.1)
    if not sock.exists():
        proc.kill()
        pytest.skip("labwc 未能创建 Wayland 套接字")
    yield env
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.mark.skipif(not HAS_LABWC, reason="需要 labwc、foot、wtype、grim")
def test_US60_labwc_list_focus_type_click_close(fox, labwc_session):
    env = {**labwc_session, "FOXOS_SESSION_BACKEND": "wayland"}
    # 两扇真实窗口
    subprocess.Popen(["foot", "-T", "us60-a"], env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(0.3)
    subprocess.Popen(["foot", "-T", "us60-b"], env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(0.4)
    wins = None
    for _ in range(20):
        wins = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
        if wins["count"] >= 2:
            break
        time.sleep(0.1)
    titles = {w["title"] for w in wins["windows"]}
    assert "us60-a" in titles and "us60-b" in titles
    a = next(w for w in wins["windows"] if w["title"] == "us60-a")
    fox.run("desktop", "focus", a["id"], extra_env=env, check=0)
    after = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]["windows"]
    focused = next(w for w in after if w["id"] == a["id"])
    assert focused["focused"] is True
    fox.run("desktop", "type", "us60-ok", extra_env=env, check=0)
    fox.run("desktop", "click", "--x", "80", "--y", "80", extra_env=env, check=0)
    fox.run("desktop", "screenshot", "--path", "shots/us60.png", extra_env=env, check=0)
    shot = fox.ws / "shots" / "us60.png"
    assert shot.exists() and shot.stat().st_size > 100
    fox.run("desktop", "close", a["id"], extra_env=env, check=0)
    time.sleep(0.3)
    left = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
    assert all(w["title"] != "us60-a" for w in left["windows"])
    st = fox.run("session", "status", extra_env=env, check=0)[1]["result"]
    assert st["backend"] == "wayland" and st["available"] is True
    # 真实 labwc 没有程序化 move（无 wlrctl 时）
    code, out, _ = fox.run("desktop", "move", left["windows"][0]["id"], "--x", "10", "--y", "10", extra_env=env)
    assert code == 6 and out["error"]["code"] == "DEPENDENCY_MISSING"
