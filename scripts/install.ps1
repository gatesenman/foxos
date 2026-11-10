<#
.SYNOPSIS
  FoxOS online installer for Windows x64: downloads from GitHub Releases, verifies SHA256SUMS, installs.
  (ASCII-only on purpose so it works with "irm ... | iex" on Windows PowerShell 5.1.)

.EXAMPLE
  irm https://github.com/gatesenman/foxos/releases/download/v0.2.0-windows-preview/install.ps1 | iex

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install.ps1 -Portable

.PARAMETER Tag          Release tag. Default v0.2.0-windows-preview; "latest" = newest non-prerelease.
.PARAMETER Token        Optional GitHub token (defaults to $env:GITHUB_TOKEN / $env:GH_TOKEN). Only needed to avoid API rate limits.
.PARAMETER Portable     Install the portable zip into %LOCALAPPDATA%\FoxOS-Portable instead of running the setup program.
.PARAMETER Silent       Silent install (NSIS /S).
.PARAMETER Dir          Target directory (portable) or install directory (NSIS /D=).
.PARAMETER Repo         Repository, default gatesenman/foxos.
.PARAMETER DownloadOnly Download and verify only; save the file into the current directory.
#>
[CmdletBinding()]
param(
  [string]$Tag = 'v0.2.0-windows-preview',
  [string]$Token = $(if ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { $env:GH_TOKEN }),
  [switch]$Portable,
  [switch]$Silent,
  [string]$Dir,
  [string]$Repo = 'gatesenman/foxos',
  [switch]$DownloadOnly
)
$ErrorActionPreference = 'Stop'
# With "irm | iex" no parameters can be passed: FOXOS_PORTABLE=1 / FOXOS_DOWNLOAD_ONLY=1 / FOXOS_TAG=... do the same
if ($env:FOXOS_PORTABLE -eq '1') { $Portable = [switch]$true }
if ($env:FOXOS_DOWNLOAD_ONLY -eq '1') { $DownloadOnly = [switch]$true }
if ($env:FOXOS_TAG) { $Tag = $env:FOXOS_TAG }
$ProgressPreference = 'SilentlyContinue'   # the progress bar makes downloads very slow on PowerShell 5.1
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not [Environment]::Is64BitOperatingSystem) { throw 'FoxOS currently ships Windows x64 builds only.' }
if ($IsWindows -or $env:OS -eq 'Windows_NT') {
  $build = [Environment]::OSVersion.Version.Build
  if ($build -lt 17763) { Write-Warning "Windows build $build detected; Windows 10 1809 (17763) or newer is recommended." }
}

$headers = @{ 'User-Agent' = 'foxos-install'; 'Accept' = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
if ($Token) { $headers['Authorization'] = "Bearer $Token" }
$api = "https://api.github.com/repos/$Repo/releases/" + $(if ($Tag -eq 'latest') { 'latest' } else { "tags/$Tag" })
try { $rel = Invoke-RestMethod -Uri $api -Headers $headers }
catch {
  $code = $_.Exception.Response.StatusCode.value__
  if ($code -eq 403 -and -not $Token) { throw 'GitHub anonymous API rate limit reached (60 requests/hour). Retry later or set $env:GITHUB_TOKEN.' }
  if ($code -eq 404) { throw "Release $Tag not found in $Repo." }
  throw "Failed to read release (HTTP $code): $($_.Exception.Message)"
}
Write-Host "FoxOS $($rel.tag_name)"

function Get-Asset([string]$pattern) {
  $a = $rel.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
  if (-not $a) { throw "No release asset matches $pattern" }
  return $a
}
function Save-Asset($asset, [string]$dest) {
  Write-Host ('Downloading {0} ({1:N1} MB)...' -f $asset.name, ($asset.size / 1MB))
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
  $asset = if ($Portable) { Get-Asset 'FoxOS-*-win-x64.zip' } else { Get-Asset 'FoxOS-Setup-*-x64.exe' }
  $sums = Get-Asset 'SHA256SUMS'
  $file = Join-Path $tmp $asset.name
  Save-Asset $sums (Join-Path $tmp 'SHA256SUMS')
  Save-Asset $asset $file
  $line = Get-Content (Join-Path $tmp 'SHA256SUMS') | Where-Object { ($_ -split '\s+')[-1].TrimStart('*') -eq $asset.name } | Select-Object -First 1
  if (-not $line) { throw "SHA256SUMS has no entry for $($asset.name)" }
  $want = ($line -split '\s+')[0].ToLower()
  $got = (Get-FileHash -Algorithm SHA256 $file).Hash.ToLower()
  if ($want -ne $got) { throw "SHA-256 mismatch: expected $want, got $got (corrupted or tampered download)" }
  Write-Host "SHA-256 OK: $got"
  if ($DownloadOnly) {
    $out = Join-Path (Get-Location) $asset.name
    Copy-Item $file $out -Force
    Write-Host "Saved: $out"
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
    Write-Host "Extracted to $target; Start menu shortcut: $lnk"
    Start-Process $exe.FullName
  } else {
    $instArgs = @()
    if ($Silent) { $instArgs += '/S' }
    if ($Dir) { $instArgs += "/D=$Dir" }   # NSIS wants /D= last and unquoted
    Write-Host 'Running setup...'
    $p = if ($instArgs.Count) { Start-Process -FilePath $file -ArgumentList $instArgs -Wait -PassThru } else { Start-Process -FilePath $file -Wait -PassThru }
    if ($p.ExitCode -ne 0) { throw "Setup exited with code $($p.ExitCode)" }
    Write-Host 'Done. Open FoxOS from the Start menu; the first-run wizard installs optional components (LibreOffice, WSL, ACP agents).'
  }
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
