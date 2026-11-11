"""本地密钥库：ACP 智能体的 API 密钥、连接器令牌、配对令牌。

存在 FOXOS_HOME/secrets.json（目录 0700、文件 0600，只有当前用户能读），不在工作空间里，
不进审计（命令参数标为 secret，审计写 ***），也不会出现在任何命令的输出里（只返回名字和末四位）。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .errors import FoxError
from .i18n import tr


def home() -> Path:
    from .desktop_client import foxos_home
    return foxos_home()


def _path() -> Path:
    return home() / "secrets.json"


def _load() -> dict:
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(d: dict) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p.parent, 0o700)
    except OSError:
        pass
    tmp = p.with_name(f".secrets.{os.getpid()}.tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(d, f)
    os.replace(tmp, p)


def _check_name(name: str) -> str:
    if not name or len(name) > 200 or any(c in name for c in "\n\r\x00"):
        raise FoxError("USAGE", tr("secrets.bad_name"))
    return name


def put(name: str, value: str) -> dict:
    _check_name(name)
    if not isinstance(value, str) or not value:
        raise FoxError("USAGE", tr("secrets.empty_value"))
    d = _load()
    d[name] = {"value": value, "updated": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    _save(d)
    return describe(name, d[name])


def get(name: str) -> str | None:
    v = _load().get(name)
    return v.get("value") if isinstance(v, dict) else None


def delete(name: str) -> bool:
    d = _load()
    if name in d:
        del d[name]
        _save(d)
        return True
    return False


def describe(name: str, v: dict) -> dict:
    val = v.get("value", "")
    return {"name": name, "hint": ("…" + val[-4:]) if len(val) >= 8 else "…", "updated": v.get("updated")}


def names(prefix: str = "") -> list[dict]:
    return [describe(k, v) for k, v in sorted(_load().items()) if k.startswith(prefix)]


def env_for(prefix: str) -> dict:
    """前缀下形如 <prefix><ENV_NAME> 的密钥 → 环境变量（例如 acp:codex-acp:OPENAI_API_KEY）。"""
    out = {}
    for k, v in _load().items():
        if k.startswith(prefix) and isinstance(v, dict):
            env = k[len(prefix):]
            if env and env.replace("_", "").isalnum() and env.upper() == env:
                out[env] = v.get("value", "")
    return out
