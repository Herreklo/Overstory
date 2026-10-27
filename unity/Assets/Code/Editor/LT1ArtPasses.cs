using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The passes a style frame is painted over (reviews/lt1/art-direction/, tools/style_frame.py): the corner exactly as
    /// LT1Houses.Still stages it (its houses, the gully, the clay), drawn once per pass with every renderer's material
    /// swapped for ArtPasses.shader, with no post, no style and no light in the air. Takes LT1Houses.Still's command
    /// line (-out, -view, -houses, -tier; one -moment) and writes {out}-{view}-{pass}.png for each view:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1ArtPasses.Passes
    ///         -out reviews/lt1/art-direction/passes/street -view street -houses C,D,E -tier street -moment 1300-drizzle
    ///         -looks grey -ref ""
    ///
    /// The beauty frames come from LT1Houses.Still itself, with the same arguments and the lights wanted.
    /// </summary>
    public static class LT1ArtPasses
    {
        static readonly string[] Names = { "normal", "distance", "position", "fine", "surface" };
        static readonly int PassId = Shader.PropertyToID("_OS_ArtPass");
        static readonly int ClassId = Shader.PropertyToID("_Class");
        static readonly string[] Quiet = { "_OS_PaletteOn", "_OS_FogLampStrength" };
        static readonly string[] QuietVectors = { "_OS_SunBeams", "_OS_GlowParams" };

        static Material pass;
        static readonly List<(Renderer r, Material[] mats, MaterialPropertyBlock block)> swapped = new();
        static readonly Dictionary<string, float> quiet = new();
        static readonly Dictionary<string, Vector4> quietVectors = new();
        static bool post;
        static CameraClearFlags clear;
        static Color background;
        static Material skybox;

        /// <summary>What a renderer is, by its material's shader: 0 nothing (the sky), 1 clay, 2 a house, 3 stone, 4 a tree, 5 the sky's dome, 6 anything else.</summary>
        static float ClassOf(Material m)
        {
            string s = m != null && m.shader != null ? m.shader.name : "";
            if (s.Contains("House")) return 2f;
            if (s.Contains("Stone")) return 3f;
            if (s.Contains("Tree")) return 4f;
            if (s.Contains("Sky")) return 5f;
            if (s.Contains("Street")) return 1f;
            return 6f;
        }

        public static void Passes()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outBase = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/art-direction/passes/street"));
            string[] views = Cli.Arg("-view", "street").Split(',');
            string moment = Cli.Arg("-moment", "1300-drizzle");
            pass = new Material(Shader.Find("Hidden/Overstory/ArtPasses")) { hideFlags = HideFlags.DontSave };
            RenderPipelineManager.beginCameraRendering += Swap;
            RenderPipelineManager.endCameraRendering += Restore;
            try
            {
                for (int k = 0; k < Names.Length; k++)
                {
                    Shader.SetGlobalFloat(PassId, k + 1);
                    LT1Houses.Still();
                    foreach (var view in views)
                    {
                        string made = $"{outBase}-{moment}-{view}-grey";
                        string file = $"{outBase}-{view}-{Names[k]}.png";
                        if (File.Exists(file))
                            File.Delete(file);
                        File.Move(made + ".png", file);
                        if (File.Exists(made + "-grey.png"))
                            File.Delete(made + "-grey.png");
                        Debug.Log($"[LT1ArtPasses] {file}");
                    }
                    if (File.Exists($"{outBase}-sheet.png"))
                        File.Delete($"{outBase}-sheet.png");
                }
            }
            finally
            {
                RenderPipelineManager.beginCameraRendering -= Swap;
                RenderPipelineManager.endCameraRendering -= Restore;
                Shader.SetGlobalFloat(PassId, 0f);
                Object.DestroyImmediate(pass);
            }
        }

        static void Swap(ScriptableRenderContext context, Camera cam)
        {
            if (cam.cameraType != CameraType.Game)
                return;
            swapped.Clear();
            foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                if (!r.enabled || r.sharedMaterials.Length == 0)
                    continue;
                var block = new MaterialPropertyBlock();
                if (r.HasPropertyBlock())
                    r.GetPropertyBlock(block);
                swapped.Add((r, r.sharedMaterials, block));
                var mats = new Material[r.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = pass;
                var mine = new MaterialPropertyBlock();
                mine.SetFloat(ClassId, ClassOf(r.sharedMaterial));
                r.sharedMaterials = mats;
                r.SetPropertyBlock(mine);
            }
            foreach (var q in Quiet)
            {
                quiet[q] = Shader.GetGlobalFloat(q);
                Shader.SetGlobalFloat(q, 0f);
            }
            foreach (var q in QuietVectors)
            {
                quietVectors[q] = Shader.GetGlobalVector(q);
                Shader.SetGlobalVector(q, Vector4.zero);
            }
            var data = cam.GetComponent<UniversalAdditionalCameraData>();
            post = data != null && data.renderPostProcessing;
            if (data != null)
                data.renderPostProcessing = false;
            clear = cam.clearFlags;
            background = cam.backgroundColor;
            skybox = RenderSettings.skybox;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            RenderSettings.skybox = null;
        }

        static void Restore(ScriptableRenderContext context, Camera cam)
        {
            if (cam.cameraType != CameraType.Game)
                return;
            foreach (var (r, mats, block) in swapped)
            {
                if (r == null)
                    continue;
                r.sharedMaterials = mats;
                r.SetPropertyBlock(block.isEmpty ? null : block);
            }
            swapped.Clear();
            foreach (var kv in quiet)
                Shader.SetGlobalFloat(kv.Key, kv.Value);
            foreach (var kv in quietVectors)
                Shader.SetGlobalVector(kv.Key, kv.Value);
            var data = cam.GetComponent<UniversalAdditionalCameraData>();
            if (data != null)
                data.renderPostProcessing = post;
            cam.clearFlags = clear;
            cam.backgroundColor = background;
            RenderSettings.skybox = skybox;
        }
    }
}
