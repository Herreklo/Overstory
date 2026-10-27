"""Direction thumbnails: ways to design one view, each a production designer's value sketch at one-eighth size and
its colour key (reviews/lt1/art-direction/directions/).

    python3 tools/style_thumb.py <view> <moment> [--only name] [--recipe reviews/lt1/art-direction/directions.json]

Each direction in the recipe is an idea in one sentence, a value plan, a colour script and a shape language, all
data. The code paints the view's masses (things the facts place: each house's walls, roof and plinth, the rock, the
steps, the ground, the sky; found from LT1ArtPasses' passes inside street boxes) as flat designed values, lifted only
by lights that are facts (each lamp, shadowed in screen space; the sky on what faces up), veiled by the air with
distance and height, and cut to the direction's few inks. Nothing is added that the facts lack. Runs in any Python
with numpy (Blender's has it), in a few seconds.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style_frame as sf  # noqa: E402

AD = sf.AD


def half(a):
    return a[::2, ::2]


def down(a, e):
    h, w = a.shape[:2]
    return a[:h // e * e, :w // e * e].reshape(h // e, e, w // e, e, *a.shape[2:]).mean((1, 3))


def mass_labels(spec, P, ps):
    """Each pixel's mass: the last in the list whose class, box, surface kind, facing and height all hold."""
    lab = np.zeros(ps["dist"].shape, np.int32)
    n = ps["normal"]
    for i, m in enumerate(spec):
        sel = ps["sky"] if m.get("sky") else np.isin(ps["cls"], m.get("cls", [1, 2, 3, 4, 6])) & ~ps["sky"]
        if "box" in m:
            lo, hi = np.array(m["box"][:3], np.float32), np.array(m["box"][3:], np.float32)
            sel = sel & np.all((P >= lo) & (P <= hi), -1)
        if "kinds" in m:
            sel = sel & np.isin(ps["kind"], m["kinds"])
        for k, axis in (("nx", 0), ("ny", 1), ("nz", 2)):
            if k in m:
                sel = sel & (n[..., axis] >= m[k][0]) & (n[..., axis] <= m[k][1])
        if "z" in m:
            sel = sel & (P[..., 2] >= m["z"][0]) & (P[..., 2] <= m["z"][1])
        lab[sel] = i
    return lab


def look_up(values, spec, i):
    """A mass's design, or the design of the mass it is like (C.east is like C.wall, which is like house)."""
    name = spec[i]["name"]
    while name not in values:
        name = next((m.get("like", "rest") for m in spec if m["name"] == name), "rest")
    return values[name]


def shadow_near(P, sel, head, dist, cam, w, h, steps):
    """style_frame.shadow, marched only from the points a lamp can reach."""
    pos, basis = cam
    flat = P[sel]
    hits = np.zeros(len(flat), np.float32)
    span = np.maximum(np.linalg.norm(head[None, :] - flat, axis=-1, keepdims=True), 0.7)
    reach, start = 1 - 0.6 / span, np.minimum(0.6 / span, 0.4)
    for k in range(1, steps):
        t = start + (reach - start) * k / steps
        q = flat * (1 - t) + head[None, :] * t
        px, qd, z = sf.project(q, pos, basis, w, h)
        ix = np.clip(px[:, 0].astype(np.int32), 0, w - 1)
        iy = np.clip(px[:, 1].astype(np.int32), 0, h - 1)
        scene = dist[iy, ix]
        hits += ((scene < qd - 0.35) & (scene > qd - 6.0) & (z > 0.1))
    vis = np.ones(dist.shape, np.float32)
    vis[sel] = 1 - np.clip((hits - 1) / 2.0, 0, 1)
    return sf.blur(vis, 1.5)


