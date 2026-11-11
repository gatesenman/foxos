#!/bin/bash
# 用 QEMU/KVM 测试引导 ISO。QEMU 只用于测试，不是产品依赖，也不打进 ISO。
# 用法：scripts/os/qemu-boot.sh [ISO 路径] [--disk] [--vnc :1] [--install-disk /path/to.img]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ISO=${1:-"$ROOT/build/os/FoxOS-0.3.0-amd64.iso"}
shift || true
MEM=${FOXOS_QEMU_MEM:-4096}
SMP=${FOXOS_QEMU_SMP:-4}
OVMF_CODE=${OVMF_CODE:-/usr/share/OVMF/OVMF_CODE_4M.fd}
OVMF_VARS_TPL=${OVMF_VARS:-/usr/share/OVMF/OVMF_VARS_4M.fd}
WORK=${FOXOS_OS_WORK:-/var/tmp/foxos-os}
mkdir -p "$WORK/qemu"
VARS="$WORK/qemu/OVMF_VARS.fd"
[ -f "$VARS" ] || cp "$OVMF_VARS_TPL" "$VARS"
[ -f "$ISO" ] || { echo "找不到 ISO：$ISO" >&2; exit 1; }
[ -e /dev/kvm ] || echo "警告：没有 /dev/kvm，会非常慢（仍可测固件，但不代表真实性能）" >&2

EXTRA=()
DISPLAY_ARGS=(-display vnc=127.0.0.1:0 -vga virtio)
DISK_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --vnc) DISPLAY_ARGS=(-display "vnc=127.0.0.1${2:-:0}" -vga virtio); shift 2 || shift ;;
    --gtk) DISPLAY_ARGS=(-display gtk -vga virtio); shift ;;
    --nographic) DISPLAY_ARGS=(-nographic); shift ;;
    --install-disk)
      img=${2:?}
      [ -f "$img" ] || qemu-img create -f qcow2 "$img" 32G
      DISK_ARGS=(-drive "file=$img,if=virtio,format=qcow2")
      shift 2
      ;;
    *) echo "未知参数 $1" >&2; exit 2 ;;
  esac
done

KVM=()
[ -e /dev/kvm ] && KVM=(-enable-kvm -cpu host)

echo "ISO=$ISO  VNC=127.0.0.1:5900（若未改 --vnc）"
exec qemu-system-x86_64 \
  "${KVM[@]}" \
  -m "$MEM" -smp "$SMP" \
  -machine q35,smm=on \
  -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
  -drive if=pflash,format=raw,file="$VARS" \
  -cdrom "$ISO" \
  -boot d \
  -device virtio-net-pci,netdev=n0 -netdev user,id=n0 \
  -device qemu-xhci -device usb-tablet \
  -serial mon:stdio \
  "${DISK_ARGS[@]}" \
  "${DISPLAY_ARGS[@]}"
