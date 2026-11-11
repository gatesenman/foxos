#!/bin/bash
# 用 ISO 构建出的根文件系统（只读叠一层 overlay）真实启动 XFCE 会话并截图：
# 以 Live 用户 foxos 登录、zh_CN.UTF-8、Papirus 图标、狐狸OS 主题，和 ISO 里完全一致。
# 不修改 chroot 本身；结束后卸载 overlay。
# 用法：sudo scripts/os/tools/shoot-desktop.sh OUT_DIR [宽x高]
set -euo pipefail
OUT=${1:?输出目录}
GEOM=${2:-1920x1080}
WORK=${FOXOS_OS_WORK:-/var/tmp/foxos-os}
LOWER="$WORK/chroot"
SHOT="$WORK/shot"
DISP=${FOXOS_SHOT_DISPLAY:-:95}
N=${DISP#:}
[ "$(id -u)" = 0 ] || exec sudo -E "$0" "$@"
[ -x "$LOWER/usr/bin/startxfce4" ] || { echo "找不到构建好的 chroot：$LOWER" >&2; exit 1; }
mkdir -p "$OUT"

cleanup() {
  set +e
  pkill -f "Xvfb $DISP" 2>/dev/null
  # 只结束根目录在 overlay 里的进程（不按 uid 杀，宿主上可能也有 uid 1000 的用户）
  for d in /proc/[0-9]*; do
    [ "$(readlink "$d/root" 2>/dev/null)" = "$SHOT/root" ] && kill -9 "${d#/proc/}" 2>/dev/null
  done
  sleep 0.5
  for m in tmp/.X11-unix dev/pts dev proc sys run; do
    mountpoint -q "$SHOT/root/$m" && umount -l "$SHOT/root/$m"
  done
  mountpoint -q "$SHOT/root" && umount -l "$SHOT/root"
  rm -rf "$SHOT"
}
trap cleanup EXIT
cleanup; trap cleanup EXIT
mkdir -p "$SHOT/upper" "$SHOT/work" "$SHOT/root"
mount -t overlay overlay -o "lowerdir=$LOWER,upperdir=$SHOT/upper,workdir=$SHOT/work" "$SHOT/root"
R="$SHOT/root"
mount -t proc proc "$R/proc"
mount --rbind /sys "$R/sys"
mount --rbind /dev "$R/dev"
mount -t tmpfs tmpfs "$R/run"
mkdir -p /tmp/.X11-unix "$R/tmp/.X11-unix"
mount --bind /tmp/.X11-unix "$R/tmp/.X11-unix"

# 与 Live 一样的用户：casper 创建的 foxos，全名「狐狸OS」，从 /etc/skel 拷配置
chroot "$R" sh -c 'getent passwd foxos >/dev/null || useradd -m -u 1000 -c "狐狸OS" -s /bin/bash foxos'
chroot "$R" sh -c 'mkdir -p /run/user/1000 && chown foxos:foxos /run/user/1000 && chmod 700 /run/user/1000'
echo foxos > "$R/etc/hostname"
grep -q foxos "$R/etc/hosts" 2>/dev/null || echo "127.0.1.1 foxos" >> "$R/etc/hosts"

Xvfb "$DISP" -screen 0 "${GEOM}x24" -nolisten tcp -ac >"$WORK/shot-xvfb.log" 2>&1 &
for _ in $(seq 50); do [ -S "/tmp/.X11-unix/X$N" ] && break; sleep 0.2; done

BUS=unix:path=/run/user/1000/bus
as_foxos() {
  # 独立的 UTS 命名空间，主机名与 Live 一样是 foxos
  unshare --uts /bin/sh -c 'hostname foxos; exec "$@"' sh \
  chroot "$R" /usr/bin/env -i HOME=/home/foxos USER=foxos LOGNAME=foxos SHELL=/bin/bash \
    PATH=/usr/local/bin:/usr/bin:/bin DISPLAY="$DISP" XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS="$BUS" \
    /bin/sh -c "set -a; . /usr/share/foxos/environment; set +a; cd /home/foxos; exec setpriv --reuid=1000 --regid=1000 --init-groups $*"
}

# 会话总线固定在 /run/user/1000/bus，后续 xfce4-popup-whiskermenu、终端都连到同一个 xfconfd
as_foxos "dbus-daemon --session --address=$BUS --fork --nopidfile" >"$WORK/shot-dbus.log" 2>&1
sleep 1
# 真实会话：与 LightDM 启动 foxos.desktop 一样走 startxfce4
as_foxos "startxfce4" >"$WORK/shot-session.log" 2>&1 &
x() { as_foxos "$*"; }
for _ in $(seq 60); do
  x "xdotool search --class xfce4-panel" >/dev/null 2>&1 && break; sleep 1
done
sleep 8  # 等 apply-defaults、壁纸、genmon 刷新


P=${FOXOS_SHOT_PREFIX:-os-032}   # 新文件名：GitHub 按 URL 缓存图片，换名才能让 README 立即显示新图
shot() { x "scrot -o /tmp/$P-$1.png"; cp "$R/tmp/$P-$1.png" "$OUT/$P-$1.png"; }
typeln() { x "xdotool type --delay 12 -- '$1'"; x "xdotool key Return"; sleep "${2:-2}"; }
win() { x "xdotool search --sync --onlyvisible --class $1" | tail -1; }
hide_all() { for w in $(x "wmctrl -l" | awk '$2>=0{print $1}'); do x "xdotool windowminimize $w" >/dev/null 2>&1 || true; done; }
as_root() {
  unshare --uts /bin/sh -c 'hostname foxos; exec "$@"' sh \
  chroot "$R" /usr/bin/env -i HOME=/root PATH=/usr/sbin:/usr/bin:/sbin:/bin DISPLAY="$DISP" \
    LANG=zh_CN.UTF-8 LANGUAGE=zh_CN:zh LC_ALL=zh_CN.UTF-8 /bin/sh -c "$*"
}

# FOXOS_SHOT_ONLY=chrome：只拍 Google Chrome 首次安装对话框、Chrome 窗口和 CDP 控制
if [ "${FOXOS_SHOT_ONLY:-}" = chrome ]; then
  # a) 首次使用对话框（与开始菜单「Google Chrome」、首次登录自启动是同一个）
  x "/usr/lib/foxos/foxos-chrome-setup --gui" >"$WORK/shot-chrome-gui.log" 2>&1 &
  sleep 6
  shot chrome-setup
  x "xdotool key Escape"; sleep 2
  # b) 用户点「同意并安装」后 pkexec 运行的就是这一步（这里没有 polkit 代理，直接以 root 运行同一脚本）
  rm -f "$R/etc/resolv.conf"; cp -L /etc/resolv.conf "$R/etc/resolv.conf"
  as_root "/usr/lib/foxos/foxos-chrome-setup --install" >"$WORK/shot-chrome-install.log" 2>&1
  tail -3 "$WORK/shot-chrome-install.log"
  # c) 人打开 CDP，智能体用 foxos 启动 Chrome、列标签页、读标题
  x "xfce4-terminal --geometry=96x22+60+600" >/dev/null 2>&1 &
  sleep 4
  WID=$(win xfce4-terminal)
  x "xdotool windowactivate --sync $WID"; sleep 2
  typeln 'clear; foxos browser cdp on' 3
  typeln 'foxos --agent demo-agent desktop launch chrome https://github.com/gatesenman/foxos' 20
  CW=$(win Google-chrome)
  x "xdotool windowsize $CW 1280 860 windowmove $CW 600 40" || true
  x "pkill -x zenity" >/dev/null 2>&1 || true   # 首次登录自启动的同一对话框，已经截过
  sleep 4
  x "xdotool windowactivate --sync $CW"; sleep 1
  x "xdotool key Escape"; sleep 1               # 关掉「翻译此页」气泡（界面是中文，页面是英文）
  x "xdotool mousemove 300 300"; sleep 2
  shot chrome
  x "xdotool windowactivate --sync $WID"; sleep 1
  typeln 'clear; foxos browser status' 4
  typeln 'foxos --agent demo-agent browser tabs' 4
  typeln "foxos --agent demo-agent browser eval 'document.title' --json | grep value" 4
  typeln 'foxos --agent demo-agent browser screenshot --path shots/chrome-page.png' 5
  shot chrome-cdp
  x "sh -c 'foxos browser status --json; xdg-settings get default-web-browser; readlink -f /etc/alternatives/x-www-browser'" > "$OUT/chrome.txt" 2>&1 || true
  cp "$R/home/foxos/FoxOS/workspace/shots/chrome-page.png" "$OUT/chrome-page.png" 2>/dev/null || true
  chown -R "${SUDO_UID:-0}:${SUDO_GID:-0}" "$OUT"
  echo "截图已写入 $OUT"; exit 0
fi

# 1. 终端：foxos 命令操作真实桌面与工作空间里的表格、文档
x "xfce4-terminal --geometry=110x30+120+70" >/dev/null 2>&1 &
sleep 4
WID=$(win xfce4-terminal)
x "xdotool windowactivate --sync $WID"; sleep 4
typeln 'clear; foxos desktop windows'
typeln 'foxos sheets create 2026-sales.xlsx --headers 月份,销售额' 3
typeln 'foxos sheets write 2026-sales.xlsx A2=1月 B2=1200 A3=2月 B3=1500 A4=合计 "B4==SUM(B2:B3)"' 3
typeln 'foxos sheets read 2026-sales.xlsx' 3
typeln 'foxos docs create weekly.docx --title 项目周报' 3
typeln 'foxos docs append weekly.docx 本周完成：XFCE 桌面、Papirus 图标与暖色主题。' 3
typeln 'foxos files list' 3
shot terminal

# 2. 开始菜单（终端在后面）
x "xfce4-popup-whiskermenu" >/dev/null 2>&1 || true
sleep 3
shot desktop
x "xdotool key Escape"; sleep 1

# 3. Thunar 文件管理器：工作空间里刚生成的文件
hide_all
x "thunar /home/foxos/FoxOS/workspace" >/dev/null 2>&1 &
sleep 5
TW=$(win thunar)
x "xdotool windowsize $TW 1100 680 windowmove $TW 380 150 windowactivate --sync $TW" || true
sleep 2
shot files
x "wmctrl -ic $TW" || true

# 4. Firefox
hide_all
x "firefox --new-window https://github.com/gatesenman/foxos" >/dev/null 2>&1 &
sleep 25
FW=$(win firefox)
x "xdotool windowsize $FW 1500 900 windowmove $FW 200 60 windowactivate --sync $FW" || true
sleep 4
# 首次启动的条款对话框与翻译提示：像用户一样关掉（Esc 关翻译提示，点「继续」）
x "xdotool key Escape"; sleep 1
x "xdotool mousemove 950 384 click 1"; sleep 3
x "xdotool mousemove 1700 1000"; sleep 1
shot firefox
x "wmctrl -ic $FW" || true
sleep 2

# 5. Mousepad 编辑器
cat > "$R/home/foxos/欢迎使用狐狸OS.txt" <<'TXT'
欢迎使用狐狸OS

这是一台真实的 Ubuntu 24.04 + XFCE 电脑：
  · 开始菜单在左下角「开始」
  · 底栏右侧是时钟、人工接管和系统
  · 智能体用 foxos desktop 列出、聚焦、键入、点击和截图

Ctrl+空格 切换拼音输入。
TXT
chroot "$R" chown foxos:foxos "/home/foxos/欢迎使用狐狸OS.txt"
hide_all
x "mousepad /home/foxos/欢迎使用狐狸OS.txt" >/dev/null 2>&1 &
sleep 5
MW=$(win mousepad)
x "xdotool windowsize $MW 1000 620 windowmove $MW 460 180 windowactivate --sync $MW" || true
sleep 2
shot editor
x "wmctrl -ic $MW" || true

# 6. 设置管理器
hide_all
x "xfce4-settings-manager" >/dev/null 2>&1 &
sleep 5
SW=$(win xfce4-settings-manager)
x "xdotool windowmove $SW 380 120 windowactivate --sync $SW" || true
sleep 2
shot settings
x "wmctrl -ic $SW" || true

# 7. 底栏「系统」：注销 / 关机对话框（只截图，按 Esc 取消）
hide_all
x "xfce4-session-logout" >/dev/null 2>&1 &
sleep 4
shot system
x "xdotool key Escape"; sleep 2
x "pkill -f xfce4-session-logout" >/dev/null 2>&1 || true

# 8. 人工接管：人暂停后，智能体的写操作返回 PAUSED，底栏显示「接管中」
x "xdotool windowactivate --sync $WID"; sleep 1
typeln 'clear; foxos control pause --reason 我来改一下' 3
typeln 'foxos --agent demo-agent desktop type hello; echo 退出码 $?' 4
sleep 15   # 等底栏 genmon 刷新到「接管中」
shot takeover
typeln 'foxos control resume' 3

# 9. 安装器：开始菜单「安装 狐狸OS」启动的 Calamares（Live 上经 pkexec 以 root 运行）
hide_all
as_root "calamares" >"$WORK/shot-calamares.log" 2>&1 &
sleep 20
CW=$(win calamares)
[ -n "$CW" ] && x "xdotool windowactivate --sync $CW" || true
sleep 2
shot installer
pkill -f 'calamares$' 2>/dev/null || true

# 窗口信息供核对：会话确实是 xfwm4 下的 foxos 用户
x "wmctrl -m" > "$OUT/wm.txt" 2>&1 || true
x "id; echo \$LANG \$LANGUAGE" >> "$OUT/wm.txt" 2>&1 || true
x "sh -c 'foxos desktop windows; echo rc=\$?; foxos desktop status'" >> "$OUT/wm.txt" 2>&1 || true
chown -R "${SUDO_UID:-0}:${SUDO_GID:-0}" "$OUT"
echo "截图已写入 $OUT"
