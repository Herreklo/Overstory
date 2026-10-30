# paintover.py -- --passes DIR --geom FILE --still PNG --view eye --light lowsun|overcast --way P|Pc --out PNG [--debug DIR]
# Stage 10's target, painted in code over our own still (VD5): ref 58's manner on the boulder's real planes.
#  1. the edges' line: every arris bows with its faces' gentle dome; old arrises wander softly; breaks (the fresh face's
#     arrises, the spall, the foot) step in and out, their risers on the foliation or the frost joint; the crack's mouth
#     a notch. Done as a warp of the still along each projected arris, so the value shapes move as wholes.
#  2. the skin: faces graded lighter at the top, darker and cooler toward the foot; a fine granular speckle on the top;
#     brushy streaks down the old sides; a drybrush light on the lit old arrises; fresh breaks paler, clean and crisp,
#     old faces carrying a grey patina; the crack's notch; a cool dark foot.
# Changes forms and surfaces only, never a fact. Seeded: the same view paints the same.
import sys, os, json, math, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pio

ROOT = "/Users/oystein/code/Overstory"
a = sys.argv[sys.argv.index("--") + 1:]; arg = dict(zip(a[::2], a[1::2]))
G = json.load(open(arg["--geom"])); K = json.load(open(f"{ROOT}/blender/parts/rock/kit/kit.json")); B = K["beside"]
VIEW, LIGHT, WAY = arg["--view"], arg["--light"], arg["--way"]; DBG = arg.get("--debug")
SS = int(arg.get("--ss", 1)); BOX = [int(v) for v in arg["--box"].split(",")] if "--box" in arg else [0, 0, 2560, 1440]
WF, HF = 2560 * SS, 1440 * SS; OX, OY = BOX[0] * SS, BOX[1] * SS      # supersampled frame; the window painted in it
W, H = (BOX[2] - BOX[0]) * SS, (BOX[3] - BOX[1]) * SS
at = np.array(B["parts"][0]["at"], float); w7 = 7.0
CAM = {"eye": (at + B["eye"]["from"], np.array(B["eye"]["look"], float), B["eye"]["fov"]),
       "back": (at + B["back"]["from"], np.array(B["back"]["look"], float), B["back"]["fov"]),
       "street": (np.array([w7/2-9, -19, 1.6]), np.array([w7/2, 1, 3]) - np.array([w7/2-9, -19, 1.6]), 38),
       "high": (at + B["high"]["from"], np.array(B["high"]["look"], float), B["high"]["fov"]),
       "iso": (at + B["iso"]["from"], np.array(B["iso"]["look"], float), B["iso"]["fov"])}
cpos, look, fov = CAM[VIEW]
fw = look / np.linalg.norm(look); rt = np.cross(fw, [0, 0, 1]); rt /= np.linalg.norm(rt); upv = np.cross(rt, fw); tf = math.tan(math.radians(fov) / 2)


def proj(X):
    """levels-frame points [.., 3] to pixel x, y and depth"""
    d = np.asarray(X) + at - cpos; z = d @ fw
    return np.stack([WF / 2 + (d @ rt) / z / tf * HF / 2 - OX, HF / 2 - (d @ upv) / z / tf * HF / 2 - OY], -1), z


def unit(toward, slope=90.0):
    b, s = math.radians(toward), math.radians(slope)
    return np.array([math.sin(b) * math.sin(s), math.cos(b) * math.sin(s), math.cos(s)])


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


class Rng:
    def __init__(self, *key):
        self.r = np.random.default_rng(zlib.crc32("|".join(("r09-paint",) + tuple(map(str, key))).encode()))
    def u(self, lo=0.0, hi=1.0): return float(self.r.uniform(lo, hi))
    def skew(self, lo, hi, k=2): return lo + (hi - lo) * float(self.r.random()) ** k


def hash3(i, j, k, s):
    h = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (s * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177; h = h ^ (h >> 16)
    return (h & 0xFFFFFF).astype(np.float64) / 0xFFFFFF


def vnoise3(P, cell, s):
    """value noise in [0, 1] over world points [N, 3], cell metres"""
    Q = P / cell; i = np.floor(Q).astype(np.int64); f = Q - i; u = f * f * (3 - 2 * f); out = np.zeros(len(P))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                wgt = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                out += wgt * hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, s)
    return out


def fbm3(P, cell, s, oct=3):
    v, a_, t = 0.0, 1.0, 0.0
    for o in range(oct):
        v = v + a_ * vnoise3(P, cell / 2 ** o, s + 17 * o); t += a_; a_ *= 0.5
    return v / t


def noise1(x, s):
    i = np.floor(x).astype(np.int64); f = x - i; u = f        # linear: an old edge runs straight between kinks
    z = np.zeros_like(i)
    return (1 - u) * hash3(i, z, z, s) + u * hash3(i + 1, z, z, s)


# ------------------------------------------------------------------ passes
PD = arg["--passes"]
def passes(mesh):
    n = pio.load(f"{PD}/{VIEW}-{mesh}-N.exr"); p = pio.load(f"{PD}/{VIEW}-{mesh}-P.exr")
    return n[..., 3] > 0.5, n[..., :3] * 2 - 1, p[..., :3] - 50 - at
covN, Nn, Pn = passes("near"); covH, Nh, Ph = passes("high")
img_full = pio.load(arg["--still"])[..., :3].astype(np.float64)
def upsample(A_, k):
    if k == 1: return A_.copy()
    h_, w_ = A_.shape[:2]; ys = np.clip((np.arange(h_ * k) + 0.5) / k - 0.5, 0, h_ - 1.001); xs = np.clip((np.arange(w_ * k) + 0.5) / k - 0.5, 0, w_ - 1.001)
    y0_, x0_ = np.floor(ys).astype(int), np.floor(xs).astype(int); fy_, fx_ = (ys - y0_)[:, None, None], (xs - x0_)[None, :, None]
    return (A_[y0_][:, x0_] * (1 - fy_) * (1 - fx_) + A_[y0_][:, x0_ + 1] * (1 - fy_) * fx_ + A_[y0_ + 1][:, x0_] * fy_ * (1 - fx_) + A_[y0_ + 1][:, x0_ + 1] * fy_ * fx_)
