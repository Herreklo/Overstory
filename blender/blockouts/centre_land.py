"""The centre's land, designed by hand: the water's outline, contour lines, spot heights and landforms.

Pure Python with numpy (Blender ships numpy), so the plan map and the clay block-in use the same ground.
The land is drawn the way a designer draws it: the shorelines, a few contour lines and spot heights, with
smooth ground between them (inverse-distance weighting), then outcrops of bedrock, the stream gullies and
the water on top. The shape is set out in docs/town-plan.md (The land; The centre in detail): a harbour bay
reaching into the town in three inlets (the Basin, the east harbour, the west cove) between three fingers of
land (the Holm and the knoll, the old town's hill, Ropewalk), islands in the bay, the square at the Basin's head
with the cathedral and the lake behind, the fire grid's slope and the forest hill inland.

Street coordinates in metres, as everywhere in LT1: x towards the Basin's head (about south), y up the old
town's slope (about east), z up. On a map with north up, +y is to the right and +x is down. The beauty
corner's landing is at about (47, 38), on the Basin's east shore.
"""

import math

import numpy as np

# -- the water -------------------------------------------------------------------------------------------------
# One coastline, traced from the west along the bay's south shore, into the west cove, up the sund's east bank,
# along the Basin's west quay to its head and back along Harbour Row, round the old town's point, into the east
# harbour and out along Ropewalk's shore. Each point says what the shore is from it to the next: "q" a quay
# (built, straight), "n" natural (rock and shingle, irregular). The water is the bay side of the line; the
# map's far edge closes it. the Holm is an island: the Basin's west quay on one side, the sund on another.

