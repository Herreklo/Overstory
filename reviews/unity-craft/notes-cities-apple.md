# Large Unity worlds, and URP on Apple silicon: research notes

Tags: [primary] = the makers' or Unity's/Apple's own words; [secondary] = press or a third party reporting; [unverified] = I could not confirm it from a fetched source. Researched 2026-10-26.

---

## A. Large data-driven worlds in Unity

### A1. Cities: Skylines II (Colossal Order), in the makers' own words

- The simulation is "fully implemented using the DOTS stack", but rendering does **not** use Entities Graphics: "we have our own that does instancing using the same lower BatchRendererGroup API… due to the unclear direction of the package at the time". No C:S1 code was reused. CO developer u/co_damsku on Reddit, Oct 2023. [primary] https://twt.omada.cafe/r/CitiesSkylines/comments/17ekhtw/comment/k64zldb/?context=3 (a mirror of reddit.com/r/CitiesSkylines/comments/17ekhtw)
- At launch, CO said the characters "are currently missing their LODs" and that it was "working on bringing these to the game along general LODs improvements across all game assets". It also said the detailed teeth were not the cause. [secondary, quoting CO's statement] https://www.techradar.com/gaming/pc-gaming/no-cities-skylines-2s-performance-issues-arent-because-of-the-citizens-teeth-developer-confirms
- Later, Iceflake (who took over development) said LODs, water and terrain were "generating too many polygons", and that "nothing can be precomputed ahead of time or baked in". [secondary, quoting the developer's City Corner blog] https://www.pcgamesn.com/cities-skylines-2/performance-blog
- Looking back in 2026, CO's CEO Mariina Hallikainen said the studio had planned around Unity features that were not finished yet. She named HDRP Shader Graph custom interpolators and ECS support for long-running jobs, and said a small studio struggles to customise an engine heavily. CO's next game is still in Unity. [secondary: AUTOMATON paraphrasing a PC Gamer interview] https://automaton-media.com/articles/newsjp/20260319-430623/

### A2. Cities: Skylines II, third-party analysis (Paavo Huhtala). This is not the makers' account.

The original is https://blog.paavo.me/cities-skylines-2-performance/. My fetch of it was blocked, so everything below comes from press summaries of it.
- He captured one frame in RenderDoc: about 87.8 ms, 6,705 draw calls and 53,361 API calls, on an RTX 3080 at 5120×1440. The game used about 6.7 GB of VRAM. [secondary] https://gigazine.net/gsc_news/en/20231106-why-cities-skylines-2-performs-poorly
- Many meshes are far too detailed for their size on screen and have no LODs. Pedestrian teeth alone are about 6k vertices, against about 10k for a low-density house. [secondary] https://hothardware.com/news/cities-skylines-2-autopsy
- Culling is frustum-only, with no occlusion culling, and distance culling is "not very aggressive". [secondary] https://www.windowscentral.com/gaming/cities-skylines-ii-runs-horribly-a-deep-dive-into-unity-explains-why
- Shadows take about half the render time. High-resolution cascades treat everything as a caster, which adds many draw calls. [secondary] hothardware, above
- CO wrote its own culling, skinning and virtual texturing. Huhtala guesses this was forced by gaps in DOTS rendering at the time, and that the release came before those systems were mature. He blames time and design, not skill. [secondary] gigazine, windowscentral, above

**Lessons:** instancing (BRG) doesn't save you from vertex count, missing LODs or shadow casters; the GPU died on geometry. A custom renderer on a moving engine API is expensive.

**For us:** every generated building needs LODs and a shadow-caster LOD (or no shadow at distance) from day one, made by the generator rather than by hand. Measure triangles per pixel, not just batches. Prefer Unity's shipped GPU Resident Drawer over a custom BRG renderer unless measurements force it.

### A3. Cities: Skylines (2015)

No primary technical source found; Unity's case study now redirects. [unverified] https://unity3d.com/case-study/cities-skylines **For us:** don't cite C:S1 practice.

### A4. Shadows of Doubt (ColePowered, Cole Jefferies)

- Everything sits on a 1.8 m tile grid, and floors are 15×15 tiles. The grid is used for "pathfinding, culling and this generation process". Hierarchy: City > District > Block > Building > Floor > Address > Room > Tile. Floorplans are hand-drawn per address. Rooms are placed procedurally, scored on floor space, shape and windows. [primary] https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/
- The game cannot render "every single room in every single building". Culling reuses the interior grid. Interiors can see the street through windows, but upper-floor interiors are not drawn from the street; the ground floor is the exception, so shopfronts read from both sides. [primary] https://www.moddb.com/news/shadows-of-doubt-devblog-6-first-person-adventures
- "The doors in Shadows also act as my 'culling portals'… As the game is procedurally generated, I had to come up with my own system for handling culling." Doors group rooms into trees, and closed doors cut down what is drawn. [primary] https://colepowered.com/?p=35092
- What was hard: 100% real-time lighting ("a big performance hog"), handled with fewer lights and distance cut-offs; thousands of movable props to save and reset. [primary] https://colepowered.itch.io/shadows/devlog/354045/shadows-of-doubt-devblog-30-the-top-shadows-of-doubt-development-challenges-part-i
- The game moved to HDRP (DevBlog 12; title only seen). [primary] https://colepowered.com/2019/02/

**Lessons:** procedural means no baked occlusion, so the generator's own topology (rooms, doors, grid) becomes the culling structure. Real-time lights are budgeted by distance.

**For us:** let the building generator emit its own visibility data (facade or interior split, openings) so culling comes from the same records that build the place. Plan for no baked lighting and no baked occlusion, because buildings change with history.

### A5. Townscaper (Oskar Stålberg)

- The grid is made of quads: "when I build content for it, I create square tiles" and skews them to fit. WFC is used, implemented differently from Bad North. Colour was "a technical challenge" because every boundary between two colours needs its own pieces. [primary, interview] https://www.mcvuk.com/business-news/when-we-made-townscaper/
- Article quoting Stålberg: the grid is a hex grid split into quads and relaxed; marching-cubes-style corner tiles fit the cells; real-time WFC "is actually allowed to fail silently". Bad North had 300+ tiles and merged each island into one mesh to cut draw calls. [secondary, with Stålberg quotes] https://gamedeveloper.com/blogs/how-townscaper-works-a-story-four-games-in-the-making
- Townscaper is made in Unity. [secondary] https://en.wikipedia.org/wiki/Townscaper
- Windows are cut with a stencil after placement. [secondary, the author's own description, unconfirmed by Stålberg] gamedeveloper, above
- I found no primary source on Townscaper's shading, AO or outlines. [unverified]

**For us:** a small kit of corner pieces gives huge variety. But every new visual state (age, repair, material) multiplies the kit the way colour did, so encode history in shader inputs (maps, vertex data) rather than in new pieces where we can. Merging each block's static meshes is a cheap win.

### A6. Megacity (2018–19) and Megacity Metro (Unity)

- Megacity: "4.5 million mesh renderers, 5000 dynamic vehicles and 200,000 unique building objects", plus 100,000 audio sources. [secondary, quoting Unity] https://www.guru3d.com/story/unity-engine-megacity-tech-demo/
- Mike Acton, Unite LA 2018, "LOD and Culling Systems that Scale" (via a summary thread): no octree (ECS chunks already group data); no transform hierarchy for static content; subscene IDs keep render batches separate, so streaming doesn't rebuild world state; LOD instances flat, not shared. [secondary, summary of a primary talk] https://nexe.gamedev.net/forums/topic/699785-slides-lod-and-culling-systems-that-scale
- Megacity Metro: "Play on Mobile, PC, and Mac with graphics powered by the Universal Render Pipeline (URP)"; DOTS, Netcode for Entities, 128+ players. [primary, Unity quoted] https://80.lv/articles/unity-launches-megacity-metro-a-new-multiplayer-game-sample ; Unity claims "large-scale streaming", Unity 6 and 2022 LTS. [primary] https://unity.com/megacity
- The GitHub README (Entities Graphics, HLOD, streaming specifics) was blocked. [unverified] https://github.com/Unity-Technologies/megacity-metro

**For us:** the nearest Unity reference for a URP city on Mac. Borrow the structure without DOTS: stream by block, keep static data flat, never rebuild global state on load.

---

## B. Unity URP on Apple silicon and Metal

### B1. How Apple GPUs work (Apple)

- TBDR: a tiling phase, then a rendering phase. "The GPU does not have video memory. So bandwidth could be a problem if the content has not been tuned." Load and store actions run once per tile. "If you don't need any data, don't load anything and clear instead." [primary] https://developer.apple.com/videos/play/wwdc2020/10602/
- Hidden surface removal is "pixel perfect and submission order independent". Submit opaque geometry first, then alpha-test/discard, then translucent, and don't interleave them. Blending and MSAA resolve happen in tile memory, so MSAA targets can be memoryless. [primary] same
- Apple-silicon Macs: fewer passes means fewer loads and stores. Write every attachment, because partial writes force occluded fragments to be shaded. "Depth pre-passes are usually unnecessary": HSR rejects hidden fragments "without any additional costs". Prefer `half`. [primary] https://developer.apple.com/videos/play/wwdc2020/10632

**For us:** the costs on a Mac are bandwidth and passes, not overdraw of opaque geometry. Keep alpha-tested foliage and clutter limited. Each extra full-screen pass costs more than it would on a desktop GPU.

### B2. Render Graph: native render pass merging and framebuffer fetch (Unity)

- More passes means more memory traffic, worst on TBDR. Use `AddRasterRenderPass`; unsafe and Compatibility Mode passes can't be optimised. Use the Render Graph Viewer to see why passes didn't merge. Reuse URP's Copy Color and Copy Depth via `ConfigureInput` rather than making your own. [primary] https://docs.unity3d.com/kr/6000.0/Manual/urp/render-graph-optimize.html
- Framebuffer fetch: `SetInputAttachment` plus `LOAD_FRAMEBUFFER_X_INPUT` reads the previous pass's result from tile memory, and URP merges the passes. It is supported on **Metal** and Vulkan; elsewhere Unity falls back to a copy. It works only for same-pixel reads. [primary] https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/framebuffer-fetch/render-graph-framebuffer-fetch
- Unity staff on what breaks a single native pass: depth copy After Opaques; post-processing (intermediate textures, bloom mips); neighbour-sampling effects (DoF, bloom); compute or unsafe passes ("only RasterPass' can be merged"); MSAA in the desktop editor. The viewer shows loads/stores and memoryless targets ("on supported hardware with DX12, Vulkan or Metal"). On-tile post-processing (6.3+) is untethered-XR only so far. [primary] https://discussions.unity.com/t/performant-and-energy-efficient-rendering-with-render-graph-and-on-tile-post-processing-for-untethered-xr-in-unity-6-3/1703007
- The Universal Renderer has a Native RenderPass toggle that enables programmable blending in custom shaders. [primary] https://docs.unity3d.com/6/Documentation/Manual/urp/urp-universal-renderer.html

**For us:** write every custom pass (outline, history overlays) as a raster pass. Use input attachments for per-pixel effects. Check merging in the Render Graph Viewer on a player build, not only in the editor. Edge-detect outlines sample neighbours and will cost a store; budget for one.

### B3. Opaque texture, depth texture copies, depth priming

- Depth Texture Mode "After Transparents" can give "a significant improvement in memory bandwidth" on mobile, because Copy Depth between opaques and transparents forces colour to be stored and reloaded, and more so with MSAA. [primary] https://docs.unity3d.com/6/Documentation/Manual/urp/urp-universal-renderer.html
- Depth priming is not supported with deferred, MSAA, or "at runtime on mobile devices that use tile-based deferred rendering (TBDR)"; Forced adds a costly prepass. [primary] same page. Whether Apple-silicon macOS counts as TBDR here is not stated. [unverified]
- Unity's XR guidance: disable Opaque Texture and Depth Texture, since both add copies and loads; depth priming has no benefit where HSR exists; 2× MSAA is cheap on tile GPUs; disable HDR to save bandwidth. [primary] https://docs.unity.com/en-us/engine/6000.3/manual/xr/graphics/untethered-device-optimization

**For us:** keep Opaque Texture off unless an effect needs it (water refraction is the likely one). Ask for depth After Transparents where we can, leave depth priming off on Apple silicon, and prefer MSAA to post AA. Each of these is a setting to test on a Mac player, not to assume.

### B4. GPU Resident Drawer and BatchRendererGroup on Metal

- BRG works on macOS with Metal, in URP/HDRP/custom SRP with the SRP Batcher. It needs BatchRendererGroup Variants set to "Keep all", unsafe code allowed, and DOTS-instancing shaders. [primary] https://docs.unity3d.com/cn/2023.2/Manual/batch-renderer-group-getting-started.html
- The GPU Resident Drawer needs Forward+, the SRP Batcher, and "Graphics APIs and platforms that support compute shaders, except OpenGL ES" (so Metal is included). MeshRenderer only; builds grow because all BRG variants are kept; disable static batching; gains are smaller in the editor views than in a player. It has its own GPU occlusion culling. [primary] https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html
- "Improves CPU performance, but it slightly increases GPU workload… If your application is GPU-bound, overall frame time might increase." The extra GPU cost is felt more on lower-end and mobile GPUs. [primary] https://docs.unity3d.com/Manual/urp/gpu-resident-drawer-performance.html

**For us:** the Resident Drawer suits many buildings that share a part kit, which is our case. But it costs GPU time on a GPU that may already be the limit, and its compute-based occlusion adds passes that can't merge. A/B test it in a Mac player with the stress-test street before it becomes the default. Per-building variation must come through instanced properties or maps, not MaterialPropertyBlocks.

### B5. Shader compilation hitches and PSOs on Metal

- Metal compiles shaders to AIR, then compiles again on the device "for every pipeline state". Binary archives "should be favored over pre-warming the Metal Shader Cache" and are valid only for the same GPU and OS build. In Fortnite, pipeline build time fell from 1:26 to 3 s. [primary] https://developer.apple.com/wwdc20/10615
- Unity 6 PSO tracing: `GraphicsStateCollection.BeginTrace` in a development build on the target API, save, then `WarmUp` or `WarmUpProgressively` while loading. "Shader Warmup is not fully supported on modern graphics APIs (DX12, Vulkan, Metal)." Traces are per API. [primary] https://discussions.unity.com/t/prevent-shader-compilation-stutters-with-pso-tracing-in-unity-6/951031
- Apple: the Metal Performance HUD flags compilation during gameplay; "unexpected compilation during gameplay… could be the source of a hitch". [primary] https://developer.apple.com/videos/play/meet-with-apple/242

**For us:** first-frame hitches will skew any timing. Warm up through a GraphicsStateCollection traced on a Mac player before measuring. Exclude the first visit to a street from frame-time numbers, or record it separately as a hitch metric.

### B6. Metal API validation, Xcode capture, Instruments

- Unity's "Metal API Validation" option checks shader resources against what is bound in the editor and reports to the console. It "doesn't enable Apple's Metal API validation"; for that, set Run in Xcode as Debug. It appears only when the editor runs on macOS. [primary] https://docs.unity.com/en-us/engine/6000.5/manual/platform-specific/apple-mac/player-settings-mac-os and https://docs.unity3d.com/ScriptReference/PlayerSettings-enableMetalAPIValidation.html
- The same page lists Memoryless Depth, Use MetalDisplayLink (steadier pacing) and Frame Timing Stats (needed by FrameTimingManager). [primary] same
- Xcode frame capture: player via Create Xcode Project with the scheme's GPU Frame Capture set to Metal; editor by making the Unity Editor the scheme's executable; or `FrameCapture.BeginCaptureToFile` plus `-enable-metal-capture`. (2021.3 page; Unity 6 page not checked.) [primary] https://docs.unity.cn/cn/current/Manual/XcodeFrameDebuggerIntegration.html
- Apple's tools: the Game Performance Overview template for long captures; Metal System Trace for GPU scheduling, gaps and overlap between frames; the Metal debugger for counters, heatmaps and sync points. Mark the app as a game for Game Mode. [primary] https://developer.apple.com/videos/play/meet-with-apple/242 ; Metal System Trace "will clearly highlight missed overlap opportunities" [primary] https://developer.apple.com/videos/play/wwdc2020/10632

**For us:** time in a built player with Frame Timing Stats on, never in the editor. Use Metal System Trace for "is the GPU idle between frames?" and the Xcode capture for "which pass stores what". Run Apple's validation (a Debug Xcode run) once per new render feature.

### B7. IL2CPP on macOS

- "The IL2CPP scripting backend requires Xcode." Apple silicon is the recommended architecture, Intel standalone is deprecated, and the minimum is macOS 12. [primary] https://docs.unity3d.com/Manual/macos-requirements-and-compatibility.html
- The Architecture setting offers Intel, Apple Silicon, or both; Run in Xcode as offers Release or Debug. [primary] https://docs.unity.com/en-us/engine/6000.3/manual/platform-specific/apple-mac/macos-delivery/macosbuildsettings

**For us:** benchmark an IL2CPP Apple-silicon-only player, which is the closest to shipping, and keep Mono editor numbers out of any judgement.

---

## Open questions and what I could not verify

1. Huhtala's original post was blocked, so all of A2 is from press summaries; it needs a direct read (including its DOTS instance-data section).
2. The Megacity Metro README was blocked; whether it uses Entities Graphics LODs, HLOD or sub-scene streaming on URP Mac is unconfirmed.
3. Whether URP treats macOS Apple silicon as "TBDR mobile" for depth priming and memoryless is undocumented in what I read. Test it.
4. No Unity statement on GPU Resident Drawer occlusion cost or Metal-specific bugs.
5. Whether on-tile post-processing (6.3+) will reach macOS.
6. Townscaper's rendering (AO, outlines, shading) and C:S1's LOD practice: no primary source found.
7. Shadows of Doubt's HDRP-switch post and Part II of the challenges were not read.
8. Whether Unity's GraphicsStateCollection uses MTLBinaryArchive on Metal: not stated.
