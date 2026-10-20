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
        static readonly (string species, int seed, int age)[] Sheet = { ("birch", 1, 15), ("birch", 1, 30), ("birch", 1, 60) };

        /// <summary>Near where the sheet's tree stands, in street metres (Broad Street): it stands at the first open,
        /// sunlit ground from here (SunlitSpot).</summary>
        static readonly Vector2 Near = new Vector2(250f, -236f);

        /// <summary>Each species' look on 20 October: its leaves' colours and how far the season has gone.</summary>
        static readonly Dictionary<string, (Color green, Color turned, Color late, Vector4 season)> Species = new()
        {
            // downy birch on the coast in late October: most leaves turned butter-yellow to gold, a third fallen, the
            // first turned gone a dull brown; never red
            ["birch"] = (new Color(0.27f, 0.38f, 0.12f), new Color(0.88f, 0.70f, 0.18f), new Color(0.58f, 0.45f, 0.20f),
                         new Vector4(0.62f, 0.30f, 0f, 0f)),
        };

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
                m.SetTexture("_Spray", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{species}_leaves.png"));
                m.SetFloat("_Leaves", leaves ? 1f : 0f);
                if (leaves) m.EnableKeyword("_OS_LEAVES"); else m.DisableKeyword("_OS_LEAVES");
                if (Species.TryGetValue(species, out var s))
                {
                    m.SetColor("_Green", s.green);
                    m.SetColor("_Turned", s.turned);
                    m.SetColor("_Late", s.late);
                    m.SetVector("_Season", s.season);
                }
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
            string path = $"{Art}/{species}/tree_{species}_s{seed}_a{age}.fbx";
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
                foreach (var moment in new[] { "1600-low-sun", "1750-sea-fog" })
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
                        Vector3 At(Vector2 off, float up) => new Vector3(Spot.x + off.x, Spot.y + off.y, ground + up);
                        var mid = new Vector3(Spot.x, Spot.y, ground + h * 0.48f);
                        var views = new (string name, Vector3 pos, Vector3 target, float fov)[]
                        {
                            // the sun behind the viewer, a little to one side, so the crown shows its lit and shaded planes
                            ("street", At(sunFlat * d * 0.94f + side * d * 0.34f, 2.8f), mid, Lens28),
                            // looking into the low sun through the leaves
                            ("into-the-sun", At(-sunFlat * d * 0.94f + side * d * 0.34f, 2.8f), mid, Lens28),
                            // from the roofs, across the light
                            ("roofs", At(side * d * 1.1f + sunFlat * d * 0.5f, 14f), new Vector3(Spot.x, Spot.y, ground + h * 0.45f), Lens35),
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
                            LT1Render.Still(stage.view, file, grey: true, eighth: true);
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
