"""真实桌面 / 会话命令：窗口列表、聚焦、移动、键入、点击、截图、人工接管。

`foxos desktop …` 与 `foxos session …` 共用同一组处理函数（文档里两种写法都有效）。
默认走 XFCE / X11（wmctrl、xdotool、scrot），不是 Electron 里画的假窗口。
"""

from __future__ import annotations

from pathlib import Path

from ..i18n import tr
from ..kernel import Command, Context, Param, register, register_app
from ..session import get_backend


def _backend(ctx: Context):
    return get_backend(ctx.workspace)


def _claim(ctx: Context) -> None:
    """多个智能体共用一台机器：桌面输入同一时间只归一个智能体，另一个得到 CONFLICT。"""
    from .. import activity
    activity.claim_desktop(ctx.workspace, ctx.agent)


def desktop_status(ctx: Context) -> dict:
    from .system import control_status

    try:
        st = _backend(ctx).status()
    except Exception as e:  # noqa: BLE001 — 把后端错误放进 status，便于诊断
        from ..errors import FoxError
        if isinstance(e, FoxError):
            st = {"backend": None, "available": False, "error": e.to_dict()}
        else:
            raise
    paused = control_status(ctx)
    return {**st, "paused": paused.get("paused"), **({"takeover": paused["state"]} if paused.get("state") else {})}


def desktop_windows(ctx: Context) -> dict:
    wins = _backend(ctx).windows()
    return {"count": len(wins), "windows": wins}


def desktop_focus(ctx: Context, window: str) -> dict:
    _claim(ctx)
    r = _backend(ctx).focus(window)
    return {"message": tr("desktop.focused_window", window), **r}


def desktop_close(ctx: Context, window: str) -> dict:
    _claim(ctx)
    r = _backend(ctx).close(window)
    return {"message": tr("desktop.closed_window", window), **r}


def desktop_move(ctx: Context, window: str, x: int, y: int) -> dict:
    _claim(ctx)
    r = _backend(ctx).move(window, int(x), int(y))
    return {"message": tr("desktop.moved_window", window, x, y), **r}


def desktop_resize(ctx: Context, window: str, width: int, height: int) -> dict:
    _claim(ctx)
    r = _backend(ctx).resize(window, int(width), int(height))
    return {"message": tr("desktop.resized_window", window, width, height), **r}


def desktop_launch(ctx: Context, command: list) -> dict:
    _claim(ctx)
    argv = [str(c) for c in (command or [])]
    if argv and argv[0].lower() in _browser_aliases():
        # `foxos desktop launch chrome [URL…]`：用狐狸OS 的 Chrome 启动参数（CDP 开启时只听 127.0.0.1）
        from .browser import chrome_argv
        argv = chrome_argv(ctx, argv[1:])
    elif len(argv) == 1 and " " in argv[0]:
        argv = ["/bin/sh", "-c", argv[0]]
    r = _backend(ctx).launch(argv)
    return {"message": tr("desktop.launched", " ".join(argv)), **r}


def _browser_aliases() -> set[str]:
    from .browser import ALIASES
    return ALIASES


def desktop_type(ctx: Context, text: str) -> dict:
    _claim(ctx)
    r = _backend(ctx).type_text(text)
    return {"message": tr("desktop.typed_characters", r.get("length", len(text))), **r}


def desktop_key(ctx: Context, keys: str) -> dict:
    _claim(ctx)
    r = _backend(ctx).key(keys)
    return {"message": tr("desktop.sent_keys", keys), **r}


def desktop_click(ctx: Context, x: int | None = None, y: int | None = None, button: int = 1, element: str | None = None) -> dict:
    _claim(ctx)
    if element:
        from ..cu import a11y
        r = a11y.act(ctx.workspace, element, "click")
        return {"message": tr("a11y.clicked", element, r.get("role"), r.get("name")), **r}
    if x is None or y is None:
        from ..errors import FoxError
        raise FoxError("USAGE", tr("a11y.click_needs_target"))
    r = _backend(ctx).click(int(x), int(y), int(button or 1))
    return {"message": tr("desktop.clicked", x, y, button or 1), **r}


