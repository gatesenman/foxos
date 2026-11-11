'use strict';
// ACP 智能体：读取官方 ACP Registry，真实下载安装（npm 包或二进制压缩包 + sha256 校验），列出已安装
const { app, net } = require('electron');
const { spawn } = require('node:child_process');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { IS_WIN, which } = require('./paths');

const REGISTRY_URL = 'https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json';
const SNAPSHOT = path.join(__dirname, 'registry-snapshot.json');

// 智能体装在 FOXOS_HOME/agents（与 Everything 应用、环境同一目录树），环境启动时只读挂载到 /opt/foxos/agents
function agentsDir() {
  const d = path.join(require('./everything').foxosHome(), 'agents');
  fs.mkdirSync(d, { recursive: true });
  return d;
}

function platformKey() {
  const os = { linux: 'linux', darwin: 'darwin', win32: 'windows' }[process.platform];
  const arch = { x64: 'x86_64', arm64: 'aarch64' }[process.arch];
  return `${os}-${arch}`;
}

async function fetchRegistry() {
  const cache = path.join(app.getPath('userData'), 'registry-cache.json');
  try {
    const res = await net.fetch(REGISTRY_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    fs.writeFileSync(cache, JSON.stringify(data));
    return { source: 'online', url: REGISTRY_URL, fetchedAt: new Date().toISOString(), data };
  } catch (e) {
    const file = fs.existsSync(cache) ? cache : SNAPSHOT;
    return { source: file === cache ? 'cache' : 'snapshot', error: String(e.message || e), data: JSON.parse(fs.readFileSync(file, 'utf8')) };
  }
}

function installedInfo(id) {
  const f = path.join(agentsDir(), id, 'foxos-agent.json');
  try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; }
}

// 汇总：注册表条目 + 本机安装状态 + 本平台可用的安装方式
async function list() {
  const reg = await fetchRegistry();
  const pk = platformKey();
  const agents = reg.data.agents.map((a) => {
    const d = a.distribution || {};
    const methods = [];
    if (d.npx) methods.push('npm');
    if (d.binary && d.binary[pk]) methods.push('binary');
    const info = installedInfo(a.id);
    return {
      id: a.id, name: a.name, version: a.version, description: a.description, license: a.license, icon: a.icon,
      repository: a.repository, website: a.website, methods,
      installed: Boolean(info && fs.existsSync(info.command)), installedVersion: info?.version || null,
    };
  });
  return { source: reg.source, error: reg.error || null, platform: pk, npm: Boolean(which('npm')), agents };
}

function registryEntry(reg, id) {
  const a = reg.data.agents.find((x) => x.id === id);
  if (!a) throw new Error(`注册表中没有智能体：${id}`);
  return a;
}

function runLogged(cmd, args, opts, log) {
  return new Promise((resolve, reject) => {
    log(`$ ${[cmd, ...args].join(' ')}\n`);
    const child = spawn(cmd, args, { ...opts, windowsHide: true, shell: IS_WIN && /\.(cmd|bat)$/i.test(cmd) });
    child.stdout.on('data', (d) => log(String(d)));
    child.stderr.on('data', (d) => log(String(d)));
    child.on('error', reject);
    child.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`${path.basename(cmd)} 退出码 ${code}`))));
  });
}

async function download(url, dest, log, progress) {
  const res = await net.fetch(url);
  if (!res.ok) throw new Error(`下载失败 HTTP ${res.status}：${url}`);
  const total = Number(res.headers.get('content-length')) || 0;
  const out = fs.createWriteStream(dest);
  const hash = crypto.createHash('sha256');
  let got = 0;
  const reader = res.body.getReader();
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    got += value.length;
    hash.update(value);
    out.write(Buffer.from(value));
    progress(total ? got / total : null, got, total);
  }
  await new Promise((r) => out.end(r));
  log(`已下载 ${(got / 1048576).toFixed(1)} MB\n`);
  return hash.digest('hex');
}

function npmBin(dir, pkgSpec) {
  const name = pkgSpec.replace(/@[^@/]+$/, '');
  const pj = JSON.parse(fs.readFileSync(path.join(dir, 'node_modules', name, 'package.json'), 'utf8'));
  const bin = typeof pj.bin === 'string' ? pj.bin : Object.values(pj.bin || {})[0];
  if (!bin) throw new Error(`${name} 没有可执行入口`);
  return { script: path.join(dir, 'node_modules', name, bin), version: pj.version };
}

// 真实安装：npm install --prefix 或下载二进制压缩包并校验 sha256
async function install(id, { log = () => {}, progress = () => {} } = {}) {
  const reg = await fetchRegistry();
  const a = registryEntry(reg, id);
  const dir = path.join(agentsDir(), id);
  fs.mkdirSync(dir, { recursive: true });
  const d = a.distribution || {};
  let info;
  if (d.npx) {
    const npm = which('npm');
    if (!npm) throw new Error('需要 npm：请先在安装向导中安装 Node.js');
    progress(null);
    await runLogged(npm, ['install', '--prefix', dir, '--no-fund', '--no-audit', '--loglevel', 'http', d.npx.package], { cwd: dir, env: process.env }, log);
    const { script, version } = npmBin(dir, d.npx.package);
    const node = which('node');
    info = { id, name: a.name, version, method: 'npm', package: d.npx.package,
      command: node || process.execPath, args: [script, ...(d.npx.args || [])],
      env: { ...(d.npx.env || {}), ...(node ? {} : { ELECTRON_RUN_AS_NODE: '1' }) } };
  } else if (d.binary && d.binary[platformKey()]) {
    const b = d.binary[platformKey()];
    const archive = path.join(dir, path.basename(new URL(b.archive).pathname));
    log(`下载 ${b.archive}\n`);
    const sha = await download(b.archive, archive, log, progress);
    if (b.sha256 && sha !== b.sha256.toLowerCase()) throw new Error(`sha256 校验失败：期望 ${b.sha256}，实际 ${sha}`);
    log(`sha256 校验通过：${sha}\n`);
    const unpack = path.join(dir, 'bin');
    fs.rmSync(unpack, { recursive: true, force: true });
    fs.mkdirSync(unpack, { recursive: true });
    if (/\.zip$/i.test(archive)) {
      if (IS_WIN) await runLogged('powershell.exe', ['-NoProfile', '-Command', `Expand-Archive -Force '${archive}' '${unpack}'`], {}, log);
      else await runLogged(which('unzip') || 'unzip', ['-o', archive, '-d', unpack], {}, log);
    } else {
      await runLogged(which('tar') || 'tar', ['-xf', archive, '-C', unpack], {}, log);
    }
    fs.rmSync(archive, { force: true });
    const cmd = path.resolve(unpack, b.cmd);
    if (!IS_WIN) fs.chmodSync(cmd, 0o755);
    info = { id, name: a.name, version: a.version, method: 'binary', command: cmd, args: b.args || [], env: b.env || {} };
  } else {
    throw new Error(`${a.name} 没有适用于 ${platformKey()} 的安装方式`);
  }
  fs.writeFileSync(path.join(dir, 'foxos-agent.json'), JSON.stringify({ ...info, installedAt: new Date().toISOString() }, null, 2));
  log(`安装完成：${a.name} ${info.version}\n`);
  return info;
}

function uninstall(id) {
  fs.rmSync(path.join(agentsDir(), id), { recursive: true, force: true });
  return true;
}

function installed() {
  return fs.readdirSync(agentsDir()).map(installedInfo).filter((i) => i && fs.existsSync(i.command));
}

module.exports = { list, install, uninstall, installed, installedInfo, fetchRegistry, platformKey, agentsDir };
