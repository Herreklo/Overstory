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
            public int id, of, x, y, w, d, @base, eave, pitch, year;
            public float angle;
            public string kind, lane, side, roof;
            public int[] footprint, chimneys;
        }
        [Serializable] public class Tree { public string id, species, crown; public int x, y, z, h, r, planted; }
        [Serializable] public class Pier { public string id, kind; public int width, z; public int[] points; }
        [Serializable] public class Boat { public string id, kind, deck; public int x, y, length, beam; public float angle; }
        [Serializable] public class Stand { public string id; public int planted, h; public int[] points; }
        [Serializable] public class Wall { public string id; public int[] points; }
        [Serializable] public class Fence { public string id, kind; public int height, width; public int[] points; }
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

        // the pack's records as R2aPatches.Json reads them
        static Color Hex(string h) => ColorUtility.TryParseHtmlString("#" + h, out var c) ? c : throw new FormatException($"not a colour: {h}");
        static Dictionary<string, object> Obj(object o) => (Dictionary<string, object>)o;
        static List<object> Arr(object o) => (List<object>)o;
        static float F(object o) => (float)(double)o;

        /// <summary>The views: the two city cameras, the street stop and the roam's poses (street frame, m).</summary>
        public static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Views =
        {
            ("mid", new Vector3(55f, -115f, 46f), new Vector3(58f, 45f, 20f), 42f),
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
            // the pack's facts for the houses' working in every render; its colours only in light
            var facts = new Tones(Path.Combine(repo, "packs", "stavanger-1989"), town);
            var tones = moment == null ? null : facts;

            var lit = Shader.Find("Universal Render Pipeline/Lit");
            var townShader = Shader.Find("Overstory/Town");
            var cache = new Dictionary<string, Material>();
            // grey: a URP Lit grey of value v; light: the town shader in colour c (sRGB), tinted by the vertex colours
            Material Mat(float v, Color c, bool tinted = false, float porosity = 0.5f, float smooth = 0.06f, float ground = 0.35f,
                         float brush = 1f, float laps = 0f, float contact = 0f)
            {
                string key = moment == null ? $"g{v}" : $"{ColorUtility.ToHtmlStringRGB(c)}{tinted}{porosity}{smooth}{ground}{brush}{laps}{contact}";
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
                    m.SetFloat("_Brush", brush);
                    m.SetFloat("_Laps", laps);
                    m.SetFloat("_Contact", contact);
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
            Material water;
            if (moment == null)
                water = Mat(0.30f, white);
            else
            {
                // opaque, its colour baked into the mesh (Water); under the screen's reflections, so no blurred mirror
                var look = facts.water;
                water = new Material(townShader) { name = "water", hideFlags = HideFlags.DontSave };
                water.SetColor("_BaseColor", white);
                water.SetFloat("_Water", 1f);
                water.SetFloat("_Porosity", 0f);
                water.SetFloat("_Smoothness", F(look["smoothness"]));
                water.SetFloat("_Ground", 0f);
                water.SetColor("_LineColor", Hex((string)look["line"]));
                water.SetFloat("_LineWidth", F(look["lineM"]));
                water.SetFloat("_WaveScale", F(look["waveScale"]));
                water.SetFloat("_WaveStrength", F(look["waveStrength"]));
                water.SetFloat("_WaveStretch", F(look["waveStretch"]));
                water.SetFloat("_WaveWobble", F(look["waveWobble"]));
                made.Add(water);
            }
            var fenceM = Mat(0.70f, tones?.fence ?? white, porosity: 0.2f, smooth: 0.15f);
            var plinth = Mat(0.36f, tones?.stone ?? white, porosity: 0.6f, smooth: 0.08f);
            var crown = Mat(0.34f, white, tinted: true, porosity: 0.3f, smooth: 0.08f, ground: 0.2f);
            var standM = Mat(0.34f, tones?.stand ?? white, porosity: 0.3f, smooth: 0.08f, ground: 0.2f);
            var trunk = Mat(0.26f, white, tinted: true, porosity: 0.6f);
            var timber = Mat(0.40f, tones?.boards ?? white, porosity: 0.7f);
            // the openings and trims take each house's paints in their vertex colours; the panes the glass's, lit or not
            var trimM = Mat(0.78f, white, tinted: true, porosity: 0.2f, smooth: 0.15f, brush: facts.brush);
            Material paneM;
            if (moment == null)
                paneM = Mat(0.12f, white);
            else
            {
                paneM = new Material(townShader) { name = "pane", hideFlags = HideFlags.DontSave };
                paneM.SetColor("_BaseColor", white);
                paneM.SetFloat("_Tinted", 1f);
                paneM.SetFloat("_Porosity", 0f);
                paneM.SetFloat("_Smoothness", F(Obj(facts.town["glass"])["smoothness"]));
                paneM.SetFloat("_Ground", 0.35f);
                paneM.SetFloat("_Pane", 1f);
                paneM.SetVector("_PaneLit", facts.paneLit);
                made.Add(paneM);
            }
            var hull = Mat(0.62f, white, tinted: true, porosity: 0.1f, smooth: 0.35f);

            Add(root, "ground", GroundMesh(town.ground, true, tones), town.ground.cover != null ? covered : ground, made);
            Add(root, "paving", Paving(town, tones), paved, made);
            if (town.stairs != null)
                Add(root, "stairs", Stairs(town.stairs, tones), paved, made);
            Add(root, "land", GroundMesh(town.coarse, false, null), ground, made);
            Add(root, "water", moment == null ? Plane(-1600f, -1400f, 1700f, 1900f, town.quay.water * M) : Water(town, facts.water), water, made);
            Add(root, "quay wall", QuayWall(town.quay), plinth, made);
            {
                var (coping, bollards) = Coping(town, facts);
                Add(root, "quay coping", coping, Mat(0.58f, tones?.copingStone ?? white, porosity: 0.3f, smooth: 0.1f), made);
                Add(root, "bollards", bollards, Mat(0.12f, tones?.bollardIron ?? white, porosity: 0f, smooth: 0.3f), made);
            }
            if (tones != null)
                Add(root, "wet bands", WetBands(town, F(facts.water["wetM"])), Mat(0.2f, tones.stone * F(facts.water["wet"]), porosity: 0f, smooth: 0.3f), made);
            if (town.walls != null)
                Add(root, "walls", Walls(town.walls), plinth, made);
            if (town.fences != null)
            {
                var (pickets, planks, hedges, stones) = Fences(town.fences, town.ground, tones);
                Add(root, "fences", pickets, fenceM, made);
                Add(root, "plank fences", planks, timber, made);
                Add(root, "hedges", hedges, crown, made);
                Add(root, "dry-stone walls", stones, plinth, made);
            }
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
                var (crowns, leaves, trunks) = Trees(town.trees, facts, tones != null);
                Add(root, "tree crowns", crowns, crown, made);
                Add(root, "tree trunks", trunks, trunk, made);
                if (moment != null)
                {
                    // the crowns' fringe: the crowns' material, each card turned to the eye (Town.shader, _Card)
                    var leafM = new Material(crown) { name = "leaves", hideFlags = HideFlags.DontSave };
                    leafM.SetFloat("_Card", 1f);
                    var edge = Arr(facts.fringe["edge"]);
                    leafM.SetVector("_CardEdge", new Vector4(F(edge[0]), F(edge[1]), 0f, 0f));
                    made.Add(leafM);
                    Add(root, "tree fringe", leaves, leafM, made);
                }
                else
                    Object.DestroyImmediate(leaves);
            }
            if (town.stands != null)
                Add(root, "stands", Stands(town.stands, town.ground), standM, made);
            var houses = new GameObject("houses");
            houses.transform.SetParent(root.transform, false);
            var trims = new MB();
            var panes = new MB();
            foreach (var p in town.placements)
            {
                var (body, roof, foot) = Masses(p, town.ground, facts.Overhang(p));
                Add(houses, $"house {p.id}", body, Mat(0.55f, tones?.Body(p) ?? white, porosity: 0.15f, smooth: 0.1f, brush: facts.brush,
                                                       laps: facts.Laps(p), contact: 1f), made);
                Add(houses, $"house {p.id} roof", roof, Mat(0.30f, tones?.Roof(p) ?? white, porosity: 0.35f, smooth: 0.12f, brush: facts.brush,
                                                            laps: facts.Courses(p)), made);
                Add(houses, $"house {p.id} plinth", foot, plinth, made);
                Openings(p, town.ground, facts, trims, panes);
                Roofline(p, facts, facts.Overhang(p), trims);
            }
            Add(houses, "openings and trims", trims.Make("openings"), trimM, made);
            Add(houses, "panes", panes.Make("panes"), paneM, made);
            if (tones != null && facts.smoke != null)
            {
                // the stoves' smoke, the moment's (Smoke)
                var smokeM = new Material(Shader.Find("Overstory/TownSmoke")) { name = "smoke", hideFlags = HideFlags.DontSave };
                smokeM.SetColor("_Colour", Hex((string)facts.smoke["srgb"]));
                smokeM.SetFloat("_Forward", F(facts.smoke["forward"]));
                made.Add(smokeM);
                Add(root, "smoke", Smoke(town, facts), smokeM, made);
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

            string[] compasses = Cli.Arg("-compass", null)?.Split(',') ?? new string[] { null };
            foreach (var m0 in moment == null ? new[] { "grey" } : moment.Split(','))
            foreach (var compass in compasses)
            {
                string m = compass == null ? m0 : $"{m0}-c{compass}";
                if (stage != null)
                {
                    // the street's moment, with the air at the city's distances (town.json, air); the asset is left alone
                    var rig = Object.Instantiate(AssetDatabase.LoadAssetAtPath<LightRig>($"{LT1}/Heart/Light/Heart_{m0}.asset")
                        ?? throw new FileNotFoundException($"no light rig Heart_{m0}"));
                    rig.hideFlags = HideFlags.DontSave;
                    made.Add(rig);
                    facts.Air(rig, compass);
                rig.reflectionStrength = F(facts.water["reflection"]);   // the harbour's mirror at the city's distances
                    stage.rig = rig;
                }
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
                    {
                        stage.Apply();
                        Shader.SetGlobalFloat("_OS_AirClear", facts.airClear);
                        Shader.SetGlobalVector("_OS_Laps", facts.laps);
                        Shader.SetGlobalVector("_OS_Contact", facts.contact);
                    }
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
            public readonly Color land, stand, fence, stone;
            readonly Dictionary<string, Color[]> crowns = new Dictionary<string, Color[]>();
            readonly Dictionary<string, (Color c, float girth)> trunks = new Dictionary<string, (Color, float)>();
            readonly Dictionary<string, Color> surfaces = new Dictionary<string, Color>();
            readonly Color[] boats, hedges;
            readonly Dictionary<string, object> paint, schemeOf;
            readonly Dictionary<string, Color> paints = new Dictionary<string, Color>();
            readonly Dictionary<int, Dictionary<string, object>> diaries = new Dictionary<int, Dictionary<string, object>>();
            readonly Dictionary<string, string> grain = new Dictionary<string, string>();
            readonly string pack;
            const int Year = 1989;

            public readonly Dictionary<string, object> timber, openings, water, fringe, town;
            /// <summary>The stoves' smoke at the moment, or null where the pack has none.</summary>
            public readonly Dictionary<string, object> smoke;
            /// <summary>The share of the look's brushwork the houses' walls, roofs and trims take.</summary>
            public readonly float brush;
            /// <summary>The weatherboards' line near the eye: full within, gone by (m), its shade, its share of a board.</summary>
            public readonly Vector4 laps;
            /// <summary>The sky a wall loses under its eaves and at its foot: under the eaves within (m), its share there,
            /// above the foot within (m), its share there.</summary>
            public readonly Vector4 contact;
            /// <summary>The quay's coping (its width and height, m) and its bollards (every so many metres, from and to; their
            /// width and height, m), and their colours.</summary>
            public readonly Vector2 coping;
            public readonly Vector4 bollards;
            public readonly Color copingStone, bollardIron;
            /// <summary>The inside of an open boat and the deck of a decked one.</summary>
            public readonly Color boatOpen, boatDecked;
            public readonly Color glass, boards;
            /// <summary>A lit room's light through its pane at a window glow of 1, linear.</summary>
            public readonly Vector4 paneLit;
            readonly Dictionary<string, object> evening;

            Dictionary<string, object> Read(string name) => Obj(R2aPatches.Json.Parse(File.ReadAllText(Path.Combine(pack, name))));

            public Tones(string pack, Town t)
            {
                this.pack = pack;
                town = Read("town.json");
                paint = Read("paint.json");
                timber = Read("timber.json");
                openings = Obj(town["openings"]);
                evening = Obj(town["evening"]);
                glass = Hex((string)Obj(town["glass"])["srgb"]);
                water = Obj(town["water"]);
                fringe = Obj(town["fringe"]);
                smoke = town.TryGetValue("smoke", out var sk) ? Obj(sk) : null;
                brush = F(town["houseBrush"]);
                var lp = Obj(town["laps"]);
                laps = new Vector4(F(lp["fullM"]), F(lp["goneM"]), F(lp["shade"]), F(lp["share"]));
                var ct = Obj(town["contact"]);
                contact = new Vector4(F(ct["eaveM"]), F(ct["eave"]), F(ct["footM"]), F(ct["foot"]));
                var qy = Obj(town["quay"]);
                var cp = Obj(qy["coping"]);
                var bl = Obj(qy["bollards"]);
                coping = new Vector2(F(cp["widthM"]), F(cp["heightM"]));
                copingStone = Hex((string)cp["srgb"]);
                bollards = new Vector4(F(Arr(bl["everyM"])[0]), F(Arr(bl["everyM"])[1]), F(bl["widthM"]), F(bl["heightM"]));
                bollardIron = Hex((string)bl["srgb"]);
                // the room behind a lit pane: its lamp on its walls and its curtains, half each (materials/glass.json)
                var room = Obj(Read("materials/glass.json")["room"]);
                Color lamp = Hex((string)room["srgbLamp"]).linear, walls = Hex((string)room["srgbWalls"]).linear,
                      cloth = Hex((string)Obj(room["curtains"])["srgb"]).linear;
                var lit = lamp * Color.Lerp(walls, cloth, 0.5f) * F(evening["pane"]);
                // by day a curtained pane shows its cloth in the daylight through the glass, as far as the cloth is opaque
                var curtains = Obj(room["curtains"]);
                curtainShare = F(curtains["share"]);
                curtained = Color.Lerp(glass.linear, cloth * F(Obj(Read("materials/glass.json")["daylight"])["curtains"]), F(curtains["opacity"]));
                paneLit = new Vector4(lit.r, lit.g, lit.b, 1f);
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
                fence = paints[(string)town["fences"]];
                stone = Hex((string)Read("materials/fieldstone.json")["srgb"]);
                boards = Hex((string)Read("materials/pine.json")["srgbWeathered"]);
                foreach (var kv in Obj(town["crowns"]))
                    crowns[kv.Key] = Arr(kv.Value).ConvertAll(o => Hex((string)o)).ToArray();
                foreach (var kv in Obj(town["trunks"]))
                    trunks[kv.Key] = (Hex((string)Obj(kv.Value)["srgb"]), F(Obj(kv.Value)["girth"]));
                foreach (var kv in Obj(town["surfaces"]))
                    surfaces[kv.Key] = Hex((string)kv.Value);
                boats = Arr(town["boats"]).ConvertAll(o => paints[(string)o]).ToArray();
                var bi = Obj(town["boatInside"]);
                boatOpen = Hex((string)bi["open"]);
                boatDecked = Hex((string)bi["decked"]);
                hedges = Arr(town["hedges"]).ConvertAll(o => Hex((string)o)).ToArray();
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

            /// <summary>The air seen across the town (town.json, air): the hour's colours stay the rig's, its thickness and
            /// layers are for hundreds of metres, not a street's fifty. A compass (the bearing of the town's +x) turns the
            /// sun to the town's own frame from the rig's azimuth.</summary>
            public float airClear;

            public void Air(LightRig r, string compass)
            {
                if (compass != null)
                {
                    float azimuth = r.streetAxisCompass - r.sunBearing;
                    r.sunBearing = Mathf.Repeat(float.Parse(compass, System.Globalization.CultureInfo.InvariantCulture) - azimuth, 360f);
                }
                // the city camera keys its lightest light, a white wall in the sun, not the light on level ground
                if (town.TryGetValue("camera", out var cam))
                    r.postExposure += F(Obj(cam)["exposure"]);
                if (!town.TryGetValue("air", out var o))
                    return;
                var a = Obj(o);
                airClear = F(a["clearM"]);
                r.fogDensity = F(a["density"]);
                r.fogHeightFalloff = F(a["heightFalloff"]);
                r.fogMidDistance = F(a["midM"]);
                r.fogFarDistance = F(a["farM"]);
                r.fogMidColour = Color.Lerp(r.fogColour, r.zenith, F(a["midToZenith"]));
                r.fogFarColour = Color.Lerp(r.fogColour, r.zenith, F(a["farToZenith"]));
                r.hazeDensity = F(a["haze"]);
                r.hazeHeight = F(a["hazeHeight"]);
                r.hazeColour = r.fogColour;
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
                object list;
                if ((p.kind == "warehouse" || p.kind == "outhouse") && period["back"] != null)
                    list = period["back"];
                else if (Kept(p))
                    list = schemeOf["body"];
                else
                    list = period["body"];
                return Worn(p, paints[(string)Pick(Arr(list), Seed(Id(p), p.kind == "outhouse" ? "back" : "body"))]);
            }

            /// <summary>A part's paint (trim, window, door): the scheme's where it holds and names the part, else the
            /// period's of the house's last painting; worn as its body is.</summary>
            public Color Paint(Placement p, string part)
            {
                var d = Diary(p);
                int painted = Last(d, "built", "repainted");
                var period = Period(painted > 0 ? painted : 1900);
                object list = Kept(p) && schemeOf.ContainsKey(part) ? schemeOf[part] : period[part];
                return Worn(p, paints[(string)Pick(Arr(list), Seed(Id(p), part))]);
            }

            /// <summary>A part's paint as a period chose it (a window put in by an event comes painted in its year).</summary>
            public Color PaintOf(int year, Placement p, string part) =>
                Worn(p, paints[(string)Pick(Arr(Period(year)[part]), Seed(Id(p), $"{part}.{year}"))]);

            int Id(Placement p) { var d = Diary(p); return d != null ? (int)(double)d["id"] : p.id; }

            /// <summary>The year of its last painting (built or repainted).</summary>
            public int Painted(Placement p) => Last(Diary(p), "built", "repainted");

            bool Kept(Placement p)
            {
                var scheme = Obj(town["scheme"]);
                string g = p.lane != null && grain.TryGetValue(p.lane, out var gg) ? gg : null;
                return schemeOf != null && Year >= (double)schemeOf["from"]
                    && (g != null && Arr(scheme["grains"]).Contains(g) || scheme.TryGetValue("kinds", out var k) && Arr(k).Contains(p.kind));
            }

            /// <summary>A house left to decline since its last painting goes part way to the soil's colour.</summary>
            Color Worn(Placement p, Color c)
            {
                var d = Diary(p);
                if (Last(d, "neglected") <= Last(d, "built", "repainted"))
                    return c;
                var n = Obj(town["neglect"]);
                return Color.Lerp(c, paints[(string)n["toward"]], F(n["share"]));
            }

            /// <summary>The era its builder worked in (its diary's built event), and that era's working (timber.json).</summary>
            public string Era(Placement p)
            {
                var d = Diary(p);
                if (d != null)
                    foreach (var e in Arr(d["events"]))
                        if ((string)Obj(e)["kind"] == "built" && Obj(Obj(e)["params"]).TryGetValue("era", out var era))
                            return (string)era;
                return "classical";
            }

            public Dictionary<string, object> Working(Placement p)
            {
                var workings = Obj(timber["workings"]);
                string era = Era(p);
                return Obj(workings.TryGetValue(era, out var w) ? w : workings[(string)Obj(town["workingOf"])[era]]);
            }

            /// <summary>How far the eaves and verges stand out from the walls, by the era's working.</summary>
            /// <summary>A roof's courses as they rise (m): its covering's course up the slope (materials/*.json, laid) by
            /// the sine of its pitch.</summary>
            public float Courses(Placement p)
            {
                var laid = Obj(Read($"materials/{Covering(p)}.json")["laid"]);
                return F(laid["courseMm"]) * M * Mathf.Sin(p.pitch * Mathf.Deg2Rad);
            }

            /// <summary>A timber house's weatherboards' exposure (m), the middle of its working's.</summary>
            public float Laps(Placement p)
            {
                var e = Arr(Obj(Working(p)["cladding"])["exposureMm"]);
                return (F(e[0]) + F(e[1])) / 2f * M;
            }

            public float Overhang(Placement p) => F(Obj(Working(p)["eaves"])["overhangMm"]) * M;

            /// <summary>The window in a wall at the date, as tools/houses.py has it: the era's, or what the latest
            /// replacement put in (timber.json, windowsByYear), unless a restoration since put the era's back. wall 0 is
            /// the front (an event's scope 'street'), 2 the back; upper, a gable's loft window.</summary>
            public (string kind, int year) WindowAt(Placement p, int wall, bool upper)
            {
                string kind = (string)Obj(Working(p)["openings"])["window"];
                int year = Last(Diary(p), "built");
                var d = Diary(p);
                if (d == null)
                    return (kind, year);
                foreach (var o in Arr(d["events"]))
                {
                    var e = Obj(o);
                    int y = (int)(double)e["year"];
                    if (y > Year)
                        break;
                    var pr = e.TryGetValue("params", out var q) && q != null ? Obj(q) : new Dictionary<string, object>();
                    string scope = pr.TryGetValue("scope", out var s) ? (string)s : "all";
                    bool hit = scope == "all" || scope == "street" && wall == 0 || scope == "back" && wall == 2 || scope == "upper" && upper;
                    if (!hit)
                        continue;
                    if ((string)e["kind"] == "windows_replaced")
                    {
                        foreach (var w in Arr(timber["windowsByYear"]))
                            if (y >= (double)Obj(w)["from"] && y <= (double)Obj(w)["to"])
                                kind = (string)Obj(w)["window"];
                        year = y;
                    }
                    else if ((string)e["kind"] == "restored" && pr.TryGetValue("windows", out var wo) && (string)wo == "original")
                    {
                        kind = (string)Obj(Working(p)["openings"])["window"];
                        year = y;
                    }
                }
                return (kind, year);
            }

            /// <summary>What is boarded up on the date: "" nothing, else the boarded event's scope (ground, all).</summary>
            public string Boarded(Placement p)
            {
                var d = Diary(p);
                string scope = "";
                if (d != null)
                    foreach (var o in Arr(d["events"]))
                    {
                        var e = Obj(o);
                        if ((string)e["kind"] == "boarded")
                            scope = e.TryGetValue("params", out var q) && Obj(q).TryGetValue("scope", out var s) ? (string)s : "all";
                        else if ((string)e["kind"] == "unboarded")
                            scope = "";
                    }
                return scope;
            }

            /// <summary>Whether a room is lit at the evening's moment (town.json, evening): never in a house its diary
            /// leaves empty (let go and not restored, or boarded); else the household home or not, and each room in turn,
            /// by seed (local scene state, claiming nothing).</summary>
            public bool Lit(Placement p, string room)
            {
                if (!Home(p))
                    return false;
                float share = Obj(evening["kinds"]).TryGetValue(p.kind, out var k) ? F(k) : 0f;
                return Hash.Unit(Hash.Then(Seed(p.id, "lit"), room)) < F(evening["room"]) * share;
            }

            /// <summary>Whether its household is in at the moment: never in a house its diary says is boarded or neglected,
            /// nor in a kind nobody lives in; seeded.</summary>
            public bool Home(Placement p)
            {
                var d = Diary(p);
                if (Boarded(p) != "" || Last(d, "neglected") > Last(d, "restored"))
                    return false;
                float share = Obj(evening["kinds"]).TryGetValue(p.kind, out var k) ? F(k) : 0f;
                return share > 0f && Hash.Unit(Seed(Id(p), "home")) < F(evening["home"]);
            }

            /// <summary>Whether its stove is lit at the moment (smoke), only in a home whose household is in; seeded.</summary>
            public bool Smoking(Placement p) =>
                smoke != null && Home(p) && Hash.Unit(Seed(p.id, "smoke")) < F(smoke["share"]);

            /// <summary>A roof's covering: the one of its year built (town.json, roofs).</summary>
            string Covering(Placement p)
            {
                int built = Mathf.Max(Mathf.Max(Last(Diary(p), "built"), 1), p.year);
                foreach (var o in Arr(town["roofs"]))
                    if (built < (double)Obj(o)["to"])
                        return (string)Obj(o)["material"];
                return null;
            }

            /// <summary>A roof's colour, weathered from new to old over its record's years (materials/*.json, oldYears);
            /// relaid, its cleaned tiles keep a share of the weathering they had (relaidKeeps).</summary>
            public Color Roof(Placement p)
            {
                var d = Diary(p);
                // a part grown later (a porch, a lean-to) is roofed in its own year
                int built = Mathf.Max(Mathf.Max(Last(d, "built"), 1), p.year);
                int laid = Mathf.Max(built, Last(d, "roof_retiled"));
                var rec = Read($"materials/{Covering(p)}.json");
                float old = F(rec["oldYears"]), keeps = rec.TryGetValue("relaidKeeps", out var k) ? F(k) : 0f;
                float age = Mathf.Clamp01((Year - laid) / old + keeps * Mathf.Clamp01((laid - built) / old));
                var c = Color.Lerp(Hex((string)rec["srgbNew"]), Hex((string)rec["srgbOld"]), age);
                // one roof a little apart from the next, claiming nothing
                return c * Hash.Range(Seed(p.id, "roof"), 0.93f, 1.07f);
            }

            public Color Crown(Tree t) =>
                crowns.TryGetValue(t.species, out var c) ? Pick(c, Hash.Of($"town.crown.{t.id}")) : stand;

            /// <summary>A window's panes by day (linear): dark glass, or the cloth of its curtains in a share of rooms.</summary>
            public Color Pane(Placement p, string room) =>
                Hash.Unit(Hash.Then(Seed(p.id, "curtains"), room)) < curtainShare ? curtained : glass.linear;
            readonly float curtainShare;
            readonly Color curtained;

            /// <summary>A tree's bark and its trunk's width at the foot per metre of its height.</summary>
            public (Color c, float girth) Trunk(Tree t) => trunks.TryGetValue(t.species, out var b) ? b : trunks["default"];

            public Color Surface(string name) => surfaces.TryGetValue(name, out var c) ? c : surfaces["setts"];

            public Color Boat(Boat b) => Pick(boats, Hash.Of($"town.boat.{b.id}"));
            public Color Hedge(Fence f) => Pick(hedges, Hash.Of($"town.hedge.{f.id}"));
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
                // grass, garden, heath, rock, forest floor, made, litter: a tone each, and how far its patches swing it
                float[] tone = { 0.43f, 0.48f, 0.33f, 0.52f, 0.24f, 0.40f, 0.36f };
                float[] swing = { 0.05f, 0.03f, 0.09f, 0.08f, 0.04f, 0.02f, 0.06f };
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
            Vector2 E(int i) => QuayAt(q, i);
            Vector2 Out(int i) => QuayOut(q, i);
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

        /// <summary>The quay's coping, a course of dressed stone along its face, standing proud of the quay; and its
        /// bollards on it, every so many metres (seeded). Neither runs where a sjøhus stands on the edge or a pier leaves
        /// it.</summary>
        static (Mesh coping, Mesh bollards) Coping(Town town, Tones facts)
        {
            var q = town.quay;
            float top = q.top * M, cw = facts.coping.x, chh = facts.coping.y;
            var houses = new List<Vector2[]>();
            foreach (var p in town.placements)
                if (p.lane == "quay")
                {
                    var fp = new Vector2[4];
                    for (int k = 0; k < 4; k++)
                        fp[k] = new Vector2(p.footprint[2 * k], p.footprint[2 * k + 1]) * M;
                    houses.Add(fp);
                }
            bool Clear(Vector2 at)
            {
                foreach (var fp in houses)
                {
                    bool inside = false;
                    for (int a = 0, b = 3; a < 4; b = a++)
                        if ((fp[a].y > at.y) != (fp[b].y > at.y) && at.x < (fp[b].x - fp[a].x) * (at.y - fp[a].y) / (fp[b].y - fp[a].y) + fp[a].x)
                            inside = !inside;
                    if (inside)
                        return false;
                }
                if (town.piers != null)
                    foreach (var pr in town.piers)
                        if (Vector2.Distance(at, new Vector2(pr.points[0], pr.points[1]) * M) < pr.width * M / 2f + 0.6f)
                            return false;
                return true;
            }
            var stone = new MB();
            var iron = new MB();
            int count = q.edge.Length / 2;
            float run = 0f, next = Hash.Range(Hash.Of("town.bollard.0"), facts.bollards.x, facts.bollards.y);
            int nb = 0;
            for (int i = 0; i + 1 < count; i++)
            {
                Vector2 a = QuayAt(q, i) + QuayOut(q, i) * 1.0f, b = QuayAt(q, i + 1) + QuayOut(q, i + 1) * 1.0f;
                Vector2 ai = a - QuayOut(q, i) * cw, bi = b - QuayOut(q, i + 1) * cw;
                float len = Vector2.Distance(a, b);
                if (Clear(0.5f * (a + b) - QuayOut(q, i) * (cw / 2f)))
                    stone.Add(Prism(new[] { a, b, bi, ai }, top - 0.1f, top + chh));
                // the bollards along it, set back from the face on the coping
                while (run + len >= next)
                {
                    float f = (next - run) / len;
                    var at = Vector2.Lerp(a, b, f) - QuayOut(q, i) * (cw / 2f);
                    if (Clear(at))
                    {
                        float hw = facts.bollards.z / 2f, cap = hw * 1.3f, h = top + chh + facts.bollards.w;
                        var o = QuayOut(q, i);
                        var t = new Vector2(-o.y, o.x);
                        iron.Add(Prism(new[] { at - t * hw - o * hw, at + t * hw - o * hw, at + t * hw + o * hw, at - t * hw + o * hw }, top + chh, h - 0.08f));
                        iron.Add(Prism(new[] { at - t * cap - o * cap, at + t * cap - o * cap, at + t * cap + o * cap, at - t * cap + o * cap }, h - 0.12f, h));
                    }
                    nb++;
                    next += Hash.Range(Hash.Of($"town.bollard.{nb}"), facts.bollards.x, facts.bollards.y);
                }
                run += len;
            }
            return (stone.Make("quay coping"), iron.Make("bollards"));
        }

        static Vector2 QuayAt(Quay q, int i) => new Vector2(q.edge[2 * i] * M, q.edge[2 * i + 1] * M);

        /// <summary>Seaward at the quay's i-th point: the right of the edge's run east.</summary>
        static Vector2 QuayOut(Quay q, int i)
        {
            int count = q.edge.Length / 2;
            var d = QuayAt(q, Mathf.Min(i + 1, count - 1)) - QuayAt(q, Mathf.Max(i - 1, 0));
            return new Vector2(d.y, -d.x).normalized;
        }

        // -- the water ---------------------------------------------------------------------------------------------------

        /// <summary>The ground's height as its mesh draws it: two triangles a cell, split from its (i+1, j) corner to its
        /// (i, j+1), so a waterline found on it is the one on screen.</summary>
        static float GroundTri(Grid g, float x, float y)
        {
            float fx = (x - g.x0 * M) / (g.step * M), fy = (y - g.y0 * M) / (g.step * M);
            int i = Mathf.Clamp(Mathf.FloorToInt(fx), 0, g.nx - 2), j = Mathf.Clamp(Mathf.FloorToInt(fy), 0, g.ny - 2);
            float tx = Mathf.Clamp01(fx - i), ty = Mathf.Clamp01(fy - j);
            float a = g.z[j * g.nx + i], b = g.z[j * g.nx + i + 1], c = g.z[(j + 1) * g.nx + i], d = g.z[(j + 1) * g.nx + i + 1];
            return (tx + ty <= 1f ? a + (b - a) * tx + (c - a) * ty : d + (c - d) * (1f - tx) + (b - d) * (1f - ty)) * M;
        }

        /// <summary>Each cell's distance, in cells, to the nearest source cell: a two-pass chamfer (1 and the root of 2).</summary>
        static float[] Chamfer(bool[] source, int W, int H)
        {
            const float D = 1.4142136f;
            var d = new float[W * H];
            for (int k = 0; k < d.Length; k++)
                d[k] = source[k] ? 0f : 1e9f;
            for (int j = 0; j < H; j++)
                for (int i = 0; i < W; i++)
                {
                    int k = j * W + i;
                    float v = d[k];
                    if (i > 0) v = Mathf.Min(v, d[k - 1] + 1f);
                    if (j > 0)
                    {
                        v = Mathf.Min(v, d[k - W] + 1f);
                        if (i > 0) v = Mathf.Min(v, d[k - W - 1] + D);
                        if (i < W - 1) v = Mathf.Min(v, d[k - W + 1] + D);
                    }
                    d[k] = v;
                }
            for (int j = H - 1; j >= 0; j--)
                for (int i = W - 1; i >= 0; i--)
                {
                    int k = j * W + i;
                    float v = d[k];
                    if (i < W - 1) v = Mathf.Min(v, d[k + 1] + 1f);
                    if (j < H - 1)
                    {
                        v = Mathf.Min(v, d[k + W] + 1f);
                        if (i < W - 1) v = Mathf.Min(v, d[k + W + 1] + D);
                        if (i > 0) v = Mathf.Min(v, d[k + W - 1] + D);
                    }
                    d[k] = v;
                }
            return d;
        }

        /// <summary>The harbour's water, opaque (Town.shader, _Water). Its colour is baked from the depth under it, the
        /// sky's hue lightening where the bed shows through, and darkest at the foot of a made thing (the quay, a pier, a
        /// house standing in the water). Its vertex alpha is its distance from the nearest waterline, -1 to 3 m, from which
        /// the shader draws one light line round everything standing in it: shore, quay, piers, jetties and boats. Half a
        /// metre over the town's ground grid, where the waterlines are, on a quarter-metre raster of what stands in the
        /// water; beyond it the land's grid, a few centimetres lower so the fine water always wins.</summary>
        static Mesh Water(Town town, Dictionary<string, object> look)
        {
            Grid g = town.ground, cg = town.coarse;
            float w = town.quay.water * M;
            Color shallow = Hex((string)look["shallow"]).linear, open = Hex((string)look["open"]).linear, foot = Hex((string)look["foot"]).linear;
            float deep = F(look["deepM"]), reach = F(look["footM"]);

            // what stands in the water, on a quarter-metre raster over the ground grid; the made things apart
            const float r = 0.25f;
            float X0 = g.x0 * M, Y0 = g.y0 * M;
            int W = Mathf.RoundToInt((g.nx - 1) * g.step * M / r), H = Mathf.RoundToInt((g.ny - 1) * g.step * M / r);
            var solid = new bool[W * H];
            var made = new bool[W * H];
            for (int j = 0; j < H; j++)
                for (int i = 0; i < W; i++)
                    solid[j * W + i] = GroundTri(g, X0 + (i + 0.5f) * r, Y0 + (j + 0.5f) * r) > w;
            void Fill(IList<Vector2> poly, bool isMade)
            {
                float x0 = float.MaxValue, y0 = float.MaxValue, x1 = float.MinValue, y1 = float.MinValue;
                foreach (var q in poly) { x0 = Mathf.Min(x0, q.x); y0 = Mathf.Min(y0, q.y); x1 = Mathf.Max(x1, q.x); y1 = Mathf.Max(y1, q.y); }
                int i0 = Mathf.Max(0, Mathf.FloorToInt((x0 - X0) / r)), i1 = Mathf.Min(W - 1, Mathf.CeilToInt((x1 - X0) / r));
                int j0 = Mathf.Max(0, Mathf.FloorToInt((y0 - Y0) / r)), j1 = Mathf.Min(H - 1, Mathf.CeilToInt((y1 - Y0) / r));
                for (int j = j0; j <= j1; j++)
                    for (int i = i0; i <= i1; i++)
                    {
                        float x = X0 + (i + 0.5f) * r, y = Y0 + (j + 0.5f) * r;
                        bool inside = false;
                        for (int a = 0, b = poly.Count - 1; a < poly.Count; b = a++)
                            if ((poly[a].y > y) != (poly[b].y > y) && x < (poly[b].x - poly[a].x) * (y - poly[a].y) / (poly[b].y - poly[a].y) + poly[a].x)
                                inside = !inside;
                        if (!inside)
                            continue;
                        solid[j * W + i] = true;
                        made[j * W + i] |= isMade;
                    }
            }
            // the quay from two metres in to its face a metre out (QuayWall)
            var quay = town.quay;
            for (int i = 0; i + 1 < quay.edge.Length / 2; i++)
                Fill(new[] { QuayAt(quay, i) - QuayOut(quay, i) * 2f, QuayAt(quay, i + 1) - QuayOut(quay, i + 1) * 2f,
                             QuayAt(quay, i + 1) + QuayOut(quay, i + 1), QuayAt(quay, i) + QuayOut(quay, i) }, true);
            if (town.piers != null)
                foreach (var p in town.piers)
                {
                    Vector2 a = new Vector2(p.points[0], p.points[1]) * M, b = new Vector2(p.points[2], p.points[3]) * M;
                    Vector2 d = (b - a).normalized, sd = new Vector2(-d.y, d.x) * (p.width * M / 2);
                    if (p.kind != "pier")
                        a += d * 4f;    // a jetty's deck floats from four metres out (Piers)
                    Fill(new[] { a - sd, a + sd, b + sd, b - sd }, p.kind == "pier");
                }
            foreach (var p in town.placements)
            {
                var fp = new Vector2[4];
                for (int k = 0; k < 4; k++)
                    fp[k] = new Vector2(p.footprint[2 * k], p.footprint[2 * k + 1]) * M;
                Fill(fp, true);
            }
            if (town.boats != null)
                foreach (var bt in town.boats)
                    Fill(HullPlan(bt), false);
            var toSolid = Chamfer(solid, W, H);
            var toWater = Chamfer(Array.ConvertAll(solid, x => !x), W, H);
            var toMade = Chamfer(made, W, H);
            // the boundary lies half a cell from a cell's centre: signed, in metres, out of the water negative
            var signed = new float[W * H];
            for (int k = 0; k < signed.Length; k++)
                signed[k] = solid[k] ? -(toWater[k] - 0.5f) * r : (toSolid[k] - 0.5f) * r;
            float Sample(float[] f, float x, float y)
            {
                float fx = (x - X0) / r - 0.5f, fy = (y - Y0) / r - 0.5f;
                int i = Mathf.Clamp(Mathf.FloorToInt(fx), 0, W - 2), j = Mathf.Clamp(Mathf.FloorToInt(fy), 0, H - 2);
                float tx = Mathf.Clamp01(fx - i), ty = Mathf.Clamp01(fy - j);
                return Mathf.Lerp(Mathf.Lerp(f[j * W + i], f[j * W + i + 1], tx), Mathf.Lerp(f[(j + 1) * W + i], f[(j + 1) * W + i + 1], tx), ty);
            }
            Color Tone(float depth, float fromMade, float d)
            {
                var c = Color.Lerp(shallow, open, Mathf.SmoothStep(0f, 1f, depth / deep));
                float f = Mathf.Clamp01(1f - fromMade / reach);
                c = Color.Lerp(c, foot, f * (2f - f));
                c.a = Mathf.Clamp01((d + 1f) / 4f);
                return c;
            }

            var v = new List<Vector3>();
            var col = new List<Color>();
            var t = new List<int>();
            // fine: half a metre, wherever water is within three quarters of a metre
            const float s = 0.5f;
            int nx = Mathf.RoundToInt(W * r / s) + 1, ny = Mathf.RoundToInt(H * r / s) + 1;
            var dv = new float[nx * ny];
            var index = new int[nx * ny];
            for (int j = 0; j < ny; j++)
                for (int i = 0; i < nx; i++)
                {
                    dv[j * nx + i] = Sample(signed, X0 + i * s, Y0 + j * s);
                    index[j * nx + i] = -1;
                }
            int V(int i, int j)
            {
                int k = j * nx + i;
                if (index[k] < 0)
                {
                    float x = X0 + i * s, y = Y0 + j * s;
                    index[k] = v.Count;
                    v.Add(U(x, y, w));
                    col.Add(Tone(w - GroundTri(g, x, y), Mathf.Max(0f, (Sample(toMade, x, y) - 0.5f) * r), dv[k]));
                }
                return index[k];
            }
            for (int j = 0; j + 1 < ny; j++)
                for (int i = 0; i + 1 < nx; i++)
                {
                    int k = j * nx + i;
                    if (Mathf.Max(Mathf.Max(dv[k], dv[k + 1]), Mathf.Max(dv[k + nx], dv[k + nx + 1])) < -0.75f)
                        continue;
                    int a = V(i, j), b = V(i + 1, j), c = V(i, j + 1), d = V(i + 1, j + 1);
                    t.AddRange(new[] { a, c, b, b, c, d });
                }
            // coarse: the bay beyond, on the land's grid, its colour from the land's depth and no line
            const float cs = 25f;
            float cx0 = -1600f, cy0 = -1400f;
            int cnx = Mathf.RoundToInt(3300f / cs) + 1, cny = Mathf.RoundToInt(3300f / cs) + 1;
            int n0 = v.Count;
            for (int j = 0; j < cny; j++)
                for (int i = 0; i < cnx; i++)
                {
                    float x = cx0 + i * cs, y = cy0 + j * cs;
                    v.Add(U(x, y, w - 0.03f));
                    col.Add(Tone(w - GroundAt(cg, x, y), reach, 3f));
                }
            for (int j = 0; j + 1 < cny; j++)
                for (int i = 0; i + 1 < cnx; i++)
                {
                    int a = n0 + j * cnx + i, b = a + 1, c = a + cnx, d = c + 1;
                    t.AddRange(new[] { a, c, b, b, c, d });
                }
            var m = new Mesh { name = "water", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            m.SetVertices(v);
            m.SetColors(col);
            m.SetTriangles(t, 0);
            var up = new Vector3[v.Count];
            for (int k = 0; k < up.Length; k++)
                up[k] = Vector3.up;
            m.normals = up;
            m.RecalculateBounds();
            return m;
        }

        /// <summary>The wet band above the water on what is built in it: the quay's face, the stone pier's sides and the
        /// feet of the houses standing in the water, a hair out from each face.</summary>
        static Mesh WetBands(Town town, float high)
        {
            var mb = new MB();
            float w = town.quay.water * M, z0 = w - 0.1f, z1 = w + high;
            void Band(Vector2 a, Vector2 b, Vector2 outward)
            {
                Vector2 a1 = a + outward * 0.02f, b1 = b + outward * 0.02f;
                mb.Quad(U(a1.x, a1.y, z0), U(b1.x, b1.y, z0), U(b1.x, b1.y, z1), U(a1.x, a1.y, z1));
            }
            var q = town.quay;
            for (int i = 0; i + 1 < q.edge.Length / 2; i++)
                Band(QuayAt(q, i) + QuayOut(q, i), QuayAt(q, i + 1) + QuayOut(q, i + 1), (QuayOut(q, i) + QuayOut(q, i + 1)).normalized);
            void Ring(IList<Vector2> poly)
            {
                Vector2 c = Vector2.zero;
                foreach (var p in poly) c += p;
                c /= poly.Count;
                for (int i = 0; i < poly.Count; i++)
                {
                    Vector2 a = poly[i], b = poly[(i + 1) % poly.Count], mid = (a + b) / 2;
                    // only a face whose foot stands in the water
                    if (GroundAt(town.ground, mid.x, mid.y) > w + 0.1f && GroundAt(town.ground, a.x, a.y) > w + 0.1f && GroundAt(town.ground, b.x, b.y) > w + 0.1f)
                        continue;
                    var n = new Vector2(b.y - a.y, a.x - b.x).normalized;
                    Band(a, b, Vector2.Dot(n, mid - c) < 0f ? -n : n);
                }
            }
            if (town.piers != null)
                foreach (var p in town.piers)
                {
                    if (p.kind != "pier")
                        continue;
                    Vector2 a = new Vector2(p.points[0], p.points[1]) * M, b = new Vector2(p.points[2], p.points[3]) * M;
                    Vector2 d = (b - a).normalized, sd = new Vector2(-d.y, d.x) * (p.width * M / 2);
                    Ring(new[] { a - sd, a + sd, b + sd, b - sd });
                }
            foreach (var p in town.placements)
            {
                var fp = new Vector2[4];
                for (int k = 0; k < 4; k++)
                    fp[k] = new Vector2(p.footprint[2 * k], p.footprint[2 * k + 1]) * M;
                Ring(fp);
            }
            return mb.Make("wet bands");
        }

        /// <summary>The smau's flights: on each sloping run between the lanes it joins, steps of about 16.5 cm, each a
        /// block whose top is the run's ground at its upper end, so the risers stand out of the benched slope and the
        /// treads lie on it. Level runs across the lanes are the lanes'.</summary>
        static Mesh Stairs(Stair[] stairs, Tones tones)
        {
            var mb = new MB { tint = tones == null ? Color.white : tones.Surface("setts").linear };
            foreach (var st in stairs)
            {
                float hw = st.width * M / 2;
                for (int i = 0; i + 5 < st.points.Length; i += 3)
                {
                    var a = new Vector3(st.points[i], st.points[i + 1], st.points[i + 2]) * M;
                    var b = new Vector3(st.points[i + 3], st.points[i + 4], st.points[i + 5]) * M;
                    float dz = b.z - a.z;
                    var plan = new Vector2(b.x - a.x, b.y - a.y);
                    float L = plan.magnitude;
                    if (Mathf.Abs(dz) < 0.05f || L < 0.1f)
                        continue;
                    Vector2 d = plan / L, n = new Vector2(-d.y, d.x) * hw, a2 = new Vector2(a.x, a.y);
                    int count = Mathf.Max(1, Mathf.RoundToInt(Mathf.Abs(dz) / 0.165f));
                    for (int k = 0; k < count; k++)
                    {
                        Vector2 p0 = a2 + d * (L * k / count), p1 = a2 + d * (L * (k + 1) / count);
                        float z0 = a.z + dz * k / count, z1 = a.z + dz * (k + 1) / count;
                        mb.Add(Prism(new[] { p0 - n, p1 - n, p1 + n, p0 + n }, Mathf.Min(z0, z1) - 0.15f, Mathf.Max(z0, z1)));
                    }
                }
            }
            return mb.Make("stairs");
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

        /// <summary>A crown's mass: rings of six between a bottom and a top point, its radius at each height from prof
        /// (0 at the bottom, 1 at the top), in plan an ellipse rx by ry turned by rot; each ring point pushed in or out
        /// by up to jit of its radius (its seed's), so the facets are chunky and no two masses alike.</summary>
        static void Blob(List<Vector3> cv, List<int> ct, float x, float y, float z0, float z1, float rx, float ry, float rot,
                         Func<float, float> prof, ulong seed, float jit)
        {
            const int seg = 6, rings = 5;
            int n0 = cv.Count;
            cv.Add(U(x, y, z0 + (z1 - z0) * 0.6f * prof(0.05f) / rings));   // the underside nearly flat where the profile is full low
            for (int k = 1; k < rings; k++)
            {
                float u = k / (float)rings, f = prof(u);
                for (int s = 0; s < seg; s++)
                {
                    ulong h = Hash.Then(Hash.Then(seed, (ulong)k), (ulong)s);
                    float a = rot + (s + Hash.Range(h, -0.2f, 0.2f)) * Mathf.PI * 2f / seg;
                    float push = 1f + jit * Hash.Range(Hash.Then(h, "r"), -1f, 1f);
                    float ca = Mathf.Cos(a) * rx * f * push, sa = Mathf.Sin(a) * ry * f * push;
                    float zu = u + jit * 0.5f / rings * Hash.Range(Hash.Then(h, "z"), -1f, 1f);
                    cv.Add(U(x + ca * Mathf.Cos(rot) - sa * Mathf.Sin(rot), y + ca * Mathf.Sin(rot) + sa * Mathf.Cos(rot),
                             z0 + (z1 - z0) * zu));
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

        static (Mesh crowns, Mesh leaves, Mesh trunks) Trees(Tree[] trees, Tones facts, bool coloured)
        {
            var cv = new List<Vector3>();
            var ct = new List<int>();
            var cc = new List<Color>();
            var centres = new List<Vector3>();   // each crown vertex's mass's centre
            var lows = new List<Vector3>();      // and the point under it its facets are shaded round
            var tv = new List<Vector3>();
            var tt = new List<int>();
            var tc = new List<Color>();
            // the fringe's cards: four corners at the card's centre, their offsets across the view in uv
            var lv = new List<Vector3>();
            var luv = new List<Vector2>();
            var ln = new List<Vector3>();
            var lc = new List<Color>();
            var lt = new List<int>();
            var fr = facts.fringe;
            float fSize = F(fr["size"]), fWidth = F(fr["width"]), fTail = F(fr["tail"]), fTurn = F(fr["turn"]), fOut = F(fr["out"]),
                  fRadial = F(fr["radial"]), fJitter = F(fr["jitter"]), soften = F(fr["soften"]), lift = F(fr["lift"]),
                  fShare = F(fr["share"]);
            float Lo(string k) => F(Arr(fr[k])[0]);
            float Hi(string k) => F(Arr(fr[k])[1]);
            // a broadleaf crown is full low and rounds over at the top; a spruce is a spire
            Func<float, float> round = u => Mathf.Sqrt(Mathf.Sin(Mathf.PI * Mathf.Pow(u, 0.8f)));
            Func<float, float> cone = u => Mathf.Min(1f, u / 0.12f) * Mathf.Pow(1f - u, 0.95f);
            foreach (var tr in trees)
            {
                float x = tr.x * M, y = tr.y * M, z = tr.z * M, h = tr.h * M, r = tr.r * M;
                ulong id = Hash.Of(tr.id);
                float R(string what, int k, float lo, float hi) => Hash.Range(Hash.Then(Hash.Then(id, what), (ulong)k), lo, hi);
                float rot = R("turn", 0, 0f, Mathf.PI * 2f);
                var tint = coloured ? facts.Crown(tr).linear : Color.white;
                // the crown's edge: a leaf stroke on each upper facet of a mass, out of it a little and turned part way
                // radial, so it shades as the mass round it; the shader lays its corners across the view and opens it
                // only where the crown turns from the eye
                var limbs = new List<Vector3>();   // where each lobe hangs, for the limb that carries it
                void Fringe(int k, int t0, Vector3 centre, float size, Color c)
                {
                    for (int i = t0, j = 0; i < ct.Count; i += 3, j++)
                    {
                        Vector3 a = cv[ct[i]], b = cv[ct[i + 1]], d = cv[ct[i + 2]];
                        var n = Vector3.Cross(b - a, d - a).normalized;
                        if (Vector3.Dot(n, (a + b + d) / 3f - centre) < 0f)
                            n = -n;
                        if (n.y < -0.5f)
                            continue;   // the underside
                        ulong hk = Hash.Then(Hash.Then(Hash.Then(id, "leaf"), (ulong)k), (ulong)j);
                        float H(string what, float lo, float hi) => Hash.Range(Hash.Then(hk, what), lo, hi);
                        if (H("share", 0f, 1f) >= fShare)
                            continue;
                        float u = H("u", 0f, 1f), v = H("v", 0f, 1f);
                        if (u + v > 1f) { u = 1f - u; v = 1f - v; }
                        float len = size * H("s", Lo("spread"), Hi("spread"));
                        var at = a + (b - a) * u + (d - a) * v + n * len * fOut;
                        var jit = new Vector3(H("x", -1f, 1f), H("y", -1f, 1f), H("z", -1f, 1f));
                        var nl = (n + (at - centre).normalized * fRadial + jit * fJitter).normalized;
                        float turn = H("lean", -fTurn, fTurn), cs = Mathf.Cos(turn), sn = Mathf.Sin(turn);
                        Vector2 Corner(float px, float py) => new Vector2(px * cs - py * sn, px * sn + py * cs);
                        int n0 = lv.Count;
                        // tip, right, tail, left across the view
                        luv.Add(Corner(0f, len)); luv.Add(Corner(len * fWidth, 0f)); luv.Add(Corner(0f, -len * fTail)); luv.Add(Corner(-len * fWidth, 0f));
                        var tone = c * H("tone", Lo("tone"), Hi("tone"));
                        for (int q = 0; q < 4; q++) { lv.Add(at); ln.Add(nl); lc.Add(tone); }
                        // both windings, so the card shows however the view's axes turn it
                        lt.AddRange(new[] { n0, n0 + 1, n0 + 2, n0, n0 + 2, n0 + 3, n0, n0 + 2, n0 + 1, n0, n0 + 3, n0 + 2 });
                    }
                }
                // one mass of the crown, a little lighter or darker than the next (claiming nothing), and its fringe
                void Mass(int k, float mx, float my, float z0, float z1, float rx, float ry, float a, Func<float, float> prof, float jit)
                {
                    int t0 = ct.Count;
                    Blob(cv, ct, mx, my, z0, z1, rx, ry, a, prof, Hash.Then(id, (ulong)k), jit);
                    var c = tint * R("tone", k, 0.86f, 1.1f);
                    var centre = U(mx, my, (z0 + z1) / 2f);
                    var low = U(mx, my, (z0 + z1) / 2f - lift * (z1 - z0) / 2f);
                    while (cc.Count < cv.Count)
                    {
                        cc.Add(c);
                        centres.Add(centre);
                        lows.Add(low);
                    }
                    if (k > 0)
                        limbs.Add(U(mx, my, z0 + 0.3f * (z1 - z0)));
                    Fringe(k, t0, low, fSize * (rx + ry) / 2f, c);
                }
                // lobes round the main mass, at their own heights and sides
                void Lobes(int n, float c0, float off0, float off1, float rk0, float rk1, float zb1, float hz0, float hz1)
                {
                    for (int k = 1; k <= n; k++)
                    {
                        float a = rot + k * 2.4f + R("a", k, -0.5f, 0.5f), off = r * R("off", k, off0, off1);
                        float zb = z + c0 + (h - c0) * R("zb", k, 0f, zb1);
                        Mass(k, x + Mathf.Cos(a) * off, y + Mathf.Sin(a) * off, zb, Mathf.Min(z + h * 0.97f, zb + (h - c0) * R("hz", k, hz0, hz1)),
                             r * R("rk", k, rk0, rk1), r * R("ryk", k, rk0 * 0.85f, rk1 * 0.9f), a, round, 0.22f);
                    }
                }
                float c0;
                switch (tr.crown)
                {
                    case "cone":
                        c0 = 0.04f * h;
                        Mass(0, x, y, z + c0, z + h, r, r, rot, cone, 0.12f);
                        break;
                    case "tall":
                        // a birch: a tall narrow mass and two or three lobes hung off it, low on a tree grown in the open
                        c0 = 0.22f * h;
                        Mass(0, x, y, z + c0, z + h, r * 0.72f, r * R("ry", 0, 0.6f, 0.72f), rot, round, 0.2f);
                        Lobes(2 + (R("n", 0, 0f, 1f) < 0.5f ? 1 : 0), c0, 0.35f, 0.6f, 0.45f, 0.62f, 0.4f, 0.4f, 0.65f);
                        break;
                    case "flat":
                        // a pine: a bare trunk, an open crown of three masses, the top one widest, leaning with the wind
                        c0 = 0.38f * h;
                        for (int k = 0; k < 3; k++)
                        {
                            float a = rot + k * 2.1f + R("a", k, -0.4f, 0.4f), off = k == 0 ? r * 0.15f : r * R("off", k, 0.3f, 0.5f);
                            float zb = z + c0 + (h - c0) * (k == 0 ? 0.3f : R("zb", k, 0f, 0.35f));
                            Mass(k, x + Mathf.Cos(a) * off, y + Mathf.Sin(a) * off, zb, zb + (h - c0) * R("hz", k, 0.55f, 0.7f),
                                 r * (k == 0 ? 0.85f : R("rk", k, 0.55f, 0.7f)), r * R("ryk", k, 0.5f, 0.7f), a, round, 0.18f);
                        }
                        break;
                    default:
                        // a sycamore, rowan or apple: a domed crown with three lobes, so its outline is a cloud, not a ball
                        c0 = Mathf.Max(1.6f, 0.25f * h);
                        Mass(0, x, y, z + c0, z + h, r * 0.8f, r * R("ry", 0, 0.7f, 0.85f), rot, round, 0.18f);
                        Lobes(3, c0, 0.4f, 0.6f, 0.45f, 0.62f, 0.3f, 0.45f, 0.7f);
                        break;
                }
                // the trunk: six sides from below the ground into the crown, its girth by its height, half at the top
                var (bark, girth) = facts.Trunk(tr);
                float w0 = girth * h / 2f, w1 = w0 / 2f, zt = z + c0 + (h - c0) * 0.3f;
                int m0 = tv.Count;
                for (int s6 = 0; s6 < 6; s6++)
                {
                    float a = rot + s6 * Mathf.PI / 3f;
                    tv.Add(U(x + Mathf.Cos(a) * w0, y + Mathf.Sin(a) * w0, z - 1f));
                    tv.Add(U(x + Mathf.Cos(a) * w1, y + Mathf.Sin(a) * w1, zt));
                }
                for (int s6 = 0; s6 < 6; s6++)
                {
                    int a0 = m0 + 2 * s6, b0 = m0 + 2 * ((s6 + 1) % 6);
                    tt.AddRange(new[] { a0, a0 + 1, b0 + 1, a0, b0 + 1, b0 });
                }
                // the limbs: the trunk forks below its top into one limb for each lobe, four-sided, thinning out
                var fork = U(x, y, zt - (zt - z - c0) * 0.6f);
                foreach (var end in limbs)
                {
                    var dir = (end - fork).normalized;
                    var side = Vector3.Cross(dir, Vector3.up).normalized;
                    if (side.sqrMagnitude < 0.5f)
                        side = Vector3.right;
                    var up2 = Vector3.Cross(side, dir);
                    int l0 = tv.Count;
                    for (int s4 = 0; s4 < 4; s4++)
                    {
                        float a = s4 * Mathf.PI / 2f;
                        var o = side * Mathf.Cos(a) + up2 * Mathf.Sin(a);
                        tv.Add(fork + o * w1 * 0.8f);
                        tv.Add(end + o * w1 * 0.35f);
                    }
                    for (int s4 = 0; s4 < 4; s4++)
                    {
                        int a0 = l0 + 2 * s4, b0 = l0 + 2 * ((s4 + 1) % 4);
                        tt.AddRange(new[] { a0, a0 + 1, b0 + 1, a0, b0 + 1, b0 });
                    }
                }
                var barkC = coloured ? bark.linear : Color.white;
                while (tc.Count < tv.Count)
                    tc.Add(barkC);
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
            var crowns = Make("tree crowns", fv, ft, fc);
            // each facet shaded part way to its mass's round, so the planes are a hint across a lit and a shaded side;
            // the round taken from a point under the mass's middle, so its underside turns to the sky's light as a
            // crown's leaves let it through, and never goes black
            var fn = crowns.normals;
            for (int i = 0; i < fn.Length; i++)
            {
                if (Vector3.Dot(fn[i], fv[i] - centres[ct[i]]) < 0f)
                    fn[i] = -fn[i];
                fn[i] = Vector3.Lerp(fn[i], (fv[i] - lows[ct[i]]).normalized, soften).normalized;
            }
            crowns.normals = fn;
            var trunks = Make("tree trunks", tv, tt, tc);
            DoubleSided(trunks);
            var leaves = new Mesh { name = "tree fringe", indexFormat = IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
            leaves.SetVertices(lv);
            leaves.SetUVs(0, luv);
            leaves.SetNormals(ln);
            leaves.SetColors(lc);
            leaves.SetTriangles(lt, 0);
            // the cards open across the view from their centres: room in the bounds for the widest
            var bounds = leaves.bounds;
            bounds.Expand(4f);
            leaves.bounds = bounds;
            return (crowns, leaves, trunks);
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
            /// <summary>A quad seen from both sides.</summary>
            public void Both(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { Quad(a, b, c, d); Quad(d, c, b, a); }
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

        /// <summary>What closes a plot: a fence as a panel from the ground to its height along each run, a post at each
        /// end (white pickets, plank fences in the weathered boards); a hedge as one faceted mass along its run, its top
        /// a little uneven; a dry-stone wall to its height, or across a fall a terrace wall from the low side's foot to a
        /// little over the high side.</summary>
        static (Mesh pickets, Mesh planks, Mesh hedges, Mesh stones) Fences(Fence[] fences, Grid g, Tones tones)
        {
            var pickets = new MB();
            var planks = new MB();
            var hedges = new MB();
            var stones = new MB();
            foreach (var f in fences)
            {
                float h = f.height * M, hw = f.width * M / 2;
                ulong seed = Hash.Of($"town.fence.{f.id}");
                for (int i = 0; i + 3 < f.points.Length; i += 2)
                {
                    Vector2 a = new Vector2(f.points[i], f.points[i + 1]) * M, b = new Vector2(f.points[i + 2], f.points[i + 3]) * M;
                    float za = GroundAt(g, a.x, a.y), zb = GroundAt(g, b.x, b.y);
                    if (f.kind == "hedge")
                    {
                        hedges.tint = tones == null ? Color.white : tones.Hedge(f).linear;
                        Hedge(hedges, a, b, h, hw, g, seed);
                        continue;
                    }
                    if (f.kind == "stone")
                    {
                        Vector2 d = (b - a).normalized, n = new Vector2(-d.y, d.x);
                        float Top(Vector2 q)
                        {
                            float l = GroundAt(g, q.x - n.x * 0.8f, q.y - n.y * 0.8f), r = GroundAt(g, q.x + n.x * 0.8f, q.y + n.y * 0.8f);
                            return Mathf.Abs(l - r) > 0.5f ? Mathf.Max(l, r) + 0.35f : GroundAt(g, q.x, q.y) + h;
                        }
                        float Foot(Vector2 q) => Mathf.Min(GroundAt(g, q.x - n.x * 0.8f, q.y - n.y * 0.8f), GroundAt(g, q.x + n.x * 0.8f, q.y + n.y * 0.8f)) - 0.2f;
                        Vector2 s0 = n * hw;
                        float ta = Top(a), tb = Top(b), fa = Foot(a), fb = Foot(b);
                        stones.Quad(U(a.x - s0.x, a.y - s0.y, fa), U(b.x - s0.x, b.y - s0.y, fb), U(b.x - s0.x, b.y - s0.y, tb), U(a.x - s0.x, a.y - s0.y, ta));
                        stones.Quad(U(a.x + s0.x, a.y + s0.y, fa), U(b.x + s0.x, b.y + s0.y, fb), U(b.x + s0.x, b.y + s0.y, tb), U(a.x + s0.x, a.y + s0.y, ta));
                        stones.Quad(U(a.x - s0.x, a.y - s0.y, ta), U(b.x - s0.x, b.y - s0.y, tb), U(b.x + s0.x, b.y + s0.y, tb), U(a.x + s0.x, a.y + s0.y, ta));
                        stones.Quad(U(a.x - s0.x, a.y - s0.y, fa), U(a.x - s0.x, a.y - s0.y, ta), U(a.x + s0.x, a.y + s0.y, ta), U(a.x + s0.x, a.y + s0.y, fa));
                        stones.Quad(U(b.x - s0.x, b.y - s0.y, fb), U(b.x - s0.x, b.y - s0.y, tb), U(b.x + s0.x, b.y + s0.y, tb), U(b.x + s0.x, b.y + s0.y, fb));
                        continue;
                    }
                    // a board's thickness, its two faces and its top, so it is there from either side
                    var mb = f.kind == "plank" ? planks : pickets;
                    Vector2 dd = (b - a).normalized, t = new Vector2(-dd.y, dd.x) * Mathf.Max(hw, 0.025f);
                    foreach (var sgn in new[] { -1f, 1f })
                        mb.Both(U(a.x + sgn * t.x, a.y + sgn * t.y, za - 0.1f), U(b.x + sgn * t.x, b.y + sgn * t.y, zb - 0.1f), U(b.x + sgn * t.x, b.y + sgn * t.y, zb + h), U(a.x + sgn * t.x, a.y + sgn * t.y, za + h));
                    mb.Both(U(a.x - t.x, a.y - t.y, za + h), U(b.x - t.x, b.y - t.y, zb + h), U(b.x + t.x, b.y + t.y, zb + h), U(a.x + t.x, a.y + t.y, za + h));
                    foreach (var (q, zq) in new[] { (a, za), (b, zb) })
                        mb.Add(Prism(new[] { q + new Vector2(-0.06f, -0.06f), q + new Vector2(0.06f, -0.06f), q + new Vector2(0.06f, 0.06f), q + new Vector2(-0.06f, 0.06f) }, zq - 0.1f, zq + h + 0.1f));
                }
            }
            return (pickets.Make("fences"), planks.Make("plank fences"), hedges.Make("hedges"), stones.Make("dry-stone walls"));
        }

        /// <summary>A clipped hedge along a run: stations about a metre and a half apart, each a section of five points
        /// (its foot, its swelling sides, its flat top), the top's height and the sides' swell a little apart from
        /// station to station, so the planes between them catch the light unevenly, as a clipped hedge does.</summary>
        static void Hedge(MB mb, Vector2 a, Vector2 b, float h, float hw, Grid g, ulong seed)
        {
            float L = (b - a).magnitude;
            if (L < 0.1f)
                return;
            Vector2 d = (b - a) / L, n = new Vector2(-d.y, d.x);
            int count = Mathf.Max(1, Mathf.RoundToInt(L / 1.5f));
            var ring = new Vector3[count + 1][];
            for (int k = 0; k <= count; k++)
            {
                // a hedge ends a little short of its run's ends, rounded off
                float t = Mathf.Lerp(Mathf.Min(0.3f, L * 0.2f), L - Mathf.Min(0.3f, L * 0.2f), k / (float)count);
                var q = a + d * t;
                float z = GroundAt(g, q.x, q.y);
                ulong sk = Hash.Then(seed, $"{Mathf.RoundToInt(q.x * 10)},{Mathf.RoundToInt(q.y * 10)}");
                float top = h * Hash.Range(Hash.Then(sk, "h"), 0.9f, 1.08f), swell = hw * Hash.Range(Hash.Then(sk, "w"), 0.9f, 1.12f);
                bool end = k == 0 || k == count;
                float sw = end ? swell * 0.8f : swell;
                ring[k] = new[]
                {
                    U(q.x - n.x * sw * 0.85f, q.y - n.y * sw * 0.85f, z - 0.1f),
                    U(q.x - n.x * sw, q.y - n.y * sw, z + top * 0.55f),
                    U(q.x - n.x * sw * 0.6f, q.y - n.y * sw * 0.6f, z + top),
                    U(q.x + n.x * sw * 0.6f, q.y + n.y * sw * 0.6f, z + top),
                    U(q.x + n.x * sw, q.y + n.y * sw, z + top * 0.55f),
                    U(q.x + n.x * sw * 0.85f, q.y + n.y * sw * 0.85f, z - 0.1f),
                };
            }
            for (int k = 0; k < count; k++)
                for (int e = 0; e < 5; e++)
                    mb.Quad(ring[k][e], ring[k + 1][e], ring[k + 1][e + 1], ring[k][e + 1]);
            foreach (var r in new[] { ring[0], ring[count] })
            {
                mb.Quad(r[0], r[1], r[4], r[5]);
                mb.Quad(r[1], r[2], r[3], r[4]);
            }
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
        static readonly float[] Stations = { 0f, 0.14f, 0.48f, 0.8f, 1f };

        /// <summary>A hull's half-beam at each station, as a share of its beam: a færing pointed at both ends.</summary>
        static float[] HalfBeams(Boat bt) =>
            bt.kind == "faering" ? new[] { 0.06f, 0.62f, 1f, 0.62f, 0.04f } : new[] { 0.8f, 0.96f, 1f, 0.72f, 0.03f };

        /// <summary>A boat's outline at its gunwale, in plan.</summary>
        static Vector2[] HullPlan(Boat bt)
        {
            float L = bt.length * M, B = bt.beam * M, ang = bt.angle * Mathf.Deg2Rad;
            Vector2 f = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)), sd = new Vector2(-f.y, f.x), o = new Vector2(bt.x, bt.y) * M;
            var hb = HalfBeams(bt);
            var plan = new Vector2[2 * Stations.Length];
            for (int k = 0; k < Stations.Length; k++)
            {
                var c = o + f * ((Stations[k] - 0.5f) * L);
                plan[k] = c + sd * (hb[k] * B / 2);
                plan[plan.Length - 1 - k] = c - sd * (hb[k] * B / 2);
            }
            return plan;
        }

        static Mesh Boats(Boat[] boats, float water, Tones tones)
        {
            var mb = new MB();
            var st = Stations;
            foreach (var bt in boats)
            {
                Color hullC = tones == null ? Color.white : tones.Boat(bt).linear;
                Color inside = tones == null ? Color.white : (bt.deck == "open" ? tones.boatOpen : tones.boatDecked).linear;
                float L = bt.length * M, B = bt.beam * M, ang = bt.angle * Mathf.Deg2Rad;
                Vector2 f = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)), sd = new Vector2(-f.y, f.x), o = new Vector2(bt.x, bt.y) * M;
                bool faering = bt.kind == "faering";
                var hb = HalfBeams(bt);
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
                mb.tint = hullC;
                for (int k = 0; k + 1 < st.Length; k++)
                {
                    mb.Quad(K(k, 1f), K(k + 1, 1f), G(k + 1, 1f), G(k, 1f));
                    mb.Quad(K(k, -1f), G(k, -1f), G(k + 1, -1f), K(k + 1, -1f));
                }
                mb.Quad(K(0, -1f), K(0, 1f), G(0, 1f), G(0, -1f));
                // the inside: the hull's sides narrowing from the gunwale to the deck (or the open boat's floor) a
                // little below it, so from above a boat is its gunwale's pale rim round its inside
                mb.tint = inside;
                Vector3 I(int k, float side) => G(k, side * 0.85f, -0.2f);
                for (int k = 0; k + 1 < st.Length; k++)
                {
                    mb.Quad(I(k, -1f), I(k, 1f), I(k + 1, 1f), I(k + 1, -1f));
                    mb.Quad(I(k, 1f), G(k, 1f), G(k + 1, 1f), I(k + 1, 1f));
                    mb.Quad(I(k, -1f), I(k + 1, -1f), G(k + 1, -1f), G(k, -1f));
                }
                mb.Quad(I(0, -1f), G(0, -1f), G(0, 1f), I(0, 1f));
                mb.tint = hullC;
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

        /// <summary>A house's chimneys on its ridge (along it from its middle, off it to the side): each one's centre in
        /// plan, the ridge's direction and the one across it, its half-size and the height of its top.</summary>
        static List<(Vector2 c, Vector2 rd, Vector2 xd, float hs, float top)> Stacks(Placement p)
        {
            var list = new List<(Vector2, Vector2, Vector2, float, float)>();
            if (p.chimneys == null || p.chimneys.Length < 4 || p.roof == "spire")
                return list;
            var fp = new Vector2[4];
            for (int i = 0; i < 4; i++)
                fp[i] = new Vector2(p.footprint[2 * i] * M, p.footprint[2 * i + 1] * M);
            float e = p.eave * M;
            Vector2 u0 = (fp[1] - fp[0]).normalized, n0 = (fp[3] - fp[0]).normalized;
            float W0 = Vector2.Distance(fp[0], fp[1]), D0 = Vector2.Distance(fp[0], fp[3]);
            bool gable = p.roof == "gable";
            Vector2 rd = gable ? n0 : u0, xd = gable ? u0 : n0, mid = 0.5f * (fp[0] + fp[2]);
            float tanr = Mathf.Tan(p.pitch * Mathf.Deg2Rad), zr = e + (gable ? W0 : D0) / 2 * tanr;
            for (int i = 0; i + 3 < p.chimneys.Length; i += 4)
            {
                float al = p.chimneys[i] * M, ac = p.chimneys[i + 1] * M, hs = p.chimneys[i + 2] * M / 2, up = p.chimneys[i + 3] * M;
                list.Add((mid + rd * al + xd * ac, rd, xd, hs, zr - ac * tanr + up));
            }
            return list;
        }

        /// <summary>The smoke of the stoves lit at the moment (town.json, smoke): from the first chimney's crown of each
        /// home whose stove burns, a plume of soft puffs that rises, then bends over in the air and drifts, widening and
        /// thinning; each puff a disc the shader turns to the eye (Shaders/TownSmoke.shader), its corner in uv, its
        /// radius and opacity in uv2.</summary>
        static Mesh Smoke(Town town, Tones facts)
        {
            var sm = facts.smoke;
            var v = new List<Vector3>();
            var uv = new List<Vector2>();
            var uv2 = new List<Vector2>();
            var t = new List<int>();
            float rise = F(sm["riseM"]), opacity = F(sm["opacity"]), toward = F(sm["towardDeg"]) * Mathf.Deg2Rad;
            var len = Arr(sm["lengthM"]);
            var wid = Arr(sm["widthM"]);
            int puffs = Mathf.Max(2, (int)F(sm["puffs"]));
            var corners = new[] { new Vector2(-1f, -1f), new Vector2(1f, -1f), new Vector2(1f, 1f), new Vector2(-1f, 1f) };
            foreach (var p in town.placements)
            {
                if (!facts.Smoking(p))
                    continue;
                var stacks = Stacks(p);
                if (stacks.Count == 0)
                    continue;
                var (c, _, _, _, top) = stacks[0];
                ulong seed = Hash.Of($"town.smoke.{p.id}");
                float L = Hash.Range(Hash.Then(seed, "length"), F(len[0]), F(len[1]));
                float a = toward + Hash.Range(Hash.Then(seed, "turn"), -0.2f, 0.2f);
                Vector2 dir = new Vector2(Mathf.Cos(a), Mathf.Sin(a)), side = new Vector2(-dir.y, dir.x);
                for (int k = 0; k < puffs; k++)
                {
                    float f = k / (float)(puffs - 1);
                    ulong sk = Hash.Then(seed, $"{k}");
                    float w = Mathf.Lerp(F(wid[0]), F(wid[1]), Mathf.Pow(f, 0.8f)) * Hash.Range(Hash.Then(sk, "w"), 0.8f, 1.2f);
                    // up first, then bent over by the air: slow along the drift at first, its rise levelling off
                    Vector2 q = c + dir * (L * Mathf.Pow(f, 1.5f)) + side * (w * 0.25f * Hash.Range(Hash.Then(sk, "s"), -1f, 1f));
                    float z = top + 0.2f + rise * (1f - Mathf.Exp(-6f * f)) + w * 0.15f * Hash.Range(Hash.Then(sk, "z"), -1f, 1f);
                    var centre = U(q.x, q.y, z);
                    var puff = new Vector2(w / 2f, opacity * Mathf.Pow(1f - f, 1.3f));
                    int n = v.Count;
                    foreach (var corner in corners)
                    {
                        v.Add(centre);
                        uv.Add(corner);
                        uv2.Add(puff);
                    }
                    t.AddRange(new[] { n, n + 1, n + 2, n, n + 2, n + 3 });
                }
            }
            var m = new Mesh { name = "smoke", hideFlags = HideFlags.DontSave, indexFormat = IndexFormat.UInt32 };
            m.SetVertices(v);
            m.SetUVs(0, uv);
            m.SetUVs(1, uv2);
            m.SetTriangles(t, 0);
            // the puffs' corners are spread by the shader, so the bounds take their widest
            m.RecalculateBounds();
            var bb = m.bounds;
            bb.Expand(F(wid[1]) * 1.2f);
            m.bounds = bb;
            return m;
        }

        static (Mesh body, Mesh roof, Mesh foot) Masses(Placement p, Grid g, float overhang)
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
            // an ark stands on the house's walls, not on the ground
            var foot = p.kind == "ark" ? new Mesh { name = "none", hideFlags = HideFlags.DontSave } : Prism(fp, low - 0.3f, b);
            var stacks = Stacks(p);
            if (stacks.Count > 0)
            {
                // the chimneys, up from the eaves to their rise above the roof where they stand; in the plinth's mesh
                var mb = new MB();
                mb.Add(foot);
                foreach (var (c, rd, xd, hs, top) in stacks)
                {
                    float hc = hs + 0.06f;
                    mb.Add(Prism(new[] { c - rd * hs - xd * hs, c + rd * hs - xd * hs, c + rd * hs + xd * hs, c - rd * hs + xd * hs },
                                 e, top));
                    // its crown: a course corbelled out round the top, so it reads as a stack and not a post
                    mb.Add(Prism(new[] { c - rd * hc - xd * hc, c + rd * hc - xd * hc, c + rd * hc + xd * hc, c - rd * hc + xd * hc },
                                 top - 0.16f, top + 0.02f));
                }
                foot = mb.Make("plinth and chimneys");
            }
            // the roof: ridge along the front (eaves) or front to back (gable), the eaves and verges out by the era's
            Vector2 u = (fp[1] - fp[0]).normalized, n = (fp[3] - fp[0]).normalized;
            float W = Vector2.Distance(fp[0], fp[1]), D = Vector2.Distance(fp[0], fp[3]);
            float o = overhang, tan = Mathf.Tan(p.pitch * Mathf.Deg2Rad);
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
            else if (p.roof == "shed")
            {
                // a lean-to's: high against the house at its front, falling away to its back; its ends walled up to it
                Quad(P(0, 0, e + (D + o) * tan), P(L, 0, e + (D + o) * tan), P(L, S, e - o * tan), P(0, S, e - o * tan));
                Gable(P(o, o, e), P(o, o, e + D * tan), P(o, S - o, e));
                Gable(P(L - o, S - o, e), P(L - o, o, e + D * tan), P(L - o, o, e));
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
            // what each wall sees of the sky, for the town shader's contact shade (_Contact): its height above the foot
            // (green) and, on the walls under the eaves (along the ridge), its depth below them (blue), in tens of metres
            var body = walls.Make("walls");
            Vector2 ridge = p.roof == "gable" ? (fp[3] - fp[0]).normalized : (fp[1] - fp[0]).normalized;
            var bv = body.vertices;
            var bn = body.normals;
            var bc = new Color[bv.Length];
            for (int i = 0; i < bv.Length; i++)
            {
                var flat = new Vector2(bn[i].x, bn[i].z);
                bool under = Mathf.Abs(bn[i].y) < 0.5f && flat.sqrMagnitude > 1e-4f && Mathf.Abs(Vector2.Dot(flat.normalized, ridge)) < 0.3f;
                bc[i] = new Color(1f, Mathf.Clamp01((bv[i].y - b) / 10f), under ? Mathf.Clamp01((e - bv[i].y) / 10f) : 1f, 1f);
            }
            body.colors = bc;
            return (body, roof, foot);
        }

        /// <summary>The roof's edges as the era made them (timber.json, verge and eaves): a barge board under each rake of a
        /// gable, out at the roof's edge, and the fascia along the eaves where the era has one, both in the trim's paint.</summary>
        static void Roofline(Placement p, Tones f, float o, MB trim)
        {
            if (p.roof != "gable" && p.roof != "eaves" || p.kind == "outhouse")
                return;
            var fp = new Vector2[4];
            for (int i = 0; i < 4; i++)
                fp[i] = new Vector2(p.footprint[2 * i] * M, p.footprint[2 * i + 1] * M);
            var wk = f.Working(p);
            var verge = Obj(wk["verge"]);
            float board = F(verge["boardMm"]) * M, fascia = F(Obj(wk["eaves"])["fasciaMm"]) * M;
            float e = p.eave * M, tan = Mathf.Tan(p.pitch * Mathf.Deg2Rad), cos = Mathf.Cos(p.pitch * Mathf.Deg2Rad);
            Vector2 u = (fp[1] - fp[0]).normalized, n = (fp[3] - fp[0]).normalized;
            float W = Vector2.Distance(fp[0], fp[1]), D = Vector2.Distance(fp[0], fp[3]);
            Vector2 c0 = fp[0] - u * o - n * o;
            float L = W + 2 * o, S = D + 2 * o, ze = e - o * tan;
            bool gable = p.roof == "gable";
            // (s along u, w along n); the gables stand at w 0 and S on a gable roof, at s 0 and L on an eaves roof
            Vector3 P(float s, float w, float z) { var q = c0 + u * s + n * w; return U(q.x, q.y, z); }
            void Both(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { trim.Quad(a, b, c, d); trim.Quad(d, c, b, a); }
            trim.tint = f.Paint(p, "trim").linear;
            float drop = board / cos, span = (gable ? L : S) / 2, zr = ze + span * tan;
            for (int end = 0; end < 2; end++)
            {
                float at = end == 0 ? -0.01f : (gable ? S : L) + 0.01f;
                Vector3 G(float along, float z) => gable ? P(along, at, z) : P(at, along, z);
                Both(G(0, ze + 0.02f), G(span, zr + 0.02f), G(span, zr - drop), G(0, ze - drop));
                Both(G(span, zr + 0.02f), G(2 * span, ze + 0.02f), G(2 * span, ze - drop), G(span, zr - drop));
            }
            if (fascia <= 0f)
                return;
            for (int side = 0; side < 2; side++)
            {
                float at = side == 0 ? -0.01f : (gable ? L : S) + 0.01f, run = gable ? S : L;
                Vector3 E(float along, float z) => gable ? P(at, along, z) : P(along, at, z);
                Both(E(0, ze + 0.02f), E(run, ze + 0.02f), E(run, ze - fascia), E(0, ze - fascia));
            }
        }

        /// <summary>Where a wall's openings sit (their centres), as tools/houses.py sets them: the first and last at the
        /// working's distance from the corners, the rest evenly between, the fewest that keep the spacing within its
        /// widest.</summary>
        static List<float> Bays(float length, float b1, float edge, float b0)
        {
            float room = length - 2 * edge;
            if (room < b0 * 0.75f)
                return new List<float> { length / 2 };
            int gaps = Mathf.Max(1, Mathf.CeilToInt(room / b1 - 1e-6f));
            var s = new List<float>();
            for (int i = 0; i <= gaps; i++)
                s.Add(edge + room * i / gaps);
            return s;
        }

        /// <summary>A building's openings at the city tier, where its builder set them (timber.json, workings: the
        /// windows in bays on each storey, the door in the front, the gables' loft windows; town.json, openings: a
        /// sjøhus's windows, hatches and port, the church's), as its diary has them in 1989: a window replaced in its
        /// year's kind, the ground floor boarded on an empty house. Each window its casing in the trim's paint, its sash
        /// in the window's and its glass in panes; the corner boards in the trim's paint; a stone step up to the door.
        /// The panes' vertex alpha is their room's light at the evening's moment.</summary>
        static void Openings(Placement p, Grid g, Tones f, MB trim, MB panes)
        {
            if (p.kind == "tower")
                return;
            var fp = new Vector2[4];
            for (int i = 0; i < 4; i++)
                fp[i] = new Vector2(p.footprint[2 * i] * M, p.footprint[2 * i + 1] * M);
            Vector2 centre = 0.25f * (fp[0] + fp[1] + fp[2] + fp[3]);
            float b = p.@base * M, e = p.eave * M;
            bool gableRoof = p.roof == "gable";
            float W = Vector2.Distance(fp[0], fp[1]), D = Vector2.Distance(fp[0], fp[3]);
            float zr = e + (gableRoof ? W : D) / 2 * Mathf.Tan(p.pitch * Mathf.Deg2Rad);
            var wk = f.Working(p);
            var op = Obj(wk["openings"]);
            var cs = Obj(wk["casing"]);
            float storey = (F(wk["storeyMm"]) + F(wk["floorMm"])) * M;
            float cw = F(cs["widthMm"]) * M, head = (F(cs["headMm"]) + F(cs["capMm"])) * M, sillC = F(cs["sillMm"]) * M;
            int full = Mathf.Max(1, Mathf.FloorToInt((e - b + 0.6f) / storey));
            string boarded = f.Boarded(p);
            Color trimC = f.Paint(p, "trim").linear, doorC = f.Paint(p, "door").linear, boards = f.boards.linear;
            var windows = Obj(f.timber["windows"]);
            bool house = p.kind == "house" || p.kind == "wing";
            Dictionary<string, object> kindOp = f.openings.TryGetValue(p.kind, out var ko) ? Obj(ko) : null;

            for (int i = 0; i < 4; i++)
            {
                Vector2 a = fp[i], c = fp[(i + 1) % 4];
                float L = Vector2.Distance(a, c);
                Vector2 d = (c - a) / L, nrm = new Vector2(d.y, -d.x);
                if (Vector2.Dot(nrm, 0.5f * (a + c) - centre) < 0f)
                    nrm = -nrm;
                bool gableEnd = gableRoof ? i % 2 == 0 : i % 2 == 1;
                float Half(float z) => z <= e ? L / 2 : L / 2 * (zr - z) / (zr - e);

                void Rect(MB mb, float s0, float s1, float z0, float z1, float off)
                {
                    Vector2 p0 = a + d * s0 + nrm * off, p1 = a + d * s1 + nrm * off;
                    mb.Quad(U(p0.x, p0.y, z0), U(p1.x, p1.y, z0), U(p1.x, p1.y, z1), U(p0.x, p0.y, z1));
                }

                // a window: its casing (none where it was lost with the old window), its sash, its glass in its columns
                void Window(float s, float z0, float w, float h, string kind, int year, bool shut, string room)
                {
                    var spec = Obj(windows[kind]);
                    bool lost = (string)spec["trims"] == "lost";
                    if (!lost)
                    {
                        trim.tint = trimC;
                        Rect(trim, s - w / 2 - cw, s + w / 2 + cw, z0 - sillC, z0 + h + head, 0.02f);
                    }
                    if (shut)
                    {
                        trim.tint = boards;
                        Rect(trim, s - w / 2, s + w / 2, z0, z0 + h, 0.03f);
                        return;
                    }
                    trim.tint = (year > Last(p) ? f.PaintOf(year, p, "window") : f.Paint(p, "window")).linear;
                    Rect(trim, s - w / 2, s + w / 2, z0, z0 + h, 0.03f);
                    float fr = (F(spec["frameMm"]) + F(spec["sashMm"])) * M, post = F(spec["frameMm"]) * M;
                    int cols = (int)F(spec["cols"]);
                    float pw = (w - 2 * fr - (cols - 1) * post) / cols;
                    var gl = f.Pane(p, room);
                    panes.tint = new Color(gl.r, gl.g, gl.b, f.Lit(p, room) ? 1f : 0f);
                    for (int k = 0; k < cols; k++)
                    {
                        float x0 = s - w / 2 + fr + k * (pw + post);
                        Rect(panes, x0, x0 + pw, z0 + fr, z0 + h - fr, 0.04f);
                    }
                }

                // a door: its casing, its leaves (or the boards over them), a stone step up from the ground to its sill
                void Door(float s, float w, float h, float threshold)
                {
                    trim.tint = trimC;
                    Rect(trim, s - w / 2 - cw, s + w / 2 + cw, b, b + threshold + h + head, 0.02f);
                    trim.tint = boarded != "" ? boards : doorC;
                    Rect(trim, s - w / 2, s + w / 2, b + threshold, b + threshold + h, 0.03f);
                    Vector2 q = a + d * s;
                    float gz = GroundAt(g, q.x + nrm.x * 0.6f, q.y + nrm.y * 0.6f);
                    if (b - gz > 0.08f)
                    {
                        Vector2 hw = d * (w / 2 + 0.25f), o = nrm * 0.9f;
                        trim.tint = f.stone.linear;
                        trim.Add(Prism(new[] { q - hw, q + hw, q + hw + o, q - hw + o }, gz - 0.2f, b));
                    }
                }

                // the corner boards, at both ends of the wall up to its eaves; under an eave they stop at the roof's
                // underside, which falls away from the wall as they stand proud of it
                if (p.kind != "outhouse")
                {
                    var corner = Obj(wk["corner"]);
                    float wc = F(corner["widthMm"]) * M, pc = F(corner["proudMm"]) * M;
                    float top = gableEnd ? e : e - (pc + 0.03f) * Mathf.Tan(p.pitch * Mathf.Deg2Rad);
                    trim.tint = trimC;
                    Rect(trim, 0f, wc, b, top, pc);
                    Rect(trim, L - wc, L, b, top, pc);
                }

                if (house)
                {
                    var (wkind, wyear) = f.WindowAt(p, i, false);
                    var spec = Obj(windows[wkind]);
                    float w = F(spec["wMm"]) * M, h = F(spec["hMm"]) * M, sill = F(op["sillMm"]) * M;
                    var bays = Bays(L, F(Arr(op["bayMm"])[1]) * M, F(op["edgeMm"]) * M, F(Arr(op["bayMm"])[0]) * M);
                    // the door on a house's front: the era's, in its middle or its first bay; it takes the bays it stands in
                    float sd = -100f, clear = 0f;
                    if (i == 0 && p.kind == "house" && op.TryGetValue("door", out var dk) && dk != null)
                    {
                        var dsp = Obj(Obj(f.timber["doors"])[(string)op["doorKind"]]);
                        float dw = F(dsp["wMm"]) * M;
                        sd = (string)dk == "centre" ? L / 2 : bays[0];
                        clear = dw / 2 + cw * 2 + w / 2 + 0.1f;
                        Door(sd, dw, F(dsp["hMm"]) * M, F(dsp["thresholdMm"]) * M);
                    }
                    for (int k = 0; k < full; k++)
                    {
                        float z0 = b + k * storey + sill;
                        if (z0 + h > e - 0.1f)
                            break;
                        for (int j = 0; j < bays.Count; j++)
                            if (k > 0 || Mathf.Abs(bays[j] - sd) > clear)
                                Window(bays[j], z0, w, h, wkind, wyear, k == 0 && boarded != "" || boarded == "all",
                                       $"{i}.{k}.{j / 2}");
                    }
                    // the loft's windows in a gable, on its floor: a storey and a floor's depth over the top storey
                    if (gableEnd && zr - e > 1.9f)
                    {
                        var (ukind, uyear) = f.WindowAt(p, i, true);
                        var us = Obj(windows[ukind]);
                        float uw = F(us["wMm"]) * M * 0.8f, uh = F(us["hMm"]) * M * 0.72f;
                        float zu = b + full * storey + sill * 0.75f;
                        if (zu + uh < zr - 0.6f && Half(zu + uh) > uw)
                        {
                            bool pair = (string)op["gable"] == "pair" && Half(zu + uh) > uw + 0.6f;
                            foreach (var s in pair ? new[] { L / 2 - uw * 0.75f, L / 2 + uw * 0.75f } : new[] { L / 2 })
                                Window(s, zu, uw, uh, ukind, uyear, boarded == "all", $"{i}.loft");
                        }
                    }
                }
                else if (p.kind == "warehouse" && kindOp != null)
                {
                    var ws = Obj(kindOp["window"]);
                    float w = F(ws["wMm"]) * M, h = F(ws["hMm"]) * M, sill = F(kindOp["sillMm"]) * M;
                    if (!gableEnd)
                    {
                        var bays = Bays(L, F(Arr(kindOp["bayMm"])[1]) * M, F(kindOp["edgeMm"]) * M, F(Arr(kindOp["bayMm"])[0]) * M);
                        for (int k = 0; k < full; k++)
                        {
                            float z0 = b + k * storey + sill;
                            if (z0 + h > e - 0.1f)
                                break;
                            for (int j = 0; j < bays.Count; j++)
                                Window(bays[j], z0, w, h, (string)op["window"], 0, boarded == "all" || k == 0 && boarded != "",
                                       $"{i}.{k}.{j / 2}");
                        }
                    }
                    else
                    {
                        // the gable: the port on the quay, a hatch on each floor above it and one in the loft
                        var port = Obj(kindOp["port"]);
                        var hatch = Obj(kindOp["hatch"]);
                        float hw = F(hatch["wMm"]) * M, hh = F(hatch["hMm"]) * M;
                        if (i == 0)
                            Door(L / 2, F(port["wMm"]) * M, F(port["hMm"]) * M, 0f);
                        for (int k = 1; k <= full; k++)
                        {
                            float z0 = b + k * storey + 0.3f;
                            if (z0 + hh > zr - 0.5f || Half(z0 + hh) < hw / 2 + cw + 0.2f)
                                break;
                            trim.tint = trimC;
                            Rect(trim, L / 2 - hw / 2 - cw, L / 2 + hw / 2 + cw, z0 - sillC, z0 + hh + head, 0.02f);
                            trim.tint = doorC;
                            Rect(trim, L / 2 - hw / 2, L / 2 + hw / 2, z0, z0 + hh, 0.03f);
                        }
                    }
                }
                else if (p.kind == "church" && kindOp != null)
                {
                    var ws = Obj(kindOp["window"]);
                    float w = F(ws["wMm"]) * M, h = F(ws["hMm"]) * M, sill = F(kindOp["sillMm"]) * M;
                    if (!gableEnd)
                        foreach (var s in Bays(L, F(Arr(kindOp["bayMm"])[1]) * M, F(kindOp["edgeMm"]) * M, F(Arr(kindOp["bayMm"])[0]) * M))
                            if (b + sill + h < e - 0.3f)
                                Window(s, b + sill, w, h, (string)op["window"], 0, false, $"{i}");
                    string[] names = { "front", "right", "back", "left" };
                    if (names[i] == (string)kindOp["doorWall"])
                    {
                        var dsp = Obj(kindOp["door"]);
                        Door(L / 2, F(dsp["wMm"]) * M, F(dsp["hMm"]) * M, 0.15f);
                    }
                }
                else if (p.kind == "ark" && i == 0)
                {
                    // the ark's front: the loft's windows, a pair where it is wide enough
                    var (akind, ayear) = f.WindowAt(p, 0, true);
                    var spec = Obj(windows[akind]);
                    float w = F(spec["wMm"]) * M * 0.9f, z0 = b + 0.55f, h = Mathf.Min(F(spec["hMm"]) * M * 0.85f, e - 0.15f - z0);
                    foreach (var s in L >= 2 * w + 1f ? new[] { L / 2 - w * 0.65f, L / 2 + w * 0.65f } : new[] { L / 2 })
                        Window(s, z0, w, h, akind, ayear, boarded == "all", "ark");
                }
                else if (p.kind == "porch" && kindOp != null)
                {
                    // the porch's door in its gable to the lane; its sides glazed where its era glazed them
                    if (i == 0)
                    {
                        var dsp = Obj(kindOp["door"]);
                        Door(L / 2, F(dsp["wMm"]) * M, F(dsp["hMm"]) * M, 0.05f);
                    }
                    else if (i != 2 && Arr(kindOp["glazed"]).Contains(f.Era(p)))
                    {
                        var ws = Obj(kindOp["window"]);
                        Window(L / 2, b + F(kindOp["sillMm"]) * M, F(ws["wMm"]) * M, F(ws["hMm"]) * M,
                               (string)op["window"], 0, boarded != "", "porch");
                    }
                }
                else if (p.kind == "lean-to" && kindOp != null && i == 2)
                {
                    var ws = Obj(kindOp["window"]);
                    var (lkind, lyear) = f.WindowAt(p, 2, false);
                    Window(L / 2, b + F(kindOp["sillMm"]) * M, F(ws["wMm"]) * M, F(ws["hMm"]) * M, lkind, lyear,
                           boarded == "all", "lean-to");
                }
                else if (p.kind == "outhouse" && kindOp != null && i == 0)
                {
                    var dsp = Obj(kindOp["door"]);
                    Door(L / 2, F(dsp["wMm"]) * M, F(dsp["hMm"]) * M, 0.05f);
                }
            }

            int Last(Placement q) => f.Painted(q);
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
