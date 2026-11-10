"""狐狸OS 环境（foxos env）端到端测试：真实的命名空间运行时、真实下载的 Alpine 官方 rootfs，不使用任何模拟。"""

import json
import os
import sys
from pathlib import Path

import pytest

linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux 后端（Windows / macOS 后端见单元测试）")


@pytest.fixture(scope="module")
def fxhome(tmp_path_factory):
    h = Path(os.environ.get("FOXOS_TEST_HOME") or tmp_path_factory.mktemp("fxhome"))
    return h


@pytest.fixture()
def envcli(fox, fxhome):
    cli = fox
    class C:
        def __call__(self, *a, check=0, **kw):
            return cli.run(*a, check=check, extra_env={"FOXOS_HOME": str(fxhome)}, **kw)[1]["result"]
        raw = staticmethod(lambda *a, **kw: cli.run(*a, extra_env={"FOXOS_HOME": str(fxhome)}, **kw))
    return C()


@linux_only
def test_US30_create_start_exec_stop(envcli, fox):
    cli = fox
    r = envcli("env", "create", "t30")
    assert r["env"]["image"] == "alpine-3.20"
    envcli("env", "start", "t30")
    try:
        r = envcli("env", "exec", "t30", "cat /etc/alpine-release; id -u; hostname; echo from-env > /workspace/us30.txt")
        assert r["exit_code"] == 0
        out = r["stdout"].split()
        assert out[0].startswith("3.20") and out[1] == "0" and out[2] == "t30"
        assert (cli.ws / "us30.txt").read_text().strip() == "from-env"
        st = envcli("env", "stats", "t30")["stats"]["t30"]
        assert st["state"] == "running" and st["processes"] >= 1
        assert any(e["name"] == "t30" and e["state"] == "running" for e in envcli("env", "list")["envs"])
    finally:
        envcli("env", "stop", "t30")
    assert envcli("env", "info", "t30")["state"] == "stopped"
    envcli("env", "delete", "t30")


@linux_only
def test_US31_isolation_rules(envcli, fox):
    cli = fox
    envcli("env", "create", "t31", "--network", "none", "--workspace-mode", "ro", "--memory-mb", "256", "--pids", "64")
    envcli("env", "start", "t31")
    try:
        r = envcli("env", "exec", "t31", "echo x > /workspace/blocked.txt; echo rc=$?; grep Seccomp: /proc/self/status; ulimit -v; ls /sys/class/net; ps -o pid | wc -l")
        assert "Read-only file system" in r["stderr"]
        assert not (cli.ws / "blocked.txt").exists()
        lines = r["stdout"].split("\n")
        assert "rc=1" in lines[0]
        assert "Seccomp:\t2" in r["stdout"]  # 过滤模式
        assert str(256 * 1024) in r["stdout"]
        assert "lo" in r["stdout"] and "eth0" not in r["stdout"]
        # 宿主进程不可见：只看到环境自己的进程
        r2 = envcli("env", "exec", "t31", "ls /proc | grep -c '^[0-9]'")
        assert int(r2["stdout"].strip()) < 10
        # 危险系统调用被 seccomp 拒绝（swapoff → EPERM）
        r3 = envcli("env", "exec", "t31", "swapoff -a 2>&1; echo done")
        assert "done" in r3["stdout"]
    finally:
        envcli("env", "stop", "t31")
        envcli("env", "delete", "t31")


@linux_only
def test_US32_snapshot_restore(envcli):
    envcli("env", "create", "t32")
    envcli("env", "start", "t32")
    envcli("env", "exec", "t32", "echo v1 > /root/state")
    envcli("env", "stop", "t32")
    snap = envcli("env", "snapshot", "t32", "--label", "v1")["snapshot"]["id"]
    envcli("env", "start", "t32")
    envcli("env", "exec", "t32", "echo v2 > /root/state")
    # 运行中不能快照（一致性）
    code, data, _ = envcli.raw("env", "snapshot", "t32")
    assert code == 5 and data["error"]["code"] == "LOCKED"
    envcli("env", "stop", "t32")
    envcli("env", "restore", "t32", snap)
    envcli("env", "start", "t32")
    assert envcli("env", "exec", "t32", "cat /root/state")["stdout"].strip() == "v1"
    envcli("env", "stop", "t32")
    envcli("env", "delete", "t32")


