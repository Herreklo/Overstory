using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;
using UnityEngine.InputSystem;
using Overstory.Scenes;

namespace Overstory.Play
{
    /// <summary>
    /// The walk (LT1g, the walk, W4): a person's pace through the corner at the eye stop, and a free camera on V.
    ///
    /// Walking (docs/research/play-craft.md, 8, Walk mode): a kinematic CharacterController (built-in physics) 0.3 m round
    /// and 1.8 m tall, stepping 0.25 m, its eye at 1.65 m (the camera study's eye stop) with a 46° lens. 1.4 m/s, 2.2 on
    /// Shift; 0.55 of that up a flight and 0.6 down, weighted by how squarely the walk meets the flight and changing over
    /// about half a second; speed rises to input with a 0.12 s half-life and falls to a stop with 0.08 s (Holden's
    /// spring). No bob. On a flight the feet stand on a ramp through the nosings (WalkWorld), so the eye drops by half a
    /// step's rise over the treads; a step up or down the body takes lifts the eye after it, at most 0.37 m behind (Quake's
    /// rule at our scale); the view leans by half the slope of the ground ahead, a ground line over 2 m looked ahead half a
    /// second (the camera study). A drop edge, the water or the heart's edge is a soft stop: the walk slows over the last
    /// half metre and holds, and slides along it.
    ///
    /// Looking: the mouse, raw, never smoothed, while the cursor is held (a click holds it, Esc lets it go); Q and E turn
    /// and R and F tilt at 60° a second; the tilt keeps to 30° up and 40° down while walking.
    ///
    /// The free camera (V): a 0.4 m sphere that meets every proxy and the roofs, flying where it looks, at a speed that
    /// follows its height (at least 2.2 m/s; Shift 2.5 times, Ctrl 0.3), up and down on PgUp and PgDn or the wheel; it
    /// stays over the water and inside the heart. V again lands it on the open ground below, or the nearest within 12 m.
    ///
    /// The corner's views (PlayKeys: 1 to 9) hold the camera until the walker is asked to move: a movement or turning
    /// key, the wheel or a click takes it from the view where it stands (walking if the view is at eye height over
    /// ground, else flying). The walker sets only the camera's place, turn and lens, and re-aims the light's shafts
    /// (StreetStage.SetShafts); it decides nothing about the world.
    ///
    /// A script (WalkScript) can drive it instead of the keys: Drive and Face each frame, Place to start.
    /// </summary>
    [DefaultExecutionOrder(50)]
    public class Walker : MonoBehaviour
    {
        public enum Mode { Held, Walk, Free }

        [Header("Walking (play-craft.md)")]
        public float eye = 1.65f;
        public float walkSpeed = 1.4f, briskSpeed = 2.2f;
        public float upFlight = 0.55f, downFlight = 0.6f;
        [Tooltip("Half-lives, seconds: speed rising to input, falling to a stop, the flight's share changing.")]
        public float rise = 0.12f, stop = 0.08f, flightChange = 0.15f;
        public float lens = 46f;

        [Header("Body")]
        public float radius = 0.3f, height = 1.8f, stepOffset = 0.25f, slopeLimit = 45f;
        [Tooltip("The eye lags a step the body takes by at most this (Quake: 12 units).")]
        public float stepLag = 0.37f;

        [Header("Looking")]
        public float mouseDegreesPerPixel = 0.08f, keyTurn = 60f;
        public float walkTiltUp = 30f, walkTiltDown = 40f, freeTiltUp = 60f, freeTiltDown = 60f;

        [Header("Edges")]
        [Tooltip("The walk slows over this before a drop edge and holds.")]
        public float edgeSlow = 0.5f;
        [Tooltip("A fall this deep within a probe's 0.15 m is an edge.")]
        public float drop = 0.3f;

        [Header("Free camera")]
        public float flyRadius = 0.4f, flyMinSpeed = 2.2f, flyCeiling = 400f;

        [Header("Scene")]
        public Camera view;
        public PlayCorner corner;
        public WalkWorld world;

