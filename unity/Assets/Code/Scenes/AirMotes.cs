using UnityEngine;
using UnityEngine.Rendering;

namespace Overstory.Scenes
{
    /// <summary>
    /// Motes in the air round the camera (AirMotes.shader): dust that sparkles in sunbeams, droplets of mist that glitter
    /// round the lamps. One mesh of seeded motes in a box that wraps round the camera, drawn additively, lit only where
    /// light reaches each mote. Non-semantic texture: it claims nothing about the world beyond the light and the air.
    /// </summary>
    [ExecuteAlways]
    public class AirMotes : MonoBehaviour
    {
        public Material material;
        public int count = 12000;
        public int seed = 1989;
        [Tooltip("The side of the box of air that wraps round the camera, in metres.")]
        public float box = 36f;

        Mesh mesh;
        MeshRenderer meshRenderer;

        void OnEnable() => Build();

        void OnDisable()
        {
            if (mesh != null)
                DestroyImmediate(mesh);
            mesh = null;
        }

        public void Build()
        {
            // (a missing component is not null to ?? in the editor, so ask for it properly)
            if (!TryGetComponent(out MeshFilter filter))
                filter = gameObject.AddComponent<MeshFilter>();
            if (!TryGetComponent(out meshRenderer))
                meshRenderer = gameObject.AddComponent<MeshRenderer>();
            meshRenderer.shadowCastingMode = ShadowCastingMode.Off;
            meshRenderer.receiveShadows = false;
            meshRenderer.sharedMaterial = material;
            var rng = new System.Random(seed);
            var pos = new Vector3[count * 4];
            var corner = new Vector2[count * 4];
            var data = new Vector2[count * 4];
            var tris = new int[count * 6];
            Vector2[] corners = { new(-1, -1), new(1, -1), new(1, 1), new(-1, 1) };
            for (int i = 0; i < count; i++)
            {
                var p = new Vector3((float)rng.NextDouble(), (float)rng.NextDouble(), (float)rng.NextDouble());
                float r = (float)rng.NextDouble();
                float size = 0.5f + 1.5f * Mathf.Pow((float)rng.NextDouble(), 3f); // mostly small, a few larger
                for (int k = 0; k < 4; k++)
                {
                    pos[i * 4 + k] = p;
                    corner[i * 4 + k] = corners[k];
                    data[i * 4 + k] = new Vector2(r, size);
                }
                int b = i * 4;
                tris[i * 6 + 0] = b; tris[i * 6 + 1] = b + 1; tris[i * 6 + 2] = b + 2;
                tris[i * 6 + 3] = b; tris[i * 6 + 4] = b + 2; tris[i * 6 + 5] = b + 3;
            }
            if (mesh == null)
                mesh = new Mesh { name = "air motes", hideFlags = HideFlags.DontSave, indexFormat = IndexFormat.UInt32 };
            mesh.Clear();
            mesh.vertices = pos;
            mesh.uv = corner;
            mesh.uv2 = data;
            mesh.triangles = tris;
            // the shader places them round the camera; bounds that never cull
            mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 100000f);
            filter.sharedMesh = mesh;
        }

        /// <summary>The motes as the rig says: how many show, how bright, how large, lit by sun and lamps.</summary>
        public void Apply(LightRig r)
        {
            Shader.SetGlobalVector("_OS_Motes", new Vector4(r.motes, box, r.moteSize, box * 0.5f));
            Shader.SetGlobalVector("_OS_MoteSun", new Vector4(0.6f, 1.0f, r.lampsOn ? 1.0f : 0f, 0f));
            if (meshRenderer != null)
                meshRenderer.enabled = r.motes > 0f;
        }
    }
}
