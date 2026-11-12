import math

import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import houses as Hh
import paint as P


def f3(c):
    c = Hh.rgb(c)
    return np.array(c, np.float32) / 255.0

W, H = 1600, 1000
VY = 0.2917 * H
K = 1.0 * H
YC = 0.7083
BACK = 0.52


def sc(z):
    return 1 - (1 - BACK) * z


def pr(x, y, z):
    s = sc(z)
    return (W / 2 + x * (W / 2) * s, VY + (YC - y) * K * s)


def quad(c, pts3, col):
    c.poly([pr(*p) for p in pts3], col)


def tquad(c, pts3, arr):
    c.paste_tex(arr, [pr(*p) for p in pts3])


def box(c, xa, xb, ya, yb, za, zb, col, top=None, side=None):
    top = top or Hh.shade(col, 0.12)
    side = side or Hh.shade(col, -0.18)
    if yb < YC:
        quad(c, [(xa, yb, za), (xb, yb, za), (xb, yb, zb), (xa, yb, zb)], top)
    elif ya > YC:
        quad(c, [(xa, ya, za), (xb, ya, za), (xb, ya, zb), (xa, ya, zb)], Hh.shade(col, -0.25))
    if xa > 0:
        quad(c, [(xa, ya, za), (xa, yb, za), (xa, yb, zb), (xa, ya, zb)], side)
    if xb < 0:
        quad(c, [(xb, ya, za), (xb, yb, za), (xb, yb, zb), (xb, ya, zb)], side)
    quad(c, [(xa, ya, za), (xb, ya, za), (xb, yb, za), (xa, yb, za)], col)


