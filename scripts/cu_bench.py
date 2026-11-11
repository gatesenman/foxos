#!/usr/bin/env python3
"""电脑操控基准：同一批真实任务，比较三种做法的成功率、步数、耗时和花费。

  llm       只用大模型（DeepSeek v4 pro 工具调用循环）
  deepseek  System 1 = DeepSeek flash（JSON + logprob 置信度）+ System 2 规划器（DeepSeek v4 pro）
  jev       System 1 = TypeSafe Jev + System 2 规划器（DeepSeek v4 pro）——默认栈

任务在真实 XFCE 桌面上跑（需要 DISPLAY、agent-desktop、Chrome CDP、DeepSeek 密钥；jev 需要 TYPESAFE_API_KEY）。
密钥只从环境 / 狐狸OS 密钥库读，不写进结果。用法：
  python3 scripts/cu_bench.py --workspace /tmp/wsbench --configs llm,deepseek,jev --out docs/test-results/cu-bench.json
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "packages" / "core"
# 每百万 token 美元（2026-11 官网价，非高峰、缓存未命中，偏保守）
PRICE = {"deepseek-v4-pro": (0.66, 1.98), "deepseek-flash": (0.15, 0.60), "jev": (0.042, 0.0)}

SITE = """<!doctype html><html><head><title>Fox Shop</title></head><body>
<h1>Fox Shop order form</h1>
<form onsubmit="event.preventDefault();document.getElementById('out').textContent='Order code: FOX-'+document.getElementById('n').value+'-'+document.getElementById('c').value;">
<label for="n">Your name</label> <input id="n" name="name">
<label for="c">Colour</label> <select id="c" name="colour"><option value="red">Red</option><option value="green">Green</option><option value="blue">Blue</option></select>
<button type="submit">Place order</button></form><p id="out" role="status"></p></body></html>"""


def serve_site(port: int) -> None:
    d = Path("/tmp/cu-bench-site")
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(SITE, encoding="utf-8")
    h = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(d), **k)  # noqa: E731
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()


def sh(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def mousepad(ws: Path, name: str, text: str) -> None:
    sh("pkill -x mousepad; sleep 1")
    (ws / name).write_text(text, encoding="utf-8")
    subprocess.Popen(["mousepad", str(ws / name)], cwd=ws, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(2.5)


def xedit(ws: Path, name: str) -> None:
    sh("pkill -x xedit; sleep 0.5")
    (ws / name).write_text("", encoding="utf-8")
    subprocess.Popen(["xedit", "-geometry", "700x500+300+150", name], cwd=ws, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    time.sleep(2.0)


def tasks(ws: Path, port: int) -> list[dict]:
    return [
        {"id": "desk-replace", "surface": "a11y (agent-desktop)",
         "setup": lambda: mousepad(ws, "bench1.txt", "draft\n"),
         "args": ["In the open Mousepad window (bench1.txt), replace the whole document text with exactly \"Shopping list: apples, milk\""
                  " and then save the file.", "--app", "mousepad"],
         "check": lambda r: (ws / "bench1.txt").read_text().strip() == "Shopping list: apples, milk"},
        {"id": "desk-append", "surface": "a11y (agent-desktop)",
         "setup": lambda: mousepad(ws, "bench2.txt", "milk\n"),
         "args": ["In the open Mousepad window (bench2.txt), make the document contain two lines: 'milk' then 'eggs' (keep milk, add eggs"
                  " as the second line), then save the file.", "--app", "mousepad"],
         "check": lambda r: [x.strip() for x in (ws / "bench2.txt").read_text().strip().splitlines()] == ["milk", "eggs"]},
        {"id": "screen-xedit", "surface": "screen (no a11y → screenshot)",
         "setup": lambda: xedit(ws, "bench3.txt"),
         "args": ["In the xedit window (bench3.txt), click into the large text area, type exactly \"hello from screen mode\" and then click"
                  " the Save button at the top.", "--app", "xedit"],
         "check": lambda r: (ws / "bench3.txt").read_text().strip() == "hello from screen mode"},
        {"id": "web-local-form", "surface": "browser (fallback: Chrome not in a11y tree)",
         "setup": lambda: sh("pkill -x mousepad; pkill -x xedit"),
         "args": ["On the Fox Shop page, enter the name Ada, choose the colour Green, place the order and report the order code shown.",
                  "--url", f"http://127.0.0.1:{port}/"],
         "check": lambda r: "FOX-Ada-green" in str(r.get("answer") or "")},
        {"id": "web-wikipedia", "surface": "browser (fallback)",
         "setup": lambda: None,
         "args": ["Open the Wikipedia article for 'Rust (programming language)' by searching for it with the site's search box, then report"
                  " who designed the language according to the infobox.", "--url", "https://en.wikipedia.org/wiki/Main_Page"],
         "check": lambda r: "graydon hoare" in str(r.get("answer") or "").lower()},
    ]


CONFIGS = {"llm": ["--mode", "llm"], "deepseek": ["--mode", "s1s2", "--policy", "deepseek"], "jev": ["--mode", "s1s2", "--policy", "typesafe"]}


def cost(cfg: str, res: dict) -> tuple[float, dict]:
    u = res.get("usage") or {}
    if cfg == "llm":
        p = u
        c = p.get("prompt_tokens", 0) / 1e6 * PRICE["deepseek-v4-pro"][0] + p.get("completion_tokens", 0) / 1e6 * PRICE["deepseek-v4-pro"][1]
        return c, {"planner": p}
    pl, sp = u.get("planner") or {}, u.get("step_policy") or {}
    c = pl.get("prompt_tokens", 0) / 1e6 * PRICE["deepseek-v4-pro"][0] + pl.get("completion_tokens", 0) / 1e6 * PRICE["deepseek-v4-pro"][1]
    if cfg == "jev":
        c += sp.get("input_tokens", 0) / 1e6 * PRICE["jev"][0]
    else:
        c += sp.get("prompt_tokens", 0) / 1e6 * PRICE["deepseek-flash"][0] + sp.get("completion_tokens", 0) / 1e6 * PRICE["deepseek-flash"][1]
    return c, {"planner": pl, "step_policy": sp}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default="/tmp/wsbench")
    ap.add_argument("--configs", default="llm,deepseek,jev")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--max-steps", type=int, default=14)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default=str(ROOT / "docs" / "test-results" / "cu-bench.json"))
    a = ap.parse_args()
    ws = Path(a.workspace)
    ws.mkdir(parents=True, exist_ok=True)
    serve_site(a.port)
    out = Path(a.out)
    rows = json.loads(out.read_text()) if out.exists() else []
    for t in tasks(ws, a.port):
        if a.tasks and t["id"] not in a.tasks.split(","):
            continue
        for cfg in a.configs.split(","):
            t["setup"]()
            cmd = [sys.executable, "-m", "foxos", "--workspace", str(ws), "--agent", "bot:bench", "computer", "task", *t["args"],
                   *CONFIGS[cfg], "--vision", "off", "--approve", "auto", "--max-steps", str(a.max_steps), "--json"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=CORE, capture_output=True, text=True, timeout=900)
            wall = round(time.time() - t0, 1)
            try:
                res = json.loads(p.stdout).get("result") or {}
            except ValueError:
                res = {"error": (p.stderr or p.stdout)[-300:]}
            try:
                ok = bool(t["check"](res))
            except Exception:  # noqa: BLE001
                ok = False
            usd, toks = cost(cfg, res)
            row = {"task": t["id"], "surface": t["surface"], "config": cfg, "success": ok, "agent_said_success": res.get("success"),
                   "steps": res.get("steps"), "s1_steps": res.get("s1_steps"), "escalations": res.get("escalations"),
                   "mean_policy_ms": res.get("mean_policy_ms"), "seconds": res.get("seconds"), "wall_seconds": wall,
                   "usd": round(usd, 5), "tokens": toks, "routed_to": res.get("routed_to"), "route_reason": res.get("route_reason"),
                   "answer": (str(res.get("answer"))[:200] if res.get("answer") else None), "task_id": res.get("task_id"),
                   "error": res.get("error") if isinstance(res.get("error"), str) else None,
                   "at": time.strftime("%Y-%m-%d %H:%M:%S %z")}
            rows.append(row)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            print(json.dumps({k: row[k] for k in ("task", "config", "success", "steps", "wall_seconds", "usd")}), flush=True)
    summary(rows)
    return 0


def summary(rows: list[dict]) -> None:
    print("\n| config | success | mean steps | mean wall s | total USD |\n|---|---|---|---|---|")
    for cfg in CONFIGS:
        rs = [r for r in rows if r["config"] == cfg]
        if not rs:
            continue
        n = len(rs)
        print(f"| {cfg} | {sum(r['success'] for r in rs)}/{n} | {sum(r['steps'] or 0 for r in rs) / n:.1f} | "
              f"{sum(r['wall_seconds'] for r in rs) / n:.1f} | {sum(r['usd'] for r in rs):.4f} |")


if __name__ == "__main__":
    sys.exit(main())
