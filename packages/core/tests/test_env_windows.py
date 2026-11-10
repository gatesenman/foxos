"""US-50 Windows 环境：一键安装系统目录、提供者协议、WSL / Windows Sandbox / Hyper-V 命令契约（可在 Linux 上运行的单元测试）。

真机端到端（Windows 硬件）见 test_env_windows_hw 中标记为 pending 的用例与 docs/windows-test-guide.md。
"""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from foxos.envs import providers as P
from foxos.envs import wsl

FX = Path(__file__).parent / "fixtures" / "windows"


def fx(name: str) -> str:
    return P.decode_wsl((FX / name).read_bytes())


def fetch_fixture(url: str) -> str:
    if url.endswith("/meta/1.0/index-system"):
        return (FX / "lxc-index-system.txt").read_text()
    if url.endswith("SHA256SUMS"):
        return (FX / "lxc-oracle-9-SHA256SUMS").read_text()
    if url.endswith("latest-releases.yaml"):
        return (FX / "alpine-latest-releases.yaml").read_text()
    if url.endswith(".CHECKSUM"):
        return (FX / "rocky-9-CHECKSUM").read_text()
    raise AssertionError(url)


# ---------------------------------------------------------------- 目录
def test_catalog_format_and_required_systems():
    c = P.catalog()
    assert c["format"] == "foxos-env-catalog/1"
    ids = {e["id"] for e in c["entries"]}
    required = {"wsl-ubuntu-20.04", "wsl-ubuntu-22.04", "wsl-ubuntu-24.04", "wsl-debian", "wsl-kali-linux", "wsl-opensuse-tumbleweed", "wsl-opensuse-leap-16.1",
                "wsl-fedoralinux-45", "wsl-almalinux-9", "rocky-9", "wsl-oraclelinux-9-5", "lxc-oracle-9", "wsl-archlinux", "alpine", "custom-rootfs",
                "windows-sandbox", "hyperv-windows-11-eval", "hyperv-custom-iso", "macos-guest"}
    assert required <= ids, required - ids
    for e in c["entries"]:
        assert e["providers"] and e["guest_os"] in ("linux", "windows", "macos", "any")
        if e["source"]["kind"] == "rootfs" and e["source"].get("origin", "").startswith("microsoft/WSL"):
            assert e["source"]["url"].startswith("https://") and len(e["source"]["sha256"]) == 64
    mac = next(e for e in c["entries"] if e["id"] == "macos-guest")
    assert mac["disabled"] and "Apple" in mac["reason"]


def test_catalog_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((P.DATA / "schemas" / "env-catalog.schema.json").read_text())
    jsonschema.validate(P.catalog(), schema)
    pschema = json.loads((P.DATA / "schemas" / "env-provider.schema.json").read_text())
    for p in P.BUILTIN:
        jsonschema.validate(p.describe(), {"$ref": "#/$defs/describe", "$defs": pschema["$defs"]})


def test_catalog_generator_is_in_sync():
    root = Path(__file__).resolve().parents[3]
    before = (P.DATA / "env-catalog.json").read_text()
    subprocess.run([sys.executable, str(root / "scripts" / "gen_env_catalog.py")], check=True, capture_output=True)
    after = json.loads((P.DATA / "env-catalog.json").read_text())
    assert [e["id"] for e in after["entries"]] == [e["id"] for e in json.loads(before)["entries"]]
    (P.DATA / "env-catalog.json").write_text(before)


# ---------------------------------------------------------------- wsl.exe 输出解析
def test_decode_utf16_and_utf8():
    assert P.decode_wsl("默认版本: 2".encode("utf-16-le")) == "默认版本: 2"
    assert P.decode_wsl(b"Default Version: 2") == "Default Version: 2"


@pytest.mark.parametrize("name,code,installed,reboot,missing,novirt,ver", [
    ("wsl-status-ok.en.txt", 0, True, False, False, False, 2),
    ("wsl-status-ok.zh.txt", 0, True, False, False, False, 2),
    ("wsl-status-missing.en.txt", 1, False, False, True, False, None),
    ("wsl-status-missing.zh.txt", 1, False, False, True, False, None),
    ("wsl-status-oc-required.en.txt", 1, False, True, True, False, None),
    ("wsl-status-novirt.zh.txt", 1, False, False, False, True, None),
])
def test_parse_wsl_status(name, code, installed, reboot, missing, novirt, ver):
    st = P.parse_wsl_status(code, fx(name))
    assert (st["installed"], st["needs_reboot"], st["missing_component"], st["virtualization_disabled"], st["default_version"]) == (installed, reboot, missing, novirt, ver)


