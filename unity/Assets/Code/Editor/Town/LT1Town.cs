using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Path = System.IO.Path;
using Object = UnityEngine.Object;

namespace Overstory.EditorTools.Town
{
    /// <summary>
    /// LT1's harbour town (fixtures/lt1-harbour-town.json, grown by blender/tools/grow_harbour.py), judged from the city
    /// camera (reviews/lt1/town/).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.Town.LT1Town.Grey
    ///         [-out reviews/lt1/town/r01] [-views mid,midhigh,street,roam1,...]
    ///
    /// Grey composes the town in memory as grey masses (the ground carved as the fixture has it, the water, the quay,
    /// each house a body, a roof and a plinth down to its lowest ground) under one grey light, and renders the views.
    /// </summary>
    public static class LT1Town
    {
        public const string Fixture = "fixtures/lt1-harbour-town.json";
        const string LT1 = "Assets/Experiments/LT1";

        // -- the fixture, as JsonUtility reads it (point lists flat) -------------------------------------------------

        [Serializable] public class Grid { public int x0, y0, step, nx, ny; public int[] z; public int[] kind; }
        [Serializable] public class Quay { public int[] edge; public int top, water, row; }
        [Serializable] public class Place { public string id, name; public int z; public int[] points; }
        [Serializable] public class Lane { public string id, name, surface; public int z, width, laid; public int[] points; }
        [Serializable] public class Stair { public string id, name; public int width; public int[] points; }
        [Serializable]
        public class Placement
        {
            public int id, of, x, y, w, d, @base, eave, pitch;
            public float angle;
            public string kind, lane, side, roof;
            public int[] footprint;
        }
        [Serializable] public class Tree { public string id, species, crown; public int x, y, z, h, r, planted; }
        [Serializable]
        public class Town
        {
            public Quay quay;
            public Lane[] lanes;
            public Stair[] stairs;
            public Placement[] placements;
            public Tree[] trees;
            public Place[] places;
            public Grid ground, coarse;
        }

        public static Town Load(string repo) =>
            JsonUtility.FromJson<Town>(File.ReadAllText(Path.Combine(repo, Fixture)));

        static Vector3 U(float x, float y, float z) => new Vector3(x, z, y);   // street frame (m) to Unity
        const float M = 0.001f;

        /// <summary>The views: the two city cameras, the street stop and the roam's poses (street frame, m).</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Views =
        {
            ("mid", new Vector3(55f, -115f, 46f), new Vector3(58f, 45f, 15f), 42f),
            ("midhigh", new Vector3(52f, -150f, 75f), new Vector3(55f, 30f, 4f), 42f),
            // the street stop: on Harbour Row at the gully's foot, three metres up, into the Gully Steps
            ("street", new Vector3(47f, -14f, 3.2f), new Vector3(50f, 30f, 9f), 46.4f),
            // the roam: the free camera over the harbour's west end, over the east roofs, and down from the heath
            ("roam1", new Vector3(-40f, -70f, 28f), new Vector3(40f, 40f, 10f), 42f),
            ("roam2", new Vector3(150f, -40f, 34f), new Vector3(60f, 50f, 14f), 42f),
            ("roam3", new Vector3(70f, 150f, 70f), new Vector3(55f, 0f, 0f), 42f),
        };

        public static void Grey()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string dir = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/town/r01"));
            Directory.CreateDirectory(dir);
            var town = Load(repo);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var made = new List<Object>();
            var root = new GameObject("Town (grey)");

            var lit = Shader.Find("Universal Render Pipeline/Lit");
            Material Grey(float v)
            {
                var m = new Material(lit) { hideFlags = HideFlags.DontSave };
                m.SetColor("_BaseColor", new Color(v, v, v));
                m.SetFloat("_Smoothness", 0.05f);
                made.Add(m);
                return m;
            }
            var ground = Grey(0.42f);
            var paved = Grey(0.56f);
            var water = Grey(0.16f);
            var wall = Grey(0.55f);
            var roofM = Grey(0.30f);
            var plinth = Grey(0.36f);
            var crown = Grey(0.34f);
            var trunk = Grey(0.26f);

