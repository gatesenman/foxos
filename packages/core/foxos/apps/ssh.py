"""SSH 远程访问：状态、开关、authorized_keys、密码登录。

安全默认值（狐狸OS 系统里）：OpenSSH 默认开启，只允许密钥登录，禁止 root 登录，防火墙放行 22。
- 打开 SSH、添加 / 导入公钥、打开密码登录、改密码：只有「人」身份能做（智能体不能给自己开门）；
- 查看状态、列出公钥、删除公钥、关闭密码登录、关闭 SSH：智能体也可以（只会收紧）。
需要 root 的操作经 /usr/lib/foxos/foxos-ssh-admin 执行（sudoers 只对收紧方向免密）。
"""

from __future__ import annotations

import json
import os
import pwd
import re
import shutil
import socket
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, register, register_app

ADMIN = os.environ.get("FOXOS_SSH_ADMIN") or "/usr/lib/foxos/foxos-ssh-admin"
_NOPASSWD = {"status", "enable", "disable", "password-off"}
_KEY_RE = re.compile(r"^(?:(?:[^\s\"]+|\"[^\"]*\")\s+)?(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(?:256|384|521)|sk-ssh-ed25519@openssh\.com|sk-ecdsa-sha2-nistp256@openssh\.com)\s+([A-Za-z0-9+/=]+)(?:\s+(.*))?$")
_COMMON = {"password", "12345678", "123456789", "1234567890", "qwertyuiop", "foxos", "foxosfoxos", "iloveyou", "admin123", "letmein"}


def _human(ctx: Context) -> bool:
    from ..kernel import is_human
    return is_human(ctx.agent)


def _need_human(ctx: Context, what: str) -> None:
    if not _human(ctx):
        raise FoxError("PERMISSION_DENIED", tr("ssh.human_only", what))


def _user(user: str | None = None) -> pwd.struct_passwd:
    try:
        return pwd.getpwnam(user) if user else pwd.getpwuid(os.getuid())
    except KeyError:
        raise FoxError("NOT_FOUND", tr("ssh.no_such_user", user))


def _auth_file(u: pwd.struct_passwd) -> Path:
    return Path(os.environ.get("FOXOS_SSH_AUTHORIZED_KEYS") or (Path(u.pw_dir) / ".ssh" / "authorized_keys"))


