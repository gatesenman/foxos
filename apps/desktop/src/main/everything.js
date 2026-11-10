'use strict';
// Everything 应用宿主：在本机运行上游 Everything 应用（不连接 puter.com）。
// - foxapp://<应用>/ 协议提供构建产物；https://js.puter.com/v2/ 被替换为狐狸OS 本地运行时
// - 应用的 puter.fs 映射到工作空间，puter.kv 存在 工作空间/AppData/<应用>/kv.json
// - 每个应用一个独立会话分区；同一时刻每个应用只有一个实例（界面窗口或无界面后台窗口）
// - UI 工具：可访问性快照、按引用点击/输入/按键、截图；供 CLI / MCP 调用
const { app, BrowserWindow, protocol, session, net, dialog, ipcMain, webContents } = require('electron');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { corePath } = require('./paths');
const kernel = require('./kernel');

const SCHEME = 'foxapp';
protocol.registerSchemesAsPrivileged([{ scheme: SCHEME, privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true, allowServiceWorkers: false, codeCache: true } }]);

const SHIM = path.join(corePath(), 'foxos', 'data', 'runtime', 'puter-shim.js');
const BRIDGE = path.join(corePath(), 'foxos', 'data', 'runtime', 'bridge.js');
const PRELOAD = path.join(__dirname, '..', 'everything-preload.js');
const BLOCK = /(^|\.)(puter\.com|puter\.site|puter\.work|plausible\.io|googletagmanager\.com|google-analytics\.com)$/i;

