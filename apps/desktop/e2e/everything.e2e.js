// US-40 ～ US-49 Everything 应用：51 个应用逐个在真实桌面里打开（不连 puter.com），
// 并做一次“界面与命令等价”检查：同一个操作分别用真实鼠标 / 键盘事件（GUI）和 foxos CLI 执行，两次结束后的界面状态与应用数据必须一致。
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { cli, launch, shot, tmpWorkspace, readAudit, ROOT } = require('./helpers');

const CATALOG = JSON.parse(fs.readFileSync(path.join(ROOT, 'packages/core/foxos/data/everything.json'), 'utf8'));
const OPS = (id) => { try { return JSON.parse(fs.readFileSync(path.join(ROOT, 'packages/core/foxos/data/ops', `${id}.json`), 'utf8')).ops; } catch { return []; } };
const ONLY = (process.env.FOXOS_E2E_APPS || '').split(',').filter(Boolean);
const STORY = { office: 'US-40', collaboration: 'US-41', creative: 'US-42', engineering: 'US-43', productivity: 'US-44', finance: 'US-45', business: 'US-46', developer: 'US-47', games: 'US-48' };
const RESULTS = path.join(ROOT, 'docs', 'test-results', 'everything.json');
const results = {};

const AVOID = /open|import|upload|file|download|export|print|save|share|copy|paste|delete|remove|reset|clear|sign|log ?out|online|invite|connect|record|camera|microphone|fullscreen|theme|skip to/i;
// 选一个主界面上、当前没有被弹窗挡住的操作（人此刻能直接点到的）
async function pickOp(page, app, ops) {
  const ok = ops.filter((o) => o.source === 'ui' && o.ui.view === '主界面' && !/\d/.test(o.ui.name || '') && !AVOID.test(o.ui.name || '') && !AVOID.test(o.resource)
    && ['button', 'link', 'tab', 'checkbox', 'switch', 'textbox', 'menuitem'].includes(o.ui.role));
  const rank = (o) => (o.verb === 'set' && o.ui.role === 'textbox' ? 0 : ['create', 'toggle', 'show', 'activate'].indexOf(o.verb) + 1 || 9);
  for (const o of ok.sort((x, y) => rank(x) - rank(y))) {
    const hit = await inView(page, app, `(() => { const s = window.__foxosBridge.snapshot({ limit: 800 });
      const e = s.elements.find((x) => x.name === ${JSON.stringify(o.ui.name)} && x.role === ${JSON.stringify(o.ui.role)});
      return !!e && !e.disabled && window.__foxosBridge.hittable({ ref: e.ref }); })()`);
    if (hit) return o;
  }
  return null;
}

async function evWindow(page, app) {
  await page.waitForFunction((a) => { const w = FX.windows().find((x) => x.key === `everything:${a}`); return w && w.view; }, app, { timeout: 30000 });
  await page.waitForFunction(async (a) => {
    const w = FX.windows().find((x) => x.key === `everything:${a}`);
    try { return await w.view.executeJavaScript('document.readyState === "complete" && !!window.__foxosBridge'); } catch { return false; }
  }, app, { timeout: 60000, polling: 300 });
  await page.waitForTimeout(1200);
}
const inView = (page, app, js) => page.evaluate(async ({ a, code }) => FX.windows().find((x) => x.key === `everything:${a}`).view.executeJavaScript(code), { a: app, code: js });

async function openFromStart(page, app) {
  await page.evaluate(() => FX.loadEverything(true));
  await page.click('#start');
  await page.click(`[data-ev-launch="${app}"]`);
  await evWindow(page, app);
}

// 界面状态签名：可见控件（角色、名称、值、勾选），去掉含数字的名称（时钟、日期等随时间变化）；加上应用数据（去掉 id / 时间字段）
async function signature(page, app, ws) {
  const snap = await inView(page, app, 'window.__foxosBridge.snapshot({ limit: 800 })');
  const ui = [...new Set(snap.elements.filter((e) => !/\d/.test(`${e.name}${e.value || ''}`)).map((e) => `${e.role}|${e.name}|${e.value ?? ''}|${e.checked ?? ''}`))].sort();
  const kvf = path.join(ws, 'AppData', app, 'kv.json');
  const strip = (v) => (Array.isArray(v) ? v.map(strip) : v && typeof v === 'object'
    ? Object.fromEntries(Object.entries(v).filter(([k]) => !/(^id$|Id$|_id$|time|date|At$|_at$|created|updated|modified|stamp|seed|uuid|epoch|device|nonce|token|session)/i.test(k)).map(([k, x]) => [k, strip(x)]))
    : typeof v === 'string' && /\d{4}-\d\d-\d\d|^[0-9a-f-]{16,}$|^[a-z0-9]{6,}-[a-z0-9]{4,}$/i.test(v) ? '<t>' : typeof v === 'number' && v > 1e11 ? '<t>' : v);
  let kv = null;
  if (fs.existsSync(kvf)) { try { kv = strip(JSON.parse(fs.readFileSync(kvf, 'utf8'))); } catch { kv = 'unreadable'; } }
  return { ui, kv: JSON.stringify(kv) };
}

