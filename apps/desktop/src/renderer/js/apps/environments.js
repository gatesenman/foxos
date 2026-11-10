// 环境：狐狸OS 自带的隔离环境（Linux 命名空间 / WSL2 / Virtualization.framework）
// 所有操作都走内核命令 foxos env ...，与 CLI / MCP 完全相同，审计记为 human。
'use strict';
(() => {
  const { el, icon } = FX;
  const fmtMB = (v) => (v >= 1024 ? `${(v / 1024).toFixed(1)} GB` : `${(+v || 0).toFixed(1)} MB`);
  const STATE = { running: ['运行中', 'ok'], stopped: ['已停止', 'muted'], starting: ['启动中', 'warn'] };

  async function act(label, args, after) {
    try { const r = await FX.k(args); FX.toast(`${label}：完成`, 'ok'); if (after) after(r); return r; }
    catch (e) { FX.toast(`${label}失败：${e.message}${e.hint ? `（${e.hint}）` : ''}`, 'error'); return null; }
  }

  FX.registerApp('environments', {
    title: () => '环境',
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
        catch (e) { side.replaceChildren(el('div', { class: 'muted small pad', text: `无法读取环境：${e.message}` })); return; }
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
          el('div', { class: 'row pad' }, el('b', { class: 'grow', text: `环境（${envs.length}）` }),
            el('button', { class: 'btn primary sm', 'data-act': 'env-new', onclick: createDialog }, icon('plus'), '新建')),
          el('div', { class: 'muted small pad', text: `后端：${backend}` }),
          ...envs.map((e) => {
            const [label, kind] = STATE[e.state] || [e.state, 'muted'];
            return el('button', { class: `env-item ${e.name === selected ? 'active' : ''}`, 'data-env': e.name, onclick: () => { selected = e.name; tab = 'overview'; renderSide(); renderMain(); } },
              icon(e.state === 'running' ? 'player-play' : 'box'), el('span', { class: 'grow', text: e.name }), el('span', { class: `badge ${kind}`, text: label }));
          }),
          el('div', { class: 'row pad' },
            el('button', { class: 'btn ghost sm', 'data-act': 'env-install', onclick: () => { selected = null; renderInstall(); } }, icon('apps'), '安装系统'),
            el('button', { class: 'btn ghost sm', 'data-act': 'env-images', onclick: () => { selected = null; renderImages(); } }, icon('download'), '镜像'),
            el('button', { class: 'btn ghost sm', 'data-act': 'env-import', onclick: importDialog }, icon('file-import'), '导入')));
      }

      function renderEmpty() {
        main.replaceChildren(el('div', { class: 'empty' }, icon('box-multiple'), el('div', { text: envs.length ? '选择左侧的环境查看详情' : '还没有环境。点“新建”从官方发行版镜像创建一个隔离环境。' })));
      }

      // ---------------------------------------------------------------- 安装系统（一键目录）
      const GUEST = [['linux', 'Linux', 'brand-ubuntu'], ['windows', 'Windows', 'brand-windows'], ['any', '从 ISO / 自定义', 'disc'], ['macos', 'macOS', 'brand-apple']];
      async function renderInstall() {
        clearInterval(timer);
        main.replaceChildren(el('div', { class: 'muted pad', text: '检查本机虚拟化能力…' }));
        let cat; let doc;
        try { [cat, doc] = await Promise.all([FX.k(['env', 'catalog']), FX.k(['env', 'doctor'])]); }
        catch (e) { main.replaceChildren(el('div', { class: 'pad', text: e.message })); return; }
        const banner = el('div', { class: 'env-doctor' });
        Object.entries(doc.results || {}).forEach(([pid, r]) => {
          banner.append(el('div', { class: `env-doc-row ${r.available ? 'ok' : 'warn'}`, 'data-provider': pid },
            icon(r.available ? 'circle-check' : 'alert-triangle'), el('b', { text: pid }), el('span', { class: 'grow muted small', text: r.available ? '可用' : (r.reason || '不可用') }),
            ...(r.actions || []).map((a) => el('button', { class: 'btn sm', 'data-fix': a.id, onclick: async () => {
              if (a.manual) { FX.confirm('需要手动操作', a.label); return; }
              if (!await FX.confirm('修复', `${a.label}？将弹出 Windows 管理员确认。`, { okText: '继续' })) return;
              const res = await act(a.label, ['env', 'fix', '--provider', pid, '--action', a.id]);
              if (res && res.reboot_required) FX.confirm('需要重启', '已完成。请重启电脑，然后回到“环境 → 安装系统”继续安装。');
              renderInstall();
            } }, icon('tool'), a.label.split('（')[0]))));
        });
        const sections = GUEST.map(([g, title, ic]) => {
          const items = cat.entries.filter((e) => e.guest_os === g);
          if (!items.length) return null;
          return el('div', { class: 'env-cat-sec' }, el('h3', {}, icon(ic), ` ${title}`),
            el('div', { class: 'env-cat-grid' }, items.map((e) => el('div', { class: `env-cat ${e.installable ? '' : 'disabled'}`, 'data-entry': e.id },
              el('div', { class: 'row' }, el('b', { class: 'grow', text: e.name }), e.default ? el('span', { class: 'badge ok', text: '推荐' }) : null),
              el('div', { class: 'muted small', text: e.source.origin || '' }),
              el('div', { class: 'muted small mono', text: e.providers.join(' / ') }),
              e.installable ? el('button', { class: 'btn primary sm', 'data-install': e.id, onclick: () => installDialog(e) }, icon('download'), '安装')
                : el('div', { class: 'small warn-text', text: e.reason || '不可用' })))));
        });
        main.replaceChildren(el('h2', { text: '安装系统' }),
          el('div', { class: 'muted small', text: `目录版本 ${cat.version} · 宿主 ${cat.host} · 每个系统都从官方来源下载并校验 sha256` }), banner, ...sections.filter(Boolean));
      }

      function installDialog(e) {
        const base = e.id.replace(/^(wsl|lxc|hyperv)-/, '').replace(/[^a-z0-9-]+/g, '-').slice(0, 30).replace(/-+$/, '');
        const name = el('input', { class: 'input', name: 'env-name', value: base });
        const needs = e.source.needs || [];
        const url = needs.includes('url') ? el('input', { class: 'input mono', name: 'env-url', placeholder: 'https://… 或 D:\\images\\rootfs.tar.gz' }) : null;
        const sha = needs.includes('url') ? el('input', { class: 'input mono', name: 'env-sha', placeholder: 'sha256（可选，建议填写）' }) : null;
        const iso = needs.includes('iso') ? el('input', { class: 'input mono', name: 'env-iso', placeholder: 'ISO 文件完整路径，如 D:\\iso\\Win11_Eval.iso' }) : null;
        const mem = e.providers.includes('hyperv') || e.providers.includes('windows-sandbox') ? el('input', { class: 'input', name: 'env-mem', type: 'number', placeholder: '内存 MB（默认 4096）' }) : null;
        const page = e.source.download_page ? el('a', { href: '#', class: 'small', onclick: (ev) => { ev.preventDefault(); window.foxos.openExternal ? window.foxos.openExternal(e.source.download_page) : FX.toast(e.source.download_page); } }, '打开微软官方下载页') : null;
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
        } }, el('div', { class: 'dialog-title', text: `安装 ${e.name}` }), el('div', { class: 'muted small', text: '环境名（小写字母、数字、连字符）' }), name, url, sha, iso, page, mem,
          el('div', { class: 'dialog-actions' }, el('button', { type: 'button', class: 'btn ghost', onclick: close }, '取消'), el('button', { type: 'submit', class: 'btn primary' }, '开始安装'))));
        document.body.append(overlay); name.focus();
      }

      async function runInstall(e, nm, args) {
        const bar = el('div', { class: 'progress' }, el('div', { class: 'progress-bar', style: 'width:2%' }));
        const status = el('div', { class: 'muted small', 'data-install-status': nm, text: '准备…' });
        main.replaceChildren(el('h2', { text: `正在安装 ${e.name}` }), el('div', { class: 'muted small', text: `环境名 ${nm}` }), bar, status);
        const poll = setInterval(async () => {
          let p; try { p = await FX.k(['env', 'progress', nm]); } catch { return; }
          const frac = p.bytes_total ? p.bytes / p.bytes_total : 0;
          const pct = Math.max(2, Math.round(((p.step || 0) + (p.state === 'done' ? 1 : frac)) / Math.max(1, p.total || p.steps || 1) * 100));
          bar.firstChild.style.width = `${Math.min(100, pct)}%`;
          status.textContent = `${p.why || ''}${p.bytes_total ? `（${fmtMB(p.bytes / 1048576)} / ${fmtMB(p.bytes_total / 1048576)}）` : ''}`;
        }, 1000);
        try {
          await FX.k(args, { timeoutMs: 4 * 3600 * 1000 });
          FX.toast(`${e.name} 安装完成`, 'ok'); selected = nm; await refresh();
        } catch (err) {
          status.textContent = `安装失败：${err.message}${err.hint ? `（${err.hint}）` : ''}`;
          main.append(el('button', { class: 'btn sm', onclick: renderInstall }, icon('arrow-left'), '返回目录'));
        } finally { clearInterval(poll); }
      }

      async function renderImages() {
        main.replaceChildren(el('div', { class: 'muted pad', text: '读取镜像…' }));
        let r; try { r = await FX.k(['env', 'images']); } catch (e) { main.replaceChildren(el('div', { class: 'pad', text: e.message })); return; }
        const url = el('input', { class: 'input mono grow', placeholder: 'https://… rootfs.tar.gz / .tar.zst / .foxenv' });
        const sha = el('input', { class: 'input mono', placeholder: 'sha256（可选）', style: 'width:220px' });
        const pull = (img, extra = []) => act(`下载 ${img}`, ['env', 'pull', img, ...extra], renderImages);
        main.replaceChildren(
          el('h3', { text: '官方镜像目录' }),
          el('table', { class: 'table' }, el('tbody', {}, r.catalog.map((c) => {
            const have = r.local.find((l) => l.id === c.id);
            return el('tr', {}, el('td', { text: c.name }), el('td', { class: 'mono small', text: c.id }), el('td', { text: `${c.size_mb} MB` }),
              el('td', {}, have ? el('span', { class: 'badge ok', text: '已下载' }) : el('button', { class: 'btn sm', 'data-pull': c.id, onclick: () => pull(c.id) }, icon('download'), '下载')));
          }))),
          el('h3', { text: '从地址安装' }),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (url.value.trim()) pull(url.value.trim(), sha.value.trim() ? ['--sha256', sha.value.trim()] : []); } }, url, sha, el('button', { class: 'btn primary sm', type: 'submit' }, '下载')),
          el('h3', { text: '本地镜像' }),
          el('table', { class: 'table' }, el('tbody', {}, r.local.map((l) => el('tr', {}, el('td', { text: l.name }), el('td', { class: 'mono small', text: l.id }),
            el('td', { class: 'mono small', text: (l.sha256 || '').slice(0, 16) }), el('td', {}, l.verified ? el('span', { class: 'badge ok', text: 'sha256 已校验' }) : el('span', { class: 'badge warn', text: '未校验' })))))));
      }

      async function renderMain() {
        clearInterval(timer);
        const e = envs.find((x) => x.name === selected); if (!e) return renderEmpty();
        const running = e.state === 'running';
        const n = e.name;
        const quick = el('div', { class: 'row wrap' },
          running ? el('button', { class: 'btn sm', 'data-act': 'stop', onclick: () => act('停止', ['env', 'stop', n], refresh) }, icon('player-stop'), '停止')
            : el('button', { class: 'btn primary sm', 'data-act': 'start', onclick: () => act('启动', ['env', 'start', n], refresh) }, icon('player-play'), '启动'),
          el('button', { class: 'btn sm', 'data-act': 'restart', onclick: () => act('重启', ['env', 'restart', n], refresh) }, icon('refresh'), '重启'),
          el('button', { class: 'btn sm', 'data-act': 'terminal', onclick: () => openShell(n) }, icon('terminal-2'), '终端'),
          el('button', { class: 'btn sm', 'data-act': 'files', onclick: () => FX.openWindow('files', { path: '' }) }, icon('folder'), '工作空间文件'),
          el('button', { class: 'btn sm', 'data-act': 'editor', onclick: () => FX.openWindow('editor', {}) }, icon('code'), '编辑器'),
          el('button', { class: 'btn sm', 'data-act': 'clone', onclick: async () => { const nn = await FX.prompt('克隆为', { value: `${n}-copy` }); if (nn) act('克隆', ['env', 'clone', n, nn], refresh); } }, icon('copy'), '克隆'),
          el('button', { class: 'btn sm', 'data-act': 'export', onclick: async () => { const out = await FX.prompt('导出到（工作空间内路径）', { value: `backups/${n}.foxenv` }); if (out) act('导出', ['env', 'export', n, '--out', out]); } }, icon('file-export'), '导出'),
          el('button', { class: 'btn ghost sm danger', 'data-act': 'delete', onclick: async () => { if (await FX.confirm('删除环境', `删除 ${n}？可写层与快照会一起删除，镜像与工作空间不受影响。`, { okText: '删除' })) act('删除', ['env', 'delete', n], refresh); } }, icon('trash'), '删除'));
        const tabs = el('div', { class: 'env-tabs' }, [['overview', '概览'], ['snapshots', '快照'], ['actions', '自定义操作'], ['settings', '设置'], ['logs', '日志']].map(([id, t]) =>
          el('button', { class: `env-tab ${tab === id ? 'active' : ''}`, 'data-tab': id, onclick: () => { tab = id; renderMain(); } }, t)));
        const pane = el('div', { class: 'env-pane' });
        const [label, kind] = STATE[e.state] || [e.state, 'muted'];
        main.replaceChildren(el('div', { class: 'row' }, el('h2', { class: 'grow', text: n }), el('span', { class: `badge ${kind}`, text: label })),
          el('div', { class: 'muted small', text: `镜像 ${e.image} · 网络 ${e.network} · 工作空间 ${e.workspace.mode}（/workspace） · 后端 ${e.backend}` }), quick, tabs, pane);
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
        pane.append(el('div', { class: 'stats' }, card('processes', '进程'), card('cpu', 'CPU'), card('memory', '内存'), card('disk', '可写层磁盘')),
          el('div', { class: 'muted small', text: `限制：${Object.entries(info.limits).map(([k, v]) => `${k}=${v}`).join('，') || '无'} · 挂载：${info.mounts.length} 个 · 目录 ${info.path}` }));
        let last = null;
        const tick = async () => {
          let s; try { s = (await FX.k(['env', 'stats', n])).stats[n]; } catch { return; }
          const now = performance.now();
          const cpu = last ? Math.max(0, (s.cpu_seconds - last.cpu) / ((now - last.t) / 1000)) * 100 : 0;
          last = { cpu: s.cpu_seconds, t: now };
          cells.processes.textContent = String(s.processes);
          cells.cpu.textContent = `${cpu.toFixed(0)}%（累计 ${s.cpu_seconds.toFixed(1)} s）`;
          cells.memory.textContent = fmtMB(s.memory_mb);
          cells.disk.textContent = fmtMB(s.disk_mb);
        };
        tick(); timer = setInterval(() => { if (!document.body.contains(pane)) return clearInterval(timer); tick(); }, 2000);
      }

      function snapshots(pane, n, info) {
        pane.append(el('div', { class: 'row' }, el('div', { class: 'muted small grow', text: '快照、恢复、克隆与导出需要先停止环境。' }),
          el('button', { class: 'btn primary sm', 'data-act': 'snapshot', onclick: async () => { const l = await FX.prompt('快照说明', { value: '' }); if (l !== null) act('快照', ['env', 'snapshot', n, ...(l ? ['--label', l] : [])], renderMain); } }, icon('camera'), '创建快照')),
          el('table', { class: 'table' }, el('tbody', {}, info.snapshots_detail.length ? info.snapshots_detail.map((s) => el('tr', {}, el('td', { class: 'mono', text: s.id }), el('td', { text: s.label || '' }), el('td', { text: fmtMB(s.size / 1048576) }), el('td', { text: s.by }),
            el('td', {}, el('button', { class: 'btn sm', 'data-restore': s.id, onclick: async () => { if (await FX.confirm('恢复快照', `把 ${n} 恢复到 ${s.id}？当前可写层会被替换。`, { okText: '恢复' })) act('恢复', ['env', 'restore', n, s.id], renderMain); } }, '恢复'))))
              : [el('tr', {}, el('td', { class: 'muted', text: '还没有快照' }))])));
      }

      function actions(pane, n, info) {
        const name = el('input', { class: 'input', placeholder: '操作名，如 test' });
        const cmd = el('input', { class: 'input mono grow', placeholder: '例如 cd /workspace && make test  （可用 ${env} ${image} ${workspace} ${host_workspace} ${hostname}）' });
        const out = el('pre', { class: 'mono small out' });
        pane.append(
          el('table', { class: 'table' }, el('tbody', {}, info.actions_detail.length ? info.actions_detail.map((a) => el('tr', {}, el('td', { text: a.name }), el('td', { class: 'mono small', text: a.command }),
            el('td', {}, el('button', { class: 'btn sm', 'data-run': a.name, onclick: async () => { out.textContent = '运行中…'; const r = await act(`运行 ${a.name}`, ['env', 'action', 'run', n, a.name]); if (r) out.textContent = `$ ${(r.command || []).join(' ')}\n${r.stdout || ''}${r.stderr || ''}\n退出码 ${r.exit_code}`; } }, icon('player-play'), '运行'))))
              : [el('tr', {}, el('td', { class: 'muted', text: '还没有自定义操作' }))])),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (name.value.trim() && cmd.value.trim()) act('添加操作', ['env', 'action', 'add', n, name.value.trim(), '--command', cmd.value], renderMain); } }, name, cmd, el('button', { class: 'btn primary sm', type: 'submit' }, '添加')), out);
      }

      function settings(pane, n, info) {
        const L = info.limits || {};
        const mem = el('input', { class: 'input', type: 'number', min: 0, value: L.memory_mb || '', placeholder: '不限' });
        const pids = el('input', { class: 'input', type: 'number', min: 0, value: L.pids || '', placeholder: '不限' });
        const cpus = el('input', { class: 'input', type: 'number', min: 0, step: 0.5, value: L.cpus || '', placeholder: '不限' });
        const net = el('select', { class: 'input' }, ['host', 'none'].map((v) => el('option', { value: v, selected: info.network === v, text: v === 'host' ? 'host（共享宿主网络）' : 'none（只有回环）' })));
        const wm = el('select', { class: 'input' }, ['rw', 'ro', 'none'].map((v) => el('option', { value: v, selected: info.workspace.mode === v, text: { rw: '读写', ro: '只读', none: '不挂载' }[v] })));
        const src = el('input', { class: 'input mono grow', placeholder: '宿主路径' });
        const tgt = el('input', { class: 'input mono', placeholder: '环境内路径，如 /data' });
        const ro = el('input', { type: 'checkbox' });
        pane.append(
          el('form', { class: 'form-grid', onsubmit: (e) => { e.preventDefault(); act('保存设置', ['env', 'limits', n, '--memory-mb', String(+mem.value || 0), '--pids', String(+pids.value || 0), '--cpus', String(+cpus.value || 0), '--network', net.value, '--workspace-mode', wm.value], renderMain); } },
            el('label', { text: '内存上限（MB）' }), mem, el('label', { text: '进程数上限' }), pids, el('label', { text: 'CPU 上限（核）' }), cpus,
            el('label', { text: '网络' }), net, el('label', { text: '工作空间' }), wm,
            el('div', {}), el('button', { class: 'btn primary sm', type: 'submit', 'data-act': 'save-limits' }, '保存（下次启动生效）')),
          el('div', { class: 'muted small', text: info.limits_note || '' }),
          el('h3', { text: '挂载' }),
          el('table', { class: 'table' }, el('tbody', {}, info.mounts.length ? info.mounts.map((m) => el('tr', {}, el('td', { class: 'mono', text: m.source }), el('td', { class: 'mono', text: m.target }), el('td', { text: m.readonly ? '只读' : '读写' }),
            el('td', {}, el('button', { class: 'btn ghost sm', onclick: () => act('移除挂载', ['env', 'mount', n, '--source', m.source, '--target', m.target, '--remove'], renderMain) }, '移除'))))
              : [el('tr', {}, el('td', { class: 'muted', text: '没有额外挂载' }))])),
          el('form', { class: 'row', onsubmit: (e) => { e.preventDefault(); if (src.value && tgt.value) act('添加挂载', ['env', 'mount', n, '--source', src.value, '--target', tgt.value, ...(ro.checked ? ['--readonly'] : [])], renderMain); } },
            src, tgt, el('label', { class: 'row' }, ro, '只读'), el('button', { class: 'btn primary sm', type: 'submit' }, '挂载')));
      }

      async function logs(pane, n) {
        const pre = el('pre', { class: 'mono small out', 'data-logs': n });
        pane.append(pre);
        try { const r = await FX.k(['env', 'logs', n, '-n', '200']); pre.textContent = Object.entries(r.logs || {}).map(([f, ls]) => `== ${f} ==\n${ls.join('\n')}`).join('\n\n') || '（无日志）'; } catch (e) { pre.textContent = e.message; }
      }

      function openShell(n) {
        // 终端里的 PATH 已包含 foxos 命令（与内置终端相同）
        const isWin = FX.env.platform === 'win32';
        FX.openWindow('terminal', { title: `环境 ${n}`, command: isWin ? 'powershell.exe' : (FX.env.shell || '/bin/sh'), args: isWin ? ['-NoProfile', '-Command', `foxos env shell ${n}`] : ['-c', `foxos env shell '${n}'`] });
      }

      async function createDialog() {
        let imgs = { catalog: [], local: [] }; try { imgs = await FX.k(['env', 'images']); } catch { /* 下面会显示错误 */ }
        const ids = [...new Set([...imgs.local.map((l) => l.id), ...imgs.catalog.map((c) => c.id)])];
        const name = el('input', { class: 'input', placeholder: '名称，如 dev', name: 'env-name' });
        const image = el('select', { class: 'input', name: 'env-image' }, ids.map((i) => el('option', { value: i, text: `${i}${imgs.local.find((l) => l.id === i) ? '' : '（需下载）'}` })));
        const net = el('select', { class: 'input' }, el('option', { value: 'host', text: '共享宿主网络' }), el('option', { value: 'none', text: '无网络' }));
        const wm = el('select', { class: 'input' }, el('option', { value: 'rw', text: '工作空间读写' }), el('option', { value: 'ro', text: '工作空间只读' }), el('option', { value: 'none', text: '不挂载工作空间' }));
        const overlay = el('div', { class: 'overlay' });
        const close = () => overlay.remove();
        overlay.append(el('form', { class: 'dialog', onsubmit: async (e) => {
          e.preventDefault(); const nm = name.value.trim(); if (!nm) return;
          close();
          if (!imgs.local.find((l) => l.id === image.value)) { FX.toast(`下载镜像 ${image.value}…`); if (!await act('下载镜像', ['env', 'pull', image.value])) return; }
          await act('创建', ['env', 'create', nm, '--image', image.value, '--network', net.value, '--workspace-mode', wm.value], () => { selected = nm; });
          refresh();
        } }, el('div', { class: 'dialog-title', text: '新建环境' }), name, image, net, wm,
          el('div', { class: 'dialog-actions' }, el('button', { type: 'button', class: 'btn ghost', onclick: close }, '取消'), el('button', { type: 'submit', class: 'btn primary' }, '创建'))));
        document.body.append(overlay); name.focus();
      }

      async function importDialog() {
        const f = await FX.prompt('.foxenv 文件（工作空间内路径）', { value: 'backups/' }); if (!f) return;
        const nm = await FX.prompt('新环境名', { value: '' }); if (!nm) return;
        act('导入', ['env', 'import', f, '--name', nm], () => { selected = nm; refresh(); });
      }

      // 审计日志有新记录（CLI / MCP / 智能体的操作）时刷新，合并 600ms 内的多次变化
      let pend = null;
      FX.on('audit', () => { if (!document.body.contains(root) || pend) return; pend = setTimeout(() => { pend = null; refresh(true); }, 600); });
      refresh();
      return { refresh, dispose: () => clearInterval(timer) };
    },
  });
})();
