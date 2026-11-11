"""多台狐狸OS：foxos machine … = MCP machine_*。控制端登记与配对；被控端（host）配对码、客户端、授权。

运行被控端服务：foxos --workspace <目录> machine serve [--listen 0.0.0.0:7443] [--name vm1]
"""

from __future__ import annotations

from .. import machines
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app


def _human(ctx):
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("machines.human_only"))


def m_list(ctx: Context, check: bool = False) -> dict:
    out = [{"name": machines.LOCAL, "local": True, "workspace": str(ctx.workspace.root)}]
    for n, m in sorted(machines.registry().items()):
        e = {"name": n, "local": False, **{k: m.get(k) for k in ("url", "fingerprint", "host", "client", "paired_at")}}
        if check:
            try:
                p = machines.ping(n)
                e.update(online=p["ok"], grants=p.get("grants"), acting=p.get("acting"), ms=p.get("ms"))
            except FoxError as er:
                e.update(online=False, error=er.message)
        out.append(e)
    return {"count": len(out), "machines": out}


def m_pair(ctx: Context, name: str, url: str, code: str, fingerprint: str | None = None, client: str | None = None) -> dict:
    _human(ctx)
    r = machines.pair(name, url, code, fingerprint, client)
    return {"message": tr("machines.paired", name, r["host"]), **r}


def m_remove(ctx: Context, name: str) -> dict:
    _human(ctx)
    return machines.remove(name)


def m_ping(ctx: Context, name: str) -> dict:
    return machines.ping(name)


def m_call(ctx: Context, name: str, command: str, params: dict | None = None) -> dict:
    return {"machine": name, "result": machines.invoke(ctx.workspace, name, command, params or {}, agent=ctx.agent, task=ctx.task)}


def h_code(ctx: Context, ttl: int = 600) -> dict:
    _human(ctx)
    return {"message": tr("machines.code_hint"), **machines.new_pairing_code(ttl)}


def h_clients(ctx: Context) -> dict:
    cs = machines.host_clients()
    return {"count": len(cs), "clients": [{"client": k, "paired_at": v.get("paired_at"), "grants": v.get("grants", {})} for k, v in sorted(cs.items())]}


def h_grant(ctx: Context, client: str, bot: str, permissions: list, apps: list | None = None, scope: str = ".") -> dict:
    _human(ctx)
    ctx.workspace.resolve(scope or ".")
    return machines.grant(client, bot, permissions, apps, scope)


def h_revoke(ctx: Context, client: str, bot: str | None = None) -> dict:
    _human(ctx)
    return machines.revoke(client, bot)


def h_unpair(ctx: Context, client: str) -> dict:
    _human(ctx)
    return machines.unpair_client(client)


NAME = Param("name", "string", tr("machines.p_name"), required=True, positional=True, metavar="MACHINE")
CLIENT = Param("client", "string", tr("machines.p_client"), required=True)
register_app("machine", tr("machines.app_summary"), tr("machines.app_description"))
register(Command("machine", "list", tr("machines.c_list"), m_list, params=[Param("check", "boolean", tr("machines.p_check"), default=False)],
                 examples=["foxos machine list --check --json"], audited=False))
register(Command("machine", "pair", tr("machines.c_pair"), m_pair,
                 params=[Param("name", "string", tr("machines.p_name"), required=True), Param("url", "string", tr("machines.p_url"), required=True),
                         Param("code", "string", tr("machines.p_code"), required=True, secret=True),
                         Param("fingerprint", "string", tr("machines.p_fingerprint")), Param("client", "string", tr("machines.p_client_name"))],
                 examples=["foxos machine pair --name vm1 --url https://192.168.1.20:7443 --code AB12-CD34-EF56 --fingerprint 3f…"],
                 permission="create", limits=[tr("machines.human_only")]))
register(Command("machine", "remove", tr("machines.c_remove"), m_remove, params=[NAME], examples=["foxos machine remove vm1"], permission="delete"))
register(Command("machine", "ping", tr("machines.c_ping"), m_ping, params=[NAME], examples=["foxos machine ping vm1 --json"]))
register(Command("machine", "call", tr("machines.c_call"), m_call,
                 params=[NAME, Param("command", "string", tr("machines.p_command"), required=True), Param("params", "object", tr("machines.p_params"))],
                 examples=["foxos machine call vm1 --command files.list --params '{\"path\":\".\"}'"], permission="run"))
register(Command("machine", "host code", tr("machines.c_code"), h_code, params=[Param("ttl", "integer", tr("machines.p_ttl"), default=600)],
                 examples=["foxos machine host code --json"], permission="create", limits=[tr("machines.human_only")]))
register(Command("machine", "host clients", tr("machines.c_clients"), h_clients, examples=["foxos machine host clients --json"]))
register(Command("machine", "host grant", tr("machines.c_grant"), h_grant,
                 params=[CLIENT, Param("bot", "string", tr("machines.p_bot"), required=True),
                         Param("permissions", "array", tr("machines.p_permissions"), required=True, items={"type": "string"}),
                         Param("apps", "array", tr("machines.p_apps"), items={"type": "string"}),
                         Param("scope", "string", tr("machines.p_scope"), default=".")],
                 examples=["foxos machine host grant --client laptop --bot coder --permissions read,create,modify --apps files --scope projects"],
                 permission="modify", limits=[tr("machines.human_only"), tr("machines.l_default_deny")]))
register(Command("machine", "host revoke", tr("machines.c_revoke"), h_revoke,
                 params=[CLIENT, Param("bot", "string", tr("machines.p_bot"))], examples=["foxos machine host revoke --client laptop --bot coder"],
                 permission="modify"))
register(Command("machine", "host unpair", tr("machines.c_unpair"), h_unpair, params=[CLIENT], examples=["foxos machine host unpair --client laptop"],
                 permission="delete"))
