#!/bin/sh
# 狐狸OS（FoxOS）一键安装：Linux（x64 / arm64）与 macOS（Apple 芯片 / Intel）
#
#   curl -fsSL https://github.com/gatesenman/foxos/releases/download/v0.3.2-os-preview/install.sh | sh
#   curl -fsSL .../install.sh | sh -s -- --method tar      # 只装到当前用户，不用 sudo
#
# 做的事：识别系统和 CPU → 从 GitHub Release 下载对应安装包 → 用同一发布里的 SHA256SUMS 校验 →
# 安装 → 运行 `foxos --version` 确认。校验不通过就停止，什么都不装。
#
# 选项（也可以用环境变量）：
#   --tag <标签>          FOXOS_TAG       发布标签，默认 v0.3.2-os-preview
#   --method <方式>       FOXOS_METHOD    auto（默认）| deb | rpm | appimage | tar；macOS 固定为 app
#   --prefix <目录>       FOXOS_PREFIX    tar / appimage 的安装目录，默认 ~/.local/share/foxos
#   --download-only       FOXOS_DOWNLOAD_ONLY=1   只下载并校验，文件留在当前目录
#   --lang <zh|en>        FOXOS_LANG      提示语言，默认中文
#   FOXOS_BASE_URL        下载地址前缀（镜像或测试用），默认 https://github.com/<仓库>/releases/download/<标签>
#   FOXOS_REPO            仓库，默认 gatesenman/foxos
set -eu

TAG=${FOXOS_TAG:-v0.3.2-os-preview}
METHOD=${FOXOS_METHOD:-auto}
PREFIX=${FOXOS_PREFIX:-}
DOWNLOAD_ONLY=${FOXOS_DOWNLOAD_ONLY:-0}
LANG_SEL=${FOXOS_LANG:-zh}
REPO=${FOXOS_REPO:-gatesenman/foxos}
VERSION=${FOXOS_VERSION:-}

while [ $# -gt 0 ]; do
  case $1 in
    --tag) TAG=$2; shift 2 ;;
    --method) METHOD=$2; shift 2 ;;
    --prefix) PREFIX=$2; shift 2 ;;
    --version) VERSION=$2; shift 2 ;;
    --download-only) DOWNLOAD_ONLY=1; shift ;;
    --lang) LANG_SEL=$2; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0" 2>/dev/null || true; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
BASE_URL=${FOXOS_BASE_URL:-https://github.com/$REPO/releases/download/$TAG}
# 版本号从标签推出：v0.3.2-os-preview → 0.3.2
[ -n "$VERSION" ] || VERSION=$(printf '%s' "$TAG" | sed -E 's/^v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

say() { # 中文 英文
  if [ "${LANG_SEL#en}" != "$LANG_SEL" ]; then printf '%s\n' "$2"; else printf '%s\n' "$1"; fi
}
die() { say "错误：$1" "Error: $2" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1; }
need curl || need wget || die "需要 curl 或 wget" "curl or wget is required"
fetch() { # url dest
  if need curl; then curl -fL --retry 3 --progress-bar -o "$2" "$1"; else wget -q --show-progress -O "$2" "$1"; fi
}
sha256() {
  if need sha256sum; then sha256sum "$1" | cut -d' ' -f1
  elif need shasum; then shasum -a 256 "$1" | cut -d' ' -f1
  else die "需要 sha256sum 或 shasum" "sha256sum or shasum is required"; fi
}

# 以 root 运行时不用 sudo；否则有 sudo 才走系统包，没有就退回到用户目录安装
SUDO=
if [ "$(id -u)" -ne 0 ]; then
  if need sudo; then SUDO=sudo; else SUDO=none; fi
fi

OS=$(uname -s)
case $(uname -m) in
  x86_64|amd64) ARCH=x64 ;;
  aarch64|arm64) ARCH=arm64 ;;
  *) die "不支持的 CPU：$(uname -m)（支持 x86_64 和 arm64）" "unsupported CPU: $(uname -m) (x86_64 and arm64 are supported)" ;;
esac

case $OS in
  Linux)
    if [ "$METHOD" = auto ]; then
      if [ "$SUDO" = none ]; then METHOD=tar
      elif need apt-get && need dpkg; then METHOD=deb
      elif need dnf || need zypper || need yum; then METHOD=rpm
      else METHOD=tar; fi
    fi
    case $METHOD in
      deb) FILE=FoxOS-$VERSION-linux-$ARCH.deb ;;
      rpm) FILE=FoxOS-$VERSION-linux-$ARCH.rpm ;;
      appimage) FILE=FoxOS-$VERSION-linux-$ARCH.AppImage ;;
      tar) FILE=FoxOS-$VERSION-linux-$ARCH.tar.gz ;;
      *) die "未知安装方式：$METHOD" "unknown method: $METHOD" ;;
    esac ;;
  Darwin)
    METHOD=app; FILE=FoxOS-$VERSION-mac-$ARCH.zip ;;
  *) die "这个脚本只支持 Linux 和 macOS；Windows 请用 install.ps1" "this script supports Linux and macOS only; on Windows use install.ps1" ;;
esac

