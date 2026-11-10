'use strict';
// 监听工作空间：智能体（CLI / MCP / ACP）对文件的修改实时推送到桌面
const fs = require('node:fs');
const path = require('node:path');

function watchWorkspace(root, onChange) {
  let pending = new Set();
  let timer = null;
  let audit = false;
  const flush = () => {
    const paths = [...pending];
    pending = new Set();
    timer = null;
    const a = audit;
    audit = false;
    onChange({ paths, audit: a });
  };
  const w = fs.watch(root, { recursive: true }, (_event, filename) => {
    if (!filename) return;
    const rel = filename.split(path.sep).join('/');
    if (rel.startsWith('.foxos/')) {
      if (rel === '.foxos/audit.jsonl') audit = true; else return;
    } else if (rel.includes('.foxos-tmp-')) {
      return;
    } else {
      pending.add(rel);
    }
    if (!timer) timer = setTimeout(flush, 150);
  });
  return () => w.close();
}

module.exports = { watchWorkspace };
