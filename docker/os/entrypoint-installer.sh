#!/bin/sh
# 只从 GitHub Release 下载狐狸OS ISO 并校验 sha256（在线安装助手）。不启动虚拟机。
# 若 Release 上没有单个完整 ISO（目前按两个分卷发布），则下载分卷、拼接后再校验。
set -eu
REL=${FOXOS_RELEASE_URL:-https://github.com/gatesenman/foxos/releases/download/v0.3.1-os-preview}
SUMS_URL=${FOXOS_SUMS_URL:-$REL/SHA256SUMS}
OUT=${FOXOS_OUT:-/out}
NAME=FoxOS-0.3.1-amd64.iso
mkdir -p "$OUT"

verify() {
  if [ -f "$OUT/SHA256SUMS" ]; then
    grep -E "  $NAME$|  \\./$NAME$" "$OUT/SHA256SUMS" | (cd "$OUT" && sha256sum -c -)
    echo "[foxos-installer] 校验通过：$OUT/$NAME"
    return 0
  fi
  if [ -n "${FOXOS_ISO_SHA256:-}" ]; then
    echo "$FOXOS_ISO_SHA256  $OUT/$NAME" | sha256sum -c -
    echo "[foxos-installer] 校验通过（FOXOS_ISO_SHA256）"
    return 0
  fi
  echo "[foxos-installer] 警告：没有 SHA256SUMS，也没有 FOXOS_ISO_SHA256，未做校验" >&2
}

assemble_parts() {
  echo "[foxos-installer] 下载分卷并拼接 $NAME"
  wget -O "$OUT/${NAME}.part1" "${REL}/${NAME}.part1"
  wget -O "$OUT/${NAME}.part2" "${REL}/${NAME}.part2"
  cat "$OUT/${NAME}.part1" "$OUT/${NAME}.part2" > "$OUT/$NAME"
  rm -f "$OUT/${NAME}.part1" "$OUT/${NAME}.part2"
}

if [ -n "${FOXOS_ISO_URL:-}" ]; then
  echo "[foxos-installer] 下载 $FOXOS_ISO_URL"
  wget -O "$OUT/$NAME" "$FOXOS_ISO_URL"
else
  wget -O "$OUT/SHA256SUMS" "$SUMS_URL" || true
  echo "[foxos-installer] 尝试下载完整 ISO $REL/$NAME"
  if wget -O "$OUT/$NAME" "$REL/$NAME" && [ -f "$OUT/SHA256SUMS" ] \
    && grep -E "  $NAME$|  \\./$NAME$" "$OUT/SHA256SUMS" | (cd "$OUT" && sha256sum -c -); then
    echo "[foxos-installer] 校验通过：$OUT/$NAME"
    ls -lh "$OUT/$NAME"
    exit 0
  fi
  echo "[foxos-installer] 完整 ISO 不可用或校验失败，改下分卷" >&2
  rm -f "$OUT/$NAME"
  assemble_parts
fi

if [ ! -f "$OUT/SHA256SUMS" ]; then
  wget -O "$OUT/SHA256SUMS" "$SUMS_URL" || true
fi
verify
ls -lh "$OUT/$NAME"
