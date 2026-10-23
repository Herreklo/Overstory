"""R2a's counter (reviews/lt1/port/2b/r2a/stones/plan.md, The measures; the design's SN4, SN7, SN8 and SN9:
reviews/lt1/port/2b/design.md), on the frames Editor/LT1R2a.cs writes. It uses r0b_count's reading, L* and marks, and
copies none of them:

    frames/<piece>/<stand>/<moment>/<look>/<config>/<view>.png     the player's frames (2560 x 1440)
    frames/<piece>/<stand>/ids/<level>/<view>-{ids,normals,mask}.png   what the mesh is at each pixel (R2aIds.shader)
    frames/<piece>/<stand>/ids/triangles.json                      SN8's triangle measures, from the mesh
    frames/<piece>/<stand>/dolly/<moment>/dolly.json, <look>/<level>/NNN.png   the levels in motion (crops)

A config is a level (L0, L1) with its changes: -noline (L1's lit line off), -flat (the patches off), -facets2 and
-nominor (the arms), -nomotes (the air's motes off, a control). The measures, each in the piece's own pixels:
- lines and specks: r0b_count.count in the level's mask (eroded by 2 px there: the outline is never counted); a speck
  found at the same pixel in every config of a view, the line-off or patch-off control among them, is counted apart as
  common (not the stone's: the air's motes sparkle in sunlight round the camera, seeded, the same in every config);
- floating lines (SN4, SN9): the form's edges are where the id render's ids or normals change, or the mask does. A line
  pixel more than 2 px from an edge floats. Two readings: literal (SN9: a line with any pixel floating fails), and
  ends (SN4: a line must start and end at another edge; one whose either end floats fails). None is allowed;
- face spread (SN7, as ../patches.md defines it): L*'s 5th to 95th percentile on each face of L0 (a face: one
  connected region of one id and one normal), eroded by 2 px, in grey; with its mean, SN7's one value;
- the patches by distance (the fade, OS_Near): per face of L0, |L0 - L0-flat| on L* box-filtered 3 x 3, as drawn and with
  the near detail forced (-near: the mips alone), wherever those frames exist;
- the chamfer's width on screen (SN4: at least 2 px at 8 m): kind 1's runs across the top arris (columns) and the
  uprights (rows), through the middle half of the piece, the median run;
- the pop (SN8): at each candidate switch k (the first dolly frame at 8, 10 and 12 m), the level's difference
  |L1[k] - L0[k]| and the switch's change |L1[k] - L0[k-1]| beside the motion's own |L0[k] - L0[k-1]|, in the piece's
  box on screen (dolly.json, dilated by 3 px), on L* box-filtered 3 x 3 (the pipeline's dither changes every frame, up
  to 4 steps a pixel; the filter keeps what the eye sees and drops it); and the level difference along the whole dolly.

    python3.13 tools/r2a_count.py [piece ...]       counts into reviews/lt1/port/2b/r2a/stones/counts.json (merged)
    python3.13 tools/r2a_count.py --table [piece ...]      the counts as Markdown tables
    python3.13 tools/r2a_count.py --sheets piece [...]     grey.png, material.png, levels.png, arms.png beside counts.json

Needs numpy (Blender's own Python has it: /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13).
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "blender", "tools"))

from r0b_count import read_png, write_png, lstar, erode, dilate, pieces, groups, count, ERODE  # noqa: E402
from time_sheet import text  # noqa: E402

STONES = os.path.join(REPO, "reviews", "lt1", "port", "2b", "r2a", "stones")
FRAMES = os.path.join(STONES, "frames")
REFS = os.path.join(REPO, "docs", "references", "stone")
NEAR = 2                    # px: a line this near a form edge is drawn by the form (SN9)
FACE_MIN = 60               # px: a face smaller than this on screen (after erosion) has no spread worth reading
SWITCHES = (8.0, 10.0, 12.0)
MOMENTS = ["1300-drizzle", "1600-low-sun", "1750-blue-hour"]
KINDS = ["top", "chamfer", "split", "bed"]


def level_of(config):
    return config.split("-")[0]


def ls(path):
    return sorted(os.listdir(path)) if os.path.isdir(path) else []


# -- the id render ---------------------------------------------------------------------------------------------------

def load_ids(piece_dir, level, view):
    stem = os.path.join(piece_dir, "ids", level, view)
    ids = read_png(stem + "-ids.png").astype(np.int32)
    normals = read_png(stem + "-normals.png").astype(np.int32)
    mask = read_png(stem + "-mask.png")[..., 0] > 127
    return ids, normals, mask


def form_edges(ids, normals, mask):
    """Pixels on a form edge: an id or a normal (beyond 3 steps, the interpolation's rounding) changes to a
    4-neighbour, or the mask does (the outline)."""
    e = np.zeros(mask.shape, bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = (slice(0, mask.shape[0] - dy), slice(0, mask.shape[1] - dx))
        b = (slice(dy, None), slice(dx, None))
        diff = (ids[a] != ids[b]).any(-1) | (np.abs(normals[a] - normals[b]) > 3).any(-1) | (mask[a] != mask[b])
        diff &= mask[a] | mask[b]
        e[a] |= diff
        e[b] |= diff
    return e


def faces(ids, normals, mask):
    """L0's faces on screen: connected regions of one id and one normal (normals quantised to 8 steps), each eroded by
    2 px; a list of (kind, slice, boolean region)."""
    key = (ids[..., 0] << 16) | (ids[..., 1] << 8) | ids[..., 2]
    nkey = ((normals[..., 0] // 8) << 10) | ((normals[..., 1] // 8) << 5) | (normals[..., 2] // 8)
    full = key.astype(np.int64) * (1 << 15) + nkey
    out = []
    for k in np.unique(full[mask]):
        sel = (full == k) & mask
        ys, xs, lab = pieces(sel)
        for gy, gx in zip(*groups(ys, xs, lab)):
            region = np.zeros(mask.shape, bool)
            region[gy, gx] = True
            region = erode(region, ERODE)
            if region.sum() < FACE_MIN:
                continue
            g, b = int(ids[gy[0], gx[0], 1]), int(ids[gy[0], gx[0], 2])
            out.append(((b - 16) // 32, (g - 16) // 32, region))
    return out


# -- lines -----------------------------------------------------------------------------------------------------------

def floating(frame, mask, edges):
    """r0b's lines and specks in the mask, and which lines float: their pixels more than NEAR px from a form edge."""
    res, marks = count(frame, mask, overlay=True)
    near = dilate(edges, NEAR)
    line = (marks == 1) | (marks == 2)
    ys, xs, lab = pieces(line)
    lit_px = lit_n = ends_n = n = 0
    if len(ys):
        for gy, gx in zip(*groups(ys, xs, lab)):
            n += 1
            off = ~near[gy, gx]
            if off.any():
                lit_px += int(off.sum())
                lit_n += 1
            # its two ends: the extreme pixels along its main axis
            pts = np.stack([gx, gy], 1).astype(np.float64)
            c = pts - pts.mean(0)
            if len(pts) > 2:
                w, v = np.linalg.eigh(np.cov(c.T))
                axis = v[:, np.argmax(w)]
            else:
                axis = np.array([1.0, 0.0])
            t = c @ axis
            ends = [int(np.argmin(t)), int(np.argmax(t))]
            if any(off[i] for i in ends):
                ends_n += 1
    res.update(lines=n, floating_px=lit_px, floating_lines=lit_n, floating_end_lines=ends_n)
    return res, marks == 3


def common_specks(results, maps):
    """Which specks are not the stone's: a speck whose every pixel is a speck (within 1 px) in every config of the same
    light, look and view, the line-off or patch-off control among them, is drawn by neither level, the line nor the
    patches (the air's motes, which sparkle in the sun round the camera, seeded and the same in every config; or the
    town's). Each config's specks split into common and the stone's own."""
    if len(maps) < 2 or not any(("noline" in c or "flat" in c) for c in maps):
        for r in results.values():
            r.update(common_specks=None, stone_specks=r["specks"])
        return
    every = None
    for c, m in maps.items():
        if "nomotes" in c:          # (the control with the motes off is not one of them)
            continue
        d = dilate(m, 1)
        every = d if every is None else (every & d)
    for c, m in maps.items():
        ys, xs, lab = pieces(m)
        n = 0
        if len(ys):
            for gy, gx in zip(*groups(ys, xs, lab)):
                if len(gy) <= 4 and every[gy, gx].all():
                    n += 1
        r = results[c]
        r.update(common_specks=n, stone_specks=max(r["specks"] - n, 0))


# -- the chamfer -----------------------------------------------------------------------------------------------------

def chamfer_width(ids, mask):
    """Kind 1's runs: down the columns of the middle half of the piece (the top arris) and along its rows (the
    uprights); the median run length in px of each, or None."""
    kind = (ids[..., 2] - 16) // 32
    ch = (kind == 1) & mask
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None, None
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    qx, qy = (x1 - x0) // 4, (y1 - y0) // 4

    def runs(lines):
        out = []
        for line in lines:
            r = 0
            for v in line:
                if v:
                    r += 1
                elif r:
                    out.append(r)
                    r = 0
            if r:
                out.append(r)
        return float(np.median(out)) if out else None
    return runs(ch[y0:y1 + 1, x].tolist() for x in range(x0 + qx, x1 - qx + 1)), \
        runs(ch[y, x0:x1 + 1].tolist() for y in range(y0 + qy, y1 - qy + 1))


# -- the patches by distance (the fade) ------------------------------------------------------------------------------

def patch_signal(sdir, moment, look, view, faces_):
    """How much the patches draw at a view, per face of L0: |L0 - L0-flat| on L* box-filtered 3 x 3 (the dither
    dropped), mean and 95th percentile, as the game draws it (OS_Near fading relief and value to the patch's mean by
    footprint); and the same with the near detail forced everywhere (-near: OS_Near 1, the mips alone filtering the
    bands), when those frames exist."""
    def frame(config):
        f = os.path.join(sdir, moment, look, config, view + ".png")
        return box3(lstar(read_png(f))) if os.path.exists(f) else None
    a, b, an, bn = frame("L0"), frame("L0-flat"), frame("L0-near"), frame("L0-flat-near")
    if a is None or b is None:
        return None
    out = []
    for k, sl, r in faces_:
        d = np.abs(a - b)[r]
        row = {"kind": KINDS[k] if k < len(KINDS) else k, "slice": sl, "px": int(r.sum()),
               "fade": [round(float(d.mean()), 2), round(float(np.percentile(d, 95)), 2)]}
        if an is not None and bn is not None:
            dn = np.abs(an - bn)[r]
            row["mips"] = [round(float(dn.mean()), 2), round(float(np.percentile(dn, 95)), 2)]
        out.append(row)
    return out


# -- the pop ---------------------------------------------------------------------------------------------------------

def box3(a):
    p = np.pad(a, 1, mode="edge")
    return sum(p[1 + dy:1 + dy + a.shape[0], 1 + dx:1 + dx + a.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0


def pop(dolly_dir, look):
    d = json.load(open(os.path.join(dolly_dir, "dolly.json")))
    dist, win = d["distances"], d["windows"]
    cw, ch = d["crop"][2], d["crop"][3]

    def L(level, i):
        return box3(lstar(read_png(os.path.join(dolly_dir, look, level, f"{i:03d}.png"))))

    def region(i):
        x0, y0, x1, y1 = win[i]
        m = np.zeros((ch, cw), bool)
        m[max(0, int(y0) - 3):min(ch, int(np.ceil(y1)) + 4), max(0, int(x0) - 3):min(cw, int(np.ceil(x1)) + 4)] = True
        return m

    def stats(a, m):
        v = a[m]
        return {"mean": round(float(v.mean()), 3), "p99": round(float(np.percentile(v, 99)), 2), "max": round(float(v.max()), 2)}
    out = {"step_mm": round(1000 * d["step"], 1), "frames": d["frames"]}
    for s in SWITCHES:
        k = next((i for i, x in enumerate(dist) if x >= s - 1e-6), None)
        if k is None or k == 0:
            continue
        m = region(k)
        a0p, a0, a1 = L("L0", k - 1), L("L0", k), L("L1", k)
        out[f"{s:g}"] = {"frame": k, "at_m": dist[k], "level": stats(np.abs(a1 - a0), m),
                         "switch": stats(np.abs(a1 - a0p), m), "motion": stats(np.abs(a0 - a0p), m)}
    curve = []
    for i in range(0, len(dist), max(1, int(round(0.5 / d["step"])))):
        curve.append([round(dist[i], 2), stats(np.abs(L("L1", i) - L("L0", i)), region(i))["mean"]])
    out["level_along"] = curve
    return out


# -- the counts ------------------------------------------------------------------------------------------------------

def count_piece(piece):
    out = {}
    pdir = os.path.join(FRAMES, piece)
    for stand in ls(pdir):
        sdir = os.path.join(pdir, stand)
        ids_cache = {}

        def ids_for(level, view):
            if (level, view) not in ids_cache:
                ids, normals, mask = load_ids(sdir, level, view)
                ids_cache[(level, view)] = (ids, normals, mask, form_edges(ids, normals, mask))
            return ids_cache[(level, view)]
        tj = os.path.join(sdir, "ids", "triangles.json")
        if os.path.exists(tj):
            out[f"triangles/{piece}/{stand}"] = json.load(open(tj))
        for level in ("L0", "L1"):
            for f in ls(os.path.join(sdir, "ids", level)):
                if f.endswith("-ids.png"):
                    view = f[:-len("-ids.png")]
                    ids, _, mask, _ = ids_for(level, view)
                    top, upright = chamfer_width(ids, mask)
                    out[f"chamfer/{piece}/{stand}/{level}/{view}"] = {"top_px": top, "upright_px": upright}
        for moment in ls(sdir):
            if moment in ("ids", "dolly"):
                continue
            for look in ls(os.path.join(sdir, moment)):
                by_view = {}
                for config in ls(os.path.join(sdir, moment, look)):
                    level = level_of(config)
                    for f in ls(os.path.join(sdir, moment, look, config)):
                        view = f[:-4]
                        ids, normals, mask, edges = ids_for(level, view)
                        frame = read_png(os.path.join(sdir, moment, look, config, f))
                        key = f"{piece}/{stand}/{moment}/{look}/{config}/{view}"
                        out[key], specks = floating(frame, mask, edges)
                        by_view.setdefault(view, ({}, {}))
                        by_view[view][0][config] = out[key]
                        by_view[view][1][config] = specks
                        if look == "grey" and level == "L0":
                            L = lstar(frame)
                            out["spread/" + key] = [
                                {"kind": KINDS[k] if k < len(KINDS) else k, "slice": s, "px": int(r.sum()),
                                 "mean": round(float(L[r].mean()), 2),
                                 "spread": round(float(np.percentile(L[r], 95) - np.percentile(L[r], 5)), 2)}
                                for k, s, r in faces(ids, normals, mask)]
                        print(key, out[key]["line_px"], out[key]["specks"], out[key]["floating_lines"], flush=True)
                for view, (results, maps) in by_view.items():
                    common_specks(results, maps)
                    ids, normals, mask, _ = ids_for("L0", view)
                    sig = patch_signal(sdir, moment, look, view, faces(ids, normals, mask))
                    if sig is not None:
                        out[f"patch/{piece}/{stand}/{moment}/{look}/{view}"] = sig
        for moment in ls(os.path.join(sdir, "dolly")):
            ddir = os.path.join(sdir, "dolly", moment)
            for look in ls(ddir):
                if os.path.isdir(os.path.join(ddir, look)):
                    out[f"pop/{piece}/{stand}/{moment}/{look}"] = pop(ddir, look)
                    print("pop", piece, stand, moment, look, flush=True)
    return out


def run(pieces_):
    cj = os.path.join(STONES, "counts.json")
    out = json.load(open(cj)) if os.path.exists(cj) else {}
    for p in pieces_:
        for k in [k for k in out if k.split("/")[0] == p
                  or (k.split("/")[0] in ("spread", "chamfer", "triangles", "pop", "patch") and k.split("/")[1] == p)]:
            del out[k]
        out.update(count_piece(p))
    with open(cj, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


# -- tables ----------------------------------------------------------------------------------------------------------

def table(pieces_):
    c = json.load(open(os.path.join(STONES, "counts.json")))
    rows = ["| piece / stand / light / look / config | view | lines px (bright/dark) | specks (the stone's / common) | lines | floating (literal / ends) |",
            "| --- | --- | --- | --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] in pieces_ and len(parts) == 6:
            r = c[k]
            rows.append(f"| {'/'.join(parts[:5])} | {parts[5]} | {r['line_px']} ({r['bright_line_px']}/{r['dark_line_px']}) | "
                        f"{r['specks']} ({r.get('stone_specks', '-')} / {r.get('common_specks', '-')}) | {r['lines']} | "
                        f"{r['floating_lines']} / {r['floating_end_lines']} |")
    rows += ["", "| face spread (grey, L0) | view | faces: kind slice px mean spread |", "| --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "spread" and parts[1] in pieces_:
            cells = "; ".join(f"{f['kind']} {f['slice']} {f['px']} {f['mean']:.1f} {f['spread']:.2f}" for f in c[k])
            rows.append(f"| {'/'.join(parts[1:6])} | {parts[6]} | {cells} |")
    rows += ["", "| chamfer | top px | upright px |", "| --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "chamfer" and parts[1] in pieces_:
            rows.append(f"| {'/'.join(parts[1:])} | {c[k]['top_px']} | {c[k]['upright_px']} |")
    rows += ["", "| triangles | level/view | front | thin (< 2 px) | median area px | median smallest altitude px |",
             "| --- | --- | --- | --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "triangles" and parts[1] in pieces_:
            for lv, t in sorted(c[k].items()):
                rows.append(f"| {'/'.join(parts[1:])} | {lv} | {t['front']} | {t['thin']} ({100 * t['thin'] / max(1, t['front']):.0f}%) | "
                            f"{t['median_area_px']:.1f} | {t['median_altitude_px']:.2f} |")
    rows += ["", "| pop (L* box 3x3) | switch | level mean / p99 | switch mean / p99 | motion mean / p99 |",
             "| --- | --- | --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "pop" and parts[1] in pieces_:
            for s in SWITCHES:
                r = c[k].get(f"{s:g}")
                if r:
                    rows.append(f"| {'/'.join(parts[1:])} | {s:g} m (frame {r['frame']}) | {r['level']['mean']:.2f} / "
                                f"{r['level']['p99']:.1f} | {r['switch']['mean']:.2f} / {r['switch']['p99']:.1f} | "
                                f"{r['motion']['mean']:.2f} / {r['motion']['p99']:.1f} |")
    rows += ["", "| patches by distance (L* box 3x3) | view | faces: kind slice px, as drawn mean / p95, mips alone mean / p95 |",
             "| --- | --- | --- |"]
    for k in sorted(c, key=lambda k: (k.split("/")[:-1], view_order(k.split("/")[-1]))):
        parts = k.split("/")
        if parts[0] == "patch" and parts[1] in pieces_:
            cells = "; ".join(f"{f['kind']} {f['slice']} {f['px']}: {f['fade'][0]:.2f} / {f['fade'][1]:.1f}"
                              + (f", {f['mips'][0]:.2f} / {f['mips'][1]:.1f}" if "mips" in f else "") for f in c[k])
            rows.append(f"| {'/'.join(parts[1:5])} | {parts[5]} | {cells} |")
    print("\n".join(rows))


def view_order(v):
    """Views by distance, the face-on ones first (1, 5, 12) and then the eye-height ones."""
    try:
        return (0, float(v.rstrip("m")))
    except ValueError:
        return (1, float(v[3:]) if v[3:].replace(".", "").isdigit() else 0.0)


# -- sheets ----------------------------------------------------------------------------------------------------------

WHITE = (1.0, 1.0, 1.0)


def as_float(rgb8):
    return rgb8.astype(np.float32) / 255.0


def zoom(a, z):
    return a.repeat(z, 0).repeat(z, 1) if z > 1 else a


def tile(frame, mask, z, pad=12, cap=(900, 560)):
    """The piece's box on screen, padded, at native size times z (nearest: each pixel as the player's), capped."""
    ys, xs = np.nonzero(mask)
    cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
    h = min(ys.max() - ys.min() + 2 * pad, cap[1] // z)
    w = min(xs.max() - xs.min() + 2 * pad, cap[0] // z)
    y0, x0 = max(0, cy - h // 2), max(0, cx - w // 2)
    return zoom(as_float(frame[y0:y0 + h, x0:x0 + w]), z)


def labelled(img, s):
    img = img.copy()
    text(img, s, 0, 0, scale=2, pad=3)
    return img


def grid(rows, gap=6, bg=0.12):
    """Rows of tiles into one image: each row as tall as its tallest tile, tiles left to right."""
    width = max(sum(t.shape[1] for t in r) + gap * (len(r) + 1) for r in rows)
    out = []
    for r in rows:
        h = max(t.shape[0] for t in r)
        line = np.full((h + gap, width, 3), bg, np.float32)
        x = gap
        for t in r:
            line[gap:gap + t.shape[0], x:x + t.shape[1]] = t
            x += t.shape[1] + gap
        out.append(line)
    out.append(np.full((gap, width, 3), bg, np.float32))
    return np.concatenate(out, 0)


def stand_moments(sdir):
    return [m for m in MOMENTS if os.path.isdir(os.path.join(sdir, m))]


VIEW_ZOOM = {"1m": 1, "5m": 3, "8m": 4, "10m": 5, "12m": 6, "eye5": 3, "eye12": 6}


def sheet_looks(piece, look):
    """grey.png / material.png: per stand and light a row, the views at native size (far views enlarged, nearest)."""
    rows = []
    pdir = os.path.join(FRAMES, piece)
    for stand in ("sun", "foot"):
        sdir = os.path.join(pdir, stand)
        for moment in stand_moments(sdir):
            row = []
            for view in ("1m", "5m", "12m", "eye5", "eye12"):
                f = os.path.join(sdir, moment, look, "L0", view + ".png")
                if not os.path.exists(f):
                    continue
                _, _, mask = load_ids(sdir, "L0", view)
                z = VIEW_ZOOM.get(view, 1)
                row.append(labelled(tile(read_png(f), mask, z), f"{piece} {stand} {moment} {view} L0" + (f" x{z}" if z > 1 else "")))
            if row:
                rows.append(row)
    return grid(rows) if rows else None


def sheet_levels(piece):
    """levels.png: per stand and light, L0, L1 and their difference (x8 about mid grey) at 8, 10 and 12 m, material."""
    rows = []
    pdir = os.path.join(FRAMES, piece)
    c = json.load(open(os.path.join(STONES, "counts.json")))
    for stand in ("sun", "foot"):
        sdir = os.path.join(pdir, stand)
        for moment in stand_moments(sdir):
            row = []
            for view in ("8m", "10m", "12m"):
                f0 = os.path.join(sdir, moment, "material", "L0", view + ".png")
                f1 = os.path.join(sdir, moment, "material", "L1", view + ".png")
                if not (os.path.exists(f0) and os.path.exists(f1)):
                    continue
                _, _, m0 = load_ids(sdir, "L0", view)
                _, _, m1 = load_ids(sdir, "L1", view)
                a, b = read_png(f0), read_png(f1)
                d = np.clip(128 + 8 * (lstar(b) - lstar(a)), 0, 255).astype(np.uint8)
                z = VIEW_ZOOM[view]
                m = m0 | m1
                row += [labelled(tile(a, m, z), f"{moment} {stand} {view} L0"), labelled(tile(b, m, z), "L1"),
                        labelled(tile(np.stack([d] * 3, -1), m, z), "L1-L0 X8")]
            p = c.get(f"pop/{piece}/{stand}/{moment}/material")
            if row:
                if p:
                    note = np.full((60, 520, 3), 0.12, np.float32)
                    y = 0
                    for s in SWITCHES:
                        r = p.get(f"{s:g}")
                        if r:
                            text(note, f"{s:g}M SWITCH {r['switch']['p99']:.1f} MOTION {r['motion']['p99']:.1f} P99", 0, y, scale=2, pad=2)
                            y += 20
                    row.append(note)
                rows.append(row)
    return grid(rows) if rows else None


def reference(name, height):
    src = [f for f in ls(REFS) if f.startswith(name)][0]
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "r.png")
        subprocess.run(["sips", "-s", "format", "png", "--resampleHeight", str(height), os.path.join(REFS, src), "--out", out],
                       check=True, capture_output=True)
        return labelled(as_float(read_png(out)), f"reference {name}")


def sheet_arms(piece):
    """arms.png: the arms (as built, facets x2, minor off) at L0, 1 m and 5 m: the lit stand first, the shade stand
    beside it, grey then material; references 05 and 10 at the end."""
    rows = []
    pdir = os.path.join(FRAMES, piece)
    for look in ("grey", "material"):
        for arm in ("L0", "L0-facets2", "L0-nominor"):
            row = []
            for stand, moment in (("sun", "1600-low-sun"), ("foot", "1600-low-sun")):
                sdir = os.path.join(pdir, stand)
                for view, z in (("1m", 1), ("5m", 4)):
                    f = os.path.join(sdir, moment, look, arm, view + ".png")
                    if os.path.exists(f):
                        _, _, mask = load_ids(sdir, "L0", view)
                        name = {"L0": "as built", "L0-facets2": "facets x2", "L0-nominor": "minor off"}[arm]
                        row.append(labelled(tile(read_png(f), mask, z, cap=(640, 400)), f"{name} {look} {stand} {view}" + (f" x{z}" if z > 1 else "")))
            if row:
                rows.append(row)
    if not rows:
        return None
    h = sum(max(t.shape[0] for t in r) + 6 for r in rows)
    refs = [reference("05", h // 2 - 6), reference("10", h // 2 - 6)]
    body = grid(rows)
    side = grid([[refs[0]], [refs[1]]])
    H = max(body.shape[0], side.shape[0])
    pad = lambda a: np.concatenate([a, np.full((H - a.shape[0], a.shape[1], 3), 0.12, np.float32)], 0)
    return np.concatenate([pad(body), pad(side)], 1)


def sheets(pieces_):
    for piece in pieces_:
        made = {"grey": sheet_looks(piece, "grey"), "material": sheet_looks(piece, "material"),
                "levels": sheet_levels(piece), "arms": sheet_arms(piece)}
        for name, img in made.items():
            if img is not None:
                d = os.path.join(STONES, "sheets", piece)
                os.makedirs(d, exist_ok=True)
                write_png(os.path.join(d, name + ".png"), np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
                print("sheet", piece, name, img.shape[1], "x", img.shape[0])


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--table":
        table(args[1:] or ls(FRAMES))
    elif args and args[0] == "--sheets":
        sheets(args[1:])
    else:
        run(args or ls(FRAMES))
