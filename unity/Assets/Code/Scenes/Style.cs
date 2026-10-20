using UnityEngine;

namespace Overstory.Scenes
{
    /// <summary>
    /// The house style: how far colour, value and air are pushed beyond the light the world gives, after the masters of
    /// colour (docs/research/masters-of-colour.md). It sits between the hour's grade and the mood: one style for the
    /// game, chosen by look tests; the mood then moves within it. A style never stylises a fact away: the ramp of colour
    /// by value spares saturated light (a lit window stays warm, a red sign red), and the hour and weather still read.
    /// </summary>
    [CreateAssetMenu(menuName = "Overstory/Style")]
    public class Style : ScriptableObject
    {
        [TextArea] public string intent;

        [Header("Colour by value (a designed ramp, blended over the scene, light kept)")]
        public Color shade = new Color(0.10f, 0.11f, 0.20f);
        public Color lowMiddle = new Color(0.26f, 0.30f, 0.40f);
        public Color highMiddle = new Color(0.66f, 0.62f, 0.56f);
        public Color light = new Color(1.0f, 0.92f, 0.76f);
        [Range(0, 1)] public float ramp = 0f;
        [Tooltip("How far the ramp takes its hues from the hour's own light (the sky's colour in shade, the sun's or the " +
                 "lamps' in light) rather than its own: a style pushes the hour's colours, it does not replace them.")]
        [Range(0, 1)] public float followLight = 0.6f;
        [Tooltip("How much saturated colour (lamps, lit windows, signs) is spared the ramp.")]
        [Range(0, 1)] public float spare = 0.8f;

        [Header("Values in masses")]
        [Tooltip("How many value groups the frame is pulled towards; 0 none.")]
        public int valueSteps = 0;
        [Range(0, 1)] public float grouping = 0f;
        [Range(0.02f, 1)] public float groupSoftness = 0.3f;

        [Header("Air in layers")]
        [Tooltip("How many flat layers the air steps back in; 0 smooth.")]
        public int airLayers = 0;
        [Range(0.02f, 1)] public float airLayerSoftness = 0.3f;

        [Header("Light and shade")]
        [Tooltip("Multiplies how strongly shade takes the sky's colour.")]
        public float shadeChroma = 1f;
        [Tooltip("The warm, saturated band where light turns into shade.")]
        public Color turningEdge = new Color(0.9f, 0.45f, 0.25f);
        [Range(0, 1)] public float turningEdgeStrength = 0.25f;

        [Header("Film")]
        [Tooltip("Colour added in the middle values.")]
        [Range(-1, 1)] public float vibrance = 0f;
        [Tooltip("Colour taken away towards black and white, as print film does.")]
        [Range(0, 1)] public float rolloff = 0f;
        public Color glowTint = Color.white;
        public float glow = 0f;

        [Header("Grade (added to the hour's)")]
        public float exposure = 0f;
        [Range(-100, 100)] public float contrast = 0f;
        [Range(-100, 100)] public float saturation = 0f;
    }
}
