#!/usr/bin/env python3
"""生成 Everything 应用的操作清单：packages/core/foxos/data/ops/<app>.json 与 docs/operations/<app>.md。

做法（都基于真实运行的应用，不靠手写）：
1. 运行时遍历：用无界面实例打开应用，读取可访问性快照；依次点击导航类控件（tab / 链接 / 导航栏按钮），
   记录每个视图里新出现的控件。每次点击前重置应用（关闭实例并清空其 AppData），保证从同一初始状态出发。
2. 静态挖掘：扫描上游源码里的键盘快捷键（ctrl/meta + 键）。
3. 归一化：控件名称 → <资源> <动词>，动词取自固定词表；每个操作带 UI 路径、参数、效果、是否可撤销、绑定步骤。

用法：python scripts/inventory_ops.py [app ...] [--src /path/to/everything]
需要：应用已安装（foxos everything install），可用的显示（xvfb），桌面可自动以 --headless 启动。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "core"))

from foxos import desktop_client  # noqa: E402
from foxos.errors import FoxError  # noqa: E402
from foxos.workspace import Workspace  # noqa: E402

CATALOG = json.loads((ROOT / "packages/core/foxos/data/everything.json").read_text(encoding="utf-8"))
OPS_DIR = ROOT / "packages/core/foxos/data/ops"
DOC_DIR = ROOT / "docs/operations"

# 名称首词 → 归一化动词
VERBS = {
    "add": "create", "new": "create", "create": "create", "insert": "create", "compose": "create", "start new": "create",
    "delete": "delete", "remove": "delete", "trash": "delete", "discard": "delete",
    "edit": "update", "update": "update", "change": "update", "modify": "update",
    "rename": "rename", "duplicate": "duplicate", "copy": "copy", "paste": "paste", "cut": "cut",
    "save": "save", "export": "export", "download": "export", "import": "import", "upload": "import", "load": "import",
    "open": "open", "close": "close", "undo": "undo", "redo": "redo", "search": "search", "find": "search", "filter": "filter",
    "sort": "sort", "print": "print", "share": "share", "send": "send", "reply": "reply", "invite": "invite",
    "start": "start", "stop": "stop", "play": "play", "pause": "pause", "record": "record", "resume": "resume",
    "reset": "reset", "clear": "clear", "restart": "reset", "next": "next", "previous": "previous", "prev": "previous", "back": "previous",
    "forward": "next", "zoom": "zoom", "cancel": "cancel", "ok": "confirm", "done": "confirm", "apply": "confirm", "confirm": "confirm",
    "submit": "confirm", "skip": "dismiss", "dismiss": "dismiss", "got": "dismiss", "show": "show", "view": "show", "hide": "hide",
    "toggle": "toggle", "select": "select", "choose": "select", "pick": "select", "move": "move", "archive": "archive", "complete": "complete",
    "mark": "mark", "assign": "assign", "schedule": "schedule", "connect": "connect", "join": "join", "leave": "leave", "sign": "sign",
    "settings": "show", "help": "show", "about": "show", "menu": "show", "more": "show", "expand": "expand", "collapse": "collapse",
    "run": "run", "send to": "send", "generate": "run", "calculate": "run", "check": "run", "test": "run", "draw": "draw",
    "rotate": "rotate", "flip": "flip", "crop": "crop", "resize": "resize", "align": "align", "group": "group", "ungroup": "ungroup",
    "lock": "lock", "unlock": "unlock", "bold": "format", "italic": "format", "underline": "format", "strikethrough": "format",
}
READ_VERBS = {"show", "hide", "search", "filter", "sort", "next", "previous", "zoom", "select", "expand", "collapse", "open", "close", "cancel", "dismiss", "print"}
NAV_ROLES = {"tab", "link"}
NAV_REGIONS = {"nav", "aside", "header", "navigation", "tablist", "toolbar"}
DANGER = re.compile(r"delete|remove|reset|clear|trash|sign out|log ?out|discard|erase|wipe|format|uninstall|close", re.I)
STOP = {"a", "an", "the", "to", "for", "of", "new", "your", "this", "my", "and", "in", "on", "with", "all"}


def slug(words: list[str]) -> str:
    s = "-".join(w for w in words if w and w not in STOP)
    s = re.sub(r"[^a-z0-9-]+", "", s)
    return re.sub(r"-{2,}", "-", s)[:40].strip("-")


def normalize(name: str, role: str) -> tuple[str, str] | None:
    """控件名称 → (资源, 动词)。无法得到稳定英文名称时返回 None。"""
    n = re.sub(r"[^\w\s+-]", " ", name.lower()).strip()
    n = re.sub(r"\s+", " ", n)
    if not n or len(n) > 48 or not re.search(r"[a-z]", n) or re.fullmatch(r"[\d\s:./-]+", n):
        return None
    words = n.split()
    if role in ("textbox", "combobox", "slider", "spinbutton", "searchbox"):
        return slug(words) or "input", "set"
    if role in ("checkbox", "switch", "radio"):
        return slug(words) or "option", "toggle"
    if role in NAV_ROLES and words[0] not in VERBS:
        return slug(words) or "view", "show"
    two = " ".join(words[:2])
    if two in VERBS:
        return slug(words[2:]) or slug(words[:1]), VERBS[two]
    if words[0] in VERBS:
        verb = VERBS[words[0]]
        res = slug(words[1:]) or slug(words)
        if words[0] in ("zoom",) and len(words) > 1:
            return "view", f"zoom-{slug(words[1:2])}"
        return res, verb
    return slug(words), "activate"


def bridge(ws: Workspace, app: str, method: str, args: dict | None = None, timeout: float = 60):
    return desktop_client.call(ws, "ev.bridge", app, {"method": method, "args": args or {}}, agent="inventory", timeout=timeout)


def reset(ws: Workspace, app: str) -> dict:
    desktop_client.call(ws, "ev.reset", app, agent="inventory")
    desktop_client.call(ws, "ev.open", app, {"window": False}, agent="inventory", timeout=90)
    time.sleep(1.5)
    return bridge(ws, app, "snapshot", {"limit": 600})


MENUISH = re.compile(r"\b(more|menu|options|actions|settings|preferences|tools|insert|format|view|file|edit)\b", re.I)


def is_nav(e: dict) -> bool:
    if not e.get("name") or e.get("disabled") or DANGER.search(e["name"]) or re.search(r"\d", e["name"]):
        return False
    if e["role"] in NAV_ROLES or (e["role"] == "button" and (e.get("region") or "") in NAV_REGIONS):
        return True
    return e["role"] == "button" and (bool(e.get("haspopup")) or bool(MENUISH.search(e["name"]) and len(e["name"]) < 30))


def walk(ws: Workspace, app: str, max_nav: int = 14) -> tuple[list[dict], str]:
    snap = reset(ws, app)
    found: list[dict] = []
    seen: set[tuple] = set()

    def take(elements, path):
        for e in elements:
            key = (e["role"], e.get("name"), e.get("region"))
            if key in seen or not e.get("name"):
                continue
            seen.add(key)
            found.append({**e, "path": list(path)})

    take(snap["elements"], [])
    navs = [e for e in snap["elements"] if is_nav(e)][:max_nav]
    for nav in navs:
        try:
            s0 = reset(ws, app)
            bridge(ws, app, "click", {"name": nav["name"], "role": nav["role"]})
            time.sleep(0.7)
            s1 = bridge(ws, app, "snapshot", {"limit": 600})
            take(s1["elements"], [{"name": nav["name"], "role": nav["role"]}])
        except FoxError as e:
            print(f"  [{app}] 导航 {nav['name']!r} 失败：{e}", file=sys.stderr)
    return found, snap.get("title") or app


SHORTCUT_RE = [
    re.compile(r"""(?:ctrlKey|metaKey|mod)[^;\n]{0,80}?\.key(?:\.toLowerCase\(\))?\s*===?\s*['"]([a-zA-Z0-9])['"]"""),
    re.compile(r"""\.key(?:\.toLowerCase\(\))?\s*===?\s*['"]([a-zA-Z0-9])['"][^;\n]{0,80}?(?:ctrlKey|metaKey)"""),
]
SHORTCUT_NAMES = {"z": ("edit", "undo"), "y": ("edit", "redo"), "s": ("document", "save"), "o": ("document", "open"), "n": ("document", "create"),
                  "c": ("selection", "copy"), "v": ("clipboard", "paste"), "x": ("selection", "cut"), "a": ("selection", "select-all"),
                  "f": ("document", "search"), "p": ("document", "print"), "b": ("text", "format-bold"), "i": ("text", "format-italic"),
                  "u": ("text", "format-underline"), "d": ("selection", "duplicate"), "g": ("selection", "group"), "k": ("command-palette", "show"),
                  "e": ("document", "export"), "l": ("selection", "lock"), "h": ("view", "toggle-help")}


