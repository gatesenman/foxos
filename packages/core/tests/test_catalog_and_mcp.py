"""能力目录、工具 Schema、MCP 服务器：与 CLI 调用同一内核。"""

import json
import subprocess
import sys

from foxos import catalog
from foxos.kernel import REGISTRY, load_apps


def test_help_json_catalog(fox):
    code, out, _ = fox.run("help", check=0)
    assert out["name"] == "foxos"
    assert out["conventions"]["exit_codes"]["5"].startswith("LOCKED")
    sheets = next(a for a in out["apps"] if a["name"] == "sheets")
    ids = {c["id"] for c in sheets["commands"]}
    assert {"sheets.create", "sheets.read", "sheets.write", "sheets.chart.create", "sheets.export"} <= ids
    for c in sheets["commands"]:
        assert c["examples"], c["id"]
        assert c["input_schema"]["type"] == "object"
        assert c["usage"].startswith("foxos sheets ")
    chart = next(c for c in sheets["commands"] if c["id"] == "sheets.chart.create")
    assert chart["input_schema"]["properties"]["type"]["enum"] == ["bar", "line", "pie"]
    assert set(chart["input_schema"]["required"]) == {"file", "type", "data"}


def test_app_help_text(fox):
    code, _, p = fox.run("sheets", "--help", json_out=False, check=0)
    assert "foxos sheets chart create" in p.stdout and "限制" in p.stdout
    code, _, p = fox.run("sheets", "chart", "create", "--help", json_out=False, check=0)
    assert "示例" in p.stdout and "退出码" in p.stdout


def test_examples_parse(fox):
    """能力目录里的每个示例都能被 CLI 解析（--help 方式不执行）。"""
    load_apps()
    for c in REGISTRY.values():
        for ex in c.examples:
            assert ex.startswith(c.cli), ex


def test_tools_export(fox):
    code, _, p = fox.run("tools", "--format", "openai", json_out=False, check=0)
    tools = json.loads(p.stdout)
    names = {t["function"]["name"] for t in tools}
    assert "sheets_chart_create" in names and "audit_tail" in names
    assert len(catalog.mcp_tools()) == len(REGISTRY)


def test_mcp_server_uses_same_kernel(fox, ws, core_env):
    proc = subprocess.Popen(
        [sys.executable, "-m", "foxos", "mcp", "--workspace", str(ws)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=core_env,
    )

    def rpc(i, method, params=None):
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params or {}}) + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    try:
        init = rpc(1, "initialize", {"protocolVersion": "2025-06-18", "clientInfo": {"name": "test-client"}, "capabilities": {}})
        assert init["result"]["serverInfo"]["name"] == "foxos"
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        tools = rpc(2, "tools/list")["result"]["tools"]
        assert any(t["name"] == "sheets_write" for t in tools)
        r = rpc(3, "tools/call", {"name": "sheets_create", "arguments": {"file": "mcp.xlsx", "headers": ["k", "v"]}})
        assert r["result"]["isError"] is False
        r = rpc(4, "tools/call", {"name": "sheets_write", "arguments": {"file": "mcp.xlsx", "cells": {"A2": "x", "B2": 5, "B3": "=B2*2"}}})
        assert r["result"]["structuredContent"]["result"]["formulas"] == 1
        r = rpc(5, "tools/call", {"name": "sheets_read", "arguments": {"file": "../etc.xlsx"}})
        assert r["result"]["isError"] is True
        assert r["result"]["structuredContent"]["error"]["code"] == "PERMISSION_DENIED"
        r = rpc(6, "tools/call", {"name": "sheets_write", "arguments": {"file": "mcp.xlsx", "cells": {"A1": 1}, "bogus": 1}})
        assert r["result"]["structuredContent"]["error"]["code"] == "USAGE"
        assert rpc(7, "nope")["error"]["code"] == -32601
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)

    # MCP 调用与 CLI 写进同一个审计日志，接口与调用方可区分
    code, out, _ = fox.run("audit", "tail", "-n", "10", check=0)
    entries = out["result"]["entries"]
    mcp = [e for e in entries if e["interface"] == "mcp"]
    assert len(mcp) == 4 and mcp[0]["agent"] == "mcp:test-client"
    assert [e["status"] for e in mcp] == ["ok", "ok", "denied", "error"]
    assert entries[-1]["command"] == "mcp" or entries[-1]["interface"] == "mcp"


def test_audit_filter_does_not_clobber_caller_identity(fox):
    fox.run("sheets", "create", "x.xlsx", agent="data-agent", check=0)
    fox.run("sheets", "read", "x.xlsx", agent="review-agent", check=0)
    code, out, _ = fox.run("audit", "tail", "--filter-agent", "data-agent", agent="review-agent", check=0)
    assert [e["agent"] for e in out["result"]["entries"]] == ["data-agent"]
    # audit tail / control status 是自省命令，不写审计
    assert [e["command"] for e in fox.audit()] == ["sheets.create", "sheets.read"]


def test_cli_reference_doc_is_up_to_date():
    from pathlib import Path

    script = Path(__file__).resolve().parents[3] / "scripts" / "gen_cli_docs.py"
    p = subprocess.run([sys.executable, str(script), "--check"], capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
