"""Where things grow on a surface, and for how long (docs/nature.md, Growth on surfaces): the growth potentials every
generator bakes into what it builds (stone now; timber, roofs, bark, concrete next), from the surface's facts, so
that the one growth layer every shader draws (unity/Assets/Shaders/Growth.hlsl) puts lichen, moss and algae only where
the facts say they grow, for as long as they have been growing. The species, their pigments and rates are the setting
pack's (Overstory.World.GrowthPack); here only where and how long.

Each function takes per-vertex arrays and returns arrays, numpy only.
"""

import numpy as np

# How long after a surface was bare (built, relaid, cleaned) the first lichen shows, in years (the map lichen's own
# rate is the pack's: about 0.7 mm a year on this coast).
LICHEN_DELAY = 12
# Feet kill growth fast: no plot kept half its cover after 200 passes (secondary, docs/research/stone.md). Traffic
# here is 0 (never trodden) to 1 (the busiest line).


def lichen_years(years_bare, traffic, exposed=None):
    """The years lichen has grown at each point: from a few years after the surface was bare, where it is quiet;
    nothing on a busy line. exposed (0 to 1, optional): how open the surface is to air and light (lichen wants both;
    it thins in a dark, damp corner where moss and algae take over). Returned over 200, as the shaders read it."""
    quiet = (1.0 - np.clip(traffic, 0.0, 1.0)) ** 1.5
    if exposed is not None:
        quiet = quiet * (0.35 + 0.65 * np.clip(exposed, 0.0, 1.0))
    return np.clip(np.clip(years_bare - LICHEN_DELAY, 0, None) * quiet / 200.0, 0.0, 1.0)


def moss(damp, traffic, years_bare, sheltered=None):
    """Moss: where the surface stays damp (a joint, an inside corner, a wall's foot, a north face), is not trodden,
    and has had the years to fill in (about sixty to be full). sheltered (optional, 0 to 1) adds where the town or a
    tree shades it (the shader also reads the sky map, so this is for shelter the generator knows of itself).
    0 to 1."""
    m = np.clip(damp, 0.0, 1.0)
    if sheltered is not None:
        m = m * (0.7 + 0.5 * np.clip(sheltered, 0.0, 1.0))
    return np.clip(m * (1.0 - 0.85 * np.clip(traffic, 0.0, 1.0)) * np.minimum(np.asarray(years_bare, float) / 60.0, 1.0), 0.0, 1.0)


# ---- on rock: the knuckle and the walls (interface-growth-rock.md) ----------------------------------------------------

import json
import os

_PACK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "packs", "stavanger-1989", "growth.json")


def pack(path=None):
    """The setting pack's growth data (packs/<pack>/growth.json): on_rock's rules, the painted values, the tufts."""
    with open(path or _PACK) as f:
        return json.load(f)


def _ramp(x, a, b):
    """0 at a, 1 at b (either way round), clipped."""
    return np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)


def on_rock(points, normals, sky, foot, joint, years_bare, rules=None):
    """Lichen and moss on a rock's or a dry wall's vertices, from what the rock knows of each (per-vertex arrays):
    points (street m, z up), normals (unit, z up), sky (0 to 1, the sky it sees), foot (m over the ground it stands
    in), joint (m to the nearest crack or bed of its own jointing, large where none), and years_bare (the fact: how
    long since it was bare, a number or an array). Lichen on the open, rain-washed tops and sloping faces, thickest
    at the crest, none under an overhang or in the damp foot; moss in the foot, in the joints and on low north faces
    that see little sky. Returns (lichen years / 200, moss 0 to 1), the rock's UV4.y and UV5.x. The numbers are the
    pack's (growth.json, rock)."""
    R = rules or pack()["rock"]
    n = np.asarray(normals, float)
    nz = n[:, 2]
    sky = np.clip(np.asarray(sky, float), 0.0, 1.0)
    foot = np.asarray(foot, float)
    joint = np.asarray(joint, float)
    years = np.broadcast_to(np.asarray(years_bare, float), nz.shape)

    # (rain-washed and open: none under an overhang, none in the damp foot or inside a joint)
    washed = _ramp(nz, R["overhang"], R["fullRain"]) * _ramp(foot, *R["footLichen"]) * (joint > R["jointLip"])

    upright = 1.0 - np.abs(nz)
    north = np.clip(n[:, 1], 0.0, 1.0) * upright
    damp = np.maximum.reduce([
        R["footMossMax"] * (1.0 - _ramp(foot, *R["footMoss"])),
        R["jointMossMax"] * (1.0 - _ramp(joint, *R["jointMoss"])),
        R["northMossMax"] * north * _ramp(sky, R["northShade"][0], R["northShade"][1]),
    ])
    m = moss(damp, 0.0, years)
    lichen = lichen_years(years, 0.0, sky ** R["skyPower"]) * washed * (1.0 - R["mossOverLichen"] * m)
    return lichen, m


