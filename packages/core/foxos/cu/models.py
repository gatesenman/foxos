"""一键安装的本机电脑操控模型（`foxos model …`）。

目录在 foxos/data/cu-models.json（scripts/gen_model_catalog.py 生成）：只有一个可选的本机视觉模型 UI-TARS-1.5-7B
（Apache-2.0，Q4_K_M GGUF 4.8 GB + mmproj 0.85 GB），给没有无障碍信息的程序做视觉定位。默认不安装。
- 下载：Hugging Face / hf-mirror.com / ModelScope（国内），断点续传（.part + Range），逐文件校验 sha256
- 检查：磁盘空间、内存（CPU 推理）、显存（nvidia-smi）
- 运行：llama.cpp 的 llama-server（MIT，按需下载官方发行包并校验 sha256；CPU / Vulkan / CUDA 自动选），
        有 GPU 且装了 vLLM 时可用 vLLM（原始权重）
- 注册：`foxos model use ui-tars-1.5-7b` 把它设为视觉定位（computer model 的 grounding = ui-tars）
模型权重放在 FOXOS_HOME/models/<id>/，不打进系统镜像。
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

CATALOG = Path(__file__).resolve().parents[1] / "data" / "cu-models.json"
SOURCES = ("hf", "hf-mirror", "modelscope")


def catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def entry(mid: str) -> dict:
    for m in catalog()["models"]:
        if m["id"] == mid:
            return m
    raise FoxError("NOT_FOUND", tr("mdl.unknown", mid), hint="foxos model catalog")


def root() -> Path:
    return secrets.home() / "models"


def mdir(mid: str) -> Path:
    return root() / mid


def runtime_dir() -> Path:
    return secrets.home() / "tools" / "llama.cpp"


# ---------- 硬件 ----------

def meminfo() -> dict:
    out = {}
    try:
        for ln in Path("/proc/meminfo").read_text().splitlines():
            k, v = ln.split(":", 1)
            out[k] = int(v.split()[0]) * 1024
    except OSError:
        pass
    return {"total": out.get("MemTotal", 0), "available": out.get("MemAvailable", 0)}


def gpus() -> list[dict]:
    if not shutil.which("nvidia-smi"):
        return []
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return []
    out = []
    for ln in p.stdout.splitlines():
        parts = [x.strip() for x in ln.split(",")]
        if len(parts) == 3 and parts[1].isdigit():
            out.append({"name": parts[0], "vram_total": int(parts[1]) * 2**20, "vram_free": int(parts[2]) * 2**20})
    return out


def hardware() -> dict:
    return {"cpu_count": os.cpu_count(), "arch": platform.machine(), "memory": meminfo(), "gpus": gpus(),
            "disk_free": shutil.disk_usage(str(secrets.home() if secrets.home().exists() else Path.home())).free,
            "vllm": bool(shutil.which("vllm"))}


def check(m: dict, backend: str = "llama.cpp") -> dict:
    """返回 {ok, problems[], warnings[]}：磁盘按还没下载的字节数算，内存/显存按目录里的估计。"""
    hw = hardware()
    need = sum(f["size"] for f in m["files"]) - sum(_have(m, f) for f in m["files"])
    probs, warns = [], []
    if need > 0 and hw["disk_free"] < need * 1.1 + 512 * 2**20:
        probs.append(tr("mdl.no_disk", _gb(need), _gb(hw["disk_free"])))
    ram = m["ram_gb"] * 1e9
    if backend == "vllm":
        if not hw["gpus"]:
            probs.append(tr("mdl.no_gpu"))
        elif max(g["vram_total"] for g in hw["gpus"]) < m["vram_gb_vllm_bf16"] * 1e9:
            probs.append(tr("mdl.no_vram", m["vram_gb_vllm_bf16"], _gb(max(g["vram_total"] for g in hw["gpus"]))))
    else:
        if hw["memory"]["total"] and hw["memory"]["total"] < ram:
            probs.append(tr("mdl.no_ram", m["ram_gb"], _gb(hw["memory"]["total"])))
        elif hw["memory"]["available"] and hw["memory"]["available"] < ram:
            warns.append(tr("mdl.low_ram", m["ram_gb"], _gb(hw["memory"]["available"])))
    return {"ok": not probs, "problems": probs, "warnings": warns, "download_bytes": max(0, need), "hardware": hw}


def _gb(n: float) -> str:
    return f"{n / 1e9:.1f} GB"


# ---------- 下载 ----------

def _url(src: str, repo: str, name: str) -> str:
    if src == "hf":
        return f"https://huggingface.co/{repo}/resolve/main/{name}"
    if src == "hf-mirror":
        return f"https://hf-mirror.com/{repo}/resolve/main/{name}"
    return f"https://modelscope.cn/models/{repo}/resolve/master/{name}"


def source_order(m: dict, source: str = "auto") -> list[str]:
    if source != "auto":
        if source == "modelscope" and not m.get("modelscope"):
            raise FoxError("USAGE", tr("mdl.no_modelscope", m["id"]))
        return [source]
    env = os.environ.get("FOXOS_MODEL_SOURCE")
    if env in SOURCES:
        return [env] + [s for s in SOURCES if s != env and (s != "modelscope" or m.get("modelscope"))]
    from .. import i18n
    china = i18n.get_lang().lower().startswith("zh")
    order = ["modelscope", "hf-mirror", "hf"] if china else ["hf", "hf-mirror", "modelscope"]
    return [s for s in order if s != "modelscope" or m.get("modelscope")]


def _have(m: dict, f: dict) -> int:
    p = mdir(m["id"]) / f["name"]
    if p.exists():
        return p.stat().st_size
    part = p.with_name(p.name + ".part")
    return part.stat().st_size if part.exists() else 0


def sha256_file(p: Path, h=None) -> str:
    h = h or hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, size: int, sha256: str, progress=None, timeout: float = 60) -> dict:
    """断点续传：已有 .part 就从它的长度接着下（Range），下完校验 sha256，再改名。校验不对删掉 .part 报错。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == size:
        return {"file": dest.name, "skipped": True}
    part = dest.with_name(dest.name + ".part")
    have = part.stat().st_size if part.exists() else 0
    if have > size:
        part.unlink()
        have = 0
    h = hashlib.sha256()
    if have:
        sha256_file(part, h)
    resumed = have
    t0 = time.time()
    if have < size:
        req = urllib.request.Request(url, headers={"User-Agent": "foxos-model/1", **({"Range": f"bytes={have}-"} if have else {})})
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — 目录里固定的模型仓库地址
            if have and r.status != 206:  # 服务器不支持续传：从头来
                have, resumed, h = 0, 0, hashlib.sha256()
                mode = "wb"
            else:
                mode = "ab"
            last = 0.0
            with open(part, mode) as out:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    h.update(chunk)
                    have += len(chunk)
                    if progress and time.time() - last > 1:
                        last = time.time()
                        progress(dest.name, have, size)
    if have != size:
        raise FoxError("ERROR", tr("mdl.short", dest.name, have, size))
    got = h.hexdigest()
    if got != sha256:
        part.unlink(missing_ok=True)
        raise FoxError("ERROR", tr("mdl.bad_sha", dest.name, got[:12], sha256[:12]))
    part.rename(dest)
    return {"file": dest.name, "bytes": size, "resumed_from": resumed, "seconds": round(time.time() - t0, 1), "sha256": got}