def shortcuts(src: Path, app: str) -> list[dict]:
    root = src / "src" / app / "src"
    keys: dict[str, str] = {}
    if not root.exists():
        return []
    for f in root.rglob("*"):
        if f.suffix not in (".js", ".ts", ".jsx", ".tsx", ".svelte", ".vue") or "node_modules" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for rx in SHORTCUT_RE:
            for m in rx.finditer(text):
                k = m.group(1).lower()
                ctx = text[max(0, m.start() - 60):m.end() + 60]
                shift = "shiftKey" in ctx and "!e.shiftKey" not in ctx and "!event.shiftKey" not in ctx
                combo = f"mod+shift+{k}" if shift else f"mod+{k}"
                keys.setdefault(combo, str(f.relative_to(src / "src" / app)))
    out = []
    for combo, where in sorted(keys.items()):
        k = combo.split("+")[-1]
        res, verb = SHORTCUT_NAMES.get(k, ("shortcut", f"key-{k}"))
        if "shift" in combo:
            if k == "z":
                res, verb = "edit", "redo"
            else:
                verb = f"{verb}-shift"
        out.append({"combo": combo, "resource": res, "verb": verb, "source": where})
    return out


def pattern_of(name: str) -> str:
    # 数据项的名称（日期、棋盘格、列表名）归为同一模式："Open list: Work" → "open list: *"，"a1, White rook" → "#"
    n = name.lower()
    m = re.match(r"^(.{3,40}?)(:|\bfor\b)\s+.+$", n)
    if m:
        return f"{m.group(1)}{m.group(2)} *"
    n = re.sub(r"\b(mon|tue|wed|thu|fri|sat|sun)(day|sday|nesday|rsday|urday)?\b", "#", n)
    n = re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b", "#", n)
    n = re.sub(r"[a-z]*\d[\w./:-]*", "#", n)
    return re.sub(r"#(\W*#)+", "#", n)