# ---- tufts: the heath above E, the weeds in D's yard (place_tufts) ---------------------------------------------------

def _value_noise(key, x, y, scale):
    """A seeded value noise at points (arrays, m) on a lattice scale m across: smooth, 0 to 1."""
    import hashing as HS
    gx, gy = np.asarray(x, float) / scale, np.asarray(y, float) / scale
    ix, iy = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def at(i, j):
        return np.array([HS.unit(HS.h(*key, int(a), int(b))) for a, b in zip(np.ravel(i), np.ravel(j))]).reshape(np.shape(i))
    a, b, c, d = at(ix, iy), at(ix + 1, iy), at(ix, iy + 1), at(ix + 1, iy + 1)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _inside(poly, x, y):
    """Even-odd test of points against a polygon [(x, y)]."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    inside = np.zeros(x.shape, bool)
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        cross = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / np.where(y2 != y1, y2 - y1, 1e-12) + x1)
        inside ^= cross
    return inside


def _to_line(line, x, y):
    """Distance of points to a polyline [(x, y)], m."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    best = np.full(x.shape, np.inf)
    for (x1, y1), (x2, y2) in zip(line[:-1], line[1:]):
        dx, dy = x2 - x1, y2 - y1
        t = np.clip(((x - x1) * dx + (y - y1) * dy) / max(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
        best = np.minimum(best, np.hypot(x - (x1 + t * dx), y - (y1 + t * dy)))
    return best


def _cells(key, box, per_sqm):
    """Candidate feet on a jittered grid over a box (x0, y0, x1, y1), one a cell at the habitat's fullest density;
    each cell's draws keyed by its own indices, so a cell never moves when the box does."""
    import hashing as HS
    c = 1.0 / np.sqrt(per_sqm)
    x0, y0, x1, y1 = box
    rows = []
    for iy in range(int(np.floor(y0 / c)), int(np.ceil(y1 / c))):
        for ix in range(int(np.floor(x0 / c)), int(np.ceil(x1 / c))):
            S = HS.Stream(*key, ix, iy)
            rows.append(((ix + S.random()) * c, (iy + S.random()) * c, S.random(), S.random(), S.random(), S.random(),
                         S.random(), S.random(), S.random(), S.random(), S.random()))
    return np.array(rows, float).reshape(-1, 11)


def place_tufts(where, ground, footprints, steps, heath_above, seed, rules=None, variants=4):
    """Where the tufts stand, from the record (ground_history: heath above E since 1958, weeds in D's yard since 1986)
    and the extents it lacks (fixtures/lt1-corner-growth.json: where): seeded feet on a jittered grid, thinned into
    patches by a seeded field (habitats' clump), each a species by the habitat's mix (willowherb in stands along a
    yard's walls and lip; the path's walked middle bare), its variant, turn, size, lean, and its rank (which stay as
    the far ones thin) and hue (one clump from the next) as seeded texture. ground(x, y): the ground's height (m);
    footprints: houses' corners [(x, y)]; steps: lines [(x, y)] the heath stays off; heath_above (m).

    Returns rows (species, variant, habitat, x, y, z, turn, scale, lean x, lean y, rank, hue) and each habitat's
    area (m²)."""
    T = (rules or pack())["tufts"]
    H = T["habitats"]
    species = list(T["species"])
    out, area = [], {}

    def emit(hab, pts, pick, size=None):
        for k, p in enumerate(pts):
            sp = pick[k]
            if sp is None:
                continue
            z = float(ground(p[0], p[1]))
            s = (0.85 + 0.3 * p[5]) * (1.0 if size is None else size[k])
            out.append((sp, int(p[6] * variants) % variants, hab, round(p[0], 3), round(p[1], 3), round(z, 3),
                        round(2 * np.pi * p[4], 4), round(s, 3), round((p[7] - 0.5) * 0.16, 4),
                        round((p[8] - 0.5) * 0.16, 4), round(p[9], 4), round(p[10], 4)))

    def patches(hab, P):
        n = _value_noise((seed, "growth clump", hab), P[:, 0], P[:, 1], H[hab]["clump"][0])
        keep = (1.0 - H[hab]["clump"][1]) + H[hab]["clump"][1] * np.clip((n - 0.3) / 0.4, 0.0, 1.0)
        return P[P[:, 2] < keep]

    def mix_pick(hab, u):
        m = H[hab]["mix"]
        names, w = list(m), np.cumsum(list(m.values()))
        return [names[min(int(np.searchsorted(w, x * w[-1], side="right")), len(names) - 1)] for x in u]

    # D's yard: long grass over it all, willowherb in stands along its walls and its lip
    import hashing as HS
    Y, Pth = where["yard"], where["path"]
    poly = Y["polygon"]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    P = _cells((seed, "growth tuft", "yard"), (min(xs), min(ys), max(xs), max(ys)), H["yard"]["perSqm"])
    P = P[_inside(poly, P[:, 0], P[:, 1])]
    P = P[_to_line(Pth["line"], P[:, 0], P[:, 1]) > 0.5 * Pth["width"] + 0.1]
    z = np.array([ground(x, y) for x, y in P[:, :2]])
    P = P[(z >= Y["onGround"][0]) & (z <= Y["onGround"][1])]
    G = _cells((seed, "area", "yard"), (min(xs), min(ys), max(xs), max(ys)), 16.0)
    area["yard"] = float(np.sum(_inside(poly, G[:, 0], G[:, 1]))) / 16.0
    # the rankest grass stands at the untrodden lip: it is never thinned there, and stands taller toward it
    reach, most, rank = H["yard"]["lip"]
    near = _to_line(Y["lip"], P[:, 0], P[:, 1]) < reach
    kept = patches("yard", P)
    P = np.concatenate([kept, P[near & ~np.isin(P[:, 0] * 1e4 + P[:, 1], kept[:, 0] * 1e4 + kept[:, 1])]])
    # and a row of it along the lip itself, so its edge is a fringe, never a dotted line
    step, inset = H["yard"]["lipRow"]
    lip = np.array(Y["lip"], float)
    row = []
    for j, (a, b) in enumerate(zip(lip[:-1], lip[1:])):
        ab = b - a
        L = float(np.hypot(*ab))
        side = np.array([-ab[1], ab[0]]) / max(L, 1e-9)
        for k in range(int(np.ceil(L / step))):
            S = HS.Stream(seed, "growth lip row", "yard", j, k)
            t = (k + S.random()) * step / L
            off = S.uniform(inset[0], inset[1])
            for sgn in (1.0, -1.0):
                q = a + min(t, 1.0) * ab + sgn * off * side
                if _inside(poly, np.array([q[0]]), np.array([q[1]]))[0]:
                    row.append([q[0], q[1]] + [S.random() for _ in range(9)])
                    break
    if row:
        R = np.array(row, float)
        zr = np.array([ground(x, y) for x, y in R[:, :2]])
        R = R[(zr >= Y["onGround"][0]) & (zr <= Y["onGround"][1])
              & (_to_line(Pth["line"], R[:, 0], R[:, 1]) > 0.5 * Pth["width"] + 0.1)]
        P = np.concatenate([P, R])
    dlip = _to_line(Y["lip"], P[:, 0], P[:, 1])
    tall = 1.0 + (rank - 1.0) * np.clip(1.0 - dlip / reach, 0.0, 1.0)
    edge = np.min([_to_line(e, P[:, 0], P[:, 1]) for e in Y["walls"] + [Y["lip"]]], axis=0)
    stand = _value_noise((seed, "growth stand", "yard"), P[:, 0], P[:, 1], 1.6)
    w = H["yard"]["mix"]["willowherb"]
    herb = P[:, 3] < np.clip(w * 4.0 * np.clip((stand - 0.45) / 0.2, 0, 1) * np.clip(1.6 - edge / 1.2, 0, 1), 0, 0.95)
    n0 = len(out)
    emit("yard", P, ["willowherb" if hb else "yardGrass" for hb in herb], size=list(tall))
    # the long grass at the lip falls out over it (nothing holds it up on the open side)
    for k in range(n0, len(out)):
        r = list(out[k])
        if r[0] != "yardGrass":
            continue
        best, to = np.inf, None
        for a, b in zip(lip[:-1], lip[1:]):
            ab = b - a
            t = float(np.clip(np.dot([r[3], r[4]] - a, ab) / max(np.dot(ab, ab), 1e-12), 0.0, 1.0))
            q = a + t * ab
            dq = float(np.hypot(q[0] - r[3], q[1] - r[4]))
            if dq < best:
                best, to = dq, (q - [r[3], r[4]]) / max(dq, 1e-6)
        if best < reach:
            lean = most * (1.0 - best / reach)
            r[8] = round(r[8] + lean * float(to[0]), 4)
            r[9] = round(r[9] + lean * float(to[1]), 4)
            out[k] = tuple(r)

    # the path to D's door: grassing over, its walked middle bare
    lx, ly = [p[0] for p in Pth["line"]], [p[1] for p in Pth["line"]]
    hw = 0.5 * Pth["width"]
    P = _cells((seed, "growth tuft", "path"), (min(lx) - hw, min(ly) - hw, max(lx) + hw, max(ly) + hw), H["path"]["perSqm"])
    d = _to_line(Pth["line"], P[:, 0], P[:, 1])
    P, d = P[d < hw], d[d < hw]
    z = np.array([ground(x, y) for x, y in P[:, :2]])
    ok = (z >= Pth["onGround"][0]) & (z <= Pth["onGround"][1]) & (d > Pth["walked"] * hw)
    P, d = P[ok], d[ok]
    area["path"] = 2.0 * hw * float(np.sum(np.hypot(np.diff(lx), np.diff(ly))))
    P = patches("path", P)
    d = _to_line(Pth["line"], P[:, 0], P[:, 1])
    emit("path", P, ["pathGrass"] * len(P), size=list(0.7 + 0.4 * (d / hw)))

    # the heath above E: heather the matrix, hair-grass in its gaps, a juniper here and there
    Hh = where["heath"]
    P = _cells((seed, "growth tuft", "heath"), Hh["box"], H["heath"]["perSqm"])
    z = np.array([ground(x, y) for x, y in P[:, :2]])
    ok = z > heath_above
    for fp in footprints:
        fx, fy = [p[0] for p in fp], [p[1] for p in fp]
        ok &= ~((P[:, 0] > min(fx) - Hh["clear"]) & (P[:, 0] < max(fx) + Hh["clear"])
                & (P[:, 1] > min(fy) - Hh["clear"]) & (P[:, 1] < max(fy) + Hh["clear"]))
    for ln in steps:
        ok &= _to_line(ln, P[:, 0], P[:, 1]) > Hh["steps"]
    G = _cells((seed, "area", "heath"), Hh["box"], 1.0)
    gz = np.array([ground(x, y) for x, y in G[:, :2]])
    area["heath"] = float(np.sum(gz > heath_above))
    P = patches("heath", P[ok])
    gaps = _value_noise((seed, "growth gaps", "heath"), P[:, 0], P[:, 1], 2.4)
    pick = []
    for k, p in enumerate(P):
        if p[3] < H["heath"]["mix"]["juniper"]:
            pick.append("juniper")
        else:
            grass = H["heath"]["mix"]["heathGrass"] * (0.4 + 1.6 * gaps[k])
            pick.append("heathGrass" if p[10] < grass else "heather")
    emit("heath", P, pick)
    return out, area


# ---- a place's ground cover: one community over the whole ground (the rock kit's stage 6, the Holm tip) -------------

class Field:
    """A seeded value noise over the ground (m), 0 to 1, vectorised (a table of 4096 seeded values on an integer-hashed
    lattice), so the tufts and the ground's map under them read one field."""

    def __init__(self, *key):
        import hashing as HS
        S = HS.Stream(*key, "field")
        self.t = np.array([S.random() for _ in range(4096)])

    def __call__(self, x, y, scale):
        gx, gy = np.asarray(x, float) / scale, np.asarray(y, float) / scale
        ix, iy = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
        fx, fy = gx - ix, gy - iy
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

        def at(i, j):
            return self.t[((i * 73856093) ^ (j * 19349663)) & 4095]
        return (at(ix, iy) * (1 - fx) + at(ix + 1, iy) * fx) * (1 - fy) + (at(ix, iy + 1) * (1 - fx) + at(ix + 1, iy + 1) * fx) * fy


def community_patch(key, x, y, hab):
    """Where a community's patches stand (its `patch`: heather where the till is thinnest): 1 inside, 0 outside, the
    edge crisp (softened over edgeM, in metres), never a smeared blend (land-rock-and-water.md, Texturing the ground):
    a seeded field over cellM, two octaves and a ragged third (`rag`, over a seventh of the cell), cut at the share of
    the ground the patches take; the field over its own slope is the distance to the edge."""
    Pt = hab.get("patch")
    if not Pt:
        return np.zeros(np.shape(x))
    F = Field(*key, "patch")
    c, rg = Pt["cellM"], Pt.get("rag", 0.0)
    n = lambda a, b: (0.72 * F(a, b, c) + 0.28 * F(a + 31.7, b - 17.3, c / 2.7)  # noqa: E731
                      + rg * F(a - 7.9, b + 23.1, c / 7.0)) / (1.0 + rg)
    g = np.mgrid[0:96, 0:96].reshape(2, -1) * (c * 0.37)
    cut = float(np.quantile(n(g[0], g[1]), 1.0 - Pt["share"]))
    x, y = np.asarray(x, float), np.asarray(y, float)
    h = 0.01
    v = n(x, y)
    slope = np.hypot(n(x + h, y) - n(x - h, y), n(x, y + h) - n(x, y - h)) / (2 * h)
    return np.clip(0.5 + (v - cut) / np.maximum(slope, 1e-6) / Pt["edgeM"], 0.0, 1.0)


def place_community(key, box, name, keep=None, rules=None, variants=4):
    """One community's tufts over a box (x0, y0, x1, y1, m): seeded feet on a jittered grid at its fullest density,
    thinned into clusters (`clump`), each the sward's species by its `mix` (hair-grass in drifts through it) or, inside
    a patch, the patch's (scaled by its `scale`: heather grazed low); keep(x, y) drops feet the place rules out (a
    house, a rock). Returns rows as place_tufts' (species, variant, habitat, x, y, z, turn, scale, lean x, lean y,
    rank, hue) and each foot's patch value."""
    T = (rules or pack())["tufts"]
    H = T["habitats"][name]
    P = _cells((*key, "growth tuft", name), box, H["perSqm"])
    if keep is not None:
        P = P[keep(P[:, 0], P[:, 1])]
    F = Field(*key, "clump", name)
    c0, c1 = H["clump"]
    # thinned into clusters, but a patch that grows as one mat (its `full`: heather) keeps every foot
    full = community_patch(key, P[:, 0], P[:, 1], H) > 0.5 if H.get("patch", {}).get("full") else np.zeros(len(P), bool)
    P = P[full | (P[:, 2] < (1.0 - c1) + c1 * np.clip((F(P[:, 0], P[:, 1], c0) - 0.3) / 0.4, 0.0, 1.0))]
    patch = community_patch(key, P[:, 0], P[:, 1], H)
    drift = Field(*key, "drift", name)(P[:, 0], P[:, 1], 2.4)

    def pick(mix, u, boost=None):
        names = list(mix)
        w = np.array([mix[s] for s in names], float)
        out = []
        for k, x in enumerate(u):
            ww = w.copy()
            if boost is not None and "heathGrass" in names:
                ww[names.index("heathGrass")] *= boost[k]
            cw = np.cumsum(ww)
            out.append(names[min(int(np.searchsorted(cw, x * cw[-1], side="right")), len(names) - 1)])
        return out
    sward = pick(H["mix"], P[:, 3], 0.4 + 1.6 * drift)
    inpatch = pick(H["patch"]["mix"], P[:, 3]) if H.get("patch") else sward
    rows = []
    for k, p in enumerate(P):
        sp = inpatch[k] if patch[k] > 0.5 else sward[k]
        s = (0.85 + 0.3 * p[5]) * (H["patch"].get("scale", 1.0) if patch[k] > 0.5 and sp != "turf" else 1.0)
        rows.append((sp, int(p[6] * variants) % variants, name, round(p[0], 3), round(p[1], 3), 0.0,
                     round(2 * np.pi * p[4], 4), round(s, 3), round((p[7] - 0.5) * 0.16, 4),
                     round((p[8] - 0.5) * 0.16, 4), round(p[9], 4), round(p[10], 4)))
    return rows, patch


def lin(hexrgb):
    """sRGB hex as linear RGB."""
    c = np.array([int(hexrgb[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def ground_map(key, box, px, name, rules=None, wind=0.0):
    """The ground under a community, top-down (its `ground`): the sward's colour, drier toward `dry` over a broad field
    (`dryShare` of the ground the drier), the patches' where they stand (the same crisp field the tufts read), one
    broad variation over varyM, the clumps' light and shade over clumpM (the turf's own tops and hollows, a painted mark
    each) and a fine grain stretched along the wind's bearing (the turf lies with it) over grainM [across, along]:
    linear RGB (px[1], px[0], 3), row 0 at box's y0."""
    H = (rules or pack())["tufts"]["habitats"][name]
    G = H["ground"]
    x0, y0, x1, y1 = box
    xs = x0 + (np.arange(px[0]) + 0.5) * (x1 - x0) / px[0]
    ys = y0 + (np.arange(px[1]) + 0.5) * (y1 - y0) / px[1]
    X, Y = np.meshgrid(xs, ys)
    m = community_patch(key, X, Y, H)[..., None]
    F = Field(*key, "ground", name)
    sward = lin(G["sward"])
    if "dry" in G:
        d = 0.7 * F(X + 40.1, Y - 3.7, G["varyM"] * 1.6) + 0.3 * F(X - 5.5, Y + 19.9, G["varyM"] / 1.7)
        cut = float(np.quantile(d, 1.0 - G["dryShare"]))
        t = np.clip((d - cut) / 0.12 + 0.5, 0.0, 1.0)[..., None]
        sward = sward * (1 - t) + lin(G["dry"]) * t
    out = sward * (1 - m) + lin(G["patch"]) * m
    v = 0.65 * F(X, Y, G["varyM"]) + 0.35 * F(X - 11.3, Y + 7.1, G["varyM"] / 2.3)
    out = out * (1.0 + G["vary"] * 2.0 * (v - 0.5))[..., None]
    b = np.radians(wind)
    u, w = X * np.sin(b) + Y * np.cos(b), X * np.cos(b) - Y * np.sin(b)
    if "clumps" in G:
        # a clump's mark is a short stroke laid with the wind (clumpM across, three times that along)
        q = F(w / G["clumpM"] + 2.9, u / (3.0 * G["clumpM"]) - 8.3, 1.0)
        out = out * (1.0 + G["clumps"] * 2.0 * (np.clip((q - 0.5) * 1.8, -0.5, 0.5)))[..., None]
    a, l = G["grainM"]
    g = 0.6 * F(w / a, u / l, 1.0) + 0.4 * F(2 * w / a + 3.3, 2 * u / l - 5.9, 1.0)
    return out * (1.0 + G["grain"] * 2.0 * (g - 0.5))[..., None], m[..., 0]
