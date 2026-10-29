using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.EditorTools
{
    /// <summary>
    /// Nature's first element, rock and land (blender/parts/rock): the Holm's rock tip in grey clay, rendered from the
    /// views and in the lights blockin.py wrote beside its FBX:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Nature.Run -natureRound r01
    ///
    /// Reads Generated/holm-tip.fbx and Generated/unity.json (each material's L* and smoothness, the views, the
    /// lights), builds Nature.unity and writes each still, 2,560 by 1,440 with the PC pipeline's 4 samples a pixel,
    /// into cache/rock/renders/&lt;round&gt;/. Positions are site metres (x east, y north, z up), as Blender built them.
    /// </summary>
    public static class LT1Nature
    {
        const string Dir = "Assets/Experiments/LT1/Nature";
        const string Gen = Dir + "/Generated";
        const int Width = 2560, Height = 1440, Msaa = 4, WarmUp = 3;

        [Serializable] class Mat { public string name; public float L, smooth; }
        [Serializable] class View { public string name; public float[] pos, target; public float lens; }
        [Serializable] class Own { public float sun, shadow, sky, equator, ground, exposure; }
        [Serializable] class Lighting { public string name; public float azimuth, elevation; public Own unity; }
        [Serializable] class Digest { public Mat[] mats; public View[] views; public Lighting[] lights; }

        static Vector3 ToUnity(float[] s) => new Vector3(s[0], s[2], s[1]);

        public static void Run()
        {
            string round = Arg("-natureRound") ?? "r01";
            var only = Arg("-natureViews")?.Split(',');
            var lightsOnly = Arg("-natureLights")?.Split(',');
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outDir = Path.Combine(root, "cache", "rock", "renders", round);
            Directory.CreateDirectory(outDir);

            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var mi = (ModelImporter)AssetImporter.GetAtPath($"{Gen}/holm-tip.fbx");
            mi.materialImportMode = ModelImporterMaterialImportMode.None;
            mi.importNormals = ModelImporterNormals.Import;
            mi.importCameras = false;
            mi.importLights = false;
            mi.animationType = ModelImporterAnimationType.None;
            mi.importAnimation = false;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.indexFormat = ModelImporterIndexFormat.UInt32;
            mi.globalScale = 1;
            mi.SaveAndReimport();
            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { Gen }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));

            var digest = JsonUtility.FromJson<Digest>(File.ReadAllText(Path.Combine(Gen, "unity.json")));
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/holm-tip.fbx");
            var site = new GameObject("Site");
            var model = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            model.transform.SetParent(site.transform, false);
            Orient(site, model);

            // each material in its own grey, by name (Blender's material names carry through as the slot names)
            var lit = Shader.Find("Universal Render Pipeline/Lit");
            var mats = digest.mats.ToDictionary(m => m.name, m =>
            {
                var mat = new Material(lit) { name = m.name };
                float y = LToY(m.L);
                mat.SetColor("_BaseColor", new Color(y, y, y).gamma);
                mat.SetFloat("_Smoothness", m.smooth);
                AssetDatabase.CreateAsset(mat, $"{Gen}/mat-{m.name}.mat");
                return mat;
            });
            int tris = 0;
            foreach (var r in model.GetComponentsInChildren<MeshRenderer>(true))
            {
                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                tris += mesh.triangles.Length / 3;
                // the FBX keeps the slots' names on the imported mesh's submeshes only through the importer's
                // remap, so the slots are matched by the object's name and its materials' order instead
                var names = SlotNames(r.gameObject.name, mesh.subMeshCount);
                r.sharedMaterials = names.Select(n => mats.TryGetValue(n, out var m) ? m : mats["rock"]).ToArray();
            }
            Debug.Log($"[LT1Nature] {tris} triangles in Unity");

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            sun.color = Color.white;
            sunGo.AddComponent<UniversalAdditionalLightData>().softShadowQuality = SoftShadowQuality.Medium;
            sun.shadowBias = 0.6f;
            sun.shadowNormalBias = 0.6f;

            var volumeGo = new GameObject("Volume");
            var volume = volumeGo.AddComponent<Volume>();
            volume.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.Add<Tonemapping>(true).mode.Override(TonemappingMode.Neutral);
            var adjust = profile.Add<ColorAdjustments>(true);
            AssetDatabase.CreateAsset(profile, $"{Gen}/nature-volume.asset");
            volume.sharedProfile = profile;

            var camGo = new GameObject("Camera");
            var cam = camGo.AddComponent<Camera>();
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Back;
            cam.nearClipPlane = 0.2f;
            cam.farClipPlane = 3000f;
            cam.usePhysicalProperties = false;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, $"{Dir}/Nature.unity");
            AssetDatabase.SaveAssets();

            // the renderer's street passes off but screen-space occlusion, and one sharp cascade; both put back after
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
            try
            {
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                foreach (var light in digest.lights.Where(l => l.unity != null && l.unity.sun > 0 && (lightsOnly == null || lightsOnly.Contains(l.name))))
                {
                    Light(sun, light);
                    adjust.postExposure.Override(light.unity.exposure);
                    foreach (var view in digest.views.Where(v => only == null || only.Contains(v.name)))
                    {
                        var pos = ToUnity(view.pos);
                        cam.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(ToUnity(view.target) - pos, Vector3.up));
                        // the lens on a 36 mm wide frame, as Blender's camera: the vertical angle for 16:9
                        float hfov = 2 * Mathf.Atan(18f / view.lens);
                        cam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(hfov / 2) * Height / Width) * Mathf.Rad2Deg;
                        urp.shadowCascadeCount = 1;
                        urp.mainLightShadowmapResolution = 4096;
                        urp.shadowDistance = 140f;
                        string file = Path.Combine(outDir, $"{view.name}-{light.name}.png");
                        Capture(cam, file);
                        Debug.Log($"[LT1Nature] {file}");
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

        // each object's material slots in Blender's order (blockin.py): the land's two, a building's wall and roof
        static string[] SlotNames(string obj, int n)
        {
            string o = obj.ToLowerInvariant();
            string[] s =
                o == "land" ? new[] { "holm-ground", "holm-ground" } :
                o == "rock" ? new[] { "rock" } :
                o == "water" ? new[] { "water" } :
                o == "landing" || o == "path-fill" || o == "pub-quay-end" ? new[] { "made-ground" } :
                o.EndsWith("-plinth") ? new[] { "plinth" } :
                o == "customs-house" || o == "harbour-office" ? new[] { "timber-red", "roof" } :
                o.StartsWith("town-") ? new[] { "town", "roof" } :
                o == "breakwater" ? new[] { "breakwater" } :
                o == "light" ? new[] { "light" } :
                new[] { "far" };
            return Enumerable.Range(0, n).Select(i => s[Math.Min(i, s.Length - 1)]).ToArray();
        }

        /// <summary>
        /// The FBX's axes as Unity imported them, found from where the customs house landed: Blender built it at
        /// site (6, -6), so its centre must sit at +x, -z in Unity.
        /// </summary>
        static void Orient(GameObject site, GameObject model)
        {
            var house = model.GetComponentsInChildren<MeshRenderer>(true).First(r => r.gameObject.name == "customs-house");
            var c = house.bounds.center;
            Debug.Log($"[LT1Nature] customs house imported at {c}");
            bool fx = c.x < 0, fz = c.z > 0;
            if (fx && fz)
                site.transform.rotation = Quaternion.Euler(0, 180, 0);
            else if (fx || fz)
                site.transform.localScale = new Vector3(fx ? -1 : 1, 1, fz ? -1 : 1);
            Physics.SyncTransforms();
            Debug.Log($"[LT1Nature] site oriented: customs house now at {house.bounds.center}");
        }

        static void Light(Light sun, Lighting l)
        {
            float a = l.azimuth * Mathf.Deg2Rad, e = l.elevation * Mathf.Deg2Rad;
            var toSun = new[] { Mathf.Cos(e) * Mathf.Sin(a), Mathf.Cos(e) * Mathf.Cos(a), Mathf.Sin(e) };
            sun.transform.rotation = Quaternion.LookRotation(-ToUnity(toSun), Vector3.up);
            var u = l.unity;
            sun.intensity = u.sun;
            sun.shadowStrength = u.shadow;
            RenderSettings.ambientSkyColor = new Color(u.sky, u.sky, u.sky).gamma;
            RenderSettings.ambientEquatorColor = new Color(u.equator, u.equator, u.equator).gamma;
            RenderSettings.ambientGroundColor = new Color(u.ground, u.ground, u.ground).gamma;
            DynamicGI.UpdateEnvironment();
        }

        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        static float LToY(float L) => L > 8 ? Mathf.Pow((L + 16) / 116f, 3) : L / 903.3f;

        static readonly Color Back = new Color(0.62f, 0.62f, 0.62f);

        static void Capture(Camera cam, string file)
        {
            var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = Msaa };
            rt.Create();
            var target = cam.targetTexture;
            try
            {
                cam.targetTexture = rt;
                for (int i = 0; i < WarmUp; i++)
                    LT1Render.Render(cam, rt);
                var resolved = new RenderTexture(Width, Height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
                Graphics.Blit(rt, resolved);
                var prev = RenderTexture.active;
                RenderTexture.active = resolved;
                var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                File.WriteAllBytes(file, tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
                resolved.Release();
                UnityEngine.Object.DestroyImmediate(resolved);
            }
            finally
            {
                cam.targetTexture = target;
                rt.Release();
                UnityEngine.Object.DestroyImmediate(rt);
            }
        }
    }
}
