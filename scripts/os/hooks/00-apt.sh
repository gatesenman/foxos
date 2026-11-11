#!/bin/sh
set -eu
# 开启 universe，生成中文 locale，时区默认上海（安装器可改）
export DEBIAN_FRONTEND=noninteractive
sed -i 's/^# *deb /deb /' /etc/apt/sources.list || true
apt-get update
apt-get install -y locales tzdata
sed -i 's/^# *zh_CN.UTF-8/zh_CN.UTF-8/; s/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
locale-gen
update-locale LANG=zh_CN.UTF-8 LANGUAGE=zh_CN:zh
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo Asia/Shanghai > /etc/timezone
