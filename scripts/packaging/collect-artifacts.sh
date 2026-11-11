#!/usr/bin/env bash
# 把 electron-builder 的产物改成统一的文件名，放进一个目录，并写出这一批的 SHA256SUMS。
#   FoxOS-<版本>-linux-<x64|arm64>.{AppImage,deb,rpm,tar.gz}
#   FoxOS-<版本>-mac-<x64|arm64>.{dmg,zip}
#   FoxOS-Setup-<版本>-<x64|arm64>.exe · FoxOS-<版本>-win-<x64|arm64>.{zip,msi}
# 用法：collect-artifacts.sh <dist 目录> <输出目录> <linux|mac|win> <x64|arm64>
set -euo pipefail
DIST=${1:?}; OUT=${2:?}; OS=${3:?}; ARCH=${4:?}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
V=$(node -p "require('$ROOT/apps/desktop/package.json').version")
mkdir -p "$OUT"
n=0
FILES=()
take() { # 源文件 目标名
  local src=$1 dst=$2
  [ -f "$src" ] || return 0
  cp -f "$src" "$OUT/$dst"; echo "  $dst  ($(du -h "$OUT/$dst" | cut -f1))"; n=$((n+1)); FILES+=("$dst")
}
echo "收集 $OS-$ARCH："
shopt -s nullglob
case "$OS" in
  linux)
    for ext in AppImage deb rpm tar.gz; do
      for f in "$DIST"/*."$ext"; do take "$f" "FoxOS-$V-linux-$ARCH.$ext"; done
    done ;;
  mac)
    for ext in dmg zip; do
      for f in "$DIST"/FoxOS-"$V"-mac-"$ARCH"."$ext"; do take "$f" "$(basename "$f")"; done
    done ;;
  win)
    for f in "$DIST"/FoxOS-Setup-"$V"-"$ARCH".exe "$DIST"/FoxOS-"$V"-win-"$ARCH".zip "$DIST"/FoxOS-"$V"-win-"$ARCH".msi; do
      take "$f" "$(basename "$f")"
    done ;;
  *) echo "未知平台 $OS" >&2; exit 2 ;;
esac
[ "$n" -gt 0 ] || { echo "没有找到 $OS-$ARCH 的产物（$DIST）" >&2; exit 1; }
if command -v sha256sum >/dev/null; then SUM="sha256sum"; else SUM="shasum -a 256"; fi
(cd "$OUT" && $SUM "${FILES[@]}" > "SHA256SUMS.$OS-$ARCH")
cat "$OUT/SHA256SUMS.$OS-$ARCH"
