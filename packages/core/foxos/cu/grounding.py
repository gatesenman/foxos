"""视觉定位：用一句话描述找到屏幕上的元素坐标（没有无障碍信息的程序、画布、游戏、远程桌面时用）。

三种方式（`foxos computer model set --grounding …`）：
- vlm        通用视觉模型（默认 DeepSeek deepseek-flash；也可 Qwen3-VL、GPT、Gemini），回 0–1000 归一化坐标
- ui-tars    UI-TARS-1.5-7B / UI-Venus-1.5 等 GUI 专用定位模型，用 vLLM / Ollama 以 OpenAI 兼容接口在本机或局域网提供
             （ScreenSpot-Pro：UI-TARS-1.5-7B 61.6%，UI-Venus-1.5-8B 68.4%；7–8B 需要约 16–20 GB 显存，量化后 8 GB 左右）
- typesafe   TypeSafe Jev 1.14 的 Box 问题（托管 API，需要提前体验资格的密钥）：回元素的框（0–1 比例）和置信度
- 本机一键模型（`foxos model install gui-owl-1.5-2b && foxos model use gui-owl-1.5-2b --as grounding`）：Qwen3-VL 系（GUI-Owl、
             UI-Venus、MAI-UI、Holo2、Qwen3.5）用 vlm（0–1000 坐标），UI-TARS-1.5 / Jedi 用 ui-tars（缩放后像素）
- omniparser Microsoft OmniParser v2 服务（omnitool 的 omniparserserver，HTTP /parse/）：把截图解析成带编号的元素列表，
             这样纯文字模型（DeepSeek v4 pro）也能按编号挑元素
权重都不打进系统镜像；需要时按 docs/computer-use-research.md 的说明单独下载。
"""

from __future__ import annotations

import base64
import json
import uuid
import math
import re
import struct
import urllib.request

from ..errors import FoxError
from ..i18n import tr
from . import llm


def png_size(png: bytes) -> tuple[int, int]:
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise FoxError("ERROR", tr("cu.not_png"))
    w, h = struct.unpack(">II", png[16:24])
    return w, h


def _json_point(text: str) -> tuple[float, float] | None:
    m = re.search(r"\{[^{}]*\}", text or "")
    if m:
        try:
            d = json.loads(m.group(0))
            if "x" in d and "y" in d:
                return float(d["x"]), float(d["y"])
            if "point" in d:
                return float(d["point"][0]), float(d["point"][1])
        except (ValueError, TypeError, KeyError, IndexError):
            pass
    m = re.search(r"\(?\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)?", text or "")
    if m:
        return float(m.group(1)), float(m.group(2))
    return None


def smart_resize(h: int, w: int, factor: int = 28, min_pixels: int = 100 * 28 * 28, max_pixels: int = 16384 * 28 * 28) -> tuple[int, int]:
    """Qwen2.5-VL / UI-TARS-1.5 的图片缩放规则：模型回的坐标是缩放后图片上的像素。"""
    hb, wb = max(factor, round(h / factor) * factor), max(factor, round(w / factor) * factor)
    if hb * wb > max_pixels:
        beta = math.sqrt((h * w) / max_pixels)
        hb, wb = math.floor(h / beta / factor) * factor, math.floor(w / beta / factor) * factor
    elif hb * wb < min_pixels:
        beta = math.sqrt(min_pixels / (h * w))
        hb, wb = math.ceil(h * beta / factor) * factor, math.ceil(w * beta / factor) * factor
    return hb, wb


def ground_vlm(png: bytes, description: str, cfg: dict) -> dict:
    w, h = png_size(png)
    g = cfg.get("grounding") or {}
    prompt = tr("cu.ground_prompt", w, h, description)
    local = llm.is_local_url(g.get("base_url"))
    r = llm.chat([{"role": "user", "content": [{"type": "text", "text": prompt}, llm.image_part(png)]}], vision=True, cfg=cfg,
                 model=g.get("model") or None, base_url=g.get("base_url") or None, timeout=600 if local else 120,
                 temperature=0 if local else None, extra={"chat_template_kwargs": {"enable_thinking": False}} if local else None)
    text = r["message"].get("content") or ""
    if "not_found" in text.lower() or "not found" in text.lower():
        raise FoxError("NOT_FOUND", tr("cu.ground_not_found", description))
    p = _json_point(text)
    if not p:
        raise FoxError("ERROR", tr("cu.ground_unparsed", text[:200]))
    x, y = round(p[0] / 1000 * w), round(p[1] / 1000 * h)
    return {"x": x, "y": y, "kind": "vlm", "model": r["model"], "raw": text[:200], "screen": [w, h], "seconds": r["seconds"]}