function foxosHome() {
  if (process.env.FOXOS_HOME) return path.resolve(process.env.FOXOS_HOME);
  if (process.platform === 'win32') return path.join(process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local'), 'FoxOS');
  if (process.platform === 'darwin') return path.join(os.homedir(), 'Library', 'Application Support', 'FoxOS');
  return path.join(process.env.XDG_DATA_HOME || path.join(os.homedir(), '.local', 'share'), 'foxos');
}
function catalog() { return JSON.parse(fs.readFileSync(path.join(corePath(), 'foxos', 'data', 'everything.json'), 'utf8')); }
function distDir(id) { return path.join(foxosHome(), 'everything', id, 'dist'); }
function manifest(id) { try { return JSON.parse(fs.readFileSync(path.join(foxosHome(), 'everything', id, 'manifest.json'), 'utf8')); } catch { return null; } }
function list() {
  const c = catalog();
  return { ...c, home: foxosHome(), apps: c.apps.map((a) => ({ ...a, installed: fs.existsSync(path.join(distDir(a.id), 'index.html')), manifest: manifest(a.id) })) };
}

// ---------------------------------------------------------------- 路径映射（Puter 虚拟路径 → 工作空间）
const USER = 'local';
function appDataRel(appId) { return `AppData/${appId}`; }
function toRel(appId, p) {
  let s = String(p == null ? '' : p).replace(/\\/g, '/').trim();
  s = s.replace(/^%appdata%/i, `/${USER}/${appDataRel(appId)}`);
  if (s === '~' || s.startsWith('~/')) s = `/${USER}${s.slice(1)}`;
  if (s.startsWith(`/${USER}/AppData/`)) { const rest = s.slice(`/${USER}/AppData/`.length).split('/'); rest[0] = appId; s = `/${USER}/AppData/${rest.join('/')}`; }
  let rel;
  if (s === `/${USER}` || s.startsWith(`/${USER}/`)) rel = s.slice(USER.length + 2);
  else if (s.startsWith('/')) rel = s.slice(1);
  else rel = `${appDataRel(appId)}/${s}`;
  rel = path.posix.normalize(rel || '.').replace(/^\.\/?/, '');
  if (rel === '..' || rel.startsWith('../')) throw Object.assign(new Error('路径越出工作空间'), { code: 'forbidden' });
  if (rel === '.foxos' || rel.startsWith('.foxos/')) throw Object.assign(new Error('.foxos 为狐狸OS 保留目录'), { code: 'forbidden' });
  return rel;
}
function absOf(rel) {
  const root = kernel.getWorkspace();
  const abs = path.resolve(root, rel);
  const real = (p) => { try { return fs.realpathSync(p); } catch { return null; } };
  let probe = abs; while (!fs.existsSync(probe) && probe !== root) probe = path.dirname(probe);
  const rp = real(probe) || probe; const rr = real(root) || root;
  if (rp !== rr && !rp.startsWith(rr + path.sep)) throw Object.assign(new Error('路径越出工作空间'), { code: 'forbidden' });
  return abs;
}
const vpath = (rel) => (rel ? `/${USER}/${rel}` : `/${USER}`);
function statItem(rel) {
  const abs = absOf(rel);
  let st; try { st = fs.statSync(abs); } catch { throw Object.assign(new Error(`${vpath(rel)} 不存在`), { code: 'subject_does_not_exist' }); }
  const uid = crypto.createHash('sha1').update(`${st.ino}:${st.dev}`).digest('hex').slice(0, 16);
  return { path: vpath(rel), name: rel ? path.posix.basename(rel) : USER, is_dir: st.isDirectory(), size: st.isDirectory() ? null : st.size, modified: Math.floor(st.mtimeMs / 1000), created: Math.floor(st.birthtimeMs / 1000), accessed: Math.floor(st.atimeMs / 1000), uid, immutable: false, type: null };
}
function lockedBy(rel) {
  const lk = path.join(kernel.getWorkspace(), '.foxos', 'locks', `${crypto.createHash('sha1').update(rel).digest('hex').slice(0, 16)}.lock`);
  try { return JSON.parse(fs.readFileSync(lk, 'utf8')); } catch { return null; }
}
function audit(rec) {
  try {
    const line = JSON.stringify({ id: crypto.randomBytes(6).toString('hex'), ts: new Date().toISOString(), status: 'ok', permission: 'write', ...rec });
    fs.appendFileSync(path.join(kernel.getWorkspace(), '.foxos', 'audit.jsonl'), `${line}\n`);
  } catch { /* 工作空间尚未初始化 */ }
}
function uniqueName(abs) {
  if (!fs.existsSync(abs)) return abs;
  const ext = path.extname(abs); const base = abs.slice(0, abs.length - ext.length);
  for (let i = 1; ; i++) { const c = `${base} (${i})${ext}`; if (!fs.existsSync(c)) return c; }
}

// ---------------------------------------------------------------- KV
const kvCache = new Map();
function kvFile(appId) { return absOf(`${appDataRel(appId)}/kv.json`); }
function kvLoad(appId) {
  if (kvCache.has(appId)) return kvCache.get(appId);
  let d = {}; try { d = JSON.parse(fs.readFileSync(kvFile(appId), 'utf8')); } catch { /* 新建 */ }
  kvCache.set(appId, d); return d;
}
const kvTimers = new Map();
function kvSave(appId) {
  clearTimeout(kvTimers.get(appId));
  kvTimers.set(appId, setTimeout(() => {
    const f = kvFile(appId); fs.mkdirSync(path.dirname(f), { recursive: true });
    const tmp = `${f}.foxos-tmp-${process.pid}`; fs.writeFileSync(tmp, JSON.stringify(kvLoad(appId), null, 1)); fs.renameSync(tmp, f);
  }, 120));
}
function kvInvalidate(appId) { kvCache.delete(appId); }
const glob = (pat) => new RegExp(`^${String(pat).replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.')}$`);

// ---------------------------------------------------------------- 宿主方法（应用内 puter.* 调用）
const methods = {
  'fs.read': (a, p) => { const rel = toRel(a, p); const abs = absOf(rel); if (!fs.existsSync(abs)) throw Object.assign(new Error(`${vpath(rel)} 不存在`), { code: 'subject_does_not_exist' }); return { name: path.basename(abs), bytes: fs.readFileSync(abs) }; },
  'fs.write': (a, p, bytes, o = {}) => {
    const rel = toRel(a, p); let abs = absOf(rel);
    const lk = lockedBy(rel); if (lk && (lk.owner || lk.agent) && !String(lk.owner || lk.agent).startsWith('human')) throw Object.assign(new Error(`${rel} 正被 ${lk.owner || lk.agent} 写入（写锁）`), { code: 'locked' });
    if (fs.existsSync(abs) && fs.statSync(abs).isDirectory()) throw Object.assign(new Error('目标是文件夹'), { code: 'is_dir' });
    if (fs.existsSync(abs) && o.overwrite === false) { if (o.dedupeName) abs = uniqueName(abs); else throw Object.assign(new Error(`${vpath(rel)} 已存在`), { code: 'item_with_same_name_exists' }); }
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    const tmp = `${abs}.foxos-tmp-${process.pid}`; fs.writeFileSync(tmp, Buffer.from(bytes)); fs.renameSync(tmp, abs);
    const r = path.relative(kernel.getWorkspace(), abs).split(path.sep).join('/');
    if (!r.startsWith(`${appDataRel(a)}/`)) audit({ agent: `human:${a}`, command: 'everything.fs.write', targets: [{ path: r, access: 'write' }], message: `${a} 保存了 ${r}` });
    return statItem(r);
  },
  'fs.readdir': (a, p) => { const rel = toRel(a, p); const abs = absOf(rel); if (!fs.existsSync(abs)) { if (rel.startsWith(appDataRel(a))) return []; throw Object.assign(new Error(`${vpath(rel)} 不存在`), { code: 'subject_does_not_exist' }); } return fs.readdirSync(abs).filter((n) => n !== '.foxos' && !n.includes('.foxos-tmp-')).map((n) => statItem(rel ? `${rel}/${n}` : n)); },
  'fs.stat': (a, p) => statItem(toRel(a, p)),
  'fs.mkdir': (a, p) => { const rel = toRel(a, p); fs.mkdirSync(absOf(rel), { recursive: true }); return statItem(rel); },
  'fs.delete': (a, p, o = {}) => { const rel = toRel(a, p); if (!rel) throw Object.assign(new Error('不能删除工作空间根目录'), { code: 'forbidden' }); const abs = absOf(rel); if (!fs.existsSync(abs)) return true; fs.rmSync(abs, { recursive: Boolean(o.recursive) || fs.statSync(abs).isFile(), force: true }); if (!rel.startsWith(`${appDataRel(a)}/`)) audit({ agent: `human:${a}`, command: 'everything.fs.delete', targets: [{ path: rel, access: 'write' }] }); return true; },
  'fs.rename': (a, p, n) => { const rel = toRel(a, p); if (/[\\/]/.test(n)) throw new Error('新名称不能包含路径'); const dest = path.posix.join(path.posix.dirname(rel), n); fs.renameSync(absOf(rel), absOf(dest)); return statItem(dest); },
  'fs.move': (a, p, d, o = {}) => { const rel = toRel(a, p); let dest = toRel(a, d); if (fs.existsSync(absOf(dest)) && fs.statSync(absOf(dest)).isDirectory()) dest = path.posix.join(dest, path.posix.basename(rel)); if (o.createMissingParents) fs.mkdirSync(path.dirname(absOf(dest)), { recursive: true }); fs.renameSync(absOf(rel), absOf(dest)); return statItem(dest); },
  'fs.copy': (a, p, d) => { const rel = toRel(a, p); let dest = toRel(a, d); if (fs.existsSync(absOf(dest)) && fs.statSync(absOf(dest)).isDirectory()) dest = path.posix.join(dest, path.posix.basename(rel)); fs.cpSync(absOf(rel), absOf(dest), { recursive: true }); return statItem(dest); },
  'fs.url': (a, p) => `${SCHEME}://${a}/__workspace/${toRel(a, p).split('/').map(encodeURIComponent).join('/')}`,
  'kv.set': (a, k, v) => { kvLoad(a)[k] = v; kvSave(a); return true; },
  'kv.get': (a, k) => { const d = kvLoad(a); return Object.prototype.hasOwnProperty.call(d, k) ? d[k] : null; },
  'kv.del': (a, k) => { delete kvLoad(a)[k]; kvSave(a); return true; },
  'kv.list': (a, pat, rv) => { const re = glob(pat); const d = kvLoad(a); const keys = Object.keys(d).filter((k) => re.test(k)); return rv ? keys.map((k) => ({ key: k, value: d[k] })) : keys; },
  'kv.incr': (a, k, n) => { const d = kvLoad(a); d[k] = (Number(d[k]) || 0) + n; kvSave(a); return d[k]; },
  'kv.add': (a, k, v) => { const d = kvLoad(a); d[k] = Array.isArray(d[k]) ? [...d[k], ...(Array.isArray(v) ? v : [v])] : (Array.isArray(v) ? v : [v]); kvSave(a); return d[k]; },
  'kv.update': (a, k, v) => { const d = kvLoad(a); d[k] = { ...(d[k] && typeof d[k] === 'object' ? d[k] : {}), ...v }; kvSave(a); return d[k]; },
  'kv.flush': (a) => { kvCache.set(a, {}); kvSave(a); return true; },
  'ui.openPicker': async (a, o = {}, wc) => {
    const r = await dialog.showOpenDialog(BrowserWindow.fromWebContents(wc) || undefined, { defaultPath: kernel.getWorkspace(), properties: [o.directory ? 'openDirectory' : 'openFile', ...(o.multiple ? ['multiSelections'] : [])] });
    if (r.canceled || !r.filePaths.length) return null;
    return r.filePaths.map((f) => { const rel = path.relative(kernel.getWorkspace(), f).split(path.sep).join('/'); if (rel.startsWith('..')) throw Object.assign(new Error('只能打开工作空间内的文件'), { code: 'forbidden' }); return statItem(rel); });
  },
  'ui.savePicker': async (a, o = {}, wc) => {
    const r = await dialog.showSaveDialog(BrowserWindow.fromWebContents(wc) || undefined, { defaultPath: path.join(kernel.getWorkspace(), o.suggestedName || 'untitled') });
    if (r.canceled || !r.filePath) return null;
    const rel = path.relative(kernel.getWorkspace(), r.filePath).split(path.sep).join('/');
    if (rel.startsWith('..')) throw Object.assign(new Error('只能保存到工作空间内'), { code: 'forbidden' });
    return vpath(rel);
  },
  'ui.title': (a, t) => { hooks.onTitle && hooks.onTitle(a, t); return true; },
  'ui.launchApp': (a, name, args) => { hooks.onLaunchApp && hooks.onLaunchApp(name, args); return true; },
  'ui.close': (a) => { hooks.onClose && hooks.onClose(a); return true; },
  'net.fetch': async (a, url, init) => {
    const u = new URL(url); if (BLOCK.test(u.hostname)) throw new Error(`本地模式不连接 ${u.hostname}`);
    const r = await fetch(url, { method: init.method, headers: init.headers, body: init.body && init.body.length ? Buffer.from(init.body) : undefined, redirect: 'follow' });
    return { status: r.status, statusText: r.statusText, headers: Object.fromEntries(r.headers), body: new Uint8Array(await r.arrayBuffer()) };
  },
};

const hooks = {};
const sessions = new Map(); // partition session -> appId
const instances = new Map(); // appId -> { wc, hidden, win, launchItems }

function setupSession(appId) {
  const part = `persist:ev-${appId}`;
  const ses = session.fromPartition(part);
  if (sessions.has(ses)) return part;
  sessions.set(ses, appId);
  ses.setPermissionRequestHandler((_wc, perm, cb) => cb(['clipboard-sanitized-write', 'clipboard-read', 'fullscreen', 'media', 'notifications'].includes(perm)));
  ses.protocol.handle(SCHEME, async (req) => {
    const u = new URL(req.url);
    if (u.pathname.startsWith('/__workspace/')) {
      const rel = decodeURIComponent(u.pathname.slice('/__workspace/'.length));
      return net.fetch(require('node:url').pathToFileURL(absOf(toRel(appId, `/${USER}/${rel}`))).href);
    }
    if (u.hostname === 'foxos-runtime') return net.fetch(require('node:url').pathToFileURL(u.pathname === '/bridge.js' ? BRIDGE : SHIM).href);
    const root = distDir(u.hostname);
    let file = path.join(root, decodeURIComponent(u.pathname));
    if (!file.startsWith(root)) return new Response('forbidden', { status: 403 });
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) file = fs.existsSync(path.join(file, 'index.html')) ? path.join(file, 'index.html') : path.join(root, 'index.html');
    const resp = await net.fetch(require('node:url').pathToFileURL(file).href);
    if (/\.html$/.test(file)) {
      // 去掉上游页面里的 Puter SDK 与统计脚本，换成本地运行时与应用桥
      let html = await resp.text();
      html = html.replace(/<script[^>]*src="https:\/\/js\.puter\.com\/v2\/?"[^>]*><\/script>/g, `<script src="${SCHEME}://foxos-runtime/puter.js"></script><script src="${SCHEME}://foxos-runtime/bridge.js"></script>`)
        .replace(/<script[^>]*src="https:\/\/plausible\.io[^"]*"[^>]*><\/script>/g, '');
      if (!html.includes('foxos-runtime/puter.js')) html = html.replace('<head>', `<head><script src="${SCHEME}://foxos-runtime/puter.js"></script><script src="${SCHEME}://foxos-runtime/bridge.js"></script>`);
      return new Response(html, { headers: { 'content-type': 'text/html; charset=utf-8' } });
    }
    return resp;
  });
  ses.webRequest.onBeforeRequest((d, cb) => {
    try { const u = new URL(d.url); if (/^https?:$/.test(u.protocol) && BLOCK.test(u.hostname)) return cb({ cancel: true }); } catch { /* 忽略 */ }
    cb({});
  });
  return part;
}

