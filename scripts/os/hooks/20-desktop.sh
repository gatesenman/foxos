#!/bin/sh
set -eu
SRC=/usr/src/foxos-os

# 去掉不再作为登录会话的 labwc（REPACK 或旧 chroot 可能还装着）
if dpkg -s labwc >/dev/null 2>&1; then
  # 不要 purge libgtk-layer-shell0：xfce4-whiskermenu-plugin 依赖它，删了开始菜单会一起被卸掉
  apt-get purge -y labwc swaybg grim wayvnc slurp wl-clipboard wtype \
    gir1.2-gtklayershell-0.1 gnome-terminal gnome-text-editor 2>/dev/null || true
  apt-get autoremove -y --purge 2>/dev/null || true
fi

# 桌面关键组件缺一不可：开始菜单、面板插件、终端、图标主题、中文翻译
missing=""
for pkg in xfce4-whiskermenu-plugin xfce4-genmon-plugin xfce4-terminal papirus-icon-theme \
  language-pack-zh-hans fonts-noto-cjk; do
  dpkg -s "$pkg" >/dev/null 2>&1 || missing="$missing $pkg"
done
if [ -n "$missing" ]; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold $missing
fi
for f in /usr/lib/x86_64-linux-gnu/xfce4/panel/plugins/libwhiskermenu.so \
  /usr/lib/x86_64-linux-gnu/xfce4/panel/plugins/libgenmon.so \
  /usr/share/icons/Papirus/index.theme \
  /usr/share/locale/zh_CN/LC_MESSAGES/xfce4-whiskermenu-plugin.mo \
  /usr/share/locale/zh_CN/LC_MESSAGES/xfce4-terminal.mo; do
  [ -e "$f" ] || { echo "20-desktop: 缺少 $f" >&2; exit 1; }
done
gtk-update-icon-cache -f /usr/share/icons/Papirus 2>/dev/null || true

# 开始菜单里不该出现的依赖带进来的条目（KDE 后台服务、Wayland 启动器、Python 解释器等）
for f in kcm_trash ktelnetservice5 org.kde.kded5 org.kde.kwalletd5 fcitx5-wayland-launcher \
  org.freedesktop.Xwayland python3.12 x11vnc calamares; do
  d=/usr/share/applications/$f.desktop
  [ -f "$d" ] || continue
  grep -q '^NoDisplay=true' "$d" || sed -i '0,/^\[Desktop Entry\]/s//[Desktop Entry]\nNoDisplay=true/' "$d"
done

# 狐狸OS 会话（X11 / XFCE）
install -d /usr/share/xsessions /usr/share/wayland-sessions
install -m 644 "$SRC/branding/session/foxos.desktop" /usr/share/xsessions/foxos.desktop
# 不提供 wayland-sessions 里的狐狸OS 项，避免登录器走到未作为产品会话维护的 Wayland 路径
rm -f /usr/share/wayland-sessions/foxos.desktop

# 主题
python3 "$SRC/branding/xfce/gen-theme.py" /usr/share/themes/FoxOS
install -d /usr/share/doc/foxos
install -m 644 "$SRC/branding/xfce/ATTRIBUTION.md" /usr/share/doc/foxos/ATTRIBUTION.desktop.md

# 系统级 XFCE 默认配置（用户尚未写 ~/.config 时生效）
install -d /etc/xdg/xfce4/xfconf/xfce-perchannel-xml /etc/xdg/xfce4/panel /etc/xdg/xfce4/whiskermenu
install -m 644 "$SRC/branding/xfce/panel/default.xml" /etc/xdg/xfce4/panel/default.xml
install -m 644 "$SRC/branding/xfce/panel/whiskermenu-1.rc" /etc/xdg/xfce4/panel/whiskermenu-1.rc
install -m 644 "$SRC/branding/xfce/panel/genmon-9.rc" /etc/xdg/xfce4/panel/genmon-9.rc
install -m 644 "$SRC/branding/xfce/whiskermenu-defaults.rc" /etc/xdg/xfce4/whiskermenu/defaults.rc
install -m 644 "$SRC/branding/xfce/helpers.rc" /etc/xdg/xfce4/helpers.rc
for f in xfce4-panel.xml xsettings.xml xfwm4.xml xfce4-desktop.xml xfce4-session.xml xfce4-terminal.xml; do
  install -m 644 "$SRC/branding/xfce/xfconf/$f" "/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/$f"
done

# 新用户骨架
install -d /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml \
  /etc/skel/.config/xfce4/panel \
  /etc/skel/.config/xfce4/whiskermenu \
  /etc/skel/.config/gtk-3.0 \
  /etc/skel/FoxOS/workspace
for f in xfce4-panel.xml xsettings.xml xfwm4.xml xfce4-desktop.xml xfce4-session.xml xfce4-terminal.xml; do
  install -m 644 "$SRC/branding/xfce/xfconf/$f" "/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/$f"