def ground_uitars(png: bytes, description: str, cfg: dict) -> dict:
    w, h = png_size(png)
    g = cfg.get("grounding") or {}
    if not g.get("base_url") or not g.get("model"):
        raise FoxError("DEPENDENCY_MISSING", tr("cu.uitars_not_configured"),
                       hint="foxos computer model set --grounding ui-tars --grounding-url http://127.0.0.1:8000/v1 --grounding-model ByteDance-Seed/UI-TARS-1.5-7B")
    prompt = ("Output only the coordinate of one point in your response. What element matches the following task: " + description)
    local = llm.is_local_url(g["base_url"])
    r = llm.chat([{"role": "user", "content": [{"type": "text", "text": prompt}, llm.image_part(png)]}], cfg=cfg,
                 model=g["model"], base_url=g["base_url"], vision=True, timeout=600 if local else 120, temperature=0 if local else None)
    text = r["message"].get("content") or ""
    p = _json_point(text.replace("<|box_start|>", "").replace("<|box_end|>", ""))
    if not p:
        raise FoxError("ERROR", tr("cu.ground_unparsed", text[:200]))
    rh, rw = smart_resize(h, w)
    x, y = round(p[0] / rw * w), round(p[1] / rh * h)
    return {"x": x, "y": y, "kind": "ui-tars", "model": r["model"], "raw": text[:200], "screen": [w, h], "seconds": r["seconds"]}


def omniparser_parse(png: bytes, cfg: dict) -> list[dict]:
    g = cfg.get("grounding") or {}
    base = (g.get("base_url") or "http://127.0.0.1:8000").rstrip("/")
    req = urllib.request.Request(base + "/parse/", data=json.dumps({"base64_image": base64.b64encode(png).decode()}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310 — 用户配置的本机服务
            data = json.loads(r.read().decode("utf-8"))
    except OSError as e:
        raise FoxError("DEPENDENCY_MISSING", tr("cu.omniparser_down", base, e), hint="docs/computer-use-research.md#omniparser") from e
    w, h = png_size(png)
    out = []
    for i, el in enumerate(data.get("parsed_content_list") or []):
        x1, y1, x2, y2 = el.get("bbox") or [0, 0, 0, 0]
        if max(x1, y1, x2, y2) <= 1.0:
            x1, x2, y1, y2 = x1 * w, x2 * w, y1 * h, y2 * h
        out.append({"id": i, "type": el.get("type"), "content": el.get("content"), "interactive": el.get("interactivity"),
                    "x": round((x1 + x2) / 2), "y": round((y1 + y2) / 2), "bbox": [round(x1), round(y1), round(x2 - x1), round(y2 - y1)]})
    return out


def ground_omniparser(png: bytes, description: str, cfg: dict) -> dict:
    els = omniparser_parse(png, cfg)
    listing = "\n".join(f"{e['id']}: [{e['type']}] {e['content']}" for e in els)
    r = llm.chat([{"role": "user", "content": tr("cu.omni_pick", description, listing)}], cfg=cfg, timeout=120)
    text = r["message"].get("content") or ""
    m = re.search(r"-?\d+", text)
    if not m or int(m.group(0)) < 0 or int(m.group(0)) >= len(els):
        raise FoxError("NOT_FOUND", tr("cu.ground_not_found", description))
    e = els[int(m.group(0))]
    return {"x": e["x"], "y": e["y"], "kind": "omniparser", "element": e, "model": r["model"], "screen": list(png_size(png))}


def ground_typesafe(png: bytes, description: str, cfg: dict) -> dict:
    from . import typesafe
    w, h = png_size(png)
    g = cfg.get("grounding") or {}
    c = typesafe.Client(model=g.get("model") or "jev-latest")
    ph = "img-" + uuid.uuid4().hex  # 占位符：state 里出现的地方会被图片替换，所以要用不会撞上普通文字的 uuid
    r = c.ask(ph, {"target": typesafe.box("Locate this UI element in the image: " + description)},
              assets={ph: typesafe.image_asset(png)})
    a = r["answers"]["target"]
    b = a["box"]
    x, y = round((b["left"] + b["right"]) / 2 * w), round((b["top"] + b["bottom"]) / 2 * h)
    return {"x": x, "y": y, "kind": "typesafe", "model": r["model"], "box": b, "confidence": a.get("confidence"),
            "screen": [w, h], "seconds": r["seconds"]}


def ground(png: bytes, description: str, cfg: dict | None = None, kind: str | None = None) -> dict:
    cfg = cfg or llm.load()
    k = kind or (cfg.get("grounding") or {}).get("kind") or "auto"
    if k == "auto":  # 默认：有 TypeSafe 密钥 → Jev Box；本地 UI-TARS 在跑 → UI-TARS；否则视觉模型
        from . import typesafe
        if typesafe.api_key():
            k = "typesafe"
        else:
            try:
                from . import models
                ep = models.endpoint("ui-tars-1.5-7b")
            except Exception:  # noqa: BLE001
                ep = None
            if ep:
                cfg = {**cfg, "grounding": {**(cfg.get("grounding") or {}), "kind": "ui-tars", "base_url": ep.get("base_url"),
                                            "model": ep.get("model")}}
                k = "ui-tars"
            else:
                k = "vlm"
    if k == "none":
        raise FoxError("DEPENDENCY_MISSING", tr("cu.grounding_off"))
    if k == "vlm":
        if not llm.vision_enabled(cfg) and not (cfg.get("grounding") or {}).get("model"):
            raise FoxError("DEPENDENCY_MISSING", tr("cu.no_vision"), hint="foxos computer model set --vision-model deepseek-flash")
        return ground_vlm(png, description, cfg)
    if k == "ui-tars":
        return ground_uitars(png, description, cfg)
    if k == "omniparser":
        return ground_omniparser(png, description, cfg)
    if k == "typesafe":
        return ground_typesafe(png, description, cfg)
    raise FoxError("USAGE", tr("cu.bad_grounding", ", ".join(llm.GROUNDING_KINDS)))