img = upsample(img_full[BOX[1]:BOX[3], BOX[0]:BOX[2]], SS)
NF = np.array([f["n"] for f in G["faces"]]); OFF = np.array([f["off"] for f in G["faces"]]); KIND = [f["kind"] for f in G["faces"]]
KEY = [f["key"] for f in G["faces"]]
dist = np.where(covN, np.linalg.norm(Pn + at - cpos, axis=-1), np.inf)  # the near level's depth, for visibility
sets = {k: np.array(v) for k, v in G["sets"].items()}
Lkey = unit(200, 70) if LIGHT == "lowsun" else np.array([0.15, -0.2, 1.0]) / np.linalg.norm([0.15, -0.2, 1.0])
camdir = lambda X: (cpos - (X + at)) / np.linalg.norm(cpos - (X + at))
print(f"[paint] {VIEW} {LIGHT} {WAY}: rock px {covN.sum()}")

# the breaks' scars on the high level (sculpt.py's planes)
scar = np.full((H, W), -1e9); scarwhy = np.full((H, W), -1)
for bi, b in enumerate(G["breaks"]):
    d = Ph @ np.array(b["f"]) - b["of"]
    for wn, ow in b["walls"]:
        d = np.minimum(d, Ph @ np.array(wn) - ow)
    upd = covH & (d > scar); scar = np.where(upd, d, scar); scarwhy = np.where(upd, bi, scarwhy)
scar = np.where(covH, scar, -1e9)

# ------------------------------------------------------------------ 1. the edges' line, as a warp
E = K.get("_r09", {})
BOW = {"worn": 0.04, "facet": 0.035, "sea": 0.04, "joint": 0.02, "pluck": 0.012}   # share of the arris: a long edge bows out gently
WANDER = (0.016, 0.30)          # metres: amplitude, wavelength of an old arris's soft wander
JOG = dict(stepM=(0.04, 0.15), depthM=(0.01, 0.035), skew=2)   # a break's steps along a plane of the structure
# each run's steps: length (m, skewed few big to many small) and depth (m)
STEPS = {"old": ((0.15, 0.5), (0.012, 0.035)), "arris": ((0.06, 0.25), (0.008, 0.025)), "corner": ((0.10, 0.40), (0.05, 0.15)),
         "fresh": ((0.10, 0.35), (0.05, 0.12)), "foot": ((0.10, 0.35), (0.05, 0.10)), "ledge": ((0.08, 0.2), (0.025, 0.045))}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
Dx = np.zeros((H, W)); Dy = np.zeros((H, W)); DJx = np.zeros((H, W)); DJy = np.zeros((H, W)); risers = []
fresh_kinds = {"pluck"}
def faceidx(k): return KEY.index(k)
breaks_on = {}  # arris (a, b) -> list of (s0, s1) in its own length share where a break steps
for b in G["breaks"]:
    # the arris each break sits on: the one its point is nearest
    q = np.array(b["at"]); best = None
    for e in G["edges"]:
        P0, P1 = np.array(e["P0"]), np.array(e["P1"]); t = P1 - P0; ln = np.linalg.norm(t); t /= ln
        s = np.clip((q - P0) @ t, 0, ln); dd = np.linalg.norm(q - (P0 + s * t))
        if best is None or dd < best[0]: best = (dd, (e["a"], e["b"]), s / ln)
    if b["why"] != "corner":
        breaks_on.setdefault(best[1], []).append((max(0.0, best[2] - 0.16), min(1.0, best[2] + 0.16), b["why"]))
    else:  # the spall: its outline steps on both arrises leaving its corner
        breaks_on.setdefault(best[1], []).append((max(0.0, best[2] - 0.3), min(1.0, best[2] + 0.3), "corner"))

# the crack's mouth: where the drawn crack meets an old arris, found in the still itself (the darkest thin mark on an
# old arris above a side, out of the scars), so the notch sits on the crack's own trace
def boxblur(A_, r):
    c = np.cumsum(np.cumsum(np.pad(A_, ((r + 1, r), (r + 1, r)), mode="edge"), 0), 1)
    return (c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:] - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1]) / (2 * r + 1) ** 2
lum0 = img @ np.array([0.2126, 0.7152, 0.0722]); ratio = lum0 / np.maximum(boxblur(lum0, 9 * SS), 1e-4)
NOTCH = (0.16, 0.075); MOUTH, best = None, 0.75
# the crack's face, by paint.py's rule (kit.json skin.crack): the biggest side facing the mass's front
Cr = K["skin"]["crack"]; Xb = next(x for x in K["mass"]["masses"] if x["id"] == "boulder"); frontv = unit(Xb["front"])
def area(i):
    pts = np.array([q for e in G["edges"] if i in (faceidx(e["a"]), faceidx(e["b"])) for q in (e["P0"], e["P1"])])
    if len(pts) < 3: return 0.0
    u_ = np.cross(NF[i], [0.3, 0.5, 0.8]); u_ /= np.linalg.norm(u_); v_ = np.cross(NF[i], u_); q = np.stack([pts @ u_, pts @ v_], -1)
    q = q[np.lexsort((q[:, 1], q[:, 0]))]; hull = []
    for pass_ in (q, q[::-1]):
        h = []
        for pt in pass_:
            while len(h) >= 2 and np.cross(h[-1] - h[-2], pt - h[-2]) <= 0: h.pop()
            h.append(pt)
        hull += h[:-1]
    # back to 3D, clipped to what stands out of the turf (z >= 0), as the page counts it
    c0 = pts.mean(0); off = c0 @ NF[i]
    H3 = [off * NF[i] + h[0] * u_ + h[1] * v_ + 0 * c0 for h in hull]
    H3 = [p_ + NF[i] * (off - p_ @ NF[i]) for p_ in H3]
    clip = []
    for k in range(len(H3)):
        p_, q_ = H3[k], H3[(k + 1) % len(H3)]
        if p_[2] >= 0: clip.append(p_)
        if (p_[2] >= 0) != (q_[2] >= 0): clip.append(p_ + (q_ - p_) * (p_[2] / (p_[2] - q_[2])))
    if len(clip) < 3: return 0.0
    q = np.array([[c @ u_, c @ v_] for c in clip])
    return 0.5 * abs(np.dot(q[:, 0], np.roll(q[:, 1], 1)) - np.dot(q[:, 1], np.roll(q[:, 0], 1)))
