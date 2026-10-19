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
            float a = L.x0 - Beyond, b = L.x1 + Beyond;
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
                if (i > 0 && lv.z > levels[i - 1].z)
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
            for (int i = 0; hill != null && i < hill.Length - 1; i++)
                w.Quad(new Vector3(-HillsWide, hill[i].y, hill[i].z), new Vector3(HillsWide, hill[i].y, hill[i].z),
                       new Vector3(HillsWide, hill[i + 1].y, hill[i + 1].z), new Vector3(-HillsWide, hill[i + 1].y, hill[i + 1].z), "grass", Up);
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
        /// height and line, with shoulders down to the ground on both sides. Seeded from its name.
        /// </summary>
        static void RidgeMesh(MeshWriter w, ulong seed, Ridge r)
        {
            const int N = 220;
            var A = new Vector2(r.ax, r.ay);
            var B = new Vector2(r.bx, r.by);
            Vector2 d = (B - A).normalized;
            Vector2 side = new Vector2(-d.y, d.x); // the ridge's back
            ulong rs = Hash.Of(seed, r.name);
            float foot = -12f, half = r.width * 0.5f;
            Vector3[] prev = null;
            for (int i = 0; i <= N; i++)
            {
                float t = i / (float)N;
                float envelope = Mathf.Pow(Mathf.Max(0f, Mathf.Sin(Mathf.PI * t)), 0.35f); // sin(pi) is a hair below zero in floats
                float rough = 0.55f * Noise1(rs, t * 7f) + 0.3f * Noise1(Hash.Of(rs, 1), t * 17f) + 0.15f * Noise1(Hash.Of(rs, 2), t * 41f);
                float h = r.height * envelope * (0.55f + 0.45f * rough);
                float crest = half * 0.18f * (Noise1(Hash.Of(rs, 3), t * 5f) - 0.5f);
                float sf = 0.4f + 0.25f * Noise1(Hash.Of(rs, 4), t * 9f), sb = 0.4f + 0.25f * Noise1(Hash.Of(rs, 5), t * 11f);
                Vector2 c = Vector2.Lerp(A, B, t);
                Vector3 P(float off, float z)
                {
                    Vector2 q = c + side * off;
                    return new Vector3(q.x, q.y, z);
                }
                var cur = new[]
                {
                    P(-half, foot), P(-half * 0.45f + crest * 0.5f, h * sf), P(crest, h), P(half * 0.45f + crest * 0.5f, h * sb), P(half, foot),
                };
                if (prev != null)
                {
                    for (int k = 0; k < 4; k++)
                    {
                        Vector3 outward = new Vector3((k < 2 ? -side : side).x, (k < 2 ? -side : side).y, 1.2f);
                        w.Quad(prev[k], cur[k], cur[k + 1], prev[k + 1], "rock", outward);
                    }
                }
                prev = cur;
            }
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
