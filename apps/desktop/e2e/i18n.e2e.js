// US-55 多语言：默认简体中文；安装向导与设置里可切换到 English，立即生效并保存；
// 切换后外壳、应用中心（分组名、应用说明）、开始菜单、对话框与内核（CLI / MCP）消息都是英文；切回中文同样生效。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { launch, shot, tmpWorkspace, cli } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_HOME || process.env.FOXOS_HOME || fs.mkdtempSync('/tmp/foxos-e2e-home-');
const HAN = /[\u4e00-\u9fff]/;
// 页面上可见文字中的中文（语言选择器里各语言用自己的名字显示，不算）
const visibleHan = (page) => page.evaluate(() => {
  const out = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    const el = n.parentElement;
    if (!el || el.closest('.lang-picker, .lang-label, webview, .xterm, .monaco-editor, code, pre') || !el.getClientRects().length) continue;
    if (/[\u4e00-\u9fff]/.test(n.textContent)) out.push(n.textContent.trim().slice(0, 60));
  }
  for (const el of document.querySelectorAll('[title],[placeholder],[aria-label]')) for (const a of ['title', 'placeholder', 'aria-label']) { const v = el.getAttribute(a); if (v && /[\u4e00-\u9fff]/.test(v) && !el.closest('.lang-picker')) out.push(`${a}=${v.slice(0, 60)}`); }
  return [...new Set(out)];
});
const reloaded = async (page) => { await page.waitForEvent('load', { timeout: 30000 }); await page.waitForSelector('body.ready', { timeout: 60000 }); };

test('US-55 默认中文，可在设置中实时切换到 English 并保存', async () => {
  const ws = tmpWorkspace('i18n');
  let { app, page, ud } = await launch(ws, { extraEnv: { FOXOS_HOME } });
  try {
    // 默认：简体中文
    assert.equal(await page.getAttribute('html', 'lang'), 'zh-CN');
    assert.equal((await page.textContent('#start span')).trim(), '开始');
    // 安装向导第一步有语言选择
    await page.evaluate(() => FX.openWindow('setup', {}));
    await page.waitForSelector('.wizard [data-field=language] [data-lang=en-US]');
    assert.deepEqual(await page.$$eval('.wizard [data-lang]', (b) => b.map((x) => x.textContent)), ['简体中文', 'English']);
    await page.evaluate(() => FX.windows().forEach((w) => FX.closeWindow(w)));

    // 设置 → English：界面立即重新载入为英文，打开的窗口恢复
    await page.dblclick('[data-launch=appcenter]');
    await page.waitForSelector('[data-ev-app]', { timeout: 60000 });
    await page.click('#open-settings');
    await page.waitForSelector('[data-section=language] [data-lang=en-US]');
    await Promise.all([reloaded(page), page.click('[data-section=language] [data-lang=en-US]')]);
    assert.equal(await page.getAttribute('html', 'lang'), 'en-US');
    assert.equal((await page.textContent('#start span')).trim(), 'Start');
    assert.equal(JSON.parse(fs.readFileSync(path.join(ud, 'settings.json'), 'utf8')).lang, 'en-US', '语言应保存到设置');
    await page.waitForSelector('.window[data-app=appcenter] [data-ev-app]', { timeout: 60000 });
    assert.equal(await page.textContent('.ev-group[data-group=office] .row b'), 'Office');
    assert.match(await page.textContent('[data-ev-app=documents] .app-card-main .muted'), /word processor/);
    await page.waitForTimeout(800);
    let han = await visibleHan(page);
    assert.deepEqual(han, [], `英文界面里不应有中文：${han.join(' | ')}`);
    await shot(page, 'US-55-english-appcenter');
    // 开始菜单、设置、环境、文件、编辑器、活动面板
    for (const a of ['files', 'environments', 'editor', 'settings']) await page.evaluate((x) => FX.openWindow(x, {}), a);
    await page.click('#start');
    await page.click('[data-tab=activity]');
    await page.waitForTimeout(1500);
    han = await visibleHan(page);
    assert.deepEqual(han, [], `英文界面里不应有中文：${han.join(' | ')}`);
    await page.click('#start');
    // 对话框
    await page.evaluate(() => { FX.confirm(FX.t('common.delete'), FX.t('common.unknown_app')); });
    await page.waitForSelector('.dialog');
    assert.ok(!HAN.test(await page.textContent('.dialog')));
    await page.keyboard.press('Escape');
    // 内核消息跟随界面语言（桌面调用内核时传 FOXOS_LANG）
    const r = await page.evaluate(() => window.foxos.run(['files', 'read', 'no-such-file.txt']));
    assert.equal(r.ok, false);
    assert.ok(!HAN.test(r.data.error.message), `内核错误应为英文：${r.data.error.message}`);
    assert.equal(r.data.error.code, 'NOT_FOUND', 'JSON 字段与错误码保持英文');
  } finally {
    await app.close();
  }
  // 重新启动后仍是英文；在设置里切回中文
  ({ app, page } = await launch(ws, { extraEnv: { FOXOS_HOME }, userData: ud, keepSettings: true }));
  try {
    assert.equal(await page.getAttribute('html', 'lang'), 'en-US');
    await page.click('#open-settings');
    await page.waitForSelector('[data-section=language] [data-lang=zh-CN]');
    await Promise.all([reloaded(page), page.click('[data-section=language] [data-lang=zh-CN]')]);
    assert.equal(await page.getAttribute('html', 'lang'), 'zh-CN');
    assert.equal((await page.textContent('#start span')).trim(), '开始');
  } finally {
    await app.close();
  }
  // CLI：FOXOS_LANG / --lang（默认中文），JSON 字段名不变
  const zh = cli(ws, ['files', 'read', 'nope.txt'], { check: false });
  const en = cli(ws, ['--lang', 'en-US', 'files', 'read', 'nope.txt'], { check: false });
  const en2 = cli(ws, ['files', 'read', 'nope.txt'], { check: false, extraEnv: { FOXOS_LANG: 'en-US' } });
  assert.ok(HAN.test(zh.error.message), zh.error.message);
  assert.ok(!HAN.test(en.error.message), en.error.message);
  assert.equal(en.error.message, en2.error.message);
  assert.deepEqual(Object.keys(en).sort(), Object.keys(zh).sort());
});

