// US-87 客户端模式：桌面程序只是“狐狸OS 电脑”的客户端。所有动作（终端、应用中心安装、打开 Word、文件、智能体、聊天）
// 都在来宾里执行；本机执行默认关闭。来宾 = 真实的狐狸OS 根文件系统（scripts/e2e/foxos-guest-chroot.sh：sshd + Xvfb :0 上的 XFCE + foxos）。
// 运行：FOXOS_E2E_GUEST_PORT=2222 FOXOS_E2E_GUEST_KEY=…/id FOXOS_E2E_GUEST_ROOT=…/chroot node --test e2e/client.e2e.js
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { _electron } = require('playwright');
const { ROOT, PY, shot, tmpWorkspace, env } = require('./helpers');

const PORT = process.env.FOXOS_E2E_GUEST_PORT;
const KEY = process.env.FOXOS_E2E_GUEST_KEY;
const GROOT = process.env.FOXOS_E2E_GUEST_ROOT;           // 来宾根目录（只用来从外面核对来宾里的文件）
const INSTALL = process.env.FOXOS_E2E_GUEST_APT === '1';  // 真的在来宾里 apt 安装 LibreOffice Writer（需要联网，较慢）
const skip = !(PORT && KEY && GROOT) && '需要 FOXOS_E2E_GUEST_PORT / FOXOS_E2E_GUEST_KEY / FOXOS_E2E_GUEST_ROOT（见 scripts/e2e/foxos-guest-chroot.sh）';

async function launchClient(ws, guest) {
  const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-e2e-client-'));
  fs.writeFileSync(path.join(ud, 'settings.json'), JSON.stringify({ setupDone: true, workspace: ws, guest }));
  const app = await _electron.launch({
    args: ['.', '--no-sandbox', `--user-data-dir=${ud}`, `--workspace=${ws}`],
    cwd: path.join(ROOT, 'apps', 'desktop'),
    env: env({ DISPLAY: process.env.DISPLAY || ':99', FOXOS_PYTHON: PY, FOXOS_CLIENT_MODE: '1' }),
    timeout: 600000,                                     // 共享构建机负载很高时 Electron 启动可能要几分钟
  });
  const page = await app.firstWindow({ timeout: 600000 });
  await page.waitForSelector('body.ready', { timeout: 180000 });
  return { app, page, ud };
}

const termText = (page, title) => page.evaluate((t) => { const w = FX.windows().find((x) => x.appId === 'terminal' && x.title().includes(t)); return w ? w.screenText() : ''; }, title);

