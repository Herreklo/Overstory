namespace Overstory.Core
{
    /// <summary>
    /// The project's one hash spec, the twin of Python's blender/resolver/hashing.py (docs/building-blocks.md, Seeds and
    /// determinism). Every visible choice that is not a fact (a sett's height, a stone's length) is seeded from stable ids
    /// through this, never from UnityEngine.Random or System.Random, so the same world and seed give the same picture on
    /// every Unity and .NET version, in C# as in Python. Both reproduce fixtures/golden/hash-vectors.json
    /// (HashVectors.Check in the editor; blender/resolver/hash_vectors.py in Python).
    ///
    /// The spec: FNV-1a 64 over a string's UTF-8 bytes; a key folds its parts from <see cref="Start"/>, each as
    /// acc = Mix(acc ^ part) (an integer as its 64-bit two's complement, a string as its FNV-1a); Mix is SplitMix64's
    /// step and finaliser; <see cref="Unit"/> = (h &gt;&gt; 11) / 2^53. So Of(a, "kerb") is Python's h(a, "kerb").
    /// </summary>
    public static class Hash
    {
        /// <summary>The fold's start: h() of no parts.</summary>
        public const ulong Start = 0x2545F4914F6CDD1DUL;

        /// <summary>SplitMix64's increment, its step through a stream.</summary>
        public const ulong Gamma = 0x9E3779B97F4A7C15UL;

        /// <summary>SplitMix64: one step (+ Gamma) and its finaliser.</summary>
        public static ulong Mix(ulong z)
        {
            unchecked
            {
                z += Gamma;
                z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
                z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
                return z ^ (z >> 31);
            }
        }

        /// <summary>64-bit FNV-1a over the string's UTF-8 bytes (a lone surrogate as U+FFFD, as .NET encodes it).</summary>
        public static ulong Fnv1a(string s)
        {
            unchecked
            {
                ulong h = 0xCBF29CE484222325UL;
                void Byte(int b)
                {
                    h ^= (byte)b;
                    h *= 0x100000001B3UL;
                }
                for (int i = 0; i < s.Length; i++)
                {
                    int c = s[i];
                    if (c >= 0xD800 && c <= 0xDBFF && i + 1 < s.Length && s[i + 1] >= 0xDC00 && s[i + 1] <= 0xDFFF)
                        c = 0x10000 + ((c - 0xD800) << 10) + (s[++i] - 0xDC00);
                    else if (c >= 0xD800 && c <= 0xDFFF)
                        c = 0xFFFD;
                    if (c < 0x80)
                        Byte(c);
                    else if (c < 0x800)
                    {
                        Byte(0xC0 | (c >> 6));
                        Byte(0x80 | (c & 0x3F));
                    }
                    else if (c < 0x10000)
                    {
                        Byte(0xE0 | (c >> 12));
                        Byte(0x80 | ((c >> 6) & 0x3F));
                        Byte(0x80 | (c & 0x3F));
                    }
                    else
                    {
                        Byte(0xF0 | (c >> 18));
                        Byte(0x80 | ((c >> 12) & 0x3F));
                        Byte(0x80 | ((c >> 6) & 0x3F));
                        Byte(0x80 | (c & 0x3F));
                    }
                }
                return h;
            }
        }

        /// <summary>One more part folded into a key: acc = Mix(acc ^ part).</summary>
        public static ulong Then(ulong acc, ulong part) => Mix(acc ^ part);

        /// <summary>One more string part folded into a key.</summary>
        public static ulong Then(ulong acc, string part) => Mix(acc ^ Fnv1a(part));

        public static ulong Of(ulong a) => Then(Start, a);
        public static ulong Of(string a) => Then(Start, a);
        public static ulong Of(ulong a, ulong b) => Then(Of(a), b);
        public static ulong Of(ulong a, string b) => Then(Of(a), b);
        public static ulong Of(string a, ulong b) => Then(Of(a), b);
        public static ulong Of(string a, string b) => Then(Of(a), b);
        public static ulong Of(ulong a, ulong b, ulong c) => Then(Of(a, b), c);
        public static ulong Of(ulong a, string b, ulong c) => Then(Of(a, b), c);
        public static ulong Of(ulong a, ulong b, string c) => Then(Of(a, b), c);
        public static ulong Of(ulong a, string b, string c) => Then(Of(a, b), c);
        public static ulong Of(ulong a, ulong b, ulong c, ulong d) => Then(Of(a, b, c), d);

        /// <summary>A uniform value in [0, 1) from a hash: (h &gt;&gt; 11) / 2^53, Python's unit().</summary>
        public static double Unit(ulong h) => (h >> 11) * (1.0 / 9007199254740992.0);

        /// <summary>A uniform value in [lo, hi) from a hash: lo + (hi - lo) * Unit, in double, as Python's uniform().</summary>
        public static float Range(ulong h, float lo, float hi) => (float)(lo + ((double)hi - lo) * Unit(h));

        /// <summary>A whole number in [0, n) from a hash: h mod n, Python's pick().</summary>
        public static int Index(ulong h, int n) => (int)(h % (ulong)n);

        /// <summary>A whole number in [lo, hi] from a hash: lo + h mod (hi - lo + 1), Python's between().</summary>
        public static long Between(ulong h, long lo, long hi) => lo + (long)(h % (ulong)(hi - lo + 1));

        /// <summary>A signed integer as a hash input (its 64-bit two's complement, as Python's).</summary>
        public static ulong Key(int i) => unchecked((ulong)(long)i);

        /// <summary>A signed integer as a hash input (its 64-bit two's complement, as Python's).</summary>
        public static ulong Key(long i) => unchecked((ulong)i);

        /// <summary>
        /// A SplitMix64 sequence from a key, Python's hashing.Stream: draw n is Mix(key + n * Gamma). For the many draws
        /// one judged part function makes from its own seed, in a fixed order; a choice that must not move when others
        /// are added takes its own key instead.
        /// </summary>
        public struct Stream
        {
            ulong state;

            public Stream(ulong key) => state = key;

            /// <summary>The next 64-bit draw.</summary>
            public ulong Next()
            {
                ulong v = Mix(state);
                unchecked { state += Gamma; }
                return v;
            }

            /// <summary>The next draw in [0, 1).</summary>
            public double Unit() => Hash.Unit(Next());

            /// <summary>The next draw in [lo, hi).</summary>
            public float Range(float lo, float hi) => Hash.Range(Next(), lo, hi);

            /// <summary>The next whole number in [lo, hi].</summary>
            public long Between(long lo, long hi) => Hash.Between(Next(), lo, hi);

            /// <summary>The next whole number in [0, n).</summary>
            public int Index(int n) => Hash.Index(Next(), n);

            /// <summary>A normal draw by Irwin and Hall: twelve units less six, summed in order as Python sums them.</summary>
            public double Normal(double mu = 0.0, double sigma = 1.0)
            {
                double s = 0.0;
                for (int i = 0; i < 12; i++)
                    s += Unit();
                return mu + sigma * (s - 6.0);
            }
        }
    }
}
