using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// R2a's face patches (SN6; reviews/lt1/port/2b/r2a/stones/plan.md, The patch array) as one Texture2DArray, built in
    /// memory at each run from the patches' own maps and manifest (blender/parts/stone/slate/patches.manifest.json),
    /// never imported and never saved.
    ///
    /// Why in memory: the importer has no way to make a 14-slice array from 28 PNGs with these mips (a normal map's
    /// mips renormalised by the importer would lose the shortening the gloss filter reads), an asset in Generated/
    /// would be one more binary to rebuild and a .meta to keep in step, and reading the PNGs each run checks every
    /// slice against the manifest's pixel hash, so a stale or half-written map can never be drawn. It costs a few
    /// seconds a run.
    ///
    /// The slices, in the contract's order: split-0..3 and bed-0..1 as built (0 to 5: the mesh's own slice numbers),
    /// then the arms in the manifest's order (facets x2 on split-0..3, 6 to 9; the minor ledges off, 10 to 13). An arm
    /// is judged by a shift added to a face's slice (Stone.shader's _OS_PatchShift), so the mesh never changes.
    ///
    /// The format: RGBAHalf (16-bit float), xyz the tangent-space normal, w the face value's multiplier, linear, with a
    /// full mip chain made here. The maps are 16-bit because the patches' slopes are shallow (a facet's 1.6 to 1.8 mm
    /// over 80 to 150 mm, about 1 degree): 8 bits a channel steps a normal by 2/255, about 0.45 degrees, two or three
    /// steps across a facet, which bands in low sun. Half keeps 11 bits near 1 and finer near 0 (a normal's x and y),
    /// about 0.03 degrees, and the value multiplier (0.75 to 1.25) to 1/2048, under 0.1 L*. 16-bit unorm would do as
    /// well at the same size; half is chosen because a normal's x and y sit near 0, where half is finest. The height map
    /// is not uploaded: no term in Stone.shader reads it (the relief is the normal map, which patches.py made from the
    /// height); its consumer would be a parallax or a lit-line-on-relief term, neither in R2a. The cost is 8 bytes a
    /// texel: 14 slices with mips are 149 MB of GPU memory, the 6 a town needs 64 MB. That is a judging format, not the
    /// game's: a compressed pair (BC5 for the normal's x and y, BC4 for the value) would be 16 MB for the 6, but BC5
    /// drops the averaged normal's length the gloss filter reads, so the game's format has to carry that variance in
    /// another channel. Named for the texture budget (building-blocks, Budgets), not R2a's to decide.
    ///
    /// The mips: each level the 2 x 2 box average of the one below (the average of every full-size texel it covers, as
    /// a box of boxes is), the normal's xyz left unnormalised, so its length is the averaged normals' coherence (Stone.
    /// shader's TextureNormalVariance, Toksvig as The Order: 1886 uses it), and the value averaged to its mean; the last
    /// mip (1 x 1) is the patch's mean, which OS_Near takes relief and value to.
    /// </summary>
    public static class R2aPatches
    {
        public const string Manifest = "blender/parts/stone/slate/patches.manifest.json";

        /// <summary>What was built: the array, patches a metre, the slice shift for each arm (by name), and a log.</summary>
        public class Built
        {
            public Texture2DArray map;
            public float perMetre;
            public string[] slices;
            public Dictionary<string, float[]> shifts = new Dictionary<string, float[]>();
            public float valueBase, valueSpan;
            public readonly StringBuilder log = new StringBuilder();
        }

        static readonly string[] AsBuilt = { "split-0", "split-1", "split-2", "split-3", "bed-0", "bed-1" };

        public static Built Build(string repo)
        {
            var clock = System.Diagnostics.Stopwatch.StartNew();
            string manifestPath = Path.Combine(repo, Manifest);
            var m = (Dictionary<string, object>)Json.Parse(File.ReadAllText(manifestPath));
            var built = new Built();
            int texels = Convert.ToInt32(m["texels"], CultureInfo.InvariantCulture);
            double mmPerTexel = Convert.ToDouble(m["mmPerTexel"], CultureInfo.InvariantCulture);
            built.perMetre = (float)(1000.0 / (texels * mmPerTexel));

            // the encoding, read from the manifest's words: a changed format stops the run rather than being misread
            var enc = (Dictionary<string, object>)m["encoding"];
            string normalEnc = (string)enc["normal"], valueEnc = (string)enc["value"];
            if (!normalEnc.Contains("16-bit RGB") || !normalEnc.Contains("green up") || !normalEnc.Contains("n = 2 v / 65535 - 1"))
                throw new InvalidDataException($"the patches' normal encoding is not the one this reader knows: \"{normalEnc}\"");
            var vm = Regex.Match(valueEnc, @"^16-bit grey: the face value's multiplier = ([0-9.]+) \+ ([0-9.]+) \* v / 65535$");
            if (!vm.Success)
                throw new InvalidDataException($"the patches' value encoding is not the one this reader knows: \"{valueEnc}\"");
            built.valueBase = float.Parse(vm.Groups[1].Value, CultureInfo.InvariantCulture);
            built.valueSpan = float.Parse(vm.Groups[2].Value, CultureInfo.InvariantCulture);

            // the slices: the six as built in the contract's order, then the arms in the manifest's
            var patches = (Dictionary<string, object>)m["patches"];
            var arms = m.ContainsKey("arms") ? (OrderedDict)m["arms"] : new OrderedDict();
            var names = new List<string>();
            var entries = new List<Dictionary<string, object>>();
            foreach (var name in AsBuilt)
            {
                if (!patches.ContainsKey(name))
                    throw new InvalidDataException($"the manifest has no patch '{name}'");
                names.Add(name);
                entries.Add((Dictionary<string, object>)patches[name]);
            }
            if (patches.Count != AsBuilt.Length)
                throw new InvalidDataException($"the manifest has {patches.Count} patches; the contract's slices are {AsBuilt.Length}");
            var armOrder = new List<string>();
            foreach (var key in arms.Order)
            {
                var kv = new KeyValuePair<string, object>(key, arms[key]);
                var a = (Dictionary<string, object>)kv.Value;
                string arm = (string)a["arm"], id = (string)a["id"];
                string baseName = id.Substring(id.LastIndexOf('/') + 1);
                int baseSlice = Array.IndexOf(AsBuilt, baseName);
                if (baseSlice < 0 || kv.Key != $"{baseName}-{arm}")
                    throw new InvalidDataException($"the arm '{kv.Key}' names no as-built patch ({id})");
                if (!armOrder.Contains(arm))
                    armOrder.Add(arm);
                if (!built.shifts.ContainsKey(arm))
                    built.shifts[arm] = new float[8];
                built.shifts[arm][baseSlice] = names.Count - baseSlice;
                names.Add(kv.Key);
                entries.Add(a);
            }
            built.shifts["as-built"] = new float[8];
            built.slices = names.ToArray();
            if (names.Count > 32)
                throw new InvalidDataException("too many slices");

            int levels = 1 + (int)Math.Floor(Math.Log(texels, 2));
            var map = new Texture2DArray(texels, texels, names.Count, TextureFormat.RGBAHalf, true, true)
            {
                name = "R2a patches",
                hideFlags = HideFlags.DontSave,
                filterMode = FilterMode.Trilinear,
                anisoLevel = 8,                // (the grain map's sampling, which the patches replace: trilinear, 8x)
                wrapMode = TextureWrapMode.Repeat,  // (the patches are seamless)
            };
            built.log.AppendLine($"patch array: {names.Count} slices {texels} x {texels}, RGBAHalf, {levels} mips, " +
                                 $"{built.perMetre:R} patches a metre ({texels} texels at {mmPerTexel} mm), value = " +
                                 $"{built.valueBase} + {built.valueSpan} v");
            for (int s = 0; s < names.Count; s++)
            {
                var files = (Dictionary<string, object>)entries[s]["files"];
                var nf = (Dictionary<string, object>)files["normal"];
                var vf = (Dictionary<string, object>)files["value"];
                var (nw, nh, nc, nRaw) = ReadChecked(repo, nf);
                var (vw, vh, vc, vRaw) = ReadChecked(repo, vf);
                if (nw != texels || nh != texels || nc != 3 || vw != texels || vh != texels || vc != 1)
                    throw new InvalidDataException($"{names[s]}: the maps are not {texels} x {texels} RGB and grey");

                // level 0: rows flipped (the PNG's rows run top first; a texture's bottom first, v up the image)
                var level = new float[texels * texels * 4];
                double meanLen = 0;
                for (int y = 0; y < texels; y++)
                {
                    int src = (texels - 1 - y) * texels, dst = y * texels;
                    for (int x = 0; x < texels; x++)
                    {
                        int i = src + x, o = (dst + x) * 4;
                        float nx = 2f * U16(nRaw, i * 3) / 65535f - 1f;
                        float ny = 2f * U16(nRaw, i * 3 + 1) / 65535f - 1f;
                        float nz = 2f * U16(nRaw, i * 3 + 2) / 65535f - 1f;
                        float len = Mathf.Sqrt(nx * nx + ny * ny + nz * nz);
                        meanLen += len;
                        // (patches.py's decode normalises: the 16-bit rounding leaves a length a few 1e-5 off 1)
                        level[o] = nx / len;
                        level[o + 1] = ny / len;
                        level[o + 2] = nz / len;
                        level[o + 3] = built.valueBase + built.valueSpan * U16(vRaw, i) / 65535f;
                    }
                }
                int size = texels;
                for (int mip = 0; mip < levels; mip++)
                {
                    var half = new ushort[size * size * 4];
                    for (int i = 0; i < half.Length; i++)
                        half[i] = Mathf.FloatToHalf(level[i]);
                    map.SetPixelData(half, mip, s);
                    if (mip == levels - 1)
                    {
                        float len = Mathf.Sqrt(level[0] * level[0] + level[1] * level[1] + level[2] * level[2]);
                        built.log.Append("  ").Append(s.ToString().PadLeft(2)).Append(' ').Append(names[s].PadRight(18))
                            .Append(" mean value ").Append(F4(level[3])).Append(", mean normal (").Append(F4(level[0]))
                            .Append(", ").Append(F4(level[1])).Append(", ").Append(F4(level[2])).Append(") length ")
                            .Append(F4(len)).Append("; normal ").Append(Hex(nf)).Append(", value ").Append(Hex(vf))
                            .AppendLine(" as the manifest");
                    }
                    if (size == 1)
                        break;
                    int next = size / 2;
                    var down = new float[next * next * 4];
                    for (int y = 0; y < next; y++)
                        for (int x = 0; x < next; x++)
                            for (int c = 0; c < 4; c++)
                            {
                                int a = ((2 * y) * size + 2 * x) * 4 + c, b = ((2 * y + 1) * size + 2 * x) * 4 + c;
                                down[(y * next + x) * 4 + c] = 0.25f * (level[a] + level[a + 4] + level[b] + level[b + 4]);
                            }
                    level = down;
                    size = next;
                }
            }
            map.Apply(false, true);   // (uploaded and made unreadable: the CPU copy freed)
            built.map = map;
            built.log.AppendLine($"  shifts: " + string.Join("; ", Shifts(built)));
            built.log.AppendLine($"  built in {clock.Elapsed.TotalSeconds:F1} s");
            return built;
        }

        static IEnumerable<string> Shifts(Built b)
        {
            foreach (var kv in b.shifts)
                yield return $"{kv.Key} [{string.Join(", ", kv.Value)}]";
        }

        static string F4(float v) => v.ToString("F4", CultureInfo.InvariantCulture);

        static string Hex(Dictionary<string, object> f) => ((string)f["pixels"]).Substring(0, 12);

        static int U16(byte[] raw, int i) => (raw[2 * i] << 8) | raw[2 * i + 1];

        /// <summary>A map read and checked against its manifest entry: its pixels' hash as patches.py's pixel_hash makes
        /// it (sha256 of numpy's shape string, then the samples big-endian, rows top first).</summary>
        static (int w, int h, int channels, byte[] raw) ReadChecked(string repo, Dictionary<string, object> entry)
        {
            string file = (string)entry["file"], want = (string)entry["pixels"];
            var (w, h, ch, raw) = Png16.Read(Path.Combine(repo, file));
            string shape = ch == 1 ? $"({h}, {w})" : $"({h}, {w}, {ch})";
            using var sha = SHA256.Create();
            var head = Encoding.UTF8.GetBytes(shape);
            sha.TransformBlock(head, 0, head.Length, null, 0);
            sha.TransformFinalBlock(raw, 0, raw.Length);
            var got = BitConverter.ToString(sha.Hash).Replace("-", "").ToLowerInvariant();
            if (got != want)
                throw new InvalidDataException($"{file}: its pixels' hash {got} is not the manifest's {want} (rebuild the patches: blender/parts/stone/slate/patches.py)");
            return (w, h, ch, raw);
        }

        /// <summary>A 16-bit PNG (grey or RGB, not interlaced) to its samples, big-endian, rows top first (as the file
        /// holds them, unfiltered).</summary>
        public static class Png16
        {
            public static (int w, int h, int channels, byte[] raw) Read(string path)
            {
                var d = File.ReadAllBytes(path);
                byte[] sig = { 137, 80, 78, 71, 13, 10, 26, 10 };
                for (int i = 0; i < 8; i++)
                    if (d[i] != sig[i])
                        throw new InvalidDataException($"{path}: not a PNG");
                int p = 8, w = 0, h = 0, ch = 0;
                var idat = new MemoryStream();
                while (p < d.Length)
                {
                    int n = (d[p] << 24) | (d[p + 1] << 16) | (d[p + 2] << 8) | d[p + 3];
                    string t = Encoding.ASCII.GetString(d, p + 4, 4);
                    if (t == "IHDR")
                    {
                        w = BE32(d, p + 8);
                        h = BE32(d, p + 12);
                        int depth = d[p + 16], type = d[p + 17], interlace = d[p + 20];
                        if (depth != 16 || (type != 0 && type != 2) || interlace != 0)
                            throw new InvalidDataException($"{path}: depth {depth}, type {type}, interlace {interlace}: only 16-bit grey or RGB, not interlaced");
                        ch = type == 0 ? 1 : 3;
                    }
                    else if (t == "IDAT")
                        idat.Write(d, p + 8, n);
                    else if (t == "IEND")
                        break;
                    p += 12 + n;
                }
                int bpp = ch * 2, stride = w * bpp;
                var filtered = new byte[h * (stride + 1)];
                idat.Position = 2;     // (the zlib header; DeflateStream reads the raw stream, the Adler-32 after it unread)
                using (var z = new DeflateStream(idat, CompressionMode.Decompress))
                {
                    int got = 0;
                    while (got < filtered.Length)
                    {
                        int r = z.Read(filtered, got, filtered.Length - got);
                        if (r <= 0)
                            throw new InvalidDataException($"{path}: its data ends after {got} of {filtered.Length} bytes");
                        got += r;
                    }
                }
                var raw = new byte[h * stride];
                for (int y = 0; y < h; y++)
                {
                    int f = filtered[y * (stride + 1)], src = y * (stride + 1) + 1, dst = y * stride, up = dst - stride;
                    for (int x = 0; x < stride; x++)
                    {
                        int a = x >= bpp ? raw[dst + x - bpp] : 0;
                        int b = y > 0 ? raw[up + x] : 0;
                        int c = x >= bpp && y > 0 ? raw[up + x - bpp] : 0;
                        int v = filtered[src + x];
                        switch (f)
                        {
                            case 0: break;
                            case 1: v += a; break;
                            case 2: v += b; break;
                            case 3: v += (a + b) >> 1; break;
                            case 4:
                                int pp = a + b - c, pa = Math.Abs(pp - a), pb = Math.Abs(pp - b), pc = Math.Abs(pp - c);
                                v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
                                break;
                            default: throw new InvalidDataException($"{path}: row {y} has filter {f}");
                        }
                        raw[dst + x] = (byte)v;
                    }
                }
                return (w, h, ch, raw);
            }

            static int BE32(byte[] d, int p) => (d[p] << 24) | (d[p + 1] << 16) | (d[p + 2] << 8) | d[p + 3];
        }

        /// <summary>A small JSON reader (the project has JsonUtility only, which reads no dictionary): objects to
        /// Dictionary (keys in file order), arrays to List, numbers to double, and strings, booleans and null.</summary>
        public static class Json
        {
            public static object Parse(string s)
            {
                int i = 0;
                var v = Value(s, ref i);
                Space(s, ref i);
                if (i != s.Length)
                    throw new FormatException($"JSON: text after the value at {i}");
                return v;
            }

            static void Space(string s, ref int i)
            {
                while (i < s.Length && char.IsWhiteSpace(s[i]))
                    i++;
            }

            static object Value(string s, ref int i)
            {
                Space(s, ref i);
                if (i >= s.Length)
                    throw new FormatException("JSON: ends early");
                char c = s[i];
                if (c == '{')
                {
                    var o = new OrderedDict();
                    i++;
                    Space(s, ref i);
                    if (s[i] == '}') { i++; return o; }
                    while (true)
                    {
                        Space(s, ref i);
                        string k = Str(s, ref i);
                        Space(s, ref i);
                        if (s[i++] != ':')
                            throw new FormatException($"JSON: ':' wanted at {i - 1}");
                        o.Add(k, Value(s, ref i));
                        Space(s, ref i);
                        char e = s[i++];
                        if (e == '}') return o;
                        if (e != ',') throw new FormatException($"JSON: ',' or '}}' wanted at {i - 1}");
                    }
                }
                if (c == '[')
                {
                    var a = new List<object>();
                    i++;
                    Space(s, ref i);
                    if (s[i] == ']') { i++; return a; }
                    while (true)
                    {
                        a.Add(Value(s, ref i));
                        Space(s, ref i);
                        char e = s[i++];
                        if (e == ']') return a;
                        if (e != ',') throw new FormatException($"JSON: ',' or ']' wanted at {i - 1}");
                    }
                }
                if (c == '"')
                    return Str(s, ref i);
                if (s.Length - i >= 4 && string.CompareOrdinal(s, i, "true", 0, 4) == 0) { i += 4; return true; }
                if (s.Length - i >= 5 && string.CompareOrdinal(s, i, "false", 0, 5) == 0) { i += 5; return false; }
                if (s.Length - i >= 4 && string.CompareOrdinal(s, i, "null", 0, 4) == 0) { i += 4; return null; }
                int start = i;
                while (i < s.Length && "+-0123456789.eE".IndexOf(s[i]) >= 0)
                    i++;
                if (i == start)
                    throw new FormatException($"JSON: a value wanted at {i}");
                return double.Parse(s.Substring(start, i - start), NumberStyles.Float, CultureInfo.InvariantCulture);
            }

            static string Str(string s, ref int i)
            {
                if (s[i] != '"')
                    throw new FormatException($"JSON: a string wanted at {i}");
                i++;
                var b = new StringBuilder();
                while (s[i] != '"')
                {
                    char c = s[i++];
                    if (c != '\\') { b.Append(c); continue; }
                    char e = s[i++];
                    switch (e)
                    {
                        case '"': b.Append('"'); break;
                        case '\\': b.Append('\\'); break;
                        case '/': b.Append('/'); break;
                        case 'b': b.Append('\b'); break;
                        case 'f': b.Append('\f'); break;
                        case 'n': b.Append('\n'); break;
                        case 'r': b.Append('\r'); break;
                        case 't': b.Append('\t'); break;
                        case 'u': b.Append((char)Convert.ToInt32(s.Substring(i, 4), 16)); i += 4; break;
                        default: throw new FormatException($"JSON: bad escape at {i - 1}");
                    }
                }
                i++;
                return b.ToString();
            }
        }

        /// <summary>A dictionary that also keeps its keys in the order the file gives them (the arms' slice order).</summary>
        public class OrderedDict : Dictionary<string, object>
        {
            readonly List<string> order = new List<string>();

            public IReadOnlyList<string> Order => order;

            public new void Add(string k, object v)
            {
                base.Add(k, v);
                order.Add(k);
            }
        }
    }
}
