#!/usr/bin/env bash
# 安装包端到端测试：在一个发行版根文件系统里（chroot，不用容器）真实走一遍
#   install.sh 一行安装（从 file:// “发布目录”下载并校验 SHA256SUMS）→ foxos --version → foxos sheets create
#   → 以普通用户无头启动桌面并截图（xvfb）→ 卸载 → 确认 /usr/bin/foxos 与安装目录已删除
# 用法：sudo e2e-rootfs.sh <根文件系统> <deb|rpm|tar|appimage> <产物目录> <x64|arm64> [截图输出目录]
#   FOXOS_E2E_NO_DESKTOP=1  跳过桌面启动（只用于 qemu-user 跨架构，报告里要标“未验证”）；FOXOS_E2E_TIMEOUT 桌面启动超时秒数
set -euo pipefail
R=${1:?根文件系统}; METHOD=${2:?方式}; ART=$(cd "${3:?产物目录}" && pwd); ARCH=${4:?x64|arm64}; SHOTS=${5:-$ART/smoke}
HERE=$(cd "$(dirname "$0")/../.." && pwd)
V=$(sed -n 's/^  "version": "\(.*\)",/\1/p' "$HERE/apps/desktop/package.json" | head -1)
case $METHOD in deb) F=FoxOS-$V-linux-$ARCH.deb ;; rpm) F=FoxOS-$V-linux-$ARCH.rpm ;; tar) F=FoxOS-$V-linux-$ARCH.tar.gz ;; appimage) F=FoxOS-$V-linux-$ARCH.AppImage ;; esac
NAME=$(. "$R/etc/os-release"; echo "${ID}-${VERSION_ID:-rolling}")
mounted=()
cleanup() { for m in "${mounted[@]}"; do umount -l "$m" 2>/dev/null || true; done; }
trap cleanup EXIT
for m in proc sys dev dev/pts; do mountpoint -q "$R/$m" || { mount --bind "/$m" "$R/$m"; mounted=("$R/$m" "${mounted[@]}"); }; done
rm -f "$R/etc/resolv.conf"; cp /etc/resolv.conf "$R/etc/resolv.conf"
rm -rf "$R/tmp/rel"; mkdir -p "$R/tmp/rel"
cp "$ART/$F" "$R/tmp/rel/"; (cd "$R/tmp/rel" && sha256sum "$F" > SHA256SUMS)
cp "$HERE/scripts/install.sh" "$R/tmp/install.sh"
# 无头启动桌面：自己起 Xvfb（各发行版 xvfb-run 的参数不一样，openSUSE 的不认 -s）
cat > "$R/tmp/e2e-launch.sh" <<'L'
Xvfb :93 -screen 0 1440x900x24 -nolisten tcp >/tmp/e2e-xvfb.log 2>&1 &
X=$!; sleep 3
DISPLAY=:93 timeout "${FOXOS_E2E_TIMEOUT:-150}" "$1" --no-sandbox --user-data-dir="/tmp/e2e-ud-$$" --workspace="/tmp/e2e-dws-$$" --screenshot=/tmp/e2e-shot.png >/tmp/e2e-desk.log 2>&1
kill $X 2>/dev/null; rm -rf "/tmp/e2e-ud-$$" "/tmp/e2e-dws-$$"; true
L
sed -i "s/\${FOXOS_E2E_TIMEOUT:-150}/${FOXOS_E2E_TIMEOUT:-150}/" "$R/tmp/e2e-launch.sh"
cat > "$R/tmp/e2e.sh" <<IN
set -u
export LANG=C.UTF-8 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
step() { printf '[e2e %s %s] %s\n' "$NAME" "$METHOD" "\$*"; }
fail() { step "失败：\$*"; exit 1; }
# 测试用的基础工具（curl 给 install.sh；xvfb 给无头启动）
if command -v apt-get >/dev/null; then export DEBIAN_FRONTEND=noninteractive; apt-get update -qq >/dev/null; apt-get install -y -qq curl ca-certificates xvfb >/dev/null || fail "apt 装测试工具"
elif command -v dnf >/dev/null; then
  # 测试机出口连不上 Cisco 的 openh264 源（与 FoxOS 无关），关掉它
  sed -i 's/^enabled=1/enabled=0/' /etc/yum.repos.d/fedora-cisco-openh264.repo 2>/dev/null || true
  dnf install -y -q --disablerepo='*openh264*' curl xorg-x11-server-Xvfb util-linux shadow-utils >/dev/null || fail "dnf 装测试工具"
