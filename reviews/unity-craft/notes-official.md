# Unity's official Unity 6 guidance: notes for a URP harbour town on Apple silicon

Tags: [primary] = Unity docs, blog, e-book page, sample or forum post by Unity staff; [secondary] = others; [unverified] = not confirmed from a fetched page. Manual pages were read in the version shown in the URL. Several pages now serve 6.4 to 6.6 text even under a 6.x URL, so version notes are given where the page made them clear.

## 1. The e-books and guides

- The Manual's "Best practice guides" page lists the Unity 6 set: Intro to URP for advanced creators; Create popular shaders and VFX with URP; Optimize for mobile, XR and Web; Optimize for consoles and PCs; Ultimate guide to profiling; Tips to increase productivity with Unity 6; Project organisation and version control; Intro to DOTS; C# style guide; ScriptableObject architecture; design patterns and SOLID. https://docs.unity3d.com/6000.4/Documentation/Manual/best-practice-guides.html [primary]
- E-book landing pages: URP advanced https://unity.com/resources/introduction-to-urp-advanced-creators-unity-6 ; mobile/XR/web https://unity.com/resources/mobile-xr-web-game-performance-optimization-unity-6 ; consoles/PC https://unity.com/resources/console-pc-game-performance-optimization-unity-6 ; version control https://unity.com/resources/best-practices-version-control-unity-6 (listed in https://discussions.unity.com/t/get-the-most-out-of-unity-6-with-these-learning-resources-technical-e-books-and-sample-projects/1541016) [primary]. I could not open the URP e-book page (the fetch was blocked) or any of the PDFs, so what follows comes from Unity's summaries, not the books.
- The consoles/PC guide (Unity 6 edition, 17 Oct 2024) "focuses on HDRP and large projects". The mobile guide is about 100 pages, "mostly focused on URP". Both point to GPU Resident Drawer, GPU occlusion culling and APV as the Unity 6 features to consider. https://unity.com/blog/unity-6-game-optimization-guides , https://unity.com/resources/console-pc-game-performance-optimization-unity-6 [primary]
- Profiling guide (Unity 6): frame budget, CPU-bound vs GPU-bound, sample vs instrumentation profiling, a written method; tools are the Profiler (new Highlights module, which compares against a target frame time), Profile Analyzer, Memory Profiler, Frame Debugger and Rendering Debugger, and Project Auditor (a package from 6.1). https://unity.com/blog/use-unity-6-profiling-tools-smart-efficient [primary]
- Shaders/VFX guide is now titled "The Universal Render Pipeline cookbook: Recipes for visuals and shader effects (Unity 6 edition)", Mar 2025. It has 12 recipes (stencil x-ray, toon/outline, decals and AO, LUT grading, reflections and refraction, water and volumetric clouds, GPU instancing / SRP Batcher / RenderMeshPrimitives), new procedural-noise (wood) and compute-shader recipes, an APV section, and Renderer Features written with Render Graph. A companion repo has one scene per recipe. https://discussions.unity.com/t/new-technical-e-book-create-popular-shaders-and-visual-effects-in-urp-unity-6-edition/1618135 , https://unity.com/resources/create-shaders-visual-effects-urp-unity-6 [primary]
- DOTS guide and productivity guide: listed only; contents not read [unverified].

For us: the PC guide leans HDRP, so for URP the mobile guide and the URP cookbook fit better. Read the cookbook's procedural-noise and RenderMeshPrimitives recipes first, since they match seeded texture and instanced buildings. Use the Profiler Highlights module with a frame budget we set ourselves.

## 2. Rendering path: Forward+ and its limits

