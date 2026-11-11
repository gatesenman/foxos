// Drives a real headless Chrome over the DevTools protocol (no extra packages).
// usage: node cdp.mjs URL OUT.json [SCRIPT.json]
// SCRIPT.json: [{"wait": ms} | {"eval": "js"} | {"shot": "path.png"} | {"waitFor": "css selector"} | {"click": "css"} | {"type": ["css", "text"]} | {"size": [w, h]}]
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, out, scriptPath] = process.argv.slice(2);
const steps = scriptPath ? JSON.parse(readFileSync(scriptPath, "utf8")) : [{ wait: 2000 }];
const chrome = process.env.CHROME || "google-chrome";
const prof = mkdtempSync(join(tmpdir(), "foxos-cdp-"));
const size = (steps.find(s => s.size) || { size: [1280, 800] }).size;
const proc = spawn(chrome, ["--headless=new", "--no-sandbox", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
  `--user-data-dir=${prof}`, "--remote-debugging-port=0", `--window-size=${size[0]},${size[1]}`, "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
const wsUrl = await new Promise((res, rej) => {
  let buf = "";
  proc.stderr.on("data", d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); });
  setTimeout(() => rej(new Error("chrome did not start")), 20000);
});
const base = wsUrl.replace(/\/devtools\/browser\/.*/, "").replace("ws://", "http://");
const targets = await (await fetch(base + "/json/list")).json();
const page = targets.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const console_ = []; const errors = [];
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === "Runtime.consoleAPICalled") console_.push(m.params.type + ": " + m.params.args.map(a => a.value ?? a.description).join(" "));
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Log.entryAdded" && m.params.entry.level === "error") errors.push(m.params.entry.text + " " + (m.params.entry.url || ""));
});
const send = (method, params = {}) => new Promise((res, rej) => {
  const i = ++id; pending.set(i, m => m.error ? rej(new Error(method + ": " + m.error.message)) : res(m.result));
  ws.send(JSON.stringify({ id: i, method, params }));
});
const evaluate = async expr => {
  const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error("eval: " + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
  return r.result.value;
};
const sleep = ms => new Promise(r => setTimeout(r, ms));
await send("Runtime.enable"); await send("Log.enable"); await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: size[0], height: size[1], deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url });
const results = [];
try {
  for (const s of steps) {
    if (s.wait) await sleep(s.wait);
    if (s.waitFor) {
      const t0 = Date.now(); const lim = s.timeout || 20000;
      while (!(await evaluate(`!!document.querySelector(${JSON.stringify(s.waitFor)})`))) {
        if (Date.now() - t0 > lim) throw new Error("timeout waiting for " + s.waitFor);
        await sleep(150);
      }
    }
    if (s.click) await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(s.click)}); if (!e) throw new Error("no element ${s.click.replace(/"/g, "'")}"); e.click(); })()`);
    if (s.type) {
      await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(s.type[0])}); e.focus(); e.value = ""; })()`);
      await send("Input.insertText", { text: s.type[1] });
    }
    if (s.key) await send("Input.dispatchKeyEvent", { type: "keyDown", key: s.key, code: s.key, windowsVirtualKeyCode: s.key === "Enter" ? 13 : 0, text: s.key === "Enter" ? "\r" : undefined });
    if (s.eval) results.push(await evaluate(s.eval));
    if (s.shot) {
      const r = await send("Page.captureScreenshot", { format: "png" });
      writeFileSync(s.shot, Buffer.from(r.data, "base64"));
    }
  }
} catch (e) { errors.push("STEP: " + e.message); }
writeFileSync(out, JSON.stringify({ results, console: console_, errors }, null, 1));
ws.close(); proc.kill("SIGKILL"); await sleep(300); rmSync(prof, { recursive: true, force: true });
process.exit(0);
