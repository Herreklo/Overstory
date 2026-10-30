"""Way P's page for a rock part: the street's paint (blender/parts/street/paint.py) on a rock's page, p3's rules
(finish.json `painted`) unchanged.

    Blender -b --factory-startup -P blender/parts/rock/kit/paint.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.json (part.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, as the street's:
hist-p.png, hist-p2.png, paint-stroke.png, paint.json, geo.png, street-normal.png, and for a sculpted part (bake.py's
high-poly bake) near-normal.png.

A rock is bare stone standing in the turf, its page its own (kit.json `skin`), not the house plinth's, painted as ref
58 paints its boulders: a calm base of its material's value under one broad, soft variation; the light's three values
held by weathering, its top a little paler (rain-washed, bleached) and its under-planes darker (unwashed, the turf's
damp and splash reach them), the turf's damp darker again over its foot, with no wet band (no eave splashes a rock);
the top's soft painted dabs in loose drifts, thickest toward the weather and fading down over the shoulders; soft
weathering runs shed down the old sides from the top's edges; the contact shade (finish.json `contact`); its cavities
dark by the cavity bake; its breaks (sculpt.py's) a little paler, clean of lichen and dabs, their outline and the
fresh face's crisp arrises caught in a thin light lip where the stone is open; a crack or two drawn as a painter draws
them, a dark line with a lighter lip along a joint's trace across a whole face, never ending inside one; the lichen as
its material's stain, a population of small pale rosettes on the top's weather side, a few merging; and the ground's
junction dark (`junction.ground`). No peel and no lap, and its runs are in the page's value, not the street's washes.
Its value and hue are its material's (the part's own, kit.json `materials` and `colour`).
"""

import copy
import importlib.util
import json
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
STREET = os.path.join(ROOT, "blender", "parts", "street")
FINISH = os.path.join(ROOT, "blender", "parts", "finish")
sys.path.insert(0, FINISH)
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FP = module(os.path.join(FINISH, "paint.py"), "finish_paint")
MK = FP.MK
SM = module(os.path.join(STREET, "marks.py"), "street_marks")
SP = module(os.path.join(STREET, "paint.py"), "street_paint")  # its digest and junction, called as they are
key, field = MK.key, FP.field


