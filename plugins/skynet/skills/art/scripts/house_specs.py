import copy

W0 = "#26292C"


def linden(mode="day"):
    return dict(seed=11, mode=mode, cx=0.5, scale=1.0, ground=0.7,
                hills=["#A9BAC2", "#8EA39B", "#6E8873"], trees="#56724F",
                masses=[
                    dict(x0=-520, x1=-250, h=118, roof="gable", rh=92, ov=16, mat="board", col="#EFEBE3", rcol="#2E3135", rmat="metal",
                         win=[(0.12, 0.22, 0.42, 0.85, 2, 1), (0.58, 0.22, 0.88, 0.85, 2, 1)], frame=W0, lights=[(0.5, 0.2)]),
                    dict(x0=-262, x1=150, h=150, roof="gable", rh=158, ov=18, mat="board", col="#F2EEE6", rcol="#2E3135", rmat="metal",
                         win=[(0.06, 0.12, 0.33, 0.96, 2, 2), (0.67, 0.12, 0.94, 0.96, 2, 2), (0.4, -0.55, 0.6, -0.12, 1, 1)], door=[(0.4, 0.6, 118)], frame=W0, doorcol="#8A5E3B", lights=[(0.36, 0.25), (0.64, 0.25)]),
                    dict(x0=150, x1=540, h=112, roof="gable", rh=84, ov=14, mat="board", col="#EAE6DD", rcol="#2E3135", rmat="metal", back=True,
                         garage=(0.08, 0.46, 86), win=[(0.6, 0.2, 0.9, 0.78, 3, 1)], frame=W0, gcol="#8A5E3B"),
                ],
                path=(-60, 60), nshrubs=10, flowers="#F3E7D2", fronttrees=[(0.06, 0.98, 330), (0.95, 1.0, 300)])


def calder(mode="day"):
    return dict(seed=23, mode=mode, cx=0.5, ground=0.72,
                hills=["#B4C1C7", "#93A6A2", "#738C7A"], trees="#4E6A4B",
                masses=[
                    dict(x0=-640, x1=-330, h=128, roof="flat", ov=20, mat="cedar", col="#9C6E48", rcol="#2B2D30", back=True, garage=(0.1, 0.9, 92), frame=W0, gcol="#4A4C4F"),
                    dict(x0=-360, x1=260, h=150, roof="flat", ov=24, mat="stucco", col="#EDEBE6", rcol="#2B2D30",
                         win=[(0.05, 0.14, 0.45, 0.96, 4, 1), (0.6, 0.14, 0.95, 0.96, 3, 1)], door=[(0.48, 0.57, 124)], doorcol="#3B3F43", frame=W0),
                    dict(x0=-260, x1=560, h=140, lift=150, roof="flat", ov=36, mat="cedar", col="#A3734B", rcol="#2B2D30",
                         win=[(0.06, 0.2, 0.55, 0.82, 5, 1), (0.66, 0.2, 0.94, 0.82, 2, 1)], frame=W0),
                ],
                path=(-60, 40), nshrubs=7, shrub="#5B7A4C", fronttrees=[(0.92, 0.98, 360)])


def marlowe(mode="day"):
    return dict(seed=37, mode=mode, cx=0.5, ground=0.74, water=True,
                hills=["#B9C6CC", "#A3B4B4"], hillh=90, hilla=30, trees="#5C7656", ntrees=10,
                lawn0="#8DA46A", lawn1="#5D7744",
                masses=[
                    dict(x0=-580, x1=-280, h=160, roof="gable", rh=110, ov=12, mat="shingle", col="#97A3A8", rcol="#4C5258", rmat="shingle",
                         win=[(0.12, 0.2, 0.4, 0.8, 2, 2), (0.6, 0.2, 0.88, 0.8, 2, 2)], frame="#F3F0EA"),
                    dict(x0=-290, x1=300, h=250, roof="gable", rh=180, ov=16, mat="shingle", col="#A0ACB0", rcol="#4C5258", rmat="shingle",
                         win=[(0.08, 0.1, 0.3, 0.42, 2, 2), (0.7, 0.1, 0.92, 0.42, 2, 2), (0.08, 0.56, 0.3, 0.92, 2, 2), (0.7, 0.56, 0.92, 0.92, 2, 2), (0.42, -0.5, 0.58, -0.15, 1, 2)],
                         door=[(0.42, 0.58, 120)], doorcol="#2F4A5E", frame="#F3F0EA", lights=[(0.38, 0.6), (0.62, 0.6)]),
                    dict(x0=290, x1=600, h=150, roof="hip", rh=90, ov=12, mat="shingle", col="#97A3A8", rcol="#4C5258", rmat="shingle", back=True,
                         garage=(0.12, 0.88, 92), frame="#F3F0EA", gcol="#E9E5DC"),
                ],
                path=(-55, 55), pathcol="#D8D0C0", nshrubs=12, shrub="#62824F", flowers="#E9D6E4")


