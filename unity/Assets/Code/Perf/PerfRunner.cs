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
    ///
    /// The pass study (docs/measuring.md, The pass budget): -perf-passes &lt;config,...&gt; measures each segment once per
    /// configuration of the pipeline's passes ('all'; '-&lt;pass&gt;', every pass but that one; '-fullscreen', the four
    /// full-screen passes off; 'bare', every pass off), and -perf-scenes empty,corner adds the scene with every renderer
    /// hidden but the air's motes, so the sky, the lights and post are drawn alone (-perf-empty-views, the views it is
    /// measured from). -perf-views &lt;name,...&gt; keeps only those views; -perf-shots some keeps a screenshot of every
    /// configuration at the first view only, and of 'all' at every view. 'flat' is 'bare' with every renderer drawn
    /// in an unlit material. -perf-offscreen-scale 0.5 draws the offscreen
    /// frames at half the width and height, to tell the pixels' cost from the vertices'.
    ///
    /// Two arms leave every pass on and set a shader keyword everywhere (step 3, history pages): 'history-off'
    /// (OS_HISTORY_OFF, every history layer its material's quiet mean, no page read) and 'haze-off' (OS_HAZE_OFF, the
    /// air's OS_Atmosphere skipped). -perf-scenes quad-rgba8,quad-bc7 adds the history quad (LT1History): every renderer
    /// hidden but the motes and a full-screen grid of 4,096 pieces reading three synthetic pages through
    /// Shaders/History.hlsl, RGBA8 or BC7, measured from the empty scene's views in 'all' and 'history-off' only.
    /// Options may follow the format (R2b, the page sample's cost: quad-bc7-half, quad-rgba8-two, quad-bc7-tile4): 'half'
    /// draws that scene's offscreen frames at half the width and height (a quarter of the pixels, every vertex), 'two'
    /// reads P0 and H1 only (the quad's OS_QUAD_TWO_PAGES), 'tile&lt;k&gt;' draws the quad whose charts' UVs span k times
    /// their texels (historyQuadTiled), so the pages are sampled minified, trilinear, with their mips.
    ///
    /// The scale test (docs/research/scale-test.md): -district &lt;dir&gt; loads the district's chunk cache (DistrictLoader),
    /// times it and the rebuild benchmarks (DistrictBench) into the summary, and -perf-scenes district-near,district-l0,
    /// district-shells measures it from its own views (district.json; -perf-district-views keeps some) in each arm, with
    /// the corner hidden and the district in its real colours.
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

        [Header("The pass study")]
        [Tooltip("The renderer whose features the pass study turns off one at a time (PC_Renderer).")]
        public UniversalRendererData rendererData;
        [Tooltip("An unlit material: the 'flat' configuration draws the bare corner with it, to tell the shading's cost from the rasterising's.")]
        public Material flat;
        [Tooltip("The views the empty scene is measured from: nothing is in it but the sky, so one or two will do.")]
        public string[] emptyViews = { "street", "high" };

        [Header("The history quad (step 3)")]
        [Tooltip("The full-screen grid of pieces reading the history pages (LT1History.AddQuad): drawn only in the quad scenes.")]
        public MeshRenderer historyQuad;
        [Tooltip("The quad's pages, RGBA8 and BC7: the quad scene binds its own.")]
        public HistoryPages pagesRGBA8, pagesBC7;
        [Tooltip("The quad's minified meshes (LT1History.QuadMesh(k)), each chart's UVs spanning k times its texels, k in historyQuadTiles: a scene quad-<format>-tile<k> draws its own.")]
        public Mesh[] historyQuadTiled;
        public int[] historyQuadTiles;

        [Header("The scale test")]
        [Tooltip("The district's loader: given -district <dir>, it loads the chunk cache there before anything is measured.")]
        public DistrictLoader district;

        /// <summary>
        /// The passes the study turns off, by name: the sky (the camera clears to a colour instead), the sun's shadow map,
        /// the renderer's screen-space and full-screen features, post-processing (grade, bloom, grain, vignette, dither),
        /// MSAA 4x, the air's motes, and the opaque and depth textures the pipeline copies after the opaque scene.
        /// </summary>
        static readonly string[] PassNames = { "sky", "shadows", "ssao", "ssr", "beams", "foglights", "keyblock", "palette", "post", "msaa", "motes", "opaquetex", "depthtex" };
        static readonly Dictionary<string, string> FeatureOf = new Dictionary<string, string>
        {
            ["ssao"] = "ScreenSpaceAmbientOcclusion", ["ssr"] = "ScreenSpaceReflection", ["beams"] = "SunBeams",
            ["foglights"] = "FogLights", ["keyblock"] = "KeyBlock", ["palette"] = "Palette",
        };
        static readonly string[] FullScreen = { "beams", "foglights", "keyblock", "palette" };

        /// <summary>Whether a quad scene (quad-&lt;format&gt;[-option...]) has the option.</summary>
        static bool QuadOption(string scene, string option) =>
            scene.StartsWith("quad-") && scene.Split('-').Skip(2).Contains(option);

        /// <summary>A quad scene's tiling (its 'tile&lt;k&gt;' option), 1 without one.</summary>
        static int QuadTile(string scene)
        {
            if (scene.StartsWith("quad-"))
                foreach (var o in scene.Split('-').Skip(2))
                    if (o.StartsWith("tile") && int.TryParse(o.Substring(4), NumberStyles.Integer, CultureInfo.InvariantCulture, out int k))
                        return k;
            return 1;
        }

        /// <summary>Whether a configuration turns a pass off.</summary>
        static bool Off(string config, string pass) =>
            config == "bare" || config == "flat" || config == "-" + pass || (config == "-fullscreen" && System.Array.IndexOf(FullScreen, pass) >= 0);

        struct Seg
        {
            public string name, scene, passes;
            public View view;
            public Moment light;
            public bool birchesOn;
        }

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

            // the scale test's district, loaded and timed before anything is drawn, and the rebuild benchmarks on its
            // largest chunk
            string districtDir = Arg("-district", null);
            DistrictLoader.Report loaded = null;
            DistrictBench.Report bench = null;
            var districtViews = new View[0];
            if (districtDir != null && district != null)
            {
                loaded = district.Load(districtDir);
                districtViews = district.views.Select(DistrictLoader.ToRunner).ToArray();
                string largest = Directory.GetFiles(Path.Combine(districtDir, "chunks"), "c_*.bin").OrderByDescending(f => new FileInfo(f).Length).First();
                bench = DistrictBench.Run(largest);
                yield return null;
            }

            // the segments: each view in each light, per scene and configuration of the passes (the corner with every
            // pass on alone unless asked), and the corner again without its birches in the A/B lights
            string[] configs = Arg("-perf-passes", "all").Split(',');
            string[] sceneNames = Arg("-perf-scenes", "corner").Split(',');
            string[] keepViews = Arg("-perf-views", null)?.Split(',');
            string[] emptyAt = Arg("-perf-empty-views", string.Join(",", emptyViews)).Split(',');
            string[] districtAt = Arg("-perf-district-views", null)?.Split(',');
            var segments = new List<Seg>();
            foreach (var l in moments)
                foreach (var scene in sceneNames)
                    foreach (var config in configs)
                    {
                        // (the motes are drawn only where the light has them)
                        if (config == "-motes" && (l.rig == null || l.rig.motes <= 0f))
                            continue;
                        string prefix = scene == "corner" ? "" : scene + "-";
                        string suffix = config == "all" ? "" : "/" + config;
                        bool inDistrict = scene.StartsWith("district");
                        bool quad = scene.StartsWith("quad-");
                        if (quad && config != "all" && config != "history-off")
                            continue;
                        foreach (var v in inDistrict ? districtViews : views)
                        {
                            if (scene == "empty" || quad ? System.Array.IndexOf(emptyAt, v.name) < 0
                                : inDistrict ? districtAt != null && System.Array.IndexOf(districtAt, v.name) < 0
                                : keepViews != null && System.Array.IndexOf(keepViews, v.name) < 0)
                                continue;
                            segments.Add(new Seg { name = $"{prefix}{v.name}@{l.name}{suffix}", scene = scene, passes = config, view = v, light = l, birchesOn = true });
                        }
                        if (scene == "corner" && config == "all" && withoutBirchesIn != null && System.Array.IndexOf(withoutBirchesIn, l.name) >= 0 && birches != null && birches.Length > 0)
                            foreach (var v in views)
                                if (keepViews == null || System.Array.IndexOf(keepViews, v.name) >= 0)
                                    segments.Add(new Seg { name = $"{v.name}@{l.name}-nobirch", scene = scene, passes = config, view = v, light = l, birchesOn = false });
                    }
            if (only != null)
                segments = segments.Where(s => only.Split(',').Any(o => s.name.StartsWith(o))).ToList();
            string shots = Arg("-perf-shots", "all");

            // what the pass study turns off, as the scene has it, so each segment starts from the same pipeline
            var camData = stage.view.GetUniversalAdditionalCameraData();
            var clear0 = stage.view.clearFlags;
            bool post0 = camData.renderPostProcessing;
            var colour0 = camData.requiresColorOption;
            var depth0 = camData.requiresDepthOption;
            int msaa0 = urp.msaaSampleCount;
            var features = rendererData != null
                ? rendererData.rendererFeatures.Where(f => f != null).ToDictionary(f => f.name, f => (feature: f, on: f.isActive))
                : new Dictionary<string, (ScriptableRendererFeature feature, bool on)>();
            foreach (var pass in FeatureOf)
                if (configs.Any(c => Off(c, pass.Key)) && !features.ContainsKey(pass.Value))
                    Debug.LogWarning($"[PerfRunner] no renderer feature '{pass.Value}' to turn off for '{pass.Key}'");
            var motes = stage.motes != null ? stage.motes.GetComponent<MeshRenderer>() : null;
            // every renderer the corner draws but the motes, with whether it is drawn (the empty scene and the district
            // hide them all)
            var districts = district != null ? district.Renderers() : new HashSet<Renderer>();
            var drawn = FindObjectsByType<Renderer>(FindObjectsInactive.Include, FindObjectsSortMode.None)
                .Where(r => r != motes && r != historyQuad && !districts.Contains(r)).ToArray();
            var drawnOn = drawn.Select(r => r.enabled).ToArray();
            var drawnWith = drawn.Select(r => r.sharedMaterials).ToArray();
            var targets = new Dictionary<(int, float), RenderTexture>();
            // (-perf-offscreen-scale 0.5 draws the offscreen frames at half the width and height: a quarter of the
            // pixels and every vertex, so what scales with it is the pixels' cost; a quad scene's 'half' option does
            // the same for that scene alone)
            float offScale = float.Parse(Arg("-perf-offscreen-scale", "1"), CultureInfo.InvariantCulture);
            float ScaleOf(Seg s) => offScale * (QuadOption(s.scene, "half") ? 0.5f : 1f);
            RenderTexture Target(int samples, float scale)
            {
                if (!targets.TryGetValue((samples, scale), out var t))
                {
                    t = new RenderTexture(Mathf.RoundToInt(Screen.width * scale), Mathf.RoundToInt(Screen.height * scale), 24,
                                          RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = samples };
                    t.Create();
                    targets[(samples, scale)] = t;
                }
                return t;
            }
            // the quad's own mesh and its two-page keyword (R2b: a scene's 'tile<k>' and 'two' options)
            var quadFilter = historyQuad != null ? historyQuad.GetComponent<MeshFilter>() : null;
            var quadMesh = quadFilter != null ? quadFilter.sharedMesh : null;
            var twoPages = historyQuad != null ? new LocalKeyword(historyQuad.sharedMaterial.shader, "OS_QUAD_TWO_PAGES") : default;
            foreach (var scene in sceneNames.Where(s => s.StartsWith("quad-")))
            {
                int k = QuadTile(scene);
                if (k != 1 && (historyQuadTiles == null || System.Array.IndexOf(historyQuadTiles, k) < 0))
                    Debug.LogError($"[PerfRunner] no quad tiled x{k} for '{scene}': it draws the untiled quad");
            }

            // the arms that set a keyword for every shader (Shaders/History.hlsl; StreetSurface.hlsl's OS_Atmosphere;
            // made here: Unity allows no keyword in a MonoBehaviour's initializers)
            var historyOff = GlobalKeyword.Create("OS_HISTORY_OFF");
            var hazeOff = GlobalKeyword.Create("OS_HAZE_OFF");

            void SetPasses(string config)
            {
                foreach (var pass in FeatureOf)
                    if (features.TryGetValue(pass.Value, out var f))
                        f.feature.SetActive(f.on && !Off(config, pass.Key));
                stage.view.clearFlags = Off(config, "sky") ? CameraClearFlags.SolidColor : clear0;
                if (Off(config, "shadows") && stage.sun != null)
                    stage.sun.shadows = LightShadows.None;     // (the stage sets them soft again on the next Apply)
                camData.renderPostProcessing = post0 && !Off(config, "post");
                urp.msaaSampleCount = Off(config, "msaa") ? 1 : msaa0;
                if (motes != null && Off(config, "motes"))
                    motes.enabled = false;                       // (the stage's motes set it from the rig on Apply)
                camData.requiresColorOption = Off(config, "opaquetex") ? CameraOverrideOption.Off : colour0;
                camData.requiresDepthOption = Off(config, "depthtex") ? CameraOverrideOption.Off : depth0;
                Shader.SetKeyword(historyOff, config == "history-off");
                Shader.SetKeyword(hazeOff, config == "haze-off");
            }

            var recorders = Counters.Select(c => ProfilerRecorder.StartNew(c.category, c.counter, 1)).ToArray();
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var timing = new FrameTiming[1];
            var csv = new StringBuilder("round,segment,frame,cpu_ms,cpu_main_ms,cpu_render_ms,gpu_ms," + string.Join(",", Counters.Select(c => c.column)) + "\n");
            var wallClock = System.Diagnostics.Stopwatch.StartNew();
            int nRounds = int.Parse(Arg("-perf-rounds", rounds.ToString()), CultureInfo.InvariantCulture);
            int nSettle = int.Parse(Arg("-perf-settle", settle.ToString()), CultureInfo.InvariantCulture);

            void Show(Seg seg)
            {
                foreach (var b in birches ?? new GameObject[0])
                    if (b != null)
                        b.SetActive(seg.birchesOn);
                for (int i = 0; i < drawn.Length; i++)
                    if (drawn[i] != null)
                    {
                        drawn[i].enabled = drawnOn[i] && seg.scene == "corner";
                        drawn[i].sharedMaterials = seg.passes == "flat" && flat != null
                            ? drawnWith[i].Select(_ => flat).ToArray() : drawnWith[i];
                    }
                stage.rig = seg.light.rig;
                shot.position = seg.view.position;
                shot.target = seg.view.target;
                shot.verticalFov = seg.view.fov;
                shot.near = near;
                shot.far = far;
                stage.shot = shot;
                stage.Apply();
                if (district != null)
                    district.Show(seg.scene.StartsWith("district-") ? seg.scene.Substring("district-".Length) : "", StreetSpace.ToUnity(seg.view.position));
                if (seg.scene.StartsWith("district"))
                    Shader.SetGlobalFloat("_OS_Clay", 0f);      // (the district in its colours; the stage sets clay on Apply)
                if (historyQuad != null)
                {
                    historyQuad.enabled = seg.scene.StartsWith("quad-");
                    var pages = seg.scene.StartsWith("quad-bc7") ? pagesBC7 : pagesRGBA8;
                    if (historyQuad.enabled && pages != null)
                        pages.Bind();
                    if (historyQuad.enabled)
                    {
                        int at = historyQuadTiles != null ? System.Array.IndexOf(historyQuadTiles, QuadTile(seg.scene)) : -1;
                        if (quadFilter != null)
                            quadFilter.sharedMesh = at >= 0 && historyQuadTiled[at] != null ? historyQuadTiled[at] : quadMesh;
                        historyQuad.sharedMaterial.SetKeyword(twoPages, QuadOption(seg.scene, "two"));
                    }
                }
                SetPasses(seg.passes);
            }

            // the machine settles after the player starts (the launch, the first pipelines, the system's own work on a
            // new app): the first segment is drawn for a while before anything is kept
            if (district != null)
                district.Show("", Vector3.zero);
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
            var roundOffscreen = segments.ToDictionary(s => s.name, _ => new List<double>());
            var probe = new RenderTexture(1, 1, 0, RenderTextureFormat.ARGB32);
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
                    // presented frame's period comes in whole refresh ticks, 6.9 ms at 144 Hz); the target has the
                    // samples the pipeline draws with
                    var target = Target(stage.view.allowMSAA ? Mathf.Max(1, urp.msaaSampleCount) : 1, ScaleOf(seg));
                    var thisRound = new List<double>(offscreenBatches);
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
                        {
                            offscreen[seg.name].Add(clock.Elapsed.TotalMilliseconds / offscreenPerBatch);
                            thisRound.Add(clock.Elapsed.TotalMilliseconds / offscreenPerBatch);
                        }
                        yield return null;
                    }
                    roundOffscreen[seg.name].Add(Stats(thisRound).median);
                    Debug.Log($"[PerfRunner] round {round} {seg.name}: frame {Stats(mine).median:F2} ms");
                }

            var summaries = new List<Segment>();
            foreach (var seg in segments)
            {
                var s = new Segment
                {
                    name = seg.name, view = seg.view.name, light = seg.light.name, scene = seg.scene, passes = seg.passes,
                    birches = seg.birchesOn, frames = cpu[seg.name].Count,
                    cpu_ms = Stats(cpu[seg.name]), cpu_main_ms = Stats(main[seg.name]), cpu_render_ms = Stats(render[seg.name]),
                    gpu_ms = Stats(gpu[seg.name]), round_medians_ms = roundMedians[seg.name].ToArray(),
                    offscreen_ms = Stats(offscreen[seg.name]), round_offscreen_ms = roundOffscreen[seg.name].ToArray(),
                    offscreen_scale = ScaleOf(seg),
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

            // a screenshot of each segment, after the measuring, so writing them disturbs no measured frame (with
            // -perf-shots some, every configuration at the first view of each scene and 'all' at every view)
            foreach (var seg in segments)
            {
                if (shots == "some" && seg.passes != "all" && seg.view != segments.First(x => x.scene == seg.scene).view)
                    continue;
                Show(seg);
                for (int i = 0; i < 10; i++)
                    yield return null;
                ScreenCapture.CaptureScreenshot(Path.Combine(outDir, seg.name.Replace('@', '-').Replace('/', '_') + ".png"));
                yield return null;
                yield return null;
            }

            foreach (var r in recorders)
                r.Dispose();
            foreach (var t in targets.Values)
                t.Release();
            probe.Release();
            foreach (var b in birches ?? new GameObject[0])
                if (b != null)
                    b.SetActive(true);
            // the pipeline as it was (the renderer's features are an asset, shared with any later run in this process)
            SetPasses("all");
            if (historyQuad != null)
            {
                historyQuad.enabled = false;
                if (quadFilter != null)
                    quadFilter.sharedMesh = quadMesh;
                historyQuad.sharedMaterial.SetKeyword(twoPages, false);
            }
            for (int i = 0; i < drawn.Length; i++)
                if (drawn[i] != null)
                    drawn[i].enabled = drawnOn[i];

            if (loaded != null)
                loaded.footprintEnd = DistrictLoader.Footprint();     // after every segment has drawn it
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
                warmUp = nWarm, framesPerSegment = nFrames, rounds = nRounds, settle = nSettle, offscreenScale = offScale,
                segments = summaries.ToArray(),
                district = loaded, bench = bench,
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
            var d = run.district;
            if (d != null && d.chunks > 0)
                sb.Append($"The district: {d.size:F0} m square, {d.plots:N0} plots in {d.chunks} chunks of {d.chunk:F0} m ({d.meshes} meshes), " +
                          $"{d.fileBytes / 1048576.0:F0} MB on disk, loaded in {d.loadSeconds:F1} s ({d.mbPerSecond:F0} MB/s); a chunk " +
                          $"{d.chunkMs.median:F2} ms (95th {d.chunkMs.p95:F2}, worst {d.chunkMs.max:F2}), a core chunk {d.coreChunkMs.median:F2} ms " +
                          $"(95th {d.coreChunkMs.p95:F2}); triangles: L0 {d.l0Triangles:N0}, shells {d.shellTriangles:N0}, ground {d.groundTriangles:N0}; " +
                          $"resident memory {d.rssBefore / 1048576} MB before, {d.rssAfter / 1048576} MB after; footprint (GPU memory included) " +
                          $"{d.footprintBefore / 1048576} MB before, {d.footprintAfter / 1048576} MB after, {d.footprintEnd / 1048576} MB at the end.\n\n");
            var b = run.bench;
            if (b != null && b.vertices > 0)
                sb.Append($"Rebuilding {b.chunk} ({b.triangles:N0} triangles, {b.vertices:N0} vertices, {b.parts} parts): placed in C# " +
                          $"{b.placeManagedMs.median:F2} ms, as a Burst job {b.placeBurstMs.median:F2} ms (Burst {(b.burst ? "on" : "off")}), uploaded " +
                          $"{b.uploadMs.median:F2} ms. A {b.pageWidth} by {b.pageHeight} history page: drawn {b.pageDrawMs.median:F2} ms, read back " +
                          $"{b.pageReadbackMs.median:F2} ms, compressed to {b.pageFormat} {b.pageCompressMs.median:F1} ms (fast {b.pageCompressFastMs.median:F1} ms).\n\n");
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
            public string name, view, light, scene, passes;
            public bool birches;
            public int frames;
            public Stat cpu_ms, cpu_main_ms, cpu_render_ms, gpu_ms;
            public double[] round_medians_ms;
            public Stat offscreen_ms;
            [Tooltip("Each round's median offscreen time (its batches'), for the spread between rounds.")]
            public double[] round_offscreen_ms;
            [Tooltip("The offscreen frames' size against the screen's (the run's -perf-offscreen-scale, halved by a quad scene's 'half').")]
            public float offscreen_scale;
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
            public float renderScale, offscreenScale;
            public bool frameTimingStats;
            public Segment[] segments;
            public DistrictLoader.Report district;
            public DistrictBench.Report bench;
        }
    }
}
