// 环境：狐狸OS 自带的隔离环境（Linux 命名空间 / WSL2 / Virtualization.framework）
// 所有操作都走内核命令 foxos env ...，与 CLI / MCP 完全相同，审计记为 human。
'use strict';
(() => {
  const { el, icon } = FX;
  const fmtMB = (v) => (v >= 1024 ? `${(v / 1024).toFixed(1)} GB` : `${(+v || 0).toFixed(1)} MB`);
  const STATE = { running: [FX.t('environments.running_2'), 'ok'], stopped: [FX.t('environments.stopped'), 'muted'], starting: [FX.t('common.starting'), 'warn'] };

  async function act(label, args, after) {
    try { const r = await FX.k(args); FX.toast(FX.t('environments.done', label), 'ok'); if (after) after(r); return r; }
    catch (e) { FX.toast(FX.t('environments.failed', label, e.message, e.hint ? FX.t('editor.hint_paren', e.hint) : ''), 'error'); return null; }
  }

  FX.registerApp('environments', {
    title: () => FX.t('common.environments'),
    icon: 'box-multiple',
    geometry: { w: 1000, h: 640 },
    key: () => 'environments',
    mount(body) {
      const root = el('div', { class: 'envs' });
      const side = el('div', { class: 'envs-side scroll' });
      const main = el('div', { class: 'envs-main scroll' });
      root.append(side, main);
      body.append(root);
      let selected = null; let lastSig = null; let envs = []; let backend = ''; let timer = null; let tab = 'overview';

      async function refresh(soft = false) {
        try { const r = await FX.k(['env', 'list']); envs = r.envs; backend = r.backend; }
        catch (e) { side.replaceChildren(el('div', { class: 'muted small pad', text: FX.t('environments.cannot_read_environments', e.message) })); return; }
        if (selected && !envs.find((x) => x.name === selected)) selected = null;
        renderSide();
        // 后台刷新时，若当前环境的状态没有变化就不重绘详情（保留正在查看的输出）
        const sig = JSON.stringify(envs.find((x) => x.name === selected) || null);
        if (soft && sig === lastSig && main.childElementCount) return;
        lastSig = sig;
        if (selected) renderMain(); else if (!soft || !main.childElementCount) renderEmpty();
      }

      function renderSide() {
        side.replaceChildren(
          el('div', { class: 'row pad' }, el('b', { class: 'grow', text: FX.t('common.environments_2', envs.length) }),
            el('button', { class: 'btn primary sm', 'data-act': 'env-new', onclick: createDialog }, icon('plus'), FX.t('environments.new'))),
          el('div', { class: 'muted small pad', text: FX.t('environments.backend', backend) }),
          ...envs.map((e) => {
            const [label, kind] = STATE[e.state] || [e.state, 'muted'];
            return el('button', { class: `env-item ${e.name === selected ? 'active' : ''}`, 'data-env': e.name, onclick: () => { selected = e.name; tab = 'overview'; renderSide(); renderMain(); } },
              icon(e.state === 'running' ? 'player-play' : 'box'), el('span', { class: 'grow', text: e.name }), el('span', { class: `badge ${kind}`, text: label }));
          }),
          el('div', { class: 'row pad' },
            el('button', { class: 'btn ghost sm', 'data-act': 'env-install', onclick: () => { selected = null; renderInstall(); } }, icon('apps'), FX.t('environments.install_a_system')),
            el('button', { class: 'btn ghost sm', 'data-act': 'env-images', onclick: () => { selected = null; renderImages(); } }, icon('download'), FX.t('environments.images')),
            el('button', { class: 'btn ghost sm', 'data-act': 'env-import', onclick: importDialog }, icon('file-import'), FX.t('environments.import'))));
      }

      function renderEmpty() {
        main.replaceChildren(el('div', { class: 'empty' }, icon('box-multiple'), el('div', { text: envs.length ? FX.t('environments.select_an_environment_on_the_left_to') : FX.t('environments.no_environments_yet_click_new_to') })));
      }

      // ---------------------------------------------------------------- 安装系统（一键目录）
      const GUEST = [['linux', 'Linux', 'brand-ubuntu'], ['windows', 'Windows', 'brand-windows'], ['any', FX.t('environments.from_iso_custom'), 'disc'], ['macos', 'macOS', 'brand-apple']];
      async function renderInstall() {
        clearInterval(timer);
        main.replaceChildren(el('div', { class: 'muted pad', text: FX.t('environments.checking_this_machine_s') }));
        let cat; let doc;
        try { [cat, doc] = await Promise.all([FX.k(['env', 'catalog']), FX.k(['env', 'doctor'])]); }
        catch (e) { main.replaceChildren(el('div', { class: 'pad', text: e.message })); return; }
        const banner = el('div', { class: 'env-doctor' });
        Object.entries(doc.results || {}).forEach(([pid, r]) => {
          banner.append(el('div', { class: `env-doc-row ${r.available ? 'ok' : 'warn'}`, 'data-provider': pid },
            icon(r.available ? 'circle-check' : 'alert-triangle'), el('b', { text: pid }), el('span', { class: 'grow muted small', text: r.available ? FX.t('environments.available') : (r.reason || FX.t('environments.unavailable')) }),
            ...(r.actions || []).map((a) => el('button', { class: 'btn sm', 'data-fix': a.id, onclick: async () => {
              if (a.manual) { FX.confirm(FX.t('environments.manual_step_needed'), a.label); return; }
              if (!await FX.confirm(FX.t('environments.fix'), FX.t('environments.windows_will_ask_for_administrator', a.label), { okText: FX.t('environments.continue') })) return;
              const res = await act(a.label, ['env', 'fix', '--provider', pid, '--action', a.id]);
              if (res && res.reboot_required) FX.confirm(FX.t('environments.restart_required'), FX.t('environments.done_restart_the_computer_then_come'));
              renderInstall();
            } }, icon('tool'), a.label.split(FX.t('common.paren_open'))[0]))));
        });
        const sections = GUEST.map(([g, title, ic]) => {
          const items = cat.entries.filter((e) => e.guest_os === g);
          if (!items.length) return null;
          return el('div', { class: 'env-cat-sec' }, el('h3', {}, icon(ic), ` ${title}`),
            el('div', { class: 'env-cat-grid' }, items.map((e) => el('div', { class: `env-cat ${e.installable ? '' : 'disabled'}`, 'data-entry': e.id },
              el('div', { class: 'row' }, el('b', { class: 'grow', text: e.name }), e.default ? el('span', { class: 'badge ok', text: FX.t('environments.recommended') }) : null),
              el('div', { class: 'muted small', text: e.source.origin || '' }),
              el('div', { class: 'muted small mono', text: e.providers.join(' / ') }),
              e.installable ? el('button', { class: 'btn primary sm', 'data-install': e.id, onclick: () => installDialog(e) }, icon('download'), FX.t('common.install'))
                : el('div', { class: 'small warn-text', text: e.reason || FX.t('environments.unavailable') })))));
        });
        main.replaceChildren(el('h2', { text: FX.t('environments.install_a_system') }),
          el('div', { class: 'muted small', text: FX.t('environments.catalog_version_host_every_system_is', cat.version, cat.host) }), banner, ...sections.filter(Boolean));
      }

      function installDialog(e) {
        const base = e.id.replace(/^(wsl|lxc|hyperv)-/, '').replace(/[^a-z0-9-]+/g, '-').slice(0, 30).replace(/-+$/, '');
        const name = el('input', { class: 'input', name: 'env-name', value: base });
        const needs = e.source.needs || [];
        const url = needs.includes('url') ? el('input', { class: 'input mono', name: 'env-url', placeholder: FX.t('environments.https_or_d_images_rootfs_tar_gz') }) : null;
        const sha = needs.includes('url') ? el('input', { class: 'input mono', name: 'env-sha', placeholder: FX.t('environments.sha256_optional_recommended') }) : null;
        const iso = needs.includes('iso') ? el('input', { class: 'input mono', name: 'env-iso', placeholder: FX.t('environments.full_path_of_the_iso_file_e_g_d_iso') }) : null;
        const mem = e.providers.includes('hyperv') || e.providers.includes('windows-sandbox') ? el('input', { class: 'input', name: 'env-mem', type: 'number', placeholder: FX.t('environments.memory_mb_default_4096') }) : null;
        const page = e.source.download_page ? el('a', { href: '#', class: 'small', onclick: (ev) => { ev.preventDefault(); window.foxos.openExternal ? window.foxos.openExternal(e.source.download_page) : FX.toast(e.source.download_page); } }, FX.t('environments.open_microsoft_s_official_download')) : null;
        const overlay = el('div', { class: 'overlay' });
        const close = () => overlay.remove();
        overlay.append(el('form', { class: 'dialog', onsubmit: async (ev) => {
          ev.preventDefault(); const nm = name.value.trim(); if (!nm) return;
          const args = ['env', 'install', e.id, nm];
          if (url) { if (!url.value.trim()) return; args.push('--url', url.value.trim()); if (sha.value.trim()) args.push('--sha256', sha.value.trim()); }
          if (iso) { if (!iso.value.trim()) return; args.push('--iso', iso.value.trim()); }
          if (mem && mem.value) args.push('--memory-mb', mem.value);
          close();
          runInstall(e, nm, args);
        } }, el('div', { class: 'dialog-title', text: FX.t('common.install_2', e.name) }), el('div', { class: 'muted small', text: FX.t('environments.environment_name_lowercase_letters') }), name, url, sha, iso, page, mem,
          el('div', { class: 'dialog-actions' }, el('button', { type: 'button', class: 'btn ghost', onclick: close }, FX.t('common.cancel')), el('button', { type: 'submit', class: 'btn primary' }, FX.t('common.start_install')))));
        document.body.append(overlay); name.focus();
      }

      async function runInstall(e, nm, args) {
        const bar = el('div', { class: 'progress' }, el('div', { class: 'progress-bar', style: 'width:2%' }));
        const status = el('div', { class: 'muted small', 'data-install-status': nm, text: FX.t('environments.preparing') });
        main.replaceChildren(el('h2', { text: FX.t('environments.installing', e.name) }), el('div', { class: 'muted small', text: FX.t('environments.environment_name', nm) }), bar, status);
        const poll = setInterval(async () => {
          let p; try { p = await FX.k(['env', 'progress', nm]); } catch { return; }
          const frac = p.bytes_total ? p.bytes / p.bytes_total : 0;
          const pct = Math.max(2, Math.round(((p.step || 0) + (p.state === 'done' ? 1 : frac)) / Math.max(1, p.total || p.steps || 1) * 100));
          bar.firstChild.style.width = `${Math.min(100, pct)}%`;
          status.textContent = `${p.why || ''}${p.bytes_total ? FX.t('environments.progress_bytes', fmtMB(p.bytes / 1048576), fmtMB(p.bytes_total / 1048576)) : ''}`;
        }, 1000);
        try {
          await FX.k(args, { timeoutMs: 4 * 3600 * 1000 });
          FX.toast(FX.t('common.installed_2', e.name), 'ok'); selected = nm; await refresh();
        } catch (err) {
          status.textContent = FX.t('environments.install_failed', err.message, err.hint ? FX.t('editor.hint_paren', err.hint) : '');
          main.append(el('button', { class: 'btn sm', onclick: renderInstall }, icon('arrow-left'), FX.t('environments.back_to_catalog')));
        } finally { clearInterval(poll); }
      }

      async function renderImages() {
        main.replaceChildren(el('div', { class: 'muted pad', text: FX.t('environments.reading_images') }));
        let r; try { r = await FX.k(['env', 'images']); } catch (e) { main.replaceChildren(el('div', { class: 'pad', text: e.message })); return; }
        const url = el('input', { class: 'input mono grow', placeholder: 'https://… rootfs.tar.gz / .tar.zst / .foxenv' });
        const sha = el('input', { class: 'input mono', placeholder: FX.t('environments.sha256_optional'), style: 'width:220px' });
        const pull = (img, extra = []) => act(FX.t('environments.download_2', img), ['env', 'pull', img, ...extra], renderImages);
        main.replaceChildren(
          el('h3', { text: FX.t('environments.official_image_catalog') }),
          el('table', { class: 'table' }, el('tbody', {}, r.catalog.map((c) => {
            const have = r.local.find((l) => l.id === c.id);
            return el('tr', {}, el('td', { text: c.name }), el('td', { class: 'mono small', text: c.id }), el('td', { text: `${c.size_mb} MB` }),
              el('td', {}, have ? el('span', { class: 'badge ok', text: FX.t('environments.downloaded') }) : el('button', { class: 'btn sm', 'data-pull': c.id, onclick: () => pull(c.id) }, icon('download'), FX.t('environments.download'))));
          }))),
          el('h3', { text: FX.t('environments.install_from_url') }),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (url.value.trim()) pull(url.value.trim(), sha.value.trim() ? ['--sha256', sha.value.trim()] : []); } }, url, sha, el('button', { class: 'btn primary sm', type: 'submit' }, FX.t('environments.download'))),
          el('h3', { text: FX.t('environments.local_images') }),
          el('table', { class: 'table' }, el('tbody', {}, r.local.map((l) => el('tr', {}, el('td', { text: l.name }), el('td', { class: 'mono small', text: l.id }),
            el('td', { class: 'mono small', text: (l.sha256 || '').slice(0, 16) }), el('td', {}, l.verified ? el('span', { class: 'badge ok', text: FX.t('environments.sha256_verified') }) : el('span', { class: 'badge warn', text: FX.t('environments.not_verified') })))))));
      }

      async function renderMain() {
        clearInterval(timer);
        const e = envs.find((x) => x.name === selected); if (!e) return renderEmpty();
        const running = e.state === 'running';
        const n = e.name;
        const quick = el('div', { class: 'row wrap' },
          running ? el('button', { class: 'btn sm', 'data-act': 'stop', onclick: () => act(FX.t('common.stop'), ['env', 'stop', n], refresh) }, icon('player-stop'), FX.t('common.stop'))
            : el('button', { class: 'btn primary sm', 'data-act': 'start', onclick: () => act(FX.t('common.start'), ['env', 'start', n], refresh) }, icon('player-play'), FX.t('common.start')),
          el('button', { class: 'btn sm', 'data-act': 'restart', onclick: () => act(FX.t('common.restart'), ['env', 'restart', n], refresh) }, icon('refresh'), FX.t('common.restart')),
          el('button', { class: 'btn sm', 'data-act': 'terminal', onclick: () => openShell(n) }, icon('terminal-2'), FX.t('common.terminal')),
          el('button', { class: 'btn sm', 'data-act': 'files', onclick: () => FX.openWindow('files', { path: '' }) }, icon('folder'), FX.t('environments.workspace_files')),
          el('button', { class: 'btn sm', 'data-act': 'editor', onclick: () => FX.openWindow('editor', {}) }, icon('code'), FX.t('common.editor')),
          el('button', { class: 'btn sm', 'data-act': 'clone', onclick: async () => { const nn = await FX.prompt(FX.t('environments.clone_as'), { value: `${n}-copy` }); if (nn) act(FX.t('environments.clone'), ['env', 'clone', n, nn], refresh); } }, icon('copy'), FX.t('environments.clone')),
          el('button', { class: 'btn sm', 'data-act': 'export', onclick: async () => { const out = await FX.prompt(FX.t('environments.export_to_path_in_the_workspace'), { value: `backups/${n}.foxenv` }); if (out) act(FX.t('environments.export'), ['env', 'export', n, '--out', out]); } }, icon('file-export'), FX.t('environments.export')),
          el('button', { class: 'btn ghost sm danger', 'data-act': 'delete', onclick: async () => { if (await FX.confirm(FX.t('environments.delete_environment'), FX.t('environments.delete_its_writable_layer_and', n), { okText: FX.t('common.delete') })) act(FX.t('common.delete'), ['env', 'delete', n], refresh); } }, icon('trash'), FX.t('common.delete')));
        const tabs = el('div', { class: 'env-tabs' }, [['overview', FX.t('environments.overview')], ['snapshots', FX.t('environments.snapshots')], ['actions', FX.t('environments.custom_actions')], ['settings', FX.t('common.settings')], ['logs', FX.t('environments.logs')]].map(([id, t]) =>
          el('button', { class: `env-tab ${tab === id ? 'active' : ''}`, 'data-tab': id, onclick: () => { tab = id; renderMain(); } }, t)));
        const pane = el('div', { class: 'env-pane' });
        const [label, kind] = STATE[e.state] || [e.state, 'muted'];
        main.replaceChildren(el('div', { class: 'row' }, el('h2', { class: 'grow', text: n }), el('span', { class: `badge ${kind}`, text: label })),
          el('div', { class: 'muted small', text: FX.t('environments.image_network_workspace_workspace', e.image, e.network, e.workspace.mode, e.backend) }), quick, tabs, pane);
        let info; try { info = await FX.k(['env', 'info', n]); } catch (err) { pane.append(el('div', { text: err.message })); return; }
        if (tab === 'overview') overview(pane, n, info);
        else if (tab === 'snapshots') snapshots(pane, n, info);
        else if (tab === 'actions') actions(pane, n, info);
        else if (tab === 'settings') settings(pane, n, info);
        else if (tab === 'logs') logs(pane, n);
      }

      function overview(pane, n, info) {
        const cells = {};
        const card = (k, t) => { cells[k] = el('div', { class: 'stat-val', 'data-stat': k, text: '—' }); return el('div', { class: 'stat' }, el('div', { class: 'muted small', text: t }), cells[k]); };
        pane.append(el('div', { class: 'stats' }, card('processes', FX.t('environments.processes')), card('cpu', 'CPU'), card('memory', FX.t('environments.memory')), card('disk', FX.t('environments.writable_layer_disk'))),
          el('div', { class: 'muted small', text: FX.t('environments.limits_mounts_directory', Object.entries(info.limits).map(([k, v]) => `${k}=${v}`).join(FX.t('common.comma')) || FX.t('environments.none'), info.mounts.length, info.path) }));
        let last = null;
        const tick = async () => {
          let s; try { s = (await FX.k(['env', 'stats', n])).stats[n]; } catch { return; }
          const now = performance.now();
          const cpu = last ? Math.max(0, (s.cpu_seconds - last.cpu) / ((now - last.t) / 1000)) * 100 : 0;
          last = { cpu: s.cpu_seconds, t: now };
          cells.processes.textContent = String(s.processes);
          cells.cpu.textContent = FX.t('environments.s_total', cpu.toFixed(0), s.cpu_seconds.toFixed(1));
          cells.memory.textContent = fmtMB(s.memory_mb);
          cells.disk.textContent = fmtMB(s.disk_mb);
        };
        tick(); timer = setInterval(() => { if (!document.body.contains(pane)) return clearInterval(timer); tick(); }, 2000);
      }

      function snapshots(pane, n, info) {
        pane.append(el('div', { class: 'row' }, el('div', { class: 'muted small grow', text: FX.t('environments.stop_the_environment_before_taking') }),
          el('button', { class: 'btn primary sm', 'data-act': 'snapshot', onclick: async () => { const l = await FX.prompt(FX.t('environments.snapshot_note'), { value: '' }); if (l !== null) act(FX.t('environments.snapshots'), ['env', 'snapshot', n, ...(l ? ['--label', l] : [])], renderMain); } }, icon('camera'), FX.t('environments.take_snapshot'))),
          el('table', { class: 'table' }, el('tbody', {}, info.snapshots_detail.length ? info.snapshots_detail.map((s) => el('tr', {}, el('td', { class: 'mono', text: s.id }), el('td', { text: s.label || '' }), el('td', { text: fmtMB(s.size / 1048576) }), el('td', { text: s.by }),
            el('td', {}, el('button', { class: 'btn sm', 'data-restore': s.id, onclick: async () => { if (await FX.confirm(FX.t('environments.restore_snapshot'), FX.t('environments.restore_to_the_current_writable', n, s.id), { okText: FX.t('environments.restore') })) act(FX.t('environments.restore'), ['env', 'restore', n, s.id], renderMain); } }, FX.t('environments.restore')))))
              : [el('tr', {}, el('td', { class: 'muted', text: FX.t('environments.no_snapshots_yet') }))])));
      }

      function actions(pane, n, info) {
        const name = el('input', { class: 'input', placeholder: FX.t('environments.action_name_e_g_test') });
        const cmd = el('input', { class: 'input mono grow', placeholder: FX.t('environments.e_g_cd_workspace_make_test_you_can') });
        const out = el('pre', { class: 'mono small out' });
        pane.append(
          el('table', { class: 'table' }, el('tbody', {}, info.actions_detail.length ? info.actions_detail.map((a) => el('tr', {}, el('td', { text: a.name }), el('td', { class: 'mono small', text: a.command }),
            el('td', {}, el('button', { class: 'btn sm', 'data-run': a.name, onclick: async () => { out.textContent = FX.t('environments.running'); const r = await act(FX.t('environments.run_2', a.name), ['env', 'action', 'run', n, a.name]); if (r) out.textContent = FX.t('environments.exit_code', (r.command || []).join(' '), r.stdout || '', r.stderr || '', r.exit_code); } }, icon('player-play'), FX.t('environments.run')))))
              : [el('tr', {}, el('td', { class: 'muted', text: FX.t('environments.no_custom_actions_yet') }))])),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (name.value.trim() && cmd.value.trim()) act(FX.t('environments.add_action'), ['env', 'action', 'add', n, name.value.trim(), '--command', cmd.value], renderMain); } }, name, cmd, el('button', { class: 'btn primary sm', type: 'submit' }, FX.t('environments.add'))), out);
      }

      function settings(pane, n, info) {
        const L = info.limits || {};
        const mem = el('input', { class: 'input', type: 'number', min: 0, value: L.memory_mb || '', placeholder: FX.t('environments.unlimited') });
        const pids = el('input', { class: 'input', type: 'number', min: 0, value: L.pids || '', placeholder: FX.t('environments.unlimited') });
        const cpus = el('input', { class: 'input', type: 'number', min: 0, step: 0.5, value: L.cpus || '', placeholder: FX.t('environments.unlimited') });
        const net = el('select', { class: 'input' }, ['host', 'none'].map((v) => el('option', { value: v, selected: info.network === v, text: v === 'host' ? FX.t('environments.host_shares_the_host_network') : FX.t('environments.none_loopback_only') })));
        const wm = el('select', { class: 'input' }, ['rw', 'ro', 'none'].map((v) => el('option', { value: v, selected: info.workspace.mode === v, text: { rw: FX.t('environments.read_write'), ro: FX.t('environments.read_only'), none: FX.t('environments.not_mounted') }[v] })));
        const src = el('input', { class: 'input mono grow', placeholder: FX.t('environments.host_path') });
        const tgt = el('input', { class: 'input mono', placeholder: FX.t('environments.path_inside_the_environment_e_g_data') });
        const ro = el('input', { type: 'checkbox' });
        pane.append(
          el('form', { class: 'form-grid', onsubmit: (e) => { e.preventDefault(); act(FX.t('environments.save_settings'), ['env', 'limits', n, '--memory-mb', String(+mem.value || 0), '--pids', String(+pids.value || 0), '--cpus', String(+cpus.value || 0), '--network', net.value, '--workspace-mode', wm.value], renderMain); } },
            el('label', { text: FX.t('environments.memory_limit_mb') }), mem, el('label', { text: FX.t('environments.process_limit') }), pids, el('label', { text: FX.t('environments.cpu_limit_cores') }), cpus,
            el('label', { text: FX.t('environments.network') }), net, el('label', { text: FX.t('common.workspace') }), wm,
            el('div', {}), el('button', { class: 'btn primary sm', type: 'submit', 'data-act': 'save-limits' }, FX.t('environments.save_applies_on_next_start'))),
          el('div', { class: 'muted small', text: info.limits_note || '' }),
          el('h3', { text: FX.t('environments.mounts') }),
          el('table', { class: 'table' }, el('tbody', {}, info.mounts.length ? info.mounts.map((m) => el('tr', {}, el('td', { class: 'mono', text: m.source }), el('td', { class: 'mono', text: m.target }), el('td', { text: m.readonly ? FX.t('environments.read_only') : FX.t('environments.read_write') }),
            el('td', {}, el('button', { class: 'btn ghost sm', onclick: () => act(FX.t('environments.remove_mount'), ['env', 'mount', n, '--source', m.source, '--target', m.target, '--remove'], renderMain) }, FX.t('environments.remove')))))
              : [el('tr', {}, el('td', { class: 'muted', text: FX.t('environments.no_extra_mounts') }))])),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (src.value && tgt.value) act(FX.t('environments.add_mount'), ['env', 'mount', n, '--source', src.value, '--target', tgt.value, ...(ro.checked ? ['--readonly'] : [])], renderMain); } },
            src, tgt, el('label', { class: 'row' }, ro, FX.t('environments.read_only')), el('button', { class: 'btn primary sm', type: 'submit' }, FX.t('environments.mounts'))));
      }

      async function logs(pane, n) {
        const pre = el('pre', { class: 'mono small out', 'data-logs': n });
        pane.append(pre);
        try { const r = await FX.k(['env', 'logs', n, '-n', '200']); pre.textContent = Object.entries(r.logs || {}).map(([f, ls]) => `== ${f} ==\n${ls.join('\n')}`).join('\n\n') || FX.t('environments.no_logs'); } catch (e) { pre.textContent = e.message; }
      }

      function openShell(n) {
        // 终端里的 PATH 已包含 foxos 命令（与内置终端相同）
        const isWin = FX.env.platform === 'win32';
        FX.openWindow('terminal', { title: FX.t('common.environment', n), command: isWin ? 'powershell.exe' : (FX.env.shell || '/bin/sh'), args: isWin ? ['-NoProfile', '-Command', `foxos env shell ${n}`] : ['-c', `foxos env shell '${n}'`] });
      }

      async function createDialog() {
        let imgs = { catalog: [], local: [] }; try { imgs = await FX.k(['env', 'images']); } catch { /* 下面会显示错误 */ }
        const ids = [...new Set([...imgs.local.map((l) => l.id), ...imgs.catalog.map((c) => c.id)])];
        const name = el('input', { class: 'input', placeholder: FX.t('environments.name_e_g_dev'), name: 'env-name' });
        const image = el('select', { class: 'input', name: 'env-image' }, ids.map((i) => el('option', { value: i, text: `${i}${imgs.local.find((l) => l.id === i) ? '' : FX.t('environments.download_needed')}` })));
        const net = el('select', { class: 'input' }, el('option', { value: 'host', text: FX.t('environments.share_host_network') }), el('option', { value: 'none', text: FX.t('environments.no_network') }));
        const wm = el('select', { class: 'input' }, el('option', { value: 'rw', text: FX.t('environments.workspace_read_write') }), el('option', { value: 'ro', text: FX.t('environments.workspace_read_only') }), el('option', { value: 'none', text: FX.t('environments.don_t_mount_the_workspace') }));
        const overlay = el('div', { class: 'overlay' });
        const close = () => overlay.remove();
        overlay.append(el('form', { class: 'dialog', onsubmit: async (e) => {
          e.preventDefault(); const nm = name.value.trim(); if (!nm) return;
          close();
          if (!imgs.local.find((l) => l.id === image.value)) { FX.toast(FX.t('environments.downloading_image', image.value)); if (!await act(FX.t('environments.download_image'), ['env', 'pull', image.value])) return; }
          await act(FX.t('environments.create'), ['env', 'create', nm, '--image', image.value, '--network', net.value, '--workspace-mode', wm.value], () => { selected = nm; });
          refresh();
        } }, el('div', { class: 'dialog-title', text: FX.t('environments.new_environment') }), name, image, net, wm,
          el('div', { class: 'dialog-actions' }, el('button', { type: 'button', class: 'btn ghost', onclick: close }, FX.t('common.cancel')), el('button', { type: 'submit', class: 'btn primary' }, FX.t('environments.create')))));
        document.body.append(overlay); name.focus();
      }

      async function importDialog() {
        const f = await FX.prompt(FX.t('environments.foxenv_file_path_in_the_workspace'), { value: 'backups/' }); if (!f) return;
        const nm = await FX.prompt(FX.t('environments.new_environment_name'), { value: '' }); if (!nm) return;
        act(FX.t('environments.import'), ['env', 'import', f, '--name', nm], () => { selected = nm; refresh(); });
      }

      // 审计日志有新记录（CLI / MCP / 智能体的操作）时刷新，合并 600ms 内的多次变化
      let pend = null;
      FX.on('audit', () => { if (!document.body.contains(root) || pend) return; pend = setTimeout(() => { pend = null; refresh(true); }, 600); });
      refresh();
      return { refresh, dispose: () => clearInterval(timer) };
    },
  });
})();
