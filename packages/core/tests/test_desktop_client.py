"""US-87：Windows（以及 macOS / 普通 Linux）上的桌面程序是“狐狸OS 电脑”的客户端，不操作用户自己的电脑。

Sarah：应用中心安装、打开 Word、终端、文件、Everything 应用、智能体都必须在狐狸OS 虚拟机（或远程狐狸OS）里执行；
本机执行默认关闭，只能在设置里明确打开，并且每次都要确认。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DESK = ROOT / "apps" / "desktop"
MAIN = DESK / "src" / "main"
REND = DESK / "src" / "renderer"


def node(js: str):
    if not shutil.which("node"):
        pytest.skip("需要 node")
    r = subprocess.run(["node", "-e", js], cwd=DESK, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def test_US87_execution_mode_defaults_to_client(tmp_path):
    foxos_rel = tmp_path / "os-release-foxos"
    foxos_rel.write_text('NAME="FoxOS"\nID=foxos\nID_LIKE=debian\n', encoding="utf-8")
    other = tmp_path / "os-release-debian"
    other.write_text("ID=debian\n", encoding="utf-8")
    out = node(f"""
const p = require('./src/main/policy.js');
console.log(JSON.stringify({{
  packaged: p.mode({{ env: {{}}, packaged: true, osRelease: {json.dumps(str(other))} }}),
  dev: p.mode({{ env: {{}}, packaged: false, osRelease: {json.dumps(str(other))} }}),
  forcedClient: p.mode({{ env: {{ FOXOS_CLIENT_MODE: '1' }}, packaged: false }}),
  hostEnv: p.mode({{ env: {{ FOXOS_HOST_EXECUTION: '1' }}, packaged: true, osRelease: {json.dumps(str(other))} }}),
  foxosOs: p.mode({{ env: {{}}, packaged: true, osRelease: {json.dumps(str(foxos_rel))} }}),
  isFoxos: p.isFoxosOs({json.dumps(str(foxos_rel))}),
}}));
""")
    assert out["packaged"] == "client"               # 安装包（Windows / macOS / 普通 Linux）默认是客户端
    assert out["forcedClient"] == "client"
    assert out["dev"] == "native" and out["hostEnv"] == "native"
    assert out["isFoxos"] is True
    if sys.platform.startswith("linux"):
        assert out["foxosOs"] == "native"              # 狐狸OS 自己（ISO / 虚拟机里）就在本机执行


def test_US87_kernel_commands_route_to_the_guest_except_vm_lifecycle():
    out = node("""
const p = require('./src/main/policy.js');
const cases = [['everything','install','circuits'], ['desktop','launch','--','libreoffice','--writer'], ['files','list'], ['acp','agent','install','x'], ['sheets','create','a.xlsx'], ['runtime','install','node'], ['env','list'], ['env','install','foxos-debian-12','foxos'], ['machine','pair'], ['help']];
console.log(JSON.stringify(Object.fromEntries(cases.map((c) => [c.join(' '), p.routeKernel(c)]))));
""")
    for k, v in out.items():
        first = k.split()[0]
        assert v == ("local" if first in ("env", "machine", "help") else "guest"), k


def test_US87_ssh_arguments_are_batch_mode_and_quoted(tmp_path):
    out = node("""
