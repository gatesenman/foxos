// US-54 滚动条：桌面外壳、应用 webview、Monaco、终端都不使用系统 / Chromium 默认滚动条，
// 而是狐狸OS 的细滚动条（轨道透明、平时隐藏、指向时出现并变宽）。截图逐像素检查，不替换任何被测组件。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const { launch, shot, tmpWorkspace } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_HOME || process.env.FOXOS_HOME || fs.mkdtempSync('/tmp/foxos-e2e-home-');

// 用 Electron 自己截取窗口里某个矩形（capturePage），返回与背景色差异明显的列数（滚动条可见宽度）
async function visibleCols(app, rect, bg) {
  const { w, h, d } = await app.evaluate(async ({ BrowserWindow }, r) => {
    const img = await BrowserWindow.getAllWindows()[0].webContents.capturePage(r);
    const s = img.getSize();
    return { w: s.width, h: s.height, d: img.toBitmap().toString('base64') };
  }, rect);
  const px = Buffer.from(d, 'base64'); // BGRA
  let cols = 0;
  for (let x = 0; x < w; x++) {
    let diff = 0;
    for (let y = 0; y < h; y++) {
      const i = (y * w + x) * 4;
      if (Math.abs(px[i + 2] - bg[0]) + Math.abs(px[i + 1] - bg[1]) + Math.abs(px[i] - bg[2]) > 40) diff++;
    }
    if (diff >= 12) cols++; // 滑块最短 32px
  }
  return cols;
}

test('US-54 外壳与应用窗口使用狐狸OS 滚动条', async () => {
  const ws = tmpWorkspace('scroll');
  const { app, page } = await launch(ws, { extraEnv: { FOXOS_HOME } });
  try {
    await page.dblclick('[data-launch=appcenter]');
    await page.waitForSelector('[data-ev-app]', { timeout: 60000 });
    const sc = '.window[data-app=appcenter] .appcenter';
    const info = await page.$eval(sc, (e) => {
      const sb = getComputedStyle(e, '::-webkit-scrollbar');
      const th = getComputedStyle(e, '::-webkit-scrollbar-thumb');
      const r = e.getBoundingClientRect();
      return { w: sb.width, scrollable: e.scrollHeight > e.clientHeight, gutter: e.offsetWidth - e.clientWidth, thumbBg: th.backgroundColor, sw: getComputedStyle(e).scrollbarWidth,
        rect: { x: Math.round(r.right - (e.offsetWidth - e.clientWidth)), y: Math.round(r.top + 40), width: e.offsetWidth - e.clientWidth, height: Math.round(r.height - 80) },
        bg: getComputedStyle(e.closest('.window')).backgroundColor };
    });
    assert.ok(info.scrollable, '应用中心应可滚动');
    assert.equal(info.w, '10px', '滚动条宽度应为狐狸OS 的 10px（Chromium 默认 15px）');
    assert.equal(info.gutter, 10);
    assert.equal(info.sw, 'auto', '不能设置 scrollbar-width（会覆盖自定义样式）');
    const bg = (info.bg.match(/\d+/g) || [0, 0, 0]).slice(0, 3).map(Number);

    // 平时隐藏：鼠标不在滚动区域时，滚动条区域只有背景色
    await page.mouse.move(5, 500);
    await page.waitForTimeout(1200);
    const hidden = await visibleCols(app, info.rect, bg);
    assert.equal(hidden, 0, `鼠标离开时滚动条应隐藏（实际可见 ${hidden} 列）`);
    // 指向滚动区域：出现，且很细（≤ 6px）
    await page.hover(`${sc} .ev-group`);
    await page.waitForTimeout(300);
    const shown = await visibleCols(app, info.rect, bg);
    assert.ok(shown >= 2 && shown <= 6, `指向时滚动条应可见且细（实际 ${shown} 列）`);
    await shot(page, 'US-54-scrollbar-hover');
    // 滚动中（键盘 / 滚轮）也出现
    await page.mouse.move(5, 500);
    await page.$eval(sc, (e) => { e.scrollTop += 300; });
    assert.ok(await page.$eval(sc, (e) => e.classList.contains('fx-scrolling')), '滚动时应标记 fx-scrolling');

    // Everything 应用 webview：主进程注入同样的滚动条样式
    const evApp = ['documents', 'notes', 'chess', 'crm'].find((id) => fs.existsSync(`${FOXOS_HOME}/everything/${id}/dist/index.html`));
    if (evApp) {
      await page.evaluate((id) => FX.openWindow('everything', { app: id }), evApp);
      await page.waitForSelector('.window[data-app=everything] webview', { timeout: 30000 });
      let w = null;
      for (let i = 0; i < 40 && w !== '10px|true'; i++) {
        await page.waitForTimeout(500);
        w = await page.evaluate(async () => {
          const v = document.querySelector('.window[data-app=everything] webview');
          try { return await v.executeJavaScript("getComputedStyle(document.documentElement, '::-webkit-scrollbar').width + '|' + !!window.__fxScrollbars"); } catch (e) { return String(e.message); }
        });
      }
      assert.equal(w, '10px|true', `${evApp} 的 webview 应注入狐狸OS 滚动条`);
    }

    // Monaco 与终端：用自己的滚动条组件，配置为同样的细滚动条 / 颜色
    await page.evaluate(() => FX.openWindow('editor', {}));
    await page.waitForFunction(() => FX.windows().some((x) => x.editor), null, { timeout: 60000 });
    const mon = await page.evaluate(() => { const e = FX.windows().find((x) => x.editor).editor; const o = e.getOptions(); const m = window.monaco.editor.EditorOption; const s = o.get(m.scrollbar); return { v: s.verticalScrollbarSize, slider: s.verticalSliderSize, shadows: s.useShadows }; });
    assert.deepEqual(mon, { v: 10, slider: 6, shadows: false });
    await page.evaluate(() => FX.openWindow('terminal', {}));
    await page.waitForSelector('.window[data-app=terminal] .xterm', { timeout: 30000 });
    const xt = await page.$eval('.window[data-app=terminal] .xterm', (e) => { const v = e.querySelector('.xterm-viewport'); return { native: v ? getComputedStyle(v, '::-webkit-scrollbar').width : null, dom: !!e.querySelector('.xterm-scrollable-element, .scrollbar') }; });
    assert.ok(xt.dom || xt.native === '10px', `终端滚动条应为 xterm 自带的细滚动条或狐狸OS 样式：${JSON.stringify(xt)}`);
    await shot(page, 'US-54-scrollbars');
  } finally {
    await app.close();
  }
});
