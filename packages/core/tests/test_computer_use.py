"""电脑操控（默认 agent-desktop + Jev；兜底截图 / 浏览器）的离线单元测试：不联网、不需要显示器。
真实端到端（XFCE + 真 Jev / DeepSeek）见 docs/test-report.md 的 US-120 起。"""

import io
import json
import os
import stat
import struct
import zlib

import pytest

from foxos.cu import agent_desktop, grounding, policy, typesafe
from foxos.errors import FoxError


# ------------------------------------------------------------------ TypeSafe Jev 客户端

class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_opener(answers, seen):
    def op(req, timeout=None):
        seen.append({"url": req.full_url, "headers": dict(req.header_items()), "body": json.loads(req.data or b"{}")})
        return _Resp(json.dumps(answers.pop(0) if isinstance(answers, list) else answers).encode())
    return op


def test_typesafe_choice_request_and_parse():
    seen = []
    q = {"a": typesafe.choice("pick", {"x": "X", "y": "Y"})}
    c = typesafe.Client(key="k", opener=fake_opener({"model": "jev-1.14.0", "answers": {"a": {"type": "choice", "choice": "y", "confidence": 0.9}},
                                                     "usage": {"input_tokens": 3}}, seen))
    r = c.ask({"s": 1}, q)
    assert r["answers"]["a"]["choice"] == "y" and r["model"] == "jev-1.14.0"
    assert seen[0]["url"].endswith("/v1/systemone") and seen[0]["body"]["questions"] == q
    assert "TypeSafe-danger-zone-images" not in seen[0]["headers"] and seen[0]["headers"]["Authorization"] == "Bearer k"


def test_typesafe_box_sets_images_header_and_rejects_bad_choice():
    body, hdr = typesafe.build_request("img", {"t": typesafe.box("find")}, assets={"img": typesafe.image_asset(b"x")})
    assert hdr == {"TypeSafe-Danger-Zone-Images": "true"} and body["assets"]["img"]["type"] == "image"
    with pytest.raises(FoxError):
        typesafe.parse_response({"answers": {"a": {"type": "choice", "choice": "zzz"}}}, {"a": typesafe.choice("p", {"x": "X"})})
    with pytest.raises(FoxError):
        typesafe.choice("too many", {str(i): str(i) for i in range(256)})


def test_typesafe_no_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setattr(typesafe, "api_key", lambda: None)
    with pytest.raises(FoxError) as e:
        typesafe.Client(key=None, opener=lambda *a, **k: None).models()
    assert e.value.code == "DEPENDENCY_MISSING"


# ------------------------------------------------------------------ 观察编译器

def test_compile_browser_builtin_and_agent_browser_formats():
    snap = "\n".join([
        '- link "Jump to content" [ref=e1]',
        '- heading "Mount Everest" [level=1, ref=e9]',
        '- textbox "Search Wikipedia" [focused] [ref=e12]: "rust"',
        '- button "Go" [disabled] [ref=e13]',
        '- paragraph "Some prose"',
    ])
    cands, text = policy.compile_browser(snap)
    ids = [c.id for c in cands]
    assert ids == ["e1", "e12"]  # heading → 文字，disabled 丢掉
    tb = cands[1]
    assert tb.role == "textbox" and tb.value == "rust" and "focused" in tb.states
    assert "Mount Everest" in text


def test_compile_computer_drops_offscreen_and_disabled():
    nodes = [{"ref": "e1", "role": "button", "name": "Save", "states": []},
             {"ref": "e2", "role": "menuitem", "name": "Quit", "states": ["offscreen"]},
             {"ref": "e3", "role": "button", "name": "Undo", "states": ["disabled"]},
             {"ref": "w2e4", "role": "textfield", "name": "", "value": "hi", "states": ["focused"]}]
    c = policy.compile_computer(nodes, "t", "")
    assert [x.id for x in c] == ["e1", "w2e4"] and c[1].value == "hi"


def test_prefilter_caps_at_255_and_keeps_goal_matches():
    cands = [policy.Candidate(f"e{i}", "button", f"thing {i}") for i in range(400)] + [policy.Candidate("e999", "button", "Save file")]
    out = policy.prefilter(cands, "save the file")
    assert len(out) == 255 and any(c.id == "e999" for c in out)


