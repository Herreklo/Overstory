using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using Overstory.Growth;
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
    /// house on the house's terms. Where ground.py's ground is there (HolmTip/Generated/ground), it takes the street's
    /// ground's place: the tip's community as the growth's tufts, over its ground map.
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
        [Serializable] class Beside { public string house; public Placed[] parts; public Eye eye, high, iso; }
        [Serializable] class Kit { public Beside beside; }

        [Serializable] class GKind { public string species; public int variant; public string[] levels; public float radius, hue; public float[] @base, tip, damp, seed; public int first, count; }
        [Serializable] class GDraw { public float[] to; public float fade, thinFrom, keepMin, widen; }
        [Serializable] class GLook { public float upNormal, calm, lamp, veil, root, tipLift, hueDetail, wet, shrinkBand, minPx; }
        [Serializable] class GroundRec { public float[] box; public string[] maps; public GDraw draw; public GLook look; public int stride; public GKind[] kinds; }

        class Build { public string name, gen; public object house, paint; public Dictionary<string, Material> mats; public GameObject root, foot; public Dictionary<string, GameObject> levels = new Dictionary<string, GameObject>(); }

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
                // a part's foot (foot.py): its grass and the small stones beside it, one mesh in vertex colour at the
                // part's origin, the same at every level
                if (AssetImporter.GetAtPath($"{b.gen}/foot.fbx") is ModelImporter fi)
                {
                    fi.materialImportMode = ModelImporterMaterialImportMode.None;
                    fi.importNormals = ModelImporterNormals.Import;
                    fi.importTangents = ModelImporterTangents.None;
                    fi.importCameras = false;
                    fi.importLights = false;
                    fi.animationType = ModelImporterAnimationType.None;
                    fi.meshCompression = ModelImporterMeshCompression.Off;
                    fi.globalScale = 1;
                    fi.SaveAndReimport();
                    b.foot = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{b.gen}/foot.fbx"));
                    b.foot.transform.SetParent(b.root.transform, false);
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
                foreach (var b in builds.Where(b => b.foot != null))
                    b.foot.SetActive(false);  // stage 2's grey judges the part alone
                Judge(builds, B, only, ways, outDir, gm, sun, cam, profile, adjust);
                return;
            }

            // the tip's ground (ground.py), in the street's ground's place; built after the scene is saved, so the scene
            // keeps none of its instances
            GrowthTufts turf = null;
            GameObject tipGround = null;
            Dictionary<string, Material> groundMats = null;
            if (!grey && File.Exists(Path.Combine(root, "unity", Dir, "Generated", "ground", "ground.json")))
            {
                (tipGround, groundMats, turf) = Ground($"{Dir}/Generated/ground", root, ways);
                ground.SetActive(false);
            }

            // the street's street stop as it is; its eye view taken back to the first part (kit.json beside.eye)
            var views = new List<View>();
            foreach (var v in ((Array)Call("Views", size[0], size[1])).Cast<object>())
                if (Get<string>(v, "name") == "street")
                    views.Add(new View { name = "street", level = Get<string>(v, "level"), pos = Get<Vector3>(v, "pos"), target = Get<Vector3>(v, "target"), fov = Get<float>(v, "fov") });
            var eyePos = V(B.parts[0].at) + V(B.eye.from);
            views.Insert(0, new View { name = "eye", level = "near", pos = eyePos, target = eyePos + V(B.eye.look), fov = B.eye.fov });
            // the raised view of the first part (kit.json beside.high), at its near level
            if (B.high?.from?.Length == 3)
            {
                var highPos = V(B.parts[0].at) + V(B.high.from);
                views.Add(new View { name = "high", level = "near", pos = highPos, target = highPos + V(B.high.look), fov = B.high.fov });
            }
            // the near-isometric view of the first part (kit.json beside.iso), at the street's level, as the street's
            // raised view draws it
            if (B.iso?.from?.Length == 3)
            {
                var isoPos = V(B.parts[0].at) + V(B.iso.from);
                views.Add(new View { name = "iso", level = "street", pos = isoPos, target = isoPos + V(B.iso.look), fov = B.iso.fov });
            }
            // a foot's material a way: P its value alone, Pc its colour (RockFoot.shader)
            var footMats = ways.ToDictionary(w => w, w =>
            {
                var m = new Material(Shader.Find("Overstory/RockFoot"));
                m.SetFloat("_Grey", w == "Pc" ? 0 : 1);
                AssetDatabase.CreateAsset(m, $"{Dir}/Generated/mat-foot-{w}.mat");
                return m;
            });
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
                            foreach (var b in builds.Where(b => b.foot != null))
                                foreach (var r in b.foot.GetComponentsInChildren<MeshRenderer>(true))
                                    r.sharedMaterial = footMats[way];
                            Shader.SetGlobalFloat("_GT_Grey", way == "Pc" ? 0f : 1f);
                            if (tipGround != null)
                                tipGround.GetComponent<MeshRenderer>().sharedMaterial = groundMats[way];
                            // with the tip's ground, the rock always (its bank stands round it)
                            foreach (var with in grey ? new[] { false } : turf != null ? new[] { true } : new[] { true, false })
                            {
                                foreach (var r in rocks)
                                    r.SetActive(with);
                                string file = Path.Combine(outDir, $"{(grey ? "grey" : with ? "tip" : "floor")}-{view.name}-{ln}-{way}.png");
                                Call("Capture", cam, file);
                                Debug.Log($"[LT1HolmTip] {file}" + (turf != null ? $" (turf: {turf.Drawn} tufts, {turf.Triangles} tris drawn)" : ""));
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
            if (turf != null)
            {
                var map = (Texture2D)groundMats[ways[0]].GetTexture("_BaseMap");
                Debug.Log($"[LT1HolmTip] cost ground: {turf.kinds.Sum(k => k.matrices.Length)} tufts in {turf.kinds.Length} kinds " +
                          $"({string.Join(", ", turf.kinds.Select(k => $"{k.name} {k.matrices.Length} x {string.Join("/", k.levels.Select(l => l.triangles.Length / 3))} tris"))}); " +
                          $"map {map.width} {map.graphicsFormat} {Bytes(map) / 1048576.0:F1} MB a way");
            }
        }

        /// <summary>
        /// The tip's ground (blender/parts/rock/kit/ground.py's ground.json, tufts.bin and maps): its community's tufts as
        /// the growth's instances (GrowthTufts, through GrowthDraw), each kind its levels (tufts.py's R2B2) and its
        /// colours, and under them the ground map in the same colours over the whole box, one quad of URP's Lit (P its
        /// value, Pc its colour). The tufts are lit as the house and the rock are (GrowthTuft's _GT_SUN).
        /// </summary>
        static (GameObject, Dictionary<string, Material>, GrowthTufts) Ground(string g, string root, string[] ways)
        {
            string full = Path.Combine(root, "unity", g);
            var R = JsonUtility.FromJson<GroundRec>(File.ReadAllText(Path.Combine(full, "ground.json")));
            AssetDatabase.ImportAsset(g, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceSynchronousImport);
            Color Gam(float[] a) => new Color(a[0], a[1], a[2]).gamma;

            // the ground map: Pc its colour, P its value (maps in that order), over the box, row 0 at its south edge
            var mats = new Dictionary<string, Material>();
            foreach (var way in ways)
            {
                string file = $"{g}/{R.maps[way == "Pc" ? 0 : 1]}";
                var ti = (TextureImporter)AssetImporter.GetAtPath(file);
                ti.sRGBTexture = true;
                ti.wrapMode = TextureWrapMode.Clamp;
                ti.anisoLevel = 16;
                ti.mipmapEnabled = true;
                ti.maxTextureSize = 4096;
                ti.textureCompression = TextureImporterCompression.CompressedHQ;
                ti.SaveAndReimport();
                var m = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                m.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(file));
                m.SetColor("_BaseColor", Color.white);
                m.SetFloat("_Smoothness", (float)St.GetField("GroundSmooth", Any).GetRawConstantValue());
                AssetDatabase.CreateAsset(m, $"{Dir}/Generated/mat-tipground-{way}.mat");
                mats[way] = m;
            }
            float[] b = R.box;
            var mesh = new Mesh { name = "tip ground" };
            mesh.vertices = new[] { new Vector3(b[0], b[1], 0), new Vector3(b[2], b[1], 0), new Vector3(b[2], b[3], 0), new Vector3(b[0], b[3], 0) }.Select(ToUnity).ToArray();
            mesh.uv = new[] { new Vector2(0, 0), new Vector2(1, 0), new Vector2(1, 1), new Vector2(0, 1) };
            mesh.triangles = new[] { 0, 2, 1, 0, 3, 2 };
            mesh.RecalculateNormals();
            if (mesh.normals[0].y < 0)
                mesh.triangles = new[] { 0, 1, 2, 0, 2, 3 };
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            var quad = new GameObject("Tip ground", typeof(MeshFilter), typeof(MeshRenderer));
            quad.GetComponent<MeshFilter>().sharedMesh = mesh;
            quad.GetComponent<MeshRenderer>().sharedMaterial = mats[ways[0]];
            quad.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;

            // the tufts: each instance its turn and scale (row by row) and foot in the scene's frame, then its rank, hue
            // and damp; in Unity's frame the turn is P·R·P (P the y and z swap) and the foot P·t
            var bin = File.ReadAllBytes(Path.Combine(full, "tufts.bin"));
            int n = BitConverter.ToInt32(bin, 0), stride = BitConverter.ToInt32(bin, 4);
            if (stride != R.stride)
                throw new IOException($"{full}/tufts.bin: stride {stride}, ground.json says {R.stride}");
            var f = new float[n * stride];
            Buffer.BlockCopy(bin, 8, f, 0, f.Length * 4);
            int[] sw = { 0, 2, 1 };
            uint Byte(float x) => (uint)Mathf.Clamp(Mathf.RoundToInt(x * 255f), 0, 255);
            var kinds = new List<GrowthTufts.Kind>();
            foreach (var k in R.kinds)
            {
                var mat = new Material(Shader.Find("Hidden/Overstory/GrowthTuft")) { name = $"growth {k.species} {k.variant}" };
                mat.SetColor("_Base", Gam(k.@base));
                mat.SetColor("_Tip", Gam(k.tip));
                mat.SetColor("_Damp", Gam(k.damp));
                mat.SetColor("_Seed", Gam(k.seed));
                mat.SetFloat("_Hue", k.hue);
                mat.EnableKeyword("_GT_SUN");
                var mtx = new Matrix4x4[k.count];
                var users = new uint[k.count];
                for (int i = 0; i < k.count; i++)
                {
                    int o = (k.first + i) * stride;
                    var m = Matrix4x4.identity;
                    for (int r = 0; r < 3; r++)
                        for (int c = 0; c < 3; c++)
                            m[r, c] = f[o + sw[r] * 3 + sw[c]];
                    var t = ToUnity(new Vector3(f[o + 9], f[o + 10], f[o + 11]));
                    m.SetColumn(3, new Vector4(t.x, t.y, t.z, 1f));
                    mtx[i] = m;
                    users[i] = Byte(f[o + 12]) | (Byte(f[o + 13]) << 8) | (Byte(f[o + 14]) << 16);
                }
                kinds.Add(new GrowthTufts.Kind
                {
                    name = $"{k.species} {k.variant}", material = mat, to = R.draw.to, fade = R.draw.fade,
                    thinFrom = R.draw.thinFrom, keepMin = R.draw.keepMin, radius = k.radius, matrices = mtx, users = users,
                    levels = k.levels.Select((p, l) => LoadTuft(Path.Combine(root, p), $"growth: {k.species} {k.variant} L{l}")).ToArray(),
                });
            }
            var L = R.look;
            Shader.SetGlobalVector("_GT_Look", new Vector4(L.calm, L.lamp, L.veil, L.root));
            Shader.SetGlobalVector("_GT_Thin", new Vector4(R.draw.thinFrom, R.draw.keepMin, R.draw.widen, L.shrinkBand));
            Shader.SetGlobalVector("_GT_LookB", new Vector4(L.tipLift, L.hueDetail, L.wet, L.minPx));
            // each tuft's root the ground's colour under its foot (the colour map; the P way greys it as it greys the tip)
            Vector3 lo = ToUnity(new Vector3(b[0], b[1], 0)), hi = ToUnity(new Vector3(b[2], b[3], 0));
            Shader.SetGlobalTexture("_GT_GroundMap", mats.TryGetValue("Pc", out var pc) ? pc.GetTexture("_BaseMap") : AssetDatabase.LoadAssetAtPath<Texture2D>($"{g}/{R.maps[0]}"));
            Shader.SetGlobalVector("_GT_GroundBox", new Vector4(lo.x, lo.z, 1f / (hi.x - lo.x), 1f / (hi.z - lo.z)));
            Shader.SetGlobalFloat("_GT_GroundOn", 1f);
            Shader.SetGlobalFloat("_GT_UpNormal", L.upNormal);
            var turf = new GameObject("Turf").AddComponent<GrowthTufts>();
            turf.kinds = kinds.ToArray();
            turf.Rebuild();
            Debug.Log($"[LT1HolmTip] ground: {n} tufts in {kinds.Count} kinds over [{string.Join(", ", b)}]");
            return (quad, mats, turf);
        }

        /// <summary>A tuft's R2B2 soup (blender/parts/growth/tufts.py): each triangle its own corners, in Unity's frame, its
        /// winding turned for Unity's; its first five UV sets kept (the rest are empty).</summary>
        static Mesh LoadTuft(string path, string name)
        {
            using var br = new BinaryReader(File.OpenRead(path));
            if (new string(br.ReadChars(4)) != "R2B2")
                throw new IOException($"{path}: not an R2B2 mesh");
            int count = br.ReadInt32();
            var v = new Vector3[count];
            for (int i = 0; i < count; i++)
                v[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            var nn = new Vector3[count];
            for (int i = 0; i < count; i++)
                nn[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            var mesh = new Mesh { name = name };
            mesh.vertices = v;
            mesh.normals = nn;
            for (int k = 0; k < 8; k++)
            {
                var uv = new List<Vector2>(count);
                for (int i = 0; i < count; i++)
                    uv.Add(new Vector2(br.ReadSingle(), br.ReadSingle()));
                if (k < 5)
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
            mesh.UploadMeshData(false);
            return mesh;
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