test('US-87 客户端模式：所有动作都在狐狸OS 电脑里执行，本机执行默认关闭', { skip, timeout: 40 * 60 * 1000 }, async () => {
  const ws = tmpWorkspace('client');
  const guestWs = path.join(GROOT, 'home', 'foxos', 'FoxOS', 'workspace');
  const { app, page } = await launchClient(ws, { kind: 'ssh', host: '127.0.0.1', port: Number(PORT), user: 'foxos', key: KEY, label: 'e2e-guest' });
  try {
    const env0 = await page.evaluate(() => FX.env);
    assert.equal(env0.mode, 'client');
    assert.equal(env0.hostExecution, false);

    // 1. 狐狸OS 电脑窗口自动打开：在线，画面（来宾 x11vnc 经 ssh -W）连上
    await page.waitForSelector('.window[data-app=computer] [data-guest-status=ok]', { timeout: 300000 });
    await page.waitForFunction(() => document.querySelector('[data-guest-view]')?.dataset.connected === '1', null, { timeout: 120000 });
    assert.equal(await page.getAttribute('[data-guest-view]', 'data-via'), 'ssh');
    await page.waitForTimeout(2000);
    await shot(page, 'US-87-computer-view');

    // 2. 内核命令（文件）写进来宾的工作空间，不写本机工作空间
    const name = `client-e2e-${process.pid}.txt`;
    await page.evaluate((n) => FX.k(['files', 'write', n, '--content', 'from the FoxOS computer']), name);
    assert.equal(fs.readFileSync(path.join(guestWs, name), 'utf8'), 'from the FoxOS computer');
    assert.ok(!fs.existsSync(path.join(ws, name)), '本机工作空间不应出现这个文件');

    // 3. 终端是来宾的 shell
    await page.evaluate(() => FX.openWindow('terminal', {}));
    await page.waitForFunction(() => FX.windows().some((w) => w.appId === 'terminal' && w.ptyId), null, { timeout: 30000 });
    await page.evaluate(() => { const w = FX.windows().find((x) => x.appId === 'terminal'); window.foxos.pty.write(w.ptyId, 'grep ^ID= /etc/os-release; whoami\r'); });
    await page.waitForFunction(() => FX.windows().find((x) => x.appId === 'terminal').screenText().includes('ID=foxos'), null, { timeout: 30000 });

    // 4. 应用中心“安装”（Everything 应用）：在来宾终端里运行 foxos everything …，不是本机 PowerShell
    const code = await page.evaluate(() => FX.runFoxosInTerminal('guest-everything', ['everything', 'info', 'circuits']));
    assert.equal(code, 0);
    assert.match(await termText(page, 'guest-everything'), /Circuits|circuits/);

    // 5. 本机执行默认关闭：直接要求在本机跑命令会被拒绝，命令没有执行
    const marker = path.join(os.tmpdir(), `foxos-host-exec-${process.pid}`);
    const err = await page.evaluate((m) => window.foxos.pty.spawn({ command: '/bin/sh', args: ['-c', `touch ${m}`] }).then(() => null, (e) => e.message), marker);
    assert.ok(err && /本机执行已关闭|running on this PC is off/.test(err), err);
    await page.waitForTimeout(500);
    assert.ok(!fs.existsSync(marker), '本机命令不应执行');

    // 6. 智能体：列表与会话都在来宾里（foxos acp stdio 经 SSH）
    const installed = await page.evaluate(() => window.foxos.agents.installed());
    assert.ok(installed.some((a) => a.id === 'foxos-local' && a.remote), JSON.stringify(installed));
    const conn = await page.evaluate(() => window.foxos.acp.start('foxos-local', {}));
    assert.equal(conn.init.agentInfo.name, 'foxos-local');
    const sess = await page.evaluate((id) => window.foxos.acp.newSession(id), conn.connId);
    assert.ok(sess.sessionId);
    await page.evaluate((id) => window.foxos.acp.stop(id), conn.connId);

    // 7. 智能体聊天：foxos bot serve 跑在来宾里，经 SSH 端口转发
    const bots = await page.evaluate(() => window.foxos.bots.url());
    assert.match(bots.url, /^http:\/\/127\.0\.0\.1:\d+\/\?t=/);
    assert.equal(await fetch(bots.url).then((r) => r.status), 200);

    // 8. 打开 Word：在来宾桌面上启动 LibreOffice Writer（可选：先在来宾里 apt 安装）
    if (INSTALL) {
      const c = await page.evaluate(() => new Promise((resolve) => FX.openWindow('terminal', { title: 'guest-apt', guestArgv: ['sh', '-c', 'sudo apt-get update -q && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "$@"', 'apt', 'libreoffice-writer'], onExit: resolve })));
      assert.equal(c, 0, await termText(page, 'guest-apt'));
    }
    const apps = await page.evaluate(() => { FX.apps = null; return FX.detectApps(true); });
    const writer = apps.office.find((o) => o.id === 'writer');
    assert.equal(writer.guest, true);
    if (writer.installed) {
      const rec = await page.evaluate(() => window.foxos.office.launch('writer', null));
      assert.ok(rec.guest);
      // 来宾桌面上出现 Writer 窗口（来宾里的 foxos desktop windows）
      const deadline = Date.now() + 180000; let seen = '';
      while (Date.now() < deadline) {
        const r = await page.evaluate(() => window.foxos.run(['desktop', 'windows'], {}));
        seen = JSON.stringify(r.data && r.data.result);
        if (/LibreOffice|Writer|无标题|Untitled/.test(seen)) break;
        await page.waitForTimeout(3000);
      }
      assert.match(seen, /LibreOffice|Writer|无标题|Untitled/);
      await page.evaluate(() => FX.openWindow('computer', {}));
      await page.waitForTimeout(4000);
      await shot(page, 'US-87-writer-in-guest');
    } else {
      const err2 = await page.evaluate(() => window.foxos.office.launch('writer', null).then(() => null, (e) => e.message));
      assert.ok(err2, '来宾里没有 LibreOffice 时应报错（来自来宾，不会在本机打开）');
    }
  } finally {
    await app.close();
  }
});
