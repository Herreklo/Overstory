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

        const float Lens35 = 37.8f, Lens28 = 46.4f, Lens50 = 27.0f;

        /// <summary>The frames: (name, camera, target, vertical field of view), in street metres.</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Shots =
        {
            // close stop behind the Landing, over the roofs, across the Basin to the Holm and Watch Knoll
            ("1-over-the-roofs", new Vector3(40f, 66f, 25f), new Vector3(30f, -240f, 4f), Lens35),
            // close stop over High Terrace's downhill roofs, along the lane to the Landing
            ("2-along-high-terrace", new Vector3(-104f, 42f, 13f), new Vector3(47f, 44f, 9.5f), Lens28),
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
        };

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
                if (isWater)
                    water = ClayWater();
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

            var stage = new GameObject("Stage").AddComponent<StreetStage>();
            stage.enabled = false;
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
            foreach (var (name, _, _, _) in Shots)
            {
                stage.shot = AssetDatabase.LoadAssetAtPath<CameraShot>($"{Dir}/Views/Heart_{name}.asset");
                stage.Apply();
                string file = Path.Combine(dir, $"heart-clay-{name}.png");
                LT1Render.Still(stage.view, file, grey: false, eighth: true);
                Debug.Log($"[LT1Heart] {file}");
            }
            Object.DestroyImmediate(rig);
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
