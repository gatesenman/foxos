'use strict';
// Windows：把安装目录里的 resources\bin（foxos.cmd）放到当前用户的 PATH 上（NSIS 安装程序装时已经加过；
// 便携 zip 和 MSI 没有安装脚本，所以桌面启动时补上）。只改 HKCU\Environment，不需要管理员；FOXOS_NO_PATH=1 可关闭。
const { execFile } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { mergeUserPath } = require('./cmdline');

function run(file, args, env) {
  return new Promise((resolve) => execFile(file, args, { windowsHide: true, env: env || process.env, timeout: 20000 }, (err, stdout) => resolve(err ? null : String(stdout))));
}

async function readUserPath() {
  const out = await run('reg.exe', ['query', 'HKCU\\Environment', '/v', 'Path']);
  if (out == null) return { value: '', type: 'REG_EXPAND_SZ' };
  const m = out.match(/^\s*Path\s+(REG_\w+)\s+(.*)$/im);
  return m ? { value: m[2].trim(), type: m[1] } : { value: '', type: 'REG_EXPAND_SZ' };
}

async function ensureUserPath(resourcesPath) {
  if (process.platform !== 'win32' || process.env.FOXOS_NO_PATH === '1') return { changed: false, reason: 'skipped' };
  const bin = path.join(resourcesPath, 'bin');
  if (!fs.existsSync(path.join(bin, 'foxos.cmd'))) return { changed: false, reason: 'no-shim' };
  const cur = await readUserPath();
  const next = mergeUserPath(cur.value, bin, (d) => fs.existsSync(d));
  if (next === cur.value) return { changed: false, reason: 'present', bin };
  // reg.exe 写原值并保留类型（REG_EXPAND_SZ：%USERPROFILE% 之类的条目不被展开）；再用 .NET 设置 FOXOS_BIN 广播 WM_SETTINGCHANGE
  const w = await run('reg.exe', ['add', 'HKCU\\Environment', '/v', 'Path', '/t', cur.type === 'REG_SZ' ? 'REG_SZ' : 'REG_EXPAND_SZ', '/d', next, '/f']);
  if (w == null) return { changed: false, reason: 'write-failed', bin };
  await run('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', "[Environment]::SetEnvironmentVariable('FOXOS_BIN', $env:FOXOS_BIN_DIR, 'User')"], { ...process.env, FOXOS_BIN_DIR: bin });
  return { changed: true, bin };
}

module.exports = { ensureUserPath, readUserPath };
