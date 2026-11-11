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
