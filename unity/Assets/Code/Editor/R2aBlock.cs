using System.Collections.Generic;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// R2a's test block (r2a/stones/plan.md, the order: the patch array, the arm and the lit line proved on a block made
    /// here before the stones arrive): a squared slate block with every one of the contract's channels (the vertex layout
    /// table), at L0 with its exposed arrises truly chamfered and at L1 a plain box whose same arrises are masked for the
    /// lit line. It is a harness fixture, not a part: its sizes, face slices, offsets and chamfer are the harness's,
    /// chosen to put a split face, a bed face and both kinds of arris (horizontal and upright) before the camera, and
    /// it claims nothing about the town.
    ///
    /// In Unity's order (x along the face, y up, z away from the viewer), standing on y = 0, its front face at z = -depth/2
    /// facing -z. Its exposed arrises are the top's four and the four uprights; the four at its foot lie on the ground and
    /// are neither chamfered nor masked.
    /// </summary>
    public static class R2aBlock
    {
        /// <summary>One face: its outline (a convex polygon, either way round), which of its sides are exposed arrises,
        /// its kind (UV2 x), its patch slice, and its UV0 frame (u and v axes in its plane, and a patch offset).</summary>
        struct Face
        {
            public Vector3[] outline;
            public bool[] arris;          // side i runs from outline[i] to outline[i + 1]
            public int kind, slice;
            public Vector3 u, v;
            public Vector2 offset;
        }

        public struct Spec
        {
            public float length, height, depth;   // metres
            public int chamferMm;                  // L0's leg along each face, and L1's code
            public float seed;                     // UV1 y
            public float years;                    // since it was split
        }

        // (the harness's block: about a wall stone's size, its split faces' u along the bedding, its offsets fixed)
        public static readonly Spec Default = new Spec { length = 0.62f, height = 0.26f, depth = 0.34f, chamferMm = 11, seed = 0.5f, years = 115f };

        const int KindChamfer = 1, KindSplit = 2, KindBed = 3, SliceNone = 7;

        /// <summary>The block at L0 (chamfered, mask 0 everywhere) or L1 (a plain box, the arrises masked).</summary>
        public static Mesh Build(Spec s, bool l0)
        {
            var faces = l0 ? Chamfered(s) : Plain(s);
            var b = new Builder();
            foreach (var f in faces)
                b.Add(f, s, l0);
            return b.Mesh(l0 ? "r2a block L0" : "r2a block L1");
        }

        // The sides in turn round the block, seen from above: front (-z), right (+x), back (+z), left (-x); each with its
        // outward direction o, its along direction t (to the right seen from outside), its half length along t and half
        // depth along o, and its slice
        static IEnumerable<(Vector3 o, Vector3 t, float L, float D, int slice, Vector2 offset)> Sides(Spec s)
        {
            float a = s.length / 2f, c = s.depth / 2f;
            yield return (Vector3.back, Vector3.right, a, c, 0, new Vector2(0.137f, 0.412f));
            yield return (Vector3.right, Vector3.forward, c, a, 1, new Vector2(0.583f, 0.091f));
            yield return (Vector3.forward, Vector3.left, a, c, 3, new Vector2(0.266f, 0.705f));
            yield return (Vector3.left, Vector3.back, c, a, 2, new Vector2(0.811f, 0.334f));
        }

        static List<Face> Plain(Spec s)
        {
            var faces = new List<Face>();
            float a = s.length / 2f, c = s.depth / 2f, h = s.height;
            foreach (var (o, t, L, D, slice, off) in Sides(s))
            {
                Vector3 P(float along, float y) => t * along + o * D + Vector3.up * y;
                faces.Add(new Face
                {
                    outline = new[] { P(-L, 0), P(L, 0), P(L, h), P(-L, h) },
                    arris = new[] { false, true, true, true },     // the foot on the ground; the upright, the top, the upright
                    kind = KindSplit, slice = slice, u = t, v = Vector3.up, offset = off,
                });
            }
            faces.Add(Top(a, c, h, 0f));
            faces.Add(Bottom(new[] { new Vector3(-a, 0, -c), new Vector3(-a, 0, c), new Vector3(a, 0, c), new Vector3(a, 0, -c) }));
            return faces;
        }

        static List<Face> Chamfered(Spec s)
        {
            var faces = new List<Face>();
            float a = s.length / 2f, c = s.depth / 2f, h = s.height, w = s.chamferMm / 1000f;
            var bottom = new List<Vector3>();
            foreach (var (o, t, L, D, slice, off) in Sides(s))
            {
                Vector3 P(float along, float depth, float y) => t * along + o * depth + Vector3.up * y;
                // the side's face, short of the chamfers at its uprights and its top
                faces.Add(new Face
                {
                    outline = new[] { P(-L + w, D, 0), P(L - w, D, 0), P(L - w, D, h - w), P(-L + w, D, h - w) },
                    arris = new bool[4], kind = KindSplit, slice = slice, u = t, v = Vector3.up, offset = off,
                });
                // its top arris's chamfer, its ends mitred to a point where it meets the uprights' and the next top's
                Vector3 across = (Vector3.up - o).normalized;
                faces.Add(new Face
                {
                    outline = new[] { P(-L + w, D, h - w), P(L - w, D, h - w), P(L - w / 2, D - w / 2, h - w / 2),
                                      P(L - w, D - w, h), P(-L + w, D - w, h), P(-L + w / 2, D - w / 2, h - w / 2) },
                    arris = new bool[6], kind = KindChamfer, slice = SliceNone, u = t, v = across, offset = Vector2.zero,
                });
                // the upright chamfer at its right-hand end, up to the mitre's point
                Vector3 diag = (t - o).normalized;
                faces.Add(new Face
                {
                    outline = new[] { P(L - w, D, 0), P(L, D - w, 0), P(L, D - w, h - w), P(L - w / 2, D - w / 2, h - w / 2), P(L - w, D, h - w) },
                    arris = new bool[5], kind = KindChamfer, slice = SliceNone, u = diag, v = Vector3.up, offset = Vector2.zero,
                });
                bottom.Add(P(-L + w, D, 0));
                bottom.Add(P(L - w, D, 0));
            }
            faces.Add(Top(a - w, c - w, h, w));
            faces.Add(Bottom(bottom.ToArray()));
            return faces;
        }

        static Face Top(float a, float c, float h, float inset) => new Face
        {
            outline = new[] { new Vector3(-a, h, -c), new Vector3(-a, h, c), new Vector3(a, h, c), new Vector3(a, h, -c) },
            arris = inset > 0f ? new bool[4] : new[] { true, true, true, true },
            kind = KindBed, slice = 4, u = Vector3.right, v = Vector3.forward, offset = new Vector2(0.452f, 0.618f),
        };

        static Face Bottom(Vector3[] outline) => new Face
        {
            outline = outline, arris = new bool[outline.Length],
            kind = KindBed, slice = 5, u = Vector3.right, v = Vector3.back, offset = new Vector2(0.209f, 0.873f),
        };

        class Builder
        {
            readonly List<Vector3> pos = new List<Vector3>(), nor = new List<Vector3>();
            readonly List<Vector2>[] uv = new List<Vector2>[8];
            readonly List<int> tris = new List<int>();

            public Builder()
            {
                for (int i = 0; i < 8; i++)
                    uv[i] = new List<Vector2>();
            }

            public void Add(Face f, Spec s, bool l0)
            {
                var p = f.outline;
                // the face's normal from its outline (Newell's), turned outward (away from the block's middle: it is
                // convex), and each triangle wound for Unity (Cross(b - a, c - a) along the outward normal, as Unity's
                // own quad is)
                Vector3 n = Vector3.zero, mid = Vector3.zero;
                for (int i = 0; i < p.Length; i++)
                {
                    Vector3 cur = p[i], nxt = p[(i + 1) % p.Length];
                    n += new Vector3((cur.y - nxt.y) * (cur.z + nxt.z), (cur.z - nxt.z) * (cur.x + nxt.x), (cur.x - nxt.x) * (cur.y + nxt.y));
                    mid += cur / p.Length;
                }
                n.Normalize();
                if (Vector3.Dot(n, mid - new Vector3(0f, s.height / 2f, 0f)) < 0f)
                    n = -n;
                for (int i = 1; i + 1 < p.Length; i++)
                {
                    // the fan (0, i, i + 1): which of its sides are the outline's arrises (the fan's inner sides never are)
                    bool sideA = i == 1 && f.arris[0];                 // p0 to pi
                    bool sideB = f.arris[i];                           // pi to pi+1
                    bool sideC = i + 1 == p.Length - 1 && f.arris[p.Length - 1];   // pi+1 to p0
                    Vector3 a = p[0], b = p[i], c = p[i + 1];
                    // (the edge opposite corner 0 is b-c, opposite 1 is c-a, opposite 2 is a-b)
                    int mask = (sideB ? 1 : 0) | (sideC ? 2 : 0) | (sideA ? 4 : 0);
                    bool flip = Vector3.Dot(Vector3.Cross(b - a, c - a), n) < 0f;
                    if (flip)
                    {
                        (b, c) = (c, b);
                        mask = (mask & 1) | ((mask & 2) << 1) | ((mask & 4) >> 1);
                    }
                    float area2 = Vector3.Cross(b - a, c - a).magnitude;
                    float h0 = area2 / (c - b).magnitude, h1 = area2 / (a - c).magnitude, h2 = area2 / (b - a).magnitude;
                    int code = f.slice + 8 * (l0 ? 0 : mask) + 64 * s.chamferMm;
                    Vertex(a, n, f, s, new Vector3(h0, 0, 0), code);
                    Vertex(b, n, f, s, new Vector3(0, h1, 0), code);
                    Vertex(c, n, f, s, new Vector3(0, 0, h2), code);
                }
            }

            void Vertex(Vector3 p, Vector3 n, Face f, Spec s, Vector3 d, int code)
            {
                tris.Add(pos.Count);
                pos.Add(p);
                nor.Add(n);
                uv[0].Add(new Vector2(Vector3.Dot(p, f.u), Vector3.Dot(p, f.v)) + f.offset);   // metres in its plane
                uv[1].Add(new Vector2(s.years / 200f, s.seed));
                uv[2].Add(new Vector2(f.kind, 0f));                     // the face; water layer 0
                uv[3].Add(new Vector2(0.5f + 0.5f * n.y, 1f));          // the loose stone's bake: sky from the normal
                uv[4].Add(Vector2.zero);                                // polish 0, lichen 0
                uv[5].Add(Vector2.zero);                                // moss 0, water held 0
                uv[6].Add(new Vector2(d.x, d.y));
                uv[7].Add(new Vector2(d.z, code));
            }

            public Mesh Mesh(string name)
            {
                var m = new Mesh { name = name, hideFlags = HideFlags.DontSave };
                m.SetVertices(pos);
                m.SetNormals(nor);
                for (int i = 0; i < 8; i++)
                    m.SetUVs(i, uv[i]);
                m.SetTriangles(tris, 0);
                m.RecalculateBounds();
                return m;
            }
        }
    }
}
