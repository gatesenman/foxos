"""技能目录：随系统分发的 pstack 技能与原则（MIT，见 data/pstack/NOTICE），加上用户自己的技能。

格式是 Agent Skills：skills/<名字>/SKILL.md，YAML 头有 name、description，可选 disable-model-invocation。
查找顺序（同名时前面的优先）：工作空间 .foxos/skills/、~/.agents/skills/、狐狸OS 自带的 pstack。
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from .errors import FoxError
from .i18n import tr

PSTACK = Path(__file__).resolve().parent / "data" / "pstack"
HARNESS_DIRS = {
    "claude-code": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "agents": Path.home() / ".agents" / "skills",
    "gemini": Path.home() / ".gemini" / "skills",
}


def _front(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    out: dict = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            out[k.strip()] = {"true": True, "false": False}.get(v, v)
    return out


def _kind(name: str) -> str:
    return "principle" if name.startswith("principle-") else "skill"


def roots(ws=None) -> list[tuple[str, Path]]:
    r = []
    if ws is not None:
        r.append(("workspace", ws.data_dir / "skills"))
    r.append(("user", Path.home() / ".agents" / "skills"))
    r.append(("pstack", PSTACK / "skills"))
    return r


def catalog(ws=None) -> list[dict]:
    seen: dict[str, dict] = {}
    for source, root in roots(ws):
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            f = d / "SKILL.md"
            if d.name in seen or not f.is_file():
                continue
            try:
                fm = _front(f.read_text(encoding="utf-8"))
            except OSError:
                continue
            name = str(fm.get("name") or d.name)
            seen[d.name] = {"name": d.name, "title": name, "kind": _kind(d.name), "source": source,
                            "description": str(fm.get("description") or ""), "path": str(f),
                            "manual_only": bool(fm.get("disable-model-invocation"))}
    if (PSTACK / "agents").is_dir():
        for f in sorted((PSTACK / "agents").glob("*.md")):
            fm = _front(f.read_text(encoding="utf-8"))
            n = f.stem
            if n not in seen:
                seen[n] = {"name": n, "title": str(fm.get("name") or n), "kind": "subagent", "source": "pstack",
                           "description": str(fm.get("description") or ""), "path": str(f), "manual_only": True}
    return sorted(seen.values(), key=lambda s: ({"skill": 0, "principle": 1, "subagent": 2}[s["kind"]], s["name"]))


def get(ws, name: str) -> dict:
    for s in catalog(ws):
        if s["name"] == name:
            return {**s, "content": Path(s["path"]).read_text(encoding="utf-8")}
    raise FoxError("NOT_FOUND", tr("skills.no_such_skill", name), hint=tr("skills.list_hint"))


def for_bot(ws, bot: dict) -> list[dict]:
    cfg = bot.get("skills") or {}
    allc = catalog(ws)
    if cfg.get("mode", "all") == "all":
        off = set(cfg.get("disabled") or [])
        return [s for s in allc if s["name"] not in off]
    on = set(cfg.get("enabled") or [])
    return [s for s in allc if s["name"] in on]


def by_path(ws) -> dict[str, str]:
    return {os.path.realpath(s["path"]): s["name"] for s in catalog(ws)}


def install(harness: str, names: list[str] | None = None, ws=None) -> dict:
    if harness not in HARNESS_DIRS:
        raise FoxError("USAGE", tr("skills.bad_harness", ", ".join(HARNESS_DIRS)))
    dest = HARNESS_DIRS[harness]
    dest.mkdir(parents=True, exist_ok=True)
    done = []
    for s in catalog(ws):
        if s["kind"] == "subagent" or s["source"] != "pstack" or (names and s["name"] not in names):
            continue
        src = Path(s["path"]).parent
        tgt = dest / s["name"]
        if tgt.exists():
            shutil.rmtree(tgt)
        shutil.copytree(src, tgt)
        done.append(s["name"])
    shutil.copy2(PSTACK / "NOTICE", dest / "PSTACK-NOTICE")
    return {"harness": harness, "path": str(dest), "installed": done, "count": len(done)}
