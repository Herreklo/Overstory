using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;
using Object = UnityEngine.Object;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// Port step 2b, R2b's look loop (make, look, fix): a panel of wall from tools/r2b_wall.py drawn at a stand in one
    /// light, from a person's eye, in grey and in its material, and a sheet of the two beside a reference.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1R2b.Still -mesh panel.bin
    ///         -out reviews/lt1/port/2b/r2b/wallstone/round1 [-moment 1600-low-sun] [-at 53,-1] [-rake 65]
    ///         [-cam 2.8,-2.2,1.6] [-aim 0,1.2,0.9] [-ref docs/references/stone/10-....jpg -crop x,y,w,h]
    ///
    /// -rake: the face's normal turned this many degrees off the sun's bearing (90 grazing); -cam: the eye out from the
    /// face, along it (to the viewer's right) and up from the ground; -aim: the point looked at, the same way.
    ///
    /// A set in one run (the checks once a look holds): -moment, -mesh and -cam each take a list (moments and meshes by
    /// commas, a mesh as tag=path; cams by semicolons, each tag:out,along,eye[,aimOut,aimAlong,aimUp]), -looks grey,material;
    /// each frame is named by what varies: out-moment-tag-cam-look.png.
    /// </summary>
    public static class LT1R2b
    {
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const float Lens35 = 37.8f;

        static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
        static float[] Fs(string s) => System.Array.ConvertAll(s.Split(','), F);

        public static void Still()
        {
            var at = Fs(Cli.Arg("-at", "53,-1"));
            float rake = F(Cli.Arg("-rake", "65"));
            var cam = Fs(Cli.Arg("-cam", "2.8,-2.2,1.6"));
            var aim = Fs(Cli.Arg("-aim", "0,1.2,0.9"));
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outBase = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/port/2b/r2b/still"));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            GameObject wall = null;
            var made = new List<Object>();
            try
            {
                var moments = Cli.Arg("-moment", "1600-low-sun").Split(',');
                var meshes = new List<(string tag, string path)>();
                foreach (var e in Cli.Arg("-mesh", "").Split(','))
                {
                    int k = e.IndexOf('=');
                    meshes.Add(k < 0 ? ("", e) : (e.Substring(0, k), e.Substring(k + 1)));
                }
                var cams = new List<(string tag, float[] v)>();
                foreach (var e in Cli.Arg("-cams", "").Split(';'))
                {
                    if (e == "")
                        continue;
                    int k = e.IndexOf(':');
                    cams.Add((e.Substring(0, k), Fs(e.Substring(k + 1))));
                }
                if (cams.Count == 0)
                    cams.Add(("", new[] { cam[0], cam[1], cam[2], aim[0], aim[1], aim[2] }));
                var looks = Cli.Arg("-looks", "grey,material").Split(',');
                string Name(string moment, string tag, string camTag, string look)
                {
                    string f = outBase;
                    if (moments.Length > 1) f += "-" + moment;
                    if (meshes.Count > 1) f += "-" + tag;
                    if (cams.Count > 1) f += "-" + camTag;
                    return f + "-" + look + ".png";
                }
                var files = new List<string>();
                foreach (var moment in moments)
                {
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        throw new FileNotFoundException($"no rig {moment}");
                    // -dry: the light's sky with its stone dry (an in-memory copy, never saved): reference 10's overcast
                    if (Cli.Flag("-dry"))
                    {
                        rig = Object.Instantiate(rig);
                        rig.hideFlags = HideFlags.DontSave;
                        rig.wetness = 0f;
                        made.Add(rig);
                    }
                    stage.rig = rig;
                    stage.Apply();
                    // the face turned so the sun rakes it: its normal the sun's bearing turned by the rake (-normal x,y: as given)
                    var s = rig.SunDirectionStreet;
                    var h = new Vector2(s.x, s.y).normalized;
                    float r = -rake * Mathf.Deg2Rad;
                    var n = new Vector2(h.x * Mathf.Cos(r) - h.y * Mathf.Sin(r), h.x * Mathf.Sin(r) + h.y * Mathf.Cos(r));
                    if (Cli.Arg("-normal", "") != "")
                    {
                        var g = Fs(Cli.Arg("-normal", ""));
                        n = new Vector2(g[0], g[1]).normalized;
                    }
                    var right = new Vector2(-n.y, n.x);
                    float ground = Ground(at[0], at[1]);
                    Vector2 Off(float o, float a) => new Vector2(at[0], at[1]) + n * o + right * a;
                    foreach (var (tag, path) in meshes)
                    {
                        var mesh = Load(Path.Combine(repo, path));
                        made.Add(mesh);
                        wall = new GameObject("r2b wall");
                        wall.transform.SetPositionAndRotation(StreetSpace.ToUnity(at[0], at[1], ground),
                                                              Quaternion.LookRotation(new Vector3(-n.x, 0f, -n.y), Vector3.up));
                        var body = new GameObject("panel");
                        body.transform.SetParent(wall.transform, false);
                        // (the panel's middle on the stand, its lowest bed 0.15 m into the ground)
                        body.transform.localPosition = new Vector3(-mesh.bounds.max.x / 2f, -0.15f, 0f);
                        body.AddComponent<MeshFilter>().sharedMesh = mesh;
                        var mr = body.AddComponent<MeshRenderer>();
                        mr.shadowCastingMode = ShadowCastingMode.On;
                        // -mat rubble (the cheek walls' rock, from cutting the gully: each stone its own value and hue) or slate
                        var saved = AssetDatabase.LoadAssetAtPath<Material>($"Assets/Art/Stone/M_Stone_{Cli.Arg("-mat", "rubble")}.mat");
                        var mat = new Material(saved) { hideFlags = HideFlags.DontSave };
                        mat.DisableKeyword("OS_PATCHES");
                        mat.SetFloat("_Grey", 0f);
                        var grey = new Material(mat) { hideFlags = HideFlags.DontSave };
                        grey.SetFloat("_Grey", 1f);
                        made.Add(mat);
                        made.Add(grey);
                        foreach (var (camTag, v) in cams)
                        {
                            var c = Off(v[0], v[1]);
                            var t = v.Length >= 6 ? Off(v[3], v[4]) : Off(aim[0], aim[1]);
                            var pos = new Vector3(c.x, c.y, Ground(c.x, c.y) + v[2]);
                            var target = new Vector3(t.x, t.y, ground + (v.Length >= 6 ? v[5] : aim[2]));
                            LT1Stone.Aim(stage, shot, ("r2b", pos, target, Lens35));
                            Debug.Log($"[LT1R2b] {moment} {tag} {camTag}: sun (street) {s}, face normal {n}, ground {ground:F3}, " +
                                      $"eye {pos}, aim {target}, {mesh.vertexCount / 3} triangles");
                            foreach (var look in looks)
                            {
                                mr.sharedMaterial = look == "grey" ? grey : mat;
                                string file = Name(moment, tag, camTag, look);
                                LT1Render.Still(stage.view, file, grey: true, eighth: false, msaa: 4);
                                files.Add(file);
                            }
                        }
                        Object.DestroyImmediate(wall);
                        wall = null;
                    }
                }
                string refFile = Cli.Arg("-ref", "");
                if (refFile != "" && files.Count == 2)
                    Sheet(Path.Combine(repo, refFile), Fs(Cli.Arg("-crop", "0,0,1,1")), files[1], files[0], $"{outBase}-sheet.png");
            }
            finally
            {
                if (wall != null)
                    Object.DestroyImmediate(wall);
                foreach (var o in made)
                    Object.DestroyImmediate(o);
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        [System.Serializable] class PieceData { public float valueLstar; public float lichenSpread; }
        [System.Serializable] class RockData { public PieceData piece; }

        /// <summary>
        /// R2b's stones in the gully (tools/r2b_gully.py: R1's laying built with R2b's parts, in Unity's frame), drawn
        /// in place of the stair and cheek walls the heart stages (the regression reference: hidden in memory, never
        /// removed), from one of the gully's views (LT1Stone.Views; the target frame's street stop when not given), in
        /// grey and in its material, and a sheet of the two beside the target frame.
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1R2b.Gully
        ///         -mesh cache/r2b/gully -out reviews/lt1/port/2b/r2b/gully/round01 [-moment 1300-drizzle,...] [-dry]
        ///         [-view street,...] [-looks grey,material] [-ref reviews/lt1/heart/target/3-street-gully-steps-target.png]
        ///         [-old]
        ///
        /// The walls are drawn in the rubble's material, the steps and copings in the slate's, each stone its own value
        /// and lichen by the slate's piece (packs/stavanger-1989/materials/slate.json). -old draws the old gully instead.
        /// </summary>
        public static void Gully()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outBase = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/port/2b/r2b/gully/still"));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var made = new List<Object>();
            var root = new GameObject("r2b gully") { hideFlags = HideFlags.DontSave };
            try
            {
                // -old: the old gully as it stands, to see the shared layers on its stones
                bool old = Cli.Flag("-old");
                foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                    if (!old && r.transform.root.name.StartsWith("stone_gully"))
                        r.enabled = false;
                string mesh = Cli.Arg("-mesh", "cache/r2b/gully");
                var drawn = new List<(MeshRenderer mr, Material mat, Material grey)>();
                // (the working's rock: the town's slate, its pieces' spread)
                var piece = JsonUtility.FromJson<RockData>(File.ReadAllText(
                    Path.Combine(repo, "packs/stavanger-1989/materials/slate.json"))).piece;
                foreach (var (part, rock) in old ? new (string, string)[0] : new[] { ("walls", "rubble"), ("slabs", "slate") })
                {
                    var m = Load(Path.Combine(repo, $"{mesh}-{part}.bin"));
                    made.Add(m);
                    var g = new GameObject(part);
                    g.transform.SetParent(root.transform, false);
                    g.AddComponent<MeshFilter>().sharedMesh = m;
                    var mr = g.AddComponent<MeshRenderer>();
                    mr.shadowCastingMode = ShadowCastingMode.On;
                    var saved = AssetDatabase.LoadAssetAtPath<Material>($"Assets/Art/Stone/M_Stone_{rock}.mat");
                    var mat = new Material(saved) { hideFlags = HideFlags.DontSave };
                    mat.DisableKeyword("OS_PATCHES");
                    mat.SetFloat("_Grey", 0f);
                    // each stone its own value and lichen, the rock's (its per-piece value the pack's alone)
                    var grain = mat.GetVector("_Grain");
                    mat.SetVector("_Grain", new Vector4(grain.x, grain.y, 0f, grain.w));
                    mat.SetVector("_Piece", new Vector4(piece.valueLstar, piece.lichenSpread, 0f, 0f));
                    var grey = new Material(mat) { hideFlags = HideFlags.DontSave };
                    grey.SetFloat("_Grey", 1f);
                    made.Add(mat);
                    made.Add(grey);
                    drawn.Add((mr, mat, grey));
                    Debug.Log($"[LT1R2b] gully {part}: {m.vertexCount / 3} triangles, {rock}");
                }
                // (several views or moments: OUT-moment-view-look.png, for tools/r2b_sheet.py)
                var viewNames = Cli.Arg("-view", "street").Split(',');
                var moments = Cli.Arg("-moment", "1300-drizzle").Split(',');
                var looks = Cli.Arg("-looks", "grey,material").Split(',');
                var files = new List<string>();
                foreach (var moment in moments)
                {
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        throw new FileNotFoundException($"no rig {moment}");
                    if (Cli.Flag("-dry"))
                    {
                        rig = Object.Instantiate(rig);
                        rig.hideFlags = HideFlags.DontSave;
                        rig.wetness = 0f;
                        made.Add(rig);
                    }
                    stage.rig = rig;
                    stage.Apply();
                    foreach (var viewName in viewNames)
                    {
                        var view = System.Array.Find(LT1Stone.Views, v => v.name == viewName);
                        if (view.name == null)
                            throw new System.ArgumentException($"no gully view {viewName}");
                        LT1Stone.Aim(stage, shot, view);
                        foreach (var look in looks)
                        {
                            foreach (var (mr, mat, grey) in drawn)
                                mr.sharedMaterial = look == "grey" ? grey : mat;
                            string file = outBase + (moments.Length > 1 || viewNames.Length > 1 ? $"-{moment}-{viewName}" : "")
                                        + "-" + look + ".png";
                            LT1Render.Still(stage.view, file, grey: true, eighth: false, msaa: 4);
                            files.Add(file);
                        }
                    }
                }
                string refFile = Cli.Arg("-ref", "reviews/lt1/heart/target/3-street-gully-steps-target.png");
                if (refFile != "" && files.Count == 2)
                    Sheet(Path.Combine(repo, refFile), Fs(Cli.Arg("-crop", "0,0,1920,1080")), files[1], files[0], $"{outBase}-sheet.png");
            }
            finally
            {
                Object.DestroyImmediate(root);
                foreach (var o in made)
                    Object.DestroyImmediate(o);
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>tools/r2b_wall.py's triangle soup: each triangle its own three corners, their normals given (the face
        /// soft, the sides flat), its winding turned for Unity's.</summary>
        internal static Mesh Load(string path)
        {
            using var br = new BinaryReader(File.OpenRead(path));
            if (new string(br.ReadChars(4)) != "R2B2")
                throw new IOException($"{path}: not an R2B2 mesh");
            int count = br.ReadInt32();
            var v = new Vector3[count];
            for (int i = 0; i < count; i++)
                v[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            var mesh = new Mesh { name = "r2b panel", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            mesh.vertices = v;
            var nn = new Vector3[count];
            for (int i = 0; i < count; i++)
                nn[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            mesh.normals = nn;
            for (int k = 0; k < 8; k++)
            {
                var uv = new List<Vector2>(count);
                for (int i = 0; i < count; i++)
                    uv.Add(new Vector2(br.ReadSingle(), br.ReadSingle()));
                mesh.SetUVs(k, uv);
            }
            var tri = new int[count];
            for (int i = 0; i < count; i += 3)
            {
                tri[i] = i;
                tri[i + 1] = i + 2;
                tri[i + 2] = i + 1;
            }
            mesh.triangles = tri;
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>The ground's height under a street point: the highest "ground" triangle there.</summary>
        static float Ground(float x, float y)
        {
            float best = float.MinValue;
            var o = StreetSpace.ToUnity(x, y, 200f);
            foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
            {
                var rr = mf.GetComponent<MeshRenderer>();
                if (!mf.gameObject.name.StartsWith("ground") || mf.sharedMesh == null || rr == null || !rr.enabled)
                    continue;
                var b = rr.bounds;
                if (o.x < b.min.x || o.x > b.max.x || o.z < b.min.z || o.z > b.max.z)
                    continue;
                var vv = mf.sharedMesh.vertices;
                var l2w = mf.transform.localToWorldMatrix;
                for (int sm = 0; sm < mf.sharedMesh.subMeshCount; sm++)
                {
                    var t = mf.sharedMesh.GetTriangles(sm);
                    for (int i = 0; i < t.Length; i += 3)
                    {
                        Vector3 a = l2w.MultiplyPoint3x4(vv[t[i]]), c = l2w.MultiplyPoint3x4(vv[t[i + 1]]), d = l2w.MultiplyPoint3x4(vv[t[i + 2]]);
                        float den = (c.z - d.z) * (a.x - d.x) + (d.x - c.x) * (a.z - d.z);
                        if (Mathf.Abs(den) < 1e-9f)
                            continue;
                        float l1 = ((c.z - d.z) * (o.x - d.x) + (d.x - c.x) * (o.z - d.z)) / den;
                        float l2 = ((d.z - a.z) * (o.x - d.x) + (a.x - d.x) * (o.z - d.z)) / den;
                        float l3 = 1f - l1 - l2;
                        if (l1 < -1e-6f || l2 < -1e-6f || l3 < -1e-6f)
                            continue;
                        best = Mathf.Max(best, l1 * a.y + l2 * c.y + l3 * d.y);
                    }
                }
            }
            if (best == float.MinValue)
                throw new System.InvalidOperationException($"no ground under ({x}, {y})");
            return best;
        }

        /// <summary>The sheet: the reference's crop beside the material still, the grey still beneath them, each 960 by
        /// 540.</summary>
        static void Sheet(string refFile, float[] crop, string material, string grey, string file)
        {
            const int W = 960, H = 540;
            var sheet = new Texture2D(2 * W, 2 * H, TextureFormat.RGB24, false);
            var fill = new Color32[4 * W * H];
            for (int i = 0; i < fill.Length; i++)
                fill[i] = new Color32(24, 24, 24, 255);
            sheet.SetPixels32(fill);
            var rf = new Texture2D(2, 2);
            rf.LoadImage(File.ReadAllBytes(refFile));
            // (the crop in the reference's pixels from its top left)
            int cx = (int)crop[0], cw = (int)crop[2], ch = (int)crop[3], cy = rf.height - (int)crop[1] - ch;
            var cut = new Texture2D(cw, ch, TextureFormat.RGB24, false);
            cut.SetPixels(rf.GetPixels(cx, cy, cw, ch));
            cut.Apply();
            Put(sheet, cut, 0, H, W, H);
            foreach (var (f, x, y) in new[] { (material, W, H), (grey.Replace(".png", "-grey.png"), 0, 0), (material.Replace(".png", "-grey.png"), W, 0) })
            {
                var t = new Texture2D(2, 2);
                t.LoadImage(File.ReadAllBytes(f));
                Put(sheet, t, x, y, W, H);
                Object.DestroyImmediate(t);
            }
            sheet.Apply();
            File.WriteAllBytes(file, sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
            Object.DestroyImmediate(rf);
            Object.DestroyImmediate(cut);
        }

        /// <summary>A texture fitted into a box of the sheet (its aspect kept, centred), bilinear.</summary>
        static void Put(Texture2D sheet, Texture2D src, int x, int y, int w, int h)
        {
            float k = Mathf.Min((float)w / src.width, (float)h / src.height);
            int dw = Mathf.RoundToInt(src.width * k), dh = Mathf.RoundToInt(src.height * k);
            int ox = x + (w - dw) / 2, oy = y + (h - dh) / 2;
            var px = new Color[dw * dh];
            for (int j = 0; j < dh; j++)
                for (int i = 0; i < dw; i++)
                    px[j * dw + i] = src.GetPixelBilinear((i + 0.5f) / dw, (j + 0.5f) / dh);
            sheet.SetPixels(ox, oy, dw, dh, px);
        }
    }
}
