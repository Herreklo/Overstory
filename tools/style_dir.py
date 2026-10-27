"""Direction keys that differ in styling, not only in value plan (reviews/lt1/art-direction/styles/).

    python3 tools/style_dir.py <view> <moment> [--only name] [--recipe reviews/lt1/art-direction/styles.json]

Each direction is a value plan painted by style_thumb.paint (masses the facts place, lights that are facts, the air)
and then drawn in one styling, all data in the recipe:

- woodblock: the picture printed from a few flat inks; each mass snapped to the nearest ink of the set, warm inks where
  a lamp lights, the air printed in steps, the sky the one graded ink. No line and no texture.
- lightline: calm planes with no mark inside them; the form drawn only by thin lines of light where an edge turns
  outwards or stands in front of something farther, each line as bright as what its bevel faces (the sky, a lamp),
  fading with distance.
- twoink: every value made of two inks of the hour over paper, cool and warm, overprinted for the darks; only a
  mass the recipe gives its own colour (a painted thing people keep) shows that colour, drained by the air.

Writes <name>-<view>-<moment>-eighth.png (grey, one-eighth), -key.png (quarter, with the inks), -detail.png (half
size, round the view's focus). Runs in Blender's Python (numpy) in a few seconds.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import style_frame as sf  # noqa: E402
import style_thumb as st  # noqa: E402

AD = sf.AD


def shifted(a, dy, dx):
    out = np.roll(a, (-dy, -dx), (0, 1))
    if dy:
        out[-dy if dy > 0 else 0:(None if dy > 0 else 1)] = a[-dy if dy > 0 else 0:(None if dy > 0 else 1)]
    if dx:
        out[:, -dx if dx > 0 else 0:(None if dx > 0 else 1)] = a[:, -dx if dx > 0 else 0:(None if dx > 0 else 1)]
    return out


def edges(P, n, dist, sky, lab, deg, rel):
    """Where the form turns outwards (normals part by more than deg and the neighbour falls behind this plane) or
    stands in front of something farther (a depth step of more than rel onto another mass, or the sky): the edge's
    own facing, the bevel between its two planes, is returned with it. A joint's gap is no edge."""
    h, w = dist.shape
    mask = np.zeros((h, w), np.float32)
    bevel = np.zeros((h, w, 3), np.float32)
    cosd = np.cos(np.radians(deg))
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nn, nP, nd, ns = shifted(n, dy, dx), shifted(P, dy, dx), shifted(dist, dy, dx), shifted(sky, dy, dx)
        step = ns | (((nd - dist) / np.maximum(dist, 1e-3) > rel) & (shifted(lab, dy, dx) != lab))
        turn = ((n * nn).sum(-1) < cosd) & ~ns & (np.abs(nd - dist) / np.maximum(dist, 1e-3) < rel) \
            & (((nP - P) * n).sum(-1) < -0.002 * dist)
        e = (step | turn) & ~sky
        b = np.where(step[..., None], n, n + nn)
        bevel = np.where((e & (mask < 0.5))[..., None], b, bevel)
        mask = np.maximum(mask, e.astype(np.float32))
    bevel /= np.maximum(np.linalg.norm(bevel, axis=-1, keepdims=True), 1e-4)
    return mask, bevel


def lines(P, ps, lab, spec, warm, air, ln):
    """The edges a styling draws: thin lines, specks of under three pixels dropped, each as strong as what its
    bevel faces (the sky above, a lamp), by mass and by a house's surface kind, fading with distance."""
    mask, bevel = edges(P, ps["normal"], ps["dist"], ps["sky"], lab, ln["deg"], ln["rel"])
    mask = mask * (sf.box(mask, 1) * 9 >= 3)
    near = sf.smoothstep(ln["far_m"], ln["near_m"], ps["dist"])
    weight = by_mass(ln.get("masses", {}), spec, lab, "line", ln.get("default", 1.0))
    for k, wk in ln.get("kinds", {}).items():
        weight = np.where((ps["cls"] == 2) & (ps["kind"] == int(k)), weight * wk, weight)
    # a wet edge shows the sky where its bevel turns the eye's ray upwards: a tread nose does, a joint between two
    # stones or a board's lap mostly does not
    v = ps["ray"]
    R = v - 2 * (v * bevel).sum(-1, keepdims=True) * bevel
    up = sf.smoothstep(ln.get("r0", 0.05), ln.get("r1", 0.5), R[..., 2])
    catch = ln["base"] + ln["up"] * up + ln["lamp"] * np.clip(warm, 0, 1)
    wide = np.maximum(mask, sf.blur(mask, ln.get("soft_px", 0.6)) * near * 1.6)
    return np.clip(wide, 0, 1) * near * weight * (1 - np.clip(air, 0, 1)) * catch


