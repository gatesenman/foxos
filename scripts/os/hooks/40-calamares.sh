#!/bin/sh
set -eu
SRC=/usr/src/foxos-os
install -d /etc/calamares /etc/calamares/modules /etc/calamares/branding/foxos
cp -a "$SRC/calamares/settings.conf" /etc/calamares/settings.conf
# arm64：Calamares 模块目录在 aarch64-linux-gnu 下
if [ "$(dpkg --print-architecture)" = arm64 ]; then
  sed -i 's#/usr/lib/x86_64-linux-gnu/#/usr/lib/aarch64-linux-gnu/#' /etc/calamares/settings.conf
fi
cp -a "$SRC/calamares/modules/." /etc/calamares/modules/
cp -a "$SRC/calamares/branding/." /etc/calamares/branding/foxos/
# 开始菜单里的「安装 狐狸OS」
cat > /usr/share/applications/calamares-foxos.desktop <<'U'
[Desktop Entry]
Type=Application
Name=安装 狐狸OS
Name[en]=Install FoxOS
Comment=把狐狸OS 安装到这台电脑
Comment[en]=Install FoxOS on this computer
Exec=pkexec calamares
Icon=foxos
Categories=System;Installer;
StartupNotify=true
U
# Live 才显示安装器（安装后的系统没有 /cdrom/casper）
cat > /etc/xdg/autostart/calamares-live-only.sh <<'U'
# placeholder; the desktop file itself is always present on the live image.
# Calamares post-install removes this desktop file via a cleanup module.
U