COAST = [
    (-380, -1400, "n"), (-340, -1150, "n"), (-360, -1000, "q"), (-330, -780, "n"), (-372, -700, "n"),
    (-318, -640, "n"), (-300, -570, "n"),
    # the west cove, a broad round bay: boatyards and slips on its west shore, a sandy beach at its head
    # facing north-west up the cove, for the summer evening sun
    (-240, -660, "n"), (-150, -722, "n"), (-40, -724, "n"), (40, -684, "n"), (80, -620, "b"), (104, -520, "b"),
    (96, -430, "n"), (70, -360, "n"), (54, -300, "q"),
    # the sund's east bank, then the Basin's west quay to the head, the head, and Harbour Row back to the point
    (54, -150, "q"), (150, -140, "q"), (240, -130, "q"), (300, -124, "q"), (332, -106, "q"), (344, -80, "q"),
    (334, -50, "q"), (300, -32, "q"), (250, -22, "q"), (150, -15, "q"), (-60, -12.4, "q"), (-160, -15.4, "q"),
    # the old town's point: rock round its tip below the bluff
    (-250, -15, "n"), (-280, 10, "n"), (-322, 60, "n"), (-348, 120, "n"), (-342, 190, "n"), (-312, 260, "n"),
    (-292, 330, "n"), (-262, 390, "n"),
    # the east harbour, opening north-east: the cannery's quays along the old town hill's east side, a shingle
    # beach where the stream comes in at its head, slips on Ropewalk's side, Ropewalk's point far out to the north-east
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
LAKE = [(540, -122, "n"), (590, -140, "n"), (640, -132, "n"), (690, -116, "n"), (720, -92, "n"), (732, -40, "n"),
        (732, -10, "n"), (710, 18, "n"), (680, 30, "n"), (630, 34, "n"), (590, 26, "n"), (556, 4, "n"), (540, -30, "n")]
LAKE_LEVEL = 5.0
# the mountains far off to the east and south-east, seen over the upland: (compass bearing in degrees from the
# old town's summit, height in metres, distance in metres). Too far for the ground; drawn as the backdrop.
FAR_RANGE = [(60, 380, 22000), (80, 620, 26000), (95, 840, 30000), (110, 760, 28000), (125, 980, 34000),
             (140, 700, 30000), (155, 520, 26000), (170, 420, 24000), (185, 300, 22000)]
BRIDGE = [(-470, 1030), (-640, 620)]  # the high bridge of 1978, from Ropewalk's point to the island
BREAKWATER = [(-206, -186), (-270, -160), (-312, -110)]  # from the Holm's tip, sheltering the Basin's mouth, a light at its end
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
    # the old town's hill, between the Basin and the east harbour: its spine, its sides, the bluff at its tip
    (38.0, [(-170, 170), (-60, 200), (60, 214), (180, 200), (240, 190)]),
    # its west slope, drawn on the old town's levels: the quay apron, then Low, High, Top and Crest terraces
    (2.2, [(-250, 2), (-160, 0), (-60, 3), (150, 0), (250, -8), (300, -18), (330, -32)]),
    # spurs bulge towards the water (about x -170, -30, 130), hollows run back where the streams come down
    (3.0, [(-232, 16), (-170, 14), (-110, 26), (-60, 19), (-30, 14), (0, 18), (49, 22), (90, 18), (130, 13), (170, 17), (200, 20), (260, 8)]),
    (8.0, [(-226, 34), (-170, 30), (-110, 46), (-60, 37), (-30, 30), (10, 36), (47, 40), (90, 35), (130, 28), (170, 34), (210, 36), (280, 18)]),
    (16.0, [(-214, 70), (-170, 64), (-110, 86), (-60, 76), (-30, 66), (10, 74), (47, 80), (90, 72), (130, 62), (170, 70), (215, 72), (290, 44)]),
    (28.0, [(-196, 124), (-160, 116), (-110, 142), (-60, 132), (-20, 120), (20, 128), (60, 134), (110, 124), (150, 112), (200, 120), (250, 108)]),
    (20.0, [(-210, 340), (-80, 370), (20, 400), (80, 440)]),
    (10.0, [(-220, 390), (-90, 420), (10, 444), (70, 470)]),
    (24.0, [(-262, 30), (-300, 70), (-324, 125), (-318, 195), (-290, 262), (-268, 330)]),  # the bluff's top edge
    (3.0, [(-276, 30), (-314, 70), (-338, 125), (-332, 195), (-304, 262), (-282, 330)]),   # its foot: a rock face
    # the saddle from the hill's back to the forest hill
    (30.0, [(240, 260), (300, 340), (360, 420)]),
    # the Holm: Barrel Quay's apron, then up to its spine, Holm Street
    (2.2, [(-190, -170), (0, -168), (38, -164)]),
    (8.0, [(-236, -236), (-120, -232), (0, -228), (34, -226)]),
    (2.2, [(56, -160), (150, -150), (240, -140), (300, -134), (334, -128)]),  # the mainland's Barrel Quay
    # the mainland west of the sund: the pub quay's upper street, then the fire grid's slope
    (8.0, [(60, -186), (150, -176), (250, -160), (300, -150)]),
    # Watch Knoll: a hill over Holm Street, its summit near the harbour side (the Fire Watch), a ridge falling
    # gently south-west towards the Grid, a rock face on its harbour side
    (None, [(112, -304, 46.0), (150, -338, 40.0), (196, -380, 31.0), (240, -424, 24.0), (276, -470, 20.0)]),
    (30.0, [(88, -312), (104, -336), (140, -372), (184, -410)]),
    (30.0, [(140, -300), (174, -322), (214, -356), (250, -398)]),
    (16.0, [(70, -320), (96, -366), (150, -416), (200, -460)]),
    (12.0, [(200, -300), (330, -280), (500, -260)]),
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
    (3.0, [(350, -170), (380, -80), (370, 20), (330, 110)]),  # the square's ground, open to the head
    (12.0, [(680, -300), (700, -60), (680, 200)]),
    (24.0, [(880, -300), (900, 0), (880, 300)]),
    # Ropewalk, east of the east harbour
    (20.0, [(-340, 1080), (-180, 980), (-20, 880), (120, 800), (220, 760)]),
    # the forest hill, south-east
    # the upland to the south, the skyline seen from the bay behind the near hills: a long ridge with spurs
    # and a pass where the railway goes through
    (50.0, [(1040, -1000), (1100, -500), (1130, 0), (1120, 500), (1060, 1100)]),  # the upland's foot, continuous
    # its crest, one line whose height runs along it: down to the pass the railway goes through, up to its top
    (None, [(1500, -1300, 120), (1640, -900, 126), (1700, -500, 118), (1720, -260, 110), (1700, -60, 96),
            (1720, 60, 102), (1760, 160, 140), (1900, 420, 166), (2050, 560, 185), (1980, 720, 170), (1940, 900, 152),
            (1880, 1060, 142), (1760, 1300, 136), (1620, 1600, 130)]),
    (None, [(1300, -1200, 80), (1360, -700, 86), (1400, -300, 80), (1420, 0, 68), (1440, 300, 84), (1450, 700, 92),
            (1400, 1100, 86), (1300, 1500, 80)]),
    (150.0, [(2400, -1400), (2500, -400), (2500, 800), (2300, 1900)]),
    # the forest hill: a ridge with two summits and a saddle, steep on its north-west side over Ropewalk
    (82.0, [(360, 770), (420, 830), (470, 880)]),
    (74.0, [(540, 960), (600, 1020)]),
    (66.0, [(500, 920), (520, 940)]),
    (62.0, [(330, 700), (260, 640)]),                  # a spur north-west, towards the stream valley
    (64.0, [(520, 860), (600, 800), (680, 790)]),      # a spur east
    (58.0, [(440, 960), (400, 1060), (420, 1160)]),    # a spur south, towards Ropewalk's back
    (60.0, [(620, 1060), (700, 1140), (800, 1180)]),   # the ridge running on south-east, lower
    (40.0, [(200, 620), (300, 560)]), (36.0, [(700, 700), (800, 860)]), (42.0, [(300, 1100), (480, 1200)]),
    (34.0, [(560, 1180), (700, 1260)]),
]
SPOTS = [
    (42.0, (40, 210)),     # the top of the old town's hill, the villas' plateau
    (36.0, (-220, 1120)),  # Ropewalk's top
    (46.0, (10, 236)),     # the old town hill's summit: a small park and a viewpoint by the villas
    (36.0, (-200, 170)),   # the bluff's top, where the hundred steps arrive: a second high point
    (31.0, (-100, 190)),   # the saddle between them, where a lane crosses the spine
    (88.0, (440, 860)),    # the forest hill's summit, the water tower
    (16.0, (-200, 1000)),
    (30.0, (300, 1300)), (45.0, (900, 900)), (25.0, (-300, -1150)),

]
OUTCROPS = [
    dict(name="the Holm's rock tip", x=-246.0, y=-246.0, r=26.0, face=10.0, top=7.0, sx=1.0, sy=1.4),
    dict(name="the beacon islet", x=-370.0, y=-60.0, r=16.0, face=8.0, top=6.0, sx=1.3, sy=1.0),
    dict(name="a skerry", x=-480.0, y=110.0, r=12.0, face=6.0, top=4.0, sx=1.0, sy=1.0),
    dict(name="a skerry", x=-640.0, y=-60.0, r=10.0, face=5.0, top=3.0, sx=1.0, sy=1.0),
    dict(name="a skerry", x=-460.0, y=560.0, r=14.0, face=7.0, top=4.0, sx=1.0, sy=1.0),
]
# Rock with an outline of its own: a plateau of bare rock inside an irregular polygon, falling at its edge over
# the face's width, its top tilted and broken in steps; the outline, not a circle, is what reads.
ROCKS = [
    dict(name="the corner's knuckle", top=12.6, face=1.4, tilt=(0.0, 0.0), steps=0.6,
         outline=[(52.4, 31.0), (58.0, 30.4), (63.6, 32.0), (66.4, 37.0), (65.0, 42.4), (66.0, 46.6), (60.6, 48.2),
                  (54.0, 47.4), (51.8, 43.0), (52.6, 37.4)]),
    dict(name="the cathedral's rise", top=10.0, face=26.0, tilt=(0.0, 0.0), steps=0.0,
         outline=[(430, -60), (468, -70), (500, -52), (512, -10), (506, 34), (476, 48), (440, 40), (424, 6)]),
]
VALLEYS = [
    # the stream from the forest hill's saddle down to the east harbour's head, in a green valley
    dict(name="the stream valley", depth=9.0, width=26.0, line=[(520, 640), (420, 650), (320, 630), (200, 590), (110, 560)]),
    # the lake's valley, carrying the railway south from the station
    # the railway's valley: low and broad enough for a line at a train's grade (at most 1.5%), wide curves,
    # into a tunnel under the High Moor at about (1500, 260)
    dict(name="the railway's valley", depth=16.0, width=70.0, line=[(740, -40), (860, 0), (980, 80), (1100, 160), (1300, 230), (1500, 260)]),
]
UPLAND_VALLEYS = [  # valleys reaching into the upland from the town's side, the ridge left whole above them
    dict(name="the farm valley", depth=18.0, width=55.0, line=[(780, -500), (950, -530), (1100, -560), (1300, -600), (1460, -620)]),
    dict(name="the quarry valley", depth=20.0, width=50.0, line=[(760, 280), (920, 300), (1080, 330), (1300, 350), (1500, 380)]),
    dict(name="the east valley", depth=16.0, width=50.0, line=[(820, 920), (950, 950), (1060, 980), (1260, 1020), (1420, 1040)]),
]
# the line: the station by the Mere at about 6 m, up the valley at about 1%, curves of 300 m and more, into the
# tunnel under the High Moor; a goods line from the yard on to Barrel Quay
RAILWAY = [(700, -170), (760, -90), (840, -10), (960, 70), (1100, 160), (1300, 230), (1500, 260)]
RAILWAY_TUNNEL = (1500, 260)
RAILWAY_START_Z = 7.0
RAILWAY_GRADE = 0.012
# the old roads, from the town's movement history (docs/town-plan.md, How people moved): they come in down the
# valleys at grades a horse could pull and are the main roads out of town; the heart's ways join them
OLD_ROADS = [
    dict(name="the King's Road", width=9.0, pts=[(446.0, -120.0), (530.0, -200.0), (700.0, -262.0), (900.0, -420.0),
                                               (1100.0, -560.0), (1300.0, -600.0), (1500.0, -640.0)]),
    dict(name="the coast road", width=8.0, pts=[(250.0, -470.0), (120.0, -600.0), (-40.0, -740.0), (-200.0, -800.0),
                                              (-380.0, -900.0), (-620.0, -960.0)]),
    dict(name="the ridge road", width=8.0, pts=[(-262.0, 8.0), (-240.0, 120.0), (-220.0, 300.0), (-130.0, 440.0),
                                              (40.0, 520.0), (150.0, 640.0), (40.0, 790.0), (-200.0, 900.0), (-470.0, 1030.0)]),
    dict(name="the station road", width=8.0, pts=[(446.0, -120.0), (560.0, -175.0), (700.0, -180.0)]),
    dict(name="the hospital road", width=7.0, pts=[(440.0, 26.0), (560.0, 70.0), (760.0, 200.0), (900.0, 420.0),
                                                 (760.0, 600.0), (520.0, 660.0), (300.0, 640.0)]),
]
GOODS_LINE = [(700, -170), (560, -200), (420, -190), (330, -134), (240, -138)]
CLIFFS = [
    # Watch Knoll's face over Holm Street: the houses back onto the rock (the high side to the left of travel)
    dict(name="Watch Knoll's face", top=34.0, base=14.0, width=4.0, line=[(158, -298), (132, -280), (104, -270), (80, -276)]),
    # the bluff: the old town hill's point, a rock face over the bay, about 20 m, high side inland
    dict(name="the bluff", top=26.0, base=2.0, width=5.0, line=[(-250, 20), (-286, 46), (-316, 90), (-334, 140), (-328, 196), (-302, 252)]),
]
CLEFTS = [  # narrow cuts in rock, made after the rock: the knoll's cleft, where the steps go up from Holm Street
    dict(name="the Crack", depth=8.0, width=3.0, line=[(112, -262), (116, -276), (120, -290)]),
]
GULLIES = [  # where the streams come down the old town's west slope to the Basin
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


def _line_dist_z(X, Y, pts):
    """Distance to a polyline of (x, y, z) points, and the line's height at the nearest point."""
    best = np.full(X.shape, 1e9)
    zb = np.zeros(X.shape)
    for (x1, y1, z1), (x2, y2, z2) in zip(pts, pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0.0, 1.0)
        d = np.hypot(X - (x1 + dx * t), Y - (y1 + dy * t))
        closer = d < best
        best = np.where(closer, d, best)
        zb = np.where(closer, z1 + (z2 - z1) * t, zb)
    return best, zb


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


# -- the smooth surface through the drawn lines ----------------------------------------------------------------------
# Solved once on a grid (Laplace's equation, the shore, the contour lines and the spot heights held fixed, coarse
# to fine), then sampled. Between two contour lines the ground ramps evenly from one to the other, as a mapmaker
# reads them; nothing flattens round a line, and the shore stays at the shore's height. Cached in .cache/.

DOMAIN = (-1600.0, -1600.0, 2800.0, 2800.0)
_GRID = {}


def _design_key():
    import hashlib
    blob = repr((COAST, ISLANDS, LAKE, CONTOURS, SPOTS, DOMAIN)).encode()
    return hashlib.sha1(blob).hexdigest()[:16]


def _constraints(step):
    x0, y0, x1, y1 = DOMAIN
    xs = np.arange(x0, x1 + step / 2, step)
    ys = np.arange(y0, y1 + step / 2, step)
    GX, GY = np.meshgrid(xs, ys, indexing="ij")
    val = np.zeros(GX.shape)
    fix = np.zeros(GX.shape, dtype=bool)
    water = water_mask(GX, GY)
    val[water], fix[water] = 1.0, True
    lake = _inside(LAKE_LINE, GX, GY)
    val[lake], fix[lake] = LAKE_LEVEL + 0.4, True

    def put(x, y, z, r=0.0):
        i = int(round((x - x0) / step))
        j = int(round((y - y0) / step))
        k = max(0, int(r / step))
        if 0 <= i < GX.shape[0] and 0 <= j < GX.shape[1]:
            val[max(0, i - k):i + k + 1, max(0, j - k):j + k + 1] = z
            fix[max(0, i - k):i + k + 1, max(0, j - k):j + k + 1] = True

    def line(pts, zf):
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(xb - xa, yb - ya) / (step * 0.5)))
            for t in range(n + 1):
                u = t / n
                put(xa + (xb - xa) * u, ya + (yb - ya) * u, zf(u))

    coast = [p for p in COAST_LINE if abs(p[0]) < 1390 and abs(p[1]) < 1390]
    line(coast, lambda u: 1.8)
    for poly, top in ISLAND_LINES:
        line(poly + poly[:1], lambda u: 1.8)
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        put(cx, cy, top, r=20.0)
    for z, pts in CONTOURS:
        if z is None:
            for (xa, ya, za), (xb, yb, zb) in zip(pts, pts[1:]):
                line([(xa, ya), (xb, yb)], lambda u, za=za, zb=zb: za + (zb - za) * u)
        else:
            line(pts, lambda u, z=z: z)
    for z, (x, y) in SPOTS:
        put(x, y, z, r=12.0)
    return val, fix


