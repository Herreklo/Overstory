"""Way P's page and strokes for a whole house: finish/paint.py's corner grown to every wall and every opening.

    Blender -b --factory-startup -P blender/parts/street/paint.py -- --gen cache/street/gen/107 --cache cache/street/bake/107
        [--out <dir>] [--since <years>]

Reads house.json (house.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, each the page's size:
  hist-p.png, hist-p2.png, paint-stroke.png, paint.json   as finish/paint.py's: the same channels and digest keys
  geo.png, street-normal.png                              as finish/marks.py's (marks.py here)
and a look at hist-p's R and G and hist-p2's R side by side, into cache/street/paint-preview/<house>.png. --out writes
elsewhere; --since sets the years since the last coat outright (the age sheet), none let go.

The corner's rules and values (finish.json `painted`, p3) are used as they are, its own functions called where they
can be; what changes is which wall, which opening and its frame. Each opening's shapes leave its own sill, head and
battens on its own wall; the sill leaks at its lower end by the frame's tilt, or, level, at the end toward the weather.
The street front is p3 (the corner is its west end); a wall less exposed to the wet winds, or painted later, takes the
corner's failed paint scaled down by its wear against the front's (paint.json `wear`), never up. The roof's tiles take
their values tile by tile. No shape claims a dated event (UK4).
"""

import copy
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FINISH = os.path.join(HERE, "..", "finish")
sys.path.insert(0, FINISH)
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402


def module(path, name):
    """A script as a module of its own name, its main left unrun (each guards its main)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FP = module(os.path.join(FINISH, "paint.py"), "finish_paint")  # the corner's shapes; it loads the corner's marks
MK = FP.MK
SM = module(os.path.join(HERE, "marks.py"), "street_marks")
key, field, wave, junction = MK.key, FP.field, FP.wave, FP.junction


# ---------------------------------------------------------------- the facts that grade the wear


def toward_weather(paints):
    """Toward where the wet winds come from (paints.json weather), in the pack's frame (x east, y north), which is the
    house's: its street front, -y, faces south."""
    a = math.radians(paints["weather"]["fromDeg"])
    return np.array([math.sin(a), math.cos(a)])


def exposure(wall, paints):
    """How squarely a wall faces the wet winds: 1 facing them, `least` on the lee."""
    W = paints["weather"]
    return W["least"] + (1.0 - W["least"]) * max(0.0, float(np.dot(wall["out"], toward_weather(paints))))


def coats(meta, paints, since):
    """The paint's age (paints.json upkeep): painted in `since` (the house's building, or the lean-to's), then every
    cycle (by the house's wealth) until a neglect or a boarding stops it, its last coat the cycle's last turn before
    that year, or a 'repainted' event's. Returns the years since that coat, the years let go, and the cycle. An age
    sheet's `coatAge` (paint.py --since) sets the years since the coat outright, none let go."""
    lo, hi = paints["upkeep"]["cycleYears"]
    cyc = lo + (hi - lo) * min(max(meta["wealth"] / 1000.0, 0.0), 1.0)
    if "coatAge" in meta:
        return meta["coatAge"], 0, cyc
    stops = [e["year"] for e in meta["events"] if e["kind"] in ("neglected", "boarded") and e["year"] <= meta["year"]]
    stop = min(stops) if stops else meta["year"]
    last = since + max(0, math.floor((stop - since) / cyc - 1e-9)) * cyc
    last = max([last] + [e["year"] for e in meta["events"] if e["kind"] == "repainted" and e["year"] <= meta["year"]])
    return meta["year"] - last, (meta["year"] - stop) if stops else 0, cyc


def wear(meta, paints, wall):
    """How far a wall's paint has gone: (years since its last coat + years let go) / the cycle, times its exposure."""
    since = meta["leanTo"]["year"] if wall["kind"] == "lean" else meta["built"]
    age, neglected, cyc = coats(meta, paints, since)
    return (age + neglected) / cyc * exposure(wall, paints)


def grade(meta, paints, walls, floor):
    """Each wall's share of the corner's failed paint: its wear against the floor's (p3 is house 107's street front
    in 1989, its wear `floor`), at most 1, so no wall fails more than the floor."""
    return {i: min(1.0, wear(meta, paints, w) / floor) for i, w in walls.items()}


def chalk(pg, C, w):
    """The paint's own age over the whole wall, a wash in L* (greyer and darker, the wash's tint): the binder gone to
    powder and the dirt held in it, from a wear of `from` to full at `full`."""
    return np.where((pg.m["cladding"] | pg.m["trims"]) & pg.vertical, C["wash"] * FL.smoothstep(C["from"], C["full"], w), 0.0)


def leak_side(o, wall, paints, A):
    """Which end of an opening leaks (-1 its start, +1 its end): the sill's lower end, z rising by `tilt` a metre along
    the wall (house.py); a level sill, or a door, at the end toward the weather."""
    t = o.get("tilt", 0.0)
    if "sill" in o and abs(t) >= A["level"]:
        return 1.0 if t < 0 else -1.0
    return 1.0 if float(np.dot(wall["dir"], toward_weather(paints))) > 0 else -1.0


def floor_of(meta, o, wall):
    """Where the water off an opening stops running down its wall: the drip board (`heights.drip`) on the house, the
    lean-to's lowest butt, or the top of an opening below it, whose cap takes it."""
    sx0, sx1 = (o.get("sill") or o["casing"])[:2]
    below = [p["casing"][3] for p in meta["openings"] if p is not o and p["wall"] == o["wall"]
             and p["casing"][3] <= o["casing"][2] and p["casing"][0] < sx1 + 0.3 and p["casing"][1] > sx0 - 0.3]
    if below:
        return [max(below)] * 2
    if wall["kind"] == "lean":
        return [meta["courses"][str(wall["group"])][0]] * 2
    return meta["heights"]["drip"]


