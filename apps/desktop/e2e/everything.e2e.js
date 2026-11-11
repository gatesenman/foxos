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
// 操作本身就带随机性的数据键（如数独“新游戏”随机生成题目），比较时去掉
const RANDOM = { sudoku: /^(puzzle|solution|values)$/ };
// 已确认的上游缺陷：测试照常运行并记录结果，但标为 TODO（不计为失败）
const KNOWN = {
  'photo-studio': '上游缺陷：src/app/pointer.ts 中 #viewport 的 pointerdown 处理只排除 button / input / .canvas-ui，开始页的“Describe an edit”文本框（textarea）被鼠标点击时焦点被抢到画布，用鼠标无法输入；CLI 的 set 不经过指针事件，所以结果不同',
};
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
  // 生成的 ID（如下拉框的值 mwaudfhd-cbltjm：Date.now().toString(36) + '-' + 6 位随机 base36）每次重置都不同，归一化后再比较。
  // 必须先归一化、再按“含数字”过滤：这种 ID 有时含数字有时不含（随机），先过滤的话同一个控件在一次结果里被丢掉、
  // 在另一次里留下成 <id>，这就是 US-44 tasks 偶发“只在 CLI 结果中出现：combobox|List|<id>|”的原因。
  const norm = (v) => (typeof v === 'string' && /^[0-9a-f-]{16,}$|^[a-z0-9]{6,}-[a-z0-9]{4,}$/i.test(v) ? '<id>' : v);
  const ui = [...new Set(snap.elements.map((e) => ({ ...e, value: norm(e.value) })).filter((e) => !/\d/.test(`${e.name}${e.value || ''}`))
    .map((e) => `${e.role}|${e.name}|${e.value ?? ''}|${e.checked ?? ''}`))].sort();
  const kvf = path.join(ws, 'AppData', app, 'kv.json');
  const rnd = RANDOM[app];
  const strip = (v) => (Array.isArray(v) ? v.map(strip) : v && typeof v === 'object'
    ? Object.fromEntries(Object.entries(v).filter(([k]) => !/(^id$|Id$|_id$|^ts$|time|date|At$|_at$|created|updated|modified|stamp|seed|uuid|epoch|device|nonce|token|session)/i.test(k) && !(rnd && rnd.test(k))).map(([k, x]) => [k.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '<id>'), strip(x)]))
    : typeof v === 'string' && /^\s*[{[]/.test(v) && (() => { try { JSON.parse(v); return true; } catch { return false; } })() ? strip(JSON.parse(v))
    : typeof v === 'string' && (/\d{4}-\d\d-\d\d|^[0-9a-f-]{16,}$|^[a-z0-9]{6,}-[a-z0-9]{4,}$/i.test(v) || /^(?=.*\d)(?=.*[a-z])[a-z0-9]{10,16}$/.test(v)) ? '<t>' : typeof v === 'number' && v > 1e11 ? '<t>' : v);
  let kv = null;
  if (fs.existsSync(kvf)) { try { kv = strip(JSON.parse(fs.readFileSync(kvf, 'utf8'))); } catch { kv = 'unreadable'; } }
  return { ui, kv: JSON.stringify(kv) };
}

// GUI：用真实输入事件操作控件（坐标点击、插入文本），与人用鼠标键盘相同
async function guiDo(page, app, op) {
  const name = op.ui.name; const role = op.ui.role;
  const locate = (scroll) => inView(page, app, `(() => { const s = window.__foxosBridge.snapshot({ limit: 800 });
    const e = s.elements.find((x) => x.name === ${JSON.stringify(name)} && x.role === ${JSON.stringify(role)}) || s.elements.find((x) => x.name.includes(${JSON.stringify(name)}) && x.role === ${JSON.stringify(role)});
    if (!e) return null; const el = document.querySelector('[data-foxos-ref="' + e.ref + '"]');
    if (${scroll}) el.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
    const r = el.getBoundingClientRect(); const numeric = el.type === 'number' || el.inputMode === 'numeric' || el.getAttribute('role') === 'spinbutton' || /page number/i.test(${JSON.stringify(name)});
    return { ref: e.ref, numeric, x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) }; })()`);
  // 先滚动到可见，等页面（含平滑滚动、布局变化）稳定后再取坐标点击；输入框要确认真的拿到了焦点
  for (let attempt = 0; attempt < 3; attempt++) {
    const found = await locate(true);
    assert.ok(found, `界面上找不到「${name}」`);
    // 数字输入框用一个合法的数字，其他输入框用固定文本；CLI 路径用同一个值
    op.value = found.numeric ? '2' : 'foxos parity';
    await page.waitForTimeout(400);
    const rect = await locate(false);
    await page.evaluate(async ({ a, r }) => {
      const v = FX.windows().find((x) => x.key === `everything:${a}`).view;
      v.focus();
      v.sendInputEvent({ type: 'mouseMove', x: r.x, y: r.y });
      v.sendInputEvent({ type: 'mouseDown', x: r.x, y: r.y, button: 'left', clickCount: 1 });
      v.sendInputEvent({ type: 'mouseUp', x: r.x, y: r.y, button: 'left', clickCount: 1 });
    }, { a: app, r: rect });
    await page.waitForTimeout(300);
    if (op.verb !== 'set') break;
    const focused = await inView(page, app, `(() => { const a = document.activeElement; return !!a && a.dataset && a.dataset.foxosRef === ${JSON.stringify(rect.ref)}; })()`);
    if (focused) break;
  }
  if (op.verb === 'set') {
    // 人设置一个输入框的值：点进去、全选（Ctrl+A）、输入；CLI 的 set 同样是替换整个值
    await page.evaluate(async ({ a, val }) => {
      const v = FX.windows().find((x) => x.key === `everything:${a}`).view;
      v.sendInputEvent({ type: 'keyDown', keyCode: 'A', modifiers: ['control'] });
      v.sendInputEvent({ type: 'keyUp', keyCode: 'A', modifiers: ['control'] });
      await new Promise((r) => setTimeout(r, 100));
      await v.insertText(val);
    }, { a: app, val: op.value });
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
    if (KNOWN[a.id]) { t.todo(KNOWN[a.id]); r.known = KNOWN[a.id]; }
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
    const args = [a.id, op.resource, op.verb, ...(op.verb === 'set' ? [op.value || 'foxos parity'] : [])];
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
