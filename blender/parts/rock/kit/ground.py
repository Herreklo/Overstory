"""Stage 6, the ground (kit.json `ground`): the tip's one community (the pack's `community`, growth.json habitats:
summer turf, hair-grass in tussocks through it; heather is the grass and heath element's) over the whole floor out to the
frame's edge, drawn as the growth's instanced tufts (unity/Assets/Code/Scenes/Growth, GrowthTufts), and the ground
under it the community's own map (growth.ground_map), so where the tufts thin out with distance the ground carries
the same colour on. Where it meets a part, the same community banks against the stone (`bank`): fuller and taller
where the stone sheds its rain (the bearings its top drains to, traced down the form's own top) and in its lee, a
little shorter on the side the weather comes from, thinner and drier under an overhang; its reach out from the turf
line varied by bearing (tongues and bays, never a ring) and broken where the turf line shows (where foot.py's till
stones lie). A tuft that would enter the stone leans further out, then shrinks, or is left out; none stands in the
house (its near level's outline at its foot) or on a stone. All of it is seeded texture over the record's facts.

Writes into `out` (cache/rock/kit/gen/ground): ground.json (the box, the maps, the draw's settings and the tufts'
kinds), tufts.bin (each instance as float32: its 3x3 turn and scale row by row and its foot, in the scene's frame,
x east, y north, z up, m; then its rank, hue and damp, 0 to 1), ground-Pc.png (sRGB) and ground-P.png (its value).

    Blender -b --factory-startup -P blender/parts/rock/kit/ground.py [-- --out cache/rock/kit/gen/ground]
"""
import json, math, os, struct, sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import foot as FT  # noqa: E402

SC, MS, HS, arg = FT.SC, FT.MS, FT.HS, FT.arg
ROOT = MS.ROOT
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
import growth as GR  # noqa: E402

K = MS.K
G = K["ground"]
UP = np.array([0.0, 0.0, 1.0])


def house_mask(gen, lowZ, cell, margin):
    """The house's foot from its near level: every edge of a piece reaching below lowZ marked on a grid, the inside
    the walls enclose filled, grown by margin. keep(x, y) -> True where a tuft may stand."""
    with bpy.data.libraries.load(os.path.join(ROOT, gen, "house.blend")) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith("near_")]
    pts = []
    for ob in dst.objects:
        if ob is None or ob.type != "MESH":
            continue
        me, mw = ob.data, np.array(ob.matrix_world)
        V = np.array([v.co for v in me.vertices]); V = V @ mw[:3, :3].T + mw[:3, 3]
        E = np.array([e.vertices[:] for e in me.edges])
        if not len(E):
            continue
        a, b = V[E[:, 0]], V[E[:, 1]]
        low = np.minimum(a[:, 2], b[:, 2]) < lowZ
        a, b = a[low], b[low]
        n = np.maximum(2, np.ceil(np.linalg.norm(b - a, axis=1) / (0.5 * cell)).astype(int))
        for k in range(len(a)):
            t = np.linspace(0.0, 1.0, n[k])[:, None]
            pts.append(a[k] + (b[k] - a[k]) * t)
    P = np.concatenate(pts)[:, :2]
    lo, hi = P.min(0) - 1.0, P.max(0) + 1.0
    W, H = np.ceil((hi - lo) / cell).astype(int)
    g = np.zeros((H, W), bool)
    ij = ((P - lo) / cell).astype(int)
    g[ij[:, 1], ij[:, 0]] = True
    # the outside, flooded from the border; what it never reaches is the house
    out = np.zeros_like(g); out[0, :] = out[-1, :] = out[:, 0] = out[:, -1] = True; out &= ~g
    while True:
        grow = out.copy()
        grow[1:, :] |= out[:-1, :]; grow[:-1, :] |= out[1:, :]; grow[:, 1:] |= out[:, :-1]; grow[:, :-1] |= out[:, 1:]
        grow &= ~g
        if (grow == out).all():
            break
        out = grow
    house = ~out
    r = int(math.ceil(margin / cell))
    for _ in range(r):
        h2 = house.copy()
        h2[1:, :] |= house[:-1, :]; h2[:-1, :] |= house[1:, :]; h2[:, 1:] |= house[:, :-1]; h2[:, :-1] |= house[:, 1:]
        house = h2

    def keep(x, y):
        i = np.floor((np.asarray(y) - lo[1]) / cell).astype(int); j = np.floor((np.asarray(x) - lo[0]) / cell).astype(int)
        inb = (i >= 0) & (i < H) & (j >= 0) & (j < W)
        res = np.ones(np.shape(x), bool)
        res[inb] = ~house[i[inb], j[inb]]
        return res
    return keep, float(house.sum() * cell * cell)