def opening_meta(meta, o, k, wall, cap_t):
    """The corner's meta for one opening, so the corner's shapes read it: its own features (a door's sill stands at
    its casing), its wall's courses and butt joints, the floor its water runs to (as `heights.drip`) and its head;
    seeds of its own (`house` names the opening)."""
    cx0, cx1, cz0, cz1 = o["casing"]
    f = {"sill": o.get("sill") or [cx0, cx1, cz0, 0.0], "casing": o["casing"], "sheets": o.get("sheets"),
         "battens": o.get("battens", []), "nails": o.get("nails", []), "opening": [o["a0"], o["a1"]],
         "joints": [("street", a, zb, zt) for w, a, zb, zt in meta["features"]["joints"] if w == wall["i"]]}
    return {"world": meta["world"], "house": f"{meta['house']}/open{k}", "courses": meta["courses"][str(wall["group"])],
            "features": f, "heights": {"drip": floor_of(meta, o, wall), "head": cz1 - cap_t}}


def graded(Q, g, om, door):
    """The corner's failed paint on a wall at share `g` (grade): at 1 the corner's own; below, its washes and runs'
    strengths, its peel's heights and the casing's peel reach times g, the tongue's runs ending sooner and the runs
    crossing fewer laps. A door has no sill: only the head's run and its battens' runs."""
    if g >= 1.0 and not door:
        return Q
    q = copy.deepcopy(Q)
    T = q["tongue"]
    f, h = om["features"], om["heights"]
    spans = {"leak": f["sill"][2] - h["drip"][0], "dry": f["sill"][2] - h["drip"][0], "cap": h["head"] - f["casing"][2]}
    if door:
        T["runs"] = {"cap": T["runs"]["cap"]}
        for kind in ("leak", "dry"):
            T["runoff"][kind]["boards"] = 0
    if g >= 1.0:
        return q
    for name, R in T["runs"].items():
        R["L"] *= g
        R["peel"] = [[w, ht * g] for w, ht in R["peel"]]
        R["length"] = (R["length"] or spans[name]) * g
    for kind in ("leak", "dry", "batten"):
        S = T["runoff"][kind]
        S["strength"] *= g
        if S["boards"]:
            S["boards"] = max(1, int(round(S["boards"] * g)))
        S["flake"] = [S["flake"][0], S["flake"][1] * g]
    q["peel"]["casing"]["reach"] *= g
    return q


# ---------------------------------------------------------------- the failed paint


def peel_casing(pg, Q, meta, side):
    """The corner's peel at the casing's leaking leg, at its foot on the sill; the leg's inner edge the sheets', as the
    corner's, or the opening's."""
    R = Q["peel"]
    f = meta["features"]
    W = R["wobble"]
    cx0, cx1, cz0, _ = f["casing"]
    ax0, ax1 = (f["sheets"] or f["opening"])[:2]
    leg = (cx0 - 0.01, ax0) if side < 0 else (ax1, cx1 + 0.01)
    on = pg.m["trims"] & pg.vertical & (pg.along > leg[0]) & (pg.along < leg[1]) & (pg.z >= cz0 - 0.005)
    edge = cz0 + R["casing"]["reach"] * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, key(meta, "p-casing"), W["cell"], pg.z)))
    return np.where(on, field(edge - pg.z, R["soft"]), 0.0)


def peel_tops(pg, Q, k, length):
    """The corner's ledges' tops, standing wet: bare but at their ends, where what they meet keeps them; a top that
    reaches the wall's corner runs on round it, as the corner's ran on at its sample's edges."""
    R = Q["peel"]
    a0p, a1p = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    ins = R["tops"]["inset"] * (1.0 + 0.5 * wave(pg, k, R["wobble"]["cell"]))
    d0 = np.where(a0p <= 0.01, np.inf, pg.along - a0p - ins)
    d1 = np.where(a1p >= length - 0.01, np.inf, a1p - pg.along - ins)
    d = np.minimum(np.minimum(d0, d1), 1.0)
    return np.where(pg.m["trims"] & pg.up, field(d, R["soft"]), 0.0)


def opening_stains(pg, Q, meta, side):
    """The corner's stains an opening's facts place: rust under some of its battens' nails, down the batten and the
    casing below; the boarding's damp strip down its leaking side."""
    f = meta["features"]
    out = np.zeros(pg.shape)
    Ru = Q["rust"]
    k = key(meta, "p-rust")
    iron = (pg.m["trims"] | pg.m["batten"]) & (pg.y < 0.0)
    for i, (xn, zn) in enumerate(f["nails"]):
        if HS.unit(HS.h(k, i)) >= Ru["share"]:
            continue
        ln = Ru["length"][0] + (Ru["length"][1] - Ru["length"][0]) * HS.unit(HS.h(k, i, "len"))
        out = np.maximum(out, FP.run(pg, HS.h(k, i, "w"), xn, zn, ln, Ru["width"], 0.002, iron))
    B = Q["sheet"]
    if f["sheets"] and B["leakWidth"] > 0.0:
        ab0, ab1 = f["sheets"][:2]
        from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
        sd = B["leakWidth"] + B["wobble"]["amp"] * wave(pg, key(meta, "p-sheet", "leak"), B["wobble"]["cell"], pg.z) - from_leak
        out = np.maximum(out, np.where(pg.m["sheet"], field(sd, 0.04), 0.0))
    return out


