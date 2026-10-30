using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace Overstory.Scenes
{
    /// <summary>
    /// The town's lamps in the fog (FogLights.shader) at a quarter of the pixels, as the sun's beams are: the halos at
    /// half the width and height with each ray's length beside them, then added onto the frame at full size, choosing
    /// the half-size neighbours by the length of their rays. Before post-processing. The lamps are the ones in view,
    /// which TownLights culls for each camera; it draws nothing while no lamp in view is lit or the halos are off.
    ///
    /// <see cref="fullSize"/> draws the old pass instead (FogLightsFull.shader: every lit lamp at every full-size pixel,
    /// after a copy of the frame, through URP's full-screen pass): the A arm of the walked corner's harness A/B
    /// ('foglights-full', retired with the corner on 30 October), off in the game.
    /// </summary>
    public class FogLightsFeature : ScriptableRendererFeature
    {
        [Tooltip("Overstory/FogLights.")]
        public Shader shader;
        [Tooltip("Overstory/FogLightsFull: the old full-size pass, the A/B's reference.")]
        public Shader fullShader;

        /// <summary>Draw the old full-size pass over every lit lamp (the harness's 'foglights-full'). Never saved.</summary>
        [System.NonSerialized] public bool fullSize;

        Material material, fullMaterial;
        HalosPass pass;
        FullScreenPassRendererFeature full;

        static readonly int CountId = Shader.PropertyToID("_OS_FogLampCount");
        static readonly int StrengthId = Shader.PropertyToID("_OS_FogLampStrength");

        public override void Create()
        {
            if (material == null && shader != null)
                material = CoreUtils.CreateEngineMaterial(shader);
            pass = new HalosPass(material) { renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing };
            if (fullMaterial == null && fullShader != null)
                fullMaterial = CoreUtils.CreateEngineMaterial(fullShader);
            if (full == null)
            {
                full = CreateInstance<FullScreenPassRendererFeature>();
                full.hideFlags = HideFlags.HideAndDontSave;
            }
            full.name = "FogLightsFull";
            full.passMaterial = fullMaterial;
            full.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
            full.requirements = ScriptableRenderPassInput.Depth;
            full.fetchColorBuffer = true;
            full.Create();
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            var type = renderingData.cameraData.cameraType;
            if (material == null || type == CameraType.Preview || type == CameraType.Reflection)
                return;
            if (fullSize)
            {
                if (fullMaterial != null)
                    full.AddRenderPasses(renderer, ref renderingData);
                return;
            }
            if (Shader.GetGlobalInt(CountId) <= 0 || Shader.GetGlobalFloat(StrengthId) <= 0f)
                return;
            pass.ConfigureInput(ScriptableRenderPassInput.Depth);
            pass.requiresIntermediateTexture = true;
            renderer.EnqueuePass(pass);
        }

        protected override void Dispose(bool disposing)
        {
            CoreUtils.Destroy(material);
            CoreUtils.Destroy(fullMaterial);
            material = fullMaterial = null;
            if (full != null)
                CoreUtils.Destroy(full);
            full = null;
        }

        class HalosPass : ScriptableRenderPass
        {
            static readonly int FogTexId = Shader.PropertyToID("_OS_FogTex");
            static readonly int FogSizeId = Shader.PropertyToID("_OS_FogSize");
            static readonly int BlitScaleBiasId = Shader.PropertyToID("_BlitScaleBias");
            static readonly MaterialPropertyBlock Block = new MaterialPropertyBlock();
            const int MarchPass = 0, CompositePass = 1;

            readonly Material material;

            // (the render graph pools these: every field is set for every pass)
            class PassData
            {
                public Material material;
                public int pass;
                public Vector4 size;
                public TextureHandle input;
            }

            public HalosPass(Material material)
            {
                this.material = material;
                profilingSampler = new ProfilingSampler("FogLights");
            }

            public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
            {
                var resources = frameData.Get<UniversalResourceData>();
                var camera = frameData.Get<UniversalCameraData>();
                if (!resources.cameraDepthTexture.IsValid() || resources.isActiveTargetBackBuffer)
                    return;

                int w = camera.cameraTargetDescriptor.width, h = camera.cameraTargetDescriptor.height;
                int lw = (w + 1) / 2, lh = (h + 1) / 2;
                var size = new Vector4(w, h, lw, lh);
                var halos = graph.CreateTexture(new TextureDesc(lw, lh)
                {
                    colorFormat = GraphicsFormat.R16G16B16A16_SFloat,
                    filterMode = FilterMode.Point,
                    wrapMode = TextureWrapMode.Clamp,
                    clearBuffer = false,
                    name = "_OS_FogHalos",
                });

                using (var builder = graph.AddRasterRenderPass<PassData>("FogLights march", out var data, profilingSampler))
                {
                    data.material = material;
                    data.pass = MarchPass;
                    data.size = size;
                    data.input = TextureHandle.nullHandle;
                    builder.UseTexture(resources.cameraDepthTexture);
                    builder.SetRenderAttachment(halos, 0, AccessFlags.WriteAll);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                }
                using (var builder = graph.AddRasterRenderPass<PassData>("FogLights composite", out var data, profilingSampler))
                {
                    data.material = material;
                    data.pass = CompositePass;
                    data.size = size;
                    data.input = halos;
                    builder.UseTexture(halos);
                    builder.UseTexture(resources.cameraDepthTexture);
                    // added onto the frame: what is there is kept and read by the blend
                    builder.SetRenderAttachment(resources.activeColorTexture, 0, AccessFlags.ReadWrite);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                }
            }

            static void Draw(RasterCommandBuffer cmd, PassData d)
            {
                Block.Clear();
                Block.SetVector(BlitScaleBiasId, new Vector4(1f, 1f, 0f, 0f));
                Block.SetVector(FogSizeId, d.size);
                if (d.input.IsValid())
                    Block.SetTexture(FogTexId, d.input);
                cmd.DrawProcedural(Matrix4x4.identity, d.material, d.pass, MeshTopology.Triangles, 3, 1, Block);
            }
        }
    }
}
