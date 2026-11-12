// 智能体窗口的文档截图（zh-CN）：主对话（流式回复 + 工具卡片）、审批卡片、智能体设置、停靠侧栏、空状态。
// 真实的 foxos bot serve + Chrome 应用模式窗口 + 本地 ACP 智能体（foxos-local，不需要模型），自己的 Xvfb + xfwm4 桌面。
// 用法：node apps/desktop/scripts/bots-ui-shots.mjs <标签>   → docs/screenshots/bots-ui-<名字>-<标签>.png
//      加 --dark 另存一组深色主题（-dark-<标签>）。
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', '..');
const PY = process.env.FOXOS_PYTHON || path.join(ROOT, '.venv', 'bin', 'python');
const TAG = process.argv[2] || 'after';
const DARK = process.argv.includes('--dark');
const OUT = path.join(ROOT, 'docs', 'screenshots');
const SW = 1600, SH = 1000;
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function until(fn, ms = 60000, what = 'condition') {
  const t0 = Date.now(); let last;
  while (Date.now() - t0 < ms) { try { last = await fn(); if (last) return last; } catch (e) { last = e; } await sleep(250); }
  throw new Error(`timed out: ${what}: ${last instanceof Error ? last.message : JSON.stringify(last)}`);
}
const freePort = () => new Promise(r => { const s = net.createServer(); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => r(p)); }); });

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-bots-shots-'));
const ws = path.join(root, 'ws'); fs.mkdirSync(ws);
let n = 140; while (fs.existsSync(`/tmp/.X${n}-lock`)) n++;
const env = { ...process.env, PYTHONPATH: path.join(ROOT, 'packages', 'core'), DISPLAY: ':' + n, FOXOS_HOME: path.join(root, 'home'),
  XDG_DATA_HOME: path.join(root, 'data'), XDG_STATE_HOME: path.join(root, 'state'), XDG_CONFIG_HOME: path.join(root, 'config'),
  FOXOS_BOTS_BROWSER: 'google-chrome', FOXOS_PLACE: 'foxos', FOXOS_LANG: 'zh-CN', LANG: 'zh_CN.UTF-8' };
delete env.FOXOS_AGENT; delete env.FOXOS_WORKSPACE;
const procs = [];
const bg = (cmd, args) => { const p = spawn(cmd, args, { env, stdio: 'ignore' }); procs.push(p); return p; };
const cli = (...args) => JSON.parse(execFileSync(PY, ['-m', 'foxos', '--workspace', ws, '--agent', 'human', '--json', ...args], { env, encoding: 'utf8' })).result;
const name = s => path.join(OUT, `bots-ui-${s}-${DARK ? 'dark-' : ''}${TAG}.png`);