const c = require('./src/main/cmdline.js');
console.log(JSON.stringify({
  args: c.sshArgs({ host: '127.0.0.1', port: 2222, user: 'foxos', key: 'C:\\\\Users\\\\A\\\\key', alias: 'foxos-env-foxos' }, { tty: true, knownHosts: 'C:\\\\kh' }),
  line: c.remoteLine(['foxos', 'everything', 'install', "it's"]),
}));
""")
    a = out["args"]
    assert a[-2:] == ["-tt", "foxos@127.0.0.1"]
    for opt in ("BatchMode=yes", "StrictHostKeyChecking=accept-new", "UserKnownHostsFile=C:\\kh", "HostKeyAlias=foxos-env-foxos", "IdentitiesOnly=yes"):
        assert opt in a
    assert a[a.index("-p") + 1] == "2222" and a[a.index("-i") + 1] == "C:\\Users\\A\\key"
    # 来宾 sh 解析后得到原样的 argv
    fake = tmp_path / "foxos"
    fake.write_text('#!/bin/sh\nprintf "[%s]" "$@"\n', encoding="utf-8")
    fake.chmod(0o755)
    assert out["line"].startswith("exec sh -lc ")
    r = subprocess.run(["sh", "-c", out["line"].replace("exec sh -lc", "sh -c", 1)], capture_output=True, text=True, env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"})
    assert r.stdout == "[everything][install][it's]"


def _src(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_US87_main_process_routes_actions_to_the_guest_and_gates_host_execution():
    idx = _src(MAIN / "index.js")
    # 打开 Word = 在狐狸OS 电脑里 desktop launch libreoffice --writer
    assert "handle('office:launch', (appId, file) => (CLIENT() ? client.officeLaunch(appId, file) : apps.launchOffice(appId, file)));" in idx
    assert "'desktop', 'launch', '--', ...argv" in _src(MAIN / "client.js") and "writer: '--writer'" in _src(MAIN / "client.js")
    # 终端：客户端模式下是来宾 shell；本机命令必须先过 hostGate
    pty = idx[idx.index("handle('pty:spawn'"):idx.index("ipcMain.on('pty:write'")]
    assert "guest.terminalSpec(opts.guestArgv || null)" in pty
    assert re.search(r"if \(opts\.command && !opts\.guestArgv\) \{ await hostGate\(", pty)
    # 智能体、Everything、聊天
    for frag in ("CLIENT() ? client.agentsList()", "CLIENT() ? client.agentsInstall(", "CLIENT() ? await client.agentInfo(agentId)",
                 "CLIENT() ? client.evList(", "CLIENT() ? client.botsEnsure() : bots.ensure()"):
        assert frag in idx, frag
    # 本机执行闸门：默认关闭，打开后每次原生对话框确认
    gate = idx[idx.index("async function hostGate"):idx.index("handle('apps:detect'")]
    assert "if (!(await hostaccess.enabled())) throw" in gate and "dialog.showMessageBox" in gate and "cancelId: 1" in gate and "defaultId: 1" in gate
    # 开关只有一个来源：核心的 foxos bot host-access（US-156），settings.json 里不再存
    assert "await hostaccess.set(patch.hostExecution === true)" in idx and "delete s.hostExecution" in idx
    ha = _src(MAIN / "hostaccess.js")
    assert "['bot', 'host-access', on ? 'enable' : 'disable']" in ha and ".enabled === true" in ha
    assert "hostExecution" not in _src(MAIN / "settings.js")      # 没有默认 true
    # kernel.run：客户端模式下除 env / machine 外都去来宾
    k = _src(MAIN / "kernel.js")
    assert "executionMode() === 'client' && policy.routeKernel(args) === 'guest'" in k


def test_US87_renderer_installs_and_opens_in_the_guest():
    term = _src(REND / "js/apps/terminal.js")
    assert "if (FX.env.mode === 'client') return new Promise((resolve) => FX.openWindow('terminal', { title, guestArgv: ['foxos', ...args]" in term
    app = _src(REND / "js/apps/appcenter.js")
    assert "FX.runFoxosInTerminal(" in app                       # Everything 安装 → 来宾终端
    assert "guestArgv: ['sh', '-c', 'sudo apt-get update -q && sudo apt-get install -y \"$@\"', 'apt', ...pkgs]" in app
    assert app.index("if (FX.env.mode === 'client') {\n          const pkgs") < app.index("await FX.runInTerminal(")
    ev = _src(REND / "js/apps/everything.js")
    assert "window.foxos.everything.openInGuest(params.app" in ev
    comp = _src(REND / "js/apps/computer.js")
    assert "new window.NoVNCRFB(view, channel(info.id)" in comp and "lifecycleArgv: argv" in comp
    assert (REND / "vendor/novnc/novnc-rfb.js").stat().st_size > 100_000 and (REND / "vendor/novnc/LICENSE.txt").exists()
    assert '<script src="vendor/novnc/novnc-rfb.js"></script>' in _src(REND / "index.html")


def test_US87_qemu_vm_exposes_a_loopback_console_for_the_client(tmp_path):
    sys.path.insert(0, str(ROOT / "packages" / "core"))
    from foxos.envs import kvm
    argv = kvm._argv_qemu_tcg("qemu-system-x86_64", {"name": "t", "disk": str(tmp_path / "d.qcow2")}, tmp_path, 2048, 2, 5907, 40000, tmp_path / "s.log", 40022)
    assert argv[argv.index("-vnc") + 1] == "127.0.0.1:7"
    assert "hostfwd=tcp:127.0.0.1:40022-:22" in " ".join(argv)


def test_US87_acp_stdio_runs_an_installed_agent_with_stdio_passed_through(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "packages" / "core"), "FOXOS_HOME": str(tmp_path / "home")}
    msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": 1, "clientCapabilities": {}}}) + "\n"
    r = subprocess.run([sys.executable, "-m", "foxos", "--workspace", str(tmp_path / "ws"), "acp", "stdio", "foxos-local"], input=msg, capture_output=True, text=True, env=env, timeout=60)
    first = json.loads(r.stdout.splitlines()[0])
    assert first["id"] == 1 and first["result"]["agentInfo"]["name"] == "foxos-local"
    r = subprocess.run([sys.executable, "-m", "foxos", "acp", "stdio", "nope", "--json"], capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 3 and json.loads(r.stdout)["error"]["code"] == "NOT_FOUND"


def test_US87_json_flag_goes_before_the_command_so_desktop_launch_does_not_swallow_it():
    """`foxos desktop launch -- libreoffice --writer --json` 会把 --json 当成 LibreOffice 的参数（Writer 打不开）。"""
    for f in ("kernel.js", "guest.js"):
        src = _src(MAIN / f)
        assert "...(json ? ['--json'] : []), ...args]" in src, f
        assert "...args, ...(json ? ['--json'] : [])" not in src, f


def test_US86_cli_starts_without_posix_only_modules_like_windows():
    """Windows 没有 pwd 模块：顶层 import pwd 曾让 Windows 上的 foxos 每个命令都报 ModuleNotFoundError。"""
    import subprocess
    import sys
    code = (
        "import sys; sys.modules['pwd'] = None; sys.modules['grp'] = None\n"
        "from foxos.cli import main\n"
        "sys.argv = ['foxos', '--json', 'acp', 'list']\n"
        "sys.exit(main())\n"
    )
    core = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, "-c", code], cwd=core, capture_output=True, text=True, timeout=300,
                       env={**__import__("os").environ, "PYTHONPATH": str(core)})
    assert "ModuleNotFoundError" not in (r.stdout + r.stderr), r.stderr[-2000:]
    assert '"ok": true' in r.stdout, (r.stdout[-500:], r.stderr[-2000:])


def test_US87_guest_version_requirement_and_first_run_help():
    """没有来宾的用户不能卡住：首次运行说明需要哪个版本、怎么拿到一台；连上旧版本时明确提示。"""
    out = node("""
