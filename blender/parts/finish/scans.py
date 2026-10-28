"""Ways B and C's tileables, from CC0 scans, in the encoding tiles.py writes (way A's), so one shader reads all three.

    Blender -b --factory-startup -P blender/parts/finish/scans.py -- --gen <corner.py's out> --cache cache/finish

Reads the scans named in finish.json ("scans"; the files in blender/parts/finish/scans/, logged in
docs/research/downloads.md) and writes into <cache>/out:
  scan-<name>.png     R the under layer's L*/100, G the surface's L*/100, B breakup, A height (as tiles.py)
  scan-<name>-n.png   the scan's own normal, packed with its gloss as a smoothness offset (finishlib.pack_normal)
  unity.json          the Unity scene's digest of the materials (LT1Finish.cs)
  scans.json          each tile's size in metres (the shader scales UV0 by tileable metres / these) and, for a
                      painted tile, the share of its paint the scan has already lost (way B's page asks for that)
Each scan keeps its own structure and loses its colour: its lightness is remapped about its material's (finish.json)
at `contrast` times its own spread. A painted scan is split into paint and bare wood by colour, each remapped about
its own layer's lightness and filled in under the other, so the page can move the loss (way C) or leave the scan's
own (way B). The cladding's tile is fitted to the house's courses (corner.py's meta), one plank face per course.
Nothing finer than `killMm` survives.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def HS_unit(key, *parts):
    return HS.unit(HS.h(key, *parts))

FILES = {
    "polyhaven": ("{}_diff_1k.jpg", "{}_disp_1k.jpg", "{}_nor_gl_1k.jpg", "{}_rough_1k.jpg"),
    "ambientcg": ("{}_Color.jpg", "{}_Displacement.jpg", "{}_NormalGL.jpg", "{}_Roughness.jpg"),
}


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}


def lab(rgb):
    """sRGB-encoded (h, w, 3) to CIE L* and b* (D65)."""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    Z = lin @ np.array([0.0193, 0.1192, 0.9505])
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)  # noqa: E731
    return 116 * f(Y) - 16, 200 * (f(Y) - f(Z / 1.089))


def load(spec):
    d = os.path.join(HERE, "scans", spec["dir"])
    names = [n.format(spec["stem"]) for n in FILES[spec["maps"]]]
    diff, disp, nor, rough = (FL.read(os.path.join(d, n)) for n in names)
    L, b = lab(diff[..., :3])
    n = nor[..., :3] * 2.0 - 1.0
    ch = {"L": L, "b": b, "h": disp[..., 0], "nx": n[..., 0], "ny": n[..., 1], "nz": n[..., 2],
          "smooth": 1.0 - rough[..., 0]}
    if spec.get("rotate"):
        # the grain runs up the scan: turn it so u runs along the grain, and the normal with it
        ch = {k: np.rot90(v, -1) for k, v in ch.items()}
        ch["nx"], ch["ny"] = -ch["ny"].copy(), ch["nx"].copy()
    return ch


def down(a, k):
    if k <= 1:
        return a
    h, w = a.shape[0] // k * k, a.shape[1] // k * k
    return a[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def seams(ch, margin_px, gap_px):
    """The rows of the scan's plank faces: between its seams (rows both low and dark, each the deepest within
    `gap_px` of it), less a margin. Returns [(start, stop)] in row order, the last wrapping past the top."""
    z = lambda a: (a - a.mean()) / max(a.std(), 1e-9)  # noqa: E731
    prof = z(ch["h"].mean(axis=1)) + z(ch["L"].mean(axis=1))
    prof = FL.blur(prof[:, None], 1, axis=0)[:, 0]
    n = prof.size
    centres = []
    for r in range(n):
        win = prof[np.arange(r - gap_px, r + gap_px + 1) % n]
        if prof[r] <= win.min() and prof[r] < -1.0:
            centres.append(r)
    faces = []
    for i, c in enumerate(centres):
        nxt = centres[(i + 1) % len(centres)] + (n if i + 1 == len(centres) else 0)
        if nxt - c > 2 * margin_px + 4:
            faces.append((c + margin_px, nxt - margin_px))
    return faces


def stack(ch, faces, rows, fade):
    """Plank faces stacked across v to `rows`, each join cross-faded over `fade` rows, the stack wrapping."""
    n = next(iter(ch.values())).shape[0]
    order = []
    total = 0
    i = 0
    while total < rows + fade:
        a, b = faces[i % len(faces)]
        order.append((a, b))
        total += (b - a) - fade
        i += 1
    out = {k: [] for k in ch}
    w = None
    for a, b in order:
        idx = np.arange(a, b) % n
        piece = {k: v[idx] for k, v in ch.items()}
        if w is None:
            out = {k: piece[k].copy() for k in ch}
            w = True
            continue
        t = np.linspace(0, 1, fade + 2)[1:-1][:, None]
        for k in ch:
            prev = out[k]
            blend = prev[-fade:] * (1 - t) + piece[k][:fade] * t
            out[k] = np.concatenate([prev[:-fade], blend, piece[k][fade:]], axis=0)
    # wrap: fade the stack's end into its start
    for k in ch:
        a = out[k]
        t = np.linspace(0, 1, fade + 2)[1:-1][:, None]
        head = a[:fade] * t + a[rows:rows + fade] * (1 - t)
        out[k] = np.concatenate([head, a[fade:rows]], axis=0)
    return out


def fit_courses(ch, faces, courses, rows, metres_v, key):
    """The cladding's tile fitted to the house's courses: its UV0 is the wall's own height, so each course of
    boards takes one whole plank face of the scan, chosen and shifted along by seed, stretched across the grain to
    the course's exposure. The faces meet at the butts, under the laps' shadow, never across a board."""
    n_cols = next(iter(ch.values())).shape[1]
    z = (np.arange(rows) + 0.5) / rows * metres_v
    zs = list(courses)
    step = float(np.mean(np.diff(zs)))
    while zs[-1] < metres_v:
        zs.append(zs[-1] + step)
    while zs[0] > 0:
        zs.insert(0, zs[0] - step)
    out = {k: np.zeros((rows, n_cols)) for k in ch}
    for i in range(len(zs) - 1):
        z0, z1 = zs[i], zs[i + 1]
        sel = (z >= z0) & (z < z1)
        if not sel.any():
            continue
        a, b = faces[int(HS_unit(key, i, "face") * len(faces)) % len(faces)]
        t = (z[sel] - z0) / (z1 - z0)
        fr = a + t * (b - a - 1)
        r0 = np.floor(fr).astype(np.int64)
        w = (fr - r0)[:, None]
        shift = int(HS_unit(key, i, "along") * n_cols)
        nr = next(iter(ch.values())).shape[0]
        for k, v in ch.items():
            lo, hi = v[r0 % nr], v[(r0 + 1) % nr]
            out[k][sel] = np.roll(lo * (1 - w) + hi * w, shift, axis=1)
    return out


def tileable_crop(ch, x0, y0, w, h):
    """A crop made to wrap: blended with itself turned half a tile, the turned copy covering the crop's edges."""
    out = {}
    yy, xx = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w), indexing="ij")
    wc = np.clip(1.0 - np.maximum(np.abs(xx), np.abs(yy)), 0, 1) ** 0.7
    wc = wc / max(wc.max(), 1e-6)
    for k, v in ch.items():
        c = v[y0:y0 + h, x0:x0 + w]
        r = np.roll(np.roll(c, h // 2, 0), w // 2, 1)
        out[k] = c * wc + r * (1 - wc)
    return out


def flattest(ch, w, h):
    """The crop window of the scan whose face is plainest: least relief and no deep shadow (a tile's own face)."""
    hgt, L = ch["h"], ch["L"]
    gy, gx = np.gradient(hgt)
    rough = np.hypot(gx, gy)
    best, at = np.inf, (0, 0)
    H, W = hgt.shape
    dark = np.percentile(L, 30)
    for y in range(0, H - h, max(1, h // 4)):
        for x in range(0, W - w, max(1, w // 4)):
            win = (slice(y, y + h), slice(x, x + w))
            score = rough[win].mean() + 0.02 * max(0.0, dark - L[win].min())
            if score < best:
                best, at = score, (x, y)
    return at


def remap(L, mask, target, contrast):
    m = L[mask].mean() if mask.any() else L.mean()
    return target + contrast * (L - m)


def fill(a, mask, radius):
    """Where `mask` is false, the masked blur of `a`, widening until every texel is reached (a layer's lightness
    carried in under the other layer)."""
    out = a.copy()
    done = mask.copy()
    for r in (radius, radius * 3, radius * 9, radius * 27):
        f = FL.blur(a, r, mask)
        reach = FL.blur(mask.astype(np.float64), r) > 1e-4
        take = (~done) & reach
        out = np.where(take, f, out)
        done |= take
        if done.all():
            break
    return np.where(done, out, a[mask].mean())


def build(name, spec, mat, tile_m, tile_px, ts, courses=None):
    ch = load(spec)
    src_px = ch["L"].shape[1]
    src_mm = spec["metres"] * 1000.0 / src_px
    info = {}
    if spec["mode"] == "planks":
        # to the tileable's own grid (2 m over 1,024 px), plank faces stacked to fill it
        k = max(1, round((tile_m * 1000.0 / tile_px) / src_mm))
        ch = {c: down(v, k) for c, v in ch.items()}
        mm = src_mm * k
        faces = seams(ch, max(1, round(spec["seamMarginMm"] / mm)), max(2, round(spec["seamGapMm"] / mm)))
        info["faces"] = len(faces)
        reps = max(1, round(tile_px / ch["L"].shape[1]))
        ch = {c: np.tile(v, (1, reps))[:, :tile_px] for c, v in ch.items()}
        if courses is not None:
            mv = spec["fitCourses"]
            ch = fit_courses(ch, faces, courses, round(tile_px * mv / tile_m), mv, HS.h("finish", "scan", name))
            metres = [tile_m, mv]
        else:
            ch = stack(ch, faces, tile_px, fade=3)
            metres = tile_m
    elif spec["mode"] == "crop":
        w, h = (round(v / src_mm) for v in spec["cropMm"])
        x0, y0 = flattest(ch, w, h)
        ch = tileable_crop(ch, x0, y0, w, h)
        metres = [w * src_mm / 1000.0, h * src_mm / 1000.0]
        info["crop"] = [x0, y0, w, h]
    else:
        metres = spec["metres"]
    px_mm = (metres if np.isscalar(metres) else metres[0]) * 1000.0 / ch["L"].shape[1]
    r = max(0, round(spec["killMm"] / px_mm / 2))
    if r:
        ch = {c: FL.blur(v, r) for c, v in ch.items()}
    nrm = np.stack([ch["nx"] * spec["normalStrength"], ch["ny"] * spec["normalStrength"], ch["nz"]], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    hgt = (ch["h"] - ch["h"].mean()) / max(ch["h"].std() * 3, 1e-6)
    if "paintBlueB" in spec:
        lo, hi = spec["paintBlueB"]
        p = FL.blur(FL.smoothstep(lo, hi, -ch["b"]), 1)
        painted = p > 0.5
        paint = fill(remap(ch["L"], painted, mat["paint"]["L"], spec["contrast"]), painted, 4)
        under = fill(remap(ch["L"], ~painted, mat["under"]["L"], spec["contrast"]), ~painted, 4)
        # losses grow from the scan's own bare cores outward as the page asks for more, and shrink into them as it
        # asks for less
        bare = 1.0 - p
        breakup = bare + 0.35 * FL.blur(bare, 6) + 0.02 * (ch["L"] - ch["L"].mean()) / ch["L"].std()
        sm = ch["smooth"]
        gloss = spec["glossContrast"] * np.where(painted, sm - sm[painted].mean(), sm - sm[~painted].mean())
        info["lostShare"] = round(float((~painted).mean()), 4)
    else:
        everywhere = np.ones_like(ch["L"], bool)
        paint = remap(ch["L"], everywhere, mat["paint"]["L"], spec["contrast"])
        under = remap(ch["L"], everywhere, mat["under"]["L"], spec["contrast"])
        breakup = 1.0 - FL.blur((ch["L"] - ch["L"].mean()) / ch["L"].std(), 6)
        gloss = spec["glossContrast"] * (ch["smooth"] - ch["smooth"].mean())
    return {"under": under, "paint": paint, "breakup": breakup, "height": hgt, "normal": nrm, "gloss": gloss,
            "metres": metres, "info": info}


def write(out, name, t):
    b = FL.equalise(t["breakup"])
    rgba = np.stack([t["under"] / 100.0, t["paint"] / 100.0, b, 0.5 + 0.5 * np.clip(t["height"], -1, 1)], -1)
    FL.write(os.path.join(out, f"scan-{name}.png"), rgba)
    FL.write(os.path.join(out, f"scan-{name}-n.png"), FL.pack_normal(t["normal"], t["gloss"]))
    print(f"[scans] {name}: {t['metres']} m, under {t['under'].mean():.1f}±{t['under'].std():.1f} surface "
          f"{t['paint'].mean():.1f}±{t['paint'].std():.1f} {t['info']}")


def main():
    a = args()
    out = os.path.join(os.path.abspath(a["cache"]), "out")
    spec = json.load(open(os.path.join(HERE, "finish.json")))
    corner = json.load(open(os.path.join(HERE, "corner.json")))
    tile_m, tile_px = corner["tileable"]["metres"], corner["tileable"]["size"]
    ts = corner["trimSheet"]
    S, M = spec["scans"], spec["materials"]
    courses = json.load(open(os.path.join(os.path.abspath(a["gen"]), "corner.json")))["courses"]
    side = {}
    for name, mat in (("painted-board", "cladding"), ("sheet", "sheet"), ("batten", "batten"), ("stone", "stone"),
                      ("tile", "tiles"), ("zinc", "zinc")):
        fit = courses if "fitCourses" in S[name] else None
        t = build(name, S[name], M[mat], tile_m, tile_px, ts, fit)
        write(out, name, t)
        side[name] = {"metres": t["metres"], **t["info"]}
        if name == "painted-board":
            # the trim sheet from the same scan, about the trims' lightness, with the street half's bevels
            tr = build("trim-sheet", S["painted-board"], M["trims"], ts["metres"], ts["size"], ts)
            vm = (np.arange(ts["size"]) + 0.5) / ts["size"] * ts["metres"]
            bevel, wear = FL.trim_bevels(vm, ts)
            bh = np.repeat(bevel[:, None], ts["size"], 1)
            nb = FL.normal_from_height(bh, ts["metres"] / ts["size"], wrap=True) * 2.0 - 1.0
            tr["normal"] = FL.blend_normals(nb, tr["normal"])
            tr["breakup"] = FL.equalise(tr["breakup"]) + S["trim-sheet"]["bevelBreakup"] * wear[:, None]
            write(out, "trim-sheet", tr)
            side["trim-sheet"] = {"metres": tr["metres"], **tr["info"]}
    json.dump(side, open(os.path.join(out, "scans.json"), "w"), indent=1)
    # the Unity scene's digest (LT1Finish.cs reads it with JsonUtility, which takes no dictionaries)
    tiles = {"cladding": "painted-board", "trims": "trim-sheet", "sheet": "sheet", "batten": "batten",
             "stone": "stone", "tiles": "tile", "zinc": "zinc"}
    two = lambda m: m if isinstance(m, list) else [m, m]  # noqa: E731
    sh = spec["marks"]["shade"]
    digest = {
        "mats": [{"name": k, "tile": tiles[k], "painted": 1 if v["painted"] else 0, "paintSmooth": v["paint"]["smooth"],
                  "paintFlat": v["paint"].get("flat", 1.0), "underSmooth": v["under"]["smooth"], "scanMetres": two(side[tiles[k]]["metres"])}
                 for k, v in M.items()],
        "tileMetres": tile_m, "dirtL": sh["dirtL"], "waterL": sh["waterL"], "cavityL": sh["cavityL"],
        "lapDark": sh["lapDark"], "lapReach": sh["lapReachMm"] / 1000.0,
        "lapScale": json.load(open(os.path.join(FL.ROOT, "blender", "parts", "finish", "corner.json")))["lapReach"],
        "groundL": spec["ground"]["L"], "groundSmooth": spec["ground"]["smooth"],
    }
    json.dump(digest, open(os.path.join(out, "unity.json"), "w"), indent=1)
    print(f"[scans] wrote {out}")


main()
