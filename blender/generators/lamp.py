"""Street lamps, by the era they were put up.

build(params, seed) makes one lamp standing at the origin, pivot at the foot of the post.
Poles reach their arm out over the street, towards the front (-y). The glowing parts use
the palette's lamp swatches, so Unity lights them only when the scene's light turns the
lamps on; each lamp's light point is returned with it for Unity to place a light there.

- post-1934: a cast-iron post painted dark green, with a four-sided lantern (warm incandescent light).
- pole-1965: a galvanised pole with a bent arm and a bell head (cool mercury light).
- pole-1983: the same pole with a flat head and a lens below (orange sodium light).
"""

import math

from kit import Builder, Frame, WORLD

VARIANTS = {
    "post-1934": dict(kind="post", light="lamp_warm", height=3.55, colour="metal_post"),
    "pole-1965": dict(kind="pole", light="lamp_mercury", height=7.0, reach=1.55, head="bell", colour="metal_galv"),
    "pole-1983": dict(kind="pole", light="lamp_sodium", height=7.4, reach=1.85, head="flat", colour="metal_galv"),
}

CHAMFER = 0.012


def name(variant):
    return f"kit_lamp_{variant}_lod0"


def _post(b, p):
    col, H = p["colour"], p["height"]
    f = WORLD
    # the cast base, its collar and the fluted shaft
    b.prism(f, 0, 0, 0.0, 0.10, 0.19, 0.17, 8, col)
    b.prism(f, 0, 0, 0.10, 0.78, 0.155, 0.11, 8, col)
    b.prism(f, 0, 0, 0.78, 0.86, 0.14, 0.14, 8, col)
    b.prism(f, 0, 0, 0.86, H, 0.075, 0.055, 8, col)
    b.prism(f, 0, 0, H, H + 0.08, 0.09, 0.09, 8, col)
    # the ladder rest, across the street line, with its knobs
    b.box(f, 0, H - 0.18, 0, 0.30, 0.022, 0.022, col, chamfer=CHAMFER)
    for s in (-1, 1):
        b.prism(f, s * 0.30, 0, H - 0.22, H - 0.14, 0.035, 0.035, 6, col)
    # the lantern: a plate, glass widening upwards, a roof that overhangs, a finial
    base = H + 0.08
    b.prism(f, 0, 0, base, base + 0.07, 0.15, 0.15, 4, col, phase=math.pi / 4)
    b.prism(f, 0, 0, base + 0.07, base + 0.48, 0.13, 0.22, 4, p["light"], top=col, bottom=col, phase=math.pi / 4)
    for k in range(4):  # corner bars down the glass
        ang = math.pi / 4 + k * math.pi / 2
        x0, y0 = math.cos(ang), math.sin(ang)
        lo = (0.135 * x0, base + 0.07, 0.135 * y0)
        hi = (0.225 * x0, base + 0.48, 0.225 * y0)
        mid = [(lo[i] + hi[i]) / 2 for i in range(3)]
        b.prism(f, mid[0], mid[2], lo[1], hi[1], 0.018, 0.018, 4, col)
    b.prism(f, 0, 0, base + 0.48, base + 0.53, 0.25, 0.25, 4, col, phase=math.pi / 4)
    b.prism(f, 0, 0, base + 0.53, base + 0.74, 0.27, 0.05, 4, col, phase=math.pi / 4)
    b.prism(f, 0, 0, base + 0.74, base + 0.86, 0.045, 0.0, 6, col)
    return (0.0, 0.0, base + 0.28)


def _pole(b, p):
    col, H, R = p["colour"], p["height"], p["reach"]
    f = WORLD
    b.prism(f, 0, 0, 0.0, 0.40, 0.13, 0.12, 12, col)
    b.prism(f, 0, 0, 0.40, H, 0.085, 0.058, 12, col)
    b.prism(f, 0, 0, H, H + 0.05, 0.065, 0.0, 12, col)
    # the arm, in a frame whose u points out over the street
    side = Frame((0, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, 0))
    bend = (0.42, H + 0.30)
    end = (R, H + 0.40)
    start = (0.0, H - 0.20)
    for (a0, b0), (a1, b1) in ((start, bend), (bend, end)):
        length = math.hypot(a1 - a0, b1 - b0)
        tilt = math.atan2(b1 - b0, a1 - a0)
        b.box(side, (a0 + a1) / 2, (b0 + b1) / 2, 0, length / 2 + 0.03, 0.032, 0.032, col, chamfer=CHAMFER, tilt=tilt)
    ea, eb = end
    if p["head"] == "bell":
        # a bell of galvanised sheet over a frosted bowl, hanging from the arm's end
        b.prism(side, ea, 0, eb - 0.10, eb + 0.02, 0.05, 0.05, 8, col)
        b.prism(side, ea, 0, eb - 0.30, eb - 0.10, 0.36, 0.09, 12, col)
        b.prism(side, ea, 0, eb - 0.46, eb - 0.30, 0.20, 0.30, 12, p["light"], top=col)
        return (0.0, -ea, eb - 0.40)
    # the flat head: a long housing, the lens on its underside
    hb = eb - 0.02
    b.box(side, ea + 0.22, hb, 0, 0.42, 0.075, 0.17, {"default": col, "v-": p["light"]}, chamfer=0.035, tilt=math.radians(4))
    b.box(side, ea + 0.24, hb - 0.08, 0, 0.30, 0.012, 0.12, p["light"], tilt=math.radians(4))
    return (0.0, -(ea + 0.24), hb - 0.10)


def build(params, seed=0):
    """params: a variant name from VARIANTS. seed is unused: a lamp of one era is the same
    everywhere; what differs between lamps on a street is their era, a fact from the fixture.
    Returns (object, light point in Blender coordinates relative to the pivot)."""
    import palette

    p = VARIANTS[params]
    b = Builder()
    light = _post(b, p) if p["kind"] == "post" else _pole(b, p)
    obj = b.build(name(params), palette.material())
    return obj, light
