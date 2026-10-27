"""The walked corner's timber houses, built from their facts and baked, for Unity (LT1Houses).

Each house is assembled by blender/parts/house/house.py from its plan (blender/blockouts/heart_layout.py's building:
footprint, base, eave, roof, pitch), its record (fixtures/lt1-corner.json: era, built, dated events), the pack's
timber workings (packs/stavanger-1989/timber.json) and the date. Writes cache/houses/<name>.bin (R2B2 soups, Unity's
frame) and cache/houses/houses.json (one row a house, for the houses buffer: its index, id, era, built, wealth, dated
events, its coats on the date (blender/parts/house/coats.py, by the pack's paint.json) and its roof's covering).

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/houses.py -- \\
        [--houses C,D,E] [--out cache/houses] [--date 1989.8] [--pack packs/stavanger-1989] [--no-bake]
        [--tiers near,street,city]

Blender only for its ray tree (mathutils): nothing is made in a scene.
"""

import argparse
import json
import math
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("blender/resolver", "blender/blockouts", "blender/parts/house"):
    sys.path.insert(0, os.path.join(ROOT, p))

import numpy as np  # noqa: E402

import hashing as HS  # noqa: E402
import coats as CO  # noqa: E402
import house as HO  # noqa: E402  (blender/parts/house, not the old generator)


def facts_of(record):
    """A fixture building's record as the house assembler reads it: its era, the year it was built, its wealth and
    its dated events, oldest first."""
    events = sorted(record["events"], key=lambda e: (e["year"], e["id"]))
    built = next(e for e in events if e["kind"] == "built")
    return dict(id=record["id"], era=built["params"]["era"], built=built["year"],
                wealth=built["params"].get("wealth", 0), storeys=built["params"].get("storeys", 1000),
                with_=built["params"].get("with", []), events=[e for e in events if e["kind"] != "built"])


def _layout_key():
    """The layout's sources' hash: the plan cache holds while they are unchanged."""
    import hashlib
    h = hashlib.sha1()
    for p in ("blender/blockouts/heart_layout.py", "blender/blockouts/centre_land.py", "blender/resolver/terrain.py",
              "fixtures/lt1-corner.json"):
        h.update(open(os.path.join(ROOT, p), "rb").read())
    return h.hexdigest()


def plan_of(letters, pad=12.0, step=0.5):
    """Each house's plan (heart_layout's building), its footprint and the carved ground round it, sampled as
    heart_build samples it. Importing the layout takes over a minute, so they are kept in cache/houses-plan.json while
    the layout's sources are unchanged (generated, untracked)."""
    path = os.path.join(ROOT, "cache", "houses-plan.json")
    key = _layout_key()
    cached = json.load(open(path)) if os.path.exists(path) else {}
    if cached.get("key") != key:
        cached = dict(key=key, houses={})
    if all(x in cached["houses"] for x in letters):
        return cached["houses"]
    import centre_land as L
    import heart_layout as H
    for letter in letters:
        b = next(x for x in H.BUILDINGS if x["name"].startswith(letter + " ("))
        xs = [b["ox"] + dx for dx in (-b["w"] - pad, b["w"] + pad, 0.0)]
        ys = [b["oy"] + dy for dy in (-b["d"] - pad, b["d"] + pad, 0.0)]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        X, Y = np.meshgrid(np.arange(x0, x1 + step / 2, step), np.arange(y0, y1 + step / 2, step), indexing="ij")
        Z = H.carve(X, Y, L.heights(X, Y))
        cached["houses"][letter] = dict(b={k: v for k, v in b.items() if isinstance(v, (int, float, str))},
                                        fp=[list(map(float, xy)) for xy in H.footprint(b, 0.0)],
                                        ground=dict(x0=x0, y0=y0, step=step, z=Z.tolist()))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(cached, open(path, "w"))
    return cached["houses"]


