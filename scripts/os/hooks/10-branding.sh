#!/bin/sh
set -eu
SRC=/usr/src/foxos-os
# 操作系统身份
cp "$SRC/branding/os-release" /etc/os-release
cp "$SRC/branding/lsb-release" /etc/lsb-release
cp "$SRC/branding/issue" /etc/issue
cp "$SRC/branding/issue.net" /etc/issue.net
echo foxos > /etc/hostname
install -m 644 "$SRC/branding/locale" /etc/default/locale
# 不要留下 Ubuntu 的默认 motd / 法律声明广告
rm -f /etc/legal /etc/update-motd.d/10-help-text /etc/update-motd.d/60-unminimize /etc/update-motd.d/91-contract-ua-esm-status 2>/dev/null || true
# 壁纸与图标
install -d /usr/share/backgrounds/foxos /usr/share/pixmaps /usr/share/icons/hicolor/256x256/apps
install -m 644 "$SRC/branding/wallpaper.png" /usr/share/backgrounds/foxos/default.png
# 从仓库图标复制
if [ -f "$SRC/icons/icon-256.png" ]; then
  install -m 644 "$SRC/icons/icon-256.png" /usr/share/pixmaps/foxos.png
  install -m 644 "$SRC/icons/icon-256.png" /usr/share/icons/hicolor/256x256/apps/foxos.png
fi
# 默认用户目录里的壁纸指向
install -d /etc/skel/.config
# 不写 /etc/debian_chroot：否则 bash 提示符会多出「(foxos)」前缀
rm -f /etc/debian_chroot
# 机器 id 在 Live / 安装时重新生成
truncate -s 0 /etc/machine-id || true
rm -f /var/lib/dbus/machine-id || true