def test_parse_wsl_status_default_distro():
    assert P.parse_wsl_status(0, fx("wsl-status-ok.zh.txt"))["default_distro"] == "Ubuntu-24.04"


def test_reboot_detection_does_not_confuse_restart_wsl():
    assert P.is_reboot_required(3010, "")
    assert P.is_reboot_required(0, fx("wsl-status-oc-required.en.txt"))
    assert not P.is_reboot_required(0, "An Http Proxy change has been detected on the host. Please restart WSL to apply the change.")


def test_parse_list_online_matches_catalog_names():
    rows = P.parse_wsl_online(fx("wsl-list-online.en.txt"))
    names = {r["name"] for r in rows}
    assert {"Ubuntu-24.04", "Debian", "kali-linux", "OracleLinux_9_5", "archlinux"} <= names
    cat = {e["source"].get("wsl_name") for e in P.catalog()["entries"]}
    assert names - {"Ubuntu"} <= cat


def test_parse_list_verbose():
    v = wsl.parse_list_verbose(fx("wsl-list-verbose.en.txt"))
    assert v["Ubuntu-24.04"] == {"default": True, "state": "running", "version": 2}
    assert v["OracleLinux_9_5"]["state"] == "stopped"


# ---------------------------------------------------------------- 来源解析（录下的服务器响应）
def test_resolve_lxc_latest_build():
    src = P.resolve_source(P.entry("lxc-oracle-9"), fetch=fetch_fixture)
    assert src["url"].startswith("https://images.linuxcontainers.org/images/oracle/9/amd64/default/") and src["url"].endswith("/rootfs.tar.xz")
    assert len(src["sha256"]) == 64 and src["format"] == "tar.xz" and src["wsl_import_needs_convert"]


def test_resolve_alpine_and_rocky_checksum():
    a = P.resolve_source(P.entry("alpine"), fetch=fetch_fixture)
    assert "alpine-minirootfs-" in a["url"] and len(a["sha256"]) == 64 and a["format"] == "tar.gz"
    r = P.resolve_source(P.entry("rocky-9"), fetch=fetch_fixture)
    assert r["sha256"] == "58de2455cd475abbaa3cef0f9d240f405c379b5a54d3826f9b55cc41e3829221"


def test_resolve_custom_requires_url():
    with pytest.raises(Exception):
        P.resolve_source(P.entry("custom-rootfs"), {})
    s = P.resolve_source(P.entry("custom-rootfs"), {"url": r"D:\images\my.tar", "sha256": "ab" * 32})
    assert s["format"] == "tar" and not s["wsl_import_needs_convert"]


