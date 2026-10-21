using UnityEngine;

namespace Overstory.World
{
    /// <summary>
    /// The setting pack's water (docs/foundations.md, the water layer): how the town's shared materials answer the
    /// water that lies and runs on them, as water profiles every surface's shader reads through Water.hlsl (x how much
    /// it darkens wet, y how glossy its wet film gets, z how long it holds water after rain, w how readily running
    /// water stains it). A surface's own rock or timber brings its profile on its material; these are the materials
    /// many surfaces share. Where water lies and runs is each surface's own, baked by its generator.
    /// </summary>
    public static class WaterPack
    {
        /// <summary>Cement and its pointing: it soaks water up, stays dark long, matt, and stains under every drip.</summary>
        public static Vector4 Cement = new Vector4(0.9f, 0.3f, 0.8f, 1.0f);
        /// <summary>The soil a joint holds: dark and matt when wet, the last to dry, too soft to streak.</summary>
        public static Vector4 Soil = new Vector4(0.6f, 0.15f, 1.0f, 0.0f);
        /// <summary>Moss and lichen: they soak it up, darken and green, and never glaze.</summary>
        public static Vector4 Growth = new Vector4(0.75f, 0.0f, 0.9f, 0.0f);

        /// <summary>Set the pack's water for every shader in the town.</summary>
        public static void Apply()
        {
            Shader.SetGlobalVector("_OS_WaterCement", Cement);
            Shader.SetGlobalVector("_OS_WaterSoil", Soil);
            Shader.SetGlobalVector("_OS_WaterGrowth", Growth);
        }
    }
}
