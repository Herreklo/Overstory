"""R2a's counter (reviews/lt1/port/2b/r2a/stones/plan.md, The measures; the design's SN4, SN7, SN8 and SN9:
reviews/lt1/port/2b/design.md), on the frames Editor/LT1R2a.cs writes. It uses r0b_count's reading, L* and marks, and
copies none of them:

    frames/<piece>/<stand>/<moment>/<look>/<config>/<view>.png     the player's frames (2560 x 1440)
    frames/<piece>/<stand>/ids/<level>/<view>-{ids,normals,mask}.png   what the mesh is at each pixel (R2aIds.shader)
    frames/<piece>/<stand>/ids/triangles.json                      SN8's triangle measures, from the mesh
    frames/<piece>/<stand>/ids/mesh.json                           each level's mesh as Unity imported it (triangles, vertices)
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
- the arms against as built (SN7's A/B): per face of L0, |arm - L0| on L* box-filtered 3 x 3, for facets x2 and minor
  ledges off, wherever those frames exist; their lines, specks and spread are counted as any config's;
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


def arm_signal(sdir, moment, look, view, faces_):
    """What each arm changes against the patches as built, per face of L0 (SN7's A/B: facets x2, minor ledges off):
    |arm - L0| on L* box-filtered 3 x 3, mean and 95th percentile, as the game draws it (the fade on). A bed face
    never moves with the arm, so its value is the frame's noise floor (the pipeline's dither and the motes)."""
    def frame(config):
        f = os.path.join(sdir, moment, look, config, view + ".png")
        return box3(lstar(read_png(f))) if os.path.exists(f) else None
    base = frame("L0")
    if base is None:
        return None
    out = {}
    for arm in ("L0-facets2", "L0-nominor"):
        a = frame(arm)
        if a is None:
            continue
        rows = []
        for k, sl, r in faces_:
            d = np.abs(a - base)[r]
            rows.append({"kind": KINDS[k] if k < len(KINDS) else k, "slice": sl, "px": int(r.sum()),
                         "change": [round(float(d.mean()), 2), round(float(np.percentile(d, 95)), 2)]})
        out[arm] = rows
    return out or None


# -- the joints (SN5) -----------------------------------------------------------------------------------------------

RIM = 6.0       # L*: a chamfer this far above both the face and the joint beside it reads as a light rim (SN5's
                # joint tolerance, taken for the rim as a starting value: SN5 gives the rim no number of its own)
JOINT_TOL = 6.0     # L*: a joint's fill within this of the faces beside it (SN5, from The Witness's slides)
JOINT_MM = 12.0     # the widest wall joint (SN5)
GENERATED = os.path.join(REPO, "unity", "Assets", "Experiments", "LT1", "R2a", "Generated")


def part_of(piece):
    """The part a frames folder judges: step, wallstone or coping (step-alone: the step without its context)."""
    return piece.split("-")[0]


def length_mm(piece):
    b = json.load(open(os.path.join(GENERATED, part_of(piece) + ".json")))["bounds"]["L0"]
    return b["maxMm"][0] - b["minMm"][0]


def classes(s_ids, s_mask, c_ids, c_mask):
    """Each pixel's class: the stone's face kinds 0 to 3 (top, chamfer, split, bed) as 0 to 3, the joint's fill 6, a
    neighbour's (or proxy's) kinds as 10 + kind, -1 neither (the town, the sky)."""
    ks = (s_ids[..., 2].astype(np.int32) - 16) // 32
    kc = (c_ids[..., 2].astype(np.int32) - 16) // 32
    cls = np.full(s_mask.shape, -1, np.int32)
    c = c_mask & ~s_mask
    cls[c] = np.where(kc[c] == 6, 6, 10 + kc[c])
    cls[s_mask] = ks[s_mask]
    return cls


def runs_of(seq):
    """A line of classes as runs: [(class, start, length)]."""
    out = []
    for i, v in enumerate(seq):
        if out and out[-1][0] == v:
            out[-1][2] += 1
        else:
            out.append([v, i, 1])
    return out


def trimmed(run, take=None):
    """A run's samples without its first and last pixel (the frame's MSAA blends them with the next class), when it is
    3 px or more; its middle pixel otherwise. take: only the first n samples after the trim (the face beside)."""
    _, a, n = run
    idx = list(range(a + 1, a + n - 1)) if n >= 3 else [a + n // 2]
    return idx[:take] if take else idx


LENS_V = 46.4      # degrees: the 28 mm lens's vertical field (LT1R2a.cs, Lens28)
EYE_DROP = 1.5     # m: about the eye's height over a stone's front at the eye views (their distance is along the ground)


def px_per_mm(view):
    """About how many pixels a millimetre at the stone's front spans in a view of 1440 rows (its distance from the
    name: "5m" face-on from 5 m, "eye5" 5 m along the ground at eye height)."""
    d = float(view[3:]) if view.startswith("eye") else float(view.rstrip("m"))
    if view.startswith("eye"):
        d = (d * d + EYE_DROP * EYE_DROP) ** 0.5
    return 1440 / (2 * np.tan(np.radians(LENS_V / 2)) * d * 1000)


def ctx_ids(sdir, level, view, shape):
    """The context's ids in a view (what LT1R2a.cs drew beside the stone, the stone black), or none."""
    stem = os.path.join(sdir, "ids", level, view + "-ctx")
    if os.path.exists(stem + "-ids.png"):
        return read_png(stem + "-ids.png").astype(np.int32), read_png(stem + "-mask.png")[..., 0] > 127
    return np.zeros(shape + (3,), np.int32), np.zeros(shape, bool)