cand = [i for i in range(len(NF)) if NF[i] @ frontv >= Cr["front"] and abs(NF[i][2]) <= 0.6 and KIND[i] not in {"base"} | fresh_kinds]
CF = max(cand, key=area) if cand else -1
CF = KEY.index(arg["--crack"]) if "--crack" in arg else CF   # paint.py counts page texels; a review tool may name it
print("[paint] crack face", KEY[CF] if CF >= 0 else None, [(KEY[i], round(area(i), 2)) for i in cand])
for e in G["edges"]:
    A, Bf = faceidx(e["a"]), faceidx(e["b"])
    if CF not in (A, Bf) or {KIND[A], KIND[Bf]} & fresh_kinds or NF[Bf if A == CF else A][2] <= NF[CF][2]: continue
    P0, P1 = np.array(e["P0"]), np.array(e["P1"]); tw = P1 - P0; ln = np.linalg.norm(tw); tw /= ln
    Pm = (P0 + P1) / 2; c = camdir(Pm)
    if NF[A] @ c <= 0 or NF[Bf] @ c <= 0: continue
    low = A if NF[A][2] < NF[Bf][2] else Bf; uL = np.cross(NF[low], tw); uL = -uL if uL @ NF[A if low == Bf else Bf] > 0 else uL
    for s0 in np.arange(0.06, 0.94, 0.01 / ln):
        X = P0 + s0 * ln * tw + uL * np.array([[0.005], [0.012], [0.02]])
        pp, zz = proj(X); xi_, yi_ = np.clip(np.rint(pp).astype(int), 0, [W - 1, H - 1]).T
        if not covN[yi_, xi_].all() or (scar[yi_, xi_] > -0.03).any(): continue
        rr = float(ratio[yi_, xi_].mean())
        # a thin mark, not a shadow's edge: the arris either side of it is not dark
        Xn = P0 + np.clip(s0 + np.array([-0.05, 0.05]) / ln, 0, 1)[:, None] * ln * tw + uL * 0.012
        pn_, _ = proj(Xn); xn_, yn_ = np.clip(np.rint(pn_).astype(int), 0, [W - 1, H - 1]).T
        if rr < 0.8 and DBG: print("[mouth?]", e["a"], e["b"], round(float(s0), 2), round(rr, 2), round(float(ratio[yn_, xn_].min()), 2))
        if rr < best and ratio[yn_, xn_].min() > 0.85: best, MOUTH = rr, (e, float(s0))
if MOUTH: print(f"[paint] crack mouth on {MOUTH[0]['a']}/{MOUTH[0]['b']} at {MOUTH[1]:.2f} (ratio {best:.2f})")