- Forward: 9 lights per object (1 main, 8 additional); per camera 256 additional on desktop/console, 32 on mobile. To go past this, Unity says to use Forward+ or Deferred. https://docs.unity3d.com/Manual/urp/lighting/light-limits-in-urp.html [primary]
- Forward+: no per-object limit; up to 256 visible lights per camera on desktop, main light included. That cap is compiled into every Lit and Complex Lit variant and raises shader compile time. Lowering it means editing ShaderConfig in an embedded URP Config package and redoing the edit after each upgrade. https://docs.unity3d.com/Manual/urp/rendering/forward-plus-rendering-path-limitations.html [primary]
- Comparison table: Forward+ supports MSAA, blends more than 2 reflection probes, has low GPU impact and is "recommended" with the Entities package. Deferred has no MSAA and a high cost on mobile from G-buffer passes. Deferred+ is suggested for many lights where Rendering Layers or accurate terrain blending aren't needed. https://docs.unity3d.com/Manual/urp/rendering-paths-comparison.html [primary]
- When Forward+ is on, URP forces main and additional lights to per-pixel, ignores Per Object Limit and always blends probes. It relies on CPU light culling, so Unity steers low-end mobile to Deferred. https://discussions.unity.com/t/urp-project-quality-settings-learn-from-the-urp-3d-sample/338359 [primary]

For us: Forward+ is a requirement anyway, because the GPU Resident Drawer needs it (section 3). Harbour lamps and windows at night fit within 256. If Lit compile times on the Macs hurt, lowering the light cap is the documented lever.

## 3. GPU Resident Drawer (GRD)

