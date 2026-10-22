using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.Play
{
    /// <summary>
    /// A walk the player takes by itself (LT1g, the walk, W4; W7's capture walks the same way): the walker steered by a
    /// script instead of the keys, logged, and judged for falls and sticks.
    ///
    ///     OverstoryPlayable.app/Contents/MacOS/Overstory -walk tools/playable/walks/a-e-a.walk
    ///         [-walk-log out.csv] [-walk-fps 30] [-walk-capture dir] [-walk-stay]
    ///
    /// The script, one command a line, street metres (x along the Row, y up the hill), # for a comment:
    ///     start x y fx fy     feet at (x, y) on the ground, facing (fx, fy)
    ///     pace walk|brisk     1.4 or 2.2 m/s (the flights slow it as they slow a player)
    ///     to x y              walk there (through it, if another `to` follows)
    ///     look x y z | off    keep the eye on a point while walking, or face the way again
    ///     wait s              stand
    ///     shot name           a still of the screen (into -walk-capture, else beside the log)
    ///     mark label          a line in the log
    ///     view n              a view key (1 to 9): the corner's view holds the camera
    ///     takeover            what a movement key does to a held view (walking at eye height over ground, else flying)
    ///     free                V: the free camera, or back to walking on the ground under it
    ///     fly s [pitch]       the free camera forward for s seconds, the view pitched (degrees, up positive)
    ///     expect walk|free|held   fail unless the walker is so
    ///     end
    ///
    /// -walk-fps fixes each frame's time (Time.captureFramerate), so the walk is the same however fast the machine draws;
    /// -walk-capture also writes every frame, numbered, for a film. The log (CSV) holds each frame's time, place, speed,
    /// whether the feet are on the ground, the proxy under them, the flight's share of speed, the mode and the walker's
    /// physics time. At the end the player log gets one line ("[WalkScript] ... PASS" or "FAIL") and the player quits,
    /// 0 for a pass (unless -walk-stay).
    ///
    /// A fall: the feet leave the ground and land more than 0.5 m lower, sink under the walk surface, or the walker is put
    /// back after falling (Walker.Falls). A stick: the walk is asked to move and covers under 0.15 m in a second; a leg
    /// not reached in its time (its length at a third of the pace, plus 10 s) is abandoned and counted too.
    /// </summary>
    [DefaultExecutionOrder(40)]
    public class WalkScript : MonoBehaviour
    {
        public Walker walker;
        public WalkWorld world;

        struct Cmd { public string op; public float[] a; public string text; public int line; }

        readonly List<Cmd> cmds = new List<Cmd>();
        string source, logPath, captureDir;
        bool stay;
        int fps;
        StreamWriter log;
        readonly List<double> physics = new List<double>();
        int reached, legs, falls, sticks, abandoned, sunk;
        float t;
        int frame;
        bool brisk;
        bool lookOn;
        Vector3 lookAt;
        float faceYaw, faceRate;
        float airStart;
        bool wasGrounded = true;
        string evt = "";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void FromCommandLine()
        {
            if (Application.isEditor)
                return;
            var args = System.Environment.GetCommandLineArgs();
            string path = null, logp = null, cap = null;
            int fps = 30;
            bool stay = false;
            for (int i = 0; i < args.Length; i++)
            {
                string next = i + 1 < args.Length ? args[i + 1] : null;
                switch (args[i])
                {
                    case "-walk": path = next; break;
                    case "-walk-log": logp = next; break;
                    case "-walk-capture": cap = next; break;
                    case "-walk-fps": int.TryParse(next, NumberStyles.Integer, CultureInfo.InvariantCulture, out fps); break;
                    case "-walk-stay": stay = true; break;
                }
            }
            if (string.IsNullOrEmpty(path))
                return;
            var walker = Object.FindFirstObjectByType<Walker>();
            if (walker == null)
            {
                Debug.LogError("[WalkScript] no walker in the scene");
                Application.Quit(2);
                return;
            }
            var ws = walker.gameObject.AddComponent<WalkScript>();
            ws.walker = walker;
            ws.world = walker.world;
            ws.source = path;
            ws.logPath = logp ?? Path.ChangeExtension(path, null) + "-log.csv";
            ws.captureDir = cap;
            ws.fps = Mathf.Max(fps, 1);
            ws.stay = stay;
            walker.Scripted = true;
        }

        static float F(string s) => float.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture);
        static string N(double v, string f) => v.ToString(f, CultureInfo.InvariantCulture);

        void Parse()
        {
            int n = 0;
            foreach (var raw in File.ReadAllLines(source))
            {
                n++;
                string line = raw;
                int hash = line.IndexOf('#');
                if (hash >= 0)
                    line = line.Substring(0, hash);
                var parts = line.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length == 0)
                    continue;
                var c = new Cmd { op = parts[0], line = n, text = string.Join(" ", parts, 1, parts.Length - 1) };
                if (c.op == "start" || c.op == "to" || c.op == "wait" || c.op == "view" || c.op == "fly" || (c.op == "look" && c.text != "off"))
                {
                    c.a = new float[parts.Length - 1];
                    for (int i = 1; i < parts.Length; i++)
                        c.a[i - 1] = F(parts[i]);
                }
                cmds.Add(c);
            }
        }

        static Vector3 U(float x, float y, float z = 0f) => StreetSpace.ToUnity(x, y, z);

        IEnumerator Start()
        {
            Time.captureFramerate = fps;
            Parse();
            if (captureDir != null)
                Directory.CreateDirectory(captureDir);
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(logPath)));
            log = new StreamWriter(logPath, false, new UTF8Encoding(false));
            log.WriteLine("t,frame,x,y,z,speed,grounded,under,factor,mode,physics_us,event,simulate_us");
            for (int i = 0; i < 10; i++)
                yield return null;   // the views, lights and proxies settle

            for (int ci = 0; ci < cmds.Count; ci++)
            {
                var c = cmds[ci];
                switch (c.op)
                {
                    case "start":
                    {
                        float yaw = c.a.Length >= 4 ? Yaw(U(c.a[2], c.a[3]) - U(c.a[0], c.a[1])) : 0f;
                        // the walk surface there (the highest ground, ramp, landing or stoop: not an eave over a door), and
                        // out along the facing until the body fits (a drawn house's sill or step stands out of its front)
                        Vector3 fwd = Quaternion.Euler(0f, yaw, 0f) * Vector3.forward;
                        bool placed = false;
                        for (float o = 0f; o <= 1.0f + 1e-3f && !placed; o += 0.1f)
                        {
                            Vector3 at = U(c.a[0], c.a[1], 200f) + fwd * o;
                            float best = float.NegativeInfinity;
                            foreach (var h in Physics.RaycastAll(at, Vector3.down, 400f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                            {
                                var wp = WalkWorld.Of(h.collider);
                                if (wp != null && WalkProxy.Walkable(wp.kind) && h.point.y > best)
                                    best = h.point.y;
                            }
                            if (float.IsNegativeInfinity(best))
                                continue;
                            placed = walker.Place(new Vector3(at.x, best, at.z), yaw);
                            if (placed && o > 0f)
                                Event($"start {o:F1} m out");
                        }
                        if (!placed)
                        {
                            Fail($"line {c.line}: the walker does not fit at the start, nor 1 m out from it");
                            yield break;
                        }
                        faceYaw = yaw;
                        Event("start");
                        yield return null;
                        break;
                    }
                    case "pace":
                        brisk = c.text == "brisk";
                        Event("pace " + c.text);
                        break;
                    case "look":
                        lookOn = c.text != "off";
                        if (lookOn)
                            lookAt = U(c.a[0], c.a[1], c.a[2]);
                        break;
                    case "mark":
                        Event("mark " + c.text);
                        break;
                    case "shot":
                        Shot(c.text);
                        Step(Vector3.zero, false);
                        yield return null;
                        break;
                    case "wait":
                    {
                        float until = t + c.a[0];
                        while (t < until)
                        {
                            Step(Vector3.zero, false);
                            yield return null;
                        }
                        break;
                    }
                    case "to":
                    {
                        Vector3 goal = U(c.a[0], c.a[1]);
                        bool through = ci + 1 < cmds.Count && cmds[ci + 1].op == "to";
                        Vector3 from = walker.Feet;
                        float dist = Vector2.Distance(new Vector2(from.x, from.z), new Vector2(goal.x, goal.z));
                        float limit = t + dist / ((brisk ? walker.briskSpeed : walker.walkSpeed) / 3f) + 10f;
                        float stuck = 0f, window = 0f;
                        Vector3 last = from;
                        bool stuckNow = false;
                        legs++;
                        while (true)
                        {
                            Vector3 f = walker.Feet;
                            var d = new Vector3(goal.x - f.x, 0f, goal.z - f.z);
                            if (d.magnitude < (through ? 0.6f : 0.25f))
                            {
                                reached++;
                                Event($"reached {N(c.a[0], "F1")} {N(c.a[1], "F1")}");
                                break;
                            }
                            if (t > limit)
                            {
                                abandoned++;
                                Event($"abandoned {N(c.a[0], "F1")} {N(c.a[1], "F1")}");
                                break;
                            }
                            Step(d, true);
                            yield return null;
                            // a stick: under 0.15 m covered in a second while asked to move
                            window += Time.deltaTime;
                            if (window >= 1f)
                            {
                                float moved = Vector2.Distance(new Vector2(walker.Feet.x, walker.Feet.z), new Vector2(last.x, last.z));
                                if (moved < 0.15f)
                                {
                                    stuck += window;
                                    if (!stuckNow)
                                    {
                                        sticks++;
                                        stuckNow = true;
                                        Event("stick");
                                    }
                                }
                                else
                                {
                                    stuck = 0f;
                                    stuckNow = false;
                                }
                                last = walker.Feet;
                                window = 0f;
                            }
                        }
                        break;
                    }
                    case "view":
                    {
                        // a view key (PlayKeys: 1 to 9): the corner's view holds the camera until the walker takes it
                        int i = Mathf.RoundToInt(c.a[0]) - 1;
                        var corner = walker.corner;
                        if (corner == null || corner.views == null || i < 0 || i >= corner.views.Length)
                        {
                            Fail($"line {c.line}: no view {i + 1}");
                            yield break;
                        }
                        corner.SetView(i);
                        Event($"view {i + 1} ({corner.views[i].name})");
                        for (int k = 0; k < 3; k++)
                        {
                            Step(Vector3.zero, false);
                            yield return null;
                        }
                        break;
                    }
                    case "takeover":
                        // what a movement key does to a held view (Walker.Update): walking if it stands at eye height
                        // over ground, else the free camera
                        walker.TakeOver();
                        faceYaw = walker.Yaw;
                        Event("takeover: " + walker.mode);
                        Step(Vector3.zero, false);
                        yield return null;
                        break;
                    case "free":
                        // V (PlayKeys)
                        walker.ToggleFree();
                        faceYaw = walker.Yaw;
                        Event("V: " + walker.mode);
                        Step(Vector3.zero, false);
                        yield return null;
                        break;
                    case "expect":
                    {
                        string want = c.text.Trim().ToLowerInvariant();
                        if (walker.mode.ToString().ToLowerInvariant() != want)
                        {
                            Fail($"line {c.line}: the walker is {walker.mode}, not {want}");
                            yield break;
                        }
                        Event("is " + want);
                        break;
                    }
                    case "fly":
                    {
                        // forward for s seconds, the view pitched (degrees, up positive): the free camera's W
                        float until = t + c.a[0], pitch = c.a.Length > 1 ? c.a[1] : 0f;
                        Vector3 start = walker.view.transform.position;
                        while (t < until)
                        {
                            walker.Face(faceYaw, pitch);
                            walker.Drive(Vector2.up, false);
                            yield return null;
                        }
                        Event($"flew {Vector3.Distance(start, walker.view.transform.position):F1} m");
                        break;
                    }
                    case "end":
                        ci = cmds.Count;
                        break;
                    default:
                        Fail($"line {c.line}: unknown command '{c.op}'");
                        yield break;
                }
            }
            // stand a moment so the last frames settle into the log
            for (int i = 0; i < fps / 2; i++)
            {
                Step(Vector3.zero, false);
                yield return null;
            }
            Finish();
        }

        static float Yaw(Vector3 d) => Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;

        /// <summary>One frame of steering: towards d (Unity, level), facing the way or the look point; then the log.</summary>
        void Step(Vector3 d, bool go)
        {
            float dt = Time.deltaTime;
            float yaw = faceYaw, pitch = 0f;
            if (lookOn)
            {
                Vector3 eye = walker.view.transform.position;
                Vector3 to = lookAt - eye;
                yaw = Yaw(to);
                pitch = Mathf.Atan2(to.y, new Vector2(to.x, to.z).magnitude) * Mathf.Rad2Deg;
            }
            else if (go && d.sqrMagnitude > 1e-6f)
            {
                // the view turns to the way with a 0.3 s half-life, as a person's head leads the walk
                float target = Yaw(d);
                float diff = Mathf.DeltaAngle(target, faceYaw);
                Spring.Damp(ref diff, ref faceRate, 0f, 0.3f, dt);
                yaw = faceYaw = target + diff;
            }
            walker.Face(yaw, pitch);
            Vector2 move = Vector2.zero;
            if (go && d.sqrMagnitude > 1e-6f)
            {
                // the way to go in the walker's own frame (the facing may lag the way)
                Vector3 local = Quaternion.Euler(0f, -yaw, 0f) * d.normalized;
                move = new Vector2(local.x, local.z);
            }
            walker.Drive(move, brisk);
        }

        void LateUpdate()
        {
            if (log == null || walker == null)
                return;
            t += Time.deltaTime;
            frame++;
            Vector3 f = walker.Feet;
            bool g = walker.Grounded;
            // a fall: off the ground, landing more than 0.5 m lower
            if (wasGrounded && !g)
                airStart = f.y;
            if (!wasGrounded && g && airStart - f.y > 0.5f)
            {
                falls++;
                evt += (evt.Length > 0 ? "; " : "") + "fall " + N(airStart - f.y, "F2");
            }
            wasGrounded = g;
            // under the walk surface: the surface found from above stands over the feet
            if (walker.mode == Walker.Mode.Walk && g && frame % 8 == 0
                && Physics.Raycast(f + Vector3.up * 2.5f, Vector3.down, out var above, 3f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore)
                && WalkWorld.Of(above.collider) != null && WalkProxy.Walkable(WalkWorld.Of(above.collider).kind) && above.point.y > f.y + 0.3f)
            {
                sunk++;
                evt += (evt.Length > 0 ? "; " : "") + "under " + WalkWorld.Of(above.collider).id;
            }
            if (walker.mode != Walker.Mode.Held)
                physics.Add(walker.PhysicsMicros);
            var s = StreetFrom(f);
            log.WriteLine(string.Join(",", N(t, "F3"), frame.ToString(CultureInfo.InvariantCulture), N(s.x, "F3"), N(s.y, "F3"), N(s.z, "F3"),
                N(walker.Speed, "F3"), g ? "1" : "0", walker.Under != null ? walker.Under.id : "", N(walker.Factor, "F3"), walker.mode.ToString(),
                N(walker.PhysicsMicros, "F1"), evt.Replace(",", ";"), N(walker.SimulateMicros, "F1")));
            evt = "";
            if (captureDir != null)
                ScreenCapture.CaptureScreenshot(Path.Combine(captureDir, "frame-" + frame.ToString("D5", CultureInfo.InvariantCulture) + ".png"));
        }

        static Vector3 StreetFrom(Vector3 u) => new Vector3(u.x, u.z, u.y);

        void Event(string e) => evt += (evt.Length > 0 ? "; " : "") + e;

        void Shot(string name)
        {
            string dir = captureDir ?? Path.GetDirectoryName(Path.GetFullPath(logPath));
            string path = Path.Combine(dir, name + ".png");
            ScreenCapture.CaptureScreenshot(path);
            Event("shot " + path);
        }

        void Fail(string why)
        {
            Debug.LogError("[WalkScript] " + why);
            Finish(why);
        }

        void Finish(string error = null)
        {
            falls += walker.Falls;
            physics.Sort();
            double mean = 0;
            foreach (var p in physics)
                mean += p;
            mean = physics.Count > 0 ? mean / physics.Count : 0;
            double p99 = physics.Count > 0 ? physics[Mathf.Clamp(Mathf.CeilToInt(0.99f * physics.Count) - 1, 0, physics.Count - 1)] : 0;
            double max = physics.Count > 0 ? physics[physics.Count - 1] : 0;
            bool pass = error == null && falls == 0 && sticks == 0 && abandoned == 0 && sunk == 0 && reached == legs;
            string line = "[WalkScript] " + source + ": reached " + reached + " of " + legs + " points in " + N(t, "F1") + " s (" + frame
                        + " frames at " + fps + " fps); falls " + falls + ", sticks " + sticks + ", abandoned " + abandoned + ", under the surface "
                        + sunk + "; walker physics mean " + N(mean, "F0") + " µs, p99 " + N(p99, "F0") + ", max " + N(max, "F0") + "; "
                        + (pass ? "PASS" : "FAIL") + (error != null ? " (" + error + ")" : "");
            Debug.Log(line);
            if (log != null)
            {
                log.WriteLine("# " + line);
                log.Flush();
                log.Dispose();
                log = null;
            }
            if (!stay)
                StartCoroutine(Quit(pass ? 0 : 1));
        }

        IEnumerator Quit(int code)
        {
            yield return null;   // a shot asked for in the last frame is written at its end
            yield return null;
            Application.Quit(code);
        }
    }
}
