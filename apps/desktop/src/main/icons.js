// 程序图标：每个程序用它自己的开源项目自带的图标（foxicon:// 协议）。
//   foxicon://everything/<应用>   本机安装的上游组件里的 icon.png（AGPL 应用只在运行时读取），其次是随仓库分发的 MIT 应用图标
//   foxicon://libreoffice/<writer|calc|impress>   本机安装的 LibreOffice 自带图标
//   foxicon://builtin/terminal|editor|browser    系统终端 / 本机 VS Code / Electron 图标
// 找不到时返回 404，界面退回字体图标并记录（icons:report）。
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { app, net, nativeImage } = require('electron');

const TP = path.join(__dirname, '..', 'third-party-icons');
const SIZES = ['256x256', '128x128', '96x96', '64x64', '48x48'];
const exists = (p) => { try { return fs.statSync(p).isFile(); } catch { return false; } };

function foxosHome() { return require('./everything').foxosHome(); }

// Linux 图标主题里按名称找 PNG（hicolor / Adwaita / pixmaps）
function themeIcon(names, roots = ['/usr/share/icons', path.join(os.homedir(), '.local/share/icons')]) {
  for (const root of roots) {
    for (const theme of ['hicolor', 'Adwaita']) {
      for (const s of SIZES) {
        const dir = path.join(root, theme, s, 'apps');
        let files = [];
        try { files = fs.readdirSync(dir); } catch { continue; }
        for (const n of names) {
          const re = n instanceof RegExp ? n : new RegExp(`^${n.replace(/[.]/g, '\\.')}\\.png$`);
          const f = files.find((x) => re.test(x));
          if (f) return path.join(dir, f);
        }
      }
    }
  }
  for (const n of names) {
    if (n instanceof RegExp) continue;
    const p = path.join('/usr/share/pixmaps', `${n}.png`);
    if (exists(p)) return p;
  }
  return null;
}

function everythingIcon(id) {
  if (!/^[a-z0-9-]+$/.test(id)) return null;
  const dir = path.join(foxosHome(), 'everything', id);
  for (const p of [path.join(dir, 'icon.png'), path.join(dir, 'dist', 'icon-128.png'), path.join(dir, 'dist', 'icon-192.png')]) if (exists(p)) return { file: p, source: 'installed' };
  const v = path.join(TP, 'everything', `${id}.png`);
  if (exists(v)) return { file: v, source: 'bundled-mit' };
  return null;
}

function sofficeDir() {
  try { const p = require('./apps').findSoffice(); return p ? path.dirname(fs.realpathSync(p)) : null; } catch { return null; }
}

// 返回 { file } 或 { exe }（Windows / macOS 用系统 API 从程序文件里取图标）
function resolve(kind, id) {
  if (kind === 'everything') return everythingIcon(id);
  if (kind === 'libreoffice') {
    if (!['writer', 'calc', 'impress'].includes(id)) return null;
    if (process.platform === 'linux') {
      const f = themeIcon([new RegExp(`^libreoffice[0-9.]*-${id}\\.png$`)], ['/usr/share/icons', '/opt', ...fs.existsSync('/opt') ? fs.readdirSync('/opt').filter((d) => /libreoffice/i.test(d)).map((d) => path.join('/opt', d, 'share', 'icons')) : []]);
      return f ? { file: f, source: 'libreoffice' } : null;
    }
    const d = sofficeDir();
    if (process.platform === 'win32' && d) {
      const exe = path.join(d, { writer: 'swriter.exe', calc: 'scalc.exe', impress: 'simpress.exe' }[id]);
      return exists(exe) ? { exe, source: 'libreoffice' } : null;
    }
    if (process.platform === 'darwin' && fs.existsSync('/Applications/LibreOffice.app')) return { exe: '/Applications/LibreOffice.app', source: 'libreoffice' };
    return null;
  }
  if (kind === 'builtin') {
    if (id === 'browser') return { file: path.join(TP, 'electron.png'), source: 'electron' };
    if (id === 'terminal') {
      if (process.platform === 'linux') {
        const f = themeIcon(['org.gnome.Terminal', 'org.gnome.Console', 'utilities-terminal', 'org.xfce.terminal', 'org.kde.konsole', 'konsole', 'xterm-color', 'xterm']);
        return f ? { file: f, source: 'system-terminal' } : null;
      }
      if (process.platform === 'win32') {
        const wt = path.join(process.env.LOCALAPPDATA || '', 'Microsoft', 'WindowsApps', 'wt.exe');
        return { exe: exists(wt) ? wt : path.join(process.env.SystemRoot || 'C:\\Windows', 'System32', 'cmd.exe'), source: 'system-terminal' };
      }
      return { exe: '/System/Applications/Utilities/Terminal.app', source: 'system-terminal' };
    }
    if (id === 'editor') {
      // 编辑器是 Monaco（VS Code 的编辑器核心）；monaco-editor 包没有自带图标，用本机安装的 VS Code 的图标
      if (process.platform === 'linux') {
        const f = themeIcon(['vscode', 'code', 'com.visualstudio.code', 'visual-studio-code', 'vscodium', 'codium']);
        if (f) return { file: f, source: 'vscode' };
      }
      if (process.platform === 'win32') {
        for (const p of [path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Microsoft VS Code', 'Code.exe'), path.join(process.env.ProgramFiles || '', 'Microsoft VS Code', 'Code.exe')]) if (exists(p)) return { exe: p, source: 'vscode' };
      }
      if (process.platform === 'darwin' && fs.existsSync('/Applications/Visual Studio Code.app')) return { exe: '/Applications/Visual Studio Code.app', source: 'vscode' };
      // 没装 VS Code：用 Monaco 所属开源项目 Code - OSS（microsoft/vscode，MIT）自带的图标
      return { file: path.join(TP, 'code-oss.png'), source: 'code-oss' };
    }
  }
  return null;
}

async function respond(req) {
  const u = new URL(req.url);
  const r = resolve(u.hostname, decodeURIComponent(u.pathname.replace(/^\//, '')));
  if (!r) return new Response('no icon', { status: 404 });
  if (r.file) return net.fetch(require('node:url').pathToFileURL(r.file).href);
  try {
    const img = await app.getFileIcon(r.exe, { size: 'large' });
    if (img.isEmpty()) return new Response('no icon', { status: 404 });
    return new Response(img.toPNG(), { headers: { 'content-type': 'image/png' } });
  } catch { return new Response('no icon', { status: 404 }); }
}

function register(ses) { ses.protocol.handle('foxicon', respond); }

// 覆盖报告：每个程序的图标来自哪里（测试与关于页使用）
function report() {
  const ev = require('./everything').catalog().apps.map((a) => {
    const r = everythingIcon(a.id);
    return { kind: 'everything', id: a.id, name: a.name, license: a.license, source: r ? r.source : null, file: r ? r.file : null };
  });
  const builtins = [['libreoffice', 'writer'], ['libreoffice', 'calc'], ['libreoffice', 'impress'], ['builtin', 'terminal'], ['builtin', 'editor'], ['builtin', 'browser']].map(([k, id]) => {
    const r = resolve(k, id);
    return { kind: k, id, source: r ? r.source : null, file: r ? (r.file || r.exe) : null };
  });
  return { everything: ev, builtins };
}

module.exports = { register, resolve, report, everythingIcon };
