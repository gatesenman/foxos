#!/usr/bin/env bash
# 为某个目标平台准备桌面安装包的随包内容，然后才能跑 electron-builder：
#   1. 只留下目标平台的 node-pty 预编译包（@lydell/node-pty-<os>-<arch>），其他平台的删掉
#   2. 自带 Python 3.12 + 内核依赖，输出到 <仓库>/build/python（electron-builder 打进 resources/python）
#      - Windows：python.org 的 embeddable 包（与 0.2.0 相同的做法）
#      - Linux / macOS：astral-sh/python-build-standalone 的 install_only_stripped 包
#   依赖都是目标平台的二进制 wheel，由 uv 跨平台安装，所以可以在任意 Linux / macOS 构建机上交叉准备。
#
# 用法：scripts/packaging/prepare-platform.sh <linux|mac|win> <x64|arm64>
set -euo pipefail
OS=${1:?用法：prepare-platform.sh <linux|mac|win> <x64|arm64>}
ARCH=${2:?用法：prepare-platform.sh <linux|mac|win> <x64|arm64>}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DESKTOP="$ROOT/apps/desktop"
OUT="$ROOT/build/python"
PY_MINOR=3.12
WIN_PY_VERSION="${WIN_PY_VERSION:-3.12.8}"
PBS_TAG="${PBS_TAG:-20261110}"          # python-build-standalone 发布标签（固定，便于复现）
PBS_PY="${PBS_PY:-3.12.16}"
PTY_VERSION=1.2.0-beta.18
DEPS=("openpyxl>=3.1,<4" "python-docx>=1.1,<2" "python-pptx>=1.0,<2" "zstandard>=0.22")

case "$OS-$ARCH" in
  linux-x64)   PTY=linux-x64;   TRIPLE=x86_64-unknown-linux-gnu;  UVPLAT=x86_64-manylinux_2_28 ;;
  linux-arm64) PTY=linux-arm64; TRIPLE=aarch64-unknown-linux-gnu; UVPLAT=aarch64-manylinux_2_28 ;;
  mac-x64)     PTY=darwin-x64;  TRIPLE=x86_64-apple-darwin;       UVPLAT=x86_64-apple-darwin ;;
  mac-arm64)   PTY=darwin-arm64; TRIPLE=aarch64-apple-darwin;     UVPLAT=aarch64-apple-darwin ;;
  win-x64)     PTY=win32-x64;   EMBED=amd64;  UVPLAT=x86_64-pc-windows-msvc ;;
  win-arm64)   PTY=win32-arm64; EMBED=arm64;  UVPLAT=aarch64-pc-windows-msvc ;;
  *) echo "不支持的平台：$OS-$ARCH" >&2; exit 2 ;;
esac

PY=$(command -v python3 || command -v python) || { echo "需要 python3" >&2; exit 6; }
command -v uv >/dev/null || { echo "需要 uv（https://docs.astral.sh/uv/）" >&2; exit 6; }

# ---------------------------------------------------------------- node-pty
echo "[prepare] node-pty：只保留 @lydell/node-pty-$PTY"
for d in "$DESKTOP"/node_modules/@lydell/node-pty-*; do
  [ -e "$d" ] || continue
  [ "$(basename "$d")" = "node-pty-$PTY" ] || rm -rf "$d"
done
if [ ! -d "$DESKTOP/node_modules/@lydell/node-pty-$PTY" ]; then
  (cd "$DESKTOP" && npm install --no-save --force --ignore-scripts "@lydell/node-pty-$PTY@$PTY_VERSION" >/dev/null)
  # npm install --no-save 会把 package-lock 里本平台的可选依赖装回来，再删一次
  for d in "$DESKTOP"/node_modules/@lydell/node-pty-*; do
    [ "$(basename "$d")" = "node-pty-$PTY" ] || rm -rf "$d"
  done
fi
test -d "$DESKTOP/node_modules/@lydell/node-pty-$PTY"

# ---------------------------------------------------------------- Python
rm -rf "$OUT"; mkdir -p "$OUT" "$ROOT/build/cache"
fetch() { # url dest（已下载过就复用缓存）
  [ -s "$2" ] && return 0
  curl -fL --retry 4 --retry-delay 3 -o "$2.part" "$1"
  mv "$2.part" "$2"
}
if [ "$OS" = win ]; then
  Z="$ROOT/build/cache/python-$WIN_PY_VERSION-embed-$EMBED.zip"
  fetch "https://www.python.org/ftp/python/$WIN_PY_VERSION/python-$WIN_PY_VERSION-embed-$EMBED.zip" "$Z"
  "$PY" -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$Z" "$OUT"
  SITE="$OUT/Lib/site-packages"
  # ._pth 决定模块搜索路径（embeddable 版忽略 PYTHONPATH）：site-packages 与随附的内核 ..\core
  printf 'python312.zip\r\n.\r\nLib\\site-packages\r\n..\\core\r\nimport site\r\n' > "$OUT/python312._pth"
else
  NAME="cpython-$PBS_PY+$PBS_TAG-$TRIPLE-install_only_stripped.tar.gz"
  T="$ROOT/build/cache/$NAME"
  fetch "https://github.com/astral-sh/python-build-standalone/releases/download/$PBS_TAG/${NAME//+/%2B}" "$T"
  tar -C "$OUT" --strip-components=1 -xzf "$T"
  SITE="$OUT/lib/python$PY_MINOR/site-packages"
  # 去掉随包用不到的大件：测试套件、IDLE、tkinter、头文件、静态库
  rm -rf "$OUT/lib/python$PY_MINOR/test" "$OUT/lib/python$PY_MINOR/idlelib" "$OUT/lib/python$PY_MINOR/tkinter" \
         "$OUT/lib/python$PY_MINOR/turtledemo" "$OUT/include" "$OUT/share" "$OUT"/lib/libtcl* "$OUT"/lib/libtk* "$OUT"/lib/tcl* "$OUT"/lib/tk* \
         "$OUT/lib/python$PY_MINOR/lib-dynload/_tkinter"* 2>/dev/null || true
  find "$OUT/lib" -name '*.a' -delete
fi
mkdir -p "$SITE"
echo "[prepare] 内核依赖 → $SITE（$UVPLAT）"
uv pip install --quiet --target "$SITE" --python-platform "$UVPLAT" --python-version "$PY_MINOR" --only-binary :all: "${DEPS[@]}"
rm -rf "$SITE/bin"
find "$OUT" -name __pycache__ -type d -prune -exec rm -rf {} +
cat > "$OUT/FOXOS-PYTHON.txt" <<TXT
Python bundled with FoxOS ($OS-$ARCH).
$( [ "$OS" = win ] && echo "Source: https://www.python.org/ftp/python/$WIN_PY_VERSION/ (embeddable package, PSF License)" || echo "Source: https://github.com/astral-sh/python-build-standalone/releases/tag/$PBS_TAG ($NAME, PSF License and bundled third-party licenses in lib/python$PY_MINOR/LICENSE.txt)" )
Kernel dependencies: ${DEPS[*]}
TXT
echo "[prepare] 完成：$OS-$ARCH，Python 在 $OUT（$(du -sh "$OUT" | cut -f1)）"