def _admin(action: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    if not Path(ADMIN).exists():
        raise FoxError("DEPENDENCY_MISSING", tr("ssh.no_admin_helper", ADMIN))
    if os.geteuid() == 0:
        argv = [ADMIN, action, *args]
    elif action in _NOPASSWD:
        argv = ["sudo", "-n", ADMIN, action, *args]
    else:
        # 打开密码登录 / 改密码：需要 sudo 密码（人在终端前确认）
        argv = ["sudo", ADMIN, action, *args]
    try:
        r = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise FoxError("ERROR", tr("ssh.admin_timeout"))
    if r.returncode:
        raise FoxError("ERROR", tr("ssh.admin_failed", action, (r.stderr or r.stdout).strip()[-400:]), hint=tr("ssh.admin_hint"))
    return r


def _addresses() -> list[str]:
    out = []
    try:
        r = subprocess.run(["ip", "-4", "-o", "addr", "show", "scope", "global"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.splitlines():
            parts = line.split()
            if "inet" in parts:
                out.append(parts[parts.index("inet") + 1].split("/")[0])
    except (OSError, subprocess.SubprocessError):
        pass
    return out


def _fingerprint(line: str) -> tuple[str, str] | None:
    with tempfile.NamedTemporaryFile("w", suffix=".pub", delete=False) as f:
        f.write(line + "\n")
        p = f.name
    try:
        r = subprocess.run(["ssh-keygen", "-lf", p], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        os.unlink(p)
    if r.returncode:
        return None
    bits, fp, *rest = r.stdout.split()
    return fp, rest[-1].strip("()") if rest else ""


def _read_keys(u: pwd.struct_passwd) -> list[dict]:
    f = _auth_file(u)
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    keys = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = _KEY_RE.match(s)
        fp = _fingerprint(s) if m else None
        keys.append({"index": len(keys) + 1, "line": i, "type": m.group(1) if m else None,
                     "comment": (m.group(3) or "") if m else "", "fingerprint": fp[0] if fp else None, "valid": bool(fp)})
    return keys


def password_strength(pw: str, user: str = "") -> list[str]:
    """返回不满足的规则（空列表 = 足够强）。"""
    problems = []
    if len(pw) < 12:
        problems.append(tr("ssh.pw_too_short"))
    classes = sum(bool(re.search(p, pw)) for p in (r"[a-z]", r"[A-Z]", r"[0-9]", r"[^A-Za-z0-9]"))
    if classes < 3:
        problems.append(tr("ssh.pw_classes"))
    low = pw.lower()
    if low in _COMMON or (user and user.lower() in low) or len(set(pw)) < 6:
        problems.append(tr("ssh.pw_common"))
    return problems


def _service() -> dict:
    try:
        r = _admin("status")
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (FoxError, ValueError, IndexError):
        st = {}
        for unit in ("ssh.service", "sshd.service"):
            try:
                a = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True, timeout=5).stdout.strip()
                e = subprocess.run(["systemctl", "is-enabled", unit], capture_output=True, text=True, timeout=5).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                a = e = ""
            if a or e:
                st = {"active": a, "enabled": e}
                if a == "active":
                    break
        return {**st, "password": None, "root_login": None, "port": "22", "ufw": None, "ufw_22": None}


def ssh_status(ctx: Context, user: str | None = None) -> dict:
    u = _user(user)
    svc = _service()
    addrs = _addresses()
    keys = _read_keys(u)
    port = int(svc.get("port") or 22)
    live = Path("/run/foxos/live-ssh.txt").exists()
    active = svc.get("active") == "active"
    return {"installed": bool(shutil.which("sshd") or Path("/usr/sbin/sshd").exists()), "active": active,
            "enabled": svc.get("enabled") == "enabled", "port": port, "addresses": addrs, "hostname": socket.gethostname(),
            "user": u.pw_name, "password_login": svc.get("password") == "yes" if svc.get("password") else None,
            "root_login": svc.get("root_login"), "firewall": {"ufw": svc.get("ufw"), "port_22_allowed": svc.get("ufw_22") == "yes"},
            "authorized_keys": len([k for k in keys if k["valid"]]), "live_one_time_password": live,
            "connect": [f"ssh {'-p %d ' % port if port != 22 else ''}{u.pw_name}@{a}" for a in addrs],
            "mcp_over_ssh": f"ssh {u.pw_name}@{addrs[0] if addrs else '<host>'} foxos mcp",
            "message": tr("ssh.status_line", tr("ssh.on") if active else tr("ssh.off"), ", ".join(addrs) or "-", port)}


def ssh_enable(ctx: Context) -> dict:
    _need_human(ctx, "ssh enable")
    _admin("enable")
    return {**ssh_status(ctx), "message": tr("ssh.enabled")}


def ssh_disable(ctx: Context) -> dict:
    _admin("disable")
    return {**ssh_status(ctx), "message": tr("ssh.disabled")}


def _github_keys(name: str) -> list[str]:
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", name):
        raise FoxError("USAGE", tr("ssh.bad_github_user", name))
    base = os.environ.get("FOXOS_GITHUB_KEYS_BASE", "https://github.com")
    try:
        with urllib.request.urlopen(f"{base}/{name}.keys", timeout=20) as r:
            text = r.read().decode("utf-8", "replace")
    except OSError as e:
        raise FoxError("ERROR", tr("ssh.github_failed", name, e))
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def ssh_keys_add(ctx: Context, key: str | None = None, file: str | None = None, github: str | None = None, user: str | None = None) -> dict:
    _need_human(ctx, "ssh keys add")
    lines: list[str] = []
    if key:
        lines += [ln.strip() for ln in key.splitlines() if ln.strip()]
    if file:
        try:
            lines += [ln.strip() for ln in Path(file).expanduser().read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
        except OSError as e:
            raise FoxError("NOT_FOUND", tr("ssh.cannot_read", file, e))
    if github:
        lines += [f"{ln} github:{github}" if len(ln.split()) == 2 else ln for ln in _github_keys(github)]
    if not lines:
        raise FoxError("USAGE", tr("ssh.keys_add_usage"))
    u = _user(user)
    f = _auth_file(u)
    existing = {k["fingerprint"] for k in _read_keys(u) if k["fingerprint"]}
    added, skipped, bad = [], [], []
    good = []
    for ln in lines:
        if not _KEY_RE.match(ln):
            bad.append(ln[:40]); continue
        fp = _fingerprint(ln)
        if not fp:
            bad.append(ln[:40]); continue
        if fp[0] in existing:
            skipped.append(fp[0]); continue
        existing.add(fp[0]); good.append(ln); added.append(fp[0])
    if bad and not good and not skipped:
        raise FoxError("USAGE", tr("ssh.no_valid_keys"))
    if good:
        f.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        old = f.read_text(encoding="utf-8") if f.exists() else ""
        if old and not old.endswith("\n"):
            old += "\n"
        f.write_text(old + "\n".join(good) + "\n", encoding="utf-8")
        os.chmod(f, 0o600)
        try:
            os.chmod(f.parent, 0o700)
        except OSError:
            pass
    return {"message": tr("ssh.keys_added", len(added), len(skipped), len(bad)), "added": added, "skipped": skipped, "invalid": bad, "file": str(f)}


def ssh_keys_list(ctx: Context, user: str | None = None) -> dict:
    u = _user(user)
    keys = _read_keys(u)
    return {"user": u.pw_name, "file": str(_auth_file(u)), "count": len(keys), "keys": [{k: v for k, v in x.items() if k != "line"} for x in keys]}


def ssh_keys_remove(ctx: Context, key: str, user: str | None = None) -> dict:
    u = _user(user)
    keys = _read_keys(u)
    target = next((k for k in keys if key in (str(k["index"]), k["fingerprint"], k["comment"])), None)
    if not target:
        raise FoxError("NOT_FOUND", tr("ssh.key_not_found", key))
    f = _auth_file(u)
    lines = f.read_text(encoding="utf-8").splitlines()
    del lines[target["line"]]
    f.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"message": tr("ssh.key_removed", target["fingerprint"] or key), "removed": target["fingerprint"]}


def ssh_password(ctx: Context, state: str, new_password: str | None = None) -> dict:
    s = str(state).strip().lower()
    if s not in ("on", "off"):
        raise FoxError("USAGE", tr("ssh.password_usage"))
    if s == "off":
        _admin("password-off")
        return {"message": tr("ssh.password_off"), "password_login": False}
    _need_human(ctx, "ssh password on")
    u = _user()
    if new_password:
        problems = password_strength(new_password, u.pw_name)
        if problems:
            raise FoxError("USAGE", tr("ssh.weak_password", "；".join(problems)))
        _admin("set-password", u.pw_name, stdin=new_password + "\n")
    _admin("password-on")
    return {"message": tr("ssh.password_on"), "password_login": True, "password_changed": bool(new_password),
            "warning": tr("ssh.password_on_warning")}


register_app("ssh", tr("ssh.app_title"), tr("ssh.app_summary"))
_USER = Param("user", "string", tr("ssh.user_param"))
register(Command("ssh", "status", tr("ssh.status_summary"), ssh_status, params=[_USER],
                 examples=["foxos ssh status", "foxos ssh status --json"], audited=False))
register(Command("ssh", "enable", tr("ssh.enable_summary"), ssh_enable, examples=["foxos ssh enable"],
                 limits=[tr("ssh.limit_human")], permission="modify"))
register(Command("ssh", "disable", tr("ssh.disable_summary"), ssh_disable, examples=["foxos ssh disable"], permission="modify"))
register(Command("ssh", "keys add", tr("ssh.keys_add_summary"), ssh_keys_add,
                 params=[Param("key", "string", tr("ssh.key_param")), Param("file", "string", tr("ssh.file_param")),
                         Param("github", "string", tr("ssh.github_param")), _USER],
                 examples=["foxos ssh keys add --github octocat", "foxos ssh keys add --file ~/id_ed25519.pub",
                           "foxos ssh keys add --key \"ssh-ed25519 AAAA... me@laptop\""],
                 limits=[tr("ssh.limit_human")], permission="modify"))
register(Command("ssh", "keys list", tr("ssh.keys_list_summary"), ssh_keys_list, params=[_USER],
                 examples=["foxos ssh keys list"], audited=False))
register(Command("ssh", "keys remove", tr("ssh.keys_remove_summary"), ssh_keys_remove,
                 params=[Param("key", "string", tr("ssh.key_ref_param"), required=True, positional=True, metavar="INDEX|SHA256:..."), _USER],
                 examples=["foxos ssh keys remove 2", "foxos ssh keys remove SHA256:abc..."], permission="modify"))
register(Command("ssh", "password", tr("ssh.password_summary"), ssh_password,
                 params=[Param("state", "string", tr("ssh.password_state_param"), required=True, positional=True, metavar="on|off"),
                         Param("new_password", "string", tr("ssh.new_password_param"))],
                 examples=["foxos ssh password off", "foxos ssh password on --new-password '…'"],
                 limits=[tr("ssh.limit_password")], permission="modify"))
