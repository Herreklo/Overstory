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
    ///         [-perf-settle 600] [-perf-only street,high]
    ///
    /// The player is run from the logged-in session (rendering needs the GPU and the screen); the Unity editor must not be
    /// open on unity/. Player settings changed for the build (frame timing stats, full screen at 2560 by 1440, running in
    /// the background) are put back afterwards. The generated scene and the player are not kept in git.
    /// </summary>
    public static class LT1Perf
    {
        const string Generated = "Assets/Experiments/LT1/Perf/Generated";
        const string ScenePath = Generated + "/LT1_PerfCorner.unity";
        const string App = "Builds/Perf/OverstoryPerf.app";     // in unity/, not kept in git

        /// <summary>
        /// The corner's birch (docs/experiments.md, LT1, the reset: self-seeded in C's yard around 1950, about 14 m,
        /// leaning over the wall into the lane): the judged downy birch at 60 (seed 1), a little older and taller than the
        /// fact's, so its cost is an upper bound. Street metres, in C's yard beside the lower flight.
        /// </summary>
        static readonly Vector2 BirchAt = new Vector2(44.5f, 28.0f);

        /// <summary>The judging views measured (LT1Stone.Views by name), and the birch's own: its crown filling the frame.</summary>
        static readonly string[] ViewNames = { "eye-foot", "eye-on", "street", "into12", "high" };

        public static void Build()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            Compose();
            urp.shadowDistance = reach;
            string app = Path.GetFullPath(Path.Combine(Application.dataPath, "..", App));
            if (!BuildPlayer(app))
                throw new System.Exception("[LT1Perf] the player did not build");
            if (Cli.Flag("-norun"))
                return;
            string outDir = Cli.RepoPath("-out", $"reviews/perf/{System.DateTime.Now:yyyy-MM-dd}");
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

        /// <summary>The corner staged, the birch planted, the runner added; saved as the generated scene.</summary>
        static void Compose()
        {
            var (stage, go) = LT1Stone.Stage(false);
            var (_, birch, ground, h) = PlantBirch();

            var runner = new GameObject("Perf runner").AddComponent<PerfRunner>();
            runner.stage = stage;
            var views = LT1Stone.Views.Where(v => System.Array.IndexOf(ViewNames, v.name) >= 0)
                .Select(v => new PerfRunner.View { name = v.name, position = v.pos, target = v.target, fov = v.fov }).ToList();
            // the birch's crown filling the frame, from 12 m up beside the lane (as the trees' into12 sheet)
            views.Add(new PerfRunner.View
            {
                name = "birch12", position = new Vector3(BirchAt.x + 13f, BirchAt.y - 9f, ground + 12f),
                target = new Vector3(BirchAt.x, BirchAt.y, ground + h * 0.62f), fov = 46.4f,
            });
            runner.views = views.ToArray();
            runner.moments = LT1Stone.Moments.Select(m => new PerfRunner.Moment
            {
                name = m, rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{m}.asset"),
            }).ToArray();
            runner.birches = new[] { birch };
            var leaves = birch.GetComponentsInChildren<MeshRenderer>();
            runner.boundsOf = leaves;
            runner.bounds = leaves.Select(r => r.localBounds).ToArray();
            runner.withoutBirchesIn = new[] { "1600-low-sun" };
            runner.keep = new[] { Shader.Find("Hidden/Overstory/TownHeight"), Shader.Find("Hidden/Overstory/SkyMapProbe") }
                .Where(s => s != null).ToArray();

            Directory.CreateDirectory(Path.Combine(Application.dataPath, "..", Generated));
            AssetDatabase.Refresh();
            var scene = EditorSceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, ScenePath, true))
                throw new System.Exception($"[LT1Perf] could not save {ScenePath}");
            Debug.Log($"[LT1Perf] composed {ScenePath}: {runner.views.Length} views, {runner.moments.Length} lights");
        }

        /// <summary>The corner's birch planted in the open scene (in memory): its root, the tree, its ground and height.</summary>
        internal static (GameObject root, GameObject birch, float ground, float height) PlantBirch()
        {
            var root = new GameObject("Trees (the corner's birch)");
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

        static bool BuildPlayer(string app)
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
                    scenes = new[] { ScenePath },
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
            foreach (var flag in new[] { "-perf-frames", "-perf-warmup", "-perf-rounds", "-perf-settle", "-perf-only" })
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