@linux_only
def test_US33_clone_export_import(envcli, fox):
    cli = fox
    envcli("env", "create", "t33")
    envcli("env", "start", "t33")
    envcli("env", "exec", "t33", "echo cloned > /root/mark")
    envcli("env", "stop", "t33")
    envcli("env", "clone", "t33", "t33b")
    exp = envcli("env", "export", "t33", "--out", "t33.foxenv")
    assert (cli.ws / "t33.foxenv").stat().st_size > 1_000_000 and len(exp["manifest"]["sha256"]) == 64
    envcli("env", "import", "t33.foxenv", "--name", "t33c")
    for n in ("t33b", "t33c"):
        envcli("env", "start", n)
        assert envcli("env", "exec", n, "cat /root/mark")["stdout"].strip() == "cloned"
        envcli("env", "stop", n)
    # 篡改镜像 → 校验失败
    import tarfile, io
    bad = cli.ws / "bad.foxenv"
    with tarfile.open(cli.ws / "t33.foxenv") as src, tarfile.open(bad, "w") as dst:
        for m in src.getmembers():
            data = src.extractfile(m).read()
            if m.name == "rootfs.tar.zst":
                data = data[:-10] + b"0123456789"
            m.size = len(data)
            dst.addfile(m, io.BytesIO(data))
    code, data, _ = envcli.raw("env", "import", "bad.foxenv", "--name", "t33d")
    assert code == 7 and data["error"]["code"] == "CONFLICT"
    for n in ("t33", "t33b", "t33c"):
        envcli("env", "delete", n)


@linux_only
def test_US34_mount_limits_actions_logs(envcli, fox, tmp_path):
    cli = fox
    host = tmp_path / "data"
    host.mkdir()
    (host / "in.txt").write_text("host-data")
    envcli("env", "create", "t34")
    envcli("env", "mount", "t34", "--source", str(host), "--target", "/data", "--readonly")
    envcli("env", "limits", "t34", "--pids", "128")
    envcli("env", "action", "add", "t34", "where", "--command", "echo ${env}:${workspace}:$(cat /data/in.txt)")
    envcli("env", "start", "t34")
    try:
        assert envcli("env", "action", "run", "t34", "where")["stdout"].strip() == "t34:/workspace:host-data"
        r = envcli("env", "exec", "t34", "touch /data/x 2>&1; ulimit -u")
        assert "Read-only" in r["stdout"] and "128" in r["stdout"]
        logs = envcli("env", "logs", "t34")["logs"]["env.log"]
        assert any("started" in l for l in logs) and any("exec" in l for l in logs)
    finally:
        envcli("env", "stop", "t34")
        envcli("env", "delete", "t34")


@linux_only
def test_US34_agent_identity_audited_and_paused(envcli, fox):
    cli = fox
    envcli("env", "create", "t34p")
    cli.run("control", "pause", agent="human:test", check=0)
    code, data, _ = envcli.raw("env", "start", "t34p")
    assert code == 8 and data["error"]["code"] == "PAUSED"
    cli.run("control", "resume", agent="human:test", check=0)
    audit = [json.loads(l) for l in (cli.ws / ".foxos" / "audit.jsonl").read_text().splitlines()]
    assert any(a["command"] == "env.create" and a["agent"] == "test-agent" for a in audit)
    envcli("env", "delete", "t34p")


def test_US35_wsl_backend_commands():
    from foxos.envs import wsl
    assert wsl.cmd_import("dev", r"C:\fx\dev", r"C:\fx\a.tar") == ["wsl.exe", "--import", "foxos-dev", r"C:\fx\dev", r"C:\fx\a.tar", "--version", "2"]
    assert wsl.cmd_exec("dev", ["uname", "-a"], "/mnt/c/ws") == ["wsl.exe", "-d", "foxos-dev", "--cd", "/mnt/c/ws", "--exec", "uname", "-a"]
    assert wsl.cmd_terminate("dev")[-1] == "foxos-dev" and wsl.cmd_export("dev", "o.tar")[1] == "--export"
    assert wsl.win_to_wsl_path(r"C:\Users\fox\Work Space") == "/mnt/c/Users/fox/Work Space"
    text = "  NAME            STATE           VERSION\n* Ubuntu          Running         2\n  foxos-dev       Stopped         2\n"
    parsed = wsl.parse_list_verbose(text.encode("utf-16-le").decode("utf-16-le"))
    assert parsed["foxos-dev"] == {"default": False, "state": "stopped", "version": 2} and parsed["Ubuntu"]["default"]


def test_US36_macos_vz_config(tmp_path):
    from foxos.envs import macos
    cfg = macos.vm_config("dev", tmp_path, tmp_path / "ws", cpus=0, memory_mb=1024)
    assert cfg["cpus"] == 1 and cfg["memoryBytes"] == 1024 ** 3 and cfg["shares"][0]["tag"] == "workspace"
    p = macos.write_config(cfg, tmp_path / "vm.json")
    assert json.loads(p.read_text())["disk"].endswith("rootfs.img")
    assert macos.helper_cmd("/opt/foxos-vz", p) == ["/opt/foxos-vz", "run", "--config", str(p)]
    swift = (Path(__file__).resolve().parents[1] / "foxos" / "data" / "macos" / "FoxVZ.swift").read_text()
    assert "VZLinuxBootLoader" in swift and "VZVirtioFileSystemDeviceConfiguration" in swift
