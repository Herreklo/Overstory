"""Bedrock as its jointing breaks it: the corner's knuckle (and any outcrop) as the cells its joint families cut.

A rock body is cut by families of parallel joint planes (the foliation and the cross joints), each family's planes at
seeded spacings; together they cut space into convex cells (a plane arrangement: neighbouring cells meet face to face,
exactly). A body keeps the cells whose middle lies in the rock's envelope (the record's outcrop as the heart's land
has it), each clipped by the body's own planes: the ice's rounding of its top (a few broad planes tangent to a low
cap), the cuts men made past it (the gully, the lane), and where the clay it replaces stops. A few of the face's
outermost cells are plucked away (the lee side the ice tore). Every face is a joint, a cut or the ice's plane, so the
rock is a few big facets along its own jointing, never blobby; nothing is bent: the cells are only kept or dropped.

Pure numpy (no bpy): tools/corner_ground.py runs it with Blender's python. Street metres (x towards the Basin's head,
y up the hill, z up). Seeds from stable ids (blender/resolver/hashing.py).
"""

import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402

EPS = 1e-7


def street(bearing):
    """A compass bearing (degrees) as a street direction (x, y)."""
    b = math.radians(bearing)
    return np.array([-math.cos(b), math.sin(b)])


def family_normal(f):
    """A joint family's unit normal (upward), from its dip and the way it dips."""
    d = street(f["dipToward"])
    dip = math.radians(f["dip"])
    return np.array([math.sin(dip) * d[0], math.sin(dip) * d[1], math.cos(dip)])


