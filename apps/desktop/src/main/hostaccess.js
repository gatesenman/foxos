'use strict';
// 「允许在本机执行」只有一个事实来源：核心的 foxos bot host-access 状态（FOXOS_HOME/host-access.json）。
// 桌面客户端的设置开关和命令行 `foxos bot host-access enable|disable` 读写的是同一个开关：
//   读：直接读核心报告的状态文件（每次都读，命令行改了立刻生效；核心原子写入）
//   写：调用 foxos bot host-access（只有人能改，写审计日志）
// 默认关闭；打开后每一次本机动作仍要逐个确认（桌面：原生对话框；智能体：审批卡片）。
const fs = require('node:fs');
const kernel = require('./kernel');

let statePath = null;

function parse(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')).enabled === true; } catch { return false; }
}

async function status() {
  const r = await kernel.runLocal(['bot', 'host-access'], { timeoutMs: 60000 });
  const res = r.ok && r.data && r.data.result;
  if (!res) return { enabled: false, error: (r.stderr || '').trim() || 'host-access status failed' };
  if (res.path) statePath = res.path;
  return res;
}

async function enabled() {
  if (!statePath) await status();
  return statePath ? parse(statePath) : false;
}

async function set(on) {
  const r = await kernel.runLocal(['bot', 'host-access', on ? 'enable' : 'disable'], { timeoutMs: 60000 });
  const res = r.ok && r.data && r.data.result;
  if (!res) throw new Error((r.data && r.data.error && r.data.error.message) || (r.stderr || '').trim() || 'host-access update failed');
  if (res.path) statePath = res.path;
  return res.enabled === true;
}

module.exports = { status, enabled, set };
