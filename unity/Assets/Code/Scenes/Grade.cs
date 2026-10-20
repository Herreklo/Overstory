using UnityEngine;

namespace Overstory.Scenes
{
    /// <summary>
    /// A mood: how a scene is filmed, laid over the light the world gives it. The stage grades in four layers, each
    /// with one owner: exposure (from the light rig: the eye adjusting to the hour), the hour's balance (the rig's
    /// grade), the mood (this), and the lens (grain, glow, vignette). A mood never changes a fact: it cannot make night
    /// day, fog clear or a lit window dark; it only chooses how what is there is seen. Values are offsets on the
    /// hour's grade unless they say otherwise. (docs/experiments.md, LT1, blue hour in sea fog.)
    /// </summary>
    [CreateAssetMenu(menuName = "Overstory/Grade (mood)")]
    public class Grade : ScriptableObject
    {
        [TextArea] public string intent;

        [Header("Exposure and tone (added to the hour's)")]
        public float exposure = 0f;
        [Range(-100, 100)] public float contrast = 0f;
        [Tooltip("Lift (shadows), gamma (midtones), gain (highlights): rgb tint, w the shift. Neutral is (1, 1, 1, 0).")]
        public Vector4 lift = new Vector4(1, 1, 1, 0), gamma = new Vector4(1, 1, 1, 0), gain = new Vector4(1, 1, 1, 0);

        [Header("Colour (added to the hour's)")]
        [Range(-100, 100)] public float saturation = 0f;
        [Range(-100, 100)] public float temperature = 0f;
        [Range(-100, 100)] public float tint = 0f;
        [Tooltip("Multiplied with the hour's filter.")]
        public Color filter = Color.white;
        [Tooltip("Split toning: the colour pushed into the shadows and into the highlights; grey is none.")]
        public Color splitShadows = Color.grey, splitHighlights = Color.grey;
        [Range(-100, 100)] public float splitBalance = 0f;
        [Tooltip("How much colour the darkest tones keep (1 all of it): the eye sees little colour in the dark.")]
        [Range(0, 1.5f)] public float shadowSaturation = 1f;

        [Header("Lens")]
        [Range(0, 1)] public float vignette = 0f;
        [Range(0.01f, 1)] public float vignetteSmoothness = 0.45f;
        public Color vignetteColour = Color.black;
        [Range(0, 1)] public float grain = 0f;
        [Tooltip("Added to the hour's glow round bright light.")]
        public float bloom = 0f;
        [Range(0, 1)] public float bloomScatter = 0.7f;
    }
}
