using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Play;
using Overstory.Scenes;
using Debug = UnityEngine.Debug;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The walk (LT1g, Phase 1a; reviews/lt1/playable/outline.md §2, W1 and W2): the corner composed inside the clay
    /// town as the player walks it, and the player built from it.
    ///
    /// Compose writes the generated scene (ScenePath, never kept in git): the heart's clay, staged as the gully's frames
    /// stage it (LT1Stone.Stage: the stone stair and cheek walls, the rigs and styles, the town's globals); the corner's
    /// five houses at 1989 in place of the heart's grey masses for them, each where export_time.py put it from the
    /// heart's footprint in the diaries (HousesRecord; LT1Time.PlaceHouses); the corner's birch (LT1Perf.PlantBirch);
    /// and the play object, with PlayCorner (the five judging views, the three judging lights, the heart's moods) and
    /// FrameTimeOverlay. Nothing in it is invented: every place, rig and mood comes from the records and tools named.
    /// It refuses to run unless the gully's stair and walls hash as accepted (Stairs, Walls: blender/tools/mesh_hash.py
    /// recomputes them from the FBX), and it never saves the heart's scene: Stage opens it, and the composed scene is
    /// saved as a copy by its own path. Then it opens what it saved and checks it (Check), and checks what the walker
    /// collides with (CheckProxies). The walker, its keys and its proxies are W4's (LT1PlayWalk.cs: AddWalk).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Play.Compose
    ///         [-stills reviews/lt1/playable/walk/w1] [-moments 1300-drizzle] [-views eye-foot,...]
    ///         [-houses Assets/Art/Buildings/time/time.json]   (another set of houses at 1989, to compare)
    ///     Unity ... -executeMethod Overstory.EditorTools.LT1Play.Build      (Compose, then the player at App)
    ///     Unity ... -executeMethod Overstory.EditorTools.LT1Play.Check      (the saved scene checked again)
    ///
    /// The lamps as the facts have them in 1989 (W3): the heart's lights.json lights a shopfront wherever heart_layout
    /// draws one, but a house's shop lights burn only if its diary (reviews/lt1/time/readers/diaries.json, the real
    /// arm) gives it a business in the composed year. ShopLights drops the others' and writes the rest to Generated/
    /// (LampsAt), which the scene's TownLights reads; the heart's own lights.json and scene are left as they are.
    ///
    /// The views: the five judging views (keys 1 to 5), then LT1g's four (keys 6 to 9; CaseViews): eye level at A's
    /// window, on the steps, on the Row, and at the Anchor's door. Those four are authored vantages, placed from the
    /// footprints in the diaries and from the places record (PlacesRecord: the Anchor cast onto Harbour Row 24, authored).
    ///
    /// -stills renders each view (in drizzle unless -moments says otherwise) from the saved scene at the
    /// player's size (PlayerFrame), as PlayCorner shows it. tools/playable.sh runs Build under the Unity lock and puts
    /// back the settings a build rewrites.
    ///
    /// For the stages after W2: W3's harness arm can call ComposeOpen() and add its runner before saving elsewhere;
    /// LT1Perf.BuildPlayer(app, scenePath) builds any scene with the harness's player settings.
    /// </summary>
    public static partial class LT1Play
    {
        public const string Generated = "Assets/Experiments/LT1/Playable/Generated";
        public const string ScenePath = Generated + "/LT1_Playable.unity";
        /// <summary>The corner's houses at 1989, stronger (export_time.py --out Assets/Art/Buildings/playable).</summary>
        public const string HousesRecord = "Assets/Art/Buildings/playable/manifest.json";
        public const string App = "Builds/Playable/OverstoryPlayable.app";     // in unity/, not kept in git
        /// <summary>The corner's diaries (the real arm's events) and the houses' footprints on the heart's layout.</summary>
        public const string Diaries = "reviews/lt1/time/readers/diaries.json";
        /// <summary>Where the engine's places stand on the heart's layout in 1989: authored (the Anchor, pl-bar).</summary>
        public const string PlacesRecord = "fixtures/lt1-places-1989.json";
        /// <summary>The lamps as the facts have them in the composed year, written by ShopLights (never kept in git).</summary>
        public const string LampsAt = Generated + "/lights-1989.json";
        /// <summary>How far round a house's footprint its own shop lights may stand (they hang 0.4 m out of its front).</summary>
        const float ShopReach = 1.0f;
        const float Lens28 = 46.4f, Lens35 = 37.8f;     // (as LT1Stone's)
        /// <summary>The gully's accepted mesh hashes (docs/measuring.md, Mesh hashes; accepted by Øystein, 22 October).</summary>
        public const string Stairs = "bff7858b698f3efd", Walls = "0a3d7db3100df20b";
        const string StoneArt = "Assets/Art/Stone";
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const string HousesRoot = "The corner's houses (1989)";
        const string PlayRoot = "Play (the walk)";
        const string Arm = "real", Style = "stronger";
        const int Year = 1989, HouseCount = 5;
        const string Blender = "/Applications/Blender.app/Contents/MacOS/Blender";
        /// <summary>The five judging views (docs/foundations.md), in LT1Stone.Views' order: keys 1 to 5.</summary>
        static readonly string[] ViewNames = { "eye-foot", "eye-on", "street", "into12", "high" };
        /// <summary>LT1g's four views (docs/experiments.md, LT1g), after the judging views: keys 6 to 9.</summary>
        public static readonly string[] CaseViewNames = { "a-window", "steps", "row", "anchor-door" };

        // -- the gully unchanged ---------------------------------------------------------------------------------------

        /// <summary>
        /// The gully's stair and cheek walls hashed from their FBX by mesh_hash.py (never re-imported) and compared with
        /// the manifest beside them, and the manifest with the accepted hashes. Throws if anything differs.
        /// </summary>
        public static (string stairs, string walls) GullyHashes()
        {
            if (gullyChecked)
                return (Stairs, Walls);     // (the FBX do not change within one run)
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string art = Path.Combine(root, "unity", StoneArt);
            var manifest = File.ReadAllText(Path.Combine(art, "mesh-hashes.json"));
            foreach (var (file, want) in new[] { ("stone_gully.fbx", Stairs), ("stone_gully_cheeks.fbx", Walls) })
            {
                var entry = JsonUtility.FromJson<HashEntryHolder>("{\"e\":" + ManifestEntry(manifest, file) + "}").e;
                if (entry == null || entry.hash != want)
                    throw new System.Exception($"[LT1Play] the gully's manifest holds {file} {entry?.hash ?? "nothing"}, not the accepted {want}: Compose refuses to run");
            }
            var args = new[] { "-b", "--factory-startup", "--python", Path.Combine(root, "blender", "tools", "mesh_hash.py"), "--",
                               "check", Path.Combine(art, "stone_gully.fbx"), Path.Combine(art, "stone_gully_cheeks.fbx") };
            var psi = new ProcessStartInfo(Blender, string.Join(" ", args.Select(a => "\"" + a.Replace("\"", "\\\"") + "\"")))
            {
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true,
                WorkingDirectory = root,
            };
            string output;
            int code;
            using (var p = Process.Start(psi))
            {
                var err = p.StandardError.ReadToEndAsync();
                output = p.StandardOutput.ReadToEnd();
                p.WaitForExit();
                code = p.ExitCode;
                _ = err.Result;
            }
            var lines = output.Split('\n').Where(l => l.StartsWith("SAME") || l.StartsWith("CHANGED") || l.StartsWith("NO ") || l.StartsWith("NOT ") || l.StartsWith("  ")).ToList();
            bool same = code == 0
                && lines.Contains($"SAME stone_gully.fbx {Stairs}")
                && lines.Contains($"SAME stone_gully_cheeks.fbx {Walls}");
            if (!same)
                throw new System.Exception($"[LT1Play] the gully's hashes differ from the accepted (exit {code}): Compose refuses to run\n{string.Join("\n", lines)}");
            Debug.Log($"[LT1Play] the gully unchanged: stairs {Stairs}, walls {Walls} (recomputed from the FBX by mesh_hash.py)");
            gullyChecked = true;
            return (Stairs, Walls);
        }

        static bool gullyChecked;

        [System.Serializable] class HashEntry { public string hash; public int triangles; }
        [System.Serializable] class HashEntryHolder { public HashEntry e; }

        /// <summary>One file's entry in a mesh-hashes.json, as JSON text (its top-level hash and triangles are read from it).</summary>
        static string ManifestEntry(string manifest, string file)
        {
            int i = manifest.IndexOf($"\"{file}\"", System.StringComparison.Ordinal);
            if (i < 0)
                return "null";
            int start = manifest.IndexOf('{', i), depth = 0;
            for (int k = start; k < manifest.Length; k++)
            {
                if (manifest[k] == '{') depth++;
                else if (manifest[k] == '}' && --depth == 0)
                    return manifest.Substring(start, k - start + 1);
            }
            return "null";
        }

        // -- compose -------------------------------------------------------------------------------------------------

        /// <summary>The corner composed and saved, then checked from what was saved; stills with -stills.</summary>
        public static void Compose()
        {
            var clock = Stopwatch.StartNew();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            try
            {
                var (stage, corner) = ComposeOpen();
                AddWalk(stage, corner);     // (the walk's own scene only: the harness arm composes without it)
                Save();
            }
            finally
            {
                urp.shadowDistance = reach;
            }
            Debug.Log($"[LT1Play] composed in {clock.Elapsed.TotalSeconds:F0} s");
            Check();
            CheckProxies();
            string stills = Cli.Arg("-stills", null);
            if (stills != null)
                Stills(Cli.RepoPath("-stills", stills));
        }

        /// <summary>
        /// The corner composed in the open scene, unsaved (Stage opens the heart's scene; nothing saves it): the stage
        /// and the play object. For W3's harness arm, which adds its runner and saves elsewhere.
        /// </summary>
        public static (StreetStage stage, PlayCorner corner) ComposeOpen()
        {
            GullyHashes();
            string record = Records();
            var export = LT1Time.Houses(record);
            var rows = export.buildings.Where(b => b.arm == Arm && b.year == Year).OrderBy(b => b.letter).ToList();
            if ((record == HousesRecord && export.style != Style) || rows.Count != HouseCount)
                throw new System.Exception($"[LT1Play] {record} holds {rows.Count} houses at {Year} in style {export.style}, " +
                                           $"not {HouseCount} at {Style}: run blender/tools/export_time.py --style {Style} --arms {Arm} --years {Year} --out Assets/Art/Buildings/playable");

            var (stage, stone) = LT1Stone.Stage(false);

            // the corner's houses in place of the heart's grey masses for them (as LT1Time stands them)
            var heart = GameObject.Find("The heart (clay)") ?? throw new MissingReferenceException("[LT1Play] no heart in the scene");
            var masses = heart.transform.Find("buildings_corner") ?? throw new MissingReferenceException("[LT1Play] the heart has no buildings_corner to replace");
            masses.gameObject.SetActive(false);
            var houses = new GameObject(HousesRoot).transform;
            houses.SetParent(heart.transform, false);
            var street = AssetDatabase.LoadAssetAtPath<Material>("Assets/Art/Materials/M_Street.mat");
            var placed = LT1Time.PlaceHouses(houses, export, Arm, Year, street);

            // the corner's birch in C's yard (as the harness plants it)
            var (_, birch, _, height) = LT1Perf.PlantBirch();

            // what the player switches between: the judging views, lights and moods, in their tools' order
            var play = new GameObject(PlayRoot);
            var corner = play.AddComponent<PlayCorner>();
            play.AddComponent<FrameTimeOverlay>();
            corner.stage = stage;
            corner.views = ViewNames.Select(n => LT1Stone.Views.First(v => v.name == n))
                .Select(v => new PlayCorner.View { name = v.name, position = v.pos, target = v.target, fov = v.fov })
                .Concat(CaseViews()).ToArray();

            // the lamps as the facts have them in 1989: a shop's light only where a business is
            var dark = ShopLights(stage);
            corner.moments = LT1Stone.Moments.Select(m => new PlayCorner.Moment
            {
                name = m,
                rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{m}.asset")
                      ?? throw new FileNotFoundException($"[LT1Play] no rig {m}: LT1Heart.Rigs writes it"),
            }).ToArray();
            corner.moods = LT1Heart.Moods
                .Select(m => new PlayCorner.Mood { name = m, grade = AssetDatabase.LoadAssetAtPath<Grade>($"{Lights}/Moods/Mood_{m}.asset") })
                .Where(m => m.grade != null).ToArray();
            corner.view = 0;
            corner.moment = 0;
            corner.mood = -1;
            var leaves = birch.GetComponentsInChildren<MeshRenderer>();
            corner.boundsOf = leaves;
            corner.bounds = leaves.Select(r => r.localBounds).ToArray();
            corner.keep = new[] { Shader.Find("Hidden/Overstory/TownHeight"), Shader.Find("Hidden/Overstory/SkyMapProbe") }
                .Where(s => s != null).ToArray();

            // the first view and light, as the player opens on them (the camera placed, the shot left out of the scene)
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            stage.rig = corner.moments[0].rig;
            stage.mood = null;
            LT1Stone.Aim(stage, shot, LT1Stone.Views.First(v => v.name == ViewNames[0]));
            stage.shot = null;
            Object.DestroyImmediate(shot);
            if (stage.skyMap != null)
                stage.skyMap.Build();     // the town's sky map over the houses, the stone and the birch

            Debug.Log($"[LT1Play] the corner: stone {stone.name}; {placed.Count} houses ({string.Join(", ", placed.Select(h => h.name))}); " +
                      $"the birch {height:F1} m; {corner.views.Length} views, {corner.moments.Length} lights, {corner.moods.Length} moods; " +
                      $"no business in {Year}: {(dark.Count == 0 ? "none" : string.Join(", ", dark))}");
            return (stage, corner);
        }

        // -- the facts: businesses, shop lights, places ------------------------------------------------------------------

        [System.Serializable] public class Footprint { public float ox, oy, angle, w, d, @base; }
        [System.Serializable] public class HouseAt { public string letter; public int id; public Footprint heart; }
        [System.Serializable] class HousesHolder { public HouseAt[] houses; }
        [System.Serializable] class DiaryEvent { public int id, year; public string kind, cause; }
        [System.Serializable] class Diary { public int id; public DiaryEvent[] events; }
        [System.Serializable] public class Lamp { public float x, y, z, dx, dy; public string kind; }
        [System.Serializable] class Lamps { public Lamp[] lamps; }

        [System.Serializable] public class PlaceFacing { public float x, y; }
        [System.Serializable] public class PlaceDoor { public float x, y, z; public PlaceFacing facing; }
        [System.Serializable] public class PlaceBuilding { public string layout, key; public float ox, oy, angle, w, d, @base, eave; }
        [System.Serializable] public class Place { public string id, name, provenance, cause; public PlaceBuilding building; public PlaceDoor door; }
        [System.Serializable] class Places { public int schemaVersion, year; public Place[] places; }

        static string RepoFile(string path) => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", path));

        /// <summary>The corner's houses with their footprints on the heart's layout (the diaries' houses).</summary>
        public static HouseAt[] Houses() =>
            JsonUtility.FromJson<HousesHolder>(File.ReadAllText(RepoFile(Diaries))).houses;

        /// <summary>
        /// Each house's business in a year from its diary (the real arm): open if the last of its business_opened,
        /// business_closed and shop_removed events up to that year (by year, then the diary's order) opened one.
        /// </summary>
        public static Dictionary<string, bool> Businesses(int year)
        {
            string text = File.ReadAllText(RepoFile(Diaries));
            var real = Json.Members(text).FirstOrDefault(m => m.name == "real").value
                       ?? throw new System.Exception($"[LT1Play] {Diaries} has no real arm");
            var open = new Dictionary<string, bool>();
            foreach (var (letter, value) in Json.Members(real))
            {
                var events = JsonUtility.FromJson<Diary>(value).events ?? new DiaryEvent[0];
                var last = events.Select((e, i) => (e, i))
                    .Where(t => t.e.year <= year && (t.e.kind == "business_opened" || t.e.kind == "business_closed" || t.e.kind == "shop_removed"))
                    .OrderBy(t => t.e.year).ThenBy(t => t.i).Select(t => t.e).LastOrDefault();
                open[letter] = last != null && last.kind == "business_opened";
            }
            return open;
        }

        /// <summary>A point in a footprint's own frame: u along its front, v back from it (heart_layout's _local, inverted).</summary>
        static Vector2 Local(Footprint f, float x, float y)
        {
            float a = f.angle * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            return new Vector2((x - f.ox) * c + (y - f.oy) * s, -(x - f.ox) * s + (y - f.oy) * c);
        }

        /// <summary>A point given in a footprint's own frame, in street metres (heart_layout's _local).</summary>
        static Vector2 World(Footprint f, float u, float v)
        {
            float a = f.angle * Mathf.Deg2Rad, c = Mathf.Cos(a), s = Mathf.Sin(a);
            return new Vector2(f.ox + u * c - v * s, f.oy + u * s + v * c);
        }

        static bool Near(Footprint f, float x, float y, float reach)
        {
            var p = Local(f, x, y);
            return p.x >= -reach && p.x <= f.w + reach && p.y >= -reach && p.y <= f.d + reach;
        }

        /// <summary>
        /// The heart's lamps with every shop light dropped that stands at a house with no business in the composed year
        /// (within ShopReach of its footprint), written to LampsAt and given to the stage's TownLights. Returns the dark
        /// houses' letters; logs each lamp dropped and why.
        /// </summary>
        static List<string> ShopLights(StreetStage stage)
        {
            var lights = stage.townLights ?? throw new MissingReferenceException("[LT1Play] the stage has no town lights");
            if (lights.source == null)
                throw new MissingReferenceException("[LT1Play] the town lights have no lights.json");
            var all = JsonUtility.FromJson<Lamps>(lights.source.text).lamps;
            var open = Businesses(Year);
            var dark = Houses().Where(h => open.TryGetValue(h.letter, out bool o) && !o).ToList();
            var dropped = new List<string>();
            var kept = all.Where(l =>
            {
                if (l.kind != "shop")
                    return true;
                var at = dark.FirstOrDefault(h => Near(h.heart, l.x, l.y, ShopReach));
                if (at == null)
                    return true;
                dropped.Add($"({l.x:F2}, {l.y:F2}) at {at.letter}");
                return false;
            }).ToArray();
            Directory.CreateDirectory(RepoFile("unity/" + Generated));
            File.WriteAllText(RepoFile("unity/" + LampsAt), JsonUtility.ToJson(new Lamps { lamps = kept }, true));
            AssetDatabase.ImportAsset(LampsAt, ImportAssetOptions.ForceSynchronousImport);
            lights.source = AssetDatabase.LoadAssetAtPath<TextAsset>(LampsAt)
                            ?? throw new FileNotFoundException($"[LT1Play] {LampsAt} did not import");
            lights.Build();
            Debug.Log($"[LT1Play] the lamps in {Year}: {kept.Length} of {all.Length} ({all.Count(l => l.kind == "shop")} shop lights in the heart's); " +
                      $"dropped {dropped.Count}, a shop's light where its diary has no business in {Year}: " +
                      $"{(dropped.Count == 0 ? "none" : string.Join(", ", dropped))}");
            return dark.Select(h => h.letter).ToList();
        }

        /// <summary>
        /// The members of a JSON object as raw text (JsonUtility reads no dictionaries, and the diaries key their arm by
        /// letter): each member's name and its value's text, in order, without parsing the values.
        /// </summary>
        static class Json
        {
            public static List<(string name, string value)> Members(string obj)
            {
                var members = new List<(string, string)>();
                int i = Space(obj, 0);
                if (i >= obj.Length || obj[i] != '{')
                    throw new System.FormatException("[LT1Play] not a JSON object");
                i = Space(obj, i + 1);
                while (i < obj.Length && obj[i] != '}')
                {
                    int nameEnd = Skip(obj, i);
                    string name = obj.Substring(i + 1, nameEnd - i - 2);
                    i = Space(obj, nameEnd);
                    if (obj[i] != ':')
                        throw new System.FormatException($"[LT1Play] no ':' after \"{name}\"");
                    int start = Space(obj, i + 1), end = Skip(obj, start);
                    members.Add((name, obj.Substring(start, end - start)));
                    i = Space(obj, end);
                    if (i < obj.Length && obj[i] == ',')
                        i = Space(obj, i + 1);
                }
                return members;
            }

            static int Space(string s, int i)
            {
                while (i < s.Length && char.IsWhiteSpace(s[i]))
                    i++;
                return i;
            }

            /// <summary>The index just past the value starting at i (a string, an object or array, or a bare word).</summary>
            static int Skip(string s, int i)
            {
                if (s[i] == '"')
                {
                    for (int k = i + 1; k < s.Length; k++)
                        if (s[k] == '\\') k++;
                        else if (s[k] == '"') return k + 1;
                    throw new System.FormatException("[LT1Play] an unclosed string");
                }
                if (s[i] == '{' || s[i] == '[')
                {
                    int depth = 0;
                    for (int k = i; k < s.Length; k++)
                    {
                        char c = s[k];
                        if (c == '"') { k = Skip(s, k) - 1; continue; }
                        if (c == '{' || c == '[') depth++;
                        else if ((c == '}' || c == ']') && --depth == 0) return k + 1;
                    }
                    throw new System.FormatException("[LT1Play] an unclosed object or array");
                }
                int e = i;
                while (e < s.Length && s[e] != ',' && s[e] != '}' && s[e] != ']' && !char.IsWhiteSpace(s[e]))
                    e++;
                return e;
            }
        }

        /// <summary>The places record (PlacesRecord): where the engine's places stand on the heart's layout, authored.</summary>
        public static Place PlaceOf(string id)
        {
            var places = JsonUtility.FromJson<Places>(File.ReadAllText(RepoFile(PlacesRecord)));
            if (places.year != Year)
                throw new System.Exception($"[LT1Play] {PlacesRecord} is for {places.year}, not {Year}");
            return places.places.FirstOrDefault(p => p.id == id)
                   ?? throw new System.Exception($"[LT1Play] {PlacesRecord} has no {id}");
        }

        /// <summary>
        /// LT1g's four views, authored vantages at eye level (1.6 to 1.65 m) placed from the facts' footprints, in street
        /// metres: at A's window (on the pavement at A's corner, beside its end window, looking up the lane and the steps), on the steps (on the Landing,
        /// looking up the upper flight to E), on the Row (across the quay road from the lane's mouth, looking up the
        /// lane), and at the Anchor's door (two metres out from it, looking along the Row to the corner).
        /// </summary>
        public static PlayCorner.View[] CaseViews()
        {
            var a = Houses().First(h => h.letter == "A").heart;
            var window = World(a, a.w + 0.3f, -1.2f);     // (on the pavement at A's corner, its end window at the left edge)
            var anchor = PlaceOf("pl-bar");
            var door = anchor.door;
            var facing = new Vector2(door.facing.x, door.facing.y).normalized;
            return new[]
            {
                new PlayCorner.View { name = "a-window", position = new Vector3(window.x, window.y, a.@base + 1.6f),
                                      target = new Vector3(48.6f, 33.0f, 6.8f), fov = Lens35 },
                new PlayCorner.View { name = "steps", position = new Vector3(47.6f, 45.0f, 8.0f + 1.65f),
                                      target = new Vector3(46.6f, 84.0f, 17.6f), fov = Lens35 },
                new PlayCorner.View { name = "row", position = new Vector3(52.4f, -10.0f, 1.9f + 1.65f),
                                      target = new Vector3(48.6f, 30.7f, 6.0f), fov = Lens28 },
                new PlayCorner.View { name = "anchor-door", position = new Vector3(door.x + 2f * facing.x, door.y + 2f * facing.y, door.z + 1.65f),
                                      target = new Vector3(49.3f, 1.0f, 3.8f), fov = Lens35 },
            };
        }

        /// <summary>The houses' record: the walk's own, or another set of export_time.py's with -houses (to compare).</summary>
        static string Records() => Cli.Arg("-houses", HousesRecord);

        /// <summary>The open scene saved as a copy into Generated/ (the heart's scene stays as it was on disk).</summary>
        static void Save()
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath, "..", Generated));
            AssetDatabase.Refresh();
            var scene = EditorSceneManager.GetActiveScene();
            if (!EditorSceneManager.SaveScene(scene, ScenePath, true))
                throw new System.Exception($"[LT1Play] could not save {ScenePath}");
            Debug.Log($"[LT1Play] saved {ScenePath} (the open scene, {scene.path}, not saved)");
        }

        // -- check -----------------------------------------------------------------------------------------------------

        /// <summary>
        /// The saved scene opened and checked: the gully's hashes, the stone in it from the hashed FBX, the five houses
        /// from the record, the birch, the three lights. Throws on any miss, so a batch run exits with an error.
        /// </summary>
        public static void Check()
        {
            var (stairs, walls) = GullyHashes();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var problems = new List<string>();
            string Source(GameObject go) => AssetDatabase.GetAssetPath(PrefabUtility.GetCorrespondingObjectFromSource(go));
            var roots = Object.FindObjectsByType<Transform>(FindObjectsInactive.Include)
                .Where(t => PrefabUtility.IsOutermostPrefabInstanceRoot(t.gameObject)).Select(t => t.gameObject).ToList();

            int stoneStairs = roots.Count(g => Source(g) == $"{StoneArt}/stone_gully.fbx");
            int stoneWalls = roots.Count(g => Source(g) == $"{StoneArt}/stone_gully_cheeks.fbx");
            if (stoneStairs != 1 || stoneWalls != 1)
                problems.Add($"the gully in the scene: {stoneStairs} stairs and {stoneWalls} cheek walls from the hashed FBX, not 1 and 1");

            var export = LT1Time.Houses(Records());
            var want = export.buildings.Where(b => b.arm == Arm && b.year == Year).ToDictionary(b => b.file);
            var housesRoot = GameObject.Find(HousesRoot);
            var houses = housesRoot == null ? new List<GameObject>()
                : housesRoot.transform.Cast<Transform>().Select(t => t.gameObject).Where(g => g.activeInHierarchy).ToList();
            var houseLines = new List<string>();
            foreach (var h in houses)
            {
                string src = Source(h);
                if (!want.TryGetValue(src, out var row))
                {
                    problems.Add($"a house not in the record: {h.name} from {src}");
                    continue;
                }
                var at = Overstory.World.StreetSpace.ToUnity(row.position.V);
                if ((h.transform.localPosition - at).sqrMagnitude > 1e-6f)
                    problems.Add($"{h.name} stands at {h.transform.localPosition}, not the record's {at}");
                houseLines.Add($"{row.letter} ({row.id}) {row.hash ?? "no hash"} {row.tris} triangles");
            }
            if (houses.Count != HouseCount)
                problems.Add($"{houses.Count} houses, not {HouseCount}");
            var masses = GameObject.Find("The heart (clay)")?.transform.Find("buildings_corner");
            if (masses == null || masses.gameObject.activeSelf)
                problems.Add("the heart's grey masses for the houses are still shown");

            var trees = GameObject.Find(LT1Perf.BirchRoot);
            int birches = trees == null ? 0 : trees.transform.Cast<Transform>().Count(t => Source(t.gameObject).StartsWith("Assets/Art/Trees/birch/"));
            if (birches != 1)
                problems.Add($"{birches} birches, not 1");

            var corner = Object.FindAnyObjectByType<PlayCorner>();
            int rigs = corner == null || corner.moments == null ? 0 : corner.moments.Select(m => m.rig).Where(r => r != null).Distinct().Count();
            if (rigs != LT1Stone.Moments.Length)
                problems.Add($"{rigs} light rigs, not {LT1Stone.Moments.Length}");
            int views = corner == null || corner.views == null ? 0 : corner.views.Length;
            var viewNames = ViewNames.Concat(CaseViewNames).ToArray();
            if (corner != null && corner.views != null && !corner.views.Select(v => v.name).SequenceEqual(viewNames))
                problems.Add($"the views {string.Join(", ", corner.views.Select(v => v.name))}, not {string.Join(", ", viewNames)}");

            // the lamps: the scene's are the composed year's, and no shop light stands at a house with no business
            var town = corner?.stage?.townLights;
            string lampsAt = town == null || town.source == null ? "none" : AssetDatabase.GetAssetPath(town.source);
            if (lampsAt != LampsAt)
                problems.Add($"the town's lamps from {lampsAt}, not {LampsAt}");
            var open = Businesses(Year);
            var lamps = town?.source == null ? new Lamp[0] : JsonUtility.FromJson<Lamps>(town.source.text).lamps;
            var wrong = lamps.Where(l => l.kind == "shop")
                .SelectMany(l => Houses().Where(h => open.TryGetValue(h.letter, out bool o) && !o && Near(h.heart, l.x, l.y, ShopReach))
                    .Select(h => $"({l.x:F2}, {l.y:F2}) at {h.letter}")).ToList();
            if (wrong.Count > 0)
                problems.Add($"shop lights at a house with no business in {Year}: {string.Join(", ", wrong)}");
            if (corner != null && corner.stage == null)
                problems.Add("the play object has no stage");
            if (Object.FindAnyObjectByType<FrameTimeOverlay>() == null)
                problems.Add("no frame-time overlay");

            Debug.Log($"[LT1Play] check {ScenePath}:\n" +
                      $"  the gully: stairs {stairs}, walls {walls} (accepted {Stairs}, {Walls}); in the scene {stoneStairs} stairs, {stoneWalls} cheek walls\n" +
                      $"  {houses.Count} houses at {Year} ({export.style}): {string.Join("; ", houseLines)}\n" +
                      $"  {birches} birch\n" +
                      $"  lamps from {lampsAt}: {lamps.Length}, {lamps.Count(l => l.kind == "shop")} shop lights; a business in {Year}: " +
                      $"{string.Join(", ", open.Select(o => $"{o.Key} {(o.Value ? "yes" : "no")}"))}\n" +
                      $"  {rigs} rigs: {(corner == null ? "" : string.Join(", ", corner.moments.Select(m => m.name)))}\n" +
                      $"  {views} views: {(corner == null ? "" : string.Join(", ", corner.views.Select(v => v.name)))}; " +
                      $"{(corner?.moods?.Length ?? 0)} moods: {(corner == null ? "" : string.Join(", ", corner.moods.Select(m => m.name)))}\n" +
                      $"  {(problems.Count == 0 ? "PASS" : "FAIL: " + string.Join("; ", problems))}");
            if (problems.Count > 0)
                throw new System.Exception("[LT1Play] the composed scene fails its check: " + string.Join("; ", problems));
        }

        // -- stills ------------------------------------------------------------------------------------------------------

        /// <summary>Each view of the saved scene at the player's size, as PlayCorner shows it, in the lights asked.</summary>
        static void Stills(string outDir)
        {
            if (EditorSceneManager.GetActiveScene().path != ScenePath)
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var corner = Object.FindAnyObjectByType<PlayCorner>();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            try
            {
                corner.Begin();
                for (int m = 0; m < corner.moments.Length; m++)
                {
                    if (!Cli.Wanted("-moments", corner.moments[m].name) || (Cli.Arg("-moments", null) == null && m != 0))
                        continue;     // (drizzle alone unless -moments asks for others)
                    corner.SetLight(m);
                    for (int v = 0; v < corner.views.Length; v++)
                    {
                        if (!Cli.Wanted("-views", corner.views[v].name))
                            continue;
                        corner.SetView(v);
                        string file = Path.Combine(outDir, $"{corner.views[v].name}-{corner.moments[m].name}.png");
                        using (var frame = new PlayerFrame(corner.stage.view))
                        {
                            frame.Render(LT1Time.WarmUp + 1);
                            frame.Save(file);
                        }
                        Debug.Log($"[LT1Play] {file}");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
            }
        }

        // -- the player ----------------------------------------------------------------------------------------------

        /// <summary>
        /// Compose, then the macOS player of the composed scene at App: full screen at 2560 by 1440 with frame timing
        /// stats on (LT1Perf.BuildPlayer), MSAA 4x from the standalone quality level's pipeline (PC_RPAsset), checked
        /// here, never changed. Logs how long Compose and the build each took.
        /// </summary>
        public static void Build()
        {
            var clock = Stopwatch.StartNew();
            Compose();
            double composed = clock.Elapsed.TotalSeconds;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            if (urp.msaaSampleCount != 4)
                throw new System.Exception($"[LT1Play] the pipeline ({urp.name}) draws MSAA {urp.msaaSampleCount}x, not the game's 4x");
            string app = Path.GetFullPath(Path.Combine(Application.dataPath, "..", App));
            if (!LT1Perf.BuildPlayer(app, ScenePath))
                throw new System.Exception("[LT1Play] the player did not build");
            Debug.Log($"[LT1Play] built {app} ({urp.name}, MSAA {urp.msaaSampleCount}x, 2560x1440): compose and check " +
                      $"{composed:F0} s, build {clock.Elapsed.TotalSeconds - composed:F0} s, both {clock.Elapsed.TotalSeconds:F0} s");
        }
    }
}
