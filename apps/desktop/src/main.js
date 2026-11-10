// 狐狸OS 桌面外壳（Electron 主进程）
// 所有业务操作都通过 `python -m foxos ... --json` 调用统一命令内核，桌面本身不直接改文件。
'use strict';

const { app, BrowserWindow, ipcMain, nativeImage } = require('electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const REPO_ROOT = path.resolve(__dirname, '..', '..', '..');
const ICON = app.isPackaged
  ? path.join(process.resourcesPath, 'icon.png')
  : path.join(REPO_ROOT, 'assets', 'icon.png');

function argValue(name) {
  const hit = process.argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : null;
}

const WORKSPACE = path.resolve(
  argValue('workspace') || process.env.FOXOS_WORKSPACE || path.join(os.homedir(), 'FoxOS', 'workspace'),
);
const SCREENSHOT = argValue('screenshot');
const SELFTEST = process.argv.includes('--selftest');
const AGENT = process.env.FOXOS_DESKTOP_AGENT || 'human:desktop';

function corePath() {
  if (app.isPackaged) return path.join(process.resourcesPath, 'core');
  return path.join(REPO_ROOT, 'packages', 'core');
}

function pythonPath() {
  if (process.env.FOXOS_PYTHON) return process.env.FOXOS_PYTHON;
  const venv = process.platform === 'win32'
    ? path.join(REPO_ROOT, '.venv', 'Scripts', 'python.exe')
    : path.join(REPO_ROOT, '.venv', 'bin', 'python');
  if (!app.isPackaged && fs.existsSync(venv)) return venv;
  return process.platform === 'win32' ? 'python' : 'python3';
}

// 调用 foxos 命令内核，返回 {ok, exitCode, data, stderr}
function runFoxos(args, { timeoutMs = 120000, json = true } = {}) {
  if (!Array.isArray(args) || args.some((a) => typeof a !== 'string')) {
    return Promise.resolve({ ok: false, exitCode: 2, data: null, stderr: 'args 必须是字符串数组' });
  }
  return new Promise((resolve) => {
    const env = { ...process.env, PYTHONPATH: [corePath(), process.env.PYTHONPATH].filter(Boolean).join(path.delimiter), PYTHONIOENCODING: 'utf-8' };
    const child = spawn(pythonPath(), ['-m', 'foxos', '--workspace', WORKSPACE, '--agent', AGENT, ...args, ...(json ? ['--json'] : [])], { env, windowsHide: true });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ ok: false, exitCode: -1, data: null, stderr: `无法启动 Python（${pythonPath()}）：${err.message}` });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      let data = null;
      if (json) { try { data = stdout.trim() ? JSON.parse(stdout) : null; } catch { data = { raw: stdout }; } }
      resolve({ ok: code === 0, exitCode: code, data, stdout, stderr });
    });
  });
}

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    title: '狐狸OS',
    icon: nativeImage.createFromPath(ICON),
    backgroundColor: '#0f1420',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      backgroundThrottling: false,
    },
  });
  win.setMenuBarVisibility(false);

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // 审计日志变化时通知界面刷新（智能体从 CLI / MCP 操作也会实时出现在操作记录里）
  const auditFile = path.join(WORKSPACE, '.foxos', 'audit.jsonl');
  fs.mkdirSync(path.dirname(auditFile), { recursive: true });
  fs.watchFile(auditFile, { interval: 700 }, () => {
    if (win && !win.isDestroyed()) win.webContents.send('audit:changed');
  });
  win.on('closed', () => { fs.unwatchFile(auditFile); win = null; });
}

ipcMain.handle('foxos:run', (_e, args, opts) => runFoxos(args, { json: !(opts && opts.json === false) }));
ipcMain.handle('foxos:env', () => ({
  workspace: WORKSPACE,
  agent: AGENT,
  platform: process.platform,
  versions: { electron: process.versions.electron, node: process.versions.node, chrome: process.versions.chrome },
  screenshot: Boolean(SCREENSHOT),
}));

// 截图模式：界面加载完数据后发出 ready，主进程截图并退出（用于文档与 CI）
ipcMain.on('ui:log', (_e, msg) => console.error(`[界面] ${msg}`));

// 自检模式：在真实界面上模拟人的操作（提交任务、运行命令、人工接管/恢复），输出 JSON 结果后退出
const SELFTEST_SCRIPT = `(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const waitFor = async (fn, ms = 20000) => { const t = Date.now(); while (Date.now() - t < ms) { const v = fn(); if (v) return v; await sleep(100); } return null; };
  const submit = (text) => { const i = document.querySelector('#task-input'); i.value = text; document.querySelector('#task-form').requestSubmit(); };
  const out = {};
  submit('根据 sales.xlsx 制作季度分析');
  out.taskListed = Boolean(await waitFor(() => [...document.querySelectorAll('.window')].some((w) => w.textContent.includes('根据 sales.xlsx 制作季度分析'))));
  submit('foxos workspace info');
  out.commandRan = Boolean(await waitFor(() => [...document.querySelectorAll('.terminal')].some((t) => t.textContent.includes('$ foxos workspace info') && t.textContent.includes('root:'))));
  document.querySelector('#takeover').click();
  out.paused = Boolean(await waitFor(() => document.querySelector('#takeover').textContent.includes('恢复')));
  const r1 = await window.foxos.run(['control', 'status']);
  out.pausedInKernel = r1.data.result.paused === true;
  document.querySelector('#takeover').click();
  out.resumed = Boolean(await waitFor(() => document.querySelector('#takeover').textContent.includes('人工接管')));
  out.activityShown = document.querySelectorAll('#activity li').length > 0;
  out.agentsShown = document.querySelectorAll('#agents li').length > 0;
  return out;
})()`;

ipcMain.on('ui:ready', async () => {
  if (SELFTEST && win) {
    const result = await win.webContents.executeJavaScript(SELFTEST_SCRIPT);
    const ok = Object.values(result).every(Boolean);
    console.log(`selftest ${ok ? 'PASS' : 'FAIL'} ${JSON.stringify(result)}`);
    app.exit(ok ? 0 : 1);
    return;
  }
  if (!SCREENSHOT || !win) return;
  await new Promise((r) => setTimeout(r, 1200));
  const image = await win.webContents.capturePage();
  const out = path.resolve(SCREENSHOT);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, image.toPNG());
  console.log(`screenshot saved: ${out}`);
  app.quit();
});

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
