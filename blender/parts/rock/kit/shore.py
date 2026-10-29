"""The shore block: the tip's rock where the sea works it, a fitted part (kit.json `shore`) made from its causes.

    Blender -b --factory-startup --python-exit-code 1 -P blender/parts/rock/kit/tip.py -- --lone 1   (alone, in grey)

Its inputs are facts: its place (a record: the waterline's point, the sea's bearing, its width along the shore and
depth to the joint behind it, the ice's surface at its back and its lip), the tip's own (the foliation and joints and
the ice's way, from the fixture) and the sea's bands at its side's exposure. From them, in this order:
- the plan: the block's outline on its joints, cut by the foliation into ribs running toward the sea and each rib cut
  across by J1, most joints running on through the next rib with a jog, some stopping; every trace bent where it is
  long, so none is a ruled line. Each cell is one rigid piece of rock, its sides on the planes that bound it (leaning
  as they dip), a crack between it and its neighbours, wider where the sea washes;
- each piece's top, by its place: above the storm top, the ice's surface itself, so the cracked pieces still read as
  one ice-rounded back; under it, a tread the sea left when it stripped the sheet above, its seaward edge on the ice's
  surface and nearly level, so the shore steps down in ledges along the bands; on the lee, the side the ice ran toward,
  some pieces plucked out to a fresh face lower down. The ribs stand a little lower toward the lee, sliding down the
  foliation;
- the rounds by place: big where the swell washes a seaward edge (larger the lower), smaller on the ice's top and its
  stoss side, crisp on the lee and in plucked pockets, a chamfer on the cracks.
The pieces are separate closed islands of one mesh; none is bent, each only cut, set and rounded.
"""

import bisect
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import part as PT  # noqa: E402

Z = Vector((0.0, 0.0, 1.0))
BANDS = ("wet", "wash", "rock")


def bearing(b):
    r = math.radians(b)
    return Vector((math.sin(r), math.cos(r), 0.0))


class Ice:
    """The ice's surface over the block: z(x, v), x metres in from the back toward the lip, v across."""

    def __init__(self, rec, D):
        self.zb, self.g0, self.ka, self.D = rec["back"], rec["backSlope"], rec["across"], D
        self.k = max(0.0, (rec["back"] - rec["lip"] - rec["backSlope"] * D) / D ** 2)

    def z(self, x, v=0.0):
        return self.zb - self.g0 * x - self.k * x * x - self.ka * v * v


class Bad(Exception):
    """A draw whose cells fold or vanish; the next draw is taken."""


def cross2(a, b):
    return a.x * b.y - a.y * b.x


