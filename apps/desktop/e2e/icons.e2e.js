// US-53 程序图标：每个程序显示它自己的开源项目自带的图标（<img>），狐狸OS 自己的程序保留狐狸OS 风格图标；
// 报告哪些程序没有拿到图标（退回字体图标）。不替换任何被测组件：图标来自本机安装的上游组件 / LibreOffice / 系统主题 / ACP 注册表。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { ROOT, launch, shot, tmpWorkspace } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_HOME || process.env.FOXOS_HOME || fs.mkdtempSync('/tmp/foxos-e2e-home-');
const OUT = path.join(ROOT, 'docs', 'test-results', 'icons.json');

// 等页面里所有 <img> 加载完成或失败（失败的会被替换成字体图标）
const settle = (page, sel) => page.waitForFunction((s) => [...document.querySelectorAll(`${s} img.app-img`)].every((i) => i.complete), sel, { timeout: 30000 });
const tileState = (page, sel) => page.$$eval(sel, (els) => els.map((e) => {
  const img = e.querySelector('img.app-img');
  const fb = e.querySelector('[data-icon-missing]');
  return { key: e.dataset.evApp || e.dataset.appId || e.dataset.launch || e.dataset.evLaunch, img: img ? img.getAttribute('src') : null, ok: !!(img && img.complete && img.naturalWidth > 0), missing: fb ? fb.dataset.iconMissing : null, font: !img && !fb && !!e.querySelector('.ti') };
}));

test('US-53 每个程序使用其开源项目自带的图标', async () => {
  const ws = tmpWorkspace('icons');
  const { app, page } = await launch(ws, { extraEnv: { FOXOS_HOME } });
  try {
    const report = await page.evaluate(() => window.foxos.icons.report());
    const own = ['files', 'environments', 'appcenter', 'settings', 'bots', 'computer'];

    // 桌面快捷方式与开始菜单
    await settle(page, '#desktop-icons');
    const desk = await tileState(page, '#desktop-icons [data-launch]');
    for (const t of desk) {
      if (own.includes(t.key)) { assert.ok(t.font, `${t.key} 是狐狸OS 自己的程序，应保留狐狸OS 风格图标`); continue; }
      const b = report.builtins.find((x) => x.id === t.key);
      assert.ok(b, `未知的内置程序 ${t.key}`);
      if (b.source) assert.ok(t.ok, `${t.key} 的图标（${b.file}）没有渲染出来`);
      else assert.ok(t.missing, `${t.key} 没有图标时应退回字体图标并标记`);
    }
    assert.ok(desk.find((t) => t.key === 'browser').ok, '浏览器应显示 Electron 图标');

    // 应用中心：51 个 Everything 应用 + ACP 智能体
    await page.dblclick('[data-launch=appcenter]');
    await page.waitForSelector('[data-ev-app]', { timeout: 60000 });
    await page.waitForSelector('.appcenter [data-action=install-agent], .appcenter .app-card .btn.primary', { timeout: 60000 });
    await settle(page, '.appcenter');
    const ev = await tileState(page, '.appcenter [data-ev-app]');
    assert.equal(ev.length, 51, '应用中心应列出 51 个 Everything 应用');
    const evMissing = [];
    for (const t of ev) {
      const r = report.everything.find((x) => x.id === t.key);
      assert.equal(t.img || t.missing, `foxicon://everything/${t.key}`, `${t.key} 的图标来源应是上游组件`);
      if (r.source) assert.ok(t.ok, `${t.key} 有上游图标（${r.source}）但没有渲染出来`);
      else { assert.ok(t.missing, `${t.key} 没有图标时应退回字体图标并标记`); evMissing.push(t.key); }
    }
    // MIT 应用的图标随狐狸OS 分发，必须全部可用；AGPL 应用只在安装后从上游组件读取
    for (const r of report.everything) if (r.license === 'MIT') assert.ok(r.source, `MIT 应用 ${r.id} 应有随附图标`);
    for (const r of report.everything) if (r.source === 'bundled-mit') assert.notEqual(r.license, 'AGPL-3.0', `AGPL 应用 ${r.id} 的图标不能随仓库分发`);

    const agents = await page.evaluate(async () => (await window.foxos.agents.list()).agents.map((a) => ({ id: a.id, icon: a.icon })));
    const ag = await tileState(page, '.appcenter [data-app-id]');
    const agentRows = ag.filter((t) => agents.some((a) => a.id === t.key));
    for (const t of agentRows) {
      const a = agents.find((x) => x.id === t.key);
      if (a.icon) assert.equal(t.img || t.missing, a.icon, `${t.key} 应使用 ACP 注册表的 icon 字段`);
    }
    await shot(page, 'US-53-appcenter-icons');

    // 开始菜单：已安装的 Everything 应用
    await page.click('#start');
    await settle(page, '#start-menu');
    const start = await tileState(page, '#start-menu [data-ev-launch]');
    for (const t of start) assert.ok(t.ok || t.missing, `开始菜单里的 ${t.key} 没有图标`);
    await shot(page, 'US-53-start-icons');
    await page.keyboard.press('Escape'); await page.mouse.click(800, 400);

    // 窗口标题栏与任务栏
    const first = report.everything.find((r) => r.source && fs.existsSync(path.join(FOXOS_HOME, 'everything', r.id, 'dist', 'index.html')));
    if (first) {
      await page.evaluate((id) => FX.openWindow('everything', { app: id }), first.id);
      await page.waitForSelector(`.window[data-app=everything] .win-icon img[src="foxicon://everything/${first.id}"]`, { timeout: 30000 });
      await page.waitForSelector(`.task[data-app=everything] img[src="foxicon://everything/${first.id}"]`, { timeout: 30000 });
      await settle(page, '.taskbar');
      assert.ok(await page.$eval('.task[data-app=everything] img', (i) => i.naturalWidth > 0), '任务栏图标没有渲染出来');
    }

    const result = {
      everything: { total: 51, rendered: ev.filter((t) => t.ok).length, missing: evMissing, sources: report.everything.reduce((m, r) => { m[r.source || 'none'] = (m[r.source || 'none'] || 0) + 1; return m; }, {}) },
      builtins: report.builtins.map((b) => ({ id: b.id, source: b.source, file: b.file && path.relative(ROOT, b.file).startsWith('..') ? b.file : b.file && path.relative(ROOT, b.file), rendered: !!(desk.find((t) => t.key === b.id) || {}).ok })),
      agents: { total: agentRows.length, withRegistryIcon: agents.filter((a) => a.icon).length, rendered: agentRows.filter((t) => t.ok).length, missing: agentRows.filter((t) => !t.ok).map((t) => t.key) },
      foxosOwn: own,
    };
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    fs.writeFileSync(OUT, JSON.stringify(result, null, 2));
    console.log(`图标覆盖：Everything ${result.everything.rendered}/51（缺 ${evMissing.join(', ') || '无'}）；内置 ${result.builtins.filter((b) => b.rendered).length}/${result.builtins.length}（${result.builtins.map((b) => `${b.id}:${b.source || '缺'}`).join(', ')}）；ACP 智能体 ${result.agents.rendered}/${result.agents.total}`);
  } finally {
    await app.close();
  }
});
