"""A house's triangles and what each vertex carries, written as an R2B2 triangle soup for Unity (LT1Houses.Load).

Triangles are in the street's frame (x east, y north, z up, metres), wound counter-clockwise seen from outside. The
writer turns them into Unity's frame (x, z, y), a mirror that the loader's turn of the winding sets right.

The vertex layout (eight float2 sets; the house shader, unity/Assets/Shaders/House.shader, reads them by these names):
  uv0  surf      the surface's own coordinates in metres: along the piece (its grain) and up it
  uv1  kind      what the face is (KINDS) and the house's row in the houses buffer
  uv2  piece     the piece's seed in [0, 1) (a board, a casing, a tile course) and the year it was put up
  uv3  bake      what the face sees: sky, ground (blender/generators/bake.py's rays)
  uv4  bake2     openness, and a lit window's own seed (0 when it is not lit)
  uv5  place     where on its piece: the board's height from its lap edge (0) to its top (1); how sheltered it is
  uv6  coat      which coat scheme paints it (SCHEMES), and its storey band
  uv7  marks     where water works into a board: how much a sill's run-off reaches it, how near it is to its end grain
Only piece constants and intrinsic geometry sit on vertices; the house's coats and care are the buffer's.
"""

import math
import struct

KINDS = {"board": 0, "underside": 1, "trim": 2, "sash": 3, "glass": 4, "tile": 5, "stone": 6, "render": 7,
         "boarding": 8, "door": 9, "room": 10, "metal": 11, "endgrain": 12, "mortar": 13, "joint": 14}
SCHEMES = {"none": 0, "body": 1, "trim": 2, "window": 3, "door": 4, "stain": 5, "back": 6}


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-12 else (0.0, 0.0, 1.0)


class Frame:
    """A plane's frame: origin o, u along it, up v, out n (u x v = n). A point (s, z, w) is o + s u + z v + w n."""

    def __init__(self, o, u, v):
        self.o, self.u, self.v = o, norm(u), norm(v)
        self.n = norm(cross(self.u, self.v))

    def at(self, s, z, w=0.0):
        o, u, v, n = self.o, self.u, self.v, self.n
        return (o[0] + s * u[0] + z * v[0] + w * n[0], o[1] + s * u[1] + z * v[1] + w * n[1],
                o[2] + s * u[2] + z * v[2] + w * n[2])


