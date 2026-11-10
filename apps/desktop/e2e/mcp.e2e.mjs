// US-10 / US-11：用官方 MCP SDK（@modelcontextprotocol/sdk）作为真实客户端连接 foxos mcp：
// 列出工具，并对每个应用（内置应用、环境、每个已安装的 Everything 应用）至少调用一个工具。
import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

const require = createRequire(import.meta.url);
const { ROOT, PY, cli, readAudit } = require('./helpers.js');
const SDK_VERSION = JSON.parse(fs.readFileSync(path.join(ROOT, 'apps/desktop/node_modules/@modelcontextprotocol/sdk/package.json'), 'utf8')).version;
const RESULTS = path.join(ROOT, 'docs', 'test-results', 'mcp.json');
const env = { ...process.env, PYTHONPATH: path.join(ROOT, 'packages', 'core'), PYTHONIOENCODING: 'utf-8' };

function parse(r) { return r.structuredContent || JSON.parse(r.content[0].text); }

// 每个应用选一个调用：优先无必填参数的只读工具
const PREFERRED = { files: ['files_list', {}], sheets: ['sheets_create', { path: 'mcp.xlsx' }], docs: ['docs_create', { path: 'mcp.docx' }], slides: ['slides_create', { path: 'mcp.pptx' }],
  env: ['env_list', {}], everything: ['everything_list', {}], audit: ['audit_tail', {}], control: ['control_status', {}] };

test('US-10 官方 MCP SDK 通过 stdio 列出工具并逐个应用调用', async () => {
  const ws = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-mcp-'));
  const transport = new StdioClientTransport({ command: PY, args: ['-m', 'foxos', '--workspace', ws, 'mcp', '--profile', 'full'], env: { ...env, FOXOS_AGENT: 'mcp-sdk-e2e' }, stderr: 'pipe' });
  const client = new Client({ name: 'foxos-e2e', version: '1.0.0' });
  await client.connect(transport);
  const info = client.getServerVersion();
  assert.equal(info.name, 'foxos');
  const { tools } = await client.listTools();
  assert.ok(tools.length > 100, `工具太少：${tools.length}`);
  const byApp = new Map();
  for (const t of tools) { const app = t._meta['foxos/id'].split('.')[0]; if (!byApp.has(app)) byApp.set(app, []); byApp.get(app).push(t); }
  const installed = new Set(cli(ws, ['everything', 'list', '--installed']).result.apps.map((a) => a.id));
  const ev = new Set(cli(ws, ['everything', 'list']).result.apps.map((a) => a.id));
  const calls = [];
  for (const [app, ts] of byApp) {
    let name; let args;
    if (PREFERRED[app]) [name, args] = PREFERRED[app];
    else if (ev.has(app)) { name = `${app}_app_status`; args = {}; }
    else {
      const t = ts.find((x) => x.annotations.readOnlyHint && !(x.inputSchema.required || []).length) || ts.find((x) => !(x.inputSchema.required || []).length);
      if (!t) { calls.push({ app, tool: null, ok: null, note: '没有无参数的工具' }); continue; }
      name = t.name; args = {};
    }
    const r = await client.callTool({ name, arguments: args });
    const p = parse(r);
    calls.push({ app, tool: name, ok: p.ok, error: p.ok ? null : p.error.code });
    assert.equal(p.ok, true, `${name} 失败：${JSON.stringify(p.error)}`);
    if (ev.has(app)) assert.equal(p.result.installed, installed.has(app));
  }
  // 一个真实的写操作：在 Everything 的 Tasks 里加任务（应用界面实时更新，数据写入工作空间）
  if (installed.has('tasks')) {
    await client.callTool({ name: 'tasks_app_reset', arguments: {} });
    const r = parse(await client.callTool({ name: 'tasks_add-task_set', arguments: { value: '从 MCP 添加', submit: true } }));
    assert.equal(r.ok, true, JSON.stringify(r.error));
    const store = parse(await client.callTool({ name: 'tasks_module_read', arguments: { target: 'src/lib/store.js#store.tasks' } }));
    assert.ok(JSON.stringify(store.result).includes('从 MCP 添加'));
    calls.push({ app: 'tasks', tool: 'tasks_add-task_set', ok: true, note: '写操作，store 中可读到新任务' });
  }
  // 错误码通过 isError + structuredContent 返回
  const bad = await client.callTool({ name: 'files_read', arguments: { path: '../etc/passwd' } });
  assert.equal(bad.isError, true);
  assert.equal(parse(bad).error.code, 'PERMISSION_DENIED');
  const audit = readAudit(ws).filter((a) => a.agent === 'mcp-sdk-e2e');
  assert.ok(audit.some((a) => a.interface === 'mcp'));
  await client.close();
  const out = { sdk: SDK_VERSION, transport: 'stdio', tools: tools.length, apps: byApp.size, calls };
  fs.mkdirSync(path.dirname(RESULTS), { recursive: true });
  let prev = {}; try { prev = JSON.parse(fs.readFileSync(RESULTS, 'utf8')); } catch { /* 首次 */ }
  fs.writeFileSync(RESULTS, `${JSON.stringify({ ...prev, stdio: out }, null, 1)}\n`);
});

