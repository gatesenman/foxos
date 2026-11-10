// US-52 轻量沙箱：在会话面板的“运行位置”选择“轻量沙箱（不联网）”启动真实的 ACP 智能体（Gemini CLI），
// 智能体进程运行在宿主上但受 Landlock + seccomp 限制（NoNewPrivs、Seccomp 过滤、私有 HOME），
// foxos MCP 留在沙箱外（宿主 HTTP），沙箱只放行到该端口的 TCP 连接。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');
const { cli, launch, shot, tmpWorkspace, PY, ROOT } = require('./helpers');

const FOXOS_HOME = process.env.FOXOS_TEST_AGENT_HOME || '/tmp/foxos-e2e-agents';
const extraEnv = { FOXOS_HOME };

function procInfo(pid) {
  const status = fs.readFileSync(`/proc/${pid}/status`, 'utf8');
  const env = Object.fromEntries(fs.readFileSync(`/proc/${pid}/environ`, 'utf8').split('\0').filter(Boolean).map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1)]));
  return { status, env };
}

test('US-52 智能体在轻量沙箱中运行（真实 Gemini CLI，Landlock + seccomp）', { skip: process.platform !== 'linux' && '本机端到端只覆盖 Linux 实现' }, async () => {
  fs.mkdirSync(FOXOS_HOME, { recursive: true });
  const ws = tmpWorkspace('sandbox');
  const caps = cli(ws, ['sandbox', 'check'], { extraEnv }).result;
  assert.ok(caps.available, `本机不支持轻量隔离：${caps.reason}`);
  const { app, page } = await launch(ws, { extraEnv });
  try {
    const installed = await page.evaluate(() => window.foxos.agents.installed());
    if (!installed.some((a) => a.id === 'gemini')) await page.evaluate(() => window.foxos.agents.install('gemini'));
    await page.evaluate(() => FX.openPanel());
    await page.waitForSelector('#agent-where');
    await page.evaluate(() => FX.emit && FX.emit('agents-changed'));
    await page.waitForFunction(() => [...document.querySelectorAll('#agent-picker option')].some((o) => o.value === 'gemini'), null, { timeout: 30000 });
    await page.selectOption('#agent-picker', 'gemini');
    await page.selectOption('#agent-where', '@sandbox-offline');
    await page.click('#agent-start');
    await page.waitForFunction(() => document.querySelector('#transcript').textContent.includes('轻量沙箱（不联网）'), null, { timeout: 120000 });
    const text = await page.textContent('#transcript');
    assert.match(text, /已连接 .*Gemini/);
    await shot(page, 'us52-sandbox-agent');

    // 真实进程检查：智能体进程（gemini.js --acp）带着 NoNewPrivs 与 seccomp 过滤运行，HOME 是沙箱私有目录
    const pids = execFileSync('pgrep', ['-f', 'gemini-cli/bundle/gemini.js --acp']).toString().trim().split('\n').map(Number);
    const mine = pids.map((pid) => ({ pid, ...procInfo(pid) })).filter((p) => p.env.FOXOS_WORKSPACE === ws);
    assert.ok(mine.length >= 1, '找不到本次启动的智能体进程');
    for (const p of mine) {
      assert.match(p.status, /NoNewPrivs:\s+1/);
      assert.match(p.status, /Seccomp:\s+2/);
      assert.equal(p.env.FOXOS_SANDBOX, 'light');
      assert.ok(p.env.HOME.startsWith(path.join(FOXOS_HOME, 'sandbox', 'gemini')), p.env.HOME);
    }
    // 同一套限制下写工作空间以外会被拒绝（与智能体使用同一个启动器）
    const p = spawnSync(PY, ['-m', 'foxos', '--workspace', ws, 'sandbox', 'run', '--network', 'off', '--json', '--', 'sh', '-c', `echo x > ${FOXOS_HOME}/escape.txt; echo ok > inside.txt`],
      { env: { ...process.env, ...extraEnv, PYTHONPATH: path.join(ROOT, 'packages', 'core') }, encoding: 'utf8' });
    assert.equal(JSON.parse(p.stdout).ok, true, p.stdout + p.stderr);
    assert.equal(fs.existsSync(path.join(FOXOS_HOME, 'escape.txt')), false);
    assert.equal(fs.readFileSync(path.join(ws, 'inside.txt'), 'utf8'), 'ok\n');
  } finally {
    await app.close();
  }
});
