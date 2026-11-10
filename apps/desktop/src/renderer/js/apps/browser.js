// 浏览器：Electron webview（Chromium），独立隔离，不注入任何桌面接口
'use strict';
(() => {
  const { el, icon } = FX;
  const HOME = 'https://duckduckgo.com/';

  function normalize(input) {
    const s = input.trim();
    if (!s) return 'about:blank';
    if (/^(https?|file):\/\//i.test(s) || s === 'about:blank') return s;
    if (/^[\w-]+(\.[\w-]+)+(:\d+)?(\/.*)?$/.test(s) || /^localhost(:\d+)?/.test(s)) return `${/^localhost/.test(s) ? 'http' : 'https'}://${s}`;
    return `https://duckduckgo.com/?q=${encodeURIComponent(s)}`;
  }

  FX.registerApp('browser', {
    title: () => '浏览器',
    icon: 'world',
    geometry: { w: 980, h: 620 },
    mount(body, params, win) {
      const url = el('input', { class: 'input url', spellcheck: 'false', value: params.url || HOME });
      const view = el('webview', { src: normalize(params.url || HOME), partition: 'persist:browser', allowpopups: true, plugins: true, class: 'webview' });
      const nav = (ic, title, fn) => el('button', { class: 'icon-btn', title, onclick: fn }, icon(ic));
      const progress = el('div', { class: 'loadbar hidden' });
      body.append(
        el('form', { class: 'toolbar', onsubmit: (e) => { e.preventDefault(); view.loadURL(normalize(url.value)); } },
          nav('arrow-left', '后退', () => view.canGoBack() && view.goBack()),
          nav('arrow-right', '前进', () => view.canGoForward() && view.goForward()),
          nav('refresh', '刷新', () => view.reload()),
          nav('home', '主页', () => view.loadURL(HOME)),
          url),
        progress, view);
      view.addEventListener('did-start-loading', () => progress.classList.remove('hidden'));
      view.addEventListener('did-stop-loading', () => progress.classList.add('hidden'));
      view.addEventListener('did-navigate', (e) => { url.value = e.url; win.params = { url: e.url }; FX.saveSession(); });
      view.addEventListener('did-navigate-in-page', (e) => { if (e.isMainFrame) url.value = e.url; });
      view.addEventListener('page-title-updated', (e) => win.setTitle(`浏览器 — ${e.title}`));
      view.addEventListener('did-fail-load', (e) => { if (e.errorCode !== -3) FX.toast(`无法打开 ${e.validatedURL}：${e.errorDescription}`, 'error'); });
      return { view, persistParams: () => ({ url: url.value }), navigate: (u) => view.loadURL(normalize(u)) };
    },
  });
})();
