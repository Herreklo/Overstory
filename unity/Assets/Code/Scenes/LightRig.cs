using UnityEngine;

namespace Overstory.Scenes
{
    /// <summary>
    /// One light for a street: the sun, the sky, the ambient light, the air, the rain, the lit windows
    /// and lamps, and the grade. Every look is shown under the same rigs; only the shading differs.
    /// Colours are as an artist picks them (sRGB); the stage converts them for the shaders.
    /// </summary>
    [CreateAssetMenu(menuName = "Overstory/Light rig")]
    public class LightRig : ScriptableObject
    {
        [Header("Sun")]
        [Tooltip("Compass bearing of the sun in degrees, measured in street axes: 0 along the street (+x), 90 towards the back of the plots (+y).")]
        public float sunBearing = 200f;
        [Range(-10, 90)] public float sunElevation = 35f;
        public Color sunColour = Color.white;
        public float sunIntensity = 1f;
        [Range(0, 1)] public float shadowStrength = 1f;

        [Header("Sky")]
        public Color zenith = new Color(0.55f, 0.6f, 0.66f);
        public Color horizon = new Color(0.7f, 0.73f, 0.76f);
        public Color belowHorizon = new Color(0.3f, 0.32f, 0.32f);
        [Range(0.2f, 4f)] public float skyCurve = 0.6f;
        public Color sunGlow = Color.black;
        public float sunGlowPower = 8f;

        [Header("Ambient (from the sky, the horizon and the ground)")]
        public Color ambientSky = new Color(0.6f, 0.64f, 0.7f);
        public Color ambientEquator = new Color(0.55f, 0.57f, 0.6f);
        public Color ambientGround = new Color(0.3f, 0.31f, 0.3f);
        public float ambientIntensity = 1f;

        [Header("Air")]
        [Tooltip("The colour of the air. Usually the horizon's.")]
        public Color fogColour = new Color(0.7f, 0.73f, 0.76f);
        [Tooltip("The colour of the air at middle distance (a layer of its own, as in Firewatch). Used when the middle distance is set.")]
        public Color fogMidColour = new Color(0.7f, 0.73f, 0.76f);
        public float fogMidDistance = 0f;
        [Tooltip("The colour the air turns to far off, so distance reads in layers. Used when the far distance is set.")]
        public Color fogFarColour = new Color(0.7f, 0.73f, 0.76f);
        [Tooltip("The distance in metres at which the far colour has taken over. 0 keeps one colour of air.")]
        public float fogFarDistance = 0f;
        [Tooltip("Optical density per metre at the base height.")]
        public float fogDensity = 0.003f;
        [Tooltip("How fast the air thins with height, per metre.")]
        public float fogHeightFalloff = 0.02f;
        public float fogBaseHeight = 0f;
        [Range(0, 1)] public float fogMaxOpacity = 0.9f;
        public Color fogSunColour = Color.black;
        public float fogSunPower = 8f;

        [Header("Light rays")]
        [Tooltip("How strongly the sky's light streams past what stands against it, looking towards the sun.")]
        public float shafts = 0f;
        [Range(0.1f, 1f)] public float shaftReach = 0.6f;
        [Range(0.9f, 1f)] public float shaftDecay = 0.965f;
        [Tooltip("How bright the sky must be to cast rays.")]
        public float shaftThreshold = 0.5f;

        [Header("Weather")]
        [Range(0, 1)] public float wetness = 0f;
        [Tooltip("How much of the sky the clouds cover, as their shadows on the town: 0 none, 1 overcast.")]
        [Range(0, 1)] public float cloudCover = 0f;
        [Tooltip("The size of a cloud's shadow, in metres.")]
        public float cloudSize = 160f;
        [Range(0.01f, 0.5f)] public float cloudSoftness = 0.08f;
        public float cloudHeight = 900f;

        [Header("Lit windows and lamps")]
        [Tooltip("Brightness of lit windows, open shopfronts and light-box signs. 0 by day.")]
        public float windowGlow = 0f;
        public bool lampsOn = false;
        [Tooltip("Brightness of the lamps' glass while they are on.")]
        public float lampGlow = 0f;
        [Tooltip("Intensity of the light each lamp casts while on.")]
        public float lampIntensity = 0f;
        [Tooltip("Intensity of the warm light a lit room spills through its windows onto what is in front.")]
        public float windowSpill = 0f;

        [Header("Grade")]
        public float postExposure = 0f;
        [Range(-100, 100)] public float contrast = 0f;
        [Range(-100, 100)] public float saturation = 0f;
        [Range(-100, 100)] public float temperature = 0f;
        [Range(-100, 100)] public float tint = 0f;
        public Color colourFilter = Color.white;
        public float bloomIntensity = 0f;
        public float bloomThreshold = 1f;
        [Range(0, 1)] public float reflectionStrength = 1f;

        [Header("Clock")]
        [Tooltip("The scene's own clock for moving water, in seconds. Fixed per rig so a still is repeatable.")]
        public float clock = 0f;

        /// <summary>Unit vector towards the sun, in street axes (x along, y back, z up).</summary>
        public Vector3 SunDirectionStreet
        {
            get
            {
                float b = sunBearing * Mathf.Deg2Rad, e = sunElevation * Mathf.Deg2Rad;
                return new Vector3(Mathf.Cos(e) * Mathf.Cos(b), Mathf.Cos(e) * Mathf.Sin(b), Mathf.Sin(e));
            }
        }
    }
}
