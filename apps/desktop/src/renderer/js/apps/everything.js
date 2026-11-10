// Everything 应用窗口：上游应用在本机运行（foxapp:// 协议 + 狐狸OS 本地 Puter 运行时），文件保存在工作空间
'use strict';
(() => {
  const { el, icon } = FX;
  const GROUP_ICON = { office: 'briefcase', collaboration: 'users', creative: 'palette', engineering: 'ruler-2', productivity: 'checklist', finance: 'coin', business: 'building-store', developer: 'api', games: 'chess' };
  FX.groupIcon = (g) => GROUP_ICON[g] || 'app-window';
  FX.evCatalog = null;
  FX.loadEverything = async (force) => { if (!FX.evCatalog || force) FX.evCatalog = await window.foxos.everything.list(); return FX.evCatalog; };
  const appInfo = (id) => FX.evCatalog && FX.evCatalog.apps.find((a) => a.id === id);

  FX.registerApp('everything', {
    title: (p) => (appInfo(p.app) ? appInfo(p.app).name : p.app),
    icon: 'app-window',
    geometry: { w: 1100, h: 700 },
    key: (p) => `everything:${p.app}`,
    mount(body, params, win) {
      const a = appInfo(params.app);
      if (a) win.node.querySelector('.win-icon').replaceChildren(icon(FX.groupIcon(a.group)));
      if (!a || !a.installed) {
        body.append(el('div', { class: 'empty' }, icon('package-off'), el('div', { text: `${a ? a.name : params.app} 尚未安装` }),
          el('div', { class: 'muted small', text: '在应用中心或安装向导里安装（从上游源码在本机构建）。' }),
          el('button', { class: 'btn primary sm', onclick: () => FX.openWindow('appcenter', {}) }, '打开应用中心')));
        return {};
      }
      const view = el('webview', { src: `foxapp://${params.app}/index.html`, partition: `persist:ev-${params.app}`, class: 'webview', allowpopups: true });
      body.append(view);
      view.addEventListener('dom-ready', () => {
        window.foxos.everything.attach(params.app, view.getWebContentsId()).then(() => { if (params.file && !win.fileSent) { win.fileSent = true; window.foxos.everything.openFile(params.app, params.file); } });
      }, { once: false });
      view.addEventListener('page-title-updated', (e) => win.setTitle(`${a.name} — ${e.title}`));
      return { view, persistParams: () => ({ app: params.app }) };
    },
  });

  window.foxos.everything.onOpen(async (appId, file) => { await FX.loadEverything(); FX.openWindow('everything', { app: appId, file }); });
  window.foxos.everything.onClose((appId) => { const w = FX.windows().find((x) => x.key === `everything:${appId}`); if (w) FX.closeWindow(w); });
  window.foxos.everything.onLaunchApp((name) => { if (appInfo(name)) FX.openWindow('everything', { app: name }); });
})();
