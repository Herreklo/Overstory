"""A sea house (sjøhus) on the quay, assembled from its facts: its plan (the town's placement: footprint, base, eave,
pitch, its gable to the water), its type's working (timber.json, workingOfType: the sea house's cladding, trims,
loading doors, hood, eaves, roof and granite), its storeys, and its dated events up to the date (which windows are in
its openings, whether they are boarded). Coats and care are not geometry: they go to the houses buffer
(tools/houses.py) and the shader reads them against the date, as for every house.

The gable to the quay is set out as the builders set it out (wooden-town-architecture.md, sea houses;
docs/references/houses/01): the loading doors stacked in its middle, one to a floor, the loft's in the face of a hoist
hood that stands out from the gable on two raking braces, the hoist's beam through the hood's gable with its block;
small windows either side, floor over floor. The long walls have a few windows on the upper floor, the back gable a
door to the yard. Every choice says what drives it: the plan, the working, or the seed, which picks only among what
the working allows and claims no history.
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
from house import _replacement, boarded_at, window_kind  # noqa: E402
from soup import Frame, Soup, add, cross, mul, norm, sub  # noqa: E402

MM = 0.001


def _bays(length, edge, widest):
    """Openings evenly along a long wall, the first and last at edge from the corners, none further apart than
    widest."""
    room = length - 2 * edge
    if room <= 0:
        return [length / 2]
    gaps = max(1, math.ceil(room / widest - 1e-6))
    return [edge + room * i / gaps for i in range(gaps + 1)]


def _strut(soup, a, b, side, wd, th):
    """A squared timber from a to b (street points), wd wide along side and th deep across it: its four long faces
    (its ends run into what it bears on)."""
    e = norm(sub(b, a))
    up = norm(cross(side, e))
    s_, u_ = mul(side, wd / 2), mul(up, th / 2)
    corners = [add(s_, u_), add(mul(s_, -1.0), u_), add(mul(s_, -1.0), mul(u_, -1.0)), add(s_, mul(u_, -1.0))]
    outs = [up, mul(side, -1.0), mul(up, -1.0), side]
    for i in range(4):
        c0, c1 = corners[i], corners[(i + 1) % 4]
        R.oquad(soup, add(a, c1), add(a, c0), add(b, c0), add(b, c1), outs[i])


def build(b, facts, timber, ground, date, index, seed, lit_share, tier="near"):
    """The sea house's soup. b: its plan (ox, oy the front's left corner, w along the gable to the quay, d back from
    it, angle, base, eave, pitch); facts: its record (type, era, built, storeys, events); tier: the level drawn
    (timber.json, levels), every level from the same facts and seed."""
    wk = timber["workings"][timber["workingOfType"][facts["type"]]]
    hid = facts["id"]
    soup = Soup()
    lv = timber["levels"][tier]
    soup.level, soup.err = lv["level"], lv["errMm"] * MM
    soup.push = pu = timber["push"]
    soup.use(house=index, year=float(facts["built"]))
    W, D = b["w"], b["d"]
    base, eave, pitch = b["base"], b["eave"], b["pitch"]
    ca, sa = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    tp = math.tan(math.radians(pitch))

    def H(x, y, z):
        return (b["ox"] + x * ca - y * sa, b["oy"] + x * sa + y * ca, base + z)

    def V(x, y):
        return (x * ca - y * sa, x * sa + y * ca, 0.0)

    ridge_u = eave + W / 2 * tp
    walls = {
        "front": (H(0, 0, 0), V(1, 0), W),
        "right": (H(W, 0, 0), V(0, 1), D),
        "back": (H(W, D, 0), V(-1, 0), W),
        "left": (H(0, D, 0), V(0, -1), D),
    }
    cl, cb, cs, db, op, hd = wk["cladding"], wk["corner"], wk["casing"], wk["dripBoard"], wk["openings"], wk["hood"]
    out_w = cl["butMm"] * MM
    cw = cs["widthMm"] * MM
    es = timber["windows"][op["window"]]
    ew, eh = es["wMm"] * MM, es["hMm"] * MM
    sill = op["sillMm"] * MM
    # the floors: a storey and a floor's depth each, the loft's floor over the last full storey
    storey = (wk["storeyMm"] + wk["floorMm"]) * MM
    n_full = int(facts["storeys"] // 1000)
    floors = [k * storey for k in range(n_full + 1)]
    loft = floors[-1]
    if loft > eave - 0.5:
        raise ValueError(f"house {hid}: its loft floor ({loft:.2f} m) is above its eave ({eave:.2f} m)")
    loading = [timber["doors"][k] for k in op["loading"]]
    boarded = boarded_at(facts, date)
    report = dict(walls={}, windows=0, doors=0)
    zdrip = -0.05

    # either side of the stacked doors: halfway between the ground door's casing and the corner board, floor over
    # floor; the loft's pair there too where the rake leaves room, else as near it as the hood and the rake allow
    inner = loading[0]["wMm"] * MM / 2 + cw
    outer = W / 2 - op["gableEdgeMm"] * MM
    ds = 0.5 * (inner + outer)
    lw, lh = op["loftMm"][0] * MM, op["loftMm"][1] * MM
    hw = hd["widthMm"] * MM / 2
    zl0 = loft + sill * 0.6
    zl1 = zl0 + lh
    room_l = C.gable_half(zl1 + cs["headMm"] * MM, eave, ridge_u, W / 2) - 0.35 - lw / 2 - cw
    near_l = hw + out_w + 0.25 + lw / 2 + cw
    ds_l = ds if near_l <= ds <= room_l else (0.5 * (near_l + room_l) if near_l <= room_l else None)

    # the hood: its frame's floor under the loft's floor, its door on the loft's floor, its eave over the door's head
    hp = hd["projectMm"] * MM
    zb_h = loft - hd["floorMm"] * MM
    lsp = loading[2]
    zd0 = loft + lsp["thresholdMm"] * MM
    zd1 = zd0 + lsp["hMm"] * MM
    z_he = zd1 + hd["eaveAboveDoorMm"] * MM
    z_hr = z_he + hw * tp

    def holes_of(name, L):
        """The wall's openings: (s0, s1, z0, z1, what, spec, upper)."""
        sc = L / 2
        hs = []
        if name in ("front", "back"):
            for k in range(n_full):
                z = floors[k] + sill
                for s in (sc - ds, sc + ds):
                    hs.append((s - ew / 2, s + ew / 2, z, z + eh, "window", op["window"], False))
            if ds_l is not None:
                for s in (sc - ds_l, sc + ds_l) if name == "front" else (sc,):
                    hs.append((s - lw / 2, s + lw / 2, zl0, zl1, "window", op["window"], True))
        if name == "front":
            for k in range(n_full):
                sp = loading[min(k, 1)]
                z0 = floors[k] + sp["thresholdMm"] * MM
                hs.append((sc - sp["wMm"] * MM / 2, sc + sp["wMm"] * MM / 2, z0, z0 + sp["hMm"] * MM, "door", sp, k > 0))
        elif name == "back":
            sp = timber["doors"][op["backDoor"]]
            z0 = sp["thresholdMm"] * MM
            hs.append((sc - sp["wMm"] * MM / 2, sc + sp["wMm"] * MM / 2, z0, z0 + sp["hMm"] * MM, "door", sp, False))
            for k in range(1, n_full):
                z = floors[k] + sill
                hs.append((sc - ew / 2, sc + ew / 2, z, z + eh, "window", op["window"], False))
        else:
            bays = _bays(L, op["sideEdgeMm"] * MM, op["sideBayMm"][1] * MM)
            for k in range(n_full):
                at = bays if k == n_full - 1 else bays[1:-1]
                z = floors[k] + sill
                for s in at:
                    hs.append((s - ew / 2, s + ew / 2, z, z + eh, "window", op["window"], False))
        return hs

    for name, (o, u, L) in walls.items():
        f = Frame(o, u, (0.0, 0.0, 1.0))
        rng = HS.Stream(seed, hid, name, "carpentry")
        gable = name in ("front", "back")
        top = ridge_u if gable else eave
        oe = wk["eaves"]["overhangMm"] * MM
        shelter = (lambda z, t=top, g=gable: 0.25 * max(0.0, min(1.0, (z - (t - 0.8)) / 0.8)) if g else
                   max(0.0, min(1.0, (z - (eave - 2.5 * oe)) / (2.5 * oe))))
        holes = holes_of(name, L)
        # the courses were set out to land on the builder's sills and heads
        keys = []
        for s0, s1, za, zb, what, sp, upper in holes:
            if what == "window":
                keys.append(za - cs["sillMm"] * MM)
            keys.append(zb + (cs["headMm"] + cs["capMm"]) * MM)
        z0 = zdrip + db["heightMm"] * MM
        lines = C.story_pole(z0, keys, top, cl["exposureMm"])
        outlines, patches = [], []
        for s0, s1, za, zb, what, sp, upper in holes:
            if what == "window":
                kind, yr = window_kind(facts, name, upper, date, sp)
                if kind == "replaced":
                    kind = _replacement(timber, yr)
                wsp = timber["windows"][kind]
                casing_spec = cs
                if wsp["trims"] == "lost":
                    patches.append((s0 - cw, s1 + cw, za - cs["sillMm"] * MM, zb + (cs["headMm"] + cs["capMm"]) * MM, yr))
                    lt = timber["lostTrims"]
                    casing_spec = dict(widthMm=lt["widthMm"], proudMm=lt["proudMm"], headMm=lt["widthMm"], capMm=0,
                                       capProudMm=0, sillMm=lt["sillMm"], sillProudMm=lt["sillProudMm"], hornMm=0,
                                       brackets=None)
                    c_ = 0.5 * (s0 + s1)
                    w_, h_ = min(wsp["wMm"] * MM, s1 - s0), min(wsp["hMm"] * MM, zb - za)
                    s0, s1, za = c_ - w_ / 2, c_ + w_ / 2, zb - h_
                soup.use(year=float(yr))
                outlines.append(C.casing(soup, f, s0, s1, za, zb, casing_spec, out_w, rng))
                C.reveal(soup, f, s0, s1, za, zb, 0.0, out_w - pu["frameSetBackMm"] * MM)
                if boarded is not None:
                    soup.use(year=float(boarded))
                    WN.boarded(soup, f, (s0, s1, za, zb), out_w, casing_spec["proudMm"] * MM * pu["trimProud"],
                               timber["boarding"], rng, float(boarded),
                               sill=(casing_spec["sillMm"] * MM * pu["sillThick"],
                                     casing_spec["sillProudMm"] * MM * pu["sillProud"]))
                    soup.use(year=float(yr))
                lit = 0.0
                if boarded is None and lit_share > 0:
                    kl = HS.unit(HS.h(seed, hid, name, int(s0 * 1000), int(za * 1000), "lit"))
                    lit = (0.05 + 0.95 * HS.unit(HS.h(seed, hid, name, int(s0 * 1000), int(za * 1000), "room"))) \
                        if kl < lit_share else 0.0
                WN.window(soup, f, (s0, s1, za, zb), wsp, out_w, rng, lit, wsp["paint"])
                report["windows"] += 1
            else:
                soup.use(year=float(facts["built"]))
                ol = C.casing(soup, f, s0, s1, za, zb, cs, out_w, rng, with_sill=False)
                ground_door = not upper
                outlines.append((ol[0], ol[1], zdrip if ground_door else za - 0.07, ol[3]))
                C.reveal(soup, f, s0, s1, za, zb, 0.0, out_w - 0.004)
                # the threshold: down to the drip board's line at the ground, a sill board proud of the wall above it
                DR.threshold(soup, f, ol[0], ol[1], zdrip if ground_door else za - 0.07, za, out_w, rng)
                DR.ledged(soup, f, (s0, s1, za, zb), sp, out_w, rng)
                if boarded is not None:
                    soup.use(year=float(boarded))
                    WN.boarded(soup, f, (s0, s1, za, zb), out_w, cs["proudMm"] * MM * pu["trimProud"],
                               timber["boarding"], rng, float(boarded))
                    soup.use(year=float(facts["built"]))
                if ground_door and sp.get("step"):
                    gp = f.at(0.5 * (s0 + s1), 0.0, 0.3)
                    DR.steps(soup, f, ol[0], ol[1], zdrip, ground(gp[0], gp[1]) - base, sp["step"], rng)
                report["doors"] += 1
        if name == "front":
            # the cladding stops at the hood's sides and its foot (its own boards close it)
            outlines.append((L / 2 - hw - out_w, L / 2 + hw + out_w, zb_h + 0.02, z_he))
        soup.use(year=float(facts["built"]))
        wall = dict(length=L, eave=eave, ridge=ridge_u if gable else None,
                    left=cb["widthMm"] * MM, right=cb["widthMm"] * MM, year=facts["built"],
                    scheme="back" if name == "back" else "body")
        n = C.clad(soup, f, wall, outlines, lines, dict(cl, marks=timber["marks"]), rng, shelter, patches)
        ends = gable
        ext = cl["butMm"] * MM + cb["proudMm"] * MM * pu["trimProud"] if ends else 0.0
        ext_db = cl["butMm"] * MM + db["proudMm"] * MM * pu["trimProud"] if ends else 0.0
        C.corner_boards(soup, f, wall, z0, eave, cb, out_w, ext, ext, rng)
        C.drip_board(soup, f, -ext_db, L + ext_db, zdrip, db, out_w, rng)
        # the granite course, down below the lowest ground along the wall
        gz = min(ground(*(o[0] + u[0] * L * t, o[1] + u[1] * L * t)) for t in (0.0, 0.25, 0.5, 0.75, 1.0)) - base
        P.dressed(soup, f, -ext * 0.5, L + ext * 0.5, min(gz, -0.1) - wk["plinth"]["belowMm"] * MM, zdrip + 0.02,
                  wk["plinth"], out_w - 0.006, HS.h(seed, hid, name, "plinth"))
        report["walls"][name] = dict(boards=n, courses=len(lines) - 1, openings=len(holes))

    # the hood on the gable to the quay: three clad walls on a boarded floor, carried by two raking braces, under its
    # own small roof, its door the loft's loading door; the hoist's beam out through its gable, the block hung on it
    f = Frame(*walls["front"][:2], (0.0, 0.0, 1.0))
    sc = W / 2
    rh = HS.Stream(seed, hid, "hood")
    hood_walls = {
        "face": (Frame(f.at(sc - hw, 0.0, out_w + hp), f.u, (0.0, 0.0, 1.0)), 2 * hw, True),
        "left": (Frame(f.at(sc - hw, 0.0, out_w), f.n, (0.0, 0.0, 1.0)), hp, False),
        "right": (Frame(f.at(sc + hw, 0.0, out_w + hp), mul(f.n, -1.0), (0.0, 0.0, 1.0)), hp, False),
    }
    zf_h = zb_h + db["heightMm"] * MM
    for hn, (fh, L, face) in hood_walls.items():
        holes = []
        keys = []
        if face:
            hole = (L / 2 - lsp["wMm"] * MM / 2, L / 2 + lsp["wMm"] * MM / 2, zd0, zd1)
            keys.append(zd1 + (cs["headMm"] + cs["capMm"]) * MM)
        lines = C.story_pole(zf_h, keys, z_hr if face else z_he, cl["exposureMm"])
        outlines = []
        if face:
            soup.use(year=float(facts["built"]))
            ol = C.casing(soup, fh, *hole, cs, out_w, rh, with_sill=False)
            outlines.append((ol[0], ol[1], zd0 - 0.07, ol[3]))
            C.reveal(soup, fh, *hole, 0.0, out_w - 0.004)
            DR.threshold(soup, fh, ol[0], ol[1], zd0 - 0.07, zd0, out_w, rh)
            DR.ledged(soup, fh, hole, lsp, out_w, rh)
            report["doors"] += 1
        wall = dict(length=L, eave=z_he, ridge=z_hr if face else None, left=cb["widthMm"] * MM if face else 0.0,
                    right=cb["widthMm"] * MM if face else 0.0, year=facts["built"], scheme="body")
        shelter = (lambda z: 0.25) if face else (lambda z: 1.0)
        C.clad(soup, fh, wall, outlines, lines, dict(cl, marks=timber["marks"]), rh, shelter, ())
        ext = cl["butMm"] * MM + cb["proudMm"] * MM * pu["trimProud"] if face else 0.0
        if face:
            C.corner_boards(soup, fh, wall, zf_h, z_he, cb, out_w, ext, ext, rh)
        C.drip_board(soup, fh, -ext if face else 0.0, L + ext if face else L, zb_h, db, out_w, rh)
    # its floor's underside, boarded, inside the drip boards
    soup.use(kind="trim", scheme="trim", seed=rh.random(), lap=0.5, shelter=1.0)
    R.oquad(soup, f.at(sc - hw - out_w, zb_h, out_w), f.at(sc + hw + out_w, zb_h, out_w),
            f.at(sc + hw + out_w, zb_h, out_w + hp + out_w), f.at(sc - hw - out_w, zb_h, out_w + hp + out_w),
            (0.0, 0.0, -1.0))
    # the braces, from the hood's front corners down to the gable's face
    bw, bt = hd["braceMm"][0] * MM, hd["braceMm"][1] * MM
    soup.use(kind="trim", scheme="trim", lap=0.5, shelter=0.5)
    for sg in (-1.0, 1.0):
        soup.use(seed=rh.random())
        s_b = sc + sg * (hw - bw / 2)
        _strut(soup, f.at(s_b, zb_h + 0.02, out_w + hp - bt * 0.6), f.at(s_b, zb_h - hd["braceDropMm"] * MM, out_w - 0.01),
               f.u, bw, bt)
    # its roof, from its front gable back into the gable behind it
    wk_h = dict(eaves=hd["eaves"], verge=hd["verge"], roof=wk["roof"])
    laid = timber["covers"][wk["roof"]["material"]]["laid"]
    R.roof(soup, lambda a, r, z: f.at(sc + a, z, out_w + hp - r), 2 * hw, hp, z_he, pitch, wk_h, rh,
           lambda s: mul(f.n, -s), lambda s: mul(f.u, s), laid=laid, push=pu, rain=None, sag=0.0, wall_out=out_w,
           ground_at=None, verges=(True, False))
    # the hoist's beam under the hood's ridge, out through its gable; the block on a short iron
    bmw, bmh = hd["beamMm"][0] * MM, hd["beamMm"][1] * MM
    z_bm = z_hr - 0.18
    soup.use(kind="trim", scheme="trim", seed=rh.random(), lap=0.5, shelter=0.0)
    w_out = out_w + hp + out_w + hd["beamOutMm"] * MM
    soup.box(f, sc - bmw / 2, sc + bmw / 2, z_bm - bmh, z_bm, out_w + hp - 0.3, w_out,
             skip=("back",) if soup.level < 2 else ("back", "top"))
    bx, by, bz = (v * MM for v in hd["blockMm"])
    if soup.level < 2:
        soup.use(kind="metal", scheme="none", seed=rh.random())
        soup.box(f, sc - 0.012, sc + 0.012, z_bm - bmh - 0.22, z_bm - bmh, w_out - 0.11, w_out - 0.086)
        soup.use(kind="trim", scheme="none", seed=rh.random())
        soup.box(f, sc - bz / 2, sc + bz / 2, z_bm - bmh - 0.22 - by, z_bm - bmh - 0.22, w_out - 0.098 - bx / 2,
                 w_out - 0.098 + bx / 2, skip=())

    # the roof over the span, its ridge from the quay's gable to the back's
    rr = HS.Stream(seed, hid, "roof")
    sg_ = pu["ridgeSag"]
    ss = HS.Stream(seed, hid, "roof", "sag")
    sag = min(sg_["mostMm"], sg_["mmPerCentury"] * max(0.0, date - facts["built"]) / 100.0) * MM
    sag *= 1.0 + sg_["spread"] * (2.0 * ss.random() - 1.0)
    rf = R.roof(soup, lambda a, r, z: H(a + W / 2, r, z), W, D, eave, pitch, wk, rr, lambda s: V(0, s),
                lambda s: V(s, 0), laid=laid, push=pu, rain=timber["rainwater"], sag=sag, wall_out=out_w,
                ground_at=lambda x, y: ground(x, y) - base)
    report["roof"] = dict(courses=rf["courses"], ridge=round(rf["ridge_top"], 2), sag_mm=round(sag / MM),
                          eave=round(eave, 2), hood=dict(eave=round(z_he, 2), ridge=round(z_hr, 2)))
    report["triangles"] = soup.triangles()
    return soup, report
