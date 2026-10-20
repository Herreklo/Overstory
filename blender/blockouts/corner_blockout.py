"""The beauty corner blocked in by hand: grey masses, the ground, lanes, steps and walls.

Run inside Blender (the MCP's code tool, or blender -b --python):

    import runpy; runpy.run_path("blender/blockouts/corner_blockout.py", run_name="__main__")

This is a level designer's blockout, not a generator: every lane, house mass and wall below was
placed by hand and checked through the game's cameras. It settles layout, height and composition in
clay before any target is painted (docs/experiments.md, LT1, the reset). Houses are masses only: a
body, a roof, a chimney, a plinth down to the ground. Their parts come later, one at a time.

The corner stands in an old town at its real density: rows of houses shoulder to shoulder along two
contour lanes, the stepped lane cutting down between them in the stream's gully, the lanes meeting it
at small level crossings, yards and walls behind, the town thinning to heath at the top. Across the
basin, the quay row and the newer town behind it; then low land falling to the fjord and its islands.

Street coordinates in metres, as Blender's: x along Harbour Row, y up the hill, z up. The ground is the
corner fixture's site (fixtures/lt1-corner.json) cut by the lanes, yards and house pads below.
"""

import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "blender", "resolver")]
import terrain  # noqa: E402

SCENE = "corner_blockout"

# -- lanes: polylines (x, y, z) and a width. Level stretches are lanes, steep ones are steps. -------------

LANES = {
    # the stepped lane in the gully: flat between A and B, a flight to the lower crossing, a flight to the
    # landing, the upper flight to E
    "Bakkesmauet": dict(width=3.2, pts=[(49.3, -0.2, 0.0), (49.3, 12.0, 0.0), (49.3, 17.2, 2.6), (49.1, 21.6, 2.6),
                                        (48.2, 32.5, 8.0), (46.5, 38.0, 8.0), (46.5, 44.5, 8.0), (46.5, 61.5, 18.4),
                                        (46.5, 64.2, 18.4)]),
    # the lower contour lane, level, bending with the hill
    "Nedre Bakken": dict(width=3.6, pts=[(-40.0, 16.6, 2.6), (-10.0, 18.2, 2.6), (20.0, 19.6, 2.6), (49.2, 19.4, 2.6),
                                         (78.0, 18.6, 2.6), (112.0, 17.0, 2.6), (135.0, 16.2, 2.6)]),
    # the upper contour lane west of the landing, level, ending in it
    "Øvre Bakken": dict(width=3.4, pts=[(-40.0, 29.4, 8.0), (-10.0, 31.0, 8.0), (18.0, 32.6, 8.0), (44.0, 34.4, 8.0)]),
    # the upper lane east of the knuckle, a little higher, reaching the rock's top where D stands
    "Knausen": dict(width=3.2, pts=[(64.5, 42.6, 12.6), (86.0, 41.6, 12.3), (112.0, 40.0, 11.8), (135.0, 39.0, 11.6)]),
    # a worn path from E up the heath, where the sheep went until 1958
    "the heath path": dict(width=1.1, pts=[(49.4, 64.6, 18.6), (53.5, 74.0, 22.4), (58.0, 86.0, 27.0), (61.0, 100.0, 30.2)]),
}
LANDING = [(43.0, 32.6), (51.3, 32.6), (51.3, 44.6), (43.0, 44.6)]  # the level place where the lanes meet, z 8
STEEP = 0.12  # a stretch rising faster than this is drawn as steps

# -- houses: masses placed by hand -------------------------------------------------------------------------
# Each house is a box in its own frame: origin at its front-left corner on the ground, local x along the
# front, local y back from it. Rows along a lane take their origin and turn from the lane at a distance
# along it, so a row follows the lane's bend. eave: height of the eaves over the floor; roof: "eaves" (ridge
# along the front), "gable" (ridge front to back, the gable to the lane), "hip", "mansard" or "flat".

