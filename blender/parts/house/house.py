"""One timber house, assembled from its facts: the footprint, base, eave, roof and pitch it stands with (the plan), the
era it was built in (which working: its cladding, trims, windows, roof and plinth), and its dated events up to the
date (which windows are in its openings, whether they are boarded). Coats and care are not geometry: they go to the
houses buffer (tools/houses.py) and the shader reads them against the date.

Every choice says what drives it: a fact (the event or the plan), the working (the pack's), or the seed, which picks
only among what the facts allow and claims no history (h(worldSeed, house, purpose)).
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "resolver"))

import carpentry as C  # noqa: E402
import doors as DR  # noqa: E402
import hashing as HS  # noqa: E402
import plinth as P  # noqa: E402
import roof as R  # noqa: E402
import windows as WN  # noqa: E402
from soup import Frame, Soup  # noqa: E402

MM = 0.001


def window_kind(facts, wall, upper, date, era_kind):
    """The window in a wall's openings at the date and the year it went in: the era's, or what the latest replacement
    before the date put in, unless a restoration since put copies of the era's back. wall: front, right, back, left;
    an event's scope 'street' is the front, 'back' the back, 'upper' the gables' loft windows."""
    kind, year = era_kind, facts["built"]
    for ev in facts["events"]:
        if ev["year"] > date:
            break
        scope = ev.get("params", {}).get("scope", "all")
        hit = scope == "all" or (scope == "street" and wall == "front") or (scope == "back" and wall == "back") or \
            (scope == "upper" and upper)
        if not hit:
            continue
        if ev["kind"] == "windows_replaced":
            kind, year = ("replaced", ev["year"])
        elif ev["kind"] == "restored" and ev.get("params", {}).get("windows") == "original":
            kind, year = era_kind, ev["year"]
    return kind, year


def _replacement(timber, year):
    for w in timber["windowsByYear"]:
        if w["from"] <= year <= w["to"]:
            return w["window"]
    raise KeyError(f"no window in windowsByYear for {year}")


def boarded_at(facts, date):
    """The year the house was boarded, if it still is at the date."""
    yr = None
    for ev in facts["events"]:
        if ev["year"] > date:
            break
        if ev["kind"] == "boarded":
            yr = ev["year"]
        elif ev["kind"] == "unboarded":
            yr = None
    return yr


def bays(length, op):
    """Where a wall's openings sit (their centres): the first and last at the working's distance from the corners,
    the rest evenly between: the fewest that keep the spacing within the working's widest."""
    b0, b1 = op["bayMm"][0] * MM, op["bayMm"][1] * MM
    edge = op["edgeMm"] * MM
    room = length - 2 * edge
    if room < b0 * 0.75:
        return [length / 2]
    gaps = max(1, math.ceil(room / b1 - 1e-6))
    return [edge + room * i / gaps for i in range(gaps + 1)]


