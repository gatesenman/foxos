#!/bin/sh
set -eu
# 丢掉构建机代理、缓存和日志，不要带进 ISO
rm -f /etc/apt/apt.conf.d/99-box-proxy
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/archives/*
# 保留 lists 为空目录
mkdir -p /var/lib/apt/lists/partial
# 构建痕迹
rm -rf /usr/src/foxos-os
# 空 machine-id，Live / 安装时再生成
truncate -s 0 /etc/machine-id || true
history -c 2>/dev/null || true
rm -f /root/.bash_history /root/.wget-hsts
