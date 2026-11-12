import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import house_specs as S
import houses
import rooms

PAL = {
    "linden": dict(wall="#EEEAE2", floor="#B88E64", view="valley", sofa="#ECE6DA", accent="#6E7F6A", island="#2F3438", cab="#E9E4DA", throw="#6E7F6A"),
    "vantage": dict(wall="#DCD8D2", floor="#6E5948", view="dusk", island="#22262A", cab="#3A3D41", top="#D8D4CE", sofa="#BDB3A6", accent="#B5843F", head="#2C2F33", throw="#B5843F", frame="#1C1D1F", vanity="#2C2F33"),
}


def main(out):
    os.makedirs(out, exist_ok=True)
    made = []
    for key, fn in S.MODELS.items():
        for mode in ("day", "dusk"):
            path = os.path.join(out, key + "-" + mode + ".webp")
            houses.house_scene(fn(mode)).save(path, "WEBP", quality=82, method=6)
            made.append(path)
    rear = os.path.join(out, "linden-rear.webp")
    houses.house_scene(S.rear(S.linden)).save(rear, "WEBP", quality=82, method=6)
    made.append(rear)
    seed = 300
    for key, pal in PAL.items():
        for kind in rooms.ROOMS:
            seed += 7
            path = os.path.join(out, key + "-" + kind + ".webp")
            rooms.room(kind, dict(pal, seed=seed)).save(path, "WEBP", quality=82, method=6)
            made.append(path)
    houses.contact(made, os.path.join(out, "contact.jpg"))
    print(len(made), "images in", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "buildings")
