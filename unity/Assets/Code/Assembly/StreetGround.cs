using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Overstory.Core;
using Overstory.World;

namespace Overstory.Assembly
{
    /// <summary>
    /// The ground of a street, generated from its layout: the pavement's flags and kerb, the
    /// carriageway's setts with a gutter along the kerb and a row of binding stones at its edge, the
    /// quay's setts and granite coping, the quay wall down into the harbour, the water, and the
    /// ground behind the plots.
    ///
    /// What each band is made of comes from the fixture (surface, when it was laid). How each stone
    /// sits (its length, a millimetre of height, a hair of tilt) is texture seeded from the world
    /// seed; it claims no history.
    ///
    /// All coordinates here are street coordinates in metres (x along, y back from the building line,
    /// z up); the mesh writer turns them into Unity's. The pavement is at z 0, level with the plots;
    /// the carriageway and quay are a kerb lower.
    /// </summary>
    public static partial class StreetGround
    {
        public const float Road = -0.12f;   // the carriageway and quay surface, a kerb below the pavement
        const float KerbWidth = 0.25f;
        const int GutterRows = 3;
        const float GutterRow = 0.15f;
        const float BindWidth = 0.25f;
        const float CopingWidth = 0.5f, CopingRise = 0.03f, CopingDepth = 0.25f;
        const float WallSetBack = 0.05f;    // the coping overhangs the wall face by this much
        const float Joint = 0.035f;         // how far joints lie below the stone tops
        const float Beyond = 2500f;         // how far plain ground carries on past the street's ends, into the haze
        const float Chunk = 12f;            // metres of street per mesh, so meshes stay small and cull

        static readonly Vector3 Up = new Vector3(0, 0, 1);
        static readonly Vector3 Harbour = new Vector3(0, -1, 0);

        /// <summary>The height of the walkable surface at street y (for standing lamps and bollards on).</summary>
        public static float SurfaceZ(StreetLayout L, float y)
        {
            if (y >= L.BandNamed("pavement").y0)
                return 0f;
            if (y <= L.quay.edge + CopingWidth)
                return Road + CopingRise;
            return Road;
        }

        public struct Part
        {
            public string name;
            public Mesh mesh;
            public bool water;
        }

        /// <summary>The street's x extent and its chunk: stones belong to the chunk they start in.</summary>
        readonly struct Span
        {
            public readonly float x0, x1, a, b;
            public Span(float x0, float x1, float a, float b) { this.x0 = x0; this.x1 = x1; this.a = a; this.b = b; }
        }

        public static List<Part> Build(StreetLayout L)
        {
            var pal = new Palette(L.palette);
            var parts = new List<Part>();
            ulong seed = Hash.Of((ulong)L.worldSeed, L.street);
            var pave = L.BandNamed("pavement");
            var road = L.BandNamed("carriageway");
            var quay = L.BandNamed("quay");

            int n = Mathf.CeilToInt((L.x1 - L.x0) / Chunk - 1e-4f);
            for (int ci = 0; ci < n; ci++)
            {
                var s = new Span(L.x0, L.x1, L.x0 + ci * Chunk, Mathf.Min(L.x0 + (ci + 1) * Chunk, L.x1));
                var w = new MeshWriter(pal);
                Pavement(w, seed, pave, s);
                Carriageway(w, seed, road, s);
                QuaySurface(w, seed, quay, L.quay.edge, s);
                QuayWall(w, seed, L.quay.edge, L.water.level, s);
                if (L.HasSlope)
                    RetainingWalls(w, seed, L, s);
                parts.Add(new Part { name = $"ground {s.a:0}-{s.b:0} m", mesh = w.ToMesh($"ground_{ci:00}") });
            }

            var plain = new MeshWriter(pal);
            PlainEnds(plain, L, pave);
            if (L.HasSlope)
                Levels(plain, L);
            else
                Backland(plain, L);
            parts.Add(new Part { name = "ground beyond and behind", mesh = plain.ToMesh("ground_plain") });

            if (L.HasSlope)
            {
                var stairs = new MeshWriter(pal);
                foreach (var st in L.slope.stairs)
                    Stairs(stairs, seed, st);
                parts.Add(new Part { name = "stairs", mesh = stairs.ToMesh("stairs") });
                foreach (var r in L.slope.ridges)
                {
                    var rw = new MeshWriter(pal);
                    RidgeMesh(rw, seed, r);
                    parts.Add(new Part { name = r.name, mesh = rw.ToMesh(r.name) });
                }
            }

            var water = new MeshWriter(pal);
            float wy = L.quay.edge + WallSetBack, wz = L.water.level, far = 12000f;
            water.Quad(new Vector3(L.x0 - far, wy, wz), new Vector3(L.x1 + far, wy, wz),
                       new Vector3(L.x1 + far, wy - far, wz), new Vector3(L.x0 - far, wy - far, wz), "ground", Up);
            parts.Add(new Part { name = "harbour water", mesh = water.ToMesh("water"), water = true });
            return parts;
        }

