#!/bin/bash
# 构建狐狸OS 预设 Linux 镜像：桌面（XFCE）、默认中文、Node / Bun / Python、ACP 智能体、foxos 与来宾桥。
# 产物（build/presets/<id>/）：
#   <id>.qcow2               UEFI 可引导磁盘（GPT：ESP + ext4），给狐狸OS 主机（KVM + cloud-hypervisor）
#   <id>.qcow2.partN         按 FOXOS_PRESET_PART_MB（默认 900）切分，GitHub Release 上传用
#   <id>-wsl.tar.gz          同一根文件系统，给 Windows 伴侣程序的 WSL2（wsl --import）
#   <id>.json                目录条目片段（大小、各分卷 sha256、需要的磁盘）
# 用法：sudo scripts/presets/build-preset.sh debian-12|ubuntu-24.04
set -euo pipefail
ID=${1:?预设：debian-12 | ubuntu-24.04}
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../.." && pwd)
WORK=${FOXOS_PRESET_WORK:-/var/tmp/foxos-presets}/$ID
OUT=${FOXOS_PRESET_OUT:-$ROOT/build/presets}/$ID
DISK_GB=${FOXOS_PRESET_DISK_GB:-8}
PART_MB=${FOXOS_PRESET_PART_MB:-900}
NODE_VER=${FOXOS_NODE_VERSION:-v24.22.2}
BUN_VER=${FOXOS_BUN_VERSION:-bun-v1.3.2}
PRESET_VER=${FOXOS_PRESET_VERSION:-2026.11}
case "$ID" in
  debian-12) SUITE=bookworm; MIRROR=${FOXOS_DEBIAN_MIRROR:-http://deb.debian.org/debian}; COMPS=main; KPKG=linux-image-amd64; EXTRA="" ;;
  ubuntu-24.04) SUITE=noble; MIRROR=${FOXOS_UBUNTU_MIRROR:-http://archive.ubuntu.com/ubuntu}; COMPS=main,universe; KPKG=linux-image-virtual; EXTRA="" ;;
  *) echo "未知预设 $ID" >&2; exit 2 ;;
esac
[ "$(id -u)" = 0 ] || exec sudo --preserve-env=FOXOS_PRESET_WORK,FOXOS_PRESET_OUT,FOXOS_PRESET_DISK_GB,FOXOS_PRESET_PART_MB,FOXOS_PRESET_VERSION,http_proxy,https_proxy "$0" "$@"
log() { echo "[preset $ID] $*"; }
trap 'echo "[preset $ID] 失败：第 $LINENO 行：$BASH_COMMAND" >&2' ERR
mkdir -p "$WORK" "$OUT"
IMG="$WORK/disk.raw"; MNT="$WORK/mnt"
cleanup() {
  set +e
  for m in dev/pts dev proc sys run boot/efi; do umount -l "$MNT/$m" 2>/dev/null; done
  umount -l "$MNT" 2>/dev/null
  [ -n "${LOOP:-}" ] && losetup -d "$LOOP" 2>/dev/null
  [ -n "${LOOP1:-}" ] && losetup -d "$LOOP1" 2>/dev/null
}
trap cleanup EXIT