def collapse(controls: list[dict]) -> tuple[list[dict], list[dict]]:
    """把重复出现的数据项控件合并成带 target 参数的一个操作。"""
    groups: dict[tuple, list[dict]] = {}
    for c in controls:
        key = (tuple(p["name"] for p in c["path"]), c.get("region"), c["role"], pattern_of(c["name"]))
        groups.setdefault(key, []).append(c)
    singles, items = [], []
    for key, cs in groups.items():
        pat = key[3]
        if len(cs) >= 3 or (("#" in pat or "*" in pat) and pat not in ("#",) or re.search(r"\d", cs[0]["name"])):
            items.append({**cs[0], "pattern": pat, "examples": [c["name"] for c in cs[:5]], "count": len(cs)})
        else:
            singles.extend(cs)
    return singles, items


def build_ops(app: str, controls: list[dict], keys: list[dict]) -> list[dict]:
    ops: list[dict] = []
    ids: set[str] = set()
    has_undo = any(k["verb"] == "undo" for k in keys) or any(re.fullmatch(r"undo", (c.get("name") or "").lower()) for c in controls)
    undo_txt = "可能（应用提供撤销，未逐项验证）" if has_undo else "否（应用没有撤销入口）"

    def add(op, view_slug=""):
        if op["id"] in ids and view_slug and not op["resource"].startswith(view_slug):
            op["resource"] = f"{view_slug}-{op['resource']}"[:48]
            op["id"] = f"{op['resource']}.{op['verb']}"
        base_res = op["resource"]
        i = 2
        while op["id"] in ids:
            op["resource"] = f"{base_res}-{i}"
            op["id"] = f"{op['resource']}.{op['verb']}"
            i += 1
        ids.add(op["id"])
        ops.append(op)

    controls, items = collapse(controls)
    for it in items:
        nav_steps = [{"click": {"name": p["name"], "role": p["role"]}} for p in it["path"]] + ([{"wait": 400}] if it["path"] else [])
        view = " > ".join(p["name"] for p in it["path"]) or "主界面"
        words = re.sub(r"[#*:,]", " ", it["pattern"]).split()
        nr = normalize(" ".join(words), "button") if words else None
        res, verb = nr if nr and nr[0] else (slug((it.get("region") or "item").lower().split()) or "item", "select")
        if verb == "activate":
            verb = "select"
        add({"id": f"{res}.{verb}", "resource": res, "verb": verb, "summary": f"{it['pattern']}（{it['count']} 项，如 {it['examples'][0]}）", "source": "ui-collection",
             "ui": {"path": f"{view} > {it.get('region') + ' > ' if it.get('region') else ''}{it['pattern']}", "role": it["role"], "region": it.get("region"), "view": view, "examples": it["examples"]},
             "params": [{"name": "target", "type": "string", "description": f"要操作的项的名称（或其一部分），如 {it['examples'][0]!r}", "required": True, "positional": True}],
             "effect": f"点击名称匹配的「{it['pattern']}」项（{it['role']}）", "permission": "read" if verb in READ_VERBS else "modify",
             "undoable": undo_txt if verb not in READ_VERBS else "不适用（只读）",
             "binding": {"kind": "ui", "open": True, "steps": nav_steps + [{"click": {"name": "{{target}}", "role": it["role"]}}]}},
            slug(view.lower().split()) if it["path"] else "")

    for c in controls:
        nr = normalize(c["name"], c["role"])
        if not nr:
            continue
        res, verb = nr
        if not res:
            continue
        nav_steps = [{"click": {"name": p["name"], "role": p["role"]}} for p in c["path"]] + ([{"wait": 400}] if c["path"] else [])
        view = " > ".join(p["name"] for p in c["path"]) or "主界面"
        where = f"{view} > {c.get('region') + ' > ' if c.get('region') else ''}{c['name']}"
        perm = "read" if verb in READ_VERBS else "delete" if verb == "delete" else "modify"
        params = []
        if verb == "set":
            params = [{"name": "value", "type": "string", "description": f"「{c['name']}」的新值", "required": True, "positional": True}]
            act = {"set": {"name": c["name"], "role": c["role"], "value": "{{value}}"}}
            effect = f"把「{c['name']}」设为给定值（触发 input / change 事件）"
            params.append({"name": "submit", "type": "boolean", "description": "设置后按 Enter 提交", "default": False})
            if c.get("options"):
                params[0]["enum"] = c["options"]
        elif verb == "toggle":
            act = {"click": {"name": c["name"], "role": c["role"]}}
            effect = f"切换「{c['name']}」"
        else:
            act = {"click": {"name": c["name"], "role": c["role"]}}
            effect = f"点击「{c['name']}」（{c['role']}）" + (f"，切换到该视图" if verb == "show" else "")
        steps = nav_steps + [act]
        if verb == "set":
            steps.append({"press_if": "submit", "press": {"key": "Enter", "name": c["name"], "role": c["role"]}})
        add({"id": f"{res}.{verb}", "resource": res, "verb": verb, "summary": f"{c['name']}", "source": "ui",
             "ui": {"path": where, "role": c["role"], "name": c["name"], "region": c.get("region"), "view": view},
             "params": params, "effect": effect, "permission": perm,
             "undoable": undo_txt if perm != "read" else "不适用（只读）",
             "binding": {"kind": "ui", "open": True, "steps": steps}}, slug(view.lower().split()) if c["path"] else "")
    for k in keys:
        add({"id": f"{k['resource']}.{k['verb']}", "resource": k["resource"], "verb": k["verb"], "summary": f"快捷键 {k['combo']}", "source": "shortcut",
             "ui": {"path": f"键盘 {k['combo']}", "shortcut": k["combo"], "defined_in": k["source"]}, "params": [],
             "effect": f"在当前焦点上按 {k['combo']}（{k['source']} 中定义）", "permission": "read" if k["verb"] in READ_VERBS else "modify",
             "undoable": undo_txt if k["verb"] not in ("undo", "redo") and k["verb"] not in READ_VERBS else "不适用",
             "binding": {"kind": "ui", "open": True, "steps": [{"press": {"key": k["combo"]}}]}})
    return ops