def local_ground(g):
    """The carved ground round a house from its cached grid: bilinear between samples."""
    Z = np.asarray(g["z"])
    x0, y0, step = g["x0"], g["y0"], g["step"]

    def ground(x, y):
        u = min(max((x - x0) / step, 0), Z.shape[0] - 1.001)
        v = min(max((y - y0) / step, 0), Z.shape[1] - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
        c = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
        return float(a + (c - a) * fv)
    return ground


BOUNCE = 0.45  # the light a painted house's own faces send on: the mean albedo of its paint and wood in grey light


def bake_soup(soup, ground, lip):
    """What each piece of the house sees (bake.py's rays and reach): its share of open sky, of open ground, and its
    openness close by. The house only knows itself; the ground is the carved ground's height under each sample.

    A piece is one made thing's flat face (a board, a casing member, a stone's facet: its kind, seed and plane, its
    triangles joined by shared corners). It sees one light, or one that runs evenly across it (a field linear in
    position, fitted to samples inside its triangles), so the light is the same however the face is cut into
    triangles and nothing on a wall follows a triangle's edge. A curved face (a tile, a pipe) sees from each corner
    along the corner's own normal, so its light follows the curve.

    A ray that meets the house brings back one bounce: what the face it meets sees, times BOUNCE, so a rafter's side
    under a deep eave is lit by the boards round it, not black. A joint and the mortar behind the stones see past
    them (lime-mortar.json, jointView and jointFar). Under a level lip (a sill, a cap: a trim face looking down) the
    sky falls in a band (timber.json, push.lipShade), each face's band read at the face's middle, so it runs level."""
    import importlib.util
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec = importlib.util.spec_from_file_location("bake", os.path.join(ROOT, "blender/generators/bake.py"))
    BK = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(BK)
    verts = [Vector(p) for p in soup.p]
    nt = len(verts) // 3
    polys = [(3 * t, 3 * t + 1, 3 * t + 2) for t in range(nt)]
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    from soup import KINDS
    kinds = [int(soup.ch[3 * t][2]) for t in range(nt)]
    through = (KINDS["joint"], KINDS["mortar"])
    SPLIT = 0.01  # m2: a triangle larger than this is sampled at four points, a smaller one at its middle
    EVEN = 0.6  # m: a piece's light runs across it only as far as samples this far apart can tell

    def look(s, n, t):
        """One sample's rays: its share of sky, of ground and of openness close by, the faces it met, and whether
        it lies buried (most of its rays meet the back of a face: a point tucked under another part)."""
        u, w = BK._basis(n)
        o = s + n * BK.LIFT
        h = o.z - ground(o.x, o.y)
        sky = gnd = near = back = 0
        met = []
        for x, y, z in BK._FAN:
            d = u * x + w * y + n * z
            hit, hn, face, dist = tree.ray_cast(o, d, BK.REACH)
            while hit is not None and kinds[t] in through and kinds[face] == KINDS["stone"]:
                hit, hn, face, dist = tree.ray_cast(hit + d * 1e-4, d, BK.REACH)
            if hit is not None:
                near += dist < BK.NEAR
                if hn.dot(d) < 0.0:
                    met.append(face)
                else:
                    back += 1
                continue
            if d.z < -1e-4 and h > 0.0 and -h / d.z < BK.REACH:
                gnd += 1
            else:
                sky += 1
        k = float(len(BK._FAN))
        return [sky / k, gnd / k, 1.0 - near / k], met, back > 0.3 * k, sky + gnd == 0

    # the samples: inside a flat triangle (its middle, and three more toward its corners when it is large), at the
    # corners of a curved one
    normal, curved, samples = [], [], []
    for t in range(nt):
        a, b, c = verts[3 * t], verts[3 * t + 1], verts[3 * t + 2]
        cr = (b - a).cross(c - a)
        area = 0.5 * cr.length
        n = cr.normalized()
        normal.append(n)
        centre = (a + b + c) / 3.0
        bent = any((Vector(soup.nrm[3 * t + i]) - n).length > 1e-3 for i in range(3))
        curved.append(bent)
        mid = look(centre, n, t)
        if bent:
            for i, q in enumerate((a, b, c)):
                to = centre - q
                v = look(q + to * min(1.0, 0.003 / max(to.length, 1e-9)), Vector(soup.nrm[3 * t + i]).normalized(), t)
                samples.append((t, i, area, (list(mid[0]), mid[1], mid[2], mid[3]) if v[2] else v))
        else:
            samples.append((t, None, area, mid))
            if area > SPLIT:
                for q in (a, b, c):
                    v = look(centre * 0.5 + q * 0.5, n, t)
                    if not v[2]:
                        samples.append((t, centre * 0.5 + q * 0.5, area / 3.0, v))
    # a face met brings back the mean of what that triangle's samples see
    acc = [[0.0, 0.0, 0.0, 0] for _ in range(nt)]
    for t, _, _, v in samples:
        for j in range(3):
            acc[t][j] += v[0][j]
        acc[t][3] += 1
    face = [(a_[0] / a_[3], a_[1] / a_[3], a_[2] / a_[3]) if a_[3] else (0.0, 0.0, 1.0) for a_ in acc]
    k = float(len(BK._FAN))
    for _, _, _, v in samples:
        v[0][0] += BOUNCE * sum(face[f][0] for f in v[1]) / k
        v[0][1] += BOUNCE * sum(face[f][1] for f in v[1]) / k

    seen = [None] * (3 * nt)
    # curved triangles: each corner its own
    for t, i, _, v in samples:
        if curved[t]:
            seen[3 * t + i] = tuple(v[0])

    # flat triangles into pieces: kind, seed and plane, joined where they share a corner
    parent = list(range(nt))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    corner = {}
    for t in range(nt):
        if curved[t]:
            continue
        n = normal[t]
        key = (kinds[t], round(soup.ch[3 * t][4], 6), round(n.x * 25), round(n.y * 25), round(n.z * 25),
               round(n.dot(verts[3 * t]) / 0.005))
        for i in range(3):
            q = verts[3 * t + i]
            ck = key + (round(q.x * 2000), round(q.y * 2000), round(q.z * 2000))
            o = corner.setdefault(ck, t)
            ra, rb = root(o), root(t)
            if ra != rb:
                parent[rb] = ra
    pieces = {}
    for t in range(nt):
        if not curved[t]:
            pieces.setdefault(root(t), []).append(t)
    by_tri = {}
    for t, at, area, v in samples:
        if not curved[t]:
            by_tri.setdefault(t, []).append((at, area, v[0], v[3]))
    for tris in pieces.values():
        n = normal[tris[0]]
        u, w = BK._basis(n)
        pts = []
        for t in tris:
            centre = (verts[3 * t] + verts[3 * t + 1] + verts[3 * t + 2]) / 3.0
            for at, area, val, shut in by_tri.get(t, ()):
                pts.append((centre if at is None else at, area, val, shut))
        # a piece running into the house (a stack through the roof, a board behind a casing) is seen only where it
        # comes out: a sample shut in on every side is left out, unless the whole piece is shut in
        if any(not p_[3] for p_ in pts):
            pts = [p_ for p_ in pts if not p_[3]]
        pts = [p_[:3] for p_ in pts]
        if not pts:
            for t in tris:
                seen[3 * t:3 * t + 3] = [(0.0, 0.0, 1.0)] * 3
            continue
        W = sum(a_ for _, a_, _ in pts)
        c = sum((q * a_ for q, a_, _ in pts), Vector((0, 0, 0))) / W
        # weighted least squares of value = m + gu*(q-c).u + gw*(q-c).w, the slopes held back (ridge) so a small
        # piece sees one light
        su = sw = suu = sww = suw = 0.0
        for q, a_, _ in pts:
            x, y = (q - c).dot(u), (q - c).dot(w)
            su += a_ * x
            sw += a_ * y
            suu += a_ * x * x
            sww += a_ * y * y
            suw += a_ * x * y
        lam = W * EVEN * EVEN / 12.0 * 0.25
        corners = [verts[3 * t + i] for t in tris for i in range(3)]
        fit = []
        for j in range(3):
            vals = [val[j] for _, _, val in pts]
            m = sum(a_ * val[j] for _, a_, val in pts) / W
            bu = sum(a_ * (q - c).dot(u) * (val[j] - m) for q, a_, val in pts)
            bw = sum(a_ * (q - c).dot(w) * (val[j] - m) for q, a_, val in pts)
            A, B, D = suu + lam, suw, sww + lam
            det = A * D - B * B
            gu, gw = ((D * bu - B * bw) / det, (A * bw - B * bu) / det) if det > 1e-12 else (0.0, 0.0)
            lo, hi = min(vals), max(vals)
            m = min(max(m, lo), hi)
            # the slope held so no corner leaves what the samples saw (scaled whole, so it stays one even field)
            k_ = 1.0
            for q in corners:
                e = gu * (q - c).dot(u) + gw * (q - c).dot(w)
                if m + e > hi + 1e-9:
                    k_ = min(k_, (hi - m) / e)
                elif m + e < lo - 1e-9:
                    k_ = min(k_, (lo - m) / e)
            fit.append((m, gu * max(k_, 0.0), gw * max(k_, 0.0)))
        for t in tris:
            for i in range(3):
                q = verts[3 * t + i]
                x, y = (q - c).dot(u), (q - c).dot(w)
                seen[3 * t + i] = tuple(m + gu * x + gw * y for m, gu, gw in fit)

    # under a level lip: a standing face's band, read up from the face's middle at each corner's height
    S, B, P = lip["shade"], lip["bandMm"] * 0.001, lip["power"]
    trim = KINDS["trim"]
    faces = {}
    for t in range(nt):
        if abs(normal[t].z) < 0.5:
            faces.setdefault(soup.fid[t], []).append(t)
    up = Vector((0.0, 0.0, 1.0))
    for tris in faces.values():
        area = sum(((verts[3 * t + 1] - verts[3 * t]).cross(verts[3 * t + 2] - verts[3 * t])).length for t in tris)
        mid = sum((((verts[3 * t + 1] - verts[3 * t]).cross(verts[3 * t + 2] - verts[3 * t])).length *
                   (verts[3 * t] + verts[3 * t + 1] + verts[3 * t + 2]) / 3.0 for t in tris), Vector((0, 0, 0))) / max(area, 1e-12)
        n = normal[tris[0]]
        band = {}
        for t in tris:
            for i in range(3):
                z = round(verts[3 * t + i].z, 5)
                if z in band:
                    continue
                o = Vector((mid.x, mid.y, z)) + n * 0.002
                gone, f = 0.0, 1.0
                while gone < B:
                    hit, hn, hf, dist = tree.ray_cast(o, up, B - gone)
                    if hit is None:
                        break
                    gone += dist
                    if kinds[hf] == trim and hn.z < -0.9:
                        f = 1.0 - S * max(0.0, 1.0 - gone / B) ** P
                        break
                    o = hit + up * 1e-4
                    gone += 1e-4
                band[z] = f
        for t in tris:
            for i in range(3):
                f = band[round(verts[3 * t + i].z, 5)]
                if f < 1.0:
                    sk, gd, op = seen[3 * t + i]
                    seen[3 * t + i] = (sk * f, gd, op)
    return seen


def roof_of(facts, timber, date):
    """The roof's covering material and the year it was laid: the era's, unless a 'roof_retiled' event since."""
    year = facts["built"]
    for e in facts["events"]:
        if e["kind"] == "roof_retiled" and e["year"] <= date:
            year = e["year"]
    return dict(material=timber["workings"][facts["era"]]["roof"]["material"], year=year)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--houses", default="C")
    ap.add_argument("--out", default="cache/houses")
    ap.add_argument("--date", type=float, default=1989.8)
    ap.add_argument("--pack", default="packs/stavanger-1989")
    ap.add_argument("--timber", default="timber.json")
    ap.add_argument("--paint", default="paint.json")
    ap.add_argument("--no-bake", action="store_true")
    ap.add_argument("--tiers", default="near", help="the levels to write (timber.json, levels): near as L.bin, others as L.<tier>.bin")
    a = ap.parse_args(argv)
    out = os.path.join(ROOT, a.out)
    os.makedirs(out, exist_ok=True)
    timber = json.load(open(os.path.join(ROOT, a.pack, a.timber)))
    # each working's covering, as its material record lays it
    timber["covers"] = {w["roof"]["material"]: json.load(open(os.path.join(ROOT, a.pack, "materials", w["roof"]["material"] + ".json")))
                        for w in timber["workings"].values()}
    paint = json.load(open(os.path.join(ROOT, a.pack, a.paint)))
    fixture = json.load(open(os.path.join(ROOT, "fixtures/lt1-corner.json")))
    records = {r["id"]: r for r in fixture["buildings"]}
    lanes = {pl["id"]: pl["lane"] for pl in fixture["placements"]}
    seed = fixture["worldSeed"]
    rows = []
    plans = plan_of(a.houses.split(","))
    for index, letter in enumerate(a.houses.split(",")):
        b = plans[letter]["b"]
        hid = int(re.match(r".*?\((\d+)", b["name"]).group(1))
        facts = facts_of(records[hid])
        ground = local_ground(plans[letter]["ground"])
        for tier in a.tiers.split(","):
            t0 = time.time()
            soup, report = HO.build(b, facts, timber, ground, a.date, index, seed, lit_share=0.5, tier=tier)
            t1 = time.time()
            baked = None if a.no_bake else bake_soup(soup, ground, timber["push"]["lipShade"])
            soup.write(os.path.join(out, f"{letter}.bin" if tier == "near" else f"{letter}.{tier}.bin"), baked)
            print(f"[houses] {letter} {tier}: {report['triangles']} triangles, built {t1 - t0:.1f} s, baked {time.time() - t1:.1f} s")
        rows.append(dict(index=index, name=letter, id=hid, era=facts["era"], built=facts["built"],
                         wealth=facts["wealth"], events=facts["events"],
                         coats=CO.coats(facts, paint, seed, a.date, CO.scheme_of(paint, lanes.get(hid))), roof=roof_of(facts, timber, a.date),
                         fp=[round(c, 3) for xy in plans[letter]["fp"] for c in xy]))
        print(f"[houses] {letter} ({hid}, {facts['era']} {facts['built']}): {report['windows']} windows, roof {report['roof']}")
        for w, r in report["walls"].items():
            print(f"[houses]   {w}: {r}")
    json.dump(dict(date=a.date, pack=a.pack, paint=a.paint, houses=rows), open(os.path.join(out, "houses.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