def rot2(p, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return Vector((c * p.x - s * p.y, s * p.x + c * p.y))


def meet2(n1, c1, n2, c2):
    """The 2D point with n1·p = c1 and n2·p = c2."""
    det = cross2(n1, n2)
    if abs(det) < 1e-6:
        raise Bad("parallel traces")
    return Vector(((c1 * n2.y - n1.y * c2) / det, (n1.x * c2 - c1 * n2.x) / det))


def area2(pts):
    return 0.5 * sum(cross2(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))


def simple(pts):
    """Whether a closed 2D polygon's edges cross nowhere but at their shared corners."""
    n = len(pts)
    for i in range(n):
        a0, a1 = pts[i], pts[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            b0, b1 = pts[j], pts[(j + 1) % n]
            d1, d2 = cross2(a1 - a0, b0 - a0), cross2(a1 - a0, b1 - a0)
            d3, d4 = cross2(b1 - b0, a0 - b0), cross2(b1 - b0, a1 - b0)
            if d1 * d2 < -1e-12 and d3 * d4 < -1e-12:
                return False
    return True


def skew(rng, r, k):
    """A draw in [r0, r1] leaning to r0 (power k): many small, few large."""
    return r[0] + (r[1] - r[0]) * rng.random() ** k


def frame(rec, fix):
    """The block's frame: s toward the sea, a across from the lee (the side the ice ran toward) to the stoss, and the
    foliation's upward normal."""
    s = bearing(rec["face"])
    a = bearing(rec["face"] + 90)
    if a.dot(bearing(fix["rock"]["ice"]["toward"])) > 0:
        a = -a
    fol = PT.families(fix)["foliation"]
    return s, a, PT.normal(fol["dip"], fol["dipToward"])


def plan(rec, S, fix, rng):
    """The block's plan in its own frame (x from the back toward the sea, v across from the lee): a 2D bmesh of its
    cells, and the traces' facts: (bm, sides, q, m, cuts, mains). `sides` are the outline's (name, plan normal, point, lean
    back: the lip's); q runs across the ribs toward the stoss, m across the J1 joints toward the sea; `cuts` are the partings'
    places along q, `mains` the main J1 joints' along m."""
    fam = PT.families(fix)
    W, D = rec["width"], rec["depth"]
    s, a, nf = frame(rec, fix)
    loc = lambda h: Vector((h.dot(s), h.dot(a)))  # noqa: E731
    hz = {n: Vector((v.x, v.y, 0.0)).normalized()
          for n, v in ((k, PT.normal(fam[k]["dip"], fam[k]["dipToward"])) for k in ("J1", "J2", "J3"))}

    def facing(d):
        h = max(hz.values(), key=lambda h: abs(h.dot(d)))
        return h if h.dot(d) > 0 else -h

    sides = []
    for name, d, p in (("lee", -a, (D / 2, -W / 2)), ("front", s, (D, 0)), ("stoss", a, (D / 2, W / 2)),
                       ("back", -s, (0, 0))):
        h = Matrix.Rotation(math.radians(rng.uniform(-S["sideTurn"], S["sideTurn"])), 3, Z) @ facing(d)
        t = rng.uniform(*S["lipLean"]) if name == "front" else 0.0
        sides.append((name, loc(h).normalized(), Vector(p), t))
    corners = []
    for i in range(4):
        (_, n1, p1, _), (_, n2, p2, _) = sides[i - 1], sides[i]
        corners.append(meet2(n1, n1.dot(p1), n2, n2.dot(p2)))
    if area2(corners) < 0:
        raise Bad("outline turned")

    bm = bmesh.new()
    bm.faces.new([bm.verts.new((p.x, p.y, 0.0)) for p in corners])

    def cut(faces, co, no):
        geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + list(faces)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=(co.x, co.y, 0.0), plane_no=(no.x, no.y, 0.0))

    # the foliation's partings, across q, ribs `leafM` wide (most thin)
    q = loc(Vector((nf.x, nf.y, 0.0)).normalized()).normalized()
    if q.y < 0:
        q = -q
    lo, hi = min(q.dot(c) for c in corners), max(q.dot(c) for c in corners)
    cuts, c = [], lo + skew(rng, S["leafM"], S["leafSkew"]) * rng.uniform(0.4, 1.0)
    while c < hi - S["leafM"][0] * 0.6:
        cuts.append(c)
        cut(list(bm.faces), q * c, q)
        c += skew(rng, S["leafM"], S["leafSkew"])
    rib = lambda f: bisect.bisect(cuts, q.dot(f.calc_center_median().xy))  # noqa: E731

    # J1 across each rib: the main joints run on through most ribs, jogging at each; some ribs take one between
    m = loc(hz["J1"])
    if m.x < 0:
        m = -m
    mlo, mhi = min(m.dot(c) for c in corners), max(m.dot(c) for c in corners)
    mains, c = [], mlo + rng.uniform(0.35, 1.0) * S["treadM"][1]
    while c < mhi - S["treadM"][0] * 0.5:
        mains.append(c)
        c += skew(rng, S["treadM"], 1.3)
    edges = [lo] + cuts + [hi]
    for r in range(len(cuts) + 1):
        qm = (edges[r] + edges[r + 1]) / 2
        at = []
        for k, c in enumerate(mains):
            if rng.random() < S["through"]:
                at.append(c + rng.uniform(-1, 1) * S["jogM"])
            nxt = mains[k + 1] if k + 1 < len(mains) else mhi
            if nxt - c > 2 * S["treadM"][0] and rng.random() < S["extra"]:
                at.append(rng.uniform(c + S["treadM"][0] * 0.8, nxt - S["treadM"][0] * 0.8))
        for c in at:
            n = rot2(m, rng.uniform(-S["riserTurn"], S["riserTurn"]))
            p = meet2(m, c, q, qm)
            cut([f for f in bm.faces if rib(f) == r], p, n)

    # cells too small or too thin join their longest neighbour
    for _ in range(200):
        bad = [f for f in bm.faces
               if f.calc_area() < S["minCell"] or 2 * f.calc_area() / f.calc_perimeter() < S["minWidthM"]]
        if not bad:
            break
        f = min(bad, key=lambda f: f.calc_area())
        shared = [e for e in f.edges if len(e.link_faces) == 2]
        if not shared:
            raise Bad("a lone sliver")
        bmesh.ops.dissolve_edges(bm, edges=[max(shared, key=lambda e: e.calc_length())], use_verts=False)
    else:
        raise Bad("slivers")

    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=S["mergeM"])
    # every trace bent where it is long, every inner corner moved a little: none a ruled line
    for e in list(bm.edges):
        L = e.calc_length()
        if L < S["bendM"]:
            continue
        outer = len(e.link_faces) < 2
        reach = min(2 * f.calc_area() / f.calc_perimeter() for f in e.link_faces)
        v0, v1 = e.verts
        p0, p1 = v0.co.xy.copy(), v1.co.xy.copy()
        nrm = Vector((-(p1 - p0).y, (p1 - p0).x)).normalized()
        ts = [rng.uniform(0.3, 0.7)] if L < 2.5 * S["bendM"] else [rng.uniform(0.25, 0.4), rng.uniform(0.6, 0.75)]
        last, t_last = v0, 0.0
        for t in ts:
            seg = bm.edges.get((last, v1))
            _, nv = bmesh.utils.edge_split(seg, last, (t - t_last) / (1 - t_last))
            off = rng.uniform(-1, 1) * min(S["bend"] * L * (0.4 if outer else 1.0), 0.3 * reach)
            nv.co.xy = p0 + (p1 - p0) * t + nrm * off
            last, t_last = nv, t
    for v in bm.verts:
        if all(len(e.link_faces) == 2 for e in v.link_edges):
            reach = min([2 * f.calc_area() / f.calc_perimeter() for f in v.link_faces] +
                        [e.calc_length() for e in v.link_edges])
            r, t = min(S["wiggleM"], 0.25 * reach) * math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
            v.co.xy += Vector((math.cos(t), math.sin(t))) * r
    for f in bm.faces:
        pts = [v.co.xy for v in f.verts]
        if not simple(pts) or abs(area2(pts)) < S["minCell"] * 0.5:
            raise Bad(f"a cell folded ({len(pts)} corners, {abs(area2(pts)):.3f} m², simple {simple(pts)})")
    return bm, sides, q, m, cuts, mains