for e in G["edges"]:
    A, Bf = faceidx(e["a"]), faceidx(e["b"]); nA, nB = NF[A], NF[Bf]
    P0, P1 = np.array(e["P0"]), np.array(e["P1"]); tw = P1 - P0; ln = float(np.linalg.norm(tw)); tw /= ln
    if max(P0[2], P1[2]) < 0.02: continue
    Pm = (P0 + P1) / 2; c = camdir(Pm); visA, visB = nA @ c > 0, nB @ c > 0
    if not (visA or visB): continue
    sil = visA != visB
    if sil and not visA: A, Bf, nA, nB, visA, visB = Bf, A, nB, nA, True, False
    (p0, p1), (z0, z1) = proj(np.stack([P0, P1]))
    seg = p1 - p0; L = float(np.linalg.norm(seg))
    if L < 6: continue
    ev = seg / L; nv = np.array([-ev[1], ev[0]])
    pm = proj(Pm[None])[0][0]
    uA = np.cross(tw, nA); uA *= -1 if uA @ (Pm - (Pm + nB)) > 0 and False else 1
    # in-plane directions away from the arris into each face
    uA = np.cross(nA, tw); uA = -uA if uA @ nB > 0 else uA
    uB = np.cross(nB, tw); uB = -uB if uB @ nA > 0 else uB
    bis = (nA + nB) / np.linalg.norm(nA + nB)
    jv = lambda v: (proj((Pm + 0.01 * v)[None])[0][0] - pm) / 0.01
    vA, vB, vb = jv(uA), jv(uB), jv(bis)
    side = vA @ nv  # A lies toward -nv if side < 0
    if side > 0: nv = -nv
    # visibility along the arris (the near level's depth buffer, or open ground for a silhouette)
    ts = np.linspace(0, 1, 64); Xs = P0[None] + np.outer(ts * ln, tw); ps, zs = proj(Xs)
    xi = np.clip(np.rint(ps[:, 0]).astype(int), 0, W - 1); yi = np.clip(np.rint(ps[:, 1]).astype(int), 0, H - 1)
    dd = np.linalg.norm(Xs + at - cpos, axis=-1)
    vis = np.zeros(64)
    for ox in (-2, 0, 2):
        for oy in (-2, 0, 2):
            xj, yj = np.clip(xi + ox, 0, W - 1), np.clip(yi + oy, 0, H - 1)
            vis = np.maximum(vis, (dist[yj, xj] > dd - 0.03).astype(float))
    if vis.mean() < 0.2: continue
    kinds = set(e["kinds"]); old = not (kinds & fresh_kinds)
    st = Rng("edge", e["a"], e["b"])
    # the bow (both faces' gentle dome lifts the arris along its bisector) and the soft wander of an old arris
    hb = min(BOW.get(e["kinds"][0], 0.02), BOW.get(e["kinds"][1], 0.02)) * ln
    s_ = np.linspace(0, 1, 512)
    delta_m = np.zeros(512)                       # metres: + A grows toward B (or the rock outward)
    bow_px = hb * 4 * s_ * (1 - s_) * (vb @ nv)
    if old:
        wsd = zlib.crc32((e["a"] + e["b"]).encode()) % 9973
        wav = WANDER[0] * (2 * noise1(s_ * ln / WANDER[1], wsd) - 1) * 0.7 + WANDER[0] * 0.3 * (2 * noise1(s_ * ln / (WANDER[1] / 2.3), wsd + 5) - 1)
        delta_m += wav * ss(0, 0.08, s_) * ss(1, 0.92, s_)
    # the breaks' steps, along the plane of the structure that crosses the arris most squarely
    jog_m = np.zeros(512); jogb_m = np.zeros(512); runs = list(breaks_on.get((e["a"], e["b"]), []) + breaks_on.get((e["b"], e["a"]), []))
    if not old:
        runs.append((0.06, 0.94, "arris"))
    elif not sil and (NF[A][2] >= 0.75) != (NF[Bf][2] >= 0.75):
        runs.append((0.08, 0.92, "old"))        # an old top/side border steps in and out along the layers
    if False:   # r09 try 3: no foot ledge (the grass hides it in the game too)
        c_ = st.u(0.3, 0.7); hw_ = st.u(0.08, 0.15); runs.append((c_ - hw_, c_ + hw_, "ledge"))   # the foot breaks out once
    fol = sets["foliation"]
    setn = fol if abs(fol @ tw) > 0.3 else max(sets.values(), key=lambda n: abs(n @ tw))
    stepping = []
    cdir = camdir(Pm); bsgn = 1 if (cdir @ nB) > (cdir @ nA) else -1   # a break's band lies on the face turned to the eye
    for r0, r1, why in runs:
        # the step lengths: a few big, more small (a skewed spread), never alike; cut where the run's length is used
        span_m = (r1 - r0) * ln; cuts_ = []; x = 0.0
        while True:
            x += st.skew(*STEPS[why][0], JOG["skew"])
            if x >= span_m - STEPS[why][0][0] * 0.6: break
            cuts_.append(x)
        edges_ = [r0] + [r0 + c_ / ln for c_ in cuts_] + [r1]
        n_ = len(edges_) - 1; scale = 0.5 if (sil and why != "ledge") else 1.0; dlo, dhi = STEPS[why][1]
        if why == "old":     # an old border: a soft walk in and out by small uneven steps
            lvl = [0.0]
            for k_ in range(n_ - 1):
                lvl.append(float(np.clip(lvl[-1] + st.skew(dlo, dhi, 2) * (1 if st.u() < 0.5 else -1), -dhi, dhi)))
            lvl = lvl[1:] + [0.0] if n_ > 1 else [0.0]
        elif why == "arris": # a fresh arris: straight, with a few small chips knocked out of it
            lvl = [st.skew(dlo, dhi, 2) * (-1 if sil else bsgn) if st.u() < 0.35 else 0.0 for k_ in range(n_)]   # on the outline a chip is a notch
        elif why == "ledge": # the foot: a ledge stands out, once or twice stepped
            d_ = st.skew(dlo, dhi, 1); lvl = [d_ if k_ % 2 == 0 else d_ * st.u(0.4, 0.7) for k_ in range(n_)]
        else:                # a flake knocked off: one bite into the face, stepping in by stages and out again
            sgn = bsgn if not sil else -1; peak = st.u(0.35, 0.65) * n_
            dmax = st.skew(dlo, dhi, 1)
            lvl = [sgn * dmax * float(np.clip(1 - abs(k_ + 0.5 - peak) / max(peak, n_ - peak, 1e-6), 0.25, 1)) * st.u(0.75, 1.0)
                   for k_ in range(n_)]
            lvl = [l_ if abs(k_ + 0.5 - peak) < 1.5 else sgn * st.u(0.02, 0.04) for k_, l_ in enumerate(lvl)]   # small steps beside
        for k_ in range(n_):
            x0_, x1_s = edges_[k_], edges_[k_ + 1]; dep = lvl[k_] * scale
            m = (s_ >= x0_) & (s_ < x1_s); jog_m[m] = dep; stepping.append((x0_, x1_s, dep))
            if why in ("corner", "fresh", "foot", "arris"): jogb_m[m] = dep
    tot = delta_m + jog_m
    to_px = np.where(tot > 0, vb @ nv if sil else vB @ nv, -(vA @ nv)) if not sil else np.full(512, vb @ nv)
    dpx = bow_px + tot * to_px
    vis_s = np.interp(s_, ts, vis); dpx *= vis_s
    mx = float(np.abs(dpx).max())
    if mx < 0.3: continue
    Lf = max(3.2 * mx, 5.0 * SS)
    # riser directions on each side: the set's trace on the face, in the image
    def rimg(n):
        tr = np.cross(setn, n); tr /= max(np.linalg.norm(tr), 1e-9); r = jv(tr); return r / max(np.linalg.norm(r), 1e-9)
    rA = rimg(nA); rB = rimg(nB) if not sil else rA
    lim = 0.8 if sil else 1.3
    shr = lambda r: float(np.clip((r @ ev) / (r @ nv if abs(r @ nv) > 1e-3 else 1e-3), -lim, lim))
    shA, shB = shr(rA), shr(rB)
    # the band
    x0, x1_ = int(max(0, min(p0[0], p1[0]) - Lf - 4)), int(min(W, max(p0[0], p1[0]) + Lf + 4))
    y0, y1_ = int(max(0, min(p0[1], p1[1]) - Lf - 4)), int(min(H, max(p0[1], p1[1]) + Lf + 4))
    X_ = xx[y0:y1_, x0:x1_] - p0[0]; Y_ = yy[y0:y1_, x0:x1_] - p0[1]
    t_img = (X_ * ev[0] + Y_ * ev[1]) / L; d_img = X_ * nv[0] + Y_ * nv[1]
    shear = np.where(d_img > 0, shB, shA)
    tk = t_img - d_img * shear / L                # where the riser through this pixel meets the arris
    # perspective: image share to arris share
    sk = np.clip((tk / z1) / ((1 - tk) / z0 + tk / z1), 0, 1)
    smooth_part = np.interp(sk, s_, (bow_px + delta_m * to_px) * vis_s)
    jog_part = np.interp(sk, s_, jog_m * to_px * vis_s, ) if stepping else 0.0
    if stepping:  # a step function: nearest, not interpolated
        jog_part = (jog_m * to_px * vis_s)[np.clip(np.rint(sk * 511).astype(int), 0, 511)]
    dp = smooth_part + jog_part
    inside = (t_img > -0.02) & (t_img < 1.02)
    phi = np.clip(1 - (d_img / Lf) ** 2, 0, 1) ** 2 * inside
    Dx[y0:y1_, x0:x1_] += nv[0] * dp * phi; Dy[y0:y1_, x0:x1_] += nv[1] * dp * phi
    if stepping:
        jb = (jogb_m * to_px * vis_s)[np.clip(np.rint(sk * 511).astype(int), 0, 511)]
        DJx[y0:y1_, x0:x1_] += nv[0] * jb * phi; DJy[y0:y1_, x0:x1_] += nv[1] * jb * phi
    for (s0, s1, dep), nxt in zip(stepping, stepping[1:] + [None]):
        if nxt is None: break
        sm = s1; tm = (sm * z0) / ((1 - sm) * z1 + sm * z0)   # arris share to image share
        k = int(np.clip(round(sm * 511), 0, 511))
        d1 = dep * to_px[max(k - 1, 0)] * vis_s[k]; d2 = nxt[2] * to_px[min(k + 1, 511)] * vis_s[k]
        b0 = bow_px[k] * vis_s[k] + delta_m[k] * to_px[k] * vis_s[k]
        if sil: continue
        risers.append(dict(p=p0 + tm * seg, nv=nv, rA=shA * ev + nv, rB=shB * ev + nv, dlo=b0 + min(d1, d2), dhi=b0 + max(d1, d2),
                           wall=setn * np.sign(setn @ tw) * np.sign(dep - nxt[2]), old=old, why=e["kinds"]))
    print(f"[edge] {e['a']:7s} {e['b']:7s} sil {int(sil)} old {int(old)} bow {hb*100:.1f} cm  max {mx:.1f} px  steps {len(stepping)} vis {vis.mean():.2f}")