def test_logprob_confidence_is_product_of_value_tokens():
    content = '{"action": "click", "target": "e12"}'
    toks = [{"token": t, "logprob": lp} for t, lp in [('{"', 0), ("action", 0), ('":', 0), (' "', 0), ("click", -0.1),
                                                       ('",', 0), (' "', 0), ("target", 0), ('":', 0), (' "', 0), ("e", -0.2),
                                                       ("12", -0.3), ('"}', 0)]]
    pa = policy._value_span_prob(content, toks, "action")
    pt = policy._value_span_prob(content, toks, "target")
    assert abs(pa - 2.718281828 ** -0.1) < 1e-6 and abs(pt - 2.718281828 ** -0.5) < 1e-6


# ------------------------------------------------------------------ Jev 单步策略（假传输层）

class FakeTS:
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def ask(self, state, qs, assets=None, model=None):
        self.calls.append({"state": state, "qs": qs, "assets": assets})
        a = self.answers.pop(0)
        return {"answers": a, "model": "jev-1.14.0", "usage": {"input_tokens": 1}, "seconds": 0.1}


def _obs(cands, kind="computer", surface="a11y", png=None):
    return policy.Observation(kind, "Win", None, cands, "", "", len(cands), surface=surface, png=png)


def test_jev_policy_min_confidence_and_target():
    ts = FakeTS([{"action": {"type": "choice", "choice": "click", "confidence": 0.95},
                  "key": {"type": "choice", "choice": "return", "confidence": 0.5},
                  "target": {"type": "choice", "choice": "e1", "confidence": 0.7}}])
    p = policy.JevPolicy(client=ts)
    d = p.decide(_obs([policy.Candidate("e1", "button", "Save")]), "g", {"goal": "save"}, [])
    assert (d.action, d.target, d.key, round(d.confidence, 2)) == ("click", "e1", None, 0.7)


def test_jev_policy_two_stage_over_255():
    cands = [policy.Candidate(f"e{i}", "button", f"b{i}") for i in range(300)]
    first = {"action": {"type": "choice", "choice": "click", "confidence": 0.9}, "key": {"type": "choice", "choice": "tab", "confidence": 0.9},
             "target_0": {"type": "choice", "choice": "e3", "probabilities": {"e3": 0.6, "e4": 0.3}},
             "target_1": {"type": "choice", "choice": "e290", "probabilities": {"e290": 0.8, "e291": 0.1}}}
    second = {"target": {"type": "choice", "choice": "e290", "confidence": 0.88}}
    ts = FakeTS([first, second])
    d = policy.JevPolicy(client=ts).decide(_obs(cands), "g", {"goal": "x"}, [])
    assert d.target == "e290" and len(ts.calls) == 2 and set(ts.calls[1]["qs"]["target"]["criteria"]) == {"e3", "e4", "e290", "e291"}


def _png(w, h):
    raw = b"".join(b"\x00" + b"\x00" * (w * 3) for _ in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def test_jev_screen_decision_uses_box_and_image_placeholder():
    ts = FakeTS([{"action": {"type": "choice", "choice": "click", "confidence": 0.9},
                  "key": {"type": "choice", "choice": "return", "confidence": 0.9},
                  "target": {"type": "box", "box": {"left": 0.1, "right": 0.3, "top": 0.5, "bottom": 0.7}, "confidence": 0.8}}])
    png = _png(200, 100)
    d = policy.JevPolicy(client=ts).decide(_obs([], surface="screen", png=png), "g", {"goal": "save", "target": "the Save button"}, [])
    assert d.point == (40, 60) and round(d.confidence, 2) == 0.8
    call = ts.calls[0]
    ph = call["state"]["screenshot"]
    assert ph.startswith("img-") and ph in call["assets"] and "Save button" in call["qs"]["target"]["instructions"]


# ------------------------------------------------------------------ agent-desktop 适配层（假的命令行）

def _fake_bin(tmp_path, out: dict):
    f = tmp_path / "agent-desktop"
    f.write_text("#!/bin/sh\ncat <<'J'\n" + json.dumps(out) + "\nJ\n")
    f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return str(f)


def test_agent_desktop_envelope_ok_and_error(tmp_path, monkeypatch):
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _fake_bin(tmp_path, {"version": "2.6", "ok": True, "data": [{"id": "w1", "title": "A"}]}))
    assert agent_desktop.windows()[0]["id"] == "w1"
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _fake_bin(tmp_path, {"version": "2.6", "ok": False, "error": {
        "code": "APP_NOT_FOUND", "message": "nope", "disposition": {"retry": "safe"}}}))
    with pytest.raises(FoxError) as e:
        agent_desktop.apps()
    assert e.value.details.get("agent_desktop_code") == "APP_NOT_FOUND"


