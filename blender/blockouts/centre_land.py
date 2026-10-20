"""The centre's land, designed by hand: the water's outline, contour lines, spot heights and landforms.

Pure Python with numpy (Blender ships numpy), so the plan map and the clay block-in use the same ground.
The land is drawn the way a designer draws it: the shorelines, a few contour lines and spot heights, with
smooth ground between them (inverse-distance weighting), then outcrops of bedrock, the stream gullies and
the water on top. The shape is set out in docs/town-plan.md (The land; The centre in detail): a harbour bay
reaching into the town in three inlets (Vågen, the east harbour, the west cove) between three fingers of
land (Holmen and the knoll, the old town's hill, Storhaug), islands in the bay, the square at Vågen's head
with the cathedral and the lake behind, the fire grid's slope and the forest hill inland.

Street coordinates in metres, as everywhere in LT1: x towards Vågen's head (about south), y up the old
town's slope (about east), z up. On a map with north up, +y is to the right and +x is down. The beauty
corner's landing is at about (47, 38), on Vågen's east shore.
"""

import math

import numpy as np

# -- the water -------------------------------------------------------------------------------------------------
# One coastline, traced from the west along the bay's south shore, into the west cove, up the sund's east bank,
# along Vågen's west quay to its head and back along Harbour Row, round the old town's point, into the east
# harbour and out along Storhaug's shore. Each point says what the shore is from it to the next: "q" a quay
# (built, straight), "n" natural (rock and shingle, irregular). The water is the bay side of the line; the
# map's far edge closes it. Holmen is an island: Vågen's west quay on one side, the sund on another.

COAST = [
    (-380, -1400, "n"), (-340, -1150, "n"), (-360, -1000, "q"), (-330, -780, "n"), (-372, -700, "n"),
    (-318, -640, "n"), (-300, -570, "n"),
    # the west cove, a broad round bay: boatyards and slips on its west shore, a sandy beach at its head
    # facing north-west up the cove, for the summer evening sun
    (-240, -660, "n"), (-150, -722, "n"), (-40, -724, "n"), (40, -684, "n"), (80, -620, "b"), (104, -520, "b"),
    (96, -430, "n"), (70, -360, "n"), (54, -300, "q"),
    # the sund's east bank, then Vågen's west quay to the head, the head, and Harbour Row back to the point
    (54, -150, "q"), (150, -140, "q"), (250, -124, "q"), (302, -112, "q"), (302, -62, "q"), (270, -40, "q"),
    (220, -24, "q"), (150, -15, "q"),
    # the old town's point: rock round its tip below the bluff
    (-250, -15, "n"), (-280, 10, "n"), (-322, 60, "n"), (-348, 120, "n"), (-342, 190, "n"), (-312, 260, "n"),
    (-292, 330, "n"), (-262, 390, "n"),
    # the east harbour, opening north-east: the cannery's quays along the old town hill's east side, a shingle
    # beach where the stream comes in at its head, slips on Storhaug's side, Storhaug's point far out to the north-east
    (-210, 430, "q"), (-120, 452, "q"), (-20, 470, "n"), (60, 500, "n"), (100, 560, "n"), (90, 640, "n"),
    (30, 700, "n"), (-60, 760, "n"), (-160, 830, "n"), (-260, 900, "n"), (-380, 960, "n"), (-470, 1030, "n"),
    (-520, 1120, "n"), (-470, 1220, "n"), (-420, 1400, "m"),
    (-1400, 1400, "m"), (-1400, -1400, "m"),
]
HOLMEN = [
    (-190, -168, "q"), (0, -156, "q"), (40, -150, "q"), (40, -270, "n"), (-60, -276, "n"), (-130, -282, "n"),
    (-190, -280, "n"), (-226, -246, "n"), (-216, -200, "n"),
]
ISLAND_SUBURB = [
    (-560, 160, "n"), (-640, 110, "n"), (-720, 140, "n"), (-820, 150, "n"), (-900, 230, "n"), (-950, 330, "n"),
    (-930, 450, "n"), (-880, 560, "n"), (-780, 610, "n"), (-700, 650, "n"), (-620, 590, "n"), (-600, 560, "q"),
    (-540, 440, "n"), (-530, 330, "n"), (-520, 240, "n"),
]
SMALL_ISLAND = [
    (-560, -460, "n"), (-610, -490, "n"), (-660, -470, "n"), (-700, -410, "n"), (-690, -340, "n"),
    (-640, -300, "n"), (-590, -310, "n"), (-552, -370, "n"),
]
ISLANDS = [(HOLMEN, 8.0), (ISLAND_SUBURB, 26.0), (SMALL_ISLAND, 12.0)]
LAKE = [(420, -122, "n"), (470, -140, "n"), (520, -132, "n"), (570, -116, "n"), (600, -92, "n"), (612, -40, "n"),
        (612, -10, "n"), (590, 18, "n"), (560, 30, "n"), (510, 34, "n"), (470, 26, "n"), (436, 4, "n"), (420, -30, "n")]
