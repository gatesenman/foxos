'use strict';
// 真实终端：node-pty 启动宿主系统的 shell，工作目录为工作空间
const pty = require('@lydell/node-pty');
const path = require('node:path');
const { IS_WIN, which } = require('./paths');
const kernel = require('./kernel');

const sessions = new Map();
let nextId = 1;

function defaultShell() {
  if (IS_WIN) return which('pwsh') || which('powershell') || 'powershell.exe';
  return process.env.SHELL && which(process.env.SHELL) ? process.env.SHELL : (which('bash') || which('zsh') || '/bin/sh');
}

function spawnPty(webContents, { cols = 100, rows = 30, command = null, args = [], title = null } = {}) {
  const id = nextId++;
  const shim = kernel.ensureShim();
  const env = {
    ...process.env,
    FOXOS_WORKSPACE: kernel.getWorkspace(),
    FOXOS_AGENT: 'human:terminal',
    TERM: 'xterm-256color',
    COLORTERM: 'truecolor',
    PATH: [shim, process.env.PATH].join(path.delimiter),
  };
  const file = command || defaultShell();
  const p = pty.spawn(file, command ? args : [], { name: 'xterm-256color', cols, rows, cwd: kernel.getWorkspace(), env });
  sessions.set(id, p);
  p.onData((d) => { if (!webContents.isDestroyed()) webContents.send('pty:data', id, d); });
  p.onExit(({ exitCode }) => {
    sessions.delete(id);
    if (!webContents.isDestroyed()) webContents.send('pty:exit', id, exitCode);
  });
  return { id, pid: p.pid, shell: file, title: title || path.basename(file) };
}

module.exports = {
  spawnPty,
  write: (id, data) => sessions.get(id)?.write(data),
  resize: (id, cols, rows) => { try { sessions.get(id)?.resize(cols, rows); } catch { /* 已退出 */ } },
  kill: (id) => { try { sessions.get(id)?.kill(); } catch { /* 已退出 */ } sessions.delete(id); },
  killAll: () => { for (const id of [...sessions.keys()]) module.exports.kill(id); },
  defaultShell,
};
