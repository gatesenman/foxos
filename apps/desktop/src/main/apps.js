'use strict';
const { t } = require('./i18n');
// 已安装软件检测、LibreOffice 原生窗口启动与跟踪
const { app } = require('electron');
const { spawn, execFile } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { IS_WIN, which } = require('./paths');
const kernel = require('./kernel');

const SOFFICE_CANDIDATES = [
  'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
  'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe',
  '/Applications/LibreOffice.app/Contents/MacOS/soffice',
];

function findSoffice() {
  if (process.env.FOXOS_SOFFICE) return fs.existsSync(process.env.FOXOS_SOFFICE) ? process.env.FOXOS_SOFFICE : null;
  return which('soffice') || which('libreoffice') || SOFFICE_CANDIDATES.find((c) => fs.existsSync(c)) || null;
}

function execOut(file, args, timeout = 8000) {
  return new Promise((resolve) => {
    execFile(file, args, { timeout, env: kernel.coreEnv(), windowsHide: true }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout: String(stdout || '').trim(), stderr: String(stderr || '').trim() });
    });
  });
}

async function version(file, args = ['--version']) {
  if (!file) return null;
  const r = await execOut(file, args);
  return r.ok ? (r.stdout || r.stderr).split('\n')[0] : null;
}

// 真实检测宿主上的软件；未安装的返回 installed:false 与安装提示
async function detect() {
  const soffice = findSoffice();
  const py = kernel.pythonPath();
  const pyVer = await version(which(py) || py);
  const deps = pyVer ? await execOut(which(py) || py, ['-c', 'import openpyxl, docx, pptx; print(openpyxl.__version__, docx.__version__ if hasattr(docx, "__version__") else "", pptx.__version__)']) : { ok: false };
  const git = which('git');
  const node = which('node');
  const npm = which('npm');
  const loVer = soffice ? await version(soffice) : null;
  const office = (id, name, flag, exts) => ({
    id, name, kind: 'native', installed: Boolean(soffice), version: loVer, path: soffice, flag, exts,
    hint: soffice ? null : t('apps.libreoffice_is_not_installed_select'),
  });
  return {
    builtin: [
      { id: 'terminal', name: t('common.terminal'), installed: true, kind: 'builtin', version: require('./pty').defaultShell() },
      { id: 'files', name: t('apps.file_manager'), installed: true, kind: 'builtin' },
      { id: 'editor', name: t('apps.code_editor'), installed: true, kind: 'builtin', version: `Monaco ${JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'node_modules', 'monaco-editor', 'package.json'), 'utf8')).version}` },
      { id: 'browser', name: t('common.browser'), installed: true, kind: 'builtin', version: `Chromium ${process.versions.chrome}` },
      { id: 'environments', name: t('common.environments'), installed: true, kind: 'builtin', version: { linux: t('apps.linux_namespaces'), win32: 'WSL2', darwin: 'Virtualization.framework' }[process.platform] || process.platform },
    ],
    office: [
      office('writer', 'LibreOffice Writer', '--writer', ['.docx', '.doc', '.odt', '.rtf', '.txt']),
      office('calc', 'LibreOffice Calc', '--calc', ['.xlsx', '.xls', '.ods', '.csv']),
      office('impress', 'LibreOffice Impress', '--impress', ['.pptx', '.ppt', '.odp']),
    ],
    tools: [
      { id: 'python', name: 'Python', installed: Boolean(pyVer), version: pyVer, path: py, hint: pyVer ? null : t('apps.install_python_3_10') },
      { id: 'python-deps', name: t('apps.python_office_libraries_openpyxl'), installed: deps.ok, version: deps.ok ? deps.stdout : null,
        hint: deps.ok ? null : t('apps.select_python_dependencies_in_the') },
      { id: 'git', name: 'git', installed: Boolean(git), version: await version(git), path: git, hint: git ? null : t('apps.install_git') },
      { id: 'node', name: 'Node.js', installed: Boolean(node), version: await version(node), path: node, hint: node ? null : t('apps.install_node_js_needed_by_npm_based') },
      { id: 'npm', name: 'npm', installed: Boolean(npm), version: await version(npm), path: npm },
      { id: 'wmctrl', name: t('apps.wmctrl_tracks_native_windows_linux'), installed: Boolean(which('wmctrl')), path: which('wmctrl'), hint: IS_WIN ? null : t('apps.optional_install_wmctrl_to_track') },
    ],
  };
}

// ---------------------------------------------------------------- LibreOffice 原生窗口
const launched = new Map(); // id -> {id, pid, app, file, startedAt, exited}
let nextId = 1;
let notify = () => {};

function onChange(fn) { notify = fn; }

function loProfile() {
  const dir = path.join(app.getPath('userData'), 'libreoffice-profile');
  fs.mkdirSync(dir, { recursive: true });
  return require('node:url').pathToFileURL(dir).href;
}

function launchOffice(appId, relFile) {
  const soffice = findSoffice();
  if (!soffice) throw new Error(t('apps.libreoffice_is_not_installed'));
  const flag = { writer: '--writer', calc: '--calc', impress: '--impress' }[appId];
  if (!flag) throw new Error(t('apps.unknown_app', appId));
  const args = [`-env:UserInstallation=${loProfile()}`, '--nologo', '--norestore', flag];
  let abs = null;
  if (relFile) {
    abs = path.resolve(kernel.getWorkspace(), relFile);
    const root = kernel.getWorkspace();
    if (!(abs === root || abs.startsWith(root + path.sep))) throw new Error(t('common.only_files_inside_the_workspace_can'));
    args.push(abs);
  }
  const child = spawn(soffice, args, { cwd: kernel.getWorkspace(), detached: !IS_WIN, stdio: 'ignore', windowsHide: false });
  const rec = { id: nextId++, pid: child.pid, app: appId, file: relFile || null, startedAt: Date.now(), exited: null };
  launched.set(rec.id, rec);
  child.on('exit', (code) => { rec.exited = code; notify(); });
  child.on('error', (e) => { rec.exited = -1; rec.error = e.message; notify(); });
  notify();
  return rec;
}

// 用 wmctrl 列出真实的 LibreOffice 窗口（X11）；其他平台只跟踪进程
async function nativeWindows() {
  const wm = which('wmctrl');
  if (!wm || IS_WIN || process.platform === 'darwin') return [];
  const r = await execOut(wm, ['-lp']);
  if (!r.ok) return [];
  return r.stdout.split('\n').filter(Boolean).map((line) => {
    const m = /^(0x[0-9a-f]+)\s+(-?\d+)\s+(\d+)\s+\S+\s+(.*)$/i.exec(line);
    return m ? { wid: m[1], desktop: Number(m[2]), pid: Number(m[3]), title: m[4] } : null;
  }).filter((w) => w && /LibreOffice/.test(w.title));
}

function processList() { return [...launched.values()]; }

async function focusNative(wid) {
  const wm = which('wmctrl');
  if (!wm) return false;
  return (await execOut(wm, ['-ia', wid])).ok;
}

async function closeNative(wid) {
  const wm = which('wmctrl');
  if (!wm) return false;
  return (await execOut(wm, ['-ic', wid])).ok;
}

function killAll() {
  for (const r of launched.values()) {
    if (r.exited == null) { try { process.kill(IS_WIN ? r.pid : -r.pid); } catch { /* 已退出 */ } }
  }
}

module.exports = { detect, findSoffice, launchOffice, nativeWindows, processList, focusNative, closeNative, onChange, killAll, execOut };