LAKE_LEVEL = 5.0
# the mountains far off to the east and south-east, seen over the upland: (compass bearing in degrees from the
# old town's summit, height in metres, distance in metres). Too far for the ground; drawn as the backdrop.
FAR_RANGE = [(60, 380, 22000), (80, 620, 26000), (95, 840, 30000), (110, 760, 28000), (125, 980, 34000),
             (140, 700, 30000), (155, 520, 26000), (170, 420, 24000), (185, 300, 22000)]
BRIDGE = [(-470, 1030), (-640, 620)]  # the high bridge of 1978, from Storhaug's point to the island
BREAKWATER = [(-206, -186), (-270, -160), (-312, -110)]  # from Holmen's tip, sheltering Vågen's mouth, a light at its end
LIGHT = (-312, -110)


def _shore(points, closed=True, amp=9.0, seed=7):
    """A shoreline as a list of (x, y): quays straight, natural shore broken into small points and coves by
    seeded noise along it, the corners kept where they were drawn."""
    out = []
    n = len(points)
    for k in range(n if closed else n - 1):
        x1, y1, kind = points[k]
        x2, y2, _ = points[(k + 1) % n]
        out.append((x1, y1))
        if kind not in ("n", "b"):
            continue
        L = math.hypot(x2 - x1, y2 - y1)
        steps = int(L / 6.0)
        nx, ny = -(y2 - y1) / (L or 1), (x2 - x1) / (L or 1)
        for i in range(1, steps):
            t = i / steps
            s = (k * 1000.0 + t * L) / 1.0
            w = math.sin(math.pi * t) ** 0.6  # no offset at the drawn corners
            a = amp if kind == "n" else amp * 0.25  # a beach is a smooth curve of sand
            off = a * w * (_n1(s / 45.0, seed) * 0.7 + _n1(s / 11.0, seed + 1) * 0.3 - 0.5) * 2.0
            out.append((x1 + (x2 - x1) * t + nx * off, y1 + (y2 - y1) * t + ny * off))
    return out


def _n1(u, seed):
    i = math.floor(u)
    f = u - i
    f = f * f * (3 - 2 * f)

    def h(k):
        v = (k * 374761393 + seed * 668265263) & 0xFFFFFFFF
        v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
        return (v & 0xFFFF) / 65535.0
    return h(i) + (h(i + 1) - h(i)) * f


COAST_LINE = _shore(COAST)
ISLAND_LINES = [(_shore(p, seed=11 + i), top) for i, (p, top) in enumerate(ISLANDS)]
LAKE_LINE = _shore(LAKE, amp=4.0, seed=31)
WATER = [COAST_LINE]

# -- the shape of the land: contour lines and spot heights -------------------------------------------------------