def shadow(c, xa, xb, za, zb, amt=0.35):
    pts = [pr(xa - 0.03, 0, za - 0.02), pr(xb + 0.03, 0, za - 0.02), pr(xb + 0.03, 0, zb + 0.02), pr(xa - 0.03, 0, zb + 0.02)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    c.glow((x0 + x1) / 2, (y0 + y1) / 2 + 4, (x1 - x0) / 2, "#2A2622", amt)


def view(seed, P_):
    im = P.paint(dict(style="landscape", seed=seed, size="60 × 100 cm"), P_)
    return P.from_img(im)


VIEWS = {
    "valley": dict(sky0="#9DB8CF", sky1="#EDE7DA", layers=["#A9B7BF", "#8DA49B", "#6F8A72", "#55704F"], horizon=0.72, top=0.38, haze="#E5E4DC", sun=(0.75, 0.25, 0.03, "#FFF6DD")),
    "coast": dict(sky0="#A8C2D4", sky1="#EEF0EA", layers=["#B7C4CA", "#93A7AA"], horizon=0.55, top=0.42, water=0.6, watercol="#7FA0B0", haze="#E8ECEA"),
    "dusk": dict(sky0="#3E4A6C", sky1="#F0B58C", layers=["#7A7F96", "#5E6680", "#434B60"], horizon=0.7, top=0.42, haze="#C9A6A0", sun=(0.3, 0.6, 0.03, "#FFD7A6")),
    "forest": dict(sky0="#B5C8D6", sky1="#F0EDE4", layers=["#8FA39B", "#6E8873", "#4D6A4E", "#3B5640"], horizon=0.8, top=0.45, haze="#DDE2DA"),
}


def shell(c, p):
    wall = p["wall"]
    bx0, bx1 = pr(-1, 1, 1)[0], pr(1, 1, 1)[0]
    ty, fy = pr(0, 1, 1)[1], pr(0, 0, 1)[1]
    walltex = Hh.texture(c.r, 400, 260, "stucco", wall, 0.0, 1)
    c.paste_tex(walltex, [(bx0, ty), (bx1, ty), (bx1, fy), (bx0, fy)])
    lw = Hh.texture(c.r, 300, 300, "stucco", Hh.shade(wall, -0.07), 0.12, 1)
    tquad(c, [(-1, 0, 0), (-1, 0, 1), (-1, 1, 1), (-1, 1, 0)], lw)
    rw = Hh.texture(c.r, 300, 300, "stucco", Hh.shade(wall, -0.12), -0.12, 1)
    tquad(c, [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)], rw)
    ceil = P.vgrad(200, 200, f3(Hh.shade(p.get("ceil", "#F4F1EA"), -0.06)), f3(p.get("ceil", "#F4F1EA")), 1)
    tquad(c, [(-1, 1, 0), (1, 1, 0), (1, 1, 1), (-1, 1, 1)], ceil)
    fl = p.get("floor", "#B48A62")
    ftex = P.vgrad(300, 300, f3(Hh.shade(fl, -0.12)), f3(fl), 1)
    ftex *= (1 + (P.vnoise(300, 300, 30, c.r, 3) - 0.5) * 0.12)[..., None]
    tquad(c, [(-1, 0, 0), (1, 0, 0), (1, 0, 1), (-1, 0, 1)], ftex)
    if p.get("planks", True):
        n = 22
        for k in range(n + 1):
            x = -1 + 2 * k / n
            c.line([pr(x, 0, 0), pr(x, 0, 1)], Hh.shade(fl, -0.22), 1.2)
    else:
        for k in range(9):
            x = -1 + 2 * k / 8
            c.line([pr(x, 0, 0), pr(x, 0, 1)], Hh.shade(fl, -0.12), 1.0)
        for z in [0.15, 0.32, 0.5, 0.68, 0.85]:
            c.line([pr(-1, 0, z), pr(1, 0, z)], Hh.shade(fl, -0.12), 1.0)
    if p.get("beams"):
        for z in [0.12, 0.34, 0.56, 0.78]:
            box(c, -1, 1, 0.97, 1.0, z, z + 0.05, p["beams"] if isinstance(p["beams"], str) else "#8A6A4C")
    c.line([pr(-1, 0, 1), pr(1, 0, 1)], Hh.shade(wall, -0.3), 2)
    c.line([pr(-1, 1, 1), pr(1, 1, 1)], Hh.shade(wall, -0.15), 1.5)
    c.line([pr(-1, 0, 1), pr(-1, 0, 0)], Hh.shade(wall, -0.3), 2)
    c.line([pr(1, 0, 1), pr(1, 0, 0)], Hh.shade(wall, -0.3), 2)


def glazing(c, x0, x1, y0, y1, vw, frame="#26292C", cols=4):
    a, b = pr(x0, y1, 1), pr(x1, y0, 1)
    w, h = int(b[0] - a[0]), int(b[1] - a[1])
    v = np.asarray(Image.fromarray((np.clip(vw, 0, 1) * 255).astype(np.uint8)).resize((w * 2, h * 2)), np.float32) / 255
    fr = 5
    c.rect(a[0] - fr, a[1] - fr, b[0] + fr, b[1] + fr, frame)
    c.paste_tex(v, [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])])
    for k in range(1, cols):
        x = a[0] + (b[0] - a[0]) * k / cols
        c.line([(x, a[1]), (x, b[1])], frame, 4)


def side_window(c, side, za, zb, ya, yb, vw):
    x = -1 if side < 0 else 1
    pts = [pr(x, ya, za), pr(x, ya, zb), pr(x, yb, zb), pr(x, yb, za)]
    c.paste_tex(np.clip(vw[::2, ::2] * 1.05, 0, 1), pts)
    c.line(pts + [pts[0]], "#2A2C2E", 3)
    zm = (za + zb) / 2
    c.line([pr(x, ya, zm), pr(x, yb, zm)], "#2A2C2E", 3)


def pendant(c, x, z, col, glow=True):
    top = pr(x, 1, z)
    bot = pr(x, 0.78, z)
    c.line([top, bot], "#2A2A2A", 1.5)
    s = sc(z) * 34
    c.poly([(bot[0] - s, bot[1] + s * 0.6), (bot[0] + s, bot[1] + s * 0.6), (bot[0] + s * 0.45, bot[1]), (bot[0] - s * 0.45, bot[1])], col)
    if glow:
        c.glow(bot[0], bot[1] + s * 0.8, s * 2.2, "#FFE7BC", 0.45)


