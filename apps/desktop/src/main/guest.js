'use strict';
// 狐狸OS 电脑（来宾）：桌面客户端把命令、终端、智能体和画面都接到这里。
//   settings.guest = { kind: 'env', env: 'foxos' }                         本机上的狐狸OS 虚拟机（foxos env install 建的：QEMU / Hyper-V / WSL2…）
//                  | { kind: 'ssh', host, port, user, key, label }          远程狐狸OS（SSH 密钥登录）
//                  | { kind: 'machine', machine, ssh?: {…} }                 配对过的狐狸OS（foxos machine pair，HTTPS 控制通道；终端仍用 SSH）
// 命令通道：SSH 上运行来宾里的 foxos（或 machine 配对的 HTTPS 通道）；画面：虚拟机控制台的 RFB（QEMU -vnc，只听 127.0.0.1），
// 没有控制台时经 SSH 在来宾里按需起 x11vnc（只听来宾的 127.0.0.1），用 ssh -W 转发。
const { app } = require('electron');
const { spawn, execFile } = require('node:child_process');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const { IS_WIN, which, corePath } = require('./paths');
const settings = require('./settings');
const cmd = require('./cmdline');
const { shQuote } = cmd;

const GUEST_VNC_PORT = 5907;

function config() { return settings.load().guest || null; }
function setConfig(g) { const s = settings.load(); s.guest = g || null; settings.save(s); return s.guest; }

function sshBin() {
  if (process.env.FOXOS_SSH) return process.env.FOXOS_SSH;
  return which('ssh') || (IS_WIN ? path.join(process.env.SystemRoot || 'C:\\Windows', 'System32', 'OpenSSH', 'ssh.exe') : 'ssh');
}

function knownHosts() {
  const d = path.join(app.getPath('userData'), 'ssh');
  fs.mkdirSync(d, { recursive: true });
  return path.join(d, 'known_hosts');
}

// 本机 kernel（只用于虚拟机生命周期查询）延迟加载，避免循环依赖
const localKernel = () => require('./kernel');

// 把配置解析成可用的连接参数：{ label, ssh, machine, console }
async function resolve(g = config()) {
  if (!g) return null;
  if (g.kind === 'env') {
    const r = await localKernel().runLocal(['env', 'info', g.env]);
    if (!r.ok) throw new Error(r.data?.error?.message || `env info ${g.env}: ${r.stderr || r.exitCode}`);
    const e = r.data.result || r.data;
    const disp = e.console || null;
    const s = e.ssh && e.ssh.port ? { host: '127.0.0.1', port: e.ssh.port, user: e.ssh.user || 'foxos', key: e.ssh.key || null, alias: `foxos-env-${g.env}` } : null;
    return { kind: 'env', label: g.env, state: e.state, provider: e.provider, ssh: s, machine: null, console: disp && disp.port ? { host: disp.host || '127.0.0.1', port: disp.port } : null };
  }
  if (g.kind === 'ssh') return { kind: 'ssh', label: g.label || `${g.user || 'foxos'}@${g.host}`, state: 'remote', ssh: { host: g.host, port: g.port || 22, user: g.user || 'foxos', key: g.key || null }, machine: null, console: null };
  if (g.kind === 'machine') return { kind: 'machine', label: g.machine, state: 'remote', ssh: g.ssh || null, machine: g.machine, console: null };
  throw new Error(`unknown guest kind ${g.kind}`);
}

function sshArgs(s, opts = {}) { return cmd.sshArgs(s, { ...opts, knownHosts: knownHosts() }); }
const remoteLine = cmd.remoteLine;

function needSsh(r) {
  if (!r) throw Object.assign(new Error('NO_GUEST'), { code: 'NO_GUEST' });
  if (!r.ssh) throw Object.assign(new Error(`${r.label}: no SSH endpoint (start the VM, or run foxos env expose NAME --ssh on)`), { code: 'NO_SSH' });
  return r.ssh;
}

function exec(r, argv, { input = null, timeoutMs = 180000 } = {}) {
  const s = needSsh(r);
  return new Promise((done) => {
    const child = execFile(sshBin(), [...sshArgs(s), remoteLine(argv)], { windowsHide: true, timeout: timeoutMs, maxBuffer: 64 * 1024 * 1024, encoding: 'utf8' },
      (err, stdout, stderr) => done({ code: err ? (typeof err.code === 'number' ? err.code : -1) : 0, stdout: String(stdout || ''), stderr: String(stderr || (err && !err.code ? err.message : '')) }));
    if (input != null) child.stdin.end(Buffer.from(String(input), 'utf8')); else child.stdin.end();
  });
}

// 在来宾里运行 foxos 内核命令，返回与 kernel.run 一样的结构
async function kernelRun(args, { json = true, stdin = null, agent = 'human:desktop', timeoutMs = 180000 } = {}) {
  let r;
  try { r = await resolve(); } catch (e) { return { ok: false, exitCode: -1, data: { ok: false, error: { code: 'GUEST_UNAVAILABLE', message: e.message } }, stdout: '', stderr: e.message }; }
  if (!r) return { ok: false, exitCode: -1, data: { ok: false, error: { code: 'NO_GUEST', message: 'NO_GUEST' } }, stdout: '', stderr: 'NO_GUEST' };
  if (r.machine && !r.ssh) return localKernel().runLocal(['--machine', r.machine, ...args], { json, stdin, agent, timeoutMs });
  let p;
  try { p = await exec(r, ['foxos', '--agent', agent, ...args, ...(json ? ['--json'] : [])], { input: stdin, timeoutMs }); } catch (e) {
    return { ok: false, exitCode: -1, data: { ok: false, error: { code: e.code || 'GUEST_UNAVAILABLE', message: e.message } }, stdout: '', stderr: e.message };
  }
  let data = null;
  if (json) { try { data = p.stdout.trim() ? JSON.parse(p.stdout) : null; } catch { data = { raw: p.stdout }; } }
  if (p.code === 255 && !data) data = { ok: false, error: { code: 'GUEST_UNAVAILABLE', message: p.stderr.trim() || 'ssh failed' } };
  return { ok: p.code === 0, exitCode: p.code, data, stdout: p.stdout, stderr: p.stderr, guest: r.label };
}

