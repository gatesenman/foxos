// US-126..US-133：驱动真实的智能体窗口（foxos-bots 用 Chrome 应用模式打开，窗口类名 foxos-bots），
// 在自己的 Xvfb + xfwm4 桌面里用 Playwright（CDP 连到这个窗口）点界面：
// 新建并配置智能体、和真实的 opencode（ACP，默认免费模型，不需要密钥）对话、工具卡片和 diff、批准 / 拒绝、
// @ 委托给第二个智能体、/ 技能、添加真实的本地 MCP 连接器（foxos mcp --http + Bearer）、停靠 / 独立窗口（_NET_WM_STRUT_PARTIAL）、
// 配对第二台狐狸OS 并切换机器、人工接管让智能体停手。
// 需要：google-chrome 或 chromium、Xvfb、xfwm4、wmctrl、xprop、xfce4-terminal、联网（opencode 免费模型）。缺任何一个就跳过（不算失败）。
import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const { ROOT, PY } = require('./helpers.js');
const SHOTS = path.join(ROOT, 'docs', 'screenshots');
const which = b => spawnSync('sh', ['-c', `command -v ${b}`]).status === 0;
const BROWSER = ['google-chrome', 'chromium', 'chromium-browser'].find(which);
const NEED = ['Xvfb', 'xfwm4', 'wmctrl', 'xprop', 'xdpyinfo', 'xfce4-terminal'].filter(b => !which(b));
const SKIP = !BROWSER ? 'no chrome/chromium' : NEED.length ? 'missing ' + NEED.join(', ') : false;
const CACHE = process.env.FOXOS_TEST_RUNTIME_CACHE || '/var/tmp/foxos-test-cache/runtime';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SW = 1600, SH = 1000;

// 截图只是给文档用的，不是断言；截不到就记一条，不影响结果
async function shot(page, name) { await page.screenshot({ path: path.join(SHOTS, name), timeout: 15000 }).catch(e => console.log(`screenshot ${name}: ${e.message.split('\n')[0]}`)); }
async function freePort() { return new Promise(r => { const s = net.createServer(); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => r(p)); }); }); }
async function until(fn, ms = 240000, what = 'condition') {
  const t0 = Date.now(); let last;
  while (Date.now() - t0 < ms) { try { last = await fn(); if (last) return last; } catch (e) { last = e; } await sleep(400); }
  throw new Error(`timed out waiting for ${what}: ${last instanceof Error ? last.message : JSON.stringify(last)}`);
}

