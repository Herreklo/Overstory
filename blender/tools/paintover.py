"""A target frame painted over a render (docs/visual-direction.md, How the look is built: target frames painted over
our own renders set the bar).

    python blender/tools/paintover.py <passes dir> <camera>      (needs numpy, scipy and Pillow)

Reads the passes LT1Heart.TargetPasses writes for one camera: the frame in the game's style, and raw, what each
pixel is made of (its palette swatch), which way it faces, where it is (mod 8 m) and how far. Paints over it what the
finished town will have and clay cannot show, the way a painter would, and writes <camera>-target.png:

1. Each material re-lit from the clay: the fog in front of each pixel is estimated from its distance and the far
   air, divided out, the light multiplied by the material's own albedo (white paint, red tile, granite, dry stone,
   earth) over the clay's grey, and the fog put back.
2. Surfaces painted in world space so they stay on them: clapboard courses with their shadow lips, corner boards,
   tile courses on the roofs, granite setts with dark wet joints, coursed stone in the walls and plinths.
3. Windows: white frames and glazing bars; in the lit ones curtains and a warm room behind, each a little different.
4. A person climbing the steps, at true scale, lit from the lamp, hidden by whatever stands in front.
5. A painter's finish: the value plan pushed (the nearest unlit masses darkest, the lamp the one white), edges lost
   in the fog and found at the focus, and painted strokes (a Kuwahara filter) with a little canvas.

The facts stay: no house, light or lane is moved, added or taken away; only what clay cannot carry is painted in.
Deterministic: every random choice is seeded by place.
"""

import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generators"))
import palette  # noqa: E402

W, H = 1920, 1080

# the cameras as LT1Heart.Shots has them (street metres), for placing a figure
CAMERAS = {
    "3-street-gully-steps": ((49.3, 12.0, 5.6), (47.5, 44.0, 10.5), 46.4),
}

# what each material is, over the clay's grey (0.42): its albedo, linear
CLAY = 0.42
ALBEDO = {
    "wall": (0.74, 0.72, 0.68),      # white painted timber
    "trim": (0.82, 0.80, 0.76),      # corner boards and frames, fresher paint
    "roof": (0.36, 0.13, 0.09),      # red clay tile
    "setts": (0.30, 0.29, 0.28),     # granite setts, wet
    "stone": (0.33, 0.31, 0.29),     # dry stone, granite steps
    "earth": (0.16, 0.18, 0.12),     # earth and grass at the edges
    "rock": (0.29, 0.29, 0.27),      # the bare granite of the hill, weathered
    "brick": (0.36, 0.17, 0.13),     # chimneys
    "metal": (0.07, 0.09, 0.08),     # lamp posts, dark green paint
}