// GUI：用真实输入事件操作控件（坐标点击、插入文本），与人用鼠标键盘相同
async function guiDo(page, app, op) {
  const name = op.ui.name; const role = op.ui.role;
  const rect = await inView(page, app, `(() => { const s = window.__foxosBridge.snapshot({ limit: 800 });
    const e = s.elements.find((x) => x.name === ${JSON.stringify(name)} && x.role === ${JSON.stringify(role)}) || s.elements.find((x) => x.name.includes(${JSON.stringify(name)}) && x.role === ${JSON.stringify(role)});
    if (!e) return null; const el = document.querySelector('[data-foxos-ref="' + e.ref + '"]'); el.scrollIntoView({ block: 'center', inline: 'center' });
    const r = el.getBoundingClientRect(); return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }; })()`);
  assert.ok(rect, `界面上找不到「${name}」`);
  await page.evaluate(async ({ a, r }) => {
    const v = FX.windows().find((x) => x.key === `everything:${a}`).view;
    v.focus();
    v.sendInputEvent({ type: 'mouseMove', x: r.x, y: r.y });
    v.sendInputEvent({ type: 'mouseDown', x: r.x, y: r.y, button: 'left', clickCount: 1 });
    v.sendInputEvent({ type: 'mouseUp', x: r.x, y: r.y, button: 'left', clickCount: 1 });
  }, { a: app, r: rect });
  await page.waitForTimeout(300);
  if (op.verb === 'set') {
    await page.evaluate(async (a) => FX.windows().find((x) => x.key === `everything:${a}`).view.insertText('foxos parity'), app);
  }
  await page.waitForTimeout(1500);
}

let ctx = null;
test.before(async () => {
  const ws = tmpWorkspace('ev');
  ctx = { ws, ...(await launch(ws)) };
});
test.after(async () => {
  fs.mkdirSync(path.dirname(RESULTS), { recursive: true });
  let prev = {};
  try { prev = JSON.parse(fs.readFileSync(RESULTS, 'utf8')); } catch { /* 首次 */ }
  fs.writeFileSync(RESULTS, `${JSON.stringify({ ...prev, ...results }, null, 1)}\n`);
  if (ctx) await ctx.app.close();
});

for (const a of CATALOG.apps) {
  if (ONLY.length && !ONLY.includes(a.id)) continue;
  test(`${STORY[a.group]} ${a.id}：本地打开，界面操作与 CLI 等价`, async (t) => {
    const { page, ws } = ctx;
    const r = results[a.id] = { app: a.id, group: a.group, boot: null, parity: null, op: null, cli: null, note: null };
    const info = cli(ws, ['everything', 'info', a.id]).result;
    if (!info.installed) {
      r.note = a.upstreamIssue || '未安装';
      t.skip(r.note);
      return;
    }
    cli(ws, [a.id, 'app', 'reset']);
    await openFromStart(page, a.id);
    // 启动检查：页面没有连接 puter.com 的报错，CLI 读到的是同一个窗口里的界面
    const text = await inView(page, a.id, 'document.body.innerText');
    assert.ok(!/Could not reach Puter|puter\.com\/action/i.test(text), `${a.id} 页面提示无法连接 Puter`);
    const st = cli(ws, [a.id, 'app', 'status']).result;
    assert.equal(st.running, true);
    r.boot = 'ok';
    await shot(page, `apps/${a.id}`);
    const op = await pickOp(page, a.id, OPS(a.id));
    if (!op) { r.parity = 'no-op'; r.note = '主界面没有适合做等价检查的操作'; return; }
    r.op = op.id;
    // GUI 路径
    await guiDo(page, a.id, op);
    const s1 = await signature(page, a.id, ws);
    // CLI 路径：同一桌面、同一窗口尺寸，从相同的初始状态出发
    cli(ws, [a.id, 'app', 'reset']);
    await openFromStart(page, a.id);
    const args = [a.id, op.resource, op.verb, ...(op.verb === 'set' ? ['foxos parity'] : [])];
    cli(ws, args, { agent: 'e2e-parity' });
    r.cli = `foxos ${args.join(' ')}`;
    await page.waitForTimeout(1500);
    const s2 = await signature(page, a.id, ws);
    const audit = readAudit(ws).filter((x) => x.agent === 'e2e-parity' && x.command === `${a.id}.${op.resource}.${op.verb}`);
    assert.ok(audit.length >= 1, 'CLI 操作没有写审计');
    const onlyGui = s1.ui.filter((x) => !s2.ui.includes(x)); const onlyCli = s2.ui.filter((x) => !s1.ui.includes(x));
    r.parity = onlyGui.length === 0 && onlyCli.length === 0 && s1.kv === s2.kv ? 'equal' : 'different';
    if (r.parity !== 'equal') fs.writeFileSync(path.join(require('node:os').tmpdir(), `foxos-parity-${a.id}.json`), JSON.stringify({ gui: s1, cli: s2 }, null, 1));
    if (r.parity !== 'equal') r.note = JSON.stringify({ onlyGui: onlyGui.slice(0, 5), onlyCli: onlyCli.slice(0, 5), kvEqual: s1.kv === s2.kv });
    assert.deepEqual(onlyGui, [], `只在 GUI 结果中出现：${onlyGui.slice(0, 5).join('; ')}`);
    assert.deepEqual(onlyCli, [], `只在 CLI 结果中出现：${onlyCli.slice(0, 5).join('; ')}`);
    assert.equal(s1.kv, s2.kv, '应用数据不一致');
    cli(ws, [a.id, 'app', 'close'], { check: false });
  });
}