def shed(sc, sink, reach, rays, step=0.03):
    """Where the stone sheds its rain, by bearing (0 to 1, the most 1): the form's top read as a height on a grid, a
    drop let fall on every cell running down its slope until it leaves the top; its bearings counted and smoothed."""
    xs = np.arange(-reach, reach + 1e-9, step); X, Y = np.meshgrid(xs, xs)
    Q = np.column_stack([X.ravel(), Y.ravel()])
    top = np.full(len(Q), np.nan)
    zs = np.arange(sink + 2.0, sink - 0.005, -0.01)
    for z in zs:
        inside = sc.field(np.column_stack([Q, np.full(len(Q), z)]), fine=False) < 0
        new = inside & np.isnan(top)
        top[new] = z
    h = top.reshape(X.shape)
    n = len(xs)

    def at(p):
        f = (p + reach) / step; i = np.clip(np.floor(f).astype(int), 0, n - 2); t = f - i
        return i, t

    def sample(px, py):
        j, tx = at(px); i, ty = at(py)
        a, b, c, d = h[i, j], h[i, j + 1], h[i + 1, j], h[i + 1, j + 1]
        return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
    ok = ~np.isnan(h.ravel()) & (h.ravel() > sink + 0.02)
    p = Q[ok].copy(); alive = np.ones(len(p), bool); exit_b = np.full(len(p), np.nan)
    e = 0.5 * step
    for _ in range(int(4 * reach / (0.5 * step))):
        if not alive.any():
            break
        q = p[alive]
        gx = (sample(q[:, 0] + e, q[:, 1]) - sample(q[:, 0] - e, q[:, 1])) / (2 * e)
        gy = (sample(q[:, 0], q[:, 1] + e) - sample(q[:, 0], q[:, 1] - e)) / (2 * e)
        g = np.column_stack([gx, gy]); gn = np.linalg.norm(g, axis=1)
        left = np.isnan(gn) | (np.abs(q).max(1) > reach - step)
        flat = ~left & (gn < 0.03)
        idx = np.flatnonzero(alive)
        exit_b[idx[left]] = np.arctan2(q[left, 0], q[left, 1])
        alive[idx[left | flat]] = False
        mv = ~left & ~flat
        p[idx[mv]] = q[mv] - 0.5 * step * g[mv] / gn[mv, None]
    b = exit_b[~np.isnan(exit_b)]
    phi = np.arange(rays) * 2 * math.pi / rays
    hist = np.histogram(np.mod(b, 2 * math.pi), bins=rays, range=(0, 2 * math.pi))[0].astype(float)
    k = np.exp(-0.5 * (np.minimum(np.arange(rays), rays - np.arange(rays)) * 360.0 / rays / 18.0) ** 2)
    sm = np.real(np.fft.ifft(np.fft.fft(hist) * np.fft.fft(k)))
    return np.clip(sm / max(sm.max(), 1e-9), 0, 1), phi


def rodrigues(axis, a):
    n = np.linalg.norm(axis)
    if n < 1e-9 or abs(a) < 1e-9:
        return np.eye(3)
    k = axis / n; X_ = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * X_ + (1 - math.cos(a)) * X_ @ X_


