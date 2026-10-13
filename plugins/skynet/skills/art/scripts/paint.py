import math
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

LONG = 1400


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def size_of(spec):
    m = re.match(r"(\d+)\s*×\s*(\d+)", spec)
    hh, ww = float(m.group(1)), float(m.group(2))
    if hh >= ww:
        return int(round(LONG * ww / hh)), LONG
    return LONG, int(round(LONG * hh / ww))


def vnoise(h, w, cell, r, octaves=4, persist=0.5):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        gh, gw = max(2, int(h / cell) + 3), max(2, int(w / cell) + 3)
        g = r.random((gh, gw)).astype(np.float32)
        out += amp * np.asarray(Image.fromarray(g, mode="F").resize((w, h), Image.BICUBIC))
        tot += amp
        amp *= persist
        cell = max(2.0, cell / 2)
    return np.clip(out / tot, 0, 1)


def noise1(n, cell, r, octaves=5, persist=0.5):
    out = np.zeros(n, np.float32)
    amp, tot = 1.0, 0.0
    x = np.arange(n, dtype=np.float32)
    for _ in range(octaves):
        k = int(n / cell) + 3
        pts = r.random(k).astype(np.float32)
        xs = np.arange(k) * cell
        out += amp * np.interp(x, xs, pts)
        tot += amp
        amp *= persist
        cell = max(2.0, cell / 2)
    out = out / tot
    return ndi.gaussian_filter1d(out, 2)


def blur(a, s):
    if a.ndim == 3:
        return ndi.gaussian_filter(a, (s, s, 0))
    return ndi.gaussian_filter(a, s)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def fill(h, w, c):
    return np.ones((h, w, 3), np.float32) * hexc(c) if isinstance(c, str) else np.ones((h, w, 3), np.float32) * c


def over(base, color, mask):
    m = mask[..., None]
    col = hexc(color) if isinstance(color, str) else color
    return base * (1 - m) + col * m


def vgrad(h, w, c0, c1, power=1.0):
    t = (np.linspace(0, 1, h, dtype=np.float32) ** power)[:, None, None]
    a = hexc(c0) if isinstance(c0, str) else c0
    b = hexc(c1) if isinstance(c1, str) else c1
    return np.broadcast_to(a * (1 - t) + b * t, (h, w, 3)).copy()


def mix(a, b, t):
    a = hexc(a) if isinstance(a, str) else a
    b = hexc(b) if isinstance(b, str) else b
    return a * (1 - t) + b * t


def canvas_tex(h, w, r, strength=0.05):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = np.sin(xx * math.pi / 2.2) * np.sin(yy * math.pi / 2.2)
    fine = r.random((h, w)).astype(np.float32) - 0.5
    fine = blur(fine, 0.6)
    t = 1 + strength * (0.5 * weave + 1.4 * fine)
    return t[..., None]


def paper_tex(h, w, r, strength=0.05):
    mott = vnoise(h, w, 120, r, 4) - 0.5
    fib = r.random((h, w)).astype(np.float32) - 0.5
    fib = ndi.uniform_filter1d(fib, 9, axis=1) * 0.6 + ndi.uniform_filter1d(fib, 9, axis=0) * 0.6
    grain = blur(r.random((h, w)).astype(np.float32) - 0.5, 0.7)
    return (1 + strength * (0.6 * mott + 1.2 * fib + 0.8 * grain))[..., None]


