using UnityEngine;

namespace Overstory.World
{
    /// <summary>
    /// The setting pack's thin growth (docs/nature.md, Growth on surfaces): which lichen and moss grow on the town's
    /// surfaces, their pigments (as the eye sees them) and how fast they grow, set once for the whole town as shader
    /// globals that every surface's shader draws through Growth.hlsl. The first pack, the Norwegian west coast: map
    /// and other crustose lichens, pale grey-white, growing about 0.7 mm a year (Matthews 2005; docs/research/stone.md);
    /// wall and pavement mosses (Grimmia, Tortula). Where and for how long are each surface's own facts.
    /// </summary>
    public static class GrowthPack
    {
        public static Color Lichen = new Color(0.74f, 0.74f, 0.68f);
        public static Color LichenOld = new Color(0.56f, 0.58f, 0.51f);
        /// <summary>x growth (m a year), y the size of a patch (m), z how much of a quiet surface it takes.</summary>
        public static Vector4 LichenRate = new Vector4(0.0007f, 0.11f, 0.85f, 0f);
        public static Color Moss = new Color(0.44f, 0.54f, 0.16f);     // wet moss on this coast: a bright yellow-green
        public static Color MossOld = new Color(0.40f, 0.40f, 0.18f);

        /// <summary>Set the pack's growth for every shader in the town.</summary>
        public static void Apply()
        {
            Shader.SetGlobalColor("_OS_Lichen", Lichen.linear);
            Shader.SetGlobalColor("_OS_LichenOld", LichenOld.linear);
            Shader.SetGlobalVector("_OS_LichenRate", LichenRate);
            Shader.SetGlobalColor("_OS_Moss", Moss.linear);
            Shader.SetGlobalColor("_OS_MossOld", MossOld.linear);
        }
    }
}
