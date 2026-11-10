"""US-52 轻量隔离级别（foxos sandbox）：真实的 Landlock + seccomp 限制（Linux），以及 macOS / Windows 策略生成。"""

import json
import os
import socket
import subprocess
import sys
import threading

import pytest

from foxos import sandbox as sb
from foxos.sandbox import linux as sbl
from foxos.sandbox import macos, windows

LINUX_OK = sys.platform.startswith("linux") and sbl.capabilities()["available"]
needs_landlock = pytest.mark.skipif(not LINUX_OK, reason="需要启用了 Landlock 的 Linux 内核")


def srun(fox, *cmd, opts=(), home=None):
    env = {"FOXOS_HOME": str(home)} if home else None
    code, _, p = fox.run("sandbox", "run", *opts, "--json", "--", *cmd, json_out=False, extra_env=env)
    data = json.loads(p.stdout)
    assert data["ok"], p.stdout + p.stderr
    return data["result"]


@pytest.fixture
def fhome(tmp_path):
    h = tmp_path / "foxhome"
    h.mkdir()
    return h


@pytest.fixture
def outside(tmp_path):
    d = tmp_path / "outside"
    d.mkdir()
    (d / "secret.txt").write_text("top secret")
    return d


def test_check_reports_capabilities(fox):
    code, data, _ = fox.run("sandbox", "check")
    assert code == 0
    caps = data["result"]
    assert caps["platform"] == sb.PLATFORM
    if sys.platform.startswith("linux"):
        assert caps["mechanism"] == "landlock+seccomp"
        assert isinstance(caps["landlock_abi"], int)


@needs_landlock
def test_workspace_writable_outside_not(fox, fhome, outside):
    r = srun(fox, "sh", "-c", f"echo hello > in.txt && cat in.txt; echo x > {outside}/escape.txt; cat {outside}/secret.txt; ls /home", home=fhome)
    assert r["stdout"].startswith("hello")
    assert (fox.ws / "in.txt").read_text() == "hello\n"
    assert not (outside / "escape.txt").exists()
    assert "top secret" not in r["stdout"]
    assert r["stderr"].count("Permission denied") >= 3


@needs_landlock
def test_children_inherit_restrictions(fox, fhome, outside):
    srun(fox, "sh", "-c", f"sh -c 'python3 -c \"open(\\\"{outside}/deep.txt\\\", \\\"w\\\")\"'", home=fhome)
    assert not (outside / "deep.txt").exists()


@needs_landlock
def test_declared_read_and_write_paths(fox, fhome, outside, tmp_path):
    w = tmp_path / "extra-write"
    w.mkdir()
    r = srun(fox, "sh", "-c", f"cat {outside}/secret.txt; echo y > {outside}/nope.txt; echo z > {w}/ok.txt",
             opts=("--read", str(outside), "--write", str(w)), home=fhome)
    assert "top secret" in r["stdout"]
    assert not (outside / "nope.txt").exists()
    assert (w / "ok.txt").read_text() == "z\n"


@needs_landlock
def test_private_home_and_tmp(fox, fhome):
    r = srun(fox, "sh", "-c", 'echo $HOME; echo $TMPDIR; echo cfg > "$HOME/.agentrc" && cat "$HOME/.agentrc"; echo t > "$TMPDIR/t" && cat "$TMPDIR/t"', home=fhome)
    lines = r["stdout"].split()
    assert lines[0].startswith(str(fhome / "sandbox"))
    assert lines[2:] == ["cfg", "t"]
    assert not (fox.ws / ".agentrc").exists()


class _Server:
    def __init__(self):
        self.s = socket.socket()
        self.s.bind(("127.0.0.1", 0))
        self.s.listen(8)
        self.port = self.s.getsockname()[1]
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            try:
                c, _ = self.s.accept()
                c.close()
            except OSError:
                return


