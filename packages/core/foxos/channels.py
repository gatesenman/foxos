"""频道（OpenBot 的「Reaching you」）：在聊天窗口以外和智能体对话。

- telegram：用你自己的 Telegram 机器人令牌（@BotFather 创建）。`foxos bot channel poll` 读取新消息（getUpdates），
  交给该智能体，再把回答发回同一个会话（sendMessage）。只回答 --chat 指定的会话（默认第一个发消息的会话，之后锁定）。
- webhook：生成一个随机令牌；`foxos bot serve` 接收 POST /hooks/<智能体>/<令牌> {"text": …}，同步返回回答。
令牌存在本地密钥库。
"""

from __future__ import annotations

import json
import secrets as pysecrets
import urllib.parse
import urllib.request

from . import bots, secrets
from .errors import FoxError
from .i18n import tr


def configure(ws, ref: str, kind: str, token: str | None, chat: str | None) -> dict:
    b = bots.get(ws, ref)
    ch = dict(b.get("channels") or {})
    if kind == "telegram":
        if not token:
            raise FoxError("USAGE", tr("channels.token_required"))
        me = _tg(token, "getMe")
        secrets.put(f"bot:{b['id']}:telegram", token)
        ch["telegram"] = {"username": me.get("username"), "chat": chat, "offset": 0}
        out = {"kind": "telegram", "username": me.get("username")}
    else:
        tok = pysecrets.token_urlsafe(24)
        secrets.put(f"bot:{b['id']}:webhook", tok)
        ch["webhook"] = {"path": f"/hooks/{b['id']}/"}
        out = {"kind": "webhook", "path": f"/hooks/{b['id']}/{tok}", "note": tr("channels.webhook_note")}
    bots.update(ws, b["id"], {"channels": ch})
    return {"bot": b["id"], **out}


def remove(ws, ref: str, kind: str) -> dict:
    b = bots.get(ws, ref)
    ch = dict(b.get("channels") or {})
    ch.pop(kind, None)
    secrets.delete(f"bot:{b['id']}:{kind}")
    bots.update(ws, b["id"], {"channels": ch})
    return {"bot": b["id"], "removed": kind}


def _tg(token: str, method: str, params: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params or {}).encode() if params else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=40) as r:
            j = json.loads(r.read().decode())
    except OSError as e:
        raise FoxError("DEPENDENCY_MISSING", tr("channels.telegram_unreachable", type(e).__name__)) from None
    if not j.get("ok"):
        raise FoxError("PERMISSION_DENIED", tr("channels.telegram_error", j.get("description")))
    return j["result"]


def poll(ws, ref: str | None = None) -> dict:
    out = []
    for b in bots.all_bots(ws):
        if ref and b["id"] != bots.get(ws, ref)["id"]:
            continue
        tg = (b.get("channels") or {}).get("telegram")
        tok = secrets.get(f"bot:{b['id']}:telegram")
        if not tg or not tok:
            continue
        ups = _tg(tok, "getUpdates", {"offset": tg.get("offset", 0), "timeout": 0})
        for u in ups:
            tg["offset"] = u["update_id"] + 1
            msg = u.get("message") or {}
            chat = str((msg.get("chat") or {}).get("id"))
            if not msg.get("text"):
                continue
            if tg.get("chat") and tg["chat"] != chat:
                continue
            tg["chat"] = chat
            r = bots.run_turn(ws, b["id"], msg["text"], actor=f"telegram:{(msg.get('from') or {}).get('username') or chat}", origin="channel")
            _tg(tok, "sendMessage", {"chat_id": chat, "text": r["text"][:4000] or "…"})
            out.append({"bot": b["id"], "chat": chat, "message": r["id"]})
        ch = dict(b.get("channels") or {})
        ch["telegram"] = tg
        bots.update(ws, b["id"], {"channels": ch})
    return {"handled": len(out), "messages": out}
