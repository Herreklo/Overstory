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
    /// The street test (blender/parts/street): a house of Harbour Row whole, from its record, in the painted finish
    /// (way P, clay; way Pc, its values in colour), rendered from four views in two lights:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse 107
    ///         -streetRound s01 [-streetViews eye,street] [-streetWays P,Pc]
    ///
    /// Reads what run/render.sh copied into Generated/&lt;house&gt;/ (the house's two levels, its page and house.json),
    /// builds Street.unity and writes each still, 2,560 by 1,440 with the PC pipeline's 4 samples a pixel and nothing
    /// more, into cache/street/renders/&lt;round&gt;/. Positions are the house's own metres (x along its street front from
    /// its left corner, y back from the building line, z up), as Blender built it. The lights, the shader and the
    /// capture are the finishing test's (LT1Finish), so a house is judged beside the corner on the same terms.
    /// </summary>
    public static class LT1Street
    {
        const string Dir = "Assets/Experiments/LT1/Street";
        const int Width = 2560, Height = 1440, Msaa = 4, WarmUp = 3;

        [Serializable] class PMat { public string name; public int painted; public float L, bareL, underL, stainDL, smooth, stainSmooth, brushL, flatUp, stainEdge, ao, shadowLift; }
        [Serializable] class PLight { public string light; public float exposure, elevation, sun, shadow, sky, equator, ground; public float[] azimuth; }
        [Serializable] class PColMat { public string name; public float[] tint, bareTint, underTint, stainTint; }
        [Serializable] class PColLight { public string light; public float[] sun, sky, equator, ground, background, floor; }
        [Serializable] class PColour { public PColMat[] mats; public PColLight[] lights; public float[] washTint; }
        [Serializable] class Paint { public PMat[] mats; public PLight[] lights; public PColour colour; public float strokeScale, edgeAmp, rimL, rimW, rimFar, bareShift, washL, bareWash, brushFar, dragL, dragScale, dlRange, aoStrength, lapDark, lapCore, lapReach, lapGrimeL, lapGrimeReach, lapGrimeBreak, lapPage; public float[] strokeFade, brushFade, rimBreak, washFade; }
        [Serializable] class Lap { public float reach, step; }
        [Serializable] class House { public int house; public float[] size; public Lap lap; }

        struct View { public string name, level; public Vector3 pos, target; public float fov; public bool floor; }

        // in the house's frame, from its size: eye level 4 m off its front, the street stop at 20 m, raised to 12 m, high
        static View[] Views(float w, float d) => new[]
        {
            new View { name = "eye", level = "near", pos = new Vector3(w / 2 - 2.6f, -4.4f, 1.6f), target = new Vector3(w / 2 - 0.4f, 0.3f, 2.1f), fov = 52 },
            new View { name = "street", level = "street", pos = new Vector3(w / 2 - 9.0f, -19.0f, 1.6f), target = new Vector3(w / 2, 1.0f, 3.0f), fov = 38 },
            new View { name = "raised", level = "street", pos = new Vector3(-7.0f, -12.0f, 12.0f), target = new Vector3(w / 2, d / 2, 2.5f), fov = 42 },
            new View { name = "high", level = "street", pos = new Vector3(-18.0f, -34.0f, 30.0f), target = new Vector3(w / 2, d / 2, 2.0f), fov = 30 },
            new View { name = "back", level = "near", pos = new Vector3(w + 7.0f, d + 11.0f, 2.2f), target = new Vector3(w / 2, d, 2.6f), fov = 44 },
            new View { name = "gable", level = "near", pos = new Vector3(-9.0f, d / 2 - 3.0f, 1.8f), target = new Vector3(0, d / 2, 3.0f), fov = 50 },
            // the floor's own cameras (LT1Finish at p3) on the same corner of the same house, in its own lights
            new View { name = "p3eye", level = "near", pos = new Vector3(-1.0f, -2.9f, 1.6f), target = new Vector3(0.95f, 0.25f, 1.75f), fov = 42, floor = true },
            new View { name = "p3street", level = "street", pos = new Vector3(-8.5f, -18.0f, 1.6f), target = new Vector3(0.9f, 0.3f, 1.9f), fov = 42, floor = true },
        };

        struct Lighting { public string name; public Vector2 azimuth; public float elevation, sun, shadow, sky, equator, ground, exposure; }

        // the finishing test's two lights (LT1Finish), where way P's plan names none of its own
        static readonly Lighting[] Lights =
        {
            new Lighting { name = "overcast", azimuth = new Vector2(-0.5f, -1f), elevation = 65, sun = 0.45f, shadow = 0.7f, sky = 0.95f, equator = 0.72f, ground = 0.14f, exposure = 1.6f },
            new Lighting { name = "lowsun", azimuth = new Vector2(0.906f, -0.423f), elevation = 18, sun = 2.6f, shadow = 1f, sky = 0.32f, equator = 0.24f, ground = 0.1f, exposure = 0.5f },
        };

        const float GroundL = 42, GroundSmooth = 0.1f;

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        public static void Run()
        {
            string id = Arg("-streetHouse") ?? "107";
            string round = Arg("-streetRound") ?? "s01";
            var only = (Arg("-streetViews") ?? "eye,street,raised,high").Split(',');
            var ways = (Arg("-streetWays") ?? "P,Pc").Split(',');
            var lights = (Arg("-streetLights") ?? "overcast,lowsun").Split(',');
            // the low sun for one house alone: turned to strike its front this many degrees off square, so the relief
            // shows (the street's own light is the light step's); the floor's cameras keep the floor's sun
            float sunOff = float.Parse(Arg("-streetSunOff") ?? "45", System.Globalization.CultureInfo.InvariantCulture);
            string gen = $"{Dir}/Generated/{id}";
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outDir = Path.Combine(root, "cache", "street", "renders", round);
            Directory.CreateDirectory(outDir);

            Import(gen);
            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { gen }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));
            var house = JsonUtility.FromJson<House>(File.ReadAllText(Path.Combine(gen, "house.json")));
            var paint = JsonUtility.FromJson<Paint>(File.ReadAllText(Path.Combine(gen, "paint.json")));
            var mats = Materials(gen, paint, house.lap);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var root_ = new GameObject($"House {id}");
            var levels = new Dictionary<string, GameObject>();
            foreach (var level in new[] { "near", "street" })
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{gen}/house-{level}.fbx");
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.SetParent(root_.transform, false);
                levels[level] = go;
            }
            Orient(root_, levels["near"]);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(8, 1, 8);
            ground.transform.position = ToUnity(new Vector3(house.size[0] / 2, -10, 0));
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            float gy = LToY(GroundL);
            gm.SetFloat("_Smoothness", GroundSmooth);
            AssetDatabase.CreateAsset(gm, $"{gen}/mat-ground.mat");
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
            AssetDatabase.CreateAsset(profile, $"{gen}/street-volume.asset");
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
            EditorSceneManager.SaveScene(scene, $"{Dir}/Street.unity");
            AssetDatabase.SaveAssets();

            // the clay test keeps only the renderer's screen-space occlusion and one sharp cascade fitted to each
            // view, and puts the rest back after
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
            try
            {
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                foreach (var light in Lights.Where(l => lights.Contains(l.name)))
                foreach (var view in Views(house.size[0], house.size[1]).Where(v => only.Contains(v.name)))
                {
                    foreach (var kv in levels)
                        kv.Value.SetActive(kv.Key == view.level);
                    cam.transform.SetPositionAndRotation(ToUnity(view.pos), Quaternion.LookRotation(ToUnity(view.target - view.pos), Vector3.up));
                    cam.fieldOfView = view.fov;
                    urp.shadowCascadeCount = 1;
                    urp.mainLightShadowmapResolution = 4096;
                    urp.shadowDistance = (view.target - view.pos).magnitude + 8f;
                    foreach (var way in ways)
                    {
                        var own = paint.lights?.FirstOrDefault(e => e.light == light.name);
                        var col = way == "Pc" ? paint.colour?.lights?.FirstOrDefault(e => e.light == light.name) : null;
                        var l = own != null ? Own(light, own) : light;
                        if (!view.floor && l.name == "lowsun")
                            l.azimuth = new Vector2(Mathf.Sin(sunOff * Mathf.Deg2Rad), -Mathf.Cos(sunOff * Mathf.Deg2Rad));
                        Light(sun, l, col);
                        cam.backgroundColor = Lin(Back.linear.r, col?.background);
                        gm.SetColor("_BaseColor", Lin(gy, col?.floor));
                        adjust.postExposure.Override(own != null ? own.exposure : light.exposure);
                        Assign(levels[view.level], mats, way, view.level);
                        string file = Path.Combine(outDir, $"{id}-{view.name}-{light.name}-{way}.png");
                        Capture(cam, file);
                        Debug.Log($"[LT1Street] {file}");
                    }
                }
            }
            finally
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = urpWas;
            }
            foreach (var kv in levels)
                Debug.Log($"[LT1Street] {kv.Key}: {kv.Value.GetComponentsInChildren<MeshFilter>(true).Sum(f => f.sharedMesh.triangles.Length / 3)} triangles in Unity");
        }

        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        static float LToY(float L) => L > 8 ? Mathf.Pow((L + 16) / 116f, 3) : L / 903.3f;

        static readonly Color Back = new Color(0.62f, 0.62f, 0.62f);

        static Color Lin(float v, float[] t) => t == null || t.Length != 3 ? new Color(v, v, v).gamma : new Color(v * t[0], v * t[1], v * t[2]).gamma;

        /// <summary>The page linear and uncompressed, the strokes repeating; the levels with their own normals.</summary>
        static void Import(string gen)
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { gen }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                bool tile = Path.GetFileNameWithoutExtension(path).StartsWith("paint-");
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = false;
                ti.mipmapEnabled = true;
                ti.wrapMode = tile ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                ti.filterMode = FilterMode.Trilinear;
                ti.anisoLevel = tile ? 8 : 4;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.maxTextureSize = 4096;
                ti.npotScale = TextureImporterNPOTScale.None;
                ti.SaveAndReimport();
            }
            foreach (var level in new[] { "near", "street" })
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{gen}/house-{level}.fbx");
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

        /// <summary>
        /// One material for each of the house's materials, way and level. A plane that stands for finer geometry reads
        /// the page's normal at every level: the street level's walls, and the roof's course planes at both.
        /// </summary>
        static Dictionary<string, Material> Materials(string gen, Paint p, Lap lap)
        {
            var shader = Shader.Find("Overstory/Finish");
            var tex = (Func<string, Texture2D>)(n => AssetDatabase.LoadAssetAtPath<Texture2D>($"{gen}/{n}.png"));
            var outp = new Dictionary<string, Material>();
            foreach (var way in new[] { "P", "Pc" })
            foreach (var level in new[] { "near", "street" })
            foreach (var m in p.mats)
            {
                var mat = new Material(shader);
                mat.SetFloat("_Paint", 1);
                var c = way == "Pc" ? p.colour?.mats?.FirstOrDefault(e => e.name == m.name) : null;
                if (c != null)
                {
                    mat.SetVector("_Tint", Tint(c.tint));
                    mat.SetVector("_BareTint", Tint(c.bareTint));
                    mat.SetVector("_UnderTint", Tint(c.underTint));
                    mat.SetVector("_StainTint", Tint(c.stainTint));
                    mat.SetVector("_WashTint", Tint(p.colour.washTint));
                }
                mat.EnableKeyword("_OS_PAINT");
                mat.SetTexture("_Hist", tex("hist-p"));
                mat.SetTexture("_Hist2", tex("hist-p2"));
                mat.SetTexture("_Geo", tex("geo"));
                mat.SetTexture("_StreetN", tex("street-normal"));
                mat.SetTexture("_Stroke", tex("paint-stroke"));
                mat.SetFloat("_StrokeScale", p.strokeScale);
                mat.SetFloat("_EdgeAmp", p.edgeAmp);
                mat.SetVector("_StrokeFade", new Vector4(p.strokeFade[0], p.strokeFade[1], 0, 0));
                mat.SetVector("_BrushFade", new Vector4(p.brushFade[0], p.brushFade[1], 0, 0));
                mat.SetFloat("_BrushL", m.brushL);
                mat.SetFloat("_BrushFar", p.brushFar);
                mat.SetFloat("_DragL", p.dragL);
                mat.SetFloat("_DragScale", p.dragScale);
                mat.SetFloat("_DLRange", p.dlRange);
                mat.SetFloat("_FlatUp", m.flatUp);
                mat.SetFloat("_StainEdge", m.stainEdge);
                mat.SetFloat("_RimL", p.rimL);
                mat.SetFloat("_RimW", p.rimW);
                mat.SetFloat("_RimFar", p.rimFar);
                mat.SetVector("_RimBreak", new Vector4(p.rimBreak[0], p.rimBreak[1], 0, 0));
                mat.SetFloat("_WashL", p.washL);
                mat.SetFloat("_BareWash", p.bareWash);
                mat.SetVector("_WashFade", p.washFade != null && p.washFade.Length == 2 ? new Vector4(p.washFade[0], p.washFade[1], 0, 0) : Vector4.zero);
                mat.SetFloat("_BareShift", p.bareShift);
                mat.SetFloat("_Painted", m.painted);
                mat.SetFloat("_PaintL", m.L);
                mat.SetFloat("_BareL", m.bareL);
                mat.SetFloat("_UnderL", m.underL);
                mat.SetFloat("_StainDL", m.stainDL);
                mat.SetFloat("_PaintSmooth", m.smooth);
                mat.SetFloat("_StainSmooth", m.stainSmooth);
                mat.SetFloat("_AOStrength", m.ao);
                mat.SetFloat("_ShadowLift", m.shadowLift);
                mat.SetFloat("_LapDark", p.lapDark);
                mat.SetFloat("_LapCore", p.lapCore);
                mat.SetFloat("_LapReach", p.lapReach);
                mat.SetFloat("_LapGrimeL", p.lapGrimeL);
                mat.SetFloat("_LapGrimeReach", p.lapGrimeReach);
                mat.SetFloat("_LapGrimeBreak", p.lapGrimeBreak);
                mat.SetFloat("_LapScale", lap.reach);
                mat.SetFloat("_LapPage", p.lapPage);
                mat.SetFloat("_LapStep", lap.step);
                if (level == "street" || m.name == "roof")
                {
                    mat.SetFloat("_Street", 1);
                    mat.EnableKeyword("_OS_STREET");
                }
                string key = $"{way}-{level}-{m.name}";
                AssetDatabase.CreateAsset(mat, $"{gen}/mat-{key}.mat");
                outp[key] = mat;
            }
            return outp;
        }

        static Vector4 Tint(float[] t) => t == null || t.Length != 3 ? Vector4.one : new Vector4(t[0], t[1], t[2], 1);

        static void Assign(GameObject level, Dictionary<string, Material> mats, string way, string levelName)
        {
            foreach (var r in level.GetComponentsInChildren<MeshRenderer>(true))
            {
                string kind = r.gameObject.name.Substring(r.gameObject.name.IndexOf('_') + 1);
                if (mats.TryGetValue($"{way}-{levelName}-{kind}", out var mat))
                    r.sharedMaterial = mat;
                else
                    Debug.LogWarning($"[LT1Street] no material for {r.gameObject.name}");
            }
        }

        /// <summary>The FBX's axes as Unity imported them: the house's cladding must sit at +x, +z (as LT1Finish).</summary>
        static void Orient(GameObject house, GameObject near)
        {
            var clad = near.GetComponentsInChildren<MeshRenderer>(true).First(r => r.gameObject.name.EndsWith("cladding"));
            var c = clad.bounds.center;
            if (c.x < 0 && c.z < 0)
                house.transform.rotation = Quaternion.Euler(0, 180, 0);
            else if (c.x < 0 || c.z < 0)
                house.transform.localScale = new Vector3(c.x < 0 ? -1 : 1, 1, c.z < 0 ? -1 : 1);
            Physics.SyncTransforms();
            Debug.Log($"[LT1Street] house oriented: cladding at {clad.bounds.center}");
        }

        static Lighting Own(Lighting l, PLight p) => p.azimuth == null || p.azimuth.Length != 2 ? l : new Lighting
        {
            name = l.name, azimuth = new Vector2(p.azimuth[0], p.azimuth[1]), elevation = p.elevation, sun = p.sun,
            shadow = p.shadow, sky = p.sky, equator = p.equator, ground = p.ground, exposure = p.exposure,
        };

        static void Light(Light sun, Lighting l, PColLight c = null)
        {
            var a = l.azimuth.normalized;
            float e = l.elevation * Mathf.Deg2Rad;
            var toSun = new Vector3(Mathf.Cos(e) * a.x, Mathf.Cos(e) * a.y, Mathf.Sin(e));
            sun.transform.rotation = Quaternion.LookRotation(-ToUnity(toSun), Vector3.up);
            sun.intensity = l.sun;
            sun.shadowStrength = l.shadow;
            sun.color = Lin(1, c?.sun);
            RenderSettings.ambientSkyColor = Lin(l.sky, c?.sky);
            RenderSettings.ambientEquatorColor = Lin(l.equator, c?.equator);
            RenderSettings.ambientGroundColor = Lin(l.ground, c?.ground);
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
    }
}
