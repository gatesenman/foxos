#!/usr/bin/env bash
# 桌面外壳冒烟测试（Linux）：生成演示工作空间 → 无头启动 Electron → 截图 → 检查截图。
# 需要 xvfb-run；用法：bash apps/desktop/scripts/smoke.sh [输出截图路径]
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="${1:-$(mktemp -d)/desktop.png}"
PY="${FOXOS_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3
WS="$(mktemp -d)/workspace"
"$PY" "$ROOT/scripts/seed_demo.py" "$WS" >/dev/null
rm -f "$OUT"
xvfb-run -a -s "-screen 0 1440x900x24" "$HERE/node_modules/.bin/electron" "$HERE" --no-sandbox \
  --workspace="$WS" --screenshot="$OUT" 2>&1 | grep -E "screenshot saved|界面" || true
python3 - "$OUT" <<'PY'
import struct, sys
data = open(sys.argv[1], "rb").read()
assert data[:8] == b"\x89PNG\r\n\x1a\n", "不是 PNG"
w, h = struct.unpack(">II", data[16:24])
assert w >= 1200 and h >= 700, (w, h)
print(f"桌面截图检查通过：{sys.argv[1]} {w}x{h}")
PY
# 界面交互自检：提交任务、运行命令、人工接管与恢复
xvfb-run -a -s "-screen 0 1440x900x24" "$HERE/node_modules/.bin/electron" "$HERE" --no-sandbox \
  --workspace="$WS" --selftest 2>&1 | grep -E "selftest|界面"
echo "桌面冒烟测试通过"