        public Mode mode { get; private set; } = Mode.Held;
        /// <summary>The feet walking; the free camera's place flying.</summary>
        public Vector3 Feet => mode == Mode.Free && fly != null ? fly.transform.position : body != null ? body.transform.position : Vector3.zero;
        public float Yaw => yaw;
        public float Speed => new Vector3(vel.x, 0f, vel.z).magnitude;
        public bool Grounded { get; private set; }
        public WalkProxy Under { get; private set; }
        public float Factor => factor;
        /// <summary>The walker's own physics this frame (moves and queries), and the simulation steps since the last, µs.</summary>
        public double PhysicsMicros { get; private set; }
        /// <summary>Of which the simulation steps (Physics.Simulate, the player only), µs.</summary>
        public double SimulateMicros { get; private set; }

        /// <summary>A script steers instead of the keys (WalkScript).</summary>
        public bool Scripted { get; set; }

        CharacterController body, fly;
        float yaw, pitch;               // degrees: about up (Unity's), up positive
        Vector3 vel, acc;               // the spring's velocity and its rate
        float vy;
        float factor = 1f, factorRate;
        float lower, lowerRate;         // the eye over a flight's treads
        float feetY, feetRate;          // the eye's following of the feet
        float lean, leanRate;
        float fov, fovRate;
        bool locked;
        float airborne;
        Vector3 safe;
        float safeAt;
        Vector2 driveMove;              // scripted: x right, y forward of the yaw; length up to 1
        bool driveBrisk;
        float climb;                    // the wheel's height still to rise or fall (free camera)
        double simMicros;
        readonly Stopwatch watch = new Stopwatch();
        readonly Dictionary<Collider, WalkProxy> proxyOf = new Dictionary<Collider, WalkProxy>();

        void Awake()
        {
            if (view == null)
                view = Camera.main;
            body = MakeBody("The walker's body", WalkWorld.BodyLayer, radius, height, stepOffset, WalkWorld.WalkMask);
            body.center = new Vector3(0f, height * 0.5f, 0f);
            fly = MakeBody("The free camera's body", WalkWorld.FlyLayer, flyRadius, flyRadius * 2f, 0f, WalkWorld.WalkMask | WalkWorld.CameraMask);
            fly.center = Vector3.zero;
            // The simulation stepped by hand, so its cost is counted with the walker's own; and only if something in the
            // scene is simulated. The walk's world is static colliders and these two controllers, which move and query
            // without a step (CharacterController.Move is immediate), so a step would only cost (0.14 ms a frame in the
            // A-E-A walk, three times the walker's own queries). The editor keeps its own setting.
            if (!Application.isEditor)
            {
                Physics.simulationMode = SimulationMode.Script;
                simulate = FindObjectsByType<Rigidbody>(FindObjectsSortMode.None).Length > 0;
            }
        }

        bool simulate;

        CharacterController MakeBody(string name, int layer, float r, float h, float step, int meets)
        {
            var go = new GameObject(name) { layer = layer };
            go.transform.SetParent(transform, false);
            var cc = go.AddComponent<CharacterController>();
            cc.radius = r;
            cc.height = h;
            cc.stepOffset = step;
            cc.slopeLimit = slopeLimit;
            cc.skinWidth = 0.03f;
            cc.minMoveDistance = 0f;
            cc.excludeLayers = ~meets;
            cc.enabled = false;
            return cc;
        }

        void FixedUpdate()
        {
            if (!simulate || Application.isEditor || Physics.simulationMode != SimulationMode.Script)
                return;
            watch.Restart();
            Physics.Simulate(Time.fixedDeltaTime);
            simMicros += watch.Elapsed.TotalMilliseconds * 1000.0;
        }

        // -- taking the camera from the views, and handing it back --------------------------------------------------

        bool HeldByViews => corner != null && corner.HoldsCamera;