def ashcombe(mode="day"):
    return dict(seed=41, mode=mode, cx=0.5, ground=0.74, scale=0.96,
                hills=["#AEBCC0", "#8EA196", "#6F876C"], trees="#46623F", treekind="round", ntrees=18,
                masses=[
                    dict(x0=-640, x1=-300, h=210, roof="hip", rh=120, ov=12, mat="stone", col="#CBBEA6", rcol="#4D545B", rmat="slate", ts=1.0,
                         win=[(0.1, 0.15, 0.28, 0.45, 2, 3), (0.42, 0.15, 0.6, 0.45, 2, 3), (0.74, 0.15, 0.92, 0.45, 2, 3), (0.1, 0.58, 0.28, 0.92, 2, 3), (0.42, 0.58, 0.6, 0.92, 2, 3), (0.74, 0.58, 0.92, 0.92, 2, 3)],
                         frame="#2C3033", chim=[(0.2, 34, 70)]),
                    dict(x0=300, x1=640, h=210, roof="hip", rh=120, ov=12, mat="stone", col="#CBBEA6", rcol="#4D545B", rmat="slate",
                         win=[(0.1, 0.15, 0.28, 0.45, 2, 3), (0.42, 0.15, 0.6, 0.45, 2, 3), (0.74, 0.15, 0.92, 0.45, 2, 3), (0.1, 0.58, 0.28, 0.92, 2, 3), (0.42, 0.58, 0.6, 0.92, 2, 3), (0.74, 0.58, 0.92, 0.92, 2, 3)],
                         frame="#2C3033", chim=[(0.7, 34, 70)]),
                    dict(x0=-310, x1=310, h=260, roof="hip", rh=160, ov=14, mat="stone", col="#D2C5AD", rcol="#4D545B", rmat="slate", inset=210,
                         win=[(0.06, 0.12, 0.18, 0.42, 2, 3), (0.24, 0.12, 0.36, 0.42, 2, 3), (0.64, 0.12, 0.76, 0.42, 2, 3), (0.82, 0.12, 0.94, 0.42, 2, 3), (0.06, 0.56, 0.18, 0.94, 2, 3), (0.24, 0.56, 0.36, 0.94, 2, 3), (0.64, 0.56, 0.76, 0.94, 2, 3), (0.82, 0.56, 0.94, 0.94, 2, 3)],
                         frame="#2C3033"),
                    dict(x0=-95, x1=95, h=290, roof="gable", rh=130, ov=10, mat="stone", col="#DACDB4", rcol="#4D545B", rmat="slate",
                         win=[(0.25, 0.12, 0.75, 0.42, 3, 3)], door=[(0.28, 0.72, 140)], doorcol="#3A2C22", frame="#2C3033", lights=[(0.16, 0.6), (0.84, 0.6)]),
                ],
                path=(-70, 70), pathcol="#D6CCB8", nshrubs=12, shrub="#4E6B42",
                fronttrees=[(0.04, 1.0, 380, "cypress"), (0.97, 1.0, 380, "cypress")])


def vantage(mode="dusk"):
    dusk = mode == "dusk"
    sky = dict(sky0="#2F3B5A", sky1="#F0B486", hills=["#6E7690", "#58617A", "#3F4A5A"], lawn0="#5C6E50", lawn1="#34442F") if dusk else dict(hills=["#A9BAC2", "#8EA39B", "#6E8873"], lawn0="#7FA05F", lawn1="#55773F")
    return dict(seed=53, mode=mode, cx=0.5, ground=0.7, hillh=180, hilla=80,
                trees="#2F4536", treekind="pine", ntrees=22, **sky,
                masses=[
                    dict(x0=-600, x1=180, h=150, roof="flat", ov=30, mat="stucco", col="#4A4E52", rcol="#1F2123",
                         win=[(0.04, 0.08, 0.96, 0.98, 8, 1)], frame="#1C1D1F"),
                    dict(x0=-260, x1=600, h=150, lift=150, roof="flat", ov=46, mat="cedar", col="#86613F", rcol="#1F2123",
                         win=[(0.05, 0.1, 0.62, 0.95, 6, 1), (0.72, 0.1, 0.95, 0.95, 2, 1)], frame="#1C1D1F"),
                ],
                pool=(0.08, 0.62, 0.78, 0.86), plinth="#8E8A82", nshrubs=6, shrub="#3E5638")


MODELS = {"linden": linden, "calder": calder, "marlowe": marlowe, "ashcombe": ashcombe, "vantage": vantage}


def rear(fn, seed_add=100):
    s = fn("dusk" if fn is not vantage else "day")
    s = copy.deepcopy(s)
    s["seed"] += seed_add
    for m in s["masses"]:
        x0, x1 = -m["x1"], -m["x0"]
        m["x0"], m["x1"] = x0, x1
        m.pop("garage", None)
        m.pop("door", None)
        wins = [(1 - w[2], w[1], 1 - w[0], w[3]) + tuple(w[4:]) for w in m.get("win", [])]
        m["win"] = wins
    if "pool" not in s:
        s["pool"] = (0.24, 0.76, 0.8, 0.93)
    s["path"] = None
    s["hedge"] = None
    s["fronttrees"] = []
    return s
