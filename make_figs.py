#!/usr/bin/env python3
"""Vẽ sáu hình sơ cứu hóc dị vật ra img/*.png.

Chạy:  python3 make_figs.py
Hình vẽ ở độ phân giải gấp ba rồi thu nhỏ lại cho nét.
"""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
OUT = HERE / 'img'
OUT.mkdir(exist_ok=True)

S = 3                      # hệ số siêu lấy mẫu
W, H = 640, 440            # kích thước cuối

BG      = (251, 247, 240)
ADULT   = (232, 222, 212)
ADULT_L = (178, 158, 152)
CHILD   = (250, 237, 234)
CHILD_L = (194, 84, 77)
ACCENT  = (158, 63, 57)
GROUND  = (224, 214, 202)
INK     = (51, 36, 31)
WARN    = (168, 91, 24)

def font(sz, bold=True):
    for p in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf',
              '/System/Library/Fonts/Supplemental/Arial.ttf',
              '/System/Library/Fonts/Helvetica.ttc']:
        if pathlib.Path(p).exists():
            try:
                return ImageFont.truetype(p, sz * S)
            except Exception:
                pass
    return ImageFont.load_default()

def new_layer(w=W, h=H):
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def sc(box):
    return [v * S for v in box]

def rrect(d, box, r, fill, outline=None, w=3):
    d.rounded_rectangle(sc(box), radius=r * S, fill=fill, outline=outline,
                        width=w * S if outline else 0)

def ell(d, cx, cy, rx, ry, fill, outline=None, w=3):
    d.ellipse(sc([cx - rx, cy - ry, cx + rx, cy + ry]), fill=fill,
              outline=outline, width=w * S if outline else 0)

def limb(d, pts, w, color):
    d.line([(x * S, y * S) for x, y in pts], fill=color, width=w * S, joint='curve')
    for x, y in (pts[0], pts[-1]):
        ell(d, x, y, w / 2, w / 2, color)

def arc_motion(d, cx, cy, r, a0, a1, color, w=4, n=3, gap=13):
    for i in range(n):
        rr = (r + i * gap) * S
        d.arc([cx * S - rr, cy * S - rr, cx * S + rr, cy * S + rr],
              a0, a1, fill=color, width=w * S)

def arrow(d, x0, y0, x1, y1, color, w=7, head=17):
    d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=color, width=w * S)
    ang = math.atan2(y1 - y0, x1 - x0)
    p = [(x1, y1),
         (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45)),
         (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))]
    d.polygon([(x * S, y * S) for x, y in p], fill=color)

def badge(d, cx, cy, text, fill=ACCENT, r=26, fs=24):
    ell(d, cx, cy, r, r, fill)
    f = font(fs)
    d.text((cx * S, cy * S), text, font=f, fill=(255, 255, 255), anchor='mm')

def label(d, cx, cy, text, color=ACCENT, fs=25):
    f = font(fs)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 11 * S
    d.rounded_rectangle([cx * S - tw / 2 - pad, cy * S - th / 2 - pad * .8,
                         cx * S + tw / 2 + pad, cy * S + th / 2 + pad * .9],
                        radius=999, fill=(255, 255, 255), outline=color, width=3 * S)
    d.text((cx * S, cy * S), text, font=f, fill=color, anchor='mm')

def ground(d, y=390, x0=40, x1=600):
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=GROUND, width=8 * S)

# ---------------------------------------------------------------- thân trẻ
def child_group(supine=False, w=420, h=230):
    """Trẻ nhỏ nằm ngang, đầu ở bên phải. Trả về layer trong suốt."""
    im, d = new_layer(w, h)
    # cẳng tay người lớn đỡ dưới
    limb(d, [(16, 152), (326, 138)], 44, ADULT)
    ell(d, 350, 116, 30, 28, ADULT, ADULT_L, 3)      # bàn tay đỡ hàm
    # thân trẻ
    rrect(d, [70, 58, 275, 128], 34, CHILD, CHILD_L, 4)
    ell(d, 312, 88, 44, 42, CHILD, CHILD_L, 4)       # đầu
    if supine:                                       # nằm ngửa — tay chân hướng lên
        limb(d, [(268, 84), (302, 62)], 13, CHILD_L)
        limb(d, [(88, 66), (52, 32)], 15, CHILD_L)
        limb(d, [(112, 62), (86, 24)], 15, CHILD_L)
    else:                                            # nằm sấp — tay chân hướng xuống
        limb(d, [(268, 100), (300, 118)], 13, CHILD_L)
        limb(d, [(88, 120), (52, 150)], 15, CHILD_L)
        limb(d, [(112, 124), (84, 158)], 15, CHILD_L)
    return im

def paste_rot(base, layer, angle, x, y):
    r = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (x * S, y * S))

# ---------------------------------------------------------------- các hình
def fig1():
    """Dưới 1 tuổi — úp sấp, 5 lần vỗ lưng."""
    im, d = new_layer()
    ground(d)
    paste_rot(im, child_group(), -14, 105, 95)
    d2 = ImageDraw.Draw(im)
    ell(d2, 268, 150, 40, 27, ADULT, ADULT_L, 3)                 # bàn tay vỗ
    arrow(d2, 268, 182, 268, 222, ACCENT)
    arc_motion(d2, 268, 150, 52, 200, 340, ACCENT, 4, 2, 15)
    label(d2, 430, 120, '5 x')
    badge(d2, 56, 56, '1')
    return im

