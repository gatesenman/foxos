// 从运行中的真实桌面截取 README 截图（xvfb 1600x1000）。
// 用法：DISPLAY=:99 FOXOS_HOME=<含已安装 Everything 应用的目录> FOXOS_SHOT_WS=<工作空间> node scripts/screenshots.js [名称…]
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');
const { _electron } = require('playwright');
const { ROOT, PY, env } = require('../e2e/helpers');

const OUT = path.join(ROOT, 'docs', 'screenshots');
const WS = process.env.FOXOS_SHOT_WS || path.join(os.homedir(), 'FoxOS', 'workspace');
const W = 1600; const H = 1000;
const only = new Set(process.argv.slice(2));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-shots-ud-'));
  fs.writeFileSync(path.join(ud, 'settings.json'), JSON.stringify({ setupDone: true, workspace: WS }));
  fs.writeFileSync(path.join(ud, 'session.json'), JSON.stringify({ bounds: { x: 0, y: 0, width: W, height: H }, windows: [] }));
  const app = await _electron.launch({
    args: ['.', '--no-sandbox', `--user-data-dir=${ud}`, `--workspace=${WS}`],
    cwd: path.join(ROOT, 'apps', 'desktop'),
    env: env({ DISPLAY: process.env.DISPLAY || ':99', FOXOS_PYTHON: PY }),
  });
  const page = await app.firstWindow();
  await page.setViewportSize({ width: W, height: H }).catch(() => {});
  await app.evaluate(({ BrowserWindow }, [w, h]) => { const b = BrowserWindow.getAllWindows()[0]; b.setBounds({ x: 0, y: 0, width: w, height: h }); }, [W, H]);
  await page.waitForSelector('body.ready', { timeout: 60000 });
  const closeAll = () => page.evaluate(() => Promise.all(FX.windows().map((w) => FX.closeWindow(w))));
  const open = (appId, params = {}, geom = null) => page.evaluate(([a, p, g]) => { FX.openWindow(a, p, g); }, [appId, params, geom]);
  const big = { x: 16, y: 12, w: 1180, h: 860 };
  const shots = [];
  async function shot(name, caption, fn) {
    if (only.size && !only.has(name)) return;
    await closeAll();
    await page.evaluate(() => document.getElementById('start-menu').classList.add('hidden'));
    try {
      const file = await fn();
      const f = file || path.join(OUT, `${name}.png`);
      if (!file) await page.screenshot({ path: f });
      shots.push({ name, caption, file: path.relative(ROOT, f) });
      console.log('ok', name);
    } catch (e) { console.log('FAIL', name, e.message.split('\n')[0]); }
  }
  // 整个 X 屏幕（LibreOffice 原生窗口在 Electron 之外）
  const grab = (f) => { execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'x11grab', '-video_size', `${W}x${H}`, '-i', `${process.env.DISPLAY || ':99'}+0,0`, '-frames:v', '1', f]); return f; };

  // 等所有程序图标（<img>）加载完成
  const iconsReady = () => page.waitForFunction(() => [...document.querySelectorAll('img.app-img')].every((i) => i.complete), null, { timeout: 30000 }).then(() => sleep(300));
  await shot('desktop', '桌面：桌面快捷方式、窗口标题栏与任务栏显示各程序自带的图标（LibreOffice、系统终端、Code - OSS、Electron、Everything 上游图标），右侧是智能体会话面板', async () => {
    await open('everything', { app: 'chess' }, { x: 190, y: 20, w: 720, h: 620 });
    await open('everything', { app: 'documents' }, { x: 560, y: 150, w: 640, h: 600 });
    await sleep(4000); await iconsReady();
  });
  await shot('start-menu', '开始菜单：内置程序与按 9 个分组列出的已安装 Everything 应用，每个程序显示其开源项目自带的图标', async () => {
    await page.click('#start'); await sleep(800); await iconsReady();
  });
  await shot('app-center', '应用中心：51 个 Everything 应用（9 个分组）显示各自上游自带的图标；另有内置应用、LibreOffice、开发工具与 ACP 智能体', async () => {
    await open('appcenter', {}, { ...big, w: 1160 });
    await page.waitForSelector('.ev-group[data-group=games]', { timeout: 60000 });
    await page.evaluate(() => document.querySelector('.ev-section').scrollIntoView());
    await sleep(600); await iconsReady();
  });
  await shot('setup-wizard', '首次运行安装向导：检测并在线安装 LibreOffice、Python 办公库、Node.js、git、环境与 Everything 分组', async () => {
    await open('setup', {}, { x: 180, y: 30, w: 900, h: 820 });
    await page.click('[data-action=next]');
    await page.waitForSelector('[data-comp]', { timeout: 60000 }); await sleep(800);
  });
  await shot('terminal', '终端：真实 PTY，foxos 命令可直接读写工作空间里的表格与文档', async () => {
    await open('terminal', {}, big);
    await page.waitForSelector('.xterm', { timeout: 30000 }); await sleep(1500);
    // 截图用中性的提示符（不显示本机主机名）
    await page.keyboard.type("export PS1='\\[\\e[32m\\]user@foxos\\[\\e[0m\\]:\\[\\e[34m\\]\\w\\[\\e[0m\\]$ '; clear\n", { delay: 5 });
    await sleep(800);
    await page.keyboard.type('foxos --version && foxos sheets read 2026年销售.xlsx --range A1:E8 && foxos env list\n', { delay: 5 });
    await sleep(6000);
  });
  await shot('files', '文件管理器：工作空间实时同步（CLI、MCP、智能体的修改立即出现）', async () => {
    await open('files', { path: '' }, big); await sleep(1500);
  });
  await shot('editor', 'Monaco 编辑器：语法高亮、保存到工作空间', async () => {
    await open('editor', { path: 'src/sales_report.py' }, big);
    await page.waitForSelector('.monaco-editor', { timeout: 30000 }); await sleep(1500);
  });
  await shot('browser', '浏览器：内置网页浏览器', async () => {
    await open('browser', { url: 'https://github.com/gatesenman/foxos' }, big); await sleep(7000);
  });
  for (const [id, cap, file, after] of [['spreadsheet', '表格（打开工作空间里的 2026年销售.xlsx）', '2026年销售.xlsx'], ['documents', '文档（打开工作空间里的 项目周报.docx）', '项目周报.docx'],
    ['whiteboard', '白板'], ['crm', '客户管理 CRM', null, 'Skip for now'], ['chess', '国际象棋']]) {
    await shot(`everything-${id}`, `Everything 应用：${cap}，本机构建运行，CLI / MCP 可操作`, async () => {
      await open('everything', file ? { app: id, file } : { app: id }, big);
      await page.waitForSelector('.window webview', { timeout: 30000 }); await sleep(8000);
      if (after) {
        await page.evaluate((t) => { const v = document.querySelector('.window webview'); return v.executeJavaScript(`(() => { const b = [...document.querySelectorAll('button')].find((x) => x.textContent.trim() === ${JSON.stringify(t)}); if (b) b.click(); return !!b; })()`); }, after);
        await sleep(1500);
      }
    });
  }
  await shot('environments-catalog', '环境 → 安装系统：一键安装 WSL2 发行版、LXC / 官方根文件系统、Windows Sandbox、Hyper-V；本机能力检查', async () => {
    await open('environments', {}, big);
    await page.click('[data-act=env-install]');
    await page.waitForSelector('[data-entry="wsl-ubuntu-24.04"]', { timeout: 60000 }); await sleep(800);
  });
  await shot('environments-alpine', '环境：已安装并运行的 Alpine 环境，实时资源、快捷操作、快照与自定义操作', async () => {
    await open('environments', {}, big);
    await page.click('[data-env=alpine]');
    await page.waitForFunction(() => { const v = document.querySelector('[data-stat=processes]'); return v && v.textContent !== '—'; }, null, { timeout: 30000 });
    await sleep(2500);
  });
  await shot('acp-agent-install', 'ACP 智能体一键安装：从 ACP Registry 安装，过程在真实终端中可见', async () => {
    await open('appcenter', {}, { ...big, w: 1160 });
    const sel = '[data-app-id=gemini] [data-action=install-agent]';
    await page.waitForSelector(sel, { timeout: 60000 });
    await page.fill('input[placeholder^="搜索智能体"]', 'Gemini'); await sleep(500);
    // 智能体区在页面最底部：给滚动容器留出底部空白，好让该区滚到窗口顶部
    await page.evaluate((s) => { const sec = document.querySelector(s).closest('section'); let p = sec.parentElement; while (p && p.scrollHeight <= p.clientHeight) p = p.parentElement; if (p) p.style.paddingBottom = '700px'; sec.scrollIntoView({ block: 'start' }); }, sel);
    await page.click(sel);
    await sleep(6000);
  });
  await shot('audit-takeover', '活动与人工接管：所有智能体操作写入审计日志；人工接管后智能体写操作被拒绝（PAUSED）', async () => {
    await page.click('[data-tab=activity]'); await sleep(500);
    await page.click('#takeover'); await sleep(1500);
    spawnSync(PY, ['-m', 'foxos', '--workspace', WS, '--agent', 'claude-code', 'docs', 'append', '项目周报.docx', '尝试写入'], { env: env() });
    await open('files', { path: '' }, { x: 16, y: 12, w: 900, h: 600 });
    await sleep(2500);
  });
  await page.evaluate(() => FX.k(['control', 'resume'])).catch(() => {});
  await page.click('[data-tab=session]').catch(() => {});
  for (const [name, file, cap] of [['libreoffice-writer', '项目周报.docx', 'LibreOffice Writer：打开工作空间里由智能体生成的 .docx'], ['libreoffice-calc', '2026年销售.xlsx', 'LibreOffice Calc：公式与原生图表（由 foxos sheets 命令写入）']]) {
    await shot(name, cap, async () => {
      for (const x of fs.readdirSync(WS)) if (x.startsWith('.~lock.')) fs.rmSync(path.join(WS, x));
      await page.evaluate((f) => FX.openPath(f), file);
      let wid = '';
      for (let i = 0; i < 60 && !wid; i++) {
        await sleep(1000);
        const r = spawnSync('xdotool', ['search', '--name', file.replace(/\..*$/, '')], { encoding: 'utf8' });
        wid = (r.stdout || '').trim().split('\n').filter(Boolean).pop() || '';
      }
      if (!wid) throw new Error('LibreOffice 窗口没有出现');
      await sleep(5000);
      spawnSync('xdotool', ['windowsize', wid, '1180', '860']); spawnSync('xdotool', ['windowmove', wid, '20', '50']); spawnSync('xdotool', ['windowraise', wid]);
      await sleep(3000);
      const f = grab(path.join(OUT, `${name}.png`));
      // 正常退出 LibreOffice（不留锁文件）
      spawnSync('xdotool', ['windowactivate', '--sync', wid]); spawnSync('xdotool', ['key', '--window', wid, 'ctrl+q']);
      for (let i = 0; i < 20 && spawnSync('pgrep', ['-f', 'soffice.bin']).status === 0; i++) await sleep(500);
      spawnSync('pkill', ['-f', 'soffice']);
      for (const x of fs.readdirSync(WS)) if (x.startsWith('.~lock.')) fs.rmSync(path.join(WS, x));
      return f;
    });
  }
  // 与已有清单合并（只重拍部分截图时保留其余条目）
  const idx = path.join(OUT, 'index.json');
  let prev = []; try { prev = JSON.parse(fs.readFileSync(idx, 'utf8')); } catch { /* 首次 */ }
  const merged = [...prev.filter((p) => !shots.find((x) => x.name === p.name)), ...shots];
  fs.writeFileSync(idx, `${JSON.stringify(merged, null, 1)}\n`);
  await Promise.race([app.close(), sleep(10000)]);
  process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