def desktop_screenshot(ctx: Context, path: str | None = None) -> dict:
    dest = ctx.workspace.root / (path or f".foxos/screenshots/session-{_ts()}.png")
    r = _backend(ctx).screenshot(dest)
    try:
        r["path"] = str(dest.relative_to(ctx.workspace.root))
    except ValueError:
        r["path"] = str(dest)
    return {"message": tr("desktop.saved_screenshot", r["path"]), **r}


def _ts() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def desktop_takeover(ctx: Context, reason: str | None = None, targets: list | None = None) -> dict:
    from .system import control_pause
    return control_pause(ctx, reason=reason, targets=targets)


def desktop_resume(ctx: Context, targets: list | None = None) -> dict:
    from .system import control_resume
    return control_resume(ctx, targets=targets)


def desktop_activity(ctx: Context) -> dict:
    from .. import activity
    return {"acting": activity.current(ctx.workspace), "desktop_owner": activity.desktop_owner(ctx.workspace)}


def desktop_release(ctx: Context) -> dict:
    from .. import activity
    return {"released": activity.release_desktop(ctx.workspace, ctx.agent)}


def _register_for(app: str) -> None:
    register(Command(app, "status", tr("desktop.show_session_and_takeover_status"), desktop_status,
                     examples=[f"foxos {app} status --json"], audited=False))
    register(Command(app, "windows", tr("desktop.list_real_compositor_windows"), desktop_windows,
                     examples=[f"foxos {app} windows --json"], audited=False))
    register(Command(app, "focus", tr("desktop.focus_a_window"), desktop_focus,
                     params=[Param("window", "string", tr("desktop.window_id_from_windows"), required=True, positional=True, metavar="WINDOW")],
                     examples=[f"foxos {app} focus 4278190080"], permission="run"))
    register(Command(app, "move", tr("desktop.move_a_window"), desktop_move,
                     params=[Param("window", "string", tr("desktop.window_id_from_windows"), required=True, positional=True, metavar="WINDOW"),
                             Param("x", "integer", tr("desktop.x_pixels"), required=True), Param("y", "integer", tr("desktop.y_pixels"), required=True)],
                     examples=[f"foxos {app} move 4278190080 --x 100 --y 80"], permission="modify"))
    register(Command(app, "resize", tr("desktop.resize_a_window"), desktop_resize,
                     params=[Param("window", "string", tr("desktop.window_id_from_windows"), required=True, positional=True, metavar="WINDOW"),
                             Param("width", "integer", tr("desktop.width_pixels"), required=True), Param("height", "integer", tr("desktop.height_pixels"), required=True)],
                     examples=[f"foxos {app} resize 4278190080 --width 800 --height 600"], permission="modify"))
    register(Command(app, "close", tr("desktop.close_a_window"), desktop_close,
                     params=[Param("window", "string", tr("desktop.window_id_from_windows"), required=True, positional=True, metavar="WINDOW")],
                     examples=[f"foxos {app} close 4278190080"], permission="modify"))
    register(Command(app, "launch", tr("desktop.launch_an_application_or_command"), desktop_launch,
                     params=[Param("command", "array", tr("desktop.command_and_arguments"), required=True, positional=True, items={"type": "string"}, metavar="CMD")],
                     examples=[f"foxos {app} launch chrome", f"foxos {app} launch -- xfce4-terminal", f"foxos {app} launch -- xfce4-terminal -T notes"], permission="run"))
    register(Command(app, "type", tr("desktop.type_text_into_the_focused_window"), desktop_type,
                     params=[Param("text", "string", tr("desktop.text_to_type"), required=True, positional=True, metavar="TEXT")],
                     examples=[f"foxos {app} type 'hello'"], permission="modify"))
    register(Command(app, "key", tr("desktop.send_key_combinations"), desktop_key,
                     params=[Param("keys", "string", tr("desktop.key_names_for_example_return_or"), required=True, positional=True, metavar="KEYS")],
                     examples=[f"foxos {app} key Return", f"foxos {app} key ctrl+c"], permission="modify"))
    register(Command(app, "click", tr("desktop.click_at_screen_coordinates"), desktop_click,
                     params=[Param("x", "integer", tr("desktop.x_pixels")), Param("y", "integer", tr("desktop.y_pixels")),
                             Param("button", "integer", tr("desktop.mouse_button_1_left_2_middle_3"), default=1),
                             Param("element", "string", tr("a11y.p_element"))],
                     examples=[f"foxos {app} click --x 400 --y 300", f"foxos {app} click --element e12"], permission="modify"))
    register(Command(app, "screenshot", tr("desktop.capture_the_session"), desktop_screenshot,
                     params=[Param("path", "string", tr("desktop.workspace_relative_png_path"), path="write")],
                     examples=[f"foxos {app} screenshot --path shots/desk.png"], permission="read"))
    register(Command(app, "activity", tr("desktop.who_is_acting"), desktop_activity,
                     examples=[f"foxos {app} activity --json"], audited=False))
    register(Command(app, "release", tr("desktop.release_input"), desktop_release,
                     examples=[f"foxos {app} release"], permission="run"))
    register(Command(app, "takeover", tr("desktop.human_takeover_pause_agent_writes"), desktop_takeover,
                     params=[Param("reason", "string", tr("system.reason_for_pausing_written_to_the")),
                             Param("targets", "array", tr("system.pause_targets"), items={"type": "string"}, cli_flag="--only", cli_repeat=True, metavar="IDENTITY")],
                     examples=[tr("desktop.foxos_app_takeover_reason", app)],
                     limits=[tr("system.only_the_human_identity_can_run_this")], permission="modify"))
    register(Command(app, "resume", tr("desktop.end_human_takeover"), desktop_resume,
                     params=[Param("targets", "array", tr("system.resume_targets"), items={"type": "string"}, cli_flag="--only", cli_repeat=True, metavar="IDENTITY")],
                     examples=[f"foxos {app} resume"],
                     limits=[tr("system.only_the_human_identity_can_run_this")], permission="modify"))