def _relax(Z, val, fix, iters):
    Z = np.where(fix, val, Z)
    for _ in range(iters):
        P = np.pad(Z, 1, mode="edge")
        N = (P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:]) * 0.25
        Z = np.where(fix, val, N)
    return Z


def _solve():
    import os
    key = _design_key()
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", f"land-{key}.npy")
    if os.path.exists(cache):
        return np.load(cache)
    Z = None
    for step, iters in [(64.0, 800), (32.0, 700), (16.0, 600), (8.0, 500), (4.0, 400)]:
        val, fix = _constraints(step)
        if Z is None:
            Z = np.where(fix, val, 12.0)
        else:  # the coarser answer, doubled, starts the finer one
            Z = np.repeat(np.repeat(Z, 2, axis=0), 2, axis=1)
            Z = np.pad(Z, ((0, max(0, val.shape[0] - Z.shape[0])), (0, max(0, val.shape[1] - Z.shape[1]))), mode="edge")
            Z = Z[:val.shape[0], :val.shape[1]]
        Z = _relax(Z, val, fix, iters)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    np.save(cache, Z)
    return Z


def _base_surface(X, Y):
    if "Z" not in _GRID:
        _GRID["Z"] = _solve()
    G = _GRID["Z"]
    x0, y0 = DOMAIN[0], DOMAIN[1]
    step = 4.0
    u = np.clip((X - x0) / step, 0, G.shape[0] - 1.001)
    v = np.clip((Y - y0) / step, 0, G.shape[1] - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    a = G[i, j] + (G[i + 1, j] - G[i, j]) * fu
    b = G[i, j + 1] + (G[i + 1, j + 1] - G[i, j + 1]) * fu
    return a + (b - a) * fv


def heights(X, Y):
    """The designed ground at arrays of points X, Y (street metres)."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Z = _base_surface(X, Y)

    # streams cut the old town's west slope; seeded unevenness off the quays
    for g in GULLIES:
        k = np.exp(-((X - g["x"]) / g["width"]) ** 2) * _smoothstep(g["y0"], g["y0"] + 25, Y) * (1 - _smoothstep(g["y1"] - 40, g["y1"], Y))
        Z -= g["depth"] * k * (Y > -15)
    for v in VALLEYS + UPLAND_VALLEYS:
        d = _poly_dist(X, Y, v["line"], closed=False)
        Z -= v["depth"] * np.exp(-(d / v["width"]) ** 2) * _smoothstep(2.0, 16.0, Z) * _smoothstep(4.0, 40.0, Z)
    rough = (_noise(X, Y, 60.0, 1989) * 0.65 + _noise(X + 500, Y, 23.0, 1990) * 0.35 - 0.5) * 2.0
    Z += rough * np.clip((Z - 4.0) / 10.0, 0.0, 1.0)

    # cliffs: inside a band either side of the line the ground steps from base to top over the face's width
    for c in CLIFFS:
        line = c["line"]
        best = np.full(X.shape, 1e9)
        side = np.zeros(X.shape)
        for (x1, y1), (x2, y2) in zip(line, line[1:]):
            dxs, dys = x2 - x1, y2 - y1
            L2 = dxs * dxs + dys * dys
            t = np.clip(((X - x1) * dxs + (Y - y1) * dys) / L2, 0.0, 1.0)
            dd = np.hypot(X - (x1 + dxs * t), Y - (y1 + dys * t))
            sgn = np.sign(dxs * (Y - y1) - dys * (X - x1))  # > 0 to the left of the line's direction
            closer = dd < best
            best = np.where(closer, dd, best)
            side = np.where(closer, sgn, side)
        s_ = side * best
        band = best < 24.0
        face = c["base"] + (c["top"] - c["base"]) * _smoothstep(-c["width"] / 2, c["width"] / 2, s_)
        blend = _smoothstep(24.0, 12.0, best)
        Z = np.where(band, Z * (1 - blend) + np.where(s_ > 0, np.maximum(Z, face), np.minimum(Z, face)) * blend, Z)

    # the water and the lake first, then bedrock standing up out of land and sea alike
    W = water_mask(X, Y)
    lake = _inside(LAKE_LINE, X, Y)
    Z = np.where(W, -6.0, Z)
    Z = np.where(lake, LAKE_LEVEL - 2.0, Z)
    for o in OUTCROPS:
        d = np.hypot((X - o["x"]) / o["sx"], (Y - o["y"]) / o["sy"])
        k = _smoothstep(o["r"], o["r"] - o["face"], d)
        Z = np.where(d < o["r"], np.maximum(Z, Z + (o["top"] - Z) * k), Z)
    for r in ROCKS:
        poly = r["outline"]
        xs_ = [p[0] for p in poly]; ys_ = [p[1] for p in poly]
        sel = (X > min(xs_) - r["face"] - 2) & (X < max(xs_) + r["face"] + 2) & (Y > min(ys_) - r["face"] - 2) & (Y < max(ys_) + r["face"] + 2)
        if not sel.any():
            continue
        Xs, Ys = X[sel], Y[sel]
        inside = _inside(poly, Xs, Ys)
        d = _poly_dist(Xs, Ys, poly)
        sd = np.where(inside, -d, d)  # negative inside the outline
        top = r["top"] - r["steps"] * np.floor(_noise(Xs, Ys, 34.0, 77) * 2.2)  # a top broken into a few broad ledges
        k = _smoothstep(r["face"], 0.0, sd)
        Zs = Z[sel]
        Z[sel] = np.where(sd < r["face"], np.maximum(Zs, Zs + (top - Zs) * k), Zs)
    # the railway: cutting and bank at its grade; a tunnel where the cutting would pass fourteen metres
    pts, acc = [], 0.0
    for k, (xr, yr) in enumerate(RAILWAY):
        if k:
            acc += math.hypot(xr - RAILWAY[k - 1][0], yr - RAILWAY[k - 1][1])
        pts.append((xr, yr, RAILWAY_START_Z + RAILWAY_GRADE * acc))
    d, zr = _line_dist_z(X, Y, pts)
    near = d < 30.0
    if near.any():
        cut = Z - zr
        bed = d < 6.0
        tunnel = cut > 14.0
        side = np.clip((d - 6.0) / 1.5, 0.0, None)  # banks at about two in three
        Zr = np.where(bed, zr, np.where(cut > 0, np.minimum(Z, zr + side), np.maximum(Z, zr - side)))
        Z = np.where(near & ~tunnel, Zr, Z)
    for c in CLEFTS:
        d = _poly_dist(X, Y, c["line"], closed=False)
        Z -= c["depth"] * np.exp(-(d / c["width"]) ** 2) * _smoothstep(4.0, 12.0, Z)
    return Z


def is_water(X, Y):
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    return water_mask(X, Y) | _inside(LAKE_LINE, X, Y)


def z_at(x, y):
    return float(heights(np.array([x]), np.array([y]))[0])


# -- uses: every piece of land has one (docs/town-plan.md, Every place has a use) --------------------------------
# (name, kind, polygon). Kinds: home, night, civic, work, nature, farm, edge. A point may lie in more than one;
# the first listed wins on the map. Checked by centre_uses.py: no land without a use.

USES = [
    ("the Holm: pubs, a club", "night", [(-300, -140), (40, -140), (40, -330), (-300, -330)]),
    ("Holm Street", "night", [(54, -146), (300, -120), (340, -190), (220, -250), (60, -262)]),
    ("Watch Knoll and the Fire Watch", "edge", [(60, -262), (250, -260), (250, -410), (70, -420)]),
    ("Market Square, the cathedral, the Fish Hall", "civic", [(290, -150), (430, -170), (530, -100), (530, 70), (380, 90), (320, 20), (340, -60)]),
    ("the Mere's park and the station", "civic", [(530, -180), (790, -190), (790, 70), (530, 70)]),
    ("Harbour Row", "work", [(-250, -30), (340, -30), (340, -4), (-250, -4)]),
    ("the old town on Herring Hill", "home", [(-250, -4), (300, -4), (330, 30), (270, 110), (120, 190), (-120, 170), (-250, 120)]),
    ("the Bluff and the Hundred Steps", "edge", [(-420, -60), (-250, -60), (-250, 120), (-200, 250), (-330, 290), (-420, 290)]),
    ("the Heights and Lookout Park", "home", [(-250, 120), (-120, 170), (120, 190), (250, 260), (170, 330), (-60, 300), (-330, 290), (-200, 250)]),
    ("the cathedral school and the bishop's garden", "civic", [(300, -4), (380, 90), (420, 360), (250, 260), (120, 190), (270, 110), (330, 30)]),
    ("the cannery and its quay", "work", [(-420, 290), (-330, 290), (-20, 440), (-10, 520), (-420, 520)]),
    ("Tin Town", "home", [(-330, 290), (-60, 300), (170, 330), (110, 470), (-20, 470), (-20, 440)]),
    ("the Plots and the old cemetery", "nature", [(170, 330), (250, 260), (420, 360), (540, 590), (330, 540), (110, 470)]),
    ("Millbrook Dell", "nature", [(-20, 470), (110, 470), (330, 540), (540, 590), (540, 700), (200, 700), (-20, 600)]),
    ("the hospital and the upper school", "civic", [(530, 70), (790, 70), (1020, 200), (1020, 560), (700, 580), (540, 590), (420, 360), (380, 90)]),
    ("the railway's valley, the goods yard, the Mudbowl", "work", [(790, -190), (1020, -200), (1100, 160), (1020, 200), (790, 70)]),
    ("the Grid", "home", [(60, -262), (220, -250), (340, -190), (430, -170), (530, -180), (620, -390), (650, -700), (140, -720), (90, -560), (70, -420), (250, -410), (250, -260)]),
    ("New Town", "civic", [(530, -180), (790, -190), (1020, -200), (1060, -660), (650, -700), (620, -390)]),
    ("Bonfire Beach", "nature", [(-60, -800), (160, -800), (160, -420), (60, -420), (-60, -560)]),
    ("Slipway Cove's boatyards", "work", [(-420, -560), (-150, -820), (-60, -800), (-60, -560), (60, -420), (60, -300), (-300, -330)]),
    ("Ferry Point and the Supply Base", "work", [(-560, -560), (-420, -560), (-150, -820), (-200, -1010), (-560, -1010)]),
    ("Gun Ridge: heath, a mast, German bunkers", "edge", [(-200, -1010), (-150, -820), (160, -800), (140, -720), (650, -700), (1060, -660), (1080, -1010)]),
    ("Plough Valley", "farm", [(1060, -660), (1020, -200), (1100, 160), (1470, 160), (1470, -1010), (1080, -1010)]),
    ("Quarry Hollow: a swimming hole, a sledging slope", "nature", [(1020, 200), (1100, 160), (1470, 160), (1470, 640), (1040, 640), (1020, 560)]),
    ("Tower Wood", "nature", [(540, 590), (700, 580), (1020, 560), (1040, 640), (880, 1000), (700, 1240), (420, 1240), (300, 1000), (200, 700), (540, 700)]),
    ("Sheepwash Valley's farms", "farm", [(1040, 640), (1470, 640), (1470, 1360), (700, 1360), (700, 1240), (880, 1000)]),
    ("Ropewalk: workers' town, the rope walk, boathouses, the brewery", "home", [(-800, 1360), (-800, 900), (-300, 640), (-20, 470), (-20, 600), (200, 700), (300, 1000), (420, 1240), (700, 1240), (700, 1360)]),
    ("Bridge Island, its marina and beach", "home", [(-1000, 60), (-480, 60), (-480, 720), (-1000, 720)]),
    ("Gull Island's cabins", "nature", [(-760, -540), (-500, -540), (-500, -250), (-760, -250)]),
    ("the Teeth and the Pip", "nature", [(-700, -140), (-300, -140), (-300, 160), (-700, 160)]),
    ("Battery Head: heath and an old battery", "edge", [(-1000, -1010), (-560, -1010), (-560, -540), (-1000, -540)]),
]
