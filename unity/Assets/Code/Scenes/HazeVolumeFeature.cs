using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace Overstory.Scenes
{
    /// <summary>
    /// The fog bank worked out once a frame along the camera's own rays (HazeVolume.compute), before the opaques: a ray
    /// for every <see cref="tile"/> by <see cref="tile"/> pixels, each integrated from the eye through the same air the
    /// surfaces shade with, and its optical depth and the town's glow it scatters kept at <see cref="slices"/> distances
    /// out to <see cref="reach"/>. Every surface, the sky and the motes then read their own ray at their own distance in
    /// one lookup (StreetSurface.hlsl, OS_HazeLookup) where each pixel marched twelve steps through two noises before;
    /// what is off the screen (a pane's reflected sky) still marches. Only while the light has a bank (_OS_Bank.x) and
    /// only for the game's and the scene view's cameras; for any other camera the shaders march as before.
    /// </summary>
    public class HazeVolumeFeature : ScriptableRendererFeature
    {
        [Tooltip("Overstory's HazeVolume.compute.")]
        public ComputeShader compute;
        [Tooltip("Screen pixels a ray of the volume stands for, across and down.")]
        public int tile = 16;
        [Tooltip("Distances each ray is kept at, from the eye out to the reach.")]
        public int slices = 128;
        [Tooltip("Integration steps between two kept distances.")]
        public int steps = 2;
        [Tooltip("How far the volume reaches (m): as far as the surfaces' march (StreetSurface.hlsl, OS_Atmosphere).")]
        public float reach = 3000f;
        [Tooltip("The distance (m) under which the kept distances lie evenly, and over which they spread in proportion.")]
        public float near = 1f;

        internal static readonly int InfoId = Shader.PropertyToID("_OS_HazeVolInfo");
        static readonly int BankId = Shader.PropertyToID("_OS_Bank");
        static readonly int HazeId = Shader.PropertyToID("_OS_Haze");

        FillPass fill;
        ResetPass reset;

        public override void Create()
        {
            fill?.Dispose();
            fill = new FillPass(this) { renderPassEvent = RenderPassEvent.BeforeRenderingOpaques };
            reset = new ResetPass { renderPassEvent = RenderPassEvent.AfterRendering };
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            // (until this camera's volume is made, the shaders march)
            Shader.SetGlobalVector(InfoId, Vector4.zero);
            var type = renderingData.cameraData.cameraType;
            if (compute == null || !SystemInfo.supportsComputeShaders || (type != CameraType.Game && type != CameraType.SceneView))
                return;
            if (Shader.GetGlobalVector(BankId).x < 0.5f || Shader.GetGlobalVector(HazeId).x <= 0f)
                return;
            renderer.EnqueuePass(fill);
            renderer.EnqueuePass(reset);
        }

        protected override void Dispose(bool disposing)
        {
            fill?.Dispose();
            fill = null;
            Shader.SetGlobalVector(InfoId, Vector4.zero);
        }

        class FillPass : ScriptableRenderPass
        {
            static readonly int OutId = Shader.PropertyToID("_OS_HazeVolOut");
            static readonly int VolId = Shader.PropertyToID("_OS_HazeVol");
            static readonly int VPId = Shader.PropertyToID("_OS_HazeVP");
            static readonly int InvVPId = Shader.PropertyToID("_OS_HazeInvVP");
            static readonly int EyeId = Shader.PropertyToID("_OS_HazeEye");
            static readonly int GridId = Shader.PropertyToID("_OS_HazeGrid");
            static readonly int SlicesId = Shader.PropertyToID("_OS_HazeSlices");

            readonly HazeVolumeFeature feature;
            RenderTexture volume;

            class PassData
            {
                public ComputeShader compute;
                public int kernel;
                public RenderTexture volume;
                public Matrix4x4 vp, inverse;
                public Vector4 eye, grid, slices, info;
            }

            public FillPass(HazeVolumeFeature feature)
            {
                this.feature = feature;
                profilingSampler = new ProfilingSampler("Haze volume");
            }

            public void Dispose()
            {
                if (volume != null)
                {
                    volume.Release();
                    CoreUtils.Destroy(volume);
                }
                volume = null;
            }

            public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
            {
                var camera = frameData.Get<UniversalCameraData>();
                int tile = Mathf.Max(feature.tile, 1), n = Mathf.Max(feature.slices, 2);
                int w = Mathf.Max(1, (camera.cameraTargetDescriptor.width + tile - 1) / tile);
                int h = Mathf.Max(1, (camera.cameraTargetDescriptor.height + tile - 1) / tile);
                if (volume == null || volume.width != w || volume.height != h || volume.volumeDepth != n || !volume.IsCreated())
                {
                    Dispose();
                    var desc = new RenderTextureDescriptor(w, h, GraphicsFormat.R16G16B16A16_SFloat, GraphicsFormat.None)
                    {
                        dimension = TextureDimension.Tex3D, volumeDepth = n, enableRandomWrite = true, msaaSamples = 1,
                    };
                    volume = new RenderTexture(desc)
                    {
                        name = "_OS_HazeVol", filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp,
                        hideFlags = HideFlags.HideAndDontSave,
                    };
                    volume.Create();
                }
                var vp = camera.GetProjectionMatrix() * camera.GetViewMatrix();
                float d0 = Mathf.Max(feature.near, 0.01f);
                float span = Mathf.Log(1f + Mathf.Max(feature.reach, 1f) / d0, 2f);
                using (var builder = graph.AddUnsafePass<PassData>("Haze volume", out var data, profilingSampler))
                {
                    data.compute = feature.compute;
                    data.kernel = feature.compute.FindKernel("Fill");
                    data.volume = volume;
                    data.vp = vp;
                    data.inverse = vp.inverse;
                    var eye = camera.worldSpaceCameraPos;
                    data.eye = new Vector4(eye.x, eye.y, eye.z, 0f);
                    data.grid = new Vector4(w, h, n, Mathf.Max(feature.steps, 1));
                    data.slices = new Vector4(d0, span, 0f, 0f);
                    data.info = new Vector4(1f, n, d0, span);
                    builder.AllowPassCulling(false);
                    builder.AllowGlobalStateModification(true);
                    builder.SetRenderFunc(static (PassData d, UnsafeGraphContext ctx) =>
                    {
                        var cmd = ctx.cmd;
                        cmd.SetComputeTextureParam(d.compute, d.kernel, OutId, d.volume);
                        cmd.SetComputeMatrixParam(d.compute, InvVPId, d.inverse);
                        cmd.SetComputeVectorParam(d.compute, EyeId, d.eye);
                        cmd.SetComputeVectorParam(d.compute, GridId, d.grid);
                        cmd.SetComputeVectorParam(d.compute, SlicesId, d.slices);
                        cmd.DispatchCompute(d.compute, d.kernel, ((int)d.grid.x + 7) / 8, ((int)d.grid.y + 7) / 8, 1);
                        cmd.SetGlobalTexture(VolId, d.volume);
                        cmd.SetGlobalMatrix(VPId, d.vp);
                        cmd.SetGlobalVector(InfoId, d.info);
                    });
                }
            }
        }

        /// <summary>After the camera: the volume is no other camera's.</summary>
        class ResetPass : ScriptableRenderPass
        {
            class PassData { }

            public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
            {
                using (var builder = graph.AddUnsafePass<PassData>("Haze volume done", out var data))
                {
                    builder.AllowPassCulling(false);
                    builder.AllowGlobalStateModification(true);
                    builder.SetRenderFunc(static (PassData d, UnsafeGraphContext ctx) => ctx.cmd.SetGlobalVector(InfoId, Vector4.zero));
                }
            }
        }
    }
}
