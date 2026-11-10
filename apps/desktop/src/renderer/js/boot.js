// 启动：读取环境、检测软件、桌面图标、开始菜单、搜索、人工接管、会话恢复
'use strict';
(async () => {
  const { el, icon, $ } = FX;
  window.addEventListener('error', (e) => window.foxos.log(`${e.message} @ ${e.filename}:${e.lineno}`));
  window.addEventListener('unhandledrejection', (e) => window.foxos.log(`未处理的 Promise 错误：${e.reason && (e.reason.stack || e.reason.message || e.reason)}`));

  FX.env = await window.foxos.env();
  $('#ws-path').textContent = FX.env.workspace;
  $('#ws-chip').addEventListener('click', () => FX.openWindow('files', { path: '' }));

  FX.detectApps = async (force = false) => {
    if (!FX.apps || force) FX.apps = await window.foxos.detectApps();
    return FX.apps;
  };

  const LAUNCHERS = [
    { id: 'files', name: '文件', icon: 'folder', run: () => FX.openWindow('files', { path: '' }) },
    { id: 'terminal', name: '终端', icon: 'terminal-2', run: () => FX.openWindow('terminal', {}) },
    { id: 'editor', name: '编辑器', icon: 'code', run: () => FX.openWindow('editor', {}) },
    { id: 'browser', name: '浏览器', icon: 'world', run: () => FX.openWindow('browser', {}) },
    { id: 'writer', name: 'Writer', icon: 'file-text', office: true, run: () => FX.launchOffice('writer') },
    { id: 'calc', name: 'Calc', icon: 'file-spreadsheet', office: true, run: () => FX.launchOffice('calc') },
    { id: 'impress', name: 'Impress', icon: 'presentation', office: true, run: () => FX.launchOffice('impress') },
    { id: 'environments', name: '环境', icon: 'box-multiple', run: () => FX.openWindow('environments', {}) },
    { id: 'appcenter', name: '应用中心', icon: 'apps', run: () => FX.openWindow('appcenter', {}) },
    { id: 'settings', name: '设置', icon: 'settings', run: () => FX.openWindow('settings', {}) },
  ];
  FX.launchers = LAUNCHERS;

  function officeInstalled(id) { const o = FX.apps && FX.apps.office.find((x) => x.id === id); return !o || o.installed; }

  function renderDesktopIcons() {
    $('#desktop-icons').replaceChildren(...LAUNCHERS.map((l) => el('button', {
      class: `desk-icon ${l.office && !officeInstalled(l.id) ? 'missing' : ''}`, 'data-launch': l.id, title: l.office && !officeInstalled(l.id) ? '未安装' : l.name,
      ondblclick: () => l.run(), onkeydown: (e) => { if (e.key === 'Enter') l.run(); },
    }, el('span', { class: 'desk-icon-img' }, icon(l.icon)), el('span', { text: l.name }))));
  }

  // 开始菜单
  const menu = $('#start-menu');
  function renderStart() {
    menu.replaceChildren(
      el('div', { class: 'start-head' }, el('img', { src: 'icon-64.png', alt: '' }), el('div', {}, el('b', { text: '狐狸OS' }), el('div', { class: 'muted small', text: FX.env.workspace }))),
      el('div', { class: 'start-grid' }, LAUNCHERS.map((l) => el('button', { class: `start-app ${l.office && !officeInstalled(l.id) ? 'missing' : ''}`, 'data-launch': l.id, onclick: () => { hideStart(); l.run(); } },
        icon(l.icon), el('span', { text: l.name }), l.office && !officeInstalled(l.id) ? el('span', { class: 'badge warn', text: '未安装' }) : null))),
      evStart(),
      el('div', { class: 'start-foot' },
        el('button', { class: 'btn ghost sm', onclick: () => { hideStart(); FX.openWindow('setup', {}); } }, icon('wand'), '安装向导'),
        el('div', { class: 'spacer' }),
        el('span', { class: 'muted small', text: `${FX.env.platform}-${FX.env.arch} · v${FX.env.versions.app}` })));
  }
  // 开始菜单里的 Everything 应用：只列出本机已安装的，按上游分组
  function evStart() {
    const c = FX.evCatalog; if (!c) return null;
    const groups = c.groups.map((g) => ({ g, apps: c.apps.filter((a) => a.group === g.id && a.installed) })).filter((x) => x.apps.length);
    if (!groups.length) return el('div', { class: 'start-ev muted small', text: 'Everything 应用尚未安装（应用中心 → Everything 应用）' });
    return el('div', { class: 'start-ev scroll' }, groups.map(({ g, apps }) => el('div', { class: 'start-ev-group', 'data-group': g.id },
      el('div', { class: 'muted small' }, icon(FX.groupIcon(g.id)), ` ${g.zh}`),
      el('div', { class: 'start-ev-apps' }, apps.map((a) => el('button', { class: 'start-ev-app', 'data-ev-launch': a.id, onclick: () => { hideStart(); FX.openWindow('everything', { app: a.id }); } }, a.name))))));
  }
  FX.on('everything-changed', () => FX.loadEverything(true).catch(() => {}));
  FX.loadEverything().catch(() => {});
  function hideStart() { menu.classList.add('hidden'); }
  $('#start').addEventListener('click', (e) => { e.stopPropagation(); renderStart(); menu.classList.toggle('hidden'); });
  document.addEventListener('pointerdown', (e) => { if (!menu.contains(e.target) && !$('#start').contains(e.target)) hideStart(); });

  // 搜索：应用 + 工作空间文件（真实文件列表）
  const pal = $('#palette');
  const results = $('#palette-results');
  let palTimer = null;
  pal.addEventListener('input', () => { clearTimeout(palTimer); palTimer = setTimeout(search, 150); });
  pal.addEventListener('keydown', (e) => { if (e.key === 'Escape') { pal.value = ''; results.classList.add('hidden'); } if (e.key === 'Enter') { const f = results.querySelector('button'); if (f) f.click(); } });
  async function search() {
    const q = pal.value.trim().toLowerCase();
    if (!q) { results.classList.add('hidden'); return; }
    const apps = LAUNCHERS.filter((l) => l.name.toLowerCase().includes(q) || l.id.includes(q));
    let files = [];
    try { files = (await FX.k(['files', 'list', '-r'])).entries.filter((f) => f.path.toLowerCase().includes(q)).slice(0, 12); } catch { /* 忽略 */ }
    const done = () => { pal.value = ''; results.classList.add('hidden'); };
    results.replaceChildren(
      ...apps.map((l) => el('button', { onclick: () => { done(); l.run(); } }, icon(l.icon), l.name, el('span', { class: 'muted small', text: '应用' }))),
      ...files.map((f) => el('button', { onclick: () => { done(); FX.openPath(f.path, f.type); } }, icon(FX.fileKind(f.name, f.type).icon), f.path, el('span', { class: 'muted small', text: FX.fileKind(f.name, f.type).label }))),
      ...(apps.length || files.length ? [] : [el('div', { class: 'muted small', text: '没有匹配的应用或文件' })]));
    results.classList.remove('hidden');
  }

  // 人工接管
  const tk = $('#takeover');
  async function refreshControl() {
    try {
      const st = await FX.k(['control', 'status']);
      tk.classList.toggle('on', st.paused);
      tk.querySelector('span').textContent = st.paused ? '恢复智能体' : '人工接管';
      tk.title = st.paused ? `已暂停（${st.state.by}，${st.state.since}）。点击恢复` : '暂停所有智能体的写操作';
      $('#tray-paused').classList.toggle('hidden', !st.paused);
      document.body.classList.toggle('paused', st.paused);
    } catch { /* 忽略 */ }
  }
  tk.addEventListener('click', async () => {
    try {
      const st = await FX.k(['control', 'status']);
      await FX.k(st.paused ? ['control', 'resume'] : ['control', 'pause', '--reason', '桌面人工接管']);
      FX.toast(st.paused ? '已恢复：智能体可以继续写入' : '已人工接管：智能体写操作暂停', 'ok');
    } catch (e) { FX.toast(e.message, 'error'); }
    refreshControl();
  });

  $('#open-settings').addEventListener('click', () => FX.openWindow('settings', {}));
  $('#toggle-panel').addEventListener('click', () => $('#panel').classList.toggle('collapsed'));

  // 工作空间变化（来自 CLI / MCP / ACP / 终端）
  window.foxos.onFsChanged((ev) => {
    if (ev.paths.length) FX.emit('fs', ev);
    if (ev.audit) { FX.emit('audit', ev); refreshControl(); }
  });

  // 时钟
  const tick = () => { const d = new Date(); $('#clock').textContent = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`; };
  tick(); setInterval(tick, 10000);

  renderDesktopIcons();
  FX.renderTaskbar();
  refreshControl();
  FX.detectApps().then(renderDesktopIcons).catch((e) => FX.toast(`检测软件失败：${e.message}`, 'error'));
  FX.refreshNative();

  // 恢复上次的窗口
  try {
    const sess = await window.foxos.session.load();
    for (const w of sess.windows || []) {
      if (!FX.appDef(w.app) || w.params == null) continue;
      try { FX.openWindow(w.app, w.params, w.geom); } catch { /* 忽略 */ }
    }
  } catch { /* 忽略 */ }
  if (!FX.env.setupDone && !FX.env.screenshot) FX.openWindow('setup', {});
  document.body.classList.add('ready');
  window.foxos.ready();
})();