def splash(pg, Q, P, S, wall, meta):
    """The foot's wetting along a wall, as the corner's broad splash: one broad swell under each of its drips by how
    much it carries (a gutter's leaking joint, the downpipe's shoe); with none, a gable's verge run-off, even, and the
    lean-to's gutterless low eave its whole length."""
    ds = [d for d in meta["features"]["drips"] if d[0] == wall["i"]]
    if ds:
        broad = np.zeros(pg.shape)
        for _, x, flow, _ in ds:
            broad = np.maximum(broad, flow * MK.gauss(pg.along - x, Q["wet"]["splashWidth"]))
        return broad
    eave = wall["kind"] == "lean" and abs(wall["dir"][0]) > 0.9
    return np.full(pg.shape, S["splash"]["leanEave"] if eave else P["marks"]["splash"]["gable"])


def wet_margin(pg, Q, meta, broad, plinth):
    """The plinth's wet margin (the corner's): splash keeps its foot wet, higher where the splash is, its top a
    wavering found edge."""
    Wt = Q["wet"]
    if "L" in Wt:
        return np.zeros(pg.shape)
    top = Wt["top"] + Wt["splash"] * broad + Wt["wobble"]["amp"] * wave(pg, key(meta, "p-wet", meta["wall"]), Wt["wobble"]["cell"])
    return np.where(plinth, field(top - pg.z, Wt["soft"]), 0.0)


# ---------------------------------------------------------------- the values


def wall_low(pg, Q, clad, zf):
    """How low on its wall each point is, 0 under the eave (or the verge) to 1 at the boards' foot, eased by the
    gradient's power; and the wall's top above each point."""
    top = FP.edges(pg, clad)
    t = np.clip((pg.z - zf) / np.maximum(top - zf, 0.1), 0.0, 1.0)
    return (1.0 - t) ** Q["wall"]["power"], top


def wall_values(pg, Q, zf, z_plinth, broad):
    """The corner's broad washes on one wall: its one gradient, light at its top and darkening steadily to its foot;
    under the eave a soft contact band; the plinth darker toward the ground, its top under the drip board dark."""
    dl = np.zeros(pg.shape)
    clad = pg.m["cladding"] & pg.vertical
    wall = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    plinth = (pg.m["stone"] | pg.m["concrete"]) & pg.vertical
    low, top = wall_low(pg, Q, clad, zf)
    Wl = Q["wall"]
    dl += np.where(wall, Wl["topL"] + (Wl["footL"] - Wl["topL"]) * low, 0.0)
    E = Q["eave"]
    d = top - pg.z
    dl -= np.where(wall & (d >= -0.002), E["L"] * (1.0 - FL.smoothstep(0.0, E["reach"], d)) ** E["power"], 0.0)
    Pl = Q["plinth"]
    dl -= np.where(plinth, Pl["L"] * (1.0 - np.clip(pg.z / z_plinth, 0.0, 1.0)), 0.0)
    dl -= np.where((pg.m["stone"] | pg.m["concrete"]) & pg.up, Pl.get("capL", 0.0), 0.0)
    Wt = Q["wet"]
    if "L" in Wt:
        wet = 1.0 - FL.smoothstep(-Wt["soft"], Wt["soft"], pg.z - Wt["top"] - Wt["splash"] * broad)
        dl -= np.where(plinth, Wt["L"] * wet, 0.0)
    return dl, top, low


def severity(meta, paints, wall, N):
    """How far a wall has gone to neglect, 0..1: its wear (paint's age and years let go against the cycle, by its
    exposure) and the neglect's own amount, eased from `from` to `full` (paint.json neglect)."""
    amount = sum(e["params"].get("amount", 0) for e in meta["events"] if e["kind"] == "neglected" and e["year"] <= meta["year"])
    w = wear(meta, paints, wall) + N["amount"] * amount / 1000.0
    return float(FL.smoothstep(N["from"], N["full"], w))


def neglect_values(pg, N, k, s, sills, top, zf):
    """A neglected wall's broad shapes, what reads from the street stop and beyond: a long soft tongue of grey under
    each sill, the upper wall grey under the eave's drip, the foot grey from the splash; their edges found, freehand.
    Each at `s` (severity) of its full strength."""
    clad = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    dl = np.zeros(pg.shape)
    if s <= 0.0:
        return dl
    Sl = N["sill"]
    for j, (sx0, sx1, z_sill, _) in enumerate(sills):
        below = np.clip(z_sill - pg.z, 0.0, None)
        reach = Sl["reach"] * (1.0 + Sl["wobble"] * wave(pg, HS.h(k, "sill", j), Sl["cell"]))
        hw = (sx1 - sx0) / 2.0 + Sl["spread"] * below
        across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sl["soft"])
        fall = (1.0 - FL.smoothstep(0.0, 1.0, below / np.maximum(reach, 0.1))) ** Sl["power"]
        dl -= np.where(clad & (pg.z < z_sill), Sl["L"] * across * fall, 0.0)
    Ev = N["eave"]
    d = top - pg.z
    edge = Ev["reach"] * (1.0 + Ev["wobble"] * wave(pg, HS.h(k, "eave"), Ev["cell"]))
    dl -= np.where(clad, Ev["L"] * (1.0 - FL.smoothstep(0.0, 1.0, d / np.maximum(edge, 0.1))) ** Ev["power"], 0.0)
    Ft = N["foot"]
    h = pg.z - zf
    edge = Ft["reach"] * (1.0 + Ft["wobble"] * wave(pg, HS.h(k, "foot"), Ft["cell"]))
    dl -= np.where(clad, Ft["L"] * (1.0 - FL.smoothstep(0.0, 1.0, h / np.maximum(edge, 0.1))) ** Ft["power"], 0.0)
    return s * dl


