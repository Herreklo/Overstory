using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.EditorTools
{
    /// <summary>
    /// A frame as the player sees it (docs/measuring.md; docs/research/painted-marks-in-motion.md, In short, 5): the
    /// player's screen size, 2560 by 1440, one sample a pixel with the game's own antialiasing (the pipeline's MSAA, 4x
    /// on the PC asset), never rendered larger and averaged down, which hides shimmer and puts footprint fades at one and
    /// a half times the distance the player sees them. Rendered through the pipeline as LT1Render does, read back exactly
    /// (the multisampled target resolved by a same-size copy) and written as an 8-bit sRGB PNG.
    /// </summary>
    public sealed class PlayerFrame : System.IDisposable
    {
        public const int Width = 2560, Height = 1440;

        readonly Camera cam;
        readonly RenderTexture target, resolved;
        readonly RenderTexture before;
        readonly Texture2D tex;
        public int Msaa { get; }

        public PlayerFrame(Camera cam, int width = Width, int height = Height)
        {
            this.cam = cam;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            // the camera takes its target's sample count: the game's (the pipeline asset's) when the camera allows MSAA
            Msaa = cam.allowMSAA ? Mathf.Max(1, urp.msaaSampleCount) : 1;
            target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = Msaa };
            resolved = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            target.Create();
            resolved.Create();
            tex = new Texture2D(width, height, TextureFormat.RGB24, false, false);
            before = cam.targetTexture;
            cam.targetTexture = target;
        }

        /// <summary>Renders the camera's view into the frame, as many times as asked (warm-up frames keep any history).</summary>
        public void Render(int times = 1)
        {
            for (int i = 0; i < times; i++)
                LT1Render.Render(cam, target);
        }

        /// <summary>Reads the last render back (sRGB bytes, bottom row first).</summary>
        public Texture2D Read()
        {
            Graphics.Blit(target, resolved);     // a same-size copy: each pixel its own, the samples resolved
            var prev = RenderTexture.active;
            RenderTexture.active = resolved;
            tex.ReadPixels(new Rect(0, 0, tex.width, tex.height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            return tex;
        }

        public void Save(string file)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(file));
            File.WriteAllBytes(file, Read().EncodeToPNG());
        }

        public void Dispose()
        {
            cam.targetTexture = before;
            target.Release();
            resolved.Release();
            Object.DestroyImmediate(target);
            Object.DestroyImmediate(resolved);
            Object.DestroyImmediate(tex);
        }
    }

    /// <summary>The measuring tools' command line: -flag value, -flag, and lists of wanted names.</summary>
    static class Cli
    {
        public static string Arg(string flag, string fallback)
        {
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, flag);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }

        public static bool Flag(string flag) => System.Array.IndexOf(System.Environment.GetCommandLineArgs(), flag) >= 0;

        /// <summary>True when -flag is absent, or one of its comma-separated names starts the value.</summary>
        public static bool Wanted(string flag, string value)
        {
            string list = Arg(flag, null);
            if (list == null)
                return true;
            foreach (var w in list.Split(','))
                if (value.StartsWith(w))
                    return true;
            return false;
        }

        /// <summary>A path from the command line, relative to the repository's root, or the fallback there.</summary>
        public static string RepoPath(string flag, string fallback)
        {
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            return Path.GetFullPath(Path.Combine(root, Arg(flag, fallback)));
        }
    }
}
