import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import paint as P

SS = 2


def rgb(h):
    if not isinstance(h, str):
        return tuple(h)
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    c = rgb(c) if isinstance(c, str) else c
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c)
    return tuple(int(v * (1 + k)) for v in c)


def mixc(a, b, t):
    a = rgb(a) if isinstance(a, str) else a
    b = rgb(b) if isinstance(b, str) else b
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


class Canvas:
    def __init__(self, W, H, seed):
        self.W, self.H = W, H
        self.r = np.random.default_rng(seed)
        self.im = Image.new("RGB", (W * SS, H * SS), (200, 200, 200))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, col):
        self.d.polygon(self.P(pts), fill=rgb(col) if isinstance(col, str) else col)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], fill=rgb(col) if isinstance(col, str) else col)

    def line(self, pts, col, w):
        self.d.line(self.P(pts), fill=rgb(col) if isinstance(col, str) else col, width=max(1, int(w * SS)))

    def ell(self, x0, y0, x1, y1, col):
        self.d.ellipse([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=rgb(col) if isinstance(col, str) else col)

    def paste_tex(self, arr, pts):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = int(math.floor(min(xs) * SS)), int(math.floor(min(ys) * SS))
        x1, y1 = int(math.ceil(max(xs) * SS)), int(math.ceil(max(ys) * SS))
        w, h = max(1, x1 - x0), max(1, y1 - y0)
        tex = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB").resize((w, h), Image.BILINEAR)
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon([(x * SS - x0, y * SS - y0) for x, y in pts], fill=255)
        self.im.paste(tex, (x0, y0), m)

    def glow(self, cx, cy, rad, col, amt):
        W, H = self.im.size
        lay = Image.new("L", (W, H), 0)
        ImageDraw.Draw(lay).ellipse([(cx - rad) * SS, (cy - rad * 0.55) * SS, (cx + rad) * SS, (cy + rad * 0.55) * SS], fill=int(255 * amt))
        lay = lay.filter(ImageFilter.GaussianBlur(rad * SS * 0.35))
        self.im = Image.composite(Image.new("RGB", (W, H), rgb(col) if isinstance(col, str) else col), self.im, lay)
        self.d = ImageDraw.Draw(self.im)

    def finish(self, strength=0.06, vign=0.18):
        im = self.im.resize((self.W, self.H), Image.LANCZOS)
        a = P.from_img(im)
        a = P.brushify(a, self.r, amp=1.4, cell=40, length=19, axis=1, strength=strength)
        a = a * P.paper_tex(self.H, self.W, self.r, 0.035)
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        d = np.sqrt(((xx / self.W) - 0.5) ** 2 * 1.4 + ((yy / self.H) - 0.5) ** 2)
        a = a * (1 - vign * np.clip(d - 0.3, 0, 1)[..., None] * 1.6)
        return P.to_img(a)


def texture(r, w, h, kind, col, light=0.0, scale=1.0):
    w, h = max(4, int(w)), max(4, int(h))
    base = np.ones((h, w, 3), np.float32) * (np.array(rgb(col), np.float32) / 255.0)
    n = P.vnoise(h, w, 40, r, 3) - 0.5
    base *= (1 + n * 0.10)[..., None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    yy = np.arange(h, dtype=np.float32)[:, None]
    if kind == "board":
        step = 13 * scale
        ln = (np.mod(xx, step) < 1.6).astype(np.float32)
        base *= (1 - 0.22 * ln)[..., None]
    elif kind == "siding":
        step = 8 * scale
        ln = (np.mod(yy, step) < 1.3).astype(np.float32)
        base *= (1 - 0.18 * ln)[..., None] * np.ones((1, w, 1))
    elif kind == "cedar":
        step = 6 * scale
        ln = (np.mod(yy, step) < 1.0).astype(np.float32)
        band = P.vnoise(h, w, 10, r, 2)
        base *= (1 - 0.2 * ln)[..., None] * (0.92 + 0.16 * band)[..., None]
    elif kind == "shingle":
        step = 9 * scale
        row = np.floor(yy / step)
        off = np.mod(row * 7.3, 11)
        ln = ((np.mod(yy, step) < 1.4) | (np.mod(xx + off * 1.0, 11 * scale) < 1.2)).astype(np.float32)
        tone = P.vnoise(h, w, 8, r, 2)
        base *= (1 - 0.25 * ln)[..., None] * (0.9 + 0.2 * tone)[..., None]
    elif kind in ("stone", "brick"):
        bh = (11 if kind == "stone" else 5.5) * scale
        out = np.zeros((h, w), np.float32)
        tone = np.zeros((h, w), np.float32)
        y = 0.0
        while y < h:
            hh = bh * (0.8 + 0.5 * r.random()) if kind == "stone" else bh
            x = -r.random() * 20
            while x < w:
                ww = (bh * (1.6 + 2.2 * r.random())) if kind == "stone" else bh * 2.1
                y0, y1, x0, x1 = int(y), int(min(h, y + hh)), int(max(0, x)), int(min(w, x + ww))
                if x1 > x0 and y1 > y0:
                    tone[y0:y1, x0:x1] = r.random()
                    out[y0:y1, x0:x1] = 1
                    out[y0:min(h, y0 + 1), x0:x1] = 0
                    out[y0:y1, x0:min(w, x0 + 1)] = 0
                x += ww
            y += hh
        base *= (0.86 + 0.24 * tone)[..., None]
        base = base * out[..., None] + (1 - out[..., None]) * (base * 0.78 + 0.12)
    elif kind == "metal":
        step = 10 * scale
        ln = (np.mod(xx, step) < 1.4).astype(np.float32)
        base *= (1 + 0.12 * ln)[..., None]
    elif kind == "slate":
        step = 7 * scale
        row = np.floor(yy / step)
        ln = ((np.mod(yy, step) < 1.2) | (np.mod(xx + np.mod(row, 2) * 6 * scale, 12 * scale) < 1.0)).astype(np.float32)
        tone = P.vnoise(h, w, 6, r, 2)
        base *= (1 - 0.22 * ln)[..., None] * (0.9 + 0.18 * tone)[..., None]
    elif kind == "stucco":
        base *= (1 + (P.vnoise(h, w, 6, r, 2) - 0.5) * 0.06)[..., None]
    g = np.linspace(1 + light, 1 - light, w, dtype=np.float32)[None, :, None]
    return np.clip(base * g, 0, 1)


def sky(c, top, bot, sun=None, clouds=0.35, cloudcol="#FFFFFF"):
    W, H = c.W, c.H
    a = P.vgrad(H * SS // 2, W * SS // 2, top, bot, 1.1)
    hh, ww = a.shape[:2]
    if sun:
        sx, sy, sr, sc = sun
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        d = np.sqrt((xx - sx * ww) ** 2 + (yy - sy * hh) ** 2)
        a = P.over(a, sc, np.exp(-(d / (sr * ww * 6)) ** 2) * 0.55)
    cl = P.aniso(hh, ww, 160, c.r, 4, 5)
    yy = np.linspace(0, 1, hh)[:, None]
    m = P.smooth(0.52, 0.8, cl) * (1 - P.smooth(0.25, 0.7, yy))
    a = P.over(a, cloudcol, m * clouds)
    c.im = P.to_img(a).resize((W * SS, H * SS), Image.BICUBIC)
    c.d = ImageDraw.Draw(c.im)


def hills(c, base, amp, cols, seed_shift=0):
    W = c.W
    for i, col in enumerate(cols):
        t = i / max(1, len(cols) - 1)
        rid = P.ridge(W, base + t * amp * 0.9, amp * (1.1 - 0.5 * t), W * (0.5 - 0.2 * t), c.r, 0.4)
        pts = [(x, float(rid[min(W - 1, x)])) for x in range(0, W + 1, 4)] + [(W, c.H), (0, c.H)]
        c.poly(pts, col)


def tree(c, x, y, h, col, kind="round", dark=None):
    r = c.r
    dark = dark or shade(col, -0.3)
    if kind == "pine":
        w = h * 0.36
        for k in range(5):
            t = k / 5
            yy = y - h * (0.18 + t * 0.78)
            ww = w * (1 - t * 0.8)
            c.poly([(x - ww, yy + h * 0.22), (x, yy - h * 0.12), (x + ww, yy + h * 0.22)], mixc(dark, col, 0.3 + 0.5 * t))
        return
    if kind == "cypress":
        c.ell(x - h * 0.12, y - h, x + h * 0.12, y, dark)
        c.ell(x - h * 0.09, y - h * 0.97, x + h * 0.08, y - h * 0.1, col)
        return
    c.rect(x - h * 0.03, y - h * 0.4, x + h * 0.03, y, shade(dark, -0.2))
    for k in range(14):
        a = r.random() * math.pi * 2
        rr = h * 0.22 * math.sqrt(r.random())
        cx, cy = x + math.cos(a) * rr * 1.2, y - h * 0.62 + math.sin(a) * rr
        s = h * (0.16 + 0.12 * r.random())
        c.ell(cx - s, cy - s * 0.9, cx + s, cy + s * 0.9, mixc(dark, col, 0.2 + 0.7 * (1 - (cy - (y - h)) / h) * r.random()))


def shrub(c, x, y, w, h, col, flowers=None):
    r = c.r
    for k in range(int(6 + w / 12)):
        cx = x + (r.random() - 0.5) * w
        s = h * (0.35 + 0.35 * r.random())
        c.ell(cx - s, y - s * 1.6, cx + s, y, mixc(shade(col, -0.35), col, r.random()))
    if flowers:
        for k in range(int(w / 6)):
            cx = x + (r.random() - 0.5) * w * 0.9
            cy = y - h * (0.3 + 0.6 * r.random())
            c.ell(cx - 2, cy - 2, cx + 2, cy + 2, flowers)


def window(c, x0, y0, x1, y1, mode, frame="#2B2B2B", cols=2, rows=1, fw=3.0, tall=False):
    c.rect(x0 - fw, y0 - fw, x1 + fw, y1 + fw, frame)
    w, h = x1 - x0, y1 - y0
    if mode == "dusk":
        g = P.vgrad(max(4, int(h)), max(4, int(w)), "#FFE3B0", "#E9964F", 0.8)
        n = P.vnoise(g.shape[0], g.shape[1], 30, c.r, 2)
        g *= (0.85 + 0.25 * n)[..., None]
        inner = np.ones_like(g[..., :1])
        g = g * inner
    else:
        g = P.vgrad(max(4, int(h)), max(4, int(w)), "#9FB4C4", "#3E4C57", 0.9)
        xx = np.linspace(0, 1, g.shape[1])[None, :]
        yy = np.linspace(0, 1, g.shape[0])[:, None]
        hl = np.clip(1 - np.abs((xx * 0.7 + yy) - 0.55) * 5, 0, 1) * 0.35
        g = g + hl[..., None]
    c.paste_tex(g, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    for k in range(1, cols):
        xx = x0 + w * k / cols
        c.line([(xx, y0), (xx, y1)], frame, fw * 0.6)
    for k in range(1, rows):
        yy = y0 + h * k / rows
        c.line([(x0, yy), (x1, yy)], frame, fw * 0.6)


def mass(c, m, ground, mode, sunk=0.0):
    x0, x1 = m["x0"], m["x1"]
    top = ground - m["h"]
    mat, col = m.get("mat", "stucco"), m.get("col", "#E9E4DA")
    if m.get("back"):
        col = shade(col, -0.12)
    tex = texture(c.r, (x1 - x0) * SS, m["h"] * SS, mat, col, light=0.06, scale=SS * m.get("ts", 1.0))
    c.paste_tex(tex, [(x0, top), (x1, top), (x1, ground), (x0, ground)])
    roof = m.get("roof", "flat")
    rc = m.get("rcol", "#3A3D40")
    rmat = m.get("rmat", "metal")
    ov = m.get("ov", 14)
    rh = m.get("rh", 0)
    if roof == "gable":
        pts = [(x0 - ov, top + 2), ((x0 + x1) / 2, top - rh), (x1 + ov, top + 2)]
        t = texture(c.r, (x1 - x0 + 2 * ov) * SS, rh * SS + 4, rmat, rc, 0.1, SS)
        c.paste_tex(t, pts)
        c.line([(x0 - ov, top + 2), ((x0 + x1) / 2, top - rh), (x1 + ov, top + 2)], shade(rc, -0.35), 3)
        gpts = [(x0 + 4, top), ((x0 + x1) / 2, top - rh + 10), (x1 - 4, top)]
        if m.get("gablefill"):
            c.poly(gpts, m["gablefill"])
    elif roof == "hip":
        inset = m.get("inset", rh * 1.4)
        pts = [(x0 - ov, top + 2), (x0 + inset, top - rh), (x1 - inset, top - rh), (x1 + ov, top + 2)]
        t = texture(c.r, (x1 - x0 + 2 * ov) * SS, rh * SS + 4, rmat, rc, 0.1, SS)
        c.paste_tex(t, pts)
        c.line([(x0 - ov, top + 2), (x0 + inset, top - rh), (x1 - inset, top - rh), (x1 + ov, top + 2)], shade(rc, -0.35), 3)
    elif roof == "shed":
        pts = [(x0 - ov, top + 4), (x0 - ov, top - rh * 0.25), (x1 + ov, top - rh), (x1 + ov, top + 4)]
        c.poly(pts, rc)
        c.rect(x0 - ov, top - 2, x1 + ov, top + 6, shade(rc, -0.3))
    else:
        c.rect(x0 - ov * 0.4, top - 10, x1 + ov * 0.4, top + 2, rc)
        c.rect(x0 - ov * 0.4, top + 2, x1 + ov * 0.4, top + 5, shade(rc, -0.35))
    eave = np.ones((8, 8, 3), np.float32) * 0.0
    sh = Image.new("L", (int((x1 - x0) * SS), int(26 * SS)), 0)
    g = np.linspace(110, 0, sh.size[1])[:, None] * np.ones((1, sh.size[0]))
    sh = Image.fromarray(g.astype(np.uint8), "L")
    c.im.paste(Image.new("RGB", sh.size, (20, 20, 25)), (int(x0 * SS), int((top + 2) * SS)), sh)
    c.d = ImageDraw.Draw(c.im)
    for wdef in m.get("win", []):
        wx0, wy0, wx1, wy1 = wdef[:4]
        cols = wdef[4] if len(wdef) > 4 else 2
        rows = wdef[5] if len(wdef) > 5 else 1
        window(c, x0 + wx0 * (x1 - x0), top + wy0 * m["h"], x0 + wx1 * (x1 - x0), top + wy1 * m["h"], mode, m.get("frame", "#26292C"), cols, rows)
    for dd in m.get("door", []):
        dx0, dx1, dh = dd
        X0, X1 = x0 + dx0 * (x1 - x0), x0 + dx1 * (x1 - x0)
        c.rect(X0 - 4, ground - dh - 4, X1 + 4, ground, m.get("frame", "#26292C"))
        c.rect(X0, ground - dh, X1, ground, m.get("doorcol", "#5A3B26"))
        c.line([((X0 + X1) / 2, ground - dh), ((X0 + X1) / 2, ground)], shade(m.get("doorcol", "#5A3B26"), -0.3), 2)
        if mode == "dusk":
            c.glow((X0 + X1) / 2, ground - dh - 10, 22, "#FFD08A", 0.5)
    for ch in m.get("chim", []):
        cx, cw, chh = ch
        X = x0 + cx * (x1 - x0)
        tx = texture(c.r, cw * SS, (chh + rh) * SS, m.get("chmat", "stone"), m.get("chcol", "#9C9286"), 0.05, SS)
        c.paste_tex(tx, [(X, top - rh * 0.6 - chh), (X + cw, top - rh * 0.6 - chh), (X + cw, top), (X, top)])
        c.rect(X - 3, top - rh * 0.6 - chh - 6, X + cw + 3, top - rh * 0.6 - chh, shade(m.get("chcol", "#9C9286"), -0.3))
    if m.get("garage"):
        gx0, gx1, gh = m["garage"]
        X0, X1 = x0 + gx0 * (x1 - x0), x0 + gx1 * (x1 - x0)
        c.rect(X0 - 4, ground - gh - 4, X1 + 4, ground, m.get("frame", "#26292C"))
        gt = texture(c.r, (X1 - X0) * SS, gh * SS, "siding", m.get("gcol", "#6A5240"), 0.05, SS * 1.6)
        c.paste_tex(gt, [(X0, ground - gh), (X1, ground - gh), (X1, ground), (X0, ground)])
    for lt in m.get("lights", []):
        X = x0 + lt[0] * (x1 - x0)
        Y = top + lt[1] * m["h"]
        c.rect(X - 3, Y - 6, X + 3, Y + 6, "#2A2A2A")
        if mode == "dusk":
            c.glow(X, Y + 4, 18, "#FFD8A0", 0.6)


def house_scene(spec):
    W, H = spec.get("size", (1600, 1000))
    c = Canvas(W, H, spec["seed"])
    mode = spec.get("mode", "day")
    if mode == "dusk":
        sky(c, spec.get("sky0", "#33405E"), spec.get("sky1", "#F2B48A"), (0.18, 0.62, 0.03, "#FFD6A0"), 0.14, "#E3A693")
    else:
        sky(c, spec.get("sky0", "#7FA6C9"), spec.get("sky1", "#E7EEF2"), (0.8, 0.2, 0.03, "#FFFBEA"), 0.45)
    ground = spec.get("ground", 0.72) * H
    hills(c, ground - spec.get("hillh", 150), spec.get("hilla", 60), spec.get("hills", ["#9DB0B8", "#7E958E", "#5F7A68"]))
    if spec.get("water"):
        wy = ground - 30
        g = P.vgrad(40, 40, spec.get("watertop", "#9FB7C6"), spec.get("waterbot", "#6E8C9E"), 1)
        c.paste_tex(g, [(0, wy - 30), (W, wy - 30), (W, ground + 40), (0, ground + 40)])
    bg_trees = spec.get("trees", "#4E6B4C")
    r = c.r
    for k in range(spec.get("ntrees", 16)):
        x = r.random() * W
        h = 140 + r.random() * 170
        tree(c, x, ground + 6, h, mixc(bg_trees, "#8FA88A", r.random() * 0.3), spec.get("treekind", "round"))
    lawn = P.vgrad(int(H - ground + 20), 40, spec.get("lawn0", "#7C9A5E"), spec.get("lawn1", "#4F6E3E"), 1)
    lawn *= (1 + (P.vnoise(lawn.shape[0], 40, 8, r, 2) - 0.5) * 0.1)[..., None]
    c.paste_tex(lawn, [(0, ground - 4), (W, ground - 4), (W, H), (0, H)])
    cx = W * spec.get("cx", 0.5)
    sc = spec.get("scale", 1.0)
    masses = sorted(spec["masses"], key=lambda m: 0 if m.get("back") else 1)
    for m in masses:
        mm = dict(m)
        mm["x0"] = cx + m["x0"] * sc
        mm["x1"] = cx + m["x1"] * sc
        mm["h"] = m["h"] * sc
        mm["rh"] = m.get("rh", 0) * sc
        g = ground - m.get("lift", 0) * sc
        mass(c, mm, g, mode)
    c.rect(cx + spec["masses"][0]["x0"] * sc - 30, ground - 4, cx + max(m["x1"] for m in spec["masses"]) * sc + 30, ground + 6, spec.get("plinth", "#BDB4A6"))
    if spec.get("pool"):
        px0, px1, py0, py1 = spec["pool"]
        g = P.vgrad(40, 40, "#8CC7D2", "#3E8DA3", 1)
        qx0 = cx + (W * px0 - W * 0.5) * sc
        qx1 = cx + (W * px1 - W * 0.5) * sc
        c.rect(qx0 - 8, H * py0 - 8, qx1 + 8, H * py1 + 8, "#D9D2C4")
        c.paste_tex(g, [(qx0, H * py0), (qx1, H * py0), (qx1, H * py1), (qx0, H * py1)])
        for k in range(14):
            yy = H * py0 + (H * (py1 - py0)) * r.random()
            xx = qx0 + (qx1 - qx0) * r.random()
            c.line([(xx, yy), (xx + 30 + r.random() * 40, yy)], "#CFEFF4", 1.4)
    path = spec.get("path")
    if path:
        a, b = path
        c.poly([(cx + a * sc - 12, ground + 4), (cx + b * sc + 12, ground + 4), (cx + b * sc + 120, H), (cx + a * sc - 120, H)], spec.get("pathcol", "#CFC6B6"))
    for k in range(spec.get("nshrubs", 8)):
        x = r.random() * W
        shrub(c, x, ground + 20 + r.random() * 30, 60 + r.random() * 80, 26, spec.get("shrub", "#55744A"), spec.get("flowers"))
    hedge = spec.get("hedge")
    if hedge:
        c.rect(0, H - 70, W * 0.32, H - 20, hedge)
        c.rect(W * 0.68, H - 70, W, H - 20, hedge)
    for t in spec.get("fronttrees", []):
        tree(c, W * t[0], H * t[1], t[2], spec.get("ftcol", "#3F5E3C"), t[3] if len(t) > 3 else "round")
    if mode == "dusk":
        for m in spec["masses"]:
            for wdef in m.get("win", []):
                x = cx + (m["x0"] + (m["x1"] - m["x0"]) * (wdef[0] + wdef[2]) / 2) * sc
                c.glow(x, ground + 18, 50 * sc, "#E9A86A", 0.18)
    return c.finish()


def contact(paths, out, cols=4, tw=400):
    ims = [Image.open(p).convert("RGB") for p in paths]
    th = int(tw * 0.625)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 8) + 8), (40, 40, 40))
    for i, im in enumerate(ims):
        im = im.copy()
        im.thumbnail((tw, th))
        sheet.paste(im, (8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 8)))
    sheet.save(out)
