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
    assert all("x11-apps" not in cmd for cmd in commands)
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


def test_storage_preflight_uses_resolved_disk_destinations(harness, monkeypatch, tmp_path):
    work = tmp_path / 'metadata'; work.mkdir()
    disk = tmp_path / 'artifact-mount'; disk.mkdir()
    (disk / 'target').touch()
    (work / 'target.qcow2').symlink_to(disk / 'target')
    monkeypatch.setattr(harness, 'WORK', work)
    checked = []
    def usage(path):
        checked.append(Path(path))
        return SimpleNamespace(free=100 * 1024**3)
    monkeypatch.setattr(harness.shutil, 'disk_usage', usage)
    harness.storage_preflight()
    assert disk / 'target' in checked and work in checked
    assert Path('/') not in checked


def test_storage_preflight_refuses_before_qemu(harness, monkeypatch, tmp_path):
    monkeypatch.setattr(harness, 'WORK', tmp_path)
    monkeypatch.setattr(harness.shutil, 'disk_usage', lambda path: SimpleNamespace(free=0))
    with pytest.raises(RuntimeError, match='Insufficient artifact storage'):
        harness.boot('candidate.iso', False, 1024, 1)
    assert not (tmp_path / 'qemu.pid').exists()


def test_existing_guest_is_not_restarted(harness, monkeypatch):
    monkeypatch.setattr(harness, 'guest_running', lambda: True)
    with pytest.raises(RuntimeError, match='Existing VM'):
        harness.boot('candidate.iso', False, 1024, 1)


def test_installed_boot_never_attaches_key_seed(harness, monkeypatch, tmp_path):
    monkeypatch.setattr(harness, 'WORK', tmp_path)
    monkeypatch.setattr(harness, 'STATE', tmp_path / 'vm.json')
    (tmp_path / 'vars.fd').write_bytes(b'fixture')
    monkeypatch.setattr(harness, 'make_seed', lambda: pytest.fail('installed boot must not create seed'))
    calls = []
    monkeypatch.setattr(harness.subprocess, 'run', lambda args, **kw: calls.append(args))
    harness.boot(None, True, 1024, 1)
    assert not any('media=cdrom' in arg or 'ide-cd' in arg for arg in calls[-1])
    assert 'chardev:serial0' in calls[-1]


@pytest.mark.parametrize('blocks,accepted', [([], True), ([{'removable': True}], True),
    ([{'removable': True, 'inserted': {'file': 'seed.iso'}}], False),
    ([{'removable': False, 'inserted': {'file': 'target.qcow2'}}], True)])
def test_empty_optical_hardware_is_not_inserted_media(harness, blocks, accepted):
    if accepted:
        harness.assert_no_optical_media(blocks)
    else:
        with pytest.raises(AssertionError): harness.assert_no_optical_media(blocks)


@pytest.mark.parametrize('text,phase', [('healthy', 'no-errors'),
    ('SQUASHFS error\nPlease remove the installation medium', 'before-removal-prompt'),
    ('Please remove the installation medium\nSQUASHFS error', 'after-removal-prompt')])
def test_squashfs_error_timing_is_not_hidden(harness, text, phase):
    assert harness.squashfs_phase(text) == phase


def test_installed_admin_uses_stdin_without_exposing_fixture(harness, monkeypatch):
    monkeypatch.setattr(harness, 'state', lambda: {'from_disk': True})
    monkeypatch.setattr(harness, 'INSTALL_PW', 'temporary-fixture-only')
    calls = []
    monkeypatch.setattr(harness, 'ssh', lambda cmd, **kw: calls.append((cmd, kw)))
    harness.admin('id -u')
    command, options = calls[0]
    assert 'temporary-fixture-only' not in command
    assert options['input'] == 'temporary-fixture-only\n'
    assert harness.scrub('temporary-fixture-only') == '***'


def test_disconnect_does_not_replay_mutating_ssh(harness, monkeypatch):
    monkeypatch.setattr(harness, 'ssh_base', lambda *a: ['ssh'])
    calls = []
    def run(*a, **kw):
        calls.append(a); return SimpleNamespace(returncode=255, stdout='', stderr='disconnected')
    monkeypatch.setattr(harness.subprocess, 'run', run)
    harness.ssh('sudo systemctl reboot')
    assert len(calls) == 1


def test_browser_checks_observed_document_not_body_title(harness):
    document = {'url': 'https://example.com/', 'title': 'Example Domain',
                'backend': 'agent-browser@0.42.0', 'refs': 1,
                'snapshot': 'This domain is for use in documentation examples\n- link "Learn more" [ref=e1]'}
    harness.assert_browser_document(document)
    for changed in ({'snapshot': ''}, {'url': 'https://wrong.example/'}, {'backend': 'builtin'}, {'refs': 0}):
        with pytest.raises(AssertionError): harness.assert_browser_document(document | changed)
