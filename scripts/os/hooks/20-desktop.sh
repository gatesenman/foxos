#!/bin/sh
set -eu
SRC=/usr/src/foxos-os
# labwc 系统级默认配置（每个用户的 ~/.config/labwc 可覆盖）
install -d /etc/xdg/labwc /usr/share/themes/FoxOS/openbox-3 /usr/share/wayland-sessions
install -m 644 "$SRC/branding/labwc/rc.xml" /etc/xdg/labwc/rc.xml
install -m 644 "$SRC/branding/labwc/menu.xml" /etc/xdg/labwc/menu.xml
install -m 644 "$SRC/branding/labwc/environment" /etc/xdg/labwc/environment
install -m 755 "$SRC/branding/labwc/autostart" /etc/xdg/labwc/autostart
install -m 644 "$SRC/branding/labwc/themerc" /usr/share/themes/FoxOS/openbox-3/themerc
install -m 644 "$SRC/branding/session/foxos.desktop" /usr/share/wayland-sessions/foxos.desktop
# 登录器
install -d /etc/lightdm /etc/lightdm/lightdm.conf.d
install -m 644 "$SRC/branding/lightdm/lightdm.conf" /etc/lightdm/lightdm.conf
install -m 644 "$SRC/branding/lightdm/lightdm-gtk-greeter.conf" /etc/lightdm/lightdm-gtk-greeter.conf
# Live 自动登录检测
install -d /usr/lib/foxos
install -m 755 "$SRC/branding/live-autologin" /usr/lib/foxos/live-autologin
install -d /etc/systemd/system/lightdm.service.d
cat > /etc/systemd/system/lightdm.service.d/foxos-live.conf <<'U'
[Service]
ExecStartPre=/usr/lib/foxos/live-autologin
U
# 面板
install -d /usr/lib/foxos/panel
install -m 755 "$SRC/panel/foxos-panel" /usr/lib/foxos/panel/foxos-panel
install -d /usr/share/applications
install -m 644 "$SRC/panel/foxos-panel.desktop" /usr/share/applications/foxos-panel.desktop
# casper Live 用户
install -m 644 "$SRC/branding/casper.conf" /etc/casper.conf
# 默认图形目标
systemctl set-default graphical.target
systemctl enable lightdm.service || true
systemctl enable NetworkManager.service || true
# 输入法默认（简体拼音）
install -d /etc/xdg/fcitx5
printf '%s
' '[Groups/0]' 'Name=Default' 'Default Layout=us' 'DefaultIM=pinyin'   '[Groups/0/Items/0]' 'Name=pinyin' 'Layout='   '[GroupOrder]' '0=Default' > /etc/xdg/fcitx5/profile

# 物理键盘 US；中文输入用法是 fcitx5。casper 也会按 cmdline layoutcode 改写。
cat > /etc/default/keyboard <<'U'
XKBMODEL="pc105"
XKBLAYOUT="us"
XKBVARIANT=""
XKBOPTIONS=""
BACKSPACE="guess"
U
# NetworkManager + netplan：默认接管所有网卡并走 DHCP
install -d /etc/netplan
install -m 600 "$SRC/branding/netplan/01-foxos.yaml" /etc/netplan/01-foxos.yaml
# Live 下 casper-md5check 没有我们的 md5sum.txt，会报失败；关掉以免吓到用户
systemctl mask casper-md5check.service 2>/dev/null || true
