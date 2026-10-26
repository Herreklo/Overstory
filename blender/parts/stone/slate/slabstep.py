"""The slab step (port step 2b, R2b): a step of the town's split slate as reference 06 shows one
(docs/references/stone/06-worn-stair-with-lichen-dale-vestland.jpg): a slab the stair's rise thick, laid on its bed,
its top a bedding plane; its front and open ends split across the laminae, so each lamina stands a little in or out
of the next and the arris between them is a line of light or of shadow; its nosing rounded by weather and feet, here
and there a piece of the top lamina lost so the one beneath shows; its corners knocked. Rigid: the flight sets it,
settled, and never bends it.

    step(seed, L, H, D, tread, ends, p, wear=None) -> dict(P (3 t, 3) the triangles' corners, kind (t,), soft (t,))

The coping slab (coping, below) is the same slab laid flat across a wall's top, split on both long sides.

Its frame: x along the step (0 its left end, L its right), y up from its bed (0) to its top (H), z back from its
front's line (0) to its back (D), in metres. tread is how far back its top is seen (the next step stands on the
rest). ends is (left, right), each "open" (a split end in view), "joint" (against the next piece of its tread) or
"walled" (under a cheek wall, unseen). wear(x, z) is the mm the feet took from its top there (the record's, from the
generator); p is the definition's params (mm, degrees).

It has no cheaper level seen as itself: its laminae, its lost flake, the wear's rows and its round's middle facet each
show from 6 to 18 m in low sun, so L1 is L0 and it hands over to the chunk's level (reviews/lt1/port/2b/r2b/step). Triangles face out of the stone (cross(b - a, c - a)).
Numpy only; deterministic from the seed (blender/resolver/hashing.py's streams).
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)
from split import inset  # noqa: E402

MM = 0.001


def _between(rng, lo_hi):
    return rng.uniform(lo_hi[0], lo_hi[1])


def _laminae(rng, H, p):
    """The heights of the laminae's beds, from 0 to H: a few, none thinner than the least."""
    k = rng.weighted([(int(c), int(w)) for c, w in p["laminae"]])
    least = p["laminaLeastMm"] * MM
    k = max(1, min(k, int(H // least)))
    w = np.array([rng.uniform(0.6, 1.4) for _ in range(k)])
    t = least + (H - k * least) * w / w.sum()
    return np.concatenate([[0.0], np.cumsum(t)])


def _front(rng, L, p):
    """The front's points along x and its line's wander in z; and the stretch where a piece of the top lamina is lost
    (the points inside it), if one is."""
    xs = [0.0]
    while xs[-1] < L:
        xs.append(xs[-1] + _between(rng, p["frontPointMm"]) * MM)
    if L - xs[-2] < 0.5 * p["frontPointMm"][0] * MM and len(xs) > 2:
        xs.pop(-2)
    xs[-1] = L
    lost = None
    if rng.random() < p["lossChance"] and L > 0.45:
        span = min(_between(rng, p["lossMm"]) * MM, 0.5 * L)
        a = rng.uniform(0.08, L - span - 0.08)
        e0, e1 = (min(_between(rng, p["lossEdgeMm"]) * MM, 0.3 * span) for _ in range(2))
        keep = [x for x in xs if not (a - 0.03 < x < a + span + 0.03)]
        cuts = sorted(rng.uniform(0.1, 0.9) for _ in range(p["lossPoints"] - 2))
        mid = [a + e0 + (span - e0 - e1) * t for t in [0.0] + cuts + [1.0]]
        # (the front's points held to the budget's most: the plain ones thinned where they are closest)
        while len(keep) + len(mid) + 2 > p["frontPointsMost"] and len(keep) > 2:
            gaps = [min(keep[i] - keep[i - 1], keep[i + 1] - keep[i]) for i in range(1, len(keep) - 1)]
            keep.pop(1 + int(np.argmin(gaps)))
        xs = sorted(keep + [a] + mid + [a + span])
        lost = (a + 0.5 * e0, a + span - 0.5 * e1, _between(rng, p["lossDepthMm"]) * MM, a, span)
    while len(xs) > p["frontPointsMost"]:
        gaps = [min(xs[i] - xs[i - 1], xs[i + 1] - xs[i]) for i in range(1, len(xs) - 1)]
        xs.pop(1 + int(np.argmin(gaps)))
    wander, stepw = p["frontWanderMm"] * MM, p["frontWanderStepMm"] * MM
    z, zs = rng.uniform(-wander, wander), []
    for _ in xs:
        z = float(np.clip(z + rng.uniform(-stepw, stepw), -wander, wander))
        zs.append(z)
    return np.array(xs), np.array(zs), lost


def _broken(lost, x):
    """Whether a point at x along a side is on its break, the slanted ends included (all of it sharp, fresh)."""
    return lost is not None and lost[3] - 1e-6 <= x <= lost[3] + lost[4] + 1e-6


class _Soup:
    """Triangles facing out of the stone (cross(b - a, c - a)), each with its kind, whether it is shaded soft, and
    each corner's share of the sky its place leaves it (1 in the open, less in a concave corner)."""

    def __init__(self):
        self.tris, self.kinds, self.soft, self.sky = [], [], [], []

    def tri(self, a, b, c, kd, sf, outward, sky=(1.0, 1.0, 1.0)):
        nrm = np.cross(b - a, c - a)
        if np.linalg.norm(nrm) < 1e-12:
            return
        if np.dot(nrm, outward) < 0:
            b, c = c, b
            sky = (sky[0], sky[2], sky[1])
        self.tris.append((a, b, c))
        self.kinds.append(kd)
        self.soft.append(sf)
        self.sky.extend(sky)

    def result(self, **kw):
        P = np.array([v for t in self.tris for v in t])
        return dict(P=P, kind=np.array(self.kinds, dtype=np.int8), soft=np.array(self.soft), sky=np.array(self.sky),
                    **kw)


def _outn(band, s):
    """The segment's outward normal in plan (x, z): the outline runs counter-clockwise, so out is its right."""
    e = band[(s + 1) % len(band)] - band[s]
    return np.array([e[1], 0.0, -e[0]])


def _P3(q, y):
    return np.array([q[0], y, q[1]])


def _faces(out, bands, Y, closed, foot=0.5, footMm=40.0, line=10.0):
    """The laminae's split faces, each lamina from its bed to the next's, each facet flat; and between laminae the
    ledge where one stands out of the next: lit from above where the lower stands out, a line of shadow where the
    upper overhangs (split where they cross). An open outline leaves out its last segment (a step's back). Where a
    lamina stands back of the one below, the corner at its foot sees less sky: half (a concave right angle's) once the
    ledge is footMm deep, so a break's back is a dark line (a strip line mm wide at its foot) and a lamina's a faint
    one."""
    k, m = len(bands), len(bands[0])
    segs = m if closed else m - 1

    def back(j, s):
        """The sky at lamina j's foot at point s: less as the lamina below stands out of it."""
        if j == 0:
            return 1.0
        lo, up = bands[j - 1], bands[j]
        o = _outn(lo, s if closed or s < m - 1 else s - 1)
        o = o / max(np.linalg.norm(o), 1e-12)
        d = float(np.dot(np.array([lo[s][0] - up[s][0], 0, lo[s][1] - up[s][1]]), o))
        return 1.0 - foot * min(1.0, max(0.0, d) / (footMm * MM))
    for j in range(k):
        b = bands[j]
        for s in range(segs):
            s1 = (s + 1) % m
            a0, a1 = _P3(b[s], Y[j][s]), _P3(b[s1], Y[j][s1])
            t0, t1 = _P3(b[s], Y[j + 1][s]), _P3(b[s1], Y[j + 1][s1])
            o = _outn(b, s)
            f0, f1 = back(j, s), back(j, s1)
            out.tri(a0, a1, t1, 2, False, o, (f0, f1, 1.0))
            out.tri(a0, t1, t0, 2, False, o, (f0, 1.0, 1.0))
    for j in range(1, k):
        lo, up = bands[j - 1], bands[j]
        for s in range(segs):
            s1 = (s + 1) % m
            o = _outn(lo, s)
            d0 = float(np.dot(np.array([lo[s][0] - up[s][0], 0, lo[s][1] - up[s][1]]), o))
            d1 = float(np.dot(np.array([lo[s1][0] - up[s1][0], 0, lo[s1][1] - up[s1][1]]), o))
            L0, L1 = _P3(lo[s], Y[j][s]), _P3(lo[s1], Y[j][s1])
            U0, U1 = _P3(up[s], Y[j][s]), _P3(up[s1], Y[j][s1])
            g0, g1 = back(j, s), back(j, s1)
            ln = max(float(np.linalg.norm(o)), 1e-12)
            if d0 > 1.5 * line * MM * ln and d1 > 1.5 * line * MM * ln:
                # (a deep ledge, a break's floor: its foot a strip a line wide, so the dark at the foot is a line)
                M0 = U0 + (L0 - U0) * (line * MM * ln / d0)
                M1 = U1 + (L1 - U1) * (line * MM * ln / d1)
                f = np.array([0, 1.0, 0])
                out.tri(L0, L1, M1, 0, False, f)
                out.tri(L0, M1, M0, 0, False, f)
                out.tri(M0, M1, U1, 0, False, f, (1.0, 1.0, g1))
                out.tri(M0, U1, U0, 0, False, f, (1.0, g1, g0))
            elif d0 * d1 >= 0:
                f = np.array([0, 1.0 if d0 + d1 > 0 else -1.0, 0])
                kd = 0 if f[1] > 0 else 3
                out.tri(L0, L1, U1, kd, False, f, (1.0, 1.0, g1))
                out.tri(L0, U1, U0, kd, False, f, (1.0, g1, g0))
            else:
                t = d0 / (d0 - d1)
                X = L0 + t * (L1 - L0)
                for (A, B, dd, g) in ((L0, U0, d0, g0), (L1, U1, d1, g1)):
                    f = np.array([0, 1.0 if dd > 0 else -1.0, 0])
                    out.tri(A, B, X, 0 if dd > 0 else 3, False, f, (1.0, g, 1.0))


def _round(out, top, I, y0, y1, y2, broke, closed):
    """The top's arris a quarter round: three rings, the top lamina's outline at y0, a ring 45 degrees round at y1,
    the top's inset outline I at y2; soft but where a break's fresh arris is."""
    m = len(top)
    ring = [[_P3(top[s], y0[s]) for s in range(m)],
            [_P3(top[s] + (I[s] - top[s]) * 0.293, y1[s]) for s in range(m)],
            [_P3(I[s], y2[s]) for s in range(m)]]
    for r0, r1 in zip(ring[:-1], ring[1:]):
        for s in range(m if closed else m - 1):
            s1 = (s + 1) % m
            o = _outn(top, s) + np.array([0, 1.0, 0])
            sf = not (broke[s] or broke[s1])
            out.tri(r0[s], r0[s1], r1[s1], 1, sf, o)
            out.tri(r0[s], r1[s1], r1[s], 1, sf, o)


def step(seed, L, H, D, tread, ends, p, wear=None):
    rng = HS.Stream(seed, "slabstep-r2b")
    wear = wear or (lambda x, z: 0.0)
    ys = _laminae(rng, H, p)
    xs, zs, lost = _front(rng, L, p)
    # a lost piece takes a thin flake off the top: the flake its own lamina
    if lost is not None:
        th = _between(rng, p["lossThickMm"]) * MM
        if ys[-1] - ys[-2] > th + p["laminaLeastMm"] * MM:
            ys = np.concatenate([ys[:-1], [H - th, H]])
    k = len(ys) - 1
    n = len(xs)
    # each end's line from the front back, slanted in plan where it was split
    slant = {}
    for side, e in zip(("l", "r"), ends):
        slant[side] = 0.0 if e == "walled" else rng.uniform(-1.0, 1.0) * p["endSlant"][e] * D
    # each lamina's own outline: the front's line moved in or out, each point a little, each split end out or in;
    # its points [back left, the front's n points, back right] (counter-clockwise in x and z, closed by the back)
    out_mm = p["laminaOutMm"] * MM
    jit = p["laminaJitterMm"] * MM
    ostep = p["laminaOutStepMm"] * MM
    bands = []
    for j in range(k):
        # (its offset wanders along the step: here flush with the next, there standing out, so its line comes and goes)
        off, offs = rng.uniform(-out_mm, out_mm), []
        for _ in range(n):
            off = float(np.clip(off + rng.uniform(-ostep, ostep), -out_mm, out_mm))
            flush = abs(off) < p["laminaFlushShare"] * out_mm
            offs.append((0.0 if flush else off) + rng.uniform(-jit, jit))
        fz = zs + np.array(offs)
        if lost is not None and j == k - 1:
            inside = (xs > lost[0]) & (xs < lost[1])
            # (the break's back line an arch, deepest in its middle, each point a little off it)
            arch = np.sin(np.pi * np.clip((xs - lost[3]) / lost[4], 0.0, 1.0)) ** 0.6
            fz = fz + np.where(inside, lost[2] * arch * np.array([rng.uniform(*p["lossRagged"]) for _ in range(n)]), 0.0)
        ex = {}
        for side, e in zip(("l", "r"), ends):
            ex[side] = 0.0 if e == "walled" else rng.uniform(-1.0, 1.0) * p["endOutMm"][e] * MM
        F = np.column_stack([xs, fz])
        F[0, 0] -= ex["l"]
        F[-1, 0] += ex["r"]
        bl = np.array([F[0, 0] + slant["l"], D])
        br = np.array([F[-1, 0] + slant["r"], D])
        bands.append(np.vstack([bl, F, br]))
    # the top lamina's front corners knocked, at an open end most
    top = bands[-1]
    for i, (e, nb) in ((1, (ends[0], 2)), (n, (ends[1], n - 1))):
        if e == "walled":
            continue
        kn = _between(rng, p["knockMm"][e]) * MM
        c = top[i].copy()
        top[i] = c + (top[nb] - c) / np.linalg.norm(top[nb] - c) * min(kn, 0.4 * np.linalg.norm(top[nb] - c))
        top[i] += (top[i - 1 if i == 1 else i + 1] - c) / np.linalg.norm(top[i - 1 if i == 1 else i + 1] - c) * kn * 0.5
    m = n + 2
    # the beds between laminae not quite level: each bed's height wanders a little at each point
    wave = p["laminaWaveMm"] * MM
    Y = [np.zeros(m)] + [np.full(m, ys[j]) + np.array([rng.uniform(-wave, wave) for _ in range(m)]) for j in range(1, k)]
    # the nosing and the open ends' top arris rounded: the feet's wear rounds it further
    c0 = _between(rng, p["nosingMm"]) * MM
    ce = {e: _between(rng, p["endRoundMm"][e]) * MM for e in ("open", "joint", "walled")}
    vary = [rng.uniform(*p["nosingVary"]) for _ in range(m)]
    ch = np.zeros(m)
    wpt = np.zeros(m)
    for s in range(m):
        x, z = top[s]
        wpt[s] = wear(x, max(z, 0.0)) * MM
        if s == 0 or s == m - 1:
            ch[s] = ce[ends[0] if s == 0 else ends[1]]
        elif _broken(lost, x):
            ch[s] = p["breakRoundMm"] * MM
        else:
            ch[s] = c0 * vary[s] + p["roundPerWear"] * wpt[s]
    for s in (1, m - 2):
        ch[s] = 0.5 * (ch[s] + ce[ends[0] if s == 1 else ends[1]])
    I = inset(top, ch)
    Y.append(np.full(m, H) - ch - wpt)

    out = _Soup()
    _faces(out, bands, Y, closed=False)
    # the rounded arris: a quarter round from the top lamina's face to the top, pulled in by its round (a ring at its
    # middle, 45 degrees round); a break's arris is fresh and sharp, not shaded round with the top
    broke = [_broken(lost, top[s][0]) for s in range(m)]
    _round(out, top, I, Y[k], H - wpt - 0.293 * ch, [H - wear(*I[s]) * MM for s in range(m)], broke, closed=False)
    # the top, a bedding plane worn by the feet: rows back from the round, fine where the wear is, to the back
    rows_z = [z for z in p["topRowsMm"]] + [tread * 1000 - p["mossRowMm"], tread * 1000]
    front = I[1:m - 1]
    lb, rb = I[0], I[m - 1]

    def end_x(c0_, c1_, z):
        t = (z - c0_[1]) / (c1_[1] - c0_[1]) if abs(c1_[1] - c0_[1]) > 1e-9 else 0.0
        return c0_[0] + t * (c1_[0] - c0_[0])

    rows = [front.copy()]
    for zr in rows_z + [None]:
        r = np.zeros_like(front)
        for i in range(n):
            z = max(zr * MM, rows[-1][i, 1] + 0.015) if zr is not None else max(lb[1], rb[1], rows[-1][i, 1] + 0.015)
            if zr is not None and z >= D - 0.02:
                z = max(rows[-1][i, 1] + 0.015, D - 0.03)
            x = front[i, 0]
            if i == 0:
                x = end_x(front[0], lb, z)
            elif i == n - 1:
                x = end_x(front[-1], rb, z)
            r[i] = (x, z)
        rows.append(r)
    up = np.array([0, 1.0, 0])
    for r0, r1 in zip(rows[:-1], rows[1:]):
        for i in range(n - 1):
            q = [_P3(v, H - wear(*v) * MM) for v in (r0[i], r0[i + 1], r1[i + 1], r1[i])]
            out.tri(q[0], q[1], q[2], 0, True, up)
            out.tri(q[0], q[2], q[3], 0, True, up)
    # its back, against the fill under the next step (seen only behind a flight's top step)
    back = [_P3(bands[0][0], 0.0), _P3(bands[0][-1], 0.0), _P3(rows[-1][-1], H), _P3(rows[-1][0], H)]
    o = np.array([0, 0, 1.0])
    out.tri(back[0], back[1], back[2], 2, False, o)
    out.tri(back[0], back[2], back[3], 2, False, o)
    return out.result(H=H, L=L, D=D, lost=lost)


def coping(seed, L, H, D, ends, p):
    """A coping slab (the same split slate as the step, laid on its bed across a wall's top): its top a bedding plane
    rounded only by the weather, its front and back split across the laminae as a step's front is, here and there a
    flake of the top lamina lost from either; its ends split where they are seen, near square where it meets the next.

        coping(seed, L, H, D, ends, p) -> dict(P, kind, soft, H, L, D, lost)

    Its frame: x along the run (0 its left end, L its right), y up from its bed, z back from its front's line (0) to
    its back's (D). ends is (left, right), each "open", "joint" or "walled" (butted into the run above a step down,
    unseen); p is the coping's definition's params. Like the step's, its L1 is L0 (reviews/lt1/port/2b/r2b/coping)."""
    rng = HS.Stream(seed, "coping-r2b")
    ys = _laminae(rng, H, p)
    fx, fz, flost = _front(rng, L, p)
    bx, bz, blost = _front(rng, L, p)
    if flost is not None or blost is not None:
        th = _between(rng, p["lossThickMm"]) * MM
        if ys[-1] - ys[-2] > th + p["laminaLeastMm"] * MM:
            ys = np.concatenate([ys[:-1], [H - th, H]])
    k = len(ys) - 1
    nf, nb = len(fx), len(bx)
    m = nf + nb
    slant = {s: (0.0 if e == "walled" else rng.uniform(-1.0, 1.0) * p["endSlant"][e] * D) for s, e in zip("lr", ends)}
    out_mm, jit, ostep = p["laminaOutMm"] * MM, p["laminaJitterMm"] * MM, p["laminaOutStepMm"] * MM

    def offsets(n, lost, xs, flake):
        off, offs = rng.uniform(-out_mm, out_mm), []
        for _ in range(n):
            off = float(np.clip(off + rng.uniform(-ostep, ostep), -out_mm, out_mm))
            offs.append((0.0 if abs(off) < p["laminaFlushShare"] * out_mm else off) + rng.uniform(-jit, jit))
        offs = np.array(offs)
        if lost is not None and flake:
            inside = (xs > lost[0]) & (xs < lost[1])
            arch = np.sin(np.pi * np.clip((xs - lost[3]) / lost[4], 0.0, 1.0)) ** 0.6
            offs = offs + np.where(inside, lost[2] * arch * np.array([rng.uniform(*p["lossRagged"]) for _ in range(n)]), 0.0)
        return offs

    # each lamina's outline: the front's points left to right, then the back's right to left (counter-clockwise in x
    # and z); each side's line moved in or out along it, each end out or in, the back's corners off square by the slant
    bands = []
    for j in range(k):
        F = np.column_stack([fx, fz + offsets(nf, flost, fx, j == k - 1)])
        Bk = np.column_stack([bx, D - bz - offsets(nb, blost, bx, j == k - 1)])
        for side, e, i in (("l", ends[0], 0), ("r", ends[1], -1)):
            ex = 0.0 if e == "walled" else rng.uniform(-1.0, 1.0) * p["endOutMm"][e] * MM
            F[i, 0] += ex if i else -ex
            Bk[i, 0] += (ex if i else -ex) + slant[side]
        bands.append(np.vstack([F, Bk[::-1]]))
    # the top lamina's corners knocked, at an open end most: each corner moved along its side and a little along its end
    top = bands[-1]
    for i, along, end, e in ((0, 1, m - 1, ends[0]), (nf - 1, nf - 2, nf, ends[1]),
                             (nf, nf + 1, nf - 1, ends[1]), (m - 1, m - 2, 0, ends[0])):
        if e == "walled":
            continue
        kn = _between(rng, p["knockMm"][e]) * MM
        c = top[i].copy()
        da, de = top[along] - c, top[end] - c
        top[i] = c + da / np.linalg.norm(da) * min(kn, 0.4 * np.linalg.norm(da)) + de / np.linalg.norm(de) * kn * 0.5
    wave = p["laminaWaveMm"] * MM
    Y = [np.zeros(m)] + [np.full(m, ys[j]) + np.array([rng.uniform(-wave, wave) for _ in range(m)]) for j in range(1, k)]
    # the top's arris rounded by the weather alone; a break's fresh; a corner between its side's round and its end's
    c0 = _between(rng, p["roundMm"]) * MM
    ce = {e: _between(rng, p["endRoundMm"][e]) * MM for e in ("open", "joint", "walled")}
    vary = [rng.uniform(*p["roundVary"]) for _ in range(m)]
    side_lost = [flost] * nf + [blost] * nb
    broke = [_broken(lo, top[s][0]) for s, lo in enumerate(side_lost)]
    ch = np.array([p["breakRoundMm"] * MM if broke[s] else c0 * vary[s] for s in range(m)])
    for s, e in ((0, ends[0]), (m - 1, ends[0]), (nf - 1, ends[1]), (nf, ends[1])):
        ch[s] = 0.5 * (ch[s] + ce[e])
    I = inset(top, ch)
    Y.append(np.full(m, H) - ch)
    out = _Soup()
    _faces(out, bands, Y, closed=True)
    _round(out, top, I, Y[k], H - 0.293 * ch, np.full(m, H), broke, closed=True)

    def zip_(Fc, Bc, y, kd, up):
        """The plane between the front's chain and the back's, both left to right, in a strip of triangles."""
        i = j_ = 0
        while i < len(Fc) - 1 or j_ < len(Bc) - 1:
            if j_ == len(Bc) - 1 or (i < len(Fc) - 1 and Fc[i + 1][0] <= Bc[j_ + 1][0]):
                out.tri(_P3(Fc[i], y), _P3(Fc[i + 1], y), _P3(Bc[j_], y), kd, kd == 0, up)
                i += 1
            else:
                out.tri(_P3(Fc[i], y), _P3(Bc[j_ + 1], y), _P3(Bc[j_], y), kd, kd == 0, up)
                j_ += 1
    # its top, a bedding plane; its bed, seen only under its overhangs
    zip_(I[:nf], I[nf:][::-1], H, 0, np.array([0, 1.0, 0]))
    zip_(bands[0][:nf], bands[0][nf:][::-1], 0.0, 3, np.array([0, -1.0, 0]))
    r = out.result(H=H, L=L, D=D, lost=(flost, blost))
    # split, it is thicker at one end and to one side than the other: its top a plane off its bed's
    ta, tb = (_between(rng, t) * MM for t in p["taperMm"])
    P = r["P"]
    P[:, 1] *= 1.0 + (ta * (P[:, 0] / L - 0.5) + tb * (P[:, 2] / D - 0.5)) / H
    return r
