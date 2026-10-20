"""A tree's whole life, grown once, year by year (docs/trees.md, the growth timeline).

    python blender/generators/tree_growth.py <species> <seed> [years] [sketch.png] [site quality]
                                                                          (numpy, and Pillow for the sketch)

After Palubicki et al. 2009, "Self-organizing tree models for image synthesis": every year each bud grows or waits by
the light it gets; the light each branch earns is summed down to the root, and the year's growth is shared
back up by the extended Borchert-Honda rule, apical control (lambda) favouring the continuing axis and loosening with
age, so a young tree is tall and an old one broad; a branch that earns too little light for its size is shed; widths
follow the pipe model and never shrink when a branch is shed or cut, so the trunk remembers. The leader keeps to the
species' height curve (Chapman-Richards) while the species keeps a leader. Light is not the paper's shadow pyramid,
which lights a crown only from above: under the west coast's overcast skies at 59 degrees north the lower crown of an
open-grown tree lives on light from the side, so each bud looks at an overcast sky along 26 rays through a voxel grid
of the foliage, and of the houses and walls beside it, and grows towards where its light comes from. A crown envelope, scaled with the tree's
height, keeps growth inside the silhouette a painter would give it; the hand-made crown masses replace it.

Every node keeps the year it grew, the year it was shed or cut, and its radius in every year since: Timeline.at(year)
is the tree at that age, and an older tree contains its younger self exactly. Deterministic: randomness only from
random.Random seeded by the tree's seed, a bud's stable key and the year. The habit and this simulator carry a version:
a change is a new version, never a silent edit of history.

Units: metres, z up, the trunk's foot at the origin; years from the seed's first summer (year 0).
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field

import numpy as np

VERSION = "growth-1"
UP = np.array([0.0, 0.0, 1.0])

# -- species: how each grows (its habit) -------------------------------------------------------------------------------
# From the species' botany where it is known (heights, growth curves, branching), tuned by eye against the reference
# board where it is not. Lengths in metres, angles in degrees, per-order lists indexed by branch order (0 the trunk).
# height is the species' on a good, sheltered site in the setting (here the west coast, not a forest record); the
# site's quality scales it, so thin soil on rock and the sea wind keep a tree low.
# internode and shoot are a grown tree's: a metamer's length, and a lateral's year in full light; a young tree's shoots
# are shorter in proportion to its height until full_size, as a seedling's are a few centimetres. setpoint: the angle
# above level each order's shoots steer towards (the gravitropic set-point), at the crown's top and at its foot, and
# steer how much of the difference a shoot makes up per internode: a limb can sag at its base and turn up at its tip.
# shed: a branch dies when its buds' mean light has been under this share of open sky for so many years running (the
# species' shade tolerance), or when it has no buds left. light: the foliage's extinction per bud in a cell, how much
# the others in a bud's own cell crowd it, and for how many years a shoot keeps its needles or leaves and so shades.
SPECIES = {
    # Norway spruce, Picea abies. Excurrent: one leader all its life, a whorl of 3 to 6 branches at the top of each
    # year's shoot, near level; branches flat, forking in their own plane; the lower ones droop with the tips turned
    # up, second-order shoots hang (the comb form). A narrow cone to the ground in the open, broad when young. On a
    # good, sheltered site on this coast about 2 m at 10 years, 11 at 30, 21 at 60 and 27 at 100.
    "spruce": dict(
        kind="conifer", height=30.0, growth=(0.030, 2.0), leader_until=999,
        internode=0.14, shoot=0.30, full_size=3.5, alpha=2.0, apical=(0.60, 0.56, 80),
        whorl=(3, 6), whorl_angle=74.0, side_angle=48.0, side_p=0.8, along_p=0.45, along_vigour=0.3, max_order=2,
        setpoint=((90, 90), (18, -22), (-30, -45), (-40, -50)), steer=0.18, light_pull=0.20, jitter=0.05,
        envelope="cone", width=(0.34, 0.17), crown_base=(0.0, 0.03),
        shed=(0.10, 4), bud_life=3, tip_radius=0.004, pipe=2.2, light=(0.30, 0.25, 6),
    ),
    # Downy birch, Betula pubescens. A leader while young, then the crown opens into a few ascending limbs and a mass
    # of fine twigs; alternate buds (2/5 phyllotaxis); an airy, irregular crown, not weeping (that is the silver birch);
    # it needs light and sheds its lower branches early. On a good site on this coast about 6 m at 15 years, 11 at 30
    # and 15 at 60; few live past 100.
    "birch": dict(
        kind="broadleaf", height=16.0, growth=(0.050, 1.5), leader_until=28,
        internode=0.22, shoot=0.35, full_size=3.0, alpha=2.0, apical=(0.58, 0.50, 40),
        phyllotaxis=144.0, lateral_angle=42.0, max_order=4,
        setpoint=((90, 90), (55, 35), (30, 10), (10, -5), (-5, -20), (-15, -30)), steer=0.15, light_pull=0.25,
        jitter=0.08,
        envelope="ovate", width=(0.20, 0.24), crown_base=(0.12, 0.38),
        shed=(0.25, 2), bud_life=4, tip_radius=0.003, pipe=2.4, light=(0.22, 0.25, 2),
    ),
}


def height_curve(sp, year, quality=1.0):
    """Chapman-Richards: H (1 - e^(-k t))^c, slow from seed, fastest in youth, levelling off; H the species' height
    times the site's quality."""
    k, c = sp["growth"]
    return quality * sp["height"] * (1.0 - math.exp(-k * max(year, 0))) ** c


