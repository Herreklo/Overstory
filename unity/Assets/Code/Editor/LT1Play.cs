using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Play;
using Overstory.Scenes;
using Debug = UnityEngine.Debug;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The walk (LT1g, Phase 1a; reviews/lt1/playable/outline.md §2, W1 and W2): the corner composed inside the clay
    /// town as the player walks it, and the player built from it.
    ///
    /// Compose writes the generated scene (ScenePath, never kept in git): the heart's clay, staged as the gully's frames
    /// stage it (LT1Stone.Stage: the stone stair and cheek walls, the rigs and styles, the town's globals); the corner's
    /// five houses at 1989 in place of the heart's grey masses for them, each where export_time.py put it from the
    /// heart's footprint in the diaries (HousesRecord; LT1Time.PlaceHouses); the corner's birch (LT1Perf.PlantBirch);
    /// and the play object, with PlayCorner (the five judging views, the three judging lights, the heart's moods) and
    /// FrameTimeOverlay. Nothing in it is invented: every place, rig and mood comes from the records and tools named.
    /// It refuses to run unless the gully's stair and walls hash as accepted (Stairs, Walls: blender/tools/mesh_hash.py
    /// recomputes them from the FBX), and it never saves the heart's scene: Stage opens it, and the composed scene is
    /// saved as a copy by its own path. Then it opens what it saved and checks it (Check).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Play.Compose
    ///         [-stills reviews/lt1/playable/walk/w1] [-moments 1300-drizzle] [-views eye-foot,...]
    ///         [-houses Assets/Art/Buildings/time/time.json]   (another set of houses at 1989, to compare)
    ///     Unity ... -executeMethod Overstory.EditorTools.LT1Play.Build      (Compose, then the player at App)
    ///     Unity ... -executeMethod Overstory.EditorTools.LT1Play.Check      (the saved scene checked again)
    ///
    /// -stills renders each judging view (in drizzle unless -moments says otherwise) from the saved scene at the
    /// player's size (PlayerFrame), as PlayCorner shows it. tools/playable.sh runs Build under the Unity lock and puts
    /// back the settings a build rewrites.
    ///
    /// For the stages after W2: W3's harness arm can call ComposeOpen() and add its runner before saving elsewhere;
    /// LT1Perf.BuildPlayer(app, scenePath) builds any scene with the harness's player settings.
    /// </summary>
    public static class LT1Play
    {
        public const string Generated = "Assets/Experiments/LT1/Playable/Generated";
        public const string ScenePath = Generated + "/LT1_Playable.unity";
        /// <summary>The corner's houses at 1989, stronger (export_time.py --out Assets/Art/Buildings/playable).</summary>
        public const string HousesRecord = "Assets/Art/Buildings/playable/manifest.json";
        public const string App = "Builds/Playable/OverstoryPlayable.app";     // in unity/, not kept in git
        /// <summary>The gully's accepted mesh hashes (docs/measuring.md, Mesh hashes; accepted by Øystein, 22 October).</summary>
        public const string Stairs = "bff7858b698f3efd", Walls = "0a3d7db3100df20b";
        const string StoneArt = "Assets/Art/Stone";
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const string HousesRoot = "The corner's houses (1989)";
        const string PlayRoot = "Play (the walk)";
        const string Arm = "real", Style = "stronger";
        const int Year = 1989, HouseCount = 5;
        const string Blender = "/Applications/Blender.app/Contents/MacOS/Blender";
        /// <summary>The five judging views (docs/foundations.md), in LT1Stone.Views' order: keys 1 to 5.</summary>
        static readonly string[] ViewNames = { "eye-foot", "eye-on", "street", "into12", "high" };

        // -- the gully unchanged ---------------------------------------------------------------------------------------

        /// <summary>
        /// The gully's stair and cheek walls hashed from their FBX by mesh_hash.py (never re-imported) and compared with
        /// the manifest beside them, and the manifest with the accepted hashes. Throws if anything differs.
        /// </summary>
        public static (string stairs, string walls) GullyHashes()
        {
            if (gullyChecked)
                return (Stairs, Walls);     // (the FBX do not change within one run)
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string art = Path.Combine(root, "unity", StoneArt);
            var manifest = File.ReadAllText(Path.Combine(art, "mesh-hashes.json"));
            foreach (var (file, want) in new[] { ("stone_gully.fbx", Stairs), ("stone_gully_cheeks.fbx", Walls) })
            {
                var entry = JsonUtility.FromJson<HashEntryHolder>("{\"e\":" + ManifestEntry(manifest, file) + "}").e;
                if (entry == null || entry.hash != want)
                    throw new System.Exception($"[LT1Play] the gully's manifest holds {file} {entry?.hash ?? "nothing"}, not the accepted {want}: Compose refuses to run");
            }
            var args = new[] { "-b", "--factory-startup", "--python", Path.Combine(root, "blender", "tools", "mesh_hash.py"), "--",
                               "check", Path.Combine(art, "stone_gully.fbx"), Path.Combine(art, "stone_gully_cheeks.fbx") };
            var psi = new ProcessStartInfo(Blender, string.Join(" ", args.Select(a => "\"" + a.Replace("\"", "\\\"") + "\"")))
            {
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true,
                WorkingDirectory = root,
            };
            string output;
            int code;
            using (var p = Process.Start(psi))
            {
                var err = p.StandardError.ReadToEndAsync();
                output = p.StandardOutput.ReadToEnd();
                p.WaitForExit();
                code = p.ExitCode;
                _ = err.Result;
            }
            var lines = output.Split('\n').Where(l => l.StartsWith("SAME") || l.StartsWith("CHANGED") || l.StartsWith("NO ") || l.StartsWith("NOT ") || l.StartsWith("  ")).ToList();
            bool same = code == 0
                && lines.Contains($"SAME stone_gully.fbx {Stairs}")
                && lines.Contains($"SAME stone_gully_cheeks.fbx {Walls}");
            if (!same)
                throw new System.Exception($"[LT1Play] the gully's hashes differ from the accepted (exit {code}): Compose refuses to run\n{string.Join("\n", lines)}");
            Debug.Log($"[LT1Play] the gully unchanged: stairs {Stairs}, walls {Walls} (recomputed from the FBX by mesh_hash.py)");
            gullyChecked = true;
            return (Stairs, Walls);
        }

        static bool gullyChecked;

        [System.Serializable] class HashEntry { public string hash; public int triangles; }
        [System.Serializable] class HashEntryHolder { public HashEntry e; }

        /// <summary>One file's entry in a mesh-hashes.json, as JSON text (its top-level hash and triangles are read from it).</summary>
        static string ManifestEntry(string manifest, string file)
        {
            int i = manifest.IndexOf($"\"{file}\"", System.StringComparison.Ordinal);
            if (i < 0)
                return "null";
            int start = manifest.IndexOf('{', i), depth = 0;
            for (int k = start; k < manifest.Length; k++)
            {
                if (manifest[k] == '{') depth++;
                else if (manifest[k] == '}' && --depth == 0)
                    return manifest.Substring(start, k - start + 1);
            }
            return "null";
        }

        // -- compose -------------------------------------------------------------------------------------------------

        /// <summary>The corner composed and saved, then checked from what was saved; stills with -stills.</summary>
        public static void Compose()
        {
            var clock = Stopwatch.StartNew();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            try
            {
                ComposeOpen();
                Save();
            }
            finally
            {
                urp.shadowDistance = reach;
            }
            Debug.Log($"[LT1Play] composed in {clock.Elapsed.TotalSeconds:F0} s");
            Check();
            string stills = Cli.Arg("-stills", null);
            if (stills != null)
                Stills(Cli.RepoPath("-stills", stills));
        }

        /// <summary>
        /// The corner composed in the open scene, unsaved (Stage opens the heart's scene; nothing saves it): the stage
        /// and the play object. For W3's harness arm, which adds its runner and saves elsewhere.
        /// </summary>
        public static (StreetStage stage, PlayCorner corner) ComposeOpen()
        {
            GullyHashes();
            string record = Records();
            var export = LT1Time.Houses(record);
            var rows = export.buildings.Where(b => b.arm == Arm && b.year == Year).OrderBy(b => b.letter).ToList();
            if ((record == HousesRecord && export.style != Style) || rows.Count != HouseCount)
                throw new System.Exception($"[LT1Play] {record} holds {rows.Count} houses at {Year} in style {export.style}, " +
                                           $"not {HouseCount} at {Style}: run blender/tools/export_time.py --style {Style} --arms {Arm} --years {Year} --out Assets/Art/Buildings/playable");

            var (stage, stone) = LT1Stone.Stage(false);

            // the corner's houses in place of the heart's grey masses for them (as LT1Time stands them)
            var heart = GameObject.Find("The heart (clay)") ?? throw new MissingReferenceException("[LT1Play] no heart in the scene");
            var masses = heart.transform.Find("buildings_corner") ?? throw new MissingReferenceException("[LT1Play] the heart has no buildings_corner to replace");
            masses.gameObject.SetActive(false);
            var houses = new GameObject(HousesRoot).transform;
            houses.SetParent(heart.transform, false);
            var street = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Street.mat");
            var placed = LT1Time.PlaceHouses(houses, export, Arm, Year, street);

            // the corner's birch in C's yard (as the harness plants it)
            var (_, birch, _, height) = LT1Perf.PlantBirch();

            // what the player switches between: the judging views, lights and moods, in their tools' order
            var play = new GameObject(PlayRoot);
            var corner = play.AddComponent<PlayCorner>();
            play.AddComponent<FrameTimeOverlay>();
            corner.stage = stage;
            corner.views = ViewNames.Select(n => LT1Stone.Views.First(v => v.name == n))
                .Select(v => new PlayCorner.View { name = v.name, position = v.pos, target = v.target, fov = v.fov }).ToArray();
            corner.moments = LT1Stone.Moments.Select(m => new PlayCorner.Moment
            {
                name = m,
                rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{m}.asset")
                      ?? throw new FileNotFoundException($"[LT1Play] no rig {m}: LT1Heart.Rigs writes it"),
            }).ToArray();
            corner.moods = LT1Heart.Moods
                .Select(m => new PlayCorner.Mood { name = m, grade = AssetDatabase.LoadAssetAtPath<Grade>($"{Lights}/Moods/Mood_{m}.asset") })
                .Where(m => m.grade != null).ToArray();
            corner.view = 0;
            corner.moment = 0;
            corner.mood = -1;
            var leaves = birch.GetComponentsInChildren<MeshRenderer>();
            corner.boundsOf = leaves;
            corner.bounds = leaves.Select(r => r.localBounds).ToArray();
            corner.keep = new[] { Shader.Find("Hidden/Overstory/TownHeight"), Shader.Find("Hidden/Overstory/SkyMapProbe") }
                .Where(s => s != null).ToArray();

            // the first view and light, as the player opens on them (the camera placed, the shot left out of the scene)
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            stage.rig = corner.moments[0].rig;
            stage.mood = null;
            LT1Stone.Aim(stage, shot, LT1Stone.Views.First(v => v.name == ViewNames[0]));
            stage.shot = null;
            Object.DestroyImmediate(shot);
            if (stage.skyMap != null)
                stage.skyMap.Build();     // the town's sky map over the houses, the stone and the birch

            Debug.Log($"[LT1Play] the corner: stone {stone.name}; {placed.Count} houses ({string.Join(", ", placed.Select(h => h.name))}); " +
                      $"the birch {height:F1} m; {corner.views.Length} views, {corner.moments.Length} lights, {corner.moods.Length} moods");
            return (stage, corner);
        }

        /// <summary>The houses' record: the walk's own, or another set of export_time.py's with -houses (to compare).</summary>
        static string Records() => Cli.Arg("-houses", HousesRecord);

        /// <summary>The open scene saved as a copy into Generated/ (the heart's scene stays as it was on disk).</summary>
        static void Save()
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath, "..", Generated));
            AssetDatabase.Refresh();
            var scene = EditorSceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, ScenePath, true))
                throw new System.Exception($"[LT1Play] could not save {ScenePath}");
            Debug.Log($"[LT1Play] saved {ScenePath} (the open scene, {scene.path}, not saved)");
        }

        // -- check -----------------------------------------------------------------------------------------------------

        /// <summary>
        /// The saved scene opened and checked: the gully's hashes, the stone in it from the hashed FBX, the five houses
        /// from the record, the birch, the three lights. Throws on any miss, so a batch run exits with an error.
        /// </summary>
        public static void Check()
        {
            var (stairs, walls) = GullyHashes();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var problems = new List<string>();
            string Source(GameObject go) => AssetDatabase.GetAssetPath(PrefabUtility.GetCorrespondingObjectFromSource(go));
            var roots = Object.FindObjectsByType<Transform>(FindObjectsInactive.Include)
                .Where(t => PrefabUtility.IsOutermostPrefabInstanceRoot(t.gameObject)).Select(t => t.gameObject).ToList();

            int stoneStairs = roots.Count(g => Source(g) == $"{StoneArt}/stone_gully.fbx");
            int stoneWalls = roots.Count(g => Source(g) == $"{StoneArt}/stone_gully_cheeks.fbx");
            if (stoneStairs != 1 || stoneWalls != 1)
                problems.Add($"the gully in the scene: {stoneStairs} stairs and {stoneWalls} cheek walls from the hashed FBX, not 1 and 1");

            var export = LT1Time.Houses(Records());
            var want = export.buildings.Where(b => b.arm == Arm && b.year == Year).ToDictionary(b => b.file);
            var housesRoot = GameObject.Find(HousesRoot);
            var houses = housesRoot == null ? new List<GameObject>()
                : housesRoot.transform.Cast<Transform>().Select(t => t.gameObject).Where(g => g.activeInHierarchy).ToList();
            var houseLines = new List<string>();
            foreach (var h in houses)
            {
                string src = Source(h);
                if (!want.TryGetValue(src, out var row))
                {
                    problems.Add($"a house not in the record: {h.name} from {src}");
                    continue;
                }
                var at = Overstory.World.StreetSpace.ToUnity(row.position.V);
                if ((h.transform.localPosition - at).sqrMagnitude > 1e-6f)
                    problems.Add($"{h.name} stands at {h.transform.localPosition}, not the record's {at}");
                houseLines.Add($"{row.letter} ({row.id}) {row.hash ?? "no hash"} {row.tris} triangles");
            }
            if (houses.Count != HouseCount)
                problems.Add($"{houses.Count} houses, not {HouseCount}");
            var masses = GameObject.Find("The heart (clay)")?.transform.Find("buildings_corner");
            if (masses == null || masses.gameObject.activeSelf)
                problems.Add("the heart's grey masses for the houses are still shown");

            var trees = GameObject.Find("Trees (the corner's birch)");
            int birches = trees == null ? 0 : trees.transform.Cast<Transform>().Count(t => Source(t.gameObject).StartsWith("Assets/Art/Trees/birch/"));
            if (birches != 1)
                problems.Add($"{birches} birches, not 1");

            var corner = Object.FindAnyObjectByType<PlayCorner>();
            int rigs = corner == null || corner.moments == null ? 0 : corner.moments.Select(m => m.rig).Where(r => r != null).Distinct().Count();
            if (rigs != LT1Stone.Moments.Length)
                problems.Add($"{rigs} light rigs, not {LT1Stone.Moments.Length}");
            int views = corner == null || corner.views == null ? 0 : corner.views.Length;
            if (views != ViewNames.Length)
                problems.Add($"{views} views, not {ViewNames.Length}");
            if (corner != null && corner.stage == null)
                problems.Add("the play object has no stage");
            if (Object.FindAnyObjectByType<FrameTimeOverlay>() == null)
                problems.Add("no frame-time overlay");

            Debug.Log($"[LT1Play] check {ScenePath}:\n" +
                      $"  the gully: stairs {stairs}, walls {walls} (accepted {Stairs}, {Walls}); in the scene {stoneStairs} stairs, {stoneWalls} cheek walls\n" +
                      $"  {houses.Count} houses at {Year} ({export.style}): {string.Join("; ", houseLines)}\n" +
                      $"  {birches} birch\n" +
                      $"  {rigs} rigs: {(corner == null ? "" : string.Join(", ", corner.moments.Select(m => m.name)))}\n" +
                      $"  {views} views: {(corner == null ? "" : string.Join(", ", corner.views.Select(v => v.name)))}; " +
                      $"{(corner?.moods?.Length ?? 0)} moods: {(corner == null ? "" : string.Join(", ", corner.moods.Select(m => m.name)))}\n" +
                      $"  {(problems.Count == 0 ? "PASS" : "FAIL: " + string.Join("; ", problems))}");
            if (problems.Count > 0)
                throw new System.Exception("[LT1Play] the composed scene fails its check: " + string.Join("; ", problems));
        }

        // -- stills ------------------------------------------------------------------------------------------------------

        /// <summary>Each judging view of the saved scene at the player's size, as PlayCorner shows it, in the lights asked.</summary>
        static void Stills(string outDir)
        {
            if (EditorSceneManager.GetActiveScene().path != ScenePath)
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var corner = Object.FindAnyObjectByType<PlayCorner>();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            try
            {
                corner.Begin();
                for (int m = 0; m < corner.moments.Length; m++)
                {
                    if (!Cli.Wanted("-moments", corner.moments[m].name) || (Cli.Arg("-moments", null) == null && m != 0))
                        continue;     // (drizzle alone unless -moments asks for others)
                    corner.SetLight(m);
                    for (int v = 0; v < corner.views.Length; v++)
                    {
                        if (!Cli.Wanted("-views", corner.views[v].name))
                            continue;
                        corner.SetView(v);
                        string file = Path.Combine(outDir, $"{corner.views[v].name}-{corner.moments[m].name}.png");
                        using (var frame = new PlayerFrame(corner.stage.view))
                        {
                            frame.Render(LT1Time.WarmUp + 1);
                            frame.Save(file);
                        }
                        Debug.Log($"[LT1Play] {file}");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
            }
        }

        // -- the player ----------------------------------------------------------------------------------------------

        /// <summary>
        /// Compose, then the macOS player of the composed scene at App: full screen at 2560 by 1440 with frame timing
        /// stats on (LT1Perf.BuildPlayer), MSAA 4x from the standalone quality level's pipeline (PC_RPAsset), checked
        /// here, never changed. Logs how long Compose and the build each took.
        /// </summary>
        public static void Build()
        {
            var clock = Stopwatch.StartNew();
            Compose();
            double composed = clock.Elapsed.TotalSeconds;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            if (urp.msaaSampleCount != 4)
                throw new System.Exception($"[LT1Play] the pipeline ({urp.name}) draws MSAA {urp.msaaSampleCount}x, not the game's 4x");
            string app = Path.GetFullPath(Path.Combine(Application.dataPath, "..", App));
            if (!LT1Perf.BuildPlayer(app, ScenePath))
                throw new System.Exception("[LT1Play] the player did not build");
            Debug.Log($"[LT1Play] built {app} ({urp.name}, MSAA {urp.msaaSampleCount}x, 2560x1440): compose and check " +
                      $"{composed:F0} s, build {clock.Elapsed.TotalSeconds - composed:F0} s, both {clock.Elapsed.TotalSeconds:F0} s");
        }
    }
}
