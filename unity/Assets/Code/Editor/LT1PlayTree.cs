using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using Debug = UnityEngine.Debug;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The corner's tree in the walk (proposal Q16, docs/proposals.md): none until 1e builds the birch again. Øystein,
    /// 22 October, on the walk's stills: "the tree looks not good in game"; the card birch also cost 11 to 17 ms where it
    /// was in view (w3-report.md). A clay stand-in was tried and judged "so incredibly big and lumpy" (Øystein, the same
    /// evening; reviews/lt1/playable/walk/tree-report.md), so the walk draws no tree.
    ///
    /// One switch, -tree none|clay|card (TreeDefault: none). 'none' plants nothing: no tree, no root for it, no collider.
    /// 'card' plants the judged card birch as before (LT1Perf.PlantBirch), for 1e's comparison. 'clay' plants it,
    /// measures it and puts in its place one opaque mesh in the clay's own material (M_Street, as the heart's masses and
    /// the 1989 houses wear it): a trunk with the birch's girth at its foot and at breast height, limbs, and the crown's
    /// masses as the tree's generator sees them (blender/generators/tree.py, spatial_masses and volumes), each a soft,
    /// low-poly volume. Kept for comparison only; not to be improved (1e owns the birch). Nothing in it is chosen by
    /// chance: it is the grown birch (seed 1, age 60) measured, as deterministic as that birch. No cards, no clip (its
    /// card coordinates are zero, so the street shader's card clip returns at once), no new shader; it casts a shadow.
    /// Neither the card birch nor the clay tree has a walker proxy (w4-report.md: the walker passes through the birch).
    ///
    /// The harness's playable arm composes through ComposeOpen, so it draws the same tree by the same switch.
    /// </summary>
    public static partial class LT1Play
    {
        /// <summary>The walk's tree when -tree is not given: none, until 1e builds the birch again (Q16).</summary>
        public const string TreeDefault = "none";
        /// <summary>The clay tree's object, under LT1Perf.BirchRoot, in place of the card birch's.</summary>
        public const string ClayTreeName = "tree_birch_s1_a60 (clay)";
        /// <summary>The swatches the clay tree's faces sit on (blender/generators/palette.py: uv("wood"), uv("leaf")):
        /// in clay every surface is one matte grey, but the palette still says what each face is.</summary>
        static readonly Vector2 WoodUV = new Vector2(0.84375f, 0.90625f), LeafUV = new Vector2(0.40625f, 0.84375f);
        const int CrownDivisions = 2;          // each crown mass an icosphere of 162 vertices, 320 triangles
        const int TrunkSides = 12, LimbSides = 8;
        const float CardPad = 0.5f;            // the share of a card's reach a mass is padded by
        const float TrunkSink = 0.4f;          // the trunk's foot below the ground, so it meets the yard's slope

        /// <summary>The tree the walk draws: -tree none|clay|card, or TreeDefault.</summary>
        public static string TreeKind
        {
            get
            {
                string kind = Cli.Arg("-tree", TreeDefault);
                if (kind != "none" && kind != "clay" && kind != "card")
                    throw new System.ArgumentException($"[LT1Play] -tree {kind}: none, clay or card");
                return kind;
            }
        }

        /// <summary>
        /// The corner's tree planted in the open scene, of the kind asked: the tree's object (under LT1Perf.BirchRoot;
        /// null for none), its height above its foot, its kind, and the renderers whose bounds the scene must set again at
        /// start (the card birch's leaves, drawn out from their pivots in the shader; none for the others).
        /// </summary>
        static (GameObject tree, float height, string kind, MeshRenderer[] cardBounds) PlantTree()
        {
            string kind = TreeKind;
            if (kind == "none")
                return (null, 0f, kind, new MeshRenderer[0]);
            var (root, birch, _, height) = LT1Perf.PlantBirch();
            if (kind == "card")
                return (birch, height, kind, birch.GetComponentsInChildren<MeshRenderer>());
            var tree = ClayTree(birch, root.transform);
            Object.DestroyImmediate(birch);
            var r = tree.GetComponent<MeshRenderer>();
            return (tree, r.bounds.max.y - tree.transform.position.y, kind, new MeshRenderer[0]);
        }

        /// <summary>The clay tree: the planted card birch measured, and one mesh made from the measures.</summary>
        static GameObject ClayTree(GameObject birch, Transform parent)
        {
            var foot = birch.transform.position;
            var filters = birch.GetComponentsInChildren<MeshFilter>();
            var bark = filters.FirstOrDefault(f => f.name.EndsWith("_branches"))
                       ?? throw new MissingReferenceException($"[LT1Play] {birch.name} has no _branches mesh to measure");
            var leaves = filters.FirstOrDefault(f => f.name.EndsWith("_leaves"))
                         ?? throw new MissingReferenceException($"[LT1Play] {birch.name} has no _leaves mesh to measure");
            Vector3[] World(MeshFilter f) => f.sharedMesh.vertices.Select(v => f.transform.TransformPoint(v)).ToArray();
            var wood = World(bark);
            var pivots = World(leaves);
            float scale = leaves.transform.lossyScale.x;
            var offsets = new List<Vector2>();
            leaves.sharedMesh.GetUVs(2, offsets);
            // a card's reach from its pivot: its corners' offsets in its plane (metres; Tree.shader, OS_CardWS)
            float reach = offsets.Count == 0 ? 0f : offsets.Average(o => o.magnitude) * scale;

            // the trunk: its girth at the foot and at breast height, from the bark round its axis there
            (Vector3 centre, float radius) Girth(float y0, float y1)
            {
                var band = wood.Where(p => p.y - foot.y >= y0 && p.y - foot.y < y1
                                           && new Vector2(p.x - foot.x, p.z - foot.z).magnitude < 1.0f).ToList();
                if (band.Count < 8)
                    throw new System.Exception($"[LT1Play] the birch's bark has {band.Count} points between {y0} and {y1} m: no girth to measure");
                float x0 = band.Min(p => p.x), x1 = band.Max(p => p.x), z0 = band.Min(p => p.z), z1 = band.Max(p => p.z);
                return (new Vector3((x0 + x1) / 2f, foot.y, (z0 + z1) / 2f), ((x1 - x0) + (z1 - z0)) / 4f);
            }
            var (footAt, footR) = Girth(0f, 0.3f);
            var (_, breastR) = Girth(1.1f, 1.5f);

            // the crown: its masses as the tree's own generator sees them (blender/generators/tree.py: spatial_masses cuts
            // the leaves into k compact masses, k-means from the farthest points, the top first; volumes fits each an
            // ellipsoid, its radii twice the leaves' spread along its axes), each drawn as one soft clay volume, padded
            // by half a card's reach (the cards are drawn out from their pivots, past the generator's volume)
            float height = Mathf.Max(pivots.Max(p => p.y), wood.Max(p => p.y)) - foot.y;
            int k = Mathf.Clamp((int)System.Math.Round(3.0 + (height - 6.0) / 5.0, System.MidpointRounding.ToEven), 3, 6);
            var which = Masses(pivots, k);
            var volumes = new List<(Vector3 c, Vector3[] axes, Vector3 radii, int n)>();
            for (int m = 0; m < k; m++)
            {
                var pts = pivots.Where((p, i) => which[i] == m).ToArray();
                if (pts.Length < 6)
                    continue;
                var (c, axes, spread) = Ellipsoid(pts);
                var r = spread * 2f + Vector3.one * (reach * CardPad);
                // rounded halfway to the sphere of the same volume: one soft mass, never a sausage (the clay's own
                // simplification, claiming nothing; the masses' centres and sizes stay the leaves')
                float g = Mathf.Pow(r.x * r.y * r.z, 1f / 3f);
                r = new Vector3(Mathf.Sqrt(r.x * g), Mathf.Sqrt(r.y * g), Mathf.Sqrt(r.z * g));
                volumes.Add((c, axes, r, pts.Length));
            }
            // the top mass is the one the trunk rises into; the others hang on limbs from the trunk at the crown's base
            var top = volumes.OrderByDescending(v => v.c.y).First();
            float crownBase = pivots.Min(p => p.y), crownTop = pivots.Max(p => p.y);

            var verts = new List<Vector3>();
            var uvs = new List<Vector2>();
            var tris = new List<int>();
            var parts = new List<(int v0, int v1, int t0, int t1, System.Func<Vector3, Vector3> outward)>();
            var (dirs, faces) = Icosphere(CrownDivisions);
            foreach (var vol in volumes)
            {
                int v0 = verts.Count, t0 = tris.Count;
                foreach (var d in dirs)
                {
                    var q = vol.axes[0] * (d.x * vol.radii.x) + vol.axes[1] * (d.y * vol.radii.y) + vol.axes[2] * (d.z * vol.radii.z);
                    verts.Add(vol.c + q - foot);
                    uvs.Add(LeafUV);
                }
                foreach (var f in faces)
                    tris.AddRange(f.Select(i => v0 + i));
                var at = vol.c - foot;
                parts.Add((v0, verts.Count, t0, tris.Count, v => v - at));
            }
            int crownTris = tris.Count;

            // the trunk: rings from below the ground into the top mass, on the line from its foot to that mass's centre
            var axisFoot = new Vector3(footAt.x, foot.y - TrunkSink, footAt.z);
            float axisTop = top.c.y - foot.y;
            Vector3 Axis(float h) => Vector3.Lerp(axisFoot, top.c, (h + TrunkSink) / (axisTop + TrunkSink));
            Tube(verts, uvs, tris, parts, foot, TrunkSides, new[]
            {
                (Axis(-TrunkSink), footR), (Axis(0f), footR), (Axis(1.3f), breastR),
                (Axis(crownBase - foot.y), breastR * 0.8f), (top.c, breastR * 0.45f),
            });
            // the limbs: from the trunk where the crown begins, out and up into each lower mass's centre
            var fork = Axis(crownBase - foot.y - 0.6f);
            foreach (var vol in volumes.Where(v => v != top))
                Tube(verts, uvs, tris, parts, foot, LimbSides, new[] { (fork, breastR * 0.5f), (vol.c, breastR * 0.3f) });

            var mesh = new Mesh { name = ClayTreeName };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            // every face outward, each part checked by itself (Unity's winding, whichever way a part was laid)
            var normals = mesh.normals;
            bool flipped = false;
            foreach (var part in parts)
            {
                int inward = Enumerable.Range(part.v0, part.v1 - part.v0).Count(i => Vector3.Dot(normals[i], part.outward(verts[i])) < 0f);
                if (inward * 2 <= part.v1 - part.v0)
                    continue;
                for (int t = part.t0; t < part.t1; t += 3)
                    (tris[t + 1], tris[t + 2]) = (tris[t + 2], tris[t + 1]);
                flipped = true;
            }
            if (flipped)
            {
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
                normals = mesh.normals;
            }
            int wrong = parts.Sum(part => Enumerable.Range(part.v0, part.v1 - part.v0).Count(i => Vector3.Dot(normals[i], part.outward(verts[i])) < 0f));
            // what each vertex sees from its facing, as the clay's bake has it (heart_build.py): up sees sky, down ground
            mesh.SetColors(normals.Select(n => { float sky = 0.5f + 0.5f * n.y; return new Color(sky, 1f - sky, 1f, 1f); }).ToList());
            mesh.RecalculateBounds();
            mesh.UploadMeshData(false);

            var tree = new GameObject(ClayTreeName);
            tree.transform.SetParent(parent, false);
            tree.transform.position = foot;
            tree.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = tree.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Street.mat")
                                      ?? throw new System.IO.FileNotFoundException("[LT1Play] no M_Street.mat, the clay's material");
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;

            ulong hash = Overstory.Core.Hash.Start;
            foreach (var v in verts)
                hash = Overstory.Core.Hash.Then(hash, string.Format(System.Globalization.CultureInfo.InvariantCulture, "{0:F4},{1:F4},{2:F4}", v.x, v.y, v.z));
            foreach (int t in tris)
                hash = Overstory.Core.Hash.Then(hash, (ulong)t);
            var b = mesh.bounds;
            string F(float x) => x.ToString("F1", System.Globalization.CultureInfo.InvariantCulture);
            Debug.Log($"[LT1Play] the corner's tree in clay ({ClayTreeName}): {tris.Count / 3} triangles ({crownTris / 3} in {volumes.Count} " +
                      $"crown masses, {(tris.Count - crownTris) / 3} trunk and limbs), {verts.Count} vertices, hash {hash:x16}, {wrong} normals inward; " +
                      $"measured from the card birch's {pivots.Length / 4} leaf cards (reach {reach:F2} m) and bark ({height:F1} m tall): " +
                      $"trunk radius {footR:F2} m at the foot, {breastR:F2} at 1.3 m; leaves {F(crownBase - foot.y)} to {F(crownTop - foot.y)} m up, " +
                      $"{F(pivots.Max(p => p.x) - pivots.Min(p => p.x))} by {F(pivots.Max(p => p.z) - pivots.Min(p => p.z))} m across; " +
                      $"the clay {F(b.min.y)} to {F(b.max.y)} m, {F(b.size.x)} by {F(b.size.z)} m; masses (centre up, radii, cards): " +
                      string.Join("; ", volumes.Select(v => $"{F(v.c.y - foot.y)} m, {F(v.radii.x)}/{F(v.radii.y)}/{F(v.radii.z)}, {v.n / 4}")));
            return tree;
        }

        /// <summary>
        /// The crown cut into k compact masses by where its leaves are, as tree.py's spatial_masses cuts it: k-means,
        /// started from the farthest points (the highest first, then each next the farthest from those chosen), so it is
        /// deterministic. Each point's mass.
        /// </summary>
        static int[] Masses(Vector3[] pts, int k, int iters = 25)
        {
            var which = new int[pts.Length];
            if (pts.Length <= k)
                return Enumerable.Range(0, pts.Length).ToArray();
            int Highest() { int best = 0; for (int i = 1; i < pts.Length; i++) if (pts[i].y > pts[best].y) best = i; return best; }
            var cent = new List<Vector3> { pts[Highest()] };
            while (cent.Count < k)
            {
                int far = 0;
                float farD = -1f;
                for (int i = 0; i < pts.Length; i++)
                {
                    float d = cent.Min(c => (pts[i] - c).magnitude);
                    if (d > farD) { farD = d; far = i; }
                }
                cent.Add(pts[far]);
            }
            for (int it = 0; it < iters; it++)
            {
                for (int i = 0; i < pts.Length; i++)
                {
                    int best = 0;
                    for (int m = 1; m < k; m++)
                        if ((pts[i] - cent[m]).magnitude < (pts[i] - cent[best]).magnitude)
                            best = m;
                    which[i] = best;
                }
                bool moved = false;
                for (int m = 0; m < k; m++)
                {
                    var own = pts.Where((p, i) => which[i] == m).ToArray();
                    if (own.Length == 0)
                        continue;
                    var c = new Vector3(own.Average(p => p.x), own.Average(p => p.y), own.Average(p => p.z));
                    moved |= (c - cent[m]).magnitude > 1e-5f;
                    cent[m] = c;
                }
                if (!moved)
                    break;
            }
            return which;
        }

        /// <summary>
        /// An ellipsoid fitted to points, as tree.py's volumes fits a crown mass: their centre, the axes of their
        /// spread (the covariance's eigenvectors, a right-handed frame) and the spread along each (a standard deviation).
        /// </summary>
        static (Vector3 centre, Vector3[] axes, Vector3 spread) Ellipsoid(Vector3[] pts)
        {
            var c = new Vector3(pts.Average(p => p.x), pts.Average(p => p.y), pts.Average(p => p.z));
            var a = new double[3, 3];
            foreach (var p in pts)
            {
                var d = p - c;
                for (int i = 0; i < 3; i++)
                    for (int j = 0; j < 3; j++)
                        a[i, j] += d[i] * d[j];
            }
            for (int i = 0; i < 3; i++)
                for (int j = 0; j < 3; j++)
                    a[i, j] = a[i, j] / (pts.Length - 1) + (i == j ? 1e-4 : 0.0);
            // Jacobi's rotations: a symmetric 3 by 3 made diagonal, its eigenvectors the columns of v
            var v = new double[3, 3] { { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, 1 } };
            for (int sweep = 0; sweep < 50; sweep++)
            {
                double off = a[0, 1] * a[0, 1] + a[0, 2] * a[0, 2] + a[1, 2] * a[1, 2];
                if (off < 1e-18)
                    break;
                for (int p = 0; p < 2; p++)
                    for (int q = p + 1; q < 3; q++)
                    {
                        if (System.Math.Abs(a[p, q]) < 1e-15)
                            continue;
                        double theta = (a[q, q] - a[p, p]) / (2.0 * a[p, q]);
                        double t = System.Math.Sign(theta == 0 ? 1.0 : theta) / (System.Math.Abs(theta) + System.Math.Sqrt(theta * theta + 1.0));
                        double cs = 1.0 / System.Math.Sqrt(t * t + 1.0), sn = t * cs;
                        for (int r = 0; r < 3; r++)
                        {
                            double arp = a[r, p], arq = a[r, q];
                            a[r, p] = cs * arp - sn * arq;
                            a[r, q] = sn * arp + cs * arq;
                        }
                        for (int r = 0; r < 3; r++)
                        {
                            double apr = a[p, r], aqr = a[q, r];
                            a[p, r] = cs * apr - sn * aqr;
                            a[q, r] = sn * apr + cs * aqr;
                        }
                        for (int r = 0; r < 3; r++)
                        {
                            double vrp = v[r, p], vrq = v[r, q];
                            v[r, p] = cs * vrp - sn * vrq;
                            v[r, q] = sn * vrp + cs * vrq;
                        }
                    }
            }
            var axes = Enumerable.Range(0, 3).Select(j => new Vector3((float)v[0, j], (float)v[1, j], (float)v[2, j]).normalized).ToArray();
            if (Vector3.Dot(Vector3.Cross(axes[0], axes[1]), axes[2]) < 0f)
                axes[2] = -axes[2];
            var spread = new Vector3(Mathf.Sqrt(Mathf.Max((float)a[0, 0], 1e-4f)), Mathf.Sqrt(Mathf.Max((float)a[1, 1], 1e-4f)),
                                     Mathf.Sqrt(Mathf.Max((float)a[2, 2], 1e-4f)));
            return (c, axes, spread);
        }

        /// <summary>
        /// A tube through rings (world centre and radius), each ring square to the tube there, open at both ends (its
        /// foot is under the ground or in the trunk, its top inside a crown mass): its vertices (relative to the tree's
        /// foot), the wood's swatch, its triangles, and the part's outward direction for the winding check.
        /// </summary>
        static void Tube(List<Vector3> verts, List<Vector2> uvs, List<int> tris,
                         List<(int v0, int v1, int t0, int t1, System.Func<Vector3, Vector3> outward)> parts,
                         Vector3 foot, int sides, (Vector3 c, float r)[] rings)
        {
            int v0 = verts.Count, t0 = tris.Count;
            for (int k = 0; k < rings.Length; k++)
            {
                var along = (rings[Mathf.Min(k + 1, rings.Length - 1)].c - rings[Mathf.Max(k - 1, 0)].c).normalized;
                var u = Vector3.ProjectOnPlane(Mathf.Abs(along.x) < 0.9f ? Vector3.right : Vector3.forward, along).normalized;
                var w = Vector3.Cross(along, u);
                for (int s = 0; s < sides; s++)
                {
                    float a = 2f * Mathf.PI * s / sides;
                    verts.Add(rings[k].c + (u * Mathf.Cos(a) + w * Mathf.Sin(a)) * rings[k].r - foot);
                    uvs.Add(WoodUV);
                }
            }
            for (int k = 0; k < rings.Length - 1; k++)
                for (int s = 0; s < sides; s++)
                {
                    int a = v0 + k * sides + s, b = v0 + k * sides + (s + 1) % sides;
                    int c = a + sides, d = b + sides;
                    tris.AddRange(new[] { a, c, b, b, c, d });
                }
            var line = rings.Select(r => r.c - foot).ToArray();
            parts.Add((v0, verts.Count, t0, tris.Count, p =>
            {
                // from the nearest point of the tube's line
                Vector3 best = line[0];
                float bestD = float.MaxValue;
                for (int i = 0; i < line.Length - 1; i++)
                {
                    var seg = line[i + 1] - line[i];
                    float t = Mathf.Clamp01(Vector3.Dot(p - line[i], seg) / Mathf.Max(seg.sqrMagnitude, 1e-8f));
                    var q = line[i] + seg * t;
                    if ((p - q).sqrMagnitude < bestD) { bestD = (p - q).sqrMagnitude; best = q; }
                }
                return p - best;
            }));
        }

        /// <summary>A unit icosphere: its vertices (directions) and triangles, subdivided so many times.</summary>
        static (List<Vector3> dirs, List<int[]> faces) Icosphere(int divisions)
        {
            float t = (1f + Mathf.Sqrt(5f)) / 2f;
            var dirs = new List<Vector3>
            {
                new(-1, t, 0), new(1, t, 0), new(-1, -t, 0), new(1, -t, 0),
                new(0, -1, t), new(0, 1, t), new(0, -1, -t), new(0, 1, -t),
                new(t, 0, -1), new(t, 0, 1), new(-t, 0, -1), new(-t, 0, 1),
            }.Select(v => v.normalized).ToList();
            var faces = new List<int[]>
            {
                new[] { 0, 11, 5 }, new[] { 0, 5, 1 }, new[] { 0, 1, 7 }, new[] { 0, 7, 10 }, new[] { 0, 10, 11 },
                new[] { 1, 5, 9 }, new[] { 5, 11, 4 }, new[] { 11, 10, 2 }, new[] { 10, 7, 6 }, new[] { 7, 1, 8 },
                new[] { 3, 9, 4 }, new[] { 3, 4, 2 }, new[] { 3, 2, 6 }, new[] { 3, 6, 8 }, new[] { 3, 8, 9 },
                new[] { 4, 9, 5 }, new[] { 2, 4, 11 }, new[] { 6, 2, 10 }, new[] { 8, 6, 7 }, new[] { 9, 8, 1 },
            };
            for (int d = 0; d < divisions; d++)
            {
                var mid = new Dictionary<(int, int), int>();
                int Mid(int a, int b)
                {
                    var key = a < b ? (a, b) : (b, a);
                    if (!mid.TryGetValue(key, out int m))
                    {
                        m = dirs.Count;
                        dirs.Add(((dirs[a] + dirs[b]) * 0.5f).normalized);
                        mid[key] = m;
                    }
                    return m;
                }
                var next = new List<int[]>();
                foreach (var f in faces)
                {
                    int ab = Mid(f[0], f[1]), bc = Mid(f[1], f[2]), ca = Mid(f[2], f[0]);
                    next.Add(new[] { f[0], ab, ca });
                    next.Add(new[] { f[1], bc, ab });
                    next.Add(new[] { f[2], ca, bc });
                    next.Add(new[] { ab, bc, ca });
                }
                faces = next;
            }
            return (dirs, faces);
        }
    }
}
