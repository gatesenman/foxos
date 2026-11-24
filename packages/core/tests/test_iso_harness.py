"""ISO 测试器的单元回归。不启动虚拟机，不替代 ISO 的实测结果。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def harness():
    source = Path(__file__).resolve().parents[3] / "scripts/os/e2e/iso_e2e.py"
    spec = importlib.util.spec_from_file_location("iso_harness_test", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_semantic_case_never_reads_model_secret(harness, monkeypatch, tmp_path):
    commands = []
    monkeypatch.setattr(harness, "WORK", tmp_path)
    monkeypatch.setattr(harness, "SECRET_FILE", tmp_path / "nonexistent-secret")
    monkeypatch.setattr(harness, "ssh_base", lambda: ["ssh"])
    monkeypatch.setattr(harness.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0, stderr=b""))

    def ssh(cmd, **kw):
        commands.append(cmd)
        return SimpleNamespace(stdout="PASSED tests/test_cu_gui.py::edit\n2 passed\n")

    monkeypatch.setattr(harness, "ssh", ssh)
    result = harness.case_cu(semantic_only=True)
    assert "2 passed" in result
    command = commands[-1]
    assert "PYTHONPATH=/tmp/cu-pt:/usr/lib/foxos/python" in command
    assert "FOXOS_CU_GUI=1" in command and "test_cu_gui.py" in command
    assert "DEEPSEEK_API_KEY" not in command and "TYPESAFE_API_KEY" not in command
    assert not harness._SECRETS


def test_boot_defaults_to_tcg_even_when_kvm_looks_accessible(harness, monkeypatch, tmp_path):
    monkeypatch.delenv("FOXOS_E2E_ACCEL", raising=False)
    monkeypatch.setattr(harness, "WORK", tmp_path)
    monkeypatch.setattr(harness, "STATE", tmp_path / "vm.json")
    monkeypatch.setattr(harness, "stop", lambda: None)
    monkeypatch.setattr(harness, "make_seed", lambda: tmp_path / "seed.iso")
    vars_fd = tmp_path / "vars.fd"
    vars_fd.write_bytes(b"test")
    monkeypatch.setattr(harness.os, "access", lambda *a: True)
    commands = []
    monkeypatch.setattr(harness.subprocess, "run", lambda cmd, **kw: commands.append(cmd))
    state = harness.boot("final.iso", False, 1024, 1)
    qemu = commands[-1]
    assert state["accel"] == "tcg"
    assert qemu[qemu.index("-accel") + 1] == "tcg,tb-size=256"
    assert qemu[qemu.index("-cpu") + 1] == "max"