# warp: each pixel takes the still where its content came from
sx = np.clip(xx - Dx, 0, W - 1.001); sy = np.clip(yy - Dy, 0, H - 1.001)
ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int); fx, fy = (sx - ix)[..., None], (sy - iy)[..., None]
def bil(A_):
    A_ = A_ if A_.ndim == 3 else A_[..., None]
    o = (A_[iy, ix] * (1 - fx) * (1 - fy) + A_[iy, ix + 1] * fx * (1 - fy) + A_[iy + 1, ix] * (1 - fx) * fy + A_[iy + 1, ix + 1] * fx * fy)
    return o
def near(A_):
    return A_[np.rint(sy).astype(int), np.rint(sx).astype(int)]
out = bil(img)
cov = near(covN) | near(covH); P = near(np.where(covH[..., None], Ph, Pn)); N = near(np.where(covH[..., None], Nh, Nn))
Sc = near(scar); Sw = near(scarwhy)
sx0 = np.clip(xx - (Dx - DJx), 0, W - 1.001); sy0 = np.clip(yy - (Dy - DJy), 0, H - 1.001)
n0 = lambda A_: A_[np.rint(sy0).astype(int), np.rint(sx0).astype(int)]
cov0 = n0(covN) | n0(covH); P0w = n0(np.where(covH[..., None], Ph, Pn))
if DBG:
    pio.save(f"{DBG}/{VIEW}-{LIGHT}-{WAY}-warp.png", out)

VLIFT = (0.22, 0.72)               # value = a + b v: 58's ladder, lit ~0.65, shade ~0.4, occlusion ~0.2
GRAIN = 0.009                      # metres: the stipple's dot
LIPW = 1.6                         # final pixels: the lit lip's width                # value = a + (1 - a) v^p: 58's shade planes sit in the middle values
SAT = 0.8 if LIGHT == 'lowsun' else 0.55
# ------------------------------------------------------------------ 2. the skin, in 58's manner
# each plane one value from the still's own light (its median), so planes meet crisply; the value then takes one colour
# ramp read from 58 (cream lit, pink-beige turned, mauve in shade, plum and aubergine in the occlusion); grain as crisp
# dots, a pale lip on the lit side of an arris, the crack a crisp plum line with a lip toward the light
rock = cov
ow = out.copy()                                   # the warped still: grass, ground and sky stay as rendered
lum = lambda c: c @ np.array([0.2126, 0.7152, 0.0722])
Lw = lum(ow)
grass = rock & (np.clip((0.80 - ow[..., 2] / np.maximum(ow[..., 1], 1e-3)) / 0.12, 0, 1) > 0.5)
ag = np.where(rock, np.clip((0.80 - ow[..., 2] / np.maximum(ow[..., 1], 1e-3)) / 0.12, 0, 1), 0)
# the plane each pixel lies on: the mass's face it is nearest outside of (the old geometry's bites filled); where a
# step moved an arris, the band it cut is its own facet, a fresh break between the two faces
ri = np.nonzero(rock); NFn = len(NF); IB = KEY.index("base")
def planelab(Q):
    d = Q @ NF.T - OFF; d[:, IB] = -9; return np.argmax(d, -1)
pl = np.full((H, W), -1); pl[ri] = planelab(P[ri]); pl0 = np.full((H, W), -1); pl0[ri] = planelab(P0w[ri])
band = rock & ((pl != pl0) | ~cov0)
z = P[..., 2]; nP = np.zeros((H, W, 3)); nP[ri] = NF[pl[ri]]
pluck = rock & np.isin(pl, [i for i, k in enumerate(KIND) if k == "pluck"]) & ~band
fresh = pluck | band
old = rock & ~fresh
topf = rock & (nP[..., 2] >= 0.75) & ~band; side = rock & ~topf
kd = np.clip(nP @ Lkey, 0, 1)
# a. each plane's value: the median of the still on it (grass left out), split in two where a cast shadow crosses it
Lb = boxblur(Lw, 2 * SS); reg = np.full((H, W), -1); V = np.where(rock, Lw, 0.0); nreg = 0
for k in np.unique(pl[ri]):
    if k >= 1000: continue
    m = (pl == k); mv = m & ~grass & ~band
    if mv.sum() < 25:
        V[m] = np.median(Lw[m]) if m.sum() else 0; reg[m] = nreg; nreg += 1; continue
    vals = Lb[mv]; t = None
    if mv.sum() > 300:
        hs, ed_ = np.histogram(vals, 64); c_ = (ed_[:-1] + ed_[1:]) / 2; w0 = np.cumsum(hs); w1 = w0[-1] - w0
        m0 = np.cumsum(hs * c_) / np.maximum(w0, 1); m1 = ((hs * c_).sum() - np.cumsum(hs * c_)) / np.maximum(w1, 1)
        kk = int(np.argmax(w0 * w1 * (m0 - m1) ** 2)); tt = c_[kk]
        lo_, hi_ = vals[vals < tt], vals[vals >= tt]
        if min(len(lo_), len(hi_)) > 0.12 * len(vals) and np.median(hi_) > 1.45 * np.median(lo_): t = tt
    if t is None:
        V[m] = np.median(vals); reg[m] = nreg; nreg += 1
    else:
        hi_m = m & (Lb >= t)
        V[hi_m] = np.median(vals[vals >= t]); V[m & ~hi_m] = np.median(vals[vals < t]); reg[hi_m] = nreg; reg[m & ~hi_m] = nreg + 1; nreg += 2
    if DBG: print(f"[skin] plane {k:2d} {'face ' + KEY[k] if k < NFn else 'break'} n {m.sum():6d} kd {float(kd[m].mean()):.2f} v {float(np.median(vals)):.3f}{' split' if t is not None else ''}")
