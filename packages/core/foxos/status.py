"""First-run doctor: a single status report for onboarding checks."""

from __future__ import annotations

from . import __version__
from .workspace import Workspace


def doctor_status(ws: Workspace) -> dict:
    """Return a machine-readable first-run status report. No Live ISO, no network."""
    audit = ws.audit_path
    return {
        "ok": True,
        "version": __version__,
        "workspace": str(ws.root),
        "audit_log": str(audit),
        "audit_log_exists": audit.exists(),
        "takeover": {
            "status_command": "foxos control status",
            "pause_command": "foxos control pause",
            "resume_command": "foxos control resume",
        },
        "mcp": {
            "stdio_command": "foxos mcp",
            "http_command": "foxos mcp --http 127.0.0.1:8743",
            "tools_command": "foxos tools --format mcp",
        },
    }


def format_status(report: dict) -> str:
    takeover = report["takeover"]
    mcp = report["mcp"]
    lines = [
        f"FoxOS {report['version']}",
        f"Workspace: {report['workspace']}",
        f"Audit log: {report['audit_log']}"
        + (" (present)" if report.get("audit_log_exists") else " (not created yet)"),
        f"Takeover: {takeover['status_command']} | {takeover['pause_command']} | {takeover['resume_command']}",
        f"MCP stdio: {mcp['stdio_command']}",
        f"MCP HTTP: {mcp['http_command']}",
        f"MCP tools: {mcp['tools_command']}",
    ]
    return "\n".join(lines) + "\n"