TMP=$(mktemp -d 2>/dev/null || mktemp -d -t foxos)
trap 'rm -rf "$TMP"' EXIT INT TERM
say "狐狸OS $VERSION · $OS $ARCH · 方式 $METHOD · $FILE" "FoxOS $VERSION · $OS $ARCH · method $METHOD · $FILE"
fetch "$BASE_URL/SHA256SUMS" "$TMP/SHA256SUMS" || die "下载 SHA256SUMS 失败（$BASE_URL）" "failed to download SHA256SUMS ($BASE_URL)"
WANT=$(awk -v f="$FILE" '{n=$2; sub(/^\*/,"",n)} n==f {print $1; exit}' "$TMP/SHA256SUMS")
[ -n "$WANT" ] || die "SHA256SUMS 里没有 $FILE" "SHA256SUMS has no entry for $FILE"
fetch "$BASE_URL/$FILE" "$TMP/$FILE" || die "下载失败：$FILE" "download failed: $FILE"
GOT=$(sha256 "$TMP/$FILE")
[ "$GOT" = "$WANT" ] || die "SHA-256 不一致：应为 $WANT，实际 $GOT（下载损坏或被篡改），已停止" "SHA-256 mismatch: expected $WANT, got $GOT (corrupted or tampered download); aborting"
say "SHA-256 校验通过：$GOT" "SHA-256 OK: $GOT"

if [ "$DOWNLOAD_ONLY" = 1 ]; then
  cp "$TMP/$FILE" "./$FILE"; say "已保存：./$FILE" "Saved: ./$FILE"; exit 0
fi

BIN_DIR=$HOME/.local/bin
link_cli() { # 目标
  if [ -w /usr/local/bin ] 2>/dev/null; then BIN_DIR=/usr/local/bin; fi
  mkdir -p "$BIN_DIR"; ln -sf "$1" "$BIN_DIR/foxos"
  case ":$PATH:" in *":$BIN_DIR:"*) ;; *) say "提示：把 $BIN_DIR 加到 PATH 后就能直接用 foxos" "Note: add $BIN_DIR to PATH to run foxos directly" ;; esac
}
root() { if [ -z "$SUDO" ]; then "$@"; else $SUDO "$@"; fi; }

case $METHOD in
  deb)
    cp "$TMP/$FILE" "$TMP/foxos.deb"; chmod 644 "$TMP/foxos.deb"; chmod 755 "$TMP"
    root apt-get install -y "$TMP/foxos.deb"
    CLI=/usr/bin/foxos ;;
  rpm)
    if need dnf; then root dnf install -y "$TMP/$FILE"
    elif need zypper; then root zypper --non-interactive install --allow-unsigned-rpm "$TMP/$FILE"
    else root yum install -y "$TMP/$FILE"; fi
    CLI=/usr/bin/foxos ;;
  tar)
    PREFIX=${PREFIX:-$HOME/.local/share/foxos}
    rm -rf "$PREFIX.new"; mkdir -p "$PREFIX.new"
    tar -xzf "$TMP/$FILE" -C "$PREFIX.new" --strip-components=1
    rm -rf "$PREFIX"; mv "$PREFIX.new" "$PREFIX"
    link_cli "$PREFIX/resources/bin/foxos"
    ln -sf "$PREFIX/foxos-desktop" "$BIN_DIR/foxos-desktop"
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/foxos.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=FoxOS
Name[zh_CN]=狐狸OS
Exec=$PREFIX/foxos-desktop %U
Icon=$PREFIX/resources/icon.png
Categories=Office;
DESK
    CLI=$PREFIX/resources/bin/foxos ;;
  appimage)
    PREFIX=${PREFIX:-$HOME/.local/share/foxos}
    mkdir -p "$PREFIX"; cp "$TMP/$FILE" "$PREFIX/FoxOS.AppImage"; chmod +x "$PREFIX/FoxOS.AppImage"
    mkdir -p "$BIN_DIR"; ln -sf "$PREFIX/FoxOS.AppImage" "$BIN_DIR/foxos-desktop"
    say "AppImage 需要 FUSE 2（Ubuntu 24.04：sudo apt install libfuse2t64）。命令行 foxos 请用 deb / rpm / tar 方式安装。" \
        "AppImage needs FUSE 2 (Ubuntu 24.04: sudo apt install libfuse2t64). For the foxos CLI use the deb / rpm / tar method."
    say "完成：$PREFIX/FoxOS.AppImage" "Done: $PREFIX/FoxOS.AppImage"; exit 0 ;;
  app)
    DEST=/Applications
    [ -w "$DEST" ] || DEST=$HOME/Applications
    mkdir -p "$DEST"
    ditto -x -k "$TMP/$FILE" "$TMP/app"
    rm -rf "$DEST/FoxOS.app"; mv "$TMP/app/FoxOS.app" "$DEST/FoxOS.app"
    # curl 下载的文件本来就不带隔离标记；保险起见清掉，避免「无法验证开发者」（安装包未经 Apple 公证）
    xattr -dr com.apple.quarantine "$DEST/FoxOS.app" 2>/dev/null || true
    link_cli "$DEST/FoxOS.app/Contents/Resources/bin/foxos"
    CLI=$DEST/FoxOS.app/Contents/Resources/bin/foxos ;;
esac

"$CLI" --version
say "完成。桌面程序在应用菜单里叫「狐狸OS」；命令行：foxos --help" "Done. Open FoxOS from your app menu; CLI: foxos --help"
