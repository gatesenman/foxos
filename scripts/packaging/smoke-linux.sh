#!/usr/bin/env bash
# Linux 安装包冒烟测试（本机或 CI 都能跑），每一项都真实执行：
#   tar.gz   解压 → resources/bin/foxos --version / help --json → 无头启动桌面并截图（xvfb）
#   AppImage --appimage-extract（不需要 FUSE）→ 同上
#   rpm      读取包信息与安装脚本，确认 /usr/bin/foxos 链接逻辑和 /opt/FoxOS 文件都在包里
#   deb      dpkg-deb 检查；加 --install 时用 apt 真装到本机（CI 的一次性 Ubuntu 机器），再从 /usr/bin/foxos 运行
# 用法：smoke-linux.sh <产物目录> <x64|arm64> [--install]
set -euo pipefail
DIR=$(cd "${1:?产物目录}" && pwd); ARCH=${2:?x64|arm64}; INSTALL=${3:-}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
V=$(node -p "require('$ROOT/apps/desktop/package.json').version" 2>/dev/null || sed -n 's/.*"version": "\(.*\)".*/\1/p' "$ROOT/apps/desktop/package.json" | head -1)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
pass=0; fail=0
ok()  { echo "  通过  $*"; pass=$((pass+1)); }
bad() { echo "  失败  $*" >&2; fail=$((fail+1)); }
check_cli() { # 名称 foxos路径
  local out
  if out=$("$2" --version 2>&1) && [ "$out" = "foxos $V" ]; then ok "$1: foxos --version → $out"; else bad "$1: foxos --version → $out"; fi
  if "$2" help --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["apps"] and d["version"]' 2>/dev/null; then ok "$1: foxos help --json"; else bad "$1: foxos help --json"; fi
  # 随包 Python 带好了内核依赖：在工作空间里建一个 xlsx 并读回
  local ws="$T/ws-$1"; mkdir -p "$ws"
  if "$2" --workspace "$ws" sheets create smoke.xlsx --json >/dev/null 2>&1 && [ -s "$ws/smoke.xlsx" ]; then ok "$1: sheets create（openpyxl 随包）"; else bad "$1: sheets create"; fi
}
check_desktop() { # 名称 可执行文件
  command -v xvfb-run >/dev/null || { echo "  跳过  $1: 没有 xvfb-run"; return 0; }
  local png="$T/$1.png"
  timeout 120 xvfb-run -a -s "-screen 0 1440x900x24" "$2" --no-sandbox --user-data-dir="$T/ud-$1" --workspace="$T/dws-$1" --screenshot="$png" >"$T/$1.log" 2>&1 || true
  if python3 - "$png" <<'PY'
import struct, sys
d = open(sys.argv[1], "rb").read()
assert d[:8] == b"\x89PNG\r\n\x1a\n"
w, h = struct.unpack(">II", d[16:24]); assert w >= 1000 and h >= 600, (w, h)
PY
  then ok "$1: 桌面无头启动并截图（$png）"; mkdir -p "$DIR/smoke"; cp "$png" "$DIR/smoke/$1-linux-$ARCH.png"
  else bad "$1: 桌面没有出截图"; tail -20 "$T/$1.log" >&2; fi
}

echo "== tar.gz"
TGZ="$DIR/FoxOS-$V-linux-$ARCH.tar.gz"
if [ -f "$TGZ" ]; then
  mkdir -p "$T/tgz"; tar -xzf "$TGZ" -C "$T/tgz" --strip-components=1
  check_cli tar "$T/tgz/resources/bin/foxos"
  check_desktop tar "$T/tgz/foxos-desktop"
else bad "缺少 $TGZ"; fi

echo "== AppImage"
AI="$DIR/FoxOS-$V-linux-$ARCH.AppImage"
if [ -f "$AI" ]; then
  (cd "$T" && "$AI" --appimage-extract >/dev/null 2>&1) || bad "AppImage 解包失败"
  [ -x "$T/squashfs-root/resources/bin/foxos" ] && check_cli appimage "$T/squashfs-root/resources/bin/foxos"
  [ -x "$T/squashfs-root/AppRun" ] && check_desktop appimage "$T/squashfs-root/AppRun"
else bad "缺少 $AI"; fi

echo "== rpm"
RPM="$DIR/FoxOS-$V-linux-$ARCH.rpm"
if [ -f "$RPM" ] && command -v rpm >/dev/null; then
  want=$([ "$ARCH" = x64 ] && echo x86_64 || echo aarch64)
  [ "$(rpm -qp --qf '%{ARCH}' "$RPM" 2>/dev/null)" = "$want" ] && ok "rpm: 架构 $want" || bad "rpm: 架构不是 $want"
  scripts=$(rpm -qp --scripts "$RPM" 2>/dev/null); files=$(rpm -qlp "$RPM" 2>/dev/null)
  grep -q "/usr/bin/foxos" <<<"$scripts" && ok "rpm: 安装脚本会建 /usr/bin/foxos" || bad "rpm: 安装脚本里没有 /usr/bin/foxos"
  grep -q '^/opt/FoxOS/resources/python/bin/python3$' <<<"$files" && ok "rpm: 随包 Python 在 /opt/FoxOS/resources/python" || bad "rpm: 没有随包 Python"
elif [ -f "$RPM" ]; then echo "  跳过  rpm: 本机没有 rpm 命令"; else bad "缺少 $RPM"; fi

echo "== deb"
DEB="$DIR/FoxOS-$V-linux-$ARCH.deb"
if [ -f "$DEB" ]; then
  want=$([ "$ARCH" = x64 ] && echo amd64 || echo arm64)
  [ "$(dpkg-deb -f "$DEB" Architecture)" = "$want" ] && ok "deb: 架构 $want" || bad "deb: 架构不是 $want"
  grep -q "/usr/bin/foxos" <<<"$(dpkg-deb -I "$DEB" postinst)" && ok "deb: postinst 会建 /usr/bin/foxos" || bad "deb: postinst 里没有 /usr/bin/foxos"
  if [ "$INSTALL" = --install ]; then
    cp "$DEB" "$T/foxos.deb"; chmod 755 "$T"; chmod 644 "$T/foxos.deb"
    sudo apt-get install -y -q "$T/foxos.deb" >"$T/apt.log" 2>&1 && ok "deb: apt 安装" || { bad "deb: apt 安装"; tail -20 "$T/apt.log" >&2; }
    [ -x /usr/bin/foxos ] && check_cli deb /usr/bin/foxos || bad "deb: 没有 /usr/bin/foxos"
    [ -x /usr/bin/foxos-desktop ] && check_desktop deb /usr/bin/foxos-desktop || bad "deb: 没有 /usr/bin/foxos-desktop"
    sudo apt-get remove -y -q foxos-desktop >/dev/null 2>&1 && [ ! -e /usr/bin/foxos ] && ok "deb: 卸载后 /usr/bin/foxos 已移除" || bad "deb: 卸载"
  fi
else bad "缺少 $DEB"; fi

echo "Linux $ARCH 冒烟：通过 $pass，失败 $fail"
[ "$fail" -eq 0 ]
