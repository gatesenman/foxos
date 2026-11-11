// 狐狸OS 本地 Puter 运行时：替换 https://js.puter.com/v2/，让 Everything 应用完全在本机运行。
// 文件系统映射到狐狸OS 工作空间，KV 存在工作空间的 AppData/<应用>/kv.json，登录为本机用户。
// 依赖云端的能力（AI、Worker、P2P、托管、分享）不会连接 puter.com，而是明确报错。
(() => {
  'use strict';
  // 消息语言跟随狐狸OS（通过 Chromium 语言传入页面的 navigator.language）
  const L = (zh, en) => (/^zh/i.test(navigator.language || 'zh') ? zh : en);
  const host = window.__foxosHost;
  if (!host) { console.error(L('[foxos] 缺少宿主桥，Puter 运行时不可用', '[foxos] Host bridge missing; the Puter runtime is unavailable')); return; }
  const info = host.info();
  const call = (m, ...a) => host.invoke(m, ...a);
  const unsupported = (what) => () => Promise.reject(Object.assign(new Error(L(`${what} 需要 Puter 云服务，狐狸OS 本地模式未提供`, `${what} needs the Puter cloud service, which FoxOS local mode does not provide`)), { code: 'not_supported_locally' }));
  const fsErr = (e) => { const err = new Error(e.message); err.code = e.code; throw err; };
  const toBytes = async (d) => {
    if (d == null) return new Uint8Array();
    if (typeof d === 'string') return new TextEncoder().encode(d);
    if (d instanceof ArrayBuffer) return new Uint8Array(d);
    if (ArrayBuffer.isView(d)) return new Uint8Array(d.buffer, d.byteOffset, d.byteLength);
    if (d instanceof Blob) return new Uint8Array(await d.arrayBuffer());
    if (Array.isArray(d) && d[0] instanceof Blob) return toBytes(d[0]);
    return new TextEncoder().encode(typeof d === 'object' ? JSON.stringify(d) : String(d));
  };
  const MIME = { json: 'application/json', txt: 'text/plain', md: 'text/markdown', html: 'text/html', csv: 'text/csv', svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', pdf: 'application/pdf', mp3: 'audio/mpeg', wav: 'audio/wav', mp4: 'video/mp4', webm: 'video/webm' };
  const mime = (n) => MIME[String(n).split('.').pop().toLowerCase()] || 'application/octet-stream';
  const pathOf = (p) => (p && typeof p === 'object' ? p.path : p);
  const item = (st) => st && ({ ...st, id: st.uid, read: () => fs.read(st.path), write: (d) => fs.write(st.path, d, { overwrite: true }), readdir: () => fs.readdir(st.path), delete: () => fs.delete(st.path, { recursive: true }), rename: (n) => fs.rename(st.path, n) });

  const fs = {
    async read(p, o = {}) { const r = await call('fs.read', pathOf(p), o).catch(fsErr); return new Blob([r.bytes], { type: mime(r.name) }); },
    async write(p, data, o = {}) {
      if (p && typeof p === 'object') { o = { ...p, ...o }; p = p.path; }
      return item(await call('fs.write', p, await toBytes(data), o).catch(fsErr));
    },
    async readdir(p, o = {}) { return (await call('fs.readdir', pathOf(p) ?? '~', o).catch(fsErr)).map(item); },
    async stat(p, o = {}) { return item(await call('fs.stat', pathOf(p), o).catch(fsErr)); },
    async mkdir(p, o = {}) { return item(await call('fs.mkdir', pathOf(p), o).catch(fsErr)); },
    async delete(p, o = {}) { for (const x of (Array.isArray(p) ? p : [p])) await call('fs.delete', pathOf(x), o).catch(fsErr); return true; },
    async rename(p, n) { return item(await call('fs.rename', pathOf(p), n).catch(fsErr)); },
    async move(p, d, o = {}) { return item(await call('fs.move', pathOf(p), pathOf(d), o).catch(fsErr)); },
    async copy(p, d, o = {}) { return item(await call('fs.copy', pathOf(p), pathOf(d), o).catch(fsErr)); },
    async getReadURL(p) { return call('fs.url', pathOf(p)).catch(fsErr); },
    async upload(files, dir = '~', o = {}) { const out = []; for (const f of (files.length != null ? [...files] : [files])) out.push(await fs.write(`${pathOf(dir)}/${f.name}`, f, o)); return out.length === 1 ? out[0] : out; },
    async space() { return { capacity: 0, used: 0 }; },
    share: unsupported(L('文件分享', 'File sharing')),
  };
  const kv = {
    MAX_KEY_SIZE: 1024, MAX_VALUE_SIZE: 400 * 1024, MAX: 1024,
    set: (k, v) => call('kv.set', String(k), v === undefined ? null : JSON.parse(JSON.stringify(v))),
    get: (k) => call('kv.get', String(k)),
    del: (k) => call('kv.del', String(k)),
    list: (pattern, rv) => { if (typeof pattern === 'boolean') { rv = pattern; pattern = '*'; } if (pattern && typeof pattern === 'object') { rv = pattern.returnValues; pattern = pattern.pattern; } return call('kv.list', pattern || '*', Boolean(rv)); },
    incr: (k, n = 1) => call('kv.incr', String(k), typeof n === 'number' ? n : 1),
    decr: (k, n = 1) => call('kv.incr', String(k), -(typeof n === 'number' ? n : 1)),
    add: (k, v) => call('kv.add', String(k), v), update: (k, v) => call('kv.update', String(k), v),
    flush: () => call('kv.flush'), expire: async () => true, expireAt: async () => true,
    share: unsupported(L('KV 分享', 'KV sharing')), unshare: async () => true, listShared: async () => [], listSharedByMe: async () => [], getShared: unsupported(L('共享数据', 'Shared data')),
  };
  const user = info.user;
  const auth = { isSignedIn: () => true, signIn: async () => user, signOut: async () => {}, getUser: async () => user, whoami: async () => user, getProfilePicture: async () => null, getMonthlyUsage: async () => ({}), getDetailedAppUsage: async () => ({}), type: 'user' };
  const launch = []; const opened = []; const closers = [];
  // 打开文件的请求可能早于应用注册 onLaunchedWithItems（例如应用先异步载入界面语言）：先记下，注册时再交给应用
  let pendingLaunch = null;
  host.onLaunchItems((items) => { const its = items.map(item); if (!launch.length && !opened.length) pendingLaunch = its; for (const fn of [...launch, ...opened]) { try { fn(its); } catch (e) { console.error(e); } } });
  const cancelled = () => Object.assign(new Error(L('用户取消', 'Cancelled by the user')), { code: 'cancelled', name: 'AbortError' });
  const ui = {
    showOpenFilePicker: async (o = {}) => { const r = await call('ui.openPicker', { multiple: Boolean(o.multiple), accept: o.accept || null }); if (!r) throw cancelled(); return o.multiple ? r.map(item) : item(r[0]); },
    showDirectoryPicker: async () => { const r = await call('ui.openPicker', { directory: true }); if (!r) throw cancelled(); return item(r[0]); },
    showSaveFilePicker: async (data, name) => { const t = await call('ui.savePicker', { suggestedName: name || 'untitled' }); if (!t) throw cancelled(); return data != null ? fs.write(t, data, { overwrite: true }) : item({ path: t, name: t.split('/').pop(), is_dir: false }); },
    onLaunchedWithItems: (fn) => { launch.push(fn); const its = pendingLaunch || (info.launchItems && info.launchItems.length ? info.launchItems.map(item) : null); pendingLaunch = null; if (its) setTimeout(() => fn(its), 0); },
    onItemsOpened: (fn) => { opened.push(fn); }, onWindowClose: (fn) => { closers.push(fn); },
    setWindowTitle: (t) => { call('ui.title', String(t)); }, launchApp: (n, a) => call('ui.launchApp', String(n), a || null),
    alert: async (m) => window.alert(String(m)), prompt: async (m, d) => window.prompt(String(m), d),
    contextMenu: () => {}, hideWindow: () => {}, showWindow: () => {}, hideSpinner: () => {}, showSpinner: () => {},
    requestPermission: async () => true, requestPictureInPicture: async () => false, exitPictureInPicture: async () => false,
    showFeedbackDialog: async () => {}, socialShare: unsupported(L('社交分享', 'Social sharing')), parentApp: () => null, exit: () => call('ui.close'),
    request: unsupported(L('Puter 桌面请求', 'Puter desktop requests')), setMenubar: () => {}, on: () => {}, wasLaunchedWithItems: () => Boolean(pendingLaunch || (info.launchItems && info.launchItems.length)),
  };
  const noAI = unsupported('Puter AI');
  const ai = { enabled: false, chat: noAI, txt2img: noAI, img2txt: noAI, txt2speech: noAI, speech2txt: noAI, txt: noAI, img: noAI, speech: noAI, listModels: async () => [], listModelProviders: async () => [] };
  const net = {
    fetch: async (url, init = {}) => {
      const body = init.body == null ? null : await toBytes(init.body);
      const headers = init.headers instanceof Headers ? Object.fromEntries(init.headers) : (init.headers || {});
      const r = await call('net.fetch', String(url), { method: init.method || 'GET', headers, body });
      return new Response([204, 304].includes(r.status) ? null : r.body, { status: r.status, statusText: r.statusText, headers: r.headers });
    },
    Socket: function Socket() { throw new Error(L('原始 TCP 套接字需要 Puter 云中继，狐狸OS 本地模式未提供', 'Raw TCP sockets need the Puter cloud relay, which FoxOS local mode does not provide')); },
    tls: { TLSSocket: function TLSSocket() { throw new Error(L('TLS 套接字需要 Puter 云中继，狐狸OS 本地模式未提供', 'TLS sockets need the Puter cloud relay, which FoxOS local mode does not provide')); } },
  };
  const cloud = (w) => ({ exec: unsupported(w), create: unsupported(w), delete: unsupported(w), get: unsupported(w), update: unsupported(w), list: async () => [] });
  window.puter = {
    env: 'app', appID: info.appID, appInstanceID: `foxos-${info.app}`, authToken: 'foxos-local', foxos: true,
    fs, kv, auth, ui, ai, net,
    perms: { request: async () => true, check: async () => true, requestReadFile: async () => true, requestWriteFile: async () => true },
    workers: cloud('Puter Worker'), hosting: cloud(L('Puter 托管', 'Puter hosting')), apps: cloud(L('Puter 应用目录', 'Puter app directory')),
    peer: { serve: unsupported(L('Puter P2P 中继', 'Puter P2P relay')), connect: unsupported(L('Puter P2P 中继', 'Puter P2P relay')), ensureTurnRelays: unsupported(L('Puter P2P 中继', 'Puter P2P relay')), createGuestGrant: unsupported(L('Puter P2P 中继', 'Puter P2P relay')) },
    drivers: { call: unsupported(L('Puter 驱动', 'Puter drivers')) }, print: (...a) => console.log(...a),
    randName: (s = '-') => `local${s}${Math.random().toString(36).slice(2, 8)}`,
    setAuthToken: () => {}, setAPIOrigin: () => {}, resetAuthToken: () => {},
  };
  window.addEventListener('beforeunload', () => { for (const fn of closers) { try { fn(); } catch { /* 忽略 */ } } });
})();
