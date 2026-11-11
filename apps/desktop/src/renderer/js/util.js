// 通用工具：DOM 构造、图标、弹窗、文件类型
'use strict';
window.FX = window.FX || {};

// 界面语言：词条来自 src/locales/<语言>.json（预加载脚本同步提供），缺失时退回简体中文，再退回键名
(() => {
  const I = window.foxos.i18n;
  FX.lang = I.lang;
  FX.languages = I.supported;
  FX.t = (key, ...args) => {
    const s = I.messages[FX.lang][key] ?? I.messages['zh-CN'][key];
    if (s === undefined) { window.foxos.log(`missing i18n key ${key}`); return key; }
    return String(s).replace(/\{(\d+)\}/g, (m, i) => (args[i] === undefined ? m : String(args[i])));
  };
  FX.has = (key) => I.messages[FX.lang][key] !== undefined;
  document.documentElement.lang = FX.lang;
  // 静态 HTML：data-i18n（文本）、data-i18n-title / data-i18n-placeholder / data-i18n-aria（属性）
  FX.applyI18n = (root = document) => {
    for (const n of root.querySelectorAll('[data-i18n]')) n.textContent = FX.t(n.dataset.i18n);
    for (const [a, attr] of [['i18nTitle', 'title'], ['i18nPlaceholder', 'placeholder'], ['i18nAria', 'aria-label']]) for (const n of root.querySelectorAll(`[data-${a.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`)) n.setAttribute(attr, FX.t(n.dataset[a]));
  };
  // 切换语言：保存设置，重新载入界面（窗口按会话恢复；内核此后使用新语言）
  FX.setLanguage = async (lang) => {
    if (lang === FX.lang) return;
    const dirty = (FX.windows ? FX.windows() : []).filter((w) => w.isDirty && w.isDirty());
    if (dirty.length && !(await FX.confirm(FX.t('util.switch_language'), FX.t('util.unsaved_changes_will_be_lost', dirty.length), { okText: FX.t('util.switch') }))) return;
    await I.set(lang);
    if (FX.saveSession) await FX.saveSession(true);
    location.reload();
  };
})();

FX.$ = (sel, root = document) => root.querySelector(sel);
FX.$$ = (sel, root = document) => [...root.querySelectorAll(sel)];

FX.el = (tag, attrs = {}, ...children) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(n.style, v);
    else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const c of children.flat(Infinity)) if (c != null && c !== false) n.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return n;
};

// Tabler Icons 图标字体（本地打包，离线可用）
FX.icon = (name, cls = '') => FX.el('i', { class: `ti ti-${name} ${cls}`.trim(), 'aria-hidden': 'true' });
// 程序图标：用开源项目自带的图标（<img>）；加载失败时退回字体图标并记下来（FX.iconMissing）。
// spec 是字体图标名（狐狸OS 自己的程序）或 { src, fallback }。
FX.iconMissing = new Set();
FX.appIcon = (spec, cls = '') => {
  if (!spec || typeof spec === 'string') return FX.icon(spec || 'box', cls);
  const img = FX.el('img', { class: `app-img ${cls}`.trim(), src: spec.src, alt: '', draggable: 'false', 'data-icon-src': spec.src });
  img.addEventListener('error', () => {
    FX.iconMissing.add(spec.src);
    const f = FX.icon(spec.fallback || 'box', cls); f.dataset.iconMissing = spec.src;
    img.replaceWith(f);
  }, { once: true });
  return img;
};
// 各程序的图标来源（见 main/icons.js）
const PROGRAM_ICONS = {
  terminal: { src: 'foxicon://builtin/terminal', fallback: 'terminal-2' },
  editor: { src: 'foxicon://builtin/editor', fallback: 'code' },
  browser: { src: 'foxicon://builtin/browser', fallback: 'world' },
  writer: { src: 'foxicon://libreoffice/writer', fallback: 'file-text' },
  calc: { src: 'foxicon://libreoffice/calc', fallback: 'file-spreadsheet' },
  impress: { src: 'foxicon://libreoffice/impress', fallback: 'presentation' },
};
FX.programIcon = (id, fallback) => PROGRAM_ICONS[id] || fallback;
FX.evIcon = (app) => ({ src: `foxicon://everything/${app.id || app}`, fallback: FX.groupIcon ? FX.groupIcon(app.group) : 'app-window' });
FX.agentIcon = (a) => (a.icon && /^https:\/\//.test(a.icon) ? { src: a.icon, fallback: 'robot' } : 'robot');

FX.fmtBytes = (n) => (n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(1)} KB` : `${(n / 1048576).toFixed(1)} MB`);
FX.fmtTime = (ts) => {
  const d = typeof ts === 'number' ? new Date(ts * (ts < 1e12 ? 1000 : 1)) : new Date(ts);
  const p = (x) => String(x).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
};
FX.hhmmss = (ts) => { const d = new Date(ts); const p = (x) => String(x).padStart(2, '0'); return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`; };

FX.ext = (p) => { const m = /\.([^./\\]+)$/.exec(p || ''); return m ? m[1].toLowerCase() : ''; };
FX.basename = (p) => String(p || '').split('/').filter(Boolean).pop() || '';
FX.dirname = (p) => String(p || '').split('/').slice(0, -1).join('/');

