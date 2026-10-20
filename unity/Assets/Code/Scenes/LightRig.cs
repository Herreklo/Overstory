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
        [Header("When and where (the sun is set from these when the clock is on)")]
        [Tooltip("Set the sun from the date, the local hour and the place, never by hand.")]
        public bool sunFromClock = false;
        public int year = 1989, month = 10, day = 20;
        [Tooltip("Local clock time in hours, e.g. 16.5 for half past four.")]
        public float hour = 16f;
        [Tooltip("Hours the local clock is ahead of UTC on that date (Norway 1989: +1 in winter time, +2 in summer time).")]
        public float utcOffset = 1f;
        public float latitude = 58.97f, longitude = 5.73f;
        [Tooltip("The compass bearing of the street's +x axis, so the sun can be given in street axes.")]
        public float streetAxisCompass = 190f;

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
        [Tooltip("What the horizon on the sun's side gives a wall that faces it; the equator colour is the side away. Clear: the same all round.")]
        public Color ambientSunSide = Color.clear;
        [Tooltip("What the town's own walls and ground give back into its lanes and yards, in place of the sky they hide.")]
        public Color townBounce = new Color(0.3f, 0.3f, 0.3f);
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
        [Tooltip("The colour of the low haze that lies on the water and thins up the hill.")]
        public Color hazeColour = new Color(0.8f, 0.8f, 0.8f);
        [Tooltip("Optical density of the haze per metre at sea level. 0: none.")]
        public float hazeDensity = 0f;
        [Tooltip("The height in metres over which the haze thins to a third.")]
        public float hazeHeight = 20f;
        [Tooltip("The haze lies as a bank: thick over the water, thinner over land, broken by wisps.")]
        public bool fogBank = false;
        [Tooltip("The bank's density over land against over water.")]
        [Range(0, 1)] public float bankOverLand = 0.35f;
        [Range(0, 1)] public float bankWisps = 0.45f;
        [Tooltip("The size of a wisp, in metres.")]
        public float bankWispSize = 140f;
        [Tooltip("How strongly the town's lamps and lit shops glow in the fog over the streets.")]
        public float townGlow = 0f;
        [Tooltip("How high that glow reaches into the fog, in metres.")]
        public float townGlowHeight = 25f;
        [Tooltip("For the sun's beams: how much more the air scatters than it hides (dust, humidity; a cinematographer's haze).")]
        public float beamHaze = 1f;

        [Header("Light rays")]
        [Tooltip("How strongly the sky's light streams past what stands against it, looking towards the sun.")]
        public float shafts = 0f;
        [Range(0.1f, 1f)] public float shaftReach = 0.6f;
        [Range(0.9f, 1f)] public float shaftDecay = 0.965f;
        [Tooltip("Motes in the air (dust in sunbeams, mist round lamps): how bright; 0 none.")]
        public float motes = 0f;
        [Tooltip("The size of a mote in metres.")]
        public float moteSize = 0.004f;
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
        [Tooltip("A high, thin layer (cirrus): it casts no shadow but catches a low sun.")]
        [Range(0, 1)] public float highCloud = 0f;
        [Tooltip("The glow low in the sky opposite a low sun (the belt of Venus).")]
        public Color antiGlow = Color.black;

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
        [Tooltip("How strongly each lamp lights the air round it (its halo in fog); 0 none.")]
        public float lampHalo = 1f;

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

        /// <summary>When the clock is on, sets the sun's bearing (in street axes) and elevation from the date, hour and place.</summary>
        public void SetSunFromClock()
        {
            if (!sunFromClock)
                return;
            var (azimuth, elevation) = Daylight.Sun(year, month, day, hour, utcOffset, latitude, longitude);
            // street bearings run from +x towards +y; on the compass that is anticlockwise from the +x axis's bearing
            sunBearing = Mathf.Repeat(streetAxisCompass - (float)azimuth, 360f);
            sunElevation = (float)elevation;
        }

        void OnValidate() => SetSunFromClock();

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
