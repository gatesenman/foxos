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
  // 运行位置：宿主（默认）或某个运行中的狐狸OS 环境
  // 轻量沙箱：宿主上运行，但只能读写工作空间（见 docs/sandbox.md）
  const baseWhere = () => [el('option', { value: '', text: FX.t('panel.host') }), el('option', { value: '@sandbox', text: FX.t('panel.light_sandbox') }), el('option', { value: '@sandbox-offline', text: FX.t('panel.light_sandbox_offline') })];
  const where = el('select', { class: 'input', id: 'agent-where', title: FX.t('panel.where_the_agent_runs'), onfocus: () => loadEnvs() }, ...baseWhere());
  async function loadEnvs() {
    const cur = where.value;
    let envs = [];
    try { envs = (await FX.k(['env', 'list'])).envs.filter((e) => e.state === 'running' && e.backend === 'linux-ns'); } catch { /* 无环境后端 */ }
    where.replaceChildren(...baseWhere(), ...envs.map((e) => el('option', { value: e.name, text: FX.t('common.environment', e.name) })));
    where.value = cur.startsWith('@') || envs.find((e) => e.name === cur) ? cur : '';
  }
  const startBtn = el('button', { class: 'btn primary sm', id: 'agent-start', onclick: () => picker.value && FX.startAgentSession(picker.value, { env: where.value || null }) }, icon('player-play'), FX.t('common.start'));
  const sessList = el('div', { class: 'sess-tabs' });
  const transcript = el('div', { class: 'transcript scroll', id: 'transcript' });
  const input = el('textarea', { class: 'input composer-input', id: 'composer', rows: '3', placeholder: FX.t('panel.give_the_agent_a_task_enter_to_send') });
  // 没有装 ACP 智能体时给出去处（应用中心 → ACP 智能体），而不是只显示“没有已安装的 ACP 智能体”
  const installAgentsBtn = el('button', { class: 'btn ghost sm', id: 'panel-install-agents', hidden: true, onclick: () => FX.openWindow('appcenter', {}) }, FX.t('panel.install_acp_agents'));
  const sendBtn = el('button', { class: 'btn primary', id: 'composer-send', onclick: () => send() }, icon('send'), FX.t('panel.send'));
  const stopBtn = el('button', { class: 'btn ghost', id: 'composer-stop', onclick: () => active && cancel(active) }, icon('player-stop'), FX.t('common.stop'));
  sessionTab.append(
    el('div', { class: 'panel-head' }, picker, where, startBtn, installAgentsBtn),
    sessList, transcript,
    el('div', { class: 'composer' }, input, el('div', { class: 'row' }, el('span', { class: 'muted small grow', id: 'composer-hint' }), stopBtn, sendBtn)));
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });

  async function loadAgents() {
    let list = [];
    try { list = await window.foxos.agents.installed(); } catch { /* 忽略 */ }
    picker.replaceChildren(...(list.length ? list.map((a) => el('option', { value: a.id, text: `${a.name || a.id} ${a.version || ''}` })) : [el('option', { value: '', text: FX.t('panel.no_acp_agents_installed') })]));
    startBtn.disabled = !list.length;
    installAgentsBtn.hidden = list.length > 0;
    render();
  }
  FX.on('agents-changed', loadAgents);

  function push(c, item) { c.log.push(item); if (c === conns.get(active)) render(); }

  FX.startAgentSession = async (agentId, opts = {}) => {
    const c = { agentId, name: agentId, sessionId: null, log: [], status: FX.t('common.starting'), busy: false };
    const tmpId = `pending-${Date.now()}`;
    conns.set(tmpId, c); active = tmpId; render();
    try {
      const r = await window.foxos.acp.start(agentId, opts);
      conns.delete(tmpId); conns.set(r.connId, c); active = r.connId; c.connId = r.connId;
      c.init = r.init; c.identity = r.identity;
      const ai = r.init.agentInfo || {};
      c.name = ai.title || ai.name || agentId;
      push(c, { kind: 'sys', text: FX.t('panel.connected_to_acp_protocol_v_identity', c.name, ai.version ? ` ${ai.version}` : '', r.init.protocolVersion, r.identity, opts.env ? (opts.env.startsWith('@sandbox') ? FX.t('panel.running_in_the_light_sandbox_can', opts.env === '@sandbox-offline' ? FX.t('panel.offline') : '') : FX.t('panel.running_in_environment_workspace_at', opts.env)) : '') });
      c.authMethods = r.init.authMethods || [];
      await newSession(c);
    } catch (e) {
      c.status = FX.t('common.failed');
      push(c, { kind: 'err', text: FX.t('panel.failed_to_start', e.message) });
    }
    render();
    updateTray();
  };

  async function newSession(c) {
    c.status = FX.t('panel.creating_session');
    render();
    try {
      const s = await window.foxos.acp.newSession(c.connId);
      c.sessionId = s.sessionId;
      c.status = FX.t('panel.ready');
      push(c, { kind: 'sys', text: FX.t('panel.session_created_the_agent_has_the', s.sessionId) });
    } catch (e) {
      c.status = FX.t('panel.sign_in_required');
      const needsAuth = e.code === -32000 || /auth/i.test(e.message);
      push(c, { kind: 'err', text: FX.t('panel.failed_to_create_session', e.message), auth: needsAuth ? c.authMethods : null });
      if (!c.authMethods.length || !needsAuth) c.status = FX.t('common.failed');
    }
    render();
  }

  async function authenticate(c, methodId) {
    push(c, { kind: 'sys', text: FX.t('panel.signing_in', methodId) });
    try { await window.foxos.acp.authenticate(c.connId, methodId); push(c, { kind: 'sys', text: FX.t('panel.signed_in') }); await newSession(c); } catch (e) { push(c, { kind: 'err', text: FX.t('panel.sign_in_failed_you_can_also_enter_an', e.message) }); }
  }

  async function send() {
    const c = conns.get(active);
    const text = input.value.trim();
    if (!c || !text || !c.sessionId || c.busy) return;
    input.value = '';
    push(c, { kind: 'user', text });
    c.busy = true; c.status = FX.t('panel.working'); render();
    try {
      const r = await window.foxos.acp.prompt(c.connId, c.sessionId, text);
      push(c, { kind: 'sys', text: FX.t('panel.turn_ended', ({ end_turn: FX.t('setup.done'), cancelled: FX.t('panel.cancelled'), max_tokens: FX.t('panel.length_limit_reached'), refusal: FX.t('panel.refused_by_the_agent'), max_turn_requests: FX.t('panel.request_limit_reached') })[r.stopReason] || r.stopReason) });
    } catch (e) { push(c, { kind: 'err', text: e.message }); }
    c.busy = false; c.status = FX.t('panel.ready'); render(); updateTray();
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
      else if (t === 'tool_call') c.log.push({ kind: 'tool', id: u.toolCallId, title: u.title || u.kind || FX.t('panel.tool_call'), status: u.status || 'pending', toolKind: u.kind });
      else if (t === 'tool_call_update') { const tc = c.log.find((x) => x.kind === 'tool' && x.id === u.toolCallId); if (tc) { if (u.status) tc.status = u.status; if (u.title) tc.title = u.title; } }
      else if (t === 'plan') c.log.push({ kind: 'plan', entries: u.entries || [] });
      else return;
      if (c === conns.get(active)) render();
    } else if (ev.type === 'fs') {
      push(c, { kind: 'fs', text: `${ev.op === 'write' ? FX.t('panel.write') : FX.t('panel.read')} ${ev.path}` });
    } else if (ev.type === 'closed') {
      c.status = FX.t('panel.exited'); c.closed = true; push(c, { kind: 'err', text: ev.reason }); updateTray();
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
      el('i', { class: 'ti ti-x', title: FX.t('panel.end_session'), onclick: (e) => { e.stopPropagation(); if (c.connId) window.foxos.acp.stop(c.connId); conns.delete(id); if (active === id) active = conns.keys().next().value ?? null; render(); updateTray(); } }))));
    const c = conns.get(active);
    transcript.replaceChildren();
    if (!c) {
      transcript.append(el('div', { class: 'empty' }, icon('robot'), el('div', { text: FX.t('panel.no_agent_session_yet') }),
        el('div', { class: 'muted small', text: FX.t('panel.pick_an_installed_acp_agent_above') }),
        el('button', { class: 'btn ghost sm', onclick: () => FX.openWindow('appcenter', {}) }, icon('apps'), FX.t('common.open_app_center'))));
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
    if (m.kind === 'thought') return el('details', { class: 'msg thought' }, el('summary', {}, icon('bulb'), FX.t('panel.thinking')), el('div', { class: 'small muted', text: m.text }));
    if (m.kind === 'tool') return el('div', { class: `msg tool ${m.status}` }, icon(m.status === 'completed' ? 'circle-check' : m.status === 'failed' ? 'circle-x' : 'loader-2'), el('span', { text: m.title }), el('span', { class: 'muted small', text: m.status }));
    if (m.kind === 'fs') return el('div', { class: 'msg fs' }, icon('file-text'), el('span', { class: 'small', text: m.text }));
    if (m.kind === 'plan') return el('div', { class: 'msg plan' }, el('div', { class: 'small muted', text: FX.t('panel.plan') }), m.entries.map((e) => el('div', { class: `plan-item ${e.status}` }, icon(e.status === 'completed' ? 'square-check' : 'square'), e.content)));
    if (m.kind === 'perm') {
      const p = m.params || {};
      const tc = p.toolCall || {};
      return el('div', { class: 'msg perm' }, el('div', {}, icon('shield-question'), el('b', { text: FX.t('panel.the_agent_requests_permission') }), tc.title || tc.kind || ''),
        m.decided ? el('div', { class: 'muted small', text: FX.t('panel.chosen', m.decided) })
          : el('div', { class: 'row wrap' }, (p.options || []).map((o) => el('button', { class: `btn sm ${/reject/.test(o.kind) ? 'ghost' : 'primary'}`, onclick: () => { m.decided = o.name; window.foxos.acp.replyPermission(m.reqId, o.optionId); render(); } }, o.name)),
            el('button', { class: 'btn sm ghost', onclick: () => { m.decided = FX.t('common.cancel'); window.foxos.acp.replyPermission(m.reqId, null); render(); } }, FX.t('common.cancel'))));
    }
    if (m.kind === 'err') return el('div', { class: 'msg err' }, icon('alert-triangle'), el('span', { text: m.text }),
      m.auth && m.auth.length ? el('div', { class: 'row wrap' }, m.auth.map((a) => el('button', { class: 'btn sm ghost', onclick: () => authenticate(c, a.id) }, FX.t('panel.sign_in', a.name || a.id)))) : null);
    return el('div', { class: 'msg sys small muted', text: m.text });
  }

  function updateTray() {
    const n = [...conns.values()].filter((c) => !c.closed && c.connId).length;
    $('#tray-agents b').textContent = String(n);
  }

  // ---------------------------------------------------------------- 活动（审计）
  const actTab = $('#tab-activity');
  const actFilter = el('select', { class: 'input', id: 'activity-filter' }, el('option', { value: '', text: FX.t('panel.all_callers_2') }));
  const actList = el('div', { class: 'activity scroll', id: 'activity-list' });
  actTab.append(el('div', { class: 'panel-head' }, actFilter, el('button', { class: 'icon-btn', title: FX.t('common.refresh'), onclick: () => loadActivity() }, icon('refresh'))), actList);
  actFilter.addEventListener('change', () => loadActivity());

  const STATUS = { ok: ['circle-check', FX.t('panel.succeeded')], error: ['circle-x', FX.t('common.failed')], denied: ['ban', FX.t('panel.denied')] };
  async function loadActivity() {
    let entries = [];
    try { entries = (await FX.k(['audit', 'tail', '-n', '200'])).entries; } catch (e) { actList.replaceChildren(el('div', { class: 'empty error', text: e.message })); return; }
    const agents = [...new Set(entries.map((e) => e.agent))];
    const cur = actFilter.value;
    actFilter.replaceChildren(el('option', { value: '', text: FX.t('panel.all_callers', agents.length) }), ...agents.map((a) => el('option', { value: a, text: a })));
    actFilter.value = agents.includes(cur) ? cur : '';
    const shown = entries.filter((e) => !actFilter.value || e.agent === actFilter.value).reverse();
    actList.replaceChildren();
    if (!shown.length) {
      actList.append(el('div', { class: 'empty' }, icon('history'), el('div', { text: FX.t('panel.no_activity_yet') }), el('div', { class: 'muted small', text: FX.t('panel.every_write_and_every_failure_you_or') })));
      return;
    }
    for (const e of shown) {
      const [ic, label] = STATUS[e.status] || ['point', e.status];
      const target = (e.targets || []).map((t) => t.path).join(FX.t('common.list_sep'));
      actList.append(el('div', { class: `act ${e.status}`, 'data-command': e.command },
        el('div', { class: 'act-head' }, icon(ic), el('b', { text: e.command }), el('span', { class: 'muted small', text: label }), el('div', { class: 'spacer' }), el('span', { class: 'muted small', text: FX.hhmmss(e.ts) })),
        el('div', { class: 'small' }, el('span', { class: `who ${/^human/.test(e.agent) ? 'human' : 'agent'}`, text: e.agent }), target ? ` · ${target}` : ''),
        e.error ? el('div', { class: 'small err-text', text: FX.t('panel.error_code_message', e.error.code, e.error.message) }) : e.message ? el('div', { class: 'small muted', text: e.message }) : null,
        target && e.status === 'ok' && /^files\.(delete)$/.test(e.command) ? null : null));
    }
  }
  FX.loadActivity = loadActivity;
  FX.on('audit', () => { if ($('#tab-activity').classList.contains('active')) loadActivity(); });

  loadAgents();
  render();
})();