H = []


def house(name, ox, oy, angle, w, d, base, eave, pitch=44.0, roof="eaves", role="row"):
    H.append(dict(name=name, ox=ox, oy=oy, angle=angle, w=w, d=d, base=base, eave=eave, pitch=pitch, roof=roof, role=role))


def at_s(pts, s):
    """The point at distance s along a polyline, and its direction in degrees."""
    for (ax, ay, az), (bx, by, bz) in zip(pts, pts[1:]):
        run = math.hypot(bx - ax, by - ay)
        if s <= run:
            t = s / run
            return ax + (bx - ax) * t, ay + (by - ay) * t, math.degrees(math.atan2(by - ay, bx - ax))
        s -= run
    (ax, ay, _), (bx, by, _) = pts[-2], pts[-1]
    return bx, by, math.degrees(math.atan2(by - ay, bx - ax))


def row(lane, side, s, plots, base, role="row"):
    """Houses along a lane, on its uphill side (side +1, left of travel) or downhill side (-1). plots:
    (name, width, depth, eave, pitch, roof, setback from the lane's edge, gap after). Fronts face the lane."""
    L = LANES[lane]
    hw = L["width"] / 2
    for name, w, d, eave, pitch, roof, setback, gap in plots:
        if name:
            if side > 0:
                # the front runs along the lane, the house behind it to the left of travel
                x, y, a = at_s(L["pts"], s)
                off = hw + setback
                ox, oy = x - math.sin(math.radians(a)) * off, y + math.cos(math.radians(a)) * off
                house(name, ox, oy, a, w, d, base, eave, pitch, roof, role)
            else:
                # downhill: the front faces uphill, so the house's frame runs backwards along the lane
                x, y, a = at_s(L["pts"], s + w)
                off = hw + setback
                ox, oy = x + math.sin(math.radians(a)) * off, y - math.cos(math.radians(a)) * off
                house(name, ox, oy, a + 180.0, w, d, base, eave, pitch, roof, role)
        s += w + gap


# Harbour Row: fronts on the quay road at y 0, merchants' houses and quay warehouses, gables and eaves mixed
for name, x0, w, d, eave, pitch, roof in [
        ("HR0", -13.6, 10.8, 8.5, 6.6, 42.0, "eaves"), ("HR1 (101, the Anchor)", -1.0, 11.0, 9.0, 7.2, 40.0, "eaves"),
        ("HR2", 11.6, 8.6, 9.5, 6.0, 46.0, "gable"), ("HR3", 21.6, 12.4, 9.0, 7.8, 40.0, "eaves"),
        ("HR4", 35.4, 1.6, 5.0, 2.6, 0.0, "flat"),  # a low link, a gateway to the yards
        ("A (104, café 1988)", 37.2, 9.8, 9.2, 6.8, 54.0, "mansard"),
        ("B (105)", 52.0, 9.4, 8.4, 6.9, 12.0, "hip"), ("HR6 (106)", 62.6, 11.2, 8.0, 6.0, 22.0, "eaves"),
        ("HR7", 75.0, 6.6, 7.0, 4.4, 48.0, "eaves"), ("HR8", 82.6, 9.2, 10.5, 6.6, 44.0, "gable"),
        ("HR9 (109, the band's loft)", 93.2, 10.6, 15.0, 8.8, 40.0, "gable"), ("HR10 (110)", 105.2, 9.6, 14.0, 9.2, 40.0, "gable"),
        ("HR11", 116.4, 13.0, 9.0, 7.0, 42.0, "eaves")]:
    role = "corner" if name[0] in "AB" and name[1] == " " else "row"
    house(name, x0, 0.0, 0.0, w, d, 0.0, eave, pitch, roof, role)