def opening_values(pg, Q, meta, side, board):
    """The corner's broad washes an opening places: a soft wash widening under its sill; its boarding holding water,
    darkest at its head, down its leaking side and at the sill, in one soft wash, with a band of its own above the lower
    batten."""
    f = meta["features"]
    dl = np.zeros(pg.shape)
    sx0, sx1, z_sill, _ = f["sill"]
    Sw = Q["sillWash"]
    if Sw["L"]:
        below = np.clip(z_sill - pg.z, 0.0, None)
        hw = (sx1 - sx0) / 2.0 + Sw["spread"] * below
        across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sw["soft"])
        fall = (1.0 - np.clip(below / Sw["reach"], 0.0, 1.0)) ** 1.5
        dl -= np.where(pg.m["cladding"] & pg.vertical & (pg.z < z_sill), Sw["L"] * across * fall, 0.0)
    if not f["sheets"]:
        return dl
    Bw = board["wash"]
    sheet = pg.m["sheet"]
    ab0, ab1, zb0, zb1 = f["sheets"][:4]
    from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
    head = (1.0 - FL.smoothstep(0.0, Bw["head"], zb1 - pg.z)) * (1.0 - 0.5 * np.clip(from_leak / (ab1 - ab0), 0, 1))
    lk = 1.0 - FL.smoothstep(0.0, Bw["leak"], from_leak)
    bx0, bx1, zc, slope, bw = f["battens"][0]
    zl = zc + slope * (pg.along - (bx0 + bx1) / 2.0) + bw / 2.0
    lowness = np.clip(0.5 - np.sign(slope) * (pg.along - (bx0 + bx1) / 2.0) / max(bx1 - bx0, 1e-3), 0.0, 1.0)
    bat = np.where(pg.z > zl - 0.01, 1.0 - FL.smoothstep(0.0, Bw["batten"] * (1.0 + Bw["lowEnd"] * lowness), pg.z - zl), 0.0)
    sill = 1.0 - FL.smoothstep(0.0, Bw["sill"], pg.z - zb0)
    wash = 1.0 - (1.0 - head) * (1.0 - lk) * (1.0 - 0.6 * sill)
    dl -= np.where(sheet, np.maximum(Bw["L"] * wash, Bw["batL"] * bat), 0.0)
    Pb = board.get("blotch")
    if Pb:
        k = key(meta, "p-blotch")
        st = Pb.get("stretch", 1.0)  # taller than wide: the water hangs from the head and runs down the ply
        n = sum(a * FL.noise2(pg.along / c, pg.z / (c * st), HS.h(k, j)) for j, (c, a) in enumerate(Pb["octaves"])) / sum(a for _, a in Pb["octaves"])
        lowS = np.clip((zb1 - pg.z) / max(zb1 - zb0, 1e-3), 0.0, 1.0)
        dl -= np.where(sheet, Pb["L"] * FL.smoothstep(Pb["cut"] - Pb["soft"], Pb["cut"] + Pb["soft"], n + Pb["low"] * (lowS - 0.5)), 0.0)
    return dl


def down(v, dl, base, mask, d, J, to="to"):
    """A junction's dark (the corner's) on a view: the value drawn down to J[to] at the junction, easing back over
    J's reach, from what the paint is there now."""
    v.put(dl, -np.where(mask, junction(d, v.get(base) + v.get(dl), J[to], J["reach"]), 0.0), "add")


def opening_junctions(v, Q, meta, dl, base, battens):
    """The darks an opening's facts place: under its sill, under each of its battens (onto the trims and the sheet),
    under its head on the sheet."""
    J = Q["junction"]
    f = meta["features"]
    clad = v.m["cladding"] & v.vertical
    if f["sill"][3] > 0.0:
        sx0, sx1, z_sill, _ = f["sill"]
        down(v, dl, base, clad & (MK.soft_box(v.along, sx0, sx1, 0.015) > 0.5), z_sill - v.z, J["sill"])
    wall = (v.m["cladding"] | v.m["trims"]) & v.vertical
    for i in battens:
        b = (v.piece == i) & v.vertical
        if not b.any():
            continue
        foot_b = FP.edges(v, b, top=False)
        a0, a1 = v.along[b].min(), v.along[b].max()
        under = (v.along > a0) & (v.along < a1)
        dB = foot_b - v.z
        onto = wall if J["batten"].get("clad", True) else v.m["trims"] & v.vertical
        down(v, dl, base, onto & ~b & under, dB, J["batten"])
        down(v, dl, base, v.m["sheet"] & under, dB, J["batten"], "sheetTo")
    if f["sheets"]:
        down(v, dl, base, v.m["sheet"], f["sheets"][3] - v.z, J["head"])


def opening_small(pg, Q, meta):
    """The small an opening places: its battens' end grain and the nails' heads, its sheets' join, a dark seam."""
    f = meta["features"]
    dl = np.zeros(pg.shape)
    Bt = Q["batten"]
    bat = pg.m["batten"]
    for bx0, bx1, zc, slope, w in f["battens"]:
        zl = pg.z - (zc + slope * (pg.along - (bx0 + bx1) / 2.0))
        on = bat & (np.abs(zl) <= w / 2.0 + 0.03) & (pg.along > bx0 - 0.05) & (pg.along < bx1 + 0.05)
        ends = np.minimum(np.abs(pg.along - bx0), np.abs(bx1 - pg.along))
        dl -= np.where(on, Bt["endL"] * FL.smoothstep(Bt["endMm"] / 1000.0, 0.0, ends), 0.0)
    Ru = Q["rust"]
    r_head = Ru["headMm"] / 1000.0
    for xn, zn in f["nails"]:
        r = np.hypot(pg.along - xn, pg.z - zn)
        dl -= np.where(bat, Ru["headL"] * FL.smoothstep(r_head, 0.6 * r_head, r), 0.0)
    sheet = pg.m["sheet"]
    if sheet.any():
        B = Q["sheet"]
        z0, z1 = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
        zs0, zs1 = pg.z[sheet].min(), pg.z[sheet].max()
        dj = np.minimum(np.where(z1 >= zs1 - 0.01, np.inf, z1 - pg.z), np.where(z0 <= zs0 + 0.01, np.inf, pg.z - z0))
        dl -= np.where(sheet, B["joinL"] * FL.smoothstep(B["joinMm"] / 1000.0, 0.0, dj), 0.0)
    return dl


