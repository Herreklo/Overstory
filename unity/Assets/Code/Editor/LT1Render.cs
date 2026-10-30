using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The editor's still renders shared by the tests (LT1Finish, LT1Street, LT1Nature, PlayerFrame): Render draws a
    /// camera through the pipeline into a target; Still renders at twice its size and averages down (a 2 x 2 box), after
    /// a few warm-up frames, with a greyscale copy beside it for the value check; Raw is one linear sample a pixel, for
    /// painting over. The first street's own stills (Checkpoint, Looks, Clay) were retired with it on 30 October.
    /// </summary>
    public static class LT1Render
    {
        const int Width = 1920, Height = 1080, Super = 2, WarmUp = 8;

        /// <summary>
        /// A raw pass for painting over a frame: one sample a pixel, no supersampling (an edge between two materials
        /// must not blend into a third), linear, written as it is.
        /// </summary>
        public static void Raw(Camera cam, string file)
        {
            var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear) { antiAliasing = 1 };
            rt.Create();
            var target = cam.targetTexture;
            try
            {
                cam.targetTexture = rt;
                for (int i = 0; i < 3; i++)
                    Render(cam, rt);
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false, true);
                tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                File.WriteAllBytes(file, tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
            }
            finally
            {
                cam.targetTexture = target;
                rt.Release();
                Object.DestroyImmediate(rt);
            }
        }

        /// <param name="msaa">samples per pixel, as the game's PC pipeline renders them (4); 1 for the frames judged
        /// before trees, which stay as they were</param>
        /// <param name="colour">whether the colour still is kept beside the value check (false: the value alone)</param>
        public static void Still(Camera cam, string file, bool grey = true, bool eighth = false, int msaa = 1,
                                 bool colour = true)
        {
            var big = new RenderTexture(Width * Super, Height * Super, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
                { antiAliasing = msaa };
            var small = new RenderTexture(Width, Height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            big.Create();
            small.Create();
            var target = cam.targetTexture;
            try
            {
                cam.targetTexture = big;
                for (int i = 0; i < WarmUp; i++)
                    Render(cam, big);
                big.filterMode = FilterMode.Bilinear;
                Graphics.Blit(big, small); // each output pixel samples the centre of four: a box filter

                var prev = RenderTexture.active;
                RenderTexture.active = small;
                var tex = new Texture2D(Width, Height, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                if (colour)
                    File.WriteAllBytes(file, tex.EncodeToPNG());
                if (eighth)
                    File.WriteAllBytes(Path.ChangeExtension(file, null) + "-eighth.png", Shrink(tex, 8).EncodeToPNG());
                if (!grey)
                {
                    Object.DestroyImmediate(tex);
                    return;
                }

                // the value check: luminance from linear light, written back as sRGB
                var px = tex.GetPixels32();
                for (int i = 0; i < px.Length; i++)
                {
                    var c = ((Color)px[i]).linear;
                    float y = 0.2126f * c.r + 0.7152f * c.g + 0.0722f * c.b;
                    byte g = (byte)Mathf.Clamp(Mathf.RoundToInt(Mathf.LinearToGammaSpace(y) * 255f), 0, 255);
                    px[i] = new Color32(g, g, g, 255);
                }
                tex.SetPixels32(px);
                File.WriteAllBytes(Path.ChangeExtension(file, null) + "-grey.png", tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
            }
            finally
            {
                cam.targetTexture = target;
                big.Release();
                small.Release();
                Object.DestroyImmediate(big);
                Object.DestroyImmediate(small);
            }
        }

        /// <summary>A copy at 1/k size, each pixel the mean of a k x k block in linear light.</summary>
        static Texture2D Shrink(Texture2D src, int k)
        {
            int w = src.width / k, h = src.height / k;
            var px = src.GetPixels();
            var out_ = new Color[w * h];
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                {
                    Color acc = Color.clear;
                    for (int j = 0; j < k; j++)
                        for (int i = 0; i < k; i++)
                            acc += px[(y * k + j) * src.width + x * k + i].linear;
                    out_[y * w + x] = (acc / (k * k)).gamma;
                }
            var t = new Texture2D(w, h, TextureFormat.RGB24, false, false);
            t.SetPixels(out_);
            t.Apply();
            return t;
        }

        internal static void Render(Camera cam, RenderTexture rt)
        {
            var request = new RenderPipeline.StandardRequest { destination = rt };
            if (RenderPipeline.SupportsRenderRequest(cam, request))
                RenderPipeline.SubmitRenderRequest(cam, request);
            else
                cam.Render();
        }
    }
}