package() {
log "导出 WSL2 根文件系统 tar.gz"
for m in dev/pts dev proc sys run; do umount -l "$MNT/$m" 2>/dev/null || true; done
tar -C "$MNT" --numeric-owner --xattrs --exclude=./boot/efi/* -czf "$OUT/foxos-$ID-wsl.tar.gz" . || [ $? -eq 1 ]
cleanup; trap - EXIT; LOOP=""; LOOP1=""
log "qcow2（压缩）"
qemu-img convert -c -O qcow2 "$IMG" "$OUT/foxos-$ID.qcow2"
rm -f "$OUT/foxos-$ID.qcow2.part"*
split -b "${PART_MB}M" -d -a 1 --numeric-suffixes=1 "$OUT/foxos-$ID.qcow2" "$OUT/foxos-$ID.qcow2.part"
python3 - "$OUT" "$ID" "$DISK_GB" "$PRESET_VER" <<'PY'
import hashlib, json, os, sys
out, pid, disk_gb, ver = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
q = os.path.join(out, f"foxos-{pid}.qcow2")
parts = sorted(n for n in os.listdir(out) if n.startswith(f"foxos-{pid}.qcow2.part"))
w = os.path.join(out, f"foxos-{pid}-wsl.tar.gz")
d = {"id": pid, "version": ver,
     "qcow2": {"name": os.path.basename(q), "size": os.path.getsize(q), "sha256": sha(q),
               "parts": [{"name": n, "size": os.path.getsize(os.path.join(out, n)), "sha256": sha(os.path.join(out, n))} for n in parts]},
     "wsl": {"name": os.path.basename(w), "size": os.path.getsize(w), "sha256": sha(w)},
     "disk_gb": disk_gb}
json.dump(d, open(os.path.join(out, f"foxos-{pid}.json"), "w"), indent=1)
with open(os.path.join(out, "SHA256SUMS"), "w") as f:
    for n in [d["qcow2"]["name"], *[p["name"] for p in d["qcow2"]["parts"]], d["wsl"]["name"]]:
        f.write(f"{sha(os.path.join(out, n))}  {n}\n")
print(json.dumps(d, indent=1))
PY
}

if [ "${FOXOS_PRESET_STAGE:-}" = package ]; then
  # 只重做打包（磁盘已构建好）：重新挂上根分区
  p_off() { sgdisk -i "$1" "$IMG" | awk '/First sector/{print $3*512}'; }
  LOOP=$(losetup --show -f -o "$(p_off 2)" "$IMG"); mount "$LOOP" "$MNT"
  package; rm -f "$IMG"; log "完成：$OUT"; exit 0
fi
log "磁盘 ${DISK_GB}G（GPT：ESP 256M + ext4）"
rm -f "$IMG"; truncate -s "${DISK_GB}G" "$IMG"
sgdisk -Z "$IMG" >/dev/null
sgdisk -n1:1M:+256M -t1:EF00 -c1:EFI -n2:0:0 -t2:8304 -c2:foxos-root "$IMG" >/dev/null
# 容器里常没有 udev 生成 loopNpM 分区节点：按偏移各挂一个 loop 设备
p_off() { sgdisk -i "$1" "$IMG" | awk '/First sector/{print $3*512}'; }
p_len() { sgdisk -i "$1" "$IMG" | awk '/Partition size/{print $3*512}'; }
LOOP1=$(losetup --show -f -o "$(p_off 1)" --sizelimit "$(p_len 1)" "$IMG")
LOOP=$(losetup --show -f -o "$(p_off 2)" --sizelimit "$(p_len 2)" "$IMG")
mkfs.vfat -F32 -n FOXOSEFI "$LOOP1" >/dev/null
mkfs.ext4 -q -L foxos-root "$LOOP"
mkdir -p "$MNT"; mount "$LOOP" "$MNT"; mkdir -p "$MNT/boot/efi"   # ESP 不挂载（构建机内核可能没有 vfat），最后用 mtools 写入

CACHE=${FOXOS_PRESET_WORK:-/var/tmp/foxos-presets}/cache-$SUITE; mkdir -p "$CACHE"
log "debootstrap $SUITE"
debootstrap --arch=amd64 --variant=minbase --components="$COMPS" --cache-dir="$CACHE" \
  --include=ca-certificates,gnupg "$SUITE" "$MNT" "$MIRROR" >"$WORK/debootstrap.log" 2>&1 || { tail -30 "$WORK/debootstrap.log"; exit 1; }
if [ "$ID" = ubuntu-24.04 ]; then
  printf 'deb %s noble main universe\ndeb %s noble-updates main universe\ndeb http://security.ubuntu.com/ubuntu noble-security main universe\n' "$MIRROR" "$MIRROR" > "$MNT/etc/apt/sources.list"
else
  printf 'deb %s bookworm main\ndeb %s bookworm-updates main\ndeb http://deb.debian.org/debian-security bookworm-security main\n' "$MIRROR" "$MIRROR" > "$MNT/etc/apt/sources.list"
fi
for m in dev dev/pts proc sys run; do mount --bind "/$m" "$MNT/$m"; done
cp -L /etc/resolv.conf "$MNT/etc/resolv.conf"
# 干净的环境：不把构建机的 HOME / NPM_CONFIG_PREFIX 之类带进镜像（之前 npm 把 Gemini CLI 装到了 /home/box/.local）
ch() { chroot "$MNT" env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOME=/root DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 "$@"; }

log "软件包：内核、systemd、SSH、XFCE 桌面、中文字体、x11vnc、Python"
ch apt-get update -q
ch apt-get install -y -q --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold \
  $KPKG grub-efi-amd64-bin grub2-common initramfs-tools systemd-sysv systemd-timesyncd udev dbus dbus-x11 dbus-user-session libpam-systemd kmod iproute2 iputils-ping \
  locales tzdata sudo openssh-server curl wget git xz-utils unzip zstd less nano procps psmisc file \
  python3 python3-venv python3-pip python3-openpyxl python3-docx \
  xserver-xorg-core xserver-xorg-input-libinput xinit lightdm lightdm-gtk-greeter \
  xfce4-session xfwm4 xfce4-panel xfdesktop4 xfce4-terminal xfce4-settings thunar mousepad \
  adwaita-icon-theme fonts-noto-cjk x11vnc xdotool wmctrl scrot $EXTRA >"$WORK/apt.log" 2>&1 || { tail -40 "$WORK/apt.log"; exit 1; }

log "中文、时区、用户 foxos（自动登录、sudo 免密，给智能体用的虚拟机）"
sed -i 's/^# *zh_CN.UTF-8/zh_CN.UTF-8/; s/^# *en_US.UTF-8/en_US.UTF-8/' "$MNT/etc/locale.gen"
grep -q '^zh_CN.UTF-8' "$MNT/etc/locale.gen" || echo 'zh_CN.UTF-8 UTF-8' >> "$MNT/etc/locale.gen"
ch locale-gen >/dev/null
echo 'LANG=zh_CN.UTF-8' > "$MNT/etc/default/locale"
ln -sf /usr/share/zoneinfo/Asia/Shanghai "$MNT/etc/localtime"; echo Asia/Shanghai > "$MNT/etc/timezone"
echo "foxos-$ID" > "$MNT/etc/hostname"; printf '127.0.0.1 localhost\n127.0.1.1 foxos-%s\n' "$ID" > "$MNT/etc/hosts"
ch useradd -m -s /bin/bash -G sudo -c "狐狸OS" foxos
ch passwd -l foxos >/dev/null
echo 'foxos ALL=(ALL) NOPASSWD:ALL' > "$MNT/etc/sudoers.d/foxos"; chmod 440 "$MNT/etc/sudoers.d/foxos"
install -d "$MNT/etc/lightdm/lightdm.conf.d"
printf '[Seat:*]\nautologin-user=foxos\nautologin-session=xfce\nuser-session=xfce\n' > "$MNT/etc/lightdm/lightdm.conf.d/50-foxos.conf"
install -d "$MNT/etc/xdg/autostart"; install -m 644 "$HERE/guest/x11vnc.desktop" "$MNT/etc/xdg/autostart/foxos-x11vnc.desktop"
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "$MNT/etc/ssh/sshd_config"
# 网络：systemd-networkd DHCP
install -d "$MNT/etc/systemd/network"
printf '[Match]\nName=en* eth*\n[Network]\nDHCP=yes\n' > "$MNT/etc/systemd/network/20-dhcp.network"
ch systemctl enable systemd-networkd >/dev/null 2>&1 || true
ln -sf /run/systemd/resolve/stub-resolv.conf "$MNT/etc/resolv.conf.target"

log "Node.js $NODE_VER（nodejs.org 官方，MIT）、Bun $BUN_VER（MIT）"
NC="$CACHE/node-$NODE_VER-linux-x64.tar.xz"
[ -f "$NC" ] || wget -q -O "$NC" "https://nodejs.org/dist/$NODE_VER/node-$NODE_VER-linux-x64.tar.xz"
rm -rf "$MNT/opt/node"; mkdir -p "$MNT/opt/node"; tar -C "$MNT/opt/node" --strip-components=1 -xJf "$NC"
for b in node npm npx corepack; do ln -sf "/opt/node/bin/$b" "$MNT/usr/local/bin/$b"; done
# baseline 版：不要求 AVX2，老 CPU 和 QEMU TCG 上也能运行（普通版在那里报 Illegal instruction）
BC="$CACHE/$BUN_VER-linux-x64-baseline.zip"
[ -f "$BC" ] || wget -q -O "$BC" "https://github.com/oven-sh/bun/releases/download/$BUN_VER/bun-linux-x64-baseline.zip"
unzip -q -o -j "$BC" 'bun-linux-x64-baseline/bun' -d "$MNT/usr/local/bin"; chmod 755 "$MNT/usr/local/bin/bun"

log "ACP 智能体：Gemini CLI（Apache-2.0，自带 ACP 模式）预装；其它在首次使用时在线安装"
ch /opt/node/bin/npm install -g --no-fund --no-audit @google/gemini-cli >"$WORK/npm.log" 2>&1 || { tail -20 "$WORK/npm.log"; exit 1; }
ln -sf /opt/node/bin/gemini "$MNT/usr/local/bin/gemini"
[ -x "$MNT/opt/node/bin/gemini" ] || { echo "Gemini CLI 没有装到 /opt/node/bin" >&2; exit 1; }

log "foxos 内核、MCP 用户服务、来宾桥"
install -d "$MNT/usr/lib/foxos/python"
cp -a "$ROOT/packages/core/foxos" "$MNT/usr/lib/foxos/python/foxos"
find "$MNT/usr/lib/foxos/python" -name __pycache__ -prune -exec rm -rf {} +
cat > "$MNT/usr/bin/foxos" <<'U'
#!/bin/sh
export PYTHONPATH="/usr/lib/foxos/python${PYTHONPATH:+:$PYTHONPATH}"
export FOXOS_LANG="${FOXOS_LANG:-zh-CN}"
exec /usr/lib/foxos/venv/bin/python -m foxos "$@"
U
chmod 755 "$MNT/usr/bin/foxos"
# 依赖装进独立 venv（发行版自带的 python3-docx 等版本太旧），失败就让构建失败
ch python3 -m venv /usr/lib/foxos/venv
ch /usr/lib/foxos/venv/bin/pip install --no-cache-dir -q 'openpyxl>=3.1,<4' 'python-docx>=1.1,<2' 'python-pptx>=1.0,<2' 'zstandard>=0.22'
ch /usr/bin/foxos --version
ch /usr/local/bin/bun --version
install -d "$MNT/usr/lib/systemd/user" "$MNT/etc/systemd/user/default.target.wants"
install -m 644 "$ROOT/scripts/os/systemd/foxos-mcp.service" "$MNT/usr/lib/systemd/user/foxos-mcp.service"
ln -sf /usr/lib/systemd/user/foxos-mcp.service "$MNT/etc/systemd/user/default.target.wants/foxos-mcp.service"
# linger：foxos 的用户服务（MCP）开机就启动，不依赖桌面登录；SSH 会话里也有用户总线
install -d "$MNT/var/lib/systemd/linger"; touch "$MNT/var/lib/systemd/linger/foxos"
install -d "$MNT/home/foxos/FoxOS/workspace"; ch chown -R foxos:foxos /home/foxos
install -m 755 "$HERE/guest/foxos-preset-firstboot" "$HERE/guest/foxos-preset-ready" "$MNT/usr/lib/foxos/"
install -m 644 "$HERE/guest/foxos-preset-firstboot.service" "$HERE/guest/foxos-preset-ready.service" "$MNT/etc/systemd/system/"
ch systemctl enable foxos-preset-firstboot.service foxos-preset-ready.service ssh.service >/dev/null 2>&1 || true
# ACP 智能体配置：Gemini CLI 以 ACP 模式启动，并接上本机 foxos MCP
install -d "$MNT/etc/foxos"
cat > "$MNT/etc/foxos/acp-agents.json" <<'J'
{"agents": [
  {"id": "gemini", "name": "Gemini CLI", "command": ["gemini", "--experimental-acp"], "installed": true, "license": "Apache-2.0"},
  {"id": "claude-code", "name": "Claude Code", "install": "npm install -g @zed-industries/claude-code-acp", "installed": false,
   "why_not_preinstalled": "Claude Code 的 SDK 不是开源许可，不能随镜像再分发；首次使用时在线安装"},
  {"id": "codex", "name": "Codex CLI", "install": "npm install -g @zed-industries/codex-acp", "installed": false}
],
 "mcp": {"foxos": {"url": "http://127.0.0.1:8765/mcp"}}}
J
printf 'id=%s\nversion=%s\nbase=%s\n' "foxos-$ID" "$PRESET_VER" "$SUITE" > "$MNT/etc/foxos-preset"

log "引导：GRUB（UEFI，可移动路径），串口控制台"
ROOTUUID=$(blkid -s UUID -o value "$LOOP"); EFIUUID=$(blkid -s UUID -o value "$LOOP1")
printf 'UUID=%s / ext4 defaults,errors=remount-ro 0 1\nUUID=%s /boot/efi vfat umask=0077 0 1\n' "$ROOTUUID" "$EFIUUID" > "$MNT/etc/fstab"
cat > "$MNT/etc/default/grub" <<G
GRUB_DEFAULT=0
GRUB_TIMEOUT=1
GRUB_DISTRIBUTOR="狐狸OS 预设 $ID"
GRUB_CMDLINE_LINUX_DEFAULT=""
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200 net.ifnames=0"
GRUB_TERMINAL="console serial"
GRUB_SERIAL_COMMAND="serial --speed=115200"
GRUB_DISABLE_OS_PROBER=true
G
ch update-initramfs -u -k all >"$WORK/initramfs.log" 2>&1 || ch update-initramfs -c -k all >>"$WORK/initramfs.log" 2>&1
# 容器里 grub-probe / grub-install 认不出 loop 上的分区：自己写 grub.cfg，用 grub-mkstandalone 生成可移动路径的 BOOTX64.EFI
K=/vmlinuz; [ -e "$MNT$K" ] || K=/boot/vmlinuz
I=/initrd.img; [ -e "$MNT$I" ] || I=/boot/initrd.img
install -d "$MNT/boot/grub"
cat > "$MNT/boot/grub/grub.cfg" <<G
set timeout=1
serial --speed=115200 --unit=0
terminal_input console serial
terminal_output console serial
menuentry "狐狸OS 预设 $ID" {
  search --no-floppy --fs-uuid --set=root $ROOTUUID
  linux $K root=UUID=$ROOTUUID ro console=tty0 console=ttyS0,115200 net.ifnames=0
  initrd $I
}
G
cat > "$MNT/tmp/early.cfg" <<G
search --no-floppy --fs-uuid --set=root $ROOTUUID
set prefix=(\$root)/boot/grub
configfile (\$root)/boot/grub/grub.cfg
G
install -d "$MNT/boot/efi/EFI/BOOT"
ch grub-mkstandalone -O x86_64-efi -o /boot/efi/EFI/BOOT/BOOTX64.EFI \
  --modules="part_gpt part_msdos ext2 fat search search_fs_uuid configfile linux normal echo gzio serial terminal efi_gop all_video" \
  "boot/grub/grub.cfg=/tmp/early.cfg" >"$WORK/grub.log" 2>&1 || { cat "$WORK/grub.log"; exit 1; }
# 把 grub-install 生成的 EFI 文件写进 ESP
mmd -i "$LOOP1" ::/EFI ::/EFI/BOOT
mcopy -i "$LOOP1" -o "$MNT/boot/efi/EFI/BOOT/BOOTX64.EFI" ::/EFI/BOOT/BOOTX64.EFI
mdir -i "$LOOP1" ::/EFI/BOOT
rm -rf "$MNT/boot/efi/"*
mv -f "$MNT/etc/resolv.conf.target" "$MNT/etc/resolv.conf" 2>/dev/null || true
ch systemctl enable systemd-resolved >/dev/null 2>&1 || true
ch apt-get clean; rm -rf "$MNT/var/lib/apt/lists/"* "$MNT/tmp/"* "$MNT/root/.npm"
# 许可说明
install -d "$MNT/usr/share/doc/foxos"
cat > "$MNT/usr/share/doc/foxos/PRESET-NOTICE.md" <<N
狐狸OS 预设 $ID（$PRESET_VER）
- 基础系统：$SUITE 官方软件包（各自许可，见 /usr/share/doc/*/copyright）
- Node.js $NODE_VER（MIT，nodejs.org）；Bun $BUN_VER（MIT，github.com/oven-sh/bun）
- Gemini CLI（Apache-2.0，npm @google/gemini-cli）
- 狐狸OS foxos 内核（本仓库）
不含：Google Chrome、Claude Code 等不允许再分发的软件（首次使用时在线安装）。
N

package
rm -f "$IMG"
log "完成：$OUT"
