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

// 狐狸OS 电脑（来宾）的 SSH 参数：BatchMode（不问密码），known_hosts 放在 userData，首次连接记下指纹之后严格校验
function sshArgs(s, { tty = false, knownHosts } = {}) {
  const a = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', '-o', 'ServerAliveInterval=20', '-o', `UserKnownHostsFile=${knownHosts}`, '-o', 'StrictHostKeyChecking=accept-new', '-o', 'LogLevel=ERROR'];
  if (s.alias) a.push('-o', `HostKeyAlias=${s.alias}`);
  if (s.port) a.push('-p', String(s.port));
  if (s.key) a.push('-i', s.key, '-o', 'IdentitiesOnly=yes');
  a.push(tty ? '-tt' : '-T', `${s.user || 'foxos'}@${s.host}`);
  return a;
}

// 来宾里执行的命令行（来宾是狐狸OS，sh）：登录 shell 让 PATH 与桌面会话一致，每个参数单独加引号。
// SSH 会话没有 DISPLAY：默认接到狐狸OS 的桌面会话 :0（live-autologin / lightdm），这样“打开 Word”出现在来宾桌面上
const GUEST_SESSION_ENV = '[ -n "${DISPLAY:-}" ] || export DISPLAY=:0; [ -n "${XAUTHORITY:-}" ] || [ ! -f "$HOME/.Xauthority" ] || export XAUTHORITY="$HOME/.Xauthority"; ';
function remoteLine(argv) { return `exec sh -lc ${shQuote(`${GUEST_SESSION_ENV}exec ${argv.map(shQuote).join(' ')}`)}`; }

module.exports = { withPath, foxosCommandLine, mergeUserPath, psQuote, shQuote, sshArgs, remoteLine, GUEST_SESSION_ENV };
