using UnityEngine;

namespace Overstory.Scenes
{
    /// <summary>
    /// A mood: how a scene is filmed, laid over the light the world gives it and the game's style. The stage grades in
    /// four layers, each with one owner: exposure (from the light rig: the eye adjusting to the hour), the hour's
    /// balance (the rig's grade), the mood (this), and the lens. A mood moves only exposure, contrast and how much colour
    /// the shade keeps, and the lens (grain, vignette, glow): never the hue of a light, and nothing that reads as
    /// weather (thicker fog, blacks lifted into haze). So it can never change a fact; it only chooses how what is there
    /// is seen, as a cinematographer does. (docs/visual-direction.md, Mood.)
    /// </summary>
    [CreateAssetMenu(menuName = "Overstory/Grade (mood)")]
    public class Grade : ScriptableObject
    {
        [TextArea] public string intent;

        [Header("Exposure and contrast (added to the hour's)")]
        public float exposure = 0f;
        [Range(-100, 100)] public float contrast = 0f;

        [Header("Shade")]
        [Tooltip("How much colour the darkest tones keep (1 all of it): drained shade reads sad, rich shade grand.")]
        [Range(0, 1.5f)] public float shadowSaturation = 1f;

        [Header("Lens")]
        [Range(0, 1)] public float vignette = 0f;
        [Range(0.01f, 1)] public float vignetteSmoothness = 0.45f;
        [Range(0, 1)] public float grain = 0f;
        [Tooltip("Added to the hour's glow round bright light.")]
        public float bloom = 0f;
        [Range(0, 1)] public float bloomScatter = 0.7f;
    }
}