def test_flatten_render_roundtrip():
    tree = {"role": "window", "name": "Doc", "children": [
        {"role": "button", "name": "Save", "ref_id": "@s1:e3", "states": ["focusable"]},
        {"role": "menuitem", "name": "Hidden", "ref_id": "@s1:e4", "states": ["offscreen"]}]}
    nodes = agent_desktop.flatten(tree)
    txt = agent_desktop.render(nodes)
    assert '- button "Save" [ref=e3]' in txt and "Hidden" not in txt


# ------------------------------------------------------------------ 路由：默认 agent-desktop，网页读不到才退浏览器

class _Ctx:
    class workspace:  # noqa: N801
        root = "/tmp"


def test_routing_default_stays_on_agent_desktop(monkeypatch):
    from foxos.cu import agent
    assert agent.needs_browser_fallback(_Ctx, "replace text in Mousepad and save", app="mousepad") is None


def test_routing_falls_back_to_browser_when_web_not_exposed(monkeypatch):
    from foxos.cu import agent
    monkeypatch.setattr(agent_desktop, "apps", lambda: [{"name": "mousepad"}])
    assert "no browser" in agent.needs_browser_fallback(_Ctx, "look this up", url="https://example.com")
    monkeypatch.setattr(agent_desktop, "apps", lambda: [{"name": "Google Chrome"}])
    monkeypatch.setattr(agent_desktop, "snapshot", lambda ws, **k: {"nodes": [{"role": "frame"}, {"role": "push button"}]})
    assert "not exposed" in agent.needs_browser_fallback(_Ctx, "look this up", app="chrome")
    monkeypatch.setattr(agent_desktop, "snapshot", lambda ws, **k: {"nodes": [{"role": "document web"}, {"role": "link"}]})
    assert agent.needs_browser_fallback(_Ctx, "look this up", app="chrome") is None


def test_grounding_auto_prefers_jev_box(monkeypatch):
    monkeypatch.setattr(typesafe, "api_key", lambda: "k")
    called = {}
    monkeypatch.setattr(grounding, "ground_typesafe", lambda png, d, cfg: called.setdefault("ts", {"x": 1, "y": 2}))
    assert grounding.ground(b"", "x", {"grounding": {"kind": "auto"}}) == {"x": 1, "y": 2}


def test_active_policy_switches_on_key(monkeypatch):
    cfg = {"provider": "deepseek", "model": "deepseek-v4-pro"}
    monkeypatch.setattr(typesafe, "api_key", lambda: None)
    assert policy.active_policy(cfg).name == "deepseek"
    monkeypatch.setattr(typesafe, "api_key", lambda: "k")
    assert policy.active_policy(cfg).name == "typesafe"
    assert policy.active_policy(cfg, "deepseek").name == "deepseek"


def test_bot_computer_use_setting_validated(tmp_path):
    from foxos import bots
    assert bots.validate_patch(None, {"computer_use": {"surface": "screen", "step_policy": "typesafe"}}) == {
        "computer_use": {"surface": "screen", "step_policy": "typesafe"}}
    with pytest.raises(FoxError):
        bots.validate_patch(None, {"computer_use": {"surface": "everything"}})

# ------------------------------------------------------------------ 慢快照时限、标题当 --app、动作重试

class _WS:
    def __init__(self, tmp):
        self.data_dir = tmp / "wsdata"
        self.data_dir.mkdir(parents=True, exist_ok=True)


def _py_ad(tmp_path, body: str) -> str:
    f = tmp_path / "agent-desktop"
    f.write_text("#!/usr/bin/env python3\nimport json,sys\n" + body + "\n")
    f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return str(f)


