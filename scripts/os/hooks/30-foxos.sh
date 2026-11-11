#!/bin/sh
set -eu
SRC=/usr/src/foxos-os
# 安装狐狸OS 命令内核（从本仓库拷入的 Python 包）
install -d /usr/lib/foxos/python
if [ -d "$SRC/foxos-pkg/foxos" ]; then
  rm -rf /usr/lib/foxos/python/foxos
  cp -a "$SRC/foxos-pkg/foxos" /usr/lib/foxos/python/foxos
fi
# Python 依赖装进狐狸OS 自己的虚拟环境（PEP 668：不往系统 Python 里 pip install，也不用 --break-system-packages）。
# --system-site-packages 让 apt 装的 python3-gi、openpyxl、python-docx 照常可用。
export PIP_DISABLE_PIP_VERSION_CHECK=1
VENV=/usr/lib/foxos/venv
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv --system-site-packages "$VENV"
fi
"$VENV/bin/python" -m pip install --no-cache-dir --ignore-installed 'python-pptx>=1.0,<2' 'zstandard>=0.22'
"$VENV/bin/python" -c 'import pptx, zstandard, openpyxl, docx'
cat > /usr/bin/foxos <<'U'
#!/bin/sh
export PYTHONPATH="/usr/lib/foxos/python${PYTHONPATH:+:$PYTHONPATH}"
export FOXOS_LANG="${FOXOS_LANG:-zh-CN}"
exec /usr/lib/foxos/venv/bin/python -m foxos "$@"
U
chmod 755 /usr/bin/foxos
# systemd 用户服务：MCP
install -d /usr/lib/systemd/user
for u in foxos-mcp.service foxos-bots.service foxos-bots-routines.service foxos-bots-routines.timer foxos-machine.service; do
  install -m 644 "$SRC/systemd/$u" "/usr/lib/systemd/user/$u"
done
# 例程定时器默认启用（到期的例程才会运行）；聊天服务按需由 foxos-bots 启动；被控端服务默认不启用（需要用户主动开）
install -d /etc/systemd/user/timers.target.wants
ln -sf /usr/lib/systemd/user/foxos-bots-routines.timer /etc/systemd/user/timers.target.wants/foxos-bots-routines.timer
# 默认工作空间骨架
install -d /etc/skel/FoxOS/workspace
# VMM（cloud-hypervisor，完整虚拟机用）
if [ -d "$SRC/vmm" ]; then
  install -d /usr/lib/foxos/vmm /usr/share/doc/foxos
  cp -a --remove-destination "$SRC/vmm/." /usr/lib/foxos/vmm/   # 正在运行的旧二进制不挡路
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

# SSH 远程访问（docs/ssh.md）：默认开启，只允许密钥登录，禁止 root 登录，ufw 放行 22。
# Live 会话另外生成一次性随机密码并显示在控制台与桌面（foxos-live-ssh）。
if [ -d "$SRC/ssh" ]; then
  command -v sshd >/dev/null 2>&1 || [ -x /usr/sbin/sshd ] || { apt-get update -q >/dev/null 2>&1; DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends openssh-server ufw; } || true
  command -v ufw >/dev/null 2>&1 || DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ufw || true
  for f in foxos-ssh-admin foxos-live-ssh foxos-live-ssh-notify foxos-ssh-setup foxos-ssh-install-target; do
    install -m 755 "$SRC/ssh/$f" /usr/lib/foxos/$f
  done
  install -m 440 "$SRC/ssh/foxos-ssh-sudoers" /etc/sudoers.d/foxos-ssh
  install -m 644 "$SRC/ssh/foxos-ssh-hostkeys.service" "$SRC/ssh/foxos-live-ssh.service" /etc/systemd/system/
  install -m 644 "$SRC/ssh/foxos-live-ssh-notify.desktop" /etc/xdg/autostart/foxos-live-ssh-notify.desktop
  install -m 644 "$SRC/ssh/foxos-ssh-firstrun.desktop" /etc/xdg/autostart/foxos-ssh-firstrun.desktop
  /usr/lib/foxos/foxos-ssh-admin password-off >/dev/null 2>&1 || true   # 写 10-foxos.conf（PasswordAuthentication no，PermitRootLogin no）
  # Ubuntu 24.04 默认用 ssh.socket 按需启动；狐狸OS 用常驻的 ssh.service，状态更直观
  systemctl disable ssh.socket >/dev/null 2>&1 || true
  systemctl enable ssh.service foxos-ssh-hostkeys.service foxos-live-ssh.service >/dev/null 2>&1 || true
  # 防火墙：开启 ufw，默认拒绝入站，放行 22/tcp（chroot 里不能调 iptables，直接写规则文件）
  if [ -f /etc/ufw/ufw.conf ]; then
    sed -i 's/^ENABLED=.*/ENABLED=yes/' /etc/ufw/ufw.conf
    grep -q 'dport 22 -j ACCEPT' /etc/ufw/user.rules 2>/dev/null || \
      sed -i 's|^### RULES ###|### RULES ###\n\n### tuple ### allow tcp 22 0.0.0.0/0 any 0.0.0.0/0 in\n-A ufw-user-input -p tcp --dport 22 -j ACCEPT|' /etc/ufw/user.rules
    grep -q 'dport 22 -j ACCEPT' /etc/ufw/user6.rules 2>/dev/null || \
      sed -i 's|^### RULES ###|### RULES ###\n\n### tuple ### allow tcp 22 ::/0 any ::/0 in\n-A ufw6-user-input -p tcp --dport 22 -j ACCEPT|' /etc/ufw/user6.rules
  fi
  rm -f /etc/ssh/ssh_host_*    # 每台机器首次开机自己生成（foxos-ssh-hostkeys.service）
fi
