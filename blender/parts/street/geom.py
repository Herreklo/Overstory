"""What every street part is built with, carried from the finishing test's corner (blender/parts/finish/corner.py,
the p3 floor at de6e1c0): faces in a part's own frame, profiles swept along a line, charts on the house's page, and
the Blender objects with face-weighted normals. A part is built along local +x, outward local -y, up +z; `place` maps
it into the house's frame (x along the street front, y back from the building line, z up, metres).
"""

import math

import bmesh
import bpy
from mathutils import Vector

MM = 0.001


class Face:
    __slots__ = ("p", "uv0", "chart", "cuv", "arris", "under", "col")

    def __init__(self, p, uv0, chart, cuv, arris=False, under=False, col=None):
        self.p, self.uv0, self.chart, self.cuv, self.arris, self.under = p, uv0, chart, cuv, arris, under
        self.col = col  # a face's own vertex colour (a pane's glass), in place of the piece's


class Piece:
    """One part in its own frame. `mode` says how the frame moves it: 'frame' bends with the timber, 'rigid' is only
    moved and turned. `wall` is the wall it stands on (an index into the house's walls, -1 for none), `group` the
    course table its boards follow."""

    def __init__(self, pid, mat, levels, place, mode="frame", kind=None, wall=-1, group=0):
        self.id, self.mat, self.levels, self.place, self.mode = pid, mat, levels, place, mode
        self.kind = kind or pid.split("/")[1]
        self.faces = {lv: [] for lv in levels}
        self.anchor, self.along = None, None
        self.wall, self.group = wall, group

    def add(self, level, face):
        self.faces[level].append(face)


class Charts:
    """The page's charts: key -> (w, h) metres and a density factor, the same at every level."""

    def __init__(self):
        self.size, self.scale = {}, {}

    def __call__(self, key, w, h, density=1.0):
        old = self.size.get(key)
        self.size[key] = (max(w, old[0] if old else 0), max(h, old[1] if old else 0))
        self.scale[key] = density
        return key

    def pack(self, page, px, size):
        """Rows, tallest first, on a page `size` pixels square. Returns key -> (x, y, w, h) in pixels and the share
        of the page filled, or None if the charts do not fit at `px` pixels a metre."""
        pad = page["padPx"]
        items = sorted(self.size.items(), key=lambda kv: (-math.ceil(kv[1][1] * px * self.scale[kv[0]]), kv[0]))
        x = y = row_h = 0
        out = {}
        for key, (w, h) in items:
            d = px * self.scale[key]
            wp, hp = math.ceil(w * d) + 2 * pad, math.ceil(h * d) + 2 * pad
            if wp > size:
                return None, 0
            if x + wp > size:
                x, y, row_h = 0, y + row_h, 0
            out[key] = (x + pad, y + pad, wp - 2 * pad, hp - 2 * pad, d)
            x += wp
            row_h = max(row_h, hp)
        if y + row_h > size:
            return None, 0
        return out, (y + row_h) / size

    def fit(self, page):
        """The smallest of the page's sizes that holds the charts at holdPxPerM or more, at the most pixels a metre
        (in whole steps) that fit; a house too big for that takes the biggest page at what fits there, down to
        pxPerM's least. Returns rects, fill, px and the page's size."""
        for size in page["sizes"]:
            px = page["pxPerM"][1]
            floor = page["holdPxPerM"] if size < page["sizes"][-1] else page["pxPerM"][0]
            while px >= floor:
                rects, fill = self.pack(page, px, size)
                if rects is not None:
                    return rects, fill, px, size
                px -= 2
        raise SystemExit(f"[house] the page is full even at {page['sizes'][-1]} px and {page['pxPerM'][0]} px a metre")


