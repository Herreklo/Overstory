using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Assembly;
using Overstory.Scenes;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The beauty corner (docs/experiments.md, LT1, the reset): its scene, its one light and its frames,
    /// all from the game's own camera. Run after blender/tools/export_street.py has written the corner at
    /// gentle and strong (see the header of blender/tools/corner_fixture.py):
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Corner.Scene
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Corner.Frames
    ///
    /// The renderer and materials are LT1's, as LT1Setup made them; this touches neither.
    /// </summary>
    public static class LT1Corner
    {
        const string Dir = "Assets/Experiments/LT1/Corner";
        const string ScenePath = Dir + "/LT1_Corner.unity";
        const string Materials = "Assets/Art/Materials";
        const string Palette = "Assets/Art/Palette";
        static readonly string[] Strengths = { "gentle", "strong" };
        static string Layout(string strength) => $"Assets/Art/Buildings/corner-{strength}/street.json";

        // The game's camera (docs/visual-direction.md, Views and Open): a 35 mm lens close in (37.8 degrees
        // vertical), longer pulled out. Street coordinates in metres.
        const float Lens35 = 37.8f, Lens60 = 22.6f;

        /// <summary>The target frames: one from each stop the player has, and the close stop turned round.</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Targets =
        {
            // close stop over the quay road, just over A's ridge, up the lane to the landing and E
            ("1-hero", new Vector3(51.5f, -16f, 15f), new Vector3(47.5f, 46f, 9f), Lens35),
            // close stop over the landing, turned round: down the lane, across the basin, into the light
            ("2-into-light", new Vector3(47f, 40f, 21f), new Vector3(46f, -120f, 2f), Lens35),
            // middle stop over the water, oblique, the horizon in frame
            ("3-middle", new Vector3(8f, -78f, 35f), new Vector3(48f, 35f, 8f), Lens35),
            // far stop, steep and map-like, a longer lens
            ("4-far", new Vector3(30f, -60f, 120f), new Vector3(48f, 32f, 5f), Lens60),
        };

        /// <summary>The close stop's honest case: eight headings round the landing, 45 m out, 13 m over the ground.</summary>
        static readonly Vector3 Landing = new Vector3(47f, 38f, 8f);
        const float HeadingRadius = 45f, StopHeight = 13f;

        public static void Scene()
        {
            Directory.CreateDirectory(Dir + "/Views");
            AssetDatabase.Refresh();

            var street = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Street.mat");
            var water = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Water.mat");
            var sky = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Sky.mat");
            if (street == null || water == null || sky == null)
                throw new FileNotFoundException("LT1's materials are missing: run LT1Setup.Scene once first");

            var rig = Asset<LightRig>(Dir + "/Corner_Oct20_1700.asset", October20);
            foreach (var (name, pos, target, fov) in Targets)
                Asset<CameraShot>($"{Dir}/Views/Corner_{name}.asset", s => Shot(s, pos, target, fov));

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.allowHDR = true;
            cam.allowMSAA = true;
            cam.clearFlags = CameraClearFlags.Skybox;
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            camData.renderShadows = true;
            camData.dithering = true;

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;

            var volume = new GameObject("Grade").AddComponent<Volume>();
            volume.isGlobal = true;

            var builder = new GameObject("The corner").AddComponent<StreetBuilder>();
            builder.enabled = false;
            builder.layout = AssetDatabase.LoadAssetAtPath<TextAsset>(Layout("gentle"));
            builder.streetMaterial = street;
            builder.waterMaterial = water;
            var files = new HashSet<string>();
            foreach (var strength in Strengths)
            {
                var text = AssetDatabase.LoadAssetAtPath<TextAsset>(Layout(strength))
                    ?? throw new FileNotFoundException($"no corner at {strength}: run blender/tools/export_street.py with --out corner-{strength}");
                var layout = StreetLayout.Parse(text.text);
                foreach (var b in layout.buildings) files.Add(b.file);
                foreach (var k in layout.kit) files.Add(k.file);
            }
            foreach (var f in files)
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(f) ?? throw new FileNotFoundException($"the corner needs {f}");
                builder.models.Add(new StreetBuilder.ModelRef { file = f, model = model });
            }

            var stage = new GameObject("Stage").AddComponent<StreetStage>();
            stage.enabled = false;
            stage.street = builder;
            stage.sun = sun;
            stage.view = cam;
            stage.volume = volume;
            stage.sky = sky;
            stage.paletteAlbedo = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_albedo.png");
            stage.paletteEmit = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_emit.png");
            stage.paletteGlow = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_glow.png");
            stage.paletteSurface = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_surface.png");
            stage.rig = rig;
            stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Corner_1-hero.asset");
            stage.look = "P";
            builder.enabled = true;
            stage.enabled = true;

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log($"[LT1Corner] scene saved: {ScenePath} ({files.Count} models)");
        }

        /// <summary>
        /// The base frames for the target paintovers (reviews/lt1/corner/base), each in colour, greyscale
        /// and at one-eighth size, and the eight headings (reviews/lt1/corner/headings).
        /// </summary>
        public static void Frames()
        {
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "corner"));
            string bases = Path.Combine(root, "base"), headings = Path.Combine(root, "headings");
            Directory.CreateDirectory(bases);
            Directory.CreateDirectory(headings);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.look = "P";
            stage.clay = false;

            foreach (var strength in Strengths)
            {
                stage.street.layout = AssetDatabase.LoadAssetAtPath<TextAsset>(Layout(strength));
                stage.street.Build();
                foreach (var (name, _, _, _) in Targets)
                {
                    if (strength != "gentle" && name != "1-hero")
                        continue; // the push in proportion is chosen on the hero frame
                    stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Corner_{name}.asset");
                    stage.Apply();
                    string file = Path.Combine(bases, $"corner-{name}-{strength}.png");
                    LT1Render.Still(stage.view, file, grey: true, eighth: true);
                    Debug.Log($"[LT1Corner] {file}");
                }
            }

            stage.street.layout = AssetDatabase.LoadAssetAtPath<TextAsset>(Layout("gentle"));
            stage.street.Build();
            var fine = stage.street.Layout.town.fine;
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            for (int k = 0; k < 8; k++)
            {
                float a = k * 45f * Mathf.Deg2Rad;
                float x = Landing.x + HeadingRadius * Mathf.Cos(a), y = Landing.y + HeadingRadius * Mathf.Sin(a);
                float ground = fine.Contains(x, y) ? Mathf.Max(fine.Sample(x, y), 0f) : 0f;
                var p = new Vector3(x, y, ground + StopHeight);
                p.z = Clear(stage.street, p); // the camera never stands in a roof or a crown
                Shot(shot, p, Landing, Lens35);
                stage.shot = shot;
                stage.Apply();
                string file = Path.Combine(headings, $"corner-heading-{k * 45:000}.png");
                LT1Render.Still(stage.view, file, grey: true, eighth: true);
                Debug.Log($"[LT1Corner] {file}");
            }
            Object.DestroyImmediate(shot);
        }

        /// <summary>The lowest height at or above p.z where the camera stands clear of every house and tree by 2 m.</summary>
        static float Clear(StreetBuilder street, Vector3 p)
        {
            var renderers = new List<MeshRenderer>();
            foreach (var t in street.GetComponentsInChildren<Transform>())
                if (t.name == "buildings" || t.name == "trees")
                    renderers.AddRange(t.GetComponentsInChildren<MeshRenderer>());
            for (int step = 0; step < 40; step++)
            {
                var u = StreetSpace.ToUnity(p);
                bool inside = false;
                foreach (var r in renderers)
                {
                    var b = r.bounds;
                    b.Expand(4f);
                    if (b.Contains(u)) { inside = true; break; }
                }
                if (!inside)
                    return p.z;
                p.z += 1f;
            }
            return p.z;
        }

        /// <summary>
        /// The clay composition (reviews/lt1/corner/clay): the corner in one matte grey, without trees, in the
        /// corner's light without cloud shadows, from the four target cameras. Judged on layout, height and
        /// composition alone; the target paintings are made over these frames. Trees are left out because no
        /// tree has been approved yet; where each stands is in docs/experiments.md.
        /// </summary>
        public static void Clay()
        {
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "corner", "clay"));
            Directory.CreateDirectory(dir);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            var rig = Object.Instantiate(stage.rig);
            rig.cloudCover = 0f;
            rig.wetness = 0f;
            stage.rig = rig;
            stage.look = "P";
            stage.clay = true;
            foreach (var strength in Strengths)
            {
                stage.street.layout = AssetDatabase.LoadAssetAtPath<TextAsset>(Layout(strength));
                stage.street.Build();
                foreach (var t in stage.street.GetComponentsInChildren<Transform>(true))
                    if (t.name == "trees")
                        t.gameObject.SetActive(false);
                foreach (var (name, _, _, _) in Targets)
                {
                    if (strength != "gentle" && name != "1-hero")
                        continue;
                    stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Corner_{name}.asset");
                    stage.Apply();
                    string file = Path.Combine(dir, $"corner-clay-{name}-{strength}.png");
                    LT1Render.Still(stage.view, file, grey: false, eighth: true);
                    Debug.Log($"[LT1Corner] {file}");
                }
            }
            Object.DestroyImmediate(rig);
        }

        static void Shot(CameraShot s, Vector3 pos, Vector3 target, float fov)
        {
            s.position = pos;
            s.target = target;
            s.verticalFov = fov;
            s.near = 0.3f;
            s.far = 6000f;
        }

        /// <summary>
        /// 20 October 1989 at 17:00, after a day of showers: the cloud breaking in the west, the sun 8 degrees
        /// up in the south-west (compass 234, which is 316 in street axes: +x is compass 190, +y compass 100),
        /// the air damp with a little haze off the fjord, the ground damp. Low October gold, not summer heat.
        /// </summary>
        static void October20(LightRig r)
        {
            r.sunBearing = 316f;
            r.sunElevation = 8.3f;
            r.sunColour = C(255, 194, 132);
            r.sunIntensity = 3.0f;
            r.shadowStrength = 1f;

            r.zenith = C(92, 120, 166);
            r.horizon = C(236, 204, 166);
            r.belowHorizon = C(62, 60, 62);
            r.skyCurve = 0.5f;
            r.sunGlow = C(255, 168, 96);
            r.sunGlowPower = 7f;

            r.ambientSky = C(106, 130, 176);
            r.ambientEquator = C(150, 140, 130);
            r.ambientGround = C(78, 72, 64);
            r.ambientIntensity = 0.6f; // little fill: shade is deep and takes the sky's colour

            r.fogColour = C(146, 136, 134);
            r.fogMidColour = C(190, 168, 152);
            r.fogMidDistance = 300f;
            r.fogFarColour = C(222, 204, 190);
            r.fogFarDistance = 2500f;
            r.fogDensity = 0.0022f;
            r.fogHeightFalloff = 0.016f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.85f;
            r.fogSunColour = C(220, 150, 92);
            r.fogSunPower = 5f;

            r.shafts = 0f; // the light-ray pass is untested; off until it is judged on its own
            r.wetness = 0.25f;
            r.cloudCover = 0.45f; // breaking cloud: the low sun falls on the town in pools
            r.cloudSize = 700f;
            r.cloudSoftness = 0.06f;
            r.cloudHeight = 1400f;
            r.windowGlow = 0f;
            r.lampsOn = false;
            r.lampGlow = 0f;
            r.lampIntensity = 0f;
            r.windowSpill = 0f;

            r.postExposure = 0.15f;
            r.contrast = 12f;
            r.saturation = 0f;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0.2f;
            r.bloomThreshold = 1.1f;
            r.reflectionStrength = 1f;
            r.clock = 0f;
        }

        static Color C(int r, int g, int b) => new Color(r / 255f, g / 255f, b / 255f);

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
