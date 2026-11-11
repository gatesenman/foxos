'use strict';
const { t } = require('./i18n');
// 调用 foxos 命令内核：桌面上的一切文件操作都经由内核（权限、写锁、审计与智能体一致）
const { app } = require('electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { REPO_ROOT, IS_WIN, corePath, which } = require('./paths');
const settings = require('./settings');
const { foxosCommandLine } = require('./cmdline');
const policy = require('./policy');

let workspace = null;

function setWorkspace(ws) {
  workspace = path.resolve(ws);
  fs.mkdirSync(workspace, { recursive: true });
}
function getWorkspace() { return workspace; }

// 安装包自带的 Python（resources/python）：Windows 是 embeddable 版（内核通过 ._pth 加入搜索路径），
// Linux / macOS 是 python-build-standalone（内核通过 PYTHONPATH）；都已带好办公库
function bundledPython() {
  if (!app.isPackaged) return null;
  const p = IS_WIN ? path.join(process.resourcesPath, 'python', 'python.exe') : path.join(process.resourcesPath, 'python', 'bin', 'python3');
  return fs.existsSync(p) ? p : null;
}

// 解释器与来源（设置页显示）：env（FOXOS_PYTHON）· settings（设置页填写且存在）· bundled（安装包自带）· venv（开发）· system（PATH 上）· missing
function pythonInfo() {
  if (process.env.FOXOS_PYTHON) return { path: process.env.FOXOS_PYTHON, source: 'env', exists: fs.existsSync(process.env.FOXOS_PYTHON) };
  const s = settings.load();
  if (s.python && fs.existsSync(s.python)) return { path: s.python, source: 'settings', exists: true };
  const b = bundledPython();
  if (b) return { path: b, source: 'bundled', exists: true, ignoredSetting: s.python || null };
  if (!app.isPackaged) {
    const venv = IS_WIN ? path.join(REPO_ROOT, '.venv', 'Scripts', 'python.exe') : path.join(REPO_ROOT, '.venv', 'bin', 'python');
    if (fs.existsSync(venv)) return { path: venv, source: 'venv', exists: true };
  }
  const sys = which(IS_WIN ? 'python' : 'python3');
  return sys ? { path: sys, source: 'system', exists: true, ignoredSetting: s.python || null } : { path: IS_WIN ? 'python' : 'python3', source: 'missing', exists: false, ignoredSetting: s.python || null };
}
function pythonPath() { return pythonInfo().path; }

function coreEnv(extra = {}) {
  return {
    ...process.env,
    PYTHONPATH: [corePath(), process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1',
    // 核心的宿主保护和桌面的执行模式保持一致：客户端模式 = 宿主（智能体只在狐狸OS 虚拟电脑里动手），native = 狐狸OS
    ...(process.env.FOXOS_PLACE ? {} : { FOXOS_PLACE: executionMode() === 'client' ? 'host' : 'foxos' }),
    ...extra,
  };
}

// 在 userData/bin 下生成 foxos 命令（终端与 ACP 智能体都能直接运行 foxos）
function ensureShim() {
  const dir = path.join(app.getPath('userData'), 'bin');
  fs.mkdirSync(dir, { recursive: true });
  const py = pythonPath();
  if (IS_WIN) {
    fs.writeFileSync(path.join(dir, 'foxos.cmd'), `@echo off\r\nset "PYTHONPATH=${corePath()};%PYTHONPATH%"\r\nset PYTHONUTF8=1\r\n"${py}" -m foxos %*\r\n`);
  } else {
    const p = path.join(dir, 'foxos');
    fs.writeFileSync(p, `#!/bin/sh\nPYTHONPATH="${corePath()}\${PYTHONPATH:+:$PYTHONPATH}" exec "${py}" -m foxos "$@"\n`);
    fs.chmodSync(p, 0o755);
  }
  return dir;
}

// foxos 命令行的绝对路径（userData/bin 下的 shim，按当前解释器生成）：桌面从不依赖 PATH 上有没有 foxos
function cliPath() { return path.join(ensureShim(), IS_WIN ? 'foxos.cmd' : 'foxos'); }
// 在桌面终端里运行 foxos 的命令行（Windows 是 PowerShell，其余是 sh）
function cliCommandLine(args) { return foxosCommandLine(cliPath(), args, IS_WIN ? 'powershell' : 'posix'); }

// 客户端模式（policy.mode() === 'client'）：除了虚拟机生命周期与配对（env / machine），所有 foxos 命令都在狐狸OS 电脑里执行
function run(args, opts = {}) {
  if (Array.isArray(args) && executionMode() === 'client' && policy.routeKernel(args) === 'guest') return require('./guest').kernelRun(args, opts);
  return runLocal(args, opts);
}

let cachedMode = null;
function executionMode() { if (!cachedMode) cachedMode = policy.mode({ packaged: app.isPackaged }); return cachedMode; }

function runLocal(args, { json = true, stdin = null, agent = 'human:desktop', timeoutMs = 180000 } = {}) {
  if (!Array.isArray(args) || args.some((a) => typeof a !== 'string')) {
    return Promise.resolve({ ok: false, exitCode: 2, data: null, stdout: '', stderr: t('kernel.args_must_be_an_array_of_strings') });
  }
  return new Promise((resolve) => {
    const full = ['-m', 'foxos', '--workspace', workspace, '--agent', agent, ...(json ? ['--json'] : []), ...args];
    const child = spawn(pythonPath(), full, { env: coreEnv(), windowsHide: true });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ ok: false, exitCode: -1, data: null, stdout: '', stderr: t('kernel.cannot_start_python', pythonPath(), err.message) });
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

module.exports = { run, runLocal, executionMode, setWorkspace, getWorkspace, pythonPath, pythonInfo, bundledPython, coreEnv, ensureShim, cliPath, cliCommandLine };
