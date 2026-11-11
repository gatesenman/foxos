#!/bin/sh
set -eu
# Live / Hyper-V / virtio / NVMe / USB 能找到启动盘上的 squashfs。
# linux-image-generic 6.8 把 squashfs、loop、virtio_blk、virtio_pci、sr_mod 编进了内核；
# overlay 是模块，必须打进 initramfs（casper 自带 hook 也会加）。
# 下面的列表幂等写入 /etc/initramfs-tools/modules（内置模块写进去也无害）。
# hv_* / hid_hyperv 不要写进 modules 强制加载：在非 Hyper-V 机器上 udev 会空等 vmbus 约 90 秒。
# MODULES=most 仍会把这些模块打进 initramfs，宿主是 Hyper-V 时会按 alias 自动加载。
for m in squashfs overlay isofs loop uas usb-storage nvme ahci sd_mod sr_mod \
         virtio_pci virtio_blk virtio_scsi virtio_net virtio_console virtio_gpu
do
  grep -qxF "$m" /etc/initramfs-tools/modules 2>/dev/null || echo "$m" >> /etc/initramfs-tools/modules
done

# plymouth 软件包会把 init-premount 脚本打进 initramfs，但没有主题时
# plymouth hook 会提前退出，不复制 plymouthd，启动时刷 “plymouthd: not found”。
# 第一张 ISO 不用闪屏（grub 也不传 splash），从 initramfs 去掉这些不完整的脚本。
install -d /etc/initramfs-tools/hooks
cat > /etc/initramfs-tools/hooks/zz-foxos-drop-plymouth <<'HOOK'
#!/bin/sh
PREREQ=""
prereqs() { echo "$PREREQ"; }
case $1 in
  prereqs) prereqs; exit 0 ;;
esac
. /usr/share/initramfs-tools/hook-functions
if [ ! -x "${DESTDIR}/usr/sbin/plymouthd" ] && [ ! -x "${DESTDIR}/sbin/plymouthd" ]; then
  rm -f "${DESTDIR}/scripts/init-premount/plymouth" \
        "${DESTDIR}/scripts/init-bottom/plymouth" \
        "${DESTDIR}/scripts/init-top/plymouth" \
        "${DESTDIR}/scripts/panic/plymouth" 2>/dev/null || true
fi
HOOK
chmod +x /etc/initramfs-tools/hooks/zz-foxos-drop-plymouth

update-initramfs -u -k all