def form(rec, S, fix, levels, rng):
    """The block's pieces in its own frame (the lip's waterline point at the origin, the site's bearings): a list of
    cells, each its columns (top, cut rows, foot, as 3D points), its top's kind and each top edge's round and pass,
    and info. `levels` is (exposure, wet, storm)."""
    W, D = rec["width"], rec["depth"]
    e, wet, storm = levels
    ice = Ice(rec, D)
    s, a, nf = frame(rec, fix)
    bm, sides, q, m, cuts, mains = plan(rec, S, fix, rng)
    wl = rec["lip"] * math.tan(math.radians(sides[1][3]))  # the lip's top stands back of the waterline

    def at(p, z):
        return s * (p.x - D - wl) + a * p.y + Z * z

    def side_of(ed):
        mid = (ed.verts[0].co.xy + ed.verts[1].co.xy) / 2
        return min(sides, key=lambda sd: abs(sd[1].dot(mid) - sd[1].dot(sd[2])))

    bm.faces.index_update()
    bm.edges.index_update()
    bm.verts.index_update()
    cells = list(bm.faces)
    rib_of = {f.index: bisect.bisect(cuts, q.dot(f.calc_center_median().xy)) for f in cells}
    R = len(cuts) + 1
    seaw = Vector((s.x, s.y, 0.0))

    # every piece is sheared down the foliation's dip (so its sides on the partings are the foliation itself, its
    # others near upright), its sea side leaning back where the swell wore it: each side one plane
    dfol = -(Z - nf * Z.dot(nf))
    dfol /= -dfol.z

    # the ribs slide down the foliation, each a little lower toward the lee
    slide = [0.0] * R
    for r in range(R - 2, -1, -1):
        slide[r] = slide[r + 1] + skew(rng, S["lee"]["stepM"], 2.0)

    def crack(ed):
        u = PT.HS.unit(PT.HS.h(rec["id"], "crack", ed.index))
        kind = "fol" if rib_of[ed.link_faces[0].index] != rib_of[ed.link_faces[1].index] else "joint"
        r = S["crackM"][kind]
        mid = (ed.verts[0].co.xy + ed.verts[1].co.xy) / 2
        wash = S["crackM"]["wash"] if ice.z(mid.x, mid.y) < storm else 1.0
        return (r[0] + (r[1] - r[0]) * u) * wash

    # each cell's top, by its place
    tops = {}
    front = sides[1]
    dips = [rng.uniform(*S["treadDip"]) for _ in range(len(mains) + 1)]
    for f in cells:
        r = rib_of[f.index]
        pts = [v.co.xy for v in f.verts]
        zs = [ice.z(p.x, p.y) for p in pts]
        if min(zs) > storm - 0.05:
            dz = slide[r] + skew(rng, S["capDrop"], 2.0)
            tops[f.index] = ("cap", lambda p, dz=dz: ice.z(p.x, p.y) - dz)
            continue
        # its ledge: the sheet between two main joints, its seaward edge on the ice's surface at the next main
        # joint (the lip's at the front), so the ledges run on along the shore across the ribs
        k = bisect.bisect(mains, m.dot(f.calc_center_median().xy))
        dz = slide[r] + skew(rng, S["washDrop"], 2.0)
        dip = math.tan(math.radians(dips[k]))

        def tread(p, k=k, dz=dz, dip=dip, r=r):
            if k < len(mains):
                t = mains[k] - m.dot(p)
            else:
                t = (front[1].dot(front[2]) - front[1].dot(p)) / max(front[1].dot(m), 0.2)
            e = p + m * t
            return min(ice.z(e.x, e.y) - dz + dip * t, ice.z(p.x, p.y) - slide[r])
        kind = "tread"
        lee = S["lee"]
        if r < len(lee["share"]) and rng.random() < lee["share"][r]:
            low = min(tread(p) for p in pts) - skew(rng, lee["depthM"], 1.6)
            gv = math.tan(math.radians(rng.uniform(*lee["dip"])))
            c = f.calc_center_median().xy
            tread = lambda p, low=low, gv=gv, c=c: max(S["floor"], low + gv * (p.y - c.y))  # noqa: E731
            kind = "pluck"
        tops[f.index] = (kind, tread)

    out = []
    for f in cells:
        kind, top = tops[f.index]
        vs = list(f.verts)
        if area2([v.co.xy for v in vs]) < 0:
            vs.reverse()
        n = len(vs)
        eds = [bm.edges.get((vs[k], vs[(k + 1) % n])) for k in range(n)]
        # the crack: each edge set in by half its crack (none on the outline)
        g = [crack(ed) / 2 if len(ed.link_faces) == 2 else 0.0 for ed in eds]
        pts = [v.co.xy for v in vs]
        for shrink in (1.0, 0.5, 0.25, 0.0):  # a cell too narrow for its cracks takes less of them
            ins = []
            for k in range(n):
                pa, pb, pc = pts[k - 1], pts[k], pts[(k + 1) % n]
                na = Vector((-(pb - pa).y, (pb - pa).x)).normalized()
                nb = Vector((-(pc - pb).y, (pc - pb).x)).normalized()
                ga, gb = g[k - 1] * shrink, g[k] * shrink
                if abs(cross2(na, nb)) < 0.05:
                    ins.append(pb + (na * ga + nb * gb) / 2)
                else:
                    ins.append(meet2(na, na.dot(pa) + ga, nb, nb.dot(pb) + gb))
            if simple(ins) and area2(ins) > S["minCell"] * 0.3 and \
                    all((ins[k] - pts[k]).length < 3 * max(g) + 1e-6 for k in range(n)):
                break
        else:
            raise Bad("a cell lost to its cracks")

        if kind == "pluck":
            run = dfol
        elif any(len(ed.link_faces) < 2 and side_of(ed)[0] == "front" for ed in eds):
            run = dfol + seaw * math.tan(math.radians(sides[1][3]))
        else:
            run = dfol + seaw * math.tan(math.radians(rng.uniform(*S["riserLean"])))
        zt = [top(ins[k]) for k in range(n)]

        def line(k, z):
            return at(ins[k], zt[k]) + run * (zt[k] - z)

        centre = sum(ins, Vector((0.0, 0.0))) / n
        inr = 2 * abs(area2(ins)) / sum((ins[(k + 1) % n] - ins[k]).length for k in range(n))

        # each top edge's round by where it stands and what faces it
        rounds = []
        for k in range(n):
            ed, pm = eds[k], (ins[k] + ins[(k + 1) % n]) / 2
            zm = (zt[k] + zt[(k + 1) % n]) / 2
            nrm = Vector(((ins[(k + 1) % n] - ins[k]).y, -(ins[(k + 1) % n] - ins[k]).x)).normalized()  # outward
            face3 = s * nrm.x + a * nrm.y
            if len(ed.link_faces) == 2:
                other = ed.link_faces[0] if ed.link_faces[1] is f else ed.link_faces[1]
                okind, otop = tops[other.index]
                h = zm - otop(pm)
            else:
                okind, h = "", (zm if side_of(ed)[0] == "front" else S["rowDropM"])
            u = PT.HS.unit(PT.HS.h(rec["id"], "round", f.index, k))
            lerp = lambda rr: rr[0] + (rr[1] - rr[0]) * u  # noqa: E731
            depth = min(1.0, max(0.0, (storm - zm) / max(storm - wet, 1e-6)))
            Rr = S["rounds"]
            if h < S["crackDropM"]:
                w, big = 0.0, False
            elif kind == "pluck" or okind == "pluck" or face3.dot(-a) > 0.6:
                w, big = lerp(Rr["crisp"]), False
            elif face3.dot(seaw) > 0.3 and zm < storm + 0.05:
                w, big = lerp(Rr["sea"]) * (0.3 + 0.7 * depth) * (0.5 + 0.5 * e), True
            elif kind == "cap" or face3.dot(a) > 0.6:
                w, big = lerp(Rr["ice"]), True
            else:
                w = lerp(Rr["joint"])
                big = w >= Rr["bigM"]
            w = min(w, Rr["dropShare"] * max(h, S["crackDropM"]), Rr["reachShare"] * inr)
            rounds.append((w, big, h))

        # the wall under each top edge cut at the bands' lines where they cross its bared face
        cutsh = []
        for k in range(n):
            w, _, h = rounds[k]
            ztop = min(zt[k], zt[(k + 1) % n])
            cutsh.append([b for b in (storm, wet) if max(ztop - h, 0.0) + 0.05 < b < ztop - w - 0.04])
        # its foot just under its lowest neighbour's top (the sea's at the lip): no deeper than it is seen
        low = min((zt[k] + zt[(k + 1) % n]) / 2 - rounds[k][2] for k in range(n))
        foot = max(S["base"], min(low, min(zt) - 0.1) - S["buryM"])
        cols = []
        for k in range(n):
            hs = sorted(set(cutsh[k - 1]) | set(cutsh[k]), reverse=True)
            cols.append([(zt[k], line(k, zt[k]))] + [(b, line(k, b)) for b in hs] + [(foot, line(k, foot))])
        cz = top(centre)
        out.append({"kind": kind, "cols": cols, "cuts": cutsh, "rounds": rounds,
                    "centre": at(centre, cz) if kind == "cap" else None})
    info = {"ribs": R, "cells": len(cells), "ledges": len(mains) + 1, "plucked": sum(t[0] == "pluck" for t in tops.values()),
            "cap": sum(t[0] == "cap" for t in tops.values()), "storm": storm, "wet": wet, "e": e}
    bm.free()
    return out, info


