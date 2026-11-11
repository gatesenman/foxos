"""Everything 应用（HeyPuter/everything 上游 51 个应用）：安装、目录，以及每个应用的 CLI / MCP 命令。

每个应用都有同一套命令（app / file / ui / data / module / op），外加从操作清单
data/ops/<应用>.json 生成的语义命令 `foxos <应用> <资源> <动作>`。命令在正在运行的应用实例里执行
（桌面窗口，或没有窗口时的无界面实例），走应用自己的代码，所以效果与人在界面上操作相同。
"""

from __future__ import annotations

from foxos.i18n import get_lang, tr
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import desktop_client, locks
from ..errors import FoxError
from ..kernel import Command, Context, Param, register, register_app

DATA = Path(__file__).resolve().parent.parent / "data"
CATALOG = json.loads((DATA / "everything.json").read_text(encoding="utf-8"))
APPS = {a["id"]: a for a in CATALOG["apps"]}
GROUPS = {g["id"]: g for g in CATALOG["groups"]}
# 每个上游应用的界面语言与日期 / 数字格式是否跟随狐狸OS 语言（扫描上游源码得出，见 data/everything-locale.json）
LOCALE = json.loads((DATA / "everything-locale.json").read_text(encoding="utf-8"))["apps"]
UPSTREAM_GIT = CATALOG["upstream"] + ".git"


def app_dir(app: str) -> Path:
    return desktop_client.foxos_home() / "everything" / app


