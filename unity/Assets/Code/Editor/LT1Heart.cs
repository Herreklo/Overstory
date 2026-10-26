using System.Collections.Generic;
using System.Linq;
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
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Heart.StyleFrames [-frames 1,9] [-styles nocturne]
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
            // the close stop over the Landing, down the lanes and across the Basin into the low sun of 16:00
            ("10-into-the-light", new Vector3(40f, 60f, 21f), new Vector3(256f, -147f, 4f), Lens35),
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
            EnsurePass("Palette", "Overstory/Palette", FullScreenPassRendererFeature.InjectionPoint.AfterRenderingPostProcessing,
                       ScriptableRenderPassInput.None);
            EnsurePass("SunBeams", "Overstory/SunBeams", FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing,
                       ScriptableRenderPassInput.Depth);
            var air = new GameObject("Air").AddComponent<AirMotes>();
            air.material = MaterialAsset("M_AirMotes", "Overstory/AirMotes");
            air.Build();

            var probe = new GameObject("Sky reflection").AddComponent<ReflectionProbe>();
            probe.size = new Vector3(20000f, 4000f, 20000f);
            probe.resolution = 256;
            probe.hdr = true;

            var stage = new GameObject("Stage").AddComponent<StreetStage>();
            stage.enabled = false;
            stage.skyMap = skyMap;
            stage.skyReflection = probe;
            stage.townLights = lamps;
            stage.motes = air;
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

        /// <summary>Writes the four rigs, each a view of its light record (fixtures/light/1989-10-20-hour.json).</summary>
        public static void Rigs()
        {
            Directory.CreateDirectory(Lights);
            AssetDatabase.Refresh();
            foreach (var h in Hours)
            {
                var r = LT1Light.Rig($"1989-10-20-{h}", $"{Lights}/Heart_{h}.asset");
                Debug.Log($"[LT1Heart] {h}: sun {r.sunElevation:F1} degrees high, street bearing {r.sunBearing:F0}");
            }
            AssetDatabase.SaveAssets();
        }

        static Color C(float r, float g, float b) => new Color(r, g, b);

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

        /// <summary>The rig: 17:50 on Friday 20 October 1989, the sun five degrees down, a bank of sea fog on the water (the blue hour's record).</summary>
        internal static LightRig NightRig()
        {
            Directory.CreateDirectory(Lights);
            AssetDatabase.Refresh();
            var r = LT1Light.Rig("1989-10-20-1750-blue-hour", $"{Lights}/Heart_{Night}.asset");
            AssetDatabase.SaveAssets();
            return r;
        }

        /// <summary>The moods as recipes, until target paintings give their looks (a graded strip in a painted frame).</summary>
        static void WriteMoods()
        {
            Directory.CreateDirectory(Lights + "/Moods");
            AssetDatabase.Refresh();
            // a mood moves exposure, contrast, how much colour the shade keeps, and the lens; never a light's hue, never
            // anything that reads as weather (docs/visual-direction.md, Mood)
            Mood("hopeless", "Nothing will change: under-exposed and flat, the shade drained of colour, the edges closing in.", g =>
            {
                g.exposure = -0.3f; g.contrast = -10f; g.shadowSaturation = 0.15f; g.vignette = 0.36f; g.grain = 0.3f; g.bloom = -0.2f; g.bloomScatter = 0.5f;
            });
            Mood("sad", "A loss: a little low, soft contrast, the colour going out of the shade.", g =>
            {
                g.exposure = -0.12f; g.contrast = -8f; g.shadowSaturation = 0.45f; g.vignette = 0.2f; g.grain = 0.15f; g.bloomScatter = 0.6f;
            });
            Mood("gritty", "Hard going: hard contrast that keeps the shapes, the shade half drained, coarse grain.", g =>
            {
                g.contrast = 18f; g.shadowSaturation = 0.5f; g.vignette = 0.3f; g.grain = 0.45f; g.bloom = -0.1f; g.bloomScatter = 0.5f;
            });
            Mood("hopeful", "It may yet turn out well: opened up, the shade keeping its colour, a soft glow round the lights.", g =>
            {
                g.exposure = 0.25f; g.contrast = 2f; g.shadowSaturation = 1.0f; g.vignette = 0.1f; g.grain = 0.1f; g.bloom = 0.4f; g.bloomScatter = 0.85f;
            });
            Mood("grand", "The town larger than the people in it: deep contrast, rich shade, the lights against it.", g =>
            {
                g.contrast = 16f; g.shadowSaturation = 1.15f; g.vignette = 0.25f; g.grain = 0.08f; g.bloom = 0.2f; g.bloomScatter = 0.75f;
            });
            Mood("success", "It worked: bright, clean, rich shade and a generous glow.", g =>
            {
                g.exposure = 0.4f; g.contrast = 8f; g.shadowSaturation = 1.2f; g.vignette = 0.05f; g.grain = 0.05f; g.bloom = 0.5f; g.bloomScatter = 0.85f;
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
            WriteStyles();
            stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset"); // the game's style
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

        // -- the game's style, after the masters of colour (docs/research/masters-of-colour.md) -----------------------

        public static readonly string[] Styles = { "nocturne", "luminous", "painted", "game" };

        /// <summary>Three candidate styles, to be judged beside the unstylised look on the same frames.</summary>
        internal static void WriteStyles()
        {
            Directory.CreateDirectory(Lights + "/Styles");
            AssetDatabase.Refresh();
            StyleAsset("nocturne", "After Whistler's nocturnes, Jansson's blue Stockholm and Grimshaw's lamplit quays: the picture is the air; " +
                                   "a few close values of blue and slate, lights as points of gold, distance in soft layers of tone.", st =>
            {
                st.shade = C(0.07f, 0.09f, 0.16f); st.lowMiddle = C(0.19f, 0.25f, 0.35f); st.highMiddle = C(0.44f, 0.48f, 0.52f); st.light = C(0.98f, 0.82f, 0.54f);
                st.ramp = 0.55f; st.spare = 0.85f;
                st.valueSteps = 5; st.grouping = 0.35f; st.groupSoftness = 0.35f;
                st.airLayers = 5; st.airLayerSoftness = 0.4f;
                st.shadeChroma = 1.0f; st.turningEdge = C(0.95f, 0.6f, 0.35f); st.turningEdgeStrength = 0.12f;
                st.vibrance = 0.1f; st.rolloff = 0.4f; st.glowTint = C(1.0f, 0.78f, 0.5f); st.glow = 0.2f;
                st.contrast = -6f; st.saturation = -10f;
            });
            StyleAsset("luminous", "After Shinkai's skies, Oga's backgrounds, Mary Blair and Firewatch: the ordinary made radiant; saturated air, " +
                                   "violet shade against coral and gold light, glow round every light, distance in crisp layers.", st =>
            {
                st.shade = C(0.12f, 0.08f, 0.28f); st.lowMiddle = C(0.17f, 0.31f, 0.55f); st.highMiddle = C(0.95f, 0.58f, 0.46f); st.light = C(1.0f, 0.93f, 0.72f);
                st.ramp = 0.45f; st.spare = 0.7f;
                st.valueSteps = 0; st.grouping = 0f;
                st.airLayers = 6; st.airLayerSoftness = 0.2f;
                st.shadeChroma = 1.6f; st.turningEdge = C(1.0f, 0.45f, 0.2f); st.turningEdgeStrength = 0.45f;
                st.vibrance = 0.45f; st.rolloff = 0.2f; st.glowTint = C(1.0f, 0.72f, 0.6f); st.glow = 0.5f;
                st.contrast = 8f; st.saturation = 12f;
            });
            StyleAsset("painted", "After Sorolla and Sargent, Sohlberg and Hopper: painterly realism pushed; full-colour shade, a warm band where light " +
                                  "turns, values gathered into masses, light shapes designed, deep saturated darks.", st =>
            {
                st.shade = C(0.10f, 0.10f, 0.21f); st.lowMiddle = C(0.30f, 0.29f, 0.42f); st.highMiddle = C(0.72f, 0.63f, 0.52f); st.light = C(1.0f, 0.90f, 0.74f);
                st.ramp = 0.3f; st.spare = 0.85f;
                st.valueSteps = 4; st.grouping = 0.25f; st.groupSoftness = 0.35f;
                st.airLayers = 4; st.airLayerSoftness = 0.45f;
                st.shadeChroma = 1.8f; st.turningEdge = C(1.0f, 0.5f, 0.25f); st.turningEdgeStrength = 0.5f;
                st.vibrance = 0.3f; st.rolloff = 0.35f; st.glowTint = C(1.0f, 0.82f, 0.6f); st.glow = 0.15f;
                st.contrast = 10f;
            });
            StyleAsset("game", "The game's style (approved by Øystein, 20 October): painted's restraint in chroma " +
                                "as the system, luminous's warm and cool split at the focus, nocturne's handling of the fog. Stålenhag and " +
                                "Hopper: strong value, moderate chroma, one warm accent.", st =>
            {
                st.shade = C(0.10f, 0.11f, 0.22f); st.lowMiddle = C(0.26f, 0.29f, 0.40f); st.highMiddle = C(0.70f, 0.62f, 0.52f); st.light = C(1.0f, 0.90f, 0.72f);
                st.ramp = 0.35f; st.followLight = 0.65f; st.spare = 0.85f;
                st.valueSteps = 5; st.grouping = 0.25f; st.groupSoftness = 0.35f;
                st.airLayers = 5; st.airLayerSoftness = 0.4f;
                st.shadeChroma = 1.4f; st.turningEdge = C(1.0f, 0.52f, 0.28f); st.turningEdgeStrength = 0.35f;
                st.vibrance = 0.2f; st.rolloff = 0.35f; st.chromaFocus = 0.6f;
                st.glowTint = C(1.0f, 0.82f, 0.6f); st.glow = 0.15f;
                st.contrast = 6f;
            });
            AssetDatabase.SaveAssets();
        }

        static void StyleAsset(string name, string intent, System.Action<Style> set) =>
            Asset<Style>($"{Lights}/Styles/Style_{name}.asset", st =>
            {
                var neutral = ScriptableObject.CreateInstance<Style>();
                EditorUtility.CopySerialized(neutral, st);
                Object.DestroyImmediate(neutral);
                st.intent = intent;
                set(st);
            });

        /// <summary>
        /// The style frames (reviews/lt1/heart/style/): 16:00 low sun and 17:50 in sea fog, from the roofs, the steps, the
        /// middle and the quay, unstylised and in each candidate style.
        /// </summary>
        public static void StyleFrames()
        {
            Rigs();
            NightRig();
            WriteStyles();
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            EnsurePass("Palette", "Overstory/Palette", FullScreenPassRendererFeature.InjectionPoint.AfterRenderingPostProcessing,
                       ScriptableRenderPassInput.None);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            if (stage.skyMap != null)
                stage.skyMap.Build();
            if (stage.townLights != null)
                stage.townLights.Build();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "style"));
            var args = System.Environment.GetCommandLineArgs();
            int si = System.Array.IndexOf(args, "-styles");
            try
            {
                foreach (var moment in new[] { "1600-low-sun", Night })
                {
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    foreach (var styleName in new[] { "none" }.Concat(Styles))
                    {
                        if (si >= 0 && si + 1 < args.Length && System.Array.IndexOf(args[si + 1].Split(','), styleName) < 0)
                            continue;
                        stage.style = styleName == "none" ? null : AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_{styleName}.asset");
                        string dir = Path.Combine(root, moment, styleName);
                        Directory.CreateDirectory(dir);
                        foreach (var (name, pos, target, _) in Shots)
                        {
                            if (System.Array.IndexOf(new[] { "1", "3", "9", "10" }, name.Split('-')[0]) < 0 || !Wanted(name))
                                continue;
                            urp.shadowDistance = Mathf.Clamp(Vector3.Distance(pos, target) * 2.2f, 150f, 2000f);
                            stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                            stage.Apply();
                            string file = Path.Combine(dir, $"heart-{moment}-{styleName}-{name}.png");
                            LT1Render.Still(stage.view, file, grey: true, eighth: true);
                            Debug.Log($"[LT1Heart] {file}");
                        }
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                stage.style = null;
            }
        }

        static Material MaterialAsset(string name, string shader)
        {
            string path = $"{Materials}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find(shader) ?? throw new FileNotFoundException($"{shader} did not compile"));
                AssetDatabase.CreateAsset(m, path);
            }
            return m;
        }

        /// <summary>Puts a full-screen pass on the renderer once, at its injection point, with its own material.</summary>
        static void EnsurePass(string name, string shader, FullScreenPassRendererFeature.InjectionPoint at, ScriptableRenderPassInput needs)
        {
            const string renderer = "Assets/Settings/PC_Renderer.asset";
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(renderer);
            if (data == null || data.rendererFeatures.Exists(f => f != null && f.name == name))
                return;
            string path = $"{Materials}/M_{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find(shader) ?? throw new FileNotFoundException($"{shader} did not compile"));
                AssetDatabase.CreateAsset(mat, path);
            }
            var feature = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
            feature.name = name;
            feature.passMaterial = mat;
            feature.injectionPoint = at;
            feature.requirements = needs;
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
            Debug.Log($"[LT1Heart] {name} added to the renderer");
        }

        /// <summary>
        /// The passes a target frame is painted over (reviews/lt1/heart/target/): the frame itself in the game's style,
        /// then, raw, what each pixel is made of (its palette UV; water marked blue), which way it faces, where it is
        /// (modulo 8 m, for patterns that stay on the surface) and how far it is.
        /// </summary>
        public static void TargetPasses()
        {
            NightRig();
            WriteStyles();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{Night}.asset");
            stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset");
            stage.skyMap?.Build();
            stage.townLights?.Build();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "heart", "target"));
            Directory.CreateDirectory(dir);
            var data = stage.view.GetComponent<UniversalAdditionalCameraData>();
            try
            {
                foreach (var (name, pos, target, _) in Shots)
                {
                    if (!Wanted(name) || System.Array.IndexOf(new[] { "3" }, name.Split('-')[0]) < 0 && !System.Environment.CommandLine.Contains("-frames"))
                        continue;
                    urp.shadowDistance = Mathf.Clamp(Vector3.Distance(pos, target) * 2.2f, 150f, 2000f);
                    stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                    Shader.SetGlobalFloat("_OS_Debug", 0f);
                    data.renderPostProcessing = true;
                    stage.Apply();
                    LT1Render.Still(stage.view, Path.Combine(dir, $"{name}-render.png"), grey: true, eighth: false);
                    // the same frame without the light in the air (the lamps' halos, the sun's beams, the town's glow),
                    // so the paintover can re-light surfaces and give the air back untouched
                    Shader.SetGlobalFloat("_OS_FogLampStrength", 0f);
                    Shader.SetGlobalVector("_OS_SunBeams", Vector4.zero);
                    Shader.SetGlobalVector("_OS_GlowParams", Vector4.zero);
                    LT1Render.Still(stage.view, Path.Combine(dir, $"{name}-render-noair.png"), grey: false, eighth: false);
                    stage.Apply();
                    // the raw passes: no post, no style, no lamps' or sun's light in the air
                    data.renderPostProcessing = false;
                    var style = stage.style;
                    stage.style = null;
                    stage.Apply();
                    Shader.SetGlobalFloat("_OS_FogLampStrength", 0f);
                    Shader.SetGlobalVector("_OS_SunBeams", Vector4.zero);
                    Shader.SetGlobalFloat("_OS_PaletteOn", 0f);
                    foreach (var (k, pass) in new[] { (1f, "material"), (2f, "normal"), (3f, "position"), (4f, "distance"), (5f, "gloss") })
                    {
                        Shader.SetGlobalFloat("_OS_Debug", k);
                        LT1Render.Raw(stage.view, Path.Combine(dir, $"{name}-{pass}.png"));
                    }
                    Shader.SetGlobalFloat("_OS_Debug", 0f);
                    stage.style = style;
                    data.renderPostProcessing = true;
                    Debug.Log($"[LT1Heart] target passes for {name}");
                }
            }
            finally
            {
                Shader.SetGlobalFloat("_OS_Debug", 0f);
                data.renderPostProcessing = true;
                urp.shadowDistance = reach;
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