JOINT_VIEWS = ("1m", "5m", "eye5")


def joint_signal(L, cls, ppm):
    """SN5 on one frame: per side of the stone (top, bottom, left, right), profiles across its edge through the middle
    60% of that side (columns for top and bottom, rows for the ends). Walking out from the stone's outline: the
    joint's fill, then the neighbour's chamfer and face (the course below's top first, where it shows); walking in: the
    stone's chamfer, then its face (its top or bed first, where it shows above the chamfer). Each part's L* pooled over the profiles (each run trimmed of its blended ends), the
    face beside a chamfer or joint its first 8 mm (at least 2 px). The rim on a side: the stone's chamfer less the
    brighter of the face and the joint beside it; RIM or more reads as a light rim. The joint against the faces either
    side: SN5's within JOINT_TOL."""
    S = (cls >= 0) & (cls < 6)
    ys, xs = np.nonzero(S)
    if len(ys) < 50:
        return None
    rb = max(2, int(round(8 * ppm)))
    reach = max(6, int(np.ceil((JOINT_MM + 20) * ppm)) + 4)     # how far a profile walks: a joint, a chamfer, a face
    out = {"ppm": round(ppm, 4), "beside_px": rb}
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    for side in ("top", "bottom", "left", "right"):
        lines = []
        if side in ("top", "bottom"):
            lo, hi = x0 + (x1 - x0) // 5, x1 - (x1 - x0) // 5
            for x in range(lo, hi + 1):
                col = np.nonzero(S[:, x])[0]
                if not len(col):
                    continue
                e = col.min() if side == "top" else col.max()
                d = -1 if side == "top" else 1
                lines.append((e, d, cls[:, x], L[:, x]))
        else:
            lo, hi = y0 + (y1 - y0) // 5, y1 - (y1 - y0) // 5
            for y in range(lo, hi + 1):
                row = np.nonzero(S[y, :])[0]
                if not len(row):
                    continue
                e = row.min() if side == "left" else row.max()
                d = -1 if side == "left" else 1
                lines.append((e, d, cls[y, :], L[y, :]))
        acc = {k: [] for k in ("chamfer", "face", "top", "joint", "n_top", "n_chamfer", "n_face")}
        widths = {"chamfer": [], "joint": []}
        gaps = n_prof = 0
        for e, d, c, l in lines:
            n_prof += 1
            # outward from the outline: the joint, the neighbour
            o = np.arange(e + d, e + d * (reach + 1), d)
            o = o[(o >= 0) & (o < len(c))]
            r = runs_of(c[o].tolist())
            k = 0
            if r and r[0][0] == -1 and any(q[0] >= 6 for q in r[1:]):
                gaps += 1                       # the town or the sky seen between the stone and its joint: a slot
                k = 1
            if k < len(r) and r[k][0] == 6:
                widths["joint"].append(r[k][2])
                acc["joint"] += [l[o[i]] for i in trimmed(r[k])]
                k += 1
                if k < len(r) and r[k][0] in (10, 13) and k + 1 < len(r) and r[k + 1][0] in (11, 12):
                    acc["n_top"] += [l[o[i]] for i in trimmed(r[k])]      # (the course below's top, seen from above)
                    k += 1
                if k < len(r) and r[k][0] == 11:
                    acc["n_chamfer"] += [l[o[i]] for i in trimmed(r[k])]
                    k += 1
                if k < len(r) and r[k][0] in (10, 12):
                    acc["n_face"] += [l[o[i]] for i in trimmed(r[k], rb)]
            # inward: the stone's chamfer and face (the coping's top or a tread's top before them, where it shows)
            i_ = np.arange(e, e - d * reach, -d)
            i_ = i_[(i_ >= 0) & (i_ < len(c))]
            r = runs_of(c[i_].tolist())
            k = 0
            if k < len(r) and r[k][0] in (0, 3) and k + 1 < len(r) and r[k + 1][0] == 1:
                acc["top"] += [l[i_[i]] for i in trimmed(r[k])]
                k += 1
            if k < len(r) and r[k][0] == 1:
                widths["chamfer"].append(r[k][2])
                acc["chamfer"] += [l[i_[i]] for i in trimmed(r[k])]
                k += 1
            if k < len(r) and r[k][0] == 2:
                acc["face"] += [l[i_[i]] for i in trimmed(r[k], rb)]

        def med(v):
            return round(float(np.median(v)), 2) if len(v) >= 8 else None
        rec = {"profiles": n_prof, "slots": gaps}
        for k, v in acc.items():
            rec[k] = med(v)
            rec[k + "_n"] = len(v)
        rec["joint_p5"] = round(float(np.percentile(acc["joint"], 5)), 2) if len(acc["joint"]) >= 8 else None
        for k, v in widths.items():
            rec[k + "_px"] = float(np.median(v)) if v else None
            rec[k + "_mm"] = round(float(np.median(v)) / ppm, 1) if v else None
        if rec["chamfer"] is not None:
            beside = [x for x in (rec["face"], rec["joint"], rec["top"]) if x is not None]
            rec["rim"] = round(rec["chamfer"] - max(beside), 2) if beside else None
        else:
            rec["rim"] = None
        if rec["joint"] is not None:
            rec["joint_vs_face"] = round(rec["joint"] - rec["face"], 2) if rec["face"] is not None else None
            rec["joint_vs_neighbour"] = round(rec["joint"] - rec["n_face"], 2) if rec["n_face"] is not None else None
        out[side] = rec
    jointed = [s for s in ("top", "bottom", "left", "right") if out[s]["joint"] is not None]
    rimmed = [s for s in ("top", "bottom", "left", "right") if (out[s]["rim"] or -99) >= RIM]
    out["jointed"], out["rimmed"] = jointed, rimmed
    out["rings"] = bool(jointed) and all(s in rimmed for s in jointed) and len(jointed) >= 2
    out["joint_off"] = [s for s in jointed if any(abs(out[s].get(k) or 0) > JOINT_TOL for k in ("joint_vs_face", "joint_vs_neighbour"))]
    return out


