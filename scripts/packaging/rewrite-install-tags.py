#!/usr/bin/env python3
"""把 install.sh / install.ps1 里的默认发布标签改成当前 TAG（供 release 工作流在上传前调用）。"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def rewrite(tag: str, root: Path = ROOT) -> None:
    if not tag:
        raise SystemExit("需要环境变量 TAG")
    for rel in ("scripts/install.sh", "scripts/install.ps1"):
        path = root / rel
        text = path.read_text()
        text = re.sub(r"TAG=\$\{FOXOS_TAG:-v[^}]+\}", "TAG=${FOXOS_TAG:-" + tag + "}", text)
        text = re.sub(r"Tag = 'v[^']+'", "Tag = '" + tag + "'", text)
        text = re.sub(
            r"releases/download/v[0-9][0-9A-Za-z._-]*/install\.(sh|ps1)",
            "releases/download/" + tag + r"/install.\1",
            text,
        )
        text = re.sub(r"默认 v[0-9][0-9A-Za-z._-]*", "默认 " + tag, text)
        text = re.sub(r"Default v[0-9][0-9A-Za-z._-]*;", "Default " + tag + ";", text)
        path.write_text(text)


def main() -> int:
    rewrite(os.environ.get("TAG", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
