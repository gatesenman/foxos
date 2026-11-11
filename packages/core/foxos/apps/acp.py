"""ACP 智能体：注册表、安装 / 卸载、官方图标、密钥、握手测试（CLI = MCP acp.*）。

与 Electron 伴侣程序同一目录布局：FOXOS_HOME/agents/<id>/foxos-agent.json。操作系统镜像预装的智能体
在 /usr/lib/foxos/agents/<id>/foxos-agent.json（只读，用户安装的同名智能体优先）。
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

from .. import audit, secrets
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app

REGISTRY_URL = "https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json"
SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "acp-registry-snapshot.json"
SYSTEM_AGENTS = Path(os.environ.get("FOXOS_SYSTEM_AGENTS", "/usr/lib/foxos/agents"))
LOCAL_ID = "foxos-local"
# 各智能体常用的 API 密钥环境变量（也可以填任意变量名）
KEY_HINTS = {
    "claude-acp": ["ANTHROPIC_API_KEY"], "codex-acp": ["OPENAI_API_KEY", "CODEX_API_KEY"], "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "qwen-code": ["OPENAI_API_KEY", "DASHSCOPE_API_KEY"], "opencode": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"], "kimi": ["MOONSHOT_API_KEY"],
    "kimi-code": ["MOONSHOT_API_KEY"], "github-copilot-cli": ["GH_TOKEN"], "cursor": ["CURSOR_API_KEY"], "goose": ["OPENAI_API_KEY"],
    "mistral-vibe": ["MISTRAL_API_KEY"], "glm-acp-agent": ["ZHIPU_API_KEY"], "minimax-code": ["MINIMAX_API_KEY"],
}
OPEN_LICENSES = ("mit", "apache", "bsd", "isc", "mpl")


def home() -> Path:
    return secrets.home()


def agents_dir() -> Path:
    d = home() / "agents"
    d.mkdir(parents=True, exist_ok=True)
    return d


def platform_key() -> str:
    osn = {"linux": "linux", "darwin": "darwin", "win32": "windows"}.get(sys.platform, sys.platform)
    arch = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}.get(platform.machine().lower(), platform.machine())
    return f"{osn}-{arch}"


def fetch_registry(offline: bool = False) -> dict:
    cache = home() / "registry-cache.json"
    if not offline and not os.environ.get("FOXOS_OFFLINE"):
        try:
            with urllib.request.urlopen(REGISTRY_URL, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return {"source": "online", "data": data}
        except (OSError, ValueError):
            pass
    f = cache if cache.exists() else SNAPSHOT
    return {"source": "cache" if f == cache else "snapshot", "data": json.loads(f.read_text(encoding="utf-8"))}


def _info_file(id_: str) -> Path | None:
    for base in (agents_dir(), SYSTEM_AGENTS):
        f = base / id_ / "foxos-agent.json"
        if f.is_file():
            return f
    return None


def installed_info(id_: str) -> dict | None:
    if id_ == LOCAL_ID:
        return {"id": LOCAL_ID, "name": tr("acp.local_agent_name"), "version": "1.0.0", "method": "builtin", "command": sys.executable,
                "args": ["-m", "foxos.local_agent"], "env": {"PYTHONPATH": str(Path(__file__).resolve().parents[2])}, "license": "same as FoxOS",
                "system": True}
    f = _info_file(id_)
    if not f:
        return None
    try:
        info = json.loads(f.read_text(encoding="utf-8"))
    except ValueError:
        return None
    cmd = info.get("command") or ""
    if cmd and not os.path.isabs(cmd):
        cmd = shutil.which(cmd) or cmd
    info["command"] = cmd
    if not cmd or not os.path.exists(cmd):
        return None
    info["system"] = str(f).startswith(str(SYSTEM_AGENTS))
    return info


def installed() -> list[dict]:
    ids = {LOCAL_ID}
    for base in (agents_dir(), SYSTEM_AGENTS):
        if base.is_dir():
            ids |= {d.name for d in base.iterdir() if (d / "foxos-agent.json").is_file()}
    return [i for i in (installed_info(x) for x in sorted(ids)) if i]


def redistributable(lic: str | None) -> bool:
    lic = (lic or "").lower()
    return any(x in lic for x in OPEN_LICENSES)


def icon_path(id_: str) -> Path | None:
    p = agents_dir() / "icons" / f"{id_}.svg"
    return p if p.is_file() else None


def fetch_icon(entry: dict) -> Path | None:
    url = entry.get("icon")
    if not url:
        return None
    p = agents_dir() / "icons" / f"{entry['id']}.svg"
    if p.is_file():
        return p
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = r.read()
        if b"<svg" not in data[:2000] or len(data) > 512 * 1024:
            return None
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p
    except OSError:
        return None


# ---------------------------------------------------------------------- 安装
def _which(name: str) -> str | None:
    return shutil.which(name)


def _run(argv: list[str], cwd: Path, log) -> None:
    log(f"$ {' '.join(argv)}")
    p = subprocess.Popen(argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for line in p.stdout:
        log(line.rstrip())
    if p.wait() != 0:
        raise FoxError("ERROR", tr("acp.step_failed", os.path.basename(argv[0]), p.returncode))


def _download(url: str, log, progress) -> tuple[bytes, str]:
    with urllib.request.urlopen(url, timeout=60) as r:
        total = int(r.headers.get("Content-Length") or 0)
        buf = io.BytesIO()
        h = hashlib.sha256()
        got = 0
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            buf.write(chunk)
            h.update(chunk)
            got += len(chunk)
            progress(got, total)
    log(tr("acp.downloaded_mb", round(got / 1048576, 1)))
    return buf.getvalue(), h.hexdigest()


def install_agent(id_: str, log=print, progress=lambda got, total: None) -> dict:
    reg = fetch_registry()
    entry = next((a for a in reg["data"]["agents"] if a["id"] == id_), None)
    if not entry:
        raise FoxError("NOT_FOUND", tr("acp.not_in_registry", id_))
    d = entry.get("distribution") or {}
    dest = agents_dir() / id_
    dest.mkdir(parents=True, exist_ok=True)
    pk = platform_key()
    if d.get("npx"):
        npm = _which("npm")
        if not npm:
            raise FoxError("DEPENDENCY_MISSING", tr("acp.npm_missing"), hint="foxos runtime install node")
        pkg = d["npx"]["package"]
        _run([npm, "install", "--prefix", str(dest), "--no-fund", "--no-audit", "--loglevel", "error", pkg], dest, log)
        name = pkg.rsplit("@", 1)[0] if pkg.count("@") > (1 if pkg.startswith("@") else 0) else pkg
        pj = json.loads((dest / "node_modules" / name / "package.json").read_text(encoding="utf-8"))
        b = pj.get("bin")
        bin_ = b if isinstance(b, str) else next(iter((b or {}).values()), None)
        if not bin_:
            raise FoxError("ERROR", tr("acp.no_bin", name))
        node = _which("node")
        if not node:
            raise FoxError("DEPENDENCY_MISSING", tr("acp.npm_missing"))
        info = {"id": id_, "name": entry["name"], "version": pj.get("version"), "method": "npm", "package": pkg, "command": node,
                "args": [str(dest / "node_modules" / name / bin_), *d["npx"].get("args", [])], "env": d["npx"].get("env", {})}
    elif d.get("binary") and d["binary"].get(pk):
        b = d["binary"][pk]
        log(tr("acp.downloading", b["archive"]))
        data, sha = _download(b["archive"], log, progress)
        if b.get("sha256") and sha != b["sha256"].lower():
            raise FoxError("PERMISSION_DENIED", tr("acp.sha_mismatch", b["sha256"], sha))
        log(tr("acp.sha_ok", sha) if b.get("sha256") else tr("acp.sha_unpublished", sha))
        unpack = dest / "bin"
        shutil.rmtree(unpack, ignore_errors=True)
        unpack.mkdir(parents=True)
        name = b["archive"].lower()
        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(unpack)
        else:
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                t.extractall(unpack, filter="data") if hasattr(tarfile, "data_filter") else t.extractall(unpack)  # noqa: S202
        cmd = (unpack / b["cmd"]).resolve()
        if not str(cmd).startswith(str(unpack.resolve())):
            raise FoxError("PERMISSION_DENIED", "bad cmd path")
        os.chmod(cmd, 0o755)
        info = {"id": id_, "name": entry["name"], "version": entry.get("version"), "method": "binary", "command": str(cmd),
                "args": b.get("args", []), "env": b.get("env", {}), "sha256": sha}
    elif d.get("uvx"):
        uvx = _which("uvx")
        if not uvx:
            raise FoxError("DEPENDENCY_MISSING", tr("acp.uv_missing"), hint="foxos runtime install uv")
        pkg = d["uvx"]["package"]
        _run([uvx, "--from", pkg, "python", "-c", "print('ok')"], dest, log)  # 预先下载到 uv 缓存
        info = {"id": id_, "name": entry["name"], "version": entry.get("version"), "method": "uvx", "command": uvx,
                "args": [pkg, *d["uvx"].get("args", [])], "env": d["uvx"].get("env", {})}
    else:
        raise FoxError("DEPENDENCY_MISSING", tr("acp.no_method", entry["name"], pk))
    info.update(license=entry.get("license"), repository=entry.get("repository"), installedAt=audit.now_iso())
    (dest / "foxos-agent.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    fetch_icon(entry)
    log(tr("acp.installed", entry["name"], info.get("version")))
    return info


# ---------------------------------------------------------------------- 握手
def agent_env(id_: str, info: dict) -> dict:
    return {**(info.get("env") or {}), **secrets.env_for(f"acp:{id_}:")}


def probe(ws, id_: str, new_session: bool = True, timeout: float = 90.0) -> dict:
    from ..acp_client import AcpConnection, AcpError, foxos_mcp_server
    info = installed_info(id_)
    if not info:
        raise FoxError("NOT_FOUND", tr("acp.not_installed", id_), hint=f"foxos acp agent install {id_}")
    ident = f"acp:{id_}"
    conn = AcpConnection(info["command"], info.get("args"), agent_env(id_, info), identity=ident, workspace=ws.root,
                         call=lambda c, p: __import__("foxos.kernel", fromlist=["invoke"]).invoke(c, p, Context(ws, agent=ident, interface="acp")))
    t0 = time.monotonic()
    conn.start()
    out: dict = {"agent": id_, "command": info["command"]}
    try:
        init = conn.initialize(timeout)
        out.update(protocolVersion=init.get("protocolVersion"), agentInfo=init.get("agentInfo"),
                   authMethods=init.get("authMethods") or [], agentCapabilities=init.get("agentCapabilities"))
        if new_session:
            try:
                s = conn.new_session([foxos_mcp_server(ws.root, ident)], timeout)
                out["session"] = {"ok": True, "sessionId": s.get("sessionId"), "models": s.get("models"), "modes": s.get("modes")}
            except AcpError as e:
                out["session"] = {"ok": False, "code": e.code, "message": str(e), "auth_required": e.code == -32000}
    except AcpError as e:
        raise FoxError("ERROR", tr("acp.handshake_failed", id_, e, conn.stderr[-500:])) from e
    finally:
        conn.stop()
    out["ms"] = round((time.monotonic() - t0) * 1000)
    return out


# ---------------------------------------------------------------------- 命令
def cmd_agent_list(ctx: Context, available: bool = False) -> dict:
    inst = {i["id"]: i for i in installed()}
    if not available:
        return {"count": len(inst), "agents": [_public(i) for i in inst.values()]}
    reg = fetch_registry()
    pk = platform_key()
    out = []
    for a in reg["data"]["agents"]:
        d = a.get("distribution") or {}
        methods = [m for m in ("npx", "uvx") if d.get(m)] + (["binary"] if (d.get("binary") or {}).get(pk) else [])
        i = inst.get(a["id"])
        out.append({"id": a["id"], "name": a["name"], "version": a.get("version"), "description": a.get("description"), "license": a.get("license"),
                    "redistributable": redistributable(a.get("license")), "icon": a.get("icon"), "repository": a.get("repository"),
                    "methods": methods, "installed": bool(i), "installed_version": (i or {}).get("version"), "key_env": KEY_HINTS.get(a["id"], [])})
    return {"source": reg["source"], "platform": pk, "count": len(out), "agents": out}


def _public(i: dict) -> dict:
    return {"id": i["id"], "name": i.get("name"), "version": i.get("version"), "method": i.get("method"), "license": i.get("license"),
            "system": i.get("system", False), "key_env": KEY_HINTS.get(i["id"], []),
            "keys": [s["name"].split(":", 2)[2] for s in secrets.names(f"acp:{i['id']}:")]}


def cmd_agent_install(ctx: Context, agent: str) -> dict:
    lines: list[str] = []

    def log(s):
        lines.append(str(s))
        if os.environ.get("FOXOS_PROGRESS"):
            print(json.dumps({"progress": "log", "text": str(s)}, ensure_ascii=False), file=sys.stderr, flush=True)

    def progress(got, total):
        if os.environ.get("FOXOS_PROGRESS"):
            print(json.dumps({"progress": "bytes", "got": got, "total": total}), file=sys.stderr, flush=True)

    info = install_agent(agent, log, progress)
    return {"message": tr("acp.installed", info["name"], info.get("version")), "agent": _public({**info, "system": False}), "log": lines[-40:]}


def cmd_agent_uninstall(ctx: Context, agent: str) -> dict:
    d = agents_dir() / agent
    if not (d / "foxos-agent.json").exists():
        raise FoxError("NOT_FOUND", tr("acp.not_installed", agent))
    shutil.rmtree(d)
    return {"message": tr("acp.uninstalled", agent), "agent": agent}


def cmd_agent_show(ctx: Context, agent: str) -> dict:
    i = installed_info(agent)
    reg = fetch_registry(offline=True)
    entry = next((a for a in reg["data"]["agents"] if a["id"] == agent), None)
    if not i and not entry:
        raise FoxError("NOT_FOUND", tr("acp.not_in_registry", agent))
    ic = icon_path(agent) or (fetch_icon(entry) if entry else None)
    return {"agent": agent, "installed": _public(i) if i else None, "registry": entry, "icon_path": str(ic) if ic else None}


def cmd_agent_probe(ctx: Context, agent: str, session: bool = True) -> dict:
    return probe(ctx.workspace, agent, new_session=session)


def cmd_agent_login(ctx: Context, agent: str, method: str) -> dict:
    """调用智能体自己的 ACP authenticate（例如 Gemini 的浏览器登录）。"""
    from ..acp_client import AcpConnection, AcpError
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("acp.login_human_only"))
    info = installed_info(agent)
    if not info:
        raise FoxError("NOT_FOUND", tr("acp.not_installed", agent))
    conn = AcpConnection(info["command"], info.get("args"), agent_env(agent, info), identity=f"acp:{agent}", workspace=ctx.workspace.root)
    conn.start()
    try:
        conn.initialize()
        conn.authenticate(method)
    except AcpError as e:
        raise FoxError("ERROR", tr("acp.login_failed", e)) from e
    finally:
        conn.stop()
    return {"message": tr("acp.signed_in", agent), "agent": agent, "method": method}


def cmd_key_set(ctx: Context, agent: str, name: str, value: str) -> dict:
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("acp.keys_human_only"))
    if not name.replace("_", "").isalnum() or name.upper() != name:
        raise FoxError("USAGE", tr("acp.bad_env_name"))
    d = secrets.put(f"acp:{agent}:{name}", value)
    return {"message": tr("acp.key_saved", name, agent), "agent": agent, "name": name, "hint": d["hint"]}


def cmd_key_list(ctx: Context, agent: str | None = None) -> dict:
    items = [{"agent": s["name"].split(":")[1], "name": s["name"].split(":", 2)[2], "hint": s["hint"], "updated": s["updated"]}
             for s in secrets.names("acp:") if s["name"].count(":") >= 2]
    if agent:
        items = [i for i in items if i["agent"] == agent]
    return {"count": len(items), "keys": items}


def cmd_key_remove(ctx: Context, agent: str, name: str) -> dict:
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("acp.keys_human_only"))
    if not secrets.delete(f"acp:{agent}:{name}"):
        raise FoxError("NOT_FOUND", tr("acp.no_key", name, agent))
    return {"message": tr("acp.key_removed", name, agent)}


AG = Param("agent", "string", tr("acp.p_agent"), required=True, positional=True, metavar="AGENT")
register_app("acp", tr("acp.app_summary"), tr("acp.app_description"))
register(Command("acp", "agent list", tr("acp.c_list"), cmd_agent_list,
                 params=[Param("available", "boolean", tr("acp.p_available"), default=False)],
                 examples=["foxos acp agent list --json", "foxos acp agent list --available --json"], audited=False))
register(Command("acp", "agent install", tr("acp.c_install"), cmd_agent_install, params=[AG],
                 examples=["foxos acp agent install codex-acp", "foxos acp agent install gemini"], permission="run",
                 limits=[tr("acp.l_install")]))
register(Command("acp", "agent uninstall", tr("acp.c_uninstall"), cmd_agent_uninstall, params=[AG],
                 examples=["foxos acp agent uninstall codex-acp"], permission="delete"))
register(Command("acp", "agent show", tr("acp.c_show"), cmd_agent_show, params=[AG], examples=["foxos acp agent show gemini --json"]))
register(Command("acp", "agent probe", tr("acp.c_probe"), cmd_agent_probe,
                 params=[AG, Param("session", "boolean", tr("acp.p_session"), default=True)],
                 examples=["foxos acp agent probe codex-acp --json"], permission="run"))
register(Command("acp", "agent login", tr("acp.c_login"), cmd_agent_login,
                 params=[AG, Param("method", "string", tr("acp.p_method"), required=True)],
                 examples=["foxos acp agent login gemini --method oauth-personal"], permission="run", limits=[tr("acp.login_human_only")]))
register(Command("acp", "key set", tr("acp.c_key_set"), cmd_key_set,
                 params=[AG, Param("name", "string", tr("acp.p_env"), required=True, positional=True, metavar="ENV_NAME"),
                         Param("value", "string", tr("acp.p_value"), required=True, cli_stdin=True, secret=True)],
                 examples=["printf %s \"$KEY\" | foxos acp key set codex-acp OPENAI_API_KEY --value-stdin"], permission="modify",
                 limits=[tr("acp.keys_human_only"), tr("acp.l_secret")]))
register(Command("acp", "key list", tr("acp.c_key_list"), cmd_key_list,
                 params=[Param("agent", "string", tr("acp.p_agent"), cli_flag="--acp-agent")], examples=["foxos acp key list --json"], audited=False))
register(Command("acp", "key remove", tr("acp.c_key_remove"), cmd_key_remove,
                 params=[AG, Param("name", "string", tr("acp.p_env"), required=True, positional=True, metavar="ENV_NAME")],
                 examples=["foxos acp key remove codex-acp OPENAI_API_KEY"], permission="delete"))
