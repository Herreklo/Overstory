using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Overstory.Play;
using Overstory.Scenes;
using Overstory.World;
using Debug = UnityEngine.Debug;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The walker in the walk's scene (LT1g, the walk, W4): Compose adds it (AddWalk), and CheckProxies runs the
    /// collision study's test 4 on what it collides with (docs/research/collision-and-navigation.md, Tests, 4).
    ///
    /// AddWalk puts on the play object: WalkWorld (the proxies from tools/playable/proxies.py's proxies.json, and the
    /// drawn clay ground as 64 m mesh colliders, all built when the player starts), the Walker and PlayKeys. The ground
    /// the stair's staging sank is a copy in the scene; it is marked readable so the player can cut it into colliders.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Play.CheckProxies
    ///
    /// CheckProxies opens the saved scene, builds the proxies as the player does, and checks:
    /// 1. every proxy names its record: an id, unique, on every one (counts by kind printed);
    /// 2. a ray down onto every tread's nosing of the gully (five points across each) meets its own flight's ramp or
    ///    landing within 3 cm of the nosing line;
    /// 3. no proxy fills an open door: a walker (0.3 m round, 1.8 m tall) fits at every door's stand point;
    /// 4. no proxy fills a way: at every half metre along every lane, stair and door path, a walker fits somewhere
    ///    across it;
    /// 5. the camera's 0.4 m sphere cannot enter a house: cast at each house from 3 m out of each face and from above,
    ///    it meets a proxy before the house's face;
    /// 6. the proxies stand where the clay is drawn: a ray down onto each house, wall and blocker meets the drawn clay
    ///    (or the corner's 1989 houses) between the proxy's top and its roof.
    /// Inside the corner's box (tools/playable/proxies.py, CORNER) a miss fails the check; in the rest of the heart it is
    /// counted and listed as a warning (the layout's own matter, not the walk's).
    /// </summary>
    public static partial class LT1Play
    {
        public const string ProxiesData = "Assets/Experiments/LT1/Playable/proxies.json";
        const string StairSidecar = "Assets/Art/Stone/stone_gully.json";
        const string CheekSidecar = "Assets/Art/Stone/stone_gully_cheeks.json";
        const float WalkerRadius = 0.3f, WalkerHeight = 1.8f, CameraSphere = 0.4f, NosingTolerance = 0.03f;
        const int ClayLayer = 31;     // the check's own, for a moment: the drawn clay as colliders

        /// <summary>The walker, its keys and its world on the play object; the sunk ground made readable for them.</summary>
        static void AddWalk(StreetStage stage, PlayCorner corner)
        {
            var data = AssetDatabase.LoadAssetAtPath<TextAsset>(ProxiesData)
                ?? throw new FileNotFoundException($"[LT1Play] no {ProxiesData}: run tools/playable/proxies.py in Blender's Python");
            var d = JsonUtility.FromJson<WalkWorld.Data>(data.text);
            // the proxies from the stair as it is: its sidecars unchanged since proxies.py read them
            foreach (var (file, want) in new[] { (StairSidecar, d.source.stair), (CheekSidecar, d.source.cheeks) })
                if (BlobHash(file) != want)
                    throw new System.Exception($"[LT1Play] {file} changed since proxies.json was written ({want}): run tools/playable/proxies.py again");

            var heart = GameObject.Find("The heart (clay)") ?? throw new MissingReferenceException("[LT1Play] no heart in the scene");
            var ground = heart.GetComponentsInChildren<MeshFilter>(true).Where(mf => mf.name.StartsWith("ground_heart"))
                .OrderBy(mf => mf.name, System.StringComparer.Ordinal).ToArray();
            if (ground.Length == 0)
                throw new MissingReferenceException("[LT1Play] the heart has no ground_heart");
            foreach (var mf in ground)
            {
                var mesh = mf.sharedMesh;
                if (AssetDatabase.Contains(mesh))
                {
                    // (never the imported asset: a copy in the scene, as the stair's staging makes when it sinks the ground)
                    mesh = Object.Instantiate(mesh);
                    mf.sharedMesh = mesh;
                }
                var so = new SerializedObject(mesh);
                so.FindProperty("m_IsReadable").boolValue = true;
                so.ApplyModifiedPropertiesWithoutUndo();
                if (!mesh.isReadable)
                    throw new System.Exception($"[LT1Play] {mf.name}'s mesh could not be made readable for the walk's ground");
            }

            var play = corner.gameObject;
            var world = play.AddComponent<WalkWorld>();
            world.proxies = data;
            world.ground = ground;
            var walker = play.AddComponent<Walker>();
            walker.view = stage.view;
            walker.corner = corner;
            walker.world = world;
            var keys = play.AddComponent<PlayKeys>();
            keys.corner = corner;
            keys.walker = walker;

            // A to E collide as they are drawn at 1989: their own meshes as colliders (cooked when the player is built),
            // not the layout's boxes, which the stronger houses outgrow by up to 2.6 m at a walker's height
            var houses = GameObject.Find(HousesRoot) ?? throw new MissingReferenceException("[LT1Play] no 1989 houses in the scene");
            var drawn = new List<string>();
            int parts = 0, tris = 0;
            foreach (Transform h in houses.transform)
            {
                var m = Regex.Match(h.name, "\\((\\d+)\\)");
                if (!m.Success)
                    throw new System.Exception($"[LT1Play] {h.name}: no record id in its name");
                string rec = $"bld/{m.Groups[1].Value}";
                if (!d.proxies.Any(p => p.id == rec))
                    throw new System.Exception($"[LT1Play] {h.name}: no proxy {rec} in {ProxiesData}");
                drawn.Add(rec);
                var seen = new HashSet<string>();
                foreach (var mf in h.GetComponentsInChildren<MeshFilter>(true).OrderBy(f => f.name, System.StringComparer.Ordinal))
                {
                    if (mf.sharedMesh == null)
                        continue;
                    string id = $"{rec}/1989/{mf.name}";
                    for (int k = 2; !seen.Add(id); k++)
                        id = $"{rec}/1989/{mf.name}#{k}";
                    var go = new GameObject("collides: " + id) { layer = WalkWorld.WalkLayer };
                    go.transform.SetParent(mf.transform, false);
                    go.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
                    var wp = go.AddComponent<WalkProxy>();
                    wp.id = id;
                    wp.kind = "house";
                    parts++;
                    tris += (int)(mf.sharedMesh.GetIndexCount(0) / 3);
                    for (int sm = 1; sm < mf.sharedMesh.subMeshCount; sm++)
                        tris += (int)(mf.sharedMesh.GetIndexCount(sm) / 3);
                }
            }
            world.drawn = drawn.ToArray();
            Debug.Log($"[LT1Play] the walk: {d.proxies.Length} proxies (clay {d.source.clay.Substring(0, 7)}, heart_layout {d.source.heart_layout.Substring(0, 8)}), " +
                      $"{d.doors.Length} doors, {d.ways.Length} ways; the ground from {string.Join(", ", ground.Select(g => g.name))}; " +
                      $"{string.Join(", ", drawn)} as drawn ({parts} meshes, {tris} triangles)");
        }

        /// <summary>A file's git blob hash (as proxies.py records its sources).</summary>
        static string BlobHash(string assetPath)
        {
            var bytes = File.ReadAllBytes(Path.Combine(Application.dataPath, "..", assetPath));
            var head = System.Text.Encoding.ASCII.GetBytes($"blob {bytes.Length}\0");
            using (var sha = System.Security.Cryptography.SHA1.Create())
            {
                sha.TransformBlock(head, 0, head.Length, null, 0);
                sha.TransformFinalBlock(bytes, 0, bytes.Length);
                return string.Concat(sha.Hash.Select(b => b.ToString("x2")));
            }
        }

        // -- test 4 ------------------------------------------------------------------------------------------------------

        public static void CheckProxies()
        {
            var clock = System.Diagnostics.Stopwatch.StartNew();
            if (EditorSceneManager.GetActiveScene().path != ScenePath)
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var world = Object.FindAnyObjectByType<WalkWorld>() ?? throw new MissingReferenceException("[LT1Play] no WalkWorld in the walk's scene");
            world.Clear();
            world.Build();
            var clay = new List<GameObject>();
            try
            {
                Physics.SyncTransforms();
                var d = world.data;
                var corner = Rect.MinMaxRect(d.corner[0], d.corner[1], d.corner[2], d.corner[3]);
                bool InCorner(float x, float y) => corner.Contains(new Vector2(x, y));
                var problems = new List<string>();
                var warnings = new List<string>();
                var report = new List<string>();
                var proxies = Object.FindObjectsByType<WalkProxy>(FindObjectsInactive.Include, FindObjectsSortMode.None);
                var byId = new Dictionary<string, WalkProxy>();

                // 1. every proxy names its record
                int unnamed = 0;
                var twice = new List<string>();
                foreach (var p in proxies)
                {
                    if (string.IsNullOrEmpty(p.id)) { unnamed++; continue; }
                    if (byId.ContainsKey(p.id)) twice.Add(p.id); else byId[p.id] = p;
                }
                if (unnamed > 0) problems.Add($"{unnamed} proxies with no id");
                if (twice.Count > 0) problems.Add($"ids twice: {string.Join(", ", twice.Take(10))}");
                var kinds = proxies.GroupBy(p => p.kind).OrderBy(g => g.Key, System.StringComparer.Ordinal).Select(g => $"{g.Key} {g.Count()}");
                report.Add($"1. {proxies.Length} proxies, every one named ({string.Join(", ", kinds)}); A to E as {string.Join(", ", new[] { 104, 105, 1203, 1107, 304 }.Select(r => $"bld/{r} ({proxies.Count(p => p.id.StartsWith($"bld/{r}/1989/", System.StringComparison.Ordinal))} drawn meshes)"))}; " +
                           $"built in {world.ParseMs + world.BoxesMs + world.SplitMs + world.BakeMs:F0} ms (boxes {world.BoxesMs:F0}, ground cut {world.SplitMs:F0}, cooked {world.BakeMs:F0}; {world.Chunks} chunks, {world.ChunkTriangles} triangles)");
                foreach (var r in new[] { 104, 105, 1203, 1107, 304 })
                    if (!proxies.Any(p => p.id.StartsWith($"bld/{r}/1989/", System.StringComparison.Ordinal)))
                        problems.Add($"house {r} does not collide as drawn");

                // 2. the nosings
                var nosings = Nosings();
                var worst = new Dictionary<string, float>();
                int rays = 0;
                foreach (var (id, flight, a, b) in nosings)
                {
                    for (int i = 0; i < 5; i++)
                    {
                        Vector3 p = Vector3.Lerp(a, b, 0.1f + 0.2f * i);
                        rays++;
                        if (!Physics.Raycast(p + Vector3.up * 1.0f, Vector3.down, out var hit, 2f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                        {
                            problems.Add($"{id}: no proxy under its nosing");
                            break;
                        }
                        var wp = WalkWorld.Of(hit.collider);
                        float off = Mathf.Abs(hit.point.y - p.y);
                        if (wp == null || wp.flight != flight || (wp.kind != "ramp" && wp.kind != "landing"))
                        {
                            problems.Add($"{id}: the ray meets {(wp == null ? "nothing named" : wp.id)}, not its flight's ramp");
                            break;
                        }
                        if (off > NosingTolerance)
                        {
                            problems.Add($"{id}: the ramp {off * 100f:F1} cm from the nosing");
                            break;
                        }
                        worst[flight] = Mathf.Max(worst.TryGetValue(flight, out float w) ? w : 0f, off);
                    }
                }
                report.Add($"2. {nosings.Count} nosings, {rays} rays: the ramps within {string.Join(", ", worst.OrderBy(k => k.Key).Select(k => $"{k.Key} {k.Value * 100f:F2} cm"))} (at most {NosingTolerance * 100f:F0})");

                // the drawn clay as colliders, for a moment (tests 3, 4 and 6)
                clay = ClayColliders();
                Physics.SyncTransforms();
                var drawn = new Dictionary<string, bool>();
                bool Drawn(string id)
                {
                    if (!drawn.TryGetValue(id, out bool yes))
                        drawn[id] = yes = id.Contains("/1989/")     // (a 1989 house's own mesh)
                            || byId.TryGetValue(id, out var p) && p.GetComponent<BoxCollider>() != null && DrawnAt(p, byId);
                    return yes;
                }
                // a proxy in a door or a way that the clay draws there too is the layout's (warned: the heart's own
                // matter, W6); one the clay does not draw there is the proxies' error, and fails in the corner
                string Blame(List<string> ids) => ids.All(Drawn) ? "the clay's own" : "not drawn there";

                // 3. doors
                int doorsCorner = 0, doorsOut = 0, doorsLayout = 0;
                var steps = new List<string>();
                foreach (var door in d.doors)
                {
                    var blockers = Fits(StreetSpace.ToUnity(door.x, door.y, door.z), WalkerRadius);
                    if (blockers != null && door.id.StartsWith("bld/", System.StringComparison.Ordinal))
                    {
                        // A to E as drawn at 1989: their fronts stand out of the layout's by a sill, a step or a bay, so
                        // the doorstep is where a walker first fits straight out from the layout's stand point (at most 1 m)
                        float ar = door.a * Mathf.Deg2Rad, nx = Mathf.Sin(ar), ny = -Mathf.Cos(ar);
                        for (float o = 0.1f; o <= 1.0f + 1e-3f && blockers != null; o += 0.1f)
                        {
                            if (Fits(StreetSpace.ToUnity(door.x + nx * o, door.y + ny * o, door.z), WalkerRadius) == null)
                            {
                                blockers = null;
                                steps.Add($"{door.id} +{o:F1} m");
                            }
                        }
                    }
                    if (blockers == null)
                        continue;
                    string line = $"{door.id} ({door.name}) filled by {string.Join(" & ", blockers)}, {Blame(blockers)}";
                    bool walked = door.id.StartsWith("bld/", System.StringComparison.Ordinal);    // A to E: the walk's own doors
                    if (InCorner(door.x, door.y) && (walked || !blockers.All(Drawn))) { problems.Add(line); doorsCorner++; }
                    else { warnings.Add(line); if (InCorner(door.x, door.y)) doorsLayout++; else doorsOut++; }
                }
                report.Add($"3. {d.doors.Length} doors: a walker fits at all but {doorsCorner} in the corner, {doorsLayout} in the corner where the clay " +
                           $"draws the same wall in the door (the layout's), and {doorsOut} beyond it; A to E's doorsteps as drawn, out from the layout's stand " +
                           $"point: {(steps.Count == 0 ? "none" : string.Join(", ", steps))}");

                // 4. ways
                int stations = 0, shut = 0, shutOut = 0;
                var shutWays = new SortedDictionary<string, int>(System.StringComparer.Ordinal);
                foreach (var way in d.ways)
                {
                    if (way.kind == "bridge" || way.kind == "mole")
                        continue;     // (over the water: no walk proxy; the walk keeps to land)
                    var pts = new List<Vector3>();
                    for (int i = 0; i + 2 < way.pts.Length; i += 3)
                        pts.Add(new Vector3(way.pts[i], way.pts[i + 1], way.pts[i + 2]));
                    float half = way.width * 0.5f;
                    for (int s = 0; s + 1 < pts.Count; s++)
                    {
                        Vector3 a = pts[s], b = pts[s + 1];
                        float len = new Vector2(b.x - a.x, b.y - a.y).magnitude;
                        if (len < 0.01f)
                            continue;
                        var along = new Vector2(b.x - a.x, b.y - a.y) / len;
                        var across = new Vector2(-along.y, along.x);
                        for (float u = 0f; u <= len; u += 0.5f)
                        {
                            float x = a.x + along.x * u, y = a.y + along.y * u, z = Mathf.Lerp(a.z, b.z, u / len);
                            if (!world.Heart.Contains(new Vector2(x, y)))
                                continue;
                            stations++;
                            List<string> why = null;
                            bool clear = false;
                            float reach = Mathf.Max(0f, half - WalkerRadius);
                            for (int k = 0; k <= Mathf.CeilToInt(reach / 0.1f) * 2 && !clear; k++)
                            {
                                float o = (k % 2 == 1 ? 1 : -1) * ((k + 1) / 2) * 0.1f;
                                o = Mathf.Clamp(o, -reach, reach);
                                var at = StreetSpace.ToUnity(x + across.x * o, y + across.y * o, z);
                                why = Fits(at, WalkerRadius);
                                clear = why == null;
                            }
                            if (clear)
                                continue;
                            bool inCorner = InCorner(x, y) && !why.All(Drawn);
                            if (inCorner) shut++; else shutOut++;
                            string key = $"{way.name}: {string.Join(" & ", why)}, {Blame(why)}";
                            shutWays[key] = (shutWays.TryGetValue(key, out int n) ? n : 0) + 1;
                            if (inCorner && shutWays[key] == 1)
                                problems.Add($"{way.name} at ({x:F1}, {y:F1}) shut by {string.Join(" & ", why)}, {Blame(why)}");
                        }
                    }
                }
                foreach (var kv in shutWays.Where(kv => !problems.Any(p => p.StartsWith(kv.Key.Split(':')[0] + " at"))))
                    warnings.Add($"{kv.Key} ({kv.Value} stations)");
                report.Add($"4. {d.ways.Length} ways, {stations} stations every 0.5 m: a walker passes all but {shut} in the corner and {shutOut} beyond it or shut by the clay's own");

                // 5. the camera's sphere and the houses
                int houses = 0, entered = 0;
                foreach (var p in proxies.Where(p => p.kind == "house" && p.GetComponent<BoxCollider>() != null))
                {
                    var bc = p.GetComponent<BoxCollider>();
                    var t = p.transform;
                    var c = t.position;
                    if (!InCorner(c.x, c.z))
                        continue;
                    houses++;
                    Vector3 half = bc.size * 0.5f;
                    var from = new List<(Vector3 dir, float face)>
                    {
                        (t.right, half.x), (-t.right, half.x), (t.forward, half.z), (-t.forward, half.z), (Vector3.up, half.y + 4f),
                    };
                    foreach (var (dir, face) in from)
                    {
                        Vector3 start = c + dir * (face + 3f);
                        if (dir == Vector3.up)
                            start = c + Vector3.up * (half.y + 6f);
                        float toFace = dir == Vector3.up ? 6f : 3f;
                        if (!Physics.SphereCast(start, CameraSphere, -dir, out var hit, toFace + 1f, WalkWorld.WalkMask | WalkWorld.CameraMask, QueryTriggerInteraction.Ignore)
                            || hit.distance > toFace - CameraSphere + 0.01f)
                        {
                            entered++;
                            problems.Add($"{p.id}: the camera's sphere reaches its face from {(dir == Vector3.up ? "above" : "the side")}");
                            break;
                        }
                    }
                }
                report.Add($"5. {houses} houses in the corner: the camera's {CameraSphere} m sphere meets a proxy before every face ({entered} reached one)");

                // 6. the proxies where the clay is drawn; A to E against their 1989 houses
                int looked = 0, bare = 0;
                foreach (var p in proxies.Where(p => (p.kind == "house" || p.kind == "wall" || p.kind == "blocker") && p.GetComponent<BoxCollider>() != null))
                {
                    var c = p.transform.position;
                    if (!InCorner(c.x, c.z))
                        continue;
                    looked++;
                    if (!Drawn(p.id))
                    {
                        bare++;
                        var (top, roof) = TopAndRoof(p, byId);
                        problems.Add($"{p.id}: no clay drawn at its top ({top:F2} m to {roof:F2})");
                    }
                }
                report.Add($"6. {looked} houses, walls and blockers in the corner: the clay drawn at each top but {bare}; A to E collide as their drawn 1989 houses");

                Debug.Log($"[LT1Play] CheckProxies {ScenePath} ({clock.Elapsed.TotalSeconds:F0} s), proxies.json from clay {d.source.clay.Substring(0, 7)}, " +
                          $"heart_layout {d.source.heart_layout.Substring(0, 8)}, stair {d.source.stair.Substring(0, 8)}:\n  " +
                          string.Join("\n  ", report) +
                          (warnings.Count > 0 ? $"\n  warned, the layout's or beyond the corner ({warnings.Count}): " + string.Join("; ", warnings.Take(40)) + (warnings.Count > 40 ? " ..." : "") : "") +
                          $"\n  {(problems.Count == 0 ? "PASS" : "FAIL: " + string.Join("; ", problems.Take(40)))}");
                if (problems.Count > 0)
                    throw new System.Exception($"[LT1Play] the walk's proxies fail test 4 ({problems.Count} problems)");
            }
            finally
            {
                foreach (var g in clay)
                    Object.DestroyImmediate(g);
                world.Clear();
            }
        }

        /// <summary>A proxy's top, and the top of its roof (a house's roof proxy, else 0.25 m over the top) plus 0.25 m.</summary>
        static (float top, float roof) TopAndRoof(WalkProxy p, Dictionary<string, WalkProxy> byId)
        {
            var bc = p.GetComponent<BoxCollider>();
            float top = p.transform.position.y + bc.size.y * 0.5f;
            float roof = top + 0.25f;
            if (byId.TryGetValue(p.id + "/roof", out var r))
                roof = r.transform.position.y + r.GetComponent<BoxCollider>().size.y * 0.5f + 0.25f;
            return (top, roof);
        }

        /// <summary>Whether the clay (ClayColliders, on ClayLayer) is drawn at a proxy's top: a ray down its middle meets it
        /// between 0.35 m under the top and its roof (0.25 m over the top for all but a house).</summary>
        static bool DrawnAt(WalkProxy p, Dictionary<string, WalkProxy> byId)
        {
            var (top, roof) = TopAndRoof(p, byId);
            var c = p.transform.position;
            // (from over the roof for a house; from just over the top for a wall or blocker, so a taller wall drawn over
            // it, in the same mesh and so the same collider, does not hide it)
            float from = p.kind == "house" ? roof + 5f : top + 0.24f;
            foreach (var hit in Physics.RaycastAll(new Vector3(c.x, from, c.z), Vector3.down, from - (top - 0.35f) + 0.01f, 1 << ClayLayer, QueryTriggerInteraction.Ignore))
                if (hit.point.y >= top - 0.35f && hit.point.y <= roof)
                    return true;
            return false;
        }

        /// <summary>Which blockers fill a walker standing on the walk surface at p (Unity), or null if it fits.</summary>
        static List<string> Fits(Vector3 p, float r)
        {
            float floor = p.y;
            var hits = Physics.RaycastAll(p + Vector3.up * 1.5f, Vector3.down, 3.5f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore);
            float best = float.PositiveInfinity;
            foreach (var h in hits)
            {
                var wp = WalkWorld.Of(h.collider);
                // the floor: a walkable proxy, or a 1989 house's own step (its mesh: a stoop or a sill a walker can stand on)
                bool floorLike = wp != null && (WalkProxy.Walkable(wp.kind) || wp.id.Contains("/1989/") && h.normal.y > 0.7f && h.point.y < p.y + 0.6f);
                if (floorLike && Mathf.Abs(h.point.y - p.y) < best)
                {
                    best = Mathf.Abs(h.point.y - p.y);
                    floor = h.point.y;
                }
            }
            Vector3 a = new Vector3(p.x, floor + r + 0.3f, p.z), b = new Vector3(p.x, floor + WalkerHeight - r, p.z);
            var over = Physics.OverlapCapsule(a, b, r - 0.02f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore)
                .Select(WalkWorld.Of).Where(w => w != null && WalkProxy.Blocks(w.kind)).Select(w => w.id).Distinct().OrderBy(s => s, System.StringComparer.Ordinal).ToList();
            return over.Count == 0 ? null : over;
        }

        /// <summary>Every tread's nosing line in the gully's sidecar (Unity space): its id, flight and two ends.</summary>
        static List<(string id, string flight, Vector3 a, Vector3 b)> Nosings()
        {
            string text = File.ReadAllText(Path.Combine(Application.dataPath, "..", StairSidecar));
            var origin = Regex.Match(text, "\"origin\"\\s*:\\s*\\[([^\\]]+)\\]").Groups[1].Value.Split(',').Select(F).ToArray();
            var list = new List<(string, string, Vector3, Vector3)>();
            var tread = new Regex("\"id\"\\s*:\\s*\"(st-gully/fl-\\d+)/tr-\\d+\"\\s*,\\s*\"name\"\\s*:\\s*\"tread\"[^{}]*?\"quad\"\\s*:\\s*\\[\\s*\\[([^\\]]+)\\]\\s*,\\s*\\[([^\\]]+)\\]");
            foreach (Match m in tread.Matches(text))
            {
                var p = m.Groups[2].Value.Split(',').Select(F).ToArray();
                var q = m.Groups[3].Value.Split(',').Select(F).ToArray();
                string id = m.Value.Substring(m.Value.IndexOf("st-gully", System.StringComparison.Ordinal)).Split('"')[0];
                list.Add((id, m.Groups[1].Value,
                          StreetSpace.ToUnity(p[0] + origin[0], p[1] + origin[1], p[2] + origin[2]),
                          StreetSpace.ToUnity(q[0] + origin[0], q[1] + origin[1], q[2] + origin[2])));
            }
            if (list.Count == 0)
                throw new System.Exception($"[LT1Play] no treads read from {StairSidecar}");
            return list;
        }

        static float F(string s) => float.Parse(s.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture);

        /// <summary>The drawn clay (the heart's houses, walls and small masses, the corner's 1989 houses) as colliders, for a moment.</summary>
        static List<GameObject> ClayColliders()
        {
            var made = new List<GameObject>();
            var heart = GameObject.Find("The heart (clay)");
            var houses = GameObject.Find(HousesRoot);
            var filters = new List<MeshFilter>();
            foreach (var name in new[] { "buildings_heart", "walls", "details", "landmarks" })
            {
                var t = heart?.transform.Find(name);
                if (t != null && t.gameObject.activeInHierarchy)
                    filters.AddRange(t.GetComponentsInChildren<MeshFilter>());
            }
            if (houses != null)
                filters.AddRange(houses.GetComponentsInChildren<MeshFilter>().Where(f => f.gameObject.activeInHierarchy));
            foreach (var mf in filters)
            {
                if (mf.sharedMesh == null)
                    continue;
                var go = new GameObject("clay " + mf.name) { layer = ClayLayer, hideFlags = HideFlags.DontSave };
                go.transform.SetPositionAndRotation(mf.transform.position, mf.transform.rotation);
                go.transform.localScale = mf.transform.lossyScale;
                go.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
                made.Add(go);
            }
            return made;
        }
    }
}
