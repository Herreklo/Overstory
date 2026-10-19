namespace Overstory.Core
{
    /// <summary>
    /// The project's own hash. Every visible choice that is not a fact (a sett's height, a stone's
    /// length) is seeded from stable ids through this, never from UnityEngine.Random or
    /// System.Random, so the same world and seed give the same picture on every Unity and .NET version.
    /// </summary>
    public static class Hash
    {
        /// <summary>SplitMix64's finaliser: a well-mixed 64-bit value from any 64-bit input.</summary>
        public static ulong Mix(ulong z)
        {
            z += 0x9E3779B97F4A7C15UL;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            return z ^ (z >> 31);
        }

        public static ulong Of(ulong a, ulong b) => Mix(Mix(a) ^ b);
        public static ulong Of(ulong a, ulong b, ulong c) => Mix(Of(a, b) ^ c);
        public static ulong Of(ulong a, ulong b, ulong c, ulong d) => Mix(Of(a, b, c) ^ d);

        /// <summary>A stable number for a name (FNV-1a over its UTF-16 code units).</summary>
        public static ulong Of(string s)
        {
            ulong h = 14695981039346656037UL;
            foreach (char ch in s)
            {
                h ^= ch;
                h *= 1099511628211UL;
            }
            return Mix(h);
        }

        public static ulong Of(ulong a, string s) => Of(a, Of(s));

        /// <summary>A uniform value in [0, 1) from a hash.</summary>
        public static float Unit(ulong h) => (h >> 40) * (1f / (1 << 24));

        /// <summary>A uniform value in [lo, hi) from a hash.</summary>
        public static float Range(ulong h, float lo, float hi) => lo + (hi - lo) * Unit(h);

        /// <summary>A whole number in [0, n) from a hash.</summary>
        public static int Index(ulong h, int n) => (int)((h >> 33) % (ulong)n);

        /// <summary>A signed integer coordinate as a hash input.</summary>
        public static ulong Key(int i) => unchecked((ulong)(long)i);
    }
}
