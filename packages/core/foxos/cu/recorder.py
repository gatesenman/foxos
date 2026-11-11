"""tmux pipe-pane 的接收端：原样追加到 out.log，同时写 asciicast v2（asciinema 播放器可播放）。

用法（由 foxos shell session new 设置）：python3 -m foxos.cu.recorder <out.log> [<cast 文件> <宽> <高>]
"""

from __future__ import annotations

import json
import os
import sys
import time


def main(argv: list[str]) -> int:
    log = argv[0]
    cast = argv[1] if len(argv) > 1 and argv[1] != "-" else None
    w, h = (int(argv[2]), int(argv[3])) if len(argv) > 3 else (200, 50)
    t0 = time.time()
    cf = None
    if cast:
        new = not os.path.exists(cast) or os.path.getsize(cast) == 0
        cf = open(cast, "a", encoding="utf-8")
        if new:
            cf.write(json.dumps({"version": 2, "width": w, "height": h, "timestamp": int(t0),
                                 "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}, "title": "foxos shell"}) + "\n")
            cf.flush()
        else:  # 续录：时间从上次最后一帧之后接着走
            try:
                with open(cast, "rb") as f:
                    f.seek(max(0, os.path.getsize(cast) - 4096))
                    last = [ln for ln in f.read().decode("utf-8", "replace").splitlines() if ln.startswith("[")]
                t0 -= float(json.loads(last[-1])[0]) if last else 0
            except (OSError, ValueError, IndexError):
                pass
    fd = sys.stdin.fileno()
    with open(log, "ab") as lf:
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            lf.write(chunk)
            lf.flush()
            if cf:
                cf.write(json.dumps([round(time.time() - t0, 6), "o", chunk.decode("utf-8", "replace")]) + "\n")
                cf.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
