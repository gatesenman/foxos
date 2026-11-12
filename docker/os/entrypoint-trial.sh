#!/bin/sh
# 用 cloud-hypervisor（狐狸OS 自己的 VMM）在有 KVM 的宿主上引导 *真正的* ISO。
# 这是 Docker Hub / GHCR 分发与试用通道，不是狐狸OS 的运行时；容器里不画一个假桌面。
set -eu

VERSION=${FOXOS_VERSION:-0.3.4}
ISO_DIR=${FOXOS_ISO_DIR:-/var/lib/foxos}
ISO_PATH=${FOXOS_ISO_PATH:-$ISO_DIR/${FOXOS_ISO_NAME:-FoxOS-${VERSION}-amd64.iso}}
FETCH=${FOXOS_FETCH:-/usr/local/bin/foxos-fetch-iso}
MEM=${FOXOS_MEM:-4G}
CPUS=${FOXOS_CPUS:-2}
VNC_PORT=${FOXOS_VNC_PORT:-5900}
WEB_PORT=${FOXOS_WEB_PORT:-6080}
CH=${CLOUD_HYPERVISOR:-/usr/lib/foxos/vmm/cloud-hypervisor}

log() { printf '[foxos-docker] %s\n' "$*"; }
die() { printf '[foxos-docker] 错误：%s\n' "$*" >&2; exit 1; }

if [ ! -e /dev/kvm ]; then
  die "这个容器没有 /dev/kvm。狐狸OS 的完整桌面试用需要宿主的 KVM（Linux 内核的虚拟化接口），请加上 --device /dev/kvm（通常还要 --device /dev/net/tun --cap-add NET_ADMIN，或 --privileged）。没有 KVM 时请改用 GitHub Release 里的 ISO 在真实电脑或 Hyper-V 上启动，不要指望容器里出现一个假桌面。"
fi
if [ ! -r /dev/kvm ] || [ ! -w /dev/kvm ]; then
  die "/dev/kvm 不可读写。请检查设备权限，或用 --group-add keep-groups / 加入 kvm 组。"
fi
[ -x "$CH" ] || die "找不到 cloud-hypervisor（$CH）"

# 下载并校验 ISO：默认从 v${VERSION}-os-preview 的 Release 读 SHA256SUMS，
# 按里面列出的分卷下载、拼接、逐卷和整张校验；已有且校验通过的 ISO 不会重下。
# 自己挂进来的 ISO（FOXOS_ISO_PATH 指向已存在的文件）只在给了 FOXOS_ISO_SHA256 时校验。
if [ -n "${FOXOS_ISO_PATH:-}" ] && [ -f "$ISO_PATH" ]; then
  if [ -n "${FOXOS_ISO_SHA256:-}" ]; then
    [ "$(sha256sum "$ISO_PATH" | awk '{print $1}')" = "$FOXOS_ISO_SHA256" ] || die "ISO 校验和不匹配"
    log "ISO sha256 校验通过"
  else
    log "使用挂载的 ISO：$ISO_PATH（未设置 FOXOS_ISO_SHA256，跳过校验）"
  fi
else
  FOXOS_VERSION=$VERSION FOXOS_ISO_NAME=$(basename "$ISO_PATH") "$FETCH" "$(dirname "$ISO_PATH")" \
    || die "下载或校验 ISO 失败"
fi

# 从 ISO 取出内核和 initrd，用与产品相同的 casper 参数直接引导（避免再套一层 GRUB）。
WORKDIR=$(mktemp -d)
log "从 ISO 提取 /casper/vmlinuz 与 initrd"
xorriso -osirrox on -indev "$ISO_PATH" -extract /casper/vmlinuz "$WORKDIR/vmlinuz" -extract /casper/initrd "$WORKDIR/initrd" >/dev/null 2>&1 \
  || die "无法从 ISO 提取内核（xorriso -extract）"
chmod 644 "$WORKDIR/vmlinuz" "$WORKDIR/initrd"

# 给来宾一张 TAP，把容器的 5900 转到虚拟机（x11vnc 在 foxos.vnc 参数下监听）。
TAP=${FOXOS_TAP:-foxos0}
ip link show "$TAP" >/dev/null 2>&1 || ip tuntap add dev "$TAP" mode tap
ip addr show dev "$TAP" | grep -q '172.30.0.1' || ip addr add 172.30.0.1/24 dev "$TAP" || true
ip link set "$TAP" up
# IPv4 转发 + DNAT：宿主机连容器的 5900，转到来宾 172.30.0.2:5900
if [ "$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null)" != 1 ]; then
  (echo 1 > /proc/sys/net/ipv4/ip_forward) 2>/dev/null \
    || log "警告：无法打开 IPv4 转发（/proc/sys 只读）；端口不通时请加 --sysctl net.ipv4.ip_forward=1"
fi
iptables -t nat -C PREROUTING -p tcp --dport "$VNC_PORT" -j DNAT --to-destination 172.30.0.2:5900 2>/dev/null \
  || iptables -t nat -A PREROUTING -p tcp --dport "$VNC_PORT" -j DNAT --to-destination 172.30.0.2:5900
iptables -C FORWARD -i eth0 -o "$TAP" -p tcp -d 172.30.0.2 --dport 5900 -j ACCEPT 2>/dev/null \
  || iptables -A FORWARD -i eth0 -o "$TAP" -p tcp -d 172.30.0.2 --dport 5900 -j ACCEPT
iptables -t nat -C POSTROUTING -o "$TAP" -j MASQUERADE 2>/dev/null \
  || iptables -t nat -A POSTROUTING -o "$TAP" -j MASQUERADE

# 可选：容器里起 noVNC，浏览器打开 http://localhost:6080
if [ "${FOXOS_NOVNC:-1}" = 1 ] && command -v websockify >/dev/null; then
  WEBROOT=${NOVNC_WEB:-/usr/share/novnc}
  if [ -d "$WEBROOT" ]; then
    log "noVNC 在 0.0.0.0:${WEB_PORT} （连到来宾 VNC 5900）"
    websockify --web="$WEBROOT" "0.0.0.0:${WEB_PORT}" "172.30.0.2:5900" >/tmp/novnc.log 2>&1 &
  fi
fi

CMDLINE="boot=casper hostname=foxos username=foxos locale=zh_CN.UTF-8 timezone=Asia/Shanghai keyboard-configuration/layoutcode=us console=ttyS0,115200n8 foxos.vnc ip=172.30.0.2::172.30.0.1:255.255.255.0:foxos:eth0:off ---"
log "用 cloud-hypervisor 引导真实 ISO（内存 $MEM，CPU $CPUS）"
log "桌面：来宾 XFCE 上的 x11vnc（不是容器里画的假桌面）。请等图形会话起来后访问 VNC 端口 ${VNC_PORT} 或 http://<host>:${WEB_PORT}"
exec "$CH" \
  --cpus "boot=${CPUS}" \
  --memory "size=${MEM}" \
  --kernel "$WORKDIR/vmlinuz" \
  --initramfs "$WORKDIR/initrd" \
  --cmdline "$CMDLINE" \
  --disk "path=${ISO_PATH},readonly=on" \
  --net "tap=${TAP},mac=52:54:00:f0:0d:01" \
  --serial tty \
  --console off
