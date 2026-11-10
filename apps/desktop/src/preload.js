'use strict';
const { contextBridge, ipcRenderer } = require('electron');

// 渲染进程能用的全部系统入口：都经过主进程，文件操作统一走 foxos 内核
const call = (ch, ...a) => ipcRenderer.invoke(ch, ...a).then((r) => {
  if (!r.ok) throw new Error(r.error);
  return r.value;
});
const on = (ch, cb) => ipcRenderer.on(ch, (_e, ...a) => cb(...a));

contextBridge.exposeInMainWorld('foxos', {
  run: (args, opts) => ipcRenderer.invoke('foxos:run', args, opts),
  env: () => call('env'),
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
  agents: {
    list: () => call('agents:list'),
    installed: () => call('agents:installed'),
    install: (id) => call('agents:install', id),
    uninstall: (id) => call('agents:uninstall', id),
    onLog: (cb) => on('agents:log', cb),
    onProgress: (cb) => on('agents:progress', cb),
  },
  acp: {
    start: (id) => call('acp:start', id),
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
  relaunch: () => call('app:relaunch'),
  chooseDir: () => call('dialog:chooseDir'),
  onFsChanged: (cb) => on('fs:changed', cb),
  ready: () => ipcRenderer.send('ui:ready'),
  log: (m) => ipcRenderer.send('ui:log', String(m)),
});
