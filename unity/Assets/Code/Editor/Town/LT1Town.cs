using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Core;
using Overstory.Scenes;
using Path = System.IO.Path;
using Object = UnityEngine.Object;

namespace Overstory.EditorTools.Town
{
    /// <summary>
    /// LT1's harbour town (fixtures/lt1-harbour-town.json, grown by blender/tools/grow_harbour.py), judged from the city
    /// camera (reviews/lt1/town/).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.Town.LT1Town.Grey
    ///         [-out reviews/lt1/town/r01] [-views mid,midhigh,street,roam1,...]
    ///
    /// Grey composes the town in memory as grey masses (the ground carved as the fixture has it, the water, the quay,
    /// each house a body, a roof and a plinth down to its lowest ground) under one grey light, and renders the views.
    /// </summary>
    public static class LT1Town
    {
        public const string Fixture = "fixtures/lt1-harbour-town.json";
        const string LT1 = "Assets/Experiments/LT1";

        // -- the fixture, as JsonUtility reads it (point lists flat) -------------------------------------------------

        [Serializable] public class Grid { public int x0, y0, step, nx, ny; public int[] z; public int[] kind, cover; }
        [Serializable] public class Quay { public int[] edge; public int top, water, row; }
        [Serializable] public class Place { public string id, name; public int z; public int[] points; }
        [Serializable] public class Lane { public string id, name, surface, grain; public int z, width, laid; public int[] points; }
        [Serializable] public class Stair { public string id, name; public int width; public int[] points; }
        [Serializable]
        public class Placement
        {
            public int id, of, x, y, w, d, @base, eave, pitch;
            public float angle;
            public string kind, lane, side, roof;
            public int[] footprint, chimneys;
        }
        [Serializable] public class Tree { public string id, species, crown; public int x, y, z, h, r, planted; }
        [Serializable] public class Pier { public string id, kind; public int width, z; public int[] points; }
        [Serializable] public class Boat { public string id, kind, deck; public int x, y, length, beam; public float angle; }
        [Serializable] public class Stand { public string id; public int planted, h; public int[] points; }
        [Serializable] public class Wall { public string id; public int[] points; }
        [Serializable] public class Fence { public string id, kind; public int height; public int[] points; }
        [Serializable]
        public class Town
        {
            public Quay quay;
            public Lane[] lanes;
            public Stair[] stairs;
            public Placement[] placements;
            public Tree[] trees;
            public Place[] places;
            public Pier[] piers;
            public Boat[] boats;
            public Stand[] stands;
            public Wall[] walls;
            public Fence[] fences;
            public Grid ground, coarse;
        }

        public static Town Load(string repo) =>
            JsonUtility.FromJson<Town>(File.ReadAllText(Path.Combine(repo, Fixture)));

        static Vector3 U(float x, float y, float z) => new Vector3(x, z, y);   // street frame (m) to Unity
        const float M = 0.001f;

        /// <summary>The views: the two city cameras, the street stop and the roam's poses (street frame, m).</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Views =
        {
            ("mid", new Vector3(55f, -115f, 46f), new Vector3(58f, 45f, 15f), 42f),
            ("midhigh", new Vector3(52f, -150f, 75f), new Vector3(55f, 30f, 4f), 42f),
            // the street stop: on Harbour Row at the gully's foot, three metres up, into the Gully Steps
            ("street", new Vector3(47f, -14f, 3.2f), new Vector3(50f, 30f, 9f), 46.4f),
            // the roam: the free camera over the harbour's west end, over the east roofs, and down from the heath
            ("roam1", new Vector3(-40f, -70f, 28f), new Vector3(40f, 40f, 10f), 42f),
            ("roam2", new Vector3(150f, -40f, 34f), new Vector3(60f, 50f, 14f), 42f),
            ("roam3", new Vector3(70f, 150f, 70f), new Vector3(55f, 0f, 0f), 42f),
        };

        public static void Grey() => Render(null);

        /// <summary>The town in its colours from the pack (packs/stavanger-1989/town.json and the paints and materials it
        /// names) under one of the light rigs (-moment, the 17:50 sea fog by default), lit and aired by the street's own
        /// stage (Scenes/StreetStage.cs) through Shaders/Town.shader. Several moments, comma-separated, render in one run.</summary>
        public static void Light() => Render(Cli.Arg("-moment", "1750-sea-fog"));

        static void Render(string moment)
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string dir = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/town/r01"));
            Directory.CreateDirectory(dir);
            var town = Load(repo);
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var made = new List<Object>();
            var root = new GameObject(moment == null ? "Town (grey)" : "Town");
            var tones = moment == null ? null : new Tones(Path.Combine(repo, "packs", "stavanger-1989"), town);

            var lit = Shader.Find("Universal Render Pipeline/Lit");
            var townShader = Shader.Find("Overstory/Town");
            var cache = new Dictionary<string, Material>();
            // grey: a URP Lit grey of value v; light: the town shader in colour c (sRGB), tinted by the vertex colours
            Material Mat(float v, Color c, bool tinted = false, float porosity = 0.5f, float smooth = 0.06f, float ground = 0.35f)
            {
                string key = moment == null ? $"g{v}" : $"{ColorUtility.ToHtmlStringRGB(c)}{tinted}{porosity}{smooth}{ground}";
                if (cache.TryGetValue(key, out var hit))
                    return hit;
                Material m;
                if (moment == null)
                {
                    m = new Material(lit) { hideFlags = HideFlags.DontSave };
                    m.SetColor("_BaseColor", new Color(v, v, v));
                    m.SetFloat("_Smoothness", 0.05f);
                }
                else
                {
                    m = new Material(townShader) { hideFlags = HideFlags.DontSave };
                    m.SetColor("_BaseColor", c);
                    m.SetFloat("_Tinted", tinted ? 1f : 0f);
                    m.SetFloat("_Porosity", porosity);
                    m.SetFloat("_Smoothness", smooth);
                    m.SetFloat("_Ground", ground);
                }
                made.Add(m);
                return cache[key] = m;
            }
            var white = Color.white;
            var ground = Mat(0.42f, tones?.land ?? white);
            Material covered;
            if (moment == null)
            {
                // the town's ground takes its tone from its cover, in its vertex colours
                covered = new Material(Shader.Find("Universal Render Pipeline/Particles/Lit")) { hideFlags = HideFlags.DontSave };
                covered.SetColor("_BaseColor", Color.white);
                covered.SetFloat("_Smoothness", 0.05f);
                made.Add(covered);
            }
            else
                covered = Mat(0f, white, tinted: true, porosity: 0.8f, smooth: 0.04f);
            var paved = Mat(0.47f, white, tinted: true, porosity: 0.45f, smooth: 0.12f);
            var water = moment == null ? Mat(0.30f, white) : AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Water.mat");
            var fenceM = Mat(0.70f, tones?.fence ?? white, porosity: 0.2f, smooth: 0.15f);
            var plinth = Mat(0.36f, tones?.stone ?? white, porosity: 0.6f, smooth: 0.08f);
            var crown = Mat(0.34f, white, tinted: true, porosity: 0.3f, smooth: 0.08f, ground: 0.2f);
            var standM = Mat(0.34f, tones?.stand ?? white, porosity: 0.3f, smooth: 0.08f, ground: 0.2f);
            var trunk = Mat(0.26f, tones?.trunk ?? white, porosity: 0.6f);
            var timber = Mat(0.40f, tones?.timber ?? white, porosity: 0.7f);
            var hull = Mat(0.62f, white, tinted: true, porosity: 0.1f, smooth: 0.35f);

