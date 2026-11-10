'use strict';
const { contextBridge, ipcRenderer } = require('electron');

// 渲染进程只能通过这几个入口访问系统：调用 foxos 命令内核、读取环境信息、订阅审计变化
contextBridge.exposeInMainWorld('foxos', {
  run: (args, opts) => ipcRenderer.invoke('foxos:run', args, opts),
  env: () => ipcRenderer.invoke('foxos:env'),
  onAuditChanged: (cb) => { ipcRenderer.on('audit:changed', () => cb()); },
  ready: () => ipcRenderer.send('ui:ready'),
  log: (msg) => ipcRenderer.send('ui:log', String(msg)),
});
