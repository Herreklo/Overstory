using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The golden views (docs/measuring.md): the street as its own test stages it (StreetStaging: Street.unity as the
    /// last LT1Street.Run left it, in way Pc), at its judging views (eye, street, raised and high; -views keeps others) in
    /// its two lights (overcast and low sun), at the player's size and as the player sees them (PlayerFrame: 2560 by 1440,
    /// one sample a pixel, the game's MSAA). Every later change to the street is compared against an accepted set of them
    /// (blender/tools/golden_compare.py; only Øystein accepts one).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Golden.Views
    ///         [-out reviews/golden/current] [-lights overcast,lowsun] [-views eye,street,...] [-tweak]
    ///
    /// Frames go to &lt;out&gt;/street/&lt;light&gt;/&lt;view&gt;.png with a frames.json beside them naming the houses.
    /// -tweak is the comparison's own test: the houses' paint a shade warmer (_Tint), in memory only (never saved), so a
    /// known small change must show in the heat map.
    /// </summary>
    public static class LT1Golden
    {
        /// <summary>Warm-up renders before a frame is kept, so screen-space history settles.</summary>
        public const int WarmUp = 8;

        public static void Views()
        {
            string outDir = Cli.RepoPath("-out", "reviews/golden/current");
            bool tweak = Cli.Flag("-tweak");
            var tweaked = new Dictionary<Material, Material>();
            var frames = new List<string>();
            int msaa = 0;
            using (StreetStaging.Pipeline())
            {
                try
                {
                    var s = StreetStaging.Open();
                    foreach (var light in s.lightNames.Where(l => Cli.Wanted("-lights", l)))
                        foreach (var stop in s.stops)
                        {
                            s.Apply(light, stop, "Pc");
                            if (tweak)
                                foreach (var r in s.roots.SelectMany(x => x.GetComponentsInChildren<Renderer>()))
                                    r.sharedMaterials = r.sharedMaterials.Select(m =>
                                    {
                                        if (m == null || !m.HasProperty("_Tint"))
                                            return m;
                                        if (!tweaked.TryGetValue(m, out var t))
                                        {
                                            t = new Material(m) { name = m.name + " (tweak, never saved)" };
                                            var c = t.GetVector("_Tint");
                                            t.SetVector("_Tint", new Vector4(c.x * 1.06f, c.y * 1.02f, c.z * 0.98f, c.w));
                                            tweaked[m] = t;
                                        }
                                        return t;
                                    }).ToArray();
                            string file = Path.Combine(outDir, "street", light, stop.name + ".png");
                            using (var frame = new PlayerFrame(s.cam))
                            {
                                frame.Render(WarmUp + 1);
                                frame.Save(file);
                                msaa = frame.Msaa;
                            }
                            frames.Add($"street/{light}/{stop.name}.png");
                            Debug.Log($"[LT1Golden] {file}");
                        }
                    Directory.CreateDirectory(Path.Combine(outDir, "street"));
                    File.WriteAllText(Path.Combine(outDir, "street", "frames.json"), JsonUtility.ToJson(new Record
                    {
                        what = "the street's golden views (LT1Golden.Views)", scene = StreetStaging.ScenePath,
                        houses = string.Join(",", s.ids),
                        width = PlayerFrame.Width, height = PlayerFrame.Height, msaa = msaa, warmUp = WarmUp,
                        tweak = tweak, unity = Application.unityVersion,
                        gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(),
                        frames = frames.ToArray(),
                    }, true));
                }
                finally
                {
                    foreach (var m in tweaked.Values)
                        Object.DestroyImmediate(m);
                }
            }
        }

        [System.Serializable]
        class Record
        {
            public string what, scene, houses;
            public int width, height, msaa, warmUp;
            public bool tweak;
            public string unity, gpu, api;
            public string[] frames;
        }
    }
}
