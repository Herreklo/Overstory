using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace Overstory.Scenes
{
    /// <summary>
    /// A full-screen pass of the style (the palette, the key block): its material drawn over the whole frame, reading
    /// the frame as it stands (_BlitTexture) and writing a new one that takes the frame's place, so the frame is read once
    /// and written once where URP's own full-screen pass first copies it whole. Drawn only while the global float
    /// <see cref="gate"/> is on (the stage sets it from the look: the key block in look D only, the palette while a style
    /// is set); while it is off the frame is left as it is, which is what the pass's own early out gave it.
    /// </summary>
    public class StylePassFeature : ScriptableRendererFeature
    {
        [Tooltip("Where in the frame the pass is drawn.")]
        public RenderPassEvent injectionPoint = RenderPassEvent.AfterRenderingPostProcessing;
        [Tooltip("What the pass reads besides the frame (depth, normals).")]
        public ScriptableRenderPassInput requirements = ScriptableRenderPassInput.None;
        [Tooltip("The pass's material: its shader reads the frame as _BlitTexture.")]
        public Material passMaterial;
        public int passIndex;
        [Tooltip("The global float that turns the pass on (above 0.5); empty: always on.")]
        public string gate = "";

        DrawPass pass;

        public override void Create()
        {
            pass = new DrawPass(name) { renderPassEvent = injectionPoint };
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            var type = renderingData.cameraData.cameraType;
            if (passMaterial == null || type == CameraType.Preview || type == CameraType.Reflection)
                return;
            if (!string.IsNullOrEmpty(gate) && Shader.GetGlobalFloat(gate) < 0.5f)
                return;
            pass.renderPassEvent = injectionPoint;
            pass.material = passMaterial;
            pass.index = passIndex;
            pass.ConfigureInput(requirements);
            pass.requiresIntermediateTexture = true;
            renderer.EnqueuePass(pass);
        }

        class DrawPass : ScriptableRenderPass
        {
            static readonly int BlitTextureId = Shader.PropertyToID("_BlitTexture");
            static readonly int BlitScaleBiasId = Shader.PropertyToID("_BlitScaleBias");
            static readonly MaterialPropertyBlock Block = new MaterialPropertyBlock();
            public Material material;
            public int index;
            readonly string label;

            class PassData
            {
                public Material material;
                public int index;
                public TextureHandle source;
            }

            public DrawPass(string label)
            {
                this.label = label;
                profilingSampler = new ProfilingSampler(label);
            }

            public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
            {
                var resources = frameData.Get<UniversalResourceData>();
                if (resources.isActiveTargetBackBuffer)
                    return;
                var source = resources.cameraColor;
                var desc = graph.GetTextureDesc(source);
                desc.name = "_CameraColor" + label;
                desc.clearBuffer = false;
                var destination = graph.CreateTexture(desc);
                using (var builder = graph.AddRasterRenderPass<PassData>(label, out var data, profilingSampler))
                {
                    data.material = material;
                    data.index = index;
                    data.source = source;
                    builder.UseTexture(source, AccessFlags.Read);
                    if ((input & ScriptableRenderPassInput.Depth) != 0)
                        builder.UseTexture(resources.cameraDepthTexture, AccessFlags.Read);
                    if ((input & ScriptableRenderPassInput.Normal) != 0)
                        builder.UseTexture(resources.cameraNormalsTexture, AccessFlags.Read);
                    builder.SetRenderAttachment(destination, 0, AccessFlags.WriteAll);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) =>
                    {
                        Block.Clear();
                        Block.SetTexture(BlitTextureId, (RTHandle)d.source);
                        Block.SetVector(BlitScaleBiasId, new Vector4(1f, 1f, 0f, 0f));
                        ctx.cmd.DrawProcedural(Matrix4x4.identity, d.material, d.index, MeshTopology.Triangles, 3, 1, Block);
                    });
                }
                resources.cameraColor = destination;
            }
        }
    }
}
