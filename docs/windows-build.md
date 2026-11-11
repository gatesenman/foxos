# 在 Linux 上构建 Windows 安装包（x64 / arm64）

正式发布由 GitHub Actions 在 Windows runner 上原生构建（`windows-2022` 出 x64、`windows-11-arm` 出 arm64，含 MSI），见 [install.md](install.md#这些安装包是怎么做出来的) 与 [`.github/workflows/release.yml`](../.github/workflows/release.yml)。
这一页是在 Linux 上交叉构建的方法，产物：`FoxOS-Setup-<版本>-<x64|arm64>.exe`（NSIS 安装程序，可选安装目录、按用户安装）与 `FoxOS-<版本>-win-<x64|arm64>.zip`（便携版）。
MSI（`FoxOS-<版本>-win-<arch>.msi`）用 WiX，需要 .NET，在 wine 里跑不起来（`candle.exe` 直接崩溃），只在 Windows 上构建。

```bash
cd apps/desktop
npm ci
# 1. 只保留目标平台的 node-pty 预编译包，并准备自带 Python（python.org embeddable 包 + 办公库的 Windows wheel，uv 跨平台安装），输出 build/python
bash ../../scripts/packaging/prepare-platform.sh win x64        # arm64：win arm64
# 2. electron-builder 交叉构建；NSIS 与改图标需要 wine（无需 root：可用便携版 wine，设置 WINEPREFIX 即可）
PATH=/path/to/wine/bin:$PATH WINEPREFIX=$HOME/.wine-foxos WINEDEBUG=-all npx electron-builder --win nsis zip --x64 --publish never
# 3. 统一文件名并写校验和
bash ../../scripts/packaging/collect-artifacts.sh dist ../../out/win-x64 win x64
```

要点：

- `npmRebuild: false`：不在 Linux 上重新编译原生模块，Windows 用预编译包；`asarUnpack` 解出 `@lydell/**`，Linux 版的 pty 包不进 Windows 包
- 内核（`packages/core/foxos`）作为 `resources/core` 随包；Python 在 `resources/python`，`python312._pth` 把 `..\core` 和 `Lib\site-packages`
  加入搜索路径（embeddable Python 忽略 `PYTHONPATH`）；桌面启动时优先用它（`src/main/kernel.js` 的 `bundledPython()`）
- 安装包默认不做代码签名（`signExecutable: false`），首次运行会有 SmartScreen 提示；在仓库 Secrets 里配置 `WIN_CSC_LINK` / `WIN_CSC_KEY_PASSWORD` 后，CI 自动签名
- LibreOffice 不随包：首次运行向导在线安装（winget；没有 winget 时用 `foxos/data/windows/install-libreoffice.ps1` 从官方站下载 MSI 并校验 SHA-256）

用户侧在线安装：`scripts/install.ps1`（从 GitHub Release 匿名下载、校验 `SHA256SUMS`、运行安装程序或解压便携版；`GITHUB_TOKEN` 可选，仅用于避开 API 频率限制）。脚本保持纯 ASCII，保证 Windows PowerShell 5.1 下 `irm … | iex` 可用。
实机验收清单见 [windows-test-guide.md](windows-test-guide.md)。