CONTOURS = [
    # the old town's hill, between Vågen and the east harbour: its spine, its sides, the bluff at its tip
    (38.0, [(-170, 170), (-60, 200), (60, 214), (180, 200), (240, 190)]),
    (20.0, [(-200, 86), (-60, 92), (60, 96), (180, 90), (250, 70)]),
    (10.0, [(-215, 50), (-60, 52), (60, 54), (190, 46), (260, 30)]),
    (20.0, [(-210, 340), (-80, 370), (20, 400), (80, 440)]),
    (10.0, [(-220, 390), (-90, 420), (10, 444), (70, 470)]),
    (24.0, [(-262, 30), (-300, 70), (-324, 125), (-318, 195), (-290, 262), (-268, 330)]),  # the bluff's top edge
    (3.0, [(-276, 30), (-314, 70), (-338, 125), (-332, 195), (-304, 262), (-282, 330)]),   # its foot: a rock face
    # the saddle from the hill's back to the forest hill
    (30.0, [(240, 260), (300, 340), (360, 420)]),
    # Holmen: low, with a spine
    (8.0, [(-236, -236), (-120, -232), (0, -228), (34, -226)]),
    # the mainland west of the sund: the pub quay's upper street, then the fire grid's slope
    (8.0, [(60, -186), (150, -176), (250, -160), (300, -150)]),
    (12.0, [(90, -300), (200, -300), (330, -280), (500, -260)]),
    (22.0, [(100, -440), (250, -430), (400, -410), (600, -390)]),
    (32.0, [(110, -600), (300, -580), (500, -560), (700, -540)]),
    (40.0, [(0, -780), (300, -760), (700, -720)]),
    # the ridge behind the fire grid: broad, with a spur towards the cove and a notch where a road crosses
    (50.0, [(40, -720), (240, -740), (440, -730), (640, -700), (840, -660)]),
    (64.0, [(100, -860), (300, -900), (420, -890)]),
    (58.0, [(480, -880), (520, -885)]),
    (66.0, [(580, -870), (760, -840), (900, -800)]),
    (40.0, [(-60, -800), (40, -880)]),
    (52.0, [(120, -1060), (400, -1120), (800, -1060)]),
    # west of the cove: the ferry quay's low ground, the oil base, the coast
    (6.0, [(-300, -660), (-150, -660), (0, -660)]),
    (16.0, [(-300, -860), (-100, -860), (100, -860)]),
    # the head: flat made ground round the square, rising gently south past the lake
    (3.5, [(300, -150), (330, -60), (330, 40), (300, 110)]),
    (12.0, [(680, -300), (700, -60), (680, 200)]),
    (24.0, [(880, -300), (900, 0), (880, 300)]),
    # Storhaug, east of the east harbour
    (20.0, [(-340, 1080), (-180, 980), (-20, 880), (120, 800), (220, 760)]),
    # the forest hill, south-east
    # the upland to the south, the skyline seen from the bay behind the near hills: a long ridge with spurs
    # and a pass where the railway goes through
    (60.0, [(1100, -700), (1150, -400), (1180, -200), (1170, 0)]),
    (70.0, [(1200, 300), (1220, 600), (1150, 900), (1000, 1100)]),
    (120.0, [(1500, -1300), (1640, -900), (1700, -500), (1720, -260)]),
    (96.0, [(1680, -120), (1700, 20)]),                   # the pass the railway goes through
    (160.0, [(1760, 160), (1900, 420), (1980, 640), (1940, 900)]),
    (185.0, [(2050, 520), (2080, 600)]),                  # the upland's top
    (140.0, [(1880, 1060), (1760, 1300), (1620, 1600)]),
    (150.0, [(2400, -1400), (2500, -400), (2500, 800), (2300, 1900)]),
    # the forest hill: a ridge with two summits and a saddle, steep on its north-west side over Storhaug
    (82.0, [(360, 770), (420, 830), (470, 880)]),
    (74.0, [(540, 960), (600, 1020)]),
    (66.0, [(500, 920), (520, 940)]),
    (60.0, [(300, 720), (340, 690), (420, 740), (520, 840), (640, 960), (660, 1060), (560, 1060), (440, 960), (330, 860), (290, 790)]),
    (40.0, [(170, 690), (260, 560), (420, 600), (600, 760), (760, 960), (720, 1120), (480, 1140), (300, 1000), (190, 860)]),
    (55.0, [(620, 1020), (720, 1120), (820, 1180)]),   # a spur running on south-east
    (50.0, [(280, 980), (220, 1080)]),                 # a spur towards Storhaug
]
SPOTS = [
    (42.0, (40, 210)),     # the top of the old town's hill, the villas' plateau
    (36.0, (-220, 1120)),  # Storhaug's top
    (46.0, (10, 236)),     # the old town hill's summit: a small park and a viewpoint by the villas
    (36.0, (-200, 170)),   # the bluff's top, where the hundred steps arrive: a second high point
    (31.0, (-100, 190)),   # the saddle between them, where a lane crosses the spine
    (88.0, (440, 860)),    # the forest hill's summit, the water tower
    (16.0, (-200, 1000)),
    (30.0, (300, 1300)), (45.0, (900, 900)), (25.0, (-300, -1150)),

]
OUTCROPS = [
    dict(name="the knoll", x=150.0, y=-330.0, r=60.0, face=14.0, top=30.0, sx=1.0, sy=1.15),
    dict(name="the corner's knuckle", x=59.0, y=39.0, r=7.5, face=1.3, top=12.6, sx=1.0, sy=1.15),
    dict(name="the cathedral's rise", x=380.0, y=-30.0, r=46.0, face=30.0, top=9.0, sx=1.0, sy=1.0),
    dict(name="Holmen's rock tip", x=-246.0, y=-246.0, r=26.0, face=10.0, top=7.0, sx=1.0, sy=1.4),
    dict(name="the beacon islet", x=-370.0, y=-60.0, r=16.0, face=8.0, top=6.0, sx=1.3, sy=1.0),
    dict(name="a skerry", x=-480.0, y=110.0, r=12.0, face=6.0, top=4.0, sx=1.0, sy=1.0),
    dict(name="a skerry", x=-640.0, y=-60.0, r=10.0, face=5.0, top=3.0, sx=1.0, sy=1.0),
    dict(name="a skerry", x=-460.0, y=560.0, r=14.0, face=7.0, top=4.0, sx=1.0, sy=1.0),
]
VALLEYS = [
    # the stream from the forest hill's saddle down to the east harbour's head, in a green valley
    dict(name="the stream valley", depth=9.0, width=26.0, line=[(520, 640), (420, 650), (320, 630), (200, 590), (110, 560)]),
    # the lake's valley, carrying the railway south from the station
    dict(name="the railway's valley", depth=7.0, width=40.0, line=[(600, -40), (760, 0), (920, 80), (1100, 160), (1300, 200)]),
]
RAILWAY = [(560, -150), (620, -60), (760, 0), (920, 80), (1100, 160), (1300, 200)]  # the station by the lake
GULLIES = [  # where the streams come down the old town's west slope to Vågen
    dict(x=49.3, depth=2.0, width=8.0, y0=10.0, y1=170.0),
    dict(x=-110.0, depth=2.6, width=9.0, y0=10.0, y1=170.0),
]


