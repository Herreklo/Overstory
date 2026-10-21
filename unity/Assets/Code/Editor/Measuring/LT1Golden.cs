using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The golden views (docs/measuring.md): today's gully, staged exactly as LT1Stone.Frames stages it, at the judging
    /// views (eye level at the foot of the steps and on them, the street stop, 12 m along the lane, the city camera) in
    /// the three judging lights, at the player's size and as the player sees them (PlayerFrame: 2560 by 1440, one
    /// sample a pixel, the game's MSAA). Every later change to the gully is compared against them
    /// (blender/tools/golden_compare.py).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Golden.Views
    ///         [-out reviews/golden/current] [-moments 1300,...] [-views eye-foot,...] [-tweak]
    ///
    /// Frames go to &lt;out&gt;/gully/&lt;moment&gt;/&lt;view&gt;.png with a frames.json beside them. -tweak is the
    /// comparison's own test: the slate's weathered colour a shade warmer, in memory only (never saved), so a known
    /// small change must show in the heat map.
    /// </summary>
    public static class LT1Golden
    {
        /// <summary>The judging views the golden set holds, by their names in LT1Stone.Views.</summary>
        public static readonly string[] ViewNames = { "eye-foot", "eye-on", "street", "into12", "high" };

        /// <summary>Warm-up renders before a frame is kept, as LT1Render.Still does, so screen-space history settles.</summary>
        public const int WarmUp = 8;

        public static void Views()
        {
            string outDir = Cli.RepoPath("-out", "reviews/golden/current");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var tweaked = new List<Material>();
            if (Cli.Flag("-tweak"))
                foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
                {
                    var m = new Material(r.sharedMaterial) { name = r.sharedMaterial.name + " (tweak, never saved)" };
                    var c = m.GetColor("_Stone");
                    m.SetColor("_Stone", new Color(c.r * 1.06f, c.g * 1.02f, c.b * 0.98f, c.a));
                    r.sharedMaterial = m;
                    tweaked.Add(m);
                }
            var frames = new List<string>();
            int msaa = 0;
            try
            {
                foreach (var moment in LT1Stone.Moments)
                {
                    if (!Cli.Wanted("-moments", moment))
                        continue;
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{moment}.asset");
                    foreach (var view in LT1Stone.Views)
                    {
                        if (System.Array.IndexOf(ViewNames, view.name) < 0 || !Cli.Wanted("-views", view.name))
                            continue;
                        LT1Stone.Aim(stage, shot, view);
                        string file = Path.Combine(outDir, "gully", moment, view.name + ".png");
                        using (var frame = new PlayerFrame(stage.view))
                        {
                            frame.Render(WarmUp + 1);
                            frame.Save(file);
                            msaa = frame.Msaa;
                        }
                        frames.Add($"gully/{moment}/{view.name}.png");
                        Debug.Log($"[LT1Golden] {file}");
                    }
                }
                File.WriteAllText(Path.Combine(outDir, "gully", "frames.json"), JsonUtility.ToJson(new Record
                {
                    what = "the gully's golden views (LT1Golden.Views)",
                    width = PlayerFrame.Width, height = PlayerFrame.Height, msaa = msaa, warmUp = WarmUp,
                    tweak = Cli.Flag("-tweak"), unity = Application.unityVersion,
                    gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(),
                    frames = frames.ToArray(),
                }, true));
            }
            finally
            {
                urp.shadowDistance = reach;
                foreach (var m in tweaked)
                    Object.DestroyImmediate(m);
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        [System.Serializable]
        class Record
        {
            public string what;
            public int width, height, msaa, warmUp;
            public bool tweak;
            public string unity, gpu, api;
            public string[] frames;
        }
    }
}
