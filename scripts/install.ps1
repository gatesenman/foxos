<#
.SYNOPSIS
  FoxOS online installer for Windows (x64 and arm64): downloads from GitHub Releases, verifies SHA256SUMS, installs.
  (ASCII-only on purpose so it works with "irm ... | iex" on Windows PowerShell 5.1.)

.EXAMPLE
  irm https://github.com/gatesenman/foxos/releases/download/v0.3.3-windows-preview/install.ps1 | iex

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install.ps1 -Portable

.PARAMETER Tag          Release tag. Default v0.3.3-windows-preview; "latest" = newest non-prerelease.
.PARAMETER Token        Optional GitHub token (defaults to $env:GITHUB_TOKEN / $env:GH_TOKEN). Only needed to avoid API rate limits.
.PARAMETER Portable     Install the portable zip into %LOCALAPPDATA%\FoxOS-Portable instead of running the setup program.
.PARAMETER Msi          Install the per-machine MSI package (msiexec; needs admin) instead of the NSIS setup.
.PARAMETER Arch         x64 or arm64. Default: detected from the OS (an x64 build also runs on Windows 11 arm64 under emulation).
.PARAMETER Silent       Silent install (NSIS /S, msiexec /qn).
.PARAMETER Dir          Target directory (portable) or install directory (NSIS /D=).
.PARAMETER Repo         Repository, default gatesenman/foxos.
.PARAMETER DownloadOnly Download and verify only; save the file into the current directory.
.PARAMETER Lang         Message language: zh-CN (default) or en-US. Also read from $env:FOXOS_LANG.
#>
[CmdletBinding()]
param(
  [string]$Tag = 'v0.3.3-windows-preview',
  [string]$Token = $(if ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { $env:GH_TOKEN }),
  [switch]$Portable,
  [switch]$Msi,
  [string]$Arch,
  [switch]$Silent,
  [string]$Dir,
  [string]$Repo = 'gatesenman/foxos',
  [switch]$DownloadOnly,
  [string]$Lang
)
$ErrorActionPreference = 'Stop'
# Messages: English / Simplified Chinese (default). Chinese is stored as \uXXXX escapes so the file stays ASCII.
$FoxLang = if ($Lang) { $Lang } elseif ($env:FOXOS_LANG) { $env:FOXOS_LANG } else { 'zh-CN' }
$FoxZh = -not ($FoxLang -like 'en*')
$FoxMsg = @{
  'x64only' = @('FoxOS needs 64-bit Windows (x64 or arm64).', '\u72d0\u72f8OS \u9700\u8981 64 \u4f4d Windows\uff08x64 \u6216 arm64\uff09\u3002')
  'oldwin' = @('Windows build {0} detected; Windows 10 1809 (17763) or newer is recommended.', '\u68c0\u6d4b\u5230 Windows \u7248\u672c\u53f7 {0}\uff1b\u5efa\u8bae\u4f7f\u7528 Windows 10 1809\uff0817763\uff09\u6216\u66f4\u65b0\u7248\u672c\u3002')
  'ratelimit' = @('GitHub anonymous API rate limit reached (60 requests/hour). Retry later or set $env:GITHUB_TOKEN.', 'GitHub \u533f\u540d API \u8fbe\u5230\u9891\u7387\u4e0a\u9650\uff08\u6bcf\u5c0f\u65f6 60 \u6b21\uff09\u3002\u8bf7\u7a0d\u540e\u91cd\u8bd5\uff0c\u6216\u8bbe\u7f6e $env:GITHUB_TOKEN\u3002')
  'norelease' = @('Release {0} not found in {1}.', '\u5728 {1} \u4e2d\u627e\u4e0d\u5230\u53d1\u5e03\u7248\u672c {0}\u3002')
  'relfail' = @('Failed to read release (HTTP {0}): {1}', '\u8bfb\u53d6\u53d1\u5e03\u4fe1\u606f\u5931\u8d25\uff08HTTP {0}\uff09\uff1a{1}')
  'noasset' = @('No release asset matches {0}', '\u53d1\u5e03\u6587\u4ef6\u4e2d\u6ca1\u6709\u5339\u914d {0} \u7684\u6587\u4ef6')
  'downloading' = @('Downloading {0} ({1:N1} MB)...', '\u6b63\u5728\u4e0b\u8f7d {0}\uff08{1:N1} MB\uff09\u2026')
  'nosum' = @('SHA256SUMS has no entry for {0}', 'SHA256SUMS \u4e2d\u6ca1\u6709 {0} \u7684\u6821\u9a8c\u503c')
  'mismatch' = @('SHA-256 mismatch: expected {0}, got {1} (corrupted or tampered download)', 'SHA-256 \u4e0d\u4e00\u81f4\uff1a\u5e94\u4e3a {0}\uff0c\u5b9e\u9645 {1}\uff08\u4e0b\u8f7d\u635f\u574f\u6216\u88ab\u7be1\u6539\uff09')
  'shaok' = @('SHA-256 OK: {0}', 'SHA-256 \u6821\u9a8c\u901a\u8fc7\uff1a{0}')
  'saved' = @('Saved: {0}', '\u5df2\u4fdd\u5b58\uff1a{0}')
  'extracted' = @('Extracted to {0}; Start menu shortcut: {1}', '\u5df2\u89e3\u538b\u5230 {0}\uff1b\u5f00\u59cb\u83dc\u5355\u5feb\u6377\u65b9\u5f0f\uff1a{1}')
  'running' = @('Running setup...', '\u6b63\u5728\u8fd0\u884c\u5b89\u88c5\u7a0b\u5e8f\u2026')
  'setupexit' = @('Setup exited with code {0}', '\u5b89\u88c5\u7a0b\u5e8f\u9000\u51fa\u7801 {0}')
  'onpath' = @('foxos CLI added to the user PATH: {0} (run foxos --version in a new terminal)', '\u547d\u4ee4\u884c foxos \u5df2\u52a0\u5165\u7528\u6237 PATH\uff1a{0}\uff08\u65b0\u5f00\u7684\u7ec8\u7aef\u91cc\u76f4\u63a5\u8fd0\u884c foxos --version\uff09')
  'done' = @('Done. Open FoxOS from the Start menu; the first-run wizard installs optional components (LibreOffice, WSL, ACP agents).', '\u5b8c\u6210\u3002\u4ece\u5f00\u59cb\u83dc\u5355\u6253\u5f00\u72d0\u72f8OS\uff1b\u9996\u6b21\u8fd0\u884c\u5411\u5bfc\u4f1a\u5b89\u88c5\u53ef\u9009\u7ec4\u4ef6\uff08LibreOffice\u3001WSL\u3001ACP \u667a\u80fd\u4f53\uff09\u3002')
}
function M([string]$key) {
  $pair = $FoxMsg[$key]
  $fmt = if ($FoxZh) { [regex]::Unescape($pair[1]) } else { $pair[0] }
  if ($args.Count) { return ($fmt -f $args) } else { return $fmt }
}
# With "irm | iex" no parameters can be passed: FOXOS_PORTABLE=1 / FOXOS_DOWNLOAD_ONLY=1 / FOXOS_TAG=... do the same
if ($env:FOXOS_PORTABLE -eq '1') { $Portable = [switch]$true }
if ($env:FOXOS_DOWNLOAD_ONLY -eq '1') { $DownloadOnly = [switch]$true }
if ($env:FOXOS_MSI -eq '1') { $Msi = [switch]$true }
if ($env:FOXOS_ARCH) { $Arch = $env:FOXOS_ARCH }
if ($env:FOXOS_TAG) { $Tag = $env:FOXOS_TAG }
$ProgressPreference = 'SilentlyContinue'   # the progress bar makes downloads very slow on PowerShell 5.1
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not [Environment]::Is64BitOperatingSystem) { throw (M 'x64only') }
if (-not $Arch) {
  $cpu = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
  $Arch = if ($cpu -eq 'ARM64') { 'arm64' } else { 'x64' }
}
if ($Arch -notin @('x64', 'arm64')) { throw (M 'x64only') }
if ($IsWindows -or $env:OS -eq 'Windows_NT') {
  $build = [Environment]::OSVersion.Version.Build
  if ($build -lt 17763) { Write-Warning (M 'oldwin' $build) }
}

