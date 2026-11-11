#!/usr/bin/env python3
"""在真实启动的狐狸OS ISO 上跑端到端用例（US-65），结果写进 JSON，再生成 docs/test-report.md 的一节。

用法（宿主机，Linux + qemu）：
  FOXOS_E2E_ACCEL=tcg python3 scripts/os/e2e/iso_e2e.py boot  --iso build/os/FoxOS-0.3.2-amd64.iso
  python3 scripts/os/e2e/iso_e2e.py run ssh foxos_over_ssh runtime acp desktop chrome bots preset
  python3 scripts/os/e2e/iso_e2e.py install        # Calamares 装到虚拟磁盘（图形界面里按键操作）
  python3 scripts/os/e2e/iso_e2e.py boot --disk    # 从装好的磁盘启动（不挂 ISO）
  python3 scripts/os/e2e/iso_e2e.py run installed_ssh
  python3 scripts/os/e2e/iso_e2e.py report docs/test-report.md

没有 KVM 时必须显式设 FOXOS_E2E_ACCEL=tcg（很慢，但能跑）。
DeepSeek 密钥只在 bots 用例运行时从 ~/.secrets/deepseek_api_key 读出，经 SSH 的标准输入写进来宾的 foxos 密钥库；
不写日志、不进结果文件（所有输出在保存前都会把密钥替换成 ***）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

WORK = Path(os.environ.get("FOXOS_E2E_WORK", "/var/tmp/foxos-e2e"))
RESULTS = WORK / "results.json"
STATE = WORK / "vm.json"
KEY = WORK / "id_ed25519"
TZ = dt.timezone(dt.timedelta(hours=8))
SECRET_FILE = Path(os.environ.get("FOXOS_E2E_DEEPSEEK_KEY_FILE", str(Path.home() / ".secrets/deepseek_api_key")))
OVMF_CODE = "/usr/share/OVMF/OVMF_CODE_4M.fd"
OVMF_VARS = "/usr/share/OVMF/OVMF_VARS_4M.fd"
_SECRETS: list[str] = []


def now() -> str:
    return dt.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")


def scrub(s: str) -> str:
    for sec in _SECRETS:
        if sec:
            s = s.replace(sec, "***")
    return s


def log(msg: str) -> None:
    print(f"[{now()}] {scrub(msg)}", flush=True)


# ------------------------------------------------------------------ VM
def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def make_seed() -> Path:
    """FOXOSSEED 种子光盘：根目录 authorized_keys，现场会话开机时导入给 foxos。"""
    WORK.mkdir(parents=True, exist_ok=True)
    if not KEY.exists():
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "foxos-e2e@host", "-f", str(KEY)], check=True)
    d = WORK / "seed"
    d.mkdir(exist_ok=True)
    (d / "authorized_keys").write_text(KEY.with_suffix(".pub").read_text())
    iso = WORK / "seed.iso"
    subprocess.run(["xorriso", "-as", "mkisofs", "-quiet", "-V", "FOXOSSEED", "-J", "-r", "-o", str(iso), str(d)], check=True)
    return iso


def boot(iso: str | None, from_disk: bool, mem: int, cpus: int) -> dict:
    accel = os.environ.get("FOXOS_E2E_ACCEL") or ("kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "")
    if accel not in ("kvm", "tcg"):
        sys.exit("没有可用的 /dev/kvm；用软件模拟请显式设 FOXOS_E2E_ACCEL=tcg")
    stop()
    WORK.mkdir(parents=True, exist_ok=True)
    seed = make_seed()
    for name, size in (("target.qcow2", "32G"), ("data.qcow2", "40G")):
        if not (WORK / name).exists():
            subprocess.run(["qemu-img", "create", "-q", "-f", "qcow2", str(WORK / name), size], check=True)
    vars_fd = WORK / "vars.fd"
    if not vars_fd.exists() or (not from_disk and os.environ.get("FOXOS_E2E_FRESH_VARS") == "1"):
        vars_fd.write_bytes(Path(OVMF_VARS).read_bytes())
    port = _free_port()
    mon = WORK / "mon.sock"
    serial = WORK / ("serial-disk.log" if from_disk else "serial.log")
    argv = ["qemu-system-x86_64", "-accel", accel, "-m", str(mem), "-smp", str(cpus), "-machine", "q35",
            "-cpu", "max" if accel == "tcg" else "host",
            "-drive", f"if=pflash,format=raw,readonly=on,file={OVMF_CODE}", "-drive", f"if=pflash,format=raw,file={vars_fd}",
            "-drive", f"file={WORK / 'target.qcow2'},if=none,id=t,format=qcow2", "-device", "virtio-blk-pci,drive=t,serial=foxostarget,bootindex=1",
            "-drive", f"file={WORK / 'data.qcow2'},if=none,id=dd,format=qcow2", "-device", "virtio-blk-pci,drive=dd,serial=foxosdata",
            "-drive", f"file={seed},media=cdrom,if=none,id=seed,readonly=on", "-device", "ide-cd,drive=seed,bus=ide.1",
            "-netdev", f"user,id=n0,hostfwd=tcp:127.0.0.1:{port}-:22", "-device", "virtio-net-pci,netdev=n0",
            "-vga", "virtio", "-display", "none", "-qmp", f"unix:{mon},server,nowait",
            "-serial", f"file:{serial}", "-device", "virtio-rng-pci", "-daemonize", "-pidfile", str(WORK / "qemu.pid")]
    if not from_disk:
        argv += ["-drive", f"file={iso},media=cdrom,if=none,id=cd,readonly=on", "-device", "ide-cd,drive=cd,bus=ide.0,bootindex=0"]
    if serial.exists():
        serial.rename(serial.with_suffix(f".{int(time.time())}.log"))
    subprocess.run(argv, check=True)
    st = {"port": port, "accel": accel, "iso": iso, "from_disk": from_disk, "started": now(), "serial": str(serial), "mem": mem}
    STATE.write_text(json.dumps(st))
    log(f"VM 已启动：accel={accel} ssh 127.0.0.1:{port} {'磁盘' if from_disk else iso}")
    return st


def stop() -> None:
    pid = WORK / "qemu.pid"
    if pid.exists():
        try:
            os.kill(int(pid.read_text().strip()), 15)
            time.sleep(3)
        except (ProcessLookupError, ValueError):
            pass
        pid.unlink(missing_ok=True)


def state() -> dict:
    return json.loads(STATE.read_text())


def qmp(*cmds: dict) -> list:
    s = socket.socket(socket.AF_UNIX)
    s.connect(str(WORK / "mon.sock"))
    f = s.makefile("rw")
    f.readline()
    out = []
    for c in ({"execute": "qmp_capabilities"}, *cmds):
        f.write(json.dumps(c) + "\n"); f.flush()
        while True:
            r = json.loads(f.readline())
            if "event" not in r:
                break
        out.append(r)
    s.close()
    return out[1:]


def screendump(path: Path) -> Path:
    ppm = path.with_suffix(".ppm")
    qmp({"execute": "screendump", "arguments": {"filename": str(ppm)}})
    time.sleep(1)
    try:
        from PIL import Image
        Image.open(ppm).save(path)
        ppm.unlink(missing_ok=True)
    except Exception:  # noqa: BLE001 — 没有 Pillow 就留 ppm
        return ppm
    return path


def ssh_base(user: str = "foxos", key: bool = True, extra: list[str] | None = None) -> list[str]:
    cmd = ["ssh", "-p", str(state()["port"]), "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
           "-o", "LogLevel=ERROR", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=30"]
    if key:
        cmd += ["-i", str(KEY), "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "PreferredAuthentications=publickey"]
    return cmd + (extra or []) + [f"{user}@127.0.0.1"]


def ssh(command: str, *, user: str = "foxos", input: str | None = None, timeout: float = 600, check: bool = False) -> subprocess.CompletedProcess:
    # 远端用登录 shell，PATH 与图形会话变量和用户自己登录时一样
    wrapped = "export DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority XDG_RUNTIME_DIR=/run/user/$(id -u); " + command
    p = subprocess.run(ssh_base(user) + ["bash", "-lc", shlex.quote(wrapped)], input=input, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise AssertionError(f"`{command}` 退出码 {p.returncode}: {scrub(p.stderr[-800:])}")
    return p


def password_attempt(user: str, password: str) -> subprocess.CompletedProcess:
    """只用密码认证尝试登录（SSH_ASKPASS 喂密码），返回 ssh 的结果。"""
    ask = WORK / "askpass.sh"
    ask.write_text("#!/bin/sh\nexec cat \"$FOXOS_E2E_PW_FILE\"\n"); ask.chmod(0o700)
    pwf = WORK / ".pw"
    pwf.write_text(password); pwf.chmod(0o600)
    env = {**os.environ, "SSH_ASKPASS": str(ask), "SSH_ASKPASS_REQUIRE": "force", "DISPLAY": "none", "FOXOS_E2E_PW_FILE": str(pwf)}
    cmd = ["ssh", "-p", str(state()["port"]), "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=ERROR",
           "-o", "ConnectTimeout=20", "-o", "PubkeyAuthentication=no", "-o", "PreferredAuthentications=password,keyboard-interactive",
           "-o", "NumberOfPasswordPrompts=1", f"{user}@127.0.0.1", "echo LOGGED-IN"]
    try:
        return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    finally:
        pwf.unlink(missing_ok=True)


def wait_ssh(timeout: float) -> float:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if ssh("true", timeout=60).returncode == 0:
                return time.time() - t0
        except subprocess.TimeoutExpired:
            pass
        time.sleep(10)
    raise AssertionError(f"{timeout:.0f} 秒内 SSH 密钥登录没有成功")


# ------------------------------------------------------------------ results
def load_results() -> list:
    return json.loads(RESULTS.read_text()) if RESULTS.exists() else []


def record(case: str, ok: bool, detail: str, started: str, evidence: list[str] | None = None) -> None:
    res = [r for r in load_results() if r["case"] != case]
    res.append({"case": case, "status": "PASS" if ok else "FAIL", "started": started, "finished": now(),
                "detail": scrub(detail)[:1500], "evidence": evidence or [], "iso": state().get("iso"), "from_disk": state().get("from_disk")})
    RESULTS.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    log(f"{case}: {'PASS' if ok else 'FAIL'} — {detail[:300]}")


def j(p: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(p.stdout)
    except ValueError:
        raise AssertionError(f"不是 JSON（退出码 {p.returncode}）：{scrub(p.stdout[-400:])} {scrub(p.stderr[-400:])}")


# ------------------------------------------------------------------ cases
def case_ssh() -> str:
    """密钥登录可用；错误密码、root 被拒；sshd 实际生效的设置；ufw 放行 22。"""
    took = wait_ssh(float(os.environ.get("FOXOS_E2E_BOOT_TIMEOUT", "3600")))
    eff = ssh("sudo -n sshd -T 2>/dev/null | grep -E '^(passwordauthentication|permitrootlogin|pubkeyauthentication|kbdinteractiveauthentication) '", check=True).stdout
    assert "permitrootlogin no" in eff and "pubkeyauthentication yes" in eff and "kbdinteractiveauthentication no" in eff, eff
    bad = password_attempt("foxos", "foxos")
    assert bad.returncode != 0 and "LOGGED-IN" not in bad.stdout, "默认密码 foxos 居然能登录"
    bad2 = password_attempt("foxos", "wrong-Password-123")
    assert bad2.returncode != 0 and "LOGGED-IN" not in bad2.stdout
    root = subprocess.run(ssh_base("root") + ["true"], capture_output=True, text=True, timeout=60)
    assert root.returncode != 0, "root 用密钥登录成功了"
    fw = ssh("sudo -n ufw status", check=True).stdout
    assert "Status: active" in fw and "22/tcp" in fw, fw
    live = "passwordauthentication yes" in eff
    msg = f"开机后 {took:.0f}s 密钥登录成功；sshd -T：{' '.join(eff.split())}；默认 / 错误密码被拒；root 被拒；ufw active 放行 22/tcp"
    if live:
        txt = ssh("sudo -n cat /run/foxos/live-ssh.txt", check=True).stdout
        m = re.search(r"(?:一次性密码|password)[^:：]*[:：]\s*(\S{16})", txt)
        assert m, "live-ssh.txt 里没有 16 位一次性密码"
        _SECRETS.append(m.group(1))
        good = password_attempt("foxos", m.group(1))
        assert good.returncode == 0 and "LOGGED-IN" in good.stdout, "现场会话的一次性密码不能登录"
        rootpw = password_attempt("root", m.group(1))
        assert rootpw.returncode != 0
        assert "警告" in txt or "WARNING" in txt.upper()
        msg += "；现场会话：一次性 16 位随机密码可登录（不记录），同一密码登录 root 被拒，live-ssh.txt 含警告"
    return msg


def case_foxos_over_ssh() -> str:
    v = ssh("foxos --version", check=True).stdout.strip()
    st = j(ssh("foxos ssh status --json", check=True))["result"]
    assert st["active"] and st["root_login"] is False, st
    # MCP over SSH（stdio）：initialize → tools/list → tools/call ssh_status
    msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "e2e", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ssh_status", "arguments": {}}}]
    p = subprocess.run(ssh_base() + ["-T", "foxos", "--workspace", "~/FoxOS/workspace", "mcp"], input="".join(json.dumps(m) + "\n" for m in msgs),
                       capture_output=True, text=True, timeout=300)
    replies = {r.get("id"): r for r in (json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{"))}
    tools = {t["name"] for t in replies[2]["result"]["tools"]}
    assert {"ssh_status", "env_catalog", "bot_message_send"} <= tools, sorted(tools)[:20]
    assert not replies[3]["result"].get("isError"), replies[3]
    return f"{v}；foxos ssh status：active、root_login=false、password_login={st['password_login']}；MCP over SSH：{len(tools)} 个工具，tools/call ssh_status 成功"


def case_runtime() -> str:
    p = ssh("foxos runtime doctor --json", timeout=900)
    d = j(p)["result"]
    assert p.returncode == 0 and d.get("ok", True), json.dumps(d, ensure_ascii=False)[:800]
    tools = d.get("tools") or d.get("runtimes") or []
    names = [t.get("id") or t.get("name") for t in tools] if isinstance(tools, list) else list(tools)
    return f"runtime doctor 退出码 0，ok={d.get('ok')}，{len(names)} 项：{', '.join(map(str, names[:14]))}"


def case_acp() -> str:
    a = j(ssh("foxos acp list --json", check=True))["result"]
    ids = [x["id"] for x in a["agents"]]
    assert "opencode" in ids, ids
    pr = j(ssh("foxos acp agent probe opencode --json", timeout=900))
    assert pr.get("ok", True) and "error" not in pr, pr
    return f"acp list：{', '.join(ids)}；opencode 握手：{json.dumps(pr.get('result'), ensure_ascii=False)[:200]}"


def case_desktop() -> str:
    shot = WORK / f"e2e-desktop-{int(time.time())}.png"
    st = j(ssh("foxos desktop status --json", check=True))["result"]
    ssh("foxos desktop launch -- xfce4-terminal -T foxos-e2e-term", check=True)
    ok = False
    for _ in range(40):
        w = j(ssh("foxos desktop windows --json", check=True))["result"]
        wins = w.get("windows", w if isinstance(w, list) else [])
        hit = [x for x in wins if "foxos-e2e-term" in (x.get("title") or "")]
        if hit:
            ok = True
            break
        time.sleep(5)
    assert ok, "终端窗口没出现"
    wid = str(hit[0].get("id"))
    ssh(f"foxos desktop focus {shlex.quote(wid)}", check=True)
    ssh("foxos desktop type 'echo FOXOS-E2E-TYPED'", check=True)
    ssh("foxos desktop key Return", check=True)
    time.sleep(5)
    ssh(f"foxos desktop screenshot --path {shlex.quote('/tmp/' + shot.name)}", check=True)
    screendump(shot)
    ssh(f"foxos desktop close {shlex.quote(wid)}", check=True)
    time.sleep(5)
    left = j(ssh("foxos desktop windows --json", check=True))["result"]
    assert "foxos-e2e-term" not in json.dumps(left, ensure_ascii=False)
    return f"desktop status：{json.dumps(st, ensure_ascii=False)[:160]}；launch → windows 里出现 → focus → type → key → screenshot → close 全部成功", [str(shot)]


def case_chrome() -> str:
    p = ssh("sudo -n /usr/lib/foxos/foxos-chrome-setup --install", timeout=3600)
    assert p.returncode == 0, p.stdout[-600:] + p.stderr[-600:]
    ver = ssh("google-chrome-stable --version", check=True).stdout.strip()
    ssh("foxos browser cdp on", check=True)
    ssh("foxos desktop launch chrome https://example.com", check=True)
    title = ""
    for _ in range(60):
        t = ssh("foxos browser tabs --json")
        if t.returncode == 0 and "Example Domain" in t.stdout:
            title = "Example Domain"
            break
        time.sleep(10)
    assert title, "CDP 没有看到 example.com 的标签页"
    shot = screendump(WORK / f"e2e-chrome-{int(time.time())}.png")
    default = ssh("xdg-settings get default-web-browser 2>/dev/null; update-alternatives --query x-www-browser | grep Value").stdout
    return f"{ver}；从 dl.google.com 装好；CDP 开启后 browser tabs 看到「{title}」；默认浏览器：{' '.join(default.split())}", [str(shot)]


def case_bots() -> str:
    key = SECRET_FILE.read_text().strip()
    _SECRETS.append(key)
    p = ssh("foxos acp key set opencode DEEPSEEK_API_KEY --value-stdin --json", input=key, timeout=120)
    assert p.returncode == 0, scrub(p.stderr[-400:])
    model = os.environ.get("FOXOS_E2E_MODEL", "deepseek/deepseek-chat")
    ssh(f"foxos acp agent config opencode --model {shlex.quote(model)} --json", check=True)
    # 「智能体」窗口启动
    ssh("foxos desktop launch -- foxos-bots", check=True)
    seen = ""
    for _ in range(60):
        w = ssh("foxos desktop windows --json").stdout
        m = re.search(r'"title":\s*"([^"]*(智能体|Bots|FoxOS Bots)[^"]*)"', w)
        if m:
            seen = m.group(1)
            break
        time.sleep(5)
    assert seen, "智能体窗口没有出现"
    shot = screendump(WORK / f"e2e-bots-{int(time.time())}.png")
    ssh("foxos bot profile delete e2e-opencode --json >/dev/null 2>&1; true")
    ssh(f"foxos bot profile create E2E-opencode --id e2e-opencode --acp-agent opencode --model {shlex.quote(model)} --approval-mode allow_reads --json", check=True)
    t0 = time.time()
    r = ssh("foxos bot message send e2e-opencode 'Reply with exactly the word FOXOS-E2E-PONG and nothing else.' --approve allow --json", timeout=1800)
    out = scrub(r.stdout)
    assert r.returncode == 0 and "FOXOS-E2E-PONG" in out, out[-800:] + scrub(r.stderr[-400:])
    # 窗口里也能看到这条对话
    time.sleep(5)
    shot2 = screendump(WORK / f"e2e-bots-chat-{int(time.time())}.png")
    return f"智能体窗口「{seen}」出现；opencode（ACP，{model}）真实回合 {time.time() - t0:.0f}s，回答含 FOXOS-E2E-PONG；密钥经 SSH 标准输入写入来宾密钥库", [str(shot), str(shot2)]


def case_preset() -> str:
    pid = os.environ.get("FOXOS_E2E_PRESET", "foxos-debian-12")
    # 数据盘：40G 虚拟盘放环境（现场会话的根在内存里，放不下 1.4 GB 镜像）
    ssh("set -e; d=/dev/disk/by-id/virtio-foxosdata; mountpoint -q /mnt/foxos-data || { sudo -n blkid $d >/dev/null || sudo -n mkfs.ext4 -q -F $d; "
        "sudo -n mkdir -p /mnt/foxos-data; sudo -n mount $d /mnt/foxos-data; sudo -n chown foxos: /mnt/foxos-data; }", check=True, timeout=600)
    tcg = ""
    if not ssh("test -w /dev/kvm").returncode == 0:
        # 嵌套：来宾里没有 KVM。测试专用：从 Ubuntu 源装 qemu，再显式允许 qemu-tcg
        ssh("command -v qemu-system-x86_64 || { sudo -n apt-get update -q && sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y -q qemu-system-x86 qemu-utils; }", check=True, timeout=3600)
        tcg = "FOXOS_ALLOW_TEST_VMM=qemu-tcg "
    cat = j(ssh("foxos env catalog --json", check=True))["result"]
    e = next(x for x in cat["entries"] if x["id"] == pid)
    t0 = time.time()
    p = ssh(f"{tcg}foxos env install {pid} e2e --location /mnt/foxos-data/envs --start --wait-ready {os.environ.get('FOXOS_E2E_PRESET_WAIT', '10800')} --json",
            timeout=6 * 3600)
    out = j(p)
    assert p.returncode == 0, json.dumps(out, ensure_ascii=False)[-800:]
    res = out["result"]
    ready = res.get("ready") or ""
    assert "FOXOS-PRESET-READY" in ready, ready
    ex = ssh("foxos env exec e2e -- foxos --version --json", timeout=900)
    ls = ssh("foxos env list").stdout
    shot = screendump(WORK / f"e2e-preset-{int(time.time())}.png")
    ssh("foxos env stop e2e --json", timeout=600)
    return (f"{pid}：从 GitHub Releases 下载 {e['download']['bytes'] if 'download' in e else ''} 字节分卷、逐卷与整体 sha256 校验、"
            f"{'qemu-tcg 嵌套' if tcg else 'KVM'} 引导，{time.time() - t0:.0f}s 后就绪：{ready.strip()[:200]}；env exec 退出码 {ex.returncode}；"
            f"env list：{' '.join(ls.split())[:200]}"), [str(shot)]


def case_installed_ssh() -> str:
    """从 Calamares 装好的磁盘启动后：密钥可登录、密码登录关闭并被拒、root 被拒、foxos 可用、不是现场会话。"""
    took = wait_ssh(float(os.environ.get("FOXOS_E2E_BOOT_TIMEOUT", "3600")))
    eff = ssh("sudo -n sshd -T 2>/dev/null | grep -E '^(passwordauthentication|permitrootlogin) ' || echo need-sudo").stdout
    casper = ssh("test -d /run/casper || grep -q boot=casper /proc/cmdline && echo live || echo installed").stdout.strip()
    assert casper == "installed", casper
    bad = password_attempt(os.environ.get("FOXOS_E2E_USER", "foxos"), os.environ.get("FOXOS_E2E_INSTALL_PW", "Fox-E2E-install-2026!"))
    assert bad.returncode != 0 and "LOGGED-IN" not in bad.stdout, "装好的系统默认接受了密码登录"
    root = subprocess.run(ssh_base("root") + ["true"], capture_output=True, text=True, timeout=60)
    assert root.returncode != 0
    v = ssh("foxos --version && foxos ssh status --json", check=True).stdout
    st = json.loads(v[v.index("{"):])["result"]
    assert st["password_login"] is False and st["active"], st
    keys = j(ssh("foxos ssh keys list --json", check=True))["result"]
    shot = screendump(WORK / f"e2e-installed-{int(time.time())}.png")
    return (f"从虚拟磁盘启动（不挂 ISO）{took:.0f}s 后密钥登录成功；{casper}；即便用安装时设置的真实密码，密码登录也被拒；root 被拒；"
            f"foxos ssh status：password_login=false；{keys['count']} 把公钥（Calamares 写入）；{' '.join(eff.split())}"), [str(shot)]


INSTALL_PW = os.environ.get("FOXOS_E2E_INSTALL_PW", "Fox-E2E-install-2026!")
# Calamares 页面上的按键（xdotool，中文界面）。坐标是 1280x800 下「你的名字」输入框；之后 Tab 依次到登录名、主机名、密码、确认密码。
CAL_STEPS = [
    ("wait", "欢迎"), ("key", "alt+n"), ("sleep", 8), ("key", "alt+n"), ("sleep", 8), ("key", "alt+n"), ("sleep", 15),   # 欢迎 → 位置 → 键盘 → 分区
    ("key", "alt+n"), ("sleep", 10),                                                                                    # 分区（预选「抹掉磁盘」）→ 用户
    ("users", None), ("sleep", 5), ("key", "alt+n"), ("sleep", 10),                                                       # 用户 → 摘要
    ("key", "alt+i"),                                                                                                   # 摘要页「安装」
]


def _x(cmd: str, timeout: float = 120) -> subprocess.CompletedProcess:
    return ssh(cmd, timeout=timeout)


def case_install() -> str:
    """Calamares 图形安装到 32G 虚拟磁盘（virtio，序列号 foxostarget），中文界面按键操作。

    只为让按键可重复，测试前在 Calamares 配置的副本里预选两项：分区页默认「抹掉磁盘」、用户页预填名字 / 登录名 / 主机名。
    SSH 设置对话框（foxos-ssh-setup --installer）的产物直接写进 /run/foxos/ssh-install：一把公钥，不开密码登录。
    """
    pub = KEY.with_suffix(".pub").read_text().strip()
    setup = (
        "set -e; rm -rf /tmp/cal-e2e; cp -a /etc/calamares /tmp/cal-e2e; "
        "printf 'initialPartitioningChoice: erase\\ninitialSwapChoice: none\\ndefaultFileSystemType: ext4\\nefiSystemPartition: /boot/efi\\n' > /tmp/cal-e2e/modules/partition.conf; "
        "printf 'presets:\\n  fullName:\\n    value: foxos\\n    editable: true\\n  loginName:\\n    value: foxos\\n    editable: true\\n' >> /tmp/cal-e2e/modules/users.conf; "
        "mkdir -p /run/foxos/ssh-install; printf '%s\\n' " + shlex.quote(pub) + " > /run/foxos/ssh-install/authorized_keys; "
        "rm -f /run/foxos/ssh-install/password /run/foxos/ssh-install/password-value; "
        "sudo -n pkill -x calamares || true; "
        "(sudo -n -E calamares -c /tmp/cal-e2e -d > /tmp/calamares-e2e.log 2>&1 &) ; sleep 2; echo started")
    ssh(setup, check=True)
    t0 = time.time()
    for _ in range(120):
        if "Calamares" in _x("xdotool search --name '安装|Calamares|狐狸OS' getwindowname %@ 2>/dev/null").stdout or \
           _x("xdotool search --class calamares 2>/dev/null").stdout.strip():
            break
        time.sleep(5)
    shots = []
    for kind, arg in CAL_STEPS:
        if kind == "wait":
            time.sleep(20)
        elif kind == "sleep":
            time.sleep(arg)
        elif kind == "key":
            _x("w=$(xdotool search --class calamares | tail -1); xdotool windowactivate --sync $w; xdotool key --clearmodifiers " + arg)
        elif kind == "users":
            shots.append(str(screendump(WORK / f"e2e-cal-users-{int(time.time())}.png")))
            pw = shlex.quote(INSTALL_PW)
            _x("w=$(xdotool search --class calamares | tail -1); xdotool windowactivate --sync $w; "
               "for i in 1 2 3; do xdotool key --clearmodifiers Tab; done; sleep 1; "
               f"xdotool type --delay 80 {pw}; xdotool key Tab; xdotool type --delay 80 {pw}; sleep 2")
            shots.append(str(screendump(WORK / f"e2e-cal-users-filled-{int(time.time())}.png")))
    shots.append(str(screendump(WORK / f"e2e-cal-installing-{int(time.time())}.png")))
    done = False
    for _ in range(int(os.environ.get("FOXOS_E2E_INSTALL_TIMEOUT", "14400")) // 30):
        lg = _x("tail -c 4000 /tmp/calamares-e2e.log").stdout
        if re.search(r"Installation (complete|finished)|ViewModule \"finished|Finished\. Exit code|FinishedPage", lg) or \
           "finished" in _x("grep -o 'Starting job \"[a-z@]*' /tmp/calamares-e2e.log | tail -1").stdout:
            done = True
            break
        if re.search(r"Installation failed|ERROR.*Job .* failed", lg):
            break
        time.sleep(30)
    shots.append(str(screendump(WORK / f"e2e-cal-finished-{int(time.time())}.png")))
    tail = _x("grep -E 'Starting job|Installation (failed|complete)|failed' /tmp/calamares-e2e.log | tail -8").stdout
    assert done, f"Calamares 没有完成：{tail[-800:]}"
    lsblk = _x("lsblk -o NAME,SIZE,FSTYPE,SERIAL /dev/disk/by-id/virtio-foxostarget").stdout
    return f"{time.time() - t0:.0f}s 完成；{' '.join(tail.split())[-400:]}；目标盘：{' '.join(lsblk.split())}", shots


CASES = {"ssh": case_ssh, "foxos_over_ssh": case_foxos_over_ssh, "runtime": case_runtime, "acp": case_acp, "desktop": case_desktop,
         "chrome": case_chrome, "bots": case_bots, "preset": case_preset, "installed_ssh": case_installed_ssh, "install": case_install}


def run(names: list[str]) -> int:
    bad = 0
    for n in names:
        started = now()
        log(f"开始 {n}")
        try:
            r = CASES[n]()
            detail, ev = (r if isinstance(r, tuple) else (r, []))
            record(n, True, detail, started, ev)
        except Exception as e:  # noqa: BLE001 — 每个用例独立记录
            bad += 1
            record(n, False, f"{type(e).__name__}: {e}", started)
    return bad


# ------------------------------------------------------------------ report
TITLES = {"ssh": "SSH：密钥可登录、默认 / 错误密码与 root 被拒、ufw 放行 22", "foxos_over_ssh": "经 SSH 运行 foxos 与 MCP over SSH（stdio）",
          "runtime": "foxos runtime doctor", "acp": "foxos acp list 与 opencode 握手", "desktop": "桌面会话控制（foxos desktop …）",
          "chrome": "Google Chrome 安装、默认浏览器、CDP", "bots": "「智能体」窗口启动 + opencode（ACP，DeepSeek）真实对话",
          "preset": "在线预设：真实下载 + 校验 + 引导 Linux 预设", "install": "Calamares 安装到虚拟磁盘",
          "installed_ssh": "重启进入装好的系统：密钥可登录、密码被拒、foxos 可用"}


def report(path: Path, heading: str) -> None:
    res = load_results()
    order = list(TITLES)
    res.sort(key=lambda r: order.index(r["case"]) if r["case"] in order else 99)
    lines = [f"## {heading}", "", f"ISO：`{res[0]['iso'] if res else ''}`；虚拟化：{state().get('accel')}（宿主没有 KVM，按要求显式用 TCG）；时间为北京时间（UTC+8）。", "",
             "| 用例 | 结果 | 开始 | 结束 | 说明 |", "|---|---|---|---|---|"]
    for r in res:
        d = r["detail"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {TITLES.get(r['case'], r['case'])} | **{r['status']}** | {r['started']} | {r['finished']} | {d} |")
    fails = [r for r in res if r["status"] != "PASS"]
    lines += ["", f"合计 {len(res)} 项，通过 {len(res) - len(fails)}，失败 {len(fails)}。", ""]
    text = path.read_text(encoding="utf-8") if path.exists() else "# 测试报告\n"
    block = "\n".join(lines)
    marker = f"## {heading}"
    if marker in text:
        pre, _, rest = text.partition(marker)
        nxt = rest.find("\n## ")
        text = pre + block + (rest[nxt:] if nxt >= 0 else "\n")
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")
    print(block)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("boot"); b.add_argument("--iso"); b.add_argument("--disk", action="store_true")
    b.add_argument("--mem", type=int, default=int(os.environ.get("FOXOS_E2E_MEM", "5120"))); b.add_argument("--cpus", type=int, default=4)
    r = sub.add_parser("run"); r.add_argument("cases", nargs="+", choices=list(CASES))
    rec = sub.add_parser("record"); rec.add_argument("case"); rec.add_argument("status", choices=["PASS", "FAIL"]); rec.add_argument("started"); rec.add_argument("detail")
    rec.add_argument("--evidence", action="append", default=[])
    sub.add_parser("stop"); sub.add_parser("shot")
    rp = sub.add_parser("report"); rp.add_argument("path"); rp.add_argument("--heading", default="0.3.2 ISO 端到端（US-65）")
    a = ap.parse_args()
    if a.cmd == "boot":
        if not a.disk and not a.iso:
            sys.exit("--iso 或 --disk")
        boot(a.iso and str(Path(a.iso).resolve()), a.disk, a.mem, a.cpus)
    elif a.cmd == "run":
        return 1 if run(a.cases) else 0
    elif a.cmd == "record":
        record(a.case, a.status == "PASS", a.detail, a.started, a.evidence)
    elif a.cmd == "stop":
        stop()
    elif a.cmd == "shot":
        print(screendump(WORK / f"shot-{int(time.time())}.png"))
    elif a.cmd == "report":
        report(Path(a.path), a.heading)
    return 0


if __name__ == "__main__":
    sys.exit(main())
