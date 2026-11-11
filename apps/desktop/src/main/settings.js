'use strict';
const { t } = require('./i18n');
// 设置与会话状态：保存在 userData 下的 JSON 文件；API 密钥用 Electron safeStorage 加密（可用时）
const { app, safeStorage } = require('electron');
const fs = require('node:fs');
const path = require('node:path');

function file(name) { return path.join(app.getPath('userData'), name); }

function readJson(name, fallback) {
  try { return JSON.parse(fs.readFileSync(file(name), 'utf8')); } catch { return fallback; }
}

function writeJson(name, data) {
  fs.mkdirSync(app.getPath('userData'), { recursive: true });
  const tmp = file(`${name}.tmp`);
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2), { mode: 0o600 });
  fs.renameSync(tmp, file(name));
}

const DEFAULTS = { workspace: null, python: null, setupDone: false, secrets: {}, agentDefault: null };

function load() { return { ...DEFAULTS, ...readJson('settings.json', {}) }; }
function save(s) { writeJson('settings.json', s); }

function encryptionInfo() {
  const available = safeStorage.isEncryptionAvailable();
  let backend = 'unknown';
  try { backend = safeStorage.getSelectedStorageBackend ? safeStorage.getSelectedStorageBackend() : 'system'; } catch { /* 非 Linux */ }
  return { available, backend };
}

function setSecret(name, value) {
  if (!/^[A-Z][A-Z0-9_]{1,63}$/.test(name)) throw new Error(t('settings.environment_variable_names_may'));
  const s = load();
  if (!value) delete s.secrets[name];
  else if (safeStorage.isEncryptionAvailable()) s.secrets[name] = { enc: safeStorage.encryptString(value).toString('base64') };
  else s.secrets[name] = { plain: value };
  save(s);
}

function secretEnv() {
  const out = {};
  for (const [k, v] of Object.entries(load().secrets || {})) {
    try { out[k] = v.enc ? safeStorage.decryptString(Buffer.from(v.enc, 'base64')) : v.plain; } catch { /* 无法解密则跳过 */ }
  }
  return out;
}

function secretNames() { return Object.keys(load().secrets || {}); }

function loadSession() { return readJson('session.json', { windows: [] }); }
function saveSession(sess) { writeJson('session.json', sess); }

module.exports = { load, save, setSecret, secretEnv, secretNames, encryptionInfo, loadSession, saveSession };
