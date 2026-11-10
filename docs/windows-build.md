# 在 Linux 上构建 Windows x64 安装包

产物：`apps/desktop/dist/FoxOS-Setup-<版本>-x64.exe`（NSIS 安装程序，可选安装目录、按用户安装）与 `FoxOS-<版本>-win-x64.zip`（便携版）。

```bash
cd apps/desktop
npm ci
# 1. Windows 版终端依赖：node-pty 的 win32-x64 预编译包（N-API，含 conpty.node / OpenConsole.exe）
npm run prepare:win-pty
# 2. 自带 Python：python.org 的 3.12 embeddable 包 + 办公库 / zstandard 的 win_amd64 wheel（uv 跨平台安装），输出 build/win-python
npm run prepare:win-python
# 3. electron-builder 交叉构建；NSIS 与改图标需要 wine（无需 root：可用便携版 wine，设置 WINEPREFIX 即可）
PATH=/path/to/wine/bin:$PATH WINEPREFIX=$HOME/.wine-foxos WINEDEBUG=-all npx electron-builder --win --x64
# 4. 校验文件
cd dist && sha256sum FoxOS-Setup-*-x64.exe FoxOS-*-win-x64.zip ../../../scripts/install.ps1 | sed 's#../../../scripts/##' > SHA256SUMS
```

要点：

- `npmRebuild: false`：不在 Linux 上重新编译原生模块，Windows 用预编译包；`asarUnpack` 解出 `@lydell/**`，Linux 版的 pty 包不进 Windows 包
- 内核（`packages/core/foxos`）作为 `resources/core` 随包；Python 在 `resources/python`，`python312._pth` 把 `..\core` 和 `Lib\site-packages`
  加入搜索路径（embeddable Python 忽略 `PYTHONPATH`）；桌面启动时优先用它（`src/main/kernel.js` 的 `bundledPython()`）
- 安装包未做代码签名（`signExecutable: false`），首次运行会有 SmartScreen 提示
- LibreOffice 不随包：首次运行向导在线安装（winget；没有 winget 时用 `foxos/data/windows/install-libreoffice.ps1` 从官方站下载 MSI 并校验 SHA-256）

用户侧在线安装：`scripts/install.ps1`（从 GitHub Release 下载、校验 `SHA256SUMS`、运行安装程序或解压便携版；私有仓库需 `GITHUB_TOKEN`）。
实机验收清单见 [windows-test-guide.md](windows-test-guide.md)。