Vface = {int(k): float(np.median(Lb[(pl == k) & ~grass & ~band])) for k in np.unique(pl[ri]) if ((pl == k) & ~grass & ~band).sum() > 25}
bi_ = np.nonzero(band)
V[bi_] = [1.06 * (max(Vface.get(int(a_), 0.3), Vface.get(int(b_), 0.3)) if c_ else Vface.get(int(a_), 0.3))
          for a_, b_, c_ in zip(pl[bi_], pl0[bi_], cov0[bi_])]
pl = np.where(band, 1000 + pl0 + 50 * pl, pl)      # each band its own region, so its edges are crisp and lipped
# 58 holds its shade planes up in the middle values: lift the darks, keep the lights
V = np.where(rock, VLIFT[0] + VLIFT[1] * V, V)
# b. within a plane: lighter at its top, darker toward the foot; the top barely
g = np.zeros((H, W))
for k in np.unique(pl[ri]):
    m = pl == k
    if m.sum() < 30 or k >= 1000: continue
    zz = z[m]; lo_, hi_ = np.percentile(zz, 2), np.percentile(zz, 98)
    if hi_ - lo_ > 0.03: g[m] = np.clip((zz - lo_) / (hi_ - lo_), 0, 1)
V *= np.where(side, 1 + 0.18 * (g - 0.5), np.where(topf, 1 + 0.03 * (g - 0.5), 1))
V *= np.where(side, 1 - 0.10 * (1 - ss(0.0, 0.30, z)), 1)
V = np.where(pluck, V * 1.06, V)
# c. the grain, crisp dots: on the top a sandy stipple (pale and dark, in sponge-like clusters); down the old sides dark
#    stipple, thick in the runs under the top's lips and toward the foot; a few pale scumbles on the lit sides
Pw = P.reshape(-1, 3)
pxm = HF / 2 / tf / np.maximum(np.linalg.norm(P + at - cpos, axis=-1), 0.1)
seen = ss(60 * SS, 180 * SS, pxm); pxf = float(np.median(pxm[rock])) / SS
clus = fbm3(Pw, 0.07, 41, 2).reshape(H, W)
na = vnoise3(Pw, GRAIN, 51).reshape(H, W); nb = vnoise3(Pw, GRAIN, 52).reshape(H, W); nc = vnoise3(Pw, 0.006, 53).reshape(H, W)
dot = lambda n_, dens: ss(0.0, 0.05, n_ - (1 - dens))
strk = np.zeros((H, W))
for i in range(NFn):
    n = NF[i]
    if abs(n[2]) > 0.75 or KIND[i] in ("pluck", "base"): continue
    m = old & (pl == i)
    if m.sum() < 50: continue
    hdir = np.cross([0, 0, 1.0], n); hdir /= np.linalg.norm(hdir); hc = P[m] @ hdir
    rs = Rng("streak", KEY[i]); val = np.zeros(m.sum()); span = (hc.min(), hc.max())
    for _ in range(int(max(2, (span[1] - span[0]) / 0.09))):
        c0 = rs.u(*span); wdt = rs.skew(0.015, 0.06); reach = rs.u(0.25, 0.8); sgn = -1 if rs.u() < 0.75 else 0.8
        prof = np.clip(1 - np.abs(hc - c0) / wdt, 0, 1) ** 0.5
        down = np.clip((1 - g[m]) / reach, 0, 1); val += sgn * rs.u(0.5, 1.0) * prof * ss(0.0, 0.12, 1 - g[m]) * (1 - ss(0.75, 1.0, down))
    Pm_ = P[m]; brk = vnoise3(np.stack([Pm_ @ hdir / 0.005, Pm_[:, 2] / 0.04, np.zeros(len(Pm_))], -1), 1.0, 31 + i)
    strk[m] = val * (0.5 + 0.9 * brk)
dens_top = topf * (0.18 + 0.30 * clus)
dens_side = old & side
dens_dark = dens_side * np.clip(0.10 + 0.25 * (1 - g) ** 1.5 + 0.45 * np.clip(-strk, 0, 1) + 0.2 * (1 - ss(0, 0.25, z)), 0, 0.7)
nt = vnoise3(Pw, 0.0055, 54).reshape(H, W); nf_ = vnoise3(Pw, 0.0035, 55).reshape(H, W); nf2 = vnoise3(Pw, 0.0035, 56).reshape(H, W)
V += seen * (0.035 * dot(nt, topf * (0.40 + 0.35 * clus)) - 0.012 * dot(nb, topf * 0.3) - 0.07 * dot(nb, dens_dark * (1 - 0.6 * ss(0.2, 0.5, kd))))
V += seen * fresh * (0.065 * dot(nf_, 0.22 * np.ones((H, W))) - 0.065 * dot(nf2, 0.22 * np.ones((H, W))))
shd = side & old & (kd < 0.15); sk_ = strk * (0.6 + 0.6 * nc)
V += seen * shd * (0.03 * np.clip(-sk_, 0, 1) ** 1.5 - 0.02 * np.clip(sk_, 0, 1))       # soft, broken by the grain of the brush
V += seen * (side & old) * (kd > 0.15) * 0.05 * ss(0.42, 0.5, strk * (0.6 + 0.6 * nc))

