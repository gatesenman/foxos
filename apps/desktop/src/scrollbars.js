// 滚动时给滚动容器加 fx-scrolling（键盘 / 滚轮滚动时滚动条也会出现，停止 900ms 后隐藏）。
// 桌面外壳直接加载；应用 webview 由主进程注入。
(() => {
  if (window.__fxScrollbars) return; window.__fxScrollbars = true;
  const timers = new WeakMap();
  document.addEventListener('scroll', (e) => {
    const t = e.target === document ? document.documentElement : e.target;
    if (!t || !t.classList) return;
    t.classList.add('fx-scrolling');
    clearTimeout(timers.get(t));
    timers.set(t, setTimeout(() => t.classList.remove('fx-scrolling'), 900));
  }, { capture: true, passive: true });
})();
