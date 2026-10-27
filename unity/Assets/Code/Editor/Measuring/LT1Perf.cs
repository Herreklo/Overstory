using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Perf;
using Overstory.Scenes;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The frame-time harness (docs/measuring.md; docs/research/performance-at-scale.md, The performance harness, and What
    /// we should do, 1): composes today's corner as the gully's frames stage it (LT1Stone.Stage: the heart in clay, the
    /// stair and its cheek walls in stone), with the corner's birch in C's yard, into a generated scene with a PerfRunner;
    /// builds a macOS player of it with frame timing stats on; and runs it full screen at 2560 by 1440 on the reference
    /// machine, as many times as asked. Each run writes reviews/perf/&lt;date&gt;/run-&lt;n&gt;/ (summary.json, summary.md;
    /// frames.csv and a screenshot per segment are kept out of git), and the runs are compared with each other in
    /// reviews/perf/&lt;date&gt;/runs.md.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Perf.Build
    ///         [-runs 2] [-norun] [-out reviews/perf/2026-10-26] [-perf-frames 150] [-perf-warmup 30] [-perf-rounds 2]
    ///         [-perf-settle 600] [-perf-only street,high] [-perf-passes all,-sky,...,bare,history-off,haze-off]
    ///         [-perf-scenes empty,corner,quad-rgba8,quad-bc7,quad-bc7-half,quad-bc7-two,quad-bc7-tile4,quad-bc7-tile8,
    ///                       quad-bc7-tri-tile8 (R2c's arms: nearmip, tri, lod, grad, direct, tex2d, alu, quiet, noisy)]
    ///         [-perf-views street,high] [-perf-empty-views street] [-perf-shots all|some]
    ///         [-district /abs/path/to/district] [-perf-district-views street,city]
    ///
    /// The player is run from the logged-in session (rendering needs the GPU and the screen); the Unity editor must not be
    /// open on unity/. Player settings changed for the build (frame timing stats, full screen at 2560 by 1440, running in
    /// the background) are put back afterwards. The generated scene and the player are not kept in git.
    ///
    /// The walk's whole scene (LT1g, W3; reviews/lt1/playable/walk/w3-report.md): BuildPlayable composes the corner as the
    /// walk's player shows it (LT1Play.ComposeOpen: the clay town, the five houses at 1989, no tree until 1e unless
    /// -tree card or clay (LT1Play.TreeDefault, proposal Q16: the gate's baseline has no tree), the lamps as the
    /// facts have them), places the runner in it with the walk's nine views (the five judging views and LT1g's four),
    /// leaves out the play's own behaviours but PlayCorner (the frame-time overlay's label and its own frame-timing capture
    /// would be in the numbers), and builds and runs it as Build does, into reviews/perf/&lt;date&gt;/playable/ by default.
    /// Every option above applies; its scene is 'playable' (-perf-scenes empty,playable).
    ///
    ///     tools/perf.sh playable [-runs 2] [-perf-passes all,-beams,-shadows,-beams+shadows,bare,flat] [-tree none|clay|card]
    ///         [-perf-ab 1300-drizzle,1600-low-sun]   (the lights in which every view is measured again without the tree)
    /// </summary>
    public static class LT1Perf
    {
        const string Generated = "Assets/Experiments/LT1/Perf/Generated";
        const string ScenePath = Generated + "/LT1_PerfCorner.unity";
        const string App = "Builds/Perf/OverstoryPerf.app";     // in unity/, not kept in git
        const string PlayableScenePath = Generated + "/LT1_PerfPlayable.unity";
        const string PlayableApp = "Builds/Perf/OverstoryPerfPlayable.app";
        /// <summary>The root PlantBirch plants the corner's birch under.</summary>
        public const string BirchRoot = "Trees (the corner's birch)";

        /// <summary>
        /// The corner's birch (docs/experiments.md, LT1, the reset: self-seeded in C's yard around 1950, about 14 m,
        /// leaning over the wall into the lane): the judged downy birch at 60 (seed 1), a little older and taller than the
        /// fact's, so its cost is an upper bound. Street metres, in C's yard beside the lower flight.
        /// </summary>
        static readonly Vector2 BirchAt = new Vector2(44.5f, 28.0f);

        /// <summary>The judging views measured (LT1Stone.Views by name), and the birch's own: its crown filling the frame.</summary>
        static readonly string[] ViewNames = { "eye-foot", "eye-on", "street", "into12", "high" };

        public static void Build() =>
            BuildAndRun(() => Compose(), ScenePath, App, $"reviews/perf/{System.DateTime.Now:yyyy-MM-dd}");

        /// <summary>The walk's whole scene measured (W3): ComposePlayable, then built and run as Build's corner.</summary>
        public static void BuildPlayable() =>
            BuildAndRun(() => ComposePlayable(), PlayableScenePath, PlayableApp, $"reviews/perf/{System.DateTime.Now:yyyy-MM-dd}/playable");

        /// <summary>
        /// The walk's scene timed and drawn offscreen in the editor, with no window on the screen: the playable scene as
        /// BuildPlayable last composed it (or composed again with -compose), each light and view drawn as the player draws
        /// it (PlayerFrame: 2560 by 1440, the game's MSAA), the arms in turn, a batch of six each a round, six rounds after one
        /// that primes, the median kept; the arms: 'all'; 'march' (HazeVolumeFeature off: the bank marched at every pixel, as before); '-Name' (the renderer
        /// feature of that name off). The editor's own work is in the numbers, so they serve an A/B between the arms of one
        /// run; tools/perf.sh gives the frame. With -stills, each arm's frame of each view is kept (VIEW-LIGHT-ARM.png).
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Perf.Offscreen
        ///         [-lights 1750-blue-hour,...] [-views eye-on,street] [-arms all,march] [-stills dir] [-out file.md] [-compose]
        /// </summary>
        public static void Offscreen()
        {
            const int batches = 6, perBatch = 6;
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
            var features = data.rendererFeatures.Where(f => f != null).ToList();
            var on0 = features.Select(f => f.isActive).ToList();
            var lights = Cli.Arg("-lights", "1750-blue-hour").Split(',');
            var views = Cli.Arg("-views", "eye-on,street").Split(',');
            var arms = Cli.Arg("-arms", "all,march").Split(',');
            string stills = Cli.Arg("-stills", null);
            string outFile = Cli.Arg("-out", "");
            var rows = new List<string>();
            try
            {
                if (Cli.Flag("-compose") || !File.Exists(Path.Combine(Application.dataPath, "..", PlayableScenePath)))
                    ComposePlayable();
                else
                    EditorSceneManager.OpenScene(PlayableScenePath, OpenSceneMode.Single);
                var corner = Object.FindAnyObjectByType<Overstory.Play.PlayCorner>()
                             ?? throw new MissingReferenceException("[LT1Perf] no PlayCorner in the playable scene");
                corner.Begin();
                foreach (var light in lights)
                {
                    int m = System.Array.FindIndex(corner.moments, x => x.name == light);
                    if (m < 0)
                        throw new System.ArgumentException($"no light {light}");
                    corner.SetLight(m);
                    foreach (var viewName in views)
                    {
                        int v = System.Array.FindIndex(corner.views, x => x.name == viewName);
                        if (v < 0)
                            throw new System.ArgumentException($"no view {viewName}");
                        corner.SetView(v);
                        var cells = new List<string>();
                        var cam = corner.stage.view;
                        var camData = cam.GetUniversalAdditionalCameraData();
                        var sun = corner.stage.sun;
                        var (clear0, post0, colour0, msaa0) = (cam.clearFlags, camData.renderPostProcessing, camData.requiresColorOption, urp.msaaSampleCount);
                        var shadows0 = sun != null ? sun.shadows : LightShadows.None;
                        // an arm is what it turns off, joined by '+'
                        void Arm(string arm)
                        {
                            var off = arm.Split('+');
                            for (int i = 0; i < features.Count; i++)
                                features[i].SetActive(on0[i] && !off.Contains("-" + features[i].name) && !(off.Contains("march") && features[i] is HazeVolumeFeature));
                            if (sun != null)
                                sun.shadows = off.Contains("shadows") ? LightShadows.None : shadows0;
                            cam.clearFlags = off.Contains("sky") ? CameraClearFlags.SolidColor : clear0;
                            camData.renderPostProcessing = post0 && !off.Contains("post");
                            camData.requiresColorOption = off.Contains("opaquetex") ? CameraOverrideOption.Off : colour0;
                            urp.msaaSampleCount = off.Contains("msaa") ? 1 : msaa0;
                        }
                        // each arm's still from its own warmed frame; then the arms timed in turn, a batch each a round,
                        // so whatever else the machine does falls on every arm alike
                        foreach (var arm in arms)
                        {
                            Arm(arm);
                            using var still = new PlayerFrame(corner.stage.view);
                            still.Render(LT1Time.WarmUp + 1);
                            if (stills != null)
                                still.Save(Path.Combine(repo, stills, $"{viewName}-{light}-{arm}.png"));
                            still.Wait();
                        }
                        var ms = arms.ToDictionary(a => a, a => new List<double>());
                        for (int b = 0; b <= batches; b++)
                            foreach (var arm in arms)
                            {
                                Arm(arm);
                                using var frame = new PlayerFrame(cam); // (the arm's own sample count)
                                frame.Render(2); // (the arm's first frames prime it)
                                frame.Wait();
                                var clock = System.Diagnostics.Stopwatch.StartNew();
                                frame.Render(perBatch);
                                frame.Wait();
                                if (b > 0) // (the first round only primes)
                                    ms[arm].Add(clock.Elapsed.TotalMilliseconds / perBatch);
                            }
                        Arm("all");
                        foreach (var arm in arms)
                        {
                            var t = ms[arm];
                            t.Sort();
                            cells.Add($"{t[t.Count / 2]:F1}");
                            Debug.Log($"[LT1Perf] offscreen {viewName}@{light} {arm}: {t[t.Count / 2]:F2} ms (batches {string.Join(" ", t.Select(x => x.ToString("F1")))})");
                        }
                        rows.Add($"| {viewName}@{light} | {string.Join(" | ", cells)} |");
                    }
                }
            }
            finally
            {
                for (int i = 0; i < features.Count; i++)
                    features[i].SetActive(on0[i]);
                urp.shadowDistance = reach;
                ShaderUtil.allowAsyncCompilation = async;
            }
            var md = new StringBuilder();
            md.AppendLine($"Milliseconds a frame, offscreen in the editor (LT1Perf.Offscreen; {SystemInfo.graphicsDeviceName}, " +
                          $"{PlayerFrame.Width}x{PlayerFrame.Height}, the game's MSAA, median of {batches} batches of {perBatch}).").AppendLine();
            md.AppendLine($"| View and light | {string.Join(" | ", arms)} |");
            md.AppendLine($"| --- |{string.Concat(Enumerable.Repeat(" --- |", arms.Length))}");
            foreach (var r in rows)
                md.AppendLine(r);
            Debug.Log("[LT1Perf] offscreen\n" + md);
            if (outFile != "")
            {
                string path = Path.Combine(repo, outFile);
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, md.ToString());
            }
        }

        static void BuildAndRun(System.Action compose, string scenePath, string appPath, string defaultOut)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            compose();
            urp.shadowDistance = reach;
            string app = Path.GetFullPath(Path.Combine(Application.dataPath, "..", appPath));
            if (!BuildPlayer(app, scenePath))
                throw new System.Exception("[LT1Perf] the player did not build");
            if (Cli.Flag("-norun"))
                return;
            string outDir = Cli.RepoPath("-out", defaultOut);
            int runs = int.Parse(Cli.Arg("-runs", "2"), CultureInfo.InvariantCulture);
            // (numbered on from any runs already in the folder, so a run can be added to a day's set)
            int first = 1;
            while (Directory.Exists(Path.Combine(outDir, $"run-{first}")))
                first++;
            for (int r = first; r < first + runs; r++)
                Run(app, Path.Combine(outDir, $"run-{r}"), $"run {r}");
            // every complete run in the folder (a run stopped part way, by a key or a lost screen, writes no summary)
            var done = Directory.Exists(outDir)
                ? Directory.GetDirectories(outDir, "run-*").Where(d => File.Exists(Path.Combine(d, "summary.json"))).OrderBy(d => d).ToList()
                : new List<string>();
            if (done.Count > 1)
                CompareRuns(done, Path.Combine(outDir, "runs.md"));
        }

        /// <summary>The corner staged, the birch planted, the runner added; saved as the generated scene (the perf
        /// corner's own unless another path is given).</summary>
        internal static void Compose(string scenePath = ScenePath)
        {
            var (stage, go) = LT1Stone.Stage(false);
            var (_, birch, ground, h) = PlantBirch();

            var views = LT1Stone.Views.Where(v => System.Array.IndexOf(ViewNames, v.name) >= 0)
                .Select(v => new PerfRunner.View { name = v.name, position = v.pos, target = v.target, fov = v.fov }).ToList();
            // the birch's crown filling the frame, from 12 m up beside the lane (as the trees' into12 sheet)
            views.Add(new PerfRunner.View
            {
                name = "birch12", position = new Vector3(BirchAt.x + 13f, BirchAt.y - 9f, ground + 12f),
                target = new Vector3(BirchAt.x, BirchAt.y, ground + h * 0.62f), fov = 46.4f,
            });
            var runner = AddRunner(stage, birch, views.ToArray(), "corner");
            // the scale test's district (loaded only when the player is given -district <dir>), drawn with the street's material
            runner.district = new GameObject("District (the scale test)").AddComponent<DistrictLoader>();
            runner.district.material = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Street.mat");
            // the history quad (step 3: LT1History), drawn only in the quad scenes, each binding its own pages
            (runner.historyQuad, runner.pagesRGBA8, runner.pagesBC7) = LT1History.AddQuad(stage.view);
            runner.historyQuad.enabled = false;
            // and its minified meshes (R2b: the scenes quad-<format>-tile4 and -tile8)
            runner.historyQuadTiles = new[] { 4, 8 };
            runner.historyQuadTiled = runner.historyQuadTiles.Select(k => LT1History.QuadMesh(k)).ToArray();

            Save(scenePath);
            Debug.Log($"[LT1Perf] composed {scenePath}: {runner.views.Length} views, {runner.moments.Length} lights");
        }

        /// <summary>
        /// The runner placed in the open scene: the stage, its views, the three judging lights, the birch with its leaf
        /// bounds and its A/B in low sun, the shaders found by name, the pass study's renderer and flat material.
        /// </summary>
        static PerfRunner AddRunner(StreetStage stage, GameObject birch, PerfRunner.View[] views, string composed)
        {
            var runner = new GameObject("Perf runner").AddComponent<PerfRunner>();
            runner.stage = stage;
            runner.composed = composed;
            runner.views = views;
            runner.moments = LT1Stone.Moments.Select(m => new PerfRunner.Moment
            {
                name = m, rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{m}.asset"),
            }).ToArray();
            // (no tree in the walk's corner until 1e: no A/B then)
            runner.birches = birch == null ? new GameObject[0] : new[] { birch };
            var leaves = birch == null ? new MeshRenderer[0] : birch.GetComponentsInChildren<MeshRenderer>();
            runner.boundsOf = leaves;
            runner.bounds = leaves.Select(r => r.localBounds).ToArray();
            // (-perf-ab <light,...>: the lights the A/B measures without the tree; low sun unless asked)
            runner.withoutBirchesIn = Cli.Arg("-perf-ab", "1600-low-sun").Split(',');
            runner.keep = new[] { Shader.Find("Hidden/Overstory/TownHeight"), Shader.Find("Hidden/Overstory/SkyMapProbe") }
                .Where(s => s != null).ToArray();
            runner.rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
            runner.flat = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "Flat (the pass study)" };
            return runner;
        }

        /// <summary>The open scene saved as a generated scene (a copy: the scene it was opened from stays as it is on disk).</summary>
        static void Save(string scenePath)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath, "..", Path.GetDirectoryName(scenePath)));
            AssetDatabase.Refresh();
            var scene = EditorSceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, scenePath, true))
                throw new System.Exception($"[LT1Perf] could not save {scenePath}");
        }

        /// <summary>
        /// The walk's corner as its player shows it (LT1Play.ComposeOpen), with the runner placed in it (W3; the
        /// pre-mortem's "W3 places the runner": the harness's scenes are setups inside one build, so the walk's scene is
        /// a build of its own). The play's own behaviours are left out but PlayCorner, which sets the town's globals at the
        /// start as the player does: the frame-time overlay (its label's draw and its own FrameTimingManager capture would
        /// be in the numbers) and whatever later stages add to steer the camera, which the runner holds instead. The views
        /// are the player's own, in its order: the five judging views, then LT1g's four (LT1Play.CaseViews).
        /// </summary>
        internal static void ComposePlayable(string scenePath = PlayableScenePath)
        {
            var (stage, corner) = LT1Play.ComposeOpen();
            var left = new List<string>();
            foreach (var mb in Object.FindObjectsByType<MonoBehaviour>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                if (mb != null && mb.GetType().Namespace == typeof(Overstory.Play.PlayCorner).Namespace && !(mb is Overstory.Play.PlayCorner))
                {
                    left.Add(mb.GetType().Name);
                    Object.DestroyImmediate(mb);
                }
            // the corner's tree, if the switch planted one (LT1Play.TreeKind)
            var trees = GameObject.Find(BirchRoot);
            var birch = trees == null || trees.transform.childCount == 0 ? null : trees.transform.GetChild(0).gameObject;
            if ((birch == null) != (LT1Play.TreeKind == "none"))
                throw new MissingReferenceException($"[LT1Perf] the walk's corner {(birch == null ? "has no tree" : "has a tree")}, but -tree is {LT1Play.TreeKind}");
            var views = corner.views.Select(v => new PerfRunner.View { name = v.name, position = v.position, target = v.target, fov = v.fov }).ToArray();
            var runner = AddRunner(stage, birch, views, "playable");
            Save(scenePath);
            Debug.Log($"[LT1Perf] composed {scenePath}: the walk's corner, {runner.views.Length} views ({string.Join(", ", views.Select(v => v.name))}), " +
                      $"{runner.moments.Length} lights; left out: {(left.Count == 0 ? "nothing" : string.Join(", ", left))}");
        }

        /// <summary>The corner's birch planted in the open scene (in memory): its root, the tree, its ground and height.</summary>
        internal static (GameObject root, GameObject birch, float ground, float height) PlantBirch()
        {
            var root = new GameObject(BirchRoot);
            float ground = GroundAt(BirchAt);
            var birch = LT1Trees.Place(root.transform, "birch", 1, 60, new Vector3(BirchAt.x, BirchAt.y, ground), 0f);
            float top = birch.GetComponentsInChildren<MeshRenderer>().Max(r => r.bounds.max.y);
            float h = top - StreetSpace.ToUnity(new Vector3(BirchAt.x, BirchAt.y, ground)).y;
            Debug.Log($"[LT1Perf] the corner's birch at {BirchAt} on ground {ground:F2} m, {h:F1} m tall");
            return (root, birch, ground, h);
        }

        /// <summary>The clay ground's height (street metres) under a point, by a ray against the ground's own meshes.</summary>
        static float GroundAt(Vector2 p)
        {
            var added = new List<MeshCollider>();
            try
            {
                foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
                    if (mf.gameObject.name.StartsWith("ground") && mf.GetComponent<Collider>() == null)
                        added.Add(mf.gameObject.AddComponent<MeshCollider>());
                Physics.SyncTransforms();
                if (!Physics.Raycast(StreetSpace.ToUnity(p.x, p.y, 400f), Vector3.down, out var hit, 800f))
                    throw new System.Exception($"[LT1Perf] no ground under {p}");
                return hit.point.y;
            }
            finally
            {
                foreach (var c in added)
                    Object.DestroyImmediate(c);
            }
        }

        /// <summary>
        /// A macOS player of one scene (the perf corner's unless another is given), with frame timing stats on, full
        /// screen at 2560 by 1440 and running in the background; those settings are put back afterwards. True when it built.
        /// </summary>
        internal static bool BuildPlayer(string app, string scenePath = ScenePath)
        {
            bool timing = PlayerSettings.enableFrameTimingStats;
            bool background = PlayerSettings.runInBackground;
            var mode = PlayerSettings.fullScreenMode;
            int w = PlayerSettings.defaultScreenWidth, h = PlayerSettings.defaultScreenHeight;
            try
            {
                PlayerSettings.enableFrameTimingStats = true;
                PlayerSettings.runInBackground = true;
                PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
                PlayerSettings.defaultScreenWidth = 2560;
                PlayerSettings.defaultScreenHeight = 1440;
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { scenePath },
                    locationPathName = app,
                    target = BuildTarget.StandaloneOSX,
                    options = BuildOptions.None,
                });
                var s = report.summary;
                Debug.Log($"[LT1Perf] build {s.result}: {app}, {s.totalSize / 1048576} MB, {s.totalTime.TotalSeconds:F0} s, {s.totalErrors} errors");
                return s.result == BuildResult.Succeeded;
            }
            finally
            {
                PlayerSettings.enableFrameTimingStats = timing;
                PlayerSettings.runInBackground = background;
                PlayerSettings.fullScreenMode = mode;
                PlayerSettings.defaultScreenWidth = w;
                PlayerSettings.defaultScreenHeight = h;
            }
        }

        /// <summary>One run of the player, full screen at 2560 by 1440, waited for. True when it wrote its summary.</summary>
        static bool Run(string app, string dir, string label)
        {
            Directory.CreateDirectory(dir);
            var args = new List<string>
            {
                "-W", "-n", app, "--args",
                "-screen-fullscreen", "1", "-screen-width", "2560", "-screen-height", "1440",
                "-perf-out", dir, "-perf-label", label, "-logFile", Path.Combine(dir, "player.log"),
            };
            foreach (var flag in new[] { "-perf-frames", "-perf-warmup", "-perf-rounds", "-perf-settle", "-perf-only",
                                         "-perf-passes", "-perf-scenes", "-perf-views", "-perf-empty-views", "-perf-shots",
                                         "-district", "-perf-district-views", "-perf-offscreen-scale" })
                if (Cli.Arg(flag, null) != null)
                {
                    args.Add(flag);
                    args.Add(Cli.Arg(flag, null));
                }
            var psi = new System.Diagnostics.ProcessStartInfo("/usr/bin/open",
                string.Join(" ", args.Select(a => "\"" + a.Replace("\"", "\\\"") + "\""))) { UseShellExecute = false };
            var clock = System.Diagnostics.Stopwatch.StartNew();
            using (var p = System.Diagnostics.Process.Start(psi))
            {
                if (!p.WaitForExit(60 * 60 * 1000))
                {
                    Debug.LogError($"[LT1Perf] {label}: the player did not finish within an hour");
                    return false;
                }
            }
            bool ok = File.Exists(Path.Combine(dir, "summary.json"));
            Debug.Log($"[LT1Perf] {label}: {(ok ? "done" : "NO SUMMARY")} in {clock.Elapsed.TotalSeconds:F0} s -> {dir}");
            return ok;
        }

        /// <summary>How far the runs agree, per segment: the spread of their medians against their mean.</summary>
        static void CompareRuns(List<string> dirs, string file)
        {
            var runs = dirs.Select(d => JsonUtility.FromJson<PerfRunner.Run>(File.ReadAllText(Path.Combine(d, "summary.json")))).ToList();
            var sb = new StringBuilder("# Frame time: how far the runs agree\n\n");
            sb.Append($"{runs.Count} complete runs ({string.Join(", ", dirs.Select(Path.GetFileName))}). Per segment, each run's ");
            sb.Append("median offscreen time (the view drawn back to back, the GPU kept busy), presented frame period and GPU ");
            sb.Append("time, and each one's spread (largest minus smallest) as a share of their mean. Acceptance: within about 3%.\n\n");
            sb.Append("| Segment | Offscreen (ms) | Spread | Frame (ms) | Spread | GPU (ms) | Spread |\n| --- | --- | --- | --- | --- | --- | --- |\n");
            double worstOff = 0, worstCpu = 0, worstGpu = 0;
            string Ms(IEnumerable<double> v) => string.Join(" / ", v.Select(x => x.ToString("F2", CultureInfo.InvariantCulture)));
            foreach (var s in runs[0].segments)
            {
                var all = runs.Select(r => r.segments.FirstOrDefault(x => x.name == s.name)).Where(x => x != null).ToList();
                double Spread(System.Func<PerfRunner.Segment, double> f)
                {
                    var v = all.Select(f).ToList();
                    return v.Average() > 0 ? (v.Max() - v.Min()) / v.Average() : 0;
                }
                double so = Spread(x => x.offscreen_ms.median), sc = Spread(x => x.cpu_ms.median), sg = Spread(x => x.gpu_ms.median);
                worstOff = System.Math.Max(worstOff, so);
                worstCpu = System.Math.Max(worstCpu, sc);
                worstGpu = System.Math.Max(worstGpu, sg);
                sb.Append($"| {s.name} | {Ms(all.Select(x => x.offscreen_ms.median))} | {100 * so:F1}% | {Ms(all.Select(x => x.cpu_ms.median))} | ");
                sb.Append($"{100 * sc:F1}% | {Ms(all.Select(x => x.gpu_ms.median))} | {100 * sg:F1}% |\n");
            }
            sb.Append($"\nWorst spread: offscreen {100 * worstOff:F1}%, frame {100 * worstCpu:F1}%, GPU {100 * worstGpu:F1}%.\n");
            File.WriteAllText(file, sb.ToString());
            Debug.Log($"[LT1Perf] runs agree within offscreen {100 * worstOff:F1}%, frame {100 * worstCpu:F1}%, GPU {100 * worstGpu:F1}% -> {file}");
        }
    }
}