            Add(root, "ground", GroundMesh(town.ground, true, tones), town.ground.cover != null ? covered : ground, made);
            Add(root, "paving", Paving(town, tones), paved, made);
            Add(root, "land", GroundMesh(town.coarse, false, null), ground, made);
            Add(root, "water", Plane(-1600f, -1400f, 1700f, 1900f, town.quay.water * M), water, made);
            Add(root, "quay wall", QuayWall(town.quay), plinth, made);
            if (town.walls != null)
                Add(root, "walls", Walls(town.walls), plinth, made);
            if (town.fences != null)
                Add(root, "fences", Fences(town.fences, town.ground), fenceM, made);
            if (town.piers != null)
            {
                var (stone, deck) = Piers(town.piers, town.quay);
                Add(root, "piers", stone, plinth, made);
                Add(root, "jetties", deck, timber, made);
            }
            if (town.boats != null)
                Add(root, "boats", Boats(town.boats, town.quay.water * M, tones), hull, made);
            if (town.trees != null && town.trees.Length > 0)
            {
                var (crowns, trunks) = Trees(town.trees, tones);
                Add(root, "tree crowns", crowns, crown, made);
                Add(root, "tree trunks", trunks, trunk, made);
            }
            if (town.stands != null)
                Add(root, "stands", Stands(town.stands, town.ground), standM, made);
            var houses = new GameObject("houses");
            houses.transform.SetParent(root.transform, false);
            foreach (var p in town.placements)
            {
                var (body, roof, foot) = Masses(p, town.ground);
                Add(houses, $"house {p.id}", body, Mat(0.55f, tones?.Body(p) ?? white, porosity: 0.15f, smooth: 0.1f), made);
                Add(houses, $"house {p.id} roof", roof, Mat(0.30f, tones?.Roof(p) ?? white, porosity: 0.35f, smooth: 0.12f), made);
                Add(houses, $"house {p.id} plinth", foot, plinth, made);
            }

            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.allowMSAA = true;
            var data = camGo.AddComponent<UniversalAdditionalCameraData>();
            data.renderShadows = true;
            if (GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
                urp.shadowDistance = 600f;
            var sun = new GameObject("Sun").AddComponent<UnityEngine.Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            StreetStage stage = null;
            if (moment == null)
            {
                // one grey light: the sky from above, a low key from the west
                sun.intensity = 1.1f;
                sun.color = Color.white;
                sun.transform.rotation = Quaternion.LookRotation(U(0.55f, 0.35f, -0.55f).normalized, Vector3.up);
                RenderSettings.ambientMode = AmbientMode.Trilight;
                RenderSettings.ambientSkyColor = new Color(0.55f, 0.55f, 0.55f);
                RenderSettings.ambientEquatorColor = new Color(0.42f, 0.42f, 0.42f);
                RenderSettings.ambientGroundColor = new Color(0.2f, 0.2f, 0.2f);
                RenderSettings.fog = true;
                RenderSettings.fogMode = FogMode.Linear;
                RenderSettings.fogColor = new Color(0.78f, 0.78f, 0.78f);
                RenderSettings.fogStartDistance = 120f;
                RenderSettings.fogEndDistance = 1400f;
                RenderSettings.skybox = null;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(0.8f, 0.8f, 0.8f);
            }
            else
            {
                // the street's own stage: the rig's sun, sky, ambient, air and grade, the game's style, the painted look
                var volume = new GameObject("Grade").AddComponent<Volume>();
                volume.isGlobal = true;
                var probe = new GameObject("Sky reflection").AddComponent<ReflectionProbe>();
                probe.transform.position = U(60f, 60f, 20f);
                probe.size = new Vector3(2000f, 600f, 2000f);
                stage = new GameObject("Stage").AddComponent<StreetStage>();
                stage.enabled = false;
                stage.sun = sun;
                stage.view = cam;
                stage.volume = volume;
                stage.sky = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Sky.mat");
                stage.skyReflection = probe;
                stage.paletteAlbedo = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Palette/palette_albedo.png");
                stage.paletteEmit = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Palette/palette_emit.png");
                stage.paletteGlow = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Palette/palette_glow.png");
                stage.paletteSurface = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Palette/palette_surface.png");
                stage.style = AssetDatabase.LoadAssetAtPath<Style>($"{LT1}/Heart/Light/Styles/{Cli.Arg("-style", "Style_game")}.asset");
                stage.look = "P";
                cam.clearFlags = CameraClearFlags.Skybox;
                data.dithering = true;
            }

            foreach (var m in moment == null ? new[] { "grey" } : moment.Split(','))
            {
                if (stage != null)
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{LT1}/Heart/Light/Heart_{m}.asset")
                        ?? throw new FileNotFoundException($"no light rig Heart_{m}");
                foreach (var v in Views)
                {
                    if (!Cli.Wanted("-views", v.name))
                        continue;
                    Vector3 p = U(v.pos.x, v.pos.y, v.pos.z), t = U(v.target.x, v.target.y, v.target.z);
                    cam.transform.SetPositionAndRotation(p, Quaternion.LookRotation(t - p, Vector3.up));
                    cam.fieldOfView = v.fov;
                    cam.nearClipPlane = 0.3f;
                    cam.farClipPlane = 6000f;
                    if (stage != null)
                        stage.Apply();
                    string file = Path.Combine(dir, $"{v.name}-{m}.png");
                    LT1Render.Still(cam, file, grey: false, msaa: 4);
                    Debug.Log($"[LT1Town] {file}");
                }
            }
            foreach (var o in made)
                if (!AssetDatabase.Contains(o))
                    Object.DestroyImmediate(o);
        }

        // -- the town's colours from the pack (Light) ----------------------------------------------------------------------

        /// <summary>Each thing's colour at the city tier, from the pack: town.json for the cover, crowns, surfaces and boats,
        /// and which paints and roofs the houses take; paint.json for the paints by period and scheme; materials/*.json
        /// for the roofs, stone and timber. Every colour is sRGB as the records hold it. Nothing here holds a colour.</summary>
        class Tones
        {
            public readonly Color[] cover;
            public readonly float[] spread;
            public readonly Color land, stand, trunk, fence, stone, timber;
            readonly Dictionary<string, Color[]> crowns = new Dictionary<string, Color[]>();
            readonly Dictionary<string, Color> surfaces = new Dictionary<string, Color>();
            readonly Color[] boats;
            readonly Dictionary<string, object> paint, schemeOf, town;
            readonly Dictionary<string, Color> paints = new Dictionary<string, Color>();
            readonly Dictionary<int, Dictionary<string, object>> diaries = new Dictionary<int, Dictionary<string, object>>();
            readonly Dictionary<string, string> grain = new Dictionary<string, string>();
            readonly string pack;
            const int Year = 1989;