        // -- the pavement: concrete flags, a granite kerb -----------------------------------------------------------

        static void Pavement(MeshWriter w, ulong seed, Band pave, Span s)
        {
            float kerbFront = pave.y0, kerbBack = pave.y0 + KerbWidth;
            // kerb stones along the street, their front face dropping past the carriageway's surface
            foreach (var p in Pieces(Hash.Of(seed, "kerb"), s, 0.9f, 1.5f, 0.008f))
                w.Stone(Frame.Ground, p.a, p.b, kerbFront, kerbBack - 0.006f, 0f, 0.015f, -Road + Joint, "kerb", "kerb", Tilt(p.h, 0.002f));

            // flags: 0.6 m squares from the building line out, the last row cut to fit against the kerb
            const float F = 0.6f, J = 0.007f;
            w.Quad(new Vector3(s.a, kerbBack, -0.02f), new Vector3(s.b, kerbBack, -0.02f), new Vector3(s.b, pave.y1, -0.02f), new Vector3(s.a, pave.y1, -0.02f), "joint", Up);
            ulong fs = Hash.Of(seed, "flags");
            int r = 0;
            for (float y1 = pave.y1; y1 > kerbBack + 0.05f; y1 -= F, r++)
            {
                float y0 = Mathf.Max(y1 - F, kerbBack);
                int k0 = s.a == s.x0 ? Mathf.FloorToInt(s.a / F) : Mathf.CeilToInt(s.a / F); // flags that start in this chunk
                for (int k = k0; k * F < s.b; k++)
                {
                    float fa = Mathf.Max(k * F, s.x0), fb = Mathf.Min((k + 1) * F - J, s.x1);
                    if (fb - fa < 0.02f)
                        continue;
                    ulong h = Hash.Of(fs, Hash.Key(k), Hash.Key(r));
                    w.Stone(Frame.Ground, fa, fb, y0 + J * 0.5f, y1 - J * 0.5f, Hash.Range(h, -0.003f, 0.003f), 0.004f, 0.02f, "flags", "flags", Tilt(h, 0.004f));
                }
            }
        }

        // -- the carriageway: granite setts in courses across the street, a gutter, binding stones ----------------

        static void Carriageway(MeshWriter w, ulong seed, Band road, Span s)
        {
            float yKerb = road.y1;                        // the kerb's foot
            float yGutter = yKerb - GutterRows * GutterRow;
            float yBind = road.y0 + BindWidth;
            w.Quad(new Vector3(s.a, road.y0, Road - Joint), new Vector3(s.b, road.y0, Road - Joint), new Vector3(s.b, yKerb, Road - Joint), new Vector3(s.a, yKerb, Road - Joint), "joint", Up);

            // the gutter: three rows of setts laid along the kerb, dished a centimetre to carry the water
            for (int r = 0; r < GutterRows; r++)
            {
                float y1 = yKerb - r * GutterRow, y0 = y1 - GutterRow;
                foreach (var p in Pieces(Hash.Of(Hash.Of(seed, "gutter"), (ulong)r), s, 0.19f, 0.26f, 0.014f))
                    Sett(w, p.h, p.a, p.b, y0 + 0.007f, y1 - 0.007f, Road - 0.01f + r * 0.003f);
            }

            // courses across the street: each a strip of constant x, its setts of varied length along y,
            // each course starting at its own offset so the joints break bond
            foreach (var c in Pieces(Hash.Of(seed, "courses"), s, 0.13f, 0.16f, 0.014f))
            {
                float y = yBind - Hash.Range(Hash.Of(c.h, 1), 0f, 0.24f);
                for (int k = 0; y < yGutter - 0.02f; k++)
                {
                    ulong sh = Hash.Of(c.h, Hash.Key(k));
                    float len = Hash.Range(sh, 0.19f, 0.26f);
                    float ya = Mathf.Max(y, yBind), yb = Mathf.Min(y + len - 0.014f, yGutter - 0.014f);
                    if (yb - ya > 0.05f)
                        Sett(w, sh, c.a, c.b, ya, yb, Road);
                    y += len;
                }
            }

            // binding stones: long granite blocks along the carriageway's edge, flush with the setts
            foreach (var p in Pieces(Hash.Of(seed, "bind"), s, 0.6f, 1.0f, 0.012f))
                w.Stone(Frame.Ground, p.a, p.b, road.y0 + 0.006f, yBind - 0.006f, Road, 0.015f, Joint, "kerb", "kerb", Tilt(p.h, 0.002f));
        }