def by_mass(values, spec, lab, key, default):
    """A per-mass setting, inherited through `like` as the masses' designs are, else the default."""
    out = np.full(lab.shape, default, np.float32)
    parent = {m["name"]: m.get("like", "rest") for m in spec}
    for i, m in enumerate(spec):
        sel = lab == i
        name = m["name"]
        while name not in values and name != "rest":
            name = parent.get(name, "rest")
        if sel.any() and name in values:
            out[sel] = values[name].get(key, default)
    return out


def ink_colour(cool, warm, paper, L, wk):
    """Two inks over paper: the warm share wk of the coverage warm, the rest cool, the coverage found so that the
    print has the value L; past the paper's own value the paper shows."""
    y = sf.from_lstar(L)
    pc, tc, tw = sf.hexlin(paper), sf.hexlin(cool), sf.hexlin(warm)
    lo, hi = np.zeros_like(y), np.full_like(y, 12.0)
    w = wk[..., None]
    for _ in range(26):
        k = (lo + hi) * 0.5
        c = pc * np.power(tc, (1 - w) * k[..., None]) * np.power(tw, w * k[..., None])
        dark = sf.luma(c) < y
        hi, lo = np.where(dark, k, hi), np.where(dark, lo, k)
    k = (lo + hi) * 0.5
    return pc * np.power(tc, (1 - w) * k[..., None]) * np.power(tw, w * k[..., None])


def woodblock(L, warm, air, lab, spec, ps, s):
    """Each pixel takes the nearest ink of the set (the sky keeps its grade), the warm inks where a lamp lights."""
    lv = np.array([i[0] for i in s["inks"]], np.float32)
    idx = np.abs(L[..., None] - lv[None, None, :]).argmin(-1)
    cool = np.array([sf.hexlin(i[1]) for i in s["inks"]], np.float32)[idx]
    hot = np.array([sf.hexlin(i[2]) for i in s["inks"]], np.float32)[idx]
    # a lamp's light printed as one smooth warm shape, not the stencil of every stone's shadow
    w = ((sf.blur(warm, s.get("warm_soft_px", 0)) > s.get("warm_at", 0.35)) & (L > s.get("warm_min_L", 0))).astype(np.float32)
    rgb = cool * (1 - w[..., None]) + hot * w[..., None]
    sky_rgb = st.by_ramp(L, s["sky_ramp"])
    rgb = np.where(ps["sky"][..., None], sky_rgb, rgb)
    return rgb


def lightline(L, warm, air, lab, spec, ps, P, s):
    """Calm planes; lines of light at the edges, each as bright as what its bevel faces."""
    k = lines(P, ps, lab, spec, warm, air, s["line"])
    Lout = np.where(ps["sky"], L, L + s["line"]["L"] * k)
    lw = np.clip(warm * k * 2, 0, 1)
    return np.clip(Lout, 0, 100), np.maximum(warm, lw)


def twoink(L, warm, air, lab, spec, ps, s):
    wk = np.clip(warm * s.get("warm_share", 1.0), 0, 1)
    rgb = ink_colour(s["cool"], s["warm"], s["paper"], L, wk)
    sky_rgb = ink_colour(s.get("sky_cool", s["cool"]), s["warm"], s["paper"], L, wk * 0)
    rgb = np.where(ps["sky"][..., None], sky_rgb, rgb)
    own = s.get("own", {})
    for i, m in enumerate(spec):
        if m["name"] in own:
            sel = lab == i
            col = sf.hexlin(own[m["name"]]["srgb"])
            y = sf.from_lstar(L)
            c = col * (y / max(sf.luma(col), 1e-4))[..., None]
            k = (own[m["name"]].get("k", 0.8) * (1 - s.get("own_drain", 1.0) * np.clip(air, 0, 1)))[..., None] * sel[..., None]
            rgb = rgb * (1 - k) + np.clip(c, 0, 1) * k
    return rgb


