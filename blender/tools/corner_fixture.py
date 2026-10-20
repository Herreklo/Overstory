"""Write the beauty corner's fixture: fixtures/lt1-corner.json.

    python3 blender/tools/corner_fixture.py

The corner (docs/experiments.md, LT1, the reset) is authored here by hand: the stepped lane from the
quay between 104 and 105, the landing where bedrock turns it, five houses with five histories, the
wall, the lantern, the trees and the ground's own dated history, the basin's far side with its quay
row, the low land and islands beyond. The script only saves writing out heights by hand: each house's
base and each wall's top is read from the site's ground, so what stands there sits on it.

Houses marked context stand round the corner so the middle and far stops see it in a town; they are
placeholders, not part of what is judged.

Street coordinates in millimetres in the fixture: x along Harbour Row, y up the hill (negative towards
the water), z up. On the compass, +y points east-south-east (100 degrees) and +x south-south-west
(190 degrees): the town faces west-north-west over the basin.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))

import terrain  # noqa: E402

mm = lambda v: int(round(v * 1000))

# -- the site, in metres here (written in millimetres) -------------------------------------------------

SITE = dict(
    edge=-15.4,                # the quay's edge on this side of the basin
    bay_x0=-260.0, bay_x1=420.0,
    yard=12.0,                 # level behind Harbour Row's plots, then the hill
    slope=0.42, steepen=0.0,
    gully_x=49.3, gully_depth=2.0, gully_width=8.0,  # the stream the stepped lane follows down
    rough=1.4,
    side_height=24.0, side_reach=300.0,              # low hills beside the bay, not mountains
    crest=dict(z=30.0, keep=0.22),                   # the hill rounds off: a low land
    seed=1989,
    far_shore=dict(y=-125.0, quay=2.1, yard=14.0, rise=14.0, reach=150.0, depth=420.0),
    outcrops=[
        # the knuckle the lane bends round: a 4 to 5 m face towards the landing, D on top
        dict(x=59.0, y=39.0, r=7.5, face=1.3, top=12.6, sx=1.0, sy=1.15),
        # the rock step E stands on, a 2 m face under its gable where the lane ends
        dict(x=46.5, y=69.0, r=6.5, face=1.4, top=20.6, sx=1.0, sy=1.0),
        # a knoll on the far side, where the newer town has its landmark
        dict(x=125.0, y=-215.0, r=34.0, face=14.0, top=24.0, sx=1.3, sy=1.0),
        # low rocky islands in the fjord beyond
        dict(x=-380.0, y=-640.0, r=120.0, face=90.0, top=16.0, sx=1.9, sy=1.0),
        dict(x=160.0, y=-760.0, r=85.0, face=65.0, top=12.0, sx=2.3, sy=1.0),
        dict(x=560.0, y=-600.0, r=60.0, face=45.0, top=9.0, sx=1.6, sy=1.0),
        dict(x=-80.0, y=-1050.0, r=140.0, face=110.0, top=22.0, sx=2.6, sy=1.0),
    ],
)


def ground(x, y):
    return terrain.natural_z(SITE, x, y)


# -- the lane --------------------------------------------------------------------------------------------

LANE_X, LANE_W = 49.3, 3.4
# flat between A and B and their yards, the lower flight, the landing, the upper flight to E
STAIR = [(LANE_X, -0.4, 0.0), (LANE_X, 14.0, 0.0), (LANE_X, 32.0, 8.0), (46.5, 38.0, 8.0), (46.5, 44.0, 8.0),
         (46.5, 61.5, 18.4), (46.5, 64.0, 18.4)]
LANDING = [(43.0, 32.0), (51.3, 32.0), (51.3, 44.5), (43.0, 44.5)]


def lane_z(y):
    for (x0, y0, z0), (x1, y1, z1) in zip(STAIR, STAIR[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return STAIR[-1][2]


# -- diaries ---------------------------------------------------------------------------------------------

street = json.load(open(os.path.join(ROOT, "fixtures", "lt1-street.json")))
DIARY = {b["id"]: b for b in street["buildings"]}


def borrowed(src, new_id, note):
    b = json.loads(json.dumps(DIARY[src]))
    b["id"] = new_id
    b.pop("plot", None)
    b["plot"] = dict(x=0, w=DIARY[src]["plot"]["w"], d=DIARY[src]["plot"]["d"])
    b["note"] = note
    return b


A = json.loads(json.dumps(DIARY[104]))
A["events"] = [
    A["events"][0],
    dict(id=2, year=1931, kind="shop_fitted", params=dict(cols=2), cause="the cannery owner's widow lets the ground floor to the quay road as a shop"),
    dict(id=3, year=1931, kind="business_opened", params=dict(kind="ironmonger", name="Vik Jernvare"), cause="an ironmonger opens"),
    dict(id=4, year=1949, kind="repainted", params={}, cause="upkeep"),
    dict(id=5, year=1974, kind="business_closed", params={}, cause="the ironmonger retires"),
    dict(id=6, year=1988, kind="business_opened", params=dict(kind="cafe", name="Kaffebrenneriet"), cause="a young couple open a café in the empty shop; the rent is low after the crash"),
]
A["note"] = "The corner's A: kept, but faded; a new café in its old shop."

C = borrowed(203, 1203, "The corner's C: 203's diary (a cooper's house of 1879, cheap new windows in 1971), on the landing.")
D = borrowed(107, 1107, "The corner's D: 107's diary (a fisherman's house of 1828, empty since 1986), on the rock.")
E = borrowed(304, 304, "The corner's E: the oldest and smallest, closing the view up the lane.")

buildings = [A, C, D, E]
placements = []


def place(bid, ax, ay, yaw, base=None, context=False, lane="corner"):
    z = ground(ax, ay) if base is None else base
    placements.append(dict(id=bid, lane=lane, anchor=[mm(ax), mm(ay)], z=mm(z), yaw=int(round(yaw * 10)), context=context))


# C beside the landing, its front to it; D on the knuckle, its front to the landing over the rock face;
# E at the top, its gable closing the view up the lane, its front to the east
place(1203, 42.8, 38.2, 90.0, base=8.4)
place(1107, 53.2, 40.5, -90.0, base=12.65)
place(304, 49.6, 69.0, 90.0, base=20.6)

# -- context: the hill either side of the corner, and the quay row across the basin ----------------------

hill = [(201, -6.0, 24.0), (202, 8.0, 26.0), (206, 22.0, 24.5), (301, -2.0, 44.0), (302, 14.0, 45.0),
        (303, 27.0, 43.0), (205, 76.0, 25.0), (207, 90.0, 24.0), (208, 104.0, 26.0), (305, 74.0, 46.0),
        (306, 88.0, 44.0), (307, 102.0, 45.5)]
for src, x, y in hill:
    nid = 2000 + src
    buildings.append(borrowed(src, nid, f"Context on the hill: {src}'s diary."))
    place(nid, x, y, 0.0, base=ground(x, y + 3.0) - 0.4, context=True, lane="hill")

# the quay row across the basin: plots of their own widths, set back unevenly, a street leaving it at two
# gaps; behind it the newer town in a looser second row (post-war, seventies, functionalist)
far = [(101, 0.0, 1.6), (102, 0.8, 1.2), (103, 0.0, 1.4), (109, 1.6, 9.0), (105, 0.4, 1.1), (108, 0.0, 1.8),
       (107, 1.2, 1.0), (104, 0.0, 1.5), (110, 0.6, 8.0), (103, 0.0, 1.3), (102, 1.4, 1.2), (106, 0.0, 2.4), (101, 0.5, 1.6)]
fx = -40.0
for i, (src, back, gap) in enumerate(far):
    nid = 3000 + i
    w = DIARY[src]["plot"]["w"] / 1000.0
    buildings.append(borrowed(src, nid, f"Context across the basin: {src}'s diary."))
    place(nid, fx + w / 2, -131.0 - back, 180.0, base=2.1, context=True, lane="far quay")
    fx += w + gap
behind = [(106, -30.0, -158.0), (207, -8.0, -162.0), (105, 16.0, -156.0), (106, 44.0, -160.0), (207, 70.0, -157.0),
          (105, 98.0, -161.0), (106, 124.0, -158.0)]
for i, (src, x, y) in enumerate(behind):
    nid = 3100 + i
    buildings.append(borrowed(src, nid, f"Context, the newer town across the basin: {src}'s diary."))
    place(nid, x, y, 180.0, base=ground(x, y - 4.0) - 0.3, context=True, lane="far town")

# -- stonework ---------------------------------------------------------------------------------------------

wall_pts = []
for y in (9.6, 14.0, 20.0, 26.0, 31.8):
    z = lane_z(y)
    wall_pts.append([mm(47.35), mm(y), mm(z), mm(z + 1.4)])
wall_pts.append([mm(43.0), mm(31.8), mm(8.0), mm(9.4)])
walls = [dict(kind="dry_stone", points=wall_pts, cause="built with the lane's steps in the 1870s; holds the cooper's yard")]

steps = [
    # to D's door: cut along the rock face from the landing
    dict(width=1100, points=[[mm(51.0), mm(32.3), mm(8.0)], [mm(52.5), mm(38.4), mm(12.55)]]),
    # up the rock step from the lane's top to E's door
    dict(width=1200, points=[[mm(48.4), mm(63.0), mm(18.4)], [mm(51.4), mm(66.6), mm(20.6)]]),
    # to C's door, one step up from the landing
    dict(width=1300, points=[[mm(43.2), mm(38.2), mm(8.0)], [mm(42.9), mm(38.2), mm(8.4)]]),
]

# -- the ground's own history ------------------------------------------------------------------------------


def tree(tid, species, x, y, planted, cause):
    return dict(id=tid, species=species, x=mm(x), y=mm(y), planted=planted, cause=cause)


trees = [
    tree("birch-yard", "birch", 43.6, 22.0, 1950, "self-seeded in the cooper's yard"),
    tree("spruce-e", "spruce", 44.0, 77.0, 1934, "planted behind the house by the fisherman's son"),
    tree("birch-heath-1", "birch", 53.0, 80.0, 1962, "seeded on the heath after the sheep went in 1958"),
    tree("birch-heath-2", "birch", 37.0, 84.0, 1966, "seeded on the heath after the sheep went in 1958"),
    tree("birch-heath-3", "birch", 58.0, 91.0, 1971, "seeded on the heath after the sheep went in 1958"),
    tree("birch-heath-4", "birch", 46.0, 96.0, 1976, "seeded on the heath after the sheep went in 1958"),
    tree("birch-d-yard", "birch", 62.5, 45.5, 1987, "the first seedling in the empty house's yard"),
    tree("rowan-hill-1", "rowan", 1.0, 31.0, 1938, "planted in a garden"),
    tree("sycamore-hill-1", "sycamore", 84.0, 32.0, 1905, "planted in a garden"),
    tree("rowan-hill-2", "rowan", 96.0, 51.0, 1951, "planted in a garden"),
]

lamps = [dict(id="lamp-landing", x=mm(44.2), y=mm(33.0), z=mm(8.0), variant="post-1934", light="warm",
              installed=1955, cause="the council brings electric light to the lane")]

fixture = dict(
    schemaVersion=1,
    note="The beauty corner (docs/experiments.md, LT1, the reset), written by blender/tools/corner_fixture.py. "
         "Authored by hand: the lane, the five houses, the wall, the lantern, the trees and the ground's history. "
         "Context houses are placeholders round it. Lengths in millimetres.",
    worldSeed=1989,
    provenance="authored",
    fine=[mm(-40.0), mm(-16.0), mm(130.0), mm(120.0), mm(1.0)],
    coarse=[mm(-1100.0), mm(-1300.0), mm(1300.0), mm(1000.0), mm(10.0)],
    heath_above=mm(21.0),
    ground_history=[
        dict(what="heath", where="the hillside above E", year=1958, cause="the last sheep are sold; heather, juniper and birch come in"),
        dict(what="weeds", where="D's yard", year=1986, cause="the house stands empty; grass, rosebay willowherb, the first birch"),
        dict(what="wear", where="the lower flight", cause="the busy middle worn smooth; moss in the joints on the shaded side"),
        dict(what="lichen", where="the knuckle and the wall", year=1874, cause="bare since the lane was cut past the rock"),
    ],
    lanes=[],
    stairs=[dict(id="stair-corner", name="Gully Steps", width=mm(LANE_W), points=[[mm(x), mm(y), mm(z)] for x, y, z in STAIR])],
    squares=[dict(id="landing", name="the landing", z=mm(8.0), surface="setts", laid=1874, corners=[[mm(x), mm(y)] for x, y in LANDING])],
    pads=[],
    walls=walls,
    steps=steps,
    buildings=buildings,
    placements=placements,
    lamps=lamps,
    trees=trees,
    lit=[],
)


def to_mm(v):
    if isinstance(v, dict):
        return {k: (x if k == "seed" else to_mm(x)) for k, x in v.items()}
    if isinstance(v, list):
        return [to_mm(x) for x in v]
    return mm(v)


fixture["site"] = to_mm(SITE)

out = os.path.join(ROOT, "fixtures", "lt1-corner.json")
with open(out, "w") as f:
    json.dump(fixture, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"wrote {out}: {len(buildings)} buildings ({sum(1 for p in placements if not p['context'])} in the corner)")
for p in placements[:3]:
    print(p["id"], "base", p["z"] / 1000.0)
print("natural ground at the landing", round(ground(47.0, 38.0), 2), "at E", round(ground(46.5, 68.5), 2), "at the knuckle top", round(ground(59.0, 39.0), 2))
