// 狐狸OS 电脑：桌面客户端的主窗口。显示狐狸OS 虚拟机（或远程狐狸OS）的画面，管理它的生命周期，
// 并且是所有动作的去处——应用中心安装、打开 Word、终端、文件、智能体都在这台电脑里执行，不碰本机。
'use strict';
(() => {
  const { el, icon } = FX;
  // RFB 字节流：主进程把 TCP / ssh -W 的数据转给这里，noVNC 用一个“类 WebSocket”的通道对象读写
  const chans = new Map(); // id -> { ch, queue: [] }
  window.foxos.rfb.onData((id, data) => {
    const c = chans.get(id); if (!c) return;
    const buf = data.slice().buffer;
    if (c.ch && c.ch.onmessage) c.ch.onmessage({ data: buf }); else c.queue.push(buf);
  });
  window.foxos.rfb.onClose((id) => { const c = chans.get(id); chans.delete(id); if (c && c.ch) { c.ch.readyState = 'closed'; if (c.ch.onclose) c.ch.onclose({ code: 1000, reason: '', wasClean: true }); } });
  window.foxos.rfb.onError((id, msg) => { const c = chans.get(id); if (c && c.ch && c.ch.onerror) c.ch.onerror(new Error(msg)); });

  function channel(id) {
    const ch = {
      binaryType: 'arraybuffer', protocol: '', readyState: 'open', onopen: null, onclose: null, onerror: null, _onmessage: null,
      send(d) { window.foxos.rfb.write(id, d instanceof ArrayBuffer ? new Uint8Array(d) : new Uint8Array(d.buffer, d.byteOffset, d.byteLength).slice()); },
      close() { if (ch.readyState === 'closed') return; ch.readyState = 'closed'; window.foxos.rfb.close(id); },
    };
    const rec = { ch, queue: [] };
    // noVNC 在 attach 时设置 onmessage：设置后把连接建立前收到的字节交给它
    Object.defineProperty(ch, 'onmessage', {
      enumerable: true,
      get: () => ch._onmessage,
      set: (f) => { ch._onmessage = f; if (f) { const q = rec.queue.splice(0); setTimeout(() => q.forEach((b) => f({ data: b })), 0); } },
    });
    chans.set(id, rec);
    return ch;
  }

  const KIND = { env: 'client.kind_env', ssh: 'client.kind_ssh', machine: 'client.kind_machine' };

  FX.registerApp('computer', {
    title: () => FX.t('client.computer_title'),
    icon: 'device-desktop',
    geometry: { w: 1120, h: 760 },
    key: () => 'computer',
    mount(body) {
      const statusEl = el('span', { class: 'badge muted', 'data-guest-status': '', text: '…' });
      const labelEl = el('b', { class: 'grow', 'data-guest-label': '' });
      const hostEl = el('span', { class: 'badge', 'data-host-exec': FX.env.hostExecution ? 'on' : 'off', title: FX.t('client.host_execution_hint'), text: FX.env.hostExecution ? FX.t('client.host_execution_on_badge') : FX.t('client.host_execution_off_badge') });
      const btn = (act, ic, label, fn) => el('button', { class: 'btn ghost sm', 'data-act': act, onclick: fn }, icon(ic), label);
      const bar = el('div', { class: 'row pad computer-bar' }, icon('device-desktop'), labelEl, statusEl, hostEl,
        btn('guest-start', 'player-play', FX.t('client.start'), () => lifecycle('start')),
        btn('guest-stop', 'player-stop', FX.t('client.stop'), () => lifecycle('stop')),
        btn('guest-view', 'refresh', FX.t('client.reconnect_view'), () => connectView()),
        btn('guest-terminal', 'terminal-2', FX.t('common.terminal'), () => FX.openWindow('terminal', {})),
        btn('guest-change', 'plug-connected', FX.t('client.change'), () => renderSetup()));
      const view = el('div', { class: 'computer-view', 'data-guest-view': '' });
      const note = el('div', { class: 'muted small pad', 'data-guest-note': '' });
      const main = el('div', { class: 'computer-main' }, view);
      body.append(el('div', { class: 'computer' }, bar, note, main));
      let rfb = null; let st = null;

      function disconnectView() { if (rfb) { try { rfb.disconnect(); } catch { /* 已断开 */ } rfb = null; } view.replaceChildren(); }

      async function connectView() {
        disconnectView();
        view.replaceChildren(el('div', { class: 'empty' }, icon('loader-2'), el('div', { text: FX.t('client.connecting_view') })));
        let info;
        try { info = await window.foxos.rfb.open(); } catch (e) {
          view.replaceChildren(el('div', { class: 'empty', 'data-view-error': '' }, icon('screen-share-off'), el('div', { text: FX.t('client.view_unavailable', e.message) })));
          return;
        }
        view.replaceChildren();
        view.dataset.via = info.via;
        rfb = new window.NoVNCRFB(view, channel(info.id), { shared: true });
        rfb.scaleViewport = true;
        rfb.resizeSession = false;
        rfb.focusOnClick = true;
        rfb.addEventListener('connect', () => { view.dataset.connected = '1'; note.textContent = FX.t(info.via === 'console' ? 'client.view_console' : 'client.view_desktop'); });
        rfb.addEventListener('disconnect', (e) => { view.dataset.connected = '0'; if (!e.detail.clean) note.textContent = FX.t('client.view_lost'); });
        rfb.addEventListener('credentialsrequired', async () => {
          const pw = await FX.prompt(FX.t('client.vnc_password'), {});
          if (pw != null) rfb.sendCredentials({ password: pw }); else disconnectView();
        });
      }

      async function lifecycle(op) {
        if (!st || !st.config || st.config.kind !== 'env') { FX.toast(FX.t('client.lifecycle_env_only'), 'error'); return; }
        try { await FX.k(['env', op, st.config.env]); FX.toast(FX.t(op === 'start' ? 'client.started' : 'client.stopped', st.config.env), 'ok'); }
        catch (e) { FX.toast(e.message, 'error'); }
        await refresh(); if (op === 'start') connectView(); else disconnectView();
      }

      async function refresh() {
        statusEl.textContent = '…';
        try { st = await window.foxos.guest.status(); } catch (e) { st = { configured: false, error: e.message }; }
        if (!st.configured) { labelEl.textContent = FX.t('client.not_connected'); statusEl.textContent = FX.t('client.not_connected'); statusEl.className = 'badge warn'; return st; }
        labelEl.textContent = `${st.label || ''} · ${FX.t(KIND[st.config.kind])}${st.provider ? ` · ${st.provider}` : ''}`;
        const ok = st.reach && st.reach.ok;
        statusEl.textContent = st.error ? st.error : ok ? FX.t('client.reachable', st.reach.version || '') : (st.state === 'running' ? FX.t('client.booting') : (st.state || FX.t('client.unreachable')));
        statusEl.className = `badge ${ok ? 'ok' : 'warn'}`;
        statusEl.dataset.guestStatus = ok ? 'ok' : (st.state || 'down');
        statusEl.title = (st.reach && st.reach.error) || '';
        note.textContent = ok ? '' : (st.reach && st.reach.error) || '';
        return st;
      }

      // ---------------------------------------------------------------- 连接 / 新建
      async function renderSetup() {
        disconnectView();
        const pane = el('div', { class: 'computer-setup scroll pad', 'data-guest-setup': '' });
        view.replaceChildren(pane);
        pane.append(el('h2', { text: FX.t('client.setup_title') }), el('p', { class: 'muted', text: FX.t('client.setup_intro') }));
        // A. 本机虚拟机
        const envBox = el('div', { class: 'card', 'data-setup': 'env' }, el('h3', {}, icon('box'), ` ${FX.t('client.kind_env')}`), el('div', { class: 'muted small', text: '…' }));
        // B. 远程（SSH）
        const f = { host: el('input', { placeholder: '192.168.1.20', 'data-f': 'host' }), port: el('input', { value: '22', size: 5, 'data-f': 'port' }), user: el('input', { value: 'foxos', 'data-f': 'user' }), key: el('input', { placeholder: FX.t('client.key_optional'), 'data-f': 'key', class: 'grow' }) };
        const sshBox = el('div', { class: 'card', 'data-setup': 'ssh' }, el('h3', {}, icon('world'), ` ${FX.t('client.kind_ssh')}`),
          el('div', { class: 'muted small', text: FX.t('client.ssh_intro') }),
          el('div', { class: 'row' }, FX.t('client.host'), f.host, FX.t('client.port'), f.port, FX.t('client.user'), f.user),
          el('div', { class: 'row' }, FX.t('client.key'), f.key, el('button', { class: 'btn ghost sm', onclick: async () => { const p = await window.foxos.chooseFile(); if (p) f.key.value = p; } }, icon('key'), FX.t('client.choose'))),
          el('div', { class: 'row' }, el('button', { class: 'btn primary sm', 'data-act': 'connect-ssh', onclick: () => use({ kind: 'ssh', host: f.host.value.trim(), port: +f.port.value || 22, user: f.user.value.trim() || 'foxos', key: f.key.value.trim() || null }) }, icon('plug-connected'), FX.t('client.connect'))));
        // C. 配对过的狐狸OS（foxos machine pair）
        const mBox = el('div', { class: 'card', 'data-setup': 'machine' }, el('h3', {}, icon('link'), ` ${FX.t('client.kind_machine')}`), el('div', { class: 'muted small', text: '…' }));
        pane.append(envBox, sshBox, mBox);
        fillEnvs(envBox); fillMachines(mBox, f);
      }

      async function use(g) {
        if (g.kind === 'ssh' && !g.host) { FX.toast(FX.t('client.host_required'), 'error'); return; }
        try { await window.foxos.guest.set(g); } catch (e) { FX.toast(e.message, 'error'); return; }
        const s = await refresh();
        if (s.reach && !s.reach.ok) FX.toast(FX.t('client.saved_unreachable', s.reach.error || ''), 'error'); else FX.toast(FX.t('client.connected', s.label || ''), 'ok');
        FX.apps = null; FX.detectApps(true).catch(() => {});
        connectView();
      }

      async function fillEnvs(box) {
        let envs = []; let presets = []; let providers = [];
        try { envs = (await FX.k(['env', 'list'])).envs || []; } catch (e) { box.lastChild.textContent = e.message; return; }
        try { presets = ((await FX.k(['env', 'catalog', '--presets'])).entries || []).filter((p) => /^foxos-(image|iso)$/.test(p.kind)); } catch { /* 目录不可用 */ }
        try { providers = ((await FX.k(['env', 'providers'])).providers || []).filter((p) => p.host_supported && p.guest_os !== 'windows' && p.id !== 'linux-ns' && (!p.doctor || p.doctor.available !== false)); } catch { /* 忽略 */ }
        const list = envs.length ? envs.map((e) => el('div', { class: 'row', 'data-env': e.name }, icon(e.state === 'running' ? 'player-play' : 'box'), el('span', { class: 'grow', text: `${e.name} · ${e.provider || e.backend || ''} · ${e.state}` }),
          el('button', { class: 'btn sm', 'data-act': 'use-env', onclick: () => use({ kind: 'env', env: e.name }) }, FX.t('client.use_this')))) : [el('div', { class: 'muted small', text: FX.t('client.no_vms') })];
        const name = el('input', { value: envs.find((e) => e.name === 'foxos') ? `foxos-${envs.length + 1}` : 'foxos', size: 12, 'data-f': 'env-name' });
        const preset = el('select', { 'data-f': 'preset' }, presets.map((p) => el('option', { value: p.id, text: p.name })));
        const prov = el('select', { 'data-f': 'provider' }, providers.length ? providers.map((p) => el('option', { value: p.id, text: p.name })) : [el('option', { value: '', text: FX.t('client.no_provider') })]);
        box.replaceChildren(box.firstChild, ...list,
          el('div', { class: 'muted small', text: FX.t('client.create_intro') }),
          el('div', { class: 'row' }, FX.t('client.name'), name, preset, prov,
            el('button', { class: 'btn primary sm', 'data-act': 'create-vm', disabled: !presets.length || !providers.length, onclick: () => {
              const n = name.value.trim(); if (!/^[a-z0-9][a-z0-9-]{0,30}$/.test(n)) { FX.toast(FX.t('client.bad_name'), 'error'); return; }
              const argv = ['env', 'install', preset.value, n, '--provider', prov.value, '--start'];
              FX.openWindow('terminal', { title: FX.t('client.creating_vm', n), lifecycleArgv: argv, onExit: async (code) => { if (code === 0) await use({ kind: 'env', env: n }); else FX.toast(FX.t('client.create_failed', code), 'error'); } });
            } }, icon('plus'), FX.t('client.create_vm'))));
      }

      async function fillMachines(box, f) {
        let ms = [];
        try { ms = (await FX.k(['machine', 'list'])).machines || []; } catch (e) { box.lastChild.textContent = e.message; return; }
        const rows = ms.filter((m) => m.name !== 'local').map((m) => el('div', { class: 'row', 'data-machine': m.name }, icon('device-laptop'), el('span', { class: 'grow', text: `${m.name} · ${m.url || ''}` }),
          el('button', { class: 'btn sm', 'data-act': 'use-machine', onclick: () => use({ kind: 'machine', machine: m.name, ssh: f.host.value.trim() ? { host: f.host.value.trim(), port: +f.port.value || 22, user: f.user.value.trim() || 'foxos', key: f.key.value.trim() || null } : null }) }, FX.t('client.use_this'))));
        box.replaceChildren(box.firstChild, el('div', { class: 'muted small', text: FX.t('client.machine_intro') }), ...(rows.length ? rows : [el('div', { class: 'muted small', text: FX.t('client.no_machines') })]),
          el('div', { class: 'row' }, el('button', { class: 'btn ghost sm', 'data-act': 'pair', onclick: pair }, icon('link-plus'), FX.t('client.pair_new'))));
      }

      async function pair() {
        const url = await FX.prompt(FX.t('client.pair_url'), { placeholder: 'https://192.168.1.20:7443' }); if (!url) return;
        const code = await FX.prompt(FX.t('client.pair_code'), {}); if (!code) return;
        const name = await FX.prompt(FX.t('client.name'), { value: 'foxos-remote' }); if (!name) return;
        try { await FX.k(['machine', 'pair', '--name', name, '--url', url, '--code', code]); FX.toast(FX.t('client.paired', name), 'ok'); renderSetup(); }
        catch (e) { FX.toast(e.message, 'error'); }
      }

      refresh().then((s) => { if (!s.configured) renderSetup(); else connectView(); });
      return { dispose: disconnectView, status: () => st, connected: () => view.dataset.connected === '1' };
    },
  });
})();