def lamp_light(P, ps, cam, lamps, kinds, w, h):
    """How much each lamp's light falls on each point: its power on what faces it, by distance, within its reach,
    where nothing on screen stands between."""
    out = {}
    for lamp in lamps:
        kind = kinds[lamp["kind"]]
        head = np.array(lamp["head"], np.float32)
        L = head[None, None, :] - P
        r2 = np.maximum((L * L).sum(-1), 0.25)
        facing = np.clip((ps["normal"] * L / np.sqrt(r2)[..., None]).sum(-1) * (1 - kind["wrap"]) + kind["wrap"], 0, 1)
        reach = sf.smoothstep(kind["reach"], kind["reach"] * 0.6, np.sqrt(r2))
        e = kind["power"] * facing / r2 * reach * shadow_near(P, (reach > 0) & ~ps["sky"], head, ps["dist"], cam, w, h, 16)
        out[lamp["id"]] = np.where(ps["sky"], 0.0, e / kind["pool_full"]).astype(np.float32)
    return out


def wet_lobe(P, ps, cam, lamp, kind, wet):
    """A lamp in wet ground: a streak below it, narrow across and long towards the eye, as rough wet stone draws a
    light (the mirror direction's bearing within a degree or two of the lamp's, its height within many)."""
    pos, _ = cam
    head = np.array(lamp["head"], np.float32)
    L = head[None, None, :] - P
    r = np.maximum(np.linalg.norm(L, axis=-1), 2.0)
    Ld = L / r[..., None]
    v = P - np.array(pos, np.float32)[None, None, :]
    v /= np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-4)
    n = ps["normal"]
    R = v - 2 * (v * n).sum(-1, keepdims=True) * n
    daz = np.degrees(np.arctan2(R[..., 0] * Ld[..., 1] - R[..., 1] * Ld[..., 0], R[..., 0] * Ld[..., 0] + R[..., 1] * Ld[..., 1]))
    delv = np.degrees(np.arcsin(np.clip(R[..., 2], -1, 1)) - np.arcsin(np.clip(Ld[..., 2], -1, 1)))
    across, along = wet["streak_deg"]
    s = np.exp(-(daz / across) ** 2 - (delv / along) ** 2) * (n[..., 2] > 0.6) * (R[..., 2] > 0)
    return (s * np.clip(kind["reach"] * 1.5 / r, 0, 1)).astype(np.float32)