let browser;
try {
  bg('Xvfb', [env.DISPLAY, '-screen', '0', `${SW}x${SH}x24`, '-nolisten', 'tcp']);
  await until(() => spawnSync('xdpyinfo', [], { env }).status === 0, 30000, 'Xvfb');
  bg('xfwm4', ['--replace', '--compositor=off']);
  await until(() => spawnSync('wmctrl', ['-m'], { env }).status === 0, 60000, 'xfwm4');

  fs.writeFileSync(path.join(ws, 'README.md'), '# 狐狸OS\n\n智能体在狐狸OS 虚拟电脑里工作。\n\n- 文件\n- 终端\n- 审批\n');
  fs.mkdirSync(path.join(ws, 'notes'));
  cli('bot', 'profile', 'create', '编码助手', '--id', 'coder', '--title', '写代码、改文件', '--acp-agent', 'foxos-local');
  cli('bot', 'profile', 'create', '研究员', '--id', 'research', '--title', '查资料、写摘要', '--acp-agent', 'foxos-local');
  cli('bot', 'profile', 'create', '新助手', '--id', 'fresh', '--title', '还没有对话', '--acp-agent', 'foxos-local');

  const cdp = await freePort();
  env.FOXOS_BOTS_BROWSER_ARGS = `--remote-debugging-port=${cdp} --disable-gpu --password-store=basic --lang=zh-CN${DARK ? ' --force-dark-mode' : ''}`;
  execFileSync(PY, ['-m', 'foxos.botchat.launch', '--workspace', ws, '--undock'], { env, encoding: 'utf8' });
  browser = await until(() => chromium.connectOverCDP(`http://127.0.0.1:${cdp}`).catch(() => null), 30000, 'CDP');
  const page = await until(() => browser.contexts().flatMap(c => c.pages()).find(p => p.url().startsWith('http://127.0.0.1')), 30000, 'page');
  if (DARK) { await page.emulateMedia({ colorScheme: 'dark' }); await page.reload(); }
  await page.waitForSelector('#bot-list .bot-item');
  const win = await until(() => execFileSync('wmctrl', ['-lx'], { env, encoding: 'utf8' }).split('\n').find(l => /foxos-bots/i.test(l)), 20000, 'window');
  const wid = win.split(/\s+/)[0];
  execFileSync('wmctrl', ['-i', '-r', wid, '-e', '0,40,30,1280,860'], { env });
  await sleep(1200);
  const shot = async s => { await sleep(600); await page.screenshot({ path: name(s) }); console.log(name(s)); };

  // 1. 空状态：还没有对话的智能体
  await page.click('.bot-item[data-id="fresh"]');
  await page.waitForSelector('#input');
  await shot('empty');

  // 2. 主对话：先完成一轮（用户消息带代码块、完成的终端卡片），再发一轮仍在进行（流式文字 + 运行中的工具卡片）
  await page.click('.bot-item[data-id="fox"]');
  await page.waitForSelector('#input');
  const send = async text => { await page.fill('#input', text); await page.click('#btn-send'); };
  await send('读取 README.md\n运行 printf "构建完成\\n共 3 个文件\\n"');
  await until(() => cli('bot', 'message', 'list', 'fox').messages.filter(m => m.role === 'bot').length >= 1, 60000, 'first turn');
  await send('先读一下说明，再跑一遍测试：\n```sh\nnpm test -- --watch=false\n```\n读取 README.md\n运行 echo 开始测试; sleep 25');
  await page.waitForFunction(() => /README\.md 有/.test(document.querySelector('#messages').textContent) && document.querySelectorAll('#messages .card').length >= 4, null, { timeout: 60000 });
  await sleep(1500);
  await shot('chat');
  await page.click('#btn-stop').catch(() => {});
  await until(() => !cli('bot', 'message', 'list', 'fox').messages.at(-1) || cli('bot', 'message', 'list', 'fox').messages.filter(m => m.role === 'bot').length >= 2, 60000, 'stopped');

  // 3. 审批卡片：写文件前请求批准（diff）
  await page.click('.bot-item[data-id="coder"]');
  await page.waitForSelector('#input');
  await send('写入 notes/todo.md：# 待办\\n- 给狐狸OS 写说明\\n- 跑一遍端到端测试');
  await page.waitForSelector('#messages [data-approve]', { timeout: 60000 });
  await shot('approval');
  const a = cli('bot', 'approval', 'list').approvals.find(x => x.bot === 'coder');
  if (a) cli('bot', 'approval', 'answer', a.id, '--option', 'allow');
  await until(() => cli('bot', 'message', 'list', 'coder').messages.some(m => m.role === 'bot'), 60000, 'approval turn');

  // 4. 智能体设置
  await page.click('.bot-item[data-id="fox"]');
  await page.click('#btn-settings');
  await page.waitForSelector('#f-kind');
  await shot('settings');

  // 5. 停靠侧栏：占住屏幕右边，旁边是最大化的窗口
  await page.click('.bot-item[data-id="fox"]');
  await page.waitForSelector('#input');
  bg('xclock', ['-title', 'probe', '-bg', '#d9d4ca']);
  const probe = await until(() => execFileSync('wmctrl', ['-l'], { env, encoding: 'utf8' }).split('\n').find(l => / probe$/.test(l)), 30000, 'probe');
  await page.click('#btn-dock');
  await until(() => page.evaluate(() => innerWidth < 760), 30000, 'docked');
  execFileSync('wmctrl', ['-i', '-r', probe.split(/\s+/)[0], '-b', 'add,maximized_vert,maximized_horz'], { env });
  await sleep(1500);
  await shot('docked');
  spawnSync('scrot', ['-o', name('docked-desktop')], { env });
  console.log(name('docked-desktop'));
  await page.click('#btn-side').catch(() => {});
  await page.click('#btn-dock').catch(() => {});
} finally {
  if (browser) await browser.close().catch(() => {});
  for (const p of procs.reverse()) { try { p.kill('SIGTERM'); } catch {} }
  spawnSync('pkill', ['-f', root]);
  fs.rmSync(root, { recursive: true, force: true });
}