# ------------------------------------------------------------------ 无障碍树（AT-SPI）与视觉定位

def desktop_tree(ctx: Context, app: str | None = None, pid: int | None = None, all: bool = False, hidden: bool = False,
                 max_nodes: int = 600, full: bool = False) -> dict:
    from ..cu import a11y
    r = a11y.tree(ctx.workspace, app=app, pid=pid, all_apps=all, hidden=hidden, max_nodes=max_nodes)
    if not full:
        r.pop("nodes", None)
    return r


def desktop_find(ctx: Context, role: str | None = None, name: str | None = None, app: str | None = None, regex: bool = False,
                 limit: int = 20) -> dict:
    from ..cu import a11y
    return a11y.find(ctx.workspace, role=role, name=name, app=app, regex=regex, limit=limit)


def desktop_apps(ctx: Context) -> dict:
    from ..cu import a11y
    apps = a11y.apps()
    return {"count": len(apps), "apps": apps}


def element_click(ctx: Context, ref: str) -> dict:
    _claim(ctx)
    from ..cu import a11y
    r = a11y.act(ctx.workspace, ref, "click")
    return {"message": tr("a11y.clicked", ref, r.get("role"), r.get("name")), **r}


def element_focus(ctx: Context, ref: str) -> dict:
    _claim(ctx)
    from ..cu import a11y
    return a11y.act(ctx.workspace, ref, "focus")


def element_read(ctx: Context, ref: str, limit: int = 20000) -> dict:
    from ..cu import a11y
    return a11y.act(ctx.workspace, ref, "read", limit=int(limit))


def element_set_text(ctx: Context, ref: str, text: str, append: bool = False) -> dict:
    _claim(ctx)
    from ..cu import a11y
    r = a11y.act(ctx.workspace, ref, "insert_text" if append else "set_text", text=text)
    return {"message": tr("a11y.set_text", ref, len(text)), **r}


def element_action(ctx: Context, ref: str, name: str) -> dict:
    _claim(ctx)
    from ..cu import a11y
    return a11y.act(ctx.workspace, ref, "action", name=name)


