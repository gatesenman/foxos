// 终端：xterm.js + node-pty，连接宿主系统真实的 shell
'use strict';
(() => {
  const ptyHandlers = new Map();
  window.foxos.pty.onData((id, data) => ptyHandlers.get(id)?.data(data));
  window.foxos.pty.onExit((id, code) => ptyHandlers.get(id)?.exit(code));

  FX.registerApp('terminal', {
    title: (p) => p.title || '终端',
    icon: 'terminal-2',
    geometry: { w: 820, h: 480 },
    mount(body, params, win) {
      body.classList.add('term-body');
      const host = FX.el('div', { class: 'term-host' });
      body.append(host);
      const term = new window.Terminal({
        fontFamily: '"JetBrains Mono", "Cascadia Mono", "DejaVu Sans Mono", "Noto Sans Mono CJK SC", monospace',
        fontSize: 13, cursorBlink: true, allowProposedApi: true, scrollback: 5000,
        theme: { background: '#0d1016', foreground: '#d7dae0', cursor: '#ff8a3d', selectionBackground: '#33415e' },
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
        if (!params.title) win.setTitle(`终端 — ${info.title}`);
        ptyHandlers.set(info.id, {
          data: (d) => term.write(d),
          exit: (code) => {
            exited = true;
            term.write(`\r\n\x1b[2m[进程已退出，退出码 ${code}]\x1b[0m\r\n`);
            win.exitCode = code;
            params.onExit && params.onExit(code);
            FX.emit('pty-exit', { winId: win.id, code });
          },
        });
        term.onData((d) => { if (!exited) window.foxos.pty.write(info.id, d); });
        doFit();
        return info;
      }).catch((e) => { term.write(`无法启动终端：${e.message}\r\n`); });
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
})();
