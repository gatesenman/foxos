"""Vercel Labs agent-desktop（Apache-2.0，npm agent-desktop@1.2.0）的薄适配层：狐狸OS 桌面操控的主后端。

agent-desktop 读 AT-SPI 无障碍树，返回 JSON 快照，每个可操作元素一个限定引用 @<快照id>:eN；按引用点击、输入、
设值、选择、滚动，默认「无头语义投递」（不移动鼠标、不抢焦点）。它没有模型，循环在我们这边（cu/policy.py）。
- 安装时下载（npm），系统镜像预装在 /usr/lib/foxos/tools/agent-desktop；用户安装在 FOXOS_HOME/tools/agent-desktop
- 每个命令一行 JSON 信封 {ok, data | error{code, message, disposition}}；STALE_REF / AMBIGUOUS_TARGET 时重新快照
- 给模型看的是短引用 eN（不带快照 id），适配层按最近一次快照补全成 @sid:eN；快照 id 存在 .foxos/agent-desktop.json
- 没有无障碍信息的程序（游戏、画布、远程桌面）退回截图 + xdotool（foxos desktop click/type/key、视觉定位）
文字输入走 --stdin，不出现在进程参数里。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

PIN = "agent-desktop@1.2.0"
LICENSE = "Apache-2.0"
SYSTEM = Path(os.environ.get("FOXOS_SYSTEM_TOOLS", "/usr/lib/foxos/tools")) / "agent-desktop"
INTERACTIVE = {"button", "menuitem", "menu", "checkbox", "radiobutton", "textfield", "textarea", "combobox", "listitem", "tab",
               "link", "slider", "spinbutton", "treeitem", "switch", "searchfield", "togglebutton", "menuitemcheckbox",
               "menuitemradio", "option", "cell", "text", "entry", "document"}
ERR_MAP = {"STALE_REF": "CONFLICT", "AMBIGUOUS_TARGET": "CONFLICT", "INVALID_ARGS": "USAGE", "NOT_FOUND": "NOT_FOUND",
           "ELEMENT_NOT_FOUND": "NOT_FOUND", "APP_NOT_FOUND": "NOT_FOUND", "PERMISSION_DENIED": "PERMISSION_DENIED", "TIMEOUT": "ERROR"}
# agent-desktop 默认 --timeout-ms 3000。慢机器（QEMU TCG）上 3 秒读不完窗口，快照里的引用会带
# identity_not_unique，随后 click / set-value 一律 AMBIGUOUS_TARGET。默认提到 30 秒；未读完就再加倍重试。
DEFAULT_TIMEOUT_MS = 30_000
MAX_TIMEOUT_MS = 120_000


def timeout_ms(override: int | None = None) -> int:
    if override is not None:
        return max(1000, int(override))
    raw = os.environ.get("FOXOS_AD_TIMEOUT_MS")
    try:
        return max(1000, int(raw)) if raw else DEFAULT_TIMEOUT_MS
    except ValueError:
        return DEFAULT_TIMEOUT_MS


def user_dir() -> Path:
    return secrets.home() / "tools" / "agent-desktop"


def binary() -> str | None:
    if os.environ.get("FOXOS_AGENT_DESKTOP"):
        return os.environ["FOXOS_AGENT_DESKTOP"]
    for base in (SYSTEM, user_dir()):
        f = base / "node_modules" / ".bin" / "agent-desktop"
        if f.exists():
            return str(f)
    return shutil.which("agent-desktop")


def install() -> dict:
    if not shutil.which("npm"):
        raise FoxError("DEPENDENCY_MISSING", tr("ad.no_npm"), hint="sudo apt install nodejs npm")
    d = user_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["npm", "install", "--prefix", str(d), "--no-audit", "--no-fund", PIN], capture_output=True, text=True, timeout=900)
    if p.returncode != 0 or not binary():
        raise FoxError("ERROR", tr("ad.install_failed", (p.stderr or p.stdout)[-600:]))
    return {"installed": PIN, "path": binary(), "license": LICENSE}


def available() -> bool:
    return bool(binary())


def run(args: list[str], stdin: str | None = None, timeout: float | None = None, timeout_ms_: int | None = None) -> dict:
    b = binary()
    if not b:
        raise FoxError("DEPENDENCY_MISSING", tr("ad.missing"), hint="foxos computer backend install")
    ms = timeout_ms(timeout_ms_)
    # snapshot / find 等观察命令吃 --timeout-ms；其它命令忽略未知标志会失败，所以只加给认识它的命令。
    obs = args and args[0] in {"snapshot", "find", "get", "is", "wait"}
    if obs and "--timeout-ms" not in args:
        args = [*args, "--timeout-ms", str(ms)]
    wall = timeout if timeout is not None else max(60.0, ms / 1000 + 30)
    try:
        p = subprocess.run([b, *args], input=stdin, capture_output=True, text=True, timeout=wall)
    except subprocess.TimeoutExpired as e:
        raise FoxError("ERROR", tr("ad.timeout", args[0])) from e
    line = next((ln for ln in reversed((p.stdout or "").splitlines()) if ln.startswith("{")), None)
    if not line:
        raise FoxError("ERROR", tr("ad.bad_output", args[0], (p.stderr or p.stdout)[-400:]))
    env = json.loads(line)
    if not env.get("ok"):
        err = env.get("error") or {}
        code = str(err.get("code") or "ERROR")
        e = FoxError(ERR_MAP.get(code, "ERROR"), f"agent-desktop {args[0]}: {code}: {err.get('message') or ''}".strip())
        e.details = {"agent_desktop_code": code, "retry": (err.get("disposition") or {}).get("retry"), "details": err.get("details")}
        raise e
    return env.get("data") or {}


# ---------------------------------------------------------------- 快照与引用

def _state_path(ws) -> Path:
    return ws.data_dir / "agent-desktop.json"


def _save_sid(ws, sid: str, app: str | None, window_id: str | None, refs: dict | None = None, nodes: list | None = None) -> None:
    slim = [{k: n.get(k) for k in ("ref", "qref", "role", "name", "description", "value") if n.get(k) not in (None, "")}
            for n in (nodes or []) if n.get("ref")]
    _state_path(ws).write_text(json.dumps({"snapshot_id": sid, "app": app, "window_id": window_id, "refs": refs or {},
                                           "nodes": slim}), encoding="utf-8")


def last(ws) -> dict:
    try:
        return json.loads(_state_path(ws).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def qualify(ws, ref: str) -> str:
    ref = str(ref).strip()
    if ref.startswith("@") and ":" in ref:
        return ref
    st = last(ws)
    if ref.lstrip("@") in (st.get("refs") or {}):
        return st["refs"][ref.lstrip("@")]
    sid = st.get("snapshot_id")
    if not sid:
        raise FoxError("NOT_FOUND", tr("ad.no_snapshot"), hint="foxos computer snapshot")
    return f"@{sid}:{ref.lstrip('@')}"


def flatten(tree: dict) -> list[dict]:
    """快照树 → 扁平节点表（深度、短引用、角色、名字、描述、状态、动作、值、边框）。"""
    out: list[dict] = []

    def rec(n: dict, depth: int):
        ref = n.get("ref_id")
        item = {"depth": depth, "role": n.get("role") or "", "name": (n.get("name") or "").strip()}
        if ref:
            item["ref"] = ref.split(":")[-1]
            item["qref"] = ref
        for k in ("description", "value", "text"):
            if n.get(k) not in (None, ""):
                item[k] = n[k] if not isinstance(n[k], str) else n[k].strip()
        if n.get("states"):
            item["states"] = n["states"]
        if n.get("available_actions"):
            item["actions"] = n["available_actions"]
        if n.get("bounds"):
            item["bounds"] = n["bounds"]
        out.append(item)
        for c in n.get("children") or []:
            rec(c, depth + 1)

    if tree:
        rec(tree, 0)
    return out


def render(nodes: list[dict], hide_offscreen: bool = True) -> str:
    lines = []
    for n in nodes:
        st = n.get("states") or []
        if hide_offscreen and "offscreen" in st:
            continue
        if not n.get("ref") and not n.get("name") and not n.get("text"):
            continue
        s = "  " * n["depth"] + f"- {n['role']}"
        if n.get("name"):
            s += " " + json.dumps(n["name"][:120], ensure_ascii=False)
        if n.get("ref"):
            s += f" [ref={n['ref']}]"
        if st:
            s += " [" + ", ".join(x for x in st if x != "offscreen") + "]" if [x for x in st if x != "offscreen"] else ""
        v = n.get("value") if n.get("value") is not None else n.get("text")
        if v not in (None, ""):
            s += ": " + json.dumps(str(v)[:200], ensure_ascii=False)
        lines.append(s)
    return "\n".join(lines)


def _snap_args(app, window_id, interactive, bounds, max_depth, surface, root_q):
    args = ["snapshot", "--compact", "--max-depth", str(max_depth)]
    if app and not window_id:
        args += ["--app", app]
    if window_id:
        args += ["--window-id", str(window_id)]
    if interactive:
        args.append("-i")
    if bounds:
        args.append("--include-bounds")
    if surface:
        args += ["--surface", surface]
    if root_q:
        args += ["--root", root_q]
    return args


def resolve_app(app: str | None, window_id: str | None = None) -> tuple[str | None, str | None]:
    """agent-desktop 的 --app 必须是 list-apps 里的名字，不能是窗口标题，否则 APP_NOT_FOUND。
    若调用方传入了标题（例如「us121.txt - Mousepad」），改成对应窗口的 id。"""
    if window_id or not app:
        return app, window_id
    try:
        if windows(app):
            return app, None
    except FoxError as e:
        if (e.details or {}).get("agent_desktop_code") not in {"APP_NOT_FOUND", "NOT_FOUND"}:
            raise
    try:
        all_w = windows()
    except FoxError:
        return app, None
    low = app.lower().strip()
    hits = [w for w in all_w if low == (w.get("app") or "").lower()
            or low in (w.get("title") or "").lower()
            or (w.get("title") or "").lower() in low]
    if not hits:
        return app, None
    exact = [w for w in hits if (w.get("title") or "").lower() == low]
    w = exact[0] if exact else hits[0]
    return (w.get("app") or app), w.get("id")


def snapshot(ws, app: str | None = None, window_id: str | None = None, interactive: bool = False, bounds: bool = True,
             max_depth: int = 14, surface: str | None = None, root: str | None = None, timeout_ms_: int | None = None) -> dict:
    """一个程序有好几个窗口（例如主窗口 + 对话框）时 agent-desktop 报 AMBIGUOUS_TARGET：逐个窗口快照再合并，
    对话框排在前面；第二个及以后窗口的引用加窗口前缀（w2e5），适配层记住它们对应的限定引用。
    快照若在时限内没读完（complete=false），把时限加倍再拍一次，避免引用带着 identity_not_unique。"""
    app, window_id = resolve_app(app, window_id)
    root_q = qualify(ws, root) if root else None
    ms = timeout_ms(timeout_ms_)

    def take(app_, window_id_, ms_):
        return run(_snap_args(app_, window_id_, interactive, bounds, max_depth, surface, root_q if window_id_ is window_id else None),
                   timeout_ms_=ms_)

    def complete_enough(d, app_, window_id_, ms_):
        if d.get("complete") is not False:
            return d
        bigger = min(max(ms_ * 2, ms_ + 15_000), MAX_TIMEOUT_MS)
        if bigger <= ms_:
            return d
        try:
            d2 = take(app_, window_id_, bigger)
            return d2 if d2.get("complete") is not False or (d2.get("ref_count") or 0) >= (d.get("ref_count") or 0) else d
        except FoxError:
            return d

    try:
        d = complete_enough(take(app, window_id, ms), app, window_id, ms)
        parts = [(None, d)]
    except FoxError as e:
        code = (e.details or {}).get("agent_desktop_code")
        if code == "APP_NOT_FOUND" and app and not window_id:
            app2, wid2 = resolve_app(app, None)
            if wid2:
                d = complete_enough(take(app2, wid2, ms), app2, wid2, ms)
                app, window_id = app2, wid2
                parts = [({"id": wid2, "app": app2, "title": app}, d)]
            else:
                raise
        elif code != "AMBIGUOUS_TARGET" or not app:
            raise
        else:
            try:
                wins = windows(app)
            except FoxError:
                wins = []
            main_like = [w for w in wins if app.lower() in (w.get("title") or "").lower() or (w.get("app") or "").lower() == app.lower()]
            dialogs = [w for w in wins if w not in main_like]
            parts = []
            for w in (dialogs + main_like or wins)[:4]:
                try:
                    dw = complete_enough(take(app, w["id"], ms), app, w["id"], ms)
                    parts.append((w, dw))
                except FoxError:
                    continue
            if not parts:
                raise
    nodes, refs, sid0 = [], {}, None
    for i, (w, d) in enumerate(parts):
        sid = d.get("snapshot_id")
        sid0 = sid0 or sid
        ns = flatten(d.get("tree") or {})
        for n in ns:
            if n.get("ref"):
                if i:
                    n["ref"] = f"w{i + 1}{n['ref']}"
                refs[n["ref"]] = n["qref"]
        if w is not None and ns:
            ns[0]["name"] = ns[0]["name"] or (w.get("title") or "")
        nodes += ns
    result = {"app": parts[0][1].get("app") or app, "snapshot_id": sid0, "ref_count": sum(d.get("ref_count") or 0 for _, d in parts),
              "complete": all(d.get("complete") is not False for _, d in parts), "windows": len(parts), "nodes": nodes,
              "snapshot": render(nodes)}
    _save_sid(ws, sid0, result["app"], window_id, refs, nodes)
    return result


def _act_once(ws, action: str, ref: str | None = None, value: str | None = None, **kw) -> dict:
    args = [action]
    stdin = None
    if ref:
        args.append(qualify(ws, ref))
    if action in ("type", "set-value"):
        args.append("--stdin")
        stdin = value or ""
    elif action == "select":
        args.append(str(value or ""))
    elif action == "scroll":
        args += ["--direction", kw.get("direction") or "down", "--amount", str(kw.get("amount") or 3)]
    elif action == "get":
        args += ["--property", kw.get("property") or "text"]
    return run(args, stdin=stdin)


def _remap_ref(ws, ref: str | None, prev_nodes: list[dict] | None = None) -> str | None:
    """新快照之后，把旧引用对到新的短引用：先按短 id，再按角色+名字+描述（唯一时）。"""
    if not ref:
        return ref
    short = str(ref).split(":")[-1].lstrip("@")
    st = last(ws)
    if short in (st.get("refs") or {}):
        return short
    prev = next((n for n in (prev_nodes or []) if n.get("ref") == short or n.get("qref") == ref), None)
    if not prev:
        return short
    nodes = st.get("nodes") or []
    keys = ("role", "name", "description")
    def same(n, ks):
        return all((n.get(k) or "") == (prev.get(k) or "") for k in ks)
    for ks in (("role", "name", "description", "value"), keys, ("role", "name")):
        hits = [n for n in nodes if n.get("ref") and same(n, ks)]
        if len(hits) == 1:
            return hits[0]["ref"]
    return short


def act(ws, action: str, ref: str | None = None, value: str | None = None, **kw) -> dict:
    """click | double-click | right-click | type | set-value | clear | focus | select | toggle | check | uncheck |
    expand | collapse | scroll | get。STALE_REF / AMBIGUOUS_TARGET（identity_not_unique，多半是快照没读完）时
    加大时限重拍快照、对上新引用再试一次。"""
    try:
        return _act_once(ws, action, ref, value, **kw)
    except FoxError as e:
        det = e.details or {}
        code = det.get("agent_desktop_code")
        retry = det.get("retry")
        kind = (det.get("details") or {}).get("kind") if isinstance(det.get("details"), dict) else None
        # 只在动作确定没落地时重试，避免点两次。identity_not_unique 是观察问题，重拍即可。
        if code not in {"STALE_REF", "AMBIGUOUS_TARGET"} or (retry and retry != "safe"):
            raise
        st = last(ws)
        prev_nodes = st.get("nodes") or []
        bigger = min(max(timeout_ms() * 2, timeout_ms() + 15_000), MAX_TIMEOUT_MS)
        try:
            snapshot(ws, app=st.get("app"), window_id=st.get("window_id"), interactive=False, timeout_ms_=bigger)
        except FoxError:
            raise e
        new_ref = _remap_ref(ws, ref, prev_nodes)
        return _act_once(ws, action, new_ref, value, **kw)


def press(combo: str, window_id: str | None = None, app: str | None = None) -> dict:
    """按键发给指定程序的进程（--app / --window-id），不依赖哪个窗口有焦点。"""
    args = ["press", combo]
    if window_id:
        args += ["--window-id", str(window_id)]
    elif app:
        args += ["--app", app]
    return run(args)


def windows(app: str | None = None) -> list[dict]:
    d = run(["list-windows", *(["--app", app] if app else [])])
    return d if isinstance(d, list) else (d.get("windows") or [])


def apps() -> list[dict]:
    return run(["list-apps"]).get("apps") or []


def focus_window(window_id: str | None = None, app: str | None = None, title: str | None = None) -> dict:
    args = ["focus-window"]
    for k, v in (("--window-id", window_id), ("--app", app), ("--title", title)):
        if v:
            args += [k, str(v)]
    return run(args)


def status() -> dict:
    if not available():
        return {"installed": False, "pin": PIN}
    try:
        d = run(["status"], timeout=20)
        return {"installed": True, "path": binary(), "version": d.get("version"), "platform": d.get("platform"),
                "accessibility": ((d.get("permissions") or {}).get("accessibility") or {}).get("state"), "pin": PIN}
    except FoxError as e:
        return {"installed": True, "path": binary(), "error": e.message, "pin": PIN}
