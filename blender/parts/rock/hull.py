"""Convex bodies cut by planes: the rock's one geometric primitive (pure numpy, no bpy).

A body is the intersection of half-spaces n.p <= d. It is kept as its faces, each a convex polygon (k, 3) counter-
clockwise seen from outside, with its plane and a label (what cut it: a joint family, the ice, a cut, the sea).
Clipping a body by a plane keeps the side n.p <= d and closes the hole with a cap carrying the plane's label, so every
face of a rock is the plane that made it, exactly: nothing is bent (BB3). Street or site metres, z up.
"""

import numpy as np

EPS = 1e-7


class Face:
    __slots__ = ("V", "n", "d", "label")

    def __init__(self, V, n, d, label):
        self.V, self.n, self.d, self.label = V, n, d, label


def _orient(V, n):
    c = V.mean(0)
    a = np.zeros(3)
    for i in range(len(V)):
        a += np.cross(V[i] - c, V[(i + 1) % len(V)] - c)
    return V if a @ n >= 0 else V[::-1]


def _cap(points, n):
    """The convex polygon through points lying on a plane of normal n, counter-clockwise seen from n."""
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
    if np.linalg.norm(u) < 1e-9:
        u = P[1] - c
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    ang = np.arctan2((P - c) @ v, (P - c) @ u)
    P = P[np.argsort(ang)]
    # drop collinear points
    out = []
    for i in range(len(P)):
        a, b, c2 = P[i - 1], P[i], P[(i + 1) % len(P)]
        if np.linalg.norm(np.cross(b - a, c2 - b)) > 1e-9:
            out.append(b)
    return np.array(out) if len(out) >= 3 else None


def box(lo, hi, label="box"):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    C = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    spec = [((0, 3, 2, 1), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)), ((0, 1, 5, 4), (0, -1, 0)),
            ((2, 3, 7, 6), (0, 1, 0)), ((1, 2, 6, 5), (1, 0, 0)), ((3, 0, 4, 7), (-1, 0, 0))]
    faces = []
    for idx, n in spec:
        n = np.array(n, float)
        V = C[list(idx)]
        faces.append(Face(_orient(V, n), n, float(n @ V[0]), label))
    return faces


def clip(faces, n, d, label):
    """The body cut by the plane n.p = d, keeping n.p <= d; None when nothing is left."""
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    out, cap = [], []
    for f in faces:
        s = f.V @ n - d
        if np.all(s <= EPS):
            out.append(f)
            continue
        if np.all(s >= -EPS):
            continue
        V = []
        k = len(f.V)
        for i in range(k):
            a, b = f.V[i], f.V[(i + 1) % k]
            sa, sb = s[i], s[(i + 1) % k]
            if sa <= EPS:
                V.append(a)
            if (sa < -EPS and sb > EPS) or (sa > EPS and sb < -EPS):
                p = a + (b - a) * (sa / (sa - sb))
                V.append(p)
                cap.append(p)
            elif abs(sa) <= EPS:
                cap.append(a)
        if len(V) >= 3:
            out.append(Face(np.array(V), f.n, f.d, f.label))
    if not out:
        return None
    C = _cap(cap, n) if len(cap) >= 3 else None
    if C is not None:
        out.append(Face(_orient(C, n), n, d, label))
    return out


def body(lo, hi, planes):
    """A box cut by planes [(n, d, label)]; None when empty."""
    f = box(lo, hi)
    for n, d, label in planes:
        f = clip(f, n, d, label)
        if f is None:
            return None
    return f


def through(n, p):
    """d for the plane of normal n through point p."""
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    return float(n @ np.asarray(p, float))


def normal(dip, dip_toward):
    """A plane's upward unit normal from its dip (degrees from horizontal) and the compass way it dips, x east y north."""
    a, b = np.radians(dip), np.radians(dip_toward)
    return np.array([np.sin(a) * np.sin(b), np.sin(a) * np.cos(b), np.cos(a)])


def volume(faces):
    c = np.mean([f.V.mean(0) for f in faces], 0)
    v = 0.0
    for f in faces:
        for i in range(1, len(f.V) - 1):
            v += np.dot(f.V[0] - c, np.cross(f.V[i] - c, f.V[i + 1] - c)) / 6
    return v


def triangles(faces):
    """Fan-triangulated faces: (verts (n, 3), tris (m, 3), labels per tri, normals per tri)."""
    V, T, L, N = [], [], [], []
    for f in faces:
        b = len(V)
        V.extend(f.V)
        for i in range(1, len(f.V) - 1):
            T.append((b, b + i, b + i + 1))
            L.append(f.label)
            N.append(f.n)
    return np.array(V), np.array(T), L, np.array(N)