# -- the timeline ------------------------------------------------------------------------------------------------------

@dataclass(eq=False)
class Node:
    """An internode: a piece of stem between two buds."""
    id: int
    parent: int                  # -1 for the first
    start: np.ndarray
    end: np.ndarray
    born: int
    order: int                   # 0 the trunk, 1 a branch off it, 2 a branch off that ...
    died: int | None = None      # the year it was shed or cut
    radius: dict = field(default_factory=dict)   # year -> radius (m), written every year it lives
    children: list = field(default_factory=list)


@dataclass(eq=False)
class Bud:
    node: int                    # the node it sits on
    pos: np.ndarray
    dir: np.ndarray
    order: int                   # the order of the shoot it would grow
    apical: bool                 # continues its node's axis
    key: str                     # a stable id, for seeding
    born: int
    light: float = 0.0
    resource: float = 0.0
    way: np.ndarray = field(default_factory=lambda: np.zeros(3))
    vigour: float = 1.0          # a weak bud (a conifer's buds along the shoot) makes less of its share


class Timeline:
    """A tree's life: its nodes, each with the year it grew, died and its radius by year."""

    def __init__(self, species, seed, quality=1.0, version=VERSION):
        self.species, self.seed, self.quality, self.version = species, seed, quality, version
        self.nodes: list[Node] = []
        self.years = 0

    def alive(self, nd, year):
        return nd.born <= year and (nd.died is None or nd.died > year)

    def at(self, year):
        """The living nodes at an age, with their radius then."""
        return [(nd, radius_at(nd, year)) for nd in self.nodes if self.alive(nd, year)]

    def height(self, year):
        return max((nd.end[2] for nd, _ in self.at(year)), default=0.0)

    def save(self, path):
        n = len(self.nodes)
        radius = np.zeros((n, self.years + 1), dtype=np.float32)
        for nd in self.nodes:
            for y, r in nd.radius.items():
                radius[nd.id, y] = r
        np.savez_compressed(
            path, version=self.version, species=self.species, seed=self.seed, years=self.years,
            parent=np.array([nd.parent for nd in self.nodes], dtype=np.int32),
            start=np.array([nd.start for nd in self.nodes], dtype=np.float32),
            end=np.array([nd.end for nd in self.nodes], dtype=np.float32),
            born=np.array([nd.born for nd in self.nodes], dtype=np.int16),
            died=np.array([-1 if nd.died is None else nd.died for nd in self.nodes], dtype=np.int16),
            order=np.array([nd.order for nd in self.nodes], dtype=np.int8),
            radius=radius,
        )
        return path


def radius_at(nd, year):
    if year in nd.radius:
        return nd.radius[year]
    ys = [y for y in nd.radius if y <= year]
    return nd.radius[max(ys)] if ys else 0.0