// 终端：打开来宾里的登录 shell，或在来宾里运行 argv（应用中心安装等，用户能看到进度）
async function terminalSpec(argv = null) {
  const s = needSsh(await resolve());
  const args = sshArgs(s, { tty: true });
  if (argv) args.push(remoteLine(argv));
  return { command: sshBin(), args };
}

// ACP 智能体跑在来宾里：stdio 经 SSH（不分配终端，二进制干净）
async function spawnStdio(argv, { env = {} } = {}) {
  const s = needSsh(await resolve());
  const sets = Object.entries(env).map(([k, v]) => `${k}=${shQuote(v)}`).join(' ');
  const line = `exec sh -lc ${shQuote(`${cmd.GUEST_SESSION_ENV}cd "$HOME" 2>/dev/null; ${sets ? `export ${sets}; ` : ''}exec ${argv.map(shQuote).join(' ')}`)}`;
  return spawn(sshBin(), [...sshArgs(s), line], { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
}

// 画面：返回一个 { write, end, on('data'|'close') } 的字节流（RFB 协议），由渲染进程的 noVNC 使用
async function rfbStream() {
  const r = await resolve();
  if (!r) throw Object.assign(new Error('NO_GUEST'), { code: 'NO_GUEST' });
  if (r.console) {
    const sock = net.connect(r.console.port, r.console.host);
    return { via: 'console', stream: sock, write: (b) => sock.write(b), end: () => sock.destroy(), on: (ev, f) => sock.on(ev === 'close' ? 'close' : ev, f) };
  }
  const s = needSsh(r);
  // 来宾里按需起 x11vnc：只听来宾的 127.0.0.1，-shared 允许多个查看端，桌面会话的 Xauthority 由 -auth guess 找
  // -auth guess 需要 xauth（狐狸OS 没装）：有 xauth 才猜，否则用会话的 XAUTHORITY，都没有就不带 -auth（Xvfb / 无认证会话）
  const script = `pgrep -u "$(id -u)" -a -x x11vnc | grep -q -e "-rfbport ${GUEST_VNC_PORT}" && exit 0
A=""; if command -v xauth >/dev/null 2>&1; then A="-auth guess"; elif [ -n "\${XAUTHORITY:-}" ] && [ -f "\$XAUTHORITY" ]; then A="-auth \$XAUTHORITY"; fi
x11vnc -display "\${DISPLAY:-:0}" \$A -localhost -rfbport ${GUEST_VNC_PORT} -forever -shared -nopw -bg -o /tmp/foxos-client-vnc.log >/dev/null 2>&1 || { tail -n 5 /tmp/foxos-client-vnc.log >&2; exit 1; }
sleep 0.5`;
  const start = await exec(r, ['sh', '-c', script], { timeoutMs: 30000 });
  if (start.code !== 0) throw new Error(`x11vnc: ${start.stderr || start.code}`);
  const p = spawn(sshBin(), [...sshArgs(s).filter((a) => a !== '-T'), '-W', `127.0.0.1:${GUEST_VNC_PORT}`], { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  // -W 不能和 -T 之后的目标顺序冲突：sshArgs 把目标放在最后，这里去掉 -T 后目标仍在最后
  return { via: 'ssh', stream: p, write: (b) => p.stdin.write(b), end: () => p.kill(), on: (ev, f) => (ev === 'data' ? p.stdout.on('data', f) : p.on(ev === 'close' ? 'exit' : ev, f)) };
}

async function status() {
  const g = config();
  if (!g) return { configured: false };
  try {
    const r = await resolve(g);
    let reach = null;
    if (r.ssh || r.machine) {
      // 轻量探测：来宾里 foxos --version（不要用 help --json，它有几 MB）
      const v = r.ssh ? await exec(r, ['foxos', '--version'], { timeoutMs: 60000 }).then((p) => ({ ok: p.code === 0, version: p.stdout.trim().split(/\s+/).pop(), stderr: p.stderr, code: p.code }))
        : await kernelRun(['machine', 'ping', r.machine], { timeoutMs: 60000 }).then((k) => ({ ok: k.ok, version: k.data?.result?.version || null, stderr: k.data?.error?.message || k.stderr }));
      reach = v.ok ? { ok: true, version: v.version || null } : { ok: false, error: (v.stderr || '').trim() || `exit ${v.code}` };
    }
    return { configured: true, config: g, label: r.label, kind: r.kind, state: r.state, provider: r.provider, ssh: r.ssh ? { host: r.ssh.host, port: r.ssh.port, user: r.ssh.user } : null, console: r.console, reach };
  } catch (e) {
    return { configured: true, config: g, error: e.message };
  }
}

module.exports = { config, setConfig, resolve, sshArgs, remoteLine, exec, kernelRun, terminalSpec, spawnStdio, rfbStream, status, sshBin, GUEST_VNC_PORT, corePath };
