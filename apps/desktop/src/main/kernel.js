'use strict';
// 调用 foxos 命令内核：桌面上的一切文件操作都经由内核（权限、写锁、审计与智能体一致）
const { app } = require('electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { REPO_ROOT, IS_WIN, corePath, which } = require('./paths');
const settings = require('./settings');

let workspace = null;

function setWorkspace(ws) {
  workspace = path.resolve(ws);
  fs.mkdirSync(workspace, { recursive: true });
}
function getWorkspace() { return workspace; }

function pythonPath() {
  if (process.env.FOXOS_PYTHON) return process.env.FOXOS_PYTHON;
  const s = settings.load();
  if (s.python && fs.existsSync(s.python)) return s.python;
  if (!app.isPackaged) {
    const venv = IS_WIN ? path.join(REPO_ROOT, '.venv', 'Scripts', 'python.exe') : path.join(REPO_ROOT, '.venv', 'bin', 'python');
    if (fs.existsSync(venv)) return venv;
  }
  return which(IS_WIN ? 'python' : 'python3') || (IS_WIN ? 'python' : 'python3');
}

function coreEnv(extra = {}) {
  return {
    ...process.env,
    PYTHONPATH: [corePath(), process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
    PYTHONIOENCODING: 'utf-8',
    ...extra,
  };
}

// 在 userData/bin 下生成 foxos 命令（终端与 ACP 智能体都能直接运行 foxos）
function ensureShim() {
  const dir = path.join(app.getPath('userData'), 'bin');
  fs.mkdirSync(dir, { recursive: true });
  const py = pythonPath();
  if (IS_WIN) {
    fs.writeFileSync(path.join(dir, 'foxos.cmd'), `@echo off\r\nset "PYTHONPATH=${corePath()};%PYTHONPATH%"\r\n"${py}" -m foxos %*\r\n`);
  } else {
    const p = path.join(dir, 'foxos');
    fs.writeFileSync(p, `#!/bin/sh\nPYTHONPATH="${corePath()}\${PYTHONPATH:+:$PYTHONPATH}" exec "${py}" -m foxos "$@"\n`);
    fs.chmodSync(p, 0o755);
  }
  return dir;
}

function run(args, { json = true, stdin = null, agent = 'human:desktop', timeoutMs = 180000 } = {}) {
  if (!Array.isArray(args) || args.some((a) => typeof a !== 'string')) {
    return Promise.resolve({ ok: false, exitCode: 2, data: null, stdout: '', stderr: 'args 必须是字符串数组' });
  }
  return new Promise((resolve) => {
    const full = ['-m', 'foxos', '--workspace', workspace, '--agent', agent, ...args, ...(json ? ['--json'] : [])];
    const child = spawn(pythonPath(), full, { env: coreEnv(), windowsHide: true });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ ok: false, exitCode: -1, data: null, stdout: '', stderr: `无法启动 Python（${pythonPath()}）：${err.message}` });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      let data = null;
      if (json) { try { data = stdout.trim() ? JSON.parse(stdout) : null; } catch { data = { raw: stdout }; } }
      resolve({ ok: code === 0, exitCode: code, data, stdout, stderr });
    });
    if (stdin != null) child.stdin.end(Buffer.from(String(stdin), 'utf8'));
    else child.stdin.end();
  });
}

module.exports = { run, setWorkspace, getWorkspace, pythonPath, coreEnv, ensureShim };
