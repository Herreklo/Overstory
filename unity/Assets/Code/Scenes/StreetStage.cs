using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Assembly;
using Overstory.World;

namespace Overstory.Scenes
{
    /// <summary>
    /// Puts a street under one light and behind one camera: applies a light rig (sun, sky, ambient,
    /// air, rain, lit windows and lamps, grade) and a camera shot. The street itself is the builder's;
    /// the stage only lights and frames it, so looks and lights can be compared on the same geometry.
    /// </summary>
    [ExecuteAlways]
    public class StreetStage : MonoBehaviour
    {
        public StreetBuilder street;
        public Light sun;
        public Camera view;
        public Volume volume;
        public Material sky;

        [Header("The shared palette")]
        public Texture2D paletteAlbedo;
        public Texture2D paletteEmit;
        public Texture2D paletteGlow;
        public Texture2D paletteSurface;

        [Header("What is shown")]
        public LightRig rig;
        public CameraShot shot;
        [Tooltip("Every surface one matte grey: shape, light and composition alone.")]
        public bool clay;
        [Tooltip("Which look draws the street: A plain URP Lit (control), B the painted ramp.")]
        public string look = "A";

        [Header("Look B, the painted ramp")]
        public float rampEdge = 0.5f;
        public float rampSoftness = 0.07f;
        public float shadowFloor = 0.0f;
        public float stroke = 0.06f;
        public Color edgeTint = new Color(0.9f, 0.45f, 0.25f, 0.25f);
        public float rim = 0.25f;

        VolumeProfile profile;

        // the light each kind of lamp gives (sRGB): incandescent, mercury vapour, high-pressure sodium
        static readonly Color Warm = new Color(1.0f, 0.74f, 0.48f);
        static readonly Color Mercury = new Color(0.78f, 0.92f, 0.94f);
        static readonly Color Sodium = new Color(1.0f, 0.62f, 0.27f);

        void OnEnable() => Apply();

        void OnValidate()
        {
            if (isActiveAndEnabled)
                Apply();
        }

        void OnDisable()
        {
            if (profile != null)
                DestroyImmediate(profile);
            profile = null;
        }

        public void Apply()
        {
            if (street != null && !street.Built)
                street.Build();
            SetPalette();
            Shader.SetGlobalFloat("_OS_Clay", clay ? 1f : 0f);
            if (look == "B") Shader.EnableKeyword("_OS_LOOK_B"); else Shader.DisableKeyword("_OS_LOOK_B");
            Shader.SetGlobalVector("_OS_Ramp", new Vector4(rampEdge, rampSoftness, shadowFloor, stroke));
            Shader.SetGlobalVector("_OS_EdgeTint", new Vector4(edgeTint.linear.r, edgeTint.linear.g, edgeTint.linear.b, edgeTint.a));
            if (rig != null)
                SetLight(rig);
            if (shot != null && view != null)
                shot.Apply(view);
        }

        void SetPalette()
        {
            if (paletteAlbedo) Shader.SetGlobalTexture("_OS_Albedo", paletteAlbedo);
            if (paletteEmit) Shader.SetGlobalTexture("_OS_Emit", paletteEmit);
            if (paletteGlow) Shader.SetGlobalTexture("_OS_Glow", paletteGlow);
            if (paletteSurface) Shader.SetGlobalTexture("_OS_Surface", paletteSurface);
            if (street != null && street.Layout != null)
                Shader.SetGlobalVector("_OS_PavingMeanUV", new Palette(street.Layout.palette).UV("setts_mean"));
        }

        static Vector4 Linear(Color c) => (Vector4)c.linear;