class Env {
  constructor() {
    this.root = fs.mkdtempSync(path.join(process.env.FOXOS_E2E_TMP || os.tmpdir(), 'foxos-bots-gui-'));
    this.ws = path.join(this.root, 'ws'); fs.mkdirSync(this.ws);
    let n = 120; while (fs.existsSync(`/tmp/.X${n}-lock`) || fs.existsSync(`/tmp/.X11-unix/X${n}`)) n++;
    this.display = ':' + n;
    this.env = { ...process.env, PYTHONPATH: path.join(ROOT, 'packages', 'core'), PYTHONIOENCODING: 'utf-8', DISPLAY: this.display,
      FOXOS_HOME: path.join(this.root, 'home'), XDG_DATA_HOME: path.join(this.root, 'data'), XDG_STATE_HOME: path.join(this.root, 'state'),
      XDG_CONFIG_HOME: path.join(this.root, 'config'), FOXOS_RUNTIME_BIN: path.join(this.root, 'bin'), FOXOS_BOTS_BROWSER: BROWSER };
    if (fs.existsSync(CACHE)) this.env.FOXOS_RUNTIME_PREFIX = CACHE;
    delete this.env.FOXOS_AGENT; delete this.env.FOXOS_WORKSPACE; delete this.env.DEEPSEEK_API_KEY;
    this.procs = [];
  }
  cli(args, { ws = this.ws, env = this.env, input } = {}) {
    const r = spawnSync(PY, ['-m', 'foxos', '--workspace', ws, '--agent', 'human', '--json', ...args], { env, encoding: 'utf8', input, timeout: 900000 });
    const d = r.stdout.trim() ? JSON.parse(r.stdout) : null;
    if (r.status !== 0) throw new Error(`foxos ${args.slice(0, 3).join(' ')}: ${r.status} ${r.stdout.slice(-800)} ${r.stderr.slice(-800)}`);
    return d.result;
  }
  bg(cmd, args, env = this.env) { const p = spawn(cmd, args, { env, stdio: ['ignore', 'pipe', 'pipe'] }); this.procs.push(p); return p; }
  x(cmd, args) { return execFileSync(cmd, args, { env: this.env, encoding: 'utf8' }); }
  windows() { return this.x('wmctrl', ['-lxG']).trim().split('\n').filter(Boolean).map(l => { const f = l.split(/\s+/); return { id: f[0], x: +f[2], y: +f[3], w: +f[4], h: +f[5], cls: f[6], title: f.slice(8).join(' ') }; }); }
  botWin() { return this.windows().find(w => w.cls.toLowerCase().includes('foxos-bots')); }
  strut(id) { const o = this.x('xprop', ['-id', id, '_NET_WM_STRUT_PARTIAL']); const m = o.match(/=\s*(.*)$/m); return m ? m[1].split(',').map(Number) : null; }
  botMessages(bot) { const f = path.join(this.ws, '.foxos', 'bots', bot, 'messages.jsonl'); return fs.existsSync(f) ? fs.readFileSync(f, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : []; }
  stop() {
    for (const p of this.procs.reverse()) { try { p.kill('SIGTERM'); } catch {} }
    spawnSync('pkill', ['-f', this.root]);
  }
}

test('US-126..US-133 智能体窗口：真实 Chrome 窗口里的完整流程', { skip: SKIP, timeout: 1800000 }, async t => {
  const E = new Env();
  let browser;
  try {
    // 桌面：Xvfb + xfwm4（真实窗口管理器，处理停靠的屏幕边保留）
    E.bg('Xvfb', [E.display, '-screen', '0', `${SW}x${SH}x24`, '-nolisten', 'tcp']);
    await until(() => spawnSync('xdpyinfo', [], { env: E.env }).status === 0, 20000, 'Xvfb');
    E.bg('xfwm4', ['--replace', '--compositor=off']);
    await until(() => spawnSync('wmctrl', ['-m'], { env: E.env }).status === 0, 20000, 'xfwm4');

    // 真实的代码智能体：opencode（默认免费模型，不需要密钥）；编辑 / 执行默认要人批准
    const rt = E.cli(['runtime', 'install', 'opencode']);
    assert.ok(rt.results[0].ok, JSON.stringify(rt.results[0]));
    const cdp = await freePort();
    E.env.FOXOS_BOTS_BROWSER_ARGS = `--remote-debugging-port=${cdp} --disable-gpu --password-store=basic`;
    const out = JSON.parse(E.x(PY, ['-m', 'foxos.botchat.launch', '--workspace', E.ws, '--undock']).trim().split('\n').pop());
    assert.equal(out.browser, BROWSER);
    browser = await until(() => chromium.connectOverCDP(`http://127.0.0.1:${cdp}`).catch(() => null), 30000, 'CDP');
    const page = await until(() => browser.contexts().flatMap(c => c.pages()).find(p => p.url().startsWith('http://127.0.0.1')), 30000, 'bots page');
    await page.waitForSelector('#bot-list .bot-item');
    const win = await until(() => E.botWin(), 20000, 'foxos-bots window');
    assert.ok(win.w > 600, 'separate window is a normal-sized window');
    await shot(page, 'bots-e2e-start.png');

    await t.test('US-126 新建智能体并在设置里配置（含 DeepSeek 服务商预设）', async () => {
      for (const [name, title] of [['Coder', 'writes code'], ['Helper', 'second bot']]) {
        await page.click('#btn-new-bot');
        await page.fill('#n-name', name);
        await page.fill('#n-title', title);
        await page.selectOption('#n-agent', 'opencode');
        await page.click('.modal [data-ok]');
        await page.waitForSelector('#input');
      }
      const coder = E.cli(['bot', 'config', 'get', 'coder']).config;
      assert.deepEqual([coder.name, coder.title, coder.backend.kind, coder.backend.agent], ['Coder', 'writes code', 'acp', 'opencode']);
      assert.equal(E.cli(['bot', 'config', 'get', 'helper']).config.backend.agent, 'opencode');
      // 主智能体的模型设置：选 DeepSeek 自动填地址和模型；不填密钥也能看（密钥只进密钥库）
      await page.click('.bot-item[data-id="fox"]');
      await page.click('#btn-settings');
      await page.waitForSelector('#f-kind');
      await page.click('#f-kind button[data-k="model"]');
      await page.waitForSelector('#f-provider');
      await page.selectOption('#f-provider', 'deepseek');
      assert.equal(await page.inputValue('#f-base'), 'https://api.deepseek.com');
      assert.equal(await page.inputValue('#f-model-name'), 'deepseek-flash');
      assert.match(await page.textContent('#f-provider-help'), /platform\.deepseek\.com/);
      await shot(page, 'bots-e2e-provider.png');
      await page.click('.save-bar .btn.primary');
      await until(() => E.cli(['bot', 'config', 'get', 'fox']).config.backend.provider === 'deepseek', 10000, 'provider saved');
      // 配置编码助手：改头衔，保存后后端读到
      await page.click('.bot-item[data-id="coder"]');
      await page.click('#btn-settings');
      await page.fill('#f-title', 'writes and edits code');
      await page.click('.save-bar .btn.primary');
      await until(() => E.cli(['bot', 'config', 'get', 'coder']).config.title === 'writes and edits code', 10000, 'title saved');
    });

    const handled = new Set();
    // 等这个智能体的新审批出现，在界面上点对应的按钮（允许 = 主按钮，拒绝 = 其他）
    const answer = async (bot, allow, scope = '#messages') => {
      const a = await until(() => E.cli(['bot', 'approval', 'list']).approvals.find(x => x.bot === bot && !handled.has(x.id)), 300000, `approval from ${bot}`);
      handled.add(a.id);
      const btn = await page.waitForSelector(`${scope} [data-approve="${a.id}"]${allow ? '.primary' : ':not(.primary)'}`, { timeout: 30000 });
      return { a, btn };
    };
    // 窄窗口（停靠时）侧栏收起，先点菜单按钮
    const side = async sel => {
      const el = page.locator(sel).first();
      if (!(await el.isVisible()) || !(await el.evaluate(e => { const r = e.getBoundingClientRect(); return r.right > 0 && r.left < innerWidth; }))) {
        await page.locator('#btn-side:visible, #btn-side2:visible').first().click();
        await page.waitForTimeout(400);
      }
      await el.click();
    };
    const say = async (bot, text) => {
      await page.click(`.bot-item[data-id="${bot}"]`);
      await page.waitForSelector('#input');
      const n = E.botMessages(bot).filter(m => m.role === 'bot').length;
      await page.fill('#input', text);
      await page.click('#btn-send');
      return () => E.botMessages(bot).filter(m => m.role === 'bot').length > n && E.botMessages(bot).filter(m => m.role === 'bot').pop();
    };
    fs.mkdirSync(path.join(E.ws, 'gui'));

    await t.test('US-127 真实 opencode 回合：编辑卡片带 diff，点「允许」后文件改了', async () => {
      fs.writeFileSync(path.join(E.ws, 'gui', 'hello.txt'), 'hello alpha\n');
      const done = await say('coder', 'Use your edit tool to change the word alpha to beta in gui/hello.txt. Change nothing else.');
      const { btn } = await answer('coder', true);
      await shot(page, 'bots-e2e-approval.png');
      await btn.click();
      const reply = await until(done, 300000, 'coder reply');
      await page.waitForSelector('#messages .card .diff');
      assert.equal(fs.readFileSync(path.join(E.ws, 'gui', 'hello.txt'), 'utf8'), 'hello beta\n');
      const edit = reply.cards.find(c => c.kind === 'edit' && c.approval);
      assert.ok(edit && edit.approval.decision === 'allow' && edit.approval.by === 'human', JSON.stringify(reply.cards));
      assert.ok(edit.content.some(x => x.type === 'diff' && /alpha/.test(x.oldText || '') && /beta/.test(x.newText)));
      await page.waitForSelector('#messages .approval .chip.ok');
    });

    await t.test('US-128 点「拒绝」：文件不变，卡片显示已拒绝', async () => {
      const done = await say('coder', 'Use your edit tool to change the word beta to gamma in gui/hello.txt.');
      const { btn } = await answer('coder', false);
      await btn.click();
      const reply = await until(done, 300000, 'coder reply');
      assert.equal(fs.readFileSync(path.join(E.ws, 'gui', 'hello.txt'), 'utf8'), 'hello beta\n');
      assert.ok(reply.cards.some(c => c.approval && c.approval.decision === 'deny' && c.approval.by === 'human'));
      await page.waitForSelector('#messages .approval .chip.bad');
    });

    await t.test('US-129 @ 委托给第二个智能体：弹出菜单选中 Helper，委托卡片完成，Helper 的编辑在审批页批准', async () => {
      await page.click('.bot-item[data-id="coder"]');
      await page.click('#btn-mention');
      await page.waitForSelector('#popup .opt');
      await page.keyboard.type('Help');
      await page.keyboard.press('Enter');
      assert.match(await page.inputValue('#input'), /^@Helper $/);
      const n = E.botMessages('coder').filter(m => m.role === 'bot').length;
      await page.keyboard.type('Create the file gui/helper.txt containing exactly: from helper');
      await page.click('#btn-send');
      await page.waitForSelector('#messages .card.deleg');
      await page.click('.nav-item[data-view="approvals"]');
      const { btn: allow } = await answer('helper', true, '#view');
      await shot(page, 'bots-e2e-approvals-page.png');
      await allow.click();
      const reply = await until(() => E.botMessages('coder').filter(m => m.role === 'bot').length > n && E.botMessages('coder').pop(), 300000, 'delegation');
      const card = reply.cards.find(c => c.type === 'delegation');
      assert.deepEqual([card.to, card.via, card.status], ['helper', 'mention', 'completed']);
      assert.equal(fs.readFileSync(path.join(E.ws, 'gui', 'helper.txt'), 'utf8').trim(), 'from helper');
      assert.equal(E.botMessages('helper').filter(m => m.role === 'bot').pop().delegated_by, 'bot:coder');
    });

    await t.test('US-130 / 技能：弹出菜单列出 pstack 技能，用了的技能显示在回答下面', async () => {
      await page.click('.bot-item[data-id="coder"]');
      await page.click('#btn-skill');
      await page.keyboard.type('unsl');
      const opts = await page.$$eval('#popup .opt', xs => xs.map(x => x.textContent));
      assert.ok(opts.some(x => x.includes('unslop')), opts.join('|'));
      await page.keyboard.press('Enter');
      const n = E.botMessages('coder').filter(m => m.role === 'bot').length;
      await page.keyboard.type("Rewrite this sentence and reply with only the rewrite: 'It is important to note that our robust solution leverages synergy.'");
      await page.click('#btn-send');
      const reply = await until(() => E.botMessages('coder').filter(m => m.role === 'bot').length > n && E.botMessages('coder').pop(), 300000, 'skill reply');
      assert.ok(reply.skills_used.includes('unslop'));
      assert.ok(reply.text.trim().length > 0);
      await page.waitForSelector('#messages .skills-used');
      assert.match(await page.locator('#messages .skills-used').last().textContent(), /unslop/);
    });

    await t.test('US-131 添加真实的本地 MCP 连接器（Streamable HTTP + Bearer），连接后列出工具', async () => {
      const port = await freePort();
      const token = 'gui-' + Math.random().toString(36).slice(2);
      const mws = path.join(E.root, 'mcp-ws'); fs.mkdirSync(mws);
      E.bg(PY, ['-m', 'foxos', '--workspace', mws, 'mcp', '--http', `127.0.0.1:${port}`], { ...E.env, FOXOS_MCP_TOKEN: token });
      await until(() => new Promise(r => { const s = net.connect(port, '127.0.0.1', () => { s.end(); r(true); }); s.on('error', () => r(false)); }), 30000, 'mcp http');
      await page.click('.nav-item[data-view="connectors"]');
      await page.click('#c-custom');
      await page.fill('#cc-id', 'local-foxos');
      await page.fill('#cc-title', 'Local FoxOS');
      await page.fill('#cc-url', `http://127.0.0.1:${port}/mcp`);
      await page.selectOption('#cc-auth', 'bearer');
      await page.click('.modal [data-ok]');
      await page.click('[data-cconnect="local-foxos"]');
      await page.fill('#mc-token', token);
      await page.click('.modal [data-ok]');
      await page.waitForSelector('[data-cdisc="local-foxos"]');
      await page.click('[data-ctools="local-foxos"]');
      await page.waitForFunction(() => /files_list/.test(document.querySelector('.modal')?.textContent || ''), null, { timeout: 60000 });
      await shot(page, 'bots-e2e-connector.png');
      await page.click('.modal [data-x]');
      const c = E.cli(['connector', 'list']).connectors.find(x => x.id === 'local-foxos');
      assert.ok(c && c.connected);
      assert.ok(!JSON.stringify(E.cli(['connector', 'list'])).includes(token), 'token never leaves the secret store');
    });

    await t.test('US-132 停靠：占住屏幕右边（_NET_WM_STRUT_PARTIAL），最大化的窗口不被盖住；取消停靠后释放', async () => {
      E.bg('xfce4-terminal', ['--disable-server', '--title', 'foxos-max-probe']);
      const probe = await until(() => E.windows().find(w => w.title === 'foxos-max-probe'), 20000, 'probe window');
      await page.click('#btn-dock');
      const docked = await until(() => { const w = E.botWin(); return w && w.x + w.w >= SW - 2 && w.w < 900 && w; }, 20000, 'docked geometry');
      const strut = await until(() => { const s = E.strut(docked.id); return s && s[1] > 0 && s; }, 10000, 'strut');
      assert.equal(strut[0], 0);
      assert.ok(strut[1] >= SW - docked.x - 4 && strut[1] <= SW / 2, `strut right ${strut[1]} vs window x ${docked.x}`);
      assert.ok(/_NET_WM_STATE_ABOVE/.test(E.x('xprop', ['-id', docked.id, '_NET_WM_STATE'])));
      E.x('wmctrl', ['-i', '-r', probe.id, '-b', 'add,maximized_vert,maximized_horz']);
      const max = await until(() => { const w = E.windows().find(x => x.id === probe.id); return w && w.w > 600 && w; }, 10000, 'maximized');
      assert.ok(max.x + max.w <= SW - strut[1] + 2, `maximized window ${max.x}+${max.w} overlaps the dock (${SW - strut[1]})`);
      await shot(page, 'bots-e2e-docked.png');
      await side('#btn-dock');
      await until(() => { const w = E.botWin(); return w && w.w > 900; }, 20000, 'separate window');
      assert.equal(E.strut(E.botWin().id), null, 'strut removed after undock');
      E.x('wmctrl', ['-i', '-r', probe.id, '-b', 'remove,maximized_vert,maximized_horz']);
      E.x('wmctrl', ['-i', '-r', probe.id, '-b', 'add,maximized_vert,maximized_horz']);
      const max2 = await until(() => { const w = E.windows().find(x => x.id === probe.id); return w && w.x + w.w >= SW - 10 && w; }, 10000, 'full width again');
      assert.ok(max2.w >= SW - 20);
    });

    await t.test('US-133 两台机器：在「机器」页配对另一台狐狸OS，聊天里切到它', async () => {
      const hws = path.join(E.root, 'alpha-ws'); fs.mkdirSync(hws);
      const henv = { ...E.env, FOXOS_HOME: path.join(E.root, 'alpha-home') };
      const host = E.bg(PY, ['-m', 'foxos', '--workspace', hws, 'machine', 'serve', '--listen', '127.0.0.1:0', '--name', 'alpha-host'], henv);
      const info = JSON.parse(await new Promise(r => host.stdout.once('data', d => r(String(d).split('\n')[0]))));
      const code = E.cli(['machine', 'host', 'code'], { ws: hws, env: henv });
      await page.click('.nav-item[data-view="machines"]');
      await page.fill('#p-name', 'alpha');
      await page.fill('#p-url', info.url);
      await page.fill('#p-code', code.code);
      await page.fill('#p-fp', code.fingerprint);
      await page.click('#p-go');
      await page.waitForFunction(() => /alpha-host/.test(document.querySelector('#view').textContent), null, { timeout: 30000 });
      const m = E.cli(['machine', 'list']).machines.find(x => x.name === 'alpha');
      assert.equal(m.fingerprint, info.fingerprint);
      E.cli(['machine', 'host', 'grant', '--client', m.client, '--bot', 'coder', '--permissions', 'read', '--apps', 'files'], { ws: hws, env: henv });
      E.cli(['bot', 'config', 'set', 'coder', '--machines', 'local,alpha']);
      await page.reload(); await page.waitForSelector('#bot-list .bot-item');
      await page.click('.bot-item[data-id="coder"]');
      await page.selectOption('#sel-machine', 'alpha');
      await until(() => (E.cli(['bot', 'config', 'get', 'coder']).config.machines || {}).default === 'alpha', 10000, 'default machine');
      await shot(page, 'bots-e2e-machines.png');
      await page.selectOption('#sel-machine', 'local');
      await until(() => (E.cli(['bot', 'config', 'get', 'coder']).config.machines || {}).default === 'local', 10000, 'back to local');
    });

    await t.test('US-134 人工接管：点「人工接管」后智能体的编辑被拦下（记为接管），点「交还」恢复', async () => {
      await page.click('#btn-takeover');
      await until(() => E.cli(['control', 'status']).paused, 10000, 'paused');
      await page.waitForSelector('#acting .chip.bad');
      E.cli(['bot', 'config', 'set', 'coder', '--rule', 'edit=allow']);
      const done = await say('coder', 'Use your edit tool to change the word beta to delta in gui/hello.txt.');
      const reply = await until(done, 300000, 'paused reply');
      assert.equal(fs.readFileSync(path.join(E.ws, 'gui', 'hello.txt'), 'utf8'), 'hello beta\n');
      const blocked = reply.cards.filter(c => c.approval && c.approval.by === 'takeover');
      assert.ok(blocked.length && blocked.every(c => c.approval.decision === 'deny'), JSON.stringify(reply.cards));
      await shot(page, 'bots-e2e-takeover.png');
      await page.click('#btn-takeover');
      await until(() => !E.cli(['control', 'status']).paused, 10000, 'resumed');
    });
  } finally {
    if (browser) await browser.close().catch(() => {});
    E.stop();
  }
});
