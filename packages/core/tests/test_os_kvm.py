"""US-61：linux-kvm 提供者、foxos env run / desktop-attach。默认不引导 1.4 GiB ISO。"""

from __future__ import annotations

import os
from pathlib import Path

from foxos.envs import kvm, providers as P


def test_US61_linux_kvm_is_a_builtin_provider(fox, fxhome=None):
    ids = {p.id for p in P.BUILTIN}
    assert "linux-kvm" in ids
    d = P.get("linux-kvm").doctor()
    assert "checks" in d and "kvm" in {c["id"] for c in d["checks"]}
    # 此构建盒是 KVM 来宾，/dev/kvm 往往存在但创建 vCPU 会触发内核 BUG。
    probe = kvm.kvm_probe()
    assert probe["device"] == "/dev/kvm"
    reason = probe["reason"] or ""
    if os.environ.get("FOXOS_KVM") == "0":
        assert probe["available"] is False
        assert "FOXOS_KVM" in reason
    elif probe["known_broken"]:
        assert probe["available"] is False
        # kvm_probe 先报告缺设备 / 无读写权限，只有设备可用时才报告内核 BUG。
        if probe["exists"] and probe["writable"]:
            assert "kvm_arch_vcpu_create" in reason


def test_US61_env_run_and_desktop_attach_verbs(fox, tmp_path):
    iso = tmp_path / "guest.iso"
    iso.write_bytes(b"ISO")  # 占位文件，只创建不启动
    home = tmp_path / "fxhome"
    env = {"FOXOS_HOME": str(home)}
    r = fox.run("env", "run", "live", "--provider", "linux-kvm", "--iso", str(iso), "--no-start", extra_env=env, check=0)[1]["result"]
    assert r["env"]["provider"] == "linux-kvm" and r["env"]["state"] == "stopped"
    listed = fox.run("env", "list", extra_env=env, check=0)[1]["result"]
    assert any(e["name"] == "live" and e["provider"] == "linux-kvm" for e in listed["envs"])
    # 未启动时 attach 应失败
    code, out, _ = fox.run("env", "desktop-attach", "live", extra_env=env)
    assert code == 6 and out["error"]["code"] == "DEPENDENCY_MISSING"
    # 未允许测试 VMM 且 KVM 不可用时，start 必须说明原因，不得悄悄用 QEMU
    probe = kvm.kvm_probe()
    if not probe["available"]:
        env2 = {**env}
        env2.pop("FOXOS_ALLOW_TEST_VMM", None)
        code, out, _ = fox.run("env", "start", "live", extra_env=env2)
        assert code == 6 and out["error"]["code"] == "DEPENDENCY_MISSING"
    fox.run("env", "delete", "live", extra_env=env, check=0)


def test_US61_catalog_lists_linux_kvm_for_linux_guests():
    alpine = next(e for e in P.catalog()["entries"] if e["id"] == "alpine")
    assert "linux-kvm" in alpine["providers"] and "linux-ns" in alpine["providers"]


def test_US61_mcp_exposes_env_run_and_desktop_attach(fox):
    cat = fox.run("help", check=0)[1]
    env = next(a for a in cat["apps"] if a["name"] == "env")
    ids = {c["id"] for c in env["commands"]}
    assert "env.run" in ids and "env.desktop-attach" in ids