def main():
    a = MK.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "house.json")))
    meta.setdefault("walls", [])
    P = json.load(open(os.path.join(FINISH, "finish.json")))
    K = json.load(open(os.path.join(HERE, "kit.json")))
    Q = P["painted"]
    bake = json.load(open(os.path.join(cache, "bake.json")))
    out = os.path.join(cache, "out")
    os.makedirs(out, exist_ok=True)
    pg = SM.Page(cache, meta, bake["mats"])
    pad = meta["page"]["padPx"]
    T = Q["tongue"]

    mats = {k: dict(Q["materials"][K["materials"][k]["like"]],
                    **{f: x for f, x in K["materials"][k].items() if f not in ("like", "describes", "_")})
            for k in bake["mats"]}
    rock = np.zeros(pg.shape, bool)
    for k in mats:
        rock |= pg.m[k]
    Sk = K["skin"]
    MS_skewed = lambda st_, lo, hi, k: lo + (hi - lo) * st_.random() ** int(k)  # noqa: E731  (mass.py's skewed)
    MS_unit = lambda toward, slope=90.0: np.array([np.sin(np.radians(toward)) * np.sin(np.radians(slope)),  # noqa: E731
                                                   np.cos(np.radians(toward)) * np.sin(np.radians(slope)), np.cos(np.radians(slope))])

    # the designed faces: each texel's the plane its normal is nearest; each plane's offset where it lies flat; a
    # texel's distance in its plane to the face's edge, the nearest line another plane (or the turf) cuts it along
    X = next(x for x in K["mass"]["masses"] if x["id"] == meta["part"])
    keys = [k for k, f in meta.get("faces", {}).items() if "n" in f]
    N = np.array([meta["faces"][k]["n"] for k in keys]); wear = [meta["faces"][k]["wear"] for k in keys]
    face = np.where(rock, np.argmax(pg.n @ N.T, -1), -1)
    D = np.array([np.median((pg.p[(face == i) & (pg.n @ N[i] > 0.999)] @ N[i])) if ((face == i) & (pg.n @ N[i] > 0.999)).any()
                  else np.max(pg.p[face == i] @ N[i], initial=0.0) for i in range(len(N))])

    def edge(i, Pf, turf=True, among=None):
        out = Pf[:, 2] / max(np.sqrt(1.0 - N[i][2] ** 2), 1e-3) if turf else np.full(len(Pf), np.inf)
        for j in (range(len(N)) if among is None else among):
            s2 = 1.0 - float(N[i] @ N[j]) ** 2
            if j != i and s2 > 1e-3:
                out = np.minimum(out, (D[j] - Pf @ N[j]) / np.sqrt(s2))
        return out

    st = lambda *k: HS.Stream(meta["world"], "rock", meta["part"], "paint", *k)  # noqa: E731
    count = lambda i: int((face == i).sum())  # noqa: E731

    # the breaks as the high-poly cuts them (sculpt.py's planes, in the levels' frame): a texel's depth inside a
    # break's cut, positive within the scar, so the scar and its outline are known exactly
    SC = module(os.path.join(HERE, "sculpt.py"), "rock_sculpt")
    Pb = pg.p + np.array([0.0, 0.0, X.get("sinkM", SC.MS.M["judge"]["sinkM"])]); scar = np.full(pg.shape, -1e9)
    for b in SC.Sculpt(X).breaks:
        d = Pb @ b["f"] - b["of"]
        for wn, ow in b["walls"]:
            d = np.minimum(d, Pb @ wn - ow)
        scar = np.maximum(scar, d)
    scar = np.where(rock, scar, -1e9)

    # the lichen (`lichen`), as it grows on coastal gneiss: a population of small round rosettes, `rM` across their
    # radius (skewed small by `skew`), pale grey-green (the material's stain), `count` of them about a middle on the
    # top's weather side (the mean of the up-facing texels' `weather` share furthest toward it) and thinning out over
    # `spreadM` (a normal spread); each on an old face looking up at least `up`, at least `clearM` plus its radius in
    # from where the stone turns steeper, never in a scar. Two either stand `gapM` apart or merge, overlapping at least
    # `overlap` of their radii: at most `merge` pairs, never three, never a shape wider than `mostM`. Each margin lobed a
    # little (`lobe`: [cell, amplitude] metres)
    Li = Sk["lichen"]; up = pg.n[..., 2]; fresh = [i for i in range(len(N)) if wear[i] in K["sculpt"]["fresh"]]
    wv = MS_unit(K["sculpt"]["chamfer"]["weather"][0]); s = pg.p @ wv
    tops = [i for i in range(len(N)) if N[i][2] >= Li["up"] and i not in fresh]
    clear = np.full(pg.shape, -1.0)
    for i in tops:
        m = rock & (face == i); clear[m] = edge(i, pg.p[m], among=[j for j in range(len(N)) if j not in tops])
    ok = rock & (scar < 0) & (clear > 0); rs = st("lichen")
    mid = pg.p[ok & (s >= np.quantile(s[ok], 1.0 - Li["weather"]))].mean(0)
    Pc, Cc = pg.p[ok], clear[ok]
    cdf = np.cumsum(np.exp(-0.5 * (np.linalg.norm(Pc - mid, axis=-1) / Li["spreadM"]) ** 2)); cdf /= cdf[-1]
    ros, paired, n = [], set(), rs.randint(*Li["count"])
    for _ in range(Li["tries"] * n):
        if len(ros) >= n:
            break
        j = min(int(np.searchsorted(cdf, rs.random())), len(Pc) - 1); q, r = Pc[j], MS_skewed(rs, *Li["rM"], Li["skew"])
        if Cc[j] < Li["clearM"] + r:
            continue
        near = [(k, float(np.linalg.norm(q - qk)), rk) for k, (qk, rk) in enumerate(ros) if np.linalg.norm(q - qk) < r + rk + Li["gapM"]]
        if near:
            k, d, rk = near[0]
            if (len(near) > 1 or k in paired or len(paired) >= 2 * Li["merge"] or d > Li["overlap"] * (r + rk)
                    or d + r + rk > Li["mostM"]):
                continue
            paired |= {k, len(ros)}
        ros.append((q, r))
    lobe = Li["lobe"][1] * (2.0 * FL.fbm3(pg.p, key(meta, "p-lichen-lobe"), Li["lobe"][0], 2) - 1.0)
    sd = np.full(pg.shape, -1.0)
    for q, r in ros:
        sd = np.maximum(sd, r - np.linalg.norm(pg.p - q, axis=-1))
    sn = np.where(rock & (scar < 0) & (up > Li["under"]), field(sd + lobe, Li["soft"]), 0.0)

    # the top's stipple (`dabs`), 58's painted dabs, not a grain: on a seeded lattice of cells `cellM`, at most one
    # soft dab in each, `rM` across its radius (skewed small by `skew`), its edge soft over `soft` of it and its outline
    # broken by `warp` of its radius, lighter by `light`.L (a `light` share of them) or darker by `dark`.L, overlapping
    # dabs adding up to `most` times that; a cell holds one with the chance `share` times its
    # density (its texels' mean): full on the top and fading down over the shoulders (`up`), gathered in loose drifts
    # (`drift`: k over cells `cellM`), thicker toward the weather (`weather`: 1 plus as much times a texel's place from
    # the lee side, -1, to the weather side, 1); none in a scar, none on the fresh face (its skin is new)
    Db, Dr = Sk["dabs"], Sk["dabs"]["drift"]
    on = rock & (scar < 0) & ~np.isin(face, fresh)
    sr = s[rock]; sw = np.clip(2.0 * (s - sr.min()) / max(float(np.ptp(sr)), 1e-6) - 1.0, -1.0, 1.0)
    dens = (Db["share"] * FL.smoothstep(Db["up"][0], Db["up"][1], up) * (1.0 + Db["weather"] * sw)
            * (Dr["k"][0] + (Dr["k"][1] - Dr["k"][0]) * FL.equalise(FL.fbm3(pg.p, key(meta, "p-dabs-drift"), Dr["cellM"], 2), rock)))
    idx = np.nonzero(on); P0 = pg.p[idx]; cm = Db["cellM"]; kd = key(meta, "p-dabs")
    code = lambda c: ((c[:, 0] + (1 << 20)) << 42) | ((c[:, 1] + (1 << 20)) << 21) | (c[:, 2] + (1 << 20))  # noqa: E731
    base = np.floor(P0 / cm).astype(np.int64); uB, invB = np.unique(code(base), return_inverse=True)
    dB = np.bincount(invB, dens[idx]) / np.bincount(invB)
    val = np.zeros(len(P0)); wp = 1.0 + Db["warp"] * (2.0 * FL.fbm3(P0, key(meta, "p-dabs-warp"), Db["rM"][1], 2) - 1.0)
    for off in np.array(np.meshgrid(*[(-1, 0, 1)] * 3)).T.reshape(-1, 3):
        c = base + off; cc = code(c); uc, first, inv = np.unique(cc, return_index=True, return_inverse=True); cu = c[first]
        h = lambda tag: FL.unit(kd, cu[:, 0], cu[:, 1], cu[:, 2], np.full(len(cu), tag))[inv]  # noqa: E731
        at = np.minimum(np.searchsorted(uB, cc), len(uB) - 1); dc = np.where(uB[at] == cc, dB[at], 0.0)
        ctr = (c + np.stack([h(0), h(1), h(2)], -1)) * cm
        r = Db["rM"][0] + (Db["rM"][1] - Db["rM"][0]) * h(3) ** Db["skew"]
        sign = np.where(h(5) < Db["light"]["share"], Db["light"]["L"], -Db["dark"]["L"])
        val += (h(4) < dc) * sign * FL.smoothstep(r, r * (1.0 - Db["soft"]), wp * np.linalg.norm(P0 - ctr, axis=-1))
    dab = np.zeros(pg.shape); dab[idx] = np.clip(val, -Db["most"] * Db["dark"]["L"], Db["most"] * Db["light"]["L"])


    # the values: the broad variation, the turf's damp over the foot, the weathered top paler, the contact shade, the
    # cavities dark, the drawn crack, then the ground's junction dark from what is there
    dl = np.zeros(pg.shape)
    Br, Fo, Cv = Sk["broad"], Sk["foot"], Sk["cavity"]
    dl += np.where(rock, Br["L"] * (2.0 * FL.fbm3(pg.p, key(meta, "p-broad"), Br["cellM"], Br["octaves"]) - 1.0), 0.0)
    dl -= np.where(rock, Fo["L"] * (1.0 - FL.smoothstep(0.0, Fo["m"], pg.z)), 0.0)
    Tp = Sk["top"]
    dl += np.where(rock, Tp["L"] * FL.smoothstep(Tp["up"][0], Tp["up"][1], up), 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
    dl -= np.where(rock, Cv["L"] * FL.smoothstep(Cv["cav"][0], Cv["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)), 0.0)

    # the crack: the joint's trace across the biggest side facing the mass's front, at a seeded offset from its middle,
    # carried over onto the face its upper end runs into (`faces`); drawn on those faces' texels only, so it ends
    # where the planes change
    Cr = Sk["crack"]
    jn = next(j for j in X["structure"]["joints"] if j["name"] == Cr["set"]); nj = MS_unit(jn["dipToward"], jn["dip"])
    front = MS_unit(X["front"])
    sides = [i for i in range(len(N)) if N[i] @ front >= Cr["front"] and abs(N[i][2]) <= 0.6]
    if sides and Cr["faces"]:
        A = max(sides, key=count); PA = pg.p[face == A]; t = PA @ nj; rc = st("crack")
        x = float(np.median(t)) + Cr["offset"] * float(np.ptp(t)) * rc.uniform(-1.0, 1.0); side = 1.0 if rc.random() < 0.5 else -1.0
        L_, amp = Cr["wander"]
        sj = pg.p @ nj - x + amp * (2.0 * FL.fbm3(pg.p, key(meta, "p-crack"), L_, 2) - 1.0)
        on = face == A; w = Cr["widthM"] / 2
        for _ in range(Cr["faces"] - 1):
            tr = rock & (np.abs(sj) < w) & ~on; ta = pg.p[on & (np.abs(sj) < w)]
            best, bz = -1, -1e9
            for j in np.unique(face[tr]):
                pj = pg.p[tr & (face == j)]
                near = np.min(np.linalg.norm(pj[::max(1, len(pj) // 400), None] - ta[None, ::max(1, len(ta) // 400)], axis=-1))
                if near < Cr["near"] and pj[:, 2].mean() > bz and N[j][2] > N[A][2]:
                    best, bz = j, pj[:, 2].mean()
            if best < 0:
                break
            on |= face == best
        lip = Cr["lipM"] / 2
        dl += np.where(on, -Cr["L"] * field(w - np.abs(sj), Cr["soft"]) + Cr["lipL"] * field(lip - np.abs(side * sj - w - lip), Cr["soft"]), 0.0)

    # the three values as 58 paints them, the light's first: the top a little paler again for its speckle's ground, the
    # under-planes darker (`under`: no rain washes them, the turf's damp and splash reach them)
    Un = Sk["under"]
    dl -= np.where(rock, Un["L"] * FL.smoothstep(Un["up"][0], Un["up"][1], -up), 0.0)
    dl += dab

    # the weathering runs (`runs`), 58's: the water the top sheds runs down the old sides and leaves soft streaks a
    # little darker, each from the side's upper edge down, tapering to a point (finish paint.py's `run`, the street's
    # own, measured around the stone instead of along a wall): `perM` runs a metre of a side's width (at least one),
    # each `widthM` wide and faded to half at `lenM` (never past the face's height), wandering `wanderM`, at most `L`
    # darker; on faces looking up less than `up`[1] (full under `up`[0]) and not under past `under`, never on the
    # fresh face or in a scar
    Ru = Sk["runs"]; rr = st("runs"); o = pg.p[rock].mean(0)
    th = np.arctan2(pg.p[..., 1] - o[1], pg.p[..., 0] - o[0]); Rm = float(np.median(np.hypot(*(pg.p[rock][:, :2] - o[:2]).T)))
    wrap = lambda a: (a + np.pi) % (2.0 * np.pi) - np.pi  # noqa: E731
    sidew = (1.0 - FL.smoothstep(Ru["up"][0], Ru["up"][1], up)) * (1.0 - FL.smoothstep(Ru["under"][0], Ru["under"][1], -up))
    runs = np.zeros(pg.shape); nr = 0
    for i in range(len(N)):
        m = rock & (face == i)
        if i in fresh or not (-Ru["under"][1] < N[i][2] < Ru["up"][1]) or not m.any():
            continue
        t0 = float(np.arctan2(np.sin(th[m]).mean(), np.cos(th[m]).mean())); along = wrap(th - t0) * Rm
        lo, hi = np.percentile(along[m], [3, 97])
        for n_ in range(max(1, int(round((hi - lo) * Ru["perM"] * rr.uniform(0.6, 1.4))))):
            w = rr.uniform(*Ru["widthM"]); x0 = rr.uniform(lo + 0.6 * w, hi - 0.6 * w) if hi - lo > 1.2 * w else (lo + hi) / 2
            head = m & (np.abs(along - x0) < w / 2)
            if not head.any():
                continue
            z0 = float(pg.z[head].max()); length = min(rr.uniform(*Ru["lenM"]), 0.5 * (z0 - float(pg.z[m].min())))
            g_ = types.SimpleNamespace(z=pg.z, along=along, shape=pg.shape)
            runs = np.maximum(runs, FP.run(g_, key(meta, "p-runs", i, n_), x0, z0, length, w / 2, Ru["wanderM"], rock & (scar < 0)))
            nr += 1
    dl -= Ru["L"] * runs * sidew

    # the breaks (`breaks`): the scar a little paler, the weathered skin knocked off it, and its outline caught by the
    # light in a thin lip, as are the fresh face's crisp arrises; the lip only where the stone is open (the occlusion)
    Bk = Sk["breaks"]; open_ = FL.smoothstep(Bk["ao"][0], Bk["ao"][1], pg.ao)
    dl += np.where(scar > 0, Bk["L"], 0.0)
    lip = FL.smoothstep(-Bk["lipM"], -Bk["lipM"] / 3, scar) * (scar <= 0)
    for i in range(len(N)):
        if wear[i] in K["sculpt"]["fresh"]:
            Pf = pg.p[face == i]; d = np.zeros(pg.shape); d[face == i] = edge(i, Pf, turf=False)
            lip = np.maximum(lip, np.where(face == i, 1.0 - FL.smoothstep(Bk["freshLipM"] / 3, Bk["freshLipM"], d), 0.0))
    dl += Bk["lipL"] * lip * open_

    base = np.zeros(pg.shape)
    for name, m in mats.items():
        base = np.where(pg.m[name], m["L"] - m.get("stainDL", 0.0) * (sn > 0.5), base)
    whole = SM.View(pg, pg.cov, {"origin": [0, 0], "dir": [1, 0], "out": [0, -1], "kind": "rock"})
    SP.down(whole, dl, base, whole.get(rock), whole.z, Q["junction"]["ground"])

    rng = Q["dlRange"]
    # the value dithered by one step of the 8-bit page, seeded, so its gentle gradients do not band
    dl = dl + 2.0 * rng / 255.0 * (FL.unit(key(meta, "p-dither"), *np.indices(pg.shape)) - 0.5)
    zero = np.zeros(pg.shape)
    hist = np.stack([zero, 0.5 + np.clip(dl, -rng, rng) / (2.0 * rng), sn, zero], axis=-1)
    FL.write(os.path.join(out, "hist-p.png"), FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2))
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.zeros(pg.shape + (3,)), pg.cov, pad + 2))
    FL.write(os.path.join(out, "paint-stroke.png"), FP.strokes(Q, meta))
    FL.write(os.path.join(out, "geo.png"), SM.geo(pg, P, meta))
    FL.write(os.path.join(out, "street-normal.png"), SM.street_normal(pg, meta))
    if bake.get("high"):  # a sculpted part: the near level's own normal from the high-poly, beside the street level's
        nn = FL.read(os.path.join(cache, "near-normal.exr"))
        FL.write(os.path.join(out, "near-normal.png"), FL.dilate(nn[..., :3], nn[..., 3] > 0.5, pad + 2))

    # the digest, as the street's; its colours kit.json's, laid on the clay's values
    Qc = copy.deepcopy(Q)
    cm = Qc["colour"]["mats"]
    for k, v in K["materials"].items():
        if k != "describes":
            cm[k] = dict(cm.get(v["like"], {}), **K["colour"].get(k, {}))
    E, L = Q["edge"], Q["lap"]
    sh = P["marks"]["shade"]
    digest = {
        "mats": [{"name": k, "painted": 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
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
    c = pg.cov & rock
    print(f"[paint] {meta['part']}: lichen {float((sn[c] > 0.5).mean()):.4f} in {len(ros)} rosettes ({len(paired) // 2} merged pairs); "
          f"dabs {float((np.abs(dab[c]) > 0.5).mean()):.3f}; {nr} runs; "
          f"scars {float((scar[c] > 0).mean()):.4f}, lip {float((lip[c] > 0.5).mean()):.4f}; "
          f"dL {np.percentile(dl[c], [1, 5, 50, 95]).round(1)}, beyond {rng}: {float((np.abs(dl[c]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