def write_docs(app: str, meta: dict, ops: list[dict], title: str) -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# {meta['name']}（{app}）操作清单", "",
             f"分组：{meta['group']} · 替代 {meta['alternativeTo']} · 许可证 {meta['license']} · 页面标题「{title}」", "",
             f"共 {len(ops)} 个操作，全部有语义命令（`foxos {app} <资源> <动词>`，MCP 工具 `{app}.<资源>.<动词>`）。"
             "绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。", "",
             "由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。", "",
             "| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |", "|---|---|---|---|---|---|"]
    for o in ops:
        ps = ", ".join(f"`{p['name']}`" + ("（必填）" if p.get("required") else "") for p in o["params"]) or "—"
        path = (o["ui"].get("path") or "").replace("|", "\\|")
        lines.append(f"| `{o['id']}` | `foxos {app} {o['resource']} {o['verb']}` | {path} | {ps} | {o['effect'].replace('|', '/')} | {o['undoable']} |")
    (DOC_DIR / f"{app}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--src", default=os.environ.get("FOXOS_EVERYTHING_SOURCE", "/workspace/everything"))
    ap.add_argument("--max-nav", type=int, default=14)
    a = ap.parse_args()
    apps = a.apps or [x["id"] for x in CATALOG["apps"]]
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="foxos-inventory-"))
    ws = Workspace(tmp)
    summary = {}
    for app in apps:
        meta = next(x for x in CATALOG["apps"] if x["id"] == app)
        home = Path(os.environ.get("FOXOS_HOME", "")) if os.environ.get("FOXOS_HOME") else None
        from foxos.apps.everything import installed
        if not installed(app):
            print(f"[{app}] 未安装，跳过", file=sys.stderr)
            summary[app] = None
            continue
        t0 = time.time()
        try:
            controls, title = walk(ws, app, a.max_nav)
        except FoxError as e:
            print(f"[{app}] 失败：{e}", file=sys.stderr)
            summary[app] = None
            continue
        finally:
            try:
                desktop_client.call(ws, "ev.close", app, agent="inventory")
            except FoxError:
                pass
        keys = shortcuts(Path(a.src), app)
        ops = build_ops(app, controls, keys)
        doc = {"app": app, "name": meta["name"], "generated_by": "scripts/inventory_ops.py", "commit": CATALOG["commit"], "title": title, "ops": ops}
        (OPS_DIR / f"{app}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        write_docs(app, meta, ops, title)
        summary[app] = len(ops)
        print(f"[{app}] {len(ops)} 个操作（{len(controls)} 个控件，{len(keys)} 个快捷键），{time.time() - t0:.0f}s", flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
