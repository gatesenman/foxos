"""多台狐狸OS：机器登记、配对、远程控制通道。

一个智能体可以控制多台狐狸OS（本机、局域网 / 远程安装、环境里的虚拟机），多个智能体也可以共用一台。

- 被控端（host）运行 `foxos machine serve`：HTTPS（自签名证书，首次运行生成），只接受配对过的客户端。
- 配对：被控端 `foxos machine host code` 给出一次性配对码（默认 10 分钟）和证书指纹；控制端
  `foxos machine pair --name vm1 --url https://… --code …` 用配对码换一个客户端令牌（存在本地密钥库），
  并钉住证书指纹。之后每次连接：控制端校验被控端证书指纹（防冒充），被控端校验客户端令牌（只存哈希）。
- 权限：被控端按「客户端 × 智能体」授权（`foxos machine host grant`），默认全部拒绝；授权写明权限级别
  （read / create / modify / delete / run）、应用（files、desktop…）与工作范围（工作空间里的子目录）。
- 审计：被控端审计里身份是 `bot:<智能体>@<客户端>`，`machine` 字段是客户端名；控制端审计也记一条，
  `machine` 是目标机器名。人工接管在被控端生效（全体或只停某个智能体）。
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import secrets as pysecrets
import socket
import ssl
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from . import audit, secrets
from .errors import FoxError
from .i18n import tr

LOCAL = "local"
PERMISSIONS = ["read", "create", "modify", "delete", "run"]
# 远程永远不能调用的应用：配对与授权、人工接管只能在被控端由人操作
NEVER_REMOTE = {"machine", "control"}


def home() -> Path:
    return secrets.home()


# ---------------------------------------------------------------------- 控制端：登记
def _reg_path() -> Path:
    return home() / "machines.json"


def registry() -> dict:
    try:
        return json.loads(_reg_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_registry(d: dict) -> None:
    p = _reg_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def get(name: str) -> dict:
    if name in (None, "", LOCAL):
        return {"name": LOCAL, "local": True}
    r = registry().get(name)
    if not r:
        raise FoxError("NOT_FOUND", tr("machines.no_such_machine", name), hint=tr("machines.list_hint"))
    return {"name": name, **r}


def fingerprint_der(der: bytes) -> str:
    return hashlib.sha256(der).hexdigest()


def _self_signed(cert: Path, key: Path, cn: str) -> None:
    try:
        subprocess.run(["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-nodes",
                        "-keyout", str(key), "-out", str(cert), "-days", "3650", "-subj", f"/CN={cn}/O=FoxOS",
                        "-addext", "basicConstraints=critical,CA:TRUE"],
                       check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise FoxError("DEPENDENCY_MISSING", tr("machines.openssl_needed", e)) from e
    os.chmod(key, 0o600)


def client_cert() -> tuple[Path, Path, str]:
    """控制端自己的证书（双向 TLS：配对时交给被控端，以后每次连接都出示）。"""
    d = home() / "client"
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(d, 0o700)
    cert, key = d / "cert.pem", d / "key.pem"
    if not cert.exists() or not key.exists():
        _self_signed(cert, key, f"{socket.gethostname() or 'foxos'}-client")
    return cert, key, fingerprint_der(ssl.PEM_cert_to_DER_cert(cert.read_text()))


def _connect(url: str, fingerprint: str | None, timeout: float = 30.0, with_cert: bool = True) -> tuple[http.client.HTTPSConnection, str]:
    u = urlparse(url)
    if u.scheme != "https":
        raise FoxError("USAGE", tr("machines.https_only"))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # 自签名证书：改为钉住指纹（下面逐字节比对）
    if with_cert:
        c, k, _ = client_cert()
        ctx.load_cert_chain(str(c), str(k))
    conn = http.client.HTTPSConnection(u.hostname, u.port or 443, timeout=timeout, context=ctx)
    try:
        conn.connect()
    except OSError as e:
        raise FoxError("DEPENDENCY_MISSING", tr("machines.unreachable", url, e)) from e
    fp = fingerprint_der(conn.sock.getpeercert(binary_form=True))
    if fingerprint and not pysecrets.compare_digest(fp, fingerprint.lower().replace(":", "")):
        conn.close()
        raise FoxError("PERMISSION_DENIED", tr("machines.fingerprint_mismatch", url), details={"expected": fingerprint, "got": fp})
    return conn, fp


def _request(url: str, fingerprint: str | None, method: str, path: str, body: dict | None = None, token: str | None = None,
             timeout: float = 600.0, with_cert: bool = True) -> tuple[int, dict, str]:
    conn, fp = _connect(url, fingerprint, timeout, with_cert)
    try:
        data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8") if body is not None else None
        hdr = {"Content-Type": "application/json"}
        if token:
            hdr["Authorization"] = f"Bearer {token}"
        conn.request(method, path, body=data, headers=hdr)
        r = conn.getresponse()
        raw = r.read().decode("utf-8", "replace")
        try:
            j = json.loads(raw) if raw else {}
        except ValueError:
            j = {"error": {"code": "ERROR", "message": raw[:300]}}
        return r.status, j, fp
    finally:
        conn.close()


def pair(name: str, url: str, code: str, fingerprint: str | None = None, client_name: str | None = None) -> dict:
    if not name or name == LOCAL or "/" in name or "@" in name:
        raise FoxError("USAGE", tr("machines.bad_name"))
    url = url.rstrip("/")
    st, hello, fp = _request(url, fingerprint, "GET", "/v1/hello", with_cert=False)
    if st != 200:
        raise FoxError("ERROR", tr("machines.not_a_foxos_host", url))
    me = client_name or socket.gethostname()
    ccert, _, cfp = client_cert()
    st, r, _ = _request(url, fp, "POST", "/v1/pair", {"code": code, "client": me, "client_cert": ccert.read_text()}, with_cert=False)
    if st != 200 or not r.get("token"):
        raise FoxError("PERMISSION_DENIED", (r.get("error") or {}).get("message") or tr("machines.pair_failed"))
    secrets.put(f"machine:{name}:token", r["token"])
    reg = registry()
    reg[name] = {"url": url, "fingerprint": fp, "client": r.get("client", me), "host": hello.get("name"),
                 "client_fingerprint": cfp, "paired_at": audit.now_iso()}
    _save_registry(reg)
    return {"name": name, "url": url, "fingerprint": fp, "host": hello.get("name"), "client": r.get("client", me)}


def remove(name: str) -> dict:
    reg = registry()
    if name not in reg:
        raise FoxError("NOT_FOUND", tr("machines.no_such_machine", name))
    m = reg.pop(name)
    _save_registry(reg)
    secrets.delete(f"machine:{name}:token")
    return {"removed": name, "url": m.get("url")}


def remote_invoke(name: str, command: str, params: dict, agent: str, task: str | None = None, ws=None) -> dict:
    """在远程机器上执行一条 foxos 命令。返回 result；远程的错误原样抛 FoxError（错误码不变）。"""
    m = get(name)
    tok = secrets.get(f"machine:{name}:token")
    if not tok:
        raise FoxError("PERMISSION_DENIED", tr("machines.not_paired", name))
    t0 = time.monotonic()
    rec = {"agent": agent, "task": task, "interface": "remote-client", "command": command, "machine": name,
           "args": _redact_remote(command, params)}
    try:
        st, r, _ = _request(m["url"], m["fingerprint"], "POST", "/v1/invoke",
                            {"command": command, "params": params or {}, "agent": agent, "task": task}, token=tok)
        if st == 401:
            raise FoxError("PERMISSION_DENIED", tr("machines.token_rejected", name))
        if not r.get("ok"):
            e = r.get("error") or {}
            raise FoxError(e.get("code", "ERROR"), e.get("message", "?"), hint=e.get("hint"), details={**(e.get("details") or {}), "machine": name})
        rec["status"] = "ok"
        return r["result"]
    except FoxError as e:
        rec["status"] = "denied" if e.code in ("PERMISSION_DENIED", "LOCKED", "PAUSED", "CONFLICT") else "error"
        rec["error"] = {"code": e.code, "message": e.message}
        raise
    finally:
        rec["duration_ms"] = round((time.monotonic() - t0) * 1000, 1)
        if ws is not None:
            audit.append_safe(ws, rec)


def _redact_remote(command: str, params: dict) -> dict:
    from .kernel import find, redact
    try:
        return redact(find(command), params or {})
    except FoxError:
        return params or {}


def ping(name: str) -> dict:
    m = get(name)
    if m.get("local"):
        return {"name": LOCAL, "ok": True}
    tok = secrets.get(f"machine:{name}:token")
    t0 = time.monotonic()
    st, r, fp = _request(m["url"], m["fingerprint"], "GET", "/v1/whoami", token=tok, timeout=10)
    return {"name": name, "ok": st == 200, "status": st, "host": r.get("host"), "client": r.get("client"), "grants": r.get("grants"),
            "acting": r.get("acting"), "ms": round((time.monotonic() - t0) * 1000, 1)}


def invoke(ws, machine: str | None, command: str, params: dict, agent: str, task: str | None = None, interface: str = "acp") -> dict:
    """本机或远程执行（聊天引擎、MCP 的 machine 参数、CLI 的 --machine 都走这里）。"""
    if machine in (None, "", LOCAL):
        from .kernel import Context, invoke as kinvoke
        return kinvoke(command, params, Context(ws, agent=agent, task=task, interface=interface))
    return remote_invoke(machine, command, params, agent, task, ws=ws)


# ---------------------------------------------------------------------- 被控端
def host_dir() -> Path:
    d = home() / "host"
    d.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(d, 0o700)
    except OSError:
        pass
    return d


def ensure_cert() -> tuple[Path, Path, str]:
    d = host_dir()
    cert, key = d / "cert.pem", d / "key.pem"
    if not cert.exists() or not key.exists():
        _self_signed(cert, key, socket.gethostname() or "foxos")
    der = ssl.PEM_cert_to_DER_cert(cert.read_text())
    return cert, key, fingerprint_der(der)


def _clients_path() -> Path:
    return host_dir() / "clients.json"


_host_lock = threading.Lock()


def host_clients() -> dict:
    try:
        return json.loads(_clients_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_clients(d: dict) -> None:
    p = _clients_path()
    tmp = p.with_name(f".clients.{os.getpid()}.tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def new_pairing_code(ttl: int = 600) -> dict:
    _, _, fp = ensure_cert()
    code = "-".join(pysecrets.token_hex(2).upper() for _ in range(3))
    (host_dir() / "pairing.json").write_text(json.dumps({"hash": _hash(code), "expires": time.time() + ttl}), encoding="utf-8")
    os.chmod(host_dir() / "pairing.json", 0o600)
    return {"code": code, "expires_in": ttl, "fingerprint": fp}


def _take_pairing_code(code: str) -> bool:
    p = host_dir() / "pairing.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if d.get("expires", 0) < time.time():
        p.unlink(missing_ok=True)
        return False
    if not pysecrets.compare_digest(d.get("hash", ""), _hash(code or "")):
        return False
    p.unlink(missing_ok=True)  # 一次性
    return True


def _client_by_token(token: str) -> tuple[str, dict] | None:
    h = _hash(token or "")
    for cid, c in host_clients().items():
        if pysecrets.compare_digest(c.get("token_hash", ""), h):
            return cid, c
    return None


def grant(client: str, bot: str, permissions: list[str], apps: list[str] | None = None, scope: str = ".") -> dict:
    bad = [p for p in permissions if p not in PERMISSIONS]
    if bad or not permissions:
        raise FoxError("USAGE", tr("machines.bad_permissions", ", ".join(PERMISSIONS)))
    with _host_lock:
        d = host_clients()
        if client not in d:
            raise FoxError("NOT_FOUND", tr("machines.no_such_client", client))
        g = {"permissions": sorted(set(permissions), key=PERMISSIONS.index), "apps": sorted(set(apps or ["*"])),
             "scope": (scope or ".").strip("/") or "."}
        d[client].setdefault("grants", {})[bot] = g
        _save_clients(d)
    return {"client": client, "bot": bot, **g}


def revoke(client: str, bot: str | None = None) -> dict:
    with _host_lock:
        d = host_clients()
        if client not in d:
            raise FoxError("NOT_FOUND", tr("machines.no_such_client", client))
        if bot:
            d[client].get("grants", {}).pop(bot, None)
        else:
            d[client]["grants"] = {}
        _save_clients(d)
    return {"client": client, "revoked": bot or "*"}


def unpair_client(client: str) -> dict:
    with _host_lock:
        d = host_clients()
        if d.pop(client, None) is None:
            raise FoxError("NOT_FOUND", tr("machines.no_such_client", client))
        _save_clients(d)
    return {"unpaired": client}


def _bot_of(agent: str) -> str:
    """bot:coder/acp:codex-acp → coder"""
    a = str(agent or "")
    if a.startswith("bot:"):
        return a[4:].split("/")[0].split("@")[0]
    return a


def check_grant(client: dict, agent: str, cmd, params: dict, ws) -> None:
    bot = _bot_of(agent)
    grants = client.get("grants") or {}
    g = grants.get(bot) or grants.get("*")
    if not g:
        raise FoxError("PERMISSION_DENIED", tr("machines.no_grant", bot), hint=tr("machines.grant_hint", bot))
    if cmd.app in NEVER_REMOTE:
        raise FoxError("PERMISSION_DENIED", tr("machines.never_remote", cmd.app))
    if cmd.permission not in g["permissions"]:
        raise FoxError("PERMISSION_DENIED", tr("machines.permission_not_granted", cmd.permission, bot), details={"granted": g["permissions"]})
    if "*" not in g["apps"] and cmd.app not in g["apps"]:
        raise FoxError("PERMISSION_DENIED", tr("machines.app_not_granted", cmd.app, bot), details={"apps": g["apps"]})
    scope = g.get("scope", ".")
    if scope != ".":
        root = (ws.root / scope).resolve()
        for p in cmd.params:
            v = (params or {}).get(p.name)
            if p.path and v:
                real = Path(os.path.realpath(v if os.path.isabs(v) else ws.root / v))
                try:
                    real.relative_to(root)
                except ValueError:
                    raise FoxError("PERMISSION_DENIED", tr("acp.outside_scope", v, scope)) from None


def serve(ws, host: str = "0.0.0.0", port: int = 7443, name: str | None = None, ready=None) -> int:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    from . import activity
    from .kernel import Context, find, invoke as kinvoke

    cert, key, fp = ensure_cert()
    me = name or socket.gethostname()

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        timeout = 900

        def setup(self):
            self.request.settimeout(30)
            self.request.do_handshake()
            self.request.settimeout(None)
            super().setup()

        def log_message(self, *a):
            pass

        def _send(self, code, body):
            data = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 64 * 1024 * 1024:
                raise ValueError("too large")
            raw = self.rfile.read(n) if n else b"{}"
            return json.loads(raw.decode("utf-8") or "{}")

        def _client(self):
            """双向认证：令牌必须属于某个已配对的控制端，且这条 TLS 连接出示的客户端证书就是配对时登记的那张。"""
            auth = self.headers.get("Authorization", "")
            c = _client_by_token(auth[7:]) if auth.startswith("Bearer ") else None
            if not c:
                return None
            try:
                der = self.connection.getpeercert(binary_form=True)
            except (AttributeError, ValueError):
                der = None
            if not der or not pysecrets.compare_digest(fingerprint_der(der), c[1].get("cert_fp") or "-"):
                audit.append_safe(ws, {"agent": f"remote:{c[0]}", "interface": "remote", "command": self.path, "status": "denied",
                                       "machine": c[0], "error": {"code": "PERMISSION_DENIED", "message": "client certificate mismatch"}})
                return None
            return c

        def do_GET(self):  # noqa: N802
            if self.path == "/v1/hello":
                return self._send(200, {"product": "foxos", "name": me, "fingerprint": fp})
            c = self._client()
            if not c:
                return self._send(401, {"error": {"code": "PERMISSION_DENIED", "message": "unauthorized"}})
            if self.path == "/v1/whoami":
                return self._send(200, {"host": me, "client": c[0], "grants": c[1].get("grants", {}),
                                        "acting": activity.current(ws)})
            self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})

        def do_POST(self):  # noqa: N802
            try:
                body = self._body()
            except ValueError:
                return self._send(400, {"error": {"code": "USAGE", "message": "bad request"}})
            if self.path == "/v1/pair":
                if not _take_pairing_code(str(body.get("code", ""))):
                    audit.append_safe(ws, {"agent": f"remote:{body.get('client')}", "interface": "remote", "command": "machine.pair",
                                           "status": "denied", "error": {"code": "PERMISSION_DENIED", "message": "bad pairing code"}})
                    return self._send(403, {"error": {"code": "PERMISSION_DENIED", "message": tr("machines.bad_code")}})
                token = pysecrets.token_urlsafe(32)
                cname = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in str(body.get("client") or "client"))[:40] or "client"
                with _host_lock:
                    d = host_clients()
                    base, i = cname, 2
                    while cname in d:
                        cname, i = f"{base}-{i}", i + 1
                    pem = str(body.get("client_cert") or "")
                    try:
                        cfp = fingerprint_der(ssl.PEM_cert_to_DER_cert(pem))
                    except ValueError:
                        return self._send(400, {"error": {"code": "USAGE", "message": tr("machines.client_cert_needed")}})
                    d[cname] = {"token_hash": _hash(token), "cert_fp": cfp, "cert_pem": pem, "paired_at": audit.now_iso(), "grants": {}}
                    _save_clients(d)
                audit.append_safe(ws, {"agent": f"remote:{cname}", "interface": "remote", "command": "machine.pair", "status": "ok",
                                       "machine": cname})
                return self._send(200, {"token": token, "client": cname, "host": me})
            if self.path != "/v1/invoke":
                return self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})
            c = self._client()
            if not c:
                return self._send(401, {"error": {"code": "PERMISSION_DENIED", "message": "unauthorized"}})
            cid, client = c
            agent = str(body.get("agent") or "remote")
            if agent == "human" or agent.startswith("human:"):
                agent = f"remote-human:{cid}"  # 远端声称的人不是这台机器上的人：不能绕过接管
            ident = f"{agent}@{cid}"
            command = str(body.get("command") or "")
            params = body.get("params") or {}
            ctx = Context(ws, agent=ident, task=body.get("task"), interface="remote", machine=cid)
            try:
                cmd = find(command)
                check_grant(client, agent, cmd, params, ws)
            except FoxError as e:
                audit.append_safe(ws, {"agent": ident, "interface": "remote", "command": command, "machine": cid,
                                       "args": params, "status": "denied", "error": {"code": e.code, "message": e.message}})
                return self._send(200, {"ok": False, "error": e.to_dict()})
            try:
                res = kinvoke(cmd.id, params, ctx)
                return self._send(200, {"ok": True, "command": cmd.id, "result": res})
            except FoxError as e:
                return self._send(200, {"ok": False, "command": cmd.id, "error": e.to_dict()})

    def tls_context() -> ssl.SSLContext:
        # 每个连接按当前已配对的控制端重建：它们的自签名证书就是信任锚；未配对的连接（配对本身）可以不出示证书
        sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sctx.minimum_version = ssl.TLSVersion.TLSv1_2
        sctx.load_cert_chain(str(cert), str(key))
        pems = "".join(c.get("cert_pem", "") for c in host_clients().values())
        if pems:
            sctx.load_verify_locations(cadata=pems)
            sctx.verify_mode = ssl.CERT_OPTIONAL
        return sctx

    class TlsServer(ThreadingHTTPServer):
        def get_request(self):
            sock, addr = self.socket.accept()
            # 握手放到处理线程里第一次读写时做，不阻塞接受新连接
            return tls_context().wrap_socket(sock, server_side=True, do_handshake_on_connect=False), addr

        def handle_error(self, request, client_address):
            pass  # TLS 握手失败（证书不对）：静默断开

    srv = TlsServer((host, port), H)
    info = {"url": f"https://{srv.server_address[0]}:{srv.server_address[1]}", "name": me, "fingerprint": fp, "workspace": str(ws.root)}
    if ready:
        ready(info)
    else:
        print(json.dumps(info, ensure_ascii=False), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
