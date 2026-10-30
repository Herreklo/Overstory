"""Stage 2, the high-poly sculpt (kit.json `sculpt`): a mass's designed planes (the blockout's, `mass.py --step block`)
as one signed-distance form, every plane kept flat, each arris a crisp flat chamfer sized by the weather it faces; then
a few cracks cut as clean V-grooves on the mass's own joint planes, and a few corners chipped off by planar cuts. No
grain, no bulge, nothing smoothed over a face. Meshed by openvdb at `voxelM`, evaluated only in bands refined from
coarser levels; checked for splinters (mass.py's measure); shot in grey from the blockout's views and saved for the
bake as `high_<id>` in `<gen>/high.blend`.

    Blender -b --factory-startup -P sculpt.py -- --out DIR [--gen DIR] [--masses boulder] [--views front,near] [--voxel M]
"""
import json, math, os, sys
from types import SimpleNamespace

import bpy
import numpy as np
import openvdb as vdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mass as MS  # noqa: E402

HS, S, arg = MS.HS, MS.K["sculpt"], MS.arg
OUT = os.path.abspath(arg("--out", os.path.join(MS.ROOT, "cache", "rock", "kit", "renders", "r04", "s2")))


def smax(a, b, k):
    """The larger of a and b, its crease rounded over k (a polynomial smooth maximum)."""
    return np.maximum(a, b) + np.maximum(k - np.abs(a - b), 0.0) ** 2 / (4 * k)


class Noise:
    """Value noise in [-1, 1] on the integer lattice, its table drawn from a seeded stream (choices integer-hashed)."""

    def __init__(self, *key):
        st = HS.Stream(*key); self.t = np.array([st.uniform(-1.0, 1.0) for _ in range(4096)])

    def __call__(self, P):
        i = np.floor(P).astype(np.int64); f = P - i; u = f * f * (3 - 2 * f); out = np.zeros(len(P))
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    h = ((i[:, 0] + dx) * 73856093 ^ (i[:, 1] + dy) * 19349663 ^ (i[:, 2] + dz) * 83492791) & 4095
                    w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                    out += w * self.t[h]
        return out


def skewed(st, lo, hi, k):
    return MS.skewed(st, lo, hi, k)


def chamfer(d, g, n, v, e, k):
    """The body (d, g) cut by a face (v, n), their arris chamfered: a flat face on the arris's bisector cutting each face
    back e metres square to the arris (0 leaves it sharp; so does a turn past 120 degrees), its creases crisp to k.
    (signed distance, gradient, where the new face or its chamfer is outermost)."""
    n = np.broadcast_to(n, g.shape)
    c = np.clip(np.einsum("ij,ij->i", g, n), -1.0, 1.0); m = np.sqrt(np.maximum(2.0 + 2.0 * c, 1e-9))
    ch = np.where((c > -0.5) & (e > 0), (d + v) / m + e * np.sqrt((1.0 - c) / 2.0), -1e3)
    D = smax(smax(d, v, k), ch, k)
    new, top = v > d, ch >= np.maximum(d, v)
    G = np.where(new[:, None], n, g); G = np.where(top[:, None], (g + n) / m[:, None], G)
    return D, G, new | top


