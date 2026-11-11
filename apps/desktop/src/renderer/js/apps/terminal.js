// 终端：xterm.js + node-pty，连接宿主系统真实的 shell
'use strict';
(() => {
  const ptyHandlers = new Map();
  window.foxos.pty.onData((id, data) => ptyHandlers.get(id)?.data(data));
  window.foxos.pty.onExit((id, code) => ptyHandlers.get(id)?.exit(code));

  FX.registerApp('terminal', {
    title: (p) => p.title || FX.t('common.terminal'),
    icon: 'terminal-2',
    geometry: { w: 820, h: 480 },
    mount(body, params, win) {
      body.classList.add('term-body');
      const host = FX.el('div', { class: 'term-host' });
      body.append(host);
      const term = new window.Terminal({
        fontFamily: '"JetBrains Mono", "Cascadia Mono", "DejaVu Sans Mono", "Noto Sans Mono CJK SC", monospace',
        fontSize: 13, cursorBlink: true, allowProposedApi: true, scrollback: 5000,
        theme: { background: '#0d1016', foreground: '#d7dae0', cursor: '#ff8a3d', selectionBackground: '#33415e', scrollbarSliderBackground: 'rgba(128,134,150,.32)', scrollbarSliderHoverBackground: 'rgba(150,156,172,.6)', scrollbarSliderActiveBackground: 'rgba(255,138,61,.7)' },
        overviewRuler: { width: 0 },
      });
      const fit = new window.FitAddon.FitAddon();
      term.loadAddon(fit);
      term.open(host);
      let ptyId = null;
      let exited = false;
      const doFit = () => { try { fit.fit(); if (ptyId) window.foxos.pty.resize(ptyId, term.cols, term.rows); } catch { /* 尚未布局 */ } };
      const ro = new ResizeObserver(() => doFit());
      ro.observe(host);
      setTimeout(doFit, 0);
      const ready = window.foxos.pty.spawn({ cols: term.cols || 100, rows: term.rows || 30, command: params.command || null, args: params.args || [] }).then((info) => {
        ptyId = info.id;
        win.ptyId = info.id;
        win.shell = info.shell;
        if (!params.title) win.setTitle(FX.t('terminal.terminal', info.title));
        ptyHandlers.set(info.id, {
          data: (d) => term.write(d),
          exit: (code) => {
            exited = true;
            term.write(FX.t('terminal.2m_process_exited_with_code_0m', code));
            win.exitCode = code;
            params.onExit && params.onExit(code);
            FX.emit('pty-exit', { winId: win.id, code });
          },
        });
        term.onData((d) => { if (!exited) window.foxos.pty.write(info.id, d); });
        doFit();
        return info;
      }).catch((e) => { term.write(FX.t('terminal.cannot_start_the_terminal', e.message)); });
      term.focus();
      return {
        term, ready,
        onResize: doFit,
        persistParams: () => (params.command ? null : {}),
        // 测试与自动化：读取终端屏幕上的文本
        screenText: () => {
          const b = term.buffer.active; const lines = [];
          for (let i = 0; i < b.length; i++) lines.push(b.getLine(i)?.translateToString(true) || '');
          return lines.join('\n');
        },
        dispose: () => { ro.disconnect(); if (ptyId) { window.foxos.pty.kill(ptyId); ptyHandlers.delete(ptyId); } term.dispose(); },
      };
    },
  });

  // 在终端里运行一条命令（安装向导等），返回退出码
  FX.runInTerminal = (title, commandLine) => new Promise((resolve) => {
    const isWin = FX.env.platform === 'win32';
    const command = isWin ? 'powershell.exe' : (FX.env.shell || '/bin/sh');
    const args = isWin ? ['-NoProfile', '-Command', commandLine] : ['-c', `${commandLine}`];
    FX.openWindow('terminal', { title, command, args, onExit: resolve });
  });
  // 在终端里运行 foxos：主进程给出 foxos 的绝对路径命令行（不依赖 PATH 上有 foxos）
  FX.foxosCommandLine = (args) => window.foxos.cli.commandLine(args);
  FX.runFoxosInTerminal = async (title, args) => FX.runInTerminal(title, await FX.foxosCommandLine(args));
})();
