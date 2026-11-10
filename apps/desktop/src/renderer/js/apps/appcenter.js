// 应用中心：真实检测本机已安装的软件；ACP 智能体从官方注册表一键安装（npm / 二进制）
'use strict';
(() => {
  const { el, icon } = FX;
  const ICONS = { terminal: 'terminal-2', files: 'folder', editor: 'code', browser: 'world', writer: 'file-text', calc: 'file-spreadsheet', impress: 'presentation', python: 'brand-python', 'python-deps': 'package', git: 'brand-git', node: 'brand-nodejs', npm: 'brand-npm', wmctrl: 'app-window' };
  const SETUP_KEY = { writer: 'libreoffice', calc: 'libreoffice', impress: 'libreoffice', python: 'python', 'python-deps': 'python-deps', node: 'node', npm: 'node', git: 'git', wmctrl: 'wmctrl' };
  const installing = new Map(); // agentId -> {log, ratio}

  window.foxos.agents.onLog((id, text) => { const s = installing.get(id); if (s) { s.log += text; FX.emit('agent-install', { id }); } });
  window.foxos.agents.onProgress((id, ratio) => { const s = installing.get(id); if (s) { s.ratio = ratio; FX.emit('agent-install', { id }); } });

  FX.installAgent = async (id) => {
    installing.set(id, { log: '', ratio: null });
    FX.emit('agent-install', { id });
    try {
      const r = await window.foxos.agents.install(id);
      FX.toast(`已安装 ${r.name || id}`, 'ok');
      return r;
    } catch (e) {
      FX.toast(`安装 ${id} 失败：${e.message}`, 'error');
      const s = installing.get(id); if (s) s.log += `\n失败：${e.message}\n`;
      throw e;
    } finally {
      const s = installing.get(id); if (s) s.done = true;
      FX.emit('agent-install', { id });
      FX.emit('agents-changed');
    }
  };
  FX.installingState = (id) => installing.get(id);

  FX.registerApp('appcenter', {
    title: () => '应用中心',
    icon: 'apps',
    geometry: { w: 900, h: 600 },
    key: () => 'appcenter',
    mount(body, params, win) {
      const content = el('div', { class: 'appcenter scroll' });
      const filter = el('input', { class: 'input', type: 'search', placeholder: '搜索智能体（名称、描述）' });
      body.append(el('div', { class: 'toolbar' }, icon('apps'), el('b', { text: '应用中心' }), el('span', { class: 'muted', text: '检测结果来自本机，不是预设数据' }), el('div', { class: 'spacer' }),
        el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('setup', {}) }, icon('wand'), '安装向导'),
        el('button', { class: 'btn ghost sm', onclick: () => refresh() }, icon('refresh'), '重新检测')), content);
      let agentData = null;

      const card = (a, actions, extra) => el('div', { class: `app-card ${a.installed ? 'ok' : 'missing'}`, 'data-app-id': a.id },
        el('div', { class: 'app-card-icon' }, icon(ICONS[a.id] || 'box')),
        el('div', { class: 'app-card-main' },
          el('div', { class: 'app-card-name' }, a.name, el('span', { class: `badge ${a.installed ? 'ok' : 'warn'}`, text: a.installed ? '已安装' : '未安装' })),
          el('div', { class: 'muted small', text: a.version || a.hint || '' }), extra || null),
        el('div', { class: 'app-card-actions' }, actions));

      function section(title, items) { return el('section', {}, el('h3', { text: title }), el('div', { class: 'card-grid' }, items)); }

      async function setupCmd(id) {
        const plan = await window.foxos.setup.plan();
        const cmd = plan.components[SETUP_KEY[id]];
        if (!cmd) { FX.toast('本平台没有可用的自动安装方式，请手动安装', 'error'); return; }
        const code = await FX.runInTerminal(`安装 ${id}`, cmd);
        FX.toast(code === 0 ? '安装完成' : `安装命令退出码 ${code}`, code === 0 ? 'ok' : 'error');
        refresh();
      }

      function renderAgents(box) {
        box.replaceChildren();
        if (!agentData) { box.append(el('div', { class: 'muted', text: '正在读取 ACP 注册表…' })); return; }
        const q = filter.value.trim().toLowerCase();
        const list = agentData.agents.filter((a) => !q || `${a.id} ${a.name} ${a.description}`.toLowerCase().includes(q));
        box.append(el('div', { class: 'muted small' }, `来源：${agentData.source === 'online' ? 'ACP 官方注册表（在线）' : agentData.source === 'cache' ? 'ACP 注册表（本地缓存）' : 'ACP 注册表（内置快照）'} · 平台 ${agentData.platform} · 共 ${agentData.agents.length} 个${agentData.npm ? '' : ' · 未检测到 npm，npm 型智能体无法安装'}`));
        const grid = el('div', { class: 'card-grid' });
        for (const a of list) {
          const st = installing.get(a.id);
          const busy = st && !st.done;
          const canInstall = a.methods.includes('binary') || (a.methods.includes('npm') && agentData.npm);
          const actions = a.installed
            ? [el('button', { class: 'btn sm primary', onclick: () => { FX.openPanel(); FX.startAgentSession(a.id); } }, icon('player-play'), '启动会话'),
              el('button', { class: 'btn sm ghost', onclick: async () => { if (await FX.confirm('卸载', `卸载 ${a.name}？`, { danger: true, okText: '卸载' })) { await window.foxos.agents.uninstall(a.id); FX.emit('agents-changed'); } } }, '卸载')]
            : [el('button', { class: 'btn sm primary', 'data-action': 'install-agent', disabled: busy || !canInstall, title: canInstall ? `安装方式：${a.methods.join(' / ')}` : '本平台没有可用的安装方式', onclick: () => FX.installAgent(a.id).catch(() => {}) }, icon('download'), busy ? '安装中…' : '安装')];
          const extra = el('div', {},
            el('div', { class: 'small', text: a.description || '' }),
            el('div', { class: 'muted small', text: `${a.version} · ${a.license || '许可证未注明'} · ${a.methods.join(' / ') || '无可用安装方式'}` }),
            st ? el('div', { class: 'install-state' },
              st.ratio != null && !st.done ? el('progress', { max: '1', value: String(st.ratio) }) : null,
              el('pre', { class: 'install-log', text: st.log.slice(-1200) || '准备中…' })) : null);
          grid.append(card({ ...a, version: null, hint: null }, actions, extra));
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

      async function refresh() {
        content.replaceChildren(el('div', { class: 'muted', text: '正在检测本机软件…' }));
        const d = await FX.detectApps(true);
        content.replaceChildren(
          section('内置应用', d.builtin.map((a) => card(a, [el('button', { class: 'btn sm ghost', onclick: () => FX.openWindow(a.id, {}) }, '打开')]))),
          section('办公套件（LibreOffice 原生窗口）', d.office.map((a) => card(a, a.installed
            ? [el('button', { class: 'btn sm ghost', onclick: () => FX.launchOffice(a.id) }, '打开')]
            : [el('button', { class: 'btn sm primary', onclick: () => setupCmd(a.id) }, icon('download'), '安装')]))),
          section('开发工具与依赖', d.tools.map((a) => card(a, a.installed ? [] : [el('button', { class: 'btn sm primary', onclick: () => setupCmd(a.id) }, icon('download'), '安装')]))),
          el('section', {}, el('h3', { text: 'ACP 智能体' }), filter, agentsBox));
        loadAgents();
      }
      refresh();
      return { refresh, dispose: () => { win.disposed = true; } };
    },
  });
})();
