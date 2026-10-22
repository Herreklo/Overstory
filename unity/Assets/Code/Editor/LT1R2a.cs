using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// Port step 2b, rung R2a's stones (reviews/lt1/port/2b/r2a/stones/plan.md, the contract).
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1R2a.Proof -tag before|after
    ///         [-overview]
    ///
    /// Proof: the off-state proof of Stone.shader's OS_PATCHES arm, one gully view (eye-foot, 1600-low-sun) as the
    /// player sees it (PlayerFrame), into frames/proof/&lt;tag&gt;.png; tools/r0b_count.py --same compares two of them.
    /// Nothing here saves an asset or the scene.
    /// </summary>
    public static class LT1R2a
    {
        const string Lights = "Assets/Experiments/LT1/Heart/Light";

        static string OutDir => Cli.RepoPath("-out", "reviews/lt1/port/2b/r2a/stones/frames");

        static LightRig Rig(string moment) => AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");

        public static void Proof()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            string tag = Cli.Arg("-tag", "after");
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            try
            {
                stage.rig = Rig("1600-low-sun");
                var view = System.Array.Find(LT1Stone.Views, v => v.name == "eye-foot");
                LT1Stone.Aim(stage, shot, view);
                string file = Path.Combine(OutDir, "proof", tag + ".png");
                var clock = System.Diagnostics.Stopwatch.StartNew();
                using (var frame = new PlayerFrame(stage.view))
                {
                    frame.Render(LT1Golden.WarmUp + 1);
                    frame.Save(file);
                }
                Debug.Log($"[LT1R2a] proof {file} in {clock.Elapsed.TotalSeconds:F1} s");
                if (Cli.Flag("-overview"))
                    Overview(stage, shot);
            }
            finally
            {
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>Frames from above round the gully's foot and the Landing, in low sun and at the blue hour (the lamps'
        /// pools), to choose where the stones stand.</summary>
        static void Overview(StreetStage stage, CameraShot shot)
        {
            var spots = new (string name, Vector3 pos, Vector3 target)[]
            {
                ("foot-above", LT1Stone.Foot + new Vector3(0f, -0.5f, 30f), LT1Stone.Foot),
                ("landing-above", new Vector3(46f, 37.5f, 38f), new Vector3(46f, 38f, 8f)),
                ("foot-oblique", LT1Stone.Foot + new Vector3(14f, -14f, 12f), LT1Stone.Foot + new Vector3(0f, 4f, 0f)),
                ("landing-oblique", new Vector3(58f, 24f, 18f), new Vector3(46f, 38f, 8f)),
            };
            foreach (var moment in new[] { "1600-low-sun", "1750-blue-hour" })
            {
                stage.rig = Rig(moment);
                foreach (var s in spots)
                {
                    LT1Stone.Aim(stage, shot, (s.name, s.pos, s.target, 46.4f));
                    string file = Path.Combine(OutDir, "overview", moment, s.name + ".png");
                    var clock = System.Diagnostics.Stopwatch.StartNew();
                    using (var frame = new PlayerFrame(stage.view))
                    {
                        frame.Render(LT1Golden.WarmUp + 1);
                        frame.Save(file);
                    }
                    Debug.Log($"[LT1R2a] overview {file} in {clock.Elapsed.TotalSeconds:F1} s");
                }
            }
        }
    }
}
