#!/bin/sh
set -eu
# 保证 Live / Hyper-V / virtio / NVMe / USB 都能找到启动盘上的 squashfs
cat >> /etc/initramfs-tools/modules <<'U'
squashfs
overlay
isofs
uas
usb-storage
nvme
ahci
sd_mod
sr_mod
virtio_pci
virtio_blk
virtio_scsi
virtio_net
virtio_console
hv_vmbus
hv_storvsc
hv_netvsc
hv_utils
hid_hyperv
U
update-initramfs -u -k all