def desktop_ground(ctx: Context, description: str, click: bool = False, kind: str | None = None, button: int = 1) -> dict:
    """截图 → 视觉定位模型 → 坐标（可直接点击）。"""
    import tempfile
    from ..cu import grounding
    with tempfile.TemporaryDirectory() as td:
        shot = Path(td) / "screen.png"
        _backend(ctx).screenshot(shot)
        png = shot.read_bytes()
    r = grounding.ground(png, description, kind=kind)
    r["description"] = description
    if click:
        _claim(ctx)
        _backend(ctx).click(int(r["x"]), int(r["y"]), int(button or 1))
        r["clicked"] = True
        r["message"] = tr("a11y.ground_clicked", description, r["x"], r["y"])
    return r


def _register_a11y(app: str) -> None:
    REF = Param("ref", "string", tr("a11y.p_ref"), required=True, positional=True, metavar="REF")
    register(Command(app, "tree", tr("a11y.c_tree"), desktop_tree,
                     params=[Param("app", "string", tr("a11y.p_app")), Param("pid", "integer", tr("a11y.p_pid")),
                             Param("all", "boolean", tr("a11y.p_all"), default=False), Param("hidden", "boolean", tr("a11y.p_hidden"), default=False),
                             Param("max_nodes", "integer", tr("a11y.p_max_nodes"), default=600),
                             Param("full", "boolean", tr("a11y.p_full"), default=False)],
                     examples=[f"foxos {app} tree", f"foxos {app} tree --app mousepad --json"],
                     limits=[tr("a11y.l_tree")], permission="read", audited=False))
    register(Command(app, "find", tr("a11y.c_find"), desktop_find,
                     params=[Param("role", "string", tr("a11y.p_role")), Param("name", "string", tr("a11y.p_name")),
                             Param("app", "string", tr("a11y.p_app")), Param("regex", "boolean", tr("a11y.p_regex"), default=False),
                             Param("limit", "integer", tr("a11y.p_limit"), default=20)],
                     examples=[f"foxos {app} find --role 'push button' --name Save", f"foxos {app} find --app mousepad --role text"],
                     permission="read", audited=False))
    register(Command(app, "apps", tr("a11y.c_apps"), desktop_apps, examples=[f"foxos {app} apps --json"], permission="read", audited=False))
    register(Command(app, "element click", tr("a11y.c_click"), element_click, params=[REF],
                     examples=[f"foxos {app} element click e12"], permission="modify"))
    register(Command(app, "element focus", tr("a11y.c_focus"), element_focus, params=[REF],
                     examples=[f"foxos {app} element focus e7"], permission="modify"))
    register(Command(app, "element read", tr("a11y.c_read"), element_read,
                     params=[REF, Param("limit", "integer", tr("a11y.p_limit_chars"), default=20000)],
                     examples=[f"foxos {app} element read e7"], permission="read"))
    register(Command(app, "element set-text", tr("a11y.c_set_text"), element_set_text,
                     params=[REF, Param("text", "string", tr("a11y.p_text"), required=True, positional=True, metavar="TEXT", cli_stdin=True),
                             Param("append", "boolean", tr("a11y.p_append"), default=False)],
                     examples=[f"foxos {app} element set-text e7 'hello'"], permission="modify"))
    register(Command(app, "element action", tr("a11y.c_action"), element_action,
                     params=[REF, Param("name", "string", tr("a11y.p_action_name"), required=True, positional=True, metavar="ACTION")],
                     examples=[f"foxos {app} element action e9 activate"], permission="modify"))
    register(Command(app, "ground", tr("a11y.c_ground"), desktop_ground,
                     params=[Param("description", "string", tr("a11y.p_description"), required=True, positional=True, metavar="DESCRIPTION"),
                             Param("click", "boolean", tr("a11y.p_click"), default=False),
                             Param("kind", "string", tr("a11y.p_kind"), enum=["vlm", "ui-tars", "omniparser"]),
                             Param("button", "integer", tr("desktop.mouse_button_1_left_2_middle_3"), default=1)],
                     examples=[f"foxos {app} ground 'the Save button in the toolbar' --click"],
                     limits=[tr("a11y.l_ground")], permission="modify"))


register_app("desktop", tr("desktop.real_desktop_session"), tr("desktop.list_focus_move_and_input_on_the"))
register_app("session", tr("desktop.real_desktop_session"), tr("desktop.list_focus_move_and_input_on_the"))
_register_for("desktop")
_register_for("session")
_register_a11y("desktop")
_register_a11y("session")