def warp(img, r, amp=4.0, cell=40):
    h, w = img.shape[:2]
    dx = (vnoise(h, w, cell, r, 3) - 0.5) * 2 * amp
    dy = (vnoise(h, w, cell, r, 3) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cy, cx = np.clip(yy + dy, 0, h - 1), np.clip(xx + dx, 0, w - 1)
    if img.ndim == 2:
        return ndi.map_coordinates(img, [cy, cx], order=1)
    return np.stack([ndi.map_coordinates(img[..., c], [cy, cx], order=1) for c in range(img.shape[2])], -1)


def streaks(h, w, r, length=31, axis=1, strength=0.06):
    n = r.random((h, w)).astype(np.float32)
    n = ndi.uniform_filter1d(n, length, axis=axis)
    n = (n - n.mean()) / (n.std() + 1e-6)
    return (1 + strength * n * 0.5)[..., None]


def brushify(img, r, amp=3.0, cell=36, length=27, axis=1, strength=0.08):
    h, w = img.shape[:2]
    out = warp(img, r, amp, cell)
    return out * streaks(h, w, r, length, axis, strength)


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def from_img(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0


def mask_draw(h, w, fn, ss=2):
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    fn(d, ss)
    if ss != 1:
        im = im.resize((w, h), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def rough(mask, r, amt=0.25, cell=6, soft=1.2):
    h, w = mask.shape
    m = blur(mask, soft)
    n = vnoise(h, w, cell, r, 2) - 0.5
    return smooth(0.5 - 0.08, 0.5 + 0.08, m + n * amt)


def colorfield(spec, r, W, H, P):
    img = fill(H, W, P["ground"])
    img *= (1 + (vnoise(H, W, 220, r, 3) - 0.5) * 0.16)[..., None]
    for box, col in P["rects"]:
        x0, y0, x1, y1 = box
        m = np.zeros((H, W), np.float32)
        m[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = 1
        m = blur(m, P.get("feather", 14))
        n = vnoise(H, W, 30, r, 3) - 0.5
        m = smooth(0.15, 0.85, m + n * 0.3)
        body = fill(H, W, col)
        body *= (1 + (vnoise(H, W, 160, r, 4) - 0.5) * P.get("var", 0.22))[..., None]
        if "glow" in P:
            g = blur(m, 40)
            img = over(img, P["glow"], np.clip(g * 0.8, 0, 1) * (1 - m))
        scum = smooth(0.55, 0.85, vnoise(H, W, 18, r, 3)) * (1 - smooth(0.6, 0.98, m)) * 0.55
        img = img * (1 - m[..., None]) + body * m[..., None]
        img = over(img, P["ground"], scum * m)
    img = brushify(img, r, amp=2.5, cell=30, length=35, axis=P.get("axis", 1), strength=0.07)
    return img * canvas_tex(H, W, r, 0.045)


def aniso(H, W, cell, r, octaves=4, squash=4):
    n = vnoise(H, max(4, W // squash), cell / squash, r, octaves)
    return np.asarray(Image.fromarray(n, mode="F").resize((W, H), Image.BICUBIC))


def ridge(W, base, amp, cell, r, sharp=0.5):
    big = noise1(W, cell, r, 3)
    ridged = 1 - np.abs(big * 2 - 1)
    shape = (1 - sharp) * big + sharp * ridged
    det = noise1(W, 30, r, 3) - 0.5
    return base - (shape - 0.5) * 2 * amp - det * amp * 0.12


def landscape(spec, r, W, H, P):
    hz = P.get("horizon", 0.62)
    img = vgrad(H, W, P["sky0"], P["sky1"], P.get("skyp", 1.2))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if "sun" in P:
        sx, sy, sr, sc = P["sun"]
        d = np.sqrt((xx - sx * W) ** 2 + (yy - sy * H) ** 2)
        img = over(img, sc, np.exp(-(d / (sr * W * 5)) ** 2) * 0.5)
        img = over(img, sc, 1 - smooth(sr * W * 0.85, sr * W * 1.05, d))
    cl = aniso(H, W, 200, r, 4, 5)
    cmask = smooth(0.5, 0.78, cl) * (1 - smooth(0.1, P.get("top", 0.4) + 0.05, yy / H))
    img = over(img, P.get("cloud", P["sky1"]), cmask * P.get("cloudamt", 0.45))
    layers = P["layers"]
    n = len(layers)
    water = P.get("water")
    col_y = np.arange(H, dtype=np.float32)[:, None]
    haze = P.get("haze", P["sky1"])
    for i, col in enumerate(layers):
        t = i / max(1, n - 1)
        base = (P.get("top", 0.4) + (hz - P.get("top", 0.4)) * t) * H
        if water:
            base = min(base, water * H - 0.02 * H)
        amp = P.get("amp", 0.08) * H * (1.25 - 0.5 * t)
        rid = ridge(W, base, amp, W * (0.45 - 0.2 * t) * (0.8 + 0.4 * r.random()), r, P.get("sharp", 0.45))
        m = smooth(-1.2, 1.2, col_y - rid[None, :])
        fade = smooth(0, P.get("mist", 0.14) * H, col_y - rid[None, :])
        mamt = P.get("mistamt", 0.5) * (1 - 0.5 * t)
        layer = fill(H, W, col)
        layer = layer * (1 - fade[..., None] * mamt) + hexc(haze) * fade[..., None] * mamt
        layer *= (1 + (vnoise(H, W, 60, r, 3) - 0.5) * 0.08)[..., None]
        img = img * (1 - m[..., None]) + layer * m[..., None]
    if water:
        wy = int(water * H)
        hh = H - wy
        src = img[max(0, wy - hh):wy][::-1]
        if src.shape[0] < hh:
            src = np.concatenate([src, np.repeat(src[-1:], hh - src.shape[0], 0)], 0)
        ys = np.arange(hh, dtype=np.float32)[:, None]
        off = np.sin(ys * 0.5 + (vnoise(hh, W, 80, r, 2) - 0.5) * 6) * (1 + ys / hh * 5)
        xs = np.clip(np.arange(W, dtype=np.float32)[None, :] + off, 0, W - 1)
        yq = np.clip(ys + np.sin(ys * 0.21) * 1.5, 0, hh - 1)
        refl = np.stack([ndi.map_coordinates(src[..., c], [np.repeat(yq, W, 1), xs], order=1) for c in range(3)], -1)
        refl = blur(refl, 1.2)
        wc = hexc(P.get("watercol", P["sky1"]))
        tt = (0.2 + 0.45 * ys / hh)[..., None]
        refl = refl * (1 - tt) + wc * tt
        line = smooth(0.62, 0.8, aniso(hh, W, 90, r, 3, 12))
        refl = over(refl, P.get("glint", "#FFFFFF"), line * 0.22)
        img[wy:] = refl
    if P.get("rain"):
        rn = r.random((H + 200, W + 200)).astype(np.float32)
        rn = ndi.rotate(rn, -16, reshape=False, mode="reflect")
        rn = ndi.uniform_filter1d(rn, 61, axis=0)
        rn = ndi.rotate(rn, 16, reshape=False, mode="reflect")[100:100 + H, 100:100 + W]
        rn = (rn - rn.mean()) / rn.std()
        rmask = smooth(1.2, 2.6, rn) * (0.4 + 0.6 * vnoise(H, W, 200, r, 2))
        img = over(img, P.get("raincol", "#D8DDE2"), rmask * 0.4)
    img = brushify(img, r, amp=3.0, cell=26, length=33, axis=1, strength=0.08)
    return img * canvas_tex(H, W, r, 0.05)


PAPER = "#F1ECE0"


def rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def lino_finish(im, r, W, H, paper=PAPER, wob=1.2, mott=0.3):
    im = im.resize((W, H), Image.LANCZOS)
    a = from_img(im)
    a = warp(a, r, wob, 10)
    p = hexc(paper)
    ink = np.clip(np.sqrt(((a - p) ** 2).sum(-1)) / 0.25, 0, 1)
    fine = vnoise(H, W, 5, r, 2)
    m = smooth(0.58, 0.74, fine) * mott + (vnoise(H, W, 90, r, 3) - 0.5) * 0.12
    m = np.clip(m, 0, 1) * ink
    a = a * (1 - m[..., None]) + p * m[..., None]
    return a * paper_tex(H, W, r, 0.06)


def wave_line(d, x0, x1, y, amp, lam, ph, r, fillc, width, ss, step=6):
    pts = []
    x = x0
    while x <= x1:
        yy = y + amp * math.sin(2 * math.pi * x / lam + ph) + (r.random() - 0.5) * width * 0.3
        pts.append((x, yy))
        x += step * ss
    if len(pts) > 1:
        d.line(pts, fill=fillc, width=int(width), joint="curve")


def linosea(spec, r, W, H, P):
    ss = 2
    w, h = W * ss, H * ss
    im = Image.new("RGB", (w, h), rgb(PAPER))
    d = ImageDraw.Draw(im)
    light, mid, dark = rgb(P["light"]), rgb(P["mid"]), rgb(P["dark"])
    pap = rgb(PAPER)
    hz = int(0.44 * h)
    d.rectangle([0, 0, w, hz], fill=light)
    for i in range(26):
        y = int(hz * (i + 0.5) / 26)
        x0 = int(r.random() * w * 0.5)
        x1 = x0 + int(w * (0.15 + r.random() * 0.5))
        d.line([(x0, y), (x1, y)], fill=pap, width=int(ss * (1.5 + r.random() * 1.5)))
    sx, sy, sr = int(w * 0.22), int(hz * 0.42), int(w * 0.07)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=pap)
    for k in range(1, 4):
        rr = sr + k * ss * 14
        d.arc([sx - rr, sy - rr, sx + rr, sy + rr], 200, 340, fill=pap, width=ss * 2)
    d.rectangle([0, hz, w, h], fill=mid)
    rows = 13
    for i in range(rows):
        t = i / rows
        y = hz + (h - hz) * (t ** 1.3) + 10
        amp = ss * (4 + 22 * t)
        lam = w * (0.06 + 0.12 * t)
        ph = r.random() * 6
        band = int(ss * (4 + 18 * t))
        wave_line(d, -50, w + 50, y + band, amp, lam, ph, r, dark, band, ss)
        wave_line(d, -50, w + 50, y, amp, lam, ph, r, pap, max(2, int(band * 0.28)), ss)
        if t > 0.35:
            for k in range(int(4 + 6 * t)):
                cx = r.random() * w
                cy = y + amp * math.sin(2 * math.pi * cx / lam + ph) - amp * 0.4
                cr = ss * (6 + 14 * t)
                d.arc([cx - cr, cy - cr, cx + cr, cy + cr], 180, 330, fill=pap, width=ss * 3)
    deck_y = int(0.39 * h)
    x0 = int(0.42 * w)
    d.rectangle([x0, deck_y, w, deck_y + int(0.03 * h)], fill=dark)
    d.line([(x0, deck_y - ss * 18), (w, deck_y - ss * 18)], fill=dark, width=ss * 4)
    px = x0 + ss * 20
    while px < w:
        d.line([(px, deck_y - ss * 18), (px, deck_y)], fill=dark, width=ss * 4)
        d.polygon([(px - ss * 7, deck_y), (px + ss * 7, deck_y), (px + ss * 5, int(0.64 * h)), (px - ss * 5, int(0.64 * h))], fill=dark)
        for k in range(5):
            yy = deck_y + int((0.64 * h - deck_y) * (k + 0.5) / 5)
            d.line([(px - ss * 4, yy), (px + ss * 4, yy + ss * 6)], fill=mid, width=ss * 2)
        px += int(w * 0.07)
    lx = x0 + int(w * 0.05)
    top = deck_y - int(0.2 * h)
    d.polygon([(lx - ss * 26, deck_y), (lx + ss * 26, deck_y), (lx + ss * 17, top), (lx - ss * 17, top)], fill=dark)
    d.rectangle([lx - ss * 22, top - ss * 34, lx + ss * 22, top], fill=dark)
    d.rectangle([lx - ss * 14, top - ss * 28, lx + ss * 14, top - ss * 6], fill=rgb(P["lamp"]))
    d.polygon([(lx - ss * 26, top - ss * 34), (lx + ss * 26, top - ss * 34), (lx, top - ss * 56)], fill=dark)
    for k in range(3):
        yy = top + int((deck_y - top) * (k + 1) / 4)
        d.rectangle([lx - ss * 5, yy - ss * 9, lx + ss * 5, yy + ss * 9], fill=pap)
    for k in range(70):
        cx = x0 + r.random() * (w - x0)
        cy = int(0.62 * h) + (r.random() - 0.3) * h * 0.08
        cr = ss * (2 + r.random() * 6)
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=pap)
    return lino_finish(im, r, W, H)


def linowave(spec, r, W, H, P):
    ss = 2
    w, h = W * ss, H * ss
    im = Image.new("RGB", (w, h), rgb(PAPER))
    d = ImageDraw.Draw(im)
    light, mid, dark = rgb(P["light"]), rgb(P["mid"]), rgb(P["dark"])
    pap = rgb(PAPER)
    d.rectangle([0, 0, w, h], fill=light)
    for i in range(18):
        y = int(0.42 * h * (i + 0.5) / 18)
        x0 = int(r.random() * w * 0.6)
        d.line([(x0, y), (x0 + int(w * (0.1 + r.random() * 0.4)), y)], fill=pap, width=ss * 2)
    xs = np.linspace(-0.05, 1.05, 400)

    def crest(x):
        return 0.22 + 0.36 * (1 - np.exp(-((x - 0.62) / 0.33) ** 2) * 0.9) + 0.03 * np.sin(x * 9)
    cy = crest(xs)
    poly = [(x * w, y * h) for x, y in zip(xs, cy)] + [(w * 1.05, h * 1.05), (-0.05 * w, h * 1.05)]
    d.polygon(poly, fill=mid)
    for k in range(1, 22):
        off = k * 0.034
        col = dark if k % 3 == 0 else (light if k % 3 == 1 else mid)
        wd = ss * (5 + k * 0.9)
        pts = [(x * w, (y + off + 0.012 * math.sin(x * 14 + k)) * h) for x, y in zip(xs, cy)]
        d.line(pts, fill=col, width=int(wd), joint="curve")
        pts2 = [(x * w, (y + off + 0.012 * math.sin(x * 14 + k)) * h - wd * 0.5) for x, y in zip(xs, cy)]
        d.line(pts2, fill=pap, width=ss * 2, joint="curve")
    for x, y in zip(xs[::5], cy[::5]):
        for j in range(3):
            cr = ss * (5 + r.random() * 9)
            fx = x * w + (r.random() - 0.5) * 30
            fy = y * h - cr * (0.6 + j * 1.3) + r.random() * 6
            d.ellipse([fx - cr, fy - cr, fx + cr, fy + cr], fill=pap)
            d.arc([fx - cr, fy - cr, fx + cr, fy + cr], 20, 160, fill=mid, width=ss * 2)
    for k in range(160):
        fx, fy = r.random() * w, (0.1 + r.random() * 0.4) * h
        if fy < crest(np.array([fx / w]))[0] * h - 30:
            cr = ss * (1.5 + r.random() * 3)
            d.ellipse([fx - cr, fy - cr, fx + cr, fy + cr], fill=pap)
    return lino_finish(im, r, W, H)


def building_row(d, r, w, h, x0, x1, base, hmin, hmax, colr, win_on, win_off, ss, lit=0.35):
    x = x0
    while x < x1:
        bw = int(w * (0.08 + r.random() * 0.1))
        bh = int(h * (hmin + r.random() * (hmax - hmin)))
        top = base - bh
        d.rectangle([x, top, x + bw, base], fill=colr)
        if r.random() < 0.4:
            d.polygon([(x, top), (x + bw, top), (x + bw // 2, top - int(bw * 0.4))], fill=colr)
        cols = max(2, bw // (ss * 22))
        rows = max(2, bh // (ss * 30))
        cw = bw / cols
        rh = bh / rows
        for i in range(cols):
            for j in range(rows - 1):
                wx = x + i * cw + cw * 0.28
                wy = top + j * rh + rh * 0.3
                c = win_on if r.random() < lit else win_off
                d.rectangle([wx, wy, wx + cw * 0.44, wy + rh * 0.45], fill=c)
        x += bw + int(ss * r.random() * 6)


def linocity(spec, r, W, H, P):
    ss = 2
    w, h = W * ss, H * ss
    im = Image.new("RGB", (w, h), rgb(PAPER))
    d = ImageDraw.Draw(im)
    night, yel, red, mid = rgb(P["night"]), rgb(P["yellow"]), rgb(P["red"]), rgb(P["mid"])
    pap = rgb(PAPER)
    d.rectangle([0, 0, w, h], fill=night)
    for k in range(60):
        cx, cy = r.random() * w, r.random() * h * 0.3
        cr = ss * (1 + r.random() * 2)
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=pap)
    if P.get("scene") == "facade":
        d.rectangle([0, 0, w, h], fill=mid)
        for j in range(int(h / (ss * 14))):
            y = j * ss * 14
            d.line([(0, y), (w, y)], fill=night, width=ss * 2)
        cols, rows = 4, 6
        mw, mh = w * 0.08, h * 0.06
        cw, rh = (w - 2 * mw) / cols, (h - 2 * mh) / rows
        for i in range(cols):
            for j in range(rows):
                x0, y0 = mw + i * cw + cw * 0.14, mh + j * rh + rh * 0.12
                x1, y1 = x0 + cw * 0.72, y0 + rh * 0.7
                d.rectangle([x0 - ss * 6, y0 - ss * 6, x1 + ss * 6, y1 + ss * 10], fill=night)
                on = r.random() < 0.42
                d.rectangle([x0, y0, x1, y1], fill=yel if on else night)
                xm = (x0 + x1) / 2
                d.line([(xm, y0), (xm, y1)], fill=night, width=ss * 4)
                d.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], fill=night, width=ss * 3)
                if on:
                    kind = r.integers(0, 4)
                    if kind == 0:
                        px = x0 + (x1 - x0) * 0.25
                        d.rectangle([px - ss * 10, y1 - ss * 22, px + ss * 10, y1], fill=red)
                        for k in range(5):
                            a = -math.pi / 2 + (k - 2) * 0.45
                            d.ellipse([px + math.cos(a) * ss * 18 - ss * 8, y1 - ss * 30 + math.sin(a) * ss * 14 - ss * 5, px + math.cos(a) * ss * 18 + ss * 8, y1 - ss * 30 + math.sin(a) * ss * 14 + ss * 5], fill=night)
                    elif kind == 1:
                        d.polygon([(x0, y0), (x0 + (x1 - x0) * 0.3, y0), (x0 + (x1 - x0) * 0.15, y1), (x0, y1)], fill=red)
                    elif kind == 2:
                        cx = x0 + (x1 - x0) * 0.7
                        d.ellipse([cx - ss * 12, y1 - ss * 22, cx + ss * 12, y1], fill=night)
                        d.ellipse([cx - ss * 8, y1 - ss * 36, cx + ss * 8, y1 - ss * 20], fill=night)
                        d.polygon([(cx - ss * 8, y1 - ss * 30), (cx - ss * 6, y1 - ss * 42), (cx - ss * 1, y1 - ss * 33)], fill=night)
                        d.polygon([(cx + ss * 8, y1 - ss * 30), (cx + ss * 6, y1 - ss * 42), (cx + ss * 1, y1 - ss * 33)], fill=night)
                else:
                    for k in range(3):
                        o = (k + 1) * (x1 - x0) / 4
                        d.line([(x0 + o, y0), (x0 + o - (y1 - y0) * 0.3, y1)], fill=mid, width=ss * 2)
        return lino_finish(im, r, W, H, wob=1.0, mott=0.2)
    base = int(h * 0.62)
    building_row(d, r, w, h, -20, w + 20, base, 0.22, 0.42, mid, yel, night, ss, 0.3)
    building_row(d, r, w, h, -40, w + 40, base + int(h * 0.02), 0.12, 0.25, night, yel, mid, ss, 0.45)
    d.rectangle([0, base, w, h], fill=night)
    for k in range(3):
        y = int(h * (0.12 + k * 0.035))
        d.line([(0, y + 40), (w, y)], fill=pap, width=ss * 2)
    tx0, tx1 = int(w * 0.18), int(w * 0.86)
    ty0, ty1 = int(h * 0.64), int(h * 0.76)
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=ss * 20, fill=red)
    d.line([((tx0 + tx1) / 2, ty0), ((tx0 + tx1) / 2 - 30, int(h * 0.15))], fill=pap, width=ss * 3)
    nwin = 6
    for i in range(nwin):
        wx0 = tx0 + (tx1 - tx0) * (0.05 + i * 0.155)
        d.rectangle([wx0, ty0 + (ty1 - ty0) * 0.15, wx0 + (tx1 - tx0) * 0.12, ty0 + (ty1 - ty0) * 0.55], fill=yel)
    d.rectangle([tx0, ty1 - (ty1 - ty0) * 0.18, tx1, ty1 - (ty1 - ty0) * 0.1], fill=pap)
    for hx in (tx0 + ss * 20, tx1 - ss * 20):
        d.ellipse([hx - ss * 9, ty1 - ss * 30, hx + ss * 9, ty1 - ss * 12], fill=yel)
        for k in range(14):
            y = ty1 + ss * 8 + k * ss * 18
            ln = ss * (12 - k * 0.6)
            if ln > 2:
                d.line([(hx, y), (hx, y + ln)], fill=yel, width=ss * (5 - k // 4))
    for k in range(30):
        y = ty1 + r.random() * (h - ty1)
        x = r.random() * w
        d.line([(x, y), (x + ss * (20 + r.random() * 70), y)], fill=mid, width=ss * 2)
    for k, off in enumerate((0.0, 0.035)):
        y = ty1 + ss * 6 + off * h
        d.line([(0, y), (w, y)], fill=mid, width=ss * (3 + k * 2))
    for i in range(4):
        wx = tx0 + (tx1 - tx0) * (0.12 + i * 0.25)
        d.ellipse([wx - ss * 10, ty1 - ss * 6, wx + ss * 10, ty1 + ss * 12], fill=night)
    d.rectangle([0, int(h * 0.9), w, h], fill=mid)
    for k in range(10):
        x = r.random() * w
        d.line([(x, int(h * 0.9) + ss * 10), (x + ss * 60, int(h * 0.9) + ss * 10)], fill=night, width=ss * 2)
    return lino_finish(im, r, W, H, wob=1.0, mott=0.18)


def rot(px, py, a):
    c, s_ = math.cos(a), math.sin(a)
    return px * c - py * s_, px * s_ + py * c


def leaf_poly(x, y, length, width, ang, bend=0.0, lobes=0, n=24, tipw=0.8):
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        hw = width * 0.5 * (math.sin(math.pi * t) ** tipw)
        if lobes:
            hw *= 0.75 + 0.25 * abs(math.sin(t * math.pi * lobes))
        cx, cy = t * length, bend * length * math.sin(math.pi * t)
        lx, ly = rot(cx, cy - hw, ang)
        rx, ry = rot(cx, cy + hw, ang)
        left.append((x + lx, y + ly))
        right.append((x + rx, y + ry))
    mid = [(x + rot(t / n * length, bend * length * math.sin(math.pi * t / n), ang)[0], y + rot(t / n * length, bend * length * math.sin(math.pi * t / n), ang)[1]) for t in range(n + 1)]
    return left + right[::-1], mid


def bez(p0, p1, p2, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


class Sheet:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.layers = []

    def layer(self, color):
        L = dict(color=color, polys=[], lines=[], dots=[])
        self.layers.append(L)
        return L


def wash(img, mask, color, r, amt=0.85, dark=True):
    H, W = mask.shape
    m = rough(mask, r, 0.12, 9, 1.4)
    dens = m * (0.55 + 0.45 * vnoise(H, W, 45, r, 3))
    if dark:
        dens += np.clip(m - blur(m, 5), 0, 1) * 1.4
    dens += (r.random((H, W)).astype(np.float32) - 0.5) * 0.12 * m
    dens = np.clip(dens * amt, 0, 1)
    c = hexc(color)
    return img * (1 - dens[..., None] * (1 - c))


def gouache(img, mask, color, r, amt=0.95):
    H, W = mask.shape
    m = rough(mask, r, 0.1, 7, 1.0)
    dry = smooth(0.25, 0.45, vnoise(H, W, 6, r, 2)) * 0.25 + 0.75
    a = np.clip(m * dry * amt, 0, 1)[..., None]
    return img * (1 - a) + hexc(color) * a


def render_sheet(sh, r, base, ink, night=False, ss=2):
    W, H = sh.W, sh.H
    img = fill(H, W, base) * paper_tex(H, W, r, 0.07 if not night else 0.12)
    inkm = np.zeros((H, W), np.float32)
    for L in sh.layers:
        def draw_fill(d, s, L=L):
            for p in L["polys"]:
                d.polygon([(x * s, y * s) for x, y in p], fill=255)
            for pts, wd in L.get("thick", []):
                d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(wd * s), joint="curve")
            for (cx, cy, rr) in L["dots"]:
                d.ellipse([(cx - rr) * s, (cy - rr) * s, (cx + rr) * s, (cy + rr) * s], fill=255)
        m = mask_draw(H, W, draw_fill, ss)
        img = gouache(img, m, L["color"], r) if night else wash(img, m, L["color"], r, L.get("amt", 0.85))

        def draw_ink(d, s, L=L):
            for pts, wd in L["lines"]:
                q = [(x * s + (r.random() - 0.5) * 1.5 * s, y * s + (r.random() - 0.5) * 1.5 * s) for x, y in pts]
                d.line(q, fill=255, width=max(1, int(wd * s)), joint="curve")
        if L["lines"]:
            inkm = np.maximum(inkm, mask_draw(H, W, draw_ink, ss))
    inkm = np.clip(inkm * (0.75 + 0.25 * vnoise(H, W, 30, r, 2)), 0, 1)
    if night:
        return img * (1 - inkm[..., None] * 0.7) + hexc(ink) * inkm[..., None] * 0.7
    return img * (1 - inkm[..., None]) + hexc(ink) * inkm[..., None]


def fern(sh, r, x, y, length, ang, curl, green, dark, lw):
    Lf = sh.layer(green)
    Ld = sh.layer(dark)
    Ld["amt"] = 0.5
    ex, ey = x + math.cos(ang) * length, y + math.sin(ang) * length
    cx, cy = x + math.cos(ang) * length * 0.5 - math.sin(ang) * length * 0.18 * curl, y + math.sin(ang) * length * 0.5 + math.cos(ang) * length * 0.18 * curl
    rach = bez((x, y), (cx, cy), (ex, ey), 60)
    Lf["lines"].append((rach, lw * 1.4))
    n = 22
    for i in range(3, n):
        t = i / n
        k = int(t * (len(rach) - 2))
        px, py = rach[k]
        qx, qy = rach[k + 1]
        a = math.atan2(qy - py, qx - px)
        L = length * 0.27 * math.sin(math.pi * (0.12 + 0.88 * (1 - t) ** 0.8)) * (1.05 - t * 0.5)
        if L < 4:
            continue
        for side in (-1, 1):
            pa = a + side * (1.05 - 0.25 * t)
            poly, mid = leaf_poly(px, py, L, L * 0.28, pa, bend=0.08 * side, lobes=5)
            (Ld if i % 4 == 0 else Lf)["polys"].append(poly)
            Lf["lines"].append((poly + [poly[0]], lw * 0.7))


def fiddle(sh, r, x, y, h, green, lw):
    L = sh.layer(green)
    pts = bez((x, y), (x + h * 0.1, y - h * 0.6), (x + h * 0.02, y - h), 30)
    L["thick"] = [(pts, lw * 4)]
    L["lines"].append((pts, lw * 1.2))
    cx, cy = pts[-1]
    sp = []
    for i in range(60):
        t = i / 60 * 4.2 * math.pi
        rr = h * 0.11 * (1 - i / 64)
        sp.append((cx - h * 0.1 + math.cos(t) * rr, cy + math.sin(t) * rr))
    L["thick"].append((sp, lw * 4))
    L["lines"].append((sp, lw * 1.2))


def botanical(spec, r, W, H, P):
    sh = Sheet(W, H)
    lw = W / 520
    kind = P["kind"]
    if kind == "fern":
        fern(sh, r, W * 0.42, H * 0.97, H * 0.86, -math.pi / 2 - 0.14, 0.8, P["green"], P["dark"], lw)
        fern(sh, r, W * 0.5, H * 0.97, H * 0.66, -math.pi / 2 + 0.5, -0.9, P["green2"], P["dark"], lw)
        fiddle(sh, r, W * 0.7, H * 0.97, H * 0.4, P["green"], lw)
        fiddle(sh, r, W * 0.2, H * 0.97, H * 0.26, P["green2"], lw)
    elif kind == "garlic":
        Lg = sh.layer(P["green"])
        Lg2 = sh.layer(P["green2"])
        for i in range(7):
            a = -math.pi / 2 + (i - 3) * 0.24 + (r.random() - 0.5) * 0.1
            ln = H * (0.4 + r.random() * 0.14)
            poly, mid = leaf_poly(W * 0.5 + (i - 3) * W * 0.02, H * 0.98, ln, W * 0.12, a, bend=(i - 3) * 0.03, tipw=0.6)
            (Lg if i % 2 else Lg2)["polys"].append(poly)
            Lg["lines"].append((poly + [poly[0]], lw * 0.8))
            Lg["lines"].append((mid, lw * 0.6))
        stalk = bez((W * 0.52, H * 0.98), (W * 0.57, H * 0.55), (W * 0.54, H * 0.3), 40)
        Ls = sh.layer(P["green"])
        Ls["thick"] = [(stalk, lw * 4)]
        Ls["lines"].append((stalk, lw))
        Lw = sh.layer(P["petal"])
        Ly = sh.layer(P["eye"])
        cx, cy = stalk[-1]
        for i in range(24):
            a = -math.pi / 2 + (r.random() - 0.5) * 2.8
            dd = H * (0.08 + r.random() * 0.1)
            fx, fy = cx + math.cos(a) * dd, cy + math.sin(a) * dd
            Ls["lines"].append(([(cx, cy), (fx, fy)], lw * 0.8))
            pr = W * 0.045
            for k in range(6):
                pa = k * math.pi / 3 + r.random() * 0.3
                poly, mid = leaf_poly(fx, fy, pr, pr * 0.55, pa, tipw=0.7, n=12)
                Lw["polys"].append(poly)
                Lw["lines"].append((poly + [poly[0]], lw * 0.6))
            Ly["dots"].append((fx, fy, pr * 0.18))
    elif kind == "seeds":
        Ls = sh.layer(P["stem"])
        Lh = sh.layer(P["head"])
        Lb = sh.layer(P["brown"])
        heads = ["clock", "poppy", "teasel", "grass", "allium", "poppy", "clock"]
        for i, kd in enumerate(heads):
            bx = W * (0.15 + i * 0.12)
            tx = bx + (r.random() - 0.5) * W * 0.12
            ty = H * (0.18 + r.random() * 0.3)
            stem = bez((bx, H * 0.97), ((bx + tx) / 2 + (r.random() - 0.5) * 60, (H + ty) / 2), (tx, ty), 40)
            Ls["lines"].append((stem, lw * 1.3))
            Ls.setdefault("thick", []).append((stem, lw * 2.5))
            if kd == "clock":
                for k in range(70):
                    a = r.random() * 2 * math.pi
                    rr = W * (0.05 + r.random() * 0.015)
                    ex, ey = tx + math.cos(a) * rr, ty + math.sin(a) * rr
                    Ls["lines"].append(([(tx, ty), (ex, ey)], lw * 0.35))
                    for j in range(5):
                        b = a + (j - 2) * 0.25
                        Ls["lines"].append(([(ex, ey), (ex + math.cos(b) * rr * 0.18, ey + math.sin(b) * rr * 0.18)], lw * 0.25))
                Lb["dots"].append((tx, ty, W * 0.012))
            elif kd == "poppy":
                hw = W * 0.035
                pts = [(tx + math.sin(t / 30 * math.pi) * hw * (1 - 0.3 * (t / 30)), ty - hw * 1.3 + t / 30 * hw * 2.6) for t in range(31)]
                poly = pts + [(2 * tx - x, y) for x, y in pts[::-1]]
                Lh["polys"].append(poly)
                Lh["lines"].append((poly + [poly[0]], lw * 0.8))
                for k in range(9):
                    a = -math.pi / 2 + (k - 4) * 0.28
                    Lb["lines"].append(([(tx, ty - hw * 1.3), (tx + math.cos(a) * hw * 0.8, ty - hw * 1.3 + math.sin(a) * hw * 0.5)], lw * 0.9))
                Lb["polys"].append([(tx - hw * 0.8, ty - hw * 1.3), (tx + hw * 0.8, ty - hw * 1.3), (tx, ty - hw * 1.65)])
            elif kd == "teasel":
                poly, mid = leaf_poly(tx, ty + W * 0.07, W * 0.14, W * 0.075, -math.pi / 2, tipw=0.6)
                Lb["polys"].append(poly)
                Lb["lines"].append((poly + [poly[0]], lw * 0.8))
                for k in range(80):
                    px = tx + (r.random() - 0.5) * W * 0.06
                    py = ty + W * 0.07 - r.random() * W * 0.14
                    Lb["lines"].append(([(px, py), (px + (px - tx) * 0.4, py - W * 0.012)], lw * 0.5))
                for side in (-1, 1):
                    br = bez((tx, ty + W * 0.07), (tx + side * W * 0.08, ty + W * 0.05), (tx + side * W * 0.07, ty - W * 0.04), 20)
                    Ls["lines"].append((br, lw * 0.8))
            elif kd == "grass":
                for k in range(12):
                    t = k / 12
                    px, py = tx + math.sin(t * 2) * W * 0.01, ty + t * H * 0.12
                    for side in (-1, 1):
                        poly, mid = leaf_poly(px, py, W * 0.03, W * 0.012, -math.pi / 2 + side * 0.5, n=10)
                        Lh["polys"].append(poly)
                        Lh["lines"].append((poly + [poly[0]], lw * 0.5))
            elif kd == "allium":
                for k in range(40):
                    a = r.random() * 2 * math.pi
                    rr = W * (0.03 + r.random() * 0.03)
                    ex, ey = tx + math.cos(a) * rr, ty + math.sin(a) * rr
                    Lb["lines"].append(([(tx, ty), (ex, ey)], lw * 0.45))
                    for j in range(3):
                        b = a + (j - 1) * 0.6
                        Lb["lines"].append(([(ex, ey), (ex + math.cos(b) * W * 0.008, ey + math.sin(b) * W * 0.008)], lw * 0.4))
                    Lh["dots"].append((ex, ey, W * 0.004))
    elif kind == "quince":
        Lbr = sh.layer(P["brown"])
        Lg = sh.layer(P["green"])
        Lp = sh.layer(P["petal"])
        Lf = sh.layer(P["fruit"])
        Lf2 = sh.layer(P["fruit2"])
        main = bez((W * -0.02, H * 0.78), (W * 0.45, H * 0.62), (W * 1.0, H * 0.2), 60)
        for k in range(len(main) - 1):
            t = k / len(main)
            Lbr.setdefault("thick", []).append(([main[k], main[k + 1]], lw * (22 - 15 * t)))
        Lbr["lines"].append((main, lw * 1.2))
        twigs = []
        for k in (12, 22, 33, 44, 52):
            px, py = main[k]
            side = -1 if k % 2 else 1
            end = (px + W * 0.08 * (0.5 + r.random()), py + side * H * 0.16)
            tw = bez((px, py), (px + W * 0.04, py + side * H * 0.04), end, 16)
            Lbr["thick"].append((tw, lw * 4))
            Lbr["lines"].append((tw, lw))
            twigs.append(end)
        for i, (ex, ey) in enumerate(twigs + main[8::9]):
            for j in range(3):
                a = (r.random() - 0.5) * 3 - math.pi / 2 + (0.8 if i % 2 else -0.8)
                poly, mid = leaf_poly(ex, ey, W * 0.11, W * 0.055, a, bend=0.1, tipw=0.7)
                Lg["polys"].append(poly)
                Lg["lines"].append((poly + [poly[0]], lw * 0.7))
                Lg["lines"].append((mid, lw * 0.5))
        for (ex, ey) in twigs[::2] + [main[38]]:
            for k in range(5):
                a = k * 2 * math.pi / 5
                poly, mid = leaf_poly(ex, ey, W * 0.042, W * 0.04, a, tipw=0.5, n=14)
                Lp["polys"].append(poly)
                Lp["lines"].append((poly + [poly[0]], lw * 0.5))
            Lbr["dots"].append((ex, ey, W * 0.006))
        for (px, py) in (main[28], main[48]):
            fr = W * 0.075
            cx, cy = px + fr * 0.2, py + fr * 1.3
            pts = []
            for k in range(40):
                a = k / 40 * 2 * math.pi
                rr = fr * (1 + 0.12 * math.cos(a * 2) - 0.18 * max(0, -math.sin(a)))
                pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 1.1))
            Lf["polys"].append(pts)
            Lf["lines"].append((pts + [pts[0]], lw * 0.8))
            sh_ = [(cx + fr * 0.15 + math.cos(a) * fr * 0.7, cy + fr * 0.2 + math.sin(a) * fr * 0.8) for a in np.linspace(-1.2, 1.9, 20)]
            Lf2["polys"].append(sh_ + [(cx + fr * 0.2, cy + fr * 0.2)])
            Lbr["lines"].append(([(px, py), (cx, cy - fr * 1.05)], lw * 1.2))
    return render_sheet(sh, r, P.get("paper", "#F4EFE4"), P.get("ink", "#2B2A26"), night=P.get("night", False))


def vstreak(H, W, cell, r, squash=6):
    n = vnoise(max(4, H // squash), W, cell, r, 3)
    return np.asarray(Image.fromarray(n, mode="F").resize((W, H), Image.BICUBIC))


def ink_mountain(D, r, cx, base, height, width, fall, strength, sharp=1.6, detail=0.14):
    H, W = D.shape
    xs = np.arange(W, dtype=np.float32)
    prof = base - height * np.exp(-(np.abs(xs - cx) / width) ** sharp)
    prof -= (noise1(W, 38, r, 4) - 0.5) * height * detail * 2
    prof -= (1 - np.abs(noise1(W, 140, r, 3) * 2 - 1)) * height * 0.12
    yy = np.arange(H, dtype=np.float32)[:, None]
    below = yy - prof[None, :]
    inside = smooth(-1, 1.5, below)
    streak = smooth(0.45, 0.75, vstreak(H, W, 14, r, 7))
    body = np.exp(-np.clip(below, 0, None) / fall) * (0.35 + 0.65 * streak)
    edge = np.exp(-(below / 3.0) ** 2) * (0.6 + 0.4 * smooth(0.3, 0.6, vnoise(H, W, 12, r, 2)))
    dens = np.clip((body * 0.9 + edge * 0.8) * strength * inside, 0, 1)
    occl = smooth(0, 4, below)
    return D * (1 - occl) + dens


def mist(D, y0, y1, amt):
    H = D.shape[0]
    yy = np.arange(H, dtype=np.float32)[:, None] / H
    band = smooth(y0, (y0 + y1) / 2, yy) * (1 - smooth((y0 + y1) / 2, y1, yy))
    return D * (1 - band * amt)


def pine(d, r, x, y, h, lean, s):
    top = (x + lean * h, y - h)
    trunk = bez((x, y), (x + lean * h * 0.15 + h * 0.12, y - h * 0.55), top, 40)
    for k in range(len(trunk) - 1):
        t = k / len(trunk)
        wd = h * (0.045 - 0.032 * t)
        d.line([(trunk[k][0] * s, trunk[k][1] * s), (trunk[k + 1][0] * s, trunk[k + 1][1] * s)], fill=235, width=max(1, int(wd * s)))
    for k in range(10):
        t = 0.12 + r.random() * 0.8
        i = int(t * len(trunk))
        px, py = trunk[i]
        d.line([((px - h * 0.012) * s, py * s), ((px + h * 0.012) * s, (py - h * 0.01) * s)], fill=120, width=max(1, int(s * 1.5)))
    for i in range(8):
        t = 0.4 + i * 0.085
        k = min(len(trunk) - 1, int(t * len(trunk)))
        tx, ty = trunk[k]
        side = -1 if i % 2 else 1
        blen = h * (0.32 - 0.24 * (t - 0.4) / 0.6) * (0.8 + 0.4 * r.random())
        bx, by = tx + side * blen, ty + h * 0.02 * r.random()
        br = bez((tx, ty), (tx + side * blen * 0.5, ty - h * 0.03), (bx, by), 12)
        d.line([(px_ * s, py_ * s) for px_, py_ in br], fill=225, width=max(1, int(h * 0.012 * s)), joint="curve")
        for c in range(4):
            u = 0.35 + c * 0.22
            cx, cy = br[min(len(br) - 1, int(u * len(br)))]
            rw = h * (0.06 + 0.03 * r.random()) * (1.3 - (t - 0.4))
            d.ellipse([(cx - rw) * s, (cy - rw * 0.32) * s, (cx + rw) * s, (cy + rw * 0.18) * s], fill=150)
            for n in range(26):
                a = math.pi * (0.02 + 0.96 * r.random())
                ln = rw * (0.6 + 0.5 * r.random())
                d.line([(cx * s, (cy - rw * 0.15) * s), ((cx + math.cos(a) * ln) * s, (cy - rw * 0.15 + math.sin(a) * ln * 0.4) * s)], fill=int(190 + r.random() * 65), width=max(1, int(s * 1.3)))


def boat(d, x, y, sz, s):
    d.polygon([((x - sz) * s, y * s), ((x + sz) * s, (y - sz * 0.12) * s), ((x + sz * 0.7) * s, (y + sz * 0.22) * s), ((x - sz * 0.7) * s, (y + sz * 0.2) * s)], fill=235)
    d.line([((x - sz * 0.2) * s, y * s), ((x - sz * 0.2) * s, (y - sz * 0.45) * s)], fill=235, width=max(1, int(sz * 0.08 * s)))
    d.polygon([((x - sz * 0.38) * s, (y - sz * 0.45) * s), ((x - sz * 0.02) * s, (y - sz * 0.45) * s), ((x - sz * 0.2) * s, (y - sz * 0.6) * s)], fill=235)
    d.line([((x + sz * 0.6) * s, (y - sz * 0.05) * s), ((x + sz * 1.2) * s, (y + sz * 0.5) * s)], fill=200, width=max(1, int(sz * 0.04 * s)))
    for k in range(4):
        yy = y + sz * (0.35 + k * 0.18)
        d.line([((x - sz * (1.2 + k * 0.4)) * s, yy * s), ((x + sz * (0.4 + k * 0.3)) * s, yy * s)], fill=120, width=max(1, int(s * 1.5)))


def seal(img, r, x, y, sz):
    H, W = img.shape[:2]
    def fn(d, s):
        d.rectangle([x * s, y * s, (x + sz) * s, (y + sz) * s], fill=255)
    m = mask_draw(H, W, fn, 2)
    def cut(d, s):
        for k in range(7):
            if k % 2 == 0:
                xx = x + sz * (0.15 + 0.7 * r.random())
                d.line([(xx * s, (y + sz * 0.15) * s), (xx * s, (y + sz * (0.4 + 0.45 * r.random())) * s)], fill=255, width=int(sz * 0.07 * s))
            else:
                yy = y + sz * (0.15 + 0.7 * r.random())
                d.line([((x + sz * 0.15) * s, yy * s), ((x + sz * (0.4 + 0.45 * r.random())) * s, yy * s)], fill=255, width=int(sz * 0.07 * s))
    c = mask_draw(H, W, cut, 2)
    m = np.clip(m - c, 0, 1) * (0.75 + 0.25 * smooth(0.3, 0.6, vnoise(H, W, 4, r, 2)))
    return over(img, "#B23A2C", m * 0.92)


def inkwash(spec, r, W, H, P):
    D = np.zeros((H, W), np.float32)
    kind = P["kind"]
    extra = []
    if kind == "mountain":
        D = ink_mountain(D, r, W * 0.75, H * 0.5, H * 0.32, W * 0.3, H * 0.09, 0.35)
        D = ink_mountain(D, r, W * 0.48, H * 0.62, H * 0.52, W * 0.22, H * 0.12, 0.9, sharp=1.3)
        D = mist(D, 0.38, 0.6, 0.95)
        D = ink_mountain(D, r, W * 0.15, H * 0.82, H * 0.2, W * 0.25, H * 0.05, 0.7)
        D = mist(D, 0.74, 0.92, 0.9)
        D = ink_mountain(D, r, W * 0.85, H * 1.02, H * 0.18, W * 0.2, H * 0.06, 0.95)
        extra.append(lambda d, s: pine(d, r, W * 0.8, H * 0.86, H * 0.13, -0.15, s))
        extra.append(lambda d, s: pine(d, r, W * 0.88, H * 0.88, H * 0.1, 0.1, s))
        sealpos = (W * 0.1, H * 0.06, W * 0.07)
    elif kind == "river":
        D = ink_mountain(D, r, W * 0.7, H * 0.42, H * 0.25, W * 0.18, H * 0.08, 0.3)
        D = ink_mountain(D, r, W * 0.3, H * 0.45, H * 0.2, W * 0.15, H * 0.07, 0.3)
        D = mist(D, 0.3, 0.6, 0.85)
        for i, (cx, side) in enumerate([(0.08, 1), (0.28, -1), (0.5, 1), (0.72, -1), (0.92, 1)]):
            base = H * (0.62 if side > 0 else 0.98)
            D = ink_mountain(D, r, W * cx, base, H * (0.28 if side > 0 else 0.38), W * 0.09, H * 0.08, 0.85, sharp=1.8)
            D = mist(D, 0.7, 0.85, 0.5)
        extra.append(lambda d, s: boat(d, W * 0.4, H * 0.72, W * 0.018, s))
        extra.append(lambda d, s: boat(d, W * 0.83, H * 0.64, W * 0.012, s))
        extra.append(lambda d, s: pine(d, r, W * 0.1, H * 0.62, H * 0.2, 0.1, s))
        extra.append(lambda d, s: pine(d, r, W * 0.52, H * 0.6, H * 0.16, -0.1, s))
        sealpos = (W * 0.955, H * 0.08, W * 0.025)
    elif kind == "pines":
        D = ink_mountain(D, r, W * 0.8, H * 0.55, H * 0.22, W * 0.25, H * 0.06, 0.25)
        D = mist(D, 0.4, 0.75, 0.9)
        D = ink_mountain(D, r, W * 0.1, H * 1.05, H * 0.36, W * 0.55, H * 0.08, 0.95, sharp=2.5)
        extra.append(lambda d, s: pine(d, r, W * 0.32, H * 0.72, H * 0.42, 0.28, s))
        extra.append(lambda d, s: pine(d, r, W * 0.42, H * 0.74, H * 0.34, 0.05, s))
        sealpos = (W * 0.8, H * 0.86, W * 0.08)
    else:
        D = ink_mountain(D, r, W * 0.3, H * 0.38, H * 0.12, W * 0.3, H * 0.04, 0.3)
        D = ink_mountain(D, r, W * 0.75, H * 0.4, H * 0.09, W * 0.25, H * 0.04, 0.25)
        D = mist(D, 0.3, 0.45, 0.6)
        D = ink_mountain(D, r, W * 0.0, H * 1.05, H * 0.3, W * 0.22, H * 0.06, 0.95, sharp=1.4)
        extra.append(lambda d, s: boat(d, W * 0.6, H * 0.6, W * 0.04, s))
        def reeds(d, s):
            for k in range(26):
                x = W * (0.02 + r.random() * 0.2)
                h = H * (0.1 + r.random() * 0.12)
                d.line([(x * s, H * s), ((x + (r.random() - 0.3) * W * 0.03) * s, (H - h) * s)], fill=210, width=max(1, int(1.6 * s)))
        extra.append(reeds)
        sealpos = (W * 0.9, H * 0.08, W * 0.04)
    if extra:
        def fn(d, s):
            for e in extra:
                e(d, s)
        D = np.maximum(D, mask_draw(H, W, fn, 2) * 0.95)
    D = blur(warp(D, r, 1.5, 12), 0.9)
    D = np.clip(D, 0, 1)
    img = fill(H, W, "#F3EEE2") * paper_tex(H, W, r, 0.06)
    ink = hexc("#1F1F24")
    img = img * (1 - D[..., None] * (1 - ink))
    return seal(img, r, *sealpos)


LIGHT = np.array([-0.62, -0.45, 0.64], np.float32)
LIGHT = LIGHT / np.linalg.norm(LIGHT)


PROFILES = {
    "jug": ([0, 0.08, 0.38, 0.62, 0.78, 0.9, 1.0], [0.72, 0.86, 1.0, 0.88, 0.6, 0.58, 0.68]),
    "vase": ([0, 0.08, 0.35, 0.6, 0.8, 0.92, 1.0], [0.55, 0.72, 1.0, 0.8, 0.36, 0.34, 0.44]),
    "bowl": ([0, 0.15, 0.5, 1.0], [0.52, 0.7, 0.9, 1.0]),
    "cup": ([0, 0.5, 1.0], [0.82, 0.9, 1.0]),
    "pear": ([0, 0.05, 0.25, 0.42, 0.6, 0.78, 0.92, 1.0], [0.05, 0.72, 1.0, 0.9, 0.58, 0.44, 0.32, 0.06]),
}


def profile(kind, t):
    from scipy.interpolate import PchipInterpolator
    xs, ys = PROFILES[kind]
    return np.clip(PchipInterpolator(xs, ys)(np.clip(t, 0, 1)), 0.01, None)


def lathe(img, dep, o, r, W, H):
    kind, cx, base, R, hh, col = o["kind"], o["x"] * W, o["y"] * H, o["r"] * W, o["h"] * H, hexc(o["c"])
    e = o.get("e", 0.2)
    steps = int(hh) + 1
    T = np.full((H, W), -1.0, np.float32)
    x0, x1 = int(max(0, cx - R * 1.4)), int(min(W, cx + R * 1.4))
    y0, y1 = int(max(0, base - hh - R * e - 2)), int(min(H, base + R * e + 2))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    sub = T[y0:y1, x0:x1]
    for i in range(steps):
        t = i / max(1, steps - 1)
        rr = float(profile(kind, np.array([t]))[0]) * R
        cy = base - t * hh
        m = ((xx - cx) / max(rr, 1e-3)) ** 2 + ((yy - cy) / max(rr * e, 1e-3)) ** 2 <= 1
        if kind != "pear" and i < steps - 1:
            m &= yy >= cy
        sub[m] = t
    mask = sub >= 0
    if not mask.any():
        return img, dep
    tt = np.clip(sub, 0, 1)
    rr = profile(kind, tt) * R
    nx = np.clip((xx - cx) / np.maximum(rr, 1e-3), -1, 1)
    nz = np.sqrt(np.clip(1 - nx ** 2, 0, 1))
    ny = np.zeros_like(nx) - 0.15
    if kind == "pear":
        ny = np.clip((tt - 0.4) * 0.8, -0.4, 0.5) * -1
    dif = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    amb = o.get("amb", 0.32)
    shade = amb + (1 - amb) * dif
    rim = np.clip(nx, 0, 1) ** 3 * 0.18
    c = col * shade[..., None] + rim[..., None] * hexc(o.get("rimc", "#C8B89A"))
    spec = np.exp(-((nx + 0.42) / 0.09) ** 2) * smooth(0.25, 0.45, tt) * (1 - smooth(0.7, 0.9, tt)) * o.get("gloss", 0.55)
    c = c + spec[..., None] * (1 - c) * 0.9
    if kind in ("jug", "vase", "bowl", "cup"):
        rt = float(profile(kind, np.array([1.0]))[0]) * R * 0.9
        cy = base - hh
        inner = ((xx - cx) / rt) ** 2 + ((yy - cy) / (rt * e)) ** 2 <= 1
        g = np.clip((yy - (cy - rt * e)) / (2 * rt * e + 1e-3), 0, 1)
        c[inner] = (col * (0.28 + 0.35 * g[..., None]))[inner]
        mask = mask | inner
    region = img[y0:y1, x0:x1]
    region[mask] = c[mask]
    img[y0:y1, x0:x1] = region
    return img, dep


def fruit(img, o, r, W, H):
    cx, cy, rx, ry, col = o["x"] * W, o["y"] * H, o["r"] * W, o["r"] * W * o.get("ry", 1.0), hexc(o["c"])
    x0, x1 = int(max(0, cx - rx * 1.3)), int(min(W, cx + rx * 1.3))
    y0, y1 = int(max(0, cy - ry * 1.3)), int(min(H, cy + ry * 1.3))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    nx, ny = (xx - cx) / rx, (yy - cy) / ry
    p = o.get("p", 2.0)
    d = np.abs(nx) ** p + np.abs(ny) ** 2
    mask = d <= 1
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    dif = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    amb = 0.3
    c = col * (amb + (1 - amb) * dif)[..., None]
    spec = np.exp(-(((nx + 0.38) / 0.16) ** 2 + ((ny + 0.36) / 0.16) ** 2)) * o.get("gloss", 0.35)
    c = c + spec[..., None] * (1 - c)
    pit = smooth(0.4, 0.75, vnoise(y1 - y0, x1 - x0, 3, r, 1)) * 0.06
    c *= (1 - pit)[..., None]
    region = img[y0:y1, x0:x1]
    region[mask] = c[mask]
    img[y0:y1, x0:x1] = region
    if o.get("stem"):
        def fn(dd, s):
            dd.line([(cx * s, (cy - ry * 0.95) * s), ((cx + rx * 0.15) * s, (cy - ry * 1.25) * s)], fill=255, width=int(rx * 0.08 * s))
        m = mask_draw(H, W, fn, 2)
        img = over(img, "#4A3A22", m)
    return img


def shadow(img, o, W, H):
    cx, base, R = o["x"] * W, o["y"] * H, o["r"] * W
    if o["kind"] in ("lemon", "orange", "pear"):
        base = base + (o["r"] * W * o.get("ry", 1.0) if o["kind"] != "pear" else 0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = ((xx - cx - R * 0.75) / (R * 1.5)) ** 2 + ((yy - base) / (R * 0.28)) ** 2
    m = blur((d <= 1).astype(np.float32), R * 0.12 + 2)
    c = ((xx - cx) / (R * 1.05)) ** 2 + ((yy - base) / (R * 0.12)) ** 2
    m2 = blur((c <= 1).astype(np.float32), 3)
    return img * (1 - (m * 0.42 + m2 * 0.3)[..., None])


def stilllife(spec, r, W, H, P):
    ty = P["table"] * H
    img = vgrad(H, W, P["wall0"], P["wall1"])
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    img *= 1.08 - 0.16 * xx
    img *= (1 + (vnoise(H, W, 90, r, 4) - 0.5) * 0.12)[..., None]
    yy = np.arange(H, dtype=np.float32)[:, None]
    top = smooth(ty - 1, ty + 1, yy)
    fy = P.get("front", 0.9) * H
    tab = vgrad(H, W, mix(P["tablec"], "#FFFFFF", 0.08), P["tablec"])
    tab *= (1 + (aniso(H, W, 120, r, 3, 8) - 0.5) * 0.14)[..., None]
    img = img * (1 - top[..., None]) + tab * top[..., None]
    if "cloth" in P:
        cx0, cx1 = P["cloth"]
        cl = np.zeros((H, W), np.float32)
        poly = [(cx0 * W, ty + 4), (cx1 * W, ty + 4), ((cx1 + 0.04) * W, H), ((cx0 - 0.03) * W, H)]
        def fn(d, s):
            d.polygon([(x * s, y * s) for x, y in poly], fill=255)
        cl = mask_draw(H, W, fn, 2)
        folds = 0.86 + 0.14 * np.sin(np.linspace(0, 1, W)[None, :] * 26 + noise1(W, 80, r)[None, :] * 4) * smooth(fy - 40, fy + 40, yy)
        cc = fill(H, W, P["clothc"]) * folds[..., None] * (1 + (vnoise(H, W, 40, r, 3) - 0.5) * 0.08)[..., None]
        img = img * (1 - cl[..., None]) + cc * cl[..., None]
    front = smooth(fy - 1, fy + 1, yy)
    img = img * (1 - front[..., None] * 0.38)
    objs = sorted(P["objs"], key=lambda o: o["y"])
    for o in objs:
        img = shadow(img, o, W, H)
    dep = None
    for o in objs:
        if o["kind"] in ("lemon", "orange"):
            img = fruit(img, o, r, W, H)
        else:
            img, dep = lathe(img, dep, o, r, W, H)
            if o["kind"] == "jug":
                cx, base, R, hh = o["x"] * W, o["y"] * H, o["r"] * W, o["h"] * H
                def handle(d, s):
                    pts = [(cx + R * (0.62 + 0.45 * math.sin(a)), base - hh * (0.45 + 0.4 * (1 - math.cos(a)) / 2 + 0.12 * math.sin(a * 0.5))) for a in np.linspace(0, math.pi, 30)]
                    d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(R * 0.16 * s), joint="curve")
                m = mask_draw(H, W, handle, 2)
                img = over(img, hexc(o["c"]) * 0.62, m)
                def spout(d, s):
                    d.polygon([((cx - R * 0.6) * s, (base - hh * 0.98) * s), ((cx - R * 0.95) * s, (base - hh * 1.06) * s), ((cx - R * 0.55) * s, (base - hh * 0.9) * s)], fill=255)
                img = over(img, hexc(o["c"]) * 0.8, mask_draw(H, W, spout, 2))
            if o["kind"] == "cup":
                cx, base, R, hh = o["x"] * W, o["y"] * H, o["r"] * W, o["h"] * H
                def chandle(d, s):
                    d.ellipse([(cx + R * 0.7) * s, (base - hh * 0.75) * s, (cx + R * 1.35) * s, (base - hh * 0.2) * s], outline=255, width=int(R * 0.14 * s))
                img = over(img, hexc(o["c"]) * 0.7, mask_draw(H, W, chandle, 2))
            if o["kind"] == "pear":
                cx, base, R, hh = o["x"] * W, o["y"] * H, o["r"] * W, o["h"] * H
                def pstem(d, s):
                    d.line([(cx * s, (base - hh * 0.98) * s), ((cx + R * 0.2) * s, (base - hh * 1.18) * s)], fill=255, width=max(2, int(R * 0.07 * s)))
                img = over(img, "#4A3A22", mask_draw(H, W, pstem, 2))
    img = np.stack([ndi.median_filter(img[..., c], size=5) for c in range(3)], -1)
    img = brushify(img, r, amp=3.2, cell=14, length=13, axis=1, strength=0.1)
    img = brushify(img, r, amp=1.5, cell=8, length=9, axis=0, strength=0.05)
    return img * canvas_tex(H, W, r, 0.03)


def geometric(spec, r, W, H, P):
    ss = 2
    w, h = W * ss, H * ss
    pal = [rgb(c) for c in P["pal"]]
    im = Image.new("RGB", (w, h), rgb(P["bg"]))
    d = ImageDraw.Draw(im)
    kind = P["kind"]
    if kind in ("grid", "moons", "market"):
        cols, rows = P["grid"]
        mg = int(min(w, h) * 0.05)
        cw, rh = (w - 2 * mg) / cols, (h - 2 * mg) / rows
        k = 0
        for j in range(rows):
            for i in range(cols):
                x0, y0 = mg + i * cw, mg + j * rh
                x1, y1 = x0 + cw, y0 + rh
                bg = pal[int(r.integers(0, len(pal)))]
                fg = pal[int(r.integers(0, len(pal)))]
                while fg == bg:
                    fg = pal[int(r.integers(0, len(pal)))]
                d.rectangle([x0, y0, x1, y1], fill=bg)
                if kind == "moons":
                    rot_ = (i + j) % 4
                    d.pieslice([x0, y0 - (rh if rot_ == 0 else 0), x1, y1 + (rh if rot_ == 2 else 0)] if rot_ in (0, 2) else [x0 - (cw if rot_ == 3 else 0), y0, x1 + (cw if rot_ == 1 else 0), y1], [0, 90, 180, 270][rot_], [180, 270, 360, 450][rot_], fill=fg)
                    continue
                if kind == "market":
                    if (i + j) % 2 == 0:
                        n = 6
                        for s_ in range(n):
                            if s_ % 2 == 0:
                                d.rectangle([x0 + s_ * cw / n, y0, x0 + (s_ + 1) * cw / n, y1], fill=fg)
                        for s_ in range(4):
                            cx = x0 + (s_ + 0.5) * cw / 4
                            d.pieslice([cx - cw / 8, y1 - cw / 8, cx + cw / 8, y1 + cw / 8], 180, 360, fill=pal[(k + 2) % len(pal)])
                    else:
                        d.polygon([(x0, y1), ((x0 + x1) / 2, y0 + rh * 0.15), (x1, y1)], fill=fg)
                        d.ellipse([(x0 + x1) / 2 - cw * 0.12, y0 + rh * 0.08, (x0 + x1) / 2 + cw * 0.12, y0 + rh * 0.08 + cw * 0.24], fill=pal[(k + 3) % len(pal)])
                    k += 1
                    continue
                t = int(r.integers(0, 6))
                if t == 0:
                    d.ellipse([x0 + cw * 0.08, y0 + rh * 0.08, x1 - cw * 0.08, y1 - rh * 0.08], fill=fg)
                elif t == 1:
                    d.pieslice([x0, y0, x1, y1 + rh], 180, 360, fill=fg)
                elif t == 2:
                    d.pieslice([x0 - cw, y0, x1, y1 + rh], 270, 360, fill=fg)
                elif t == 3:
                    d.ellipse([x0 + cw * 0.08, y0 + rh * 0.08, x1 - cw * 0.08, y1 - rh * 0.08], fill=fg)
                    d.ellipse([x0 + cw * 0.3, y0 + rh * 0.3, x1 - cw * 0.3, y1 - rh * 0.3], fill=bg)
                elif t == 4:
                    d.rectangle([x0, y0 + rh * 0.38, x1, y1 - rh * 0.38], fill=fg)
                else:
                    d.pieslice([x0, y0 - rh, x1 + cw, y1], 90, 180, fill=fg)
    else:
        for k in range(14):
            c = pal[k % len(pal)]
            th = int(min(w, h) * (0.03 + r.random() * 0.06))
            if k % 2 == 0:
                y = int(h * (0.08 + r.random() * 0.84))
                a, b = sorted([r.random(), r.random()])
                d.rectangle([int(w * a * 0.6), y, int(w * (0.4 + b * 0.6)), y + th], fill=c)
            else:
                x = int(w * (0.08 + r.random() * 0.84))
                a, b = sorted([r.random(), r.random()])
                d.rectangle([x, int(h * a * 0.6), x + th, int(h * (0.4 + b * 0.6))], fill=c)
        for k in range(3):
            cx, cy, cr = w * r.random(), h * r.random(), min(w, h) * (0.06 + r.random() * 0.06)
            d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=pal[(k + 2) % len(pal)])
    im = im.resize((W, H), Image.LANCZOS)
    a = from_img(im)
    a *= (1 + (vnoise(H, W, 70, r, 3) - 0.5) * 0.06)[..., None]
    a = brushify(a, r, amp=0.8, cell=10, length=9, axis=int(r.integers(0, 2)), strength=0.05)
    return a * canvas_tex(H, W, r, 0.04)


def stroke(layer, r, pts, width, color, load=1.0, bristles=46):
    d = ImageDraw.Draw(layer, "RGBA")
    n = len(pts)
    base = np.array(color, np.float32)
    bw = max(2, int(width / bristles * 2.6))
    for b in range(bristles):
        u = b / (bristles - 1) - 0.5
        jit = base * (0.85 + 0.3 * r.random()) + (r.random(3) - 0.5) * 24
        col = tuple(int(np.clip(v, 0, 255)) for v in jit)
        dry = 0.4 + 0.6 * r.random()
        alpha = int((150 + 100 * r.random()) * load)
        seg = []
        for i in range(n - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy) + 1e-6
            nx, ny = -dy / ln, dx / ln
            t = i / n
            press = min(1.0, 0.75 + t * 6) * (1 - 0.25 * t)
            off = u * width * press
            alive = abs(u) < 0.5 * press + 0.02 and load * (1 - t ** (1.2 + 3 * dry)) > r.random() * 0.4
            if alive:
                seg.append((x0 + nx * off, y0 + ny * off))
            else:
                if len(seg) > 1:
                    d.line(seg, fill=col + (alpha,), width=bw)
                seg = []
        if len(seg) > 1:
            d.line(seg, fill=col + (alpha,), width=bw)


def impasto(a, r, k=2.2):
    L = blur(a.mean(-1), 1.2)
    gx = np.roll(L, -1, 1) - np.roll(L, 1, 1)
    gy = np.roll(L, -1, 0) - np.roll(L, 1, 0)
    rel = (-gx * 0.7 - gy * 0.7) * k
    return np.clip(a * (1 + rel[..., None]), 0, 1)


def path(r, w, h, x0, y0, x1, y1, bulge=0.3, n=80):
    mx, my = (x0 + x1) / 2 + (r.random() - 0.5) * w * bulge, (y0 + y1) / 2 + (r.random() - 0.5) * h * bulge
    return bez((x0, y0), (mx, my), (x1, y1), n)


def gestural(spec, r, W, H, P):
    ss = 2
    w, h = W * ss, H * ss
    layer = Image.new("RGBA", (w, h), rgb(P["bg"]) + (255,))
    pal = [rgb(c) for c in P["pal"]]
    if P.get("kind") == "pull":
        for k in range(16):
            x = w * (k / 16) + (r.random() - 0.5) * w * 0.05
            pts = [(x + math.sin(t * 3 + k) * w * 0.02, -50 + t * (h + 100)) for t in np.linspace(0, 1, 90)]
            stroke(layer, r, pts, w * (0.1 + r.random() * 0.06), pal[k % len(pal)], load=0.9, bristles=60)
    for k in range(P.get("n", 9)):
        c = pal[int(r.integers(0, len(pal)))]
        x0, y0 = w * (0.1 + r.random() * 0.8), h * (0.1 + r.random() * 0.8)
        ang = r.random() * math.pi * 2
        ln = max(w, h) * (0.35 + r.random() * 0.45)
        x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
        stroke(layer, r, path(r, w, h, x0, y0, x1, y1, 0.6), min(w, h) * (0.08 + r.random() * 0.11), c, load=0.8 + r.random() * 0.2, bristles=70)
    if P.get("turn"):
        cx, cy = w * 0.5, h * 0.52
        pts = [(cx + math.cos(a) * w * 0.3 * (1 - 0.25 * a / 5), cy + math.sin(a) * h * 0.24 * (1 - 0.25 * a / 5)) for a in np.linspace(3.6, 8.6, 120)]
        stroke(layer, r, pts, min(w, h) * 0.16, rgb(P["turn"]), load=1.0, bristles=90)
    d = ImageDraw.Draw(layer, "RGBA")
    for k in range(P.get("marks", 8)):
        x0, y0 = r.random() * w, r.random() * h
        pts = path(r, w, h, x0, y0, x0 + (r.random() - 0.5) * w * 0.5, y0 + (r.random() - 0.5) * h * 0.5, 0.4, 30)
        d.line(pts, fill=rgb(P.get("mark", "#1B1B1E")) + (235,), width=int(min(w, h) * 0.008 * (1 + r.random())), joint="curve")
    for k in range(P.get("splat", 3)):
        cx, cy = r.random() * w, r.random() * h
        c = pal[int(r.integers(0, len(pal)))]
        for j in range(60):
            a = r.random() * 2 * math.pi
            dd = abs(r.normal()) * w * 0.05
            cr = ss * (1 + r.random() * 5) * (1.4 - dd / (w * 0.15))
            if cr > 0:
                px, py = cx + math.cos(a) * dd, cy + math.sin(a) * dd
                d.ellipse([px - cr, py - cr, px + cr, py + cr], fill=c + (235,))
    im = layer.convert("RGB").resize((W, H), Image.LANCZOS)
    a = from_img(im)
    a = warp(a, r, 1.5, 8)
    a = impasto(a, r)
    return a * canvas_tex(H, W, r, 0.05)


STYLES = {"colorfield": colorfield, "landscape": landscape, "linosea": linosea, "linowave": linowave, "linocity": linocity, "botanical": botanical, "inkwash": inkwash, "stilllife": stilllife, "geometric": geometric, "gestural": gestural}


def paint(spec, P):
    style, seed, size = spec["style"], spec["seed"], spec["size"]
    W, H = size_of(size)
    r = np.random.default_rng(seed)
    a = STYLES[style](spec, r, W, H, P)
    return to_img(a)