        /// <summary>Takes the camera where the view left it: walking if it stands at eye height over ground, else flying.</summary>
        public void TakeOver(bool preferFree = false)
        {
            var t = view.transform;
            Vector3 f = t.forward;
            yaw = Mathf.Atan2(f.x, f.z) * Mathf.Rad2Deg;
            pitch = Mathf.Asin(Mathf.Clamp(f.y, -1f, 1f)) * Mathf.Rad2Deg;
            fov = view.fieldOfView;
            fovRate = 0f;
            if (corner != null && corner.HoldsCamera)
                corner.Release();
            if (!preferFree && Physics.Raycast(t.position, Vector3.down, out var hit, eye + 0.65f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore)
                && Walkable(hit.collider) && EnterWalk(hit.point))
                return;
            EnterFree(t.position);
        }

        /// <summary>V: walking to the free camera and back (from a held view, straight to the free camera).</summary>
        public void ToggleFree()
        {
            if (mode == Mode.Held || HeldByViews)
            {
                TakeOver(preferFree: true);
                return;
            }
            if (mode == Mode.Walk)
            {
                EnterFree(view.transform.position);
                return;
            }
            // land on the open ground under the free camera: straight down, else the nearest within 12 m (over a roof, the
            // street beside it); over the water, or with no ground near, it stays flying
            Vector3 p = fly.transform.position;
            bool landed = Land(p);
            for (float r = 1.5f; r <= 12f + 1e-3f && !landed; r += 1.5f)
                for (int i = 0; i < 12 && !landed; i++)
                {
                    float a = (yaw + i * 30f) * Mathf.Deg2Rad;     // (the way it looks first)
                    landed = Land(p + new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * r);
                }
            if (landed)
                pitch = 0f;     // (on its feet, looking ahead: not down at the ground the flight looked at)
        }

        /// <summary>Walks from the first surface under a point, if it is open walk surface (not a roof or a wall, and not the
        /// ground inside a house) over the water's edge and inside the heart, and the body fits there.</summary>
        bool Land(Vector3 p)
        {
            return Physics.Raycast(p, Vector3.down, out var hit, flyCeiling + 50f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore)
                   && Walkable(hit.collider) && hit.point.y > Sea + 0.15f && (world == null || world.InHeart(hit.point, 2f))
                   && EnterWalk(hit.point);
        }