def assemble(cells):
    """The cells as one bmesh of closed islands, with each top edge's round in its pass: (bm, big, small)."""
    bm = bmesh.new()
    big, small = {}, {}
    for c in cells:
        cols = c["cols"]
        n = len(cols)
        vs = [[(z, bm.verts.new(p)) for z, p in col] for col in cols]
        tops = [col[0][1] for col in vs]
        if c["centre"] is not None:
            mid = bm.verts.new(c["centre"])
            for k in range(n):
                bm.faces.new((mid, tops[k], tops[(k + 1) % n]))
        else:
            bm.faces.new(tops)
        bm.faces.new([col[-1][1] for col in reversed(vs)])
        for k in range(n):
            L, Rc = vs[k], vs[(k + 1) % n]
            levels = [math.inf] + sorted(c["cuts"][k], reverse=True) + [-math.inf]
            for i in range(len(levels) - 1):
                hu, hl = levels[i], levels[i + 1]
                band = lambda col: [v for j, (z, v) in enumerate(col)  # noqa: E731
                                    if (j == 0 and hu == math.inf) or (j > 0 and hl - 1e-9 <= z <= hu + 1e-9)]
                bm.faces.new(band(L) + list(reversed(band(Rc))))
            w, isbig, _ = c["rounds"][k]
            ed = bm.edges.get((tops[k], tops[(k + 1) % n]))
            (big if isbig else small)[ed] = w
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    loose = [ed for ed in bm.edges if len(ed.link_faces) != 2]
    if loose:
        raise RuntimeError(f"[shore] {len(loose)} edges not shared by two faces")
    return bm, big, small


