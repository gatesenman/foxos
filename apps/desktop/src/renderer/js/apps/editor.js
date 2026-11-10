// 代码编辑器：Monaco（与 VS Code 同一编辑器内核），通过 foxos 内核真实读写；外部修改实时提示
'use strict';
(() => {
  const { el, icon } = FX;
  const VS = '../../node_modules/monaco-editor/min/vs';
  let monacoReady = null;

  function loadMonaco() {
    if (monacoReady) return monacoReady;
    monacoReady = new Promise((resolve, reject) => {
      window.MonacoEnvironment = {
        getWorkerUrl: () => new URL(`${VS}/base/worker/workerMain.js`, location.href).href,
      };
      const s = document.createElement('script');
      s.src = `${VS}/loader.js`;
      s.onload = () => {
        window.require.config({ paths: { vs: VS } });
        window.require(['vs/editor/editor.main'], () => {
          window.monaco.editor.defineTheme('foxos', {
            base: 'vs-dark', inherit: true, rules: [],
            colors: { 'editor.background': '#10131a', 'editorLineNumber.foreground': '#4a5163', 'editor.lineHighlightBackground': '#171b24' },
          });
          resolve(window.monaco);
        }, reject);
      };
      s.onerror = () => reject(new Error('无法加载 Monaco'));
      document.head.append(s);
    });
    return monacoReady;
  }

  const LANG = { js: 'javascript', mjs: 'javascript', cjs: 'javascript', jsx: 'javascript', ts: 'typescript', tsx: 'typescript', py: 'python', sh: 'shell', bash: 'shell', zsh: 'shell', ps1: 'powershell', json: 'json', jsonl: 'json', md: 'markdown', html: 'html', htm: 'html', css: 'css', scss: 'scss', xml: 'xml', yaml: 'yaml', yml: 'yaml', toml: 'ini', ini: 'ini', sql: 'sql', rs: 'rust', go: 'go', java: 'java', c: 'c', h: 'c', cpp: 'cpp', hpp: 'cpp', cs: 'csharp', rb: 'ruby', php: 'php', lua: 'lua', r: 'r', csv: 'plaintext', txt: 'plaintext' };

  FX.registerApp('editor', {
    title: (p) => (p.path ? `编辑器 — ${FX.basename(p.path)}` : '编辑器'),
    icon: 'code',
    geometry: { w: 860, h: 560 },
    key: (p) => (p.path ? `editor:${p.path}` : null),
    mount(body, params, win) {
      let path = params.path || null;
      let mtime = null;
      let dirty = false;
      let editor = null;
      let savedVersion = null;
      const pathLabel = el('span', { class: 'muted mono', text: path || '未保存的新文件' });
      const dirtyDot = el('span', { class: 'dirty-dot hidden', title: '有未保存的修改' });
      const banner = el('div', { class: 'banner hidden' });
      const host = el('div', { class: 'editor-host' });
      const status = el('div', { class: 'statusbar' });
      body.append(
        el('div', { class: 'toolbar' }, icon('file-code'), pathLabel, dirtyDot, el('div', { class: 'spacer' }),
          el('button', { class: 'btn ghost sm', 'data-action': 'reload', onclick: () => load(true) }, icon('refresh'), '重新载入'),
          el('button', { class: 'btn primary sm', 'data-action': 'save', onclick: () => save() }, icon('device-floppy'), '保存')),
        banner, host, status);

      const setDirty = (d) => { dirty = d; dirtyDot.classList.toggle('hidden', !d); win.setTitle(`${d ? '* ' : ''}编辑器 — ${path ? FX.basename(path) : '新文件'}`); };

      function showBanner(text, actions) {
        banner.replaceChildren(icon('alert-triangle'), el('span', { text }), el('div', { class: 'spacer' }),
          ...actions.map(([label, fn, cls]) => el('button', { class: `btn sm ${cls || 'ghost'}`, onclick: () => { banner.classList.add('hidden'); fn(); } }, label)));
        banner.classList.remove('hidden');
      }

      async function load(force = false) {
        if (!path) return;
        if (dirty && !force) return;
        try {
          const r = await FX.k(['files', 'read', path]);
          mtime = r.modified;
          const m = await loadMonaco();
          const model = editor.getModel();
          m.editor.setModelLanguage(model, LANG[FX.ext(path)] || 'plaintext');
          if (model.getValue() !== r.content) editor.setValue(r.content);
          savedVersion = model.getAlternativeVersionId();
          setDirty(false);
          banner.classList.add('hidden');
          status.textContent = `${r.bytes} 字节 · ${LANG[FX.ext(path)] || 'plaintext'} · UTF-8`;
        } catch (e) {
          if (e.code === 'NOT_FOUND') showBanner('文件已不存在（可能被删除或重命名）。保存会重新创建。', [['知道了', () => {}]]);
          else FX.toast(e.message, 'error');
        }
      }

      async function save(force = false) {
        if (!editor) return;
        if (!path) {
          const p = await FX.prompt('保存为', { placeholder: '工作空间内的相对路径，例如 notes/todo.md' });
          if (!p) return;
          path = p; pathLabel.textContent = p; win.key = `editor:${p}`; win.params = { path: p };
        }
        const args = ['files', 'write', path, '--content-stdin'];
        if (mtime != null && !force) args.push('--expect-mtime', String(mtime));
        try {
          const r = await FX.k(args, { stdin: editor.getValue() });
          mtime = r.modified;
          savedVersion = editor.getModel().getAlternativeVersionId();
          setDirty(false);
          FX.toast(`已保存 ${path}`, 'ok');
          FX.saveSession();
        } catch (e) {
          if (e.code === 'CONFLICT') showBanner('文件在你编辑期间被其他人（智能体或终端）修改过。', [['载入磁盘版本', () => load(true)], ['覆盖保存', () => save(true), 'danger']]);
          else FX.toast(`${e.message}${e.hint ? `（${e.hint}）` : ''}`, 'error');
        }
      }

      loadMonaco().then((m) => {
        editor = m.editor.create(host, { value: '', language: 'plaintext', theme: 'foxos', automaticLayout: true, fontSize: 13, minimap: { enabled: false }, scrollBeyondLastLine: false, wordWrap: 'on' });
        editor.onDidChangeModelContent(() => setDirty(editor.getModel().getAlternativeVersionId() !== savedVersion));
        editor.addCommand(m.KeyMod.CtrlCmd | m.KeyCode.KeyS, () => save());
        win.editor = editor;
        if (path) load(true); else { savedVersion = editor.getModel().getAlternativeVersionId(); status.textContent = '新文件'; }
      }).catch((e) => { host.append(el('div', { class: 'empty error', text: e.message })); });

      // 外部修改：干净时自动载入；有未保存修改时提示
      FX.on('fs', (ev) => {
        if (win.disposed || !path || !ev.paths.includes(path)) return;
        FX.k(['files', 'read', path]).then((r) => {
          if (r.modified === mtime) return;
          if (!dirty) load(true);
          else showBanner('磁盘上的文件已被修改，而你有未保存的修改。', [['载入磁盘版本', () => load(true)], ['保留我的修改', () => {}]]);
        }).catch(() => {});
      });

      return {
        persistParams: () => (path ? { path } : null),
        save, load, value: () => editor && editor.getValue(), isDirty: () => dirty,
        beforeClose: async () => !dirty || FX.confirm('关闭编辑器', `「${path || '新文件'}」有未保存的修改，确定放弃？`, { okText: '放弃修改', danger: true }),
        dispose: () => { win.disposed = true; editor && editor.dispose(); },
      };
    },
  });
})();