def write_png(path, rgb_lin, grey=False):
    """A linear RGB array (row 0 at the bottom) as an sRGB PNG through Blender's images."""
    a = np.clip(rgb_lin, 0, 1)
    if grey:
        a = np.repeat((a @ np.array([0.2126, 0.7152, 0.0722]))[..., None], 3, -1)
    s = np.where(a <= 0.0031308, 12.92 * a, 1.055 * a ** (1 / 2.4) - 0.055)
    H, W = s.shape[:2]
    im = bpy.data.images.new(os.path.basename(path), W, H, alpha=False)
    im.colorspace_settings.name = "sRGB"
    im.pixels.foreach_set(np.concatenate([s, np.ones((H, W, 1))], -1).astype(np.float32).ravel())
    im.filepath_raw = path; im.file_format = "PNG"; im.save()


def main():
    out = os.path.abspath(arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "gen", "ground")))
    os.makedirs(out, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    P = GR.pack(); T = P["tufts"]; SP = T["species"]
    seed = json.load(open(os.path.join(ROOT, "packs", "stavanger-1989", "pack.json")))["worldSeed"]
    key = (seed, "lt1-holm-tip", "ground")
    B = K["beside"]; box = G["box"]; Bk = G["bank"]
    keepHouse, houseM2 = house_mask(B["gen"], *G["house"])
    w = K["sculpt"]["chamfer"]["weather"]; weather = math.radians(w[0]); lee = weather + math.pi
    # the tufts' own shapes (tufts.py), level 0, to keep them out of the stone
    import tufts as TF  # noqa: E402  (foot.py put blender/parts/growth on the path)
    shapes = {}

    def shape(sp, v):
        if (sp, v) not in shapes:
            tris = TF.mesh(TF.blades(SP[sp], sp, v, seed), SP[sp], 0)
            shapes[(sp, v)] = np.array([vx[0] for tr in tris for vx in tr])
        return shapes[(sp, v)]

    # each part: its turf and drip lines, where it sheds, its stones (foot.py's)
    parts = []
    for pl in B["parts"]:
        X = next(x for x in MS.M["masses"] if x["id"] == pl["part"]); sc = SC.Sculpt(X)
        sink = X.get("sinkM", MS.M["judge"]["sinkM"]); rays = Bk["rays"]; phi = np.arange(rays) * 2 * math.pi / rays
        turf = FT.outline(sc, phi, sink)
        drip = np.max([FT.outline(sc, phi, sink + hh) for hh in np.linspace(0.0, Bk["dripM"], 6)], 0)
        sh, _ = shed(sc, sink, float(drip.max()) + 0.1, rays)
        rc = SC.Noise(*key, "reach", pl["part"]); rr = float(turf.mean()) / Bk["reachWaveM"]
        rv = rc(np.column_stack([rr * np.sin(phi), rr * np.cos(phi), np.full(rays, 0.5)])); rv = (rv - rv.min()) / max(np.ptp(rv), 1e-6)
        lw = 0.5 * (1 + np.cos(phi - lee)); ex = 0.5 * (1 + np.cos(phi - weather))
        reach = Bk["reachM"] * (Bk["reachVary"][0] + (Bk["reachVary"][1] - Bk["reachVary"][0]) * rv) * (1 + Bk["shed"] * sh + Bk["lee"] * lw)
        fj = os.path.join(ROOT, "cache", "rock", "kit", "gen", pl["part"], "foot.json")
        stones = json.load(open(fj)).get("placed", []) if os.path.exists(fj) else []
        parts.append({"id": pl["part"], "at": np.array(pl["at"], float), "sc": sc, "sink": sink, "turf": turf, "drip": drip,
                      "shed": sh, "lee": lw, "exposed": ex, "reach": reach, "rays": rays, "stones": stones})

    def polar(pt, x, y):
        dx, dy = np.asarray(x) - pt["at"][0], np.asarray(y) - pt["at"][1]
        b = np.mod(np.arctan2(dx, dy), 2 * math.pi); i = np.round(b / (2 * math.pi) * pt["rays"]).astype(int) % pt["rays"]
        return np.hypot(dx, dy), b, i

    def zone(pt, x, y):
        """0 to 1: how much of the bank a foot is in (1 from the turf line to the drip line, easing out by the reach)."""
        r, b, i = polar(pt, x, y)
        t0, td, re = pt["turf"][i], pt["drip"][i], pt["reach"][i]
        out_ = np.clip(1 - (r - td) / re, 0, 1) ** 1.3
        return np.where(r < td, 1.0, out_), r, b, i

    def keep(x, y):
        k = keepHouse(x, y)
        for pt in parts:
            r, b, i = polar(pt, x, y)
            k &= r > pt["turf"][i] + G["clearM"]
            for s in pt["stones"]:
                k &= np.hypot(x - pt["at"][0] - s[0], y - pt["at"][1] - s[1]) > s[2] * G["stoneClear"]
        return k

    rows, _ = GR.place_community(key, box, G["community"], keep=lambda x, y: keep(x, y), rules=P)
    # the bank: the community's own feet thinned where it takes over, its own laid in at its density
    xs = np.array([r[3] for r in rows]); ys = np.array([r[4] for r in rows])
    zw = np.zeros(len(rows))
    for pt in parts:
        zw = np.maximum(zw, zone(pt, xs, ys)[0])
    thin = HS.Stream(*key, "thin")
    rows = [r for r, z_ in zip(rows, zw) if thin.random() >= z_]
    inst = []  # (species, variant, R 3x3 with scale, foot, rank, hue, damp)

    def matrix(r, extra=np.eye(3)):
        Rz = rodrigues(UP, r[6]); Rl = rodrigues(np.array([-r[9], r[8], 0.0]), math.hypot(r[8], r[9]))
        return extra @ Rl @ Rz * r[7]
    sinkT = T["look"]["sink"]
    for r in rows:
        inst.append((r[0], r[1], matrix(r), np.array([r[3], r[4], -sinkT]), r[10], r[11], 0.0))
    nBank, nDrop = 0, 0
    for pt in parts:
        R0 = float(pt["drip"].max() + pt["reach"].max())
        cb = (pt["at"][0] - R0, pt["at"][1] - R0, pt["at"][0] + R0, pt["at"][1] + R0)
        C = GR._cells((*key, "bank", pt["id"]), cb, Bk["perSqm"])
        C = C[keep(C[:, 0], C[:, 1])]
        z_, r_, b_, i_ = zone(pt, C[:, 0], C[:, 1])
        under = r_ < pt["turf"][i_] + 0.5 * (pt["drip"][i_] - pt["turf"][i_]) * (pt["drip"][i_] > pt["turf"][i_] + 0.05)
        dens = z_ * np.where(under, Bk["under"], 1.0)
        sel = C[:, 2] < dens
        mix = Bk["mix"]; names = list(mix); cw = np.cumsum([mix[s] for s in names])
        for c, z1, r1, b1, i1, un in zip(C[sel], z_[sel], r_[sel], b_[sel], i_[sel], under[sel]):
            sp = names[min(int(np.searchsorted(cw, c[3] * cw[-1], side="right")), len(names) - 1)]
            v = int(c[6] * 4) % 4
            lift = Bk["tall"][0] + (Bk["tall"][1] - Bk["tall"][0]) * (0.5 * pt["shed"][i1] + 0.5 * pt["lee"][i1])
            s = (0.85 + 0.3 * c[5]) * (1 + z1 * (lift - 1)) * (1 - Bk["exposed"] * z1 * pt["exposed"][i1])
            if un:
                s *= Bk["underScale"]
            o = np.array([math.sin(b1), math.cos(b1), 0.0])
            a0 = math.radians(Bk["leanOut"][0] + (Bk["leanOut"][1] - Bk["leanOut"][0]) * c[7]) * z1
            row = (sp, v, "bank", c[0], c[1], 0.0, 2 * math.pi * c[4], s, (c[8] - 0.5) * 0.12, (c[9] - 0.5) * 0.12, c[10], c[1] % 1.0)
            pv = shape(sp, v); foot = np.array([c[0], c[1], -sinkT])
            done = None
            for k in range(Bk["tries"]):
                for shrink in (1.0, 0.8, 0.64):
                    M = matrix(row[:7] + (s * shrink,) + row[8:], rodrigues(np.cross(UP, o), a0 + math.radians(Bk["leanStep"]) * k))
                    Q = pv @ M.T + foot - np.r_[pt["at"][:2], 0.0] + [0.0, 0.0, pt["sink"]]
                    if (pt["sc"].field(Q, fine=False) > -0.005).all():
                        done = M
                        break
                if done is not None:
                    break
            if done is None:
                nDrop += 1
                continue
            damp = float(np.clip(z1 * (0.35 + 0.65 * pt["shed"][i1]) * (0.6 if un else 1.0), 0, 1))
            inst.append((sp, v, done, foot, float(c[10]), float((c[0] * 13.7 + c[1] * 7.3) % 1.0), damp))
            nBank += 1

    # the kinds, the bin
    kinds = {}
    for e in inst:
        kinds.setdefault((e[0], e[1]), []).append(e)
    season = G.get("season")
    data, K_ = [], []
    for (sp, v), es in sorted(kinds.items()):
        spec = SP[sp]; col = dict(spec, **(spec.get(season, {}) if season else {}))
        first = len(data)
        for e in es:
            data.append(np.r_[e[2].ravel(), e[3], e[4], e[5], e[6]])
        K_.append({"species": sp, "variant": v, "levels": [f"cache/growth/tufts/{sp}-{v}-L{l}.bin" for l in range(3)],
                   "radius": round(max(spec["height"][1], spec["width"][1]) * 1.6, 3),
                   "base": GR.lin(col["base"]).round(5).tolist(), "tip": GR.lin(col["tip"]).round(5).tolist(),
                   "damp": GR.lin(col.get("damp", col["tip"])).round(5).tolist(),
                   "seed": GR.lin(col.get("seed", "#a9a49a")).round(5).tolist(), "hue": spec["clumpHue"],
                   "first": first, "count": len(es)})
    D = np.array(data, np.float32)
    with open(os.path.join(out, "tufts.bin"), "wb") as f:
        f.write(struct.pack("<ii", len(D), D.shape[1])); f.write(D.tobytes())

    # the ground: the community's map, damper where the stones shed their rain
    px = G["px"]
    gmap, patch = GR.ground_map(key, box, px, G["community"], rules=P, wind=w[0])
    xs_ = box[0] + (np.arange(px[0]) + 0.5) * (box[2] - box[0]) / px[0]
    ys_ = box[1] + (np.arange(px[1]) + 0.5) * (box[3] - box[1]) / px[1]
    GX, GY = np.meshgrid(xs_, ys_)
    dampC = GR.lin(Bk["groundDamp"][1])
    for pt in parts:
        R0 = float(pt["drip"].max() + pt["reach"].max())
        near = np.hypot(GX - pt["at"][0], GY - pt["at"][1]) < R0 + 0.2
        z_, r_, b_, i_ = zone(pt, GX[near], GY[near])
        dmp = (z_ * (0.35 + 0.65 * pt["shed"][i_]) * Bk["groundDamp"][0])[:, None]
        gmap[near] = gmap[near] * (1 - dmp) + dampC * dmp
    write_png(os.path.join(out, "ground-Pc.png"), gmap)
    write_png(os.path.join(out, "ground-P.png"), gmap, grey=True)
    area = (box[2] - box[0]) * (box[3] - box[1]) - houseM2
    info = {"community": G["community"], "season": season, "box": box, "px": px, "maps": ["ground-Pc.png", "ground-P.png"],
            "draw": G["draw"], "look": T["look"], "stride": int(D.shape[1]), "kinds": K_,
            "counts": {"tufts": len(D), "bank": nBank, "bankDropped": nDrop, "perSqm": round(len(D) / area, 2),
                       "bySpecies": {s: sum(k["count"] for k in K_ if k["species"] == s) for s in sorted({k["species"] for k in K_})}},
            "parts": [{"id": pt["id"], "shedPeak": round(math.degrees(float(np.argmax(pt["shed"]) * 2 * math.pi / pt["rays"])), 1),
                       "reachM": [round(float(pt["reach"].min()), 2), round(float(pt["reach"].max()), 2)]} for pt in parts]}
    json.dump(info, open(os.path.join(out, "ground.json"), "w"), indent=1)
    print("[ground]", json.dumps(info["counts"]), json.dumps(info["parts"]))


if __name__ == "__main__":
    main()
