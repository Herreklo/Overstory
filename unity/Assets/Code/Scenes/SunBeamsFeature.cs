using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

namespace Overstory.Scenes
{
    /// <summary>
    /// The sun's beams in the haze (SunBeamsQuarter.shader), at a quarter of the pixels (W5;
    /// docs/research/performance-craft.md, item 1): the cloud layer into a small map when it changes, the march at half
    /// the width and height, a blur across and down that cancels the march's ordered offsets, and a composite that adds
    /// the beams onto the frame at full size, choosing its half-size neighbours by the length of their rays. Before
    /// post-processing, as the full-size pass was. It draws nothing while the stage has the beams off (every light but
    /// low sun and morning).
    ///
    /// <see cref="fullSize"/> draws the old pass instead (SunBeams.shader: 40 steps a pixel at full size, URP's soft
    /// shadow filter at every step, after a copy of the frame), exactly as URP's full-screen feature drew it: the A arm
    /// of the harness's A/B (PerfRunner's 'beams-full'), off in the game. It costs the player nothing while off.
    /// </summary>
    public class SunBeamsFeature : ScriptableRendererFeature
    {
        [Tooltip("Overstory/SunBeamsQuarter.")]
        public Shader shader;
        [Tooltip("Draw the old full-size pass instead (the A/B's reference; SunBeams.shader through URP's full-screen pass).")]
        public bool fullSize;
        [Tooltip("The old pass's material (M_SunBeams, Overstory/SunBeams).")]
        public Material fullMaterial;

        /// <summary>The harness's arms for how the beams meet the frame (PerfRunner, 'beams-&lt;arm&gt;'): "" adds them onto
        /// the frame by blending; "copy" copies the frame and writes it whole with the beams added; "nocomposite" marches
        /// and blurs but never composites (the march's own cost). Never saved.</summary>
        [System.NonSerialized] public string arm = "";

        Material material;
        CloudMapPass cloudPass;
        BeamsPass pass;
        FullScreenPassRendererFeature full;

        public override void Create()
        {
            if (material == null && shader != null)
                material = CoreUtils.CreateEngineMaterial(shader);
            cloudPass?.Dispose();
            cloudPass = new CloudMapPass(material) { renderPassEvent = RenderPassEvent.BeforeRenderingOpaques };
            pass = new BeamsPass(material) { renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing };

            if (full == null)
            {
                full = CreateInstance<FullScreenPassRendererFeature>();
                full.hideFlags = HideFlags.HideAndDontSave;
            }
            full.name = "SunBeams";
            full.passMaterial = fullMaterial;
            full.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
            full.requirements = ScriptableRenderPassInput.Depth;
            full.fetchColorBuffer = true;
            full.Create();
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            var type = renderingData.cameraData.cameraType;
            if (type == CameraType.Preview || type == CameraType.Reflection)
                return;
            // the clouds' map, for their shadows on the town, whether the beams are drawn or not
            if (material != null)
                renderer.EnqueuePass(cloudPass);
            if (fullSize)
            {
                full.passMaterial = fullMaterial;
                full.AddRenderPasses(renderer, ref renderingData);
                return;
            }
            if (material == null)
                return;
            // the stage's beams (StreetStage: strength 0 in every light without shafts, and no sun after sunset)
            var beams = Shader.GetGlobalVector(BeamsPass.SunBeamsId);
            var sun = Shader.GetGlobalVector(BeamsPass.SunColId);
            if (beams.x <= 0f || sun.x + sun.y + sun.z <= 0.001f)
                return;
            pass.arm = arm ?? "";
            pass.ConfigureInput(ScriptableRenderPassInput.Depth);
            pass.requiresIntermediateTexture = true;
            renderer.EnqueuePass(pass);
        }

        protected override void Dispose(bool disposing)
        {
            cloudPass?.Dispose();
            CoreUtils.Destroy(material);
            material = null;
            if (full != null)
                CoreUtils.Destroy(full);
            full = null;
        }

        /// <summary>
        /// The cloud layer's field into a small map before the opaques (SunBeamsQuarter.shader, pass 0), for the shadows
        /// the clouds cast on the town (StreetLooks.hlsl, OS_CloudLight) and for the beams' march alike: 512², 8 m a
        /// texel over a 4 km square of the layer's own grid, which drifts with the wind, round where the camera's air
        /// meets the layer. It is drawn again only when that point strays a quarter of the way to the square's edge or
        /// the clouds' size changes, so neither the wind nor the camera draws anything new until then. Where the map
        /// does not reach, the shaders compute the field themselves.
        /// </summary>
        class CloudMapPass : ScriptableRenderPass
        {
            internal static readonly int CloudMapId = Shader.PropertyToID("_OS_CloudMap");
            internal static readonly int CloudMapRectId = Shader.PropertyToID("_OS_CloudMapRect");
            static readonly int CloudsId = Shader.PropertyToID("_OS_Clouds");
            static readonly int DriftId = Shader.PropertyToID("_OS_CloudDrift");
            static readonly int SunDirId = Shader.PropertyToID("_OS_SunDir");
            static readonly int BlitScaleBiasId = Shader.PropertyToID("_BlitScaleBias");
            static readonly MaterialPropertyBlock Block = new MaterialPropertyBlock();

