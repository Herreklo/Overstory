"""Grow the town above Harbour Row: a stand-in for the fabric pass (docs/research/generating-the-past.md).

    blender -b --factory-startup --python grow_town.py -- ../../fixtures/lt1-street.json ../../fixtures/lt1-town.json

From a few site facts it lays out what a west-coast harbour town builds into its hill, in the order a
town grows:
- lanes along the contours, one above the other, each cut level into the slope;
- stepped lanes climbing straight up, the main one in the gully where the stream runs;
- a small square where the main stepped lane meets the first lane;
- houses on the uphill side of each lane, facing the harbour, each on a stone basement where the
  ground falls away, with a front garden levelled at the house's floor, a garden wall along the lane
  and steps up through it;
- diaries for every house (older higher up, where the town began), checked by validate.py, and
  generated again if a house fails (generate, test, reject);
- lamps by the era each lane was laid out, trees in gardens, by the stream and on the hill;
- who is in at blue hour.

Everything it writes is labelled `generated-past`: facts the engine's fabric pass will own. The
output is deterministic for a world seed. Lengths in the fixture are millimetres; this script works in
metres and converts at the end.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402

import building  # noqa: E402
import validate  # noqa: E402
from resolve import resolve  # noqa: E402
from hashing import h, unit  # noqa: E402
from eras import era_for  # noqa: E402

STYLE = "measured"  # the shape the town is grown and exported at; the export must use the same
import terrain  # noqa: E402

YEAR = 1989

SITE = dict(edge=-15.4, bay_x0=-30.0, bay_x1=146.0, yard=17.0, slope=0.2, steepen=0.0008,
            gully_x=50.0, gully_depth=4.5, gully_width=10.0, rough=2.4, side_height=110.0, side_reach=230.0)

LANES = [  # name, height (m), width (m), surface, laid, lamps
    ("Øvre gate", 7.0, 4.6, "asphalt", 1968, "pole-1965"),
    ("Bakken", 15.5, 4.0, "asphalt", 1971, "pole-1965"),
    ("Kirkebakken", 24.5, 3.6, "setts", 1912, "post-1934"),
    ("Steinveien", 34.0, 3.4, "gravel", None, "post-1934"),
    ("Utsikten", 44.0, 3.2, "gravel", None, "post-1934"),
]
STAIR_XS = [-14.0, 49.7, 126.0]  # the stepped lanes: west end, the gully, east end
SQUARE = dict(lane=0, x0=57.0, x1=75.0, depth=12.0)
LANE_X = (-18.0, 132.0)


def rnd(*k):
    return unit(h(SEED, "town", *k))


# -- lanes ------------------------------------------------------------------------------------------------

def contour(z, x0, x1, step=2.0):
    """The line along which the natural ground stands at height z, smoothed."""
    pts = []
    for k in range(int((x1 - x0) / step) + 1):
        x = x0 + k * step
        lo, hi = SITE["yard"] + 1.0, 400.0
        if terrain.natural_z(SITE, x, lo) > z:
            continue
        if terrain.natural_z(SITE, x, SITE["yard"] + 12.0) > z:  # where the bay's side rises, the lane stops
            continue
        for _ in range(40):
            mid = (lo + hi) / 2
            if terrain.natural_z(SITE, x, mid) < z:
                lo = mid
            else:
                hi = mid
        pts.append([x, (lo + hi) / 2])
    for _ in range(6):  # lanes are laid out smoother than the ground they follow
        pts = [pts[0]] + [[p[0], (a[1] + p[1] * 2 + b[1]) / 4] for a, p, b in zip(pts, pts[1:], pts[2:])] + [pts[-1]]
    return pts


def frame(pts, s):
    """Point, unit tangent and downhill normal at arc length s along a 2D polyline."""
    acc = 0.0
    for k in range(len(pts) - 1):
        ax, ay = pts[k][0], pts[k][1]
        bx, by = pts[k + 1][0], pts[k + 1][1]
        L = math.hypot(bx - ax, by - ay)
        if acc + L >= s or k == len(pts) - 2:
            t = 0.0 if L == 0 else min(1.0, max(0.0, (s - acc) / L))
            tx, ty = (bx - ax) / L, (by - ay) / L
            return (ax + (bx - ax) * t, ay + (by - ay) * t), (tx, ty), (ty, -tx)
        acc += L
    raise ValueError("empty polyline")


def length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def arc_at_x(pts, x):
    """Arc length where the polyline reaches x (lanes run in +x)."""
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if a[0] <= x <= b[0] and b[0] > a[0]:
            return acc + L * (x - a[0]) / (b[0] - a[0])
        acc += L
    return None


# -- houses -----------------------------------------------------------------------------------------------

def diary(bid, lane_index, n):
    """A house's history: older higher up, where the town began."""
    k = lambda *p: rnd("diary", bid, n, *p)
    span = [(1885, 1965), (1860, 1935), (1840, 1910), (1825, 1890), (1820, 1880)][lane_index]
    y0 = int(span[0] + (span[1] - span[0]) * k("year"))
    era = era_for(y0, h(SEED, bid, "era"))
    storeys = 1500 if k("st") < 0.55 else 2000
    if era in ("functionalist", "postwar", "seventies") and k("st2") < 0.5:
        storeys = 2000
    with_ = [a for a, p in (("bislag", 0.3), ("veranda", 0.1), ("dormer", 0.15), ("bay", 0.12), ("ark", 0.08)) if k("with", a) < p]
    events = [dict(id=1, year=y0, kind="built", params=dict(era=era, storeys=storeys, wealth=int(200 + 650 * k("w")), **({"with": with_} if with_ else {})),
                   cause="built as the town climbed the hill")]
    year, eid = y0, 2
    for m in range(int(k("n") * 4)):
        year += 8 + int(k("dy", m) * 22)
        if year > YEAR:
            break
        r = k("what", m)
        if r < 0.45:
            ev = dict(kind="repainted", params={}, cause="upkeep")
        elif r < 0.65 and 1950 <= year <= 1985:
            ev = dict(kind="windows_replaced", params=dict(scope="all" if k("sc", m) < 0.6 else "street"), cause="new windows, cheaper to heat")
        elif r < 0.75:
            ev = dict(kind="extended", params=dict(kind="lean_to"), cause="a wash house at the back")
        elif r < 0.82 and year >= 1975:
            ev = dict(kind="neglected", params=dict(amount=200 + int(300 * k("ng", m))), cause="the owners grew old")
        elif r < 0.88 and year >= 1980:
            ev = dict(kind="restored", params=dict(windows="original", amount=300), cause="a young family restores it")
        else:
            ev = dict(kind="repainted", params={}, cause="new owners")
        ev.update(id=eid, year=year)
        events.append(ev)
        eid += 1
    w = 7000 + 1000 * int(k("pw") * 4)
    d = 7000 + 500 * int(k("pd") * 3)
    return dict(id=bid, type="house", character="high_road" if k("hr") < 0.7 else "low_road", plot=dict(x=0, w=w, d=d), events=events, provenance="generated-past")


