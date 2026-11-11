#!/bin/sh
set -eu
SRC=/usr/src/foxos-os
# 安装狐狸OS 命令内核（从本仓库拷入的 Python 包）
install -d /usr/lib/foxos/python
if [ -d "$SRC/foxos-pkg/foxos" ]; then
  rm -rf /usr/lib/foxos/python/foxos
  cp -a "$SRC/foxos-pkg/foxos" /usr/lib/foxos/python/foxos
fi
# 补充发行版里可能没有的 Python 依赖
export PIP_DISABLE_PIP_VERSION_CHECK=1
python3 -m pip install --break-system-packages --no-cache-dir 'python-pptx>=1.0,<2' 'zstandard>=0.22' ||   python3 -m pip install --no-cache-dir 'python-pptx>=1.0,<2' 'zstandard>=0.22' || true
cat > /usr/bin/foxos <<'U'
#!/bin/sh
export PYTHONPATH="/usr/lib/foxos/python${PYTHONPATH:+:$PYTHONPATH}"
export FOXOS_LANG="${FOXOS_LANG:-zh-CN}"
exec /usr/bin/python3 -m foxos "$@"
U
chmod 755 /usr/bin/foxos
# systemd 用户服务：MCP
install -d /usr/lib/systemd/user
install -m 644 "$SRC/systemd/foxos-mcp.service" /usr/lib/systemd/user/foxos-mcp.service
# 默认工作空间骨架
install -d /etc/skel/FoxOS/workspace
# VMM（cloud-hypervisor，完整虚拟机用）
if [ -d "$SRC/vmm" ]; then
  install -d /usr/lib/foxos/vmm /usr/share/doc/foxos
  cp -a "$SRC/vmm/." /usr/lib/foxos/vmm/
  if [ -f /usr/lib/foxos/vmm/NOTICE ]; then
    cp /usr/lib/foxos/vmm/NOTICE /usr/share/doc/foxos/NOTICE.vmm
  fi
  if [ -x /usr/lib/foxos/vmm/cloud-hypervisor ]; then
    ln -sf /usr/lib/foxos/vmm/cloud-hypervisor /usr/bin/cloud-hypervisor
  fi
fi
# Google Chrome：不预装（Google 条款不允许再分发），只装首次使用时从 Google 官方源安装的入口。
# 见 docs/os.md「浏览器：为什么 Chrome 不在 ISO 里」。
if [ -d "$SRC/chrome" ]; then
  command -v zenity >/dev/null 2>&1 || DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends zenity || true
  command -v xorriso >/dev/null 2>&1 || { apt-get update -q >/dev/null 2>&1; DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends xorriso; } || true   # 预设系统的种子光盘
  install -m 755 "$SRC/chrome/foxos-chrome-setup" /usr/lib/foxos/foxos-chrome-setup
  ln -sf /usr/lib/foxos/foxos-chrome-setup /usr/bin/foxos-chrome-setup
  install -m 755 "$SRC/chrome/foxos-chrome" /usr/bin/foxos-chrome
  install -m 644 "$SRC/chrome/foxos-chrome.desktop" /usr/share/applications/foxos-chrome.desktop
  install -d /etc/xdg/autostart
  install -m 644 "$SRC/chrome/foxos-chrome-firstrun.desktop" /etc/xdg/autostart/foxos-chrome-firstrun.desktop
  # 默认浏览器：入口是 foxos-chrome（装好后就是 Chrome；没装时先询问，拒绝则用 Firefox）
  cat > /etc/xdg/mimeapps.list <<'M'
[Default Applications]
text/html=foxos-chrome.desktop
application/xhtml+xml=foxos-chrome.desktop
x-scheme-handler/http=foxos-chrome.desktop
x-scheme-handler/https=foxos-chrome.desktop
M
  install -d /etc/xdg/xfce4
  sed -i '/^WebBrowser=/d' /etc/xdg/xfce4/helpers.rc 2>/dev/null || true
  echo 'WebBrowser=foxos-chrome' >> /etc/xdg/xfce4/helpers.rc
  install -d /usr/share/xfce4/helpers
  cat > /usr/share/xfce4/helpers/foxos-chrome.desktop <<'H'
[Desktop Entry]
NoDisplay=true
Version=1.0
Encoding=UTF-8
Type=X-XFCE-Helper
X-XFCE-Category=WebBrowser
X-XFCE-CommandsWithParameter=/usr/bin/foxos-chrome "%s"
Icon=google-chrome
Name=Google Chrome
X-XFCE-Commands=/usr/bin/foxos-chrome
H
  update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/bin/foxos-chrome 220 || true
fi