done
install -m 644 "$SRC/branding/xfce/panel/whiskermenu-1.rc" /etc/skel/.config/xfce4/panel/whiskermenu-1.rc
install -m 644 "$SRC/branding/xfce/panel/genmon-9.rc" /etc/skel/.config/xfce4/panel/genmon-9.rc
install -m 644 "$SRC/branding/xfce/whiskermenu-defaults.rc" /etc/skel/.config/xfce4/whiskermenu/defaults.rc
install -m 644 "$SRC/branding/xfce/gtk-3.0/settings.ini" /etc/skel/.config/gtk-3.0/settings.ini
install -m 644 "$SRC/branding/xfce/gtk-3.0/user-gtk.css" /etc/skel/.config/gtk-3.0/gtk.css
# 用户 gtk.css 只放终端留白（xfce4-terminal 自己的样式优先级高于主题）；主题本身已经 @import Adwaita。
install -d /etc/xdg/gtk-3.0
install -m 644 "$SRC/branding/xfce/gtk-3.0/settings.ini" /etc/xdg/gtk-3.0/settings.ini

# 环境变量（会话与用户服务）
install -d /etc/environment.d
install -m 644 "$SRC/branding/xfce/99-foxos.conf" /etc/environment.d/99-foxos.conf
# LightDM / 登录会话也能读到
install -d /usr/share/foxos
install -m 644 "$SRC/branding/xfce/environment" /usr/share/foxos/environment
# 让 startxfce4 / xinit 带上输入法与语言
install -d /etc/X11/Xsession.d
cat > /etc/X11/Xsession.d/70foxos <<'U'
# 狐狸OS 会话环境
[ -f /usr/share/foxos/environment ] && set -a && . /usr/share/foxos/environment && set +a
export XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-XFCE}"
export XDG_SESSION_DESKTOP="${XDG_SESSION_DESKTOP:-foxos}"
export XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-x11}"
U

# 登录后默认设置、输入法、按需 VNC
install -d /usr/lib/foxos/session /etc/xdg/autostart
install -m 755 "$SRC/branding/xfce/apply-defaults" /usr/lib/foxos/session/apply-defaults
install -m 755 "$SRC/branding/xfce/maybe-x11vnc" /usr/lib/foxos/session/maybe-x11vnc
install -m 644 "$SRC/branding/xfce/autostart/foxos-defaults.desktop" /etc/xdg/autostart/foxos-defaults.desktop
install -m 644 "$SRC/branding/xfce/autostart/fcitx5.desktop" /etc/xdg/autostart/fcitx5.desktop
install -m 644 "$SRC/branding/xfce/autostart/foxos-vnc.desktop" /etc/xdg/autostart/foxos-vnc.desktop

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

# 面板附属：系统菜单、人工接管（不再用自定义整条 GTK 底栏）
install -d /usr/lib/foxos/panel /usr/share/applications
install -m 755 "$SRC/panel/foxos-takeover" /usr/lib/foxos/panel/foxos-takeover
install -m 755 "$SRC/panel/foxos-takeover-genmon" /usr/lib/foxos/panel/foxos-takeover-genmon
install -m 644 "$SRC/panel/foxos-system.desktop" /usr/share/applications/foxos-system.desktop
install -m 755 "$SRC/panel/foxos-system-genmon" /usr/lib/foxos/panel/foxos-system-genmon
install -m 755 "$SRC/panel/foxos-clock-genmon" /usr/lib/foxos/panel/foxos-clock-genmon
for id in 7 10; do
  install -m 644 "$SRC/branding/xfce/panel/genmon-$id.rc" /etc/xdg/xfce4/panel/genmon-$id.rc
  install -m 644 "$SRC/branding/xfce/panel/genmon-$id.rc" /etc/skel/.config/xfce4/panel/genmon-$id.rc
done
rm -f /usr/share/applications/foxos-panel.desktop /usr/lib/foxos/panel/foxos-panel

# casper Live 用户
install -m 644 "$SRC/branding/casper.conf" /etc/casper.conf

# 默认图形目标
systemctl set-default graphical.target
systemctl enable lightdm.service || true
systemctl enable NetworkManager.service || true

# 输入法：默认英文键盘，Ctrl+空格 切到简体拼音（DefaultIM）。
# 键盘必须排第一：否则开机就是拼音，xdotool / 智能体键入的英文会变成汉字候选。
install -d /etc/xdg/fcitx5
printf '%s\n' '[Groups/0]' 'Name=Default' 'Default Layout=us' 'DefaultIM=pinyin' \
  '[Groups/0/Items/0]' 'Name=keyboard-us' 'Layout=' \
  '[Groups/0/Items/1]' 'Name=pinyin' 'Layout=' \
  '[GroupOrder]' '0=Default' > /etc/xdg/fcitx5/profile

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
