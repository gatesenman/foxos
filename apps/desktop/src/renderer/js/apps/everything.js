// Everything 应用窗口：上游应用在本机运行（foxapp:// 协议 + 狐狸OS 本地 Puter 运行时），文件保存在工作空间
'use strict';
(() => {
  const { el, icon } = FX;
  const GROUP_ICON = { office: 'briefcase', collaboration: 'users', creative: 'palette', engineering: 'ruler-2', productivity: 'checklist', finance: 'coin', business: 'building-store', developer: 'api', games: 'chess' };
  FX.groupIcon = (g) => GROUP_ICON[g] || 'app-window';
  // 分组名与应用说明随界面语言（词条 ev.group.* / ev.desc.* / ev.issue.*；应用名保持上游名称）
  FX.groupName = (g) => FX.t(`ev.group.${g.id || g}`);
  FX.evDesc = (a) => (FX.has(`ev.desc.${a.id}`) ? FX.t(`ev.desc.${a.id}`) : a.description || '');
  FX.evIssue = (a) => (a.upstreamIssue ? (FX.has(`ev.issue.${a.id}`) ? FX.t(`ev.issue.${a.id}`) : a.upstreamIssue) : null);
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
      if (a) { win.iconSpec = FX.evIcon(a); win.node.querySelector('.win-icon').replaceChildren(FX.appIcon(win.iconSpec)); FX.renderTaskbar(); }
      if (FX.env.mode === 'client') {
        // 客户端模式：Everything 应用在狐狸OS 电脑的桌面上打开，这里只给出状态
        const msg = el('div', { class: 'muted', text: FX.t('client.opening_in_guest', a ? a.name : params.app) });
        body.append(el('div', { class: 'empty', 'data-guest-open': params.app }, icon('device-desktop'), msg,
          el('button', { class: 'btn', onclick: () => FX.openWindow('computer', {}) }, icon('device-desktop'), FX.t('client.computer_title'))));
        window.foxos.everything.openInGuest(params.app, params.file || null)
          .then(() => { msg.textContent = FX.t('client.opened_in_guest', a ? a.name : params.app); FX.openWindow('computer', {}); })
          .catch((e) => { msg.textContent = e.message; msg.classList.add('error'); });
        return;
      }
      if (!a || !a.installed) {
        body.append(el('div', { class: 'empty' }, icon('package-off'), el('div', { text: FX.t('everything.is_not_installed', a ? a.name : params.app) }),
          el('div', { class: 'muted small', text: FX.t('everything.install_it_from_the_app_center_or') }),
          el('button', { class: 'btn primary sm', onclick: () => FX.openWindow('appcenter', {}) }, FX.t('common.open_app_center'))));
        return {};
      }
      const view = el('webview', { src: `foxapp://${params.app}/index.html`, partition: a.partition, class: 'webview', allowpopups: true });
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
