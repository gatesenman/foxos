"""The kernel uses os.unshare / os.setns, which need Python 3.12+."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]
ROOT = CORE.parent.parent


def test_requires_python_matches_unshare_and_running_interpreter():
    text = (CORE / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
    assert match, "pyproject.toml must declare requires-python"
    req = match.group(1)
    assert req.startswith(">=") and tuple(int(p) for p in req[2:].split(".")[:2]) >= (3, 12), req
    assert sys.version_info >= (3, 12)
    linux = (CORE / "foxos" / "envs" / "linux.py").read_text(encoding="utf-8")
    assert "os.unshare" in linux and "os.setns" in linux
    arch = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    assert "Python 3.12+" in arch