def offsets(key, f, lo, hi):
    """A family's planes (their n.p) over [lo, hi], each the next at a seeded spacing; a family with a deep spacing
    (the sheeting) is laid from the top down, its planes further apart with depth."""
    rng = HS.Stream(key, "joints", f["name"])
    a = f["spacingM"]
    if "deepSpacingM" in f:
        b, deep = f["deepSpacingM"], f["deepM"]
        t = hi + rng.uniform(0.0, a[1])
        out = [t]
        while t > lo:
            k = min(1.0, max(0.0, (hi - t) / deep))
            t -= rng.uniform(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            out.append(t)
        return np.array(out[::-1])
    t = lo - rng.uniform(0.0, a[1])
    out = [t]
    while t < hi:
        t += rng.uniform(*a)
        out.append(t)
    return np.array(out)


# --- convex cells: a list of faces, each (corners (k, 3), outward normal, d, label); the cell is n.p <= d for all ---

def _orient(V, n):
    """The polygon's corners turned counter-clockwise seen from n."""
    c = V.mean(0)
    a = np.cross(V[1] - V[0], V[2] - V[0])
    if len(V) > 3:
        a = np.zeros(3)
        for i in range(len(V)):
            a += np.cross(V[i] - c, V[(i + 1) % len(V)] - c)
    return V if a @ n >= 0 else V[::-1]


def _cap(points, n):
    """The convex polygon through points on a plane (normal n), counter-clockwise seen from n, duplicates merged."""
    P = np.array(points)
    keep = []
    for p in P:
        if not any(np.linalg.norm(p - q) < 1e-6 for q in keep):
            keep.append(p)
    if len(keep) < 3:
        return None
    P = np.array(keep)
    c = P.mean(0)
    u = P[0] - c
    u -= n * (u @ n)
    u /= max(np.linalg.norm(u), 1e-12)
    v = np.cross(n, u)
    ang = np.arctan2((P - c) @ v, (P - c) @ u)
    return P[np.argsort(ang)]


def clip(cell, n, d, label):
    """The cell less what lies past the plane n.p = d (keeps n.p <= d); the cut's face labelled. None when empty."""
    faces, cut = [], []
    for V, fn, fd, lab in cell:
        s = V @ n - d
        if np.all(s <= EPS):
            faces.append((V, fn, fd, lab))
            cut += [V[i] for i in np.nonzero(np.abs(s) <= EPS)[0]]
            continue
        if np.all(s >= -EPS):
            cut += [V[i] for i in np.nonzero(np.abs(s) <= EPS)[0]]
            continue
        out = []
        for i in range(len(V)):
            p, q = V[i], V[(i + 1) % len(V)]
            sp, sq = s[i], s[(i + 1) % len(V)]
            if sp <= EPS:
                out.append(p)
                if abs(sp) <= EPS:
                    cut.append(p)
            if (sp < -EPS and sq > EPS) or (sp > EPS and sq < -EPS):
                x = p + (q - p) * (sp / (sp - sq))
                out.append(x)
                cut.append(x)
        if len(out) >= 3:
            faces.append((np.array(out), fn, fd, lab))
    if not faces:
        return None
    capV = _cap(cut, n) if len(cut) >= 3 else None
    if capV is not None:
        faces.append((capV, n.copy(), d, label))
    return faces


def polyclip(V, n, d):
    """A convex polygon less what lies past the plane n.p = d (keeps n.p <= d). None when empty."""
    s = V @ n - d
    if np.all(s <= EPS):
        return V
    if np.all(s >= -EPS):
        return None
    out = []
    for i in range(len(V)):
        p, q, sp, sq = V[i], V[(i + 1) % len(V)], s[i], s[(i + 1) % len(V)]
        if sp <= EPS:
            out.append(p)
        if (sp < -EPS and sq > EPS) or (sp > EPS and sq < -EPS):
            out.append(p + (q - p) * (sp / (sp - sq)))
    return np.array(out) if len(out) >= 3 else None


def area(V):
    a = np.zeros(3)
    for i in range(1, len(V) - 1):
        a += np.cross(V[i] - V[0], V[i + 1] - V[0])
    return 0.5 * np.linalg.norm(a)


def volume(cell):
    """The cell's volume and centroid."""
    c0 = np.mean([V.mean(0) for V, *_ in cell], axis=0)
    vol, cen = 0.0, np.zeros(3)
    for V, *_ in cell:
        for i in range(1, len(V) - 1):
            a, b, c = V[0] - c0, V[i] - c0, V[i + 1] - c0
            v = abs(np.dot(a, np.cross(b, c))) / 6.0
            vol += v
            cen += v * (c0 + (V[0] + V[i] + V[i + 1] - 3 * c0) / 4.0)
    return vol, (cen / vol if vol > 1e-12 else c0)


def box_cell(M, lo, hi, labels):
    """The parallelepiped lo <= M p <= hi (three families), its faces labelled (family, plane index, +1 or -1)."""
    Mi = np.linalg.inv(M)
    C = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                C[i, j, k] = Mi @ np.array([(lo[0], hi[0])[i], (lo[1], hi[1])[j], (lo[2], hi[2])[k]])
    faces = []
    for f in range(3):
        for side in (0, 1):
            quad = []
            for a in (0, 1):
                for b in ((0, 1) if a == 0 else (1, 0)):
                    idx = [0, 0, 0]
                    idx[f] = side
                    others = [g for g in range(3) if g != f]
                    idx[others[0]], idx[others[1]] = a, b
                    quad.append(C[tuple(idx)])
            n = M[f] / np.linalg.norm(M[f]) * (1 if side else -1)
            V = _orient(np.array(quad), n)
            d = float(V[0] @ n)
            faces.append((V, n, d, labels[f][side]))
    return faces


# --- the outcrop ---

class Envelope:
    """The rock's room on the heart's land (tools/corner_site.py's grids): where it stands and how high."""

    def __init__(self, site, npz):
        f = site["fine"]
        self.x0, self.y0, self.st = f["x0"], f["y0"], f["step"]
        self.fine, self.bare = npz["fine"], npz["carved_bare"]
        rock = (self.fine - self.bare) > 0.3
        # (grown a little: the foot may spread under the ground round it)
        g = rock.copy()
        r = int(round(1.5 / self.st))
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    g |= np.roll(np.roll(rock, dx, 0), dy, 1)
        self.mask = g
        self.extend = []    # (y0, y1, x): between y0 and y1, the rock west of x stands as it does at x
    def _ij(self, x, y):
        i = np.clip(np.round((np.asarray(x) - self.x0) / self.st).astype(int), 0, self.fine.shape[0] - 1)
        j = np.clip(np.round((np.asarray(y) - self.y0) / self.st).astype(int), 0, self.fine.shape[1] - 1)
        return i, j

    def sample(self, A, x, y):
        """Bilinear."""
        u = np.clip((np.asarray(x, float) - self.x0) / self.st, 0, A.shape[0] - 1.001)
        v = np.clip((np.asarray(y, float) - self.y0) / self.st, 0, A.shape[1] - 1.001)
        i, j = u.astype(int), v.astype(int)
        fu, fv = u - i, v - j
        return ((A[i, j] * (1 - fu) + A[i + 1, j] * fu) * (1 - fv) + (A[i, j + 1] * (1 - fu) + A[i + 1, j + 1] * fu) * fv)

    def ground(self, x, y):
        return self.sample(self.bare, x, y)

    def inside(self, p, cap=None):
        """Whether a point lies in the rock: under the land's top where the outcrop stands (out to the cuts men made
        past it), and under the cap's own surface (cap(x, y)) where given."""
        x, y = p[..., 0], p[..., 1]
        for y0, y1, xf in self.extend:
            x = np.where((y >= y0) & (y <= y1) & (x < xf), xf, x)
        i, j = self._ij(x, y)
        ok = self.mask[i, j] & (p[..., 2] < self.sample(self.fine, x, y))
        if cap is not None:
            ok &= p[..., 2] < cap(p[..., 0], p[..., 1])
        return ok


def dome_surface(D):
    """The low cap itself, z(x, y)."""
    cx, cy = D["centre"]
    rx, ry = D["radii"]

    def z(x, y):
        ex, ey = (np.asarray(x) - cx) / rx, (np.asarray(y) - cy) / ry
        return D["top"] - D["drop"] * (ex * ex + ey * ey)
    return z


def dome_planes(key, name, D, lift=0.0):
    """A low cap's broad planes: tangent to it at seeded points about planeM apart (z <= each), lifted by lift."""
    rng = HS.Stream(key, "dome", name)
    cx, cy = D["centre"]
    rx, ry = D["radii"]
    s = D["planeM"]
    pts = [(cx, cy)]
    nx, ny = int(math.ceil(2 * rx / s)), int(math.ceil(2 * ry / s))
    for a in range(nx + 1):
        for b in range(ny + 1):
            x = cx - rx + a * 2 * rx / nx + rng.uniform(-0.3, 0.3) * s
            y = cy - ry + b * 2 * ry / ny + rng.uniform(-0.3, 0.3) * s
            pts.append((x, y))
    planes = []
    for k, (x, y) in enumerate(pts):
        ex, ey = (x - cx) / rx, (y - cy) / ry
        z = D["top"] - D["drop"] * (ex * ex + ey * ey)
        fx, fy = -2 * D["drop"] * ex / rx, -2 * D["drop"] * ey / ry
        n = np.array([-fx, -fy, 1.0])
        d = z + lift - fx * x - fy * y
        L = np.linalg.norm(n)
        planes.append((n / L, d / L, ("top", name, k)))
    return planes


def vplane(a, b, keep):
    """The upright plane through street points a and b, keeping the side of point keep (n.p <= d)."""
    a, b, keep = np.asarray(a, float), np.asarray(b, float), np.asarray(keep, float)
    t = (b - a) / np.linalg.norm(b - a)
    n = np.array([t[1], -t[0], 0.0])
    d = n[:2] @ a
    if n[:2] @ keep > d:
        n, d = -n, -d
    return n, d


def lane_edge(pts, half, side):
    """A lane's edge, offset half its width to one side (+1 left of its run, -1 right), as segments."""
    P = np.asarray(pts, float)[:, :2]
    out = []
    for a, b in zip(P[:-1], P[1:]):
        t = (b - a) / np.linalg.norm(b - a)
        left = np.array([-t[1], t[0]])
        out.append((a + side * half * left, b + side * half * left))
    return out


# --- the bodies and their cells ---

class Body:
    """One convex piece of the rock's room: its planes (cuts, the clay's edge, the bottom) and its cap."""

    def __init__(self, name, planes, dome):
        self.name, self.planes, self.dome = name, planes, dome
        self.cells = {}     # key -> (faces, volume, centroid)
        self.solid = set()

    def holds(self, q):
        return all(n @ q <= d + 1e-6 for n, d, lab in self.planes)


def arrangement(key, fams, lo, hi):
    """The joint families' cells over the box lo..hi: (key, faces) for each, the faces labelled
    (family, plane index, side). The first three families make parallelepipeds, the rest cut them."""
    N = [family_normal(f) for f in fams]
    C = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    T = []
    for f, n in zip(fams, N):
        r = C @ n
        T.append(offsets(key, f, r.min(), r.max()))
    M = np.array(N[:3])
    out = []
    rng3 = [range(len(T[f]) - 1) for f in range(3)]
    for i in rng3[0]:
        for j in rng3[1]:
            for k in rng3[2]:
                a = np.array([T[0][i], T[1][j], T[2][k]])
                b = np.array([T[0][i + 1], T[1][j + 1], T[2][k + 1]])
                labels = [((0, i, -1), (0, i + 1, 1)), ((1, j, -1), (1, j + 1, 1)), ((2, k, -1), (2, k + 1, 1))]
                cell = box_cell(M, a, b, labels)
                P = np.vstack([V for V, *_ in cell])
                if np.any(P.max(0) < lo) or np.any(P.min(0) > hi):
                    continue
                subs = [((i, j, k), cell)]
                for f in range(3, len(fams)):
                    nxt = []
                    for kk, c in subs:
                        P = np.vstack([V for V, *_ in c])
                        r = P @ N[f]
                        for l in range(len(T[f]) - 1):
                            if T[f][l + 1] <= r.min() or T[f][l] >= r.max():
                                continue
                            s = clip(c, N[f], T[f][l + 1], (f, l + 1, 1))
                            if s is None:
                                continue
                            s = clip(s, -N[f], -T[f][l], (f, l, -1))
                            if s is not None:
                                nxt.append((kk + (l,), s))
                    subs = nxt
                out += subs
    return out, N, T


def neighbour(key, lab):
    """The cell across a joint face."""
    f, _, side = lab
    k = list(key)
    k[f] += side
    return tuple(k)


def build(fix, site, npz):
    """The knuckle's bodies with their kept cells, from the fixture's jointing, domes and cuts."""
    K = fix["knuckle"]
    key = K["id"]
    env = Envelope(site, npz)
    fams = K["jointing"]["families"]
    lo, hi = np.array([50.3, 27.8, 2.4]), np.array([66.1, 49.6, 13.0])
    cells, N, T = arrangement(key, fams, lo, hi)
    # (which joints are open: a seeded share of each family's planes; the rest are tight, and a face runs on across
    # them unbroken)
    env.open = [[i for i in range(len(t)) if HS.unit(HS.h(key, "open", f["name"], i)) < f.get("openShare", 1.0)]
                for f, t in zip(fams, T)]

    cuts = K["cuts"]
    gully = vplane(cuts["gully"]["a"], cuts["gully"]["b"], (60.0, 30.0))
    # (the cut leans back from its foot: its batter)
    bt = math.radians(cuts["gully"].get("batterDeg", 0.0))
    gn = np.array([gully[0][0] * math.cos(bt), gully[0][1] * math.cos(bt), math.sin(bt)])
    a3 = np.array([*cuts["gully"]["a"], cuts["gully"].get("footZ", 0.0)])
    gully = (gn, float(gn @ a3))
    landing = (np.array([-1.0, 0.0, 0.0]), -cuts["landing"]["x"])
    lane = [l for l in site["lanes"] if l["name"] == "High Terrace"][0]
    half = cuts["terraceWidth"] / 2 + cuts["terraceMargin"]
    pts = [p for p in lane["pts"] if 44 <= p[0] <= 68]
    south = lane_edge(pts, half, -1)
    north = lane_edge(pts, half, +1)
    # (the fin keeps south of the edge where the lane runs past it; the upper rock north of every segment)
    fin_lane = vplane(*[s for s in south if s[0][0] <= 58.5 <= s[1][0] + 0.1][0], (57.0, 30.0))
    up_lane = [vplane(a, b, (57.0, 46.0)) for a, b in north]

    def P(n, d, lab):
        return (np.asarray(n, float), float(d), lab)

    def xle(x, lab):
        return P((1, 0, 0), x, lab)

    def xge(x, lab):
        return P((-1, 0, 0), -x, lab)

    def yle(y, lab):
        return P((0, 1, 0), y, lab)

    def yge(y, lab):
        return P((0, -1, 0), -y, lab)

    def zge(z):
        return P((0, 0, -1), -z, ("bottom",))

    # (the cap: the cells under it are kept, their tops the sheeting's own steps; the ice's planes, a little over it,
    # cut what stands too proud)
    D = {name: v for name, v in K["domes"].items() if not name.startswith("_")}
    domes = {name: dome_planes(key, name, v, v.get("clipLiftM", 0.0)) for name, v in D.items()}
    caps = {name: dome_surface(v) for name, v in D.items()}
    g = cuts["gully"]
    env.extend.append((min(g["a"][1], g["b"][1]), max(g["a"][1], g["b"][1]), g["rockToX"]))
    cutg = P(gully[0], gully[1], ("cut", "gully"))
    cutf = P(fin_lane[0], fin_lane[1], ("cut", "lane"))
    cutl = P(landing[0], landing[1], ("cut", "landing"))
    cutu = [P(n, d, ("cut", "lane")) for n, d in up_lane]
    bodies = [
        Body("F1", [cutg, cutf, xle(60.0, ("box", "x60")), yge(28.5, ("box", "y28.5")), zge(2.5)], "fin"),
        Body("F2", [cutf, xge(60.0, ("box", "x60")), xle(61.5, ("box", "x61.5")), yge(30.0, ("box", "y30")),
                    zge(2.5)], "fin"),
        Body("U1", [cutl, *cutu, xle(60.0, ("box", "x60")), yle(43.5, ("box", "y43.5")), zge(6.0)], "upper"),
        Body("U2", [*cutu, xge(60.0, ("box", "x60")), xle(61.5, ("box", "x61.5")), yle(42.0, ("box", "y42")),
                    zge(6.0)], "upper"),
        Body("U3", [*cutu, xge(54.0, ("box", "x54")), xle(60.0, ("box", "x60")), yge(43.5, ("box", "y43.5")),
                    yle(49.5, ("box", "y49.5")), zge(6.0)], "upper"),
        Body("U4", [*cutu, xge(61.5, ("box", "x61.5")), xle(64.5, ("box", "x64.5")), yle(40.5, ("box", "y40.5")),
                    zge(6.0)], "upper"),
        Body("U5", [*cutu, xge(64.5, ("box", "x64.5")), xle(66.0, ("box", "x66")), yle(39.0, ("box", "y39")),
                    zge(6.0)], "upper"),
    ]
    rule = {k: v for k, v in K.get("faces", {}).items() if not k.startswith("_")}
    names = [f["name"] for f in fams]
    for B in bodies:
        fill = any(F.get("fill") for F in rule.get(B.name, []))
        planes = B.planes + [(n, d, lab) for n, d, lab in domes[B.dome]]
        for k, cell in cells:
            Pc = np.vstack([V for V, *_ in cell])
            # (quick reject: wholly past one of the body's planes)
            if any(np.all(Pc @ n > d) for n, d, lab in planes):
                continue
            v0, _ = volume(cell)
            c = cell
            for n, d, lab in planes:
                c = clip(c, n, d, lab)
                if c is None:
                    break
            if c is None:
                continue
            v, cen = volume(c)
            if v < 1e-4:
                continue
            B.cells[k] = (c, v, cen)
            if fill:
                if cen[2] >= caps[B.dome](cen[0], cen[1]):
                    continue
            elif not env.inside(cen, caps[B.dome]):
                continue
            # (a sliver the cap left on a cell's top falls away; one against a cut or the clay's edge stays)
            held = any(lab[0] in ("cut", "box") for *_, lab in c)
            if not held and (v < 0.12 or v < 0.2 * v0):
                continue
            B.solid.add(k)
    for B in bodies:
        for F in rule.get(B.name, []):
            face_rule(key, B, F, env, names, N, T)
    pluck(key, K["pluck"]["share"], bodies, env)
    support(bodies, env)
    return bodies, env, N


def support(bodies, env):
    """Nothing floats: a kept cell stays only if a chain of kept cells, face to face, carries it down to the ground."""
    seen, todo = set(), []
    for B in bodies:
        for k in B.solid:
            c = B.cells[k][0]
            P = np.vstack([V for V, *_ in c])
            if np.any(P[:, 2] <= env.ground(P[:, 0], P[:, 1]) + 0.3) or any(lab[0] == "bottom" for *_, lab in c):
                seen.add((B.name, k))
                todo.append((B, k))
    while todo:
        B, k = todo.pop()
        for V, n, lab, X in _faces(B, k, bodies)[1]:
            if X not in seen:
                seen.add(X)
                todo.append(([O for O in bodies if O.name == X[0]][0], X[1]))
    for B in bodies:
        B.solid = {k for k in B.solid if (B.name, k) in seen}


def slab(T, n, p):
    """The index of the slab (between planes i and i + 1) a point lies in."""
    return int(np.searchsorted(T, float(n @ np.asarray(p, float))) - 1)


def supercell(env, k):
    """The block a cell belongs to when only the open joints count: cells across a tight joint are one block."""
    return tuple(int(np.searchsorted(o, i, side="right")) for o, i in zip(env.open, k))


def face_rule(key, B, F, env, names, N, T):
    """A face stands on one plane of its family: through the fixture's point (at), or else, in each column of another
    family, the outermost the rock still holds faceM over the ground. What stood beyond it has fallen, but for a
    seeded share of the big blocks at its foot (the next slab out, under footM, clear of the clay's edge). side +1 is
    the family's own normal's way, -1 the other."""
    f, side = names.index(F["family"]), F["side"]
    if "at" in F:
        m0 = side * slab(T[f], N[f], F["at"])
        front = None
    else:
        g = names.index(F["column"])
        front = {}
        for k in B.solid:
            cen = B.cells[k][2]
            if cen[2] >= env.ground(cen[0], cen[1]) + F["faceM"]:
                front[k[g]] = max(front.get(k[g], -1 << 30), side * k[f])
    drop = []
    for k in B.solid:
        m = m0 if front is None else front.get(k[g])
        if m is None or side * k[f] <= m:
            continue
        c, v, cen = B.cells[k]
        if side * k[f] == m + 1 and cen[2] < env.ground(cen[0], cen[1]) + F["footM"] and \
                not any(lab[0] == "box" for *_, lab in c) and \
                HS.unit(HS.h(key, "foot", F["family"], *supercell(env, k))) < F.get("footShare", 1.0):
            continue
        drop.append(k)
    for k in drop:
        B.solid.discard(k)


def _faces(B, k, bodies, cell=None):
    """A kept cell's faces: those that show, and those hidden against a kept cell (with that cell's (body, key)).
    Never the bottom; a joint against a kept neighbour, or the clay's edge where the next body goes on, is hidden."""
    shown, hidden = [], []
    for V, n, d, lab in (cell if cell is not None else B.cells[k][0]):
        if lab[0] == "bottom":
            continue
        if isinstance(lab[0], int):
            nb = neighbour(k, lab)
            if nb in B.solid:
                hidden.append((V, n, lab, (B.name, nb)))
                continue
        elif lab[0] == "box":
            q = V.mean(0) + 0.05 * n
            O = [O for O in bodies if O is not B and k in O.solid and O.holds(q)]
            if O:
                hidden.append((V, n, lab, (O[0].name, k)))
                continue
        shown.append((V, n, lab))
    return shown, hidden


def _faces_out(B, k, bodies):
    return _faces(B, k, bodies)[0]


def pluck(key, share, bodies, env):
    """The lee face's outermost blocks the ice tore away: of the cells showing a face to the street (downhill), a
    seeded share, never the low ones (big blocks low) nor those held by a cut."""
    for B in bodies:
        if not B.name.startswith("F"):
            continue
        drop = []
        for k in sorted(B.solid):
            c, v, cen = B.cells[k]
            if any(lab[0] == "cut" for *_, lab in c):
                continue
            if cen[2] < env.ground(cen[0], cen[1]) + 1.6:
                continue
            front = [n for V, n, lab in _faces_out(B, k, bodies) if isinstance(lab[0], int) and n[1] < -0.35]
            if front and HS.unit(HS.h(key, "pluck", *supercell(env, k))) < share:
                drop.append(k)
        for k in drop:
            B.solid.discard(k)


def spalls(key, sp, bodies, env):
    """The plates the open joint faces have shed (the foliation's thin plates and the joints' skins break away as a
    piece): for a seeded share of each kept cell's open joint faces, the face set back a plate's depth. Rigid: the cell
    is only cut along a plane parallel to its own face, and a whole block (cells across tight joints) sheds the
    same plate, so the steps fall only at open joints. (body, key) -> (planes, the cell as it now stands)."""
    E = {}
    lo, hi = sp["depthM"]
    for B in bodies:
        for k in sorted(B.solid):
            c0, v0, _ = B.cells[k]
            planes = []
            for V, n, lab in _faces_out(B, k, bodies):
                if not isinstance(lab[0], int):
                    continue
                h = HS.h(key, "spall", *supercell(env, k), *lab)
                if HS.unit(h) >= sp["share"]:
                    continue
                s = lo + (hi - lo) * HS.unit(HS.h(h, "depth"))
                planes.append((n, float(V[0] @ n) - s, lab))
            if not planes:
                continue
            c = c0
            for n, d, lab in planes:
                c = clip(c, n, d, lab) if c is not None else None
            if c is None or volume(c)[0] < 0.6 * v0:
                continue
            E[(B.name, k)] = (planes, c)
    return E


def faces(bodies, env, key=None, sp=None):
    """Every face that shows: (corners, normal, label, body, cell key), less those wholly in the ground. With sp, the
    shed plates (spalls), and where a cell has shed one against a kept neighbour, the strip of the neighbour's face it
    bares."""
    E = spalls(key, sp, bodies, env) if sp else {}
    out = []

    def keep(V, n, lab, B, k):
        g = env.ground(V[:, 0], V[:, 1])
        if not np.all(V[:, 2] < g - 0.05) and area(V) > 1e-4:
            out.append((V, n, lab, B.name, k))
    for B in bodies:
        for k in sorted(B.solid):
            cell = E[(B.name, k)][1] if (B.name, k) in E else None
            shown, hidden = _faces(B, k, bodies, cell)
            for V, n, lab in shown:
                keep(V, n, lab, B, k)
            for V, n, lab, X in hidden:
                if X not in E:
                    continue
                planes = E[X][0]
                for i, (ni, di, _) in enumerate(planes):
                    P = polyclip(V, -ni, -di)
                    for nj, dj, _ in planes[:i]:
                        P = polyclip(P, nj, dj) if P is not None else None
                    if P is not None:
                        keep(P, n, lab, B, k)
    return out


def fix_tjunctions(F, tol=2e-5):
    """Each face's corners with every other face's corners that lie on its edges put in, so faces meet point to point
    (no cracks where a shed plate's strip meets the face beside it). Returns each face's ring of points."""
    allp = np.unique(np.round(np.vstack([V for V, *_ in F]), 6), axis=0)
    rings = []
    for V, *_ in F:
        ring = []
        for i in range(len(V)):
            a, b = V[i], V[(i + 1) % len(V)]
            ring.append(a)
            ab = b - a
            L2 = ab @ ab
            lo, hi = np.minimum(a, b) - tol, np.maximum(a, b) + tol
            m = np.all((allp >= lo) & (allp <= hi), axis=1)
            Q = allp[m]
            if len(Q):
                t = (Q - a) @ ab / L2
                dist = np.linalg.norm(Q - a - np.outer(t, ab), axis=1)
                ok = (dist < tol) & (t > 1e-4) & (t < 1 - 1e-4)
                for j in np.argsort(t[ok]):
                    ring.append(Q[ok][j])
        rings.append(np.array(ring))
    return rings


# --- tessellation: exact on every edge (an edge's points from its two ends alone), a web inside ---

def _edge(a, b, h):
    m = max(1, int(math.ceil(np.linalg.norm(b - a) / h - 1e-6)))
    flip = tuple(np.round(a, 6)) > tuple(np.round(b, 6))
    p, q = (b, a) if flip else (a, b)
    pts = [p + (q - p) * (s / m) for s in range(m)] + [q]
    if flip:
        pts = pts[::-1]
    return pts[:-1]


def tessellate(V, n, h, ring=None, he=None, inset=0.0):
    """A convex face as triangles (k, 3, 3). Its edges (the ring's points, corners and any T-points) split from their
    own ends alone at he(a, b) (the same on both faces that share one), the inside a web about h apart; with inset, a
    first ring that far in, so what is baked at the edge (a joint's dark margin) stays that narrow."""
    pts = V if ring is None else ring
    he = he or (lambda a, b: h)
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        out += _edge(a, b, he(a, b))
    ring = np.array(out)
    c = V.mean(0)
    m = len(ring)
    tris = []
    rc = np.linalg.norm(ring - c, axis=1)
    if inset > 0 and rc.min() > 3 * inset:
        inner = ring + (c - ring) * (inset / rc)[:, None]
        for i in range(m):
            j = (i + 1) % m
            tris.append([ring[i], ring[j], inner[j]])
            tris.append([ring[i], inner[j], inner[i]])
        ring = inner
    R = int(math.ceil(np.max(np.linalg.norm(ring - c, axis=1)) / h - 1e-6))
    if not tris and (m == 3 or (m == len(V) and R <= 1)):
        tris = [[ring[0], ring[i], ring[i + 1]] for i in range(1, m - 1)]
    else:
        R = max(R, 1)
        rings = [c + (ring - c) * (r / R) for r in range(1, R + 1)]
        for i in range(m):
            j = (i + 1) % m
            tris.append([c, rings[0][i], rings[0][j]])
            for r in range(1, R):
                a, b = rings[r - 1], rings[r]
                tris.append([a[i], b[i], b[j]])
                tris.append([a[i], b[j], a[j]])
    T = np.array(tris)
    # (each turned outward)
    cr = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    flip = cr @ n < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    return T[np.linalg.norm(cr, axis=1) > 1e-10]