def tile_values(pg, Q, meta, roof):
    """The roof one dark mass, a few of its tiles catching more light, tile by tile: each cell of `cover` along its
    eave by `course` up its slope from the foot (features.roof), so a plane that stands for many tiles lights its own
    few. Off any slope (the ridge), by piece, as the corner's."""
    T = Q["tiles"]
    tiles = pg.m["tiles"] | pg.m["roof"] | pg.m["slate"]
    if roof is None:
        cell = (pg.piece, 0, 0)
    else:
        a = math.radians(roof["pitch"])
        # up the slope from its foot, in the eave wall's own frame (y back from its face), as the foot is given
        s = (pg.y - roof["foot"][0]) * math.cos(a) + (pg.z - roof["foot"][1]) * math.sin(a)
        cell = (np.floor(s / roof["course"]).astype(np.int64), np.floor((pg.along - roof["x0"]) / roof["cover"]).astype(np.int64),
                np.full(pg.shape, roof["wall"]))
    u = FL.unit(key(meta, "p-tile"), *cell)
    v = FL.unit(key(meta, "p-tile-v"), *cell)
    return np.where(tiles & (u < T["share"]), T["L"] * (0.5 + 0.5 * v), 0.0)


def roof_years(meta):
    """Years the roof has weathered: since it was built, or since it was last retiled."""
    since = max([meta["built"]] + [e["year"] for e in meta["events"] if e["kind"] == "roof_retiled" and e["year"] <= meta["year"]])
    return meta["year"] - since


def roof_values(pg, R, meta, roof, wall):
    """A slope's age in broad shapes, never tile by tile: the eave course darkest, where the water stands longest and
    the dirt off the slope gathers; moss and lichen down the pans from the ridge, where the water runs, each pan's
    reach its own; the shaded slope darker all over. All at the roof's age (`fullYears` to full)."""
    tiles = pg.m["tiles"] | pg.m["roof"] | pg.m["slate"]
    age = float(FL.smoothstep(0.0, R["fullYears"], roof_years(meta)))
    if age <= 0.0:
        return np.zeros(pg.shape)
    k = key(meta, "p-roof", roof["wall"])
    a = math.radians(roof["pitch"])
    s = (pg.y - roof["foot"][0]) * math.cos(a) + (pg.z - roof["foot"][1]) * math.sin(a)
    top = roof["courses"] * roof["course"]
    E = R["eave"]
    reach = E["courses"] * roof["course"] * (1.0 + E["wobble"] * wave(pg, HS.h(k, "eave"), E["cell"]))
    dl = -E["L"] * (1.0 - FL.smoothstep(0.0, 1.0, s / np.maximum(reach, 0.05))) ** E["power"]
    M = R["moss"]
    u = (pg.along - roof["x0"]) / roof["cover"]
    col = np.floor(u).astype(np.int64)
    pan = u - col - roof["pan"]
    lane = MK.gauss(pan - np.round(pan), M["width"])
    lc = top * (M["reach"][0] + (M["reach"][1] - M["reach"][0]) * FL.unit(k, col))
    lc = lc * (1.0 + M["wobble"] * wave(pg, HS.h(k, "moss"), M["cell"], s))
    dl -= M["L"] * lane * (1.0 - FL.smoothstep(0.0, 1.0, (top - s) / np.maximum(lc, 0.05))) ** M["power"]
    south = np.array([0.0, -1.0])
    sunward = max(0.0, float(np.dot(wall["out"], south)))
    dl -= R["shadeL"] * (1.0 - sunward)
    return np.where(tiles, age * dl, 0.0)


def roof_marks(pg, R, meta, roof, wall):
    """A slope's age in the colour as well as the value: its lower share greyer and darker (a wash: the water stands
    longest there and the dirt off the slope gathers), a streak down the slope under the chimney (its soot and the
    water off its flashing), and lichen in patches on the top courses, thinning down the slope (the stain: paler,
    grey-green). At the roof's age, as roof_values. Returns (wash in L*, stain 0..1)."""
    tiles = pg.m["tiles"] | pg.m["roof"] | pg.m["slate"]
    age = float(FL.smoothstep(0.0, R["fullYears"], roof_years(meta)))
    wash, sn = np.zeros(pg.shape), np.zeros(pg.shape)
    if age <= 0.0:
        return wash, sn
    k = key(meta, "p-roofmarks", roof["wall"])
    a = math.radians(roof["pitch"])
    s = (pg.y - roof["foot"][0]) * math.cos(a) + (pg.z - roof["foot"][1]) * math.sin(a)
    top = roof["courses"] * roof["course"]
    Lo = R["lower"]
    edge = top * Lo["share"] * (1.0 + Lo["wobble"] * wave(pg, HS.h(k, "lower"), Lo["cell"]))
    wash += Lo["wash"] * (1.0 - FL.smoothstep(edge - top * Lo["soft"], edge + top * Lo["soft"], s))
    ch = meta["features"].get("chimney")
    if ch:
        C = R["chimney"]
        ca = (np.asarray(ch[:2]) - np.asarray(wall["origin"])) @ np.asarray(wall["dir"])
        hw = ch[2] / 2.0 + C["spread"] * np.clip(top - s, 0.0, None)
        across = MK.soft_box(pg.along - ca, -hw, hw, C["soft"])
        down = 1.0 - (1.0 - C["fade"]) * np.clip((top - s) / top, 0.0, 1.0)
        wash = np.maximum(wash, C["wash"] * across * down)
    sn = lichen(pg, R["lichen"], k, (top - s) / top, age)
    return np.where(tiles, age * wash, 0.0), np.where(tiles, sn, 0.0)


