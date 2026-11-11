'use strict';
const { t } = require('./i18n');
// 本机控制通道：foxos CLI / MCP（Python 内核）通过它驱动正在运行的桌面（Everything 应用、窗口、界面工具）。
// 只监听 127.0.0.1，随机端口 + 随机令牌，写入 工作空间/.foxos/desktop.json（权限 600）。
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const kernel = require('./kernel');

let server = null;
let infoFile = null;

function start(handler, extra = {}) {
  const token = crypto.randomBytes(24).toString('hex');
  server = http.createServer((req, res) => {
    const send = (code, obj) => { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); };
    if (req.headers.authorization !== `Bearer ${token}`) return send(401, { ok: false, error: { code: 'PERMISSION_DENIED', message: t('control.invalid_token') } });
    if (req.method !== 'POST') return send(405, { ok: false, error: { code: 'USAGE', message: t('control.only_post_is_supported') } });
    let body = '';
    req.on('data', (d) => { body += d; if (body.length > 50e6) req.destroy(); });
    req.on('end', async () => {
      let msg;
      try { msg = JSON.parse(body || '{}'); } catch { return send(400, { ok: false, error: { code: 'USAGE', message: t('control.the_request_is_not_json') } }); }
      try { send(200, { ok: true, result: await handler(msg) }); } catch (e) { send(200, { ok: false, error: { code: e.code && /^[A-Z_]+$/.test(e.code) ? e.code : 'ERROR', message: String(e.message || e) } }); }
    });
  });
  server.listen(0, '127.0.0.1', () => {
    const dir = path.join(kernel.getWorkspace(), '.foxos');
    fs.mkdirSync(dir, { recursive: true });
    infoFile = path.join(dir, 'desktop.json');
    fs.writeFileSync(infoFile, JSON.stringify({ port: server.address().port, token, pid: process.pid, startedAt: new Date().toISOString(), ...extra }), { mode: 0o600 });
  });
}

function stop() {
  try { if (infoFile) { const d = JSON.parse(fs.readFileSync(infoFile, 'utf8')); if (d.pid === process.pid) fs.unlinkSync(infoFile); } } catch { /* 忽略 */ }
  if (server) server.close();
}

module.exports = { start, stop };
