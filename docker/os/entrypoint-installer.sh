#!/bin/sh
# 狐狸OS 在线安装助手：只从 GitHub Release 下载 ISO 并按 SHA256SUMS 校验，不启动虚拟机。
# 版本由镜像构建参数 FOXOS_VERSION 决定（也可在 docker run 时用 -e FOXOS_VERSION= 覆盖）。
# 分卷下载、拼接和校验都在 foxos-fetch-iso 里完成。
set -eu
OUT=${FOXOS_OUT:-/out}
FETCH=${FOXOS_FETCH:-/usr/local/bin/foxos-fetch-iso}
exec "$FETCH" "$OUT"
