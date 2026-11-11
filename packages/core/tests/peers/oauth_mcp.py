"""测试用的对端：一个真实的 OAuth 2.1（PKCE S256、动态注册、刷新令牌）+ MCP Streamable HTTP 服务器。

它代表第三方应用一侧，在 127.0.0.1 上监听，让连接器的完整授权流程（发现 → 注册 → 授权 → 回调 → 换令牌 →
带令牌调用工具 → 刷新）在测试里真实跑一遍。授权页自动同意（相当于用户点了「允许」）。
用法：python oauth_mcp.py READY_FILE
"""
import base64
import hashlib
import json
import secrets
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CLIENTS: dict = {}
CODES: dict = {}
TOKENS: dict = {}
REFRESH: dict = {}
NOTES: list = []
LOG: list = []


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    @property
    def base(self):
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def _json(self, code, obj, headers=None):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n).decode() if n else ""

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
        if u.path.startswith("/.well-known/oauth-protected-resource"):
            return self._json(200, {"resource": self.base + "/mcp", "authorization_servers": [self.base]})
        if u.path == "/.well-known/oauth-authorization-server":
            return self._json(200, {"issuer": self.base, "authorization_endpoint": self.base + "/authorize", "token_endpoint": self.base + "/token",
                                    "registration_endpoint": self.base + "/register", "code_challenge_methods_supported": ["S256"],
                                    "grant_types_supported": ["authorization_code", "refresh_token"]})
        if u.path == "/authorize":
            if q.get("client_id") not in CLIENTS or q.get("code_challenge_method") != "S256" or not q.get("code_challenge"):
                return self._json(400, {"error": "invalid_request"})
            if q["redirect_uri"] not in CLIENTS[q["client_id"]]["redirect_uris"]:
                return self._json(400, {"error": "bad redirect"})
            code = secrets.token_urlsafe(12)
            CODES[code] = {"client_id": q["client_id"], "challenge": q["code_challenge"], "redirect_uri": q["redirect_uri"]}
            LOG.append("authorize")
            self.send_response(302)
            self.send_header("Location", q["redirect_uri"] + "?" + urllib.parse.urlencode({"code": code, "state": q.get("state", "")}))
            self.end_headers()
            return
        if u.path == "/log":
            return self._json(200, {"log": LOG, "notes": NOTES})
        self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        raw = self._body()
        if u.path == "/register":
            body = json.loads(raw)
            cid = "client-" + secrets.token_hex(4)
            CLIENTS[cid] = {"redirect_uris": body.get("redirect_uris", [])}
            LOG.append("register")
            return self._json(201, {"client_id": cid, "redirect_uris": CLIENTS[cid]["redirect_uris"]})
        if u.path == "/token":
            f = {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}
            if f.get("grant_type") == "authorization_code":
                c = CODES.pop(f.get("code", ""), None)
                if not c or c["client_id"] != f.get("client_id") or c["redirect_uri"] != f.get("redirect_uri"):
                    return self._json(400, {"error": "invalid_grant"})
                want = base64.urlsafe_b64encode(hashlib.sha256(f.get("code_verifier", "").encode()).digest()).rstrip(b"=").decode()
                if want != c["challenge"]:
                    return self._json(400, {"error": "invalid_grant", "error_description": "PKCE"})
                LOG.append("token")
            elif f.get("grant_type") == "refresh_token":
                if f.get("refresh_token") not in REFRESH:
                    return self._json(400, {"error": "invalid_grant"})
                REFRESH.pop(f["refresh_token"])
                LOG.append("refresh")
            else:
                return self._json(400, {"error": "unsupported_grant_type"})
            at, rt = "at-" + secrets.token_hex(8), "rt-" + secrets.token_hex(8)
            TOKENS[at] = True
            REFRESH[rt] = True
            # 第一次给一个立刻过期的令牌，让客户端下一次调用前刷新
            return self._json(200, {"access_token": at, "refresh_token": rt, "token_type": "Bearer",
                                    "expires_in": 1 if LOG.count("token") == 1 and "refresh" not in LOG else 3600})
        if u.path == "/mcp":
            auth = self.headers.get("Authorization", "")
            if not auth.startswith("Bearer ") or auth[7:] not in TOKENS:
                return self._json(401, {"error": "unauthorized"}, {"WWW-Authenticate": f'Bearer resource_metadata="{self.base}/.well-known/oauth-protected-resource"'})
            m = json.loads(raw)
            if "id" not in m:
                self.send_response(202)
                self.end_headers()
                return
            meth = m.get("method")
            if meth == "initialize":
                res = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "notes-peer", "version": "1.0"}}
            elif meth == "tools/list":
                res = {"tools": [
                    {"name": "echo", "description": "Echo text", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}},
                     "annotations": {"readOnlyHint": True}},
                    {"name": "save_note", "description": "Save a note", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}},
                     "annotations": {"readOnlyHint": False}}]}
            elif meth == "tools/call":
                p = m["params"]
                txt = (p.get("arguments") or {}).get("text", "")
                if p["name"] == "save_note":
                    NOTES.append(txt)
                    LOG.append("save_note")
                res = {"content": [{"type": "text", "text": f"{p['name']}:{txt}"}], "isError": False}
            else:
                return self._json(200, {"jsonrpc": "2.0", "id": m["id"], "error": {"code": -32601, "message": "no method"}})
            return self._json(200, {"jsonrpc": "2.0", "id": m["id"], "result": res}, {"Mcp-Session-Id": "s1"})
        self._json(404, {"error": "not found"})


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    with open(sys.argv[1], "w") as f:
        f.write(f"http://127.0.0.1:{srv.server_address[1]}")
    srv.serve_forever()
