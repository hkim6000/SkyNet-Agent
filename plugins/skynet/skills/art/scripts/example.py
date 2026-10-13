import os
import sys

from PIL import Image

import paint
import scenes

EXAMPLES = [
    dict(key="field-with-low-sun", style="colorfield", seed=11, size="160 × 120 cm", params={'ground': '#B5532F', 'rects': [((0.1, 0.07, 0.9, 0.36), '#D9A441'), ((0.1, 0.4, 0.9, 0.66), '#D98577'), ((0.1, 0.7, 0.9, 0.93), '#7A1F1C')]}),
    dict(key="morning-over-hollin-water", style="landscape", seed=21, size="100 × 140 cm", params={'sky0': '#8FA6BE', 'sky1': '#F3DCC4', 'layers': ['#B9BCC6', '#9AA2B1', '#75839A', '#52627A'], 'horizon': 0.58, 'top': 0.42, 'water': 0.6, 'sun': (0.66, 0.4, 0.03, '#FFF1DC'), 'haze': '#EAD8C8', 'amp': 0.07, 'watercol': '#8C9DB2', 'cloud': '#F7E6D6'}),
    dict(key="north-pier-high-tide", style="linosea", seed=31, size="50 × 70 cm", params={'light': '#A9CBDA', 'mid': '#3F7FA6', 'dark': '#1B3954', 'lamp': '#F0C24B'}),
    dict(key="swell", style="linowave", seed=32, size="60 × 60 cm", params={'light': '#9FC6D8', 'mid': '#2F6E99', 'dark': '#16304C'}),
    dict(key="late-tram", style="linocity", seed=33, size="70 × 50 cm", params={'night': '#1C2340', 'yellow': '#F2C14E', 'red': '#C8432F', 'mid': '#3A4A72'}),
    dict(key="fern-unfurling", style="botanical", seed=41, size="56 × 38 cm", params={'kind': 'fern', 'green': '#7FA65A', 'green2': '#A8C26E', 'dark': '#4E7A3A'}),
    dict(key="seed-heads", style="botanical", seed=43, size="50 × 50 cm", params={'kind': 'seeds', 'stem': '#9A8A5E', 'head': '#B9A06A', 'brown': '#8A6440'}),
    dict(key="mountain-after-rain", style="inkwash", seed=51, size="135 × 70 cm", params={'kind': 'mountain'}),
    dict(key="blue-jug-with-lemons", style="stilllife", seed=61, size="40 × 55 cm", params={'wall0': '#8E8574', 'wall1': '#B5AA94', 'table': 0.6, 'tablec': '#6B4E36', 'cloth': (0.2, 0.9), 'clothc': '#ECE8DF', 'objs': [{'kind': 'jug', 'x': 0.42, 'y': 0.74, 'r': 0.11, 'h': 0.42, 'c': '#2F4E9A', 'e': 0.18}, {'kind': 'lemon', 'x': 0.63, 'y': 0.78, 'r': 0.06, 'ry': 0.72, 'p': 1.6, 'c': '#E8C33A'}, {'kind': 'lemon', 'x': 0.74, 'y': 0.83, 'r': 0.058, 'ry': 0.72, 'p': 1.6, 'c': '#E3BB2E'}, {'kind': 'lemon', 'x': 0.27, 'y': 0.84, 'r': 0.055, 'ry': 0.75, 'p': 1.6, 'c': '#EAC94A'}]}),
    dict(key="signal-no-4", style="geometric", seed=71, size="120 × 120 cm", params={'kind': 'grid', 'grid': (4, 4), 'bg': '#F0E6D2', 'pal': ['#E4572E', '#F3A712', '#29335C', '#4C9F70', '#F0E6D2', '#E8B4BC']}),
    dict(key="loud-weather", style="gestural", seed=81, size="150 × 200 cm", params={'bg': '#DCE3E8', 'pal': ['#2D5DA8', '#FAFAF5', '#F2C230', '#7FB1D8', '#1F3F7A'], 'n': 16, 'marks': 5, 'mark': '#1B1B1E'}),
]


def main(out):
    os.makedirs(out, exist_ok=True)
    made = []
    for e in EXAMPLES:
        im = paint.paint(dict(style=e["style"], seed=e["seed"], size=e["size"]), e["params"])
        path = os.path.join(out, e["key"] + ".webp")
        im.save(path, "WEBP", quality=84, method=6)
        th = im.copy()
        th.thumbnail((640, 640), Image.LANCZOS)
        th.save(os.path.join(out, e["key"] + "-thumb.webp"), "WEBP", quality=82, method=6)
        made.append((e["key"], im))
        print("painted", e["key"], im.size)
    room = scenes.room_banner([(made[0][1], False), (made[3][1], True), (made[1][1], False)], wall="#E9E1D6", floor="#BFA88C", visitor="#7E3B2B")
    room.save(os.path.join(out, "banner.webp"), "WEBP", quality=82, method=6)
    face = scenes.portrait(dict(bg="#C3D5E2", skin="#F2D2B6", hair="#E0C27A", style="bob", cloth="#1F4F6E", stripes="#F1ECE0"))
    face.save(os.path.join(out, "portrait.webp"), "WEBP", quality=85)
    print("banner and portrait done ->", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "painted")
