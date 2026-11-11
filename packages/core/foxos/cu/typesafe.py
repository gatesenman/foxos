"""TypeSafe AI 的 System One API（Jev）客户端：按官方 OpenAPI（https://api.typesafe.ai/openapi.json，2026-11 读取）实现。

Jev 不生成文字：给它状态（state，文字 / JSON / 图片）和一组有类型的问题，一次请求并行返回：
- choice  从最多 255 个选项里选一个 → choice、probabilities（每个选项）、confidence
- score   按 ≤10 个有序等级打分 → score（期望值）、probabilities、confidence
- noul    是 / 否 → noul（为「是」的概率 0–1）
- box     图片里的位置（Jev 1.14，需请求头 TypeSafe-Danger-Zone-Images: true）→ box{top,bottom,left,right}（0–1）、confidence
POST {base}/v1/systemone，Authorization: Bearer <key>；GET /v1/models 列模型（jev-latest / jev-preview / jev-1.14.0）。
429 / 529 按指数退避重试（与官方 SDK 一致，遵守 retry-after）。密钥在本地密钥库 model:typesafe:api_key，或环境变量 TYPESAFE_API_KEY。
不依赖官方 SDK（typesafe-sdk）：只用标准库，便于在系统镜像里直接用。
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request

from .. import secrets
from ..errors import FoxError
from ..i18n import tr

BASE = "https://api.typesafe.ai"
MODEL = "jev-latest"
MAX_CHOICES = 255
MAX_SCORE_LEVELS = 10
KEY_NAME = "model:typesafe:api_key"


def api_key() -> str | None:
    return secrets.get(KEY_NAME) or os.environ.get("TYPESAFE_API_KEY")


def choice(instructions, criteria: dict) -> dict:
    if not 1 <= len(criteria) <= MAX_CHOICES:
        raise FoxError("USAGE", tr("ts.too_many_choices", len(criteria), MAX_CHOICES))
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def score(instructions, levels: list) -> dict:
    if not 1 <= len(levels) <= MAX_SCORE_LEVELS:
        raise FoxError("USAGE", tr("ts.bad_levels", MAX_SCORE_LEVELS))
    return {"type": "score", "instructions": instructions, "criteria": list(levels)}


def noul(instructions, true: str | None = None, false: str | None = None) -> dict:
    q = {"type": "noul", "instructions": instructions}
    if true or false:
        q["criteria"] = {k: v for k, v in (("true", true), ("false", false)) if v}
    return q


def box(instructions) -> dict:
    return {"type": "box", "instructions": instructions}


def image_asset(png: bytes, fmt: str = "png") -> dict:
    return {"type": "image", "format": fmt, "data_base64": base64.b64encode(png).decode()}


def build_request(state, questions: dict, model: str | None = None, assets: dict | None = None) -> tuple[dict, dict]:
    """返回 (请求体, 额外请求头)。有图片或 box 问题时加 Danger-Zone-Images 头。"""
    if not questions:
        raise FoxError("USAGE", tr("ts.no_questions"))
    body = {"model": model or MODEL, "state": state, "questions": questions}
    hdr = {}
    if assets:
        body["assets"] = assets
    if assets or any(q.get("type") == "box" for q in questions.values()):
        hdr["TypeSafe-Danger-Zone-Images"] = "true"
    return body, hdr


def parse_response(data: dict, questions: dict) -> dict:
    """校验回答与问题一一对应、类型一致；返回 {name: answer}。"""
    ans = data.get("answers")
    if not isinstance(ans, dict):
        raise FoxError("ERROR", tr("ts.bad_response", "answers"))
    for name, q in questions.items():
        a = ans.get(name)
        if not isinstance(a, dict) or a.get("type") != q["type"]:
            raise FoxError("ERROR", tr("ts.bad_response", name))
        if q["type"] == "choice" and a.get("choice") not in q["criteria"]:
            raise FoxError("ERROR", tr("ts.bad_response", name))
    return ans


class Client:
    def __init__(self, key: str | None = None, base_url: str | None = None, model: str | None = None, timeout: float = 30.0,
                 retries: int = 3, opener=None):
        self.key = key or api_key()
        self.base = (base_url or os.environ.get("TYPESAFE_BASE_URL") or BASE).rstrip("/")
        self.model = model or MODEL
        self.timeout, self.retries = timeout, retries
        self._open = opener or urllib.request.urlopen  # 测试时注入假的传输层

    def _req(self, method: str, path: str, body: dict | None = None, headers: dict | None = None) -> dict:
        if not self.key:
            raise FoxError("DEPENDENCY_MISSING", tr("ts.no_key"), hint="foxos model provider add typesafe --key-stdin")
        hdr = {"Authorization": f"Bearer {self.key}", "Accept": "application/json", "User-Agent": "foxos-typesafe/1", **(headers or {})}
        data = None
        if body is not None:
            hdr["Content-Type"] = "application/json"
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        last = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(self.base + path, data=data, headers=hdr, method=method)
            try:
                with self._open(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:400]
                last = FoxError("PERMISSION_DENIED" if e.code == 401 else "ERROR", tr("ts.http", e.code, detail))
                if e.code not in (429, 529, 500, 502, 503, 504):
                    raise last from None
                ra = e.headers.get("retry-after") if e.headers else None
                delay = float(ra) if ra and ra.replace(".", "", 1).isdigit() else 0.5 * 2 ** attempt
            except (OSError, ValueError) as e:
                last = FoxError("DEPENDENCY_MISSING", tr("ts.conn", self.base, e))
                delay = 0.5 * 2 ** attempt
            if attempt < self.retries:
                time.sleep(min(delay, 8))
        raise last  # type: ignore[misc]

    def models(self) -> list[dict]:
        return self._req("GET", "/v1/models").get("models") or []

    def ask(self, state, questions: dict, assets: dict | None = None, model: str | None = None) -> dict:
        body, hdr = build_request(state, questions, model or self.model, assets)
        t0 = time.time()
        data = self._req("POST", "/v1/systemone", body, hdr)
        return {"answers": parse_response(data, questions), "model": data.get("model"), "usage": data.get("usage") or {},
                "seconds": round(time.time() - t0, 3)}
