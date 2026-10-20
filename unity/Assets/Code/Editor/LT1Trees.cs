using System.Collections.Generic;
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
    /// The first look test of the tree system (docs/experiments.md, LT1, the first look test): grown trees, assembled
    /// from their parts (blender/generators/tree.py), stood in the heart in clay and drawn by the tree shader in the
    /// corner's light at 16:00 and at 17:50 in sea fog, in the game's style, from the street stop and from the roofs.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Trees.Frames
    ///
    /// Each tree is shown alone, on Broad Street (a sheet, not a fact: no tree stands there in the town's history yet).
    /// Frames go to reviews/lt1/trees/first/; full-size frames are not kept in git.
    /// </summary>
    public static class LT1Trees
    {
        const string Art = "Assets/Art/Trees";
        const string HeartDir = "Assets/Experiments/LT1/Heart";
        const string HeartScene = HeartDir + "/LT1_Heart.unity";
        const string Lights = HeartDir + "/Light";
        const float Lens28 = 46.4f, Lens35 = 37.8f;

        /// <summary>The trees on the sheet: species, seed, age.</summary>
        static (string species, int seed, int age)[] Sheet
        {
            get { string sp = Arg("-species", "birch"); return new[] { (sp, 1, 15), (sp, 1, 30), (sp, 1, 60) }; }
        }

        /// <summary>A model's name, with any dated events in it (tree.py: tree_birch_s1_a60_cut50).</summary>
        static string ModelSuffix = "";

        /// <summary>Near where the sheet's tree stands, in street metres (Broad Street): it stands at the first open,
        /// sunlit ground from here (SunlitSpot).</summary>
        static readonly Vector2 Near = new Vector2(250f, -236f);

        /// <summary>Each species' look on 20 October: its leaves' colours and how far the season has gone.</summary>
        static readonly Dictionary<string, (Color green, Color turned, Color late, Vector4 season)> Species = new()
        {
            // downy birch on the coast on 20 October: most leaves turned an ochre gold (greyed, never cadmium), the
            // last still olive, the first a dull brown, never orange or red; nearly half fallen, from the inside and
            // below, so the limbs show
            ["birch"] = (new Color(0.40f, 0.42f, 0.20f), new Color(0.64f, 0.55f, 0.29f), new Color(0.44f, 0.37f, 0.24f),
                         new Vector4(0.78f, 0.40f, 0f, 0f)),     // two curtains in five gone
            // the silver birch turns as the downy does on this coast
            ["silver_birch"] = (new Color(0.40f, 0.42f, 0.20f), new Color(0.64f, 0.55f, 0.29f), new Color(0.44f, 0.37f, 0.24f),
                                new Vector4(0.78f, 0.40f, 0f, 0f)),
        };

        /// <summary>Which painted leaves each species' cards carry: its sprays, or its clumps.</summary>
        static readonly Dictionary<string, string> Atlas = new() { ["birch"] = "clusters", ["silver_birch"] = "clusters" };

        public static (Material bark, Material leaves) Materials(string species)
        {
            string dir = $"{Art}/{species}";
            var shader = Shader.Find("Overstory/Tree");
            Material Make(string name, bool leaves)
            {
                string path = $"{dir}/M_Tree_{species}_{name}.mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null)
                {
                    m = new Material(shader);
                    AssetDatabase.CreateAsset(m, path);
                }
                m.shader = shader;
                m.SetTexture("_Bark", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{species}_bark.png"));
                // the painted leaves the species' cards carry (as blender/generators/tree.py PARTS[species]["atlas"])
                string atlas = Atlas.TryGetValue(species, out var a) ? a : "leaves";
                m.SetTexture("_Spray", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{species}_{atlas}.png"));
                m.SetTexture("_Twigs", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{species}_twigs.png"));
                m.SetFloat("_Leaves", leaves ? 1f : 0f);
                m.SetFloat("_AlphaToMask", 1f);   // leaves' edges and fine twigs, soft under MSAA
                if (leaves) m.EnableKeyword("_OS_LEAVES"); else m.DisableKeyword("_OS_LEAVES");
                if (Species.TryGetValue(species, out var s))
                {
                    m.SetColor("_Green", s.green);
                    m.SetColor("_Turned", s.turned);
                    m.SetColor("_Late", s.late);
                    m.SetVector("_Season", s.season);
                    m.SetFloat("_Hold", 0.15f);
                    // every setting written here, so the material is what this code says (a material keeps the values
                    // it was first saved with, and a changed shader default never reaches it)
                    m.SetFloat("_InnerGlow", 0f);
                    m.SetFloat("_MassShadow", 8f);
                    m.SetFloat("_LeafSkyTint", 0.35f);
                    m.SetFloat("_SunPale", 0.45f);
                    m.SetFloat("_Scatter", 0.32f);
                    m.SetFloat("_Cutoff", 0.5f);
                    m.SetColor("_Through", new Color(1f, 0.85f, 0.45f, 0.9f));
                }
                // a birch's twigs and young branches are dark purple-brown up to two or three centimetres; the white
                // bark comes with age on the limbs and the trunk
                m.SetVector("_TwigRadius", new Vector4(0.012f, 0.045f, 0f, 0f));
                // a birch's twigs are a purple-grey brown, and seen through the leaves they are lost in them: lighter
                // than bark's dark marks, never black lines
                m.SetColor("_Twig", new Color(0.36f, 0.27f, 0.27f));
                m.enableInstancing = true;
                EditorUtility.SetDirty(m);
                return m;
            }
            var bark = Make("bark", false);
            var leafy = Make("leaves", true);
            AssetDatabase.SaveAssets();
            return (bark, leafy);
        }

        /// <summary>A grown tree, stood with its foot at a point (street metres), turned by yaw degrees.</summary>
        public static GameObject Place(Transform parent, string species, int seed, int age, Vector3 street, float yaw)
        {
            string path = $"{Art}/{species}/tree_{species}_s{seed}_a{age}{ModelSuffix}.fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (model == null)
                throw new FileNotFoundException($"no grown tree at {path}: run blender/generators/tree.py first");
            var (bark, leaves) = Materials(species);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(model, parent);
            go.transform.SetPositionAndRotation(StreetSpace.ToUnity(street), Quaternion.Euler(0f, yaw, 0f));
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                bool leafy = r.gameObject.name.EndsWith("_leaves");
                var mats = new Material[r.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = leafy ? leaves : bark;
                r.sharedMaterials = mats;
                r.shadowCastingMode = ShadowCastingMode.On;
            }
            return go;
        }

        /// <summary>Colliders on the heart while they are needed, for rays: the clay has none of its own.</summary>
        sealed class Rays : System.IDisposable
        {
            readonly List<MeshCollider> added = new();
            public Rays()
            {
                var heart = GameObject.Find("The heart (clay)");
                foreach (var mf in heart.GetComponentsInChildren<MeshFilter>())
                    if (mf.GetComponent<Collider>() == null)
                        added.Add(mf.gameObject.AddComponent<MeshCollider>());
                Physics.SyncTransforms();
            }
            public void Dispose()
            {
                foreach (var c in added)
                    Object.DestroyImmediate(c);
            }
        }

        /// <summary>
        /// The first place near a point (street metres) where a tree can stand in the low sun for the sheet: open ground
        /// (the ground's own mesh, level, above the water), nothing within seven metres, and the sun reaching its foot,
        /// its middle and its top. Searched in a fixed spiral, so it is the same place every time.
        /// </summary>
        static Vector3 SunlitSpot(Vector2 near, Vector3 toSunUnity, float height)
        {
            using var rays = new Rays();
            for (int i = 0; i < 4000; i++)
            {
                float r = 3f * Mathf.Sqrt(i), a = i * 2.39996323f;
                var p = near + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * r;
                if (!Physics.Raycast(StreetSpace.ToUnity(p.x, p.y, 400f), Vector3.down, out var hit, 800f))
                    continue;
                if (!hit.collider.gameObject.name.StartsWith("ground") || hit.normal.y < 0.97f || hit.point.y < 1.0f)
                    continue;
                var foot = hit.point;
                bool clear = true;
                for (int k = 0; k < 8 && clear; k++)
                {
                    var dir = Quaternion.Euler(0f, k * 45f, 0f) * Vector3.forward;
                    foreach (float up in new[] { 1.5f, 6f })
                        if (Physics.Raycast(foot + Vector3.up * up, dir, 7f))
                            clear = false;
                }
                if (!clear)
                    continue;
                bool lit = true;
                foreach (float up in new[] { 1.0f, height * 0.5f, height })
                    if (Physics.Raycast(foot + Vector3.up * up, toSunUnity, 600f))
                        lit = false;
                if (lit)
                    return new Vector3(p.x, p.y, foot.y);
            }
            throw new System.Exception("no sunlit open ground found for the tree sheet");
        }

        /// <summary>A check of an imported tree: what reached Unity in its channels.</summary>
        public static void Inspect()
        {
            foreach (var path in Directory.GetFiles(Art, "*.fbx", SearchOption.AllDirectories))
                foreach (var o in AssetDatabase.LoadAllAssetsAtPath(path.Replace('\\', '/')))
                    if (o is Mesh m)
                    {
                        var uv1 = new List<Vector2>();
                        m.GetUVs(1, uv1);
                        var cols = m.colors;
                        string Range(IEnumerable<float> xs) { float lo = float.MaxValue, hi = float.MinValue; foreach (var x in xs) { lo = Mathf.Min(lo, x); hi = Mathf.Max(hi, x); } return $"{lo:F3}..{hi:F3}"; }
                        Debug.Log($"[LT1Trees] {m.name}: {m.vertexCount} vertices, {m.triangles.Length / 3} triangles, uv1 {uv1.Count} x {Range(uv1.ConvertAll(v => v.x))} y {Range(uv1.ConvertAll(v => v.y))}, colours {cols.Length} r {Range(System.Array.ConvertAll(cols, c => c.r))}, bounds {m.bounds.size}");
                    }
        }

        /// <summary>
        /// The seasons sheet: the birch at 30 and 60 years in mid-May (leaves coming out, young green: the season's
        /// "fallen" share read as "not yet out", the same order), July, 20 October and January (bare: the drawn branches
        /// and the sprays' own twigs), all in the corner's 16:00 light, so only the tree changes.
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Trees.Seasons
        ///         [-species silver_birch] [-moment 1300-drizzle] [-ages 60] [-seasons 01-january]
        ///
        /// -moment draws the sheet in another of the corner's lights (the grey drizzle judges form without the low
        /// sun's flattery); its frames are named with it.
        /// </summary>
        public static void Seasons()
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
            string moment = Arg("-moment", "1600-low-sun");
            // the tree stands in the same place, and is seen from the same side, whatever the light
            var lowSun = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_1600-low-sun.asset");
            stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            Vector3 sunStreet = lowSun.SunDirectionStreet;
            var spot = SunlitSpot(Near, StreetSpace.ToUnity(sunStreet).normalized, 17f);
            var sunFlat = new Vector2(sunStreet.x, sunStreet.y).normalized;
            var side = new Vector2(-sunFlat.y, sunFlat.x);
            var root = new GameObject("Trees (seasons)").transform;
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "seasons"));
            Directory.CreateDirectory(dir);
            string species = Arg("-species", "birch");
            var (bark, leaves) = Materials(species);
            var seasons = new (string name, Color green, Vector4 season)[]
            {
                ("05-may", new Color(0.50f, 0.58f, 0.20f), new Vector4(0f, 0.55f, 0f, 0f)),     // half out: a pale haze
                ("07-july", new Color(0.25f, 0.37f, 0.11f), new Vector4(0f, 0f, 0f, 0f)),
                ("10-october-20", new Color(0.36f, 0.40f, 0.15f), new Vector4(0.78f, 0.40f, 0f, 0f)),
                ("01-january", new Color(0.27f, 0.38f, 0.12f), new Vector4(1f, 1.3f, 0f, 0f)),
            };
            try
            {
                using var rays = new Rays();
                foreach (int age in new[] { 30, 60 })
                {
                    if (!Wanted("-ages", age.ToString()))
                        continue;
                    var tree = Place(root, species, 1, age, spot, 0f);
                    float h = 0f;
                    foreach (var r in tree.GetComponentsInChildren<MeshRenderer>())
                        h = Mathf.Max(h, r.bounds.max.y - spot.z);
                    float d = Mathf.Max(h * 1.55f, 9f);
                    var off = sunFlat * d * 0.5f + side * d * 0.87f;   // side light, as the street frames
                    shot.position = new Vector3(spot.x + off.x, spot.y + off.y, spot.z + 2.8f);
                    shot.target = new Vector3(spot.x, spot.y, spot.z + h * 0.48f);
                    shot.verticalFov = Lens28;
                    shot.near = 0.3f;
                    shot.far = 9000f;
                    foreach (var (name, green, season) in seasons)
                    {
                        if (!Wanted("-seasons", name))
                            continue;
                        leaves.SetColor("_Green", green);
                        leaves.SetVector("_Season", season);
                        urp.shadowDistance = 160f;
                        stage.shot = shot;
                        stage.Apply();
                        string light = moment == "1600-low-sun" ? "" : $"-{moment}";
                        string file = Path.Combine(dir, $"{species}-s1-a{age}-{name}{light}.png");
                        LT1Render.Still(stage.view, file, grey: true, eighth: true, msaa: 4);
                        Debug.Log($"[LT1Trees] {file}");
                    }
                    Object.DestroyImmediate(tree);
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Materials(species);   // back to 20 October
                Object.DestroyImmediate(root.gameObject);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>
        /// The variety sheet: twelve birches of thirty years from twelve seeds on the same site, side by side in the
        /// 16:00 light. Each must be its own tree and every one a downy birch of that age.
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Trees.Variety
        /// (after blender/generators/tree.py has assembled birch seeds 1 to 12 at 30)
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
            string moment = Arg("-moment", "1600-low-sun");
            // the tree stands in the same place, and is seen from the same side, whatever the light
            var lowSun = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_1600-low-sun.asset");
            stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            Vector3 sunStreet = lowSun.SunDirectionStreet;
            var spot = SunlitSpot(Near, StreetSpace.ToUnity(sunStreet).normalized, 17f);
            var sunFlat = new Vector2(sunStreet.x, sunStreet.y).normalized;
            var side = new Vector2(-sunFlat.y, sunFlat.x);
            var root = new GameObject("Trees (variety)").transform;
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "variety"));
            Directory.CreateDirectory(dir);
            try
            {
                using var rays = new Rays();
                for (int seed = 1; seed <= 12; seed++)
                {
                    // six planted garden birches (sheltered), then six self-seeded on an exposed knoll
                    ModelSuffix = seed <= 6 ? "" : "_x10_wild";
                    var tree = Place(root, "birch", seed, 30, spot, 0f);
                    ModelSuffix = "";
                    float h = 0f;
                    foreach (var r in tree.GetComponentsInChildren<MeshRenderer>())
                        h = Mathf.Max(h, r.bounds.max.y - spot.z);
                    // the same camera for every seed, framed for a 12 m tree, so their sizes compare
                    float d = 12f * 1.55f;
                    var off = sunFlat * d * 0.5f + side * d * 0.87f;   // side light, as the street frames
                    shot.position = new Vector3(spot.x + off.x, spot.y + off.y, spot.z + 2.8f);
                    shot.target = new Vector3(spot.x, spot.y, spot.z + 12f * 0.48f);
                    shot.verticalFov = Lens28;
                    shot.near = 0.3f;
                    shot.far = 9000f;
                    urp.shadowDistance = 160f;
                    stage.shot = shot;
                    stage.Apply();
                    string file = Path.Combine(dir, $"birch-s{seed}-a30.png");
                    LT1Render.Still(stage.view, file, grey: false, eighth: true, msaa: 4);
                    Debug.Log($"[LT1Trees] {file} ({h:F1} m)");
                    Object.DestroyImmediate(tree);
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(root.gameObject);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>
        /// A pruned tree beside the same tree unpruned (reviews/lt1/trees/pruned/): the 60-year birch whose three
        /// heaviest limbs above 3 m were cut at the trunk ten years before, at 16:00 and in grey light.
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Trees.Pruned
        /// (after: blender ... tree.py -- birch 1 60 1.0 - cut:50:3:3.0)
        /// </summary>
        public static void Pruned()
        {
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "pruned"));
            Directory.CreateDirectory(outDir);
            ModelSuffix = "_cut50";
            try
            {
                var args = new List<string>(System.Environment.GetCommandLineArgs()) { "-ages", "60", "-views", "street,into" };
                Frames();
            }
            finally { ModelSuffix = ""; }
            foreach (var m in new[] { "1300-drizzle", "1600-low-sun", "1750-sea-fog" })
                foreach (var v in new[] { "street", "into-the-sun" })
                {
                    string src = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "first", m, $"birch-s1-a60-{v}.png"));
                    if (File.Exists(src))
                        File.Copy(src, Path.Combine(outDir, $"birch-s1-a60-cut50-{m}-{v}.png"), true);
                }
        }

        /// <summary>
        /// The character sheet (reviews/lt1/trees/character/): old self-seeded birches from an exposed knoll (60 years),
        /// in October at 16:00 and bare in January, so their wind-shaped, painterly forms show.
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Trees.Character
        /// (after: blender ... tree.py -- birch SEED 60 0.6 - exposure:1.0 self-seeded, for seeds 7 to 10)
        /// </summary>
        public static void Character()
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
            string moment = Arg("-moment", "1600-low-sun");
            // the tree stands in the same place, and is seen from the same side, whatever the light
            var lowSun = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_1600-low-sun.asset");
            stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            Vector3 sunStreet = lowSun.SunDirectionStreet;
            var spot = SunlitSpot(Near, StreetSpace.ToUnity(sunStreet).normalized, 17f);
            var sunFlat = new Vector2(sunStreet.x, sunStreet.y).normalized;
            var side = new Vector2(-sunFlat.y, sunFlat.x);
            var root = new GameObject("Trees (character)").transform;
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "character"));
            Directory.CreateDirectory(dir);
            var (bark, leaves) = Materials("birch");
            var october = leaves.GetVector("_Season");
            try
            {
                using var rays = new Rays();
                for (int seed = 7; seed <= 10; seed++)
                {
                    ModelSuffix = "_x10_wild";
                    var tree = Place(root, "birch", seed, 60, spot, 0f);
                    ModelSuffix = "";
                    float d = 10f * 1.6f;
                    var off = sunFlat * d * 0.5f + side * d * 0.87f;
                    shot.position = new Vector3(spot.x + off.x, spot.y + off.y, spot.z + 2.2f);
                    shot.target = new Vector3(spot.x, spot.y, spot.z + 4.6f);
                    shot.verticalFov = Lens28;
                    shot.near = 0.3f;
                    shot.far = 9000f;
                    foreach (var (name, season) in new[] { ("10-october-20", october), ("01-january", new Vector4(1f, 1.3f, 0f, 0f)) })
                    {
                        leaves.SetVector("_Season", season);
                        urp.shadowDistance = 160f;
                        stage.shot = shot;
                        stage.Apply();
                        string file = Path.Combine(dir, $"birch-s{seed}-a60-knoll-{name}.png");
                        LT1Render.Still(stage.view, file, grey: false, eighth: true, msaa: 4);
                        Debug.Log($"[LT1Trees] {file}");
                    }
                    Object.DestroyImmediate(tree);
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Materials("birch");
                Object.DestroyImmediate(root.gameObject);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>A command-line value, or the default when it is not given.</summary>
        static string Arg(string flag, string fallback)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, flag);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }

        /// <summary>A command-line filter: -moments 1600-low-sun, -ages 30,60, -views street (prefixes match).</summary>
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
            stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset");
            if (stage.skyMap != null)
                stage.skyMap.Build();
            if (stage.townLights != null)
                stage.townLights.Build();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            var lowSun = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_1600-low-sun.asset");
            Vector3 sunStreet = lowSun.SunDirectionStreet;
            var spot = SunlitSpot(Near, StreetSpace.ToUnity(sunStreet).normalized, 17f);
            float ground = spot.z;
            var Spot = new Vector2(spot.x, spot.y);
            // the sun's way along the ground, in street axes: the street stop has it behind, the other view looks into it
            var sunFlat = new Vector2(sunStreet.x, sunStreet.y).normalized;
            Debug.Log($"[LT1Trees] the sheet's tree stands at {spot} (street), the sun towards {sunFlat}");
            var root = new GameObject("Trees (sheet)").transform;
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "reviews", "lt1", "trees", "first"));
            using var rays = new Rays();
            try
            {
                foreach (var moment in new[] { "1600-low-sun", "1750-sea-fog", "1300-drizzle" })
                {
                    if (!Wanted("-moments", moment))
                        continue;
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    string dir = Path.Combine(outDir, moment);
                    Directory.CreateDirectory(dir);
                    foreach (var (species, seed, age) in Sheet)
                    {
                        if (!Wanted("-ages", age.ToString()))
                            continue;
                        var tree = Place(root, species, seed, age, new Vector3(Spot.x, Spot.y, ground), 0f);
                        float h = tree.GetComponentInChildren<MeshRenderer>().bounds.size.y;
                        foreach (var r in tree.GetComponentsInChildren<MeshRenderer>())
                            h = Mathf.Max(h, r.bounds.max.y - ground);
                        // the street stop: a person's eye a little raised, far enough to see the whole tree
                        float d = Mathf.Max(h * 1.55f, 9f);
                        var side = new Vector2(-sunFlat.y, sunFlat.x);
                        var across = (sunFlat * 0.5f + side * 0.87f).normalized;   // the street stop's bearing, side-lit
                        Vector3 At(Vector2 off, float up) => new Vector3(Spot.x + off.x, Spot.y + off.y, ground + up);
                        var mid = new Vector3(Spot.x, Spot.y, ground + h * 0.48f);
                        var crown = new Vector3(Spot.x, Spot.y, ground + h * 0.62f);
                        var views = new (string name, Vector3 pos, Vector3 target, float fov)[]
                        {
                            // the sun from the side and a little behind (about 60 degrees off the view), so the crown
                            // shows its lit and its shaded planes, as a painter judges form
                            ("street", At(sunFlat * d * 0.5f + side * d * 0.87f, 2.8f), mid, Lens28),
                            // looking into the low sun through the leaves
                            ("into-the-sun", At(-sunFlat * d * 0.94f + side * d * 0.34f, 2.8f), mid, Lens28),
                            // from the roofs, across the light
                            ("roofs", At(side * d * 1.1f + sunFlat * d * 0.5f, 14f), new Vector3(Spot.x, Spot.y, ground + h * 0.45f), Lens35),
                            // the city camera's middle stop: about 35 m up, looking down about 40 degrees
                            ("middle", At(across * 33f, 35f), mid, Lens35),
                            // pulled out and steep, on a long lens: near an isometric view of the town
                            ("high", At(across * 52f, 81f), mid, 15f),
                            // lower roaming heights, to choose from: just over the ridges, the close stop, between
                            ("over18", At(across * 19.7f, 18f), mid, Lens28),
                            ("over25", At(across * 25f, 25f), mid, Lens35),
                            ("over40", At(across * 36f, 40f), mid, 25f),
                            // lower still, looking into the crown: a first-floor window, just over the ridges, a roof
                            ("into08", At(across * 14f, 8f), crown, Lens28),
                            ("into12", At(across * 16f, 12f), crown, Lens28),
                            ("into15", At(across * 18f, 15f), crown, Lens28),
                        };
                        foreach (var (view, pos0, target, fov) in views)
                        {
                            if (!Wanted("-views", view))
                                continue;
                            // step round the tree until nothing (a lamp, a wall) stands between the camera and it
                            var pos = pos0;
                            for (int step = 0; step < 24; step++)
                            {
                                var off = new Vector2(pos0.x - Spot.x, pos0.y - Spot.y);
                                float ang = ((step + 1) / 2) * 15f * (step % 2 == 0 ? 1f : -1f) * Mathf.Deg2Rad;
                                var o = new Vector2(off.x * Mathf.Cos(ang) - off.y * Mathf.Sin(ang), off.x * Mathf.Sin(ang) + off.y * Mathf.Cos(ang));
                                pos = new Vector3(Spot.x + o.x, Spot.y + o.y, pos0.z);
                                bool blocked = false;
                                foreach (float f in new[] { 0.15f, 0.5f, 0.85f })
                                    if (Physics.Linecast(StreetSpace.ToUnity(pos), StreetSpace.ToUnity(new Vector3(Spot.x, Spot.y, ground + h * f))))
                                        blocked = true;
                                if (!blocked)
                                    break;
                            }
                            shot.position = pos;
                            shot.target = target;
                            shot.verticalFov = fov;
                            shot.near = 0.3f;
                            shot.far = 9000f;
                            urp.shadowDistance = 160f;
                            stage.shot = shot;
                            stage.Apply();
                            string file = Path.Combine(dir, $"{species}-s{seed}-a{age}-{view}.png");
                            LT1Render.Still(stage.view, file, grey: true, eighth: true, msaa: 4);
                            Debug.Log($"[LT1Trees] {file} (tree {h:F1} m)");
                        }
                        Object.DestroyImmediate(tree);
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(root.gameObject);
                Object.DestroyImmediate(shot);
            }
        }
    }
}
