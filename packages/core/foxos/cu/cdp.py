"""Chrome DevTools Protocol 上的「浏览器操控」：无障碍快照 + 按 ref 操作（与 Playwright MCP 同一种做法，
不需要视觉模型）、文本提取、按键、下拉框、滚动、下载。

快照来自 Chrome 自己的无障碍树（Accessibility.getFullAXTree），每个元素给一个 ref（e1、e2…），
对应页面里的 backendDOMNodeId；按 ref 点击时先滚动到可见，再在元素中心发真实的鼠标事件（Input.dispatchMouseEvent），
输入用 Input.insertText（触发 input 事件，React / Vue 表单也能用）。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr

SKIP_ROLES = {"none", "generic", "InlineTextBox", "LineBreak", "presentation", "ignored", "LayoutTable", "LayoutTableRow",
              "LayoutTableCell", "group", "Section", "paragraph", "div", "strong", "emphasis", "Pre", "time", "mark", "subscript",
              "superscript", "code", "DescriptionListDetail", "DescriptionListTerm", "abbr", "Abbr", "ruby", "LabelText", "Canvas"}
KEEP_UNNAMED = {"textbox", "searchbox", "combobox", "checkbox", "radio", "button", "slider", "spinbutton", "switch", "listbox",
                "table", "list", "navigation", "main", "form", "dialog", "row", "img", "image", "separator", "tablist"}
PROPS = ("focused", "checked", "disabled", "expanded", "selected", "pressed", "required", "invalid", "level", "readonly", "modal")


def _browser():
    from ..apps import browser
    return browser


def connect(ctx, tab: str | None = None):
    b = _browser()
    b._require_cdp(ctx)
    p = b._page(ctx, tab)
    return p, b._WS(p["ws"], timeout=30)


def _refs_path(ctx) -> Path:
    return ctx.workspace.data_dir / "browser-refs.json"


def _save_refs(ctx, tab: str, refs: dict, url: str) -> None:
    try:
        d = json.loads(_refs_path(ctx).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    d[tab] = {"refs": refs, "url": url, "t": time.time()}
    if len(d) > 20:
        d = dict(sorted(d.items(), key=lambda kv: kv[1].get("t", 0))[-20:])
    tmp = _refs_path(ctx).with_suffix(".tmp")
    tmp.write_text(json.dumps(d), encoding="utf-8")
    os.replace(tmp, _refs_path(ctx))


def _ref_node(ctx, tab: str, ref: str) -> int:
    try:
        d = json.loads(_refs_path(ctx).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    r = (d.get(tab) or {}).get("refs", {}).get(ref)
    if r is None:
        raise FoxError("NOT_FOUND", tr("cu.no_browser_ref", ref), hint="foxos browser snapshot")
    return int(r)


def _val(x):
    return (x or {}).get("value") if isinstance(x, dict) else x


def _eval(ws, expr: str):
    r = ws.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    return (r.get("result") or {}).get("value")


def wait_ready(ws, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if _eval(ws, "document.readyState") == "complete":
                return
        except FoxError:
            pass
        time.sleep(0.2)


def snapshot(ctx, tab: str | None = None, max_chars: int = 40000, interactive_only: bool = False) -> dict:
    p, ws = connect(ctx, tab)
    try:
        wait_ready(ws, 10)
        nodes = ws.call("Accessibility.getFullAXTree").get("nodes") or []
        info = _eval(ws, "JSON.stringify({url: location.href, title: document.title})")
    finally:
        ws.close()
    meta = json.loads(info or "{}")
    by_id = {n["nodeId"]: n for n in nodes}
    children: dict = {}
    for n in nodes:
        for c in n.get("childIds") or []:
            children.setdefault(n["nodeId"], []).append(c)
    root = next((n for n in nodes if not n.get("parentId")), nodes[0] if nodes else None)
    lines: list[str] = []
    refs: dict = {}
    count = [0]
    size = [0]
    truncated = [False]

    def emit(line: str):
        if size[0] + len(line) > max_chars:
            truncated[0] = True
            return False
        lines.append(line)
        size[0] += len(line) + 1
        return True

    def rec(nid, depth, parent_name=""):
        if truncated[0]:
            return
        n = by_id.get(nid)
        if n is None:
            return
        role = _val(n.get("role")) or ""
        name = (_val(n.get("name")) or "").strip()
        printed = False
        if not n.get("ignored") and role not in ("RootWebArea", "WebArea"):
            if role == "StaticText":
                if name and name not in parent_name and not interactive_only and any(ch.isalnum() for ch in name):
                    emit("  " * depth + "- text: " + json.dumps(name[:300], ensure_ascii=False))
                return
            if role not in SKIP_ROLES and (name or role in KEEP_UNNAMED):
                interactive = role in KEEP_UNNAMED or role in ("link", "menuitem", "tab", "option", "treeitem", "menuitemcheckbox", "menuitemradio")
                if interactive_only and not interactive and role not in ("heading",):
                    pass
                else:
                    count[0] += 1
                    ref = f"e{count[0]}"
                    if n.get("backendDOMNodeId"):
                        refs[ref] = n["backendDOMNodeId"]
                    s = "  " * depth + f"- {role}"
                    if name:
                        s += " " + json.dumps(name[:200], ensure_ascii=False)
                    props = []
                    for pr in n.get("properties") or []:
                        if pr.get("name") in PROPS:
                            v = _val(pr.get("value"))
                            if v in (True, "true"):
                                props.append(pr["name"])
                            elif pr["name"] == "level" and v:
                                props.append(f"level={v}")
                            elif pr["name"] == "checked" and v == "mixed":
                                props.append("checked=mixed")
                    if props:
                        s += " [" + ", ".join(props) + "]"
                    s += f" [ref={ref}]"
                    v = _val(n.get("value"))
                    if v not in (None, "") and role in ("textbox", "searchbox", "combobox", "slider", "spinbutton", "listbox"):
                        s += ": " + json.dumps(str(v)[:200], ensure_ascii=False)
                    printed = emit(s)
        for c in children.get(nid, []):
            rec(c, depth + (1 if printed else 0), name if printed else parent_name)

    if root:
        rec(root["nodeId"], 0)
    _save_refs(ctx, p["id"], refs, meta.get("url") or p["url"])
    return {"tab": p["id"], "url": meta.get("url") or p["url"], "title": meta.get("title") or p.get("title"), "refs": len(refs),
            "truncated": truncated[0], "snapshot": "\n".join(lines)}


def _center(ws, backend_id: int) -> tuple[float, float]:
    try:
        ws.call("DOM.scrollIntoViewIfNeeded", {"backendNodeId": backend_id})
    except FoxError:
        pass
    q = ws.call("DOM.getContentQuads", {"backendNodeId": backend_id}).get("quads") or []
    if not q:
        raise FoxError("ERROR", tr("cu.not_visible"))
    pts = q[0]
    xs, ys = pts[0::2], pts[1::2]
    return sum(xs) / 4, sum(ys) / 4


def _mouse_click(ws, x: float, y: float, button: str = "left", count: int = 1) -> None:
    ws.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    for i in range(1, count + 1):
        ws.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": button, "clickCount": i})
        ws.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": button, "clickCount": i})


KEYS = {"Enter": (13, "\r"), "Tab": (9, "\t"), "Escape": (27, None), "Backspace": (8, None), "Delete": (46, None),
        "ArrowDown": (40, None), "ArrowUp": (38, None), "ArrowLeft": (37, None), "ArrowRight": (39, None),
        "PageDown": (34, None), "PageUp": (33, None), "Home": (36, None), "End": (35, None), "Space": (32, " ")}


def _press(ws, key: str) -> None:
    mods = 0
    parts = key.split("+")
    k = parts[-1]
    for m in parts[:-1]:
        mods |= {"alt": 1, "ctrl": 2, "control": 2, "meta": 4, "cmd": 4, "shift": 8}.get(m.lower(), 0)
    if k in KEYS:
        code, text = KEYS[k]
        name = " " if k == "Space" else k
    elif len(k) == 1:
        code, text, name = ord(k.upper()), k, k
    else:
        raise FoxError("USAGE", tr("cu.bad_key", key))
    base = {"key": name, "code": ("Key" + k.upper()) if len(k) == 1 and k.isalpha() else k, "windowsVirtualKeyCode": code,
            "nativeVirtualKeyCode": code, "modifiers": mods}
    ws.call("Input.dispatchKeyEvent", {**base, "type": "keyDown" if (text and not mods) else "rawKeyDown", **({"text": text} if text and not mods else {})})
    ws.call("Input.dispatchKeyEvent", {**base, "type": "keyUp"})


def _after_action(ws, settle: float = 0.6) -> dict:
    time.sleep(settle)
    wait_ready(ws, 15)
    try:
        info = json.loads(_eval(ws, "JSON.stringify({url: location.href, title: document.title})") or "{}")
    except (FoxError, ValueError):
        info = {}
    return info


def click(ctx, ref: str, tab: str | None = None, button: str = "left", double: bool = False) -> dict:
    p, ws = connect(ctx, tab)
    try:
        bid = _ref_node(ctx, p["id"], ref)
        x, y = _center(ws, bid)
        _mouse_click(ws, x, y, button, 2 if double else 1)
        info = _after_action(ws)
    finally:
        ws.close()
    return {"message": tr("cu.browser_clicked", ref), "ref": ref, "x": round(x), "y": round(y), "tab": p["id"], **info}


def type_text(ctx, ref: str, text: str, tab: str | None = None, submit: bool = False, clear: bool = True) -> dict:
    p, ws = connect(ctx, tab)
    try:
        bid = _ref_node(ctx, p["id"], ref)
        try:
            ws.call("DOM.scrollIntoViewIfNeeded", {"backendNodeId": bid})
        except FoxError:
            pass
        ws.call("DOM.focus", {"backendNodeId": bid})
        if clear:
            obj = ws.call("DOM.resolveNode", {"backendNodeId": bid}).get("object", {}).get("objectId")
            if obj:
                ws.call("Runtime.callFunctionOn", {"objectId": obj, "functionDeclaration":
                        "function(){ if (typeof this.select === 'function') { this.select(); } else if (this.isContentEditable) { document.execCommand('selectAll'); } }"})
        if text:
            ws.call("Input.insertText", {"text": text})
        if submit:
            _press(ws, "Enter")
        info = _after_action(ws, 0.8 if submit else 0.2)
    finally:
        ws.close()
    return {"message": tr("cu.browser_typed", ref, len(text)), "ref": ref, "submitted": submit, "tab": p["id"], **info}


def press(ctx, key: str, tab: str | None = None) -> dict:
    p, ws = connect(ctx, tab)
    try:
        _press(ws, key)
        info = _after_action(ws, 0.4)
    finally:
        ws.close()
    return {"message": tr("cu.browser_pressed", key), "key": key, "tab": p["id"], **info}


def select_option(ctx, ref: str, value: str, tab: str | None = None) -> dict:
    p, ws = connect(ctx, tab)
    try:
        bid = _ref_node(ctx, p["id"], ref)
        obj = ws.call("DOM.resolveNode", {"backendNodeId": bid}).get("object", {}).get("objectId")
        r = ws.call("Runtime.callFunctionOn", {"objectId": obj, "returnByValue": True, "arguments": [{"value": value}], "functionDeclaration": """
            function(v){ if (this.tagName !== 'SELECT') return {ok:false, error:'not a <select>'};
              const o = Array.from(this.options).find(o => o.value === v || o.label.trim() === v || o.text.trim() === v);
              if (!o) return {ok:false, error:'no option ' + v, options: Array.from(this.options).map(o => o.text.trim())};
              this.value = o.value; this.dispatchEvent(new Event('input', {bubbles:true})); this.dispatchEvent(new Event('change', {bubbles:true}));
              return {ok:true, value:o.value, text:o.text.trim()}; }"""})
        val = (r.get("result") or {}).get("value") or {}
        info = _after_action(ws, 0.3)
    finally:
        ws.close()
    if not val.get("ok"):
        raise FoxError("NOT_FOUND", val.get("error") or "select failed", details={"options": val.get("options")})
    return {"message": tr("cu.browser_selected", ref, val.get("text")), "ref": ref, **val, "tab": p["id"], **info}


def scroll(ctx, direction: str = "down", amount: int = 600, tab: str | None = None) -> dict:
    dy = {"down": amount, "up": -amount}.get(direction, 0)
    dx = {"right": amount, "left": -amount}.get(direction, 0)
    p, ws = connect(ctx, tab)
    try:
        _eval(ws, f"window.scrollBy({dx}, {dy})")
        pos = _eval(ws, "JSON.stringify([scrollX, scrollY, document.documentElement.scrollHeight, innerHeight])")
    finally:
        ws.close()
    x, y, h, vh = json.loads(pos or "[0,0,0,0]")
    return {"tab": p["id"], "scroll": [x, y], "page_height": h, "viewport_height": vh, "at_bottom": y + vh >= h - 2}


def history(ctx, step: int, tab: str | None = None) -> dict:
    p, ws = connect(ctx, tab)
    try:
        _eval(ws, f"history.go({int(step)})")
        info = _after_action(ws, 0.8)
    finally:
        ws.close()
    return {"tab": p["id"], **info}


def page_text(ctx, tab: str | None = None, ref: str | None = None, max_chars: int = 30000) -> dict:
    p, ws = connect(ctx, tab)
    try:
        wait_ready(ws, 10)
        if ref:
            bid = _ref_node(ctx, p["id"], ref)
            obj = ws.call("DOM.resolveNode", {"backendNodeId": bid}).get("object", {}).get("objectId")
            r = ws.call("Runtime.callFunctionOn", {"objectId": obj, "returnByValue": True,
                                                   "functionDeclaration": "function(){ return this.innerText || this.value || this.textContent || ''; }"})
            text = (r.get("result") or {}).get("value") or ""
        else:
            text = _eval(ws, "document.body ? document.body.innerText : ''") or ""
        info = json.loads(_eval(ws, "JSON.stringify({url: location.href, title: document.title})") or "{}")
    finally:
        ws.close()
    trunc = len(text) > max_chars
    return {"tab": p["id"], **info, "text": text[:max_chars], "truncated": trunc, "chars": len(text)}


def wait_for(ctx, text: str | None = None, seconds: float = 0, tab: str | None = None, timeout: float = 20) -> dict:
    if seconds and not text:
        time.sleep(min(float(seconds), 60))
        return {"waited": seconds}
    p, ws = connect(ctx, tab)
    try:
        deadline = time.time() + float(timeout)
        while time.time() < deadline:
            body = _eval(ws, "document.body ? document.body.innerText : ''") or ""
            if text and text in body:
                return {"found": True, "text": text, "tab": p["id"]}
            time.sleep(0.4)
    finally:
        ws.close()
    raise FoxError("NOT_FOUND", tr("cu.text_not_found", text, timeout))


# ------------------------------------------------------------------ 下载

def downloads_dir(ctx) -> Path:
    d = ctx.workspace.root / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def download(ctx, url: str | None = None, ref: str | None = None, tab: str | None = None, timeout: float = 120) -> dict:
    """在浏览器里真实下载（点击链接或打开地址），存到工作空间 downloads/。"""
    b = _browser()
    b._require_cdp(ctx)
    ver = b._cdp_version(ctx) or {}
    bws = b._WS(ver["webSocketDebuggerUrl"], timeout=timeout)
    dest = downloads_dir(ctx)
    try:
        bws.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(dest), "eventsEnabled": True})
        if ref:
            click(ctx, ref, tab=tab)
        elif url:
            p, ws = connect(ctx, tab)
            try:
                ws.call("Page.navigate", {"url": url})
            finally:
                ws.close()
        else:
            raise FoxError("USAGE", tr("cu.download_needs"))
        name = None
        guid = None
        deadline = time.time() + float(timeout)
        while time.time() < deadline:
            m = bws.recv()
            meth = m.get("method")
            prm = m.get("params") or {}
            if meth == "Browser.downloadWillBegin":
                name, guid = prm.get("suggestedFilename"), prm.get("guid")
            elif meth == "Browser.downloadProgress" and (guid is None or prm.get("guid") == guid):
                if prm.get("state") == "completed":
                    f = dest / (name or "")
                    return {"message": tr("cu.downloaded", ctx.rel(f)), "path": ctx.rel(f), "bytes": f.stat().st_size if f.exists() else prm.get("receivedBytes"),
                            "url": url}
                if prm.get("state") == "canceled":
                    raise FoxError("ERROR", tr("cu.download_canceled"))
        raise FoxError("ERROR", tr("cu.download_timeout", timeout))
    finally:
        try:
            bws.call("Browser.setDownloadBehavior", {"behavior": "default"})
        except FoxError:
            pass
        bws.close()


def list_downloads(ctx) -> dict:
    d = downloads_dir(ctx)
    files = [{"path": ctx.rel(f), "bytes": f.stat().st_size, "mtime": f.stat().st_mtime} for f in sorted(d.iterdir()) if f.is_file()
             and not f.name.endswith(".crdownload")]
    return {"dir": ctx.rel(d), "count": len(files), "files": files}
