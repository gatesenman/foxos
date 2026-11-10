// 端到端测试辅助：用 Playwright 驱动真实的 Electron 桌面（xvfb 下运行），不替换任何被测组件
'use strict';
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { execFileSync, spawnSync } = require('node:child_process');
const { _electron } = require('playwright');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const PY = process.env.FOXOS_PYTHON || path.join(ROOT, '.venv', 'bin', 'python');
const SHOTS = process.env.FOXOS_SHOTS || path.join(ROOT, 'docs', 'screenshots', 'e2e');

function tmpWorkspace(tag) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `foxos-e2e-${tag}-`));
}

function env(extra = {}) {
  return { ...process.env, PYTHONPATH: path.join(ROOT, 'packages', 'core'), ...extra };
}

// 调用真实 CLI，返回解析后的 JSON
function cli(ws, args, { agent = 'e2e-cli', extraEnv = {}, check = true } = {}) {
  const p = spawnSync(PY, ['-m', 'foxos', '--workspace', ws, '--agent', agent, ...args, '--json'], { env: env(extraEnv), encoding: 'utf8', timeout: 600000 });
  let data = null;
  try { data = JSON.parse(p.stdout); } catch { /* 非 JSON */ }
  if (check && p.status !== 0) throw new Error(`foxos ${args.join(' ')} 退出码 ${p.status}\n${p.stdout}\n${p.stderr}`);
  return data;
}

async function launch(ws, { extraEnv = {}, userData } = {}) {
  const ud = userData || fs.mkdtempSync(path.join(os.tmpdir(), 'foxos-e2e-ud-'));
  // 预先标记安装向导已完成，避免首次运行向导挡住测试（向导本身由独立用例覆盖）
  fs.writeFileSync(path.join(ud, 'settings.json'), JSON.stringify({ setupDone: true, workspace: ws }));
  const app = await _electron.launch({
    args: ['.', '--no-sandbox', `--user-data-dir=${ud}`, `--workspace=${ws}`],
    cwd: path.join(ROOT, 'apps', 'desktop'),
    env: env({ DISPLAY: process.env.DISPLAY || ':99', FOXOS_PYTHON: PY, ...extraEnv }),
  });
  const page = await app.firstWindow();
  await page.waitForSelector('body.ready', { timeout: 60000 });
  await page.evaluate(() => FX.windows().forEach((w) => FX.closeWindow(w)));
  return { app, page, ud };
}

async function shot(page, name) {
  fs.mkdirSync(SHOTS, { recursive: true });
  const f = path.join(SHOTS, `${name}.png`);
  await page.screenshot({ path: f });
  return f;
}

function readAudit(ws) {
  const f = path.join(ws, '.foxos', 'audit.jsonl');
  if (!fs.existsSync(f)) return [];
  return fs.readFileSync(f, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l));
}

module.exports = { ROOT, PY, cli, launch, shot, tmpWorkspace, readAudit, env, execFileSync };
