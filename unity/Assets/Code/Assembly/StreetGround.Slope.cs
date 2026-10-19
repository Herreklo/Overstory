using System.Collections.Generic;
using UnityEngine;
using Overstory.Core;
using Overstory.World;

namespace Overstory.Assembly
{
    /// <summary>
    /// The town above the street, generated from the fixture's slope: levels of ground held by
    /// dry-stone retaining walls, the lane along each level, stepped lanes climbing between the
    /// houses, the hillside beyond, and ridges of hills and mountains in the distance.
    ///
    /// Where the levels, lanes, stairs and ridges are is the fixture's (authored geography, until
    /// the fabric pass writes it). How each stone sits and how a ridge's crest wanders is seeded
    /// texture and claims nothing.
    /// </summary>
    public static partial class StreetGround
    {
        const float CapWidth = 0.45f, CapRise = 0.08f;
        const float StepRise = 0.18f;
        const float Parapet = 0.7f, ParapetWidth = 0.35f;
        const float HillsWide = 4000f;      // how far the hillside carries on along the coast

        static string SurfaceSwatch(string surface) => surface switch
        {
            "grass" => "grass",
            "ground" => "grass",
            "asphalt" => "asphalt",
            "gravel" => "gravel",
            "setts" => "setts_mean",
            "flags" => "flags",
            _ => surface,
        };

        /// <summary>Retaining walls in this chunk: coursed dry stone with a row of capstones on top.</summary>
        static void RetainingWalls(MeshWriter w, ulong seed, StreetLayout L, Span s)
        {
            var levels = L.slope.levels;
            if (L.slope.HasSite)
            {
                // the terraces fill the bay; beside it the hills rise
                float a = Mathf.Max(s.a, L.slope.site.bayX0), b = Mathf.Min(s.b, L.slope.site.bayX1);
                if (b <= a)
                    return;
                s = new Span(Mathf.Max(s.x0, L.slope.site.bayX0), Mathf.Min(s.x1, L.slope.site.bayX1), a, b);
            }
            for (int i = 1; i < levels.Length; i++)
            {
                float face = levels[i].y0, bottom = levels[i - 1].z, top = levels[i].z;
                if (top <= bottom)
                    continue;
                var f = Frame.Wall(face);
                ulong ws = Hash.Of(Hash.Of(seed, "retaining"), (ulong)i);
                w.Quad(new Vector3(s.a, face, top), new Vector3(s.b, face, top), new Vector3(s.b, face, bottom), new Vector3(s.a, face, bottom), "joint", Harbour);
                float z = top;
                for (int c = 0; z > bottom + 0.05f; c++)
                {
                    float z0 = Mathf.Max(z - Hash.Range(Hash.Of(ws, Hash.Key(c)), 0.22f, 0.38f), bottom);
                    foreach (var p in Pieces(Hash.Of(ws, Hash.Key(c), 3), s, 0.35f, 0.9f, 0.025f))
                        w.Stone(f, p.a, p.b, z0 + 0.012f, z - 0.012f, Hash.Range(Hash.Of(p.h, 5), 0.0f, 0.035f), 0.03f, 0.08f, "drystone", "drystone", Vector2.zero);
                    z = z0;
                }
                // capstones along the top, a little proud of the face and of the level behind
                foreach (var p in Pieces(Hash.Of(ws, "cap"), s, 0.6f, 1.1f, 0.02f))
                    w.Stone(Frame.Ground, p.a, p.b, face - 0.05f, face + CapWidth, top + CapRise + Hash.Range(Hash.Of(p.h, 9), -0.01f, 0.01f), 0.02f, CapRise + 0.15f,
                            "drystone", "drystone", Tilt(Hash.Of(p.h, 3), 0.006f));
            }
        }

