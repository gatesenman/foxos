// 文件管理器：真实的工作空间文件系统；新建、重命名、删除都经过 foxos 内核（权限、写锁、审计）
'use strict';
(() => {
  const { el, icon } = FX;

  FX.openPath = async (rel, type = 'file', forceApp = null) => {
    const kind = FX.fileKind(rel, type);
    const app = forceApp || kind.opener;
    if (app === 'files') return FX.openWindow('files', { path: rel });
    if (app === 'editor') return FX.openWindow('editor', { path: rel });
    if (app === 'browser') return FX.openWindow('browser', { url: FX.fileUrl(rel) });
    if (['writer', 'calc', 'impress'].includes(app)) return FX.launchOffice(app, rel);
    return null;
  };
  FX.fileUrl = (rel) => `file://${FX.env.workspace.replace(/\\/g, '/').replace(/^([A-Za-z]):/, '/$1:')}/${rel.split('/').map(encodeURIComponent).join('/')}`;

  FX.registerApp('files', {
    title: (p) => `文件 — ${p.path ? p.path : '工作空间'}`,
    icon: 'folder',
    geometry: { w: 760, h: 480 },
    mount(body, params, win) {
      let cwd = params.path || '';
      let selected = null;
      let entries = [];
      const history = [];
      const crumbs = el('div', { class: 'crumbs' });
      const list = el('div', { class: 'file-list', tabindex: '0' });
      const status = el('div', { class: 'statusbar' });
      const tb = (ic, title, fn, extra = '') => el('button', { class: `icon-btn ${extra}`, title, onclick: fn }, icon(ic));
      const toolbar = el('div', { class: 'toolbar' },
        tb('arrow-left', '后退', () => { if (history.length) go(history.pop(), false); }),
        tb('arrow-up', '上一级', () => { if (cwd) go(FX.dirname(cwd)); }),
        tb('refresh', '刷新', () => load()),
        crumbs,
        el('div', { class: 'spacer' }),
        el('button', { class: 'btn ghost sm', 'data-action': 'new-folder', onclick: newFolder }, icon('folder-plus'), '新建文件夹'),
        el('button', { class: 'btn ghost sm', 'data-action': 'new-file', onclick: newFile }, icon('file-plus'), '新建文件'),
        tb('pencil', '重命名（F2）', () => rename(), 'need-sel'),
        tb('trash', '删除（Delete）', () => del(), 'need-sel danger'));
      body.append(toolbar, list, status);

      function rel(name) { return cwd ? `${cwd}/${name}` : name; }

      function renderCrumbs() {
        crumbs.replaceChildren(el('button', { class: 'crumb', onclick: () => go('') }, icon('home'), '工作空间'));
        let acc = '';
        for (const part of cwd.split('/').filter(Boolean)) {
          acc = acc ? `${acc}/${part}` : part;
          const target = acc;
          crumbs.append(el('span', { class: 'sep', text: '/' }), el('button', { class: 'crumb', onclick: () => go(target) }, part));
        }
      }

      function render() {
        list.replaceChildren(el('div', { class: 'file-row head' }, el('span', { text: '名称' }), el('span', { text: '类型' }), el('span', { text: '大小' }), el('span', { text: '修改时间' })));
        if (!entries.length) list.append(el('div', { class: 'empty' }, icon('folder-open'), el('div', { text: '空文件夹' })));
        for (const e of entries) {
          const kind = FX.fileKind(e.name, e.type);
          const row = el('div', {
            class: `file-row ${selected === e.path ? 'sel' : ''}`, 'data-path': e.path, 'data-type': e.type, tabindex: '-1',
            onclick: () => { selected = e.path; render(); },
            ondblclick: () => open(e),
            oncontextmenu: (ev) => { ev.preventDefault(); selected = e.path; render(); menu(ev, e); },
          }, el('span', { class: 'fname' }, icon(kind.icon, `ft-${kind.opener}`), el('span', { text: e.name })),
          el('span', { class: 'muted', text: kind.label }), el('span', { class: 'muted', text: e.type === 'dir' ? '' : FX.fmtBytes(e.bytes) }),
          el('span', { class: 'muted', text: FX.fmtTime(e.modified) }));
          list.append(row);
        }
        status.textContent = `${entries.length} 项${selected ? ` · 已选择 ${FX.basename(selected)}` : ''}`;
        body.classList.toggle('has-sel', Boolean(selected));
      }

      async function load() {
        try {
          const r = await FX.k(['files', 'list', ...(cwd ? [cwd] : [])]);
          entries = r.entries;
          if (selected && !entries.some((e) => e.path === selected)) selected = null;
          renderCrumbs(); render();
          win.setTitle(`文件 — ${cwd || '工作空间'}`);
        } catch (e) {
          FX.toast(e.message, 'error');
          if (e.code === 'NOT_FOUND' && cwd) go(FX.dirname(cwd), false);
        }
      }

      function go(p, push = true) { if (push) history.push(cwd); cwd = p; selected = null; load(); FX.saveSession(); }
      function open(e) { if (e.type === 'dir') go(e.path); else FX.openPath(e.path, e.type); }

      async function newFolder() {
        const name = await FX.prompt('新建文件夹', { placeholder: '文件夹名称' });
        if (!name) return;
        try { await FX.k(['files', 'mkdir', rel(name)]); selected = rel(name); await load(); } catch (e) { FX.toast(e.message, 'error'); }
      }
      async function newFile() {
        const name = await FX.prompt('新建文件', { placeholder: '例如 notes.md、report.docx、data.xlsx、deck.pptx' });
        if (!name) return;
        const p = rel(name);
        const e = FX.ext(name);
        try {
          if (e === 'xlsx') await FX.k(['sheets', 'create', p]);
          else if (e === 'docx') await FX.k(['docs', 'create', p]);
          else if (e === 'pptx') await FX.k(['slides', 'create', p]);
          else await FX.k(['files', 'write', p, '--content', '']);
          selected = p; await load();
        } catch (err) { FX.toast(err.message, 'error'); }
      }
      async function rename(target = selected) {
        if (!target) return;
        const name = await FX.prompt('重命名', { value: FX.basename(target) });
        if (!name || name === FX.basename(target)) return;
        const dest = FX.dirname(target) ? `${FX.dirname(target)}/${name}` : name;
        try { await FX.k(['files', 'rename', target, dest]); selected = dest; await load(); } catch (e) { FX.toast(e.message, 'error'); }
      }
      async function del(target = selected) {
        if (!target) return;
        if (!(await FX.confirm('删除', `把「${FX.basename(target)}」移到回收站？可以在活动面板或用 foxos files restore 恢复。`, { okText: '删除', danger: true }))) return;
        try { const r = await FX.k(['files', 'delete', target]); FX.toast(`已移到回收站：${r.path}`, 'ok'); selected = null; await load(); } catch (e) { FX.toast(e.message, 'error'); }
      }

      function menu(ev, e) {
        const kind = FX.fileKind(e.name, e.type);
        const items = [['folder-open', '打开', () => open(e)]];
        if (kind.alt) items.push(['external-link', kind.alt === 'browser' ? '用浏览器打开' : '用 LibreOffice Calc 打开', () => FX.openPath(e.path, e.type, kind.alt)]);
        if (e.type === 'file' && kind.opener !== 'editor' && ['csv', 'md', 'txt', 'html'].includes(FX.ext(e.name))) items.push(['code', '用编辑器打开', () => FX.openPath(e.path, e.type, 'editor')]);
        items.push(['pencil', '重命名', () => rename(e.path)], ['trash', '删除', () => del(e.path)]);
        FX.contextMenu(ev.clientX, ev.clientY, items);
      }

      list.addEventListener('keydown', (ev) => {
        if (ev.key === 'F2') rename();
        if (ev.key === 'Delete') del();
        if (ev.key === 'Enter' && selected) { const e = entries.find((x) => x.path === selected); if (e) open(e); }
      });

      // 智能体或终端对文件的修改：实时刷新
      const onFs = (ev) => { if (win.disposed) return; if (ev.paths.some((p) => FX.dirname(p) === cwd || p === cwd || p.startsWith(cwd ? `${cwd}/` : ''))) load(); };
      FX.on('fs', onFs);
      load();
      return { persistParams: () => ({ path: cwd }), reload: load, cwd: () => cwd, dispose: () => { win.disposed = true; } };
    },
  });

  FX.contextMenu = (x, y, items) => {
    document.querySelectorAll('.ctx-menu').forEach((m) => m.remove());
    const m = FX.el('div', { class: 'ctx-menu', style: { left: `${x}px`, top: `${y}px` } },
      items.map(([ic, label, fn]) => FX.el('button', { onclick: () => { m.remove(); fn(); } }, FX.icon(ic), label)));
    document.body.append(m);
    setTimeout(() => addEventListener('pointerdown', function off(e) { if (!m.contains(e.target)) { m.remove(); removeEventListener('pointerdown', off); } }), 0);
  };
})();
