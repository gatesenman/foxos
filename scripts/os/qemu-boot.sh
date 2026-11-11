#!/bin/bash
# 用 QEMU 测试引导 ISO。QEMU 只用于测试，不是产品依赖，也不打进 ISO。
# 用法：scripts/os/qemu-boot.sh [ISO 路径] [--tcg] [--gtk|--vnc :N|--nographic]
#                                [--install-disk /path/to.img] [--serial-log PATH]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ISO=${1:-"$ROOT/build/os/FoxOS-0.3.0-amd64.iso"}
if [ "${1:-}" != "" ] && [ "${1:0:2}" != "--" ]; then
  shift || true
fi
MEM=${FOXOS_QEMU_MEM:-4096}
SMP=${FOXOS_QEMU_SMP:-4}
OVMF_CODE=${OVMF_CODE:-/usr/share/OVMF/OVMF_CODE_4M.fd}
OVMF_VARS_TPL=${OVMF_VARS:-/usr/share/OVMF/OVMF_VARS_4M.fd}
WORK=${FOXOS_OS_WORK:-/var/tmp/foxos-os}
mkdir -p "$WORK/qemu"
VARS="$WORK/qemu/OVMF_VARS.fd"
[ -f "$VARS" ] || cp "$OVMF_VARS_TPL" "$VARS"
[ -f "$ISO" ] || { echo "找不到 ISO：$ISO" >&2; exit 1; }

# 显示：Debian 的 qemu 10 可能没有 ui-vnc.so，这时改用 gtk
has_vnc=0
if qemu-system-x86_64 -display help 2>/dev/null | grep -qi '^ *vnc'; then
  has_vnc=1
fi
if [ "$has_vnc" -eq 1 ]; then
  DISPLAY_ARGS=(-display vnc=127.0.0.1:0 -vga virtio)
  DISPLAY_NOTE="VNC=127.0.0.1:5900"
else
  DISPLAY_ARGS=(-display gtk -vga virtio)
  DISPLAY_NOTE="显示=gtk（此宿主的 QEMU 没有 VNC 模块）"
fi

DISK_ARGS=()
SERIAL_LOG=${FOXOS_QEMU_SERIAL:-"$WORK/qemu/serial.log"}
ACCEL=${FOXOS_QEMU_ACCEL:-auto}

while [ $# -gt 0 ]; do
  case "$1" in
    --vnc)
      DISPLAY_ARGS=(-display "vnc=127.0.0.1${2:-:0}" -vga virtio)
      DISPLAY_NOTE="VNC=127.0.0.1${2:-:0}"
      shift 2 || shift
      ;;
    --gtk) DISPLAY_ARGS=(-display gtk -vga virtio); DISPLAY_NOTE="显示=gtk"; shift ;;
    --nographic) DISPLAY_ARGS=(-nographic); DISPLAY_NOTE="无图形（串口控制台）"; shift ;;
    --tcg) ACCEL=tcg; shift ;;
    --serial-log) SERIAL_LOG=$2; shift 2 ;;
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
if [ "$ACCEL" = tcg ]; then
  echo "使用 TCG（软件模拟）。在本机 KVM 不可用时仍可测引导，但不代表真实性能。"
elif [ -e /dev/kvm ]; then
  if dmesg 2>/dev/null | grep -q 'kvm_arch_vcpu_create'; then
    echo "警告：此宿主的 KVM 曾触发内核 BUG（kvm_arch_vcpu_create），改用 TCG。" >&2
  elif [ ! -r /dev/kvm ] || [ ! -w /dev/kvm ]; then
    echo "警告：/dev/kvm 存在但当前用户不可读写，改用 TCG。也可用 sudo 或加入 kvm 组。" >&2
  else
    KVM=(-enable-kvm -cpu host)
  fi
else
  echo "警告：没有 /dev/kvm，改用 TCG（会很慢）。" >&2
fi

: > "$SERIAL_LOG"
echo "ISO=$ISO  $DISPLAY_NOTE  串口日志=$SERIAL_LOG"
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
  -serial file:"$SERIAL_LOG" \
  "${DISK_ARGS[@]}" \
  "${DISPLAY_ARGS[@]}"
