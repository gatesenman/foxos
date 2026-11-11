"""多语言：词条两种语言齐全、占位符一致；--lang / FOXOS_LANG 切换消息语言，JSON 字段名与错误码不变。"""

import json
import re
from pathlib import Path

LOC = Path(__file__).resolve().parents[1] / "foxos" / "data" / "locales"
HAN = re.compile(r"[\u4e00-\u9fff]")
PH = re.compile(r"(?<!\{)\{(\d+)[^{}]*\}")


def load(lang):
    return json.loads((LOC / f"{lang}.json").read_text(encoding="utf-8"))


def test_locale_keys_identical_and_placeholders_match():
    zh, en = load("zh-CN"), load("en-US")
    assert set(zh) == set(en), sorted(set(zh) ^ set(en))[:20]
    for k in zh:
        assert zh[k].strip() and en[k].strip(), k
        assert sorted(PH.findall(zh[k])) == sorted(PH.findall(en[k])), k
    # 英文词条不应残留中文（少数是匹配本地化系统输出的文本，不在词条里）
    bad = [k for k, v in en.items() if HAN.search(v)]
    assert not bad, bad[:10]


def test_error_message_follows_lang(fox):
    _, r_zh, _ = fox.run("files", "read", "no-such.txt", check=3)
    _, r_en, _ = fox.run("--lang", "en-US", "files", "read", "no-such.txt", check=3)
    _, r_env, _ = fox.run("files", "read", "no-such.txt", check=3, extra_env={"FOXOS_LANG": "en-US"})
    assert r_zh["error"]["code"] == r_en["error"]["code"] == r_env["error"]["code"] == "NOT_FOUND"
    assert HAN.search(r_zh["error"]["message"])
    assert not HAN.search(r_en["error"]["message"]) and not HAN.search(r_env["error"]["message"])
    assert set(r_zh) == set(r_en) and set(r_zh["error"]) == set(r_en["error"])


def test_help_catalog_follows_lang(fox):
    _, zh, _ = fox.run("help", "sheets", check=0)
    _, en, _ = fox.run("help", "sheets", check=0, extra_env={"FOXOS_LANG": "en-US"})
    assert HAN.search(json.dumps(zh, ensure_ascii=False))
    assert not HAN.search(json.dumps(en, ensure_ascii=False))
