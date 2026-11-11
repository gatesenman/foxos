// US-50 环境 → 安装系统：一键目录、本机能力检查、从目录安装一个系统；GUI 结果与 CLI 一致
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const { cli, launch, shot, tmpWorkspace } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_HOME || fs.mkdtempSync('/tmp/foxos-e2e-home-');
const extraEnv = { FOXOS_HOME };
const NAME = `inst${process.pid}`;

test('US-50 安装系统目录与一键安装（Linux 宿主上真实安装 Alpine）', { skip: process.platform !== 'linux' && '本用例在 Linux 宿主上真实安装；Windows 见 docs/windows-test-guide.md' }, async () => {
  const ws = tmpWorkspace('envinst');
  const { app, page } = await launch(ws, { extraEnv });
  try {
    await page.dblclick('[data-launch=environments]');
    await page.click('[data-act=env-install]');
    await page.waitForSelector('[data-entry="wsl-ubuntu-24.04"]', { timeout: 60000 });
    // 目录：Linux / Windows / macOS 三类都在；macOS 禁用并说明原因；Linux 宿主上 Windows Sandbox 不可安装
    assert.ok(await page.$('[data-entry=windows-sandbox].disabled'));
    assert.match(await page.textContent('[data-entry=macos-guest]'), /Apple/);
    assert.ok(await page.$('[data-provider=linux-ns]'));
    const cat = cli(ws, ['env', 'catalog'], { extraEnv }).result;
    assert.equal(await page.$$eval('[data-entry], [data-preset]', (n) => n.length), cat.count);
    await shot(page, 'US-50-env-install');

    await page.click('[data-install=alpine]');
    await page.fill('input[name=env-name]', NAME);
    await page.click('.dialog button[type=submit]');
    await page.waitForSelector(`[data-env="${NAME}"]`, { timeout: 300000 });
    const info = cli(ws, ['env', 'info', NAME], { extraEnv }).result;
    assert.equal(info.state, 'stopped');
    assert.match(info.image, /^alpine-minirootfs-/);
    const prog = cli(ws, ['env', 'progress', NAME], { extraEnv }).result;
    assert.equal(prog.state, 'done');
    cli(ws, ['env', 'start', NAME], { extraEnv });
    const out = cli(ws, ['env', 'exec', NAME, 'cat /etc/alpine-release'], { extraEnv }).result;
    assert.match(out.stdout, /^\d+\.\d+/);
    cli(ws, ['env', 'stop', NAME], { extraEnv });
    cli(ws, ['env', 'delete', NAME], { extraEnv });
  } finally {
    await app.close();
  }
});

test('US-63 预设系统：目录顶部列出已配置好的 Linux / Windows / macOS，显示大小、可用性与原因，安装对话框', { skip: process.platform !== 'linux' && '本用例按 Linux 宿主的可用性断言' }, async () => {
  const ws = tmpWorkspace('envpreset');
  const { app, page } = await launch(ws, { extraEnv });
  try {
    await page.dblclick('[data-launch=environments]');
    await page.click('[data-act=env-install]');
    await page.waitForSelector('[data-section=presets] [data-preset="foxos-debian-12"]', { timeout: 60000 });
    const cat = cli(ws, ['env', 'catalog', '--presets'], { extraEnv }).result;
    assert.equal(await page.$$eval('[data-section=presets] [data-preset]', (n) => n.length), cat.presets);
    // 每张卡都显示下载大小与所需磁盘
    for (const e of cat.entries) {
      const txt = await page.textContent(`[data-preset="${e.id}"] [data-sizes]`);
      assert.match(txt, /\d/);
    }
    // Linux 宿主：Linux 预设可装；Windows 预设禁用并说明 cloud-hypervisor；macOS 说明 Apple 许可
    assert.ok(await page.$('[data-install-preset="foxos-debian-12"]'));
    assert.ok(await page.$('[data-preset="windows-11-enterprise-eval"].disabled'));
    assert.match(await page.textContent('[data-preset="windows-11-enterprise-eval"]'), /cloud-hypervisor/);
    assert.match(await page.textContent('[data-preset="macos-latest"]'), /Apple/);
    await page.$eval('[data-section=presets]', (n) => n.scrollIntoView());
    await shot(page, 'US-63-env-presets');
    await page.click('[data-install-preset="foxos-debian-12"]');
    await page.waitForSelector('.dialog input[name=env-name]');
    assert.ok(await page.$('.dialog input[name=env-start]'));
    assert.equal(await page.$('.dialog input[name=env-product-key]'), null);
    await shot(page, 'US-63-env-preset-dialog');
    await page.click('.dialog button.ghost');
  } finally {
    await app.close();
  }
});
