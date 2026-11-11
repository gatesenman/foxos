#!/usr/bin/env python3
"""生成狐狸OS 的 xfwm4 窗口装饰与 GTK 主题目录（纯标准库，输出 XPM 文本）。"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# 暖色、克制的狐狸配色：浅色窗框配深色壁纸，关闭按钮悬停时才用橙色。
TITLE_H = 32
BORDER = 1
BTN = 20
PAD = 6

C = {
    "title_active": "#F7F1E8",
    "title_inactive": "#EDE4D8",
    "border_active": "#C9B6A1",
    "border_inactive": "#D9CBBA",
    "text_active": "#2C241C",
    "text_inactive": "#8A7A6C",
    "icon": "#3D3228",
    "icon_dim": "#9A8A7A",
    "close_hover_bg": "#D96B2B",
    "close_hover_fg": "#FFF8F0",
    "close_press_bg": "#B5551F",
    "btn_hover_bg": "#E8DCCE",
    "btn_press_bg": "#D4C4B0",
}


def xpm(pixels: list[list[str]], names: dict[str, str]) -> str:
    """pixels[y][x] 是 names 里的单字符键。"""
    h = len(pixels)
    w = len(pixels[0]) if h else 0
    # None / space meaning transparent uses c None
    used = sorted({p for row in pixels for p in row})
    lines = [
        "/* XPM */",
        f"static char * pix[] = {{",
        f"\"{w} {h} {len(used)} 1\",",
    ]
    for ch in used:
        color = names[ch]
        if color.lower() == "none":
            lines.append(f"\"{ch} c None\",")
        else:
            lines.append(f"\"{ch} c {color}\",")
    for i, row in enumerate(pixels):
        comma = "," if i < h - 1 else ""
        lines.append('"' + "".join(row) + f'"{comma}')
    lines.append("};")
    lines.append("")
    return "\n".join(lines)


def solid(w: int, h: int, color: str) -> str:
    return xpm([["x"] * w for _ in range(h)], {"x": color})


def title_bar(active: bool, width: int = 16) -> str:
    bg = C["title_active"] if active else C["title_inactive"]
    border = C["border_active"] if active else C["border_inactive"]
    rows = []
    for y in range(TITLE_H):
        row = []
        for x in range(width):
            if y == 0:
                row.append("b")
            else:
                row.append("g")
        rows.append(row)
    return xpm(rows, {"b": border, "g": bg})


def corner(side: str, active: bool, top: bool) -> str:
    bg = C["title_active"] if active else C["title_inactive"]
    if not top:
        bg = C["title_active"] if active else C["title_inactive"]
    border = C["border_active"] if active else C["border_inactive"]
    w, h = 8, TITLE_H if top else 8
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            edge = (y == 0 if top else y == h - 1) or (x == 0 if side == "left" else x == w - 1)
            # bottom corners also need vertical border on outer x, and bottom edge
            if not top:
                edge = (y == h - 1) or (x == 0 if side == "left" else x == w - 1)
            row.append("b" if edge else "g")
        rows.append(row)
    # top corners: top edge + outer side, fill is title bg
    if top:
        rows = []
        for y in range(h):
            row = []
            for x in range(w):
                if y == 0 or (x == 0 if side == "left" else x == w - 1):
                    row.append("b")
                else:
                    row.append("g")
            rows.append(row)
    return xpm(rows, {"b": border, "g": bg})


def side(active: bool) -> str:
    border = C["border_active"] if active else C["border_inactive"]
    return solid(BORDER, 16, border)


def bottom(active: bool) -> str:
    border = C["border_active"] if active else C["border_inactive"]
    return solid(16, BORDER, border)


def button(kind: str, state: str) -> str:
    """kind: close/hide/maximize/maximize-toggled/menu; state: active/inactive/prelight/pressed."""
    size = BTN
    active = state != "inactive"
    if kind == "close" and state == "prelight":
        bg, fg = C["close_hover_bg"], C["close_hover_fg"]
    elif kind == "close" and state == "pressed":
        bg, fg = C["close_press_bg"], C["close_hover_fg"]
    elif state == "prelight":
        bg, fg = C["btn_hover_bg"], C["icon"]
    elif state == "pressed":
        bg, fg = C["btn_press_bg"], C["icon"]
    elif state == "inactive":
        bg, fg = C["title_inactive"], C["icon_dim"]
    else:
        bg, fg = C["title_active"], C["icon"]

    # transparent margin so the button sits in the title bar
    # We'll fill entire button with title-matching default, then a rounded-ish inner chip on hover.
    title_bg = C["title_active"] if active else C["title_inactive"]
    rows = [[title_bg] * size for _ in range(size)]  # placeholder, we'll map to chars later

    def setp(x, y, color_key="fg"):
        if 0 <= x < size and 0 <= y < size:
            rows[y][x] = color_key

    # background chip with slight inset
    inset = 2
    for y in range(inset, size - inset):
        for x in range(inset, size - inset):
            # cut corners by 2px for a soft square
            if (x in (inset, size - inset - 1) and y in (inset, size - inset - 1)):
                continue
            rows[y][x] = "bg"

    cx, cy = size // 2, size // 2
    if kind == "close":
        for i in range(-5, 6):
            setp(cx + i, cy + i)
            setp(cx + i, cy - i)
            setp(cx + i + 1, cy + i)
            setp(cx + i + 1, cy - i)
    elif kind == "hide":
        for x in range(cx - 5, cx + 6):
            setp(x, cy + 4)
            setp(x, cy + 5)
    elif kind in ("maximize", "maximize-toggled"):
        x0, y0, x1, y1 = cx - 5, cy - 5, cx + 5, cy + 5
        if kind == "maximize-toggled":
            x0, y0, x1, y1 = cx - 4, cy - 3, cx + 4, cy + 5
            # back window
            for x in range(cx - 2, cx + 7):
                setp(x, cy - 5)
            for y in range(cy - 5, cy + 2):
                setp(cx + 6, y)
        for x in range(x0, x1 + 1):
            setp(x, y0)
            setp(x, y1)
        for y in range(y0, y1 + 1):
            setp(x0, y)
            setp(x1, y)
        # slightly thicker top edge
        for x in range(x0, x1 + 1):
            setp(x, y0 + 1)
    elif kind == "menu":
        for i, y in enumerate((cy - 4, cy, cy + 4)):
            for x in range(cx - 5, cx + 6):
                setp(x, y)
    elif kind == "shade":
        for x in range(cx - 5, cx + 6):
            setp(x, cy - 3)
        # small chevron
        for i in range(0, 5):
            setp(cx - i, cy + i - 1)
            setp(cx + i, cy + i - 1)
    elif kind == "stick":
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                setp(x, y)
        for x in range(cx - 5, cx + 6):
            setp(x, cy)
        for y in range(cy - 5, cy + 6):
            setp(cx, y)

    # map colors
    pix = []
    for y in range(size):
        row = []
        for x in range(size):
            v = rows[y][x]
            if v == "fg":
                row.append("f")
            elif v == "bg":
                row.append("b")
            else:
                row.append("t")
        pix.append(row)
    return xpm(pix, {"t": title_bg, "b": bg, "f": fg})


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def themerc() -> str:
    return f"""# 狐狸OS xfwm4 主题
