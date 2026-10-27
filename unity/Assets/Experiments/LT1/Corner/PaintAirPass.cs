using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace Overstory.Corner
{
    /// <summary>
    /// The painted corner's air at runtime (PaintAir.shader, pass "Scene"), enqueued for each camera by
    /// PaintedCornerLook so no shared renderer asset changes. Two passes after the transparents: the distance pass (every
    /// opaque renderer drawn again with _P_Mode 1 into its own target, anti-aliased as the frame is, so the edges against
    /// the sky stay clean), then the air over the frame and the distance, which takes the frame's place.
    /// </summary>
    public sealed class PaintAirPass : ScriptableRenderPass
    {
        static readonly int ModeId = Shader.PropertyToID("_P_Mode");
        static readonly int DistId = Shader.PropertyToID("_P_Dist");
        static readonly int DistTexelId = Shader.PropertyToID("_P_Dist_TexelSize");
        static readonly int BlitTextureId = Shader.PropertyToID("_BlitTexture");
        static readonly int BlitScaleBiasId = Shader.PropertyToID("_BlitScaleBias");
        static readonly int CamPosId = Shader.PropertyToID("_P_CamPos");
        static readonly int CamFwdId = Shader.PropertyToID("_P_CamFwd");
        static readonly int CamRightId = Shader.PropertyToID("_P_CamRight");
        static readonly int CamUpId = Shader.PropertyToID("_P_CamUp");
        static readonly int TurnsId = Shader.PropertyToID("_P_ContactTurns");
        // the passes that draw a colour: PaintSurface's, and a shader of an element's own that paints itself
        static readonly System.Collections.Generic.List<ShaderTagId> Forward = new System.Collections.Generic.List<ShaderTagId>
            { new ShaderTagId("UniversalForward"), new ShaderTagId("UniversalForwardOnly"), new ShaderTagId("SRPDefaultUnlit") };
        const int ScenePass = 1;

        public Material air;
        /// <summary>The contact shade's turns averaged in each pixel (4: the frame is drawn at 1x, not supersampled).</summary>
        public float contactTurns = 4f;

        class DistData
        {
            public RendererListHandle list;
        }

        class AirData
        {
            public Material air;
            public TextureHandle source, dist;
            public Vector4 texel, pos, fwd, right, up;
            public float turns;
            public MaterialPropertyBlock block;
        }

        readonly MaterialPropertyBlock block = new MaterialPropertyBlock();

        public PaintAirPass()
        {
            renderPassEvent = RenderPassEvent.AfterRenderingTransparents;
            requiresIntermediateTexture = true;
            profilingSampler = new ProfilingSampler("Painted corner: air");
        }

        public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
        {
            var resources = frameData.Get<UniversalResourceData>();
            if (air == null || resources.isActiveTargetBackBuffer)
                return;
            var cameraData = frameData.Get<UniversalCameraData>();
            var renderingData = frameData.Get<UniversalRenderingData>();
            var lightData = frameData.Get<UniversalLightData>();
            var target = cameraData.cameraTargetDescriptor;
            int w = target.width, h = target.height;
            var msaa = (MSAASamples)Mathf.Max(1, target.msaaSamples);

            // the distance from the eye (r, times the coverage), the coverage (g) and the veil (b, times the coverage)
            var dist = graph.CreateTexture(new TextureDesc(w, h)
            {
                format = GraphicsFormat.R16G16B16A16_SFloat, msaaSamples = msaa, clearBuffer = true, clearColor = Color.clear,
                filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp, name = "_P_Dist",
            });
            var depth = graph.CreateTexture(new TextureDesc(w, h)
            {
                format = GraphicsFormat.D32_SFloat, msaaSamples = msaa, clearBuffer = true, name = "_P_DistDepth",
            });
            using (var builder = graph.AddRasterRenderPass<DistData>("Painted corner: distance", out var d, profilingSampler))
            {
                var draw = RenderingUtils.CreateDrawingSettings(Forward, renderingData, cameraData, lightData, SortingCriteria.CommonOpaque);
                var filter = new FilteringSettings(RenderQueueRange.opaque);
                d.list = graph.CreateRendererList(new RendererListParams(renderingData.cullResults, draw, filter));
                builder.UseRendererList(d.list);
                builder.SetRenderAttachment(dist, 0, AccessFlags.Write);
                builder.SetRenderAttachmentDepth(depth, AccessFlags.Write);
                builder.AllowGlobalStateModification(true);
                builder.SetRenderFunc(static (DistData data, RasterGraphContext ctx) =>
                {
                    ctx.cmd.SetGlobalFloat(ModeId, 1f);
                    ctx.cmd.DrawRendererList(data.list);
                    ctx.cmd.SetGlobalFloat(ModeId, 0f);
                });
            }

            // the air over the frame, in its place
            var source = resources.cameraColor;
            var outDesc = graph.GetTextureDesc(source);
            outDesc.name = "_CameraColorPaintedAir";
            outDesc.clearBuffer = false;
            var destination = graph.CreateTexture(outDesc);
            var cam = cameraData.camera;
            var proj = cam.projectionMatrix;
            float tanX = 1f / Mathf.Max(Mathf.Abs(proj.m00), 1e-6f), tanY = 1f / Mathf.Max(Mathf.Abs(proj.m11), 1e-6f);
            using (var builder = graph.AddRasterRenderPass<AirData>("Painted corner: air", out var a, profilingSampler))
            {
                a.air = air;
                a.source = source;
                a.dist = dist;
                a.texel = new Vector4(1f / w, 1f / h, w, h);
                a.pos = cam.transform.position;
                a.fwd = cam.transform.forward;
                a.right = cam.transform.right * tanX;
                a.up = cam.transform.up * tanY;
                a.turns = contactTurns;
                a.block = block;
                builder.UseTexture(source, AccessFlags.Read);
                builder.UseTexture(dist, AccessFlags.Read);
                builder.SetRenderAttachment(destination, 0, AccessFlags.WriteAll);
                builder.SetRenderFunc(static (AirData data, RasterGraphContext ctx) =>
                {
                    var b = data.block;
                    b.Clear();
                    b.SetTexture(BlitTextureId, (RTHandle)data.source);
                    b.SetVector(BlitScaleBiasId, new Vector4(1f, 1f, 0f, 0f));
                    b.SetTexture(DistId, (RTHandle)data.dist);
                    b.SetVector(DistTexelId, data.texel);
                    b.SetVector(CamPosId, data.pos);
                    b.SetVector(CamFwdId, data.fwd);
                    b.SetVector(CamRightId, data.right);
                    b.SetVector(CamUpId, data.up);
                    b.SetFloat(TurnsId, data.turns);
                    ctx.cmd.DrawProcedural(Matrix4x4.identity, data.air, ScenePass, MeshTopology.Triangles, 3, 1, b);
                });
            }
            resources.cameraColor = destination;
        }
    }
}
