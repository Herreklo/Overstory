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
    /// memory. Writes a CSV of every frame, a JSON summary per segment (median, 95th and 99th percentile, worst) and a
    /// short markdown table, keeps one screenshot per segment, then quits.
    ///
    /// The scene is the street as its own test stages it (LT1Perf.Compose: Street.unity copied, its houses, views and
    /// lights), and the plan is set there: the views (each house's level and the shadowed distance fitted to it) and each
    /// light as the editor applied it at each view (the sun, the trilight, the background, the sky, its reflection, the
    /// ground, the exposure, and what the town's sky map reads of each renderer). Here a segment only puts those back
    /// and draws the town's sky map again; it decides nothing. The pipeline is the street test's: the renderer's
    /// screen-space occlusion alone, one 4096 shadow cascade.
    ///
    /// Command line: -perf-out &lt;dir&gt; (required; without it the runner does nothing), -perf-frames N (a segment's
    /// frames per round), -perf-warmup N, -perf-rounds N, -perf-settle N, -perf-only &lt;name,...&gt; (segments whose names
    /// start so), -perf-label &lt;text&gt;, -perf-views &lt;name,...&gt; (only those views). Every segment is measured once per
    /// round, the rounds one after another, after the first segment has been drawn for a while to let the machine
    /// settle; screenshots are taken after all measuring (-perf-shots some: every configuration at the first view only,
    /// and 'all' at every view). -perf-offscreen-scale 0.5 draws the offscreen frames at half the width and height, to
    /// tell the pixels' cost from the vertices'.
    ///
    /// The pass study (docs/measuring.md, The pass budget): -perf-passes &lt;config,...&gt; measures each segment once per
    /// configuration ('all'; '-&lt;pass&gt;', every pass but that one, '-a+b' every pass but those; 'bare', every pass
    /// off; 'flat', bare with every renderer in an unlit material), the passes being PassNames. -perf-scenes empty,street
    /// adds the scene with every renderer hidden, so the sky, the lights and post are drawn alone (-perf-empty-views, the
    /// views it is measured from).
    ///
    /// The scale test (docs/research/scale-test.md): -district &lt;dir&gt; loads the district's chunk cache (DistrictLoader),
    /// times it and the rebuild benchmarks (DistrictBench) into the summary, and -perf-scenes district-near,district-l0,
    /// district-shells measures it from its own views (district.json; -perf-district-views keeps some) in each light,
    /// with the street hidden.
    /// </summary>
    public class PerfRunner : MonoBehaviour
    {
        /// <summary>A view, in street metres (x along, y back, z up), with each house's level and its shadowed distance.</summary>
        [System.Serializable]
        public class View
        {
            public string name;
            public Vector3 position;
            public Vector3 target;
            public float fov;
            [Tooltip("Each house's level from this view (near, street or city), in the order of houses.")]
            public string[] levels;
            [Tooltip("The shadowed distance fitted to the view (0: the runner's own).")]
            public float shadowDistance;
        }

        /// <summary>A house's levels: the objects and their names (near, street, city).</summary>
        [System.Serializable]
        public class House
        {
            public string id;
            public GameObject[] levels;
            public string[] names;
        }

        /// <summary>A light as the editor applied it at a view: everything a segment puts back.</summary>
        [System.Serializable]
        public class Lit
        {
            public string light, view;
            public Quaternion sunRotation;
            public Color sunColour;
            public float sunIntensity, sunShadow;
            public Color ambientSky, ambientEquator, ambientGround;
            [Tooltip("The ambient probe's 27 coefficients (red, green, blue, nine each).")]
            public float[] probe;
            public Color background;
            public bool skyOn;
            public Vector4 zenith;
            public Cubemap reflection;
            public Color ground;
            public float exposure;
            [Tooltip("What the town's sky map reads of each of townRenderers: its house's wall and its own top (linear).")]
            public Color[] wall, top;
        }

        [Header("The street (LT1Perf.Compose)")]
        public Camera view;
        public Light sun;
        public Volume volume;
        public GameObject sky;
        public Material skyMaterial, groundMaterial;
        [Tooltip("The town's sky map (null when the street was drawn without the town's light).")]
        public SkyMap town;
        public Renderer[] townRenderers;
        public House[] houses;
        public View[] views;
        public Lit[] lit;
        [Tooltip("The houses, as the street's test built them.")]
        public string houseIds;

        [Header("Timing")]
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
        [Tooltip("The shadowed distance for a view that names none (the district's), and the far plane there.")]
        public float shadowDistance = 120f, districtFar = 9000f;
        [Tooltip("Shaders the scene's components find by name at runtime (SkyMap), held here so the build keeps them.")]
        public Shader[] keep;

        [Header("The pass study")]
        [Tooltip("The renderer whose features the street's pipeline sets and the pass study turns off (PC_Renderer).")]
        public UniversalRendererData rendererData;
        [Tooltip("An unlit material: the 'flat' configuration draws the bare street with it, to tell the shading's cost from the rasterising's.")]
        public Material flat;
        [Tooltip("The views the empty scene is measured from: nothing is in it but the sky, so one or two will do.")]
        public string[] emptyViews = { "street", "high" };

        [Header("The scale test")]
        [Tooltip("The district's loader: given -district <dir>, it loads the chunk cache there before anything is measured.")]
        public DistrictLoader district;

        /// <summary>
        /// The passes the study turns off, by name: the sky the light draws (the camera's flat background stays), the
        /// sun's shadow map, the renderer's screen-space occlusion, post-processing (the tonemapper, the exposure and the
        /// grade), MSAA, the town's light (the sky map's walls and horizon, _OS_SkyMapOn), and the opaque and depth
        /// textures the pipeline copies after the opaque scene.
        /// </summary>
        public static readonly string[] PassNames = { "sky", "shadows", "ssao", "post", "msaa", "townlight", "opaquetex", "depthtex" };

        static bool IsOcclusion(ScriptableRendererFeature f) => f.name.Contains("AmbientOcclusion");

        /// <summary>Whether a configuration turns a pass off ('-a+b' turns off each it names).</summary>
        static bool Off(string config, string pass) =>
            config == "bare" || config == "flat"
            || (config.StartsWith("-") && config.Substring(1).Split('+').Contains(pass));

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        struct Seg
        {
            public string name, scene, passes, light;
            public View view;
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
        }

        /// <summary>A light as applied at a view, or at the light's first view for a view the street has not (the district's).</summary>
        Lit LitFor(string light, string viewName) =>
            lit.FirstOrDefault(l => l.light == light && l.view == viewName) ?? lit.First(l => l.light == light);

        static SphericalHarmonicsL2 Probe(float[] c)
        {
            var sh = new SphericalHarmonicsL2();
            if (c == null || c.Length != 27)
                return sh;
            for (int ch = 0; ch < 3; ch++)
                for (int k = 0; k < 9; k++)
                    sh[ch, k] = c[ch * 9 + k];
            return sh;
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
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            if (!volume.sharedProfile.TryGet(out ColorAdjustments adjust))
                Debug.LogError("[PerfRunner] the street's volume has no colour adjustments: the exposure is left as it is");
            float streetFar = view.farClipPlane;
            var shadows0 = sun.shadows;

            // the scale test's district, loaded and timed before anything is drawn, and the rebuild benchmarks on its
            // largest chunk; its street shader reads the town's growth and water (the street itself reads neither)
            string districtDir = Arg("-district", null);
            DistrictLoader.Report loaded = null;
            DistrictBench.Report bench = null;
            var districtViews = new View[0];
            if (districtDir != null && district != null)
            {
                GrowthPack.Apply();
                WaterPack.Apply();
                Shader.SetGlobalFloat("_OS_NearForce", 0f);
                Shader.SetGlobalFloat("_OS_Clay", 0f);
                loaded = district.Load(districtDir);
                districtViews = district.views.Select(DistrictLoader.ToRunner).ToArray();
                string largest = Directory.GetFiles(Path.Combine(districtDir, "chunks"), "c_*.bin").OrderByDescending(f => new FileInfo(f).Length).First();
                bench = DistrictBench.Run(largest);
                yield return null;
            }

            // the segments: each view in each light, per scene and configuration of the passes (the street with every
            // pass on alone unless asked)
            string[] configs = Arg("-perf-passes", "all").Split(',');
            foreach (var c in configs.Where(c => c.StartsWith("-")))
                foreach (var p in c.Substring(1).Split('+').Where(p => System.Array.IndexOf(PassNames, p) < 0))
                    Debug.LogError($"[PerfRunner] no pass '{p}' to turn off in '{c}' (the passes: {string.Join(", ", PassNames)})");
            foreach (var c in configs.Where(c => c != "all" && c != "bare" && c != "flat" && !c.StartsWith("-")))
                Debug.LogError($"[PerfRunner] no configuration '{c}': it is measured as 'all'");
            string[] sceneNames = Arg("-perf-scenes", "street").Split(',');
            string[] keepViews = Arg("-perf-views", null)?.Split(',');
            string[] emptyAt = Arg("-perf-empty-views", string.Join(",", emptyViews)).Split(',');
            string[] districtAt = Arg("-perf-district-views", null)?.Split(',');
            var lights = lit.Select(l => l.light).Distinct().ToArray();
            var segments = new List<Seg>();
            foreach (var l in lights)
                foreach (var scene in sceneNames)
                    foreach (var config in configs)
                    {
                        string prefix = scene == "street" ? "" : scene + "-";
                        string suffix = config == "all" ? "" : "/" + config;
                        bool inDistrict = scene.StartsWith("district");
                        if (inDistrict && district == null)
                            continue;
                        foreach (var v in inDistrict ? districtViews : views)
                        {
                            if (scene == "empty" ? System.Array.IndexOf(emptyAt, v.name) < 0
                                : inDistrict ? districtAt != null && System.Array.IndexOf(districtAt, v.name) < 0
                                : keepViews != null && System.Array.IndexOf(keepViews, v.name) < 0)
                                continue;
                            segments.Add(new Seg { name = $"{prefix}{v.name}@{l}{suffix}", scene = scene, passes = config, view = v, light = l });
                        }
                    }
            if (only != null)
                segments = segments.Where(s => only.Split(',').Any(o => s.name.StartsWith(o))).ToList();
            string shots = Arg("-perf-shots", "all");

            // the street's pipeline (its test's: the screen-space occlusion alone), and what the pass study turns off, as
            // the scene has it, so each segment starts from the same pipeline
            var features = rendererData != null
                ? rendererData.rendererFeatures.Where(f => f != null).ToList()
                : new List<ScriptableRendererFeature>();
            var featuresWere = features.Select(f => f.isActive).ToList();
            if (configs.Any(c => Off(c, "ssao")) && !features.Any(IsOcclusion))
                Debug.LogWarning("[PerfRunner] no screen-space occlusion feature to turn off for 'ssao'");
            var camData = view.GetUniversalAdditionalCameraData();
            bool post0 = camData.renderPostProcessing;
            var colour0 = camData.requiresColorOption;
            var depth0 = camData.requiresDepthOption;
            int msaa0 = urp.msaaSampleCount;
            var skyR = sky != null ? sky.GetComponent<Renderer>() : null;
            // every renderer the street draws but the sky, with whether it is drawn (the empty scene and the district
            // hide them all)
            var districts = district != null ? district.Renderers() : new HashSet<Renderer>();
            var drawn = FindObjectsByType<Renderer>(FindObjectsInactive.Include)
                .Where(r => r != skyR && !districts.Contains(r)).ToArray();
            var drawnOn = drawn.Select(r => r.enabled).ToArray();
            var drawnWith = drawn.Select(r => r.sharedMaterials).ToArray();
            // what the town's sky map reads of each renderer, per light and view
            var albedo = lit.ToDictionary(l => l, l =>
            {
                var m = new Dictionary<Renderer, (Color wall, Color top)>();
                for (int i = 0; townRenderers != null && i < townRenderers.Length; i++)
                    if (townRenderers[i] != null && l.wall != null && i < l.wall.Length)
                        m[townRenderers[i]] = (l.wall[i], l.top[i]);
                return m;
            });
            var targets = new Dictionary<(int, float), RenderTexture>();
            float offScale = float.Parse(Arg("-perf-offscreen-scale", "1"), CultureInfo.InvariantCulture);
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

            void SetPasses(string config)
            {
                for (int i = 0; i < features.Count; i++)
                    features[i].SetActive(IsOcclusion(features[i]) && !Off(config, "ssao"));
                if (sky != null && Off(config, "sky"))
                    sky.SetActive(false);                       // (the next segment's light sets it again)
                if (Off(config, "shadows"))
                    sun.shadows = LightShadows.None;           // (as is)
                camData.renderPostProcessing = post0 && !Off(config, "post");
                urp.msaaSampleCount = Off(config, "msaa") ? 1 : msaa0;
                if (Off(config, "townlight"))
                    Shader.SetGlobalFloat("_OS_SkyMapOn", 0f); // (the next segment's map binds it again)
                camData.requiresColorOption = Off(config, "opaquetex") ? CameraOverrideOption.Off : colour0;
                camData.requiresDepthOption = Off(config, "depthtex") ? CameraOverrideOption.Off : depth0;
            }

            var recorders = Counters.Select(c => ProfilerRecorder.StartNew(c.category, c.counter, 1)).ToArray();
            var timing = new FrameTiming[1];
            var csv = new StringBuilder("round,segment,frame,cpu_ms,cpu_main_ms,cpu_render_ms,gpu_ms," + string.Join(",", Counters.Select(c => c.column)) + "\n");
            var wallClock = System.Diagnostics.Stopwatch.StartNew();
            int nRounds = int.Parse(Arg("-perf-rounds", rounds.ToString()), CultureInfo.InvariantCulture);
            int nSettle = int.Parse(Arg("-perf-settle", settle.ToString()), CultureInfo.InvariantCulture);

            void Show(Seg seg)
            {
                var v = seg.view;
                bool street = seg.scene == "street";
                var lt = LitFor(seg.light, v.name);
                // each house at its level from this view
                if (v.levels != null)
                    for (int i = 0; i < houses.Length && i < v.levels.Length; i++)
                        for (int k = 0; k < houses[i].levels.Length; k++)
                            if (houses[i].levels[k] != null)
                                houses[i].levels[k].SetActive(houses[i].names[k] == v.levels[i]);
                for (int i = 0; i < drawn.Length; i++)
                    if (drawn[i] != null)
                    {
                        drawn[i].enabled = drawnOn[i] && street;
                        drawn[i].sharedMaterials = seg.passes == "flat" && flat != null
                            ? drawnWith[i].Select(_ => flat).ToArray() : drawnWith[i];
                    }
                view.transform.SetPositionAndRotation(ToUnity(v.position), Quaternion.LookRotation(ToUnity(v.target - v.position), Vector3.up));
                view.fieldOfView = v.fov;
                view.farClipPlane = seg.scene.StartsWith("district") ? districtFar : streetFar;
                urp.shadowCascadeCount = 1;
                urp.mainLightShadowmapResolution = 4096;
                urp.shadowDistance = v.shadowDistance > 0 ? v.shadowDistance : shadowDistance;
                // the light as the editor applied it at this view
                sun.transform.rotation = lt.sunRotation;
                sun.intensity = lt.sunIntensity;
                sun.color = lt.sunColour;
                sun.shadowStrength = lt.sunShadow;
                sun.shadows = shadows0;
                RenderSettings.ambientMode = AmbientMode.Trilight;
                RenderSettings.ambientSkyColor = lt.ambientSky;
                RenderSettings.ambientEquatorColor = lt.ambientEquator;
                RenderSettings.ambientGroundColor = lt.ambientGround;
                RenderSettings.ambientProbe = Probe(lt.probe);
                RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
                RenderSettings.customReflectionTexture = lt.reflection;
                view.backgroundColor = lt.background;
                if (sky != null)
                {
                    sky.SetActive(lt.skyOn);
                    sky.transform.position = view.transform.position;
                }
                if (skyMaterial != null)
                    skyMaterial.SetVector("_SkyZenith", lt.zenith);
                Shader.SetGlobalVector("_OS_StageSky", lt.skyOn ? lt.zenith : Vector4.zero);
                if (groundMaterial != null)
                    groundMaterial.SetColor("_BaseColor", lt.ground);
                if (adjust != null)
                    adjust.postExposure.Override(lt.exposure);
                // the town's map drawn again for what stands and how it is lit now
                if (town != null)
                {
                    var a = albedo[lt];
                    town.albedo = r => a.TryGetValue(r, out var x) ? x : (Color.black, Color.black);
                    town.sun = -sun.transform.forward;
                    town.sunLight = sun.color.linear * sun.intensity;
                    town.sunShadow = lt.sunShadow;
                    town.Build();
                }
                if (district != null)
                    district.Show(seg.scene.StartsWith("district-") ? seg.scene.Substring("district-".Length) : "", ToUnity(v.position));
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
                    var target = Target(view.allowMSAA ? Mathf.Max(1, urp.msaaSampleCount) : 1, offScale);
                    var thisRound = new List<double>(offscreenBatches);
                    for (int b = 0; b <= offscreenBatches; b++)
                    {
                        var clock = System.Diagnostics.Stopwatch.StartNew();
                        for (int k = 0; k < offscreenPerBatch; k++)
                        {
                            var request = new RenderPipeline.StandardRequest { destination = target };
                            if (RenderPipeline.SupportsRenderRequest(view, request))
                                RenderPipeline.SubmitRenderRequest(view, request);
                            else
                            {
                                view.targetTexture = target;
                                view.Render();
                                view.targetTexture = null;
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
                    name = seg.name, view = seg.view.name, light = seg.light, scene = seg.scene, passes = seg.passes,
                    frames = cpu[seg.name].Count,
                    cpu_ms = Stats(cpu[seg.name]), cpu_main_ms = Stats(main[seg.name]), cpu_render_ms = Stats(render[seg.name]),
                    gpu_ms = Stats(gpu[seg.name]), round_medians_ms = roundMedians[seg.name].ToArray(),
                    offscreen_ms = Stats(offscreen[seg.name]), round_offscreen_ms = roundOffscreen[seg.name].ToArray(),
                    offscreen_scale = offScale,
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
            // the pipeline as it was (the renderer's features are an asset, shared with any later run in this process)
            SetPasses("all");
            for (int i = 0; i < features.Count; i++)
                features[i].SetActive(featuresWere[i]);
            for (int i = 0; i < drawn.Length; i++)
                if (drawn[i] != null)
                {
                    drawn[i].enabled = drawnOn[i];
                    drawn[i].sharedMaterials = drawnWith[i];
                }

            if (loaded != null)
                loaded.footprintEnd = DistrictLoader.Footprint();     // after every segment has drawn it
            var run = new Run
            {
                label = label, scene = "street", houses = houseIds,
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
            sb.Append($"# Frame time: the street (house{(run.houses != null && run.houses.Contains(",") ? "s" : "")} {run.houses}){(run.label != "" ? ", " + run.label : "")}\n\n");
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
            public int frames;
            public Stat cpu_ms, cpu_main_ms, cpu_render_ms, gpu_ms;
            public double[] round_medians_ms;
            public Stat offscreen_ms;
            [Tooltip("Each round's median offscreen time (its batches'), for the spread between rounds.")]
            public double[] round_offscreen_ms;
            [Tooltip("The offscreen frames' size against the screen's (the run's -perf-offscreen-scale).")]
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
            [Tooltip("The scene the build holds: the street.")]
            public string scene;
            [Tooltip("The street's houses, as its test built them.")]
            public string houses;
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