# sheds in Harbour Row's yards
house("shed 1", 2.4, 11.4, 0.0, 4.6, 2.8, 0.3, 2.4, 20.0)
house("shed 2", 25.0, 11.2, 0.0, 6.0, 3.0, 0.3, 2.6, 18.0)
house("shed 3", 64.4, 11.0, 0.0, 4.2, 3.0, 0.3, 2.4, 20.0)
house("shed 4", 118.0, 11.0, 0.0, 5.0, 3.2, 0.3, 2.6, 18.0)

# below the lower lane, fronting it, their backs high over the yards on plinths
row("Nedre Bakken", -1, 13.0, [("L1", 7.0, 5.0, 4.6, 44.0, "eaves", 0.2, 46.0), ("L2", 6.4, 4.8, 4.2, 46.0, "eaves", 0.2, 30.0),
                               ("L3", 8.0, 5.2, 4.8, 42.0, "eaves", 0.2, 0.0)], 2.6)

# the lower lane's uphill side, shoulder to shoulder; a gap with steps up at s 72; C's yard from s 76
row("Nedre Bakken", +1, 4.0, [
    ("U1", 9.6, 7.0, 5.4, 42.0, "eaves", 0.0, 0.0), ("U2", 7.2, 6.6, 4.4, 46.0, "eaves", 0.0, 1.2),
    ("U3", 6.4, 8.4, 5.2, 48.0, "gable", 0.0, 0.6), ("U4", 12.8, 7.2, 5.0, 40.0, "eaves", 0.0, 0.0),
    ("U5", 6.0, 6.6, 4.0, 46.0, "eaves", 0.0, 1.6), ("U6", 8.8, 7.6, 6.2, 42.0, "eaves", 2.6, 0.8),
    ("U7", 7.0, 8.0, 4.6, 48.0, "gable", 0.0, 0.4), ("U7b", 5.6, 6.4, 4.2, 46.0, "eaves", 0.0, 3.0)], 2.75)
# (the row ends at x 32: steps go up the gap to the upper lane, then C's yard and the stepped lane)
row("Nedre Bakken", +1, 91.8, [
    ("U10 (under the rock)", 6.8, 6.4, 4.2, 46.0, "eaves", 0.0, 1.4), ("U11", 8.4, 6.8, 5.6, 42.0, "eaves", 0.0, 0.0),
    ("U12", 6.0, 8.2, 5.0, 48.0, "gable", 0.0, 1.8), ("U13", 11.6, 7.0, 4.6, 42.0, "eaves", 0.0, 0.6),
    ("U14", 7.0, 7.4, 6.0, 44.0, "eaves", 1.8, 1.0), ("U15", 6.2, 8.6, 5.0, 48.0, "gable", 0.0, 0.4),
    ("U16", 9.6, 7.0, 4.4, 44.0, "eaves", 0.0, 0.0), ("U17", 8.2, 7.2, 6.4, 40.0, "eaves", 0.0, 1.2)], 2.75)

# the upper lane's uphill side, west of the landing
row("Øvre Bakken", +1, 0.0, [
    ("V1", 8.0, 6.8, 4.6, 46.0, "eaves", 0.0, 0.8), ("V2", 10.4, 7.0, 5.6, 42.0, "eaves", 0.0, 0.0),
    ("V3", 6.2, 8.6, 4.6, 48.0, "gable", 0.0, 2.4), ("V4", 8.6, 6.6, 4.2, 46.0, "eaves", 3.0, 1.0),
    ("V5", 7.2, 7.2, 5.4, 44.0, "eaves", 0.0, 0.0), ("V6", 13.2, 7.6, 6.4, 40.0, "eaves", 0.0, 1.4),
    ("V7", 6.0, 7.8, 4.4, 48.0, "gable", 0.0, 0.6), ("V8", 8.8, 6.8, 4.8, 44.0, "eaves", 0.0, 1.0),
    ("V9", 5.8, 6.4, 4.0, 46.0, "eaves", 0.0, 1.2)], 8.3)

