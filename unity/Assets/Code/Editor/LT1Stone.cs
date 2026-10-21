using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The second part, stone (docs/experiments.md, LT1, the second part; docs/stone.md): the gully steps laid from
    /// their facts (blender/generators/stone.py), stood where the plan puts them in the heart (the clay steps hidden)
    /// and drawn by the stone shader, from eye level on and at the foot of the steps, the target frame's street stop,
    /// 12 m and the city camera, in drizzle, low sun and the blue hour.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Stone.Frames
    ///         [-moments 1300-drizzle,...] [-views eye-foot,...] [-grey]
    ///
    /// Frames go to reviews/lt1/stone/gully/.
    /// </summary>
    public static class LT1Stone
    {
        const string Art = "Assets/Art/Stone";
        const string HeartDir = "Assets/Experiments/LT1/Heart";
        const string HeartScene = HeartDir + "/LT1_Heart.unity";
        const string Lights = HeartDir + "/Light";
        const float Lens28 = 46.4f, Lens35 = 37.8f;

        [System.Serializable]
        class Info { public string name; public float[] origin; }

        static string Arg(string flag, string fallback)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, flag);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }

        static bool Wanted(string flag, string value)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, flag);
            if (i < 0 || i + 1 >= args.Length)
                return true;
            foreach (var w in args[i + 1].Split(','))
                if (value.StartsWith(w))
                    return true;
            return false;
        }

        static bool Flag(string flag) => System.Array.IndexOf(System.Environment.GetCommandLineArgs(), flag) >= 0;

        /// <summary>The slaty rock's material: its pigments set here (a saved material keeps its values; a shader's
        /// later default never reaches it), as eye colours.</summary>
        public static Material Material(bool grey)
        {
            string path = $"{Art}/M_Stone_slate.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find("Overstory/Stone"));
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = Shader.Find("Overstory/Stone");
            // the town's own rock (the board, 02, 03, 06): weathered to a blue-grey, freshly split darker and bluer;
            // its split faces a little warmer
            m.SetColor("_Stone", new Color(0.56f, 0.565f, 0.57f));
            m.SetColor("_Fresh", new Color(0.38f, 0.40f, 0.43f));
            m.SetColor("_Edge", new Color(0.58f, 0.565f, 0.55f));
            m.SetTexture("_GrainMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{Art}/slate_grain.png"));
            m.SetVector("_Grain", new Vector4(1.0f, 1.0f, 0.14f, 0f));
            m.SetFloat("_Weather", 60f);
            m.SetVector("_Polish", new Vector4(0.18f, 0.42f, 0f, 0f));
            m.SetVector("_Relief", new Vector4(0.0016f, 0.0012f, 0f, 0f));
            m.SetFloat("_Porosity", 0.5f);
            m.SetFloat("_Grey", grey ? 1f : 0f);
            m.SetFloat("_History", Flag("-history") ? 1f : Flag("-albedo") ? 2f : 0f);
            m.enableInstancing = true;
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>The stair stood where its mesh was laid from (its street origin), the clay steps hidden.</summary>
        static (GameObject go, Vector3 origin) Place(string which, Material mat)
        {
            string fbx = $"{Art}/stone_{which}.fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            if (model == null)
                throw new FileNotFoundException($"no stair at {fbx}: run blender/generators/stone.py first");
            var info = JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(Application.dataPath, "..", fbx[..^4] + ".json")));
            var origin = new Vector3(info.origin[0], info.origin[1], info.origin[2]);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
            go.transform.SetPositionAndRotation(StreetSpace.ToUnity(origin), Quaternion.identity);
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                r.sharedMaterial = mat;
                r.shadowCastingMode = ShadowCastingMode.On;
            }
            // the importer turns each child half round (its axis conversion); the mesh itself is already in street
            // order (x across, y up, z along), so the children are set straight (a tree never showed it: it looks the
            // same turned round)
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
                mf.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            // the clay steps the stone replaces
            foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                if (r.gameObject.name == "steps" && !Flag("-clay-steps"))
                    r.enabled = false;
            return (go, origin);
        }

        public static void Frames()
        {
            LT1Heart.Rigs();
            LT1Heart.NightRig();
            LT1Heart.WriteStyles();
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(HeartScene, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            stage.style = Flag("-nostyle") ? null : AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset");
            if (stage.skyMap != null)
                stage.skyMap.Build();
            if (stage.townLights != null)
                stage.townLights.Build();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool grey = Flag("-grey");
            // the pack's growth (lichen, moss), set once for the whole town
            GrowthPack.Apply();
            var mat = Material(grey);
            AssetDatabase.SaveAssets();
            var (go, o) = Place("gully", mat);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "stone", "gully"));
            // the flight's path in street metres (heart_layout: Gully Steps): the lower flight from Low Terrace to the
            // Landing, the upper from the Landing to Top Terrace
            var foot = new Vector3(49.2f, 24.6f, 3.0f);
            var lowerMid = new Vector3(48.6f, 30.7f, 5.5f);
            var landing = new Vector3(47.3f, 40.0f, 8.0f);
            var upperMid = new Vector3(46.5f, 62.0f, 12.2f);
            var views = new (string name, Vector3 pos, Vector3 target, float fov)[]
            {
                // eye level: a person at the foot of the steps, looking up them
                ("eye-foot", foot + new Vector3(0.6f, -3.2f, 1.7f), lowerMid + new Vector3(0f, 0f, 0.4f), Lens35),
                // eye level on the steps, halfway up, looking at the treads ahead
                ("eye-on", new Vector3(49.6f, 28.4f, 4.3f + 1.65f), new Vector3(48.7f, 33.5f, 6.4f), Lens35),
                // close: the treads underfoot, a person looking down at them
                ("eye-down", new Vector3(50.2f, 27.0f, 3.9f + 1.6f), new Vector3(49.1f, 29.2f, 4.4f), Lens35),
                // the target frame's street stop (LT1Heart.Shots, 3)
                ("street", new Vector3(49.3f, 12f, 5.6f), new Vector3(47.5f, 44f, 10.5f), Lens28),
                // 12 m up beside the flight, looking down along it
                ("into12", new Vector3(56f, 18f, 3f + 12f), lowerMid, Lens28),
                // the city camera, pulled out and steep (near-isometric)
                ("high", new Vector3(80f, 2f, 60f), new Vector3(48.5f, 36f, 7f), 15f),
            };
            try
            {
                foreach (var moment in new[] { "1300-drizzle", "1600-low-sun", "1750-blue-hour" })
                {
                    if (!Wanted("-moments", moment))
                        continue;
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        continue;
                    stage.rig = rig;
                    string dir = Path.Combine(outDir, moment);
                    Directory.CreateDirectory(dir);
                    foreach (var (view, pos, target, fov) in views)
                    {
                        if (!Wanted("-views", view))
                            continue;
                        shot.position = pos;
                        shot.target = target;
                        shot.verticalFov = fov;
                        shot.near = 0.1f;
                        shot.far = 9000f;
                        urp.shadowDistance = 120f;
                        stage.shot = shot;
                        stage.Apply();
                        string file = Path.Combine(dir, $"gully-{view}{(grey ? "-greylight" : "")}{(Flag("-history") ? "-history" : "")}{(Flag("-albedo") ? "-albedo" : "")}{(Flag("-nostyle") ? "-nostyle" : "")}.png");
                        LT1Render.Still(stage.view, file, grey: true, eighth: true, msaa: 4);
                        Debug.Log($"[LT1Stone] {file}");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }
    }
}
