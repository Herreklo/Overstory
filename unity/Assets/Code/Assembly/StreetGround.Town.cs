using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Overstory.Core;
using Overstory.World;

namespace Overstory.Assembly
{
    /// <summary>
    /// The grown town's ground and stonework (blender/tools/grow_town.py): the hill as a height field
    /// (fine over the town, coarse over the land around it), lanes, the square, stepped lanes and garden
    /// steps, garden and retaining walls, and each house's stone basement. Where everything is comes
    /// from the town fixture, resolved by the export; how each stone sits is seeded texture.
    /// </summary>
    public static partial class StreetGround
    {
        static void TownParts(List<Part> parts, Palette pal, ulong seed, StreetLayout L)
        {
            var t = L.town;
            parts.Add(new Part { name = "the hill, close", mesh = TerrainMesh(pal, t.fine, null, "town ground", L.quay.edge) });
            parts.Add(new Part { name = "the hill, around", mesh = TerrainMesh(pal, t.coarse, t.fine, "land", L.quay.edge) });

            var w = new MeshWriter(pal);
            foreach (var lane in t.lanes)
                Ribbon(w, lane.points, lane.width, LaneSwatch(lane.surface), 0.04f);
            foreach (var sq in t.squares)
                w.Quad(Lift(sq.corners[0], 0.04f), Lift(sq.corners[1], 0.04f), Lift(sq.corners[2], 0.04f), Lift(sq.corners[3], 0.04f), LaneSwatch(sq.surface), Up);
            parts.Add(new Part { name = "lanes and square", mesh = w.ToMesh("lanes") });

            var stone = new MeshWriter(pal);
            ulong ss = Hash.Of(seed, "town stone");
            foreach (var st in t.stairs)
                StepsAlong(stone, Hash.Of(ss, st.name), st.points, st.width);
            int k = 0;
            foreach (var st in t.steps)
                StepsAlong(stone, Hash.Of(ss, (ulong)k++), st.points, st.width);
            parts.Add(new Part { name = "stepped lanes and steps", mesh = stone.ToMesh("steps") });

            var walls = new MeshWriter(pal);
            k = 0;
            foreach (var wall in t.walls)
                WallAlong(walls, Hash.Of(Hash.Of(ss, "wall"), (ulong)k++), wall);
            foreach (var f in t.foundations)
                Basement(walls, Hash.Of(Hash.Of(ss, "basement"), (ulong)f.id), f);
            parts.Add(new Part { name = "walls and basements", mesh = walls.ToMesh("walls") });
        }

        static string LaneSwatch(string surface) => surface switch
        {
            "asphalt" => "asphalt",
            "gravel" => "gravel",
            "setts" => "setts_mean",
            _ => "flags",
        };

        static Vector3 Lift(P3 p, float dz) => new Vector3(p.x, p.y, p.z + dz);

        // -- the ground -------------------------------------------------------------------------------------

