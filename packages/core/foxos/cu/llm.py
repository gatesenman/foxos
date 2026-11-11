"""模型调用（OpenAI 兼容的 /chat/completions）：智能体循环与视觉定位共用。

默认 DeepSeek：
- 文字模型 deepseek-v4-pro（只收文字）：配合无障碍快照（网页 / 桌面）就能操作，不需要截图
- 视觉模型 deepseek-flash（DeepSeek-V4.1-Flash，收图片）：截图理解与视觉定位
也可以换成任何 OpenAI 兼容服务：OpenAI、通义千问（DashScope）、智谱、Kimi，或本机 vLLM / Ollama
（例如 UI-TARS-1.5-7B、UI-Venus-1.5-8B、Qwen3-VL 作为视觉定位模型）。

配置在 FOXOS_HOME/computer-model.json；密钥在本地密钥库（secrets.json，0600），名字 model:<provider>:api_key，
也认环境变量 DEEPSEEK_API_KEY / FOXOS_MODEL_API_KEY。密钥不会出现在输出、日志、审计里。
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "model": "deepseek-v4-pro", "vision_model": "deepseek-flash",
                 "env": ["DEEPSEEK_API_KEY"]},
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-5.5", "vision_model": "gpt-5.5", "env": ["OPENAI_API_KEY"]},
    "dashscope": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen3.7-plus", "vision_model": "qwen3-vl-plus",
                  "env": ["DASHSCOPE_API_KEY"]},
    "zhipu": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-5.1", "vision_model": "glm-5v-turbo", "env": ["ZHIPU_API_KEY"]},
    "moonshot": {"base_url": "https://api.moonshot.cn/v1", "model": "kimi-k3", "vision_model": "kimi-k3", "env": ["MOONSHOT_API_KEY"]},
    # 托管的电脑操控模型（都走 OpenAI 兼容的 /chat/completions；原生 computer-use 工具协议未接，见 docs/computer-use-research.md）
    "anthropic": {"base_url": "https://api.anthropic.com/v1", "model": "claude-opus-4-8", "vision_model": "claude-opus-4-8",
                  "env": ["ANTHROPIC_API_KEY"], "note": "Claude computer use; OpenAI-SDK-compatible endpoint"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-3-pro-preview",
               "vision_model": "gemini-3-pro-preview", "env": ["GEMINI_API_KEY"], "note": "Gemini computer use; OpenAI-compatible endpoint"},
    "volcengine": {"base_url": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-1-5-ui-tars-250428",
                   "vision_model": "doubao-1-5-ui-tars-250428", "env": ["ARK_API_KEY"], "note": "Doubao / UI-TARS on Volcengine Ark"},
    "local": {"base_url": "http://127.0.0.1:8000/v1", "model": "", "vision_model": "", "env": []},
}


def custom_providers() -> dict:
    try:
        return json.loads((secrets.home() / "model-providers.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def all_providers() -> dict:
    return {**PROVIDERS, **custom_providers()}


def is_local_url(url: str | None) -> bool:
    return bool(url) and any(h in url for h in ("127.0.0.1", "localhost", "[::1]"))
GROUNDING_KINDS = ("auto", "vlm", "ui-tars", "omniparser", "typesafe", "none")
DEFAULT = {"provider": "deepseek", "base_url": None, "model": None, "vision_model": None, "vision": "auto",
           "grounding": {"kind": "auto", "base_url": None, "model": None}, "max_steps": 30}


def _path() -> Path:
    return secrets.home() / "computer-model.json"


def load() -> dict:
    try:
        d = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    cfg = {**DEFAULT, **{k: v for k, v in d.items() if v is not None}}
    cfg["grounding"] = {**DEFAULT["grounding"], **(d.get("grounding") or {})}
    prov = all_providers().get(cfg["provider"], PROVIDERS["local"])
    cfg["base_url"] = (cfg.get("base_url") or prov["base_url"]).rstrip("/")
    cfg["model"] = cfg.get("model") or prov["model"]
    cfg["vision_model"] = cfg.get("vision_model") if cfg.get("vision_model") is not None else prov["vision_model"]
    return cfg


def save(patch: dict) -> dict:
    try:
        d = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    for k, v in patch.items():
        if k == "grounding":
            d["grounding"] = {**(d.get("grounding") or {}), **{kk: vv for kk, vv in v.items() if vv is not None}}
        elif isinstance(v, dict) and isinstance(d.get(k), dict):
            d[k] = {**d[k], **{kk: vv for kk, vv in v.items() if vv is not None}}
        elif v is not None:
            d[k] = v
    _path().parent.mkdir(parents=True, exist_ok=True)
    _path().write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return load()


def reset_keys(keys: list[str]) -> None:
    try:
        d = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    for k in keys:
        d.pop(k, None)
    _path().write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def key_name(provider: str) -> str:
    return f"model:{provider}:api_key"


def api_key(cfg: dict) -> str | None:
    k = secrets.get(key_name(cfg["provider"])) if hasattr(secrets, "get") else None
    if k:
        return k
    for e in all_providers().get(cfg["provider"], {}).get("env", []) + ["FOXOS_MODEL_API_KEY"]:
        if os.environ.get(e):
            return os.environ[e]
    return None


def has_key(cfg: dict | None = None) -> bool:
    cfg = cfg or load()
    return bool(api_key(cfg)) or cfg["provider"] == "local"


def vision_enabled(cfg: dict) -> bool:
    if cfg.get("vision") == "off":
        return False
    return bool(cfg.get("vision_model"))


def public(cfg: dict) -> dict:
    k = api_key(cfg)
    return {**cfg, "api_key": (f"…{k[-4:]}" if k else None), "vision_enabled": vision_enabled(cfg)}


def image_part(png: bytes, mime: str = "image/png") -> dict:
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64," + base64.b64encode(png).decode()}}


def chat(messages: list[dict], tools: list[dict] | None = None, *, vision: bool = False, cfg: dict | None = None,
         model: str | None = None, base_url: str | None = None, timeout: float = 180.0, temperature: float | None = None,
         retries: int = 2, extra: dict | None = None) -> dict:
    """返回 {"message": 助手消息（原样，含 reasoning_content / tool_calls）, "usage", "model", "seconds"}。"""
    cfg = cfg or load()
    m = model or (cfg["vision_model"] if vision else cfg["model"])
    if not m:
        raise FoxError("DEPENDENCY_MISSING", tr("cu.no_model"), hint="foxos computer model set --provider deepseek")
    local = cfg["provider"] == "local" or is_local_url(base_url) or all_providers().get(cfg["provider"], {}).get("keyless")
    key = None if (is_local_url(base_url) and base_url != cfg.get("base_url")) else api_key(cfg)
    if not key and not local:
        raise FoxError("DEPENDENCY_MISSING", tr("cu.no_key", cfg["provider"]), hint=f"foxos computer model key --value-stdin  # {cfg['provider']}")
    body: dict = {"model": m, "messages": messages}
    if tools:
        body["tools"] = tools
    if temperature is not None:
        body["temperature"] = temperature
    if extra:
        body.update(extra)
    hdr = {"Content-Type": "application/json"}
    if key:
        hdr["Authorization"] = f"Bearer {key}"
    url = (base_url or cfg["base_url"]).rstrip("/") + "/chat/completions"
    t0 = time.time()
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=hdr, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — 用户配置的模型服务
                data = json.loads(r.read().decode("utf-8"))
            msg = data["choices"][0]["message"]
            return {"message": msg, "usage": data.get("usage") or {}, "model": m, "seconds": round(time.time() - t0, 2),
                    "logprobs": data["choices"][0].get("logprobs")}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            last = FoxError("ERROR", tr("cu.model_http", m, e.code, detail))
            if e.code in (400, 401, 403, 404, 422):
                raise last from None
        except (OSError, ValueError, KeyError, IndexError) as e:
            last = FoxError("DEPENDENCY_MISSING", tr("cu.model_failed", url, e))
        time.sleep(1.5 * (attempt + 1))
    raise last  # type: ignore[misc]


def assistant_for_history(msg: dict) -> dict:
    """把助手消息放回对话历史：保留 tool_calls 与 reasoning_content（DeepSeek 思考模式在同一轮工具调用里需要它）。"""
    out = {"role": "assistant", "content": msg.get("content") or ""}
    if msg.get("tool_calls"):
        out["tool_calls"] = [{"id": c["id"], "type": "function", "function": {"name": c["function"]["name"],
                                                                               "arguments": c["function"].get("arguments") or "{}"}}
                             for c in msg["tool_calls"]]
    if msg.get("reasoning_content"):
        out["reasoning_content"] = msg["reasoning_content"]
    return out
