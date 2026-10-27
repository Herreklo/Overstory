using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
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
        [System.Serializable] class PMass { public int slot; public float[] box, nz; }
        [System.Serializable] class PClay { public int wall, ground, roof, glass; public float[] roofNz; }
        [System.Serializable] class PHide { public float[] box; public int cls; }
        [System.Serializable] class PCover { public string name; public int slot; }
        [System.Serializable] class PLantern { public float post, glassH, glassBottom, glassTop, capH, capW; public int glassSlot, metalSlot; }
        [System.Serializable] class PLamp { public string id, srgb; public float[] @base, head, halo; public float power, white, haloStrength; }
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

        /// <summary>
        /// The painted corner: the street stop in the sea fog at 17:50, drawn with one designed surface
        /// (PaintSurface.shader) in place of every material and one pass of air (PaintAir.shader), every value from
        /// Paint.json, at its size, anti-aliased and supersampled. Writes {out}.png, {out}-grey.png and {out}-eighth.png
        /// (the value check at 1/8, grey).
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1ArtPasses.Paint
        ///         [-data Assets/Experiments/LT1/ArtDirection/Paint.json] [-out reviews/lt1/art-direction/engine/...]
        /// </summary>
        public static void Paint()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string unity = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var P = JsonUtility.FromJson<PaintData>(File.ReadAllText(Path.Combine(unity, Cli.Arg("-data", "Assets/Experiments/LT1/ArtDirection/Paint.json"))));
            string outBase = Path.Combine(repo, Cli.Arg("-out", P.@out));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var made = new List<Object>();
            var root = new GameObject("painted") { hideFlags = HideFlags.DontSave };
            var meshes = new List<(MeshFilter mf, Mesh mesh)>();
            var renderers = new List<(Renderer r, Material[] mats, MaterialPropertyBlock block, bool on)>();
            var lights = new List<(Light l, bool on)>();
            var features = new Dictionary<ScriptableRendererFeature, bool>();
            var rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
            Camera cam = null;
            UniversalAdditionalCameraData camData = null;
            bool camPost = false;
            CameraClearFlags camClear = CameraClearFlags.Skybox;
            Color camBack = Color.black;
            var sky = RenderSettings.skybox;
            var targets = new List<RenderTexture>();
            try
            {
                // the houses drawn, their clay cut out of the corner's in memory (as LT1Houses.Still does)
                string dir = Path.Combine(repo, "cache/houses");
                var all = JsonUtility.FromJson<HRows>(File.ReadAllText(Path.Combine(dir, "houses.json")));
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
                foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
                {
                    if (mf.sharedMesh == null || !mf.name.StartsWith("buildings_"))
                        continue;
                    var kept = (Mesh)cutClay.Invoke(null, new object[] { mf, cut });
                    if (kept == null)
                        continue;
                    made.Add(kept);
                    meshes.Add((mf, mf.sharedMesh));
                    mf.sharedMesh = kept;
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
                cam = stage.view;

                // every renderer drawn with the painted surface, by what it is; the sky's dome and anything not a mesh off
                var paint = new Material(Shader.Find("Hidden/Overstory/PaintSurface")) { hideFlags = HideFlags.DontSave };
                made.Add(paint);
                var tally = new Dictionary<string, int>();
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    var block = new MaterialPropertyBlock();
                    if (r.HasPropertyBlock())
                        r.GetPropertyBlock(block);
                    renderers.Add((r, r.sharedMaterials, block, r.enabled));
                    if (!r.enabled || r.sharedMaterials.Length == 0)
                        continue;
                    float cls = ClassOf(r.sharedMaterial);
                    string key = $"{cls} {(r.sharedMaterial != null && r.sharedMaterial.shader != null ? r.sharedMaterial.shader.name : "-")} {r.GetType().Name}";
                    tally[key] = tally.TryGetValue(key, out int n) ? n + 1 : 1;
                    string shaderName = r.sharedMaterial != null && r.sharedMaterial.shader != null ? r.sharedMaterial.shader.name : "";
                    if (cls == 5f || !(r is MeshRenderer) || System.Array.Exists(P.off ?? new string[0], o => shaderName.Contains(o)))
                    {
                        r.enabled = false;
                        continue;
                    }
                    var mats = new Material[r.sharedMaterials.Length];
                    for (int i = 0; i < mats.Length; i++)
                        mats[i] = paint;
                    var mine = new MaterialPropertyBlock();
                    mine.SetFloat(ClassId, cls);
                    r.sharedMaterials = mats;
                    r.SetPropertyBlock(mine);
                }
                foreach (var kv in tally)
                    Debug.Log($"[LT1ArtPasses] renderers {kv.Key}: {kv.Value}");
                foreach (var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
                {
                    lights.Add((l, l.enabled));
                    l.enabled = false;
                }
                if (rendererData != null)
                    foreach (var f in rendererData.rendererFeatures)
                        if (f != null)
                        {
                            features[f] = f.isActive;
                            f.SetActive(false);
                        }

                foreach (var m in houseMeshes)
                {
                    var g = new GameObject(m.name);
                    g.transform.SetParent(root.transform, false);
                    g.AddComponent<MeshFilter>().sharedMesh = m;
                    var mr = g.AddComponent<MeshRenderer>();
                    mr.sharedMaterial = paint;
                    mr.shadowCastingMode = ShadowCastingMode.On;
                    var b = new MaterialPropertyBlock();
                    b.SetFloat(ClassId, 2f);
                    mr.SetPropertyBlock(b);
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
                    Shader.SetGlobalVector(g.name, v);
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
                Shader.SetGlobalVectorArray("_P_Albedo", albedo);
                Shader.SetGlobalVectorArray("_P_SurfB", surfB);
                Shader.SetGlobalVectorArray("_P_Veil", veils);
                var mMin = new Vector4[16];
                var mMax = new Vector4[16];
                var mN = new Vector4[16];
                for (int k = 0; k < P.masses.Length; k++)
                {
                    var b = P.masses[k].box;
                    mMin[k] = new Vector4(b[0], b[1], b[2], P.masses[k].slot);
                    mMax[k] = new Vector4(b[3], b[4], b[5], 1f);
                    mN[k] = new Vector4(P.masses[k].nz[0], P.masses[k].nz[1], 0f, 0f);
                }
                Shader.SetGlobalVectorArray("_P_MassMin", mMin);
                Shader.SetGlobalVectorArray("_P_MassMax", mMax);
                Shader.SetGlobalVectorArray("_P_MassN", mN);
                Shader.SetGlobalFloat("_P_MassCount", P.masses.Length);
                var hMin = new Vector4[4];
                var hMax = new Vector4[4];
                for (int k = 0; k < P.hide.Length; k++)
                {
                    var b = P.hide[k].box;
                    hMin[k] = new Vector4(b[0], b[1], b[2], 0f);
                    hMax[k] = new Vector4(b[3], b[4], b[5], P.hide[k].cls);
                }
                Shader.SetGlobalVectorArray("_P_HideMin", hMin);
                Shader.SetGlobalVectorArray("_P_HideMax", hMax);
                Shader.SetGlobalFloat("_P_HideCount", P.hide.Length);
                Shader.SetGlobalVector("_P_Clay", new Vector4(P.clay.wall, P.clay.ground, P.clay.roof, P.clay.glass));
                Shader.SetGlobalVector("_P_ClayRoof", new Vector4(P.clay.roofNz[0], P.clay.roofNz[1], 0f, 0f));
                Shader.SetGlobalVector("_P_Lantern", new Vector4(P.lantern.glassSlot, P.lantern.metalSlot, 0f, 0f));
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
                Shader.SetGlobalVectorArray("_P_Coats", coats);
                Shader.SetGlobalFloat("_P_Date", all.date);

                // the lamps at their places: each a 1955 lantern (post, glass, cap) with its light, shadowed
                var lampPos = new Vector4[8];
                var lampHalo = new Vector4[8];
                float lampReach = globals.TryGetValue("_P_Pool", out var pool) ? pool.w : 16f;
                var lt = P.lantern;
                for (int k = 0; k < P.lamps.Length && k < 8; k++)
                {
                    var lamp = P.lamps[k];
                    Vector3 foot = Street(lamp.@base), head = Street(lamp.head);
                    float glass0 = head.y - 0.5f * lt.glassH, glass1 = head.y + 0.5f * lt.glassH;
                    Part(root, made, paint, $"lamp {lamp.id} post", Frustum(foot, foot.y, glass0, 0.5f * lt.post, 0.5f * lt.post), 8f, 0f);
                    Part(root, made, paint, $"lamp {lamp.id} glass", Frustum(foot, glass0, glass1, 0.5f * lt.glassBottom, 0.5f * lt.glassTop), 7f, lamp.white);
                    Part(root, made, paint, $"lamp {lamp.id} cap", Frustum(foot, glass1, glass1 + lt.capH, 0.5f * lt.capW, 0.01f), 8f, 0f);
                    var lg = new GameObject($"lamp {lamp.id} light");
                    lg.transform.SetParent(root.transform, false);
                    lg.transform.position = head;
                    var light = lg.AddComponent<Light>();
                    light.type = LightType.Point;
                    ColorUtility.TryParseHtmlString(lamp.srgb, out var lc);
                    light.color = lc;
                    light.intensity = lamp.power;
                    light.range = lampReach;
                    light.shadows = LightShadows.Soft;
                    light.shadowNearPlane = 0.05f;
                    var hc = LinearOf(lamp.srgb) * lamp.haloStrength;
                    lampPos[k] = new Vector4(head.x, head.y, head.z, lamp.halo[0]);
                    lampHalo[k] = new Vector4(hc.r, hc.g, hc.b, lamp.halo[1]);
                }
                Shader.SetGlobalVectorArray("_P_LampPos", lampPos);
                Shader.SetGlobalVectorArray("_P_LampHalo", lampHalo);
                Shader.SetGlobalFloat("_P_LampCount", Mathf.Min(P.lamps.Length, 8));

                // the colour and the distance, each supersampled and anti-aliased; then the air over both
                camData = cam.GetComponent<UniversalAdditionalCameraData>();
                camPost = camData != null && camData.renderPostProcessing;
                if (camData != null)
                    camData.renderPostProcessing = false;
                camClear = cam.clearFlags;
                camBack = cam.backgroundColor;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = Color.clear;
                RenderSettings.skybox = null;
                int W = P.width * P.super, H = P.height * P.super;
                RenderTexture Target(int w, int h, int depth, RenderTextureFormat f, RenderTextureReadWrite rw, int aa)
                {
                    var t = new RenderTexture(w, h, depth, f, rw) { antiAliasing = aa, filterMode = FilterMode.Point };
                    t.Create();
                    targets.Add(t);
                    return t;
                }
                var colour = Target(W, H, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear, P.msaa);
                var dist = Target(W, H, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear, P.msaa);
                var was = cam.targetTexture;
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
                        var idsSmall = Target(P.width, P.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear, 1);
                        Graphics.Blit(ids, idsSmall);
                        var keep = RenderTexture.active;
                        RenderTexture.active = idsSmall;
                        var idTex = new Texture2D(P.width, P.height, TextureFormat.RGB24, false, true);
                        idTex.ReadPixels(new Rect(0, 0, P.width, P.height), 0, 0);
                        idTex.Apply();
                        RenderTexture.active = keep;
                        made.Add(idTex);
                        File.WriteAllBytes(outBase + "-ids.png", idTex.EncodeToPNG());
                        // and each pixel's street point (x, y, z) and its normal's up, as raw floats, bottom row first
                        var pos = Target(P.width, P.height, 24, RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear, 1);
                        cam.targetTexture = pos;
                        Shader.SetGlobalFloat("_P_Mode", 3f);
                        LT1Render.Render(cam, pos);
                        RenderTexture.active = pos;
                        var posTex = new Texture2D(P.width, P.height, TextureFormat.RGBAFloat, false, true);
                        posTex.ReadPixels(new Rect(0, 0, P.width, P.height), 0, 0);
                        posTex.Apply();
                        RenderTexture.active = keep;
                        made.Add(posTex);
                        File.WriteAllBytes(outBase + "-pos.bin", posTex.GetRawTextureData());
                    }
                }
                finally
                {
                    Shader.SetGlobalFloat("_P_Mode", 0f);
                    cam.targetTexture = was;
                }
                var air = new Material(Shader.Find("Hidden/Overstory/PaintAir")) { hideFlags = HideFlags.DontSave };
                made.Add(air);
                float tanY = Mathf.Tan(0.5f * cam.fieldOfView * Mathf.Deg2Rad), tanX = tanY * W / H;
                air.SetTexture("_P_Dist", dist);
                air.SetVector("_P_CamPos", cam.transform.position);
                air.SetVector("_P_CamFwd", cam.transform.forward);
                air.SetVector("_P_CamRight", cam.transform.right * tanX);
                air.SetVector("_P_CamUp", cam.transform.up * tanY);
                Debug.Log($"[LT1ArtPasses] camera at {cam.transform.position}, fov {cam.fieldOfView}, physical {cam.usePhysicalProperties}");
                var big = Target(W, H, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB, 1);
                var small = Target(P.width, P.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB, 1);
                Graphics.Blit(colour, big, air);
                big.filterMode = FilterMode.Bilinear;
                Graphics.Blit(big, small); // each pixel the mean of the four under it at 2x

                var prev = RenderTexture.active;
                RenderTexture.active = small;
                var tex = new Texture2D(P.width, P.height, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, P.width, P.height), 0, 0);
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
                foreach (var kv in features)
                    kv.Key.SetActive(kv.Value);
                foreach (var (l, on) in lights)
                    if (l != null)
                        l.enabled = on;
                foreach (var (r, mats, block, on) in renderers)
                {
                    if (r == null)
                        continue;
                    r.sharedMaterials = mats;
                    r.SetPropertyBlock(block.isEmpty ? null : block);
                    r.enabled = on;
                }
                foreach (var (mf, mesh) in meshes)
                    mf.sharedMesh = mesh;
                if (cam != null)
                {
                    if (camData != null)
                        camData.renderPostProcessing = camPost;
                    cam.clearFlags = camClear;
                    cam.backgroundColor = camBack;
                }
                RenderSettings.skybox = sky;
                Object.DestroyImmediate(root);
                foreach (var o in made)
                    if (o != null)
                        Object.DestroyImmediate(o);
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>One part of a lantern: its mesh drawn with the painted surface as a class, casting no shadow (the
        /// lamp's light sits inside it).</summary>
        static void Part(GameObject root, List<Object> made, Material paint, string name, Mesh mesh, float cls, float emit)
        {
            made.Add(mesh);
            var g = new GameObject(name);
            g.transform.SetParent(root.transform, false);
            g.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = g.AddComponent<MeshRenderer>();
            mr.sharedMaterial = paint;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            var b = new MaterialPropertyBlock();
            b.SetFloat(ClassId, cls);
            b.SetFloat("_Emit", emit);
            mr.SetPropertyBlock(b);
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
