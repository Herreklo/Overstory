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
        class Flight { public string name; public float[] a; public float[] b; public float width; public int steps; public float rise; public float tread; public float[] S; }

        [System.Serializable]
        class Info { public string name; public float[] origin; public Flight[] flights; }

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
            m.SetColor("_Stone", new Color(0.50f, 0.505f, 0.51f));     // (weathered slate, a mid-dark grey under its lichen; the board, 06)
            m.SetColor("_Fresh", new Color(0.38f, 0.40f, 0.43f));
            m.SetColor("_Edge", new Color(0.58f, 0.565f, 0.55f));
            m.SetTexture("_GrainMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{Art}/slate_grain.png"));
            // (the bedding plane's soft values at full strength read as cloud shadows across every tread)
            m.SetVector("_Grain", new Vector4(0.4f, 0.2f, 0.14f, 0f));
            m.SetFloat("_Weather", 100f);
            m.SetVector("_Polish", new Vector4(0.06f, 0.42f, 0f, 0f));     // the worn line clean, scarcely darker
            m.SetVector("_Relief", new Vector4(0.0016f, 0.0012f, 0f, 0f));
            // its answer to water (Water.hlsl): dense slate darkens near black wet (the board, 02), glazes where feet
            // polished it, sheds water and dries fast, streaks a little
            m.SetVector("_Water", new Vector4(0.85f, 1.0f, 0.2f, 0.55f));
            // the repairs' cement (upkeep.py): a little paler and warmer than the slate even when old, greying with grime
            m.SetColor("_Cement", new Color(0.72f, 0.71f, 0.67f));
            m.SetColor("_CementOld", new Color(0.54f, 0.53f, 0.50f));
            m.SetColor("_CementFilm", new Color(0.25f, 0.28f, 0.22f));
            m.SetColor("_Soil", new Color(0.32f, 0.30f, 0.26f));     // (a joint at Dale is dark, 7 to 12% of white, never black)
            m.SetColor("_Streak", new Color(0.24f, 0.26f, 0.21f));   // (water's film on a face: algae and grime, dark green-grey)
            m.SetFloat("_Grey", grey ? 1f : 0f);
            m.SetFloat("_History", Flag("-history") ? 1f : Flag("-albedo") ? 2f : Flag("-normals") ? 3f : 0f);
            m.enableInstancing = true;
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>
        /// The cheek walls' rubble: the rock that came out of cutting the gully, laid dry, not the stair's chosen
        /// slabs (an element shares the town's systems, never another's look): warmer, every stone its own value and
        /// hue (some rusty, some greenish, some blue-grey), rougher, its upright faces weathered sooner.
        /// </summary>
        public static Material RubbleMaterial(bool grey)
        {
            string path = $"{Art}/M_Stone_rubble.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Material(grey));
                AssetDatabase.CreateAsset(m, path);
            }
            m.CopyPropertiesFromMaterial(Material(grey));
            m.SetColor("_Stone", new Color(0.54f, 0.52f, 0.49f));
            m.SetColor("_Fresh", new Color(0.44f, 0.44f, 0.44f));
            m.SetColor("_Edge", new Color(0.56f, 0.53f, 0.49f));
            m.SetVector("_Grain", new Vector4(0.45f, 0.35f, 0.42f, 0.65f));    // (w: each stone's own hue)
            m.SetFloat("_Weather", 70f);
            m.SetVector("_Polish", new Vector4(0.08f, 0.45f, 0f, 0f));    // (hand-worn: a coping's inner edge, darker and smoother)
            // (rubble: mixed, more porous; darkens unevenly, takes less glaze, dries slower, streaks more)
            m.SetVector("_Water", new Vector4(0.75f, 0.6f, 0.5f, 0.9f));
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>
        /// Dressed granite, brought in for money (a stair's facts choose it: stair_facts.py): a mid grey speckled
        /// rock, paler than the slate, weathering slowly, worn smooth and glossy where feet go, darkening little when
        /// wet and glazing over (its own water profile), its own painted grain (granite_grain.png).
        /// </summary>
        public static Material GraniteMaterial(bool grey)
        {
            string path = $"{Art}/M_Stone_granite.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Material(grey));
                AssetDatabase.CreateAsset(m, path);
            }
            m.CopyPropertiesFromMaterial(Material(grey));
            m.SetColor("_Stone", new Color(0.62f, 0.61f, 0.60f));
            m.SetColor("_Fresh", new Color(0.58f, 0.58f, 0.58f));
            m.SetColor("_Edge", new Color(0.60f, 0.59f, 0.58f));
            m.SetTexture("_GrainMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{Art}/granite_grain.png"));
            m.SetVector("_Grain", new Vector4(1.0f, 1.0f, 0.10f, 0.15f));
            m.SetFloat("_Weather", 140f);
            m.SetVector("_Polish", new Vector4(0.05f, 0.55f, 0f, 0f));
            m.SetVector("_Water", new Vector4(0.45f, 0.9f, 0.1f, 0.3f));
            EditorUtility.SetDirty(m);
            return m;
        }

        [System.Serializable]
        class Facts { public string name; public string stone; }

        /// <summary>The stair stood where its mesh was laid from (its street origin), the clay steps hidden.</summary>
        static (GameObject go, Vector3 origin) Place(string which, Material mat, string folder = "")
        {
            string fbx = $"{Art}/{folder}stone_{which}.fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            if (model == null)
                throw new FileNotFoundException($"no stair at {fbx}: run blender/generators/stone.py first");
            var info = JsonUtility.FromJson<Info>(File.ReadAllText(Path.Combine(Application.dataPath, "..", fbx[..^4] + ".json")));
            var origin = new Vector3(info.origin[0], info.origin[1], info.origin[2]);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
            go.transform.SetPositionAndRotation(StreetSpace.ToUnity(origin), Quaternion.identity);
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                // (a step-ramp's setts are their own granite whatever its kerbs are)
                r.sharedMaterial = r.name.Contains("_setts") ? GraniteMaterial(mat.GetFloat("_Grey") > 0.5f) : mat;
                r.shadowCastingMode = ShadowCastingMode.On;
            }
            // the importer turns each child half round (its axis conversion); the mesh itself is already in street
            // order (x across, y up, z along), so the children are set straight (a tree never showed it: it looks the
            // same turned round)
            // (a single-mesh FBX is imported as one object: straighten it in place, never move it to the origin)
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
                if (mf.transform == go.transform)
                    mf.transform.rotation = Quaternion.identity;
                else
                    mf.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            // the clay steps the stone replaces
            foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                if (r.gameObject.name == "steps" && !Flag("-clay-steps"))
                    r.enabled = false;
            if (!Flag("-clay-steps"))
            {
                SinkGround(info);
                if (folder != "")
                    return (go, origin);
                // the cheek walls (blender/generators/wall.py), where they are built, in place of the clay's
                string wfbx = $"{Art}/stone_{which}_cheeks.fbx";
                var wmodel = AssetDatabase.LoadAssetAtPath<GameObject>(wfbx);
                if (wmodel != null)
                {
                    var wgo = (GameObject)PrefabUtility.InstantiatePrefab(wmodel);
                    wgo.transform.SetPositionAndRotation(StreetSpace.ToUnity(origin), Quaternion.identity);
                    var rubble = RubbleMaterial(mat.GetFloat("_Grey") > 0.5f);
                    foreach (var r in wgo.GetComponentsInChildren<MeshRenderer>())
                    {
                        r.sharedMaterial = rubble;
                        r.shadowCastingMode = ShadowCastingMode.On;
                    }
                    foreach (var mf in wgo.GetComponentsInChildren<MeshFilter>())
                        mf.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
                    CutClayWalls(info);

                }
            }
            return (go, origin);
        }

        /// <summary>The clay's walls along the flights, cut away where the stone walls stand (in memory, for the frames).</summary>
        static void CutClayWalls(Info info)
        {
            if (info.flights == null)
                return;
            foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
            {
                if (mf.gameObject.name != "walls")
                    continue;
                var mesh = Object.Instantiate(mf.sharedMesh);
                var v = mesh.vertices;
                var l2w = mf.transform.localToWorldMatrix;
                for (int sub = 0; sub < mesh.subMeshCount; sub++)
                {
                    var tris = mesh.GetTriangles(sub);
                    var keep = new System.Collections.Generic.List<int>(tris.Length);
                    for (int t = 0; t < tris.Length; t += 3)
                    {
                        var c = (l2w.MultiplyPoint3x4(v[tris[t]]) + l2w.MultiplyPoint3x4(v[tris[t + 1]]) + l2w.MultiplyPoint3x4(v[tris[t + 2]])) / 3f;
                        bool cut = false;
                        foreach (var f in info.flights)
                        {
                            var a = new Vector2(f.a[0], f.a[1]);
                            var d = new Vector2(f.b[0] - f.a[0], f.b[1] - f.a[1]);
                            float run = d.magnitude;
                            var up = d / run;
                            var p = new Vector2(c.x, c.z) - a;
                            float s = Vector2.Dot(p, up), tt = Mathf.Abs(up.y * p.x - up.x * p.y);
                            if (s > -0.5f && s < run + 0.5f && tt < f.width / 2 + 1.4f)
                                cut = true;
                        }
                        if (!cut)
                        {
                            keep.Add(tris[t]);
                            keep.Add(tris[t + 1]);
                            keep.Add(tris[t + 2]);
                        }
                    }
                    mesh.SetTriangles(keep, sub);
                }
                mf.sharedMesh = mesh;
            }
        }

        /// <summary>
        /// The clay ground carves a stepped lane as a ramp, and its coarse triangles lift the ramp over the
        /// steps (a wedge over the first tread). Under each flight the ground is lowered to a line beneath
        /// the foot of every riser (a line through points on a line stays under the steps), rising to the
        /// treads' level a little beside the flight; in memory, for the frames, until the lane's own paving
        /// meets the flight.
        /// </summary>
        static void SinkGround(Info info)
        {
            if (info.flights == null)
                return;
            foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
            {
                if (!mf.gameObject.name.StartsWith("ground_heart"))
                    continue;
                var mesh = Object.Instantiate(mf.sharedMesh);
                var v = mesh.vertices;
                var l2w = mf.transform.localToWorldMatrix;
                var w2l = mf.transform.worldToLocalMatrix;
                foreach (var f in info.flights)
                {
                    var a = new Vector2(f.a[0], f.a[1]);
                    var d = new Vector2(f.b[0] - f.a[0], f.b[1] - f.a[1]);
                    float run = d.magnitude;
                    var up = d / run;
                    var right = new Vector2(up.y, -up.x);
                    float slope = (f.b[2] - f.a[2]) / run;
                    for (int i = 0; i < v.Length; i++)
                    {
                        var wp = l2w.MultiplyPoint3x4(v[i]);          // Unity (x, up, y)
                        var p = new Vector2(wp.x, wp.z) - a;
                        float s = Vector2.Dot(p, up), t = Mathf.Abs(Vector2.Dot(p, right));
                        if (s < 0.05f || s > run + 0.3f || t > f.width / 2 + 1.6f)
                            continue;
                        // under the foot of every riser, following the flight's own set-out (its landings run flat
                        // where a straight line would rise through them), and a little beside the flight up to the
                        // treads' own level
                        float inner = f.a[2] + (s - 0.03f) * slope - 0.12f;
                        if (f.S != null && f.S.Length > 0)
                        {
                            // (the ground is a 1.5 m grid: a triangle spans several steps, so each vertex goes under
                            // the lowest stair surface its triangles reach, the stair 1.6 m back, or the straight
                            // triangle between two vertices crossed above the steps between them)
                            int k = 0;
                            while (k < f.S.Length && f.S[k] <= s - 1.6f)
                                k++;
                            inner = f.a[2] + k * f.rise - 0.12f;
                        }
                        if (s < f.tread + 0.1f)
                            inner = Mathf.Max(inner, f.a[2] - 0.02f);     // (under the first step the lane meets its foot)
                        float beside = Mathf.Clamp01((t - f.width / 2) / 1.6f);
                        float limit = inner + beside * (0.12f + f.rise);
                        if (wp.y > limit)
                        {
                            wp.y = limit;
                            v[i] = w2l.MultiplyPoint3x4(wp);
                        }
                    }
                }
                mesh.vertices = v;
                mesh.RecalculateBounds();
                mf.sharedMesh = mesh;
            }
        }

        /// <summary>
        /// The gully's judging views, in street metres (also the measuring tools': LT1Golden, LT1Perf, LT1Motion). The
        /// flight's path (heart_layout: Gully Steps): the lower flight from Low Terrace to the Landing, the upper from
        /// the Landing to Top Terrace.
        /// </summary>
        internal static readonly Vector3 Foot = new Vector3(49.2f, 24.6f, 3.0f), LowerMid = new Vector3(48.6f, 30.7f, 5.5f);
        internal static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Views =
        {
            // eye level: a person at the foot of the steps, looking up them
            ("eye-foot", Foot + new Vector3(0.6f, -3.2f, 1.7f), LowerMid + new Vector3(0f, 0f, 0.4f), Lens35),
            // eye level on the steps, halfway up, looking at the treads ahead
            ("eye-on", new Vector3(49.6f, 28.4f, 4.3f + 1.65f), new Vector3(48.7f, 33.5f, 6.4f), Lens35),
            // close: the treads underfoot, a person looking down at them
            ("eye-down", new Vector3(50.2f, 27.0f, 3.9f + 1.6f), new Vector3(49.1f, 29.2f, 4.4f), Lens35),
            // the target frame's street stop (LT1Heart.Shots, 3)
            ("street", new Vector3(49.3f, 12f, 5.6f), new Vector3(47.5f, 44f, 10.5f), Lens28),
            // 12 m up beside the flight, looking down along it
            ("into12", new Vector3(56f, 18f, 3f + 12f), LowerMid, Lens28),
            // the city camera, pulled out and steep (near-isometric)
            ("high", new Vector3(80f, 2f, 60f), new Vector3(48.5f, 36f, 7f), 15f),
        };

        /// <summary>The gully's three judging lights (docs/foundations.md, The judging views).</summary>
        internal static readonly string[] Moments = { "1300-drizzle", "1600-low-sun", "1750-blue-hour" };

        /// <summary>
        /// The heart opened and staged as the gully's frames see it: the rigs and styles written, the clay town in look P
        /// and the game's style (none with -nostyle), the sky map and lamps built, the pack's growth and water set, the
        /// stone's material written, and the stair placed (the clay steps hidden, the ground sunk, the cheek walls in).
        /// </summary>
        internal static (StreetStage stage, GameObject go) Stage(bool grey)
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
            // the pack's growth (lichen, moss), set once for the whole town
            GrowthPack.Apply();
            WaterPack.Apply();
            // -detail painted|real: one end of "true up close, painted from afar" everywhere, to compare
            string detail = Arg("-detail", "");
            Shader.SetGlobalFloat("_OS_NearForce", detail == "painted" ? 1f : detail == "real" ? 2f : 0f);
            var mat = Material(grey);
            AssetDatabase.SaveAssets();
            var (go, _) = Place("gully", mat);
            return (stage, go);
        }

        /// <summary>The camera put on one of the gully's views, with the frames' near and far planes and shadow reach.</summary>
        internal static void Aim(StreetStage stage, CameraShot shot, (string name, Vector3 pos, Vector3 target, float fov) view)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            shot.position = view.pos;
            shot.target = view.target;
            shot.verticalFov = view.fov;
            shot.near = 0.1f;
            shot.far = 9000f;
            urp.shadowDistance = 120f;
            stage.shot = shot;
            stage.Apply();
        }

        public static void Frames()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool grey = Flag("-grey");
            var (stage, go) = Stage(grey);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "stone", "gully"));
            try
            {
                foreach (var moment in Moments)
                {
                    if (!Wanted("-moments", moment))
                        continue;
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        continue;
                    stage.rig = rig;
                    string dir = Path.Combine(outDir, moment);
                    Directory.CreateDirectory(dir);
                    foreach (var v in Views)
                    {
                        string view = v.name;
                        if (!Wanted("-views", view))
                            continue;
                        Aim(stage, shot, v);
                        // -paint: the clay kept, the style's brushwork on (clay alone judges the light; the painted
                        // language is judged with the brush)
                        if (Flag("-paint"))
                            Shader.SetGlobalVector("_OS_Paint", new Vector4(stage.wrap, stage.muting, stage.grime, stage.brush));
                        string file = Path.Combine(dir, $"gully-{view}{(grey ? "-greylight" : "")}{(Flag("-history") ? "-history" : "")}{(Flag("-albedo") ? "-albedo" : "")}{(Flag("-normals") ? "-normals" : "")}{(Flag("-paint") ? "-paint" : "")}{(Arg("-detail", "") != "" ? "-" + Arg("-detail", "") : "")}{(Flag("-nostyle") ? "-nostyle" : "")}.png");
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

        /// <summary>
        /// The stair generator's variety sheet in the game's light (docs/foundations.md: the variety sheet, reviewed
        /// once per kind of thing): every flight in Assets/Art/Stone/Variety (stone.py -- variety), each placed where
        /// the plan has it in the clay town and photographed from the same place, a person at its foot a little to
        /// one side looking up its first metres, with the style's brushwork on, into reviews/lt1/stone/variety/.
        /// </summary>
        public static void Variety()
        {
            LT1Heart.Rigs();
            LT1Heart.WriteStyles();
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(HeartScene, OpenSceneMode.Single);
            var stage = Object.FindAnyObjectByType<StreetStage>();
            stage.clay = true;
            stage.look = "P";
            stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset");
            if (stage.skyMap != null)
                stage.skyMap.Build();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            GrowthPack.Apply();
            WaterPack.Apply();
            Shader.SetGlobalFloat("_OS_NearForce", 0f);
            var mat = Material(false);
            AssetDatabase.SaveAssets();
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "stone", "variety"));
            string srcDir = Path.Combine(Application.dataPath, "Art", "Stone", "Variety");
            try
            {
                foreach (var json in Directory.GetFiles(srcDir, "stone_*.json"))
                {
                    if (json.EndsWith(".facts.json"))
                        continue;
                    string which = Path.GetFileNameWithoutExtension(json).Substring("stone_".Length);
                    if (Arg("-only", "") != "" && !which.Contains(Arg("-only", "")))
                        continue;
                    var facts = JsonUtility.FromJson<Facts>(File.ReadAllText(json.Replace(".json", ".facts.json")));
                    var (go, _) = Place(which, facts.stone == "granite" ? GraniteMaterial(false) : mat, "Variety/");
                    var info = JsonUtility.FromJson<Info>(File.ReadAllText(json));
                    var f = info.flights[0];
                    var a = new Vector3(f.a[0], f.a[1], f.a[2]);
                    var d2 = new Vector2(f.b[0] - f.a[0], f.b[1] - f.a[1]);
                    float run = d2.magnitude;
                    var d = new Vector3(d2.x / run, d2.y / run, 0f);
                    var right = new Vector3(d.y, -d.x, 0f);
                    float slope = (f.b[2] - f.a[2]) / run;
                    try
                    {
                        var mid = (new Vector3(f.a[0], f.a[1], f.a[2]) + new Vector3(f.b[0], f.b[1], f.b[2])) * 0.5f;
                        var views = new (string name, Vector3 pos, Vector3 target)[]
                        {
                            // a person at its foot, a little to one side, looking up its first metres
                            ("foot", a - d * 3.2f + right * 0.9f + new Vector3(0f, 0f, 1.65f),
                             a + d * 3.0f + new Vector3(0f, 0f, slope * 3.0f * 0.75f + 0.2f)),
                            // 12 m up beside its first flight, looking down along it (its runs and repairs)
                            ("into12", mid - d * 9f + right * 1.5f + new Vector3(0f, 0f, 12f), mid),
                        };
                        foreach (var moment in new[] { "1300-drizzle", "1600-low-sun" })
                        foreach (var (vname, vpos, vtarget) in views)
                        {
                            if (!Wanted("-moments", moment) || !Wanted("-views", vname))
                                continue;
                            stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                            shot.position = vpos;
                            shot.target = vtarget;
                            shot.verticalFov = Lens28;
                            shot.near = 0.1f;
                            shot.far = 9000f;
                            urp.shadowDistance = 120f;
                            stage.shot = shot;
                            stage.Apply();
                            Shader.SetGlobalVector("_OS_Paint", new Vector4(stage.wrap, stage.muting, stage.grime, stage.brush));
                            string dir = Path.Combine(outDir, moment);
                            Directory.CreateDirectory(dir);
                            string file = Path.Combine(dir, vname == "foot" ? $"{which}.png" : $"{which}-{vname}.png");
                            LT1Render.Still(stage.view, file, grey: false, eighth: false, msaa: 4);
                            Debug.Log($"[LT1Stone.Variety] {file}");
                        }
                    }
                    finally
                    {
                        Object.DestroyImmediate(go);
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(shot);
            }
        }
    }
}
