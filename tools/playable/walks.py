"""The walk's scripted walks (LT1g, the walk, W4), written for the player's WalkScript from the proxies' data.

    python3 tools/playable/walks.py [proxies.json] [out dir]

Each walk follows the layout's own ways: the door's stand point, the lane's centreline, the gully's flights along
their walking lines (stone_gully.json's breaklines, a point a tread, taken about every metre), and the door path to
the next door. Nothing in it is invented: a waypoint off a centreline is only the step out of a door, or the side of a
door path where the path's centreline hugs its house's front closer than a walker's shoulders.

keys.walk: the keys as a script (views, takeover, V, the free camera).

a-e-a.walk: from A's door (104) along the Row, up Gully Steps to E's door (304) at a person's pace, and back
at a brisk one, with stills at the door, the flight's foot, the Landing, the top and E's door.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PROXIES = os.path.join(ROOT, "unity", "Assets", "Experiments", "LT1", "Playable", "proxies.json")
OUT = os.path.join(HERE, "walks")
SHOULDER = 0.3 + 0.2   # the walker's radius, and room


def pts3(flat):
    return [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]


def thin(pts, every=1.0):
    """Points along a line about every metre, its ends and its turns kept."""
    out = [pts[0]]
    run = 0.0
    for a, b in zip(pts, pts[1:]):
        run += math.hypot(b[0] - a[0], b[1] - a[1])
        if run >= every:
            out.append(b)
            run = 0.0
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def main(src, out_dir):
    d = json.load(open(src))
    ways = {w["name"]: w for w in d["ways"]}
    doors = {x["id"]: x for x in d["doors"]}
    houses = {p["id"]: p for p in d["proxies"] if p["kind"] == "house"}
    walking = {w["flight"]: pts3(w["pts"]) for w in d["walking"]}
    a_door, e_door = doors["bld/104/door"], doors["bld/304/door"]
    gully = pts3(ways["Gully Steps"]["pts"])
    to_e = pts3(ways["the way to E (304, 1826)"]["pts"])

    def outward(door, dist):
        """A point dist out from a door, square to its front (the front faces local -v)."""
        a = math.radians(door["a"])
        nx, ny = math.sin(a), -math.cos(a)
        return door["x"] + nx * dist, door["y"] + ny * dist

    # the door path to E hugs E's front: walk it on its open side, a shoulder off the face
    e = houses["bld/304"]
    ea = math.radians(e["a"])
    nx, ny = math.sin(ea), -math.cos(ea)                       # out of E's front
    fx = e["x"] + nx * (e["w"] / 2)                           # a point on E's front
    fy = e["y"] + ny * (e["w"] / 2)

    def off_face(x, y):
        dist = (x - fx) * nx + (y - fy) * ny
        k = max(0.0, SHOULDER - dist)
        return x + nx * k, y + ny * k

    up = []
    up.append(("start", a_door["x"], a_door["y"], *outward(a_door, 5.0)))
    up.append(("shot", "a-door"))
    up.append(("to", *outward(a_door, 2.0)))
    # along the Row to the foot of Gully Steps, then up its lane to the flight
    row_y = outward(a_door, 2.0)[1]
    up.append(("to", gully[0][0], row_y))
    for p in gully[1:3]:
        up.append(("to", p[0], p[1]))
    f0 = thin(walking["st-gully/fl-0"])
    up.append(("to", f0[0][0], f0[0][1] - 0.8))
    up.append(("shot", "foot"))
    up.extend(("to", p[0], p[1]) for p in f0)
    up.append(("shot", "landing"))
    f1 = thin(walking["st-gully/fl-1"])
    up.extend(("to", p[0], p[1]) for p in f1)
    up.append(("shot", "top"))
    up.append(("to", gully[-1][0], gully[-1][1]))
    for p in to_e[:-1]:
        up.append(("to", *off_face(p[0], p[1])))
    # along E's front to its door
    ex, ey = off_face(*outward(e_door, 0.0))
    sx, sy = off_face(*to_e[0][:2])
    up.append(("to", sx + (ex - sx) * 0.7, sy + (ey - sy) * 0.7))
    up.append(("to", e_door["x"], e_door["y"]))
    up.append(("look", e_door["x"] - nx * 1.0, e_door["y"] - ny * 1.0, e_door["z"] + 1.2))
    up.append(("wait", 1.0))
    up.append(("shot", "e-door"))
    up.append(("look", "off"))

    # back the same way, brisk, the door path and the flights reversed
    moves = [c for c in up if c[0] == "to"]
    back = [("mark", "back"), ("pace", "brisk")]
    back.extend(("to", c[1], c[2]) for c in reversed(moves[:-1]))
    back.append(("to", *outward(a_door, 0.3)))     # A's doorstep as drawn at 1989 (CheckProxies: its sill 0.1 m out)
    back.append(("shot", "a-door-again"))
    lines = ["# A's door (104) to E's (304) and back, as tools/playable/walks.py writes it from proxies.json",
             f"# proxies: clay {d['source']['clay'][:7]}, heart_layout {d['source']['heart_layout'][:8]}, stair {d['source']['stair'][:8]}",
             "pace walk"]
    for c in up + back + [("end",)]:
        lines.append(" ".join(c[0:1] + tuple(f"{v:.3f}" if isinstance(v, float) else str(v) for v in c[1:])))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "a-e-a.walk")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    # the keys' walk: the views, the takeover from each, V and the free camera (the player takes no keys from a shell)
    keys = ["# the keys as a script: views 1 to 9 held, taken over (walking at eye height, else flying), V both ways",
            "pace walk",
            f"start {a_door['x']:.3f} {a_door['y']:.3f} {outward(a_door, 5.0)[0]:.3f} {outward(a_door, 5.0)[1]:.3f}",
            "expect walk", "view 1", "expect held", "takeover", "expect walk", "shot keys-1-walk",
            "view 5", "expect held", "takeover", "expect free", "shot keys-5-free",
            "free", "expect walk", "wait 1", "shot keys-5-landed",
            "free", "expect free", "fly 2 -20", "fly 2 10", "shot keys-flown", "mark flown"]
    for v in (2, 6, 7, 8, 9):
        keys += [f"view {v}", "expect held", "takeover", "expect walk", "wait 0.5", f"shot keys-{v}-walk"]
    keys += ["view 3", "takeover", "mark the street view (3)", "view 4", "takeover", "mark into12 (4)", "end"]
    with open(os.path.join(out_dir, "keys.walk"), "w") as f:
        f.write("\n".join(keys) + "\n")
    n = sum(1 for c in up + back if c[0] == "to")
    length = 0.0
    prev = (up[0][1], up[0][2])
    for c in up + back:
        if c[0] == "to":
            length += math.hypot(c[1] - prev[0], c[2] - prev[1])
            prev = (c[1], c[2])
    print(f"[walks] {path}: {n} points, {length:.0f} m in plan")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else PROXIES, sys.argv[2] if len(sys.argv) > 2 else OUT)
