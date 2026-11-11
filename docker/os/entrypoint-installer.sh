#!/bin/sh
# 只从 GitHub Release 下载狐狸OS ISO 并校验 sha256（在线安装助手）。不启动虚拟机。
set -eu
ISO_URL=${FOXOS_ISO_URL:-https://github.com/gatesenman/foxos/releases/download/v0.3.0-os-preview/FoxOS-0.3.0-amd64.iso}
SUMS_URL=${FOXOS_SUMS_URL:-https://github.com/gatesenman/foxos/releases/download/v0.3.0-os-preview/SHA256SUMS}
OUT=${FOXOS_OUT:-/out}
mkdir -p "$OUT"
NAME=$(basename "$ISO_URL")
echo "[foxos-installer] 下载 $ISO_URL"
wget -O "$OUT/$NAME" "$ISO_URL"
if wget -O "$OUT/SHA256SUMS" "$SUMS_URL"; then
  # 只校验我们刚下的文件名
  grep -E "  $NAME$|  \\./$NAME$" "$OUT/SHA256SUMS" | (cd "$OUT" && sha256sum -c -)
  echo "[foxos-installer] 校验通过：$OUT/$NAME"
else
  if [ -n "${FOXOS_ISO_SHA256:-}" ]; then
    echo "$FOXOS_ISO_SHA256  $OUT/$NAME" | sha256sum -c -
    echo "[foxos-installer] 校验通过（FOXOS_ISO_SHA256）"
  else
    echo "[foxos-installer] 警告：没有 SHA256SUMS，也没有 FOXOS_ISO_SHA256，未做校验" >&2
  fi
fi
ls -lh "$OUT/$NAME"