const p = require('./src/main/policy');
console.log(JSON.stringify({min: p.GUEST_MIN_VERSION, links: p.GUEST_LINKS,
  c: [p.guestCompat('0.3.2'), p.guestCompat('foxos 0.3.3'), p.guestCompat('0.10.0'), p.guestCompat(null), p.guestCompat('0.2.9')]}));
""")
    assert out["min"] == "0.3.3"
    assert out["c"] == ["old", "ok", "ok", "unknown", "old"]
    assert all(u.startswith("https://github.com/gatesenman/foxos/") for u in out["links"].values())
    assert "os-preview" in out["links"]["releases"]
    assert "compat: policy.guestCompat(" in _src(MAIN / "guest.js")
    assert "guestLinks: policy.GUEST_LINKS" in _src(MAIN / "index.js")
    comp = _src(DESK / "src" / "renderer" / "js" / "apps" / "computer.js")
    for needle in ("'data-setup': 'need'", "client.need_iso", "client.need_ssh", "client.need_create", "client.need_remote",
                   "link('releases'", "link('iso_guide'", "client.version_old", "client.preset_too_old"):
        assert needle in comp, needle
    for loc in ("zh-CN", "en-US"):
        d = json.loads((DESK / "src" / "locales" / f"{loc}.json").read_text(encoding="utf-8"))
        for k in ("need_title", "need_version", "need_iso", "need_ssh", "need_create", "need_remote", "link_releases",
                  "link_iso_guide", "link_client_guide", "preset_too_old", "version_old", "version_old_note"):
            assert d.get(f"client.{k}"), (loc, k)
        assert "{0}" in d["client.need_version"] and "{1}" in d["client.version_old"]
