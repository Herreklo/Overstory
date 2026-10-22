using UnityEngine;

namespace Overstory.Play
{
    /// <summary>
    /// Daniel Holden's critically damped spring, set by a half-life: exact at any frame rate and continuous in velocity
    /// (docs/research/play-craft.md, Speed, acceleration and stopping: every smoothing uses it).
    /// </summary>
    public static class Spring
    {
        const float Ln2x2 = 1.3862944f;   // 2 ln 2: the damping y over a half-life is 2 ln 2 / half-life

        public static void Damp(ref float x, ref float v, float goal, float halfLife, float dt)
        {
            float y = Ln2x2 / Mathf.Max(halfLife, 1e-4f);
            float j0 = x - goal;
            float j1 = v + j0 * y;
            float e = Mathf.Exp(-y * dt);
            x = e * (j0 + j1 * dt) + goal;
            v = e * (v - j1 * y * dt);
        }

        public static void Damp(ref Vector3 x, ref Vector3 v, Vector3 goal, float halfLife, float dt)
        {
            float y = Ln2x2 / Mathf.Max(halfLife, 1e-4f);
            Vector3 j0 = x - goal;
            Vector3 j1 = v + j0 * y;
            float e = Mathf.Exp(-y * dt);
            x = e * (j0 + j1 * dt) + goal;
            v = e * (v - j1 * (y * dt));
        }
    }
}