def test_snapshot_passes_longer_timeout_and_retries_incomplete(tmp_path, monkeypatch):
    """默认把 --timeout-ms 提到 30s；第一次 complete=false 时加倍再拍，第二次的引用才用来点击。"""
    log = tmp_path / "argv.log"
    body = (
        "argv=sys.argv[1:]\n"
        f"open({str(log)!r}, 'a').write(' '.join(argv)+'\\n')\n"
        "cmd=argv[0]\n"
        "ms=3000\n"
        "if '--timeout-ms' in argv:\n"
        "    ms=int(argv[argv.index('--timeout-ms')+1])\n"
        "if cmd=='snapshot':\n"
        "    ok = ms >= 60000\n"
        "    sid = 's2' if ok else 's1'\n"
        "    tree={'role':'window','name':'us121.txt','children':[\n"
        "        {'role':'document','name':'','ref_id':'@'+sid+':e2','available_actions':['set-value']}]}\n"
        "    print(json.dumps({'ok': True, 'data': {'snapshot_id': sid, 'app': 'mousepad',\n"
        "        'complete': ok, 'ref_count': 1, 'tree': tree}}))\n"
        "elif cmd=='list-windows':\n"
        "    print(json.dumps({'ok': True, 'data': [{'id': 'w-mp', 'title': 'us121.txt - Mousepad', 'app': 'mousepad'}]}))\n"
        "else:\n"
        "    print(json.dumps({'ok': True, 'data': {}}))\n"
    )
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _py_ad(tmp_path, body))
    monkeypatch.delenv("FOXOS_AD_TIMEOUT_MS", raising=False)
    ws = _WS(tmp_path)
    r = agent_desktop.snapshot(ws, app="mousepad")
    lines = log.read_text().strip().splitlines()
    assert any("--timeout-ms 30000" in ln and ln.startswith("snapshot") for ln in lines)
    assert any("--timeout-ms 60000" in ln and ln.startswith("snapshot") for ln in lines)
    assert r["complete"] is True and r["snapshot_id"] == "s2"
    assert r["app"] == "mousepad"


def test_snapshot_window_title_as_app_uses_window_id(tmp_path, monkeypatch):
    """--app 传入窗口标题时 agent-desktop 会 APP_NOT_FOUND：改成按标题找到窗口 id。"""
    log = tmp_path / "argv.log"
    body = (
        "argv=sys.argv[1:]\n"
        f"open({str(log)!r}, 'a').write(' '.join(argv)+'\\n')\n"
        "cmd=argv[0]\n"
        "if cmd=='list-windows':\n"
        "    if '--app' in argv:\n"
        "        app=argv[argv.index('--app')+1]\n"
        "        if app!='mousepad':\n"
        "            print(json.dumps({'ok': False, 'error': {'code': 'APP_NOT_FOUND', 'message': app, 'disposition': {'retry': 'safe'}}}))\n"
        "            raise SystemExit(0)\n"
        "    print(json.dumps({'ok': True, 'data': [{'id': 'w-mp', 'title': '~/FoxOS/workspace/us121.txt - Mousepad', 'app': 'mousepad'}]}))\n"
        "elif cmd=='snapshot':\n"
        "    assert '--window-id' in argv and argv[argv.index('--window-id')+1]=='w-mp'\n"
        "    print(json.dumps({'ok': True, 'data': {'snapshot_id': 's9', 'app': 'mousepad', 'complete': True, 'ref_count': 1,\n"
        "        'tree': {'role':'window','name':'us121.txt','children':[{'role':'document','ref_id':'@s9:e2'}]}}}))\n"
        "else:\n"
        "    print(json.dumps({'ok': True, 'data': {}}))\n"
    )
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _py_ad(tmp_path, body))
    r = agent_desktop.snapshot(_WS(tmp_path), app="~/FoxOS/workspace/us121.txt - Mousepad")
    assert r["app"] == "mousepad" and r["snapshot_id"] == "s9"