            const int Res = 512;
            const float Side = 4096f, Texel = Side / Res;

            readonly Material material;
            RTHandle map;
            bool drawn;
            Vector2 centre;
            float size;

            class PassData
            {
                public Material material;
                public Vector4 rect;
            }

            public CloudMapPass(Material material)
            {
                this.material = material;
                profilingSampler = new ProfilingSampler("SunBeams cloud map");
            }

            public void Dispose()
            {
                map?.Release();
                map = null;
                drawn = false;
                Shader.SetGlobalVector(CloudMapRectId, Vector4.zero);
            }

            public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
            {
                var clouds = Shader.GetGlobalVector(CloudsId);
                if (clouds.x <= 0.001f)
                {
                    Shader.SetGlobalVector(CloudMapRectId, Vector4.zero);
                    return;
                }
                var eye = frameData.Get<UniversalCameraData>().worldSpaceCameraPos;
                var toSun = Shader.GetGlobalVector(SunDirId);
                float up = Mathf.Max(toSun.y, 0.05f), reach = (clouds.w - eye.y) / up;
                var at = new Vector2(eye.x + toSun.x * reach, eye.z + toSun.z * reach) + (Vector2)Shader.GetGlobalVector(DriftId);
                if (map == null)
                    map = RTHandles.Alloc(new RenderTextureDescriptor(Res, Res, GraphicsFormat.R16_SFloat, GraphicsFormat.None),
                                          FilterMode.Bilinear, TextureWrapMode.Clamp, name: "_OS_CloudMap");
                bool stray = !drawn || Mathf.Abs(at.x - centre.x) > Side / 4f || Mathf.Abs(at.y - centre.y) > Side / 4f;
                if (stray)
                    centre = new Vector2(Mathf.Round(at.x / Texel) * Texel, Mathf.Round(at.y / Texel) * Texel);
                var rect = new Vector4(centre.x - Side / 2f, centre.y - Side / 2f, 1f / Side, Res);
                if (stray || clouds.y != size || !map.rt.IsCreated())
                {
                    drawn = true;
                    size = clouds.y;
                    using (var builder = graph.AddRasterRenderPass<PassData>("SunBeams cloud map", out var data, profilingSampler))
                    {
                        data.material = material;
                        data.rect = rect;
                        builder.SetRenderAttachment(graph.ImportTexture(map), 0, AccessFlags.WriteAll);
                        builder.AllowPassCulling(false);
                        builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) =>
                        {
                            Block.Clear();
                            Block.SetVector(BlitScaleBiasId, new Vector4(1f, 1f, 0f, 0f));
                            Block.SetVector(CloudMapRectId, d.rect);
                            ctx.cmd.DrawProcedural(Matrix4x4.identity, d.material, 0, MeshTopology.Triangles, 3, 1, Block);
                        });
                    }
                }
                Shader.SetGlobalTexture(CloudMapId, map.rt);
                Shader.SetGlobalVector(CloudMapRectId, rect);
            }
        }

        class BeamsPass : ScriptableRenderPass
        {
            internal static readonly int SunBeamsId = Shader.PropertyToID("_OS_SunBeams");
            internal static readonly int SunColId = Shader.PropertyToID("_OS_SunCol");
            static readonly int BeamTexId = Shader.PropertyToID("_OS_BeamTex");
            static readonly int BeamSizeId = Shader.PropertyToID("_OS_BeamSize");
            static readonly int CloudMapId = Shader.PropertyToID("_OS_CloudMap");
            static readonly int CloudMapRectId = Shader.PropertyToID("_OS_CloudMapRect");
            static readonly int BlitScaleBiasId = Shader.PropertyToID("_BlitScaleBias");

            const int CloudPass = 0, MarchPass = 1, AcrossPass = 2, DownPass = 3, CompositePass = 4, CompositeOverPass = 5;
            static readonly int FrameTexId = Shader.PropertyToID("_OS_FrameTex");

            public string arm = "";

            readonly Material material;

            // (the render graph pools these: every field is set for every pass)
            class PassData
            {
                public Material material;
                public int pass;
                public TextureHandle input, cloud;
                public Vector4 size, cloudRect;

                public void Set(Material material, int pass, Vector4 size, Vector4 cloudRect, TextureHandle input, TextureHandle cloud)
                {
                    this.material = material;
                    this.pass = pass;
                    this.size = size;
                    this.cloudRect = cloudRect;
                    this.input = input;
                    this.cloud = cloud;
                }
            }

            public BeamsPass(Material material)
            {
                this.material = material;
                profilingSampler = new ProfilingSampler("SunBeams");
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

                // the cloud layer's map (CloudMapPass, before the opaques): the march reads it as the shadows do
                var cloudRect = Shader.GetGlobalVector(CloudMapPass.CloudMapRectId);
                var cloud = TextureHandle.nullHandle;

                var low = new TextureDesc(lw, lh)
                {
                    colorFormat = GraphicsFormat.R16G16_SFloat,
                    filterMode = FilterMode.Point,
                    wrapMode = TextureWrapMode.Clamp,
                    clearBuffer = false,
                    name = "_OS_Beams",
                };
                var march = graph.CreateTexture(low);
                low.name = "_OS_BeamsAcross";
                var across = graph.CreateTexture(low);
                low.name = "_OS_BeamsDown";
                var down = graph.CreateTexture(low);

                using (var builder = graph.AddRasterRenderPass<PassData>("SunBeams march", out var data, profilingSampler))
                {
                    data.Set(material, MarchPass, size, cloudRect, TextureHandle.nullHandle, cloud);
                    builder.UseTexture(resources.cameraDepthTexture);
                    if (resources.mainShadowsTexture.IsValid())
                        builder.UseTexture(resources.mainShadowsTexture);
                    if (cloud.IsValid())
                        builder.UseTexture(cloud);
                    builder.SetRenderAttachment(march, 0, AccessFlags.WriteAll);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                }
                Filter(graph, "SunBeams blur across", AcrossPass, march, across, size);
                Filter(graph, "SunBeams blur down", DownPass, across, down, size);

                if (arm == "nocomposite")
                {
                    // (the march and blur kept, their result read by nothing)
                    using (var builder = graph.AddUnsafePass<PassData>("SunBeams sink", out var data, profilingSampler))
                    {
                        data.Set(material, -1, size, Vector4.zero, down, TextureHandle.nullHandle);
                        builder.UseTexture(down);
                        builder.AllowPassCulling(false);
                        builder.SetRenderFunc(static (PassData d, UnsafeGraphContext ctx) => { });
                    }
                    return;
                }
                if (arm == "copy")
                {
                    var frameDesc = graph.GetTextureDesc(resources.cameraColor);
                    frameDesc.name = "_OS_BeamsFrame";
                    frameDesc.clearBuffer = false;
                    frameDesc.msaaSamples = MSAASamples.None;
                    var frame = graph.CreateTexture(frameDesc);
                    graph.AddBlitPass(resources.activeColorTexture, frame, Vector2.one, Vector2.zero, passName: "SunBeams copy");
                    using (var builder = graph.AddRasterRenderPass<PassData>("SunBeams composite over", out var data, profilingSampler))
                    {
                        data.Set(material, CompositeOverPass, size, Vector4.zero, down, frame);
                        builder.UseTexture(down);
                        builder.UseTexture(frame);
                        builder.UseTexture(resources.cameraDepthTexture);
                        builder.SetRenderAttachment(resources.activeColorTexture, 0, AccessFlags.WriteAll);
                        builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                    }
                    return;
                }
                using (var builder = graph.AddRasterRenderPass<PassData>("SunBeams composite", out var data, profilingSampler))
                {
                    data.Set(material, CompositePass, size, Vector4.zero, down, TextureHandle.nullHandle);
                    builder.UseTexture(down);
                    builder.UseTexture(resources.cameraDepthTexture);
                    // added onto the frame: what is there is kept and read by the blend
                    builder.SetRenderAttachment(resources.activeColorTexture, 0, AccessFlags.ReadWrite);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                }
            }

            void Filter(RenderGraph graph, string name, int which, TextureHandle from, TextureHandle to, Vector4 size)
            {
                using (var builder = graph.AddRasterRenderPass<PassData>(name, out var data, profilingSampler))
                {
                    data.Set(material, which, size, Vector4.zero, from, TextureHandle.nullHandle);
                    builder.UseTexture(from);
                    builder.SetRenderAttachment(to, 0, AccessFlags.WriteAll);
                    builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) => Draw(ctx.cmd, d));
                }
            }

            static readonly MaterialPropertyBlock Block = new MaterialPropertyBlock();

            static void Draw(RasterCommandBuffer cmd, PassData d)
            {
                Block.Clear();
                Block.SetVector(BlitScaleBiasId, new Vector4(1f, 1f, 0f, 0f));
                Block.SetVector(BeamSizeId, d.size);
                Block.SetVector(CloudMapRectId, d.cloudRect);
                if (d.input.IsValid())
                    Block.SetTexture(BeamTexId, d.input);
                if (d.cloud.IsValid())
                    Block.SetTexture(d.pass == CompositeOverPass ? FrameTexId : CloudMapId, d.cloud);
                cmd.DrawProcedural(Matrix4x4.identity, d.material, d.pass, MeshTopology.Triangles, 3, 1, Block);
            }
        }
    }
}
