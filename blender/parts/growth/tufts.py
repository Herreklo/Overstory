"""Tufts: the heath's and the weeds' plants as small fans of tapered blades (the art-direction page, The growth: spiky,
varied silhouettes, never round blobs), each species a function of its pack data (packs/<pack>/growth.json, tufts,
species), a few seeded variants each, at three levels.

How the best studios build it (reviews/lt1/growth/corner/craft.md): geometry blades, not cards (alpha testing is the
expensive part and puffs crowns out far off); each blade a tapered ribbon along a curve, joined into a clump whose
middle sets their lean, so a clump fans out and never domes (Ghost of Tsushima); a clump's normals bent toward one
dome over it so the clump lights as one mass (Bad North), dark at the root and light at the tip; the far levels
are the near one's tallest blades, widened, so the silhouette's spikes hold at every distance (Horizon: build the
far levels first and keep their outline).

A tuft is a fixed part: its geometry claims nothing (non-semantic texture, seeded from its species and variant). Where
the tufts stand is the generator's (blender/generators/growth.py, place_tufts), from the record.

Each mesh is an R2B2 triangle soup (as unity/Assets/Code/Editor/LT1R2b.cs, Load, reads it), in the street's frame
(x east, y north, z up, metres) about the tuft's foot, written in Unity's (x, z, y). Its vertices carry:
  uv0  x across the blade (-1 to 1, 0 at a tip), y how far up it (0 root, 1 tip)
  uv1  x how far out from the clump's middle the blade stands (0 to 1), y the blade's own seed (0 to 1)
  uv2  x what it is: 0 a blade or stem, 1 a seed pod; y its height over the tuft's foot over the tuft's height
  uv3  xy, uv4 x: the point on the blade's middle line the vertex stands across from (Unity's frame), so a far blade can
       be widened to a least width on screen about it; uv4 y: the blade's half width at its root (m)
The normal is the clump's dome over the vertex, not the blade's own.

    $PY blender/parts/growth/tufts.py [--out cache/growth/tufts] [--variants 4]
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
import hashing as HS  # noqa: E402
import growth  # noqa: E402

UP = np.array([0.0, 0.0, 1.0])


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def blades(spec, species, variant, seed):
    """The tuft's blades at its fullest (level 0): each its foot, its curve's three points, its width and seeds,
    tallest first (the far levels keep the first of them)."""
    S = HS.Stream(seed, "tuft", species, variant)
    H = S.uniform(*spec["height"])
    W = S.uniform(*spec["width"])
    R = 0.5 * W
    n = spec["blades"][0]
    lean0, lean1 = spec["lean"]
    curl = spec["curl"]
    out = []
    for b in range(n):
        # the feet gather in the clump's middle; the first few are its tallest spikes
        r = 0.42 * R * math.sqrt(S.random())
        th = 2.0 * math.pi * S.random()
        foot = np.array([r * math.cos(th), r * math.sin(th), 0.0])
        tall = 0.92 + 0.08 * S.random() if b < 3 else 0.42 + 0.5 * S.random() ** 0.7
        h = H * tall
        # it leans out from the middle (more the further out it stands), its way turned a little
        away = th + S.uniform(-0.55, 0.55) if r > 1e-4 else 2.0 * math.pi * S.random()
        o = np.array([math.cos(away), math.sin(away), 0.0])
        lean = (lean0 + (lean1 - lean0) * (0.3 + 0.7 * r / (0.42 * R))) * S.uniform(0.75, 1.25)
        a = min(lean, 1.0) * math.radians(62.0) * (0.55 if b < 3 else 1.0)
        d = math.cos(a) * UP + math.sin(a) * o
        c = curl * S.uniform(0.5, 1.3)
        p0 = foot
        p1 = foot + d * h * 0.55
        p2 = foot + d * h + (o * 0.35 - UP * 0.5) * c * h
        side = _unit(np.cross(UP, o))
        tw = S.uniform(-0.45, 0.45)
        side = _unit(side * math.cos(tw) + d * 0.0 + np.cross(d, side) * math.sin(tw))
        out.append({"p": (p0, p1, p2), "side": side, "w": spec["bladeWidth"] * S.uniform(0.75, 1.25),
                    "r": r / max(0.42 * R, 1e-6), "seed": S.random(), "out": o})
    out[3:] = sorted(out[3:], key=lambda bl: -np.linalg.norm(bl["p"][2] - bl["p"][0]))
    pods = []
    if "pods" in spec:
        for k in range(spec["pods"][0]):
            st = out[k % n]
            t = S.uniform(0.62, 0.95)
            base = _bez(st["p"], t)
            o = _unit(st["out"] + np.array([S.uniform(-0.6, 0.6), S.uniform(-0.6, 0.6), 0.0]))
            L = S.uniform(0.06, 0.12)
            tip = base + _unit(UP * S.uniform(0.6, 1.4) + o) * L + o * L * 0.3
            pods.append({"base": base, "tip": tip, "side": _unit(np.cross(UP, o)), "seed": S.random(), "stem": k % n})
    return {"H": H, "R": R, "blades": out, "pods": pods}


def _bez(p, t):
    return (1 - t) ** 2 * p[0] + 2 * (1 - t) * t * p[1] + t * t * p[2]


def mesh(tuft, spec, level):
    """The tuft's triangles at a level: the tallest of its blades, fewer segments, widened to keep its cover."""
    n0 = spec["blades"][0]
    n = spec["blades"][level]
    segs = spec["segments"][level]
    widen = math.sqrt(n0 / n) * (1.25 if level == 2 else 1.0)
    H, R = tuft["H"], tuft["R"]
    tris = []

    def normal(p):
        # the clump's dome over the point: one mass, lighter on top
        q = np.array([p[0] / (R * 1.3), p[1] / (R * 1.3), 0.8 + p[2] / max(H, 1e-3)])
        return _unit(q)

    def vert(p, across, up, bl, part, centre=None, half=0.0):
        c = p if centre is None else centre
        return (p, normal(p), (across, up), (bl["r"], bl["seed"]), (part, p[2] / max(H, 1e-3)),
                (c[0], c[2]), (c[1], half))

    for bl in tuft["blades"][:n]:
        ring = []
        half = 0.5 * bl["w"] * widen
        for i in range(segs):
            t = i / segs
            c = _bez(bl["p"], t)
            w = half * (1.0 - t) ** 0.85
            ring.append((vert(c - bl["side"] * w, -1.0, t, bl, 0.0, c, half),
                         vert(c + bl["side"] * w, 1.0, t, bl, 0.0, c, half)))
        tip = vert(_bez(bl["p"], 1.0), 0.0, 1.0, bl, 0.0, None, half)
        for i in range(segs - 1):
            (a, b), (c, d) = ring[i], ring[i + 1]
            tris += [(a, b, d), (a, d, c)]
        a, b = ring[-1]
        tris.append((a, b, tip))
    if "pods" in spec:
        for pd in tuft["pods"][:spec["pods"][level]]:
            w = 0.004 * widen
            bl = {"r": 1.0, "seed": pd["seed"]}
            tris.append((vert(pd["base"] - pd["side"] * w, -1.0, 0.0, bl, 1.0, pd["base"], w),
                         vert(pd["base"] + pd["side"] * w, 1.0, 0.0, bl, 1.0, pd["base"], w),
                         vert(pd["tip"], 0.0, 1.0, bl, 1.0, None, w)))
    return tris


