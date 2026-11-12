#!/bin/sh
# 从 GitHub Release 下载狐狸OS ISO，并按 Release 里的 SHA256SUMS 校验。
# 分卷列表（FoxOS-<版本>-amd64.iso.part-00、part-01……）直接从 SHA256SUMS 里读，
# 所以分卷数量变了也不用改脚本。每个分卷先单独校验，再追加到 ISO 并立即删掉，
# 磁盘峰值约为「ISO + 一个分卷」。最后整张 ISO 再校验一次。
#
# 用法：foxos-fetch-iso <输出目录>
# 环境变量：
#   FOXOS_VERSION       版本号，默认 0.3.4（镜像构建时由 build arg 写入）
#   FOXOS_RELEASE_URL   Release 下载地址，默认 .../releases/download/v<版本>-os-preview
#   FOXOS_ISO_NAME      ISO 文件名，默认 FoxOS-<版本>-amd64.iso
#   FOXOS_SUMS_URL      SHA256SUMS 地址，默认 <Release>/SHA256SUMS
#   FOXOS_ISO_URL       直接指定 ISO 地址（跳过 Release）；此时用 FOXOS_ISO_SHA256 校验
#   FOXOS_ISO_SHA256    整张 ISO 的 sha256（可选，FOXOS_ISO_URL 时建议必填）
#   FOXOS_PREFER_FULL=1 Release 里同时有整张 ISO 和分卷时，优先下载整张（默认用分卷）
set -eu

OUT=${1:-${FOXOS_OUT:-.}}
VERSION=${FOXOS_VERSION:-0.3.4}
REL=${FOXOS_RELEASE_URL:-https://github.com/gatesenman/foxos/releases/download/v${VERSION}-os-preview}
NAME=${FOXOS_ISO_NAME:-FoxOS-${VERSION}-amd64.iso}
SUMS_URL=${FOXOS_SUMS_URL:-$REL/SHA256SUMS}
ISO="$OUT/$NAME"

log() { printf '[foxos-fetch] %s\n' "$*"; }
die() { printf '[foxos-fetch] 错误：%s\n' "$*" >&2; exit 1; }

if command -v wget >/dev/null 2>&1; then
  fetch() { wget -q --show-progress --progress=dot:giga -c -O "$2" "$1"; }
elif command -v curl >/dev/null 2>&1; then
  fetch() { curl -fL --retry 3 -C - -o "$2" "$1"; }
else
  die "需要 wget 或 curl"
fi

# sum_of <文件名>：从 SHA256SUMS 里取出该文件的 sha256（兼容 "./名字" 和 "*名字"）
sum_of() {
  awk -v n="$1" '{ f=$2; sub(/^\*/, "", f); sub(/^\.\//, "", f); if (f == n) { print $1; exit } }' "$OUT/SHA256SUMS"
}
check() { # check <sha256> <路径>
  [ "$(sha256sum "$2" | awk '{print $1}')" = "$1" ]
}

mkdir -p "$OUT"

if [ -n "${FOXOS_ISO_URL:-}" ]; then
  log "下载 $FOXOS_ISO_URL"
  fetch "$FOXOS_ISO_URL" "$ISO"
  if [ -n "${FOXOS_ISO_SHA256:-}" ]; then
    check "$FOXOS_ISO_SHA256" "$ISO" || die "ISO 校验和不匹配（FOXOS_ISO_SHA256）"
    log "校验通过：$ISO"
  else
    log "警告：没有 FOXOS_ISO_SHA256，未做校验" >&2
  fi
  exit 0
fi

log "版本 $VERSION，Release：$REL"
rm -f "$OUT/SHA256SUMS"
fetch "$SUMS_URL" "$OUT/SHA256SUMS" || die "无法下载 $SUMS_URL"
FULL_SUM=$(sum_of "$NAME")
[ -n "$FULL_SUM" ] || die "SHA256SUMS 里没有 $NAME"
if [ -n "${FOXOS_ISO_SHA256:-}" ] && [ "$FOXOS_ISO_SHA256" != "$FULL_SUM" ]; then
  die "FOXOS_ISO_SHA256 与 Release 的 SHA256SUMS 不一致"
fi

if [ -f "$ISO" ] && check "$FULL_SUM" "$ISO"; then
  log "已有 ISO 且校验通过：$ISO"
  exit 0
fi

# 分卷：SHA256SUMS 里所有 <名字>.part-NN（也接受旧的 .partN），按名字排序
PARTS=$(awk -v n="$NAME" '{ f=$2; sub(/^\*/, "", f); sub(/^\.\//, "", f);
  if (index(f, n ".part") == 1) print f }' "$OUT/SHA256SUMS" | sort)

download_full() {
  log "下载整张 ISO：$NAME"
  fetch "$REL/$NAME" "$ISO.download"
  check "$FULL_SUM" "$ISO.download" || { rm -f "$ISO.download"; return 1; }
  mv "$ISO.download" "$ISO"
}

if [ -z "$PARTS" ] || [ "${FOXOS_PREFER_FULL:-0}" = 1 ]; then
  download_full || die "整张 ISO 校验失败"
else
  COUNT=$(printf '%s\n' "$PARTS" | wc -l | tr -d ' ')
  log "按 SHA256SUMS 下载 $COUNT 个分卷并拼接"
  rm -f "$ISO.assemble"
  : > "$ISO.assemble"
  i=0
  for P in $PARTS; do
    i=$((i + 1))
    PSUM=$(sum_of "$P")
    log "分卷 $i/$COUNT：$P"
    tries=0
    while :; do
      tries=$((tries + 1))
      fetch "$REL/$P" "$OUT/$P" || true
      if check "$PSUM" "$OUT/$P"; then break; fi
      rm -f "$OUT/$P"
      [ "$tries" -lt 2 ] || { rm -f "$ISO.assemble"; die "分卷 $P 校验失败"; }
      log "分卷 $P 校验失败，重新下载一次"
    done
    log "分卷 $P 校验通过"
    cat "$OUT/$P" >> "$ISO.assemble"
    rm -f "$OUT/$P"
  done
  check "$FULL_SUM" "$ISO.assemble" || { rm -f "$ISO.assemble"; die "拼接后的 ISO 校验失败"; }
  mv "$ISO.assemble" "$ISO"
fi

log "校验通过：$ISO（sha256 $FULL_SUM）"
ls -l "$ISO"