def chamfer_facets(L, cls, normals, ppm):
    """Every chamfer facet of the stone on screen (one connected region of kind 1 and one normal, 12 px or more)
    against what lies beside it, wherever it is (a coping's front arris borders its top, not a joint): its L* (trimmed
    of its blended edge where that leaves 30% of it) and, in a band from 2 px to 8 mm (at least 3 px) beyond it, the
    stone's top or bed, its split faces, the joint's fill and the context's pieces, each a median where it is 15% or
    more of the band (not a corner's alone). Its rim: its L* less
    the brightest of them; RIM or more reads as a light line along that arris. Named by its normal (top, bottom) or,
    upright, by its side on screen."""
    cham = cls == 1
    if not cham.any():
        return []
    nkey = ((normals[..., 0] // 8) << 10) | ((normals[..., 1] // 8) << 5) | (normals[..., 2] // 8)
    rb = max(3, int(round(8 * ppm)))
    S = (cls >= 0) & (cls < 6)
    cx = np.nonzero(S)[1].mean()
    out = []
    for k in np.unique(nkey[cham]):
        ys, xs, lab = pieces(cham & (nkey == k))
        for gy, gx in zip(*groups(ys, xs, lab)):
            if len(gy) < 12:
                continue
            g = np.zeros(cls.shape, bool)
            g[gy, gx] = True
            core = erode(g, 1)
            if core.sum() < 0.3 * len(gy):
                core = g
            ring = dilate(g, rb) & ~dilate(g, 1)
            n = normals[gy[0], gx[0]].astype(np.float64) / 255 * 2 - 1
            name = "top" if n[1] > 0.5 else "bottom" if n[1] < -0.5 else ("left" if gx.mean() < cx else "right")
            rec = {"side": name, "px": int(len(gy)), "normal": [round(float(v), 3) for v in n],
                   "box": [int(gx.min()), int(gy.min()), int(gx.max()), int(gy.max())],
                   "L": round(float(np.median(L[core])), 2)}
            seen = int((ring & (cls >= 0)).sum())
            for part, m in (("top", (cls == 0) | (cls == 3)), ("face", cls == 2), ("joint", cls == 6), ("context", cls >= 10)):
                m = ring & m
                # (a part only at the facet's ends, a corner's, under 15% of what lies beside it, is not beside it)
                rec[part] = round(float(np.median(L[m])), 2) if m.sum() >= max(8, 0.15 * seen) else None
            beside = [rec[p_] for p_ in ("top", "face", "joint", "context") if rec[p_] is not None]
            rec["rim"] = round(rec["L"] - max(beside), 2) if beside else None
            out.append(rec)
    return sorted(out, key=lambda r: -r["px"])


def joint_lines(frame, cls, ppm):
    """r0b's lines in the ring round the stone's outline (its joint and the faces either side, out to the widest joint
    and 8 mm in): the bright lines lying along the joints (a light rim drawn as a line) and the dark ones (a dark
    outline, SN5's other fault)."""
    S = (cls >= 0) & (cls < 6)
    C = cls >= 6
    rj = max(3, int(np.ceil(JOINT_MM * ppm)) + 2)
    rin = max(3, int(np.ceil(20 * ppm)))
    ring = (S | C) & dilate(S, rj) & ~erode(S, rin)
    res, marks = count(frame, ring, overlay=True)
    return {k: res[k] for k in ("mask_px", "bright_line_px", "bright_lines", "dark_line_px", "dark_lines")}, marks


# -- the pop ---------------------------------------------------------------------------------------------------------

def box3(a):
    p = np.pad(a, 1, mode="edge")
    return sum(p[1 + dy:1 + dy + a.shape[0], 1 + dx:1 + dx + a.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0


def pop(sdir, dolly_dir, look):
    d = json.load(open(os.path.join(dolly_dir, "dolly.json")))
    dist, win = d["distances"], d["windows"]
    cw, ch = d["crop"][2], d["crop"][3]
    mdir = os.path.join(sdir, "ids", "dolly")
    # the stone's own masks (ids/dolly/<level>/NNN.png: its context drawn and never counted), else its box on screen
    masks = all(len([f for f in ls(os.path.join(mdir, lv)) if f.endswith(".png")]) == len(dist) for lv in ("L0", "L1"))

    def L(level, i):
        return box3(lstar(read_png(os.path.join(dolly_dir, look, level, f"{i:03d}.png"))))

    def mask(level, i):
        return read_png(os.path.join(mdir, level, f"{i:03d}.png"))[..., 0] > 127

    def region(i, levels):
        if masks:
            return dilate(np.logical_or.reduce([mask(lv, j) for lv, j in levels]), 3)
        x0, y0, x1, y1 = win[i]
        m = np.zeros((ch, cw), bool)
        m[max(0, int(y0) - 3):min(ch, int(np.ceil(y1)) + 4), max(0, int(x0) - 3):min(cw, int(np.ceil(x1)) + 4)] = True
        return m

    def stats(a, m):
        v = a[m]
        return {"mean": round(float(v.mean()), 3), "p99": round(float(np.percentile(v, 99)), 2), "max": round(float(v.max()), 2)}
    out = {"step_mm": round(1000 * d["step"], 1), "frames": d["frames"], "region": "mask" if masks else "box"}
    for s in SWITCHES:
        k = next((i for i, x in enumerate(dist) if x >= s - 1e-6), None)
        if k is None or k == 0:
            continue
        m = region(k, (("L0", k - 1), ("L0", k), ("L1", k)))
        a0p, a0, a1 = L("L0", k - 1), L("L0", k), L("L1", k)
        out[f"{s:g}"] = {"frame": k, "at_m": dist[k], "level": stats(np.abs(a1 - a0), m),
                         "switch": stats(np.abs(a1 - a0p), m), "motion": stats(np.abs(a0 - a0p), m)}
    curve = []
    for i in range(0, len(dist), max(1, int(round(0.5 / d["step"])))):
        curve.append([round(dist[i], 2), stats(np.abs(L("L1", i) - L("L0", i)), region(i, (("L0", i), ("L1", i))))["mean"]])
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
        oj = os.path.join(sdir, "ids", "open.json")
        if os.path.exists(oj):
            out[f"open/{piece}/{stand}"] = json.load(open(oj))
        mj = os.path.join(sdir, "ids", "mesh.json")
        if os.path.exists(mj):
            out[f"mesh/{piece}/{stand}"] = json.load(open(mj))
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
                        if config in ("L0", "L1") and view in JOINT_VIEWS:
                            ci, cm = ctx_ids(sdir, level, view, mask.shape)
                            cls = classes(ids, mask, ci, cm)
                            Lf = lstar(frame)
                            j = joint_signal(Lf, cls, px_per_mm(view))
                            if j is not None:
                                j["context"] = bool(cm.any())
                                j["chamfers"] = chamfer_facets(Lf, cls, normals, px_per_mm(view))
                                j["lines"] = joint_lines(frame, cls, px_per_mm(view))[0]
                                out["joint/" + key] = j
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
                    arms = arm_signal(sdir, moment, look, view, faces(ids, normals, mask))
                    if arms is not None:
                        out[f"arm/{piece}/{stand}/{moment}/{look}/{view}"] = arms
        for moment in ls(os.path.join(sdir, "dolly")):
            ddir = os.path.join(sdir, "dolly", moment)
            for look in ls(ddir):
                if os.path.isdir(os.path.join(ddir, look)):
                    out[f"pop/{piece}/{stand}/{moment}/{look}"] = pop(sdir, ddir, look)
                    print("pop", piece, stand, moment, look, flush=True)
    return out


def run(pieces_):
    cj = os.path.join(STONES, "counts.json")
    out = json.load(open(cj)) if os.path.exists(cj) else {}
    for p in pieces_:
        for k in [k for k in out if k.split("/")[0] == p
                  or (k.split("/")[0] in ("spread", "chamfer", "triangles", "mesh", "pop", "patch", "arm", "joint", "open") and k.split("/")[1] == p)]:
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
    rows += ["", "| mesh as imported | L0 triangles | L0 vertices | L1 triangles | L1 vertices |", "| --- | --- | --- | --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "mesh" and parts[1] in pieces_:
            rows.append(f"| {'/'.join(parts[1:])} | {c[k]['L0']['triangles']} | {c[k]['L0']['vertices']} | "
                        f"{c[k]['L1']['triangles']} | {c[k]['L1']['vertices']} |")
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
    rows += ["", "| the arms against as built (L* box 3x3) | view | arm | faces: kind slice px, change mean / p95 |",
             "| --- | --- | --- | --- |"]
    for k in sorted(c, key=lambda k: (k.split("/")[:-1], view_order(k.split("/")[-1]))):
        parts = k.split("/")
        if parts[0] == "arm" and parts[1] in pieces_:
            for arm, faces_ in sorted(c[k].items()):
                cells = "; ".join(f"{f['kind']} {f['slice']} {f['px']}: {f['change'][0]:.2f} / {f['change'][1]:.1f}" for f in faces_)
                rows.append(f"| {'/'.join(parts[1:5])} | {parts[5]} | {arm} | {cells} |")
    rows += ["", "| open faces seen (px of the undrawn bed, back and ends; -1 none to see) | level/view: px |", "| --- | --- |"]
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "open" and parts[1] in pieces_:
            rows.append(f"| {'/'.join(parts[1:])} | " + "; ".join(f"{lv} {n}" for lv, n in sorted(c[k].items())) + " |")
    rows += ["", f"| joints (SN5, L* median; rim = chamfer - brighter beside, a rim at {RIM:g}; joint within {JOINT_TOL:g} of the faces) "
             "| view | side | chamfer px (mm) / L* | face | top | joint px (mm) / L* / p5 | neighbour chamfer / face | rim | "
             "joint - face / - neighbour | slots |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    f_ = lambda v: "-" if v is None else f"{v:.1f}"
    for k in sorted(c, key=lambda k: (k.split("/")[:-1], view_order(k.split("/")[-1]))):
        parts = k.split("/")
        if parts[0] == "joint" and parts[1] in pieces_:
            j = c[k]
            for side in ("top", "bottom", "left", "right"):
                r = j[side]
                if r["chamfer"] is None and r["joint"] is None:
                    continue
                rows.append(f"| {'/'.join(parts[1:6])} | {parts[6]} | {side} | {f_(r['chamfer_px'])} ({f_(r['chamfer_mm'])}) / {f_(r['chamfer'])} | "
                            f"{f_(r['face'])} | {f_(r['top'])} | {f_(r['joint_px'])} ({f_(r['joint_mm'])}) / {f_(r['joint'])} / {f_(r['joint_p5'])} | "
                            f"{f_(r['n_chamfer'])} / {f_(r['n_face'])} | {f_(r['rim'])} | {f_(r.get('joint_vs_face'))} / "
                            f"{f_(r.get('joint_vs_neighbour'))} | {r['slots']} of {r['profiles']} |")
            for f in j.get("chamfers", []):
                rows.append(f"| {'/'.join(parts[1:6])} | {parts[6]} | chamfer facet {f['side']} ({f['px']} px) | {f_(f['L'])} | "
                            f"{f_(f['face'])} | {f_(f['top'])} | {f_(f['joint'])} | context {f_(f['context'])} | {f_(f['rim'])} | | |")
            ln = j["lines"]
            rows.append(f"| {'/'.join(parts[1:6])} | {parts[6]} | all | rimmed: {', '.join(j['rimmed']) or 'none'} of jointed: "
                        f"{', '.join(j['jointed']) or 'none'}; rings: {'YES' if j['rings'] else 'no'}; joint off by more than {JOINT_TOL:g}: "
                        f"{', '.join(j['joint_off']) or 'none'}; lines in the joints' ring: bright {ln['bright_lines']} ({ln['bright_line_px']} px), "
                        f"dark {ln['dark_lines']} ({ln['dark_line_px']} px) | | | | | | | |")
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


def fit(mask, z, cap=(900, 560), pad=12):
    """The view's zoom, lowered until the piece's whole box fits the tile's cap (a long stone shown whole, not its
    middle), never under 1."""
    ys, xs = np.nonzero(mask)
    w, h = xs.max() - xs.min() + 2 * pad, ys.max() - ys.min() + 2 * pad
    while z > 1 and (w * z > cap[0] or h * z > cap[1]):
        z -= 1
    return z


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
    """grey.png / material.png: the 1 m views side by side in the first row, then per stand and light a row of the
    others, each at native size (far views enlarged, nearest, as far as the piece fits)."""
    rows = []
    pdir = os.path.join(FRAMES, piece)
    for views in (("1m",), ("5m", "12m", "eye5", "eye12")):
        near = []
        for stand in ("sun", "foot"):
            sdir = os.path.join(pdir, stand)
            for moment in stand_moments(sdir):
                row = []
                for view in views:
                    f = os.path.join(sdir, moment, look, "L0", view + ".png")
                    if not os.path.exists(f):
                        continue
                    _, _, mask = load_ids(sdir, "L0", view)
                    z = fit(mask, VIEW_ZOOM.get(view, 1))
                    row.append(labelled(tile(read_png(f), mask, z), f"{piece} {stand} {moment} {view} L0" + (f" x{z}" if z > 1 else "")))
                if views == ("1m",):
                    near += row
                elif row:
                    rows.append(row)
        if near:
            rows.append(near)
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
                m = m0 | m1
                z = fit(m, VIEW_ZOOM[view])
                row += [labelled(tile(a, m, z), f"{moment} {stand} {view} L0" + (f" x{z}" if z > 1 else "")), labelled(tile(b, m, z), "L1"),
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
    # (a piece judged without the arms, the step and the coping, gets no arms sheet)
    if not any(os.path.isdir(os.path.join(pdir, stand, "1600-low-sun", look, arm))
               for stand in ("sun", "foot") for look in ("grey", "material") for arm in ("L0-facets2", "L0-nominor")):
        return None
    for look in ("grey", "material"):
        for arm in ("L0", "L0-facets2", "L0-nominor"):
            row = []
            for stand, moment in (("sun", "1600-low-sun"), ("foot", "1600-low-sun")):
                sdir = os.path.join(pdir, stand)
                for view, z in (("1m", 1), ("5m", 4)):
                    f = os.path.join(sdir, moment, look, arm, view + ".png")
                    if os.path.exists(f):
                        _, _, mask = load_ids(sdir, "L0", view)
                        z = fit(mask, z, cap=(640, 400))
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


def mesh_band(piece, width):
    """A band over a sheet: each level's mesh as Unity imported it (the vertex cost beside the triangles). Every stand
    holds the same mesh; a stand whose counts differ is named."""
    c = json.load(open(os.path.join(STONES, "counts.json")))
    seen = {}
    for k in sorted(c):
        parts = k.split("/")
        if parts[0] == "mesh" and parts[1] == piece:
            m = c[k]
            seen.setdefault(f"L0 {m['L0']['triangles']} TRIS {m['L0']['vertices']} VERTS   "
                            f"L1 {m['L1']['triangles']} TRIS {m['L1']['vertices']} VERTS", []).append(parts[2])
    if not seen:
        return None
    lines = [f"{piece} as imported: {s}" + (f" ({', '.join(st)})" if len(seen) > 1 else "") for s, st in seen.items()]
    band = np.full((10 + 20 * len(lines), width, 3), 0.12, np.float32)
    for i, line in enumerate(lines):
        text(band, line, 6, 5 + 20 * i, scale=2, pad=2)
    return band


def sheets(pieces_):
    for piece in pieces_:
        made = {"grey": sheet_looks(piece, "grey"), "material": sheet_looks(piece, "material"),
                "levels": sheet_levels(piece), "arms": sheet_arms(piece)}
        for name, img in made.items():
            if img is not None:
                band = mesh_band(piece, img.shape[1])
                if band is not None:
                    img = np.concatenate([band, img], 0)
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
