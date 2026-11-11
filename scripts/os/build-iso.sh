#!/bin/bash
# 制作狐狸OS Live + 安装 ISO（UEFI + BIOS）。必须在本仓库根目录的 scripts/os 下维护。
# 详细步骤见 docs/os-build.md。需要 root（会自行 sudo）。
# 环境变量：
#   FOXOS_OS_WORK    工作目录（默认 /var/tmp/foxos-os）
#   FOXOS_OS_OUT     输出目录（默认 <仓库>/build/os）
#   FOXOS_OS_MIRROR  Ubuntu 软件源（默认 http://archive.ubuntu.com/ubuntu）
#   FOXOS_OS_KEEP=1  结束后保留 chroot，方便排查
#   FOXOS_OS_REPACK=1  复用已有 chroot，跳过 apt / Firefox / VMM 下载，只重跑 hook 并打包
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
VERSION=0.3.1
SUITE=noble
ARCH=amd64
ISO_NAME="FoxOS-${VERSION}-amd64.iso"
VOLID="FOXOS_031"
WORK=${FOXOS_OS_WORK:-/var/tmp/foxos-os}
OUT=${FOXOS_OS_OUT:-"$ROOT/build/os"}
MIRROR=${FOXOS_OS_MIRROR:-http://archive.ubuntu.com/ubuntu}
CHROOT="$WORK/chroot"
ISO="$WORK/iso"
STAGING="$WORK/staging"   # 拷进 chroot 的 /usr/src/foxos-os

log() { printf '[foxos-os] %s\n' "$*"; }
die() { printf '[foxos-os] 错误：%s\n' "$*" >&2; exit 1; }

if [ "$(id -u)" -ne 0 ]; then
  exec sudo --preserve-env=FOXOS_OS_WORK,FOXOS_OS_OUT,FOXOS_OS_MIRROR,FOXOS_OS_KEEP,FOXOS_OS_REPACK,FOXOS_CH_VERSION,http_proxy,https_proxy,HTTP_PROXY,HTTPS_PROXY "$0" "$@"
fi

# 构建机 apt 若需代理，chroot 里同样用（收尾 hook 会删掉，不带进 ISO）
maybe_proxy() {
  if [ -f /etc/apt/apt.conf.d/99-box-proxy ]; then
    cp /etc/apt/apt.conf.d/99-box-proxy "$CHROOT/etc/apt/apt.conf.d/99-box-proxy"
  fi
}

mount_chroot() {
  mount --bind /dev "$CHROOT/dev"
  mount --bind /dev/pts "$CHROOT/dev/pts"
  mount -t proc proc "$CHROOT/proc"
  mount -t sysfs sysfs "$CHROOT/sys"
  mount -t tmpfs tmpfs "$CHROOT/run"
  cp /etc/resolv.conf "$CHROOT/etc/resolv.conf"
}

unmount_chroot() {
  if [ -d "$CHROOT" ]; then
    umount -l "$CHROOT/dev/pts" "$CHROOT/dev" "$CHROOT/proc" "$CHROOT/sys" "$CHROOT/run" 2>/dev/null || true
  fi
}
trap unmount_chroot EXIT

chroot_run() { chroot "$CHROOT" /usr/bin/env DEBIAN_FRONTEND=noninteractive "$@"; }

# ------------------------------------------------------------------ 准备目录
# 给 debootstrap 一个会超时重试的 wget，避免偶发半开连接把整个构建卡住
mkdir -p "$WORK/bin"
cat > "$WORK/bin/wget" <<'WGET'
#!/bin/sh
exec /usr/bin/wget --timeout=30 --tries=8 --retry-connrefused "$@"
WGET
chmod +x "$WORK/bin/wget"
export PATH="$WORK/bin:/usr/sbin:/usr/bin:/sbin:/bin"

log "工作目录 $WORK"
mkdir -p "$WORK" "$OUT" "$ISO/casper" "$ISO/boot/grub" "$ISO/.disk" "$STAGING"
# 把脚本、品牌、面板、仓库里的 foxos 包、图标放到 staging，供 chroot hook 使用
rsync -a --delete \
  "$SCRIPT_DIR/branding" "$SCRIPT_DIR/panel" "$SCRIPT_DIR/calamares" "$SCRIPT_DIR/systemd" "$SCRIPT_DIR/hooks" \
  "$STAGING/"
mkdir -p "$STAGING/icons" "$STAGING/foxos-pkg"
cp -a "$ROOT/assets/icons/." "$STAGING/icons/"
cp -a "$ROOT/packages/core/foxos" "$STAGING/foxos-pkg/"
# Calamares 品牌图
cp "$ROOT/assets/icons/icon-256.png" "$STAGING/calamares/branding/logo.png"
cp "$SCRIPT_DIR/branding/wallpaper.png" "$STAGING/calamares/branding/welcome.png"

# ------------------------------------------------------------------ debootstrap
if [ ! -f "$CHROOT/usr/bin/apt-get" ]; then
  log "debootstrap $SUITE（$MIRROR）"
  rm -rf "$CHROOT"
  mkdir -p "$CHROOT"
  debootstrap --arch="$ARCH" --variant=minbase --components=main,universe,restricted \
    --include=ca-certificates,wget,gnupg \
    "$SUITE" "$CHROOT" "$MIRROR"
else
  log "已有 chroot，跳过 debootstrap（删除 $CHROOT 可强制重做）"
fi

mount_chroot
maybe_proxy
cp "$SCRIPT_DIR/config/sources.list" "$CHROOT/etc/apt/sources.list"
# 若用户换了镜像，改写源
if [ "$MIRROR" != "http://archive.ubuntu.com/ubuntu" ]; then
  sed -i "s|http://archive.ubuntu.com/ubuntu|$MIRROR|g" "$CHROOT/etc/apt/sources.list"
fi

REPACK=0
if [ "${FOXOS_OS_REPACK:-0}" = 1 ] && [ -x "$CHROOT/usr/bin/startxfce4" ]; then
  REPACK=1
  log "FOXOS_OS_REPACK=1，跳过 apt / Firefox / VMM 下载，只重跑 hook 并打包"
fi

if [ "$REPACK" != 1 ]; then
log "安装软件包"
chroot_run apt-get update
# shellcheck disable=SC2046
PACKAGES=$(grep -vE '^\s*(#|$)' "$SCRIPT_DIR/config/packages.list" | tr '\n' ' ')
chroot_run apt-get install -y --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold $PACKAGES

# ------------------------------------------------------------------ 第三方（许可允许）：Firefox .deb/tarball 与 cloud-hypervisor
log "安装 Firefox（Mozilla 官方 tarball，不用 Snap）"
FF="$WORK/cache/firefox.tar.xz"
mkdir -p "$WORK/cache"
if [ ! -f "$FF" ]; then
  wget -O "$FF" "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=zh-CN"
fi
rm -rf "$CHROOT/opt/firefox"
tar -C "$CHROOT/opt" -xJf "$FF"
ln -sfn /opt/firefox/firefox "$CHROOT/usr/bin/firefox"
cat > "$CHROOT/usr/share/applications/firefox.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Firefox
Name[zh_CN]=Firefox 浏览器
Comment=浏览网页
Exec=/usr/bin/firefox %u
Icon=/opt/firefox/browser/chrome/icons/default/default128.png
Categories=Network;WebBrowser;
StartupNotify=true
MimeType=text/html;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
EOF

log "安装 cloud-hypervisor（Apache-2.0 VMM，完整虚拟机用）"
CH_VER=${FOXOS_CH_VERSION:-v46.0}
CH_URL="https://github.com/cloud-hypervisor/cloud-hypervisor/releases/download/${CH_VER}/cloud-hypervisor-static"
CH_BIN="$WORK/cache/cloud-hypervisor-static"
if [ ! -f "$CH_BIN" ]; then
  wget -O "$CH_BIN" "$CH_URL"
  chmod +x "$CH_BIN"
fi
install -d "$STAGING/vmm"
install -m 755 "$CH_BIN" "$STAGING/vmm/cloud-hypervisor"
cat > "$STAGING/vmm/NOTICE" <<EOF
cloud-hypervisor ${CH_VER}
https://github.com/cloud-hypervisor/cloud-hypervisor
Licensed under the Apache License, Version 2.0.
Copyright the cloud-hypervisor authors.
The binary shipped in 狐狸OS is the official static build of this version.
EOF

fi

# ------------------------------------------------------------------ hooks
log "拷入 staging 并运行 hooks"
rm -rf "$CHROOT/usr/src/foxos-os"
cp -a "$STAGING" "$CHROOT/usr/src/foxos-os"
for hook in "$SCRIPT_DIR"/hooks/*.sh; do
  name=$(basename "$hook")
  log "hook $name"
  cp "$hook" "$CHROOT/tmp/$name"
  chmod +x "$CHROOT/tmp/$name"
  chroot_run "/tmp/$name"
  rm -f "$CHROOT/tmp/$name"
done

# ------------------------------------------------------------------ squashfs + ISO 树
unmount_chroot
trap - EXIT

log "收集内核与 squashfs"
KERNEL=$(ls -1 "$CHROOT/boot/vmlinuz-"* | sort | tail -1)
INITRD=$(ls -1 "$CHROOT/boot/initrd.img-"* | sort | tail -1)
[ -f "$KERNEL" ] && [ -f "$INITRD" ] || die "chroot 里没有内核或 initrd"
cp -f "$KERNEL" "$ISO/casper/vmlinuz"
cp -f "$INITRD" "$ISO/casper/initrd"
chmod 644 "$ISO/casper/vmlinuz" "$ISO/casper/initrd"
# 打包前检查 Live initrd（casper BUILD_SYSTEM、overlay、plymouth）
python3 "$SCRIPT_DIR/verify-initrd.sh" "$ISO/casper/initrd"

log "mksquashfs（这一步较久）"
rm -f "$ISO/casper/filesystem.squashfs"
# 保留空的 /run /proc /sys /dev /tmp。casper 在 pivot 前会 chroot 到根文件系统做 adduser，
# 没有 /run 时会报 “could not open lock file /run/adduser”，Live 用户建不出来，
# lightdm 随后 “Can't login unknown user 'foxos'”，进不了桌面。
# 不要用 -e run / -e proc 把目录本身排除掉。
mkdir -p "$CHROOT/run" "$CHROOT/proc" "$CHROOT/sys" "$CHROOT/dev" "$CHROOT/tmp" "$CHROOT/var/tmp"
mksquashfs "$CHROOT" "$ISO/casper/filesystem.squashfs" \
  -comp xz -Xbcj x86 -b 1M -quiet \
  -wildcards -e 'usr/src/foxos-os' -e 'tmp/*' -e 'var/tmp/*' -e 'run/*' -e 'proc/*' -e 'sys/*'

du -sx --block-size=1 "$CHROOT" | cut -f1 > "$ISO/casper/filesystem.size"
# 清单
if [ -x "$CHROOT/usr/bin/dpkg-query" ]; then
  chroot "$CHROOT" dpkg-query -W --showformat='${Package} ${Version}\n' > "$ISO/casper/filesystem.manifest" || true
fi

cp "$SCRIPT_DIR/iso/grub.cfg" "$ISO/boot/grub/grub.cfg"
echo "狐狸OS ${VERSION} amd64" > "$ISO/.disk/info"
echo "full_cd/single" > "$ISO/.disk/cd_type"
echo "$ISO_NAME" > "$ISO/.disk/casper-uuid-helper" 2>/dev/null || true
# README
cat > "$ISO/README.txt" <<EOF
狐狸OS（FoxOS）${VERSION}
https://github.com/gatesenman/foxos
这是一张可试用、可安装的系统光盘。请从 UEFI（或传统 BIOS）引导。
EOF

log "grub-mkrescue 生成混合 ISO（UEFI + BIOS）"
mkdir -p "$OUT"
rm -f "$OUT/$ISO_NAME"
grub-mkrescue -o "$OUT/$ISO_NAME" "$ISO" \
  --compress=xz \
  -volid "$VOLID" \
  -joliet -rational-rock

# 有些 grub-mkrescue 会忽略 -volid 的短横写法，再以 xorriso 确认体积即可
ls -lh "$OUT/$ISO_NAME"
sha256sum "$OUT/$ISO_NAME" | tee "$OUT/SHA256SUMS"
SIZE=$(stat -c%s "$OUT/$ISO_NAME")
if [ "$SIZE" -ge $((2 * 1024 * 1024 * 1024)) ]; then
  die "ISO 达到或超过 2 GB（GitHub Release 单文件上限），需要再减包"
fi

if [ "${FOXOS_OS_KEEP:-0}" != 1 ]; then
  log "清理工作目录（FOXOS_OS_KEEP=1 可保留）"
  # 只删 iso 树与 staging，默认保留 chroot 以便重打包；彻底清理请手动 rm -rf $WORK
  rm -rf "$ISO" "$STAGING"
fi

log "完成：$OUT/$ISO_NAME"