def build(b, facts, timber, ground, date, index, seed, lit_share):
    """The house's soup. b: its plan (heart_layout's building); facts: its record (era, built, events, wealth)."""
    wk = timber["workings"][facts["era"]]
    hid = facts["id"]
    soup = Soup()
    soup.use(house=index, year=float(facts["built"]))
    W, D = b["w"], b["d"]
    base, eave, pitch = b["base"], b["eave"], b["pitch"]
    ca, sa = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))

    def H(x, y, z):
        return (b["ox"] + x * ca - y * sa, b["oy"] + x * sa + y * ca, base + z)

    def V(x, y):
        return (x * ca - y * sa, x * sa + y * ca, 0.0)

    gable_ends = ("front", "back") if b["roof"] == "gable" else ("left", "right")
    half_span = (W if b["roof"] == "gable" else D) / 2
    ridge_u = eave + half_span * math.tan(math.radians(pitch))
    walls = {
        "front": (H(0, 0, 0), V(1, 0), W),
        "right": (H(W, 0, 0), V(0, 1), D),
        "back": (H(W, D, 0), V(-1, 0), W),
        "left": (H(0, D, 0), V(0, -1), D),
    }
    cl, cb, cs, db = wk["cladding"], wk["corner"], wk["casing"], wk["dripBoard"]
    out_w = cl["butMm"] * MM
    era_window = wk["openings"]["window"]
    boarded = boarded_at(facts, date)
    report = dict(walls={}, windows=0)
    zdrip = -0.05
    for name, (o, u, L) in walls.items():
        f = Frame(o, u, (0.0, 0.0, 1.0))
        rng = HS.Stream(seed, hid, name, "carpentry")
        gable = name in gable_ends
        top = ridge_u if gable else eave
        oe = wk["eaves"]["overhangMm"] * MM
        shelter = (lambda z, t=top, g=gable: 0.25 * max(0.0, min(1.0, (z - (t - 0.8)) / 0.8)) if g else
                   max(0.0, min(1.0, (z - (eave - 2.5 * oe)) / (2.5 * oe))))
        # the openings where the builder set them: the ground floor's windows in bays, the gables' loft windows
        op = wk["openings"]
        es = timber["windows"][era_window]
        sill = op["sillMm"] * MM
        era_holes = [(s - es["wMm"] * MM / 2, s + es["wMm"] * MM / 2, sill, sill + es["hMm"] * MM, False)
                     for s in bays(L, op)]
        # the door on the front, where the plan has it (the layout's door paths lead there): the era's door, in the
        # middle of the front or in its first bay at the side; it takes the bay it stands in
        dsp, door_hole = None, None
        if name == "front" and op.get("door"):
            dsp = timber["doors"][op["doorKind"]]
            sd = L / 2 if op["door"] == "centre" else bays(L, op)[0]
            dw, foot = dsp["wMm"] * MM, dsp["thresholdMm"] * MM
            door_hole = (sd - dw / 2, sd + dw / 2, foot, foot + dsp["hMm"] * MM)
            clear = dw / 2 + cs["widthMm"] * MM * 2 + es["wMm"] * MM / 2 + 0.1
            era_holes = [h for h in era_holes if abs(0.5 * (h[0] + h[1]) - sd) > clear]
        if gable and ridge_u - eave > 1.9:
            uw, uh = es["wMm"] * MM * 0.8, es["hMm"] * MM * 0.72
            # the loft's windows on its floor: a storey and a floor's depth up, at the sill's height
            z_u = (wk["storeyMm"] + wk["floorMm"]) * MM + sill * 0.75
            if z_u + uh < ridge_u - 0.6 and C.gable_half(z_u + uh, eave, ridge_u, L / 2) > uw:
                pair = op["gable"] == "pair" and C.gable_half(z_u + uh, eave, ridge_u, L / 2) > uw + 0.6
                for s in ((L / 2 - uw * 0.75, L / 2 + uw * 0.75) if pair else (L / 2,)):
                    era_holes.append((s - uw / 2, s + uw / 2, z_u, z_u + uh, True))
        # the courses were set out to land on the builder's sills and heads
        keys = []
        for h in era_holes:
            keys += [h[2] - cs["sillMm"] * MM, h[3] + (cs["headMm"] + cs["capMm"]) * MM]
        if door_hole is not None:
            keys.append(door_hole[3] + (cs["headMm"] + cs["capMm"]) * MM)
        z0 = zdrip + db["heightMm"] * MM
        lines = C.story_pole(z0, keys, top, cl["exposureMm"])
        # what is in each opening at the date: the era's window in its casing, or a later one in a smaller opening
        # under the old head, its trims lost, the rest of the old hole boarded in with that year's boards
        outlines, patches = [], []
        for s0, s1, za, zb, upper in era_holes:
            kind, yr = window_kind(facts, name, upper, date, era_window)
            if kind == "replaced":
                kind = _replacement(timber, yr)
            sp = timber["windows"][kind]
            k = 0.8 if upper else 1.0
            casing_spec = cs
            if sp["trims"] == "lost":
                old = (s0 - cs["widthMm"] * MM, s1 + cs["widthMm"] * MM, za - cs["sillMm"] * MM,
                       zb + (cs["headMm"] + cs["capMm"]) * MM, yr)
                patches.append(old)
                lt = timber["lostTrims"]
                casing_spec = dict(widthMm=lt["widthMm"], proudMm=lt["proudMm"], headMm=lt["widthMm"], capMm=0,
                                   capProudMm=0, sillMm=lt["sillMm"], sillProudMm=lt["sillProudMm"], hornMm=0,
                                   brackets=None)
                c_ = 0.5 * (s0 + s1)
                w_, h_ = sp["wMm"] * MM * k, sp["hMm"] * MM * (0.72 if upper else 1.0)
                s0, s1, za = c_ - w_ / 2, c_ + w_ / 2, zb - h_
            soup.use(year=float(yr))
            outlines.append(C.casing(soup, f, s0, s1, za, zb, casing_spec, out_w, rng))
            C.reveal(soup, f, s0, s1, za, zb, out_w + casing_spec["proudMm"] * MM, out_w - 0.004)
            if boarded is not None:
                soup.use(year=float(boarded))
                WN.boarded(soup, f, outlines[-1], out_w, casing_spec["proudMm"] * MM, timber["boarding"], rng,
                           float(boarded))
                soup.use(year=float(yr))
            lit = 0.0
            if boarded is None and lit_share > 0:
                kl = HS.unit(HS.h(seed, hid, name, int(s0 * 1000), "lit"))
                lit = (0.05 + 0.95 * HS.unit(HS.h(seed, hid, name, int(s0 * 1000), "room"))) if kl < lit_share else 0.0
            WN.window(soup, f, (s0, s1, za, zb), sp, out_w, rng, lit, sp["paint"])
            report["windows"] += 1
        if door_hole is not None:
            ds0, ds1, dz0, dz1 = door_hole
            soup.use(year=float(facts["built"]))
            ol = C.casing(soup, f, ds0, ds1, dz0, dz1, cs, out_w, rng, with_sill=False)
            outlines.append((ol[0], ol[1], zdrip, ol[3]))
            C.reveal(soup, f, ds0, ds1, dz0, dz1, out_w + cs["proudMm"] * MM, out_w - 0.004)
            DR.threshold(soup, f, ol[0], ol[1], zdrip, dz0, out_w, rng)
            DR.door(soup, f, door_hole, dsp, out_w, rng, 0.0)
            if boarded is not None:
                soup.use(year=float(boarded))
                WN.boarded(soup, f, (ol[0], ol[1], dz0, ol[3]), out_w, cs["proudMm"] * MM, timber["boarding"], rng,
                           float(boarded))
            gp = f.at(0.5 * (ds0 + ds1), 0.0, 0.3)
            DR.steps(soup, f, ol[0], ol[1], zdrip, ground(gp[0], gp[1]) - base, dsp["step"], rng)
            report["door"] = dict(wall=name, at=round(0.5 * (ds0 + ds1), 2))
        soup.use(year=float(facts["built"]))
        wall = dict(length=L, eave=eave, ridge=ridge_u if gable else None,
                    left=cb["widthMm"] * MM, right=cb["widthMm"] * MM, year=facts["built"],
                    scheme="back" if name == "back" else "body")
        n = C.clad(soup, f, wall, outlines, lines, cl, rng, shelter, patches)
        ext = cl["butMm"] * MM + cb["proudMm"] * MM if name in ("front", "back") else 0.0
        C.corner_boards(soup, f, wall, z0, eave, cb, out_w, ext, ext, rng)
        C.drip_board(soup, f, -ext, L + ext, zdrip, db, out_w, rng)
        # the plinth, down below the lowest ground along the wall
        gz = min(ground(*(o[0] + u[0] * L * t, o[1] + u[1] * L * t)) for t in (0.0, 0.25, 0.5, 0.75, 1.0)) - base
        P.plinth(soup, f, -ext * 0.5, L + ext * 0.5, min(gz, -0.25) - 0.35, zdrip + 0.02, wk["plinth"], out_w - 0.006,
                 HS.h(seed, hid, name, "plinth"))
        report["walls"][name] = dict(boards=n, courses=len(lines) - 1, openings=len(era_holes), patches=len(patches))

    # the roof over the span, its ridge along the gables
    if b["roof"] == "gable":
        place = lambda a, r, z: H(a + W / 2, r, z)
        span, length = W, D
        side_dir = lambda s: V(s, 0)
        verge_dir = lambda s: V(0, s)
    else:
        place = lambda a, r, z: H(r, a + D / 2, z)
        span, length = D, W
        side_dir = lambda s: V(0, s)
        verge_dir = lambda s: V(s, 0)
    rr = HS.Stream(seed, hid, "roof")
    rf = R.roof(soup, place, span, length, eave, pitch, wk, rr, verge_dir, side_dir)
    ch = wk["chimney"]
    # one stack at mid-ridge, or a pair, each by a room's wall (the seed picks where among what the era allows)
    at = [0.5] if ch["count"] == 1 else [0.22 + 0.08 * rr.random(), 0.70 + 0.08 * rr.random()]
    for t in at:
        r_at = length * (t + (rr.random() - 0.5) * (0.3 if ch["count"] == 1 else 0.0))
        R.chimney(soup, place, r_at, 0.0, rf["ridge_top"], ch, rr, eave)
    report["roof"] = dict(courses=rf["courses"], ridge=round(rf["ridge_top"], 2))
    report["triangles"] = soup.triangles()
    return soup, report
