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
        public static Color Lichen = new Color(0.64f, 0.65f, 0.60f);       // a pale grey crust, never white
        public static Color LichenOld = new Color(0.55f, 0.57f, 0.51f);
        public static Color LichenRim = new Color(0.30f, 0.30f, 0.29f);    // map lichen's dark prothallus, seen as a line
        /// <summary>x growth (m a year), y the size of a patch (m), z how much of a quiet surface it takes.</summary>
        public static Vector4 LichenRate = new Vector4(0.0007f, 0.11f, 0.85f, 0f);
        public static Color Moss = new Color(0.40f, 0.49f, 0.17f);     // wet moss on this coast (measured on the board, 06: median 0.33, 0.41, 0.18; its tips fresher)
        public static Color MossOld = new Color(0.31f, 0.35f, 0.15f);

        /// <summary>Set the pack's growth for every shader in the town.</summary>
        public static void Apply()
        {
            Shader.SetGlobalColor("_OS_Lichen", Lichen.linear);
            Shader.SetGlobalColor("_OS_LichenOld", LichenOld.linear);
            Shader.SetGlobalColor("_OS_LichenRim", LichenRim.linear);
            Shader.SetGlobalVector("_OS_LichenRate", LichenRate);
            Shader.SetGlobalColor("_OS_Moss", Moss.linear);
            Shader.SetGlobalColor("_OS_MossOld", MossOld.linear);
        }
    }
}