# -- the crown's envelope: where growth may go, scaled with the tree's height ----------------------------------------

def envelope_ok(p, sp, H, H_full):
    """Inside the species' crown for a tree of height H that will grow to H_full. Simple solids for now; the
    hand-made masses replace them."""
    H = max(H, 0.05)
    m = min(H / H_full, 1.0)                              # how grown the tree is
    width = sp["width"][0] + (sp["width"][1] - sp["width"][0]) * m
    base = sp["crown_base"][0] + (sp["crown_base"][1] - sp["crown_base"][0]) * m
    z = p[2] / H
    r = math.hypot(p[0], p[1]) / H
    if z < 0.0 or z > 1.06:
        return False
    if sp["envelope"] == "cone":
        return r <= width * (1.04 - z) / (1.04 - base) + 0.03 if z >= base else r <= 0.03
    # ovate: from the crown base, widest a little above the crown's middle, rounded at the top
    if z < base:
        return r <= 0.04 + 0.5 * width * (z / max(base, 1e-3)) ** 3
    t = (z - base) / (1.06 - base)
    return r <= width * math.sin(math.pi * min(t, 1.0) ** 0.75) * 1.05 + 0.03


# -- light: an overcast sky seen through the crown -----------------------------------------------------------------

def sky_directions():
    """Directions over the sky with their weights: an overcast sky (CIE: luminance (1 + 2 sin e) / 3), each sample
    weighted by the patch of sky it stands for. Rings at 12, 35, 60 and 90 degrees above level."""
    dirs, w = [], []
    rings = ((12.0, 10, 24.0), (35.0, 9, 23.0), (60.0, 6, 25.0), (90.0, 1, 0.0))
    for e, n, band in rings:
        er = math.radians(e)
        lum = (1 + 2 * math.sin(er)) / 3
        if n == 1:
            area = 2 * math.pi * (1 - math.cos(math.radians(12.5)))
        else:
            area = 2 * math.pi * math.cos(er) * math.radians(band) / n
        for k in range(n):
            az = 2 * math.pi * (k + 0.5 * (e > 30)) / n
            dirs.append((math.cos(er) * math.cos(az), math.cos(er) * math.sin(az), math.sin(er)))
            w.append(lum * area)
    w = np.array(w)
    return np.array(dirs), w / w.sum()


SKY_DIRS, SKY_W = sky_directions()
# steps along a ray, in cells: fine near the bud, coarser further off, read from a blurred grid at the coarse steps
_steps = []
_t = 0.0
for _d, _upto in ((1, 8), (2, 16), (4, 32), (8, 64), (16, 128), (32, 256)):
    while _t + _d <= _upto:
        _t += _d
        _steps.append((_t - _d / 2, _d))
RAY_STEPS = np.array(_steps)


