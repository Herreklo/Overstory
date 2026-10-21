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
    /// The corner through the years, in clay (docs/experiments.md, LT1f). The heart's clay, with the corner's five houses
    /// built by the test-quality generator from their diaries (blender/tools/export_time.py) standing where the heart's
    /// grey masses for them stand, at 1989, 2000, 2010 and 2020. Everything but the year is held: one camera per view,
    /// one sun (20 October at 15:00 UTC: 16:00 on the clock in 1989, 17:00 in the three later years, when summer time
    /// still ran), no cloud shadows, no motes, the same seeds.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Time.Frames
    ///         [-arms real,shuffled] [-years 1989,...] [-views eye,...] [-out reviews/lt1/time/frames]
    ///     Unity ... LT1Time.Probe -out &lt;dir&gt;      (candidate views at 1280 by 720, the record in 1989)
    ///
    /// Frames are the player's (PlayerFrame: 2560 by 1440, one sample a pixel, the game's MSAA). Beside them,
    /// frames.json says which camera, sun and houses made each, and where each house's middle falls in each view.
    /// The heart's scene is opened, never saved.
    /// </summary>
    public static class LT1Time
    {
        const string HeartScene = "Assets/Experiments/LT1/Heart/LT1_Heart.unity";
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const string Materials = "Assets/Art/Materials";
        const string TimeJson = "Assets/Art/Buildings/time/time.json";
        const float Lens28 = 46.4f, Lens35 = 37.8f;
        public const int WarmUp = 8;

        /// <summary>
        /// The judging views (docs/foundations.md), named and the same in every year. Street metres; a z marked
        /// above ground (aboveGround) is a height over the ground under that point, found once by a ray.
        /// </summary>
        public static readonly View[] Views =
        {
            // eye level on the quay road across from the lane's foot: A's front and B's, the lane between them
            new View("eye", new Vector3(45.5f, -13.5f, 1.65f), new Vector3(48.5f, 5.0f, 3.6f), Lens28, true),
            // the street stop on Gully Steps (LT1Heart.Shots, 3): up the steps to the Landing, C, D on the rock, E
            new View("street", new Vector3(49.3f, 12f, 5.6f), new Vector3(47.5f, 44f, 10.5f), Lens28, false),
            // 12 m over the foot of the steps, up the lane: C's back and gable, D on the knuckle, E closing the view
            new View("12m", new Vector3(51.0f, 12.0f, 12f), new Vector3(49.0f, 55.0f, 4f), Lens35, true),
            // the city camera, pulled out and steep, near-isometric, from the sun's side, the five houses in frame
            new View("city", new Vector3(118f, -52f, 92f), new Vector3(49f, 46f, 8f), 28f, false),
        };

        public struct View
        {
            public string name;
            public Vector3 pos, target;
            public float fov;
            public bool aboveGround;
            public View(string name, Vector3 pos, Vector3 target, float fov, bool aboveGround)
            {
                this.name = name; this.pos = pos; this.target = target; this.fov = fov; this.aboveGround = aboveGround;
            }
        }

        // -- the houses, as export_time.py wrote them --------------------------------------------------------------

        [System.Serializable] public class P3 { public float x, y, z; public Vector3 V => new Vector3(x, y, z); }
        [System.Serializable] public class Row { public string arm, letter, file; public int year, id, tris; public P3 position, middle; public float yaw; }
        [System.Serializable] public class Export { public string style; public int worldSeed; public int[] years; public Row[] buildings; }

        public static Export Houses()
        {
            var text = AssetDatabase.LoadAssetAtPath<TextAsset>(TimeJson)
                ?? throw new FileNotFoundException("no corner through the years: run blender/tools/export_time.py");
            return JsonUtility.FromJson<Export>(text.text);
        }

        // -- the stage -----------------------------------------------------------------------------------------------

        public sealed class Stage : System.IDisposable
        {
            public StreetStage stage;
            public Transform houses;
            public GameObject corner;      // the heart's grey masses for the five houses, hidden
            readonly LightRig rig;
            readonly CameraShot shot;
            readonly float reach;
            readonly MeshCollider ground;
            readonly Material street;
            public readonly Export export;
            public string arm;
            public int year;

            public Stage()
            {
                export = Houses();
                EditorSceneManager.OpenScene(HeartScene, OpenSceneMode.Single);
                stage = Object.FindAnyObjectByType<StreetStage>();
                stage.clay = true;
                stage.look = "P";
                stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{Lights}/Styles/Style_game.asset");
                var src = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_1600-low-sun.asset")
                    ?? throw new FileNotFoundException("the heart's rigs are missing: run LT1Heart.Rigs");
                // the corner's light held for every year: the 16:00 sun of 20 October 1989 (15:00 UTC), with nothing
                // that moves on its own (cloud shadows, motes, shafts), so only the year differs between frames
                rig = Object.Instantiate(src);
                rig.cloudCover = 0f;
                rig.motes = 0f;
                rig.shafts = 0f;
                stage.rig = rig;
                if (stage.townLights != null)
                    stage.townLights.Build();
                GrowthPack.Apply();
                WaterPack.Apply();
                Shader.SetGlobalFloat("_OS_NearForce", 0f);

                street = AssetDatabase.LoadAssetAtPath<Material>(Materials + "/M_Street.mat");
                var heart = GameObject.Find("The heart (clay)") ?? throw new MissingReferenceException("no heart in the scene");
                foreach (Transform t in heart.transform)
                {
                    if (t.name == "buildings_corner")
                        corner = t.gameObject;
                    if (t.name == "ground_heart")
                    {
                        var mf = t.GetComponentInChildren<MeshFilter>();
                        ground = mf.gameObject.AddComponent<MeshCollider>();
                        ground.sharedMesh = mf.sharedMesh;
                    }
                }
                if (corner == null)
                    throw new MissingReferenceException("the heart has no buildings_corner to replace");
                corner.SetActive(false);
                houses = new GameObject("LT1f: the corner's houses").transform;
                houses.SetParent(heart.transform, false);

                var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
                reach = urp.shadowDistance;
                urp.shadowDistance = 160f;
                shot = ScriptableObject.CreateInstance<CameraShot>();
            }

            /// <summary>The five houses of one arm in one year, and the sky map redrawn over them.</summary>
            public void Place(string arm, int year)
            {
                this.arm = arm;
                this.year = year;
                for (int i = houses.childCount - 1; i >= 0; i--)
                    Object.DestroyImmediate(houses.GetChild(i).gameObject);
                foreach (var b in export.buildings)
                {
                    if (b.arm != arm || b.year != year)
                        continue;
                    var model = AssetDatabase.LoadAssetAtPath<GameObject>(b.file) ?? throw new FileNotFoundException(b.file);
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(model, houses);
                    go.name = $"{b.letter} ({b.id}) {year}";
                    go.transform.localPosition = StreetSpace.ToUnity(b.position.V);
                    go.transform.localRotation = Quaternion.Euler(0f, -b.yaw, 0f);
                    foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
                    {
                        var mats = new Material[r.sharedMaterials.Length];
                        for (int i = 0; i < mats.Length; i++)
                            mats[i] = street;
                        r.sharedMaterials = mats;
                        r.shadowCastingMode = ShadowCastingMode.On;
                    }
                }
                if (stage.skyMap != null)
                    stage.skyMap.Build();
            }

            /// <summary>The ground's height under a street point, or the fallback.</summary>
            public float Ground(float x, float y, float fallback = 0f)
            {
                var from = StreetSpace.ToUnity(new Vector3(x, y, 400f));
                return ground != null && ground.Raycast(new Ray(from, Vector3.down), out var hit, 1000f) ? hit.point.y : fallback;
            }

            public (Vector3 pos, Vector3 target) Resolve(View v)
            {
                if (!v.aboveGround)
                    return (v.pos, v.target);
                return (new Vector3(v.pos.x, v.pos.y, Ground(v.pos.x, v.pos.y) + v.pos.z),
                        new Vector3(v.target.x, v.target.y, Ground(v.target.x, v.target.y) + v.target.z));
            }

            public void Aim(View v, float sideways = 0f)
            {
                var (pos, target) = Resolve(v);
                if (sideways != 0f)
                {
                    var d = target - pos;
                    var right = new Vector3(d.y, -d.x, 0f).normalized;
                    pos += right * sideways;
                    target += right * sideways;
                }
                shot.position = pos;
                shot.target = target;
                shot.verticalFov = v.fov;
                shot.near = 0.1f;
                shot.far = 9000f;
                stage.shot = shot;
                stage.Apply();
            }

            /// <summary>Where each house's middle falls in the current view (0 to 1, from the top left), and if in front.</summary>
            public List<string> Labels()
            {
                var cam = stage.view;
                var list = new List<string>();
                foreach (var b in export.buildings)
                {
                    if (b.arm != arm || b.year != year)
                        continue;
                    var p = cam.WorldToViewportPoint(StreetSpace.ToUnity(b.middle.V));
                    list.Add($"{{\"letter\":\"{b.letter}\",\"x\":{p.x:0.0000},\"y\":{1f - p.y:0.0000},\"front\":{(p.z > 0 ? "true" : "false")}}}");
                }
                return list;
            }

            public void Dispose()
            {
                var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(rig);
                Object.DestroyImmediate(shot);
            }
        }

        static string Arg(string flag, string fallback) => Cli.Arg(flag, fallback);

        static bool Wanted(string flag, string value)
        {
            string list = Arg(flag, null);
            if (list == null)
                return true;
            return System.Array.IndexOf(list.Split(','), value) >= 0;
        }

        /// <summary>The frames, then the masks, in one run.</summary>
        public static void FramesAndMasks()
        {
            Frames();
            Masks();
        }

        /// <summary>The frames: every arm, year and view, at the player's size, with frames.json beside them.</summary>
        public static void Frames()
        {
            string outDir = Cli.RepoPath("-out", "reviews/lt1/time/frames");
            using var s = new Stage();
            var record = new List<string>();
            foreach (var arm in new[] { "real", "shuffled" })
            {
                if (!Wanted("-arms", arm))
                    continue;
                foreach (var year in s.export.years)
                {
                    if (!Wanted("-years", year.ToString()))
                        continue;
                    s.Place(arm, year);
                    foreach (var v in Views)
                    {
                        if (!Wanted("-views", v.name))
                            continue;
                        s.Aim(v);
                        string rel = $"{arm}/{v.name}-{year}.png";
                        string file = Path.Combine(outDir, rel);
                        int msaa;
                        using (var frame = new PlayerFrame(s.stage.view))
                        {
                            frame.Render(WarmUp + 1);
                            frame.Save(file);
                            msaa = frame.Msaa;
                        }
                        var (pos, target) = s.Resolve(v);
                        record.Add($"{{\"file\":\"{rel}\",\"arm\":\"{arm}\",\"year\":{year},\"view\":\"{v.name}\",\"msaa\":{msaa}," +
                                   $"\"camera\":[{pos.x:0.###},{pos.y:0.###},{pos.z:0.###}],\"target\":[{target.x:0.###},{target.y:0.###},{target.z:0.###}],\"fov\":{v.fov}," +
                                   $"\"labels\":[{string.Join(",", s.Labels())}]}}");
                        Debug.Log($"[LT1Time] {file}");
                    }
                }
            }
            Directory.CreateDirectory(outDir);
            File.WriteAllText(Path.Combine(outDir, "frames.json"),
                "{\n \"what\": \"the corner through the years in clay (LT1Time.Frames)\",\n" +
                $" \"width\": {PlayerFrame.Width}, \"height\": {PlayerFrame.Height}, \"warmUp\": {WarmUp}, \"unity\": \"{Application.unityVersion}\",\n" +
                $" \"sun\": \"Heart_1600-low-sun: 20 October, 15:00 UTC (16:00 CET in 1989; 17:00 CEST in 2000, 2010, 2020); no cloud shadows, motes or shafts\",\n" +
                $" \"style\": \"{s.export.style}\",\n \"frames\": [\n  " + string.Join(",\n  ", record) + "\n ]\n}\n");
        }

        /// <summary>
        /// Each house's own pixels in each view: the house white, everything else black, depth kept, so a house hidden
        /// behind another is hidden here too. Used to place the ways of showing time where the record changed a house
        /// (never a picture difference), into &lt;out&gt;/masks/&lt;arm&gt;/&lt;view&gt;-&lt;year&gt;-&lt;letter&gt;.png.
        /// </summary>
        public static void Masks()
        {
            string outDir = Path.Combine(Cli.RepoPath("-out", "reviews/lt1/time/frames"), "masks");
            using var s = new Stage();
            var unlit = Shader.Find("Universal Render Pipeline/Unlit");
            var white = new Material(unlit);
            white.SetColor("_BaseColor", Color.white);
            var black = new Material(unlit);
            black.SetColor("_BaseColor", Color.black);
            var cam = s.stage.view;
            var camData = cam.GetComponent<UniversalAdditionalCameraData>();
            bool post = camData.renderPostProcessing;
            try
            {
                foreach (var arm in new[] { "real", "shuffled" })
                {
                    if (!Wanted("-arms", arm))
                        continue;
                    foreach (var year in s.export.years)
                    {
                        if (!Wanted("-years", year.ToString()))
                            continue;
                        s.Place(arm, year);
                        var saved = new List<(MeshRenderer r, Material[] m)>();
                        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                            saved.Add((r, r.sharedMaterials));
                        try
                        {
                            foreach (var v in Views)
                            {
                                if (!Wanted("-views", v.name))
                                    continue;
                                s.Aim(v);
                                camData.renderPostProcessing = false;
                                cam.clearFlags = CameraClearFlags.SolidColor;
                                cam.backgroundColor = Color.black;
                                for (int h = 0; h < s.houses.childCount; h++)
                                {
                                    var house = s.houses.GetChild(h);
                                    foreach (var (r, m) in saved)
                                    {
                                        var mats = new Material[m.Length];
                                        bool mine = r.transform.IsChildOf(house);
                                        for (int i = 0; i < mats.Length; i++)
                                            mats[i] = mine ? white : black;
                                        r.sharedMaterials = mats;
                                    }
                                    string letter = house.name.Substring(0, 1);
                                    using var frame = new PlayerFrame(cam);
                                    frame.Render(2);
                                    frame.Save(Path.Combine(outDir, arm, $"{v.name}-{year}-{letter}.png"));
                                }
                                camData.renderPostProcessing = post;
                                cam.clearFlags = CameraClearFlags.Skybox;
                                Debug.Log($"[LT1Time] masks {arm} {year} {v.name}");
                            }
                        }
                        finally
                        {
                            foreach (var (r, m) in saved)
                                if (r != null)
                                    r.sharedMaterials = m;
                        }
                    }
                }
            }
            finally
            {
                camData.renderPostProcessing = post;
                cam.clearFlags = CameraClearFlags.Skybox;
                Object.DestroyImmediate(white);
                Object.DestroyImmediate(black);
            }
        }

        /// <summary>Candidate views, small and fast, to choose the judging views from (never committed).</summary>
        public static void Probe()
        {
            string outDir = Cli.RepoPath("-out", "reviews/lt1/time/probe");
            var candidates = new List<View>(Views)
            {
                new View("eye2", new Vector3(45.5f, -13.5f, 1.65f), new Vector3(48.5f, 5.0f, 3.6f), Lens28, true),
                new View("street2", new Vector3(49.3f, 12f, 5.6f), new Vector3(49.0f, 50f, 12f), Lens35, false),
                new View("12m-lane", new Vector3(51.0f, 12.0f, 12f), new Vector3(49.0f, 55.0f, 4f), Lens35, true),
                new View("12m-landing", new Vector3(36.0f, 55.0f, 12f), new Vector3(52.0f, 42.0f, 3f), Lens35, true),
                new View("city2", new Vector3(100f, -25f, 80f), new Vector3(48f, 47f, 8f), 30f, false),
                new View("city3", new Vector3(5f, -35f, 85f), new Vector3(49f, 47f, 8f), 30f, false),
            };
            using var s = new Stage();
            s.Place("real", 1989);
            foreach (var v in candidates)
            {
                if (!Wanted("-views", v.name))
                    continue;
                s.Aim(v);
                using var frame = new PlayerFrame(s.stage.view, 1280, 720);
                frame.Render(WarmUp + 1);
                frame.Save(Path.Combine(outDir, $"probe-{v.name}.png"));
                Debug.Log($"[LT1Time] probe {v.name} {string.Join(" ", s.Labels())}");
            }
        }
    }
}