def install(mid: str, source: str = "auto", force: bool = False, progress=None) -> dict:
    m = entry(mid)
    chk = check(m)
    if not chk["ok"] and not force:
        raise FoxError("DEPENDENCY_MISSING", "; ".join(chk["problems"]), hint=tr("mdl.force_hint"))
    t0 = time.time()
    rt = ensure_runtime(progress=progress)
    files, errors = [], []
    for f in m["files"]:
        for src in source_order(m, source):
            repo = m["modelscope"] if src == "modelscope" else m["gguf_repo"]
            try:
                r = download(_url(src, repo, f["name"]), mdir(mid) / f["name"], f["size"], f["sha256"], progress)
                files.append({**r, "source": src})
                break
            except (OSError, urllib.error.URLError, FoxError) as e:
                errors.append(f"{src}: {f['name']}: {e}")
        else:
            raise FoxError("ERROR", tr("mdl.download_failed", f["name"], " | ".join(errors[-3:])))
    meta = {"id": mid, "installed": time.time(), "files": [f["name"] for f in m["files"]], "license": m["license"]}
    (mdir(mid) / "installed.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return {"model": mid, "files": files, "runtime": rt, "warnings": chk["warnings"], "seconds": round(time.time() - t0, 1),
            "license": m["license"], "path": str(mdir(mid))}


