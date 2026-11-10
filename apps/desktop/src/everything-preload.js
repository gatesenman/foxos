'use strict';
// Everything 应用页面的预加载：只暴露狐狸OS 本地 Puter 运行时需要的宿主调用
const { contextBridge, ipcRenderer } = require('electron');
const info = ipcRenderer.sendSync('ev:info');
let launchCb = null;
ipcRenderer.on('ev:launch', (_e, items) => { if (launchCb) launchCb(items); });
contextBridge.exposeInMainWorld('__foxosHost', {
  info: () => info,
  invoke: (m, ...a) => ipcRenderer.invoke('ev:invoke', m, ...a).then((r) => { if (r.ok) return r.value; throw r.error; }),
  onLaunchItems: (cb) => { launchCb = cb; },
});
