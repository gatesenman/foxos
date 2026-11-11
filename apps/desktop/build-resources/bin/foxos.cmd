@echo off
rem foxos command line (bundled Python 3.12 + kernel). The installer adds this folder to the user PATH.
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
if not defined PYTHONPYCACHEPREFIX set "PYTHONPYCACHEPREFIX=%LOCALAPPDATA%\FoxOS\pycache"
"%~dp0..\python\python.exe" -m foxos %*
exit /b %ERRORLEVEL%