fol = sets["foliation"]
for i in [i for i, k in enumerate(KIND) if k == "pluck"]:
    m = pluck & (pl == i)
    if m.sum() < 200: continue
    rs = Rng("layers", KEY[i]); nfc = NF[i]
    # the banding: soft, uneven, wavy and broken light and dark bands along the layers, quiet from afar
    sf = P @ fol; wv = fbm3(Pw, 0.30, 101, 2).reshape(H, W); fq = fbm3(Pw, 0.5, 102, 2).reshape(H, W)
    tdir0 = np.cross(fol, NF[i]); tdir0 /= np.linalg.norm(tdir0)
    Qb = np.stack([(sf + 0.03 * (wv - 0.5)) / 0.035, (P @ tdir0) / 0.5, np.zeros(H * W).reshape(H, W)], -1).reshape(-1, 3)
    bnds = (2 * fbm3(Qb, 1.0, 105, 2).reshape(H, W) - 1) * ss(0.35, 0.55, fbm3(Pw, 0.22, 103, 2).reshape(H, W))   # irregular, long along the layers, broken
    V = np.where(m, V * (1 + 0.05 * seen * bnds), V)
    # the steps where the fracture jumped a layer: one long, one short, not quite parallel, broken and fading mid-face
    tdir = np.cross(fol, nfc); tdir /= np.linalg.norm(tdir); ta = P @ tdir
    t_lo, t_hi = np.percentile(ta[m], 3), np.percentile(ta[m], 97); lo_, hi_ = np.percentile(sf[m], 6), np.percentile(sf[m], 94)
    wm = 0.005                                                   # metres: the riser's line, thin from afar
    for q_, reach in ((rs.u(0.25, 0.4), rs.u(0.7, 0.9)), (rs.u(0.62, 0.78), rs.u(0.3, 0.45))):
        if reach < 0.5 and pxf < 150: continue                   # from the street stop one step at most
        tl = rs.u(-0.06, 0.06); ns = fol + tl * nfc + rs.u(-0.05, 0.05) * tdir; ns /= np.linalg.norm(ns)
        o_ = float(np.percentile((P @ ns)[m], 100 * (0.06 + 0.88 * q_)))
        start = 0 if rs.u() < 0.5 else 1; al = (ta - t_lo) / max(t_hi - t_lo, 1e-6); al = al if start == 0 else 1 - al
        keep = (1 - ss(reach - 0.18, reach, al)) * (fbm3(Pw, 0.09, 104 + int(q_ * 100), 2).reshape(H, W) > 0.36)
        rn = ns if rs.u() < 0.5 else -ns; dark = (rn @ Lkey) < 0.05 or LIGHT != "lowsun"
        d_ = (P @ ns - o_) * (1 if rn @ ns > 0 else -1)
        V = np.where(m & (d_ > 0) & (d_ < wm), V * (1 - (0.30 if dark else -0.06) * keep), V)
        V = np.where(m & (d_ <= 0) & (d_ > -1.2 * wm), V * (1 + 0.05 * keep), V)
# d. the occlusion where the stone meets the turf: a crisp plum band with a ragged top
occ = rock & (z < 0.02 + 0.035 * vnoise3(Pw, 0.05, 71).reshape(H, W))
V = np.where(occ, V * 0.5, V)
# e. the lip: on the lit side of an arris a pale line of two pixels, broken in runs; none on the silhouette
bnd = np.zeros((H, W), bool)
for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    l2 = np.roll(pl, (dy, dx), (0, 1)); V2 = np.roll(V, (dy, dx), (0, 1))
    bnd |= rock & (l2 >= 0) & (l2 != pl) & (V > V2 + 0.035)
pxf = float(np.median(pxm[rock])) / SS          # final pixels per metre: the lip is about 6 mm, never under a pixel or over LIPW
lipw = np.zeros((H, W)); ring = bnd.copy(); nfull = max(1, int(round(float(np.clip(0.0055 * pxf, 0.7, LIPW)) * SS))); lipw[bnd] = 1
for r_ in range(1, nfull + 1):
    grow = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        grow |= np.roll(ring, (dy, dx), (0, 1)) & (np.roll(pl, (dy, dx), (0, 1)) == pl)
    grow &= rock & (lipw == 0); lipw[grow] = 1 if r_ < nfull else 0.5; ring = grow
