using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using Overstory.Scenes;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The light records (fixtures/light/, schemas/light-record.schema.json) and the rigs written from them. A rig
    /// is a view of its record: every light value comes from the record's world state and the pack's light tables
    /// through light-derive-2, never from a number typed here. tools/light_record.py writes a record's sources and
    /// id; this writes its derived block and checks it on every load.
    ///
    ///     -executeMethod Overstory.EditorTools.LT1Light.Derive                      every record's derived block
    ///     -executeMethod Overstory.EditorTools.LT1Light.ValueView -in a.png -out b.png   ten L* bands in false colour
    /// </summary>
    public static class LT1Light
    {
        static string Root => Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
        static string Records => Path.Combine(Root, "fixtures", "light");
        const string Heart = "Assets/Art/Blockout/heart/lights.json";

        [System.Serializable] class Lamp { public string kind; }
        [System.Serializable] class Lamps { public Lamp[] lamps; }

        public static void Derive()
        {
            foreach (var path in Directory.GetFiles(Records, "*.json"))
                Load(Path.GetFileNameWithoutExtension(path));
        }

        /// <summary>Writes the rig at asset from the named record (fixtures/light/name.json) and returns it; with a
        /// place, the record's overrides for that place pushed after the keys.</summary>
        public static LightRig Rig(string record, string asset, string place = null)
        {
            var (rec, pack) = Load(record);
            if (place != null)
                rec.derived = LightDerive.Derive(rec, pack, ScriptableObject.CreateInstance<LightRig>().streetAxisCompass, place);
            var r = AssetDatabase.LoadAssetAtPath<LightRig>(asset);
            bool made = r == null;
            if (made)
                r = ScriptableObject.CreateInstance<LightRig>();
            LightDerive.ToRig(rec, pack, r, GlassKind());
            if (made)
                AssetDatabase.CreateAsset(r, asset);
            EditorUtility.SetDirty(r);
            return r;
        }

        /// <summary>A record and its pack, the record's derived block derived again and checked against the stored
        /// one: within tolerance it stands; otherwise the new block is written and the change is logged.</summary>
        static (LightRecord, LightPack) Load(string name)
        {
            string path = Path.Combine(Records, name + ".json");
            string text = File.ReadAllText(path);
            var rec = JsonUtility.FromJson<LightRecord>(text);
            if (rec.sources == null || rec.sources.function != LightDerive.Function)
                throw new System.InvalidOperationException($"{name}: function {rec.sources?.function}, not {LightDerive.Function}: run tools/light_record.py write");
            string light = Path.Combine(Root, "packs", rec.world.pack, "light");
            var pack = LightPack.Read(File.ReadAllText(Path.Combine(light, "sky.json")), File.ReadAllText(Path.Combine(light, "lamp-kinds.json")),
                                      File.ReadAllText(Path.Combine(light, "keys.json")), File.ReadAllText(Path.Combine(Root, "schemas", "light-terms.json")));
            var fresh = LightDerive.Derive(rec, pack, ScriptableObject.CreateInstance<LightRig>().streetAxisCompass);
            string now = JsonUtility.ToJson(fresh, true), stored = rec.derived != null ? JsonUtility.ToJson(rec.derived, true) : "";
            if (!LightDerive.Close(now, stored))
            {
                int at = text.LastIndexOf("\"derived\":", System.StringComparison.Ordinal);
                if (at < 0)
                    throw new System.InvalidOperationException($"{name}: no derived block");
                File.WriteAllText(path, text.Substring(0, at) + "\"derived\": " + now.Replace("\n", "\n  ") + "\n}\n");
                Debug.Log($"[LT1Light] {name}: derived again (EV100 {fresh.exposureEv100:F2}, sun {fresh.sun.elevationMillidegrees / 1000f:F1} degrees, " +
                          $"{fresh.sun.illuminanceLux:F0} lux, sky {fresh.sky.illuminanceLux:F1} lux, circuits {string.Join(",", fresh.circuitsOn)})");
            }
            rec.derived = fresh;
            return (rec, pack);
        }

        /// <summary>The kind whose glass the street's lamps show: the commonest street kind in the heart's lamps.</summary>
        static string GlassKind()
        {
            var counts = new Dictionary<string, int>();
            foreach (var l in JsonUtility.FromJson<Lamps>(File.ReadAllText(Path.Combine(Application.dataPath, "..", Heart))).lamps)
                if (l.kind != "shop")
                    counts[l.kind] = counts.TryGetValue(l.kind, out var n) ? n + 1 : 1;
            string best = null;
            foreach (var kv in counts)
                if (best == null || kv.Value > counts[best] || (kv.Value == counts[best] && string.CompareOrdinal(kv.Key, best) < 0))
                    best = kv.Key;
            return best;
        }

        // ten bands of CIE L*, dark to light, each its own hue so neighbouring values never read as one
        static readonly Color32[] Bands =
        {
            new Color32(20, 12, 40, 255), new Color32(52, 24, 104, 255), new Color32(40, 64, 160, 255), new Color32(24, 112, 176, 255),
            new Color32(24, 152, 136, 255), new Color32(80, 184, 80, 255), new Color32(176, 208, 48, 255), new Color32(248, 208, 40, 255),
            new Color32(248, 144, 48, 255), new Color32(255, 240, 230, 255),
        };

        /// <summary>The value view (schemas/light-terms.json, views): a still's L* in ten bands of false colour.</summary>
        public static void ValueView()
        {
            var args = System.Environment.GetCommandLineArgs();
            string input = null, output = null;
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == "-in") input = args[i + 1];
                if (args[i] == "-out") output = args[i + 1];
            }
            var tex = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            tex.LoadImage(File.ReadAllBytes(input));
            var px = tex.GetPixels32();
            var hist = new int[10];
            for (int i = 0; i < px.Length; i++)
            {
                float y = 0.2126f * Mathf.GammaToLinearSpace(px[i].r / 255f) + 0.7152f * Mathf.GammaToLinearSpace(px[i].g / 255f) + 0.0722f * Mathf.GammaToLinearSpace(px[i].b / 255f);
                float l = y > 0.008856f ? 116f * Mathf.Pow(y, 1f / 3f) - 16f : 903.3f * y;
                int b = Mathf.Clamp(Mathf.FloorToInt(l / 10f), 0, 9);
                hist[b]++;
                px[i] = Bands[b];
            }
            tex.SetPixels32(px);
            File.WriteAllBytes(output, tex.EncodeToPNG());
            var share = new string[10];
            for (int b = 0; b < 10; b++)
                share[b] = $"{100f * hist[b] / px.Length:F0}";
            Debug.Log($"[LT1Light] value view {Path.GetFileName(output)}: per cent by L* band 0-9: {string.Join(" ", share)}");
        }
    }
}
