import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import paint as Pt


def rgb(c):
    return Pt.rgb(c)


def shade(c, k):
    r_, g, b = rgb(c)
    return (int(r_ * k), int(g * k), int(b * k))


def portrait(p, size=480, seed=1):
    S = 960
    im = Image.new("RGB", (S, S), rgb(p["bg"]))
    d = ImageDraw.Draw(im)
    cx = S // 2
    hair = rgb(p["hair"])
    if p["style"] == "long":
        d.rounded_rectangle([cx - 190, 250, cx + 190, 800], radius=150, fill=hair)
    if p["style"] == "bob":
        d.rounded_rectangle([cx - 175, 230, cx + 175, 590], radius=140, fill=hair)
    d.rounded_rectangle([cx - 330, 690, cx + 330, S + 200], radius=220, fill=rgb(p["cloth"]))
    if p.get("stripes"):
        for y in range(720, S, 46):
            d.line([(cx - 330, y), (cx + 330, y)], fill=rgb(p["stripes"]), width=16)
        d.rounded_rectangle([cx - 330, 690, cx + 330, S + 200], radius=220, outline=rgb(p["bg"]), width=1)
    if p.get("dots"):
        for k, (x, y, c) in enumerate([(cx - 200, 820, "#E4572E"), (cx + 150, 780, "#F2C230"), (cx + 60, 900, "#FAFAF5"), (cx - 90, 760, "#F2C230"), (cx + 240, 880, "#E4572E")]):
            d.ellipse([x - 14 - k * 2, y - 12, x + 14 + k * 2, y + 12], fill=rgb(c))
    d.rounded_rectangle([cx - 62, 560, cx + 62, 730], radius=40, fill=shade(p["skin"], 0.88))
    d.polygon([(cx - 120, 690), (cx, 790), (cx + 120, 690)], fill=shade(p["skin"], 0.88))
    d.ellipse([cx - 150, 250, cx + 150, 640], fill=rgb(p["skin"]))
    d.chord([cx - 150, 250, cx + 150, 640], 300, 60, fill=shade(p["skin"], 0.93))
    d.ellipse([cx - 168, 420, cx - 128, 500], fill=shade(p["skin"], 0.92))
    d.ellipse([cx + 128, 420, cx + 168, 500], fill=shade(p["skin"], 0.85))
    st = p["style"]
    if st in ("long", "bob"):
        d.pieslice([cx - 165, 225, cx + 165, 520], 180, 360, fill=hair)
        d.polygon([(cx - 165, 372), (cx - 40, 300), (cx - 150, 470)], fill=hair)
    elif st == "short":
        d.pieslice([cx - 158, 232, cx + 158, 470], 175, 365, fill=hair)
        d.polygon([(cx - 158, 352), (cx - 150, 420), (cx - 120, 330)], fill=hair)
    elif st == "bun":
        d.ellipse([cx - 80, 160, cx + 80, 300], fill=hair)
        d.pieslice([cx - 158, 238, cx + 158, 480], 180, 360, fill=hair)
    elif st == "crop":
        d.pieslice([cx - 165, 230, cx + 165, 500], 170, 370, fill=hair)
        for k in range(7):
            x = cx - 140 + k * 45
            d.ellipse([x - 40, 240 + (k % 2) * 20, x + 40, 320 + (k % 2) * 20], fill=hair)
    elif st == "fade":
        d.pieslice([cx - 154, 240, cx + 154, 430], 180, 360, fill=hair)
    elif st == "curly":
        for k in range(16):
            a = math.pi + k / 15 * math.pi
            x, y = cx + math.cos(a) * 150, 380 + math.sin(a) * 140
            d.ellipse([x - 60, y - 55, x + 60, y + 55], fill=hair)
        d.ellipse([cx - 120, 230, cx + 120, 340], fill=hair)
    if p.get("beard"):
        d.chord([cx - 140, 380, cx + 140, 650], 10, 170, fill=rgb(p["beard"]))
        d.ellipse([cx - 40, 540, cx + 40, 575], fill=rgb(p["skin"]))
    if p.get("glasses"):
        for x in (cx - 68, cx + 68):
            d.ellipse([x - 48, 418, x + 48, 492], outline=rgb("#2B2622"), width=9)
        d.line([(cx - 20, 450), (cx + 20, 450)], fill=rgb("#2B2622"), width=8)
    im = im.resize((size, size), Image.LANCZOS)
    r = np.random.default_rng(seed)
    a = Pt.from_img(im) * Pt.paper_tex(size, size, r, 0.05)
    return Pt.to_img(a)