        /// <summary>The levels' ground and lanes, plain walls past the street's ends, and the hillside.</summary>
        static void Levels(MeshWriter w, StreetLayout L)
        {
            bool site = L.slope.HasSite;
            float a = site ? L.slope.site.bayX0 : L.x0 - Beyond, b = site ? L.slope.site.bayX1 : L.x1 + Beyond;
            var levels = L.slope.levels;
            for (int i = 0; i < levels.Length; i++)
            {
                var lv = levels[i];
                string ground = SurfaceSwatch(lv.surface);
                bool lane = lv.lane != null && !string.IsNullOrEmpty(lv.lane.surface) && lv.lane.y1 > lv.lane.y0;
                if (lane)
                {
                    Flat(w, a, b, lv.y0, lv.lane.y0, lv.z, ground);
                    Flat(w, a, b, lv.lane.y0, lv.lane.y1, lv.z, SurfaceSwatch(lv.lane.surface));
                    Flat(w, a, b, lv.lane.y1, lv.y1, lv.z, ground);
                }
                else
                {
                    Flat(w, a, b, lv.y0, lv.y1, lv.z, ground);
                }
                if (!site && i > 0 && lv.z > levels[i - 1].z)
                {
                    // past the detailed street the walls are plain, far enough out to dissolve in the air
                    float bottom = levels[i - 1].z, top = lv.z;
                    foreach (var (wa, wb) in new[] { (a, L.x0), (L.x1, b) })
                    {
                        w.Quad(new Vector3(wa, lv.y0, top), new Vector3(wb, lv.y0, top), new Vector3(wb, lv.y0, bottom), new Vector3(wa, lv.y0, bottom), "drystone", Harbour);
                        w.Quad(new Vector3(wa, lv.y0 - 0.05f, top + CapRise), new Vector3(wb, lv.y0 - 0.05f, top + CapRise),
                               new Vector3(wb, lv.y0 + CapWidth, top + CapRise), new Vector3(wa, lv.y0 + CapWidth, top + CapRise), "drystone", Up);
                    }
                }
            }
            var hill = L.slope.hillside;
            for (int i = 0; !site && hill != null && i < hill.Length - 1; i++)
                w.Quad(new Vector3(-HillsWide, hill[i].y, hill[i].z), new Vector3(HillsWide, hill[i].y, hill[i].z),
                       new Vector3(HillsWide, hill[i + 1].y, hill[i + 1].z), new Vector3(-HillsWide, hill[i + 1].y, hill[i + 1].z),
                       SurfaceSwatch(string.IsNullOrEmpty(L.slope.hillsideSurface) ? "grass" : L.slope.hillsideSurface), Up);
        }

        static void Flat(MeshWriter w, float a, float b, float y0, float y1, float z, string swatch)
        {
            if (y1 - y0 > 1e-3f)
                w.Quad(new Vector3(a, y0, z), new Vector3(b, y0, z), new Vector3(b, y1, z), new Vector3(a, y1, z), swatch, Up);
        }

        /// <summary>
        /// A stepped lane: flags where its path runs level; where it climbs, stone steps of equal rise on a
        /// solid flight, between stepped parapet walls.
        /// </summary>
        static void Stairs(MeshWriter w, ulong seed, Stair st)
        {
            float x0 = st.x - st.width * 0.5f, x1 = st.x + st.width * 0.5f;
            ulong ss = Hash.Of(seed, st.name);
            for (int k = 0; k < st.path.Length - 1; k++)
            {
                YZ p = st.path[k], q = st.path[k + 1];
                float dy = q.y - p.y, dz = q.z - p.z;
                if (Mathf.Abs(dz) < 1e-3f)
                {
                    // level: a strip of flags with a kerb of stone each side
                    w.Stone(Frame.Ground, x0, x1, p.y, q.y, p.z + 0.03f, 0.01f, 0.06f, "flags", "flags", Vector2.zero);
                    continue;
                }
                int n = Mathf.Max(1, Mathf.CeilToInt(dz / StepRise));
                float rise = dz / n, tread = dy / n;
                for (int i = 0; i < n; i++)
                {
                    float ya = p.y + tread * i, yb = p.y + tread * (i + 1);
                    float top = p.z + rise * (i + 1);
                    ulong h = Hash.Of(ss, Hash.Key(k * 1000 + i));
                    // the step: its nose a little proud, its body down to the step below
                    w.Stone(Frame.Ground, x0, x1, ya - 0.02f, yb, top + Hash.Range(h, -0.004f, 0.004f), 0.012f, rise + 0.02f, "stone", "stone", Tilt(h, 0.004f));
                    // the flight's solid sides, step by step, down to the ground it starts from
                    float under = top - rise;
                    if (under > p.z + 1e-3f)
                    {
                        w.Quad(new Vector3(x0, ya, p.z), new Vector3(x0, yb, p.z), new Vector3(x0, yb, under), new Vector3(x0, ya, under), "drystone", new Vector3(-1, 0, 0));
                        w.Quad(new Vector3(x1, ya, p.z), new Vector3(x1, yb, p.z), new Vector3(x1, yb, under), new Vector3(x1, ya, under), "drystone", new Vector3(1, 0, 0));
                    }
                    // stepped parapets
                    float wallTop = top + Parapet;
                    w.Stone(Frame.Ground, x0 - ParapetWidth, x0, ya, yb + 0.01f, wallTop, 0.02f, wallTop - p.z, "drystone", "drystone", Vector2.zero);
                    w.Stone(Frame.Ground, x1, x1 + ParapetWidth, ya, yb + 0.01f, wallTop, 0.02f, wallTop - p.z, "drystone", "drystone", Vector2.zero);
                }
            }
        }

