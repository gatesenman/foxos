"""连接器命令：foxos connector <资源> <动作> = MCP connector_<资源>_<动作>。"""

from __future__ import annotations

import json

from .. import connectors
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app

CID = Param("connector", "string", tr("connector.p_id"), required=True, positional=True, metavar="CONNECTOR")


def _human(ctx):
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("bot.human_only"))


def c_catalog(ctx: Context) -> dict:
    c = connectors.catalog()
    return {"count": len(c), "catalog": c}


def c_list(ctx: Context) -> dict:
    c = connectors.installed()
    return {"count": len(c), "connectors": c}


def c_add(ctx: Context, key: str | None = None, id: str | None = None, title: str | None = None, url: str | None = None,
          command: list | None = None, auth: str | None = None, header: str | None = None) -> dict:
    _human(ctx)
    r = connectors.add(key, id, title, url, command, auth, header)
    return {"message": tr("connector.added", r["title"]), "connector": r}


def c_remove(ctx: Context, connector: str) -> dict:
    _human(ctx)
    return connectors.remove(connector)


def c_connect(ctx: Context, connector: str, token: str | None = None, client_id: str | None = None, client_secret: str | None = None,
              no_browser: bool = False) -> dict:
    _human(ctx)
    c = connectors.get(connector)
    kind = (c.get("auth") or {}).get("kind")
    if kind == "bearer":
        if not token:
            raise FoxError("USAGE", tr("connector.token_required"))
        connectors.set_token(connector, token)
    elif kind == "oauth":
        def show(url):
            import sys
            print(json.dumps({"authorize_url": url}, ensure_ascii=False), file=sys.stderr, flush=True)
        connectors.oauth_connect(connector, client_id, client_secret, open_browser=not no_browser, on_url=show)
    try:
        t = connectors.refresh_tools(connector)
    except FoxError as e:
        if e.code == "PERMISSION_DENIED":  # 对端拒绝了令牌：不算连上，删掉这枚令牌
            connectors.disconnect(connector)
            return {"connected": False, "tools": None, "warning": e.message}
        return {"connected": True, "tools": None, "warning": e.message}
    return {"message": tr("connector.connected", c["title"], len(t["tools"])), "connected": True, "tools": t["tools"], "server": t["server"]}


def c_disconnect(ctx: Context, connector: str) -> dict:
    _human(ctx)
    return connectors.disconnect(connector)


def c_tools(ctx: Context, connector: str, refresh: bool = False) -> dict:
    if refresh:
        return connectors.refresh_tools(connector)
    c = connectors.get(connector)
    return {"id": connector, "tools": c.get("tools") or [], "server": c.get("server")}


def c_call(ctx: Context, connector: str, tool: str, arguments: dict | None = None) -> dict:
    return connectors.call_tool(ctx.workspace, ctx.agent, connector, tool, arguments or {})


register_app("connector", tr("connector.app_summary"), tr("connector.app_description"))
register(Command("connector", "catalog", tr("connector.c_catalog"), c_catalog, examples=["foxos connector catalog --json"], audited=False))
register(Command("connector", "list", tr("connector.c_list"), c_list, examples=["foxos connector list --json"], audited=False))
register(Command("connector", "add", tr("connector.c_add"), c_add,
                 params=[Param("key", "string", tr("connector.p_key")), Param("id", "string", tr("connector.p_id")),
                         Param("title", "string", tr("connector.p_title")), Param("url", "string", tr("connector.p_url")),
                         Param("command", "array", tr("connector.p_command"), items={"type": "string"}, cli_repeat=True, cli_flag="--arg"),
                         Param("auth", "string", tr("connector.p_auth"), enum=["none", "bearer", "oauth"]),
                         Param("header", "string", tr("connector.p_header"))],
                 examples=["foxos connector add --key exa", "foxos connector add --id mine --url https://mcp.example.com/mcp --auth bearer"],
                 permission="create", limits=[tr("bot.human_only")]))
register(Command("connector", "remove", tr("connector.c_remove"), c_remove, params=[CID], examples=["foxos connector remove exa"], permission="delete"))
register(Command("connector", "connect", tr("connector.c_connect"), c_connect,
                 params=[CID, Param("token", "string", tr("connector.p_token"), cli_stdin=True, secret=True),
                         Param("client_id", "string", tr("connector.p_client_id")),
                         Param("client_secret", "string", tr("connector.p_client_secret"), secret=True),
                         Param("no_browser", "boolean", tr("connector.p_no_browser"), default=False)],
                 examples=["printf %s \"$KEY\" | foxos connector connect exa-authenticated --token-stdin", "foxos connector connect notion"],
                 permission="modify", limits=[tr("bot.human_only"), tr("connector.l_secret")]))
register(Command("connector", "disconnect", tr("connector.c_disconnect"), c_disconnect, params=[CID],
                 examples=["foxos connector disconnect notion"], permission="modify"))
register(Command("connector", "tools", tr("connector.c_tools"), c_tools,
                 params=[CID, Param("refresh", "boolean", tr("connector.p_refresh"), default=False)], examples=["foxos connector tools exa --refresh"]))
register(Command("connector", "tool call", tr("connector.c_call"), c_call,
                 params=[CID, Param("tool", "string", tr("connector.p_tool"), required=True),
                         Param("arguments", "object", tr("connector.p_arguments"))],
                 examples=["foxos connector tool call exa --tool web_search_exa --arguments '{\"query\":\"ACP\"}'"], permission="run",
                 limits=[tr("connector.l_call")]))
