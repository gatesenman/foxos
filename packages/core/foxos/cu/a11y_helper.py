"""AT-SPI 助手：在带 PyGObject（gi）的系统 Python 里运行，读写桌面程序的无障碍树。

foxos 内核可能跑在没有 gi 的虚拟环境里，所以单独起进程：stdin 收一个 JSON 请求，stdout 回一个 JSON。
请求：{"op": "tree"|"find"|"act"|"apps", ...}

节点引用（path ref）：「<pid>:<i.j.k>」——进程号加从应用根往下的子节点序号。
"""

from __future__ import annotations

import json
import re
import sys
import time

import warnings

import gi

warnings.filterwarnings("ignore", category=DeprecationWarning)

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi  # noqa: E402

S = Atspi.StateType
INTERACTIVE = {"push button", "toggle button", "check box", "radio button", "menu item", "check menu item", "radio menu item",
               "menu", "combo box", "text", "entry", "password text", "spin button", "slider", "link", "page tab", "list item",
               "table cell", "tree item", "icon", "terminal", "document web", "document text", "editbar", "tool bar",
               "button", "toggle", "menu bar", "scroll bar", "tab", "list box", "option", "search box"}
SKIP_UNNAMED = {"filler", "panel", "section", "unknown", "redundant object", "layered pane", "viewport", "scroll pane",
                "split pane", "grouping", "invalid", "root pane", "glass pane", "option pane", "internal frame", "block quote", "paragraph"}


def _safe(f, default=None):
    try:
        return f()
    except Exception:  # noqa: BLE001 — 单个节点出错不影响整棵树
        return default


def apps() -> list:
    d = Atspi.get_desktop(0)
    out = []
    for i in range(_safe(d.get_child_count, 0)):
        a = _safe(lambda: d.get_child_at_index(i))
        if a is None:
            continue
        out.append(a)
    return out


def app_info(a) -> dict:
    pid = _safe(a.get_process_id, 0)
    frames = []
    active = False
    for j in range(min(_safe(a.get_child_count, 0), 30)):
        w = _safe(lambda: a.get_child_at_index(j))
        if w is None:
            continue
        st = _safe(w.get_state_set)
        showing = bool(st and st.contains(S.SHOWING))
        act = bool(st and st.contains(S.ACTIVE))
        active = active or act
        frames.append({"name": _safe(w.get_name, ""), "role": _safe(w.get_role_name, ""), "showing": showing, "active": act})
    return {"app": _safe(a.get_name, ""), "pid": pid, "windows": frames, "active": active}


def states(node) -> list:
    st = _safe(node.get_state_set)
    if not st:
        return []
    out = []
    for name, s in (("focused", S.FOCUSED), ("checked", S.CHECKED), ("selected", S.SELECTED), ("expanded", S.EXPANDED),
                    ("editable", S.EDITABLE), ("active", S.ACTIVE)):
        if st.contains(s):
            out.append(name)
    if not st.contains(S.SENSITIVE) and not st.contains(S.ENABLED):
        out.append("disabled")
    return out


def bbox(node):
    c = _safe(node.get_component_iface)
    if c is None:
        return None
    e = _safe(lambda: c.get_extents(Atspi.CoordType.SCREEN))
    if e is None or e.width <= 0 or e.height <= 0:
        return None
    return [e.x, e.y, e.width, e.height]


def actions(node) -> list:
    a = _safe(node.get_action_iface)
    if a is None:
        return []
    return [_safe(lambda: Atspi.Action.get_action_name(node, i), "") for i in range(_safe(lambda: Atspi.Action.get_n_actions(node), 0))]


def text_of(node, limit=400):
    if _safe(node.get_text_iface) is None:
        return None
    n = _safe(lambda: Atspi.Text.get_character_count(node), 0)
    s = _safe(lambda: Atspi.Text.get_text(node, 0, min(n, limit)), "")
    return s + ("…" if n > limit else "")


def value_of(node):
    v = _safe(node.get_value_iface)
    if v is None:
        return None
    return _safe(v.get_current_value)


def find_app(pid=None, name=None):
    for a in apps():
        if pid and _safe(a.get_process_id) == int(pid):
            return a
        if name and (_safe(a.get_name, "") or "").lower() == name.lower():
            return a
    if name:
        for a in apps():
            if name.lower() in (_safe(a.get_name, "") or "").lower():
                return a
    return None


def resolve(ref: str):
    pid, _, path = ref.partition(":")
    a = find_app(pid=int(pid))
    if a is None:
        raise LookupError(f"no application with pid {pid}")
    n = a
    for idx in [int(x) for x in path.split(".") if x != ""]:
        n = n.get_child_at_index(idx)
        if n is None:
            raise LookupError(f"element {ref} is gone")
    return n


def walk(app, max_depth=40, max_nodes=600, showing_only=True, text_limit=200):
    pid = _safe(app.get_process_id, 0)
    out = []

    def rec(node, path, depth, printed_depth):
        if len(out) >= max_nodes or depth > max_depth:
            return
        role = _safe(node.get_role_name, "") or ""
        st = _safe(node.get_state_set)
        if depth > 0 and showing_only and st is not None and not st.contains(S.SHOWING) and role not in ("menu item",):
            return
        if depth > 0 and showing_only and role == "menu item" and st is not None and not st.contains(S.SHOWING):
            return
        name = (_safe(node.get_name, "") or "").strip()
        keep = depth <= 1 or bool(name) or role in INTERACTIVE or (role not in SKIP_UNNAMED and role)
        if role in SKIP_UNNAMED and not name:
            keep = False
        nd = printed_depth
        if keep:
            item = {"ref": f"{pid}:{'.'.join(map(str, path))}", "role": role, "name": name, "depth": printed_depth}
            stt = states(node)
            if stt:
                item["states"] = stt
            acts = actions(node)
            if acts:
                item["actions"] = acts
            if role in ("text", "entry", "password text", "terminal", "spin button", "document text", "search box", "label", "static", "heading"):
                tx = text_of(node, text_limit) if role != "password text" else None
                if tx and tx != name:
                    item["text"] = tx
            v = value_of(node)
            if v is not None:
                item["value"] = v
            b = bbox(node)
            if b:
                item["bbox"] = b
            out.append(item)
            nd = printed_depth + 1
        for j in range(min(_safe(node.get_child_count, 0), 400)):
            ch = _safe(lambda: node.get_child_at_index(j))
            if ch is not None:
                rec(ch, path + [j], depth + 1, nd)

    rec(app, [], 0, 0)
    return out, len(out) >= max_nodes