def paint(d, view, recipe, P, ps, cam, w, h, rays, lit, draw=True):
    """One direction's value sketch, in L*: masses, lights, air, then the lamps themselves."""
    spec = view["masses"]
    lab = mass_labels(spec, P, ps)
    nz = np.clip(ps["normal"][..., 2], 0, 1)
    L = np.zeros(lab.shape, np.float32)
    lamp_k = np.zeros(lab.shape, np.float32)
    sky_k = np.zeros(lab.shape, np.float32)
    sun_k = np.zeros(lab.shape, np.float32)
    tint = np.zeros(lab.shape + (3,), np.float32)
    tint_k = np.zeros(lab.shape, np.float32)
    for i in range(len(spec)):
        m = lab == i
        if not m.any():
            continue
        v = look_up(d["masses"], spec, i)
        L[m], lamp_k[m], sky_k[m], sun_k[m] = v.get("L", 30), v.get("lamp", 0), v.get("sky", 0), v.get("sun", 0)
        if "grad" in v:
            # a painter's gradation: no large mass one flat value; L* per metre about the mass's middle height
            z = P[..., 2][m]
            g = v.get("grad_max", 6.0)
            L[m] += np.clip(v["grad"] * (z - np.median(z)), -g, g)
        if "tint" in v:
            tint[m], tint_k[m] = sf.hexlin(v["tint"]), v.get("tint_k", 0.6)
    lamps = recipe["lamps"] + d.get("extra_lamps", [])
    kinds = recipe["lamp_kinds"]
    lights = lamp_light(P, ps, cam, lamps, kinds, w, h) if d.get("lamps_on", True) else {}
    pool = np.zeros(lab.shape, np.float32)
    hue = np.zeros(lab.shape + (3,), np.float32)
    for l in lamps:
        if l["id"] in lights:
            e = lights[l["id"]] * d.get("lamp_scale", {}).get(l["id"], 1.0)
            pool = pool + e
            hue = hue + e[..., None] * sf.hexlin(kinds[l["kind"]]["srgb"])[None, None, :]
    pool = 1 - np.exp(-pool * d.get("lamp_boost", 1.0))
    L = L + sky_k * nz + lamp_k * pool
    sun = ps.get("sun")
    if sun is not None and d.get("sun"):
        # the sun where the render's own light puts it (a fact): what it reaches lifted, in its own colour
        L = L + sun_k * sun
        hue = hue + (sun * 4)[..., None] * sf.hexlin(d["sun"]["srgb"])[None, None, :]
        pool = np.maximum(pool, sun * d["sun"].get("share", 1.0))
    skyb = sf.blur(ps["sky"].astype(np.float32), 1.0)
    for i, m in enumerate(spec):
        v = look_up(d["masses"], spec, i)
        if "rim" in v and (lab == i).any():
            r = v["rim"]
            near = sf.blur(ps["sky"].astype(np.float32), r["px"] * w / 1920.0) > 0.02
            L = np.where((lab == i) & near & (skyb < 0.5), r["L"], L)
    wet = d.get("wet")
    warm = pool.copy()
    if wet:
        for l in lamps:
            s = np.clip(wet_lobe(P, ps, cam, l, kinds[l["kind"]], wet) *
                        wet.get("by_lamp", {}).get(l["id"], 1.0), 0, 1)
            L = L + wet["L"] * s
            warm = np.maximum(warm, np.clip(s * 2, 0, 1))
            hue = hue + (s * 4)[..., None] * sf.hexlin(kinds[l["kind"]]["srgb"])[None, None, :]
    # the sky, and the town's light held in the air towards a lit place
    elev = np.degrees(np.arcsin(np.clip(rays[..., 2], -1, 1)))
    sk = d["sky"]
    sky_L = sk["horizon"] + (sk["zenith"] - sk["horizon"]) * sf.smoothstep(sk.get("deg0", 0), sk["deg"], elev)
    g = d.get("glow")
    glowf = np.zeros(lab.shape, np.float32)
    if g:
        (gx, gy), _, _ = [q[0] for q in sf.project(np.array([g["towards"]], np.float32), cam[0], cam[1], w, h)]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        px_deg = h / (2 * np.degrees(np.arctan(cam[1][3])))
        dx, dy = (xx - gx) / (g["deg_wide"] * px_deg), (yy - gy) / (np.where(yy < gy, g["deg_up"], g["deg_down"]) * px_deg)
        glowf = np.exp(-(dx * dx + dy * dy)).astype(np.float32)
    a = d["air"]
    zmid = (cam[0][2] + np.minimum(P[..., 2], 60.0)) * 0.5
    dens = np.exp(-np.maximum(zmid - a.get("z0", 0.0), 0.0) / a.get("height_m", 1e6))
    t = 1 - np.exp(-np.maximum(ps["dist"] - a.get("from_m", 0.0), 0.0) * dens / a["m"])
    fog_L = a["L"] + (sky_L - sk["horizon"]) * a.get("sky_share", 0.0) + glowf * (g["L"] if g else 0)
    L = L * (1 - t) + fog_L * t
    L = np.where(ps["sky"], sky_L + glowf * (g["L"] if g else 0) * g.get("sky_share", 1.0) if g else sky_L, L)
    warm = np.maximum(warm * (1 - t), glowf * (g.get("warm", 0) if g else 0))
    if g:
        hue = hue + (glowf * g.get("warm", 0) * 4)[..., None] * sf.hexlin(g.get("srgb", "#ffc27e"))[None, None, :]
    # lit rooms: who is in is a fact the render already draws
    win = d.get("windows")
    if win:
        L = np.where(lit, L * (1 - (1 - t) * 0.95) + win * (1 - t) * 0.95 + fog_L * 0, L)
        warm = np.where(lit, np.maximum(warm, 1 - t), warm)
    # the lamps: post, glass and halo (a full frame draws its own, style_frame.draw_lamps)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for l in (lamps if draw else []):
        art = {**d["lamp"]["default"], **d["lamp"].get(l["id"], {})}
        kind = kinds[l["kind"]]
        (bx, by), bd, _ = [q[0] for q in sf.project(np.array([l["base"]], np.float32), cam[0], cam[1], w, h)]
        (hx, hy), hd, hz = [q[0] for q in sf.project(np.array([l["head"]], np.float32), cam[0], cam[1], w, h)]
        if hz <= 0:
            continue
        px_m = h / (2 * hd * cam[1][3])
        front = ps["dist"] > hd - 1.0
        tl = 1 - np.exp(-hd * np.exp(-max((cam[0][2] + l["head"][2]) * 0.5 - a.get("z0", 0), 0) / a.get("height_m", 1e6)) / a["m"])
        post = (np.abs(xx - (bx + (hx - bx) * (yy - by) / min(hy - by, -1e-3))) < max(kind["post_m"] * px_m * 0.5, 0.6)) \
            & (yy > hy) & (yy < by) & front
        L = np.where(post, art.get("post", 12) * (1 - tl) + fog_L * tl, L)
        if d.get("lamps_on", True):
            rr = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
            s = art["halo_m"] * px_m * (1 + a.get("fog", 0.6) * hd / 40.0)
            halo = art["halo_L"] * np.exp(-(rr / max(s, 1.0)) ** 2) * (0.35 + 0.65 * front)
            L = L + halo
            warm = np.maximum(warm, np.clip(halo / 20.0, 0, 1))
            hue = hue + (np.clip(halo / 10.0, 0, 4))[..., None] * sf.hexlin(kind["srgb"])[None, None, :]
            glass = (rr < max(kind["glass_m"] * px_m * 0.5, 1.2)) & front
            L = np.where(glass, art["glass"], L)
            warm = np.where(glass, 0.5, warm)
    win_hue = sf.hexlin(d["colour"]["warm"])[None, None, :]
    if win:
        hue = np.where(lit[..., None], hue + win_hue * 4, hue)
    hue = hue / np.maximum(hue.max(-1, keepdims=True), 1e-6)
    hue = np.where((hue.sum(-1) < 1e-3)[..., None], win_hue / win_hue.max(), hue)
    air = np.where(ps["sky"], -1.0, t).astype(np.float32)
    if sun is not None and d.get("sun"):
        warm = np.maximum(warm, sun * (1 - t) * d["sun"].get("share", 1.0))
    tint_k = tint_k * (1 - t)
    return np.clip(L, 0, 100), np.clip(warm, 0, 1), hue, air, np.concatenate([tint, tint_k[..., None]], -1)


