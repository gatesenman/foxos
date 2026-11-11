// 设置：工作空间、Python、智能体 API 密钥（加密保存，作为环境变量传给 ACP 智能体）
'use strict';
(() => {
  const { el, icon } = FX;
  const KNOWN = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'DASHSCOPE_API_KEY', 'OPENROUTER_API_KEY', 'DEEPSEEK_API_KEY'];

  FX.registerApp('settings', {
    title: () => FX.t('common.settings'),
    icon: 'settings',
    geometry: { w: 700, h: 560 },
    key: () => 'settings',
    mount(body) {
      const root = el('div', { class: 'settings scroll' });
      body.append(root);
      async function render() {
        const s = await window.foxos.settings.get();
        const env = FX.env;
        const keyName = el('input', { class: 'input', list: 'known-keys', placeholder: FX.t('settings.environment_variable_name_e_g') });
        const keyVal = el('input', { class: 'input', type: 'password', placeholder: FX.t('settings.value_leave_empty_to_delete') });
        const py = el('input', { class: 'input mono', value: s.python || '', placeholder: env.python });
        root.replaceChildren(
          el('section', { 'data-section': 'language' }, el('h3', { class: 'lang-label', text: FX.t('util.language') }), FX.langPicker(),
            el('div', { class: 'muted small', text: FX.t('settings.language_hint') })),
          el('section', { 'data-section': 'execution' }, el('h3', { text: FX.t('client.execution_title') }),
            el('div', { class: 'muted small', 'data-mode': env.mode, text: env.mode === 'client' ? FX.t('client.mode_client', env.guest ? (env.guest.env || env.guest.host || env.guest.machine) : FX.t('client.not_connected')) : FX.t('client.mode_native') }),
            env.mode === 'client' ? el('div', { class: 'row' }, el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('computer', {}) }, icon('device-desktop'), FX.t('client.computer_title'))) : null,
            env.mode === 'client' ? el('label', { class: 'row', 'data-host-exec-toggle': '' },
              el('input', { type: 'checkbox', checked: !!s.hostExecution, onchange: async (e) => {
                const on = e.target.checked;
                if (on && !(await FX.confirm(FX.t('client.host_execution_enable_title'), FX.t('client.host_execution_enable_body'), { danger: true }))) { e.target.checked = false; return; }
                await window.foxos.settings.set({ hostExecution: on }); FX.env.hostExecution = on; FX.toast(on ? FX.t('client.host_execution_on_badge') : FX.t('client.host_execution_off_badge'), on ? 'error' : 'ok');
              } }),
              el('span', { text: FX.t('client.host_execution_label') })) : null,
            env.mode === 'client' ? el('div', { class: 'muted small', text: FX.t('client.host_execution_hint') }) : null),
          el('section', {}, el('h3', { text: FX.t('common.workspace') }),
            el('div', { class: 'row' }, el('code', { class: 'grow', text: env.workspace }),
              el('button', { class: 'btn ghost sm', onclick: async () => {
                const d = await window.foxos.chooseDir(); if (!d) return;
                await window.foxos.settings.set({ workspace: d });
                if (await FX.confirm(FX.t('common.switch_workspace'), FX.t('settings.the_desktop_must_restart_to_switch', d), { okText: FX.t('common.restart') })) window.foxos.relaunch();
              } }, FX.t('common.change')))),
          el('section', {}, el('h3', { text: FX.t('settings.python_interpreter_foxos_kernel') }),
            el('div', { class: 'row' }, py, el('button', { class: 'btn ghost sm', onclick: async () => { await window.foxos.settings.set({ python: py.value.trim() || null }); FX.toast(FX.t('settings.saved_takes_effect_after_restart'), 'ok'); } }, FX.t('common.save'))),
            el('div', { class: 'muted small', 'data-python-source': env.pythonInfo?.source || '' }, FX.t('settings.currently_using', env.python), ' ', env.pythonInfo && env.pythonInfo.source !== 'missing' ? FX.t(`settings.python_source_${env.pythonInfo.source}`) : ''),
            env.pythonInfo?.source === 'missing' ? el('div', { class: 'small', style: 'color: var(--danger, #e5484d)', text: FX.t('settings.python_source_missing') }) : null,
            env.pythonInfo?.ignoredSetting ? el('div', { class: 'muted small', text: FX.t('settings.python_setting_ignored', env.pythonInfo.ignoredSetting) }) : null,
            env.cli ? el('div', { class: 'muted small', 'data-cli-path': env.cli, text: FX.t('settings.cli_path', env.cli) }) : null),
          el('section', {}, el('h3', { text: FX.t('settings.agent_keys') }),
            el('p', { class: 'muted small', text: FX.t('settings.keys_are_passed_as_environment', env.encryption.available ? FX.t('settings.system_keychain', env.encryption.backend) : FX.t('settings.encrypted_storage_is_not_available')) }),
            el('div', { class: 'key-list' }, s.secrets.length ? s.secrets.map((n) => el('div', { class: 'row' }, icon('key'), el('code', { class: 'grow', text: n }), el('span', { class: 'muted small', text: FX.t('settings.set') }),
              el('button', { class: 'btn ghost sm', onclick: async () => { await window.foxos.settings.setSecret(n, ''); render(); } }, FX.t('common.delete')))) : el('div', { class: 'muted small', text: FX.t('settings.no_keys_set_yet') })),
            el('datalist', { id: 'known-keys' }, KNOWN.map((k) => el('option', { value: k }))),
            el('form', { class: 'row', onsubmit: async (e) => { e.preventDefault(); const n = keyName.value.trim(); if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(n)) { FX.toast(FX.t('settings.invalid_variable_name'), 'error'); return; } await window.foxos.settings.setSecret(n, keyVal.value); render(); } },
              keyName, keyVal, el('button', { class: 'btn primary sm', type: 'submit' }, FX.t('common.save')))),
          el('section', {}, el('h3', { text: FX.t('settings.installation_and_components') }),
            el('div', { class: 'row' }, el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('setup', {}) }, icon('wand'), FX.t('common.open_setup_wizard')), el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('appcenter', {}) }, icon('apps'), FX.t('common.app_center')))),
          el('section', {}, el('h3', { text: FX.t('settings.about') }),
            el('div', { class: 'muted small mono', text: FX.t('settings.foxos_electron_chromium_node', env.versions.app, env.versions.electron, env.versions.chrome, env.versions.node, env.platform, env.arch) }),
            el('div', { class: 'muted small mono', text: FX.t('settings.user_data', env.userData) })));
      }
      render();
      return { render };
    },
  });
})();