class Sky:
    """How much of an overcast sky each bud sees through the foliage (the buds and the young, leafy shoots) and through
    whatever stands beside the tree (the site's boxes: a house, a wall), and the direction its light comes from: the
    shoot grows towards it. Rays along 26 directions, marched through the foliage's optical depth in a voxel grid,
    from near the bud outwards at coarser steps through a blurred copy of the grid."""

    LEVELS = 4

    def __init__(self, radius, height, cell, extinction, own):
        self.cell, self.k, self.own = cell, extinction, own
        m = 2 ** (self.LEVELS - 1)
        nx = int(math.ceil((2 * radius / cell + 1) / m)) * m
        nz = int(math.ceil((height / cell + 4) / m)) * m
        self.shape = np.array([nx, nx, nz])
        self.origin = np.array([-radius, -radius, 0.0])

    def build(self, buds, foliage, boxes=()):
        """buds and foliage: points (foliage weighs half a bud); boxes: (x0, y0, z0, x1, y1, z1), opaque."""
        tau = np.zeros(tuple(self.shape), dtype=np.float32)
        for pts, wgt in ((buds, 1.0), (foliage, 0.5)):
            if len(pts):
                ii = self.cells(np.asarray(pts))
                np.add.at(tau, (ii[:, 0], ii[:, 1], ii[:, 2]), wgt * self.k)
        for (x0, y0, z0, x1, y1, z1) in boxes:
            i0, i1 = self.cells(np.array([[x0, y0, z0], [x1, y1, z1]]))
            tau[i0[0]:i1[0] + 1, i0[1]:i1[1] + 1, i0[2]:i1[2] + 1] = 50.0
        self.mips = [tau]
        for _ in range(self.LEVELS - 1):
            t = self.mips[-1]
            a, b, c = (np.array(t.shape) // 2)
            self.mips.append(t.reshape(a, 2, b, 2, c, 2).mean(axis=(1, 3, 5)))

    def cells(self, pts):
        i = np.floor((pts - self.origin) / self.cell).astype(int)
        return np.clip(i, 0, self.shape - 1)

    def light(self, pts):
        """For each point: the share of open sky it sees (0 to 1), and the way its light comes from."""
        pts = np.asarray(pts, dtype=float)
        p = (pts - self.origin) / self.cell                  # continuous cell coordinates
        n = len(pts)
        seen = np.zeros(n)
        way = np.zeros((n, 3))
        for d, w in zip(SKY_DIRS, SKY_W):
            depth = np.zeros(n)
            inside = np.ones(n, dtype=bool)
            for t, dt in RAY_STEPS:
                q = p + d * t
                ok = inside & (q[:, 0] >= 0) & (q[:, 1] >= 0) & (q[:, 2] >= 0) & (q[:, 0] < self.shape[0]) \
                    & (q[:, 1] < self.shape[1]) & (q[:, 2] < self.shape[2])
                if not ok.any():
                    break
                inside = ok
                lvl = min(int(math.log2(dt)), self.LEVELS - 1)
                g = self.mips[lvl]
                ii = (q[ok] / (2 ** lvl)).astype(int)
                depth[ok] += g[ii[:, 0], ii[:, 1], ii[:, 2]] * dt
            tr = np.exp(-depth) * w
            seen += tr
            way += tr[:, None] * d
        # crowding: the others in the bud's own cell
        ii = self.cells(pts)
        own = np.maximum(self.mips[0][ii[:, 0], ii[:, 1], ii[:, 2]] - self.k, 0.0)
        seen *= np.exp(-self.own * own)
        norm = np.linalg.norm(way, axis=1, keepdims=True)
        return seen, np.where(norm > 1e-9, way / np.maximum(norm, 1e-9), 0.0)


# -- geometry helpers --------------------------------------------------------------------------------------------------

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else UP.copy()


def rotate(v, axis, deg):
    """Rodrigues' rotation of v about axis."""
    a = unit(axis)
    t = math.radians(deg)
    return v * math.cos(t) + np.cross(a, v) * math.sin(t) + a * np.dot(a, v) * (1 - math.cos(t))


def side_of(v):
    """A horizontal vector at right angles to v (or any right angle if v is vertical)."""
    s = np.cross(UP, v)
    return unit(s) if np.linalg.norm(s) > 1e-6 else np.array([1.0, 0.0, 0.0])


def tilt(d, towards, deg):
    """d turned by deg towards the direction 'towards' (in the plane of the two)."""
    axis = np.cross(d, towards)
    if np.linalg.norm(axis) < 1e-9:
        axis = side_of(d)
    return unit(rotate(d, axis, deg))


# -- growing -----------------------------------------------------------------------------------------------------------

def grow(species, seed, years=60, site=(), quality=1.0):
    """Grow a tree of the species for so many years. site: obstacles that cast full shade, as axis-aligned boxes
    (x0, y0, z0, x1, y1, z1) in the tree's frame: a house beside it, a wall. quality: the site's, from its soil and
    shelter (1 a good, sheltered garden; about 0.4 a birch on a knoll in the sea wind)."""
    sp = SPECIES[species]
    tl = Timeline(species, seed, quality)
    H_full = sp["height"] * quality
    extinction, own, foliage_years = sp["light"]
    C = 10.0                                              # a bud in open sky gets C
    per_light = sp["shoot"] / sp["internode"] / C         # internodes grown per unit of resource

    def rng_for(key, year):
        return random.Random(f"{VERSION}:{species}:{seed}:{key}:{year}")

    first = Node(0, -1, np.zeros(3), np.array([0.0, 0.0, sp["internode"] * 0.12]), 0, 0)
    first.radius[0] = sp["tip_radius"]
    tl.nodes.append(first)
    buds = [Bud(0, first.end.copy(), UP.copy(), 0, True, "0", 0)]
    starved = {}                                          # branch base -> years in a row its buds have been starved

    for year in range(1, years + 1):
        nodes = tl.nodes
        N = len(nodes)
        parent = np.array([nd.parent for nd in nodes])
        live = np.array([nd.died is None for nd in nodes])
        top = max(nd.end[2] for nd in nodes if nd.died is None)
        target = height_curve(sp, year, quality)
        H = max(target, 0.05)                             # the crown keeps to the height curve all its life
        # shoots, and the grain of the shade, in proportion to the tree until it is grown
        length = sp["internode"] * min(max(H / sp["full_size"], 0.12), 1.0)
        cell = 1.5 * length
        sky = Sky(H * (max(sp["width"]) + 0.08) + 3 * cell, H * 1.1 + 3 * cell, cell, extinction, own)

        # 1. light: what each bud sees of the sky through the foliage and the site, and from where
        if buds:
            pts = np.array([bd.pos for bd in buds])
            leafy = [(nd.start + nd.end) / 2 for nd in nodes if nd.died is None and year - nd.born < foliage_years]
            sky.build(pts, np.array(leafy).reshape(-1, 3), site)
            seen, way = sky.light(pts)
            for bd, l, w in zip(buds, seen, way):
                bd.light, bd.way = float(C * l), w

        def summed():
            qn, nb = np.zeros(N), np.zeros(N)
            for bd in buds:
                qn[bd.node] += bd.light
                nb[bd.node] += 1
            for i in range(N - 1, 0, -1):
                if live[i]:
                    qn[parent[i]] += qn[i]
                    nb[parent[i]] += nb[i]
            return qn, nb

        qn, nb = summed()

        # 2. shedding: a branch starved of light for years, or with no buds left, dies (the trunk is never shed)
        share, years_starved = sp["shed"]
        shed_any = False
        for nd in nodes:
            if nd.died is None and nd.parent >= 0 and nd.order > nodes[nd.parent].order and year - nd.born > 1:
                if nb[nd.id] > 0 and qn[nd.id] / nb[nd.id] >= share * C:
                    starved.pop(nd.id, None)
                    continue
                starved[nd.id] = starved.get(nd.id, 0) + 1
                if nb[nd.id] == 0 or starved[nd.id] >= years_starved:
                    kill(tl, nd.id, year)
                    shed_any = True
        if shed_any:
            live = np.array([nd.died is None for nd in nodes])
            buds = [bd for bd in buds if nodes[bd.node].died is None]
            qn, nb = summed()

        # 3. the year's growth shared back up (extended Borchert-Honda)
        l0, l1, mature = sp["apical"]
        lam = l0 + (l1 - l0) * min(year / mature, 1.0)
        buds_at = {}
        for bd in buds:
            buds_at.setdefault(bd.node, []).append(bd)
        v = np.zeros(N)
        v[0] = sp["alpha"] * qn[0]
        for nd in nodes:
            if nd.died is not None or v[nd.id] <= 0:
                continue
            kids = [("n", nodes[c]) for c in nd.children if nodes[c].died is None] + [("b", bd) for bd in buds_at.get(nd.id, [])]
            if not kids:
                continue
            light = [qn[k.id] if t == "n" else k.light for t, k in kids]
            main = [(t == "n" and k.order == nd.order) or (t == "b" and k.apical) for t, k in kids]
            qm = sum(l for l, m in zip(light, main) if m)
            ql = sum(l for l, m in zip(light, main) if not m)
            den = lam * qm + (1 - lam) * ql
            if den <= 0:
                continue
            for (t, k), l, m in zip(kids, light, main):
                share = v[nd.id] * (lam if m else 1 - lam) * l / den
                if t == "n":
                    v[k.id] = share
                else:
                    k.resource = share

        # 4. buds with resource grow shoots; the new buds wait for next year. The leader keeps to the height curve.
        grown, kept = [], []
        for bd in buds:
            rng = rng_for(bd.key, year)
            n = int(bd.resource * bd.vigour * per_light + rng.random())
            leader = bd.order == 0 and bd.apical and year < sp["leader_until"]
            exact = None
            if leader:
                rise = target - top                 # the leader meets the height curve, never overshoots it
                n = int(math.ceil(rise / length)) if rise > 1e-3 else 0
                exact = rise / n if n else None
            n = min(n, 8)
            if n <= 0:
                if year - bd.born <= sp["bud_life"] or leader:
                    kept.append(bd)
                continue
            new = shoot(tl, sp, bd, n, exact or length, year, H, H_full, rng, exact=exact is not None)
            if new is None:
                bd.born = year                      # at the crown's edge: a living shoot that cannot extend
                kept.append(bd)
                continue
            grown.extend(new)
        buds = kept + grown

        # 5. widths: the pipe model, never smaller than last year (the trunk remembers)
        r = np.zeros(len(tl.nodes))
        for nd in reversed(tl.nodes):
            if nd.died is not None:
                continue
            kids = [c for c in nd.children if tl.nodes[c].died is None]
            rr = sum(r[c] ** sp["pipe"] for c in kids) ** (1.0 / sp["pipe"]) if kids else sp["tip_radius"]
            r[nd.id] = max(rr, radius_at(nd, year - 1), sp["tip_radius"])
            nd.radius[year] = float(r[nd.id])
        tl.years = year
    return tl


def shoot(tl, sp, bd, n, length, year, crown_h, H_full, rng, exact=False):
    """Grow n internodes of about the length from a bud; return the new buds, or None if it could not grow at all."""
    nodes = tl.nodes
    parent_id, pos, d = bd.node, bd.pos.copy(), bd.dir.copy()
    order = bd.order
    hi, lo = sp["setpoint"][min(order, len(sp["setpoint"]) - 1)]
    new_buds = []
    made = 0
    for i in range(n):
        toward = bd.way
        jitter = np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]) * sp["jitter"]
        # steer towards the order's set-point angle for this height in the crown, then towards light, then a wobble
        set_to = lo + (hi - lo) * min(max(pos[2] / max(crown_h, 1e-3), 0.0), 1.0)
        turn = (set_to - math.degrees(math.asin(max(-1.0, min(1.0, d[2]))))) * sp["steer"]
        d2 = tilt(d, UP if turn > 0 else -UP, abs(turn)) if abs(turn) > 1e-3 else d
        d2 = unit(d2 + sp["light_pull"] * toward + jitter)
        end = pos + d2 * length * (1.0 if exact else 0.85 + 0.3 * rng.random())
        if not envelope_ok(end, sp, crown_h * 1.02, H_full):
            break
        d = d2
        nd = Node(len(nodes), parent_id, pos, end, year, order)
        nd.radius[year] = sp["tip_radius"]
        nodes[parent_id].children.append(nd.id)
        nodes.append(nd)
        made += 1
        if sp["kind"] == "broadleaf" and order + 1 <= sp["max_order"]:
            # one lateral bud at each node, turning round the shoot by the phyllotaxis angle
            ang = (nd.id * sp["phyllotaxis"]) % 360.0
            s = rotate(side_of(d), d, ang)
            ld = tilt(d, s, sp["lateral_angle"] + rng.uniform(-10, 10))
            new_buds.append(Bud(nd.id, end.copy(), ld, order + 1, False, f"{bd.key}.{year}.{i}", year))
        elif sp["kind"] == "conifer" and order + 1 <= sp["max_order"] and i < n - 1 and rng.random() < sp["along_p"]:
            # small side buds along the year's shoot, left and right in turn: on the leader round the stem
            # (the interwhorl branches), on a limb in its own plane
            if order == 0:
                s = rotate(side_of(d), d, rng.uniform(0, 360))
                ld = tilt(d, s, sp["whorl_angle"] + rng.uniform(-8, 8))
            else:
                ld = tilt(d, (1 if i % 2 else -1) * side_of(d), sp["side_angle"] + rng.uniform(-10, 10))
            new_buds.append(Bud(nd.id, end.copy(), ld, order + 1, False, f"{bd.key}.{year}.a{i}", year,
                                vigour=sp["along_vigour"]))
        parent_id, pos = nd.id, end
    if made == 0:
        return None
    if sp["kind"] == "conifer" and order + 1 <= sp["max_order"]:
        if order == 0:
            # a whorl at the top of the leader's year
            k = rng.randint(*sp["whorl"])
            a0 = rng.uniform(0, 360)
            for w in range(k):
                s = rotate(side_of(d), d, a0 + w * 360.0 / k + rng.uniform(-14, 14))
                ld = tilt(d, s, sp["whorl_angle"] + rng.uniform(-6, 6))
                new_buds.append(Bud(parent_id, pos.copy(), ld, 1, False, f"{bd.key}.{year}.w{w}", year))
        else:
            # flat branching: a side bud left and right, in the branch's own plane
            s = side_of(d)
            for sign, tag in ((1, "l"), (-1, "r")):
                if rng.random() < sp["side_p"]:
                    ld = tilt(d, sign * s, sp["side_angle"] + rng.uniform(-8, 8))
                    new_buds.append(Bud(parent_id, pos.copy(), ld, order + 1, False, f"{bd.key}.{year}.{tag}", year))
    new_buds.append(Bud(parent_id, pos.copy(), d, order, True, f"{bd.key}.{year}", year))
    return new_buds