def for_moment(d, moment):
    """A direction's design in one light: its own moment's design over the shared parts (shape, idea)."""
    ms = d.get("moments")
    if not ms:
        return d if moment == d.get("moment", moment) else None
    if moment not in ms:
        return None
    return {**{k: v for k, v in d.items() if k != "moments"}, **ms[moment]}


def design_view(rec, frames, name):
    """A view with the masses every view shares (things placed in street metres) and any of its own."""
    own = rec.get("views", {}).get(name, {})
    return {**frames["views"][name], **own, "masses": rec["masses"] + own.get("masses", [])}


def kinds_of(rec, frames):
    return {**frames, "lamp_kinds": {**frames["lamp_kinds"], **rec.get("lamp_kinds", {})}}


def inks(L, levels):
    lv = np.array(levels, np.float32)
    return lv[np.abs(L[..., None] - lv[None, None, :]).argmin(-1)]


def by_ramp(L, ramp):
    xs = np.array([p[0] for p in ramp], np.float32)
    cols = np.array([sf.hexlin(p[1]) for p in ramp], np.float32)
    return np.stack([np.interp(L, xs, cols[:, k]) for k in range(3)], -1)


def colour_key(L, warm, c, hue=None, air=None, tint=None):
    """Colour by value and depth: the near ramp, leaning to the far ramp as the air thickens, the sky its own; the
    light's own hue where lamplight lies; L* kept."""
    rgb = by_ramp(L, c["ramp"])
    if air is not None and "ramp_far" in c:
        t = np.clip(air, 0, 1)[..., None] ** c.get("far_gamma", 1.0)
        rgb = rgb * (1 - t) + by_ramp(L, c["ramp_far"]) * t
    if air is not None and "ramp_sky" in c:
        rgb = np.where((air < 0)[..., None], by_ramp(L, c["ramp_sky"]), rgb)
    if tint is not None:
        # a mass's own grey (wet granite warm, painted boards cool): its hue at the ramp's value
        tk = tint[..., 3:4]
        tc = tint[..., :3] / np.maximum(sf.luma(tint[..., :3])[..., None], 1e-4) * sf.luma(rgb)[..., None]
        rgb = rgb * (1 - tk) + tc * tk
    wcol = sf.hexlin(c["warm"])[None, None, :] if hue is None else hue
    y = sf.from_lstar(L)
    wrgb = wcol * (y / np.maximum(sf.luma(wcol), 1e-4))[..., None]
    wrgb = np.clip(wrgb, 0, None)
    over = wrgb.max(-1, keepdims=True)
    wrgb = np.where(over > 1, wrgb / over + (1 - 1 / over) * 0.9, wrgb)
    k = (warm * c.get("warm_share", 1.0))[..., None]
    out = rgb * (1 - k) + wrgb * k
    # keep each pixel's designed value
    out *= (y / np.maximum(sf.luma(out), 1e-5))[..., None]
    return np.clip(out, 0, 1)