def test_act_retries_ambiguous_after_fresh_snapshot(tmp_path, monkeypatch):
    """click 遇到 identity_not_unique 时，加大时限重拍并把 e2 对到新快照再点一次。"""
    log = tmp_path / "argv.log"
    body = (
        "argv=sys.argv[1:]\n"
        f"open({str(log)!r}, 'a').write(' '.join(argv)+'\\n')\n"
        "cmd=argv[0]\n"
        "if cmd=='list-windows':\n"
        "    print(json.dumps({'ok': True, 'data': [{'id': 'w-mp', 'title': 'us121.txt - Mousepad', 'app': 'mousepad'}]}))\n"
        "elif cmd=='snapshot':\n"
        "    sid = 's-new' if '--timeout-ms' in argv and int(argv[argv.index('--timeout-ms')+1]) >= 60000 else 's-old'\n"
        "    print(json.dumps({'ok': True, 'data': {'snapshot_id': sid, 'app': 'mousepad', 'complete': True, 'ref_count': 1,\n"
        "        'tree': {'role':'window','name':'us121.txt','children':[{'role':'document','name':'','ref_id':'@'+sid+':e2'}]}}}))\n"
        "elif cmd=='click':\n"
        "    ref=argv[1]\n"
        "    if ref.startswith('@s-old:'):\n"
        "        print(json.dumps({'ok': False, 'error': {'code': 'AMBIGUOUS_TARGET', 'message': 'not unique',\n"
        "            'disposition': {'retry': 'safe'}, 'details': {'kind': 'identity_not_unique'}}}))\n"
        "    else:\n"
        "        print(json.dumps({'ok': True, 'data': {'clicked': ref}}))\n"
        "else:\n"
        "    print(json.dumps({'ok': True, 'data': {}}))\n"
    )
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _py_ad(tmp_path, body))
    monkeypatch.delenv("FOXOS_AD_TIMEOUT_MS", raising=False)
    ws = _WS(tmp_path)
    agent_desktop.snapshot(ws, app="mousepad")
    r = agent_desktop.act(ws, "click", "e2")
    clicks = [ln for ln in log.read_text().splitlines() if ln.startswith("click ")]
    assert any("@s-old:e2" in ln for ln in clicks)
    assert any("@s-new:e2" in ln for ln in clicks)
    assert r.get("clicked") == "@s-new:e2"


def test_timeout_ms_env_override(monkeypatch):
    monkeypatch.setenv("FOXOS_AD_TIMEOUT_MS", "45000")
    assert agent_desktop.timeout_ms() == 45000
    monkeypatch.delenv("FOXOS_AD_TIMEOUT_MS")
    assert agent_desktop.timeout_ms() == 30000


def test_set_value_and_press_get_timeout_ms(tmp_path, monkeypatch):
    log = tmp_path / "argv.log"
    body = (
        "argv=sys.argv[1:]\n"
        f"open({str(log)!r}, 'a').write(' '.join(argv)+'\\n')\n"
        "cmd=argv[0]\n"
        "if cmd=='list-windows':\n"
        "    print(__import__('json').dumps({'ok': True, 'data': [{'id': 'w', 'title': 't', 'app': 'mousepad'}]}))\n"
        "elif cmd=='snapshot':\n"
        "    print(__import__('json').dumps({'ok': True, 'data': {'snapshot_id': 's1', 'app': 'mousepad', 'complete': True, 'ref_count': 1,\n"
        "        'tree': {'role':'window','children':[{'role':'textfield','ref_id':'@s1:e2'}]}}}))\n"
        "elif cmd=='press' and '--headed' not in argv:\n"
        "    print(__import__('json').dumps({'ok': False, 'error': {'code': 'ACTION_FAILED',\n"
        "        'message': 'focus changes are not allowed', 'disposition': {'retry': 'safe'},\n"
        "        'details': {'cause': 'display_active_window'}}}))\n"
        "elif cmd=='focus-window':\n"
        "    print(__import__('json').dumps({'ok': False, 'error': {'code': 'ACTION_FAILED', 'message': 'did not settle',\n"
        "        'disposition': {'retry': 'unknown'}}}))\n"
        "else:\n"
        "    print(__import__('json').dumps({'ok': True, 'data': {'args': argv}}))\n"
    )
    monkeypatch.setenv("FOXOS_AGENT_DESKTOP", _py_ad(tmp_path, body))
    monkeypatch.delenv("FOXOS_AD_TIMEOUT_MS", raising=False)
    ws = _WS(tmp_path)
    agent_desktop.snapshot(ws, app="mousepad")
    agent_desktop.act(ws, "set-value", "e2", "hello")
    r = agent_desktop.press("ctrl+s", app="mousepad")
    lines = log.read_text().splitlines()
    assert any(ln.startswith("set-value ") and "--timeout-ms 30000" in ln and "@s1:e2" in ln for ln in lines)
    assert any(ln.startswith("press ctrl+s") and "--headed" in ln for ln in lines)
    assert r.get("args") and "--headed" in r["args"]