def lin(c):
    c = np.asarray(c, dtype=np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def hash2(a, b):
    """A seeded 0-1 from two integer arrays: the same block always gets the same value."""
    h = (a.astype(np.int64) * 73856093) ^ (b.astype(np.int64) * 19349663)
    return ((h % 1000003) / 1000003.0).astype(np.float32) % 1.0


def soft_line(t, width, edge):
    """1 inside a band of the given width at the start of each period (t in 0-1), softened by edge."""
    return np.clip((width - t) / max(edge, 1e-4), 0.0, 1.0)


def swatches(material):
    """The swatch name of every pixel, from its palette UV (sky: black)."""
    names = {}
    for n in palette.NAMES:
        u, v = palette.uv(n)
        names[(round(u * 255), round(v * 255))] = n
    keys = np.array(list(names.keys()), dtype=np.float32)
    labels = list(names.values())
    rg = (material[..., :2] * 255.0).reshape(-1, 2)
    d = ((rg[:, None, :] - keys[None, :, :]) ** 2).sum(-1)
    idx = d.argmin(1)
    out = np.array(labels, dtype=object)[idx].reshape(material.shape[:2])
    sky = material.sum(-1) < 0.01
    out[sky] = "sky"
    out[material[..., 2] > 0.8] = "water"
    return out


def paint(passes, camera):
    base = os.path.join(passes, camera)
    render = lin(load(f"{base}-render.png"))
    # the light in the air (the lamps' halos, the beams, the town's glow): given back untouched at the end
    noair = lin(load(f"{base}-render-noair.png")) if os.path.exists(f"{base}-render-noair.png") else render
    air = np.clip(render - noair, 0.0, None)
    gloss = load(f"{base}-gloss.png")[..., 0] if os.path.exists(f"{base}-gloss.png") else np.zeros(render.shape[:2], np.float32)
    spec = (gloss ** 2)[..., None]                                    # how much of what is seen is reflection
    mat = swatches(load(f"{base}-material.png"))
    n = load(f"{base}-normal.png") * 2.0 - 1.0
    pos = load(f"{base}-position.png") * 8.0                     # Unity x, y (up), z, each mod 8 m
    dist_rgb = np.asarray(Image.open(f"{base}-distance.png").convert("RGB"), dtype=np.float32)
    g = dist_rgb[..., 1] / 255.0
    whole = np.round(dist_rgb[..., 0] / 255.0 * 256.0 - g)
    dist = (whole + g) / 256.0 * 4096.0
    sky = mat == "sky"
    dist[sky] = 4096.0
    focal = (H / 2) / math.tan(math.radians(CAMERAS[camera][2]) / 2)
    px_per_m = focal / np.maximum(dist, 0.5)                       # how many pixels a metre covers here

    def has(*names):
        m = np.zeros(mat.shape, dtype=bool)
        for k in names:
            m |= mat == k
        return m

    up = np.abs(n[..., 1])
    wall = has("render_white") & (up < 0.35)
    roof = has("roof_red")
    setts = has("setts_mean", "flags", "asphalt")
    stone = has("stone", "drystone", "quay_wall")
    ground = has("ground", "heath", "grass", "rock")
    earth = ground & (up >= 0.6)                                      # flat earth and grass
    rock = ground & (up < 0.6)                                        # steep ground is the bare rock
    brick = has("brick")
    metal = has("metal_post")
    glass = has("glass", "glass_shop")
    lit = has("glass_lit", "glass_shop_lit")

    # 1. the fog in front of each pixel: the far air's colour, and how much of it lies between
    far = sky | (dist > 150.0)
    fog = np.median(render[far & ~sky], axis=0) if (far & ~sky).sum() > 100 else np.median(render[sky], axis=0)
    hidden = 1.0 - np.exp(-0.006 * dist)[..., None]
    hidden[sky] = 1.0
    surface = np.clip((noair - fog * hidden) / np.maximum(1.0 - hidden, 0.05), 0.0, None)

    out = surface.copy()

    def relight(mask, albedo):
        # the diffuse part takes the material's albedo; what is reflection keeps its own colour
        ratio = np.array(albedo, dtype=np.float32) / CLAY
        out[mask] = surface[mask] * (ratio * (1.0 - spec[mask]) + spec[mask])

    relight(wall, ALBEDO["wall"])
    relight(roof, ALBEDO["roof"])
    relight(setts, ALBEDO["setts"])
    relight(stone, ALBEDO["stone"])
    relight(earth, ALBEDO["earth"])
    relight(rock, ALBEDO["rock"])
    relight(brick, ALBEDO["brick"])
    relight(metal, ALBEDO["metal"])

    px, py, pz = pos[..., 0], pos[..., 1], pos[..., 2]
    # the wall's own horizontal axis: along x or along z, whichever it faces less
    along = np.where(np.abs(n[..., 0]) > np.abs(n[..., 2]), pz, px)
    fade = lambda period: np.clip((px_per_m * period - 2.0) / 3.0, 0.0, 1.0)  # patterns go where the lens can't see them

    # 2a. clapboard: courses of 19 cm, a shadow under each lap, a lit lip above it
    t = (py % 0.19) / 0.19
    lap = soft_line(t, 0.12, 0.05) * 0.18 - soft_line(1.0 - t, 0.08, 0.04) * 0.05
    shade_wall = 1.0 - lap * fade(0.19)
    out[wall] *= shade_wall[wall][:, None]

    # corner boards and the edges of walls: where the facing turns, a white board 12 cm wide
    nx = ndimage.sobel(n[..., 0], axis=1) ** 2 + ndimage.sobel(n[..., 2], axis=1) ** 2
    corner = ndimage.binary_dilation(nx > 0.5, iterations=2) & wall
    out[corner] = surface[corner] * (np.array(ALBEDO["trim"]) / CLAY)

    # 2b. roof tiles: courses by height, tiles across, each course's lower edge in shadow
    tr = (py % 0.24) / 0.24
    course = np.floor(py / 0.24)
    ta = ((along + 0.105 * (course % 2)) % 0.21) / 0.21
    tile = 1.0 - (soft_line(tr, 0.16, 0.06) * 0.35 + soft_line(ta, 0.06, 0.04) * 0.18) * fade(0.21)
    tile *= 1.0 + (hash2(np.floor(along / 0.21), course) - 0.5) * 0.18 * fade(0.21)
    out[roof] *= tile[roof][:, None]

    # 2c. setts: 10 by 16 cm granite in staggered rows, dark wet joints, each stone its own grey
    row = np.floor(pz / 0.10)
    ts = (pz % 0.10) / 0.10
    tx = ((px + 0.08 * (row % 2)) % 0.16) / 0.16
    joint = np.maximum(soft_line(ts, 0.12, 0.06), soft_line(tx, 0.08, 0.05))
    sett = (1.0 - joint * 0.55 * fade(0.10)) * (1.0 + (hash2(np.floor(px / 0.16), row) - 0.5) * 0.22 * fade(0.10))
    out[setts] *= sett[setts][:, None]

    # 2d. coursed stone: courses of 32 cm, blocks of 45 to 90 cm, mortar dark, each block its own value
    sc = np.floor(py / 0.32)
    tsy = (py % 0.32) / 0.32
    blen = 0.45 + 0.45 * hash2(sc, np.zeros_like(sc))
    tsx = ((along + 0.3 * (sc % 2)) % blen) / blen
    mortar = np.maximum(soft_line(tsy, 0.09, 0.05), soft_line(tsx, 0.05, 0.04))
    block = (1.0 - mortar * 0.5 * fade(0.32)) * (1.0 + (hash2(np.floor(along / blen), sc) - 0.5) * 0.3 * fade(0.32))
    out[stone] *= block[stone][:, None]

    # 2e. earth and grass: tufts in world space, a little green, darker in the hollows
    grain = 1.0 + (hash2(np.floor(px / 0.07), np.floor(pz / 0.07)) - 0.5) * 0.35 * fade(0.07)
    out[earth] *= grain[earth][:, None]

    # 2f. the bare rock: planes broken into facets, each its own grey, lichen in pale spots on the faces that see the sky
    fx, fz, fy = np.floor(px / 0.7), np.floor(pz / 0.7), np.floor(py / 0.5)
    facet = 1.0 + (hash2(fx + fy * 13, fz) - 0.5) * 0.32 * fade(0.5)
    lichen = (hash2(np.floor(px / 0.09), np.floor(pz / 0.09) + np.floor(py / 0.09) * 7) > 0.86) & (n[..., 1] > -0.2)
    out[rock] *= facet[rock][:, None]
    li = rock & lichen & (fade(0.09) > 0.3)
    out[li] = out[li] * 0.6 + surface[li] * (np.array([0.42, 0.44, 0.38]) / CLAY) * 0.4

    # 3. windows: frames and glazing bars in white paint; curtains and a warm room in the lit ones
    frame_light = np.median(surface[wall], axis=0) * (np.array(ALBEDO["trim"]) / CLAY) if wall.any() else np.array([0.2, 0.2, 0.2])
    labels, count = ndimage.label(glass | lit)
    for k, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        ys, xs = sl
        h_, w_ = ys.stop - ys.start, xs.stop - xs.start
        if h_ < 4 or w_ < 3:
            continue
        region = labels[sl] == k
        d_here = float(np.median(dist[sl][region]))
        fw = max(1, int(round(0.06 * focal / d_here)))          # a 6 cm frame
        yy, xx = np.mgrid[0:h_, 0:w_]
        frame = (yy < fw) | (yy >= h_ - fw) | (xx < fw) | (xx >= w_ - fw)
        bars = (np.abs(xx - w_ / 2) < max(0.5, fw * 0.6)) | (np.abs(yy - h_ * 0.42) < max(0.5, fw * 0.6))
        is_lit = lit[sl][region].mean() > 0.5
        local = out[sl]
        if is_lit:
            rng = np.random.default_rng(k * 7919 + int(xs.start) * 31 + int(ys.start))
            warm = np.array([1.0, 0.72, 0.42]) * (0.85 + 0.3 * rng.random())
            room = surface[sl].mean(axis=(0, 1)).max()
            # a curtain either side, drawn back, warmer and darker than the room behind
            cw = 0.18 + 0.12 * rng.random()
            curtain = (xx < w_ * cw) | (xx > w_ * (1.0 - cw))
            glow = room * warm[None, None, :] * (0.75 + 0.35 * (1.0 - yy / max(h_, 1)))[..., None]  # the lamp in the room is high
            glow = np.where(curtain[..., None], glow * np.array([0.55, 0.42, 0.30]), glow)
            local[region] = glow[region]
        local[region & (frame | bars)] = frame_light * (1.3 if is_lit else 0.8)
        out[sl] = local

    # 4. a person climbing the steps, at true scale, lit from the lantern above
    figure(out, dist, camera, focal)

    # put the fog back, the light in the air with it, and keep the lights as they were
    final = out * (1.0 - hidden) + fog * hidden + air
    lights = has("lamp_warm", "lamp_sodium", "lamp_mercury", "lamp_red", "lamp_white") | (lin(load(f"{base}-render.png")).max(-1) > 0.92)
    final[lights] = render[lights]
    final[sky] = render[sky]

    # 5. the value plan: the nearest unlit masses the darkest; the lamp the one white
    lum = (final * np.array([0.2126, 0.7152, 0.0722])).sum(-1)
    near_dark = (dist < 16.0) & (lum < 0.03) & ~lights
    final[near_dark] *= 0.85

    # edges lost in the fog: soften with distance; found at the focus (the near lamp and the steps)
    soft = np.clip((dist - 35.0) / 120.0, 0.0, 1.0)[..., None]
    blurred = np.stack([ndimage.gaussian_filter(final[..., c], 1.6) for c in range(3)], -1)
    final = final * (1.0 - soft) + blurred * soft

    g = srgb(final)
    g = kuwahara(g, 2) * 0.6 + g * 0.4                                  # painted strokes
    canvas = ndimage.gaussian_filter(np.random.default_rng(1989).random((H, W)).astype(np.float32), 0.7)
    g = np.clip(g + (canvas[..., None] - 0.5) * 0.025, 0.0, 1.0)
    return (g * 255.0 + 0.5).astype(np.uint8)


def kuwahara(img, r):
    """Each pixel takes the mean of the least varied of its four quadrants (Kuwahara 1976): flat painted strokes
    that keep their edges."""
    size = r + 1
    lum = img.mean(-1)
    box = lambda a: ndimage.uniform_filter(a, size, mode="nearest")
    m = [box(img[..., c]) for c in range(3)]
    l1, l2 = box(lum), box(lum * lum)
    out = np.zeros_like(img)
    best = np.full(lum.shape, np.inf, dtype=np.float32)
    half = r // 2
    for dy in (-half, half):
        for dx in (-half, half):
            sh = lambda a: ndimage.shift(a, (dy, dx), order=0, mode="nearest")
            var = sh(l2) - sh(l1) ** 2
            take = var < best
            best = np.where(take, var, best)
            for c in range(3):
                out[..., c] = np.where(take, sh(m[c]), out[..., c])
    return out


def figure(out, dist, camera, focal):
    """A person on the steps, back to the camera, coat and cap, the lantern's light on one shoulder."""
    if camera != "3-street-gully-steps":
        return
    (cx, cy, cz), (tx, ty, tz), _ = CAMERAS[camera]
    to_u = lambda x, y, z: np.array([x, z, y], dtype=np.float64)       # street to Unity
    c, t = to_u(cx, cy, cz), to_u(tx, ty, tz)
    fwd = (t - c) / np.linalg.norm(t - c)
    right = np.cross(np.array([0.0, 1.0, 0.0]), fwd)
    right /= np.linalg.norm(right)
    upv = np.cross(fwd, right)

    def project(p):
        v = p - c
        depth = v @ fwd
        return W / 2 + (v @ right) / depth * focal, H / 2 - (v @ upv) / depth * focal, depth

    feet = to_u(48.52, 31.0, 5.76)              # on a tread of the lower flight, against the lit steps above
    head = to_u(48.52, 31.0, 5.76 + 1.74)
    fx, fy, fd = project(feet)
    hx, hy, _ = project(head)
    hgt = fy - hy
    # drawn at four times the resolution and averaged, so its edge is soft as a brush's
    k = 4
    x0, x1 = int(fx - hgt * 0.4), int(fx + hgt * 0.4)
    y0, y1 = int(hy - hgt * 0.1), int(fy + hgt * 0.05)
    yy, xx = np.mgrid[y0 * k:y1 * k, x0 * k:x1 * k].astype(np.float32) / k
    u = (xx - fx) / hgt                         # figure units: height 1, 0 at the feet, 1 at the head's top
    v = (fy - yy) / hgt
    # a coat widening to the hem, shoulders rounded, the arms a little out from it
    half = np.where(v > 0.78, 0.115 - (v - 0.78) * 1.2, 0.098 + (0.78 - v) * 0.09)
    coat = (np.abs(u + 0.006) < half) & (v > 0.43) & (v < 0.83)
    arms = (np.abs(np.abs(u) - 0.125) < 0.028) & (v > 0.5) & (v < 0.78)
    legs = ((u > 0.012) & (u < 0.068) & (v > 0.0) & (v < 0.46)) | ((u > -0.072) & (u < -0.018) & (v > 0.075) & (v < 0.46))
    feet_ = ((u > 0.0) & (u < 0.09) & (v > 0.0) & (v < 0.025)) | ((u > -0.085) & (u < -0.01) & (v > 0.075) & (v < 0.1))
    head_ = ((u / 0.062) ** 2 + ((v - 0.905) / 0.068) ** 2) < 1.0
    cap = ((u / 0.075) ** 2 + ((v - 0.955) / 0.03) ** 2 < 1.0) | ((np.abs(u - 0.03) < 0.08) & (np.abs(v - 0.94) < 0.008))
    shape = (coat | arms | legs | feet_ | head_ | cap).astype(np.float32)
    lit_side = shape * (np.clip((u - 0.03) / 0.08, 0.0, 1.0) * ((v > 0.45) & (v < 0.97)))  # the lantern is up to the right
    cover = shape.reshape(y1 - y0, k, x1 - x0, k).mean(axis=(1, 3))
    rim = lit_side.reshape(y1 - y0, k, x1 - x0, k).mean(axis=(1, 3))
    region = (slice(y0, y1), slice(x0, x1))
    visible = (dist[region] > fd - 0.3).astype(np.float32)        # hidden by what is in front
    a = (cover * visible)[..., None]
    ink = np.array([0.018, 0.020, 0.028], dtype=np.float32)
    glow = np.array([0.20, 0.13, 0.07], dtype=np.float32)
    paint_ = ink * (1.0 - rim[..., None]) + glow * rim[..., None]
    out[region] = out[region] * (1.0 - a) + paint_ * a


if __name__ == "__main__":
    passes, camera = sys.argv[1], sys.argv[2]
    img = paint(passes, camera)
    path = os.path.join(passes, f"{camera}-target.png")
    Image.fromarray(img).save(path)
    print(path)
