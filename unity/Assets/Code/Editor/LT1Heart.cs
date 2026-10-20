using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The heart of the town in clay (docs/town-plan.md; blender/blockouts/heart_build.py): its scene and its
    /// frames, all from the game's own camera, in the corner's light (20 October 1989, 17:00).
    ///
    ///     blender -b --factory-startup --python blender/blockouts/heart_build.py -- unity
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Heart.Scene
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Heart.Frames
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Heart.LightFrames [-frames 1,5] [-hours 1600]
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Heart.NightFrames [-frames 1,9] [-moods hopeful]
    ///
    /// The renderer and materials are LT1's; this touches neither.
    /// </summary>
    public static class LT1Heart
    {
        const string Dir = "Assets/Experiments/LT1/Heart";
        const string ScenePath = Dir + "/LT1_Heart.unity";
        const string Models = "Assets/Art/Blockout/heart";
        const string Materials = "Assets/Art/Materials";
        const string Palette = "Assets/Art/Palette";
        const string Rig = "Assets/Experiments/LT1/Corner/Corner_Oct20_1700.asset";
        const string Lights = Dir + "/Light";

        const float Lens35 = 37.8f, Lens28 = 46.4f, Lens50 = 27.0f;

        /// <summary>The frames: (name, camera, target, vertical field of view), in street metres.</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Shots =
        {
            // close stop behind the Landing, over the roofs, across the Basin to the Holm and Watch Knoll
            ("1-over-the-roofs", new Vector3(40f, 66f, 25f), new Vector3(30f, -240f, 4f), Lens35),
            // close stop over High Terrace's downhill roofs, along the lane to the Landing
            ("2-along-high-terrace", new Vector3(-150f, 36.7f, 12.5f), new Vector3(20f, 36.5f, 9f), Lens28),
            // the street stop on Gully Steps, three metres over them, up to the Landing
            ("3-street-gully-steps", new Vector3(49.3f, 12f, 5.6f), new Vector3(47.5f, 44f, 10.5f), Lens28),
            // the middle stop over the Basin's mouth, into the heart
            ("4-middle", new Vector3(-150f, -110f, 48f), new Vector3(150f, 30f, 8f), Lens35),
            // the far stop, steep and map-like
            ("5-far", new Vector3(-480f, -360f, 320f), new Vector3(120f, -40f, 0f), Lens50),
            // from the Roads, the town in its landscape
            ("6-from-the-roads", new Vector3(-720f, -120f, 8f), new Vector3(100f, 60f, 22f), Lens50),
            // from Lookout Park over the Roads: Bridge Island, the High Bridge, the platform in the fjord
            ("7-from-lookout-park", new Vector3(26f, 214f, 58f), new Vector3(-2100f, 1500f, 60f), Lens35),
            // the middle stop over the Basin's head, at Watch Knoll and the Fire Watch above Holm Street
            ("8-watch-knoll", new Vector3(10f, -110f, 42f), new Vector3(140f, -330f, 26f), Lens35),
            // the street stop on Harbour Row's quay, along the lamps towards the Basin's head
            ("9-harbour-row-quay", new Vector3(-30f, -9.5f, 4.4f), new Vector3(150f, -7f, 4.0f), Lens28),
        };

        /// <summary>The frames named after -frames on the command line (by number, e.g. -frames 5,8), or all.</summary>
        static bool Wanted(string name)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-frames");
            if (i < 0 || i + 1 >= args.Length)
                return true;
            return System.Array.IndexOf(args[i + 1].Split(','), name.Split('-')[0]) >= 0;
        }

        public static void Scene()
        {
            Directory.CreateDirectory(Dir + "/Views");
            AssetDatabase.Refresh();
            var street = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Street.mat");
            var water = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Water.mat");
            var sky = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Sky.mat");
            var rig = AssetDatabase.LoadAssetAtPath<LightRig>(Rig);
            if (street == null || water == null || sky == null || rig == null)
                throw new FileNotFoundException("LT1's materials or the corner's rig are missing: run LT1Setup.Scene and LT1Corner.Scene first");
            foreach (var (name, pos, target, fov) in Shots)
                Asset<CameraShot>($"{Dir}/Views/Heart_{name}.asset", s =>
                {
                    s.position = pos;
                    s.target = target;
                    s.verticalFov = fov;
                    s.near = 0.3f;
                    s.far = 9000f;
                });

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cam = new GameObject("Camera") { tag = "MainCamera" }.AddComponent<Camera>();
            cam.allowHDR = true;
            cam.allowMSAA = true;
            cam.clearFlags = CameraClearFlags.Skybox;
            var camData = cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            camData.renderShadows = true;
            camData.dithering = true;
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            var volume = new GameObject("Grade").AddComponent<Volume>();
            volume.isGlobal = true;

            var heart = new GameObject("The heart (clay)");
            int n = 0;
            foreach (var path in Directory.GetFiles(Models, "*.fbx"))
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path.Replace('\\', '/'));
                if (model == null)
                    continue;
                var go = (GameObject)PrefabUtility.InstantiatePrefab(model, heart.transform);
                bool isWater = model.name.StartsWith("water");
                foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
                {
                    var mats = new Material[r.sharedMaterials.Length];
                    for (int i = 0; i < mats.Length; i++)
                        mats[i] = isWater ? water : street;
                    r.sharedMaterials = mats;
                    r.shadowCastingMode = isWater ? ShadowCastingMode.Off : ShadowCastingMode.On;
                }
                n++;
            }

            // the town's sky map over the heart (street x -390 to 540, y -480 to 330), half a metre a texel
            var skyMap = heart.AddComponent<SkyMap>();
            skyMap.enabled = false;
            skyMap.town = heart.transform;
            skyMap.centre = new Vector2(75f, -75f);
            skyMap.size = 1024f;
            skyMap.resolution = 2048;
            skyMap.enabled = true;

            var lamps = new GameObject("Lamps").AddComponent<TownLights>();
            lamps.source = AssetDatabase.LoadAssetAtPath<TextAsset>(Models + "/lights.json");
            lamps.Build();
            EnsureFogLights();

            var probe = new GameObject("Sky reflection").AddComponent<ReflectionProbe>();
            probe.size = new Vector3(20000f, 4000f, 20000f);
            probe.resolution = 256;
            probe.hdr = true;

            var stage = new GameObject("Stage").AddComponent<StreetStage>();
            stage.enabled = false;
            stage.skyMap = skyMap;
            stage.skyReflection = probe;
            stage.townLights = lamps;
            stage.sun = sun;
            stage.view = cam;
            stage.volume = volume;
            stage.sky = sky;
            stage.paletteAlbedo = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_albedo.png");
            stage.paletteEmit = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_emit.png");
            stage.paletteGlow = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_glow.png");
            stage.paletteSurface = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_surface.png");
            stage.rig = rig;
            stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{Shots[0].name}.asset");
            stage.look = "P";
            stage.clay = true;
            stage.enabled = true;
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log($"[LT1Heart] scene saved: {ScenePath} ({n} models)");
        }

        /// <summary>
        /// The clay frames (reviews/lt1/heart/clay): the heart in one matte grey, in the corner's light without cloud
        /// shadows and with thinner air, so the structure reads at every distance. Each at full size and at one-eighth.
        /// </summary>
        public static void Frames()
        {
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "clay"));
            Directory.CreateDirectory(dir);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            var rig = Object.Instantiate(stage.rig);
            rig.cloudCover = 0f;
            rig.wetness = 0f;
            rig.fogDensity *= 0.35f;
            stage.rig = rig;
            stage.clay = true;
            stage.look = "P";
            var map = stage.skyMap;
            stage.skyMap = null; // the flat clay: lit as if every point saw the whole sky, as the clay was first judged
            var waters = new List<(MeshRenderer, Material[])>();
            var clayWater = ClayWater();
            foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                if (r.gameObject.name.StartsWith("water") || (r.transform.parent != null && r.transform.parent.name.StartsWith("water")))
                {
                    waters.Add((r, r.sharedMaterials));
                    var m = new Material[r.sharedMaterials.Length];
                    for (int i = 0; i < m.Length; i++)
                        m[i] = clayWater;
                    r.sharedMaterials = m;
                }
            foreach (var (name, _, _, _) in Shots)
            {
                if (!Wanted(name))
                    continue;
                stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                stage.Apply();
                string file = Path.Combine(dir, $"heart-clay-{name}.png");
                LT1Render.Still(stage.view, file, grey: false, eighth: true);
                Debug.Log($"[LT1Heart] {file}");
            }
            Object.DestroyImmediate(rig);
            stage.skyMap = map;
            foreach (var (r, m) in waters)
                r.sharedMaterials = m;
        }

        // -- light, air and atmosphere (docs/experiments.md, LT1, light on the clay) ------------------------------

        /// <summary>The colour script: four hours of 20 October 1989, the sun from the clock (Norway on winter time, UTC+1).</summary>
        public static readonly string[] Hours = { "0930-morning", "1300-drizzle", "1600-low-sun", "1750-blue-hour" };

        /// <summary>Writes the four rigs. Their colours are chosen as an artist would; the sun is the clock's.</summary>
        public static void Rigs()
        {
            Directory.CreateDirectory(Lights);
            AssetDatabase.Refresh();
            Asset<LightRig>($"{Lights}/Heart_{Hours[0]}.asset", r =>
            {
                // a clear cold morning: the sun low in the south-east behind Herring Hill, the old town in its own shade,
                // a white haze on the water
                Clock(r, 9.5f);
                Sun(r, C(1.0f, 0.86f, 0.70f), 2.4f, 1f);
                Sky(r, C(0.40f, 0.55f, 0.76f), C(0.80f, 0.82f, 0.84f), C(0.25f, 0.26f, 0.28f), 0.55f, C(0.95f, 0.80f, 0.62f), 6f, Color.black);
                Shade(r, C(0.46f, 0.57f, 0.76f), C(0.56f, 0.60f, 0.68f), C(0.82f, 0.76f, 0.66f), C(0.32f, 0.31f, 0.29f), C(0.40f, 0.38f, 0.35f), 0.7f);
                Air(r, C(0.66f, 0.70f, 0.76f), C(0.74f, 0.77f, 0.82f), C(0.84f, 0.86f, 0.88f), 0.0006f, C(0.70f, 0.60f, 0.48f), 5f);
                Haze(r, C(0.86f, 0.88f, 0.90f), 0.0035f, 12f);
                Clouds(r, 0.2f, 0.12f, 0.25f);
                Grading(r, 0.05f, 8f, 0f, 0.1f);
            });
            Asset<LightRig>($"{Lights}/Heart_{Hours[1]}.asset", r =>
            {
                // grey drizzle at midday: the sun a pale disc behind the cloud, light from the whole sky, the far shore gone
                Clock(r, 13f);
                Sun(r, C(0.92f, 0.94f, 0.97f), 0.45f, 0.35f);
                Sky(r, C(0.60f, 0.63f, 0.67f), C(0.75f, 0.77f, 0.79f), C(0.30f, 0.31f, 0.32f), 0.7f, C(0.12f, 0.12f, 0.11f), 3f, Color.black);
                Shade(r, C(0.72f, 0.75f, 0.80f), C(0.62f, 0.65f, 0.68f), C(0.66f, 0.68f, 0.70f), C(0.32f, 0.33f, 0.33f), C(0.30f, 0.31f, 0.32f), 1.0f);
                Air(r, C(0.62f, 0.66f, 0.70f), C(0.70f, 0.73f, 0.76f), C(0.76f, 0.78f, 0.80f), 0.0014f, C(0.05f, 0.05f, 0.05f), 3f);
                r.fogMidDistance = 220f;
                r.fogFarDistance = 1500f;
                r.fogMaxOpacity = 0.92f;
                Haze(r, C(0.78f, 0.80f, 0.82f), 0.004f, 25f);
                Clouds(r, 0.97f, 0.15f, 0f);
                r.cloudHeight = 900f;
                r.wetness = 0.85f;
                Grading(r, 0.2f, 4f, -5f, 0f);
            });
            Asset<LightRig>($"{Lights}/Heart_{Hours[2]}.asset", r =>
            {
                // the corner's light: the sun 8 degrees high in the south-west after a day of showers, the cloud
                // breaking in the west, a little haze off the fjord
                Clock(r, 16f);
                Sun(r, C(1.0f, 0.72f, 0.46f), 3.0f, 1f);
                Sky(r, C(0.33f, 0.46f, 0.68f), C(0.94f, 0.80f, 0.63f), C(0.24f, 0.23f, 0.24f), 0.5f, C(1.0f, 0.62f, 0.34f), 7f, C(0.12f, 0.08f, 0.10f));
                Shade(r, C(0.40f, 0.51f, 0.72f), C(0.50f, 0.53f, 0.62f), C(0.80f, 0.64f, 0.50f), C(0.33f, 0.29f, 0.25f), C(0.46f, 0.38f, 0.31f), 0.62f);
                Air(r, C(0.60f, 0.60f, 0.66f), C(0.76f, 0.69f, 0.66f), C(0.90f, 0.80f, 0.70f), 0.0006f, C(0.86f, 0.56f, 0.32f), 5f);
                Haze(r, C(0.88f, 0.78f, 0.68f), 0.0025f, 16f);
                Clouds(r, 0.32f, 0.12f, 0.35f);
                r.wetness = 0.25f;
                Grading(r, 0.1f, 10f, 0f, 0.2f);
            });
            Asset<LightRig>($"{Lights}/Heart_{Hours[3]}.asset", r =>
            {
                // blue hour: the sun five degrees down, an orange glow low in the west, the pink band in the east,
                // the high cloud still lit
                Clock(r, 17f + 50f / 60f);
                Sun(r, Color.black, 0f, 0f);
                Sky(r, C(0.16f, 0.24f, 0.44f), C(0.50f, 0.46f, 0.56f), C(0.10f, 0.10f, 0.13f), 0.45f, C(0.78f, 0.42f, 0.22f), 4f, C(0.32f, 0.22f, 0.34f));
                Shade(r, C(0.24f, 0.32f, 0.54f), C(0.26f, 0.30f, 0.46f), C(0.44f, 0.36f, 0.42f), C(0.11f, 0.11f, 0.13f), C(0.10f, 0.10f, 0.13f), 1.0f);
                Air(r, C(0.26f, 0.30f, 0.44f), C(0.33f, 0.35f, 0.50f), C(0.48f, 0.44f, 0.56f), 0.0007f, C(0.40f, 0.24f, 0.18f), 4f);
                Haze(r, C(0.40f, 0.42f, 0.54f), 0.003f, 18f);
                Clouds(r, 0.3f, 0.12f, 0.45f);
                Grading(r, 0.35f, 6f, 0f, 0f);
            });
            AssetDatabase.SaveAssets();
            foreach (var h in Hours)
            {
                var r = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{h}.asset");
                Debug.Log($"[LT1Heart] {h}: sun {r.sunElevation:F1} degrees high, street bearing {r.sunBearing:F0}");
            }
        }

        static Color C(float r, float g, float b) => new Color(r, g, b);

        static void Clock(LightRig r, float hour)
        {
            r.sunFromClock = true;
            r.year = 1989;
            r.month = 10;
            r.day = 20;
            r.hour = hour;
            r.utcOffset = 1f; // summer time ended on 24 September 1989
            r.latitude = 58.97f;
            r.longitude = 5.73f;
            r.streetAxisCompass = 190f;
            r.SetSunFromClock();
        }

        static void Sun(LightRig r, Color colour, float intensity, float shadow)
        {
            r.sunColour = colour;
            r.sunIntensity = intensity;
            r.shadowStrength = shadow;
        }

        static void Sky(LightRig r, Color zenith, Color horizon, Color below, float curve, Color glow, float glowPower, Color anti)
        {
            r.zenith = zenith;
            r.horizon = horizon;
            r.belowHorizon = below;
            r.skyCurve = curve;
            r.sunGlow = glow;
            r.sunGlowPower = glowPower;
            r.antiGlow = anti;
        }

        static void Shade(LightRig r, Color sky, Color away, Color sunSide, Color ground, Color town, float intensity)
        {
            r.ambientSky = sky;
            r.ambientEquator = away;
            r.ambientSunSide = sunSide;
            r.ambientGround = ground;
            r.townBounce = town;
            r.ambientIntensity = intensity;
        }

        static void Air(LightRig r, Color near, Color middle, Color far, float density, Color sun, float sunPower)
        {
            r.fogColour = near;
            r.fogMidColour = middle;
            r.fogMidDistance = 300f;
            r.fogFarColour = far;
            r.fogFarDistance = 2500f;
            r.fogDensity = density;
            r.fogHeightFalloff = 0.012f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.85f;
            r.fogSunColour = sun;
            r.fogSunPower = sunPower;
        }

        static void Haze(LightRig r, Color colour, float density, float height)
        {
            r.hazeColour = colour;
            r.hazeDensity = density;
            r.hazeHeight = height;
        }

        static void Clouds(LightRig r, float cover, float softness, float high)
        {
            r.cloudCover = cover;
            r.cloudSize = 2400f; // big masses, as a painter simplifies a sky; their shadows lie on the town in broad patches
            r.cloudSoftness = softness;
            r.cloudHeight = 1400f;
            r.highCloud = high;
        }

        static void Grading(LightRig r, float exposure, float contrast, float saturation, float bloom)
        {
            r.postExposure = exposure;
            r.contrast = contrast;
            r.saturation = saturation;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = bloom;
            r.bloomThreshold = 1.1f;
        }

        /// <summary>
        /// The light frames (reviews/lt1/heart/light/&lt;hour&gt;/): every camera at every hour, in clay with the town's sky
        /// map, in colour, greyscale and at one-eighth. Sun shadows reach as far as the stop needs.
        /// </summary>
        public static void LightFrames()
        {
            Rigs();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            if (stage.skyMap != null)
                stage.skyMap.Build();
            CheckSkyMap(stage.skyMap);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            try
            {
                foreach (var hour in Hours)
                {
                    if (!WantedHour(hour))
                        continue;
                    string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "light", hour));
                    Directory.CreateDirectory(dir);
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{hour}.asset");
                    foreach (var (name, pos, target, _) in Shots)
                    {
                        if (!Wanted(name))
                            continue;
                        urp.shadowDistance = Mathf.Clamp(Vector3.Distance(pos, target) * 2.2f, 150f, 2000f);
                        stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                        stage.Apply();
                        string file = Path.Combine(dir, $"heart-{hour}-{name}.png");
                        LT1Render.Still(stage.view, file, grey: true, eighth: true);
                        Debug.Log($"[LT1Heart] {file}");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
            }
        }

        // -- blue hour in sea fog, with the town's lights; the moods (docs/experiments.md, LT1) -----------------------

        const string Night = "1750-sea-fog";
        public static readonly string[] Moods = { "hopeless", "hopeful", "grand", "sad", "gritty", "success" };

        /// <summary>The rig: 17:50 on Friday 20 October 1989, the sun five degrees down, a bank of sea fog on the water.</summary>
        static LightRig NightRig()
        {
            Directory.CreateDirectory(Lights);
            AssetDatabase.Refresh();
            return Asset<LightRig>($"{Lights}/Heart_{Night}.asset", r =>
            {
                Clock(r, 17f + 50f / 60f);
                Sun(r, Color.black, 0f, 0f);
                // a sky mostly fog: blue overhead, a last dull glow low in the west, tight to where the sun went down
                Sky(r, C(0.13f, 0.20f, 0.38f), C(0.32f, 0.37f, 0.50f), C(0.08f, 0.09f, 0.12f), 0.5f, C(0.30f, 0.17f, 0.12f), 10f, C(0.10f, 0.08f, 0.13f));
                Shade(r, C(0.22f, 0.30f, 0.50f), C(0.24f, 0.29f, 0.42f), C(0.32f, 0.30f, 0.40f), C(0.10f, 0.10f, 0.12f), C(0.12f, 0.11f, 0.12f), 1.0f);
                Air(r, C(0.17f, 0.25f, 0.41f), C(0.21f, 0.29f, 0.45f), C(0.29f, 0.34f, 0.49f), 0.0008f, C(0.14f, 0.09f, 0.07f), 8f);
                r.fogMaxOpacity = 0.97f;
                // the sea fog: thick on the water, thinning over a dozen metres, so the hills stand out of it
                Haze(r, C(0.19f, 0.28f, 0.45f), 0.019f, 12f);
                Clouds(r, 0.9f, 0.2f, 0f);
                r.wetness = 0.75f;
                r.lampsOn = true;
                r.lampIntensity = 10f;
                r.lampGlow = 24f;
                r.lampHalo = 4f;
                r.windowGlow = 1.3f;
                r.windowSpill = 0f;
                Grading(r, 0.6f, 8f, 0f, 0.5f);
                r.bloomThreshold = 1.3f; // above the sky, so only the lamps and lit windows glow
            });
        }

        /// <summary>The moods as recipes, until target paintings give their looks (a graded strip in a painted frame).</summary>
        static void WriteMoods()
        {
            Directory.CreateDirectory(Lights + "/Moods");
            AssetDatabase.Refresh();
            Mood("hopeless", "Nothing will change: the colour drained to a sick grey-green, flat, the blacks lifted to fog, the edges closing in.", g =>
            {
                // the darks and middle drained; a lit window keeps its warmth (a fact), only dimmer
                g.exposure = -0.2f; g.contrast = -12f; g.saturation = -28f; g.filter = C(0.94f, 1.0f, 0.93f);
                g.lift = new Vector4(0.98f, 1.0f, 0.97f, 0.03f); g.gain = new Vector4(0.96f, 0.98f, 0.94f, -0.05f);
                g.splitShadows = C(0.45f, 0.52f, 0.47f); g.splitHighlights = C(0.52f, 0.52f, 0.49f);
                g.shadowSaturation = 0.15f; g.vignette = 0.34f; g.grain = 0.3f; g.bloom = -0.2f; g.bloomScatter = 0.5f;
            });
            Mood("hopeful", "It may yet turn out well: warmer highlights over a light, cool shade, lifted, a soft glow round the lights.", g =>
            {
                g.exposure = 0.25f; g.contrast = 4f; g.saturation = 10f; g.temperature = 10f;
                g.lift = new Vector4(1.0f, 1.0f, 1.02f, 0.02f); g.gain = new Vector4(1.04f, 1.0f, 0.95f, 0.02f);
                g.splitShadows = C(0.47f, 0.50f, 0.56f); g.splitHighlights = C(0.62f, 0.54f, 0.44f); g.splitBalance = 20f;
                g.shadowSaturation = 0.9f; g.vignette = 0.12f; g.grain = 0.12f; g.bloom = 0.45f; g.bloomScatter = 0.85f;
            });
            Mood("grand", "The town as larger than the people in it: deep contrast, rich colour, cool shade against warm light, distance in clear layers.", g =>
            {
                // depth, not more blue: the cool comes from the hour already, so the grade warms the lights against it
                g.contrast = 14f; g.saturation = -4f;
                g.lift = new Vector4(1.0f, 0.99f, 0.99f, -0.02f); g.gain = new Vector4(1.04f, 1.0f, 0.95f, 0.03f);
                g.splitShadows = C(0.50f, 0.50f, 0.50f); g.splitHighlights = C(0.62f, 0.53f, 0.42f); g.splitBalance = 10f;
                g.shadowSaturation = 1.0f; g.vignette = 0.25f; g.grain = 0.1f; g.bloom = 0.25f; g.bloomScatter = 0.75f;
            });
            Mood("sad", "A loss: low contrast, the colour going out of it, cool shade, the haze shown more than the light.", g =>
            {
                g.exposure = -0.1f; g.contrast = -10f; g.saturation = -30f; g.temperature = -12f;
                g.lift = new Vector4(0.98f, 1.0f, 1.03f, 0.03f);
                g.splitShadows = C(0.44f, 0.48f, 0.56f); g.splitHighlights = C(0.50f, 0.50f, 0.52f);
                g.shadowSaturation = 0.6f; g.vignette = 0.22f; g.grain = 0.18f; g.bloom = 0f; g.bloomScatter = 0.6f;
            });
            Mood("gritty", "Hard going: hard contrast, crushed blacks, dirty teal against rust, coarse grain.", g =>
            {
                // hard, not black: the shadows keep their shapes
                g.exposure = 0.05f; g.contrast = 16f; g.saturation = -15f;
                g.lift = new Vector4(0.98f, 1.0f, 1.0f, -0.015f); g.gamma = new Vector4(1.0f, 0.99f, 0.97f, -0.02f);
                g.splitShadows = C(0.43f, 0.51f, 0.52f); g.splitHighlights = C(0.60f, 0.51f, 0.42f);
                g.shadowSaturation = 0.5f; g.vignette = 0.3f; g.grain = 0.45f; g.bloom = -0.1f; g.bloomScatter = 0.5f;
            });
            Mood("success", "It worked: bright, warm, clean whites, colour up, a generous glow.", g =>
            {
                g.exposure = 0.4f; g.contrast = 10f; g.saturation = 20f; g.temperature = 8f;
                g.gain = new Vector4(1.03f, 1.01f, 0.97f, 0.04f);
                g.splitShadows = C(0.48f, 0.50f, 0.54f); g.splitHighlights = C(0.60f, 0.55f, 0.46f); g.splitBalance = 25f;
                g.shadowSaturation = 1.0f; g.vignette = 0.08f; g.grain = 0.06f; g.bloom = 0.6f; g.bloomScatter = 0.85f;
            });
            AssetDatabase.SaveAssets();
        }

        static void Mood(string name, string intent, System.Action<Grade> set) =>
            Asset<Grade>($"{Lights}/Moods/Mood_{name}.asset", g =>
            {
                // start each recipe from neutral, so a value left out is neutral rather than last time's
                var neutral = ScriptableObject.CreateInstance<Grade>();
                EditorUtility.CopySerialized(neutral, g);
                Object.DestroyImmediate(neutral);
                g.intent = intent;
                set(g);
            });

        /// <summary>
        /// The night frames (reviews/lt1/heart/night/): every camera at 17:50 in sea fog, neutral; then the street, the
        /// roofs, the middle and the quay in each mood. Colour, greyscale and one-eighth.
        /// </summary>
        public static void NightFrames()
        {
            NightRig();
            WriteMoods();
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            // loaded only now: opening a scene unloads assets nothing in it holds, and a rig made before would be gone
            var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{Night}.asset");
            var args = System.Environment.GetCommandLineArgs();
            int hi = System.Array.IndexOf(args, "-halo"); // a check: -halo 0 renders without the lamps' light in the fog
            if (hi >= 0 && hi + 1 < args.Length)
                rig.lampHalo = float.Parse(args[hi + 1], System.Globalization.CultureInfo.InvariantCulture);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            stage.rig = rig;
            if (stage.skyMap != null)
                stage.skyMap.Build();
            if (stage.townLights != null)
                stage.townLights.Build();
            Debug.Log($"[LT1Heart] {(stage.townLights != null ? stage.townLights.Count : 0)} lamps; sun {rig.sunElevation:F1} degrees");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "night"));
            try
            {
                var runs = new List<(string mood, string[] shots)> { ("neutral", null) };
                foreach (var mood in Moods)
                    runs.Add((mood, new[] { "1", "3", "4", "9" }));
                foreach (var (mood, only) in runs)
                {
                    if (!WantedMood(mood))
                        continue;
                    stage.mood = mood == "neutral" ? null : AssetDatabase.LoadAssetAtPath<Grade>($"{Lights}/Moods/Mood_{mood}.asset");
                    string dir = Path.Combine(root, mood);
                    Directory.CreateDirectory(dir);
                    foreach (var (name, pos, target, _) in Shots)
                    {
                        if (!Wanted(name) || (only != null && System.Array.IndexOf(only, name.Split('-')[0]) < 0))
                            continue;
                        urp.shadowDistance = Mathf.Clamp(Vector3.Distance(pos, target) * 2.2f, 150f, 2000f);
                        stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                        stage.Apply();
                        string file = Path.Combine(dir, $"heart-night-{mood}-{name}.png");
                        LT1Render.Still(stage.view, file, grey: true, eighth: true);
                        Debug.Log($"[LT1Heart] {file}");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                stage.mood = null;
            }
        }

        /// <summary>A check: every model in the heart's scene, with its size, place and material.</summary>
        public static void Inventory()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
            {
                var mf = r.GetComponent<MeshFilter>();
                var mesh = mf != null ? mf.sharedMesh : null;
                Debug.Log($"[LT1Heart] {r.gameObject.name}: {(mesh ? mesh.vertexCount : 0)} vertices, uv {(mesh ? mesh.uv.Length : 0)}, " +
                          $"colours {(mesh ? mesh.colors.Length : 0)}, bounds {r.bounds.center} {r.bounds.size}, " +
                          $"enabled {r.enabled}, material {(r.sharedMaterial ? r.sharedMaterial.name : "none")}");
            }
            var lamps = Object.FindAnyObjectByType<TownLights>();
            Debug.Log($"[LT1Heart] lamps: {(lamps ? lamps.Count : -1)}");
        }

        static bool WantedMood(string mood)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-moods");
            return i < 0 || i + 1 >= args.Length || System.Array.IndexOf(args[i + 1].Split(','), mood) >= 0;
        }

        /// <summary>The fog's lamps: a full-screen pass after the opaque scene, before post-processing, on the renderer.</summary>
        static void EnsureFogLights()
        {
            const string renderer = "Assets/Settings/PC_Renderer.asset";
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(renderer);
            if (data == null || data.rendererFeatures.Exists(f => f != null && f.name == "FogLights"))
                return;
            const string path = Materials + "/M_FogLights.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Overstory/FogLights") ?? throw new FileNotFoundException("FogLights.shader did not compile"));
                AssetDatabase.CreateAsset(mat, path);
            }
            var feature = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
            feature.name = "FogLights";
            feature.passMaterial = mat;
            feature.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
            feature.requirements = ScriptableRenderPassInput.Depth;
            feature.fetchColorBuffer = true;
            AssetDatabase.AddObjectToAsset(feature, data);
            AssetDatabase.TryGetGUIDAndLocalFileIdentifier(feature, out string _, out long id);
            var so = new SerializedObject(data);
            var list = so.FindProperty("m_RendererFeatures");
            list.arraySize++;
            list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue = feature;
            var map = so.FindProperty("m_RendererFeatureMap");
            map.arraySize++;
            map.GetArrayElementAtIndex(map.arraySize - 1).longValue = id;
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(data);
            AssetDatabase.SaveAssets();
            Debug.Log("[LT1Heart] the fog's lamps added to the renderer");
        }

        static bool WantedHour(string hour)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-hours");
            if (i < 0 || i + 1 >= args.Length)
                return true;
            return System.Array.IndexOf(args[i + 1].Split(','), hour.Split('-')[0]) >= 0;
        }

        /// <summary>
        /// Proves the sky map lies the right way round: the Fire Watch's top must read about 60 m where it stands,
        /// and the map must not show it mirrored. Writes the map as a picture beside the frames.
        /// </summary>
        static void CheckSkyMap(SkyMap map)
        {
            if (map == null || !map.Built)
            {
                Debug.LogWarning("[LT1Heart] no sky map");
                return;
            }
            // the Fire Watch stands at street (140, -318); with the map mirrored in v it would read at z = 2 * centre - z
            float at = map.Probe(140f, -318f), mirror = map.Probe(140f, 2f * map.centre.y + 318f);
            Debug.Log($"[LT1Heart] sky map, sampled as the street shader samples it: the Fire Watch reads {at:F1} m, its mirror {mirror:F1} m");
            if (!(at > 50f))
                Debug.LogError("[LT1Heart] the sky map is not the right way round (or the Fire Watch has moved)");
            var h = map.ReadHeights();
            if (h.Length == 0)
                return;
            int n = map.resolution;
            var tex = new Texture2D(n, n, TextureFormat.RGB24, false, false);
            var px = new Color32[n * n];
            for (int i = 0; i < px.Length; i++)
            {
                byte g = (byte)Mathf.Clamp(Mathf.RoundToInt((h[i] + 2f) * 3.2f), 0, 255);
                px[i] = h[i] < -500f ? new Color32(40, 60, 90, 255) : new Color32(g, g, g, 255);
            }
            tex.SetPixels32(px);
            tex.Apply();
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "light"));
            Directory.CreateDirectory(dir);
            File.WriteAllBytes(Path.Combine(dir, "sky-map.png"), tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
        }

        /// <summary>The water for clay frames: dark and glossy, outside the clay switch, so it reads as water.</summary>
        static Material ClayWater()
        {
            const string path = Materials + "/M_ClayWater.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(m, path);
            }
            m.SetColor("_BaseColor", new Color(0.14f, 0.17f, 0.21f));
            m.SetFloat("_Smoothness", 0.88f);
            m.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(m);
            return m;
        }

        static T Asset<T>(string path, System.Action<T> set) where T : ScriptableObject
        {
            var a = AssetDatabase.LoadAssetAtPath<T>(path);
            if (a == null)
            {
                a = ScriptableObject.CreateInstance<T>();
                AssetDatabase.CreateAsset(a, path);
            }
            set(a);
            EditorUtility.SetDirty(a);
            return a;
        }
    }
}
