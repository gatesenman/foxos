// 智能体面板：ACP 会话（真实的智能体进程）与活动时间线（真实的审计日志）
'use strict';
(() => {
  const { el, icon, $ } = FX;
  const conns = new Map(); // connId -> {agentId, name, sessionId, init, log:[], status, authMethods}
  let active = null;

  FX.openPanel = () => { $('#panel').classList.remove('collapsed'); switchTab('session'); };

  function switchTab(t) {
    for (const b of document.querySelectorAll('.panel-tabs button')) b.classList.toggle('active', b.dataset.tab === t);
    for (const s of document.querySelectorAll('.panel .tab')) s.classList.toggle('active', s.id === `tab-${t}`);
    if (t === 'activity') loadActivity();
  }
  document.querySelectorAll('.panel-tabs button').forEach((b) => b.addEventListener('click', () => switchTab(b.dataset.tab)));

  // ---------------------------------------------------------------- 会话
  const sessionTab = $('#tab-session');
  const picker = el('select', { class: 'input', id: 'agent-picker' });
  const startBtn = el('button', { class: 'btn primary sm', id: 'agent-start', onclick: () => picker.value && FX.startAgentSession(picker.value) }, icon('player-play'), '启动');
  const sessList = el('div', { class: 'sess-tabs' });
  const transcript = el('div', { class: 'transcript scroll', id: 'transcript' });
  const input = el('textarea', { class: 'input composer-input', id: 'composer', rows: '3', placeholder: '给智能体布置任务（Enter 发送，Shift+Enter 换行）' });
  const sendBtn = el('button', { class: 'btn primary', id: 'composer-send', onclick: () => send() }, icon('send'), '发送');
  const stopBtn = el('button', { class: 'btn ghost', id: 'composer-stop', onclick: () => active && cancel(active) }, icon('player-stop'), '停止');
  sessionTab.append(
    el('div', { class: 'panel-head' }, picker, startBtn),
    sessList, transcript,
    el('div', { class: 'composer' }, input, el('div', { class: 'row' }, el('span', { class: 'muted small grow', id: 'composer-hint' }), stopBtn, sendBtn)));
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });

  async function loadAgents() {
    let list = [];
    try { list = await window.foxos.agents.installed(); } catch { /* 忽略 */ }
    picker.replaceChildren(...(list.length ? list.map((a) => el('option', { value: a.id, text: `${a.name || a.id} ${a.version || ''}` })) : [el('option', { value: '', text: '没有已安装的 ACP 智能体' })]));
    startBtn.disabled = !list.length;
    render();
  }
  FX.on('agents-changed', loadAgents);

  function push(c, item) { c.log.push(item); if (c === conns.get(active)) render(); }

  FX.startAgentSession = async (agentId) => {
    const c = { agentId, name: agentId, sessionId: null, log: [], status: '启动中', busy: false };
    const tmpId = `pending-${Date.now()}`;
    conns.set(tmpId, c); active = tmpId; render();
    try {
      const r = await window.foxos.acp.start(agentId);
      conns.delete(tmpId); conns.set(r.connId, c); active = r.connId; c.connId = r.connId;
      c.init = r.init; c.identity = r.identity;
      const ai = r.init.agentInfo || {};
      c.name = ai.title || ai.name || agentId;
      push(c, { kind: 'sys', text: `已连接 ${c.name}${ai.version ? ` ${ai.version}` : ''}（ACP 协议 v${r.init.protocolVersion}）。身份：${r.identity}` });
      c.authMethods = r.init.authMethods || [];
      await newSession(c);
    } catch (e) {
      c.status = '失败';
      push(c, { kind: 'err', text: `启动失败：${e.message}` });
    }
    render();
    updateTray();
  };

  async function newSession(c) {
    c.status = '创建会话';
    render();
    try {
      const s = await window.foxos.acp.newSession(c.connId);
      c.sessionId = s.sessionId;
      c.status = '就绪';
      push(c, { kind: 'sys', text: `会话已创建（${s.sessionId}）。已向智能体提供 foxos MCP 工具，文件读写经过 foxos 内核并记入审计。` });
    } catch (e) {
      c.status = '需要登录';
      const needsAuth = e.code === -32000 || /auth/i.test(e.message);
      push(c, { kind: 'err', text: `创建会话失败：${e.message}`, auth: needsAuth ? c.authMethods : null });
      if (!c.authMethods.length || !needsAuth) c.status = '失败';
    }
    render();
  }

  async function authenticate(c, methodId) {
    push(c, { kind: 'sys', text: `正在登录（${methodId}）…` });
    try { await window.foxos.acp.authenticate(c.connId, methodId); push(c, { kind: 'sys', text: '登录完成' }); await newSession(c); } catch (e) { push(c, { kind: 'err', text: `登录失败：${e.message}。也可以在设置中填写 API 密钥后重启会话。` }); }
  }

  async function send() {
    const c = conns.get(active);
    const text = input.value.trim();
    if (!c || !text || !c.sessionId || c.busy) return;
    input.value = '';
    push(c, { kind: 'user', text });
    c.busy = true; c.status = '工作中'; render();
    try {
      const r = await window.foxos.acp.prompt(c.connId, c.sessionId, text);
      push(c, { kind: 'sys', text: `本轮结束：${({ end_turn: '完成', cancelled: '已取消', max_tokens: '达到长度上限', refusal: '智能体拒绝', max_turn_requests: '达到请求上限' })[r.stopReason] || r.stopReason}` });
    } catch (e) { push(c, { kind: 'err', text: e.message }); }
    c.busy = false; c.status = '就绪'; render(); updateTray();
  }
  function cancel(connId) { const c = conns.get(connId); if (c && c.sessionId) window.foxos.acp.cancel(c.connId, c.sessionId); }

  window.foxos.acp.onEvent((connId, ev) => {
    const c = conns.get(connId); if (!c) return;
    if (ev.type === 'update') {
      const u = ev.update || {};
      const t = u.sessionUpdate;
      const last = c.log[c.log.length - 1];
      const txt = u.content && u.content.type === 'text' ? u.content.text : '';
      if (t === 'agent_message_chunk') { if (last && last.kind === 'agent') last.text += txt; else c.log.push({ kind: 'agent', text: txt }); }
      else if (t === 'agent_thought_chunk') { if (last && last.kind === 'thought') last.text += txt; else c.log.push({ kind: 'thought', text: txt }); }
      else if (t === 'tool_call') c.log.push({ kind: 'tool', id: u.toolCallId, title: u.title || u.kind || '工具调用', status: u.status || 'pending', toolKind: u.kind });
      else if (t === 'tool_call_update') { const tc = c.log.find((x) => x.kind === 'tool' && x.id === u.toolCallId); if (tc) { if (u.status) tc.status = u.status; if (u.title) tc.title = u.title; } }
      else if (t === 'plan') c.log.push({ kind: 'plan', entries: u.entries || [] });
      else return;
      if (c === conns.get(active)) render();
    } else if (ev.type === 'fs') {
      push(c, { kind: 'fs', text: `${ev.op === 'write' ? '写入' : '读取'} ${ev.path}` });
    } else if (ev.type === 'closed') {
      c.status = '已退出'; c.closed = true; push(c, { kind: 'err', text: ev.reason }); updateTray();
    }
  });

  window.foxos.acp.onPermission((connId, reqId, params) => {
    const c = conns.get(connId); if (!c) { window.foxos.acp.replyPermission(reqId, null); return; }
    push(c, { kind: 'perm', reqId, params, decided: null });
    FX.openPanel();
  });

  function render() {
    sessList.replaceChildren(...[...conns.entries()].map(([id, c]) => el('button', { class: `sess-tab ${id === active ? 'active' : ''}`, onclick: () => { active = id; render(); } },
      el('span', { class: `dot ${c.closed ? 'off' : c.busy ? 'busy' : 'on'}` }), c.name, el('span', { class: 'muted small', text: c.status }),
      el('i', { class: 'ti ti-x', title: '结束会话', onclick: (e) => { e.stopPropagation(); if (c.connId) window.foxos.acp.stop(c.connId); conns.delete(id); if (active === id) active = conns.keys().next().value ?? null; render(); updateTray(); } }))));
    const c = conns.get(active);
    transcript.replaceChildren();
    if (!c) {
      transcript.append(el('div', { class: 'empty' }, icon('robot'), el('div', { text: '还没有智能体会话' }),
        el('div', { class: 'muted small', text: '在上方选择已安装的 ACP 智能体并启动；没有的话到应用中心安装。智能体也可以在终端里直接用 foxos 命令，或通过 MCP 接入，它们的操作都会出现在「活动」里。' }),
        el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('appcenter', {}) }, icon('apps'), '打开应用中心')));
    } else {
      for (const m of c.log) transcript.append(renderMsg(c, m));
      transcript.scrollTop = transcript.scrollHeight;
    }
    const ready = c && c.sessionId && !c.busy && !c.closed;
    sendBtn.disabled = !ready; input.disabled = !(c && c.sessionId && !c.closed);
    stopBtn.disabled = !(c && c.busy);
    $('#composer-hint').textContent = c ? `${c.name} · ${c.status}` : '';
  }

  function renderMsg(c, m) {
    if (m.kind === 'user') return el('div', { class: 'msg user' }, el('div', { class: 'bubble', text: m.text }));
    if (m.kind === 'agent') return el('div', { class: 'msg agent' }, el('div', { class: 'bubble', text: m.text }));
    if (m.kind === 'thought') return el('details', { class: 'msg thought' }, el('summary', {}, icon('bulb'), '思考过程'), el('div', { class: 'small muted', text: m.text }));
    if (m.kind === 'tool') return el('div', { class: `msg tool ${m.status}` }, icon(m.status === 'completed' ? 'circle-check' : m.status === 'failed' ? 'circle-x' : 'loader-2'), el('span', { text: m.title }), el('span', { class: 'muted small', text: m.status }));
    if (m.kind === 'fs') return el('div', { class: 'msg fs' }, icon('file-text'), el('span', { class: 'small', text: m.text }));
    if (m.kind === 'plan') return el('div', { class: 'msg plan' }, el('div', { class: 'small muted', text: '计划' }), m.entries.map((e) => el('div', { class: `plan-item ${e.status}` }, icon(e.status === 'completed' ? 'square-check' : 'square'), e.content)));
    if (m.kind === 'perm') {
      const p = m.params || {};
      const tc = p.toolCall || {};
      return el('div', { class: 'msg perm' }, el('div', {}, icon('shield-question'), el('b', { text: '智能体请求权限：' }), tc.title || tc.kind || ''),
        m.decided ? el('div', { class: 'muted small', text: `已选择：${m.decided}` })
          : el('div', { class: 'row wrap' }, (p.options || []).map((o) => el('button', { class: `btn sm ${/reject/.test(o.kind) ? 'ghost' : 'primary'}`, onclick: () => { m.decided = o.name; window.foxos.acp.replyPermission(m.reqId, o.optionId); render(); } }, o.name)),
            el('button', { class: 'btn sm ghost', onclick: () => { m.decided = '取消'; window.foxos.acp.replyPermission(m.reqId, null); render(); } }, '取消')));
    }
    if (m.kind === 'err') return el('div', { class: 'msg err' }, icon('alert-triangle'), el('span', { text: m.text }),
      m.auth && m.auth.length ? el('div', { class: 'row wrap' }, m.auth.map((a) => el('button', { class: 'btn sm ghost', onclick: () => authenticate(c, a.id) }, `登录：${a.name || a.id}`))) : null);
    return el('div', { class: 'msg sys small muted', text: m.text });
  }

  function updateTray() {
    const n = [...conns.values()].filter((c) => !c.closed && c.connId).length;
    $('#tray-agents b').textContent = String(n);
  }

  // ---------------------------------------------------------------- 活动（审计）
  const actTab = $('#tab-activity');
  const actFilter = el('select', { class: 'input', id: 'activity-filter' }, el('option', { value: '', text: '全部调用者' }));
  const actList = el('div', { class: 'activity scroll', id: 'activity-list' });
  actTab.append(el('div', { class: 'panel-head' }, actFilter, el('button', { class: 'icon-btn', title: '刷新', onclick: () => loadActivity() }, icon('refresh'))), actList);
  actFilter.addEventListener('change', () => loadActivity());

  const STATUS = { ok: ['circle-check', '成功'], error: ['circle-x', '失败'], denied: ['ban', '被拒绝'] };
  async function loadActivity() {
    let entries = [];
    try { entries = (await FX.k(['audit', 'tail', '-n', '200'])).entries; } catch (e) { actList.replaceChildren(el('div', { class: 'empty error', text: e.message })); return; }
    const agents = [...new Set(entries.map((e) => e.agent))];
    const cur = actFilter.value;
    actFilter.replaceChildren(el('option', { value: '', text: `全部调用者（${agents.length}）` }), ...agents.map((a) => el('option', { value: a, text: a })));
    actFilter.value = agents.includes(cur) ? cur : '';
    const shown = entries.filter((e) => !actFilter.value || e.agent === actFilter.value).reverse();
    actList.replaceChildren();
    if (!shown.length) {
      actList.append(el('div', { class: 'empty' }, icon('history'), el('div', { text: '还没有任何活动' }), el('div', { class: 'muted small', text: '你和智能体通过 foxos（CLI、MCP、ACP、桌面）做的每一次写操作和每一次失败都会记录在 .foxos/audit.jsonl，并显示在这里。' })));
      return;
    }
    for (const e of shown) {
      const [ic, label] = STATUS[e.status] || ['point', e.status];
      const target = (e.targets || []).map((t) => t.path).join('、');
      actList.append(el('div', { class: `act ${e.status}`, 'data-command': e.command },
        el('div', { class: 'act-head' }, icon(ic), el('b', { text: e.command }), el('span', { class: 'muted small', text: label }), el('div', { class: 'spacer' }), el('span', { class: 'muted small', text: FX.hhmmss(e.ts) })),
        el('div', { class: 'small' }, el('span', { class: `who ${/^human/.test(e.agent) ? 'human' : 'agent'}`, text: e.agent }), target ? ` · ${target}` : ''),
        e.error ? el('div', { class: 'small err-text', text: `${e.error.code}：${e.error.message}` }) : e.message ? el('div', { class: 'small muted', text: e.message }) : null,
        target && e.status === 'ok' && /^files\.(delete)$/.test(e.command) ? null : null));
    }
  }
  FX.loadActivity = loadActivity;
  FX.on('audit', () => { if ($('#tab-activity').classList.contains('active')) loadActivity(); });

  loadAgents();
  render();
})();
