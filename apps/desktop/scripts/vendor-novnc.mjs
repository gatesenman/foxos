// 生成 src/renderer/vendor/novnc/novnc-rfb.js：把 noVNC（MPL-2.0）的 RFB 客户端打包成一个普通脚本（window.NoVNCRFB）。
// 用法（在任意临时目录装好依赖后）：
//   npm i @novnc/novnc@1.7.0 esbuild@0.25 && node apps/desktop/scripts/vendor-novnc.mjs <node_modules 所在目录>
// noVNC 的 core/util/browser.js 用了顶层 await 检测 H.264 解码；IIFE 不支持，这里改成 Promise 回填（结果只影响是否声明 H.264 编码）。
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = path.resolve(process.argv[2] || '.');
const { build } = await import(path.join(root, 'node_modules', 'esbuild', 'lib', 'main.js'));
const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, '..', 'src', 'renderer', 'vendor', 'novnc');
const nv = path.join(root, 'node_modules', '@novnc', 'novnc');
const version = JSON.parse(fs.readFileSync(path.join(nv, 'package.json'), 'utf8')).version;
fs.mkdirSync(outDir, { recursive: true });
await build({
  stdin: { contents: `import RFB from ${JSON.stringify(path.join(nv, 'core', 'rfb.js'))};\nwindow.NoVNCRFB = RFB;\n`, resolveDir: root, loader: 'js' },
  bundle: true, format: 'iife', minify: true, target: 'chrome130', legalComments: 'eof',
  banner: { js: `/* noVNC ${version} core (https://github.com/novnc/noVNC), MPL-2.0; pako, MIT. Source: npm @novnc/novnc@${version}. See LICENSE.txt in this folder. */` },
  outfile: path.join(outDir, 'novnc-rfb.js'),
  plugins: [{ name: 'no-tla', setup(b) {
    b.onLoad({ filter: /core[\\/]util[\\/]browser\.js$/ }, (a) => {
      const src = fs.readFileSync(a.path, 'utf8');
      const fixed = src.replace('supportsWebCodecsH264Decode = await _checkWebCodecsH264DecodeSupport();',
        '_checkWebCodecsH264DecodeSupport().then((v) => { supportsWebCodecsH264Decode = v; }, () => {});');
      if (fixed === src) throw new Error('noVNC browser.js changed: update vendor-novnc.mjs');
      return { contents: fixed, loader: 'js' };
    });
  } }],
});
fs.copyFileSync(path.join(nv, 'LICENSE.txt'), path.join(outDir, 'LICENSE.txt'));
fs.copyFileSync(path.join(nv, 'AUTHORS'), path.join(outDir, 'AUTHORS'));
fs.copyFileSync(path.join(nv, 'vendor', 'pako', 'LICENSE'), path.join(outDir, 'LICENSE.pako.txt'));
fs.copyFileSync(path.join(nv, 'docs', 'LICENSE.MPL-2.0'), path.join(outDir, 'LICENSE.MPL-2.0.txt'));
console.log(`noVNC ${version} -> ${outDir}`);