def installed() -> list[dict]:
    out = []
    if root().exists():
        for d in sorted(root().iterdir()):
            if (d / "installed.json").exists():
                st = server_state(d.name)
                out.append({"id": d.name, "bytes": sum(p.stat().st_size for p in d.glob("*.gguf")), "server": st})
    return out


def remove(mid: str) -> dict:
    stop(mid)
    d = mdir(mid)
    if not d.exists():
        raise FoxError("NOT_FOUND", tr("mdl.not_installed", mid))
    n = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
    shutil.rmtree(d)
    return {"model": mid, "freed_bytes": n}


# ---------- llama.cpp 运行时 ----------

def runtime_variant() -> str:
    arch = platform.machine().lower()
    if arch in ("aarch64", "arm64"):
        return "cpu-arm64"
    if os.environ.get("FOXOS_LLAMA_VARIANT"):
        return os.environ["FOXOS_LLAMA_VARIANT"]
    if gpus():
        return "cuda-x64"
    return "cpu-x64"


def server_bin() -> Path | None:
    if os.environ.get("FOXOS_LLAMA_SERVER"):
        return Path(os.environ["FOXOS_LLAMA_SERVER"])
    for base in (Path("/usr/lib/foxos/tools/llama.cpp"), runtime_dir()):
        for p in sorted(base.glob("*/llama-server")) + sorted(base.glob("*/*/llama-server")):
            if os.access(p, os.X_OK):
                return p
    w = shutil.which("llama-server")
    return Path(w) if w else None


def ensure_runtime(progress=None) -> dict:
    b = server_bin()
    if b:
        return {"llama_server": str(b), "downloaded": False}
    lc = catalog()["llama_cpp"]
    var = runtime_variant()
    name, sha = lc["assets"][var]
    url = f"https://github.com/ggml-org/llama.cpp/releases/download/{lc['tag']}/{name}"
    dest = runtime_dir() / name
    size = _remote_size(url)
    download(url, dest, size, sha, progress)
    out = runtime_dir() / f"{lc['tag']}-{var}"
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dest) as tf:
        tf.extractall(out, filter="data")  # noqa: S202 — sha256 已校验的官方发行包
    dest.unlink()
    b = server_bin()
    if not b:
        raise FoxError("ERROR", tr("mdl.no_server_bin", str(out)))
    return {"llama_server": str(b), "downloaded": True, "tag": lc["tag"], "variant": var, "license": lc["license"]}


def _remote_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "foxos-model/1"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        return int(r.headers["Content-Length"])


# ---------- 服务 ----------

def _state_path(mid: str) -> Path:
    return mdir(mid) / "server.json"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def server_state(mid: str) -> dict | None:
    try:
        st = json.loads(_state_path(mid).read_text())
    except (OSError, ValueError):
        return None
    if st.get("pid") and not _alive(st["pid"]):
        return {**st, "running": False}
    return {**st, "running": True}


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _health(base: str, timeout: float = 3) -> bool:
    try:
        with urllib.request.urlopen(base.rsplit("/v1", 1)[0] + "/health", timeout=timeout) as r:  # noqa: S310 — 本机
            return r.status == 200
    except (OSError, ValueError):
        return False


