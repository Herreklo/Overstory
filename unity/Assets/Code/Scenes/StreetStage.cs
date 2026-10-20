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
        [Tooltip("The town's sky map: how much sky each point of the town sees. Optional.")]
        public SkyMap skyMap;
        [Tooltip("A probe that sees only the sky, captured again whenever the light changes, so water and wet stone reflect this hour's sky. Optional.")]
        public ReflectionProbe skyReflection;

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

        [Header("Look D, the woodblock print")]
        [Tooltip("Exposure stops per ink plate: larger is fewer, broader plates.")]
        public float stopsPerPlate = 1.1f;
        [Tooltip("How far the world-fixed carving breaks a plate's edge, in plates.")]
        public float carving = 0f;
        [Tooltip("Spacing of the white-line carving in the darks, in metres, close by.")]
        public float whiteLineSpacing = 0.45f;
        public float whiteLines = 0f;
        [Tooltip("The key block's ink: indigo, never black.")]
        public Color ink = new Color(0.11f, 0.12f, 0.22f, 0.85f);
        public float inkFadeStart = 60f, inkFadeEnd = 450f;
        public float airBands = 5f, skyBands = 7f;
        [Tooltip("How strongly shade takes the sky's colour in look D: 1 as the light gives it, more is richer.")]
        public float shadowChroma = 1.7f;

        [Header("Look P, painterly realism")]
        [Tooltip("How far light wraps round a form: soft as a painter models it.")]
        public float wrap = 0.4f;
        [Tooltip("How far the base colours are muted towards grey, so the light carries the colour.")]
        public float muting = 0.3f;
        [Tooltip("How much dirt and damp gather where a surface sees the ground.")]
        public float grime = 0.6f;
        public Color grimeColour = new Color(0.62f, 0.58f, 0.5f);
        [Tooltip("How strongly the world-fixed brushwork breaks colour and light.")]
        public float brush = 0.5f;
        public float paintShadowChroma = 1.3f;

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
            if (look == "D") Shader.EnableKeyword("_OS_LOOK_D"); else Shader.DisableKeyword("_OS_LOOK_D");
            if (look == "P") Shader.EnableKeyword("_OS_LOOK_P"); else Shader.DisableKeyword("_OS_LOOK_P");
            Shader.SetGlobalVector("_OS_Paint", new Vector4(wrap, muting, grime, brush));
            var g = grimeColour.linear;
            Shader.SetGlobalVector("_OS_Grime", new Vector4(g.r, g.g, g.b, 1f));
            bool print = look == "D";
            Shader.SetGlobalFloat("_OS_KeyBlock", print ? 1f : 0f);
            Shader.SetGlobalFloat("_OS_AirBands", print ? airBands : 0f);
            Shader.SetGlobalFloat("_OS_SkyBands", print ? skyBands : 0f);
            Shader.SetGlobalVector("_OS_Plates", new Vector4(stopsPerPlate, carving, whiteLineSpacing, whiteLines));
            var inkLinear = ink.linear;
            Shader.SetGlobalVector("_OS_Ink", new Vector4(inkLinear.r, inkLinear.g, inkLinear.b, ink.a));
            Shader.SetGlobalVector("_OS_InkFade", new Vector4(inkFadeStart, inkFadeEnd, 0, 0));
            Shader.SetGlobalFloat("_OS_ShadowChroma", look == "P" ? paintShadowChroma : shadowChroma);
            Shader.SetGlobalVector("_OS_Ramp", new Vector4(rampEdge, rampSoftness, shadowFloor, stroke));
            Shader.SetGlobalVector("_OS_EdgeTint", new Vector4(edgeTint.linear.r, edgeTint.linear.g, edgeTint.linear.b, edgeTint.a));
            if (rig != null)
                SetLight(rig);
            if (shot != null && view != null)
                shot.Apply(view);
            SetShafts();
        }

        /// <summary>Where the sun stands on screen, for the light rays; they are off when it is behind the camera.</summary>
        void SetShafts()
        {
            if (rig == null || view == null)
                return;
            Vector3 toSun = StreetSpace.ToUnity(rig.SunDirectionStreet).normalized;
            Vector3 vp = view.WorldToViewportPoint(view.transform.position + toSun * 5000f);
            bool ahead = vp.z > 0f && rig.shafts > 0f;
            Shader.SetGlobalVector("_OS_SunScreen", new Vector4(vp.x, vp.y, ahead ? 1f : 0f, 0f));
            Shader.SetGlobalVector("_OS_Shafts", new Vector4(rig.shafts, rig.shaftReach, rig.shaftDecay, rig.shaftThreshold));
            var c = Linear(rig.sunColour);
            Shader.SetGlobalVector("_OS_ShaftColour", new Vector4(c.x, c.y, c.z, 1f));
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
            r.SetSunFromClock();
            if (skyMap != null)
                skyMap.Bind();
            else
                Shader.SetGlobalFloat("_OS_SkyMapOn", 0f);
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
                sky.SetColor("_AntiGlow", r.antiGlow);
                sky.SetFloat("_HighCloud", r.highCloud);
                RenderSettings.skybox = sky;
            }
            if (skyReflection != null)
            {
                skyReflection.mode = ReflectionProbeMode.Realtime;
                skyReflection.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                skyReflection.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
                skyReflection.cullingMask = 0; // the sky alone
                skyReflection.clearFlags = ReflectionProbeClearFlags.Skybox;
                skyReflection.RenderProbe();
            }

            RenderSettings.fog = false; // the air is our own (OS_Atmosphere), the same for every look
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = r.ambientSky * r.ambientIntensity;
            RenderSettings.ambientEquatorColor = r.ambientEquator * r.ambientIntensity;
            RenderSettings.ambientGroundColor = r.ambientGround * r.ambientIntensity;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            DynamicGI.UpdateEnvironment();

            Shader.SetGlobalVector("_OS_SunDir", toSun);
            Shader.SetGlobalVector("_OS_SunCol", Linear(r.sunColour) * Mathf.Clamp(r.sunIntensity, 0.45f, 1.4f));
            // the shared sky term: the rig's hemisphere light, in linear light
            Shader.SetGlobalVector("_OS_SkyAmb", Linear(r.ambientSky) * r.ambientIntensity);
            Shader.SetGlobalVector("_OS_HorizonAmb", Linear(r.ambientEquator) * r.ambientIntensity);
            Shader.SetGlobalVector("_OS_GroundAmb", Linear(r.ambientGround) * r.ambientIntensity);
            var side = Linear(r.ambientSunSide) * r.ambientIntensity;
            Shader.SetGlobalVector("_OS_SunSideAmb", new Vector4(side.x, side.y, side.z, r.ambientSunSide.a > 0f ? 1f : 0f));
            Shader.SetGlobalVector("_OS_TownBounce", Linear(r.townBounce) * r.ambientIntensity);
            var skyLight = Linear(r.ambientSky);
            Shader.SetGlobalVector("_OS_Rim", new Vector4(skyLight.x, skyLight.y, skyLight.z, rim));
            // the air far off; a rig without a far distance keeps one colour of air
            bool layered = r.fogFarDistance > 0f;
            var far = Linear(layered ? r.fogFarColour : r.fogColour);
            Shader.SetGlobalVector("_OS_FogFar", new Vector4(far.x, far.y, far.z, layered ? r.fogFarDistance : 1e6f));
            bool middle = r.fogMidDistance > 0f;
            var mid = Linear(middle ? r.fogMidColour : r.fogColour);
            Shader.SetGlobalVector("_OS_FogMid", new Vector4(mid.x, mid.y, mid.z, middle ? r.fogMidDistance : 1f));
            Shader.SetGlobalFloat("_OS_Wetness", r.wetness);
            Shader.SetGlobalFloat("_OS_WindowGlow", r.windowGlow);
            Shader.SetGlobalFloat("_OS_LampGlow", r.lampsOn ? r.lampGlow : 0f);
            Shader.SetGlobalFloat("_OS_Time", r.clock);
            Shader.SetGlobalVector("_OS_Clouds", new Vector4(r.cloudCover, r.cloudSize, r.cloudSoftness, r.cloudHeight));
            Shader.SetGlobalVector("_OS_CloudDrift", Vector4.zero); // the wind will move it, from the clock
            Shader.SetGlobalVector("_OS_FogColor", Linear(r.fogColour));
            Shader.SetGlobalVector("_OS_FogParams", new Vector4(r.fogDensity, r.fogHeightFalloff, r.fogBaseHeight, r.fogMaxOpacity));
            var hz = Linear(r.hazeColour);
            Shader.SetGlobalVector("_OS_HazeColor", new Vector4(hz.x, hz.y, hz.z, 1f));
            Shader.SetGlobalVector("_OS_Haze", new Vector4(r.hazeDensity, r.hazeHeight, 0f, 0f));
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
                foreach (var light in street.SpillLights)
                {
                    light.enabled = r.windowSpill > 0f;
                    light.intensity = r.windowSpill;
                    light.color = new Color(1.0f, 0.72f, 0.42f);
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
