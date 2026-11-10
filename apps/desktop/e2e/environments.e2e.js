// US-37 环境应用：在 GUI 中创建、启动、执行自定义操作、快照，结果与 CLI 看到的状态一致
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { cli, launch, shot, tmpWorkspace, readAudit } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_HOME || fs.mkdtempSync('/tmp/foxos-e2e-home-');
const extraEnv = { FOXOS_HOME };
const NAME = `gui${process.pid}`;

test('US-37 环境应用的 GUI 操作与 CLI 状态一致', { skip: process.platform !== 'linux' && '仅 Linux 后端可在本机端到端运行' }, async () => {
  const ws = tmpWorkspace('env');
  cli(ws, ['env', 'pull', 'alpine-3.20'], { extraEnv });
  const { app, page } = await launch(ws, { extraEnv });
  try {
    await page.dblclick('[data-launch=environments]');
    await page.waitForSelector('[data-act=env-new]');
    // GUI：新建环境（无网络、工作空间读写）
    await page.click('[data-act=env-new]');
    await page.fill('input[name=env-name]', NAME);
    await page.selectOption('select[name=env-image]', 'alpine-3.20');
    await page.click('.dialog button[type=submit]');
    await page.waitForSelector(`[data-env="${NAME}"]`, { timeout: 60000 });
    let st = cli(ws, ['env', 'info', NAME], { extraEnv }).result;
    assert.equal(st.state, 'stopped');
    assert.equal(st.image, 'alpine-3.20');

    // GUI：启动 → CLI 看到运行中
    await page.click(`[data-env="${NAME}"]`);
    await page.click('[data-act=start]');
    await page.waitForSelector('[data-act=stop]', { timeout: 60000 });
    st = cli(ws, ['env', 'info', NAME], { extraEnv }).result;
    assert.equal(st.state, 'running');
    // 概览里的实时资源数据来自真实环境
    await page.waitForFunction(() => { const v = document.querySelector('[data-stat=processes]'); return v && v.textContent !== '—'; });
    await shot(page, 'US-37-environments');

    // GUI：添加并运行自定义操作，写入工作空间
    await page.click('[data-tab=actions]');
    await page.fill('input[placeholder^="操作名"]', 'hello');
    await page.fill('input[placeholder^="例如"]', 'echo "from ${env} on ${image}" > /workspace/hello.txt && cat /workspace/hello.txt');
    await page.click('.envs form.row button[type=submit]');
    await page.waitForSelector('[data-run=hello]');
    await page.click('[data-run=hello]');
    await page.waitForFunction(() => /退出码 0/.test(document.querySelector('.envs .out')?.textContent || ''), null, { timeout: 60000 });
    assert.equal(fs.readFileSync(path.join(ws, 'hello.txt'), 'utf8').trim(), `from ${NAME} on alpine-3.20`);

    // CLI 停止 → GUI 通过审计事件实时刷新
    cli(ws, ['env', 'stop', NAME], { extraEnv });
    await page.waitForSelector('[data-act=start]', { timeout: 30000 });

    // GUI：快照 → CLI 看到同一个快照
    await page.click('[data-tab=snapshots]');
    await page.click('[data-act=snapshot]');
    await page.fill('.dialog input', 'gui');
    await page.click('.dialog button[type=submit]');
    await page.waitForSelector('[data-restore]', { timeout: 60000 });
    const snaps = cli(ws, ['env', 'info', NAME], { extraEnv }).result.snapshots_detail;
    assert.equal(snaps.length, 1);
    assert.equal(snaps[0].label, 'gui');
    const guiId = await page.getAttribute('[data-restore]', 'data-restore');
    assert.equal(guiId, snaps[0].id);

    // 审计：GUI 操作记为 human，CLI 操作记为 e2e-cli
    const audit = readAudit(ws).filter((a) => String(a.command).startsWith('env.'));
    assert.ok(audit.some((a) => a.command === 'env.create' && /human/.test(a.agent)), JSON.stringify(audit.slice(-5)));
    assert.ok(audit.some((a) => a.command === 'env.stop' && a.agent === 'e2e-cli'));
  } finally {
    try { cli(ws, ['env', 'delete', NAME], { extraEnv, check: false }); } catch { /* 清理 */ }
    await app.close();
  }
});
