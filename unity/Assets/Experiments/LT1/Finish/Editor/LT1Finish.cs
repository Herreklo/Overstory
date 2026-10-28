using System;
using System.Collections.Generic;
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
    /// The finishing test (blender/parts/finish): house 107's street corner in 1989, one mesh finished three ways in
    /// clay (A procedural, B scanned, C both), rendered from four views in two lights:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Finish.Run -finishRound r01
    ///
    /// Reads what the Blender scripts left in Generated/ (the corner's two levels, its page, the tileables and
    /// unity.json), builds Finish.unity and writes each still, 2,560 by 1,440 with the PC pipeline's 4 samples a
    /// pixel and nothing more, into cache/finish/renders/&lt;round&gt;/. Positions are street metres (x along the
    /// street, y from the building line, z up), the corner at the origin, as Blender built it.
    /// </summary>
    public static class LT1Finish
    {
        const string Dir = "Assets/Experiments/LT1/Finish";
        const string Gen = Dir + "/Generated";
        const int Width = 2560, Height = 1440, Msaa = 4, WarmUp = 3;

        [Serializable] class Mat { public string name, tile; public int painted; public float paintSmooth, paintFlat, underSmooth; public float[] scanMetres; }
        [Serializable] class Digest { public Mat[] mats; public float tileMetres, dirtL, waterL, cavityL, lapDark, lapReach, lapScale, groundL, groundSmooth; }

        struct View { public string name, level; public Vector3 pos, target; public float fov; }

        // eye level about 3 m off, the street stop at 20 m, raised to 12 m, and high
        static readonly View[] Views =
        {
            new View { name = "eye", level = "near", pos = new Vector3(-1.0f, -2.9f, 1.6f), target = new Vector3(0.95f, 0.25f, 1.75f), fov = 42 },
            new View { name = "street", level = "street", pos = new Vector3(-8.5f, -18.0f, 1.6f), target = new Vector3(0.9f, 0.3f, 1.9f), fov = 42 },
            new View { name = "raised", level = "street", pos = new Vector3(-6.0f, -11.0f, 12.0f), target = new Vector3(0.9f, 0.3f, 1.8f), fov = 42 },
            new View { name = "high", level = "street", pos = new Vector3(-18.0f, -34.0f, 30.0f), target = new Vector3(0.9f, 0.3f, 1.6f), fov = 42 },
        };

        struct Lighting { public string name; public Vector2 azimuth; public float elevation, sun, shadow, sky, equator, ground, exposure; }

        // overcast: photo 09's grey day, the sky doing the work and a weak high key for the eave's and sill's shade;
        // low sun: raking along the street wall from the west, the gable lit full
        static readonly Lighting[] Lights =
        {
            new Lighting { name = "overcast", azimuth = new Vector2(-0.5f, -1f), elevation = 65, sun = 0.45f, shadow = 0.7f, sky = 0.95f, equator = 0.72f, ground = 0.14f, exposure = 1.6f },
            new Lighting { name = "lowsun", azimuth = new Vector2(-1f, -0.35f), elevation = 11, sun = 2.6f, shadow = 1f, sky = 0.32f, equator = 0.24f, ground = 0.1f, exposure = -0.6f },
        };

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        public static void Run()
        {
            string round = Arg("-finishRound") ?? "r01";
            var only = (Arg("-finishViews") ?? "eye,street,raised,high").Split(',');
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outDir = Path.Combine(root, "cache", "finish", "renders", round);
            Directory.CreateDirectory(outDir);

            Import();
            // last run's materials and profile go first: writing an asset over one that exists keeps stale parts
            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { Gen }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));
            var digest = JsonUtility.FromJson<Digest>(File.ReadAllText(Path.Combine(Gen, "unity.json")));
            var mats = Materials(digest);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var corner = new GameObject("Corner");
            var levels = new Dictionary<string, GameObject>();
            foreach (var level in new[] { "near", "street" })
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/corner-{level}.fbx");
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.SetParent(corner.transform, false);
                levels[level] = go;
            }
            Orient(corner, levels["near"]);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(8, 1, 8);
            ground.transform.position = ToUnity(new Vector3(0, -10, 0));
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            float gy = LToY(digest.groundL);
            gm.SetColor("_BaseColor", new Color(gy, gy, gy).gamma);
            gm.SetFloat("_Smoothness", digest.groundSmooth);
            AssetDatabase.CreateAsset(gm, $"{Gen}/mat-ground.mat");
            ground.GetComponent<Renderer>().sharedMaterial = gm;

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            sun.color = Color.white;

            var volumeGo = new GameObject("Volume");
            var volume = volumeGo.AddComponent<Volume>();
            volume.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            var tone = profile.Add<Tonemapping>(true);
            tone.mode.Override(TonemappingMode.Neutral);
            var adjust = profile.Add<ColorAdjustments>(true);
            AssetDatabase.CreateAsset(profile, $"{Gen}/finish-volume.asset");
            volume.sharedProfile = profile;

            var camGo = new GameObject("Camera");
            var cam = camGo.AddComponent<Camera>();
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.62f, 0.62f, 0.62f);
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 500f;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, $"{Dir}/Finish.unity");
            AssetDatabase.SaveAssets();

            // the project's renderer carries the street's own passes (haze, palette, sun beams, reflections); the
            // clay test keeps only screen-space occlusion, and restores the rest after
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            Debug.Log($"[LT1Finish] pipeline {GraphicsSettings.currentRenderPipeline?.name}, quality {QualitySettings.names[QualitySettings.GetQualityLevel()]}");
            try
            {
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                foreach (var light in Lights)
                {
                    Light(sun, light);
                    // exposed as photo 09 was: its white paint at about 232 of 255 under the grey sky
                    adjust.postExposure.Override(light.exposure);
                    foreach (var view in Views.Where(v => only.Contains(v.name)))
                    {
                        foreach (var kv in levels)
                            kv.Value.SetActive(kv.Key == view.level);
                        cam.transform.SetPositionAndRotation(ToUnity(view.pos), Quaternion.LookRotation(ToUnity(view.target - view.pos), Vector3.up));
                        cam.fieldOfView = view.fov;
                        foreach (var way in new[] { "A", "B", "C" })
                        {
                            Assign(levels[view.level], mats, way, view.level);
                            string file = Path.Combine(outDir, $"{view.name}-{light.name}-{way}.png");
                            Capture(cam, file);
                            Debug.Log($"[LT1Finish] {file}");
                        }
                    }
                }
            }
            finally
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
            }
            Tris(levels);
        }

        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        static float LToY(float L) => L > 8 ? Mathf.Pow((L + 16) / 116f, 3) : L / 903.3f;

        /// <summary>Import settings: the page and tileables linear and uncompressed, the tileables repeating.</summary>
        static void Import()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Gen }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                string n = Path.GetFileNameWithoutExtension(path);
                bool tile = n.StartsWith("tile-") || n.StartsWith("scan-");
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = false;
                ti.mipmapEnabled = true;
                ti.wrapMode = tile ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                ti.filterMode = FilterMode.Trilinear;
                ti.anisoLevel = tile ? 8 : 4;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.maxTextureSize = 2048;
                ti.npotScale = TextureImporterNPOTScale.None;
                ti.SaveAndReimport();
            }
            foreach (var level in new[] { "near", "street" })
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{Gen}/corner-{level}.fbx");
                mi.materialImportMode = ModelImporterMaterialImportMode.None;
                mi.importNormals = ModelImporterNormals.Import;
                mi.importTangents = ModelImporterTangents.CalculateMikk;
                mi.importBlendShapes = false;
                mi.importCameras = false;
                mi.importLights = false;
                mi.animationType = ModelImporterAnimationType.None;
                mi.importAnimation = false;
                mi.meshCompression = ModelImporterMeshCompression.Off;
                mi.globalScale = 1;
                mi.SaveAndReimport();
            }
        }

        /// <summary>One material for each of the corner's materials, way and level.</summary>
        static Dictionary<string, Material> Materials(Digest d)
        {
            var shader = Shader.Find("Overstory/Finish");
            var tex = (Func<string, Texture2D>)(n => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/{n}.png"));
            var outp = new Dictionary<string, Material>();
            foreach (var way in new[] { "A", "B", "C" })
            foreach (var level in new[] { "near", "street" })
            foreach (var m in d.mats)
            {
                var mat = new Material(shader);
                bool scan = way != "A";
                string stem = (scan ? "scan-" : "tile-") + m.tile;
                mat.SetTexture("_Tile", tex(stem));
                mat.SetTexture("_TileN", tex(stem + "-n"));
                var scale = scan ? new Vector4(d.tileMetres / m.scanMetres[0], d.tileMetres / m.scanMetres[1], 0, 0) : new Vector4(1, 1, 0, 0);
                mat.SetVector("_TileScale", scale);
                mat.SetTexture("_Hist", tex(way == "B" ? "hist-b" : "hist-a"));
                mat.SetTexture("_Geo", tex("geo"));
                mat.SetTexture("_StreetN", tex("street-normal"));
                mat.SetFloat("_Painted", m.painted);
                mat.SetFloat("_PaintSmooth", m.paintSmooth);
                mat.SetFloat("_UnderSmooth", m.underSmooth);
                mat.SetFloat("_PaintFlat", m.paintFlat);
                mat.SetFloat("_DirtL", d.dirtL);
                mat.SetFloat("_WaterL", d.waterL);
                mat.SetFloat("_CavityL", d.cavityL);
                mat.SetFloat("_LapDark", d.lapDark);
                mat.SetFloat("_LapReach", d.lapReach);
                mat.SetFloat("_LapScale", d.lapScale);
                // way B's page carries no board values and no dirt: its own surface is the scan's
                mat.SetFloat("_BoardScale", way == "B" ? 0 : 1);
                if (level == "street")
                {
                    mat.SetFloat("_Street", 1);
                    mat.EnableKeyword("_OS_STREET");
                }
                string key = $"{way}-{level}-{m.name}";
                AssetDatabase.CreateAsset(mat, $"{Gen}/mat-{key}.mat");
                outp[key] = mat;
            }
            return outp;
        }

        static void Assign(GameObject level, Dictionary<string, Material> mats, string way, string levelName)
        {
            foreach (var r in level.GetComponentsInChildren<MeshRenderer>(true))
            {
                string kind = r.gameObject.name.Substring(r.gameObject.name.IndexOf('_') + 1);
                if (mats.TryGetValue($"{way}-{levelName}-{kind}", out var mat))
                    r.sharedMaterial = mat;
                else
                    Debug.LogWarning($"[LT1Finish] no material for {r.gameObject.name}");
            }
        }

        /// <summary>
        /// The FBX's axes as Unity imported them, found from where the near cladding landed: Blender built the street
        /// wall along +x and the gable back along +y, so its centre must sit at +x, +z in Unity.
        /// </summary>
        static void Orient(GameObject corner, GameObject near)
        {
            var clad = near.GetComponentsInChildren<MeshRenderer>(true).First(r => r.gameObject.name.EndsWith("cladding"));
            var c = clad.bounds.center;
            Debug.Log($"[LT1Finish] near cladding imported at {c} (bounds {clad.bounds.size})");
            if (c.x < 0 && c.z < 0)
                corner.transform.rotation = Quaternion.Euler(0, 180, 0);
            else if (c.x < 0 || c.z < 0)
                corner.transform.localScale = new Vector3(c.x < 0 ? -1 : 1, 1, c.z < 0 ? -1 : 1);
            Physics.SyncTransforms();
            Debug.Log($"[LT1Finish] corner oriented: cladding now at {clad.bounds.center}");
        }

        static void Light(Light sun, Lighting l)
        {
            var a = l.azimuth.normalized;
            float e = l.elevation * Mathf.Deg2Rad;
            var toSun = new Vector3(Mathf.Cos(e) * a.x, Mathf.Cos(e) * a.y, Mathf.Sin(e));
            sun.transform.rotation = Quaternion.LookRotation(-ToUnity(toSun), Vector3.up);
            sun.intensity = l.sun;
            sun.shadowStrength = l.shadow;
            var lin = (Func<float, Color>)(v => new Color(v, v, v).gamma);
            RenderSettings.ambientSkyColor = lin(l.sky);
            RenderSettings.ambientEquatorColor = lin(l.equator);
            RenderSettings.ambientGroundColor = lin(l.ground);
            DynamicGI.UpdateEnvironment();
        }

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

        static void Tris(Dictionary<string, GameObject> levels)
        {
            foreach (var kv in levels)
            {
                int tris = kv.Value.GetComponentsInChildren<MeshFilter>(true).Sum(f => (int)(f.sharedMesh.triangles.Length / 3));
                Debug.Log($"[LT1Finish] {kv.Key}: {tris} triangles in Unity");
                foreach (var f in kv.Value.GetComponentsInChildren<MeshFilter>(true).Where(f => f.name.EndsWith("cladding")))
                {
                    var c = f.sharedMesh.colors;
                    Debug.Log($"[LT1Finish] {f.name}: {c.Length} colours, alpha {(c.Length > 0 ? c.Min(x => x.a) : -1)}..{(c.Length > 0 ? c.Max(x => x.a) : -1)}");
                }
            }
        }
    }
}