def kept_colours(own, lab, spec, ps, view_name):
    """What people paint and keep, in its own colour: each entry's pixels (masses, classes, surface kinds) take
    the colour its coat has in the render under a flat sky (a fact the coats give), one colour per mass."""
    out = np.zeros(lab.shape + (3,), np.float32)
    k = np.zeros(lab.shape, np.float32)
    names = [m["name"] for m in spec]
    for o in own:
        sel = ~ps["sky"]
        if "masses" in o:
            sel = sel & np.isin(lab, [names.index(n) for n in o["masses"] if n in names])
        if "cls" in o:
            sel = sel & np.isin(ps["cls"], o["cls"])
        if "kinds" in o:
            sel = sel & np.isin(ps["kind"], o["kinds"])
        if "srgb" in o:
            out[sel], k[sel] = sf.hexlin(o["srgb"]), o.get("k", 1.0)
            continue
        ref = sf.load_render(view_name, o["from"])
        if ref.shape[:2] != lab.shape:
            ref = st.half(ref)
        for i in np.unique(lab[sel]):
            m = sel & (lab == i)
            out[m], k[m] = np.median(ref[m], 0), o.get("k", 1.0)
    return out, k


def coat_states(c, lab, spec, ps, view_name):
    """Each wall board's coat as one of a few states (fresh, aged, bare): the coats' own value under a flat sky,
    against its wall's median, averaged along the board so a state is a run of board, never a speck."""
    ref = sf.luma(sf.load_render(view_name, c["from"]))
    if ref.shape != lab.shape:
        ref = st.half(ref)
    names = [m["name"] for m in spec]
    sel = (ps["cls"] == 2) & np.isin(ps["kind"], c["kinds"])
    ratio = np.zeros(lab.shape, np.float32)
    inside = np.zeros(lab.shape, np.float32)
    for n in c["masses"]:
        if n not in names:
            continue
        m = sel & (lab == names.index(n))
        if m.sum() < 50:
            continue
        inside[m] = 1.0
    # against the wall's own light nearby (an eave's shade or a corner's occlusion is light, not a coat)
    k = lab.shape[1] / 960.0
    near = sf.blur(ref * inside, c["local_px"] * k) / np.maximum(sf.blur(inside, c["local_px"] * k), 1e-4)
    ratio = np.where(inside > 0, ref / np.maximum(near, 1e-4), 0.0).astype(np.float32)
    r = max(1, int(round(c["run_px"] * k)))
    avg = sf.box1(ratio, r, 1) / np.maximum(sf.box1(inside, r, 1), 1e-4)
    state = np.full(lab.shape, -1, np.int32)
    for i, edge in enumerate(c["below"]):
        state = np.where((inside > 0) & (state < 0) & (avg >= edge), i, state)
    return np.where((inside > 0) & (state < 0), len(c["below"]), state)