# the corner's C, D and E, placed one by one
house("C (1203, cooper 1879)", 35.8, 35.6, 4.0, 7.2, 7.4, 8.4, 4.4, 45.0, "gable", "corner")
house("D (1107, empty since 1986)", 60.6, 36.6, 90.0, 7.6, 7.0, 12.65, 4.0, 46.0, "gable", "corner")  # front to the landing (west)
house("E (304, 1826)", 49.8, 64.6, 90.0, 7.0, 6.8, 20.6, 4.0, 46.0, "eaves", "corner")  # gable to the lane

# the east upper lane's uphill side
row("Knausen", +1, 3.0, [
    ("W1", 7.6, 6.6, 4.6, 46.0, "eaves", 0.0, 0.0), ("W2", 9.0, 7.0, 5.6, 42.0, "eaves", 0.0, 1.6),
    ("W3", 6.2, 8.2, 4.6, 48.0, "gable", 0.0, 0.8), ("W4", 11.4, 7.0, 5.0, 42.0, "eaves", 0.0, 0.0),
    ("W5", 6.6, 6.6, 4.2, 46.0, "eaves", 2.4, 1.4), ("W6", 8.4, 7.2, 5.8, 44.0, "eaves", 0.0, 1.0),
    ("W7", 6.0, 8.0, 4.4, 48.0, "gable", 0.0, 0.6)], 12.5)

# the town thinning towards the heath: a few houses higher up, each on its own
for name, ox, oy, a, w, d, eave, roof in [("X1", -24.0, 47.0, 4.0, 7.4, 6.6, 4.4, "eaves"), ("X2", -2.0, 48.6, -3.0, 6.4, 7.6, 4.0, "gable"),
                                         ("X3", 20.0, 49.6, 6.0, 8.0, 6.6, 4.6, "eaves"), ("X4", 76.0, 56.0, -4.0, 7.0, 6.4, 4.2, "eaves"),
                                         ("X5", 96.0, 55.0, -6.0, 6.4, 7.6, 4.6, "gable")]:
    house(name, ox, oy, a, w, d, None, eave, 46.0 if roof == "gable" else 44.0, roof)

# across the basin: the quay row, colourful and dense, facing back across the water (fronts at y -131)
fx = 120.0
for i, (w, d, eave, pitch, roof, gap) in enumerate([
        (9.0, 9.0, 7.4, 40.0, "eaves", 0.6), (8.0, 8.5, 6.2, 44.0, "gable", 0.4), (10.4, 9.0, 8.2, 38.0, "eaves", 0.8),
        (7.6, 8.0, 5.8, 45.0, "gable", 0.4), (11.0, 10.0, 9.0, 36.0, "eaves", 6.0), (9.4, 9.0, 7.6, 40.0, "eaves", 0.5),
        (8.2, 8.5, 6.6, 44.0, "gable", 0.4), (12.0, 14.0, 9.6, 38.0, "gable", 0.6), (9.0, 9.0, 7.0, 42.0, "eaves", 0.4),
        (10.0, 9.0, 8.4, 38.0, "eaves", 7.0), (8.4, 8.0, 6.2, 44.0, "gable", 0.4), (9.6, 9.0, 7.8, 40.0, "eaves", 0.5),
        (11.2, 12.0, 9.4, 36.0, "gable", 0.6), (8.0, 8.0, 6.0, 45.0, "eaves", 0.4), (9.8, 9.0, 8.0, 40.0, "eaves", 0.5),
        (10.6, 10.0, 8.8, 38.0, "gable", 0.5), (8.6, 8.5, 6.6, 42.0, "eaves", 0.4), (9.4, 9.0, 7.6, 40.0, "eaves", 0.6),
        (10.2, 9.0, 8.0, 40.0, "eaves", 0.5), (8.8, 9.0, 7.0, 44.0, "gable", 0.4)]):
    back = (0.0, 0.6, 0.0, 1.2, 0.0, 0.4)[i % 6]
    # the far row faces +y: its frame runs from high x to low x
    house(f"far {i + 1}", fx, -131.0 - back, 180.0, w, d, 2.1, eave, pitch, roof, "far")
    fx -= w + gap