        void SetLight(LightRig r)
        {
            Vector3 toSun = StreetSpace.ToUnity(r.SunDirectionStreet).normalized;

            if (sun != null)
            {
                sun.type = LightType.Directional;
                sun.transform.rotation = Quaternion.LookRotation(-toSun, Vector3.up);
                sun.color = r.sunColour;
                sun.intensity = r.sunIntensity;
                sun.shadows = LightShadows.Soft;
                sun.shadowStrength = r.shadowStrength;
                RenderSettings.sun = sun;
            }

            if (sky != null)
            {
                sky.SetColor("_Zenith", r.zenith);
                sky.SetColor("_Horizon", r.horizon);
                sky.SetColor("_Below", r.belowHorizon);
                sky.SetFloat("_Curve", r.skyCurve);
                sky.SetColor("_SunGlow", r.sunGlow);
                sky.SetFloat("_SunGlowPower", r.sunGlowPower);
                RenderSettings.skybox = sky;
            }

            RenderSettings.fog = false; // the air is our own (OS_Atmosphere), the same for every look
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = r.ambientSky * r.ambientIntensity;
            RenderSettings.ambientEquatorColor = r.ambientEquator * r.ambientIntensity;
            RenderSettings.ambientGroundColor = r.ambientGround * r.ambientIntensity;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            DynamicGI.UpdateEnvironment();

            Shader.SetGlobalVector("_OS_SunDir", toSun);
            // the shared sky term: the rig's hemisphere light, in linear light
            Shader.SetGlobalVector("_OS_SkyAmb", Linear(r.ambientSky) * r.ambientIntensity);
            Shader.SetGlobalVector("_OS_HorizonAmb", Linear(r.ambientEquator) * r.ambientIntensity);
            Shader.SetGlobalVector("_OS_GroundAmb", Linear(r.ambientGround) * r.ambientIntensity);
            var sky = Linear(r.ambientSky);
            Shader.SetGlobalVector("_OS_Rim", new Vector4(sky.x, sky.y, sky.z, rim));
            // until rigs carry a far air colour, the far air is the near air
            var near = Linear(r.fogColour);
            Shader.SetGlobalVector("_OS_FogFar", new Vector4(near.x, near.y, near.z, 1e6f));
            Shader.SetGlobalFloat("_OS_Wetness", r.wetness);
            Shader.SetGlobalFloat("_OS_WindowGlow", r.windowGlow);
            Shader.SetGlobalFloat("_OS_LampGlow", r.lampsOn ? r.lampGlow : 0f);
            Shader.SetGlobalFloat("_OS_Time", r.clock);
            Shader.SetGlobalVector("_OS_FogColor", Linear(r.fogColour));
            Shader.SetGlobalVector("_OS_FogParams", new Vector4(r.fogDensity, r.fogHeightFalloff, r.fogBaseHeight, r.fogMaxOpacity));
            var fs = Linear(r.fogSunColour);
            Shader.SetGlobalVector("_OS_FogSun", new Vector4(fs.x, fs.y, fs.z, r.fogSunPower));

            if (street != null)
            {
                foreach (var (light, kind) in street.LampLights)
                {
                    light.enabled = r.lampsOn;
                    light.intensity = r.lampIntensity;
                    light.color = kind == "sodium" ? Sodium : kind == "mercury" ? Mercury : Warm;
                }
            }

            if (volume != null)
                SetGrade(r);
        }

        void SetGrade(LightRig r)
        {
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                profile.name = "stage grade (generated)";
                profile.hideFlags = HideFlags.DontSave;
            }
            volume.isGlobal = true;
            volume.sharedProfile = profile;

            var tone = Get<Tonemapping>();
            tone.mode.Override(TonemappingMode.Neutral);

            var adj = Get<ColorAdjustments>();
            adj.postExposure.Override(r.postExposure);
            adj.contrast.Override(r.contrast);
            adj.saturation.Override(r.saturation);
            adj.colorFilter.Override(r.colourFilter);

            var wb = Get<WhiteBalance>();
            wb.temperature.Override(r.temperature);
            wb.tint.Override(r.tint);

            var bloom = Get<Bloom>();
            bloom.intensity.Override(r.bloomIntensity);
            bloom.threshold.Override(r.bloomThreshold);
            bloom.highQualityFiltering.Override(true);

#if URP_SCREEN_SPACE_REFLECTION
            var ssr = Get<ScreenSpaceReflectionVolumeSettings>();
            ssr.mode.Override(ScreenSpaceReflectionVolumeSettings.ReflectionMode.OpaquesOnly);
            ssr.reflectionStrength.Override(r.reflectionStrength);
            ssr.minimumSmoothness.Override(0.5f);
            ssr.smoothnessFadeStart.Override(0.6f);
#endif
        }

        T Get<T>() where T : VolumeComponent
        {
            if (!profile.TryGet(out T c))
                c = profile.Add<T>(true);
            c.active = true;
            return c;
        }
    }
}
