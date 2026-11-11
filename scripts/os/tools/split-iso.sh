#!/bin/sh
# 把 ISO 切成不超过 0.8 GiB 的分卷（FoxOS-x.y.z-amd64.iso.part-aa …），并在 SHA256SUMS 里同时记录整盘与各分卷。
# 用法：split-iso.sh build/os/FoxOS-0.3.1-amd64.iso [每份字节数，默认 858993459 = 0.8 GiB]
set -eu
ISO=$1
PART=${2:-858993459}
DIR=$(dirname "$ISO")
NAME=$(basename "$ISO")
cd "$DIR"
rm -f "$NAME".part-*
split -b "$PART" -d -a 2 "$NAME" "$NAME.part-"
{
  sha256sum "$NAME"
  sha256sum "$NAME".part-*
} > SHA256SUMS
for p in "$NAME".part-*; do
  s=$(stat -c%s "$p")
  [ "$s" -le "$PART" ] || { echo "split-iso: $p is $s bytes" >&2; exit 1; }
done
cat "$NAME".part-* | sha256sum | awk -v want="$(sha256sum "$NAME" | cut -d' ' -f1)" '{ if ($1 != want) { print "split-iso: parts do not reassemble" > "/dev/stderr"; exit 1 } }'
ls -l "$NAME".part-*
