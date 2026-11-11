"""US-63：在线选择并安装狐狸OS 预设系统（Linux / Windows / macOS），可续传下载、逐卷校验、主机可用性说明。

默认只跑不需要网络与虚拟机的用例。真实下载 + 校验 + 引导：FOXOS_PRESET_E2E=1（Linux 主机；KVM 坏时再加 FOXOS_ALLOW_TEST_VMM=qemu-tcg）。
"""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import shutil
import threading
import xml.dom.minidom
from pathlib import Path

import pytest

from foxos.envs import download, presets, providers
from foxos.errors import FoxError


def test_US63_catalog_lists_presets_with_sizes_and_reasons(fox):
    r = fox.run("env", "catalog", "--presets", check=0)[1]["result"]
    ids = {e["id"]: e for e in r["entries"]}
    assert r["presets"] == len(ids) >= 4
    win = ids["windows-11-enterprise-eval"]
    assert win["kind"] == "windows-media" and win["media"]["url"].startswith("https://go.microsoft.com/")
    assert win["download_bytes"] > 4 * 1024 ** 3 and win["disk_bytes"] > win["download_bytes"]
    mac = ids["macos-latest"]
    assert "Apple" in (mac.get("reason") or mac["unavailable"]["linux"]) and mac["hosts"] == {"macos": {"provider": "macos-vz", "arch": ["aarch64"]}}
    linux = [e for e in r["entries"] if e["kind"] in ("foxos-image", "foxos-iso")]
    assert linux, "至少一个 Linux 预设"
    for e in linux:
        art = e["artifacts"][e["hosts"]["linux"]["artifact"]]
        assert art["sha256"] and art["size"] == sum(p["size"] for p in art.get("parts", [])) if art.get("parts") else art["size"]
        assert all(p["url"].startswith("https://github.com/gatesenman/foxos/releases/download/") for p in art.get("parts", []))
        assert e["download_bytes"] == art["size"] and e["disk_bytes"] > art["size"]
    # 同一套命令在 MCP 里也有
    from foxos import catalog as cmdcat
    names = {t["name"] for t in cmdcat.mcp_tools("full", None)}
    assert {"env_catalog", "env_install", "env_progress"} <= names, sorted(n for n in names if n.startswith("env"))


def test_US63_host_targets_windows_and_macos_rules():
    w = presets.get("windows-11-enterprise-eval")
    assert presets.target(w, "windows", "x86_64") == {"provider": "hyperv", "artifact": None, "available": True, "reason": None}
    t = presets.target(w, "linux", "x86_64")
    assert not t["available"] and "cloud-hypervisor" in t["reason"]
    m = presets.get("macos-latest")
    assert presets.target(m, "macos", "aarch64")["available"]
    assert not presets.target(m, "macos", "x86_64")["available"]           # Intel Mac：IPSW 虚拟化只在 Apple 芯片
    for h in ("linux", "windows"):
        assert "Apple" in presets.target(m, h)["reason"]
    deb = next(e for e in presets.entries() if e["kind"] == "foxos-image")
    assert presets.target(deb, "linux", "x86_64")["provider"] == "linux-kvm"
    assert presets.target(deb, "windows", "x86_64") == {"provider": "wsl2", "artifact": "wsl", "available": True, "reason": None}


