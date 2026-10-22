using UnityEngine;

namespace Overstory.Play
{
    /// <summary>
    /// One collision proxy of the walk (WalkWorld builds them): the record it stands for and its kind, so a ray or a
    /// foot can say what it touched (docs/research/collision-and-navigation.md, item 4: a record id on every proxy).
    /// A ramp over a flight also says which way is up it and how high its steps are, for the walker's pace on a flight
    /// and its eye over the treads.
    /// </summary>
    public class WalkProxy : MonoBehaviour
    {
        /// <summary>The kinds a walker walks on; the rest stop it (house, wall, cheek, blocker) or only the camera (roof).</summary>
        public static bool Walkable(string kind) => kind == "ground" || kind == "ramp" || kind == "landing" || kind == "stoop";

        /// <summary>The kinds that may not stand in a door or a way (CheckProxies).</summary>
        public static bool Blocks(string kind) => kind == "house" || kind == "wall" || kind == "cheek" || kind == "blocker";

        [Tooltip("The record or thing it stands for: bld/104, st-gully/fl-0/run-1, heart/ground/0_1 ...")]
        public string id;
        [Tooltip("ground, ramp, landing, stoop, house, roof, wall, cheek or blocker.")]
        public string kind;
        [Tooltip("A ramp's flight (st-gully/fl-0), or a landing's.")]
        public string flight;

        [Header("A ramp (Unity space)")]
        [Tooltip("The foot of the ramp's top line.")]
        public Vector3 start;
        [Tooltip("Up the flight, level (unit).")]
        public Vector3 up;
        [Tooltip("The ramp's length in plan, metres.")]
        public float length;
        [Tooltip("Its steps' rise, metres: a foot on the ramp stands this much over the treads at a riser's foot.")]
        public float rise;

        public bool IsRamp => kind == "ramp";

        /// <summary>How far along the ramp, in plan, a point is (0 at its foot, length at its top).</summary>
        public float Along(Vector3 p) => Vector3.Dot(new Vector3(p.x - start.x, 0f, p.z - start.z), up);
    }
}
