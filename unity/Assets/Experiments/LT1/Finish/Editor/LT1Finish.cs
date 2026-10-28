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
    /// The finishing test (blender/parts/finish): house 107's street corner in 1989, one mesh finished several ways in
    /// clay (A procedural, B scanned, C both, P painted; Pc, P's values in colour), rendered from four views in two lights:
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

        [Serializable] class Mat { public string name, tile; public int painted, authored; public float paintSmooth, paintFlat, underSmooth, stainL, tideW, stainMottleL, tideL, flakeScale, islandL, grainMip, grainFade; public float[] islandW; public float[] scanMetres; }
        [Serializable] class Digest { public Mat[] mats; public float tileMetres, dirtL, waterL, cavityL, lipL, crackL, haloL, haloW, haloDull, runBody, lapDark, lapCore, lapReach, lapScale, lapPage, lapStep, groundL, groundSmooth; }
        // way P's digest (paint.py): each material one value, the strokes and the shapes' edges, and its own light
        [Serializable] class PMat { public string name; public int painted; public float L, bareL, underL, stainDL, smooth, stainSmooth, brushL, flatUp, stainEdge, ao, shadowLift; }
        [Serializable] class PLight { public string light; public float exposure, elevation, sun, shadow, sky, equator, ground; public float[] azimuth; }
        // way Pc, the colour still: P's values with a hue of luminance 1 laid on each, and each light's colour
        [Serializable] class PColMat { public string name; public float[] tint, bareTint, underTint, stainTint; }
        [Serializable] class PColLight { public string light; public float[] sun, sky, equator, ground, background, floor; }
        [Serializable] class PColour { public PColMat[] mats; public PColLight[] lights; public float[] washTint; }
        [Serializable] class Paint { public PMat[] mats; public PLight[] lights; public PColour colour; public float strokeScale, edgeAmp, rimL, rimW, rimFar, bareShift, washL, bareWash, brushFar, dragL, dragScale, dlRange, aoStrength, lapDark, lapCore, lapReach, lapGrimeL, lapGrimeReach, lapGrimeBreak, lapPage; public float[] strokeFade, brushFade, rimBreak, washFade; }

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
        // low sun: raking the street wall at 25° from the east end, so each lap throws its shadow; the gable in shade
        static readonly Lighting[] Lights =
        {
            new Lighting { name = "overcast", azimuth = new Vector2(-0.5f, -1f), elevation = 65, sun = 0.45f, shadow = 0.7f, sky = 0.95f, equator = 0.72f, ground = 0.14f, exposure = 1.6f },
            new Lighting { name = "lowsun", azimuth = new Vector2(0.906f, -0.423f), elevation = 18, sun = 2.6f, shadow = 1f, sky = 0.32f, equator = 0.24f, ground = 0.1f, exposure = 0.5f },
        };

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        public static void Run()
        {
            string round = Arg("-finishRound") ?? "r01";
            var only = (Arg("-finishViews") ?? "eye,street,raised,high").Split(',');
            var ways = (Arg("-finishWays") ?? "A,B,C").Split(',');
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outDir = Path.Combine(root, "cache", "finish", "renders", round);
            Directory.CreateDirectory(outDir);

            Import();
            // last run's materials and profile go first: writing an asset over one that exists keeps stale parts
            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { Gen }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));
            var digest = JsonUtility.FromJson<Digest>(File.ReadAllText(Path.Combine(Gen, "unity.json")));
            string paintPath = Path.Combine(Gen, "paint.json");
            var paint = File.Exists(paintPath) ? JsonUtility.FromJson<Paint>(File.ReadAllText(paintPath)) : null;
            var mats = Materials(digest, paint);
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
            // the narrowest filter: crisp batten and sill shadows, their edges still anti-aliased; the laps are too
            // small for the map at a grazing light (they alias), so the shader throws their shadows itself
            sunGo.AddComponent<UniversalAdditionalLightData>().softShadowQuality = SoftShadowQuality.Low;
            sun.shadowBias = 1f;
            sun.shadowNormalBias = 1f;

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
            cam.backgroundColor = Back;
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
            // one sharp cascade fitted to each view, put back after
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
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
                        urp.shadowCascadeCount = 1;
                        urp.mainLightShadowmapResolution = 4096;
                        urp.shadowDistance = (view.target - view.pos).magnitude + 3f;
                        foreach (var way in ways)
                        {
                            // way P is lit and exposed by its own value plan, where it names a light; way Pc as P,
                            // in the light's colours where the palette names it
                            var own = way.StartsWith("P") ? paint?.lights?.FirstOrDefault(e => e.light == light.name) : null;
                            var col = way == "Pc" ? paint?.colour?.lights?.FirstOrDefault(e => e.light == light.name) : null;
                            Light(sun, own != null ? Own(light, own) : light, col);
                            cam.backgroundColor = Lin(Back.linear.r, col?.background);
                            gm.SetColor("_BaseColor", Lin(gy, col?.floor));
                            adjust.postExposure.Override(own != null ? own.exposure : light.exposure);
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
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = urpWas;
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

        // the plain sky behind
        static readonly Color Back = new Color(0.62f, 0.62f, 0.62f);

        // a linear value as a colour, in a tint of luminance 1 where one is given, else grey
        static Color Lin(float v, float[] t) => t == null || t.Length != 3 ? new Color(v, v, v).gamma : new Color(v * t[0], v * t[1], v * t[2]).gamma;

        /// <summary>Import settings: the page and tileables linear and uncompressed, the tileables repeating.</summary>
        static void Import()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Gen }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                string n = Path.GetFileNameWithoutExtension(path);
                bool tile = n.StartsWith("tile-") || n.StartsWith("scan-") || n.StartsWith("paint-");
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
        static Dictionary<string, Material> Materials(Digest d, Paint p)
        {
            var shader = Shader.Find("Overstory/Finish");
            var tex = (Func<string, Texture2D>)(n => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/{n}.png"));
            var outp = new Dictionary<string, Material>();
            foreach (var way in new[] { "A", "B", "C" })
            foreach (var level in new[] { "near", "street" })
            foreach (var m in d.mats)
            {
                var mat = new Material(shader);
                // way A reads its own tileables, but an authored face (a scan) where the material asks for one
                bool scan = way != "A" || m.authored == 1;
                string stem = (scan ? "scan-" : "tile-") + m.tile;
                mat.SetTexture("_Tile", tex(stem));
                mat.SetTexture("_TileN", tex(stem + "-n"));
                var scale = scan ? new Vector4(d.tileMetres / m.scanMetres[0], d.tileMetres / m.scanMetres[1], 0, 0) : new Vector4(1, 1, 0, 0);
                mat.SetVector("_TileScale", scale);
                mat.SetTexture("_Hist", tex(way == "B" ? "hist-b" : "hist-a"));
                mat.SetTexture("_Geo", tex("geo"));
                mat.SetTexture("_StreetN", tex("street-normal"));
                // way A's painted faces flake by the flake atlas; a scan keeps its own breakup
                mat.SetTexture("_Flake", tex("tile-flake"));
                mat.SetFloat("_FlakeScale", scan ? 0 : m.flakeScale);
                mat.SetFloat("_HaloL", d.haloL);
                mat.SetFloat("_HaloW", d.haloW);
                mat.SetFloat("_HaloDull", d.haloDull);
                mat.SetFloat("_RunBody", d.runBody);
                mat.SetFloat("_Painted", m.painted);
                mat.SetFloat("_PaintSmooth", m.paintSmooth);
                mat.SetFloat("_UnderSmooth", m.underSmooth);
                mat.SetFloat("_PaintFlat", m.paintFlat);
                mat.SetFloat("_StainL", m.stainL);
                mat.SetFloat("_TideW", m.tideW);
                mat.SetFloat("_StainMottleL", m.stainMottleL);
                mat.SetFloat("_TideL", m.tideL);
                mat.SetVector("_IslandW", new Vector4(m.islandW[0], m.islandW[1], 0, 0));
                mat.SetFloat("_IslandL", m.islandL);
                mat.SetFloat("_GrainMip", m.grainMip);
                mat.SetFloat("_GrainFade", m.grainFade);
                mat.SetFloat("_DirtL", d.dirtL);
                mat.SetFloat("_WaterL", d.waterL);
                mat.SetFloat("_CavityL", d.cavityL);
                mat.SetFloat("_LapDark", d.lapDark);
                mat.SetFloat("_LapCore", d.lapCore);
                mat.SetFloat("_LipL", d.lipL);
                mat.SetFloat("_CrackL", d.crackL);
                mat.SetFloat("_LapReach", d.lapReach);
                mat.SetFloat("_LapScale", d.lapScale);
                mat.SetFloat("_LapPage", d.lapPage);
                mat.SetFloat("_LapStep", d.lapStep);
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
            if (p == null)
                return outp;
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
                // the geometry's own facts are the same for every way
                mat.SetFloat("_LapScale", d.lapScale);
                mat.SetFloat("_LapPage", p.lapPage);
                mat.SetFloat("_LapStep", d.lapStep);
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

        static Vector4 Tint(float[] t) => t == null || t.Length != 3 ? Vector4.one : new Vector4(t[0], t[1], t[2], 1);

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

        // way P's own light where its plan gives one whole, else the light with only P's exposure
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
