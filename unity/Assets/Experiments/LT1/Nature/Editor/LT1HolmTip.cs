using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The Holm tip's rock (blender/parts/rock/kit) beside house 107, the street's way:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1HolmTip.Run -tipRound k01
    ///         [-tipViews eye,street] [-tipWays P,Pc] [-tipLights overcast,lowsun]
    ///
    /// Reads what blender/parts/rock/kit/run/render.sh copied into HolmTip/Generated/&lt;name&gt;/ (the house's build and
    /// each part's: levels, page, house.json, paint.json), builds HolmTip.unity, and writes each still into
    /// cache/rock/kit/renders/&lt;round&gt;/ twice: with the rock (tip-) and without it (floor-: the house alone in the same
    /// frame). Where the parts stand and the eye view are kit.json's `beside`. Everything else is the street's own code,
    /// called as it is (LT1Street's import, materials, one city mesh, orientation, lights and capture, by reflection),
    /// with its ground, sun, volume, camera and renderer set as LT1Street.Run sets them, so a rock is judged beside the
    /// house on the house's terms.
    /// </summary>
    public static class LT1HolmTip
    {
        const string Dir = "Assets/Experiments/LT1/Nature/HolmTip";
        const BindingFlags Any = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static;
        static readonly Type St = typeof(LT1Street);

        [Serializable] class Placed { public string part; public float[] at; }
        [Serializable] class Eye { public float[] from, look; public float fov; }
        [Serializable] class TipMat { public string name; public float L; public float smooth; public string normal, ao; }
        [Serializable] class TipView { public string name, level; public float[] pos, target; public float fov; }
        [Serializable] class TipMats { public TipMat[] mats; public TipView[] views; public float sunOff; }
        [Serializable] class Beside { public string house; public Placed[] parts; public Eye eye; }
        [Serializable] class Kit { public Beside beside; }

        class Build { public string name, gen; public object house, paint; public Dictionary<string, Material> mats; public GameObject root; public Dictionary<string, GameObject> levels = new Dictionary<string, GameObject>(); }

        struct View { public string name, level; public Vector3 pos, target; public float fov; }

        static object Call(string name, params object[] a) => St.GetMethod(name, Any).Invoke(null, a);
        static object Static(string name) => St.GetField(name, Any).GetValue(null);
        static T Get<T>(object o, string f) => o == null ? default : (T)o.GetType().GetField(f).GetValue(o);
        static object Json(string path, string type) => JsonUtility.FromJson(File.ReadAllText(path), St.GetNestedType(type, BindingFlags.NonPublic));
        static Vector3 ToUnity(Vector3 s) => (Vector3)Call("ToUnity", s);
        static Vector3 V(float[] a) => new Vector3(a[0], a[1], a[2]);

        public static void Run()
        {
            string round = Arg("-tipRound") ?? "k01";
            var only = (Arg("-tipViews") ?? "eye,street").Split(',');
            var ways = (Arg("-tipWays") ?? "P,Pc").Split(',');
            var lights = (Arg("-tipLights") ?? "overcast,lowsun").Split(',');
            float sunOff = float.Parse(Arg("-tipSunOff") ?? "45", System.Globalization.CultureInfo.InvariantCulture);
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var B = JsonUtility.FromJson<Kit>(File.ReadAllText(Path.Combine(root, "blender", "parts", "rock", "kit", "kit.json"))).beside;
            string outDir = Path.Combine(root, "cache", "rock", "kit", "renders", round);
            Directory.CreateDirectory(outDir);
            var levelNames = (string[])Static("Levels");

            foreach (var path in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { Dir }).Select(AssetDatabase.GUIDToAssetPath))
                if (path.EndsWith(".mat") || path.EndsWith(".asset"))  // never a model whose materials are its own
                    AssetDatabase.DeleteAsset(path);
            var builds = new List<Build>();
            foreach (var name in new[] { B.house }.Concat(B.parts.Select(p => p.part)))
            {
                var b = new Build { name = name, gen = $"{Dir}/Generated/{name}" };
                Call("Import", b.gen);
                b.house = Json(Path.Combine(b.gen, "house.json"), "House");
                b.paint = Json(Path.Combine(b.gen, "paint.json"), "Paint");
                b.mats = (Dictionary<string, Material>)Call("Materials", b.gen, b.paint, b.house);
                // a sculpted part (bake.py's high-poly bake) wears its near level's own normal, as its street level
                // wears the street's
                var nearN = AssetDatabase.LoadAssetAtPath<Texture2D>($"{b.gen}/near-normal.png");
                if (nearN != null)
                    foreach (var kv in b.mats.Where(kv => kv.Key.Split('-')[1] == "near"))
                    {
                        kv.Value.SetTexture("_StreetN", nearN);
                        kv.Value.SetFloat("_Street", 1);
                        kv.Value.EnableKeyword("_OS_STREET");
                    }
                builds.Add(b);
            }
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            foreach (var b in builds)
            {
                b.root = new GameObject(b.name == B.house ? $"House {b.name}" : $"Rock {b.name}");
                foreach (var level in levelNames)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{b.gen}/house-{level}.fbx");
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                    go.transform.SetParent(b.root.transform, false);
                    // a part's level is one object, which the import makes the model's root: its Blender name back
                    // (`<level>_<material>`), as the street's code reads it
                    if (go.GetComponent<MeshRenderer>() != null)
                        go.name = $"{level}_{Get<string>(Get<Array>(b.paint, "mats").GetValue(0), "name")}";
                    b.levels[level] = go;
                }
            }
            // the house as the street orients it; each part the same way round (their FBX axes are the same), at its place
            var h = builds[0];
            Call("Orient", h.root, h.levels["near"]);
            for (int k = 1; k < builds.Count; k++)
            {
                var b = builds[k];
                b.root.transform.SetPositionAndRotation(ToUnity(V(B.parts[k - 1].at)), h.root.transform.rotation);
                b.root.transform.localScale = h.root.transform.localScale;
            }
            Physics.SyncTransforms();
            foreach (var b in builds)
            {
                foreach (var r in b.root.GetComponentsInChildren<MeshRenderer>(true))
                    r.shadowCastingMode = ShadowCastingMode.TwoSided;
                b.levels["city"] = (GameObject)Call("OneMesh", b.levels["city"], b.paint, b.gen);
            }

            var size = Get<float[]>(h.house, "size");
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(8, 1, 8);
            ground.transform.position = ToUnity(new Vector3(size[0] / 2, -10, 0));
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            float gy = (float)Call("LToY", (float)St.GetField("GroundL", Any).GetRawConstantValue());
            gm.SetFloat("_Smoothness", (float)St.GetField("GroundSmooth", Any).GetRawConstantValue());
            AssetDatabase.CreateAsset(gm, $"{Dir}/Generated/mat-ground.mat");
            ground.GetComponent<Renderer>().sharedMaterial = gm;

            // -tipGrey 1: the target frame's grey-box (tip.py), the tip's masses around 107 in their greys, the parts and
            // the street's ground away; the masses come in 107's frame, so they stand as a part stands, at its origin
            bool grey = Arg("-tipGrey") == "1";
            TipMats tipRec = null;
            if (grey)
            {
                string tg = $"{Dir}/Generated/tip";
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{tg}/tip.fbx");
                mi.globalScale = 1;
                mi.importCameras = false;
                mi.importLights = false;
                mi.animationType = ModelImporterAnimationType.None;
                mi.importNormals = ModelImporterNormals.Import;
                mi.importTangents = ModelImporterTangents.CalculateMikk;
                mi.SaveAndReimport();
                var tip = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{tg}/tip.fbx"));
                tip.transform.SetPositionAndRotation(Vector3.zero, h.root.transform.rotation);
                tip.transform.localScale = h.root.transform.localScale;
                var greys = new Dictionary<string, Material>();
                tipRec = JsonUtility.FromJson<TipMats>(File.ReadAllText(Path.Combine(root, "unity", tg, "tip.json")));
                // the tip's low sun is the site's (tip.py), unless asked for another
                if (Arg("-tipSunOff") == null)
                    sunOff = tipRec.sunOff;
                foreach (var m in tipRec.mats)
                {
                    var g = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                    g.SetColor("_BaseColor", (Color)Call("Lin", (float)Call("LToY", m.L), null));
                    g.SetFloat("_Smoothness", m.smooth);
                    // a baked game mesh's page (carve.py): its normal in tangent space on its own UV, and its AO
                    if (!string.IsNullOrEmpty(m.normal))
                    {
                        var ti = (TextureImporter)AssetImporter.GetAtPath($"{tg}/{m.normal}");
                        ti.textureType = TextureImporterType.NormalMap;
                        ti.SaveAndReimport();
                        g.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{tg}/{m.normal}"));
                        g.EnableKeyword("_NORMALMAP");
                    }
                    if (!string.IsNullOrEmpty(m.ao))
                    {
                        var ti = (TextureImporter)AssetImporter.GetAtPath($"{tg}/{m.ao}");
                        ti.sRGBTexture = false;
                        ti.SaveAndReimport();
                        g.SetTexture("_OcclusionMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{tg}/{m.ao}"));
                        g.SetFloat("_OcclusionStrength", 1f);
                        g.EnableKeyword("_OCCLUSIONMAP");
                    }
                    AssetDatabase.CreateAsset(g, $"{Dir}/Generated/grey-{m.name}.mat");
                    greys[m.name] = g;
                }
                foreach (var r in tip.GetComponentsInChildren<MeshRenderer>(true))
                {
                    r.sharedMaterials = r.sharedMaterials.Select(m => m != null && greys.TryGetValue(m.name, out var g) ? g : m).ToArray();
                    r.shadowCastingMode = ShadowCastingMode.TwoSided;
                }
                ground.SetActive(false);
            }

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            sunGo.AddComponent<UniversalAdditionalLightData>().softShadowQuality = SoftShadowQuality.Low;
            sun.shadowBias = 1f;
            sun.shadowNormalBias = 1f;

            var volume = new GameObject("Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.Add<Tonemapping>(true).mode.Override(TonemappingMode.Neutral);
            var adjust = profile.Add<ColorAdjustments>(true);
            AssetDatabase.CreateAsset(profile, $"{Dir}/Generated/tip-volume.asset");
            volume.sharedProfile = profile;

            var camGo = new GameObject("Camera");
            var cam = camGo.AddComponent<Camera>();
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = grey ? 2000f : 500f;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, "Assets/Experiments/LT1/Nature/HolmTip.unity");
            AssetDatabase.SaveAssets();
            if (Arg("-tipJudge") == "1")
            {
                Judge(builds, B, only, ways, outDir, gm, sun, cam, profile, adjust);
                return;
            }

            // the street's street stop as it is; its eye view taken back to the first part (kit.json beside.eye)
            var views = new List<View>();
            foreach (var v in ((Array)Call("Views", size[0], size[1])).Cast<object>())
                if (Get<string>(v, "name") == "street")
                    views.Add(new View { name = "street", level = Get<string>(v, "level"), pos = Get<Vector3>(v, "pos"), target = Get<Vector3>(v, "target"), fov = Get<float>(v, "fov") });
            var eyePos = V(B.parts[0].at) + V(B.eye.from);
            views.Insert(0, new View { name = "eye", level = "near", pos = eyePos, target = eyePos + V(B.eye.look), fov = B.eye.fov });
            // the target frame's own views of the tip (kit.json tip.views, in 107's frame by tip.py)
            foreach (var v in tipRec?.views ?? new TipView[0])
                views.Add(new View { name = v.name, level = v.level, pos = V(v.pos), target = V(v.target), fov = v.fov });

            var back = (Color)Static("Back");
            var lightingT = St.GetNestedType("Lighting", BindingFlags.NonPublic);
            var rocks = builds.Skip(1).Select(b => b.root).ToList();
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
            try
            {
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                foreach (object light in (Array)Static("Lights"))
                {
                    string ln = Get<string>(light, "name");
                    if (!lights.Contains(ln))
                        continue;
                    foreach (var view in views.Where(v => only.Contains(v.name)))
                    {
                        foreach (var b in builds)
                        foreach (var kv in b.levels)
                            kv.Value.SetActive(kv.Key == view.level);
                        cam.transform.SetPositionAndRotation(ToUnity(view.pos), Quaternion.LookRotation(ToUnity(view.target - view.pos), Vector3.up));
                        cam.fieldOfView = view.fov;
                        urp.shadowCascadeCount = grey ? 4 : 1;
                        urp.mainLightShadowmapResolution = 4096;
                        urp.shadowDistance = grey ? 250f : (view.target - view.pos).magnitude + 8f;
                        foreach (var way in ways)
                        {
                            // the scene's light is the house's (its paint.json), as the street's
                            var own = Get<Array>(h.paint, "lights")?.Cast<object>().FirstOrDefault(e => Get<string>(e, "light") == ln);
                            var col = way == "Pc" ? Get<Array>(Get<object>(h.paint, "colour"), "lights")?.Cast<object>().FirstOrDefault(e => Get<string>(e, "light") == ln) : null;
                            object l = own != null ? Call("Own", light, own) : light;
                            if (ln == "lowsun")
                                lightingT.GetField("azimuth").SetValue(l, new Vector2(Mathf.Sin(sunOff * Mathf.Deg2Rad), -Mathf.Cos(sunOff * Mathf.Deg2Rad)));
                            Call("Light", sun, l, col);
                            cam.backgroundColor = (Color)Call("Lin", back.linear.r, Get<float[]>(col, "background"));
                            gm.SetColor("_BaseColor", (Color)Call("Lin", gy, Get<float[]>(col, "floor")));
                            adjust.postExposure.Override(own != null ? Get<float>(own, "exposure") : Get<float>(light, "exposure"));
                            foreach (var b in builds)
                                Call("Assign", b.levels[view.level], b.mats, way, (string)Call("MatLevel", view.level));
                            foreach (var with in grey ? new[] { false } : new[] { true, false })
                            {
                                foreach (var r in rocks)
                                    r.SetActive(with);
                                string file = Path.Combine(outDir, $"{(grey ? "grey" : with ? "tip" : "floor")}-{view.name}-{ln}-{way}.png");
                                Call("Capture", cam, file);
                                Debug.Log($"[LT1HolmTip] {file}");
                            }
                            foreach (var r in rocks)
                                r.SetActive(true);
                        }
                    }
                }
            }
            finally
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = urpWas;
            }
            // the cost line: each build's triangles and draws a level, its materials, and its page on the GPU at full as
            // the street's timing counts it (every texture but the strokes, which every house shares)
            long Bytes(Texture2D t)
            {
                long n = 0;
                for (int m = 0; m < t.mipmapCount; m++)
                    n += (long)UnityEngine.Experimental.Rendering.GraphicsFormatUtility.ComputeMipmapSize(
                        Math.Max(1, t.width >> m), Math.Max(1, t.height >> m), t.graphicsFormat);
                return n;
            }
            foreach (var b in builds)
            {
                var tris = string.Join(", ", b.levels.Select(kv => $"{kv.Key} {kv.Value.GetComponentsInChildren<MeshFilter>(true).Sum(f => f.sharedMesh.triangles.Length / 3)} tris {kv.Value.GetComponentsInChildren<MeshRenderer>(true).Length} draws"));
                var tex = b.mats.Values.SelectMany(m => m.GetTexturePropertyNames().Select(m.GetTexture)).OfType<Texture2D>().Distinct().ToList();
                long page = tex.Where(t => !t.name.StartsWith("paint-")).Sum(Bytes), shared = tex.Where(t => t.name.StartsWith("paint-")).Sum(Bytes);
                Debug.Log($"[LT1HolmTip] cost {b.name}: {tris}; {Get<Array>(b.paint, "mats").Length} materials; page {page / 1048576.0:F1} MB " +
                          $"({string.Join(", ", tex.Where(t => !t.name.StartsWith("paint-")).Select(t => $"{t.name} {t.width} {t.graphicsFormat}"))}), strokes {shared / 1048576.0:F1} MB");
            }
        }

        [Serializable] class JudgeView { public string name; public float[] pos, target, toSun; public float fov; }
        [Serializable] class JudgeRec { public JudgeView[] views; public float rock, rough, skyE, sunE; public float[] ground, sky, sunRGB; }

        /// <summary>
        /// -tipJudge 1: each part alone in stage 2's grey (game.py's judge.json: sculpt.py's clay, sun, sky and views in
        /// the levels' frame), its near level as the game draws it, with its baked normal (way N) or bare (way M), the
        /// house away and the style's grade off: the game mesh's planes judged beside the high-poly's stills in the same
        /// light. Writes judge-&lt;part&gt;-&lt;view&gt;-&lt;way&gt;.png.
        /// </summary>
        static void Judge(List<Build> builds, Beside B, string[] only, string[] ways, string outDir, Material gm, Light sun,
                          Camera cam, VolumeProfile profile, ColorAdjustments adjust)
        {
            builds[0].root.SetActive(false);
            foreach (var c in profile.components)
                c.active = c is Tonemapping || c is ColorAdjustments;
            adjust.postExposure.Override(0f);
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
            try
            {
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = (30f, 1, 4096);
                for (int k = 1; k < builds.Count; k++)
                {
                    var b = builds[k];
                    var J = JsonUtility.FromJson<JudgeRec>(File.ReadAllText(Path.Combine(b.gen, "judge.json")));
                    var at = V(B.parts[k - 1].at);
                    foreach (var o in builds.Skip(1))
                        o.root.SetActive(o == b);
                    foreach (var kv in b.levels)
                        kv.Value.SetActive(kv.Key == "near");
                    // URP's Lit reads its normal on UV0 (metres in the plane); the page is UV1, the same charts moved and
                    // scaled (never turned), so the imported tangents hold on it
                    foreach (var mf in b.levels["near"].GetComponentsInChildren<MeshFilter>(true))
                    {
                        var m = UnityEngine.Object.Instantiate(mf.sharedMesh);
                        var page = new List<Vector2>();
                        m.GetUVs(1, page);
                        m.SetUVs(0, page);
                        mf.sharedMesh = m;
                    }
                    var mats = ways.ToDictionary(w => w, w =>
                    {
                        var m = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                        m.SetColor("_BaseColor", new Color(J.rock, J.rock, J.rock).gamma);
                        m.SetFloat("_Smoothness", 1f - J.rough);
                        if (w == "N")
                        {
                            m.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{b.gen}/near-normal.png"));
                            m.EnableKeyword("_NORMALMAP");
                        }
                        AssetDatabase.CreateAsset(m, $"{Dir}/Generated/judge-{b.name}-{w}.mat");
                        return m;
                    });
                    // Cycles' sun is irradiance and its sky radiance; URP's Lambert carries no 1/π, its ambient is radiance
                    gm.SetColor("_BaseColor", new Color(J.ground[0], J.ground[1], J.ground[2]).gamma);
                    sun.color = new Color(J.sunRGB[0], J.sunRGB[1], J.sunRGB[2]).gamma;
                    sun.intensity = J.sunE / Mathf.PI;
                    sun.shadowStrength = 1f;
                    var sky = new Color(J.sky[0] * J.skyE, J.sky[1] * J.skyE, J.sky[2] * J.skyE);
                    RenderSettings.ambientMode = AmbientMode.Trilight;
                    RenderSettings.ambientSkyColor = sky.gamma;
                    RenderSettings.ambientEquatorColor = sky.gamma;
                    cam.backgroundColor = sky.gamma;
                    foreach (var v in J.views.Where(v => only.Contains(v.name)))
                    {
                        var lit = J.sunE / Mathf.PI * v.toSun[2];
                        RenderSettings.ambientGroundColor = new Color(J.ground[0] * (lit + sky.r), J.ground[1] * (lit + sky.g), J.ground[2] * (lit + sky.b)).gamma;
                        DynamicGI.UpdateEnvironment();
                        sun.transform.rotation = Quaternion.LookRotation(-ToUnity(V(v.toSun)), Vector3.up);
                        cam.transform.SetPositionAndRotation(ToUnity(at + V(v.pos)), Quaternion.LookRotation(ToUnity(V(v.target) - V(v.pos)), Vector3.up));
                        cam.fieldOfView = v.fov;
                        foreach (var w in ways)
                        {
                            foreach (var r in b.levels["near"].GetComponentsInChildren<MeshRenderer>(true))
                                r.sharedMaterials = r.sharedMaterials.Select(_ => mats[w]).ToArray();
                            string file = Path.Combine(outDir, $"judge-{b.name}-{v.name}-{w}.png");
                            Call("Capture", cam, file);
                            Debug.Log($"[LT1HolmTip] {file}");
                        }
                    }
                }
            }
            finally
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = urpWas;
            }
        }

        static string Arg(string name) => (string)Call("Arg", name);
    }
}
