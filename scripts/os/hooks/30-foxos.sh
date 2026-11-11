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
  cp -a "$SRC/vmm/." /usr/lib/foxos/vmm/
  if [ -f /usr/lib/foxos/vmm/NOTICE ]; then
    cp /usr/lib/foxos/vmm/NOTICE /usr/share/doc/foxos/NOTICE.vmm
  fi
  if [ -x /usr/lib/foxos/vmm/cloud-hypervisor ]; then
    ln -sf /usr/lib/foxos/vmm/cloud-hypervisor /usr/bin/cloud-hypervisor
  fi
fi
