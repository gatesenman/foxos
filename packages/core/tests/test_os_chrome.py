"""US-62：Google Chrome 作为默认浏览器；`foxos desktop launch chrome`；本机 CDP（只听 127.0.0.1，人开启）。

没有 Chrome / Xvfb 时只跑开关与权限用例；有就真的启动 Chrome、打开网页、读标题、截图。
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

CHROME = shutil.which("google-chrome-stable") or shutil.which("google-chrome")
HAS_REAL = bool(CHROME and shutil.which("Xvfb"))


def _free_port() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def test_US62_cdp_is_off_by_default_and_only_a_person_can_enable_it(fox):
    st = fox.run("browser", "status", check=0)[1]["result"]
    assert st["cdp"]["enabled"] is False and st["cdp"]["address"] == "127.0.0.1"
    code, out, _ = fox.run("browser", "tabs")
    assert code == 4 and out["error"]["code"] == "PERMISSION_DENIED"
    code, out, _ = fox.run("browser", "cdp", "on")              # 智能体不能给自己开远程控制
    assert code == 4
    r = fox.run("browser", "cdp", "on", "--port", "9333", agent="human", check=0)[1]["result"]
    assert r["cdp"] == {"enabled": True, "address": "127.0.0.1", "port": 9333}
    fox.run("browser", "cdp", "off", check=0)                    # 智能体可以关
    assert fox.run("browser", "status", check=0)[1]["result"]["cdp"]["enabled"] is False


def test_US62_launch_chrome_alias_uses_foxos_chrome_flags(fox, tmp_path):
    fake = tmp_path / "s.json"
    fakechrome = tmp_path / "google-chrome-stable"
    fakechrome.write_text("#!/bin/sh\necho 'Google Chrome 1.0'\n"); fakechrome.chmod(0o755)
    env = {"FOXOS_SESSION_BACKEND": "fake", "FOXOS_SESSION_FAKE": str(fake), "FOXOS_CHROME": str(fakechrome),
           "XDG_CONFIG_HOME": str(tmp_path / "cfg")}
    fox.run("browser", "cdp", "on", "--port", "9444", agent="human", check=0, extra_env=env)
    r = fox.run("desktop", "launch", "chrome", "https://example.com", extra_env=env, check=0)[1]["result"]
    argv = r["command"]
    assert argv[0] == str(fakechrome)
    assert "--remote-debugging-address=127.0.0.1" in argv and "--remote-debugging-port=9444" in argv
    assert f"--user-data-dir={tmp_path / 'cfg' / 'foxos' / 'chrome-agent'}" in argv   # 单独的智能体配置文件
    assert argv[-1] == "https://example.com"
    # MCP 里也有同一组工具
    tools = fox.run("tools", check=0)[1]
    names = {t["name"] for t in (tools.get("result", tools).get("tools") if isinstance(tools, dict) else tools)}
    assert {"browser_open", "browser_tabs", "browser_screenshot", "browser_cdp"} <= names


def _listen_addrs(port: int) -> set[str]:
    out = set()
    for f in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            lines = Path(f).read_text().splitlines()[1:]
        except OSError:
            continue
        for ln in lines:
            parts = ln.split()
            local, state = parts[1], parts[3]
            addr, p = local.rsplit(":", 1)
            if int(p, 16) == port and state == "0A":
                out.add(addr)
    return out


@pytest.mark.skipif(not HAS_REAL, reason="需要 Google Chrome 与 Xvfb")
def test_US62_real_chrome_open_page_read_title_and_screenshot(fox, tmp_path):
    disp = ":%d" % (150 + os.getpid() % 50)
    xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1600x1000x24", "-nolisten", "tcp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    port = _free_port()
    env = {"DISPLAY": disp, "FOXOS_SESSION_BACKEND": "x11", "XDG_CONFIG_HOME": str(tmp_path / "cfg"),
           "FOXOS_CHROME_FLAGS": "--disable-gpu --password-store=basic"}
    try:
        time.sleep(1.5)
        page = fox.ws / "hello.html"
        page.write_text("<!doctype html><meta charset=utf-8><title>狐狸OS Chrome 测试</title>"
                        "<body style='background:#2a1f1a;color:#f5b84a;font:48px sans-serif'><h1>你好，Chrome</h1>", encoding="utf-8")
        fox.run("browser", "cdp", "on", "--port", str(port), agent="human", check=0, extra_env=env)
        r = fox.run("desktop", "launch", "chrome", page.as_uri(), extra_env=env, check=0)[1]["result"]
        assert r["pid"] > 0
        st = None
        for _ in range(60):
            st = fox.run("browser", "status", extra_env=env, check=0)[1]["result"]
            if st["cdp"]["running"]:
                break
            time.sleep(0.5)
        assert st and st["cdp"]["running"], st
        assert "Chrome" in st["cdp"]["browser"]
        assert _listen_addrs(port) <= {"0100007F", "00000000000000000000000001000000"}, _listen_addrs(port)  # 只听本机
        tabs = None
        for _ in range(40):
            tabs = fox.run("browser", "tabs", extra_env=env, check=0)[1]["result"]["tabs"]
            if any(t["url"].endswith("hello.html") and t["title"] for t in tabs):
                break
            time.sleep(0.5)
        tab = next(t for t in tabs if t["url"].endswith("hello.html"))
        assert tab["title"] == "狐狸OS Chrome 测试"
        v = fox.run("browser", "eval", "document.querySelector('h1').textContent", "--tab", tab["id"], extra_env=env, check=0)[1]["result"]
        assert v["value"] == "你好，Chrome"
        shot = fox.run("browser", "screenshot", "--path", "shots/chrome.png", "--tab", tab["id"], extra_env=env, check=0)[1]["result"]
        data = (fox.ws / "shots" / "chrome.png").read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and shot["bytes"] > 2000
        o = fox.run("browser", "open", "about:blank", extra_env=env, check=0)[1]["result"]
        assert o["via"] == "cdp" and o["tab"]
        fox.run("browser", "close", o["tab"], extra_env=env, check=0)
        if shutil.which("scrot") or shutil.which("maim"):
            fox.run("desktop", "screenshot", "--path", "shots/desk.png", extra_env=env, check=0)
            assert (fox.ws / "shots" / "desk.png").stat().st_size > 2000
    finally:
        subprocess.run(["pkill", "-f", f"remote-debugging-port={port}"], check=False)
        xvfb.terminate()
        try:
            xvfb.wait(5)
        except subprocess.TimeoutExpired:
            xvfb.kill()
