'use strict';
const { contextBridge, ipcRenderer } = require('electron');

// 渲染进程能用的全部系统入口：都经过主进程，文件操作统一走 foxos 内核
const call = (ch, ...a) => ipcRenderer.invoke(ch, ...a).then((r) => {
  if (!r.ok) throw new Error(r.error);
  return r.value;
});
const on = (ch, cb) => ipcRenderer.on(ch, (_e, ...a) => cb(...a));

const I18N = ipcRenderer.sendSync('i18n:init');

contextBridge.exposeInMainWorld('foxos', {
  i18n: { ...I18N, set: (l) => call('i18n:set', l) },
  run: (args, opts) => ipcRenderer.invoke('foxos:run', args, opts),
  openExternal: (url) => ipcRenderer.invoke('foxos:openExternal', url),
  env: () => call('env'),
  cli: { commandLine: (args) => call('cli:commandLine', args) },
  detectApps: () => call('apps:detect'),
  office: {
    launch: (appId, file) => call('office:launch', appId, file),
    list: () => call('office:list'),
    focus: (wid) => call('office:focus', wid),
    close: (wid) => call('office:close', wid),
    onChanged: (cb) => on('office:changed', cb),
  },
  pty: {
    spawn: (opts) => call('pty:spawn', opts),
    write: (id, d) => ipcRenderer.send('pty:write', id, d),
    resize: (id, c, r) => ipcRenderer.send('pty:resize', id, c, r),
    kill: (id) => ipcRenderer.send('pty:kill', id),
    onData: (cb) => on('pty:data', cb),
    onExit: (cb) => on('pty:exit', cb),
  },
  icons: { report: () => call('icons:report') },
  bots: { url: () => call('bots:url') },
  agents: {
    list: () => call('agents:list'),
    installed: () => call('agents:installed'),
    install: (id) => call('agents:install', id),
    uninstall: (id) => call('agents:uninstall', id),
    onLog: (cb) => on('agents:log', cb),
    onProgress: (cb) => on('agents:progress', cb),
  },
  acp: {
    start: (id, opts) => call('acp:start', id, opts || {}),
    newSession: (c) => call('acp:newSession', c),
    authenticate: (c, m) => call('acp:authenticate', c, m),
    prompt: (c, s, t) => call('acp:prompt', c, s, t),
    cancel: (c, s) => call('acp:cancel', c, s),
    stop: (c) => call('acp:stop', c),
    stderr: (c) => call('acp:stderr', c),
    onEvent: (cb) => on('acp:event', cb),
    onPermission: (cb) => on('acp:permission', cb),
    replyPermission: (reqId, optionId) => ipcRenderer.send('acp:permissionReply', reqId, optionId),
  },
  settings: {
    get: () => call('settings:get'),
    set: (p) => call('settings:set', p),
    setSecret: (n, v) => call('secrets:set', n, v),
  },
  session: { load: () => call('session:load'), save: (s) => call('session:save', s) },
  setup: { plan: () => call('setup:plan') },
  everything: {
    list: () => call('ev:list'),
    attach: (appId, wcId) => call('ev:attach', appId, wcId),
    openFile: (appId, rel) => call('ev:openFile', appId, rel),
    openInGuest: (appId, rel) => call('ev:openInGuest', appId, rel),
    onOpen: (cb) => on('ev:open', cb),
    onTitle: (cb) => on('ev:title', cb),
    onClose: (cb) => on('ev:close', cb),
    onLaunchApp: (cb) => on('ev:launchApp', cb),
  },
  guest: {
    status: () => call('guest:status'),
    set: (g) => call('guest:set', g),
  },
  rfb: {
    open: () => call('rfb:open'),
    write: (id, data) => ipcRenderer.send('rfb:write', id, data),
    close: (id) => ipcRenderer.send('rfb:close', id),
    onData: (cb) => on('rfb:data', cb),
    onClose: (cb) => on('rfb:close', cb),
    onError: (cb) => on('rfb:error', cb),
  },
  chooseFile: () => call('dialog:chooseFile'),
  relaunch: () => call('app:relaunch'),
  chooseDir: () => call('dialog:chooseDir'),
  onFsChanged: (cb) => on('fs:changed', cb),
  ready: () => ipcRenderer.send('ui:ready'),
  log: (m) => ipcRenderer.send('ui:log', String(m)),
});