PROBE = """
import socket, sys
for port in map(int, sys.argv[1:]):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=3).close(); print(port, "ok")
    except OSError as e:
        print(port, type(e).__name__)
try:
    socket.socket(socket.AF_INET, socket.SOCK_DGRAM); print("udp ok")
except OSError as e:
    print("udp", type(e).__name__)
"""


@needs_landlock
def test_network_on_off_and_allowed_port(fox, fhome, tmp_path):
    a, b = _Server(), _Server()
    on = srun(fox, "python3", "-c", PROBE, str(a.port), str(b.port), home=fhome)["stdout"]
    assert f"{a.port} ok" in on and f"{b.port} ok" in on and "udp ok" in on
    off = srun(fox, "python3", "-c", PROBE, str(a.port), opts=("--network", "off"), home=fhome)["stdout"]
    assert f"{a.port} PermissionError" in off and "udp PermissionError" in off
    # 只放行一个端口（桌面端用来连接宿主上的 foxos MCP HTTP 服务器）
    ws = str(fox.ws)
    p = subprocess.run([sys.executable, "-m", "foxos.sandbox", "wrap", "--workspace", ws, "--network", "off", "--connect-port", str(a.port), "--",
                        "python3", "-c", PROBE, str(a.port), str(b.port)], capture_output=True, text=True, env={**os.environ, "FOXOS_HOME": str(fhome)},
                       cwd=str(sb.Path(sb.__file__).parents[2]))
    caps = sbl.capabilities()
    if caps["landlock_abi"] >= 4:
        assert f"{a.port} ok" in p.stdout and f"{b.port} PermissionError" in p.stdout and "udp PermissionError" in p.stdout, p.stdout + p.stderr


@needs_landlock
def test_seccomp_blocks_namespaces_and_ptrace(fox, fhome):
    code = ("import ctypes, os; libc = ctypes.CDLL(None, use_errno=True); "
            "r = libc.ptrace(0, 0, 0, 0); print('ptrace', r, ctypes.get_errno()); "
            "r = libc.unshare(0x10000000); print('unshare', r, ctypes.get_errno())")
    out = srun(fox, "python3", "-c", code, home=fhome)["stdout"]
    assert "ptrace -1 1" in out and "unshare -1 1" in out
    st = srun(fox, "sh", "-c", "grep -E '^(NoNewPrivs|Seccomp):' /proc/self/status", home=fhome)["stdout"]
    assert "NoNewPrivs:\t1" in st and "Seccomp:\t2" in st


@needs_landlock
@pytest.mark.skipif(LINUX_OK and sbl.abi_version() < 6, reason="信号作用域需要 Landlock ABI 6")
def test_cannot_signal_processes_outside(fox, fhome):
    victim = subprocess.Popen(["sleep", "60"])
    try:
        r = srun(fox, "sh", "-c", f"kill -0 {victim.pid} && echo reach; sleep 30 & kill $! && echo own-child", home=fhome)
        assert "reach" not in r["stdout"] and "own-child" in r["stdout"]
        assert victim.poll() is None
    finally:
        victim.kill()


@needs_landlock
def test_policy_command_shows_rules(fox):
    code, _, p = fox.run("sandbox", "policy", "--network", "off", "--json", "--", "python3", json_out=False)
    r = json.loads(p.stdout)["result"]
    kinds = {x["path"]: x["access"] for x in r["landlock_rules"]}
    assert kinds[str(fox.ws)] == "rw" and kinds["/usr"] == "ro"
    assert "ptrace" in r["seccomp_denied"]
    assert "(deny default)" in r["seatbelt_profile"]


def test_seccomp_program_builds_for_all_arches():
    for arch in sbl.NR:
        for net in (True, False):
            for ports in (False, True):
                prog = sbl.seccomp_program(net, arch, tcp_ports=ports)
                assert len(prog) % 8 == 0 and 40 < len(prog) // 8 < 200


