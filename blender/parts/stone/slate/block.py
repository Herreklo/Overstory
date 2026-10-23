"""Rigid blocks cut by planes: the machinery the stone part functions build with (port step 2b, R2a; the design's SN1,
SN4 and SN8: reviews/lt1/port/2b/design.md; the contract: reviews/lt1/port/2b/r2a/stones/plan.md).

A stone is a rigid convex block, the intersection of half-spaces, made in its own frame from facts: its beds and
faces, a split face's facets (convex folds, so the block stays convex), chips (planar cuts at the corners of the mass)
and, at L0, a chamfer on every exposed arris. Its wear, a height field from wear.py's laws, is subtracted from it: the
block is cut by the field's triangles, column by column, and nothing else moves a vertex. Faces no one sees (beds,
backs, ends in a wall) are not drawn. A drawn face that ends at a hidden one runs on past it by a skirt, so a
neighbour's joint, fill or wear never opens a gap; a cover (a neighbour standing over a face) trims what is drawn the
same way. What is drawn is merged face by face, made conforming (no T-junctions: every vertex on an edge is a corner of
the triangles on both sides), rid of edges shorter than two pixels wherever the faces about them lie flat within a
planarity tolerance, thinned of corners that only lie straight along an edge, and triangulated for size on screen
(SN8's thin-triangle gate): each face cut exactly so it has the fewest triangles under size, and of those cuts the
one whose triangles are least thin (tri_cost).

Numpy only. Lengths in metres; x, y, z the stone's own frame, z up. A plane is n . p <= d inside, n its outward normal.

    planes = [plane("top", (0, 0, 1), d=H, kind=0), plane("bed", (0, 0, -1), d=0, role="hidden", skirt=0.02), ...]
    faces = polyhedron(planes)                    # the convex block's faces
    planes += [p for p, _sag, _ang in chamfers(planes, leg, 160)]     # L0: a chamfer on every exposed arris
    surf = cut(planes, field=grid, regions=...)   # the drawn surface: merged loops per face
    surf, moves = collapse(surf, size, tol, keep, bounds)     # no edge shorter than size where faces lie flat
    mesh = triangulate(thin_out(surf, size), size)    # welded vertices, triangles, each its face and plane
"""

import math

import numpy as np

TOL = 1e-9          # a point this near a plane (m) lies on it
SLIVER = 0.01       # best_triangles: a triangle's (size / altitude)^2 weighs this much against its being thin at all
WELD = 1e-7         # two vertices this near (m) are one
TINY = 1e-10        # a polygon of less area (m2) is none
BIG = 10.0          # the half size (m) of the square a face is clipped from


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def plane(name, n, d=None, point=None, role="exposed", face=None, **info):
    """A half-space n . p <= d. role: exposed (drawn), hidden (not drawn; its skirt, m, moves it out for the drawn
    faces that end on it), cover (not part of the block: a neighbour over the faces, which are drawn only to its
    skirt past it), wall and field (the wear's prisms and its triangles' planes). face: the face it belongs to
    (a split face's facets share one; the wear's triangles are the top's)."""
    n = unit(n)
    d = float(n @ np.asarray(point, float)) if point is not None else float(d)
    p = dict(name=name, n=n, d=d, role=role, face=face or name, skirt=0.0)
    p.update(info)
    return p


def basis(n):
    """Two unit vectors in the plane of n, (e1, e2, n) right-handed."""
    a = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = unit(np.cross(a, n))
    return e1, np.cross(n, e1)


def area(poly, n):
    """A planar polygon's signed area about n (positive counter-clockwise seen from n's side)."""
    if len(poly) < 3:
        return 0.0
    c = np.cross(poly, np.roll(poly, -1, axis=0)).sum(axis=0)
    return 0.5 * float(c @ n)


def _clean(poly):
    """Consecutive points within WELD made one."""
    if len(poly) == 0:
        return poly
    out = [poly[0]]
    for p in poly[1:]:
        if np.linalg.norm(p - out[-1]) > WELD:
            out.append(p)
    if len(out) > 1 and np.linalg.norm(out[0] - out[-1]) <= WELD:
        out.pop()
    return np.array(out) if len(out) >= 3 else np.zeros((0, 3))


def clip(poly, n, d):
    """The part of a convex polygon (k x 3) with n . p <= d (Sutherland and Hodgman); points within TOL of the plane
    count as inside."""
    if len(poly) == 0:
        return poly
    s = poly @ n - d
    if (s <= TOL).all():
        return poly
    if (s > -TOL).all() and not (s <= TOL).any():
        return np.zeros((0, 3))
    out = []
    k = len(poly)
    for i in range(k):
        j = (i + 1) % k
        if s[i] <= TOL:
            out.append(poly[i])
        if (s[i] < -TOL and s[j] > TOL) or (s[i] > TOL and s[j] < -TOL):
            t = s[i] / (s[i] - s[j])
            out.append(poly[i] + t * (poly[j] - poly[i]))
    return _clean(np.array(out)) if out else np.zeros((0, 3))


def same_plane(p, q):
    return np.abs(p["n"] - q["n"]).max() < 1e-12 and abs(p["d"] - q["d"]) < TOL


def dedupe(planes):
    """The planes with any that repeats an earlier one dropped (earlier planes win: pass the block's first)."""
    keep = []
    for p in planes:
        if not any(same_plane(p, q) for q in keep):
            keep.append(p)
    return keep


