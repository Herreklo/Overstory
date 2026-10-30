"""r03: the Holm tip's outcrop as a few rigid masses (kit.json `mass`); ref 57's LOW ROCKY OUTCROP is the bar.

Each mass is convex, in its own frame: its top facets, its sides on the plan (a joint's, a worn or a plucked face),
its base, and the wear rule's facets on its arrises and corners. Every face bulges gently by its kind, so faces are
flat only in the large. The mass is split along the record's joints, foliation and sheeting into rigid blocks parted
by seams; each block settles by a small turn and is rounded on its own, each arris a rolling-ball round of the cutting
face's kind (body.py's exact round), varied along it by height and seeded waves and never more than the record's cap
of the block's least width: worn arrises big and soft, joints middling, seams and plucked faces crisp. Meshed by
openvdb. Blocks and masses are only moved and turned.

Step 1 shoots each mass alone in grey clay on a flat ground, from 57's boulder row's view in a low warm sun, and
measures its flat share (`flat`) and splinters (`spike`) into `mass.json`.

    Blender -b --factory-startup -P mass.py -- --step 1 --out DIR [--masses A,B] [--views front,back] [--voxel M]
"""
import json, math, os, sys

import bpy
import numpy as np
import openvdb as vdb
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "blender", "resolver")]
import hashing as HS  # noqa: E402


def arg(n, d=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(n) + 1] if n in a else d


K = json.load(open(os.path.join(HERE, "kit.json")))
M = K["mass"]
R = M["round"]
REC = json.load(open(os.path.join(ROOT, M["fracture"]["record"])))  # the place's record, read only
OUT = os.path.abspath(arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "renders", "r03")))


def unit(facing, slope):
    """The outward normal of a face facing bearing `facing` (0 = +y, 90 = +x), `slope` degrees from level."""
    b, a = math.radians(facing), math.radians(slope)
    return np.array([math.sin(b) * math.sin(a), math.cos(b) * math.sin(a), math.cos(a)])


def cut(d, g, n, v, r):
    """The body (d, g) cut by a face (value v, gradient n) with its arris rounded by a rolling ball of radius r: the
    exact distance to the wedge both eroded by r, less r, its angle read from the body's gradient (body.py's)."""
    n = np.broadcast_to(n, g.shape)
    a1, b1 = d + r, v + r
    c = np.clip(np.einsum("ij,ij->i", g, n), -0.9999, 0.9999); s2 = 1 - c * c
    inside = (a1 <= 0) & (b1 <= 0)
    r1 = (a1 > 0) & (b1 - a1 * c <= 0)
    r2 = ~r1 & (b1 > 0) & (a1 - b1 * c <= 0)
    corner = ~(inside | r1 | r2)
    D = np.where(a1 >= b1, a1, b1); G = np.where((a1 >= b1)[:, None], g, n)
    D = np.where(r1, a1, D); G = np.where(r1[:, None], g, G)
    D = np.where(r2, b1, D); G = np.where(r2[:, None], n, G)
    q = np.sqrt(np.maximum(a1 * a1 + b1 * b1 - 2 * a1 * b1 * c, 0) / s2)
    gc = ((a1 - b1 * c) / s2)[:, None] * g + ((b1 - a1 * c) / s2)[:, None] * n
    gc /= np.maximum(np.linalg.norm(gc, axis=1), 1e-9)[:, None]
    D = np.where(corner, q, D); G = np.where(corner[:, None], gc, G)
    return D - r, G


# ---------------------------------------------------------------- a mass
def corners(planes):
    """The convex polytope n.p <= d's corners, each with the planes through it (exact, by every triple)."""
    N = np.array([n for n, d in planes]); D = np.array([d for n, d in planes]); out = []
    for i in range(len(N)):
        for j in range(i + 1, len(N)):
            for k in range(j + 1, len(N)):
                A = N[[i, j, k]]
                if abs(np.linalg.det(A)) < 1e-6:
                    continue
                p = np.linalg.solve(A, D[[i, j, k]])
                if np.all(N @ p - D <= 1e-6) and not any(np.linalg.norm(p - q) < 1e-4 for q, _ in out):
                    out.append((p, tuple(np.nonzero(np.abs(N @ p - D) < 1e-6)[0])))
    return out


def skewed(st, lo, hi, k):
    """A size between lo and hi, skewed toward lo by the integer power k: a few big, many small."""
    return lo + (hi - lo) * st.random() ** int(k)