def swatches(c, hgt, wid):
    sw = c["swatches"]
    strip = np.zeros((hgt, wid, 3), np.float32)
    for i, hx in enumerate(sw):
        strip[:, i * wid // len(sw):(i + 1) * wid // len(sw)] = sf.hexlin(hx)
    return strip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("view")
    ap.add_argument("moment")
    ap.add_argument("--recipe", default=os.path.join(AD, "directions.json"))
    ap.add_argument("--only", default=None)
    ap.add_argument("--out", default=os.path.join(AD, "directions"))
    a = ap.parse_args()
    rec = json.load(open(a.recipe))
    frames = json.load(open(os.path.join(AD, "frames.json")))
    view = design_view(rec, frames, a.view)
    full = sf.load_passes(a.view)
    img = sf.load_render(a.view, a.moment)
    lit_full = sf.lit_panes(img, full, 0.08)
    sw = frames["moments"][a.moment].get("sun_warm")
    if sw:
        g = sf.load_render(a.view, a.moment, "grey")
        warmth = (g[..., 0] - g[..., 2]) / np.maximum(g.mean(-1), 1e-3)
        full["sun"] = sf.blur(sf.smoothstep(*sw, warmth), 1.0) * (~full["sky"])
    ps = {k: half(v) for k, v in full.items() if isinstance(v, np.ndarray)}
    lit = half(sf.blur(lit_full.astype(np.float32), 1.0)) > 0.3
    h, w = ps["dist"].shape
    rays, basis = sf.camera_rays(view["pos"], view["target"], view["fov"], w, h)
    P = np.array(view["pos"], np.float32)[None, None, :] + rays * ps["dist"][..., None]
    cam = (view["pos"], basis)
    os.makedirs(a.out, exist_ok=True)
    for name, d0 in rec["directions"].items():
        if a.only and name != a.only:
            continue
        d = for_moment(d0, a.moment)
        if d is None:
            continue
        L, warm, hue, air, tint = paint(d, view, kinds_of(rec, frames), P, ps, cam, w, h, rays, lit)
        Le = down(L, 4)
        if d.get("posterize"):
            Le = inks(Le, d["inks"])
        base = os.path.join(a.out, f"{name}-{a.view}-{a.moment}")
        g = sf.srgb(sf.from_lstar(Le))
        sf.write_png(f"{base}-eighth.png", (np.repeat(g[..., None], 3, -1) * 255).round())
        key = colour_key(Le, down(warm, 4), d["colour"], down(hue, 4), down(air, 4), down(tint, 4))
        key = np.concatenate([key, swatches(d["colour"], 14, key.shape[1])], 0)
        sf.write_png(f"{base}-key.png", (sf.srgb(key) * 255).round())
        bands = np.clip((Le / 20).astype(np.int32), 0, 4)
        print(name, "values", [round(100.0 * float((bands == b).mean()), 1) for b in range(5)])


if __name__ == "__main__":
    main()