def face_polygon(p, others):
    """The polygon of plane p inside every other half-space, counter-clockwise about p's normal."""
    e1, e2 = basis(p["n"])
    c = p["n"] * p["d"]
    poly = np.array([c + BIG * (a * e1 + b * e2) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for q in others:
        if q is p:
            continue
        poly = clip(poly, q["n"], q["d"])
        if len(poly) == 0:
            break
    if len(poly) and area(poly, p["n"]) < TINY:
        return np.zeros((0, 3))
    return poly


def offset(p, by):
    q = dict(p)
    q["d"] = p["d"] + by
    return q


def polyhedron(planes, skirts=False):
    """The convex block's faces: [(plane, polygon)] for every plane that bounds it. With skirts, each hidden plane and
    cover is first moved out by its skirt (the drawn faces run on past it)."""
    ps = dedupe([offset(p, p.get("skirt", 0.0)) if skirts and p["role"] in ("hidden", "cover") else p
                 for p in planes])
    out = []
    for p in ps:
        poly = face_polygon(p, ps)
        if len(poly):
            out.append((p, poly))
    return out


# -- arrises and chamfers -------------------------------------------------------------------------------------------

def shared_edges(faces):
    """{(i, j): (a, b)}: the edge two faces of a convex block share (i < j index faces), as its two end points."""
    out = {}
    for i, (pi, poly) in enumerate(faces):
        for j, (pj, _) in enumerate(faces):
            if j <= i:
                continue
            on = [q for q in poly if abs(q @ pj["n"] - pj["d"]) <= 10 * TOL]
            pts = []
            for q in on:
                if not any(np.linalg.norm(q - r) <= WELD for r in pts):
                    pts.append(q)
            if len(pts) >= 2:
                # the two farthest apart (a convex face meets another along one segment)
                best = max(((a, b) for a in pts for b in pts), key=lambda ab: np.linalg.norm(ab[0] - ab[1]))
                if np.linalg.norm(best[0] - best[1]) > WELD:
                    out[(i, j)] = best
    return out


def dihedral(pa, pb):
    """The interior angle (degrees) between two faces of a convex block with outward normals na and nb."""
    c = float(np.clip(pa["n"] @ pb["n"], -1.0, 1.0))
    return 180.0 - math.degrees(math.acos(c))


def chamfer_plane(fa, fb, edge, leg, through=None):
    """The chamfer on the arris two faces fa and fb share (each (plane, polygon)): a plane through the points set back
    leg (m) on each face, square to the arris (symmetric: the same leg on both, as a mason or a machinist gives a
    chamfer, C10 a 10 mm leg), so its face is 2 leg sin(theta / 2) across for an interior angle theta. With through, a
    point, the same plane moved to pass through it (chamfers' chain: its leg is then what that makes it). Returns
    (plane, sagitta): the arris's distance from the plane, leg cos(theta / 2), L1's error where L0 chamfers it."""
    (pa, polya), (pb, polyb) = fa, fb
    q0, q1 = edge
    e = unit(q1 - q0)
    ua = unit(np.cross(e, pa["n"]))
    if (polya.mean(axis=0) - q0) @ ua < 0:
        ua = -ua
    ub = unit(np.cross(e, pb["n"]))
    if (polyb.mean(axis=0) - q0) @ ub < 0:
        ub = -ub
    n = unit(pa["n"] + pb["n"])
    if through is not None:
        d = float(n @ through)
        leg = (d - float(n @ q0)) / float(n @ ua)
    d = float(n @ (q0 + leg * ua))
    assert abs(float(n @ (q0 + leg * ub)) - d) < 1e-9, "a chamfer not symmetric"
    sag = float(n @ q0) - d
    assert sag > 0, "a chamfer that cuts nothing"
    name = "ch:" + "|".join(sorted((pa["face"], pb["face"])))
    if pa["name"] != pa["face"] or pb["name"] != pb["face"]:          # (a facet's own arris: its own chamfer)
        name += ":" + "|".join(sorted((pa["name"], pb["name"])))
    p = plane(name, n, d=d, role="exposed", face=name, kind=1, chamfer=tuple(sorted((pa["face"], pb["face"]))),
              leg=leg, sagitta=sag, between=(pa["name"], pb["name"]), arris=(q0.copy(), q1.copy()),
              angle=dihedral(pa, pb), inward=(ua, ub))
    return p, sag


def arrises(faces, arris_max_deg):
    """The block's exposed arrises: [(i, j, edge, angle)] where two exposed faces meet at an interior angle of at most
    arris_max_deg (flatter folds, a split face's own, are not arrises)."""
    out = []
    for (i, j), edge in sorted(shared_edges(faces).items()):
        pa, pb = faces[i][0], faces[j][0]
        if pa["role"] != "exposed" or pb["role"] != "exposed" or pa["face"] == pb["face"]:
            continue
        ang = dihedral(pa, pb)
        if ang <= arris_max_deg:
            out.append((i, j, edge, ang))
    return out


def _meet(planes):
    """The point three planes share."""
    A = np.array([p["n"] for p in planes])
    return np.linalg.solve(A, np.array([p["d"] for p in planes]))


def chamfers(planes, leg, arris_max_deg, pairs=None, start=None):
    """L0's chamfers (SN4): one plane on every exposed arris of the convex block the planes bound, leg (m) along each
    face. An arris a facet's ridge breaks (the riser folding back below a lamina, under an end that does not) is one
    chamfer band, as a mason runs it: its top piece has the leg, and each piece below is set through the point where
    the band's edge above crosses the ridge on the face that folds there, so the edge runs on unbroken. (Each at its
    own leg would cross the ridge a fraction of a mm apart and leave a piece that thin; the legs below differ from
    the stone's by the fold's turn, a few hundredths of a mm, reported as legDriftMm.)

    pairs: None (every arris, by its faces' names in order), or the face pairs (sorted name tuples) to chamfer, in the
    order given: an arris of any other pair stays square (a wall stone's arrises that run back into the wall, inside
    its joints). start: None, or start(pair, made), called before each pair's first piece with the chamfers made so
    far, returning None or a point the piece is set through instead of its leg (where a chamfer must meet another one
    and a square arris at one point, so no cap a fraction of a mm across is left between them). Returns
    [(plane, sagitta, angle)]."""
    faces = polyhedron([p for p in planes if p["role"] in ("exposed", "hidden")])
    by_pair = {}
    for i, j, edge, ang in arrises(faces, arris_max_deg):
        key = tuple(sorted((faces[i][0]["face"], faces[j][0]["face"])))
        by_pair.setdefault(key, []).append((i, j, edge, ang))
    out = []
    for key in (sorted(by_pair) if pairs is None else [tuple(sorted(k)) for k in pairs if tuple(sorted(k)) in by_pair]):
        pieces = by_pair[key]
        # the chain from its top: the piece with the highest end, then each that shares an end with the last
        left = sorted(pieces, key=lambda t: -max(t[2][0][2], t[2][1][2]))
        chain = [left.pop(0)]
        while left:
            _i, _j, (a0, a1), _ang = chain[-1]
            nxt = next((k for k, t in enumerate(left) if any(np.linalg.norm(u - w) <= 10 * WELD
                                                            for u in t[2] for w in (a0, a1))), None)
            chain.append(left.pop(0 if nxt is None else nxt))
        prev = None
        for i, j, edge, ang in chain:
            through = None
            if prev is None and start is not None:
                through = start(key, out)
            if prev is not None:
                (pi, pj, ppl, pedge) = prev
                old = {faces[pi][0]["face"]: faces[pi][0], faces[pj][0]["face"]: faces[pj][0]}
                new = {faces[i][0]["face"]: faces[i][0], faces[j][0]["face"]: faces[j][0]}
                folded = [f for f in new if new[f]["name"] != old[f]["name"]]
                shared = any(np.linalg.norm(u - w) <= 10 * WELD for u in edge for w in pedge)
                if len(folded) == 1 and shared:
                    f = folded[0]
                    through = _meet([ppl, old[f], new[f]])
            p, sag = chamfer_plane(faces[i], faces[j], edge, leg, through=through)
            p["legDrift"] = p["leg"] - leg
            out.append((p, sag, ang))
            prev = (i, j, p, edge)
    return out


# -- the wear: a height field subtracted -----------------------------------------------------------------------------

def _triangulations(n):
    """Every triangulation of a convex n-gon's corners 0..n-1, as lists of (i, j, k): the edge (0, n - 1) lies in one
    triangle (0, k, n - 1), and each side of it is cut the same way."""
    def tri(idx):
        if len(idx) < 3:
            return [[]]
        out = []
        a, b = idx[0], idx[-1]
        for m in range(1, len(idx) - 1):
            for left in tri(idx[:m + 1]):
                for right in tri(idx[m:]):
                    out.append(left + [(a, idx[m], b)] + right)
        return out
    return tri(list(range(n)))


def _ccw2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 1e-15


def grid_triangles(xs, ys, depth, top, centre_depth=None, fit=0.0, choose=None, nodes=None, between=None):
    """The wear field's triangles over a grid (xs across, ys back, depth[j, i] the worn depth in m at (xs[i], ys[j])).
    nodes: None, or (X, Y), each node's place in plan where it is not the grid's (a node moved onto a chamfer's edge),
    X[j, i] and Y[j, i]. between: None, or {(j, i): (x, y, depth)}, a node on row j between columns i and i + 1 (where
    the nosing's chamfer runs out between two of the row's nodes), a corner of the cells either side of that edge.

    Each cell is split along one of its diagonals: the one that better fits the field at its centre (centre_depth(x,
    y)), unless both fit within fit (m) and choose (given the splits, each a list of (plan, lifted) triangles) prefers
    the other. A cell with a node between is cut by whichever of its polygon's triangulations (every triangle counter-
    clockwise) fits the field best at its triangles' centres, or as choose prefers among those within fit. Returns
    [(plan triangle 3 x 2 counter-clockwise, lifted 3 x 3)]."""
    if nodes is None:
        X, Y = np.meshgrid(np.asarray(xs, float), np.asarray(ys, float))
    else:
        X, Y = nodes
    between = between or {}
    out = []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            P = {(a, b): np.array([X[j + b, i + a], Y[j + b, i + a], top - depth[j + b, i + a]])
                 for a in (0, 1) for b in (0, 1)}
            if (j, i) in between or (j + 1, i) in between:
                poly = [P[0, 0]]
                if (j, i) in between:
                    x, y, d = between[(j, i)]
                    poly.append(np.array([x, y, top - d]))
                poly += [P[1, 0], P[1, 1]]
                if (j + 1, i) in between:
                    x, y, d = between[(j + 1, i)]
                    poly.append(np.array([x, y, top - d]))
                poly.append(P[0, 1])
                cands = []
                for tris in _triangulations(len(poly)):
                    sp = [(poly[a], poly[b], poly[c]) for a, b, c in tris]
                    if not all(_ccw2(a, b, c) for a, b, c in sp):
                        continue
                    sp = [(np.array([a[:2], b[:2], c[:2]]), np.array([a, b, c])) for a, b, c in sp]
                    err = 0.0
                    if centre_depth is not None:
                        for _p2, lifted in sp:
                            c3 = lifted.mean(axis=0)
                            err = max(err, abs((top - c3[2]) - centre_depth(c3[0], c3[1])))
                    cands.append((err, sp))
                if not cands:
                    raise ValueError(f"a field cell with a node between cannot be cut ({j}, {i})")
                best = min(range(len(cands)), key=lambda k: (cands[k][0], k))
                ok = [k for k in range(len(cands)) if cands[k][0] <= fit]
                if choose is not None and len(ok) > 1:
                    best = ok[choose([cands[k][1] for k in ok])]
                out += cands[best][1]
                continue
            splits = [[(P[0, 0], P[1, 0], P[1, 1]), (P[0, 0], P[1, 1], P[0, 1])],
                      [(P[0, 0], P[1, 0], P[0, 1]), (P[1, 0], P[1, 1], P[0, 1])]]
            splits = [[(np.array([a[:2], b[:2], c[:2]]), np.array([a, b, c])) for a, b, c in sp] for sp in splits]
            use = 0
            if centre_depth is not None:
                cx, cy = 0.5 * (xs[i] + xs[i + 1]), 0.5 * (ys[j] + ys[j + 1])
                want = centre_depth(cx, cy)
                err = [abs(0.5 * (depth[j, i] + depth[j + 1, i + 1]) - want),
                       abs(0.5 * (depth[j + 1, i] + depth[j, i + 1]) - want)]
                use = 0 if err[0] <= err[1] + 1e-15 else 1
                if choose is not None and max(err) <= fit:
                    use = choose(splits)
            out += splits[use]
    return out


def piece_cost(planes, tris, size, field_face="top"):
    """What a cell's split costs where it is drawn: for each of its field triangles, the worn top that is left of it on
    the block (as cut makes it) and the best cut of that polygon (best_triangles' sum at size). A diagonal that meets
    a chamfer or a chip close to another corner leaves a short edge there and costs its thin triangles. (Only the
    field's faces count: the block's own faces split by a cell's walls merge again, but the top's do not.)"""
    block = dedupe([offset(p, p.get("skirt", 0.0)) if p["role"] in ("hidden", "cover") else p for p in planes])
    total = 0.0
    for tri2, lifted in tris:
        ps = dedupe(block + [field_plane(lifted, field_face)] + prism(tri2))
        if empty(ps):
            continue
        for p in ps:
            if p["role"] != "field":
                continue
            poly = face_polygon(p, ps)
            if len(poly) < 3 or area(poly, p["n"]) <= 1e-12:
                continue
            e1, e2 = basis(p["n"])
            try:
                total += best_triangles(np.stack([poly @ e1, poly @ e2], -1), size)[1]
            except ValueError:
                total += 1e9
    return total


def prism(tri2):
    """The three vertical half-spaces over a plan triangle (counter-clockwise)."""
    out = []
    for k in range(3):
        p, q = tri2[k], tri2[(k + 1) % 3]
        n = np.array([q[1] - p[1], -(q[0] - p[0]), 0.0])
        out.append(plane("wall", n, point=[p[0], p[1], 0.0], role="wall"))
    return out


def field_plane(lifted, face):
    a, b, c = lifted
    n = np.cross(b - a, c - a)
    assert n[2] > 0, "a field triangle not counter-clockwise"
    return plane("field", n, point=a, role="field", face=face, kind=0)


# -- the drawn surface -----------------------------------------------------------------------------------------------

class Welder:
    """One vertex for every point within WELD (a hash of cells, neighbours searched)."""

    def __init__(self):
        self.pts = []
        self.cells = {}

    def key(self, p):
        return tuple(int(math.floor(v / (10 * WELD))) for v in p)

    def add(self, p):
        k = self.key(p)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for i in self.cells.get((k[0] + dx, k[1] + dy, k[2] + dz), ()):
                        if np.linalg.norm(self.pts[i] - p) <= WELD:
                            return i
        self.pts.append(np.array(p, float))
        self.cells.setdefault(k, []).append(len(self.pts) - 1)
        return len(self.pts) - 1

    def array(self):
        return np.array(self.pts) if self.pts else np.zeros((0, 3))


def _on_segment(P, a, b, ids):
    """The ids of points strictly inside segment ab (within WELD of it), sorted along it."""
    A, B = P[a], P[b]
    d = B - A
    L2 = float(d @ d)
    if L2 <= WELD * WELD or not len(ids):
        return []
    Q = P[ids]
    t = (Q - A) @ d / L2
    off = np.linalg.norm(Q - (A + t[:, None] * d), axis=1)
    keep = (t > 1e-9) & (t < 1 - 1e-9) & (off <= WELD) & (np.asarray(ids) != a) & (np.asarray(ids) != b)
    sel = np.asarray(ids)[keep]
    return [int(i) for i in sel[np.argsort(t[keep])]]


def merge_loops(polys, W):
    """Polygons that tile one planar region (pieces of one face on one plane) merged into its boundary loops, as
    vertex ids: shared edges cancel, an edge split by another piece's vertex is split to match."""
    idl = []
    for poly in polys:
        ids = [W.add(p) for p in poly]
        ids = [v for k, v in enumerate(ids) if v != ids[k - 1]]
        if len(ids) >= 3:
            idl.append(ids)
    P = W.array()
    allv = sorted({v for ids in idl for v in ids})
    edges = {}
    for ids in idl:
        for k in range(len(ids)):
            a, b = ids[k], ids[(k + 1) % len(ids)]
            chain = [a] + _on_segment(P, a, b, allv) + [b]
            for u, v in zip(chain, chain[1:]):
                edges[(u, v)] = edges.get((u, v), 0) + 1
    left = {}
    for (u, v), c in edges.items():
        back = edges.get((v, u), 0)
        for _ in range(c - min(c, back)):
            left.setdefault(u, []).append(v)
    loops = []
    while left:
        start = min(left)
        loop = [start]
        cur = start
        while True:
            nxt = left[cur].pop(0)
            if not left[cur]:
                del left[cur]
            if nxt == start:
                break
            loop.append(nxt)
            cur = nxt
            assert cur in left, "a face's boundary does not close"
        loops.append(loop)
    return loops


def empty(ps):
    """A piece with no inside: two of its half-spaces face each other on one plane (a prism wall on a block's face, the
    cell beyond it), so its faces have area but it has no volume, and drawing them would draw a face twice."""
    for i, p in enumerate(ps):
        for q in ps[i + 1:]:
            if np.abs(p["n"] + q["n"]).max() < 1e-12 and p["d"] + q["d"] <= TOL:
                return True
    return False


def cut(planes, field=None, regions=None, field_face="top", keep=None):
    """The block's drawn surface. planes: the convex block (exposed, hidden with skirts, covers). field: None, or the
    wear's triangles (grid_triangles) cutting the block from above, the top's face. regions: {face: [[half-spaces],
    ...]}, disjoint convex regions whose union is where a face is seen (a joint end above its fill, say); a face
    without one is seen wherever it is.

    keep: None, or a test keep(point, faces) of a vertex and the names of the faces holding it: a vertex it passes
    stays a corner of every loop that holds it even where it lies straight between its neighbours (a structure
    line's on the field, so the field keeps its quads and never fans).

    Returns dict(W, groups): W the welder (every vertex), groups [(face, plane, loops)], loops lists of vertex ids,
    counter-clockwise about the plane's normal."""
    block = dedupe([offset(p, p.get("skirt", 0.0)) if p["role"] in ("hidden", "cover") else p for p in planes])
    pieces = []
    if field is None:
        pieces.append(block)
    else:
        for tri2, lifted in field:
            fp = field_plane(lifted, field_face)
            pieces.append(dedupe(block + [fp] + prism(tri2)))
    W = Welder()
    raw = []            # (face, plane, polygon)
    for ps in pieces:
        if empty(ps):
            continue
        for p in ps:
            if p["role"] not in ("exposed", "field"):
                continue
            poly = face_polygon(p, ps)
            if not len(poly):
                continue
            regs = (regions or {}).get(p["face"])
            parts = [poly]
            if regs:
                parts = []
                for reg in regs:
                    q = poly
                    for h in reg:
                        q = clip(q, h["n"], h["d"])
                        if not len(q):
                            break
                    if len(q) and area(q, p["n"]) >= TINY:
                        parts.append(q)
            for q in parts:
                raw.append((p, q))
    # group by face and plane: the wear's triangles on one plane (the flat top) merge into one
    groups = []
    for p, q in raw:
        for g in groups:
            if g[0]["face"] == p["face"] and same_plane(g[0], p):
                g[1].append(q)
                break
        else:
            groups.append((p, [q]))
    for _, polys in groups:          # every corner welded first, so a piece's edge splits where another's vertex is
        for poly in polys:
            for v in poly:
                W.add(v)
    out = []
    for p, polys in groups:
        for loop in merge_loops(polys, W):
            out.append((p["face"], p, loop))
    return dict(W=W, groups=conform(simplify(out, W, keep), W))


def _straight(P, a, v, b):
    """v lies inside the segment ab (within WELD of it)."""
    A, Bp, Q = P[a], P[b], P[v]
    d = Bp - A
    L2 = float(d @ d)
    if L2 <= WELD * WELD:
        return False
    t = float((Q - A) @ d) / L2
    return 0.0 < t < 1.0 and float(np.linalg.norm(Q - (A + t * d))) <= WELD


def simplify(groups, W, keep=None):
    """A vertex that lies straight between its neighbours in every loop that holds it is no corner of anything (a
    piece's corner the merge left on a straight edge, where the field's triangles either side lie in one plane): it
    leaves every loop, unless keep(point, faces) holds it (faces: the names of the faces whose loops hold it)."""
    P = W.array()
    loops = [list(loop) for _f, _p, loop in groups]
    names = [f for f, _p, _l in groups]
    while True:
        holders = {}
        for li, loop in enumerate(loops):
            for k, v in enumerate(loop):
                holders.setdefault(v, []).append((li, k))
        drop = set()
        for v, hs in holders.items():
            if keep is not None and keep(P[v], {names[li] for li, _k in hs}):
                continue
            if len({li for li, _k in hs}) != len(hs):
                continue
            if all(len(loops[li]) > 3 and _straight(P, loops[li][k - 1], v, loops[li][(k + 1) % len(loops[li])])
                   for li, k in hs):
                drop.add(v)
        if not drop:
            break
        new = [[v for v in loop if v not in drop] for loop in loops]
        if any(len(loop) < 3 for loop in new):
            break
        loops = new
    return [(f, p, loop) for (f, p, _l), loop in zip(groups, loops)]


def conform(groups, W):
    """No T-junctions: every vertex of a loop that lies inside another loop's edge (another face's corner on a shared
    edge) becomes a corner of that loop too."""
    P = W.array()
    allv = sorted({v for _f, _p, loop in groups for v in loop})
    out = []
    for face, p, loop in groups:
        new = []
        for k in range(len(loop)):
            a, b = loop[k], loop[(k + 1) % len(loop)]
            new.append(a)
            new.extend(_on_segment(P, a, b, allv))
        out.append((face, p, new))
    return out


def collapse(surf, short, tol, keep=None, bounds=()):
    """Edges shorter than short (m) made one point wherever that bends no face by more than tol (m): one end moves
    onto the other in every loop that holds it. Two of the field's lines meeting a chamfer's edge just apart (a row
    and a cell's diagonal from one node outside it), or a cut crossing an arris near a corner, leave such an edge, and
    every triangle at it is a sliver; where the faces around it lie nearly in one plane, the end that moves stays on
    all of them within tol and the sliver goes. A move is refused if it would bend a face past tol, take a vertex off
    a bound it lies on (bounds: (n, d) of the hidden planes, covers and seen regions, where the drawn surface may end
    open), make a loop not simple or not counter-clockwise, hold a vertex twice, or put a vertex inside an edge; a
    vertex keep(point, faces) holds never moves. Shortest first, then by vertex ids, pass after pass: deterministic.
    Returns (surf, moves): moves [(from, to, length m, bend m)]."""
    W, groups = surf["W"], surf["groups"]
    P = W.array()
    loops = [list(loop) for _f, _p, loop in groups]
    planes = [p for _f, p, _l in groups]
    names = [f for f, _p, _l in groups]
    bounds = [(np.asarray(n, float), float(d)) for n, d in bounds]
    moves = []

    def on_bounds(q):
        return [k for k, (n, d) in enumerate(bounds) if abs(float(q @ n) - d) < 1e-7]

    def simple(loop, p):
        e1, e2 = basis(p["n"])
        P3 = P[loop]
        if area(P3, p["n"]) <= 0:
            return False
        try:
            best_triangles(np.stack([P3 @ e1, P3 @ e2], -1), 1.0)
        except ValueError:
            return False
        return True

    while True:
        holders = {}
        for li, loop in enumerate(loops):
            for v in loop:
                holders.setdefault(v, set()).add(li)
        edges = set()
        for loop in loops:
            for k in range(len(loop)):
                a, b = loop[k], loop[(k + 1) % len(loop)]
                edges.add((min(a, b), max(a, b)))
        cand = sorted((float(np.linalg.norm(P[a] - P[b])), a, b) for a, b in edges)
        allv = sorted(holders)
        done = False
        for length, a, b in cand:
            if length >= short:
                break
            options = []
            for u, v in ((a, b), (b, a)):
                if keep is not None and keep(P[u], {names[li] for li in holders[u]}):
                    continue
                if any(abs(float(P[v] @ bounds[k][0]) - bounds[k][1]) >= 1e-7 for k in on_bounds(P[u])):
                    continue
                new, bend, ok = {}, 0.0, True
                for li in sorted(holders[u]):
                    loop = loops[li]
                    n = len(loop)
                    k = loop.index(u)
                    if v in loop:
                        if loop[(k + 1) % n] != v and loop[k - 1] != v:
                            ok = False
                            break
                        nl = [w for w in loop if w != u]
                    else:
                        e = abs(float(P[v] @ planes[li]["n"]) - planes[li]["d"])
                        bend = max(bend, e)
                        if e > tol:
                            ok = False
                            break
                        nl = [v if w == u else w for w in loop]
                    if len(nl) >= 3 and not simple(nl, planes[li]):
                        ok = False
                        break
                    new[li] = nl
                if not ok:
                    continue
                # no vertex inside an edge the move makes
                for li, nl in new.items():
                    if len(nl) < 3:
                        continue
                    k = nl.index(v)
                    for w in (nl[k - 1], nl[(k + 1) % len(nl)]):
                        if _on_segment(P, v, w, allv):
                            ok = False
                if ok:
                    options.append((bend, len(holders[u]), u, v, new))
            if not options:
                continue
            bend, _h, u, v, new = min(options, key=lambda t: (t[0], t[1], t[2]))
            for li, nl in new.items():
                loops[li] = nl
            moves.append((int(u), int(v), length, bend))
            done = True
            break
        if not done:
            break
    keep_groups = [(f, p, loop) for (f, p, _l), loop in zip(groups, loops) if len(loop) >= 3]
    return dict(W=W, groups=keep_groups), moves


# -- triangulation for size on screen --------------------------------------------------------------------------------

def _alt(a, b, c):
    """A triangle's smallest altitude (twice its area over its longest side), any dimension."""
    ab, ac, bc = b - a, c - a, c - b
    if len(a) == 2:
        A2 = abs(ab[0] * ac[1] - ab[1] * ac[0])
    else:
        A2 = float(np.linalg.norm(np.cross(ab, ac)))
    L = max(np.linalg.norm(ab), np.linalg.norm(ac), np.linalg.norm(bc))
    return A2 / L if L > 0 else 0.0


def _cross2(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _cross2v(o, a, b):
    """_cross2 over arrays (the last axis x, y), each product in the same order, so the same numbers."""
    return (a[..., 0] - o[..., 0]) * (b[..., 1] - o[..., 1]) - (a[..., 1] - o[..., 1]) * (b[..., 0] - o[..., 0])


def _inside_v(P2, Q):
    """Each point of Q strictly inside the simple polygon P2 (even-odd)."""
    x, y = Q[:, 0][:, None], Q[:, 1][:, None]
    x0, y0 = P2[:, 0][None, :], P2[:, 1][None, :]
    x1, y1 = np.roll(P2[:, 0], -1)[None, :], np.roll(P2[:, 1], -1)[None, :]
    cross = (y0 > y) != (y1 > y)
    dy = np.where(cross, y1 - y0, 1.0)
    hit = cross & (x < x0 + (y - y0) * (x1 - x0) / dy)
    return (hit.sum(axis=1) % 2) == 1


def _diagonals(P2, eps=1e-13):
    """ok[i, j]: the chord between corners i and j lies inside the polygon, crossing no edge properly (touching at an
    end is no crossing) and passing through no other corner (sides count as chords)."""
    n = len(P2)
    ok = np.zeros((n, n), dtype=bool)
    k = np.arange(n)
    nk = (k + 1) % n
    ok[k, nk] = ok[nk, k] = True
    I, J = np.triu_indices(n, 2)
    sel = ~((I == 0) & (J == n - 1))
    I, J = I[sel], J[sel]
    if not len(I):
        return ok
    scale = max(float(np.ptp(P2[:, 0])), float(np.ptp(P2[:, 1])), 1e-9)
    A, Bc = P2[I][:, None, :], P2[J][:, None, :]
    C, D = P2[None, :, :], P2[nk][None, :, :]
    d1, d2 = _cross2v(A, Bc, C), _cross2v(A, Bc, D)
    d3, d4 = _cross2v(C, D, A), _cross2v(C, D, Bc)
    proper = (((d1 > eps) & (d2 < -eps)) | ((d1 < -eps) & (d2 > eps))) & \
             (((d3 > eps) & (d4 < -eps)) | ((d3 < -eps) & (d4 > eps)))
    touches = (k[None, :] == I[:, None]) | (k[None, :] == J[:, None]) | (nk[None, :] == I[:, None]) | \
              (nk[None, :] == J[:, None])
    good = ~(proper & ~touches).any(axis=1)
    ab = P2[J] - P2[I]
    L2 = (ab * ab).sum(axis=1)
    t = ((P2[None, :, :] - P2[I][:, None, :]) * ab[:, None, :]).sum(axis=2) / L2[:, None]
    off = np.abs(d1) / np.sqrt(L2)[:, None]
    own = (k[None, :] == I[:, None]) | (k[None, :] == J[:, None])
    good &= ~((t > 0.0) & (t < 1.0) & (off < 1e-9 * scale) & ~own).any(axis=1)
    good &= _inside_v(P2, 0.5 * (P2[I] + P2[J]))
    ok[I, J] = ok[J, I] = good
    return ok


def tri_cost(al, size):
    """What a triangle of smallest altitude al costs a cut at size (SN8 counts the triangles under two pixels, so a
    thin one costs one), plus SLIVER x (size / al)^2, so of two cuts with as many thin triangles the one whose
    triangles are least thin wins, and a sliver a tenth of size thin costs as much as a second thin triangle (a strip
    fanned from one far corner into long slivers loses to a cut that leaves its corner's cap alone thin)."""
    return (1.0 if al < size else 0.0) + SLIVER * (size / al) ** 2


def best_triangles(P2, size):
    """The simple polygon P2 (counter-clockwise, collinear corners allowed) cut into its n - 2 triangles so the sum of
    tri_cost is least: exactly, by the interval recursion over chords (O(n^3)); fewest thin triangles first, then the
    least thin, so none is made that a better cut avoids. Returns index triples, and the sum."""
    n = len(P2)
    if n == 3:
        if _cross2(*P2) <= 1e-14:
            raise ValueError("a face whose only triangle is degenerate")
        return [(0, 1, 2)], tri_cost(_alt(*P2), size)
    ok = _diagonals(P2)
    pts = [(float(x), float(y)) for x, y in P2]
    side = [[math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]) for j in range(n)] for i in range(n)]
    INF = float("inf")
    cost = [[INF] * n for _ in range(n)]
    pick = [[-1] * n for _ in range(n)]
    for i in range(n - 1):
        cost[i][i + 1] = 0.0
    for gap in range(2, n):
        for i in range(0, n - gap):
            j = i + gap
            if not ok[i, j]:
                continue
            best, bk = INF, -1
            a = pts[i]
            c = pts[j]
            sij = side[i][j]
            ci = cost[i]
            for k in range(i + 1, j):
                if ci[k] == INF or cost[k][j] == INF:
                    continue
                b = pts[k]
                A2 = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                if A2 <= 1e-14:
                    continue
                al = A2 / max(side[i][k], sij, side[k][j])
                if al <= 0:
                    continue
                v = ci[k] + cost[k][j] + tri_cost(al, size)
                if v < best - 1e-15:
                    best, bk = v, k
            cost[i][j], pick[i][j] = best, bk
    if cost[0][n - 1] == INF:
        raise ValueError("a face that cannot be triangulated (not simple?)")
    tris = []
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        k = pick[i][j]
        tris.append((i, k, j))
        stack += [(i, k), (k, j)]
    return sorted(tris), cost[0][n - 1]


def _loop_cost(P, plane, loop, size):
    e1, e2 = basis(plane["n"])
    P3 = P[loop]
    return best_triangles(np.stack([P3 @ e1, P3 @ e2], -1), size)[1]


def thin_out(surf, size):
    """Fewest, fattest triangles: a corner lying straight between its neighbours in every loop that holds it (a
    column's line on a planar face, say) leaves all those loops whenever the loops' best cut costs no more without it
    (best_triangles' sum, at size). Every holder loses it together, so no T-junction is made. Corners are tried in
    their welded order, pass after pass, until none goes: deterministic."""
    W, groups = surf["W"], surf["groups"]
    P = W.array()
    loops = [list(loop) for _f, _p, loop in groups]
    planes = [p for _f, p, _l in groups]
    cost = [_loop_cost(P, planes[li], loops[li], size) for li in range(len(loops))]
    version = [0] * len(loops)          # a loop's version moves on when it loses a corner
    tried = {}                          # a corner kept, with its holders' versions then: kept again until one moves
    while True:
        holders = {}
        for li, loop in enumerate(loops):
            for k, v in enumerate(loop):
                holders.setdefault(v, []).append((li, k))
        dropped = False
        for v in sorted(holders):
            hs = holders[v]
            if len({li for li, _k in hs}) != len(hs):
                continue
            seen = tuple((li, version[li]) for li, _k in hs)
            if tried.get(v) == seen:
                continue
            tried[v] = seen
            if not all(len(loops[li]) > 3 and _straight(P, loops[li][k - 1], v, loops[li][(k + 1) % len(loops[li])])
                       for li, k in hs):
                continue
            new = {li: [u for u in loops[li] if u != v] for li, _k in hs}
            try:
                after = {li: _loop_cost(P, planes[li], loop, size) for li, loop in new.items()}
            except ValueError:
                continue
            if sum(after.values()) <= sum(cost[li] for li in new) * (1 + 1e-12):
                for li, loop in new.items():
                    loops[li], cost[li] = loop, after[li]
                    version[li] += 1
                dropped = True
                break                       # the holders changed: start the pass again
        if not dropped:
            break
    return dict(W=W, groups=[(f, p, loop) for (f, p, _l), loop in zip(groups, loops)])


def triangulate(surf, size=0.01):
    """The drawn surface as one mesh: V (vertices), T (triangles, counter-clockwise about their face's normal),
    face (each triangle's face), planes (each triangle's plane), and loops (each group's loops, for the checks). Each
    face is cut by best_triangles at size (m), the level's two pixels at its far edge."""
    W, groups = surf["W"], surf["groups"]
    V = W.array()
    T, faces, planes = [], [], []
    for face, p, loop in groups:
        e1, e2 = basis(p["n"])
        P3 = V[loop]
        P2 = np.stack([P3 @ e1, P3 @ e2], -1)
        if area(P3, p["n"]) <= 0:
            raise ValueError(f"{face}: a loop not counter-clockwise about its normal")
        local, _c = best_triangles(P2, size)
        for a, b, c in local:
            T.append((loop[a], loop[b], loop[c]))
            faces.append(face)
            planes.append(p)
    T = np.array(T, dtype=np.int64).reshape(-1, 3)
    used = np.unique(T)                        # only the vertices a triangle holds, in their welded order
    remap = np.full(len(V), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    groups = [(face, p, [int(remap[v]) for v in loop]) for face, p, loop in groups]
    return dict(V=V[used], T=remap[T], face=faces, plane=planes, groups=groups)


# -- measures --------------------------------------------------------------------------------------------------------

def tri_altitudes(V, T):
    """Each triangle's smallest altitude and area (m, m2)."""
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    A2 = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    L = np.max(np.stack([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - a, axis=1),
                         np.linalg.norm(c - b, axis=1)]), axis=0)
    return A2 / L, 0.5 * A2


def _lattice_uvw(n, cache={}):
    if n not in cache:
        uv = np.array([(u, v) for u in range(n + 1) for v in range(n + 1 - u)], float)
        cache[n] = np.column_stack([uv, n - uv.sum(axis=1)]) / n
    return cache[n]


def sample_tris(V, T, step):
    """Points over every triangle, about step (m) apart (barycentric lattice), with each point's triangle."""
    pts, owner = [], []
    for ti, (i, j, k) in enumerate(T):
        a, b, c = V[i], V[j], V[k]
        L = max(np.linalg.norm(b - a), np.linalg.norm(c - a), np.linalg.norm(c - b))
        w = _lattice_uvw(max(1, int(math.ceil(L / step))))
        pts.append(w @ np.array([a, b, c]))
        owner.append(np.full(len(w), ti))
    if not pts:
        return np.zeros((0, 3)), np.zeros(0, int)
    return np.concatenate(pts), np.concatenate(owner)


def point_tri_distance(P, a, b, c):
    """The distance from each point (n x 3) to the triangle abc (exact: the plane, or its nearest edge)."""
    n = np.cross(b - a, c - a)
    nn = np.linalg.norm(n)
    if nn < 1e-18:
        return np.full(len(P), np.inf)
    n = n / nn
    dpl = (P - a) @ n
    Q = P - dpl[:, None] * n
    inside = np.ones(len(P), bool)
    for p, q in ((a, b), (b, c), (c, a)):
        inside &= (np.cross(q - p, Q - p) @ n) >= -1e-15
    best = np.where(inside, np.abs(dpl), np.inf)
    for p, q in ((a, b), (b, c), (c, a)):
        d = q - p
        t = np.clip((P - p) @ d / max(float(d @ d), 1e-30), 0.0, 1.0)
        best = np.minimum(best, np.linalg.norm(P - (p + t[:, None] * d), axis=1))
    return best


def surface_distance(P, V, T, reach=None):
    """The distance from each point to the nearest triangle of a mesh. With reach (m), a triangle is tried only for
    the points inside its box grown by reach, so a distance up to reach is exact and a point farther from every
    triangle is inf."""
    best = np.full(len(P), np.inf)
    for i, j, k in T:
        a, b, c = V[i], V[j], V[k]
        if reach is None:
            best = np.minimum(best, point_tri_distance(P, a, b, c))
            continue
        lo = np.minimum(np.minimum(a, b), c) - reach
        hi = np.maximum(np.maximum(a, b), c) + reach
        sel = np.nonzero(np.all((P >= lo) & (P <= hi), axis=1))[0]
        if len(sel):
            best[sel] = np.minimum(best[sel], point_tri_distance(P[sel], a, b, c))
    return best
