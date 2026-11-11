'use strict';
// 客户端模式下各功能的“在狐狸OS 电脑里执行”实现。index.js 在 kernel.executionMode() === 'client' 时调用这里，
// 本机（Windows / macOS / 普通 Linux）只负责显示与转发：不在本机装软件、不开本机 LibreOffice、不跑本机终端。
const crypto = require('node:crypto');
const net = require('node:net');
const path = require('node:path');
const { spawn } = require('node:child_process');
const guest = require('./guest');
const { t } = require('./i18n');

const OFFICE_FLAGS = { writer: '--writer', calc: '--calc', impress: '--impress' };

function failed(r, what) {
  const msg = r.data?.error?.message || (r.stderr || '').trim() || `${what}: exit ${r.exitCode}`;
  return Object.assign(new Error(msg), { code: r.data?.error?.code || 'GUEST_ERROR' });
}

let wsCache = null;
async function guestWorkspace() {
  if (wsCache && wsCache.key === JSON.stringify(guest.config())) return wsCache.path;
  const r = await guest.resolve();
  const p = await guest.exec(r, ['sh', '-c', 'printf %s "${FOXOS_WORKSPACE:-$HOME/FoxOS/workspace}"'], { timeoutMs: 30000 });
  if (p.code !== 0 || !p.stdout.startsWith('/')) throw new Error(p.stderr.trim() || 'guest workspace');
  wsCache = { key: JSON.stringify(guest.config()), path: p.stdout };
  return p.stdout;
}

// “打开 Word”= 在狐狸OS 电脑的桌面上打开 LibreOffice Writer（文件是来宾工作空间里的相对路径）
let nextLaunch = 1;
async function officeLaunch(appId, relFile) {
  const flag = OFFICE_FLAGS[appId];
  if (!flag) throw new Error(`unknown app ${appId}`);
  const argv = ['libreoffice', flag];
  if (relFile) {
    const rel = path.posix.normalize(String(relFile).replace(/\\/g, '/'));
    if (rel.startsWith('../') || rel === '..' || rel.startsWith('/')) throw new Error('only files inside the workspace');
    argv.push(path.posix.join(await guestWorkspace(), rel));
  }
  const r = await guest.kernelRun(['desktop', 'launch', '--', ...argv]);
  if (!r.ok) throw failed(r, 'desktop launch');
  return { id: nextLaunch++, app: appId, file: relFile || null, startedAt: Date.now(), exited: null, guest: r.guest || true, pid: r.data?.result?.pid ?? null };
}

// 应用中心的检测结果来自来宾
async function detect(builtinFrom) {
  const r = await guest.resolve();
  const probe = 'for c in soffice libreoffice git node npm python3 wmctrl; do p=$(command -v $c 2>/dev/null) && printf "%s\\t%s\\n" "$c" "$p"; done; soffice --version 2>/dev/null | head -n1 | sed "s/^/ver\\t/"';
  const p = await guest.exec(r, ['sh', '-c', probe], { timeoutMs: 60000 });
  if (p.code === 255) throw new Error(p.stderr.trim() || 'ssh');
  const have = Object.fromEntries(p.stdout.split('\n').filter(Boolean).map((l) => l.split('\t')));
  const soffice = have.soffice || have.libreoffice || null;
  const office = (id, name, flag, exts) => ({ id, name, kind: 'native', installed: Boolean(soffice), version: have.ver || null, path: soffice, flag, exts, guest: true,
    hint: soffice ? null : t('client.libreoffice_missing') });
  const tool = (id, name) => ({ id, name, installed: Boolean(have[id]), path: have[id] || null, version: null, guest: true });
  return {
    guest: r.label,
    builtin: builtinFrom,
    office: [
      office('writer', 'LibreOffice Writer', '--writer', ['.docx', '.doc', '.odt', '.rtf', '.txt']),
      office('calc', 'LibreOffice Calc', '--calc', ['.xlsx', '.xls', '.ods', '.csv']),
      office('impress', 'LibreOffice Impress', '--impress', ['.pptx', '.ppt', '.odp']),
    ],
    tools: [tool('python3', 'Python'), tool('git', 'git'), tool('node', 'Node.js'), tool('npm', 'npm'), tool('wmctrl', 'wmctrl')],
  };
}

// ACP 智能体：注册表、安装、列表都在来宾里
async function agentsList() {
  const r = await guest.kernelRun(['acp', 'agent', 'list', '--available'], { timeoutMs: 120000 });
  if (!r.ok) throw failed(r, 'acp agent list');
  const res = r.data.result;
  return { source: res.source, error: res.error || null, platform: res.platform, npm: true, guest: r.guest, agents: res.agents.map((a) => ({
    id: a.id, name: a.name, version: a.version, description: a.description, license: a.license, icon: a.icon, repository: a.repository, website: a.website,
    methods: (a.methods || []).map((m) => (m === 'npx' ? 'npm' : m)), installed: Boolean(a.installed), installedVersion: a.installed_version || null })) };
}

