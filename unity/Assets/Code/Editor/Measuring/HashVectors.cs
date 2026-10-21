using System.Globalization;
using System.IO;
using Overstory.Core;
using UnityEditor;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The hash spec's test (docs/building-blocks.md, Seeds and determinism): Core/Hash.cs must reproduce every key,
    /// unit and stream in fixtures/golden/hash-vectors.json, which Python's blender/resolver/hashing.py wrote and
    /// reproduces (blender/resolver/hash_vectors.py check). Exits 1 on any difference, naming the key.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.HashVectors.Check -logFile -
    /// </summary>
    public static class HashVectors
    {
        [System.Serializable] class Part { public string t, v; }
        [System.Serializable] class Vector { public Part[] key; public string hash; public double unit; }
        [System.Serializable] class StreamVector { public Part[] key; public string[] draws; public double[] normals; }
        [System.Serializable] class Data { public Vector[] vectors; public StreamVector[] streams; }

        public static void Check()
        {
            string path = Cli.RepoPath("-vectors", "fixtures/golden/hash-vectors.json");
            var data = JsonUtility.FromJson<Data>(File.ReadAllText(path, System.Text.Encoding.UTF8));
            int bad = 0;
            foreach (var v in data.vectors)
            {
                ulong h = Of(v.key);
                ulong want = ulong.Parse(v.hash, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                // (the unit is exact from the hash; the tolerance only covers the JSON reader's last digit)
                if (h != want || System.Math.Abs(Hash.Unit(h) - v.unit) > 1e-15)
                {
                    bad++;
                    Debug.LogError($"[HashVectors] DIFF {Show(v.key)}: {h:x16}, want {v.hash}; unit {Hash.Unit(h):R}, want {v.unit:R}");
                }
            }
            foreach (var s in data.streams)
            {
                var stream = new Hash.Stream(Of(s.key));
                for (int i = 0; i < s.draws.Length; i++)
                {
                    ulong got = stream.Next();
                    if (got != ulong.Parse(s.draws[i], NumberStyles.HexNumber, CultureInfo.InvariantCulture))
                    {
                        bad++;
                        Debug.LogError($"[HashVectors] DIFF stream {Show(s.key)} draw {i}: {got:x16}, want {s.draws[i]}");
                    }
                }
                stream = new Hash.Stream(Of(s.key));
                for (int i = 0; i < s.normals.Length; i++)
                {
                    double got = stream.Normal();
                    if (System.Math.Abs(got - s.normals[i]) > 1e-12)
                    {
                        bad++;
                        Debug.LogError($"[HashVectors] DIFF stream {Show(s.key)} normal {i}: {got:R}, want {s.normals[i]:R}");
                    }
                }
            }
            string verdict = bad == 0 ? "PASS" : "FAIL";
            Debug.Log($"[HashVectors] {verdict}: {data.vectors.Length} hashes and {data.streams.Length} streams, {bad} differ ({path})");
            if (bad != 0 || data.vectors.Length != 200)
                EditorApplication.Exit(1);
        }

        /// <summary>A key's parts folded as the spec folds them: an integer as its two's complement, a string by FNV-1a.</summary>
        static ulong Of(Part[] key)
        {
            ulong acc = Hash.Start;
            foreach (var p in key)
                acc = p.t == "int"
                    ? Hash.Then(acc, p.v.StartsWith("-")
                        ? Hash.Key(long.Parse(p.v, CultureInfo.InvariantCulture))
                        : ulong.Parse(p.v, CultureInfo.InvariantCulture))
                    : Hash.Then(acc, p.v);
            return acc;
        }

        static string Show(Part[] key) => "[" + string.Join(", ", System.Array.ConvertAll(key, p => p.t == "int" ? p.v : $"\"{p.v}\"")) + "]";
    }
}