        /// <summary>
        /// A ridge of hills or mountains: a crest running from a to b, rising from its ends, wandering in
        /// height and line, with shoulders down to the ground on both sides, built as crisp facets that
        /// catch the light plane by plane. Seeded from its name.
        /// </summary>
        static Mesh RidgeMesh(Palette pal, ulong seed, Ridge r)
        {
            const int N = 70, K = 7; // samples along the ridge, and across it: few, so the faces read
            var A = new Vector2(r.ax, r.ay);
            var B = new Vector2(r.bx, r.by);
            Vector2 d = (B - A).normalized;
            Vector2 side = new Vector2(-d.y, d.x);
            ulong rs = Hash.Of(seed, r.name);
            float foot = -12f, half = r.width * 0.5f;
            var verts = new List<Vector3>((N + 1) * K);
            for (int i = 0; i <= N; i++)
            {
                float t = i / (float)N;
                float envelope = Mathf.Pow(Mathf.Max(0f, Mathf.Sin(Mathf.PI * t)), 0.35f); // sin(pi) is a hair below zero in floats
                float rough = 0.55f * Noise1(rs, t * 7f) + 0.3f * Noise1(Hash.Of(rs, 1), t * 17f) + 0.15f * Noise1(Hash.Of(rs, 2), t * 41f);
                float h = r.height * envelope * (0.55f + 0.45f * rough);
                float crest = half * 0.18f * (Noise1(Hash.Of(rs, 3), t * 5f) - 0.5f);
                float sf = 0.75f + 0.5f * Noise1(Hash.Of(rs, 4), t * 9f), sb = 0.75f + 0.5f * Noise1(Hash.Of(rs, 5), t * 11f);
                Vector2 c = Vector2.Lerp(A, B, t);
                for (int k = 0; k < K; k++)
                {
                    // across the ridge: a convex-then-concave profile from foot to crest to foot
                    float u = k / (float)(K - 1) * 2f - 1f; // -1 front foot, 0 crest, 1 back foot
                    float shape = Mathf.Pow(1f - Mathf.Abs(u), u < 0 ? sf : sb);
                    float off = Mathf.Lerp(crest, u < 0 ? -half : half, Mathf.Abs(u));
                    Vector2 q = c + side * off;
                    verts.Add(StreetSpace.ToUnity(q.x, q.y, Mathf.Lerp(foot, h, shape)));
                }
            }
            var tris = new List<int>(N * (K - 1) * 6);
            for (int i = 0; i < N; i++)
                for (int k = 0; k < K - 1; k++)
                {
                    int a = i * K + k, b = (i + 1) * K + k;
                    tris.Add(a); tris.Add(b); tris.Add(a + 1);
                    tris.Add(a + 1); tris.Add(b); tris.Add(b + 1);
                }
            // wind the surface to face up, whichever way the ridge runs
            Vector3 ca = verts[(N / 2) * K + K / 2], cb = verts[(N / 2 + 1) * K + K / 2], cc = verts[(N / 2) * K + K / 2 + 1];
            if (Vector3.Cross(cb - ca, cc - ca).y < 0f)
                for (int i = 0; i < tris.Count; i += 3)
                    (tris[i + 1], tris[i + 2]) = (tris[i + 2], tris[i + 1]);
            var m = Faceted(r.name, verts, tris, pal.UV(string.IsNullOrEmpty(r.surface) ? "rock" : r.surface));
            return m;
        }

