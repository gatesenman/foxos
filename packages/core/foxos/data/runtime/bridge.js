// 狐狸OS 应用桥（注入到 Everything 应用页面）：给智能体提供与人相同的操作入口。
// snapshot：可访问性树（可交互元素带稳定引用）；click / focus：按引用操作真实控件；
// modules / invoke：调用应用自身 ES 模块导出的函数（构建时由 vite.foxos.config.mjs 登记）。
(() => {
  'use strict';
  let seq = 0;
  const refs = new Map();
  const INTERACTIVE = 'button, a[href], input, select, textarea, summary, [role=button], [role=menuitem], [role=tab], [role=option], [role=checkbox], [role=switch], [role=link], [role=treeitem], [role=gridcell], [contenteditable=""], [contenteditable=true], [tabindex]:not([tabindex="-1"])';
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const labelOf = (el) => { const id = el.getAttribute('aria-labelledby'); if (id) { const t = id.split(/\s+/).map((x) => document.getElementById(x)?.textContent || '').join(' ').trim(); if (t) return t; } return ''; };
  const nameOf = (el) => (el.tagName === 'SELECT'
    ? (el.getAttribute('aria-label') || labelOf(el) || (el.labels && el.labels[0] && el.labels[0].textContent.replace(el.textContent, '')) || el.getAttribute('title') || el.getAttribute('name') || el.id || '')
    : (el.getAttribute('aria-label') || labelOf(el) || el.getAttribute('title') || (el.labels && el.labels[0] && el.labels[0].textContent) || el.getAttribute('placeholder') || el.getAttribute('alt') || el.textContent || el.value || '')).replace(/\s+/g, ' ').trim().slice(0, 120);
  const roleOf = (el) => el.getAttribute('role') || ({ A: 'link', BUTTON: 'button', SELECT: 'combobox', TEXTAREA: 'textbox', SUMMARY: 'button' }[el.tagName]) || (el.tagName === 'INPUT' ? ({ checkbox: 'checkbox', radio: 'radio', range: 'slider', button: 'button', submit: 'button' }[el.type] || 'textbox') : el.isContentEditable ? 'textbox' : 'generic');
  function refOf(el) { if (!el.dataset.foxosRef) { el.dataset.foxosRef = `e${++seq}`; } refs.set(el.dataset.foxosRef, new WeakRef(el)); return el.dataset.foxosRef; }
  function find(ref) {
    const w = refs.get(ref); const el = w && w.deref();
    if (el && el.isConnected) return el;
    const q = document.querySelector(`[data-foxos-ref="${CSS.escape(ref)}"]`);
    if (!q) throw Object.assign(new Error(`界面元素 ${ref} 已不存在（重新 snapshot）`), { code: 'NOT_FOUND' });
    return q;
  }
  function region(el) { const r = el.closest('[role=dialog], dialog, [role=menu], header, nav, aside, main, footer, [role=toolbar], [aria-label]'); return r && r !== el ? (r.getAttribute('aria-label') || r.getAttribute('role') || r.tagName.toLowerCase()) : null; }
  function describe(ref) {
    const el = ref ? find(ref) : document.activeElement;
    if (!el) return null;
    return { ref: ref || (el.dataset && el.dataset.foxosRef) || null, role: roleOf(el), name: nameOf(el), value: 'value' in el ? String(el.value).slice(0, 500) : el.isContentEditable ? el.textContent.slice(0, 500) : undefined, checked: 'checked' in el ? el.checked : undefined, disabled: Boolean(el.disabled || el.getAttribute('aria-disabled') === 'true'), region: region(el),
      haspopup: el.getAttribute('aria-haspopup') || undefined, expanded: el.getAttribute('aria-expanded') || undefined,
      options: el.tagName === 'SELECT' ? [...el.options].slice(0, 50).map((o) => o.value) : undefined };
  }
  function snapshot({ all = false, limit = 400 } = {}) {
    const out = [];
    for (const el of document.querySelectorAll(INTERACTIVE)) {
      if (!all && !visible(el)) continue;
      out.push(describe(refOf(el)));
      if (out.length >= limit) break;
    }
    const dialogs = [...document.querySelectorAll('[role=dialog], dialog[open]')].filter(visible).map((d) => d.getAttribute('aria-label') || (d.querySelector('h1,h2,h3') || {}).textContent || 'dialog');
    return { title: document.title, url: location.href, dialogs, focused: describe(null), count: out.length, elements: out };
  }
  // 按可访问名称查找控件：先精确匹配，再包含匹配；region 可限定所在区域
  function byName(name, role, reg) {
    const want = String(name || '').toLowerCase();
    const pool = [...document.querySelectorAll(INTERACTIVE)].filter(visible).filter((e) => (!role || roleOf(e) === role) && (!reg || region(e) === reg));
    const el = pool.find((e) => nameOf(e).toLowerCase() === want) || pool.find((e) => nameOf(e).toLowerCase().includes(want));
    if (!el) throw Object.assign(new Error(`没有找到名为「${name}」的控件`), { code: 'NOT_FOUND' });
    return el;
  }
  // 与人一样：控件被弹窗 / 遮罩挡住时不能点（返回 OBSCURED），除非显式 force
  function hittable(el) {
    el.scrollIntoView({ block: 'center', inline: 'center' });
    const r = el.getBoundingClientRect();
    const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return !top || el === top || el.contains(top) || top.contains(el) || (el.labels && [...el.labels].some((l) => l.contains(top)));
  }
  function assertHittable(el, force) {
    if (force || hittable(el)) return;
    const top = document.elementFromPoint(...(() => { const r = el.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })());
    const cover = top && (top.closest('[role=dialog], dialog') || top);
    throw Object.assign(new Error(`「${nameOf(el)}」被${cover && cover.getAttribute ? (cover.getAttribute('aria-label') || cover.getAttribute('role') || cover.tagName.toLowerCase()) : '其他元素'}挡住，先关闭弹窗（或加 force）`), { code: 'CONFLICT' });
  }
  function click({ ref, name, role, region: reg, force }) {
    const el = ref ? find(ref) : byName(name, role, reg);
    assertHittable(el, force);
    el.scrollIntoView({ block: 'center', inline: 'center' });
    const r = el.getBoundingClientRect(); const x = r.left + r.width / 2; const y = r.top + r.height / 2;
    const opts = { bubbles: true, cancelable: true, composed: true, clientX: x, clientY: y, button: 0, view: window };
    el.dispatchEvent(new PointerEvent('pointerdown', { ...opts, pointerId: 1, isPrimary: true }));
    el.dispatchEvent(new MouseEvent('mousedown', opts));
    if (el.focus) el.focus();
    el.dispatchEvent(new PointerEvent('pointerup', { ...opts, pointerId: 1, isPrimary: true }));
    el.dispatchEvent(new MouseEvent('mouseup', opts));
    el.click();
    return describe(refOf(el));
  }
  function focus(ref, clear) {
    const el = ref ? find(ref) : document.activeElement;
    if (!el) throw Object.assign(new Error('没有可输入的元素'), { code: 'NOT_FOUND' });
    el.focus();
    if (clear) { if ('value' in el) { el.value = ''; el.dispatchEvent(new Event('input', { bubbles: true })); } else if (el.isContentEditable) el.textContent = ''; }
    if ('select' in el && !clear && el.type !== 'checkbox') { try { el.setSelectionRange(el.value.length, el.value.length); } catch { /* 不支持 */ } }
    return true;
  }
  function setValue({ ref, name, role, region: reg, value, force }) {
    if (!ref) ref = refOf(byName(name, role, reg));
    const el = find(ref);
    assertHittable(el, force);
    if (el.tagName === 'SELECT') { el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return describe(ref); }
    if (el.type === 'checkbox' || el.type === 'radio') { if (Boolean(value) !== el.checked) el.click(); return describe(ref); }
    const proto = Object.getPrototypeOf(el); const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
    if (setter) setter.call(el, value); else el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true }));
    return describe(ref);
  }
  const mods = () => globalThis.__foxosModules || {};
  function modules() { return Object.fromEntries(Object.entries(mods()).map(([k, ns]) => [k, Object.keys(ns).map((n) => `${n}:${typeof ns[n]}`)])); }
  function resolve(target) {
    const [file, ...pathParts] = String(target).split('#');
    const ns = mods()[file];
    if (!ns) throw Object.assign(new Error(`应用模块 ${file} 不存在（是否用狐狸OS 构建安装？）`), { code: 'NOT_FOUND' });
    let obj = ns; let parent = null;
    for (const p of (pathParts[0] || '').split('.').filter(Boolean)) { parent = obj; obj = obj[p]; if (obj == null) throw Object.assign(new Error(`${target} 不存在`), { code: 'NOT_FOUND' }); }
    return { obj, parent };
  }
  const plain = (v, d = 0) => {
    if (v == null || typeof v !== 'object') return typeof v === 'function' ? `[function ${v.name}]` : v;
    if (d > 6) return '[…]';
    if (v instanceof Map) return Object.fromEntries([...v].slice(0, 500).map(([k, x]) => [String(k), plain(x, d + 1)]));
    if (v instanceof Set) return [...v].slice(0, 500).map((x) => plain(x, d + 1));
    if (Array.isArray(v)) return v.slice(0, 1000).map((x) => plain(x, d + 1));
    if (v instanceof Node) return `[${v.nodeName}]`;
    const o = {}; for (const k of Object.keys(v).slice(0, 300)) o[k] = plain(v[k], d + 1); return o;
  };
  async function invoke({ target, args = [] }) { const { obj, parent } = resolve(target); if (typeof obj !== 'function') return plain(obj); return plain(await obj.apply(parent, args)); }
  function read({ target }) { return plain(resolve(target).obj); }
  // 键盘：在焦点元素（或按名称找到的元素）上派发真实的 keydown / keyup 事件；mod 在 macOS 上是 Meta，其他平台是 Ctrl
  function press({ key, name, role, ref }) {
    const el = ref ? find(ref) : name ? byName(name, role) : (document.activeElement || document.body);
    if (el && el.focus) el.focus();
    const parts = String(key).split('+'); const k = parts.pop();
    const mac = /Mac/.test(navigator.platform);
    const m = new Set(parts.map((x) => x.toLowerCase()));
    const init = { key: k.length === 1 ? k : k[0].toUpperCase() + k.slice(1), bubbles: true, cancelable: true, composed: true,
      ctrlKey: m.has('ctrl') || (m.has('mod') && !mac), metaKey: m.has('meta') || (m.has('mod') && mac), shiftKey: m.has('shift'), altKey: m.has('alt') };
    if (k.length === 1) init.code = /[a-z]/i.test(k) ? `Key${k.toUpperCase()}` : undefined;
    const t = el || document.body;
    const ok = t.dispatchEvent(new KeyboardEvent('keydown', init));
    if (ok && init.key === 'Enter' && t.form && !init.ctrlKey && !init.metaKey) t.form.requestSubmit ? t.form.requestSubmit() : t.form.submit();
    t.dispatchEvent(new KeyboardEvent('keyup', init));
    return { key, target: describe(refOf(t)) };
  }
  async function run({ steps = [] }) {
    const results = [];
    for (const s of steps) {
      if (s.click) results.push(click(s.click));
      else if (s.set) results.push(setValue(s.set));
      else if (s.invoke) results.push(await invoke(s.invoke));
      else if (s.press) results.push(press(s.press));
      else if (s.wait) await new Promise((r) => setTimeout(r, Math.min(5000, s.wait)));
      await new Promise((r) => setTimeout(r, 60));
    }
    return results;
  }
  const api = { snapshot, click, focus, describe, setValue, press, hittable: ({ ref }) => hittable(find(ref)), modules, invoke, read, run, text: () => document.body.innerText.slice(0, 20000) };
  window.__foxosBridge = {
    ...api,
    call: async (m, p) => { if (!api[m]) throw new Error(`未知桥方法 ${m}`); return api[m](p || {}); },
  };
})();
