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

x "xfce4-terminal --geometry=96x26+140+96" >/dev/null 2>&1 &
sleep 4
WID=$(x "xdotool search --sync --onlyvisible --class xfce4-terminal" | tail -1)
x "xdotool windowactivate --sync $WID"
sleep 1
x "xdotool type --delay 15 'clear; grep PRETTY /etc/os-release; echo \$XDG_CURRENT_DESKTOP \$LANG'"
x "xdotool key Return"; sleep 1
x "xdotool type --delay 15 'foxos desktop windows'"
x "xdotool key Return"; sleep 3
x "scrot -o /tmp/os-desktop-session.png"
cp "$R/tmp/os-desktop-session.png" "$OUT/os-desktop-session.png"
x "scrot -o -u /tmp/os-terminal.png"
cp "$R/tmp/os-terminal.png" "$OUT/os-terminal.png"
x "xfce4-popup-whiskermenu" >/dev/null 2>&1 || true
sleep 3
x "scrot -o /tmp/os-desktop.png"
cp "$R/tmp/os-desktop.png" "$OUT/os-desktop.png"
x "xdotool key Escape"; sleep 1
# 编辑器：Mousepad 打开一份中文说明
cat > "$R/home/foxos/欢迎使用狐狸OS.txt" <<'TXT'
欢迎使用狐狸OS

这是一台真实的 Ubuntu 24.04 + XFCE 电脑：
  · 开始菜单在左下角「开始」
  · 底栏右侧是时钟、人工接管和系统
  · 智能体用 foxos desktop 列出、聚焦、键入、点击和截图

Ctrl+空格 切换拼音输入。
TXT
chroot "$R" chown foxos:foxos "/home/foxos/欢迎使用狐狸OS.txt"
x "xdotool search --class xfce4-terminal windowminimize" >/dev/null 2>&1 || true
x "mousepad /home/foxos/欢迎使用狐狸OS.txt" >/dev/null 2>&1 &
sleep 5
MW=$(x "xdotool search --sync --onlyvisible --class mousepad" | tail -1)
x "xdotool windowsize $MW 900 560 windowmove $MW 300 160 windowactivate --sync $MW" || true
sleep 2
x "scrot -o -u -b /tmp/os-editor.png"
cp "$R/tmp/os-editor.png" "$OUT/os-editor.png"
# 窗口信息供核对：会话确实是 xfwm4 下的 foxos 用户
x "wmctrl -m" > "$OUT/wm.txt" 2>&1 || true
x "id; echo \$LANG \$LANGUAGE" >> "$OUT/wm.txt" 2>&1 || true
x "sh -c 'foxos desktop windows; echo rc=\$?; foxos desktop status'" >> "$OUT/wm.txt" 2>&1 || true
chown -R "${SUDO_UID:-0}:${SUDO_GID:-0}" "$OUT"
echo "截图已写入 $OUT"
