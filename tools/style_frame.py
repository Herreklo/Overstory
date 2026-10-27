"""A style frame: the walked corner's render, art-directed in code over its passes (reviews/lt1/art-direction/).

    python3 tools/style_frame.py <view> <moment> [--recipe reviews/lt1/art-direction/frames.json] [--values-only]

Runs in any Python with numpy (Blender's has it). Reads LT1Houses.Still's beauty frames
(render/v-<moment>-<view>-material.png) and LT1ArtPasses' passes (passes/p-<view>-<pass>.png), and writes
frames/<view>-<moment>.png with its grey, its value study at one-eighth size (five values, before any colour) and
the shares of each value. Every look is data in the recipe (the views' focus, the lamps and their facts, each
moment's value plan, colour script, air, edges and marks); the code holds only what a painter does to any frame:

1. Light that is a fact and the render lacks (a lamp the layout gives a way but drops today) is added from its
   place: its pool on what faces it, shadowed by what stands between, its post and head, its glow in the air.
2. The value plan: the frame's masses are set to their designed values (the darkest dark the nearest unlit mass,
   the white the light that means people), by depth band and by light, with the detail inside a mass quietened.
3. The colour script: one key colour of air and shade, light warm and paler at its peak, colour by value (darks to
   the shade's hue, lights to the light's), chroma placed at the focus and drained away from it.
4. Edges and marks: found at the focus and where a lit plane meets the sky, lost in shade and with distance; the
   surface drawn as a few flat painted marks from the street stop up, the size of a mark growing with distance.

Nothing moves, appears or goes that is not a fact: no house, step, lamp or person is added that the facts lack.
Deterministic: the only noise is seeded.
"""

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from r0b_count import read_png, write_png  # noqa: E402

AD = os.path.join(REPO, "reviews", "lt1", "art-direction")


# -- colour ------------------------------------------------------------------------------------------------------

def lin(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055).astype(np.float32)


def hexlin(h):
    h = h.lstrip("#")
    return lin(np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32))


def luma(c):
    return (c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722).astype(np.float32)


def lstar(y):
    y = np.maximum(y, 0.0)
    return np.where(y > 0.008856, 116.0 * np.cbrt(y) - 16.0, 903.3 * y).astype(np.float32)


def from_lstar(l):
    l = np.asarray(l, np.float32)
    return np.where(l > 8.0, ((l + 16.0) / 116.0) ** 3, l / 903.3).astype(np.float32)


# -- filters (box sums, so any radius costs the same) -----------------------------------------------------------

def box1(a, r, axis):
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur_rgb(a, sigma):
    return np.stack([blur(a[..., k], sigma) for k in range(a.shape[-1])], -1)


def box(a, r):
    return box1(box1(a, r, 0), r, 1)


def blur(a, sigma):
    """Three box passes, close to a Gaussian of this sigma (pixels)."""
    if sigma < 0.5:
        return a
    r = max(1, int(round((math.sqrt(12.0 * sigma * sigma / 3.0 + 1.0) - 1.0) / 2.0)))
    for _ in range(3):
        a = box(a, r)
    return a


def guided(guide, src, r, eps):
    """He's guided filter: src smoothed inside the guide's edges (a grey guide)."""
    mi, ms = box(guide, r), box(src, r)
    var = box(guide * guide, r) - mi * mi
    cov = box(guide * src, r) - mi * ms
    a = cov / (var + eps)
    b = ms - a * mi
    return box(a, r) * guide + box(b, r)


