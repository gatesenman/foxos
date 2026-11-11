"""AT-SPI 无障碍树（Linux 桌面程序：GTK、Qt、Chrome、Firefox、LibreOffice、Electron）——文字就能看懂界面。

与 Playwright MCP 的无障碍快照同一思路：每个可操作的元素给一个短引用（e1、e2…），按引用点击、输入；
不需要视觉模型，纯文本模型（例如 DeepSeek）也能操作桌面程序。引用保存在 .foxos/a11y-refs.json，
同时记下角色与名字，元素变了会报错而不是点错地方。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr

HELPER = Path(__file__).resolve().parent / "a11y_helper.py"


def _python() -> str:
    env = os.environ.get("FOXOS_A11Y_PYTHON")
    if env:
        return env
    for cand in (sys.executable, "/usr/bin/python3", shutil.which("python3") or ""):
        if cand and os.path.exists(cand):
            p = subprocess.run([cand, "-c", "import gi; gi.require_version('Atspi', '2.0'); from gi.repository import Atspi"],
                               capture_output=True, timeout=20)
            if p.returncode == 0:
                os.environ["FOXOS_A11Y_PYTHON"] = cand
                return cand
    raise FoxError("DEPENDENCY_MISSING", tr("a11y.no_atspi"), hint="sudo apt install at-spi2-core gir1.2-atspi-2.0 python3-gi")


def call(req: dict, timeout: float = 30.0) -> dict:
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.environ.get("AT_SPI_BUS_ADDRESS")):
        raise FoxError("DEPENDENCY_MISSING", tr("desktop.x11_display_is_not_available"), hint=tr("desktop.start_an_xfce_session_or_set_display"))
    try:
        p = subprocess.run([_python(), "-W", "ignore", str(HELPER)], input=json.dumps(req), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise FoxError("ERROR", tr("a11y.timeout", req.get("op"))) from e
    try:
        out = json.loads(p.stdout or "{}")
    except ValueError:
        raise FoxError("ERROR", tr("a11y.helper_failed", (p.stderr or p.stdout)[-500:])) from None
    if not out.get("ok"):
        raise FoxError(out.get("code") or "ERROR", out.get("message") or tr("a11y.helper_failed", p.stderr[-300:]))
    return out["result"]


# ------------------------------------------------------------------ 引用

def _refs_path(ws) -> Path:
    return ws.data_dir / "a11y-refs.json"


def _load_refs(ws) -> dict:
    try:
        return json.loads(_refs_path(ws).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"next": 1, "refs": {}}


def _save_refs(ws, d: dict) -> None:
    if len(d["refs"]) > 5000:  # 只留最近的
        keep = sorted(d["refs"].items(), key=lambda kv: int(kv[0][1:]))[-3000:]
        d["refs"] = dict(keep)
    tmp = _refs_path(ws).with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, _refs_path(ws))


def assign(ws, nodes: list[dict]) -> None:
    """给节点分配短引用 e<n>（同一个元素在同一次登记里复用原来的引用）。"""
    d = _load_refs(ws)
    by_path = {v["path"]: k for k, v in d["refs"].items()}
    for n in nodes:
        k = by_path.get(n["ref"])
        if k is None or d["refs"][k].get("role") != n["role"] or d["refs"][k].get("name") != n["name"]:
            k = f"e{d['next']}"
            d["next"] += 1
        d["refs"][k] = {"path": n["ref"], "role": n["role"], "name": n["name"]}
        n["path"] = n["ref"]
        n["ref"] = k
    _save_refs(ws, d)


def lookup(ws, ref: str) -> dict:
    ref = str(ref).strip()
    if ":" in ref and ref.split(":")[0].isdigit():
        return {"path": ref}
    r = _load_refs(ws)["refs"].get(ref)
    if not r:
        raise FoxError("NOT_FOUND", tr("a11y.no_ref", ref), hint="foxos desktop tree")
    return r


def render(apps: list[dict]) -> str:
    lines = []
    for a in apps:
        lines.append(f'- application "{a["app"]}" [pid={a["pid"]}]' + (" [active]" if a.get("active") else ""))
        for n in a["nodes"]:
            if n["role"] == "application":
                continue
            ind = "  " * max(1, n["depth"])
            s = f'{ind}- {n["role"]}'
            if n.get("name"):
                s += f' "{n["name"][:120]}"'
            s += f' [ref={n["ref"]}]'
            if n.get("states"):
                s += " [" + ", ".join(n["states"]) + "]"
            if n.get("text") is not None:
                s += ": " + json.dumps(n["text"][:200], ensure_ascii=False)
            if n.get("value") is not None:
                s += f" value={n['value']}"
            lines.append(s)
    return "\n".join(lines)


def tree(ws, app: str | None = None, pid: int | None = None, all_apps: bool = False, hidden: bool = False, max_nodes: int = 600) -> dict:
    r = call({"op": "tree", "app": app, "pid": pid, "all": all_apps, "hidden": hidden, "max_nodes": max_nodes})
    nodes = [n for a in r["apps"] for n in a["nodes"]]
    assign(ws, nodes)
    return {"apps": [{k: v for k, v in a.items() if k != "nodes"} for a in r["apps"]], "count": len(nodes),
            "truncated": r["truncated"], "snapshot": render(r["apps"]), "nodes": nodes}


def find(ws, role: str | None = None, name: str | None = None, app: str | None = None, regex: bool = False, limit: int = 20) -> dict:
    r = call({"op": "find", "role": role, "name": name, "app": app, "regex": regex, "limit": limit})
    assign(ws, r["matches"])
    return {"count": len(r["matches"]), "matches": r["matches"]}


def act(ws, ref: str, action: str, **kw) -> dict:
    r = lookup(ws, ref)
    req = {"op": "act", "ref": r["path"], "action": action, **kw}
    if r.get("role"):
        req["expect_role"] = r["role"]
        req["expect_name"] = r.get("name")
    out = call(req)
    out["ref"] = ref
    out["path"] = r["path"]
    return out


def apps() -> list[dict]:
    return call({"op": "apps"})["apps"]
