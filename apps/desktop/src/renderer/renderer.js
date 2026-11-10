// 狐狸OS 桌面界面（渲染进程）。只通过 window.foxos.run() 调用统一命令内核。
'use strict';

const $ = (sel, root = document) => root.querySelector(sel);
const el = (tag, attrs = {}, ...children) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c != null) n.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return n;
};
const SVG = 'http://www.w3.org/2000/svg';
const svg = (tag, attrs = {}) => {
  const n = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};

const state = { env: null, audit: [], terminal: [], paused: false, fileFilter: '', files: [] };
const windows = new Map();
let zTop = 10;

function fox(args, opts) {
  return window.foxos.run(args, opts);
}

// ---------------------------------------------------------------- windows
function openWindow(id, title, geom, render) {
  let w = windows.get(id);
  if (!w) {
    const node = $('#window-tpl').content.firstElementChild.cloneNode(true);
    $('.win-name', node).textContent = title;
    Object.assign(node.style, { left: `${geom.x}px`, top: `${geom.y}px`, width: `${geom.w}px`, height: `${geom.h}px` });
    $('.win-close', node).addEventListener('click', () => { node.remove(); windows.delete(id); });
    node.addEventListener('mousedown', () => focus(node));
    dragBy($('.win-title', node), node);
    $('#desktop').append(node);
    w = { node, body: $('.win-body', node), render };
    windows.set(id, w);
  }
  focus(w.node);
  return Promise.resolve(render(w.body)).then(() => w);
}

function focus(node) {
  document.querySelectorAll('.window.focused').forEach((n) => n.classList.remove('focused'));
  node.classList.add('focused');
  node.style.zIndex = String(++zTop);
}

function dragBy(handle, node) {
  handle.addEventListener('mousedown', (e) => {
    if (e.target.closest('button')) return;
    const sx = e.clientX; const sy = e.clientY;
    const ox = node.offsetLeft; const oy = node.offsetTop;
    const move = (ev) => { node.style.left = `${ox + ev.clientX - sx}px`; node.style.top = `${Math.max(0, oy + ev.clientY - sy)}px`; };
    const up = () => { removeEventListener('mousemove', move); removeEventListener('mouseup', up); };
    addEventListener('mousemove', move); addEventListener('mouseup', up);
  });
}

async function refreshOpenWindows() {
  for (const w of windows.values()) await w.render(w.body);
}

