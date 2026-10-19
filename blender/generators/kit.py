"""Mesh building blocks shared by every generator.

A Builder collects faces in plain Python lists, each face tagged with a palette
swatch, and turns them into one mesh object at the end. Geometry is placed in
frames: an origin with three axes (u along a surface, v up it, n out of it), so a
wall, a roof slope or a gable is written once in its own flat coordinates.
"""

import math
from mathutils import Vector

from palette import uv as swatch_uv


class Frame:
    """A local coordinate system: point(a, b, c) = origin + a*u + b*v + c*n."""

    def __init__(self, origin, u, v, n):
        self.o = Vector(origin)
        self.u = Vector(u).normalized()
        self.v = Vector(v).normalized()
        self.n = Vector(n).normalized()

    def point(self, a, b, c=0.0):
        return self.o + self.u * a + self.v * b + self.n * c

    def sub(self, a, b, c=0.0):
        """The same axes, moved to a local point."""
        return Frame(self.point(a, b, c), self.u, self.v, self.n)


WORLD = Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0))  # u = x, v = up, n = -y (front)


def _newell(pts):
    n = Vector((0, 0, 0))
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n.x += (p.y - q.y) * (p.z + q.z)
        n.y += (p.z - q.z) * (p.x + q.x)
        n.z += (p.x - q.x) * (p.y + q.y)
    return n