# the newer town behind it: post-war and seventies blocks, flat roofs, taller, looser
for i, (x0, y0, w, d, eave) in enumerate([(-50.0, -168.0, 18.0, 12.0, 13.0), (-24.0, -172.0, 14.0, 12.0, 16.0),
                                          (-2.0, -166.0, 22.0, 11.0, 10.0), (28.0, -176.0, 12.0, 12.0, 22.0),
                                          (48.0, -168.0, 20.0, 12.0, 12.0), (76.0, -170.0, 16.0, 13.0, 15.0),
                                          (150.0, -170.0, 18.0, 12.0, 11.0), (176.0, -176.0, 14.0, 14.0, 18.0),
                                          (-40.0, -200.0, 20.0, 14.0, 14.0), (10.0, -204.0, 16.0, 12.0, 11.0),
                                          (40.0, -210.0, 24.0, 12.0, 17.0), (170.0, -206.0, 20.0, 12.0, 12.0)]):
    house(f"newer {i + 1}", x0 + w, y0, 180.0, w, d, None, eave, 0.0, "flat", "far")

# -- yards and walls ------------------------------------------------------------------------------------------
# yards: level pads (x0, y0, x1, y1, z) made with walls; walls: polylines (x, y) with a top height, and the
# wall's foot follows the ground

YARDS = [
    (36.2, 21.8, 47.2, 31.4, 4.6),     # C's yard, the birch's, behind the wall on the stepped lane
    (60.6, 36.0, 66.6, 46.0, 12.5),    # D's yard on the rock, growing over
    (-40.0, 9.0, 47.0, 15.6, 0.3),     # Harbour Row's yards, west of the lane
    (52.0, 9.0, 135.0, 14.8, 0.3),     # and east
]
WALLS = [
    [(47.3, 9.4), (47.3, 21.6)],                        # the stepped lane's wall, lower flight
    [(47.4, 21.8), (47.2, 31.6), (43.0, 32.4)],         # holding C's yard, turning at the landing
    [(36.0, 21.6), (47.0, 21.6)],                       # C's yard along the lower lane
    [(-40.0, 29.3), (-10.0, 30.9), (18.0, 32.5), (36.0, 33.0)],   # the upper lane's downhill edge
    [(-40.0, 9.0), (47.0, 9.0)], [(52.0, 9.0), (135.0, 9.0)],      # yards behind Harbour Row
    [(-40.0, 15.6), (47.2, 15.6)], [(52.0, 15.0), (135.0, 15.0)],  # the lower lane's downhill edge
    [(66.6, 36.0), (66.6, 46.0)],                       # D's yard, east
    [(64.0, 41.0), (135.0, 38.4)],                      # the east upper lane's downhill edge
]


def ground_site():
    fx = json.load(open(os.path.join(ROOT, "fixtures", "lt1-corner.json")))

    def m(k, v):
        if k == "seed":
            return v
        if isinstance(v, dict):
            return {kk: m(kk, vv) for kk, vv in v.items()}
        if isinstance(v, list):
            return [m(k, vv) for vv in v]
        return v / 1000.0
    return {k: m(k, v) for k, v in fx["site"].items()}


SITE = ground_site()


def lane_z_at(pts, x, y):
    d, k, t, _ = terrain.nearest_on_polyline([p[:2] for p in pts], x, y)
    return d, pts[k][2] + (pts[k + 1][2] - pts[k][2]) * t


def frame(h):
    c, s_ = math.cos(math.radians(h["angle"])), math.sin(math.radians(h["angle"]))
    return lambda x, y: (h["ox"] + x * c - y * s_, h["oy"] + x * s_ + y * c)