// ---------------------------------------------------------------- helpers
function colName(n) { let s = ''; while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); } return s; }
function colIndex(letters) { return letters.split('').reduce((a, c) => a * 26 + (c.charCodeAt(0) - 64), 0); }
function parseRef(ref) {
  // 'Sales'!$B$2:$B$7 → {c1, r1, c2, r2}
  const m = /([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?$/.exec(String(ref || '').replace(/\$/g, ''));
  if (!m) return null;
  const c1 = colIndex(m[1]); const r1 = Number(m[2]);
  return { c1, r1, c2: m[3] ? colIndex(m[3]) : c1, r2: m[4] ? Number(m[4]) : r1 };
}
function pick(grid, ref) {
  const r = parseRef(ref); if (!r) return [];
  const out = [];
  for (let row = r.r1; row <= r.r2; row++) for (let c = r.c1; c <= r.c2; c++) out.push(grid[row - 1]?.[c - 1]);
  return out;
}
function fmtTime(ts) { return ts ? ts.slice(11, 19) : ''; }
function avatarFor(name) {
  const n = name.toLowerCase();
  if (n.startsWith('human')) return '👤';
  if (n.includes('super') || n.includes('lead')) return '🧭';
  if (n.includes('data')) return '📊';
  if (n.includes('doc')) return '📝';
  if (n.includes('slide') || n.includes('deck')) return '🎞';
  if (n.includes('review')) return '🔍';
  if (n.startsWith('mcp')) return '🔌';
  return '🤖';
}
function badge(status) { return el('span', { class: `badge ${status}`, text: status }); }

// ---------------------------------------------------------------- chart preview (SVG)
function chartSvg(chart, grid) {
  const W = 420; const H = 150; const P = 24;
  const s = svg('svg', { width: '100%', viewBox: `0 0 ${W} ${H}` });
  const series = chart.series.map((sr) => pick(grid, sr.values).map(Number).map((v) => (Number.isFinite(v) ? v : 0)));
  const cats = chart.series[0]?.categories ? pick(grid, chart.series[0].categories) : [];
  const colors = ['#ff7a2f', '#37d6e6', '#3ccf91', '#ffc24b', '#b48cff'];
  const n = Math.max(0, ...series.map((x) => x.length));
  if (!n) return s;
  if (chart.type === 'pie') {
    const vals = series[0]; const total = vals.reduce((a, b) => a + b, 0) || 1;
    let a0 = -Math.PI / 2; const cx = 90; const cy = H / 2; const r = 70;
    vals.forEach((v, i) => {
      const a1 = a0 + (v / total) * Math.PI * 2;
      const large = a1 - a0 > Math.PI ? 1 : 0;
      s.append(svg('path', { d: `M${cx},${cy} L${cx + r * Math.cos(a0)},${cy + r * Math.sin(a0)} A${r},${r} 0 ${large} 1 ${cx + r * Math.cos(a1)},${cy + r * Math.sin(a1)} Z`, fill: colors[i % colors.length] }));
      const t = svg('text', { x: 180, y: 20 + i * 16 }); t.textContent = `${cats[i] ?? i + 1}: ${v}`; s.append(t);
      a0 = a1;
    });
    return s;
  }
  const max = Math.max(1, ...series.flat());
  const iw = W - P * 2; const ih = H - P * 2; const step = iw / n;
  s.append(svg('line', { x1: P, y1: H - P, x2: W - P, y2: H - P, stroke: '#2a3450' }));
  series.forEach((vals, si) => {
    if (chart.type === 'line') {
      const pts = vals.map((v, i) => `${P + step * (i + 0.5)},${H - P - (v / max) * ih}`).join(' ');
      s.append(svg('polyline', { points: pts, fill: 'none', stroke: colors[si % colors.length], 'stroke-width': 2 }));
    } else {
      const bw = (step * 0.7) / series.length;
      vals.forEach((v, i) => {
        const h = (v / max) * ih;
        s.append(svg('rect', { x: P + step * i + step * 0.15 + bw * si, y: H - P - h, width: bw, height: h, rx: 2, fill: colors[si % colors.length] }));
      });
    }
  });
  cats.forEach((c, i) => { const t = svg('text', { x: P + step * (i + 0.5), y: H - 10, 'text-anchor': 'middle' }); t.textContent = c ?? ''; s.append(t); });
  return s;
}

// ---------------------------------------------------------------- window renderers
function renderSheet(file) {
  return async (body) => {
    const r = await fox(['sheets', 'read', file, '--computed']);
    const r2 = r.ok ? r : await fox(['sheets', 'read', file]);
    body.replaceChildren();
    if (!r2.ok) { body.append(el('div', { class: 'muted', text: r2.data?.error?.message || r2.stderr })); return; }
    const res = r2.data.result;
    const values = res.values || res.rows;
    body.append(el('div', { class: 'sheet-meta', text: `${res.file} · 工作表 ${res.sheet} · ${res.range}${res.computed_by ? ' · 公式已由 LibreOffice 求值' : ''}` }));
    const table = el('table', { class: 'grid' });
    const cols = values[0]?.length || 0;
    table.append(el('tr', {}, el('th', { text: '' }), Array.from({ length: cols }, (_, i) => el('th', { text: colName(i + 1) }))));
    values.forEach((row, ri) => {
      table.append(el('tr', {}, el('th', { text: String(ri + 1) }), row.map((v, ci) => {
        const formula = res.rows[ri][ci];
        const isF = typeof formula === 'string' && formula.startsWith('=');
        const shown = typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(2)) : (v ?? '');
        const td = el('td', { class: `${isF ? 'f ' : ''}${typeof v === 'number' ? 'num' : ''}`, text: String(shown) });
        if (isF) td.title = formula;
        return td;
      })));
    });
    body.append(table);
    for (const c of res.charts) {
      body.append(el('div', { class: 'chart-box' }, el('div', { class: 'muted', text: `图表 #${c.index} · ${c.type} · ${c.title || '未命名'} · 锚点 ${c.anchor}` }), chartSvg(c, values)));
    }
  };
}

async function renderFiles(body) {
  const r = await fox(['files', 'list']);
  body.replaceChildren();
  if (!r.ok) { body.append(el('div', { class: 'muted', text: r.data?.error?.message || r.stderr })); return; }
  const ul = el('ul', { class: 'list' });
  state.files = r.data.result.files;
  const files = state.files.filter((f) => !state.fileFilter || f.path.toLowerCase().includes(state.fileFilter));
  for (const f of files) {
    const isXlsx = /\.xlsx$/i.test(f.path);
    ul.append(el('li', { class: isXlsx ? 'clickable' : '', onclick: () => isXlsx && openSheet(f.path) },
      el('span', { class: 'mono', text: `${isXlsx ? '📊' : /\.pdf$/i.test(f.path) ? '📕' : '📄'} ${f.path}` }),
      el('span', { class: 'muted', text: `${(f.bytes / 1024).toFixed(1)} KB` })));
  }
  if (!files.length) ul.append(el('li', { class: 'muted', text: state.fileFilter ? '没有匹配的文件' : '工作空间为空' }));
  body.append(ul);
}

function renderTerminal(body) {
  body.replaceChildren();
  const term = el('div', { class: 'terminal' });
  for (const item of state.terminal) {
    term.append(el('div', {}, el('span', { class: 'prompt', text: '$ ' }), item.cmd));
    term.append(el('div', { class: item.ok ? '' : 'err', text: item.out }));
  }
  if (!state.terminal.length) term.append(el('div', { class: 'muted', text: '在底部输入栏输入 foxos 命令，例如：foxos sheets read reports/sales.xlsx' }));
  body.append(term);
  body.scrollTop = body.scrollHeight;
}

async function renderTasks(body) {
  const r = await fox(['tasks', 'list']);
  body.replaceChildren();
  const ul = el('ul', { class: 'list' });
  for (const t of (r.data?.result?.tasks || []).slice().reverse()) {
    ul.append(el('li', {}, el('span', {}, el('span', { class: 'mono muted', text: `${t.id} ` }), t.goal), badge(t.status)));
  }
  if (!ul.children.length) ul.append(el('li', { class: 'muted', text: '暂无任务' }));
  body.append(el('div', { class: 'sheet-meta', text: '阶段 0：任务只入队记录，尚未接入模型自动执行。' }), ul);
}

function renderApps(body) {
  const apps = [
    ['📊', '表格 Spreadsheet', '已接入：create / read / write / chart create / chart list / export（openpyxl + LibreOffice）', 'ok'],
    ['📝', '文档 Documents', '未接入（阶段 1）', 'na'],
    ['🎞', '演示 Presentation', '未接入（阶段 2）', 'na'],
    ['⌨', '终端 · git · Python · Node', '使用宿主系统已安装的版本', 'ok'],
  ];
  body.replaceChildren(...apps.map(([g, n, d, s]) => el('div', { class: 'app-card' }, el('span', { class: 'glyph', text: g }),
    el('div', { class: 'info' }, el('div', { text: n }), el('div', { class: 'muted', text: d })), badge(s === 'ok' ? 'ok' : 'na'))));
}

function agentSummary() {
  const by = new Map();
  for (const e of state.audit) {
    const a = by.get(e.agent) || { name: e.agent, count: 0, last: null, errors: 0 };
    a.count++; a.last = e; if (e.status !== 'ok') a.errors++;
    by.set(e.agent, a);
  }
  return [...by.values()].sort((x, y) => (y.last.ts > x.last.ts ? 1 : -1));
}

function renderAgentsWin(body) {
  const ul = el('ul', { class: 'list' });
  for (const a of agentSummary()) {
    ul.append(el('li', {}, el('span', { text: `${avatarFor(a.name)} ${a.name}` }), el('span', { class: 'muted', text: `${a.count} 次操作 · ${a.errors} 次失败/拒绝` })));
  }
  body.replaceChildren(el('div', { class: 'sheet-meta', text: '智能体身份来自 --agent / FOXOS_AGENT / MCP 客户端名，统计自审计日志。' }), ul);
}

function renderActivityWin(body) {
  const table = el('table', { class: 'grid' }, el('tr', {}, ['时间', '智能体', '接口', '命令', '目标', '状态'].map((h) => el('th', { text: h }))));
  for (const e of state.audit.slice().reverse()) {
    table.append(el('tr', {}, el('td', { class: 'mono', text: fmtTime(e.ts) }), el('td', { text: e.agent }), el('td', { text: e.interface || '' }),
      el('td', { class: 'mono', text: e.command }), el('td', { class: 'mono', text: (e.targets || []).map((t) => t.path).join(', ') }),
      el('td', {}, badge(e.status))));
  }
  body.replaceChildren(table);
}

// ---------------------------------------------------------------- right panel
function renderRightPanel() {
  const now = Date.now();
  const agents = $('#agents');
  agents.replaceChildren();
  for (const a of agentSummary().slice(0, 7)) {
    const active = now - Date.parse(a.last.ts) < 60_000;
    agents.append(el('li', {}, el('span', { class: 'avatar', text: avatarFor(a.name) }),
      el('div', {}, el('div', { class: 'name', text: a.name }), el('div', { class: 'sub', text: `${a.last.command} · ${fmtTime(a.last.ts)}` })),
      el('span', { class: `dot ${active ? 'active' : ''}`, title: active ? '最近 1 分钟内有操作' : '空闲' })));
  }
  if (!agents.children.length) agents.append(el('li', { class: 'muted', text: '还没有智能体操作' }));

  const list = $('#activity');
  list.replaceChildren();
  for (const e of state.audit.slice(-40).reverse()) {
    const tgt = (e.targets || []).map((t) => t.path).join(', ');
    list.append(el('li', {},
      el('div', { class: 'row1' }, el('span', {}, el('span', { class: 'who', text: e.agent }), ' ', el('span', { class: 'cmd', text: e.command })), badge(e.status)),
      el('div', { class: 'meta', text: `${fmtTime(e.ts)} · ${e.interface || ''}${tgt ? ` · ${tgt}` : ''}${e.error ? ` · ${e.error.code}` : ''}` })));
  }
  $('#audit-count').textContent = `（共 ${state.audit.length} 条）`;
}

async function loadAudit() {
  const r = await fox(['audit', 'tail', '-n', '200']);
  if (r.ok) state.audit = r.data.result.entries;
  renderRightPanel();
}

async function loadControl() {
  const r = await fox(['control', 'status']);
  state.paused = Boolean(r.data?.result?.paused);
  const b = $('#takeover');
  b.textContent = state.paused ? '▶ 恢复智能体' : '✋ 人工接管';
  b.title = state.paused ? '智能体写操作已暂停，点击恢复' : '暂停所有智能体的写操作，由人接管';
}

// ---------------------------------------------------------------- commands & tasks
function shellSplit(s) {
  const out = []; let cur = ''; let q = null; let has = false;
  for (const ch of s) {
    if (q) { if (ch === q) q = null; else cur += ch; continue; }
    if (ch === '"' || ch === "'") { q = ch; has = true; continue; }
    if (/\s/.test(ch)) { if (cur || has) { out.push(cur); cur = ''; has = false; } continue; }
    cur += ch;
  }
  if (cur || has) out.push(cur);
  return out;
}

async function runCommandLine(line) {
  // 终端里显示与命令行完全一致的人类可读输出（不加 --json）
  const argv = shellSplit(line).slice(1);
  const r = await fox(argv, { json: false });
  state.terminal.push({ cmd: line, ok: r.ok, out: (r.stdout + (r.stderr ? r.stderr : '')).trimEnd() + (r.ok ? '' : `\n(exit ${r.exitCode})`) });
  await OPENERS.terminal();
}

async function submitTask(text) {
  if (/^foxos(\s|$)/.test(text)) return runCommandLine(text);
  await fox(['tasks', 'create', text]);
  return openWindow('tasks', '任务中心', { x: 680, y: 380, w: 460, h: 260 }, renderTasks);
}

function openSheet(file) {
  return openWindow(`sheet:${file}`, `表格 · ${file}`, { x: 470, y: 16, w: 470, h: 740 }, renderSheet(file));
}

const OPENERS = {
  apps: () => openWindow('apps', '应用中心', { x: 130, y: 60, w: 420, h: 300 }, renderApps),
  tasks: () => openWindow('tasks', '任务中心', { x: 680, y: 380, w: 460, h: 260 }, renderTasks),
  agents: () => openWindow('agents', '智能体中心', { x: 160, y: 90, w: 420, h: 280 }, renderAgentsWin),
  files: () => openWindow('files', '文件中心', { x: 112, y: 16, w: 345, h: 220 }, renderFiles),
  terminal: () => openWindow('terminal', '命令终端', { x: 112, y: 250, w: 345, h: 506 }, renderTerminal),
  activity: () => openWindow('activity', '活动记录', { x: 140, y: 60, w: 720, h: 420 }, renderActivityWin),
};

// ---------------------------------------------------------------- boot
async function boot() {
  state.env = await window.foxos.env();
  $('#ws-path').textContent = state.env.workspace;
  $('#versions').textContent = `Electron ${state.env.versions.electron} · ${state.env.platform}\n身份 ${state.env.agent}`;

  const icons = [['📁', '文件中心', 'files'], ['📊', '表格', null], ['⌨', '终端', 'terminal'], ['📋', '任务', 'tasks'], ['📝', '文档', 'off'], ['🎞', '演示', 'off']];
  for (const [g, label, key] of icons) {
    $('#desktop-icons').append(el('button', {
      class: `dicon ${key === 'off' ? 'off' : ''}`,
      title: key === 'off' ? '未接入（规划中）' : label,
      onclick: async () => {
        if (key === 'off') return;
        if (key) return OPENERS[key]();
        const f = await fox(['files', 'list']);
        const first = f.data?.result?.files?.find((x) => /\.xlsx$/i.test(x.path));
        if (first) openSheet(first.path); else OPENERS.files();
      },
    }, el('span', { class: 'glyph', text: g }), el('span', { class: 'label', text: label })));
  }
  $('#nav').addEventListener('click', (e) => { const b = e.target.closest('[data-open]'); if (b) OPENERS[b.dataset.open](); });
  $('#takeover').addEventListener('click', async () => { await fox(['control', state.paused ? 'resume' : 'pause']); await loadControl(); });
  $('#task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = $('#task-input'); const text = input.value.trim();
    if (!text) return;
    input.value = '';
    await submitTask(text);
  });
  $('#search').addEventListener('input', async (e) => {
    state.fileFilter = e.target.value.trim().toLowerCase();
    await OPENERS.files();
  });

  window.foxos.onAuditChanged(async () => { await loadAudit(); });

  // 初始桌面：文件中心 + 第一个表格 + 命令终端
  await loadAudit();
  await loadControl();
  await OPENERS.files();
  const first = state.files.find((x) => /\.xlsx$/i.test(x.path));
  if (first) {
    await openSheet(first.path);
    await runCommandLine(`foxos sheets read ${first.path} --range A13:D14 --computed`);
    await runCommandLine(`foxos files list`);
  } else {
    await OPENERS.terminal();
  }
  await loadAudit();
  window.foxos.ready();
}

boot().catch((err) => { window.foxos.log(`启动失败：${err && err.stack}`); window.foxos.ready(); });
