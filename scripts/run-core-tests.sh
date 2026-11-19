#!/bin/sh
# Run packages/core pytest in an isolated venv (uv if available, else python3 -m venv).
# Usage: scripts/run-core-tests.sh [pytest args...]
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CORE="$ROOT/packages/core"
VENV="${FOXOS_TEST_VENV:-$ROOT/.venv}"
if command -v uv >/dev/null 2>&1; then
  if [ ! -x "$VENV/bin/python" ]; then
    uv venv "$VENV"
  fi
  uv pip install --python "$VENV/bin/python" -e "$CORE[test]"
else
  if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
  fi
  "$VENV/bin/python" -m pip install -e "$CORE[test]"
fi
cd "$CORE"
exec "$VENV/bin/python" -m pytest "$@"