active_text_color={C['text_active']}
inactive_text_color={C['text_inactive']}
button_offset={PAD}
button_spacing=4
full_width_title=true
title_shadow_active=false
title_shadow_inactive=false
title_horizontal_offset=10
title_vertical_offset_active=1
title_vertical_offset_inactive=1
shadow_delta_x=0
shadow_delta_y=2
shadow_delta_width=0
shadow_delta_height=0
placement_ratio=20
"""


def gtk_index() -> str:
    return """[Desktop Entry]
Type=X-GNOME-VisualStyle
Name=FoxOS
Comment=狐狸OS 桌面主题
Name[en]=FoxOS
Comment[en]=FoxOS desktop theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=FoxOS
MetacityTheme=FoxOS
IconTheme=Adwaita
CursorTheme=Adwaita
ButtonLayout=menu:minimize,maximize,close
"""


GTK_CSS = Path(__file__).with_name("gtk-3.0").joinpath("gtk.css")


def gtk2_rc() -> str:
    return '''
gtk-color-scheme = "bg_color:#F7F1E8\\nfg_color:#2C241C\\nselected_bg_color:#D96B2B\\nselected_fg_color:#FFF8F0\\nbase_color:#FFF8F0\\ntext_color:#2C241C"
gtk-font-name = "Noto Sans CJK SC 11"
style "default" {
  bg[NORMAL] = "#F7F1E8"
  fg[NORMAL] = "#2C241C"
  bg[SELECTED] = "#D96B2B"
  fg[SELECTED] = "#FFF8F0"
  base[NORMAL] = "#FFF8F0"
  text[NORMAL] = "#2C241C"
}
class "GtkWidget" style "default"
'''


def generate(dest: Path) -> None:
    dest = Path(dest)
    xfwm = dest / "xfwm4"
    if xfwm.exists():
        shutil.rmtree(xfwm)
    write(dest / "index.theme", gtk_index())
    css_src = Path(__file__).resolve().parent / "gtk-3.0" / "gtk.css"
    css_dst = dest / "gtk-3.0" / "gtk.css"
    css_dst.parent.mkdir(parents=True, exist_ok=True)
    if css_src.exists():
        shutil.copy2(css_src, css_dst)
    write(dest / "gtk-2.0" / "gtkrc", gtk2_rc())
    # gtk4: just import Adwaita
    write(dest / "gtk-4.0" / "gtk.css", '@import url("resource:///org/gtk/libgtk/theme/Adwaita/gtk.css");\n')

    write(xfwm / "themerc", themerc())
    for active, suffix in ((True, "active"), (False, "inactive")):
        write(xfwm / f"title-1-{suffix}.xpm", title_bar(active, 8))
        write(xfwm / f"title-2-{suffix}.xpm", title_bar(active, 8))
        write(xfwm / f"title-3-{suffix}.xpm", title_bar(active, 16))
        write(xfwm / f"title-4-{suffix}.xpm", title_bar(active, 8))
        write(xfwm / f"title-5-{suffix}.xpm", title_bar(active, 8))
        write(xfwm / f"top-left-{suffix}.xpm", corner("left", active, True))
        write(xfwm / f"top-right-{suffix}.xpm", corner("right", active, True))
        write(xfwm / f"left-{suffix}.xpm", side(active))
        write(xfwm / f"right-{suffix}.xpm", side(active))
        write(xfwm / f"bottom-{suffix}.xpm", bottom(active))
        write(xfwm / f"bottom-left-{suffix}.xpm", corner("left", active, False))
        write(xfwm / f"bottom-right-{suffix}.xpm", corner("right", active, False))

    kinds = ("close", "hide", "maximize", "maximize-toggled", "menu", "shade", "stick", "stick-toggled")
    states = ("active", "inactive", "prelight", "pressed")
    for kind in kinds:
        src_kind = "stick" if kind == "stick-toggled" else kind
        for st in states:
            write(xfwm / f"{kind}-{st}.xpm", button(src_kind, st))

    print(f"generated theme at {dest}")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/usr/share/themes/FoxOS")
    generate(out)