def keptprint(L, warm, air, lab, spec, ps, s, own, own_k):
    """Two inks of the hour printed in flat steps over paper: each pixel's value snapped to the print's steps and
    its warmth to the warm block's steps (the sky keeps its grade); a kept thing in its own colour at that value,
    drained by the air."""
    lv = np.array(s["steps"], np.float32)
    Lq = np.where(ps["sky"], L, lv[np.abs(L[..., None] - lv[None, None, :]).argmin(-1)])
    ws = np.array(s["warm_steps"], np.float32)
    wsoft = sf.blur(warm, s.get("warm_soft_px", 0))
    wq = ws[np.clip((wsoft[..., None] >= np.array(s["warm_at"], np.float32)).sum(-1), 0, len(ws) - 1)]
    wq = np.where(Lq < s.get("warm_min_L", 0), 0.0, wq)
    wq = np.where(ps["sky"], warm * s.get("sky_warm", 0.6), wq)
    rgb = ink_colour(s["cool"], s["warm"], s["paper"], Lq, wq * s.get("warm_share", 1.0))
    if "key" in s:
        # the deepest blocks take the key ink as a printer's third plate, so a dark is deep, never a pure hue
        ky = s["key"]
        kc = sf.hexlin(ky["srgb"])
        kc = kc * (sf.from_lstar(Lq) / max(sf.luma(kc), 1e-4))[..., None]
        a = (sf.smoothstep(ky["from_L"], ky.get("full_L", 8), Lq) * ky.get("k", 1.0))[..., None]
        rgb = rgb * (1 - a) + np.clip(kc, 0, 1) * a
    y = sf.from_lstar(Lq)
    c = own * (y / np.maximum(sf.luma(own), 1e-4))[..., None]
    over = c.max(-1, keepdims=True)
    c = np.where(over > 1, c / np.maximum(over, 1e-6), c)
    kk = (own_k * (1 - s.get("own_drain", 1.0) * np.clip(air, 0, 1)))[..., None]
    return rgb * (1 - kk) + c * kk


def stylise(d, rec, frames, view, P, ps, cam, w, h, rays, lit, lab0, view_name):
    """One direction in one light, in linear RGB."""
    spec = view["masses"]
    k = w / 960.0  # pixel sizes in the recipe are at half size
    lab = st.clean_labels(lab0, int(round(d.get("clean_px", 0) * k)))
    raw = ps
    if d.get("calm_px"):
        # calm planes: a stone's or a board's own tilt is not drawn; lines still come from the true form
        n2 = np.stack([sf.blur(ps["normal"][..., c], d["calm_px"] * k) for c in range(3)], -1)
        n2 /= np.maximum(np.linalg.norm(n2, axis=-1, keepdims=True), 1e-4)
        keep = np.isin(lab, [i for i, m in enumerate(spec) if m["name"] in d.get("calm_keep", [])])
        n2 = np.where(keep[..., None], raw["normal"], n2)
        ps = {**raw, "normal": n2, "calm": d["calm_px"]}
    L, warm, hue, air, tint = st.paint(d, view, st.kinds_of(rec, frames), P, ps, cam, w, h, rays, lit)
    s = d["styling"]
    if s["kind"] == "woodblock":
        if "cut" in s:
            # white-line cuts: the block carved away where an edge catches the sky (tread noses, copings)
            L = np.where(ps["sky"], L, L + s["cut"]["L"] * lines(P, raw, lab, spec, warm, air, scaled(s["cut"], k)))
        rgb = woodblock(L, warm, air, lab, spec, ps, scaled(s, k))
    elif s["kind"] == "lightline":
        L, warm = lightline(L, warm, air, lab, spec, raw, P, {**s, "line": scaled(s["line"], k)})
        rgb = st.colour_key(L, warm, d["colour"], hue, air, tint)
    elif s["kind"] == "keptprint":
        if "cut" in s:
            L = np.where(ps["sky"], L, L + s["cut"]["L"] * lines(P, raw, lab, spec, warm, air, scaled(s["cut"], k)))
        if "coats" in s:
            # history in whole runs of board: each coat state a value step (and bare wood the warm ink)
            c = s["coats"]
            cs = coat_states(c, lab, spec, raw, view_name)
            for i, st_ in enumerate(c["states"]):
                L = np.where(cs == i, L + st_.get("dL", 0), L)
                warm = np.where(cs == i, np.maximum(warm, st_.get("warm", 0)), warm)
        own, own_k = kept_colours(s.get("own", []), lab, spec, raw, view_name)
        rgb = keptprint(L, warm, air, lab, spec, ps, scaled(s, k), own, own_k)
    else:
        rgb = twoink(L, warm, air, lab, spec, ps, s)
    return np.clip(rgb, 0, 1)