const TEXT_EXT = new Set(['txt', 'md', 'json', 'jsonl', 'js', 'mjs', 'cjs', 'ts', 'tsx', 'jsx', 'py', 'sh', 'bash', 'zsh', 'ps1', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf', 'html', 'htm', 'css', 'scss', 'xml', 'sql', 'rs', 'go', 'java', 'c', 'h', 'cpp', 'hpp', 'cs', 'rb', 'php', 'lua', 'r', 'log', 'env', 'gitignore', 'dockerfile', 'makefile', 'csv', 'tsv']);
FX.fileKind = (name, type) => {
  if (type === 'dir') return { icon: 'folder', opener: 'files', label: FX.t('util.folder') };
  const e = FX.ext(name);
  if (['xlsx', 'xls', 'ods'].includes(e)) return { icon: 'file-spreadsheet', opener: 'calc', label: FX.t('util.spreadsheet') };
  if (['docx', 'doc', 'odt', 'rtf'].includes(e)) return { icon: 'file-text', opener: 'writer', label: FX.t('util.document') };
  if (['pptx', 'ppt', 'odp'].includes(e)) return { icon: 'presentation', opener: 'impress', label: FX.t('util.presentation') };
  if (e === 'pdf') return { icon: 'file-type-pdf', opener: 'browser', label: 'PDF' };
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(e)) return { icon: 'photo', opener: 'browser', label: FX.t('util.image') };
  if (['html', 'htm'].includes(e)) return { icon: 'file-code', opener: 'editor', label: FX.t('util.web_page'), alt: 'browser' };
  if (e === 'csv' || e === 'tsv') return { icon: 'file-spreadsheet', opener: 'editor', label: 'CSV', alt: 'calc' };
  if (TEXT_EXT.has(e) || !e) return { icon: e === 'md' ? 'markdown' : ['js', 'ts', 'py', 'sh', 'json', 'css', 'rs', 'go'].includes(e) ? 'file-code' : 'file', opener: 'editor', label: FX.t('util.kind_text') };
  return { icon: 'file', opener: 'editor', label: e.toUpperCase() };
};

// 调用内核：成功返回 result，失败抛出带 code 的错误
FX.k = async (args, opts) => {
  const r = await window.foxos.run(args, opts);
  if (r.ok) return r.data ? r.data.result : r.stdout;
  const err = r.data && r.data.error;
  const e = new Error(err ? err.message : (r.stderr || FX.t('util.exit_code', r.exitCode)));
  e.code = err ? err.code : 'ERROR';
  e.hint = err && err.hint;
  throw e;
};

// 提示条
FX.toast = (msg, kind = 'info') => {
  let box = FX.$('#toasts');
  if (!box) { box = FX.el('div', { id: 'toasts', class: 'toasts' }); document.body.append(box); }
  const t = FX.el('div', { class: `toast ${kind}` }, FX.icon(kind === 'error' ? 'alert-triangle' : kind === 'ok' ? 'circle-check' : 'info-circle'), FX.el('span', { text: msg }));
  box.append(t);
  setTimeout(() => t.remove(), kind === 'error' ? 7000 : 3500);
};

// 输入弹窗（Electron 不支持 window.prompt）
FX.prompt = (title, { value = '', placeholder = '', okText = FX.t('util.ok') } = {}) => new Promise((resolve) => {
  const input = FX.el('input', { class: 'input', value, placeholder });
  const close = (v) => { overlay.remove(); resolve(v); };
  const overlay = FX.el('div', { class: 'overlay' },
    FX.el('form', { class: 'dialog', onsubmit: (e) => { e.preventDefault(); close(input.value.trim() || null); } },
      FX.el('div', { class: 'dialog-title', text: title }), input,
      FX.el('div', { class: 'dialog-actions' },
        FX.el('button', { type: 'button', class: 'btn ghost', onclick: () => close(null) }, FX.t('common.cancel')),
        FX.el('button', { type: 'submit', class: 'btn primary' }, okText))));
  FX.$('#modal-root').append(overlay);
  input.focus();
  input.select();
});

FX.confirm = (title, body, { okText = FX.t('util.ok'), danger = false } = {}) => new Promise((resolve) => {
  const close = (v) => { overlay.remove(); resolve(v); };
  const overlay = FX.el('div', { class: 'overlay' },
    FX.el('div', { class: 'dialog' },
      FX.el('div', { class: 'dialog-title', text: title }), FX.el('div', { class: 'dialog-body', text: body }),
      FX.el('div', { class: 'dialog-actions' },
        FX.el('button', { class: 'btn ghost', onclick: () => close(false) }, FX.t('common.cancel')),
        FX.el('button', { class: `btn ${danger ? 'danger' : 'primary'}`, onclick: () => close(true) }, okText))));
  FX.$('#modal-root').append(overlay);
});

// 简单事件总线
FX.bus = new EventTarget();
FX.emit = (name, detail) => FX.bus.dispatchEvent(new CustomEvent(name, { detail }));
FX.on = (name, fn) => FX.bus.addEventListener(name, (e) => fn(e.detail));
// 语言选择（安装向导第一步与设置共用）：每种语言用它自己的名字显示
FX.LANG_NAMES = { 'zh-CN': '简体中文', 'en-US': 'English' };
FX.langPicker = () => FX.el('div', { class: 'lang-picker', role: 'radiogroup', 'aria-label': FX.t('util.language') },
  FX.languages.map((l) => FX.el('button', { class: `btn ${l === FX.lang ? 'primary' : 'ghost'}`, role: 'radio', 'aria-checked': String(l === FX.lang), 'data-lang': l, lang: l, onclick: () => FX.setLanguage(l) }, FX.LANG_NAMES[l] || l)));
FX.applyI18n();
