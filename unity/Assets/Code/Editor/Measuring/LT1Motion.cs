using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The motion sheets (docs/measuring.md; docs/research/painted-marks-in-motion.md, Look tests that would prove it, 1):
    /// the gully, staged as its frames stage it, along camera paths at 60 frames a second, each frame as the player sees
    /// it (PlayerFrame: 2560 by 1440, one sample a pixel, the game's MSAA), written as a PNG sequence. The paths:
    /// - still: the street stop held still, to catch anything that moves when nothing should;
    /// - walk: a person walking past the foot of the steps at 1.4 m/s, eye at 1.7 m, looking at the steps;
    /// - pan: the street stop turning slowly, 5 degrees a second;
    /// - crane: rising from the street stop (2.8 m) to 12 m over the lane, eased in and out.
    /// The world's clock is the light's own, so the world holds still and only the camera moves.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Motion.Sheets
    ///         [-paths still,walk,pan,crane] [-moments 1600-low-sun] [-out reviews/motion/current] [-birch]
    ///         [-test crawl|smooth] [-nodither]
    ///
    /// Sequences go to &lt;out&gt;/&lt;moment&gt;/&lt;path&gt;/0000.png on; blender/tools/motion_measure.py measures them.
    /// -birch plants the corner's birch (LT1Perf). -test stands a board on the first steps, in memory only, with a checker
    /// of millimetre squares: "crawl" samples it without mips (it aliases and crawls as the camera moves), "smooth" with
    /// trilinear mips (the same pattern band-limited), the shimmer measure's own known case. -nodither turns the camera's
    /// dithering off in memory: URP draws it as a fresh noise each frame, so a still camera with it on is never still.
    /// </summary>
    public static class LT1Motion
    {
        public const int Fps = 60;

        /// <summary>A camera path: where the camera is and looks at a time (seconds), and how long it runs.</summary>
        public sealed class CamPath
        {
            public string name;
            public float seconds;
            public System.Func<float, (Vector3 pos, Vector3 target, float fov)> at;
        }

        static float Ease(float u) => u * u * (3f - 2f * u);

        public static readonly CamPath[] Paths = MakePaths();

        static CamPath[] MakePaths()
        {
            var street = System.Array.Find(LT1Stone.Views, v => v.name == "street");
            var foot = LT1Stone.Foot;
            var lookUp = LT1Stone.LowerMid + new Vector3(0f, 0f, 0.4f);
            // the street stop's ground: the lane 2.8 m under its eye
            float streetGround = street.pos.z - 2.8f;
            return new[]
            {
                new CamPath { name = "still", seconds = 1f, at = t => (street.pos, street.target, street.fov) },
                // along Low Terrace past the foot of the steps, 3.2 m out, eye at 1.7 m, the head turned to the steps
                new CamPath
                {
                    name = "walk", seconds = 2.5f,
                    at = t => (new Vector3(foot.x - 1.15f + 1.4f * t, foot.y - 3.2f, foot.z + 1.7f), lookUp, 37.8f),
                },
                // the street stop turning from 7.5 degrees left of its view to 7.5 right, about its own eye
                new CamPath
                {
                    name = "pan", seconds = 3f,
                    at = t =>
                    {
                        var d = street.target - street.pos;
                        float a = (-7.5f + 5f * t) * Mathf.Deg2Rad;
                        var r = new Vector3(d.x * Mathf.Cos(a) - d.y * Mathf.Sin(a), d.x * Mathf.Sin(a) + d.y * Mathf.Cos(a), d.z);
                        return (street.pos, street.pos + r, street.fov);
                    },
                },
                // straight up from the street stop to 12 m over the lane, keeping its view's target
                new CamPath
                {
                    name = "crane", seconds = 3f,
                    at = t => (new Vector3(street.pos.x, street.pos.y, streetGround + Mathf.Lerp(2.8f, 12f, Ease(t / 3f))),
                               street.target, street.fov),
                },
            };
        }

        public static void Sheets()
        {
            string outDir = Cli.RepoPath("-out", "reviews/motion/current");
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            var (stage, go) = LT1Stone.Stage(false);
            var extras = new List<Object>();
            if (Cli.Flag("-birch"))
                extras.Add(LT1Perf.PlantBirch().root);
            string test = Cli.Arg("-test", "");
            if (test != "")
                extras.AddRange(TestBoard(test == "crawl"));
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            // -nodither: the camera's dithering off, in memory (URP's dither is a fresh noise each frame, a level up or down)
            var cameraData = stage.view.GetComponent<UniversalAdditionalCameraData>();
            bool dithered = cameraData != null && cameraData.dithering;
            if (cameraData != null && Cli.Flag("-nodither"))
                cameraData.dithering = false;
            string suffix = (test != "" ? "-" + test : "") + (Cli.Flag("-nodither") ? "-nodither" : "");
            try
            {
                foreach (var moment in LT1Stone.Moments)
                {
                    if (!Cli.Wanted("-moments", moment) || (Cli.Arg("-moments", null) == null && moment != "1600-low-sun"))
                        continue;
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{moment}.asset");
                    foreach (var path in Paths)
                    {
                        if (!Cli.Wanted("-paths", path.name))
                            continue;
                        string dir = Path.Combine(outDir, moment, path.name + suffix);
                        if (Directory.Exists(dir))
                            Directory.Delete(dir, true);
                        Directory.CreateDirectory(dir);
                        int n = Mathf.RoundToInt(path.seconds * Fps);
                        var clock = System.Diagnostics.Stopwatch.StartNew();
                        using (var frame = new PlayerFrame(stage.view))
                        {
                            for (int i = 0; i < n; i++)
                            {
                                var (pos, target, fov) = path.at(i / (float)Fps);
                                LT1Stone.Aim(stage, shot, (path.name, pos, target, fov));
                                // the first frame after the golden views' warm-up; then one render a frame, as the game draws
                                frame.Render(i == 0 ? LT1Golden.WarmUp + 1 : 1);
                                frame.Save(Path.Combine(dir, $"{i:0000}.png"));
                            }
                        }
                        File.WriteAllText(Path.Combine(dir, "sequence.json"), JsonUtility.ToJson(new Sequence
                        {
                            path = path.name, moment = moment, fps = Fps, frames = n, width = PlayerFrame.Width,
                            height = PlayerFrame.Height, test = test, birch = Cli.Flag("-birch"),
                            dithering = cameraData != null && cameraData.dithering,
                        }, true));
                        Debug.Log($"[LT1Motion] {dir}: {n} frames in {clock.Elapsed.TotalSeconds:F0} s");
                    }
                }
            }
            finally
            {
                urp.shadowDistance = reach;
                if (cameraData != null)
                    cameraData.dithering = dithered;
                foreach (var o in extras)
                    Object.DestroyImmediate(o);
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        /// <summary>
        /// The known crawling pattern: a board standing on the first steps, facing down the lane, 1.2 by 0.8 m, with a
        /// checker of 1 mm squares (about half a pixel from the walk). Without mips it aliases into a moire that crawls as
        /// the camera moves; with trilinear mips the same pattern is band-limited to its mean. In memory only.
        /// </summary>
        static Object[] TestBoard(bool crawl)
        {
            const int size = 1024;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, !crawl, false)
            {
                filterMode = crawl ? FilterMode.Point : FilterMode.Trilinear, anisoLevel = crawl ? 0 : 8,
                wrapMode = TextureWrapMode.Repeat, name = "crawl test checker",
            };
            var px = new Color32[size * size];
            for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                    px[y * size + x] = ((x + y) & 1) == 0 ? new Color32(235, 235, 235, 255) : new Color32(20, 20, 20, 255);
            tex.SetPixels32(px);
            tex.Apply(!crawl);
            var mat = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "crawl test board" };
            mat.SetTexture("_BaseMap", tex);
            mat.SetTextureScale("_BaseMap", new Vector2(1.2f, 0.8f));     // 1024 squares a metre
            var board = GameObject.CreatePrimitive(PrimitiveType.Quad);
            board.name = "crawl test board";
            Object.DestroyImmediate(board.GetComponent<Collider>());
            board.GetComponent<MeshRenderer>().sharedMaterial = mat;
            var at = LT1Stone.Foot + new Vector3(0f, 1.2f, 0.9f);
            board.transform.SetPositionAndRotation(StreetSpace.ToUnity(at), Quaternion.LookRotation(StreetSpace.ToUnity(new Vector3(0f, 1f, 0f)) - StreetSpace.ToUnity(Vector3.zero), Vector3.up));
            board.transform.localScale = new Vector3(1.2f, 0.8f, 1f);
            return new Object[] { board, mat, tex };
        }

        [System.Serializable]
        class Sequence
        {
            public string path, moment, test;
            public int fps, frames, width, height;
            public bool birch, dithering;
        }
    }
}
