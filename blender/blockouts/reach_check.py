"""Every place reachable, every lane joined: a check on the heart's layout.

    python blender/blockouts/reach_check.py   (needs numpy)

1. Every building has its door on a way: the middle of its front lies within reach (3 m) of a street, lane,
   stair, path, quay, square, the Landing or a small place. Landmarks set in a square or a yard count when
   they stand in it.
2. Nothing stands in a way: no building, yard, wall or shed reaches into a street, lane, stair or path, and no
   retaining wall the ground needs (heart_layout.ground_walls) crosses one.
3. Every way joins the network: an end of each lane lies on (within 3 m of) another lane, a square or the
   water's edge where boats come in; and the whole network is one piece, reached from Harbour Row.

Prints every failure. Exit status 1 if there is any.
"""

import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import centre_land as L  # noqa: E402
import heart_layout as H  # noqa: E402

REACH = 3.0


def seg_dist(px, py, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy or 1e-9)))
    return math.hypot(px - (x1 + dx * t), py - (y1 + dy * t))


def lane_dist(lane, x, y):
    pts = [(p[0], p[1]) for p in lane["pts"]]
    return min(seg_dist(x, y, a, b) for a, b in zip(pts, pts[1:])) - lane["width"] / 2


def place_polys():
    return [("the Landing", H.LANDING), ("Market Square", H.MARKET_SQUARE)] + [(n, p) for n, p, _ in H.SMALL_PLACES]


def poly_dist(poly, x, y):
    inside = L._inside(poly, np.array([x]), np.array([y]))[0]
    if inside:
        return -1.0
    return min(seg_dist(x, y, a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


def door(b):
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    u, v = b["w"] / 2, -0.4
    return b["ox"] + u * c - v * s, b["oy"] + u * s + v * c


def check(report=None):
    report = {} if report is None else report
    failures = []
    places = place_polys()
    for b in H.BUILDINGS:
        if b["name"] in H.EXEMPT:
            continue
        x, y = door(b)
        d_lane = min(lane_dist(l, x, y) for l in H.LANES)
        d_place = min(poly_dist(p, x, y) for _, p in places)
        if min(d_lane, d_place) > REACH:
            failures.append(f"no way to the door of {b['name']} at ({x:.0f}, {y:.0f}): nearest way {min(d_lane, d_place):.1f} m")
    # nothing stands in a way
    ways = [l for l in H.LANES if l["kind"] != "mole"]

    def in_way(pts, what):
        for l in ways:
            d = min(lane_dist(l, x, y) for x, y in pts)
            if d < -0.1:
                failures.append(f"{what} stands {-d:.1f} m into {l['name']}")
                return

    def cover(poly, n=16):
        """Points over a polygon: its edges and a grid inside, so a lane passing through is seen."""
        pts = [(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t) for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1])
               for t in np.linspace(0.0, 1.0, n, endpoint=False)]
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        gx, gy = np.meshgrid(np.linspace(min(xs), max(xs), n), np.linspace(min(ys), max(ys), n))
        m = L._inside(poly, gx.ravel(), gy.ravel())
        return pts + list(zip(gx.ravel()[m], gy.ravel()[m]))

    for b in H.BUILDINGS:
        own = f"the way to {b['name']}"  # a door path ends at its own door
        for l in ways:
            if l["name"] == own:
                continue
            x0, y0, x1, y1 = l.setdefault("_box", (min(p[0] for p in l["pts"]) - 20, min(p[1] for p in l["pts"]) - 20,
                                                   max(p[0] for p in l["pts"]) + 20, max(p[1] for p in l["pts"]) + 20))
            if not (x0 < b["ox"] < x1 and y0 < b["oy"] < y1):
                continue
            d = min(lane_dist(l, x, y) for x, y in cover(H.footprint(b, -0.15), 8))
            if d < -0.1:
                failures.append(f"{b['name']} stands {-d:.1f} m into {l['name']}")
                break
    for poly, _ in H.YARDS:
        in_way(cover(poly), "a yard")
    for d in H.DETAILS:
        if d["kind"] in ("wall", "shed"):
            c, s = math.cos(math.radians(d["a"])), math.sin(math.radians(d["a"]))
            in_way([(d["x"] + u * c, d["y"] + u * s) for u in np.linspace(-d["l"] / 2, d["l"] / 2, 9)], f"a {d['kind']} at ({d['x']:.0f}, {d['y']:.0f})")
    # the retaining walls, on the carved ground sampled every 2 m as the build samples it every 1.5 m
    x0, y0, x1, y1 = H.HEART
    GX, GY = np.meshgrid(np.arange(x0, x1 + 1.0, 2.0), np.arange(y0, y1 + 1.0, 2.0), indexing="ij")
    GZ = H.carve(GX, GY, L.heights(GX, GY))

    def ground(x, y):
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return float(L.z_at(x, y))
        u, v = min((x - x0) / 2.0, GX.shape[0] - 1.001), min((y - y0) / 2.0, GX.shape[1] - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        a = GZ[i, j] + (GZ[i + 1, j] - GZ[i, j]) * fu
        b = GZ[i, j + 1] + (GZ[i + 1, j + 1] - GZ[i, j + 1]) * fu
        return float(a + (b - a) * fv)

    walls = H.ground_walls(ground)
    for w in walls:
        fp = H._box(w["x"], w["y"], w["a"], w["l"], w["w"])
        for l in ways:
            into = H.intrusion(fp, l, -0.1)
            if into > 0.0:
                failures.append(f"a retaining wall at ({w['x']:.0f}, {w['y']:.0f}) stands {into:.1f} m into {l['name']}")
                break
    report["walls"] = len(walls)
    # the network: lanes joined at their ends, one piece
    names = [l["name"] for l in H.LANES]
    parent = {n: n for n in names + [n for n, _ in places]}

    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    def join(a, b):
        parent[find(a)] = find(b)

    for la in H.LANES:
        ends = (la["pts"][0],) if la.get("door") else (la["pts"][0], la["pts"][-1])  # a door path ends at its door
        for end in ends:
            joined = False
            for lb in H.LANES:
                if lb is la:
                    continue
                if lane_dist(lb, end[0], end[1]) < REACH:
                    join(la["name"], lb["name"])
                    joined = True
            for pn, poly in places:
                if poly_dist(poly, end[0], end[1]) < REACH:
                    join(la["name"], pn)
                    joined = True
            x0, y0, x1, y1 = H.HEART
            at_edge = min(end[0] - x0, x1 - end[0], end[1] - y0, y1 - end[1]) < 25.0  # it runs on into the town
            if not joined and not at_edge and la["kind"] != "mole":
                failures.append(f"{la['name']} ends nowhere at ({end[0]:.0f}, {end[1]:.0f})")
        # lanes that cross each other part way also join
        for lb in H.LANES:
            if lb is la:
                continue
            if any(lane_dist(lb, p[0], p[1]) < 0.5 for p in la["pts"]):
                join(la["name"], lb["name"])
    root = find("Harbour Row")
    for n in names:
        if find(n) != root:
            failures.append(f"{n} is cut off from Harbour Row")
    return failures


if __name__ == "__main__":
    info = {}
    f = check(info)
    for line in f:
        print("FAIL", line)
    print(f"{len(H.BUILDINGS)} buildings, {len(H.LANES)} ways, {info.get('walls', 0)} retaining walls: {len(f)} failures")
    sys.exit(1 if f else 0)
