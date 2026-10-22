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
    /// Port step 2b's rung R0b (reviews/lt1/port/2b/design.md, The ladder): today's gully mesh, unchanged, shaded with
    /// one change at a time, so the one-pixel lines and specks can be split between the pipeline's (bloom, the shadow
    /// normal bias, SSAO), the stone shader's own terms (GeometricNormalFiltering, a joint value floor, the cut marks)
    /// and the mesh's. Frames at the player's size (PlayerFrame: 2560 by 1440, one sample a pixel, the pipeline's 4x
    /// MSAA, never supersampled), with a mask of the gully's own pixels (stair and cheek walls) per view.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1R0b.Run
    ///         [-moments 1600-low-sun] [-views eye-foot,...] [-configs A,gnf,...] [-out reviews/lt1/port/2b/r0b]
    ///
    /// The pipeline's overrides are made in memory after LT1Stone.Stage (which saves assets) and restored in a finally;
    /// nothing here saves an asset or the scene. The stone's toggles are global floats read by Stone.shader, 0 by default,
    /// inside its OS_R0B blocks (a shader_feature this script alone turns on, for the configs that need it).
    /// </summary>
    public static class LT1R0b
    {
        static readonly string[] Configs =
            { "A", "gnf", "jointfloor", "cutmarks", "bloom-off", "bloom-clamp", "bias02", "ssao-off", "all", "all-clamp",
              "all-flat", "all-onecolour", "all-norelief", "all-nogrowth", "all-onerock", "all-nolichen", "all-nomoss",
              "A2" };

        const float BiasLow = 0.2f, BloomClamp = 2f;

        static readonly int GnfId = Shader.PropertyToID("_OS_R0b_GNF");
        static readonly int FloorId = Shader.PropertyToID("_OS_R0b_JointFloor");
        static readonly int CutId = Shader.PropertyToID("_OS_R0b_CutMarks");
        static readonly int FlatId = Shader.PropertyToID("_OS_R0b_Flat");
        static readonly int KindsId = Shader.PropertyToID("_OS_R0b_Kinds");
        // the shader's arms live behind this keyword (a shader_feature): off, the stone is drawn by the game's own
        // variant, so A, A2 and the pipeline's configs are today's output exactly
        static readonly GlobalKeyword R0bKeyword = GlobalKeyword.Create("OS_R0B");

        /// <summary>
        /// Whether a config has a change: each alone by its name; "all" every one with bloom off (the upper bound),
        /// "all-clamp" with bloom's clamp lowered instead (the realistic proxy), "all-flat" as "all" with the stone one
        /// rock colour and no relief (the mesh alone), "all-onecolour" and "all-norelief" its two halves (the colour
        /// flattened, the relief kept; the relief gone, the colour kept), "all-nogrowth" and "all-onerock" the colour's
        /// two halves (the growth's colour skipped; the rock's own colour one value, growth and streaks kept),
        /// "all-nolichen" and "all-nomoss" the growth's two (lichen gone, moss kept; moss gone, lichen kept); "A2" the
        /// baseline again, last, for the run-to-run noise.
        /// </summary>
        /// <summary>The mesh-alone arm's value in Stone.shader: 1 both halves, 2 the colour alone, 3 the relief alone,
        /// 4 the growth's colour skipped, 5 the rock's own colour one value, 6 lichen gone, 7 moss gone.</summary>
        static float Flat(string config) =>
            config == "all-flat" ? 1f : config == "all-onecolour" ? 2f : config == "all-norelief" ? 3f :
            config == "all-nogrowth" ? 4f : config == "all-onerock" ? 5f : config == "all-nolichen" ? 6f :
            config == "all-nomoss" ? 7f : 0f;

        static bool Has(string config, string what)
        {
            if (config == what)
                return true;
            if (!config.StartsWith("all") || what == "flat" && Flat(config) == 0f)
                return false;
            if (what == "bloom-off")
                return config != "all-clamp";
            if (what == "bloom-clamp")
                return config == "all-clamp";
            return true;
        }

        public static void Run()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance, bias = urp.shadowNormalBias;
            var rendererData = AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/PC_Renderer.asset");
            ScriptableRendererFeature ssao = null;
            foreach (var f in rendererData.rendererFeatures)
                if (f != null && f.GetType().Name.Contains("ScreenSpaceAmbientOcclusion"))
                    ssao = f;
            bool ssaoWas = ssao != null && ssao.isActive;
            string outDir = Cli.RepoPath("-out", "reviews/lt1/port/2b/r0b");
            string configs = Cli.Arg("-configs", null);

            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var white = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "r0b white (never saved)" };
            white.SetColor("_BaseColor", Color.white);
            var black = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "r0b black (never saved)" };
            black.SetColor("_BaseColor", Color.black);
            var log = new List<string>();
            try
            {
                // the gully's own renderers: the stair (and its setts) and the cheek walls
                var gully = new HashSet<Renderer>();
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                    if (r.enabled && r.transform.root.name.StartsWith("stone_gully"))
                        gully.Add(r);
                log.Add($"gully renderers {gully.Count}; shadowNormalBias {bias}; ssao {(ssao != null ? ssaoWas.ToString() : "none")}");

                foreach (var moment in LT1Stone.Moments)
                {
                    if (!Cli.Wanted("-moments", moment))
                        continue;
                    stage.rig = AssetDatabase.LoadAssetAtPath<LightRig>($"Assets/Experiments/LT1/Heart/Light/Heart_{moment}.asset");
                    foreach (var view in LT1Stone.Views)
                    {
                        if (!Cli.Wanted("-views", view.name))
                            continue;
                        LT1Stone.Aim(stage, shot, view);
                        Mask(stage.view, gully, white, black, Path.Combine(outDir, moment, "mask", view.name + ".png"));
                        stage.volume.sharedProfile.TryGet(out Bloom bloom);
                        float intensity = bloom != null ? bloom.intensity.value : 0f;
                        bool clampWas = bloom != null && bloom.clamp.overrideState;
                        float clampValue = bloom != null ? bloom.clamp.value : 0f;
                        foreach (var config in Configs)
                        {
                            if (configs != null && System.Array.IndexOf(configs.Split(','), config) < 0)
                                continue;
                            try
                            {
                                Shader.SetGlobalFloat(GnfId, Has(config, "gnf") ? 1f : 0f);
                                Shader.SetGlobalFloat(FloorId, Has(config, "jointfloor") ? 1f : 0f);
                                Shader.SetGlobalFloat(CutId, Has(config, "cutmarks") ? 1f : 0f);
                                Shader.SetGlobalFloat(FlatId, Flat(config));
                                Shader.SetKeyword(R0bKeyword, Has(config, "gnf") || Has(config, "jointfloor") ||
                                                              Has(config, "cutmarks") || Has(config, "flat"));
                                urp.shadowNormalBias = Has(config, "bias02") ? BiasLow : bias;
                                if (ssao != null)
                                    ssao.SetActive(Has(config, "ssao-off") ? false : ssaoWas);
                                if (bloom != null)
                                {
                                    bloom.intensity.Override(Has(config, "bloom-off") ? 0f : intensity);
                                    if (Has(config, "bloom-clamp"))
                                        bloom.clamp.Override(BloomClamp);
                                    else
                                    {
                                        bloom.clamp.value = clampValue;
                                        bloom.clamp.overrideState = clampWas;
                                    }
                                }
                                string file = Path.Combine(outDir, moment, config, view.name + ".png");
                                using (var frame = new PlayerFrame(stage.view))
                                {
                                    frame.Render(LT1Golden.WarmUp + 1);
                                    frame.Save(file);
                                    if (config == "A")
                                    {
                                        var stack = VolumeManager.instance.stack.GetComponent<Bloom>();
                                        log.Add($"{moment} {view.name}: msaa {frame.Msaa}, bloom intensity {stack.intensity.value}, threshold {stack.threshold.value}, clamp {stack.clamp.value}, hq {stack.highQualityFiltering.value}");
                                    }
                                }
                                Debug.Log($"[LT1R0b] {file}");
                            }
                            finally
                            {
                                Shader.SetGlobalFloat(GnfId, 0f);
                                Shader.SetGlobalFloat(FloorId, 0f);
                                Shader.SetGlobalFloat(CutId, 0f);
                                Shader.SetGlobalFloat(FlatId, 0f);
                                Shader.SetKeyword(R0bKeyword, false);
                                urp.shadowNormalBias = bias;
                                if (ssao != null)
                                    ssao.SetActive(ssaoWas);
                                if (bloom != null)
                                {
                                    bloom.intensity.Override(intensity);
                                    bloom.clamp.value = clampValue;
                                    bloom.clamp.overrideState = clampWas;
                                }
                            }
                        }
                        if (configs == null || System.Array.IndexOf(configs.Split(','), "kinds") >= 0)
                            Kinds(stage.view, rendererData, Path.Combine(outDir, moment, "kinds", view.name + ".png"));
                    }
                }
            }
            finally
            {
                Shader.SetGlobalFloat(GnfId, 0f);
                Shader.SetGlobalFloat(FloorId, 0f);
                Shader.SetGlobalFloat(CutId, 0f);
                Shader.SetGlobalFloat(FlatId, 0f);
                Shader.SetGlobalFloat(KindsId, 0f);
                Shader.SetKeyword(R0bKeyword, false);
                urp.shadowNormalBias = bias;
                urp.shadowDistance = reach;
                if (ssao != null)
                    ssao.SetActive(ssaoWas);
                Directory.CreateDirectory(outDir);
                File.AppendAllLines(Path.Combine(outDir, "run-log.txt"), log);
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
                Object.DestroyImmediate(white);
                Object.DestroyImmediate(black);
            }
        }

        /// <summary>
        /// Each stone pixel's kind (UV2 x: 0 top, 1 rounded edge, 2 split face, 3 bed, 4 pointing, 5 dab, 6 joint soil)
        /// in red as kind / 8, its piece's seed in green (one value over a stone: its outline is where it changes) and
        /// its baked ground light in blue, linear; written through the sRGB
        /// target with post-processing and every renderer feature off (all restored after).
        /// </summary>
        static void Kinds(Camera cam, UniversalRendererData rendererData, string file)
        {
            var data = cam.GetUniversalAdditionalCameraData();
            bool post = data.renderPostProcessing;
            var was = new Dictionary<ScriptableRendererFeature, bool>();
            try
            {
                foreach (var f in rendererData.rendererFeatures)
                    if (f != null)
                    {
                        was[f] = f.isActive;
                        f.SetActive(false);
                    }
                data.renderPostProcessing = false;
                Shader.SetGlobalFloat(KindsId, 1f);
                Shader.SetKeyword(R0bKeyword, true);
                using (var frame = new PlayerFrame(cam))
                {
                    frame.Render(2);
                    frame.Save(file);
                }
            }
            finally
            {
                Shader.SetGlobalFloat(KindsId, 0f);
                Shader.SetKeyword(R0bKeyword, false);
                foreach (var kv in was)
                    kv.Key.SetActive(kv.Value);
                data.renderPostProcessing = post;
            }
        }

        /// <summary>
        /// The gully's pixels: every renderer drawn unlit black, the gully's white in one render and black in the other,
        /// post-processing off and a black background; written as the two renders' difference (the glows of the
        /// renderer features cancel). Occluders in front of the gully stay in place.
        /// </summary>
        static void Mask(Camera cam, HashSet<Renderer> gully, Material white, Material black, string file)
        {
            var saved = new Dictionary<Renderer, Material[]>();
            var data = cam.GetUniversalAdditionalCameraData();
            bool post = data.renderPostProcessing;
            var clear = cam.clearFlags;
            var bg = cam.backgroundColor;
            try
            {
                foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    saved[r] = r.sharedMaterials;
                    var mats = new Material[r.sharedMaterials.Length];
                    for (int i = 0; i < mats.Length; i++)
                        mats[i] = gully.Contains(r) ? white : black;
                    r.sharedMaterials = mats;
                }
                data.renderPostProcessing = false;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = Color.black;
                Texture2D on, off;
                using (var frame = new PlayerFrame(cam))
                {
                    frame.Render(2);
                    on = Object.Instantiate(frame.Read());
                    foreach (var r in gully)
                    {
                        var mats = new Material[r.sharedMaterials.Length];
                        for (int i = 0; i < mats.Length; i++)
                            mats[i] = black;
                        r.sharedMaterials = mats;
                    }
                    frame.Render(2);
                    off = frame.Read();
                    var a = on.GetPixels32();
                    var b = off.GetPixels32();
                    for (int i = 0; i < a.Length; i++)
                    {
                        int d = Mathf.Max(a[i].r - b[i].r, Mathf.Max(a[i].g - b[i].g, a[i].b - b[i].b));
                        byte m = (byte)(d > 64 ? 255 : 0);
                        a[i] = new Color32(m, m, m, 255);
                    }
                    on.SetPixels32(a);
                    on.Apply();
                    Directory.CreateDirectory(Path.GetDirectoryName(file));
                    File.WriteAllBytes(file, on.EncodeToPNG());
                    Object.DestroyImmediate(on);
                }
            }
            finally
            {
                foreach (var kv in saved)
                    if (kv.Key != null)
                        kv.Key.sharedMaterials = kv.Value;
                data.renderPostProcessing = post;
                cam.clearFlags = clear;
                cam.backgroundColor = bg;
            }
        }
    }
}