# Put resources\bin (foxos.cmd) first on the user PATH and drop missing old FoxOS entries; also update this session.
# Read and write the raw registry value (REG_EXPAND_SZ) so entries like %USERPROFILE%\... stay unexpanded,
# then set FOXOS_BIN through .NET, which broadcasts WM_SETTINGCHANGE so new terminals see the change.
function Add-FoxosPath([string]$bin) {
  if (-not (Test-Path (Join-Path $bin 'foxos.cmd'))) { return }
  $bin = $bin.TrimEnd('\')
  $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true)
  $cur = [string]$key.GetValue('Path', '', [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
  $rest = @($cur -split ';' | Where-Object { $_ -and ($_.TrimEnd('\') -ne $bin) -and -not (($_ -like '*\resources\bin') -and -not (Test-Path ([Environment]::ExpandEnvironmentVariables($_)))) })
  $key.SetValue('Path', ((@($bin) + $rest) -join ';'), [Microsoft.Win32.RegistryValueKind]::ExpandString)
  $key.Close()
  [Environment]::SetEnvironmentVariable('FOXOS_BIN', $bin, 'User')
  if (($env:Path -split ';') -notcontains $bin) { $env:Path = "$bin;$env:Path" }
  Write-Host (M 'onpath' $bin)
}

$headers = @{ 'User-Agent' = 'foxos-install'; 'Accept' = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
if ($Token) { $headers['Authorization'] = "Bearer $Token" }
$api = "https://api.github.com/repos/$Repo/releases/" + $(if ($Tag -eq 'latest') { 'latest' } else { "tags/$Tag" })
try { $rel = Invoke-RestMethod -Uri $api -Headers $headers }
catch {
  $code = $_.Exception.Response.StatusCode.value__
  if ($code -eq 403 -and -not $Token) { throw (M 'ratelimit') }
  if ($code -eq 404) { throw (M 'norelease' $Tag $Repo) }
  throw (M 'relfail' $code $_.Exception.Message)
}
Write-Host "FoxOS $($rel.tag_name) (windows-$Arch)"

function Get-Asset([string]$pattern) {
  $a = $rel.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
  if (-not $a) { throw (M 'noasset' $pattern) }
  return $a
}
function Save-Asset($asset, [string]$dest) {
  Write-Host (M 'downloading' $asset.name ($asset.size / 1MB))
  if ($Token) {
    $h = $headers.Clone(); $h['Accept'] = 'application/octet-stream'
    Invoke-WebRequest -UseBasicParsing -Uri $asset.url -Headers $h -OutFile $dest
  } else {
    Invoke-WebRequest -UseBasicParsing -Uri $asset.browser_download_url -Headers @{ 'User-Agent' = 'foxos-install' } -OutFile $dest
  }
}

$tmpRoot = if ($env:TEMP) { $env:TEMP } else { [IO.Path]::GetTempPath() }
$tmp = Join-Path $tmpRoot ('foxos-install-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $asset = if ($Portable) { Get-Asset "FoxOS-*-win-$Arch.zip" } elseif ($Msi) { Get-Asset "FoxOS-*-win-$Arch.msi" } else { Get-Asset "FoxOS-Setup-*-$Arch.exe" }
  $sums = Get-Asset 'SHA256SUMS'
  $file = Join-Path $tmp $asset.name
  Save-Asset $sums (Join-Path $tmp 'SHA256SUMS')
  Save-Asset $asset $file
  $line = Get-Content (Join-Path $tmp 'SHA256SUMS') | Where-Object { ($_ -split '\s+')[-1].TrimStart('*') -eq $asset.name } | Select-Object -First 1
  if (-not $line) { throw (M 'nosum' $asset.name) }
  $want = ($line -split '\s+')[0].ToLower()
  $got = (Get-FileHash -Algorithm SHA256 $file).Hash.ToLower()
  if ($want -ne $got) { throw (M 'mismatch' $want $got) }
  Write-Host (M 'shaok' $got)
  if ($DownloadOnly) {
    $out = Join-Path (Get-Location) $asset.name
    Copy-Item $file $out -Force
    Write-Host (M 'saved' $out)
    return
  }
  if ($Portable) {
    $target = if ($Dir) { $Dir } else { Join-Path $env:LOCALAPPDATA 'FoxOS-Portable' }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Expand-Archive -Path $file -DestinationPath $target
    $exe = Get-ChildItem -Path $target -Filter 'FoxOS.exe' -Recurse | Select-Object -First 1
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'FoxOS (portable).lnk'
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($lnk); $s.TargetPath = $exe.FullName; $s.WorkingDirectory = $exe.DirectoryName; $s.Save()
    Write-Host (M 'extracted' $target $lnk)
    Add-FoxosPath (Join-Path $exe.DirectoryName 'resources\bin')
    Start-Process $exe.FullName
  } elseif ($Msi) {
    $msiArgs = @('/i', "`"$file`"", $(if ($Silent) { '/qn' } else { '/passive' }), '/norestart')
    if ($Dir) { $msiArgs += "APPLICATIONFOLDER=`"$Dir`"" }
    Write-Host (M 'running')
    $p = Start-Process -FilePath 'msiexec.exe' -ArgumentList $msiArgs -Wait -PassThru
    if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { throw (M 'setupexit' $p.ExitCode) }
    $root = if ($Dir) { $Dir } else { Join-Path $env:ProgramFiles 'FoxOS' }
    Add-FoxosPath (Join-Path $root 'resources\bin')
    Write-Host (M 'done')
  } else {
    $instArgs = @()
    if ($Silent) { $instArgs += '/S' }
    if ($Dir) { $instArgs += "/D=$Dir" }   # NSIS wants /D= last and unquoted
    Write-Host (M 'running')
    $p = if ($instArgs.Count) { Start-Process -FilePath $file -ArgumentList $instArgs -Wait -PassThru } else { Start-Process -FilePath $file -Wait -PassThru }
    if ($p.ExitCode -ne 0) { throw (M 'setupexit' $p.ExitCode) }
    # The NSIS setup already adds resources\bin to the user PATH; this also updates the current session
    $root = if ($Dir) { $Dir } else { Join-Path $env:LOCALAPPDATA 'Programs\FoxOS' }
    Add-FoxosPath (Join-Path $root 'resources\bin')
    Write-Host (M 'done')
  }
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
