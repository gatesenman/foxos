# 狐狸OS Windows 预设：首次登录时运行（autounattend.xml 的 FirstLogonCommands）。
# 安装运行时（Node.js / Bun / Python / Git）、ACP 智能体（Gemini CLI）、狐狸OS Windows 伴侣（foxos 命令与 MCP），
# 开启 OpenSSH 服务器并放入主机的公钥，让主机上的 foxos env exec 能连进来。全部从各项目官方地址下载。
$ErrorActionPreference = 'Continue'
$seed = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg = Get-Content (Join-Path $seed 'seed.json') -Raw | ConvertFrom-Json
$log = 'C:\FoxOS\preset-install.log'
New-Item -ItemType Directory -Force -Path 'C:\FoxOS' | Out-Null
function Log($m) { "$(Get-Date -Format s) $m" | Tee-Object -FilePath $log -Append }
function Get-File($url, $out) { Log "下载 $url"; Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $out }
$tmp = Join-Path $env:TEMP 'foxos-preset'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null

Log '语言与区域：zh-CN'
try { Set-WinUILanguageOverride -Language zh-CN; Set-WinSystemLocale zh-CN; Set-Culture zh-CN; Set-WinUserLanguageList zh-CN -Force } catch { Log $_ }

Log "Node.js $($cfg.node_version)"
Get-File "https://nodejs.org/dist/$($cfg.node_version)/node-$($cfg.node_version)-x64.msi" "$tmp\node.msi"
Start-Process msiexec.exe -Wait -ArgumentList '/i', "$tmp\node.msi", '/qn', '/norestart'
Log "Python $($cfg.python_version)"
Get-File "https://www.python.org/ftp/python/$($cfg.python_version)/python-$($cfg.python_version)-amd64.exe" "$tmp\python.exe"
Start-Process "$tmp\python.exe" -Wait -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0'
Log 'Git for Windows'
$git = (Invoke-RestMethod 'https://api.github.com/repos/git-for-windows/git/releases/latest').assets | Where-Object name -like 'Git-*-64-bit.exe' | Select-Object -First 1
if ($git) { Get-File $git.browser_download_url "$tmp\git.exe"; Start-Process "$tmp\git.exe" -Wait -ArgumentList '/VERYSILENT', '/NORESTART' }
Log 'Bun'
try { powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://bun.sh/install.ps1 | iex" } catch { Log $_ }
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')

Log 'ACP 智能体：Gemini CLI（Apache-2.0）'
& npm.cmd install -g --no-fund --no-audit '@google/gemini-cli' 2>&1 | Out-File -Append $log

Log '狐狸OS Windows 伴侣（foxos 命令、MCP、智能体会话）'
Get-File $cfg.companion_install "$tmp\install.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$tmp\install.ps1" -Silent 2>&1 | Out-File -Append $log

Log 'OpenSSH 服务器 + 主机公钥（foxos 桥）'
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
Set-Service sshd -StartupType Automatic; Start-Service sshd
if ($cfg.ssh_authorized_key) {
  $ak = 'C:\ProgramData\ssh\administrators_authorized_keys'
  Set-Content -Path $ak -Value $cfg.ssh_authorized_key -Encoding ascii
  icacls $ak /inheritance:r /grant 'Administrators:F' /grant 'SYSTEM:F' | Out-Null
}
New-NetFirewallRule -Name 'FoxOS-SSH' -DisplayName 'FoxOS bridge (SSH)' -Protocol TCP -LocalPort 22 -Action Allow -ErrorAction SilentlyContinue | Out-Null

"FOXOS-PRESET-READY windows $(Get-Date -Format s)" | Set-Content 'C:\FoxOS\preset-ready.txt'
Log '完成'
