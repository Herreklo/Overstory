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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("view")
    ap.add_argument("moment")
    ap.add_argument("--recipe", default=os.path.join(AD, "styles.json"))
    ap.add_argument("--only", default=None)
    ap.add_argument("--out", default=os.path.join(AD, "styles"))
    a = ap.parse_args()
    rec = json.load(open(a.recipe))
    if "masses" not in rec:
        rec["masses"] = json.load(open(os.path.join(AD, "directions.json")))["masses"]
    frames = json.load(open(os.path.join(AD, "frames.json")))
    view = st.design_view(rec, frames, a.view)
    full = sf.load_passes(a.view)
    img = sf.load_render(a.view, a.moment)
    lit_full = sf.lit_panes(img, full, 0.08)
    ps = {k: st.half(v) for k, v in full.items() if isinstance(v, np.ndarray)}
    lit = st.half(sf.blur(lit_full.astype(np.float32), 1.0)) > 0.3
    h, w = ps["dist"].shape
    rays, basis = sf.camera_rays(view["pos"], view["target"], view["fov"], w, h)
    ps["ray"] = rays
    P = np.array(view["pos"], np.float32)[None, None, :] + rays * ps["dist"][..., None]
    cam = (view["pos"], basis)
    spec = view["masses"]
    lab0 = st.mass_labels(spec, P, ps)
    (fx, fy), _, _ = [q[0] for q in sf.project(np.array([view["focus"]], np.float32), cam[0], basis, w, h)]
    os.makedirs(a.out, exist_ok=True)
    for name, d0 in rec["directions"].items():
        if a.only and name != a.only:
            continue
        d = st.for_moment(d0, a.moment)
        if d is None:
            continue
        lab = st.clean_labels(lab0, d.get("clean_px", 0))
        raw = ps
        if d.get("calm_px"):
            # calm planes: a stone's or a board's own tilt is not drawn; lines still come from the true form
            n2 = np.stack([sf.blur(ps["normal"][..., k], d["calm_px"]) for k in range(3)], -1)
            n2 /= np.maximum(np.linalg.norm(n2, axis=-1, keepdims=True), 1e-4)
            keep = np.isin(lab, [i for i, m in enumerate(spec) if m["name"] in d.get("calm_keep", [])])
            n2 = np.where(keep[..., None], raw["normal"], n2)
            ps = {**raw, "normal": n2, "calm": d["calm_px"]}
        L, warm, hue, air, tint = st.paint(d, view, st.kinds_of(rec, frames), P, ps, cam, w, h, rays, lit)
        s = d["styling"]
        if s["kind"] == "woodblock":
            if "cut" in s:
                # white-line cuts: the block carved away where an edge catches the sky (tread noses, copings)
                L = np.where(ps["sky"], L, L + s["cut"]["L"] * lines(P, raw, lab, spec, warm, air, s["cut"]))
            rgb = woodblock(L, warm, air, lab, spec, ps, s)
        elif s["kind"] == "lightline":
            L, warm = lightline(L, warm, air, lab, spec, raw, P, s)
            rgb = st.colour_key(L, warm, d["colour"], hue, air, tint)
        else:
            rgb = twoink(L, warm, air, lab, spec, ps, s)
        rgb = np.clip(rgb, 0, 1)
        base = os.path.join(a.out, f"{name}-{a.view}-{a.moment}")
        Le = st.down(sf.lstar(sf.luma(rgb)), 4)
        g = sf.srgb(sf.from_lstar(Le))
        sf.write_png(f"{base}-eighth.png", (np.repeat(g[..., None], 3, -1) * 255).round())
        key = st.down(rgb, 2)
        sw = d["colour"]["swatches"] if "colour" in d else s["swatches"]
        key = np.concatenate([key, st.swatches({"swatches": sw}, 16, key.shape[1])], 0)
        sf.write_png(f"{base}-key.png", (sf.srgb(key) * 255).round())
        cx = int(np.clip(fx - w // 4, 0, w // 2))
        cy = int(np.clip(fy - h // 4, 0, h // 2))
        sf.write_png(f"{base}-detail.png", (sf.srgb(rgb[cy:cy + h // 2, cx:cx + w // 2]) * 255).round())
        ps = raw
        bands = np.clip((Le / 20).astype(np.int32), 0, 4)
        print(name, "values", [round(100.0 * float((bands == b).mean()), 1) for b in range(5)])


if __name__ == "__main__":
    main()
