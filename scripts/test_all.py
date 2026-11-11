#!/usr/bin/env python3
"""npm run test:all：运行全部测试并生成 docs/test-report.md。

依次运行（不使用模拟）：
  pytest        packages/core/tests
  smoke         apps/desktop/scripts/smoke.sh（桌面冒烟）
  e2e           apps/desktop/e2e/*.e2e.js / *.e2e.mjs（Playwright 驱动真实 Electron 桌面、官方 MCP SDK）
  os            packages/core/tests/test_os_session.py、test_os_kvm.py 与 test_os_chrome.py（真实 XFCE / X11 会话、linux-kvm 动词）
结果（JUnit XML）写到 build/test-results/，汇总写到 docs/test-results/summary.json，报告写到 docs/test-report.md。

用法：python3 scripts/test_all.py [--only pytest,smoke,e2e] [--e2e mcp,sandbox,...] [--report-only]
环境变量：
  DISPLAY        没有时自动启动 Xvfb（需要已安装 Xvfb）
  FOXOS_HOME     Everything 应用所在的狐狸OS 主目录（everything.e2e 需要已安装的应用：foxos everything install --all）
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "test-results"
DESKTOP = ROOT / "apps" / "desktop"
PY = str(ROOT / ".venv" / "bin" / "python") if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
E2E_ORDER = ["icons.e2e.js", "scrollbars.e2e.js", "i18n.e2e.js", "mcp.e2e.mjs", "sandbox.e2e.js", "environments.e2e.js", "env-install.e2e.js", "hostaccess.e2e.js", "bots.e2e.mjs", "everything.e2e.js"]


def ensure_display(env: dict) -> subprocess.Popen | None:
    if env.get("DISPLAY") or sys.platform != "linux":
        return None
    if not shutil.which("Xvfb"):
        print("没有 DISPLAY，也找不到 Xvfb：桌面端到端测试会失败", file=sys.stderr)
        return None
    env["DISPLAY"] = ":97"
    p = subprocess.Popen(["Xvfb", ":97", "-screen", "0", "1600x1000x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    return p


def run(cmd: list[str], env: dict, cwd: Path, log: Path) -> int:
    print(f"\n$ {' '.join(cmd)}", flush=True)
    with open(log, "w", encoding="utf-8") as f:
        p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        for line in p.stdout:
            sys.stdout.write(line)
            f.write(line)
        return p.wait()


def junit_single(path: Path, name: str, ok: bool, message: str, seconds: float) -> None:
    from xml.sax.saxutils import quoteattr
    body = "" if ok else f"<failure message={quoteattr(message[-500:])}/>"
    path.write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<testsuites><testcase name={quoteattr(name)} classname="smoke" file="smoke.sh" time="{seconds:.3f}">{body}</testcase></testsuites>\n', encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="pytest,smoke,e2e",
                    help="comma list: pytest,smoke,e2e,os")
    ap.add_argument("--e2e", default=",".join(f.split(".")[0] for f in E2E_ORDER))
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "packages" / "core"), "FOXOS_PYTHON": PY}
    xvfb = None
    codes = {}
    t0 = time.time()
    try:
        only = set(a.only.split(","))
        if not a.report_only:
            if "pytest" in only:
                codes["pytest"] = run([PY, "-m", "pytest", "-q", "packages/core/tests", f"--junitxml={OUT / 'pytest.xml'}"], env, ROOT, OUT / "pytest.log")
            if "os" in only:
                codes["os"] = run([PY, "-m", "pytest", "-q",
                                   "packages/core/tests/test_os_session.py", "packages/core/tests/test_os_kvm.py", "packages/core/tests/test_os_chrome.py",
                                   f"--junitxml={OUT / 'os.xml'}"], env, ROOT, OUT / "os.log")
            if "smoke" in only or "e2e" in only:
                xvfb = ensure_display(env)
            if "smoke" in only and sys.platform == "linux":
                s = time.time()
                out = OUT / "smoke.png"
                c = run(["bash", "scripts/smoke.sh", str(out)], env, DESKTOP, OUT / "smoke.log")
                junit_single(OUT / "smoke.xml", "US-08 桌面冒烟", c == 0, (OUT / "smoke.log").read_text(encoding="utf-8"), time.time() - s)
                codes["smoke"] = c
            if "e2e" in only:
                want = set(a.e2e.split(","))
                for f in E2E_ORDER:
                    if f.split(".")[0] not in want:
                        continue
                    name = f.split(".")[0]
                    codes[f] = run(["node", "--test", "--test-timeout=1800000", "--test-reporter=spec", "--test-reporter-destination=stdout",
                                    "--test-reporter=junit", f"--test-reporter-destination={OUT / (name + '.xml')}", f"e2e/{f}"], env, DESKTOP, OUT / f"{name}.log")
    finally:
        if xvfb:
            xvfb.terminate()
    r = subprocess.run([PY, str(ROOT / "scripts" / "gen_test_report.py"), "--duration", str(round(time.time() - t0))], cwd=ROOT, env=env)
    print("\n退出码：", codes)
    return 1 if any(codes.values()) or r.returncode else 0


if __name__ == "__main__":
    sys.exit(main())
