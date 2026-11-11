// 智能体：OpenBot 式的多智能体聊天（主智能体 + 其它智能体）。界面由内核的 foxos bot serve 提供，
// 与狐狸OS 里的独立「智能体」窗口相同；这里以窗口形式合并在桌面里。
'use strict';
(() => {
  const { el } = FX;
  FX.registerApp('bots', {
    title: () => FX.t('bots.title'),
    icon: 'sparkles',
    geometry: { w: 1100, h: 720 },
    key: () => 'bots',
    mount(body, params) {
      const msg = el('div', { class: 'muted small pad', text: FX.t('bots.starting') });
      body.append(msg);
      window.foxos.bots.url().then(({ url }) => {
        const hash = params.bot ? `#bot/${encodeURIComponent(params.bot)}` : '';
        const view = el('webview', { src: url + hash, partition: 'persist:bots', class: 'webview' });
        view.addEventListener('did-fail-load', (e) => { if (e.errorCode !== -3) FX.toast(FX.t('bots.cannot_open', e.errorDescription), 'error'); });
        msg.replaceWith(view);
      }).catch((e) => { msg.textContent = FX.t('bots.cannot_start', e.message); });
      return {};
    },
  });
})();
