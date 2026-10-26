using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The light's passes timed offscreen in the editor, with no window on the screen: the gully's stage as its stills
    /// draw it (LT1Stone.Stage), each moment and view drawn into a 2560 by 1440 target with MSAA 4x back to back, six
    /// batches of six after one that primes, as PerfRunner's offscreen frames are; each arm the same frames with one pass
    /// changed ('all'; '-foglights' without the lamps' halos; 'foglights-full' with them drawn as before the third round).
    /// The editor's own work is in the numbers, so they are for an A/B between the arms of one run; the player's harness
    /// (tools/perf.sh) gives the frame.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1LightTime.Passes
    ///         [-moment 1750-sea-fog,...] [-view street,eye-foot] [-arms all,-foglights,foglights-full] [-out file.md]
    /// </summary>
    public static class LT1LightTime
    {
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const string Renderer = "Assets/Settings/PC_Renderer.asset";
        const int Batches = 6, PerBatch = 6;

        public static void Passes()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var moments = Cli.Arg("-moment", "1750-sea-fog").Split(',');
            var viewNames = Cli.Arg("-view", "street,eye-foot").Split(',');
            var arms = Cli.Arg("-arms", "all,-foglights,foglights-full").Split(',');
            string outFile = Cli.Arg("-out", "");
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Renderer);
            var fog = data.rendererFeatures.OfType<FogLightsFeature>().FirstOrDefault()
                      ?? throw new System.InvalidOperationException("no FogLightsFeature on the renderer");
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var target = new RenderTexture(2560, 1440, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 4 };
            target.Create();
            var probe = new RenderTexture(1, 1, 0, RenderTextureFormat.ARGB32);
            probe.Create();
            var rows = new List<string>();
            try
            {
                foreach (var moment in moments)
                {
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset")
                                ?? throw new FileNotFoundException($"no rig {moment}");
                    stage.Apply();
                    foreach (var viewName in viewNames)
                    {
                        var view = System.Array.Find(LT1Stone.Views, v => v.name == viewName);
                        if (view.name == null)
                            throw new System.ArgumentException($"no gully view {viewName}");
                        LT1Stone.Aim(stage, shot, view);
                        var cells = new List<string>();
                        foreach (var arm in arms)
                        {
                            fog.SetActive(arm != "-foglights");
                            fog.fullSize = arm == "foglights-full";
                            TownLights.cullToView = !fog.fullSize; // (as it was: every lamp at every pixel)
                            var ms = new List<double>();
                            for (int b = 0; b <= Batches; b++)
                            {
                                var clock = System.Diagnostics.Stopwatch.StartNew();
                                for (int k = 0; k < PerBatch; k++)
                                {
                                    var request = new RenderPipeline.StandardRequest { destination = target };
                                    if (RenderPipeline.SupportsRenderRequest(stage.view, request))
                                        RenderPipeline.SubmitRenderRequest(stage.view, request);
                                    else
                                    {
                                        stage.view.targetTexture = target;
                                        stage.view.Render();
                                        stage.view.targetTexture = null;
                                    }
                                }
                                Graphics.Blit(target, probe);
                                AsyncGPUReadback.Request(probe).WaitForCompletion();
                                if (b > 0) // (the first batch only primes)
                                    ms.Add(clock.Elapsed.TotalMilliseconds / PerBatch);
                            }
                            ms.Sort();
                            double median = ms[ms.Count / 2];
                            cells.Add($"{median:F1}");
                            Debug.Log($"[LT1LightTime] {moment} {viewName} {arm}: {median:F2} ms (batches {string.Join(" ", ms.Select(x => x.ToString("F1")))}), " +
                                      $"lamps in view {Shader.GetGlobalInt("_OS_FogLampCount")}");
                        }
                        rows.Add($"| {moment} {viewName} | {string.Join(" | ", cells)} |");
                    }
                }
            }
            finally
            {
                fog.SetActive(true);
                fog.fullSize = false;
                TownLights.cullToView = true;
                target.Release();
                probe.Release();
                Object.DestroyImmediate(target);
                Object.DestroyImmediate(probe);
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
                ShaderUtil.allowAsyncCompilation = async;
            }
            if (outFile != "")
            {
                var md = new StringBuilder();
                md.AppendLine($"Milliseconds a frame, offscreen in the editor (LT1LightTime.Passes; {SystemInfo.graphicsDeviceName}, 2560x1440, MSAA 4x, " +
                              $"median of {Batches} batches of {PerBatch}).").AppendLine();
                md.AppendLine($"| Moment and view | {string.Join(" | ", arms)} |");
                md.AppendLine($"| --- |{string.Concat(Enumerable.Repeat(" --- |", arms.Length))}");
                foreach (var r in rows)
                    md.AppendLine(r);
                string path = Path.Combine(repo, outFile);
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, md.ToString());
            }
        }
    }
}