def test_US63_windows_preset_answer_file_and_hyperv_plan(tmp_path):
    w = presets.get("windows-11-enterprise-eval")
    info = presets.windows_seed(w, tmp_path / "seed", name="win11", product_key="AAAAA-BBBBB-CCCCC-DDDDD-EEEEE", ssh_pub="ssh-ed25519 AAAA test")
    xml_text = (tmp_path / "seed" / "autounattend.xml").read_text(encoding="utf-8")
    doc = xml.dom.minidom.parseString(xml_text.encode("utf-8"))             # 合法 XML
    assert doc.getElementsByTagName("UILanguage")[0].firstChild.data == "zh-CN"
    assert "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE" in xml_text and info["product_key"]
    assert "FOXOSSEED" in xml_text and "postinstall.ps1" in xml_text
    seed = json.loads((tmp_path / "seed" / "foxos" / "seed.json").read_text(encoding="utf-8"))
    assert seed["ssh_authorized_key"].startswith("ssh-ed25519") and seed["node_version"].startswith("v")
    ps = (tmp_path / "seed" / "foxos" / "postinstall.ps1").read_text(encoding="utf-8")
    for needle in ("nodejs.org/dist", "python.org/ftp/python", "bun.sh/install.ps1", "@google/gemini-cli", "OpenSSH.Server", "FOXOS-PRESET-READY"):
        assert needle in ps
    # 不填密钥（评估版）：应答文件里没有 ProductKey
    presets.windows_seed(w, tmp_path / "seed2", name="w", product_key=None, ssh_pub=None)
    assert "<ProductKey>" not in (tmp_path / "seed2" / "autounattend.xml").read_text(encoding="utf-8")
    steps = providers.HyperV().plan_install({**w, "tpm": True}, "win11", {"iso": r"C:\iso\w.iso", "seed_iso": r"C:\FoxOS\seed.iso", "disk_gb": 64})
    ps_plan = steps[0]["powershell"]
    assert ps_plan.count("Add-VMDvdDrive") == 2 and "seed.iso" in ps_plan and "Enable-VMTPM" in ps_plan and "Msvm_Keyboard" in ps_plan
    assert "IMAPI2FS" in presets.ps_seed_iso(r"C:\x\seed", r"C:\x\seed.iso")


