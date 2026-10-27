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


def bake_soup(soup, ground):
    """What each triangle's corners see (bake.py's rays and reach): their share of open sky, of open ground, and
    their openness close by. The house only knows itself; the ground is the carved ground's height under each sample. A ray that
    meets the house itself brings back one bounce: what the face it meets sees of sky and ground, times BOUNCE, so a
    rafter's side under a deep eave is lit by the boards round it, not black. A joint (the slot between stones drawn as
    one face, from the street tier) and the mortar behind the stones see past them: their shade is in the joint's share
    (lime-mortar.json, jointView and jointFar). A stone's facet sees one light, the mean of its triangles'."""
    import importlib.util
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec = importlib.util.spec_from_file_location("bake", os.path.join(ROOT, "blender/generators/bake.py"))
    BK = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(BK)
    verts = [Vector(p) for p in soup.p]
    polys = [(i, i + 1, i + 2) for i in range(0, len(verts), 3)]
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    from soup import KINDS
    kinds = [int(soup.ch[3 * t][2]) for t in range(len(polys))]
    through = (KINDS["joint"], KINDS["mortar"])
    INSET = 0.003  # a corner's sample stands this far in from the corner, toward the triangle's middle

    def look(s, n, dirs, t):
        """One sample's rays: its share of sky, of ground and of openness close by, the faces it met, and whether
        it lies buried (most of its rays meet the back of a face: a corner tucked under another part)."""
        o = s + n * BK.LIFT
        h = o.z - ground(o.x, o.y)
        sky = gnd = near = back = 0
        met = []
        for d in dirs:
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
        k = float(len(dirs))
        return (sky / k, gnd / k, 1.0 - near / k), met, back > 0.3 * k

    # each corner of a triangle sees from its own corner, so the light runs smoothly over a face cut into many
    # triangles (a board cut at a casing and at its marks) instead of stepping at each cut; a buried corner takes the
    # triangle's middle
    first, hits = [], []
    for t in range(len(polys)):
        a, b, c = verts[3 * t], verts[3 * t + 1], verts[3 * t + 2]
        n = (b - a).cross(c - a).normalized()
        u, w = BK._basis(n)
        centre = (a + b + c) / 3.0
        dirs = [u * x + w * y + n * z for x, y, z in BK._FAN]
        mid = look(centre, n, dirs, t)
        for q in (a, b, c):
            to = centre - q
            s = q + to * min(1.0, INSET / max(to.length, 1e-9))
            v = look(s, n, dirs, t)
            v = mid if v[2] else v
            first.append(v[0])
            hits.append((v[1], float(len(dirs))))
    # a face met brings back the mean of what its corners see
    face = [tuple(sum(first[3 * f + i][j] for i in range(3)) / 3.0 for j in range(3)) for f in range(len(polys))]
    seen = []
    for (sky, gnd, op), (met, k) in zip(first, hits):
        sky += BOUNCE * sum(face[f][0] for f in met) / k
        gnd += BOUNCE * sum(face[f][1] for f in met) / k
        seen.append((sky, gnd, op))
    # a stone's facet is one plane a hand wide: it sees one light, whatever triangles it is cut into (else each
    # triangle of its fan shows as a shard)
    facets = {}
    for t in range(len(polys)):
        if kinds[t] != KINDS["stone"]:
            continue
        a, b, c = verts[3 * t], verts[3 * t + 1], verts[3 * t + 2]
        n = (b - a).cross(c - a)
        area = n.length
        if area < 1e-12:
            continue
        n = n / area
        key = (round(soup.ch[3 * t][4], 6), round(n.x * 50), round(n.y * 50), round(n.z * 50))
        facets.setdefault(key, []).append((t, area))
    for tris in facets.values():
        total = sum(w for _, w in tris)
        mean = tuple(sum(seen[3 * t + j][i] * w for t, w in tris for j in range(3)) / (3.0 * total) for i in range(3))
        for t, _ in tris:
            seen[3 * t:3 * t + 3] = [mean] * 3
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
            baked = None if a.no_bake else bake_soup(soup, ground)
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
