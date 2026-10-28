using System;
using UnityEngine;

namespace Overstory.Growth
{
    /// <summary>
    /// The growth's tufts in a scene: their kinds (meshes by level, material, reach) and instances, saved with the scene,
    /// drawn through the growth's own BatchRendererGroup (GrowthDraw) while enabled, in the editor and in the app alike.
    /// Filled by the scene's builder (it was the painted corner's growth element, now removed) from the generator's
    /// placements; it draws what it holds and decides nothing.
    /// </summary>
    [ExecuteAlways]
    public sealed class GrowthTufts : MonoBehaviour
    {
        [Serializable]
        public sealed class Kind
        {
            public string name;
            public Mesh[] levels;
            public Material material;
            public float[] to;
            public float fade;
            public float thinFrom = 1e6f, keepMin = 1f;
            public float radius = 1f;
            public Matrix4x4[] matrices;
            public uint[] users;
        }

        public Kind[] kinds = new Kind[0];

        GrowthDraw draw;

        /// <summary>From the last camera's cull: instances and triangles drawn.</summary>
        public int Drawn => draw != null ? draw.lastDrawn : 0;
        public int Triangles => draw != null ? draw.lastTriangles : 0;

        void OnEnable() => Rebuild();

        void OnDisable()
        {
            draw?.Dispose();
            draw = null;
        }

        /// <summary>Starts drawing what it holds now (again, if it was).</summary>
        public void Rebuild()
        {
            OnDisable();
            if (kinds == null || kinds.Length == 0)
                return;
            draw = new GrowthDraw();
            foreach (var k in kinds)
            {
                if (k == null || k.levels == null || k.levels.Length == 0 || k.material == null || k.matrices == null || k.matrices.Length == 0)
                    continue;
                var g = new GrowthDraw.Kind
                {
                    name = k.name, levels = k.levels, material = k.material, to = k.to, fade = k.fade,
                    thinFrom = k.thinFrom, keepMin = k.keepMin, radius = k.radius,
                };
                g.matrices.AddRange(k.matrices);
                g.users.AddRange(k.users);
                draw.Add(g);
            }
            draw.Build();
        }
    }
}
