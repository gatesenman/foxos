// 狐狸OS 在用户机器上构建 Everything 应用时使用的包装配置：
// 不修改上游源码，只在构建时追加一个插件，把应用自己的 ES 模块（store、actions 等）登记到
// globalThis.__foxosModules，供狐狸OS 的应用桥调用应用自身的逻辑（与人在界面上操作走同一套代码）。
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';

const appDir = process.cwd();
const candidates = ['vite.config.js', 'vite.config.mjs', 'vite.config.ts', 'vite.config.mts'];
const found = candidates.find((f) => fs.existsSync(path.join(appDir, f)));

function exposeModules() {
  const srcDir = path.join(appDir, 'src') + path.sep;
  return {
    name: 'foxos-expose-modules',
    enforce: 'post',
    transform(code, id) {
      const file = id.split('?')[0];
      if (!file.startsWith(srcDir) || file.includes(`${path.sep}node_modules${path.sep}`)) return null;
      if (!/\.(m?[jt]sx?)$/.test(file) || id.includes('?')) return null;
      if (!/\bexport\b/.test(code)) return null;
      const rel = path.relative(appDir, file).split(path.sep).join('/');
      return { code: `${code}\nimport * as __foxosSelf from ${JSON.stringify(file)};\n(globalThis.__foxosModules ||= {})[${JSON.stringify(rel)}] = __foxosSelf;\n`, map: null };
    },
  };
}

export default async (env) => {
  let user = {};
  if (found) {
    const mod = await import(pathToFileURL(path.join(appDir, found)).href);
    user = mod.default;
    if (typeof user === 'function') user = await user(env);
  }
  return { ...user, plugins: [...(user.plugins || []), exposeModules()] };
};