def kill(tl, node_id, year):
    """Shed a node and everything beyond it."""
    stack = [node_id]
    while stack:
        nd = tl.nodes[stack.pop()]
        if nd.died is None:
            nd.died = year
            stack.extend(nd.children)


def check(tl):
    """The timeline's promises: a node lives from its birth to its death, and never thins."""
    for nd in tl.nodes:
        ys = sorted(nd.radius)
        assert ys[0] == nd.born, (nd.id, ys[0], nd.born)
        last = nd.died - 1 if nd.died is not None else tl.years
        assert ys[-1] == last, (nd.id, ys[-1], last)
        rs = [nd.radius[y] for y in ys]
        assert all(r1 >= r0 for r0, r1 in zip(rs, rs[1:])), nd.id
    return True


# -- a quick look: the tree drawn side-on at several ages (no Blender needed) -----------------------------------------

def sketch(tl, ages, path, px_per_m=22):
    from PIL import Image, ImageDraw
    sp = SPECIES[tl.species]
    H = sp["height"] * 1.05
    W = 2 * sp["height"] * max(sp["width"]) + 4
    w, h = int(W * px_per_m), int(H * px_per_m)
    sheet = Image.new("RGB", (w * len(ages), h + 26), (236, 232, 222))
    d = ImageDraw.Draw(sheet)
    for i, y in enumerate(ages):
        ox = i * w + w / 2
        living = sorted(tl.at(y), key=lambda t: t[1])
        for nd, r in living:
            x0, z0 = ox + nd.start[0] * px_per_m, h - nd.start[2] * px_per_m
            x1, z1 = ox + nd.end[0] * px_per_m, h - nd.end[2] * px_per_m
            d.line([(x0, z0), (x1, z1)], fill=(44, 38, 32), width=max(1, int(round(2 * r * px_per_m))))
        d.line([(i * w, h), (i * w + w, h)], fill=(120, 110, 96))
        d.text((i * w + 6, h + 6), f"{tl.species} {tl.seed}: {y} years, {tl.height(y):.1f} m", fill=(30, 30, 30))
    sheet.save(path)
    return path


if __name__ == "__main__":
    import time
    species = sys.argv[1] if len(sys.argv) > 1 else "spruce"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    years = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    out = sys.argv[4] if len(sys.argv) > 4 else f"/tmp/{species}-{seed}.png"
    quality = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    t = time.time()
    tl = grow(species, seed, years, quality=quality)
    check(tl)
    print(f"{species} seed {seed}: {len(tl.nodes)} nodes grown, {len(tl.at(years))} alive at {years} years, "
          f"{tl.height(years):.1f} m, trunk {2 * radius_at(tl.nodes[0], years) * 100:.0f} cm, {time.time() - t:.1f} s")
    print(sketch(tl, [y for y in (5, 15, 30, 60, 100) if y <= years], out))