def newell(pts):
    n = Vector((0.0, 0.0, 0.0))
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def outward(prof, P, Q, d):
    """Walk the profile so every swept face looks away from the solid: with (P, Q, d) right-handed a face's normal
    is its edge turned left, so the closed section must run clockwise in (p, q). Each point carries the attributes
    of the edge leaving it, so a reversed walk shifts them by one."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(prof, prof[1:] + prof[:1]))
    hand = P.cross(Q).dot(d)
    if area * hand <= 0:
        return prof
    n = len(prof)
    pts = prof[::-1]
    return [(pts[k][0], pts[k][1]) + tuple(prof[n - 2 - k][2:]) if k < n - 1 else pts[k] for k in range(n)]


def cap_bounds(prof):
    ps = [p[0] for p in prof]
    qs = [p[1] for p in prof]
    return (min(ps), min(qs), max(ps), max(qs))


def cap_size(prof):
    b = cap_bounds(prof)
    return (max(b[2] - b[0], 0.005), max(b[3] - b[1], 0.005))


def extrude(piece, level, prof, o, L, P, Q, charts, nseg=1, caps=(False, False), planar=None, cut=None, nominal=None):
    """Sweep a 2D profile along a straight line, in the piece's frame.

    prof: [(p, q, group, arris)] points in order (an open polyline); each edge (i, i+1) takes the group and arris of
    its first point. o: start; L: the sweep (its length the piece's length); P, Q: the profile's axes. Charts: each
    group's (length x width) unless `planar` gives a function local point -> (chartkey, cu, cv) for wall-plane
    charting. `cut` (start, end) gives each end's offset along the sweep as a function of the profile point (p, q):
    an end sawn askew, or a board's end cut to a gable's rake. UV0 is metres along the sweep and across the group."""
    length = L.length
    d = L.normalized()
    prof = outward(prof, P, Q, d)
    nominal = nominal or {}
    groups = {}
    for i in range(len(prof) - 1):
        g = prof[i][2]
        a = math.dist(prof[i][:2], prof[i + 1][:2])
        groups.setdefault(g, [0.0, []])
        groups[g][1].append((i, groups[g][0], a))
        groups[g][0] += a
    for i in range(len(prof) - 1):
        g, arris = prof[i][2], prof[i][3]
        total = groups[g][0]
        start = next(s for (j, s, a) in groups[g][1] if j == i)
        a = math.dist(prof[i][:2], prof[i + 1][:2])
        nom = nominal.get(g, total)
        for k in range(nseg):
            t0, t1 = k / nseg, (k + 1) / nseg
            pts, uv0, cuv = [], [], []
            for (t, j, s) in ((t0, i, start), (t1, i, start), (t1, i + 1, start + a), (t0, i + 1, start + a)):
                along = t * length + (cut[int(t)](*prof[j][:2]) if cut is not None and t in (0, 1) else 0.0)
                p = o + d * along + P * prof[j][0] + Q * prof[j][1]
                pts.append(p)
                frac = s / total if total > 0 else 0.0
                if planar is not None:
                    key, cu, cv = planar(p)
                    cuv.append((cu, cv))
                    uv0.append((cu, cv))
                else:
                    cuv.append((along, frac * nom))
                    uv0.append((along, frac * nom))
            key = planar(pts[0])[0] if planar is not None else charts(f"{piece.id}#{g}", length + 0.02, nom)
            piece.add(level, Face(pts, uv0, key, cuv, arris))
    for end, on in ((0, caps[0]), (1, caps[1])):
        if not on:
            continue
        t = end * length
        bounds = cap_bounds(prof)
        ring = list(prof)
        pts = [o + d * (t + (cut[end](*p[:2]) if cut is not None else 0.0)) + P * p[0] + Q * p[1] for p in ring]
        if newell(pts).dot(d) * (1 if end else -1) < 0:
            pts, ring = pts[::-1], ring[::-1]
        key = charts(f"{piece.id}#cap{end}", *cap_size(prof))
        cuv = [((p[0] - bounds[0]), (p[1] - bounds[1])) for p in ring]
        piece.add(level, Face(pts, list(cuv), key, cuv, False))


def rect_profile(w, h, c, groups=("bottom", "front", "top", "back"), chamfer_edges=(True, True), back=False):
    """A board's section, p across (0..w), q out of the wall (0..h): points walk bottom -> front -> top, each
    carrying the group and arris flag of the edge that leaves it. `c` chamfers the two front arrises when
    chamfer_edges says so; a chamfer belongs to the front's group and is flagged as an arris."""
    cb, ct = (c if chamfer_edges[0] else 0.0), (c if chamfer_edges[1] else 0.0)
    pts = [(0.0, 0.0, groups[0], False)]
    if cb > 0:
        pts += [(0.0, h - cb, groups[1], True), (cb, h, groups[1], False)]
    else:
        pts += [(0.0, h, groups[1], False)]
    if ct > 0:
        pts += [(w - ct, h, groups[1], True), (w, h - ct, groups[2], False)]
    else:
        pts += [(w, h, groups[2], False)]
    pts += [(w, 0.0, groups[3] if back else groups[2], False)]
    if back:
        pts += [(0.0, 0.0, groups[3], False)]
    return pts


def data_profile(points_mm, scale_q=1.0):
    """A member's moulded section from a version's data: [p, q] millimetres, p across from its outer edge to the
    edge at the opening, q out from the wall (0), walked from one edge to the other; a point with a third value 1
    starts an arris edge (a worn round). The side edges are 'left' and 'right', the face 'front'. The far side of
    an opening sweeps the same section with p mirrored (P pointing back across)."""
    pts = [(p * MM, q * MM * scale_q, (bool(r[0]) if r else False)) for p, q, *r in points_mm]
    out = []
    for i, (p, q, a) in enumerate(pts):
        g = "left" if i == 0 else ("right" if i == len(pts) - 2 else "front")
        out.append((p, q, g, a))
    return out


def to_object(name, faces, place_of, deform, rects, page_size, colour_of):
    mesh = bpy.data.meshes.new(name)
    verts, polys, uv0, uv1, cols, rest, pieces = [], [], [], [], [], [], []
    for (pc, f) in faces:
        idx = []
        M = place_of(pc)
        for p in f.p:
            w = M @ p
            rest.append(tuple(w))
            verts.append(tuple(deform(pc, w)))
            idx.append(len(verts) - 1)
        polys.append(idx)
        rx, ry, rw, rh, d = rects[f.chart]
        for (u, v), (cu, cv) in zip(f.uv0, f.cuv):
            uv0.append((u, v))
            uv1.append(((rx + cu * d) / page_size, (ry + cv * d) / page_size))
        cols.append(colour_of(pc, f, [M @ p for p in f.p]))
        pieces.append(pc.index)
    mesh.from_pydata(verts, [], polys)
    mesh.update()
    l0 = mesh.uv_layers.new(name="uv0")
    l1 = mesh.uv_layers.new(name="page")
    l0.data.foreach_set("uv", [c for uv in uv0 for c in uv])
    l1.data.foreach_set("uv", [c for uv in uv1 for c in uv])
    ca = mesh.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    flat = []
    for poly, c in zip(mesh.polygons, cols):
        for k in range(poly.loop_total):
            flat += c[k] if isinstance(c[0], list) else c
    ca.data.foreach_set("color", flat)
    ra = mesh.attributes.new("rest", "FLOAT_VECTOR", "POINT")
    ra.data.foreach_set("vector", [c for r in rest for c in r])
    pa = mesh.attributes.new("piece", "INT", "FACE")
    pa.data.foreach_set("value", pieces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish_normals(obj)
    return obj


def finish_normals(obj):
    """Face-weighted normals: big faces stay flat, chamfers roll the light between them; a turn over 50 degrees is
    a hard edge."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0)
            e.smooth = a < math.radians(50)
        else:
            e.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.update()
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    mod = obj.modifiers.new("weighted", "WEIGHTED_NORMAL")
    mod.mode = "FACE_AREA"
    mod.weight = 100
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def tris_of(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)