sil = rock & ~(np.roll(rock, 1, 0) & np.roll(rock, -1, 0) & np.roll(rock, 1, 1) & np.roll(rock, -1, 1))
for _ in range(3 * SS): sil = sil | np.roll(sil, 1, 0) | np.roll(sil, -1, 0) | np.roll(sil, 1, 1) | np.roll(sil, -1, 1)
lipw *= ~sil
runs_ = vnoise3(Pw, 0.07, 81).reshape(H, W) > 0.36
litlip = (kd > 0.12) | (LIGHT != "lowsun")
V += 0.085 * lipw * runs_ * litlip * ~occ
# f. the crack (paint.py's mark, carried from the still): a crisp plum line, a pale lip on the side toward the light
anyb = np.zeros((H, W), bool)
for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)): anyb |= np.roll(pl, (dy, dx), (0, 1)) != pl
for _ in range(3 * SS): anyb = anyb | np.roll(anyb, 1, 0) | np.roll(anyb, -1, 0) | np.roll(anyb, 1, 1) | np.roll(anyb, -1, 1)
rat = Lw / np.maximum(boxblur(Lw, 6 * SS), 1e-4)
ck = np.where(rock & ~grass & ~anyb & ~occ & (pl == CF), ss(0.35, 0.5, np.clip((0.90 - rat) / 0.12, 0, 1)), 0)   # crisp, on the crack's face
cen = P[ri].mean(0) + at
(pc0, pc1), _ = proj(np.stack([cen, cen + Lkey * 0.05]))
ld = (pc1 - pc0) / max(np.linalg.norm(pc1 - pc0), 1e-6)
lipc = np.roll(ck, (int(round(1.8 * SS * ld[1])), int(round(1.8 * SS * ld[0]))), (0, 1)) * (1 - ck)
V = V * (1 - ck) + ck * V * 0.36 + 0.07 * lipc * (LIGHT == "lowsun")
if DBG:
    sk3 = np.stack([band * 1.0, ck, pluck * 1.0], -1).astype(float); pio.save(f"{DBG}/{VIEW}-{LIGHT}-{WAY}-skin.png", sk3.reshape(H // SS, SS, W // SS, SS, 3).mean((1, 3)) if SS > 1 else sk3)
out = np.repeat(V[..., None], 3, -1)

# f. the crack's mouth: a small notch bitten into the shoulder over the arris, its floor in shade, a pale lip on the
#    side that faces the light (58: where the crack meets the edge)
if MOUTH is not None:
    e, s0 = MOUTH; P0, P1 = np.array(e["P0"]), np.array(e["P1"]); tw = P1 - P0; ln = np.linalg.norm(tw); tw /= ln
    A = KEY.index(e["a"]); Bf = KEY.index(e["b"]); nA, nB = NF[A], NF[Bf]
    upper = A if nA[2] > nB[2] else Bf; nU = NF[upper]; nL = NF[Bf if upper == A else A]
    uU = np.cross(nU, tw); uU = -uU if uU @ nL > 0 else uU
    c0 = P0 + s0 * ln * tw; wN, dN = NOTCH
    ring = [c0 - tw * wN * 0.55, c0 + uU * dN + tw * wN * 0.08, c0 + tw * wN * 0.45]
    (pa, pb, pc), _ = proj(np.stack(ring))
    def tri(p1_, p2_, p3_, val):
        global out
        x0, y0 = int(min(p1_[0], p2_[0], p3_[0]) - 2), int(min(p1_[1], p2_[1], p3_[1]) - 2)
        x1, y1 = int(max(p1_[0], p2_[0], p3_[0]) + 3), int(max(p1_[1], p2_[1], p3_[1]) + 3)
        X_, Y_ = xx[y0:y1, x0:x1], yy[y0:y1, x0:x1]
        def ed(a_, b_):
            d_ = b_ - a_; n_ = np.array([d_[1], -d_[0]]) / max(np.linalg.norm(d_), 1e-9); return (X_ - a_[0]) * n_[0] + (Y_ - a_[1]) * n_[1]
        e1, e2, e3 = ed(p1_, p2_), ed(p2_, p3_), ed(p3_, p1_)
        sgn = 1 if (e1 + e2 + e3).mean() > 0 else -1
        cvg = np.clip(np.minimum(np.minimum(e1 * sgn, e2 * sgn), e3 * sgn) + 0.5, 0, 1)
        blk = out[y0:y1, x0:x1]; out[y0:y1, x0:x1] = blk * (1 - cvg[..., None]) + blk * val * cvg[..., None]
    # the notch's two walls: the one turned from the light dark, the other its floor, half lit
    wall1 = np.cross(tw, nU) * -1; lit1 = float(np.cross(uU, nU) @ Lkey)
    tri(pa, pb, (pa + pc) / 2, 0.40 if lit1 < 0 else 0.78)
    tri((pa + pc) / 2, pb, pc, 0.78 if lit1 < 0 else 0.40)
    print(f"[paint] notch at {s0:.2f} of {e['a']}/{e['b']}")

# ------------------------------------------------------------------ the risers: each step's small wall, dark where it
# turns from the light, a pale lip where it faces it
def stroke(p, q, wpx, val, mode):
    global out
    x0, y0 = int(max(0, min(p[0], q[0]) - 4)), int(max(0, min(p[1], q[1]) - 4))
    x1, y1 = int(min(W, max(p[0], q[0]) + 5)), int(min(H, max(p[1], q[1]) + 5))
    if x1 <= x0 or y1 <= y0: return
    X_ = xx[y0:y1, x0:x1]; Y_ = yy[y0:y1, x0:x1]; d = q - p; ln2 = max(d @ d, 1e-9)
    t = np.clip(((X_ - p[0]) * d[0] + (Y_ - p[1]) * d[1]) / ln2, 0, 1)
    dd = np.hypot(X_ - p[0] - t * d[0], Y_ - p[1] - t * d[1])
    cvg = np.clip(wpx / 2 + 0.5 - dd, 0, 1) * rock[y0:y1, x0:x1]
    blk = out[y0:y1, x0:x1]
    out[y0:y1, x0:x1] = blk * (1 - cvg[..., None]) + (blk * val) * cvg[..., None]
pxm_med = float(np.median(pxm[rock]))
wline = float(np.clip(0.006 * pxm_med, 0.8 * SS, 2.2 * SS))
for r in risers:
    lit_w = float(r["wall"] @ Lkey)
    val = 0.55 if lit_w < 0.1 else 1.14
    for rr, lo, hi in ((r["rB"], max(r["dlo"], 0), r["dhi"]), (r["rA"], r["dlo"], min(r["dhi"], 0))):
        if hi - lo < 0.4 * SS: continue
        p = r["p"] + rr * lo; q = r["p"] + rr * hi
        stroke(p, q, wline, val, "wall")
if DBG: print(f"[paint] risers {len(risers)} line {wline:.2f} px, median {pxm_med:.0f} px/m")

# ------------------------------------------------------------------ 3. colour by value, on 58's ramp
RV = np.array([0.0, 0.058, 0.19, 0.29, 0.39, 0.49, 0.64, 0.78, 0.875, 1.0])
RS = np.array([(8, 4, 10), (23, 11, 26), (60, 45, 62), (90, 72, 82), (120, 96, 96), (148, 118, 110), (188, 157, 140), (215, 196, 171), (236, 224, 204), (250, 245, 236)]) / 255
RT = np.array([(8, 4, 10), (23, 11, 26), (60, 45, 62), (90, 74, 82), (118, 100, 96), (142, 128, 108), (184, 167, 140), (215, 198, 172), (236, 225, 204), (250, 246, 236)]) / 255
Vf = out[..., 0]
ramp = lambda R: np.stack([np.interp(Vf, RV, R[:, c]) for c in range(3)], -1)
RF = np.array([(8, 4, 10), (23, 11, 26), (60, 46, 60), (92, 78, 82), (124, 108, 104), (150, 136, 126), (188, 174, 158), (218, 207, 190), (238, 230, 216), (250, 247, 240)]) / 255
C = np.where(fresh[..., None], ramp(RF), np.where(topf[..., None], ramp(RT), ramp(RS)))
if WAY == "Pc":
    gl = lum(C)[..., None]; C = gl + SAT * (C - gl)
else:
    C = np.repeat(Vf[..., None], 3, -1) * np.array([1.0, 0.985, 0.965])
fin = np.where(rock[..., None], C * (1 - ag[..., None]) + ow * ag[..., None], ow)
if SS > 1:
    fin = fin.reshape(H // SS, SS, W // SS, SS, 3).mean((1, 3))
full = img_full.copy(); full[BOX[1]:BOX[3], BOX[0]:BOX[2]] = fin; fin = full
pio.save(arg["--out"], np.clip(fin, 0, 1))
print("[paint] wrote", arg["--out"])

