<#
.SYNOPSIS
  狐狸OS（FoxOS）Windows 在线安装：从 GitHub Release 下载安装包，校验 SHA256SUMS 后安装。

.EXAMPLE
  # 仓库是私有的：先设置能读取 gatesenman/foxos 的令牌
  $env:GITHUB_TOKEN = '<令牌>'
  powershell -ExecutionPolicy Bypass -File install.ps1

.EXAMPLE
  # 便携版：解压到 %LOCALAPPDATA%\FoxOS-Portable 并创建开始菜单快捷方式，不写注册表
  powershell -ExecutionPolicy Bypass -File install.ps1 -Portable

.PARAMETER Tag      Release 标签，默认 v0.2.0-windows-preview；传 latest 取最新正式版
.PARAMETER Token    GitHub 令牌（默认读取环境变量 GITHUB_TOKEN / GH_TOKEN；公开仓库可不填）
.PARAMETER Portable 安装便携版 zip 而不是安装程序
.PARAMETER Silent   静默安装（NSIS /S）
.PARAMETER Dir      便携版解压目录，或安装程序的安装目录（NSIS /D=）
.PARAMETER Repo     仓库，默认 gatesenman/foxos
.PARAMETER DownloadOnly 只下载并校验，把文件保存到当前目录，不安装
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
$ProgressPreference = 'SilentlyContinue'   # Windows PowerShell 5.1 的进度条会让下载慢很多
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not [Environment]::Is64BitOperatingSystem) { throw '狐狸OS 目前只提供 Windows x64 版本' }
$build = [Environment]::OSVersion.Version.Build
if ($build -lt 17763) { Write-Warning "当前 Windows 版本号 $build；建议 Windows 10 1809（17763）或更新版本" }

$headers = @{ 'User-Agent' = 'foxos-install'; 'Accept' = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
if ($Token) { $headers['Authorization'] = "Bearer $Token" }
$api = "https://api.github.com/repos/$Repo/releases/" + $(if ($Tag -eq 'latest') { 'latest' } else { "tags/$Tag" })
try { $rel = Invoke-RestMethod -Uri $api -Headers $headers }
catch {
  $code = $_.Exception.Response.StatusCode.value__
  if ($code -eq 404 -and -not $Token) { throw "找不到 Release $Tag。仓库 $Repo 是私有的：请先设置 `$env:GITHUB_TOKEN 为有读取权限的令牌" }
  throw "读取 Release 失败（HTTP $code）：$($_.Exception.Message)"
}
Write-Host "狐狸OS $($rel.tag_name)  $($rel.name)"

function Get-Asset([string]$pattern) {
  $a = $rel.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
  if (-not $a) { throw "Release 中没有匹配 $pattern 的文件" }
  return $a
}
function Save-Asset($asset, [string]$dest) {
  $h = $headers.Clone(); $h['Accept'] = 'application/octet-stream'
  Write-Host ("下载 {0}（{1:N1} MB）…" -f $asset.name, ($asset.size / 1MB))
  Invoke-WebRequest -UseBasicParsing -Uri $asset.url -Headers $h -OutFile $dest
}

$tmp = Join-Path $env:TEMP ("foxos-install-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $asset = if ($Portable) { Get-Asset 'FoxOS-*-win-x64.zip' } else { Get-Asset 'FoxOS-Setup-*-x64.exe' }
  $sums = Get-Asset 'SHA256SUMS'
  $file = Join-Path $tmp $asset.name
  Save-Asset $sums (Join-Path $tmp 'SHA256SUMS')
  Save-Asset $asset $file
  $line = Get-Content (Join-Path $tmp 'SHA256SUMS') | Where-Object { ($_ -split '\s+')[-1].TrimStart('*') -eq $asset.name } | Select-Object -First 1
  if (-not $line) { throw "SHA256SUMS 中没有 $($asset.name)" }
  $want = ($line -split '\s+')[0].ToLower()
  $got = (Get-FileHash -Algorithm SHA256 $file).Hash.ToLower()
  if ($want -ne $got) { throw "SHA-256 不匹配：期望 $want，实际 $got（文件可能损坏或被篡改）" }
  Write-Host "SHA-256 校验通过：$got"
  if ($DownloadOnly) {
    Copy-Item $file (Join-Path (Get-Location) $asset.name) -Force
    Write-Host "已保存：$(Join-Path (Get-Location) $asset.name)"
    return
  }

  if ($Portable) {
    $target = if ($Dir) { $Dir } else { Join-Path $env:LOCALAPPDATA 'FoxOS-Portable' }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Expand-Archive -Path $file -DestinationPath $target
    $exe = Get-ChildItem -Path $target -Filter 'FoxOS.exe' -Recurse | Select-Object -First 1
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) '狐狸OS（便携版）.lnk'
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($lnk); $s.TargetPath = $exe.FullName; $s.WorkingDirectory = $exe.DirectoryName; $s.Save()
    Write-Host "已解压到 $target，开始菜单快捷方式：$lnk"
    Start-Process $exe.FullName
  } else {
    $instArgs = @()
    if ($Silent) { $instArgs += '/S' }
    if ($Dir) { $instArgs += "/D=$Dir" }   # NSIS 要求 /D= 放在最后且不加引号
    Write-Host '运行安装程序…'
    $p = if ($instArgs.Count) { Start-Process -FilePath $file -ArgumentList $instArgs -Wait -PassThru } else { Start-Process -FilePath $file -Wait -PassThru }
    if ($p.ExitCode -ne 0) { throw "安装程序退出码 $($p.ExitCode)" }
    Write-Host '安装完成。从开始菜单打开“狐狸OS”。首次运行会打开安装向导（LibreOffice、环境 / WSL、ACP 智能体等组件在线安装）。'
  }
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
