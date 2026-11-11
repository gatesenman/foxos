"""US-86：Windows 伴侣程序从不依赖 PATH 上的 foxos（Sarah 的 0.2.0 上应用中心“安装”报 CommandNotFoundException）。

根因：Windows 的环境变量名不区分大小写，真机上叫 "Path"；pty.js 用 `{...process.env, PATH: shim + …}` 得到两个键，
PowerShell 读到的是没改过的 "Path"，于是 `foxos everything install …` 找不到命令。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DESK = ROOT / "apps" / "desktop"


def node(js: str):
    if not shutil.which("node"):
        pytest.skip("需要 node")
    r = subprocess.run(["node", "-e", js], cwd=DESK, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def test_US86_with_path_keeps_a_single_windows_path_key():
    out = node("""
const { withPath } = require('./src/main/cmdline.js');
const env = withPath({ Path: 'C:\\\\Windows\\\\system32', TERM: 'x' }, ['C:\\\\Users\\\\A\\\\AppData\\\\Roaming\\\\FoxOS\\\\bin'], true);
const old = { ...{ Path: 'C:\\\\Windows\\\\system32' }, PATH: 'C:\\\\shim;C:\\\\Windows\\\\system32' };
console.log(JSON.stringify({ keys: Object.keys(env).filter((k) => k.toUpperCase() === 'PATH'), value: env.Path, oldKeys: Object.keys(old) }));
""")
    assert out["keys"] == ["Path"]
    assert out["value"].startswith("C:\\Users\\A\\AppData\\Roaming\\FoxOS\\bin;")
    assert out["oldKeys"] == ["Path", "PATH"]          # 0.2.0 的写法：两个键，子进程看到的是旧的 Path


def test_US86_terminal_commands_use_an_absolute_cli_path():
    out = node("""
const { foxosCommandLine, mergeUserPath } = require('./src/main/cmdline.js');
let rel = null; try { foxosCommandLine('foxos', ['--version'], 'powershell'); } catch (e) { rel = e.message; }
console.log(JSON.stringify({
  ps: foxosCommandLine("C:\\\\Users\\\\O'Brien\\\\AppData\\\\Roaming\\\\FoxOS\\\\bin\\\\foxos.cmd", ['everything', 'install', 'circuits'], 'powershell'),
  sh: foxosCommandLine('/opt/FoxOS/resources/bin/foxos', ['env', 'shell', "a b'c"], 'posix'),
  rel,
  merged: mergeUserPath('%USERPROFILE%\\\\bin;C:\\\\Old\\\\resources\\\\bin;C:\\\\New\\\\resources\\\\bin\\\\', 'C:\\\\New\\\\resources\\\\bin', () => false),
}));
""")
    assert out["ps"] == "& 'C:\\Users\\O''Brien\\AppData\\Roaming\\FoxOS\\bin\\foxos.cmd' 'everything' 'install' 'circuits'; exit $LASTEXITCODE"
    assert out["sh"] == "'/opt/FoxOS/resources/bin/foxos' 'env' 'shell' 'a b'\\''c'"
    assert out["rel"] and "绝对路径" in out["rel"]
    assert out["merged"] == "C:\\New\\resources\\bin;%USERPROFILE%\\bin"


def test_US86_no_renderer_or_main_code_runs_bare_foxos():
    """渲染进程与主进程都不能拼出 `foxos …` 这种依赖 PATH 的命令行。"""
    bad = []
    for f in list((DESK / "src" / "renderer").rglob("*.js")) + list((DESK / "src" / "main").glob("*.js")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("//"):
                continue
            if re.search(r"[`'\"]foxos (everything|env|sheets|docs|slides|acp|mcp|desktop|ssh|machines?|vm|guest)\b", line):
                bad.append(f"{f.relative_to(ROOT)}:{n}: {line.strip()}")
    assert not bad, "\n".join(bad)


def test_US86_windows_package_ships_cli_shim_on_user_path():
    pkg = json.loads((DESK / "package.json").read_text(encoding="utf-8"))
    b = pkg["build"]
    assert {"from": "build-resources/bin", "to": "bin", "filter": ["foxos.cmd"]} in b["win"]["extraResources"]
    assert b["nsis"]["include"] == "build-resources/win/installer.nsh"
    nsh = (DESK / "build-resources/win/installer.nsh").read_text(encoding="utf-8")
    assert "customInstall" in nsh and "customUnInstall" in nsh and "DoNotExpandEnvironmentNames" in nsh and "ExpandString" in nsh
    cmd = (DESK / "build-resources/bin/foxos.cmd").read_bytes()
    assert b"\r\n" in cmd and b'"%~dp0..\\python\\python.exe" -m foxos %*' in cmd
    ps1 = (ROOT / "scripts/install.ps1").read_text(encoding="ascii")
    assert ps1.count("Add-FoxosPath (") == 3 and "DoNotExpandEnvironmentNames" in ps1