def scaled(s, k):
    return {**s, **{key: s[key] * k for key in ("soft_px", "warm_soft_px") if key in s}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("view")
    ap.add_argument("moment")
    ap.add_argument("--recipe", default=os.path.join(AD, "styles.json"))
    ap.add_argument("--only", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--frame", action="store_true", help="the full frame, at full size, into frames/")
    a = ap.parse_args()
    rec = json.load(open(a.recipe))
    rec["masses"] = json.load(open(os.path.join(AD, "directions.json")))["masses"] + rec.get("masses_more", [])
    frames = json.load(open(os.path.join(AD, "frames.json")))
    view = st.design_view(rec, frames, a.view)
    full = sf.load_passes(a.view)
    img = sf.load_render(a.view, a.moment)
    lit_full = sf.lit_panes(img, full, 0.08)
    sw = frames["moments"][a.moment].get("sun_warm")
    if sw:
        # where the sun falls is a fact the render's grey light already draws: its warm share
        g = sf.load_render(a.view, a.moment, "grey")
        warmth = (g[..., 0] - g[..., 2]) / np.maximum(g.mean(-1), 1e-3)
        full["sun"] = sf.blur(sf.smoothstep(*sw, warmth), 1.0) * (~full["sky"])
    size = (lambda v: v) if a.frame else st.half
    ps = {k: size(v) for k, v in full.items() if isinstance(v, np.ndarray)}
    lit = size(sf.blur(lit_full.astype(np.float32), 1.0)) > 0.3
    h, w = ps["dist"].shape
    rays, basis = sf.camera_rays(view["pos"], view["target"], view["fov"], w, h)
    ps["ray"] = rays
    P = np.array(view["pos"], np.float32)[None, None, :] + rays * ps["dist"][..., None]
    cam = (view["pos"], basis)
    lab0 = st.mass_labels(view["masses"], P, ps)
    (fx, fy), _, _ = [q[0] for q in sf.project(np.array([view["focus"]], np.float32), cam[0], basis, w, h)]
    out = a.out or os.path.join(AD, "frames" if a.frame else "styles")
    os.makedirs(out, exist_ok=True)
    for name, d0 in rec["directions"].items():
        if a.only and name != a.only:
            continue
        d = st.for_moment(d0, a.moment)
        if d is None:
            continue
        rgb = stylise(d, rec, frames, view, P, ps, cam, w, h, rays, lit, lab0, a.view)
        e = 8 if a.frame else 4
        Le = st.down(sf.lstar(sf.luma(rgb)), e)
        g = sf.srgb(sf.from_lstar(Le))
        bands = np.clip((Le / 20).astype(np.int32), 0, 4)
        shares = [round(100.0 * float((bands == b).mean()), 1) for b in range(5)]
        if a.frame:
            base = os.path.join(out, f"{a.view}-{a.moment}")
            sf.write_png(f"{base}.png", (sf.srgb(rgb) * 255).round())
            grey = sf.srgb(sf.luma(rgb))
            sf.write_png(f"{base}-grey.png", (np.repeat(grey[..., None], 3, -1) * 255).round())
            five = sf.srgb(sf.from_lstar(st.inks(Le, [10, 30, 50, 70, 90])))
            sf.write_png(f"{base}-values.png", (np.repeat(five[..., None], 3, -1) * 255).round())
        else:
            base = os.path.join(out, f"{name}-{a.view}-{a.moment}")
            key = st.down(rgb, 2)
            swc = d["colour"]["swatches"] if "colour" in d else d["styling"]["swatches"]
            key = np.concatenate([key, st.swatches({"swatches": swc}, 16, key.shape[1])], 0)
            sf.write_png(f"{base}-key.png", (sf.srgb(key) * 255).round())
            cx = int(np.clip(fx - w // 4, 0, w // 2))
            cy = int(np.clip(fy - h // 4, 0, h // 2))
            sf.write_png(f"{base}-detail.png", (sf.srgb(rgb[cy:cy + h // 2, cx:cx + w // 2]) * 255).round())
        sf.write_png(f"{base}-eighth.png", (np.repeat(g[..., None], 3, -1) * 255).round())
        print(name, a.view, a.moment, "values", shares)


if __name__ == "__main__":
    main()