def room_banner(works, wall="#E9E1D6", floor="#BFA88C", visitor="#7E3B2B", W=1600, H=760, seed=1):
    r = np.random.default_rng(seed)
    wc = Pt.hexc(wall)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = np.broadcast_to(wc * (0.9 + 0.12 * yy), (H, W, 3)).copy()
    floor_y = int(H * 0.8)
    n = len(works)
    xs = [W * 0.46, W * 0.67, W * 0.88][:n] if n > 2 else [W * 0.56, W * 0.81][:n]
    X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    for x in xs:
        pool = np.exp(-(((X - x) / (W * 0.12)) ** 2 + ((Y - H * 0.1) / (H * 0.55)) ** 2))
        img += pool[..., None] * 0.1
    img = img * Pt.paper_tex(H, W, r, 0.025)
    fl = Pt.hexc(floor)
    fimg = np.broadcast_to(fl * (0.85 + 0.2 * (yy - 0.8) / 0.2), (H, W, 3)).copy()
    fimg *= (1 + (Pt.aniso(H, W, 200, r, 3, 10) - 0.5) * 0.1)[..., None]
    img[floor_y:] = fimg[floor_y:]
    img[floor_y - 10:floor_y] = wc * 0.97
    img[floor_y - 10:floor_y - 8] = wc * 0.8
    im = Pt.to_img(img)
    shadow = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    pieces = []
    for (art, framed), x in zip(works, xs):
        art = art.convert("RGB")
        th = H * (0.4 if art.height >= art.width else 0.3)
        tw = th * art.width / art.height
        if tw > W * 0.16:
            tw = W * 0.16
            th = tw * art.height / art.width
        art = art.resize((int(tw), int(th)), Image.LANCZOS)
        if framed:
            mat = int(th * 0.1)
            fr = Image.new("RGB", (art.width + 2 * mat, art.height + 2 * mat), (246, 244, 238))
            fr.paste(art, (mat, mat))
            outer = Image.new("RGB", (fr.width + 16, fr.height + 16), (34, 30, 28))
            outer.paste(fr, (8, 8))
            art = outer
        x0, y0 = int(x - art.width / 2), int(H * 0.43 - art.height / 2)
        sd.rectangle([x0 + 8, y0 + 14, x0 + art.width + 8, y0 + art.height + 18], fill=150)
        pieces.append((art, x0, y0))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, shadow.point(lambda v: int(v * 0.45)))
    for art, x0, y0 in pieces:
        im.paste(art, (x0, y0))
    d = ImageDraw.Draw(im, "RGBA")
    bx = int(xs[len(xs) // 2])
    d.rectangle([bx - 170, int(H * 0.82), bx + 170, int(H * 0.86)], fill=(52, 44, 38, 255))
    for lx in (bx - 150, bx + 140):
        d.rectangle([lx, int(H * 0.86), lx + 10, int(H * 0.92)], fill=(40, 34, 30, 255))
    d.ellipse([bx - 190, int(H * 0.915), bx + 190, int(H * 0.94)], fill=(0, 0, 0, 40))
    if n > 1:
        person(d, int((xs[0] + xs[1]) / 2), int(H * 0.96), H * 0.5, visitor)
    person(d, int(min(W * 0.97, xs[-1] + W * 0.08)), int(H * 0.98), H * 0.53, "#3A3A3A", coat=True)
    return im


def person(d, x, foot, h, color, coat=False):
    c = rgb(color)
    dark = (40, 36, 34, 255)
    head = h * 0.13
    d.ellipse([x - h * 0.16, foot - 6, x + h * 0.16, foot + 6], fill=(0, 0, 0, 45))
    d.rounded_rectangle([x - h * 0.06, foot - h * 0.45, x - h * 0.012, foot], radius=6, fill=dark)
    d.rounded_rectangle([x + h * 0.012, foot - h * 0.45, x + h * 0.06, foot], radius=6, fill=dark)
    d.rounded_rectangle([x - h * 0.1, foot - h * (0.86 if not coat else 0.86), x + h * 0.1, foot - h * (0.42 if not coat else 0.3)], radius=int(h * 0.06), fill=c + (255,))
    d.rounded_rectangle([x - h * 0.03, foot - h * 0.9, x + h * 0.03, foot - h * 0.84], radius=4, fill=(196, 160, 132, 255))
    d.ellipse([x - head / 2, foot - h * 0.9 - head, x + head / 2, foot - h * 0.9 + head * 0.05], fill=(58, 44, 36, 255))