async function agentsInstalled() {
  const r = await guest.kernelRun(['acp', 'agent', 'list'], { timeoutMs: 60000 });
  if (!r.ok) throw failed(r, 'acp agent list');
  return r.data.result.agents.map((a) => ({ id: a.id, name: a.name, version: a.version, method: a.method, remote: true, command: 'foxos', args: ['acp', 'stdio', a.id] }));
}

async function agentsInstall(id, { log = () => {} } = {}) {
  log(`$ foxos acp agent install ${id}  (FoxOS computer)\n`);
  const r = await guest.kernelRun(['acp', 'agent', 'install', id], { timeoutMs: 30 * 60 * 1000 });
  if (r.stderr) log(r.stderr);
  if (!r.ok) throw failed(r, 'acp agent install');
  log(`${r.data?.result?.message || 'ok'}\n`);
  return r.data.result;
}

async function agentsUninstall(id) {
  const r = await guest.kernelRun(['acp', 'agent', 'uninstall', id]);
  if (!r.ok) throw failed(r, 'acp agent uninstall');
  return true;
}

async function agentInfo(id) {
  const all = await agentsInstalled();
  return all.find((a) => a.id === id) || null;
}

// 智能体聊天：foxos bot serve 跑在来宾里，经同一条 SSH 连接做本地端口转发
let botChild = null;
let botPending = null;
function freePort() {
  return new Promise((resolve, reject) => { const s = net.createServer(); s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => resolve(port)); }); s.on('error', reject); });
}
function botsEnsure() {
  if (botChild && botChild.exitCode === null && botChild.url) return Promise.resolve({ url: botChild.url, guest: true });
  if (botPending) return botPending;
  botPending = (async () => {
    const r = await guest.resolve();
    if (!r || !r.ssh) throw new Error('NO_SSH');
    const local = await freePort();
    const remote = 20000 + crypto.randomInt(30000);
    const token = crypto.randomBytes(24).toString('base64url');
    const args = guest.sshArgs(r.ssh);
    args.splice(args.length - 1, 0, '-o', 'ExitOnForwardFailure=yes', '-L', `127.0.0.1:${local}:127.0.0.1:${remote}`);
    args.push(guest.remoteLine(['env', `FOXOS_BOTS_TOKEN=${token}`, 'foxos', 'bot', 'serve', '--listen', `127.0.0.1:${remote}`]));
    const c = spawn(guest.sshBin(), args, { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
    return new Promise((resolve, reject) => {
      let out = ''; let err = '';
      const tm = setTimeout(() => { c.kill(); reject(new Error(`bot serve did not start in the FoxOS computer ${err}`)); }, 60000);
      c.stderr.on('data', (d) => { err = (err + d).slice(-2000); });
      c.stdout.on('data', (d) => {
        out += d;
        if (!out.includes('\n')) return;
        clearTimeout(tm);
        c.url = `http://127.0.0.1:${local}/?t=${token}`;
        botChild = c;
        resolve({ url: c.url, guest: r.label });
      });
      c.on('exit', (code) => { clearTimeout(tm); if (!c.url) reject(new Error(err.trim() || `ssh exited ${code}`)); });
    });
  })().finally(() => { botPending = null; });
  return botPending;
}
function botsStop() { if (botChild && botChild.exitCode === null) botChild.kill(); botChild = null; }

// Everything 应用：目录元数据用本机自带的，安装状态以狐狸OS 电脑为准；打开时在来宾桌面上打开（foxos <app> open）
async function evList(hostList) {
  const r = await guest.kernelRun(['everything', 'list', '--installed'], { timeoutMs: 60000 });
  if (!r.ok) throw failed(r, 'everything list');
  const ids = new Set((r.data.result.apps || []).map((a) => a.id));
  return { ...hostList, guest: r.guest, apps: hostList.apps.map((a) => ({ ...a, installed: ids.has(a.id), guest: true })) };
}

async function evOpen(appId, relFile) {
  const r = await guest.kernelRun([appId, 'open', ...(relFile ? [relFile] : [])], { timeoutMs: 120000 });
  if (!r.ok) throw failed(r, `${appId} open`);
  return r.data.result;
}

module.exports = { evList, evOpen, officeLaunch, detect, agentsList, agentsInstalled, agentsInstall, agentsUninstall, agentInfo, botsEnsure, botsStop, guestWorkspace, OFFICE_FLAGS };
