"""foxos-bots：在狐狸OS 桌面上打开「智能体」窗口。

- 复用正在运行的 foxos bot serve（FOXOS_HOME/botchat.json 记录地址、令牌与 pid），没有就在后台启动一个；
- 用应用模式的浏览器窗口打开（Chromium/Chrome 的 --app，没有时用 Firefox 的独立配置），窗口类名 foxos-bots；
- 已经打开就切到前台；按 ~/.config/foxos/bots-ui.json 的偏好停靠到屏幕一侧或作为独立窗口（--dock / --undock 会改偏好）。

聊天窗口和系统里其它窗口是分开的：foxos desktop window list 给它标上 role=foxos-bots，智能体操作桌面时据此避开它。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

from . import server

CHROMIUMS = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge")


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _reachable(url: str) -> bool:
    u = urllib.parse.urlparse(url)
    try:
        with socket.create_connection((u.hostname, u.port), timeout=1.5):
            return True
    except OSError:
        return False


def running_url() -> str | None:
    try:
        info = json.loads(server.info_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not _alive(int(info.get("pid", 0))) or not _reachable(info["url"]):
        return None
    return f"{info['url']}?t={info['token']}"


def start_server(workspace: str | None) -> str:
    state = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "foxos"
    state.mkdir(parents=True, exist_ok=True)
    ready = state / f"bots-ready-{os.getpid()}"
    ready.unlink(missing_ok=True)
    argv = [sys.executable, "-m", "foxos", *(["--workspace", workspace] if workspace else []), "bot", "serve", "--ready-file", str(ready)]
    log = open(state / "bots.log", "ab")  # noqa: SIM115 - 交给子进程
    subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(200):
        if ready.exists() and ready.read_text().strip():
            url = ready.read_text().strip()
            ready.unlink(missing_ok=True)
            return url
        time.sleep(0.1)
    raise SystemExit("foxos-bots: bot serve did not start; see " + str(state / "bots.log"))


def _window_ids() -> list[str]:
    if not shutil.which("wmctrl") or not os.environ.get("DISPLAY"):
        return []
    r = subprocess.run(["wmctrl", "-lx"], capture_output=True, text=True)
    return [ln.split()[0] for ln in r.stdout.splitlines() if len(ln.split()) > 2 and server.WINDOW_CLASS in ln.split()[2].lower()]


def _firefox_profile() -> Path:
    p = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "foxos" / "bots-firefox"
    (p / "chrome").mkdir(parents=True, exist_ok=True)
    (p / "user.js").write_text("\n".join([
        'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
        'user_pref("browser.shell.checkDefaultBrowser", false);',
        'user_pref("browser.startup.homepage_override.mstone", "ignore");',
        'user_pref("datareporting.policy.dataSubmissionEnabled", false);',
        'user_pref("browser.tabs.inTitlebar", 0);',
        'user_pref("trailhead.firstrun.didSeeAboutWelcome", true);',
        'user_pref("browser.aboutwelcome.enabled", false);',
        'user_pref("toolkit.startup.max_resumed_crashes", -1);',
        'user_pref("browser.sessionstore.resume_from_crash", false);',
        'user_pref("browser.preonboarding.enabled", false);',
        'user_pref("termsofuse.bypassNotification", true);',
        'user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);',
        'user_pref("datareporting.policy.firstRunURL", "");',
    ]) + "\n", encoding="utf-8")
    # 应用模式：隐藏标签栏与地址栏
    (p / "chrome" / "userChrome.css").write_text("#TabsToolbar, #nav-bar, #PersonalToolbar, #titlebar { visibility: collapse !important; }\n", encoding="utf-8")
    return p


def browser_argv(url: str) -> list[str]:
    for b in ([os.environ["FOXOS_BOTS_BROWSER"]] if os.environ.get("FOXOS_BOTS_BROWSER") else []) + list(CHROMIUMS):
        exe = shutil.which(b)
        if exe and "firefox" not in b:
            data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "foxos" / "bots-browser"
            return [exe, f"--app={url}", f"--class={server.WINDOW_CLASS}", f"--user-data-dir={data}", "--no-first-run",
                    "--no-default-browser-check", "--window-size=1100,760"]
    ff = shutil.which("firefox")
    if ff:
        return [ff, "--new-instance", "--profile", str(_firefox_profile()), "--class", server.WINDOW_CLASS, "--name", server.WINDOW_CLASS, url]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="foxos-bots", description="Open the FoxOS bots window")
    ap.add_argument("--workspace", "-w", default=None)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dock", action="store_true", help="dock to the side of the screen and remember it")
    g.add_argument("--undock", action="store_true", help="separate window and remember it")
    ap.add_argument("--side", choices=["left", "right"])
    ap.add_argument("--url", default=None, help="use this server URL instead of finding or starting one")
    ap.add_argument("--print-url", action="store_true", help="only print the URL (starts the server if needed)")
    ap.add_argument("--bot", default=None, help="open this bot")
    ap.add_argument("--page", default=None, help="open a page: approvals, connectors, agents, machines, skills, routines, runtime, "
                                                 "or settings/<bot>/<tab>")
    a = ap.parse_args(argv)
    prefs = server.load_prefs()
    if a.dock or a.undock or a.side:
        prefs = server.save_prefs({**({"dock": bool(a.dock)} if (a.dock or a.undock) else {}), **({"side": a.side} if a.side else {})})
    url = a.url or running_url() or start_server(a.workspace)
    if a.print_url:
        print(url)
        return 0
    wins = _window_ids()
    if wins:
        subprocess.run(["wmctrl", "-i", "-a", wins[0]])
        print(json.dumps({"url": url.split("?")[0], "reused_window": True, "window": server.apply_window_mode(prefs)}))
        return 0
    if a.page:
        url += "#" + "/".join(urllib.parse.quote(x) for x in a.page.split("/"))
    elif a.bot:
        url += "#bot/" + urllib.parse.quote(a.bot)
    cmd = browser_argv(url)
    if not cmd:
        print("foxos-bots: no browser found (install chromium or firefox); open " + url.split("?")[0], file=sys.stderr)
        return 6
    subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    applied = {"applied": False}
    for _ in range(100):
        if _window_ids():
            time.sleep(0.4)
            applied = server.apply_window_mode(prefs)
            break
        time.sleep(0.15)
    print(json.dumps({"url": url.split("?")[0], "browser": os.path.basename(cmd[0]), "window": applied}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
