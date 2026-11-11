"""智能体运行环境：Node / Bun / Python(uv, pipx) / 常用工具 / 智能体命令行。

清单在 data/runtime-manifest.json（固定版本、许可证、官方来源、sha256、安装阶段）。同一份代码用于：
- 构建 ISO：`python3 -m foxos.runtime install --phase iso --system`（scripts/os/hooks/35-agent-runtime.sh，root，装到 /usr/lib/foxos/runtime，
  命令链接到 /usr/local/bin，ACP 智能体登记到 /usr/lib/foxos/agents）；
- 首次登录与随时安装：`foxos runtime install <名字>`（当前用户，装到 ~/.local/share/foxos/runtime，链接到 ~/.local/bin，
  ACP 智能体登记到 FOXOS_HOME/agents）。
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

from .errors import FoxError
from .i18n import tr

MANIFEST = Path(__file__).resolve().parent / "data" / "runtime-manifest.json"
SYSTEM_PREFIX = Path("/usr/lib/foxos/runtime")
SYSTEM_BIN = Path("/usr/local/bin")
SYSTEM_AGENTS = Path(os.environ.get("FOXOS_SYSTEM_AGENTS", "/usr/lib/foxos/agents"))


def _foxos_home() -> Path:
    from .desktop_client import foxos_home
    return foxos_home()


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def tool(name: str) -> dict:
    for t in manifest()["tools"]:
        if t["name"] == name:
            return t
    raise FoxError("NOT_FOUND", tr("runtime.no_such_tool", name), hint="foxos runtime list")


def user_prefix() -> Path:
    return Path(os.environ.get("FOXOS_RUNTIME_PREFIX") or Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "foxos" / "runtime")


def user_bin() -> Path:
    return Path(os.environ.get("FOXOS_RUNTIME_BIN") or Path.home() / ".local" / "bin")


def search_path() -> str:
    extra = [str(user_bin()), str(SYSTEM_BIN), "/usr/bin", "/bin"]
    cur = os.environ.get("PATH", "").split(os.pathsep)
    return os.pathsep.join(dict.fromkeys([*extra[:1], *cur, *extra[1:]]))


def _progress(name: str, step: str, pct: float | None = None, **kw):
    ev = {"tool": name, "step": step, **({"pct": round(pct, 1)} if pct is not None else {}), **kw}
    if os.environ.get("FOXOS_PROGRESS") == "1":
        print(json.dumps(ev, ensure_ascii=False), file=sys.stderr, flush=True)
    f = os.environ.get("FOXOS_PROGRESS_FILE")
    if f:
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev, ensure_ascii=False) + "\n")


def _download(t: dict) -> tuple[bytes, str]:
    url = t["url"]
    if not url.startswith("https://"):
        raise FoxError("PERMISSION_DENIED", tr("runtime.https_only"))
    req = urllib.request.Request(url, headers={"User-Agent": "foxos-runtime"})
    buf = io.BytesIO()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            total = int(r.headers.get("Content-Length") or 0)
            got, last = 0, 0.0
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                buf.write(chunk)
                got += len(chunk)
                if time.monotonic() - last > 0.5:
                    last = time.monotonic()
                    _progress(t["name"], "download", 100 * got / total if total else None, mb=round(got / 1e6, 1))
    except OSError as e:
        raise FoxError("DEPENDENCY_MISSING", tr("runtime.download_failed", url, e)) from None
    data = buf.getvalue()
    sha = hashlib.sha256(data).hexdigest()
    if t.get("sha256") and sha != t["sha256"].lower():
        raise FoxError("PERMISSION_DENIED", tr("runtime.sha_mismatch", t["name"], t["sha256"], sha))
    _progress(t["name"], "verified" if t.get("sha256") else "unverified", 100, sha256=sha)
    return data, sha


def _extract(data: bytes, dest: Path, strip: int, is_zip: bool):
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    root = dest.resolve()

    def target(name: str) -> Path | None:
        parts = [p for p in name.split("/") if p not in ("", ".")][strip:]
        if not parts:
            return None
        p = (dest / "/".join(parts)).resolve()
        if not str(p).startswith(str(root) + os.sep):
            raise FoxError("PERMISSION_DENIED", tr("runtime.bad_archive"))
        return p

    if is_zip:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for i in z.infolist():
                p = target(i.filename)
                if p is None:
                    continue
                if i.is_dir():
                    p.mkdir(parents=True, exist_ok=True)
                    continue
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(z.read(i))
                mode = (i.external_attr >> 16) & 0o777
                os.chmod(p, mode or 0o755)
        return
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        for m in tf.getmembers():
            p = target(m.name)
            if p is None:
                continue
            if m.isdir():
                p.mkdir(parents=True, exist_ok=True)
            elif m.issym():
                if os.path.isabs(m.linkname) or not str((p.parent / m.linkname).resolve()).startswith(str(root)):
                    continue
                p.parent.mkdir(parents=True, exist_ok=True)
                if p.is_symlink() or p.exists():
                    p.unlink()
                os.symlink(m.linkname, p)
            elif m.isfile():
                p.parent.mkdir(parents=True, exist_ok=True)
                with tf.extractfile(m) as src, open(p, "wb") as out:
                    shutil.copyfileobj(src, out)
                os.chmod(p, m.mode & 0o777 or 0o644)


def _link(src: Path, bindir: Path, name: str | None = None):
    bindir.mkdir(parents=True, exist_ok=True)
    dst = bindir / (name or src.name)
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    os.symlink(src, dst)
    return dst


def _run(argv, env=None, cwd=None, name="?"):
    _progress(name, "run", cmd=" ".join(argv[:3]))
    p = subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        tail = (p.stderr or p.stdout or "")[-800:]
        raise FoxError("ERROR", tr("runtime.step_failed", argv[0], p.returncode, tail))
    return p


def _env() -> dict:
    return {**os.environ, "PATH": search_path(), "npm_config_update_notifier": "false", "npm_config_fund": "false", "npm_config_audit": "false"}


def _register_acp(t: dict, cmd: Path, system: bool, home: Path | None = None):
    a = t["acp"]
    base = SYSTEM_AGENTS if system else _foxos_home() / "agents"
    d = base / a["id"]
    d.mkdir(parents=True, exist_ok=True)
    info = {"id": a["id"], "name": t["title"], "version": t["version"], "method": "runtime:" + t["kind"], "command": str(cmd), "args": a.get("args", []),
            "env": {}, "license": t["license"], "repository": t["source"], "installedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "installedBy": "foxos runtime"}
    (d / "foxos-agent.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return d


def install(name: str, system: bool = False, force: bool = False) -> dict:
    t = tool(name)
    prefix = SYSTEM_PREFIX if system else user_prefix()
    bindir = SYSTEM_BIN if system else user_bin()
    if system and not t.get("redistributable"):
        raise FoxError("PERMISSION_DENIED", tr("runtime.not_redistributable", name, t["license"]))
    if not force:
        st = status(t)
        if st["ok"]:
            _progress(name, "done", 100, already=True)
            return {"tool": name, "already": True, **st}
    _progress(name, "start", 0, version=t["version"])
    home = prefix / t["name"]
    kind = t["kind"]
    sha = None
    linked = []
    if kind in ("tarball", "zip", "binary"):
        data, sha = _download(t)
        _extract(data, home, t.get("strip", 0), t["url"].endswith(".zip"))
        for b in t.get("bins", []):
            p = home / b
            if not p.exists():
                raise FoxError("ERROR", tr("runtime.no_bin", name, b))
            os.chmod(p, 0o755)
            linked.append(str(_link(p, bindir, Path(b).name)))
        for alias, target_ in (t.get("links") or {}).items():
            linked.append(str(_link(home / target_, bindir, alias)))
    elif kind == "npm":
        npm = shutil.which("npm", path=search_path())
        if not npm:
            raise FoxError("DEPENDENCY_MISSING", tr("runtime.needs_node"), hint="foxos runtime install node")
        home.mkdir(parents=True, exist_ok=True)
        _run([npm, "install", "-g", "--prefix", str(home), "--loglevel", "error", f"{t['package']}@{t['version']}"], env=_env(), name=name)
        for b in t.get("bins", []):
            p = home / "bin" / b
            if not p.exists():
                raise FoxError("ERROR", tr("runtime.no_bin", name, b))
            linked.append(str(_link(p, bindir, b)))
    elif kind == "uv-tool":
        uv = shutil.which("uv", path=search_path())
        if not uv:
            raise FoxError("DEPENDENCY_MISSING", tr("runtime.needs_uv"), hint="foxos runtime install uv")
        env = {**_env(), "UV_TOOL_DIR": str(prefix / "uv-tools"), "UV_TOOL_BIN_DIR": str(bindir), "UV_PYTHON_INSTALL_DIR": str(prefix / "uv-python")}
        _run([uv, "tool", "install", "--force", "--python", t.get("python", "3.12"), f"{t['package']}=={t['version']}"], env=env, name=name)
        linked = [str(bindir / b) for b in t.get("bins", [])]
    elif kind == "rustup":
        data, sha = _download(t)
        home.mkdir(parents=True, exist_ok=True)
        ri = home / "rustup-init"
        ri.write_bytes(data)
        os.chmod(ri, 0o755)
        env = {**_env(), "RUSTUP_HOME": str(home / "rustup"), "CARGO_HOME": str(home / "cargo")}
        _run([str(ri), "-y", "--no-modify-path", "--profile", "minimal", "--default-toolchain", "stable"], env=env, name=name)
        for b in t.get("bins", []):
            # rustup 的代理命令需要 RUSTUP_HOME/CARGO_HOME：写小包装脚本而不是软链接
            w = bindir / b
            bindir.mkdir(parents=True, exist_ok=True)
            if w.is_symlink() or w.exists():
                w.unlink()
            w.write_text(f"#!/bin/sh\nexport RUSTUP_HOME='{home / 'rustup'}' CARGO_HOME='{home / 'cargo'}'\nexec '{home / 'cargo' / 'bin' / b}' \"$@\"\n")
            os.chmod(w, 0o755)
            linked.append(str(w))
    elif kind == "apt":
        missing = [p for p in t.get("packages", []) if subprocess.run(["dpkg", "-s", p], capture_output=True).returncode]
        if missing:
            if os.geteuid() != 0:
                raise FoxError("PERMISSION_DENIED", tr("runtime.apt_needs_root", " ".join(missing)), hint="sudo apt-get install -y " + " ".join(missing))
            _run(["apt-get", "install", "-y", "--no-install-recommends", *missing], env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"}, name=name)
        for alias, target_ in (t.get("links_system") or {}).items():
            if os.path.exists(target_) and os.access(bindir.parent if not bindir.exists() else bindir, os.W_OK):
                linked.append(str(_link(Path(target_), bindir, alias)))
    elif kind == "bundled":
        pass
    else:
        raise FoxError("ERROR", tr("runtime.bad_kind", kind))
    acp_dir = None
    if t.get("acp"):
        cmd = (home / t["acp"]["bin"]) if kind in ("tarball", "zip", "binary") else (bindir / t["acp"]["bin"])
        acp_dir = str(_register_acp(t, cmd, system))
    st = status(t)
    _progress(name, "done" if st["ok"] else "check_failed", 100, version=st.get("found"))
    return {"tool": name, "already": False, "sha256": sha, "linked": linked, "acp": acp_dir, **st}


def status(t: dict) -> dict:
    chk = t.get("check")
    if t["kind"] == "apt" and not chk:
        return {"ok": True}
    if not chk:  # 没有 --version 的适配器：看 ACP 登记文件
        a = t.get("acp") or {}
        for base in (_foxos_home() / "agents", SYSTEM_AGENTS):
            f = base / a.get("id", "?") / "foxos-agent.json"
            if f.is_file():
                info = json.loads(f.read_text(encoding="utf-8"))
                ok = os.path.exists(info.get("command", ""))
                return {"ok": ok, "found": info.get("version"), "path": info.get("command")}
        return {"ok": False, "found": None}
    exe = shutil.which(chk[0], path=search_path())
    if not exe:
        return {"ok": False, "found": None}
    try:
        # 第一次运行（新的数据目录要初始化）在忙的机器上可能很慢，版本检查给足时间
        p = subprocess.run([exe, *chk[1:]], capture_output=True, text=True, timeout=float(os.environ.get("FOXOS_RUNTIME_CHECK_TIMEOUT", "240")), env=_env())
        out = (p.stdout or p.stderr or "").strip().splitlines()
        found = out[0].strip() if out else ""
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "found": None, "path": exe, "error": type(e).__name__}
    ok = p.returncode == 0 and (t.get("expect") or "") in found
    return {"ok": ok, "found": found, "path": exe}


def listing(phase: str | None = None, check: bool = True) -> list[dict]:
    out = []
    for t in manifest()["tools"]:
        if phase and t["phase"] != phase:
            continue
        e = {k: t.get(k) for k in ("name", "title", "group", "kind", "phase", "version", "license", "redistributable", "source", "size_mb", "why_not_iso")}
        e["acp"] = (t.get("acp") or {}).get("id")
        if check:
            e.update(status(t))
        out.append(e)
    return out


def doctor() -> dict:
    items = listing()
    problems = [{"tool": i["name"], "phase": i["phase"], "found": i.get("found")} for i in items if i["phase"] == "iso" and not i["ok"]]
    py = {"version": sys.version.split()[0]}
    em = list(Path("/usr/lib").glob("python3*/EXTERNALLY-MANAGED"))
    py["pep668"] = bool(em)
    py["advice"] = tr("runtime.pep668_advice")
    venv = Path("/usr/lib/foxos/venv/bin/python")
    py["foxos_venv"] = str(venv) if venv.exists() else None
    path_ok = str(user_bin()) in os.environ.get("PATH", "").split(os.pathsep)
    try:
        free = shutil.disk_usage(Path.home()).free
    except OSError:
        free = None
    return {"ok": not problems and path_ok, "problems": problems, "python": py, "path_has_local_bin": path_ok, "local_bin": str(user_bin()),
            "disk_free_gb": round(free / 2**30, 1) if free else None, "firstboot_pending": [i["name"] for i in items if i["phase"] == "firstboot" and not i["ok"]],
            "tools": items}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python3 -m foxos.runtime")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("install")
    i.add_argument("names", nargs="*")
    i.add_argument("--phase")
    i.add_argument("--system", action="store_true")
    i.add_argument("--force", action="store_true")
    i.add_argument("--keep-going", action="store_true")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        bad = [x for x in listing() if x["phase"] == "iso" and not x["ok"]]
        for x in listing():
            print(f"{'ok ' if x['ok'] else '-- '} {x['name']:<16} {x['phase']:<9} {x.get('found') or ''}")
        return 1 if bad else 0
    names = a.names or [t["name"] for t in manifest()["tools"] if a.phase and t["phase"] == a.phase]
    rc = 0
    for n in names:
        try:
            r = install(n, system=a.system, force=a.force)
            print(json.dumps({"tool": n, "ok": r.get("ok"), "found": r.get("found")}, ensure_ascii=False), flush=True)
            if not r.get("ok"):
                rc = 1
        except FoxError as e:
            print(json.dumps({"tool": n, "ok": False, "error": e.message}, ensure_ascii=False), flush=True)
            rc = 1
            if not a.keep_going:
                return rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