def test_seatbelt_profile_generation(tmp_path):
    ws = tmp_path / 'we"ird'
    ws.mkdir()
    p = sb.Policy(workspace=str(ws), network=False, read=["/opt/tools"], tmp=str(tmp_path / "t"))
    prof = macos.profile(p)
    assert prof.startswith("(version 1)\n(deny default)")
    assert '(subpath "' + str(ws.resolve()).replace('"', '\\"') + '")' in prof
    assert "(allow network*)" not in prof and "(local unix-socket)" in prof
    assert '(subpath "/opt/tools")' in prof.split("file-write*")[0]
    assert "(allow network*)" in macos.profile(sb.Policy(workspace=str(ws)))
    cmd = macos.command(p, ["node", "a.js"])
    assert cmd[:2] == ["/usr/bin/sandbox-exec", "-p"] and cmd[-2:] == ["node", "a.js"]


def test_windows_acl_plan():
    p = sb.Policy(workspace=r"C:\Users\u\FoxOS\workspace", tmp=r"C:\t", read=[r"C:\Users\u\AppData\Roaming\FoxOS\agents"])
    r = windows.icacls_plan(p, "restricted")
    assert r[0] == ["icacls", r"C:\Users\u\FoxOS\workspace", "/setintegritylevel", "(OI)(CI)low"] and len(r) == 2
    a = windows.icacls_plan(p, "appcontainer", "S-1-15-2-1")
    assert ["icacls", r"C:\Users\u\FoxOS\workspace", "/grant", "*S-1-15-2-1:(OI)(CI)F"] in a
    assert ["icacls", r"C:\Users\u\AppData\Roaming\FoxOS\agents", "/grant", "*S-1-15-2-1:(OI)(CI)RX"] in a


def test_program_paths_cover_venv_and_shebang(tmp_path):
    paths = sb.program_paths(sys.executable)
    assert any(os.path.exists(os.path.join(p, "pyvenv.cfg")) or sys.prefix.startswith(p) or p.startswith(sys.base_prefix) for p in paths)
    script = tmp_path / "bin" / "tool"
    script.parent.mkdir()
    script.write_text("#!/usr/bin/env python3\nprint(1)\n")
    script.chmod(0o755)
    got = sb.program_paths(str(script))
    assert str(tmp_path) in got


WINE = os.environ.get("FOXOS_TEST_WINE")
WINE_PY = os.environ.get("FOXOS_TEST_WINE_PYTHON")


@pytest.mark.skipif(not (WINE and WINE_PY), reason="设置 FOXOS_TEST_WINE / FOXOS_TEST_WINE_PYTHON 后在 wine 中运行 Windows 代码路径")
def test_windows_code_path_under_wine(tmp_path):
    """wine 不实现强制完整性控制与 AppContainer，这里只验证 Windows 代码路径能走通：受限令牌、作业对象、管道与退出码。"""
    import shutil
    shutil.copytree(sb.Path(sb.__file__).parents[1], tmp_path / "foxos")
    (tmp_path / "ws").mkdir()
    (tmp_path / "t.py").write_text(
        "import sys, os, json\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        "os.environ['FOXOS_HOME'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home')\n"
        "from foxos import sandbox as sb\n"
        "ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ws')\n"
        "r = sb.run(sb.Policy(workspace=ws, max_processes=8, memory_mb=512), ['cmd.exe', '/c', 'echo hi> out.txt & type out.txt & echo %FOXOS_SANDBOX%'], timeout=60)\n"
        "print(json.dumps({'code': r.returncode, 'out': r.stdout.decode()}))\n", encoding="utf-8")
    env = {**os.environ, "WINEDEBUG": "-all", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run([WINE, WINE_PY, "Z:" + str(tmp_path / "t.py").replace("/", "\\")], capture_output=True, text=True, env=env, timeout=180)
    r = json.loads(p.stdout.strip().splitlines()[-1])
    assert r["code"] == 0 and "hi" in r["out"] and "light" in r["out"], p.stdout + p.stderr
    assert (tmp_path / "ws" / "out.txt").exists()