def lichen(pg, Lc, k, depth, age):
    """Lichen's patches, a stain 0..1 whose edge is at 0.5: seeded rosettes over `octaves` ([cell m, weight]), many on
    the top courses (depth 0 at the ridge, 1 at the eave) and fewer down the slope, more of them the older the roof."""
    O = Lc["octaves"]
    n = sum(w * FL.noise2(pg.along / c, pg.z / c, HS.h(k, "lichen", j)) for j, (c, w) in enumerate(O)) / sum(w for _, w in O)
    thr = Lc["cut"] + Lc["down"] * np.clip(depth, 0.0, 1.0) + (1.0 - age) * 0.5
    return FL.smoothstep(thr - Lc["soft"], thr + Lc["soft"], n)


def grime(pg, Q, low, sills):
    """The lap grime's strength on a wall's boards: everywhere some, more down its gradient and on the courses each
    sill drips on."""
    L = Q["lap"]
    sill = np.zeros(pg.shape)
    for sx0, sx1, z_sill, _ in sills:
        sill = np.maximum(sill, MK.soft_box(pg.along, sx0 - 0.1, sx1 + 0.1, L["sillSoft"]) * MK.soft_box(pg.z, z_sill - 0.35, z_sill, L["sillSoft"]))
    a = L["base"] + L["foot"] * low + L["sill"] * sill
    return np.where(pg.m["cladding"] & pg.vertical, np.clip(a, 0.0, 1.0), 0.0)


# ---------------------------------------------------------------- the digest's colours


def house_paint(meta, paints):
    """The paint the house wears (paints.json): a 'repainted' event's, else its era's default; its trims' with it."""
    D = paints["defaults"]
    ev = [e for e in meta["events"] if e["kind"] == "repainted" and e["year"] <= meta["year"] and e["params"].get("wall")]
    if ev:
        wall = ev[-1]["params"]["wall"]
        return paints["paints"][wall], paints["paints"][D["repaint"].get(wall, D[meta["era"]]["trim"])]
    d = D["warehouse"] if meta["type"] == "warehouse" else D[meta["era"]]
    return paints["paints"][d["wall"]], paints["paints"][d["trim"]]


def preview(path, pl, dl, wash, rng, washL):
    """hist-p's R and G and hist-p2's R side by side, each at half the page, to look at."""
    half = lambda a: a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2).mean(axis=(1, 3))  # noqa: E731
    panels = [half(pl), half(0.5 + np.clip(dl, -rng, rng) / (2.0 * rng)), half(np.clip(wash / washL, 0.0, 1.0))]
    img = np.concatenate(panels, axis=1)
    FL.write(path, np.repeat(img[..., None], 3, axis=-1))


# ---------------------------------------------------------------- the house


