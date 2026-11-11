; 把 resources\bin（foxos.cmd）放到当前用户 PATH 的最前面，卸载时去掉。
; 直接读写注册表原值（REG_EXPAND_SZ，%USERPROFILE% 之类的条目保持不展开），再通过 .NET 设置 FOXOS_BIN 广播 WM_SETTINGCHANGE。
; NSIS 里 $$ 是字面的 $，反引号是字符串定界符。
!define FOXOS_PS_HEAD `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$$d='$INSTDIR\resources\bin'; $$k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',$$true); $$p=[string]$$k.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames); $$r=@($$p -split ';' | Where-Object { $$_ -and ($$_.TrimEnd('\') -ne $$d) });`

!macro customInstall
  nsExec::ExecToLog `${FOXOS_PS_HEAD} $$k.SetValue('Path',((@($$d)+$$r) -join ';'),'ExpandString'); [Environment]::SetEnvironmentVariable('FOXOS_BIN',$$d,'User')"`
!macroend

!macro customUnInstall
  nsExec::ExecToLog `${FOXOS_PS_HEAD} $$k.SetValue('Path',($$r -join ';'),'ExpandString'); [Environment]::SetEnvironmentVariable('FOXOS_BIN',$$null,'User')"`
!macroend
