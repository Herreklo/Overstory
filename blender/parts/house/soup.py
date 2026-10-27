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
        self.tri(a, b, c, ta[0], ta[1], ta[2], None if laps is None else (la[0], la[1], la[2]),
                 None if ns is None else (ns[0], ns[1], ns[2]), None if marks is None else (mk[0], mk[1], mk[2]))
        self.tri(a, c, d, ta[0], ta[2], ta[3], None if laps is None else (la[0], la[2], la[3]),
                 None if ns is None else (ns[0], ns[2], ns[3]), None if marks is None else (mk[0], mk[2], mk[3]))

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

    def triangles(self):
        return len(self.p) // 3

    def merge(self, other):
        self.p += other.p
        self.nrm += other.nrm
        self.ch += other.ch

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