class Soup:
    """Triangles with their channels. The current attributes (set with .use) go on every triangle added."""

    def __init__(self):
        self.p, self.nrm, self.ch = [], [], []
        # each triangle's face: a quad's two triangles share one (the bake lights a face as one)
        self.fid, self._faces, self._quad = [], 0, None
        self.a = dict(kind=0, house=0, seed=0.0, year=1800.0, lap=0.5, shelter=0.0, scheme=0, band=0.0, lit=0.0)
        # the level drawn (0 near, 1 street, 2 city) and its error (m): a box shallower than the error shows only
        # its front, its sides being under a pixel at the distance the level is seen from (timber.json, levels)
        self.level, self.err = 0, 0.0

    def use(self, **kw):
        for k, v in kw.items():
            if k == "kind":
                v = KINDS[v]
            elif k == "scheme":
                v = SCHEMES[v]
            self.a[k] = v
        return self

    def tri(self, a, b, c, ta=(0.0, 0.0), tb=(0.0, 0.0), tc=(0.0, 0.0), laps=None, ns=None, marks=None):
        """ns: the corners' own normals (a rounded surface), else the face's. marks: the corners' uv7, else none."""
        n = cross(sub(b, a), sub(c, a))
        if dot(n, n) < 1e-16:
            return
        n = norm(n)
        A = self.a
        if self._quad is None:
            self.fid.append(self._faces)
            self._faces += 1
        else:
            self.fid.append(self._quad)
        for i, (p, t) in enumerate(((a, ta), (b, tb), (c, tc))):
            self.p.append(p)
            self.nrm.append(n if ns is None else ns[i])
            lap = A["lap"] if laps is None else laps[i]
            mk = (0.0, 0.0) if marks is None else marks[i]
            self.ch.append((t[0], t[1], A["kind"], A["house"], A["seed"], A["year"], lap, A["shelter"],
                            A["scheme"], A["band"], A["lit"], mk[0], mk[1]))

    def quad(self, a, b, c, d, ta=None, laps=None, ns=None, marks=None):
        """a b c d counter-clockwise seen from outside; ta their surface coordinates; ns their own normals; marks
        their uv7."""
        ta = ta or ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        la = laps or (None, None, None, None)
        mk = marks or (None, None, None, None)
        self._quad = self._faces
        self._faces += 1
        self.tri(a, b, c, ta[0], ta[1], ta[2], None if laps is None else (la[0], la[1], la[2]),
                 None if ns is None else (ns[0], ns[1], ns[2]), None if marks is None else (mk[0], mk[1], mk[2]))
        self.tri(a, c, d, ta[0], ta[2], ta[3], None if laps is None else (la[0], la[2], la[3]),
                 None if ns is None else (ns[0], ns[2], ns[3]), None if marks is None else (mk[0], mk[2], mk[3]))
        self._quad = None

    def box(self, f, s0, s1, z0, z1, w0, w1, skip=("back",), grain="s"):
        """A box in frame f's (s, z, w) space; its faces outward. skip names faces not drawn (back: the w0 face).
        grain: the surface coordinates run along s (a horizontal piece) or z (a vertical one)."""
        P = lambda s, z, w: f.at(s, z, w)
        def tc(x, y):
            return (x, y) if grain == "s" else (y, x)
        faces = {
            "front": ((s0, z0, w1), (s1, z0, w1), (s1, z1, w1), (s0, z1, w1)),
            "back": ((s1, z0, w0), (s0, z0, w0), (s0, z1, w0), (s1, z1, w0)),
            "top": ((s0, z1, w1), (s1, z1, w1), (s1, z1, w0), (s0, z1, w0)),
            "bottom": ((s0, z0, w0), (s1, z0, w0), (s1, z0, w1), (s0, z0, w1)),
            "left": ((s0, z0, w0), (s0, z0, w1), (s0, z1, w1), (s0, z1, w0)),
            "right": ((s1, z0, w1), (s1, z0, w0), (s1, z1, w0), (s1, z1, w1)),
        }
        thin = self.level > 0 and w1 - w0 < self.err
        for name, q in faces.items():
            if name in skip or (thin and name != "front"):
                continue
            if name in ("front", "back"):
                t = [tc(c[0], c[1]) for c in q]
            elif name in ("top", "bottom"):
                t = [tc(c[0], c[2]) for c in q]
            else:
                t = [tc(c[2], c[1]) for c in q]
            self.quad(*(P(*c) for c in q), ta=t)

    def poly(self, pts, out, ta=None):
        """A flat convex polygon (3 or 4 points), wound to face out (a direction)."""
        n = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
        if dot(n, out) < 0.0:
            pts = pts[::-1]
            ta = ta[::-1] if ta else None
        if len(pts) == 3:
            t = ta or ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
            self.tri(pts[0], pts[1], pts[2], t[0], t[1], t[2])
        else:
            self.quad(*pts, ta=ta)

    def bbox(self, f, s0, s1, z0, z1, w0, w1, c, skip=("back",), grain="s"):
        """A box in frame f's (s, z, w) space as box() draws it, its arrises chamfered by c (m): each edge between
        two drawn faces becomes a narrow face of its own that catches the light, and each corner a small triangle.
        Only at the level that draws them (near): a chamfer under the level's error is a plain box. The chamfer is
        never more than a quarter of the box's least drawn side."""
        lo, hi = (s0, z0, w0), (s1, z1, w1)
        names = {(0, 0): "left", (0, 1): "right", (1, 0): "bottom", (1, 1): "top", (2, 0): "back", (2, 1): "front"}
        thin = self.level > 0 and w1 - w0 < self.err
        drawn = {k: (v not in skip and not (thin and v != "front")) for k, v in names.items()}
        c = min(c, 0.25 * min(hi[a] - lo[a] for a in range(3)))
        if self.level > 0 or c < 1e-4:
            return self.box(f, s0, s1, z0, z1, w0, w1, skip=skip, grain=grain)
        axes = (f.u, f.v, f.n)

        def P(q):
            return f.at(q[0], q[1], q[2])

        def tc(x, y):
            return (x, y) if grain == "s" else (y, x)

        def V(corner, a):
            # the corner's vertex on face (a, its side): pulled in along the other axes where their face is drawn
            q = [hi[k] if corner[k] else lo[k] for k in range(3)]
            for b in range(3):
                if b != a and drawn[(b, corner[b])]:
                    q[b] += -c if corner[b] else c
            return q

        def t_of(q, a):
            # the surface coordinates a face on axis a carries (as box() gives them)
            return tc(q[0], q[1]) if a == 2 else tc(q[0], q[2]) if a == 1 else tc(q[2], q[1])

        def out(a, side):
            return mul(axes[a], 1.0 if side else -1.0)

        corners = [(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
        for a in range(3):
            b_, c_ = [x for x in range(3) if x != a]
            for side in (0, 1):
                if not drawn[(a, side)]:
                    continue
                # the face's four corners in order round it
                order = [(0, 0), (1, 0), (1, 1), (0, 1)]
                ring = []
                for u_, v_ in order:
                    cr = [0, 0, 0]
                    cr[a], cr[b_], cr[c_] = side, u_, v_
                    ring.append(tuple(cr))
                qs = [V(cr, a) for cr in ring]
                self.poly([P(q) for q in qs], out(a, side), ta=[t_of(q, a) for q in qs])
        # the chamfers along each edge where two drawn faces meet
        for a in range(3):
            for b in range(a + 1, 3):
                k = 3 - a - b
                for sa in (0, 1):
                    for sb in (0, 1):
                        if not (drawn[(a, sa)] and drawn[(b, sb)]):
                            continue
                        ends = []
                        for sk in (0, 1):
                            cr = [0, 0, 0]
                            cr[a], cr[b], cr[k] = sa, sb, sk
                            ends.append(tuple(cr))
                        qs = [V(ends[0], a), V(ends[1], a), V(ends[1], b), V(ends[0], b)]
                        o = norm(add(out(a, sa), out(b, sb)))
                        self.poly([P(q) for q in qs], o, ta=[t_of(q, a) for q in qs])
        # the corners where three drawn faces meet
        for cr in corners:
            if all(drawn[(a, cr[a])] for a in range(3)):
                qs = [V(cr, a) for a in range(3)]
                o = norm(add(add(out(0, cr[0]), out(1, cr[1])), out(2, cr[2])))
                self.poly([P(q) for q in qs], o, ta=[t_of(q, 2) for q in qs])

    def triangles(self):
        return len(self.p) // 3

    def merge(self, other):
        self.p += other.p
        self.nrm += other.nrm
        self.ch += other.ch
        self.fid += [f + self._faces for f in other.fid]
        self._faces += other._faces

    def write(self, path, bake=None):
        """The R2B2 soup: magic, count, positions, normals, then the eight UV sets (Unity's frame: x, z, y).
        bake: per vertex (sky, ground, open), or None for a neutral wall's."""
        count = len(self.p)
        with open(path, "wb") as f:
            f.write(struct.pack("<4si", b"R2B2", count))
            f.write(b"".join(struct.pack("<3f", p[0], p[2], p[1]) for p in self.p))
            f.write(b"".join(struct.pack("<3f", n[0], n[2], n[1]) for n in self.nrm))
            sets = [
                lambda i, c: (c[0], c[1]),
                lambda i, c: (c[2], c[3]),
                lambda i, c: (c[4], c[5]),
                lambda i, c: (bake[i][0], bake[i][1]) if bake else (0.5, 0.3),
                lambda i, c: (bake[i][2] if bake else 1.0, c[10]),
                lambda i, c: (c[6], c[7]),
                lambda i, c: (c[8], c[9]),
                lambda i, c: (c[11], c[12]),
            ]
            for fn in sets:
                f.write(b"".join(struct.pack("<2f", *fn(i, c)) for i, c in enumerate(self.ch)))