        /// <summary>
        /// A height field as a mesh: smooth normals from the grid, one swatch per triangle (grass low,
        /// heath higher, rock where it is steep), each triangle its own vertices so swatches never blend.
        /// With a hole, the cells the finer grid covers are left out and the border is skirted down.
        /// </summary>
        static Mesh TerrainMesh(Palette pal, HeightGrid g, HeightGrid hole, string name, float shore)
        {
            var verts = new List<Vector3>();
            var normals = new List<Vector3>();
            var uvs = new List<Vector2>();
            var colours = new List<Color>();
            var tris = new List<int>();
            Vector2 grass = pal.UV("grass"), heath = pal.UV("heath"), rock = pal.UV("rock"), bed = pal.UV("ground");

            Vector3 P(int i, int j) => StreetSpace.ToUnity(g.x0 + i * g.step, g.y0 + j * g.step, g.At(i, j));
            Vector3 N(int i, int j)
            {
                float dx = (g.At(i + 1, j) - g.At(i - 1, j)) / (2 * g.step);
                float dy = (g.At(i, j + 1) - g.At(i, j - 1)) / (2 * g.step);
                return new Vector3(-dx, 1f, -dy).normalized; // street (-dz/dx, -dz/dy, 1) in Unity's axes
            }
            bool Covered(float x, float y) => hole != null
                && x > hole.x0 + hole.step && x < hole.x0 + (hole.nx - 2) * hole.step
                && y > hole.y0 + hole.step && y < hole.y0 + (hole.ny - 2) * hole.step;

            void Tri(int ia, int ja, int ib, int jb, int ic, int jc)
            {
                Vector3 a = P(ia, ja), b = P(ib, jb), c = P(ic, jc);
                float z = (a.y + b.y + c.y) / 3f;
                Vector3 fn = Vector3.Cross(b - a, c - a).normalized;
                // bare rock only on crags; heath above the town; grass within it
                Vector2 uv = z < -1.2f ? bed : (fn.y < 0.42f ? rock : (z > 55f ? heath : grass));
                int n0 = verts.Count;
                foreach (var (p, nn) in new[] { (a, N(ia, ja)), (b, N(ib, jb)), (c, N(ic, jc)) })
                {
                    verts.Add(p);
                    normals.Add(nn);
                    uvs.Add(uv);
                    colours.Add(new Color(0.5f + 0.5f * nn.y, 0.5f - 0.5f * nn.y, 1f, 1f));
                }
                tris.Add(n0); tris.Add(n0 + 1); tris.Add(n0 + 2);
            }

            for (int j = 0; j < g.ny - 1; j++)
                for (int i = 0; i < g.nx - 1; i++)
                {
                    float x = g.x0 + (i + 0.5f) * g.step, y = g.y0 + (j + 0.5f) * g.step;
                    if (Covered(x, y))
                        continue;
                    Tri(i, j, i, j + 1, i + 1, j);
                    Tri(i + 1, j, i, j + 1, i + 1, j + 1);
                }

            if (hole == null)
            {
                // a skirt round the fine grid, down into the coarse land, so no seam shows between them
                void Skirt(int i0, int j0, int i1, int j1, Vector3 outward)
                {
                    Vector3 a = P(i0, j0), b = P(i1, j1);
                    Vector3 c = b + Vector3.down * 6f, d = a + Vector3.down * 6f;
                    int n0 = verts.Count;
                    foreach (var p in new[] { a, b, c, d })
                    {
                        verts.Add(p);
                        normals.Add(Vector3.up);
                        uvs.Add(grass);
                        colours.Add(new Color(0.5f, 0.5f, 1f, 1f));
                    }
                    Vector3 fn = Vector3.Cross(b - a, c - a);
                    if (Vector3.Dot(fn, outward) < 0) { tris.Add(n0); tris.Add(n0 + 2); tris.Add(n0 + 1); tris.Add(n0); tris.Add(n0 + 3); tris.Add(n0 + 2); }
                    else { tris.Add(n0); tris.Add(n0 + 1); tris.Add(n0 + 2); tris.Add(n0); tris.Add(n0 + 2); tris.Add(n0 + 3); }
                }
                for (int i = 0; i < g.nx - 1; i++)
                {
                    Skirt(i, 0, i + 1, 0, Vector3.back);
                    Skirt(i, g.ny - 1, i + 1, g.ny - 1, Vector3.forward);
                }
                for (int j = 0; j < g.ny - 1; j++)
                {
                    Skirt(0, j, 0, j + 1, Vector3.left);
                    Skirt(g.nx - 1, j, g.nx - 1, j + 1, Vector3.right);
                }
            }

            var m = new Mesh { name = name, hideFlags = HideFlags.DontSave, indexFormat = IndexFormat.UInt32 };
            m.SetVertices(verts);
            m.SetNormals(normals);
            m.SetUVs(0, uvs);
            m.SetColors(colours);
            m.SetTriangles(tris, 0, true);
            return m;
        }

        // -- lanes ------------------------------------------------------------------------------------------

        /// <summary>A strip of surface along a polyline, its corners mitred where it bends.</summary>
        static void Ribbon(MeshWriter w, P3[] pts, float width, string swatch, float lift)
        {
            int n = pts.Length;
            var left = new Vector3[n];
            var right = new Vector3[n];
            for (int k = 0; k < n; k++)
            {
                Vector2 a = new Vector2(pts[Mathf.Max(k - 1, 0)].x, pts[Mathf.Max(k - 1, 0)].y);
                Vector2 b = new Vector2(pts[Mathf.Min(k + 1, n - 1)].x, pts[Mathf.Min(k + 1, n - 1)].y);
                Vector2 d = (b - a).normalized;
                Vector2 side = new Vector2(-d.y, d.x) * (width * 0.5f);
                var c = new Vector3(pts[k].x, pts[k].y, pts[k].z + lift);
                left[k] = c + new Vector3(side.x, side.y, 0);
                right[k] = c - new Vector3(side.x, side.y, 0);
            }
            for (int k = 0; k < n - 1; k++)
                w.Quad(right[k], right[k + 1], left[k + 1], left[k], swatch, Up);
        }

        // -- steps ------------------------------------------------------------------------------------------

        /// <summary>
        /// Stone steps along a path: where it climbs, steps of equal rise (about 17 cm) in granite; where
        /// it runs level, flags.
        /// </summary>
        static void StepsAlong(MeshWriter w, ulong h, P3[] pts, float width)
        {
            for (int k = 0; k < pts.Length - 1; k++)
            {
                P3 p = pts[k], q = pts[k + 1];
                var d = new Vector3(q.x - p.x, q.y - p.y, 0f);
                float run = d.magnitude;
                if (run < 0.05f)
                    continue;
                d /= run;
                var side = new Vector3(-d.y, d.x, 0f);
                var f = Frame.Of(new Vector3(p.x, p.y, 0f), side, d, Up);
                float dz = q.z - p.z, hw = width * 0.5f;
                if (Mathf.Abs(dz) < 0.05f)
                {
                    w.Stone(f, -hw, hw, 0f, run, p.z + 0.05f, 0.01f, 0.2f, "flags", "flags", Vector2.zero);
                    continue;
                }
                int n = Mathf.Max(1, Mathf.CeilToInt(Mathf.Abs(dz) / 0.17f));
                float tread = run / n, rise = dz / n;
                for (int i = 0; i < n; i++)
                {
                    float top = p.z + rise * (dz > 0 ? i + 1 : i) + 0.03f;
                    ulong sh = Hash.Of(h, (ulong)(k * 1000 + i));
                    w.Stone(f, -hw, hw, i * tread - 0.02f, (i + 1) * tread, top + Hash.Range(sh, -0.004f, 0.004f), 0.015f, Mathf.Abs(rise) + 0.25f, "stone", "stone", Tilt(sh, 0.003f));
                }
            }
        }