class Sculpt:
    def __init__(self, X):
        self.X, self.id = X, X["id"]
        self.ms = MS.Mass(X, over={"bulge": {**MS.M["bulge"], "share": {}}}, wear=False)  # the designed planes, flat
        T = X["structure"]; self.sets = [("foliation", MS.unit(T["foliation"]["dipToward"], T["foliation"]["dip"]))] + \
            [(j["name"], MS.unit(j["dipToward"], j["dip"])) for j in T["joints"]]
        self.nf = self.sets[0][1]
        w = S["chamfer"]["weather"]; self.weather = MS.unit(w[0], 90 - w[1])
        self.cracks, self.chips = self.place_cracks(), self.place_chips()

    # ------------------------------------------------------------ placing
    def form(self, P):
        """The designed planes cut in turn at P, each arris chamfered (`chamfer`): `big` where its bisector faces the
        weather (toward `weather`, over `at`), `small` where it is sheltered, `fresh` where a fresh face meets (a fresh
        face's chamfers stay fresh); the base's left sharp. (signed distance, gradient)."""
        Ch = S["chamfer"]; fs = self.ms.faces; fresh = set(S["fresh"])
        d = P @ fs[0][0] - fs[0][1]; g = np.tile(fs[0][0], (len(P), 1)); fr = np.full(len(P), fs[0][2] in fresh)
        for n, off, kind, key, _ in fs[1:]:
            v = P @ n - off
            if kind == "base":
                e = np.zeros(len(P))
            else:
                b = g + n; b /= np.maximum(np.linalg.norm(b, axis=1), 1e-9)[:, None]
                t = np.clip((b @ self.weather - Ch["at"][0]) / (Ch["at"][1] - Ch["at"][0]), 0.0, 1.0)
                e = np.where(fr | (kind in fresh), Ch["fresh"], Ch["small"] + (Ch["big"] - Ch["small"]) * t * t * (3 - 2 * t))
            d, g, out = chamfer(d, g, n, v, e, Ch["soft"])
            fr = np.where(out, fr | (kind in fresh), fr)
        return d, g

    def surface(self, a, b):
        """The form's surface between a (outside) and b (inside), by bisection on the chamfered form."""
        for _ in range(30):
            m = (a + b) / 2
            if self.form(m[None])[0][0] > 0:
                a = m
            else:
                b = m
        return (a + b) / 2

    def place_cracks(self):
        """Cracks on the mass's own planes of weakness (`crack`): per set a seeded count, each on a plane at a seeded
        offset through the body, reaching `reachM` (skewed: a few long, more short) round a point where the plane meets
        the surface `fromUpDeg` down from its top toward the mass's front; a clean V `widthM` open at the surface and
        `depthM` deep, both closing toward the reach's end."""
        C = S["crack"]; st = HS.Stream("lt1-holm-tip", "sculpt", "crack", self.id); out = []
        V = np.array([p for p, _ in MS.corners([(f[0], f[1]) for f in self.ms.faces])]); mid = V.mean(0); mid[2] = 0.55 * self.ms.H
        front = MS.unit(self.X["front"], 90)
        for name, n in self.sets:
            for _ in range(st.randint(*C["count"][name])):
                t = V @ n; x = st.uniform(t.min() + C["marginM"], t.max() - C["marginM"])
                p0 = mid - (mid @ n - x) * n
                up = np.array([0.0, 0.0, 1.0]) - n[2] * n; up /= np.linalg.norm(up); side = np.cross(n, up)
                a = math.radians(st.uniform(*C["fromUpDeg"])); side = side if side @ front >= 0 else -side
                u = math.cos(a) * up + math.sin(a) * side
                c = self.surface(p0 + 3.0 * u, p0)
                out.append(dict(n=n, x=x, c=c, rho=skewed(st, *C["reachM"], C["skew"]), w=st.uniform(*C["widthM"]),
                                k=st.uniform(*C["depthM"]), wander=Noise("lt1-holm-tip", "sculpt", "wander", self.id, len(out)), set=name))
        return out

    def place_chips(self):
        """Chips (`chip`): a corner knocked off where it stands out (its faces turn from each other by `minDeg` or more),
        by its kind's `share` (fresh: a plucked face meets there; worn: weathered faces only, above `above` of the
        height), at most `most`: a planar facet across it, facing the corner's mean normal turned by up to `jitterDeg`,
        sunk `depthM` (skewed small) past the chamfered surface, its creases crisp to `soft`; held within `reach` times
        its depth of the corner so it never shaves a face."""
        C = S["chip"]; st = HS.Stream("lt1-holm-tip", "sculpt", "chip", self.id); fs = self.ms.faces
        sink = self.X.get("sinkM", 0.0); out = []
        for p, s in MS.corners([(f[0], f[1]) for f in fs]):
            s = [k for k in s if fs[k][2] != "base"]
            if len(s) < 3 or p[2] < sink + 0.08:
                continue
            N = [fs[k][0] for k in s]
            if min(math.degrees(math.acos(np.clip(a @ b, -1, 1))) for ai, a in enumerate(N) for b in N[ai + 1:]) < C["minDeg"]:
                continue
            kind = "fresh" if {fs[k][2] for k in s} & set(S["fresh"]) else "worn"; K = C[kind]
            if (kind == "worn" and p[2] < K["above"] * self.ms.H) or st.random() >= K["share"] or len(out) >= C["most"]:
                continue
            u = sum(N); u /= np.linalg.norm(u)
            v = np.array([st.normal(), st.normal(), st.normal()]); v -= (v @ u) * u
            u = u + math.tan(math.radians(st.uniform(0, C["jitterDeg"]))) * v / max(np.linalg.norm(v), 1e-9); u /= np.linalg.norm(u)
            q = self.surface(p + 0.3 * u, p - 0.8 * u); dp = skewed(st, *K["depthM"], C["skew"])
            out.append(dict(u=u, o=float(u @ q) - dp, q=q, rho=C["reach"] * dp, soft=K["soft"], kind=kind))
        return out

    # ------------------------------------------------------------ the field
    def field(self, P, fine=True):
        """The sculpted form's signed distance at P (negative in the rock); not fine, the form a game mesh follows: its
        chamfers and chips, without the cracks the bake carries."""
        d, g = self.form(P)
        for c in self.chips:
            d = smax(d, np.minimum(P @ c["u"] - c["o"], c["rho"] - np.linalg.norm(P - c["q"], axis=1)), c["soft"])
        if not fine:
            return d
        Ck = S["crack"]; L, amp = Ck["wander"]
        for c in self.cracks:
            # a clean V whose trace is the joint's plane on the surface, wandering a little, cut square into the
            # surface (its offset read where the surface normal through P meets the surface, so both walls stand alike
            # whatever the plane's angle); its width held on the surface (the slot narrows by the angle's sine), its
            # depth fading out where the plane meets the surface shallower than `steep` (the V opens to nothing,
            # never thins to a slit); width and depth closing together toward the reach's end
            q = P - c["c"]; r = np.linalg.norm(q - np.outer(q @ c["n"], c["n"]), axis=1); tp = np.clip(1 - (r / c["rho"]) ** 2, 0, 1)
            s = P @ c["n"] - c["x"] - d * (g @ c["n"]) + amp * c["wander"](P / L)
            sn = np.linalg.norm(np.cross(g, c["n"]), axis=1)
            deep = c["k"] * tp * np.clip((sn - Ck["steep"][0]) / (Ck["steep"][1] - Ck["steep"][0]), 0, 1)
            half = 0.5 * c["w"] * tp * sn * np.clip(1 + d / np.maximum(deep, 1e-6), 0, 1)
            d = smax(d, half - np.abs(s) - 0.0005, Ck["soft"])
        return d

    # ------------------------------------------------------------ meshing
    def mesh(self, mat, vs, fine=True, name=None):
        """The surface by openvdb at vs; each level evaluated only where the coarser one says the surface may be (its
        lookup error at most 1.2 times half a cell's diagonal), the coarsest everywhere."""
        lo, hi = self.ms.lo, self.ms.hi; hs = [h for h in S["levels"] if h > 2 * vs] + [vs]; bg = 2 * vs
        E = [1.2 * 0.87 * h for h in hs]; prev = None
        for L, h in enumerate(hs):
            n = (np.ceil((hi - lo) / h).astype(int) + 1); last = L == len(hs) - 1
            band = bg + sum(E[L - 1:len(hs) - 1]) if L else None
            if last:
                grid = vdb.FloatGrid(bg); grid.transform = vdb.createLinearTransform(voxelSize=h)
            else:
                A = np.empty(tuple(n), np.float32)
            X_, Y_ = np.meshgrid(lo[0] + np.arange(n[0]) * h, lo[1] + np.arange(n[1]) * h, indexing="ij")
            step = max(1, int(2e6 // (n[0] * n[1]))); ev = 0
            for k0 in range(0, n[2], step):
                k = np.arange(k0, min(n[2], k0 + step)); sh = (n[0], n[1], len(k))
                P = np.stack([np.repeat(X_[..., None], len(k), 2), np.repeat(Y_[..., None], len(k), 2),
                              np.broadcast_to(lo[2] + k * h, sh)], -1).reshape(-1, 3)
                if prev is None:
                    a = self.field(P, fine); ev += len(P)
                else:
                    ph, PA = prev; i = np.clip(np.rint((P - lo) / ph).astype(int), 0, np.array(PA.shape) - 1)
                    c = PA[i[:, 0], i[:, 1], i[:, 2]]; a = np.where(c < 0, -1.0, 1.0) * (bg if last else 1.0)
                    m = np.abs(c) < band; a[m] = self.field(P[m], fine); ev += int(m.sum())
                if last:
                    grid.copyFromArray(np.clip(a, -bg, bg).astype(np.float32).reshape(sh), ijk=(0, 0, k0), tolerance=0)
                else:
                    A[:, :, k0:k0 + len(k)] = a.reshape(sh)
            print(f"[sculpt] level {h} m: {ev} evaluations", flush=True)
            if not last:
                prev = (h, A)
        pts, tris, quads = grid.convertToPolygons(isovalue=0.0, adaptivity=0.0)
        V = np.asarray(pts, float) + lo; T = np.asarray(tris, np.int64).reshape(-1, 3); Q = np.asarray(quads, np.int64).reshape(-1, 4)
        F = np.concatenate([T, Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]])
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        if np.einsum("ij,ij->i", a, np.cross(b, c)).sum() < 0:  # outward
            F = F[:, ::-1]
        name = name or f"high_{self.id}"; me = bpy.data.meshes.new(name)
        me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
        me.loops.add(3 * len(F)); me.loops.foreach_set("vertex_index", F.astype(np.int32).ravel())
        me.polygons.add(len(F)); me.polygons.foreach_set("loop_start", np.arange(0, 3 * len(F), 3, dtype=np.int32))
        me.update(); me.validate(); me.shade_smooth(); me.materials.append(mat)
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
        return ob

    def spikes(self):
        f = lambda P: (self.field(P),)  # noqa: E731
        return MS.Mass.spikes(SimpleNamespace(form=f, lattice=self.ms.lattice, chunks=self.ms.chunks))


def main():
    os.makedirs(OUT, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    MS.M["judge"] = {**MS.M["judge"], **S["judge"]}; J = MS.M["judge"]
    rock = MS.clay("rock", [J["rock"]] * 3, J["rough"]); sun, cam = MS.judge_scene()
    only = arg("--masses", "boulder"); views = arg("--views", ",".join(S["views"])).split(",")
    vs = float(arg("--voxel", S["voxelM"])); info = {}
    for X in MS.M["masses"]:
        if X["id"] not in only.split(","):
            continue
        sc = Sculpt(X); ob = sc.mesh(rock, vs); ob.location.z = -X.get("sinkM", J["sinkM"])
        info[sc.id] = {"tris": len(ob.data.polygons), "cracks": [[c["set"], round(c["rho"], 2), round(c["w"], 3)] for c in sc.cracks],
                       "chips": {k: sum(c["kind"] == k for c in sc.chips) for k in ("fresh", "worn")}, **sc.spikes()}
        print("[sculpt]", sc.id, json.dumps(info[sc.id]), flush=True)
        for v in views:
            off, fit = S["views"][v]; J["fit"] = fit
            MS.aim(sun, cam, sc.ms, X["front"] + off)
            bpy.context.scene.render.filepath = os.path.join(OUT, f"{sc.id}-{v}.png"); bpy.ops.render.render(write_still=True)
        gen = os.path.abspath(arg("--gen", os.path.join(MS.ROOT, "cache", "rock", "kit", "gen", sc.id))); os.makedirs(gen, exist_ok=True)
        ob.location.z = 0.0; bpy.data.libraries.write(os.path.join(gen, "high.blend"), {ob}, fake_user=True)
        ob.hide_render = True
    json.dump(info, open(os.path.join(OUT, "sculpt.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
