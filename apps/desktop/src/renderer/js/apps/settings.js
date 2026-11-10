// 设置：工作空间、Python、智能体 API 密钥（加密保存，作为环境变量传给 ACP 智能体）
'use strict';
(() => {
  const { el, icon } = FX;
  const KNOWN = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'DASHSCOPE_API_KEY', 'OPENROUTER_API_KEY', 'DEEPSEEK_API_KEY'];

  FX.registerApp('settings', {
    title: () => '设置',
    icon: 'settings',
    geometry: { w: 700, h: 560 },
    key: () => 'settings',
    mount(body) {
      const root = el('div', { class: 'settings scroll' });
      body.append(root);
      async function render() {
        const s = await window.foxos.settings.get();
        const env = FX.env;
        const keyName = el('input', { class: 'input', list: 'known-keys', placeholder: '环境变量名，例如 ANTHROPIC_API_KEY' });
        const keyVal = el('input', { class: 'input', type: 'password', placeholder: '值（留空表示删除）' });
        const py = el('input', { class: 'input mono', value: s.python || '', placeholder: env.python });
        root.replaceChildren(
          el('section', {}, el('h3', { text: '工作空间' }),
            el('div', { class: 'row' }, el('code', { class: 'grow', text: env.workspace }),
              el('button', { class: 'btn ghost sm', onclick: async () => {
                const d = await window.foxos.chooseDir(); if (!d) return;
                await window.foxos.settings.set({ workspace: d });
                if (await FX.confirm('切换工作空间', `需要重启桌面才能切换到 ${d}。现在重启？`, { okText: '重启' })) window.foxos.relaunch();
              } }, '更改…'))),
          el('section', {}, el('h3', { text: 'Python 解释器（foxos 内核）' }),
            el('div', { class: 'row' }, py, el('button', { class: 'btn ghost sm', onclick: async () => { await window.foxos.settings.set({ python: py.value.trim() || null }); FX.toast('已保存，重启后生效', 'ok'); } }, '保存')),
            el('div', { class: 'muted small', text: `当前使用：${env.python}` })),
          el('section', {}, el('h3', { text: '智能体密钥' }),
            el('p', { class: 'muted small', text: `密钥以环境变量的形式传给你启动的 ACP 智能体，不写入工作空间。加密方式：${env.encryption.available ? `系统钥匙串（${env.encryption.backend}）` : '系统不支持加密存储，以明文保存在用户数据目录'}` }),
            el('div', { class: 'key-list' }, s.secrets.length ? s.secrets.map((n) => el('div', { class: 'row' }, icon('key'), el('code', { class: 'grow', text: n }), el('span', { class: 'muted small', text: '已设置' }),
              el('button', { class: 'btn ghost sm', onclick: async () => { await window.foxos.settings.setSecret(n, ''); render(); } }, '删除'))) : el('div', { class: 'muted small', text: '还没有设置任何密钥。' })),
            el('datalist', { id: 'known-keys' }, KNOWN.map((k) => el('option', { value: k }))),
            el('form', { class: 'row', onsubmit: async (e) => { e.preventDefault(); const n = keyName.value.trim(); if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(n)) { FX.toast('变量名不合法', 'error'); return; } await window.foxos.settings.setSecret(n, keyVal.value); render(); } },
              keyName, keyVal, el('button', { class: 'btn primary sm', type: 'submit' }, '保存'))),
          el('section', {}, el('h3', { text: '安装与组件' }),
            el('div', { class: 'row' }, el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('setup', {}) }, icon('wand'), '打开安装向导'), el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('appcenter', {}) }, icon('apps'), '应用中心'))),
          el('section', {}, el('h3', { text: '关于' }),
            el('div', { class: 'muted small mono', text: `狐狸OS ${env.versions.app} · Electron ${env.versions.electron} · Chromium ${env.versions.chrome} · Node ${env.versions.node} · ${env.platform}-${env.arch}` }),
            el('div', { class: 'muted small mono', text: `用户数据：${env.userData}` })));
      }
      render();
      return { render };
    },
  });
})();
