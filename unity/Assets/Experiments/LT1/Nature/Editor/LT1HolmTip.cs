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

            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { Dir }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));
            var builds = new List<Build>();
            foreach (var name in new[] { B.house }.Concat(B.parts.Select(p => p.part)))
            {
                var b = new Build { name = name, gen = $"{Dir}/Generated/{name}" };
                Call("Import", b.gen);
                b.house = Json(Path.Combine(b.gen, "house.json"), "House");
                b.paint = Json(Path.Combine(b.gen, "paint.json"), "Paint");
                b.mats = (Dictionary<string, Material>)Call("Materials", b.gen, b.paint, b.house);
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
            cam.farClipPlane = 500f;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, "Assets/Experiments/LT1/Nature/HolmTip.unity");
            AssetDatabase.SaveAssets();

            // the street's street stop as it is; its eye view taken back to the first part (kit.json beside.eye)
            var views = new List<View>();
            foreach (var v in ((Array)Call("Views", size[0], size[1])).Cast<object>())
                if (Get<string>(v, "name") == "street")
                    views.Add(new View { name = "street", level = Get<string>(v, "level"), pos = Get<Vector3>(v, "pos"), target = Get<Vector3>(v, "target"), fov = Get<float>(v, "fov") });
            var eyePos = V(B.parts[0].at) + V(B.eye.from);
            views.Insert(0, new View { name = "eye", level = "near", pos = eyePos, target = eyePos + V(B.eye.look), fov = B.eye.fov });

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
                        urp.shadowCascadeCount = 1;
                        urp.mainLightShadowmapResolution = 4096;
                        urp.shadowDistance = (view.target - view.pos).magnitude + 8f;
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
                            foreach (var with in new[] { true, false })
                            {
                                foreach (var r in rocks)
                                    r.SetActive(with);
                                string file = Path.Combine(outDir, $"{(with ? "tip" : "floor")}-{view.name}-{ln}-{way}.png");
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

        static string Arg(string name) => (string)Call("Arg", name);
    }
}
