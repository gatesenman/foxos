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
            colors: { 'editor.background': '#10131a', 'editorLineNumber.foreground': '#4a5163', 'editor.lineHighlightBackground': '#171b24', 'scrollbar.shadow': '#00000000', 'scrollbarSlider.background': '#80869650', 'scrollbarSlider.hoverBackground': '#969cacA0', 'scrollbarSlider.activeBackground': '#ff8a3dB0', 'editorOverviewRuler.border': '#00000000' },
          });
          resolve(window.monaco);
        }, reject);
      };
      s.onerror = () => reject(new Error(FX.t('editor.cannot_load_monaco')));
      document.head.append(s);
    });
    return monacoReady;
  }

  const LANG = { js: 'javascript', mjs: 'javascript', cjs: 'javascript', jsx: 'javascript', ts: 'typescript', tsx: 'typescript', py: 'python', sh: 'shell', bash: 'shell', zsh: 'shell', ps1: 'powershell', json: 'json', jsonl: 'json', md: 'markdown', html: 'html', htm: 'html', css: 'css', scss: 'scss', xml: 'xml', yaml: 'yaml', yml: 'yaml', toml: 'ini', ini: 'ini', sql: 'sql', rs: 'rust', go: 'go', java: 'java', c: 'c', h: 'c', cpp: 'cpp', hpp: 'cpp', cs: 'csharp', rb: 'ruby', php: 'php', lua: 'lua', r: 'r', csv: 'plaintext', txt: 'plaintext' };

  FX.registerApp('editor', {
    title: (p) => (p.path ? FX.t('editor.editor_2', FX.basename(p.path)) : FX.t('common.editor')),
    icon: 'code',
    geometry: { w: 860, h: 560 },
    key: (p) => (p.path ? `editor:${p.path}` : null),
    mount(body, params, win) {
      let path = params.path || null;
      let mtime = null;
      let dirty = false;
      win.isDirty = () => dirty;
      let editor = null;
      let savedVersion = null;
      const pathLabel = el('span', { class: 'muted mono', text: path || FX.t('editor.unsaved_new_file') });
      const dirtyDot = el('span', { class: 'dirty-dot hidden', title: FX.t('editor.unsaved_changes') });
      const banner = el('div', { class: 'banner hidden' });
      const host = el('div', { class: 'editor-host' });
      const status = el('div', { class: 'statusbar' });
      body.append(
        el('div', { class: 'toolbar' }, icon('file-code'), pathLabel, dirtyDot, el('div', { class: 'spacer' }),
          el('button', { class: 'btn ghost sm', 'data-action': 'reload', onclick: () => load(true) }, icon('refresh'), FX.t('editor.reload')),
          el('button', { class: 'btn primary sm', 'data-action': 'save', onclick: () => save() }, icon('device-floppy'), FX.t('common.save'))),
        banner, host, status);

      const setDirty = (d) => { dirty = d; dirtyDot.classList.toggle('hidden', !d); win.setTitle(FX.t('editor.editor', d ? '* ' : '', path ? FX.basename(path) : FX.t('editor.new_file'))); };

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
          status.textContent = FX.t('editor.bytes_utf_8', r.bytes, LANG[FX.ext(path)] || 'plaintext');
        } catch (e) {
          if (e.code === 'NOT_FOUND') showBanner(FX.t('editor.the_file_no_longer_exists_it_may'), [[FX.t('editor.got_it'), () => {}]]);
          else FX.toast(e.message, 'error');
        }
      }

      async function save(force = false) {
        if (!editor) return;
        if (!path) {
          const p = await FX.prompt(FX.t('editor.save_as'), { placeholder: FX.t('editor.path_relative_to_the_workspace_e_g') });
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
          FX.toast(FX.t('editor.saved', path), 'ok');
          FX.saveSession();
        } catch (e) {
          if (e.code === 'CONFLICT') showBanner(FX.t('editor.someone_else_an_agent_or_the'), [[FX.t('editor.load_the_version_on_disk'), () => load(true)], [FX.t('editor.overwrite'), () => save(true), 'danger']]);
          else FX.toast(`${e.message}${e.hint ? FX.t('editor.hint_paren', e.hint) : ''}`, 'error');
        }
      }

      loadMonaco().then((m) => {
        editor = m.editor.create(host, { value: '', language: 'plaintext', theme: 'foxos', automaticLayout: true, fontSize: 13, minimap: { enabled: false }, scrollBeyondLastLine: false, wordWrap: 'on', overviewRulerLanes: 0, hideCursorInOverviewRuler: true, scrollbar: { useShadows: false, verticalScrollbarSize: 10, horizontalScrollbarSize: 10, verticalSliderSize: 6, horizontalSliderSize: 6, vertical: 'auto', horizontal: 'auto' } });
        editor.onDidChangeModelContent(() => setDirty(editor.getModel().getAlternativeVersionId() !== savedVersion));
        editor.addCommand(m.KeyMod.CtrlCmd | m.KeyCode.KeyS, () => save());
        win.editor = editor;
        if (path) load(true); else { savedVersion = editor.getModel().getAlternativeVersionId(); status.textContent = FX.t('editor.new_file'); }
      }).catch((e) => { host.append(el('div', { class: 'empty error', text: e.message })); });

      // 外部修改：干净时自动载入；有未保存修改时提示
      FX.on('fs', (ev) => {
        if (win.disposed || !path || !ev.paths.includes(path)) return;
        FX.k(['files', 'read', path]).then((r) => {
          if (r.modified === mtime) return;
          if (!dirty) load(true);
          else showBanner(FX.t('editor.the_file_changed_on_disk_and_you'), [[FX.t('editor.load_the_version_on_disk'), () => load(true)], [FX.t('editor.keep_my_changes'), () => {}]]);
        }).catch(() => {});
      });

      return {
        persistParams: () => (path ? { path } : null),
        save, load, value: () => editor && editor.getValue(), isDirty: () => dirty,
        beforeClose: async () => !dirty || FX.confirm(FX.t('editor.close_editor'), FX.t('editor.has_unsaved_changes_discard_them', path || FX.t('editor.new_file')), { okText: FX.t('editor.discard_changes'), danger: true }),
        dispose: () => { win.disposed = true; editor && editor.dispose(); },
      };
    },
  });
})();