def level_object(name, bm, big, small, segments, mats, info):
    """The pieces rounded at a level's segments (the big rounds in full, the cracks' and crisp edges in one), split
    smooth from sharp by angle, their faces given the band's material their middle stands in (`mats`: wet, wash,
    rock)."""
    me = bpy.data.meshes.new(name + "-hull")
    bm.edges.index_update()
    bm.to_mesh(me)
    for m in mats:
        me.materials.append(m)
    lv = [info["wet"], info["storm"]]
    for p in me.polygons:
        p.material_index = sum(p.center.z >= h for h in lv)
    me.set_sharp_from_angle(angle=math.radians(35))
    passes = []
    for key, rr, segs in (("round_small", small, 1), ("round_big", big, segments)):
        wmax = max(list(rr.values()) + [1e-6])
        att = me.attributes.new(key, "FLOAT", "EDGE")
        vals = [0.0] * len(me.edges)
        for ed, w in rr.items():
            vals[ed.index] = w / wmax
        att.data.foreach_set("value", vals)
        passes.append((key, wmax, segs))
    ob = bpy.data.objects.new(name + "-hull", me)
    bpy.context.scene.collection.objects.link(ob)
    if segments:
        for key, wmax, segs in passes:
            mod = ob.modifiers.new(key, "BEVEL")
            mod.limit_method, mod.offset_type, mod.width = "WEIGHT", "OFFSET", wmax
            mod.edge_weight = key
            mod.segments, mod.profile = segs, 0.5
            mod.use_clamp_overlap = False
            mod.harden_normals = True
            mod.material = -1
    tri = ob.modifiers.new("tris", "TRIANGULATE")
    tri.keep_custom_normals = True
    dg = bpy.context.evaluated_depsgraph_get()
    out = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    out.name = name
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    res = bpy.data.objects.new(name, out)
    bpy.context.scene.collection.objects.link(res)
    return res