# -- the height function ---------------------------------------------------------------------------------------


def _inside(poly, X, Y):
    c = np.zeros(X.shape, dtype=bool)
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        cond = (y1 > Y) != (y2 > Y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = (x2 - x1) * (Y - y1) / (y2 - y1) + x1
        c ^= cond & (X < xi)
    return c


def _seg_dist(X, Y, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy or 1e-9
    t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0.0, 1.0)
    return np.hypot(X - (x1 + dx * t), Y - (y1 + dy * t))


def _poly_dist(X, Y, poly, closed=True):
    pts = poly + poly[:1] if closed else poly
    d = np.full(X.shape, 1e9)
    for a, b in zip(pts, pts[1:]):
        d = np.minimum(d, _seg_dist(X, Y, a, b))
    return d


def _smoothstep(a, b, v):
    t = np.clip((v - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _noise(X, Y, scale, seed):
    u, v = X / scale, Y / scale
    i, j = np.floor(u), np.floor(v)
    fu, fv = u - i, v - j
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)

    def h(a, b):
        k = (a * 374761393 + b * 668265263 + seed * 2246822519) % 4294967296
        k = (k * 1274126177 + 12345) % 4294967296
        return (k % 1000003) / 1000003.0
    a = h(i, j) + (h(i + 1, j) - h(i, j)) * fu
    b = h(i, j + 1) + (h(i + 1, j + 1) - h(i, j + 1)) * fu
    return a + (b - a) * fv


def water_mask(X, Y):
    w = _inside(COAST_LINE, X, Y)
    for p, _ in ISLAND_LINES:
        w &= ~_inside(p, X, Y)
    return w


def heights(X, Y):
    """The designed ground at arrays of points X, Y (street metres)."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    num = np.zeros(X.shape)
    den = np.zeros(X.shape)

    def add(z, d, p=2.2):
        w = 1.0 / (d ** p + 900.0)  # soft within about 20 m of a line, so lines never pinch into stars
        num[...] += w * z
        den[...] += w

    coast = [p for p in COAST_LINE if abs(p[0]) < 1390 and abs(p[1]) < 1390]  # not the map's far edge
    add(1.6, _poly_dist(X, Y, coast, closed=False))
    add(LAKE_LEVEL + 0.6, _poly_dist(X, Y, LAKE_LINE))
    for poly, top in ISLAND_LINES:
        add(1.6, _poly_dist(X, Y, poly))
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        add(top, np.hypot(X - cx, Y - cy))
    for z, line in CONTOURS:
        add(z, _poly_dist(X, Y, line, closed=False))
    for z, (x, y) in SPOTS:
        add(z, np.hypot(X - x, Y - y))
    Z = num / den

    # streams cut the old town's west slope; seeded unevenness off the quays
    for g in GULLIES:
        k = np.exp(-((X - g["x"]) / g["width"]) ** 2) * _smoothstep(g["y0"], g["y0"] + 25, Y) * (1 - _smoothstep(g["y1"] - 40, g["y1"], Y))
        Z -= g["depth"] * k * (Y > -15)
    for v in VALLEYS:
        d = _poly_dist(X, Y, v["line"], closed=False)
        Z -= v["depth"] * np.exp(-(d / v["width"]) ** 2) * _smoothstep(2.0, 16.0, Z)
    rough = (_noise(X, Y, 60.0, 1989) * 0.65 + _noise(X + 500, Y, 23.0, 1990) * 0.35 - 0.5) * 2.0
    Z += rough * np.clip((Z - 4.0) / 10.0, 0.0, 1.0)

    # the water and the lake first, then bedrock standing up out of land and sea alike
    W = water_mask(X, Y)
    lake = _inside(LAKE_LINE, X, Y)
    Z = np.where(W, -6.0, Z)
    Z = np.where(lake, LAKE_LEVEL - 2.0, Z)
    for o in OUTCROPS:
        d = np.hypot((X - o["x"]) / o["sx"], (Y - o["y"]) / o["sy"])
        k = _smoothstep(o["r"], o["r"] - o["face"], d)
        Z = np.where(d < o["r"], np.maximum(Z, Z + (o["top"] - Z) * k), Z)
    return Z


def is_water(X, Y):
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    return water_mask(X, Y) | _inside(LAKE_LINE, X, Y)


def z_at(x, y):
    return float(heights(np.array([x]), np.array([y]))[0])
