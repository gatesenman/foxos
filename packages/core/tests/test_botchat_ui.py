"""US-159: the bots window UI is complete in both languages and uses only icons that ship with it."""
import json
import re
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "foxos" / "botchat" / "static"


def _src():
    return (STATIC / "app.js").read_text(encoding="utf-8") + (STATIC / "index.html").read_text(encoding="utf-8")


def test_US159_locales_complete_and_icons_shipped():
    zh = json.loads((STATIC / "locales" / "zh-CN.json").read_text(encoding="utf-8"))
    en = json.loads((STATIC / "locales" / "en-US.json").read_text(encoding="utf-8"))
    assert set(zh) == set(en), sorted(set(zh) ^ set(en))
    assert all(str(v).strip() for v in list(zh.values()) + list(en.values()))

    src = _src()
    keys = set(re.findall(r'\bt\("([a-z_]+\.[a-z0-9_]+)"', src))
    keys |= set(re.findall(r'data-i18n(?:-title|-placeholder)?="([a-z_]+\.[a-z0-9_]+)"', src))
    keys |= {"chat.thinking", "chat.working", "app.theme_auto", "app.theme_light", "app.theme_dark"}
    # keys ending in "_" are prefixes completed at run time ("settings.tab_" + name)
    missing = sorted(k for k in keys if (not any(z.startswith(k) for z in zh) if k.endswith("_") else k not in zh))
    assert not missing, missing

    css = next(STATIC.glob("vendor/**/tabler-icons*.css")).read_text(encoding="utf-8")
    have = set(re.findall(r"\.ti-([a-z0-9-]+):before", css))
    used = set(re.findall(r'\bti ti-([a-z0-9-]+)', src))
    unknown = sorted(u for u in used if u not in have)
    assert not unknown, unknown


def test_US159_theme_follows_system_and_dark_tokens_exist():
    css = (STATIC / "app.css").read_text(encoding="utf-8")
    assert 'html[data-theme="dark"]' in css
    assert "scrollbar-width: thin" in css or "::-webkit-scrollbar" in css
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "prefers-color-scheme: dark" in js and "applyTheme" in js