        /// <summary>
        /// The ground around the town, as a height field generated from the site's facts: the bay the
        /// town fills, the hills that rise beside it (and run out into the sea as headlands), the
        /// hillside climbing behind it, and seeded roughness that fades out near the town. Inside the
        /// bay the terraces and walls are drawn by Levels and RetainingWalls, so the field leaves a hole
        /// there; at the bay's edges it meets them at their own heights.
        /// </summary>
        static Mesh SiteTerrain(Palette pal, ulong seed, StreetLayout L)
        {
            var site = L.slope.site;
            var levels = L.slope.levels;
            var hill = L.slope.hillside;
            float edge = L.quay.edge, townBack = levels[levels.Length - 1].y1;
            const float Cell = 14f; // facets large enough to read as planes
            float x0 = site.bayX0 - 1300f, x1 = site.bayX1 + 1300f, y0 = edge - 900f, y1 = 1100f;
            int nx = Mathf.CeilToInt((x1 - x0) / Cell), ny = Mathf.CeilToInt((y1 - y0) / Cell);
            ulong rs = Hash.Of(seed, "site");

            float LevelZ(float y)
            {
                float z = 0f;
                foreach (var lv in levels)
                    if (y >= lv.y0)
                        z = lv.z;
                return z;
            }
            float Profile(float y)
            {
                if (y <= hill[0].y)
                    return Mathf.Lerp(0f, hill[0].z, Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(y / hill[0].y)));
                for (int i = 0; i < hill.Length - 1; i++)
                    if (y <= hill[i + 1].y)
                        return Mathf.Lerp(hill[i].z, hill[i + 1].z, Mathf.SmoothStep(0f, 1f, (y - hill[i].y) / (hill[i + 1].y - hill[i].y)));
                return hill[hill.Length - 1].z;
            }
            float Height(float x, float y)
            {
                float d = Mathf.Max(site.bayX0 - x, x - site.bayX1, 0f);           // how far outside the bay
                float t = Mathf.Clamp01(d / site.sideReach);
                float side = site.sideHeight * (1f - (1f - t) * (1f - t));         // rising fast, then easing
                float back = y < townBack ? Mathf.Lerp(LevelZ(y), Profile(y), Mathf.SmoothStep(0f, 1f, d / 40f)) : Profile(y);
                float h;
                if (y >= edge)
                    h = Mathf.Max(back, side);
                else
                {
                    // the sea: the bay's floor; beside it the hills run out as headlands, then drop under the water
                    float out_ = Mathf.Clamp01((edge - y) / (site.sideReach * 1.2f));
                    h = Mathf.Lerp(side, -14f, Mathf.SmoothStep(0f, 1f, out_)) - (d <= 0f ? 14f : 0f);
                }
                float near = Mathf.Sqrt(d * d + Mathf.Max(0f, y - townBack) * Mathf.Max(0f, y - townBack));
                float fade = Mathf.SmoothStep(0f, 1f, near / 80f);
                float rough = 0.6f * Noise2(rs, x / site.roughScale, y / site.roughScale) + 0.4f * Noise2(Hash.Of(rs, 1), x / (site.roughScale * 0.35f), y / (site.roughScale * 0.35f));
                return h + site.roughHeight * (rough - 0.5f) * 2f * fade;
            }
            bool InTown(float x, float y) => x > site.bayX0 + 0.5f && x < site.bayX1 - 0.5f && y > edge - 0.5f && y < townBack - 0.5f;