def fig2():
    """Dưới 1 tuổi — lật ngửa, 5 lần ấn ngực bằng hai ngón."""
    im, d = new_layer()
    ground(d)
    paste_rot(im, child_group(supine=True), -14, 105, 95)
    d2 = ImageDraw.Draw(im)
    limb(d2, [(296, 112), (296, 166)], 13, ADULT_L)              # hai ngón tay
    limb(d2, [(326, 106), (326, 160)], 13, ADULT_L)
    arrow(d2, 311, 174, 311, 210, ACCENT)                        # ấn xuống giữa ngực
    label(d2, 440, 118, '5 x')
    badge(d2, 56, 56, '2')
    return im

# ---- trẻ lớn: người lớn quỳ sau lưng ----
def big_pair(d, fist=False):
    ground(d)
    # người lớn
    ell(d, 148, 128, 40, 42, ADULT, ADULT_L, 4)
    rrect(d, [108, 176, 190, 330], 34, ADULT, ADULT_L, 4)
    limb(d, [(148, 330), (128, 388)], 22, ADULT)
    limb(d, [(172, 330), (196, 388)], 22, ADULT)
    # trẻ cúi người về trước
    rrect(d, [236, 196, 388, 268], 34, CHILD, CHILD_L, 4)
    ell(d, 428, 246, 38, 37, CHILD, CHILD_L, 4)
    limb(d, [(300, 266), (292, 340)], 17, CHILD_L)
    limb(d, [(336, 266), (348, 340)], 17, CHILD_L)
    limb(d, [(380, 258), (404, 300)], 15, CHILD_L)
    # tay người lớn đỡ trước ngực trẻ
    limb(d, [(186, 220), (300, 252)], 20, ADULT)
    if fist:
        ell(d, 318, 244, 24, 22, ADULT, ADULT_L, 3)

def fig3():
    """Trên 1 tuổi — 5 lần vỗ lưng giữa hai xương bả vai."""
    im, d = new_layer()
    big_pair(d)
    ell(d, 286, 158, 38, 26, ADULT, ADULT_L, 3)
    arrow(d, 286, 188, 286, 216, ACCENT)
    arc_motion(d, 286, 158, 48, 200, 340, ACCENT, 4, 2, 15)
    label(d, 470, 130, '5 x')
    badge(d, 56, 56, '3')
    return im

def fig4():
    """Trên 1 tuổi — 5 lần ấn bụng, trên rốn dưới mũi ức."""
    im, d = new_layer()
    big_pair(d, fist=True)
    arrow(d, 360, 292, 326, 252, ACCENT)          # vào trong và lên trên
    ell(d, 318, 244, 9, 9, ACCENT)
    label(d, 470, 130, '5 x')
    badge(d, 56, 56, '4')
    return im

def fig5():
    """Con lả đi — đặt nằm ngửa mặt phẳng cứng, gọi 115."""
    im, d = new_layer()
    ground(d, 330, 60, 580)
    rrect(d, [150, 246, 380, 322], 36, CHILD, CHILD_L, 4)
    ell(d, 424, 284, 42, 41, CHILD, CHILD_L, 4)
    limb(d, [(200, 246), (176, 208)], 16, CHILD_L)
    limb(d, [(250, 246), (234, 204)], 16, CHILD_L)
    # điện thoại
    rrect(d, [452, 96, 528, 210], 16, (255, 255, 255), ACCENT, 5)
    d.text((490 * S, 156 * S), '115', font=font(30), fill=ACCENT, anchor='mm')
    arc_motion(d, 548, 130, 22, 300, 60, ACCENT, 5, 3, 14)
    badge(d, 56, 56, '5')
    return im

def fig6():
    """Con lả đi — ép tim, làm theo hướng dẫn tổng đài."""
    im, d = new_layer()
    ground(d, 330, 60, 580)
    rrect(d, [150, 246, 380, 322], 36, CHILD, CHILD_L, 4)
    ell(d, 424, 284, 42, 41, CHILD, CHILD_L, 4)
    # hai bàn tay chồng lên nhau giữa ngực
    ell(d, 300, 214, 44, 30, ADULT, ADULT_L, 4)
    ell(d, 300, 176, 44, 30, ADULT, ADULT_L, 4)
    limb(d, [(300, 150), (300, 92)], 20, ADULT)
    arrow(d, 300, 246, 300, 282, ACCENT)
    badge(d, 56, 56, '6')
    return im

FIGS = [('nghen-1', fig1), ('nghen-2', fig2), ('nghen-3', fig3),
        ('nghen-4', fig4), ('nghen-5', fig5), ('nghen-6', fig6)]

def main():
    for name, fn in FIGS:
        layer = fn()
        base = Image.new('RGBA', (W * S, H * S), BG + (255,))
        base.alpha_composite(layer)
        out = base.convert('RGB').resize((W, H), Image.LANCZOS)
        # hình phẳng ít màu — dồn về bảng 48 màu, nhẹ đi khoảng ba phần tư
        # mà mắt không thấy khác
        out = out.quantize(colors=48, method=Image.MEDIANCUT, dither=Image.NONE)
        out.save(OUT / (name + '.png'), optimize=True)
        print(name + '.png', (OUT / (name + '.png')).stat().st_size // 1024, 'KB')

if __name__ == '__main__':
    main()