def run(mid: str, backend: str = "auto", port: int | None = None, ctx_size: int = 8192, threads: int | None = None,
        wait: float = 600) -> dict:
    m = entry(mid)
    st = server_state(mid)
    if st and st.get("running") and _health(st["base_url"]):
        return {**st, "already_running": True}
    if backend == "auto":
        backend = "vllm" if (shutil.which("vllm") and gpus()) else "llama.cpp"
    port = port or _free_port()
    log = mdir(mid) / "server.log"
    mdir(mid).mkdir(parents=True, exist_ok=True)
    if backend == "llama.cpp":
        if not (mdir(mid) / "installed.json").exists():
            raise FoxError("NOT_FOUND", tr("mdl.not_installed", mid), hint=f"foxos model install {mid}")
        b = server_bin() or Path(ensure_runtime()["llama_server"])
        files = {f["role"]: mdir(mid) / f["name"] for f in m["files"]}
        argv = [str(b), "-m", str(files["model"]), "--host", "127.0.0.1", "--port", str(port), "-c", str(ctx_size),
                "--alias", mid, "--jinja", "--no-webui", "-t", str(threads or max(1, (os.cpu_count() or 2) - 1))]
        if "mmproj" in files:
            argv += ["--mmproj", str(files["mmproj"])]
        if gpus():
            argv += ["-ngl", "999"]
        env = {**os.environ, "LD_LIBRARY_PATH": f"{b.parent}:{os.environ.get('LD_LIBRARY_PATH', '')}"}
        model_name = mid
    elif backend == "vllm":
        chk = check(m, "vllm")
        if not chk["ok"]:
            raise FoxError("DEPENDENCY_MISSING", "; ".join(chk["problems"]))
        argv = ["vllm", "serve", m["source_repo"], "--host", "127.0.0.1", "--port", str(port), "--served-model-name", mid,
                "--max-model-len", str(ctx_size)]
        env = dict(os.environ)
        model_name = mid
    else:
        raise FoxError("USAGE", tr("mdl.bad_backend", backend))
    t0 = time.time()
    with open(log, "ab") as lf:
        p = subprocess.Popen(argv, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, start_new_session=True)
    base = f"http://127.0.0.1:{port}/v1"
    st = {"id": mid, "backend": backend, "base_url": base, "model": model_name, "pid": p.pid, "port": port,
          "started": time.time(), "argv": argv[:1] + ["…"], "log": str(log)}
    _state_path(mid).write_text(json.dumps(st, indent=1))
    while time.time() - t0 < wait:
        if p.poll() is not None:
            tail = log.read_text(errors="replace")[-800:] if log.exists() else ""
            raise FoxError("ERROR", tr("mdl.server_died", mid, tail))
        if _health(base):
            return {**st, "running": True, "load_seconds": round(time.time() - t0, 1)}
        time.sleep(1.0)
    raise FoxError("ERROR", tr("mdl.server_timeout", mid, int(wait)))


def stop(mid: str) -> dict:
    st = server_state(mid)
    if not st or not st.get("pid"):
        return {"model": mid, "stopped": False}
    if st.get("running"):
        try:
            os.killpg(st["pid"], signal.SIGTERM)
        except OSError:
            pass
        for _ in range(50):
            if not _alive(st["pid"]):
                break
            time.sleep(0.1)
        else:
            try:
                os.killpg(st["pid"], signal.SIGKILL)
            except OSError:
                pass
    _state_path(mid).unlink(missing_ok=True)
    return {"model": mid, "stopped": True}


def endpoint(mid: str) -> dict:
    st = server_state(mid)
    if not st or not st.get("running"):
        raise FoxError("DEPENDENCY_MISSING", tr("mdl.not_running", mid), hint=f"foxos model run {mid}")
    return st