// Everything 应用：狐狸OS 通过 Chromium 语言（navigator.language）把界面语言传给上游应用；
// 上游提供了中文界面的（spreadsheet）跟随切换，其余应用在中文下标「英文界面」（见 data/everything-locale.json）
const evText = (page) => page.evaluate(async () => {
  const v = document.querySelector('.window[data-app=everything] webview');
  try { return JSON.parse(await v.executeJavaScript('JSON.stringify([navigator.language, document.documentElement.lang, (document.body && document.body.innerText) || ""])')); } catch { return null; }
});
test('US-55 Everything 应用跟随狐狸OS 语言（上游支持时）', async (t) => {
  if (!fs.existsSync(path.join(FOXOS_HOME, 'everything', 'spreadsheet', 'dist', 'index.html'))) return t.skip('需要已安装的 spreadsheet（FOXOS_HOME）');
  const ws = tmpWorkspace('i18n-ev');
  for (const [lang, want, uiLang, badge] of [['zh-CN', /文件\n编辑\n视图/, 'zh-Hans', true], ['en-US', /File\nEdit\nView/, 'en', false]]) {
    const { app, page } = await launch(ws, { extraEnv: { FOXOS_HOME, FOXOS_LANG: lang } });
    try {
      await page.dblclick('[data-launch=appcenter]');
      await page.waitForSelector('[data-ev-app=chess]', { timeout: 60000 });
      assert.equal(await page.$('[data-ev-app=chess] [data-ui-lang]') !== null, badge, `${lang}：没有中文界面的应用${badge ? '应' : '不应'}标「英文界面」`);
      assert.equal(await page.$('[data-ev-app=spreadsheet] [data-ui-lang]'), null, 'spreadsheet 有中文界面，不标');
      await page.evaluate(() => FX.windows().forEach((w) => FX.closeWindow(w)));
      await page.evaluate(() => FX.openWindow('everything', { app: 'spreadsheet' }));
      await page.waitForSelector('.window[data-app=everything] webview', { timeout: 30000 });
      let r = null;
      for (let i = 0; i < 60 && !(r && want.test(r[2])); i++) { await page.waitForTimeout(500); r = await evText(page); }
      assert.ok(r, 'spreadsheet 页面应载入');
      assert.equal(r[0], lang, 'navigator.language 跟随狐狸OS 语言');
      assert.equal(r[1], uiLang, 'spreadsheet 选用对应语言的界面');
      assert.match(r[2], want);
      await shot(page, `US-55-spreadsheet-${lang}`);
    } finally {
      await app.close();
    }
  }
});
