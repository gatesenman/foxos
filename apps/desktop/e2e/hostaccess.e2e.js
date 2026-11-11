// US-156 「允许在本机执行」只有一个开关：桌面客户端的设置和 `foxos bot host-access` 读写同一个状态（FOXOS_HOME/host-access.json）。
// 客户端模式（FOXOS_CLIENT_MODE=1），不需要来宾：这里只测本机开关本身。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { _electron } = require('playwright');
const { ROOT, PY, cli, shot, tmpWorkspace, readAudit, env } = require('./helpers');

test('US-156 设置里的本机执行开关和 foxos bot host-access 是同一个状态', { timeout: 15 * 60 * 1000 }, async () => {
  const ws = tmpWorkspace('hostaccess');
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-e2e-home-'));
  const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-e2e-ud-'));
  // 旧版本把开关存在 settings.json 里：这个值不再生效
  fs.writeFileSync(path.join(ud, 'settings.json'), JSON.stringify({ setupDone: true, workspace: ws, hostExecution: true }));
  const xenv = { FOXOS_HOME: home, FOXOS_PLACE: 'host' };
  const status = () => cli(ws, ['bot', 'host-access'], { agent: 'human:cli', extraEnv: xenv }).result;
  const app = await _electron.launch({
    args: ['.', '--no-sandbox', `--user-data-dir=${ud}`, `--workspace=${ws}`],
    cwd: path.join(ROOT, 'apps', 'desktop'),
    env: env({ DISPLAY: process.env.DISPLAY || ':99', FOXOS_PYTHON: PY, FOXOS_CLIENT_MODE: '1', FOXOS_HOME: home }),
    timeout: 600000,
  });
  try {
    const page = await app.firstWindow({ timeout: 600000 });
    await page.waitForSelector('body.ready', { timeout: 180000 });

    // 1. 默认关：旧 settings.json 里的 true 不算数；桌面和命令行看到的一样
    const env0 = await page.evaluate(() => FX.env);
    assert.equal(env0.mode, 'client');
    assert.equal(env0.hostExecution, false);
    assert.equal(status().enabled, false);
    const st0 = await page.evaluate(() => window.foxos.hostAccess.status());
    assert.equal(st0.on_host, true, JSON.stringify(st0));   // 客户端模式下核心认为自己在宿主上
    assert.equal(st0.path, status().path);
    const err0 = await page.evaluate(() => window.foxos.pty.spawn({ command: '/bin/sh', args: ['-c', 'true'] }).then(() => null, (e) => e.message));
    assert.ok(err0 && /本机执行已关闭|running on this PC is off/.test(err0), err0);

    // 2. 在设置里打开（先在确认框里点危险按钮）→ 命令行看到已打开，记在审计里，是人打开的
    const openSettings = async () => {
      await page.evaluate(() => { FX.windows().filter((w) => w.appId === 'settings').forEach((w) => FX.closeWindow(w)); FX.openWindow('settings', {}); });
      await page.waitForSelector('.window[data-app=settings] [data-host-exec-toggle] input', { timeout: 60000 });
      return page.locator('.window[data-app=settings] [data-host-exec-toggle] input');
    };
    let box = await openSettings();
    assert.equal(await box.isChecked(), false);
    await box.click();
    await page.click('#modal-root .dialog .btn.danger');
    await page.waitForFunction(() => FX.env.hostExecution === true, null, { timeout: 60000 });
    const st1 = status();
    assert.equal(st1.enabled, true);
    assert.equal(st1.by, 'human:desktop');
    assert.ok(readAudit(ws).some((e) => e.command === 'bot.host-access' && e.agent === 'human:desktop' && e.status === 'ok'));
    assert.equal(await page.evaluate(() => window.foxos.settings.get().then((s) => s.hostExecution)), true);
    await shot(page, 'US-156-host-access-on');
    // settings.json 里不再有自己的一份
    assert.ok(!('hostExecution' in JSON.parse(fs.readFileSync(path.join(ud, 'settings.json'), 'utf8'))));

    // 3. 智能体不能改这个开关
    const bot = cli(ws, ['bot', 'host-access', 'disable'], { agent: 'bot:fox', extraEnv: xenv, check: false });
    assert.equal(bot.ok, false, JSON.stringify(bot));
    assert.equal(status().enabled, true);

    // 4. 在命令行里关掉 → 设置里也是关，本机动作又被拒绝（不用重启）
    assert.equal(cli(ws, ['bot', 'host-access', 'disable'], { agent: 'human:cli', extraEnv: xenv }).result.enabled, false);
    assert.equal(await page.evaluate(() => window.foxos.settings.get().then((s) => s.hostExecution)), false);
    box = await openSettings();
    assert.equal(await box.isChecked(), false);
    const err1 = await page.evaluate(() => window.foxos.pty.spawn({ command: '/bin/sh', args: ['-c', 'true'] }).then(() => null, (e) => e.message));
    assert.ok(err1 && /本机执行已关闭|running on this PC is off/.test(err1), err1);

    // 5. 命令行打开 → 设置里是开；在设置里取消勾选（关闭不需要确认）→ 命令行看到关
    cli(ws, ['bot', 'host-access', 'enable'], { agent: 'human:cli', extraEnv: xenv });
    box = await openSettings();
    assert.equal(await box.isChecked(), true);
    await box.click();
    await page.waitForFunction(() => FX.env.hostExecution === false, null, { timeout: 60000 });
    assert.equal(status().enabled, false);
    await shot(page, 'US-156-host-access-off');
  } finally {
    await app.close().catch(() => {});
    for (const d of [ws, home, ud]) fs.rmSync(d, { recursive: true, force: true });
  }
});
