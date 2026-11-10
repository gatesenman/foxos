"""工作空间约束：拒绝越界路径，且拒绝也写入审计日志。"""

import os

import pytest

from foxos.errors import FoxError
from foxos.workspace import Workspace


@pytest.mark.parametrize("bad", ["../escape.xlsx", "a/../../escape.xlsx", "/tmp/foxos-escape-abs.xlsx"])
def test_cli_rejects_paths_outside_workspace(fox, ws, bad):
    code, out, _ = fox.run("sheets", "create", bad)
    assert code == 4
    assert out["error"]["code"] == "PERMISSION_DENIED"
    assert not (ws.parent / "escape.xlsx").exists()
    assert not os.path.exists("/tmp/foxos-escape-abs.xlsx")
    last = fox.audit()[-1]
    assert last["status"] == "denied" and last["command"] == "sheets.create"
    assert last["error"]["code"] == "PERMISSION_DENIED" and last["args"]["file"] == bad


def test_export_output_outside_workspace_denied(fox, ws):
    fox.run("sheets", "create", "ok.xlsx", check=0)
    code, out, _ = fox.run("sheets", "export", "ok.xlsx", "../leak.csv")
    assert code == 4
    assert not (ws.parent / "leak.csv").exists()


@pytest.mark.skipif(os.name != "posix", reason="符号链接测试只在 POSIX 上跑")
def test_symlink_escape_rejected(fox, ws, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (ws / "link").symlink_to(outside, target_is_directory=True)
    code, out, _ = fox.run("sheets", "create", "link/evil.xlsx")
    assert code == 4
    assert not (outside / "evil.xlsx").exists()


def test_reserved_dir_rejected(fox, ws):
    code, out, _ = fox.run("sheets", "read", ".foxos/audit.jsonl")
    assert code == 4 and "保留目录" in out["error"]["message"]
    code, out, _ = fox.run("sheets", "create", "sub/../.foxos/x.xlsx")
    assert code == 4


def test_absolute_path_inside_workspace_allowed(fox, ws):
    fox.run("sheets", "create", str(ws / "abs.xlsx"), check=0)
    assert (ws / "abs.xlsx").exists()


def test_resolve_unit(tmp_path):
    w = Workspace(tmp_path / "w")
    assert w.resolve("a/b.xlsx") == (tmp_path / "w" / "a" / "b.xlsx").resolve()
    for bad in ["..", "../x", "/", ""]:
        with pytest.raises(FoxError):
            w.resolve(bad)
