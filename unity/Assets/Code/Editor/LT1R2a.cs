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
    /// Block -moments m [-looks grey,material] [-configs L0,L1,L1-noline,L0-flat] [-views 1,5,8,12,eye5]: the harness's
    ///     test block (R2aBlock) at the stand, in one light per run: the patch array, the arm and L1's lit line before the
    ///     stones arrive. Frames into frames/block/&lt;moment&gt;/&lt;look&gt;/&lt;config&gt;/&lt;view&gt;.png, the ids, normals and
    ///     mask into frames/block/ids/&lt;level&gt;/, the log into logs/block-&lt;moment&gt;.txt.
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

        static LightRig Rig(string moment) => AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");

        // The stand (judging harness): where the judged stone lies, in street metres, on the Gully Steps lane 1.8 m short
        // of the flight's foot (LT1Stone.Foot), clear of the gully, its face to the street (south, -y), the cameras
        // coming up the lane from the street. No lamp stands near: the nearest is the Landing's, 13 m up the flight
        // (Art/Blockout/heart/lights.json), and the three judging rigs have the lamps off.
        static readonly Vector2 Stand = new Vector2(49.3f, 22.6f);
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
        // The test block

        public static void Block()
        {
            string moment = Cli.Arg("-moments", "1600-low-sun");
            var looks = Cli.Arg("-looks", "grey,material").Split(',');
            var configs = Cli.Arg("-configs", "L0,L1,L1-noline").Split(',');
            var viewNames = Cli.Arg("-views", "1,5,8,12,eye5").Split(',');
            var log = new StringBuilder();
            log.AppendLine($"LT1R2a.Block, {System.DateTime.Now:yyyy-MM-dd HH:mm}: {moment}; looks {string.Join(",", looks)}; " +
                           $"configs {string.Join(",", configs)}; views {string.Join(",", viewNames)}");
            Run(moment, log, (stage, shot, kit) =>
            {
                // (the harness's chamfer form for the block, which has no part definition: the leg along each face in mm
                // as UV7 codes it, at 45 degrees; the stones take theirs from their definition)
                kit.Chamfer(1f, 45f, "the block's own (a harness fixture): leg, 45 degrees", log);
                var spec = R2aBlock.Default;
                var piece = kit.Place("block", R2aBlock.Build(spec, true), R2aBlock.Build(spec, false), spec.depth, spec.height, log);
                Judge(stage, shot, kit, piece, moment, looks, configs, viewNames, Path.Combine(OutDir, "block"), log);
            });
            Directory.CreateDirectory(LogDir);
            File.WriteAllText(Path.Combine(LogDir, $"block-{moment}.txt"), log.ToString());
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
                    piece.Show(config, grey ? kit.grey : kit.material);
                    foreach (var v in views)
                    {
                        LT1Stone.Aim(stage, shot, v);
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
        // The piece on the stand

        sealed class Piece
        {
            public string name;
            public MeshRenderer l0, l1, shadow;
            public Vector3 front;        // street metres: the middle of its face to the street
            public float baseZ, height;
            public readonly List<Object> made = new List<Object>();

            /// <summary>Which level shows: L0 casting no shadow (L1's shadow-only copy casts it, so both levels' shadows
            /// are the same), or L1 casting its own; -noline takes L1's lit line away, -flat the patches.</summary>
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
                float dist = float.Parse(name, System.Globalization.CultureInfo.InvariantCulture);
                float r = Down * Mathf.Deg2Rad;
                return (name + "m", front + new Vector3(0f, -Mathf.Cos(r), Mathf.Sin(r)) * dist, front, Lens28);
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

            /// <summary>A piece set on the stand: its L0 and L1 meshes (in Unity's order, standing on y = 0, the face to
            /// the street at z = -depth/2), lowered onto the ground at its lowest corner (the ground's slope sinks the
            /// rest a little, as a stone lies bedded), and L1's shadow-only copy.</summary>
            public Piece Place(string name, Mesh l0, Mesh l1, float depth, float height, StringBuilder log)
            {
                var b = l1.bounds;
                float lowest = float.MaxValue, highest = float.MinValue;
                var under = new HashSet<string>();
                foreach (var cx in new[] { b.min.x, b.max.x })
                    foreach (var cz in new[] { b.min.z, b.max.z })
                    {
                        float g = Ground(Stand.x + cx, Stand.y + cz, out var what);
                        under.Add(what);
                        lowest = Mathf.Min(lowest, g);
                        highest = Mathf.Max(highest, g);
                    }
                var at = StreetSpace.ToUnity(Stand.x, Stand.y, lowest);
                var piece = new Piece { name = name, baseZ = lowest, height = height };
                piece.l0 = Make(name + " L0", l0, at, piece);
                piece.l1 = Make(name + " L1", l1, at, piece);
                piece.shadow = Make(name + " L1 shadow", l1, at, piece);
                piece.front = new Vector3(Stand.x, Stand.y - depth / 2f, lowest + height / 2f);
                pieces.Add(piece);
                log.AppendLine($"{name} on the stand ({Stand.x}, {Stand.y}): the ground ({string.Join(", ", under)}) {lowest:F3} to {highest:F3} m under " +
                               $"its corners, its foot at {lowest:F3} (sunk {highest - lowest:F3} m at the highest); its face's " +
                               $"middle ({piece.front.x:F2}, {piece.front.y:F2}, {piece.front.z:F2}); L0 {l0.vertexCount / 3} " +
                               $"triangles, L1 {l1.vertexCount / 3}");
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
                if (!made.Contains(mesh))
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
