"""The ground of the town: a hill rising from the harbour, the bay's sides, and what people cut into it.

natural_z(site, x, y) is the ground before anyone built on it: the yards behind the quay street, a
hill that steepens as it climbs, a gully where water runs down (and where the stepped lane follows
it), the bay's sides rising to headlands, and seeded unevenness that fades out near the street.

Field is a height grid over an area; carve() cuts lanes, the square, house pads and gardens into it,
the way a town is built into a slope. Both the town's growth (grow_town.py) and the export use these
same functions, so a house's base and the ground drawn under it always agree.

Street coordinates in metres: x along the harbour, y up the hill (negative towards the water), z up.
Pure Python, deterministic: noise comes from hashing.h.
"""

import math

from hashing import h, unit


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def noise2(seed, u, v):
    """Smooth value noise, 0..1."""
    i, j = math.floor(u), math.floor(v)
    fu, fv = u - i, v - j
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)

    def c(a, b):
        return unit(h(seed, a, b))

    top = c(i, j) + (c(i + 1, j) - c(i, j)) * fu
    bot = c(i, j + 1) + (c(i + 1, j + 1) - c(i, j + 1)) * fu
    return top + (bot - top) * fv


def natural_z(site, x, y):
    """The ground before building, in metres."""
    s = site
    edge = s["edge"]
    if y < edge:  # the harbour: the bay's floor, or the hills running out as headlands
        d = max(s["bay_x0"] - x, x - s["bay_x1"], 0.0)
        side = s["side_height"] * (1 - (1 - min(1.0, d / s["side_reach"])) ** 2)
        out = min(1.0, (edge - y) / (s["side_reach"] * 1.2))
        return side * (1 - smoothstep(0, 1, out)) - 9.0 * (1 - min(1.0, d / 20.0)) - 4.0
    if y < 0:
        return -0.4  # under the quay street, which draws its own surface
    rise_y = s["yard"]  # the yards behind the quay street stay level
    t = max(0.0, y - rise_y)
    z = s["slope"] * t + s["steepen"] * t * t
    z *= smoothstep(rise_y, rise_y + 6.0, y)
    # the gully: a shallow valley the stream (and the stepped lane) follows
    gx = s["gully_x"]
    z -= s["gully_depth"] * math.exp(-((x - gx) / s["gully_width"]) ** 2) * smoothstep(rise_y + 4, rise_y + 30, y)
    # unevenness, none near the quay street
    n = noise2(s["seed"], x / 60.0, y / 60.0) * 0.65 + noise2(s["seed"] + 7, x / 23.0, y / 23.0) * 0.35
    z += s["rough"] * (n - 0.5) * 2 * smoothstep(rise_y + 2, rise_y + 26, y)
    # the bay's sides rise to the hills
    d = max(s["bay_x0"] - x, x - s["bay_x1"], 0.0)
    side = s["side_height"] * (1 - (1 - min(1.0, d / s["side_reach"])) ** 2)
    return max(z, side) if y >= rise_y else max(-0.02, side * smoothstep(0, 30, d))


class Field:
    """A height grid: z[j][i] at (x0 + i*step, y0 + j*step)."""

    def __init__(self, site, x0, y0, x1, y1, step):
        self.x0, self.y0, self.step = x0, y0, step
        self.nx = int(round((x1 - x0) / step)) + 1
        self.ny = int(round((y1 - y0) / step)) + 1
        self.z = [[natural_z(site, x0 + i * step, y0 + j * step) for i in range(self.nx)] for j in range(self.ny)]

    def points(self):
        for j in range(self.ny):
            for i in range(self.nx):
                yield i, j, self.x0 + i * self.step, self.y0 + j * self.step

    def sample(self, x, y):
        """Bilinear height at a point inside the grid."""
        u = (x - self.x0) / self.step
        v = (y - self.y0) / self.step
        i = min(max(int(math.floor(u)), 0), self.nx - 2)
        j = min(max(int(math.floor(v)), 0), self.ny - 2)
        fu, fv = u - i, v - j
        a = self.z[j][i] + (self.z[j][i + 1] - self.z[j][i]) * fu
        b = self.z[j + 1][i] + (self.z[j + 1][i + 1] - self.z[j + 1][i]) * fu
        return a + (b - a) * fv


# -- geometry helpers -----------------------------------------------------------------------------------


def nearest_on_polyline(pts, x, y):
    """(distance, index of segment, t along it, point) of the nearest point on a 2D polyline."""
    best = (1e18, 0, 0.0, pts[0])
    for k in range(len(pts) - 1):
        ax, ay = pts[k][0], pts[k][1]
        bx, by = pts[k + 1][0], pts[k + 1][1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1e-9
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        px, py = ax + dx * t, ay + dy * t
        d = math.hypot(x - px, y - py)
        if d < best[0]:
            best = (d, k, t, (px, py))
    return best


def in_quad(q, x, y):
    """Whether (x, y) lies inside a convex quad given as four (x, y) corners in order."""
    sign = 0
    for k in range(4):
        ax, ay = q[k]
        bx, by = q[(k + 1) % 4]
        c = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if abs(c) < 1e-9:
            continue
        s = 1 if c > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True


def carve(field, town):
    """Cut the town into the ground: lanes level across, embankments below them, the square, and each
    house's pad and front garden flat at the house's base. Cuts above a lane are held by walls (drawn
    from the town's walls), so the ground there stays as it was."""
    lanes = town["lanes"]
    stairs = town.get("stairs", [])
    for i, j, x, y in field.points():
        z = field.z[j][i]
        for st in stairs:  # stepped lanes: their own slope, banks on both sides
            pts = st["points"]
            d, k, t, _ = nearest_on_polyline([p[:2] for p in pts], x, y)
            hw = st["width"] / 2 + 0.4
            if d > hw + 12:
                continue
            sz = pts[k][2] + (pts[k + 1][2] - pts[k][2]) * t
            if d <= hw:
                z = sz
            else:
                z = min(max(z, sz - (d - hw) * 0.7), sz + (d - hw) * 0.9)
        for lane in lanes:
            pts = lane["points"]
            d, k, t, _ = nearest_on_polyline(pts, x, y)
            hw = lane["width"] / 2
            if d > hw + 14:
                continue
            lz = lane["z"]
            # which side of the lane: downhill is towards the harbour (the lane's normal)
            ax, ay = pts[k][0], pts[k][1]
            bx, by = pts[k + 1][0], pts[k + 1][1]
            side = (bx - ax) * (y - ay) - (by - ay) * (x - ax)  # > 0 to the left of travel (uphill, as lanes run in +x)
            if d <= hw:
                z = lz
            elif side < 0 and z < lz:  # below the lane: an embankment, about 30 degrees
                z = max(z, lz - (d - hw) * 0.6)
        for sq in town.get("squares", []):
            if in_quad(sq["corners"], x, y):
                z = sq["z"]
        for pad in town.get("pads", []):
            if in_quad(pad["corners"], x, y):
                z = min(z, pad["z"]) if pad["kind"] == "house" else pad["z"]
            elif pad["kind"] == "house":
                # behind and beside a house the cut eases back into the slope
                cx = sum(p[0] for p in pad["corners"]) / 4
                cy = sum(p[1] for p in pad["corners"]) / 4
                half = max(math.hypot(p[0] - cx, p[1] - cy) for p in pad["corners"])
                dd = math.hypot(x - cx, y - cy) - half
                if 0 < dd < 6 and z > pad["z"]:
                    z = min(z, pad["z"] + dd * 0.9)
        field.z[j][i] = z