test('US-11 官方 MCP SDK 通过 Streamable HTTP 连接（令牌认证、compact 工具集、everything_run）', async () => {
  const ws = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-mcph-'));
  const token = 'e2e-' + Math.random().toString(36).slice(2);
  const srv = spawn(PY, ['-m', 'foxos', '--workspace', ws, '--agent', 'mcp-http-e2e', 'mcp', '--http', '127.0.0.1:0'], { env: { ...env, FOXOS_MCP_TOKEN: token }, stdio: ['ignore', 'pipe', 'pipe'] });
  const url = await new Promise((resolve, reject) => {
    let b = ''; srv.stdout.on('data', (d) => { b += d; try { resolve(JSON.parse(b.split('\n')[0]).url); } catch { /* 等完整一行 */ } });
    srv.on('exit', (c) => reject(new Error(`服务器退出 ${c}`)));
  });
  try {
    // 没有令牌：401
    const unauth = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'ping' }) });
    assert.equal(unauth.status, 401);
    const transport = new StreamableHTTPClientTransport(new URL(url), { requestInit: { headers: { Authorization: `Bearer ${token}` } } });
    const client = new Client({ name: 'foxos-e2e-http', version: '1.0.0' });
    await client.connect(transport);
    const { tools } = await client.listTools();
    const names = new Set(tools.map((t) => t.name));
    for (const n of ['everything_run', 'everything_commands', 'env_list', 'files_write']) assert.ok(names.has(n), `缺少 ${n}`);
    assert.ok(![...names].some((n) => n.startsWith('tasks_')), 'compact 模式不应直接列出 Everything 应用的工具');
    const w = parse(await client.callTool({ name: 'files_write', arguments: { path: 'hello.md', content: '# 来自 HTTP MCP\n' } }));
    assert.equal(w.ok, true);
    assert.equal(fs.readFileSync(path.join(ws, 'hello.md'), 'utf8'), '# 来自 HTTP MCP\n');
    const c = parse(await client.callTool({ name: 'everything_commands', arguments: { app: 'chess' } }));
    assert.equal(c.ok, true);
    assert.ok(c.result.commands.some((x) => x.command === 'ui snapshot'));
    await client.close();
    let prev = {}; try { prev = JSON.parse(fs.readFileSync(RESULTS, 'utf8')); } catch { /* 首次 */ }
    fs.writeFileSync(RESULTS, `${JSON.stringify({ ...prev, http: { sdk: SDK_VERSION, transport: 'streamable-http', tools: tools.length } }, null, 1)}\n`);
  } finally { srv.kill(); }
});