class _RangeHandler(http.server.BaseHTTPRequestHandler):
    data = b""
    drop_first = True
    hits: list = []

    def log_message(self, *a):  # noqa: D401
        pass

    def do_GET(self):  # noqa: N802
        rng = self.headers.get("Range")
        start = int(rng.split("=")[1].split("-")[0]) if rng else 0
        type(self).hits.append(start)
        body = self.data[start:]
        self.send_response(206 if rng else 200)
        self.send_header("Content-Length", str(len(body)))
        if rng:
            self.send_header("Content-Range", f"bytes {start}-{len(self.data) - 1}/{len(self.data)}")
        self.end_headers()
        if type(self).drop_first:
            type(self).drop_first = False
            self.wfile.write(body[: len(body) // 3])   # 模拟断线
            self.wfile.flush()
            self.connection.shutdown(2)
            return
        self.wfile.write(body)


@pytest.fixture()
def range_server():
    _RangeHandler.data = os.urandom(3 * 1024 * 1024 + 123)
    _RangeHandler.drop_first = True
    _RangeHandler.hits = []
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _RangeHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    yield srv, _RangeHandler
    srv.shutdown()


def test_US63_download_resumes_after_disconnect_and_verifies(range_server, tmp_path):
    srv, h = range_server
    url = f"http://127.0.0.1:{srv.server_address[1]}/part1"
    sha = hashlib.sha256(h.data).hexdigest()
    seen = []
    r = download.fetch(url, tmp_path / "p1", size=len(h.data), sha256=sha, progress=lambda **k: seen.append(k), retries=3)
    assert r["verified"] and r["resumed"] >= 1 and r["sha256"] == sha
    assert h.hits[0] == 0 and h.hits[1] > 0                                  # 第二次请求从断点继续（Range）
    assert (tmp_path / "p1").read_bytes() == h.data and not (tmp_path / "p1.partial").exists()
    assert seen[-1]["bytes"] == len(h.data)
    # 已有且校验一致：直接复用
    assert download.fetch(url, tmp_path / "p1", size=len(h.data), sha256=sha)["cached"]
    # 校验不一致：报 CONFLICT 并删除，不留坏文件
    h.drop_first = False
    with pytest.raises(FoxError) as ei:
        download.fetch(url, tmp_path / "bad", size=len(h.data), sha256="0" * 64)
    assert ei.value.code == "CONFLICT" and not (tmp_path / "bad").exists() and not (tmp_path / "bad.partial").exists()


def test_US63_parts_assemble_and_checksum(tmp_path):
    whole = os.urandom(2_500_000)
    parts = []
    for i, off in enumerate(range(0, len(whole), 1_000_000)):
        p = tmp_path / f"x.part{i + 1}"; p.write_bytes(whole[off:off + 1_000_000]); parts.append(p)
    r = download.assemble(parts, tmp_path / "x", sha256=hashlib.sha256(whole).hexdigest(), size=len(whole))
    assert r["verified"] and (tmp_path / "x").read_bytes() == whole
    with pytest.raises(FoxError):
        download.assemble(list(reversed(parts)), tmp_path / "y", sha256=hashlib.sha256(whole).hexdigest())
    assert not (tmp_path / "y").exists()


def test_US63_preset_install_from_local_mirror_registers_kvm_env(fox, tmp_path):
    """用本地「镜像站」走完整的安装流程（分卷下载、拼接校验、种子光盘、注册 linux-kvm 环境），不引导。"""
    if not presets.iso_tool() or not shutil.which("ssh-keygen"):
        pytest.skip("需要 xorriso/genisoimage 与 ssh-keygen")
    disk = os.urandom(1_200_000)
    mirror = tmp_path / "mirror" / "rel"; mirror.mkdir(parents=True)
    parts = []
    for i, off in enumerate(range(0, len(disk), 500_000)):
        n = f"foxos-test.qcow2.part{i + 1}"; (mirror / n).write_bytes(disk[off:off + 500_000])
        parts.append({"name": n, "size": len(disk[off:off + 500_000]), "sha256": hashlib.sha256(disk[off:off + 500_000]).hexdigest()})
    cat = {"format": presets.FORMAT, "version": "test", "release_base": (tmp_path / "mirror").as_uri(), "entries": [{
        "id": "foxos-test", "name": "Test preset", "guest_os": "linux", "kind": "foxos-image", "release": "rel", "disk_gb": 1, "features": ["zh-CN"],
        "artifacts": {"qcow2": {"name": "foxos-test.qcow2", "size": len(disk), "sha256": hashlib.sha256(disk).hexdigest(), "parts": parts}},
        "hosts": {"linux": {"provider": "linux-kvm", "artifact": "qcow2"}}}]}
    cf = tmp_path / "presets.json"; cf.write_text(json.dumps(cat))
    env = {"FOXOS_PRESETS_FILE": str(cf), "FOXOS_ALLOW_TEST_VMM": "qemu-tcg"}
    dry = fox.run("env", "install", "foxos-test", "t1", "--dry-run", extra_env=env, check=0)[1]["result"]
    assert dry["plan"]["download_bytes"] == len(disk) and len(dry["plan"]["files"]) == 3
    code, out, p = fox.run("env", "install", "foxos-test", "t1", extra_env=env)
    err = p.stderr
    if code == 6 and "linux-kvm" in json.dumps(out, ensure_ascii=False):
        pytest.skip("这台机器没有可用的 linux-kvm（也没有 QEMU 测试 VMM）")
    assert code == 0, (out, err)
    res = out["result"]
    assert res["download"]["assembled"]["verified"] and len(res["download"]["parts"]) == 3
    info = fox.run("env", "info", "t1", extra_env=env, check=0)[1]["result"]
    assert info.get("provider", info.get("backend")) == "linux-kvm"
    prog = fox.run("env", "progress", "t1", extra_env=env, check=0)[1]["result"]
    assert prog["state"] == "done"
    fox.run("env", "delete", "t1", extra_env=env, check=0)


@pytest.mark.skipif(os.environ.get("FOXOS_PRESET_E2E") != "1", reason="真实下载与引导：设置 FOXOS_PRESET_E2E=1")
def test_US63_real_linux_preset_download_verify_boot(fox):
    pid = os.environ.get("FOXOS_PRESET_ID", "foxos-debian-12")
    name = "e2e-" + pid.replace("foxos-", "").replace(".", "")[:20]
    code, out, p = fox.run("env", "install", pid, name, "--start", "--wait-ready", os.environ.get("FOXOS_PRESET_WAIT", "2400"), timeout=4 * 3600)
    assert code == 0, (out, p.stderr)
    res = out["result"]
    assert res["download"]["assembled"]["verified"]
    assert "FOXOS-PRESET-READY" in res["ready"] and "node=v" in res["ready"] and "bun=1" in res["ready"] and "foxos=foxos" in res["ready"] and "mcp=active" in res["ready"]
    r = fox.run("env", "exec", name, "--", "sh", "-c", "foxos --version; locale | head -1; node --version; bun --version; gemini --version", timeout=1800, json_out=False)
    try:
        assert r[0] == 0, r
        text = r[2].stdout
        assert "foxos" in text and "zh_CN" in text
    finally:
        fox.run("env", "stop", name, timeout=120)
        if os.environ.get("FOXOS_PRESET_KEEP") != "1":
            fox.run("env", "delete", name, timeout=120)
