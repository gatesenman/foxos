"""界面语言：命令行 / MCP / 内核消息的多语言（简体中文 zh-CN 默认，English en-US）。

词条在 foxos/data/locales/<语言>.json，键名与语言无关；JSON 输出的字段名、错误码始终是英文。
语言来自 --lang（命令行全局选项）或环境变量 FOXOS_LANG，缺省 zh-CN。命令说明在导入时取词，
因此语言必须在导入命令注册表之前确定（cli.py 最先调用 init_from_argv）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

SUPPORTED = ("zh-CN", "en-US")
DEFAULT = "zh-CN"
_DIR = Path(__file__).resolve().parent / "data" / "locales"
_messages: dict[str, dict[str, str]] = {}


def normalize(lang: str | None) -> str | None:
    s = str(lang or "").strip().replace("_", "-").lower()
    if not s:
        return None
    if s.startswith("zh"):
        return "zh-CN"
    if s.startswith("en"):
        return "en-US"
    return None


_lang = normalize(os.environ.get("FOXOS_LANG")) or DEFAULT


def messages(lang: str) -> dict[str, str]:
    if lang not in _messages:
        _messages[lang] = json.loads((_DIR / f"{lang}.json").read_text(encoding="utf-8"))
    return _messages[lang]


def get_lang() -> str:
    return _lang


def set_lang(lang: str | None) -> str:
    """设置当前语言（同时写入 FOXOS_LANG，子进程跟随）。不支持的语言忽略并保持原值。"""
    global _lang
    n = normalize(lang)
    if n:
        _lang = n
        os.environ["FOXOS_LANG"] = n
    return _lang


def init_from_argv(argv: list[str]) -> str:
    """在解析参数之前从 argv 里找 --lang（命令说明在导入时取词，必须先定语言）。"""
    for i, a in enumerate(argv):
        if a == "--":
            break
        if a == "--lang" and i + 1 < len(argv):
            return set_lang(argv[i + 1])
        if a.startswith("--lang="):
            return set_lang(a.split("=", 1)[1])
    return _lang


def tr(key: str, *args) -> str:
    """取词条；有参数时按 str.format 填入位置参数 {0} {1}…（无参数时原样返回，文本里的花括号不受影响）。"""
    s = messages(_lang).get(key)
    if s is None:
        s = messages(DEFAULT).get(key, key)
    return s.format(*args) if args else s
