"""Vercel Labs agent-browser（Apache-2.0，npm agent-browser@0.42.0）的薄适配层：agent-desktop 的同门兄弟，管网页。

用 `--cdp <端口>` 连狐狸OS 自己的 Chrome（foxos browser 的 CDP），不另外下载浏览器；会话名按工作空间区分。
快照是同样的「- role "name" [ref=eN]」文字格式，按 @eN 点击 / 填写 / 按键 / 选择 / 滚动；遮挡、隐藏、禁用时报错而不是点错。
标签页：狐狸OS 的标签 id 就是 CDP target id，agent-browser 直接接受，所以每次操作前先切到那个标签。
`foxos browser backend set agent-browser|builtin|auto`（默认 auto：装了就用 agent-browser，否则用内置 CDP 实现）。
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

PIN = "agent-browser@0.42.0"
LICENSE = "Apache-2.0"
SYSTEM = Path(os.environ.get("FOXOS_SYSTEM_TOOLS", "/usr/lib/foxos/tools")) / "agent-browser"


def user_dir() -> Path:
    return secrets.home() / "tools" / "agent-browser"


def binary() -> str | None:
    if os.environ.get("FOXOS_AGENT_BROWSER"):
        return os.environ["FOXOS_AGENT_BROWSER"]
    for base in (SYSTEM, user_dir()):
        f = base / "node_modules" / ".bin" / "agent-browser"
        if f.exists():
            return str(f)
    return shutil.which("agent-browser")


def install() -> dict:
    if not shutil.which("npm"):
        raise FoxError("DEPENDENCY_MISSING", tr("ad.no_npm"), hint="sudo apt install nodejs npm")
    d = user_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["npm", "install", "--prefix", str(d), "--no-audit", "--no-fund", PIN], capture_output=True, text=True, timeout=900)
    if p.returncode != 0 or not binary():
        raise FoxError("ERROR", tr("ad.install_failed", (p.stderr or p.stdout)[-600:]))
    return {"installed": PIN, "path": binary(), "license": LICENSE}


def _session(ctx) -> str:
    return "foxos-" + hashlib.sha1(str(ctx.workspace.root).encode()).hexdigest()[:10]


def run(ctx, args: list[str], timeout: float = 60) -> dict:
    b = binary()
    if not b:
        raise FoxError("DEPENDENCY_MISSING", tr("ab.missing"), hint="foxos browser engine install agent-browser")
    from ..apps.browser import load_cfg
    port = str(load_cfg(ctx)["port"])
    cwd = ctx.workspace.data_dir / "agent-browser"
    cwd.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    readonly = args[0] in ("snapshot", "get") or args[:2] == ["tab", "list"]
    for attempt in range(2 if readonly else 1):  # 只读命令偶尔卡住（守护进程忙）：重试一次
        try:
            p = subprocess.run([b, "--cdp", port, "--session", _session(ctx), "--json", *args], capture_output=True, text=True,
                               timeout=timeout if not readonly else min(timeout, 30), cwd=str(cwd), env=env)
            break
        except subprocess.TimeoutExpired as e:
            if attempt or not readonly:
                raise FoxError("ERROR", tr("ab.timeout", " ".join(args[:2]))) from e
    line = next((ln for ln in reversed((p.stdout or "").splitlines()) if ln.startswith("{")), None)
    if not line:
        raise FoxError("ERROR", tr("ad.bad_output", args[0], (p.stderr or p.stdout)[-400:]))
    d = json.loads(line)
    if not d.get("success"):
        err = d.get("error")
        msg = err.get("message") if isinstance(err, dict) else str(err)
        raise FoxError("ERROR", f"agent-browser {args[0]}: {msg}")
    return d.get("data") or {}


def use_tab(ctx, tab: str | None) -> None:
    """切到狐狸OS 的标签（CDP target id）。注意：agent-browser 切标签会清掉快照引用，所以已经是当前标签时不切。"""
    if not tab:
        return
    tabs = run(ctx, ["tab", "list"]).get("tabs") or []
    if any(t.get("active") and tab in (t.get("targetId"), t.get("tabId"), t.get("label")) for t in tabs):
        return
    run(ctx, ["tab", tab])


def _ref(ref: str) -> str:
    ref = str(ref).strip()
    return ref if ref.startswith("@") or ref.startswith(("#", ".", "/", "[")) else "@" + ref


def snapshot(ctx, tab: str | None = None, interactive: bool = False) -> dict:
    use_tab(ctx, tab)
    d = run(ctx, ["snapshot", *(["-i"] if interactive else [])])
    snap = d.get("snapshot") or d.get("tree") or ""
    url = run(ctx, ["get", "url"]).get("url")
    title = run(ctx, ["get", "title"]).get("title")
    return {"tab": tab, "url": url, "title": title, "refs": len(d.get("refs") or {}), "snapshot": snap, "backend": PIN}


def _offscreen_retry(ctx, ref: str, args: list[str]) -> dict:
    """agent-browser 不点视口外的元素（防点错）：先 scrollintoview 再试一次。"""
    try:
        return run(ctx, args)
    except FoxError as e:
        if "outside the viewport" not in e.message and "not visible" not in e.message:
            raise
        run(ctx, ["scrollintoview", _ref(ref)])
        return run(ctx, args)


def click(ctx, ref: str, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return {"clicked": ref, **_offscreen_retry(ctx, ref, ["click", _ref(ref)])}


def fill(ctx, ref: str, text: str, tab: str | None = None, submit: bool = False) -> dict:
    use_tab(ctx, tab)
    r = _offscreen_retry(ctx, ref, ["fill", _ref(ref), "--", text])
    if submit:
        run(ctx, ["press", "Enter"])
    return {"typed": len(text), "ref": ref, "submitted": submit, **r}


def press(ctx, key: str, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return {"key": key, **run(ctx, ["press", key])}


def select(ctx, ref: str, value: str, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return {"ref": ref, "value": value, **run(ctx, ["select", _ref(ref), value])}


def scroll(ctx, direction: str = "down", amount: int = 600, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return {"direction": direction, **run(ctx, ["scroll", direction, str(amount)])}


def navigate(ctx, url: str, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return run(ctx, ["open", url], timeout=90)


def back(ctx, tab: str | None = None) -> dict:
    use_tab(ctx, tab)
    return run(ctx, ["back"])


def text(ctx, ref: str | None = None, tab: str | None = None, max_chars: int = 30000) -> dict:
    use_tab(ctx, tab)
    d = run(ctx, ["get", "text", _ref(ref) if ref else "body"])
    t = str(d.get("text") or "")
    return {"text": t[:max_chars], "truncated": len(t) > max_chars}


def status() -> dict:
    return {"installed": bool(binary()), "path": binary(), "pin": PIN, "license": LICENSE}