function appOfSender(wc) { return sessions.get(wc.session) || null; }

ipcMain.on('ev:info', (e) => {
  const a = appOfSender(e.sender);
  const inst = a && instances.get(a);
  e.returnValue = a ? { app: a, appID: `foxos-${a}`, user: { username: USER, uuid: `foxos-${os.userInfo().username}`, email: null, email_confirmed: true, is_temp: false }, launchItems: inst && inst.launchItems ? inst.launchItems.map((r) => statItem(r)) : [] } : null;
});
ipcMain.handle('ev:invoke', async (e, method, ...args) => {
  const a = appOfSender(e.sender);
  if (!a) return { ok: false, error: { message: '未知应用', code: 'forbidden' } };
  const fn = methods[method];
  if (!fn) return { ok: false, error: { message: `本地模式未实现 ${method}`, code: 'not_supported_locally' } };
  try { return { ok: true, value: await fn(a, ...args, e.sender) }; } catch (err) { return { ok: false, error: { message: String(err.message || err), code: err.code || 'error' } }; }
});

// 界面窗口里的 webview 登记为该应用的实例
function registerWebview(appId, wc) {
  const prev = instances.get(appId);
  if (prev && prev.hidden && prev.win && !prev.win.isDestroyed()) prev.win.destroy();
  instances.set(appId, { wc, hidden: false, launchItems: prev ? prev.launchItems : null });
  wc.on('destroyed', () => { if (instances.get(appId)?.wc === wc) instances.delete(appId); });
}