def footprint(h, grow=0.0):
    w = frame(h)
    return [w(-grow, -grow), w(h["w"] + grow, -grow), w(h["w"] + grow, h["d"] + grow), w(-grow, h["d"] + grow)]


def build_ground(x0, y0, x1, y1, step):
    """The site's ground, cut by the lanes, the landing, the yards and the houses' pads."""
    f = terrain.Field(SITE, x0, y0, x1, y1, step)
    for h in H:  # a house with no floor height given stands on the natural ground at its middle
        if h["base"] is None:
            cx, cy = frame(h)(h["w"] / 2, h["d"] / 2)
            h["base"] = round(terrain.natural_z(SITE, cx, cy), 2)
    pads = [dict(kind="house", z=h["base"] - 0.05, corners=footprint(h, 0.6)) for h in H if h["role"] != "far"]
    pads += [dict(kind="garden", z=z, corners=[(a, b), (c, b), (c, d), (a, d)]) for a, b, c, d, z in YARDS]
    town = dict(lanes=[], stairs=[dict(width=L["width"], points=[list(p) for p in L["pts"]]) for L in LANES.values()],
                squares=[dict(z=8.0, corners=LANDING)], pads=pads, site=SITE)
    terrain.carve(f, town)
    return f


# -- mesh helpers -----------------------------------------------------------------------------------------------


