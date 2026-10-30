using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Object = UnityEngine.Object;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The street as its own test stages it, for the measuring tools (LT1Perf, LT1Golden): Street.unity as the last
    /// LT1Street.Run left it (its houses, ground, sun, volume, camera, sky and the town's sky map), each house's materials
    /// from its Generated folder, the street's judging views (LT1Street's RowViews for a row, its Views for one house: eye,
    /// street, raised and high unless -views says) and its two lights (overcast and low sun, the street's own rows over
    /// the corner's), applied by LT1Street's own functions so a frame here is drawn as the street's stills are.
    ///
    /// LT1Street keeps its staging private, and the street lane owns it, so this reads it by reflection and never edits
    /// it: a member it needs that is renamed or gone stops the tool with that member's name. Two of Run's rules are
    /// repeated here: the low sun turned off square for a view that is not the floor's (-streetSunOff, 45 degrees), and
    /// the volume's effects (Neutral tonemapping, the colour adjustments, and its Grade when it has one), made again when
    /// the scene's profile comes back without them (street-volume.asset keeps them as no sub-assets, so they live only in
    /// the session that built them). Nothing is written into the street's folders: the scene is opened, never saved; the
    /// sky's and ground's materials and the volume's profile are copies, and a made grade's look-up goes to the harness's
    /// own Generated folder, so a light set here changes none of the street's assets.
    /// </summary>
    sealed class StreetStaging
    {
        public const string ScenePath = "Assets/Experiments/LT1/Street/Street.unity";
        const string Gen = "Assets/Experiments/LT1/Street/Generated";
        /// <summary>The harness's own generated folder (not in git): the perf scene and anything made for it.</summary>
        public const string Own = "Assets/Experiments/LT1/Perf/Generated";
        const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

        /// <summary>The judging views the tools hold by default (LT1Street.Run's own default).</summary>
        public static readonly string[] JudgingViews = { "eye", "street", "raised", "high" };

        /// <summary>A view as the street stages it: street metres (x along, y back, z up), each house's level, the
        /// shadowed distance fitted to it.</summary>
        public sealed class Stop
        {
            public string name;
            public Vector3 pos, target;
            public float fov, shadowDistance;
            public bool floor;
            public string[] levels;
        }

        public string[] ids;
        public bool row;
        public Camera cam;
        public Light sun;
        public Volume volume;
        public ColorAdjustments adjust;
        public GameObject sky;
        public Material skyMat;
        public Renderer ground;
        public Material groundMat;
        public SkyMap town;
        public Cubemap cube;
        public GameObject[] roots;
        public Dictionary<string, GameObject>[] levels;
        public Dictionary<string, Material>[] mats;
        public Stop[] stops;
        public string[] lightNames;

        IList built;
        object paint0;
        Array lights;
        Array ownLights;
        float sunOff;

        static readonly Type T = typeof(LT1Street);

        static Type Nested(string name) =>
            T.GetNestedType(name, Any) ?? throw new MissingMemberException($"[StreetStaging] LT1Street has no type {name}");

        static MethodInfo Method(string name) =>
            T.GetMethod(name, Any) ?? throw new MissingMemberException($"[StreetStaging] LT1Street has no method {name}");

        static object Static(string name) =>
            (T.GetField(name, Any) ?? throw new MissingMemberException($"[StreetStaging] LT1Street has no field {name}")).GetValue(null);

        static object Call(string name, params object[] args) => Method(name).Invoke(null, args);

        static object Get(object o, string field)
        {
            if (o == null)
                return null;
            var f = o.GetType().GetField(field, Any) ?? throw new MissingMemberException($"[StreetStaging] {o.GetType().Name} has no field {field}");
            return f.GetValue(o);
        }

        static void Set(object o, string field, object value)
        {
            var f = o.GetType().GetField(field, Any) ?? throw new MissingMemberException($"[StreetStaging] {o.GetType().Name} has no field {field}");
            f.SetValue(o, value);
        }

        static Vector3 ToUnity(Vector3 s) => new Vector3(s.x, s.z, s.y);

        /// <summary>An asset folder, made with its parents if it is not there.</summary>
        public static void Folder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
                return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            Folder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        static IEnumerable<Transform> All(UnityEngine.SceneManagement.Scene scene) =>
            scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true));

        /// <summary>Street.unity opened as the street's test left it, and staged as it stages it (in memory only).</summary>
        public static StreetStaging Open()
        {
            if (!File.Exists(ScenePath))
                throw new FileNotFoundException($"[StreetStaging] no {ScenePath}: run the street's test first (blender/parts/street/run/render.sh)");
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var all = All(scene).ToList();
            GameObject Find(string name) => all.FirstOrDefault(t => t.name == name)?.gameObject
                                            ?? throw new MissingReferenceException($"[StreetStaging] no '{name}' in {ScenePath}");
            var s = new StreetStaging();
            // the houses in the order the test built them (its list's order is each house's place in the town's map)
            s.roots = all.Where(t => t.name.StartsWith("House ")).Select(t => t.gameObject).ToArray();
            if (s.roots.Length == 0)
                throw new MissingReferenceException($"[StreetStaging] no house in {ScenePath}");
            s.ids = s.roots.Select(r => r.name.Substring("House ".Length)).ToArray();
            s.row = s.roots.Length > 1;
            s.cam = Find("Camera").GetComponent<Camera>();
            s.sun = Find("Sun").GetComponent<Light>();
            s.volume = Find("Volume").GetComponent<Volume>();
            s.sky = Find("Sky");
            s.ground = Find("Ground").GetComponent<Renderer>();
            s.town = Object.FindAnyObjectByType<SkyMap>(FindObjectsInactive.Include);

            // the house's record, paint, materials and levels, as LT1Street's Built
            var builtType = Nested("Built");
            s.built = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(builtType));
            s.levels = new Dictionary<string, GameObject>[s.roots.Length];
            s.mats = new Dictionary<string, Material>[s.roots.Length];
            for (int i = 0; i < s.roots.Length; i++)
            {
                string gen = $"{Gen}/{s.ids[i]}";
                var b = Activator.CreateInstance(builtType);
                Set(b, "id", s.ids[i]);
                Set(b, "house", JsonUtility.FromJson(File.ReadAllText(Path.Combine(gen, "house.json")), Nested("House")));
                Set(b, "paint", JsonUtility.FromJson(File.ReadAllText(Path.Combine(gen, "paint.json")), Nested("Paint")));
                s.mats[i] = AssetDatabase.FindAssets("t:Material", new[] { gen })
                    .Select(AssetDatabase.GUIDToAssetPath).Where(p => Path.GetFileName(p).StartsWith("mat-"))
                    .ToDictionary(p => Path.GetFileNameWithoutExtension(p).Substring("mat-".Length), AssetDatabase.LoadAssetAtPath<Material>);
                Set(b, "mats", s.mats[i]);
                Set(b, "root", s.roots[i]);
                s.levels[i] = new Dictionary<string, GameObject>();
                foreach (Transform c in s.roots[i].transform)
                    if (c.name.StartsWith("house-"))
                        s.levels[i][c.name.Substring("house-".Length)] = c.gameObject;
                Set(b, "levels", s.levels[i]);
                s.built.Add(b);
            }
            s.paint0 = Get(s.built[0], "paint");

            // the sky's and ground's materials and the volume's profile as copies, so nothing of the street's is changed
            var skyR = s.sky.GetComponent<MeshRenderer>();
            s.skyMat = new Material(skyR.sharedMaterial) { name = "sky (the harness's copy)" };
            skyR.sharedMaterial = s.skyMat;
            s.groundMat = new Material(s.ground.sharedMaterial) { name = "ground (the harness's copy)" };
            s.ground.sharedMaterial = s.groundMat;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.name = "street volume (the harness's copy)";
            var kept = s.volume.sharedProfile != null ? s.volume.sharedProfile.components.Where(c => c != null).ToList() : new List<VolumeComponent>();
            foreach (var c in kept)
            {
                var copy = Object.Instantiate(c);
                copy.name = c.name;
                profile.components.Add(copy);
            }
            if (kept.Count == 0)
            {
                // as LT1Street.Run makes them: Neutral, the colour adjustments, and the street's grade if it has one
                profile.Add<Tonemapping>(true).mode.Override(TonemappingMode.Neutral);
                profile.Add<ColorAdjustments>(true);
                var grade = T.GetMethod("Grade", Any);
                if (grade != null)
                {
                    Folder(Own);
                    grade.Invoke(null, new object[] { profile, Own });
                }
                Debug.Log($"[StreetStaging] the scene's volume came back without its effects: made again as LT1Street.Run makes them " +
                          $"({string.Join(", ", profile.components.Select(c => c.GetType().Name))})");
            }
            s.volume.sharedProfile = profile;
            if (!profile.TryGet(out s.adjust))
                throw new MissingReferenceException("[StreetStaging] the street's volume has no colour adjustments");
            s.cube = new Cubemap(32, TextureFormat.RGBAHalf, true) { name = "stage-sky" };
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.fog = false;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = s.cube;

            // the lights: the street's rows over the corner's, else the paint's copy (LT1Street.Run)
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            s.lights = (Array)Static("Lights");
            s.ownLights = (Array)Call("SourceLights", root) ?? (Array)Get(s.paint0, "lights");
            s.lightNames = s.lights.Cast<object>().Select(l => (string)Get(l, "name")).ToArray();
            s.sunOff = float.Parse(Cli.Arg("-streetSunOff", "45"), System.Globalization.CultureInfo.InvariantCulture);

            // the views: the row's four for a row, else the house's, each house at the level its distance takes
            var houses = s.built.Cast<object>().Select(b => Get(b, "house")).ToArray();
            float[] Size(object h) => (float[])Get(h, "size");
            float w = s.row ? s.roots.Select((r, i) => r.transform.position.x + Size(houses[i])[0]).Max() : Size(houses[0])[0];
            float d = houses.Max(h => Size(h)[1]);
            var views = (Array)Call(s.row ? "RowViews" : "Views", w, d);
            var stops = new List<Stop>();
            foreach (var v in views)
            {
                var stop = new Stop
                {
                    name = (string)Get(v, "name"), pos = (Vector3)Get(v, "pos"), target = (Vector3)Get(v, "target"),
                    fov = (float)Get(v, "fov"), floor = (bool)Get(v, "floor"),
                };
                if (!Cli.Wanted("-views", stop.name) || (Cli.Arg("-views", null) == null && Array.IndexOf(JudgingViews, stop.name) < 0))
                    continue;
                string level = (string)Get(v, "level");
                stop.levels = s.built.Cast<object>().Select(b => s.row ? (string)Call("LevelAt", b, stop.pos) : level).ToArray();
                stop.shadowDistance = s.row
                    ? s.built.Cast<object>().Max(b => (float)Call("FarFrom", b, stop.pos)) + 4f
                    : (stop.target - stop.pos).magnitude + 8f;
                stops.Add(stop);
            }
            s.stops = stops.ToArray();
            Debug.Log($"[StreetStaging] {ScenePath}: house{(s.row ? "s" : "")} {string.Join(", ", s.ids)}; views " +
                      $"{string.Join(", ", s.stops.Select(x => x.name))}; lights {string.Join(", ", s.lightNames)}; " +
                      $"the town's light {(s.town != null ? "on" : "off")}");
            return s;
        }

        /// <summary>A light as the street draws it from a view (LT1Street.Run): the street's row over the test's own, the
        /// low sun turned off square for a view that is not the floor's; and the exposure.</summary>
        (object light, float exposure) Lighting(string name, Stop stop)
        {
            var light = lights.Cast<object>().FirstOrDefault(l => (string)Get(l, "name") == name)
                        ?? throw new ArgumentException($"[StreetStaging] no light {name}");
            var own = ownLights?.Cast<object>().FirstOrDefault(e => (string)Get(e, "light") == name);
            var l = own != null ? Call("Own", light, own) : light;
            if (!stop.floor && name == "lowsun")
                Set(l, "azimuth", new Vector2(Mathf.Sin(sunOff * Mathf.Deg2Rad), -Mathf.Cos(sunOff * Mathf.Deg2Rad)));
            return (l, own != null ? (float)Get(own, "exposure") : (float)Get(light, "exposure"));
        }

        /// <summary>The paint's colour for a light, in way Pc (null in way P: the clay).</summary>
        object Colour(string name, string way)
        {
            if (way != "Pc")
                return null;
            var ls = (Array)Get(Get(paint0, "colour"), "lights");
            return ls?.Cast<object>().FirstOrDefault(e => (string)Get(e, "light") == name);
        }

        /// <summary>A light and a view staged as LT1Street.Run stages them: each house's level, the camera, the shadowed
        /// distance, the sun and the trilight, the background, the sky and its reflection, the ground, the exposure, the
        /// materials of the way, and the town's light worked out again. Into <paramref name="cubeFor"/> if given.</summary>
        public void Apply(string lightName, Stop stop, string way = "Pc", Cubemap cubeFor = null)
        {
            for (int i = 0; i < roots.Length; i++)
                foreach (var kv in levels[i])
                    kv.Value.SetActive(kv.Key == stop.levels[i]);
            cam.transform.SetPositionAndRotation(ToUnity(stop.pos), Quaternion.LookRotation(ToUnity(stop.target - stop.pos), Vector3.up));
            cam.fieldOfView = stop.fov;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            urp.shadowCascadeCount = 1;
            urp.mainLightShadowmapResolution = 4096;
            urp.shadowDistance = stop.shadowDistance;
            var (l, exposure) = Lighting(lightName, stop);
            var col = Colour(lightName, way);
            Call("Light", sun, l, col);
            var back = (Color)Static("Back");
            cam.backgroundColor = (Color)Call("Lin", back.linear.r, (float[])Get(col, "background"));
            var c = cubeFor ?? cube;
            RenderSettings.customReflectionTexture = c;
            Call("Sky", sky, skyMat, cam, l, col, c);
            float gy = (float)Call("LToY", Convert.ToSingle(Static("GroundL")));
            groundMat.SetColor("_BaseColor", (Color)Call("Lin", gy, (float[])Get(col, "floor")));
            adjust.postExposure.Override(exposure);
            for (int i = 0; i < roots.Length; i++)
                Call("Assign", levels[i][stop.levels[i]], mats[i], way, (string)Call("MatLevel", stop.levels[i]));
            if (town != null)
                Call("Relight", town, built, sun, l, way, groundMat);
        }

        /// <summary>Every level of every house in a way's materials (the levels a view does not show keep theirs).</summary>
        public void AssignAll(string way = "Pc")
        {
            for (int i = 0; i < roots.Length; i++)
                foreach (var kv in levels[i])
                    Call("Assign", kv.Value, mats[i], way, (string)Call("MatLevel", kv.Key));
        }

        /// <summary>What a renderer of the town is made of in a way, as the town's sky map reads it (LT1Street.TownAlbedo).</summary>
        public (Color wall, Color top) Albedo(Renderer r, string way = "Pc") =>
            ((Color, Color))Call("TownAlbedo", r, built, way, groundMat);

        /// <summary>The pipeline as the street's test draws: the renderer's screen-space occlusion alone, one 4096 cascade,
        /// shaders compiled before they draw; put back when disposed.</summary>
        public static IDisposable Pipeline() => new Restore();

        sealed class Restore : IDisposable
        {
            readonly Dictionary<ScriptableRendererFeature, bool> was;
            readonly (float, int, int) urpWas;
            readonly bool async;

            public Restore()
            {
                var rd = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/Settings/PC_Renderer.asset");
                was = rd.rendererFeatures.Where(f => f != null).ToDictionary(f => f, f => f.isActive);
                foreach (var f in was.Keys)
                    f.SetActive(f.name.Contains("AmbientOcclusion"));
                var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
                urpWas = (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution);
                async = ShaderUtil.allowAsyncCompilation;
                ShaderUtil.allowAsyncCompilation = false;
            }

            public void Dispose()
            {
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
                (urp.shadowDistance, urp.shadowCascadeCount, urp.mainLightShadowmapResolution) = urpWas;
                ShaderUtil.allowAsyncCompilation = async;
                Shader.SetGlobalVector("_OS_StageSky", Vector4.zero);
            }
        }
    }
}