            static Color Hex(string h) => ColorUtility.TryParseHtmlString("#" + h, out var c) ? c : throw new FormatException($"not a colour: {h}");
            static Dictionary<string, object> Obj(object o) => (Dictionary<string, object>)o;
            static List<object> Arr(object o) => (List<object>)o;
            Dictionary<string, object> Read(string name) => Obj(R2aPatches.Json.Parse(File.ReadAllText(Path.Combine(pack, name))));

            public Tones(string pack, Town t)
            {
                this.pack = pack;
                town = Read("town.json");
                paint = Read("paint.json");
                foreach (var kv in Obj(paint["colours"]))
                    paints[kv.Key] = Hex((string)Obj(kv.Value)["srgb"]);
                paints["soil"] = Hex((string)Obj(paint["soil"])["srgb"]);
                var names = new List<string>(Obj(town["cover"]).Keys);
                cover = new Color[names.Count];
                spread = new float[names.Count];
                // in the order the fixture's cover codes count them (grow_harbour.py, COVER)
                for (int i = 0; i < names.Count; i++)
                {
                    var c = Obj(Obj(town["cover"])[names[i]]);
                    cover[i] = Hex((string)c["srgb"]);
                    spread[i] = (float)(double)c["spread"];
                }
                land = Hex((string)town["land"]);
                stand = Hex((string)town["stand"]);
                trunk = Hex((string)town["trunk"]);
                fence = paints[(string)town["fences"]];
                stone = Hex((string)Read("materials/fieldstone.json")["srgb"]);
                timber = Hex((string)Read("materials/pine.json")["srgbWeathered"]);
                foreach (var kv in Obj(town["crowns"]))
                    crowns[kv.Key] = Arr(kv.Value).ConvertAll(o => Hex((string)o)).ToArray();
                foreach (var kv in Obj(town["surfaces"]))
                    surfaces[kv.Key] = Hex((string)kv.Value);
                boats = Arr(town["boats"]).ConvertAll(o => paints[(string)o]).ToArray();
                var scheme = Obj(town["scheme"]);
                foreach (var o in Arr(paint["schemes"]))
                    if ((string)Obj(o)["name"] == (string)scheme["name"])
                        schemeOf = Obj(o);
                // the buildings' diaries, by id, and each lane's grain
                var json = Obj(R2aPatches.Json.Parse(File.ReadAllText(Path.Combine(Path.GetDirectoryName(Path.GetDirectoryName(pack)), Fixture))));
                foreach (var b in Arr(json["buildings"]))
                    diaries[(int)(double)Obj(b)["id"]] = Obj(b);
                foreach (var l in t.lanes)
                    grain[l.id] = l.grain;
            }

            ulong Seed(int id, string what) => Hash.Then(Hash.Of($"town.{id}"), what);
            T Pick<T>(IList<T> from, ulong h) => from[Hash.Index(h, from.Count)];

            Dictionary<string, object> Diary(Placement p) =>
                diaries.TryGetValue(p.id, out var d) ? d : diaries.TryGetValue(p.of, out d) ? d : null;

            /// <summary>The year of the last event of these kinds in a diary, or 0.</summary>
            static int Last(Dictionary<string, object> d, params string[] kinds)
            {
                int y = 0;
                if (d != null)
                    foreach (var e in Arr(d["events"]))
                        if (Array.IndexOf(kinds, (string)Obj(e)["kind"]) >= 0)
                            y = Mathf.Max(y, (int)(double)Obj(e)["year"]);
                return y;
            }

            Dictionary<string, object> Period(int year)
            {
                foreach (var o in Arr(paint["periods"]))
                {
                    var q = Obj(o);
                    if (year >= (double)q["from"] && year < (double)q["to"])
                        return q;
                }
                throw new ArgumentException($"no paint period for {year}");
            }

            /// <summary>A body's paint: the old town's white where the scheme holds (town.json, scheme), a warehouse's or an
            /// outhouse's the back-of-house paints of its period, any other the bodies of the period of its last painting;
            /// a house left to decline since then goes part way to the soil's colour.</summary>
            public Color Body(Placement p)
            {
                var d = Diary(p);
                int painted = Last(d, "built", "repainted");
                var period = Period(painted > 0 ? painted : 1900);
                var scheme = Obj(town["scheme"]);
                string g = p.lane != null && grain.TryGetValue(p.lane, out var gg) ? gg : null;
                bool kept = schemeOf != null && Year >= (double)schemeOf["from"]
                    && (g != null && Arr(scheme["grains"]).Contains(g) || scheme.TryGetValue("kinds", out var k) && Arr(k).Contains(p.kind));
                object list;
                if ((p.kind == "warehouse" || p.kind == "outhouse") && period["back"] != null)
                    list = period["back"];
                else if (kept)
                    list = schemeOf["body"];
                else
                    list = period["body"];
                int id = d != null ? (int)(double)d["id"] : p.id;
                var c = paints[(string)Pick(Arr(list), Seed(id, p.kind == "outhouse" ? "back" : "body"))];
                if (Last(d, "neglected") > painted)
                {
                    var n = Obj(town["neglect"]);
                    c = Color.Lerp(c, paints[(string)n["toward"]], (float)(double)n["share"]);
                }
                return c;
            }

            /// <summary>A roof's covering by the year it was laid (town.json, roofs), weathered from new to old over its
            /// record's years (materials/*.json, oldYears).</summary>
            public Color Roof(Placement p)
            {
                var d = Diary(p);
                int built = Mathf.Max(Last(d, "built"), 1);
                int laid = Mathf.Max(built, Last(d, "roof_retiled"));
                string material = null;
                foreach (var o in Arr(town["roofs"]))
                    if (built < (double)Obj(o)["to"]) { material = (string)Obj(o)["material"]; break; }
                var rec = Read($"materials/{material}.json");
                float age = Mathf.Clamp01((Year - laid) / (float)(double)rec["oldYears"]);
                var c = Color.Lerp(Hex((string)rec["srgbNew"]), Hex((string)rec["srgbOld"]), age);
                // one roof a little apart from the next, claiming nothing
                return c * Hash.Range(Seed(p.id, "roof"), 0.93f, 1.07f);
            }

            public Color Crown(Tree t) =>
                crowns.TryGetValue(t.species, out var c) ? Pick(c, Hash.Of($"town.crown.{t.id}")) : stand;

            public Color Surface(string name) => surfaces.TryGetValue(name, out var c) ? c : surfaces["setts"];

            public Color Boat(Boat b) => Pick(boats, Hash.Of($"town.boat.{b.id}"));
        }

        static void Add(GameObject parent, string name, Mesh mesh, Material mat, List<Object> made)
        {
            made.Add(mesh);
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = mat;
        }

        // -- the ground ------------------------------------------------------------------------------------------------

        public static float GroundAt(Grid g, float x, float y)
        {
            float fx = (x - g.x0 * M) / (g.step * M), fy = (y - g.y0 * M) / (g.step * M);
            int i = Mathf.Clamp(Mathf.FloorToInt(fx), 0, g.nx - 2), j = Mathf.Clamp(Mathf.FloorToInt(fy), 0, g.ny - 2);
            float tx = Mathf.Clamp01(fx - i), ty = Mathf.Clamp01(fy - j);
            float a = Mathf.Lerp(g.z[j * g.nx + i], g.z[j * g.nx + i + 1], tx);
            float b = Mathf.Lerp(g.z[(j + 1) * g.nx + i], g.z[(j + 1) * g.nx + i + 1], tx);
            return Mathf.Lerp(a, b, ty) * M;
        }

