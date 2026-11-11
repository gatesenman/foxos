'use strict';
// 狐狸OS 桌面（Electron 主进程）
const { app, BrowserWindow, ipcMain, nativeImage, session, shell, dialog, webContents } = require('electron');
const fs = require('node:fs');
const path = require('node:path');
const paths = require('./paths');

// 测试与多实例：--user-data-dir= 指定独立的用户数据目录（必须在 ready 之前）
const userDataArg = paths.argValue('user-data-dir');
if (userDataArg) app.setPath('userData', path.resolve(userDataArg));

const settings = require('./settings');
const kernel = require('./kernel');
const pty = require('./pty');
const apps = require('./apps');
const agents = require('./agents');
const setup = require('./setup');
const { watchWorkspace } = require('./fswatch');
const { AcpConnection } = require('./acp');
const everything = require('./everything');
const control = require('./control');

const s0 = settings.load();
kernel.setWorkspace(paths.argValue('workspace') || s0.workspace || paths.defaultWorkspace());
const SCREENSHOT = paths.argValue('screenshot');
const HEADLESS = process.argv.includes('--headless');

let win = null;
let stopWatch = null;
const send = (ch, ...a) => { if (win && !win.isDestroyed()) win.webContents.send(ch, ...a); };

function createWindow() {
  const sess = settings.loadSession();
  const b = sess.bounds || { width: 1440, height: 900 };
  win = new BrowserWindow({
    ...b,
    minWidth: 1024,
    minHeight: 680,
    title: '狐狸OS',
    icon: nativeImage.createFromPath(paths.iconPath()),
    backgroundColor: '#0b0d12',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: true,
      backgroundThrottling: false,
    },
  });
  if (sess.maximized) win.maximize();
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  const saveBounds = () => {
    if (!win || win.isDestroyed()) return;
    const cur = settings.loadSession();
    settings.saveSession({ ...cur, bounds: win.getNormalBounds(), maximized: win.isMaximized() });
  };
  win.on('resize', saveBounds);
  win.on('move', saveBounds);
  win.on('closed', () => { pty.killAll(); win = null; });

  stopWatch = watchWorkspace(kernel.getWorkspace(), (ev) => send('fs:changed', ev));
  apps.onChange(() => send('office:changed'));
}

const SCROLLBAR_CSS = fs.readFileSync(path.join(__dirname, '..', 'scrollbars.css'), 'utf8');
const SCROLLBAR_JS = fs.readFileSync(path.join(__dirname, '..', 'scrollbars.js'), 'utf8');
// 浏览器 webview：禁止注入 preload、强制隔离
app.on('web-contents-created', (_e, contents) => {
  contents.on('will-attach-webview', (_ev, webPreferences, params) => {
    delete webPreferences.preload;
    const evApp = /^persist:ev-([a-z0-9]+(?:-[a-z0-9]+)*)--[0-9a-f]{8}$/.exec(params.partition || '');
    if (evApp) { everything.setupSession(evApp[1]); webPreferences.preload = everything.PRELOAD; }
    webPreferences.nodeIntegration = false;
    webPreferences.contextIsolation = true;
    webPreferences.sandbox = true;
    if (!/^(https?:|about:blank|file:|foxapp:)/.test(params.src || 'about:blank')) _ev.preventDefault();
  });
  // 每个应用 webview（Everything 应用、浏览器）注入狐狸OS 滚动条样式
  if (contents.getType() === 'webview') {
    contents.on('dom-ready', () => {
      contents.insertCSS(SCROLLBAR_CSS).catch(() => {});
      contents.executeJavaScript(SCROLLBAR_JS, false).catch(() => {});
    });
  }
  contents.setWindowOpenHandler(({ url }) => {
    if (contents.getType() === 'webview') { contents.loadURL(url); return { action: 'deny' }; }
    return { action: 'deny' };
  });
});

// ---------------------------------------------------------------- IPC
const handle = (ch, fn) => ipcMain.handle(ch, async (_e, ...a) => {
  try { return { ok: true, value: await fn(...a) }; } catch (err) { return { ok: false, error: String(err && err.message || err) }; }
});