class Builder:
    def __init__(self):
        self.verts = []  # Vector
        self.faces = []  # list of vertex indices
        self.swatch = []  # swatch name per face
        self.roles = []  # what each face is: 0 part, 1 wall cladding, 2 roof
        self.role = 0
        self.parts = []  # which placed part each face belongs to, -1 for none
        self.part = -1

    # -- low level --------------------------------------------------------

    def face(self, pts, swatch, outward=None):
        """Add a polygon. If outward is given, flip the winding so the normal points away from it."""
        pts = [Vector(p) for p in pts]
        if outward is not None:
            c = sum(pts, Vector()) / len(pts)
            if _newell(pts).dot(c - Vector(outward)) < 0:
                pts.reverse()
        base = len(self.verts)
        self.verts.extend(pts)
        self.faces.append(list(range(base, base + len(pts))))
        self.swatch.append(swatch)
        self.roles.append(self.role)
        self.parts.append(self.part)

    # -- boxes ------------------------------------------------------------

    def box(self, frame, a, b, c, ha, hb, hc, swatch, chamfer=0.0, tilt=0.0):
        """A box centred at local (a, b, c) with half sizes, optionally chamfered and tilted in the u-v plane.

        swatch is a name or a dict keyed by face: 'n+', 'n-', 'u+', 'u-', 'v+', 'v-', 'edge', 'default'.
        """
        def name(key):
            if isinstance(swatch, str):
                return swatch
            return swatch.get(key, swatch.get("default"))

        ct, st = math.cos(tilt), math.sin(tilt)

        def P(x, y, z):
            # rotate in the u-v plane around the box centre, then place
            rx, ry = x * ct - y * st, x * st + y * ct
            return frame.point(a + rx, b + ry, c + z)

        centre = frame.point(a, b, c)
        h = (ha, hb, hc)
        keys = (("u-", "u+"), ("v-", "v+"), ("n-", "n+"))
        w = min(chamfer, 0.45 * min(h))

        if w <= 1e-5:
            corners = {}
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        corners[(sx, sy, sz)] = P(sx * ha, sy * hb, sz * hc)
            for axis in range(3):
                for s in (-1, 1):
                    quad = []
                    for t1, t2 in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                        k = [0, 0, 0]
                        k[axis] = s
                        others = [i for i in range(3) if i != axis]
                        k[others[0]], k[others[1]] = t1, t2
                        quad.append(corners[tuple(k)])
                    self.face(quad, name(keys[axis][(s + 1) // 2]), outward=centre)
            return

        # chamfered: every face inset by w, edges and corners filled in
        def vert(signs, axis):
            p = [0.0, 0.0, 0.0]
            for i in range(3):
                p[i] = signs[i] * (h[i] if i == axis else h[i] - w)
            return P(*p)

        for axis in range(3):
            for s in (-1, 1):
                quad = []
                others = [i for i in range(3) if i != axis]
                for t1, t2 in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                    k = [0, 0, 0]
                    k[axis] = s
                    k[others[0]], k[others[1]] = t1, t2
                    quad.append(vert(k, axis))
                self.face(quad, name(keys[axis][(s + 1) // 2]), outward=centre)
        edge = name("edge") if not isinstance(swatch, str) and "edge" in swatch else None
        for a1 in range(3):
            for a2 in range(a1 + 1, 3):
                a3 = 3 - a1 - a2
                for s1 in (-1, 1):
                    for s2 in (-1, 1):
                        quad = []
                        for s3, first in ((-1, True), (1, True), (1, False), (-1, False)):
                            k = [0, 0, 0]
                            k[a1], k[a2], k[a3] = s1, s2, s3
                            quad.append(vert(k, a1 if first else a2))
                        # the edge takes the colour of its upper or outer neighbour
                        pick = edge or name(keys[a2][(s2 + 1) // 2] if a2 == 1 or a2 == 2 else keys[a1][(s1 + 1) // 2])
                        self.face(quad, pick, outward=centre)
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    k = (sx, sy, sz)
                    tri = [vert(k, 0), vert(k, 1), vert(k, 2)]
                    self.face(tri, edge or name(keys[1][(sy + 1) // 2]), outward=centre)

    # -- turned and cast shapes (posts, poles, bollards) --------------------

    def prism(self, frame, a, c, b0, b1, r0, r1, sides, swatch, top=None, bottom=None, phase=None):
        """A tapered prism standing along v, centred at local (a, c): radius r0 at b0, r1 at b1.

        sides 4 makes a square post, 8 an octagon, 12 or more reads as round. swatch is the
        side colour; top and bottom colour the end caps (no cap when r is 0 there).
        """
        if phase is None:
            phase = math.pi / sides  # a flat face to the front
        ring = [(math.cos(phase + 2 * math.pi * i / sides), math.sin(phase + 2 * math.pi * i / sides)) for i in range(sides)]
        lo = [frame.point(a + r0 * x, b0, c + r0 * y) for x, y in ring]
        hi = [frame.point(a + r1 * x, b1, c + r1 * y) for x, y in ring]
        centre = frame.point(a, (b0 + b1) / 2, c)
        for i in range(sides):
            j = (i + 1) % sides
            if r0 <= 1e-6:
                self.face([frame.point(a, b0, c), hi[j], hi[i]], swatch, outward=centre)
            elif r1 <= 1e-6:
                self.face([lo[i], lo[j], frame.point(a, b1, c)], swatch, outward=centre)
            else:
                self.face([lo[i], lo[j], hi[j], hi[i]], swatch, outward=centre)
        if r1 > 1e-6:
            self.face(hi, top or swatch, outward=centre)
        if r0 > 1e-6:
            self.face(lo, bottom or swatch, outward=centre)

    # -- lapped strips (clapboard, roof courses) ---------------------------

    def strip(self, frame, poly, b0, b1, depth, lap, swatch, side_swatch=None):
        """Extrude a convex polygon (in local a-b) along n by depth.

        The front face leans out towards its bottom edge by lap, like an overlapping board.
        """
        if len(poly) < 3:
            return
        area = 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))
        if area < 1e-5:
            return  # a sliver left by clipping
        span = max(b1 - b0, 1e-6)

        def front(a, b):
            t = min(max((b - b0) / span, 0.0), 1.0)
            return frame.point(a, b, depth + lap * (1.0 - t))

        centre = frame.point(sum(p[0] for p in poly) / len(poly), (b0 + b1) / 2, depth / 2)
        fr = [front(a, b) for a, b in poly]
        bk = [frame.point(a, b, 0.0) for a, b in poly]
        self.face(fr, swatch, outward=centre)
        self.face(bk, side_swatch or swatch, outward=centre)
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            self.face([fr[i], fr[j], bk[j], bk[i]], side_swatch or swatch, outward=centre)

    # -- output -------------------------------------------------------------

    def deform(self, fn):
        self.verts = [fn(p) for p in self.verts]

    def build(self, name, material):
        import bpy

        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        layer = mesh.uv_layers.new(name="UVMap")
        for poly, sw in zip(mesh.polygons, self.swatch):
            u, v = swatch_uv(sw)
            for li in poly.loop_indices:
                layer.data[li].uv = (u, v)
        role = mesh.attributes.new("role", "INT", "FACE")
        role.data.foreach_set("value", self.roles[: len(mesh.polygons)])
        part = mesh.attributes.new("part", "INT", "FACE")
        part.data.foreach_set("value", self.parts[: len(mesh.polygons)])
        mesh.validate(clean_customdata=False)
        mesh.materials.append(material)
        for p in mesh.polygons:
            p.use_smooth = False
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def triangles(self):
        return sum(len(f) - 2 for f in self.faces)


# -- 2D helpers --------------------------------------------------------------


def clip_x(poly, lo, hi):
    """Clip a convex polygon (list of (a, b)) to lo <= a <= hi."""

    def clip(pts, keep, edge):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            pin, qin = keep(p), keep(q)
            if pin:
                out.append(p)
            if pin != qin:
                t = (edge - p[0]) / (q[0] - p[0])
                out.append((edge, p[1] + t * (q[1] - p[1])))
        return out

    pts = clip(poly, lambda p: p[0] >= lo - 1e-9, lo)
    if len(pts) < 3:
        return []
    pts = clip(pts, lambda p: p[0] <= hi + 1e-9, hi)
    return pts if len(pts) >= 3 else []


def clip_below(poly, m, c):
    """Clip a convex polygon to the half-plane b <= m*a + c."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp = p[1] - (m * p[0] + c)
        fq = q[1] - (m * q[0] + c)
        if fp <= 1e-9:
            out.append(p)
        if (fp < -1e-9 and fq > 1e-9) or (fp > 1e-9 and fq < -1e-9):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out if len(out) >= 3 else []


def clip_above(poly, m, c):
    """Clip a convex polygon to the half-plane b >= m*a + c."""
    flipped = [(a, -b) for a, b in poly]
    res = clip_below(flipped, -m, -c)
    return [(a, -b) for a, b in res]


def subtract(intervals, cut):
    """Remove (lo, hi) from a list of (lo, hi) intervals."""
    out = []
    for lo, hi in intervals:
        if cut[1] <= lo or cut[0] >= hi:
            out.append((lo, hi))
            continue
        if cut[0] > lo:
            out.append((lo, cut[0]))
        if cut[1] < hi:
            out.append((cut[1], hi))
    return [(lo, hi) for lo, hi in out if hi - lo > 1e-4]
