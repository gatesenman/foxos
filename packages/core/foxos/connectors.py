"""连接器：给智能体接上外部能力（MCP 服务器、OAuth 应用、频道）。参考 OpenBot 的连接器目录与按智能体授权。

- 目录（CATALOG）：OpenBot 目录里的同一批托管 MCP 服务器（Parallel、Exa、Firecrawl 的免密钥与 API 密钥两种、
  Notion 的 OAuth + 动态客户端注册、Google Drive 的 OAuth），外加 GitHub MCP 与自定义（任意 URL 或本机 stdio 命令）。
- 认证：none / bearer（密钥存在本地密钥库）/ oauth（授权码 + PKCE，本机回环地址回调，支持 RFC 7591 动态注册，自动刷新）。
- 工具：连接时读取 tools/list 存起来；智能体通过 foxos 命令 / MCP `connector_tool_call` 调用，
  只能调用授权给它的连接器；目录里标为写入的工具按该智能体的审批规则询问。每次调用都写审计。
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets as pysecrets
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

from . import audit, secrets
from .errors import FoxError
from .i18n import tr

PROTO = "2025-06-18"

CATALOG = [
    {"key": "parallel", "title": "Parallel Search", "vendor": "Parallel", "summary": "connectors.s_parallel", "url": "https://search.parallel.ai/mcp",
     "auth": {"kind": "none"}, "write_tools": [], "docs": "https://docs.parallel.ai/integrations/mcp/search-mcp", "icon": "world-search"},
    {"key": "parallel-authenticated", "title": "Parallel Search (API key)", "vendor": "Parallel", "summary": "connectors.s_parallel_key",
     "url": "https://search.parallel.ai/mcp", "auth": {"kind": "bearer"}, "write_tools": [], "docs": "https://docs.parallel.ai/integrations/mcp/search-mcp", "icon": "world-search"},
    {"key": "exa", "title": "Exa Search", "vendor": "Exa", "summary": "connectors.s_exa", "url": "https://mcp.exa.ai/mcp", "auth": {"kind": "none"},
     "write_tools": [], "docs": "https://exa.ai/docs/reference/exa-mcp", "icon": "search"},
    {"key": "exa-authenticated", "title": "Exa Search (API key)", "vendor": "Exa", "summary": "connectors.s_exa_key", "url": "https://mcp.exa.ai/mcp",
     "auth": {"kind": "bearer", "header": "x-api-key"}, "write_tools": [], "docs": "https://exa.ai/docs/reference/exa-mcp", "icon": "search"},
    {"key": "firecrawl", "title": "Firecrawl", "vendor": "Firecrawl", "summary": "connectors.s_firecrawl", "url": "https://mcp.firecrawl.dev/v2/mcp",
     "auth": {"kind": "none"}, "write_tools": ["firecrawl_crawl", "firecrawl_extract"], "docs": "https://docs.firecrawl.dev/mcp-server", "icon": "flame"},
    {"key": "firecrawl-authenticated", "title": "Firecrawl (API key)", "vendor": "Firecrawl", "summary": "connectors.s_firecrawl_key",
     "url": "https://mcp.firecrawl.dev/v2/mcp", "auth": {"kind": "bearer"}, "write_tools": ["firecrawl_crawl", "firecrawl_extract"],
     "docs": "https://docs.firecrawl.dev/mcp-server", "icon": "flame"},
    {"key": "notion", "title": "Notion", "vendor": "Notion", "summary": "connectors.s_notion", "url": "https://mcp.notion.com/mcp",
     "auth": {"kind": "oauth", "authorization_url": "https://mcp.notion.com/authorize", "token_url": "https://mcp.notion.com/token",
              "registration_url": "https://mcp.notion.com/register", "scopes": []},
     "write_tools": ["notion-create-pages", "notion-update-page", "notion-move-pages", "notion-duplicate-page", "notion-create-database",
                     "notion-update-database", "notion-create-comment"], "docs": "https://developers.notion.com/docs/mcp", "icon": "brand-notion"},
    {"key": "google-drive", "title": "Google Drive", "vendor": "Google", "summary": "connectors.s_gdrive", "url": "https://drivemcp.googleapis.com/mcp/v1",
     "auth": {"kind": "oauth", "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth", "token_url": "https://oauth2.googleapis.com/token",
              "scopes": ["https://www.googleapis.com/auth/drive.readonly"], "params": {"access_type": "offline", "prompt": "consent"},
              "client_required": True},
     "write_tools": ["create_file", "copy_file"], "docs": "https://developers.google.com/workspace/guides/configure-mcp-servers", "icon": "brand-google-drive"},
    {"key": "github", "title": "GitHub", "vendor": "GitHub", "summary": "connectors.s_github", "url": "https://api.githubcopilot.com/mcp/",
     "auth": {"kind": "bearer"}, "write_tools": ["create_issue", "create_pull_request", "merge_pull_request", "push_files", "create_or_update_file",
                                                 "delete_file", "add_issue_comment", "update_issue"], "docs": "https://github.com/github/github-mcp-server", "icon": "brand-github"},
]


def home() -> Path:
    return secrets.home()


def _path() -> Path:
    return home() / "connectors.json"


def _load() -> dict:
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(d: dict):
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def catalog() -> list[dict]:
    inst = _load()
    return [{**c, "summary": tr(c["summary"]), "installed": any(v.get("key") == c["key"] for v in inst.values())} for c in CATALOG]


def installed() -> list[dict]:
    out = []
    for cid, c in sorted(_load().items()):
        out.append({"id": cid, **{k: v for k, v in c.items() if k != "tools"}, "tool_count": len(c.get("tools") or []),
                    "connected": connected(cid, c)})
    return out


def get(cid: str) -> dict:
    c = _load().get(cid)
    if not c:
        raise FoxError("NOT_FOUND", tr("connectors.no_such_connector", cid), hint="foxos connector catalog")
    return {"id": cid, **c}


def connected(cid: str, c: dict) -> bool:
    k = (c.get("auth") or {}).get("kind", "none")
    return k == "none" or bool(secrets.get(f"connector:{cid}:token"))


def add(key: str | None, cid: str | None = None, title: str | None = None, url: str | None = None, command: list | None = None,
        auth: str | None = None, header: str | None = None) -> dict:
    d = _load()
    if key:
        e = next((c for c in CATALOG if c["key"] == key), None)
        if not e:
            raise FoxError("NOT_FOUND", tr("connectors.not_in_catalog", key))
        rec = {"key": key, "title": e["title"], "vendor": e["vendor"], "transport": "http", "url": e["url"], "auth": e["auth"],
               "write_tools": e["write_tools"], "icon": e.get("icon"), "docs": e.get("docs")}
        cid = cid or key
    else:
        if not cid or not (url or command):
            raise FoxError("USAGE", tr("connectors.custom_needs"))
        if url and not url.startswith(("https://", "http://127.0.0.1", "http://localhost")):
            raise FoxError("PERMISSION_DENIED", tr("connectors.https_only"))
        au = {"kind": auth or "none", **({"header": header} if header else {})}
        if au["kind"] == "oauth":
            if not url:
                raise FoxError("USAGE", tr("connectors.oauth_needs_url"))
            au.update(discover_oauth(url))
        rec = {"key": "custom", "title": title or cid, "vendor": "", "transport": "http" if url else "stdio", "url": url,
               "command": command, "auth": au, "write_tools": [], "icon": "plug"}
    if not cid or not all(ch.isalnum() or ch in "-_" for ch in cid):
        raise FoxError("USAGE", tr("connectors.bad_id"))
    if cid in d:
        raise FoxError("CONFLICT", tr("connectors.exists", cid))
    rec["added"] = audit.now_iso()
    d[cid] = rec
    _save(d)
    return {"id": cid, **rec}


def _get_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "foxos-connector"}), timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except (OSError, ValueError):
        return None


def discover_oauth(mcp_url: str) -> dict:
    """MCP 授权发现：先读受保护资源元数据（RFC 9728）找授权服务器，再读授权服务器元数据（RFC 8414）。"""
    u = urllib.parse.urlparse(mcp_url)
    origin = f"{u.scheme}://{u.netloc}"
    issuers = [origin]
    for path in (f"/.well-known/oauth-protected-resource{u.path.rstrip('/')}", "/.well-known/oauth-protected-resource"):
        prm = _get_json(origin + path)
        if prm and prm.get("authorization_servers"):
            issuers = [str(x).rstrip("/") for x in prm["authorization_servers"]] + issuers
            break
    for iss in issuers:
        iu = urllib.parse.urlparse(iss)
        for path in (f"/.well-known/oauth-authorization-server{iu.path.rstrip('/')}", f"/.well-known/openid-configuration{iu.path.rstrip('/')}"):
            meta = _get_json(f"{iu.scheme}://{iu.netloc}{path}")
            if meta and meta.get("authorization_endpoint") and meta.get("token_endpoint"):
                if "S256" not in (meta.get("code_challenge_methods_supported") or ["S256"]):
                    raise FoxError("PERMISSION_DENIED", tr("connectors.oauth_no_pkce", iss))
                return {"authorization_url": meta["authorization_endpoint"], "token_url": meta["token_endpoint"],
                        **({"registration_url": meta["registration_endpoint"]} if meta.get("registration_endpoint") else {}),
                        "scopes": [], "issuer": meta.get("issuer", iss)}
    raise FoxError("DEPENDENCY_MISSING", tr("connectors.oauth_discovery_failed", mcp_url))


def remove(cid: str) -> dict:
    d = _load()
    if cid not in d:
        raise FoxError("NOT_FOUND", tr("connectors.no_such_connector", cid))
    d.pop(cid)
    _save(d)
    for suffix in ("token", "refresh", "expires", "client_id", "client_secret"):
        secrets.delete(f"connector:{cid}:{suffix}")
    return {"removed": cid}


def set_token(cid: str, token: str) -> dict:
    get(cid)
    secrets.put(f"connector:{cid}:token", token)
    return {"id": cid, "connected": True}


def disconnect(cid: str) -> dict:
    get(cid)
    for suffix in ("token", "refresh", "expires"):
        secrets.delete(f"connector:{cid}:{suffix}")
    return {"id": cid, "connected": False}


# ---------------------------------------------------------------------- OAuth（授权码 + PKCE，回环地址回调）
def oauth_connect(cid: str, client_id: str | None = None, client_secret: str | None = None, open_browser: bool = True,
                  timeout: float = 300.0, on_url=None) -> dict:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    c = get(cid)
    a = c.get("auth") or {}
    if a.get("kind") != "oauth":
        raise FoxError("USAGE", tr("connectors.not_oauth", cid))
    got: dict = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *x):
            pass

        def do_GET(self):  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            body = tr("connectors.oauth_done_page").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_address[1]}/callback"
    cid_ = client_id or secrets.get(f"connector:{cid}:client_id")
    csec = client_secret or secrets.get(f"connector:{cid}:client_secret")
    if not cid_ and a.get("registration_url"):
        reg = _post_json(a["registration_url"], {"client_name": "FoxOS", "redirect_uris": [redirect], "grant_types": ["authorization_code", "refresh_token"],
                                                 "response_types": ["code"], "token_endpoint_auth_method": "none"})
        cid_ = reg.get("client_id")
        csec = reg.get("client_secret")
    if not cid_:
        srv.server_close()
        raise FoxError("DEPENDENCY_MISSING", tr("connectors.client_id_needed", cid))
    secrets.put(f"connector:{cid}:client_id", cid_)
    if csec:
        secrets.put(f"connector:{cid}:client_secret", csec)
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = pysecrets.token_urlsafe(16)
    q = {"response_type": "code", "client_id": cid_, "redirect_uri": redirect, "state": state, "code_challenge": challenge,
         "code_challenge_method": "S256", **({"scope": " ".join(a["scopes"])} if a.get("scopes") else {}), **(a.get("params") or {})}
    url = a["authorization_url"] + "?" + urllib.parse.urlencode(q)
    if on_url:
        on_url(url)
    if open_browser:
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if os.name == "posix" else None
    srv.timeout = 1
    t_end = time.time() + timeout
    while not got and time.time() < t_end:
        srv.handle_request()
    srv.server_close()
    if not got:
        raise FoxError("ERROR", tr("connectors.oauth_timeout"))
    if got.get("state") != state or not got.get("code"):
        raise FoxError("PERMISSION_DENIED", tr("connectors.oauth_bad_state", got.get("error", "")))
    tok = _post_form(a["token_url"], {"grant_type": "authorization_code", "code": got["code"], "redirect_uri": redirect, "client_id": cid_,
                                     "code_verifier": verifier, **({"client_secret": csec} if csec else {})})
    _store_tokens(cid, tok)
    return {"id": cid, "connected": True, "scopes": tok.get("scope")}


def _store_tokens(cid: str, tok: dict):
    if not tok.get("access_token"):
        raise FoxError("PERMISSION_DENIED", tr("connectors.oauth_no_token"))
    secrets.put(f"connector:{cid}:token", tok["access_token"])
    if tok.get("refresh_token"):
        secrets.put(f"connector:{cid}:refresh", tok["refresh_token"])
    if tok.get("expires_in"):
        secrets.put(f"connector:{cid}:expires", str(time.time() + float(tok["expires_in"]) - 60))


def _refresh_if_needed(cid: str, c: dict):
    a = c.get("auth") or {}
    exp = secrets.get(f"connector:{cid}:expires")
    if a.get("kind") != "oauth" or not exp or float(exp) > time.time():
        return
    rt = secrets.get(f"connector:{cid}:refresh")
    if not rt:
        return
    csec = secrets.get(f"connector:{cid}:client_secret")
    tok = _post_form(a["token_url"], {"grant_type": "refresh_token", "refresh_token": rt, "client_id": secrets.get(f"connector:{cid}:client_id") or "",
                                     **({"client_secret": csec} if csec else {})})
    _store_tokens(cid, tok)


def _post_json(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _post_form(url, body):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(body).encode(), headers={"Content-Type": "application/x-www-form-urlencoded",
                                                                                         "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise FoxError("PERMISSION_DENIED", tr("connectors.oauth_token_failed", e.code, e.read().decode("utf-8", "replace")[:300])) from e


# ---------------------------------------------------------------------- MCP 客户端
class McpClient:
    def __init__(self, c: dict):
        self.c = c
        self.sid = None
        self.n = 0
        self.proc = None
        cid = c["id"]
        _refresh_if_needed(cid, c)
        self.headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": "foxos-connector/0.3"}
        a = c.get("auth") or {}
        if a.get("kind") in ("bearer", "oauth"):
            tok = secrets.get(f"connector:{cid}:token")
            if not tok:
                raise FoxError("PERMISSION_DENIED", tr("connectors.not_connected", cid), hint=f"foxos connector connect {cid}")
            h = a.get("header") or "Authorization"
            self.headers[h] = f"Bearer {tok}" if h.lower() == "authorization" else tok
        if c.get("transport") == "stdio":
            env = {**os.environ, **secrets.env_for(f"connector:{cid}:env:")}
            self.proc = subprocess.Popen(c["command"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                         encoding="utf-8", env=env)

    def close(self):
        if self.proc and self.proc.poll() is None:
            self.proc.kill()

    def _rpc(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})}
        if not notify:
            self.n += 1
            msg["id"] = self.n
        if self.proc:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()
            if notify:
                return None
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    raise FoxError("ERROR", tr("connectors.server_exited"))
                m = json.loads(line)
                if m.get("id") == self.n:
                    return self._result(m)
        hdr = dict(self.headers)
        if self.sid:
            hdr["Mcp-Session-Id"] = self.sid
        req = urllib.request.Request(self.c["url"], data=json.dumps(msg).encode(), headers=hdr, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                self.sid = r.headers.get("Mcp-Session-Id") or self.sid
                ctype = r.headers.get("Content-Type", "")
                raw = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise FoxError("PERMISSION_DENIED", tr("connectors.unauthorized", self.c["id"], e.code)) from e
            raise FoxError("ERROR", tr("connectors.http_error", e.code, e.read().decode("utf-8", "replace")[:200])) from e
        except OSError as e:
            raise FoxError("DEPENDENCY_MISSING", tr("connectors.unreachable", self.c["url"], e)) from e
        if notify:
            return None
        if "text/event-stream" in ctype:
            for line in raw.splitlines():
                if line.startswith("data:"):
                    try:
                        m = json.loads(line[5:].strip())
                    except ValueError:
                        continue
                    if m.get("id") == self.n:
                        return self._result(m)
            raise FoxError("ERROR", tr("connectors.no_reply"))
        return self._result(json.loads(raw))

    def _result(self, m):
        if m.get("error"):
            raise FoxError("ERROR", tr("connectors.rpc_error", m["error"].get("message")))
        return m.get("result")

    def initialize(self):
        r = self._rpc("initialize", {"protocolVersion": PROTO, "capabilities": {}, "clientInfo": {"name": "foxos", "version": "1"}})
        self._rpc("notifications/initialized", None, notify=True)
        return r

    def tools(self):
        return (self._rpc("tools/list", {}) or {}).get("tools", [])

    def call(self, name, args):
        return self._rpc("tools/call", {"name": name, "arguments": args or {}})


def refresh_tools(cid: str) -> dict:
    c = get(cid)
    cl = McpClient(c)
    try:
        init = cl.initialize()
        tools = cl.tools()
    finally:
        cl.close()
    d = _load()
    d[cid]["tools"] = [{"name": t["name"], "description": (t.get("description") or "")[:300], "write": t["name"] in (c.get("write_tools") or [])
                        or bool((t.get("annotations") or {}).get("destructiveHint")) or (t.get("annotations") or {}).get("readOnlyHint") is False}
                       for t in tools]
    d[cid]["server"] = (init or {}).get("serverInfo")
    d[cid]["tools_refreshed"] = audit.now_iso()
    _save(d)
    return {"id": cid, "server": d[cid]["server"], "tools": d[cid]["tools"]}


def call_tool(ws, caller: str, cid: str, tool: str, arguments: dict) -> dict:
    from . import bots
    c = get(cid)
    tinfo = next((t for t in c.get("tools") or [] if t["name"] == tool), None)
    if c.get("tools") and not tinfo:
        raise FoxError("NOT_FOUND", tr("connectors.no_such_tool", tool, cid))
    is_write = bool((tinfo or {}).get("write")) or tool in (c.get("write_tools") or [])
    if caller.startswith("bot:"):
        b = bots.get(ws, caller[4:].split("/")[0].split("@")[0])
        if cid not in (b.get("connectors") or []):
            raise FoxError("PERMISSION_DENIED", tr("connectors.not_granted", cid, b["name"]), hint=f"foxos bot config set {b['id']} --connectors {cid}")
        if is_write:
            dec = bots._auto_decision(b, "edit")
            if dec == "deny":
                raise FoxError("PERMISSION_DENIED", tr("connectors.write_denied", tool))
            once = os.environ.get("FOXOS_BOT_APPROVE")  # 这一轮的一次性审批方式（bot message send --approve）
            if dec == "ask" and once in ("allow", "deny"):
                dec = once
                if dec == "deny":
                    raise FoxError("PERMISSION_DENIED", tr("connectors.write_not_approved", tool))
            if dec == "ask":
                opts = [{"optionId": "allow", "name": tr("bots.allow_once"), "kind": "allow_once"},
                        {"optionId": "reject", "name": tr("bots.deny"), "kind": "reject_once"}]
                ans = bots.ask_file(ws, b, {"toolCallId": f"{cid}.{tool}", "title": f"{c['title']} · {tool}", "kind": "edit", "rawInput": arguments},
                                    opts, os.environ.get("FOXOS_BOT_TURN"))
                if ans != "allow":
                    raise FoxError("PERMISSION_DENIED", tr("connectors.write_not_approved", tool))
    cl = McpClient(c)
    try:
        cl.initialize()
        r = cl.call(tool, arguments)
    finally:
        cl.close()
    text = "\n".join(x.get("text", "") for x in (r or {}).get("content", []) if x.get("type") == "text")
    return {"connector": cid, "tool": tool, "write": is_write, "isError": bool((r or {}).get("isError")), "text": text[:100000],
            "structured": (r or {}).get("structuredContent")}
