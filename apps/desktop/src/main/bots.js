'use strict';
// 智能体聊天：启动（或复用）内核里的 foxos bot serve，返回带一次性令牌的本机地址。
// 桌面里的「智能体」窗口与狐狸OS（XFCE）里的独立窗口是同一个界面、同一份数据（FOXOS_HOME 与工作空间）。
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const kernel = require('./kernel');

let child = null;
let pending = null;

function readyFile() { return path.join(os.tmpdir(), `foxos-bots-${process.pid}.url`); }

function ensure() {
  if (child && child.exitCode === null && child.url) return Promise.resolve({ url: child.url });
  if (pending) return pending;
  pending = new Promise((resolve, reject) => {
    const rf = readyFile();
    try { fs.unlinkSync(rf); } catch { /* 没有旧文件 */ }
    const args = ['-m', 'foxos', '--workspace', kernel.getWorkspace(), 'bot', 'serve', '--ready-file', rf];
    const c = spawn(kernel.pythonPath(), args, { env: kernel.coreEnv(), windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    c.stderr.on('data', (d) => { err = (err + d).slice(-2000); });
    const t0 = Date.now();
    const tick = () => {
      if (c.exitCode !== null) { pending = null; reject(new Error(err || `bot serve exited ${c.exitCode}`)); return; }
      let url = '';
      try { url = fs.readFileSync(rf, 'utf8').trim(); } catch { /* 还没写 */ }
      if (url) { try { fs.unlinkSync(rf); } catch { /* 忽略 */ } c.url = url; child = c; pending = null; resolve({ url }); return; }
      if (Date.now() - t0 > 30000) { c.kill(); pending = null; reject(new Error('bot serve did not start')); return; }
      setTimeout(tick, 150);
    };
    c.on('error', (e) => { pending = null; reject(e); });
    tick();
  });
  return pending;
}

function stop() { if (child && child.exitCode === null) child.kill(); child = null; }

module.exports = { ensure, stop };