def row(rec, K, fix):
    """The block's record and, `row` a side, its neighbours along the shore across a joint `gapM` wide: the same
    making, their own seeds, their surface a little higher or lower (`rowVary`, metres at the back and the lip)."""
    out = [rec]
    a = bearing(rec["face"] + 90)
    rng = PT.HS.Stream(K["world"], "shore", rec["id"], "row")
    for side in (1, -1):
        for j in range(1, rec.get("row", 0) + 1):
            off = side * j * (rec["width"] + rec["gapM"])
            dv = [rng.uniform(-v, v) for v in rec["rowVary"]]
            out.append(dict(rec, id=f"{rec['id']}{'+' if side > 0 else '-'}{j}",
                            at=[rec["at"][0] + a.x * off, rec["at"][1] + a.y * off],
                            back=rec["back"] + dv[0], lip=rec["lip"] + dv[1], width=rec["width"] + rng.uniform(-0.5, 0.5)))
    return out


def drawn(rec, K, fix, levels):
    """The block's pieces from its first draw that holds: (cells, info, draw)."""
    for draw in range(40):
        try:
            cells, info = form(rec, K["shore"], fix, levels, PT.HS.Stream(K["world"], "shore", rec["id"], draw))
            return cells, info, draw
        except Bad as err:
            print(f"[shore] {rec['id']} draw {draw}: {err}")
    raise RuntimeError(f"[shore] {rec['id']}: no draw holds")


def build(name, rec, K, fix, levels, mats, segments):
    """The shore block for a place record `rec`, as an object `name` at its place (module doc)."""
    cells, info, draw = drawn(rec, K, fix, levels)
    bm, big, small = assemble(cells)
    ob = level_object(name, bm, big, small, segments, mats, info)
    bm.free()
    ob.location = (rec["at"][0], rec["at"][1], 0.0)
    tris = len(ob.data.polygons)
    wb, ws = sorted(big.values()), sorted(small.values())
    print(f"[shore] {rec['id']} (draw {draw}): {info['cells']} pieces in {info['ribs']} ribs, {info['ledges']} ledges "
          f"({info['cap']} cap, "
          f"{info['plucked']} plucked), exposure {info['e']:.2f}, wet {info['wet']:.2f}, storm {info['storm']:.2f}; "
          f"{tris} triangles at {segments} segments; rounds {len(wb)} big {wb[0] if wb else 0:.3f}-"
          f"{wb[-1] if wb else 0:.3f} m, {len(ws)} small")
    return ob