def art(c, x0, x1, y0, y1, cols):
    a, b = pr(x0, y1, 1), pr(x1, y0, 1)
    c.rect(a[0] - 6, a[1] - 6, b[0] + 6, b[1] + 6, "#2E2B28")
    c.rect(a[0], a[1], b[0], b[1], cols[0])
    w = b[0] - a[0]
    c.rect(a[0] + w * 0.1, a[1] + (b[1] - a[1]) * 0.15, a[0] + w * 0.55, b[1] - (b[1] - a[1]) * 0.2, cols[1])
    c.ell(a[0] + w * 0.5, a[1] + (b[1] - a[1]) * 0.25, a[0] + w * 0.85, a[1] + (b[1] - a[1]) * 0.6, cols[2])


def plant(c, x, z, h=0.35):
    base = pr(x, 0, z)
    s = sc(z)
    box(c, x - 0.04, x + 0.04, 0, 0.08, z, z + 0.04, "#C9BBA6")
    for k in range(9):
        a = -math.pi / 2 + (c.r.random() - 0.5) * 1.6
        L = h * K * s * (0.6 + 0.4 * c.r.random()) * 0.6
        tip = (base[0] + math.cos(a) * L * 0.6, base[1] - 0.08 * K * s + math.sin(a) * L)
        c.line([(base[0], base[1] - 0.08 * K * s), tip], "#4F6E45", 3 * s)
        c.ell(tip[0] - 14 * s, tip[1] - 8 * s, tip[0] + 14 * s, tip[1] + 8 * s, Hh.mixc("#4F6E45", "#7E9C66", c.r.random()))


