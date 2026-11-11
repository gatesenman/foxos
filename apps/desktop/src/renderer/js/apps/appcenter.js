// 应用中心：真实检测本机已安装的软件；ACP 智能体从官方注册表一键安装（npm / 二进制）
'use strict';
(() => {
  const { el, icon } = FX;
  const ICONS = { terminal: 'terminal-2', files: 'folder', editor: 'code', browser: 'world', writer: 'file-text', calc: 'file-spreadsheet', impress: 'presentation', python: 'brand-python', 'python-deps': 'package', git: 'brand-git', node: 'brand-nodejs', npm: 'brand-npm', wmctrl: 'app-window', environments: 'box-multiple' };
  const SETUP_KEY = { writer: 'libreoffice', calc: 'libreoffice', impress: 'libreoffice', python: 'python', 'python-deps': 'python-deps', node: 'node', npm: 'node', git: 'git', wmctrl: 'wmctrl' };
  const installing = new Map(); // agentId -> {log, ratio}

  window.foxos.agents.onLog((id, text) => { const s = installing.get(id); if (s) { s.log += text; FX.emit('agent-install', { id }); } });
  window.foxos.agents.onProgress((id, ratio) => { const s = installing.get(id); if (s) { s.ratio = ratio; FX.emit('agent-install', { id }); } });

  FX.installAgent = async (id) => {
    installing.set(id, { log: '', ratio: null });
    FX.emit('agent-install', { id });
    try {
      const r = await window.foxos.agents.install(id);
      FX.toast(FX.t('appcenter.installed_2', r.name || id), 'ok');
      return r;
    } catch (e) {
      FX.toast(FX.t('appcenter.installing_failed', id, e.message), 'error');
      const s = installing.get(id); if (s) s.log += FX.t('appcenter.failed', e.message);
      throw e;
    } finally {
      const s = installing.get(id); if (s) s.done = true;
      FX.emit('agent-install', { id });
      FX.emit('agents-changed');
    }
  };
  FX.installingState = (id) => installing.get(id);

  FX.registerApp('appcenter', {
    title: () => FX.t('common.app_center'),
    icon: 'apps',
    geometry: { w: 900, h: 600 },
    key: () => 'appcenter',
    mount(body, params, win) {
      const content = el('div', { class: 'appcenter scroll' });
      const filter = el('input', { class: 'input', type: 'search', placeholder: FX.t('appcenter.search_agents_name_description') });
      body.append(el('div', { class: 'toolbar' }, icon('apps'), el('b', { text: FX.t('common.app_center') }), el('span', { class: 'muted', text: FX.t('appcenter.detected_on_this_machine_not_preset') }), el('div', { class: 'spacer' }),
        el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('setup', {}) }, icon('wand'), FX.t('common.setup_wizard')),
        el('button', { class: 'btn ghost sm', onclick: () => refresh() }, icon('refresh'), FX.t('appcenter.detect_again'))), content);
      let agentData = null;

      const card = (a, actions, extra) => el('div', { class: `app-card ${a.installed ? 'ok' : 'missing'}`, 'data-app-id': a.id },
        el('div', { class: 'app-card-icon' }, FX.appIcon(a.iconSpec || FX.programIcon(a.id, ICONS[a.id] || 'box'))),
        el('div', { class: 'app-card-main' },
          el('div', { class: 'app-card-name' }, a.name, el('span', { class: `badge ${a.installed ? 'ok' : 'warn'}`, text: a.installed ? FX.t('common.installed') : FX.t('common.not_installed') })),
          el('div', { class: 'muted small', text: a.version || a.hint || '' }), extra || null),
        el('div', { class: 'app-card-actions' }, actions));

      function section(title, items) { return el('section', {}, el('h3', { text: title }), el('div', { class: 'card-grid' }, items)); }

      async function setupCmd(id) {
        const plan = await window.foxos.setup.plan();
        const cmd = plan.components[SETUP_KEY[id]];
        if (!cmd) { FX.toast(FX.t('appcenter.no_automatic_install_on_this'), 'error'); return; }
        const code = await FX.runInTerminal(FX.t('common.install_2', id), cmd);
        FX.toast(code === 0 ? FX.t('appcenter.installed') : FX.t('appcenter.install_command_exited_with_code', code), code === 0 ? 'ok' : 'error');
        refresh();
      }

      function renderAgents(box) {
        box.replaceChildren();
        if (!agentData) { box.append(el('div', { class: 'muted', text: FX.t('appcenter.reading_the_acp_registry') })); return; }
        const q = filter.value.trim().toLowerCase();
        const list = agentData.agents.filter((a) => !q || `${a.id} ${a.name} ${a.description}`.toLowerCase().includes(q));
        box.append(el('div', { class: 'muted small' }, FX.t('appcenter.source_platform_agents', agentData.source === 'online' ? FX.t('appcenter.official_acp_registry_online') : agentData.source === 'cache' ? FX.t('appcenter.acp_registry_local_cache') : FX.t('appcenter.acp_registry_built_in_snapshot'), agentData.platform, agentData.agents.length, agentData.npm ? '' : FX.t('appcenter.npm_not_found_npm_based_agents'))));
        const grid = el('div', { class: 'card-grid' });
        for (const a of list) {
          const st = installing.get(a.id);
          const busy = st && !st.done;
          const canInstall = a.methods.includes('binary') || (a.methods.includes('npm') && agentData.npm);
          const actions = a.installed
            ? [el('button', { class: 'btn sm primary', onclick: () => { FX.openPanel(); FX.startAgentSession(a.id); } }, icon('player-play'), FX.t('appcenter.start_session')),
              el('button', { class: 'btn sm ghost', onclick: async () => { if (await FX.confirm(FX.t('appcenter.uninstall'), FX.t('appcenter.uninstall_2', a.name), { danger: true, okText: FX.t('appcenter.uninstall') })) { await window.foxos.agents.uninstall(a.id); FX.emit('agents-changed'); } } }, FX.t('appcenter.uninstall'))]
            : [el('button', { class: 'btn sm primary', 'data-action': 'install-agent', disabled: busy || !canInstall, title: canInstall ? FX.t('appcenter.install_method', a.methods.join(' / ')) : FX.t('appcenter.no_install_method_for_this_platform'), onclick: () => FX.installAgent(a.id).catch(() => {}) }, icon('download'), busy ? FX.t('appcenter.installing') : FX.t('common.install'))];
          const extra = el('div', {},
            el('div', { class: 'small', text: a.description || '' }),
            el('div', { class: 'muted small', text: `${a.version} · ${a.license || FX.t('appcenter.license_not_stated')} · ${a.methods.join(' / ') || FX.t('appcenter.no_install_method')}` }),
            st ? el('div', { class: 'install-state' },
              st.ratio != null && !st.done ? el('progress', { max: '1', value: String(st.ratio) }) : null,
              el('pre', { class: 'install-log', text: st.log.slice(-1200) || FX.t('appcenter.preparing') })) : null);
          grid.append(card({ ...a, version: null, hint: null, iconSpec: FX.agentIcon(a) }, actions, extra));
        }
        box.append(grid);
      }

      const agentsBox = el('div');
      filter.addEventListener('input', () => renderAgents(agentsBox));
      FX.on('agent-install', () => { if (!win.disposed) renderAgents(agentsBox); });
      FX.on('agents-changed', () => { if (!win.disposed) loadAgents(); });

      async function loadAgents() {
        try { agentData = await window.foxos.agents.list(); } catch (e) { agentData = { agents: [], source: 'error', platform: '', npm: false }; FX.toast(e.message, 'error'); }
        renderAgents(agentsBox);
      }

      // Everything 应用（HeyPuter/everything，按上游的 9 个分组），在本机从上游源码构建
      const evBox = el('section', { class: 'ev-section' });
      async function evInstall(ids, label) {
        const code = await FX.runFoxosInTerminal(FX.t('common.install_2', label), ['everything', 'install', ...ids]);
        FX.toast(code === 0 ? FX.t('common.installed_2', label) : FX.t('appcenter.install_command_exited_with_code', code), code === 0 ? 'ok' : 'error');
        await FX.loadEverything(true); renderEverything(); FX.emit('everything-changed');
      }
      async function renderEverything() {
        let c; try { c = await FX.loadEverything(true); } catch (e) { evBox.replaceChildren(el('h3', { text: FX.t('appcenter.everything_apps') }), el('div', { class: 'muted', text: e.message })); return; }
        const inst = c.apps.filter((a) => a.installed).length;
        evBox.replaceChildren(
          el('h3', { text: FX.t('appcenter.everything_apps_installed', inst, c.apps.length) }),
          el('div', { class: 'muted small', text: FX.t('appcenter.source_root_license_apps_marked_agpl', c.upstream, String(c.commit).slice(0, 8), c.rootLicense) }),
          ...c.groups.map((g) => {
            const apps = c.apps.filter((a) => a.group === g.id);
            const missing = apps.filter((a) => !a.installed && !a.upstreamIssue).map((a) => a.id);
            return el('div', { class: 'ev-group', 'data-group': g.id },
              el('div', { class: 'row' }, icon(FX.groupIcon(g.id)), el('b', { text: FX.groupName(g) }), el('span', { class: 'muted small', text: `${apps.filter((a) => a.installed).length}/${apps.length}` }), el('div', { class: 'spacer' }),
                missing.length ? el('button', { class: 'btn sm ghost', 'data-install-group': g.id, onclick: () => evInstall(missing, FX.t('appcenter.the_group', FX.groupName(g))) }, icon('download'), FX.t('appcenter.install_group', missing.length)) : null),
              el('div', { class: 'card-grid' }, apps.map((a) => el('div', { class: `app-card ${a.installed ? 'ok' : 'missing'}`, 'data-ev-app': a.id },
                el('div', { class: 'app-card-icon' }, FX.appIcon(FX.evIcon(a))),
                el('div', { class: 'app-card-main' },
                  el('div', { class: 'app-card-name' }, a.name, el('span', { class: `badge ${a.installed ? 'ok' : a.upstreamIssue ? 'error' : 'warn'}`, text: a.installed ? FX.t('common.installed') : a.upstreamIssue ? FX.t('appcenter.upstream_does_not_build') : FX.t('common.not_installed') }), a.agpl ? el('span', { class: 'badge', text: 'AGPL' }) : null,
                    a.uiLanguages && !a.uiLanguages.includes(FX.lang) ? el('span', { class: 'badge', 'data-ui-lang': 'en', title: a.localeFormats === 'follows' ? FX.t('appcenter.ui_english_formats_follow') : FX.t('appcenter.ui_english_tip'), text: FX.t('appcenter.ui_english') }) : null),
                  el('div', { class: 'muted small', text: FX.evIssue(a) || FX.evDesc(a) })),
                el('div', { class: 'app-card-actions' }, a.installed
                  ? [el('button', { class: 'btn sm ghost', onclick: () => FX.openWindow('everything', { app: a.id }) }, FX.t('common.open')),
                    el('button', { class: 'btn sm ghost', onclick: async () => { if (await FX.confirm(FX.t('appcenter.uninstall'), FX.t('appcenter.uninstall_data_in_the_workspace_is', a.name), { danger: true, okText: FX.t('appcenter.uninstall') })) { await FX.k(['everything', 'uninstall', a.id]); renderEverything(); FX.emit('everything-changed'); } } }, FX.t('appcenter.uninstall'))]
                  : a.upstreamIssue ? [] : [el('button', { class: 'btn sm primary', 'data-install': a.id, onclick: () => evInstall([a.id], a.name) }, icon('download'), FX.t('common.install'))])))));
          }));
      }

      async function refresh() {
        content.replaceChildren(el('div', { class: 'muted', text: FX.t('appcenter.detecting_software_on_this_machine') }));
        const d = await FX.detectApps(true);
        content.replaceChildren(
          section(FX.t('appcenter.built_in_apps'), d.builtin.map((a) => card(a, [el('button', { class: 'btn sm ghost', onclick: () => FX.openWindow(a.id, {}) }, FX.t('common.open'))]))),
          section(FX.t('appcenter.office_suite_native_libreoffice'), d.office.map((a) => card(a, a.installed
            ? [el('button', { class: 'btn sm ghost', onclick: () => FX.launchOffice(a.id) }, FX.t('common.open'))]
            : [el('button', { class: 'btn sm primary', onclick: () => setupCmd(a.id) }, icon('download'), FX.t('common.install'))]))),
          section(FX.t('appcenter.developer_tools_and_dependencies'), d.tools.map((a) => card(a, a.installed ? [] : [el('button', { class: 'btn sm primary', onclick: () => setupCmd(a.id) }, icon('download'), FX.t('common.install'))]))),
          evBox,
          el('section', {}, el('h3', { text: FX.t('appcenter.acp_agents') }), filter, agentsBox));
        renderEverything();
        loadAgents();
      }
      refresh();
      return { refresh, dispose: () => { win.disposed = true; } };
    },
  });
})();