        static Mesh GroundMesh(Grid g, bool fine, Tones tones)
        {
            var v = new Vector3[g.nx * g.ny];
            for (int j = 0; j < g.ny; j++)
                for (int i = 0; i < g.nx; i++)
                    v[j * g.nx + i] = U((g.x0 + i * g.step) * M, (g.y0 + j * g.step) * M, g.z[j * g.nx + i] * M);
            var t = new int[(g.nx - 1) * (g.ny - 1) * 6];
            int k = 0;
            for (int j = 0; j < g.ny - 1; j++)
                for (int i = 0; i < g.nx - 1; i++)
                {
                    int a = j * g.nx + i, b = a + 1, c = a + g.nx, d = c + 1;
                    // street frame to Unity mirrors: wind so the faces look up
                    t[k++] = a; t[k++] = c; t[k++] = b;
                    t[k++] = b; t[k++] = c; t[k++] = d;
                }
            var m = new Mesh { name = fine ? "town ground" : "land", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            m.vertices = v;
            m.triangles = t;
            if (fine && g.cover != null && g.cover.Length == v.Length)
            {
                // grass, garden, heath, rock, forest floor, made: a tone each, and how far its patches swing it
                float[] tone = { 0.43f, 0.48f, 0.33f, 0.52f, 0.24f, 0.40f };
                float[] swing = { 0.05f, 0.03f, 0.09f, 0.08f, 0.04f, 0.02f };
                var col = new Color[v.Length];
                for (int i = 0; i < v.Length; i++)
                {
                    int c = Mathf.Clamp(g.cover[i] / 16, 0, tone.Length - 1);
                    float patch = g.cover[i] % 16 / 15f - 0.5f;
                    float val = tone[c] + patch * swing[c];
                    var cc = tones == null ? new Color(val, val, val, 1f) : tones.cover[c] * (1f + 2f * patch * tones.spread[c]);
                    cc.a = 1f;
                    col[i] = cc.linear;   // vertex colours are not converted as a material's are
                }
                m.colors = col;
            }
            m.RecalculateNormals();
            m.RecalculateBounds();
            return m;
        }

        static Mesh Plane(float x0, float y0, float x1, float y1, float z)
        {
            var m = new Mesh { name = "plane", hideFlags = HideFlags.DontSave };
            m.vertices = new[] { U(x0, y0, z), U(x1, y0, z), U(x0, y1, z), U(x1, y1, z) };
            m.triangles = new[] { 0, 2, 1, 1, 2, 3 };
            m.RecalculateNormals();
            return m;
        }

        /// <summary>The quay's face, set a metre out from its edge, and its coping: a strip from the face to two metres in,
        /// a hair above the quay, which covers the ground grid's step down to the sea bed.</summary>
        static Mesh QuayWall(Quay q)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            float top = q.top * M, foot = q.water * M - 2.5f;
            int count = q.edge.Length / 2;
            Vector2 E(int i) => new Vector2(q.edge[2 * i] * M, q.edge[2 * i + 1] * M);
            Vector2 Out(int i)
            {
                var d = E(Mathf.Min(i + 1, count - 1)) - E(Mathf.Max(i - 1, 0));
                return new Vector2(d.y, -d.x).normalized;      // seaward: the right of the edge's run east
            }
            for (int i = 0; i + 1 < count; i++)
            {
                Vector2 a = E(i) + Out(i) * 1.0f, b = E(i + 1) + Out(i + 1) * 1.0f;
                Vector2 ai = E(i) - Out(i) * 2.0f, bi = E(i + 1) - Out(i + 1) * 2.0f;
                int n = v.Count;
                v.Add(U(a.x, a.y, top)); v.Add(U(b.x, b.y, top)); v.Add(U(a.x, a.y, foot)); v.Add(U(b.x, b.y, foot));
                t.AddRange(new[] { n, n + 1, n + 2, n + 1, n + 3, n + 2 });
                n = v.Count;
                v.Add(U(a.x, a.y, top + 0.03f)); v.Add(U(b.x, b.y, top + 0.03f)); v.Add(U(ai.x, ai.y, top + 0.03f)); v.Add(U(bi.x, bi.y, top + 0.03f));
                t.AddRange(new[] { n, n + 2, n + 1, n + 1, n + 2, n + 3 });
            }
            var m = new Mesh { name = "quay wall", hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        // -- paving: the Row, the lanes and the level places as their own surfaces, a few centimetres over the ground ----

        static Mesh Paving(Town town, Tones tones)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            var col = new List<Color>();
            Color tint = Color.white;
            void Tint(string surface) => tint = tones == null ? Color.white : tones.Surface(surface).linear;
            void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { int n = v.Count; v.Add(a); v.Add(b); v.Add(c); v.Add(d); t.AddRange(new[] { n, n + 2, n + 1, n + 1, n + 2, n + 3 }); for (int k = 0; k < 4; k++) col.Add(tint); }
            // a strip along a polyline (x, y, z), its sides hw out, its normal in plan from the neighbouring points
            void Strip(IList<Vector3> pts, float hwL, float hwR, float lift)
            {
                Vector2 Side(int i)
                {
                    var d = (Vector2)(pts[Mathf.Min(i + 1, pts.Count - 1)] - pts[Mathf.Max(i - 1, 0)]);
                    return new Vector2(-d.y, d.x).normalized;   // the left of the run
                }
                for (int i = 0; i + 1 < pts.Count; i++)
                {
                    Vector3 a = pts[i], b = pts[i + 1];
                    Vector2 sa = Side(i), sb = Side(i + 1);
                    Quad(U(a.x - sa.x * hwR, a.y - sa.y * hwR, a.z + lift), U(b.x - sb.x * hwR, b.y - sb.y * hwR, b.z + lift),
                         U(a.x + sa.x * hwL, a.y + sa.y * hwL, a.z + lift), U(b.x + sb.x * hwL, b.y + sb.y * hwL, b.z + lift));
                }
            }
            // the Row: from the quay's edge to the building line
            var edge = new List<Vector3>();
            for (int i = 0; i + 1 < town.quay.edge.Length; i += 2)
                edge.Add(new Vector3(town.quay.edge[i] * M, town.quay.edge[i + 1] * M, town.quay.top * M));
            Tint("row");
            Strip(edge, town.quay.row * M + 0.3f, 0f, 0.02f);
            foreach (var l in town.lanes)
            {
                var pts = new List<Vector3>();
                for (int i = 0; i + 2 < l.points.Length; i += 3)
                    pts.Add(new Vector3(l.points[i] * M, l.points[i + 1] * M, l.points[i + 2] * M));
                Tint(l.surface);
                Strip(pts, l.width * M / 2, l.width * M / 2, 0.04f);
            }
            if (town.places != null)
                foreach (var pl in town.places)
                {
                    var q = new Vector2[pl.points.Length / 2];
                    for (int i = 0; i < q.Length; i++)
                        q[i] = new Vector2(pl.points[2 * i] * M, pl.points[2 * i + 1] * M);
                    float z = pl.z * M + 0.05f;
                    Tint(pl.id);
                    for (int i = 1; i + 1 < q.Length; i++)
                    {
                        int n = v.Count;
                        v.Add(U(q[0].x, q[0].y, z)); v.Add(U(q[i].x, q[i].y, z)); v.Add(U(q[i + 1].x, q[i + 1].y, z));
                        t.AddRange(new[] { n, n + 1, n + 2 });
                        col.Add(tint); col.Add(tint); col.Add(tint);
                    }
                }
            var m = new Mesh { name = "paving", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetColors(col);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        // -- trees: a crown by its kind and a trunk, all in two meshes -------------------------------------------------

        /// <summary>A crown's blob: rings of seven between a bottom and a top point, its radius at each height from prof
        /// (0 at the bottom, 1 at the top), in plan an ellipse rx by ry turned by rot.</summary>
        static void Blob(List<Vector3> cv, List<int> ct, float x, float y, float z0, float z1, float rx, float ry, float rot,
                         Func<float, float> prof)
        {
            const int seg = 7, rings = 6;
            int n0 = cv.Count;
            cv.Add(U(x, y, z0 + (z1 - z0) * 0.6f * prof(0.05f) / rings));   // the underside nearly flat where the profile is full low
            for (int k = 1; k < rings; k++)
            {
                float u = k / (float)rings, f = prof(u);
                for (int s = 0; s < seg; s++)
                {
                    float a = rot + s * Mathf.PI * 2f / seg;
                    float ca = Mathf.Cos(a) * rx * f, sa = Mathf.Sin(a) * ry * f;
                    cv.Add(U(x + ca * Mathf.Cos(rot) - sa * Mathf.Sin(rot), y + ca * Mathf.Sin(rot) + sa * Mathf.Cos(rot),
                             z0 + (z1 - z0) * u));
                }
            }
            cv.Add(U(x, y, z1));
            int top = cv.Count - 1;
            for (int s = 0; s < seg; s++)
            {
                int s1 = (s + 1) % seg;
                ct.AddRange(new[] { n0, n0 + 1 + s1, n0 + 1 + s });
                for (int k = 0; k < rings - 2; k++)
                {
                    int a = n0 + 1 + k * seg + s, b = n0 + 1 + k * seg + s1, c = a + seg, d = b + seg;
                    ct.AddRange(new[] { a, b, c, b, d, c });
                }
                int l = n0 + 1 + (rings - 2) * seg;
                ct.AddRange(new[] { l + s, l + s1, top });
            }
        }

        static (Mesh crowns, Mesh trunks) Trees(Tree[] trees, Tones tones)
        {
            var cv = new List<Vector3>();
            var ct = new List<int>();
            var cc = new List<Color>();
            var tv = new List<Vector3>();
            var tt = new List<int>();
            // a broadleaf crown is full low and rounds over at the top; a spruce is a spire
            Func<float, float> round = u => Mathf.Sqrt(Mathf.Sin(Mathf.PI * Mathf.Pow(u, 0.8f)));
            Func<float, float> cone = u => Mathf.Min(1f, u / 0.12f) * Mathf.Pow(1f - u, 0.95f);
            foreach (var tr in trees)
            {
                float x = tr.x * M, y = tr.y * M, z = tr.z * M, h = tr.h * M, r = tr.r * M;
                float R(string what, int k, float lo, float hi) => Hash.Range(Hash.Then(Hash.Then(Hash.Of(tr.id), what), (ulong)k), lo, hi);
                float rot = R("turn", 0, 0f, Mathf.PI * 2f);
                float c0;
                switch (tr.crown)
                {
                    case "cone":
                        c0 = 0.04f * h;
                        Blob(cv, ct, x, y, z + c0, z + h, r, r, rot, cone);
                        break;
                    case "tall":
                        // a birch: one tall crown with a lobe off it
                        c0 = 0.3f * h;
                        Blob(cv, ct, x, y, z + c0, z + h, r, r * R("ry", 0, 0.8f, 1f), rot, round);
                        {
                            float a = R("lobe", 0, 0f, 6.28f), off = r * R("off", 0, 0.35f, 0.55f);
                            Blob(cv, ct, x + Mathf.Cos(a) * off, y + Mathf.Sin(a) * off, z + c0 + (h - c0) * 0.1f,
                                 z + c0 + (h - c0) * R("lt", 0, 0.55f, 0.75f), r * 0.6f, r * 0.55f, rot, round);
                        }
                        break;
                    case "flat":
                        // a pine: a bare trunk, an open crown of three masses, the top one widest, leaning with the wind
                        c0 = 0.38f * h;
                        for (int k = 0; k < 3; k++)
                        {
                            float a = rot + k * 2.1f + R("a", k, -0.4f, 0.4f), off = k == 0 ? r * 0.15f : r * R("off", k, 0.3f, 0.5f);
                            float zb = z + c0 + (h - c0) * (k == 0 ? 0.3f : R("zb", k, 0f, 0.35f));
                            Blob(cv, ct, x + Mathf.Cos(a) * off, y + Mathf.Sin(a) * off, zb, zb + (h - c0) * R("hz", k, 0.55f, 0.7f),
                                 r * (k == 0 ? 0.85f : R("rk", k, 0.55f, 0.7f)), r * R("ryk", k, 0.5f, 0.7f), a, round);
                        }
                        break;
                    default:
                        // a sycamore, rowan or apple: a domed crown with two lobes, so its outline is a cloud, not a ball
                        c0 = Mathf.Max(1.6f, 0.25f * h);
                        Blob(cv, ct, x, y, z + c0, z + h, r * 0.85f, r * R("ry", 0, 0.75f, 0.9f), rot, round);
                        for (int k = 0; k < 2; k++)
                        {
                            float a = rot + k * 2.6f + R("a", k, -0.5f, 0.5f), off = r * R("off", k, 0.4f, 0.55f);
                            float zb = z + c0 + (h - c0) * R("zb", k, 0.05f, 0.25f);
                            Blob(cv, ct, x + Mathf.Cos(a) * off, y + Mathf.Sin(a) * off, zb, zb + (h - c0) * R("hz", k, 0.5f, 0.7f),
                                 r * R("rk", k, 0.5f, 0.65f), r * R("ryk", k, 0.45f, 0.6f), a, round);
                        }
                        break;
                }
                var tint = tones == null ? Color.white : tones.Crown(tr).linear;
                while (cc.Count < cv.Count)
                    cc.Add(tint);
                // the trunk: a square post from below the ground into the crown
                float tw = Mathf.Clamp(h * 0.025f, 0.12f, 0.4f);
                var post = Prism(new[] { new Vector2(x - tw, y - tw), new Vector2(x + tw, y - tw), new Vector2(x + tw, y + tw), new Vector2(x - tw, y + tw) }, z - 1f, z + c0 + (h - c0) * 0.3f);
                int m0 = tv.Count;
                tv.AddRange(post.vertices);
                foreach (var i in post.triangles)
                    tt.Add(m0 + i);
                Object.DestroyImmediate(post);
            }
            // the crowns were wound counterclockwise seen from outside in the street frame, which the mirror into
            // Unity turns inwards: flip them
            for (int i = 0; i < ct.Count; i += 3)
                (ct[i + 1], ct[i + 2]) = (ct[i + 2], ct[i + 1]);
            Mesh Make(string name, List<Vector3> v, List<int> t, List<Color> c)
            {
                var m = new Mesh { name = name, indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
                m.SetVertices(v);
                if (c != null)
                    m.SetColors(c);
                m.SetTriangles(t, 0);
                m.RecalculateNormals();
                return m;
            }
            // faceted planes, never a sphere's normals (reviews/lt1/town/method.md): each face its own three vertices
            var fv = new List<Vector3>(ct.Count);
            var fc = new List<Color>(ct.Count);
            var ft = new List<int>(ct.Count);
            for (int i = 0; i < ct.Count; i++)
            {
                fv.Add(cv[ct[i]]);
                fc.Add(cc[ct[i]]);
                ft.Add(i);
            }
            return (Make("tree crowns", fv, ft, fc), Make("tree trunks", tv, tt, null));
        }

        /// <summary>The spruce stands' closed canopy: where the rows have grown together, one rough surface at a little
        /// over half the trees' height, its sides down to the ground; the spires stand out of it.</summary>
        static Mesh Stands(Stand[] stands, Grid g)
        {
            var mb = new MB();
            float gx0 = g.x0 * M, gy0 = g.y0 * M, gx1 = (g.x0 + (g.nx - 1) * g.step) * M, gy1 = (g.y0 + (g.ny - 1) * g.step) * M;
            foreach (var st in stands)
            {
                var q = new Vector2[4];
                for (int i = 0; i < 4; i++)
                    q[i] = new Vector2(st.points[2 * i] * M, st.points[2 * i + 1] * M);
                float h = st.h * M;
                int nu = Mathf.CeilToInt(Vector2.Distance(q[0], q[1]) / 4f), nv = Mathf.CeilToInt(Vector2.Distance(q[0], q[3]) / 4f);
                // inset a little, so the edge trees stand clear of it with their lower branches
                Vector2 Q(float a, float b)
                {
                    a = Mathf.Lerp(0.04f, 0.96f, a); b = Mathf.Lerp(0.04f, 0.96f, b);
                    return Vector2.Lerp(Vector2.Lerp(q[0], q[1], a), Vector2.Lerp(q[3], q[2], a), b);
                }
                bool In(Vector2 p) => p.x > gx0 + 1f && p.x < gx1 - 1f && p.y > gy0 + 1f && p.y < gy1 - 1f;
                Vector3 Top(int i, int j)
                {
                    var p = Q(i / (float)nu, j / (float)nv);
                    float rough = Hash.Range(Hash.Then(Hash.Then(Hash.Of(st.id), (ulong)i), (ulong)j), -0.1f, 0.1f) * h;
                    return U(p.x, p.y, GroundAt(g, p.x, p.y) + 0.62f * h + rough);
                }
                Vector3 Foot(int i, int j) { var p = Q(i / (float)nu, j / (float)nv); return U(p.x, p.y, GroundAt(g, p.x, p.y) - 0.5f); }
                for (int j = 0; j < nv; j++)
                    for (int i = 0; i < nu; i++)
                        if (In(Q((i + 0.5f) / nu, (j + 0.5f) / nv)))
                            mb.Quad(Top(i, j), Top(i + 1, j), Top(i + 1, j + 1), Top(i, j + 1));
                for (int i = 0; i < nu; i++)
                {
                    if (In(Q((i + 0.5f) / nu, 0f))) mb.Quad(Foot(i, 0), Foot(i + 1, 0), Top(i + 1, 0), Top(i, 0));
                    if (In(Q((i + 0.5f) / nu, 1f))) mb.Quad(Foot(i, nv), Foot(i + 1, nv), Top(i + 1, nv), Top(i, nv));
                }
                for (int j = 0; j < nv; j++)
                {
                    if (In(Q(0f, (j + 0.5f) / nv))) mb.Quad(Foot(0, j), Foot(0, j + 1), Top(0, j + 1), Top(0, j));
                    if (In(Q(1f, (j + 0.5f) / nv))) mb.Quad(Foot(nu, j), Foot(nu, j + 1), Top(nu, j + 1), Top(nu, j));
                }
            }
            return mb.Make("stands");
        }

        // -- made things on the ground and the water ------------------------------------------------------------------

        /// <summary>A greybox mesh builder: quads and other meshes gathered into one, every face from both sides.</summary>
        class MB
        {
            public readonly List<Vector3> v = new List<Vector3>();
            public readonly List<int> t = new List<int>();
            readonly List<Color> col = new List<Color>();
            /// <summary>The vertex colour (linear) of what is added from here on.</summary>
            public Color tint = Color.white;
            void Fill() { while (col.Count < v.Count) col.Add(tint); }
            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { int n = v.Count; v.Add(a); v.Add(b); v.Add(c); v.Add(d); t.AddRange(new[] { n, n + 2, n + 1, n, n + 3, n + 2 }); Fill(); }
            public void Tri(Vector3 a, Vector3 b, Vector3 c) { int n = v.Count; v.Add(a); v.Add(b); v.Add(c); t.AddRange(new[] { n, n + 2, n + 1 }); Fill(); }
            public void Add(Mesh m)
            {
                int n = v.Count;
                v.AddRange(m.vertices);
                foreach (var i in m.triangles)
                    t.Add(n + i);
                Fill();
                Object.DestroyImmediate(m);
            }
            public Mesh Make(string name)
            {
                var m = new Mesh { name = name, indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
                m.SetVertices(v);
                m.SetColors(col);
                m.SetTriangles(t, 0);
                m.RecalculateNormals();
                DoubleSided(m);
                return m;
            }
        }

        /// <summary>The fences: a panel from the ground to its height along each run, a post at each end.</summary>
        static Mesh Fences(Fence[] fences, Grid g)
        {
            var mb = new MB();
            foreach (var f in fences)
            {
                float h = f.height * M;
                for (int i = 0; i + 3 < f.points.Length; i += 2)
                {
                    Vector2 a = new Vector2(f.points[i], f.points[i + 1]) * M, b = new Vector2(f.points[i + 2], f.points[i + 3]) * M;
                    float za = GroundAt(g, a.x, a.y), zb = GroundAt(g, b.x, b.y);
                    mb.Quad(U(a.x, a.y, za - 0.1f), U(b.x, b.y, zb - 0.1f), U(b.x, b.y, zb + h), U(a.x, a.y, za + h));
                    foreach (var (q, zq) in new[] { (a, za), (b, zb) })
                        mb.Add(Prism(new[] { q + new Vector2(-0.06f, -0.06f), q + new Vector2(0.06f, -0.06f), q + new Vector2(0.06f, 0.06f), q + new Vector2(-0.06f, 0.06f) }, zq - 0.1f, zq + h + 0.1f));
                }
            }
            return mb.Make("fences");
        }

        /// <summary>Retaining walls round the level places: the face from its foot to its top at each point, a coping
        /// half a metre deep, and the inner face.</summary>
        static Mesh Walls(Wall[] walls)
        {
            var mb = new MB();
            foreach (var w in walls)
            {
                int n = w.points.Length / 4;
                Vector2 c = Vector2.zero;
                for (int i = 0; i < n; i++)
                    c += new Vector2(w.points[4 * i], w.points[4 * i + 1]) * M;
                c /= n;
                for (int i = 0; i < n; i++)
                {
                    int j = (i + 1) % n;
                    Vector2 a = new Vector2(w.points[4 * i], w.points[4 * i + 1]) * M, b = new Vector2(w.points[4 * j], w.points[4 * j + 1]) * M;
                    float af = w.points[4 * i + 2] * M, at = w.points[4 * i + 3] * M, bf = w.points[4 * j + 2] * M, bt = w.points[4 * j + 3] * M;
                    Vector2 ai = a + (c - a).normalized * 0.5f, bi = b + (c - b).normalized * 0.5f;
                    mb.Quad(U(a.x, a.y, af), U(b.x, b.y, bf), U(b.x, b.y, bt), U(a.x, a.y, at));
                    mb.Quad(U(a.x, a.y, at), U(b.x, b.y, bt), U(bi.x, bi.y, bt), U(ai.x, ai.y, at));
                    mb.Quad(U(ai.x, ai.y, at), U(bi.x, bi.y, bt), U(bi.x, bi.y, bf), U(ai.x, ai.y, af));
                }
            }
            return mb.Make("walls");
        }

        /// <summary>The steamer pier in stone down into the water; the jetties as timber decks floating at their level,
        /// each with a gangway down from the quay.</summary>
        static (Mesh stone, Mesh timber) Piers(Pier[] piers, Quay quay)
        {
            var stone = new MB();
            var timber = new MB();
            float water = quay.water * M, top = quay.top * M;
            foreach (var p in piers)
            {
                Vector2 a = new Vector2(p.points[0], p.points[1]) * M, b = new Vector2(p.points[2], p.points[3]) * M;
                Vector2 d = (b - a).normalized, s = new Vector2(-d.y, d.x) * (p.width * M / 2);
                float z = p.z * M;
                if (p.kind == "pier")
                {
                    stone.Add(Prism(new[] { a - s, a + s, b + s, b - s }, water - 3f, z));
                    continue;
                }
                // the floating deck from four metres out, the gangway from the quay's coping down to it
                Vector2 a4 = a + d * 4f;
                timber.Add(Prism(new[] { a4 - s, a4 + s, b + s, b - s }, z - 0.35f, z));
                Vector2 g = s.normalized * 0.6f, a0 = a - d * 0.5f;
                timber.Quad(U(a0.x - g.x, a0.y - g.y, top + 0.05f), U(a0.x + g.x, a0.y + g.y, top + 0.05f),
                            U(a4.x + g.x, a4.y + g.y, z), U(a4.x - g.x, a4.y - g.y, z));
            }
            return (stone.Make("piers"), timber.Make("jetties"));
        }

        /// <summary>The boats: a hull lofted through five stations from the transom to the stem (a færing pointed at
        /// both ends), its sheer rising to the bow; a wheelhouse or a cabin on deck by its kind.</summary>
        static Mesh Boats(Boat[] boats, float water, Tones tones)
        {
            var mb = new MB();
            float[] st = { 0f, 0.14f, 0.48f, 0.8f, 1f };
            foreach (var bt in boats)
            {
                mb.tint = tones == null ? Color.white : tones.Boat(bt).linear;
                float L = bt.length * M, B = bt.beam * M, ang = bt.angle * Mathf.Deg2Rad;
                Vector2 f = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)), sd = new Vector2(-f.y, f.x), o = new Vector2(bt.x, bt.y) * M;
                bool faering = bt.kind == "faering";
                float[] hb = faering ? new[] { 0.06f, 0.62f, 1f, 0.62f, 0.04f } : new[] { 0.8f, 0.96f, 1f, 0.72f, 0.03f };
                float fb = bt.kind == "sjark" ? 1.05f : bt.kind == "cruiser" ? 0.85f : bt.kind == "snekke" ? 0.6f : 0.45f;
                float draft = fb * 0.5f;
                Vector3 G(int k, float side, float lift = 0f)
                {
                    var p = o + f * ((st[k] - 0.5f) * L) + sd * (side * hb[k] * B / 2);
                    return U(p.x, p.y, water + fb + 0.35f * st[k] * st[k] * (faering ? 1f : 0.8f) + lift);
                }
                Vector3 K(int k, float side)
                {
                    var p = o + f * ((st[k] - 0.5f) * L) + sd * (side * hb[k] * B * 0.2f);
                    return U(p.x, p.y, water - draft * (0.4f + 0.6f * Mathf.Sin(Mathf.PI * Mathf.Min(1f, st[k] * 1.4f))));
                }
                for (int k = 0; k + 1 < st.Length; k++)
                {
                    mb.Quad(K(k, 1f), K(k + 1, 1f), G(k + 1, 1f), G(k, 1f));
                    mb.Quad(K(k, -1f), G(k, -1f), G(k + 1, -1f), K(k + 1, -1f));
                    // the deck (or the open boat's floor) a little below the gunwale
                    mb.Quad(G(k, -1f, -0.2f), G(k, 1f, -0.2f), G(k + 1, 1f, -0.2f), G(k + 1, -1f, -0.2f));
                }
                mb.Quad(K(0, -1f), K(0, 1f), G(0, 1f), G(0, -1f));
                if (bt.deck == "open")
                    continue;
                bool wheel = bt.deck == "wheelhouse";
                float s0 = wheel ? 0.2f : 0.34f, s1 = wheel ? 0.44f : 0.74f, hw = B * (wheel ? 0.31f : 0.36f);
                float zd = water + fb + 0.35f * 0.1f, hh = wheel ? 1.9f : 0.95f;
                Vector2 p0 = o + f * ((s0 - 0.5f) * L), p1 = o + f * ((s1 - 0.5f) * L);
                mb.Add(Prism(new[] { p0 - sd * hw, p1 - sd * hw, p1 + sd * hw, p0 + sd * hw }, zd - 0.2f, zd + hh));
            }
            return mb.Make("boats");
        }

        // -- a house as masses: body, roof, plinth -----------------------------------------------------------------------

        static (Mesh body, Mesh roof, Mesh foot) Masses(Placement p, Grid g)
        {
            var fp = new Vector2[4];
            for (int i = 0; i < 4; i++)
                fp[i] = new Vector2(p.footprint[2 * i] * M, p.footprint[2 * i + 1] * M);
            float b = p.@base * M, e = p.eave * M;
            float low = b;
            foreach (var q in fp)
                low = Mathf.Min(low, GroundAt(g, q.x, q.y));
            for (int i = 0; i < 4; i++)
            {
                var mid = 0.5f * (fp[i] + fp[(i + 1) % 4]);
                low = Mathf.Min(low, GroundAt(g, mid.x, mid.y));
            }
            var walls = new MB();
            walls.Add(Prism(fp, b, e));
            var foot = Prism(fp, low - 0.3f, b);
            Vector2 u0 = (fp[1] - fp[0]).normalized, n0 = (fp[3] - fp[0]).normalized;
            float W0 = Vector2.Distance(fp[0], fp[1]), D0 = Vector2.Distance(fp[0], fp[3]);
            if (p.chimneys != null && p.chimneys.Length >= 4 && p.roof != "spire")
            {
                // the chimneys on the ridge (along it from its middle, off it to the side), up from the eaves to their
                // rise above the roof where they stand; in the plinth's mesh
                var mb = new MB();
                mb.Add(foot);
                bool gable = p.roof == "gable";
                Vector2 rd = gable ? n0 : u0, xd = gable ? u0 : n0, mid = 0.5f * (fp[0] + fp[2]);
                float tanr = Mathf.Tan(p.pitch * Mathf.Deg2Rad), zr = e + (gable ? W0 : D0) / 2 * tanr;
                for (int i = 0; i + 3 < p.chimneys.Length; i += 4)
                {
                    float al = p.chimneys[i] * M, ac = p.chimneys[i + 1] * M, hs = p.chimneys[i + 2] * M / 2, up = p.chimneys[i + 3] * M;
                    Vector2 c = mid + rd * al + xd * ac;
                    mb.Add(Prism(new[] { c - rd * hs - xd * hs, c + rd * hs - xd * hs, c + rd * hs + xd * hs, c - rd * hs + xd * hs },
                                 e, zr - ac * tanr + up));
                }
                foot = mb.Make("plinth and chimneys");
            }
            // the roof: ridge along the front (eaves) or front to back (gable), the eaves out 0.4 m
            Vector2 u = (fp[1] - fp[0]).normalized, n = (fp[3] - fp[0]).normalized;
            float W = Vector2.Distance(fp[0], fp[1]), D = Vector2.Distance(fp[0], fp[3]);
            float o = 0.4f, tan = Mathf.Tan(p.pitch * Mathf.Deg2Rad);
            Vector2 c0 = fp[0] - u * o - n * o;
            float L = W + 2 * o, S = D + 2 * o;
            var v = new List<Vector3>();
            var t = new List<int>();
            Vector3 P(float s, float w, float z) { var q = c0 + u * s + n * w; return U(q.x, q.y, z); }
            void Quad(Vector3 a, Vector3 bb, Vector3 c, Vector3 d) { int k = v.Count; v.Add(a); v.Add(bb); v.Add(c); v.Add(d); t.AddRange(new[] { k, k + 2, k + 1, k, k + 3, k + 2 }); }
            void Tri(Vector3 a, Vector3 bb, Vector3 c) { int k = v.Count; v.Add(a); v.Add(bb); v.Add(c); t.AddRange(new[] { k, k + 2, k + 1 }); }
            // a gable end is wall, in the wall's colour
            void Gable(Vector3 a, Vector3 bb, Vector3 c) => walls.Tri(a, bb, c);
            if (p.roof == "spire")
            {
                var apex = 0.5f * (fp[0] + fp[2]);
                float za = e + (W / 2) * tan;
                for (int i = 0; i < 4; i++)
                {
                    Vector2 q0 = fp[i] + (fp[i] - apex).normalized * 0.3f, q1 = fp[(i + 1) % 4] + (fp[(i + 1) % 4] - apex).normalized * 0.3f;
                    Tri(U(q0.x, q0.y, e), U(apex.x, apex.y, za), U(q1.x, q1.y, e));
                }
            }
            else if (p.roof == "gable")
            {
                float zr = e + (W / 2) * tan;
                // ridge runs front to back (along n) at the middle of u
                Quad(P(0, 0, e - o * tan), P(0, S, e - o * tan), P(L / 2, S, zr), P(L / 2, 0, zr));
                Quad(P(L / 2, 0, zr), P(L / 2, S, zr), P(L, S, e - o * tan), P(L, 0, e - o * tan));
                Gable(P(o, o, e), P(L / 2, o, zr), P(L - o, o, e));
                Gable(P(L - o, S - o, e), P(L / 2, S - o, zr), P(o, S - o, e));
            }
            else
            {
                float zr = e + (D / 2) * tan;
                Quad(P(0, 0, e - o * tan), P(L, 0, e - o * tan), P(L, S / 2, zr), P(0, S / 2, zr));
                Quad(P(0, S / 2, zr), P(L, S / 2, zr), P(L, S, e - o * tan), P(0, S, e - o * tan));
                Gable(P(o, S - o, e), P(o, S / 2, zr), P(o, o, e));
                Gable(P(L - o, o, e), P(L - o, S / 2, zr), P(L - o, S - o, e));
            }
            var roof = new Mesh { name = "roof", hideFlags = HideFlags.DontSave };
            roof.SetVertices(v);
            roof.SetTriangles(t, 0);
            roof.RecalculateNormals();
            DoubleSided(roof);
            return (walls.Make("walls"), roof, foot);
        }

        static Mesh Prism(Vector2[] fp, float z0, float z1)
        {
            var v = new List<Vector3>();
            var t = new List<int>();
            for (int i = 0; i < fp.Length; i++)
            {
                var a = fp[i];
                var b = fp[(i + 1) % fp.Length];
                int k = v.Count;
                v.Add(U(a.x, a.y, z0)); v.Add(U(b.x, b.y, z0)); v.Add(U(b.x, b.y, z1)); v.Add(U(a.x, a.y, z1));
                t.AddRange(new[] { k, k + 2, k + 1, k, k + 3, k + 2 });
            }
            int top = v.Count;
            foreach (var q in fp)
                v.Add(U(q.x, q.y, z1));
            t.AddRange(new[] { top, top + 2, top + 1, top, top + 3, top + 2 });
            var m = new Mesh { name = "prism", hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetTriangles(t, 0);
            m.RecalculateNormals();
            DoubleSided(m);
            return m;
        }

        /// <summary>Greybox only: every face drawn from both sides, so a winding slip shows as a face, not a hole.</summary>
        static void DoubleSided(Mesh m)
        {
            var v = m.vertices;
            var n = m.normals;
            var t = m.triangles;
            var c = m.colors;
            var v2 = new Vector3[v.Length * 2];
            var n2 = new Vector3[v.Length * 2];
            var t2 = new int[t.Length * 2];
            for (int i = 0; i < v.Length; i++) { v2[i] = v[i]; v2[i + v.Length] = v[i]; n2[i] = n[i]; n2[i + v.Length] = -n[i]; }
            for (int i = 0; i < t.Length; i += 3)
            {
                t2[i] = t[i]; t2[i + 1] = t[i + 1]; t2[i + 2] = t[i + 2];
                t2[t.Length + i] = t[i] + v.Length; t2[t.Length + i + 1] = t[i + 2] + v.Length; t2[t.Length + i + 2] = t[i + 1] + v.Length;
            }
            m.vertices = v2;
            m.normals = n2;
            if (c != null && c.Length == v.Length)
            {
                var c2 = new Color[v2.Length];
                for (int i = 0; i < v.Length; i++) { c2[i] = c[i]; c2[i + v.Length] = c[i]; }
                m.colors = c2;
            }
            m.triangles = t2;
        }
    }
}