def kuwahara(img, r):
    """Each pixel takes the mean colour of the calmest of its four quadrants (Kuwahara): flat painted marks with
    their edges kept. img (h, w, 3); the calm is judged on luminance."""
    rr = max(1, r // 2)
    pad = 2 * rr
    img = np.pad(img, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    y = luma(img)
    stats = [box(img, rr), box(y, rr), box(y * y, rr)]
    best, best_var = None, None
    for dy, dx in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        # the window opening from the pixel towards (dy, dx): a box of radius rr centred rr away
        mc, my, myy = (np.roll(np.roll(m, -dy * rr, axis=0), -dx * rr, axis=1) for m in stats)
        vy = myy - my * my
        if best is None:
            best, best_var = mc, vy
        else:
            pick = vy < best_var
            best = np.where(pick[..., None], mc, best)
            best_var = np.where(pick, vy, best_var)
    return best[pad:-pad, pad:-pad]


def by_radius(img, rmap, radii, op):
    """op(img, r) for each radius, blended per pixel by the wanted radius rmap (pixels)."""
    out = img.copy()
    prev_r, prev = 0.0, img
    for r in radii:
        cur = op(img, r)
        t = np.clip((rmap - prev_r) / max(r - prev_r, 1e-3), 0.0, 1.0)[..., None]
        inside = (rmap > prev_r)[..., None]
        out = np.where(inside, prev * (1 - t) + cur * t, out)
        prev_r, prev = r, cur
    return np.where((rmap > radii[-1])[..., None], prev, out)


# -- the camera and the passes ---------------------------------------------------------------------------------

def camera_rays(pos, target, fov, w, h):
    """Unit rays (street axes) through each pixel's centre, as Unity's camera looks at a target with z up."""
    pos, target = np.array(pos, np.float32), np.array(target, np.float32)
    f = target - pos
    f /= np.linalg.norm(f)
    right = np.cross(f, np.array([0, 0, 1], np.float32))
    right /= np.linalg.norm(right)
    up = np.cross(right, f)
    t = math.tan(math.radians(fov) / 2.0)
    u = ((np.arange(w, dtype=np.float32) + 0.5) / w * 2.0 - 1.0) * t * (w / h)
    v = (1.0 - (np.arange(h, dtype=np.float32) + 0.5) / h * 2.0) * t
    d = f[None, None, :] + u[None, :, None] * right[None, None, :] + v[:, None, None] * up[None, None, :]
    return d / np.linalg.norm(d, axis=-1, keepdims=True), (f, right, up, t)


def project(points, pos, basis, w, h):
    """Street points (n, 3) to pixel (x, y) and their distance from the camera."""
    f, right, up, t = basis
    rel = np.asarray(points, np.float32) - np.array(pos, np.float32)
    z = rel @ f
    x = (rel @ right) / (z * t * (w / h))
    y = (rel @ up) / (z * t)
    return np.stack([(x + 1) * 0.5 * w, (1 - y) * 0.5 * h], -1), np.linalg.norm(rel, axis=-1), z


def load_passes(view):
    base = os.path.join(AD, "passes", f"p-{view}")
    raw = {k: read_png(f"{base}-{k}.png").astype(np.float32) / 255.0 for k in ("normal", "distance", "surface")}
    n = raw["normal"] * 2.0 - 1.0
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-4)
    dr, dg, db = raw["distance"][..., 0], raw["distance"][..., 1], raw["distance"][..., 2]
    whole = dr * 255.0
    clean = np.abs(whole - np.round(whole)) < 0.25
    c = np.where(clean, (np.round(whole) + dg) / 255.0, dr)
    dist = (np.power(2.0, 13.0 * c) - 1.0).astype(np.float32)
    cls = np.round(db * 255.0).astype(np.int32)
    sky = (cls == 0) | (cls == 5)
    dist = np.where(sky, 9000.0, dist).astype(np.float32)
    s = raw["surface"]
    return dict(normal=n, dist=dist, cls=cls, sky=sky, kind=np.round(s[..., 0] * 64.0).astype(np.int32),
                palette=s[..., :2])


GLASS, ROOM = 4, 10  # the house kinds a lit pane shows (blender/parts/house/soup.py, KINDS)


def lit_panes(img, ps, threshold):
    """A lit pane is a house's glass or the room behind it, bright in this light: who is in is a fact the render
    already draws."""
    pane = (ps["cls"] == 2) & np.isin(ps["kind"], (GLASS, ROOM))
    return blur((pane & (luma(img) > threshold)).astype(np.float32), 1.0) > 0.3


def load_render(view, moment, look="material"):
    return lin(read_png(os.path.join(AD, "render", f"v-{moment}-{view}-{look}.png")).astype(np.float32) / 255.0)


# -- the painter's steps -------------------------------------------------------------------------------------------

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def add_lamps(img, P, n, dist, sky, cls, rays, cam, lamps, kinds, air, w, h, wet):
    """Each lamp the render lacks: its light on what faces it (shadowed in screen space), its post and head, and
    its glow in the air. Returns the image and a mask of where lamp light lies (for the value plan)."""
    pos, basis = cam
    pool = np.zeros(img.shape[:2], np.float32)
    for lamp in lamps:
        kind = lamp.get("_kind") or kinds[lamp["kind"]]
        colour = hexlin(kind["srgb"])
        head = np.array(lamp["head"], np.float32)
        L = head[None, None, :] - P
        r2 = np.maximum((L * L).sum(-1), 0.25)
        Ld = L / np.sqrt(r2)[..., None]
        facing = np.clip((n * Ld).sum(-1) * (1 - kind["wrap"]) + kind["wrap"], 0.0, 1.0)
        reach = smoothstep(kind["reach"], kind["reach"] * 0.6, np.sqrt(r2))
        e = kind["power"] * facing / r2 * reach
        e = np.where(sky, 0.0, e) * shadow(P, head, dist, cam, w, h, kind.get("shadow_steps", 24))
        # the lamp's own clay stand-in takes none of its light: it is painted out later
        base = np.array(lamp["base"], np.float32)
        own = (np.sqrt(((P[..., :2] - base[None, None, :2]) ** 2).sum(-1)) < kind["clay_box_m"]) \
            & (P[..., 2] > base[2] - 0.05) & (P[..., 2] < head[2] + 0.5)
        e = np.where(blur(own.astype(np.float32), 1.5) > 0.05, 0.0, e)
        pool = np.maximum(pool, np.clip(e / kind["pool_full"], 0, 1))
        if wet:
            # the lamp in the wet: a glossy lobe round the mirror direction, long towards the eye on flat ground
            v = P - np.array(pos, np.float32)[None, None, :]
            v /= np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-4)
            hv = Ld - v
            hv /= np.maximum(np.linalg.norm(hv, axis=-1, keepdims=True), 1e-4)
            spec = np.clip((n * hv).sum(-1), 0, 1) ** wet["lobe"] * (n[..., 2] > 0.6)
            vis = shadow(P, head, dist, cam, w, h, 12)
            spec = spec * kind["power"] / np.maximum(r2, 4.0) ** 0.5 * wet["lamp"] * vis * reach
            img = img + (spec * wet["share"])[..., None] * colour[None, None, :]
            pool = np.maximum(pool, np.clip(spec * wet["share"] / kind["pool_full"], 0, 1))
        if lamp.get("add", False):
            # the light the render lacks: the lamp stands by fact but the layout drops it today
            img = img + surface_albedo(img)[..., None] * e[..., None] * colour[None, None, :]
    return img, pool