- Requirements: Forward+ only; platforms with compute shaders, excluding OpenGL ES (Metal is not named, but it meets that rule [inference]); a Mesh Renderer; SRP Batcher on; Project Settings > Graphics > Shader Stripping > BatchRendererGroup Variants = Keep All. To enable: Keep All, SRP Batcher, GRD = Instanced Drawing, renderer = Forward+. Keep All makes builds longer because every BRG variant is compiled. Probe Atlas Blending is the default with GRD + Forward+. https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html [primary] (6.0 page: https://docs.unity3d.com/6/Documentation/Manual/urp/gpu-resident-drawer.html)
- An object qualifies only if it: has a Mesh Renderer; does not use the Light Probes "Use Proxy Volume" setting; uses static GI only (no realtime GI); uses a shader with DOTS instancing; does not move between one camera finishing and the next starting; does not use MaterialPropertyBlock; has no per-instance callback such as OnRenderObject. To opt an object out, add "Disallow GPU Driven Rendering" (can apply to children). https://docs.unity3d.com/Manual/urp/make-object-compatible-gpu-rendering.html [primary]
- Performance: it pays off with many objects sharing a mesh and shader variant. It lowers CPU cost but adds some GPU work, so a GPU-bound frame can get slower. Instanced merging can raise overdraw, and on non-tiled GPUs Unity suggests Depth Priming Auto/Forced. Disable static batching. In the lighting settings, turn on Fixed Lightmap Size and turn off Use Mipmap Limits. Gains in the Editor's Scene/Game views understate those in builds. Look for "Hybrid Batch Group" draws in the Frame Debugger. https://docs.unity3d.com/Manual/urp/gpu-resident-drawer-performance.html [primary]
- URP asset: Small-Mesh Screen-Percentage culling (0 = off; "may not work with custom LOD meshes"; exempt objects with the Disallow Small Mesh Culling component). https://docs.unity3d.com/Manual/urp/universalrp-asset.html [primary]

For us: this is the main lever for many generated buildings, and it rules things out. Per-building history or seed values cannot go through MaterialPropertyBlock. They must go through DOTS-instanced per-instance properties in a DOTS-instancing shader, or be baked into vertex data or textures. Measure in a build, not in Play mode, and check the GPU side: Apple GPUs are tile-based, so the overdraw note differs (see section 5).

## 4. GPU occlusion culling

- Needs GRD (with the same object restrictions) and Render Graph (Compatibility Mode off). Turn on GPU Occlusion on the Universal Renderer. It is most effective with shared meshes, heavy occlusion, and occluded objects that have many vertices and a small screen radius. Bounds are spheres, so thin or long meshes are rarely culled. Where there is little occlusion it can cost time. https://docs.unity3d.com/6000.2/Documentation/Manual/urp/gpu-culling.html [primary]
- It is disabled when On-Tile Validation is enabled. https://docs.unity3d.com/Manual/urp/universalrp-asset.html [primary]

For us: a street of facades occludes the blocks behind it well, so expect a gain at street level. But long terraced rows and quay walls are elongated and get bounding spheres, so cull per building or per bay, not per row. Turn it on and off in A/B timing tests rather than assuming it helps.

## 5. Render Graph, native render passes, tile GPUs, on-tile mode

- Render Graph merges passes into native render passes on TBDR GPUs, aliases memory, and culls unused passes. Keeping textures in tile memory saves bandwidth. https://docs.unity3d.com/Manual/urp/render-graph-introduction.html [primary]
- Optimisation advice: reuse URP's Copy Color/Copy Depth (request inputs with ConfigureInput); prefer AddRasterRenderPass; use SetInputAttachment / framebuffer fetch for reads at the same pixel; don't split passes for tidiness; AddUnsafePass can't be optimised; avoid blitting to the camera colour and back (blit to a new texture and swap it in). Use the Render Graph Viewer to see why passes didn't merge. https://docs.unity.com/en-us/engine/6000.0/manual/render-pipelines/universal-render-pipeline/customizing-urp/render-graph/optimize [primary]
- Versions: in 6.3 URP Compatibility Mode is deprecated, and upgraded projects fail to build until Render Graph is enabled or URP_COMPATIBILITY_MODE is defined (marked "As Designed"). https://issuetracker.unity.com/issues/15954/projects-upgraded-to-63-fail-to-build-due-to-render-graph-being-disabled-on-upgrade-by-default [primary]. In 6.4 "URP Compatibility Mode is now fully removed", define included. https://docs.unity3d.com/6000.4/Documentation/Manual/UpgradeGuideUnity64.html [primary]
- On-tile rendering (Tile-Only Mode on the renderer; documented in the 6.5/6.6 manuals, release version not stated). It keeps intermediates and depth in tile memory. It forbids depth and opaque textures, TAA, MSAA, HDR, built-in post, upscaling, camera stacking and Deferred. https://docs.unity3d.com/Manual/on-tile-rendering.html [primary]

For us: write every custom effect (history overlays, picking, outlines) as a Render Graph raster pass from the start. Compatibility Mode is gone in 6.4. Apple silicon is tile-based, so pass merging counts for us. Tile-Only Mode is too restrictive for us: no depth texture, no HDR, no TAA/STP.

## 6. Depth priming, depth and opaque textures

- Depth Priming: Disabled / Auto (only if a depth prepass already exists; "not supported on Android, iOS, or Apple TV") / Forced (adds a prepass, costing memory and time). It doesn't work with Deferred or MSAA, nor at runtime on TBDR mobile. Custom shaders need DepthOnly and DepthNormals passes or they turn invisible. Depth Texture Mode can be After Opaques, After Transparents or Force Prepass; After Transparents saves bandwidth on mobile by avoiding a render target switch. https://docs.unity3d.com/6/Documentation/Manual/urp/urp-universal-renderer.html [primary]
- The Opaque Texture is a copy, like a GrabPass, taken before transparents. Downsampling can be None, 2x Bilinear, 4x Box or 4x Bilinear; the optimisation page advises 4x Bilinear. Store Action "Store" greatly raises bandwidth on tile GPUs. https://docs.unity3d.com/Manual/urp/universalrp-asset.html , https://docs.unity.cn/Manual/urp/optimize-for-better-performance.html [primary]
- The same optimisation page: fewer shadow cascades and shorter shadow distance, low soft shadows, LUT grading in LDR, LOD cross-fade dither set to Bayer. [primary, same URL]

For us: the docs don't say whether macOS Metal on Apple silicon is treated as a "TBDR mobile" device for depth priming. Their wording names Android/iOS/tvOS only. Measure Disabled vs Forced on an M-series Mac. Every custom building shader needs DepthOnly and DepthNormals passes. Use the opaque texture only if water refraction needs it, and downsample it.

## 7. Upscaling: STP and FSR

- STP needs compute (SM 5.0), not GLES. It forces TAA, picks quality per platform (higher on PC and consoles), and can't be combined with dynamic resolution. https://docs.unity3d.com/Manual/urp/stp/stp-upscaler.html , https://docs.unity3d.com/Manual/resolution-scale-introduction.html [primary]
- URP filters: Automatic, Bilinear, Nearest, FSR 1.0 (SM 4.5+, with a sharpness setting, stays active at scale 1.0), STP 1.0 (improves quality even at 1.0). DLSS/FSR2 are HDRP only. MetalFX isn't mentioned. https://docs.unity3d.com/Manual/urp/universalrp-asset.html [primary]

For us: STP at a render scale of about 0.67 to 0.77 is the official URP route on Macs. Its TAA will smear thin seeded detail and trade signage unless motion vectors are right, which matters for "reads at a glance". Judge STP against native in the engine before adopting it.

## 8. Shader variants, stripping, PSO warm-up

- URP strips variants for features turned off in the URP Assets (for example main-light shadows off removes those variants). https://docs.unity3d.com/6000.2/Documentation/Manual/urp/shader-stripping.html [primary]
- Global settings: Strip Debug Variants (removes the Rendering Debugger from players), Strip Unused Post Processing Variants (keeps only Volume Profiles that exist), Strip Unused Variants (can halve some counts), Export Shader Variants logs, a log level. https://docs.unity3d.com/6/Documentation/Manual/urp/urp-global-settings.html [primary]. Turning LOD cross-fade off, or using 2x2 Stencil dither, cuts variants. https://docs.unity3d.com/Manual/urp/universalrp-asset.html [primary]
- GraphicsStateCollection: documented as experimental in the 6.0 manual already, not only from 6.1. Modern APIs compile shaders when the PSO is created. Trace in development builds only (BeginTrace early, EndTrace, SaveToFile to .graphicsstate, or SendToEditor with Autoconnect Profiler), keep one collection per graphics API and platform, and use Append / traceCacheMisses to fill gaps. Warm up with WarmUp or WarmUpProgressively (a job handle) during loading; PSOs are cached to disk. The 6.4 manual adds automatic warm-up before or after the first scene, under Graphics > Shader loading. Check the Profiler markers Shader.CreateGPUProgram and CreateGraphicsGraphicsPipelineImpl. https://docs.unity3d.com/6/Documentation/Manual/shader-prewarm.html , https://docs.unity3d.com/Manual/shader-pso-trace.html , https://docs.unity3d.com/Manual/shader-prewarm.html [primary]

For us: GRD's Keep All plus Forward+ make for many variants and long Mac builds. Keep one URP Asset per quality tier and turn off unused features. Trace a Metal collection while walking the harbour once, and warm it progressively behind a loading screen. That removes first-sight hitches when a new building kind appears.

## 9. LOD: Mesh LOD (6.2+) and LOD Groups

- Mesh LOD is documented from the 6.2 manual: https://docs.unity3d.com/6000.2/Documentation/Manual/lod/mesh-lod-introduction.html , https://docs.unity3d.com/6000.2/Documentation/Manual/lod/mesh-lod-generate-lods.html [primary]. LODs are generated at import and stored in the mesh's index buffer, with a smaller memory footprint than a LOD Group. Selection uses screen size plus project-wide and per-object settings. Skinned meshes get LODs, but skin weights and blend shapes are ignored and deformation stays at LOD0. Particles, VFX Graph and static batching always use LOD0. RenderMeshInstanced and RenderMeshPrimitives need forceMeshLod. Unity doesn't recommend combining it with a LOD Group, and there is no per-LOD material. Triangles only. Cross-fade needs GRD. https://docs.unity3d.com/Manual/lod/mesh-lod-introduction.html (6.4+ text) [primary]

For us: Mesh LOD is generated on import, so it suits generator output brought in from Blender as FBX. Whether runtime-built meshes can get Mesh LODs is not documented. The simplifier could erase the details that carry history (sills, patches, sags). Keep LOD Groups, or our own levels from the generator, for the hero street, and use Mesh LOD for distant blocks after a contact-sheet check.

## 10. Adaptive Probe Volumes (URP)

- Probes are placed automatically by geometry density and sampled per pixel (8 nearest), giving fewer seams than Light Probe Groups. Supports Lighting Scenarios (bake blending), streaming, Baking Sets and runtime sky occlusion. Limits: probes can't be moved by hand (leaks near walls need overrides), Light Probe Groups can't be converted, and blending breaks if geometry moves between bakes. https://docs.unity3d.com/Manual/urp/probevolumes-concept.html [primary]
- Unity's URP "Fantasy Kingdom" sample uses APV on mobile. https://unity.com/vn/blog/unity-6-graphics-learning-resources [primary]

For us: APV needs a bake. When history changes a building, the bake goes stale, and lighting scenarios break if geometry moves. Use it for the fixed town shell and time-of-day scenarios, and expect light leaks where generated buildings change.

## 11. SRP Batcher rules

- An object needs a Mesh or Skinned Mesh Renderer (no particles) and no MaterialPropertyBlock. Its shader declares built-ins in one `UnityPerDraw` CBUFFER and all material properties in one `UnityPerMaterial` CBUFFER. The Inspector shows compatibility. URP Lit and Unlit comply, except the particle versions. https://docs.unity3d.com/6000.1/Documentation/Manual/SRPBatcher-Materials.html [primary]

For us: every hand-written HLSL building shader needs every material property inside one CBUFFER_START(UnityPerMaterial), plus DOTS-instancing support for GRD. Shader Graph does both.

## 12. Scripting backend and Metal validation on macOS

- IL2CPP gives "improved performance and shorter startup times" but longer builds and bigger binaries. Cross-compiling is "generally not supported". https://docs.unity3d.com/cn/6000.0/Manual/il2cpp-introduction.html [primary]
- macOS players need macOS 12+. Apple silicon is "the recommended target architecture"; Intel x64 is deprecated. IL2CPP needs Xcode. https://docs.unity3d.com/Manual/macos-requirements-and-compatibility.html [primary]
- `PlayerSettings.enableMetalAPIValidation`: "Enables Metal API validation in the Editor." The page says nothing about players. https://docs.unity3d.com/ScriptReference/PlayerSettings-enableMetalAPIValidation.html [primary]

For us: time IL2CPP Apple silicon builds, not Mono and not the Editor. Turn Metal validation off when timing in the Editor, since validation adds CPU cost [unverified, general Metal knowledge]. Whether it reaches players is unverified.

## 13. Samples

- URP 3D Sample: Terminal hub (PBR, GPU Lightmapper), Garden (stylised painterly, modular architecture on the default Lit shader, SpeedTree, many dynamic lights, Forward+ or Deferred), Oasis (Shader Graph sand, water, fog), Cockpit (VR, custom lighting). It shipped for 2022.3 with Unity 6 support promised (Render Graph, GRD). Known issues: long builds from variant counts; TAA set per camera. https://discussions.unity.com/t/introducing-the-new-urp-3d-sample/929894 [primary]. Settings: the Garden uses Forward+; the HighQuality URP Asset uses Forward+ plus a Decal feature (Automatic, which becomes Screen Space on HSR GPUs); Mobile_Low uses Deferred; Mobile_High has additional-light shadows off and uses cookies instead. https://discussions.unity.com/t/urp-project-quality-settings-learn-from-the-urp-3d-sample/338359 [primary]. I did not confirm its Unity 6 STP/GRD/APV settings (the blog https://Blogs.Unity3D.com/engine-platform/dive-into-the-urp-3d-sample failed to load).
- Megacity Metro: URP, DOTS with Netcode for Entities, 100+ players, mobile, Switch and desktop; Unity 6 and 2022 LTS. https://unity.com/fr/demos/megacity-competitive-action-sample [primary]; Mac and PC listed by https://80.lv/articles/unity-launches-megacity-metro-a-new-multiplayer-game-sample [secondary]. Its rendering settings (Entities Graphics/BRG, HLOD, path) were not confirmed.

For us: the Garden is the nearest official precedent, a stylised modular town on the default Lit shader with Forward+, and worth opening in Unity 6 to copy its URP Assets. Megacity is the official precedent for a city drawn through BRG/Entities, but I did not verify its settings.

## Open questions / not verified

1. Whether Metal on Apple silicon Macs counts as "TBDR" for Depth Priming Auto and Forced. The docs only exclude Android, iOS and tvOS.
2. Whether Metal API Validation affects macOS players. Unity's page says Editor only.
3. When on-tile rendering and automatic PSO warm-up arrived: seen in the 6.4 to 6.6 manuals, release not confirmed.
4. Whether Mesh LOD works on meshes built at runtime, and how it interacts with lightmaps.
5. The URP 3D Sample's Unity 6 settings (STP, GRD, APV) and Megacity Metro's renderer settings. Check them in the projects.
6. The contents of the e-book PDFs (URP advanced, PC, DOTS, productivity): the URP page was blocked and no PDF was read.
7. Unity has not published an IL2CPP vs Mono speed figure for macOS.
