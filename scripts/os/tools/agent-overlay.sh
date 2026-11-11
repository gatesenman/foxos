#!/bin/bash
# 在 ISO 构建出的根文件系统上叠一层 overlay（不修改 chroot 本身），把当前仓库的 foxos、hooks 30/35、
# 智能体窗口与运行环境装进去，然后以 Live 用户 foxos 运行检查或启动真实 XFCE 会话截图。
# 这等同于 ISO 里 hook 阶段之后的系统，用来在不重新打包 ISO 的情况下做端到端验证。
# 用法（root）：
#   agent-overlay.sh up            挂载并运行 apt（新增的包）+ hook 30 + hook 35
#   agent-overlay.sh as-foxos CMD  以 foxos 用户运行命令（PATH 与登录后一致）
#   agent-overlay.sh desktop       启动 Xvfb + XFCE 会话（DISPLAY=$FOXOS_OVL_DISPLAY，默认 :96）
#   agent-overlay.sh shot FILE     截整屏
#   agent-overlay.sh down          卸载并删除 overlay
set -euo pipefail
WORK=${FOXOS_OS_WORK:-/var/tmp/foxos-os}
LOWER="$WORK/chroot"
OVL=${FOXOS_OVL:-/var/tmp/foxos-agentchat-ovl}
R="$OVL/root"
DISP=${FOXOS_OVL_DISPLAY:-:96}
N=${DISP#:}
SCRIPT_DIR=$(cd "$(dirname "$0")/.." && pwd)
ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
[ "$(id -u)" = 0 ] || exec sudo -E "$0" "$@"

down() {
  set +e
  pkill -f "Xvfb $DISP" 2>/dev/null
  for d in /proc/[0-9]*; do
    [ "$(readlink "$d/root" 2>/dev/null)" = "$R" ] && kill -9 "${d#/proc/}" 2>/dev/null
  done
  sleep 0.5
  for m in tmp/.X11-unix dev/pts dev proc sys run; do
    mountpoint -q "$R/$m" && umount -l "$R/$m"
  done
  mountpoint -q "$R" && umount -l "$R"
  rm -rf "$OVL"
}

as_foxos() {
  BUS=unix:path=/run/user/1000/bus
  unshare --uts /bin/sh -c 'hostname foxos; exec "$@"' sh \
  chroot "$R" /usr/bin/env -i HOME=/home/foxos USER=foxos LOGNAME=foxos SHELL=/bin/bash LANG=zh_CN.UTF-8 \
    PATH=/home/foxos/.local/bin:/usr/local/bin:/usr/bin:/bin DISPLAY="$DISP" XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS="$BUS" \
    /bin/sh -c "[ -f /usr/share/foxos/environment ] && { set -a; . /usr/share/foxos/environment; set +a; }; cd /home/foxos; exec setpriv --reuid=1000 --regid=1000 --init-groups $*"
}

up() {
  [ -x "$LOWER/usr/bin/startxfce4" ] || { echo "no built chroot at $LOWER" >&2; exit 1; }
  down; set -e
  mkdir -p "$OVL/upper" "$OVL/work" "$R"
  mount -t overlay overlay -o "lowerdir=$LOWER,upperdir=$OVL/upper,workdir=$OVL/work" "$R"
  mount -t proc proc "$R/proc"
  mount --rbind /sys "$R/sys"
  mount --rbind /dev "$R/dev"
  mount -t tmpfs tmpfs "$R/run"
  mkdir -p /tmp/.X11-unix "$R/tmp/.X11-unix"
  mount --bind /tmp/.X11-unix "$R/tmp/.X11-unix"
  cp /etc/resolv.conf "$R/etc/resolv.conf"
  [ -f /etc/apt/apt.conf.d/99-box-proxy ] && cp /etc/apt/apt.conf.d/99-box-proxy "$R/etc/apt/apt.conf.d/99-box-proxy"
  # 和 build-iso.sh 一样的 staging
  S="$R/usr/src/foxos-os"
  rm -rf "$S"; mkdir -p "$S/foxos-pkg"
  cp -a "$SCRIPT_DIR/branding" "$SCRIPT_DIR/panel" "$SCRIPT_DIR/systemd" "$SCRIPT_DIR/hooks" "$SCRIPT_DIR/bots" "$S/"
  cp -a "$ROOT/packages/core/foxos" "$S/foxos-pkg/"
  find "$S/foxos-pkg" -name __pycache__ -prune -exec rm -rf {} +
  PKGS=$(grep -vE '^\s*(#|$)' "$SCRIPT_DIR/config/packages.list" | tr '\n' ' ')
  chroot "$R" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update -qq
  # shellcheck disable=SC2086
  chroot "$R" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends $PKGS >/dev/null
  for h in 30-foxos.sh 35-agent-runtime.sh; do
    echo "[overlay] hook $h"
    cp "$SCRIPT_DIR/hooks/$h" "$R/tmp/$h"; chmod +x "$R/tmp/$h"
    chroot "$R" /usr/bin/env DEBIAN_FRONTEND=noninteractive PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin "/tmp/$h"
  done
  chroot "$R" sh -c 'getent passwd foxos >/dev/null || useradd -m -u 1000 -c "狐狸OS" -s /bin/bash foxos'
  chroot "$R" sh -c 'mkdir -p /run/user/1000 && chown foxos:foxos /run/user/1000 && chmod 700 /run/user/1000'
  echo "[overlay] ready at $R"
}

desktop() {
  Xvfb "$DISP" -screen 0 "${FOXOS_OVL_GEOM:-1920x1080}x24" -nolisten tcp -ac >"$OVL/xvfb.log" 2>&1 &
  for _ in $(seq 50); do [ -S "/tmp/.X11-unix/X$N" ] && break; sleep 0.2; done
  as_foxos "dbus-daemon --session --address=unix:path=/run/user/1000/bus --fork --nopidfile" >"$OVL/dbus.log" 2>&1
  sleep 1
  as_foxos "startxfce4" >"$OVL/session.log" 2>&1 &
  for _ in $(seq 60); do as_foxos "xdotool search --class xfce4-panel" >/dev/null 2>&1 && break; sleep 1; done
  sleep 6
  echo "[overlay] XFCE on $DISP"
}

case "${1:-}" in
  up) up ;;
  down) down ;;
  as-foxos) shift; as_foxos "$*" ;;
  desktop) desktop ;;
  shot) as_foxos "scrot -o /tmp/ovl-shot.png" && cp "$R/tmp/ovl-shot.png" "$2" && chmod 644 "$2" ;;
  *) sed -n 2,12p "$0"; exit 2 ;;
esac