            Add(root, "ground", GroundMesh(town.ground, true), ground, made);
            Add(root, "paving", Paving(town), paved, made);
            Add(root, "land", GroundMesh(town.coarse, false), ground, made);
            Add(root, "water", Plane(-1600f, -1400f, 1700f, 1900f, town.quay.water * M), water, made);
            Add(root, "quay wall", QuayWall(town.quay), plinth, made);
            if (town.trees != null && town.trees.Length > 0)
            {
                var (crowns, trunks) = Trees(town.trees);
                Add(root, "tree crowns", crowns, crown, made);
                Add(root, "tree trunks", trunks, trunk, made);
            }
            var houses = new GameObject("houses");
            houses.transform.SetParent(root.transform, false);
            foreach (var p in town.placements)
            {
                var (body, roof, foot) = Masses(p, town.ground);
                Add(houses, $"house {p.id}", body, wall, made);
                Add(houses, $"house {p.id} roof", roof, roofM, made);
                Add(houses, $"house {p.id} plinth", foot, plinth, made);
            }

            // one grey light: the sky from above, a low key from the west
            var sunGo = new GameObject("key");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.1f;
            sun.color = Color.white;
            sun.shadows = LightShadows.Soft;
            sunGo.transform.rotation = Quaternion.LookRotation(U(0.55f, 0.35f, -0.55f).normalized, Vector3.up);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.55f, 0.55f, 0.55f);
            RenderSettings.ambientEquatorColor = new Color(0.42f, 0.42f, 0.42f);
            RenderSettings.ambientGroundColor = new Color(0.2f, 0.2f, 0.2f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.78f, 0.78f, 0.78f);
            RenderSettings.fogStartDistance = 120f;
            RenderSettings.fogEndDistance = 1400f;
            RenderSettings.skybox = null;

            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.8f, 0.8f, 0.8f);
            cam.allowMSAA = true;
            var data = camGo.AddComponent<UniversalAdditionalCameraData>();
            data.renderShadows = true;
            if (GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
                urp.shadowDistance = 600f;

            foreach (var v in Views)
            {
                if (!Cli.Wanted("-views", v.name))
                    continue;
                Vector3 p = U(v.pos.x, v.pos.y, v.pos.z), t = U(v.target.x, v.target.y, v.target.z);
                cam.transform.SetPositionAndRotation(p, Quaternion.LookRotation(t - p, Vector3.up));
                cam.fieldOfView = v.fov;
                cam.nearClipPlane = 0.3f;
                cam.farClipPlane = 6000f;
                string file = Path.Combine(dir, $"{v.name}-grey.png");
                LT1Render.Still(cam, file, grey: false, msaa: 4);
                Debug.Log($"[LT1Town] {file}");
            }
            foreach (var o in made)
                Object.DestroyImmediate(o);
        }

        static void Add(GameObject parent, string name, Mesh mesh, Material mat, List<Object> made)
        {
            made.Add(mesh);
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = mat;
        }

        // -- the ground ------------------------------------------------------------------------------------------------

        public static float GroundAt(Grid g, float x, float y)
        {
            float fx = (x - g.x0 * M) / (g.step * M), fy = (y - g.y0 * M) / (g.step * M);
            int i = Mathf.Clamp(Mathf.FloorToInt(fx), 0, g.nx - 2), j = Mathf.Clamp(Mathf.FloorToInt(fy), 0, g.ny - 2);
            float tx = Mathf.Clamp01(fx - i), ty = Mathf.Clamp01(fy - j);
            float a = Mathf.Lerp(g.z[j * g.nx + i], g.z[j * g.nx + i + 1], tx);
            float b = Mathf.Lerp(g.z[(j + 1) * g.nx + i], g.z[(j + 1) * g.nx + i + 1], tx);
            return Mathf.Lerp(a, b, ty) * M;
        }

        static Mesh GroundMesh(Grid g, bool fine)
        {
            var v = new Vector3[g.nx * g.ny];
            for (int j = 0; j < g.ny; j++)
                for (int i = 0; i < g.nx; i++)
                    v[j * g.nx + i] = U((g.x0 + i * g.step) * M, (g.y0 + j * g.step) * M, g.z[j * g.nx + i] * M);
            var t = new int[(g.nx - 1) * (g.ny - 1) * 6];
            int k = 0;
            for (int j = 0; j < g.ny - 1; j++)
                for (int i = 0; i < g.nx - 1; i++)
                {
                    int a = j * g.nx + i, b = a + 1, c = a + g.nx, d = c + 1;
                    // street frame to Unity mirrors: wind so the faces look up
                    t[k++] = a; t[k++] = c; t[k++] = b;
                    t[k++] = b; t[k++] = c; t[k++] = d;
                }
            var m = new Mesh { name = fine ? "town ground" : "land", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            m.vertices = v;
            m.triangles = t;
            m.RecalculateNormals();
            m.RecalculateBounds();
            return m;
        }

        static Mesh Plane(float x0, float y0, float x1, float y1, float z)
        {
            var m = new Mesh { name = "plane", hideFlags = HideFlags.DontSave };
            m.vertices = new[] { U(x0, y0, z), U(x1, y0, z), U(x0, y1, z), U(x1, y1, z) };
            m.triangles = new[] { 0, 2, 1, 1, 2, 3 };
            m.RecalculateNormals();
            return m;
        }

        /// <summary>The quay's face, set a metre out from its edge, and its coping: a strip from the face to two metres in,
        /// a hair above the quay, which covers the ground grid's step down to the sea bed.</summary>
        static Mesh QuayWall(Quay q)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            float top = q.top * M, foot = q.water * M - 2.5f;
            int count = q.edge.Length / 2;
            Vector2 E(int i) => new Vector2(q.edge[2 * i] * M, q.edge[2 * i + 1] * M);
            Vector2 Out(int i)
            {
                var d = E(Mathf.Min(i + 1, count - 1)) - E(Mathf.Max(i - 1, 0));
                return new Vector2(d.y, -d.x).normalized;      // seaward: the right of the edge's run east
            }
            for (int i = 0; i + 1 < count; i++)
            {
                Vector2 a = E(i) + Out(i) * 1.0f, b = E(i + 1) + Out(i + 1) * 1.0f;
                Vector2 ai = E(i) - Out(i) * 2.0f, bi = E(i + 1) - Out(i + 1) * 2.0f;
                int n = v.Count;
                v.Add(U(a.x, a.y, top)); v.Add(U(b.x, b.y, top)); v.Add(U(a.x, a.y, foot)); v.Add(U(b.x, b.y, foot));
                t.AddRange(new[] { n, n + 1, n + 2, n + 1, n + 3, n + 2 });
                n = v.Count;
                v.Add(U(a.x, a.y, top + 0.03f)); v.Add(U(b.x, b.y, top + 0.03f)); v.Add(U(ai.x, ai.y, top + 0.03f)); v.Add(U(bi.x, bi.y, top + 0.03f));
                t.AddRange(new[] { n, n + 2, n + 1, n + 1, n + 2, n + 3 });
            }
            var m = new Mesh { name = "quay wall", hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        // -- paving: the Row, the lanes and the level places as their own surfaces, a few centimetres over the ground ----

        static Mesh Paving(Town town)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { int n = v.Count; v.Add(a); v.Add(b); v.Add(c); v.Add(d); t.AddRange(new[] { n, n + 2, n + 1, n + 1, n + 2, n + 3 }); }
            // a strip along a polyline (x, y, z), its sides hw out, its normal in plan from the neighbouring points
            void Strip(IList<Vector3> pts, float hwL, float hwR, float lift)
            {
                Vector2 Side(int i)
                {
                    var d = (Vector2)(pts[Mathf.Min(i + 1, pts.Count - 1)] - pts[Mathf.Max(i - 1, 0)]);
                    return new Vector2(-d.y, d.x).normalized;   // the left of the run
                }
                for (int i = 0; i + 1 < pts.Count; i++)
                {
                    Vector3 a = pts[i], b = pts[i + 1];
                    Vector2 sa = Side(i), sb = Side(i + 1);
                    Quad(U(a.x - sa.x * hwR, a.y - sa.y * hwR, a.z + lift), U(b.x - sb.x * hwR, b.y - sb.y * hwR, b.z + lift),
                         U(a.x + sa.x * hwL, a.y + sa.y * hwL, a.z + lift), U(b.x + sb.x * hwL, b.y + sb.y * hwL, b.z + lift));
                }
            }
            // the Row: from the quay's edge to the building line
            var edge = new List<Vector3>();
            for (int i = 0; i + 1 < town.quay.edge.Length; i += 2)
                edge.Add(new Vector3(town.quay.edge[i] * M, town.quay.edge[i + 1] * M, town.quay.top * M));
            Strip(edge, town.quay.row * M + 0.3f, 0f, 0.02f);
            foreach (var l in town.lanes)
            {
                var pts = new List<Vector3>();
                for (int i = 0; i + 2 < l.points.Length; i += 3)
                    pts.Add(new Vector3(l.points[i] * M, l.points[i + 1] * M, l.points[i + 2] * M));
                Strip(pts, l.width * M / 2, l.width * M / 2, 0.04f);
            }
            if (town.places != null)
                foreach (var pl in town.places)
                {
                    var q = new Vector2[pl.points.Length / 2];
                    for (int i = 0; i < q.Length; i++)
                        q[i] = new Vector2(pl.points[2 * i] * M, pl.points[2 * i + 1] * M);
                    float z = pl.z * M + 0.05f;
                    for (int i = 1; i + 1 < q.Length; i++)
                    {
                        int n = v.Count;
                        v.Add(U(q[0].x, q[0].y, z)); v.Add(U(q[i].x, q[i].y, z)); v.Add(U(q[i + 1].x, q[i + 1].y, z));
                        t.AddRange(new[] { n, n + 1, n + 2 });
                    }
                }
            var m = new Mesh { name = "paving", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        // -- trees: a crown by its kind and a trunk, all in two meshes -------------------------------------------------

        static (Mesh crowns, Mesh trunks) Trees(Tree[] trees)
        {
            var cv = new List<Vector3>();
            var ct = new List<int>();
            var tv = new List<Vector3>();
            var tt = new List<int>();
            const int seg = 7, rings = 5;
            foreach (var tr in trees)
            {
                float x = tr.x * M, y = tr.y * M, z = tr.z * M, h = tr.h * M, r = tr.r * M;
                // the crown's bottom and top above the ground, and its shape along its height (radius at u in 0..1)
                float c0, c1;
                Func<float, float> radius;
                switch (tr.crown)
                {
                    case "cone": c0 = 0.04f * h; c1 = h; radius = u => r * Mathf.Min(1f, u / 0.12f) * Mathf.Pow(1f - u, 0.95f); break;
                    case "tall": c0 = 0.26f * h; c1 = h; radius = u => r * Mathf.Sin(Mathf.PI * Mathf.Pow(u, 0.75f)); break;
                    case "flat": c0 = 0.45f * h; c1 = h; radius = u => r * Mathf.Sin(Mathf.PI * Mathf.Pow(u, 0.6f)); break;
                    default: c0 = Mathf.Max(1.6f, 0.22f * h); c1 = h; radius = u => r * Mathf.Sin(Mathf.PI * Mathf.Pow(u, 0.8f)); break;
                }
                float rot = (tr.x * 7 + tr.y * 13) % 360 * Mathf.Deg2Rad;
                int n0 = cv.Count;
                cv.Add(U(x, y, z + c0));
                for (int k = 1; k < rings; k++)
                {
                    float u = k / (float)rings;
                    float rr = radius(u);
                    for (int s = 0; s < seg; s++)
                    {
                        float a = rot + s * Mathf.PI * 2f / seg;
                        cv.Add(U(x + Mathf.Cos(a) * rr, y + Mathf.Sin(a) * rr, z + c0 + (c1 - c0) * u));
                    }
                }
                cv.Add(U(x, y, z + c1));
                int top = cv.Count - 1;
                for (int s = 0; s < seg; s++)
                {
                    int s1 = (s + 1) % seg;
                    ct.AddRange(new[] { n0, n0 + 1 + s1, n0 + 1 + s });
                    for (int k = 0; k < rings - 2; k++)
                    {
                        int a = n0 + 1 + k * seg + s, b = n0 + 1 + k * seg + s1, c = a + seg, d = b + seg;
                        ct.AddRange(new[] { a, b, c, b, d, c });
                    }
                    int l = n0 + 1 + (rings - 2) * seg;
                    ct.AddRange(new[] { l + s, l + s1, top });
                }
                // the trunk: a square post from below the ground into the crown
                float tw = Mathf.Clamp(h * 0.025f, 0.12f, 0.4f);
                var post = Prism(new[] { new Vector2(x - tw, y - tw), new Vector2(x + tw, y - tw), new Vector2(x + tw, y + tw), new Vector2(x - tw, y + tw) }, z - 1f, z + c0 + (c1 - c0) * 0.3f);
                int m0 = tv.Count;
                tv.AddRange(post.vertices);
                foreach (var i in post.triangles)
                    tt.Add(m0 + i);
                Object.DestroyImmediate(post);
            }
            // the crowns were wound counterclockwise seen from outside in the street frame, which the mirror into
            // Unity turns inwards: flip them
            for (int i = 0; i < ct.Count; i += 3)
                (ct[i + 1], ct[i + 2]) = (ct[i + 2], ct[i + 1]);
            Mesh Make(string name, List<Vector3> v, List<int> t)
            {
                var m = new Mesh { name = name, indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
                m.SetVertices(v);
                m.SetTriangles(t, 0);
                m.RecalculateNormals();
                return m;
            }
            return (Make("tree crowns", cv, ct), Make("tree trunks", tv, tt));
        }

        // -- a house as masses: body, roof, plinth -----------------------------------------------------------------------

        static (Mesh body, Mesh roof, Mesh foot) Masses(Placement p, Grid g)
        {
            var fp = new Vector2[4];
            for (int i = 0; i < 4; i++)
                fp[i] = new Vector2(p.footprint[2 * i] * M, p.footprint[2 * i + 1] * M);
            float b = p.@base * M, e = p.eave * M;
            float low = b;
            foreach (var q in fp)
                low = Mathf.Min(low, GroundAt(g, q.x, q.y));
            for (int i = 0; i < 4; i++)
            {
                var mid = 0.5f * (fp[i] + fp[(i + 1) % 4]);
                low = Mathf.Min(low, GroundAt(g, mid.x, mid.y));
            }
            var body = Prism(fp, b, e);
            var foot = Prism(fp, low - 0.3f, b);
            // the roof: ridge along the front (eaves) or front to back (gable), the eaves out 0.4 m
            Vector2 u = (fp[1] - fp[0]).normalized, n = (fp[3] - fp[0]).normalized;
            float W = Vector2.Distance(fp[0], fp[1]), D = Vector2.Distance(fp[0], fp[3]);
            float o = 0.4f, tan = Mathf.Tan(p.pitch * Mathf.Deg2Rad);
            Vector2 c0 = fp[0] - u * o - n * o;
            float L = W + 2 * o, S = D + 2 * o;
            var v = new List<Vector3>();
            var t = new List<int>();
            Vector3 P(float s, float w, float z) { var q = c0 + u * s + n * w; return U(q.x, q.y, z); }
            void Quad(Vector3 a, Vector3 bb, Vector3 c, Vector3 d) { int k = v.Count; v.Add(a); v.Add(bb); v.Add(c); v.Add(d); t.AddRange(new[] { k, k + 2, k + 1, k, k + 3, k + 2 }); }
            void Tri(Vector3 a, Vector3 bb, Vector3 c) { int k = v.Count; v.Add(a); v.Add(bb); v.Add(c); t.AddRange(new[] { k, k + 2, k + 1 }); }
            if (p.roof == "spire")
            {
                var apex = 0.5f * (fp[0] + fp[2]);
                float za = e + (W / 2) * tan;
                for (int i = 0; i < 4; i++)
                {
                    Vector2 q0 = fp[i] + (fp[i] - apex).normalized * 0.3f, q1 = fp[(i + 1) % 4] + (fp[(i + 1) % 4] - apex).normalized * 0.3f;
                    Tri(U(q0.x, q0.y, e), U(apex.x, apex.y, za), U(q1.x, q1.y, e));
                }
            }
            else if (p.roof == "gable")
            {
                float zr = e + (W / 2) * tan;
                // ridge runs front to back (along n) at the middle of u
                Quad(P(0, 0, e - o * tan), P(0, S, e - o * tan), P(L / 2, S, zr), P(L / 2, 0, zr));
                Quad(P(L / 2, 0, zr), P(L / 2, S, zr), P(L, S, e - o * tan), P(L, 0, e - o * tan));
                Tri(P(o, o, e), P(L / 2, o, zr), P(L - o, o, e));
                Tri(P(L - o, S - o, e), P(L / 2, S - o, zr), P(o, S - o, e));
            }
            else
            {
                float zr = e + (D / 2) * tan;
                Quad(P(0, 0, e - o * tan), P(L, 0, e - o * tan), P(L, S / 2, zr), P(0, S / 2, zr));
                Quad(P(0, S / 2, zr), P(L, S / 2, zr), P(L, S, e - o * tan), P(0, S, e - o * tan));
                Tri(P(o, S - o, e), P(o, S / 2, zr), P(o, o, e));
                Tri(P(L - o, o, e), P(L - o, S / 2, zr), P(L - o, S - o, e));
            }
            var roof = new Mesh { name = "roof", hideFlags = HideFlags.DontSave };
            roof.SetVertices(v);
            roof.SetTriangles(t, 0);
            roof.RecalculateNormals();
            DoubleSided(roof);
            return (body, roof, foot);
        }

        static Mesh Prism(Vector2[] fp, float z0, float z1)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            for (int i = 0; i < fp.Length; i++)
            {
                var a = fp[i];
                var b = fp[(i + 1) % fp.Length];
                int k = v.Count;
                v.Add(U(a.x, a.y, z0)); v.Add(U(b.x, b.y, z0)); v.Add(U(b.x, b.y, z1)); v.Add(U(a.x, a.y, z1));
                t.AddRange(new[] { k, k + 2, k + 1, k, k + 3, k + 2 });
            }
            int top = v.Count;
            foreach (var q in fp)
                v.Add(U(q.x, q.y, z1));
            t.AddRange(new[] { top, top + 2, top + 1, top, top + 3, top + 2 });
            var m = new Mesh { name = "prism", hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        /// <summary>Greybox only: every face drawn from both sides, so a winding slip shows as a face, not a hole.</summary>
        static void DoubleSided(Mesh m)
        {
            var v = m.vertices;
            var n = m.normals;
            var t = m.triangles;
            var v2 = new Vector3[v.Length * 2];
            var n2 = new Vector3[v.Length * 2];
            var t2 = new int[t.Length * 2];
            for (int i = 0; i < v.Length; i++) { v2[i] = v[i]; v2[i + v.Length] = v[i]; n2[i] = n[i]; n2[i + v.Length] = -n[i]; }
            for (int i = 0; i < t.Length; i += 3)
            {
                t2[i] = t[i]; t2[i + 1] = t[i + 1]; t2[i + 2] = t[i + 2];
                t2[t.Length + i] = t[i] + v.Length; t2[t.Length + i + 1] = t[i + 2] + v.Length; t2[t.Length + i + 2] = t[i + 1] + v.Length;
            }
            m.vertices = v2;
            m.normals = n2;
            m.triangles = t2;
        }
    }
}
