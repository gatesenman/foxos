#!/bin/sh
# 智能体运行环境：Node LTS（npm、corepack、pnpm）、Bun、uv、gh、Gemini CLI、Codex（含 ACP 适配器）、Qwen Code、opencode，
# 以及「智能体」窗口与首次登录安装。清单与版本固定在 foxos/data/runtime-manifest.json；下载都校验 sha256（npm 包由 npm 校验固定版本）。
# 专有许可的命令行（Claude Code、Claude Agent ACP、Cursor CLI）不进 ISO，首次登录时经用户确认才从官方来源下载。
set -eu
SRC=/usr/src/foxos-os
PY=/usr/lib/foxos/venv/bin/python
export PYTHONPATH=/usr/lib/foxos/python HOME=/root FOXOS_HOME=/root/.foxos-build FOXOS_LANG=en-US FOXOS_PROGRESS=1
export npm_config_cache=/var/tmp/foxos-npm-cache UV_CACHE_DIR=/var/tmp/foxos-uv-cache
"$PY" -m foxos.runtime install --phase iso --system
echo "35-agent-runtime: installed"
"$PY" -m foxos.runtime check || { echo "35-agent-runtime: an ISO-phase tool failed its --version check" >&2; exit 1; }
# 电脑操控后端（Apache-2.0，版本固定）：agent-desktop（默认：无障碍树观察 / 操作）、agent-browser（兜底：网页，经 CDP 连自带 Chrome）
for pkg in agent-desktop@1.2.0 agent-browser@0.42.0; do
  name=${pkg%@*}
  install -d "/usr/lib/foxos/tools/$name"
  npm install --prefix "/usr/lib/foxos/tools/$name" --no-audit --no-fund "$pkg"
  "/usr/lib/foxos/tools/$name/node_modules/.bin/$name" --version
done
rm -rf /var/tmp/foxos-npm-cache /var/tmp/foxos-uv-cache /root/.foxos-build /root/.npm /root/.cache/node-gyp
# 用户 PATH：~/.local/bin（首次登录与 foxos runtime install 装在这里），/usr/local/bin 已在默认 PATH
cat > /etc/profile.d/foxos-runtime.sh <<'P'
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) PATH="$HOME/.local/bin:$PATH" ;; esac
export PATH
P
# 「智能体」窗口、首次登录安装、图标
install -m 755 "$SRC/bots/foxos-bots" /usr/bin/foxos-bots
install -m 755 "$SRC/bots/foxos-runtime-firstboot" /usr/bin/foxos-runtime-firstboot
install -m 644 "$SRC/bots/foxos-bots.desktop" /usr/share/applications/foxos-bots.desktop
install -d /etc/xdg/autostart /usr/share/icons/hicolor/scalable/apps
install -m 644 "$SRC/bots/foxos-runtime-firstboot.desktop" /etc/xdg/autostart/foxos-runtime-firstboot.desktop
install -m 644 /usr/lib/foxos/python/foxos/botchat/static/favicon.svg /usr/share/icons/hicolor/scalable/apps/foxos-bots.svg
gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
# 许可证与来源
install -d /usr/share/doc/foxos
install -m 644 /usr/lib/foxos/python/foxos/data/pstack/NOTICE /usr/share/doc/foxos/NOTICE.pstack
install -m 644 /usr/lib/foxos/python/foxos/botchat/static/vendor/tabler/LICENSE /usr/share/doc/foxos/LICENSE.tabler-icons
"$PY" - <<'J' > /usr/share/doc/foxos/agent-runtime.txt
import json
from foxos import runtime
for t in runtime.manifest()["tools"]:
    print(f"{t['name']:<16} {t['version']:<22} {t['phase']:<10} {t['license']:<40} {t['source']}")
J
