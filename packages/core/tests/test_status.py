"""First-run `foxos status --json` doctor."""

import json


def test_status_json_reports_version_audit_takeover_and_mcp(fox, ws):
    code, data, proc = fox.run("status", check=0)
    assert code == 0
    assert data["ok"] is True
    assert data["version"]
    assert data["workspace"] == str(ws)
    assert data["audit_log"].endswith("audit.jsonl")
    assert "audit.jsonl" in data["audit_log"]
    assert data["takeover"]["status_command"] == "foxos control status"
    assert data["takeover"]["pause_command"] == "foxos control pause"
    assert data["mcp"]["stdio_command"] == "foxos mcp"
    assert "--http" in data["mcp"]["http_command"]
    assert data["mcp"]["tools_command"].startswith("foxos tools")


def test_status_human_readable(fox):
    code, _, proc = fox.run("status", json_out=False, check=0)
    assert code == 0
    text = proc.stdout
    assert "FoxOS" in text
    assert "Audit log:" in text
    assert "foxos control status" in text
    assert "foxos mcp" in text
