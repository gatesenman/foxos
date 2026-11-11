#!/bin/sh
# 端到端测试用的“狐狸OS 电脑”：把狐狸OS 的根文件系统（ISO 里的 chroot）跑成一台只听 127.0.0.1 的来宾——
# sshd（密钥登录）、Xvfb :0 上的 XFCE 桌面会话、来宾里的 foxos。桌面客户端用它代替虚拟机测试“所有动作都在来宾里执行”。
# 用法（root）：
#   foxos-guest-chroot.sh start <rootfs> <ssh端口> <公钥文件> [要装进来宾的 packages/core 目录]
#   foxos-guest-chroot.sh stop  <rootfs>
set -eu
cmd=$1; R=$(cd "$2" && pwd)

stop() {
  for p in /proc/[0-9]*; do
    r=$(readlink "$p/root" 2>/dev/null || true)
    case "$r" in "$R"|"$R"/*) kill -9 "${p#/proc/}" 2>/dev/null || true ;; esac
  done
  [ -f "$R/run/foxos-e2e-xvfb.pid" ] && kill "$(cat "$R/run/foxos-e2e-xvfb.pid")" 2>/dev/null || true
  sleep 1
  for m in dev/pts dev sys proc; do umount -l "$R/$m" 2>/dev/null || true; done
}

if [ "$cmd" = stop ]; then stop; exit 0; fi

PORT=$3; PUB=$4; CORE=${5:-}
grep -q '^ID=foxos' "$R/etc/os-release" || { echo "not a FoxOS rootfs: $R" >&2; exit 2; }
mountpoint -q "$R/proc" || mount -t proc proc "$R/proc"
mountpoint -q "$R/sys" || mount -t sysfs sys "$R/sys"
mountpoint -q "$R/dev" || mount --bind /dev "$R/dev"
mountpoint -q "$R/dev/pts" || mount -t devpts devpts "$R/dev/pts" -o newinstance,ptmxmode=0666 2>/dev/null || mount --bind /dev/pts "$R/dev/pts"
cp -L /etc/resolv.conf "$R/etc/resolv.conf" 2>/dev/null || true
if [ -n "$CORE" ]; then
  # 来宾里的 foxos 换成被测版本（相当于装了这一版的狐狸OS）
  rm -rf "$R/usr/lib/foxos/python/foxos" && cp -r "$CORE/foxos" "$R/usr/lib/foxos/python/foxos"
  find "$R/usr/lib/foxos/python/foxos" -name __pycache__ -prune -exec rm -rf {} +
fi
chroot "$R" sh -c 'id foxos >/dev/null 2>&1 || useradd -m -s /bin/bash foxos; usermod -p "*" foxos; echo "foxos ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-foxos-e2e; chmod 440 /etc/sudoers.d/90-foxos-e2e'
install -d -m 700 "$R/home/foxos/.ssh"
cp "$PUB" "$R/home/foxos/.ssh/authorized_keys"
chroot "$R" sh -c 'chown -R foxos:foxos /home/foxos/.ssh && chmod 600 /home/foxos/.ssh/authorized_keys && ssh-keygen -A >/dev/null && mkdir -p /run/sshd'
chroot "$R" /usr/sbin/sshd -p "$PORT" -o ListenAddress=127.0.0.1 -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o UsePAM=no -o PidFile=/run/foxos-e2e-sshd.pid
# 显示 :0：Xvfb 跑在宿主上，但在私有挂载命名空间里把 /tmp 换成来宾的 /tmp（套接字落在来宾里）
mkdir -p "$R/tmp/.X11-unix" && chmod 1777 "$R/tmp" "$R/tmp/.X11-unix"
rm -f "$R/tmp/.X11-unix/X0" "$R/tmp/.X0-lock"
unshare -m sh -c "mount --bind '$R/tmp' /tmp && exec Xvfb :0 -screen 0 1280x800x24 -nolisten tcp" >/dev/null 2>&1 &
echo $! > "$R/run/foxos-e2e-xvfb.pid"
for i in $(seq 1 50); do [ -S "$R/tmp/.X11-unix/X0" ] && break; sleep 0.2; done
chroot "$R" su - foxos -c 'DISPLAY=:0 nohup dbus-launch --exit-with-session startxfce4 >/tmp/foxos-e2e-xfce.log 2>&1 &'
echo "guest ready: ssh -p $PORT foxos@127.0.0.1"
