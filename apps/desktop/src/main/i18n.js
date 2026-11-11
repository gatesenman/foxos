// 界面语言（简体中文 zh-CN 默认，English en-US）。词条在 src/locales/<语言>.json；
// 主进程用 t()，渲染进程通过预加载脚本拿到同一份词条（FX.t）。内核 / CLI / MCP 通过环境变量 FOXOS_LANG 跟随。
'use strict';
const fs = require('node:fs');
const path = require('node:path');

const SUPPORTED = ['zh-CN', 'en-US'];
const DEFAULT = 'zh-CN';
const DIR = path.join(__dirname, '..', 'locales');
const messages = Object.fromEntries(SUPPORTED.map((l) => [l, JSON.parse(fs.readFileSync(path.join(DIR, `${l}.json`), 'utf8'))]));

function normalize(l) {
  const s = String(l || '').trim().replace('_', '-').toLowerCase();
  if (!s) return null;
  if (s.startsWith('zh')) return 'zh-CN';
  if (s.startsWith('en')) return 'en-US';
  return null;
}
let lang = normalize(process.env.FOXOS_LANG) || DEFAULT;

function getLang() { return lang; }
function setLang(l) { const n = normalize(l); if (!n) throw new Error(`unsupported language: ${l}`); lang = n; process.env.FOXOS_LANG = n; return n; }
function format(s, args) { return String(s).replace(/\{(\d+)\}/g, (m, i) => (args[i] === undefined ? m : String(args[i]))); }
function t(key, ...args) {
  const s = messages[lang][key] ?? messages[DEFAULT][key];
  return s === undefined ? key : format(s, args);
}

module.exports = { SUPPORTED, DEFAULT, messages, normalize, getLang, setLang, t, format };
