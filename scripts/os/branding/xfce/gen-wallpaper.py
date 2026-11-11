#!/usr/bin/env python3
"""生成狐狸OS 默认壁纸：暖色渐变、柔和的山脊线，居中的狐狸标志与「狐狸OS」字样。

用法：gen-wallpaper.py ICON.png OUT.png [宽 高]
壁纸为本项目自制，只用到仓库里的狐狸OS 图标和系统 Noto CJK 字体（SIL OFL 1.1）。
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
]
FONT_REG = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
]


def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size, index=2)  # SC
        except OSError:
            continue
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    icon_path, out = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
    s = h / 1080

    # 背景：左上深茄紫到右下暖棕的斜向渐变
    top = (24, 18, 28)
    bottom = (52, 30, 24)
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    for y in range(h):
        for x in range(0, w):
            t = min(1.0, max(0.0, (x / w) * 0.35 + (y / h) * 0.65))
            px[x, y] = lerp(top, bottom, t)
    img = grad.convert("RGBA")

    # 中央偏上的暖色光晕
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = w // 2, int(h * 0.42)
    for r, a in ((int(520 * s), 38), (int(360 * s), 46), (int(220 * s), 40)):
        gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(217, 107, 43, a))
    glow = glow.filter(ImageFilter.GaussianBlur(int(140 * s)))
    img = Image.alpha_composite(img, glow)

    # 底部几层像狐尾一样的柔和山脊
    ridges = [
        (0.70, 70, (92, 44, 30, 120), 1.3, 0.0),
        (0.78, 58, (138, 62, 30, 110), 1.8, 1.2),
        (0.86, 46, (193, 90, 36, 90), 2.4, 2.1),
        (0.93, 30, (232, 138, 79, 70), 3.0, 0.6),
    ]
    for base, amp, color, freq, phase in ridges:
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        pts = []
        for i in range(0, w + 8, 8):
            x = i
            y = h * base + amp * s * math.sin(freq * math.pi * x / w + phase) \
                + amp * 0.35 * s * math.sin(2.7 * freq * math.pi * x / w + phase * 1.7)
            pts.append((x, y))
        pts += [(w, h), (0, h)]
        ld.polygon(pts, fill=color)
        layer = layer.filter(ImageFilter.GaussianBlur(int(2 * s) or 1))
        img = Image.alpha_composite(img, layer)

    # 居中标志（圆角 + 柔和投影）
    size = int(168 * s)
    icon = Image.open(icon_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=255)
    icon.putalpha(Image.composite(icon.getchannel("A"), mask, mask))
    ix, iy = (w - size) // 2, int(h * 0.42) - size // 2 - int(40 * s)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (ix + 6 * s, iy + 14 * s, ix + size + 6 * s, iy + size + 14 * s),
        radius=int(size * 0.22), fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(22 * s)))
    img = Image.alpha_composite(img, shadow)
    img.alpha_composite(icon, (ix, iy))

    # 字样
    d = ImageDraw.Draw(img)
    title = "狐狸OS"
    ft = font(FONT_BOLD, int(64 * s))
    tw = d.textlength(title, font=ft)
    ty = iy + size + int(34 * s)
    d.text(((w - tw) / 2, ty), title, font=ft, fill=(250, 240, 228, 255))
    sub = "F O X O S"
    fs = font(FONT_REG, int(20 * s))
    sw = d.textlength(sub, font=fs)
    d.text(((w - sw) / 2, ty + int(92 * s)), sub, font=fs, fill=(232, 170, 120, 220))

    img.convert("RGB").save(out, optimize=True)


if __name__ == "__main__":
    main()
