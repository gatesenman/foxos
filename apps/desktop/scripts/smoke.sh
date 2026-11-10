#!/usr/bin/env bash
# 桌面冒烟测试（Linux）：空工作空间 → 无头启动 Electron → 截图 → 检查截图。需要 xvfb-run。
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$(mktemp -d)/desktop.png}"
TMP="$(mktemp -d)"
rm -f "$OUT"
xvfb-run -a -s "-screen 0 1440x900x24" "$HERE/node_modules/.bin/electron" "$HERE" --no-sandbox \
  --user-data-dir="$TMP/user" --workspace="$TMP/ws" --screenshot="$OUT" 2>&1 | grep -E "screenshot saved|界面" || true
python3 - "$OUT" <<'PY'
import struct, sys
data = open(sys.argv[1], "rb").read()
assert data[:8] == b"\x89PNG\r\n\x1a\n", "不是 PNG"
w, h = struct.unpack(">II", data[16:24])
assert w >= 1000 and h >= 600, (w, h)
print(f"桌面截图检查通过：{sys.argv[1]} {w}x{h}")
PY