def write_r2b(path, tris):
    """An R2B2 soup: its vertices in Unity's frame (x, z, y), the winding turned as the loader expects."""
    vs = [v for t in tris for v in t]
    with open(path, "wb") as f:
        f.write(b"R2B2")
        f.write(struct.pack("<i", len(vs)))
        for v in vs:
            p = v[0]
            f.write(struct.pack("<3f", p[0], p[2], p[1]))
        for v in vs:
            nn = v[1]
            f.write(struct.pack("<3f", nn[0], nn[2], nn[1]))
        for k in range(8):
            for v in vs:
                uv = v[2 + k] if k < 5 else (0.0, 0.0)
                f.write(struct.pack("<2f", *uv))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "cache", "growth", "tufts"))
    ap.add_argument("--variants", type=int, default=4)
    a = ap.parse_args()
    P = growth.pack()
    T = P["tufts"]
    seed = json.load(open(os.path.join(ROOT, "packs", "stavanger-1989", "pack.json")))["worldSeed"]
    os.makedirs(a.out, exist_ok=True)
    manifest = {"pack": "stavanger-1989", "variants": a.variants, "species": {}}
    budget = T["budget"]["trisPerTuft"]
    over = []
    for name, spec in T["species"].items():
        rows = []
        for v in range(a.variants):
            tuft = blades(spec, name, v, seed)
            row = {"variant": v, "height": round(tuft["H"], 3), "radius": round(max(tuft["H"], tuft["R"] * 1.6), 3), "levels": []}
            for level in range(3):
                tris = mesh(tuft, spec, level)
                fn = f"{name}-{v}-L{level}.bin"
                write_r2b(os.path.join(a.out, fn), tris)
                sha = hashlib.sha256(open(os.path.join(a.out, fn), "rb").read()).hexdigest()[:16]
                row["levels"].append({"file": fn, "tris": len(tris), "sha256": sha})
                if len(tris) > budget[level]:
                    over.append(f"{fn}: {len(tris)} > {budget[level]}")
            rows.append(row)
        manifest["species"][name] = rows
    with open(os.path.join(a.out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    for name, rows in manifest["species"].items():
        print(f"{name:11s}", " ".join(f"L{l}:{max(r['levels'][l]['tris'] for r in rows):3d}" for l in range(3)))
    if over:
        print("over budget:", *over, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