def manifest(app: str) -> dict | None:
    try:
        return json.loads((app_dir(app) / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def installed(app: str) -> bool:
    return (app_dir(app) / "dist" / "index.html").exists()


def _row(a: dict) -> dict:
    m = manifest(a["id"])
    return {"id": a["id"], "name": a["name"], "group": a["group"], "group_name": GROUPS[a["group"]]["zh" if get_lang() == "zh-CN" else "en"], "license": a["license"],
            "agpl": a["agpl"], "alternative_to": a["alternativeTo"], "installed": installed(a["id"]),
            "installed_commit": m and m.get("commit"), "ops": len(load_ops(a["id"])),
            "ui_languages": LOCALE[a["id"]]["ui"], "locale_formats": LOCALE[a["id"]]["formats"]}


# ---------------------------------------------------------------- 目录与安装
register_app("everything", tr("everything.everything_apps"), tr("everything.the_51_apps_of_upstream_heyputer"),
             limits=[tr("everything.agpl_3_0_apps_are_fetched_from")])


def ev_list(ctx: Context, group: str | None = None, installed_only: bool = False) -> dict:
    rows = [_row(a) for a in CATALOG["apps"] if (not group or a["group"] == group)]
    if installed_only:
        rows = [r for r in rows if r["installed"]]
    return {"count": len(rows), "installed": sum(r["installed"] for r in rows), "upstream": CATALOG["upstream"], "commit": CATALOG["commit"],
            "groups": CATALOG["groups"], "apps": rows}


def ev_info(ctx: Context, app: str) -> dict:
    a = _need(app)
    return {**_row(a), "description": a["description"], "license_file": a["licenseFile"], "upstream_url": a["upstreamUrl"],
            "path": str(app_dir(app)), "manifest": manifest(app), "commands": _app_command_list(app)}


def _need(app: str) -> dict:
    if app not in APPS:
        raise FoxError("NOT_FOUND", tr("everything.no_everything_app_named", app), hint="foxos everything list")
    return APPS[app]


def _run(cmd: list[str], cwd: Path, log, env=None, timeout=1800) -> None:
    log(f"$ {' '.join(cmd)}\n")
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    out = p.stdout.decode("utf-8", "replace")
    log(out[-4000:])
    if p.returncode != 0:
        raise FoxError("ERROR", tr("everything.command_failed_exit_code", p.returncode, ' '.join(cmd[:3])), details={"output": out[-2000:]})


def _fetch_source(apps: list[str], dest: Path, source: str | None, log) -> Path:
    """返回包含 src/<app> 与 dev/ 的上游源码目录（固定在目录里的提交）。"""
    commit = CATALOG["commit"]
    if source:
        src = Path(source).expanduser().resolve()
        if (src / ".git").exists() and shutil.which("git"):
            for a in apps:
                log(tr("everything.exporting_src_of_from_local", src, commit[:8], a))
            tar = subprocess.run(["git", "-C", str(src), "archive", commit, "dev", "LICENSE", *[f"src/{a}" for a in apps]], stdout=subprocess.PIPE, check=True).stdout
            subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)
            return dest
        for a in apps:
            shutil.copytree(src / "src" / a, dest / "src" / a, ignore=shutil.ignore_patterns("node_modules", "dist"))
        shutil.copytree(src / "dev", dest / "dev")
        shutil.copy2(src / "LICENSE", dest / "LICENSE")
        return dest
    if not shutil.which("git"):
        raise FoxError("DEPENDENCY_MISSING", tr("everything.git_is_needed_to_fetch_the"), hint=tr("everything.install_git_from_the_setup_wizard"))
    g = ["git", "-C", str(dest)]
    _run(["git", "init", "-q", str(dest)], dest.parent, log)
    _run([*g, "remote", "add", "origin", UPSTREAM_GIT], dest, log)
    _run([*g, "config", "core.sparseCheckout", "true"], dest, log)
    (dest / ".git" / "info" / "sparse-checkout").write_text("\n".join(["/LICENSE", "/dev/", *[f"/src/{a}/" for a in apps]]) + "\n")
    _run([*g, "fetch", "--depth", "1", "--filter=blob:none", "origin", commit], dest, log, timeout=3600)
    _run([*g, "checkout", "-q", "FETCH_HEAD"], dest, log, timeout=3600)
    return dest


ICON_NAMES = ("icon-128.png", "icon.png")


def _copy_icon(adir: Path, dest: Path) -> str | None:
    for n in ICON_NAMES:
        if (adir / n).exists():
            shutil.copy2(adir / n, dest / "icon.png")
            return n
    return None


def ev_icons(ctx: Context, source: str | None = None) -> dict:
    """给已安装但缺少图标的应用补上上游图标（只取 src/<应用>/icon*.png，不重新构建）。"""
    need = [a["id"] for a in CATALOG["apps"] if installed(a["id"]) and not (app_dir(a["id"]) / "icon.png").exists()]
    done, missing = [], []
    if need:
        work = Path(tempfile.mkdtemp(prefix="foxos-ev-icons-"))
        try:
            _fetch_source(need, work, source, lambda s: None)
            for a in need:
                (done if _copy_icon(work / "src" / a, app_dir(a)) else missing).append(a)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    have = [a["id"] for a in CATALOG["apps"] if (app_dir(a["id"]) / "icon.png").exists()]
    return {"message": tr("everything.added_icons_for_app_s_installed_app", len(done), len(have)), "added": done, "missing": missing, "with_icon": have}


def install_app(app: str, source: str | None = None, log=lambda s: None, keep_build: bool = False) -> dict:
    a = _need(app)
    npm = shutil.which("npm")
    if not npm:
        raise FoxError("DEPENDENCY_MISSING", tr("everything.node_js_22_12_and_npm_are_needed_to"), hint=tr("everything.install_node_js_from_the_setup"))
    work = Path(tempfile.mkdtemp(prefix=f"foxos-ev-{app}-"))
    try:
        _fetch_source([app], work, source, log)
        adir = work / "src" / app
        if not (adir / "package.json").exists():
            raise FoxError("NOT_FOUND", tr("everything.the_upstream_source_has_no_src", app))
        html = (adir / "index.html").read_text(encoding="utf-8", errors="replace") if (adir / "index.html").exists() else ""
        import re as _re
        for ref in _re.findall(r'<script[^>]+type="module"[^>]+src="/([^"]+)"', html):
            if not (adir / ref).exists():
                raise FoxError("DEPENDENCY_MISSING", tr("everything.upstream_src_lacks_referenced_by", app, ref),
                               hint=a.get("upstreamIssue") or tr("everything.this_is_an_upstream_problem"))
        env = {**os.environ, "npm_config_fund": "false", "npm_config_audit": "false", "CI": "1"}
        _run([npm, "ci", "--no-audit", "--no-fund", "--loglevel=error"] if (adir / "package-lock.json").exists() else [npm, "install", "--no-audit", "--no-fund"], adir, log, env=env)
        out = app_dir(app)
        stage = out.with_name(f"{app}.new")
        shutil.rmtree(stage, ignore_errors=True)
        stage.mkdir(parents=True)
        vite = adir / "node_modules" / "vite" / "bin" / "vite.js"
        node = shutil.which("node") or "node"
        _run([node, str(vite), "build", "--config", str(DATA / "runtime" / "vite.foxos.config.mjs"), "--outDir", str(stage / "dist"), "--emptyOutDir"], adir, log, env=env)
        # 上游自带的程序图标（桌面的应用中心、开始菜单、任务栏、标题栏使用）
        _copy_icon(adir, stage)
        # 许可证与版权声明随安装保留
        notices = stage / "licenses"
        notices.mkdir()
        shutil.copy2(work / "LICENSE", notices / "everything-root-LICENSE")
        for f in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "NOTICE"):
            if (adir / f).exists():
                shutil.copy2(adir / f, notices / f"{app}-{f}")
        digest = hashlib.sha256()
        for p in sorted((stage / "dist").rglob("*")):
            if p.is_file():
                digest.update(p.relative_to(stage).as_posix().encode())
                digest.update(p.read_bytes())
        m = {"app": app, "name": a["name"], "commit": CATALOG["commit"], "upstream": CATALOG["upstream"], "license": a["license"],
             "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "dist_sha256": digest.hexdigest(),
             "source": source or UPSTREAM_GIT}
        (stage / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        shutil.rmtree(out, ignore_errors=True)
        stage.rename(out)
        log(tr("everything.installed", a['name'], out))
        return m
    finally:
        if not keep_build:
            shutil.rmtree(work, ignore_errors=True)


def ev_install(ctx: Context, apps: list | None = None, all: bool = False, group: str | None = None, source: str | None = None, force: bool = False) -> dict:
    targets = list(apps or [])
    if all:
        targets = [a["id"] for a in CATALOG["apps"]]
    if group:
        targets += [a["id"] for a in CATALOG["apps"] if a["group"] == group]
    if not targets:
        raise FoxError("USAGE", tr("everything.name_the_apps_to_install_or_use_all"))
    for t in targets:
        _need(t)
    source = source or os.environ.get("FOXOS_EVERYTHING_SOURCE")
    done, skipped, failed = [], [], []
    verbose = os.environ.get("FOXOS_PROGRESS") == "1"
    for i, t in enumerate(dict.fromkeys(targets)):
        if installed(t) and not force and (manifest(t) or {}).get("commit") == CATALOG["commit"]:
            skipped.append(t)
            continue
        if verbose:
            print(tr("everything.installing", i + 1, len(targets), t), flush=True)
        try:
            install_app(t, source, log=(lambda s: print(s, end="", flush=True)) if verbose else (lambda s: None))
            done.append(t)
        except FoxError as e:
            failed.append({"app": t, "code": e.code, "message": e.message})
    msg = tr("everything.installed_already_up_to_date_failed", len(done), len(skipped), len(failed))
    if failed and not done and not skipped:
        raise FoxError("ERROR", msg, details={"failed": failed})
    return {"message": msg, "installed": done, "skipped": skipped, "failed": failed}


def ev_uninstall(ctx: Context, app: str) -> dict:
    _need(app)
    shutil.rmtree(app_dir(app), ignore_errors=True)
    return {"message": tr("everything.uninstalled_workspace_data_in", app, app), "app": app}


def ev_commands(ctx: Context, app: str) -> dict:
    from ..kernel import REGISTRY
    _need(app)
    cmds = [c for c in REGISTRY.values() if c.app == app]
    return {"app": app, "count": len(cmds), "commands": [
        {"command": c.name, "id": c.id, "tool": c.tool_name, "cli": c.usage(), "summary": c.summary, "permission": c.permission,
         "params": c.input_schema()} for c in cmds]}


def ev_run(ctx: Context, app: str, command: str, args: dict | None = None) -> dict:
    from ..kernel import invoke
    _need(app)
    cid = f"{app}.{'.'.join(command.replace('.', ' ').split())}"
    return {"app": app, "command": cid, "result": invoke(cid, args or {}, ctx)}


APPP = Param("app", "string", tr("everything.app_id_see_foxos_everything_list"), required=True, positional=True, metavar="APP")
register(Command("everything", "list", tr("everything.list_the_51_everything_apps_group"), ev_list,
                 params=[Param("group", "string", tr("everything.show_only_one_group"), enum=list(GROUPS)), Param("installed_only", "boolean", tr("everything.list_only_installed_apps"), cli_flag="--installed")],
                 examples=["foxos everything list", "foxos everything list --group office --json"]))
register(Command("everything", "info", tr("everything.show_an_app_s_details_license_and"), ev_info, params=[APPP], examples=["foxos everything info tasks --json"]))
register(Command("everything", "install", tr("everything.build_and_install_an_app_locally"), ev_install,
                 params=[Param("apps", "array", tr("everything.app_id"), positional=True, items={"type": "string"}, metavar="APP"),
                         Param("all", "boolean", tr("everything.install_all_51")), Param("group", "string", tr("everything.install_a_whole_group"), enum=list(GROUPS)),
                         Param("source", "string", tr("everything.use_a_local_upstream_repository")),
                         Param("force", "boolean", tr("everything.rebuild_even_if_installed"), cli_short="-f")],
                 examples=["foxos everything install tasks chess", "foxos everything install --group games", "foxos everything install --all"],
                 limits=[tr("everything.needs_git_node_js_22_12_and_npm_each")], permission="run"))
register(Command("everything", "commands", tr("everything.list_all_commands_of_an_app_semantic"), ev_commands, params=[APPP],
                 examples=["foxos everything commands tasks --json"]))
register(Command("everything", "run", tr("everything.run_any_command_of_an_app_same_as"), ev_run,
                 params=[APPP, Param("command", "string", tr("everything.command_such_as_task_create_or_ui"), required=True, positional=True, metavar="COMMAND"),
                         Param("args", "object", tr("everything.command_arguments_json_object"))],
                 examples=[tr("everything.foxos_everything_run_tasks_add_task")],
                 audited=False))
register(Command("everything", "icons", tr("everything.add_the_upstream_app_icons_to"), ev_icons,
                 params=[Param("source", "string", tr("everything.local_upstream_repository_path_by"))], examples=["foxos everything icons --json"], permission="modify"))
register(Command("everything", "uninstall", tr("everything.uninstall_an_app_workspace_data_is"), ev_uninstall, params=[APPP], permission="delete",
                 examples=["foxos everything uninstall chess"]))


# ---------------------------------------------------------------- 每个应用的通用命令
def _ensure_installed(app: str) -> None:
    if not installed(app):
        raise FoxError("DEPENDENCY_MISSING", tr("everything.is_not_installed", APPS[app]['name']), hint=f"foxos everything install {app}")


def _ui_lock(ctx: Context, app: str):
    # 同一应用实例同一时刻只允许一个调用者驱动界面（与文件写锁同一机制）
    return locks.write_lock(ctx.workspace, f"AppData/{app}/.ui", ctx.agent, max(ctx.lock_wait, 30.0))


def _bridge(ctx: Context, app: str, method: str, args: dict | None = None, mutate: bool = False):
    _ensure_installed(app)
    if mutate:
        with _ui_lock(ctx, app):
            return desktop_client.call(ctx.workspace, "ev.bridge", app, {"method": method, "args": args or {}}, agent=ctx.agent)
    return desktop_client.call(ctx.workspace, "ev.bridge", app, {"method": method, "args": args or {}}, agent=ctx.agent)


def _kv_path(ctx: Context, app: str) -> Path:
    return ctx.workspace.root / "AppData" / app / "kv.json"


def make_handlers(app: str) -> dict:
    name = APPS[app]["name"]

    def app_open(ctx, file=None, headless=False):
        _ensure_installed(app)
        rel = ctx.rel(file) if file else None
        st = desktop_client.call(ctx.workspace, "ev.open", app, {"file": rel, "window": not headless}, agent=ctx.agent)
        return {"message": tr("everything.opened", name) + (tr("everything.text_2", rel) if rel else ""), **st}

    def app_close(ctx):
        return {"message": tr("everything.closed", name), **desktop_client.call(ctx.workspace, "ev.close", app, agent=ctx.agent)}

    def app_reset(ctx):
        return {"message": tr("everything.reset_cleared_its_data_in_this", name), **desktop_client.call(ctx.workspace, "ev.reset", app, agent=ctx.agent)}

    def app_status(ctx):
        try:
            return desktop_client.call(ctx.workspace, "ev.status", app, agent=ctx.agent) if desktop_client._info(ctx.workspace) else {"app": app, "installed": installed(app), "running": False, "mode": None}
        except FoxError:
            return {"app": app, "installed": installed(app), "running": False, "mode": None}

    def file_open(ctx, path):
        return app_open(ctx, file=path)

    def ui_snapshot(ctx, all=False, limit=400):
        return _bridge(ctx, app, "snapshot", {"all": all, "limit": limit})

    def ui_text(ctx):
        return {"text": _bridge(ctx, app, "text")}

    def ui_click(ctx, ref=None, name=None, role=None, force=False):
        if not ref and not name:
            raise FoxError("USAGE", tr("everything.needs_ref_or_name"))
        return {"clicked": _bridge(ctx, app, "click", {"ref": ref, "name": name, "role": role, "force": force}, mutate=True)}

    def ui_type(ctx, text, ref=None, clear=False):
        return {"element": _bridge(ctx, app, "type", {"ref": ref, "text": text, "clear": clear}, mutate=True)}

    def ui_set(ctx, ref, value, force=False):
        return {"element": _bridge(ctx, app, "setValue", {"ref": ref, "value": value, "force": force}, mutate=True)}

    def ui_press(ctx, key, ref=None):
        return _bridge(ctx, app, "press", {"key": key, "ref": ref}, mutate=True)

    def ui_screenshot(ctx, out=None):
        r = _bridge(ctx, app, "screenshot")
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(base64.b64decode(r["png_base64"]))
            return {"message": tr("everything.saved_screenshot", ctx.rel(out)), "path": ctx.rel(out), "width": r["width"], "height": r["height"]}
        return r

    def data_list(ctx, pattern="*"):
        p = _kv_path(ctx, app)
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        rx = re.compile("^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$")
        keys = sorted(k for k in d if rx.match(k))
        return {"count": len(keys), "keys": keys}

    def data_get(ctx, key):
        p = _kv_path(ctx, app)
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        if key not in d:
            raise FoxError("NOT_FOUND", tr("everything.has_no_data_key", app, key))
        return {"key": key, "value": d[key]}

    def module_list(ctx):
        return {"modules": _bridge(ctx, app, "modules")}

    def module_call(ctx, target, args=None):
        return {"result": _bridge(ctx, app, "invoke", {"target": target, "args": args or []}, mutate=True)}

    def module_read(ctx, target):
        return {"value": _bridge(ctx, app, "read", {"target": target})}

    def op_list(ctx):
        ops = load_ops(app)
        return {"count": len(ops), "bound": sum(1 for o in ops if o.get("binding", {}).get("kind") not in (None, "none")), "ops": [
            {k: o.get(k) for k in ("id", "summary", "ui", "params", "undoable")} | {"binding": (o.get("binding") or {}).get("kind", "none"), "cli": _op_cli(app, o)} for o in ops]}

    return dict(app_open=app_open, app_close=app_close, app_reset=app_reset, app_status=app_status, file_open=file_open, ui_snapshot=ui_snapshot, ui_text=ui_text,
                ui_click=ui_click, ui_type=ui_type, ui_set=ui_set, ui_press=ui_press, ui_screenshot=ui_screenshot, data_list=data_list,
                data_get=data_get, module_list=module_list, module_call=module_call, module_read=module_read, op_list=op_list)


# ---------------------------------------------------------------- 操作清单 → 语义命令
_OPS_CACHE: dict[str, list] = {}


def load_ops(app: str) -> list:
    if app not in _OPS_CACHE:
        f = DATA / "ops" / f"{app}.json"
        try:
            _OPS_CACHE[app] = json.loads(f.read_text(encoding="utf-8")).get("ops", [])
        except (OSError, ValueError):
            _OPS_CACHE[app] = []
    return _OPS_CACHE[app]


def _op_cli(app: str, o: dict) -> str:
    return f"foxos {app} {o['resource']} {o['verb']}"


def _op_example(app: str, o: dict) -> str:
    import shlex
    parts = [_op_cli(app, o)]
    for p in o.get("params", []):
        if p.get("required") and p.get("positional"):
            ex = (o.get("ui") or {}).get("examples") or []
            v = ex[0] if p["name"] == "target" and ex else (p.get("enum") or [tr("everything.examples")])[0]
            parts.append(shlex.quote(str(v)))
    return " ".join(parts) + " --json"


def _subst(v, values: dict):
    if isinstance(v, str):
        m = re.fullmatch(r"\{\{(\w+)\}\}", v)
        if m:
            return values.get(m.group(1))
        return re.sub(r"\{\{(\w+)\}\}", lambda mm: "" if values.get(mm.group(1)) is None else str(values.get(mm.group(1))), v)
    if isinstance(v, list):
        return [_subst(x, values) for x in v]
    if isinstance(v, dict):
        return {k: _subst(x, values) for k, x in v.items()}
    return v


def _op_handler(app: str, op: dict):
    def handler(ctx, **values):
        b = op["binding"]
        raw = [s for s in b.get("steps", []) if not s.get("press_if") or values.get(s["press_if"])]
        steps = _subst([{k: v for k, v in s.items() if k != "press_if"} for s in raw], values)
        if b.get("open"):
            _ensure_installed(app)
        results = _bridge(ctx, app, "run", {"steps": steps}, mutate=op.get("permission", "modify") != "read")
        return {"message": tr("everything.text", APPS[app]['name'], op['summary']), "op": op["id"], "results": results}
    return handler


def _app_command_list(app: str) -> list[str]:
    from ..kernel import REGISTRY
    return sorted(c.cli for c in REGISTRY.values() if c.app == app)


GENERIC = [
    ("app open", tr("everything.open_the_app_desktop_window_headless"), "app_open", [Param("file", "string", tr("everything.also_open_a_file_from_the_workspace"), path="read"), Param("headless", "boolean", tr("everything.don_t_show_a_window"))], "run"),
    ("app close", tr("everything.close_the_app_instance"), "app_close", [], "run"),
    ("app status", tr("everything.whether_the_app_is_installed_and"), "app_status", [], "read"),
    ("app reset", tr("everything.reset_the_app_close_the_instance_and"), "app_reset", [], "delete"),
    ("file open", tr("everything.open_a_workspace_file_in_the_app"), "file_open", [Param("path", "string", tr("common.file_path"), required=True, positional=True, path="read", metavar="PATH")], "run"),
    ("ui snapshot", tr("everything.accessibility_snapshot_of_the_ui"), "ui_snapshot", [Param("all", "boolean", tr("everything.include_invisible_elements")), Param("limit", "integer", tr("everything.maximum_number_of_elements_returned"), default=400)], "read"),
    ("ui text", tr("everything.read_the_visible_text_of_the_ui"), "ui_text", [], "read"),
    ("ui click", tr("everything.click_a_control_by_ref_or_name_the"), "ui_click", [Param("ref", "string", tr("everything.element_reference_returned_by")), Param("name", "string", tr("everything.find_by_accessible_name")), Param("role", "string", tr("everything.limit_to_a_role_such_as_button")), Param("force", "boolean", tr("everything.click_even_when_a_dialog_covers_the"))], "modify"),
    ("ui type", tr("everything.type_text_into_a_control_real_input"), "ui_type", [Param("text", "string", tr("everything.text_to_type"), required=True, positional=True, metavar="TEXT"), Param("ref", "string", tr("everything.element_reference_the_focused")), Param("clear", "boolean", tr("everything.clear_first"))], "modify"),
    ("ui set", tr("everything.set_the_value_of_an_input_select"), "ui_set", [Param("ref", "string", tr("everything.element_reference"), required=True), Param("value", "string", tr("everything.value"), required=True), Param("force", "boolean", tr("everything.set_even_when_the_control_is_covered"))], "modify"),
    ("ui press", tr("everything.press_a_key_or_shortcut_such_as"), "ui_press", [Param("key", "string", tr("everything.key"), required=True, positional=True, metavar="KEY"), Param("ref", "string", tr("everything.element_reference_to_focus_first"))], "modify"),
    ("ui screenshot", tr("everything.screenshot_of_the_app_window_png"), "ui_screenshot", [Param("out", "string", tr("everything.save_to_a_workspace_path"), path="write")], "read"),
    ("data list", tr("everything.list_the_data_keys_the_app_saved"), "data_list", [Param("pattern", "string", tr("everything.wildcard_pattern"), default="*", positional=True, metavar="PATTERN")], "read"),
    ("data get", tr("everything.read_one_item_the_app_saved"), "data_get", [Param("key", "string", tr("everything.data_key"), required=True, positional=True, metavar="KEY")], "read"),
    ("module list", tr("everything.list_the_app_s_own_es_modules_and"), "module_list", [], "read"),
    ("module read", tr("everything.read_a_value_from_an_app_module_such"), "module_read", [Param("target", "string", tr("everything.module_path_export_property_such_as"), required=True, positional=True, metavar="TARGET")], "read"),
    ("module call", tr("everything.call_the_app_s_own_function_method"), "module_call", [Param("target", "string", tr("everything.module_path_export_method"), required=True, positional=True, metavar="TARGET"), Param("args", "array", tr("everything.arguments_json_array"), items={})], "modify"),
    ("op list", tr("everything.list_the_app_s_operation_inventory"), "op_list", [], "read"),
]


def register_everything_apps() -> None:
    for a in CATALOG["apps"]:
        app = a["id"]
        register_app(app, a["name"], tr("everything.alternative_to_an_upstream", GROUPS[a['group']]['zh'], a['alternativeTo']),
                     limits=[tr("everything.license", a['license'])])
        h = make_handlers(app)
        for verb, summary, key, params, perm in GENERIC:
            ex = {"app open": [f"foxos {app} app open", f"foxos {app} app open --headless --json"], "ui snapshot": [f"foxos {app} ui snapshot --json"],
                  "ui click": [f"foxos {app} ui click --ref e12", f"foxos {app} ui click --name Settings"], "ui type": [f"foxos {app} ui type 'hello' --ref e5"],
                  "ui press": [f"foxos {app} ui press mod+z"], "data list": [f"foxos {app} data list --json"], "op list": [f"foxos {app} op list --json"],
                  "module list": [f"foxos {app} module list --json"]}.get(verb, [f"foxos {app} {verb} --json" if not any(p.required for p in params) else f"foxos {app} {verb} " + " ".join("X" for p in params if p.required and p.positional)])
            register(Command(app, verb, summary, h[key], params=list(params), examples=ex, permission=perm,
                             audited=perm != "read" or verb in ("ui screenshot",)))
        seen = set()
        for o in load_ops(app):
            b = o.get("binding") or {}
            if b.get("kind") in (None, "none"):
                continue
            verb = f"{o['resource']} {o['verb']}"
            if verb in seen or verb.split()[0] in ("app", "file", "ui", "data", "module", "op"):
                continue
            seen.add(verb)
            params = [Param(p["name"], p.get("type", "string"), p.get("description", ""), required=p.get("required", False), default=p.get("default"),
                            enum=p.get("enum"), positional=p.get("positional", False), metavar=p["name"].upper()) for p in o.get("params", [])]
            ui = o.get("ui") or {}
            register(Command(app, verb, o["summary"], _op_handler(app, o), params=params,
                             description=tr("everything.ui", ui.get('path', '')) + (tr("everything.shortcut", ui['shortcut']) if ui.get("shortcut") else "") + tr("everything.effect", o.get('effect', '')),
                             examples=o.get("examples") or [_op_example(app, o)], permission=o.get("permission", "modify")))


register_everything_apps()
