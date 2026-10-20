using UnityEngine;
using UnityEngine.Rendering;

namespace Overstory.Scenes
{
    /// <summary>
    /// The town seen from straight above, as a map of its height: from it every point works out how much of its sky
    /// the town leaves open, so lanes, yards and the feet of walls darken and roofs and quays stay open
    /// (StreetLooks.hlsl, OS_TownSky). Nothing is baked: the map is drawn again whenever the town changes, at any
    /// size of town, which per-part bakes (blender/generators/bake.py) cannot see across.
    /// </summary>
    [ExecuteAlways]
    public class SkyMap : MonoBehaviour
    {
        [Tooltip("What the map is drawn from: every renderer under it, except water.")]
        public Transform town;
        [Tooltip("The middle of the mapped square, in Unity's x and z.")]
        public Vector2 centre;
        [Tooltip("The side of the mapped square in metres.")]
        public float size = 1024f;
        public int resolution = 2048;
        [Tooltip("A height over everything in the town, where the map's camera looks down from.")]
        public float top = 600f;
        [Tooltip("Read the map's v from the top. Off on every platform so far: the GPU projection for render textures " +
                 "already turns it the right way up; LT1Heart.CheckSkyMap proves it against a known tower.")]
        public bool flipV = false;

        RenderTexture map;
        Material heightMaterial;

        public bool Built => map != null && map.IsCreated();

        void OnEnable() => Build();

        void OnDisable()
        {
            Shader.SetGlobalFloat("_OS_SkyMapOn", 0f);
            if (map != null)
            {
                map.Release();
                DestroyImmediate(map);
            }
            if (heightMaterial != null)
                DestroyImmediate(heightMaterial);
            map = null;
            heightMaterial = null;
        }

        /// <summary>Draws the map from the town as it stands now, and hands it to the shaders.</summary>
        public void Build()
        {
            if (town == null)
                return;
            var shader = Shader.Find("Hidden/Overstory/TownHeight");
            if (shader == null)
            {
                Debug.LogWarning("[SkyMap] the height shader is missing");
                return;
            }
            if (heightMaterial == null)
                heightMaterial = new Material(shader) { hideFlags = HideFlags.DontSave };
            if (map == null || map.width != resolution)
            {
                if (map != null)
                {
                    map.Release();
                    DestroyImmediate(map);
                }
                map = new RenderTexture(resolution, resolution, 24, RenderTextureFormat.RHalf, RenderTextureReadWrite.Linear)
                {
                    name = "town sky map",
                    filterMode = FilterMode.Bilinear,
                    wrapMode = TextureWrapMode.Clamp,
                    hideFlags = HideFlags.DontSave,
                };
                map.Create();
            }

            // an orthographic camera over the middle, looking straight down, +x to the right and +z up the image
            var eye = new Vector3(centre.x, top, centre.y);
            var view = Matrix4x4.Scale(new Vector3(1, 1, -1)) *
                       Matrix4x4.TRS(eye, Quaternion.LookRotation(Vector3.down, Vector3.forward), Vector3.one).inverse;
            var proj = Matrix4x4.Ortho(-size / 2, size / 2, -size / 2, size / 2, 0.1f, top + 400f);
            var vp = GL.GetGPUProjectionMatrix(proj, true) * view;

            var cmd = new CommandBuffer { name = "town sky map" };
            cmd.SetRenderTarget(map);
            cmd.ClearRenderTarget(true, true, new Color(-1000f, 0, 0, 0));
            cmd.SetGlobalMatrix("_OS_HeightVP", vp);
            foreach (var r in town.GetComponentsInChildren<MeshRenderer>())
            {
                if (r.gameObject.name.StartsWith("water") || !r.enabled)
                    continue;
                var mf = r.GetComponent<MeshFilter>();
                if (mf == null || mf.sharedMesh == null)
                    continue;
                for (int i = 0; i < mf.sharedMesh.subMeshCount; i++)
                    cmd.DrawRenderer(r, heightMaterial, i, 0);
            }
            Graphics.ExecuteCommandBuffer(cmd);
            cmd.Release();
            Bind();
        }

        public void Bind()
        {
            if (!Built)
                return;
            Shader.SetGlobalTexture("_OS_SkyMap", map);
            // uv = (xz - corner) / size, v read from the top when flipped
            Shader.SetGlobalVector("_OS_SkyMapRect", new Vector4(centre.x - size / 2, centre.y - size / 2, 1f / size, flipV ? 1f : 0f));
            Shader.SetGlobalFloat("_OS_SkyMapOn", 1f);
        }

        /// <summary>
        /// The map's height at a point (Unity x, z), sampled on the GPU exactly as the street shader samples it,
        /// so it proves the map's orientation on whatever graphics API this runs on.
        /// </summary>
        public float Probe(float x, float z)
        {
            var shader = Shader.Find("Hidden/Overstory/SkyMapProbe");
            if (shader == null || !Built)
                return float.NaN;
            Bind();
            var mat = new Material(shader) { hideFlags = HideFlags.DontSave };
            mat.SetVector("_Probe", new Vector4(x, z, 0, 0));
            var rt = new RenderTexture(1, 1, 0, RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear);
            rt.Create();
            Graphics.Blit(null, rt, mat);
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(1, 1, TextureFormat.RGBAFloat, false, true);
            tex.ReadPixels(new Rect(0, 0, 1, 1), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            float h = tex.GetPixel(0, 0).r;
            DestroyImmediate(tex);
            rt.Release();
            DestroyImmediate(rt);
            DestroyImmediate(mat);
            return h;
        }

        /// <summary>Reads the whole map back, for pictures: heights in metres, in the order the GPU returns its rows.</summary>
        public float[] ReadHeights()
        {
            var request = AsyncGPUReadback.Request(map, 0);
            request.WaitForCompletion();
            if (request.hasError)
                return new float[0];
            var raw = request.GetData<ushort>();
            var heights = new float[raw.Length];
            for (int i = 0; i < raw.Length; i++)
                heights[i] = Mathf.HalfToFloat(raw[i]);
            return heights;
        }
    }
}