        // -- the quay: setts in rows along the street, granite coping at the edge ----------------------------------

        static void QuaySurface(MeshWriter w, ulong seed, Band quay, float edge, Span s)
        {
            float yCope = edge + CopingWidth;
            w.Quad(new Vector3(s.a, yCope, Road - Joint), new Vector3(s.b, yCope, Road - Joint), new Vector3(s.b, quay.y1, Road - Joint), new Vector3(s.a, quay.y1, Road - Joint), "joint", Up);
            ulong qs = Hash.Of(seed, "quay");
            float y = quay.y1;
            for (int r = 0; y > yCope + 0.05f; r++)
            {
                float rh = Hash.Range(Hash.Of(qs, Hash.Key(r)), 0.14f, 0.16f);
                float y0 = Mathf.Max(y - rh, yCope);
                foreach (var p in Pieces(Hash.Of(qs, Hash.Key(r), 7), s, 0.19f, 0.27f, 0.014f))
                    Sett(w, p.h, p.a, p.b, y0 + 0.007f, y - 0.007f, Road);
                y -= rh;
            }
            // coping: long granite blocks, a little proud of the setts, their front face down to the wall
            foreach (var p in Pieces(Hash.Of(seed, "coping"), s, 1.0f, 1.8f, 0.01f))
                w.Stone(Frame.Ground, p.a, p.b, edge, yCope - 0.008f, Road + CopingRise + Hash.Range(Hash.Of(p.h, 9), -0.006f, 0.006f), 0.02f, CopingDepth,
                        "stone", "stone", Tilt(Hash.Of(p.h, 3), 0.003f));
        }

        // -- the quay wall: coursed granite down into the water -----------------------------------------------------

        static void QuayWall(MeshWriter w, ulong seed, float edge, float waterLevel, Span s)
        {
            float face = edge + WallSetBack;
            float top = Road + CopingRise - CopingDepth, bottom = waterLevel - 0.6f;
            var f = Frame.Wall(face);
            w.Quad(new Vector3(s.a, face, top), new Vector3(s.b, face, top), new Vector3(s.b, face, bottom), new Vector3(s.a, face, bottom), "joint", Harbour);
            ulong ws = Hash.Of(seed, "wall");
            float z = top;
            for (int c = 0; z > bottom; c++)
            {
                float z0 = z - Hash.Range(Hash.Of(ws, Hash.Key(c)), 0.40f, 0.48f);
                foreach (var p in Pieces(Hash.Of(ws, Hash.Key(c), 11), s, 0.8f, 1.6f, 0.015f))
                    w.Stone(f, p.a, p.b, z0 + 0.008f, z - 0.008f, Hash.Range(Hash.Of(p.h, 5), 0.0f, 0.03f), 0.025f, 0.06f, "quay_wall", "quay_wall", Vector2.zero);
                z = z0;
            }
        }

        // -- past the ends, and behind the plots --------------------------------------------------------------------