ipcMain.handle('foxos:openExternal', (_e, url) => (/^https:\/\//.test(String(url)) ? shell.openExternal(String(url)).then(() => true) : false));
ipcMain.handle('foxos:run', (_e, args, opts = {}) => kernel.run(args, { json: opts.json !== false, stdin: opts.stdin ?? null, ...(opts.timeoutMs ? { timeoutMs: Math.min(+opts.timeoutMs || 0, 4 * 3600 * 1000) } : {}) }));

handle('env', () => ({
  workspace: kernel.getWorkspace(),
  agent: 'human:desktop',
  platform: process.platform,
  arch: process.arch,
  versions: { electron: process.versions.electron, chrome: process.versions.chrome, node: process.versions.node, app: app.getVersion() },
  userData: app.getPath('userData'),
  python: kernel.pythonPath(),
  encryption: settings.encryptionInfo(),
  setupDone: settings.load().setupDone,
  screenshot: Boolean(SCREENSHOT),
  shell: process.env.SHELL || '/bin/sh',
}));

handle('apps:detect', () => apps.detect());

// Everything 应用
handle('ev:list', () => everything.list());
handle('ev:attach', (appId, wcId) => { const wc = webContents.fromId(wcId); if (!wc) throw new Error('webview 不存在'); everything.registerWebview(appId, wc); return true; });
handle('ev:openFile', (appId, rel) => everything.openFile(appId, rel));
everything.hooks.onTitle = (appId, t) => send('ev:title', appId, t);
everything.hooks.onLaunchApp = (name, args) => send('ev:launchApp', name, args);
everything.hooks.onClose = (appId) => send('ev:close', appId);

// 控制通道：CLI / MCP → 桌面
async function controlHandler(msg) {
  const { op, app: appId, params = {}, agent = 'agent' } = msg;
  if (op === 'ping') return { pid: process.pid, headless: HEADLESS, workspace: kernel.getWorkspace() };
  if (op === 'ev.status') return everything.status(appId);
  if (op === 'ev.open') {
    if (win && !HEADLESS && params.window !== false) { send('ev:open', appId, params.file || null, agent); for (let i = 0; i < 100 && !everything.instances.get(appId); i++) await new Promise((r) => setTimeout(r, 100)); }
    const inst = await everything.ensureInstance(appId, { launchRel: params.file || null });
    await everything.waitReady(inst.wc);
    if (params.file) everything.openFile(appId, params.file);
    return everything.status(appId);
  }
  if (op === 'ev.close') return { closed: everything.close(appId) };
  if (op === 'ev.reset') return everything.reset(appId);
  if (op === 'ev.bridge') return everything.bridge(appId, params.method, params.args || {});
  if (op === 'ev.reloadData') { everything.kvInvalidate(appId); const inst = everything.instances.get(appId); if (inst) { inst.wc.reload(); await everything.waitReady(inst.wc); } return everything.status(appId); }
  throw Object.assign(new Error(`未知操作 ${op}`), { code: 'USAGE' });
}
handle('office:launch', (appId, file) => apps.launchOffice(appId, file));
handle('office:list', async () => ({ processes: apps.processList(), windows: await apps.nativeWindows() }));
handle('office:focus', (wid) => apps.focusNative(wid));
handle('office:close', (wid) => apps.closeNative(wid));

handle('pty:spawn', (opts) => pty.spawnPty(win.webContents, opts || {}));
ipcMain.on('pty:write', (_e, id, data) => pty.write(id, data));
ipcMain.on('pty:resize', (_e, id, cols, rows) => pty.resize(id, cols, rows));
ipcMain.on('pty:kill', (_e, id) => pty.kill(id));

handle('agents:list', () => agents.list());
handle('agents:installed', () => agents.installed());
handle('agents:install', (id) => agents.install(id, {
  log: (text) => send('agents:log', id, text),
  progress: (ratio, got, total) => send('agents:progress', id, ratio, got, total),
}));
handle('agents:uninstall', (id) => agents.uninstall(id));

// ACP 连接
const conns = new Map();
const permWaiters = new Map();
let nextConn = 1;
let nextPerm = 1;
handle('acp:start', async (agentId, opts = {}) => {
  const info = agents.installedInfo(agentId);
  if (!info) throw new Error(`未安装：${agentId}`);
  const connId = nextConn++;
  const c = new AcpConnection(info, {
    onEvent: (ev) => send('acp:event', connId, ev),
    onPermission: (params) => new Promise((resolve) => {
      const reqId = nextPerm++;
      permWaiters.set(reqId, resolve);
      send('acp:permission', connId, reqId, params);
    }),
  });
  conns.set(connId, c);
  try { await c.start(opts.env || null); } catch (e) { conns.delete(connId); c.stop(); throw e; }
  const init = await c.initialize();
  return { connId, init, identity: c.identity };
});
handle('acp:newSession', (connId) => conns.get(connId).newSession());
handle('acp:authenticate', (connId, methodId) => conns.get(connId).authenticate(methodId));
handle('acp:prompt', (connId, sessionId, text) => conns.get(connId).prompt(sessionId, text));
handle('acp:cancel', (connId, sessionId) => conns.get(connId).cancel(sessionId));
handle('acp:stop', (connId) => { conns.get(connId)?.stop(); conns.delete(connId); return true; });
handle('acp:stderr', (connId) => conns.get(connId)?.stderr || '');
ipcMain.on('acp:permissionReply', (_e, reqId, optionId) => {
  const r = permWaiters.get(reqId);
  if (r) { permWaiters.delete(reqId); r(optionId || null); }
});

handle('settings:get', () => { const s = settings.load(); return { ...s, secrets: settings.secretNames() }; });
handle('settings:set', (patch) => {
  const s = settings.load();
  const allowed = ['workspace', 'python', 'setupDone', 'agentDefault'];
  for (const k of allowed) if (k in patch) s[k] = patch[k];
  settings.save(s);
  return true;
});
handle('secrets:set', (name, value) => { settings.setSecret(name, value); return settings.secretNames(); });
handle('session:load', () => settings.loadSession());
handle('session:save', (state) => { const cur = settings.loadSession(); settings.saveSession({ ...cur, ...state }); return true; });
handle('setup:plan', () => setup.plan());
handle('app:relaunch', () => { app.relaunch(); app.exit(0); });
handle('dialog:chooseDir', async () => {
  const r = await dialog.showOpenDialog(win, { properties: ['openDirectory', 'createDirectory'] });
  return r.canceled ? null : r.filePaths[0];
});
handle('shell:showInFolder', (rel) => shell.showItemInFolder(path.resolve(kernel.getWorkspace(), rel)));

// 截图模式（文档与 CI）：界面就绪后截取窗口并退出
ipcMain.on('ui:ready', async () => {
  if (!SCREENSHOT || !win) return;
  await new Promise((r) => setTimeout(r, 1500));
  const image = await win.webContents.capturePage();
  fs.mkdirSync(path.dirname(path.resolve(SCREENSHOT)), { recursive: true });
  fs.writeFileSync(path.resolve(SCREENSHOT), image.toPNG());
  console.log(`screenshot saved: ${path.resolve(SCREENSHOT)}`);
  app.quit();
});
handle('icons:report', () => require('./icons').report());
ipcMain.on('ui:log', (_e, msg) => console.error(`[界面] ${msg}`));

app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_wc, _perm, cb) => cb(false));
  require('./icons').register(session.defaultSession);
  const launch = { exec: process.execPath, args: [...(app.isPackaged ? [] : [app.getAppPath()]), ...process.argv.filter((a) => a === '--no-sandbox' || a.startsWith('--user-data-dir='))] };
  control.start(controlHandler, { launch });
  try { fs.mkdirSync(everything.foxosHome(), { recursive: true }); fs.writeFileSync(path.join(everything.foxosHome(), 'desktop-launch.json'), JSON.stringify(launch)); } catch { /* 忽略 */ }
  if (!HEADLESS) createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('before-quit', () => {
  for (const c of conns.values()) c.stop();
  if (stopWatch) stopWatch();
  control.stop();
  if (process.env.FOXOS_CLOSE_NATIVE_ON_EXIT === '1') apps.killAll();
});
app.on('window-all-closed', () => { if (!HEADLESS && process.platform !== 'darwin') app.quit(); });