// 无界面实例（CLI / MCP 调用时应用没有打开）
async function ensureInstance(appId, { launchRel = null } = {}) {
  const cur = instances.get(appId);
  if (cur && !cur.wc.isDestroyed()) return cur;
  if (!fs.existsSync(path.join(distDir(appId), 'index.html'))) throw Object.assign(new Error(`${appId} 未安装：运行 foxos everything install ${appId}`), { code: 'DEPENDENCY_MISSING' });
  const part = setupSession(appId);
  const win = new BrowserWindow({ show: false, width: 1280, height: 800, webPreferences: { partition: part, preload: PRELOAD, contextIsolation: true, sandbox: true, backgroundThrottling: false, offscreen: false } });
  const inst = { wc: win.webContents, hidden: true, win, launchItems: launchRel ? [launchRel] : null };
  instances.set(appId, inst);
  win.webContents.on('destroyed', () => { if (instances.get(appId) === inst) instances.delete(appId); });
  await win.loadURL(`${SCHEME}://${appId}/index.html`);
  await waitReady(inst.wc);
  return inst;
}
async function waitReady(wc, ms = 15000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    try { if (await wc.executeJavaScript('document.readyState === "complete" && !!window.__foxosBridge', true)) return true; } catch { /* 页面切换中 */ }
    await new Promise((r) => setTimeout(r, 150));
  }
  return false;
}

