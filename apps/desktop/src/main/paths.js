'use strict';
// 路径与可执行文件定位（开发模式 / 打包模式通用）
const { app } = require('electron');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const REPO_ROOT = path.resolve(__dirname, '..', '..', '..', '..');
const IS_WIN = process.platform === 'win32';

function argValue(name) {
  const hit = process.argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : null;
}

function resourcesDir() {
  return app.isPackaged ? process.resourcesPath : path.join(REPO_ROOT, 'assets');
}

function corePath() {
  return app.isPackaged ? path.join(process.resourcesPath, 'core') : path.join(REPO_ROOT, 'packages', 'core');
}

function iconPath() {
  return app.isPackaged ? path.join(process.resourcesPath, 'icon.png') : path.join(REPO_ROOT, 'assets', 'icon.png');
}

// 在 PATH 中查找可执行文件（Windows 考虑 PATHEXT）
function which(cmd, extraDirs = []) {
  if (path.isAbsolute(cmd)) return fs.existsSync(cmd) ? cmd : null;
  const dirs = [...extraDirs, ...(process.env.PATH || '').split(path.delimiter)].filter(Boolean);
  const exts = IS_WIN ? (process.env.PATHEXT || '.EXE;.CMD;.BAT;.COM').split(';').map((e) => e.toLowerCase()) : [''];
  for (const d of dirs) {
    for (const e of exts) {
      const p = path.join(d, cmd + e);
      try {
        if (fs.statSync(p).isFile()) return p;
      } catch { /* 不存在 */ }
    }
  }
  return null;
}

function defaultWorkspace() {
  return process.env.FOXOS_WORKSPACE || path.join(os.homedir(), 'FoxOS', 'workspace');
}

module.exports = { REPO_ROOT, IS_WIN, argValue, resourcesDir, corePath, iconPath, which, defaultWorkspace };