def main():
    a = MK.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "house.json")))
    if a.get("since"):
        meta["coatAge"] = float(a["since"])
    P = json.load(open(os.path.join(FL.ROOT, "blender", "parts", "finish", "finish.json")))
    S = json.load(open(os.path.join(HERE, "paint.json")))
    St = json.load(open(os.path.join(HERE, "street.json")))
    paints = json.load(open(os.path.join(FL.ROOT, St["paints"])))
    W = json.load(open(os.path.join(FL.ROOT, St["eras"][meta["era"]])))
    Q = P["painted"]
    A = S["wear"]
    bake = json.load(open(os.path.join(cache, "bake.json")))
    out = os.path.abspath(a["out"]) if a.get("out") else os.path.join(cache, "out")
    os.makedirs(out, exist_ok=True)
    pg = SM.Page(cache, meta, bake["mats"])
    pad = meta["page"]["padPx"]
    board = S["boarding"] if "boarding" in S and not a.get("boarding") else FP.boarding(Q, a.get("boarding"))
    cap_t = W["casing"]["capMm"] / 1000.0 * W["push"]["capThick"]
    T = Q["tongue"]

    # every material's paint value: the corner's, the boarding's kept variant, and paint.json's for the rest
    extra = {k: v for k, v in S["materials"].items() if k != "describes"}
    mats = dict(Q["materials"], sheet=board["sheet"], batten=board["batten"])
    # a name takes that material's values; {"like": name, ...} takes them with its own over them
    mats.update({k: (dict(mats[v]) if isinstance(v, str) else
                     dict(mats[v["like"]], **{f: x for f, x in v.items() if f != "like"}) if "like" in v else v)
                 for k, v in extra.items()})
    # the wall's value is its paint's: the clay's, scaled by the house paint's L* against the paint the clay was set for
    wp, tp_ = house_paint(meta, paints)
    k = wp["L"] / paints["paints"][S["clayPaint"]["paint"]]["L"]
    mats["cladding"] = dict(mats["cladding"], L=round(mats["cladding"]["L"] * k, 1))

    pl, sn, dl, gr = (np.zeros(pg.shape) for _ in range(4))
    wash, far = np.zeros(pg.shape), np.zeros(pg.shape)
    walls = {w["i"]: w for w in meta["walls"]}
    views = {i: SM.View(pg, pg.wall == i, w) for i, w in walls.items()}
    grades = grade(meta, paints, walls, A["floor"])
    roofs = {r["wall"]: r for r in meta["features"]["roof"]}
    log = []

    # each opening on its own wall, the other openings' pieces left out of its view
    ops = []
    for k, o in enumerate(meta["openings"]):
        wall = walls[o["wall"]]
        mine = [pc["i"] for pc in meta["pieces"] if pc["kind"] == f"open{k}"]
        others = [pc["i"] for pc in meta["pieces"] if pc["kind"].startswith("open") and pc["kind"] != f"open{k}"]
        v = SM.View(pg, (pg.wall == wall["i"]) & ~np.isin(pg.piece, others), wall)
        om = opening_meta(meta, o, k, wall, cap_t)
        side = leak_side(o, wall, paints, A)
        g = grades[wall["i"]]
        door = "sill" not in o
        ops.append((k, o, wall, v, om, side, g, door, mine))
        log.append(f"open{k} w{wall['i']} {o['kind']} {'+' if side > 0 else '-'}")

    # the failed paint, the corner's: each opening's runs, its tongue, its casing's peel and its stains; each wall's
    # tops and its plinth's wet margin
    for k, o, wall, v, om, side, g, door, mine in ops:
        q = graded(Q, g, om, door)
        if g >= A["from"]["runoff"]:
            pt, ws, fr, st = FP.runoff(v, q["tongue"], om, side)
            if g >= A["from"]["tongue"]:
                tp, tw = FP.tongue(v, q, om, side)
                pt = np.maximum(pt, tp)
                ws = np.maximum(ws, tw)
            v.put(pl, pt)
            v.put(wash, ws)
            v.put(far, fr)
            v.put(sn, st)
        if g >= A["from"]["peel"] and not door:
            v.put(pl, peel_casing(v, q, om, side))
        v.put(sn, opening_stains(v, Q, om, side))
    broads = {}
    for i, v in views.items():
        wall = walls[i]
        vm = {"world": meta["world"], "house": meta["house"], "wall": i}
        if grades[i] >= A["from"]["peel"]:
            v.put(pl, peel_tops(v, Q, key(meta, "p-tops", i), wall["length"]))
        broads[i] = splash(v, Q, P, S, wall, meta)
        ck = chalk(v, A["chalk"], wear(meta, paints, wall))
        v.put(wash, np.maximum(v.get(wash), ck))
        v.put(far, np.maximum(v.get(far), ck))
        plinth = (v.m["stone"] | v.m["concrete"] | (v.m["render"] & (v.z < meta["heights"]["plinth"] + 0.1))) & v.vertical
        v.put(sn, wet_margin(v, Q, vm, broads[i], plinth))
    painted = pg.m["cladding"] | pg.m["trims"]
    pl = np.where(painted, pl, 0.0)

    # the values: broad washes first, each wall's and each opening's; then the contact shade; then the darks at
    # every junction, from what the paint is there; then the small
    lows = {}
    for i, v in views.items():
        wall = walls[i]
        lean = wall["kind"] == "lean"
        zf = meta["courses"]["1"][0] if lean else meta["heights"]["drip"][1]
        z_pl = zf if lean else meta["heights"]["plinth"]
        d, top, low = wall_values(v, Q, zf, z_pl, broads[i])
        v.put(dl, d, "add")
        lows[i] = (zf, top, low)
    for k, o, wall, v, om, side, g, door, mine in ops:
        v.put(dl, opening_values(v, Q, om, side, board), "add")
    N = S["neglect"]
    for i, v in views.items():
        sills = [om["features"]["sill"] for k, o, wall, ov, om, side, g, door, mine in ops if wall["i"] == i and not door]
        sv = severity(meta, paints, walls[i], N)
        log.append(f"w{i} severity {sv:.2f}")
        v.put(dl, neglect_values(v, N, key(meta, "p-neglect", i), sv, sills, lows[i][1], lows[i][0]), "add")
    dl += np.where((pg.m["trims"] | pg.m["stone"] | pg.m["batten"]) & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        if name in pg.m:
            own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * (C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
                 + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)))
    base = np.zeros(pg.shape)
    for name, m in mats.items():
        if name in pg.m:
            base = np.where(pg.m[name], m["L"] - m.get("stainDL", 0.0) * (sn > 0.5), base)
    J = Q["junction"]
    for i, v in views.items():
        wall = (v.m["cladding"] | v.m["trims"]) & v.vertical
        down(v, dl, base, wall, lows[i][1] - v.z, J["eave"])
    for k, o, wall, v, om, side, g, door, mine in ops:
        opening_junctions(v, Q, om, dl, base, [i for i in mine if meta["pieces"][i]["mat"] == "batten"])
    for i, v in views.items():
        lean = walls[i]["kind"] == "lean"
        zf = lows[i][0]
        clad = v.m["cladding"] & v.vertical
        plinth = (v.m["stone"] | v.m["concrete"] | (v.m["render"] & (v.z < meta["heights"]["plinth"] + 0.1))) & v.vertical
        down(v, dl, base, clad, v.z - zf, J["drip"])
        down(v, dl, base, plinth, (zf if lean else meta["heights"]["drip"][0]) - v.z, J["plinth"])
        down(v, dl, base, plinth, v.z, J["ground"])
    for k, o, wall, v, om, side, g, door, mine in ops:
        v.put(dl, opening_small(v, Q, om), "add")
    for i, v in views.items():
        if i in roofs:
            v.put(dl, roof_values(v, S["roof"], meta, roofs[i], walls[i]), "add")
            rw, rs = roof_marks(v, S["roof"], meta, roofs[i], walls[i])
            v.put(wash, np.maximum(v.get(wash), rw))
            v.put(far, np.maximum(v.get(far), rw))
            v.put(sn, np.maximum(v.get(sn), rs))
    loose = SM.View(pg, pg.wall == -1, walls[0])
    loose.put(dl, tile_values(loose, Q, meta, None), "add")
    # the ridge's own tiles take the top courses' lichen
    age = float(FL.smoothstep(0.0, S["roof"]["fullYears"], roof_years(meta)))
    ridge = loose.m["tiles"] & (loose.z > meta["heights"]["ridge"] - 0.4)
    loose.put(sn, np.maximum(loose.get(sn), np.where(ridge, lichen(loose, S["roof"]["lichen"], key(meta, "p-roofmarks", -1), np.zeros(loose.shape), age), 0.0)))
    for i, v in views.items():
        sills = [om["features"]["sill"] for k, o, wall, ov, om, side, g, door, mine in ops if wall["i"] == i and not door]
        v.put(gr, grime(v, Q, lows[i][2], sills))

    rng = Q["dlRange"]
    hist = np.stack([pl, 0.5 + np.clip(dl, -rng, rng) / (2.0 * rng), sn, gr], axis=-1)
    FL.write(os.path.join(out, "hist-p.png"), FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2))
    h2 = np.stack([np.clip(wash / T["washL"], 0.0, 1.0), np.clip(far / T["washL"], 0.0, 1.0), np.zeros(pg.shape)], axis=-1)
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.where(pg.cov[..., None], h2, 0), pg.cov, pad + 2))
    FL.write(os.path.join(out, "paint-stroke.png"), FP.strokes(Q, meta))
    FL.write(os.path.join(out, "geo.png"), SM.geo(pg, P, meta))
    FL.write(os.path.join(out, "street-normal.png"), SM.street_normal(pg, meta))

    # the digest, as the corner's; way Pc's paint is the house's own (paints.json), laid on the clay's values
    Qc = copy.deepcopy(Q)
    Qc["materials"]["cladding"] = mats["cladding"]
    cm = Qc["colour"]["mats"]
    cm["cladding"]["paint"] = [wp["C"], wp["h"]]
    cm["trims"]["paint"] = [tp_["C"], tp_["h"]]
    cm.update(board.get("colour", {}))
    for k, v in extra.items():
        cm[k] = dict(cm[v]) if isinstance(v, str) else dict(cm[v["like"]]) if "like" in v else S["colour"].get(k, {})
    # paint.json's colours over them (a stain the corner's material has none of)
    for k, c in S["colour"].items():
        if isinstance(c, dict):
            cm[k] = dict(cm.get(k, {}), **c)
    E, L = dict(Q["edge"], **S.get("edge", {})), Q["lap"]
    sh = P["marks"]["shade"]
    M = P["materials"]
    digest = {
        "mats": [{"name": k, "painted": 1 if M.get(k, {}).get("painted") else 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
                  "underL": v.get("underL", v["L"]), "stainDL": v.get("stainDL", 0.0), "smooth": v["smooth"],
                  "stainSmooth": v.get("stainSmooth", v["smooth"]), "brushL": v.get("brushL", 0.0), "flatUp": v.get("flatUp", 0.0),
                  "stainEdge": v.get("stainEdge", 1.0), "ao": v.get("ao", Q["aoStrength"]), "shadowLift": v.get("shadowLift", 0.0)}
                 for k, v in mats.items()],
        "lights": [dict(v, light=k) for k, v in Q["light"].items()],
        "strokeScale": meta["page"]["size"] / meta["page"]["pxPerM"] / Q["stroke"]["metres"],
        "edgeAmp": E["amp"], "strokeFade": E["fadeLod"], "brushFade": Q["brush"]["fadeLod"], "brushFar": Q["brush"]["far"],
        "dragL": Q["drag"]["L"], "dragScale": Q["drag"]["scale"], "dlRange": Q["dlRange"], "rimL": E["rimL"],
        "rimW": E["rimW"], "rimFar": E["rimFar"], "rimBreak": E["rimBreak"], "bareShift": E["bareShift"],
        "washL": T["washL"], "bareWash": T["bareWash"], "washFade": T["runoff"]["far"]["lod"] if T.get("runoff", {}).get("use") else [0, 0],
        "aoStrength": Q["aoStrength"], "lapDark": L["occlusion"], "lapCore": L["occCoreMm"] / 1000.0,
        "lapReach": L["occReachMm"] / 1000.0, "lapGrimeL": L["grimeL"], "lapGrimeReach": L["reach"],
        "lapGrimeBreak": L["break"], "lapPage": sh["lapPageMm"] / 1000.0,
        "colour": FP.colours(P, Qc, mats),
    }
    json.dump(digest, open(os.path.join(out, "paint.json"), "w"), indent=1)
    preview(os.path.join(FL.ROOT, "cache", "street", "paint-preview", f"{meta['house']}.png"), pl, dl, wash, rng, T["washL"])
    share = lambda m: float((m & pg.cov).sum()) / max(1, int((painted & pg.cov).sum()))  # noqa: E731
    print(f"[paint] wear by wall {', '.join(f'w{i} {wear(meta, paints, w):.2f}' for i, w in walls.items())}; "
          f"grade by wall {', '.join(f'w{i} {g:.2f}' for i, g in grades.items())}; {'; '.join(log)}")
    print(f"[paint] boarding {a.get('boarding') or ('paint.json' if 'boarding' in S else Q['boarding']['use'])}; peeled {share(painted & (pl > 0.5)):.3f} of the paint; "
          f"stained {share(sn > 0.5):.3f}; dL {np.percentile(dl[pg.cov], [1, 5, 50, 95]).round(1)}, "
          f"beyond {rng}: {float((np.abs(dl[pg.cov]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