# ---------------------------------------------------------------- 命令契约
def test_wsl_install_plan_import(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\fox\AppData\Local")
    e = P.entry("wsl-ubuntu-24.04")
    src = P.resolve_source(e, fetch=fetch_fixture)
    steps = P.Wsl2().plan_install(e, "ubuntu", {"_resolved": src})
    dl, imp, chk = steps
    assert dl["download"] == "https://releases.ubuntu.com/24.04.5/ubuntu-24.04.5-wsl-amd64.wsl" and len(dl["sha256"]) == 64 and "convert" not in dl
    assert imp["argv"][:3] == ["wsl.exe", "--import", "foxos-ubuntu"] and imp["argv"][-2:] == ["--version", "2"]
    assert imp["argv"][4].endswith("ubuntu-24.04.5-wsl-amd64.wsl") and imp["registers"] == "foxos-ubuntu"
    assert chk["argv"][:3] == ["wsl.exe", "-d", "foxos-ubuntu"]


def test_wsl_install_plan_lxc_converts_xz():
    e = P.entry("lxc-oracle-9")
    src = P.resolve_source(e, fetch=fetch_fixture)
    dl, imp, _ = P.Wsl2().plan_install(e, "ol9", {"_resolved": src, "location": r"D:\fox\ol9"})
    assert dl["convert"] == "tar.gz" and imp["argv"][4] == os.path.join(r"D:\fox\ol9", "rootfs.tar.gz")


def test_wsl_install_plan_store_only():
    steps = P.Wsl2().plan_install(P.entry("wsl-oraclelinux-9-5"), "ol", {})
    assert steps == [{"argv": ["wsl.exe", "--install", "-d", "OracleLinux_9_5", "--no-launch"], "why": steps[0]["why"], "registers": "OracleLinux_9_5"}]


def test_wsl_enable_action_and_elevation():
    argv = P.step_argv({"argv": ["wsl.exe", "--install", "--no-distribution"], "elevate": True})
    assert argv[0] == "powershell.exe" and "Start-Process -FilePath 'wsl.exe' -ArgumentList '--install','--no-distribution' -Verb RunAs -Wait -PassThru" in argv[-1]
    assert argv[-1].endswith("exit $p.ExitCode")
    ps = P.step_argv({"powershell": "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -All -NoRestart", "elevate": True})
    assert "-Verb RunAs" in ps[-1] and "Microsoft-Hyper-V-All" in ps[-1]


def test_wsb_generation():
    xml = P.wsb_xml(r"C:\Users\fox\FoxOS\workspace", networking=False, memory_mb=4096, readonly=True, logon_command="explorer.exe C:\\Users\\WDAGUtilityAccount\\Desktop\\workspace")
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    assert root.tag == "Configuration" and root.findtext("Networking") == "Disable" and root.findtext("MemoryInMB") == "4096"
    mf = root.find("MappedFolders/MappedFolder")
    assert mf.findtext("HostFolder") == r"C:\Users\fox\FoxOS\workspace" and mf.findtext("ReadOnly") == "true"
    assert root.findtext("LogonCommand/Command").startswith("explorer.exe")
    steps = P.WindowsSandbox().plan_install(P.entry("windows-sandbox"), "sb", {"location": r"C:\fx", "workspace": r"C:\ws"})
    assert steps[0]["write"].endswith("sb.wsb") and steps[1]["argv"][:3] == ["cmd.exe", "/c", "start"]


def test_hyperv_plan_cmdlets():
    with pytest.raises(Exception) as ei:
        P.HyperV().plan_install(P.entry("hyperv-windows-11-eval"), "win11", {})
    assert "iso" in str(ei.value).lower()
    steps = P.HyperV().plan_install(P.entry("hyperv-windows-11-eval"), "win11", {"iso": r"D:\iso\Win11_Eval.iso", "memory_mb": 8192, "cpus": 4, "disk_gb": 80, "location": r"D:\vms\win11"})
    ps = steps[0]["powershell"]
    assert steps[0]["elevate"]
    assert "New-VM -Name 'foxos-win11' -Generation 2 -MemoryStartupBytes 8589934592" in ps and "-NewVHDSizeBytes 85899345920" in ps
    assert "Set-VMProcessor -VMName 'foxos-win11' -Count 4" in ps and "Add-VMDvdDrive -VMName 'foxos-win11' -Path 'D:\\iso\\Win11_Eval.iso'" in ps
    assert "Enable-VMTPM" in ps and "Start-VM -Name 'foxos-win11'" in ps
    assert steps[1]["argv"] == ["vmconnect.exe", "localhost", "foxos-win11"]
    ps2 = P.HyperV().plan_install(P.entry("hyperv-custom-iso"), "lin", {"iso": r"D:\a'b.iso"})[0]["powershell"]
    assert "-EnableSecureBoot Off" in ps2 and "'D:\\a''b.iso'" in ps2 and "Enable-VMTPM" not in ps2


def test_edition_detection():
    assert not P.edition_supports_hyperv("Core") and not P.edition_supports_hyperv("CoreSingleLanguage")
    assert P.edition_supports_hyperv("Professional") and P.edition_supports_hyperv("Enterprise") and P.edition_supports_hyperv("Education")


def test_wsl_cwd_mapping():
    cfg = {"name": "u", "wsl_distro": "foxos-u", "workspace": {"path": r"C:\Users\fox\FoxOS\workspace"}}
    assert wsl.map_cwd("/workspace/src", cfg) == "/mnt/c/Users/fox/FoxOS/workspace/src"
    assert wsl.cmd_exec_d("OracleLinux_9_5", ["ls"], "/tmp") == ["wsl.exe", "-d", "OracleLinux_9_5", "--cd", "/tmp", "--exec", "ls"]


# ---------------------------------------------------------------- 提供者协议
def test_builtin_providers_describe():
    ids = {p.id for p in P.BUILTIN}
    assert {"linux-ns", "wsl2", "windows-sandbox", "hyperv", "macos-vz", "macos-guest"} <= ids
    for p in P.BUILTIN:
        d = p.describe()
        assert d["protocol"] == P.PROTOCOL and d["platforms"]


def test_external_provider_jsonrpc(tmp_path, monkeypatch):
    home = tmp_path / "home"
    pd = home / "providers" / "demo"
    pd.mkdir(parents=True)
    (pd / "demo.py").write_text(textwrap.dedent('''
        import json, sys
        for line in sys.stdin:
            m = json.loads(line)
            if m["method"] == "initialize":
                r = {"protocol": "foxos-env-provider/1", "id": "demo"}
            elif m["method"] == "doctor":
                r = {"available": True, "reason": None, "checks": [{"id": "demo", "ok": True, "detail": "ok"}], "actions": []}
            elif m["method"] == "plan_install":
                r = {"steps": [{"argv": ["demo-vm", "create", m["params"]["name"]], "why": "demo"}]}
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": m["id"], "error": {"code": -32601, "message": "no such method"}})); continue
            print(json.dumps({"jsonrpc": "2.0", "id": m["id"], "result": r}))
    '''))
    (pd / "provider.json").write_text(json.dumps({"protocol": "foxos-env-provider/1", "id": "demo", "name": "Demo", "platforms": ["linux", "windows", "macos"],
                                                  "capabilities": ["create"], "command": [sys.executable, str(pd / "demo.py")]}))
    monkeypatch.setenv("FOXOS_HOME", str(home))
    p = P.get("demo")
    assert isinstance(p, P.ExternalProvider) and p.describe()["builtin"] is False
    assert p.doctor()["available"]
    assert p.plan_install({"id": "x"}, "vm1", {})[0]["argv"] == ["demo-vm", "create", "vm1"]
    with pytest.raises(Exception):
        p.call("nope")


def test_cli_catalog_and_dry_run(fox, tmp_path):
    env = {"FOXOS_HOME": str(tmp_path / "home")}
    _, r, _ = fox.run("env", "catalog", "--guest", "windows", check=0, extra_env=env)
    ents = r["result"]["entries"]
    assert "windows-sandbox" in [e["id"] for e in ents] and all(e["guest_os"] == "windows" for e in ents)
    _, r, _ = fox.run("env", "install", "wsl-oraclelinux-9-5", "ol", "--provider", "wsl2", "--dry-run", check=0, extra_env=env)
    assert r["result"]["plan"]["steps"][0]["argv"][:4] == ["wsl.exe", "--install", "-d", "OracleLinux_9_5"]
    _, r, _ = fox.run("env", "install", "macos-guest", "m", check=6, extra_env=env)
    assert r["error"]["code"] == "DEPENDENCY_MISSING"
    if sys.platform != "win32":
        _, r, _ = fox.run("env", "install", "wsl-oraclelinux-9-5", "ol", "--provider", "wsl2", check=6, extra_env=env)
        assert "dry-run" in json.dumps(r, ensure_ascii=False)
    _, r, _ = fox.run("env", "providers", check=0, extra_env=env)
    assert {p["id"] for p in r["result"]["providers"]} >= {"wsl2", "hyperv", "windows-sandbox", "linux-ns"}


# ---------------------------------------------------------------- 真机（Windows 硬件）——待验证
pytestmark_hw = pytest.mark.skipif(sys.platform != "win32", reason="pending：需要 Windows 实机（见 docs/windows-test-guide.md）")


@pytestmark_hw
def test_hw_wsl_install_ubuntu(fox):  # pragma: no cover
    fox.run("env", "install", "wsl-ubuntu-24.04", "hwtest", check=0, timeout=3600)
    _, r, _ = fox.run("env", "exec", "hwtest", "--", "cat", "/etc/os-release", check=0)
    assert "Ubuntu" in r["result"]["stdout"]
    fox.run("env", "delete", "hwtest", check=0)


@pytestmark_hw
def test_hw_doctor(fox):  # pragma: no cover
    _, r, _ = fox.run("env", "doctor", check=0)
    assert "wsl2" in r["result"]["results"]