def wet_sheen(img, wet, ps, rays):
    """Wet ground takes the air's colour at a grazing angle (Fresnel) and darkens where it looks straight down."""
    if not wet:
        return img
    up = np.clip((ps["normal"][..., 2] - 0.6) / 0.3, 0, 1) * (~ps["sky"])
    graze = np.clip(1 + (rays * ps["normal"]).sum(-1), 0, 1) ** 5
    f = wet["fresnel0"] + (1 - wet["fresnel0"]) * graze
    sheen = hexlin(wet["air_srgb"]) * wet["air"]
    dark = 1 - wet["darken"] * up
    return img * dark[..., None] + (up * f)[..., None] * sheen[None, None, :]


def draw_lamps(img, P, dist, cls, cam, lamps, kinds, air, w, h, lit):
    """The lamps themselves, after the value plan: a light that means people keeps its own value. A lamp stands
    in every light; it glows only when the moment lights it."""
    for lamp in lamps:
        kind = lamp.get("_kind") or kinds[lamp["kind"]]
        head = np.array(lamp["head"], np.float32)
        if lit:
            img = glow(img, head, kind, hexlin(kind["srgb"]), dist, cam, air, w, h)
        img = draw_lantern(img, lamp, kind, dist, cam, w, h, P, cls, lit)
    return img


