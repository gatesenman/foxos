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
    title: () => FX.t('common.browser'),
    icon: 'world',
    geometry: { w: 980, h: 620 },
    mount(body, params, win) {
      const url = el('input', { class: 'input url', spellcheck: 'false', value: params.url || HOME });
      const view = el('webview', { src: normalize(params.url || HOME), partition: 'persist:browser', allowpopups: true, plugins: true, class: 'webview' });
      const nav = (ic, title, fn) => el('button', { class: 'icon-btn', title, onclick: fn }, icon(ic));
      const progress = el('div', { class: 'loadbar hidden' });
      body.append(
        el('form', { class: 'toolbar', onsubmit: (e) => { e.preventDefault(); view.loadURL(normalize(url.value)); } },
          nav('arrow-left', FX.t('common.back'), () => view.canGoBack() && view.goBack()),
          nav('arrow-right', FX.t('browser.forward'), () => view.canGoForward() && view.goForward()),
          nav('refresh', FX.t('common.refresh'), () => view.reload()),
          nav('home', FX.t('browser.home'), () => view.loadURL(HOME)),
          url),
        progress, view);
      view.addEventListener('did-start-loading', () => progress.classList.remove('hidden'));
      view.addEventListener('did-stop-loading', () => progress.classList.add('hidden'));
      view.addEventListener('did-navigate', (e) => { url.value = e.url; win.params = { url: e.url }; FX.saveSession(); });
      view.addEventListener('did-navigate-in-page', (e) => { if (e.isMainFrame) url.value = e.url; });
      view.addEventListener('page-title-updated', (e) => win.setTitle(FX.t('browser.browser', e.title)));
      view.addEventListener('did-fail-load', (e) => { if (e.errorCode !== -3) FX.toast(FX.t('browser.cannot_open', e.validatedURL, e.errorDescription), 'error'); });
      return { view, persistParams: () => ({ url: url.value }), navigate: (u) => view.loadURL(normalize(u)) };
    },
  });
})();
