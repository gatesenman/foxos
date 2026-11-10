// 通用工具：DOM 构造、图标、弹窗、文件类型
'use strict';
window.FX = window.FX || {};

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
  if (type === 'dir') return { icon: 'folder', opener: 'files', label: '文件夹' };
  const e = FX.ext(name);
  if (['xlsx', 'xls', 'ods'].includes(e)) return { icon: 'file-spreadsheet', opener: 'calc', label: '表格' };
  if (['docx', 'doc', 'odt', 'rtf'].includes(e)) return { icon: 'file-text', opener: 'writer', label: '文档' };
  if (['pptx', 'ppt', 'odp'].includes(e)) return { icon: 'presentation', opener: 'impress', label: '演示' };
  if (e === 'pdf') return { icon: 'file-type-pdf', opener: 'browser', label: 'PDF' };
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(e)) return { icon: 'photo', opener: 'browser', label: '图片' };
  if (['html', 'htm'].includes(e)) return { icon: 'file-code', opener: 'editor', label: '网页', alt: 'browser' };
  if (e === 'csv' || e === 'tsv') return { icon: 'file-spreadsheet', opener: 'editor', label: 'CSV', alt: 'calc' };
  if (TEXT_EXT.has(e) || !e) return { icon: e === 'md' ? 'markdown' : ['js', 'ts', 'py', 'sh', 'json', 'css', 'rs', 'go'].includes(e) ? 'file-code' : 'file', opener: 'editor', label: '文本' };
  return { icon: 'file', opener: 'editor', label: e.toUpperCase() };
};

// 调用内核：成功返回 result，失败抛出带 code 的错误
FX.k = async (args, opts) => {
  const r = await window.foxos.run(args, opts);
  if (r.ok) return r.data ? r.data.result : r.stdout;
  const err = r.data && r.data.error;
  const e = new Error(err ? err.message : (r.stderr || `退出码 ${r.exitCode}`));
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
FX.prompt = (title, { value = '', placeholder = '', okText = '确定' } = {}) => new Promise((resolve) => {
  const input = FX.el('input', { class: 'input', value, placeholder });
  const close = (v) => { overlay.remove(); resolve(v); };
  const overlay = FX.el('div', { class: 'overlay' },
    FX.el('form', { class: 'dialog', onsubmit: (e) => { e.preventDefault(); close(input.value.trim() || null); } },
      FX.el('div', { class: 'dialog-title', text: title }), input,
      FX.el('div', { class: 'dialog-actions' },
        FX.el('button', { type: 'button', class: 'btn ghost', onclick: () => close(null) }, '取消'),
        FX.el('button', { type: 'submit', class: 'btn primary' }, okText))));
  FX.$('#modal-root').append(overlay);
  input.focus();
  input.select();
});

FX.confirm = (title, body, { okText = '确定', danger = false } = {}) => new Promise((resolve) => {
  const close = (v) => { overlay.remove(); resolve(v); };
  const overlay = FX.el('div', { class: 'overlay' },
    FX.el('div', { class: 'dialog' },
      FX.el('div', { class: 'dialog-title', text: title }), FX.el('div', { class: 'dialog-body', text: body }),
      FX.el('div', { class: 'dialog-actions' },
        FX.el('button', { class: 'btn ghost', onclick: () => close(false) }, '取消'),
        FX.el('button', { class: `btn ${danger ? 'danger' : 'primary'}`, onclick: () => close(true) }, okText))));
  FX.$('#modal-root').append(overlay);
});

// 简单事件总线
FX.bus = new EventTarget();
FX.emit = (name, detail) => FX.bus.dispatchEvent(new CustomEvent(name, { detail }));
FX.on = (name, fn) => FX.bus.addEventListener(name, (e) => fn(e.detail));