        static void PlainEnds(MeshWriter w, StreetLayout L, Band pave)
        {
            float edge = L.quay.edge, face = edge + WallSetBack;
            float top = Road + CopingRise - CopingDepth, bottom = L.water.level - 0.6f;
            foreach (var (a, b) in new[] { (L.x0 - Beyond, L.x0), (L.x1, L.x1 + Beyond) })
            {
                w.Quad(new Vector3(a, pave.y0, 0), new Vector3(b, pave.y0, 0), new Vector3(b, pave.y1, 0), new Vector3(a, pave.y1, 0), "flags", Up);
                w.Quad(new Vector3(a, pave.y0, 0), new Vector3(b, pave.y0, 0), new Vector3(b, pave.y0, Road), new Vector3(a, pave.y0, Road), "kerb", Harbour);
                w.Quad(new Vector3(a, edge + CopingWidth, Road), new Vector3(b, edge + CopingWidth, Road), new Vector3(b, pave.y0, Road), new Vector3(a, pave.y0, Road), "setts_mean", Up);
                w.Quad(new Vector3(a, edge, Road + CopingRise), new Vector3(b, edge, Road + CopingRise), new Vector3(b, edge + CopingWidth, Road + CopingRise), new Vector3(a, edge + CopingWidth, Road + CopingRise), "stone", Up);
                w.Quad(new Vector3(a, edge, Road + CopingRise), new Vector3(b, edge, Road + CopingRise), new Vector3(b, edge, top), new Vector3(a, edge, top), "stone", Harbour);
                w.Quad(new Vector3(a, face, top), new Vector3(b, face, top), new Vector3(b, face, bottom), new Vector3(a, face, bottom), "quay_wall", Harbour);
            }
        }

        static void Backland(MeshWriter w, StreetLayout L)
        {
            // the ground behind the plots follows the fixture's profile; without one it stays flat
            float a = L.x0 - Beyond, b = L.x1 + Beyond;
            var pr = L.backland.profile;
            if (pr == null || pr.Length < 2)
                pr = new[] { new YZ { y = 0f, z = 0f }, new YZ { y = Beyond, z = 0f } };
            string swatch = L.backland.surface == "ground" ? "grass" : L.backland.surface;
            for (int i = 0; i < pr.Length - 1; i++)
                w.Quad(new Vector3(a, pr[i].y, pr[i].z), new Vector3(b, pr[i].y, pr[i].z), new Vector3(b, pr[i + 1].y, pr[i + 1].z), new Vector3(a, pr[i + 1].y, pr[i + 1].z), swatch, Up);
        }

        // -- stones --------------------------------------------------------------------------------------------------

        readonly struct Piece
        {
            public readonly float a, b;
            public readonly ulong h;
            public Piece(float a, float b, ulong h) { this.a = a; this.b = b; this.h = h; }
        }

        /// <summary>
        /// A run of stones along x: lengths from lo to hi seeded by their index, walked from the street's
        /// start so every chunk agrees. Yields the stones that start in this chunk, each less its joint,
        /// clipped only at the street's ends.
        /// </summary>
        static IEnumerable<Piece> Pieces(ulong h, Span s, float lo, float hi, float joint)
        {
            float x = s.x0 - Hash.Range(Hash.Of(h, 0xA5), 0f, hi); // the run's own offset at the street's start
            for (ulong i = 0; x < s.b; i++)
            {
                ulong ph = Hash.Of(h, i);
                float len = Hash.Range(ph, lo, hi);
                if (x >= s.a || (s.a == s.x0 && x + len > s.x0))
                {
                    float a = Mathf.Max(x, s.x0), b = Mathf.Min(x + len - joint, s.x1);
                    if (b - a > 0.03f)
                        yield return new Piece(a, b, ph);
                }
                x += len;
            }
        }

        static readonly string[] SettTones = { "setts_light", "setts_mid", "setts_mid", "setts_dark" };

        static void Sett(MeshWriter w, ulong h, float xa, float xb, float ya, float yb, float top)
        {
            string tone = SettTones[Hash.Index(Hash.Of(h, 2), SettTones.Length)];
            w.Stone(Frame.Ground, xa, xb, ya, yb, top + Hash.Range(Hash.Of(h, 3), -0.003f, 0.003f), 0.024f, Joint, tone, tone, Tilt(Hash.Of(h, 4), 0.01f));
        }

        static Vector2 Tilt(ulong h, float slope) => new Vector2(Hash.Range(h, -slope, slope), Hash.Range(Hash.Of(h, 1), -slope, slope));

        // -- geometry ------------------------------------------------------------------------------------------------

        /// <summary>A plane to lay stones in: u and v span it, n points out of it (street axes).</summary>
        readonly struct Frame
        {
            readonly Vector3 o;
            public readonly Vector3 u, v, n;

            Frame(Vector3 o, Vector3 u, Vector3 v, Vector3 n) { this.o = o; this.u = u; this.v = v; this.n = n; }

            /// <summary>The ground: u along the street, v back from the building line, n up.</summary>
            public static readonly Frame Ground = new Frame(Vector3.zero, new Vector3(1, 0, 0), new Vector3(0, 1, 0), new Vector3(0, 0, 1));

            /// <summary>A wall facing the harbour at street y = face: u along the street, v up, n towards the water.</summary>
            public static Frame Wall(float face) => new Frame(new Vector3(0, face, 0), new Vector3(1, 0, 0), new Vector3(0, 0, 1), new Vector3(0, -1, 0));

            public Vector3 P(float a, float b, float c) => o + u * a + v * b + n * c;
        }