        // -- walls ------------------------------------------------------------------------------------------

        const float WallThick = 0.42f;

        /// <summary>A dry-stone wall along a line, coursed on both faces, capped with long stones.</summary>
        static void WallAlong(MeshWriter w, ulong h, Wall wall)
        {
            var pts = wall.points;
            for (int k = 0; k < pts.Length - 1; k++)
            {
                var a = new Vector3(pts[k].x, pts[k].y, 0f);
                var b = new Vector3(pts[k + 1].x, pts[k + 1].y, 0f);
                float len = (b - a).magnitude;
                if (len < 0.05f)
                    continue;
                var u = (b - a) / len;
                var n = new Vector3(u.y, -u.x, 0f);
                float zb = Mathf.Min(pts[k].zb, pts[k + 1].zb), zt = (pts[k].zt + pts[k + 1].zt) * 0.5f;
                if (zt - zb < 0.15f)
                    continue;
                StoneFace(w, Hash.Of(h, (ulong)k), Frame.Of(a + n * (WallThick * 0.5f), u, Up, n), 0f, len, zb, zt);
                StoneFace(w, Hash.Of(h, (ulong)k, 1), Frame.Of(b - n * (WallThick * 0.5f), -u, Up, -n), 0f, len, zb, zt);
                // the cap
                var cap = Frame.Of(a, u, n, Up);
                foreach (var p in Pieces(Hash.Of(h, (ulong)k, 2), new Span(0f, len, 0f, len), 0.5f, 1.1f, 0.02f))
                    w.Stone(cap, p.a, p.b, -WallThick * 0.55f, WallThick * 0.55f, zt + 0.06f + Hash.Range(p.h, -0.01f, 0.01f), 0.02f, 0.14f, "drystone", "drystone", Tilt(p.h, 0.01f));
            }
        }

        /// <summary>A house's stone basement: its four sides coursed, from the floor down into the ground.</summary>
        static void Basement(MeshWriter w, ulong h, Foundation f)
        {
            if (f.top - f.bottom < 0.1f)
                return;
            var c = f.corners;
            var centre = new Vector3((c[0].x + c[1].x + c[2].x + c[3].x) / 4f, (c[0].y + c[1].y + c[2].y + c[3].y) / 4f, 0f);
            for (int k = 0; k < 4; k++)
            {
                var a = new Vector3(c[k].x, c[k].y, 0f);
                var b = new Vector3(c[(k + 1) % 4].x, c[(k + 1) % 4].y, 0f);
                float len = (b - a).magnitude;
                var u = (b - a) / len;
                var n = new Vector3(u.y, -u.x, 0f);
                if (Vector3.Dot(n, (a + b) * 0.5f - centre) < 0f)
                {
                    (a, b) = (b, a);
                    u = -u;
                    n = new Vector3(u.y, -u.x, 0f);
                }
                StoneFace(w, Hash.Of(h, (ulong)k), Frame.Of(a + n * 0.06f, u, Up, n), -0.06f, len + 0.06f, f.bottom, f.top - 0.02f);
            }
        }

        /// <summary>Coursed stones over a face: in a frame whose u runs along it, v up and n out of it.</summary>
        static void StoneFace(MeshWriter w, ulong h, Frame f, float a0, float a1, float zb, float zt)
        {
            w.Quad(f.P(a0, zb, -0.03f), f.P(a1, zb, -0.03f), f.P(a1, zt, -0.03f), f.P(a0, zt, -0.03f), "joint", f.n);
            float z = zt;
            for (int c = 0; z > zb + 0.04f; c++)
            {
                float z0 = Mathf.Max(z - Hash.Range(Hash.Of(h, (ulong)c), 0.24f, 0.38f), zb);
                foreach (var p in Pieces(Hash.Of(h, (ulong)c, 3), new Span(a0, a1, a0, a1), 0.35f, 0.85f, 0.025f))
                    w.Stone(f, p.a, p.b, z0 + 0.012f, z - 0.012f, Hash.Range(Hash.Of(p.h, 5), 0.0f, 0.03f), 0.03f, 0.08f, "drystone", "drystone", Vector2.zero);
                z = z0;
            }
        }
    }
}