def mirror(img, wet, ps, P, rays, cam, w, h):
    """Wet ground mirrors what stands over it (screen-space, as games do): each wet pixel marches its reflected ray
    until it passes behind something on screen, and takes that colour, broken by the ground's roughness."""
    if not wet or not wet.get("mirror"):
        return img
    pos, basis = cam
    n = ps["normal"]
    up = (n[..., 2] > 0.75) & ~ps["sky"]
    idx = np.nonzero(up.ravel())[0]
    v = rays.reshape(-1, 3)[idx]
    nn = n.reshape(-1, 3)[idx]
    r = v - 2 * (v * nn).sum(-1, keepdims=True) * nn
    p0 = P.reshape(-1, 3)[idx]
    got = np.zeros((idx.size, 3), np.float32)
    found = np.zeros(idx.size, bool)
    flat = img.reshape(-1, 3)
    t = 0.3
    for _ in range(40):
        q = p0 + r * t
        px, qd, z = project(q, pos, basis, w, h)
        ix, iy = px[:, 0].astype(np.int32), px[:, 1].astype(np.int32)
        ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h) & (z > 0.2)
        ixc, iyc = np.clip(ix, 0, w - 1), np.clip(iy, 0, h - 1)
        scene = ps["dist"][iyc, ixc]
        hit = ok & ~found & (scene < qd) & (scene > qd - max(1.5, t * 0.3))
        sky = ok & ~found & ps["sky"][iyc, ixc] & (t > 30)
        take = hit | sky
        got[take] = flat[iyc[take] * w + ixc[take]]
        found |= take
        t *= 1.16
    # a ray that leaves the picture upwards finds the sky beyond the frame: the sky's colour at the picture's top
    px_end, _, z_end = project(p0 + r * t, pos, basis, w, h)
    away = ~found & (r[:, 2] > 0.05) & ((px_end[:, 1] < 0) | (z_end <= 0))
    top = ps["sky"][: h // 6]
    if top.any() and away.any():
        got[away] = img[: h // 6][top].mean(0)
        found |= away
    out = np.zeros_like(flat)
    out[idx] = got
    m = np.zeros(flat.shape[0], np.float32)
    m[idx] = found
    out = out.reshape(img.shape)
    m = m.reshape(img.shape[:2])
    # rough wet stone: the mirror smeared down the picture and broken into seeded patches
    out = np.stack([box1(blur(out[..., k], wet["blur_px"]), int(wet["streak_px"]), 0) for k in range(3)], -1)
    m = box1(blur(m, wet["blur_px"]), int(wet["streak_px"]), 0)
    rng = np.random.default_rng(1989)
    patches = blur(rng.random(img.shape[:2]).astype(np.float32), wet["patch_px"])
    patches = smoothstep(0.5 - wet["patch_soft"], 0.5 + wet["patch_soft"], (patches - patches.mean()) / (patches.std() + 1e-6) * 0.25 + 0.5)
    graze = np.clip(1 + (rays * n).sum(-1), 0, 1) ** 3
    k = wet["mirror"] * (0.35 + 0.65 * patches) * (0.3 + 0.7 * graze) * up
    ps["shine"] = np.clip(k * m / wet["mirror"], 0, 1)
    return img * (1 - (k * m)[..., None] * wet["mirror_cover"]) + out * (k * m)[..., None]


def merge_masses(tl, plan, ps, pool):
    """Planes of one clay mass (a rock, a retaining wall) told as one value, as a painter lets a dark mass be one
    shape: L* pulled to its neighbourhood's, inside the class, away from lamp pools."""
    mg = plan.get("merge")
    if not mg:
        return tl
    mass = ((ps["cls"] == 1) & (ps["normal"][..., 2] < 0.6)).astype(np.float32)
    mean = blur(tl * mass, mg["px"]) / np.maximum(blur(mass, mg["px"]), 1e-3)
    k = mg["share"] * mass * (1 - pool)
    return tl * (1 - k) + mean * k


def surface_albedo(img):
    """What a lamp's light is multiplied by: the surface's own lightness, from the render (white paint takes more
    than wet granite), kept within what paint and stone can be."""
    y = luma(img)
    return np.clip(0.18 + 2.2 * blur(y, 2.0) / (blur(y, 2.0).mean() + 1e-4) * 0.12, 0.12, 0.8)


def shadow(P, head, dist, cam, w, h, steps):
    """1 where the lamp sees the point, 0 where something on screen stands between (screen-space, as games do)."""
    pos, basis = cam
    hits = np.zeros(dist.shape, np.float32)
    flat = P.reshape(-1, 3)
    # the march stops short of the head itself, so a lamp the render draws does not shade its own light
    # and starts clear of the surface it leaves, so a face lit at a grazing angle does not shade itself
    span = np.maximum(np.linalg.norm(head[None, :] - flat, axis=-1, keepdims=True), 0.7)
    reach, start = 1 - 0.6 / span, np.minimum(0.6 / span, 0.4)
    for k in range(1, steps):
        t = start + (reach - start) * k / steps
        q = flat * (1 - t) + head[None, :] * t
        px, qd, z = project(q, pos, basis, w, h)
        ix = np.clip(px[:, 0].astype(np.int32), 0, w - 1)
        iy = np.clip(px[:, 1].astype(np.int32), 0, h - 1)
        scene = dist[iy, ix]
        blocked = (scene < qd - 0.35) & (scene > qd - 6.0) & (z > 0.1)
        hits = hits + blocked.reshape(dist.shape)
    # a shadow needs a few blocked samples: one alone is the march's aliasing, not a thing in the way
    return blur(1 - np.clip((hits - 1) / 2.0, 0, 1), 1.5)


def draw_lantern(img, lamp, kind, dist, cam, w, h, P=None, cls=None, lit=True):
    """The lamp as its kind draws it (the kind's parts, in metres: a post, a glass lantern, a cap), hidden by
    whatever stands in front. A lamp the render already stands as a clay box is painted out first, from its own
    place, so the frame shows the lantern the lamps element will make, not the box."""
    pos, basis = cam
    base, head = np.array(lamp["base"], np.float32), np.array(lamp["head"], np.float32)
    out = img.copy()
    if P is not None and not lamp.get("add", False):
        flat = np.sqrt(((P[..., :2] - base[None, None, :2]) ** 2).sum(-1))
        box = (cls == 1) & (flat < kind["clay_box_m"]) & (P[..., 2] > base[2] - 0.05) & (P[..., 2] < head[2] + 0.5)
        box = blur(box.astype(np.float32), 1.5) > 0.05
        # each row across the box takes what stands either side of it, as a painter fills a post's place
        cols = np.arange(w)[None, :].repeat(h, 0)
        left = np.maximum.accumulate(np.where(box, -1, cols), axis=1)
        right = np.minimum.accumulate(np.where(box, w, cols)[:, ::-1], axis=1)[:, ::-1]
        lc, rc = np.clip(left, 0, w - 1), np.clip(right, 0, w - 1)
        t = np.clip((cols - left) / np.maximum(right - left, 1), 0, 1)[..., None]
        rows = np.arange(h)[:, None]
        fill = out[rows, lc] * (1 - t) + out[rows, rc] * t
        out = np.where(box[..., None], blur_rgb(fill, 1.0), out)
    _, hd, _ = project(head[None], pos, basis, w, h)
    ppm = h / (2 * float(hd[0]) * basis[3])  # pixels per metre at the lamp
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    post = lin(np.array(kind["post_srgb"], np.float32) / 255.0)
    glass = hexlin(kind["srgb"]) * kind["head_white"] if lit else hexlin(kind["glass_unlit_srgb"])

    def part(z0, z1, half0, half1, colour):
        nonlocal out
        a = np.array([[head[0], head[1], z0], [head[0], head[1], z1]], np.float32)
        ((x0, y0), (x1, y1)), (d0, d1), _ = project(a, pos, basis, w, h)
        t = np.clip((yy - y1) / max(y0 - y1, 1e-3), 0, 1)
        half = (half1 + (half0 - half1) * t) * ppm
        cx = x1 + (x0 - x1) * t
        inside = np.clip(half - np.abs(xx - cx) + 0.5, 0, 1) * np.clip(np.minimum(yy - y1, y0 - yy) + 0.5, 0, 1)
        m = inside * (dist > (d1 + (d0 - d1) * t) - 0.4)
        out = out * (1 - m[..., None]) + m[..., None] * colour

    hz = head[2]
    part(base[2], hz - kind["glass_m"] * 0.6, kind["post_m"] * 0.6, kind["post_m"] * 0.45, post)
    part(hz - kind["glass_m"] * 0.6, hz - kind["glass_m"] * 0.5, kind["head_m"] * 0.42, kind["head_m"] * 0.42, post)
    part(hz - kind["glass_m"] * 0.5, hz + kind["glass_m"] * 0.5, kind["head_m"] * 0.4, kind["head_m"] * 0.5, glass)
    part(hz + kind["glass_m"] * 0.5, hz + kind["glass_m"] * 0.5 + kind["cap_m"], kind["head_m"] * 0.62,
         kind["head_m"] * 0.12, post)
    return out


def glow(img, head, kind, colour, dist, cam, air, w, h):
    """The lamp's light in the air: a halo that grows larger and softer the more fog lies between, seen only
    where nothing nearer than the lamp stands in front."""
    pos, basis = cam
    (hx, hy), hd, z = [a[0] for a in project(head[None], pos, basis, w, h)]
    if z <= 0:
        return img
    fog = air.get("fog", 0.0)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rr = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
    px_m = h / (2 * hd * basis[3])
    halo = np.zeros((h, w), np.float32)
    for size, share in kind["halo"]:
        s = size * kind.get("halo_size", 1.0) * px_m * (1 + fog * hd / 40.0)
        halo += share * np.exp(-(rr / max(s, 1.0)) ** 2)
    front = smoothstep(hd - 2.0, hd + 1.0, dist)
    behind = 0.35 + 0.65 * front
    a = kind["halo_strength"] * (0.3 + fog) * halo * behind
    return img + a[..., None] * colour[None, None, :]


def masses(plan, P, ps):
    """The masses a moment's plan names, each a box in street metres round a thing the facts place (a rock, a
    wall), on the classes it lists: a soft mask each."""
    out = []
    for m in plan.get("masses", []):
        lo, hi = np.array(m["box"][:3], np.float32), np.array(m["box"][3:], np.float32)
        inside = np.all((P >= lo) & (P <= hi), -1) & np.isin(ps["cls"], m.get("cls", [1])) & ~ps["sky"]
        if m.get("steep_only"):
            inside &= ps["normal"][..., 2] < 0.6
        out.append({**m, "mask": blur(inside.astype(np.float32), 2.0)})
    return out


def local_value(plan, ps):
    """Local value: a white wall is lighter than granite in the same light, a roof darker; offsets in L* by what
    each surface is (ps: the passes)."""
    off = np.zeros(ps["dist"].shape, np.float32)
    lv = plan.get("local", {})
    house = ps["cls"] == 2
    up = ps["normal"][..., 2] > 0.7
    off += np.where(house & np.isin(ps["kind"], (0, 2, 3, 12)), lv.get("paint", 0.0), 0.0)
    off += np.where(house & (ps["kind"] == 5), lv.get("roof", 0.0), 0.0)
    off += np.where(ps["cls"] == 3, lv.get("stone", 0.0), 0.0)
    off += np.where((ps["cls"] == 3) & up, lv.get("tread", 0.0), 0.0)
    off += np.where((ps["cls"] == 1) & up, lv.get("ground", 0.0), 0.0)
    off += np.where((ps["cls"] == 1) & ~up, lv.get("clay", 0.0), 0.0)
    return blur(off, 1.0)


def air_glow(plan, ps, rays):
    """The town's own light held in the fog: a broad lift of the air, strongest towards a lit place (its
    direction), in L*, on the sky and on whatever stands far enough to be veiled."""
    g = plan.get("glow")
    if not g:
        return np.zeros(ps["dist"].shape, np.float32)
    d = np.array(g["towards"], np.float32)
    az = np.degrees(np.arctan2(rays[..., 0], rays[..., 1]) - math.atan2(d[0], d[1]))
    el = np.degrees(np.arcsin(np.clip(rays[..., 2], -1, 1)) - math.asin(d[2] / np.linalg.norm(d)))
    # a bank, not a ball: wide along the horizon, thinning fast upwards and slower downwards into the gully
    up = np.where(el > 0, g["deg_up"], g["deg_down"])
    shape = np.exp(-(az / g["deg_wide"]) ** 2 - (el / up) ** 2)
    veil = 1 - np.exp(-ps["dist"] / g["veil_m"])
    return (g["lstar"] * shape * veil).astype(np.float32)


def value_plan(img, plan, dist, sky, pool, focus_w, lit, local, glow_l, ps):
    """The masses set to their designed values. A base (edge-aware, so a mass stays one mass) carries the value;
    the detail riding on it is quietened by the plan's calm, most in shade and with distance."""
    y = np.maximum(luma(img), 1e-5)
    ly = np.log(y)
    guide = np.clip(np.log(np.maximum(dist, 0.5)) / 9.0, 0, 1) * 0.5 + np.clip(srgb(y), 0, 1) * 0.5
    base = guided(guide, ly, plan["mass_px"], plan["mass_eps"])
    detail = ly - base
    L = lstar(np.exp(base))
    target = np.zeros_like(L)
    weight = np.zeros_like(L)
    # depth bands: each a designed range of L*, the render's own order kept inside it
    for band in plan["bands"]:
        lo, hi = band["m"]
        wgt = smoothstep(lo - band.get("soft", 4.0), lo, dist) * (1 - smoothstep(hi, hi + band.get("soft", 4.0), dist))
        wgt = np.where(sky, 0.0, wgt)
        a, b = band["from"]
        c, d = band["to"]
        t = np.clip((L - a) / max(b - a, 1e-3), 0, 1)
        target += wgt * (c + (d - c) * t)
        weight += wgt
    tl = np.where(weight > 1e-3, target / np.maximum(weight, 1e-3), L) + local
    # the sky: its own range, lifted low where the town's light is in the air
    sa, sb = plan["sky"]["from"]
    sc, sd = plan["sky"]["to"]
    tl = np.where(sky, sc + (sd - sc) * np.clip((L - sa) / max(sb - sa, 1e-3), 0, 1), tl)
    up = plan["sky"].get("up")
    if up:
        # [from, to, L*]: the sky darkening upwards (degrees above the horizon), away from the town's light
        tl = np.where(sky, tl + up[2] * smoothstep(up[0], up[1], ps["elev"]), tl)
    tl = merge_masses(tl, plan, ps, pool)
    bl = plan.get("by_light")
    if bl and ps.get("sun") is not None:
        # low sun's two values: what the sun reaches lifted, what only the sky reaches held down
        lifted = np.maximum(tl, np.minimum(tl + bl["sun"], bl.get("sun_max", 100.0)))
        tl = np.where(sky, tl, (tl + bl["shade"]) * (1 - ps["sun"]) + lifted * ps["sun"])
    # named masses: one the design holds to a value of its own (a curtain of rock), whatever its planes do
    for m in ps.get("masses", []):
        a, b = m["from"]
        c, d = m["to"]
        t = np.clip((L - a) / max(b - a, 1e-3), 0, 1)
        tl = tl + (c + (d - c) * t - tl) * m.get("share", 1.0) * m["mask"]
        tl = tl + m.get("sky_lift", 0.0) * np.clip(ps["normal"][..., 2], 0, 1) * m["mask"]
    # the veil: away from the focus the middle distance leans to the air's value, so the found edges are the focus's
    veil = plan.get("veil")
    if veil:
        band = smoothstep(veil["m"][0], veil["m"][1], dist) * (1 - focus_w) * (~sky)
        tl = tl + (veil["lstar"] - tl) * veil["share"] * band
    tl = tl + glow_l
    # lamp pools and lit panes keep their light above the plan: they are the values that mean people
    # (on a named mass the design's value stands under the pool, so the light lifts it without spreading)
    lift = plan.get("pool_lift", 0.0)
    held = sum((m["mask"] for m in ps.get("masses", [])), np.zeros_like(L))
    tl = tl * (1 - pool) + (np.maximum(tl, L * (1 - held) + tl * held) + lift) * pool
    tl = np.where(lit, np.minimum(np.maximum(tl, L), plan.get("lit_max", 100.0)), tl)
    # the wet's shine is a signal (the treads' lines leading up), kept with the focus and the pools
    calm = plan["calm"] + (1 - plan["calm"]) * np.maximum(np.maximum(focus_w, pool), ps.get("shine", 0) * plan.get("shine_keep", 0.0))
    calm = calm + (plan.get("focus_detail", 1.0) - 1.0) * focus_w
    ly2 = np.log(np.maximum(from_lstar(tl), 1e-5)) + detail * calm
    gain = np.exp(ly2) / y
    return img * gain[..., None]


def accents(cs, P, ps):
    """The moment's one accent, by what a surface is (a house kind, a class) and where (a box in street metres):
    keeps its own hue and more of its chroma than anything round it."""
    k = np.zeros(ps["dist"].shape, np.float32)
    for a in cs.get("accents", []):
        m = np.isin(ps["cls"], a.get("cls", [2])) & ~ps["sky"]
        if "kinds" in a:
            m &= np.isin(ps["kind"], a["kinds"])
        if "box" in a:
            m &= np.all((P >= np.array(a["box"][:3], np.float32)) & (P <= np.array(a["box"][3:], np.float32)), -1)
        k = np.maximum(k, blur(m.astype(np.float32), 1.0) * a["chroma"])
    return k


def colour_script(img, cs, focus_w, pool, lit, sky, glow, accent=None, sun=None):
    """Colour by value: each pixel keeps its value and takes its hue between the shade's colour (darks) and the
    light's (lights), mixed with its own by the script's strength; chroma placed at the focus, drained away."""
    y = np.maximum(luma(img), 1e-5)
    v = np.clip(lstar(y) / 100.0, 0, 1)
    own = img / y[..., None]
    keys = cs["ramp"]
    xs = np.array([k[0] for k in keys], np.float32)
    cols = np.array([hexlin(k[1]) for k in keys], np.float32)
    cols = cols / np.maximum(luma(cols)[:, None], 1e-5)
    ramp = np.stack([np.interp(v, xs, cols[:, k]) for k in range(3)], -1)
    strength = cs["strength"] * (1 - np.where(lit, cs["keep_lit"], 0.0)) * (1 - pool * cs.get("keep_pool", 0.0))
    strength = np.where(sky, cs.get("strength_sky", cs["strength"]), strength)
    hue = own * (1 - strength[..., None]) + ramp * strength[..., None]
    bl = cs.get("by_light")
    if bl and sun is not None:
        # the sun's gold on what it reaches, the sky's blue in every shade, whatever their value
        sc, hc = (hexlin(bl[k]) for k in ("sun_srgb", "shade_srgb"))
        lh = (hc / luma(hc)) * (1 - sun[..., None]) + (sc / luma(sc)) * sun[..., None]
        k = np.where(sky, 0.0, bl["share"])[..., None]
        hue = hue * (1 - k) + lh * k
    if cs.get("glow_srgb"):
        # the town's light held in the fog: its own warm hue where the air glows, the more the stronger it is
        gc = hexlin(cs["glow_srgb"])
        gk = (cs["glow_share"] * glow / max(float(glow.max()), 1e-3))[..., None]
        hue = hue * (1 - gk) + (gc / max(float(luma(gc)), 1e-5))[None, None, :] * gk
    # chroma: drained away from the focus and the lamps, kept where light means people
    grey = np.ones_like(hue)
    keep = cs["chroma_far"] + (cs["chroma_focus"] - cs["chroma_far"]) * np.maximum(focus_w, pool)
    keep = np.where(lit, 1.0, keep)
    keep = np.where(sky, cs.get("chroma_sky", keep), keep)
    if accent is not None:
        a = np.clip(accent, 0, None)
        hue = own * (a > 0)[..., None] * np.minimum(a, 1)[..., None] + hue * (1 - np.minimum(a, 1))[..., None]
        keep = np.where(a > 0, np.maximum(keep * (1 - np.minimum(a, 1)), a), keep)
    hue = grey + (hue - grey) * keep[..., None]
    hue = hue / np.maximum(luma(hue)[..., None], 1e-5)
    return hue * y[..., None]


def edges_and_marks(img, dist, sky, focus_w, pool, em):
    """Lost and found, and the painted mark: away from the focus, in shade and with distance, the surface becomes a
    few flat marks (Kuwahara), bigger the farther and the darker; a lost edge is a soft blend into the air."""
    y = luma(img)
    dark = 1 - smoothstep(em["dark_lo"], em["dark_hi"], lstar(y))
    far = smoothstep(em["near_m"], em["far_m"], dist)
    want = em["mark_px"][0] + (em["mark_px"][1] - em["mark_px"][0]) * np.maximum(far, dark * em["dark_share"])
    want = want * (1 - focus_w * em["focus_keep"]) * (1 - pool * em.get("pool_keep", 0.0))
    want = np.where(sky, em.get("sky_px", 0.0), want)
    out = by_radius(img, want, em["radii"], kuwahara)
    soft = em["lost_px"] * np.maximum(far * (1 - focus_w), dark * em["dark_share"] * (1 - focus_w))
    # the sky as a few soft shapes: a painter's sky, not the render's every wisp
    soft = np.where(sky, em.get("sky_soft_px", 0.0), soft)
    return by_radius(out, soft, [1.0, 2.5, 5.0, 12.0], lambda a, r: blur_rgb(a, r))


def lens(img, ln, h, w):
    """Halation round bright light, a soft vignette, and a fine seeded grain, the way film and canvas carry it."""
    y = luma(img)
    bright = np.maximum(y - ln["halo_from"], 0.0)
    bl = sum(blur(bright, s) * k for s, k in ln["halo"])
    img = img + bl[..., None] * hexlin(ln["halo_srgb"])[None, None, :]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img = img * (1 - ln["vignette"] * smoothstep(0.6, 1.5, r))[..., None]
    rng = np.random.default_rng(1989)
    g = blur(rng.random((h, w)).astype(np.float32) - 0.5, 0.6)
    return img * (1 + g[..., None] * ln["grain"])


def value_study(img, out_base):
    """The value study: one-eighth size, grey, and in five values, with each value's share of the frame."""
    h, w = img.shape[:2]
    e = 8
    small = img[:h // e * e, :w // e * e].reshape(h // e, e, w // e, e, 3).mean((1, 3))
    L = lstar(luma(small))
    grey = srgb(from_lstar(L))
    write_png(f"{out_base}-eighth.png", (np.repeat(grey[..., None], 3, -1) * 255).round())
    bands = np.clip((L / 20.0).astype(np.int32), 0, 4)
    shades = np.array([10, 30, 50, 70, 92], np.float32)
    five = srgb(from_lstar(shades[bands]))
    write_png(f"{out_base}-values.png", (np.repeat(five[..., None], 3, -1) * 255).round())
    share = [round(100.0 * float((bands == b).mean()), 1) for b in range(5)]
    return share


def merged(base, over):
    """A moment's recipe with a view's own changes laid over it, key by key."""
    out = dict(base)
    for k, v in over.items():
        out[k] = merged(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("view")
    ap.add_argument("moment")
    ap.add_argument("--recipe", default=os.path.join(AD, "frames.json"))
    ap.add_argument("--values-only", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    recipe = json.load(open(a.recipe))
    view = recipe["views"][a.view]
    mo = recipe["moments"][a.moment]
    frame = merged(mo, view.get("moments", {}).get(a.moment, {}))
    img = load_render(a.view, a.moment)
    h, w = img.shape[:2]
    ps = load_passes(a.view)
    rays, basis = camera_rays(view["pos"], view["target"], view["fov"], w, h)
    P = np.array(view["pos"], np.float32)[None, None, :] + rays * ps["dist"][..., None]
    cam = (view["pos"], basis)
    # the focus: a soft field round the designed focal point, in the picture
    (fx, fy), _, _ = [q[0] for q in project(np.array([view["focus"]], np.float32), view["pos"], basis, w, h)]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rf = np.sqrt(((xx - fx) / w) ** 2 + ((yy - fy) / h) ** 2)
    focus_w = np.exp(-(rf / view["focus_radius"]) ** 2).astype(np.float32)
    ps["lit"] = lit_panes(img, ps, frame.get("lit_from", 0.08))
    if frame.get("sun_warm"):
        g = load_render(a.view, a.moment, "grey")
        warm = (g[..., 0] - g[..., 2]) / np.maximum(g.mean(-1), 1e-3)
        ps["sun"] = blur(smoothstep(*frame["sun_warm"], warm), 1.0) * (~ps["sky"])
    # each lamp's kind with this moment's art over it (a painter's subordination of one lamp to another)
    lamps = [{**l, "_kind": {**recipe["lamp_kinds"][l["kind"]], **frame.get("lamp_art", {}).get(l["id"], {})}}
             for l in recipe["lamps"]]
    lit_on = frame.get("lamps_on", False)
    img, pool = add_lamps(img, P, ps["normal"], ps["dist"], ps["sky"], ps["cls"], rays, cam, lamps if lit_on else [],
                          recipe["lamp_kinds"], frame.get("air", {}), w, h, frame.get("wet")) \
        if lit_on else (img, np.zeros((h, w), np.float32))
    ps["masses"] = masses(frame["values"], P, ps)
    for m in ps["masses"]:
        pool = pool * (1 - (1 - m.get("pool", 1.0)) * m["mask"])
    ps["elev"] = np.degrees(np.arcsin(np.clip(rays[..., 2], -1, 1))).astype(np.float32)
    img = wet_sheen(img, frame.get("wet"), ps, rays)
    img = mirror(img, frame.get("wet"), ps, P, rays, cam, w, h)
    glow_l = air_glow(frame["values"], ps, rays)
    img = value_plan(img, frame["values"], ps["dist"], ps["sky"], pool, focus_w, ps["lit"],
                     local_value(frame["values"], ps), glow_l, ps)
    img = draw_lamps(img, P, ps["dist"], ps["cls"], cam, lamps, recipe["lamp_kinds"], frame.get("air", {}), w, h, lit_on)
    out = a.out or os.path.join(AD, "frames", f"{a.view}-{a.moment}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if a.values_only:
        print("values", value_study(img, out))
        return
    img = colour_script(img, frame["colour"], focus_w, pool, ps["lit"], ps["sky"], glow_l, accents(frame["colour"], P, ps), ps.get("sun"))
    img = edges_and_marks(img, ps["dist"], ps["sky"], focus_w, pool, frame["edges"])
    img = lens(img, frame["lens"], h, w)
    write_png(f"{out}.png", (srgb(img) * 255).round())
    g = srgb(luma(img))
    write_png(f"{out}-grey.png", (np.repeat(g[..., None], 3, -1) * 255).round())
    print("values", value_study(img, out))


if __name__ == "__main__":
    main()