        sealed class MeshWriter
        {
            readonly Palette pal;
            readonly List<Vector3> verts = new List<Vector3>();
            readonly List<Vector3> normals = new List<Vector3>();
            readonly List<Vector2> uvs = new List<Vector2>();
            readonly List<Color> colours = new List<Color>();
            readonly List<int> tris = new List<int>();


            public MeshWriter(Palette pal) { this.pal = pal; }

            /// <summary>A flat quad in street coordinates, wound to face along the outward hint (street axes).</summary>
            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, string swatch, Vector3 outward)
            {
                Vector3 ua = StreetSpace.ToUnity(a), ub = StreetSpace.ToUnity(b), uc = StreetSpace.ToUnity(c), ud = StreetSpace.ToUnity(d);
                // Unity's front faces wind clockwise as seen from outside: cross(b - a, c - a) points out
                Vector3 nrm = Vector3.Cross(ub - ua, uc - ua);
                if (nrm.sqrMagnitude < 1e-14f)
                    nrm = Vector3.Cross(uc - ua, ud - ua);
                if (nrm.sqrMagnitude < 1e-14f)
                    return; // degenerate
                if (Vector3.Dot(nrm, StreetSpace.ToUnity(outward)) < 0)
                {
                    (ub, ud) = (ud, ub);
                    nrm = -nrm;
                }
                nrm.Normalize();
                Vector2 uv = pal.UV(swatch);
                int i = verts.Count;
                verts.Add(ua); verts.Add(ub); verts.Add(uc); verts.Add(ud);
                // what generated ground sees: open sky above it, open ground below; walls see half of each
                var seen = new Color(0.5f + 0.5f * nrm.y, 0.5f - 0.5f * nrm.y, 1f, 1f);
                for (int k = 0; k < 4; k++) { normals.Add(nrm); uvs.Add(uv); colours.Add(seen); }
                tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
                tris.Add(i); tris.Add(i + 2); tris.Add(i + 3);
            }

            /// <summary>
            /// A stone in frame f: its face spans a0..a1 by b0..b1 at height top along n, inset by bevel,
            /// and its bevelled sides run back by depth to its full size. tilt leans the face (rise per
            /// metre along u and v).
            /// </summary>
            public void Stone(Frame f, float a0, float a1, float b0, float b1, float top, float bevel, float depth, string face, string side, Vector2 tilt)
            {
                float ac = (a0 + a1) * 0.5f, bc = (b0 + b1) * 0.5f;
                float e = Mathf.Min(bevel, 0.45f * Mathf.Min(a1 - a0, b1 - b0));
                float T(float a, float b) => top + tilt.x * (a - ac) + tilt.y * (b - bc);
                Vector3 t00 = f.P(a0 + e, b0 + e, T(a0 + e, b0 + e)), t10 = f.P(a1 - e, b0 + e, T(a1 - e, b0 + e));
                Vector3 t11 = f.P(a1 - e, b1 - e, T(a1 - e, b1 - e)), t01 = f.P(a0 + e, b1 - e, T(a0 + e, b1 - e));
                float bottom = top - depth;
                Vector3 g00 = f.P(a0, b0, bottom), g10 = f.P(a1, b0, bottom), g11 = f.P(a1, b1, bottom), g01 = f.P(a0, b1, bottom);
                Quad(t00, t10, t11, t01, face, f.n);
                Quad(g00, g10, t10, t00, side, -f.v);
                Quad(g10, g11, t11, t10, side, f.u);
                Quad(g11, g01, t01, t11, side, f.v);
                Quad(g01, g00, t00, t01, side, -f.u);
            }

            public Mesh ToMesh(string name)
            {
                var m = new Mesh { name = name, hideFlags = HideFlags.DontSave };
                m.indexFormat = verts.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16;
                m.SetVertices(verts);
                m.SetNormals(normals);
                m.SetUVs(0, uvs);
                m.SetColors(colours);
                m.SetTriangles(tris, 0, true);
                return m;
            }
        }
    }
}
