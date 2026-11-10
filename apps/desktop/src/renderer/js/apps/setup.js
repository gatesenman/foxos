// 首次启动安装向导：检测组件，勾选后真实在线安装（系统包管理器 / pip / npm / 官方二进制）
'use strict';
(() => {
  const { el, icon } = FX;

  FX.registerApp('setup', {
    title: () => '安装向导',
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
            el('h2', { text: '欢迎使用狐狸OS' }),
            el('p', { class: 'muted', text: '智能体与人共用的桌面：真实的终端、文件、编辑器、浏览器与 LibreOffice。接下来检测本机组件，并按你的勾选在线安装缺少的部分。' }))),
          el('div', { class: 'field' }, el('label', { text: '工作空间（智能体与你共享的文件夹）' }),
            el('div', { class: 'row' }, el('code', { class: 'grow', text: FX.env.workspace }),
              el('button', { class: 'btn ghost sm', onclick: async () => {
                const d = await window.foxos.chooseDir(); if (!d) return;
                await window.foxos.settings.set({ workspace: d });
                if (await FX.confirm('切换工作空间', `已设置为 ${d}，需要重启桌面生效。现在重启？`, { okText: '重启' })) window.foxos.relaunch();
              } }, '更改…'))),
          nav(null, () => go(1), '检测组件'));
      }

      function nav(back, next, nextText = '下一步') {
        return el('div', { class: 'wizard-nav' },
          back ? el('button', { class: 'btn ghost', onclick: back }, '上一步') : el('span'),
          el('div', { class: 'spacer' }),
          el('button', { class: 'btn ghost', 'data-action': 'skip', onclick: finish }, '跳过'),
          next ? el('button', { class: 'btn primary', 'data-action': 'next', onclick: next }, nextText) : null);
      }

      async function stepComponents() {
        root.replaceChildren(el('div', { class: 'muted', text: '正在检测…' }));
        [detected, plan] = await Promise.all([FX.detectApps(true), window.foxos.setup.plan()]);
        try { agentList = await window.foxos.agents.list(); } catch { agentList = { agents: [], npm: false } }
        const lo = detected.office[0];
        const tools = Object.fromEntries(detected.tools.map((t) => [t.id, t]));
        const comps = [
          { id: 'libreoffice', name: 'LibreOffice（Writer / Calc / Impress）', installed: lo.installed, version: lo.version, cmd: plan.components.libreoffice },
          { id: 'python', name: 'Python 3', installed: tools.python.installed, version: tools.python.version, cmd: plan.components.python },
          { id: 'python-deps', name: 'Python 办公库 openpyxl / python-docx / python-pptx', installed: tools['python-deps'].installed, version: tools['python-deps'].version, cmd: plan.components['python-deps'] },
          { id: 'node', name: 'Node.js 与 npm（npm 型 ACP 智能体需要）', installed: tools.node.installed && tools.npm.installed, version: tools.node.version, cmd: plan.components.node },
          { id: 'git', name: 'git', installed: tools.git.installed, version: tools.git.version, cmd: plan.components.git },
        ];
        if (plan.components.wmctrl !== undefined) comps.push({ id: 'wmctrl', name: 'wmctrl（任务栏跟踪 LibreOffice 窗口）', installed: tools.wmctrl.installed, cmd: plan.components.wmctrl });
        const featured = ['claude-acp', 'codex-acp', 'gemini', 'opencode', 'qwen-code', 'goose'];
        const agents = featured.map((id) => agentList.agents.find((a) => a.id === id)).filter(Boolean);
        if (!step || picks.size === 0) for (const c of comps) if (!c.installed && c.cmd) picks.add(c.id);
        const row = (c, cmdText) => el('label', { class: `comp ${c.installed ? 'ok' : ''}`, 'data-comp': c.id },
          el('input', { type: 'checkbox', checked: picks.has(c.id), disabled: c.installed || !cmdText, onchange: (e) => (e.target.checked ? picks.add(c.id) : picks.delete(c.id)) }),
          el('div', { class: 'grow' }, el('div', {}, c.name, el('span', { class: `badge ${c.installed ? 'ok' : 'warn'}`, text: c.installed ? '已安装' : '未安装' })),
            el('div', { class: 'muted small mono', text: c.installed ? (c.version || '') : (cmdText || '本平台没有可用的自动安装方式') })));
        root.replaceChildren(
          el('h2', { text: '选择要安装的组件' }),
          el('p', { class: 'muted small', text: `平台 ${plan.platform} · 包管理器 ${plan.packageManager || '未检测到'}。系统软件会在真实终端里安装，需要时在终端里输入 sudo 密码。` }),
          el('div', { class: 'comp-list' }, comps.map((c) => row(c, c.cmd))),
          el('h3', { text: 'ACP 智能体（可选）' }),
          el('p', { class: 'muted small', text: '从 ACP 官方注册表安装；使用时需要各自的账号或 API 密钥（在设置中填写）。' }),
          el('div', { class: 'comp-list' }, agents.map((a) => row({ id: `agent:${a.id}`, name: `${a.name} ${a.version}`, installed: a.installed, version: a.installedVersion },
            a.methods.includes('binary') ? '官方二进制' : (a.methods.includes('npm') && agentList.npm ? `npm 安装` : null)))),
          nav(() => go(0), () => go(2), '开始安装'));
      }

      async function stepInstall() {
        const list = [...picks];
        const lines = el('div', { class: 'comp-list' });
        root.replaceChildren(el('h2', { text: '正在安装' }), lines, el('div', { class: 'wizard-nav' }, el('div', { class: 'spacer' }), el('button', { class: 'btn primary', disabled: true, 'data-action': 'done' }, '完成')));
        const doneBtn = root.querySelector('[data-action=done]');
        if (!list.length) lines.append(el('div', { class: 'muted', text: '没有勾选任何组件。' }));
        for (const id of list) {
          const state = el('span', { class: 'badge', text: '等待' });
          const prog = el('progress', { class: 'hidden', max: '1' });
          lines.append(el('div', { class: 'comp', 'data-install': id }, el('div', { class: 'grow', text: id.replace(/^agent:/, 'ACP 智能体 ') }), prog, state));
        }
        for (const id of list) {
          const line = lines.querySelector(`[data-install="${CSS.escape(id)}"]`);
          const state = line.querySelector('.badge');
          const prog = line.querySelector('progress');
          state.textContent = '安装中'; state.className = 'badge';
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
              const code = await FX.runInTerminal(`安装 ${id}`, plan.components[id]);
              ok = code === 0;
            }
          } catch { ok = false; }
          prog.classList.add('hidden');
          state.textContent = ok ? '完成' : '失败'; state.className = `badge ${ok ? 'ok' : 'err'}`;
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
