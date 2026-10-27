using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.EditorTools.Corner;
using Object = UnityEngine.Object;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The passes a style frame is painted over (reviews/lt1/art-direction/, tools/style_frame.py): the corner exactly as
    /// LT1Houses.Still stages it (its houses, the gully, the clay), drawn once per pass with every renderer's material
    /// swapped for ArtPasses.shader, with no post, no style and no light in the air. Takes LT1Houses.Still's command
    /// line (-out, -view, -houses, -tier; one -moment) and writes {out}-{view}-{pass}.png for each view:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1ArtPasses.Passes
    ///         -out reviews/lt1/art-direction/passes/street -view street -houses C,D,E -tier street -moment 1300-drizzle
    ///         -looks grey -ref ""
    ///
    /// The beauty frames come from LT1Houses.Still itself, with the same arguments and the lights wanted.
    /// </summary>
    public static class LT1ArtPasses
    {
        static readonly string[] Names = { "normal", "distance", "position", "fine", "surface" };
        static readonly int PassId = Shader.PropertyToID("_OS_ArtPass");
        static readonly int ClassId = Shader.PropertyToID("_Class");
        static readonly string[] Quiet = { "_OS_PaletteOn", "_OS_FogLampStrength" };
        static readonly string[] QuietVectors = { "_OS_SunBeams", "_OS_GlowParams" };

        static Material pass;
        static readonly List<(Renderer r, Material[] mats, MaterialPropertyBlock block)> swapped = new();
        static readonly Dictionary<string, float> quiet = new();
        static readonly Dictionary<string, Vector4> quietVectors = new();
        static bool post;
        static CameraClearFlags clear;
        static Color background;
        static Material skybox;

        /// <summary>What a renderer is, by its material's shader: 0 nothing (the sky), 1 clay, 2 a house, 3 stone, 4 a tree, 5 the sky's dome, 6 anything else.</summary>
        static float ClassOf(Material m)
        {
            string s = m != null && m.shader != null ? m.shader.name : "";
            if (s.Contains("House")) return 2f;
            if (s.Contains("Stone")) return 3f;
            if (s.Contains("Tree")) return 4f;
            if (s.Contains("Sky")) return 5f;
            if (s.Contains("Street")) return 1f;
            return 6f;
        }

        public static void Passes()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outBase = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/art-direction/passes/street"));
            string[] views = Cli.Arg("-view", "street").Split(',');
            string moment = Cli.Arg("-moment", "1300-drizzle");
            pass = new Material(Shader.Find("Hidden/Overstory/ArtPasses")) { hideFlags = HideFlags.DontSave };
            RenderPipelineManager.beginCameraRendering += Swap;
            RenderPipelineManager.endCameraRendering += Restore;
            try
            {
                for (int k = 0; k < Names.Length; k++)
                {
                    Shader.SetGlobalFloat(PassId, k + 1);
                    LT1Houses.Still();
                    foreach (var view in views)
                    {
                        string made = $"{outBase}-{moment}-{view}-grey";
                        string file = $"{outBase}-{view}-{Names[k]}.png";
                        if (File.Exists(file))
                            File.Delete(file);
                        File.Move(made + ".png", file);
                        if (File.Exists(made + "-grey.png"))
                            File.Delete(made + "-grey.png");
                        Debug.Log($"[LT1ArtPasses] {file}");
                    }
                    if (File.Exists($"{outBase}-sheet.png"))
                        File.Delete($"{outBase}-sheet.png");
                }
            }
            finally
            {
                RenderPipelineManager.beginCameraRendering -= Swap;
                RenderPipelineManager.endCameraRendering -= Restore;
                Shader.SetGlobalFloat(PassId, 0f);
                Object.DestroyImmediate(pass);
            }
        }

        static void Swap(ScriptableRenderContext context, Camera cam)
        {
            if (cam.cameraType != CameraType.Game)
                return;
            swapped.Clear();
            foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                if (!r.enabled || r.sharedMaterials.Length == 0)
                    continue;
                var block = new MaterialPropertyBlock();
                if (r.HasPropertyBlock())
                    r.GetPropertyBlock(block);
                swapped.Add((r, r.sharedMaterials, block));
                var mats = new Material[r.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = pass;
                var mine = new MaterialPropertyBlock();
                mine.SetFloat(ClassId, ClassOf(r.sharedMaterial));
                r.sharedMaterials = mats;
                r.SetPropertyBlock(mine);
            }
            foreach (var q in Quiet)
            {
                quiet[q] = Shader.GetGlobalFloat(q);
                Shader.SetGlobalFloat(q, 0f);
            }
            foreach (var q in QuietVectors)
            {
                quietVectors[q] = Shader.GetGlobalVector(q);
                Shader.SetGlobalVector(q, Vector4.zero);
            }
            var data = cam.GetComponent<UniversalAdditionalCameraData>();
            post = data != null && data.renderPostProcessing;
            if (data != null)
                data.renderPostProcessing = false;
            clear = cam.clearFlags;
            background = cam.backgroundColor;
            skybox = RenderSettings.skybox;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            RenderSettings.skybox = null;
        }

        static void Restore(ScriptableRenderContext context, Camera cam)
        {
            if (cam.cameraType != CameraType.Game)
                return;
            foreach (var (r, mats, block) in swapped)
            {
                if (r == null)
                    continue;
                r.sharedMaterials = mats;
                r.SetPropertyBlock(block.isEmpty ? null : block);
            }
            swapped.Clear();
            foreach (var kv in quiet)
                Shader.SetGlobalFloat(kv.Key, kv.Value);
            foreach (var kv in quietVectors)
                Shader.SetGlobalVector(kv.Key, kv.Value);
            var data = cam.GetComponent<UniversalAdditionalCameraData>();
            if (data != null)
                data.renderPostProcessing = post;
            cam.clearFlags = clear;
            cam.backgroundColor = background;
            RenderSettings.skybox = skybox;
        }

        // ---- the painted corner (reviews/lt1/art-direction/README.md, What matters) ----

        [System.Serializable] class PGlobal { public string name, srgb; public float[] v, pos, dir; public float a = 1f, w; }
        [System.Serializable] class PSurface { public int slot; public string srgb; public float keep, wet, calm, gloss; public float lamp = 1f, veil = 1f; }
        [System.Serializable] class PMass { public int slot; public float[] box, nz, foot; }
        [System.Serializable] class PCrack { public string name; public float width; public float[] points; }
        [System.Serializable] class PClay { public int wall, ground, roof, glass; public float[] roofNz; }
        [System.Serializable] class PHide { public float[] box; public int cls; }
        [System.Serializable] class PCover { public string name; public int slot; }
        [System.Serializable] class PTuft { public string name; public int slot; public float[] from, to, lumps; public float depth, overhang, drop; public float shape = 0.6f; }
        [System.Serializable] class PLantern { public float post, glassH, glassBottom, glassTop, capH, capW; public int glassSlot, metalSlot; public float shadowBias = 0.05f, shadowNormalBias = 0.4f; }
        [System.Serializable] class PLamp { public string id, srgb; public float[] @base, head, halo; public float[] fill = new float[2]; public string fillSrgb; public float power, white, haloStrength; public float @catch = 1f; }
        [System.Serializable]
        class PaintData
        {
            public string view, moment, @out, tier;
            public string[] houses, off;
            public int width, height, super, msaa;
            public float shadowM;
            public PGlobal[] globals;
            public PSurface[] surfaces;
            public PMass[] masses;
            public PClay clay;
            public PHide[] hide;
            public PCover[] covers;
            public PLantern lantern;
            public PTuft[] tufts;
            public PCrack[] cracks;
            public PLamp[] lamps;
        }
        // the houses' records (cache/houses/houses.json): only what the painted frame reads, their coats and roofs
        [System.Serializable] class HCoat { public string srgb; public float year; }
        [System.Serializable] class HCoats { public HCoat body, back, trim, window, door; }
        [System.Serializable] class HRoof { public string material; public float year; }
        [System.Serializable] class HRow { public string name; public int index; public float[] fp; public HCoats coats; public HRoof roof; }
        [System.Serializable] class HRows { public float date; public HRow[] houses; }

        static Color LinearOf(string hex) =>
            ColorUtility.TryParseHtmlString(hex.StartsWith("#") ? hex : "#" + hex, out var c) ? c.linear
                : throw new System.FormatException($"not a colour: {hex}");

        static bool Has(float[] a) => a != null && a.Length > 0;
        static Vector3 Street(float[] a) => new Vector3(a[0], a[2], a[1]);

        /// <summary>What Compose made: the corner under one root (its camera, the greybox, the houses, the lamps and the
        /// elements), the globals it set, and how to put the heart back.</summary>
        internal sealed class Composed
        {
            internal CornerBuild Build;
            internal GameObject Root;
            internal Camera Camera;
            internal UniversalRendererData RendererData;
            internal int Width, Height, Super, Msaa;
            internal float ShadowM;
            internal string Out;
            internal readonly List<System.Action> restore = new();
            internal readonly List<System.Action> cleanup = new();
            bool restored, cleaned;

            /// <summary>The pipeline, the renderer's features, the heart's lights and renderers as they were (nothing
            /// made is destroyed): before anything is saved.</summary>
            internal void RestoreSettings()
            {
                if (restored)
                    return;
                restored = true;
                for (int i = restore.Count - 1; i >= 0; i--)
                    try { restore[i](); } catch (System.Exception e) { Debug.LogException(e); }
            }

            /// <summary>RestoreSettings, then everything made in memory destroyed (what was saved as an asset stays).</summary>
            internal void Cleanup()
            {
                RestoreSettings();
                if (cleaned)
                    return;
                cleaned = true;
                for (int i = cleanup.Count - 1; i >= 0; i--)
                    try { cleanup[i](); } catch (System.Exception e) { Debug.LogException(e); }
            }
        }

        internal const string PaintJson = "Assets/Experiments/LT1/ArtDirection/Paint.json";

        /// <summary>
        /// The painted corner composed in the heart (LT1Stone.Stage), under one root: the frame's camera on the view; the
        /// stage's meshes copied under Greybox, each drawn with the painted surface (PaintSurface.shader) for what it is,
        /// one material per class, the stage's own renderers and lights off; the houses (cut out of the clay); the lamps;
        /// then the elements ([CornerElement], Corner/CornerElement.cs) and what they hide. Every value is from Paint.json,
        /// set as globals and kept (Build.Globals) so the scene's look sets them again. The caller draws it (Paint) or
        /// saves it (LT1PaintedCorner), then calls Cleanup.
        /// </summary>
        internal static Composed Compose(string dataPath, bool forScene)
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string unity = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var P = JsonUtility.FromJson<PaintData>(File.ReadAllText(Path.Combine(unity, dataPath)));
            var C = new Composed
            {
                Width = P.width, Height = P.height, Super = Mathf.Max(1, P.super), Msaa = Mathf.Max(1, P.msaa),
                ShadowM = P.shadowM, Out = P.@out,
            };
            var build = C.Build = new CornerBuild { ForScene = forScene, Moment = P.moment, View = P.view };
            var made = build.Made;
            var G = build.Globals;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            C.restore.Add(() => urp.shadowDistance = reach);
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            C.restore.Add(() => ShaderUtil.allowAsyncCompilation = async);
            var sky = RenderSettings.skybox;
            C.restore.Add(() => RenderSettings.skybox = sky);
            try
            {
                var (stage, go) = LT1Stone.Stage(false);
                var shot = ScriptableObject.CreateInstance<CameraShot>();
                C.cleanup.Add(() =>
                {
                    if (go != null)
                        Object.DestroyImmediate(go);
                    Object.DestroyImmediate(shot);
                });
                C.cleanup.Add(() =>
                {
                    foreach (var o in made)
                        if (o != null && !EditorUtility.IsPersistent(o))
                            Object.DestroyImmediate(o);
                });
                var root = C.Root = new GameObject("Painted corner");
                C.cleanup.Add(() =>
                {
                    if (C.Root != null)
                        Object.DestroyImmediate(C.Root);
                });
                C.RendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");

                // the houses, their clay cut out of the corner's in memory (as LT1Houses.Still does)
                string dir = Path.Combine(repo, "cache/houses");
                var all = JsonUtility.FromJson<HRows>(File.ReadAllText(Path.Combine(dir, "houses.json")));
                build.Date = all.date;
                var cut = new List<Vector2[]>();
                var houseMeshes = new List<Mesh>();
                foreach (var name in P.houses)
                {
                    var row = System.Array.Find(all.houses, r => r.name == name)
                        ?? throw new System.ArgumentException($"house {name} is not in {dir}/houses.json");
                    var fp = new Vector2[4];
                    for (int i = 0; i < 4; i++)
                        fp[i] = new Vector2(row.fp[2 * i], row.fp[2 * i + 1]);
                    cut.Add(fp);
                    var m = LT1R2b.Load(Path.Combine(dir, P.tier == "near" ? $"{name}.bin" : $"{name}.{P.tier}.bin"));
                    m.name = $"house {name}";
                    made.Add(m);
                    houseMeshes.Add(m);
                }
                var cutClay = typeof(LT1Houses).GetMethod("CutClay", BindingFlags.NonPublic | BindingFlags.Static);
                var cutOf = new Dictionary<MeshFilter, Mesh>();
                foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
                {
                    if (mf.sharedMesh == null || !mf.name.StartsWith("buildings_"))
                        continue;
                    var kept = (Mesh)cutClay.Invoke(null, new object[] { mf, cut });
                    if (kept == null)
                        continue;
                    made.Add(kept);
                    cutOf[mf] = kept;
                }

                // the hour and the view
                var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{P.moment}.asset")
                    ?? throw new FileNotFoundException($"no rig {P.moment}");
                stage.rig = rig;
                stage.Apply();
                var view = System.Array.Find(LT1Stone.Views, v => v.name == P.view);
                if (view.name == null)
                    throw new System.ArgumentException($"no view {P.view}");
                LT1Stone.Aim(stage, shot, view);
                urp.shadowDistance = P.shadowM;
                // the clay's palette (StreetStage), kept for the scene
                foreach (var t in new[] { "_OS_Albedo", "_OS_Emit", "_OS_Glow", "_OS_Surface" })
                {
                    var tex = Shader.GetGlobalTexture(t);
                    if (tex != null)
                        G.Texture(t, tex);
                }

                // the frame's camera: the view's, with no post, cleared to nothing (the air draws the sky)
                var camGo = new GameObject("Camera");
                camGo.transform.SetParent(root.transform, false);
                var cam = camGo.AddComponent<Camera>();
                cam.CopyFrom(stage.view);
                camGo.tag = "MainCamera";
                cam.targetTexture = null;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = Color.clear;
                cam.allowHDR = true;
                cam.allowMSAA = true;
                var camData = cam.GetUniversalAdditionalCameraData();
                camData.renderPostProcessing = false;
                camData.antialiasing = AntialiasingMode.None;
                camData.renderShadows = true;
                camData.requiresColorOption = CameraOverrideOption.Off;
                camData.requiresDepthOption = CameraOverrideOption.Off;
                C.Camera = build.Camera = cam;
                RenderSettings.skybox = null;

                // what the corner draws before its elements (the greybox): every mesh of the stage copied under the root,
                // drawn with the painted surface for what it is (one material per class); the stage's own renderers and
                // lights off; the sky's dome and anything not a mesh left out
                var paintShader = Shader.Find("Hidden/Overstory/PaintSurface");
                var classMats = new Dictionary<(float, float, float), Material>();
                Material ClassMat(float cls, float emit, float slot)
                {
                    if (classMats.TryGetValue((cls, emit, slot), out var m))
                        return m;
                    m = new Material(paintShader) { name = $"paint class {cls}" + (emit != 0f ? $" head {emit}" : "") + (slot != 0f ? $" slot {slot}" : "") };
                    m.SetFloat(ClassId, cls);
                    m.SetFloat("_Emit", emit);
                    m.SetFloat("_Slot", slot);
                    made.Add(m);
                    classMats[(cls, emit, slot)] = m;
                    return m;
                }
                build.ClassMaterial = ClassMat;
                var greybox = new GameObject("Greybox");
                greybox.transform.SetParent(root.transform, false);
                var tally = new Dictionary<string, int>();
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    if (r.transform.IsChildOf(root.transform) || !r.enabled || r.sharedMaterials.Length == 0)
                        continue;
                    r.enabled = false;
                    C.restore.Add(() => { if (r != null) r.enabled = true; });
                    float cls = ClassOf(r.sharedMaterial);
                    string shaderName = r.sharedMaterial != null && r.sharedMaterial.shader != null ? r.sharedMaterial.shader.name : "";
                    string key = $"{cls} {(shaderName != "" ? shaderName : "-")} {r.GetType().Name}";
                    tally[key] = tally.TryGetValue(key, out int n) ? n + 1 : 1;
                    var mf = r.GetComponent<MeshFilter>();
                    if (cls == 5f || !(r is MeshRenderer) || mf == null || mf.sharedMesh == null
                        || System.Array.Exists(P.off ?? new string[0], o => shaderName.Contains(o)))
                        continue;
                    var g = new GameObject(r.name) { layer = r.gameObject.layer };
                    g.transform.SetPositionAndRotation(r.transform.position, r.transform.rotation);
                    g.transform.localScale = r.transform.lossyScale;
                    g.transform.SetParent(greybox.transform, true);
                    g.AddComponent<MeshFilter>().sharedMesh = cutOf.TryGetValue(mf, out var cutMesh) ? cutMesh : mf.sharedMesh;
                    var mr = g.AddComponent<MeshRenderer>();
                    // a material whose shader paints itself (tag "OverstoryPaint"="Own", or _PaintOwn 1) keeps it: it reads
                    // the page's globals and answers _P_Mode as PaintSurface does
                    var mats = new Material[r.sharedMaterials.Length];
                    for (int i = 0; i < mats.Length; i++)
                        mats[i] = PaintsItself(r.sharedMaterials[i]) ? r.sharedMaterials[i] : ClassMat(cls, 0f, 0f);
                    mr.sharedMaterials = mats;
                    mr.shadowCastingMode = r.shadowCastingMode;
                    mr.receiveShadows = r.receiveShadows;
                    mr.lightProbeUsage = LightProbeUsage.Off;
                    mr.reflectionProbeUsage = ReflectionProbeUsage.Off;
                    mr.renderingLayerMask = r.renderingLayerMask;
                    build.Greybox.Add(new CornerPiece { Name = r.name, Path = PathOf(r.transform), Class = (int)cls, Renderer = mr });
                }
                foreach (var kv in tally)
                    Debug.Log($"[LT1ArtPasses] renderers {kv.Key}: {kv.Value}");
                foreach (var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
                {
                    if (!l.enabled)
                        continue;
                    l.enabled = false;
                    C.restore.Add(() => { if (l != null) l.enabled = true; });
                }
                if (C.RendererData != null)
                    foreach (var f in C.RendererData.rendererFeatures)
                        if (f != null)
                        {
                            bool on = f.isActive;
                            f.SetActive(false);
                            C.restore.Add(() => f.SetActive(on));
                        }

                var houses = new GameObject("Houses");
                houses.transform.SetParent(root.transform, false);
                foreach (var m in houseMeshes)
                {
                    var g = new GameObject(m.name);
                    g.transform.SetParent(houses.transform, false);
                    g.AddComponent<MeshFilter>().sharedMesh = m;
                    var mr = g.AddComponent<MeshRenderer>();
                    mr.sharedMaterial = ClassMat(2f, 0f, 0f);
                    mr.shadowCastingMode = ShadowCastingMode.On;
                    mr.lightProbeUsage = LightProbeUsage.Off;
                    mr.reflectionProbeUsage = ReflectionProbeUsage.Off;
                    build.Greybox.Add(new CornerPiece { Name = m.name, Path = $"Houses/{m.name}", Class = 2, Renderer = mr });
                }

                // the designed values
                var globals = new Dictionary<string, Vector4>();
                foreach (var g in P.globals)
                {
                    Vector4 v;
                    if (!string.IsNullOrEmpty(g.srgb))
                    {
                        var c = LinearOf(g.srgb) * g.a;
                        v = new Vector4(c.r, c.g, c.b, g.w);
                    }
                    else if (Has(g.pos))
                        v = (Vector4)Street(g.pos) + new Vector4(0f, 0f, 0f, g.w);
                    else if (Has(g.dir))
                        v = Street(g.dir).normalized;
                    else
                        v = new Vector4(g.v[0], g.v.Length > 1 ? g.v[1] : 0f, g.v.Length > 2 ? g.v[2] : 0f, g.v.Length > 3 ? g.v[3] : 0f);
                    globals[g.name] = v;
                    G.Vector(g.name, v);
                }
                Debug.Log($"[LT1ArtPasses] zenith {globals["_P_SkyZenith"]}, focus {globals["_P_Focus"]}");
                var albedo = new Vector4[48];
                var surfB = new Vector4[48];
                var veils = new Vector4[48];
                for (int i = 0; i < 48; i++)
                {
                    albedo[i] = new Vector4(0.18f, 0.18f, 0.18f, 0f);
                    surfB[i] = new Vector4(0f, 0f, 0f, 1f);
                    veils[i] = Vector4.one;
                }
                foreach (var sf in P.surfaces)
                {
                    var c = LinearOf(sf.srgb);
                    albedo[sf.slot] = new Vector4(c.r, c.g, c.b, sf.wet);
                    surfB[sf.slot] = new Vector4(sf.calm, sf.gloss, sf.keep, sf.lamp);
                    veils[sf.slot] = new Vector4(sf.veil, 0f, 0f, 0f);
                }
                G.Array("_P_Albedo", albedo);
                G.Array("_P_SurfB", surfB);
                G.Array("_P_Veil", veils);
                var mMin = new Vector4[16];
                var mMax = new Vector4[16];
                var mN = new Vector4[16];
                var mFoot = new Vector4[16];
                for (int k = 0; k < P.masses.Length; k++)
                {
                    var b = P.masses[k].box;
                    mMin[k] = new Vector4(b[0], b[1], b[2], P.masses[k].slot);
                    mMax[k] = new Vector4(b[3], b[4], b[5], 1f);
                    mN[k] = new Vector4(P.masses[k].nz[0], P.masses[k].nz[1], 0f, 0f);
                    var f = P.masses[k].foot;
                    if (Has(f))
                        mFoot[k] = new Vector4(f[0], f[1], f[2], 0f);
                }
                G.Array("_P_MassFoot", mFoot);
                // the rock's crack and bedding lines: each a run of street points, cut into segments (world)
                var crA = new Vector4[24];
                var crB = new Vector4[24];
                int crN = 0;
                if (P.cracks != null)
                    foreach (var cr in P.cracks)
                    {
                        // a line is widest in its middle and tapers to its two ends
                        int last = cr.points.Length / 3 - 1;
                        float Wd(int j) => cr.width * (j == 0 || j == last ? 0.15f : 1f);
                        for (int j = 0; j < last && crN < 24; j++, crN++)
                        {
                            Vector3 a = Street(new[] { cr.points[3 * j], cr.points[3 * j + 1], cr.points[3 * j + 2] });
                            Vector3 bb = Street(new[] { cr.points[3 * j + 3], cr.points[3 * j + 4], cr.points[3 * j + 5] });
                            crA[crN] = new Vector4(a.x, a.y, a.z, Wd(j));
                            crB[crN] = new Vector4(bb.x, bb.y, bb.z, Wd(j + 1));
                        }
                    }
                G.Array("_P_CrackA", crA);
                G.Array("_P_CrackB", crB);
                G.Float("_P_CrackCount", crN);
                G.Array("_P_MassMin", mMin);
                G.Array("_P_MassMax", mMax);
                G.Array("_P_MassN", mN);
                G.Float("_P_MassCount", P.masses.Length);
                G.Vector("_P_Clay", new Vector4(P.clay.wall, P.clay.ground, P.clay.roof, P.clay.glass));
                G.Vector("_P_ClayRoof", new Vector4(P.clay.roofNz[0], P.clay.roofNz[1], 0f, 0f));
                G.Vector("_P_Lantern", new Vector4(P.lantern.glassSlot, P.lantern.metalSlot, 0f, 0f));
                var coats = new Vector4[64];
                string[] parts = { "body", "back", "trim", "window", "door" };
                foreach (var row in all.houses)
                {
                    if (row.index * 8 + 5 >= coats.Length)
                        continue;
                    for (int p = 0; p < parts.Length; p++)
                    {
                        var coat = (HCoat)typeof(HCoats).GetField(parts[p]).GetValue(row.coats);
                        var c = LinearOf(coat.srgb);
                        coats[row.index * 8 + p] = new Vector4(c.r, c.g, c.b, coat.year);
                    }
                    var cover = System.Array.Find(P.covers, cv => cv.name == row.roof.material);
                    coats[row.index * 8 + 5] = new Vector4(cover != null ? cover.slot : 5, row.roof.year, 0f, 0f);
                }
                G.Array("_P_Coats", coats);
                G.Float("_P_Date", all.date);

                // the lamps at their places: each a 1955 lantern (post, glass, cap) with its light, shadowed
                var lamps = new GameObject("Lamps");
                lamps.transform.SetParent(root.transform, false);
                var lampPos = new Vector4[8];
                var lampHalo = new Vector4[8];
                var lampFill = new Vector4[8];
                var lampCatch = new Vector4[8];
                float lampReach = globals.TryGetValue("_P_Pool", out var pool) ? pool.w : 16f;
                // the light reaches as far as its streak holds on the wet (the pool's own reach is the shader's)
                float lightReach = lampReach * (globals.TryGetValue("_P_Streak", out var streak) ? Mathf.Max(1f, streak.w) : 1f);
                var lt = P.lantern;
                for (int k = 0; k < P.lamps.Length && k < 8; k++)
                {
                    var lamp = P.lamps[k];
                    Vector3 foot = Street(lamp.@base), head = Street(lamp.head);
                    float glass0 = head.y - 0.5f * lt.glassH, glass1 = head.y + 0.5f * lt.glassH;
                    var post = Part(lamps, made, ClassMat(8f, 0f, 0f), $"lamp {lamp.id} post", Frustum(foot, foot.y, glass0, 0.5f * lt.post, 0.5f * lt.post));
                    var glass = Part(lamps, made, ClassMat(7f, lamp.white, 0f), $"lamp {lamp.id} glass", Frustum(foot, glass0, glass1, 0.5f * lt.glassBottom, 0.5f * lt.glassTop));
                    var cap = Part(lamps, made, ClassMat(8f, 0f, 0f), $"lamp {lamp.id} cap", Frustum(foot, glass1, glass1 + lt.capH, 0.5f * lt.capW, 0.01f));
                    foreach (var (pr, pc) in new[] { (post, 8), (glass, 7), (cap, 8) })
                        build.Greybox.Add(new CornerPiece { Name = pr.name, Path = $"Lamps/{pr.name}", Class = pc, Renderer = pr });
                    var lg = new GameObject($"lamp {lamp.id} light");
                    lg.transform.SetParent(lamps.transform, false);
                    lg.transform.position = head;
                    var light = lg.AddComponent<Light>();
                    light.type = LightType.Point;
                    ColorUtility.TryParseHtmlString(lamp.srgb, out var lc);
                    light.color = lc;
                    light.intensity = lamp.power;
                    light.range = lightReach;
                    light.shadows = LightShadows.Soft;
                    light.shadowNearPlane = 0.05f;
                    // its own bias, so a wall it rakes takes no acne rings (the pipeline's is set for the sun)
                    light.GetUniversalAdditionalLightData().usePipelineSettings = false;
                    light.shadowBias = lt.shadowBias;
                    light.shadowNormalBias = lt.shadowNormalBias;
                    var hc = LinearOf(lamp.srgb) * lamp.haloStrength;
                    lampPos[k] = new Vector4(head.x, head.y, head.z, lamp.halo[0]);
                    lampHalo[k] = new Vector4(hc.r, hc.g, hc.b, lamp.halo[1]);
                    var fc = LinearOf(string.IsNullOrEmpty(lamp.fillSrgb) ? lamp.srgb : lamp.fillSrgb) * (lamp.fill != null && lamp.fill.Length > 0 ? lamp.fill[0] : 0f);
                    lampCatch[k] = new Vector4(lamp.@catch, 0f, 0f, 0f);
                    lampFill[k] = new Vector4(fc.r, fc.g, fc.b, lamp.fill != null && lamp.fill.Length > 1 ? lamp.fill[1] : 1f);
                    build.Lamps.Add(new CornerLamp { Id = lamp.id, Head = head, Foot = foot, Colour = lc.linear, Power = lamp.power, Light = light });
                }
                // the designed mats of heather and grass breaking the curtain's straight tops
                if (P.tufts != null)
                    foreach (var tf in P.tufts)
                        Part(lamps, made, ClassMat(9f, 0f, tf.slot), $"tuft {tf.name}", Tuft(tf));
                G.Array("_P_LampPos", lampPos);
                G.Array("_P_LampHalo", lampHalo);
                G.Array("_P_LampFill", lampFill);
                G.Array("_P_LampCatch", lampCatch);
                G.Float("_P_LampCount", Mathf.Min(P.lamps.Length, 8));
                G.Float("_P_Mode", 0f);

                // the elements, and what they hide; then the page's hidden boxes and theirs
                build.Elements = new GameObject("Elements");
                build.Elements.transform.SetParent(root.transform, false);
                CornerElements.Run(build);
                var boxes = new List<(Vector3 min, Vector3 max, int cls)>();
                foreach (var h in P.hide)
                    boxes.Add((new Vector3(h.box[0], h.box[1], h.box[2]), new Vector3(h.box[3], h.box[4], h.box[5]), h.cls));
                boxes.AddRange(build.HideBoxes);
                if (boxes.Count > 16)
                    throw new System.Exception($"[LT1ArtPasses] {boxes.Count} hidden boxes: the surface holds 16");
                var hMin = new Vector4[16];
                var hMax = new Vector4[16];
                for (int k = 0; k < boxes.Count; k++)
                {
                    hMin[k] = new Vector4(boxes[k].min.x, boxes[k].min.y, boxes[k].min.z, 0f);
                    hMax[k] = new Vector4(boxes[k].max.x, boxes[k].max.y, boxes[k].max.z, boxes[k].cls);
                }
                G.Array("_P_HideMin", hMin);
                G.Array("_P_HideMax", hMax);
                G.Float("_P_HideCount", boxes.Count);
                return C;
            }
            catch
            {
                C.Cleanup();
                throw;
            }
        }

        /// <summary>Whether a material's shader paints itself in the painted corner (tag "OverstoryPaint"="Own", or a
        /// material float _PaintOwn of 1): it is never swapped for PaintSurface.</summary>
        internal static bool PaintsItself(Material m) =>
            m != null && m.shader != null && (m.GetTag("OverstoryPaint", false) == "Own" || (m.HasFloat("_PaintOwn") && m.GetFloat("_PaintOwn") > 0.5f));

        internal static Texture2D GreyOf(Texture2D src, int k) => Grey(src, k);

        static string PathOf(Transform t)
        {
            string p = t.name;
            for (var q = t.parent; q != null; q = q.parent)
                p = q.name + "/" + p;
            return p;
        }

        /// <summary>
        /// The painted corner: the street stop in the sea fog at 17:50, drawn with one designed surface
        /// (PaintSurface.shader) in place of every material and one pass of air (PaintAir.shader, pass 0), every value
        /// from Paint.json, with the corner's elements (Compose), at its size, anti-aliased and supersampled. Writes
        /// {out}.png, {out}-grey.png and {out}-eighth.png (the value check at 1/8, grey).
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1ArtPasses.Paint
        ///         [-data Assets/Experiments/LT1/ArtDirection/Paint.json] [-out reviews/lt1/art-direction/engine/...]
        ///         [-elements none|name,...]
        /// </summary>
        public static void Paint()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var C = Compose(Cli.Arg("-data", PaintJson), false);
            string outBase = Path.Combine(repo, Cli.Arg("-out", C.Out));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var made = C.Build.Made;
            var targets = new List<RenderTexture>();
            try
            {
                var cam = C.Camera;
                // the colour and the distance, each supersampled and anti-aliased; then the air over both
                int W = C.Width * C.Super, H = C.Height * C.Super;
                RenderTexture Target(int w, int h, int depth, RenderTextureFormat f, RenderTextureReadWrite rw, int aa)
                {
                    var t = new RenderTexture(w, h, depth, f, rw) { antiAliasing = aa, filterMode = FilterMode.Point };
                    t.Create();
                    targets.Add(t);
                    return t;
                }
                var colour = Target(W, H, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear, C.Msaa);
                var dist = Target(W, H, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear, C.Msaa);
                try
                {
                    cam.targetTexture = colour;
                    Shader.SetGlobalFloat("_P_Mode", 0f);
                    for (int i = 0; i < 2; i++)
                        LT1Render.Render(cam, colour);
                    cam.targetTexture = dist;
                    Shader.SetGlobalFloat("_P_Mode", 1f);
                    LT1Render.Render(cam, dist);
                    if (Cli.Arg("-ids", "0") == "1")
                    {
                        // each pixel's slot (r, times 4) and class (g, times 16), for checking which surface is which
                        var ids = Target(W, H, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear, 1);
                        cam.targetTexture = ids;
                        Shader.SetGlobalFloat("_P_Mode", 2f);
                        LT1Render.Render(cam, ids);
                        var idsSmall = Target(C.Width, C.Height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear, 1);
                        Graphics.Blit(ids, idsSmall);
                        var keep = RenderTexture.active;
                        RenderTexture.active = idsSmall;
                        var idTex = new Texture2D(C.Width, C.Height, TextureFormat.RGB24, false, true);
                        idTex.ReadPixels(new Rect(0, 0, C.Width, C.Height), 0, 0);
                        idTex.Apply();
                        RenderTexture.active = keep;
                        made.Add(idTex);
                        File.WriteAllBytes(outBase + "-ids.png", idTex.EncodeToPNG());
                        // and each pixel's street point (x, y, z) and its normal's up, as raw floats, bottom row first
                        var pos = Target(C.Width, C.Height, 24, RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear, 1);
                        cam.targetTexture = pos;
                        Shader.SetGlobalFloat("_P_Mode", 3f);
                        LT1Render.Render(cam, pos);
                        RenderTexture.active = pos;
                        var posTex = new Texture2D(C.Width, C.Height, TextureFormat.RGBAFloat, false, true);
                        posTex.ReadPixels(new Rect(0, 0, C.Width, C.Height), 0, 0);
                        posTex.Apply();
                        RenderTexture.active = keep;
                        made.Add(posTex);
                        File.WriteAllBytes(outBase + "-pos.bin", posTex.GetRawTextureData());
                    }
                }
                finally
                {
                    Shader.SetGlobalFloat("_P_Mode", 0f);
                    cam.targetTexture = null;
                }
                var air = new Material(Shader.Find("Hidden/Overstory/PaintAir")) { hideFlags = HideFlags.DontSave };
                made.Add(air);
                float tanY = Mathf.Tan(0.5f * cam.fieldOfView * Mathf.Deg2Rad), tanX = tanY * W / H;
                air.SetTexture("_P_Dist", dist);
                air.SetVector("_P_Dist_TexelSize", new Vector4(1f / W, 1f / H, W, H));
                air.SetVector("_P_CamPos", cam.transform.position);
                air.SetVector("_P_CamFwd", cam.transform.forward);
                air.SetVector("_P_CamRight", cam.transform.right * tanX);
                air.SetVector("_P_CamUp", cam.transform.up * tanY);
                Debug.Log($"[LT1ArtPasses] camera at {cam.transform.position}, fov {cam.fieldOfView}, physical {cam.usePhysicalProperties}");
                var big = Target(W, H, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB, 1);
                var small = Target(C.Width, C.Height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB, 1);
                Graphics.Blit(colour, big, air, 0);
                big.filterMode = FilterMode.Bilinear;
                Graphics.Blit(big, small); // each pixel the mean of the four under it at 2x

                var prev = RenderTexture.active;
                RenderTexture.active = small;
                var tex = new Texture2D(C.Width, C.Height, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, C.Width, C.Height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                made.Add(tex);
                File.WriteAllBytes(outBase + ".png", tex.EncodeToPNG());
                var grey = Grey(tex, 1);
                made.Add(grey);
                File.WriteAllBytes(outBase + "-grey.png", grey.EncodeToPNG());
                var eighth = Grey(tex, 8);
                made.Add(eighth);
                File.WriteAllBytes(outBase + "-eighth.png", eighth.EncodeToPNG());
                Debug.Log($"[LT1ArtPasses] {outBase}.png");
            }
            finally
            {
                foreach (var t in targets)
                {
                    t.Release();
                    Object.DestroyImmediate(t);
                }
                C.Cleanup();
            }
        }

        /// <summary>One part of a lantern: its mesh drawn with the painted surface for its class, casting no shadow (the
        /// lamp's light sits inside it).</summary>
        static MeshRenderer Part(GameObject parent, List<Object> made, Material material, string name, Mesh mesh)
        {
            made.Add(mesh);
            var g = new GameObject(name);
            g.transform.SetParent(parent.transform, false);
            g.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = g.AddComponent<MeshRenderer>();
            mr.sharedMaterial = material;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            mr.lightProbeUsage = LightProbeUsage.Off;
            mr.reflectionProbeUsage = ReflectionProbeUsage.Off;
            return mr;
        }

        /// <summary>A designed mat of heather or grass along a straight top edge (Paint.json, tufts): a run of rounded
        /// lumps (along, half width, height in metres), each section an arch from just over the lip, draped a little
        /// down its face, back into the top. Its silhouette is the point: few, large shapes, no texture.</summary>
        static Mesh Tuft(PTuft tf)
        {
            Vector3 a = Street(tf.from), b = Street(tf.to);
            Vector3 run = b - a;
            float len = run.magnitude;
            Vector3 along = run / Mathf.Max(len, 1e-4f);
            Vector3 back = Vector3.Cross(along, Vector3.up).normalized;
            int N = Mathf.Max(2, Mathf.CeilToInt(len / 0.04f)), M = 12;
            var v = new List<Vector3>();
            var t = new List<int>();
            for (int i = 0; i <= N; i++)
            {
                float u = len * i / N, h = 0f;
                for (int k = 0; k + 2 < tf.lumps.Length; k += 3)
                {
                    float q = (u - tf.lumps[k]) / Mathf.Max(tf.lumps[k + 1], 1e-3f);
                    if (q * q < 1f)
                        h = Mathf.Max(h, tf.lumps[k + 2] * Mathf.Pow(1f - q * q, tf.shape));
                }
                float sc = Mathf.Clamp01(h / 0.12f);
                for (int j = 0; j <= M; j++)
                {
                    float th = Mathf.PI * j / M;
                    float yb = -tf.overhang * sc + (tf.depth + tf.overhang * sc) * (1f - Mathf.Cos(th)) * 0.5f;
                    float zc = -tf.drop * sc + (h + tf.drop * sc) * Mathf.Sin(th);
                    v.Add(a + along * u + back * yb + Vector3.up * zc);
                }
            }
            for (int i = 0; i < N; i++)
                for (int j = 0; j < M; j++)
                {
                    int p00 = i * (M + 1) + j, p01 = p00 + 1, p10 = p00 + M + 1, p11 = p10 + 1;
                    t.Add(p00); t.Add(p01); t.Add(p10);
                    t.Add(p10); t.Add(p01); t.Add(p11);
                }
            var mesh = new Mesh { name = tf.name, indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.SetVertices(v);
            mesh.SetTriangles(t, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>A square frustum round a vertical axis (Unity metres): from y0 at half width r0 to y1 at r1, flat
        /// faces, its top and bottom closed.</summary>
        static Mesh Frustum(Vector3 axis, float y0, float y1, float r0, float r1)
        {
            var v = new List<Vector3>();
            var n = new List<Vector3>();
            var t = new List<int>();
            Vector3 C(int i, float y, float r)
            {
                float a = (i % 4) * Mathf.PI * 0.5f + Mathf.PI * 0.25f;
                return new Vector3(axis.x + Mathf.Cos(a) * r * Mathf.Sqrt(2f), y, axis.z + Mathf.Sin(a) * r * Mathf.Sqrt(2f));
            }
            void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d)
            {
                var nn = Vector3.Cross(b - a, d - a).normalized;
                int o = v.Count;
                v.AddRange(new[] { a, b, c, d });
                n.AddRange(new[] { nn, nn, nn, nn });
                t.AddRange(new[] { o, o + 1, o + 2, o, o + 2, o + 3 });
            }
            for (int i = 0; i < 4; i++)
                Quad(C(i, y0, r0), C(i, y1, r1), C(i + 1, y1, r1), C(i + 1, y0, r0));
            Quad(C(0, y1, r1), C(3, y1, r1), C(2, y1, r1), C(1, y1, r1));
            Quad(C(0, y0, r0), C(1, y0, r0), C(2, y0, r0), C(3, y0, r0));
            var mesh = new Mesh { name = "lantern part", hideFlags = HideFlags.DontSave };
            mesh.SetVertices(v);
            mesh.SetNormals(n);
            mesh.SetTriangles(t, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>The frame's luminance (from linear light, written back as sRGB) at 1/k size, each pixel the mean of
        /// a k x k block in linear light.</summary>
        static Texture2D Grey(Texture2D src, int k)
        {
            int w = src.width / k, h = src.height / k;
            var px = src.GetPixels();
            var out_ = new Color[w * h];
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                {
                    float acc = 0f;
                    for (int j = 0; j < k; j++)
                        for (int i = 0; i < k; i++)
                        {
                            var c = px[(y * k + j) * src.width + x * k + i].linear;
                            acc += 0.2126f * c.r + 0.7152f * c.g + 0.0722f * c.b;
                        }
                    float g = Mathf.LinearToGammaSpace(acc / (k * k));
                    out_[y * w + x] = new Color(g, g, g, 1f);
                }
            var t = new Texture2D(w, h, TextureFormat.RGB24, false, false);
            t.SetPixels(out_);
            t.Apply();
            return t;
        }
    }
}
