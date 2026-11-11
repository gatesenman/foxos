#!/usr/bin/env node
// 多语言检查：
//  1. src/locales/zh-CN.json 与 en-US.json 的键完全一致，占位符 {0}… 一致，没有空值
//  2. 源码里用到的每个词条键（FX.t('…') / t('…')）都存在
//  3. 渲染进程与主进程源码里没有写死的界面文字：字符串 / 模板字面量中不能有中文；
//     作为界面文字使用的英文字面量（text / title / placeholder / aria-label、toast / confirm / prompt 的参数）也不允许
//  4. index.html 中可见的中文都有 data-i18n / data-i18n-* 标注
// 用法：node scripts/lint-i18n.js [--json]
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const acorn = require('acorn');
const walk = require('acorn-walk');

const SRC = path.join(__dirname, '..', 'src');
const HAN = /[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/;
// 不翻译的专有名词 / 产品名 / 技术标识（作为界面文字出现时允许）
const ALLOW_EN = /^(?:https?:.*|[A-Z][\w.+-]*(?: [A-Z][\w.+-]*)*|[a-z0-9_.:/@-]+|.*\$\{.*|[\W\d]*)$/;
// 允许出现中文的字面量：语言自身的名字（语言选择器用各自语言显示）
const ALLOW_HAN = new Set(['简体中文']);
const problems = [];
const add = (file, line, kind, text) => problems.push({ file: path.relative(path.join(SRC, '..'), file), line, kind, text: String(text).slice(0, 120) });

// 1
const loc = Object.fromEntries(['zh-CN', 'en-US'].map((l) => [l, JSON.parse(fs.readFileSync(path.join(SRC, 'locales', `${l}.json`), 'utf8'))]));
const ph = (s) => (String(s).match(/\{\d+\}/g) || []).sort().join(',');
for (const [a, b] of [['zh-CN', 'en-US'], ['en-US', 'zh-CN']]) for (const k of Object.keys(loc[a])) if (!(k in loc[b])) add(`src/locales/${b}.json`, 0, 'missing-key', k);
for (const k of Object.keys(loc['zh-CN'])) {
  if (k in loc['en-US'] && ph(loc['zh-CN'][k]) !== ph(loc['en-US'][k]) && !/^setup\.group_label$/.test(k)) add('src/locales/en-US.json', 0, 'placeholder-mismatch', k);
  for (const l of ['zh-CN', 'en-US']) if (loc[l][k] === '' ) add(`src/locales/${l}.json`, 0, 'empty', k);
  if (loc['en-US'][k] && HAN.test(loc['en-US'][k]) && !ALLOW_HAN.has(loc['en-US'][k]) && !/[\/]\s*语言$/.test(loc['en-US'][k])) add('src/locales/en-US.json', 0, 'han-in-en', k);
}

// 2 + 3
const files = [];
(function scan(d) { for (const f of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, f.name); if (f.isDirectory()) { if (!['locales', 'third-party-icons'].includes(f.name)) scan(p); } else if (/\.js$/.test(f.name)) files.push(p); } })(SRC);
const used = new Set();
const UI_PROPS = new Set(['text', 'title', 'placeholder', 'aria-label', 'label', 'okText', 'cancelText']);
const UI_CALLS = new Set(['toast', 'confirm', 'prompt', 'alert']);
for (const file of files) {
  const src = fs.readFileSync(file, 'utf8');
  let ast;
  try { ast = acorn.parse(src, { ecmaVersion: 'latest', allowHashBang: true, allowReturnOutsideFunction: true, locations: true }); } catch (e) { add(file, 0, 'parse-error', e.message); continue; }
  walk.fullAncestor(ast, (node, _s, anc) => {
    const parent = anc[anc.length - 2];
    const line = node.loc.start.line;
    if (node.type === 'CallExpression') {
      const c = node.callee;
      const name = c.type === 'Identifier' ? c.name : c.type === 'MemberExpression' && !c.computed ? c.property.name : null;
      if ((name === 't') && node.arguments[0] && node.arguments[0].type === 'Literal') {
        const k = node.arguments[0].value; used.add(k);
        if (!(k in loc['zh-CN'])) add(file, line, 'unknown-key', k);
      }
      if (UI_CALLS.has(name)) for (const a of node.arguments.slice(0, 2)) if (a.type === 'Literal' && typeof a.value === 'string' && /[A-Za-z]{2,} [A-Za-z]{2,}/.test(a.value) && !ALLOW_EN.test(a.value)) add(file, line, 'hardcoded-en', a.value);
    }
    if (node.type === 'Literal' && typeof node.value === 'string' && HAN.test(node.value) && !ALLOW_HAN.has(node.value)) add(file, line, 'hardcoded-han', node.value);
    if (node.type === 'TemplateElement' && HAN.test(node.value.cooked)) add(file, line, 'hardcoded-han', node.value.cooked);
    if (node.type === 'Property' && parent && node.value.type === 'Literal' && typeof node.value.value === 'string') {
      const key = node.key.type === 'Identifier' ? node.key.name : node.key.value;
      const v = node.value.value;
      if (UI_PROPS.has(key) && /[A-Za-z]{2,}/.test(v) && /\s/.test(v) && !ALLOW_EN.test(v) && file.includes(`${path.sep}renderer${path.sep}`)) add(file, line, 'hardcoded-en', v);
    }
  });
}
for (const k of Object.keys(loc['zh-CN'])) if (!used.has(k) && !/^(ev\.|shell\.)/.test(k)) add('src/locales/zh-CN.json', 0, 'unused-key', k);

// 4
const html = fs.readFileSync(path.join(SRC, 'renderer', 'index.html'), 'utf8');
for (const m of html.matchAll(/<([a-z0-9]+)([^>]*)>([^<]*)/gi)) {
  const [, tag, attrs, text] = m;
  if (tag === 'html') continue;
  if (HAN.test(text) && !/data-i18n=/.test(attrs)) add('src/renderer/index.html', 0, 'html-text', text.trim());
  for (const a of ['title', 'placeholder', 'aria-label']) {
    const v = (attrs.match(new RegExp(`\\s${a}="([^"]*)"`)) || [])[1];
    if (v && HAN.test(v) && !new RegExp(`data-i18n-${a === 'aria-label' ? 'aria' : a}=`).test(attrs)) add('src/renderer/index.html', 0, 'html-attr', `${a}=${v}`);
  }
  for (const k of attrs.matchAll(/data-i18n(?:-\w+)?="([^"]+)"/g)) { used.add(k[1]); if (!(k[1] in loc['zh-CN'])) add('src/renderer/index.html', 0, 'unknown-key', k[1]); }
}

const errors = problems.filter((p) => p.kind !== 'unused-key');
if (process.argv.includes('--json')) console.log(JSON.stringify({ keys: Object.keys(loc['zh-CN']).length, problems }, null, 1));
else {
  for (const p of problems) console.log(`${p.kind === 'unused-key' ? '提示' : '错误'} ${p.file}:${p.line} ${p.kind} ${p.text}`);
  console.log(`词条 ${Object.keys(loc['zh-CN']).length} 个；错误 ${errors.length}，提示 ${problems.length - errors.length}`);
}
process.exit(errors.length ? 1 : 0);
