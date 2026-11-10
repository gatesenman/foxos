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

  // envName：在狐狸OS 环境里运行智能体（Linux 后端）。智能体目录只读挂载在环境的 /opt/foxos/agents，
  // 工作空间在 /workspace；MCP 改用宿主上的 Streamable HTTP 服务器（环境需共享宿主网络）。
  async start(envName = null) {
    const extra = { ...settings.secretEnv(), ...(this.agent.env || {}), FOXOS_WORKSPACE: kernel.getWorkspace(), FOXOS_AGENT: this.identity };
    if (!envName) {
      this.proc = spawn(this.agent.command, this.agent.args || [], { cwd: kernel.getWorkspace(), env: { ...process.env, ...extra }, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
    } else if (envName === '@sandbox' || envName === '@sandbox-offline') {
      // 轻量隔离：智能体直接运行在宿主上，但只能读写工作空间（foxos.sandbox：Landlock + seccomp / Seatbelt / 受限令牌 + 作业对象）。
      // foxos MCP 运行在沙箱外（宿主 Streamable HTTP），这样 Everything 应用与桌面控制仍然可用；不联网时只放行到该端口的 TCP 连接。
      const offline = envName === '@sandbox-offline';
      await this._startHttpMcp();
      const port = String(new URL(this.mcpHttp.url).port);
      const args = ['-m', 'foxos.sandbox', 'wrap', '--workspace', kernel.getWorkspace(), '--profile', this.agent.id, '--network', offline ? 'off' : 'on',
        '--connect-port', port, '--read', require('./agents').agentsDir()];
      for (const [k, v] of Object.entries(extra)) args.push('--env', `${k}=${v}`);
      args.push('--', this.agent.command, ...(this.agent.args || []));
      this.sandbox = { network: !offline };
      this.proc = spawn(kernel.pythonPath(), args, { cwd: kernel.getWorkspace(), env: { ...process.env, PYTHONPATH: corePath() }, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
    } else {
      const info = await kernel.run(['env', 'info', envName]);
      if (!info.ok) throw new Error(info.data?.error?.message || `环境 ${envName} 不可用`);
      const e = info.data.result;
      if (e.state !== 'running') throw new Error(`环境 ${envName} 没有运行，先启动它`);
      if (e.backend !== 'linux-ns') throw new Error(`在环境中运行智能体目前只支持 Linux 后端（当前 ${e.backend}）`);
      const agentsRoot = require('./agents').agentsDir();
      const map = (p) => (typeof p === 'string' && p.startsWith(agentsRoot) ? `/opt/foxos/agents${p.slice(agentsRoot.length)}` : p);
      const args = ['-m', 'foxos.envs.linux', 'exec', e.path, '--cwd', e.workspace.mode === 'none' ? '/' : '/workspace'];
      for (const [k, v] of Object.entries({ ...extra, FOXOS_WORKSPACE: '/workspace' })) args.push('--env', `${k}=${v}`);
      args.push('--', map(this.agent.command), ...(this.agent.args || []).map(map));
      this.envName = envName; this.envNetwork = e.network;
      this.proc = spawn(kernel.pythonPath(), args, { cwd: kernel.getWorkspace(), env: { ...process.env, PYTHONPATH: corePath() }, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
      if (e.network === 'host') await this._startHttpMcp();
    }
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
    let s = String(p || '');
    // 环境里的智能体看到的工作空间是 /workspace
    if (this.envName && (s === '/workspace' || s.startsWith('/workspace/'))) s = s.slice('/workspace'.length).replace(/^\//, '') || '.';
    const abs = path.resolve(kernel.getWorkspace(), s);
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

  // 宿主上的 Streamable HTTP MCP 服务器（只监听 127.0.0.1，随机端口 + 随机令牌），供环境里的智能体连接
  _startHttpMcp() {
    return new Promise((resolve, reject) => {
      const token = require('node:crypto').randomBytes(24).toString('hex');
      const p = spawn(kernel.pythonPath(), ['-m', 'foxos', '--workspace', kernel.getWorkspace(), '--agent', this.identity, 'mcp', '--http', '127.0.0.1:0'],
        { env: { ...process.env, PYTHONPATH: corePath(), FOXOS_MCP_TOKEN: token, PYTHONIOENCODING: 'utf-8' }, stdio: ['ignore', 'pipe', 'pipe'] });
      this.mcpProc = p;
      let buf = '';
      const t = setTimeout(() => reject(new Error('MCP HTTP 服务器启动超时')), 15000);
      p.stdout.on('data', (d) => {
        buf += String(d);
        const line = buf.split('\n')[0];
        try { const j = JSON.parse(line); clearTimeout(t); this.mcpHttp = { url: j.url, token }; resolve(this.mcpHttp); } catch { /* 等待完整一行 */ }
      });
      p.on('exit', (c) => { clearTimeout(t); if (!this.mcpHttp) reject(new Error(`MCP HTTP 服务器退出（${c}）`)); });
    });
  }

  mcpServers() {
    if (this.sandbox) {
      const caps = (this.init && this.init.agentCapabilities && this.init.agentCapabilities.mcpCapabilities) || {};
      if (caps.http) return [{ type: 'http', name: 'foxos', url: this.mcpHttp.url, headers: [{ name: 'Authorization', value: `Bearer ${this.mcpHttp.token}` }] }];
      // 不支持 HTTP MCP 的智能体：stdio MCP 跟智能体一起运行在沙箱里（文件与办公命令可用；不联网时 Everything 应用与桌面控制不可用）
    }
    if (this.envName) {
      const caps = (this.init && this.init.agentCapabilities && this.init.agentCapabilities.mcpCapabilities) || {};
      if (!this.mcpHttp || !caps.http) {
        this.onEvent({ type: 'stderr', text: `[狐狸OS] 环境 ${this.envName} 中的智能体${!this.mcpHttp ? '（环境无网络）' : '不支持 HTTP MCP'}，未注入 foxos MCP；可在环境里直接运行 foxos 命令以外的工具。\n` });
        return [];
      }
      return [{ type: 'http', name: 'foxos', url: this.mcpHttp.url, headers: [{ name: 'Authorization', value: `Bearer ${this.mcpHttp.token}` }] }];
    }
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
    const r = await this.request('session/new', { cwd: this.envName ? '/workspace' : kernel.getWorkspace(), mcpServers: this.mcpServers() }, 120000);
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
    if (this.mcpProc) { try { this.mcpProc.kill(); } catch { /* 已退出 */ } }
  }
}

module.exports = { AcpConnection, PROTOCOL_VERSION };
