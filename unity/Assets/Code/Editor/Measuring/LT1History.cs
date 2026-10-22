using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Unity.Collections;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Core;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The history quad (step 3, R2; docs/research/history-pages.md): three synthetic 1024 by 512 pages (P0, P1, H1) and a
    /// 4,096-entry piece table, read by a full-screen grid of 4,096 pieces through the real include
    /// (Shaders/History.hlsl), so the include's cost is timed on the harness (LT1Perf's quad scenes) before any real
    /// shader is ported. The pages are made here, RGBA8 and then BC7 through EditorUtility.CompressTexture, seeded
    /// (Core/Hash.cs), into Assets/Experiments/LT1/History/Generated/ (out of git: their hashes are reported instead).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1History.Pages
    ///         [-out reviews/lt1/history] [-frames /abs/scratch/dir]
    ///
    /// Pages rebuilds them and answers R0's open questions on this machine's Metal: whether CompressTexture keeps the
    /// mips it is given, BC7's error on these pages (per channel, so a perceptual weighting shows), and whether the GPU
    /// copies a Texture2D into an array slice (Graphics.CopyTexture; checked by drawing the quad from a copied array
    /// against one filled on the CPU). It saves the history-quad scene (LT1_HistoryQuad.unity, generated) and writes
    /// &lt;out&gt;/r2-pages.json.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1History.QuietMeans
    ///
    /// prints the gully's per-material means of the quantities history off holds (LT1Stone sets them on the materials).
    /// </summary>
    public static class LT1History
    {
        const string Dir = "Assets/Experiments/LT1/History";
        const string Generated = Dir + "/Generated";
        const string ScenePath = Generated + "/LT1_HistoryQuad.unity";
        const string QuadShader = "Hidden/Overstory/HistoryQuad";

        /// <summary>A page's size, the shared pages (P0, P1, H1), its mips (history-pages.md, 4: three suffice).</summary>
        public const int W = 1024, H = 512, Slices = 3, Mips = 3;

        /// <summary>The grid: 64 by 64 pieces, each a 16 by 8 texel rectangle on the 4-texel grid, 2 texels of padding.</summary>
        public const int Grid = 64, Pieces = Grid * Grid, CellW = W / Grid, CellH = H / Grid, Pad = 2;

        static readonly string[] SliceNames = { "p0", "p1", "h1" };

        // ------------------------------------------------------------------------------------------------ the pages

        /// <summary>A slice's texels at every mip: per piece a value, a gradient across its chart and fine noise, over a
        /// smooth field across the page, each channel its own (uncorrelated, as history-pages.md's test pages).</summary>
        static Color32[][] Content(int slice)
        {
            var mips = new Color32[Mips][];
            var m0 = new Color32[W * H];
            const int L = 32;     // the smooth field's lattice, in texels
            int lw = W / L + 2, lh = H / L + 2;
            var lattice = new float[4][];
            for (int c = 0; c < 4; c++)
            {
                lattice[c] = new float[lw * lh];
                for (int j = 0; j < lh; j++)
                    for (int i = 0; i < lw; i++)
                        lattice[c][j * lw + i] = (float)Hash.Unit(Hash.Of((ulong)(slice * 4 + c), "field", (ulong)(j * lw + i)));
            }
            var piece = new float[Pieces * 8];
            for (int p = 0; p < Pieces; p++)
                for (int c = 0; c < 4; c++)
                {
                    ulong k = Hash.Of((ulong)p, "page", (ulong)(slice * 4 + c));
                    piece[p * 8 + c] = (float)Hash.Unit(k);
                    piece[p * 8 + 4 + c] = (float)Hash.Unit(Hash.Then(k, "slope")) * 2f - 1f;
                }
            for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                {
                    int p = (y / CellH) * Grid + x / CellW;
                    float gx = (x % CellW + 0.5f) / CellW - 0.5f, gy = (y % CellH + 0.5f) / CellH - 0.5f;
                    float fx = x / (float)L, fy = y / (float)L;
                    int ix = (int)fx, iy = (int)fy;
                    float tx = fx - ix, ty = fy - iy;
                    tx = tx * tx * (3f - 2f * tx);
                    ty = ty * ty * (3f - 2f * ty);
                    var px = new byte[4];
                    for (int c = 0; c < 4; c++)
                    {
                        var lc = lattice[c];
                        float field = Mathf.Lerp(Mathf.Lerp(lc[iy * lw + ix], lc[iy * lw + ix + 1], tx),
                                                 Mathf.Lerp(lc[(iy + 1) * lw + ix], lc[(iy + 1) * lw + ix + 1], tx), ty);
                        float noise = (float)Hash.Unit(Hash.Of((ulong)(y * W + x), "grain", (ulong)(slice * 4 + c))) - 0.5f;
                        float v = 0.1f + 0.55f * piece[p * 8 + c] + 0.25f * piece[p * 8 + 4 + c] * (c % 2 == 0 ? gx : gy)
                                  + 0.2f * (field - 0.5f) + 0.04f * noise;
                        px[c] = (byte)Mathf.Clamp(Mathf.RoundToInt(v * 255f), 0, 255);
                    }
                    m0[y * W + x] = new Color32(px[0], px[1], px[2], px[3]);
                }
            mips[0] = m0;
            for (int m = 1; m < Mips; m++)
                mips[m] = Box(mips[m - 1], W >> (m - 1), H >> (m - 1));
            return mips;
        }

        /// <summary>A mip from the one above: each texel the rounded mean of its four (the charts sit on the 4-texel grid,
        /// so to mip 2 no texel straddles two charts: the box is chart-aware here).</summary>
        static Color32[] Box(Color32[] src, int w, int h)
        {
            int w2 = w / 2, h2 = h / 2;
            var dst = new Color32[w2 * h2];
            for (int y = 0; y < h2; y++)
                for (int x = 0; x < w2; x++)
                {
                    Color32 a = src[2 * y * w + 2 * x], b = src[2 * y * w + 2 * x + 1], c = src[(2 * y + 1) * w + 2 * x], d = src[(2 * y + 1) * w + 2 * x + 1];
                    dst[y * w2 + x] = new Color32((byte)((a.r + b.r + c.r + d.r + 2) / 4), (byte)((a.g + b.g + c.g + d.g + 2) / 4),
                                                  (byte)((a.b + b.b + c.b + d.b + 2) / 4), (byte)((a.a + b.a + c.a + d.a + 2) / 4));
                }
            return dst;
        }

        /// <summary>A linear RGBA32 texture holding the given mips, as they are (no mip of Unity's own).</summary>
        static Texture2D Texture(Color32[][] mips, int w, int h, string name)
        {
            // (kept through a scene change: Pages opens its scene after making them)
            var t = new Texture2D(w, h, TextureFormat.RGBA32, mips.Length, true) { name = name, hideFlags = HideFlags.DontSave };
            for (int m = 0; m < mips.Length; m++)
                t.SetPixels32(mips[m], m);
            t.Apply(false);
            return t;
        }

        /// <summary>The piece table: one group (slice 0), each piece two pairs of resets and an age on the year × 16 + month
        /// grid from the pack's first year (history-pages.md, 3), seeded.</summary>
        internal static uint[] PieceTable()
        {
            var t = new uint[Pieces * 4];
            for (int p = 0; p < Pieces; p++)
            {
                ulong k = Hash.Of((ulong)p, "piece");
                uint Date(string what, int years) => (uint)(Hash.Index(Hash.Then(k, what), years) * 16 + 1 + Hash.Index(Hash.Then(k, what + "-month"), 12));
                t[p * 4] = 0;
                t[p * 4 + 1] = Date("placed", 140) | (Date("bare", 140) << 16);
                t[p * 4 + 2] = Date("bed", 140) | (Date("lifted", 140) << 16);
                t[p * 4 + 3] = (uint)(Hash.Index(Hash.Then(k, "age"), 41) * 16);
            }
            return t;
        }

        static Texture2DArray NewArray(TextureFormat format, string name) => new Texture2DArray(W, H, Slices, format, Mips, true)
        {
            name = name, filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp, anisoLevel = 0,
        };

        /// <summary>An array filled on the CPU from the slices' own data, mip by mip.</summary>
        static Texture2DArray Fill(Texture2D[] slices, string name)
        {
            var a = NewArray(slices[0].format, name);
            for (int s = 0; s < Slices; s++)
                for (int m = 0; m < Mips; m++)
                    a.SetPixelData(slices[s].GetPixelData<byte>(m), m, s);
            a.Apply(false, false);
            return a;
        }

        /// <summary>An array whose slices the GPU copies from the textures (Graphics.CopyTexture); not readable, so what is
        /// drawn from it is the GPU's copy and never CPU data.</summary>
        static Texture2DArray Copy(Texture2D[] slices, string name)
        {
            var a = NewArray(slices[0].format, name);
            a.Apply(false, true);
            for (int s = 0; s < Slices; s++)
                for (int m = 0; m < Mips; m++)
                    Graphics.CopyTexture(slices[s], 0, m, a, s, m);
            return a;
        }

        static string PagePath(string format) => $"{Generated}/pages-{format}.asset";

        /// <summary>The pages as saved assets, made if missing: (RGBA8 array, BC7 array).</summary>
        internal static (Texture2DArray rgba8, Texture2DArray bc7) EnsurePages()
        {
            var a = AssetDatabase.LoadAssetAtPath<Texture2DArray>(PagePath("rgba8"));
            var b = AssetDatabase.LoadAssetAtPath<Texture2DArray>(PagePath("bc7"));
            if (a != null && b != null)
                return (a, b);
            var built = Build(null);
            return (built.rgba8, built.bc7);
        }

        class Built
        {
            public Texture2DArray rgba8, bc7;
            public Texture2D[] raw, compressed;
            public double compressSeconds;
        }

        /// <summary>Makes the slices, compresses them to BC7 and saves both arrays.</summary>
        static Built Build(Report report)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath, "..", Generated));
            var b = new Built { raw = new Texture2D[Slices], compressed = new Texture2D[Slices] };
            var clock = System.Diagnostics.Stopwatch.StartNew();
            for (int s = 0; s < Slices; s++)
            {
                var mips = Content(s);
                b.raw[s] = Texture(mips, W, H, SliceNames[s]);
                b.compressed[s] = Texture(mips, W, H, SliceNames[s] + "-bc7");
            }
            clock.Restart();
            foreach (var t in b.compressed)
            {
                EditorUtility.CompressTexture(t, TextureFormat.BC7, TextureCompressionQuality.Best);
                t.Apply(false);
            }
            b.compressSeconds = clock.Elapsed.TotalSeconds;
            b.rgba8 = Fill(b.raw, "pages-rgba8");
            b.bc7 = Fill(b.compressed, "pages-bc7");
            foreach (var (array, f) in new[] { (b.rgba8, "rgba8"), (b.bc7, "bc7") })
            {
                AssetDatabase.DeleteAsset(PagePath(f));
                AssetDatabase.CreateAsset(array, PagePath(f));
            }
            AssetDatabase.SaveAssets();
            if (report != null)
            {
                report.compressSeconds = b.compressSeconds;
                report.compressedFormat = b.compressed[0].format.ToString();
                report.compressedMips = b.compressed[0].mipmapCount;
                report.pageHashes = Enumerable.Range(0, Slices).Select(s =>
                    $"{SliceNames[s]} rgba8 {Sha(b.raw[s])}, bc7 {Sha(b.compressed[s])}").ToArray();
            }
            return b;
        }

        static string Sha(Texture2D t)
        {
            using var sha = System.Security.Cryptography.SHA256.Create();
            var all = new List<byte>();
            for (int m = 0; m < t.mipmapCount; m++)
                all.AddRange(t.GetPixelData<byte>(m).ToArray());
            return string.Concat(sha.ComputeHash(all.ToArray()).Take(8).Select(x => x.ToString("x2")));
        }

        // ------------------------------------------------------------------------------------------------ the quad

        /// <summary>The grid: 4,096 cells covering clip space, each its own four vertices (its piece is flat), UV1 its
        /// chart's inside in the pages, UV3.x its piece index.
        ///
        /// Tiled (R2b, the step-3 verdict's decision 7): each cell's UVs span <paramref name="tile"/> times its chart's
        /// texels from the chart's corner (kept inside the page, so they run on into the charts beside it), so the pages
        /// are sampled minified, trilinear, with their mips, as the street stop will. At 1440p a cell is 40 by 22.5
        /// pixels over 12 by 4 texels: 0.3 texels a pixel across at 1 (magnified, mip 0), 1.2 at 4 (LOD 0.26, mips 0
        /// and 1), 2.4 at 8 (LOD 1.26, mips 1 and 2). At 1 the UVs are R2's to the bit.</summary>
        internal static Mesh QuadMesh(int tile = 1)
        {
            int spanW = (CellW - 2 * Pad) * tile, spanH = (CellH - 2 * Pad) * tile;
            var pos = new List<Vector3>(Pieces * 4);
            var uv1 = new List<Vector2>(Pieces * 4);
            var uv3 = new List<Vector2>(Pieces * 4);
            var tri = new List<int>(Pieces * 6);
            for (int cy = 0; cy < Grid; cy++)
                for (int cx = 0; cx < Grid; cx++)
                {
                    int p = cy * Grid + cx, v = pos.Count;
                    float x0 = -1f + 2f * cx / Grid, x1 = -1f + 2f * (cx + 1) / Grid;
                    float y0 = -1f + 2f * cy / Grid, y1 = -1f + 2f * (cy + 1) / Grid;
                    int tx = Mathf.Min(cx * CellW + Pad, W - spanW), ty = Mathf.Min(cy * CellH + Pad, H - spanH);
                    float u0 = tx / (float)W, u1 = (tx + spanW) / (float)W;
                    float v0 = ty / (float)H, v1 = (ty + spanH) / (float)H;
                    pos.AddRange(new[] { new Vector3(x0, y0, 0), new Vector3(x1, y0, 0), new Vector3(x1, y1, 0), new Vector3(x0, y1, 0) });
                    uv1.AddRange(new[] { new Vector2(u0, v0), new Vector2(u1, v0), new Vector2(u1, v1), new Vector2(u0, v1) });
                    for (int k = 0; k < 4; k++)
                        uv3.Add(new Vector2(p, 0));
                    tri.AddRange(new[] { v, v + 2, v + 1, v, v + 3, v + 2 });
                }
            var mesh = new Mesh { name = tile == 1 ? "History quad (4,096 pieces)" : $"History quad (4,096 pieces, tiled x{tile})" };
            mesh.SetVertices(pos);
            mesh.SetUVs(1, uv1);
            mesh.SetUVs(3, uv3);
            mesh.SetTriangles(tri, 0);
            // (its positions are clip space: bounds that hold any frustum, so it is never culled)
            mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 100000f);
            return mesh;
        }

        /// <summary>
        /// The quad and its two sets of pages in the open scene, in front of the camera (its positions are clip space; it
        /// stands a metre ahead only so it is never culled): the quad renderer, and the RGBA8 and BC7 binders (neither
        /// binds on enable: the caller binds one).
        /// </summary>
        internal static (MeshRenderer quad, HistoryPages rgba8, HistoryPages bc7) AddQuad(Camera cam)
        {
            var (ra, rb) = EnsurePages();
            var go = new GameObject("History quad (step 3, R2)");
            go.transform.SetParent(cam.transform, false);
            go.transform.localPosition = new Vector3(0f, 0f, 1f);
            go.AddComponent<MeshFilter>().sharedMesh = QuadMesh();
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = new Material(Shader.Find(QuadShader)) { name = "History quad" };
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = false;
            var table = PieceTable();
            HistoryPages Binder(string name, Texture2DArray a)
            {
                var b = new GameObject(name).AddComponent<HistoryPages>();
                b.transform.SetParent(go.transform, false);
                b.bindOnEnable = false;
                b.rgba = a;
                b.pieces = table;
                return b;
            }
            return (r, Binder("Pages RGBA8", ra), Binder("Pages BC7", rb));
        }

        // ------------------------------------------------------------------------------------------------ the checks

        [System.Serializable]
        class Report
        {
            public string what = "step 3, R2: the synthetic pages and R0's Metal questions (LT1History.Pages)";
            public string unity, gpu, api, copyTextureSupport;
            public int width = W, height = H, slices = Slices, mips = Mips, pieces = Pieces;
            public string[] pageHashes;
            public double compressSeconds;
            public string compressedFormat;
            public int compressedMips;
            public bool compressKeepsMips;
            public string mipsTest;
            public string[] bc7Error;
            public bool decodeExact;
            public string[] copy;
            public string[] frames;
            public string quietMeans;
        }

        /// <summary>A Texture2D's mip decoded on the GPU (a same-size blit into a linear 8-bit target, read back).</summary>
        static Color32[] Decode(Texture2D src, int mip)
        {
            int w = Mathf.Max(1, src.width >> mip), h = Mathf.Max(1, src.height >> mip);
            var one = new Texture2D(w, h, src.format, false, true) { filterMode = FilterMode.Point };
            one.SetPixelData(src.GetPixelData<byte>(mip), 0);
            one.Apply(false);
            var rt = RenderTexture.GetTemporary(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear);
            Graphics.Blit(one, rt);
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var back = new Texture2D(w, h, TextureFormat.RGBA32, false, true);
            back.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            back.Apply(false);
            RenderTexture.active = prev;
            RenderTexture.ReleaseTemporary(rt);
            var px = back.GetPixels32();
            Object.DestroyImmediate(one);
            Object.DestroyImmediate(back);
            return px;
        }

        /// <summary>Per channel: mean, 99th percentile and largest absolute difference, in 8-bit steps.</summary>
        static string Error(Color32[] a, Color32[] b)
        {
            var parts = new List<string>();
            for (int c = 0; c < 4; c++)
            {
                var d = new int[a.Length];
                long sum = 0;
                for (int i = 0; i < a.Length; i++)
                {
                    d[i] = Mathf.Abs(Ch(a[i], c) - Ch(b[i], c));
                    sum += d[i];
                }
                System.Array.Sort(d);
                parts.Add($"{"rgba"[c]} {sum / (double)a.Length:F2}/{d[(int)System.Math.Ceiling(0.99 * d.Length) - 1]}/{d[^1]}");
            }
            return string.Join(", ", parts);
        }

        static int Ch(Color32 p, int c) => c == 0 ? p.r : c == 1 ? p.g : c == 2 ? p.b : p.a;

        static bool Same(Color32[] a, Color32[] b) => a.Length == b.Length && !a.Where((p, i) => !p.Equals(b[i])).Any();

        public static void Pages()
        {
            string outDir = Cli.RepoPath("-out", "reviews/lt1/history");
            string framesDir = Cli.Arg("-frames", null);
            var rep = new Report
            {
                unity = Application.unityVersion, gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(),
                copyTextureSupport = SystemInfo.copyTextureSupport.ToString(),
            };
            // the scene first (a new scene clears what the old one held)
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var b = Build(rep);

            // the decode is exact: RGBA8 through the same path comes back byte for byte
            rep.decodeExact = Enumerable.Range(0, Mips).All(m => Same(Decode(b.raw[0], m), b.raw[0].GetPixels32(m)));

            // does CompressTexture keep the mips it is given? Two textures share mip 0; one's mip 1 is ours (the box,
            // inverted: no filter of mip 0 makes it), the other's the box. If it regenerated mips from mip 0, their
            // compressed mip 1 would be the same bytes.
            {
                const int tw = 256, th = 128;
                var top = new Color32[tw * th];
                var src = b.raw[2].GetPixels32(0);
                for (int y = 0; y < th; y++)
                    for (int x = 0; x < tw; x++)
                        top[y * tw + x] = src[y * W + x];
                var box1 = Box(top, tw, th);
                var ours1 = box1.Select(p => new Color32((byte)(255 - p.r), (byte)(255 - p.g), (byte)(255 - p.b), (byte)(255 - p.a))).ToArray();
                var tOurs = Texture(new[] { top, ours1, Box(ours1, tw / 2, th / 2) }, tw, th, "mips-ours");
                var tBox = Texture(new[] { top, box1, Box(box1, tw / 2, th / 2) }, tw, th, "mips-box");
                EditorUtility.CompressTexture(tOurs, TextureFormat.BC7, TextureCompressionQuality.Best);
                EditorUtility.CompressTexture(tBox, TextureFormat.BC7, TextureCompressionQuality.Best);
                bool differ = !tOurs.GetPixelData<byte>(1).ToArray().SequenceEqual(tBox.GetPixelData<byte>(1).ToArray());
                var back = Decode(tOurs, 1);
                rep.compressKeepsMips = differ && tOurs.mipmapCount == 3;
                rep.mipsTest = $"mip counts {tOurs.mipmapCount}/{tBox.mipmapCount}; compressed mip 1 differs between ours and the box: {differ}; " +
                               $"ours decoded against ours: {Error(back, ours1)}; against the box: {Error(back, box1)}";
                Object.DestroyImmediate(tOurs);
                Object.DestroyImmediate(tBox);
            }

            // BC7's error on the pages, slice by slice and mip by mip (mean/99th/max in 8-bit steps, per channel)
            var err = new List<string>();
            for (int s = 0; s < Slices; s++)
                for (int m = 0; m < Mips; m++)
                    err.Add($"{SliceNames[s]} mip {m}: {Error(Decode(b.compressed[s], m), b.raw[s].GetPixels32(m))}");
            rep.bc7Error = err.ToArray();

            // the scene: a camera, the date, the quad and its pages
            var cam = new GameObject("Camera").AddComponent<Camera>();
            cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 100f;
            new GameObject("The fabric's date").AddComponent<FabricDate>().Set(1989);
            var (quad, rgba8, bc7) = AddQuad(cam);
            rgba8.bindOnEnable = true;
            EditorSceneManager.SaveScene(scene, ScenePath);

            // does the GPU copy a Texture2D into an array slice? The quad drawn from arrays the GPU filled by
            // CopyTexture against the same drawn from the arrays filled on the CPU, at the player's size (a chart's 12 by 4
            // texels magnified: mip 0), a quarter of it (about 1:1, mips 0 and 1) and a sixteenth (minified about 4.8
            // times: the last mip, 2)
            var copies = new List<string>();
            var gpuRgba = Copy(b.raw, "pages-rgba8 (GPU copy)");
            var gpuBc7 = Copy(b.compressed, "pages-bc7 (GPU copy)");
            HistoryPages Temp(Texture2DArray a)
            {
                var h = new GameObject("temp pages").AddComponent<HistoryPages>();
                h.bindOnEnable = false;
                h.rgba = a;
                h.pieces = rgba8.pieces;
                return h;
            }
            var arms = new (string name, HistoryPages pages, bool off)[]
            {
                ("on-rgba8", rgba8, false), ("on-rgba8-gpucopy", Temp(gpuRgba), false),
                ("on-bc7", bc7, false), ("on-bc7-gpucopy", Temp(gpuBc7), false), ("off", rgba8, true),
            };
            var shots = new Dictionary<string, Color32[]>();
            var sizes = new[] { (PlayerFrame.Width, PlayerFrame.Height), (PlayerFrame.Width / 4, PlayerFrame.Height / 4), (PlayerFrame.Width / 16, PlayerFrame.Height / 16) };
            foreach (var (w, h) in sizes)
                foreach (var (name, pages, off) in arms)
                {
                    pages.Bind();
                    if (off) Shader.EnableKeyword("OS_HISTORY_OFF");
                    using (var f = new PlayerFrame(cam, w, h))
                    {
                        f.Render(2);
                        string key = $"{name}@{w}";
                        shots[key] = f.Read().GetPixels32();
                        if (framesDir != null && w == PlayerFrame.Width)
                            f.Save(Path.Combine(framesDir, $"quad-{name}.png"));
                    }
                    Shader.DisableKeyword("OS_HISTORY_OFF");
                }
            foreach (int w in sizes.Select(x => x.Item1))
            {
                copies.Add($"{w} wide: RGBA8 GPU copy = CPU fill: {Same(shots[$"on-rgba8-gpucopy@{w}"], shots[$"on-rgba8@{w}"])}; " +
                           $"BC7 GPU copy = CPU fill: {Same(shots[$"on-bc7-gpucopy@{w}"], shots[$"on-bc7@{w}"])}; " +
                           $"BC7 against RGBA8 (sRGB frame): {Error(shots[$"on-bc7@{w}"], shots[$"on-rgba8@{w}"])}; " +
                           $"off differs from on: {!Same(shots[$"off@{w}"], shots[$"on-rgba8@{w}"])}");
            }
            rep.copy = copies.ToArray();
            rep.frames = shots.Keys.Select(k => $"{k}: {Sha(shots[k])}").ToArray();
            rep.quietMeans = Means();

            Directory.CreateDirectory(outDir);
            File.WriteAllText(Path.Combine(outDir, "r2-pages.json"), JsonUtility.ToJson(rep, true));
            Debug.Log($"[LT1History] {JsonUtility.ToJson(rep, true)}");
            Object.DestroyImmediate(gpuRgba);
            Object.DestroyImmediate(gpuBc7);
        }

        static string Sha(Color32[] px)
        {
            using var sha = System.Security.Cryptography.SHA256.Create();
            var bytes = new byte[px.Length * 4];
            for (int i = 0; i < px.Length; i++)
            {
                bytes[i * 4] = px[i].r;
                bytes[i * 4 + 1] = px[i].g;
                bytes[i * 4 + 2] = px[i].b;
                bytes[i * 4 + 3] = px[i].a;
            }
            return string.Concat(sha.ComputeHash(bytes).Take(8).Select(x => x.ToString("x2")));
        }

        // ------------------------------------------------------------------------------------------------ quiet means

        /// <summary>
        /// The gully's means, per material, of what history off holds (Stone.shader: polish, lichen years / 200, moss,
        /// water held; years since bare / 200, the water layer), over every vertex: the materials' quiet means as
        /// LT1Stone sets them.
        /// </summary>
        public static void QuietMeans() => Debug.Log(Means());

        static string Means()
        {
            var sb = new StringBuilder("[LT1History] quiet means (vertex means: polish, lichen/200, moss, held; years/200, water):\n");
            foreach (var (fbx, cheeks) in new[] { ("Assets/Art/Stone/stone_gully.fbx", false), ("Assets/Art/Stone/stone_gully_cheeks.fbx", true) })
            {
                var acc = new Dictionary<string, (double[] sum, long n)>();
                foreach (var mesh in AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<Mesh>())
                {
                    string mat = cheeks ? "rubble" : mesh.name.Contains("_setts") ? "granite" : "slate";
                    var u1 = new List<Vector2>(); var u2 = new List<Vector2>(); var u4 = new List<Vector2>(); var u5 = new List<Vector2>();
                    mesh.GetUVs(1, u1); mesh.GetUVs(2, u2); mesh.GetUVs(4, u4); mesh.GetUVs(5, u5);
                    if (!acc.TryGetValue(mat, out var a))
                        a = (new double[6], 0);
                    for (int i = 0; i < mesh.vertexCount; i++)
                    {
                        a.sum[0] += u4[i].x; a.sum[1] += u4[i].y; a.sum[2] += u5[i].x; a.sum[3] += u5[i].y;
                        a.sum[4] += u1[i].x; a.sum[5] += u2[i].y;
                    }
                    a.n += mesh.vertexCount;
                    acc[mat] = a;
                }
                foreach (var kv in acc)
                    sb.Append($"  {kv.Key} ({kv.Value.n:N0} vertices): " +
                              string.Join(", ", kv.Value.sum.Select(x => (x / kv.Value.n).ToString("F4", CultureInfo.InvariantCulture))) + "\n");
            }
            return sb.ToString();
        }
    }
}