class Mass:
    def __init__(self, X):
        self.X, self.id = X, X["id"]
        self.faces = []  # (normal, offset, kind, key, warp): tops, sides, chips, wear, base; cut by falling radius
        for i, (f, s, p, kind) in enumerate(X["tops"]):
            n = unit(f, s); self.faces.append((n, float(n @ p), kind, f"top/{i}", None))
        for i, (f, s, dist, kind) in enumerate(X["sides"]):
            n = unit(f, s); b = math.radians(f)
            self.faces.append((n, float(n @ [dist * math.sin(b), dist * math.cos(b), 0.0]), kind, f"side/{i}", None))
        for i, (f, s, p, kind) in enumerate(X.get("chips", [])):
            n = unit(f, s); self.faces.append((n, float(n @ p), kind, f"chip/{i}", None))
        base = (np.array([0.0, 0.0, -1.0]), 0.0, "base", "base", None)
        self.faces += self.wear(self.faces + [base]) + [base]
        cs = corners([(f[0], f[1]) for f in self.faces])
        self.faces = [(n, d, kind, key, self.warp(key, kind, n, [p for p, s in cs if i in s])) for i, (n, d, kind, key, _) in enumerate(self.faces)]
        # an arris takes the smaller round of its two faces: cut in order of falling radius, so a fresher face's crisp
        # arris survives and no ball is forced into a facet too small for it
        self.faces = self.faces[:1] + sorted(self.faces[1:], key=lambda f: -R[f[2]])
        V = np.array([p for p, _ in corners([(f[0], f[1]) for f in self.faces])])
        self.H = float(V[:, 2].max())
        self.lo, self.hi = V.min(0) - 0.15, V.max(0) + 0.15; self.lo[2] = -0.1
        st = HS.Stream("lt1-holm-tip", "mass", "wave", self.id); V = M["vary"]
        self.waves = []
        for _ in range(3):
            a = st.uniform(0, 2 * math.pi); z = st.uniform(-0.5, 0.5)
            k = np.array([math.cos(a), math.sin(a), z]) / math.sqrt(1 + z * z)
            self.waves.append((k, st.uniform(*V["waveM"]), st.uniform(0, 2 * math.pi)))
        self.blocks = self.fracture()

    def fracture(self):
        """The mass split into rigid blocks along the record's joints (`fracture`): each set's planes (J1 to J3 and the
        foliation, at their spacings, the sheeting under the first top at its own) shown at `show` of the set, in
        seeded order, each splitting the one block a seeded point on it lies in (so a seam ends at an older one), never
        leaving a block under `leastM` across it, at most `most` blocks. A seam is its family's tight width (the
        record's outcrop `tightM`), opening by `widen` a metre up toward the weather; its lips the `seam` round. Each
        block is the mass's faces and its seams' faces, rounded in turn: (region [(n, s, side)], faces)."""
        Fr = M["fracture"]; rk = REC["rock"]; fam = {f["name"]: f for f in REC["outcrop"]["families"]}
        tight = min(f["tightM"] for f in fam.values()); st = HS.Stream("lt1-holm-tip", "mass", "fracture", self.id)
        planes = [(f[0], f[1]) for f in self.faces]; V = np.array([p for p, _ in corners(planes)])
        cands = []
        for name, n, sp in [(j["name"], unit(j["dipToward"], j["dip"]), j["spacingM"]) for j in rk["joints"]] + \
                [("foliation", unit(rk["foliation"]["dipToward"], rk["foliation"]["dip"]), rk["foliation"]["spacingM"])]:
            t = V @ n; x = t.min() + st.random() * st.uniform(*sp)
            while x < t.max():
                if st.random() < Fr["show"][name]:
                    cands.append((st.random(), name, n, x, fam.get(name, {}).get("tightM", tight)))
                x += st.uniform(*sp)
        f0, s0 = self.X["tops"][0][:2]; n = unit(f0, s0); t = V @ n; x = t.max() - st.uniform(*rk["sheeting"]["spacingM"])
        while x > t.min() + Fr["leastM"]:
            if st.random() < Fr["show"]["sheeting"]:
                cands.append((st.random(), "sheeting", n, x, tight))
            x -= st.uniform(*rk["sheeting"]["spacingM"])
        regs = [[]]
        for _, name, n, x, w in sorted(cands, key=lambda c: c[0]):
            if len(regs) >= Fr["most"]:
                break
            for _ in range(12):
                q = self.lo + np.array([st.random(), st.random(), st.random()]) * (self.hi - self.lo); q = q - (q @ n - x) * n
                if all(q @ m_ - d_ < -0.05 for m_, d_ in planes):
                    break
            else:
                continue
            b = next(i for i, rg in enumerate(regs) if all(sd * (q @ m_ - s_) <= 0 for m_, s_, sd, _ in rg))
            sides = []
            for sd in (1, -1):
                C = corners(planes + [(e * m_, e * s_) for m_, s_, e, _ in regs[b]] + [(sd * n, sd * x)])
                sides.append(len(C) >= 4 and (max(sd * (x - p @ n) for p, _ in C) >= Fr["leastM"]))
            if all(sides):
                regs[b:b + 1] = [regs[b] + [(n, x, 1, w)], regs[b] + [(n, x, -1, w)]]
        ez = np.array([0.0, 0.0, 1.0]); cap = REC["outcrop"]["chamfers"]["capShare"]; out = []
        for i, rg in enumerate(regs):
            seams = []
            for j, (n, x, sd, w) in enumerate(rg):
                k = Fr["widen"] if abs(n[2]) < 0.5 else 0.0; u = sd * n + 0.5 * k * ez; L = float(np.linalg.norm(u))
                seams.append((u / L, (sd * x - w / 2) / L, "seam", f"block/{i}/seam/{j}", None))
            fs = self.faces[:1] + sorted(self.faces[1:] + seams, key=lambda f: -R[f[2]])
            C = np.array([p for p, _ in corners([(f[0], f[1]) for f in fs])])
            least = min(float(np.ptp(C @ f[0])) for f in fs)
            rot, piv = np.eye(3), np.zeros(3)
            if len(regs) > 1:  # a loosened block settles a little, turned about its foot: a lean, no history
                st = HS.Stream("lt1-holm-tip", "mass", "settle", self.id, i)
                a = st.uniform(0, 2 * math.pi); ax = np.array([math.cos(a), math.sin(a), 0.0]); th = math.radians(st.uniform(*Fr["settleDeg"]))
                X_ = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
                rot = np.eye(3) * math.cos(th) + math.sin(th) * X_ + (1 - math.cos(th)) * np.outer(ax, ax)
                piv = C.mean(0); piv[2] = 0.0
            out.append(([(n, x, sd) for n, x, sd, _ in rg], fs, rot, piv, cap * least))
        return out

    def wear(self, faces):
        """The wear rule (`wear`), on the designed polytope: on each arris where an exposed face meets another, from
        each end by chance a broad facet that starts part way along and deepens to the corner; at each corner of three
        faces by chance a facet across it, worn where an exposed face meets, else a crisp chip."""
        W = M["wear"]; A_, C_ = W["arris"], W["corner"]; ex = set(W["exposed"])
        st = HS.Stream("lt1-holm-tip", "mass", "wear", self.id)
        cs = corners([(f[0], f[1]) for f in faces]); kinds = [f[2] for f in faces]; out = []
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                if "base" in (kinds[i], kinds[j]) or not ({kinds[i], kinds[j]} & ex):
                    continue
                vs = [p for p, s in cs if i in s and j in s]
                if len(vs) < 2:
                    continue
                e = np.cross(faces[i][0], faces[j][0]); e /= np.linalg.norm(e); t_ = [p @ e for p in vs]
                a, b = vs[int(np.argmin(t_))], vs[int(np.argmax(t_))]; L = float(np.linalg.norm(b - a))
                if L < A_["leastM"]:
                    continue
                kind = kinds[i] if kinds[i] in ex else kinds[j]
                for end, other in ((a, b), (b, a)):
                    if st.random() >= A_["share"]:
                        continue
                    s = st.uniform(*A_["fromEnd"]); q = end + s * (other - end); eo = (other - end) / L
                    x = min(skewed(st, *A_["depthM"], A_["skew"]) / (s * L), 0.6); tau = x / math.sqrt(1 - x * x)
                    t = st.uniform(*A_["t"]); nm = (1 - t) * faces[i][0] + t * faces[j][0]; nm /= np.linalg.norm(nm)
                    u = nm - tau * eo; u /= np.linalg.norm(u)
                    out.append((u, float(u @ q), kind, f"arris/{len(out)}", None))
        for p, s in cs:
            fs = [k for k in s if kinds[k] != "base"]
            if len(fs) < 3:
                continue
            ks = {kinds[k] for k in fs} & ex
            share, dm = (C_["share"], C_["depthM"]) if ks else (C_["crisp"]["share"], C_["crisp"]["depthM"])
            if st.random() >= share:
                continue
            u = sum(faces[k][0] for k in fs); u /= np.linalg.norm(u)
            v = np.array([st.normal(), st.normal(), st.normal()]); v -= (v @ u) * u
            u = u + math.tan(math.radians(st.uniform(0, C_["jitterDeg"]))) * v / max(np.linalg.norm(v), 1e-9); u /= np.linalg.norm(u)
            kind = ("sea" if "sea" in ks else "worn") if ks else "chip"
            out.append((u, float(u @ p) - skewed(st, *dm, C_["skew"]), kind, f"corner/{len(out)}", None))
        return out

    def warp(self, key, kind, n, vs):
        """A face's gentle outward bulge (`bulge`), seeded by the mass and the face: a dome over the face, its crown
        shifted off the face's middle by up to `shift` of its reach and standing `share` of the face's size (by its kind:
        worn and ice-shaped faces most, fresh fractures least), times `amp`; reaching `reach` times its size."""
        B = M["bulge"]; sh = B["share"].get(kind, 0.0)
        if sh <= 0 or len(vs) < 3:
            return None
        V = np.array(vs); p0 = V.mean(0); E = float(np.linalg.norm(V - p0, axis=1).max()); L = B["reach"] * E
        st = HS.Stream("lt1-holm-tip", "mass", "warp", self.X["id"], key)
        c0, u0, v0 = st.uniform(*B["amp"]) * sh * E, st.uniform(-1, 1) * B["shift"] * E, st.uniform(-1, 1) * B["shift"] * E
        a = np.cross(n, [0.0, 0.0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0.0, 0.0]); a /= np.linalg.norm(a); b = np.cross(n, a)

        def w(Q):
            q = (((Q - p0) @ a - u0) / L) ** 2 + (((Q - p0) @ b - v0) / L) ** 2
            return c0 * np.maximum(1 - q, 0.0)
        return (w, a, b)

    def value(self, P, f):
        """A face at P: its signed distance (the rock behind it) and gradient, warped."""
        n, d, kind, key, wp = f
        v = P @ n - d
        if wp is None:
            return v, np.broadcast_to(n, P.shape)
        w, a, b = wp; e = 0.01
        du = (w(P + e * a) - w(P - e * a)) / (2 * e); dv = (w(P + e * b) - w(P - e * b)) / (2 * e)
        G = n - du[:, None] * a - dv[:, None] * b
        return v - w(P), G / np.linalg.norm(G, axis=1)[:, None]

    def vary(self, P, share):
        wave = sum(np.sin(2 * math.pi * (P @ k) / L + ph) for k, L, ph in self.waves) / 3
        return 1 + share * wave

    def chain(self, P, faces, cap):
        """The faces cut in turn at P, each arris rounded, never more than cap (the record's `capShare` of the block's
        least width) but for the `capExempt` kinds: (signed distance, gradient)."""
        V = M["vary"]; ex = V["exposure"]; free = set(M["fracture"]["capExempt"])
        h = np.clip(P[:, 2] / self.H, 0, 1); m = (ex[0] + (ex[1] - ex[0]) * h) * self.vary(P, V["wave"])
        mc = self.vary(P, V["chipWave"])
        d, g = self.value(P, faces[0])
        for f in faces[1:]:
            v, G = self.value(P, f); kind = f[2]
            r = R[kind] * (mc if kind in ("chip", "base") else m)
            d, g = cut(d, g, G, v, r if kind in free else np.minimum(r, cap))
        return d, g

    def form(self, P, which=False):
        """The form at P: each block (or the whole mass) in its own settled frame, its faces cut in turn; (signed
        distance, gradient[, the block])."""
        mg = M["fracture"]["margin"]; d = np.full(len(P), 1e3); g = np.tile([0.0, 0.0, 1.0], (len(P), 1))
        b = np.zeros(len(P), int)
        for j, (rg, fs, rot, piv, cap) in enumerate(self.blocks):
            Q = (P - piv) @ rot + piv; k = np.ones(len(P), bool)
            for n, x, sd in rg:
                k &= sd * (Q @ n - x) < mg
            i = np.nonzero(k)[0]
            if not len(i):
                continue
            db, gb = self.chain(Q[i], fs, cap); bt = db < d[i]; d[i[bt]] = db[bt]; g[i[bt]] = gb[bt] @ rot.T; b[i[bt]] = j
        return (d, g, b) if which else (d, g)

    def lattice(self, vs):
        n = np.ceil((self.hi - self.lo) / vs).astype(int) + 1
        return self.lo, tuple(n)

    def chunks(self, vs):
        o, (nx, ny, nz) = self.lattice(vs)
        X_, Y_ = np.meshgrid(o[0] + np.arange(nx) * vs, o[1] + np.arange(ny) * vs, indexing="ij")
        step = max(1, int(2e6 // (nx * ny)))
        for k0 in range(0, nz, step):
            k = np.arange(k0, min(nz, k0 + step))
            yield k0, (nx, ny, len(k)), np.stack([np.repeat(X_[..., None], len(k), 2), np.repeat(Y_[..., None], len(k), 2),
                                                  np.broadcast_to(o[2] + k * vs, (nx, ny, len(k)))], -1).reshape(-1, 3)

    def mesh(self, mat, vs):
        """The surface meshed by openvdb at vs, evaluated only in a band round the form's coarse field."""
        o, _ = self.lattice(vs); bg = 3 * vs; cvs, band = 0.06, 0.12
        co, _ = self.lattice(cvs)
        C = np.concatenate([self.form(P)[0].reshape(sh) for _, sh, P in self.chunks(cvs)], 2)
        grid = vdb.FloatGrid(bg); grid.transform = vdb.createLinearTransform(voxelSize=vs)
        for k0, sh, P in self.chunks(vs):
            i = np.clip(np.rint((P - co) / cvs).astype(int), 0, np.array(C.shape) - 1); c = C[i[:, 0], i[:, 1], i[:, 2]]
            a = np.where(c < 0, -bg, bg); m = np.abs(c) < band; a[m] = self.form(P[m])[0]
            grid.copyFromArray(np.clip(a, -bg, bg).astype(np.float32).reshape(sh), ijk=(0, 0, k0), tolerance=0)
        pts, tris, quads = grid.convertToPolygons(isovalue=0.0, adaptivity=0.0)
        V = np.asarray(pts, float) + o
        me = bpy.data.meshes.new(self.id)
        me.from_pydata(V.tolist(), [], [list(f) for f in np.asarray(tris)] + [list(f) for f in np.asarray(quads)])
        me.validate(); me.materials.append(mat)
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new(self.id, me); bpy.context.scene.collection.objects.link(ob)
        for o_ in bpy.context.selected_objects:
            o_.select_set(False)
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
        return ob

    def flat_share(self, ob):
        """The share of the mass's surface above its base that lies on one of its faces' planes (within `flat.M`, its
        facing within `flat.deg`): flat, not rounds."""
        me = ob.data; me.calc_loop_triangles()
        V = np.array([v.co for v in me.vertices]); T = np.array([t.vertices[:] for t in me.loop_triangles])
        a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; N = np.cross(b - a, c - a); A = np.linalg.norm(N, axis=1) / 2
        N = N / np.maximum(2 * A, 1e-12)[:, None]; C = (a + b + c) / 3; up = C[:, 2] > 0.03
        flat = np.zeros(len(C), bool); cos = math.cos(math.radians(M["flat"]["deg"]))
        per = {}; blk = self.form(C, which=True)[2]
        for j, (rg, fs, rot, piv, cap) in enumerate(self.blocks):
            i = np.nonzero(blk == j)[0]; Q = (C[i] - piv) @ rot + piv; Nq = N[i] @ rot
            for f in fs:
                if f[2] == "base":
                    continue
                v, G = self.value(Q, f)
                on = (np.abs(v) < M["flat"]["M"]) & (np.einsum("ij,ij->i", Nq, G) > cos) & up[i]
                key = f[3].split("/seam/")[0] + "/seam" if "/seam/" in f[3] else f[3]
                per[key] = round(per.get(key, 0.0) + float(A[i][on].sum()), 2); flat[i[on]] = True
        return {"flatShare": round(float(A[flat].sum() / A[up].sum()), 3), "areaM2": round(float(A[up].sum()), 1), "faceM2": per}

    def spikes(self):
        """Splinters (body.py's measure): at each surface voxel the share of a cube `ballM` round it that is rock."""
        sp = M["spike"]; vs = sp["voxelM"]; o, sh = self.lattice(vs)
        I = np.concatenate([(self.form(P)[0] < 0).reshape(s) for _, s, P in self.chunks(vs)], 2).astype(np.int32)
        r = int(round(sp["ballM"] / vs)); k = 2 * r + 1
        J = np.pad(I, r + 1)
        for ax in range(3):
            J = np.cumsum(J, ax, dtype=np.int32)
        a, b = slice(k, None), slice(None, -k)
        sl = lambda x, y, z: J[x][:, y][:, :, z]  # noqa: E731
        box = (sl(a, a, a) - sl(b, a, a) - sl(a, b, a) - sl(a, a, b) + sl(b, b, a) + sl(b, a, b) + sl(a, b, b) - sl(b, b, b))
        cov = box[:I.shape[0], :I.shape[1], :I.shape[2]] / k ** 3
        out = np.zeros_like(I, bool)
        for ax in range(3):
            for s in (1, -1):
                out |= np.roll(I, s, ax) == 0
        zz = o[2] + np.arange(I.shape[2]) * vs
        surf = (I == 1) & out & (zz > 0.05)[None, None, :]
        return {"spikeVoxels": int((surf & (cov < sp["least"])).sum()), "leastShare": round(float(cov[surf].min()), 3)}


# ---------------------------------------------------------------- the judge scene
def clay(name, rgb, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    return m


def cycles(px, samples):
    sc = bpy.context.scene; sc.render.engine = "CYCLES"
    pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "METAL"; pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = "GPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = px; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"


def judge_scene():
    J = M["judge"]; sc = bpy.context.scene; cycles(J["px"], J["samples"])
    wo = bpy.data.worlds.new("w"); sc.world = wo; wo.use_nodes = True
    bg = wo.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*J["sky"], 1); bg.inputs[1].default_value = J["skyE"]
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
    sun.data.angle = math.radians(1.5); sun.data.energy = J["sunE"]; sun.data.color = J["sunRGB"]
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    g = bpy.data.meshes.new("ground"); g.from_pydata([(-200, -200, 0), (200, -200, 0), (200, 200, 0), (-200, 200, 0)], [], [(0, 1, 2, 3)])
    g.materials.append(clay("ground", J["ground"], 0.95)); sc.collection.objects.link(bpy.data.objects.new("ground", g))
    return sun, cam


def aim(sun, cam, ms, bearing):
    """The camera at `bearing` from the mass's middle, `elev` up, `fit` times its size off; the sun `sunRel` from it."""
    J = M["judge"]; c = (ms.lo + ms.hi) / 2; c[2] = 0.42 * ms.H - J["sinkM"]
    size = float(max(ms.hi[0] - ms.lo[0], ms.hi[1] - ms.lo[1]))
    b, e = math.radians(bearing), math.radians(J["elev"])
    pos = Vector(c) + J["fit"] * size * Vector((math.sin(b) * math.cos(e), math.cos(b) * math.cos(e), math.sin(e)))
    cam.location = pos; cam.rotation_euler = (Vector(c) - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.sensor_fit = "VERTICAL"; cam.data.angle = math.radians(J["fov"]); cam.data.clip_start = 0.1
    sb, se = math.radians(bearing + J["sunRel"]), math.radians(J["sunEl"])
    dv = Vector((math.sin(sb) * math.cos(se), math.cos(sb) * math.cos(se), math.sin(se)))
    sun.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler()


def step1():
    J = M["judge"]; rock = clay("rock", [J["rock"]] * 3, J["rough"]); sun, cam = judge_scene()
    only = arg("--masses"); views = arg("--views", "front,back").split(",")
    vs = float(arg("--voxel", M["voxelM"])); info = {}
    for X in M["masses"]:
        if only and X["id"] not in only.split(","):
            continue
        ms = Mass(X); ob = ms.mesh(rock, vs); ob.location.z = -J["sinkM"]
        info[ms.id] = {"heightM": round(ms.H, 2), "planes": len(ms.faces), "blocks": len(ms.blocks), "capM": [round(b[4], 2) for b in ms.blocks], "tris": len(ob.data.polygons), **ms.flat_share(ob), **ms.spikes()}
        print("[mass]", ms.id, json.dumps(info[ms.id]))
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name not in ("ground", ms.id):
                o.hide_render = True
        ob.hide_render = False
        for v in views:
            aim(sun, cam, ms, X["front"] + (J["back"] if v == "back" else 0))
            bpy.context.scene.render.filepath = os.path.join(OUT, f"{ms.id}-{v}.png"); bpy.ops.render.render(write_still=True)
    json.dump(info, open(os.path.join(OUT, "mass.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "masses.blend"))


def main():
    os.makedirs(OUT, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    if arg("--step", "1") == "1":
        step1()


if __name__ == "__main__":
    main()
