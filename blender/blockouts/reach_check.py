"""Every place reachable, every lane joined: a check on the heart's layout.

    python blender/blockouts/reach_check.py   (needs numpy)

1. Every building has its door on a way: the middle of its front lies within reach (3 m) of a street, lane,
   stair, path, quay, square, the Landing or a small place. Landmarks set in a square or a yard count when
   they stand in it.
2. Every way joins the network: an end of each lane lies on (within 3 m of) another lane, a square or the
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


def check():
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
    f = check()
    for line in f:
        print("FAIL", line)
    print(f"{len(H.BUILDINGS)} buildings, {len(H.LANES)} ways: {len(f)} failures")
    sys.exit(1 if f else 0)