elif command -v zypper >/dev/null; then
  # 测试机出口只放行 https，openh264 编解码源连不上（与 FoxOS 无关）
  sed -i 's|baseurl=http://|baseurl=https://|' /etc/zypp/repos.d/*.repo
  for r in repo-openh264 repo-non-oss repo-debug repo-source; do zypper -q modifyrepo -d "\$r" >/dev/null 2>&1 || true; done
  zypper -q --non-interactive install -y curl xorg-x11-server-Xvfb shadow util-linux >/dev/null || fail "zypper 装测试工具"
elif command -v pacman >/dev/null; then pacman -Sy --noconfirm --needed -q curl xorg-server-xvfb gtk3 nss alsa-lib libxss libxtst libnotify libsecret at-spi2-core xdg-utils ttf-liberation >/dev/null || fail "pacman 装测试工具"; fi
id tester >/dev/null 2>&1 || useradd -m tester || fail useradd
# 上一次失败的测试可能留下文件：先清掉，保证从干净状态开始
rm -rf /home/tester/.local/opt/foxos /home/tester/.local/bin/foxos /home/tester/.local/bin/foxos-desktop /home/tester/squashfs-root /home/tester/e2e-ws
step "一行安装（install.sh --method $METHOD，file:// 发布目录，校验 SHA256SUMS）"
if [ "$METHOD" = tar ] || [ "$METHOD" = appimage ]; then
  su tester -c "FOXOS_BASE_URL=file:///tmp/rel FOXOS_VERSION=$V FOXOS_METHOD=$METHOD FOXOS_LANG=en sh /tmp/install.sh" || fail install.sh
  CLI=/home/tester/.local/bin/foxos; DESK=/home/tester/.local/bin/foxos-desktop
else
  FOXOS_BASE_URL=file:///tmp/rel FOXOS_VERSION=$V FOXOS_METHOD=$METHOD FOXOS_LANG=en sh /tmp/install.sh || fail install.sh
  CLI=/usr/bin/foxos; DESK=/opt/FoxOS/foxos-desktop
fi
if [ "$METHOD" != appimage ]; then
  out=\$(su tester -c "\$CLI --version") ; [ "\$out" = "foxos $V" ] || fail "foxos --version → \$out"; step "foxos --version → \$out"
  su tester -c "rm -rf ~/e2e-ws; \$CLI --workspace ~/e2e-ws sheets create e2e.xlsx --json" | grep -q '"ok": true' || fail "sheets create"
  [ -s /home/tester/e2e-ws/e2e.xlsx ] || fail "e2e.xlsx 不存在"; step "foxos sheets create e2e.xlsx → OK"
else
  # AppImage 只含桌面：用 --appimage-extract 后的 resources/bin/foxos 验证随包内核
  su tester -c "cd ~ && rm -rf squashfs-root && ~/.local/opt/foxos/FoxOS.AppImage --appimage-extract >/dev/null" || fail "appimage-extract"
  out=\$(su tester -c "~/squashfs-root/resources/bin/foxos --version"); [ "\$out" = "foxos $V" ] || fail "AppImage foxos --version → \$out"; step "AppImage 内 foxos --version → \$out"
  su tester -c "rm -rf ~/e2e-ws; ~/squashfs-root/resources/bin/foxos --workspace ~/e2e-ws sheets create e2e.xlsx --json" | grep -q '"ok": true' || fail "sheets create"; step "foxos sheets create e2e.xlsx → OK"
  DESK="/home/tester/squashfs-root/AppRun"
fi
if [ "${FOXOS_E2E_NO_DESKTOP:-0}" = 1 ]; then
  step "跳过桌面启动（FOXOS_E2E_NO_DESKTOP=1：qemu-user 下 Chromium 无法运行，要在原生 arm64 机器上验证）——本项未验证"
else
rm -f /tmp/e2e-shot.png
su tester -c "sh /tmp/e2e-launch.sh \$DESK" || true
[ -s /tmp/e2e-shot.png ] || { tail -5 /tmp/e2e-desk.log; fail "桌面没有启动出截图"; }
step "桌面无头启动并截图 → /tmp/e2e-shot.png"
fi
case "$METHOD" in
  deb) apt-get remove -y -qq foxos-desktop >/dev/null || fail "apt remove" ;;
  rpm) if command -v dnf >/dev/null; then dnf remove -y -q foxos-desktop >/dev/null; else zypper -q --non-interactive remove foxos-desktop >/dev/null; fi || fail "rpm 卸载" ;;
  tar|appimage) rm -rf /home/tester/.local/opt/foxos /home/tester/.local/bin/foxos /home/tester/.local/bin/foxos-desktop /home/tester/.local/share/applications/foxos.desktop /home/tester/squashfs-root ;;
esac
for p in /usr/bin/foxos /usr/bin/foxos-desktop /opt/FoxOS /home/tester/.local/opt/foxos /home/tester/.local/bin/foxos /home/tester/.local/bin/foxos-desktop; do [ ! -e "\$p" ] || fail "卸载后还有 \$p"; done
step "卸载干净"
if [ "${FOXOS_E2E_NO_DESKTOP:-0}" = 1 ]; then step "通过（桌面启动未验证）"; else step "通过"; fi
IN
chroot "$R" /usr/bin/env FOXOS_E2E_NO_DESKTOP="${FOXOS_E2E_NO_DESKTOP:-0}" /bin/bash /tmp/e2e.sh
mkdir -p "$SHOTS"; [ "${FOXOS_E2E_NO_DESKTOP:-0}" = 1 ] || cp "$R/tmp/e2e-shot.png" "$SHOTS/e2e-$NAME-$METHOD-$ARCH.png"