def pick_apps(req):
    if req.get("pid") or req.get("app"):
        a = find_app(pid=req.get("pid"), name=req.get("app"))
        if a is None:
            raise LookupError(f"no accessible application {req.get('app') or req.get('pid')}")
        return [a]
    all_ = apps()
    if req.get("all"):
        return all_
    act = [a for a in all_ if app_info(a)["active"]]
    return act or [a for a in all_ if any(w["showing"] for w in app_info(a)["windows"])][-1:]


def op_tree(req):
    res = []
    trunc = False
    for a in pick_apps(req):
        nodes, t = walk(a, req.get("depth", 40), req.get("max_nodes", 600), not req.get("hidden"), req.get("text_limit", 200))
        trunc = trunc or t
        res.append({**app_info(a), "nodes": nodes})
    return {"apps": res, "truncated": trunc}


def op_find(req):
    role = (req.get("role") or "").lower()
    name = req.get("name")
    rx = re.compile(name, re.I) if req.get("regex") and name else None
    out = []
    for a in pick_apps({**req, "all": not (req.get("pid") or req.get("app"))}):
        nodes, _ = walk(a, 40, req.get("max_nodes", 3000), not req.get("hidden"), 400)
        for n in nodes:
            if role and role not in n["role"].lower():
                continue
            if name:
                hay = (n.get("name") or "") + " " + (n.get("text") or "")
                if rx and not rx.search(hay):
                    continue
                if not rx and name.lower() not in hay.lower():
                    continue
            out.append({**n, "app": _safe(a.get_name, "")})
            if len(out) >= req.get("limit", 20):
                return {"matches": out}
    return {"matches": out}


def _do_action(node, prefer):
    a = _safe(node.get_action_iface)
    if a is None:
        return None
    names = actions(node)
    for want in prefer:
        for i, n in enumerate(names):
            if n == want:
                if Atspi.Action.do_action(node, i):
                    return n
    return None


def op_act(req):
    node = resolve(req["ref"])
    role = _safe(node.get_role_name, "")
    name = (_safe(node.get_name, "") or "").strip()
    if req.get("expect_name") and name and req["expect_name"] != name and req.get("expect_role") not in ("frame", "window", "dialog"):
        raise LookupError(f"element changed: expected {req.get('expect_role')} '{req['expect_name']}', found {role} '{name}'; take a new tree")
    if req.get("expect_role") and req["expect_role"] != role:
        raise LookupError(f"element changed: expected {req['expect_role']} '{req.get('expect_name')}', found {role} '{name}'")
    action = req["action"]
    res = {"ref": req["ref"], "role": role, "name": name, "action": action}
    if action == "click":
        done = _do_action(node, ["click", "activate", "press", "toggle", "jump", "open", "select"])
        if done:
            res["via"] = f"action:{done}"
        else:
            b = bbox(node)
            if not b:
                raise RuntimeError("element has no action and no on-screen position")
            x, y = b[0] + b[2] // 2, b[1] + b[3] // 2
            Atspi.generate_mouse_event(x, y, "b1c")
            res.update(via="mouse", x=x, y=y)
    elif action == "action":
        done = _do_action(node, [req["name"]])
        if not done:
            raise LookupError(f"element has no action {req['name']}; it has {actions(node)}")
        res["via"] = f"action:{done}"
    elif action == "focus":
        c = node.get_component_iface()
        res["focused"] = bool(c and c.grab_focus())
    elif action in ("set_text", "insert_text"):
        e = _safe(node.get_editable_text_iface)
        if e is None:
            raise LookupError(f"{role} '{name}' is not editable text")
        if action == "set_text":
            ok = e.set_text_contents(req.get("text", ""))
        else:
            pos = req.get("position")
            if pos is None:
                pos = _safe(lambda: Atspi.Text.get_character_count(node), 0)
            ok = e.insert_text(int(pos), req.get("text", ""), len(req.get("text", "").encode("utf-8")))
        res["ok"] = bool(ok)
        time.sleep(0.05)
        res["text"] = text_of(node, 2000)
    elif action == "read":
        res["text"] = text_of(node, req.get("limit", 20000))
        res["value"] = value_of(node)
        res["states"] = states(node)
        res["bbox"] = bbox(node)
        res["actions"] = actions(node)
    else:
        raise ValueError(f"unknown action {action}")
    return res


def op_apps(req):
    return {"apps": [app_info(a) for a in apps()]}


def main():
    req = json.loads(sys.stdin.read() or "{}")
    try:
        fn = {"tree": op_tree, "find": op_find, "act": op_act, "apps": op_apps}[req.get("op")]
        out = {"ok": True, "result": fn(req)}
    except LookupError as e:
        out = {"ok": False, "code": "NOT_FOUND", "message": str(e)}
    except Exception as e:  # noqa: BLE001
        out = {"ok": False, "code": "ERROR", "message": f"{type(e).__name__}: {e}"}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
