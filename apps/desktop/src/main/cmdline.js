'use strict';
// 纯函数（不依赖 Electron，单元测试与 wine 下的回归测试直接 require）：
//   withPath     给子进程的环境变量前置 PATH 目录。Windows 的环境变量名不区分大小写，真机上通常叫 "Path"；
//                `{ ...process.env, PATH: … }` 会得到 "Path" 和 "PATH" 两个键，子进程（PowerShell）读到的是没改过的 "Path"，
//                于是终端里找不到 foxos（0.2.0 / 0.3.2 应用中心“安装”报 CommandNotFoundException 的根因）。
//   foxosCommandLine  在终端里运行 foxos 时用绝对路径调用（不依赖 PATH），按 shell 正确加引号并带回退出码。
const path = require('node:path');

function pathKeys(env) { return Object.keys(env).filter((k) => k.toUpperCase() === 'PATH'); }

function withPath(env, dirs, isWin = process.platform === 'win32') {
  const out = { ...env };
  const keys = isWin ? pathKeys(out) : (Object.hasOwn(out, 'PATH') ? ['PATH'] : []);
  const name = keys[0] || 'PATH';
  const delim = isWin ? ';' : ':';
  const current = keys.map((k) => out[k]).find((v) => v) || '';
  for (const k of keys) delete out[k];
  out[name] = [...dirs.filter(Boolean), current].filter(Boolean).join(delim);
  return out;
}

const psQuote = (s) => `'${String(s).replace(/'/g, "''")}'`;
const shQuote = (s) => `'${String(s).replace(/'/g, "'\\''")}'`;

// shell：'powershell'（Windows 终端）或 'posix'
function foxosCommandLine(cli, args, shell) {
  const abs = shell === 'powershell' ? path.win32.isAbsolute(cli || '') : path.posix.isAbsolute(cli || '');
  if (!cli || !abs) throw new Error(`foxos 命令行必须是绝对路径：${cli}`);
  if (!Array.isArray(args) || args.some((a) => typeof a !== 'string')) throw new Error('args 必须是字符串数组');
  if (shell === 'powershell') return `& ${[cli, ...args].map(psQuote).join(' ')}; exit $LASTEXITCODE`;
  return [cli, ...args].map(shQuote).join(' ');
}

// 用户 PATH（HKCU\Environment\Path）里放上 resources\bin：放到最前，去掉重复项和已经不存在的旧 FoxOS 目录（便携版换了位置）
function mergeUserPath(current, bin, exists = () => true) {
  const norm = (d) => d.replace(/[\\/]+$/, '').toLowerCase();
  const b = bin.replace(/[\\/]+$/, '');
  const rest = String(current || '').split(';').filter((d) => d && norm(d) !== norm(b) && !(/\\resources\\bin$/i.test(d.replace(/[\\/]+$/, '')) && !exists(d)));
  return [b, ...rest].join(';');
}

module.exports = { withPath, foxosCommandLine, mergeUserPath, psQuote, shQuote };
