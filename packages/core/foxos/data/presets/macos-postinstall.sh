#!/bin/sh
# 狐狸OS macOS 预设：在 macOS 虚拟机里完成「设置助理」后运行（共享文件夹 FoxOS 里的这个脚本）。
# Apple 不允许跳过设置助理的自动化，所以这一步需要人在来宾里点一下终端运行：
#   sh "/Volumes/My Shared Files/FoxOS/macos-postinstall.sh"
set -eu
SEED_DIR=$(cd "$(dirname "$0")" && pwd)
NODE_VER=$(python3 -c "import json;print(json.load(open('$SEED_DIR/seed.json'))['node_version'])" 2>/dev/null || echo v24.22.2)
echo "[狐狸OS] Node.js $NODE_VER（nodejs.org 官方 pkg）"
curl -fsSL -o /tmp/node.pkg "https://nodejs.org/dist/$NODE_VER/node-$NODE_VER.pkg"
sudo installer -pkg /tmp/node.pkg -target /
echo "[狐狸OS] Bun"
curl -fsSL https://bun.sh/install | bash
echo "[狐狸OS] Gemini CLI（ACP）"
sudo npm install -g --no-fund --no-audit @google/gemini-cli
echo "[狐狸OS] foxos 命令与 MCP（Python 3 来自 Xcode 命令行工具，第一次会提示安装）"
xcode-select -p >/dev/null 2>&1 || xcode-select --install || true
mkdir -p "$HOME/FoxOS"
curl -fsSL -o /tmp/foxos.tar.gz https://github.com/gatesenman/foxos/archive/refs/heads/main.tar.gz
tar -C "$HOME/FoxOS" -xzf /tmp/foxos.tar.gz
printf '#!/bin/sh\nexport PYTHONPATH="%s/FoxOS/foxos-main/packages/core"\nexec python3 -m foxos "$@"\n' "$HOME" | sudo tee /usr/local/bin/foxos >/dev/null
sudo chmod 755 /usr/local/bin/foxos
sudo systemsetup -setremotelogin on || true
mkdir -p "$HOME/.ssh"; python3 -c "import json;print(json.load(open('$SEED_DIR/seed.json')).get('ssh_authorized_key',''))" >> "$HOME/.ssh/authorized_keys"
echo "FOXOS-PRESET-READY macos $(date +%FT%T)"