def living(c, p):
    vw = view(p["seed"], VIEWS[p.get("view", "valley")])
    glazing(c, -0.82, 0.82, 0.08, 0.92, vw, p.get("frame", "#26292C"), 5)
    if p.get("fire", True):
        box(c, -1.0, -0.96, 0, 0.62, 0.42, 0.7, p.get("stone", "#A79C8E"))
        a = pr(-0.96, 0.08, 0.5)
        b = pr(-0.96, 0.24, 0.62)
        c.poly([pr(-0.96, 0.06, 0.48), pr(-0.96, 0.06, 0.64), pr(-0.96, 0.24, 0.64), pr(-0.96, 0.24, 0.48)], "#1E1B19")
        c.glow((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2, 40, "#FFB565", 0.7)
    rug = p.get("rug", "#D8CFC0")
    quad(c, [(-0.6, 0.002, 0.2), (0.6, 0.002, 0.2), (0.6, 0.002, 0.72), (-0.6, 0.002, 0.72)], rug)
    shadow(c, -0.55, 0.55, 0.52, 0.66, 0.3)
    sofa = p.get("sofa", "#E7E1D6")
    box(c, -0.55, 0.55, 0.0, 0.17, 0.52, 0.66, sofa)
    box(c, -0.55, 0.55, 0.17, 0.33, 0.62, 0.68, Hh.shade(sofa, -0.05))
    box(c, -0.6, -0.5, 0.0, 0.24, 0.5, 0.68, Hh.shade(sofa, -0.08))
    box(c, 0.5, 0.6, 0.0, 0.24, 0.5, 0.68, Hh.shade(sofa, -0.08))
    for k, x in enumerate([-0.35, 0.1]):
        box(c, x, x + 0.18, 0.17, 0.3, 0.58, 0.6, p.get("accent", "#8C6B4F"))
    shadow(c, -0.25, 0.25, 0.32, 0.44, 0.35)
    box(c, -0.25, 0.25, 0.0, 0.11, 0.32, 0.44, p.get("table", "#5B4636"))
    box(c, 0.62, 0.86, 0.0, 0.2, 0.18, 0.36, p.get("chair", "#B79572"))
    box(c, 0.62, 0.86, 0.2, 0.36, 0.33, 0.37, Hh.shade(p.get("chair", "#B79572"), -0.1))
    plant(c, 0.86, 0.82)
    pendant(c, 0.0, 0.42, p.get("lamp", "#C7A15E"))


def kitchen(c, p):
    vw = view(p["seed"], VIEWS[p.get("view", "valley")])
    cab = p.get("cab", "#E6E0D5")
    top = p.get("top", "#F1EEE8")
    box(c, -1.0, -0.3, 0, 0.36, 0.86, 1.0, cab, top)
    box(c, 0.3, 1.0, 0, 0.36, 0.86, 1.0, cab, top)
    glazing(c, -0.28, 0.28, 0.42, 0.9, vw, p.get("frame", "#26292C"), 2)
    box(c, -1.0, -0.36, 0.56, 0.94, 0.9, 1.0, Hh.shade(cab, -0.04))
    box(c, 0.36, 1.0, 0.56, 0.94, 0.9, 1.0, Hh.shade(cab, -0.04))
    box(c, -0.96, -0.94, 0.0, 0.36, 0.2, 0.86, cab, top)
    box(c, -1.0, -0.96, 0.0, 0.36, 0.2, 0.86, Hh.shade(cab, -0.08), top)
    shadow(c, -0.48, 0.48, 0.42, 0.62, 0.35)
    isl = p.get("island", "#3E4A52")
    box(c, -0.48, 0.48, 0.0, 0.34, 0.44, 0.62, isl, p.get("isltop", "#EEEBE4"))
    box(c, -0.5, 0.5, 0.34, 0.37, 0.43, 0.63, p.get("isltop", "#EEEBE4"))
    for x in [-0.36, -0.06, 0.24]:
        box(c, x, x + 0.1, 0.0, 0.24, 0.3, 0.38, p.get("stool", "#7D5B3E"))
        box(c, x - 0.01, x + 0.11, 0.24, 0.27, 0.29, 0.39, Hh.shade(p.get("stool", "#7D5B3E"), 0.1))
    for x in [-0.3, 0.0, 0.3]:
        pendant(c, x, 0.52, p.get("lamp", "#C7A15E"))
    plant(c, 0.9, 0.7, 0.3)


def suite(c, p):
    vw = view(p["seed"], VIEWS[p.get("view", "valley")])
    side_window(c, -1, 0.3, 0.8, 0.12, 0.9, vw)
    head = p.get("head", "#9C7B5E")
    box(c, -0.42, 0.42, 0.0, 0.62, 0.95, 1.0, head)
    shadow(c, -0.4, 0.4, 0.5, 0.96, 0.3)
    bed = p.get("bed", "#F2EEE7")
    box(c, -0.4, 0.4, 0.0, 0.2, 0.52, 0.95, bed)
    box(c, -0.4, 0.4, 0.2, 0.22, 0.52, 0.95, Hh.shade(bed, 0.05))
    box(c, -0.41, 0.41, 0.1, 0.23, 0.5, 0.68, p.get("throw", "#7E8F86"))
    box(c, -0.32, -0.04, 0.22, 0.33, 0.86, 0.94, "#FBF9F5")
    box(c, 0.04, 0.32, 0.22, 0.33, 0.86, 0.94, "#FBF9F5")
    for x in [-0.66, 0.46]:
        box(c, x, x + 0.2, 0.0, 0.2, 0.84, 0.98, p.get("night", "#6F5440"))
        bt = pr(x + 0.1, 0.2, 0.9)
        c.ell(bt[0] - 18, bt[1] - 60, bt[0] + 18, bt[1] - 22, "#F4E2C2")
        c.glow(bt[0], bt[1] - 40, 46, "#FFE3B4", 0.55)
    box(c, -0.36, 0.36, 0.0, 0.14, 0.32, 0.42, p.get("bench", "#B9A07F"))
    art(c, -0.3, 0.3, 0.68, 0.9, [p.get("art0", "#E8DCCB"), p.get("art1", "#8E9F96"), p.get("art2", "#C98E62")])
    plant(c, 0.85, 0.55)


def bath(c, p):
    vw = view(p["seed"], VIEWS[p.get("view", "valley")])
    glazing(c, -0.6, 0.6, 0.18, 0.92, vw, p.get("frame", "#26292C"), 3)
    shadow(c, -0.4, 0.4, 0.62, 0.86, 0.3)
    tub = p.get("tub", "#FAF8F4")
    a, b = pr(-0.42, 0.24, 0.62), pr(0.42, 0.0, 0.62)
    a2 = pr(-0.36, 0.24, 0.86)
    c.ell(a[0], a2[1] - 30, b[0], a[1] + 40, Hh.shade(tub, -0.06))
    c.rect(a[0] + 10, a[1] + 10, b[0] - 10, b[1] - 20, tub)
    c.ell(a[0] + 10, b[1] - 50, b[0] - 10, b[1] + 6, tub)
    c.ell(a[0] + 30, a2[1] - 14, b[0] - 30, a[1] + 22, "#CFE3EA")
    box(c, 0.96, 1.0, 0.0, 0.34, 0.12, 0.62, p.get("vanity", "#7A5A40"))
    box(c, 0.82, 0.96, 0.0, 0.34, 0.12, 0.62, p.get("vanity", "#7A5A40"), p.get("top", "#EDEAE4"))
    mp = [pr(0.99, 0.48, 0.18), pr(0.99, 0.48, 0.56), pr(0.99, 0.86, 0.56), pr(0.99, 0.86, 0.18)]
    c.poly(mp, "#C9D4D8")
    c.line(mp + [mp[0]], "#8D7A62", 4)
    plant(c, -0.85, 0.75, 0.4)
    pendant(c, -0.6, 0.5, p.get("lamp", "#C7A15E"))


def dining(c, p):
    vw = view(p["seed"], VIEWS[p.get("view", "valley")])
    glazing(c, -0.7, 0.7, 0.08, 0.92, vw, p.get("frame", "#26292C"), 4)
    shadow(c, -0.5, 0.5, 0.4, 0.72, 0.35)
    tb = p.get("table", "#6B4D36")
    ch = p.get("chair", "#D8CDBB")
    for x in [-0.4, -0.12, 0.16]:
        box(c, x, x + 0.16, 0, 0.36, 0.76, 0.8, ch)
    box(c, -0.5, 0.5, 0.25, 0.28, 0.42, 0.74, tb)
    box(c, -0.46, -0.42, 0.0, 0.25, 0.44, 0.48, Hh.shade(tb, -0.2))
    box(c, 0.42, 0.46, 0.0, 0.25, 0.44, 0.48, Hh.shade(tb, -0.2))
    for x in [-0.44, 0.28]:
        box(c, x, x + 0.16, 0, 0.15, 0.3, 0.38, ch)
        box(c, x, x + 0.16, 0.15, 0.4, 0.3, 0.32, Hh.shade(ch, -0.05))
    a = pr(-0.3, 0.8, 0.58)
    b = pr(0.3, 0.74, 0.58)
    c.line([pr(0, 1, 0.58), pr(0, 0.8, 0.58)], "#2A2A2A", 1.5)
    c.rect(a[0], a[1], b[0], b[1], p.get("lamp", "#C7A15E"))
    c.glow((a[0] + b[0]) / 2, b[1] + 20, 120, "#FFE6B8", 0.4)
    plant(c, -0.86, 0.8, 0.45)


ROOMS = {"living": living, "kitchen": kitchen, "suite": suite, "bath": bath, "dining": dining}


def room(kind, p):
    c = Hh.Canvas(W, H, p["seed"])
    shell(c, p)
    ROOMS[kind](c, p)
    return c.finish(0.05, 0.22)
