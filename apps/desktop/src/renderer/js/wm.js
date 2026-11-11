// 桌面窗口管理：拖动、八向缩放、最小化、最大化、关闭、层级、任务栏、会话保存
'use strict';
(() => {
  const { el, icon, $ } = FX;
  const wins = new Map();
  let z = 10;
  let seq = 1;
  const apps = {};

  FX.registerApp = (id, def) => { apps[id] = def; };
  FX.appDef = (id) => apps[id];

  function desktopRect() { return $('#desktop').getBoundingClientRect(); }

  function focus(w) {
    for (const o of wins.values()) o.node.classList.remove('focused');
    w.node.classList.add('focused');
    w.node.style.zIndex = String(++z);
    FX.renderTaskbar();
  }

  function clamp(w) {
    const r = desktopRect();
    const n = w.node;
    n.style.left = `${Math.max(0, Math.min(n.offsetLeft, r.width - 120))}px`;
    n.style.top = `${Math.max(0, Math.min(n.offsetTop, r.height - 40))}px`;
  }

  function startDrag(w, e) {
    if (e.button !== 0 || e.target.closest('button') || w.state === 'maximized') return;
    e.preventDefault();
    const sx = e.clientX; const sy = e.clientY; const ox = w.node.offsetLeft; const oy = w.node.offsetTop;
    document.body.classList.add('dragging');
    const move = (ev) => { w.node.style.left = `${ox + ev.clientX - sx}px`; w.node.style.top = `${Math.max(0, oy + ev.clientY - sy)}px`; };
    const up = () => { removeEventListener('pointermove', move); removeEventListener('pointerup', up); document.body.classList.remove('dragging'); clamp(w); FX.saveSession(); };
    addEventListener('pointermove', move); addEventListener('pointerup', up);
  }

  function startResize(w, dir, e) {
    if (w.state === 'maximized') return;
    e.preventDefault(); e.stopPropagation();
    const n = w.node;
    const s = { x: e.clientX, y: e.clientY, l: n.offsetLeft, t: n.offsetTop, w: n.offsetWidth, h: n.offsetHeight };
    const minW = 320; const minH = 200;
    document.body.classList.add('dragging');
    const move = (ev) => {
      const dx = ev.clientX - s.x; const dy = ev.clientY - s.y;
      if (dir.includes('e')) n.style.width = `${Math.max(minW, s.w + dx)}px`;
      if (dir.includes('s')) n.style.height = `${Math.max(minH, s.h + dy)}px`;
      if (dir.includes('w')) { const nw = Math.max(minW, s.w - dx); n.style.width = `${nw}px`; n.style.left = `${s.l + s.w - nw}px`; }
      if (dir.includes('n')) { const nh = Math.max(minH, s.h - dy); n.style.height = `${nh}px`; n.style.top = `${Math.max(0, s.t + s.h - nh)}px`; }
      w.onResize && w.onResize();
    };
    const up = () => { removeEventListener('pointermove', move); removeEventListener('pointerup', up); document.body.classList.remove('dragging'); w.onResize && w.onResize(); FX.saveSession(); };
    addEventListener('pointermove', move); addEventListener('pointerup', up);
  }

  function setState(w, state) {
    const n = w.node;
    if (state === 'maximized' && w.state !== 'maximized') {
      w.restore = { left: n.style.left, top: n.style.top, width: n.style.width, height: n.style.height };
      n.classList.add('maximized');
    }
    if (state === 'normal' && w.state === 'maximized' && w.restore) {
      n.classList.remove('maximized');
      Object.assign(n.style, w.restore);
    }
    if (state === 'minimized') n.classList.add('minimized'); else n.classList.remove('minimized');
    if (state !== 'minimized') w.prevState = state;
    w.state = state;
    n.dataset.state = state;
    setTimeout(() => w.onResize && w.onResize(), 30);
    if (state !== 'minimized') focus(w); else FX.renderTaskbar();
    FX.saveSession();
  }

  // 打开一个应用窗口。key 相同则复用（例如同一文件只开一个编辑器窗口）
  FX.openWindow = (appId, params = {}, geom = null) => {
    const def = apps[appId];
    if (!def) throw new Error(`未知应用 ${appId}`);
    const key = def.key ? def.key(params) : null;
    if (key) {
      const existing = [...wins.values()].find((w) => w.key === key);
      if (existing) { if (existing.state === 'minimized') setState(existing, existing.prevState || 'normal'); else focus(existing); return existing; }
    }
    const r = desktopRect();
    const g = geom || def.geometry || { w: 760, h: 480 };
    const offset = (wins.size % 6) * 28;
    const id = `w${seq++}`;
    const titleEl = el('span', { class: 'win-title-text', text: def.title(params) });
    const body = el('div', { class: 'win-body' });
    const node = el('div', { class: 'window', 'data-app': appId, 'data-id': id, style: {
      left: `${g.x ?? Math.max(8, Math.min(r.width - g.w - 8, 80 + offset))}px`,
      top: `${g.y ?? Math.max(8, Math.min(r.height - g.h - 8, 30 + offset))}px`,
      width: `${Math.min(g.w, r.width - 16)}px`, height: `${Math.min(g.h, r.height - 16)}px`,
    } },
    el('div', { class: 'win-titlebar' },
      el('span', { class: 'win-icon' }, FX.appIcon(FX.programIcon(appId, def.icon))), titleEl,
      el('span', { class: 'win-controls' },
        el('button', { class: 'wc min', title: '最小化', 'data-action': 'minimize' }, icon('minus')),
        el('button', { class: 'wc max', title: '最大化 / 还原', 'data-action': 'maximize' }, icon('square')),
        el('button', { class: 'wc close', title: '关闭', 'data-action': 'close' }, icon('x')))),
    body,
    ...['n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'].map((d) => el('div', { class: `rz rz-${d}`, 'data-dir': d })));
    const w = { id, appId, key, params, node, body, state: 'normal', prevState: 'normal', setTitle: (t) => { titleEl.textContent = t; FX.renderTaskbar(); }, title: () => titleEl.textContent };
    wins.set(id, w);
    $('#desktop').append(node);
    node.addEventListener('pointerdown', () => { if (!node.classList.contains('focused')) focus(w); }, true);
    $('.win-titlebar', node).addEventListener('pointerdown', (e) => startDrag(w, e));
    $('.win-titlebar', node).addEventListener('dblclick', (e) => { if (!e.target.closest('button')) setState(w, w.state === 'maximized' ? 'normal' : 'maximized'); });
    for (const h of node.querySelectorAll('.rz')) h.addEventListener('pointerdown', (e) => startResize(w, h.dataset.dir, e));
    $('.win-controls', node).addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.action === 'minimize') setState(w, 'minimized');
      if (b.dataset.action === 'maximize') setState(w, w.state === 'maximized' ? 'normal' : 'maximized');
      if (b.dataset.action === 'close') FX.closeWindow(w);
    });
    focus(w);
    try {
      const api = def.mount(body, params, w) || {};
      Object.assign(w, api);
    } catch (err) {
      body.append(el('div', { class: 'empty error' }, icon('alert-triangle'), el('div', { text: `无法启动：${err.message}` })));
    }
    if (g.state === 'maximized') setState(w, 'maximized');
    if (g.state === 'minimized') setState(w, 'minimized');
    FX.saveSession();
    return w;
  };

  FX.closeWindow = async (w) => {
    if (w.beforeClose && (await w.beforeClose()) === false) return;
    try { w.dispose && w.dispose(); } catch { /* 忽略 */ }
    w.node.remove();
    wins.delete(w.id);
    FX.renderTaskbar();
    FX.saveSession();
  };

  FX.windows = () => [...wins.values()];
  FX.focusWindow = (w) => { if (w.state === 'minimized') setState(w, w.prevState || 'normal'); else focus(w); };
  FX.setWindowState = setState;

  // 会话保存：窗口、位置、状态、参数（重启后恢复）
  let saveTimer = null;
  FX.saveSession = () => {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      const list = FX.windows().filter((w) => apps[w.appId].persist !== false).map((w) => {
        const n = w.node;
        const geom = w.state === 'maximized' && w.restore
          ? { x: parseInt(w.restore.left, 10), y: parseInt(w.restore.top, 10), w: parseInt(w.restore.width, 10), h: parseInt(w.restore.height, 10) }
          : { x: n.offsetLeft, y: n.offsetTop, w: n.offsetWidth, h: n.offsetHeight };
        return { app: w.appId, params: w.persistParams ? w.persistParams() : w.params, geom: { ...geom, state: w.state } };
      });
      window.foxos.session.save({ windows: list }).catch(() => {});
    }, 300);
  };

  // 任务栏：内置窗口 + 真实的 LibreOffice 原生窗口
  FX.nativeWindows = [];
  FX.renderTaskbar = () => {
    const box = $('#task-items');
    if (!box) return;
    box.replaceChildren();
    for (const w of FX.windows()) {
      const def = apps[w.appId];
      const active = w.node.classList.contains('focused') && w.state !== 'minimized';
      box.append(el('button', {
        class: `task ${active ? 'active' : ''} ${w.state === 'minimized' ? 'min' : ''}`, title: w.title(), 'data-win': w.id, 'data-app': w.appId,
        onclick: () => { if (active) setState(w, 'minimized'); else FX.focusWindow(w); },
      }, w.iconSpec ? FX.appIcon(w.iconSpec) : FX.appIcon(FX.programIcon(w.appId, def.icon)), el('span', { text: w.title() })));
    }
    for (const nw of FX.nativeWindows) {
      box.append(el('button', {
        class: 'task native', title: `${nw.title}（原生窗口）`, 'data-native': nw.wid,
        onclick: () => window.foxos.office.focus(nw.wid).catch(() => {}),
      }, FX.appIcon(FX.programIcon(/Calc/.test(nw.title) ? 'calc' : /Impress/.test(nw.title) ? 'impress' : 'writer')), el('span', { text: nw.title }), el('i', { class: 'ti ti-external-link native-mark' })));
    }
  };
})();
