using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.Perf
{
    /// <summary>
    /// The frame-time harness's runner (docs/measuring.md, The frame-time harness; docs/research/performance-at-scale.md,
    /// The performance harness): runs in a built player, never the editor, holds each judging view in each light for a
    /// fixed number of frames, and records per frame the CPU and GPU frame time (FrameTimingManager), the draw calls,
    /// SetPass calls, triangles, vertices and shadow casters (ProfilerRecorder; a release player has no batch count), and
    /// memory. Writes a CSV of
    /// every frame, a JSON summary per segment (median, 95th and 99th percentile, worst) and a short markdown table,
    /// keeps one screenshot per segment, then quits.
    ///
    /// The plan (views, lights, the birches to hide for the A/B segments) is set by LT1Perf.Build when it composes the
    /// scene. Command line: -perf-out &lt;dir&gt; (required; without it the runner does nothing), -perf-frames N (a segment's
    /// frames per round), -perf-warmup N, -perf-rounds N, -perf-settle N, -perf-only &lt;name,...&gt; (segments whose names
    /// start so), -perf-label &lt;text&gt;. Every segment is measured once per round, the rounds one after another, after the
    /// first segment has been drawn for a while to let the machine settle; screenshots are taken after all measuring.
    /// The world's clock is the light's own (StreetStage: _OS_Time from the rig), so every segment draws a still world.
    /// </summary>
    public class PerfRunner : MonoBehaviour
    {
        [System.Serializable]
        public class View
        {
            public string name;
            public Vector3 position;
            public Vector3 target;
            public float fov;
        }

        [System.Serializable]
        public class Moment
        {
            public string name;
            public LightRig rig;
        }

        public StreetStage stage;
        public View[] views;
        public Moment[] moments;
        [Tooltip("The birches in the corner: drawn in every segment but the A/B ones, where they are hidden.")]
        public GameObject[] birches;
        [Tooltip("The moments (lights) in which every view is measured a second time without the birches (A/B).")]
        public string[] withoutBirchesIn;
        [Tooltip("Frames drawn before each segment's measured frames are kept.")]
        public int warmUp = 30;
        [Tooltip("Frames measured per segment in each round.")]
        public int frames = 150;
        [Tooltip("Rounds: every segment is measured once a round.")]
        public int rounds = 2;
        [Tooltip("Frames drawn on the first segment after the player starts, before anything is measured.")]
        public int settle = 600;
        [Tooltip("Offscreen: batches of back-to-back renders per segment and round (after one that only primes), and renders a batch.")]
        public int offscreenBatches = 6, offscreenPerBatch = 6;
        public float near = 0.1f, far = 9000f, shadowDistance = 120f;
        [Tooltip("Shaders the scene's components find by name at runtime (SkyMap), held here so the build keeps them.")]
        public Shader[] keep;
        [Tooltip("Renderers whose bounds the editor set by hand (a leaf card is drawn out from its pivot in the shader), " +
                 "with those bounds: a scene keeps no renderer's own bounds, so they are set again here.")]
        public Renderer[] boundsOf;
        public Bounds[] bounds;

        // the counters, by their names in the profiler (ProfilerRecorder; render ones are per frame)
        static readonly (string column, ProfilerCategory category, string counter)[] Counters =
        {
            ("draws", ProfilerCategory.Render, "Draw Calls Count"),
            ("setpass", ProfilerCategory.Render, "SetPass Calls Count"),
            ("triangles", ProfilerCategory.Render, "Triangles Count"),
            ("vertices", ProfilerCategory.Render, "Vertices Count"),
            ("shadow_casters", ProfilerCategory.Render, "Shadow Casters Count"),
            ("mem_total_used", ProfilerCategory.Memory, "Total Used Memory"),
            ("mem_total_reserved", ProfilerCategory.Memory, "Total Reserved Memory"),
            ("mem_gfx_used", ProfilerCategory.Memory, "Gfx Used Memory"),
            ("mem_gc_used", ProfilerCategory.Memory, "GC Used Memory"),
            ("mem_system_used", ProfilerCategory.Memory, "System Used Memory"),
        };

        static string Arg(string flag, string fallback)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, flag);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }

        void Awake()
        {
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
            for (int i = 0; boundsOf != null && i < boundsOf.Length; i++)
                if (boundsOf[i] != null)
                    boundsOf[i].localBounds = bounds[i];
        }

        IEnumerator Start()
        {
            string outDir = Arg("-perf-out", null);
            if (outDir == null)
                yield break;
            Directory.CreateDirectory(outDir);
            int nFrames = int.Parse(Arg("-perf-frames", frames.ToString()), CultureInfo.InvariantCulture);
            int nWarm = int.Parse(Arg("-perf-warmup", warmUp.ToString()), CultureInfo.InvariantCulture);
            string only = Arg("-perf-only", null);
            string label = Arg("-perf-label", "");

            // the town's shared globals, as the editor's frames set them (LT1Stone.Stage)
            GrowthPack.Apply();
            WaterPack.Apply();
            Shader.SetGlobalFloat("_OS_NearForce", 0f);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            urp.shadowDistance = shadowDistance;

            var segments = new List<(string name, View view, Moment light, bool birchesOn)>();
            foreach (var l in moments)
            {
                foreach (var v in views)
                    segments.Add(($"{v.name}@{l.name}", v, l, true));
                if (withoutBirchesIn != null && System.Array.IndexOf(withoutBirchesIn, l.name) >= 0 && birches != null && birches.Length > 0)
                    foreach (var v in views)
                        segments.Add(($"{v.name}@{l.name}-nobirch", v, l, false));
            }
            if (only != null)
                segments = segments.Where(s => only.Split(',').Any(o => s.name.StartsWith(o))).ToList();

            var recorders = Counters.Select(c => ProfilerRecorder.StartNew(c.category, c.counter, 1)).ToArray();
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var timing = new FrameTiming[1];
            var csv = new StringBuilder("round,segment,frame,cpu_ms,cpu_main_ms,cpu_render_ms,gpu_ms," + string.Join(",", Counters.Select(c => c.column)) + "\n");
            var wallClock = System.Diagnostics.Stopwatch.StartNew();
            int nRounds = int.Parse(Arg("-perf-rounds", rounds.ToString()), CultureInfo.InvariantCulture);
            int nSettle = int.Parse(Arg("-perf-settle", settle.ToString()), CultureInfo.InvariantCulture);

            void Show((string name, View view, Moment light, bool birchesOn) seg)
            {
                foreach (var b in birches ?? new GameObject[0])
                    if (b != null)
                        b.SetActive(seg.birchesOn);
                stage.rig = seg.light.rig;
                shot.position = seg.view.position;
                shot.target = seg.view.target;
                shot.verticalFov = seg.view.fov;
                shot.near = near;
                shot.far = far;
                stage.shot = shot;
                stage.Apply();
            }

            // the machine settles after the player starts (the launch, the first pipelines, the system's own work on a
            // new app): the first segment is drawn for a while before anything is kept
            if (segments.Count > 0)
            {
                Show(segments[0]);
                for (int i = 0; i < nSettle; i++)
                    yield return null;
            }

            // every segment measured once a round, the rounds one after another, so what disturbs the machine for a
            // while lands on several segments a little rather than on one a lot; a segment's numbers are all its frames
            var cpu = segments.ToDictionary(s => s.name, _ => new List<double>());
            var main = segments.ToDictionary(s => s.name, _ => new List<double>());
            var render = segments.ToDictionary(s => s.name, _ => new List<double>());
            var gpu = segments.ToDictionary(s => s.name, _ => new List<double>());
            var counts = segments.ToDictionary(s => s.name, _ => Counters.Select(__ => new List<long>()).ToArray());
            var roundMedians = segments.ToDictionary(s => s.name, _ => new List<double>());
            var offscreen = segments.ToDictionary(s => s.name, _ => new List<double>());
            var target = new RenderTexture(Screen.width, Screen.height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
                { antiAliasing = stage.view.allowMSAA ? Mathf.Max(1, urp.msaaSampleCount) : 1 };
            var probe = new RenderTexture(1, 1, 0, RenderTextureFormat.ARGB32);
            target.Create();
            probe.Create();
            for (int round = 1; round <= nRounds; round++)
                foreach (var seg in segments)
                {
                    Show(seg);
                    for (int i = 0; i < nWarm; i++)
                        yield return null;
                    var mine = new List<double>(nFrames);
                    for (int f = 0; f < nFrames; f++)
                    {
                        yield return null;
                        FrameTimingManager.CaptureFrameTimings();
                        // (the timings come a few frames late; the warm-up before covers the hand-over between segments)
                        if (FrameTimingManager.GetLatestTimings(1, timing) < 1)
                            continue;
                        var t = timing[0];
                        cpu[seg.name].Add(t.cpuFrameTime);
                        mine.Add(t.cpuFrameTime);
                        main[seg.name].Add(t.cpuMainThreadFrameTime);
                        render[seg.name].Add(t.cpuRenderThreadFrameTime);
                        gpu[seg.name].Add(t.gpuFrameTime);
                        csv.Append(round).Append(',').Append(seg.name).Append(',').Append(f).Append(',')
                            .Append(F(t.cpuFrameTime)).Append(',').Append(F(t.cpuMainThreadFrameTime)).Append(',')
                            .Append(F(t.cpuRenderThreadFrameTime)).Append(',').Append(F(t.gpuFrameTime));
                        for (int c = 0; c < recorders.Length; c++)
                        {
                            long v = recorders[c].Valid ? recorders[c].LastValue : -1;
                            counts[seg.name][c].Add(v);
                            csv.Append(',').Append(v);
                        }
                        csv.Append('\n');
                    }
                    roundMedians[seg.name].Add(Stats(mine).median);
                    // the same view drawn offscreen, back to back, the GPU kept busy: the time a frame's drawing takes,
                    // free of the display's cadence (macOS presents on the screen's refresh even with vsync off, so a
                    // presented frame's period comes in whole refresh ticks, 6.9 ms at 144 Hz)
                    for (int b = 0; b <= offscreenBatches; b++)
                    {
                        var clock = System.Diagnostics.Stopwatch.StartNew();
                        for (int k = 0; k < offscreenPerBatch; k++)
                        {
                            var request = new RenderPipeline.StandardRequest { destination = target };
                            if (RenderPipeline.SupportsRenderRequest(stage.view, request))
                                RenderPipeline.SubmitRenderRequest(stage.view, request);
                            else
                            {
                                stage.view.targetTexture = target;
                                stage.view.Render();
                                stage.view.targetTexture = null;
                            }
                        }
                        Graphics.Blit(target, probe);
                        AsyncGPUReadback.Request(probe).WaitForCompletion();
                        if (b > 0)     // (the first batch only primes)
                            offscreen[seg.name].Add(clock.Elapsed.TotalMilliseconds / offscreenPerBatch);
                        yield return null;
                    }
                    Debug.Log($"[PerfRunner] round {round} {seg.name}: frame {Stats(mine).median:F2} ms");
                }

            var summaries = new List<Segment>();
            foreach (var seg in segments)
            {
                var s = new Segment
                {
                    name = seg.name, view = seg.view.name, light = seg.light.name, birches = seg.birchesOn, frames = cpu[seg.name].Count,
                    cpu_ms = Stats(cpu[seg.name]), cpu_main_ms = Stats(main[seg.name]), cpu_render_ms = Stats(render[seg.name]),
                    gpu_ms = Stats(gpu[seg.name]), round_medians_ms = roundMedians[seg.name].ToArray(),
                    offscreen_ms = Stats(offscreen[seg.name]),
                };
                s.counters = Counters.Select((c, i) => new Counter
                {
                    name = c.column, median = Median(counts[seg.name][i]), max = counts[seg.name][i].Count > 0 ? counts[seg.name][i].Max() : -1,
                }).ToArray();
                summaries.Add(s);
                Debug.Log($"[PerfRunner] {seg.name}: offscreen {s.offscreen_ms.median:F2} ms, frame {s.cpu_ms.median:F2} ms, gpu {s.gpu_ms.median:F2} ms, " +
                          $"{s.Count("triangles"):N0} triangles, {s.Count("draws")} draws");
            }
            double measured = wallClock.Elapsed.TotalSeconds;

            // a screenshot of each segment, after the measuring, so writing them disturbs no measured frame
            foreach (var seg in segments)
            {
                Show(seg);
                for (int i = 0; i < 10; i++)
                    yield return null;
                ScreenCapture.CaptureScreenshot(Path.Combine(outDir, seg.name.Replace('@', '-') + ".png"));
                yield return null;
                yield return null;
            }

            foreach (var r in recorders)
                r.Dispose();
            target.Release();
            probe.Release();
            foreach (var b in birches ?? new GameObject[0])
                if (b != null)
                    b.SetActive(true);

            var run = new Run
            {
                label = label,
                started = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture),
                seconds = measured,
                unity = Application.unityVersion,
                device = SystemInfo.deviceModel, gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(),
                screen = $"{Screen.width}x{Screen.height}", fullscreen = Screen.fullScreenMode.ToString(),
                msaa = urp.msaaSampleCount, renderScale = urp.renderScale, quality = QualitySettings.names[QualitySettings.GetQualityLevel()],
                vsync = QualitySettings.vSyncCount, frameTimingStats = FrameTimingManager.IsFeatureEnabled(),
                warmUp = nWarm, framesPerSegment = nFrames, rounds = nRounds, settle = nSettle,
                segments = summaries.ToArray(),
            };
            File.WriteAllText(Path.Combine(outDir, "frames.csv"), csv.ToString());
            File.WriteAllText(Path.Combine(outDir, "summary.json"), JsonUtility.ToJson(run, true));
            File.WriteAllText(Path.Combine(outDir, "summary.md"), Table(run));
            Debug.Log($"[PerfRunner] done: {summaries.Count} segments in {run.seconds:F0} s -> {outDir}");
            Application.Quit(0);
        }

        static string F(double v) => v.ToString("F3", CultureInfo.InvariantCulture);

        static long Median(List<long> v)
        {
            if (v.Count == 0)
                return -1;
            var s = v.OrderBy(x => x).ToList();
            return s[s.Count / 2];
        }

        static Stat Stats(List<double> v)
        {
            if (v.Count == 0)
                return new Stat();
            var s = v.OrderBy(x => x).ToArray();
            double Q(double q) => s[Mathf.Clamp((int)System.Math.Ceiling(q * s.Length) - 1, 0, s.Length - 1)];
            return new Stat { median = Q(0.5), p95 = Q(0.95), p99 = Q(0.99), max = s[s.Length - 1], mean = s.Average() };
        }

        static string Table(Run run)
        {
            var sb = new StringBuilder();
            sb.Append($"# Frame time: the corner{(run.label != "" ? ", " + run.label : "")}\n\n");
            sb.Append($"{run.started}, {run.gpu} ({run.api}), {run.screen} {run.fullscreen}, MSAA {run.msaa}x, render scale {run.renderScale}, ");
            sb.Append($"quality {run.quality}, vsync {run.vsync}; {run.rounds} rounds of {run.framesPerSegment} frames a segment, each after ");
            sb.Append($"{run.warmUp} warm-up, after {run.settle} frames to settle; {run.seconds:F0} s measuring.\n\n");
            sb.Append("Milliseconds, median / 95th percentile. Offscreen: the view drawn into a 2560 by 1440 target (the ");
            sb.Append("game's MSAA) back to back with the GPU kept busy, wall time a frame: the cost of drawing it, the steadiest ");
            sb.Append("number, used for A/B. Frame: the presented frame's period (FrameTimingManager's CPU frame time, which ");
            sb.Append("includes waiting for the GPU and the screen; macOS presents on the display's refresh even with vsync off, ");
            sb.Append("so it comes in whole ticks, 6.9 ms at 144 Hz; 16.7 ms is 60 fps). GPU: the GPU's own time per presented ");
            sb.Append("frame, which on Apple's tile GPUs overlaps frames and can exceed the period. Triangles, draws, SetPass ");
            sb.Append("calls and shadow casters: the median frame, every pass (shadows included). Memory: total used.\n\n");
            sb.Append("| Segment | Offscreen | Frame | GPU | Main thread | Render thread | Triangles | Draws | SetPass | Shadow casters | Memory (MB) |\n");
            sb.Append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n");
            foreach (var s in run.segments)
                sb.Append($"| {s.name} | {s.offscreen_ms.median:F1} / {s.offscreen_ms.p95:F1} | {s.cpu_ms.median:F1} / {s.cpu_ms.p95:F1} | " +
                          $"{s.gpu_ms.median:F1} / {s.gpu_ms.p95:F1} | {s.cpu_main_ms.median:F2} | {s.cpu_render_ms.median:F2} | " +
                          $"{s.Count("triangles"):N0} | {s.Count("draws")} | {s.Count("setpass")} | {s.Count("shadow_casters")} | " +
                          $"{s.Count("mem_total_used") / 1048576.0:F0} |\n");
            return sb.ToString();
        }

        [System.Serializable]
        public class Stat
        {
            public double median, p95, p99, max, mean;
        }

        [System.Serializable]
        public class Counter
        {
            public string name;
            public long median, max;
        }

        [System.Serializable]
        public class Segment
        {
            public string name, view, light;
            public bool birches;
            public int frames;
            public Stat cpu_ms, cpu_main_ms, cpu_render_ms, gpu_ms;
            public double[] round_medians_ms;
            public Stat offscreen_ms;
            public Counter[] counters;

            public long Count(string counter)
            {
                foreach (var c in counters)
                    if (c.name == counter)
                        return c.median;
                return -1;
            }
        }

        [System.Serializable]
        public class Run
        {
            public string label, started, unity, device, gpu, api, screen, fullscreen, quality;
            public double seconds;
            public int msaa, vsync, warmUp, framesPerSegment, rounds, settle;
            public float renderScale;
            public bool frameTimingStats;
            public Segment[] segments;
        }
    }
}
