using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The street test (blender/parts/street): a house of Harbour Row whole, from its record, in the painted finish
    /// (way P, clay; way Pc, its values in colour), rendered from four views in two lights:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Street.Run -streetHouse 107
    ///         -streetRound s01 [-streetViews eye,street] [-streetWays P,Pc]
    ///
    /// Reads what run/render.sh copied into Generated/&lt;house&gt;/ (the house's two levels, its page and house.json),
    /// builds Street.unity and writes each still, 2,560 by 1,440 with the PC pipeline's 4 samples a pixel and nothing
    /// more, into cache/street/renders/&lt;round&gt;/. Positions are the house's own metres (x along its street front from
    /// its left corner, y back from the building line, z up), as Blender built it. The lights, the shader and the
    /// capture are the finishing test's (LT1Finish), so a house is judged beside the corner on the same terms.
    /// </summary>
    public static class LT1Street
    {
        const string Dir = "Assets/Experiments/LT1/Street";
        const int Width = 2560, Height = 1440, Msaa = 4, WarmUp = 3;

        [Serializable] class PMat { public string name; public int painted; public float L, bareL, underL, stainDL, smooth, stainSmooth, brushL, flatUp, stainEdge, ao, shadowLift; }
        [Serializable] class PLight { public string light; public float exposure, elevation, sun, shadow, sky, equator, ground; public float[] azimuth; }
        [Serializable] class PColMat { public string name; public float[] tint, bareTint, underTint, stainTint; }
        [Serializable] class PColLight { public string light; public float[] sun, sky, equator, ground, background, floor; }
        [Serializable] class PColour { public PColMat[] mats; public PColLight[] lights; public float[] washTint; }
        [Serializable] class Paint { public PMat[] mats; public PLight[] lights; public PColour colour; public float strokeScale, edgeAmp, rimL, rimW, rimFar, bareShift, washL, bareWash, brushFar, dragL, dragScale, dlRange, aoStrength, lapDark, lapCore, lapReach, lapGrimeL, lapGrimeReach, lapGrimeBreak, lapPage; public float[] strokeFade, brushFade, rimBreak, washFade; }
        [Serializable] class Lap { public float reach, step; }
        [Serializable] class Plot { public float w, d; }
        [Serializable] class Page { public int size; public float pxPerM; }
        [Serializable] class GlassKind { public string name, shape; public float tiltDeg; public float[] perM; }
        [Serializable] class Glass { public float gloss; public float[] walls, ceiling, floor, furniture, curtain, room, curtains, daylight; public GlassKind[] kinds; }
        [Serializable] class House { public int house; public float[] size; public Lap lap; public float planeShadow, seenWithinM, cityFromM; public Plot plot; public Page page; public Glass glass; }

        struct View { public string name, level; public Vector3 pos, target; public float fov; public bool floor; }

        // in the house's frame, from its size: eye level 4 m off its front, the street stop at 20 m, raised to 12 m, high
        static View[] Views(float w, float d) => new[]
        {
            new View { name = "eye", level = "near", pos = new Vector3(w / 2 - 2.6f, -4.4f, 1.6f), target = new Vector3(w / 2 - 0.4f, 0.3f, 2.1f), fov = 52 },
            new View { name = "street", level = "street", pos = new Vector3(w / 2 - 9.0f, -19.0f, 1.6f), target = new Vector3(w / 2, 1.0f, 3.0f), fov = 38 },
            new View { name = "raised", level = "street", pos = new Vector3(-7.0f, -12.0f, 12.0f), target = new Vector3(w / 2, d / 2, 2.5f), fov = 42 },
            new View { name = "high", level = "street", pos = new Vector3(-18.0f, -34.0f, 30.0f), target = new Vector3(w / 2, d / 2, 2.0f), fov = 30 },
            new View { name = "back", level = "near", pos = new Vector3(w + 7.0f, d + 11.0f, 2.2f), target = new Vector3(w / 2, d, 2.6f), fov = 44 },
            new View { name = "gable", level = "near", pos = new Vector3(-9.0f, d / 2 - 3.0f, 1.8f), target = new Vector3(0, d / 2, 3.0f), fov = 50 },
            // where the city level takes over (house.json cityFromM) and beyond: down the street at 60 and 120 m, and from
            // a roof 80 m off
            new View { name = "far", level = "city", pos = new Vector3(w / 2 - 22.0f, -56.0f, 1.6f), target = new Vector3(w / 2, 1.0f, 3.5f), fov = 38 },
            new View { name = "farther", level = "city", pos = new Vector3(w / 2 - 44.0f, -112.0f, 1.6f), target = new Vector3(w / 2, 1.0f, 3.5f), fov = 38 },
            new View { name = "farhigh", level = "city", pos = new Vector3(-40.0f, -64.0f, 26.0f), target = new Vector3(w / 2, d / 2, 3.0f), fov = 38 },
            // the floor's own cameras (LT1Finish at p3) on the same corner of the same house, in its own lights
            new View { name = "p3eye", level = "near", pos = new Vector3(-1.0f, -2.9f, 1.6f), target = new Vector3(0.95f, 0.25f, 1.75f), fov = 42, floor = true },
            new View { name = "p3street", level = "street", pos = new Vector3(-8.5f, -18.0f, 1.6f), target = new Vector3(0.9f, 0.3f, 1.9f), fov = 42, floor = true },
        };

        struct Lighting { public string name; public Vector2 azimuth; public float elevation, sun, shadow, sky, equator, ground, exposure; }

        // the finishing test's two lights (LT1Finish), where way P's plan names none of its own
        static readonly Lighting[] Lights =
        {
            new Lighting { name = "overcast", azimuth = new Vector2(-0.5f, -1f), elevation = 65, sun = 0.45f, shadow = 0.7f, sky = 0.95f, equator = 0.72f, ground = 0.14f, exposure = 1.6f },
            new Lighting { name = "lowsun", azimuth = new Vector2(0.906f, -0.423f), elevation = 18, sun = 2.6f, shadow = 1f, sky = 0.32f, equator = 0.24f, ground = 0.1f, exposure = 0.5f },
        };

        const float GroundL = 42, GroundSmooth = 0.1f;

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        public static void Run()
        {
            string id = Arg("-streetHouse") ?? "107";
            string round = Arg("-streetRound") ?? "s01";
            var only = (Arg("-streetViews") ?? "eye,street,raised,high").Split(',');
            var ways = (Arg("-streetWays") ?? "P,Pc").Split(',');
            var lights = (Arg("-streetLights") ?? "overcast,lowsun").Split(',');
            // the low sun for one house alone: turned to strike its front this many degrees off square, so the relief
            // shows (the street's own light is the light step's); the floor's cameras keep the floor's sun
            float sunOff = float.Parse(Arg("-streetSunOff") ?? "45", System.Globalization.CultureInfo.InvariantCulture);
            // every view at one level, for an A/B of two levels at the same view
            string levelAll = Arg("-streetLevel");
            string gen = $"{Dir}/Generated/{id}";
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outDir = Path.Combine(root, "cache", "street", "renders", round);
            Directory.CreateDirectory(outDir);

            Import(gen);
            foreach (var guid in AssetDatabase.FindAssets("t:Material t:VolumeProfile", new[] { gen }))
                AssetDatabase.DeleteAsset(AssetDatabase.GUIDToAssetPath(guid));
            var house = JsonUtility.FromJson<House>(File.ReadAllText(Path.Combine(gen, "house.json")));
            var paint = JsonUtility.FromJson<Paint>(File.ReadAllText(Path.Combine(gen, "paint.json")));
            // an A/B of the planes' microshadow without touching the house's data
            if (Arg("-streetPlaneShadow") != null)
                house.planeShadow = float.Parse(Arg("-streetPlaneShadow"), System.Globalization.CultureInfo.InvariantCulture);
            // and of the planes' flattening, without a new paint
            if (Arg("-streetRoofFlatUp") != null)
                foreach (var m in paint.mats)
                    if (m.name == "roof")
                        m.flatUp = float.Parse(Arg("-streetRoofFlatUp"), System.Globalization.CultureInfo.InvariantCulture);
            var mats = Materials(gen, paint, house);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var root_ = new GameObject($"House {id}");
            var levels = new Dictionary<string, GameObject>();
            foreach (var level in Levels)
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{gen}/house-{level}.fbx");
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                go.transform.SetParent(root_.transform, false);
                levels[level] = go;
            }
            Orient(root_, levels["near"]);
            // the house's shadows cast two-sided (-streetShadowTwo 0 keeps them one-sided, for an A/B): one-sided, the
            // sun's normal bias opens the joints between faces turned different ways, and the sun shows through them in
            // lines on the ground (108, c02)
            if (Arg("-streetShadowTwo") != "0")
                foreach (var r in root_.GetComponentsInChildren<MeshRenderer>(true))
                    r.shadowCastingMode = ShadowCastingMode.TwoSided;
            // the city level as one draw (-streetCityOne 0 keeps a material a piece, for an A/B)
            if (Arg("-streetCityOne") != "0")
                levels["city"] = OneMesh(levels["city"], paint, gen);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(8, 1, 8);
            ground.transform.position = ToUnity(new Vector3(house.size[0] / 2, -10, 0));
            var gm = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            float gy = LToY(GroundL);
            gm.SetFloat("_Smoothness", GroundSmooth);
            AssetDatabase.CreateAsset(gm, $"{gen}/mat-ground.mat");
            ground.GetComponent<Renderer>().sharedMaterial = gm;

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            sunGo.AddComponent<UniversalAdditionalLightData>().softShadowQuality = SoftShadowQuality.Low;
            sun.shadowBias = 1f;
            sun.shadowNormalBias = 1f;

            var volume = new GameObject("Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.Add<Tonemapping>(true).mode.Override(TonemappingMode.Neutral);
            var adjust = profile.Add<ColorAdjustments>(true);
            AssetDatabase.CreateAsset(profile, $"{gen}/street-volume.asset");
            volume.sharedProfile = profile;

            var camGo = new GameObject("Camera");
            var cam = camGo.AddComponent<Camera>();
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 500f;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, $"{Dir}/Street.unity");
            AssetDatabase.SaveAssets();

            // the clay test keeps only the renderer's screen-space occlusion and one sharp cascade fitted to each
            // view, and puts the rest back after
            var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
            var was = rd.rendererFeatures.ToDictionary(f => f, f => f.isActive);
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution, urp.useSRPBatcher);
            try
            {
                if (Arg("-streetSrpBatcher") == "0")
                    urp.useSRPBatcher = false;
                foreach (var f in rd.rendererFeatures)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                foreach (var light in Lights.Where(l => lights.Contains(l.name)))
                foreach (var view0 in Views(house.size[0], house.size[1]).Where(v => only.Contains(v.name)))
                {
                    var view = view0;
                    if (levelAll != null)
                        view.level = levelAll;
                    foreach (var kv in levels)
                        kv.Value.SetActive(kv.Key == view.level);
                    cam.transform.SetPositionAndRotation(ToUnity(view.pos), Quaternion.LookRotation(ToUnity(view.target - view.pos), Vector3.up));
                    cam.fieldOfView = view.fov;
                    urp.shadowCascadeCount = 1;
                    urp.mainLightShadowmapResolution = 4096;
                    urp.shadowDistance = (view.target - view.pos).magnitude + 8f;
                    foreach (var way in ways)
                    {
                        var own = paint.lights?.FirstOrDefault(e => e.light == light.name);
                        var col = way == "Pc" ? paint.colour?.lights?.FirstOrDefault(e => e.light == light.name) : null;
                        var l = own != null ? Own(light, own) : light;
                        if (!view.floor && l.name == "lowsun")
                            l.azimuth = new Vector2(Mathf.Sin(sunOff * Mathf.Deg2Rad), -Mathf.Cos(sunOff * Mathf.Deg2Rad));
                        Light(sun, l, col);
                        cam.backgroundColor = Lin(Back.linear.r, col?.background);
                        gm.SetColor("_BaseColor", Lin(gy, col?.floor));
                        adjust.postExposure.Override(own != null ? own.exposure : light.exposure);
                        Assign(levels[view.level], mats, way, MatLevel(view.level));
                        string file = Path.Combine(outDir, $"{id}-{view.name}-{light.name}-{way}.png");
                        Capture(cam, file);
                        Debug.Log($"[LT1Street] {file}");
                    }
                }
                if (Arg("-streetTiming") != null)
                    Timing(int.Parse(Arg("-streetTiming")), root_, mats, cam, sun, gm, adjust, house, paint, outDir, sunOff);
                SrpBatcher(mats.Values.First().shader);
            }
            finally
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution, urp.useSRPBatcher) = urpWas;
            }
            foreach (var kv in levels)
                Debug.Log($"[LT1Street] {kv.Key}: {kv.Value.GetComponentsInChildren<MeshFilter>(true).Sum(f => f.sharedMesh.triangles.Length / 3)} triangles in Unity");
        }

        /// <summary>
        /// The cost of a street of such houses, offscreen: `n` copies of the house side by side on their plots, each
        /// drawn at the level its distance from the camera takes (the near level within house.json seenWithinM, the city
        /// level from cityFromM), in
        /// way Pc and the low sun, drawn into a 2560 by 1440 target with MSAA 4x back to back, six batches of six after
        /// one that primes (as LT1LightTime). The copies share one page, so texture memory is counted per house, not
        /// measured. The editor's own work is in the numbers: an offscreen frame, not the player's.
        /// </summary>
        static void Timing(int n, GameObject house0, Dictionary<string, Material> mats, Camera cam, Light sun, Material gm,
                           ColorAdjustments adjust, House house, Paint paint, string outDir, float sunOff)
        {
            const int Batches = 6, PerBatch = 6;
            float plot = house.plot != null && house.plot.w > 0 ? house.plot.w / 1000f : house.size[0] + 1f;
            float within = house.seenWithinM > 0 ? house.seenWithinM : 10f;
            float cityFrom = house.cityFromM > 0 ? house.cityFromM : float.MaxValue;
            // a house too far for its shadow (about a ridge's 9 m over the sun's rise) to reach the shadowed distance
            // casts none: d12, the same pixels as casting (-streetFarShadow cast, for an A/B)
            bool drop = Arg("-streetFarShadow") != "cast";
            var houses = new List<GameObject> { house0 };
            for (int k = 1; k < n; k++)
            {
                var c = UnityEngine.Object.Instantiate(house0);
                c.transform.position = house0.transform.position + new Vector3(k * plot, 0, 0);
                houses.Add(c);
            }
            float w = house.size[0], d = house.size[1];
            // near3, the worst near view: three houses drawn near at once (a lane or a corner, where three stand
            // within reach), at eye level 5 m off the middle one of the first three, looking wide across all three
            var views = new[]
            {
                ("street", new Vector3(w / 2 - 9.0f, -19.0f, 1.6f), new Vector3(w / 2, 1.0f, 3.0f), 38f, 0),
                ("raised", new Vector3(-7.0f, -12.0f, 12.0f), new Vector3(w / 2, d / 2, 2.5f), 42f, 0),
                ("along", new Vector3(-4.0f, -9.0f, 1.6f), new Vector3(60.0f, 2.0f, 3.0f), 52f, 0),
                ("near3", new Vector3(plot + w / 2, -5.0f, 1.6f), new Vector3(plot + w / 2, 2.0f, 4.0f), 75f, 3),
            };
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var lowsun = Lights.First(l => l.name == "lowsun");
            var own = paint.lights?.FirstOrDefault(e => e.light == "lowsun");
            var l_ = own != null ? Own(lowsun, own) : lowsun;
            l_.azimuth = new Vector2(Mathf.Sin(sunOff * Mathf.Deg2Rad), -Mathf.Cos(sunOff * Mathf.Deg2Rad));
            var col = paint.colour?.lights?.FirstOrDefault(e => e.light == "lowsun");
            Light(sun, l_, col);
            adjust.postExposure.Override(own != null ? own.exposure : lowsun.exposure);
            var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = Msaa };
            rt.Create();
            var probe = new RenderTexture(1, 1, 0, RenderTextureFormat.ARGB32);
            probe.Create();
            var rows = new List<string>();
            var streamed = new List<string>();
            // a house's own page (every texture but the strokes, which every house shares), bytes from a mip down
            var pageTex = mats.Values.SelectMany(m => m.GetTexturePropertyNames().Select(m.GetTexture)).OfType<Texture2D>()
                .Distinct().Where(t => !t.name.StartsWith("paint-")).ToList();
            var sharedTex = mats.Values.SelectMany(m => m.GetTexturePropertyNames().Select(m.GetTexture)).OfType<Texture2D>()
                .Distinct().Where(t => t.name.StartsWith("paint-")).ToList();
            long From(Texture2D t, int mip)
            {
                long b = 0;
                for (int m = mip; m < t.mipmapCount; m++)
                    b += (long)UnityEngine.Experimental.Rendering.GraphicsFormatUtility.ComputeMipmapSize(
                        Math.Max(1, t.width >> m), Math.Max(1, t.height >> m), t.graphicsFormat);
                return b;
            }
            long pageFull = pageTex.Sum(t => From(t, 0)), shared = sharedTex.Sum(t => From(t, 0));
            int maxRed = QualitySettings.streamingMipmapsMaxLevelReduction;
            float pxPerM = house.page != null && house.page.pxPerM > 0 ? house.page.pxPerM : 128f;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            try
            {
                foreach (var (name, pos, target, fov, forceNear) in views)
                {
                    cam.transform.SetPositionAndRotation(ToUnity(pos), Quaternion.LookRotation(ToUnity(target - pos), Vector3.up));
                    cam.fieldOfView = fov;
                    urp.shadowCascadeCount = 1;
                    urp.mainLightShadowmapResolution = 4096;
                    urp.shadowDistance = name == "along" ? 80f : (target - pos).magnitude + 8f;
                    int nearN = 0, cityN = 0, tris = 0, subs = 0, dropped = 0;
                    var planes = GeometryUtility.CalculateFrustumPlanes(cam);
                    for (int hi = 0; hi < houses.Count; hi++)
                    {
                        var h = houses[hi];
                        var lv = h.GetComponentsInChildren<Transform>(true).Where(t => t.parent == h.transform).ToList();
                        var centre = h.transform.position + ToUnity(new Vector3(w / 2, d / 2, 3f));
                        float dc = Vector3.Distance(cam.transform.position, centre);
                        string at = hi < forceNear || dc < within ? "near" : dc >= cityFrom ? "city" : "street";
                        nearN += at == "near" ? 1 : 0;
                        cityN += at == "city" ? 1 : 0;
                        // its shadow reaches its height over the sun's rise beyond it
                        float reach = (house.size.Length > 2 ? house.size[2] : 9f) / Mathf.Tan(Mathf.Max(l_.elevation, 5f) * Mathf.Deg2Rad);
                        bool cast = !drop || dc - 0.5f * Mathf.Max(w, d) <= urp.shadowDistance + reach;
                        dropped += cast ? 0 : 1;
                        foreach (var t in lv)
                        {
                            bool on = t.name.EndsWith("-" + at);
                            t.gameObject.SetActive(on);
                            if (!on)
                                continue;
                            foreach (var r in t.GetComponentsInChildren<MeshRenderer>())
                                r.shadowCastingMode = !cast ? ShadowCastingMode.Off : Arg("-streetShadowTwo") != "0" ? ShadowCastingMode.TwoSided : ShadowCastingMode.On;
                            Assign(t.gameObject, mats, "Pc", MatLevel(at));
                            foreach (var r in t.GetComponentsInChildren<MeshRenderer>())
                                if (GeometryUtility.TestPlanesAABB(planes, r.bounds))
                                {
                                    var mf = r.GetComponent<MeshFilter>();
                                    tris += mf.sharedMesh.triangles.Length / 3;
                                    subs += mf.sharedMesh.subMeshCount;
                                }
                        }
                    }
                    // the mip the streamer would hold for each house: the finest its page's densest texels (the street
                    // walls, pxPerM) need at the house's nearest point, as many screen pixels a metre there; a house out
                    // of view, or as far as it may go, at the most mips the quality settings let it drop
                    long bytes = 0;
                    var mips = new int[maxRed + 1];
                    float pxK = 2f * Mathf.Tan(fov * 0.5f * Mathf.Deg2Rad) / Height;
                    foreach (var h in houses)
                    {
                        var rs = h.GetComponentsInChildren<MeshRenderer>();
                        var bb = rs[0].bounds;
                        foreach (var r in rs)
                            bb.Encapsulate(r.bounds);
                        float dist = Mathf.Max(0.1f, Mathf.Sqrt(bb.SqrDistance(cam.transform.position)));
                        int mip = GeometryUtility.TestPlanesAABB(planes, bb)
                            ? Mathf.Clamp(Mathf.FloorToInt(Mathf.Log(pxPerM * dist * pxK, 2f)), 0, maxRed) : maxRed;
                        mips[mip]++;
                        bytes += pageTex.Sum(t => From(t, mip));
                    }
                    streamed.Add($"| {name} | {(bytes + shared) / 1048576.0:F0} | {string.Join(" / ", mips)} | {(long)houses.Count * pageFull / 1048576.0 + shared / 1048576.0:F0} |");
                    cam.targetTexture = rt;
                    // the renderer's own count of the last frame (its profiler counters; "-" where the editor keeps none)
                    var rec = new[] { "Draw Calls Count", "Batches Count", "SetPass Calls Count", "Shadow Casters Count" }
                        .Select(c => Unity.Profiling.ProfilerRecorder.StartNew(Unity.Profiling.ProfilerCategory.Render, c)).ToArray();
                    var ms = new List<double>();
                    for (int b = 0; b <= Batches; b++)
                    {
                        var clock = System.Diagnostics.Stopwatch.StartNew();
                        for (int k = 0; k < PerBatch; k++)
                            LT1Render.Render(cam, rt);
                        Graphics.Blit(rt, probe);
                        AsyncGPUReadback.Request(probe).WaitForCompletion();
                        if (b > 0)
                            ms.Add(clock.Elapsed.TotalMilliseconds / PerBatch);
                    }
                    string stats = string.Join(" / ", rec.Select(r => r.Valid && r.LastValue > 0 ? r.LastValue.ToString() : "-"));
                    foreach (var r in rec)
                        r.Dispose();
                    cam.targetTexture = null;
                    ms.Sort();
                    double median = ms[ms.Count / 2];
                    rows.Add($"| {name} | {n} | {nearN} | {cityN} | {dropped} | {tris:N0} | {subs} | {stats} | {median:F1} | {string.Join(" ", ms.Select(x => x.ToString("F1")))} |");
                    Debug.Log($"[LT1Street] timing {name}: {median:F2} ms, {nearN} near and {cityN} city of {n}, {tris} triangles and {subs} draws in view");
                    Capture(cam, Path.Combine(outDir, $"timing-{name}.png"));
                }
            }
            finally
            {
                ShaderUtil.allowAsyncCompilation = async;
                rt.Release();
                probe.Release();
                UnityEngine.Object.DestroyImmediate(rt);
                UnityEngine.Object.DestroyImmediate(probe);
            }
            // what one house holds: its page's textures and its levels' meshes, as the runtime counts them
            long texBytes = 0, meshBytes = 0;
            var texLines = new List<string>();
            foreach (var t in mats.Values.SelectMany(m => m.GetTexturePropertyNames().Select(m.GetTexture)).Where(t => t != null).Distinct())
            {
                long b = UnityEngine.Profiling.Profiler.GetRuntimeMemorySizeLong(t);
                texBytes += b;
                texLines.Add($"{t.name} {t.width}x{t.height} {(t is Texture2D t2 ? t2.format.ToString() : "")} {b / 1048576.0:F1} MB");
            }
            foreach (var mf in house0.GetComponentsInChildren<MeshFilter>(true))
                meshBytes += UnityEngine.Profiling.Profiler.GetRuntimeMemorySizeLong(mf.sharedMesh);
            var md = new System.Text.StringBuilder();
            md.AppendLine($"Offscreen in the editor, batch mode (LT1Street.Timing; {SystemInfo.graphicsDeviceName}, 2560x1440, MSAA 4x, way Pc, low sun, " +
                          $"one 4096 shadow cascade, screen-space occlusion; median of {Batches} batches of {PerBatch}). A row of {n} copies of house {house.house} " +
                          $"on {plot:F1} m plots, near level within {within:F0} m, city level from {(cityFrom < float.MaxValue ? cityFrom.ToString("F0") + " m" : "nowhere")}. Not the player's frame.").AppendLine();
            md.AppendLine($"City level {(Arg("-streetCityOne") == "0" ? "a material a piece" : "one mesh, one material")}; far shadows {(drop ? "dropped beyond the shadow distance and the shadow's reach" : "cast by every house")}.").AppendLine();
            md.AppendLine("| View | Houses | Near | City | Casting none | Triangles in view | Draws in view (counted) | Renderer: draw calls / batches / set-pass / shadow casters | ms a frame | Batches |");
            md.AppendLine("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |");
            foreach (var r in rows)
                md.AppendLine(r);
            md.AppendLine().AppendLine($"Textures streamed (GPU, counted, not measured: the mip each house's page would hold at its nearest point " +
                                       $"for {pxPerM:F0} px/m at 2560x1440, at most {maxRed} mips dropped, the quality setting; one shared stroke texture):").AppendLine();
            md.AppendLine($"| View | MB streamed | Houses at mip 0 / 1 / ... / {maxRed} | MB all at full |");
            md.AppendLine("| --- | --- | --- | --- |");
            foreach (var r in streamed)
                md.AppendLine(r);
            md.AppendLine().AppendLine($"One house's page on the GPU at full: {pageFull / 1048576.0:F1} MB, at mip {maxRed} and down {pageTex.Sum(t => From(t, maxRed)) / 1048576.0:F2} MB; " +
                                       $"shared strokes {shared / 1048576.0:F1} MB.");
            md.AppendLine().AppendLine($"One house, as the editor counts it (a CPU copy beside the GPU's): textures {texBytes / 1048576.0:F1} MB ({string.Join("; ", texLines)}); meshes, every level, {meshBytes / 1048576.0:F1} MB.");
            File.WriteAllText(Path.Combine(outDir, "timing.md"), md.ToString());
            Debug.Log("[LT1Street] timing\n" + md);
        }

        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        static float LToY(float L) => L > 8 ? Mathf.Pow((L + 16) / 116f, 3) : L / 903.3f;

        static readonly Color Back = new Color(0.62f, 0.62f, 0.62f);

        static Color Lin(float v, float[] t) => t == null || t.Length != 3 ? new Color(v, v, v).gamma : new Color(v * t[0], v * t[1], v * t[2]).gamma;

        /// <summary>The page linear and block-compressed, streamed by mip, the strokes repeating; the levels with their own normals.</summary>
        static void Import(string gen)
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { gen }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti))
                    continue;  // the one material's tables, made here
                bool tile = Path.GetFileNameWithoutExtension(path).StartsWith("paint-");
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = false;
                ti.mipmapEnabled = true;
                ti.wrapMode = tile ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                ti.filterMode = FilterMode.Trilinear;
                ti.anisoLevel = tile ? 8 : 4;
                // block-compressed (BC7 on the Mac): s07, no still changes by 1.4 L* over 8 px at any view, a quarter of
                // the memory; -streetCompress 0 keeps the page uncompressed for an A/B
                ti.textureCompression = Arg("-streetCompress") == "0" ? TextureImporterCompression.Uncompressed : TextureImporterCompression.CompressedHQ;
                // streamed: a far house holds only the mips its distance needs (in the player; counted in Timing)
                ti.streamingMipmaps = true;
                ti.maxTextureSize = 4096;
                ti.npotScale = TextureImporterNPOTScale.None;
                ti.SaveAndReimport();
            }
            foreach (var level in Levels)
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{gen}/house-{level}.fbx");
                mi.materialImportMode = ModelImporterMaterialImportMode.None;
                mi.importNormals = ModelImporterNormals.Import;
                mi.importTangents = ModelImporterTangents.CalculateMikk;
                mi.importBlendShapes = false;
                mi.importCameras = false;
                mi.importLights = false;
                mi.animationType = ModelImporterAnimationType.None;
                mi.importAnimation = false;
                mi.meshCompression = ModelImporterMeshCompression.Off;
                mi.globalScale = 1;
                mi.SaveAndReimport();
            }
        }

        /// <summary>
        /// One material for each of the house's materials, way and level. A plane that stands for finer geometry reads
        /// the page's normal at every level: the street level's walls, and the roof's course planes at both.
        /// </summary>
        static Dictionary<string, Material> Materials(string gen, Paint p, House house)
        {
            var lap = house.lap;
            var shader = Shader.Find("Overstory/Finish");
            var tex = (Func<string, Texture2D>)(n => AssetDatabase.LoadAssetAtPath<Texture2D>($"{gen}/{n}.png"));
            var outp = new Dictionary<string, Material>();
            foreach (var way in new[] { "P", "Pc" })
            foreach (var level in new[] { "near", "street" })
            foreach (var m in p.mats)
            {
                var mat = new Material(shader);
                mat.SetFloat("_Paint", 1);
                var c = way == "Pc" ? p.colour?.mats?.FirstOrDefault(e => e.name == m.name) : null;
                if (c != null)
                {
                    mat.SetVector("_Tint", Tint(c.tint));
                    mat.SetVector("_BareTint", Tint(c.bareTint));
                    mat.SetVector("_UnderTint", Tint(c.underTint));
                    mat.SetVector("_StainTint", Tint(c.stainTint));
                    mat.SetVector("_WashTint", Tint(p.colour.washTint));
                }
                mat.EnableKeyword("_OS_PAINT");
                mat.SetTexture("_Hist", tex("hist-p"));
                mat.SetTexture("_Hist2", tex("hist-p2"));
                mat.SetTexture("_Geo", tex("geo"));
                mat.SetTexture("_StreetN", tex("street-normal"));
                mat.SetTexture("_Stroke", tex("paint-stroke"));
                mat.SetFloat("_StrokeScale", p.strokeScale);
                mat.SetFloat("_EdgeAmp", p.edgeAmp);
                mat.SetVector("_StrokeFade", new Vector4(p.strokeFade[0], p.strokeFade[1], 0, 0));
                mat.SetVector("_BrushFade", new Vector4(p.brushFade[0], p.brushFade[1], 0, 0));
                mat.SetFloat("_BrushL", m.brushL);
                mat.SetFloat("_BrushFar", p.brushFar);
                mat.SetFloat("_DragL", p.dragL);
                mat.SetFloat("_DragScale", p.dragScale);
                mat.SetFloat("_DLRange", p.dlRange);
                mat.SetFloat("_FlatUp", m.flatUp);
                mat.SetFloat("_StainEdge", m.stainEdge);
                mat.SetFloat("_RimL", p.rimL);
                mat.SetFloat("_RimW", p.rimW);
                mat.SetFloat("_RimFar", p.rimFar);
                mat.SetVector("_RimBreak", new Vector4(p.rimBreak[0], p.rimBreak[1], 0, 0));
                mat.SetFloat("_WashL", p.washL);
                mat.SetFloat("_BareWash", p.bareWash);
                mat.SetVector("_WashFade", p.washFade != null && p.washFade.Length == 2 ? new Vector4(p.washFade[0], p.washFade[1], 0, 0) : Vector4.zero);
                mat.SetFloat("_BareShift", p.bareShift);
                mat.SetFloat("_Painted", m.painted);
                mat.SetFloat("_PaintL", m.L);
                mat.SetFloat("_BareL", m.bareL);
                mat.SetFloat("_UnderL", m.underL);
                mat.SetFloat("_StainDL", m.stainDL);
                mat.SetFloat("_PaintSmooth", m.smooth);
                mat.SetFloat("_StainSmooth", m.stainSmooth);
                mat.SetFloat("_AOStrength", m.ao);
                mat.SetFloat("_ShadowLift", m.shadowLift);
                mat.SetFloat("_LapDark", p.lapDark);
                mat.SetFloat("_LapCore", p.lapCore);
                mat.SetFloat("_LapReach", p.lapReach);
                mat.SetFloat("_LapGrimeL", p.lapGrimeL);
                mat.SetFloat("_LapGrimeReach", p.lapGrimeReach);
                mat.SetFloat("_LapGrimeBreak", p.lapGrimeBreak);
                mat.SetFloat("_LapScale", lap.reach);
                mat.SetFloat("_LapPage", p.lapPage);
                mat.SetFloat("_LapStep", lap.step);
                if (level == "street" || m.name == "roof")
                {
                    mat.SetFloat("_Street", 1);
                    mat.EnableKeyword("_OS_STREET");
                }
                // the roof's course planes stand for tiles: their baked rolls shadow themselves as the real courses do
                if (m.name == "roof")
                {
                    mat.SetFloat("_Plane", 1);
                    mat.SetFloat("_PlaneShadow", house.planeShadow);
                    mat.EnableKeyword("_OS_PLANE");
                }
                string key = $"{way}-{level}-{m.name}";
                AssetDatabase.CreateAsset(mat, $"{gen}/mat-{key}.mat");
                outp[key] = mat;
            }
            // the windows' glass (OS_Glass): the room behind it and its kinds' waves from glass.json, by way of house.json;
            // way P's room in the clay's greys (each colour's luminance), way Pc's in its colours
            var g = house.glass;
            if (g != null && g.walls != null)
            {
                var glassShader = Shader.Find("Overstory/Glass");
                foreach (var way in new[] { "P", "Pc" })
                foreach (var level in new[] { "near", "street" })
                {
                    Vector4 C(float[] c, float a)
                    {
                        if (way == "P")
                        {
                            float y = 0.2126f * c[0] + 0.7152f * c[1] + 0.0722f * c[2];
                            return new Vector4(y, y, y, a);
                        }
                        return new Vector4(c[0], c[1], c[2], a);
                    }
                    var r = g.room;
                    var mat = new Material(glassShader);
                    mat.SetTexture("_Geo", tex("geo"));
                    mat.SetFloat("_Gloss", g.gloss);
                    // room: lampPower, lampSoftM2, depthM, halfWidthM, sillM, heightM, ambient, lampDropM, lampSwingM,
                    // furnitureHeightM, furnitureHalfLengthM, cornerReachM, cornerLight, shadeRadiusM, shadeGlow
                    mat.SetVector("_RoomWall", C(g.walls, r[2]));
                    mat.SetVector("_RoomCeiling", C(g.ceiling, r[3]));
                    mat.SetVector("_RoomFloor", C(g.floor, r[4]));
                    mat.SetVector("_RoomShape", new Vector4(r[5], r[11], r[12], 0));
                    mat.SetVector("_RoomFurniture", C(g.furniture, r[9]));
                    mat.SetVector("_RoomFurniture2", new Vector4(r[10], 0, 0, 0));
                    // curtains: share, opacity, depthM, valanceShare, foldsPerM
                    mat.SetVector("_Curtain", C(g.curtain, g.curtains[0]));
                    mat.SetVector("_CurtainB", new Vector4(g.curtains[1], g.curtains[2], g.curtains[3], g.curtains[4]));
                    mat.SetVector("_GlassDay", new Vector4(g.daylight[0], g.daylight[1], g.daylight[2], g.daylight[3]));
                    var shapes = new[] { "rings", "waves", "one-way", "flat" };
                    for (int k = 0; k < 4 && k < g.kinds.Length; k++)
                    {
                        var kd = g.kinds[k];
                        mat.SetVector($"_Kind{k}", new Vector4(kd.tiltDeg * Mathf.Deg2Rad, kd.perM[0], kd.perM[1], Array.IndexOf(shapes, kd.shape)));
                    }
                    string key = $"{way}-{level}-glass";
                    AssetDatabase.CreateAsset(mat, $"{gen}/mat-{key}.mat");
                    outp[key] = mat;
                }
            }
            // a far house's one material: the street level's shared values, and each material's own from a table, a row
            // a material in paint.json's order, which the merged city mesh's faces name in their uv2.x (OneMesh)
            foreach (var way in new[] { "P", "Pc" })
            {
                var tab = new Texture2D(7, p.mats.Length, TextureFormat.RGBAFloat, false, true) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp, name = $"mattab-{way}" };
                for (int k = 0; k < p.mats.Length; k++)
                {
                    var m = p.mats[k];
                    var c = way == "Pc" ? p.colour?.mats?.FirstOrDefault(e => e.name == m.name) : null;
                    Color V(float[] t, float w) { var v = Tint(t); return new Color(v.x, v.y, v.z, w); }
                    tab.SetPixel(0, k, new Color(m.painted, m.L, m.bareL, m.underL));
                    tab.SetPixel(1, k, new Color(m.stainDL, m.smooth, m.stainSmooth, m.ao));
                    tab.SetPixel(2, k, new Color(m.shadowLift, m.brushL, m.flatUp, m.stainEdge));
                    tab.SetPixel(3, k, V(c?.tint, m.name == "roof" ? house.planeShadow : 0f));
                    tab.SetPixel(4, k, V(c?.bareTint, 0));
                    tab.SetPixel(5, k, V(c?.underTint, 0));
                    tab.SetPixel(6, k, V(c?.stainTint, 0));
                }
                tab.Apply(false, true);
                AssetDatabase.CreateAsset(tab, $"{gen}/mattab-{way}.asset");
                var one = new Material(outp[$"{way}-street-{p.mats[0].name}"]);
                one.SetFloat("_Plane", 0);
                one.DisableKeyword("_OS_PLANE");
                one.SetFloat("_One", 1);
                one.EnableKeyword("_OS_ONE");
                one.SetTexture("_MatTab", tab);
                AssetDatabase.CreateAsset(one, $"{gen}/mat-{way}-street-one.mat");
                outp[$"{way}-street-one"] = one;
            }
            return outp;
        }

        /// <summary>Whether the SRP Batcher draws OS_Finish's materials: on in the pipeline, and the shader compatible.</summary>
        static void SrpBatcher(Shader shader)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var flags = System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static;
            var code = typeof(ShaderUtil).GetMethod("GetSRPBatcherCompatibilityCode", flags);
            var why = typeof(ShaderUtil).GetMethod("GetSRPBatcherCompatibilityIssueReason", flags);
            string state = "unknown (no editor query)";
            if (code != null)
            {
                int c = Convert.ToInt32(code.Invoke(null, new object[] { shader, 0 }));
                state = c == 0 ? "compatible" : $"not compatible: {(why != null ? why.Invoke(null, new object[] { shader, 0, c }) : c)}";
            }
            Debug.Log($"[LT1Street] SRP Batcher: pipeline {(urp.useSRPBatcher ? "on" : "off")}; {shader.name} {state}");
        }

        /// <summary>
        /// The city level as one mesh and one material, one draw a far house: every piece's faces merged, each vertex
        /// naming its material's row in the one material's table (uv2.x, paint.json's order). The level's own object is
        /// replaced in place, under the same name, so the levels swap as before.
        /// </summary>
        static GameObject OneMesh(GameObject level, Paint p, string gen)
        {
            var index = p.mats.Select((m, k) => (m.name, k)).ToDictionary(e => e.name, e => e.k);
            var parts = new List<CombineInstance>();
            var rows = new List<float>();
            var toLevel = level.transform.worldToLocalMatrix;
            foreach (var r in level.GetComponentsInChildren<MeshRenderer>(true))
            {
                string kind = r.gameObject.name.Substring(r.gameObject.name.IndexOf('_') + 1);
                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                if (!index.TryGetValue(kind, out int row) || mesh.colors.Length != mesh.vertexCount)
                    throw new Exception($"[LT1Street] city {r.gameObject.name}: no material row or no vertex colours");
                for (int s = 0; s < mesh.subMeshCount; s++)
                {
                    var sub = new Mesh { indexFormat = mesh.indexFormat };
                    sub.SetVertices(mesh.vertices);
                    sub.SetNormals(mesh.normals);
                    sub.SetTangents(mesh.tangents);
                    sub.SetColors(mesh.colors);
                    sub.SetUVs(0, mesh.uv);
                    sub.SetUVs(1, mesh.uv2);
                    sub.SetUVs(2, Enumerable.Repeat(new Vector2(row, 0), mesh.vertexCount).ToList());
                    sub.SetTriangles(mesh.GetTriangles(s), 0);
                    parts.Add(new CombineInstance { mesh = sub, transform = toLevel * r.transform.localToWorldMatrix });
                }
            }
            var merged = new Mesh { name = $"{level.name}-one", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            merged.CombineMeshes(parts.ToArray(), true, true);
            merged.Optimize();
            merged.UploadMeshData(false);
            AssetDatabase.CreateAsset(merged, $"{gen}/house-city-one.asset");
            var go = new GameObject(level.name);
            go.transform.SetParent(level.transform.parent, false);
            go.transform.localPosition = level.transform.localPosition;
            go.transform.localRotation = level.transform.localRotation;
            go.transform.localScale = level.transform.localScale;
            var one = new GameObject("city_one");
            one.transform.SetParent(go.transform, false);
            one.AddComponent<MeshFilter>().sharedMesh = merged;
            one.AddComponent<MeshRenderer>();
            UnityEngine.Object.DestroyImmediate(level);
            Debug.Log($"[LT1Street] city as one: {parts.Count} parts, {merged.vertexCount} vertices, {merged.triangles.Length / 3} triangles, one draw");
            return go;
        }

        static readonly string[] Levels = { "near", "street", "city" };

        // the city level draws with the street level's materials: its faces are the street level's, on the same charts
        static string MatLevel(string level) => level == "city" ? "street" : level;

        static Vector4 Tint(float[] t) => t == null || t.Length != 3 ? Vector4.one : new Vector4(t[0], t[1], t[2], 1);

        static void Assign(GameObject level, Dictionary<string, Material> mats, string way, string levelName)
        {
            foreach (var r in level.GetComponentsInChildren<MeshRenderer>(true))
            {
                string kind = r.gameObject.name.Substring(r.gameObject.name.IndexOf('_') + 1);
                if (mats.TryGetValue($"{way}-{levelName}-{kind}", out var mat))
                    r.sharedMaterial = mat;
                else
                    Debug.LogWarning($"[LT1Street] no material for {r.gameObject.name}");
            }
        }

        /// <summary>The FBX's axes as Unity imported them: the house's cladding must sit at +x, +z (as LT1Finish).</summary>
        static void Orient(GameObject house, GameObject near)
        {
            var clad = near.GetComponentsInChildren<MeshRenderer>(true).First(r => r.gameObject.name.EndsWith("cladding"));
            var c = clad.bounds.center;
            if (c.x < 0 && c.z < 0)
                house.transform.rotation = Quaternion.Euler(0, 180, 0);
            else if (c.x < 0 || c.z < 0)
                house.transform.localScale = new Vector3(c.x < 0 ? -1 : 1, 1, c.z < 0 ? -1 : 1);
            Physics.SyncTransforms();
            Debug.Log($"[LT1Street] house oriented: cladding at {clad.bounds.center}");
        }

        static Lighting Own(Lighting l, PLight p) => p.azimuth == null || p.azimuth.Length != 2 ? l : new Lighting
        {
            name = l.name, azimuth = new Vector2(p.azimuth[0], p.azimuth[1]), elevation = p.elevation, sun = p.sun,
            shadow = p.shadow, sky = p.sky, equator = p.equator, ground = p.ground, exposure = p.exposure,
        };

        static void Light(Light sun, Lighting l, PColLight c = null)
        {
            var a = l.azimuth.normalized;
            float e = l.elevation * Mathf.Deg2Rad;
            var toSun = new Vector3(Mathf.Cos(e) * a.x, Mathf.Cos(e) * a.y, Mathf.Sin(e));
            sun.transform.rotation = Quaternion.LookRotation(-ToUnity(toSun), Vector3.up);
            sun.intensity = l.sun;
            sun.shadowStrength = l.shadow;
            sun.color = Lin(1, c?.sun);
            RenderSettings.ambientSkyColor = Lin(l.sky, c?.sky);
            RenderSettings.ambientEquatorColor = Lin(l.equator, c?.equator);
            RenderSettings.ambientGroundColor = Lin(l.ground, c?.ground);
            DynamicGI.UpdateEnvironment();
        }

        static void Capture(Camera cam, string file)
        {
            var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = Msaa };
            rt.Create();
            var target = cam.targetTexture;
            try
            {
                cam.targetTexture = rt;
                for (int i = 0; i < WarmUp; i++)
                    LT1Render.Render(cam, rt);
                var resolved = new RenderTexture(Width, Height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
                Graphics.Blit(rt, resolved);
                var prev = RenderTexture.active;
                RenderTexture.active = resolved;
                var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                File.WriteAllBytes(file, tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
                resolved.Release();
                UnityEngine.Object.DestroyImmediate(resolved);
            }
            finally
            {
                cam.targetTexture = target;
                rt.Release();
                UnityEngine.Object.DestroyImmediate(rt);
            }
        }
    }
}
