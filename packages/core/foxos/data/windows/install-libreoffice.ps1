# 狐狸OS 安装向导：在线安装 LibreOffice（Windows x64）
# 优先用 winget；没有 winget 时从 The Document Foundation 官方下载站取最新稳定版 MSI，校验 SHA-256 后静默安装。
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
if (Get-Command winget -ErrorAction SilentlyContinue) {
  Write-Host '使用 winget 安装 LibreOffice…'
  winget install --id TheDocumentFoundation.LibreOffice -e --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -eq 0) { exit 0 }
  Write-Host "winget 返回 $LASTEXITCODE，改为直接下载 MSI…"
}
$base = 'https://download.documentfoundation.org/libreoffice/stable/'
$index = (Invoke-WebRequest -UseBasicParsing $base).Links.href | Where-Object { $_ -match '^\d+\.\d+\.\d+/$' }
$ver = ($index | ForEach-Object { $_.TrimEnd('/') } | Sort-Object { [version]$_ } | Select-Object -Last 1)
if (-not $ver) { throw '无法从官方下载站读取 LibreOffice 版本列表' }
$name = "LibreOffice_${ver}_Win_x86-64.msi"
$url = "$base$ver/win/x86_64/$name"
$dest = Join-Path $env:TEMP $name
Write-Host "下载 LibreOffice $ver：$url"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dest
Invoke-WebRequest -UseBasicParsing -Uri "$url.sha256" -OutFile "$dest.sha256"
$want = ((Get-Content -Raw "$dest.sha256") -split '\s+')[0].ToLower()
Remove-Item "$dest.sha256" -ErrorAction SilentlyContinue
$got = (Get-FileHash -Algorithm SHA256 $dest).Hash.ToLower()
if ($want -and $want -ne $got) { Remove-Item $dest; throw "SHA-256 不匹配：期望 $want，实际 $got" }
Write-Host 'SHA-256 校验通过，开始安装（会弹出管理员确认）…'
$p = Start-Process msiexec.exe -ArgumentList '/i', "`"$dest`"", '/qb', '/norestart' -Verb RunAs -Wait -PassThru
Remove-Item $dest -ErrorAction SilentlyContinue
if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { throw "安装失败，msiexec 退出码 $($p.ExitCode)" }
Write-Host 'LibreOffice 安装完成'