        /// <summary>Starts walking with the feet at a point (Unity space), facing yaw; false if the body does not fit there.</summary>
        public bool Place(Vector3 feet, float faceYaw)
        {
            if (Physics.Raycast(feet + Vector3.up * 1.0f, Vector3.down, out var hit, 3f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                feet = hit.point;
            yaw = faceYaw;
            pitch = 0f;
            fov = lens;
            if (corner != null && corner.HoldsCamera)
                corner.Release();
            return EnterWalk(feet);
        }

        bool EnterWalk(Vector3 feet)
        {
            Vector3 a = feet + Vector3.up * (radius + 0.06f), b = feet + Vector3.up * (height - radius);
            if (Physics.CheckCapsule(a, b, radius - 0.02f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                return false;
            fly.enabled = false;
            body.enabled = false;
            body.transform.position = feet + Vector3.up * 0.02f;
            body.enabled = true;
            Physics.SyncTransforms();
            mode = Mode.Walk;
            vel = acc = Vector3.zero;
            vy = 0f;
            feetY = body.transform.position.y;
            feetRate = lowerRate = leanRate = factorRate = 0f;
            lower = lean = 0f;
            factor = 1f;
            airborne = 0f;
            safe = body.transform.position;
            Grounded = true;
            FrameTimeOverlay.ViewName = "walk";
            Hold(true);
            return true;
        }

        void EnterFree(Vector3 at)
        {
            body.enabled = false;
            fly.enabled = false;
            fly.transform.position = at;
            fly.enabled = true;
            Physics.SyncTransforms();
            mode = Mode.Free;
            vel = acc = Vector3.zero;
            climb = 0f;
            lean = 0f;
            FrameTimeOverlay.ViewName = "free";
            Hold(true);
        }

        void EnterHeld()
        {
            body.enabled = false;
            fly.enabled = false;
            mode = Mode.Held;
            vel = acc = Vector3.zero;
            Hold(false);
        }

        /// <summary>The cursor held for mouse look (never while a script drives).</summary>
        void Hold(bool on)
        {
            if (Scripted || Application.isEditor && !Application.isPlaying)
                return;
            locked = on;
            Cursor.lockState = on ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !on;
        }

        // -- input ------------------------------------------------------------------------------------------------

        /// <summary>A script's steering this frame: move (x right, y forward of the facing, length up to 1), and pace.</summary>
        public void Drive(Vector2 move, bool brisk)
        {
            driveMove = Vector2.ClampMagnitude(move, 1f);
            driveBrisk = brisk;
        }

        /// <summary>A script's facing (degrees: yaw about up, pitch up positive).</summary>
        public void Face(float faceYaw, float facePitch)
        {
            yaw = faceYaw;
            pitch = facePitch;
        }

        static float Down(Keyboard k, Key a) => k[a].isPressed ? 1f : 0f;

        bool WantsToMove(Keyboard k, Mouse m)
        {
            if (k != null && (k.wKey.isPressed || k.aKey.isPressed || k.sKey.isPressed || k.dKey.isPressed || k.upArrowKey.isPressed
                || k.downArrowKey.isPressed || k.leftArrowKey.isPressed || k.rightArrowKey.isPressed || k.qKey.isPressed || k.eKey.isPressed
                || k.rKey.isPressed || k.fKey.isPressed || k.pageUpKey.isPressed || k.pageDownKey.isPressed))
                return true;
            return m != null && (m.leftButton.wasPressedThisFrame || Mathf.Abs(m.scroll.ReadValue().y) > 0.01f);
        }

        void Look(Keyboard k, Mouse m, float dt, float up, float down)
        {
            if (!Scripted)
            {
                if (m != null && locked)
                {
                    Vector2 d = m.delta.ReadValue();
                    yaw += d.x * mouseDegreesPerPixel;
                    pitch += d.y * mouseDegreesPerPixel;
                }
                if (k != null)
                {
                    float scale = keyTurn * (view != null ? view.fieldOfView / 46f : 1f);   // turning scaled to the lens
                    yaw += (Down(k, Key.E) - Down(k, Key.Q)) * scale * dt;
                    pitch += (Down(k, Key.R) - Down(k, Key.F)) * scale * dt;
                }
            }
            yaw = Mathf.Repeat(yaw + 180f, 360f) - 180f;
            pitch = Mathf.Clamp(pitch, -down, up);
        }

        Vector2 MoveKeys(Keyboard k)
        {
            if (Scripted)
                return driveMove;
            if (k == null)
                return Vector2.zero;
            var v = new Vector2(Mathf.Max(Down(k, Key.D), Down(k, Key.RightArrow))
                              - Mathf.Max(Down(k, Key.A), Down(k, Key.LeftArrow)),
                                Mathf.Max(Down(k, Key.W), Down(k, Key.UpArrow))
                              - Mathf.Max(Down(k, Key.S), Down(k, Key.DownArrow)));
            return Vector2.ClampMagnitude(v, 1f);
        }

        // -- each frame -------------------------------------------------------------------------------------------

        void Update()
        {
            float dt = Time.deltaTime;
            if (dt <= 0f || view == null)
                return;
            var k = Keyboard.current;
            var m = Mouse.current;

            if (HeldByViews)
            {
                if (mode != Mode.Held)
                    EnterHeld();
                if (Scripted || !WantsToMove(k, m))
                {
                    PhysicsMicros = SimulateMicros = simMicros;
                    simMicros = 0;
                    return;
                }
                TakeOver();
            }
            if (!Scripted && k != null && k.escapeKey.wasPressedThisFrame)
                Hold(false);
            else if (!Scripted && !locked && m != null && m.leftButton.wasPressedThisFrame)
                Hold(true);

            watch.Restart();
            if (mode == Mode.Walk)
                WalkStep(k, dt);
            else if (mode == Mode.Free)
                FreeStep(k, m, dt);
            PhysicsMicros = watch.Elapsed.TotalMilliseconds * 1000.0 + simMicros;
            SimulateMicros = simMicros;
            simMicros = 0;

            if (corner != null && corner.stage != null)
                corner.stage.SetShafts();
        }

        float Sea => world != null ? world.Sea : -0.2f;

        bool Walkable(Collider c)
        {
            var p = Proxy(c);
            return p != null && WalkProxy.Walkable(p.kind);
        }

        WalkProxy Proxy(Collider c)
        {
            if (c == null)
                return null;
            if (!proxyOf.TryGetValue(c, out var p))
                proxyOf[c] = p = c.GetComponent<WalkProxy>();
            return p;
        }

        void WalkStep(Keyboard k, float dt)
        {
            Look(k, Mouse.current, dt, walkTiltUp, walkTiltDown);
            var turn = Quaternion.Euler(0f, yaw, 0f);
            Vector3 fwd = turn * Vector3.forward, right = turn * Vector3.right;
            Vector2 move = MoveKeys(k);
            bool brisk = Scripted ? driveBrisk : k != null && (k.leftShiftKey.isPressed || k.rightShiftKey.isPressed);
            Vector3 wish = fwd * move.y + right * move.x;
            Vector3 feet = body.transform.position;

            // the ground under the feet: what it is, and its slope along the way the walk goes
            Under = null;
            float slopeFactor = 1f;
            if (Physics.Raycast(feet + Vector3.up * 0.3f, Vector3.down, out var under, 1.0f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
            {
                Under = Proxy(under.collider);
                Vector3 heading = wish.sqrMagnitude > 1e-4f ? wish.normalized : (vel.sqrMagnitude > 1e-4f ? new Vector3(vel.x, 0f, vel.z).normalized : Vector3.zero);
                Vector3 n = under.normal;
                var nh = new Vector3(n.x, 0f, n.z);
                float steep = n.y > 0.1f ? nh.magnitude / n.y : 0f;
                if (steep > 1e-3f && heading != Vector3.zero)
                {
                    float along = -Vector3.Dot(heading, nh / nh.magnitude);   // + up the slope
                    float w = Mathf.Clamp01((steep - 0.25f) / 0.15f);           // flights and stepped ways, not a street's camber
                    float f = along > 0f ? Mathf.Lerp(1f, upFlight, along) : Mathf.Lerp(1f, downFlight, -along);
                    slopeFactor = Mathf.Lerp(1f, f, w);
                }
            }
            Spring.Damp(ref factor, ref factorRate, slopeFactor, flightChange, dt);

            Vector3 goal = wish * ((brisk ? briskSpeed : walkSpeed) * factor);
            Spring.Damp(ref vel, ref acc, goal, goal.sqrMagnitude >= vel.sqrMagnitude ? rise : stop, dt);
            vel.y = 0f;
            vel = Guard(feet, vel);

            // move: the body slides along walls and steps up to 0.25 m; gravity holds it to the ground
            bool was = body.isGrounded;
            vy = was ? -1f : Mathf.Max(vy - 9.81f * dt, -30f);
            var flags = body.Move(vel * dt + Vector3.up * (vy * dt));
            if (was && !body.isGrounded && vy <= 0f
                && Physics.SphereCast(body.transform.position + Vector3.up * (radius + 0.05f), radius - 0.02f, Vector3.down, out var snap,
                                      stepOffset + 0.1f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                body.Move(Vector3.down * snap.distance);   // down a step without a fall (the body stops on the ground it meets)
            Grounded = body.isGrounded;
            feet = body.transform.position;
            if (Grounded)
            {
                airborne = 0f;
                if (Time.time - safeAt > 0.5f && Under != null && WalkProxy.Walkable(Under.kind))
                {
                    safe = feet;
                    safeAt = Time.time;
                }
            }
            else if ((airborne += dt) > 2f || feet.y < Sea - 5f)
            {
                // fell through or off: back to where it last stood (a script counts this as a fall)
                Falls++;
                EnterWalk(safe);
                feet = body.transform.position;
            }
            // (velocity stays what the walk asked for: against a wall the body slides, and a script sees it stick by its
            // own measure, the distance it covers)
            Moved = flags;

            // the eye: over the treads on a ramp, after the body's steps, leaning with the ground ahead
            float lowerGoal = 0f;
            if (Under != null && Under.IsRamp)
            {
                float s = Under.Along(feet);
                lowerGoal = Under.rise * 0.5f * Mathf.Clamp01(Mathf.Min(s, Under.length - s) / 0.6f);
            }
            Spring.Damp(ref lower, ref lowerRate, lowerGoal, 0.15f, dt);
            Spring.Damp(ref feetY, ref feetRate, feet.y, 0.08f, dt);
            if (feetY < feet.y - stepLag) { feetY = feet.y - stepLag; feetRate = Mathf.Max(feetRate, 0f); }
            if (feetY > feet.y + stepLag) { feetY = feet.y + stepLag; feetRate = Mathf.Min(feetRate, 0f); }
            Spring.Damp(ref lean, ref leanRate, LeanGoal(feet, fwd), 0.25f, dt);
            Spring.Damp(ref fov, ref fovRate, lens, 0.25f, dt);

            view.transform.SetPositionAndRotation(new Vector3(feet.x, feetY + eye - lower, feet.z), Quaternion.Euler(-(pitch + lean), yaw, 0f));
            view.fieldOfView = fov;
        }

        /// <summary>How often the walker was put back after a fall (WalkScript counts falls by it too).</summary>
        public int Falls { get; private set; }
        public CollisionFlags Moved { get; private set; }

        /// <summary>Half the slope of the ground ahead along the facing: a 2 m line looked ahead half a second (degrees, up positive).</summary>
        float LeanGoal(Vector3 feet, Vector3 fwd)
        {
            float ahead = Mathf.Max(0f, Vector3.Dot(vel, fwd)) * 0.5f;
            float a = Ground(feet + fwd * (ahead + 1f), feet.y), b = Ground(feet + fwd * (ahead - 1f), feet.y);
            if (float.IsNaN(a) || float.IsNaN(b))
                return 0f;
            float slope = Mathf.Atan2(a - b, 2f) * Mathf.Rad2Deg;
            return 0.5f * Mathf.Clamp(slope, -35f, 35f);
        }

        /// <summary>The walk surface's height at a point near a reference height (NaN where there is none).</summary>
        float Ground(Vector3 p, float near)
        {
            if (Physics.Raycast(new Vector3(p.x, near + 1.5f, p.z), Vector3.down, out var hit, 3.5f, WalkWorld.WalkMask, QueryTriggerInteraction.Ignore)
                && Walkable(hit.collider))
                return hit.point.y;
            return float.NaN;
        }

        /// <summary>
        /// The soft stop: the walk slows over the last half metre before a drop edge, the water or the heart's edge, and
        /// holds; turned towards the edge it slides along it (the nearest direction within 80° that is clear).
        /// </summary>
        Vector3 Guard(Vector3 feet, Vector3 v)
        {
            float sp = v.magnitude;
            if (sp < 1e-4f)
                return v;
            Vector3 dir = v / sp;
            float k = Allowed(feet, dir);
            if (k >= 1f)
                return v;
            float best = sp * k;
            Vector3 bestDir = dir;
            for (int i = 1; i <= 4; i++)
            {
                for (int side = -1; side <= 1; side += 2)
                {
                    float ang = 20f * i * side;
                    float c = Mathf.Cos(ang * Mathf.Deg2Rad);
                    if (sp * c <= best)
                        continue;
                    Vector3 d = Quaternion.Euler(0f, ang, 0f) * dir;
                    float s = sp * c * Allowed(feet, d);
                    if (s > best)
                    {
                        best = s;
                        bestDir = d;
                    }
                }
            }
            return bestDir * best;
        }

        /// <summary>The share of speed allowed along dir: 1 clear, falling to 0 over edgeSlow before an edge.</summary>
        float Allowed(Vector3 feet, Vector3 dir)
        {
            float clear = Clearance(feet, dir);
            return Mathf.Clamp01((clear - radius - 0.05f) / edgeSlow);
        }

        /// <summary>How far along dir the walk surface carries on without a drop, the water or the heart's edge.</summary>
        float Clearance(Vector3 feet, Vector3 dir)
        {
            const float step = 0.15f;
            float reach = radius + 0.05f + edgeSlow + step;
            float prev = feet.y;
            for (float d = step; d <= reach + 1e-3f; d += step)
            {
                Vector3 p = feet + dir * d;
                if (world != null && !world.InHeart(p, 2f))
                    return d;
                if (!Physics.Raycast(new Vector3(p.x, prev + stepOffset + 0.6f, p.z), Vector3.down, out var hit, stepOffset + 0.6f + drop + 1.0f,
                                     WalkWorld.WalkMask, QueryTriggerInteraction.Ignore))
                    return d;                                   // nothing under it within a fall's reach
                float y = hit.point.y;
                if (y > prev + stepOffset)
                    continue;                                   // a rise: the body's own collision meets it
                if (y < prev - drop || y < Sea + 0.15f)
                    return d;                                   // a drop, or the water
                prev = y;
            }
            return float.MaxValue;
        }

        void FreeStep(Keyboard k, Mouse m, float dt)
        {
            Look(k, Scripted ? null : m, dt, freeTiltUp, freeTiltDown);
            var rot = Quaternion.Euler(-pitch, yaw, 0f);
            Vector2 move = MoveKeys(k);
            Vector3 p = fly.transform.position;
            float over = p.y - Sea;
            if (Physics.Raycast(p, Vector3.down, out var hit, 1000f, WalkWorld.WalkMask | WalkWorld.CameraMask, QueryTriggerInteraction.Ignore))
                over = hit.distance;
            float upDown = 0f;
            if (!Scripted)
            {
                if (k != null)
                    upDown = Down(k, Key.PageUp) - Down(k, Key.PageDown);
                if (m != null)
                {
                    // a wheel's notch (120, or 1 where the input system scales it) climbs a fifth of the height, at least 1 m
                    float s = m.scroll.ReadValue().y;
                    float notches = Mathf.Abs(s) >= 10f ? s / 120f : s;
                    climb += notches * Mathf.Max(1f, over * 0.2f);
                }
            }
            float dz = climb * (1f - Mathf.Exp(-dt * 8f));
            climb -= dz;
            float speed = Mathf.Max(flyMinSpeed, over);
            if (!Scripted && k != null)
            {
                if (k.leftShiftKey.isPressed || k.rightShiftKey.isPressed) speed *= 2.5f;
                if (k.leftCtrlKey.isPressed || k.rightCtrlKey.isPressed) speed *= 0.3f;
            }
            Vector3 goal = (rot * new Vector3(move.x, 0f, move.y) + Vector3.up * upDown) * speed;
            Spring.Damp(ref vel, ref acc, goal, goal.sqrMagnitude >= vel.sqrMagnitude ? rise : stop, dt);
            fly.Move(vel * dt + Vector3.up * dz);
            // over the water, under the ceiling, inside the heart
            p = fly.transform.position;
            Vector3 q = p;
            q.y = Mathf.Clamp(q.y, Sea + 0.6f, flyCeiling);
            if (world != null)
            {
                var h = world.Heart;
                q.x = Mathf.Clamp(q.x, h.xMin + 2f, h.xMax - 2f);
                q.z = Mathf.Clamp(q.z, h.yMin + 2f, h.yMax - 2f);
            }
            if (q != p)
            {
                fly.enabled = false;
                fly.transform.position = q;
                fly.enabled = true;
            }
            Spring.Damp(ref fov, ref fovRate, lens, 0.25f, dt);
            view.transform.SetPositionAndRotation(fly.transform.position, rot);
            view.fieldOfView = fov;
        }
    }
}
