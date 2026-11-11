// 首次启动安装向导：检测组件，勾选后真实在线安装（系统包管理器 / pip / npm / 官方二进制）
'use strict';
(() => {
  const { el, icon } = FX;

  FX.registerApp('setup', {
    title: () => FX.t('common.setup_wizard'),
    icon: 'wand',
    geometry: { w: 760, h: 580 },
    key: () => 'setup',
    persist: false,
    mount(body, params, win) {
      const root = el('div', { class: 'wizard scroll' });
      body.append(root);
      let step = 0;
      let detected = null;
      let plan = null;
      let agentList = null;
      const picks = new Set();

      async function stepWelcome() {
        root.replaceChildren(
          el('div', { class: 'wizard-hero' }, el('img', { src: 'icon-64.png', alt: '' }), el('div', {},
            el('h2', { text: FX.t('setup.welcome_to_foxos') }),
            el('p', { class: 'muted', text: FX.t('setup.a_desktop_shared_by_agents_and') }))),
          el('div', { class: 'field' }, el('label', { text: FX.t('setup.workspace_the_folder_you_share_with') }),
            el('div', { class: 'row' }, el('code', { class: 'grow', text: FX.env.workspace }),
              el('button', { class: 'btn ghost sm', onclick: async () => {
                const d = await window.foxos.chooseDir(); if (!d) return;
                await window.foxos.settings.set({ workspace: d });
                if (await FX.confirm(FX.t('common.switch_workspace'), FX.t('setup.set_to_the_desktop_must_restart_for', d), { okText: FX.t('common.restart') })) window.foxos.relaunch();
              } }, FX.t('common.change')))),
          nav(null, () => go(1), FX.t('setup.detect_components')));
      }

      function nav(back, next, nextText = FX.t('setup.next')) {
        return el('div', { class: 'wizard-nav' },
          back ? el('button', { class: 'btn ghost', onclick: back }, FX.t('setup.back')) : el('span'),
          el('div', { class: 'spacer' }),
          el('button', { class: 'btn ghost', 'data-action': 'skip', onclick: finish }, FX.t('setup.skip')),
          next ? el('button', { class: 'btn primary', 'data-action': 'next', onclick: next }, nextText) : null);
      }

      async function stepComponents() {
        root.replaceChildren(el('div', { class: 'muted', text: FX.t('setup.detecting') }));
        [detected, plan] = await Promise.all([FX.detectApps(true), window.foxos.setup.plan()]);
        try { agentList = await window.foxos.agents.list(); } catch { agentList = { agents: [], npm: false } }
        const lo = detected.office[0];
        const tools = Object.fromEntries(detected.tools.map((t) => [t.id, t]));
        const comps = [
          { id: 'libreoffice', name: FX.t('setup.libreoffice_writer_calc_impress'), installed: lo.installed, version: lo.version, cmd: plan.components.libreoffice },
          { id: 'python', name: 'Python 3', installed: tools.python.installed, version: tools.python.version, cmd: plan.components.python },
          { id: 'python-deps', name: FX.t('setup.python_office_libraries_openpyxl'), installed: tools['python-deps'].installed, version: tools['python-deps'].version, cmd: plan.components['python-deps'] },
          { id: 'node', name: FX.t('setup.node_js_and_npm_needed_by_npm_based'), installed: tools.node.installed && tools.npm.installed, version: tools.node.version, cmd: plan.components.node },
          { id: 'git', name: 'git', installed: tools.git.installed, version: tools.git.version, cmd: plan.components.git },
        ];
        if (plan.components.wmctrl !== undefined) comps.push({ id: 'wmctrl', name: FX.t('setup.wmctrl_tracks_libreoffice_windows_in'), installed: tools.wmctrl.installed, cmd: plan.components.wmctrl });
        // 环境组件与 Everything 分组
        let envReady = false;
        try { const im = await FX.k(['env', 'images']); envReady = im.backend !== 'linux-ns' ? false : im.local.length > 0; } catch { envReady = false; }
        if (plan.components.environments) comps.push({ id: 'environments', name: FX.t('common.environments_2', { linux: FX.t('setup.linux_namespaces_alpine_image'), windows: 'WSL2', macos: FX.t('setup.virtualization_framework_helper') }[plan.platform] || plan.platform), installed: envReady, cmd: plan.components.environments });
        let ev = null; try { ev = await FX.loadEverything(true); } catch { ev = null; }
        const evComps = ev ? ev.groups.map((g) => {
          const apps = ev.apps.filter((a) => a.group === g.id);
          const n = apps.filter((a) => a.installed).length;
          return { id: `everything:${g.id}`, name: FX.t('setup.group_label', g.zh, g.en, apps.map((a) => a.name).join(FX.t('common.list_sep'))), installed: n === apps.filter((a) => !a.upstreamIssue).length, version: FX.t('setup.installed', n, apps.length), cmd: plan.components[`everything:${g.id}`] };
        }) : [];
        const featured = ['claude-acp', 'codex-acp', 'gemini', 'opencode', 'qwen-code', 'goose'];
        const agents = featured.map((id) => agentList.agents.find((a) => a.id === id)).filter(Boolean);
        if (!step || picks.size === 0) for (const c of comps) if (!c.installed && c.cmd) picks.add(c.id);
        const row = (c, cmdText) => el('label', { class: `comp ${c.installed ? 'ok' : ''}`, 'data-comp': c.id },
          el('input', { type: 'checkbox', checked: picks.has(c.id), disabled: c.installed || !cmdText, onchange: (e) => (e.target.checked ? picks.add(c.id) : picks.delete(c.id)) }),
          el('div', { class: 'grow' }, el('div', {}, c.name, el('span', { class: `badge ${c.installed ? 'ok' : 'warn'}`, text: c.installed ? FX.t('common.installed') : FX.t('common.not_installed') })),
            el('div', { class: 'muted small mono', text: c.installed ? (c.version || '') : (cmdText || FX.t('setup.no_automatic_install_on_this')) })));
        root.replaceChildren(
          el('h2', { text: FX.t('setup.choose_components_to_install') }),
          el('p', { class: 'muted small', text: FX.t('setup.platform_package_manager_system', plan.platform, plan.packageManager || FX.t('setup.not_detected')) }),
          el('div', { class: 'comp-list' }, comps.map((c) => row(c, c.cmd))),
          el('h3', { text: FX.t('setup.everything_apps_optional_in_upstream') }),
          el('p', { class: 'muted small', text: FX.t('setup.built_locally_from_a_pinned_commit') }),
          el('div', { class: 'comp-list' }, evComps.map((c) => row(c, c.cmd))),
          el('h3', { text: FX.t('setup.acp_agents_optional') }),
          el('p', { class: 'muted small', text: FX.t('setup.installed_from_the_official_acp') }),
          el('div', { class: 'comp-list' }, agents.map((a) => row({ id: `agent:${a.id}`, name: `${a.name} ${a.version}`, installed: a.installed, version: a.installedVersion },
            a.methods.includes('binary') ? FX.t('setup.official_binary') : (a.methods.includes('npm') && agentList.npm ? FX.t('setup.npm') : null)))),
          nav(() => go(0), () => go(2), FX.t('common.start_install')));
      }

      async function stepInstall() {
        const list = [...picks];
        const lines = el('div', { class: 'comp-list' });
        root.replaceChildren(el('h2', { text: FX.t('setup.installing_2') }), lines, el('div', { class: 'wizard-nav' }, el('div', { class: 'spacer' }), el('button', { class: 'btn primary', disabled: true, 'data-action': 'done' }, FX.t('setup.done'))));
        const doneBtn = root.querySelector('[data-action=done]');
        if (!list.length) lines.append(el('div', { class: 'muted', text: FX.t('setup.no_components_selected') }));
        for (const id of list) {
          const state = el('span', { class: 'badge', text: FX.t('setup.waiting') });
          const prog = el('progress', { class: 'hidden', max: '1' });
          lines.append(el('div', { class: 'comp', 'data-install': id }, el('div', { class: 'grow', text: id.replace(/^agent:/, FX.t('setup.acp_agent')) }), prog, state));
        }
        for (const id of list) {
          const line = lines.querySelector(`[data-install="${CSS.escape(id)}"]`);
          const state = line.querySelector('.badge');
          const prog = line.querySelector('progress');
          state.textContent = FX.t('setup.installing'); state.className = 'badge';
          let ok = false;
          try {
            if (id.startsWith('agent:')) {
              const aid = id.slice(6);
              prog.classList.remove('hidden');
              const off = (d) => { if (d.id === aid) { const s = FX.installingState(aid); if (s && s.ratio != null) prog.value = s.ratio; } };
              FX.on('agent-install', off);
              await FX.installAgent(aid);
              ok = true;
            } else {
              const code = await FX.runInTerminal(FX.t('common.install_2', id), plan.components[id]);
              ok = code === 0;
            }
          } catch { ok = false; }
          prog.classList.add('hidden');
          state.textContent = ok ? FX.t('setup.done') : FX.t('common.failed'); state.className = `badge ${ok ? 'ok' : 'err'}`;
        }
        await FX.detectApps(true);
        doneBtn.disabled = false;
        doneBtn.onclick = finish;
      }

      async function finish() {
        await window.foxos.settings.set({ setupDone: true });
        FX.env.setupDone = true;
        FX.closeWindow(win);
      }

      function go(n) { step = n; [stepWelcome, stepComponents, stepInstall][n](); }
      go(0);
      return { go, picks };
    },
  });
})();
