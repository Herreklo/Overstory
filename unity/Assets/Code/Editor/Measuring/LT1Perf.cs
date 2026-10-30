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
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The frame-time harness (docs/measuring.md; docs/research/performance-at-scale.md, The performance harness, and What
    /// we should do, 1): composes the street as its own test stages it (StreetStaging: Street.unity as the last
    /// LT1Street.Run left it, its houses, its judging views and its two lights) into a generated scene with a PerfRunner;
    /// builds a macOS player of it with frame timing stats on; and runs it full screen at 2560 by 1440 on the reference
    /// machine, as many times as asked. Each run writes reviews/perf/&lt;date&gt;/street/run-&lt;n&gt;/ (summary.json,
    /// summary.md; frames.csv and a screenshot per segment are kept out of git), and the runs are compared with each
    /// other in runs.md beside them.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Perf.Build
    ///         [-runs 2] [-norun] [-out reviews/perf/2026-10-30/street] [-views eye,street,raised,high]
    ///         [-perf-frames 150] [-perf-warmup 30] [-perf-rounds 2] [-perf-settle 600] [-perf-only street,high]
    ///         [-perf-passes all,-sky,-shadows,-ssao,-post,-msaa,-townlight,-opaquetex,-depthtex,bare,flat]
    ///         [-perf-scenes empty,street] [-perf-views street,high] [-perf-empty-views street] [-perf-shots all|some]
    ///         [-district /abs/path/to/district] [-perf-district-views street,city]
    ///
    /// The street is whatever its test last built (blender/parts/street/run/render.sh: one house, or a row with
    /// -streetHouses); its views are the test's own for that (StreetStaging; -views at compose time keeps some), in way
    /// Pc (the colour), each house at the level its distance takes. The player is run from the logged-in session
    /// (rendering needs the GPU and the screen); the Unity editor must not be open on unity/. Player settings changed for
    /// the build (frame timing stats, full screen at 2560 by 1440, running in the background) are put back afterwards.
    /// The generated scene, its copies of the sky's and ground's materials and the volume's profile, and the player are
    /// not kept in git; nothing of the street's own is written.
    /// </summary>
    public static class LT1Perf
    {
        const string Generated = StreetStaging.Own;
        const string ScenePath = Generated + "/LT1_PerfStreet.unity";
        const string App = "Builds/Perf/OverstoryPerf.app";     // in unity/, not kept in git

        public static void Build() =>
            BuildAndRun(() => Compose(), ScenePath, App, $"reviews/perf/{System.DateTime.Now:yyyy-MM-dd}/street");

        /// <summary>
        /// The street timed and drawn offscreen in the editor, with no window on the screen: staged as its test stages it
        /// (StreetStaging), each light and view drawn as the player draws it (PlayerFrame: 2560 by 1440, the game's MSAA),
        /// the arms in turn, a batch of six each a round, six rounds after one that primes, the median kept. An arm is
        /// what it turns off, joined by '+': 'all' (nothing); '-Name' (the renderer feature of that name; the street's
        /// pipeline has the screen-space occlusion alone); 'shadows'; 'hard' (the sun's shadows hard); 'sky' (the drawn
        /// sky); 'post'; 'opaquetex'; 'msaa'; 'Name.path=value' sets a serialized field of that renderer feature. The
        /// editor's own work is in the numbers, so they serve an A/B between the arms of one run; tools/perf.sh gives the
        /// frame. With -stills, each arm's frame of each view is kept (VIEW-LIGHT-ARM.png).
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Perf.Offscreen
        ///         [-lights overcast,lowsun] [-views eye,street] [-arms all,shadows] [-stills dir] [-out file.md]
        /// </summary>
        public static void Offscreen()
        {
            int batches = int.Parse(Cli.Arg("-batches", "6"), CultureInfo.InvariantCulture);
            const int perBatch = 6;
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var arms = Cli.Arg("-arms", "all").Split(',');
            string stills = Cli.Arg("-stills", null);
            string outFile = Cli.Arg("-out", "");
            var rows = new List<string>();
            using (StreetStaging.Pipeline())
            {
                var s = StreetStaging.Open();
                var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
                var features = data.rendererFeatures.Where(f => f != null).ToList();
                var on0 = features.Select(f => f.isActive).ToList();     // (the street's pipeline: the occlusion alone)
                var cam = s.cam;
                var camData = cam.GetUniversalAdditionalCameraData();
                var sun = s.sun;
                var set0 = new Dictionary<(ScriptableRendererFeature f, string path), string>();
                try
                {
                    foreach (var light in s.lightNames.Where(l => Cli.Wanted("-lights", l)))
                        foreach (var stop in s.stops)
                        {
                            s.Apply(light, stop);
                            var cells = new List<string>();
                            var (post0, colour0, msaa0) = (camData.renderPostProcessing, camData.requiresColorOption, urp.msaaSampleCount);
                            var shadows0 = sun.shadows;
                            bool sky0 = s.sky.activeSelf;
                            void Set(ScriptableRendererFeature f, string path, string value)
                            {
                                var so = new SerializedObject(f);
                                var prop = so.FindProperty(path) ?? throw new System.ArgumentException($"no {path} in {f.name}");
                                string was = prop.propertyType switch
                                {
                                    SerializedPropertyType.Float => prop.floatValue.ToString(CultureInfo.InvariantCulture),
                                    SerializedPropertyType.Boolean => prop.boolValue ? "1" : "0",
                                    _ => prop.intValue.ToString(),
                                };
                                if (!set0.ContainsKey((f, path)))
                                    set0[(f, path)] = was;
                                if (prop.propertyType == SerializedPropertyType.Float)
                                    prop.floatValue = float.Parse(value, CultureInfo.InvariantCulture);
                                else if (prop.propertyType == SerializedPropertyType.Boolean)
                                    prop.boolValue = value == "1";
                                else
                                    prop.intValue = int.Parse(value);
                                so.ApplyModifiedPropertiesWithoutUndo();
                                f.Create();
                            }
                            void Arm(string arm)
                            {
                                var off = arm.Split('+');
                                foreach (var kv in set0.ToList())
                                    Set(kv.Key.f, kv.Key.path, kv.Value);
                                foreach (var item in off.Where(o => o.Contains('=')))
                                {
                                    int dot = item.IndexOf('.'), eq = item.IndexOf('=');
                                    var f = features.First(x => x.name == item.Substring(0, dot));
                                    Set(f, item.Substring(dot + 1, eq - dot - 1), item.Substring(eq + 1));
                                }
                                for (int i = 0; i < features.Count; i++)
                                    features[i].SetActive(on0[i] && !off.Contains("-" + features[i].name));
                                sun.shadows = off.Contains("shadows") ? LightShadows.None : off.Contains("hard") ? LightShadows.Hard : shadows0;
                                s.sky.SetActive(sky0 && !off.Contains("sky"));
                                camData.renderPostProcessing = post0 && !off.Contains("post");
                                camData.requiresColorOption = off.Contains("opaquetex") ? CameraOverrideOption.Off : colour0;
                                urp.msaaSampleCount = off.Contains("msaa") ? 1 : msaa0;
                            }
                            // each arm's still from its own warmed frame; then the arms timed in turn, a batch each a
                            // round, so whatever else the machine does falls on every arm alike
                            foreach (var arm in arms)
                            {
                                Arm(arm);
                                using var still = new PlayerFrame(cam);
                                still.Render(LT1Golden.WarmUp + 1);
                                if (stills != null)
                                    still.Save(Path.Combine(repo, stills, $"{stop.name}-{light}-{arm}.png"));
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
                                Debug.Log($"[LT1Perf] offscreen {stop.name}@{light} {arm}: {t[t.Count / 2]:F2} ms (batches {string.Join(" ", t.Select(x => x.ToString("F1")))})");
                            }
                            rows.Add($"| {stop.name}@{light} | {string.Join(" | ", cells)} |");
                        }
                }
                finally
                {
                    foreach (var kv in set0.ToList())
                    {
                        var so = new SerializedObject(kv.Key.f);
                        var prop = so.FindProperty(kv.Key.path);
                        if (prop.propertyType == SerializedPropertyType.Float)
                            prop.floatValue = float.Parse(kv.Value, CultureInfo.InvariantCulture);
                        else if (prop.propertyType == SerializedPropertyType.Boolean)
                            prop.boolValue = kv.Value == "1";
                        else
                            prop.intValue = int.Parse(kv.Value);
                        so.ApplyModifiedPropertiesWithoutUndo();
                        kv.Key.f.Create();
                    }
                }
            }
            var md = new StringBuilder();
            md.AppendLine($"Milliseconds a frame, offscreen in the editor (LT1Perf.Offscreen, the street; {SystemInfo.graphicsDeviceName}, " +
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
            compose();
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

        /// <summary>
        /// The street staged as its test stages it and the plan of every light at every view recorded into a runner, so
        /// the player puts each back as the editor applied it (PerfRunner.Lit): the sun, the trilight and its probe, the
        /// background, the drawn sky and its reflection, the ground, the exposure, and what the town's sky map reads of
        /// each renderer. The houses wear way Pc (the colour). Saved as the generated scene, with its own copies of the
        /// sky's and ground's materials, the volume's profile and a reflection cube per light; the street's scene and
        /// assets stay as they are on disk.
        /// </summary>
        internal static void Compose(string scenePath = ScenePath)
        {
            StreetStaging.Folder(Generated);
            using (StreetStaging.Pipeline())
            {
                var s = StreetStaging.Open();
                // the copies StreetStaging made, kept as the generated scene's own assets
                AssetDatabase.CreateAsset(s.skyMat, Generated + "/sky.mat");
                AssetDatabase.CreateAsset(s.groundMat, Generated + "/ground.mat");
                var profile = s.volume.sharedProfile;
                AssetDatabase.CreateAsset(profile, Generated + "/volume.asset");
                foreach (var c in profile.components)
                    AssetDatabase.AddObjectToAsset(c, profile);
                AssetDatabase.SaveAssetIfDirty(profile);
                s.AssignAll("Pc");

                var townRenderers = s.town != null && s.town.town != null
                    ? s.town.town.GetComponentsInChildren<Renderer>(true) : new Renderer[0];
                var cubes = s.lightNames.ToDictionary(l => l, l => new Cubemap(32, TextureFormat.RGBAHalf, true) { name = $"reflection-{l}" });
                var lit = new List<PerfRunner.Lit>();
                foreach (var light in s.lightNames)
                    foreach (var stop in s.stops)
                    {
                        s.Apply(light, stop, "Pc", cubes[light]);
                        var probe = RenderSettings.ambientProbe;
                        var coefficients = new float[27];
                        for (int ch = 0; ch < 3; ch++)
                            for (int k = 0; k < 9; k++)
                                coefficients[ch * 9 + k] = probe[ch, k];
                        var albedo = townRenderers.Select(r => s.Albedo(r, "Pc")).ToArray();
                        lit.Add(new PerfRunner.Lit
                        {
                            light = light, view = stop.name,
                            sunRotation = s.sun.transform.rotation, sunColour = s.sun.color, sunIntensity = s.sun.intensity, sunShadow = s.sun.shadowStrength,
                            ambientSky = RenderSettings.ambientSkyColor, ambientEquator = RenderSettings.ambientEquatorColor,
                            ambientGround = RenderSettings.ambientGroundColor, probe = coefficients,
                            background = s.cam.backgroundColor, skyOn = s.sky.activeSelf, zenith = s.skyMat.GetVector("_SkyZenith"),
                            reflection = cubes[light], ground = s.groundMat.GetColor("_BaseColor"), exposure = s.adjust.postExposure.value,
                            wall = albedo.Select(a => a.wall).ToArray(), top = albedo.Select(a => a.top).ToArray(),
                        });
                    }
                foreach (var kv in cubes)
                    AssetDatabase.CreateAsset(kv.Value, $"{Generated}/{kv.Value.name}.cubemap");

                var runner = new GameObject("Perf runner").AddComponent<PerfRunner>();
                runner.view = s.cam;
                runner.sun = s.sun;
                runner.volume = s.volume;
                runner.sky = s.sky;
                runner.skyMaterial = s.skyMat;
                runner.groundMaterial = s.groundMat;
                runner.town = s.town;
                runner.townRenderers = townRenderers;
                runner.houseIds = string.Join(",", s.ids);
                runner.houses = s.roots.Select((r, i) => new PerfRunner.House
                {
                    id = s.ids[i], levels = s.levels[i].Values.ToArray(), names = s.levels[i].Keys.ToArray(),
                }).ToArray();
                runner.views = s.stops.Select(v => new PerfRunner.View
                {
                    name = v.name, position = v.pos, target = v.target, fov = v.fov, levels = v.levels, shadowDistance = v.shadowDistance,
                }).ToArray();
                runner.lit = lit.ToArray();
                runner.keep = new[] { "Hidden/Overstory/TownHeight", "Hidden/Overstory/TownHorizon", "Hidden/Overstory/SkyMapProbe" }
                    .Select(Shader.Find).Where(x => x != null).ToArray();
                runner.rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
                runner.flat = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "Flat (the pass study)" };
                AssetDatabase.CreateAsset(runner.flat, Generated + "/flat.mat");
                // the scale test's district (loaded only when the player is given -district <dir>), drawn with the street's material
                runner.district = new GameObject("District (the scale test)").AddComponent<DistrictLoader>();
                runner.district.material = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Street.mat");

                Save(scenePath);
                Debug.Log($"[LT1Perf] composed {scenePath}: the street (house{(s.row ? "s" : "")} {runner.houseIds}), " +
                          $"views {string.Join(", ", runner.views.Select(v => v.name))}, lights {string.Join(", ", s.lightNames)}, " +
                          $"{townRenderers.Length} renderers in the town's map");
            }
            // the copy opened in place of the street's scene, so nothing later can save the street's
            EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
        }

        /// <summary>The open scene saved as a generated scene (a copy: the scene it was opened from stays as it is on disk).</summary>
        static void Save(string scenePath)
        {
            var scene = EditorSceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, scenePath, true))
                throw new System.Exception($"[LT1Perf] could not save {scenePath}");
        }

        /// <summary>
        /// A macOS player of one scene, with frame timing stats on, full screen at 2560 by 1440 and running in the
        /// background; those settings are put back afterwards. True when it built.
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
