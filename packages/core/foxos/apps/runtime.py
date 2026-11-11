"""运行环境命令：foxos runtime list / doctor / install = MCP runtime_*。"""

from __future__ import annotations

from .. import runtime as rt
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app


def r_list(ctx: Context, phase: str | None = None, group: str | None = None) -> dict:
    items = [i for i in rt.listing(phase) if not group or i["group"] == group]
    return {"count": len(items), "installed": sum(1 for i in items if i.get("ok")), "tools": items, "manifest": str(rt.MANIFEST)}


def r_doctor(ctx: Context) -> dict:
    return rt.doctor()


def r_install(ctx: Context, name: list, force: bool = False, accept_license: bool = False) -> dict:
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("runtime.human_only"))
    names = name
    if names == ["firstboot"]:
        names = [i["name"] for i in rt.listing("firstboot", check=False)]
    out = []
    for n in names:
        t = rt.tool(n)
        if not t.get("redistributable") and not accept_license:
            raise FoxError("USAGE", tr("runtime.accept_license", n, t["license"], t["source"]), hint=f"foxos runtime install {n} --accept-license")
        out.append(rt.install(n, force=force))
    return {"results": out, "ok": all(r.get("ok") for r in out),
            "message": tr("runtime.installed", ", ".join(f"{r['tool']} {r.get('found') or ''}".strip() for r in out))}


register_app("runtime", tr("runtime.app_summary"), tr("runtime.app_description"))
register(Command("runtime", "list", tr("runtime.c_list"), r_list,
                 params=[Param("phase", "string", tr("runtime.p_phase"), enum=["iso", "firstboot", "optional"]),
                         Param("group", "string", tr("runtime.p_group"), enum=["runtime", "tools", "agents", "optional"])],
                 examples=["foxos runtime list --json", "foxos runtime list --group agents"], audited=False))
register(Command("runtime", "doctor", tr("runtime.c_doctor"), r_doctor, examples=["foxos runtime doctor --json"], audited=False))
register(Command("runtime", "install", tr("runtime.c_install"), r_install,
                 params=[Param("name", "array", tr("runtime.p_name"), required=True, positional=True, metavar="NAME", items={"type": "string"}),
                         Param("force", "boolean", tr("runtime.p_force"), default=False),
                         Param("accept_license", "boolean", tr("runtime.p_accept"), default=False)],
                 examples=["foxos runtime install codex codex-acp", "foxos runtime install claude claude-acp --accept-license", "foxos runtime install go"],
                 permission="create", limits=[tr("runtime.human_only"), tr("runtime.l_sources")]))
