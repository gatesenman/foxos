'use strict';
// ACP（Agent Client Protocol）客户端：以子进程启动智能体，stdio 上逐行 JSON-RPC 2.0。
// 狐狸OS 作为客户端：提供 fs 读写（经 foxos 内核，受工作空间约束、写锁、人工接管与审计），
// 并在 session/new 中把 foxos MCP 服务器交给智能体。
const { spawn } = require('node:child_process');
const path = require('node:path');
const kernel = require('./kernel');
const settings = require('./settings');
const { corePath } = require('./paths');

const PROTOCOL_VERSION = 1;

class AcpConnection {
  constructor(agent, { onEvent, onPermission }) {
    this.agent = agent; // {id, name, command, args, env}
    this.onEvent = onEvent;
    this.onPermission = onPermission;
    this.nextId = 1;
    this.pending = new Map();
    this.buffer = '';
    this.stderr = '';
    this.sessions = new Set();
    this.closed = false;
  }

  get identity() { return `acp:${this.agent.id}`; }

  start() {
    const env = { ...process.env, ...settings.secretEnv(), ...(this.agent.env || {}), FOXOS_WORKSPACE: kernel.getWorkspace() };
    this.proc = spawn(this.agent.command, this.agent.args || [], { cwd: kernel.getWorkspace(), env, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
    this.proc.stdout.on('data', (d) => this._onData(String(d)));
    this.proc.stderr.on('data', (d) => {
      this.stderr = (this.stderr + String(d)).slice(-20000);
      this.onEvent({ type: 'stderr', text: String(d) });
    });
    this.proc.on('error', (e) => this._close(`无法启动：${e.message}`));
    this.proc.on('exit', (code, sig) => this._close(`智能体进程已退出（${sig || code}）`));
  }

  _close(reason) {
    if (this.closed) return;
    this.closed = true;
    for (const { reject } of this.pending.values()) reject(new Error(reason));
    this.pending.clear();
    this.onEvent({ type: 'closed', reason });
  }

  _send(msg) {
    if (this.closed) throw new Error('连接已关闭');
    this.proc.stdin.write(`${JSON.stringify(msg)}\n`);
  }

  request(method, params, timeoutMs = 120000) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`${method} 超时`)); }, timeoutMs);
      this.pending.set(id, {
        resolve: (v) => { clearTimeout(timer); resolve(v); },
        reject: (e) => { clearTimeout(timer); reject(e); },
      });
      this._send({ jsonrpc: '2.0', id, method, params });
    });
  }

  notify(method, params) { this._send({ jsonrpc: '2.0', method, params }); }

  _onData(chunk) {
    this.buffer += chunk;
    let i;
    while ((i = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, i).trim();
      this.buffer = this.buffer.slice(i + 1);
      if (!line) continue;
      let msg;
      try { msg = JSON.parse(line); } catch { this.onEvent({ type: 'stdout', text: line }); continue; }
      this._dispatch(msg);
    }
  }

  async _dispatch(msg) {
    if (msg.id != null && (msg.result !== undefined || msg.error !== undefined) && !msg.method) {
      const p = this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      if (msg.error) {
        const e = new Error(msg.error.message || 'ACP 错误');
        e.code = msg.error.code;
        e.data = msg.error.data;
        p.reject(e);
      } else p.resolve(msg.result);
      return;
    }
    if (msg.method === 'session/update') {
      this.onEvent({ type: 'update', sessionId: msg.params?.sessionId, update: msg.params?.update });
      return;
    }
    if (msg.method && msg.id != null) {
      try {
        const result = await this._handleRequest(msg.method, msg.params || {});
        this._send({ jsonrpc: '2.0', id: msg.id, result });
      } catch (e) {
        this._send({ jsonrpc: '2.0', id: msg.id, error: { code: e.rpcCode || -32603, message: String(e.message || e) } });
      }
    }
  }

  async _handleRequest(method, params) {
    if (method === 'session/request_permission') {
      this.onEvent({ type: 'permission', params });
      const optionId = await this.onPermission(params);
      return optionId ? { outcome: { outcome: 'selected', optionId } } : { outcome: { outcome: 'cancelled' } };
    }
    if (method === 'fs/read_text_file') {
      const rel = this._rel(params.path);
      const r = await kernel.run(['files', 'read', rel], { agent: this.identity });
      if (!r.ok) throw Object.assign(new Error(r.data?.error?.message || r.stderr), { rpcCode: -32002 });
      let content = r.data.result.content;
      if (params.line || params.limit) {
        const lines = content.split('\n');
        const start = Math.max(0, (params.line || 1) - 1);
        content = lines.slice(start, params.limit ? start + params.limit : undefined).join('\n');
      }
      this.onEvent({ type: 'fs', op: 'read', path: rel });
      return { content };
    }
    if (method === 'fs/write_text_file') {
      const rel = this._rel(params.path);
      const r = await kernel.run(['files', 'write', rel, '--content-stdin'], { agent: this.identity, stdin: params.content ?? '' });
      if (!r.ok) throw Object.assign(new Error(r.data?.error?.message || r.stderr), { rpcCode: -32003 });
      this.onEvent({ type: 'fs', op: 'write', path: rel });
      return null;
    }
    throw Object.assign(new Error(`客户端不支持：${method}`), { rpcCode: -32601 });
  }

  _rel(p) {
    const abs = path.resolve(kernel.getWorkspace(), String(p || ''));
    return path.relative(kernel.getWorkspace(), abs) || '.';
  }

  async initialize() {
    this.init = await this.request('initialize', {
      protocolVersion: PROTOCOL_VERSION,
      clientCapabilities: { fs: { readTextFile: true, writeTextFile: true }, terminal: false },
      clientInfo: { name: 'foxos', title: '狐狸OS', version: require('../../package.json').version },
    }, 60000);
    return this.init;
  }

  mcpServers() {
    return [{
      name: 'foxos',
      command: kernel.pythonPath(),
      args: ['-m', 'foxos', 'mcp', '--workspace', kernel.getWorkspace()],
      env: [
        { name: 'PYTHONPATH', value: corePath() },
        { name: 'FOXOS_AGENT', value: this.identity },
        { name: 'PYTHONIOENCODING', value: 'utf-8' },
      ],
    }];
  }

  async newSession() {
    const r = await this.request('session/new', { cwd: kernel.getWorkspace(), mcpServers: this.mcpServers() }, 120000);
    this.sessions.add(r.sessionId);
    return r;
  }

  authenticate(methodId) { return this.request('authenticate', { methodId }, 300000); }

  prompt(sessionId, text) {
    return this.request('session/prompt', { sessionId, prompt: [{ type: 'text', text }] }, 30 * 60 * 1000);
  }

  cancel(sessionId) { try { this.notify('session/cancel', { sessionId }); } catch { /* 已关闭 */ } }

  stop() {
    if (this.proc && !this.closed) { try { this.proc.kill(); } catch { /* 已退出 */ } }
  }
}

module.exports = { AcpConnection, PROTOCOL_VERSION };