function openFile(appId, rel) {
  const inst = instances.get(appId);
  if (inst) { inst.launchItems = [rel]; inst.wc.send('ev:launch', [statItem(rel)]); }
}

// 应用桥调用：在应用页面内执行（快照、点击、输入、按键、模块操作）
async function js(wc, expr) {
  const r = await wc.executeJavaScript(`(async () => { try { return { ok: true, v: await (${expr}) }; } catch (e) { return { ok: false, m: String(e && e.message || e), c: e && e.code }; } })()`, true);
  if (!r.ok) throw Object.assign(new Error(r.m), { code: r.c || 'ERROR' });
  return r.v;
}
async function bridge(appId, method, params = {}) {
  const inst = await ensureInstance(appId);
  if (method === 'screenshot') { const img = await inst.wc.capturePage(); return { png_base64: img.toPNG().toString('base64'), width: img.getSize().width, height: img.getSize().height }; }
  if (method === 'type') {
    await js(inst.wc, `window.__foxosBridge.focus(${JSON.stringify(params.ref || null)}, ${JSON.stringify(Boolean(params.clear))})`);
    await inst.wc.insertText(String(params.text || ''));
    return js(inst.wc, `window.__foxosBridge.describe(${JSON.stringify(params.ref || null)})`);
  }
  if (method === 'press') {
    if (params.ref) await js(inst.wc, `window.__foxosBridge.focus(${JSON.stringify(params.ref)}, false)`);
    const parts = String(params.key).split('+'); const key = parts.pop(); const modifiers = parts.map((m) => ({ ctrl: 'control', cmd: 'meta', mod: process.platform === 'darwin' ? 'meta' : 'control' }[m.toLowerCase()] || m.toLowerCase()));
    inst.wc.sendInputEvent({ type: 'keyDown', keyCode: key, modifiers });
    if (key.length === 1 && !modifiers.some((m) => m === 'control' || m === 'meta')) inst.wc.sendInputEvent({ type: 'char', keyCode: key, modifiers });
    inst.wc.sendInputEvent({ type: 'keyUp', keyCode: key, modifiers });
    await new Promise((r) => setTimeout(r, 120));
    return { pressed: params.key };
  }
  return js(inst.wc, `window.__foxosBridge.call(${JSON.stringify(method)}, ${JSON.stringify(params)})`);
}

function status(appId) {
  const inst = instances.get(appId);
  return { app: appId, installed: fs.existsSync(path.join(distDir(appId), 'index.html')), running: Boolean(inst && !inst.wc.isDestroyed()), mode: inst ? (inst.hidden ? 'headless' : 'window') : null, url: inst ? inst.wc.getURL() : null };
}
function close(appId) { const inst = instances.get(appId); if (!inst) return false; if (inst.hidden) inst.win.destroy(); else hooks.onClose && hooks.onClose(appId); instances.delete(appId); return true; }

module.exports = { list, catalog, setupSession, registerWebview, ensureInstance, bridge, status, close, openFile, hooks, PRELOAD, SCHEME, foxosHome, distDir, kvInvalidate, instances, waitReady, toRel };
