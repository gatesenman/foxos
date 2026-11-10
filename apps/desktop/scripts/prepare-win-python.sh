#!/usr/bin/env bash
# 准备 Windows 版自带的 Python（官方 embeddable 发行包 + 办公库的 win_amd64 二进制包），输出到 build/win-python
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="$ROOT/build/win-python"
VER="${PY_VERSION:-3.12.8}"
rm -rf "$OUT"; mkdir -p "$OUT"
curl -fsSL -o "$OUT/../python-embed.zip" "https://www.python.org/ftp/python/$VER/python-$VER-embed-amd64.zip"
python3 -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$OUT/../python-embed.zip" "$OUT"
uv pip install --target "$OUT/Lib/site-packages" --python-platform x86_64-pc-windows-msvc --python-version 3.12 --only-binary :all: \
  "openpyxl>=3.1,<4" "python-docx>=1.1,<2" "python-pptx>=1.0,<2" "zstandard>=0.22"
rm -rf "$OUT/Lib/site-packages/bin"
# ._pth 文件决定模块搜索路径（embeddable 版忽略 PYTHONPATH）：site-packages 与随附的 foxos 内核 ..\core
printf 'python312.zip\r\n.\r\nLib\\site-packages\r\n..\\core\r\nimport site\r\n' > "$OUT/python312._pth"
echo "Windows Python 已准备：$OUT"
