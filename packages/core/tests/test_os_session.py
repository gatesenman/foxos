"""US-60：真实桌面会话命令（CLI + 接管）。假后端始终可跑；有 XFCE / xfwm4 时再跑一次真实会话。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

_TERM = shutil.which("xfce4-terminal") or shutil.which("xterm")
_SHOT = shutil.which("scrot") or shutil.which("maim")
HAS_XFCE = bool(
    shutil.which("xfwm4")
    and shutil.which("wmctrl")
    and shutil.which("xdotool")
    and _TERM
    and _SHOT
    and shutil.which("Xvfb")
)


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


def test_US60_desktop_human_output_lists_windows(fox, tmp_path):
    """不加 --json 时，人看到的也是窗口列表和会话状态，而不是空输出。"""
    env = {**_fake_env(tmp_path / "session.json"), "FOXOS_LANG": "zh-CN"}
    code, _, p = fox.run("desktop", "windows", json_out=False, extra_env=env)
    assert code == 0 and "没有窗口" in p.stdout
    fox.run("desktop", "launch", "terminal", extra_env=env, check=0)
    code, _, p = fox.run("desktop", "windows", json_out=False, extra_env=env)
    assert code == 0 and "terminal" in p.stdout and p.stdout.lstrip().startswith("*")
    code, _, p = fox.run("session", "status", json_out=False, extra_env=env)
    assert code == 0 and "backend: fake" in p.stdout and "paused:" in p.stdout


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


def _launch_terminal(title: str, env: dict) -> subprocess.Popen:
    term = shutil.which("xfce4-terminal") or shutil.which("xterm")
    if Path(term).name == "xfce4-terminal":
        argv = [term, "--disable-server", "--title", title]
    else:
        argv = [term, "-T", title]
    return subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


@pytest.fixture
def xfce_session(tmp_path):
    if not HAS_XFCE:
        pytest.skip("需要 xfwm4、wmctrl、xdotool、scrot/maim、xfce4-terminal/xterm、Xvfb")
    display = ":93"
    runtime = tmp_path / "xdg"
    runtime.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    env = {
        **os.environ,
        "DISPLAY": display,
        "HOME": str(home),
        "XDG_RUNTIME_DIR": str(runtime),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_CURRENT_DESKTOP": "XFCE",
        "XDG_SESSION_DESKTOP": "foxos",
        "XDG_SESSION_TYPE": "x11",
        "FOXOS_SESSION_BACKEND": "x11",
    }
    env.pop("WAYLAND_DISPLAY", None)
    log = open(runtime / "session.log", "wb")
    xvfb = subprocess.Popen(
        ["Xvfb", display, "-screen", "0", "1280x800x24", "-nolisten", "tcp"],
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    ready = False
    for _ in range(50):
        r = subprocess.run(["xset", "-display", display, "q"], capture_output=True)
        if r.returncode == 0:
            ready = True
            break
        time.sleep(0.1)
    if not ready:
        xvfb.kill()
        pytest.skip("Xvfb 未能启动测试显示")
    wm = subprocess.Popen(["xfwm4", "--compositor=off", "--sm-client-disable"], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(0.3)
    if wm.poll() is not None:
        xvfb.kill()
        pytest.skip("xfwm4 未能在测试显示上启动")
    yield env
    for p in (wm, xvfb):
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()


@pytest.mark.skipif(not HAS_XFCE, reason="需要 xfwm4、wmctrl、xdotool、scrot/maim、终端、Xvfb")
def test_US60_xfce_list_focus_type_click_move_close(fox, xfce_session):
    env = xfce_session
    _launch_terminal("us60-a", env)
    time.sleep(0.4)
    _launch_terminal("us60-b", env)
    time.sleep(0.5)
    wins = None
    for _ in range(25):
        wins = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
        titles = {w["title"] for w in wins["windows"]}
        if "us60-a" in titles and "us60-b" in titles:
            break
        time.sleep(0.15)
    titles = {w["title"] for w in wins["windows"]}
    assert "us60-a" in titles and "us60-b" in titles
    a = next(w for w in wins["windows"] if w["title"] == "us60-a")
    fox.run("desktop", "focus", a["id"], extra_env=env, check=0)
    after = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]["windows"]
    focused = next(w for w in after if w["id"] == a["id"])
    assert focused["focused"] is True
    fox.run("desktop", "type", "us60-ok", extra_env=env, check=0)
    fox.run("desktop", "click", "--x", "80", "--y", "80", extra_env=env, check=0)
    fox.run("desktop", "move", a["id"], "--x", "40", "--y", "60", extra_env=env, check=0)
    fox.run("desktop", "resize", a["id"], "--width", "640", "--height", "400", extra_env=env, check=0)
    moved = next(w for w in fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]["windows"] if w["id"] == a["id"])
    # xfwm 会加上边框，允许少量偏差
    assert abs(moved["x"] - 40) <= 40 and abs(moved["y"] - 60) <= 50
    assert abs(moved["width"] - 640) <= 40 and abs(moved["height"] - 400) <= 50
    fox.run("desktop", "screenshot", "--path", "shots/us60.png", extra_env=env, check=0)
    shot = fox.ws / "shots" / "us60.png"
    assert shot.exists() and shot.stat().st_size > 100
    fox.run("desktop", "close", a["id"], extra_env=env, check=0)
    time.sleep(0.4)
    left = fox.run("desktop", "windows", extra_env=env, check=0)[1]["result"]
    assert all(w["title"] != "us60-a" for w in left["windows"])
    st = fox.run("session", "status", extra_env=env, check=0)[1]["result"]
    assert st["backend"] == "x11" and st["available"] is True