def new_obj(name, verts, faces, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def box(v, f, x0, y0, z0, x1, y1, z1):
    n = len(v)
    v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f += [(n, n + 3, n + 2, n + 1), (n + 4, n + 5, n + 6, n + 7), (n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 6, n + 5),
          (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]


def house_mesh(h, ground, coll):
    """A house as masses, built in its own frame: a plinth down to the lowest ground under it, the body,
    the roof, a chimney."""
    v, f = [], []
    W, D, z0 = h["w"], h["d"], h["base"]
    to = frame(h)
    low = min(ground(*to(x, y)) for x in (0, W / 2, W) for y in (0, D / 2, D))
    if low < z0 - 0.15:
        box(v, f, 0.05, 0.05, low - 0.3, W - 0.05, D - 0.05, z0)
    ze = z0 + h["eave"]
    box(v, f, 0, 0, z0, W, D, ze)
    o = 0.45  # the eave's overhang
    roof = h["roof"]
    if roof == "flat":
        box(v, f, -0.15, -0.15, ze, W + 0.15, D + 0.15, ze + 0.5)
    elif roof == "hip":
        n = len(v)
        inset = min(W, D) / 2
        rise = math.tan(math.radians(h["pitch"])) * inset
        v += [(-o, -o, ze), (W + o, -o, ze), (W + o, D + o, ze), (-o, D + o, ze), (inset, D / 2, ze + rise), (W - inset, D / 2, ze + rise)]
        f += [(n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 5), (n + 2, n + 3, n + 4, n + 5), (n + 3, n, n + 4), (n, n + 3, n + 2, n + 1)]
    else:
        along = roof in ("eaves", "mansard")  # ridge along the front
        span = D if along else W
        rise = math.tan(math.radians(h["pitch"])) * (span / 2 + o) * (0.8 if roof == "mansard" else 1.0)
        n = len(v)
        if along:
            v += [(-o * 0.6, -o, ze), (W + o * 0.6, -o, ze), (W + o * 0.6, D + o, ze), (-o * 0.6, D + o, ze),
                  (-o * 0.6, D / 2, ze + rise), (W + o * 0.6, D / 2, ze + rise)]
            f += [(n, n + 1, n + 5, n + 4), (n + 2, n + 3, n + 4, n + 5), (n + 1, n + 2, n + 5), (n + 3, n, n + 4), (n, n + 3, n + 2, n + 1)]
            n = len(v)
            v += [(0, 0, ze), (0, D, ze), (0, D / 2, ze + rise - 0.2), (W, 0, ze), (W, D, ze), (W, D / 2, ze + rise - 0.2)]
            f += [(n, n + 2, n + 1), (n + 3, n + 4, n + 5)]
        else:
            v += [(-o, -o * 0.6, ze), (W + o, -o * 0.6, ze), (W + o, D + o * 0.6, ze), (-o, D + o * 0.6, ze),
                  (W / 2, -o * 0.6, ze + rise), (W / 2, D + o * 0.6, ze + rise)]
            f += [(n + 1, n + 2, n + 5, n + 4), (n + 3, n, n + 4, n + 5), (n, n + 1, n + 4), (n + 2, n + 3, n + 5), (n, n + 3, n + 2, n + 1)]
            n = len(v)
            v += [(0, 0, ze), (W, 0, ze), (W / 2, 0, ze + rise - 0.2), (0, D, ze), (W, D, ze), (W / 2, D, ze + rise - 0.2)]
            f += [(n, n + 1, n + 2), (n + 3, n + 5, n + 4)]
        cx = W * 0.62 if along else W / 2
        cy = D / 2 if along else D * 0.62
        box(v, f, cx - 0.35, cy - 0.35, ze + rise * 0.4, cx + 0.35, cy + 0.35, ze + rise + 1.1)
    v = [(*to(x, y), z) for x, y, z in v]
    ob = new_obj(h["name"], v, f, coll)
    ob["role"] = h["role"]
    return ob


def lane_meshes(ground, coll):
    """Each lane as a surface on the cut ground, steps where it is steep."""
    v, f = [], []
    for name, L in LANES.items():
        pts, hw = L["pts"], L["width"] / 2
        for (ax, ay, az), (bx, by, bz) in zip(pts, pts[1:]):
            dx, dy = bx - ax, by - ay
            run = math.hypot(dx, dy)
            if run < 0.05:
                continue
            ux, uy = dx / run, dy / run
            nx, ny = -uy, ux
            steep = abs(bz - az) / run > STEEP
            n_seg = max(1, int(abs(bz - az) / 0.17)) if steep else max(1, int(run / 2.0))
            for i in range(n_seg):
                t0, t1 = i / n_seg, (i + 1) / n_seg
                p0 = (ax + dx * t0, ay + dy * t0)
                p1 = (ax + dx * t1, ay + dy * t1)
                if steep:
                    top = az + (bz - az) * (t1 if bz > az else t0) + 0.03
                    zb = top - abs(bz - az) / n_seg - 0.25
                    corners = [(p0[0] + nx * hw, p0[1] + ny * hw), (p0[0] - nx * hw, p0[1] - ny * hw),
                               (p1[0] - nx * hw, p1[1] - ny * hw), (p1[0] + nx * hw, p1[1] + ny * hw)]
                    n = len(v)
                    v += [(x, y, zb) for x, y in corners] + [(x, y, top) for x, y in corners]
                    f += [(n + 4, n + 5, n + 6, n + 7), (n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 6, n + 5),
                          (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]
                else:
                    za = az + (bz - az) * t0 + 0.04
                    zb_ = az + (bz - az) * t1 + 0.04
                    n = len(v)
                    v += [(p0[0] + nx * hw, p0[1] + ny * hw, za), (p0[0] - nx * hw, p0[1] - ny * hw, za),
                          (p1[0] - nx * hw, p1[1] - ny * hw, zb_), (p1[0] + nx * hw, p1[1] + ny * hw, zb_)]
                    f += [(n, n + 1, n + 2, n + 3)] if (nx * dy - ny * dx) < 0 else [(n, n + 3, n + 2, n + 1)]
    n = len(v)
    v += [(x, y, 8.04) for x, y in LANDING]
    f += [(n, n + 1, n + 2, n + 3)]
    return new_obj("lanes and steps", v, f, coll)


def wall_meshes(ground, coll):
    """Dry-stone walls: 0.45 m thick, from the lower ground on either side to 1 m over the higher."""
    v, f = [], []
    for line in WALLS:
        for (ax, ay), (bx, by) in zip(line, line[1:]):
            run = math.hypot(bx - ax, by - ay)
            k = max(1, int(run / 2.0))
            ux, uy = (bx - ax) / run, (by - ay) / run
            nx, ny = -uy * 0.225, ux * 0.225
            for i in range(k):
                x0, y0 = ax + (bx - ax) * i / k, ay + (by - ay) * i / k
                x1, y1 = ax + (bx - ax) * (i + 1) / k, ay + (by - ay) * (i + 1) / k
                zs = [ground(x0 + nx * 3, y0 + ny * 3), ground(x0 - nx * 3, y0 - ny * 3),
                      ground(x1 + nx * 3, y1 + ny * 3), ground(x1 - nx * 3, y1 - ny * 3)]
                lo, hi = min(zs) - 0.3, max(zs) + 1.0
                n = len(v)
                c = [(x0 + nx, y0 + ny), (x0 - nx, y0 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny)]
                v += [(x, y, lo) for x, y in c] + [(x, y, hi) for x, y in c]
                f += [(n + 4, n + 5, n + 6, n + 7), (n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 6, n + 5),
                      (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]
    return new_obj("walls", v, f, coll)


def grid_mesh(name, field, coll, skip=None):
    v, f = [], []
    nx, ny = field.nx, field.ny
    for j in range(ny):
        for i in range(nx):
            v.append((field.x0 + i * field.step, field.y0 + j * field.step, field.z[j][i]))
    for j in range(ny - 1):
        for i in range(nx - 1):
            x, y = field.x0 + (i + 0.5) * field.step, field.y0 + (j + 0.5) * field.step
            if skip and skip(x, y):
                continue
            a = j * nx + i
            f.append((a, a + 1, a + nx + 1, a + nx))
    return new_obj(name, v, f, coll)


def quay_meshes(coll):
    """The quay road, the pavement and the quay at z 0 from the building line to the quay's edge, its wall
    down to the water, and the water of the basin and the fjord."""
    v, f = [], []
    box(v, f, -160.0, -15.4, -3.0, 260.0, 0.0, 0.0)
    ob = new_obj("quay road and quay", v, f, coll)
    v, f = [], []
    v += [(-2000.0, -2000.0, -2.1), (2000.0, -2000.0, -2.1), (2000.0, 2000.0, -2.1), (-2000.0, 2000.0, -2.1)]
    f += [(0, 1, 2, 3)]
    w = new_obj("water", v, f, coll)
    w["role"] = "water"
    return ob, w


def build():
    scene = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
    old = bpy.data.collections.get("blockout")
    if old:  # only what this script made; cameras and lights the user set up stay
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    for me in [m for m in bpy.data.meshes if m.users == 0]:
        bpy.data.meshes.remove(me)
    coll = bpy.data.collections.new("blockout")
    scene.collection.children.link(coll)

    fine = build_ground(-45.0, -15.4, 140.0, 125.0, 1.0)  # first: it fills in the floors not given by hand
    ground = fine.sample
    coarse = terrain.Field(SITE, -1100.0, -1300.0, 1300.0, 1000.0, 10.0)
    grid_mesh("ground, close", fine, coll)
    inside = lambda x, y: -44.0 < x < 139.0 and -15.0 < y < 124.0
    grid_mesh("land, around", coarse, coll, skip=inside)
    for h in H:
        g = ground if h["role"] != "far" else coarse.sample
        house_mesh(h, g, coll)
    lane_meshes(ground, coll)
    wall_meshes(ground, coll)
    quay_meshes(coll)
    return scene, len(H)


if __name__ == "__main__":
    scene, n = build()
    print(f"blocked in {n} houses in scene {scene.name}")