            var verts = new List<Vector3>((nx + 1) * (ny + 1));
            for (int j = 0; j <= ny; j++)
                for (int i = 0; i <= nx; i++)
                {
                    float x = x0 + i * Cell, y = y0 + j * Cell;
                    verts.Add(StreetSpace.ToUnity(x, y, Height(x, y)));
                }
            var tris = new List<int>(nx * ny * 6);
            for (int j = 0; j < ny; j++)
                for (int i = 0; i < nx; i++)
                {
                    float xa = x0 + i * Cell, ya = y0 + j * Cell;
                    if (InTown(xa, ya) && InTown(xa + Cell, ya + Cell) && InTown(xa + Cell, ya) && InTown(xa, ya + Cell))
                        continue;
                    int a = j * (nx + 1) + i, b = a + 1, c = a + nx + 1, e = c + 1;
                    // wound so the surface faces up in Unity's left-handed space
                    tris.Add(a); tris.Add(c); tris.Add(b);
                    tris.Add(b); tris.Add(c); tris.Add(e);
                }
            var m = Faceted("site terrain", verts, tris, pal.UV(SurfaceSwatch(string.IsNullOrEmpty(site.surface) ? "heath" : site.surface)));
            return m;
        }

        /// <summary>Smooth seeded value noise over a plane, 0..1.</summary>
        static float Noise2(ulong h, float u, float v)
        {
            int i = Mathf.FloorToInt(u), j = Mathf.FloorToInt(v);
            float fu = u - i, fv = v - j;
            fu = fu * fu * (3f - 2f * fu);
            fv = fv * fv * (3f - 2f * fv);
            float H(int a, int b) => Hash.Unit(Hash.Of(h, Hash.Key(a), Hash.Key(b)));
            return Mathf.Lerp(Mathf.Lerp(H(i, j), H(i + 1, j), fu), Mathf.Lerp(H(i, j + 1), H(i + 1, j + 1), fu), fv);
        }

        /// <summary>
        /// Land as crisp planes: every triangle its own flat face, so a slope catches the low sun or
        /// loses it as a whole, like a carved or painted landform, not a smooth blob.
        /// </summary>
        static Mesh Faceted(string name, List<Vector3> verts, List<int> tris, Vector2 uv)
        {
            var fv = new List<Vector3>(tris.Count);
            var fn = new List<Vector3>(tris.Count);
            var fc = new List<Color>(tris.Count);
            var fu = new List<Vector2>(tris.Count);
            var ft = new List<int>(tris.Count);
            for (int i = 0; i < tris.Count; i += 3)
            {
                Vector3 a = verts[tris[i]], b = verts[tris[i + 1]], c = verts[tris[i + 2]];
                Vector3 n = Vector3.Cross(b - a, c - a);
                if (n.sqrMagnitude < 1e-10f)
                    continue;
                n.Normalize();
                var seen = new Color(0.5f + 0.5f * n.y, 0.5f - 0.5f * n.y, 1f, 1f); // open slopes: sky above, ground below
                int k = fv.Count;
                fv.Add(a); fv.Add(b); fv.Add(c);
                for (int j = 0; j < 3; j++) { fn.Add(n); fc.Add(seen); fu.Add(uv); }
                ft.Add(k); ft.Add(k + 1); ft.Add(k + 2);
            }
            var m = new Mesh { name = name, hideFlags = HideFlags.DontSave, indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            m.SetVertices(fv);
            m.SetNormals(fn);
            m.SetColors(fc);
            m.SetUVs(0, fu);
            m.SetTriangles(ft, 0, true);
            return m;
        }

        /// <summary>Smooth seeded value noise along one dimension, 0..1.</summary>
        static float Noise1(ulong h, float u)
        {
            int i = Mathf.FloorToInt(u);
            float f = u - i;
            f = f * f * (3f - 2f * f);
            return Mathf.Lerp(Hash.Unit(Hash.Of(h, Hash.Key(i))), Hash.Unit(Hash.Of(h, Hash.Key(i + 1))), f);
        }
    }
}