def extents(ob):
    """Local extents: ground-level footprint (x0, x1, y0 front, y1 back) and the full width (x0, x1)."""
    vs = [v.co for v in ob.data.vertices]
    g = [v for v in vs if v.z < 1.0]
    return (min(v.x for v in g), max(v.x for v in g), min(v.y for v in g), max(v.y for v in g)), (min(v.x for v in vs), max(v.x for v in vs))


def world(origin, yaw, x, y):
    c, s = math.cos(yaw), math.sin(yaw)
    return (origin[0] + x * c - y * s, origin[1] + x * s + y * c)


def place(lane_pts, lane_z, hw, s, fp, setback_min=1.8, rise_min=0.4, base_fixed=None, rise_max=1.8):
    """Put a house with ground footprint fp at arc s, front to the lane. Returns its placement."""
    (L, t, n) = frame(lane_pts, s)
    yaw = math.atan2(n[1], n[0]) + math.pi / 2
    x0, x1, y0, y1 = fp
    rise = rise_min
    for _ in range(3):
        setback = max(setback_min, rise * 1.75 + 1.2)
        front = (L[0] - n[0] * (hw + setback), L[1] - n[1] * (hw + setback))
        origin = (front[0] + y0 * n[0], front[1] + y0 * n[1])
        quad = [world(origin, yaw, x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        # the floor is set at the ground along the house's front; its back is cut into the slope
        front_mid = [world(origin, yaw, x, y0) for x in (x0, (x0 + x1) / 2, x1)]
        ground = max(terrain.natural_z(SITE, x, y) for x, y in front_mid) + 0.25
        base = base_fixed if base_fixed is not None else min(max(ground, lane_z + rise_min), lane_z + rise_max)
        rise = base - lane_z
    low = min(terrain.natural_z(SITE, x, y) for x, y in quad)
    return dict(L=L, t=t, n=n, yaw=yaw, setback=setback, origin=origin, quad=quad, base=round(base, 3), low=low, rise=rise)


def grow(fixture):
    global SEED
    SEED = fixture["worldSeed"]
    SITE["seed"] = SEED
    bpy.ops.wm.read_factory_settings(use_empty=True)
    town = dict(lanes=[], stairs=[], squares=[], pads=[], walls=[], steps=[], buildings=[], placements=[], lamps=[], trees=[], lit=[])

    # lanes along the contours
    lanes = []
    for li, (name, z, width, surface, laid, lamp) in enumerate(LANES):
        pts = contour(z, *LANE_X)
        lanes.append(dict(id=f"lane-{li + 1}", name=name, z=z, width=width, surface=surface, laid=laid, lamp=lamp, points=pts))
    town["lanes"] = lanes

    # stepped lanes: from the quay street up through every lane they reach
    for si, sx in enumerate(STAIR_XS):
        path = [[sx, 1.0 if -1 < sx < 140 else 6.0, 0.0]]
        if si != 1:
            path = [[sx, 6.0, terrain.natural_z(SITE, sx, 6.0)]]
        for lane in lanes:
            a = arc_at_x(lane["points"], sx)
            if a is None:
                break
            (p, _, n) = frame(lane["points"], a)
            path.append([p[0] + n[0] * lane["width"] / 2, p[1] + n[1] * lane["width"] / 2, lane["z"]])  # the lane's lower edge
            path.append([p[0] - n[0] * lane["width"] / 2, p[1] - n[1] * lane["width"] / 2, lane["z"]])  # across it
        town["stairs"].append(dict(id=f"stair-{si + 1}", name=["Vestre smau", "Smauet", "Østre smau"][si], width=2.4 if si == 1 else 1.8, points=path))

    # the square, uphill of the first lane where the main stepped lane arrives
    sq = SQUARE
    lane = lanes[sq["lane"]]
    hw = lane["width"] / 2
    a0, a1 = arc_at_x(lane["points"], sq["x0"]), arc_at_x(lane["points"], sq["x1"])
    (p0, _, n0), (p1, _, n1) = frame(lane["points"], a0), frame(lane["points"], a1)
    corners = [(p0[0] - n0[0] * hw, p0[1] - n0[1] * hw), (p1[0] - n1[0] * hw, p1[1] - n1[1] * hw),
               (p1[0] - n1[0] * (hw + sq["depth"]), p1[1] - n1[1] * (hw + sq["depth"])), (p0[0] - n0[0] * (hw + sq["depth"]), p0[1] - n0[1] * (hw + sq["depth"]))]
    town["squares"].append(dict(id="square-1", name="Torget", z=lane["z"], corners=corners, surface="setts", laid=1912))
    # the square is cut into the hill: walls on its two sides
    for (ax, ay), (bx, by) in ((corners[0], corners[3]), (corners[1], corners[2])):
        wall = []
        for k in range(7):
            t = k / 6
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            wall.append([x, y, lane["z"], max(lane["z"] + 0.4, terrain.natural_z(SITE, x, y) + 0.3)])
        town["walls"].append(dict(kind="dry_stone", points=wall))

    # houses along each lane
    bid = 1000
    skip = []  # (lane, arc0, arc1) kept clear
    for li, lane in enumerate(lanes):
        for sx in STAIR_XS:
            a = arc_at_x(lane["points"], sx)
            if a is not None:
                skip.append((li, a - 3.4, a + 3.4))
    skip.append((sq["lane"], a0 - 1.0, a1 + 1.0))
    for li, lane in enumerate(lanes):
        pts, z, hw = lane["points"], lane["z"], lane["width"] / 2
        total = length(pts)
        s = 3.0
        while s < total - 6.0:
            gap = 1.8 + 1.6 * rnd("gap", li, round(s))
            if rnd("garden", li, round(s)) < 0.12:
                gap += 6.0 + 5.0 * rnd("gw", li, round(s))
            for attempt in range(6):
                d = diary(bid, li, attempt)
                plan = resolve(d, YEAR, SEED)
                ob = building.build(plan, STYLE, name=f"probe_{bid}")
                ok = not validate.check(ob)
                fp, (wx0, wx1) = extents(ob)
                bpy.data.objects.remove(ob, do_unlink=True)
                if ok:
                    break
            else:
                s += 8.0
                continue
            sc = s + gap - wx0
            lo, hi = sc + wx0, sc + wx1
            blocked = [b for b in skip if b[0] == li and lo < b[2] and hi > b[1]]
            if blocked:
                s = max(b[2] for b in blocked)
                continue
            if hi > total - 3.0:
                break
            pl = place(pts, z, hw, sc, fp, rise_max=0.8 + 1.3 * rnd("rise", bid))
            town["buildings"].append(d)
            door = plan["main"]["cols"][plan["main"]["door_col"]] / 1000.0 if plan["main"].get("cols") else 0.0
            town["placements"].append(dict(id=bid, lane=lane["id"], origin=pl["origin"], z=pl["base"], yaw=pl["yaw"], foundation=pl["quad"], low=pl["low"] - 0.5))
            add_garden(town, pl, z, hw, fp, door)
            if rnd("lit", bid) < 0.62:
                r = rnd("floors", bid)
                town["lit"].append(dict(building=bid, floors=["ground"] if r < 0.45 else (["upper"] if r < 0.75 else ["ground", "upper"]), cause="someone is home"))
            bid += 1
            s = sc + wx1

    # the café at the back of the square
    cafe = dict(id=bid, type="house", character="high_road", plot=dict(x=0, w=10000, d=8000), provenance="generated-past", events=[
        dict(id=1, year=1888, kind="built", params=dict(era="chalet", storeys=2000, wealth=600), cause="a baker builds on the new square"),
        dict(id=2, year=1931, kind="shop_fitted", params=dict(cols=2), cause="the bakery gets a shop window"),
        dict(id=3, year=1931, kind="business_opened", params=dict(kind="cafe", name="Torgkafeen"), cause="the baker's daughter opens a café"),
        dict(id=4, year=1979, kind="repainted", params={}, cause="upkeep")])
    plan = resolve(cafe, YEAR, SEED)
    ob = building.build(plan, STYLE, name="probe_cafe")
    fp, (wx0, wx1) = extents(ob)
    bpy.data.objects.remove(ob, do_unlink=True)
    pl = place(lane["points"] if False else lanes[0]["points"], lanes[0]["z"], lanes[0]["width"] / 2, (a0 + a1) / 2 - (wx0 + wx1) / 2,
               fp, setback_min=sq["depth"] + 0.2, rise_min=0.25, base_fixed=lanes[0]["z"] + 0.25)
    town["buildings"].append(cafe)
    town["placements"].append(dict(id=bid, lane="square-1", origin=pl["origin"], z=pl["base"], yaw=pl["yaw"], foundation=pl["quad"], low=pl["low"] - 0.5))
    town["pads"].append(dict(kind="house", z=pl["base"] - 0.05, corners=grow_quad(pl["quad"], 0.6)))
    town["lit"].append(dict(building=bid, floors=["ground", "upper"], cause="Torgkafeen is open late on Fridays"))

    lamps_and_trees(town, lanes, corners)
    return town


def grow_quad(q, by):
    cx = sum(p[0] for p in q) / 4
    cy = sum(p[1] for p in q) / 4
    out = []
    for x, y in q:
        dx, dy = x - cx, y - cy
        L = math.hypot(dx, dy) or 1
        out.append((x + dx / L * by * 1.41, y + dy / L * by * 1.41))
    return out


def add_garden(town, pl, lane_z, hw, fp, door):
    """The house's pad, its front garden levelled at the floor, the garden wall and steps up through it."""
    x0, x1, y0, y1 = fp
    base, yaw, origin, n = pl["base"], pl["yaw"], pl["origin"], pl["n"]
    town["pads"].append(dict(kind="house", z=base - 0.05, corners=grow_quad(pl["quad"], 0.6)))
    if pl["rise"] < 0.15:
        return
    # the garden: from the lane's edge to the house front, across the house
    edge_y = y0 - pl["setback"] + 0.05  # local y of the lane's edge
    garden = [world(origin, yaw, x, y) for x, y in ((x0 + 0.2, edge_y), (x1 - 0.2, edge_y), (x1 - 0.2, y0), (x0 + 0.2, y0))]
    town["pads"].append(dict(kind="garden", z=base - 0.02, corners=garden))
    # the wall along the lane, an opening where the steps come up to the door
    dx = min(max(door, x0 + 1.2), x1 - 1.2)
    for a, b in ((x0 + 0.2, dx - 0.8), (dx + 0.8, x1 - 0.2)):
        if b - a < 0.3:
            continue
        wall = []
        for k in range(4):
            x = a + (b - a) * k / 3
            px, py = world(origin, yaw, x, edge_y)
            wall.append([px, py, lane_z - 0.1, base + 0.35])
        town["walls"].append(dict(kind="garden", points=wall))
    # the steps: from the lane up into the garden, towards the door
    run = pl["rise"] / 0.17 * 0.29
    a = world(origin, yaw, dx, edge_y)
    b = world(origin, yaw, dx, edge_y + run)
    town["steps"].append(dict(width=1.3, points=[[a[0], a[1], lane_z], [b[0], b[1], base]]))


def lamps_and_trees(town, lanes, square):
    for li, lane in enumerate(lanes):
        pts, total = lane["points"], length(lane["points"])
        s = 10.0 + 8.0 * rnd("lamp0", li)
        k = 0
        while s < total - 6:
            (p, _, n) = frame(pts, s)
            if all(abs(p[0] - sx) > 4 for sx in STAIR_XS):
                town["lamps"].append(dict(id=f"lamp-{lane['id']}-{k}", x=p[0] + n[0] * (lane["width"] / 2 + 0.35), y=p[1] + n[1] * (lane["width"] / 2 + 0.35),
                                          z=lane["z"], variant=lane["lamp"], light="mercury" if lane["lamp"] == "pole-1965" else "warm"))
                k += 1
            s += 26.0 + 6.0 * rnd("lampgap", li, k)
    for c in (square[2], square[3]):  # two lamps at the back of the square
        cx = (square[0][0] + square[1][0] + square[2][0] + square[3][0]) / 4
        cy = (square[0][1] + square[1][1] + square[2][1] + square[3][1]) / 4
        town["lamps"].append(dict(id=f"lamp-square-{len(town['lamps'])}", x=c[0] + (cx - c[0]) * 0.18, y=c[1] + (cy - c[1]) * 0.18,
                                  z=lanes[0]["z"], variant="post-1934", light="warm"))

    def clear(x, y, r):
        for pl in town["placements"]:
            q = grow_quad(pl["foundation"], r)
            if terrain.in_quad(q, x, y):
                return False
        for lane in lanes:
            d, _, _, _ = terrain.nearest_on_polyline(lane["points"], x, y)
            if d < lane["width"] / 2 + 1.0:
                return False
        for st in town["stairs"]:
            d, _, _, _ = terrain.nearest_on_polyline([p[:2] for p in st["points"]], x, y)
            if d < st["width"] / 2 + 1.2:
                return False
        if terrain.in_quad(square, x, y):
            return False
        return True

    def tree(x, y, species, planted, cause):
        if clear(x, y, 2.5):
            town["trees"].append(dict(id=f"tree-{len(town['trees']) + 1}", species=species, x=x, y=y, planted=planted, cause=cause))

    # by the stream in the gully: a line of birch and rowan
    for k in range(8):
        y = 24 + k * 14.0
        side = 1 if k % 2 else -1
        tree(SITE["gully_x"] + side * (4.0 + 2.0 * rnd("gt", k)), y, "birch" if rnd("gs", k) < 0.7 else "rowan", 1900 + int(70 * rnd("gy", k)), "self-seeded along the stream")
    # gardens: behind the houses, between them, and in the yards behind the quay street
    for k in range(70):
        x = LANE_X[0] + (LANE_X[1] - LANE_X[0]) * rnd("tx", k)
        y = 14 + 130 * rnd("ty", k)
        r = rnd("ts", k)
        species = "sycamore" if r < 0.3 else ("birch" if r < 0.62 else ("rowan" if r < 0.84 else "spruce"))
        if rnd("tk", k) < 0.45:
            tree(x, y, species, 1880 + int(95 * rnd("tp", k)), "planted in a garden")
    # the hill above the town: birch where grazing stopped, a spruce planting
    for k in range(30):
        x = -60 + 220 * rnd("hx", k)
        y = 145 + 80 * rnd("hy", k)
        spruce = (40 < x < 100 and 160 < y < 205)
        tree(x, y, "spruce" if spruce else "birch", 1957 if spruce else 1925 + int(40 * rnd("hp", k)),
             "the spruce planting" if spruce else "birch coming up as grazing stopped")


def mm(v):
    return int(round(v * 1000))


def to_fixture(town, seed):
    out = dict(schemaVersion=2, note="The town above Harbour Row, grown by blender/tools/grow_town.py from the site facts below: a stand-in for the engine's fabric pass. Lengths in millimetres.",
               worldSeed=seed, site={k: (mm(v) if isinstance(v, float) else v) for k, v in SITE.items()}, provenance="generated-past")
    out["lanes"] = [dict(id=l["id"], name=l["name"], z=mm(l["z"]), width=mm(l["width"]), surface=l["surface"], laid=l["laid"], points=[[mm(x), mm(y)] for x, y in l["points"]]) for l in town["lanes"]]
    out["stairs"] = [dict(id=s["id"], name=s["name"], width=mm(s["width"]), points=[[mm(x), mm(y), mm(z)] for x, y, z in s["points"]]) for s in town["stairs"]]
    out["squares"] = [dict(id=q["id"], name=q["name"], z=mm(q["z"]), surface=q["surface"], laid=q["laid"], corners=[[mm(x), mm(y)] for x, y in q["corners"]]) for q in town["squares"]]
    out["pads"] = [dict(kind=p["kind"], z=mm(p["z"]), corners=[[mm(x), mm(y)] for x, y in p["corners"]]) for p in town["pads"]]
    out["walls"] = [dict(kind=w["kind"], points=[[mm(a) for a in p] for p in w["points"]]) for w in town["walls"]]
    out["steps"] = [dict(width=mm(s["width"]), points=[[mm(a) for a in p] for p in s["points"]]) for s in town["steps"]]
    out["buildings"] = town["buildings"]
    out["placements"] = [dict(id=p["id"], lane=p["lane"], x=mm(p["origin"][0]), y=mm(p["origin"][1]), z=mm(p["z"]), yaw=int(round(math.degrees(p["yaw"]) * 10)),
                              foundation=[[mm(x), mm(y)] for x, y in p["foundation"]], low=mm(p["low"])) for p in town["placements"]]
    out["lamps"] = [dict(id=l["id"], x=mm(l["x"]), y=mm(l["y"]), z=mm(l["z"]), variant=l["variant"], light=l["light"]) for l in town["lamps"]]
    out["trees"] = [dict(id=t["id"], species=t["species"], x=mm(t["x"]), y=mm(t["y"]), planted=t["planted"], cause=t["cause"]) for t in town["trees"]]
    out["lit"] = town["lit"]
    return out


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    fx = json.load(open(argv[0]))
    town = grow(fx)
    out = to_fixture(town, fx["worldSeed"])
    with open(argv[1], "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"grew {len(out['lanes'])} lanes, {len(out['stairs'])} stepped lanes, {len(out['buildings'])} houses, {len(out['lamps'])} lamps, {len(out['trees'])} trees")
