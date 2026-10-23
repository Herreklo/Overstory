using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;
using Debug = UnityEngine.Debug;
using Object = UnityEngine.Object;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// Port step 2b, rung R2a's stones (reviews/lt1/port/2b/r2a/stones/plan.md, the contract).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1R2a.&lt;method&gt; [args]
    ///
    /// Proof -tag before|after [-overview]: the off-state proof of Stone.shader's OS_PATCHES arm, one gully view
    ///     (eye-foot, 1600-low-sun) as the player sees it, into frames/proof/&lt;tag&gt;.png; tools/r0b_count.py --same
    ///     compares two of them.
    /// FindSunStand [-moments 1600-low-sun] [-radius 60] [-step 1] [-size L,D,H] [-tag t]: the search that chose the sun
    ///     stand (Stands), for a footprint (the block's 0.7 x 0.4 x 0.3 m when not given).
    /// Block -moments m [-stand foot|sun] [-looks grey,material] [-configs L0,L1,L1-noline,L0-flat] [-views 1,5,8,12,eye5]:
    ///     the harness's test block (R2aBlock) on a stand, in one light per run: the patch array, the arm and L1's lit
    ///     line before the stones arrive. Frames into frames/block/&lt;stand&gt;/&lt;moment&gt;/&lt;look&gt;/&lt;config&gt;/&lt;view&gt;.png,
    ///     the ids, normals and mask into frames/block/&lt;stand&gt;/ids/&lt;level&gt;/, the log into
    ///     logs/block-&lt;stand&gt;-&lt;moment&gt;.txt. A config is a level with its changes: -noline (L1's lit line off),
    ///     -flat (the patches off), -facets2 and -nominor (the arms, from the manifest), -nomotes (the air's motes off, a
    ///     control), -near (OS_Near 1 everywhere, a control for the patch fade); -dolly adds the levels in motion;
    ///     -tag t writes the log as logs/block-&lt;stand&gt;-&lt;moment&gt;-t.txt.
    /// Readback -parts step[,wallstone,coping]: each stone's FBX as imported, read back against its sidecar, its part
    ///     definition and the contract, with no render (logs/readback-&lt;part&gt;.txt; the run fails on any difference).
    /// Stones -parts p -moments m [-stand foot|sun] [...as Block]: each stone judged as the block is, one at a time,
    ///     read back first; frames into frames/&lt;part&gt;/&lt;stand&gt;/..., the log into logs/&lt;part&gt;-&lt;stand&gt;-&lt;moment&gt;.txt.
    ///
    /// Every frame is the player's (PlayerFrame: 2560 x 1440, MSAA 4x, never supersampled). The heart is staged as the
    /// gully's frames stage it (LT1Stone.Stage) and never saved; the judged stone's materials are copies of the slate's
    /// (LT1Stone.Material's asset) with OS_PATCHES on, made here and never saved. Nothing here saves an asset or a scene.
    /// </summary>
    public static class LT1R2a
    {
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const string SlateMaterial = "Assets/Art/Stone/M_Stone_slate.mat";
        const float Lens28 = 46.4f;     // (the gully's 28 mm lens, LT1Stone's: the harsher pixel size SN4 and SN8 are written to)

        static string OutDir => Cli.RepoPath("-out", "reviews/lt1/port/2b/r2a/stones/frames");
        static string LogDir => Cli.RepoPath("-logs", "reviews/lt1/port/2b/r2a/stones/logs");
        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
        // (-tag names a run's log apart from the main set's: a control run into the same frames' tree)
        static string Tag => Cli.Arg("-tag", "") == "" ? "" : "-" + Cli.Arg("-tag", "");

        static LightRig Rig(string moment) => AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");

        // The stands (judging harness): where the judged stone lies, in street metres, its face to the street (-y), the
        // cameras coming from -y.
        //   foot: on the Gully Steps lane 1.8 m short of the flight's foot (LT1Stone.Foot), clear of the gully, where the
        //     gully's stones live; in shade in all three judging lights (drizzle is overcast, at 1600 the lane is in
        //     the houses' shadow, at 1750 the sun is down). No lamp is near: the nearest is the Landing's, 13 m up
        //     the flight (Art/Blockout/heart/lights.json), and the three judging rigs have the lamps off.
        //   sun: the lane's mouth on Harbour Row, 21.6 m south of the foot, the nearest spot to it in direct sun at
        //     1600-low-sun (FindSunStand, logs/sun-stand-1600-low-sun.txt: the sun at bearing 316, 8.1 degrees up,
        //     comes in over the harbour, unblocked for 400 m from the footprint's corners at 50 and 300 mm; every
        //     camera sees the face). Raking low sun is the hardest test for relief, lines and specks; judged in
        //     1600-low-sun only.
        static readonly (string name, Vector2 at, string moment)[] Stands =
        {
            ("foot", new Vector2(49.3f, 22.6f), null),
            ("sun", new Vector2(49.0f, 3.0f), "1600-low-sun"),
        };

        static (string name, Vector2 at, string moment) StandFor(string name, string moment)
        {
            var s = System.Array.Find(Stands, t => t.name == name);
            if (s.name == null)
                throw new System.ArgumentException($"no stand '{name}'");
            if (s.moment != null && s.moment != moment)
                throw new System.ArgumentException($"the {name} stand is judged in {s.moment} only");
            return s;
        }
        const float Down = 20f;         // degrees: the face-on views see about this much of the top
        const float Eye = 1.6f;         // metres: a person's eye over the ground

        // ---------------------------------------------------------------------------------------------------------
        // The off-state proof

        public static void Proof()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            string tag = Cli.Arg("-tag", "after");
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            try
            {
                stage.rig = Rig("1600-low-sun");
                var view = System.Array.Find(LT1Stone.Views, v => v.name == "eye-foot");
                LT1Stone.Aim(stage, shot, view);
                string file = Path.Combine(OutDir, "proof", tag + ".png");
                var clock = Stopwatch.StartNew();
                using (var frame = new PlayerFrame(stage.view))
                {
                    frame.Render(LT1Golden.WarmUp + 1);
                    frame.Save(file);
                }
                Debug.Log($"[LT1R2a] proof {file} in {clock.Elapsed.TotalSeconds:F1} s");
                if (Cli.Flag("-overview"))
                    Overview(stage, shot);
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>Frames from above round the gully's foot and the Landing, in low sun and at the blue hour (the lamps'
        /// pools), to choose where the stones stand.</summary>
        static void Overview(StreetStage stage, CameraShot shot)
        {
            var spots = new (string name, Vector3 pos, Vector3 target)[]
            {
                ("foot-above", LT1Stone.Foot + new Vector3(0f, -0.5f, 30f), LT1Stone.Foot),
                ("landing-above", new Vector3(46f, 37.5f, 38f), new Vector3(46f, 38f, 8f)),
                ("foot-oblique", LT1Stone.Foot + new Vector3(14f, -14f, 12f), LT1Stone.Foot + new Vector3(0f, 4f, 0f)),
                ("landing-oblique", new Vector3(58f, 24f, 18f), new Vector3(46f, 38f, 8f)),
            };
            foreach (var moment in new[] { "1600-low-sun", "1750-blue-hour" })
            {
                stage.rig = Rig(moment);
                foreach (var s in spots)
                {
                    LT1Stone.Aim(stage, shot, (s.name, s.pos, s.target, Lens28));
                    string file = Path.Combine(OutDir, "overview", moment, s.name + ".png");
                    var clock = Stopwatch.StartNew();
                    using (var frame = new PlayerFrame(stage.view))
                    {
                        frame.Render(LT1Golden.WarmUp + 1);
                        frame.Save(file);
                    }
                    Debug.Log($"[LT1R2a] overview {file} in {clock.Elapsed.TotalSeconds:F1} s");
                }
            }
        }

        // ---------------------------------------------------------------------------------------------------------
        // Finding the sun stand

        /// <summary>
        /// FindSunStand [-moments 1600-low-sun]: where on the heart's open ground a stone stands in direct sun and every
        /// judging camera sees it, nearest the flight's foot. In memory, every renderer that casts a shadow takes a mesh
        /// collider (destroyed after; nothing is saved); on a grid (-step, 1 m) within -radius (60 m) of the foot each spot is tested: open sky over it (the
        /// first thing a ray down meets is the ground), the ground flat within 20 mm under the footprint (-size L,D,H:
        /// the block's 0.7 x 0.4 m, 0.3 m high, when not given), the sun unblocked for 400 m from the footprint's
        /// corners and the middles of its long sides at 50 mm and at its height, and
        /// a clear line from each camera (1, 5 and 12 m face-on with 20 degrees of top, eye height at 5 and 12 m, the
        /// face to the street, -y) to the face, each eye camera on open ground. The candidates into
        /// logs/sun-stand-&lt;moment&gt;.txt.
        /// </summary>
        public static void FindSunStand()
        {
            string moment = Cli.Arg("-moments", "1600-low-sun");
            var log = new StringBuilder();
            var (stage, go) = LT1Stone.Stage(false);
            var colliders = new List<MeshCollider>();
            var clock = Stopwatch.StartNew();
            try
            {
                var rig = Rig(moment);
                stage.rig = rig;
                stage.Apply();
                var sunStreet = rig.SunDirectionStreet;
                var sun = StreetSpace.ToUnity(sunStreet).normalized;
                log.AppendLine($"FindSunStand, {System.DateTime.Now:yyyy-MM-dd HH:mm}: {moment}, sun bearing {rig.sunBearing:F1}, " +
                               $"elevation {rig.sunElevation:F2} degrees, towards the sun (street) ({sunStreet.x:F3}, {sunStreet.y:F3}, {sunStreet.z:F3})");
                var groundBounds = new Bounds();
                bool any = false;
                foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                {
                    if (!r.enabled || r.shadowCastingMode == ShadowCastingMode.Off)
                        continue;
                    var mf = r.GetComponent<MeshFilter>();
                    if (mf == null || mf.sharedMesh == null || r.GetComponent<Collider>() != null)
                        continue;
                    var c = r.gameObject.AddComponent<MeshCollider>();
                    c.sharedMesh = mf.sharedMesh;
                    colliders.Add(c);
                    if (r.gameObject.name.StartsWith("ground"))
                    {
                        if (!any) groundBounds = r.bounds; else groundBounds.Encapsulate(r.bounds);
                        any = true;
                    }
                }
                Physics.SyncTransforms();
                float radius = float.Parse(Cli.Arg("-radius", "60"), System.Globalization.CultureInfo.InvariantCulture);
                float step = float.Parse(Cli.Arg("-step", "1"), System.Globalization.CultureInfo.InvariantCulture);
                log.AppendLine($"  {colliders.Count} shadow casters given colliders in {clock.Elapsed.TotalSeconds:F0} s; the ground spans street x " +
                               $"{groundBounds.min.x:F0} to {groundBounds.max.x:F0}, y {groundBounds.min.z:F0} to {groundBounds.max.z:F0}; " +
                               $"searched within {radius} m of the foot on a {step} m grid");
                var names = new List<string>();
                foreach (var c in colliders)
                    names.Add(c.gameObject.name);
                names.Sort();
                log.AppendLine($"  the casters: {string.Join(", ", names)}");

                bool GroundAt(float x, float y, out float z)
                {
                    z = 0f;
                    if (!Physics.Raycast(StreetSpace.ToUnity(x, y, 300f), Vector3.down, out var hit, 400f))
                        return false;
                    z = hit.point.y;
                    return hit.collider.gameObject.name.StartsWith("ground");
                }
                bool Clear(Vector3 from, Vector3 to)
                {
                    var d = to - from;
                    return !Physics.Raycast(from, d.normalized, d.magnitude - 0.02f);
                }

                // (the footprint and height judged: -size L,D,H in metres, the block's 0.7 x 0.4 x 0.3 when not given)
                var size = Cli.Arg("-size", "0.7,0.4,0.3").Split(',');
                float halfL = float.Parse(size[0], System.Globalization.CultureInfo.InvariantCulture) / 2f;
                float halfD = float.Parse(size[1], System.Globalization.CultureInfo.InvariantCulture) / 2f;
                float tall = float.Parse(size[2], System.Globalization.CultureInfo.InvariantCulture);
                log.AppendLine($"  footprint {2f * halfL} x {2f * halfD} m, {tall} m high");
                var found = new List<(float dist, Vector2 at, float z, string note)>();
                int tested = 0;
                float x0 = Mathf.Max(groundBounds.min.x, LT1Stone.Foot.x - radius), x1 = Mathf.Min(groundBounds.max.x, LT1Stone.Foot.x + radius);
                float y0 = Mathf.Max(groundBounds.min.z, LT1Stone.Foot.y - radius), y1 = Mathf.Min(groundBounds.max.z, LT1Stone.Foot.y + radius);
                for (float x = Mathf.Ceil(x0); x <= x1; x += step)
                    for (float y = Mathf.Ceil(y0); y <= y1; y += step)
                    {
                        tested++;
                        float lo = float.MaxValue, hi = float.MinValue;
                        bool ok = true;
                        foreach (var dx in new[] { -halfL, halfL })
                            foreach (var dy in new[] { -halfD, halfD })
                            {
                                if (!GroundAt(x + dx, y + dy, out var g)) { ok = false; break; }
                                lo = Mathf.Min(lo, g);
                                hi = Mathf.Max(hi, g);
                            }
                        if (!ok || hi - lo > 0.02f)
                            continue;
                        // the sun on the footprint's corners, low and high, and on the face's middle
                        foreach (var dx in new[] { -halfL, 0f, halfL })
                            foreach (var dy in new[] { -halfD, halfD })
                                foreach (var h in new[] { 0.05f, tall })
                                    if (ok && Physics.Raycast(StreetSpace.ToUnity(x + dx, y + dy, lo + h), sun, 400f))
                                        ok = false;
                        if (!ok)
                            continue;
                        // every camera sees the face's middle
                        var face = StreetSpace.ToUnity(x, y - halfD, lo + tall / 2f);
                        var faceStreet = new Vector3(x, y - halfD, lo + tall / 2f);
                        float r = Down * Mathf.Deg2Rad;
                        foreach (var dist in new[] { 1f, 5f, 12f })
                        {
                            var cam = faceStreet + new Vector3(0f, -Mathf.Cos(r), Mathf.Sin(r)) * dist;
                            if (ok && !Clear(StreetSpace.ToUnity(cam), face))
                                ok = false;
                        }
                        foreach (var dist in new[] { 5f, 12f })
                        {
                            if (!ok)
                                break;
                            if (!GroundAt(x, y - halfD - dist, out var g)) { ok = false; break; }
                            if (!Clear(StreetSpace.ToUnity(x, y - halfD - dist, g + Eye), face))
                                ok = false;
                        }
                        if (!ok)
                            continue;
                        float toFoot = Vector2.Distance(new Vector2(x, y), new Vector2(LT1Stone.Foot.x, LT1Stone.Foot.y));
                        found.Add((toFoot, new Vector2(x, y), lo, $"ground {lo:F3} to {hi:F3}"));
                    }
                found.Sort((a, b) => a.dist.CompareTo(b.dist));
                log.AppendLine($"  {tested} spots tested in {clock.Elapsed.TotalSeconds:F0} s, {found.Count} pass; the nearest the foot ({LT1Stone.Foot.x}, {LT1Stone.Foot.y}):");
                for (int i = 0; i < Mathf.Min(25, found.Count); i++)
                    log.AppendLine($"    ({found[i].at.x:F1}, {found[i].at.y:F1}): {found[i].dist:F1} m from the foot, {found[i].note}");
            }
            finally
            {
                foreach (var c in colliders)
                    if (c != null)
                        Object.DestroyImmediate(c);
                Object.DestroyImmediate(go);
            }
            Directory.CreateDirectory(LogDir);
            File.WriteAllText(Path.Combine(LogDir, $"sun-stand-{moment}{Tag}.txt"), log.ToString());
            Debug.Log("[LT1R2a] " + log.ToString().Replace("\n", "\n[LT1R2a] "));
        }

        // ---------------------------------------------------------------------------------------------------------
        // The test block

        public static void Block()
        {
            string moment = Cli.Arg("-moments", "1600-low-sun");
            var stand = StandFor(Cli.Arg("-stand", "foot"), moment);
            var looks = Cli.Arg("-looks", "grey,material").Split(',');
            var configs = Cli.Arg("-configs", "L0,L1,L1-noline").Split(',');
            var viewNames = Cli.Arg("-views", "1,5,8,12,eye5").Split(',');
            var log = new StringBuilder();
            log.AppendLine($"LT1R2a.Block, {System.DateTime.Now:yyyy-MM-dd HH:mm}: {moment}, the {stand.name} stand; looks {string.Join(",", looks)}; " +
                           $"configs {string.Join(",", configs)}; views {string.Join(",", viewNames)}");
            Run(moment, log, (stage, shot, kit) =>
            {
                // (the harness's chamfer form for the block, which has no part definition: the leg along each face in mm
                // as UV7 codes it, at 45 degrees; the stones take theirs from their definition)
                kit.Chamfer(1f, 45f, "the block's own (a harness fixture): leg, 45 degrees", log);
                var spec = R2aBlock.Default;
                var piece = kit.Place("block", stand.at, R2aBlock.Build(spec, true), R2aBlock.Build(spec, false), log);
                Judge(stage, shot, kit, piece, moment, looks, configs, viewNames, Path.Combine(OutDir, "block", stand.name), log);
                if (Cli.Flag("-dolly"))
                    Dolly(stage, shot, kit, piece, moment, looks, Path.Combine(OutDir, "block", stand.name), log);
            });
            Directory.CreateDirectory(LogDir);
            File.WriteAllText(Path.Combine(LogDir, $"block-{stand.name}-{moment}{Tag}.txt"), log.ToString());
        }

        /// <summary>The stage made and lit, the kit (patch array, materials, globals) built, the work done, everything
        /// restored and destroyed after.</summary>
        static void Run(string moment, StringBuilder log, System.Action<StreetStage, CameraShot, Kit> work)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            // (every variant compiled before it draws: with the editor's asynchronous compiling a new variant draws as
            // the placeholder until it is ready)
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            Kit kit = null;
            try
            {
                var rig = Rig(moment);
                if (rig == null)
                    throw new FileNotFoundException($"no rig {moment}");
                stage.rig = rig;
                // the air (the town's own, OS_Atmosphere; Unity's fog is off by design)
                log.AppendLine($"light {moment}: fog density {rig.fogDensity}, max opacity {rig.fogMaxOpacity}, mid at " +
                               $"{rig.fogMidDistance} m, far at {rig.fogFarDistance} m, haze {rig.hazeDensity}; OS_HAZE_OFF " +
                               $"{(Shader.IsKeywordEnabled("OS_HAZE_OFF") ? "ON: the air is off" : "off: the air is on")}; " +
                               $"lamps {(rig.lampsOn ? "on" : "off")}");
                kit = new Kit(log);
                work(stage, shot, kit);
            }
            finally
            {
                kit?.Dispose();
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>A piece's frames: per look (grey first), per level config, per view; then each level's ids, normals
        /// and mask per view.</summary>
        static void Judge(StreetStage stage, CameraShot shot, Kit kit, Piece piece, string moment, string[] looks,
                          string[] configs, string[] viewNames, string root, StringBuilder log)
        {
            var views = new List<(string name, Vector3 pos, Vector3 target, float fov)>();
            foreach (var v in viewNames)
                views.Add(piece.View(v));
            foreach (var v in views)
                log.AppendLine($"  view {v.name}: camera ({v.pos.x:F2}, {v.pos.y:F2}, {v.pos.z:F2}) on ({v.target.x:F2}, " +
                               $"{v.target.y:F2}, {v.target.z:F2}), {v.fov} degrees, {Vector3.Distance(v.pos, v.target):F2} m");
            foreach (var look in looks)
            {
                bool grey = look == "grey";
                kit.Look(grey);
                foreach (var config in configs)
                {
                    // (the arms: the wall stone's split faces' patches drawn with twice the facets, or without the minor
                    // steps, from the manifest's slices; every other config as built)
                    kit.Arm(config.Contains("facets2") ? "facets2" : config.Contains("nominor") ? "nominor" : "as-built");
                    piece.Show(config, grey ? kit.grey : kit.material);
                    foreach (var v in views)
                    {
                        LT1Stone.Aim(stage, shot, v);
                        // (-nomotes, a control: the air's motes off, which the stage's Apply turns back on as the rig says)
                        if (config.Contains("nomotes") && stage.motes != null && stage.motes.TryGetComponent(out MeshRenderer motes))
                            motes.enabled = false;
                        string file = Path.Combine(root, moment, look, config, v.name + ".png");
                        var clock = Stopwatch.StartNew();
                        using (var frame = new PlayerFrame(stage.view))
                        {
                            frame.Render(LT1Golden.WarmUp + 1);
                            frame.Save(file);
                        }
                        log.AppendLine($"  {look} {config} {v.name}: {clock.Elapsed.TotalSeconds:F1} s");
                    }
                }
            }
            kit.Look(false);
            kit.Arm("as-built");
            foreach (var level in new[] { "L0", "L1" })
            {
                piece.Show(level, kit.material);
                foreach (var v in views)
                {
                    LT1Stone.Aim(stage, shot, v);
                    kit.Ids(stage.view, level == "L0" ? piece.l0 : piece.l1, Path.Combine(root, "ids", level, v.name), log);
                }
            }
            Triangles(stage, shot, piece, views, root, log);
            Debug.Log($"[LT1R2a] {piece.name} in {moment}: {looks.Length * configs.Length * views.Count} frames into {root}");
        }

        /// <summary>
        /// SN8's triangle measures, from the mesh and the camera (no render): per level and view, the front-facing
        /// triangles on screen, the share whose smallest altitude is under 2 px (thin: at most 10% at the level's far
        /// edge, L0 at 8 m and L1 at 20 m) and the median triangle's area in px (at least 10). The far edges are always
        /// measured, whatever views the frames took. Into the log and &lt;root&gt;/ids/triangles.json.
        /// </summary>
        static void Triangles(StreetStage stage, CameraShot shot, Piece piece,
                              List<(string name, Vector3 pos, Vector3 target, float fov)> views, string root, StringBuilder log)
        {
            var all = new List<(string name, Vector3 pos, Vector3 target, float fov)>(views);
            foreach (var edge in new[] { "8", "20" })
                if (!all.Exists(v => v.name == edge + "m"))
                    all.Add(piece.View(edge));
            var json = new StringBuilder("{\n");
            bool first = true;
            foreach (var level in new[] { "L0", "L1" })
                foreach (var v in all)
                {
                    LT1Stone.Aim(stage, shot, v);
                    var r = level == "L0" ? piece.l0 : piece.l1;
                    var t = ScreenTriangles(stage.view, r);
                    log.AppendLine($"  triangles {level} {v.name}: {t.front} front-facing of {t.total}; thin (smallest altitude " +
                                   $"under 2 px) {t.thin} = {100f * t.thin / Mathf.Max(1, t.front):F0}%; median area {t.medianArea:F1} px, " +
                                   $"median smallest altitude {t.medianAltitude:F2} px");
                    json.Append(first ? "" : ",\n").Append($" \"{level}/{v.name}\": {{\"total\": {t.total}, \"front\": {t.front}, " +
                        $"\"thin\": {t.thin}, \"median_area_px\": {F(t.medianArea)}, \"median_altitude_px\": {F(t.medianAltitude)}}}");
                    first = false;
                }
            Directory.CreateDirectory(Path.Combine(root, "ids"));
            File.WriteAllText(Path.Combine(root, "ids", "triangles.json"), json.Append("\n}\n").ToString());
        }

        static string F(float v) => v.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);

        static float ArgF(string flag, float fallback) =>
            float.Parse(Cli.Arg(flag, fallback.ToString(System.Globalization.CultureInfo.InvariantCulture)), System.Globalization.CultureInfo.InvariantCulture);

        /// <summary>
        /// The levels in motion: a dolly straight back from the face (face-on, 20 degrees of top seen) from -from (6 m)
        /// to -to (14 m) at a walker's -speed (1.4 m/s) and the player's -fps (60), the camera's step each frame. Each
        /// level is rendered over the whole path, warmed up at the first frame and then one render a frame, as the
        /// motion harness renders a walk (LT1Motion), so any switch distance is the L0 sequence up to a frame and the
        /// L1 sequence from it. Each frame is kept as a crop round the screen's middle (where the face's middle is);
        /// dolly.json gives each frame's distance and the piece's box on screen (its L1 bounds projected), where
        /// tools/r2a_count.py measures the pop: the switch's change (L1 at k against L0 at k - 1) beside the motion's
        /// own (L0 at k against L0 at k - 1). Into &lt;root&gt;/dolly/&lt;moment&gt;/&lt;look&gt;/&lt;level&gt;/NNN.png.
        /// </summary>
        static void Dolly(StreetStage stage, CameraShot shot, Kit kit, Piece piece, string moment, string[] looks, string root,
                          StringBuilder log)
        {
            float from = ArgF("-from", 6f), to = ArgF("-to", 14f), speed = ArgF("-speed", 1.4f), fps = ArgF("-fps", 60f);
            float step = speed / fps;
            int n = Mathf.FloorToInt((to - from) / step + 1e-4f) + 1;
            const int cw = 640, ch = 400;
            int cx0 = (PlayerFrame.Width - cw) / 2, cy0 = (PlayerFrame.Height - ch) / 2;
            string dir = Path.Combine(root, "dolly", moment);
            var dist = new float[n];
            for (int i = 0; i < n; i++)
                dist[i] = from + i * step;
            log.AppendLine($"  dolly: {from} to {dist[n - 1]:F3} m at {speed} m/s and {fps} fps ({step * 1000f:F1} mm a frame), {n} frames a level; " +
                           $"crops {cw} x {ch} from ({cx0}, {cy0})");
            var crop = new Texture2D(cw, ch, TextureFormat.RGB24, false, false);
            var windows = new string[n];
            try
            {
                foreach (var look in looks)
                {
                    bool grey = look == "grey";
                    kit.Look(grey);
                    foreach (var level in new[] { "L0", "L1" })
                    {
                        piece.Show(level, grey ? kit.grey : kit.material);
                        string d = Path.Combine(dir, look, level);
                        Directory.CreateDirectory(d);
                        var clock = Stopwatch.StartNew();
                        using (var frame = new PlayerFrame(stage.view))
                            for (int i = 0; i < n; i++)
                            {
                                LT1Stone.Aim(stage, shot, piece.ViewAt(dist[i], $"dolly{i:000}"));
                                frame.Render(i == 0 ? LT1Golden.WarmUp + 1 : 1);
                                var tex = frame.Read();
                                // (the readback's rows run bottom up; the crop is centred, so the same rows either way)
                                crop.SetPixels(tex.GetPixels(cx0, PlayerFrame.Height - cy0 - ch, cw, ch));
                                crop.Apply();
                                File.WriteAllBytes(Path.Combine(d, $"{i:000}.png"), crop.EncodeToPNG());
                                if (windows[i] == null)
                                {
                                    var box = ScreenBox(stage.view, piece.l1);
                                    windows[i] = $"[{F(box.xMin - cx0)}, {F(box.yMin - cy0)}, {F(box.xMax - cx0)}, {F(box.yMax - cy0)}]";
                                }
                            }
                        log.AppendLine($"  dolly {look} {level}: {n} frames in {clock.Elapsed.TotalSeconds:F1} s");
                    }
                }
                kit.Look(false);
            }
            finally
            {
                Object.DestroyImmediate(crop);
            }
            var json = new StringBuilder("{\n");
            json.Append($" \"from\": {F(from)}, \"to\": {F(dist[n - 1])}, \"speed\": {F(speed)}, \"fps\": {F(fps)}, \"step\": {F(step)},\n");
            json.Append($" \"frames\": {n}, \"crop\": [{cx0}, {cy0}, {cw}, {ch}], \"looks\": [\"{string.Join("\", \"", looks)}\"],\n");
            json.Append(" \"distances\": [");
            for (int i = 0; i < n; i++)
                json.Append(i == 0 ? "" : ", ").Append(F(dist[i]));
            json.Append("],\n \"windows\": [");
            for (int i = 0; i < n; i++)
                json.Append(i == 0 ? "" : ", ").Append(windows[i]);
            json.Append("]\n}\n");
            File.WriteAllText(Path.Combine(dir, "dolly.json"), json.ToString());
        }

        /// <summary>The renderer's bounds on the player's frame, in pixels from the top left.</summary>
        static Rect ScreenBox(Camera cam, Renderer r)
        {
            var vp = Matrix4x4.Perspective(cam.fieldOfView, (float)PlayerFrame.Width / PlayerFrame.Height, cam.nearClipPlane,
                                           cam.farClipPlane) * cam.worldToCameraMatrix;
            var b = r.bounds;
            float x0 = float.MaxValue, y0 = float.MaxValue, x1 = float.MinValue, y1 = float.MinValue;
            for (int i = 0; i < 8; i++)
            {
                var w = new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z);
                var c = vp * new Vector4(w.x, w.y, w.z, 1f);
                float px = (c.x / c.w * 0.5f + 0.5f) * PlayerFrame.Width, py = (0.5f - c.y / c.w * 0.5f) * PlayerFrame.Height;
                x0 = Mathf.Min(x0, px); x1 = Mathf.Max(x1, px); y0 = Mathf.Min(y0, py); y1 = Mathf.Max(y1, py);
            }
            return Rect.MinMaxRect(x0, y0, x1, y1);
        }

        /// <summary>The renderer's triangles as the player's frame projects them (2560 x 1440, the camera's lens): how
        /// many face the camera, how many of those are thin, and the medians.</summary>
        static (int total, int front, int thin, float medianArea, float medianAltitude) ScreenTriangles(Camera cam, Renderer r)
        {
            var mesh = r.GetComponent<MeshFilter>().sharedMesh;
            var l2w = r.transform.localToWorldMatrix;
            var vp = Matrix4x4.Perspective(cam.fieldOfView, (float)PlayerFrame.Width / PlayerFrame.Height, cam.nearClipPlane,
                                           cam.farClipPlane) * cam.worldToCameraMatrix;
            Vector2 Px(Vector3 w)
            {
                var c = vp * new Vector4(w.x, w.y, w.z, 1f);
                return new Vector2((c.x / c.w * 0.5f + 0.5f) * PlayerFrame.Width, (0.5f - c.y / c.w * 0.5f) * PlayerFrame.Height);
            }
            var v = mesh.vertices;
            var tris = mesh.triangles;
            var areas = new List<float>();
            var altitudes = new List<float>();
            int thin = 0;
            var eye = cam.transform.position;
            for (int i = 0; i < tris.Length; i += 3)
            {
                Vector3 a = l2w.MultiplyPoint3x4(v[tris[i]]), b = l2w.MultiplyPoint3x4(v[tris[i + 1]]), c = l2w.MultiplyPoint3x4(v[tris[i + 2]]);
                if (Vector3.Dot(Vector3.Cross(b - a, c - a), a - eye) >= 0f)
                    continue;     // (facing away)
                Vector2 pa = Px(a), pb = Px(b), pc = Px(c);
                float area2 = Mathf.Abs((pb.x - pa.x) * (pc.y - pa.y) - (pc.x - pa.x) * (pb.y - pa.y));
                float longest = Mathf.Max((pb - pa).magnitude, Mathf.Max((pc - pb).magnitude, (pa - pc).magnitude));
                float altitude = longest > 0f ? area2 / longest : 0f;
                areas.Add(area2 / 2f);
                altitudes.Add(altitude);
                if (altitude < 2f)
                    thin++;
            }
            areas.Sort();
            altitudes.Sort();
            float Median(List<float> l) => l.Count == 0 ? 0f : (l.Count % 2 == 1 ? l[l.Count / 2] : 0.5f * (l[l.Count / 2 - 1] + l[l.Count / 2]));
            return (tris.Length / 3, areas.Count, thin, Median(areas), Median(altitudes));
        }

        // ---------------------------------------------------------------------------------------------------------
        // The stones

        const string Generated = "Assets/Experiments/LT1/R2a/Generated";
        const string PackParts = "packs/stavanger-1989/parts/stone";

        /// <summary>
        /// Readback -parts step[,...]: each stone's FBX as Unity imported it, read back against its sidecar, its part
        /// definition and the contract (plan.md, The vertex layout), with no render. Into logs/readback-&lt;part&gt;.txt;
        /// fails the run on any difference.
        /// </summary>
        public static void Readback()
        {
            int failed = 0;
            foreach (var part in Cli.Arg("-parts", "step").Split(','))
            {
                var log = new StringBuilder();
                log.AppendLine($"LT1R2a.Readback, {System.DateTime.Now:yyyy-MM-dd HH:mm}: {part}");
                var stone = Stone.Load(part, log);
                failed += stone.fails.Count;
                Directory.CreateDirectory(LogDir);
                File.WriteAllText(Path.Combine(LogDir, $"readback-{part}.txt"), log.ToString());
                Debug.Log("[LT1R2a] " + log.ToString().Replace("\n", "\n[LT1R2a] "));
            }
            if (failed > 0)
                throw new System.InvalidOperationException($"[LT1R2a] readback: {failed} failures (logs/readback-*.txt)");
        }

        /// <summary>
        /// Stones -parts step -moments m [-stand foot|sun] [-looks grey,material] [-configs L0,L1,L1-noline,L0-flat]
        /// [-views 1,5,8,10,12,eye5,eye12] [-dolly] [-tag t]: each stone judged as the block is (Judge, Dolly), one part
        /// at a time, its FBX read back first (Stone.Load: the run stops on any difference). Frames into
        /// frames/&lt;part&gt;/&lt;stand&gt;/..., the log into logs/&lt;part&gt;-&lt;stand&gt;-&lt;moment&gt;[-t].txt.
        /// </summary>
        public static void Stones()
        {
            string moment = Cli.Arg("-moments", "1600-low-sun");
            var stand = StandFor(Cli.Arg("-stand", "foot"), moment);
            var looks = Cli.Arg("-looks", "grey,material").Split(',');
            var configs = Cli.Arg("-configs", "L0,L1,L1-noline,L0-flat").Split(',');
            var viewNames = Cli.Arg("-views", "1,5,8,10,12,eye5,eye12").Split(',');
            foreach (var part in Cli.Arg("-parts", "step").Split(','))
            {
                var log = new StringBuilder();
                log.AppendLine($"LT1R2a.Stones, {System.DateTime.Now:yyyy-MM-dd HH:mm}: {part} in {moment}, the {stand.name} stand; looks " +
                               $"{string.Join(",", looks)}; configs {string.Join(",", configs)}; views {string.Join(",", viewNames)}");
                try
                {
                    Run(moment, log, (stage, shot, kit) =>
                    {
                        var stone = Stone.Load(part, log);
                        if (stone.fails.Count > 0)
                            throw new System.InvalidOperationException($"{part}: the readback fails ({stone.fails.Count}): " +
                                                                       string.Join("; ", stone.fails));
                        kit.Chamfer(stone.legPerMm, stone.chamferDeg, stone.chamferSource, log);
                        var piece = kit.Place(part, stand.at, stone.l0, stone.l1, log);
                        string root = Path.Combine(OutDir, part, stand.name);
                        Judge(stage, shot, kit, piece, moment, looks, configs, viewNames, root, log);
                        if (Cli.Flag("-dolly"))
                            Dolly(stage, shot, kit, piece, moment, looks, root, log);
                        piece.Hide();
                    });
                }
                finally
                {
                    Directory.CreateDirectory(LogDir);
                    File.WriteAllText(Path.Combine(LogDir, $"{part}-{stand.name}-{moment}{Tag}.txt"), log.ToString());
                }
            }
        }

        /// <summary>
        /// A stone as Unity imported it (Generated/&lt;part&gt;.fbx, the sidecar &lt;part&gt;.json beside it, the definition
        /// packs/.../parts/stone/&lt;part&gt;.json), read back: the importer's settings (nothing here changes them), the
        /// children's transforms (the importer's axis turn is taken off, as LT1Stone.Place does: the mesh is in Unity's
        /// order already), and per level every contract channel (plan.md, The vertex layout) against the contract's
        /// rules and the sidecar's numbers. Every difference is a fail, named in the log.
        /// </summary>
        sealed class Stone
        {
            public string part, fbx;
            public Mesh l0, l1;
            public float legPerMm = 1f, chamferDeg = 45f;
            public string chamferSource = "";
            public Dictionary<string, object> sidecar, definition;
            public readonly List<string> fails = new List<string>();

            void Fail(StringBuilder log, string what)
            {
                fails.Add(what);
                log.AppendLine("  FAIL " + what);
            }

            public static Stone Load(string part, StringBuilder log)
            {
                var s = new Stone { part = part };
                string defPath = Path.Combine(Repo, PackParts, part + ".json");
                if (!File.Exists(defPath))
                    throw new FileNotFoundException($"no part definition {defPath}");
                s.definition = (Dictionary<string, object>)R2aPatches.Json.Parse(File.ReadAllText(defPath));
                s.fbx = $"{Generated}/{part}.fbx";
                string side = Path.Combine(Repo, "unity", s.fbx[..^4] + ".json");
                if (!File.Exists(Path.Combine(Repo, "unity", s.fbx)) || !File.Exists(side))
                    throw new FileNotFoundException($"no {s.fbx} with its sidecar: the Blender export installs it");
                s.sidecar = (Dictionary<string, object>)R2aPatches.Json.Parse(File.ReadAllText(side));
                log.AppendLine($"stone {part}: {s.fbx} (md5 {Md5(Path.Combine(Repo, "unity", s.fbx))}), its sidecar (md5 {Md5(side)}), " +
                               $"the definition {PackParts}/{part}.json (md5 {Md5(defPath)})");

                // the importer, as it is (Generated/ is outside ArtImport's folder: the defaults)
                var imp = AssetImporter.GetAtPath(s.fbx) as ModelImporter;
                if (imp == null)
                    throw new FileNotFoundException($"{s.fbx} is not imported as a model");
                log.AppendLine($"  importer: compression {imp.meshCompression}, normals {imp.importNormals}, tangents {imp.importTangents}, " +
                               $"weld {imp.weldVertices}, optimise polygons {imp.optimizeMeshPolygons} vertices {imp.optimizeMeshVertices}, " +
                               $"readable {imp.isReadable}, axis conversion baked {imp.bakeAxisConversion}, scale {imp.globalScale} " +
                               $"(file scale {imp.useFileScale}, {imp.fileScale}), lightmap UVs {imp.generateSecondaryUV}, " +
                               $"swap UVs {imp.swapUVChannels}, keep quads {imp.keepQuads}");
                if (imp.meshCompression != ModelImporterMeshCompression.Off)
                    s.Fail(log, $"importer: mesh compression {imp.meshCompression} (the channels must come through exact)");
                if (imp.generateSecondaryUV || imp.swapUVChannels)
                    s.Fail(log, "importer: UV2 generated or the UVs swapped (UV1 and UV2 are contract channels)");
                if (imp.importNormals != ModelImporterNormals.Import)
                    s.Fail(log, $"importer: normals {imp.importNormals}, not the file's");

                // the meshes, by the sidecar's object names when it gives them, else by L0 / L1 in their names
                var meshes = new List<Mesh>();
                foreach (var o in AssetDatabase.LoadAllAssetsAtPath(s.fbx))
                    if (o is Mesh m)
                        meshes.Add(m);
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(s.fbx);
                foreach (var mf in model.GetComponentsInChildren<MeshFilter>())
                {
                    var t = mf.transform;
                    log.AppendLine($"  object {t.name}: mesh {mf.sharedMesh.name}, local position {t.localPosition}, rotation " +
                                   $"{t.localRotation.eulerAngles}, scale {t.localScale} (the rotation and position taken off: the " +
                                   $"mesh is in Unity's order)");
                    if ((t.localScale - Vector3.one).sqrMagnitude > 1e-10f)
                        s.Fail(log, $"object {t.name}: scale {t.localScale}, not 1");
                }
                foreach (var m in meshes)
                {
                    string n = m.name.ToLowerInvariant();
                    if (n.EndsWith("l0") || n.Contains("_l0") || n.Contains(" l0") || n.Contains("-l0"))
                        s.l0 = m;
                    else if (n.EndsWith("l1") || n.Contains("_l1") || n.Contains(" l1") || n.Contains("-l1"))
                        s.l1 = m;
                }
                if (s.l0 == null || s.l1 == null)
                    throw new System.InvalidOperationException($"{s.fbx}: meshes {string.Join(", ", meshes.ConvertAll(m => m.name))}; no L0 and L1");

                // the chamfer's form for the lit line: its measure from the part (only the leg is built) and the angle a
                // square arris gives an equal-legged chamfer
                s.ChamferForm(log);
                // (L0 first: its code's chamfer is the stone's, which bounds L1's)
                s.Level(s.l0, 0, log);
                s.Level(s.l1, 1, log);
                s.Pivot(log);
                log.AppendLine(s.fails.Count == 0 ? $"  readback {part}: every check passes" : $"  readback {part}: {s.fails.Count} FAIL");
                return s;
            }

            static string Md5(string path)
            {
                using (var md5 = System.Security.Cryptography.MD5.Create())
                    return System.BitConverter.ToString(md5.ComputeHash(File.ReadAllBytes(path))).Replace("-", "").ToLowerInvariant()[..12];
            }

            object Find(params string[] keys)
            {
                foreach (var root in new[] { sidecar, definition })
                {
                    object cur = root;
                    foreach (var k in keys)
                        cur = cur is Dictionary<string, object> d && d.TryGetValue(k, out var v) ? v : null;
                    if (cur != null)
                        return cur;
                }
                return null;
            }

            void ChamferForm(StringBuilder log)
            {
                var measure = Find("chamferMeasure") as string ?? Find("params", "chamferMeasure") as string ?? "leg";
                if (measure != "leg")
                    Fail(log, $"chamfer measure '{measure}': only the leg is built");
                legPerMm = 1f;
                chamferDeg = 45f;
                chamferSource = $"the part's measure '{measure}' (the code's mm is the leg kept along each face), at 45 degrees " +
                                "(an equal-legged chamfer on a square arris; the arrises' own turns are measured below)";
            }

            /// <summary>One level's channels against the contract. Returns L1's creases (for L0's chamfers).</summary>
            int stoneChamfer = -1;

            void Level(Mesh m, int level, StringBuilder log)
            {
                string L = "L" + level;
                var v = m.vertices;
                var nrm = m.normals;
                var tri = m.triangles;
                var uv = new List<Vector4>[8];
                var dims = new int[8];
                for (int c = 0; c < 8; c++)
                {
                    var attr = VertexAttribute.TexCoord0 + c;
                    if (!m.HasVertexAttribute(attr))
                    {
                        Fail(log, $"{L}: no UV{c}");
                        return;
                    }
                    dims[c] = m.GetVertexAttributeDimension(attr);
                    uv[c] = new List<Vector4>();
                    m.GetUVs(c, uv[c]);
                }
                int nt = tri.Length / 3;
                log.AppendLine($"  {L} ({m.name}): {nt} triangles, {v.Length} vertices, UV dimensions {string.Join(" ", dims)}, " +
                               $"normals {(nrm.Length == v.Length ? "yes" : "NO")}");

                // the creases: edges between two drawn faces turned by 20 degrees or more (an arris), and open edges
                var edges = new Dictionary<(long, long, long, long, long, long), List<int>>();
                (long, long, long) Q(Vector3 p) => ((long)Mathf.Round(p.x * 1e5f), (long)Mathf.Round(p.y * 1e5f), (long)Mathf.Round(p.z * 1e5f));
                (long, long, long, long, long, long) E(Vector3 p, Vector3 q)
                {
                    var a = Q(p);
                    var b = Q(q);
                    return a.CompareTo(b) <= 0 ? (a.Item1, a.Item2, a.Item3, b.Item1, b.Item2, b.Item3) : (b.Item1, b.Item2, b.Item3, a.Item1, a.Item2, a.Item3);
                }
                var faceN = new Vector3[nt];
                var area = new float[nt];
                for (int t = 0; t < nt; t++)
                {
                    Vector3 a = v[tri[3 * t]], b = v[tri[3 * t + 1]], c = v[tri[3 * t + 2]];
                    var cr = Vector3.Cross(b - a, c - a);
                    area[t] = cr.magnitude / 2f;
                    faceN[t] = cr.normalized;
                    for (int k = 0; k < 3; k++)
                    {
                        var key = E(v[tri[3 * t + k]], v[tri[3 * t + (k + 1) % 3]]);
                        if (!edges.TryGetValue(key, out var l))
                            edges[key] = l = new List<int>();
                        l.Add(t);
                    }
                }
                var creases = new List<(Vector3 a, Vector3 b, float turn)>();
                int open = 0, nonManifold = 0;
                var turns = new SortedDictionary<int, int>();
                foreach (var kv in edges)
                {
                    var k = kv.Key;
                    var a = new Vector3(k.Item1, k.Item2, k.Item3) * 1e-5f;
                    var b = new Vector3(k.Item4, k.Item5, k.Item6) * 1e-5f;
                    if (kv.Value.Count == 1) { open++; continue; }
                    if (kv.Value.Count > 2) { nonManifold++; continue; }
                    float turn = Vector3.Angle(faceN[kv.Value[0]], faceN[kv.Value[1]]);
                    if (turn >= 20f)
                    {
                        creases.Add((a, b, turn));
                        int bin = Mathf.RoundToInt(turn / 5f) * 5;
                        turns[bin] = turns.TryGetValue(bin, out var c0) ? c0 + 1 : 1;
                    }
                }
                var tb = new List<string>();
                foreach (var kv in turns)
                    tb.Add($"{kv.Key}: {kv.Value}");
                log.AppendLine($"    edges: {edges.Count}; open {open} (the undrawn faces' borders); non-manifold {nonManifold}; creases (turn of 20 " +
                               $"degrees or more) {creases.Count}, their turns in degrees to 5: {string.Join(", ", tb)}");
                if (nonManifold > 0)
                    Fail(log, $"{L}: {nonManifold} non-manifold edges");

                // per triangle
                int badCode = 0, badKind = 0, badMask = 0, badChamfer = 0, badSlice = 0, badWinding = 0, badSky = 0, badEdges = 0,
                    badLine = 0, badNormal = 0;
                float worstNormal = 0f, worstSky = 0f, worstEdge = 0f, worstLine = 0f, worstGrad = 0f;
                var kinds = new SortedDictionary<int, (int n, float area)>();
                var slices = new SortedDictionary<string, int>();
                var chamfers = new SortedDictionary<int, int>();
                var masked = 0;
                float years = float.NaN, seed = float.NaN;
                bool oneHistory = true;
                for (int t = 0; t < nt; t++)
                {
                    int i0 = tri[3 * t], i1 = tri[3 * t + 1], i2 = tri[3 * t + 2];
                    int[] I = { i0, i1, i2 };
                    float code = uv[7][i0].y;
                    if (uv[7][i1].y != code || uv[7][i2].y != code || code != Mathf.Round(code) || code < 0f)
                    {
                        badCode++;
                        continue;
                    }
                    int ci = (int)code, slice = ci % 8, mask = (ci / 8) % 8, ch = ci / 64;
                    float kf = uv[2][i0].x;
                    if (uv[2][i1].x != kf || uv[2][i2].x != kf || kf != Mathf.Round(kf) || kf < 0f || kf > 3f)
                    {
                        badKind++;
                        continue;
                    }
                    int kind = (int)kf;
                    kinds[kind] = kinds.TryGetValue(kind, out var ka) ? (ka.n + 1, ka.area + area[t]) : (1, area[t]);
                    string sk = $"{KindName(kind)} {slice}";
                    slices[sk] = slices.TryGetValue(sk, out var sc) ? sc + 1 : 1;
                    chamfers[ch] = chamfers.TryGetValue(ch, out var cc) ? cc + 1 : 1;
                    // a slice by kind: split faces 0..3, the top and beds 4..5, chamfers none (7)
                    bool sliceOk = kind == 1 ? slice == 7 : kind == 2 ? slice <= 3 : slice == 4 || slice == 5;
                    if (!sliceOk)
                        badSlice++;
                    if (level == 0 && (mask != 0))
                        badMask++;
                    if (level == 1 && kind == 1)
                        badKind++;
                    // L0: every triangle the stone's chamfer (one for the stone); L1: what the chamfer keeps, never more
                    if (level == 0 && stoneChamfer < 0)
                        stoneChamfer = ch;
                    if (ch < 0 || (level == 0 && ch != stoneChamfer) || (level == 1 && ch > stoneChamfer) || (mask != 0 && ch == 0))
                        badChamfer++;
                    // the history channels: one stone, one age and seed
                    if (float.IsNaN(years)) { years = uv[1][i0].x; seed = uv[1][i0].y; }
                    foreach (var i in I)
                        if (uv[1][i].x != years || uv[1][i].y != seed)
                            oneHistory = false;
                    // winding against the normals, and the normals against the face
                    foreach (var i in I)
                    {
                        float ang = Vector3.Angle(nrm[i], faceN[t]);
                        worstNormal = Mathf.Max(worstNormal, ang);
                        if (ang > 90f) badWinding++;
                        else if (ang > 0.5f) badNormal++;
                        // UV3: the sky from the normal, 0.5 + 0.5 n_up (up is Unity's y)
                        float sky = Mathf.Abs(uv[3][i].x - (0.5f + 0.5f * nrm[i].y));
                        worstSky = Mathf.Max(worstSky, sky);
                        if (sky > 2e-3f) badSky++;
                    }
                    // the edge distances: d0, d1 in UV6, d2 in UV7.x
                    var D = new float[3, 3];
                    for (int c = 0; c < 3; c++)
                    {
                        D[c, 0] = uv[6][I[c]].x;
                        D[c, 1] = uv[6][I[c]].y;
                        D[c, 2] = uv[7][I[c]].x;
                    }
                    Vector3 P0 = v[i0], P1 = v[i1], P2 = v[i2];
                    Vector3[] P = { P0, P1, P2 };
                    if (level == 0)
                    {
                        // the solid-wireframe encoding: each corner its height over the opposite edge in its own slot, 0 in
                        // the others (the slots travel with the corners, whatever order the import gives them)
                        var used = new bool[3];
                        bool ok = true;
                        for (int c = 0; c < 3 && ok; c++)
                        {
                            int slot = -1;
                            for (int k = 0; k < 3; k++)
                                if (Mathf.Abs(D[c, k]) > 1e-7f)
                                {
                                    if (slot >= 0) { ok = false; break; }
                                    slot = k;
                                }
                            if (!ok || slot < 0 || used[slot]) { ok = false; break; }
                            used[slot] = true;
                            Vector3 q = P[(c + 1) % 3], r = P[(c + 2) % 3];
                            float h = Vector3.Cross(r - q, P[c] - q).magnitude / Mathf.Max((r - q).magnitude, 1e-12f);
                            float e = Mathf.Abs(D[c, slot] - h);
                            worstEdge = Mathf.Max(worstEdge, e);
                            if (e > 1e-5f) ok = false;
                        }
                        if (!ok)
                            badEdges++;
                    }
                    if (level == 1 && mask != 0)
                    {
                        masked++;
                        // a masked slot holds the distance to an arris line in the triangle's plane: affine across the
                        // triangle with a gradient of one, zero on one of L1's creases
                        for (int k = 0; k < 3; k++)
                        {
                            if (((mask >> k) & 1) == 0)
                                continue;
                            // the gradient in the plane from the three corners' values
                            Vector3 e1 = P1 - P0, e2 = P2 - P0;
                            float d0 = D[0, k], d1 = D[1, k] - d0, d2 = D[2, k] - d0;
                            float a11 = Vector3.Dot(e1, e1), a12 = Vector3.Dot(e1, e2), a22 = Vector3.Dot(e2, e2);
                            float det = a11 * a22 - a12 * a12;
                            float x1 = (a22 * d1 - a12 * d2) / det, x2 = (a11 * d2 - a12 * d1) / det;
                            var grad = x1 * e1 + x2 * e2;
                            float gl = grad.magnitude;
                            worstGrad = Mathf.Max(worstGrad, Mathf.Abs(gl - 1f));
                            if (Mathf.Abs(gl - 1f) > 1e-3f) { badLine++; continue; }
                            // two points on the zero line, near the triangle
                            var foot = P0 - grad * (d0 / (gl * gl));
                            var along = Vector3.Cross(faceN[t], grad).normalized;
                            float span = Mathf.Max((P1 - P0).magnitude, (P2 - P0).magnitude);
                            var qa = foot - along * span;
                            var qb = foot + along * span;
                            float best = float.MaxValue;
                            foreach (var cr in creases)
                                best = Mathf.Min(best, Mathf.Max(LineDist(qa, cr.a, cr.b), LineDist(qb, cr.a, cr.b)));
                            worstLine = Mathf.Max(worstLine, best);
                            if (best > 2e-4f) badLine++;
                        }
                    }
                }
                var kl = new List<string>();
                foreach (var kv in kinds)
                    kl.Add($"{KindName(kv.Key)} {kv.Value.n} ({kv.Value.area:F4} m2)");
                var sl = new List<string>();
                foreach (var kv in slices)
                    sl.Add($"{kv.Key}: {kv.Value}");
                var chl = new List<string>();
                foreach (var kv in chamfers)
                    chl.Add($"{kv.Key} mm: {kv.Value}");
                log.AppendLine($"    kinds: {string.Join(", ", kl)}");
                log.AppendLine($"    slices by kind: {string.Join(", ", sl)}; chamfer codes {string.Join(", ", chl)}; {masked} triangles masked");
                log.AppendLine($"    history: years/200 {years}, seed {seed}, {(oneHistory ? "one for the stone" : "NOT ONE")}; normals: the worst " +
                               $"{worstNormal:F3} degrees off the face; sky (UV3) the worst {worstSky:E1} off 0.5 + 0.5 n_up; edge distances the worst " +
                               $"{worstEdge * 1000f:F5} mm off the corners' heights" +
                               (level == 1 ? $"; arris lines: gradient the worst {worstGrad:E1} off one, the zero line the worst {worstLine * 1000f:F3} mm " +
                                             "from a crease" : ""));
                void Count(int n, string what)
                {
                    if (n > 0)
                        Fail(log, $"{L}: {n} triangles {what}");
                }
                Count(badCode, "with no one whole code (UV7.y)");
                Count(badKind, level == 1 ? "with no one face kind (UV2.x), or a chamfer at L1" : "with no one face kind (UV2.x)");
                Count(badSlice, "with a slice not their kind's");
                Count(badMask, "masked at L0 (L0 carries mask 0)");
                Count(badChamfer, "with a chamfer code out of range");
                Count(badWinding, "wound against their normals");
                Count(badNormal, "with normals off their face by over half a degree");
                Count(badSky, "with a sky (UV3.x) not their normal's");
                Count(badEdges, "whose edge distances are not the corners' heights");
                Count(badLine, "with an arris line off L1's creases or not a distance");
                if (!oneHistory)
                    Fail(log, $"{L}: more than one age or seed (UV1)");

                // against the sidecar's numbers, where it gives them
                var want = Find("levels", L, "triangles") ?? Find("levels", L.ToLowerInvariant(), "triangles") ?? Find(L, "triangles");
                if (want is double wt)
                {
                    log.AppendLine($"    triangles {nt} against the sidecar's {wt}");
                    if ((int)wt != nt)
                        Fail(log, $"{L}: {nt} triangles, the sidecar {wt}");
                }
                var budget = Find("levels", L.ToLowerInvariant(), "triangles");
                if (budget is double bt && nt > bt)
                    Fail(log, $"{L}: {nt} triangles over the definition's {bt}");
                if (level == 0)
                {
                    var cm = Find("chamferMm");
                    log.AppendLine($"    the stone's chamfer {stoneChamfer} mm (L0's code)" + (cm is double c ? $", the sidecar's {c}" : ""));
                    if (cm is double cmm && (int)cmm != stoneChamfer)
                        Fail(log, $"L0: the code's chamfer {stoneChamfer} mm, the sidecar's {cmm}");
                }
            }

            /// <summary>The pivot (the definition's, bed-front-left: x along from the left end as the street sees it, y up
            /// from the bed, z back from the face) and the size against the sidecar's.</summary>
            void Pivot(StringBuilder log)
            {
                var b = l1.bounds;
                var b0 = l0.bounds;
                log.AppendLine($"  bounds: L1 {b.min.ToString("F4")} to {b.max.ToString("F4")}, L0 {b0.min.ToString("F4")} to {b0.max.ToString("F4")} " +
                               $"(pivot '{Find("pivot")}')");
                if (Find("pivot") as string == "bed-front-left")
                {
                    if (Mathf.Abs(b.min.x) > 1e-4f || Mathf.Abs(b.min.y) > 1e-4f || Mathf.Abs(b.min.z) > 1e-4f)
                        Fail(log, $"pivot: L1's bounds start at {b.min.ToString("F4")}, not at the bed's front left (0, 0, 0)");
                }
                // the face to the street: the drawn split faces' mean normal looks -z, the top's +y
                Vector3 split = Vector3.zero, top = Vector3.zero;
                var v = l1.vertices;
                var tri = l1.triangles;
                var k = new List<Vector4>();
                l1.GetUVs(2, k);
                for (int t = 0; t < tri.Length; t += 3)
                {
                    var cr = Vector3.Cross(v[tri[t + 1]] - v[tri[t]], v[tri[t + 2]] - v[tri[t]]);
                    if (k[tri[t]].x == 2f) split += cr;
                    if (k[tri[t]].x == 0f) top += cr;
                }
                log.AppendLine($"  the faces' mean normals: the top {top.normalized.ToString("F3")}, the split faces {split.normalized.ToString("F3")}");
                if (top.normalized.y < 0.9f)
                    Fail(log, "orientation: the top does not face up (+y)");
            }

            static float LineDist(Vector3 p, Vector3 a, Vector3 b)
            {
                var d = (b - a).normalized;
                var w = p - a;
                return (w - Vector3.Dot(w, d) * d).magnitude;
            }

            static string KindName(int k) => k switch { 0 => "top", 1 => "chamfer", 2 => "split", 3 => "bed", _ => k.ToString() };
        }

        // ---------------------------------------------------------------------------------------------------------
        // The piece on the stand

        sealed class Piece
        {
            public string name;
            public MeshRenderer l0, l1, shadow;
            public Vector3 front;        // street metres: the middle of its face to the street
            public float baseZ, height;
            public readonly List<Object> made = new List<Object>();

            /// <summary>Which level shows: L0 casting no shadow (L1's shadow-only copy casts it, so both levels' shadows
            /// are the same), or L1 casting its own; -noline takes L1's lit line away, -flat the patches, -near forces
            /// the near detail.</summary>
            public void Show(string config, Material m)
            {
                bool isL0 = config.StartsWith("L0");
                l0.enabled = isL0;
                l0.sharedMaterial = m;
                l0.shadowCastingMode = ShadowCastingMode.Off;
                shadow.enabled = isL0;
                shadow.sharedMaterial = m;
                shadow.shadowCastingMode = ShadowCastingMode.ShadowsOnly;
                l1.enabled = !isL0;
                l1.sharedMaterial = m;
                l1.shadowCastingMode = ShadowCastingMode.On;
                Shader.SetGlobalFloat("_OS_PatchLineOff", config.Contains("noline") ? 1f : 0f);
                Shader.SetGlobalFloat("_OS_PatchFlat", config.Contains("flat") ? 1f : 0f);
                // (-near, a control for the patch fade: OS_Near 1 everywhere in the frame, Detail.hlsl's own debug
                // switch, so the mips alone filter the patches' bands)
                Shader.SetGlobalFloat("_OS_NearForce", config.EndsWith("-near") ? 2f : 0f);
            }

            public void Hide()
            {
                l0.enabled = l1.enabled = shadow.enabled = false;
            }

            /// <summary>A judging view by name: "5" face-on from 5 m with the top seen at 20 degrees, "eye5" from 5 m
            /// along the ground at a person's eye height; all through the 28 mm lens.</summary>
            public (string name, Vector3 pos, Vector3 target, float fov) View(string name)
            {
                if (name.StartsWith("eye"))
                {
                    float d = float.Parse(name.Substring(3), System.Globalization.CultureInfo.InvariantCulture);
                    float x = front.x, y = front.y - d;
                    return (name, new Vector3(x, y, Ground(x, y) + Eye), front, Lens28);
                }
                return ViewAt(float.Parse(name, System.Globalization.CultureInfo.InvariantCulture), name + "m");
            }

            /// <summary>Face-on from a distance, the top seen at 20 degrees.</summary>
            public (string name, Vector3 pos, Vector3 target, float fov) ViewAt(float dist, string name)
            {
                float r = Down * Mathf.Deg2Rad;
                return (name, front + new Vector3(0f, -Mathf.Cos(r), Mathf.Sin(r)) * dist, front, Lens28);
            }
        }

        // ---------------------------------------------------------------------------------------------------------
        // The kit: the patch array and its globals, the judged materials, the grey swap and the id render

        sealed class Kit : System.IDisposable
        {
            public readonly R2aPatches.Built patches;
            public readonly Material material, grey, ids, blank;
            readonly Dictionary<Renderer, Material[]> greySwap = new Dictionary<Renderer, Material[]>();
            readonly List<Object> made = new List<Object>();
            readonly List<Piece> pieces = new List<Piece>();
            bool idsChecked;

            public Kit(StringBuilder log)
            {
                patches = R2aPatches.Build(Repo);
                log.Append(patches.log);
                Shader.SetGlobalTexture("_OS_PatchMap", patches.map);
                Shader.SetGlobalFloat("_OS_PatchPerMetre", patches.perMetre);
                Arm("as-built");
                Shader.SetGlobalFloat("_OS_PatchFlat", 0f);
                Shader.SetGlobalFloat("_OS_PatchLineOff", 0f);
                Shader.SetGlobalFloat("_OS_NearForce", 0f);
                var slate = AssetDatabase.LoadAssetAtPath<Material>(SlateMaterial);
                material = new Material(slate) { name = "r2a slate, patched (never saved)", hideFlags = HideFlags.DontSave };
                material.EnableKeyword("OS_PATCHES");
                material.SetFloat("_Grey", 0f);
                grey = new Material(material) { name = "r2a slate, patched, grey (never saved)", hideFlags = HideFlags.DontSave };
                grey.SetFloat("_Grey", 1f);
                var idShader = Shader.Find("Overstory/R2aIds");
                ids = new Material(idShader) { name = "r2a ids (never saved)", hideFlags = HideFlags.DontSave };
                blank = new Material(idShader) { name = "r2a blank (never saved)", hideFlags = HideFlags.DontSave };
                blank.SetFloat("_Mode", 2f);
                made.AddRange(new Object[] { material, grey, ids, blank });
                log.AppendLine($"materials: copies of {SlateMaterial} with OS_PATCHES " +
                               $"({material.IsKeywordEnabled("OS_PATCHES")}), _Grey 0 and 1; never saved");
            }

            public void Arm(string name)
            {
                if (!patches.shifts.TryGetValue(name, out var shift))
                    throw new System.ArgumentException($"no arm '{name}' in the patches' manifest");
                Shader.SetGlobalFloatArray("_OS_PatchShift", shift);
            }

            /// <summary>The chamfer's form from a definition: its leg along each face per mm of UV7's width (the code's
            /// width is the leg when 1), and its angle to the face (45 degrees for a square arris).</summary>
            public void Chamfer(float legPerMm, float angle, string source, StringBuilder log)
            {
                float a = angle * Mathf.Deg2Rad;
                var c = new Vector4(legPerMm / 1000f, Mathf.Cos(a), Mathf.Sin(a), 0f);
                Shader.SetGlobalVector("_OS_Chamfer", c);
                log.AppendLine($"chamfer: {source}; _OS_Chamfer ({c.x}, {c.y:F4}, {c.z:F4})");
            }

            /// <summary>Grey: every stone in the frame drawn in grey light (the gully's own materials swapped for grey
            /// copies, in memory), the judged piece's grey copy set by Show.</summary>
            public void Look(bool toGrey)
            {
                if (!toGrey)
                {
                    foreach (var kv in greySwap)
                        if (kv.Key != null)
                            kv.Key.sharedMaterials = kv.Value;
                    greySwap.Clear();
                    return;
                }
                var copies = new Dictionary<Material, Material>();
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    if (IsPiece(r))
                        continue;
                    var mats = r.sharedMaterials;
                    bool any = false;
                    var swapped = new Material[mats.Length];
                    for (int i = 0; i < mats.Length; i++)
                    {
                        var m = mats[i];
                        swapped[i] = m;
                        if (m == null || !m.HasProperty("_Grey") || m.GetFloat("_Grey") > 0.5f)
                            continue;
                        if (!copies.TryGetValue(m, out var g))
                        {
                            g = new Material(m) { name = m.name + " grey (never saved)", hideFlags = HideFlags.DontSave };
                            g.SetFloat("_Grey", 1f);
                            copies[m] = g;
                            made.Add(g);
                        }
                        swapped[i] = g;
                        any = true;
                    }
                    if (any)
                    {
                        greySwap[r] = mats;
                        r.sharedMaterials = swapped;
                    }
                }
            }

            /// <summary>(a search finds no DontSave object, so the pieces' renderers are never among the town's)</summary>
            bool IsPiece(Renderer r)
            {
                foreach (var p in pieces)
                    if (r == p.l0 || r == p.l1 || r == p.shadow)
                        return true;
                return false;
            }

            /// <summary>A piece set on the stand: its L0 and L1 meshes (in Unity's order, y up, the face to the street
            /// towards -z), its L1 bounds centred on the stand in plan and its bed (L1's lowest point) lowered onto the
            /// ground at the lowest corner (the ground's slope sinks the rest a little, as a stone lies bedded), and
            /// L1's shadow-only copy. Its face's middle is where the views look: the bounds' front, half its height up.
            /// </summary>
            public Piece Place(string name, Vector2 stand, Mesh l0, Mesh l1, StringBuilder log)
            {
                var b = l1.bounds;
                float halfL = b.extents.x, halfD = b.extents.z;
                float lowest = float.MaxValue, highest = float.MinValue;
                var under = new HashSet<string>();
                foreach (var cx in new[] { -halfL, halfL })
                    foreach (var cz in new[] { -halfD, halfD })
                    {
                        float g = Ground(stand.x + cx, stand.y + cz, out var what);
                        under.Add(what);
                        lowest = Mathf.Min(lowest, g);
                        highest = Mathf.Max(highest, g);
                    }
                // (the mesh's own origin, its pivot, moved so the bounds sit centred on the stand, the bed on the ground)
                var at = StreetSpace.ToUnity(stand.x, stand.y, lowest) - new Vector3(b.center.x, b.min.y, b.center.z);
                var piece = new Piece { name = name, baseZ = lowest, height = b.size.y };
                piece.l0 = Make(name + " L0", l0, at, piece);
                piece.l1 = Make(name + " L1", l1, at, piece);
                piece.shadow = Make(name + " L1 shadow", l1, at, piece);
                piece.front = new Vector3(stand.x, stand.y - halfD, lowest + b.size.y / 2f);
                pieces.Add(piece);
                log.AppendLine($"{name} on the stand ({stand.x}, {stand.y}): {b.size.x:F3} x {b.size.z:F3} m in plan, {b.size.y:F3} high " +
                               $"(L1's bounds); the ground ({string.Join(", ", under)}) {lowest:F3} to {highest:F3} m under its " +
                               $"corners, its bed at {lowest:F3} (sunk {highest - lowest:F3} m at the highest); its face's middle " +
                               $"({piece.front.x:F2}, {piece.front.y:F2}, {piece.front.z:F2}); L0 {l0.triangles.Length / 3} triangles, " +
                               $"L1 {l1.triangles.Length / 3}");
                return piece;
            }

            MeshRenderer Make(string name, Mesh mesh, Vector3 at, Piece piece)
            {
                var go = new GameObject(name) { hideFlags = HideFlags.DontSave };
                go.transform.SetPositionAndRotation(at, Quaternion.identity);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var r = go.AddComponent<MeshRenderer>();
                r.receiveShadows = true;
                r.enabled = false;
                piece.made.Add(go);
                // (an imported mesh is an asset: never destroyed here)
                if (!made.Contains(mesh) && !EditorUtility.IsPersistent(mesh))
                    made.Add(mesh);
                return r;
            }

            /// <summary>
            /// The piece's ids and normals (R2aIds.shader) and its mask, from the camera as the frames see it: every
            /// other renderer drawn black (it still hides what lies behind it), particles and lines off, post and the
            /// renderer features off, HDR and MSAA off, into a linear 8-bit target (no intermediate's rounding: the
            /// slices' values are checked exact). All restored after.
            /// </summary>
            public void Ids(Camera cam, Renderer target, string stem, StringBuilder log)
            {
                var rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
                var data = cam.GetUniversalAdditionalCameraData();
                bool post = data.renderPostProcessing, hdr = cam.allowHDR, msaa = cam.allowMSAA;
                var clear = cam.clearFlags;
                var bg = cam.backgroundColor;
                var before = cam.targetTexture;
                var mats = new Dictionary<Renderer, Material[]>();
                var off = new List<Renderer>();
                var feats = new Dictionary<ScriptableRendererFeature, bool>();
                int w = PlayerFrame.Width, h = PlayerFrame.Height;
                var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear) { antiAliasing = 1 };
                var tex = new Texture2D(w, h, TextureFormat.RGBA32, false, true);
                try
                {
                    // (the town's renderers, and the piece's own: objects made DontSave are not found by a search)
                    var all = new List<Renderer>(Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None));
                    foreach (var p in pieces)
                        all.AddRange(new Renderer[] { p.l0, p.l1, p.shadow });
                    foreach (var r in all)
                    {
                        if (!r.enabled || mats.ContainsKey(r))
                            continue;
                        if (r is ParticleSystemRenderer || r is LineRenderer || r is TrailRenderer)
                        {
                            r.enabled = false;
                            off.Add(r);
                            continue;
                        }
                        mats[r] = r.sharedMaterials;
                        var m = new Material[r.sharedMaterials.Length];
                        for (int i = 0; i < m.Length; i++)
                            m[i] = r == target ? ids : blank;
                        r.sharedMaterials = m;
                    }
                    if (rendererData != null)
                        foreach (var f in rendererData.rendererFeatures)
                            if (f != null)
                            {
                                feats[f] = f.isActive;
                                f.SetActive(false);
                            }
                    if (!idsChecked)
                    {
                        idsChecked = true;
                        var states = new List<string>();
                        if (rendererData != null)
                            foreach (var f in rendererData.rendererFeatures)
                                if (f != null)
                                    states.Add($"{f.name} {(f.isActive ? "on" : "off")}");
                        log.AppendLine($"  ids render: shader {ids.shader.name} supported {ids.shader.isSupported}, errors " +
                                       $"{ShaderUtil.ShaderHasError(ids.shader)}; renderer {(rendererData != null ? rendererData.name : "none")} " +
                                       $"features {string.Join(", ", states)}; async compiling {ShaderUtil.allowAsyncCompilation}");
                    }
                    data.renderPostProcessing = false;
                    cam.allowHDR = false;
                    cam.allowMSAA = false;
                    cam.clearFlags = CameraClearFlags.SolidColor;
                    cam.backgroundColor = new Color(0f, 0f, 0f, 0f);
                    cam.targetTexture = rt;
                    Directory.CreateDirectory(Path.GetDirectoryName(stem));
                    Color32[] idPixels = null;
                    foreach (var (mode, suffix) in new[] { (0f, "ids"), (1f, "normals") })
                    {
                        ids.SetFloat("_Mode", mode);
                        LT1Render.Render(cam, rt);
                        LT1Render.Render(cam, rt);
                        var prev = RenderTexture.active;
                        RenderTexture.active = rt;
                        tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
                        tex.Apply();
                        RenderTexture.active = prev;
                        File.WriteAllBytes($"{stem}-{suffix}.png", tex.EncodeToPNG());
                        if (mode == 0f)
                            idPixels = tex.GetPixels32();
                    }
                    // the mask: the piece's pixels (an id's green is never 0 on a stone); and the slices' values, which
                    // must be exact (32 slice + 16) if nothing rounded them on the way
                    var counts = new SortedDictionary<int, int>();
                    int inexact = 0, n = 0;
                    var mask = new Color32[idPixels.Length];
                    for (int i = 0; i < idPixels.Length; i++)
                    {
                        byte g = idPixels[i].g;
                        bool on = g > 0;
                        mask[i] = on ? new Color32(255, 255, 255, 255) : new Color32(0, 0, 0, 255);
                        if (!on)
                            continue;
                        n++;
                        if ((g - 16) % 32 != 0)
                            inexact++;
                        counts[g] = counts.TryGetValue(g, out var k) ? k + 1 : 1;
                    }
                    tex.SetPixels32(mask);
                    tex.Apply();
                    File.WriteAllBytes($"{stem}-mask.png", tex.EncodeToPNG());
                    var parts = new List<string>();
                    foreach (var kv in counts)
                        parts.Add((kv.Key - 16) % 32 == 0 ? $"slice {(kv.Key - 16) / 32}: {kv.Value}" : $"g {kv.Key}: {kv.Value}");
                    log.AppendLine($"  ids {Path.GetFileName(Path.GetDirectoryName(stem))}/{Path.GetFileName(stem)}: {n} px; " +
                                   $"{string.Join(", ", parts)}; {inexact} inexact");
                    if (inexact > 0)
                        Debug.LogWarning($"[LT1R2a] ids {stem}: {inexact} pixels' slice values are not exact: something rounded them");
                }
                finally
                {
                    foreach (var kv in mats)
                        if (kv.Key != null)
                            kv.Key.sharedMaterials = kv.Value;
                    foreach (var r in off)
                        if (r != null)
                            r.enabled = true;
                    foreach (var kv in feats)
                        kv.Key.SetActive(kv.Value);
                    data.renderPostProcessing = post;
                    cam.allowHDR = hdr;
                    cam.allowMSAA = msaa;
                    cam.clearFlags = clear;
                    cam.backgroundColor = bg;
                    cam.targetTexture = before;
                    rt.Release();
                    Object.DestroyImmediate(rt);
                    Object.DestroyImmediate(tex);
                }
            }

            public void Dispose()
            {
                Look(false);
                foreach (var p in pieces)
                    foreach (var o in p.made)
                        if (o != null)
                            Object.DestroyImmediate(o);
                foreach (var o in made)
                    if (o != null)
                        Object.DestroyImmediate(o);
                if (patches?.map != null)
                    Object.DestroyImmediate(patches.map);
                Shader.SetGlobalFloat("_OS_PatchFlat", 0f);
                Shader.SetGlobalFloat("_OS_PatchLineOff", 0f);
                Shader.SetGlobalFloat("_OS_NearForce", 0f);
            }
        }

        // ---------------------------------------------------------------------------------------------------------
        // The ground

        /// <summary>The ground's height (street z) at a street (x, y): the highest of the heart's ground meshes under it
        /// (as the stair sank them), by a ray straight down.</summary>
        static float Ground(float x, float y) => Ground(x, y, out _);

        static float Ground(float x, float y, out string what)
        {
            float best = float.MinValue;
            what = null;
            var origin = StreetSpace.ToUnity(x, y, 200f);
            foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
            {
                if (!mf.gameObject.name.StartsWith("ground") || mf.sharedMesh == null)
                    continue;
                var r = mf.GetComponent<MeshRenderer>();
                if (r == null || !r.enabled)
                    continue;
                var bounds = r.bounds;
                if (origin.x < bounds.min.x || origin.x > bounds.max.x || origin.z < bounds.min.z || origin.z > bounds.max.z)
                    continue;
                var mesh = mf.sharedMesh;
                var v = mesh.vertices;
                var l2w = mf.transform.localToWorldMatrix;
                for (int s = 0; s < mesh.subMeshCount; s++)
                {
                    var t = mesh.GetTriangles(s);
                    for (int i = 0; i < t.Length; i += 3)
                    {
                        Vector3 a = l2w.MultiplyPoint3x4(v[t[i]]), b = l2w.MultiplyPoint3x4(v[t[i + 1]]), c = l2w.MultiplyPoint3x4(v[t[i + 2]]);
                        // (a vertical ray: the triangle's barycentrics in plan, its height there)
                        float d = (b.z - c.z) * (a.x - c.x) + (c.x - b.x) * (a.z - c.z);
                        if (Mathf.Abs(d) < 1e-9f)
                            continue;
                        float l1 = ((b.z - c.z) * (origin.x - c.x) + (c.x - b.x) * (origin.z - c.z)) / d;
                        float l2 = ((c.z - a.z) * (origin.x - c.x) + (a.x - c.x) * (origin.z - c.z)) / d;
                        float l3 = 1f - l1 - l2;
                        if (l1 < -1e-6f || l2 < -1e-6f || l3 < -1e-6f)
                            continue;
                        float z = l1 * a.y + l2 * b.y + l3 * c.y;
                        if (z > best)
                        {
                            best = z;
                            what = mf.gameObject.name;
                        }
                    }
                }
            }
            if (best == float.MinValue)
                throw new System.InvalidOperationException($"no ground under ({x}, {y})");
            return best;
        }
    }
}
